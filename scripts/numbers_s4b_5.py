"""The derived numbers of Sections 4.4-5 of the note (input, chain, offsets and drift, power, the
1/f trade-off, the simulation method, the vendor models and Table 7) that are not a direct readout
of one archived result: arithmetic, ratios, differences, unit conversions and single roundings of
archived results, and the data-sheet constants they use (each cited where it is defined below).
No simulation is run; only archived results in ../sim/results/ are read.

Constants: k = 1.380649e-23 J/K, T = 300.15 K (ngspice's 27 C; spice.KT = kT).

Input admittance (Section 4.4, Figure 10; zin_numbers.json, protection.json):
    C_eff = Im(Y_in) / w of the bare front ends (input A driven, B grounded) at 1 k, 100 k, 300 k
            and 1 MHz; the range over 1 k - 300 kHz and the value at 1 MHz
    C_JFETs = N C_iss                                  H: 2 x 13 pF, L: 12 x 24 pF
    the frequencies at which C_eff reaches twice its minimum (protection.json)
    R_par = 1 / Re(Y_in): the negative value closest to zero, bare and with the input network
    the input network's conductance  Re Y_Z = w^2 C_Z^2 R_Z / (1 + w^2 C_Z^2 R_Z^2)  <= 1 / R_Z,
        and the check  Re Y_net(f) = Re Y_bare(f) + Re Y_Z(f) + 1 / R_B  at the minimum
    C_in = C_P + C_Z below f_Z = 1 / (2 pi R_Z C_Z), against the simulated C_eff with the network
    the H/L crossover against the source resistance R_s (noise_vs_source.json, the full chain at a
        total gain of 1000): R_x where e_H(R_s) = e_L(R_s), by linear interpolation of ln(e_H / e_L)
        in log10 R_s between the grid points where it changes sign (the method of numbers_s1_3.py)
Protection (Section 4.4, Table 6d; protection.json): relative costs e_tot / e_FE - 1 of 10 and
    22 ohm, the noise-figure increases, H's current noise with leakage i_tot / i_RB - 1, the
    forward bias per diode |V_GS| / n of the bootstrapped clamp strings, the common-mode range.
Chain (Section 4.5):
    Figure 11's drawn setting  G = G_FE (10 a3)(10 a4)(5 a5)  with a3 = a4 = 1/2, a5 = 2/5
    S2's noise gain with four equal resistors  1 + R_f / R_g = 1 + 499/499
    S5 into 50 ohm through 49.9 ohm:  v_op = v_load (49.9 + 50) / 50,  i = v_op / 99.9 ohm
    the THS3091's i_n- R_F against the chain at a total gain of 1 (chain_noise.json, H_LN_1):
        e_S5 = i_n- R_F;  share of the noise power (e_S5 / e_chain)^2;
        at 1 Hz with a 1/f continuation of the data sheet's 10 Hz value (as the corrected model):
        i_n-(1 Hz) = sqrt(i_w^2 + (i_10^2 - i_w^2) * 10 Hz / 1 Hz)
Offset and trim (Section 4.6; cmrr_mc.py, cmrr_mc.json, curves_noise.npz):
    within a dual: sigma_d = sqrt(2) sigma_half (V_TO and beta);  data-sheet limit / sigma_d;
        mean |dV_GS| = sigma_d sqrt(2 / pi)
    square law at a fixed current:  dV_GS = dV_TO - (1/2) (V_GS - V_TO) dbeta / beta,
        V_GS - V_TO = sqrt(I_D / beta);  between the two sides (N per side, independent devices)
        sigma_side = sigma_d / sqrt(N)
    unsorted JFE150: sigma = (V_GS(off),max - V_GS(off),min) / 7 (the range taken as +/-3.5 sigma);
        the two sides' means differ by sigma sqrt(2 / 12)
    a uniform +/-5 mV bin: sigma = 5 mV / sqrt(3)
    offset at the input = V_out,dc,rms / G (cmrr_mc.json)
    trim: the input-referred shift of a current dI injected into one summing node is dI w, with the
        weight of Eq. (9) for a current entering the summing node,  w = 1/(N g_m) + R_F/G.  w is read
        from the simulated noise of R_D, which enters the same node (Table 8's runs,
        curves_noise.npz, group 'drain-side R_D', both sides):
            e_RD = sqrt(2) w sqrt(4kT / R_D)   ->   w = e_RD / (sqrt(2) sqrt(4kT / R_D))
        at the lowest frequency of the runs, 0.1 Hz (w is flat to 0.1 % from 0.1 Hz to 1 MHz).
        Closed-form check (H): 1/(N g_m) with g_m of the operating point (fe_gain_derived.json) and
        with the card's source resistance R_S in series,  1/(N g_m') = (1/g_m + R_S) / N.
        dI = V_DAC / R_trim;  range dv = dI w;  12-bit step 2 dv / 2^12;
        noise of R_trim at the input  sqrt(4kT / R_trim) w
Power (Section 4.7; large_signal.json, sink_power.json, chain_extras.json):
    PSRR ranges of H at a gain of 100; L at 1000 with the 6 V sinks minus H, per rail and frequency
    a regulator's noise at the input  e_in = e_reg 10^(-PSRR/20)  (PSRR at 100 Hz, the lowest
        frequency simulated)
    ripple rejection in series  regulator + amplifier (dB) at 1 MHz, per rail
    regulator dissipation P = V_headroom I (chain_extras.json); junction rise  dT = P theta_JA
    LT3045 output  V = I_SET R_SET,  with the +/-1 % initial accuracy of I_SET
1/f against bandwidth (Section 4.8; curves_noise.npz): the totals at 1 and 10 Hz, the op amps'
    and the input JFETs' groups, and the projection without the op amps' group
        e' = sqrt(e^2 - e_op^2)
    capacitance ratio of JFE150 to JFE2140: 24 pF / 13 pF
Method (Section 5.1): Monte Carlo trials per case; the THD grid of large_signal.json.
Vendor models (Section 5.3, Table 7; model_defects.json, opamp_noise_check.json):
    model / data-sheet ratios (the LSK389B card's white noise with and without NLEV/GDSNOI against the
        LSK389 data sheet's 1.6 nV/rtHz at 1 kHz); the LTspice library record (version, date, SHA-256,
        change-log entry); HD3 in dBc = 20 log10(h3) and its excess over the data sheet's curve,
        as read and scaled to the curve's amplitude (HD3 relative to the fundamental proportional to
        V^2: + 40 log10(2 Vpp / 1 Vpp) = +12.0 dB; model_defects.json)
    current-noise 1/f corner  f_c = f_0 (i_n(f_0) / i_n,w)^2,  f_0 = 10 Hz
    the white current noise of the THS4021/THS4031 models against the data sheets, and its effect
        on the front ends' white noise through Eq. (9):
            e'^2 = e^2 + 2 w^2 (i_ds^2 - i_model^2),  relative change e'/e - 1  (10 kHz)
    the published THS4021 in H at a gain of 100 and the published THS3091 in the chain: ratios
Writes ../sim/results/numbers_s4b_5.json.  Usage: python numbers_s4b_5.py
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "sim" / "results"
SCRIPTS = ROOT / "scripts"
KT = 1.380649e-23 * 300.15          # as spice.KT (ngspice's 27 C)

OUT: dict[str, dict] = {}


def put(key: str, value, text: str, source: str, unit: str = "") -> None:
    """One quantity: its value (SI unless the unit says otherwise), the text the note uses (one
    rounding of the value), and its source."""
    OUT[key] = dict(value=value, unit=unit, text=text, source=source)


def load(name: str) -> dict:
    return json.loads((R / name).read_text(encoding="utf-8"))


def sig(x: float, n: int = 2) -> str:
    """x rounded once to n significant figures, written without an exponent."""
    if x == 0:
        return "0"
    d = n - 1 - int(math.floor(math.log10(abs(x))))
    return f"{round(x, d):.{max(d, 0)}f}"


def crossing(rs, eh, el) -> float | None:
    """The source resistance where e_H / e_L falls through 1: linear interpolation of ln(e_H / e_L)
    in log10 R_s between the two grid points where it changes sign (the method of numbers_s1_3.py)."""
    d = np.log(np.asarray(eh) / np.asarray(el))
    for i in range(len(rs) - 1):
        if d[i] > 0 >= d[i + 1]:
            x0, x1 = math.log10(rs[i]), math.log10(rs[i + 1])
            return 10 ** (x0 + d[i] / (d[i] - d[i + 1]) * (x1 - x0))
    return None


def at(f: np.ndarray, y: np.ndarray, f0: float) -> float:
    """The value at the grid point nearest to f0 (log scale)."""
    return float(y[int(np.argmin(np.abs(np.log10(f) - np.log10(f0))))])


# --------------------------------------------------------------------------------------------
# Data-sheet constants (typical values unless stated; pages are the printed page numbers, which
# equal the PDF page numbers for the TI and ADI documents)
# --------------------------------------------------------------------------------------------
DS = dict(
    # TI JFE2140, SLPS730B, Sec. 6.5 Electrical Characteristics, p. 5
    JFE2140_ciss=13e-12,            # C_iss at V_DS = 5 V
    JFE2140_dvgs_typ=1e-3,          # |V_GS1 - V_GS2| at I_DS = 2 mA, typ
    JFE2140_dvgs_max=4e-3,          # the same, max
    JFE2140_drift_max=10e-6,        # drift of the mismatch, max, -40 to +125 C (V/K)
    JFE2140_idss_ratio_lim=0.05,    # I_DSS1 / I_DSS2 = 0.95 ... 1.05 (min, max)
    JFE2140_en10_2mA=2.4e-9,        # e_n at 10 Hz, I_DS 2 mA, V_DS 10 V
    # TI JFE150, SLPS732B, Sec. 6.5, p. 5
    JFE150_ciss=24e-12,             # C_iss at V_DS = 5 V
    JFE150_vgsoff=(-1.5, -0.9),     # V_GSC (cutoff) min and max
    JFE150_en10_5mA=1.8e-9,         # e_n at 10 Hz, 5 mA, 5 V
    JFE150_en10_2mA=1.6e-9,         # e_n at 10 Hz, 2 mA, 5 V
    # InterFET IF3601, IF35076.R01, p. 3, typical noise curve (V_DS 3 V, I_D 5 mA)
    IF3601_en10=0.6e-9,
    # TI THS4021, SLOS265F: p. 1 (2 GHz GBW, 1.2 nV/rtHz), Sec. 5.6 p. 6 (SOIC: 1.2 nV, 2.3 pA,
    # f > 10 kHz), Sec. 5.7 p. 8 (DGN: 1.5 nV, 2 pA)
    THS4021_gbw=2e9, THS4021_en=1.2e-9, THS4021_en_dgn=1.5e-9, THS4021_in=2.3e-12,
    # TI THS4031, SLOS224L, Sec. 5.6 p. 6 (R_L 150 ohm; f > 10 kHz)
    THS4031_in=2.3e-12,
    # 10 Hz current noise of both: SLOS265F Fig. 5-12 (p. 11) and SLOS224L Fig. 5-14 (p. 12), read from the
    # pixels at the 10 Hz frame edge, 18.5-18.8 pA/rtHz (18.2 at the curve's first visible point, 10.4 Hz;
    # the first reading by eye was 20); models.py's 1/f generators are fitted to it (1/f part 18.5 pA/rtHz)
    THS4021_in10=18.6e-12, THS4031_in10=18.6e-12,
    # TI THS3091, SLOS423K, Sec. 7.5: p. 6 (noise, f > 10 kHz), p. 7 (swing, current, +/-15 V)
    THS3091_in_inv=14e-12, THS3091_in10=200e-12,      # 10 Hz: Fig. 7-16, p. 12, read by eye
    THS3091_swing_1k_min=12.8, THS3091_swing_100_min=12.1,
    THS3091_iout_min=(225e-3, 200e-3),                 # sourcing, sinking, 25 C, into 40 ohm
    # TI LM7171, SNOS760D, Sec. 5.5 p. 5 (A grade): slew rate, unity-gain bandwidth
    LM7171A_sr=4100e6, LM7171A_ugbw=160e6,
    # TI OPA2810, SBOS789C p. 1; OPA1612, SBOS450C p. 1
    OPA2810_vs=(4.75, 27.0), OPA2810_gbw=70e6, OPA1612_bw=40e6, OPA1612_en=1.1e-9,
    # TI TMUX6219, SCDS420E: Sec. 5.6 p. 6 (R_ON at +/-15 V, 25 C), Sec. 5.7 p. 7 (C_ON)
    TMUX6219_ron=(2.1, 2.9), TMUX6219_con=148e-12,
    # ADI LT3094 Rev. 0: p. 4 (noise at 10 Hz with C_SET 4.7 uF), p. 3 (theta_JA, MSOP) and
    # Table 4, p. 28 (33 C/W with 2500 mm^2 of top copper ... 35 C/W with 100 mm^2);
    # ripple rejection p. 5: 74 dB at 1 MHz (C_SET 0.47 uF)
    LT3094_en10=70e-9, LT3094_psrr_1M=74.0, theta_ja=(33.0, 35.0),
    # ADI LT3045 Rev. D: p. 3 (70 nV/rtHz at 10 Hz, C_SET 4.7 uF; 76 dB at 1 MHz), p. 1 (output
    # 0 V to 15 V; SET current 100 uA, +/-1 % initial accuracy)
    LT3045_en10=70e-9, LT3045_psrr_1M=76.0, LT3045_vout_max=15.0, I_SET=100e-6, I_SET_tol=0.01,
    # SR560 manual Rev. 3.1, specifications, p. 5; NF 5307 operation manual, Sec. 5.1, p. 31
    SR560_cin=25e-12, NF5307_cin_max=35e-12,
)
R_SET = 150e3                       # design (Section 4.7)
SIGMA = dict(half_vto=0.85e-3, half_beta=0.01, dual_vto=0.100, dual_beta=0.05,   # cmrr_mc.perturb
             bin_vto=0.085, bin_beta=0.05, in_bin_vto=3e-3, in_bin_beta=0.02)


def check_cmrr_mc_sigmas() -> None:
    """The sigma values above are those that cmrr_mc.py draws (perturb)."""
    src = (SCRIPTS / "cmrr_mc.py").read_text(encoding="utf-8")
    for tok in ("g(0.100, \"jfet\")", "g(0.05, \"jfet\")", "g(0.00085, \"jfet\")", "g(0.01, \"jfet\")",
                "g(0.085, \"jfet\")", "g(0.003, \"jfet\")", "g(0.02, \"jfet\")"):
        assert tok in src, f"cmrr_mc.py no longer draws {tok}"


# --------------------------------------------------------------------------------------------
def input_admittance() -> None:
    z = load("zin_numbers.json")
    pr = load("protection.json")
    src = "zin_numbers.json"
    for k, lab in (("H100", "H"), ("L200", "L")):
        c = z[k]["bare_dm"]["C_eff"]
        lo = [c[f] for f in ("1000", "100000", "300000")]
        put(f"{lab}_Ceff_bare_1k_300k_pF", [min(lo) * 1e12, max(lo) * 1e12],
            f"{min(lo) * 1e12:.2f}-{max(lo) * 1e12:.2f} pF" if lab == "L" else
            f"{min(lo) * 1e12:.3f}-{max(lo) * 1e12:.3f} pF", f"{src} {k}.bare_dm.C_eff (1 k, 100 k, 300 kHz)", "pF")
        put(f"{lab}_Ceff_bare_1M_pF", c["1e+06"] * 1e12, f"{c['1e+06'] * 1e12:.2f} pF", f"{src} {k}.bare_dm.C_eff 1 MHz", "pF")
        ar = pr["admittance_readout"][k]
        put(f"{lab}_C_JFETs_pF", ar["C_JFETs"] * 1e12, f"{ar['n']} x {ar['C_iss'] * 1e12:g} = {ar['C_JFETs'] * 1e12:g} pF",
            "N C_iss; C_iss SLPS730B / SLPS732B Sec. 6.5 p. 5 (protection.json admittance_readout)", "pF")
        put(f"{lab}_Ceff_twice_below_Hz", ar["f_rise_low"], f"{ar['f_rise_low']:.0f} Hz",
            f"protection.json admittance_readout.{k}.f_rise_low (C_eff >= 2 x its minimum)", "Hz")
        put(f"{lab}_Ceff_twice_above_MHz", ar["f_rise_high"] / 1e6, f"{ar['f_rise_high'] / 1e6:.2f} MHz",
            f"protection.json admittance_readout.{k}.f_rise_high", "MHz")
        b = z[k]["bare_dm"]
        put(f"{lab}_Rneg_bare", b["Rpar_neg_min"],
            (f"{b['Rpar_neg_min'] / 1e3:.2f} kohm" if lab == "H" else f"{b['Rpar_neg_min']:.0f} ohm")
            + f" at {b['Rpar_neg_min_f'] / 1e6:.1f} MHz", f"{src} {k}.bare_dm.Rpar_neg_min(_f)", "ohm")
        s = z[k]["sources_archived"]
        n = z[k]["network_dm"]
        if n["Rpar_neg_min"] is None:
            put(f"{lab}_network_ReY", "positive", "Re Y_in > 0 at every frequency", f"{src} {k}.network_dm.Rpar_neg_min = null")
        else:
            put(f"{lab}_network_ReY_negative_MHz", [n["ReY_negative_from"] / 1e6, n["ReY_negative_to"] / 1e6],
                f"from {n['ReY_negative_from'] / 1e6:.2f} to {n['ReY_negative_to'] / 1e6:.0f} MHz",
                f"{src} {k}.network_dm.ReY_negative_from/to", "MHz")
            put(f"{lab}_Rneg_network", n["Rpar_neg_min"],
                f"{n['Rpar_neg_min'] / 1e3:.2f} kohm at {n['Rpar_neg_min_f'] / 1e6:.1f} MHz",
                f"{src} {k}.network_dm.Rpar_neg_min(_f)", "ohm")
        put(f"{lab}_CP_plus_CZ_pF", z[k]["C_P_plus_C_Z"] * 1e12, f"{z[k]['C_P_plus_C_Z'] * 1e12:.0f} pF",
            f"{src} {k}.C_P_plus_C_Z (chain.INPUT_NET)", "pF")
        put(f"{lab}_f_Z_MHz", z[k]["f_Z"] / 1e6, f"{z[k]['f_Z'] / 1e6:.1f} MHz", f"{src} {k}.f_Z = 1/(2 pi R_Z C_Z)", "MHz")
        cn = n["C_eff"]["100000"]
        put(f"{lab}_Ceff_network_100k_pF", cn * 1e12, f"{cn * 1e12:.1f} pF", f"{src} {k}.network_dm.C_eff 100 kHz", "pF")
        put(f"{lab}_network_largest_peak_dB", z[k]["network_largest_peak_db"], f"{z[k]['network_largest_peak_db']:.2f} dB",
            f"{src} {k}.network_largest_peak_db", "dB")
    s = z["H100"]["sources_archived"]
    put("H_bare_1Meg_peak", [s["bare_1Meg"]["peak_db"], s["bare_1Meg"]["f_peak"] / 1e6],
        f"{s['bare_1Meg']['peak_db']:.0f} dB at {s['bare_1Meg']['f_peak'] / 1e6:.2f} MHz",
        "zin_numbers.json H100.sources_archived.bare_1Meg", "dB, MHz")
    s = z["L200"]["sources_archived"]
    put("L_bare_1k_peak", [s["bare_1k"]["peak_db"], s["bare_1k"]["f_peak"] / 1e6],
        f"{s['bare_1k']['peak_db']:.0f} dB at {s['bare_1k']['f_peak'] / 1e6:.1f} MHz",
        "zin_numbers.json L200.sources_archived.bare_1k", "dB, MHz")
    s = z["H100"]["sources_archived"]["network_1k"]
    put("H_network_1k_peak", [s["peak_db"], s["f_peak"] / 1e6], f"{s['peak_db']:.2f} dB at {s['f_peak'] / 1e6:.1f} MHz",
        "zin_numbers.json H100.sources_archived.network_1k (the largest with the network)", "dB, MHz")
    # H: the network's conductance against the bare front end's negative conductance
    net = z["H100"]["network"]
    f0 = z["H100"]["bare_dm"]["ReY_min_f"]
    w = 2 * math.pi * f0
    x = w * net["cz"] * net["rz"]
    g_z = x * x / net["rz"] / (1 + x * x)
    g_bare = z["H100"]["bare_dm"]["ReY_min"]
    g_net = z["H100"]["network_dm"]["ReY_min"]
    put("H_GZ_max_mS", 1e3 / net["rz"], f"{1e3 / net['rz']:.2f} mS", "1 / R_Z, R_Z = 2.2 kohm (chain.INPUT_NET)", "mS")
    put("H_Gbare_at_min_mS", -g_bare * 1e3, f"{-g_bare * 1e3:.2f} mS at {f0 / 1e6:.1f} MHz",
        "zin_numbers.json H100.bare_dm.ReY_min (magnitude)", "mS")
    put("H_GZ_at_min_mS", g_z * 1e3, f"{g_z * 1e3:.2f} mS", "w^2 C_Z^2 R_Z / (1 + w^2 C_Z^2 R_Z^2) at the bare minimum", "mS")
    chk = g_bare + g_z + 1 / net["rbias"]
    put("H_ReY_network_check", [chk, g_net], f"{1 / chk:.0f} ohm (sum) against {1 / g_net:.0f} ohm (simulated)",
        "Re Y_bare + Re Y_Z + 1/R_B at 12.6 MHz against zin_numbers.json H100.network_dm.ReY_min", "S")
    # where L stops being the quieter input: the H/L crossover against the source resistance,
    # computed as in numbers_s1_3.py (the summary's numbers)
    nvs = load("noise_vs_source.json")
    rs = [r["rs"] for r in nvs["H_LN"]]
    assert rs == [r["rs"] for r in nvs["L"]]
    cross = {}
    for fk in nvs["H_LN"][0]["vn"]:
        eh = [r["vn"][fk] for r in nvs["H_LN"]]
        el = [r["vn"][fk] for r in nvs["L"]]
        cross[f"{float(fk):g}"] = crossing(rs, eh, el)
    put("H_L_crossover_ohm", cross,
        f"{sig(cross['1e+07'])} ohm at 10 MHz, {sig(cross['1e+06'] / 1e3)} kohm at 1 MHz, "
        f"{sig(cross['100000'] / 1e3)} kohm at 100 kHz, {sig(cross['1000'] / 1e3)}-{sig(cross['10'] / 1e3)} kohm at 1 kHz and 10 Hz",
        "noise_vs_source.json (full chain, G 1000): R_s where e_H = e_L, ln(e_H/e_L) interpolated linearly in "
        "log10 R_s between the grid points (as numbers_s1_3.py)", "ohm")
    put("SR560_Cin_pF", DS["SR560_cin"] * 1e12, "25 pF", "SR560 manual Rev. 3.1, specifications, p. 5 (PDF p. 9)", "pF")
    put("NF5307_Cin_pF", DS["NF5307_cin_max"] * 1e12, "less than 35 pF",
        "NF 5307 operation manual (D: 507571), Sec. 5.1, p. 31 (PDF p. 43)", "pF")


def protection() -> None:
    pr = load("protection.json")
    rows = {r["R_s"]: r for r in pr["table_6d (quoted floors)"]}
    put("H_floor_increase_10_22_pct", [rows[10]["H_increase"] * 100, rows[22]["H_increase"] * 100],
        f"{rows[10]['H_increase'] * 100:.0f}-{rows[22]['H_increase'] * 100:.0f} %",
        "protection.json table_6d (quoted floors), R_s 10 and 22 ohm, H_increase", "%")
    put("L_floor_increase_10_pct", rows[10]["L_increase"] * 100, f"{rows[10]['L_increase'] * 100:.0f} %",
        "protection.json table_6d (quoted floors), R_s 10 ohm, L_increase", "%")
    put("H_NF_increase_10_22_dB", [rows[10]["NF_H_1k_increase"], rows[22]["NF_H_1k_increase"]],
        f"{rows[10]['NF_H_1k_increase']:.1f}-{rows[22]['NF_H_1k_increase']:.1f} dB",
        "protection.json table_6d (quoted floors), NF_H_1k_increase", "dB")
    bias = pr["bias_resistor_noise"]["1e+08"]
    put("H_bias_noise_fA", bias * 1e15, f"{bias * 1e15:.1f} fA/rtHz", "protection.json bias_resistor_noise 1e+08", "fA/rtHz")
    for i_l in ("1e-11", "1e-10"):
        v = pr["H_current_noise_with_leakage"][i_l] / bias - 1
        put(f"H_current_noise_leak_{i_l}_pct", v * 100, f"{v * 100:.0f} %",
            f"protection.json H_current_noise_with_leakage[{i_l}] / bias_resistor_noise[1e+08] - 1", "%")
    op = pr["operating_points"]
    put("H_clamp_2_diodes_V", op["H"]["per_diode"]["2"], f"{op['H']['per_diode']['2']:.2f} V",
        "protection.json operating_points.H.per_diode.2 (|V_GS| / 2)", "V")
    put("L_clamp_3_diodes_V", op["L"]["per_diode"]["3"], f"{op['L']['per_diode']['3']:.2f} V",
        "protection.json operating_points.L.per_diode.3 (|V_GS| / 3)", "V")
    for fe in ("H", "L"):
        put(f"{fe}_CM_range_V", [op[fe]["V_CM_min"], op[fe]["V_CM_max"]],
            f"{op[fe]['V_CM_min']:+.1f} V to {op[fe]['V_CM_max']:+.1f} V",
            f"protection.json operating_points.{fe}.V_CM_min/max", "V")


def chain_stages() -> None:
    import chain                                    # imported for the gain formula only
    s = chain.Setting("H100", a3=0.5, a4=0.5, a5=0.4)
    put("fig11_total_gain", s.gain, f"{s.gain:.0f}", "chain.Setting('H100', 0.5, 0.5, 0.4).gain "
        "(make_schematics.CHAIN_SETTING): G_FE x 5 x 5 x 2", "")
    da = load("da_compare.json")
    t = {k: next(r for r in da[k]["thd"] if r["f0"] == 1e7 and r["vout_pp"] == 1.0) for k in ("THS4031", "LM7171")}
    put("S2_THS4031_THD_10MHz_pct", t["THS4031"]["thd"] * 100, f"{t['THS4031']['thd'] * 100:.1f} %",
        "da_compare.json THS4031.thd (10 MHz, 1 Vpp, total gain 100)", "%")
    put("S2_LM7171_THD_10MHz_pct", t["LM7171"]["thd"] * 100, f"{t['LM7171']['thd'] * 100:.3f} %",
        "da_compare.json LM7171.thd (10 MHz, 1 Vpp)", "%")
    ls = load("large_signal_THS4031.json")
    sr = next(r for r in ls["H100"]["step"] if r["vstep"] == 10.0)["slew_v_us"]
    put("S2_THS4031_slew_V_us", sr, f"{sr:.0f} V/us", "large_signal_THS4031.json H100.step (10 V)", "V/us")
    put("LM7171A", [DS["LM7171A_sr"] / 1e6, DS["LM7171A_ugbw"] / 1e6], "4100 V/us, 160 MHz",
        "SNOS760D Sec. 5.5, p. 5 (A grade; 200 MHz is the B grade); stable for gains of +2 or more, p. 1", "V/us, MHz")
    r_da = 499.0                                     # S2's four resistors (chain.py)
    put("S2_noise_gain", 1 + r_da / r_da, f"1 + 499/499 = {1 + r_da / r_da:g}", "difference amplifier, four equal "
        "resistors: noise gain 1 + R_f/R_g", "")
    v_load = 5.0
    v_op = v_load * (49.9 + 50) / 50
    put("S5_50ohm", [v_op, v_op / 99.9], f"{v_op:.1f} V and {v_op / 99.9 * 1e3:.0f} mA at the THS3091 for 5 V into 50 ohm",
        "v_op = v_load (49.9 + 50)/50; against SLOS423K Sec. 7.5 p. 7: >= 12.1 V into 100 ohm, >= 200 mA", "V, A")
    put("THS3091_swing_min", [DS["THS3091_swing_1k_min"], DS["THS3091_swing_100_min"]], "12.8 V (1 kohm), 12.1 V (100 ohm)",
        "SLOS423K Sec. 7.5, p. 7 (min, 25 C, +/-15 V)", "V")
    put("TMUX6219", [*DS["TMUX6219_ron"], DS["TMUX6219_con"] * 1e12], "2.1 ohm typ, 2.9 ohm max, 148 pF on",
        "SCDS420E Sec. 5.6 p. 6, Sec. 5.7 p. 7 (+/-15 V, 25 C)", "ohm, pF")
    # the THS3091's inverting-input current noise in R_F at a total gain of 1
    cn = load("chain_noise.json")["H_LN_1"]["en"]
    e_w, e_1 = cn["100000.0"], cn["1"]
    rf = 1e3
    e_s5 = DS["THS3091_in_inv"] * rf
    i1 = math.sqrt(DS["THS3091_in_inv"] ** 2 + (DS["THS3091_in10"] ** 2 - DS["THS3091_in_inv"] ** 2) * 10)
    put("chain_gain1_white_nV", e_w * 1e9, f"{e_w * 1e9:.1f} nV/rtHz", "chain_noise.json H_LN_1.en 100 kHz", "nV/rtHz")
    put("chain_gain1_1Hz_nV", e_1 * 1e9, f"{sig(e_1 * 1e9)} nV/rtHz", "chain_noise.json H_LN_1.en 1 Hz", "nV/rtHz")
    put("S5_in_RF_white_nV", e_s5 * 1e9, f"{e_s5 * 1e9:.0f} nV/rtHz", "i_n- R_F = 14 pA/rtHz x 1 kohm (SLOS423K p. 6)", "nV/rtHz")
    put("S5_share_white", (e_s5 / e_w) ** 2, f"{(e_s5 / e_w) ** 2:.2f} (a third)", "(i_n- R_F / e_chain)^2, white", "")
    put("S5_in_1Hz_pA", i1 * 1e12, f"{i1 * 1e12:.0f} pA/rtHz", "sqrt(i_w^2 + (i_10^2 - i_w^2) 10): 1/f below 10 Hz", "pA/rtHz")
    put("S5_in_RF_1Hz_nV", i1 * rf * 1e9, f"{sig(i1 * rf * 1e9)} nV/rtHz", "i_n-(1 Hz) R_F", "nV/rtHz")
    put("S5_share_1Hz", (i1 * rf / e_1) ** 2, f"{(i1 * rf / e_1) ** 2:.2f}", "(i_n-(1 Hz) R_F / e_chain(1 Hz))^2", "")


def offsets() -> dict:
    check_cmrr_mc_sigmas()
    mc = load("cmrr_mc.json")
    import frontend as F                             # the cases' N, R_F, R_G and gain only
    cal = load("jfet_calibration.json")
    sd_v = math.sqrt(2) * SIGMA["half_vto"]
    sd_b = math.sqrt(2) * SIGMA["half_beta"]
    put("H_MC_dual_sigma", [sd_v * 1e3, sd_b * 100], f"{sd_v * 1e3:.1f} mV and {sd_b * 100:.1f} %",
        "sqrt(2) x (0.85 mV, 1 %) per half (cmrr_mc.py perturb)", "mV, %")
    put("H_MC_limits_in_sigma", [DS["JFE2140_dvgs_max"] / sd_v, DS["JFE2140_idss_ratio_lim"] / sd_b],
        f"{DS['JFE2140_dvgs_max'] / sd_v:.1f} sigma and {DS['JFE2140_idss_ratio_lim'] / sd_b:.1f} sigma",
        "4 mV / sigma_d and 0.05 / sigma_d (SLPS730B Sec. 6.5 p. 5: |dV_GS| max 4 mV, I_DSS ratio 0.95-1.05)", "")
    m = sd_v * math.sqrt(2 / math.pi)
    put("H_MC_mean_abs_dVGS_mV", m * 1e3, f"{m * 1e3:.2f} mV", "sigma_d sqrt(2/pi) against 1 mV typ (SLPS730B p. 5)", "mV")
    # square-law attribution of H's offset to V_TO and beta
    p = F.CASES["H100"]
    card = cal["JFE2140"]["card"]
    beta = float(re.search(r"BETA=([0-9.]+)m", card).group(1)) * 1e-3
    vov = math.sqrt(p.id / beta)
    s_b_side = 0.5 * vov * sd_b / math.sqrt(p.n)
    s_v_side = sd_v / math.sqrt(p.n)
    put("H_VGS_minus_VTO_V", vov, f"{vov:.2f} V", "sqrt(I_D / beta), I_D 5 mA, beta 14.24 mA/V^2 (JFE2140 card)", "V")
    put("H_offset_terms_mV", [s_b_side * 1e3, s_v_side * 1e3, math.hypot(s_b_side, s_v_side) * 1e3],
        f"beta {s_b_side * 1e3:.1f} mV, V_TO {s_v_side * 1e3:.2f} mV, together {math.hypot(s_b_side, s_v_side) * 1e3:.1f} mV rms",
        "(1/2)(V_GS - V_TO) sigma_beta,d / sqrt(N) and sigma_VTO,d / sqrt(N), N = 2", "mV")
    off = {}
    for k in ("H100", "H10", "L200"):
        v = mc[k]["vout_dc_rms"] / mc[k]["gain"]
        off[k] = v
        put(f"{k}_MC_offset_input_mV", v * 1e3, f"{mc[k]['vout_dc_rms']:.2f} V rms at G = {mc[k]['gain']:.0f}: {v * 1e3:.1f} mV",
            f"cmrr_mc.json {k}.vout_dc_rms / gain ({mc[k]['trials']} trials)", "mV")
    put("MC_trials", {k: mc[k]["trials"] for k in mc if isinstance(mc[k], dict) and "trials" in mc[k]},
        "12 per case; 6 with one class of mismatch; 4 for the R_UP test", "cmrr_mc.json <case>.trials", "")
    # L: unsorted and binned JFE150
    s_u = (DS["JFE150_vgsoff"][1] - DS["JFE150_vgsoff"][0]) / 7
    n_l = F.CASES["L200"].n
    d_u = s_u * math.sqrt(2 / n_l)
    put("L_unsorted_sigma_mV", s_u * 1e3, f"{s_u * 1e3:.0f} mV", "(-0.9 V - (-1.5 V)) / 7 (SLPS732B Sec. 6.5 p. 5)", "mV")
    put("L_unsorted_side_diff_mV", d_u * 1e3, f"{d_u * 1e3:.0f} mV", "sigma sqrt(2/12)", "mV")
    put("L_unsorted_output_V", d_u * mc["L200"]["gain"], f"{d_u * mc['L200']['gain']:.0f} V rms",
        "x the total gain 1005 (cmrr_mc.json L200.gain)", "V")
    put("L_bin_sigma_mV", 5e-3 / math.sqrt(3) * 1e3, f"{5 / math.sqrt(3):.1f} mV",
        "uniform +/-5 mV: 5 mV / sqrt(3) (the code uses 3 mV)", "mV")
    return off


def trim(off: dict) -> None:
    import frontend as F
    z = np.load(R / "curves_noise.npz")
    fg = load("fe_gain_derived.json")
    cal = load("jfet_calibration.json")
    w = {}
    for k in ("H100", "H10", "L200"):
        p = F.CASES[k]
        rd = 600.0 if k.startswith("H") else 100.0          # R_D (Table 5)
        i_rd = math.sqrt(4 * KT / rd)
        f = z[f"{k}_f"]
        g = z[f"{k}_g_drain-side R_D"]
        w0 = float(g[0]) / (math.sqrt(2) * i_rd)
        wlist = [float(x) / (math.sqrt(2) * i_rd) for x in g[(f >= 0.1) & (f <= 1e6)]]
        w[k] = w0
        put(f"{k}_trim_weight_ohm", w0, f"{w0:.1f} ohm" if w0 < 10 else f"{w0:.0f} ohm",
            f"curves_noise.npz {k}_g_drain-side R_D at {f[0]:g} Hz / (sqrt(2) sqrt(4kT/R_D)); "
            f"flat to {(max(wlist) / min(wlist) - 1) * 100:.2f} % from 0.1 Hz to 1 MHz", "ohm")
        put(f"{k}_RF_over_G_ohm", p.rf / p.gain, f"{p.rf / p.gain:.2f} ohm", f"frontend.CASES['{k}']: R_F / G", "ohm")
    # closed-form check for H: g_m of the operating point, with and without the card's R_S
    gm_side = fg["g_m one side from the operating point (S)"]
    rs = float(re.search(r"RS=([0-9.]+)", cal["JFE2140"]["card"]).group(1))
    n_h = F.CASES["H100"].n
    gm1 = gm_side / n_h
    for k in ("H100", "H10"):
        p = F.CASES[k]
        w_int = 1 / gm_side + p.rf / p.gain
        w_rs = (1 / gm1 + rs) / n_h + p.rf / p.gain
        put(f"{k}_weight_closed_form_ohm", [w_int, w_rs],
            f"{w_int:.2f} ohm with N g_m = {gm_side * 1e3:.1f} mS; {w_rs:.2f} ohm with R_S = {rs:g} ohm in series",
            "1/(N g_m) + R_F/G (fe_gain_derived.json); (1/g_m + R_S)/N + R_F/G (JFE2140 card RS)", "ohm")
    p = F.CASES["L200"]
    ngm_l = 1 / (w["L200"] - p.rf / p.gain)
    put("L200_Ngm_effective_mS", ngm_l * 1e3, f"{ngm_l * 1e3:.0f} mS", "1 / (w - R_F/G), from the simulated weight", "mS")
    put("H_Ngm_effective_mS", 1 / (w["H100"] - F.CASES["H100"].rf / F.CASES["H100"].gain) * 1e3,
        f"{1 / (w['H100'] - F.CASES['H100'].rf / F.CASES['H100'].gain) * 1e3:.1f} mS", "1 / (w - R_F/G), H100", "mS")
    # the trim: DAC +/-10 V through 50 kohm (H; 100 kohm before 22 November 2026, whose range covered H's
    # Monte Carlo offset at a gain of 100 only to 1.1 times its rms) and 10 kohm (L), 12 bits
    for k, r_trim in (("H100", 50e3), ("H10", 50e3), ("L200", 10e3)):
        di = 10.0 / r_trim
        dv = di * w[k]
        step = 2 * dv / 2 ** 12
        i_n = math.sqrt(4 * KT / r_trim)
        e_n = i_n * w[k]
        put(f"{k}_trim_range_mV", dv * 1e3, f"+/-{dv * 1e3:.1f} mV", f"{di * 1e6:g} uA x w", "mV")
        put(f"{k}_trim_step_uV", step * 1e6, f"{step * 1e6:.1f} uV", "2 dv / 2^12", "uV")
        put(f"{k}_trim_noise", [i_n * 1e12, e_n * 1e9], f"{i_n * 1e12:.2f} pA/rtHz -> {e_n * 1e9:.2g} nV/rtHz",
            "sqrt(4kT/R_trim); x w", "pA/rtHz, nV/rtHz")
        put(f"{k}_trim_range_over_MC_offset", dv / off[k], f"{dv / off[k]:.1f}", "range / the Monte Carlo's rms input offset",
            "")
        # the share of builds whose offset lies outside the range, for a Gaussian spread of that rms value
        # (two-sided: erfc(r / sqrt 2), r = range / rms)
        r = dv / off[k]
        put(f"{k}_trim_share_outside", math.erfc(r / math.sqrt(2)), f"{100 * math.erfc(r / math.sqrt(2)):.2g} %",
            "erfc(r / sqrt(2)), r = trim range / Monte Carlo rms input offset (Gaussian spread assumed)", "")
        # the DAC's own output noise enters through the same resistor as e_DAC / R_trim; it equals the
        # resistor's thermal current noise when e_DAC = sqrt(4kT R_trim)
        e_lim = math.sqrt(4 * KT * r_trim)
        put(f"{k}_trim_dac_noise_limit", e_lim * 1e9, f"{e_lim * 1e9:.0f} nV/rtHz",
            "sqrt(4kT R_trim): the DAC output noise that equals the trim resistor's thermal noise", "nV/rtHz")
    # the first choice for H, 100 kohm, for comparison
    r100 = 10.0 / 100e3 * w["H100"] / off["H100"]
    put("H100_trim_100k_range_over_MC_offset_and_share_outside", [r100, math.erfc(r100 / math.sqrt(2))],
        f"{r100:.1f}; {100 * math.erfc(r100 / math.sqrt(2)):.2g} %", "100 uA x w / rms offset; erfc(r / sqrt(2))", "")


def power() -> None:
    ls = load("large_signal.json")["H100"]["psrr"]
    sp = load("sink_power.json")["L200 | 6 V"]["psrr_L1000"]
    fr = ["100", "1000.0", "10000.0", "100000.0", "1000000.0", "10000000.0"]
    h = {r: [-ls[r][f] for f in fr] for r in ("VP", "VM")}
    lo = {r: [-sp[r][f] for f in fr] for r in ("VP", "VM")}
    low = h["VP"][:4] + h["VM"][:4]
    put("H_PSRR_to_100k_dB", [min(low), max(low)], f"{min(low):.0f}-{max(low):.0f} dB",
        "large_signal.json H100.psrr, both rails, 100 Hz-100 kHz", "dB")
    for i, lab in ((4, "1M"), (5, "10M")):
        put(f"H_PSRR_{lab}_dB", [h["VP"][i], h["VM"][i]], f"{h['VP'][i]:.0f} / {h['VM'][i]:.0f} dB (+15 / -15 V)",
            f"large_signal.json H100.psrr at {lab}Hz", "dB")
    diff = [lo[r][i] - h[r][i] for r in ("VP", "VM") for i in range(6)]
    put("L_minus_H_PSRR_dB", [min(diff), max(diff)], f"{min(diff):.0f}-{max(diff):.0f} dB",
        "sink_power.json 'L200 | 6 V'.psrr_L1000 minus large_signal.json H100.psrr, per rail, 100 Hz-10 MHz", "dB")
    for r, e, lab in (("VP", DS["LT3045_en10"], "+15 V, LT3045"), ("VM", DS["LT3094_en10"], "-15 V, LT3094")):
        ps = h[r][0]
        e_in = e * 10 ** (-ps / 20)
        put(f"reg_noise_at_input_{r}_pV", e_in * 1e12, f"{e_in * 1e12:.2f} pV/rtHz ({ps:.1f} dB)",
            f"70 nV/rtHz x 10^(-PSRR(100 Hz)/20), {lab}", "pV/rtHz")
    put("ripple_series_1MHz_dB", [DS["LT3045_psrr_1M"] + h["VP"][4], DS["LT3094_psrr_1M"] + h["VM"][4]],
        f"{DS['LT3045_psrr_1M'] + h['VP'][4]:.0f} dB (+15 V: 76 + {h['VP'][4]:.1f}), "
        f"{DS['LT3094_psrr_1M'] + h['VM'][4]:.0f} dB (-15 V: 74 + {h['VM'][4]:.1f})",
        "LT3045 Rev. D p. 3, LT3094 Rev. 0 p. 5, plus large_signal.json H100.psrr at 1 MHz", "dB")
    ce = load("chain_extras.json")["supply"]
    for k in ("L_1000", "L_1000_filters_on", "H_LN_1000", "H_LN_1000_filters_on"):
        put(f"supply_{k}_mA", [ce[k]["I_plus15"] * 1e3, ce[k]["I_minus15"] * 1e3],
            f"{ce[k]['I_plus15'] * 1e3:.0f} / {ce[k]['I_minus15'] * 1e3:.0f} mA",
            f"chain_extras.json supply.{k}.I_plus15 / I_minus15", "mA")
    put("L_drain_resistors_mA", ce["L_1000"]["I_RD_total"] * 1e3, f"{ce['L_1000']['I_RD_total'] * 1e3:.0f} mA",
        "chain_extras.json supply.L_1000.I_RD_total", "mA")
    pl = [ce[k][r][v] for k in ("L_1000", "L_1000_filters_on") for r in ("P_LT3045", "P_LT3094") for v in ("2 V", "3 V")]
    ph = [ce[k][r][v] for k in ("H_LN_1000", "H_LN_1000_filters_on") for r in ("P_LT3045", "P_LT3094") for v in ("2 V", "3 V")]
    put("P_reg_L_W", [min(pl), max(pl)], f"{min(pl):.2f}-{max(pl):.2f} W", "chain_extras.json supply.L_1000(_filters_on).P_LT30xx", "W")
    put("P_reg_H_W", [min(ph), max(ph)], f"{min(ph):.2f}-{max(ph):.2f} W", "chain_extras.json supply.H_LN_1000(_filters_on)", "W")
    dt = [max(pl) * t for t in DS["theta_ja"]]
    put("reg_junction_rise_K", dt, f"{dt[0]:.0f}-{dt[1]:.0f} K", "P_max x theta_JA, 33 and 35 C/W (LT3094 Rev. 0 Table 4 p. 28; "
        "LT3045 Rev. D Table 4 p. 22)", "K")
    v = DS["I_SET"] * R_SET
    put("LT3045_Vout", [v, v * (1 + DS["I_SET_tol"])], f"{v:.1f} V nominal, {v * (1 + DS['I_SET_tol']):.2f} V at +1 %",
        "I_SET R_SET; LT3045 Rev. D p. 1 (100 uA +/-1 %, output to 15 V)", "V")


def one_over_f() -> None:
    z = np.load(R / "curves_noise.npz")
    for k in ("H100", "H10", "L200"):
        f = z[f"{k}_f"]
        for f0, lab in ((10.0, "10Hz"), (1.0, "1Hz")):
            e = at(f, z[f"{k}_total"], f0)
            op = at(f, z[f"{k}_g_loop op amps"], f0)
            jf = at(f, z[f"{k}_g_input JFETs"], f0)
            pr = math.sqrt(e * e - op * op)
            put(f"{k}_{lab}", dict(total=e * 1e9, op_amps=op * 1e9, jfets=jf * 1e9, without_op_amps=pr * 1e9),
                f"{e * 1e9:.2f} -> {pr * 1e9:.2f} nV/rtHz (op amps {op * 1e9:.2f}, JFETs {jf * 1e9:.2f})",
                f"curves_noise.npz {k}_total, _g_loop op amps, _g_input JFETs at {f0:g} Hz; sqrt(e^2 - e_op^2)", "nV/rtHz")
    put("JFE150_over_JFE2140_C", DS["JFE150_ciss"] / DS["JFE2140_ciss"], f"{DS['JFE150_ciss'] / DS['JFE2140_ciss']:.1f}",
        "24 pF / 13 pF (SLPS732B, SLPS730B Sec. 6.5 p. 5)", "")
    put("THS4021_datasheet", [DS["THS4021_gbw"], DS["THS4021_en"], DS["THS4021_en_dgn"]], "2 GHz, 1.2 nV/rtHz (1.5 in DGN)",
        "SLOS265F p. 1; Sec. 5.7 p. 8 (DGN)", "Hz, V/rtHz")
    put("OPA2810", [*DS["OPA2810_vs"], DS["OPA2810_gbw"]], "4.75-27 V, 70 MHz", "SBOS789C p. 1", "V, Hz")
    put("OPA1612", [DS["OPA1612_bw"], DS["OPA1612_en"]], "40 MHz, 1.1 nV/rtHz", "SBOS450C p. 1", "Hz, V/rtHz")


def method() -> None:
    ls = load("large_signal.json")["H100"]["thd"]
    grid = sorted({(r["f0"], r["vout_pp"]) for r in ls})
    f10 = max(f for f, v in grid if v == 10)
    f1 = max(f for f, v in grid if v == 1)
    put("THD_grid", [f1, f10], f"1 Vpp to {f1 / 1e6:g} MHz, 10 Vpp to {f10 / 1e6:g} MHz", "large_signal.json H100.thd (f0, vout_pp)", "Hz")
    # the pitfall of Section 5.1: the two wrong operating points reproduced by op_pitfall.py
    op = load("op_pitfall.json")
    nd = op["R_F route, gain 30, noise deck"]
    put("pitfall_noise_without_nodeset", op["R_F route, gain 30, noise at 10 kHz without .nodeset (nV/rtHz)"],
        f"{op['R_F route, gain 30, noise at 10 kHz without .nodeset (nV/rtHz)']:.1f} nV/rtHz",
        "op_pitfall.json 'R_F route, gain 30, noise at 10 kHz without .nodeset (nV/rtHz)'", "nV/rtHz")
    put("pitfall_kcl_at_bootstrap_node", [nd["kcl_residual_at_b"], nd["values"]["@rupa[i]"]],
        f"{nd['kcl_residual_at_b'] * 1e3:.2f} mA of R_UP's {nd['values']['@rupa[i]'] * 1e3:.2f} mA",
        "op_pitfall.json noise deck: kcl_residual_at_b, @rupa[i]", "A")
    js = op["JFE150 sink, gain 100"]
    put("pitfall_JFE150_sink", [js["v_sa"], js["f3db"], js["f3db_adopted"]],
        f"source node {js['v_sa']:.2f} V; -3 dB {js['f3db'] / 1e6:.0f} MHz instead of {js['f3db_adopted'] / 1e6:.1f} MHz",
        "op_pitfall.json 'JFE150 sink, gain 100' (v_sa, f3db, f3db_adopted)", "")


def vendor_models() -> None:
    md = load("model_defects.json")
    on = load("opamp_noise_check.json")
    j, o = md["jfet"], md["opamp"]
    a = j["JFE2140 1/f"]
    put("JFE2140_card_10Hz", [a["e_10Hz_card_ngspice"] * 1e9, a["e_10Hz_eq1_with_card_white"] * 1e9],
        f"{a['e_10Hz_card_ngspice'] * 1e9:.2f} (ngspice), {a['e_10Hz_eq1_with_card_white'] * 1e9:.2f} (Eq. (1))",
        "model_defects.json jfet.JFE2140 1/f", "nV/rtHz")
    put("JFE2140_1f_power_ratio", a["one_over_f_power_ratio_datasheet_to_card"], f"{a['one_over_f_power_ratio_datasheet_to_card']:.1f}",
        "model_defects.json", "")
    put("JFE2140_KF_ratio_JFE150", j["TI process argument"]["kf_card_ratio_JFE150_to_JFE2140"],
        f"{j['TI process argument']['kf_card_ratio_JFE150_to_JFE2140']:.2f}", "3.25e-18 / 0.2e-18", "")
    c = j["JFE2140 capacitances"]
    put("JFE2140_C_ratios", [c["ratio_ciss"], c["ratio_crss"]], f"{c['ratio_ciss']:.2f}x, {c['ratio_crss']:.2f}x", "model_defects.json", "")
    b = j["JFE150 1/f"]
    put("JFE150_KF_percent", b["kf_difference_percent"], f"+{b['kf_difference_percent']:.1f} %", "calibrated / card - 1", "%")
    put("JFE150_card_10Hz", b["e_10Hz_card_with_calibrated_white"] * 1e9, f"{b['e_10Hz_card_with_calibrated_white'] * 1e9:.2f} nV/rtHz",
        "model_defects.json (card KF, calibrated white)", "nV/rtHz")
    c = j["JFE150 capacitances"]
    put("JFE150_C_ratios", [c["ratio_ciss"], c["ratio_crss"]], f"{c['ratio_ciss']:.2f}x, {c['ratio_crss']:.2f}x", "model_defects.json", "")
    b = j["LSBF862 1/f"]
    put("LSBF862_card_10Hz", [b["e_1f_10Hz_eq1"] * 1e9, b["e_10Hz_card_ngspice"] * 1e9],
        f"{b['e_1f_10Hz_eq1'] * 1e9:.1f} (Eq. (1)), {b['e_10Hz_card_ngspice'] * 1e9:.1f} (ngspice)", "model_defects.json", "nV/rtHz")
    put("LSBF862_1f_power_ratio", b["one_over_f_power_ratio_card_to_datasheet"], f"{b['one_over_f_power_ratio_card_to_datasheet']:.0f}",
        "model_defects.json", "")
    b = j["2N5564 KF"]
    put("2N5564_corner_GHz", b["corner_eq1_with_calibrated_white"] / 1e9, f"{b['corner_eq1_with_calibrated_white'] / 1e9:.2f} GHz",
        "model_defects.json (Eq. (1), calibrated white 1.28 nV/rtHz)", "GHz")
    put("2N5564_1MHz_nV", b["e_1f_eq1"]["1e+06"] * 1e9, f"{b['e_1f_eq1']['1e+06'] * 1e9:.0f} nV/rtHz", "Eq. (1) at 1 MHz", "nV/rtHz")
    b = j["J310"]
    put("J310_10kHz", [b["e_1f_10kHz_eq1"] * 1e6, b["e_10kHz_card_ngspice"] * 1e6, b["sink_current"] * 1e3],
        f"{b['e_1f_10kHz_eq1'] * 1e6:.2f} uV/rtHz (Eq. (1)), {b['e_10kHz_card_ngspice'] * 1e6:.2f} (ngspice, "
        f"{b['sink_current'] * 1e3:.0f} mA)", "model_defects.json jfet.J310", "uV/rtHz")
    put("J310_sink_H10_10kHz_nV", b["sink_run"]["en"]["10000.0"] * 1e9, f"{b['sink_run']['en']['10000.0'] * 1e9:.1f} nV/rtHz",
        "model_defects.json jfet.J310.sink_run.en.10000.0", "nV/rtHz")
    b = j["LSK389"]["LSK389B"]
    w_on, w_off = b["with_nlev_gdsnoi"]["en_white_100k"], b["without_nlev_gdsnoi"]["en_white_100k"]
    put("LSK389B_white", [w_on * 1e9, w_off * 1e9], f"{w_on * 1e9:.2f} with, {w_off * 1e9:.2f} without",
        "model_defects.json jfet.LSK389.LSK389B (2 mA, 10 V); LTspice 26.1.1.0 standard.jft", "nV/rtHz")
    e_ds = j["LSK389"]["datasheet"]["en_1k"]
    put("LSK389B_over_datasheet", [w_on / e_ds, w_off / e_ds], f"{w_on / e_ds:.2f}x with, {w_off / e_ds:.2f}x without",
        "white / 1.6 nV/rtHz (LSK389 Doc 201122 Rev A27, p. 2, at 1 kHz)", "")
    lib = md["ltspice_library"]
    sha = lib["sha256"]
    jlog = [e for e in lib["changelog_jfet_entries"] if "Linear Systems" in e][0]
    put("LTspice_library", [lib["ltspice_version"], lib["modified_utc"][:10], sha, jlog],
        f"LTspice {lib['ltspice_version']}, standard.jft dated {lib['modified_utc'][:10]}, SHA-256 {sha[:8]}...{sha[-4:]}; "
        f"change log: \"{jlog}\"", "model_defects.json ltspice_library", "")
    # op amps
    for p in ("THS4021", "THS4031", "THS3091", "LM7171"):
        t = on["table7"][p]
        put(f"{p}_model_10Hz", [t["e_n_10"] * 1e9, t["i_n_10"] * 1e12],
            f"{t['e_n_10'] * 1e9:.1f} nV/rtHz, {t['i_n_10'] * 1e12:.0f} pA/rtHz", f"opamp_noise_check.json table7.{p}", "nV, pA")
        r = o[p]
        put(f"{p}_ratios", [r["ratio_e_10"], r["ratio_i_10"], r["ratio_e_white"], r["ratio_i_white"]],
            ", ".join("-" if x is None else f"{x:.2f}" for x in (r["ratio_e_10"], r["ratio_i_10"], r["ratio_e_white"], r["ratio_i_white"])),
            f"model_defects.json opamp.{p}: e_10, i_10, e_white, i_white", "")
    hd = o["THS4031 HD3"]
    put("THS4031_HD3", [hd["hd3_dBc_1Vpp"], hd["excess_unscaled_dB"], hd["excess_scaled_dB"]],
        f"{hd['hd3_dBc_1Vpp']:.0f} dBc at 1 Vpp; {hd['excess_unscaled_dB']:.0f} dB above the curve as read, "
        f"{hd['excess_scaled_dB']:.0f} dB after scaling to 2 Vpp ({hd['hd3_dBc_scaled_to_2Vpp']:.1f} dBc)",
        "model_defects.json opamp.THS4031 HD3 (SLOS224L Fig. 5-15, p. 12; -50 dBc at 2 Vpp)", "dB")
    put("THS3091_white_in_model_pA", on["table7"]["THS3091"]["i_n_white_kf0"] * 1e12,
        f"{on['table7']['THS3091']['i_n_white_kf0'] * 1e12:.1f} pA/rtHz", "opamp_noise_check.json table7.THS3091.i_n_white_kf0", "pA/rtHz")
    put("LM7171_white_en_model_nV", on["table7"]["LM7171"]["e_n_white_kf0"] * 1e9,
        f"{on['table7']['LM7171']['e_n_white_kf0'] * 1e9:.1f} nV/rtHz", "opamp_noise_check.json table7.LM7171", "nV/rtHz")
    # current-noise 1/f corners, f_c = f_0 (i_n(f_0)/i_n,w)^2, f_0 = 10 Hz
    for p in ("THS4021", "THS4031"):
        t = on["table7"][p]
        fc_m = 10 * (t["i_n_10"] / t["i_n_white_kf0"]) ** 2
        fc_d = 10 * (DS[f"{p}_in10"] / DS[f"{p}_in"]) ** 2
        put(f"{p}_in_corner", [fc_m, fc_d], f"{fc_m / 1e6:.2f} MHz (model, own white) against {fc_d / 1e3:.2f} kHz (data sheet)",
            "10 Hz x (i_n(10 Hz) / i_n,w)^2; data sheet 18.6 pA/rtHz at 10 Hz (Figs., read from the pixels) and "
            "2.3 pA/rtHz (Sec. 5.6 p. 6)", "Hz")
        put(f"{p}_white_in", [t["i_n_white_kf0"] * 1e12, DS[f"{p}_in"] * 1e12, t["i_n_white_kf0"] / DS[f"{p}_in"]],
            f"{t['i_n_white_kf0'] * 1e12:.2f} pA/rtHz against {DS[f'{p}_in'] * 1e12:.1f} ({t['i_n_white_kf0'] / DS[f'{p}_in']:.2f}x)",
            f"opamp_noise_check.json table7.{p}.i_n_white_kf0; SLOS265F / SLOS224L Sec. 5.6 p. 6", "pA/rtHz")
    # the effect of the THS4021's low white current noise on the front ends (Eq. (9), 10 kHz)
    z = np.load(R / "curves_noise.npz")
    i_m = on["table7"]["THS4021"]["i_n_white_kf0"]
    i_d = DS["THS4021_in"]
    for k, rd in (("H100", 600.0), ("H10", 600.0), ("L200", 100.0)):
        f = z[f"{k}_f"]
        w = at(f, z[f"{k}_g_drain-side R_D"], 1e4) / (math.sqrt(2) * math.sqrt(4 * KT / rd))
        e = at(f, z[f"{k}_total"], 1e4)
        e2 = math.sqrt(e * e + 2 * w * w * (i_d ** 2 - i_m ** 2))
        put(f"{k}_effect_white_in", [e * 1e9, e2 * 1e9, (e2 / e - 1) * 100],
            f"{e * 1e9:.3f} -> {e2 * 1e9:.3f} nV/rtHz (+{(e2 / e - 1) * 100:.2f} %)",
            "sqrt(e^2 + 2 w^2 (2.3^2 - 1.18^2) pA^2), w from the R_D group at 10 kHz", "nV/rtHz, %")
    hf = on["H100 front end, published THS4021"]
    put("H100_published_THS4021_10Hz", [hf["published"]["en"]["10"] * 1e9, hf["corrected"]["en"]["10"] * 1e9,
                                        hf["ratio_published_to_corrected"]["10"]],
        f"{hf['published']['en']['10'] * 1e9:.1f} against {hf['corrected']['en']['10'] * 1e9:.2f} nV/rtHz "
        f"(x{hf['ratio_published_to_corrected']['10']:.1f})", "opamp_noise_check.json 'H100 front end, published THS4021'", "nV/rtHz")
    ch = on["chain, published THS3091"]
    put("chain_published_THS3091_1Hz", [ch["H_LN_1"]["ratio_published_to_corrected"]["1"],
                                        ch["H_LN_10"]["ratio_published_to_corrected"]["1"]],
        f"x{ch['H_LN_1']['ratio_published_to_corrected']['1']:.2f} at a total gain of 1, "
        f"x{ch['H_LN_10']['ratio_published_to_corrected']['1']:.2f} at 10",
        "opamp_noise_check.json 'chain, published THS3091' (1 Hz)", "")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(SCRIPTS))
    input_admittance()
    protection()
    chain_stages()
    off = offsets()
    trim(off)
    power()
    one_over_f()
    method()
    vendor_models()
    put("datasheet_constants", {k: v for k, v in DS.items()}, "-", "see the comments in numbers_s4b_5.py (DS)", "SI")
    (R / "numbers_s4b_5.json").write_text(json.dumps(OUT, indent=1), encoding="utf-8", newline="\n")
    print("quantity | value | source")
    for k, v in OUT.items():
        if k != "datasheet_constants":
            print(f"{k} | {v['text']} | {v['source']}")


if __name__ == "__main__":
    main()
