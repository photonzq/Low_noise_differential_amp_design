"""Robustness of the front ends' stability (Section 4.3 of the note): the complete loop's margins,
broken at the op amp's output pin (frontend.check_loop_out), for the final values and for
corners of the parts and of the layout, and for an isolation resistor between each op amp's
output and its feedback network.

Corners: C_node x0.7 and x1.3 (tolerance plus layout capacitance at the summing node); C_I x1.1
with C_X x0.9 and the reverse (1 % parts, trimmed or not, plus layout); 10 pF from each op amp's
output to ground (layout and the following stage's input).  Each case also gives the modulus
margin min|1 + T|, the closest approach of the return ratio to -1 (its inverse is the peak of the
sensitivity function; 0.5, i.e. a 6 dB peak, is a common minimum).

Writes ../sim/results/stability_corners.json.  Usage: python stability_corners.py
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


def margins(p: F.FE, extra: str = "", riso: float = 0.0) -> dict:
    orig = F.netlist

    def patched(q):
        text = orig(q)
        if riso:
            for x, o in (("a", "b"), ("b", "a")):
                text = re.sub(rf"^(CI{x}) o{x} ", rf"\g<1> q{x} ", text, flags=re.M)
                text = re.sub(rf"^(CX{o}) o{x} ", rf"\g<1> q{x} ", text, flags=re.M)
                text = re.sub(rf"^(RF{x}) o{x} ", rf"\g<1> q{x} ", text, flags=re.M)
                text += f"RISO{x} o{x} q{x} {riso:g}\n"
        return text + extra

    F.netlist = patched
    try:
        out = {}
        for mode in ("dm", "cm"):
            r = F.check_loop_out(p, mode)
            fr, t = r["T"]
            mm = np.abs(1 + t)
            out[mode] = dict(pm=r["pm"], gm_db=r["gm_db"], fc=r["crossings"][-1]["f"] if r["crossings"] else None,
                             modulus=float(mm.min()), f_modulus=float(fr[np.argmin(mm)]))
        return out
    finally:
        F.netlist = orig


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    res = {}
    for case in ("H100", "H10", "L200"):
        p = F.CASES[case]
        variants = {
            "nominal": (p, "", 0.0),
            "C_node x0.7": (replace(p, cnode=p.cnode * 0.7), "", 0.0),
            "C_node x1.3": (replace(p, cnode=p.cnode * 1.3), "", 0.0),
            "C_I x1.1, C_X x0.9": (replace(p, ci=p.ci * 1.1, cx=p.cx * 0.9), "", 0.0),
            "C_I x0.9, C_X x1.1": (replace(p, ci=p.ci * 0.9, cx=p.cx * 1.1), "", 0.0),
            "10 pF at each op-amp output": (p, "COLA oa 0 10p\nCOLB ob 0 10p\n", 0.0),
            "R_iso 10 ohm": (p, "", 10.0),
            "R_iso 33 ohm": (p, "", 33.0),
        }
        for name, (q, extra, riso) in variants.items():
            q = replace(q, name=f"{case}_corner_{re.sub(r'[^A-Za-z0-9]+', '_', name)}")
            try:
                r = margins(q, extra, riso)
            except RuntimeError as e:
                r = dict(failed=str(e).splitlines()[1][:150])
            res[f"{case} | {name}"] = r
            if "failed" in r:
                print(case, name, "failed", flush=True)
            else:
                print(f"{case:5s} {name:28s} DM PM {r['dm']['pm']:5.1f} GM {r['dm']['gm_db']:5.1f} mod {r['dm']['modulus']:.2f} | "
                      f"CM PM {r['cm']['pm']:5.1f} GM {r['cm']['gm_db']:5.1f} mod {r['cm']['modulus']:.2f}", flush=True)
    (spice.RESULTS / "stability_corners.json").write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
