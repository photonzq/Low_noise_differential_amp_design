# Fix phase 1b: model checks and figures (21 November 2026)

Scripts changed or added: `models.py` (adds `prepare_published_opamps()` → `_lib/opamps_published.lib`; JFE2325 calibrated at V_GS = 0), `opamp_noise_check.py`, `model_defects.py` (new), `jfet_model_check.py`, `noise_theory.py`, `jfet_data.py`, `make_figures.py`. Results: `opamp_noise_check.json`, `model_defects.json`, `jfet_calibration.json`, `jfet_model_check.json`, `noise_theory.json`, `jfet_table3.json`.

## Published op-amp models (opamp_noise_check.json: table7.<part>.e_n_10, .i_n_10, .e_n_white_kf0, .i_n_white_kf0, .corner_*)

| Model | e_n at 10 Hz | i_n− at 10 Hz | white (KF = 0) | i_n− corner, own white / data-sheet white |
|---|---|---|---|---|
| THS4021 | 18.21 nV | 293.4 pA | 1.274 nV, 1.185 pA | 613 kHz / 163 kHz |
| THS4031 | 22.19 nV | 300.4 pA | 1.265 nV, 1.117 pA | 723 kHz / 205 kHz |
| THS3091 | 37.04 nV | 316.9 pA | 1.917 nV, 1.548 pA | 419 kHz / 5.1 kHz |
| LM7171 | 4.08 nV (no 1/f) | 0.97 pA | 4.08 nV | – |

Data sheets' own i_n corners: 0.76 kHz (THS4021), 0.91 kHz (THS4031). ADA4899 corrected for its 4 kΩ input resistor: 0.997 nV, 2.60 pA, 45.0 pA at 10 Hz ("ADA4899 corrected for R_d").

## Published THS4021 in H100 (opamp_noise_check.json "H100 front end, published THS4021")
16.19 nV/√Hz at 10 Hz against 2.70 corrected (×6.0), NOT the note's 11.3 (×4); loop op amps 16.0 nV. (Only one loop op amp published gives 11.6 — scratch, unarchived; possibly the origin of 11.3; unconfirmed.)
The "×1.8": the published THS3091 in the chain at total gain 1 at 1 Hz: 1145 vs 651 nV/√Hz = ×1.76; ×1.65 at gain 10 ("chain, published THS3091").

## LSK389 LTspice cards (model_defects.json: jfet.LSK389), LSK389B at 2 mA, 10 V
With NLEV = 3, GDSNOI = 7: 1.409 nV/√Hz; without: 0.858 (note's 1.41 = with). LSK389A 1.390/0.782; LSK389C 1.262/0.892; LSK170A/B/C identical.
Library record (ltspice_library): %LOCALAPPDATA%\LTspice\lib\cmp\standard.jft dated 2026-09-20, SHA-256 82bdc4a4…3557, LTspice 26.1.1.0; last JFET entry in change log "06/26/23 Updated JFET device models from Linear Systems"; tokens Kf=67860f (2N5564), Kf=46340f (J310).

## model_defects.json (Table 7 rows under table7)
- JFE2140 card at 10 Hz: 1.19 nV/√Hz (ngspice), 1.21 (Eq. (1)); 1/f power 14.5× too low. C_iss, C_rss ratios 0.665 (→ 0.67×, not 0.66×) and 0.297.
- JFE150 KF: 3.495/3.25 = +7.5 %. C ratios 0.742, 0.501.
- LSBF862 card at 10 Hz: 9.07 nV/√Hz (Eq. (1)); 8.20 (ngspice, includes λ·V_DS); KF ratio 50.3×. C ratios 0.565, 0.248.
- 2N5564 (LTspice): 1/f corner 1.14 GHz with KF 6.786e-11 (not "megahertz"); 43 nV/√Hz at 1 MHz.
- J310 card: 0.585 µV/√Hz gate-referred at 10 kHz (Eq. (1)); 0.544 in ngspice at 11 mA and 9.3 V.
- J310 sink, H at gain 10, 6 V: 60.7 nV/√Hz at 10 kHz (jfet.J310.sink_run.en."10000.0").
- Op-amp error ratios: THS4021 4.55×/14.7×; THS4031 5.55×/15.0×; THS3091 5.70×/1.58×; THS3091 white i_n− 0.111×; LM7171 0.480×.
- THS4031 HD3 at 10 MHz: −37.7 dBc (→ "−38"); vs data sheet −50 dBc: 12.3 dB as read, 24.3 dB scaled to 2 Vpp (HD3 ∝ V²); "about 20 dB" matches neither.

## JFE2325 recalibration (jfet_calibration.json)
SLPS816A p. 5: "Gate connected to ground", V_DS 2.5 V. Now at V_GS = 0: I_D 0.325 → 0.3782 mA (card I_DSS); V_GS −80.3 mV → 0; g_m 0.638 → 0.688 mS; card white 4.169 → 4.015 nV; RX 66.96 → 143.14 Ω. KF (40e-18, as published) and CGS/CGD (0.75/0.20 pF) unchanged. Table 4: RX 67.0 → 143.1; target add "V_GS = 0".
NEW: the card's 1/f power is 3.2× the data sheet's Fig. 5-24 at 10 Hz (56.7 vs 32 nV/√Hz); model gives 4.66 nV/√Hz at 10 kHz, not 4.3. KF not refitted (the note's method for the JFE2140 would refit KF to the data sheet).
LSBF862 (not refitted): RX clipped at 0 → achieved white 0.898 vs target 0.80; 1.458 nV/√Hz at 10 Hz; stored in jfet_calibration.json, checked in jfet_model_check.json "calibration check".

## SR560 2N5564 targets (jfet_model_check.json "2N5564 targets")
1.28 and 3.6 nV/√Hz are hard-coded in models.py (RX sets white 1.28, KF sets 3.6 at 1 kHz); log–log interpolation of the stated readings gives 1.250/3.444 (second reading 1.277/3.416). Suggested text: "1.28 nV/√Hz white and 3.6 nV/√Hz at 1 kHz, set by eye between Vishay's 1 mA and 10 mA curves (70254 Rev. E p. 5); log–log interpolation to 4.5 mA gives 1.25–1.28 and 3.42–3.44." models.py comment corrected.

## noise_theory.json (Section 1)
√(4kT·(2/3)/g_m) = 0.653 nV/√Hz for g_m 25.93 mS (0.704 in ngspice with RS, RD); 2^(−1/4) = 0.841 (15.9 % per doubling); √(2qI_G) 0.566 fA/√Hz at 1 pA, 17.9 fA at 1 nA; e_n/i_n crossover for 1 nV/√Hz: 1.77 MΩ at 1 pA, 55.9 kΩ at 1 nA; Eq. (2): 0.900 differential and 0.636 per side (H), 0.327 differential (L), 1.81 differential (SR560); Eq. (4): 55.3 Ω and 663 Ω; ΔI/I = 2 × 85/407 = 0.418.
jfet_table3.json: Table 3 with FOM. LSK389 vs others: 2.47 (JFE2140), 2.04 (JFE150), 2.95 (LSBF862), 3.16 (BF862) with data-sheet value; 1.80, 1.49, 2.16, 2.31 with Cordell's 1.17.

## Figures (only these changed)
- Figure 1: stars from curves_noise.npz at 10 kHz, front end alone (1.07, 0.41), stated in figure; FEMTO at 3.0 differential; Stahl PR-E3 at 2 × 16.4 = 32.8 pF (data sheet v3.12 p. 5).
- Figure 5: regenerated (plain tick labels).
- Figure 9: annotations from frontend._margins, matching Table 6: (b) CM 452 MHz, −80°; (c) 19.6 MHz/60° and 59.2 MHz/57°; panel (a) now 189 MHz, −97° → the note's "Figure 9a: −88° at 179 MHz" must change.
- Figure 10: reference lines computed 2 × 13 pF (SLPS730B p. 5), 12 × 24 pF (SLPS732B p. 5); panel (c) adds L with 1 kΩ; y-axis to 30 dB (21 dB peak no longer clipped).

## Other
- THS4021/THS4031 white current noise: data sheets 2.3/2.1 pA/√Hz; models 1.18/1.12 (the correction keeps that); effect on design negligible (to be stated).
- LM7171 data sheet has a current-noise curve (Fig. 5-17 p. 10), not modelled; models.py comment fixed; THS3091 citation now §7.5 p. 6.
- sim/runs/checks/ holds copies of TI model text (THS4021_raw.cir, THS4031_raw.cir, ths3091_lib.cir); jfet_calibration.json stores each part's full card text (as before). Consider removing before publishing.
- model_defects.py reads opamp_noise_check.json, da_compare.json, jfet_calibration.json and imports sink_options.op_point and gain_options.noise_checked.

## README rows
| `models.py` | add: `prepare_published_opamps()` writes `_lib/opamps_published.lib` (vendor op-amp models as published and with KF = 0, for Table 7); the JFE2325 is calibrated at V_GS = 0 | `jfet_calibration.json` |
| `opamp_noise_check.py` | two-gain noise check of op-amp models: Section 4.3.1 models; published THS4021, THS4031, THS3091, LM7171 with 1/f corners; H100 with published THS4021; chain at gains 1 and 10 with published THS3091 | `opamp_noise_check.json` |
| `model_defects.py` | every number of Table 7 and its paragraphs (run after `opamp_noise_check.py`) | `model_defects.json` |
| `jfet_model_check.py` | add: calibration check of every calibrated part, the JFE2325 against Fig. 5-24 at V_GS = 0, the 2N5564 targets | `jfet_model_check.json` |
| `jfet_data.py`, `noise_theory.py` | Table 3 with FOM and LSK389 ratios; the closed forms of Section 1 | `jfet_table3.json`, `noise_theory.json` |
Order: run `opamp_noise_check.py`, `model_defects.py`, `jfet_model_check.py`, `noise_theory.py`, `jfet_data.py` after `da_compare.py` and before `make_figures.py`.
