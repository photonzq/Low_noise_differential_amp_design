"""Patch of low_noise_preamp.md, lines 768-1091 (Sections 6 and 7 and the Appendix; Section 8, lines
1027-1060, is left alone), after the number audit of 21 November 2026 (audit/number_audit_2026-11-21.md,
"Audit D") and the archived results of fix phase 1 (audit/phase1_simulations.md,
audit/phase1_models_figures.md).  The derived numbers come from scripts/numbers_s6_7.py
(sim/results/numbers_s6_7.json).

Every edit is an exact-string replacement whose old text occurs exactly once in the note and lies
inside the range, which is found by its headings so that edits elsewhere in the note do not move it:
from "## 6. Results" up to "## 8. Files" (lines 768-1026 on 21 November 2026) and from
"## Appendix. ngspice pitfalls and techniques" up to "## References" (lines 1061-1091).  Nothing
outside these lines can change, and no edit adds or removes a line.  UTF-8 with \n newlines.
Usage: python patch_s6_7.py <path to low_noise_preamp.md>
"""
from __future__ import annotations

import sys
from pathlib import Path

START, SEC8, APPENDIX, END = ("## 6. Results", "## 8. Files", "## Appendix. ngspice pitfalls and techniques",
                              "## References")

EDITS: list[tuple[str, str]] = [
    # ---- 6.1, Table 8: single roundings of curves_noise.npz ----------------------------------
    ("contributions (`scripts/collect_curves.py`, `noise`; `sim/results/curves_noise.npz`).*",
     "contributions (`scripts/collect_curves.py`, `noise`; `sim/results/curves_noise.npz`, read at the listed "
     "frequencies and rounded once by `scripts/numbers_s6_7.py`).*"),
    ("| H, gain 100 | 1 Hz | 7.91 |", "| H, gain 100 | 1 Hz | 7.90 |"),
    ("| | 1 kHz | 1.10 | 0.96 | 0.41 |", "| | 1 kHz | 1.10 | 0.96 | 0.40 |"),
    ("| | 1 MHz | 1.07 | 0.93 | 0.41 |", "| | 1 MHz | 1.07 | 0.93 | 0.40 |"),
    ("| H, gain 10 | 10 Hz | 3.81 |", "| H, gain 10 | 10 Hz | 3.80 |"),
    ("| | 1 kHz | 1.93 | 0.96 | 1.22 | 0.37 | 0.62 | 0.79 | 0.41 |",
     "| | 1 kHz | 1.93 | 0.96 | 1.22 | 0.37 | 0.62 | 0.79 | 0.40 |"),
    ("| L, gain 201 | 1 Hz | 2.34 |", "| L, gain 201 | 1 Hz | 2.33 |"),
    # ---- 6.1, the JFETs against Eq. (2); the sinks' rank; V_T --------------------------------
    ("In the white region the JFETs contribute 0.93 nV/√Hz (H) and 0.33 nV/√Hz (L), as Eq. (2) predicts from the "
     "data sheets ($\\sqrt2 \\times 0.9/\\sqrt2$ and $\\sqrt2 \\times 0.8/\\sqrt{12}$).",
     "In the white region the JFETs contribute 0.93 nV/√Hz (H) and 0.33 nV/√Hz (L). Eq. (2) gives "
     "$\\sqrt2 \\times 0.9/\\sqrt2$ = 0.90 and $\\sqrt2 \\times 0.8/\\sqrt{12}$ = 0.33 nV/√Hz from the data sheets' "
     "0.9 nV/√Hz for a JFE2140 (SLPS730B p. 1) and 0.8 nV/√Hz for a JFE150 (SLPS732B p. 5, Table 6.5), both at 5 mA "
     "(`sim/results/noise_theory.json`); H's 0.93 is higher mainly because the calibrated JFE2140 card itself gives "
     "0.92 nV/√Hz at 5 mA (`sim/results/jfet_model_check.json`)."),
    ("the second-largest term after $R_G$, because",
     "the largest term after $R_G$ and the JFETs (Table 8), because"),
    ("$V_T = kT/q$ = 25.9 mV, the sink's",
     "$V_T = kT/q$ = 25.9 mV at 300.15 K (ngspice's 27 °C), the sink's"),
    # ---- 6.1, the stages after the front end; R_F = 250 ohm; Table 8a --------------------------
    ("= 2.0 nV/√Hz of their own at 1 kHz, mostly the LM7171 in S2; with the THS4031 in S2 the high-reserve figures "
     "are 2.0 nV/√Hz (below, and Section 6.5).",
     "= 2.0 nV/√Hz of their own at 1 kHz (`sim/results/fe_closed_forms.json`), mostly the LM7171 in S2; with the "
     "THS4031 in S2 they add only 0.74 nV/√Hz (`sim/results/da_compare.json`, `noise_H_HR`; below, and Section 6.5)."),
    ("The front end's floor falls to 1.45 nV/√Hz", "The front end's floor falls to 1.44 nV/√Hz"),
    ("Noise in nV/√Hz, at 10 kHz unless stated.*",
     "Noise in nV/√Hz, at 10 kHz unless stated. The bound row's front-end noise is "
     "$\\sqrt{e_{tot}^2 - e_{sinks}^2}$ (`scripts/fe_closed_forms.py`, `scripts/numbers_s6_7.py`).*"),
    ("| MMBT3904 (adopted) | 2 V | 0.79 (0.66 / 0.44) |", "| MMBT3904 (adopted) | 2 V | 0.79 (0.65 / 0.44) |"),
    ("| 0.70 (0.66 / 0.23) | 1.87 / 3.79 / 2.92 | 1.07 | – | −12.9 |",
     "| 0.70 (0.66 / 0.23) | 1.87 / 3.79 / 2.92 | 1.07 | – | −12.8 |"),
    ("| 0.45 (0.39 / 0.23) |", "| 0.45 (0.38 / 0.23) |"),
    ("| 0.40 | 1.45 / 3.15 / 3.44 |", "| 0.40 | 1.44 / 3.15 / 3.44 |"),
    # ---- 6.1, Table 9: ranges over the gains of a row, rounded once ---------------------------
    ("| | 1000 – 50 000 | 8.4 | 2.84 |", "| | 1000 – 50 000 | 8.3–8.4 | 2.83–2.84 |"),
    ("| H (high reserve) | 100 – 1000 | 29 | 9.5 | 2.77 | 2.62 | 4.86 |",
     "| H (high reserve) | 100 – 1000 | 29 | 9.4–9.6 | 2.76–2.78 | 2.61–2.62 | 4.85–4.86 |"),
    ("| | 1000 – 100 000 | 2.7 | 0.94–0.96 | 0.43 | 0.42 | 0.54 |",
     "| | 1000 – 100 000 | 2.7–2.8 | 0.94–0.96 | 0.43 | 0.42 | 0.54–0.55 |"),
    # ---- 6.1, the high-reserve mode against the SR560; THS4031 in S2 (da_compare.py hr) -------
    ("In the high-reserve mode, which keeps the front end at a gain of 10 for 20 dB more input headroom, the noise is "
     "2.6–2.8 nV/√Hz against the SR560's 9.4–20. The H_HR figures include the LM7171's 8.5 nV/√Hz, which S2 sees "
     "behind a front-end gain of only 10; with the THS4031 in S2 they are 2.0 nV/√Hz (Section 6.5).",
     "In the high-reserve mode, which keeps the front end at a gain of 10 instead of 100 for "
     "$20\\log_{10}(100/10)$ = 20 dB more input headroom, the noise is 2.8 nV/√Hz at 1 kHz and 2.6 nV/√Hz white, "
     "against the SR560's 9.4–20 at 1 kHz. The H_HR figures include the LM7171's 8.5 nV/√Hz (A grade, SNOS760D §5.5, "
     "p. 5), which S2 sees behind a front-end gain of only 10. With the THS4031 in S2 they are 2.0–2.1 nV/√Hz from "
     "1 kHz to 1 MHz, but 4.2–4.7 nV/√Hz at 10 Hz and 3.0 nV/√Hz at 10 MHz, against 9.4–9.6 and 4.85–4.86 with the "
     "LM7171 (`scripts/da_compare.py hr`, `sim/results/da_compare.json`, `noise_H_HR`; Section 6.5)."),
    # ---- 6.2 -----------------------------------------------------------------------------------
    ("H is the input for sources above about 300 Ω and L below.",
     "Which input has the lower noise figure depends on the frequency: L up to a source resistance between 10 and "
     "100 kΩ at 10 Hz and 1 kHz, between 300 Ω and 1 kΩ at 1 MHz and between 30 and 100 Ω at 10 MHz, and H above "
     "it (Table 10)."),
    ("With 1 MΩ, both are attenuated by 20 dB at 1 MHz, so",
     "With 1 MΩ the input networks attenuate both by 41.9 dB (H) and 63.9 dB (L) at 1 MHz (21.9 and 43.8 dB at "
     "100 kHz; `scripts/collect_curves.py zin`, `sim/results/zin_numbers.json`, `sources_archived`), so"),
    ("| 100 Ω | 7.7 | 2.4 | 2.4 | 4.1 |", "| 100 Ω | 7.7 | 2.4 | 2.3 | 4.1 |"),
    ("| 100 kΩ | 0.03 | 0.01 | 3.3 | 18.9 |", "| 100 kΩ | 0.03 | 0.01 | 3.3 | 18.8 |"),
    ("with the SR560's 4 nV/√Hz alone at 1 kHz for comparison.",
     "with the SR560's specified 4 nV/√Hz at 1 kHz alone for comparison (manual, specifications chart, printed "
     "p. 5; data sheet p. 3)."),
    # ---- 6.3, Table 11 ---------------------------------------------------------------------------
    ("*Table 11. Frequency response of the chain (`scripts/chain.py ac`).*",
     "*Table 11. Frequency response of the chain (`scripts/chain.py ac`, `sim/results/chain_ac.json`; the SR560 row "
     "from `scripts/sr560_chain.py`, `sim/results/sr560_chain.json`, its peaking from `sr560_chain_ac_*.npz` by "
     "`scripts/numbers_s6_7.py`). A range covers the gains of its row.*"),
    ("| 25.1–25.2 MHz | 0.00 dB | −0.40 dB | none |", "| 25.0–25.2 MHz | 0.00 dB | −0.40 to −0.41 dB | none |"),
    ("| 14.9 MHz | +0.01 dB | −0.36 dB | 0.17 dB |", "| 14.85–14.87 MHz | +0.01 dB | −0.35 to −0.36 dB | 0.17 dB |"),
    ("| 16.6 MHz | 0.00 dB | −0.80 dB | none |", "| 16.6 MHz | 0.00 dB | −0.80 to −0.81 dB | none |"),
    ("the chain's later stages reach beyond 100 MHz.",
     "the stages after the front end, alone, reach −3 dB at 116–156 MHz (`scripts/chain_extras.py post`, "
     "`sim/results/chain_extras.json`)."),
    ("with the input networks, no source from 50 Ω to 1 MΩ peaks by more than 0.6 dB (Figure 10c).",
     "with the input networks, none of the simulated sources (50 Ω, 1 kΩ and 1 MΩ) peaks by more than 0.6 dB "
     "(0.57 dB, H with 1 kΩ; Figure 10c, `zin_numbers.json`)."),
    # ---- 6.4, the Monte Carlo and Table 12 ------------------------------------------------------
    ("The CMRR was estimated by Monte Carlo over 12 trials per case (`scripts/cmrr_mc.py`). Each trial draws:",
     "The CMRR was estimated by Monte Carlo over 12 trials per case, 6 for the runs with one class of mismatch at a "
     "time (`scripts/cmrr_mc.py`, `sim/results/cmrr_mc.json`). Each trial draws from Gaussian distributions clipped "
     "at 3σ, whose widths are assumptions of this study unless a source is given:"),
    ("- resistors with 0.05 % σ (0.1 % parts), and S2's network with 0.005 % σ;",
     "- resistors with 0.05 % σ (for 0.1 % parts), and S2's network with 0.005 % σ (for a 0.01 % network);"),
    ("- $C_I$, $C_X$ and $C_{node}$ with 1 % σ;",
     "- $C_I$ and $C_X$ with 1 % σ (for 2 % C0G parts); $C_{node}$ is not varied;"),
    ("- the input networks' capacitors with 2.5 % σ, and $R_Z$ with 0.5 %;",
     "- the input networks' capacitors with 2.5 % σ (for 5 % parts), and $R_Z$ with 0.5 %;"),
    ("- JFETs from their data sheets' matching: JFE2140 halves within a dual at 0.85 mV of $V_{TO}$ and 1 % of "
     "$\\beta$; JFE150 from one ±5 mV bin;",
     "- the JFETs: each JFE2140 half with σ 0.85 mV of $V_{TO}$ and 1 % of $\\beta$ about its dual's common offset "
     "(σ 100 mV and 5 %). The two halves of a dual then differ by $\\sqrt2 \\times 0.85$ = 1.20 mV rms, a mean "
     "$\\lvert\\Delta V_{GS}\\rvert$ of $1.20\\sqrt{2/\\pi}$ = 0.96 mV, against the data sheet's 1 mV typical and "
     "4 mV maximum (SLPS730B p. 5, Table 6.5); the data sheet specifies no $\\beta$ matching, only "
     "$I_{DSS1}/I_{DSS2}$ = 0.95–1.05. The JFE150s come from one ±5 mV $V_{GS}$ bin: σ 3 mV of $V_{TO}$ (a uniform "
     "±5 mV spread has $5/\\sqrt3$ = 2.9 mV) and 2 % of $\\beta$ about the bin's common offset (σ 85 mV and 5 %);"),
    ("- the cascodes with 50 mV and 5 %.", "- each LSBF862 cascode with σ 50 mV of $V_{TO}$ and 5 % of $\\beta$."),
    ("*Table 12. CMRR, median of 12 trials (dB), at a total gain of 1000 (H, L) and 100 (H with the front end at ×10).*",
     "*Table 12. CMRR (dB), median of 12 trials (6 in the rows with one class of mismatch), at a total gain of 1000 "
     "(H, L) and 100 (H with the front end at ×10). The SR560 reproduction's row is from `scripts/sr560_chain.py` "
     "(`sim/results/sr560_chain.json`, ideal matching). The SR560's specification is 100 dB to 1 kHz, falling by 6 dB per "
     "octave above (data sheet p. 3), i.e. $100 - 20\\log_{10}(f/1\\ \\mathrm{kHz})$ dB; its manual gives > 90 dB to "
     "1 kHz (printed p. 5). The NF 5307 row is the gain-100 curve of Fig. 46 on NF's data-sheet page "
     "(`refs/commercial_preamps/NF_Corporation/NF_5307_datasheet_fig46.jpg`), read by eye at the table's "
     "frequencies.*"),
    ("| NF 5307 (plot, gain 100) | – | 136 (100 Hz) | 118 (20 kHz) | 100 (200 kHz) | 86 | – |",
     "| NF 5307 (plot, gain 100) | 136 | 136 | 126 | 107 | 86 | – |"),
    ("For L, with 250 pF per input at 2.5 % σ and 50 Ω sources, this gives about 51 dB at 1 MHz, the 55 dB of the "
     "capacitor-only runs. The error is purely capacitive, so one trimmer per input nulls it at all frequencies for a "
     "given source: L recovers 24 dB at 1 MHz.",
     "For L, with $C_P$ = 30 pF and $C_Z$ = 220 pF per input, each with 2.5 % σ, the two inputs differ by "
     "$\\Delta C = \\sqrt2 \\times 2.5\\,\\% \\times \\sqrt{30^2 + 220^2}$ pF = 7.9 pF rms. With 50 Ω sources this "
     "gives 52 dB at 1 MHz, and 56 dB for the median $\\lvert\\Delta C\\rvert$, 0.674 times the rms value, against "
     "the 55 dB median of the capacitor-only runs (`scripts/numbers_s6_7.py`). The error is purely capacitive, so "
     "one trimmer per input nulls it at all frequencies for a given source: L recovers 25 dB at 1 MHz."),
    ("At 10 Hz both front ends sit at 106–114 dB, against 124–132 dB at 1 kHz.",
     "At 10 Hz the front ends sit at 108 dB (L) and 114 dB (H), against 124 dB (H) and 132 dB (L) at 1 kHz with the "
     "inputs driven directly."),
    ("$-(R_{BS}/R_{UP})\\,\\Delta V$ = −0.32 $\\Delta V$ relative to the sources, and below the bootstrap's 45 Hz "
     "corner, where $C_{BS}$ no longer holds that voltage, the input JFETs' $V_{DS}$ follows a third of the common "
     "mode.",
     "$-(R_{BS}/R_{UP})\\,\\Delta V$ = −(3.5 kΩ/10.9 kΩ) $\\Delta V$ = −0.32 $\\Delta V$ relative to the sources, "
     "and below the bootstrap's corner, $1/(2\\pi R_{BS}C_{BS})$ = 45 Hz, where $C_{BS}$ no longer holds that "
     "voltage, the input JFETs' $V_{DS}$ follows about a third of the common mode."),
    ("the CMRR of the JFET-only trials (H, inputs driven directly, 4 trials) rises from 106 to 138 dB at 10 Hz and "
     "from 112 to 138 dB at 100 Hz, and does not change above 10 kHz (`scripts/cmrr_mc.py`, test runs "
     "`sim/runs/cmrr_mc/test_rup_*`).",
     "the median CMRR of the JFET-only trials (H, inputs driven directly, 4 trials) rises from 106.2 to 138.0 dB at "
     "10 Hz and from 111.8 to 137.9 dB at 100 Hz, by 31.8 and 26.1 dB, and changes by at most 0.33 dB from 10 kHz "
     "up (`scripts/cmrr_mc.py`, cases `H100_jfet_rs0_R_UP` and `H100_jfet_rs0_ideal_I_BS`, "
     "`sim/results/cmrr_mc.json`, `rup_test`; the same decks as the first test's in `sim/runs/cmrr_mc/test_rup_*`)."),
    ("leave about 125 dB at low frequencies and do not limit anywhere. Discrete 0.1 % resistors instead of a network "
     "in S2 cost 13 dB at 1 kHz (111 dB).",
     "leave 124–132 dB up to 100 kHz and do not limit anywhere. Discrete 0.1 % resistors instead of a network in S2 "
     "cost 12 dB at 1 kHz (111.5 against 123.8 dB, case `H100_discrete`)."),
    ("*Figure 15. CMRR against frequency, medians of 12 trials:",
     "*Figure 15. CMRR against frequency, medians of 12 trials (6 in panel c):"),
    # ---- 6.5, Table 13 and its text --------------------------------------------------------------
    ("*Table 13. Large-signal results (`scripts/large_signal.py`; `sim/results/large_signal.json`). THD includes "
     "harmonics 2–9 of a differential sine, at the output; H at a total gain of 100 (front end ×100, S2 at the full "
     "output level), L at 1000.*",
     "*Table 13. Large-signal results (`scripts/large_signal.py`; `sim/results/large_signal.json`; L's 10 V step from "
     "`large_signal_L1000_step.json` and H's recovery from `large_signal_THS4031.json`, both reproduced by "
     "`scripts/large_signal.py repro`; L's supply rejection with the 6 V sinks from `sink_power.json`). THD includes "
     "harmonics 2–9 of a differential sine, at the output; H at a total gain of 100 (front end ×100, S2 at the full "
     "output level), L at 1000. S2 is the LM7171 unless stated. L's entries, except the supply rejection, were "
     "simulated with the first design's 2 V sinks (MMBT3904), before the 6 V PZT3904 sinks of Section 4.2.1.*"),
    ("| 0.0008 % / 0.024 % |", "| 0.0008 % / 0.023 % |"),
    ("both dominated by the third harmonic of the chain after the front end. The 10 V step's 312 V/µs gives a "
     "full-power bandwidth of 312 V/µs / (π × 10 V) ≈ 10 MHz for 10 Vpp. Its 9 % overshoot comes from the chain, "
     "not the front end. The distortion in these runs sits close to the numerical floor of the method below about "
     "−110 dBc (0.0003 %): values there vary by several dB with the integration settings.",
     "both dominated by the third harmonic of the chain after the front end. L's value at 10 MHz depends on S2: "
     "0.0078 % with the LM7171, 0.0396 % with the THS4031 (`scripts/large_signal.py floor`, "
     "`sim/results/large_signal_floor.json`). The 10 V step's 312 V/µs gives a full-power bandwidth of "
     "312 V/µs / (π × 10 V) = 9.93 MHz for 10 Vpp. Its 9.4 % overshoot is mostly the front end's own: alone, with "
     "its outputs unloaded, the front end overshoots 8.8 % on the same step, and 9.5 % when S2 loads it. The stages "
     "after S2 limit the slew rate: 395 V/µs at the front end's outputs alone and 390 V/µs at S2's output, against "
     "312 V/µs at the chain's output (`scripts/chain_extras.py step`, `sim/results/chain_extras.json`). "
     "The numerical floor of the THD measurement lies far below these values. The same sources, transient and harmonic "
     "analysis applied to a purely linear reference (an ideal gain and one RC low-pass at the chain's −3 dB "
     "frequency) give −158 to −179 dBc, and five integration settings (Gear, trapezoidal, two tighter tolerances, "
     "four times finer steps) change H's THD at 1 Vpp by at most 0.4 dB: −122.0 to −122.1 dBc at 1 kHz, −121.0 to "
     "−121.4 dBc at 100 kHz and −101.2 dBc at 1 MHz (`large_signal_floor.json`)."),
    ("When the input returns, the output undershoots by 1.3 V for about 0.1 µs and settles within 0.15 µs.",
     "When the input returns, the output undershoots by 1.38 V, stays more than 0.1 V below its final value for "
     "33 ns, and settles within 0.15 µs (`sim/results/overload_numbers.json`)."),
    ("When the input returns, the front end's outputs swing through about −1.9 and +2.6 V and are back within 12 mV "
     "of rest after 0.2 µs. The output is within 0.1 V after 0.19 µs; its ramp after the first 85 ns is S2's slew "
     "rate (Figure 16d).",
     "When the input returns, the front end's outputs swing to −2.15 V (side A) and +2.88 V (side B), 2.50 and "
     "2.53 V from rest, and are back within 12 mV of rest after 0.19 µs. The output is within 0.1 V after 0.19 µs: "
     "after a delay of 86 ns it returns with a 10–90 % slope of 112 V/µs and peaks of 268 V/µs over 5 ns, not at a "
     "constant slew rate (Figure 16d)."),
    ("(These waveforms are from the run with the THS4031 in S2, `sim/results/overload_curves_H100_THS4031.npz`.",
     "(These waveforms are from the run with the THS4031 in S2, `sim/results/overload_curves_H100_THS4031.npz`, "
     "and the numbers from `scripts/overload_detail.py numbers`, `sim/results/overload_numbers.json`."),
    ("In the H run they still follow to within +23 mV (side A) and −8 mV (side B),",
     "In the H run they still follow to within +23.5 mV (side A) and −7.9 mV (side B),"),
    ("These small $V_{GS}$ changes, far from the +0.36 V that would forward-bias a gate, shift the JFETs' current by "
     "up to 0.8 mA per side. The clipped integrators cannot cancel that, so each summing node moves until $R_D$ "
     "carries the difference, $\\Delta V = \\Delta I\\,R_D$: from 8.99 V to 8.56 V (side A) and 9.13 V (side B). "
     "Nothing winds up beyond this: the summing nodes return with the outputs, within 0.2 µs.",
     "These small $V_{GS}$ changes, far from the +0.36 V that would bring a gate to zero bias ($V_{GS}$ = −0.36 V at "
     "rest, Table 5), still shift the JFETs' current. The clipped integrators cannot cancel that, so each summing "
     "node moves until $R_D$ carries the difference: from 8.99 V to 8.56 V (side A) and 9.13 V (side B), i.e. "
     "$\\Delta I = -\\Delta V/R_D$ = +0.72 mA and −0.23 mA with $R_D$ = 600 Ω ($g_m\\Delta V_{GS}$ gives +0.81 and "
     "−0.27 mA). Nothing winds up beyond this: the summing nodes are back within 10 mV of rest 0.11 µs after the "
     "input returns."),
    ("The common-mode servo sees this −0.12 V as an error and integrates it at about 0.12 V/s, which is a few "
     "microvolts over 20 µs but would matter",
     "The common-mode servo sees this −0.12 V as its error $e$ and integrates it, with its transconductance "
     "$G_{INT}$ = 1 µS into $C_{INT}$ = 1 µF (Section 4.2), at $G_{INT}e/C_{INT}$ = 0.12 V/s, which is 2.4 µV over "
     "20 µs but would matter"),
    ("- **Larger overloads.** At about ten times full scale on H (1 V differential), $V_{GS}$ of one side would reach "
     "the gate's forward voltage and the input would draw gate current. The tenfold run stopped with \"timestep too "
     "small\" in an input JFET.",
     "- **Larger overloads.** With the op amps clipped, the source nodes sit on the divider $R_F$–$R_G$–$R_F$ "
     "between the clipped outputs, so they differ by $(v_{oa} - v_{ob})\\,R_G/(2R_F + R_G)$ = "
     "26.4 V × 10.1 Ω / 1010.1 Ω = 0.26 V, and each side's $V_{GS}$ changes by about $(v_{in} - 0.26\\ \\mathrm{V})/2$ "
     "(the JFETs' own current change neglected): 0.37 V at ten times full scale on H (1 V differential). One gate "
     "reaches zero bias at 0.97 V, 9.7 times full scale (`overload_numbers.json`), and beyond that it approaches "
     "forward bias and the input draws gate current. No run at this level is archived."),
    ("After one second it would have moved the sinks' reference by about 0.12 V, i.e. the outputs' common mode by "
     "about 0.3 V, which then decays with the servo's time constant of about 0.4 s.",
     "After one second it would have moved the sinks' reference by $G_{INT}e\\,(1\\ \\mathrm{s})/C_{INT}$ = 0.12 V, "
     "i.e. the outputs' common mode by $R_F/R_T$ = 500 Ω/182 Ω = 2.75 times that, 0.33 V, which then decays with the "
     "servo loop's time constant $(C_{INT}/G_{INT})(R_T/R_F)$ = 0.36 s (`overload_numbers.json`)."),
    ("$C_{BS}$ (1 µF behind 3.5 kΩ, a 3.5 ms time constant)",
     "$C_{BS}$ (1 µF behind $R_{BS}$ = 3.5 kΩ, $R_{BS}C_{BS}$ = 3.5 ms)"),
    # ---- 6.5, Table 14 and the choice of S2 ------------------------------------------------------
    ("*Table 14. The difference amplifier S2 (H, total gain 100; `scripts/da_compare.py`). Noise is the "
     "input-referred white level (1 MHz) and the 1 kHz value.*",
     "*Table 14. The difference amplifier S2 (H, total gain 100; `scripts/da_compare.py`, "
     "`sim/results/da_compare.json`; slew rates from `large_signal_THS4031.json` and `large_signal.json`). The first "
     "column gives data-sheet values: THS4031, SLOS224L pp. 1 and 6; LM7171 A grade, SNOS760D §5.5, p. 5; THS3091, "
     "SLOS423K pp. 1 and 6. Noise is the simulated input-referred white level (1 MHz) and the 1 kHz value, from each "
     "part's model (the LM7171's raised to its data sheet's, `scripts/models.py`).*"),
    ("| THS4031 (1.6 nV/√Hz, 100 MHz) |", "| THS4031 (1.2 nV/√Hz, 100 MHz at a gain of 2) |"),
    ("| LM7171, A grade (8.5 nV/√Hz, 4100 V/µs) |", "| LM7171, A grade (8.5 nV/√Hz, 4100 V/µs, 160 MHz) |"),
    ("| THS3091 (2 nV/√Hz, current feedback, 1 kΩ) |",
     "| THS3091 (1.1 nV/√Hz, its model 1.9; current feedback, so S2's resistors are 1 kΩ instead of 499 Ω) |"),
    ("The THS4031's third harmonic at 10 MHz (−38 dBc at 1 Vpp) is about 20 dB higher than its data sheet would "
     "suggest (Section 5.3), but even the data sheet's −50 dBc at 2 Vpp would leave it ten times worse than the "
     "LM7171.",
     "The THS4031's third harmonic at 10 MHz (−38 dBc at 1 Vpp) is 12 dB above the data sheet's −50 dBc at 2 Vpp "
     "(SLOS224L Fig. 5-15, p. 12, read by eye), and 24 dB above it once that is scaled to 1 Vpp as $V^2$, i.e. to "
     "−62 dBc (Section 5.3, `model_defects.json`). Even −62 dBc would leave it 17 dB, 6.9 times, above the LM7171's "
     "−79 dBc."),
    ("3.94 against 3.56 nV/√Hz at a total gain of 10, and 2.6 against 2.0 nV/√Hz in the high-reserve mode.",
     "3.94 against 3.56 nV/√Hz at a total gain of 10, and in the high-reserve mode 2.6 against 2.0 nV/√Hz white and "
     "2.8 against 2.0–2.1 nV/√Hz at 1 kHz (Section 6.1)."),
    ("(H with the THS4031 in S2, whose 133 V/µs sets the output's ramp after 85 ns; L with the LM7171, driven from "
     "50 Ω)",
     "(H with the THS4031 in S2: after 86 ns the output returns with a 10–90 % slope of 112 V/µs; L with the LM7171, "
     "driven from 50 Ω; `overload_numbers.json`)"),
    # ---- 6.6, Table 15 ---------------------------------------------------------------------------
    ("and the NF 5307 (its documents). Input noise in nV/√Hz.*",
     "and the NF 5307 (its documents). Input noise in nV/√Hz. SR560: manual, specifications chart (printed p. 5), "
     "noise curve (printed p. 20) and noise table (printed p. 21), and data sheet p. 3. NF 5307: specifications sheet "
     "(`NF_5307_specifications_EN.pdf`); noise plot, instruction manual Fig. 4.7 (PDF p. 37, printed p. 25); CMRR "
     "plot, Fig. 46 of NF's data-sheet page; the plots read by eye. This design: Tables 9, 11 and 12; input "
     "capacitance $C_P + C_Z$ (`protection.json`).*"),
    ("| Input noise, white / 1 kHz, gain ≥ 100 | 4 (1 kHz) | 3.2 / 5.7 | 4 (spec.); 2.5–3 (plot) |",
     "| Input noise, white / 1 kHz, gain ≥ 1000 | 4 (1 kHz) | 3.2 / 5.7 | 4 (spec., 1 kHz); ≈ 3 (plot, gain 100) |"),
    ("| Input noise at 10 Hz | ≈ 11 (typical curve) | 48 (model's 1/f overstated) | ≈ 4 (plot) | 2.8 | 0.96 |",
     "| Input noise at 10 Hz, gain ≥ 1000 | ≈ 11 (typical curve) | 48 (model's 1/f overstated) | ≈ 6 (plot, gain 100) "
     "| 2.8 | 0.94–0.96 |"),
    ("| 15 (plot, ×10) |", "| 15–16 (plot) |"),
    ("| Bandwidth (−3 dB) | 1 MHz | 0.73–0.79 MHz | 10 MHz (+0.2/−3 dB) | 14.9 MHz (25 MHz at ×10) |",
     "| Bandwidth (−3 dB) | 1 MHz (1.2 MHz typ., data sheet) | 0.73–0.79 MHz | 10 MHz (+0.2/−3 dB) | 14.85–14.87 MHz "
     "(25.0–25.2 MHz at ×10) |"),
    ("| CMRR at 1 kHz / 1 MHz | 100 dB / 40 dB | 102.5 / 61.6 dB (matched) | 120 dB (DC–1 kHz) / 86 dB |",
     "| CMRR at 1 kHz / 1 MHz | 100 dB / 40 dB (data sheet; manual > 90 / > 30 dB) | 102.5 / 61.6 dB (matched) | "
     "≥ 120 dB (DC–1 kHz, gain 1000) / 86 dB (plot, gain 100) |"),
    # ---- 7 -----------------------------------------------------------------------------------------
    ("**The common-mode local loop at about 270 MHz.** The final front ends keep 8–10 dB of gain margin in a mode",
     "**The common-mode local loop near 250 MHz (H) and 205 MHz (L).** The final front ends keep 8–10 dB of gain "
     "margin at the frequency where the common-mode return ratio at the op amp's output crosses −180° "
     "(`curves_loop.npz` with `frontend._margins`, interpolated by `scripts/numbers_s6_7.py`), in a mode"),
    ("The THS4031's 10 MHz distortion is known to be about 20 dB too high in its model;",
     "The THS4031 model's third harmonic at 10 MHz is 12 dB above its data sheet's as read, and 24 dB above once "
     "scaled to the same level (Sections 5.3 and 6.5);"),
    ("The CMRR Monte Carlo and the large-signal runs were not repeated; the sinks'",
     "The CMRR Monte Carlo and the large-signal runs were not repeated, except the THD at 10 MHz and 1 Vpp (0.0072 % "
     "with the 6 V sinks against 0.0078 %, `large_signal_floor.json`); the sinks'"),
    ("The leakage of the protection and the relay adds current noise that matters for H above about 100 kΩ of source "
     "impedance. The bias resistors (100 MΩ for H) add $\\sqrt{4kT/R}$ = 13 fA/√Hz.",
     "The bias resistors (100 MΩ for H) add $\\sqrt{4kT/R}$ = 13 fA/√Hz at 300.15 K, and the leakage of the "
     "protection and the relay adds its shot noise. For H, the total equals the voltage noise of 1.08 nV/√Hz at "
     "84 kΩ of source impedance with the bias resistor alone, and at 49 kΩ with 1 nA of leakage "
     "(`scripts/protection.py`, `sim/results/protection.json`)."),
    ("raises the low-frequency CMRR by about 30 dB in the ideal test of Section 6.4;",
     "raises the low-frequency CMRR by 32 dB at 10 Hz and 26 dB at 100 Hz in the ideal test of Section 6.4;"),
    # ---- Appendix ----------------------------------------------------------------------------------
    ("The first front ends of this note oscillated at 290 MHz in common mode for that reason (Section 4.3).",
     "The first front ends of this note oscillated in common mode for that reason, H at 293 MHz with 50 Ω sources "
     "and 283 MHz with its inputs tied through 1 mΩ, L at 277 and 230 MHz (`scripts/osc_check.py first`, "
     "`sim/results/osc_check.json`; Section 4.3)."),
    ("kept ngspice's dynamic gmin stepping busy for over half an hour, and",
     "hung in ngspice's dynamic gmin stepping, and"),
    ("Fixed-step gmin stepping (`gminsteps=20`) failed fast but also made every good trial fail.",
     "Fixed-step gmin stepping (`gminsteps`) failed fast but also made good trials fail; no deck of that attempt is "
     "archived."),
    ("The large-signal benches retry with three sets (`tran` in `scripts/large_signal.py`) and record which one ran.",
     "The large-signal benches try three sets of options in turn and then the inputs driven from 50 Ω (`tran` in "
     "`scripts/large_signal.py`), and record which one ran."),
    ("LTspice's 2N5564 card has KF = 67860f where its source has 6.786e-002f, a factor of 10⁶ (Section 5.3).",
     "LTspice's 2N5564 card has KF = 67860f where Linear Systems' own listing has 6.786e-002f, a factor of 10⁶ "
     "(Section 5.3). The card read is in `lib/cmp/standard.jft` of LTspice 26.1.1.0 (file dated 20 September 2026, "
     "SHA-256 82bdc4a4…3557; the change log's last JFET entry is \"06/26/23 Updated JFET device models from Linear "
     "Systems\"), recorded in `sim/results/model_defects.json` (`ltspice_library`)."),
]


def offset(lines: list[str], i: int) -> int:
    """Character offset of the start of line i (0-based) of the text split into lines."""
    return sum(len(x) + 1 for x in lines[:i])


def main(path: str) -> None:
    p = Path(path)
    s = p.read_text(encoding="utf-8")
    assert "\r" not in s, "expected \\n newlines"
    lines = s.split("\n")
    at = {}
    for h in (START, SEC8, APPENDIX, END):
        found = [i for i, x in enumerate(lines) if x == h]
        assert len(found) == 1, f"heading {h!r} found {len(found)} times"
        at[h] = found[0]
    i0, i8, ia, ie = at[START], at[SEC8], at[APPENDIX], at[END]
    assert i0 < i8 < ia < ie
    print(f"range: lines {i0 + 1}-{i8} and {ia + 1}-{ie} (Section 8, lines {i8 + 1}-{ia}, left alone)")
    a1, b1, a2, b2 = offset(lines, i0), offset(lines, i8), offset(lines, ia), offset(lines, ie)
    head, part1, sec8, part2, tail = s[:a1], s[a1:b1], s[b1:a2], s[a2:b2], s[b2:]
    parts = [part1, part2]
    for old, new in EDITS:
        assert old.count("\n") == new.count("\n") == 0, f"an edit may not add or remove lines: {old[:80]!r}"
        whole = head + parts[0] + sec8 + parts[1] + tail
        assert whole.count(old) == 1, f"not exactly once ({whole.count(old)}): {old[:80]!r}"
        k = [i for i, t in enumerate(parts) if old in t]
        assert len(k) == 1, f"outside the range (or in Section 8): {old[:80]!r}"
        parts[k[0]] = parts[k[0]].replace(old, new, 1)
    out = head + parts[0] + sec8 + parts[1] + tail
    assert out.startswith(head) and out.endswith(tail) and sec8 in out
    assert out.count("\n") == s.count("\n")
    p.write_text(out, encoding="utf-8", newline="\n")
    print(f"{len(EDITS)} replacements applied to {p}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python patch_s6_7.py <path to low_noise_preamp.md>")
    main(sys.argv[1])
