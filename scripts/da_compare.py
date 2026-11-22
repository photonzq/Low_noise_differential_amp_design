"""Choice of the difference amplifier S2 (unity gain, four equal resistors): distortion at
10 MHz (1 Vpp at the output) and 1 MHz (10 Vpp), the chain's response, and the input-referred
noise at the lowest front-end gain where S2 matters most (H10, total gain 10) and at H100.

Candidates (all on +/-15 V): THS4031 (voltage feedback), LM7171 (A grade; its macromodel's noise is
far below the data sheet, so the noise run uses the data-sheet value through an added generator,
models.py), THS3091 (current feedback; 1 k resistors instead of 499 ohm, as current-feedback
amplifiers need a minimum R_F).  The noise and distortion of every part are those of its model in
../sim/models/_lib/opamps.lib (models.py), not data-sheet figures.
Every transient is run anew: an earlier version reused a run folder's tran.txt without checking
that the deck and the model libraries it includes were unchanged, and so kept distortion results
from before the model recalibration of 22 November 2026.  Writes ../sim/results/da_compare.json.

Measures:
    chain response  H(f) = v(out) / (v_a - v_b),  f_3dB where |H| = |H(1 kHz)| / sqrt(2),
                    peak 20 log10(max|H| / |H(1 kHz)|), large_signal.thd_run for the THD
    input noise     e_in(f) = onoise(f) / |H(f)| (ngspice's inoise), input A driven, B grounded,
                    chain.run_noise
`hr` mode, the high-reserve mode H_HR (front end H10 at a gain of 10, the rest of the gain after it)
at total gains of 100 and 1000, with each S2 in turn (THS4031, and the default LM7171 for
comparison); the default S2 (chain.DA_OPAMP) is restored afterwards.  The stages after the front end
add, referred to the input,
    e_post(f) = sqrt(e_chain(f)^2 - e_FE(f)^2)
with e_FE the H10 front end alone (curves_noise.npz, key H10_total, collect_curves.py noise).
Stored under the new key noise_H_HR: {S2: {H_HR_<gain>: {tag, en, e_post}}}, densities in V/rtHz at
1 Hz ... 10 MHz (keys as in chain_noise.json); the LM7171 rows repeat chain_noise.json's H_HR_100
and H_HR_1000 (same decks, run in folders of their own).
Usage: python da_compare.py [opamp ...]        python da_compare.py hr [opamp ...]
"""
from __future__ import annotations

import json
import math
import re
import sys

import numpy as np

import chain
import large_signal as L
import models
import spice

CANDIDATES = {"THS4031": 499.0, "LM7171": 499.0, "THS3091": 1000.0}
DEFAULT_DA = chain.DA_OPAMP          # restored after each candidate
HR_DA = ("THS4031", "LM7171")
HR_GAINS = (100, 1000)
HR_REPORT = (("10", "10 Hz"), ("1000.0", "1 kHz"), ("10000.0", "10 kHz"), ("10000000.0", "10 MHz"))


def thd_cached(s: chain.Setting, tag: str, f0: float, vpp: float) -> dict:
    """large_signal.thd_run in ../sim/runs/large/<tag> (the name is kept from the cached version)."""
    return L.thd_run(s, tag, f0, vpp)


def patch_resistors(r: float):
    """S2's four resistors (RD1-RD4) as r: chain.netlist() writes 499; replaced in its text."""
    orig = chain.netlist

    def netlist(s, load=1e6):
        txt = orig(s, load)
        return re.sub(r"^(RD[1-4] \S+ \S+) 499$", rf"\g<1> {r:g}", txt, flags=re.M)
    chain.netlist = netlist
    return orig


def fe_alone_h10() -> tuple[np.ndarray, np.ndarray]:
    """The H10 front end's own input noise (archived, collect_curves.py noise)."""
    d = np.load(spice.RESULTS / "curves_noise.npz")
    return d["H10_f"], d["H10_total"]


def noise_hr(das) -> None:
    """The high-reserve mode at total gains of 100 and 1000 with each S2 of das (module docstring)."""
    path = spice.RESULTS / "da_compare.json"
    res = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    block = res.setdefault("noise_H_HR", {})
    f_fe, e_fe = fe_alone_h10()
    for da in das:
        chain.DA_OPAMP = da
        orig = patch_resistors(CANDIDATES[da])
        try:
            r = block.setdefault(da, {})
            for g in HR_GAINS:
                s = chain.allocate(g, "H_HR")
                n = chain.run_noise(s, run_suffix=f"_S2_{da}")
                post = {}
                for k, v in n["en"].items():
                    efe = spice.at(f_fe, e_fe, float(k))
                    post[k] = math.sqrt(max(v * v - efe * efe, 0.0))
                r[f"H_HR_{g}"] = dict(tag=s.tag, en=n["en"], e_post=post)
                print(f"{da} in S2, H_HR gain {g} ({s.tag}): input noise "
                      + ", ".join(f"{lab} {n['en'][k] * 1e9:.3f}" for k, lab in HR_REPORT)
                      + f" nV/rtHz; white (100 kHz) {n['en']['100000.0'] * 1e9:.3f}; stages after the front end "
                      + ", ".join(f"{lab} {post[k] * 1e9:.3f}" for k, lab in HR_REPORT), flush=True)
        finally:
            chain.netlist = orig
            chain.DA_OPAMP = DEFAULT_DA
        path.write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    print(f"default S2 restored: chain.DA_OPAMP = {chain.DA_OPAMP}")


def main(args):
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare_opamps()          # the other libraries are in place (models.py)
    if args and args[0] == "hr":
        noise_hr(args[1:] or HR_DA)
        return
    path = spice.RESULTS / "da_compare.json"
    res = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    for da in args or list(CANDIDATES):
        chain.DA_OPAMP = da
        orig = patch_resistors(CANDIDATES[da])
        try:
            r = res.setdefault(da, {})
            s = chain.allocate(100, "H_LN")
            ac = chain.run_ac(s)
            r["ac_H100"] = dict(f3db=ac["f3db"], peak_db=ac["peak_db"], db_10M=ac["db_10M"])
            print(f"{da}: G 100 f3dB {ac['f3db'] / 1e6:.1f} MHz, peak {ac['peak_db']:.2f} dB, "
                  f"10 MHz {ac['db_10M']:+.2f} dB", flush=True)
            r["thd"] = []
            for f0, vpp in ((1e7, 1.0), (1e6, 10.0)):
                try:
                    x = thd_cached(s, f"H100_thd_da2_{da}_{f0:g}_{vpp:g}", f0, vpp)
                    r["thd"].append(x)
                    print(f"{da}: THD {f0 / 1e6:g} MHz {vpp:g} Vpp {x['thd'] * 100:.4f} % (H2 "
                          f"{20 * math.log10(x['h2']):.0f}, H3 {20 * math.log10(x['h3']):.0f} dBc)", flush=True)
                except RuntimeError as e:
                    r["thd"].append(dict(f0=f0, vout_pp=vpp, failed=str(e).splitlines()[1][:150]))
                    print(f"{da}: THD {f0 / 1e6:g} MHz {vpp:g} Vpp failed", flush=True)
            r["noise"] = {}
            for mode, g in (("H_HR", 10), ("H_LN", 100)):
                n = chain.run_noise(chain.allocate(g, mode))
                r["noise"][f"{mode}_{g}"] = n["en"]
                print(f"{da}: noise {mode} G {g}: 1 kHz {n['en']['1000.0'] * 1e9:.2f}, 1 MHz "
                      f"{n['en']['1000000.0'] * 1e9:.2f} nV/rtHz", flush=True)
        finally:
            chain.netlist = orig
            chain.DA_OPAMP = DEFAULT_DA
        path.write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main(sys.argv[1:])
