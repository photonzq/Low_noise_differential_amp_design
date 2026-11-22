"""The wrong operating points of Section 5.1 of the note, reproduced.

1. The R_F-route variant at a gain of 30 (gain_options.py: R_F 146.4 ohm, R_G 10.1 ohm, C_I, C_X
   and C_node x 3.41): its noise deck, run without .nodeset, converges to a state that its AC deck
   does not.  Printed: the node voltages, the currents in R_UP and R_BS and the cascodes' gate
   currents, and Kirchhoff's current law at the bootstrap node b,
       residual = I(R_UP) - I(R_BS) - sum I_G(cascodes),
   which a converged DC solution keeps at zero; and the input-referred noise at 10 kHz of that run.
2. The JFE150 current sink at a gain of 100 (sink_options.py): the source node's voltage at the
   operating point, and the front end's -3 dB bandwidth from the AC run.

Writes ../sim/results/op_pitfall.json.  Usage: python op_pitfall.py
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace

import frontend as F
import models
import spice


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    out = {}
    base = F.CASES["H100"]
    rf = 29 * base.rg / 2
    sc = base.rf / rf
    p = replace(base, name="H_RF30_pitfall", rf=rf, ci=base.ci * sc, cx=base.cx * sc, cnode=base.cnode * sc)
    probes = ["v(sa)", "v(ba)", "v(da1)", "v(ca)", "v(oa)", "@rupa[i]", "@rbsa[i]"] + \
             [f"@j.xca{k}.j1[ig]" for k in range(1, p.n + 1)]
    for tag, src in (("ac deck", F.SRC_DM), ("noise deck", F.SRC_NOISE)):
        ctl = ".control\n" + spice.WR + "op\n" + "".join(f"print {q}\n" for q in probes) + ".endc\n"
        f = spice.run(f"pitfall/{p.name}_{tag.split()[0]}", F.deck(p, f"op {tag}", src, ctl))
        v = {q: spice.printed(f, q) for q in probes}
        resid = v["@rupa[i]"] - v["@rbsa[i]"] - sum(v[f"@j.xca{k}.j1[ig]"] for k in range(1, p.n + 1))
        out[f"R_F route, gain 30, {tag}"] = dict(values=v, kcl_residual_at_b=resid)
        print(tag, {k: f"{x:.4g}" for k, x in v.items()}, f"KCL residual at b {resid * 1e3:.3f} mA", flush=True)
    nz = F.check_noise(p)
    out["R_F route, gain 30, noise at 10 kHz without .nodeset (nV/rtHz)"] = nz["en"]["10000.0"] * 1e9
    print(f"noise at 10 kHz without .nodeset: {nz['en']['10000.0'] * 1e9:.1f} nV/rtHz", flush=True)

    q = replace(F.CASES["H100"], name="H100_sink_JFE150_6V_pitfall", sink="J:JFE150", v_sink=6.0, v_be_sink=-0.4)
    ctl = ".control\n" + spice.WR + "op\nprint v(sa) v(ea) v(vsink)\n.endc\n"
    f = spice.run(f"pitfall/{q.name}_op", F.deck(q, f"op {q.name}", F.SRC_DM, ctl))
    ac = F.check_ac(q)
    out["JFE150 sink, gain 100"] = dict(v_sa=spice.printed(f, "v(sa)"), f3db=ac["f3db"],
                                        f3db_adopted=F.check_ac(F.CASES["H100"])["f3db"])
    print(f"JFE150 sink at a gain of 100: source node {out['JFE150 sink, gain 100']['v_sa']:.3f} V, "
          f"f3dB {ac['f3db'] / 1e6:.0f} MHz (adopted {out['JFE150 sink, gain 100']['f3db_adopted'] / 1e6:.1f} MHz)",
          flush=True)
    (spice.RESULTS / "op_pitfall.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
