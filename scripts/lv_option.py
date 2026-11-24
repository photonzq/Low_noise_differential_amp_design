"""The low-voltage alternative for the H front end's loop op amps (Section 4.3.1 of the note, the last
row of Table 6b): an ADA4899 (unity-gain stable) on its own +/-5 V rails (the oa_rail field of
frontend.FE), the summing node at V_ref = +3 V and the bootstrap at V_BS = 1.2 V; H at a gain of 100
(R_F 500 ohm, R_G 10.1 ohm, two JFE2140 per side, LSBF862 cascodes, sinks to -15 V) otherwise as
built.  ADI's model as published (no noise correction; its 1/f is unverified, Section 4.3.1).

Compensation.  With S = C_I + C_X and D = C_I - C_X (Eqs. (10), (10a) of the note):
    T_DM ~ k_DM / (j w D R_F),   T_CM ~ 1 / (j w S R_F),   k_DM = g_m R_G / (2 + g_m R_G)
    beta_CM = S / (S + C_node + C_par),   beta_DM = D / (S + C_node + C_par)
A unity-gain-stable op amp tolerates beta up to 1, so C_node can stay small.  Every case is judged
on the complete loop broken at the op amp's output pin (frontend.check_loop_out, Middlebrook's
double injection, DM and CM):
    phase margin  PM = 180 deg + arg T  where |T| = 1     (the smallest over all crossings)
    gain margin   GM = -20 log10 |T|    where arg T = -180 deg (mod 360) with |T| < 1
    modulus margin    min |1 + T|
and on the front end's differential response (frontend.check_ac): f_-3dB, and the peaking
20 log10(max|H| / |H(1 Hz)|).

  scan 1: C_node = 0, S in {8, 10.6, 14} pF x D in {1.77, 2.5, 3.5} pF   -> (PM, GM, [f_c / MHz])
  scan 2: C_node = 0, (S, D) in {(20, 2.5), (20, 3), (28, 2.5), (28, 3), (40, 3)} pF
                                                              -> (PM, GM, [f_c / MHz], min|1 + T|)
  scan 3: (S, D, C_node) in {(14, 2.5, 22), (14, 2.5, 47), (14, 2.5, 100), (10.6, 2.5, 47)} pF
  -> ../sim/results/lv_option_scan.json

  final: C_I 8.5 pF, C_X 5.5 pF (S 14, D 3), C_node 22 pF: margins (PM, GM, crossovers, modulus),
  f_-3dB, peaking, the input-referred noise e_n(f) at 1 Hz ... 10 MHz (frontend.check_noise; the
  adopted H100 with the THS4021 alongside), and the peak-to-peak swing of v(oa), v(ob), v(ca),
  v(sa) after 0.3 us of a 1 us transient at 0.05 ns steps with quiet inputs, 50-ohm sources and
  the input network (osc_check.run).  -> ../sim/results/lv_option.json

Operating point and common-mode range (an estimate from the operating point, not a simulation of
the range).  From the operating point at V_CM = 0 (gate at 0 V):
    V_GS1  = V(s) - V(g)                 input JFET: the source sits V_GS1 above the gate
    V_BS   = V(b) - V(s) = R_BS I_BS     bootstrap (R_BS = 1.2 kohm, I_BS from R_UP)
    |V_GS2| = V(d) - V(b)                cascode (N-JFET, gate on the bootstrap node b)
    V_DS1  = V(d) - V(s) = V_BS + |V_GS2|
    V_DS2  = V(c) - V(d)                 the cascode's own V_DS; V(c) is held at V_ref by the op amp
    V_O    = V(o) = V_CM + V_GS1         the adjusted sink reference leaves no DC current in R_F
The stack g -> s -> b -> d follows the input, c does not.  A differential output V_od at the front
end's gain G puts V_CM +- V_od / (2G) on the gates and V_CM + V_GS1 +- V_od / 2 on the outputs.
    upper limit, cascode:  V_DS2 >= V_DS,sat2 + V_od / (2G),  V_DS,sat2 = sqrt(I_D / beta_2)
                           (square law with the LSBF862 card's BETA; I_D = 5 mA):
        V_CM,max,c   = V(c) - V_GS1 - V_DS1 - V_DS,sat2 - V_od / (2G)
      and with the 1 V minimum used for the adopted design's +3.7 V (Section 4.2: V_DS,sat
      plus room for the signal):
        V_CM,max,1V  = V(c) - V_GS1 - V_DS1 - 1 V
    op amps' output swing [V_OL, V_OH] (each model on its rails, R_F = 500 ohm as its load):
        V_CM,min,o   = V_OL - V_GS1 + V_od / 2,      V_CM,max,o = V_OH - V_GS1 - V_od / 2
    current sink (emitter at V_E, V_CE kept above 0.5 V as in sink_options.py):
        V_CM,min,T   = V_E + 0.5 V - V_GS1
    range = [max(V_CM,min,o, V_CM,min,T), min(V_CM,max,c, V_CM,max,o)]
  evaluated for V_od = 0, 1 V and 10 V (the front end's differential output at full scale with the
  chain's 10 V full-scale output: 1 V at total gains of 1000 and up, 10 V at a total gain of 100),
  for the low-voltage option and, with the same equations, for the adopted H100 (THS4021 on
  +/-15 V, V_ref 9 V, V_BS 3.5 V).  The output differential that would put V_CM,min,o at a given
  value x is V_od = 2 (x + V_GS1 - V_OL).
  The op amps' swing: open loop, inverting input grounded, the non-inverting input swept over
  +-50 mV, the output loaded with R_F to ground (.dc); V_OH, V_OL = the extremes of v(out); also
  unloaded, and closed loop (an inverting stage of gain -2 overdriven, R_F as load) as a check.
  For the ADA4899 the range is also evaluated with the +-3.8 V swing that the note assumes.  The
  ADA4899's input common-mode range: inputs held at V_in by a gain-of-two inverting stage fed with
  2 V_in (output near 0 V), V_in swept across the rails; the range is where |V(inp) - V(inn)| < 1 mV.
  -> ../sim/results/lv_option_range.json

An existing results file is overwritten only if the regenerated content is identical; otherwise
the new content goes to <name>_regen.json and the differences are printed.

Usage: python lv_option.py [scan] [final] [range] [notran]      (default: scan final range)
       notran: the final step without the transient; it then writes lv_option_notran.json only.
"""
from __future__ import annotations

import json
import math
import re
import sys
import time
from dataclasses import replace

import numpy as np

import blocks
import frontend as F
import models
import osc_check as O
import spice

CASE_TEXT = "H100 with ADA4899 on +/-5 V, vref 3 V, vbs 1.2 V, C_I 8.5 pF, C_X 5.5 pF, C_node 22 pF"
LV = dict(opamp="ADA4899", oa_rail=5.0, vref=3.0, vbs=1.2)       # the low-voltage changes to H100
SCAN1_S = (8e-12, 10.6e-12, 14e-12)
SCAN1_D = (1.77e-12, 2.5e-12, 3.5e-12)
SCAN2 = ((20e-12, 2.5e-12), (20e-12, 3.0e-12), (28e-12, 2.5e-12), (28e-12, 3.0e-12), (40e-12, 3.0e-12))
SCAN3 = ((14e-12, 2.5e-12, 22e-12), (14e-12, 2.5e-12, 47e-12), (14e-12, 2.5e-12, 100e-12),
         (10.6e-12, 2.5e-12, 47e-12))
V_CE_MIN = 0.5            # the sink's V_CE kept above saturation (sink_options.V_SAT_BJT)
V_DS_C_MIN_ADOPTED = 1.0  # the cascode's minimum V_DS behind the adopted design's +3.7 V (Section 4.2)


def lv_base(**kw) -> F.FE:
    kw.setdefault("name", "H100_LV")
    return replace(F.CASES["H100"], **LV, **kw)


# ---------------------------------------------------------------------------------------------
# results files
# ---------------------------------------------------------------------------------------------
def _flat(x, path=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from _flat(v, f"{path}/{k}")
    elif isinstance(x, (list, tuple)):
        for i, v in enumerate(x):
            yield from _flat(v, f"{path}[{i}]")
    else:
        yield path, x


def save_checked(name: str, data: dict) -> str:
    """Write RESULTS/name unless it exists with other content; then write <stem>_regen.json and
    print every value that differs."""
    path = spice.RESULTS / name
    text = json.dumps(data, indent=1)
    if not path.exists():
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"{name}: written (new)")
        return "new"
    old_text = path.read_text(encoding="utf-8")
    if old_text == text:
        print(f"{name}: the regenerated content is identical to the archived file (left as it is)")
        return "identical"
    old, new = dict(_flat(json.loads(old_text))), dict(_flat(json.loads(text)))
    regen = path.with_name(path.stem + "_regen.json")
    regen.write_text(text, encoding="utf-8", newline="\n")
    print(f"{name}: the regenerated content differs; written to {regen.name}")
    for k in sorted(set(old) | set(new)):
        a, b = old.get(k, "<missing>"), new.get(k, "<missing>")
        if a != b:
            rel = (f"  (rel. {abs(b - a) / max(abs(a), 1e-300):.2e})"
                   if isinstance(a, (int, float)) and isinstance(b, (int, float)) else "")
            print(f"    {k}: archived {a!r}, regenerated {b!r}{rel}")
    return "differs"


# ---------------------------------------------------------------------------------------------
# compensation scan and the final values
# ---------------------------------------------------------------------------------------------
def loop_entry(p: F.FE, modulus: bool) -> dict:
    out = {}
    for mode in ("dm", "cm"):
        r = F.check_loop_out(p, mode)
        fr, t = r["T"]
        e = (round(r["pm"], 1), round(r["gm_db"], 1), [round(x["f"] / 1e6, 1) for x in r["crossings"]])
        if modulus:
            e += (round(float(np.abs(1 + t).min()), 2),)
        out[mode] = e
    ac = F.check_ac(p)
    print(p.name, out, f"f3dB {ac['f3db'] / 1e6:.1f} MHz peak {ac['peak_db']:.2f}", flush=True)
    return dict(out=out, f3db=ac["f3db"], peak=ac["peak_db"])


def scan() -> dict:
    res = {}
    # scan 1 (C_node = 0); its base also gives the operating point printed first
    base = lv_base(cnode=0.0, ci=6.19e-12, cx=4.42e-12)
    print("gain", base.gain)
    op = F.check_op(base)
    print({k: round(v, 4) for k, v in op.items()} if "error" not in op else op)
    for s in SCAN1_S:
        for d in SCAN1_D:
            p = replace(base, name=f"H100_LV_S{s * 1e12:g}_D{d * 1e12:g}", ci=(s + d) / 2, cx=(s - d) / 2, cnode=0.0)
            res[p.name] = loop_entry(p, modulus=False)
    # scan 2 (C_node = 0, larger S)
    base = lv_base(cnode=0.0)
    for s, d in SCAN2:
        p = replace(base, name=f"H100_LV_S{s * 1e12:g}_D{d * 1e12:g}", ci=(s + d) / 2, cx=(s - d) / 2)
        res[p.name] = loop_entry(p, modulus=True)
    # scan 3 (a small C_node)
    base = lv_base()
    for s, d, cn in SCAN3:
        p = replace(base, name=f"H100_LV_S{s * 1e12:g}_D{d * 1e12:g}_CN{cn * 1e12:g}", ci=(s + d) / 2,
                    cx=(s - d) / 2, cnode=cn)
        res[p.name] = loop_entry(p, modulus=True)
    return res


def final(tran: bool = True) -> dict:
    p = lv_base(ci=8.5e-12, cx=5.5e-12, cnode=22e-12)
    out = {}
    for mode in ("dm", "cm"):
        r = F.check_loop_out(p, mode)
        fr, t = r["T"]
        out[mode] = dict(pm=r["pm"], gm_db=r["gm_db"], fc=[x["f"] for x in r["crossings"]],
                         modulus=float(np.abs(1 + t).min()))
    ac = F.check_ac(p)
    nz = F.check_noise(p)
    osc = None
    if tran:
        t0 = time.time()
        osc = O.run(replace(p, name="H100_LV_osc"))
        print(f"transient: {time.time() - t0:.1f} s", flush=True)
    # the adopted H100 (THS4021) for comparison; its own run folder, same netlist as CASES["H100"]
    ref = F.check_noise(replace(F.CASES["H100"], name="H100_lv_reference"))
    res = dict(case=CASE_TEXT, loop=out, f3db=ac["f3db"], peak=ac["peak_db"],
               en_LV={k: v * 1e9 for k, v in nz["en"].items()},
               en_THS4021={k: v * 1e9 for k, v in ref["en"].items()})
    if osc is not None:
        # the node entries only: osc_check.run also records the bench and the parts (C_I, C_X, ...)
        res["osc"] = {k: v["pkpk"] for k, v in osc.items() if isinstance(v, dict) and "pkpk" in v}
    print(json.dumps(res, indent=1))
    return res


# ---------------------------------------------------------------------------------------------
# operating point and common-mode range
# ---------------------------------------------------------------------------------------------
OP_NODES = ("v(ga)", "v(sa)", "v(ba)", "v(da1)", "v(ca)", "v(oa)", "v(ob)", "v(vref)", "v(ea)", "v(vsink)")


def op_point(p: F.FE) -> dict:
    ctl = (".control\n" + spice.WR + "op\nprint " + " ".join(OP_NODES) + "\n"
           "print @j.xja1.j1[id] @j.xca1.j1[id] @rupa[i] @rda[i]\n.endc\n")
    f = spice.run(f"fe/{p.name}/op_range", F.deck(p, f"op {p.name}", F.SRC_DM, ctl))
    keys = OP_NODES + ("@j.xja1.j1[id]", "@j.xca1.j1[id]", "@rupa[i]", "@rda[i]")
    return {k: spice.printed(f, k) for k in keys}


SPICE_SUFFIX = (("meg", 1e6), ("f", 1e-15), ("p", 1e-12), ("n", 1e-9), ("u", 1e-6), ("m", 1e-3),
                ("k", 1e3), ("g", 1e9), ("t", 1e12))


def spice_number(s: str) -> float:
    m = re.match(r"([-+]?[0-9.]+(?:[eE][-+]?[0-9]+)?)([a-zA-Z]*)$", s)
    x, suf = float(m.group(1)), m.group(2).lower()
    for p, k in SPICE_SUFFIX:
        if suf.startswith(p):
            return x * k
    return x


def jfet_card(name: str) -> dict:
    """Parameters of a JFET .model card in the prepared library ../sim/models/_lib/jfets.lib."""
    text = (spice.LIB / "jfets.lib").read_text(encoding="utf-8", errors="replace")
    m = re.search(rf"^\.model\s+{re.escape(name)}\s+NJF\s*\((.*?)\)\s*$", text, re.M | re.I)
    return {k.upper(): spice_number(v) for k, v in re.findall(r"(\w+)\s*=\s*(\S+)", m.group(1))}


def opamp_swing(part: str, rail: float, r_load: float) -> dict:
    """V_OH, V_OL of OA_<part> on +/-rail: open loop, overdriven by +-50 mV, R_load to ground."""
    deck = (f"* {part} output swing, +/-{rail:g} V, {r_load:g} ohm\n{spice.OPTIONS}.options rshunt=1e12\n"
            f"{spice.lib('opamps.lib')}{blocks.COMMON}VP vp 0 {rail:g}\nVM vm 0 {-rail:g}\n"
            f"VD inp 0 DC 0\nX1 inp 0 out vp vm OA_{part}\nRL out 0 {r_load:g} rnl\n"
            ".control\n" + spice.WR + "dc VD -0.05 0.05 0.001\nwrdata swing.txt v(out)\n.endc\n.end\n")
    f = spice.run(f"lv_option/swing_{part}_{r_load:g}", deck)
    d = spice.read_table(f / "swing.txt")
    v = d["v(out)"]
    return dict(v_oh=float(v.max()), v_ol=float(v.min()), r_load=r_load, rail=rail)


def opamp_clip(part: str, rail: float, r_load: float) -> dict:
    """The same limits closed-loop: an inverting stage of gain -2 driven over +-(0.6 rail), so that
    it clips (its inputs stay at 0 V, inside any input range)."""
    deck = (f"* {part} closed-loop clipping, +/-{rail:g} V, {r_load:g} ohm\n{spice.OPTIONS}.options rshunt=1e12\n"
            f"{spice.lib('opamps.lib')}{blocks.COMMON}VP vp 0 {rail:g}\nVM vm 0 {-rail:g}\n"
            f"VIN in 0 DC 0\nR1 in inn 1k rnl\nR2 inn out 2k rnl\nX1 0 inn out vp vm OA_{part}\n"
            f"RL out 0 {r_load:g} rnl\n.control\n" + spice.WR
            + f"dc VIN {-0.6 * rail:g} {0.6 * rail:g} {0.002 * rail:g}\nwrdata clip.txt v(out)\n.endc\n.end\n")
    f = spice.run(f"lv_option/clip_{part}_{r_load:g}", deck)
    v = spice.read_table(f / "clip.txt")["v(out)"]
    return dict(v_oh=float(v.max()), v_ol=float(v.min()), r_load=r_load, rail=rail)


def opamp_input_range(part: str, rail: float, tol: float = 1e-3) -> dict:
    """Input common-mode range of OA_<part> on +/-rail: inputs at V_in, output near 0 V (gain-of-
    two inverting stage fed with 2 V_in), V_in swept; range where |V(inp) - V(inn)| < tol."""
    deck = (f"* {part} input common-mode range, +/-{rail:g} V\n{spice.OPTIONS}.options rshunt=1e12\n"
            f"{spice.lib('opamps.lib')}{blocks.COMMON}VP vp 0 {rail:g}\nVM vm 0 {-rail:g}\n"
            "VIN inp 0 DC 0\nE2 a 0 inp 0 2\nR1 a inn 1k rnl\nR2 inn out 1k rnl\n"
            f"X1 inp inn out vp vm OA_{part}\n"
            ".control\n" + spice.WR + f"dc VIN {-rail:g} {rail:g} 0.01\nwrdata cmr.txt v(inn) v(out)\n.endc\n.end\n")
    f = spice.run(f"lv_option/input_range_{part}", deck)
    d = spice.read_table(f / "cmr.txt")
    vin = d["v-sweep"] if "v-sweep" in d else d[list(d)[0]]
    err = np.abs(vin - d["v(inn)"])
    ok = vin[err < tol]
    return dict(v_in_min=float(ok.min()), v_in_max=float(ok.max()), tol=tol, rail=rail)


def cm_range(op: dict, v_c: float, gain: float, sw: dict, v_ds_sat2: float, v_od: float) -> dict:
    v_gs1 = op["v(sa)"] - op["v(ga)"]
    v_ds1 = op["v(da1)"] - op["v(sa)"]
    hi_c = v_c - v_gs1 - v_ds1 - v_ds_sat2 - v_od / (2 * gain)
    hi_1v = v_c - v_gs1 - v_ds1 - V_DS_C_MIN_ADOPTED
    lo_o = sw["v_ol"] - v_gs1 + v_od / 2
    hi_o = sw["v_oh"] - v_gs1 - v_od / 2
    lo_t = op["v(ea)"] + V_CE_MIN - v_gs1
    lo = max(lo_o, lo_t)
    return dict(V_od=v_od, V_CM_max_cascode=hi_c, V_CM_max_cascode_1V=hi_1v, V_CM_min_swing=lo_o,
                V_CM_max_swing=hi_o, V_CM_min_sink=lo_t, range=[lo, min(hi_c, hi_o)],
                range_1V=[lo, min(hi_1v, hi_o)], empty=lo > min(hi_c, hi_o))


def cm_range_all() -> dict:
    card = jfet_card("LSBF862_M")
    out = {}
    designs = (("low-voltage (ADA4899, +/-5 V, V_ref 3 V, V_BS 1.2 V)",
                lv_base(name="H100_LV_range", ci=8.5e-12, cx=5.5e-12, cnode=22e-12), "ADA4899", 5.0),
               ("adopted (THS4021, +/-15 V, V_ref 9 V, V_BS 3.5 V)",
                replace(F.CASES["H100"], name="H100_lv_range_ref"), "THS4021", 15.0))
    for label, p, part, rail in designs:
        op = op_point(p)
        i_d = op["@j.xca1.j1[id]"]
        v_ds_sat2 = math.sqrt(abs(i_d) / card["BETA"])
        v_gs1 = op["v(sa)"] - op["v(ga)"]
        sw = opamp_swing(part, rail, p.rf)
        st = dict(V_GS1=v_gs1, V_BS=op["v(ba)"] - op["v(sa)"], V_GS2_abs=op["v(da1)"] - op["v(ba)"],
                  V_DS1=op["v(da1)"] - op["v(sa)"], V_DS2=op["v(ca)"] - op["v(da1)"],
                  V_O_minus_V_CM=op["v(oa)"] - op["v(ga)"], V_ref_held=op["v(ca)"], V_vref=op["v(vref)"],
                  V_E=op["v(ea)"], I_D_cascode=i_d, I_D_input=op["@j.xja1.j1[id]"], I_BS=op["@rupa[i]"],
                  I_RD=op["@rda[i]"], V_DS_sat2=v_ds_sat2, V_GS2_square_law=card["VTO"] + v_ds_sat2,
                  LSBF862=dict(VTO=card["VTO"], BETA=card["BETA"]))
        sw_free = opamp_swing(part, rail, 1e6)
        clip = opamp_clip(part, rail, p.rf)
        rows = [cm_range(op, op["v(ca)"], p.gain, sw, v_ds_sat2, v) for v in (0.0, 1.0, 10.0)]
        v_od_max = 2 * min(sw["v_oh"] - v_gs1, v_gs1 - sw["v_ol"])           # at V_CM = 0
        out[label] = dict(op=op, stack=st, swing=sw, swing_unloaded=sw_free, clip_closed_loop=clip,
                          gain=p.gain, ranges=rows, V_od_max_at_V_CM_0=v_od_max,
                          V_od_for_V_CM_min_minus_0p9=2 * (-0.9 + v_gs1 - sw["v_ol"]))
        if part == "ADA4899":
            # the same with the +-3.8 V swing that the note assumes (not the model's)
            sw38 = dict(v_oh=3.8, v_ol=-3.8, r_load=p.rf, rail=rail)
            out[label]["ranges_with_3p8V_swing"] = [cm_range(op, op["v(ca)"], p.gain, sw38, v_ds_sat2, v)
                                                    for v in (0.0, 1.0, 10.0)]
            out[label]["V_od_for_V_CM_min_minus_0p9_with_3p8V"] = 2 * (-0.9 + v_gs1 + 3.8)
        print(f"\n{label}:")
        print("  op: " + ", ".join(f"{k} {v:.4f}" for k, v in op.items() if k.startswith("v(")))
        print(f"  V_GS1 {st['V_GS1']:.3f} V, V_BS {st['V_BS']:.3f} V, |V_GS2| {st['V_GS2_abs']:.3f} V, "
              f"V_DS1 {st['V_DS1']:.3f} V, V_DS2 {st['V_DS2']:.3f} V, outputs at V_CM + {st['V_O_minus_V_CM']:.3f} V, "
              f"summing node {st['V_ref_held']:.4f} V (vref {st['V_vref']:.4f} V)")
        print(f"  I_D {i_d * 1e3:.3f} mA per JFET, I_BS {st['I_BS'] * 1e3:.3f} mA; cascode V_DS,sat2 = sqrt(I_D/beta) "
              f"= {v_ds_sat2:.3f} V (V_GS2 by the square law {st['V_GS2_square_law']:.3f} V)")
        print(f"  {part} swing on +/-{rail:g} V with {p.rf:g} ohm: {sw['v_ol']:+.3f} ... {sw['v_oh']:+.3f} V "
              f"(unloaded {sw_free['v_ol']:+.3f} ... {sw_free['v_oh']:+.3f} V; closed loop, {p.rf:g} ohm: "
              f"{clip['v_ol']:+.3f} ... {clip['v_oh']:+.3f} V); largest differential output at V_CM = 0: {v_od_max:.2f} V")

        def show(rs, tag):
            for r in rs:
                print(f"  {tag}V_od {r['V_od']:4.1f} V: cascode (sat + signal) {r['V_CM_max_cascode']:+.2f}, cascode (1 V) "
                      f"{r['V_CM_max_cascode_1V']:+.2f}, swing {r['V_CM_min_swing']:+.2f} ... {r['V_CM_max_swing']:+.2f}, "
                      f"sink {r['V_CM_min_sink']:+.2f} -> range {r['range'][0]:+.2f} ... {r['range'][1]:+.2f} V"
                      f"{' (empty)' if r['empty'] else ''}; with the 1 V rule {r['range_1V'][0]:+.2f} ... "
                      f"{r['range_1V'][1]:+.2f} V")
        show(rows, "")
        print(f"  V_od that puts the swing-limited lower end at -0.9 V: {out[label]['V_od_for_V_CM_min_minus_0p9']:.2f} V")
        if part == "ADA4899":
            show(out[label]["ranges_with_3p8V_swing"], "+-3.8 V swing: ")
            print(f"  +-3.8 V swing: V_od that puts the lower end at -0.9 V: "
                  f"{out[label]['V_od_for_V_CM_min_minus_0p9_with_3p8V']:.2f} V")
    ir = opamp_input_range("ADA4899", 5.0)
    out["ADA4899 input common-mode range, +/-5 V"] = ir
    print(f"\nADA4899 input common-mode range on +/-5 V (|V(inp) - V(inn)| < {ir['tol'] * 1e3:g} mV): "
          f"{ir['v_in_min']:+.2f} ... {ir['v_in_max']:+.2f} V")
    return out


def main(args):
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    steps = [a for a in args if a in ("scan", "final", "range")] or ["scan", "final", "range"]
    tran = "notran" not in args
    if "scan" in steps:
        save_checked("lv_option_scan.json", scan())
    if "final" in steps:
        res = final(tran)
        save_checked("lv_option.json" if tran else "lv_option_notran.json", res)
    if "range" in steps:
        res = cm_range_all()
        (spice.RESULTS / "lv_option_range.json").write_text(json.dumps(res, indent=1), encoding="utf-8",
                                                            newline="\n")


if __name__ == "__main__":
    main(sys.argv[1:])
