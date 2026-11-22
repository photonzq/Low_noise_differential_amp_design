"""Input protection and the input network: the closed forms of Section 4.4 of the note and its
Table 6d.  None of the protection is in the simulated netlists; the inputs here are archived results
of other scripts and one operating point of each front end.

Constants: k = 1.380649e-23 J/K, T = 300.15 K (ngspice's 27 C, spice.KT = kT), q = 1.602176634e-19 C.

The bare front ends' input (Section 4.4, Figure 10), read from the archived simulations of
collect_curves.py (curves_zin.npz: input A driven by 1 A AC, input B grounded; curves_sources.npz):
    Y_in = 1 / Z_in,   C_eff = Im(Y_in) / w,   R_par = 1 / Re(Y_in)  (negative where Re Y_in < 0)
    the plateau of C_eff (its minimum, 1 kHz - 1 MHz) and the frequencies below and above it at
    which C_eff reaches twice the plateau; the smallest |R_par| among the negative values
    the JFETs' own capacitance: C_JFETs = N C_iss (C_iss of the data sheet at V_GS = 0 and 5 V, the
    calibration target of models.py: JFE2140 13 pF, JFE150 24 pF)
    peaking of a source's response: 20 log10(max|H| / |H(10 Hz)|)
Input capacitance with the input network (chain.INPUT_NET), below the corner 1 / (2 pi R_Z C_Z) of
the damping network:
    C_in ~ C_P + C_Z (+ C_bare, the bootstrapped front end's own Im(Y_in) / w, 1 kHz - 1 MHz median
           of curves_zin.npz)            H: 10 + 10 pF = 20 pF;  L: 30 + 220 pF = 250 pF

A series resistor R_s in each input (Table 6d):
    e_Rs  = sqrt(2 * 4kT R_s)                 both inputs, in series with the source
    e_tot = sqrt(e_FE^2 + e_Rs^2)             e_FE: the simulated white floors, H 1.08 and L 0.42 nV/rtHz
    f_p   = 1 / (2 pi R_s C_in)               C_in = C_P + C_Z: 20 pF (H), 250 pF (L)
    NF    = 10 log10(1 + e_tot^2 / (4kT R_src)),   R_src = 1 kohm (H)
  e_FE is the chain's white noise at a total gain of 1000 (chain_noise.json, H_LN_1000 and L_1000
  at 100 kHz), rounded to the two decimals that the note quotes (1.08, 0.42); the table is also
  given with the unrounded values.  NF(R_s = 0) is compared with the simulated noise figure of the
  chain with a 1 kohm source (noise_vs_source.json, H_LN, 100 kHz).
  Relative costs: e_tot / e_FE - 1 and NF(R_s) - NF(0).  The R_s at which e_Rs equals the input
  JFETs' own contribution e_J (fe_gain_options.json, H at a gain of 100, 10 kHz):
    R_s,J = e_J^2 / (8kT)
Clamp diodes:
    i_L   = sqrt(2 q I_L)                     shot noise of a leakage current I_L
    i_RB  = sqrt(4kT / R_B)                   bias resistor: H 100 Mohm, L 10 Mohm (and 1 Gohm)
    i_tot = sqrt(i_RB^2 + i_L^2)
    R_x   = e_FE / i_tot                      source impedance at which H's current noise equals
                                              its voltage noise (e_FE = 1.08 nV/rtHz)
  A bootstrapped string of n diodes from each gate to its own source node: each diode at |V_GS| / n
  of forward bias, V_GS = V(s) - V(g) from the operating point.
Common-mode range that a clamp to fixed rails must clear (from the operating point, as
fe_closed_forms.py does for Section 4.2):
    V_CM,max = V(c) - V_GS - V_DS,J - 1 V     (the cascode keeps V_DS,sat plus room for the signal)
    V_CM,min = V_E + 0.5 V - V_GS             (the sink's V_CE stays above 0.5 V; emitter at V_E)

Writes ../sim/results/protection.json.  Usage: python protection.py
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import replace

import numpy as np

import chain
import frontend as F
import models
import spice

Q = 1.602176634e-19
KT = spice.KT
RS_NOTE = (0, 1, 10, 22, 47, 100, 1000)          # the rows of Table 6d
RS_ALL = (0, 1, 3, 10, 22, 47, 100, 220, 1000)   # as computed for the table (3 and 220 ohm not shown)
R_SRC_NF = 1000.0
LEAK = (1e-12, 10e-12, 100e-12, 1e-9)
V_CE_MIN = 0.5
V_DS_C_MIN = 1.0


def white_floors() -> dict:
    cn = json.loads((spice.RESULTS / "chain_noise.json").read_text(encoding="utf-8"))
    return {"H": cn["H_LN_1000"]["en"]["100000.0"], "L": cn["L_1000"]["en"]["100000.0"]}


def input_capacitance() -> dict:
    z = np.load(spice.RESULTS / "curves_zin.npz")
    out = {}
    for fe, case in (("H", "H100"), ("L", "L200")):
        f, zz = z[f"{case}_dm_f"], z[f"{case}_dm_z"]
        c_eff = np.imag(1 / zz) / (2 * np.pi * f)
        c_bare = float(np.median(c_eff[(f >= 1e3) & (f <= 1e6)]))
        net = chain.INPUT_NET[fe]
        out[fe] = dict(C_P=net["cp"], C_Z=net["cz"], R_Z=net["rz"], C_bare=c_bare,
                       C_in=net["cp"] + net["cz"], C_in_with_bare=net["cp"] + net["cz"] + c_bare,
                       f_corner_RZ_CZ=1 / (2 * np.pi * net["rz"] * net["cz"]))
    return out


def admittance_readout() -> dict:
    """Section 4.4's figures from the archived simulations of collect_curves.py (Figure 10)."""
    z = np.load(spice.RESULTS / "curves_zin.npz")
    s = np.load(spice.RESULTS / "curves_sources.npz")
    cal = json.loads((spice.RESULTS / "jfet_calibration.json").read_text(encoding="utf-8"))
    out = {}
    for case in ("H100", "L200"):
        p = F.CASES[case]
        f, zz = z[f"{case}_dm_f"], z[f"{case}_dm_z"]
        y = 1 / zz
        c_eff = np.imag(y) / (2 * np.pi * f)
        band = (f >= 1e3) & (f <= 1e6)
        k0 = int(np.argmin(np.where(band, c_eff, np.inf)))
        plateau = float(c_eff[k0])
        lo = [k for k in range(k0) if c_eff[k] >= 2 * plateau]
        hi = [k for k in range(k0, len(f)) if c_eff[k] >= 2 * plateau]
        g = np.real(y)
        neg = np.where(g < 0)[0]
        kn = int(neg[np.argmin(-1 / g[neg])])
        out[case] = dict(C_JFETs=p.n * cal[p.jfet]["ciss_target"], n=p.n, C_iss=cal[p.jfet]["ciss_target"],
                         C_eff_plateau=plateau, f_plateau=float(f[k0]),
                         C_eff_median_1k_1M=float(np.median(c_eff[band])),
                         C_eff_1k=spice.at(f, c_eff, 1e3), C_eff_1M=spice.at(f, c_eff, 1e6),
                         f_rise_low=float(f[lo[-1]]) if lo else None, f_rise_high=float(f[hi[0]]) if hi else None,
                         R_neg_min=float(-1 / g[kn]), f_R_neg_min=float(f[kn]))
    peaks = {}
    for k in sorted(set(k.rsplit("_", 1)[0] for k in s.keys())):
        f, h = s[k + "_f"], np.abs(s[k + "_h"])
        i = int(np.argmax(h))
        peaks[k] = dict(peak_db=float(20 * np.log10(h[i] / h[0])), f_peak=float(f[i]))
    out["source_peaking"] = peaks
    out["network_max_peak_db"] = max(v["peak_db"] for k, v in peaks.items() if "_network_" in k)
    return out


def series_table(e_fe: dict, c_in: dict) -> list[dict]:
    rows = []
    for rs in RS_ALL:
        e_rs = math.sqrt(2 * 4 * KT * rs)
        h, l = math.hypot(e_fe["H"], e_rs), math.hypot(e_fe["L"], e_rs)
        nf = 10 * math.log10(1 + h ** 2 / (4 * KT * R_SRC_NF))
        rows.append(dict(R_s=rs, in_note=rs in RS_NOTE, e_Rs=e_rs, H_total=h, L_total=l,
                         f_pole_H=1 / (2 * math.pi * rs * c_in["H"]) if rs else None,
                         f_pole_L=1 / (2 * math.pi * rs * c_in["L"]) if rs else None, NF_H_1k=nf,
                         H_increase=h / e_fe["H"] - 1, L_increase=l / e_fe["L"] - 1))
    nf0 = rows[0]["NF_H_1k"]
    for r in rows:
        r["NF_H_1k_increase"] = r["NF_H_1k"] - nf0
    return rows


def op_point(p: F.FE) -> dict:
    nodes = ("v(ga)", "v(sa)", "v(da1)", "v(ca)", "v(ea)")
    ctl = ".control\n" + spice.WR + "op\nprint " + " ".join(nodes) + "\n.endc\n"
    f = spice.run(f"fe/{p.name}/op", F.deck(p, f"op {p.name}", F.SRC_DM, ctl))
    return {k: spice.printed(f, k) for k in nodes}


def fmt_f(x):
    return "-" if x is None else (f"{x / 1e9:.2f} GHz" if x >= 1e9 else f"{x / 1e6:.1f} MHz")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    res = {}

    # input capacitance with the input network
    cin = input_capacitance()
    res["input_capacitance"] = cin
    for fe, c in cin.items():
        print(f"{fe}: C_P {c['C_P'] * 1e12:g} + C_Z {c['C_Z'] * 1e12:g} pF = {c['C_in'] * 1e12:g} pF "
              f"(+ the bare front end's {c['C_bare'] * 1e12:.2f} pF = {c['C_in_with_bare'] * 1e12:.2f} pF); "
              f"R_Z C_Z corner {c['f_corner_RZ_CZ'] / 1e6:.1f} MHz")
    c_tab = {fe: c["C_in"] for fe, c in cin.items()}

    # the bare front ends' input admittance and the source peaking (archived simulations)
    ro = admittance_readout()
    res["admittance_readout"] = ro
    for case in ("H100", "L200"):
        r = ro[case]
        print(f"{case}: JFETs' own {r['n']} x {r['C_iss'] * 1e12:g} pF = {r['C_JFETs'] * 1e12:g} pF; bootstrapped "
              f"C_eff {r['C_eff_plateau'] * 1e12:.3f} pF at its minimum ({r['f_plateau'] / 1e3:.1f} kHz), "
              f"{r['C_eff_1k'] * 1e12:.3f} pF at 1 kHz, {r['C_eff_1M'] * 1e12:.3f} pF at 1 MHz; twice the minimum "
              f"below {r['f_rise_low']:.0f} Hz and above {r['f_rise_high'] / 1e6:.2f} MHz; negative parallel "
              f"resistance at its smallest {-r['R_neg_min']:.0f} ohm at {r['f_R_neg_min'] / 1e6:.1f} MHz")
    for k in ("H100_bare_1Meg", "L200_bare_1k"):
        print(f"{k}: peak {ro['source_peaking'][k]['peak_db']:.1f} dB at "
              f"{ro['source_peaking'][k]['f_peak'] / 1e6:.2f} MHz")
    print(f"largest peak with the input networks (50 ohm, 1 kohm, 1 Mohm sources): {ro['network_max_peak_db']:.2f} dB")

    # Table 6d
    full = white_floors()
    quoted = {k: round(v * 1e9, 2) * 1e-9 for k, v in full.items()}
    res["white_floors"] = dict(full=full, quoted=quoted, source="chain_noise.json, H_LN_1000 and L_1000, 100 kHz")
    print(f"\nwhite floors (chain, gain 1000, 100 kHz): H {full['H'] * 1e9:.4f}, L {full['L'] * 1e9:.4f} nV/rtHz; "
          f"quoted {quoted['H'] * 1e9:.2f}, {quoted['L'] * 1e9:.2f}")
    for tag, floors in (("quoted floors", quoted), ("unrounded floors", full)):
        rows = series_table(floors, c_tab)
        res[f"table_6d ({tag})"] = rows
        print(f"\nTable 6d with the {tag}: R_s per input | added differential | H total | L total | pole H "
              f"({c_tab['H'] * 1e12:g} pF) | pole L ({c_tab['L'] * 1e12:g} pF) | NF, H, 1 kohm source")
        for r in rows:
            print(f"  {r['R_s']:>5g} ohm{' ' if r['in_note'] else '*'} | {r['e_Rs'] * 1e9:5.2f} | "
                  f"{r['H_total'] * 1e9:5.2f} (+{r['H_increase'] * 100:3.0f} %) | {r['L_total'] * 1e9:5.2f} "
                  f"(+{r['L_increase'] * 100:3.0f} %) | {fmt_f(r['f_pole_H']):>10s} | {fmt_f(r['f_pole_L']):>10s} | "
                  f"{r['NF_H_1k']:.2f} dB (+{r['NF_H_1k_increase']:.2f})")
    print("  (* not shown in the note's table)")

    # the noise figure against the simulated chain with a 1 kohm source
    nv = json.loads((spice.RESULTS / "noise_vs_source.json").read_text(encoding="utf-8"))
    sim = next(r for r in nv["H_LN"] if r["rs"] == R_SRC_NF)
    res["NF_H_1k_simulated"] = sim["nf_db"]
    print("\nNF with a 1 kohm source, simulated chain (noise_vs_source.json, H_LN): "
          + ", ".join(f"{k} Hz {v:.3f} dB" for k, v in sim["nf_db"].items()))

    # the series resistance at which e_Rs equals the input JFETs' contribution (H, gain 100)
    go = json.loads((spice.RESULTS / "fe_gain_options.json").read_text(encoding="utf-8"))
    e_j = go["H, gain 100 (adopted)"]["groups"]["input JFETs"]["10000"] * 1e-9
    rs_j = e_j ** 2 / (8 * KT)
    res["R_s_equal_to_JFETs_H"] = dict(e_J=e_j, R_s=rs_j)
    print(f"R_s per input whose noise equals H's input JFETs ({e_j * 1e9:.2f} nV/rtHz): {rs_j:.1f} ohm")

    # clamp leakage and bias resistors
    leak = {f"{i:g}": math.sqrt(2 * Q * i) for i in LEAK}
    bias = {f"{r:g}": math.sqrt(4 * KT / r) for r in (100e6, 10e6, 1e9)}
    tot = {f"{i:g}": math.sqrt(bias["1e+08"] ** 2 + v ** 2) for i, v in zip(LEAK, leak.values())}
    res["leakage_shot_noise"] = leak
    res["bias_resistor_noise"] = bias
    res["H_current_noise_with_leakage"] = tot
    print("\nleakage shot noise sqrt(2 q I_L): " + ", ".join(f"{k} A: {v * 1e15:.2f} fA" for k, v in leak.items()))
    print("bias resistors sqrt(4kT/R_B): " + ", ".join(f"{k} ohm: {v * 1e15:.2f} fA" for k, v in bias.items()))
    print("H (100 Mohm) with leakage: " + ", ".join(
        f"{k} A: {v * 1e15:.2f} fA (+{(v / bias['1e+08'] - 1) * 100:.1f} %)" for k, v in tot.items()))
    # the source impedance at which H's current noise equals its voltage noise: R_x = e_FE / i_n
    r_x = {"bias only": quoted["H"] / bias["1e+08"]}
    r_x.update({f"bias + {k} A leakage": quoted["H"] / v for k, v in tot.items()})
    res["H_R_x_current_equals_voltage_noise"] = r_x
    print("source impedance where H's current noise equals its 1.08 nV/rtHz: " + ", ".join(
        f"{k} {v / 1e3:.0f} kohm" for k, v in r_x.items()))

    # operating points: bootstrapped clamp strings and the common-mode range for rail clamps
    ops = {}
    for fe, case in (("H", "H100"), ("L", "L200")):
        p = replace(F.CASES[case], name=f"{case}_protection")
        op = op_point(p)
        v_gs = op["v(sa)"] - op["v(ga)"]
        v_ds = op["v(da1)"] - op["v(sa)"]
        ops[fe] = dict(op=op, V_GS=v_gs, V_DS_J=v_ds,
                       per_diode={n: v_gs / n for n in (1, 2, 3)},
                       V_CM_max=op["v(ca)"] - v_gs - v_ds - V_DS_C_MIN,
                       V_CM_min=op["v(ea)"] + V_CE_MIN - v_gs, sink_V_RT=p.v_sink)
        o = ops[fe]
        print(f"\n{fe} ({case}): V_GS {v_gs:.3f} V, V_DS,J {v_ds:.3f} V, summing node {op['v(ca)']:.4f} V, "
              f"sink emitter {op['v(ea)']:.3f} V ({p.v_sink:g} V across R_T)")
        print("  bootstrapped clamp, forward bias per diode: " + ", ".join(
            f"{n} diode{'s' if n > 1 else ''} {v:.3f} V" for n, v in o["per_diode"].items()))
        print(f"  common-mode range for rail clamps: {o['V_CM_min']:+.2f} ... {o['V_CM_max']:+.2f} V")
    res["operating_points"] = ops

    (spice.RESULTS / "protection.json").write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
