"""Search of the front ends' compensation (C_I, C_X, C_node) for stability of the complete loop,
judged at the op amp's output pin (frontend.check_loop_out), and the resulting bandwidth.

Background: with C_node = 0 the common-mode local loop of the THS4021 (decompensated, stable at
noise gains of 10 and above) is unstable: in common mode the op amp sees C_I + C_X as its
feedback capacitance and only the summing node's parasitic capacitance to ground, i.e. a noise
gain near 2 at a few hundred MHz.  A capacitor C_node from each summing node to ground raises
the noise gain, but in differential mode the feedback capacitance is C_I - C_X, so the same
C_node lowers the differential local-loop bandwidth to about GBW (C_I - C_X) / (C_I + C_X +
C_node), which then lags the outer loop at its crossover.  This script scans the three values,
keeps the stable sets and reports the margins of both modes and the -3 dB bandwidth of the front
end.  Results: ../sim/results/comp_search_<case>.json.

Usage: python comp_search.py <case> [quick]
"""
from __future__ import annotations

import itertools
import json
import sys
from dataclasses import replace

import frontend as F
import spice


GRIDS = {
    # (C_I + C_X = S, C_I - C_X = D, C_node), in F
    "H100": dict(S=[6e-12, 8e-12, 10.6e-12, 14e-12], D=[1.77e-12, 2.5e-12, 3.5e-12, 5e-12],
                 CN=[68e-12, 100e-12, 150e-12, 220e-12]),
    "H10": dict(S=[10.6e-12, 14e-12], D=[5e-12, 7.77e-12, 10e-12], CN=[100e-12, 150e-12, 220e-12]),
    "L200": dict(S=[21.2e-12, 30e-12, 40e-12], D=[5.6e-12, 8e-12, 12e-12], CN=[220e-12, 330e-12, 470e-12]),
}
# Points evaluated after the grids: the adopted values (Table 6) and their neighbours with C_node
# raised to the next E12 values (330 pF for H, 680 pF for L; Section 4.3.1), (S, D, C_node) in F.
EXTRA = {
    "H100": [(14e-12, 4e-12, 220e-12), (14e-12, 4e-12, 330e-12), (14e-12, 3.5e-12, 330e-12),
             (18e-12, 4e-12, 330e-12)],
    "H10": [(14e-12, 12e-12, 220e-12), (14e-12, 11e-12, 330e-12)],
    "L200": [(30e-12, 12e-12, 680e-12), (30e-12, 14e-12, 680e-12), (30e-12, 14e-12, 470e-12),
             (36e-12, 14e-12, 680e-12)],
}


def evaluate(p: F.FE) -> dict:
    out = {}
    for mode in ("dm", "cm"):
        r = F.check_loop_out(p, mode)
        out[mode] = dict(crossings=r["crossings"], gain_margins=r["gain_margins"], pm=r["pm"],
                         gm_db=r["gm_db"])
    stable = all(len(out[m]["crossings"]) > 0 and out[m]["pm"] > 0 for m in ("dm", "cm"))
    if stable:
        ac = F.check_ac(p)
        out["f3db"] = ac["f3db"]
        out["peak_db"] = ac["peak_db"]
        out["g10M_db"] = ac["g10M_db"]
    out["stable"] = stable
    return out


def main(args):
    sys.stdout.reconfigure(encoding="utf-8")
    case = args[0]
    g = GRIDS[case]
    path = spice.RESULTS / f"comp_search_{case}.json"
    res = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    for s, d, cn in list(itertools.product(g["S"], g["D"], g["CN"])) + EXTRA.get(case, []):
        if d >= s:
            continue
        ci, cx = (s + d) / 2, (s - d) / 2
        key = f"S{s * 1e12:g}_D{d * 1e12:g}_CN{cn * 1e12:g}"
        if key in res:
            continue
        p = replace(F.CASES[case], name=f"{case}_comp_{key}", ci=ci, cx=cx, cnode=cn)
        try:
            r = evaluate(p)
        except RuntimeError as e:
            r = dict(failed=str(e).splitlines()[1][:160])
        r.update(ci=ci, cx=cx, cnode=cn)
        res[key] = r
        if "failed" in r:
            print(key, "failed", flush=True)
        else:
            print(f"{key}: DM PM {r['dm']['pm']:.1f} GM {r['dm']['gm_db']:.1f} | CM PM {r['cm']['pm']:.1f} "
                  f"GM {r['cm']['gm_db']:.1f} | f3dB {r.get('f3db', float('nan')) / 1e6:.1f} MHz "
                  f"peak {r.get('peak_db', float('nan')):.2f} dB", flush=True)
        path.write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main(sys.argv[1:])
