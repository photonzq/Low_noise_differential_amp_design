"""Current sinks that survive their dissipation, and the drift their heat causes (Section 4.2 of the
note, the L front end's sinks).

Each source node's DC current, 62 mA per side for L, flows from about +0.5 V to -15 V, so the sink
transistor and R_T dissipate about 0.96 W per side between them, whatever the design.  The adopted
L sink, an MMBT3904 with 2 V across R_T, puts 0.84 W into a SOT-23 rated 225 mW.  The PZT3904 is
the same die in SOT-223 (onsemi PZT3904T1/D: the same electrical characteristics as the MMBT3904L;
1.5 W and R_thJA = 83.3 K/W on FR-4 with 713 mm^2 of copper), so the MMBT3904 model holds for it;
more voltage across R_T moves heat from the transistor into the resistor.

For L with 2, 4, 6 and 8 V across R_T:
  - operating point: sink current, the transistor's and R_T's dissipation, the junction's rise for
    the SOT-23 (556 K/W) and the SOT-223 (83.3 K/W), and the lower end of the common-mode range;
  - drift: the input-referred DC offset per kelvin of temperature difference between the two sink
    transistors (side a's 1 K warmer, ngspice's instance parameter dtemp);
  - the complete loop's margins and the front end's noise;
  - the chain's supply rejection from both rails (large_signal.psrr_run, L at a gain of 1000).
H at gains of 100 and 10, with 2 and 6 V, for the same drift figure.

Writes ../sim/results/sink_power.json.  Usage: python sink_power.py
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import replace

import chain
import frontend as F
import gain_options as GO
import large_signal as LS
import models
import sink_options as SO
import spice

R_TH = {"SOT-23 (MMBT3904)": 556.0, "SOT-223 (PZT3904, 713 mm2)": 83.3}
L_VRT = (2.0, 4.0, 6.0, 8.0)
H_VRT = (2.0, 6.0)


def drift(p: F.FE) -> float:
    """Input-referred DC offset (V) per kelvin by which side a's sink transistor is warmer."""
    orig = F.netlist
    vals = []
    for dt in (0.0, 1.0):
        def patched(q, dt=dt):
            text = orig(q)
            if dt:
                text, n = re.subn(r"^(QTa \S+ \S+ \S+ \S+)$", rf"\g<1> dtemp={dt:g}", text, flags=re.M)
                assert n == 1
            return text
        F.netlist = patched
        try:
            ctl = ".control\n" + spice.WR + "op\nprint v(oa) v(ob)\n.endc\n"
            f = spice.run(f"fe/{p.name}/drift_{dt:g}", F.deck(p, f"drift {p.name}", F.SRC_DM, ctl))
            vals.append(spice.printed(f, "v(oa)") - spice.printed(f, "v(ob)"))
        finally:
            F.netlist = orig
    return (vals[1] - vals[0]) / p.gain


def psrr_l(p: F.FE, tag: str) -> dict:
    orig = F.CASES["L200"]
    F.CASES["L200"] = p
    try:
        return LS.psrr_run(chain.allocate(1000, "L"), f"L1000_{tag}")
    finally:
        F.CASES["L200"] = orig


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    res = {}
    for v in L_VRT:
        p = replace(F.CASES["L200"], name=f"L200_sinkpow_{v:g}V", v_sink=v)
        o = SO.op_point(p)
        r = dict(op=o, rise={k: o["p_transistor"] * rth for k, rth in R_TH.items()},
                 drift_uV_per_K=drift(p) * 1e6, loop=GO.margins(p))
        ac = F.check_ac(p)
        nz, gain, how = GO.noise_checked(p, ac)
        r["en"] = {k: x * 1e9 for k, x in nz["en"].items()}
        r["noise_op"] = how
        r["f3db"] = ac["f3db"]
        r["psrr_L1000"] = psrr_l(p, f"sinkpow_{v:g}V")
        res[f"L200 | {v:g} V"] = r
        lp, e, ps = r["loop"], r["en"], r["psrr_L1000"]
        print(f"L200 V_RT {v:g} V: I {o['i_sink'] * 1e3:.2f} mA, P_T {o['p_transistor'] * 1e3:.0f} mW "
              f"(rise SOT-23 {r['rise']['SOT-23 (MMBT3904)']:.0f} K, SOT-223 {r['rise']['SOT-223 (PZT3904, 713 mm2)']:.0f} K), "
              f"P_RT {o['p_rt'] * 1e3:.0f} mW, V_CM,min {o['vcm_min']:.2f} V, drift {r['drift_uV_per_K']:.1f} uV/K | "
              f"DM {lp['dm']['pm']}/{lp['dm']['gm_db']}/{lp['dm']['mod']} CM {lp['cm']['pm']}/{lp['cm']['gm_db']}/{lp['cm']['mod']} "
              f"f3dB {r['f3db'] / 1e6:.1f} MHz | noise 10 Hz {e['10']:.3f} white {e['10000.0']:.3f} 10 MHz {e['10000000.0']:.3f} "
              f"[{how}] | PSRR VP " + " ".join(f"{float(k):g}:{x:.0f}" for k, x in ps["VP"].items())
              + " | VM " + " ".join(f"{float(k):g}:{x:.0f}" for k, x in ps["VM"].items()), flush=True)
    for case in ("H100", "H10"):
        for v in H_VRT:
            p = replace(F.CASES[case], name=f"{case}_sinkpow_{v:g}V", v_sink=v)
            o = SO.op_point(p)
            d = drift(p) * 1e6
            res[f"{case} | {v:g} V"] = dict(op=o, drift_uV_per_K=d,
                                            rise={k: o["p_transistor"] * rth for k, rth in R_TH.items()})
            print(f"{case} V_RT {v:g} V: P_T {o['p_transistor'] * 1e3:.0f} mW, drift {d:.1f} uV/K", flush=True)
    (spice.RESULTS / "sink_power.json").write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")


def tab_capacitance():
    """The SOT-223's collector tab is the source node, so its heat-spreading copper is capacitance
    from the source node to ground (about 140 pF for the 713 mm^2 of the data sheet's rating over a
    ground plane 0.2 mm below).  L with 6 V across R_T and 0, 60, 140 and 300 pF on each source node:
    the complete loop's margins and the bandwidth.  Adds 'L200 | 6 V | C_tab ...' to sink_power.json."""
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    path = spice.RESULTS / "sink_power.json"
    res = json.loads(path.read_text(encoding="utf-8"))
    orig = F.netlist
    for c in (0.0, 60e-12, 140e-12, 300e-12):
        p = replace(F.CASES["L200"], name=f"L200_sinkpow_6V_tab{c * 1e12:g}p", v_sink=6.0)
        extra = f"CTABA sa 0 {c:g}\nCTABB sb 0 {c:g}\n" if c else ""
        F.netlist = lambda q, extra=extra: orig(q) + extra
        try:
            lp = GO.margins(p)
            f3 = F.check_ac(p)["f3db"]
        finally:
            F.netlist = orig
        res[f"L200 | 6 V | C_tab {c * 1e12:g} pF"] = dict(loop=lp, f3db=f3)
        print(f"L200 6 V, C_tab {c * 1e12:4.0f} pF: DM {lp['dm']['pm']}/{lp['dm']['gm_db']}/{lp['dm']['mod']} "
              f"CM {lp['cm']['pm']}/{lp['cm']['gm_db']}/{lp['cm']['mod']} f3dB {f3 / 1e6:.1f} MHz", flush=True)
    path.write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    if sys.argv[1:] == ["tab"]:
        tab_capacitance()
    else:
        main()
