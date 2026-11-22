# Number audit of low_noise_preamp.md (21 November 2026)

Every number in the report was checked against the rule that it must follow from an equation written in the note and an archived script, from an archived result, or from an external document cited by page, table or figure. Four ranges were audited separately; line numbers refer to the note as it stood on 21 November 2026 before any fix. The tables list only the numbers that fail the rule or disagree with their source.

Totals: about 1875 numbers checked, about 450 flagged in 266 rows (lines 1–252: 108 in 59 rows; 253–583: 79 in 59 rows; 584–767: 112 in 69 rows plus about 20 ratios; 768–1091: about 150 in 79 rows). The low-voltage option and the input protection (Section 4.3.1, part, and Table 6d) were checked separately by recovering their calculations into scripts; that summary is at the end.

# Audit A: lines 1–252 (summary, Sections 1–3), about 108 flagged in 59 rows (of about 435)

| line | number, with context | problem | likely source | suggested fix |
|---|---|---|---|---|
| 11 (90, 167; 168 "≈250") | "effective input capacitance of about 20 pF" | no equation/script: it is C_P + C_Z (10+10 H; 30+220 L); curves_zin only bare FE | chain.py INPUT_NET | write C_in ≈ C_P + C_Z for f ≪ 1/(2πR_Z C_Z) (7.2 MHz H, 15 MHz L); zin run with network |
| 11 | "0.05 pF between 1 kHz and 1 MHz" | mismatch: 0.050–0.057 up to ≈300 kHz, 0.066 (500 kHz), 0.082 (700 kHz), 0.114 pF at 1 MHz | curves_zin.npz H100_dm_z | "≈0.05 pF 1 kHz–300 kHz (0.11 pF at 1 MHz)"; script → JSON |
| 11 | "bias current in the picoampere range" | no citation | V_DS 3.9 V; SLPS730B p. 5, Fig. 6-6 | cite |
| 12 (168) | "for sources below about 300 Ω" | no criterion; archived curves don't cross at 300 Ω (L quieter up to ≈30 kΩ at 1 kHz, ≈1 kΩ at 1 MHz; H quieter above ≈100 Ω only at 10 MHz) | noise_vs_source.json | state criterion, compute in noise_vs_source.py, or call it a recommendation |
| 14 | "−3 dB at 14.9 MHz (H, gain ≥ 100)" | rounding: 14.849 MHz at gain 100 | chain_ac.json H_LN_100.f3db | "14.85–14.87 MHz" |
| 14 | "H is 5 times quieter … L 13 times" | no script (5.707/1.115 = 5.1; 5.707/0.428 = 13.3) | sr560_chain.json LN_1000; chain_noise H_LN_1000, L_1000 at 1 kHz | compute ratios |
| 14 | "about 20 times … (15–17 times the specified 1 MHz)" | no script (14.85/0.73–0.75 = 20; 16.6/0.73–0.79 = 21–23) | chain_ac, sr560_chain | compute |
| 14 | "H 2.3–2.8 times … L 6–7 times" (vs NF 5307) | no script; differs from l. 170 (2.3–3.7, 6–10) | NF plot 2.5–3 nV/√Hz vs 1.08/0.42 | compute both; "against NF's plotted 2.5–3" |
| 14 | "with 0.05 % resistors" | mismatch: σ = 0.05 % for 0.1 % parts; σ = 0.005 % (0.01 % network) for RD1–RD4 | cmrr_mc.py docstring 9–11 | "0.1 % resistors (σ 0.05 %), 0.01 % network in S2" |
| 14 | "against 86 dB in the NF 5307's plot" | no citation | NF_5307_datasheet_fig46.jpg ≈86 dB at 1 MHz, gain 100 | cite figure |
| 18 | "2.7 for the BF862/LSBF862" | mismatch: Table 3 BF862 2.5 | jfet_data.py; Table 3 | "2.5 (BF862) / 2.7 (LSBF862)" |
| 18 (220) | "about twice as good per unit of capacitance" | no script: 8.0/3.9 = 2.1, 8.0/3.2 = 2.5, 8.0/2.7 = 3.0; 1.5–2.2 vs Cordell's 5.9 | Table 3 | give range, compute |
| 19 | "4.6–5.7 times … 15 times … a tenth … half" | no script: uncorrected model values only as comments in models.py | models.py VENDOR_OPAMPS comments | archive uncorrected-model fixture runs; cite from Table 7 |
| 20 | "oscillated near 290 MHz" | mismatch: osc_check 282.8 MHz; old loop −180° at 284.7 MHz; §4.3 says 293; archived run is H100 with final C_I/C_X and C_node 0, not first version; no L run | osc_check.json H100_cnode0p.f_dom; curves_loop out_H100_old_cm | "≈285 MHz"; archive first-version H and L transients |
| 23 | "CM range to about ±0.5–1 V" | mismatch: §4.3.1 −0.9 to +0.5 V; lv_option_range.json: −3.69 to +0.66 V at zero output, −0.9 V only at 5.6 V output, empty at 10 V | lv_option_range.json | quote archived range with output condition |
| 39 | "γ is 2/3 for a long channel" | no citation | literature_notes T3 (Spieler 1999 p. 3), T8 (Leach 1994 p. 1531) | cite |
| 39 | "g_m = 25.9 mS in TI's model (Section 3.4)" | pointer wrong: Section 3.4/Table 4 don't show g_m | jfet_calibration.json JFE150.gm 0.025926 | cite JSON |
| 39 | "√(4kT·2/3/g_m) = 0.65 nV/√Hz" | no script; ngspice with RS/RD gives 0.704 | jfet_calibration JFE150.en_model_white | print from noise_theory.py |
| 39 | "each doubling … buys only 16 %" | no equation: 1 − 2^(−1/4) = 0.159 | – | write 2^(−1/4) = 0.84 |
| 41 | "0.57 fA/√Hz at 1 pA, 18 fA/√Hz at 1 nA" | no script | survey_TI §7.4 | add sqrt(2qI_G) to noise_theory.py |
| 41 | "matters only above about 100 kΩ" | no source; contradicts own 1 MΩ: e_n/i_n 55 kΩ at 1 nA, 1.75 MΩ at 1 pA | – | state criterion and gate current |
| 41 | "1–10 nA between 6 and 10 V (JFE150 Figs. 6-5 and 6-6 of SLPS732B)" | wrong citation: SLPS732B Fig. 6-6 is I_G vs V_GS; V_DS curve of JFE2140 is SLPS730B Fig. 6-6 | survey §1.1–1.2, §7.4 | "SLPS732B Fig. 6-5 (JFE150), SLPS730B Fig. 6-6 (JFE2140)" |
| 52 | "spread of 85 mV in V_TO, typical of the JFE150 lot" | no source: σ assumed in cmrr_mc.py; no lot data; no conversion from 0.6 V V_GS(off) range | cmrr_mc.py 17–18, 95; SLPS732B p. 5 | write conversion (600 mV/7 ≈ 86 mV?), call it σ, drop "typical of the lot" |
| 52 | "by tens of percent at 5 mA" | no equation/script | ΔI/I = 2ΔV_TO/(V_GS − V_TO) = 2·85/407 ≈ 42 % per σ | write it |
| 70 | "at constant total current, C_det/3" | citation lacks slide; MOSFET result | O'Connor 1997 slide 2; BNL ICFA95 Eq. (3) | cite slide; note basis |
| 70 | "beyond about 600 Ω … a single device" | rounding: Eq. (4) gives 663 Ω | make_figures.py | "about 660 Ω"; print 55 Ω and 663 Ω from a script |
| 90 | Fig. 1 stars "simulated noise" | hard-coded 1.07/0.41 (FE only), not 1.08/0.42 of summary/Table 2 | make_figures.py l. 139; curves_noise.npz | read from npz; caption "front end alone" |
| 90 | Fig. 1a FEMTO point at 2.0 | basis mismatch: axis differential, 2.0 single-ended; differential 3.0 | jfet_data COMMERCIAL; survey §3.1 | plot 3.0 |
| 102 | "gain 1 to 50 000, two first-order filters, 50 Ω output" | no page | manual printed p. 5; data sheet PDF p. 3; R438 on sheet 560_4F | cite |
| 124 | Table 1 LN model 1 kHz gain 50: 9.5 | rounding: 9.447 → 9.4 | sr560_chain.json noise.LN_50 | 9.4 |
| 130 | Table 1 HR model 1 kHz gain 1000: 9.5 | rounding: 9.447 → 9.4 | noise.HDR_1000 | 9.4 |
| 132 | "within about 30 % at most gains" | no script; exceptions: LN 5 −32 %, LN ≥100 +43 %, HR 10 +40 %, HR 1000 −37 %; 11 of 15 within | sr560_chain.json | compute; state exceptions |
| 132 | "corner of 5–15 kHz" | no citation | Vishay 70254 Rev. E p. 5 | cite |
| 134 | FE CMRR "102.5 dB at 1 kHz" | rounding: 102.554 → 102.6 | sr560_frontend.json cmrr_db_1k | 102.6 |
| 136 | "against the manual's 1 MHz" | no page | manual printed p. 5; data sheet PDF p. 3: 1.2 MHz typ | cite; mention 1.2 MHz |
| 136 | "specification of 100 dB up to 1 kHz" | no citation; conflicts with manual p. 5 ">90 dB to 1 kHz"; 100 dB is data sheet | data sheet PDF p. 3 | cite; note manual's 90 dB |
| 146 (242) | "1.28 nV/√Hz white" (1.8; "3.6 nV at 1 kHz") | no script; not reproducible: stated interpolation gives 1.25 and 3.44 | models.py 2N5564 comment; Vishay p. 5 | compute interpolation in script; cite p. 5 |
| 146 (222, 227) | "0.9", "0.33" differential, "0.64 per side" | Eq. (2) only; no script | – | print from noise_theory.py |
| 148 | "raise it tenfold" | no source; inconsistent with 15–25× elsewhere | chain_ac.json | "15–25 times" |
| 165 | Stahl PR-E3 "0.69 | 16.4 pF" | basis mismatch: 16.4 pF "at either input"; 0.69 "both channels connected" (≈33 pF); also in Fig. 1a | Stahl PR-E3 data sheet v3.12 p. 5 | 0.69 with ≈33 pF, or 1.05 with 16.4 pF |
| 170 | remembered unit "about 3 nV/√Hz" | recollection | – | label as remembered |
| 170 | "below 35 pF" | no page | 5307 manual PDF p. 21 | cite |
| 170 | "factor 2.3–3.7 … L by 6–10" | no script; 4/0.42 = 9.5; bases differ from l. 14 | – | "6–9.5"; align |
| 181 | "V_GS = 0 for Linear Systems, V_DS = 5 V for TI" | mismatch: LSK170, LSK489 quote C_iss at operating current; JFE2325 at 2 V | survey C13, §2.2–2.3, §1.3 | qualify per part |
| 184 | "about 6 V … 3–5 V keeps it in pA" | no citation | SLPS732B Fig. 6-5; SLPS730B Fig. 6-6 | cite |
| 185 (222) | "4 mV maximum, 10 µV/°C" | no citation; 10 µV/°C is max (1.7 typ) | SLPS730B p. 5 | cite; "max" |
| 196–212 (220 "5.9") | FOM column (17 values) | no script output: jfet_data.fom() never called; values correct | jfet_data.py | print Table 3 from script |
| 197 | BF862 "I_D 15 mA" | inferred (noise at V_GS = 0, I_DSS 10–25 mA) | survey_InterFET §2.1 | "≈ I_DSS (10–25 mA)" |
| 201 (229, 243) | JFE2325 "0.385 mA"; Table 4 RX 67.0 | mismatch: models.py calibrates at 0.325 mA (V_GS −80 mV) vs 4.3 nV "gate grounded" at ≈I_DSS 385 µA | models.py cal; jfet_calibration JFE2325.vgs; SLPS816A p. 5 | recalibrate at V_GS = 0, or explain |
| 203 | IF170 "C_iss 20", "10 Hz 1.72" | basis: 20 pF max (p. 2); 1.72 at 5 mA not 2 mA (p. 4) | survey_InterFET §1.7 | mark "max", "(5 mA)" |
| 205 (207) | IF9030 C_iss 60; IF4500 55 | basis: 60 max; 55 curve reading (table max 35) | survey §1.3–1.4 | mark |
| 209 | LSK389 "1.17 measured" | no page; A-weighted band incl. second stage | Cordell app note Rev. A4 Table 1 p. 5 | cite; state basis |
| 222 | Spinelli "0.9 nV/√Hz, DC–100 kHz" | no page/table | Table 1 p. 2 | cite |
| 222 | "rises above about 6 V" | no citation | SLPS730B Fig. 6-6 | cite |
| 225 | LSK489 "C_rss 1.5–2 pF" | no citation | LSK489 DS p. 2 (2 pF); Cordell app note p. 2 (1.5 pF) | cite |
| 227 | "reach the same 0.33 nV/√Hz differential" | basis: differential vs IF3601 per-device 0.34; one IF3601 per side gives 0.48 differential; "lower 1/f" unquantified (8.8 vs 15.3) | Table 3 | like with like; add 10 Hz figures |
| 233 | "thermal noise 8kTg_m/3" | no citation for ngspice | models.py docstring | cite ngspice manual |
| 241 | LSBF862 "RX 0 … 0.8 / 1.4 nV" | mismatch: model white 0.898 > 0.80 (RX clipped at 0); KF fitted assuming 0.80 → ≈1.46 at 10 Hz | jfet_calibration LSBF862.en_model_white | report achieved values and why |
| 249 | "grading exponent at 0.5" | no citation | models.py docstring | cite ngspice manual |

Most serious (A): input capacitance (C_P + C_Z unscripted); Stahl PR-E3 basis (~2× capacitance); "≤ 300 Ω" no criterion; 290 MHz; ±0.5–1 V LV; line 41 wrong citation and contradiction; 85 mV "typical of the lot"; SR560 inputs (2N5564 1.28/3.6 not reproducible; 100 dB vs manual's >90 dB; Table 1 9.5 → 9.4); Table 4 (LSBF862 white noise misses target; JFE2325 calibration current); smaller: 0.05 % resistors, 0.05 pF to 1 MHz, 2.3–2.8×/6–7× vs 2.3–3.7×/6–10×.
Notes (A): SR560 op-amp behavioural figures (OP37 "ADI data sheet Rev. E? typ.") have no archived data sheets; feed 1.1 nV/√Hz (l. 134) and 0.73–0.79 MHz (l. 136).


# Audit B: lines 253–583 (Sections 4.1–4.3.1), 79 numbers flagged in 59 rows (of about 630 checked)

| line | number, with context | problem | likely source | suggested fix |
|---|---|---|---|---|
| 275 | "giving 20 dB more headroom at the input" | no script, no equation (20·log10(100/10)) | gains 100 vs 10 (chain.allocate) | write expression or compute |
| 275 | "for 2.4 times the noise (Table 9)" | no script; gain/frequency unspecified | chain_noise.json: H_HR/H_LN 2.42 (gain 1000, 10 kHz), 2.34 (gain 100), 3.1 at 10 MHz | "2.3–2.5 in the white region, gains 100–1000"; compute ratio |
| 283 (T5) | g_m per JFET, L: 25.7 mS | no source | none (fe_gain_derived has H only; jfet_model_check 25.93 mS at V_DS 5 V) | archive L200 @j.xja1.j1[gm] |
| 293 (T5) | JFET capacitance per input 26 pF / 288 pF | no script (Eq. (2) in note) | 2×13 pF, 12×24 pF (jfet_calibration.json ciss_target; SLPS730B, SLPS732B Table 6.5) | compute N·C_iss in fe_closed_forms |
| 309 | "JFE2140s for DC–100 kHz" | no page/table | literature_notes C11: Table 1, p. 2 | add "Table 1, p. 2" |
| 330 | "1 % error … 110 µA … 55 mV … 152 mV" | no script | ε(N I_D + I_BS) R_F | compute |
| 330 | "V_BE (−2 mV/K) adds −0.1 % per kelvin" | no citation; archive −1.71 mV/K (H), −1.46..−1.47 (L) → −0.086 %/K | fe_closed_forms drift dVBE_dT_mV | use −1.7 mV/K, −0.09 %/K |
| 330 | "tens of millivolts of output per kelvin" | mismatch: archive 4.86 (H), 4.92 (L 6 V), 12.4 (L 2 V) mV/K | fe_closed_forms drift output_mV_per_K | "about 5 mV/K" |
| 330 | "a few percent … outputs volts away" | no source; 3 % → 0.17 V (H), 0.46 V (L) | – | quantify or drop "volts" |
| 343 | "0.05 % of 11 mA gives 2.8 mV … 28 µV" | no script; 0.05 % unstated assumption | ΔI R_F = 5.5 µA × 500 | state assumption; compute |
| 347 | "unity gain at 0.16 Hz", "16 Hz filter" | no script | 1 µS/1 µF, 1 kΩ/10 µF | compute servo block |
| 347 | "(2.7 V per volt for H)" | mismatch: R_F/R_T = 500/181.8 = 2.75 | frontend.py | 2.75 |
| 344, 347 | "below 1 Hz", "about 0.4 Hz with nearly 90°" | no script/equation (f_c = 2.75×0.159 = 0.44 Hz; PM = 90° − atan(0.44/16) = 88°) | – | write and compute |
| 349 | "between V_M + 1 V and V_M + 5 V" | mismatch for L: code clamps at V_M + V_RT + 3 V (V_M + 9 V for L); L's sink base at −8.10 V = V_M + 6.9 V | frontend.py BSNK; sink_power "L200 | 6 V" v_ctrl | "V_M + 1 V to V_M + V_RT + 3 V (V_M + 5 V for H, V_M + 9 V for L)" |
| 352 | "each adds 0.4 pA/√Hz" | no script (sqrt(4kT/100k) = 0.41) | – | compute |
| 355 | "1/(2π R_BS C_BS) ≈ 45 Hz" | no script | 45.5 Hz | compute |
| 355 | "NPN's base current (about 50 µA at 5 mA)" | no source; implies β = 100, part unnamed | MMBTH10 card (FE default cascode) | name part; cite h_FE/BF |
| 355 | "turns into 0.25 nV/√Hz at the input" | no script/equation/run | none | closed form or archived NPN-cascode run |
| 379 | "first two terms dominate, 0.93 and 0.41 … 0.33 and 0.20" | no source named; 0.93 is JFET term at 1 MHz; Table 6c says 0.94 (10 kHz); Eq. (2) gives 0.90 | curves_noise.npz H100_g_input JFETs 0.934 (1 MHz), 0.936 (10 kHz); L200 0.328/0.202 | state frequency and source |
| 384 | "Ng_m … 308 mS for L, Section 6.1" | no source; Section 6.1 gives neither | 35 mS ✓ (fe_gain_derived); none for L | archive L g_m; fix cross-reference |
| 386 | "their gain of 1000 with an R_A of a few ohms" | no page; source: R_A = 1 Ω | literature_notes C11: R_A 1 Ω, R_B 500 Ω, G_n 1001, pp. 4–6 | "G_n = 1001 with R_A = 1 Ω (pp. 4–6)" |
| 404 | "V_CE,min = 0.5 V" (Eq. 9b) | not stated as choice; no citation | MMBT3904/PZT3904 p. 2: V_CE(sat) ≤ 0.2 V (10 mA), ≤ 0.3 V (50 mA) | state as margin above V_CE(sat), cite p. 2 |
| 447 | "CM loop has 6.7 times the … gain" | no script (1/k_DM) | k = 0.1484 → 6.74 | compute in gain_options derived |
| 449 | "stable only at a noise gain of about 10" | no citation | SLOS265F p. 1 ("Stable at gains ≥10V/V"), §6.1 p. 21 | cite; add THS4021 PDF to opamp README |
| 449 | "β_CM was about 0.5" | no script; needs C_par ≈ 10.6 pF never computed | – | compute C_par (cascode C_gd at bias, THS4021 C_i 1.5 pF p. 7) |
| 449 | "1 V peak to peak at about 290 MHz" | mismatch: archive 1.03 V at 283 MHz; JSON lacks C_I/C_X (osc_check H100 0 today uses 9/5 pF) | osc_check.json H100_cnode0p; docstring "near 280 MHz" | 283 MHz; record C_I, C_X, C_node |
| 449 | "crossover at 452 MHz with −80° (Figure 9b)" | mismatch with figure: annotation 433 MHz, −76°; 452/−80.3° is first sweep point past crossing (Table 6) | curves_loop.npz out_H100_old_cm; make_figures.fig_loop_gain | one convention |
| 451 | "β_DM … about 0.02" | no script | 4/234 = 0.017 | compute |
| 451 | "falls from about 30 MHz" (Table 6b "halved") | first version's FE bandwidth not archived | da_compare_before_cnode.json ac_H100: 30.7/30.1 MHz (chain at gain 100) | cite that file |
| 451 | "1.50 against 1.07 … 0.51 against 0.41" | ambiguous (white floors vs 10 MHz); L 0.51 is from 2 V sinks; adopted L 0.504 | sink_power L200 6 V: 0.5038 / 0.4073; curves_noise L200 0.5054 | "1.50 at 10 MHz against a white floor of 1.07; 0.50 against 0.41" |
| 451 | "oscillated at 293 MHz with 1 V" | mismatch: 283 MHz | osc_check.json | 283 MHz |
| 459 (T6) | L, CM at op-amp output: 52° | rounding: 51.45° → 51° | curves_loop.npz; stability_corners L200 nominal | 51° |
| 466 | "8–10 dB at about 270 MHz" | mismatch: −180° crossing ≈ 251 MHz (H), ≈ 204 MHz (L) | curves_loop.npz out_H100_cm, out_L200_cm | "≈250 MHz (H), 205 MHz (L)"; store GM frequency |
| 472 | "needs a noise gain of about 10" | no citation | SLOS265F p. 1 | cite |
| 479 | "about 0.5, far above the 0.1 that the op amp tolerates" | as 449; 0.1 uncited | SLOS265F p. 1 | cite; give C_par |
| 482 | Eq. (10b) "1.6 GHz × 0.15 × 0.1 ≈ 24 MHz" | no citation; datasheet SLOS265F rev F p. 1 says 2 GHz GBW (p. 6: 290 MHz at G=10, 110 MHz at G=20); no script | TI_ths4021_datasheet.pdf | cite 2 GHz (30 MHz) or measure model GBW; compute |
| 488 | "0.5 (6 dB peak) common minimum" | no citation | – | cite a control text or state as rule |
| 494 (T6a) | Nominal, L CM 52° | rounding 51.45 | stability_corners.json | 51° |
| 495 (T6a) | C_node ×0.7, L CM 50° | rounding 49.47 | same | 49° |
| 496 (T6a) | C_node ×1.3, L CM 51° | rounding 50.49 | same | 50° |
| 497 (T6a) | C_I×1.1/C_X×0.9: H×100 DM 17 dB, H×10 CM 59° | rounding 16.45 dB, 58.46° | same | 16 dB, 58° |
| 503 | "1.3–1.5 times … 270–330 pF … 560–680 pF" | mismatch: 1.3–1.5× → 286–330 / 611–705 pF; E12 values span 1.23–1.5× (H), 1.19–1.45× (L) | ×1.3 in Table 6a; comp_search_H100 S14_D4_CN330; comp_search_L200 S30_D14_CN680 | "about 1.2–1.5× (E12 …)"; cite runs |
| 513 (T6b) | "bandwidth halved" | relative to unsourced 30 MHz | as 451 | as 451 |
| 514 (T6b) | 330 pF: "slightly more above 1 MHz" | no noise run for 330 pF | – | run or mark as Eq. (9) estimate |
| 517 (T6b) | ×20 R_G: 3.15 / 1.45 / 2.14 | rounding 1.4448 → 1.44 | fe_gain_options.json | 1.44 |
| 518 (T6b) | ×30 R_G: "+20 % white noise" | rounding 20.5 % → 21 % | fe_gain_derived white rise 0.2051 | +21 % |
| 525 | "rises from 1.07 to 1.45" | rounding 1.4448 | fe_gain_options | 1.44 |
| 529 | "so is the bandwidth, 16 MHz" | mismatch with "unchanged": 15.06 → 15.92 MHz | fe_gain_options f3db | "16 against 15 MHz" |
| 535 | "125 mA at 12 V" | 12 V uncited (125 mA ✓) | SLOS265F p. 7: V_O ±12 V min at R_L 250 Ω | cite p. 7 |
| 542 (T6c) | R_G, gain 100: 0.41 | rounding 0.4049 → 0.40 | fe_gain_options | 0.40 |
| 544 (T6c) | op amps, gain 20 (R_G): 0.21 | rounding 0.2049 → 0.20 | same | 0.20 |
| 546 (T6c) | R_F, gain 10: 0.41 | rounding 0.4049 → 0.40 | same | 0.40 |
| 548 (T6c) | total 10 kHz, gain 20 (R_G): 1.45 | rounding 1.4448 → 1.44 | same | 1.44 |
| 567 | "unity-gain-stable op amp of 100–200 MHz (THS4031, LM7171)" | mismatch: LM7171 stable only for gains ≥ +2 (SNOS760D p. 1); 100–200 MHz uncited | THS4031 120 MHz (SLOS224L p. 1); LM7171 160/200 MHz (SNOS760D p. 5); signal_chain_parts.md A1 | cite; drop LM7171 or β ≤ 0.5 |
| 567 | "only 15–30 MHz … a few MHz" | no script; "a few MHz" unquantified | – | compute; quantify |
| 573 | "1 V at 290 MHz" | mismatch: 283 MHz | osc_check.json | 283 MHz |
| 575 | "phase at 200–400 MHz decides the CM margin" | approximate, no source | crossings 204–251 MHz; oscillations 270/283 MHz; first-version crossover 433–452 MHz | cite or "about 200–300 MHz" |
| 579 | "10:1 passive probe adds 10 pF" | no citation | – | cite probe datasheet or say "typically" |
| 581 | "the 200–400 MHz mode" | as 575 | | |

Most serious: (1) line 349 servo clamp wrong for L; (2) Eq. (10b) 1.6 GHz uncited, datasheet says 2 GHz, no script; (3) oscillation 290/293 vs archived 283 MHz, run lacks C_I/C_X; (4) LM7171 called unity-gain stable, datasheet says ≥ +2; (5) V_BE −2 mV/K vs archived −1.7; "tens of mV/K" vs ≈5 mV/K; (6) unsourced L g_m (25.7 mS), Ng_m (308 mS) with wrong Section 6.1 cross-reference, NPN-cascode figures, β_CM ≈ 0.5 (C_par never computed); (7) "about 270 MHz" vs 204–251 MHz, and Figure 9b annotation 433 MHz/−76° vs text 452/−80°.

Other: THS4021 PDF not listed in refs/datasheets/opamp/README.md; fe_closed_forms.py labels C_tab/CMRR as (9b) while the note has (9c); L results behind Tables 6/6a etc. predate the 6 V sink switch (sink_power shows same margins/bandwidth); line 390: 11.1/61.9 mA are R_T currents incl. base current (source node carries ≈11.03 mA for H); Eq. (10b) premise assumes equalized loops but adopted H100 has D/S = 0.29 vs k = 0.15 (outer crossovers 8.9 MHz DM, 21 MHz CM).

# Audit C: lines 584–767 (Sections 4.4–5), 112 numbers flagged in 69 rows plus about 20 ratios (of about 330)

| line | number, with context | problem | likely source | suggested fix |
|---|---|---|---|---|
| 586 | "0.05 pF between 1 kHz and 1 MHz" (bare H) | holds within +20 % only 0.9–350 kHz; 0.057 pF at 1 kHz, 0.114 pF at 1 MHz | curves_zin.npz H100_dm_* | "0.05 pF from 1 kHz to about 300 kHz (0.11 pF at 1 MHz)"; also l. 11; collect_curves zin prints |
| 586 | "L's is 0.33 pF against 288 pF" | 0.33 only 0.9–280 kHz; 0.38 at 1 kHz, 0.99 pF at 1 MHz | curves_zin L200_dm_* | as above |
| 586 | "the JFETs' own 26 pF" / "288 pF" | no equation/script: 2×13, 12×24 pF; hard-coded lines in make_figures | SLPS730B §6.5 p. 5 (13 pF); SLPS732B §6.5 p. 5 (24 pF) | write N·C_iss with citations; compute |
| 586 | "above a few MHz it rises" | rise starts at a few hundred kHz (H 0.066 pF at 0.5 MHz; L 0.49 pF at 0.5 MHz, 0.99 at 1 MHz) | curves_zin | "above a few hundred kilohertz" |
| 595 | "−1.1 kΩ at its minimum near 13 MHz for H" | grid min −1.049 kΩ at 12.6 MHz (−1.04 parabolic); no script; L −110 Ω correct (−109.8) | curves_zin H100_dm_z | "−1.0 kΩ"; print minima |
| 595 | "1 kΩ source by 16 dB at 2.6 MHz on L (Figure 10c)" | value correct, figure reference wrong (Fig. 10c plots L only with 50 Ω) | collect_curves_log.txt "L200 bare 1k: peak 16.0 dB at 2.63 MHz"; curves_sources.npz | cite log, or add curve to Fig. 10c |
| 597 | "connector's and relay's C_P of 10 and 30 pF" | no source: modelling allowance (chain.py INPUT_NET) worded as physical | relay sheets in refs/datasheets/relays/ not cited | call it assumed allowance, or cite |
| 597 | "no source from 50 Ω to 1 MΩ peaks … 0.6 dB" | only 50 Ω, 1 kΩ, 1 MΩ simulated (largest 0.6 dB: H, 1 kΩ, 5.0 MHz) | collect_curves_log "network" | "none of the three sources", or sweep R_S |
| 597 | "about 20 pF for H and 250 pF for L" | no equation/script: C_P + C_Z (valid below 7.2 and 15 MHz) | chain.py INPUT_NET | write C_in ≈ C_P + C_Z; or input-impedance run with network |
| 597 | "25 pF for SR560 and 35 pF for NF 5307" | no citation; NF is a maximum (< 35 pF, 33 pF typ) | SR560 manual spec chart PDF p. 9; NF_5307_specifications_EN.pdf, manual PDF p. 21 | cite; "< 35 pF (33 typ)" |
| 649 | Fig. 11 "at a total gain of 1000" | MISMATCH: drawn Setting("H100", a3=0.5, a4=0.5, a5=0.4) gives 100×5×5×2 = 5000; gain 1000 is (1, 0.1, 0.2) | make_schematics.py l. 265; chain.Setting.gain | caption 5000, or draw gain-1000 setting |
| 651 | "LM7171 (A grade, 4100 V/µs, 200 MHz)" | no citation; A grade unity-gain bandwidth 160 MHz (200 is B grade); 4100 correct | SNOS760D §5.5 p. 5; p. 1 | "A grade: 4100 V/µs, 160 MHz (SNOS760D §5.5 p. 5)" |
| 651 | "1.3 % … 0.012 % … 133 V/µs" "(Section 6.4)" | values correct, section wrong (Table 14 in 6.5) | da_compare.json (1.306 %, 0.0120 %); large_signal_THS4031.json slew 133.1 | "Section 6.5, Table 14" |
| 652 | "20 pF of relay and layout capacitance" | no source; assumed in chain.py stage_filter | none | state as allowance, or cite |
| 653 | "tapped through a 1 Ω switch" | no source; lower than archived switches (TMUX6219/7219: 2.1 Ω typ, 2.9 Ω max, 148 pF on) | refs/datasheets/signal_chain_parts.md | mark idealised, or use chosen switch's values |
| 654 | "±10 V into high impedance and ±5 V into 50 Ω" | no source: every deck uses 1 MΩ load; 50 Ω never simulated; THS3091 swing/current not cited | large_signal.json overload v_during 11.36 V; SLOS423K §7.5 | cite, or 50 Ω-load transient |
| 656 | "14 pA/√Hz … dominates: 24.6 nV/√Hz white" | totals correct (chain_noise H_LN_1: 24.6, 650.6) but no per-stage breakdown archived; i_n·R_F ≈ 1/3 of white power (estimate); dominates only at 1 Hz | chain_noise.json | archive breakdown, or "largest single term" |
| 660 | "match to 4 mV at most (10 µV/°C)" | no citation | SLPS730B §6.5 p. 5 | cite |
| 660 | "Monte Carlo of Section 6.3 … 3.4 V rms … 3.4 mV" | values correct, section wrong (6.4) | cmrr_mc.json H100 vout_dc_rms 3.360 V | "Section 6.4" |
| 660 | "0.85 mV of V_TO and 1 % of β mismatch within a dual" | text disagrees with code: cmrr_mc.py l. 92 adds σ 0.85 mV and 1 % to each half → difference σ 1.2 mV and 1.4 %; neither derived from data sheet (1 mV typ/4 mV max; I_DSS ratio 0.95–1.05); β term ≈ 3 mV of 3.4 mV | cmrr_mc.py docstring 14–16, code 92; SLPS730B p. 5 | describe per-half σ and derive, or change code to per-pair |
| 660 | "85 mV spread of V_TO … V_GS(off) range implies" | no equation/citation: SLPS732B p. 5: −1.5 to −0.9 V; 85 mV ≈ 0.6 V/7 (±3.5σ) unstated | cmrr_mc.py l. 95 | σ = ΔV_GS(off)/7 with citation |
| 660 | "mean V_GS differ by about 35 mV rms" | no equation/script: 85 × sqrt(2/12) = 34.7 mV | – | σ_Δ = σ_VTO sqrt(2/N) |
| 660 | "into saturation … one trial … no DC solution" | no archived output; unsorted case not in cmrr_mc.py (docstring note only) | cmrr_mc.py 17–21, 165 | add unsorted L case, archive |
| 660 | "2.3 V rms … (2.3 mV at the input)" | 2.260 V/1005 = 2.25 mV → 2.2 mV; rests on unstated 2 % β spread in bin | cmrr_mc.json L200 | "2.2 mV"; state assumptions |
| 662 | H: "±100 µA, ±2.9 mV … 1.4 µV steps … 0.01 nV/√Hz" | no script; inconsistent with Eq. (9) weight 1/(Ng_m) + R_F/G: with 34 Ω (gain 100) ±3.4 mV, 1.7 µV, 0.014 nV/√Hz; with 79 Ω (gain 10) ±7.9 mV, 3.9 µV, 0.032 nV/√Hz | Ng_m 34.5 mS; R_F 500 Ω | trim block in fe_closed_forms: Δv = ΔI (1/(Ng_m) + R_F/G), step 2Δv/2^12, sqrt(4kT/R) × weight; both gains |
| 662 | L: "10 kΩ gives ±1 mA, ±3.2 mV" | same: 3.25 + 1.24 Ω → ±4.5 mV | Ng_m 308 mS | as above |
| 676 | "drift apart by at most 10 µV/°C" | no citation | SLPS730B §6.5 p. 5 | cite |
| 692 | "LT3045 figures from ADI's product page, its data sheet could not be downloaded" (2 nV/√Hz, 0.8 µV, 76 dB, 260 mV) | values correct, claim wrong: refs/literature/ADI_2022_LT3045_Datasheet_RevD.pdf is valid; p. 1 shows all four (official LT3094 Rev. B archived beside it) | LT3045 Rev. D p. 1 | cite Rev. D p. 1; fix regulators README and references |
| 694 | "2.2 nV/√Hz at 10 kHz (C_SET = 4.7 µF)" | wrong condition: LT3094 Rev 0 p. 4: 2.2 nV/√Hz with C_SET = 0.47 µF; 70 nV and 0.8 µV are with 4.7 µF | LT3094_Rev0_mirror_xdevs.pdf p. 4 | attach 4.7 µF to those two only |
| 698 | "L is better by 10–20 dB" | no script; 8.9–21.6 dB | large_signal.json H100 vs L1000 psrr | "9–22 dB", scripted |
| 698 | "70 nV at 10 Hz becomes 0.6 pV/√Hz" | no equation/script; PSRR not simulated below 100 Hz; on negative rail (100.7 dB) 0.65 pV | large_signal psrr at 100 Hz | e_in = e_reg 10^(−PSRR/20) per rail |
| 698 | "about 155 dB at 1 MHz" | no script; mixes rails: positive 76 + 80.6 = 156.6 dB; negative 74 + 86.0 = 160.0 dB | large_signal.json; LT3094 p. 5; LT3045 Rev. D p. 1 | give per-rail sums |
| 698 | "draws 120 mA … through its drain resistors" | no equation/script: 2 × 6 V/100 Ω | fe_closed_forms | write/add |
| 698 | "about 200 mA from each rail in all" | NO SOURCE | none | store supply currents from L chain OP |
| 698 | "dissipates up to about 0.6 W" | derived from unsourced 200 mA | – | compute from archived currents |
| 698 | "copper area of a few square centimetres" | no citation | LT3094 Rev 0 p. 3: θ_JA 33 °C/W MSOP | cite p. 3 (0.6 W × 33 = 20 K) |
| 702 | "a decompensated 1.6 GHz amplifier" | MISMATCH: SLOS265F p. 1 gives 2 GHz | TI_ths4021_datasheet.pdf p. 1 | "2 GHz (SLOS265F p. 1)" |
| 702 | "with 1.5 nV/√Hz" | no citation; p. 1 and §5.6 (SOIC, p. 6) give 1.2; 1.5 is §5.7 (DGN, p. 8); model uses 1.2 | SLOS265F pp. 1, 6, 8 | "1.2 nV/√Hz (1.5 in DGN)" |
| 706 | "50–100 MHz on ±15 V (OPA2810-class)" | MISMATCH: OPA2810 70 MHz on 4.75–27 V (≤ ±13.5 V) | SBOS789C p. 1 | cite; ±12 V, or name a ±15 V part |
| 706 | "(OPA1612-class, 40 MHz)" | no citation | SBOS450C p. 1 | cite |
| 706 | "H gain 100 … 2.70 to 2.43 … 7.9 to 7.0" | no equation/script; sqrt(e² − e_op²) gives 2.448 and 7.058 | curves_noise H100_total, H100_g_loop op amps | write and script; "2.45", "7.1" |
| 706 | "H gain 10 … 3.8 to 2.9 … 10.6 to 7.2" | no equation/script (2.90, 7.23 correct) | curves_noise H10_* | script |
| 706 | "L … 0.83 to 0.77 … 2.3 to 2.1" | no script; 0.7755 → 0.78 | curves_noise L200_* | "0.78" |
| 706 | "1.8 against 2.4 nV/√Hz at 10 Hz per device" | no citation; different currents (5 vs 2 mA); JFE150 at 2 mA 1.6 | SLPS732B p. 5; SLPS730B p. 5 | cite; state currents |
| 706 | "IF3601-class … 0.6 nV/√Hz at 10 Hz" | no citation | InterFET IF35076.R01 p. 3 (survey_InterFET §1.1) | cite |
| 721 | "Monte Carlo (12 trials per case)" | one-class cases ran 6 | cmrr_mc.json trials | "12 (6 for one-class)" |
| 722 | "1 and 10 Vpp sines from 1 kHz to 10 MHz" | 10 Vpp only up to 1 MHz | large_signal.json thd | "1 Vpp to 10 MHz, 10 Vpp to 1 MHz" |
| 742 | "0.2e-18: 1.2 nV/√Hz at 10 Hz, 2 mA" | no archived output for published card (JSON stores refit); Eq. (1) gives 1.21 | survey C9; jfet_calibration.json | store published card's 10 Hz value |
| 742–760 | Table 7 "Error" ratios (14×, 0.66×, … 0.48×) and text repeats | ratios computed by no script; correct to rounding (8.648/13 = 0.665 → 0.67) | jfet_calibration.json | check script writes Error column |
| 744–745 | "1.8 nV at 10 Hz, 5 mA"; "24 pF, 4.5 pF (Fig. 6-12)" | JFE150 data sheet number never given | jfet_calibration JFE150.src: SLPS732B §6.5 p. 5, Fig. 6-12 p. 7 | add |
| 744 | "consistent (7 %)" | basis/script: KF ratio 3.495/3.25 = +7.5 % | jfet_calibration | "KF +7.5 %", printed by models.py |
| 746 | "8.75e-17: about 9 nV/√Hz at 10 Hz" | no script output (Eq. (1) 9.07; only README/comment) | README_InterFET_NXP_others l. 84 | store in JSON |
| 746–747 | "1.4 typ, 4.0 max"; "11.5 pF, 3.5 pF" | no citation | Linear Systems Doc 201195 Rev A2 p. 2 | add |
| 748 | "67860f = 6.786e-11"; "6.786e-002f"; "Vishay's curve" | no citations; LTspice card not archived, version not stated | LinearSystems/2N5564/Copy_2N5564_NJF.txt.pdf; jfet_calibration 2N5564.src (Vishay 70254 Rev. E p. 5) | cite; state LTspice version |
| 749 | "about 0.6 µV/√Hz gate-referred at 10 kHz, 11 mA" | no script (Eq. (1) 0.585; only sink_options docstring) | jfet_calibration J310.card | compute in script |
| 749, 762 | "(Section 6.1, where it was dropped)" | wrong reference: 6.1 never mentions J310 | sink_options docstring | add sentence or cite script |
| 750 | "NLEV = 3, GDSNOI = 5–8" | no source; cards not archived; only LSK170A has Gdsnoi 8 | README_TI_LIS l. 27–28 | quote cards (cite library and version) |
| 750, 762 | "ngspice 1.41 vs 0.86 nV/√Hz" | no archived run; unclear which has NLEV/GDSNOI | none | add with/without check |
| 751–756 | op-amp "Model gives": 18.2/293, 22.2/300, 37/317, 1.5 pA, 4.1 nV | NO ARCHIVED SCRIPT: decks only in sim/runs/checks/; caption credits models.py (comments only); recomputing: 18.2/293, 22.2/300, 36.9/318, 1.57 pA | sim/runs/checks/*/noise.txt | script two-gain check → sim/results; 1.5 → 1.6 |
| 753 | "−37 dBc at 1 Vpp (in S2)" | h3 0.01297 = −37.7 → −38 | da_compare.json | "−38 dBc" |
| 753 | "about 20 dB too high" | no equation: −37.7 vs about −52 (Fig. 5-15) is 14 dB at different amplitudes; HD3 ∝ V² gives about 26 dB | SLOS224L Fig. 5-15 p. 12 | state scaling, compute |
| 755 | "14 pA/√Hz (Sec. 6.5)" | wrong citation: SLOS423K §7.5 p. 6 | THS3091 p. 6 | "§7.5, p. 6" (also models.py) |
| 756 | "8.5 nV (A grade); 43 nV (Fig. 5-16)" | incomplete; Fig. 5-16 at ±5 V, read by eye | SNOS760D §5.5 p. 5; Fig. 5-16 p. 10 | add |
| 758 | "exponent of 0.5 at 5 V" | no citation for ngspice | ngspice manual JFET level 1 | cite |
| 760 | "corner near 100 kHz instead of about 1 kHz" | no equation/script: f_c = f0 (i_n(f0)/i_n,w)² ≈ 95 kHz and 1 kHz | check decks; SLOS265F Fig. 5-12 | write and script |
| 760 | "H front end showed 11.3 nV/√Hz at 10 Hz" | NO ARCHIVED RUN with published model | none | archive uncorrected-model run |
| 760 | "too high by a factor of 1.8" | NO ARCHIVED RUN | none | same |
| 762 | "1/f corner … megahertz range" | too low: Eq. (1) gives 43 nV at 1 MHz and corner near 1.1 GHz | jfet_calibration 2N5564 | "near 1 GHz", scripted |
| 762 | "61 nV/√Hz at 10 kHz" (J310 sink) | no archived run (sink_options.json no J310) | sink_options docstring | add case or drop |
| 762 | "NXP's old BF862 model, 8.75e-17" | NXP file not archived, only transcribed | README_InterFET_NXP_others l. 16, 26 | cite NXP file and revision |

Most serious (C): (1) Fig. 11 caption gain 1000 vs drawn 5000; (2) offset trim uses only 1/(Ng_m), contrary to Eq. (9): ±3.4 mV (gain 100), ±7.9 mV (gain 10), ±4.5 mV (L); (3) unarchived: Table 7 op-amp model values, 11.3 nV and ×1.8, LSK389 1.41/0.86, J310 61 nV, unsorted JFE150 MC; Table 7 caption wrongly credits models.py; (4) data sheet mismatches: THS4021 1.6 GHz → 2 GHz, 1.5 → 1.2 nV; LM7171A 200 → 160 MHz; OPA2810 not ±15 V; THS3091 "Sec. 6.5" → §7.5; LT3094 2.2 nV is with C_SET 0.47 µF; (5) LT3045 Rev. D is archived; (6) §4.6 MC: per-half σ (1.2 mV, 1.4 % within a dual), not derived; 1 % β sets most of the 3.4 mV; "Section 6.3" → 6.4; (7) §4.8 projections unscripted, 2.43/7.0/0.77 → 2.45/7.1/0.78; (8) input admittance claims (0.05/0.33 pF only to ≈300 kHz; −1.1 → −1.0 kΩ; L 1 kΩ not in Fig. 10c); (9) power (200 mA, 0.6 W, copper area, 155 dB mixes rails); (10) 2N5564 "megahertz range" → about 1 GHz.
Other (C): opamp README lacks TI_ths4021_datasheet.pdf; LM7171 data sheet has input current-noise curve (Fig. 5-17 p. 10) but models.py says none (corrected model lacks that 1/f term); LT3045 output range ends at 15 V (Rev. D p. 1): +15 V from 100 µA × 150 kΩ at the limit, ±1 % SET current allows 15.15 V. Confirmed correct: drift numbers 671–688; pitfall paragraph 725; PSRR ranges 698; LT3094 values vs Rev. 0 pp. 1, 4–5; source peaking 595; 3.36/2.26 V offsets; S2 distortion/slew 651; Table 7 JFET capacitances and KF; vendor KF values; data sheet values with figure citations; MMBT3904 E_G 1.17, X_TI 3.

# Audit D: lines 768–1091 (Sections 6, 7, appendix), about 150 flagged in 79 rows (of about 780); about 30 outright mismatches; systematic double rounding (0.4049 → 0.405 → 0.41) in Tables 8, 8a, 10, 13

| line | number, with context | problem | likely source | suggested fix |
|---|---|---|---|---|
| 776 | 7.91 Total H gain 100 1 Hz | 7.9048 → 7.90 | curves_noise.npz H100_total | 7.90 |
| 778, 779 | 0.41 R_G H gain 100 at 1 kHz and 1 MHz | 0.4049 → 0.40 | H100_g_R_G | 0.40 |
| 781 | 3.81 Total H gain 10 10 Hz | 3.8045 → 3.80; Table 8a has 3.80 | H10_total; sink_options en["10"] | 3.80 |
| 782 | 0.41 R_F H gain 10 1 kHz | 0.4049 → 0.40 | H10_g_R_F | 0.40 |
| 784 | 2.34 Total L 1 Hz | 2.3350 → 2.33 | L200_total | 2.33 |
| 793 | "0.93 … 0.33 as Eq. (2) predicts … 0.9 … 0.8" | no citation for 0.9/0.8; arithmetic gives 0.90 and 0.327, not 0.93 | SLPS730B p. 1 (0.9 at 5 mA); SLPS732B p. 5 Table 6.5 (0.8 at 5 mA) | cite; "= 0.90 and 0.33"; model gives 0.93; compute |
| 795 | "0.79 … second-largest after R_G" | mismatch: at 1 kHz JFETs (0.96) larger → sinks third; at 10 Hz op amps (2.47), JFETs (2.40) larger | curves_noise H10 groups | "largest after R_G and the JFETs" (also sink_options docstring) |
| 801 | V_T = kT/q = 25.9 mV | T not stated | fe_closed_forms (300.15 K) | "at 300.15 K (ngspice 27 °C)" |
| 823 | "with the THS4031 in S2 the high-reserve figures are 2.0 nV/√Hz" | NO SOURCE: no H_HR 100–1000 run with THS4031 (da_compare runs only H_HR 10 and H_LN 100); repeated l. 857, 979 | none | add H_HR 100/1000 to da_compare noise loop, or delete |
| 829, 843 | "floor falls to 1.45" (R_F 250) | 1.4448 → 1.44 | sink_options RF250 en["10000.0"] | 1.44 |
| 835 | "(0.66 / 0.44)" adopted R_T part | 0.6547 → 0.65 (0.66 is 10 Hz) | split.R_T["10000"] | 0.65 |
| 838 | −12.9 V_CM,min BC817-25 2 V | −12.845 → −12.8 | op.vcm_min | −12.8 |
| 840 | "(0.39 / 0.23)" BC 6 V R_T part | 0.3847 → 0.38 | split.R_T | 0.38 |
| 842 | "1.07" gain-100 cell of no-sink row | no script | sqrt(1.0708² − 0.0788²) = 1.068 | add to fe_closed_forms |
| 852 | 2.84 10 Hz H gains 1000–50000 | 2.840 at 1000; 2.832 at 10000/50000 | chain_noise H_LN_* | "2.83–2.84" |
| 853 | "9.5" (10 Hz), "2.77" (1 kHz) H_HR | gain 100: 9.63/2.779; gain 1000: 9.41/2.760 | H_HR_100, H_HR_1000 | "9.4–9.6", "2.76–2.78" |
| 855 | 0.54 10 MHz L 1000–100000 | 0.5453 at 1000 | L_1000 | "0.54–0.55" |
| 857 | "20 dB more input headroom" | no equation/script | 20 log10(100/10) | write |
| 857 | "LM7171's 8.5 nV/√Hz" | no citation | SNOS760D p. 5 §5.5 (A grade, 10 kHz) | cite |
| 857 | "THS4031 in S2 2.0 nV/√Hz" | no source (l. 823) | | |
| 861 | "H for sources above about 300 Ω and L below" | no criterion; Table 10 contradicts at 10 Hz and 1 kHz (L lower NF up to 10 kΩ; at 1 kΩ, 1 kHz: 0.05 vs 0.31 dB); crossover 300 Ω–1 kΩ only at 1 MHz | noise_vs_source.json | state criterion or quote crossover per frequency |
| 861 | "With 1 MΩ, both attenuated by 20 dB at 1 MHz" | MISMATCH: archived 41.9 dB (H), 63.9 dB (L) at 1 MHz; H −21.9 dB at 100 kHz | curves_sources.npz H100_network_1Meg_h, L200_network_1Meg_h | "about 42 dB (H) and 64 dB (L)" |
| 869 | 2.4 H 1 MHz 100 Ω | 2.349 → 2.3 | noise_vs_source.json | 2.3 |
| 873 | 18.9 H 10 MHz 100 kΩ | 18.849 → 18.8 | same | 18.8 |
| 878 | "SR560's 4 nV/√Hz" (Fig. 13 caption) | no citation | manual Rev. 2.8 printed p. 5 (PDF p. 9); data sheet PDF p. 3 | cite |
| 882, 889 | SR560 row Table 11: 0.73–0.79 MHz, −4.2 to −4.8 dB, peaking none | wrong script named (caption cites chain.py ac); peaking not stored | sr560_chain.json ac; sr560_chain_ac_*.npz | cite sr560_chain.py; store peak_db |
| 886 | 25.1–25.2 MHz, −0.40 dB (H FE ×10) | 25.046 MHz at gain 1; −0.402 to −0.407 dB | chain_ac H_LN_1, H_HR_1 | "25.0–25.2 MHz", "−0.40 to −0.41 dB" |
| 891 | "later stages reach beyond 100 MHz" | no source | none | stage-by-stage AC run in chain.py |
| 899 | "over 12 trials per case" | one-class cases ran 6 (nt = max(trials // 2, 2)) | cmrr_mc.json *_only_* | "12 (6 for one-class runs)" |
| 901 | "0.05 % σ (0.1 % parts) … 0.005 % σ" | not labelled as assumptions | cmrr_mc.py docstring | state as assumptions |
| 902 | "C_I, C_X and C_node with 1 % σ" | MISMATCH: perturb() scales only CIA/CIB/CXA/CXB; C_node never varied | cmrr_mc.py | remove C_node or add and rerun |
| 904 | "JFE2140 … 0.85 mV of V_TO and 1 % of β" | no citation; 0.85 mV derived σ without derivation; data sheet no β matching (only I_DSS1/I_DSS2 0.95–1.05) | SLPS730B p. 5 (ΔV_GS 1 mV typ, 4 mV max) | cite; derive σ (0.85·√2·√(2/π) = 0.96 mV mean |ΔV_GS|); label 1 % as assumption (also l. 660) |
| 905 | "cascodes with 50 mV and 5 %" | not labelled assumption | cmrr_mc.py | label or cite |
| 909, 936 | "median of 12 trials" (Table 12, Fig. 15) | rows 920–923 and Fig. 15c used 6 trials | cmrr_mc.json | state |
| 925 | SR560 spec "100, 100, 80, 60, 40" | no citation; manual p. 5 ">90 dB to 1 kHz", data sheet PDF p. 3 100 dB; 80/60/40 extrapolated without equation | refs/benchmark/SRS_SR560_datasheet.pdf p. 3 | cite; write 100 − 20 log10(f/1 kHz); mention manual's 90 dB |
| 926 | NF 5307 "136 (100 Hz), 118, 100, 86" | imprecise citation | NF web page Fig. 46 (NF_5307_datasheet_fig46.jpg), read by eye | cite figure |
| 930 | "about 51 dB at 1 MHz" | no script; ΔC not stated (needs ΔC = √2·2.5 %·250 pF = 8.8 pF rms) | – | write ΔC; median |ΔC| = 0.674σ gives 54.6 dB ≈ 55 dB median |
| 930 | "L recovers 24 dB at 1 MHz" | no script (84 − 60) | cmrr_mc.json | write |
| 931 | "both front ends sit at 106–114 dB" | imprecise: H 114, L 108, H×10 104; 106 is H JFET-only | cmrr_mc.json | "108 (L) and 114 (H)" |
| 931 | "−0.32 ΔV", "45 Hz corner", "a third" | no script (3.5k/10.9k = 0.321; 45.5 Hz) | Table at l. 286 | add to fe_closed_forms |
| 931 | "106 to 138 dB at 10 Hz … 112 to 138 dB at 100 Hz" (4 trials) | NO SCRIPT: cmrr_mc.py has no R_UP-replacement option; not stored; archived decks reproduce (106.2 → 138.0, 111.8 → 137.9) | sim/runs/cmrr_mc/test_rup_*/*/ac.txt | add case to cmrr_mc.py |
| 932 | "cost 13 dB at 1 kHz (111 dB)" | no script (124 − 111) | H100_discrete | write |
| 940 | Table 13 caption sources | incomplete: L 10 V step in large_signal_L1000_step.json, H recovery in large_signal_THS4031.json, 6 V PSRR in sink_power.json | – | name all |
| 946 | 0.024 % L 1 MHz 10 Vpp | 0.02345 % → 0.023 % | large_signal.json | 0.023 % |
| 947 | 0.0078 % L 10 MHz 1 Vpp | matches JSON, but earlier run with same options gave 0.0396 % (H3 −68 dBc); difference unexplained | large_signal_log_L1000.txt vs large_signal_log_2.txt | document change |
| 949 | L 10 V step "34 ns, 4.9 %, 106/164 ns, 275 V/µs" | NO SCRIPT writes large_signal_L1000_step.json; log prints "slew nan V/us" | large_signal_L1000_step.json | large_signal.py writes it (fix slew for repeated time points) |
| 950 | "0.19 µs (THS4031 in S2)" | no script writes large_signal_THS4031.json; reproduces from npz (0.193 µs) | overload_curves_H100_THS4031.npz | compute in overload_detail.py |
| 953 | "312 V/µs/(π × 10 V) ≈ 10 MHz" | no script (9.93 MHz) | – | add |
| 953 | "9 % overshoot comes from the chain, not the front end" | no source (no FE step archived) | – | store FE step run |
| 953 | "numerical floor … about −110 dBc (0.0003 %)" | no source; two runs (l. 947) differ by 14 dB | – | archive floor test |
| 957 | "undershoots by 1.3 V for about 0.1 µs" | min −1.385 V; beyond −0.1 V from 82 to 115 ns | overload_curves.npz L1000_v(out) | 1.4 V; compute |
| 958 | "swing through about −1.9 and +2.6 V" | MISMATCH: oa min −2.15 V, ob max +2.88 V (−2.50/+2.53 V from rest) | overload_curves_H100_THS4031.npz | correct |
| 958, 960 | "+13.4/−13.0 V, 26.4, 11.4 V, 12 mV/0.2 µs, 0.19 µs, 85 ns, +23/−8 mV, 8.99→8.56/9.13 V, +0.23/+0.35/−0.12 V" | no script (agree with npz; run_h_ths4031 only saves curves) | npz | add extraction, store JSON |
| 960 | "+0.36 V that would forward-bias a gate" | 0.355 V is |V_GS| at rest; a 0.36 V change only brings junction to zero bias; uncited | fe_closed_forms headroom.H100.V_GS | reword, cite |
| 960 | "up to 0.8 mA per side" | no script; disagrees with own ΔV = ΔI·R_D: 0.43 V/600 Ω = 0.72 mA (g_m·ΔV_GS gives 0.81) | npz; GM_SIDE | choose one, compute |
| 960 | "about 0.12 V/s"; "a few microvolts" | equation not written (1 µS into 1 µF; 2.4 µV) | – | write |
| 964 | "about ten times full scale … forward voltage"; "tenfold run stopped" | no equation; tenfold run not archived (only large_signal.py docstring) | – | ΔV_GS ≈ [V_in − 26.4 V·R_G/(2R_F + R_G)]/2 ≈ 0.37 V |
| 965, 966 | "about 0.12 V … 0.3 V … 0.4 s"; "3.5 ms" | no equation/script (0.12 × 2.7 = 0.33 V; τ = 1/2.7 s⁻¹ = 0.37 s; R·C) | l. 347, l. 286 | write steps |
| 971 | Table 14 "133 V/µs", "312 V/µs" | caption cites da_compare.py (no step test); 133 from large_signal_THS4031.json (no script writes it) | large_signal*.json | cite files; script |
| 975 | "THS4031 (1.6 nV/√Hz, 100 MHz)" | MISMATCH: SLOS224L 1.2 nV/√Hz (pp. 1, 6); models.py uses 1.2; 100 MHz at G = 2 uncited | TI_ths4031_datasheet.pdf | "1.2 nV/√Hz; 100 MHz at G = 2"; fix da_compare docstring |
| 976 | "LM7171 A grade (8.5 nV/√Hz, 4100 V/µs)" | no citation (correct) | SNOS760D p. 5 §5.5, p. 1 | cite |
| 977 | "THS3091 (2 nV/√Hz, …, 1 kΩ)" | MISMATCH: SLOS423K 1.1 nV/√Hz (pp. 1, 6); 1.92 is model's; 1 kΩ unexplained | data sheet; models.py; da_compare.py | "1.1 (model 1.9)"; explain 1 kΩ |
| 979 | "about 20 dB higher than its data sheet" | no derivation: −38 vs −50 dBc is 12 dB unscaled, 24 dB if HD3 ∝ V²; l. 753 quotes −37 (run −37.7) | da_compare.json | write scaling |
| 979 | "ten times worse than the LM7171" | no derivation: −50 vs −79 dBc 29 dB (28×); at 1 Vpp 17 dB (7×) | da_compare.json | state number and basis |
| 979 | "2.6 against 2.0 nV/√Hz" | 2.0 no source; 2.6 white vs l. 823/829 2.78 at 1 kHz | – | see l. 823 |
| 983 | "133 V/µs sets the output's ramp after 85 ns" | no script; npz ramp ≈110 V/µs (10–90 %), peaks ≈240 V/µs | npz | compute, reword |
| 987–997 | NF 5307 column (4/2.5–3, ≈4, 15, <35 pF, 10 MHz, 120/86 dB, 10–1000) | imprecise citation; 120 dB at gain 1000, 86 dB from gain-100 plot | spec sheet PDF; manual Fig. 4.7 (PDF p. 37); web page Fig. 46 (survey.md §1.2) | cite each; state gains |
| 991 | "1.08 / 1.11", "0.42 / 0.43" labelled "gain ≥ 100" | values for gains ≥ 1000; at 100, H 1.12/1.17 | chain_noise.json | relabel "≥ 1000" |
| 991–997 | SR560 spec column (4, ≈11, 13, 25 pF, 1 MHz, 100/40 dB, 1–50000) | no citation; manual p. 5: 1 MHz, >90 dB; data sheet p. 3: 1.2 MHz typ, 100 dB | manual PDF pp. 9, 24, 25; data sheet p. 3 | cite each |
| 994 | "≈ 20 pF", "≈ 250 pF" | C_P + C_Z not written here (l. 597); protection.py computes, not cited | protection.json input_capacitance | cite |
| 1005 | "CM local loop at about 270 MHz" | mismatch: CM GM point 260 MHz (H), 206 MHz (L); 270 only as oscillation with C_node 33 pF | comp_search_*.json cm.gain_margins; osc_check.json | "≈260 MHz (H), ≈210 MHz (L)" (also l. 466) |
| 1007 | "about 20 dB too high" | as l. 979 | | |
| 1015 | "above about 100 kΩ of source impedance" | no source | protection.json: 12.9–22 fA/√Hz crosses 1.08 nV/√Hz at 49–84 kΩ | compute crossover in protection.py |
| 1015 | "√(4kT/R) = 13 fA/√Hz" | script not cited; T not stated | protection.json bias_resistor_noise 12.87 | cite |
| 1021 | "about 30 dB" | no script (32 dB at 10 Hz, 26 dB at 100 Hz) | R_UP test decks | quote from stored result |
| 1067 | "oscillated at 290 MHz in common mode" | archived 282.8 MHz (H100_cnode0p with final C_I/C_X); first version not archived; elsewhere 290 (l. 20, 449, 573), 293 (l. 451) | osc_check.json | archive first-version run or quote 283; consistent |
| 1069 | "over half an hour"; "gminsteps=20" | no log; cmrr_mc.py says "for hours"; no deck uses gminsteps | – | archive or soften |
| 1070 | "retry with three sets" | three option sets, then fourth try on 50 Ω bench | large_signal.py tran() | reword |
| 1073 | "KF = 67860f … 6.786e-002f, 10⁶" | 67860f only in note: no citation, no archived copy; 6.786e-002f archived | sim/models/README_InterFET_NXP_others.md l. 41 | cite LTspice library file and version; archive card (also l. 762) |

Most serious (D): (1) THS4031 high-reserve 2.0 nV/√Hz never simulated; (2) 1 MΩ attenuation 20 dB vs 42/64 dB; (3) Table 14 op-amp data sheet values wrong (THS4031 1.2, THS3091 1.1); (4) CMRR MC description (6 trials in one-class runs; C_node never varied); (5) unscripted results: R_UP CMRR test, large_signal_L1000_step.json (slew nan), large_signal_THS4031.json; (6) overload description values; (7) oscillation frequencies 290 vs 283, 270 vs 260/206; (8) SR560 spec citation (100 dB vs manual >90 dB); (9) "H above 300 Ω" only at 1 MHz; (10) L THD at 10 MHz: two runs differ 5×, undocumented; (11) LTspice KF 67860f uncited, not archived.

Outside range, noticed: l. 753 −37 dBc (run −37.7 → −38); l. 651 "Section 6.4" should be 6.5 (distortion), l. 660 "Section 6.3" should be 6.4 (Monte Carlo); l. 762 J310 "Section 6.1" never mentions J310 (now it does); Table 1 (l. 130) 9.5 → 9.4; l. 1095 SR560 specs printed pp. 20–21 vs spec chart printed p. 5; l. 1096 Fig. 46 is NF's online data-sheet page figure, not the manual.

# The low-voltage option and the input protection, recovered into scripts

Created: scripts/lv_option.py (scan, final reproduce lv_option_scan.json and lv_option.json byte-identical; range writes lv_option_range.json; 1 µs transient ran, 7–14 s), scripts/opamp_noise_check.py (opamp_noise_check.json; also corrected THS4021), scripts/protection.py (protection.json; Table 6d, leakage and bias-resistor noise, bootstrapped clamp string, rail-clamp CM range, Figure 10 readouts).

Verified: LV margins 59.1°/33.6 dB/0.900, 50.0°/20.2 dB/0.759; 18.9 MHz; 3.529/1.062/1.070; adopted FE 2.697/1.499; transient ≤ 10 nV pk-pk; V_DS 1.546, cascode 1.094, outputs V_CM + 0.347; ADA4899 at 10 Hz 46.9 pA, 10.18 nV; ADA4817 3.997/169.8; THS4021 corrected 19.93 pA (e_n 4.03); Table 6d identical with floors 1.08/0.42 (chain_noise 1.0836/0.4196); 69.7 %; 13.3–27.5 %; +0.08/+0.17 dB; NF at R_s = 0: 0.295 closed form, 0.298 sim; leakage 0.57/1.79/5.66/17.90 fA; 100 MΩ 12.87 fA; C_P + C_Z = 20/250 pF (+0.05/0.33 pF bare FE); clamp string H 2 diodes 0.178 V, L 3 diodes 0.188 V; rail-clamp CM range −12.83…+3.73 (H), −8.97…+3.57 (L); negative resistance −1049 Ω/−110 Ω; peaking 21.3, 16.0, 0.57 dB.

Discrepancies: ±3.8 V swing: ADA4899 model clips at ±3.34 V with R_F load; "−0.9 to +0.5 V at full output" has no derivation: upper +0.65 V (cascode just saturated) or +0.09 V (1 V margin); lower −3.2 V at 1 V DM output (model swing) or −3.65 V (±3.8 V); −0.9 V needs 5.6–6.5 V DM output; at total gain 100 the FE must deliver 10 V DM, impossible with LV (max ≈ 6.0 V); summary's "±0.5–1 V" same problem; line 561 "against −12 V to +3.7 V" still −12 V and mixes conditions (adopted lower end at 10 V output −8.7 V); ADA4899 noise numbers include the model's 4 kΩ input resistor: corrected 0.997 nV, 2.60 pA white, 45.0 pA at 10 Hz (note 47 is uncorrected); roundings: −1.05 kΩ not −1.1 kΩ; 27.5 % not 28 %; H input capacitance 0.11 pF at 1 MHz (not 0.05); 100 pA leakage adds 9 % current noise; L upper limit +3.6 V not +3.7 V.
Still without script: product-page values (ADA4899 600 MHz, 310 V/µs, 5–12 V; ADA4817 1 GHz, 2.5 fA); 25 pF/35 pF of SR560 and NF 5307; generic diode capacitances; "doubles every 10 °C"; Eq. (10b) 24 MHz and "15–30 MHz"; Table 7's raw THS4021/THS4031/THS3091 figures from inline runs.
scripts/README.md not yet updated for the three scripts.
