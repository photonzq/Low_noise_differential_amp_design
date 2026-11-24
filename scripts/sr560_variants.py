"""Two more SR560 models beside the reproduction as drawn (sr560_frontend.py, sr560_chain.py).

  corrected          the netlist of sr560_chain.py with its three departures from the documents
                     corrected (sr560_bw_check.py, (f)): C406 = 82 pF from U403's output to its
                     inverting input (sheet 560_4F and the parts list), C301 = 47 pF (parts list)
                     instead of the schematic's 6.8 pF, and every op amp with its data sheet's
                     open-loop dynamics instead of the behavioural model's poles: the OP37 and LT1028
                     fitted to their gain-phase plots, the LF356 and LF411 as two-pole fits to their
                     Bode plots (sr560_bw_check.py, (e); the fitted values are read from
                     sr560_bw_check.json, gain_phase_fits and datasheet_readings, and rebuilt with
                     sr560_bw_check.refit).  The op amps' noise generators, DC gains and output
                     stages, and every other part, are those of the reproduction.
  corrected_lsk389b  the corrected model with U106 an LSK389B (LSK389B_LIS of models.py: Linear
                     Systems' card, Rev 2, calibrated to the LSK389 data sheet Rev A27) instead of
                     the NPD5564 (the 2N5564 card): newer units, per a teardown report of two units
                     (EEVblog forum, "SR560 Low noise amp -- Noise Calculation", 18 March 2024); the
                     manual (Rev. 3.1, 4/2023) lists the NPD5564.

For each model the analyses of the reproduction, with the deck edit applied: the front end alone
(sr560_frontend.run_case, x10: gain, -3 dB, CMRR at 1 kHz, input noise and its groups at 1 kHz),
the chain's input noise at every gain of both modes, its AC response at gains of 1 to 50 000 and
its CMRR with ideal matching at a gain of 1000 (sr560_chain's functions; offset trim and vernier
calibration as there).  Decks under ../sim/runs/sr560_variants/<model>/.

Checks, stored in the results:
  check_operating_point      the deck whose operating point fell back to ngspice's transient op before
                             the SR560 decks got sr560_frontend.NODESET: solved with its old 1-mOhm
                             input resistors and without the nodeset (abstol = 1e-15 A, and 1e-12 A),
                             with 1-Ohm resistors, with the nodeset, and from the fallback's state:
                             the fallback's state is not a DC solution, and the solution is the same
                             from every starting point that converges; and the trimmed state at a
                             gain of 1000 from sr560_frontend.NODESET alone and from
                             sr560_chain.trimmed's continuation
  check_as_drawn             the same code without an edit, at a gain of 1000 (noise, AC), against
                             sr560_chain.json: must agree exactly (the edit plumbing changes nothing)
  check_cmrr_trim            the CMRR with ideal matching of the as-drawn chain at a gain of 1000,
                             trimmed and with the offset trim at 0 V (the front end alone's setting)
  check_corrected_vs_bw      the corrected model's -3 dB at gains of 1, 100 and 1000 against
                             sr560_bw_check.json's variant f_datasheet_add_C406_C301_47p (same decks)

Writes ../sim/results/sr560_variants.json and the curves sr560_variants_<model>_*.npz (and the
front end's sr560_x10_<jfet>_<model>_curves.npz).
Usage: python sr560_variants.py [model ...]     (default: both; about 100 ngspice runs per model)
       python sr560_variants.py checks          (the checks alone; the models' results are kept)
"""
from __future__ import annotations

import json
import sys

import numpy as np

import models
import spice
import sr560_bw_check as BW
import sr560_chain as SC
import sr560_frontend as FE

OUT = spice.RESULTS / "sr560_variants.json"
JFET_LSK = "LSK389B_LIS"
BY_TYPE = {"LF356": ["U204", "U303"], "LF411": ["U103", "U404"], "OP37": ["U102", "U201", "U305", "U403"],
           "LT1028": ["U105", "U402"]}
FE_INSTS = ("U102", "U103")               # the op amps of the front end alone
MODELS = {
    "corrected": dict(jfet="2N5564", desc="C406 = 82 pF added, C301 = 47 pF, every op amp with its data "
                                          "sheet's open-loop dynamics; U106 NPD5564 (2N5564 card)"),
    "corrected_lsk389b": dict(jfet=JFET_LSK, desc="the corrected model with U106 an LSK389B (LSK389B_LIS, "
                                                  "calibrated to the LSK389 data sheet Rev A27)"),
}
AC_GAINS = (1, 10, 100, 1000, 10000, 50000)


def opamp_dynamics() -> tuple[dict, dict]:
    """The four data-sheet op-amp subcircuits (name -> text) and their parameters, from the fits
    archived by sr560_bw_check.py."""
    bw = json.loads((spice.RESULTS / "sr560_bw_check.json").read_text(encoding="utf-8"))
    fits, ds = bw["gain_phase_fits"], bw["datasheet_readings"]
    par = {"LF356_DS": dict(base="LF356", gbw=ds["LF356 Bode"]["two_pole"]["gbw"],
                            poles=[ds["LF356 Bode"]["two_pole"]["fp2"]], doublet=None,
                            source="sr560_bw_check.json datasheet_readings['LF356 Bode'].two_pole"),
           "LF411_DS": dict(base="LF411", gbw=ds["LF411 Bode"]["two_pole"]["gbw"],
                            poles=[ds["LF411 Bode"]["two_pole"]["fp2"]], doublet=None,
                            source="sr560_bw_check.json datasheet_readings['LF411 Bode'].two_pole")}
    for m in ("OP37", "LT1028"):
        f = fits[m]["fit"]
        par[f"{m}_DS"] = dict(base=m, gbw=f["gbw"], poles=list(f["poles"]), doublet=list(f["doublet"]),
                              source=f"sr560_bw_check.json gain_phase_fits['{m}'].fit")
    subs = {n: BW.refit(p["base"], n, p["gbw"], poles=tuple(p["poles"]),
                        doublet=tuple(p["doublet"]) if p["doublet"] else None) for n, p in par.items()}
    return subs, par


def edits(model: str, subs: dict) -> tuple:
    """(chain edit, front-end edit) of a model; the front end's JFET is passed to run_case."""
    chain_models = {i: f"{t}_DS" for t, insts in BY_TYPE.items() for i in insts}
    chain = [BW.make_edit(chain_models, subs), BW.ADD_C406, BW.C301_47P]
    jfet = MODELS[model]["jfet"]
    if jfet != "2N5564":
        chain.append(BW.make_edit({}, {}, replace={r"^XJA da ina sa \S+$": f"XJA da ina sa {jfet}",
                                                   r"^XJB db inb sb \S+$": f"XJB db inb sb {jfet}"}))
    fe_models = {i: chain_models[i] for i in FE_INSTS}
    fe = BW.make_edit(fe_models, {n: subs[n] for n in set(fe_models.values())})
    return BW.compose(*chain), fe


def ac_summary(f, h) -> dict:
    mag = np.abs(h)
    ref = spice.at(f, mag, 1e3)
    return dict(gain_1k=ref, f3db=spice.f3db(f, mag, ref),
                db_300k=float(20 * np.log10(spice.at(f, mag, 3e5) / ref)),
                db_1M=float(20 * np.log10(spice.at(f, mag, 1e6) / ref)),
                peak_db=float(20 * np.log10(mag.max() / ref)))


def run_model(model: str, subs: dict) -> dict:
    chain_edit, fe_edit = edits(model, subs)
    runs = f"sr560_variants/{model}"
    jfet = MODELS[model]["jfet"]
    res = dict(description=MODELS[model]["desc"], jfet=jfet)
    # the front end alone (x10), as sr560_frontend.py
    res["frontend_x10"] = FE.run_case(True, jfet, edit=fe_edit, suffix=f"_{model}")
    fe = res["frontend_x10"]
    print(f"{model}: front end x10 gain(1k) {fe['gain_1k']:.4f}, f3dB {fe['f3db'] / 1e6:.3f} MHz, "
          f"CMRR(1k) {fe['cmrr_db_1k']:.1f} dB, e_in(1k) {fe['en_in']['1000.0'] * 1e9:.3f} nV/rtHz", flush=True)
    # the chain's noise at every gain of both modes
    rows = {}
    for mode, gl in (("LN", SC.GAINS_LN), ("HDR", SC.GAINS_HDR)):
        for g in gl:
            s = SC.trimmed(SC.allocate(g, mode), g, runs=runs, edit=chain_edit)
            r = SC.run_noise(s, runs=runs, edit=chain_edit)
            rows[f"{mode}_{g}"] = dict(mode=mode, gain=g, setting=s.tag, nominal=s.nominal, en=r["en"],
                                       manual=SC.MANUAL[mode].get(g))
            print(f"{model} {mode:3s} G {g:>6}: en(1k) {r['en']['1000.0'] * 1e9:6.2f}  en(100k) "
                  f"{r['en']['100000.0'] * 1e9:6.2f}  en(10) {r['en']['10'] * 1e9:7.2f}  (manual "
                  f"{SC.MANUAL[mode].get(g)})", flush=True)
            if mode == "LN" and g in (100, 1000):
                np.savez(spice.RESULTS / f"sr560_variants_{model}_noise_{mode}_{g}.npz", f=r["f"], inn=r["inn"])
    res["noise"] = rows
    # the chain's AC response
    acs = {}
    for g in AC_GAINS:
        s = SC.trimmed(SC.allocate(g, "LN"), g, runs=runs, edit=chain_edit)
        r = SC.run_ac(s, runs=runs, edit=chain_edit)
        acs[str(g)] = dict(setting=s.tag, **ac_summary(r["f"], r["h"]))
        print(f"{model} AC G {g:>6}: f3dB {acs[str(g)]['f3db'] / 1e6:.3f} MHz, 1 MHz {acs[str(g)]['db_1M']:+.2f} dB, "
              f"peak {acs[str(g)]['peak_db']:+.2f} dB", flush=True)
        np.savez(spice.RESULTS / f"sr560_variants_{model}_ac_{g}.npz", f=r["f"], h=r["h"])
    res["ac"] = acs
    # CMRR with ideal matching at a gain of 1000
    s = SC.trimmed(SC.allocate(1000, "LN"), 1000, runs=runs, edit=chain_edit)
    dm = SC.run_ac(s, runs=runs, edit=chain_edit)
    cm = SC.run_ac(s, SC.SRC_CM, "cm", runs=runs, edit=chain_edit)
    cmrr = 20 * np.log10(np.abs(dm["h"]) / np.abs(cm["h"]))
    res["cmrr_ideal_matching"] = {str(f0): float(spice.at(dm["f"], cmrr, f0)) for f0 in (10, 1e3, 1e4, 1e5, 1e6)}
    np.savez(spice.RESULTS / f"sr560_variants_{model}_cmrr.npz", f=dm["f"], cmrr=cmrr)
    print(f"{model} CMRR (ideal matching) at G 1000: {res['cmrr_ideal_matching']}", flush=True)
    return res


def check_as_drawn() -> dict:
    """sr560_chain's functions without an edit, in this script's run folder, against the archive."""
    arch = json.loads((spice.RESULTS / "sr560_chain.json").read_text(encoding="utf-8"))
    runs = "sr560_variants/as_drawn"
    s = SC.trimmed(SC.allocate(1000, "LN"), 1000, runs=runs)
    n = SC.run_noise(s, runs=runs)
    a = SC.run_ac(s, runs=runs)
    f3 = ac_summary(a["f"], a["h"])["f3db"]
    dn = {k: n["en"][k] / v - 1 for k, v in arch["noise"]["LN_1000"]["en"].items()}
    out = dict(noise_LN_1000_rel_diff=dn, f3db_1000_rel_diff=f3 / arch["ac"]["1000"]["f3db"] - 1)
    out["max_abs_rel_diff"] = max([abs(x) for x in dn.values()] + [abs(out["f3db_1000_rel_diff"])])
    print(f"check as drawn: largest relative difference from sr560_chain.json {out['max_abs_rel_diff']:.2e}",
          flush=True)
    return out


OP_NODES = ["da", "db", "sa", "sb", "tail", "out", "mid", "sv", "ref", "vtop", "out50"]


def check_operating_point() -> dict:
    """The deck whose operating point fell back to ngspice's transient op before every SR560 deck got
    sr560_frontend.NODESET: the as-drawn chain at a gain of 1000 (LN) with VTRIM = 1 V, the second deck
    of its offset trim.  Solved (1) without the nodeset, (2) with it, (3) with a nodeset at the state
    that (1) returns.  (2) and (3) must give the same solution; (1)'s state is not a DC solution if
    v(ref) differs from the 6.2 V of VREF, which feeds it through R125 with no DC load."""
    import dataclasses
    s = dataclasses.replace(SC.allocate(1000, "LN"), vtrim=1.0)
    src = "VA ina0 0 DC 0\nRSA ina0 ina 1 rnl\nRSB ina0 inb 1 rnl\n"
    ctl = ".control\nop\nprint " + " ".join(f"v({n})" for n in OP_NODES) + "\n.endc\n"
    base = SC.deck(s, "operating-point check", src, ctl)
    old = base.replace("RSA ina0 ina 1 rnl", "RSA ina0 ina 1m rnl").replace("RSB ina0 inb 1 rnl", "RSB ina0 inb 1m rnl")

    def solve(tag: str, text: str) -> dict:
        f = spice.run(f"sr560_variants/op_check/{tag}", text)
        return dict(fallback=spice.op_fallback(f), v={n: spice.printed(f, f"v({n})") for n in OP_NODES})

    out = dict(deck="as-drawn chain, gain 1000 (LN), VTRIM = 1 V (sr560_chain.trimmed's second deck)")
    out["one_mohm_without_nodeset"] = solve("one_mohm_without_nodeset", old.replace(FE.NODESET, ""))
    assert old.count("abstol=1e-15") == 1
    out["one_mohm_abstol_1e-12_without_nodeset"] = solve("one_mohm_abstol_1e-12_without_nodeset",
                                                         old.replace(FE.NODESET, "").replace("abstol=1e-15", "abstol=1e-12"))
    out["one_ohm_without_nodeset"] = solve("one_ohm_without_nodeset", base.replace(FE.NODESET, ""))
    out["without_nodeset"] = out["one_mohm_without_nodeset"]
    out["with_nodeset"] = solve("with_nodeset", base)
    ns = ".nodeset " + " ".join(f"v({n})={v:.9g}" for n, v in out["without_nodeset"]["v"].items()) + "\n"
    out["nodeset_at_fallback_state"] = solve("nodeset_at_fallback_state", base.replace(FE.NODESET, ns))
    a, b = out["with_nodeset"]["v"], out["nodeset_at_fallback_state"]["v"]
    out["max_abs_diff_with_vs_from_fallback_V"] = max(abs(a[n] - b[n]) for n in OP_NODES)
    # the trimmed state (gain 1000, the noise deck's sources): from FE.NODESET alone, and from the
    # continuation that sr560_chain.trimmed uses
    t = SC.trimmed(SC.allocate(1000, "LN"), 1000, runs="sr560_variants/op_check")
    nsrc = "VIN ina0 0 DC 0 AC 1\nRSA ina0 ina 1m rnl\nRSB 0 inb 1m rnl\n"      # the old 1-mOhm sources
    out["trimmed_vtrim_V"] = t.vtrim
    out["trimmed_generic_nodeset"] = solve("trimmed_generic_nodeset",
                                           SC.deck(dataclasses.replace(t, nodeset=None), "operating-point check", nsrc, ctl))
    out["trimmed_continuation"] = solve("trimmed_continuation", SC.deck(t, "operating-point check", nsrc, ctl))
    for k in ("one_mohm_without_nodeset", "one_mohm_abstol_1e-12_without_nodeset", "one_ohm_without_nodeset",
              "with_nodeset", "nodeset_at_fallback_state", "trimmed_generic_nodeset", "trimmed_continuation"):
        x = out[k]
        print(f"op check, {k}: fallback {x['fallback']}, v(ref) {x['v']['ref']:.4f}, v(da) {x['v']['da']:.4f}, "
              f"v(out) {x['v']['out']:+.6f}, v(out50) {x['v']['out50']:+.4f}", flush=True)
    return out


def check_cmrr_trim() -> dict:
    """The CMRR with ideal matching against the offset trim: the as-drawn chain at a gain of 1000 (LN),
    trimmed (sr560_chain.trimmed, as in sr560_chain.json) and with VTRIM = 0 V, the setting of the
    front end alone in sr560_frontend.py.  P103's wiper (VTRIM) feeds drain A through R121 (75 kOhm)
    while R120 (100 kOhm) loads drain B to ground, so with both drains at 6.2 V the trim decides how
    the tail current divides between the two JFETs: VTRIM = 0 takes 6.2 V / 75 kOhm - 6.2 V / 100 kOhm
    = 21 uA more through JFET A, and the trim (6.2 V - VTRIM) / 75 kOhm = 6.2 V / 100 kOhm balances
    them.  With identical JFETs, an unequal division leaves them with unequal g_m."""
    import dataclasses
    runs = "sr560_variants/cmrr_trim"
    t = SC.trimmed(SC.allocate(1000, "LN"), 1000, runs=runs)
    src = "VA ina0 0 DC 0\nRSA ina0 ina 1 rnl\nRSB ina0 inb 1 rnl\n"
    q = ["v(sa)", "v(sb)", "v(da)", "v(db)", "v(out)", "@j.xja.j1[id]", "@j.xjb.j1[id]", "@j.xja.j1[gm]",
         "@j.xjb.j1[gm]"]
    ctl = ".control\nop\nprint " + " ".join(q) + "\n.endc\n"
    out = dict(deck="as-drawn chain, gain 1000 (LN); sources SRC_DM and SRC_CM of sr560_chain.py")
    for label, vt in (("trimmed", t.vtrim), ("vtrim_0V", 0.0)):
        s = dataclasses.replace(t, vtrim=vt)
        f = SC._op(f"{runs}/{s.tag}/op_{label}",
                   lambda ns, s=s: SC.deck(dataclasses.replace(s, nodeset=ns), f"trim check {label}", src, ctl),
                   [s.nodeset, None, ""], None)
        op = {k: spice.printed(f, k) for k in q}
        dm = SC.run_ac(s, SC.SRC_DM, f"dm_{label}", runs=runs)
        cm = SC.run_ac(s, SC.SRC_CM, f"cm_{label}", runs=runs)
        c = 20 * np.log10(np.abs(dm["h"]) / np.abs(cm["h"]))
        out[label] = dict(vtrim=vt, op=op,
                          id_a_minus_b=op["@j.xja.j1[id]"] - op["@j.xjb.j1[id]"],
                          gm_a_over_b_minus_1=op["@j.xja.j1[gm]"] / op["@j.xjb.j1[gm]"] - 1,
                          cmrr={str(f0): float(spice.at(dm["f"], c, f0)) for f0 in (10, 1e3, 1e4, 1e5, 1e6)})
        r = out[label]
        print(f"cmrr vs trim, {label} (VTRIM {vt:.4f} V): I_D(A) - I_D(B) {r['id_a_minus_b'] * 1e6:+.2f} uA, "
              f"g_m(A)/g_m(B) - 1 {r['gm_a_over_b_minus_1']:+.3e}, v(sa) - v(sb) "
              f"{(op['v(sa)'] - op['v(sb)']) * 1e3:+.4f} mV; CMRR {r['cmrr']}", flush=True)
    return out


def main(args):
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    todo = [] if args == ["checks"] else (args or list(MODELS))
    subs, par = opamp_dynamics()
    res = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    res["description"] = __doc__.split("\n\n")[0]
    res["opamp_dynamics"] = par
    res.setdefault("models", {})
    res["check_operating_point"] = check_operating_point()
    res["check_as_drawn"] = check_as_drawn()
    res["check_cmrr_trim"] = check_cmrr_trim()
    for m in todo:
        res["models"][m] = run_model(m, subs)
        OUT.write_text(json.dumps(res, indent=1, default=float), encoding="utf-8", newline="\n")
    if "corrected" in res["models"]:
        bw = json.loads((spice.RESULTS / "sr560_bw_check.json").read_text(encoding="utf-8"))["chain"]
        res["check_corrected_vs_bw"] = {
            g: dict(this=res["models"]["corrected"]["ac"][g]["f3db"] / 1e6,
                    bw_check=bw[g]["results"]["f_datasheet_add_C406_C301_47p"]["f3db_MHz"])
            for g in ("1", "100", "1000")}
        for g, v in res["check_corrected_vs_bw"].items():
            v["rel_diff"] = v["this"] / v["bw_check"] - 1
        print("check corrected vs sr560_bw_check:", res["check_corrected_vs_bw"], flush=True)
    OUT.write_text(json.dumps(res, indent=1, default=float), encoding="utf-8", newline="\n")
    print(f"written {OUT.name}")


if __name__ == "__main__":
    main(sys.argv[1:])
