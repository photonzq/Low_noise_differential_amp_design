"""Patch of low_noise_preamp.md, Sections 4.1-4.3.1 (lines 253-583 of the note as audited on
21 November 2026): the fixes of Audit B (audit/number_audit_2026-11-21.md) and of the low-voltage
option's paragraphs, with the numbers of scripts/numbers_s4a.py (sim/results/numbers_s4a.json) and
the archived results named in the text.

Only the text from the heading "## 4. The new design" up to (not including) the heading
"### 4.4 The input: ..." is edited, so the patch can be applied before or after the patches of the
other ranges.  Every replacement is an exact string that must occur exactly once in that range.
UTF-8, newlines "\n".

Usage: python patch_s4a.py <path to low_noise_preamp.md>      (the file is rewritten in place)
"""
from __future__ import annotations

import sys
from pathlib import Path

START = "## 4. The new design\n"
END = "### 4.4 The input: bootstrapping, negative conductance and damping\n"

# (line in the audited note, old, new)
REPLACEMENTS = [
    # 275: headroom as an expression; the noise ratio from chain_noise.json (Table 9's columns)
    (275,
     "in the high-reserve mode H_HR it stays at 10, giving 20 dB more headroom at the input for 2.4 times "
     "the noise (Table 9);",
     "in the high-reserve mode H_HR it stays at 10, giving $20\\log_{10}(100/10)$ = 20 dB more headroom at "
     "the input for 2.3–2.5 times the noise at 1 kHz and 100 kHz, at total gains of 100 and 1000 (Table 9; "
     "`scripts/numbers_s4a.py`);"),
    # 277: Table 5's operating-point values and capacitances now come from a script
    (277,
     "*Table 5. The two front ends (`scripts/frontend.py`, `CASES`).*",
     "*Table 5. The two front ends (`scripts/frontend.py`, `CASES`). The operating-point values come from "
     "`frontend.check_op`, collected with the JFET capacitances in `scripts/numbers_s4a.py` "
     "(`sim/results/numbers_s4a.json`).*"),
    # 293: N C_iss with its data-sheet source, and the model's value at the operating point
    (293,
     "| JFET capacitance per input | 26 pF | 288 pF |",
     "| JFET capacitance per input, $NC_{iss}$ | 26 pF: 2 × 13 pF at $V_{DS}$ = 5 V (TI SLPS730B, p. 5); "
     "25 pF in the model at the operating point | 288 pF: 12 × 24 pF at $V_{DS}$ = 5 V (TI SLPS732B, p. 5); "
     "279 pF in the model |"),
    # 309: page of the design example (repository version: dc to 100 kHz, JFE2140, p. 4)
    (309,
     "(Spinelli and Haberman 2024 built it with JFE2140s for DC–100 kHz)",
     "(Spinelli and Haberman 2024 built it with JFE2140s for DC–100 kHz, p. 4)"),
    # 330: the error formula; V_BE drift from the model; output drift from the simulation; 3 % assumed
    (330,
     "A 1 % error in H's 11 mA sink is 110 µA, which moves the output by 55 mV; in L's 61 mA sink it moves "
     "the output by 152 mV. The sink's $V_{BE}$ (−2 mV/K across the 2 V on $R_T$) adds −0.1 % per kelvin, "
     "i.e. tens of millivolts of output per kelvin. A few percent of error would put the outputs volts away "
     "from the sources and use up the op amps' swing.",
     "An error $\\varepsilon$ moves the output by $\\varepsilon\\,(NI_D + I_{BS})\\,R_F$: 1 % of H's 11 mA "
     "is 110 µA, which moves the output by 55 mV; in L's 61 mA sink it moves the output by 152 mV. In H, the "
     "sink's $V_{BE}$ falls by 1.7 mV/K (the MMBT3904 model at its operating point, `fe_closed_forms.json`), "
     "so its current rises by 1.7 mV / 2 V ≈ 0.09 % per kelvin; the outputs move by 4.9 mV per kelvin, in H "
     "and in L alike (the simulated drift of Section 4.6). An error of 3 %, an assumed figure, would put H's "
     "outputs 0.17 V and L's 0.46 V away from the sources."),
    # 343: the 0.05 % mismatch is an assumption; arithmetic written out
    (343,
     "0.05 % of 11 mA gives 2.8 mV at H's outputs, 28 µV referred to the input.",
     "an assumed 0.05 % of 11 mA, 5.5 µA, gives 2.75 mV at H's outputs, 27.5 µV referred to the input."),
    # 344: the crossover computed below
    (344,
     "Its loop crosses over below 1 Hz, far below any signal of interest.",
     "Its loop crosses over at about 0.4 Hz (below), far below any signal of interest."),
    # 347: servo arithmetic; R_F / R_T = 2.75 (not 2.7); crossover and phase margin computed
    (347,
     "which gives an integrator with unity gain at 0.16 Hz, and its output sets vsink through 1 kΩ and 10 µF, "
     "a 16 Hz filter that keeps the integrator's noise from the sinks. A change of the base reference changes "
     "each sink's current by $\\Delta V/R_T$ and each output by $(R_F/R_T)\\,\\Delta V$ (2.7 V per volt for "
     "H), so the servo loop crosses over at about 0.4 Hz with nearly 90° of phase margin.",
     "which gives an integrator with unity gain at 1 µS/(2π × 1 µF) = 0.16 Hz, and its output sets vsink "
     "through 1 kΩ and 10 µF, a 1/(2π × 1 kΩ × 10 µF) = 16 Hz filter that keeps the integrator's noise from "
     "the sinks. A change of the base reference changes each sink's current by $\\Delta V/R_T$ and each "
     "output by $(R_F/R_T)\\,\\Delta V$: 500 Ω/181.8 Ω = 2.75 V per volt for H, 249 Ω/98.4 Ω = 2.53 for L. "
     "The servo loop therefore crosses over at 2.75 × 0.16 Hz = 0.44 Hz for H (0.40 Hz for L), where the "
     "16 Hz filter takes 1.6° of phase, leaving 88° of phase margin (`scripts/numbers_s4a.py`)."),
    # 349: the clamp as coded (frontend.py), with L's limit and the sinks' bases (sink_power.json)
    (349,
     "The servo's output must be limited, here to between $V_M$ + 1 V and $V_M$ + 5 V.",
     "The servo's output must be limited, here to between $V_M$ + 1 V and $V_M + V_{RT}$ + 3 V: $V_M$ + 5 V "
     "for H and $V_M$ + 9 V for L. The sinks' bases sit at $V_M$ + 2.8 V in H and $V_M$ + 6.9 V in L "
     "(operating points in `sink_power.json`)."),
    # 352: the resistor's noise current as an expression
    (352,
     "and each adds 0.4 pA/√Hz into a low-impedance source node;",
     "and each adds $\\sqrt{4kT/100\\ \\mathrm{k\\Omega}}$ = 0.4 pA/√Hz into a low-impedance source node;"),
    # 355: corner computed; the NPN cascode's base current and noise from a run (MMBTH10, numbers_s4a.py)
    (355,
     "$1/(2\\pi R_{BS}C_{BS})$ ≈ 45 Hz. A JFET cascode was chosen over an NPN because an NPN's base current "
     "(about 50 µA at 5 mA) has a shot noise that the bootstrap network turns into 0.25 nV/√Hz at the input, "
     "while a JFET cascode has none.",
     "$1/(2\\pi R_{BS}C_{BS})$ = 1/(2π × 3.5 kΩ × 1 µF) = 45 Hz. A JFET cascode was chosen over an NPN "
     "because an NPN's base current (48 µA at 5 mA in the MMBTH10 model) has a shot noise that the bootstrap "
     "network turns into 0.26 nV/√Hz at the input (H at a gain of 100 with MMBTH10 cascodes, 10 kHz; "
     "`scripts/numbers_s4a.py`), while a JFET cascode has none."),
    # 379: frequency and sources of the two terms (Table 6c's 10 kHz values; curves_noise.npz for L)
    (379,
     "The first two terms dominate, 0.93 and 0.41 nV/√Hz for H at a gain of 100 and 0.33 and 0.20 nV/√Hz "
     "for L.",
     "The first two terms dominate: at 10 kHz the JFETs give 0.94 nV/√Hz and $R_G$ 0.40 nV/√Hz for H at a "
     "gain of 100 (Table 6c), and 0.33 and 0.20 nV/√Hz for L (`sim/results/curves_noise.npz`)."),
    # 384: N g_m from the operating point (Table 5), not Section 6.1; frequency of the contributions
    (384,
     "(35 mS per side for H and 308 mS for L, Section 6.1) and $R_G$ is small. For H at a gain of 100 the "
     "simulated contributions are",
     "(2 × 17.3 = 35 mS per side for H and 12 × 25.7 = 308 mS for L, Table 5) and $R_G$ is small. For H at "
     "a gain of 100 the simulated contributions at 10 kHz are"),
    # 386: the paper's values (p. 5) and the arithmetic
    (386,
     "The second part is negligible at their gain of 1000 with an $R_A$ of a few ohms.",
     "The second part, $R_B/G_n$ = 500 Ω/1001 = 0.50 Ω, is negligible against their $1/g_m$ ≈ 1/(30 mS) "
     "= 33 Ω, at their gain of 1001 with $R_A$ = 1 Ω and $R_B$ = 500 Ω (p. 5)."),
    # 390: the source node's current and R_T's current (base current included) told apart
    (390,
     "Each source node's DC current, the JFETs' plus the bootstrap's, leaves through its sink to −15 V: "
     "11.1 mA per side for H and 61.9 mA for L (operating point).",
     "Each source node's DC current, the JFETs' plus the bootstrap's, 11.0 mA per side for H and 61.1 mA "
     "for L, leaves through its sink to −15 V; with the sink's base current, $R_T$ carries $I_T$ = 11.1 mA "
     "and 61.9 mA (operating point, `scripts/numbers_s4a.py`)."),
    # 404/408: V_CE,min stated as a design margin with the data sheets' V_CE(sat)
    (408,
     "with the sink's emitter at $V_E \\approx V_M + V_{RT}$. The design takes 6 V:",
     "with the sink's emitter at $V_E \\approx V_M + V_{RT}$, and $V_{CE,min}$ a design margin above the "
     "data sheets' $V_{CE(sat)}$ of at most 0.2 V at 10 mA and 0.3 V at 50 mA, both with $I_B = I_C/10$ "
     "(onsemi MMBT3904LT1/D and PZT3904T1/D, p. 2). The design takes 6 V:"),
    # 447: 1/k_DM written; Figure 9a's annotation in Table 6's convention
    (447,
     "so without $C_X$ the common-mode loop has 6.7 times the differential loop's gain, and it was unstable "
     "with the $C_I$ of 1.1 pF that the differential loop wanted (Figure 9a: phase margin −88° at 179 MHz).",
     "so without $C_X$ the common-mode loop has $1/k_{DM}$ = 6.7 times the differential loop's gain, and it "
     "was unstable with the $C_I$ of 1.1 pF that the differential loop wanted (Figure 9a, d: phase margin "
     "−97° at 189 MHz)."),
    # 449: minimum stable gain cited
    (449,
     "The THS4021 is decompensated: it is stable only at a noise gain of about 10 or more.",
     "The THS4021 is decompensated: it is stable only at gains of 10 V/V or more (TI SLOS265F, p. 1), i.e. "
     "at a noise gain of about 10 or more."),
    # 449: beta_CM of the first version computed with C_par
    (449,
     "In the first version ($C_I$ = 6.19 pF, $C_X$ = 4.42 pF, no added $C_{node}$), $\\beta_{CM}$ was about "
     "0.5.",
     "In the first version ($C_I$ = 6.19 pF, $C_X$ = 4.42 pF, no added $C_{node}$), the summing node had "
     "only its own 10.1 pF (the cascodes' $C_{gd}$ and the op amp's input, $C_{par}$ of Eq. (10a)), so "
     "$\\beta_{CM}$ = 10.61/(10.61 + 10.1) = 0.51."),
    # 449: the oscillation with its bench (osc_check.json); Figure 9b in Table 6's convention
    (449,
     "But a transient run with the inputs quiet showed both outputs swinging 1 V peak to peak in common mode "
     "at about 290 MHz, and the return ratio taken at the op amp's output pin, which every loop passes "
     "through, showed why: a common-mode crossover at 452 MHz with −80° of phase margin (Figure 9b).",
     "But a transient run with the inputs quiet showed both outputs swinging 1.0 V peak to peak in common "
     "mode at 283 MHz with the inputs tied to ground through 1 mΩ, the bench of the first runs (293 MHz with "
     "50 Ω sources and the input network; `sim/results/osc_check.json`). The return ratio taken at the op "
     "amp's output pin, which every loop passes through, showed why: a common-mode crossover at 452 MHz with "
     "−80° of phase margin (Figure 9b, e)."),
    # 451: beta_CM and beta_DM of the final values, with C_par
    (451,
     "lowers $\\beta_{CM}$ below 0.1. In differential mode, however, the same capacitor lowers $\\beta_{DM}$ "
     "to $(C_I - C_X)/(C_I + C_X + C_{node})$, about 0.02,",
     "lowers $\\beta_{CM}$ below 0.1: with 220 pF, to 14/(14 + 220 + 10.1) = 0.057 for H. In differential "
     "mode, however, the same capacitor lowers $\\beta_{DM}$ to $(C_I - C_X)/(C_I + C_X + C_{node} + "
     "C_{par})$ = 4/244 = 0.016,"),
    # 451: bandwidth before/after from archived runs; noise at 10 MHz with the adopted L; oscillation benches
    (451,
     "The front ends' bandwidth falls from about 30 MHz to 15–26 MHz, and the loop op amps' voltage noise, "
     "which now drives $C_{node}$, raises the noise above a few MHz: 1.50 against 1.07 nV/√Hz at 10 MHz for "
     "H, 0.51 against 0.41 for L (Eq. (9), last term). A transient run with the final values shows no "
     "oscillation (≤ 1 µV peak to peak at the outputs, `scripts/osc_check.py`); the same bench run with the "
     "first version oscillated at 293 MHz with 1 V peak to peak.",
     "At a total gain of 100 the chain's bandwidth falls from 30.1 MHz with the first front end "
     "(`da_compare_before_cnode.json`) to 14.8 MHz (`chain_ac.json`); the front ends alone now reach 15 MHz "
     "(H at 100), 26 MHz (H at 10) and 17 MHz (L). The loop op amps' voltage noise, which now drives "
     "$C_{node}$, raises the noise above a few MHz: at 10 MHz it is 1.50 nV/√Hz for H and 0.50 for L, against "
     "white floors of 1.07 and 0.41 (Eq. (9), last term; `fe_gain_options.json`, `sink_power.json`). A "
     "transient run with the final values shows no oscillation (≤ 1 µV peak to peak at the outputs, "
     "`scripts/osc_check.py`); the same bench, 50 Ω sources and the input network, run with the first "
     "versions oscillated in common mode at 293 MHz with 1.0 V peak to peak (H) and at 277 MHz with 0.78 V "
     "(L)."),
    # 453: Table 6's convention, source file, and L's sinks
    (453,
     "*Table 6. Loop margins of the final front ends: the outer loop broken at $R_F$ (crossover, phase "
     "margin, gain margin) and the complete loop broken at the op amp's output pin (`scripts/collect_curves.py`, "
     "`loop`).*",
     "*Table 6. Loop margins of the final front ends and of H's first version: the outer loop broken at $R_F$ "
     "(crossover, phase margin, gain margin) and the complete loop broken at the op amp's output pin "
     "(`scripts/collect_curves.py`, `loop`; `sim/results/curves_loop.npz`). Each crossover and its phase "
     "margin are read at the first point of the sweep past the crossing. L was simulated with its first "
     "sinks (MMBT3904, 2 V); with the adopted PZT3904 at 6 V, `sink_power.json` gives the same complete-loop "
     "margins within 0.1° and 0.1 dB.*"),
    # 459: 51.45 deg rounds to 51
    (459,
     "| L | 10.6 MHz, 66°, 18 dB | 20 MHz, 63°, 12 dB | 27 MHz, 63°, 17 dB | 57 MHz, 52°, 10 dB |",
     "| L | 10.6 MHz, 66°, 18 dB | 20 MHz, 63°, 12 dB | 27 MHz, 63°, 17 dB | 57 MHz, 51°, 10 dB |"),
    # 464: Figure 9's annotations, now in Table 6's convention
    (464,
     "*Figure 9. The front end's compensation in three steps (H, gain 100): (a, d) without the cross-coupled "
     "capacitors, the common-mode outer loop is unstable; (b, e) with them but without $C_{node}$, the outer "
     "loops are stable but the op amp's own common-mode loop is not, which only a loop broken at the op amp's "
     "output shows; (c, f) the final values.*",
     "*Figure 9. The front end's compensation in three steps (H, gain 100): (a, d) without the cross-coupled "
     "capacitors ($C_I$ = 1.1 pF only, loop broken at $R_F$), the common-mode outer loop is unstable, −97° at "
     "189 MHz; (b, e) with them but without $C_{node}$, the outer loops are stable but the op amp's own "
     "common-mode loop is not, −80° at 452 MHz, which only a loop broken at the op amp's output shows; (c, f) "
     "the final values. The crossovers and phase margins printed in (d)–(f) follow Table 6's convention "
     "(`scripts/make_figures.py`, from `curves_loop.npz`).*"),
    # 466: gain margins and the -180 deg crossings (curves_loop.npz)
    (466,
     "The remaining common-mode gain margin, 8–10 dB at about 270 MHz, depends on",
     "The remaining common-mode gain margin, 8.4 dB for H and 10 dB for L where the phase crosses −180° "
     "(251 and 204 MHz, interpolated between the points of `curves_loop.npz`), depends on"),
    # 472: minimum stable gain cited
    (472,
     "(the THS4021 needs a noise gain of about 10 or more)",
     "(the THS4021 is stable at gains of 10 V/V or more, SLOS265F p. 1)"),
    # 479: C_par computed (cascodes' C_gd at bias, THS4021's C_i); beta_CM computed; 0.1 cited
    (479,
     "and with no added $C_{node}$ it was about 0.5, far above the 0.1 that the op amp tolerates.",
     "where $C_{par}$ is the summing node's own capacitance: the cascodes' $C_{gd}$ at their bias, 4.3 pF "
     "each ($V_{GD}$ = −5.0 V; the LSBF862 card's CGD = 14.3 pF and PB = 0.5 V in "
     "$\\mathrm{CGD}/\\sqrt{1 - V_{GD}/\\mathrm{PB}}$, ngspice's grading exponent 0.5), and the THS4021's "
     "input capacitance of 1.5 pF (SLOS265F p. 7), 10.1 pF in all for H. With no added $C_{node}$, "
     "$\\beta_{CM}$ was 10.61/(10.61 + 10.1) = 0.51, far above the 0.1 that the op amp tolerates (1/10, "
     "from its minimum stable gain)."),
    # 482: Eq. (10b) with the data sheet's 2 GHz
    (482,
     "\\approx 1.6\\ \\mathrm{GHz} \\times 0.15 \\times 0.1 \\approx 24\\ \\mathrm{MHz}",
     "\\approx 2\\ \\mathrm{GHz} \\times 0.15 \\times 0.1 \\approx 30\\ \\mathrm{MHz}"),
    # 486: GBW cited; the adopted values are not equalised (D/S against k_DM), their local bandwidth
    (486,
     "for H at a gain of 100. This bound, not the JFETs, limits the front end's bandwidth once $C_{node}$ "
     "makes the common-mode loop stable.",
     "for H at a gain of 100, with the THS4021's gain–bandwidth product of 2 GHz (SLOS265F p. 1; "
     "`scripts/numbers_s4a.py`). This bound, not the JFETs, limits the front end's bandwidth once $C_{node}$ "
     "makes the common-mode loop stable. The adopted H values do not equalise the outer loops: their $D/S$ "
     "= 4/14 = 0.29 is about twice $k_{DM}$, which slows the differential outer loop (8.9 against 21 MHz, "
     "Table 6) and raises the differential local bandwidth to $\\mathrm{GBW}\\,\\beta_{DM}$ = 2 GHz × 0.0164 "
     "= 33 MHz."),
    # 488: the 0.5 minimum stated as this note's design rule
    (488,
     "and 0.5 (a 6 dB peak) is a common minimum for a robust loop.",
     "and this note takes 0.5 (a 6 dB peak) as its minimum for a robust loop, a design rule (rule 4 below)."),
    # 490: Table 6a's source and L's sinks
    (490,
     "phase margin, gain margin and modulus margin, in differential (DM) and common mode (CM).*",
     "phase margin, gain margin and modulus margin, in differential (DM) and common mode (CM) "
     "(`sim/results/stability_corners.json`; L with its first sinks, as in Table 6).*"),
    # 494-497: single roundings of stability_corners.json
    (494,
     "| Nominal | 60°, 19 dB, 0.89 | 57°, 8.4 dB, 0.61 | 62°, 9.8 dB, 0.66 | 57°, 8.4 dB, 0.61 | 63°, 17 dB, "
     "0.83 | 52°, 10 dB, 0.66 |",
     "| Nominal | 60°, 19 dB, 0.89 | 57°, 8.4 dB, 0.61 | 62°, 9.8 dB, 0.66 | 57°, 8.4 dB, 0.61 | 63°, 17 dB, "
     "0.83 | 51°, 10 dB, 0.66 |"),
    (495,
     "| 66°, 14 dB, 0.78 | 50°, 7.6 dB, 0.55 |",
     "| 66°, 14 dB, 0.78 | 49°, 7.6 dB, 0.55 |"),
    (496,
     "| 60°, 19 dB, 0.87 | 51°, 12 dB, 0.73 |",
     "| 60°, 19 dB, 0.87 | 50°, 12 dB, 0.73 |"),
    (497,
     "| $C_I$ × 1.1, $C_X$ × 0.9 | 69°, 17 dB, 0.85 | 58°, 8.2 dB, 0.60 | 64°, 8.7 dB, 0.63 | 59°, 7.6 dB, "
     "0.58 |",
     "| $C_I$ × 1.1, $C_X$ × 0.9 | 69°, 16 dB, 0.85 | 58°, 8.2 dB, 0.60 | 64°, 8.7 dB, 0.63 | 58°, 7.6 dB, "
     "0.58 |"),
    # 503: the E12 values' actual ratios; the runs at the top values
    (503,
     "- $C_{node}$ should be placed at about 1.3–1.5 times the simulated value: 270–330 pF for H and "
     "560–680 pF for L.",
     "- $C_{node}$ should be placed at about 1.2–1.5 times the simulated value: the E12 values 270–330 pF for "
     "H (1.23–1.50 × 220 pF) and 560–680 pF for L (1.19–1.45 × 470 pF). At 330 pF and 680 pF the "
     "common-mode phase margins are 53° and 50° and the gain margins 11.7 and 13 dB (`comp_search_H100.json`, "
     "`comp_search_L200.json`)."),
    # 513: "halved" refers to the chain's bandwidth of Section 4.3
    (513,
     "| 2.70 / 1.07 / 1.50 nV/√Hz | bandwidth halved; noise above a few MHz |",
     "| 2.70 / 1.07 / 1.50 nV/√Hz | bandwidth halved (Section 4.3); noise above a few MHz |"),
    # 514, 515: no noise runs for these two options
    (514,
     "| 14 MHz | about as adopted, slightly more above 1 MHz |",
     "| 14 MHz | not simulated; by Eq. (9), more above 1 MHz |"),
    (515,
     "| 12 MHz | as adopted |",
     "| 12 MHz | not simulated |"),
    # 517, 518: single roundings (1.4448 -> 1.44; 20.5 % -> 21 %)
    (517,
     "| 27 MHz | 3.15 / 1.45 / 2.14 nV/√Hz |",
     "| 27 MHz | 3.15 / 1.44 / 2.14 nV/√Hz |"),
    (518,
     "| +20 % white noise; CM margin unchanged |",
     "| +21 % white noise; CM margin unchanged |"),
    # 521: the low-voltage option's output swing among its costs
    (521,
     "| 19 MHz | 3.53 / 1.06 / 1.07 nV/√Hz | common-mode range; two more rails; LF noise per the model (below) |",
     "| 19 MHz | 3.53 / 1.06 / 1.07 nV/√Hz | output swing (6.0 V differential at most) and common-mode range; "
     "two more rails; LF noise per the model (below) |"),
    # 525: 1.4448 -> 1.44
    (525,
     "At gain 20 the white floor rises from 1.07 to 1.45 nV/√Hz:",
     "At gain 20 the white floor rises from 1.07 to 1.44 nV/√Hz:"),
    # 529: 15.92 against 15.06 MHz
    (529,
     "But $k_{DM}$ is unchanged, and so is the bandwidth, 16 MHz.",
     "But $k_{DM}$ is unchanged, and so, nearly, is the bandwidth: 16 MHz against 15 MHz."),
    # 535: the 12 V is the THS4021's guaranteed swing (p. 7)
    (535,
     "With $R_F$ = 96 Ω that is 125 mA at 12 V, against the THS4021's guaranteed 80 mA (TI SLOS265F, p. 7).",
     "With $R_F$ = 96 Ω that is 125 mA at 12 V, the THS4021's guaranteed swing into 250 Ω, against its "
     "guaranteed 80 mA (TI SLOS265F, p. 7)."),
    # 542-548: single roundings of fe_gain_options.json at 10 kHz
    (542, "| $R_G$ | 0.41 | 0.89 | 0.39 | 1.22 |", "| $R_G$ | 0.40 | 0.89 | 0.39 | 1.22 |"),
    (544, "| Loop op amps (summing node) | 0.13 | 0.21 | 0.13 | 0.29 |",
     "| Loop op amps (summing node) | 0.13 | 0.20 | 0.13 | 0.29 |"),
    (546, "| $R_F$ | 0.04 | 0.20 | 0.09 | 0.41 |", "| $R_F$ | 0.04 | 0.20 | 0.09 | 0.40 |"),
    (548, "| Total at 10 kHz | 1.07 | 1.45 | 1.07 | 1.90 |", "| Total at 10 kHz | 1.07 | 1.44 | 1.07 | 1.90 |"),
    # 551: kept as an alternative with its limits; product-page noise confirmed by the corrected model
    (551,
     "removes the conflict at its root and is a viable alternative. The ADA4899-1 is unity-gain stable with "
     "600 MHz of bandwidth at a gain of +1, 1 nV/√Hz and 2.6 pA/√Hz, and 310 V/µs (Analog Devices' product "
     "page; its data sheet was not obtained).",
     "removes the conflict at its root, but its low supply limits the output swing and the common-mode range "
     "(below), so it is an alternative only where those suffice. The ADA4899-1 is unity-gain stable with "
     "600 MHz of bandwidth at a gain of +1, 1 nV/√Hz and 2.6 pA/√Hz, and 310 V/µs (Analog Devices' product "
     "page; its data sheet was not obtained). ADI's model, corrected for its 4 kΩ input resistor, has the "
     "same 1.0 nV/√Hz and 2.6 pA/√Hz white (`opamp_noise_check.json`)."),
    # 560: the model's input range
    (560,
     "- **The summing node must sit within the op amp's input range**, so it moves from +9 V to +3 V.",
     "- **The summing node must sit within the op amp's input range** (±3.71 V in ADI's model on ±5 V, "
     "`lv_option_range.json`), so it moves from +9 V to +3 V."),
    # 561: output swing limit and the real common-mode range with its output condition (lv_option_range.json)
    (561,
     "- **The common-mode range shrinks.** It is limited above by the cascodes' headroom and below by the op "
     "amps' output swing (outputs at $V_{CM}$ + 0.35 V ± half the differential output, within about ±3.8 V). "
     "The estimate is about −0.9 V to +0.5 V at full output, against −12 V to +3.7 V; it is estimated from "
     "the operating point, not simulated.",
     "- **The output swing and the common-mode range shrink.** ADI's model swings ±3.34 V into $R_F$ on "
     "±5 V, and the outputs sit at $V_{CM}$ + 0.35 V ± half the differential output, so the front end "
     "delivers at most 2 × (3.34 − 0.35) = 6.0 V of differential output, at $V_{CM}$ = 0, against the 10 V "
     "it must deliver at a total gain of 100 for the chain's 10 V full scale. The common-mode range is "
     "limited above by the cascodes' headroom and below by the op amps' swing: with 1 V of differential "
     "output, the front end's full scale at total gains from 1000 up, it is −3.2 V to +0.09 V (+0.65 V if "
     "the cascodes may run down to saturation), and at 10 V there is none. The adopted front end has "
     "−12.8 V to +3.7 V, and −8.7 V to +3.7 V at 10 V of output. These limits follow from the operating "
     "point and the models' swing (`scripts/lv_option.py`, `range`); the range itself was not simulated."),
    # 562: ADA4899 current noise corrected for the model's input resistor; sources named
    (562,
     "ADI's model has 47 pA/√Hz at 10 Hz (10 nV/√Hz voltage noise), against 20 pA/√Hz for the THS4021, and "
     "gives 3.5 nV/√Hz at 10 Hz against 2.7.",
     "ADI's model, corrected for its 4 kΩ input resistor, has 45 pA/√Hz at 10 Hz (10 nV/√Hz voltage noise), "
     "against 20 pA/√Hz for the corrected THS4021 model (`opamp_noise_check.json`), and the front end gives "
     "3.5 nV/√Hz at 10 Hz against 2.7 (`lv_option.json`)."),
    # 565: product-page values attributed; the model's values archived
    (565,
     "The similar ADA4817-1 (1 GHz, FET input, 4 nV/√Hz, 2.5 fA/√Hz) would remove the current-noise term "
     "altogether. Its ADI model shows a very large voltage 1/f (about 170 nV/√Hz at 10 Hz), unverified.",
     "The similar ADA4817-1 (1 GHz, FET input, 4 nV/√Hz, 2.5 fA/√Hz; Analog Devices' product page) would "
     "remove the current-noise term altogether. Its ADI model has the 4.0 nV/√Hz white but a very large "
     "voltage 1/f, 170 nV/√Hz at 10 Hz (`opamp_noise_check.json`), unverified."),
    # 567: THS4031 and LM7171 from their data sheets; Eq. (10b) evaluated; the slower outer loop estimated
    (567,
     "A unity-gain-stable op amp of 100–200 MHz on ±15 V (THS4031, LM7171): its local bandwidth, by Eq. "
     "(10b) with $\\beta_{CM}$ up to 1, is only 15–30 MHz, so the outer loop would have to slow to a few MHz.",
     "A low-gain-stable op amp on ±15 V (THS4031, LM7171): the THS4031 is unity-gain stable with 120 MHz of "
     "bandwidth (TI SLOS224L, p. 1), so by Eq. (10b) with $\\beta_{CM}$ up to 1 its local differential "
     "bandwidth is at most 120 MHz × 0.15 = 18 MHz. The LM7171 is stable only at gains of +2 or more "
     "(TI SNOS760D, p. 1), so $\\beta_{CM}$ ≤ 0.5, and its A grade's 160 MHz of unity-gain bandwidth (§5.5, "
     "p. 5) gives 160 MHz × 0.15 × 0.5 = 12 MHz. Against the 33 MHz of the adopted design, the outer loop "
     "would have to slow in proportion, from 8.9 MHz to about 3–5 MHz (an estimate, not simulated)."),
    # 573: the oscillation with its bench
    (573,
     "The first front end's oscillation was obvious there: 1 V peak to peak at 290 MHz.",
     "The first front end's oscillation was obvious there: 1.0 V peak to peak at 293 MHz with 50 Ω sources "
     "(Section 4.3)."),
    # 575: the frequencies where the margin is decided (curves_loop.npz)
    (575,
     "The THS4021's phase at 200–400 MHz decides the common-mode margin here, and the model's accuracy there "
     "is unknown.",
     "The THS4021's phase near 200–250 MHz decides the common-mode margin here (the common-mode loops cross "
     "−180° at 204 MHz in L and 251 MHz in H), and the model's accuracy there is unknown."),
    # 579: the probe's capacitance as an assumption
    (579,
     "since a 10:1 passive probe adds 10 pF to the node it touches.",
     "since a 10:1 passive probe adds its input capacitance, assumed here to be about 10 pF, to the node it "
     "touches."),
    # 581: the mode's frequency from the archived runs (stability_corners.json, f_modulus)
    (581,
     "its decay gives the damping of the 200–400 MHz mode directly.",
     "its decay gives the damping of the common-mode loop's weakest mode directly, near 240 MHz in H and "
     "170 MHz in L, where $\\lvert 1+T\\rvert$ is smallest (`stability_corners.json`)."),
]


def main(argv):
    if len(argv) != 2:
        sys.exit(__doc__)
    path = Path(argv[1])
    data = path.read_bytes()
    assert b"\r" not in data, "the note must use \\n newlines"
    text = data.decode("utf-8")
    assert text.count(START) == 1 and text.count(END) == 1, "range headings not found exactly once"
    i0, i1 = text.index(START), text.index(END)
    assert i0 < i1
    head, s, tail = text[:i0], text[i0:i1], text[i1:]
    for line, old, new in REPLACEMENTS:
        n = s.count(old)
        assert n == 1, f"line {line}: found {n} times: {old[:90]!r}"
        s = s.replace(old, new)
    path.write_bytes((head + s + tail).encode("utf-8"))
    print(f"{path}: {len(REPLACEMENTS)} replacements in Sections 4.1-4.3.1")


if __name__ == "__main__":
    main(sys.argv)
