"""Input noise against source resistance for the H and L inputs (full chain at a gain of 1000,
input A driven through a resistive source R_S, input B grounded), and the noise figure
NF = 10 log10( v_n^2 / 4kTR_S ) at 10 Hz, 1 kHz, 100 kHz, 1 MHz and 10 MHz.  The input networks
of chain.INPUT_NET are included, so the source sees the bias resistor, C_P, the damping network
and the bootstrapped JFETs.  Writes ../sim/results/noise_vs_source.json.
"""
from __future__ import annotations

import json
import sys

import numpy as np

import chain
import models
import spice

RS = [1, 3, 10, 30, 100, 300, 1e3, 3e3, 1e4, 3e4, 1e5, 3e5, 1e6, 1e7]
FREQ = [10, 1e3, 1e5, 1e6, 1e7]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    out = {}
    for mode in ("H_LN", "L"):
        s = chain.allocate(1000, mode)
        rows = []
        for rs in RS:
            r = chain.run_noise(s, rs)
            fr, inn = r["f"], r["inn"]
            row = dict(rs=rs, vn={str(f0): spice.at(fr, inn, f0) for f0 in FREQ})
            row["nf_db"] = {k: float(10 * np.log10(v ** 2 / (4 * spice.KT * rs))) for k, v in row["vn"].items()}
            rows.append(row)
            print(f"{mode} R_S {rs:>9g}: " + "  ".join(f"{k}: {v * 1e9:7.2f} nV ({row['nf_db'][k]:5.2f} dB)"
                                                       for k, v in row["vn"].items()))
        out[mode] = rows
    (spice.RESULTS / "noise_vs_source.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
