"""Derived numbers of the summary and Sections 1-3 of the note (lines 1-252), computed from archived
results and data-sheet constants only (no simulation).  Every number that the text derives
(a ratio, a difference, a crossover, a unit conversion, a single rounding) is computed here;
direct readouts of a results file are listed as well where the text quotes them, so that one table
holds the whole range.  Writes ../sim/results/numbers_s1_3.json and prints "quantity | value | source".

Inputs (../sim/results/): chain_noise.json, chain_ac.json, sr560_chain.json, sr560_frontend.json,
sr560_variants.json, noise_vs_source.json, osc_check.json, lv_option_range.json, zin_numbers.json, cmrr_mc.json,
large_signal.json, model_defects.json, noise_theory.json, jfet_calibration.json,
jfet_model_check.json, jfet_table3.json, curves_noise.npz; and jfet_data.JFETS (the survey values of
Table 3, each with its data-sheet page in ../refs/datasheets/jfet/survey_*.md).

Formulas (e: input noise density; f_3dB: -3 dB bandwidth; G: total gain):
  (1) quieter by           r = e_SR560(1 kHz, G 1000) / e_new(1 kHz, G 1000)          (H and L)
  (2) bandwidth ratio      r = f_3dB,new(G) / f_3dB,SR560(G) at the same G (H: 100, L: 1000);
                           against a specification: f_3dB,new / f_spec, f_spec = 1 MHz (SR560 manual
                           Rev. 3.1, printed p. 5) or 1.2 MHz typical (SR560 data sheet, p. 3)
  (3) NF 5307              r = e_5307 / e_new: e_5307 = 2.8 and 3.1 nV/rtHz (white, NF's plot, manual
                           Fig. 4.7, PDF p. 37, gain 100, read by eye; the reading of numbers_s6_7.py,
                           imported) against e_new white (100 kHz, G 1000); e_5307 = 4 nV/rtHz (typical,
                           1 kHz, gain 1000, NF specification sheet NF_5307_specifications_EN.pdf, also
                           from numbers_s6_7.py) against e_new(1 kHz, G 1000)
  (1)-(3) are evaluated twice: with the results files' values, and with the values the summary of
                           the note quotes (their single roundings, checked against the files: SR560
                           5.7, H 1.11 and L 0.43 nV/rtHz at 1 kHz, H 1.08 and L 0.42 white, f_3dB 14.85,
                           16.6 and 0.73 MHz); both give the same rounded ratio, and the text writes the
                           second
  (4) H/L crossover        for each frequency, R_x where e_H(R_s) = e_L(R_s): linear interpolation of
                           ln(e_H / e_L) in log10 R_s between the two grid points where it changes sign
                           (noise_vs_source.json, full chain at G 1000, source R_s on input A); also
                           where e_H / e_L = 1.01 and 0.99 (the band where the two differ by < 1 %)
  (5) Table 1 deviation    d = e_model(1 kHz) / e_manual - 1 for each of the 15 columns (manual:
                           SR560 manual printed p. 21, in sr560_chain.json 'manual'); count |d| <= 30 %
  (6) the JFETs' own capacitance per input   C = N C_iss (H: 2 x 13 pF, SLPS730B p. 5; L: 12 x 24 pF,
                           SLPS732B p. 5); Stahl PR-E3 with both channels connected: 2 x 16.4 pF
                           (data sheet v3.12, p. 5, "at either input"); H's bias current per input
                           N I_G, I_G about 1 pA per JFE2140 at its 3.9 V of V_DS (SLPS730B Fig. 6-6)
  (7) sigma of V_TO        (V_GS(off),max - V_GS(off),min) / 7 = (-0.9 - (-1.5)) V / 7 (JFE150,
                           SLPS732B p. 5), taking the data sheet's range as +-3.5 sigma (an assumption)
  (8) current sharing      Delta I / I = 2 Delta V_TO / (V_GS - V_TO) (square law; noise_theory.json)
  (9) one device against twelve: per side e_1 / sqrt(N), differential sqrt(2) e_1 / sqrt(N) (Eq. (2));
                           10 Hz figure of merit e_n(10 Hz) sqrt(C_iss) (JFE150 and IF3601, jfet_data)
  (10) ngspice channel noise check   e = sqrt(4kT (2 / (3 g_m) + R_S)) at the JFE150 card's operating
                           point (g_m from jfet_calibration.json, R_S = the card's RS, T = 300.15 K),
                           against the card's simulated white noise en_model_white (KF = 0, no RX)
  (11) JFE2325 refit       KF = (e_lf^2 - e_w^2) g_m^2 f_lf / I_D (models.py), e_lf = 32 nV/rtHz at
                           f_lf = 10 Hz (SLPS816A Fig. 5-24, p. 9, read by eye), e_w = 4.3 nV/rtHz
                           (p. 5); and KF_card / KF
  (12) ratios and ranges quoted from results files (model_defects.json, jfet_table3.json, chain_ac.json,
                           osc_check.json, lv_option_range.json, zin_numbers.json, cmrr_mc.json) are
                           read out and rounded once
  (13)-(18) the SR560 models of sr560_variants.py (Section 2.2): (13) the corrected model's noise against
                           the model as drawn, max |e_c / e_a - 1|; (14) Table 1 for the LSK389B model, as
                           (5); (15) the LSK389B per device, e = e_JFETs / sqrt(2) from the front end's
                           noise groups, against its calibration point (jfet_calibration.json) and
                           against the change Cordell measured from 2 to 4 mA; the weight of the drain
                           loads and the OP37, (g_N / (1 + g_N R113)) / (g_L / (1 + g_L R113)) with each
                           JFET's g_m at the operating point; (16) e_model / e_measured - 1 against a
                           user's two units (4.0 nV/rtHz with the NPD5564, 3.5 with the LSK389B, 1 kHz,
                           gain 1000; EEVblog forum, 18 March 2024); (17) the summary's ratios against the
                           corrected models with the values it quotes; (18) the CMRR against the offset
                           trim (check_cmrr_trim), the current split 6.2 V / 75 kOhm - 6.2 V / 100 kOhm and
                           the trim 6.2 V (1 - 75/100) for equal currents, the first version's failed trim
                           VTRIM = -v0 / (v1 - v0) with v1 from the transient-op fallback, and that
                           version's CMRR against the untrimmed chain; the operating-point checks
Usage: python numbers_s1_3.py
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np

import jfet_data as JD
import models
import spice

R = spice.RESULTS

# ---- data-sheet constants (each with its source) ----------------------------------------------
SR560_F_SPEC_MANUAL = 1.0e6      # SR560 manual Rev. 3.1, printed p. 5: "-3 dB at 1 MHz, 1 Vpp output"
SR560_F_SPEC_DS = 1.2e6          # SR560 data sheet, p. 3: "-3 dB at 1.2 MHz (typ.)"
# NF 5307: the reading of its manual's Fig. 4.7 (PDF p. 37, printed p. 25; gain 100 x 1, white, 2.8-3.1
# nV/rtHz by eye) and its specification (NF_5307_specifications_EN.pdf: 4 nV/rtHz typ., 1 kHz, input
# short-circuited, gain 1000), as numbers_s6_7.py holds them for Sections 6 and 7
from numbers_s6_7 import NF_EN_PLOT_G100, NF_EN_SPEC  # noqa: E402
NF5307_PLOT = tuple(v * 1e-9 for v in NF_EN_PLOT_G100)
NF5307_SPEC = NF_EN_SPEC * 1e-9
STAHL_C_EACH = 16.4e-12          # Stahl PR-E3 (4 MHz) data sheet v3.12, p. 5, Table 2: 16.4 pF at either input
JFE150_VGSOFF = (-1.5, -0.9)     # TI SLPS732B p. 5: V_GSC min / max (V_DS 10 V, 0.1 uA)
N_SIGMA_RANGE = 7.0              # assumption: the min-max range spans +-3.5 sigma
JFE2325_FIG_5_24_10HZ = 32e-9    # SLPS816A Fig. 5-24, p. 9, 10 Hz, gate grounded (read by eye; models.py)
JFE2325_TABLE_10KHZ = 4.3e-9     # SLPS816A p. 5, Table 5.5, 10 kHz, gate grounded
JFE2140_IG_3V9 = 1e-12           # JFE2140 gate current at V_DS = 3.9 V (H's input JFETs, Section 4.2): about
                                 # 1 pA, read off SLPS730B Fig. 6-6 (0.7-0.9 pA at 4 V for 1-10 mA); p. 5:
                                 # 1 pA typ, 10 pA max at V_DS = 2 V
N_H, N_L = 2, 12                 # JFETs per side (Section 4.2)
# SR560 (Section 2.2)
EEV_NPD5564, EEV_LSK389B = 4.0e-9, 3.5e-9   # a user's two units, 1 kHz, gain 1000, after the manual's CMRR and
                                 # offset adjustments (Audio Precision APx515): EEVblog forum, "SR560 Low noise
                                 # amp -- Noise Calculation", 18 March 2024 (refs/benchmark/README.md); a user
                                 # report, not an SRS document
CORDELL_LSK389 = (1.17e-9, 1.11e-9)  # LSK389 application note Rev A4, Table 1 (p. 5): a two-stage amplifier's
                                 # input noise at 2 and 4 mA (refs/datasheets/jfet/survey_TI_LIS_Toshiba_onsemi.md)
R113 = 110.0                     # SR560 sheet 560_1F: source resistor of JFET A
VREF_SR560, R120, R121 = 6.2, 100e3, 75e3   # the drains' 6.2 V; R120 drain B to ground; R121 drain A to P103
SR560_CMRR_FIRST_VERSION = (104.966, 102.534, 86.4653, 67.671, 61.649)   # sr560_chain.json cmrr_ideal_matching
                                 # as committed in f1bea76 (10 Hz, 1 kHz, 10 kHz, 100 kHz, 1 MHz), from a trim
                                 # whose second deck had fallen back to ngspice's transient op


def load(name: str):
    return json.loads((R / name).read_text(encoding="utf-8"))


ROWS: list[tuple[str, str, str]] = []


def put(out: dict, key: str, value, source: str, fmt: str = "{:.4g}"):
    """Store one quantity and remember its printed row."""
    out[key] = dict(value=value, source=source)
    if isinstance(value, (list, tuple)):
        txt = ", ".join(fmt.format(v) if isinstance(v, (int, float)) else str(v) for v in value)
    elif isinstance(value, (int, float)):
        txt = fmt.format(value)
    else:
        txt = str(value)
    ROWS.append((key, txt, source))


def crossings(rs, eh, el, level: float = 1.0):
    """R_s where e_H / e_L crosses `level` going from above to below (interpolation of ln(e_H/e_L) in
    log10 R_s); None if it never does."""
    d = np.log(np.asarray(eh) / np.asarray(el)) - math.log(level)
    for i in range(len(rs) - 1):
        if d[i] > 0 >= d[i + 1]:
            x0, x1 = math.log10(rs[i]), math.log10(rs[i + 1])
            return 10 ** (x0 + d[i] / (d[i] - d[i + 1]) * (x1 - x0))
    return None


def summary_and_section2(out: dict) -> None:
    cn = load("chain_noise.json")
    ca = load("chain_ac.json")
    sr = load("sr560_chain.json")
    # (1) noise at 1 kHz and white, total gain 1000
    e_sr = sr["noise"]["LN_1000"]["en"]["1000.0"]
    e_h1k, e_l1k = cn["H_LN_1000"]["en"]["1000.0"], cn["L_1000"]["en"]["1000.0"]
    e_hw, e_lw = cn["H_LN_1000"]["en"]["100000.0"], cn["L_1000"]["en"]["100000.0"]
    put(out, "e_SR560_1kHz_G1000_nV", e_sr * 1e9, "sr560_chain.json noise.LN_1000.en['1000.0']")
    put(out, "e_H_1kHz_G1000_nV", e_h1k * 1e9, "chain_noise.json H_LN_1000.en['1000.0']")
    put(out, "e_L_1kHz_G1000_nV", e_l1k * 1e9, "chain_noise.json L_1000.en['1000.0']")
    put(out, "e_H_white_G1000_nV", e_hw * 1e9, "chain_noise.json H_LN_1000.en['100000.0']")
    put(out, "e_L_white_G1000_nV", e_lw * 1e9, "chain_noise.json L_1000.en['100000.0']")
    put(out, "SR560_over_H_1kHz", e_sr / e_h1k, "(1) 5.707 / 1.114")
    put(out, "SR560_over_L_1kHz", e_sr / e_l1k, "(1) 5.707 / 0.426")
    # the values the summary quotes, each a single rounding of a results-file value (checked)
    q = dict(sr=5.7, h1k=1.11, l1k=0.43, hw=1.08, lw=0.42)
    for k, raw, nd in (("sr", e_sr, 1), ("h1k", e_h1k, 2), ("l1k", e_l1k, 2), ("hw", e_hw, 2), ("lw", e_lw, 2)):
        assert round(raw * 1e9, nd) == q[k], (k, raw)
    put(out, "SR560_over_H_L_1kHz_quoted", [q["sr"] / q["h1k"], q["sr"] / q["l1k"]], "(1) 5.7 / 1.11, 5.7 / 0.43")
    # (2) bandwidths
    f = {k: v["f3db"] for k, v in ca.items()}
    fsr = {k: v["f3db"] for k, v in sr["ac"].items()}
    h_ln_hi = [f[k] for k in f if k.startswith("H_LN_") and int(k.split("_")[-1]) >= 100]
    h_lo = [f[k] for k in f if k.startswith(("H_LN_", "H_HR_")) and int(k.split("_")[-1]) <= 10]
    h_hr_hi = [f[k] for k in f if k.startswith("H_HR_") and int(k.split("_")[-1]) >= 100]
    l_all = [f[k] for k in f if k.startswith("L_")]
    put(out, "f3dB_H_LN_gain_ge_100_MHz", [min(h_ln_hi) / 1e6, max(h_ln_hi) / 1e6], "chain_ac.json H_LN_100..50000.f3db")
    put(out, "f3dB_H_gain_le_10_MHz", [min(h_lo) / 1e6, max(h_lo) / 1e6], "chain_ac.json H_*_1, H_*_10 .f3db")
    put(out, "f3dB_H_HR_gain_ge_100_MHz", [min(h_hr_hi) / 1e6, max(h_hr_hi) / 1e6], "chain_ac.json H_HR_100, 1000 .f3db")
    put(out, "f3dB_L_MHz", [min(l_all) / 1e6, max(l_all) / 1e6], "chain_ac.json L_*.f3db")
    put(out, "f3dB_new_chain_all_MHz", [min(f.values()) / 1e6, max(f.values()) / 1e6], "chain_ac.json, every entry")
    put(out, "f3dB_SR560_MHz", [min(fsr.values()) / 1e6, max(fsr.values()) / 1e6], "sr560_chain.json ac.*.f3db")
    put(out, "f3dB_SR560_G100_MHz", fsr["100"] / 1e6, "sr560_chain.json ac['100'].f3db")
    put(out, "f3dB_SR560_G1000_MHz", fsr["1000"] / 1e6, "sr560_chain.json ac['1000'].f3db")
    put(out, "BW_ratio_H_G100", f["H_LN_100"] / fsr["100"], "(2) 14.82 / 0.729")
    put(out, "BW_ratio_H_G1000", f["H_LN_1000"] / fsr["1000"], "(2) 14.82 / 0.729")
    put(out, "BW_ratio_L_G1000", f["L_1000"] / fsr["1000"], "(2) 16.53 / 0.729")
    put(out, "BW_ratio_H_G100_to_spec_1MHz", f["H_LN_100"] / SR560_F_SPEC_MANUAL, "(2) 14.82 / 1")
    put(out, "BW_ratio_L_G1000_to_spec_1MHz", f["L_1000"] / SR560_F_SPEC_MANUAL, "(2) 16.53 / 1")
    put(out, "BW_ratio_H_G100_to_ds_1p2MHz", f["H_LN_100"] / SR560_F_SPEC_DS, "(2) 14.82 / 1.2")
    put(out, "BW_ratio_L_G1000_to_ds_1p2MHz", f["L_1000"] / SR560_F_SPEC_DS, "(2) 16.53 / 1.2")
    put(out, "BW_ratio_new_chain_to_spec_1MHz", [min(f.values()) / SR560_F_SPEC_MANUAL, max(f.values()) / SR560_F_SPEC_MANUAL],
        "(2) 14.82 / 1 to 25.04 / 1")
    qf = dict(h=14.82, l=16.5, sr=0.73)
    assert round(f["H_LN_100"] / 1e6, 2) == qf["h"] and round(f["L_1000"] / 1e6, 1) == qf["l"]
    assert round(fsr["100"] / 1e6, 2) == qf["sr"] and round(fsr["1000"] / 1e6, 2) == qf["sr"]
    put(out, "BW_ratio_H_L_quoted", [qf["h"] / qf["sr"], qf["l"] / qf["sr"]], "(2) 14.82 / 0.73, 16.5 / 0.73")
    put(out, "f3dB_H_front_end_x10_MHz", [min(h_lo + h_hr_hi) / 1e6, max(h_lo + h_hr_hi) / 1e6],
        "chain_ac.json H gains 1, 10 and high reserve 100, 1000 (front end at x10)")
    db = {k: v["db_10M"] for k, v in ca.items()}
    h_x100 = [db[k] for k in db if k.startswith("H_LN_") and int(k.split("_")[-1]) >= 100]
    h_x10 = [db[k] for k in db if k.startswith("H_") and not (k.startswith("H_LN_") and int(k.split("_")[-1]) >= 100)]
    put(out, "db_10M_H_x100", [min(h_x100), max(h_x100)], "chain_ac.json H_LN_100..50000.db_10M (Table 12)")
    put(out, "db_10M_H_x10", [min(h_x10), max(h_x10)], "chain_ac.json H gains 1, 10, H_HR_100, 1000 .db_10M (Table 12)")
    put(out, "db_10M_L", [min(v for k, v in db.items() if k.startswith("L_")), max(v for k, v in db.items() if k.startswith("L_"))],
        "chain_ac.json L_*.db_10M (Table 12)")
    # (3) NF 5307
    put(out, "NF5307_plot_white_nV", [v * 1e9 for v in NF5307_PLOT], "numbers_s6_7.NF_EN_PLOT_G100 (manual Fig. 4.7)")
    put(out, "NF5307_plot_over_H_white", [NF5307_PLOT[0] / e_hw, NF5307_PLOT[1] / e_hw], "(3) 2.8 / 1.084, 3.1 / 1.084")
    put(out, "NF5307_plot_over_L_white", [NF5307_PLOT[0] / e_lw, NF5307_PLOT[1] / e_lw], "(3) 2.8 / 0.418, 3.1 / 0.418")
    put(out, "NF5307_spec_over_H_1kHz", NF5307_SPEC / e_h1k, "(3) 4 / 1.114")
    put(out, "NF5307_spec_over_L_1kHz", NF5307_SPEC / e_l1k, "(3) 4 / 0.426")
    pl = [v * 1e9 for v in NF5307_PLOT]
    put(out, "NF5307_ratios_quoted", [pl[0] / q["hw"], pl[1] / q["hw"], NF_EN_SPEC / q["h1k"],
                                      pl[0] / q["lw"], pl[1] / q["lw"], NF_EN_SPEC / q["l1k"]],
        "(3) 2.8/1.08, 3.1/1.08, 4/1.11 (H); 2.8/0.42, 3.1/0.42, 4/0.43 (L)")
    # (4) H/L crossovers against source resistance
    nvs = load("noise_vs_source.json")
    rs = [r["rs"] for r in nvs["H_LN"]]
    assert rs == [r["rs"] for r in nvs["L"]]
    cross = {}
    for fk in nvs["H_LN"][0]["vn"]:
        eh = [r["vn"][fk] for r in nvs["H_LN"]]
        el = [r["vn"][fk] for r in nvs["L"]]
        cross[fk] = dict(R_x=crossings(rs, eh, el), R_L_quieter_by_1pc=crossings(rs, eh, el, 1.01),
                         R_H_quieter_by_1pc=crossings(rs, eh, el, 0.99))
        put(out, f"H_L_crossover_{float(fk):g}Hz_ohm",
            [cross[fk]["R_x"], cross[fk]["R_L_quieter_by_1pc"], cross[fk]["R_H_quieter_by_1pc"]],
            "(4) noise_vs_source.json: R_x (e_H = e_L), e_H/e_L = 1.01, = 0.99", fmt="{:.3g}")
    out["H_L_crossover_detail"] = cross
    # first-version oscillation
    osc = load("osc_check.json")
    for k in ("H100_first", "H10_first", "L200_first", "H100_first_ties", "L200_first_ties"):
        put(out, f"osc_{k}_MHz_Vpp", [osc[k]["cm_out"]["f_dom"] / 1e6, osc[k]["cm_out"]["pkpk"]],
            f"osc_check.json {k}.cm_out (f_dom, pkpk); bench: {osc[k]['bench']}")
    # low-voltage option
    lv = load("lv_option_range.json")["low-voltage (ADA4899, +/-5 V, V_ref 3 V, V_BS 1.2 V)"]
    for r in lv["ranges"]:
        put(out, f"LV_CM_range_at_Vod_{r['V_od']:g}V", None if r["empty"] else r["range"],
            "lv_option_range.json low-voltage ranges (empty: " + str(r["empty"]) + ")")
    for r in lv["ranges"]:
        put(out, f"LV_CM_range_1V_margin_at_Vod_{r['V_od']:g}V", None if r["empty"] else r["range_1V"],
            "lv_option_range.json range_1V (upper end with the cascodes' 1 V margin, as Section 4.3.1)")
    put(out, "LV_Vod_max_at_VCM_0_V", lv["V_od_max_at_V_CM_0"], "lv_option_range.json V_od_max_at_V_CM_0")
    put(out, "LV_Vod_for_VCM_min_-0.9V", lv["V_od_for_V_CM_min_minus_0p9"], "lv_option_range.json V_od_for_V_CM_min_minus_0p9")
    put(out, "LV_op_amp_swing_V", [lv["swing"]["v_ol"], lv["swing"]["v_oh"]], "lv_option_range.json swing (R_F load)")
    # the fix and its robustness (summary, finding 3; Sections 4.3 and 4.3.1)
    dab = load("da_compare_before_cnode.json")
    f_first = dab["LM7171"]["ac_H100"]["f3db"]
    put(out, "chain_f3dB_G100_first_final_ratio", [f_first / 1e6, f["H_LN_100"] / 1e6, f["H_LN_100"] / f_first],
        "da_compare_before_cnode.json LM7171.ac_H100.f3db (first version), chain_ac.json H_LN_100.f3db; 14.8 / 30.1")
    sc = load("stability_corners.json")
    nom = [sc[f"{c} | nominal"][m]["modulus"] for c in ("H100", "H10", "L200") for m in ("dm", "cm")]
    low = [sc[f"{c} | C_node x0.7"][m]["modulus"] for c in ("H100", "H10", "L200") for m in ("dm", "cm")]
    put(out, "modulus_margin_min_nominal_and_Cnode_x0.7", [min(nom), min(low)],
        "stability_corners.json, smallest over H100, H10, L200, DM and CM")
    s4a = load("numbers_s4a.json")["4.3.1 mitigations"]
    e12 = s4a["H: E12 values / simulated C_node"]["value"] + s4a["L: E12 values / simulated C_node"]["value"]
    put(out, "Cnode_E12_over_simulated_H_L", e12, "numbers_s4a.json: 270-330 pF / 220 pF (H), 560-680 pF / 470 pF (L)")
    lvj = load("lv_option.json")
    put(out, "LV_CM_gain_margin_dB_f3dB_MHz", [lvj["loop"]["cm"]["gm_db"], lvj["f3db"] / 1e6], "lv_option.json loop.cm.gm_db, f3db")
    # input capacitance
    z = load("zin_numbers.json")
    for case in ("H100", "L200"):
        put(out, f"Cin_{case}_network_pF_1k_100k_300k_1M", [v * 1e12 for v in z[case]["network_dm"]["C_eff"].values()],
            f"zin_numbers.json {case}.network_dm.C_eff")
        put(out, f"Cin_{case}_bare_pF_1k_100k_300k_1M", [v * 1e12 for v in z[case]["bare_dm"]["C_eff"].values()],
            f"zin_numbers.json {case}.bare_dm.C_eff")
        put(out, f"CP_plus_CZ_{case}_pF", z[case]["C_P_plus_C_Z"] * 1e12, f"zin_numbers.json {case}.C_P_plus_C_Z")
        put(out, f"f_Z_{case}_MHz", z[case]["f_Z"] / 1e6, f"zin_numbers.json {case}.f_Z = 1/(2 pi R_Z C_Z)")
    # CMRR, distortion, slew (summary)
    mc = load("cmrr_mc.json")
    i1k, i1M = mc["H100"]["freq"].index(1000.0), mc["H100"]["freq"].index(1e6)
    put(out, "CMRR_median_H100_1kHz_dB", mc["H100"]["median"][i1k], f"cmrr_mc.json H100 ({mc['H100']['trials']} trials, 50 ohm)")
    put(out, "CMRR_median_H100_rs0_1MHz_dB", mc["H100_rs0"]["median"][i1M], f"cmrr_mc.json H100_rs0 ({mc['H100_rs0']['trials']} trials)")
    put(out, "CMRR_median_L200_rs0_1MHz_dB", mc["L200_rs0"]["median"][i1M], f"cmrr_mc.json L200_rs0 ({mc['L200_rs0']['trials']} trials)")
    ls = load("large_signal.json")["H100"]
    thd = {(r["f0"], r["vout_pp"]): r["thd"] for r in ls["thd"]}
    put(out, "THD_H100_1Vpp_1MHz_10MHz_percent", [100 * thd[(1e6, 1)], 100 * thd[(1e7, 1)]], "large_signal.json H100.thd")
    put(out, "slew_H100_10V_V_per_us", [r["slew_v_us"] for r in ls["step"] if r["vstep"] == 10.0][0], "large_signal.json H100.step")
    # (5) Table 1
    dev, rows = {}, []
    groups = {"LN": [1, 2, 5, 10, 20, 50, (100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000)],
              "HDR": [10, 20, 50, 100, 200, 500, 1000, 2000]}
    for mode, cols in groups.items():
        for c in cols:
            gs = c if isinstance(c, tuple) else (c,)
            vals = [sr["noise"][f"{mode}_{g}"]["en"]["1000.0"] for g in gs]
            whites = [sr["noise"][f"{mode}_{g}"]["en"]["100000.0"] for g in gs]
            man = sr["noise"][f"{mode}_{gs[0]}"]["manual"]
            d = [v * 1e9 / man - 1 for v in vals]
            key = f"{mode}_{gs[0]}" + (f"-{gs[-1]}" if len(gs) > 1 else "")
            dev[key] = dict(model_1k_nV=[min(vals) * 1e9, max(vals) * 1e9], model_100k_nV=[min(whites) * 1e9, max(whites) * 1e9],
                            manual=man, deviation=[min(d), max(d)])
            rows.append(key)
    within = [k for k in rows if max(abs(x) for x in dev[k]["deviation"]) <= 0.30]
    out["table1"] = dev
    for k in rows:
        put(out, f"Table1_{k}", [dev[k]["model_1k_nV"][0], dev[k]["model_1k_nV"][1], 100 * dev[k]["deviation"][0],
                                 100 * dev[k]["deviation"][1]],
            "(5) sr560_chain.json noise: e_model(1 kHz) min, max (nV/rtHz); d min, max (%)")
    put(out, "Table1_columns_within_30pc", [len(within), len(rows)], "(5) count of |d| <= 30 %")
    put(out, "Table1_exceptions", [k for k in rows if k not in within], "(5)")
    fe = load("sr560_frontend.json")["sr560_x10_2N5564"]
    put(out, "SR560_FE_CMRR_1kHz_dB", fe["cmrr_db_1k"], "sr560_frontend.json cmrr_db_1k")
    put(out, "SR560_FE_f3dB_MHz", fe["f3db"] / 1e6, "sr560_frontend.json f3db")
    put(out, "SR560_FE_gain_1k", fe["gain_1k"], "sr560_frontend.json gain_1k")
    put(out, "SR560_chain_CMRR_dB_10_1k_10k_100k_1M", list(sr["cmrr_ideal_matching"].values()), "sr560_chain.json cmrr_ideal_matching")
    # 2N5564 targets (Section 2.3)
    t = load("jfet_model_check.json")["2N5564 targets"]
    ll = [t["readings"][n]["interpolated"]["log-log"] for n in t["readings"]]
    put(out, "2N5564_loglog_white_nV", [min(x["white"] for x in ll) * 1e9, max(x["white"] for x in ll) * 1e9],
        "jfet_model_check.json '2N5564 targets' log-log, both readings")
    put(out, "2N5564_loglog_1kHz_nV", [min(x["at_1kHz"] for x in ll) * 1e9, max(x["at_1kHz"] for x in ll) * 1e9],
        "jfet_model_check.json '2N5564 targets' log-log, both readings")


def section1_and_3(out: dict) -> None:
    nt = load("noise_theory.json")
    cal = load("jfet_calibration.json")
    put(out, "JFE150_gm_mS", cal["JFE150"]["gm"] * 1e3, "jfet_calibration.json JFE150.gm (5 mA, 5 V)")
    put(out, "e_th_JFE150_nV", nt["JFE150 channel noise"]["e_th"] * 1e9, "noise_theory.json sqrt(4kT (2/3) / g_m)")
    put(out, "two_pow_minus_quarter", nt["current doubling"]["factor"], "noise_theory.json 2^(-1/4)")
    put(out, "i_n_1pA_1nA_fA", [nt["gate-current shot noise"]["1e-12"] * 1e15, nt["gate-current shot noise"]["1e-09"] * 1e15],
        "noise_theory.json sqrt(2 q I_G)")
    put(out, "R_x_1nV_at_1pA_1nA_kohm", [nt["e_n/i_n crossover"]["I_G 1e-12"]["R_x"]["e_n 1e-09"] / 1e3,
                                         nt["e_n/i_n crossover"]["I_G 1e-09"]["R_x"]["e_n 1e-09"] / 1e3],
        "noise_theory.json e_n / i_n, e_n = 1 nV/rtHz")
    # (7), (8)
    sig = (JFE150_VGSOFF[1] - JFE150_VGSOFF[0]) / N_SIGMA_RANGE
    put(out, "sigma_VTO_from_VGSoff_range_mV", sig * 1e3, "(7) 0.6 V / 7 (SLPS732B p. 5)")
    cs = nt["current sharing"]
    put(out, "dI_over_I_per_sigma", [cs["dVTO"] * 1e3, cs["overdrive_operating_point"] * 1e3, cs["dI_over_I"]],
        "(8) noise_theory.json: dV_TO (mV), V_GS - V_TO (mV), 2 dV_TO / (V_GS - V_TO)")
    put(out, "Eq4_Rs_N12_N1_10MHz_ohm", [nt["Eq. (4)"]["R_s_N12"], nt["Eq. (4)"]["R_s_N1"]],
        "noise_theory.json 1 / (2 pi 10 MHz N 24 pF)")
    e2 = nt["Eq. (2)"]
    put(out, "Eq2_H_side_diff_nV", [e2["H: 2 x JFE2140 per side"]["e_side"] * 1e9, e2["H: 2 x JFE2140 per side"]["e_diff"] * 1e9],
        "noise_theory.json Eq. (2)")
    put(out, "Eq2_L_side_diff_nV", [e2["L: 12 x JFE150 per side"]["e_side"] * 1e9, e2["L: 12 x JFE150 per side"]["e_diff"] * 1e9],
        "noise_theory.json Eq. (2)")
    put(out, "Eq2_SR560_side_diff_nV", [e2["SR560: 1 x 2N5564 per side"]["e_side"] * 1e9, e2["SR560: 1 x 2N5564 per side"]["e_diff"] * 1e9],
        "noise_theory.json Eq. (2)")
    # (6) capacitances per input and Figure 1's stars
    c_h = N_H * JD.JFETS["JFE2140"][5]
    c_l = N_L * JD.JFETS["JFE150"][5]
    put(out, "C_JFETs_H_L_pF", [c_h, c_l], "(6) 2 x 13 pF, 12 x 24 pF")
    put(out, "H_bias_current_per_input_pA", N_H * JFE2140_IG_3V9 * 1e12, "2 x about 1 pA (SLPS730B Fig. 6-6 at 3.9 V)")
    put(out, "Stahl_both_channels_pF", 2 * STAHL_C_EACH * 1e12, "(6) 2 x 16.4 pF")
    cn = np.load(R / "curves_noise.npz")
    put(out, "Fig1_stars_10kHz_H100_L200_nV", [spice.at(cn["H100_f"], cn["H100_total"], 1e4) * 1e9,
                                              spice.at(cn["L200_f"], cn["L200_total"], 1e4) * 1e9],
        "curves_noise.npz H100_total, L200_total at 10 kHz (front ends alone)")
    t3 = load("jfet_table3.json")
    put(out, "Fig1_FEMTO_Stahl_basis", [t3["fig1_basis"]["FEMTO DLPVA-101-B"]["en"], t3["fig1_basis"]["Stahl PR-E3"]["en"],
                                        t3["fig1_basis"]["Stahl PR-E3"]["cin"]], "jfet_table3.json fig1_basis")
    # FOM (Table 3) and the LSK389 ratios
    fom = {r["part"]: r["fom"] for r in t3["table3"]}
    put(out, "FOM_LSK389_JFE2140_JFE150_LSBF862_BF862", [fom[p] for p in ("LSK389", "JFE2140", "JFE150", "LSBF862", "BF862")],
        "jfet_table3.json table3.fom = e_n sqrt(C_iss)")
    rat = t3["lsk389_ratios"]
    put(out, "FOM_LSK389_measured", rat["fom_lsk389_measured"], "jfet_table3.json 1.17 sqrt(25)")
    best = ("JFE150", "JFE2140", "LSBF862")
    put(out, "LSK389_over_best_datasheet", [rat["ratio_datasheet"][p] for p in best], "jfet_table3.json (JFE150, JFE2140, LSBF862)")
    put(out, "LSK389_over_best_measured", [rat["ratio_measured"][p] for p in best], "jfet_table3.json (JFE150, JFE2140, LSBF862)")
    sec33 = ("JFE2140", "JFE150", "LSBF862", "LSK170", "IF170", "LSK489")
    put(out, "LSK389_over_Sec3.3_parts_datasheet", [rat["ratio_datasheet"][p] for p in sec33], "jfet_table3.json " + ", ".join(sec33))
    put(out, "LSK389_over_Sec3.3_parts_measured", [rat["ratio_measured"][p] for p in sec33], "jfet_table3.json " + ", ".join(sec33))
    # (9) twelve JFE150 against one IF3601 per side
    e150, e150_10, c150 = JD.JFETS["JFE150"][2], JD.JFETS["JFE150"][4], JD.JFETS["JFE150"][5]
    e36, e36_10, c36 = JD.JFETS["IF3601"][2], JD.JFETS["IF3601"][4], JD.JFETS["IF3601"][5]
    put(out, "IF3601_x1_side_diff_nV_C_pF", [e36, math.sqrt(2) * e36, c36], "(9) 0.34, sqrt(2) 0.34, 650 pF")
    put(out, "JFE150_x12_side_diff_nV_C_pF", [e150 / math.sqrt(N_L), math.sqrt(2) * e150 / math.sqrt(N_L), N_L * c150],
        "(9) 0.8/sqrt(12), sqrt(2) 0.8/sqrt(12), 12 x 24 pF")
    put(out, "FOM_10Hz_JFE150_IF3601", [e150_10 * math.sqrt(c150), e36_10 * math.sqrt(c36)], "(9) 1.8 sqrt(24), 0.60 sqrt(650)")
    # model defects quoted in the summary (Table 8)
    md = load("model_defects.json")
    op, jf = md["opamp"], md["jfet"]
    put(out, "opamp_e10_ratio_THS4021_THS4031_THS3091", [op[p]["ratio_e_10"] for p in ("THS4021", "THS4031", "THS3091")],
        "model_defects.json opamp.*.ratio_e_10")
    put(out, "opamp_i10_ratio_THS4021_THS4031", [op[p]["ratio_i_10"] for p in ("THS4021", "THS4031")],
        "model_defects.json opamp.*.ratio_i_10")
    put(out, "THS3091_white_i_ratio", op["THS3091"]["ratio_i_white"], "model_defects.json opamp.THS3091.ratio_i_white")
    put(out, "LM7171_white_e_ratio", op["LM7171"]["ratio_e_white"], "model_defects.json opamp.LM7171.ratio_e_white")
    put(out, "JFE2140_1f_power_ratio", jf["JFE2140 1/f"]["one_over_f_power_ratio_datasheet_to_card"],
        "model_defects.json jfet['JFE2140 1/f']")
    put(out, "LSBF862_1f_power_ratio", jf["LSBF862 1/f"]["one_over_f_power_ratio_card_to_datasheet"],
        "model_defects.json jfet['LSBF862 1/f']")
    put(out, "2N5564_KF_ratio", jf["2N5564 KF"]["ratio"], "model_defects.json jfet['2N5564 KF'] (67860f / 6.786e-002f)")
    # (10) ngspice channel noise: 8kT g_m / 3, checked on the JFE150 card (KF = 0, no RX)
    c = cal["JFE150"]
    rs_card = models._get(c["card"], "rs")
    e_chk = math.sqrt(4 * spice.KT * (2 / (3 * c["gm"]) + rs_card))
    put(out, "ngspice_channel_noise_check_nV", [e_chk * 1e9, c["en_model_white"] * 1e9, e_chk / c["en_model_white"] - 1],
        "(10) sqrt(4kT (2/(3 g_m) + R_S)); jfet_calibration.json en_model_white; relative difference")
    put(out, "ngspice_check_inputs_gm_mS_RS_ohm_T_K", [c["gm"] * 1e3, rs_card, spice.KT / 1.380649e-23],
        "jfet_calibration.json JFE150.gm and its card's RS; spice.KT")
    # (11) JFE2325 refit and the other Table 4 numbers
    j = cal["JFE2325"]
    kf_chk = (JFE2325_FIG_5_24_10HZ ** 2 - JFE2325_TABLE_10KHZ ** 2) * j["gm"] ** 2 * 10.0 / j["id"]
    put(out, "JFE2325_KF_refit", [j["kf"], kf_chk, j["kf_card"], j["kf_card"] / j["kf"]],
        "(11) jfet_calibration.json kf; (32^2 - 4.3^2) nV^2 g_m^2 10 Hz / I_D; kf_card; kf_card / kf")
    put(out, "JFE2325_RX_ohm_ID_mA_gm_mS", [j["rx"], j["id"] * 1e3, j["gm"] * 1e3], "jfet_calibration.json JFE2325")
    put(out, "JFE2325_model_10kHz_10Hz_nV", [j["en_achieved_at_f_w"] * 1e9, j["en_achieved_lf"] * 1e9],
        "jfet_calibration.json JFE2325 en_achieved_at_f_w, en_achieved_lf")
    jm = load("jfet_model_check.json")["JFE2325"]
    put(out, "JFE2325_published_card_1f_ratio", jm["published_card"]["one_over_f_power_ratio_10Hz"],
        "jfet_model_check.json JFE2325.published_card")
    lb = cal["LSBF862"]
    put(out, "LSBF862_achieved_white_10Hz_nV", [lb["en_achieved_white"] * 1e9, lb["en_achieved_lf"] * 1e9, lb["rx"]],
        "jfet_calibration.json LSBF862 (RX clipped at 0)")


SR560_MODELS = ("corrected", "corrected_lsk389b")


def sr560_models(out: dict) -> None:
    """(6) The two further SR560 models of sr560_variants.py (Section 2.2): the corrected netlist and
    op-amp dynamics, and the same with the LSK389B of newer units; their noise, bandwidth, CMRR and
    front end, and the summary's ratios against them (the as-drawn model is summary_and_section2's)."""
    v = load("sr560_variants.json")
    cn, ca = load("chain_noise.json"), load("chain_ac.json")
    e_h1k, e_l1k = cn["H_LN_1000"]["en"]["1000.0"], cn["L_1000"]["en"]["1000.0"]
    for m in SR560_MODELS:
        r = v["models"][m]
        n, src = r["noise"], f"sr560_variants.json models.{m}"
        e1k, ew, e10 = (n["LN_1000"]["en"][k] for k in ("1000.0", "100000.0", "10"))
        put(out, f"SR560_{m}_e_1kHz_white_10Hz_G1000_nV", [e1k * 1e9, ew * 1e9, e10 * 1e9],
            f"{src}.noise.LN_1000.en (1 kHz, 100 kHz, 10 Hz)")
        put(out, f"SR560_{m}_noise_1kHz_100kHz_nV", {k: [x["en"]["1000.0"] * 1e9, x["en"]["100000.0"] * 1e9]
                                                     for k, x in n.items()}, f"{src}.noise.*.en (Table 1)")
        put(out, f"SR560_{m}_over_H_L_1kHz", [e1k / e_h1k, e1k / e_l1k], f"(6) {src} LN_1000 at 1 kHz / chain_noise.json")
        f3 = {g: a["f3db"] / 1e6 for g, a in r["ac"].items()}
        put(out, f"SR560_{m}_f3dB_MHz", [min(f3.values()), max(f3.values())], f"{src}.ac.*.f3db")
        put(out, f"SR560_{m}_f3dB_G100_G1000_MHz", [f3["100"], f3["1000"]], f"{src}.ac['100', '1000'].f3db")
        put(out, f"SR560_{m}_dB_1MHz", [min(a["db_1M"] for a in r["ac"].values()), max(a["db_1M"] for a in r["ac"].values())],
            f"{src}.ac.*.db_1M")
        put(out, f"SR560_{m}_peaking_dB_max", max(a["peak_db"] for a in r["ac"].values()), f"{src}.ac.*.peak_db")
        put(out, f"BW_ratio_H_G100_L_G1000_over_SR560_{m}",
            [ca["H_LN_100"]["f3db"] / (f3["100"] * 1e6), ca["L_1000"]["f3db"] / (f3["1000"] * 1e6)],
            f"(6) chain_ac.json H_LN_100, L_1000 f3db / {src}.ac['100', '1000'].f3db")
        put(out, f"SR560_{m}_CMRR_dB_10_1k_10k_100k_1M", list(r["cmrr_ideal_matching"].values()),
            f"{src}.cmrr_ideal_matching")
        fe = r["frontend_x10"]
        put(out, f"SR560_{m}_FE_gain_f3dBMHz_CMRR1k", [fe["gain_1k"], fe["f3db"] / 1e6, fe["cmrr_db_1k"]],
            f"{src}.frontend_x10 (gain_1k, f3db, cmrr_db_1k)")
        put(out, f"SR560_{m}_FE_en_1k_100k_nV", [fe["en_in"]["1000.0"] * 1e9, fe["en_in"]["100000.0"] * 1e9],
            f"{src}.frontend_x10.en_in")
        put(out, f"SR560_{m}_FE_groups_1k_nV", {g: x * 1e9 for g, x in fe["groups_1k"].items()},
            f"{src}.frontend_x10.groups_1k")
    # (13) the corrected model's noise against the model as drawn (the corrections change only the dynamics)
    sr = load("sr560_chain.json")
    nc = v["models"]["corrected"]["noise"]
    dmax = max(abs(nc[k]["en"][fk] / sr["noise"][k]["en"][fk] - 1) for k in nc for fk in ("1000.0", "100000.0", "10"))
    put(out, "SR560_corrected_vs_as_drawn_noise_max_rel_diff", dmax,
        "(13) max |e_corrected / e_as_drawn - 1| over every gain of both modes at 10 Hz, 1 kHz, 100 kHz")
    # (14) Table 1 for the LSK389B model: d = e_model(1 kHz) / e_manual - 1, as (5)
    nl = v["models"]["corrected_lsk389b"]["noise"]
    cols = {"LN": [1, 2, 5, 10, 20, 50, (100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000)],
            "HDR": [10, 20, 50, 100, 200, 500, 1000, 2000]}
    dl = {}
    for mode, cs in cols.items():
        for c in cs:
            gs = c if isinstance(c, tuple) else (c,)
            e = [nl[f"{mode}_{g}"]["en"]["1000.0"] * 1e9 for g in gs]
            w = [nl[f"{mode}_{g}"]["en"]["100000.0"] * 1e9 for g in gs]
            man = nl[f"{mode}_{gs[0]}"]["manual"]
            key = f"{mode}_{gs[0]}" + (f"-{gs[-1]}" if len(gs) > 1 else "")
            dl[key] = dict(e_1k=[min(e), max(e)], e_100k=[min(w), max(w)], manual=man,
                           d_pc=[100 * (min(e) / man - 1), 100 * (max(e) / man - 1)])
    out["table1_lsk389b"] = dl
    for k, x in dl.items():
        put(out, f"Table1_LSK389B_{k}", x["e_1k"] + x["e_100k"] + x["d_pc"],
            "(14) sr560_variants.json corrected_lsk389b noise: e(1 kHz) min, max; e(100 kHz) min, max (nV/rtHz); d min, max (%)")
    within = [k for k, x in dl.items() if max(abs(d) for d in x["d_pc"]) <= 30]
    put(out, "Table1_LSK389B_columns_within_30pc", [len(within), len(dl)], "(14) count of |d| <= 30 %")
    put(out, "Table1_LSK389B_exceptions", {k: dl[k]["d_pc"] for k in dl if k not in within}, "(14)")
    # (15) the LSK389B in the front end: per device, its g_m, and the weight of the drain loads and OP37
    fl, fn = v["models"]["corrected_lsk389b"]["frontend_x10"], v["models"]["corrected"]["frontend_x10"]
    cal = load("jfet_calibration.json")["LSK389B_LIS"]
    e_dev = fl["groups_1k"]["input JFETs"] / math.sqrt(2)
    put(out, "SR560_LSK389B_per_device_1kHz_nV_and_at_calibration", [e_dev * 1e9, cal["en_achieved_at_f_w"] * 1e9,
                                                                    e_dev / cal["en_achieved_at_f_w"] - 1],
        "(15) frontend_x10.groups_1k['input JFETs'] / sqrt(2) (4.5 mA, V_DS 5.9 V); jfet_calibration.json "
        "LSK389B_LIS en_achieved_at_f_w (1 kHz, 2 mA, 10 V); ratio - 1")
    put(out, "Cordell_LSK389_2mA_4mA_nV_change", [CORDELL_LSK389[0] * 1e9, CORDELL_LSK389[1] * 1e9,
                                                 CORDELL_LSK389[1] / CORDELL_LSK389[0] - 1],
        "LSK389 application note Rev A4, Table 1 (p. 5): 1.17 and 1.11 nV/rtHz at 2 and 4 mA; ratio - 1")
    put(out, "SR560_LSK389B_RX_ohm_and_its_noise_nV", [cal["rx"], math.sqrt(4 * spice.KT * cal["rx"]) * 1e9],
        "jfet_calibration.json LSK389B_LIS rx; sqrt(4kT RX)")
    ga, gn = fl["op"]["@j.xja.j1[gm]"], fn["op"]["@j.xja.j1[gm]"]
    geff = (gn / (1 + gn * R113)) / (ga / (1 + ga * R113))
    rl = [fl["groups_1k"][g] / fn["groups_1k"][g] for g in ("drain loads R131, R117", "U102 (OP37)")]
    put(out, "SR560_gm_2N5564_LSK389B_mS_and_load_weight", [gn * 1e3, ga * 1e3, geff] + rl,
        "(15) frontend_x10.op @j.xja.j1[gm] (2N5564, LSK389B); (g_N/(1 + g_N R113)) / (g_L/(1 + g_L R113)), "
        "R113 = 110 ohm; simulated ratios LSK389B/NPD5564 of the drain loads' and the OP37's shares")
    # (16) a user's two units (EEVblog forum, 18 March 2024; refs/benchmark/README.md), gain 1000, 1 kHz
    put(out, "EEVblog_units_vs_models_pc", [100 * (fn_e / m - 1) for fn_e, m in
                                           ((v["models"]["corrected"]["noise"]["LN_1000"]["en"]["1000.0"], EEV_NPD5564),
                                            (nl["LN_1000"]["en"]["1000.0"], EEV_LSK389B))],
        "(16) e_model(1 kHz, G 1000) / e_measured - 1: NPD5564 model / 4.0 nV, LSK389B model / 3.5 nV")
    # (17) the summary's ratios against the corrected models, with the values it quotes (checked roundings)
    e_l = nl["LN_1000"]["en"]["1000.0"]
    assert round(e_l * 1e9, 2) == 3.23
    put(out, "SR560_LSK389B_over_H_L_1kHz_quoted", [3.23 / 1.11, 3.23 / 0.43], "(17) 3.23 / 1.11, 3.23 / 0.43")
    fc = {m: v["models"][m]["ac"] for m in SR560_MODELS}
    q = {m: (round(fc[m]["100"]["f3db"] / 1e6, 2), round(fc[m]["1000"]["f3db"] / 1e6, 2)) for m in SR560_MODELS}
    assert q == {"corrected": (1.04, 1.04), "corrected_lsk389b": (1.09, 1.09)}, q
    put(out, "BW_ratio_H_L_over_corrected_models_quoted", [14.82 / 1.09, 14.82 / 1.04, 16.5 / 1.09, 16.5 / 1.04],
        "(17) 14.82 / 1.09, 14.82 / 1.04 (H, G 100); 16.5 / 1.09, 16.5 / 1.04 (L, G 1000)")
    # (18) the CMRR against the offset trim (check_cmrr_trim) and the failed trim of the first version
    ct = v["check_cmrr_trim"]
    for k in ("trimmed", "vtrim_0V"):
        x = ct[k]
        put(out, f"SR560_CMRR_trim_{k}", [x["vtrim"], x["id_a_minus_b"] * 1e6, 100 * x["gm_a_over_b_minus_1"],
                                          (x["op"]["v(sa)"] - x["op"]["v(sb)"]) * 1e3] + list(x["cmrr"].values()),
            f"sr560_variants.json check_cmrr_trim.{k}: VTRIM (V), I_D(A) - I_D(B) (uA), g_m(A)/g_m(B) - 1 (%), "
            "v(sa) - v(sb) (mV), CMRR at 10 Hz, 1 kHz, 10 kHz, 100 kHz, 1 MHz (dB)")
    put(out, "SR560_trim_split_closed_form", [(VREF_SR560 / R121 - VREF_SR560 / R120) * 1e6, VREF_SR560 * (1 - R121 / R120)],
        "(18) 6.2 V / 75 kOhm - 6.2 V / 100 kOhm (uA, VTRIM = 0); VTRIM for equal currents, 6.2 V (1 - 75/100)")
    co = v["check_operating_point"]
    v0, v1 = ct["vtrim_0V"]["op"]["v(out)"], co["one_mohm_without_nodeset"]["v"]["out"]
    v1_true = co["one_ohm_without_nodeset"]["v"]["out"]
    put(out, "SR560_failed_trim_VTRIM_mV", [-v0 / (v1 - v0) * 1e3, -v0 / (v1_true - v0) * 1e3],
        "(18) -v0 / (v1 - v0): v0 = v(out) at VTRIM 0 (check_cmrr_trim), v1 = v(out) at VTRIM 1 V from the "
        "fallback (check_operating_point one_mohm_without_nodeset) and from the DC solution (one_ohm_...)")
    fe_gain = load("sr560_frontend.json")["sr560_x10_2N5564"]["gain_1k"]
    put(out, "SR560_trim_secant_G1000",
        [v0 * 1e3, v1_true * 1e3, (v1_true - v0) * 1e3, ct["trimmed"]["vtrim"], ct["trimmed"]["op"]["v(out)"] * 1e6,
         ct["trimmed"]["op"]["v(out)"] / fe_gain * 1e6, co["trimmed_continuation"]["v"]["out50"] * 1e3],
        "(18) the trim at a gain of 1000 (sr560_chain.trimmed): v(out) at VTRIM = 0 and 1 V (mV), slope (mV/V), "
        "VTRIM = -v0/(v1 - v0) (V), v(out) there (uV) and referred to the input through the front end's gain "
        "(uV), v(out50) there (mV)")
    put(out, "SR560_first_version_CMRR_minus_untrimmed_dB",
        [a - b for a, b in zip(SR560_CMRR_FIRST_VERSION, ct["vtrim_0V"]["cmrr"].values())],
        "(18) the first version's sr560_chain.json cmrr_ideal_matching (commit f1bea76) - check_cmrr_trim.vtrim_0V")
    for k in ("one_mohm_without_nodeset", "one_mohm_abstol_1e-12_without_nodeset", "one_ohm_without_nodeset",
              "with_nodeset", "nodeset_at_fallback_state", "trimmed_generic_nodeset", "trimmed_continuation"):
        x = co[k]
        put(out, f"SR560_op_check_{k}", [x["fallback"], x["v"]["ref"], x["v"]["da"], x["v"]["out"], x["v"]["out50"]],
            f"sr560_variants.json check_operating_point.{k}: fallback, v(ref), v(da), v(out), v(out50)")
    put(out, "SR560_variants_check_as_drawn_max_rel_diff", v["check_as_drawn"]["max_abs_rel_diff"],
        "sr560_variants.json check_as_drawn (the code without an edit against sr560_chain.json)")
    put(out, "SR560_variants_check_corrected_vs_bw_rel_diff",
        {g: x["rel_diff"] for g, x in v["check_corrected_vs_bw"].items()},
        "sr560_variants.json check_corrected_vs_bw (against sr560_bw_check.json f_datasheet_add_C406_C301_47p)")
    fe0 = load("sr560_frontend.json")["sr560_x10_2N5564"]
    put(out, "SR560_FE_groups_1k_nV", {g: x * 1e9 for g, x in fe0["groups_1k"].items()},
        "sr560_frontend.json sr560_x10_2N5564.groups_1k (as drawn)")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out: dict = {}
    summary_and_section2(out)
    sr560_models(out)
    section1_and_3(out)
    (R / "numbers_s1_3.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    w = max(len(k) for k, _, _ in ROWS)
    print(f"{'quantity':{w}s} | value | source")
    for k, v, s in ROWS:
        print(f"{k:{w}s} | {v} | {s}")


if __name__ == "__main__":
    main()
