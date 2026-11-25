"""Quieter current sinks for the front end (Section 6.1 of the note).

Each source node's DC current leaves through a current sink: an NPN with R_T to -15 V, whose base
reference is adjusted once for each variant (frontend.sink_reference).  Its noise current enters the source node and reaches the input with
the weight R_F / G per side (Eq. (9)): 5 ohm at a gain of 100 but 50 ohm at a gain of 10, where the
sinks are the third-largest contributor, after R_G and the JFETs (Table 9 of the note).  The sink's
noise current has three parts:
  - R_T's thermal noise, sqrt(4kT / R_T) = sqrt(4kT I / V_RT), lowered by a larger drop V_RT;
  - the base current's shot noise, sqrt(2q I_C / beta), which reaches the collector almost in full
    because the base is held at AC ground; a higher beta, or a JFET (no gate current), lowers it;
  - the collector current's shot noise, suppressed by the degeneration, r_e / (r_e + R_T).
Variants: MMBT3904 (the adopted part, beta 122 in its model) with 2, 4 and 6 V across R_T;
BC817-25 (beta 339) with 2, 4 and 6 V; JFE150 (no gate current; its model calibrated in Section 3.4)
with 6 V.  (A J310 sink was tried first: the J310 card, from LTspice's standard.jft, has
KF = 46340f, which puts its gate-referred 1/f noise near 0.6 uV/rtHz at 10 kHz, so it was dropped.)
For comparison, the dominant term at a gain of 10, R_G, is lowered by halving R_F for that range:
R_F 250 ohm, R_G 55.6 ohm, with C_I + C_X doubled, D = C_I - C_X rescaled for the lower k_DM, and
C_node doubled.  For each, at gains of 10 and 100: the
complete loop's margins, the noise split (the sink's R_T and transistor parts separately), the
sink-limited lower end of the common-mode range, and the sink's dissipation.  L is evaluated for
dissipation only (its sinks carry 61 mA; their noise weight is 1.2 ohm).
Operating points: a variant whose decks' operating points fall back to ngspice's transient op (a
state that need not be a DC solution; the note's Section 5.1 and Appendix A) is evaluated again with
abstol = 1e-12 A, then with the sources tied to the gates through 1 ohm instead of 1 mOhm
(evaluate_checked, frontend.op_checked); each entry records its ties (r_in), the step that held
(op_how) and the decks that fell back before it (op_note).  No variant needs it without the servo;
with the servo of the note's Appendix B, the JFE150 sink at a gain of 100 did.

Writes ../sim/results/sink_options.json.  Usage: python sink_options.py [chain]; python sink_options.py
only "<case> | <label>" ... re-evaluates single entries and merges them into the archived file.
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace

import numpy as np

import frontend as F
import gain_options as GO
import models
import spice

VARIANTS = [
    ("MMBT3904, 2 V (adopted)", dict(sink="MMBT3904", v_sink=2.0, v_be_sink=0.66)),
    ("MMBT3904, 4 V", dict(sink="MMBT3904", v_sink=4.0, v_be_sink=0.66)),
    ("MMBT3904, 6 V", dict(sink="MMBT3904", v_sink=6.0, v_be_sink=0.66)),
    ("BC817-25, 2 V", dict(sink="BC817-25", v_sink=2.0, v_be_sink=0.66)),
    ("BC817-25, 4 V", dict(sink="BC817-25", v_sink=4.0, v_be_sink=0.66)),
    ("BC817-25, 6 V", dict(sink="BC817-25", v_sink=6.0, v_be_sink=0.66)),
    ("JFE150, 6 V", dict(sink="J:JFE150", v_sink=6.0, v_be_sink=-0.4)),
]
VTO = {"J310": -3.409, "JFE150": -0.975}      # the models' pinch-off voltages (sim/models/_lib/jfets.lib)
RF_HALF = dict(rf=250.0, rg=2 * 250.0 / 9, ci=23e-12, cx=5e-12, cnode=440e-12)
V_SAT_BJT = 0.5              # V_CE kept above saturation
FREQS = (10.0, 1e4, 1e6, 1e7)


def op_point(p: F.FE) -> dict:
    ctl = ".control\n" + spice.WR + "op\nprint v(sa) v(ea) v(vsink) @rta[i]\n.endc\n"
    f = spice.run(f"fe/{p.name}/op_sink", F.deck(p, f"op {p.name}", F.SRC_DM, ctl))
    v = {k: spice.printed(f, k) for k in ("v(sa)", "v(ea)", "v(vsink)", "@rta[i]")}
    i_t = abs(v["@rta[i]"])
    v_ce = v["v(sa)"] - v["v(ea)"]
    if p.sink.startswith("J:"):
        v_sat = (v["v(vsink)"] - v["v(ea)"]) - VTO[p.sink[2:]] + 0.3      # V_DS,sat + 0.3 V
    else:
        v_sat = V_SAT_BJT
    return dict(v_sa=v["v(sa)"], v_ea=v["v(ea)"], v_ctrl=v["v(vsink)"], i_sink=i_t, v_ce=v_ce,
                p_transistor=v_ce * i_t, p_rt=(v["v(ea)"] - p.vm) * i_t,
                vcm_min=v["v(ea)"] + v_sat - v["v(sa)"])       # sink-limited lower end of the CM range


def sink_split(nz: dict, gain: np.ndarray) -> dict:
    """Input-referred density of the sinks' R_T and of the sink transistors (both sides), and the
    transistor's sub-generators, at FREQS."""
    fr = nz["frequency"]
    parts = {"R_T": np.zeros_like(fr), "transistor": np.zeros_like(fr)}
    subs = {}
    for k, v in nz.items():
        if not k.startswith("onoise_") or k == "onoise_spectrum":
            continue
        b = k[len("onoise_"):]
        if b in ("rta", "rtb"):
            parts["R_T"] += v ** 2
        elif b in ("qta", "qtb", "j.xta.j1", "j.xtb.j1"):
            parts["transistor"] += v ** 2
        elif b.startswith(("qta_", "qtb_", "j.xta.j1_", "j.xtb.j1_")):
            tail = b.split("_", 1)[1] if b.startswith("q") else b.split("j1_", 1)[1]
            subs[tail] = subs.get(tail, np.zeros_like(fr)) + v ** 2
    out = {}
    for name, v2 in list(parts.items()) + [(f"transistor:{t}", v2) for t, v2 in subs.items()]:
        d = np.sqrt(v2) / gain
        out[name] = {f"{f0:g}": float(np.interp(np.log10(f0), np.log10(fr), d)) * 1e9 for f0 in FREQS}
    return out


def evaluate(p: F.FE) -> dict:
    r = dict(op=op_point(p), loop=GO.margins(p))
    ac = F.check_ac(p)
    nz, gain, how = GO.noise_checked(p, ac)
    grp = F.noise_groups(nz["nz"], gain)
    fr = nz["f"]
    r.update(noise_op=how, f3db=ac["f3db"], en={k: v * 1e9 for k, v in nz["en"].items()},
             sinks={f"{f0:g}": float(np.interp(np.log10(f0), np.log10(fr), grp["current sinks"])) * 1e9
                    for f0 in FREQS},
             split=sink_split(nz["nz"], gain),
             groups={g: {f"{f0:g}": float(np.interp(np.log10(f0), np.log10(fr), v)) * 1e9 for f0 in FREQS}
                     for g, v in grp.items()})
    return r


def variant(case: str, label: str, kw: dict) -> F.FE:
    tag = label.split(" (")[0].replace(", ", "_").replace(" ", "").replace("-", "")
    return replace(F.CASES[case], name=f"{case}_sink_{tag}", **kw)


def evaluate_checked(p: F.FE) -> dict:
    """evaluate(p) through frontend.op_checked: if the operating point of any of its decks fell back to
    ngspice's transient op (spice.FALLBACKS), whose end state need not be a DC solution, evaluate again
    with abstol = 1e-12 A instead of 1e-15 A, then with the sources tied to the gates through 1 ohm instead
    of 1 mOhm (frontend.FE.r_in, noiseless), then with both (the note's Section 5.1 and Appendix A).  No
    variant needs it without the servo.  With the servo of the note's Appendix B in the netlists, every
    deck of the JFE150 sink at a gain of 100 fell back, with 1-mOhm ties, to a state with the source nodes
    at -0.95 V and the input gates conducting; 1-ohm ties made them converge (op_pitfall.py reproduces
    it).  The entry records the ties it was evaluated with (r_in), the op_checked step (op_how) and the
    decks that fell back before it (op_note)."""
    r, how, note = F.op_checked(evaluate, p,
                                keep=lambda r_: {f"fe/{p.name}/noise"} if r_.get("noise_op") == "nodeset" else set())
    r.update(r_in=1.0 if "ties" in how else p.r_in, op_how=how, op_note=note)
    return r


def run_variant(case: str, label: str, kw: dict, res: dict) -> None:
    """Evaluate one variant into res['<case> | <label>']."""
    p = variant(case, label, kw)
    try:
        r = evaluate_checked(p)
        if r["f3db"] > 100e6:        # an operating point that the noise check cannot catch:
            raise RuntimeError(      # wrong in the AC deck as well
                f"implausible operating point: f3dB {r['f3db'] / 1e6:.0f} MHz, source node "
                f"{r['op']['v_sa']:.2f} V")
    except RuntimeError as exc:
        res[f"{case} | {label}"] = dict(failed=str(exc)[:200], op=op_point(p))
        print(f"{case:5s} {label:26s} FAILED: {str(exc)[:160]}", flush=True)
        return
    res[f"{case} | {label}"] = r
    o, e, lp = r["op"], r["en"], r["loop"]
    sp = r["split"]
    print(f"{case:5s} {label:26s} white {e['10000.0']:.3f} (10 Hz {e['10']:.2f}, 10 MHz {e['10000000.0']:.2f}) "
          f"sinks {r['sinks']['10000']:.3f} [R_T {sp['R_T']['10000']:.3f}, transistor {sp['transistor']['10000']:.3f}; "
          + ", ".join(f"{k.split(':')[1]} {v['10000']:.3f}" for k, v in sp.items()
                      if k.startswith("transistor:") and v["10000"] > 0.003)
          + f"] sinks at 10 Hz {r['sinks']['10']:.3f} | DM {lp['dm']['pm']}/{lp['dm']['gm_db']}/{lp['dm']['mod']} "
          f"CM {lp['cm']['pm']}/{lp['cm']['gm_db']}/{lp['cm']['mod']} | f3dB {r['f3db'] / 1e6:.1f} MHz | "
          f"I {o['i_sink'] * 1e3:.2f} mA, V_CE {o['v_ce']:.2f} V, P {o['p_transistor'] * 1e3:.0f} + "
          f"{o['p_rt'] * 1e3:.0f} mW, V_CM,min {o['vcm_min']:.2f} V, source node {o['v_sa']:.3f} V "
          f"[{r['noise_op']}; ties {r['r_in']:g} ohm"
          f"{'; ' + r['op_note'] + '; evaluated with ' + r['op_how'] if r['op_note'] else ''}]", flush=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    res = {}
    for case in ("H10", "H100"):
        for label, kw in VARIANTS:
            run_variant(case, label, kw, res)
    p = replace(F.CASES["H10"], name="H10_rf250", **RF_HALF)
    r = evaluate(p)
    res["H10 | R_F 250 ohm for this range (MMBT3904, 2 V)"] = r
    e, lp = r["en"], r["loop"]
    print(f"H10   R_F 250, R_G 55.6 ohm       white {e['10000.0']:.3f} (10 Hz {e['10']:.2f}, 1 MHz {e['1000000.0']:.2f}, "
          f"10 MHz {e['10000000.0']:.2f}) sinks {r['sinks']['10000']:.3f} | DM {lp['dm']['pm']}/{lp['dm']['gm_db']}/"
          f"{lp['dm']['mod']} CM {lp['cm']['pm']}/{lp['cm']['gm_db']}/{lp['cm']['mod']} | f3dB {r['f3db'] / 1e6:.1f} MHz "
          f"[{r['noise_op']}]", flush=True)
    for label, kw in VARIANTS[:3]:
        tag = label.split(" (")[0].replace(", ", "_").replace(" ", "").replace("-", "")
        p = replace(F.CASES["L200"], name=f"L200_sink_{tag}", **kw)
        o = op_point(p)
        res[f"L200 | {label}"] = dict(op=o)
        print(f"L200  {label:26s} I {o['i_sink'] * 1e3:.2f} mA, V_CE {o['v_ce']:.2f} V, "
              f"P {o['p_transistor'] * 1e3:.0f} + {o['p_rt'] * 1e3:.0f} mW, V_CM,min {o['vcm_min']:.2f} V", flush=True)
    (spice.RESULTS / "sink_options.json").write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")


def chain_effect():
    """The sink variants' effect on the complete chain wherever it uses the gain-10 front end: the
    high-reserve mode (H_HR) at total gains of 100 and 1000, and H_LN at a total gain of 10.
    frontend.CASES['H10'] is replaced for each variant and restored afterwards.  Adds the
    'chain | ...' entries to ../sim/results/sink_options.json."""
    import chain
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    path = spice.RESULTS / "sink_options.json"
    res = json.loads(path.read_text(encoding="utf-8"))
    orig = F.CASES["H10"]
    picks = [VARIANTS[0], VARIANTS[4], VARIANTS[5], VARIANTS[6], ("R_F 250 ohm (MMBT3904, 2 V)", RF_HALF)]
    try:
        for label, kw in picks:
            tag = "".join(ch for ch in label.split(" (")[0] if ch.isalnum())
            F.CASES["H10"] = replace(orig, name=f"H10_chain_{tag}", **kw)
            for mode, g in (("H_HR", 100), ("H_HR", 1000), ("H_LN", 10)):
                r = chain.run_noise(chain.allocate(g, mode), run_suffix=f"_sink_{tag}")
                e = {k: v * 1e9 for k, v in r["en"].items()}
                res[f"chain | {label} | {mode} {g}"] = dict(en=e)
                print(f"chain {mode} {g:5d} {label:30s} 10 Hz {e['10']:.2f}  1 kHz {e['1000.0']:.3f}  "
                      f"100 kHz {e['100000.0']:.3f}  10 MHz {e['10000000.0']:.2f}", flush=True)
    finally:
        F.CASES["H10"] = orig
    path.write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")


def only(keys: list[str]) -> None:
    """Re-evaluate the entries keys ('<case> | <label>') of sink_options.json as main() does, and merge
    them into it."""
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    path = spice.RESULTS / "sink_options.json"
    res = json.loads(path.read_text(encoding="utf-8"))
    labels = dict(VARIANTS)
    for key in keys:
        case, label = key.split(" | ", 1)
        run_variant(case, label, labels[label], res)
    path.write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    if sys.argv[1:] == ["chain"]:
        chain_effect()
    elif sys.argv[1:2] == ["only"]:
        only(sys.argv[2:])
    else:
        main()
