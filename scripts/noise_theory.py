"""Closed-form noise of a JFET input stage, used for the JFET selection and the noise-versus-
capacitance trade-off of the note (no simulation).

Model of one input (one side of a differential stage) made of N identical JFETs in parallel, each
at drain current I_D, with white input noise density e_1(I_D), 1/f corner f_c(I_D), input
capacitance C_1 (gate to source plus gate to drain, at the operating point) and gate current I_G:

    e_n^2(f) = (e_1^2 / N) (1 + f_c / f)            (paralleling: voltage noise power / N)
    C_in      = N C_1                                 (capacitance x N)
    i_n^2     = 2 q N I_G                             (shot noise of the gate current)

Seen from a source impedance Z_s, the input noise is (e_n and the current that e_n drives through
C_in are fully correlated, since they are the same channel noise):

    v_n^2 = e_n^2 |1 + j w C_in Z_s|^2 + i_n^2 |Z_s|^2 + 4 k T Re(Z_s)

A differential stage has two such inputs, so its differential input noise is sqrt(2) e_n per side.

With a resistive source R_s at frequency f, e_n^2 (1 + (w C_in R_s)^2) is smallest when
w N C_1 R_s = 1, i.e. N_opt = 1 / (w C_1 R_s): the paralleled JFETs' reactance equals the source
resistance ("capacitive matching" in the frequency domain), and then e_n,min^2 = 2 e_1^2 w C_1 R_s.

The figure of merit of a JFET for a given input-capacitance budget C is e_1 sqrt(C_1): N = C / C_1
devices give e_n = e_1 sqrt(C_1 / C), so for every budget the part with the lowest e_1 sqrt(C_1)
(at its own best current) gives the lowest noise.  For a given total current budget I the figure is
e_1 sqrt(I_D) instead.

`python noise_theory.py` evaluates the numbers of Section 1 of the note (closed_forms below) and
writes ../sim/results/noise_theory.json.  T = 300.15 K (ngspice's 27 C, as every simulation; the
functions above use KT at 298.15 K, 25 C):
  channel noise of one JFET           e_th = sqrt(4kT (2/3) / g_m), g_m of the JFE150 at 5 mA, 5 V from
                                      jfet_calibration.json (the card's g_m; the card keeps TI's DC
                                      parameters); and the ngspice value with RS and RD (en_model_white)
  current dependence                  e ~ I_D^(-1/4): doubling I_D multiplies e by 2^(-1/4)
  gate-current shot noise             i_n = sqrt(2 q I_G) at I_G = 1 pA, 10 pA, 100 pA, 1 nA
  e_n / i_n crossover                 R_x = e_n / i_n (i_n R = e_n) for e_n = 0.8, 0.9, 1 nV/rtHz;
                                      R_s = 4kT / i_n^2 = 2 V_T / I_G (i_n R = sqrt(4kT R), the
                                      source's own thermal noise)
  paralleling, Eq. (2)                e_side = e_1 / sqrt(N), e_diff = sqrt(2) e_1 / sqrt(N),
                                      C_in = N C_1 (H: N = 2 JFE2140, L: N = 12 JFE150; the SR560:
                                      one 2N5564 per side), e_1 and C_1 from jfet_data.JFETS
  capacitive matching, Eq. (4)        R_s = 1 / (2 pi f N C_1) for N = 12 and N = 1 at 10 MHz (JFE150)
  current sharing                     Delta I / I = 2 Delta V_TO / (V_GS - V_TO) for Delta V_TO = 85 mV
                                      (the sigma assumed in cmrr_mc.py; about 0.6 V / 7 from the
                                      V_GS(off) range -1.5 to -0.9 V of SLPS732B p. 5) at 5 mA:
                                      V_GS from jfet_calibration.json, V_TO from the card; and with the
                                      square-law overdrive sqrt(I_D / (beta (1 + lambda V_DS)))
  R_G's thermal noise                 sqrt(4kT R_G), R_G = 10.1 ohm (H) and 2.49 ohm (L)
  differential penalty                10 log10(2) dB
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np

KT = 1.380649e-23 * 298.15
Q = 1.602176634e-19
K_B = 1.380649e-23
T_SPICE = 300.15                 # ngspice's default temperature, 27 C


def en_parallel(e1: float, n: float) -> float:
    return e1 / math.sqrt(n)


def vn_source(f, e_n, fc, c_in, zs, i_n=0.0, include_source=True):
    """Total input noise density (V/rtHz) with source impedance zs (complex array or scalar)."""
    w = 2 * np.pi * np.asarray(f, dtype=float)
    en2 = e_n ** 2 * (1 + fc / np.asarray(f, dtype=float))
    zs = np.asarray(zs, dtype=complex)
    v2 = en2 * np.abs(1 + 1j * w * c_in * zs) ** 2 + (i_n ** 2) * np.abs(zs) ** 2
    if include_source:
        v2 = v2 + 4 * KT * np.real(zs)
    return np.sqrt(v2)


def n_opt_resistive(f, c1, rs):
    return 1.0 / (2 * np.pi * np.asarray(f) * c1 * rs)


def band_rms(e1, fc, c1, n, rs, f_lo, f_hi, npts=2000):
    """rms amplifier noise (V) over [f_lo, f_hi] with a resistive source rs, source noise excluded."""
    f = np.logspace(math.log10(f_lo), math.log10(f_hi), npts)
    v = vn_source(f, e1 / math.sqrt(n), fc, n * c1, rs, 0.0, include_source=False)
    return math.sqrt(float(np.trapezoid(v ** 2, f)))


def noise_figure_db(vn_total, rs):
    """Noise figure of the amplifier with source rs: total over source-only noise power."""
    return 10 * np.log10(vn_total ** 2 / (4 * KT * rs))


def closed_forms() -> dict:
    """The numbers of Section 1 of the note (see the module docstring)."""
    import jfet_data as JD
    import models
    import spice
    kt4 = 4 * K_B * T_SPICE
    vt = K_B * T_SPICE / Q
    cal = json.loads((spice.RESULTS / "jfet_calibration.json").read_text(encoding="utf-8"))
    j150 = cal["JFE150"]
    gm = j150["gm"]
    out = dict(T_K=T_SPICE)
    out["JFE150 channel noise"] = dict(
        gm=gm, gm_source="jfet_calibration.json JFE150.gm (5 mA, 5 V)",
        e_th=math.sqrt(kt4 * 2 / 3 / gm), e_th_25C=math.sqrt(4 * K_B * 298.15 * 2 / 3 / gm),
        e_ngspice_with_RS_RD=j150["en_model_white"], e_datasheet=j150["en_target_white"])
    out["current doubling"] = dict(factor=2 ** -0.25, improvement=1 - 2 ** -0.25)
    out["gate-current shot noise"] = {f"{ig:g}": math.sqrt(2 * Q * ig) for ig in (1e-12, 10e-12, 100e-12, 1e-9)}
    out["e_n/i_n crossover"] = {
        f"I_G {ig:g}": dict(i_n=math.sqrt(2 * Q * ig),
                            R_x={f"e_n {en:g}": en / math.sqrt(2 * Q * ig) for en in (0.8e-9, 0.9e-9, 1e-9)},
                            R_source_thermal=kt4 / (2 * Q * ig), R_source_thermal_2VT_over_IG=2 * vt / ig)
        for ig in (1e-12, 1e-9)}
    out["e_n/i_n crossover"]["note"] = "1 nV / 1 fA = 1 Mohm (identity); R_x = e_n / i_n"
    e2140, c2140 = JD.JFETS["JFE2140"][2] * 1e-9, JD.JFETS["JFE2140"][5] * 1e-12
    e150, c150 = JD.JFETS["JFE150"][2] * 1e-9, JD.JFETS["JFE150"][5] * 1e-12
    e5564 = cal["2N5564"]["en_target_white"]
    out["Eq. (2)"] = {
        "H: 2 x JFE2140 per side": dict(e_1=e2140, N=2, e_side=e2140 / math.sqrt(2), e_diff=math.sqrt(2) * e2140 / math.sqrt(2),
                                        C_in=2 * c2140, src="JFE2140 0.9 nV/rtHz at 5 mA (SLPS730B Fig. 6-16), 13 pF (SLPS730B p. 5)"),
        "L: 12 x JFE150 per side": dict(e_1=e150, N=12, e_side=e150 / math.sqrt(12), e_diff=math.sqrt(2) * e150 / math.sqrt(12),
                                        C_in=12 * c150, src="JFE150 0.8 nV/rtHz at 5 mA, 24 pF at 5 V (SLPS732B p. 5, Table 6.5)"),
        "SR560: 1 x 2N5564 per side": dict(e_1=e5564, N=1, e_side=e5564, e_diff=math.sqrt(2) * e5564,
                                           src="the 2N5564 calibration target (models.py; jfet_model_check.json '2N5564 targets')"),
    }
    f0 = 10e6
    out["Eq. (4)"] = dict(f=f0, C_1=c150, R_s_N12=1 / (2 * math.pi * f0 * 12 * c150),
                          R_s_N1=1 / (2 * math.pi * f0 * c150))
    card = j150["card"]          # the calibrated card keeps TI's VTO, BETA and LAMBDA
    vto, beta, lam = models._get(card, "vto"), models._get(card, "beta"), models._get(card, "lambda")
    vov_op = j150["vgs"] - vto
    vov_sq = math.sqrt(j150["id"] / (beta * (1 + lam * j150["vds"])))
    dvto = 0.085
    out["current sharing"] = dict(
        dVTO=dvto, dVTO_source="sigma assumed in cmrr_mc.py; 0.6 V / 7 = 0.0857 V from SLPS732B p. 5 "
                               "(V_GS(off) -1.5 to -0.9 V)", V_GS=j150["vgs"], V_TO=vto, I_D=j150["id"],
        overdrive_operating_point=vov_op, dI_over_I=2 * dvto / vov_op,
        overdrive_square_law=vov_sq, dI_over_I_square_law=2 * dvto / vov_sq)
    out["R_G thermal noise"] = {f"{rg:g} ohm": math.sqrt(kt4 * rg) for rg in (10.1, 2.49)}
    out["differential penalty dB"] = 10 * math.log10(2)
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    import spice
    r = closed_forms()
    ch = r["JFE150 channel noise"]
    print(f"JFE150: g_m {ch['gm'] * 1e3:.3f} mS -> sqrt(4kT 2/3 / g_m) = {ch['e_th'] * 1e9:.4f} nV/rtHz "
          f"(25 C: {ch['e_th_25C'] * 1e9:.4f}); ngspice with RS, RD {ch['e_ngspice_with_RS_RD'] * 1e9:.4f}; data sheet "
          f"{ch['e_datasheet'] * 1e9:.2f}")
    print(f"2^(-1/4) = {r['current doubling']['factor']:.4f}: doubling I_D lowers e by {100 * r['current doubling']['improvement']:.1f} %")
    print("sqrt(2 q I_G): " + ", ".join(f"{k} A: {v * 1e15:.3f} fA/rtHz" for k, v in r["gate-current shot noise"].items()))
    for k, v in r["e_n/i_n crossover"].items():
        if k.startswith("I_G"):
            print(f"{k} A: R_x " + ", ".join(f"{e}: {x / 1e3:.1f} kohm" for e, x in v["R_x"].items())
                  + f"; i_n R = sqrt(4kTR) at {v['R_source_thermal']:.4g} ohm")
    for k, v in r["Eq. (2)"].items():
        print(f"Eq. (2) {k}: per side {v['e_side'] * 1e9:.4f}, differential {v['e_diff'] * 1e9:.4f} nV/rtHz"
              + (f", C_in {v['C_in'] * 1e12:.0f} pF" if "C_in" in v else ""))
    e4 = r["Eq. (4)"]
    print(f"Eq. (4) at 10 MHz, JFE150: N = 12 for R_s = {e4['R_s_N12']:.2f} ohm, N = 1 for {e4['R_s_N1']:.1f} ohm")
    cs = r["current sharing"]
    print(f"Delta I / I = 2 x {cs['dVTO'] * 1e3:.0f} mV / {cs['overdrive_operating_point'] * 1e3:.1f} mV = {cs['dI_over_I']:.3f} "
          f"(square law {cs['overdrive_square_law'] * 1e3:.1f} mV: {cs['dI_over_I_square_law']:.3f})")
    print("sqrt(4kT R_G): " + ", ".join(f"{k}: {v * 1e9:.4f} nV/rtHz" for k, v in r["R_G thermal noise"].items())
          + f"; differential penalty {r['differential penalty dB']:.2f} dB")
    (spice.RESULTS / "noise_theory.json").write_text(json.dumps(r, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
