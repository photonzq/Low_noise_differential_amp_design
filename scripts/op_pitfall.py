"""The wrong operating points of Section 5.1 of the note, reproduced.  Every one is ngspice-46's
transient-op fallback: when gmin and source stepping both fail, ngspice takes the end of a 10 us
transient as the operating point and notes it only in the log ("Transient op started"); the end state
need not be a DC solution, and nothing is reported as an error.

1. The circuits of the note (no servo).  The R_F-route variant at a gain of 20 (gain_options.py: R_F
   96 ohm, R_G 10.1 ohm, C_I, C_X and C_node x 5.21): the operating points of its AC deck, which
   converges, and of the deck of its complete loop with the differential voltage injection at the op
   amps' outputs (frontend.loop_out_deck), which falls back, (a) as run, abstol = 1e-15 A with the gates
   tied to ground through 1 mOhm, (b) with 1-ohm ties, (c) with abstol = 1e-12 A.  Printed for each:
   node voltages, an input JFET's gate current, the sinks' base node vsink (fed from the reference
   through 1 kOhm with 10 uF, 10 ms), the currents in R_UP and R_BS and the cascodes' gate currents, and
   Kirchhoff's current law at the bootstrap node b,
       residual = I(R_UP) - I(R_BS) - sum I_G(cascodes),
   which a DC solution keeps at zero; and the complete loop's margins (gain_options.margins) in each
   setting.  And the two cases of the earlier version, which converge without the servo: the R_F-route
   variant at a gain of 30 (R_F 146.4 ohm, x 3.41), its noise deck's operating point and noise at 10 kHz,
   and the JFE150 sink at a gain of 100 (sink_options.py), its source node and -3 dB bandwidth.
2. With the servo of the note's Appendix B in the netlists (FE.cm_servo), as in the earlier version:
   the same quantities for the gain-30 variant's AC and noise decks (the noise deck falls back) and for
   the JFE150 sink (every deck falls back), and the gain-20 variant's margins (its loop decks converge).

Writes ../sim/results/op_pitfall.json.  Usage: python op_pitfall.py
"""
from __future__ import annotations

import contextlib
import json
import sys
from dataclasses import replace

import frontend as F
import gain_options as G
import models
import spice

OP_CTL = ".control\n" + spice.WR + "op\n{prints}.endc\n"
ABSTOL_12 = ("abstol=1e-15", "abstol=1e-12")


def probes(p: F.FE) -> list[str]:
    casc = [f"@j.xca{k}.j1[ig]" if p.cascode.startswith("J:") else f"@qca{k}[ib]" for k in range(1, p.n + 1)]
    return ["v(oa)", "v(sa)", "v(ga)", "v(ba)", "v(da1)", "v(ca)", "v(vsink)", "@j.xja1.j1[ig]",
            "@rupa[i]", "@rbsa[i]"] + casc


def op_values(name: str, text: str, p: F.FE) -> dict:
    """Run an op deck; its printed values, the KCL residual at the bootstrap node, and the fallback flag."""
    f = spice.run(name, text)
    v = {q: spice.printed(f, q) for q in probes(p)}
    resid = v["@rupa[i]"] - v["@rbsa[i]"] - sum(v[q] for q in probes(p)[10:])
    return dict(values=v, kcl_residual_at_b=resid, fallback=spice.op_fallback(f))


def ctl(p: F.FE) -> str:
    return OP_CTL.format(prints="".join(f"print {q}\n" for q in probes(p)))


def show(tag: str, r: dict) -> None:
    v = r["values"]
    print(f"  {tag}: fallback {r['fallback']}; outputs {v['v(oa)']:.3f} V, sources {v['v(sa)']:.3f} V, "
          f"vsink {v['v(vsink)']:.3f} V, b {v['v(ba)']:.3f} V, gate current {v['@j.xja1.j1[ig]'] * 1e3:.3g} mA; "
          f"KCL residual at b {r['kcl_residual_at_b'] * 1e3:.3f} mA of R_UP's {v['@rupa[i]'] * 1e3:.3f} mA", flush=True)


def gain20(p20: F.FE) -> dict:
    out = {"ac deck": op_values(f"pitfall/{p20.name}_ac_op", F.deck(p20, "op ac deck", F.SRC_DM, ctl(p20)), p20)}
    show("ac deck", out["ac deck"])
    settings = {"abstol 1e-15 A, 1-mOhm ties (as run)": ("", None, None),
                "1-ohm ties": ("_ties1", None, 1.0),
                "abstol 1e-12 A": ("_abstol12", ABSTOL_12, None)}
    for label, (sfx, opt, r_in) in settings.items():
        q = replace(p20, name=p20.name + sfx, r_in=r_in or p20.r_in)
        n0 = len(spice.FALLBACKS)
        with (spice.options_replaced(*opt) if opt else contextlib.nullcontext()):
            op = op_values(f"pitfall/{q.name}_loopout_dm_v_op", F.loop_out_deck(q, "dm", "v", ctl(q)), q)
            m = G.margins(q)
        fb = sorted({f.relative_to(spice.RUNS).as_posix() for f in spice.FALLBACKS[n0:]})
        out[f"loop deck at the op-amp outputs (dm, v), {label}"] = dict(op=op, margins=m, fallbacks=fb)
        show(f"loop deck, {label}", op)
        print(f"    margins DM {m['dm']}, CM {m['cm']}", flush=True)
    return out


def gain30(p30: F.FE) -> dict:
    out = {}
    for tag, src in (("ac deck", F.SRC_DM), ("noise deck", F.SRC_NOISE)):
        out[tag] = op_values(f"pitfall/{p30.name}_{tag.split()[0]}", F.deck(p30, f"op {tag}", src, ctl(p30)), p30)
        show(tag, out[tag])
    nz = F.check_noise(p30)
    out["noise at 10 kHz (nV/rtHz)"] = nz["en"]["10000.0"] * 1e9
    print(f"  noise at 10 kHz: {out['noise at 10 kHz (nV/rtHz)']:.2f} nV/rtHz", flush=True)
    return out


def jfe150(q: F.FE) -> dict:
    c = ".control\n" + spice.WR + "op\nprint v(sa) v(ea) v(vsink)\n.endc\n"
    f = spice.run(f"pitfall/{q.name}_op", F.deck(q, f"op {q.name}", F.SRC_DM, c))
    ac = F.check_ac(q)
    out = dict(v_sa=spice.printed(f, "v(sa)"), fallback=spice.op_fallback(f), f3db=ac["f3db"])
    print(f"  JFE150 sink: source node {out['v_sa']:.3f} V (fallback {out['fallback']}), "
          f"f3dB {ac['f3db'] / 1e6:.1f} MHz", flush=True)
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    base = F.CASES["H100"]
    p20 = replace(G.cases()["R_F route, gain 20, all capacitors x5.21"][0], name="H_RF20_pitfall")
    rf = 29 * base.rg / 2
    sc = base.rf / rf
    p30 = replace(base, name="H_RF30_pitfall", rf=rf, ci=base.ci * sc, cx=base.cx * sc, cnode=base.cnode * sc)
    pj = replace(base, name="H100_sink_JFE150_6V_pitfall", sink="J:JFE150", v_sink=6.0, v_be_sink=-0.4)
    out = {"f3db_adopted": F.check_ac(base)["f3db"]}
    print("1. without the servo (the circuits of the note)", flush=True)
    print(" R_F route, gain 20", flush=True)
    a = {"R_F route, gain 20": gain20(p20)}
    print(" R_F route, gain 30", flush=True)
    a["R_F route, gain 30"] = gain30(p30)
    a["JFE150 sink, gain 100"] = jfe150(pj)
    out["without the servo"] = a
    print("2. with the servo of Appendix B", flush=True)
    s20 = replace(p20, name="H_RF20_pitfall_servo", cm_servo=True)
    n0 = len(spice.FALLBACKS)
    m = G.margins(s20)
    b = {"R_F route, gain 20, margins": dict(
        margins=m, fallbacks=sorted({f.relative_to(spice.RUNS).as_posix() for f in spice.FALLBACKS[n0:]}))}
    print(f" R_F route, gain 20: margins DM {m['dm']}, CM {m['cm']}", flush=True)
    print(" R_F route, gain 30", flush=True)
    b["R_F route, gain 30"] = gain30(replace(p30, name="H_RF30_pitfall_servo", cm_servo=True))
    b["JFE150 sink, gain 100"] = jfe150(replace(pj, name="H100_sink_JFE150_6V_pitfall_servo", cm_servo=True))
    out["with the servo"] = b
    (spice.RESULTS / "op_pitfall.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
