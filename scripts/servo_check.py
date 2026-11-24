"""Does the front end need its common-mode servo, and can the servo latch without its clamp (Section 4.2)?

The servo (frontend.netlist, cm_servo): e = [(v_oa - v_sa) + (v_ob - v_sb)] / 2 drives 1 uS into 1 uF, an
integrator with unity gain at 0.16 Hz; its output, limited to V_M + 1 V ... V_M + V_RT + 3 V and filtered by
1 kOhm and 10 uF, is the base reference vsink of both current sinks (QTx: collector at the source node sx,
emitter through R_T to V_M).  The front ends of the note have no servo: their reference is a fixed
voltage, adjusted once (frontend.sink_reference); this check is Appendix B's (the servo as an option).

(a) What the servo sets: H at a gain of 100 and L at a gain of 201 (frontend.CASES H100, L200), DC operating
    points, input common mode 0 V unless stated.
      servo          the adopted design
      fixed          no servo, the reference fixed at the servo's settled value (vsink0): the same operating
                     point; its AC response and noise are compared with the servo's
      design         no servo, the reference at its design value V_M + V_RT + 0.66 V (FE.v_be_sink)
      +20 mV, -20 mV no servo, the reference 20 mV above or below 'fixed': as a sink whose V_BE is 20 mV
                     lower or higher than the model's (the spread between parts), or an error of the reference
      52 C           +25 K (ngspice .temp), with the servo and with 'fixed'
      CM -8 V, +3 V  input common mode, with the servo and with 'fixed': R_UP's current, and with it the
                     current the sinks must take, follows the input; a fixed sink does not
    For each: the outputs against their sources, v(ox) - v(sx) (= R_F I_RF); the sinks' and R_UP's currents.
(b) Can it latch?  The servo loop opened (no servo) and the reference swept from -14 V to +14 V (.dc, each
    point starting from the last): e against the reference.  The closed loop's equilibria are the zeros of
    e where e rises with the reference (stable: the servo lowers the reference when e > 0), and a limit of
    the servo's output where e keeps pushing the reference into it (a latch).  Then the closed loop itself:
    the servo's output limited to the design clamp, or to +-14 V as an op-amp integrator on +-15 V without a
    clamp would be; solved without .nodeset, and from a .nodeset with the sinks' bases at +14 V.  Each: the
    sinks' base-collector voltage v(vsink) - v(sx) (saturated above about +0.5 V), their collector current,
    e, the outputs.
Every deck ties the inputs through 1 ohm (FE.r_in), so that no operating point depends on rounding (the
note's Appendix), and records whether its operating point fell back to ngspice's transient op.
Writes ../sim/results/servo_check.json and servo_check_sweep_<case>.npz.  Usage: python servo_check.py
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import replace

import numpy as np

import frontend as F
import models
import spice

CASES = ("H100", "L200")
DV_REF = 0.020          # reference error for the sensitivity, V
DT = 25.0               # temperature step, K
VCM = (-8.0, 3.0)       # input common modes, V (inside both inputs' ranges: H -12.8..+3.7, L -9.0..+3.6 V)
RAIL = 14.0             # an op-amp integrator's output limit on +-15 V
OUT = spice.RESULTS / "servo_check.json"


def base(case: str) -> F.FE:
    """The case with the servo (the front ends of the note have none: cm_servo = False by default)."""
    return replace(F.CASES[case], name=f"servo_{case}", r_in=1.0, cm_servo=True)


def src(vcm: float = 0.0) -> str:
    return f"VA ina 0 DC {vcm:g} AC 0.5\nVB inb 0 DC {vcm:g} AC -0.5\nRIA ina ga 1m rnl\nRIB inb gb 1m rnl\n"


def r_up(p: F.FE) -> float:
    return (p.vp - (0.6 + p.vbs)) / p.i_bs          # as frontend.side()


def solution(deck: str) -> str:
    """A .nodeset line with the top-level node voltages of a converged deck's operating point ('print all'
    in its log), as printed (no rounding of our own)."""
    log = (spice.RUNS / deck / "run.log").read_text(encoding="utf-8")
    return ".nodeset " + " ".join(f"v({n})={v}" for n, v in re.findall(r"stdout ([A-Za-z0-9_]+) = ([-+0-9.eE]+)", log)) + "\n"


def op(p: F.FE, tag: str, vcm: float = 0.0, temp: float | None = None, edit=None, nodeset: str = "",
       retry: str = "") -> dict:
    """One DC operating point: the outputs against the sources, the currents, the servo's nodes.  If it
    falls back to the transient op, it is solved again with abstol = 1e-12 A, then from the retry
    .nodeset if one is given (a converged neighbour's solution), then from that with abstol = 1e-12 A;
    'started' records which converged (with the servo's integrator, a DC gain of 1e6, some decks converge
    only with abstol = 1e-12 A, and a .nodeset does not help them)."""
    probes = ["v(oa)", "v(ob)", "v(sa)", "v(sb)", "v(ba)", "v(bb)", "v(vsink)", "v(vsink0)", "v(ea)",
              "@qta[ic]", "@qtb[ic]", "@qta[ib]"] + (["v(nerr)", "v(nint)"] if p.cm_servo else [])
    ctl = ".control\n" + spice.WR + "op\nprint all\n" + "".join(f"print {q}\n" for q in probes) + ".endc\n"
    text = F.deck(p, f"servo check {tag}", src(vcm), ctl)
    if edit:
        text = edit(text)
    extra = (f".temp {temp:g}\n" if temp is not None else "")
    deck = f"servo_check/{p.name}/{tag}"
    tries = [("as given", nodeset, False), ("abstol 1e-12 A", nodeset, True)]
    if retry:
        tries += [("a converged neighbour's solution", retry, False),
                  ("a converged neighbour's solution, abstol 1e-12 A", retry, True)]
    for started, ns, loose in tries:
        t = text.replace(".control", extra + ns + ".control", 1)
        if loose:
            assert t.count("abstol=1e-15") == 1
            t = t.replace("abstol=1e-15", "abstol=1e-12")
        f = spice.run(deck, t)
        if not spice.op_fallback(f):
            break
    v = {q: spice.printed(f, q) for q in probes}
    r = dict(fallback=spice.op_fallback(f), started=started, deck=deck, vcm=vcm,
             temp=temp if temp is not None else 27.0)
    r["out_minus_src"] = [v["v(oa)"] - v["v(sa)"], v["v(ob)"] - v["v(sb)"]]
    r["cm_offset"] = sum(r["out_minus_src"]) / 2                  # = e, the servo's error
    r["i_rf"] = [x / p.rf for x in r["out_minus_src"]]
    r["i_sink"] = [v["@qta[ic]"], v["@qtb[ic]"]]
    r["i_up"] = [(p.vp - v["v(ba)"]) / r_up(p), (p.vp - v["v(bb)"]) / r_up(p)]
    r["v_src"] = [v["v(sa)"], v["v(sb)"]]
    r["v_out"] = [v["v(oa)"], v["v(ob)"]]
    r["v_ref"], r["v_base"], r["v_emitter"] = v["v(vsink0)"], v["v(vsink)"], v["v(ea)"]
    r["v_bc"] = v["v(vsink)"] - v["v(sa)"]                       # the sink's base-collector voltage
    r["i_base"] = v["@qta[ib]"]
    if p.cm_servo:
        r["e"], r["v_int"] = v["v(nerr)"], v["v(nint)"]
    return r


def fixed(p: F.FE, v_ref: float) -> F.FE:
    """p without the servo, its sinks' base reference (vsink0) fixed at v_ref."""
    return replace(p, cm_servo=False, v_ref_sink=v_ref)


def clamp_edit(lo: float, hi: float):
    """Replace the servo's output limits in the deck text."""
    def edit(text: str) -> str:
        new, n = re.subn(r"^BSNK vsink0 0 V=max\(min\((\S+-V\(nint\)), \S+\), \S+\)$",
                         lambda m: f"BSNK vsink0 0 V=max(min({m.group(1)}, {hi:g}), {lo:g})", text, flags=re.M)
        assert n == 1, "BSNK line not found"
        return new
    return edit


def role(case: str) -> dict:
    p = base(case)
    out = {"servo": op(p, "servo")}
    v_ref = out["servo"]["v_ref"]
    q = fixed(p, v_ref)
    out["fixed"] = op(q, "fixed")
    out["design"] = op(fixed(p, p.vm + p.v_sink + p.v_be_sink), "design")
    adj = F.sink_reference(replace(F.CASES[case], name=f"adjusted_{case}"))
    out["adjusted_reference"] = dict(v_ref=adj, minus_servo=adj - v_ref)
    out["ref_plus_20mV"] = op(fixed(p, v_ref + DV_REF), "ref_plus_20mV")
    out["ref_minus_20mV"] = op(fixed(p, v_ref - DV_REF), "ref_minus_20mV")
    out["servo_52C"] = op(p, "servo_52C", temp=27.0 + DT)
    out["fixed_52C"] = op(q, "fixed_52C", temp=27.0 + DT)
    for vcm in VCM:
        out[f"fixed_cm_{vcm:+g}V"] = op(q, f"fixed_cm_{vcm:+g}V", vcm=vcm)
        out[f"servo_cm_{vcm:+g}V"] = op(p, f"servo_cm_{vcm:+g}V", vcm=vcm,
                                        retry=solution(out[f"fixed_cm_{vcm:+g}V"]["deck"]))
    # the signal path: AC response and noise, with the servo and with the reference fixed at its value
    sig = {}
    for tag, x in (("servo", p), ("fixed", q)):
        x = replace(x, name=f"{x.name}_{tag}")
        ac, nz = F.check_ac(x), F.check_noise(x)
        sig[tag] = dict(f3db=ac["f3db"], gain_1k=ac["gain_1k"], en={k: v for k, v in nz["en"].items()})
    sig["max_rel_diff_en"] = max(abs(sig["fixed"]["en"][k] / sig["servo"]["en"][k] - 1) for k in sig["servo"]["en"])
    sig["rel_diff_f3db"] = sig["fixed"]["f3db"] / sig["servo"]["f3db"] - 1
    out["signal_path"] = sig
    # sensitivities of the outputs' common-mode offset without the servo
    out["sens"] = dict(
        per_mV_ref=(out["ref_plus_20mV"]["cm_offset"] - out["ref_minus_20mV"]["cm_offset"]) / (2 * DV_REF * 1e3),
        per_K_fixed=(out["fixed_52C"]["cm_offset"] - out["fixed"]["cm_offset"]) / DT,
        per_K_servo=(out["servo_52C"]["cm_offset"] - out["servo"]["cm_offset"]) / DT,
        per_V_cm_fixed=(out[f"fixed_cm_{VCM[1]:+g}V"]["cm_offset"] - out[f"fixed_cm_{VCM[0]:+g}V"]["cm_offset"])
        / (VCM[1] - VCM[0]),
        per_V_cm_servo=(out[f"servo_cm_{VCM[1]:+g}V"]["cm_offset"] - out[f"servo_cm_{VCM[0]:+g}V"]["cm_offset"])
        / (VCM[1] - VCM[0]),
        i_up_per_V_cm=(out[f"servo_cm_{VCM[1]:+g}V"]["i_up"][0] - out[f"servo_cm_{VCM[0]:+g}V"]["i_up"][0])
        / (VCM[1] - VCM[0]))
    return out


def sweep(case: str) -> dict:
    """The servo loop opened: e against the sinks' base reference, -RAIL ... +RAIL."""
    p = fixed(base(case), 0.0)
    ctl = (".control\n" + spice.WR + f"dc VSNK {-RAIL:g} {RAIL:g} 0.02\n"
           "wrdata sweep.txt v(oa) v(ob) v(sa) v(sb) v(vsink) v(ea)\n.endc\n")
    f = spice.run(f"servo_check/{p.name}/sweep", F.deck(p, f"servo sweep {case}", src(), ctl))
    d = spice.read_table(f / "sweep.txt")
    vref = np.asarray(d[list(d)[0]]).real            # the sweep's scale, written first (wr_singlescale)
    e = ((d["v(oa)"] - d["v(sa)"]) + (d["v(ob)"] - d["v(sb)"])) / 2
    v_bc = d["v(vsink)"] - d["v(sa)"]
    i_e = (d["v(ea)"] - p.vm) / (p.v_sink / (p.n * p.id + p.i_bs))
    np.savez(spice.RESULTS / f"servo_check_sweep_{case}.npz", v_ref=vref, e=e, v_bc=v_bc, i_e=i_e,
             v_src=d["v(sa)"], v_out=d["v(oa)"])
    zeros = []
    for k in range(len(vref) - 1):
        if e[k] == 0 or e[k] * e[k + 1] < 0:
            x = vref[k] - e[k] * (vref[k + 1] - vref[k]) / (e[k + 1] - e[k])
            zeros.append(dict(v_ref=float(x), slope=float((e[k + 1] - e[k]) / (vref[k + 1] - vref[k])),
                              v_bc=float(np.interp(x, vref, v_bc))))
    q = base(case)
    lo, hi = q.vm + 1, q.vm + q.v_sink + 3
    at = lambda x, y=e: float(np.interp(x, vref, y))
    i_nom = q.n * q.id + q.i_bs
    above = vref > zeros[0]["v_ref"] if zeros else vref > 0
    return dict(fallback=spice.op_fallback(f), zeros=zeros, design_clamp=[lo, hi],
                e_at_design_lo=at(lo), e_at_design_hi=at(hi), e_at_rail_lo=at(-RAIL), e_at_rail_hi=at(RAIL),
                e_min_above_zero=float(e[above].min()), e_max_below_zero=float(e[~above].max()),
                v_bc_at_design_hi=at(hi, v_bc), v_bc_at_rail_hi=at(RAIL, v_bc),
                saturation_onset_v_ref=float(np.interp(0.5, v_bc, vref)) if v_bc.max() > 0.5 else None,
                i_sink_nominal=i_nom, i_emitter_at_design_hi=at(hi, i_e), i_emitter_at_rail_hi=at(RAIL, i_e),
                p_rt_at_design_hi=at(hi, i_e) ** 2 * q.v_sink / i_nom, p_rt_at_rail_hi=at(RAIL, i_e) ** 2 * q.v_sink / i_nom,
                p_rt_nominal=i_nom * q.v_sink,
                v_out_at_rail_lo=at(-RAIL, d["v(oa)"]), v_out_at_rail_hi=at(RAIL, d["v(oa)"]),
                v_src_at_rail_lo=at(-RAIL, d["v(sa)"]), v_src_at_rail_hi=at(RAIL, d["v(sa)"]))


def closed(case: str) -> dict:
    """The closed loop with the design clamp and with +-RAIL, from no .nodeset and from the bases at +RAIL."""
    p = base(case)
    v0 = p.vm + p.v_sink + p.v_be_sink
    high = f".nodeset v(vsink0)={RAIL:g} v(vsink)={RAIL:g} v(nint)={v0 - RAIL:.6g}\n"
    lo, hi = p.vm + 1, p.vm + p.v_sink + 3
    out = {}
    for tag, edit, ns in (("design_clamp", None, ""), ("design_clamp_high_start", None, high),
                          ("rail", clamp_edit(-RAIL, RAIL), ""), ("rail_high_start", clamp_edit(-RAIL, RAIL), high)):
        out[tag] = op(p, f"closed_{tag}", edit=edit, nodeset=ns)
    out["design_clamp_limits"] = [lo, hi]
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    res = dict(description=__doc__.split("\n\n")[0], role={}, latch={})
    for case in CASES:
        r = res["role"][case] = role(case)
        s = r["sens"]
        print(f"{case}: servo: outputs - sources {r['servo']['out_minus_src'][0] * 1e3:+.3f} mV, sinks "
              f"{r['servo']['i_sink'][0] * 1e3:.3f} mA, reference {r['servo']['v_ref']:.4f} V | fixed at it: "
              f"{r['fixed']['cm_offset'] * 1e3:+.3f} mV | design reference: {r['design']['cm_offset'] * 1e3:+.1f} mV "
              f"(reference {r['design']['v_ref']:.3f} V) | per mV of reference {s['per_mV_ref'] * 1e3:+.3f} mV | "
              f"per K: fixed {s['per_K_fixed'] * 1e3:+.3f}, servo {s['per_K_servo'] * 1e3:+.4f} mV | per V of input CM: "
              f"fixed {s['per_V_cm_fixed'] * 1e3:+.2f}, servo {s['per_V_cm_servo'] * 1e3:+.4f} mV (R_UP current "
              f"{s['i_up_per_V_cm'] * 1e6:+.1f} uA/V) | signal path: f3dB {r['signal_path']['rel_diff_f3db']:+.1e}, "
              f"noise {r['signal_path']['max_rel_diff_en']:.1e} | fallbacks "
              f"{[k for k, x in r.items() if isinstance(x, dict) and x.get('fallback')]}", flush=True)
        w = res["latch"][case] = dict(sweep=sweep(case), closed=closed(case))
        sw, cl = w["sweep"], w["closed"]
        print(f"{case}: sweep zeros {[(round(z['v_ref'], 3), round(z['slope'], 3)) for z in sw['zeros']]}; e at the design "
              f"clamp {sw['e_at_design_lo']:+.3f} / {sw['e_at_design_hi']:+.3f} V, at the rails {sw['e_at_rail_lo']:+.3f} / "
              f"{sw['e_at_rail_hi']:+.3f} V; saturation from {sw['saturation_onset_v_ref']} V; fallback {sw['fallback']}", flush=True)
        for tag, x in cl.items():
            if isinstance(x, dict):
                print(f"   closed {tag:24s} fallback {x['fallback']}, base {x['v_base']:+.3f} V, V_BC {x['v_bc']:+.3f} V, "
                      f"sink {x['i_sink'][0] * 1e3:+.3f} mA, e {x['cm_offset']:+.4f} V, outputs {x['v_out'][0]:+.3f} V, "
                      f"sources {x['v_src'][0]:+.3f} V", flush=True)
    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    print(f"written {OUT.name}")


if __name__ == "__main__":
    main()
