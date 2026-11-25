"""Derived numbers of Section 3.5 of the note (bipolar input stages and 1/f noise) and of its Table 5, computed
from archived results and data-sheet constants only (no simulation).  Writes ../sim/results/numbers_s3_5.json and
prints "quantity | value | source".

Inputs (../sim/results/): bipolar_inputs.json (the input-stage testbench), bipolar_inputs.npz, bipolar_fe.json and
bipolar_fe.npz (the bipolar front end B against L200; bipolar_inputs.py), bipolar_comp_search.json,
curves_noise.npz (L200's noise groups).

Formulas:
  (1) white noise of one device (Leach, Proc. IEEE 82(10), 1994, Eq. (43)), r_bb' = e_n^2 / 4kT - r_e / 2 with
      r_e = kT / q I_C; T = 298.15 K for a data sheet's 25 C, 300.15 K for the simulator
  (2) an array of N per side, differential: e_n x sqrt(2 / N)
  (3) i_n from a total-noise curve with a source R_S:  i_n = sqrt(e_tot^2 - 4kT R_S - e_n^2) / R_S, against the
      base current's shot noise sqrt(2 q I_C / h_FE)
  (4) corner of a current noise from a plotted level i(f) and its flat level i_w:  f_c = f ((i / i_w)^2 - 1)
  (5) 1/f noise of a JFET from a 0.1-10 Hz peak-to-peak value: rms = p-p / 6.6, and with e^2 = e_w^2 + K / f,
      rms^2 = e_w^2 x 9.9 Hz + K ln(100), so K = (rms^2 - 9.9 e_w^2) / ln 100; e(1 Hz) = sqrt(e_w^2 + K)
  (6) the base current's noise in the front end: it flows through R_G / 2 as well as r_bb' / N, coherently,
      e^2 = e_tb^2 + 2 i_side^2 [(r / N + R_G / 2)^2 - (r / N)^2], r = RB + RE, i_side the testbench's i_n
  (7) crossover (bipolar_inputs.crossover) and noise figure at 290 K (bipolar_inputs.nf_db) of the fitted two-ports
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np

import bipolar_inputs as B
import spice

R = spice.RESULTS
K_B, Q = 1.380649e-23, 1.602176634e-19
T25, TSIM = 298.15, 300.15

# --- data-sheet constants (refs/datasheets/bjt/, refs/datasheets/jfet/TI/), typical values -------------------------
SSM2212_EN = dict(table_10=1.6e-9, table_1k=0.85e-9, curve_1k=0.76e-9, curve_10=0.74e-9, curve_1=1.04e-9,
                  curve_2=0.59e-9, curve_0p1=13.2e-9, pp_0p1_10=0.4e-6)
# SSM2212 Rev C Table 1 (p. 3) and Fig. 4 (p. 6; the MAT12's Fig. 3), 1 mA; the curve read at 480 dpi by eye
SSM2212_FIG5 = {1e-3: 83.2e-9, 0.5e-3: 74.7e-9, 0.2e-3: 55.6e-9, 0.1e-3: 46.5e-9}
# Fig. 5 (p. 6; MAT12 Fig. 4): total noise at 1 kHz with R_S = 100 kOhm, read at 480 dpi by eye
SSM2212_HFE = 605.0          # Table 1, 1 mA, typical
OTHER_CORNERS = {
    # part: (plotted i_n at 10 Hz, plotted flat level, pA, at 1 mA; source)
    "2SB737": (3.5, 0.8, "Rohm data book p. 188, Fig. 15"),
    "LM394": (7.5, 0.6, "SNLS385A p. 7, base current noise vs frequency"),
}
MAT03_TPC10 = (235e-9, 165.0)   # MAT03 Rev C TPC 10 (p. 5): total noise at 1 kHz, 1 mA, R_S = 100 kOhm; h_FE at 1 mA
STATED_CORNERS = {"OP37": (140.0, "OP37 Rev B p. 7, TPC 8"), "LT1028": (250.0, "LT1028 Rev D p. 11 and p. 6")}
JFE150 = dict(w=0.8e-9, at10=1.8e-9, pp=0.13e-6, fig_1hz=14.0e-9)   # SLPS732B p. 5 (5 mA, 5 V) and Fig. 6-9 (p. 7)
L_N = 12

ROWS: list[tuple[str, str, str]] = []


def put(out: dict, key: str, value, source: str, fmt: str = "{:.4g}"):
    out[key] = dict(value=value, source=source)
    if isinstance(value, (list, tuple)):
        txt = ", ".join(fmt.format(v) if isinstance(v, (int, float)) else str(v) for v in value)
    else:
        txt = fmt.format(value) if isinstance(value, (int, float)) else str(value)
    ROWS.append((key, txt, source))


def rbb(e: float, i_c: float, t: float = T25) -> float:
    """(1)"""
    return e ** 2 / (4 * K_B * t) - K_B * t / (Q * i_c) / 2


def section(out: dict) -> None:
    tb = json.loads((R / "bipolar_inputs.json").read_text(encoding="utf-8"))
    fe = json.loads((R / "bipolar_fe.json").read_text(encoding="utf-8"))
    d = np.load(R / "bipolar_fe.npz")
    cn = np.load(R / "curves_noise.npz")

    # calibration
    put(out, "rbb_from_table_1k_ohm", rbb(SSM2212_EN["table_1k"], 1e-3), "(1) 0.85 nV, 1 mA, 25 C")
    put(out, "rbb_from_curve_1k_ohm", rbb(SSM2212_EN["curve_1k"], 1e-3), "(1) 0.76 nV, 1 mA, 25 C")
    c = B.SSM2212
    e_card = math.sqrt(4 * K_B * T25 * (c["rb"] + c["re"]) + 2 * K_B * T25 * (K_B * T25 / Q) / 1e-3)
    put(out, "en_card_1mA_nV", e_card * 1e9, "(1) inverted: RB 28 + RE 0.3 ohm, 1 mA, 25 C")
    shot = math.sqrt(2 * Q * 1e-3 / SSM2212_HFE)
    rows = []
    for ic, tot in sorted(SSM2212_FIG5.items(), reverse=True):
        i_n = math.sqrt(tot ** 2 - 4 * K_B * T25 * 1e5 - SSM2212_EN["curve_1k"] ** 2) / 1e5
        rows.append((ic * 1e3, i_n * 1e12, (i_n / math.sqrt(2 * Q * ic / SSM2212_HFE)) ** 2))
    put(out, "ssm2212_fig5_in_1kHz", rows, "(3) Fig. 5 at 1, 0.5, 0.2, 0.1 mA: (I_C mA, i_n pA, i_n^2 / 2qI_B)")
    put(out, "ssm2212_shot_1mA_pA", shot * 1e12, "sqrt(2 q 1 mA / 605)")
    put(out, "ssm2212_fig5_power_ratio_range", [min(r[2] for r in rows), max(r[2] for r in rows)], "(3)")
    # Table 5's derived r_bb' (1): LS3250 0.7 nV at 2 mA (Doc 201128 p. 2); LS310-LS313 1.3 nV at 1 mA and 1.8 nV at
    # 0.1 mA, 1 kHz (Doc 201121 p. 2); MAT14 1.8 nV at 1 mA, 1 kHz (Rev A p. 3)
    put(out, "rbb_LS3250_ohm", rbb(0.7e-9, 2e-3), "(1) 0.7 nV, 2 mA")
    put(out, "rbb_LS310_ohm", [rbb(1.8e-9, 0.1e-3), rbb(1.3e-9, 1e-3)], "(1) 1.8 nV at 0.1 mA, 1.3 nV at 1 mA")
    put(out, "rbb_MAT14_ohm", rbb(1.8e-9, 1e-3), "(1) 1.8 nV, 1 mA")
    # the base-current noise that the table's 1.6 nV/rtHz at 10 Hz would need through RB + RE, at 1 kHz as 1/f
    i_f10 = math.sqrt(SSM2212_EN["table_10"] ** 2 - SSM2212_EN["table_1k"] ** 2) / (c["rb"] + c["re"])
    put(out, "table_10Hz_needs_in_1kHz_over_shot", i_f10 / math.sqrt(100) / shot, "sqrt(1.6^2 - 0.85^2) / 28.3 ohm, / 10")
    # the corners' rise with current: 2SB737 Fig. 15 at 0.1 and 10 mA (1.0 and 0.28 pA; 16 and 2.4 pA), LM394 at
    # 10 uA and 10 mA (0.5 and 0.055 pA; 35 and 1.8 pA): A_F = 1 + d log f_c / d log I
    fc_2sb = [10 * ((1.0 / 0.28) ** 2 - 1), 10 * ((16 / 2.4) ** 2 - 1)]
    fc_lm = [10 * ((0.5 / 0.055) ** 2 - 1), 10 * ((35 / 1.8) ** 2 - 1)]
    put(out, "af_2SB737", 1 + math.log10(fc_2sb[1] / fc_2sb[0]) / 2, f"corners {fc_2sb[0]:.0f} and {fc_2sb[1]:.0f} Hz, 0.1 and 10 mA")
    put(out, "af_LM394", 1 + math.log10(fc_lm[1] / fc_lm[0]) / 3, f"corners {fc_lm[0]:.0f} and {fc_lm[1]:.0f} Hz, 10 uA and 10 mA")
    corners = {}
    for part, (i10, iw, src) in OTHER_CORNERS.items():
        corners[part] = 10 * ((i10 / iw) ** 2 - 1)
        put(out, f"corner_{part}_1mA_Hz", corners[part], f"(4) {src}: {i10} and {iw} pA")
    i_pair = math.sqrt(MAT03_TPC10[0] ** 2 - 2 * 4 * K_B * T25 * 1e5) / math.sqrt(2) / 1e5
    i_one = math.sqrt(MAT03_TPC10[0] ** 2 - 4 * K_B * T25 * 1e5) / 1e5
    s3 = math.sqrt(2 * Q * 1e-3 / MAT03_TPC10[1])
    put(out, "corner_MAT03_1mA_Hz", [1e3 * ((i_pair / s3) ** 2 - 1), 1e3 * ((i_one / s3) ** 2 - 1)],
        "(3), (4) TPC 10, 235 nV at 1 mA, read as a pair (two R_S) and as one device")
    for part, (fc, src) in STATED_CORNERS.items():
        put(out, f"corner_{part}_Hz", fc, src)
    put(out, "kf_central", float(B.ssm2212_card("x").split("KF=")[1].split()[0]), "KF = 2 q f_c0 I_B0^(1 - AF), f_c0 200 Hz")

    # JFE150's 1 Hz noise, three readings, per device and for L's array
    k_tab = (JFE150["at10"] ** 2 - JFE150["w"] ** 2) * 10
    rms = JFE150["pp"] / 6.6
    k_pp = (rms ** 2 - 9.9 * JFE150["w"] ** 2) / math.log(100)
    e1 = [math.sqrt(JFE150["w"] ** 2 + k_tab), math.sqrt(JFE150["w"] ** 2 + k_pp), JFE150["fig_1hz"]]
    put(out, "jfe150_1Hz_per_device_nV", [v * 1e9 for v in e1], "(5) table (1/f from 10 Hz), 0.13 uV p-p, Fig. 6-9")
    put(out, "jfe150_1Hz_L_array_nV", [v * math.sqrt(2 / L_N) * 1e9 for v in e1], "(2) N = 12")
    # the SSM2212's own curve over 0.1-10 Hz against its 0.1-10 Hz specification
    f = np.logspace(-1, 1, 400)
    e_curve = np.interp(np.log10(f), np.log10([0.1, 0.5, 1, 2, 10]), np.array([13.2, 2.9, 1.04, 0.59, 0.74]) * 1e-9)
    pp_curve = 6.6 * math.sqrt(np.trapezoid(e_curve ** 2, f))
    put(out, "ssm2212_curve_pp_0p1_10_uV", pp_curve * 1e6, "(5) its Fig. 4 read at 0.1, 0.5, 1, 2, 10 Hz, integrated")
    put(out, "ssm2212_pp_spec_over_curve", SSM2212_EN["pp_0p1_10"] / pp_curve, "0.4 uV p-p / the curve's")

    # testbench
    chk = tb["check_JFE150_L_against_L200"]
    put(out, "tb_check_L_ratio_range", [min(v["ratio"] for v in chk.values()), max(v["ratio"] for v in chk.values())],
        "bipolar_inputs.json, 1 Hz to 100 kHz")
    an = [tb[k]["analytic_check"] for k in tb if isinstance(tb[k], dict) and "analytic_check" in tb[k]]
    put(out, "tb_analytic_en_ratio_range", [min(a["e_n_ratio"] for a in an), max(a["e_n_ratio"] for a in an)],
        "Leach (43) at 100 kHz")
    put(out, "tb_analytic_in_ratio_range", [min(a["i_n_ratio"] for a in an), max(a["i_n_ratio"] for a in an)],
        "Leach (44) at 100 kHz")
    for k in ("JFE150_L", "SSM2212_12", "SSM2212_24", "SSM2212_48", "SSM2212_24_fc30", "SSM2212_24_fc1k",
              "SSM2212L_24"):
        a = tb[k]["at"]
        put(out, f"tb_{k}_en_nV", [a[f]["e_n"] * 1e9 for f in ("1", "10", "1000", "100000")], "1 Hz, 10 Hz, 1 kHz, 100 kHz")
        put(out, f"tb_{k}_in_pA", [a[f]["i_n"] * 1e12 for f in ("1", "10", "1000", "100000")], "1 Hz, 10 Hz, 1 kHz, 100 kHz")
    fc = tb["flicker_check"]
    put(out, "flicker_check_max_dev", [fc["max_dev_e_n"], fc["max_dev_i_n"]], "one NPN against Leach (43)-(44) with 1/f")
    # the 1/f noise of the arrays' base currents in e_n, through (RB + RE) / N: e^2 = e_w^2 + 2 (i_1^2 - i_w^2)(r / N)^2
    a24 = tb["SSM2212_24"]["at"]
    r_n = (B.SSM2212["rb"] + B.SSM2212["re"]) / 24
    e1 = math.sqrt(a24["100000"]["e_n"] ** 2 + 2 * (a24["1"]["i_n"] ** 2 - a24["100000"]["i_n"] ** 2) * r_n ** 2)
    put(out, "tb_24_1Hz_en_placement_check_nV", [e1 * 1e9, a24["1"]["e_n"] * 1e9], "formula, simulated")
    w_l = tb["JFE150_L"]["at"]["100000"]["e_n"]
    put(out, "tb_white_reduction_pct", [100 * (1 - tb[k]["at"]["100000"]["e_n"] / w_l) for k in
                                        ("SSM2212_12", "SSM2212_24", "SSM2212_48")], "12, 24, 48 per side against L")
    put(out, "tb_white_en_ratio_L_over_24", tb["JFE150_L"]["at"]["100000"]["e_n"] / tb["SSM2212_24"]["at"]["100000"]["e_n"],
        "100 kHz")
    put(out, "tb_1Hz_en_ratio_L_over_24", tb["JFE150_L"]["at"]["1"]["e_n"] / tb["SSM2212_24"]["at"]["1"]["e_n"], "1 Hz")
    op = tb["SSM2212_24"]["op"]
    put(out, "b_device_ic_mA_ib_uA_beta_vbe", [op["ic"] * 1e3, op["ib"] * 1e6, op["beta"], op["vbe"]], "testbench op")
    put(out, "b_bias_current_per_input_uA", 24 * op["ib"] * 1e6, "24 I_B")
    put(out, "b_offset_10ohm_mV", 24 * op["ib"] * 10 * 1e3, "24 I_B x 10 ohm")
    put(out, "b_gm_side_S_vs_L", [24 * op["gm"], 12 * 0.025691], "24 g_m (testbench op) and 12 x 25.69 mS (JFE150)")

    # the front end B
    put(out, "b_comp_pF", [fe["b_comp"]["ci"] * 1e12, fe["b_comp"]["cx"] * 1e12, fe["b_comp"]["cnode"] * 1e12], "B_COMP")
    m = fe["b_margins"]
    put(out, "b_margins", [m["dm"]["pm"], m["dm"]["gm_db"], m["cm"]["pm"], m["cm"]["gm_db"]], "DM PM, GM; CM PM, GM")
    put(out, "b_f3db_MHz_peak_dB_gain", [fe["b_f3db"] / 1e6, fe["b_peak_db"], fe["b_gain_1k"]], "check_ac")
    bop = fe["b_op"]
    put(out, "b_fe_op", [bop["v(sa)"], bop["v(da1)"] - bop["v(sa)"], bop["v(ca)"], bop["v(oa)"] - bop["v(sa)"],
                         bop["@qja1[ic]"] * 1e3], "v(sa), V_CE, v(ca), v(oa) - v(sa), I_C (mA)")
    # the cascodes' role: each transistor's collector-base capacitance at B's V_CB (the card's CJC, VJC, MJC;
    # Gummel-Poon depletion capacitance), which the bootstrapped cascode keeps from the input, and their noise
    v_cb = bop["v(da1)"] - bop["v(ga)"]
    c_mu = c["cjc"] / (1 + v_cb / c["vjc"]) ** c["mjc"]
    put(out, "b_vcb_cmu_pF_x24_pF", [v_cb, c_mu * 1e12, 24 * c_mu * 1e12], "V_CB (V), C_mu per device, 24 C_mu")
    put(out, "b_cascode_noise_pV", [fe["b_noise"][f0]["groups"]["cascodes"] * 1e12 for f0 in ("1", "1000")],
        "the cascodes' group at 1 Hz and 1 kHz")
    bn = fe["b_noise"]
    fl = cn["L200_f"]

    def lat(key, f0):
        return float(cn[key][int(np.argmin(np.abs(np.log10(fl) - math.log10(f0))))])

    for f0 in ("1", "10", "100", "1000", "100000", "1e+06", "1e+07"):
        put(out, f"b_vs_L_total_{f0}_nV", [bn[f0]["total"] * 1e9, lat("L200_total", float(f0)) * 1e9], "B, L200")
    for f0 in ("1", "1000"):
        g = bn[f0]["groups"]
        put(out, f"b_groups_{f0}_nV", [g["input JFETs"] * 1e9, g["R_G"] * 1e9, g["loop op amps"] * 1e9,
                                       g["drain-side R_D"] * 1e9, g["current sinks"] * 1e9],
            "inputs, R_G, op amps, R_D, sinks")
        put(out, f"L_groups_{f0}_nV", [lat(f"L200_g_{k}", float(f0)) * 1e9 for k in
                                       ("input JFETs", "R_G", "loop op amps", "drain-side R_D", "current sinks")],
            "curves_noise.npz")
    put(out, "opamp_reduction_1kHz", lat("L200_g_loop op amps", 1e3) / bn["1000"]["groups"]["loop op amps"], "L / B")
    r_over_n = (B.SSM2212["rb"] + B.SSM2212["re"]) / 24
    i_side = tb["SSM2212_24"]["at"]["1"]["i_n"]
    e_tb = tb["SSM2212_24"]["at"]["1"]["e_n"]
    e6 = math.sqrt(e_tb ** 2 + 2 * i_side ** 2 * ((r_over_n + 2.49 / 2) ** 2 - r_over_n ** 2))
    put(out, "b_devices_1Hz_eq6_nV", [e6 * 1e9, bn["1"]["groups"]["input JFETs"] * 1e9, e_tb * 1e9], "(6), simulated, testbench")

    # with a source
    f = d["f_L200"]
    j = {f0: int(np.argmin(np.abs(np.log10(f) - math.log10(f0)))) for f0 in (1, 10, 100, 1e3, 1e4, 1e5, 1e6)}
    for tag in ("B", "B_fc30", "B_fc1k"):
        x = B.crossover(d[f"coef_{tag}"], d["coef_L200"])
        put(out, f"crossover_{tag}_ohm", [float(x[j[f0]]) for f0 in j], "1, 10, 100 Hz, 1, 10, 100 kHz, 1 MHz")
    for rs in (1.0, 3.0, 10.0, 30.0, 100.0):
        put(out, f"nf_{rs:g}ohm_dB", [[float(B.nf_db(d[f"coef_{tag}"][:, j[f0]], rs)) for tag in
                                       ("L200", "B", "B_fc30", "B_fc1k")] for f0 in (1, 10, 1e3)],
            "per 1 Hz, 10 Hz, 1 kHz: L, B, B_fc30, B_fc1k")
    for rs in (1.0, 100.0):
        nf = {tag: [float(B.nf_db(d[f"coef_{tag}"][:, j[f0]], rs)) for f0 in (1, 10, 1e3)]
              for tag in ("L200", "B", "B_fc30", "B_fc1k")}
        put(out, f"nf_gain_B_over_L_{rs:g}ohm_dB", [[nf["L200"][i] - nf[t][i] for t in ("B", "B_fc30", "B_fc1k")]
                                                    for i in range(3)], "L - B (positive: B lower), 1 Hz, 10 Hz, 1 kHz")
    # B's minimum noise figure and its source resistance (Figure 8): R_opt = sqrt(S_e / S_i),
    # F_min = 1 + (2 sqrt(S_e S_i) + S_x) / 4 k T0, T0 = 290 K; and the fits' largest deviation from the runs
    for f0 in (1, 10, 1e3):
        se, sx, si = d["coef_B"][:, j[f0]]
        put(out, f"b_nfmin_{f0:g}Hz", [math.sqrt(se / si), 10 * math.log10(1 + (2 * math.sqrt(se * si) + sx) / (4 * K_B * 290.0))],
            "R_opt (ohm), NF_min (dB), corner 200 Hz")
    put(out, "fe_two_port_max_dev_db", max(v["two_port_max_dev_db"] for v in fe["sweep"].values()), "bipolar_fe.json sweep")
    # input impedance and sources
    for tag in ("L200", "B"):
        z = fe[f"zin_{tag}"]["dm"]
        put(out, f"zin_{tag}_dm", [[z[f0]["r_par"], z[f0]["c_eff"] * 1e12] for f0 in ("10", "1000", "1e+06", "1e+07")],
            "R_par (ohm), C (pF) at 10 Hz, 1 kHz, 1 MHz, 10 MHz")
        s = fe[f"sources_{tag}"]
        put(out, f"sources_{tag}", [[k, s[k]["peak_db"], s[k]["f_peak"] / 1e6] for k in s], "peak dB at MHz")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out: dict = {}
    section(out)
    (R / "numbers_s3_5.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    w = max(len(k) for k, _, _ in ROWS)
    print(f"{'quantity':{w}s} | value | source")
    for k, v, s in ROWS:
        print(f"{k:{w}s} | {v} | {s}")


if __name__ == "__main__":
    main()
