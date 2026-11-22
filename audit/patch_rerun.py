"""Patch of low_noise_preamp.md after the re-run of every simulation with the recalibrated models
(22 November 2026).

What changed in the models: the JFE150's and JFE2140's C_rss targets, read from the pixels of their data
sheets' capacitance plots (4.1 and 3.9 pF at 5 V instead of 4.5 and 4.2 pF read by eye), and the
THS4021's and THS4031's 1/f current-noise generators, refitted to 18.6 pA/rtHz at 10 Hz (20 by eye).
L now runs with its 6 V PZT3904 sinks everywhere (frontend.CASES), except Table 13's steps, which did
not complete with them.  Also: the trim resistor for H becomes 50 kohm; da_compare.py's distortion
runs are fresh (they had been taken from cached runs of the old models).

Every new value is the quoted form in sim/results/numbers_s1_3.json, numbers_s4a.json,
numbers_s4b_5.json or numbers_s6_7.json, or a value of the results file the note names next to it,
rounded as the note rounds it.  Every edit is an exact-string replacement whose old text occurs the
stated number of times (once unless given); two lines are added (Appendix).  A second run is refused.
Usage: python patch_rerun.py <path to low_noise_preamp.md>
"""
from __future__ import annotations

import sys
from pathlib import Path

# (old, new) or (old, new, count)
EDITS: list[tuple] = [
    # ---- summary -------------------------------------------------------------------------------
    ("(0.06 pF at 1 kHz, 0.05 pF at 100 kHz, 0.11 pF at 1 MHz; `sim/results/zin_numbers.json`)",
     "(0.05 pF at 1 kHz and at 100 kHz, 0.11 pF at 1 MHz; `sim/results/zin_numbers.json`)"),
    ("about 95 Ω at 10 MHz, 0.70 kΩ at 1 MHz and 27–71 kΩ at 1 kHz and 10 Hz",
     "about 96 Ω at 10 MHz, 0.70 kΩ at 1 MHz and 27–70 kΩ at 1 kHz and 10 Hz", 2),
    ("The full chain reaches −3 dB at 14.85–14.87 MHz (H, gain ≥ 100), 25.0–25.2 MHz (H with the front end "
     "at ×10: gain ≤ 10 and the high-reserve mode) and 16.6 MHz (L), and at 10 MHz it is 0.35–0.36 dB (H, "
     "gain ≥ 100), 0.40–0.41 dB (H, front end at ×10) and 0.80–0.81 dB (L) below its midband gain",
     "The full chain reaches −3 dB at 14.82–14.84 MHz (H, gain ≥ 100), 24.9–25.0 MHz (H with the front end "
     "at ×10: gain ≤ 10 and the high-reserve mode) and 16.5 MHz (L), and at 10 MHz it is 0.37 dB (H, "
     "gain ≥ 100), 0.41–0.42 dB (H, front end at ×10) and 0.82 dB (L) below its midband gain"),
    ("with $14.85/0.73$ = 20 times (H, gain 100) and $16.6/0.73$ = 23 times (L, gain 1000)",
     "with $14.82/0.73$ = 20 times (H, gain 100) and $16.5/0.73$ = 23 times (L, gain 1000)"),
    ("at 293 MHz (H) and 277 MHz (L) with 50 Ω sources", "at 293 MHz (H) and 276 MHz (L) with 50 Ω sources"),
    ("the chain's falls from 30.1 to 14.85 MHz, $14.85/30.1$ = 0.49)",
     "the chain's falls from 30.1 to 14.82 MHz, $14.82/30.1$ = 0.49)"),
    # ---- Sections 2-3 --------------------------------------------------------------------------
    ("(14.85–25.2 MHz for this design's chain at its gains", "(14.82–25.0 MHz for this design's chain at its gains"),
    ("**DC–14.85 MHz**", "**DC–14.82 MHz**"),
    ("**DC–16.6 MHz**", "**DC–16.5 MHz**"),
    ("**quieter than H below 95 Ω (10 MHz) to 71 kΩ (10 Hz) of source**",
     "**quieter than H below 96 Ω (10 MHz) to 70 kΩ (10 Hz) of source**"),
    ("*Table 4. Calibration of the JFET models (data sheets' typical values; `sim/results/jfet_calibration.json`).*",
     "*Table 4. Calibration of the JFET models (data sheets' typical values; `sim/results/jfet_calibration.json`). "
     "The $C_{rss}$ targets of the JFE150 and JFE2140 are read from the pixels of SLPS732B Fig. 6-12 (p. 7) and "
     "SLPS730B Fig. 6-17 (p. 8) at 5 V (`scripts/ti_plot_check.py`); read by eye, they had been taken as 4.5 "
     "and 4.2 pF.*"),
    ("| 20.3 / 6.3 → 25.1 / 12.6 | 0.8 / 1.8 nV at 1 kHz / 10 Hz, 5 mA, 5 V; $C_{iss}$ 24, $C_{rss}$ 4.5 pF |",
     "| 20.3 / 6.3 → 25.7 / 11.5 | 0.8 / 1.8 nV at 1 kHz / 10 Hz, 5 mA, 5 V; $C_{iss}$ 24, $C_{rss}$ 4.1 pF |"),
    ("| 9.2 / 3.5 → 10.2 / 11.8 | 1.1 / 2.4 nV, 2 mA, 10 V; $C_{iss}$ 13, $C_{rss}$ 4.2 pF |",
     "| 9.2 / 3.5 → 10.6 / 11.0 | 1.1 / 2.4 nV, 2 mA, 10 V; $C_{iss}$ 13, $C_{rss}$ 3.9 pF |"),
    # ---- Section 4.3 ---------------------------------------------------------------------------
    ("(Figure 9a, d: phase margin −97° at 189 MHz)", "(Figure 9a, d: phase margin −93° at 189 MHz)"),
    ("The outer loops had 71° and 77° of phase margin", "The outer loops had 72° and 77° of phase margin"),
    ("a common-mode crossover at 452 MHz with −80° of phase margin",
     "a common-mode crossover at 452 MHz with −81° of phase margin"),
    ("to 14.85 MHz (`chain_ac.json`)", "to 14.82 MHz (`chain_ac.json`)"),
    ("and at 277 MHz with 0.78 V (L).", "and at 276 MHz with 0.78 V (L)."),
    (" L was simulated with its first sinks (MMBT3904, 2 V); with the adopted PZT3904 at 6 V, `sink_power.json` "
     "gives the same complete-loop margins within 0.1° and 0.1 dB.*",
     " L with its 6 V sinks (Section 4.2.1).*"),
    ("| L | 10.6 MHz, 66°, 18 dB | 20 MHz, 63°, 12 dB | 27 MHz, 63°, 17 dB | 57 MHz, 51°, 10 dB |",
     "| L | 10.6 MHz, 66°, 19 dB | 20 MHz, 63°, 12 dB | 27 MHz, 63°, 17 dB | 59 MHz, 51°, 10 dB |"),
    ("| H, first version | 21 MHz, 71° | 28 MHz, 77° | 90 MHz, 66° | **452 MHz, −80°: oscillates** |",
     "| H, first version | 21 MHz, 72° | 28 MHz, 77° | 90 MHz, 65° | **452 MHz, −81°: oscillates** |"),
    ("the common-mode outer loop is unstable, −97° at 189 MHz;", "the common-mode outer loop is unstable, −93° at 189 MHz;"),
    ("the op amp's own common-mode loop is not, −80° at 452 MHz,", "the op amp's own common-mode loop is not, −81° at 452 MHz,"),
    # ---- Section 4.3.1 -------------------------------------------------------------------------
    ("(`sim/results/stability_corners.json`; L with its first sinks, as in Table 6).*",
     "(`sim/results/stability_corners.json`; L with its 6 V sinks, as in Table 6).*"),
    ("| 66°, 14 dB, 0.78 | 49°, 7.6 dB, 0.55 |", "| 66°, 14 dB, 0.78 | 50°, 7.6 dB, 0.54 |"),
    ("| 60°, 19 dB, 0.87 | 50°, 12 dB, 0.73 |", "| 60°, 19 dB, 0.86 | 51°, 12 dB, 0.72 |"),
    ("| 67°, 15 dB, 0.80 | 52°, 9.9 dB, 0.64 |", "| 67°, 15 dB, 0.79 | 52°, 9.9 dB, 0.64 |"),
    ("| 55°, 19 dB, 0.87 | 51°, 11 dB, 0.68 |", "| 55°, 19 dB, 0.87 | 51°, 11 dB, 0.67 |"),
    ("| 15 MHz | 2.70 / 1.07 / 1.50 nV/√Hz |", "| 15 MHz | 2.67 / 1.07 / 1.50 nV/√Hz |"),
    ("| 27 MHz | 3.15 / 1.44 / 2.14 nV/√Hz |", "| 27 MHz | 3.09 / 1.44 / 2.14 nV/√Hz |"),
    ("| 26 MHz | 2.95 / 1.29 / 1.87 nV/√Hz |", "| 26 MHz | 2.90 / 1.29 / 1.87 nV/√Hz |"),
    ("| 16 MHz | 2.69 / 1.07 / 5.38 nV/√Hz |", "| 16 MHz | 2.66 / 1.07 / 5.38 nV/√Hz |"),
    ("| 53°, 21 dB, 0.85 | 47°, 10 dB, 0.62 | 16 MHz | 2.70 / 1.07 / 3.63 nV/√Hz |",
     "| 54°, 21 dB, 0.85 | 47°, 10 dB, 0.62 | 16 MHz | 2.67 / 1.07 / 3.63 nV/√Hz |"),
    ("| 50°, 20 dB, 0.76 | 19 MHz |", "| 50°, 20 dB, 0.75 | 19 MHz |"),
    ("and the common-mode loop has −14° of phase margin.", "and the common-mode loop has −15° of phase margin."),
    ("and the modulus margin 0.76 against 0.61;", "and the modulus margin 0.75 against 0.61;"),
    ("against 20 pA/√Hz for the corrected THS4021 model", "against 19 pA/√Hz for the corrected THS4021 model"),
    ("near 240 MHz in H and 170 MHz in L,", "near 240 MHz in H and 160 MHz in L,"),
    # ---- Section 4.4 ---------------------------------------------------------------------------
    ("is 0.050–0.057 pF from 1 kHz to 300 kHz", "is 0.047–0.053 pF from 1 kHz to 300 kHz"),
    ("L's is 0.33–0.39 pF (0.99 pF at 1 MHz)", "L's is 0.31–0.36 pF (0.95 pF at 1 MHz)"),
    ("to −1.05 kΩ at its smallest, at 12.6 MHz, for H and to −110 Ω at 15.8 MHz for L",
     "to −1.07 kΩ at its smallest, at 12.6 MHz, for H and to −112 Ω at 17.8 MHz for L"),
    ("a 1 MΩ source peaks by 21 dB at 0.24 MHz on H", "a 1 MΩ source peaks by 22 dB at 0.24 MHz on H"),
    ("cancels only part of the bare front end's −0.95 mS there, and H's input conductance stays negative from "
     "0.14 to 25 MHz, with −1.64 kΩ at 12.6 MHz",
     "cancels only part of the bare front end's −0.94 mS there, and H's input conductance stays negative from "
     "0.16 to 25 MHz, with −1.68 kΩ at 12.6 MHz"),
    ("peaks by more than 0.57 dB (H, 1 kΩ, at 5.0 MHz; Figure 10c)",
     "peaks by more than 0.52 dB (H, 1 kΩ, at 5.0 MHz; Figure 10c)"),
    # ---- Section 4.6: the trim with 50 kohm ----------------------------------------------------
    (r"For H, a 12-bit DAC at ±10 V through 100 kΩ gives ±100 µA, i.e. ±3.8 mV at the input at a gain of 100 and "
     r"±8.3 mV at a gain of 10, in steps ($2\Delta I\,w/2^{12}$) of 1.9 and 4.0 µV, and the 100 kΩ adds "
     r"$\sqrt{4kT/100\ \mathrm{k\Omega}}$ = 0.41 pA/√Hz, i.e. 0.016 and 0.034 nV/√Hz at the input. For L, 10 kΩ "
     r"gives ±1 mA, i.e. ±4.8 mV (`scripts/numbers_s4b_5.py`). These ranges are 1.1 (H at a gain of 100), 2.5 "
     r"(H at 10) and 2.2 (L) times the rms input offsets of the Monte Carlo (3.4, 3.3 and 2.2 mV, `cmrr_mc.json`), "
     r"so that, for a Gaussian spread, 26 % of H front ends at a gain of 100 would lie outside the range, against "
     r"1 % at a gain of 10 and 3 % for L ($\mathrm{erfc}(r/\sqrt2)$ for a range of $r$ times the rms offset, "
     r"`scripts/numbers_s4b_5.py`): for H at a gain of 100 the range of this example is too small.",
     r"For H, a 12-bit DAC at ±10 V through 50 kΩ gives ±200 µA, i.e. ±7.6 mV at the input at a gain of 100 and "
     r"±16.6 mV at a gain of 10, in steps ($2\Delta I\,w/2^{12}$) of 3.7 and 8.1 µV, and the 50 kΩ adds "
     r"$\sqrt{4kT/50\ \mathrm{k\Omega}}$ = 0.58 pA/√Hz, i.e. 0.022 and 0.048 nV/√Hz at the input. For L, 10 kΩ "
     r"gives ±1 mA, i.e. ±4.8 mV, in steps of 2.4 µV, and adds 1.29 pA/√Hz, i.e. 0.0062 nV/√Hz "
     r"(`scripts/numbers_s4b_5.py`). These ranges are 2.3 (H at a gain of 100), 5.0 (H at 10) and 2.2 (L) times "
     r"the rms input offsets of the Monte Carlo (3.4, 3.3 and 2.2 mV, `cmrr_mc.json`), so that, for a Gaussian "
     r"spread, 2.3 % of H front ends at a gain of 100 would lie outside the range, against $5.6\times10^{-5}$ % "
     r"at a gain of 10 and 3.1 % for L ($\mathrm{erfc}(r/\sqrt2)$ for a range of $r$ times the rms offset, "
     r"`scripts/numbers_s4b_5.py`). With 100 kΩ, H's range at a gain of 100 would be only 1.1 times its rms "
     r"offset, and 26 % would lie outside. The DAC's own output noise passes through the same resistor; it adds "
     r"less than the resistor's thermal noise as long as it is below $\sqrt{4kTR}$, 29 nV/√Hz for 50 kΩ and "
     r"13 nV/√Hz for 10 kΩ."),
    # ---- Section 4.8 ---------------------------------------------------------------------------
    ("and at a front-end gain of 10 the op amps contribute more than the JFETs at 1 and 10 Hz (7.8 against 7.0 "
     "and 2.5 against 2.4 nV/√Hz, `curves_noise.npz`).",
     "and at a front-end gain of 10 the op amps contribute about as much as the JFETs at 1 and 10 Hz (7.3 against "
     "7.0 and 2.3 against 2.4 nV/√Hz, `curves_noise.npz`)."),
    ("H 2.7 nV/√Hz at 10 Hz and 7.9 at 1 Hz (gain 100)", "H 2.7 nV/√Hz at 10 Hz and 7.8 at 1 Hz (gain 100)"),
    ("H at a gain of 100 falls from 2.70 to 2.45 nV/√Hz at 10 Hz and from 7.9 to 7.1 at 1 Hz; H at a gain of 10 "
     "from 3.8 to 2.9 at 10 Hz and from 10.6 to 7.2 at 1 Hz; L from 0.83 to 0.78 at 10 Hz",
     "H at a gain of 100 falls from 2.67 to 2.45 nV/√Hz at 10 Hz and from 7.8 to 7.1 at 1 Hz; H at a gain of 10 "
     "from 3.7 to 2.9 at 10 Hz and from 10.2 to 7.2 at 1 Hz; L from 0.83 to 0.77 at 10 Hz"),
    # ---- Section 5 -----------------------------------------------------------------------------
    ("and the noise came out at 57.5 nV/√Hz", "and the noise came out at 64.0 nV/√Hz"),
    ("with a bandwidth of 278 MHz instead of 15.1 MHz", "with a bandwidth of 322 MHz instead of 15.0 MHz"),
    ("Data-sheet values cited by figure are read by eye from its curves.*",
     "Data-sheet values cited by figure are read by eye from its curves, except the JFETs' $C_{rss}$ and the "
     "THS4021's and THS4031's current noise, read from the curves' pixels (`scripts/ti_plot_check.py`).*"),
    ("| 13 pF (§6.5, p. 5), 4.2 pF (Fig. 6-17, p. 8) | 0.67×, 0.30× |",
     "| 13 pF (§6.5, p. 5), 3.9 pF (Fig. 6-17, p. 8) | 0.67×, 0.32× |"),
    ("| 24 pF (§6.5, p. 5), 4.5 pF (Fig. 6-12, p. 7) | 0.74×, 0.50× |",
     "| 24 pF (§6.5, p. 5), 4.1 pF (Fig. 6-12, p. 7) | 0.74×, 0.55× |"),
    ("comes out at 30–50 % of the data sheet's", "comes out at 32–55 % of the data sheet's"),
    ("six times the 2.70 nV/√Hz it has with the corrected model", "six times the 2.67 nV/√Hz it has with the corrected model"),
    # ---- Section 6.1 ---------------------------------------------------------------------------
    ("| H, gain 100 | 1 Hz | 7.90 | 7.04 | 0.41 | 3.56 | 0.28 | 0.08 | 0.04 |",
     "| H, gain 100 | 1 Hz | 7.81 | 7.04 | 0.41 | 3.33 | 0.28 | 0.08 | 0.04 |"),
    ("| | 10 Hz | 2.70 | 2.40 | 0.41 | 1.13 | 0.28 | 0.08 | 0.04 |",
     "| | 10 Hz | 2.67 | 2.40 | 0.41 | 1.06 | 0.28 | 0.08 | 0.04 |"),
    ("| H, gain 10 | 10 Hz | 3.80 | 2.40 | 1.22 | 2.47 | 0.62 | 0.79 | 0.41 |",
     "| H, gain 10 | 10 Hz | 3.71 | 2.40 | 1.22 | 2.31 | 0.62 | 0.79 | 0.41 |"),
    ("| | 1 kHz | 1.93 | 0.96 | 1.22 | 0.37 | 0.62 | 0.79 | 0.40 |",
     "| | 1 kHz | 1.92 | 0.96 | 1.22 | 0.36 | 0.62 | 0.79 | 0.40 |"),
    ("| L, gain 201 | 1 Hz | 2.33 | 2.13 | 0.20 | 0.94 | 0.09 | 0.06 | 0.01 |",
     "| L, gain 201 | 1 Hz | 2.33 | 2.13 | 0.20 | 0.92 | 0.09 | 0.04 | 0.01 |"),
    ("| | 10 Hz | 0.83 | 0.74 | 0.20 | 0.31 | 0.09 | 0.06 | 0.01 |",
     "| | 10 Hz | 0.83 | 0.74 | 0.20 | 0.30 | 0.09 | 0.04 | 0.01 |"),
    ("| | 1 kHz | 0.42 | 0.33 | 0.20 | 0.09 | 0.09 | 0.06 | 0.01 |",
     "| | 1 kHz | 0.41 | 0.33 | 0.20 | 0.09 | 0.09 | 0.04 | 0.01 |"),
    ("| | 10 MHz | 0.51 | 0.33 | 0.20 | 0.31 | 0.09 | 0.06 | 0.01 |",
     "| | 10 MHz | 0.50 | 0.33 | 0.20 | 0.31 | 0.09 | 0.04 | 0.01 |"),
    ("and the loop op amps' 1/f dominates H at a gain of 10 (Section 4.8).",
     "and at a gain of 10 the loop op amps' 1/f is about as large as the JFETs' (Section 4.8)."),
    (r"\sqrt{2.78^2 - 1.93^2}$ = 2.0 nV/√Hz", r"\sqrt{2.78^2 - 1.92^2}$ = 2.0 nV/√Hz"),
    ("| 1.90 / 3.80 / 2.94 |", "| 1.90 / 3.71 / 2.94 |"),
    ("| 1.84 / 3.77 / 2.90 |", "| 1.84 / 3.67 / 2.90 |"),
    ("| 1.82 / 3.76 / 2.89 |", "| 1.82 / 3.66 / 2.89 |"),
    ("| 1.87 / 3.79 / 2.92 |", "| 1.87 / 3.69 / 2.92 |"),
    ("| 1.81 / 3.76 / 2.88 |", "| 1.81 / 3.66 / 2.88 |"),
    ("| 1.79 / 3.75 / 2.87 |", "| 1.79 / 3.65 / 2.87 |"),
    ("| 1.77 / 3.75 / 2.86 |", "| 1.77 / 3.65 / 2.86 |"),
    ("| 1.44 / 3.15 / 3.44 |", "| 1.44 / 3.09 / 3.44 |"),
    ("| | 100 | 10.7 | 3.54 | 1.17 | 1.12 | 1.58 | 0.41 mV rms |",
     "| | 100 | 10.6 | 3.52 | 1.17 | 1.12 | 1.58 | 0.41 mV rms |"),
    ("| | 1000 – 50 000 | 8.3–8.4 | 2.83–2.84 |", "| | 1000 – 50 000 | 8.3 | 2.80–2.81 |"),
    ("| | 1000 – 100 000 | 2.7–2.8 | 0.94–0.96 | 0.43 | 0.42 | 0.54–0.55 | 1.43 mV rms at 1000 |",
     "| | 1000 – 100 000 | 2.7–2.8 | 0.94–0.96 | 0.42–0.43 | 0.42 | 0.54 | 1.43 mV rms at 1000 |"),
    ("but 4.2–4.7 nV/√Hz at 10 Hz", "but 4.1–4.6 nV/√Hz at 10 Hz"),
    # ---- Section 6.2 ---------------------------------------------------------------------------
    ("and 3.2, 1.4 and 0.46 dB with 10, 30 and 100 Ω for L", "and 3.2, 1.4 and 0.45 dB with 10, 30 and 100 Ω for L"),
    ("| 10 Ω | 17.0 | 9.3 | 9.1 | 11.9 | 8.2 | 3.2 | 3.2 | 4.9 |", "| 10 Ω | 16.9 | 9.3 | 9.1 | 11.9 | 8.2 | 3.2 | 3.1 | 4.9 |"),
    ("| 30 Ω | 12.4 | 5.4 | 5.3 | 7.7 | 4.6 | 1.4 | 1.3 | 3.4 |", "| 30 Ω | 12.3 | 5.4 | 5.3 | 7.7 | 4.6 | 1.4 | 1.3 | 3.4 |"),
    ("| 100 Ω | 7.7 | 2.4 | 2.3 | 4.1 | 1.9 | 0.46 | 0.50 | 4.3 |", "| 100 Ω | 7.6 | 2.4 | 2.3 | 4.1 | 1.9 | 0.45 | 0.50 | 4.3 |"),
    ("| 300 Ω | 4.2 | 0.97 | 0.94 | 2.5 | 0.74 | 0.16 | 0.33 | 7.2 |", "| 300 Ω | 4.1 | 0.97 | 0.94 | 2.5 | 0.74 | 0.16 | 0.33 | 7.1 |"),
    ("| 10 kΩ | 0.21 | 0.03 | 0.50 | 9.4 | 0.03 | 0.01 | 3.8 | 21.2 |", "| 10 kΩ | 0.20 | 0.03 | 0.50 | 9.3 | 0.03 | 0.01 | 3.8 | 21.2 |"),
    ("| 1 MΩ | 0.05 | 0.04 | 10.9 | 28.8 | 0.41 | 0.41 | 21.5 | 41.2 |", "| 1 MΩ | 0.05 | 0.04 | 10.9 | 28.8 | 0.41 | 0.41 | 21.4 | 41.2 |"),
    ("*Table 10. Noise figure (dB) against source resistance (`scripts/noise_vs_source.py`; source resistance in "
     "series with input A, input B grounded).*",
     "*Table 10. Noise figure (dB) against source resistance (`scripts/noise_vs_source.py`, `noise_vs_source.json`, "
     "rounded by `scripts/numbers_s6_7.py`; source resistance in series with input A, input B grounded).*"),
    # ---- Section 6.3 ---------------------------------------------------------------------------
    ("| H, front end ×10 | 1 – 10 (and H_HR up to 1000) | 25.0–25.2 MHz | 0.00 dB | −0.40 to −0.41 dB | none |",
     "| H, front end ×10 | 1 – 10 (and H_HR up to 1000) | 24.9–25.0 MHz | 0.00 dB | −0.41 to −0.42 dB | none |"),
    ("| H, front end ×100 | 100 – 50 000 | 14.85–14.87 MHz | +0.01 dB | −0.35 to −0.36 dB | 0.17 dB |",
     "| H, front end ×100 | 100 – 50 000 | 14.82–14.84 MHz | +0.01 dB | −0.37 dB | 0.17 dB |"),
    ("| L | 200 – 100 000 | 16.6 MHz | 0.00 dB | −0.80 to −0.81 dB | none |",
     "| L | 200 – 100 000 | 16.5 MHz | −0.01 dB | −0.82 dB | none |"),
    ("peaks by more than 0.6 dB (0.57 dB, H with 1 kΩ; Figure 10c, `zin_numbers.json`)",
     "peaks by more than 0.52 dB (H with 1 kΩ; Figure 10c, `zin_numbers.json`)"),
    # ---- Section 6.4 ---------------------------------------------------------------------------
    ("| L, inputs driven directly | 108 | 132 | 136 | 118 | 98 | 78 |", "| L, inputs driven directly | 108 | 132 | 137 | 118 | 98 | 78 |"),
    # ---- Section 6.5 ---------------------------------------------------------------------------
    ("L's 10 V step from `large_signal_L1000_step.json` and H's recovery from `large_signal_THS4031.json`, both "
     "reproduced by `scripts/large_signal.py repro`; L's supply rejection with the 6 V sinks from `sink_power.json`).",
     "L's steps from `large_signal_L1000_step.json` and H's recovery from `large_signal_THS4031.json`, both "
     "reproduced by `scripts/large_signal.py repro`; rounded by `scripts/numbers_s6_7.py`)."),
    ("L's entries, except the supply rejection, were simulated with the first design's 2 V sinks (MMBT3904), "
     "before the 6 V PZT3904 sinks of Section 4.2.1.*",
     "L's entries are simulated with the 6 V PZT3904 sinks of Section 4.2.1, except the steps: with these sinks "
     "the step transients did not complete (Appendix, \"Transients that stop or crawl\"), so L's steps are those of "
     "the first design's 2 V sinks (MMBT3904), with which the loop margins and the bandwidth are the same "
     "(`sink_power.json`).*"),
    ("| THD, 1 MHz, 1 / 10 Vpp | 0.0009 % / 0.025 % | 0.0008 % / 0.023 % |",
     "| THD, 1 MHz, 1 / 10 Vpp | 0.0009 % / 0.025 % | 0.0009 % / 0.023 % |"),
    ("| THD, 10 MHz, 1 Vpp | 0.012 % (fundamental 0.963 Vpp) | 0.0078 % (fundamental 0.918 Vpp) |",
     "| THD, 10 MHz, 1 Vpp | 0.012 % (fundamental 0.961 Vpp) | 0.0100 % (fundamental 0.916 Vpp) |"),
    ("| 23 ns, 7.8 %, 83 / 129 ns | not obtained (the transient failed numerically on every bench) |",
     "| 23 ns, 7.7 %, 83 / 129 ns | 34 ns, 4.7 %, 106 / 163 ns (50 Ω sources; 2 V sinks) |"),
    ("| 27 ns, 9.4 %, 84 / 131 ns, 312 V/µs | 34 ns, 4.9 %, 106 / 164 ns, 275 V/µs (50 Ω sources) |",
     "| 27 ns, 9.3 %, 84 / 131 ns, 312 V/µs | 34 ns, 4.7 %, 106 / 163 ns, 275 V/µs (50 Ω sources; 2 V sinks) |"),
    ("| 117 / 120 dB; 90 / 98 dB; 70 / 78 dB, with the 6 V sinks of Section 4.2.1 (−15 V: 122, 102 and 80 dB with "
     "the first design's 2 V) |",
     "| 117 / 120 dB; 90 / 98 dB; 70 / 78 dB (−15 V with the first design's 2 V sinks: 122, 102 and 80 dB, "
     "`sink_power.json`) |"),
    ("and 0.012 % against 0.0032 %; `large_signal.json`)", "and 0.011 % against 0.0032 %; `large_signal.json`)"),
    ("L's value at 10 MHz depends on S2: 0.0078 % with the LM7171, 0.0396 % with the THS4031",
     "L's value at 10 MHz depends on S2 and, less, on the sinks: 0.0100 % with the LM7171 and 0.0369 % with the "
     "THS4031 with the 6 V sinks, 0.0072 % and 0.0376 % with the first design's 2 V sinks"),
    ("Its 9.4 % overshoot is mostly the front end's own: alone, with its outputs unloaded, the front end "
     "overshoots 8.8 % on the same step, and 9.5 % when S2 loads it. The stages after S2 limit the slew rate: "
     "395 V/µs at the front end's outputs alone",
     "Its 9.3 % overshoot is mostly the front end's own: alone, with its outputs unloaded, the front end "
     "overshoots 8.7 % on the same step, and 9.4 % when S2 loads it. The stages after S2 limit the slew rate: "
     "394 V/µs at the front end's outputs alone"),
    ("give −158 to −179 dBc, and five integration settings (Gear, trapezoidal, two tighter tolerances, four times "
     "finer steps) change H's THD at 1 Vpp by at most 0.4 dB: −122.0 to −122.1 dBc at 1 kHz, −121.0 to −121.4 dBc "
     "at 100 kHz and −101.2 dBc at 1 MHz (`large_signal_floor.json`).",
     "give −158 to −180 dBc, and five integration settings (Gear, trapezoidal, two tighter tolerances, four times "
     "finer steps) change H's THD at 1 Vpp by at most 0.1 dB: −122.0 to −122.1 dBc at 1 kHz, −121.0 to −121.2 dBc "
     "at 100 kHz and −101.2 to −101.3 dBc at 1 MHz (`large_signal_floor.json`; at 100 kHz the setting with "
     "reltol = 1e-5 and abstol = 1e-11 stopped, Appendix)."),
    ("the output undershoots by 1.38 V", "the output undershoots by 1.31 V"),
    ("swing to −2.15 V (side A) and +2.88 V (side B), 2.50 and 2.53 V from rest",
     "swing to −2.13 V (side A) and +2.86 V (side B), 2.49 and 2.51 V from rest"),
    ("with a 10–90 % slope of 112 V/µs and peaks of 268 V/µs", "with a 10–90 % slope of 111 V/µs and peaks of 268 V/µs"),
    ("| THS4031 (1.2 nV/√Hz, 100 MHz at a gain of 2) | 1.31 % |", "| THS4031 (1.2 nV/√Hz, 100 MHz at a gain of 2) | 1.30 % |"),
    ("the output returns with a 10–90 % slope of 112 V/µs;", "the output returns with a 10–90 % slope of 111 V/µs;"),
    # ---- Section 6.6 ---------------------------------------------------------------------------
    ("| 1.08 / 1.11 | 0.42 / 0.43 |", "| 1.08 / 1.11 | 0.42 / 0.42–0.43 |"),
    ("| 14.85–14.87 MHz (25.0–25.2 MHz at ×10) | 16.6 MHz |", "| 14.82–14.84 MHz (24.9–25.0 MHz at ×10) | 16.5 MHz |"),
    # ---- Section 7 -----------------------------------------------------------------------------
    ("All op-amp noise models were corrected to their data sheets' typical curves, read by eye.",
     "All op-amp noise models were corrected to their data sheets' typical curves, read by eye, except the "
     "THS4021's and THS4031's current noise, read from the curves' pixels (`scripts/ti_plot_check.py`)."),
    ("The L results of Section 6 were simulated with the first design's 2 V sinks, except the supply rejection in "
     "Table 13. With 6 V, the loop margins, bandwidth and noise are the same (`scripts/sink_power.py`). The CMRR "
     "Monte Carlo and the large-signal runs were not repeated, except the THD at 10 MHz and 1 Vpp (0.0072 % with "
     "the 6 V sinks against 0.0078 %, `large_signal_floor.json`); the sinks' output impedance only rises with $R_T$.",
     "The L results of Sections 4 and 6 are simulated with the 6 V sinks, except the steps of Table 13, which did "
     "not complete with them (Appendix) and come from the first design's 2 V sinks; with either sink design the "
     "loop margins and the bandwidth are the same (`scripts/sink_power.py`), and the sinks' output impedance only "
     "rises with $R_T$."),
    ("The DC offset trim of Section 4.6 is designed on paper only, and its example range covers only 1.1 times H's "
     "simulated rms offset at a gain of 100.",
     "The DC offset trim of Section 4.6 is designed on paper only; with 50 kΩ its example range covers 2.3 times "
     "H's simulated rms offset at a gain of 100, which for a Gaussian spread leaves 2.3 % of front ends outside it."),
    # ---- Section 8 -----------------------------------------------------------------------------
    ("| `scripts/nf5307_plot_check.py` | the NF 5307's CMRR and noise plots read from their pixels, a check of the "
     "readings by eye (`nf5307_plot_check.json`) |",
     "| `scripts/nf5307_plot_check.py`, `scripts/ti_plot_check.py` | the NF 5307's CMRR and noise plots read from "
     "their pixels, a check of the readings by eye (`nf5307_plot_check.json`); TI's capacitance and op-amp noise "
     "plots read from their pixels, the source of the JFE150's and JFE2140's $C_{rss}$ and of the THS4021's and "
     "THS4031's current noise at 10 Hz (`ti_plot_check.json`) |"),
    # ---- Appendix ------------------------------------------------------------------------------
    ("L at 277 and 230 MHz (`scripts/osc_check.py first`", "L at 276 and 227 MHz (`scripts/osc_check.py first`"),
    ("stopped at 8.3 ns for H at 100 kHz, where it had run before.\n",
     "stopped at 8.3 ns for H at 100 kHz, where it had run before.\n"
     "  - L's steps with the 6 V sinks (`scripts/large_signal.py`): the 1 V step stopped at once with ngspice's "
     "\"memory required\" error, and the 10 V step ran for more than 30 minutes without finishing and was stopped "
     "by hand. With the first design's sinks (`large_signal.py repro L1000_step`) both steps ran on the 50 Ω "
     "bench, where before the recalibration the 1 V step had failed on every bench; Table 13 quotes those. H's "
     "steps ran as before.\n"),
    ("- **LTspice-only parameters.**",
     "- **Cached runs that outlive a model change.** `scripts/da_compare.py` reused a run folder's results "
     "whenever one existed, so after the recalibration its distortion figures still came from the old models "
     "(Table 14's THS4031 at 10 MHz: 1.31 % before the fresh run, 1.30 % after). A cache must key on the deck and "
     "on the content of every library it includes; the script now runs every transient anew.\n"
     "- **LTspice-only parameters.**"),
]


def main() -> None:
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    assert "\r" not in text
    if "about 96 Ω at 10 MHz" in text:
        sys.exit("already patched: refusing a second run")
    n_lines = text.count("\n")
    for e in EDITS:
        old, new = e[0], e[1]
        n = e[2] if len(e) > 2 else 1
        c = text.count(old)
        assert c == n, (c, n, old[:90])
        text = text.replace(old, new)
    assert text.count("\n") == n_lines + 2, (text.count("\n"), n_lines)
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"{len(EDITS)} replacements applied to {path.name}")


if __name__ == "__main__":
    main()
