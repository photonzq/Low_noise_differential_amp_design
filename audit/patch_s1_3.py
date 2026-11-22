"""Patch of low_noise_preamp.md, lines 1-252 (summary, Sections 1-3, Tables 1-4, Figures 1-5): the
fixes of Audit A (audit/number_audit_2026-11-21.md).  Exact-string replacements only; each old string
must occur exactly once in the note and lie before Section 4.  New numbers come from
scripts/numbers_s1_3.py (sim/results/numbers_s1_3.json) and the results files it reads, or from the
data-sheet pages cited in the text.

Usage: python patch_s1_3.py <path to low_noise_preamp.md>      (rewrites the file in place)
"""
from __future__ import annotations

import sys
from pathlib import Path

SECTION_4 = "\n## 4. The new design\n"

R: list[tuple[str, str]] = [
    # ---- summary: H (line 11) --------------------------------------------------------------------
    ("bias current in the picoampere range, and an effective input capacitance of about 20 pF set by "
     "the input network rather than by the 26 pF of JFETs, which bootstrapping hides (0.05 pF between "
     "1 kHz and 1 MHz).",
     "a bias current of about 2 pA per input (two JFETs at about 1 pA each at their 3.9 V of $V_{DS}$: "
     "SLPS730B Fig. 6-6; 1 pA typical, 10 pA maximum at 2 V, p. 5), and an effective input capacitance "
     "of 20 pF set by the input network ($C_P + C_Z$ = 10 + 10 pF; 20.1 pF at 1 kHz and 19.9 pF at 1 MHz "
     "in simulation) rather than by the 26 pF of JFETs, which bootstrapping hides (0.06 pF at 1 kHz, "
     "0.05 pF at 100 kHz, 0.11 pF at 1 MHz; `sim/results/zin_numbers.json`)."),
    # ---- summary: L (line 12) --------------------------------------------------------------------
    ("(0.43 at 1 kHz, 0.96 at 10 Hz; gain 1000), for sources below about 300 Ω.",
     "(0.43 at 1 kHz, 0.96 at 10 Hz; gain 1000). It has the lower noise for source resistances up to about "
     "95 Ω at 10 MHz, 0.70 kΩ at 1 MHz and 27–71 kΩ at 1 kHz and 10 Hz, where the two inputs' curves cross "
     "(interpolated in `scripts/numbers_s1_3.py` between the grid points of Section 6.2, Table 10: 30–100 Ω, "
     "300 Ω–1 kΩ and 10–100 kΩ), and H above them. Between about 3 kΩ and 200 kΩ at 1 kHz the two differ by "
     "less than 1 %."),
    # ---- summary: bandwidth, comparisons, CMRR (line 14) ------------------------------------------
    ("The full chain reaches −3 dB at 14.9 MHz (H, gain ≥ 100), 25 MHz (H, gain ≤ 10) and 16.6 MHz (L), "
     "and is within 0.4 dB (H) and 0.8 dB (L) of its midband gain at 10 MHz. Against the SR560 reproduced "
     "in the same simulator (5.7 nV/√Hz at 1 kHz, 3.2 nV/√Hz white, −3 dB at 0.73–0.79 MHz), H is 5 times "
     "quieter at 1 kHz and L 13 times, with about 20 times the simulated bandwidth (15–17 times the "
     "SR560's specified 1 MHz).",
     "The full chain reaches −3 dB at 14.85–14.87 MHz (H, gain ≥ 100), 25.0–25.2 MHz (H with the front "
     "end at ×10: gain ≤ 10 and the high-reserve mode) and 16.6 MHz (L), and at 10 MHz it is 0.35–0.36 dB "
     "(H, gain ≥ 100), 0.40–0.41 dB (H, front end at ×10) and 0.80–0.81 dB (L) below its midband gain "
     "(Table 11, `sim/results/chain_ac.json`). Against the SR560 reproduced in the same simulator "
     "(5.7 nV/√Hz at 1 kHz, 3.2 nV/√Hz white, −3 dB at 0.73–0.79 MHz), H is $5.7/1.11$ = 5.1 times quieter "
     "at 1 kHz and L $5.7/0.43$ = 13.3 times (gain 1000), with $14.85/0.73$ = 20 times (H, gain 100) and "
     "$16.6/0.73$ = 23 times (L, gain 1000) the reproduced SR560's bandwidth at the same gain, and 15–17 "
     "times the 1 MHz of the SR560's manual (printed p. 5; 12–14 times the 1.2 MHz typical of its data "
     "sheet, p. 3; `scripts/numbers_s1_3.py`)."),
    ("(specified at 4 nV/√Hz, about 2.5–3 nV/√Hz in NF's own plot; Section 2.4), H is 2.3–2.8 times quieter "
     "at the same input capacitance class and L 6–7 times. The median "
     "common-mode rejection over 12 Monte Carlo trials with 0.05 % resistors and matched JFETs is 124 dB "
     "at 1 kHz and, with the inputs driven directly, 95 dB at 1 MHz (H; L 98 dB), against 86 dB in the "
     "NF 5307's plot.",
     "(specified at 4 nV/√Hz, about 3 nV/√Hz in NF's own plot; Section 2.4), H is $2.8/1.08$ to $3.1/1.08$ "
     "= 2.6–2.9 times quieter than the plotted white noise and $4/1.11$ = 3.6 times quieter than the "
     "specification at 1 kHz, at the same input capacitance class, and L $2.8/0.42$ to $3.1/0.42$ = 6.7–7.4 "
     "and $4/0.43$ = 9.3 times. The median "
     "common-mode rejection over 12 Monte Carlo trials with 0.1 % resistors (σ 0.05 %), a 0.01 % network "
     "in the difference amplifier (σ 0.005 %) and matched JFETs (`scripts/cmrr_mc.py`) is 124 dB at "
     "1 kHz and, with the inputs driven directly, 95 dB at 1 MHz (H; L 98 dB), against about 86 dB at "
     "1 MHz and a gain of 100 in NF's plot for the 5307 (its web data sheet, "
     "`refs/commercial_preamps/NF_Corporation/NF_5307_datasheet_fig46.jpg`, read by eye)."),
    # ---- summary: finding 1 (line 18) ------------------------------------------------------------
    ("the best JFETs of 2026 are about twice as good per unit of capacitance as the LSK389.** The figure "
     "of merit for a given input-capacitance budget is $e_n\\sqrt{C_{iss}}$ (Eq. (6)). On data-sheet "
     "typical values it is about 8 for the LSK389, 3.2 for the JFE2140, 3.9 for the JFE150 and 2.7 for "
     "the BF862/LSBF862, in nV·√pF/√Hz (Section 3).",
     "the best JFETs of 2026 are two to three times as good per unit of capacitance as the LSK389.** The "
     "figure of merit for a given input-capacitance budget is $e_n\\sqrt{C_{iss}}$ (Eq. (6)). On "
     "data-sheet typical values it is 8.0 for the LSK389, 3.2 for the JFE2140, 3.9 for the JFE150, 2.7 "
     "for the LSBF862 and 2.5 for the discontinued BF862, in nV·√pF/√Hz (Table 3), so the LSK389's is "
     "2.04 (JFE150), 2.47 (JFE2140) and 2.95 (LSBF862) times theirs, and 1.49–2.16 times with the "
     "1.17 nV/√Hz measured in Cordell's application note (Section 3.3; `sim/results/jfet_table3.json`)."),
    # ---- summary: finding 2 (line 19) ------------------------------------------------------------
    ("by large factors** (Section 5.3, Table 7). TI's JFE2140",
     "by large factors** (Section 5.3, Table 7; `sim/results/model_defects.json`). TI's JFE2140"),
    ("the THS3091 model has a tenth of the data sheet's white inverting-input current noise; and the "
     "LM7171 model half its voltage noise.",
     "the THS3091 model has 0.11 times the data sheet's white inverting-input current noise; and the "
     "LM7171 model 0.48 times its white voltage noise."),
    # ---- summary: finding 3 (line 20) ------------------------------------------------------------
    ("The first version of both front ends oscillated near 290 MHz in common mode, inside the loop op "
     "amp's own local loop,",
     "The first version of both front ends oscillated in common mode, at 293 MHz (H) and 277 MHz (L) "
     "with 50 Ω sources (283 MHz for H with its inputs tied to ground through 1 mΩ; "
     "`sim/results/osc_check.json`), inside the loop op amp's own local loop,"),
    ("A capacitor from each summing node to ground cures it, at the cost of half the front end's bandwidth "
     "and a rise of the noise above a few MHz (Section 4.3).",
     "A capacitor from each summing node to ground cures it, at the cost of half the bandwidth (at a total "
     "gain of 100 the chain's falls from 30.1 to 14.85 MHz, $14.85/30.1$ = 0.49) and a rise of the noise "
     "above a few MHz (Section 4.3)."),
    # ---- summary: robustness (line 21) -----------------------------------------------------------
    ("so $C_{node}$ should be fitted 1.3–1.5 times larger.",
     "so $C_{node}$ should be fitted 1.2–1.5 times larger: the E12 values 270–330 pF for H and 560–680 pF "
     "for L (Table 6a, `sim/results/stability_corners.json`; Section 4.3.1)."),
    # ---- summary: low-voltage option (line 23) ---------------------------------------------------
    ("   - **A unity-gain-stable low-voltage op amp** (ADA4899 on ±5 V) is a viable alternative. It gives "
     "20 dB of common-mode gain margin, 19 MHz and no high-frequency noise penalty, but it shrinks the "
     "common-mode range to about ±0.5–1 V unless a folded cascode is added, and its model's 1/f is "
     "unverified.",
     "   - **A unity-gain-stable low-voltage op amp** (ADA4899 on ±5 V) gives 20 dB of common-mode gain "
     "margin, 19 MHz and no high-frequency noise penalty (`sim/results/lv_option.json`), but its rails limit "
     "the front end: it delivers at most 6.0 V of differential output, where a total gain of 100 needs "
     "10 V, and its common-mode range is −3.2 V to +0.09 V at 1 V of output, the full scale at total gains "
     "of 1000 and up, and empty at 10 V (estimated from the operating point, "
     "`sim/results/lv_option_range.json`). Its model's 1/f is unverified."),
    # ---- Section 1.1 (line 39) -------------------------------------------------------------------
    ("where $\\gamma$ is 2/3 for a long channel and $\\beta$",
     "where $\\gamma$ is 2/3 for a long channel (Spieler 1999, p. 3; Leach 1994, p. 1531) and $\\beta$"),
    ("The JFE150 at 5 mA, for example, has $g_m$ = 25.9 mS in TI's model (Section 3.4), so "
     "$\\sqrt{4kT\\cdot\\frac23/g_m}$ = 0.65 nV/√Hz, against 0.8 nV/√Hz in its data sheet (Table 6.5 of "
     "SLPS732B). The white noise falls as $I_D^{-1/4}$, so each doubling of the current buys only 16 %,",
     "The JFE150 at 5 mA and 5 V, for example, has $g_m$ = 25.9 mS in TI's model "
     "(`sim/results/jfet_calibration.json`), so $\\sqrt{4kT\\cdot\\frac23/g_m}$ = 0.65 nV/√Hz at 27 °C "
     "(`scripts/noise_theory.py`; ngspice gives 0.70 nV/√Hz with the card's source resistance, "
     "Section 3.4), against 0.8 nV/√Hz in its data sheet (Table 6.5 of SLPS732B). The white noise falls "
     "as $I_D^{-1/4}$, so each doubling of the current multiplies it by $2^{-1/4}$ = 0.84, a gain of only "
     "16 %,"),
    # ---- Section 1.1 (line 41) -------------------------------------------------------------------
    ("0.57 fA/√Hz at 1 pA, 18 fA/√Hz at 1 nA. It matters only above about 100 kΩ of source impedance at "
     "these voltage-noise levels ($e_n/i_n$ = 1 nV / 1 fA = 1 MΩ). The gate current of a JFET grows "
     "steeply with the drain-gate voltage through impact ionization; the TI parts reach 1–10 nA between "
     "6 and 10 V of drain-source voltage (JFE150 Figs. 6-5 and 6-6 of SLPS732B),",
     "0.57 fA/√Hz at 1 pA, 18 fA/√Hz at 1 nA (`scripts/noise_theory.py`). It matters only where "
     "$i_n\\lvert Z_s\\rvert$ approaches $e_n$, i.e. for source impedances above $e_n/i_n$: with $e_n$ = "
     "1 nV/√Hz, 1.77 MΩ at 1 pA and 55.9 kΩ at 1 nA of gate current. The gate current of a JFET grows "
     "steeply with the drain-gate voltage through impact ionization; the TI parts stay near 1 pA up to "
     "about 5 V of drain-source voltage and reach 0.4–4 nA at 10 V for drain currents of 1–10 mA "
     "(SLPS732B Fig. 6-5 for the JFE150, SLPS730B Fig. 6-6 for the JFE2140, read off the curves),"),
    # ---- Section 1.2 (line 52) -------------------------------------------------------------------
    ("A spread of 85 mV in $V_{TO}$, typical of the JFE150 lot (Section 4.6), shifts each device's "
     "current by tens of percent at 5 mA, so the devices of one side must come from one $V_{GS}$ bin.",
     "A standard deviation of 85 mV in $V_{TO}$, the value the Monte Carlo of Section 6.4 assumes for "
     "unsorted JFE150 (about $0.6\\ \\mathrm{V}/7$ = 86 mV: the data sheet's $V_{GS(off)}$ range of "
     "−1.5 to −0.9 V, SLPS732B p. 5, taken as ±3.5σ, an assumption), shifts each device's current by "
     "$\\Delta I/I = 2\\Delta V_{TO}/(V_{GS}-V_{TO})$ = $2 \\times 85/407$ = 42 % at 5 mA "
     "(`scripts/noise_theory.py`), so the devices of one side must come from one $V_{GS}$ bin "
     "(Section 4.6)."),
    # ---- Section 1.3 (line 70) -------------------------------------------------------------------
    ("(Spieler 1999, pp. 4–6; O'Connor et al. 1997): at constant current density, the optimum input "
     "capacitance equals the source's capacitance, $C_{in} = C_{det}$; at constant total current, "
     "$C_{det}/3$.",
     "(Spieler 1999, pp. 4–6; O'Connor et al. 1997, slide 2): at constant current density, the optimum "
     "input capacitance equals the source's capacitance, $C_{in} = C_{det}$; at constant total current, "
     "$C_{det}/3$ (also Brookhaven's ICFA95 slides, Eq. (3)), a result derived for MOSFETs in strong "
     "inversion, whose $g_m \\propto \\sqrt{I_D C_{gs}}$ scales as the JFET's $g_m = 2\\sqrt{\\beta I_D}$ "
     "does with $\\beta \\propto C$."),
    ("is the optimum for a 55 Ω source, and beyond about 600 Ω of source resistance the optimum is a "
     "single device or fewer.",
     "is the optimum for $R_s = 1/(2\\pi \\cdot 10\\ \\mathrm{MHz} \\cdot 12 \\cdot 24\\ \\mathrm{pF})$ "
     "= 55 Ω, and beyond $1/(2\\pi \\cdot 10\\ \\mathrm{MHz} \\cdot 24\\ \\mathrm{pF})$ = 663 Ω of source "
     "resistance the optimum is a single device or fewer (`scripts/noise_theory.py`)."),
    # ---- Figure 1 caption (line 90) --------------------------------------------------------------
    ("the commercial instruments of Table 2 (diamonds, their specified $e_n$ and input capacitance) and "
     "the two new front ends (stars, simulated noise at the JFETs' own capacitance; the effective input "
     "capacitance with the input network is about 20 pF for H).",
     "the commercial instruments of Table 2 (diamonds: their specified $e_n$ and input capacitance; the "
     "FEMTO DLPVA-101-B at its differential 3.0 nV/√Hz, the Stahl PR-E3 with its two single-ended "
     "channels connected in parallel, 0.69 nV/√Hz at 2 × 16.4 = 32.8 pF, data sheet v3.12 p. 5) and the two new front ends (stars: the front end alone, "
     "simulated at 10 kHz, 1.07 nV/√Hz for H and 0.41 nV/√Hz for L, `sim/results/curves_noise.npz`, "
     "plotted at the JFETs' own 26 and 288 pF; with the input network the effective input capacitance "
     "is 20 pF for H and 250 pF for L, `sim/results/zin_numbers.json`)."),
    # ---- Section 2.1 (line 102) ------------------------------------------------------------------
    ("The SR560 (manual Rev. 2.8, schematics on PDF pp. 46–56) is a DC-coupled preamplifier with a gain "
     "of 1 to 50 000, two first-order filters and a 50 Ω output.",
     "The SR560 (manual Rev. 3.1, schematics on PDF pp. 47–56) is a DC-coupled preamplifier with a gain "
     "of 1 to 50 000 (manual, printed p. 5), two first-order filters (6 dB/octave, data sheet p. 3) and "
     "a 50 Ω output (R438, 49.9 Ω, to J405 on sheet 560_4F, PDF p. 50)."),
    # ---- Table 1 (lines 119, 124, 130) -----------------------------------------------------------
    ("Manual: the table on printed p. 21. The model's white level (100 kHz) is given for the gains of "
     "100 and above.*",
     "Manual: the table on printed p. 21. Model: `sim/results/sr560_chain.json`, with its white level "
     "(100 kHz) for the low-noise mode.*"),
    ("| Low noise, model, 1 kHz | 52 | 36 | 17 | 11.5 | 9.9 | 9.5 | 5.7 |",
     "| Low noise, model, 1 kHz | 52 | 36 | 17 | 11.5 | 9.9 | 9.4 | 5.7 |"),
    ("| High reserve, model, 1 kHz | 35 | 25.5 | 22 | 19.9 | 16.6 | 16.4 | 9.5 | 9.4 |",
     "| High reserve, model, 1 kHz | 35 | 25.5 | 22 | 19.9 | 16.6 | 16.4 | 9.4 | 9.4 |"),
    # ---- Section 2.2 (line 132) ------------------------------------------------------------------
    ("The agreement is within about 30 % at most gains.",
     "The model is within 30 % of the manual in 11 of the 15 columns ($e_\\mathrm{model}/e_\\mathrm{manual} "
     "- 1$, `scripts/numbers_s1_3.py`); the exceptions are the low-noise gain of 5 (−32 %) and gains of "
     "100 and above (+43 to +44 %), and the high-reserve gains of 10 (+40 %) and 1000 (−37 %)."),
    ("The only 2N5564 noise curve available, Vishay's, has an excess noise with a corner of 5–15 kHz "
     "that is not 1/f-shaped,",
     "The only 2N5564 noise curve available, Vishay's (70254 Rev. E, p. 5), has an excess noise with a "
     "corner of 5–15 kHz (where the curve is √2 times its 100 kHz level: about 5 kHz at 10 mA and 15 kHz "
     "at 1 mA, read by eye, `refs/datasheets/jfet/survey_InterFET_NXP_others.md` Section 3.1) that is "
     "not 1/f-shaped,"),
    # ---- Section 2.2 (line 134) ------------------------------------------------------------------
    ("and the CMRR with ideal matching is 102.5 dB at 1 kHz.",
     "and the CMRR with ideal matching is 102.6 dB at 1 kHz (`sim/results/sr560_frontend.json`)."),
    # ---- Section 2.2 (line 136) ------------------------------------------------------------------
    ("The chain's −3 dB bandwidth is 0.73–0.79 MHz at every gain (Figure 3c), against the manual's 1 MHz.",
     "The chain's −3 dB bandwidth is 0.73–0.79 MHz at every gain (Figure 3c), against 1 MHz at 1 Vpp "
     "output in the manual (printed p. 5) and 1.2 MHz typical in the data sheet (p. 3)."),
    ("at 10 Hz, 1 kHz, 10 kHz, 100 kHz and 1 MHz, against the specification of 100 dB up to 1 kHz falling "
     "at 6 dB per octave.",
     "at 10 Hz, 1 kHz, 10 kHz, 100 kHz and 1 MHz (`sim/results/sr560_chain.json`), against a "
     "specification falling at 6 dB per octave above 1 kHz from more than 90 dB in the manual "
     "(printed p. 5) or from 100 dB in the data sheet (p. 3, at a gain of 100 in the low-noise mode)."),
    # ---- Section 2.3 (lines 146, 148) ------------------------------------------------------------
    ("A single 2N5564 pair at 4.5 mA gives 1.28 nV/√Hz white per device, 1.8 nV/√Hz differential. "
     "Paralleled modern JFETs give 0.9 nV/√Hz differential with two JFE2140 halves per side (H) and "
     "0.33 nV/√Hz with twelve JFE150 per side (L).",
     "A single 2N5564 pair at 4.5 mA gives 1.28 nV/√Hz white per device, $\\sqrt2 \\times 1.28$ = "
     "1.8 nV/√Hz differential (the model's targets: 1.28 nV/√Hz white and 3.6 nV/√Hz at 1 kHz, set by "
     "eye between Vishay's 1 mA and 10 mA curves, 70254 Rev. E p. 5; log–log interpolation to 4.5 mA "
     "gives 1.25–1.28 and 3.42–3.44, `sim/results/jfet_model_check.json`). Paralleled modern JFETs give "
     "0.9 nV/√Hz differential ($\\sqrt2 \\times 0.9/\\sqrt2$) with two JFE2140 halves per side (H) and "
     "0.33 nV/√Hz ($\\sqrt2 \\times 0.8/\\sqrt{12}$) with twelve JFE150 per side (L), by Eq. (2) and the "
     "data sheets' 0.9 and 0.8 nV/√Hz at 5 mA (Table 3; `scripts/noise_theory.py`)."),
    ("current-feedback and fast voltage-feedback op amps raise it tenfold.",
     "current-feedback and fast voltage-feedback op amps raise it 15- to 25-fold (14.85–25.2 MHz for "
     "this design's chain at its gains, `sim/results/chain_ac.json`)."),
    # ---- Table 2 (lines 154, 165, 167, 168) ------------------------------------------------------
    ("*Table 2. Commercial voltage preamplifiers (specified or typical values from their documents; "
     "$C_{in}$ per input).*",
     "*Table 2. Commercial voltage preamplifiers (specified or typical values from their documents; "
     "$C_{in}$ per input as connected). This design: Sections 4 and 6, `scripts/numbers_s1_3.py`.*"),
    ("| NF 5307 | 4 | 35 | DC–10 MHz | DC | specification; about 2.5–3 in NF's plot |",
     "| NF 5307 | 4 | < 35 | DC–10 MHz | DC | specification (1 kHz, gain 1000); about 3 (2.8–3.1) in NF's plot "
     "at a gain of 100 |"),
    ("| Stahl PR-E3 | 0.69 | 16.4 | 0.5 kHz–4 MHz | AC | two channels tied |",
     "| Stahl PR-E3 | 0.69 | 32.8 | 0.5 kHz–4 MHz | AC | both channels tied, 2 × 16.4 pF (data sheet "
     "v3.12, p. 5) |"),
    ("| **This design, H** | **1.08** | **≈ 20 (26 pF of JFETs, bootstrapped)** | **DC–14.9 MHz** | "
     "**DC** | **gain ≥ 1000** |",
     "| **This design, H** | **1.08** | **20 (network; 26 pF of JFETs, bootstrapped)** | "
     "**DC–14.85 MHz** | **DC** | **gain ≥ 1000** |"),
    ("| **This design, L** | **0.42** | **≈ 250 (network); 288 pF of JFETs** | **DC–16.6 MHz** | **DC** | "
     "**for sources ≤ 300 Ω** |",
     "| **This design, L** | **0.42** | **250 (network; 288 pF of JFETs)** | **DC–16.6 MHz** | **DC** | "
     "**quieter than H below 95 Ω (10 MHz) to 71 kΩ (10 Hz) of source** |"),
    # ---- Section 2.4 (line 170) ------------------------------------------------------------------
    ("that was remembered from the 1980s, measured at about 3 nV/√Hz, matches the NF 5307",
     "that was remembered from the 1980s, and remembered as measuring about 3 nV/√Hz (a recollection; "
     "no document found), matches the NF 5307"),
    ("specified at 4 nV/√Hz and plotted at about 2.5–3 nV/√Hz at a gain of 100 (manual Fig. 4.7, PDF "
     "p. 37), with an input capacitance below 35 pF.",
     "specified at 4 nV/√Hz typical (1 kHz, gain 1000; NF's specification sheet) and plotted at about "
     "3 nV/√Hz (2.8–3.1, read by eye) at a gain of 100 (manual Fig. 4.7, PDF p. 37), with an input "
     "capacitance below 35 pF (33 pF typical; manual Section 3.2.1, PDF p. 21)."),
    ("In either case its noise, 2.5–4 nV/√Hz, is the figure to beat, and the H input beats it by a "
     "factor of 2.3–3.7 at a similar input capacitance, the L input by 6–10 at a larger one.",
     "In either case its noise, about 3–4 nV/√Hz, is the figure to beat. The H input beats it by a factor "
     "of $2.8/1.08$ to $3.1/1.08$ = 2.6–2.9 against the plotted white noise and $4/1.11$ = 3.6 against the "
     "specification at 1 kHz, at a similar input capacitance; the L input by $2.8/0.42$ to $3.1/0.42$ = "
     "6.7–7.4 and $4/0.43$ = 9.3, at a larger one (gain 1000, `scripts/numbers_s1_3.py`)."),
    # ---- Section 3.1 (lines 181, 184, 185) -------------------------------------------------------
    ("Data sheets quote $C_{iss}$ at different biases ($V_{GS}$ = 0 for Linear Systems, $V_{DS}$ = 5 V "
     "for TI), so cross-vendor comparisons need care.",
     "Data sheets quote $C_{iss}$ at different biases ($V_{GS}$ = 0 for the LSK389 and LSBF862, 100 µA "
     "and 500 µA for the LSK170 and LSK489, $V_{DS}$ = 5 V for the JFE150 and JFE2140 and 2 V for the "
     "JFE2325; their p. 2 or p. 5, and item C13 of `refs/datasheets/jfet/survey_TI_LIS_Toshiba_onsemi.md`), "
     "so cross-vendor comparisons need care."),
    ("above a part-specific voltage (about 6 V for the TI parts). A cascode that holds $V_{DS}$ at 3–5 V "
     "keeps it in the picoampere range.",
     "above a part-specific voltage (about 6 V for the TI parts: SLPS732B Fig. 6-5, SLPS730B Fig. 6-6). "
     "A cascode that holds $V_{DS}$ at 3–5 V keeps it in the picoampere range (about 1 pA in the same "
     "figures)."),
    ("(JFE2140: 4 mV maximum, 10 µV/°C), which sets the differential offset and its drift.",
     "(JFE2140: 4 mV maximum and 10 µV/°C maximum drift, 1 mV and 1.7 µV/°C typical; SLPS730B p. 5), "
     "which sets the differential offset and its drift."),
    # ---- Table 3 (lines 192, 197, 201, 203, 205, 207, 209) ---------------------------------------
    ("*Table 3. Low-noise JFETs: typical data-sheet values. $e_n$ at 1 kHz (or the white level where "
     "stated) at $I_D$; $e_n$ at 10 Hz; $C_{iss}$ at the data sheet's conditions; figure of merit "
     "$e_n\\sqrt{C_{iss}}$ in nV·√pF/√Hz.*",
     "*Table 3. Low-noise JFETs: typical data-sheet values (maxima where marked max). $e_n$ at 1 kHz "
     "(or the white level where stated) at $I_D$; $e_n$ at 10 Hz (at $I_D$ unless stated); $C_{iss}$ at "
     "the data sheet's conditions; figure of merit $e_n\\sqrt{C_{iss}}$ in nV·√pF/√Hz "
     "(`scripts/jfet_data.py`, `sim/results/jfet_table3.json`).*"),
    ("| BF862 | NXP | discontinued | 0.8 | 15 | – | 10 | 2.5 | single; at 100 kHz near $I_{DSS}$ |",
     "| BF862 | NXP | discontinued | 0.8 | $I_{DSS}$, 10–25 | – | 10 | 2.5 | single; at 100 kHz and "
     "$V_{GS}$ = 0 (NXP p. 4) |"),
    ("| JFE2325 | TI | active (new) | 4.3 | 0.385 | – | 0.85 | 4.0 | dual, self-biased; $e_n$ at 10 kHz |",
     "| JFE2325 | TI | active (new) | 4.3 | 0.385 ($I_{DSS}$) | – | 0.85 | 4.0 | dual, self-biased; $e_n$ "
     "at 10 kHz, gate grounded |"),
    ("| IF170 | InterFET | active | 1.0 | 2 | 1.72 | 20 | 4.5 | 2SK170 type |",
     "| IF170 | InterFET | active | 1.0 | 2 | 1.70 (5 mA) | 20 max | 4.5 | 2SK170 type |"),
    ("| IF9030 | InterFET | active | 0.7 | 5 | – | 60 | 5.4 | |",
     "| IF9030 | InterFET | active | 0.7 | 5 | – | 60 max | 5.4 | |"),
    ("| IF4500 | InterFET | active | 0.85 | 5 | 1.1 | 55 | 6.3 | |",
     "| IF4500 | InterFET | active | 0.85 | 5 | 1.1 | 55 | 6.3 | $C_{iss}$ off its curve at $V_{GS}$ = 0, "
     "10 V (table: 35 max) |"),
    ("| LSK389 | Linear Systems | active | 1.6 | 2 | 3.2 | 25 | 8.0 | dual; 1.17 measured in its app note |",
     "| LSK389 | Linear Systems | active | 1.6 | 2 | 3.2 | 25 | 8.0 | dual; 1.17 measured in its app note "
     "(A-weighted, with the test amplifier's second stage; Cordell Rev. A4, Table 1, p. 5) |"),
    # ---- Section 3.3 (lines 220, 222, 225, 227, 229) ---------------------------------------------
    ("On data-sheet values the LSK389 has a figure of merit of about 8 (5.9 with the 1.17 nV/√Hz "
     "measured in Cordell's application note). Parts that are better by a factor of about two per unit "
     "of capacitance, all in production:",
     "On data-sheet values the LSK389 has a figure of merit of 8.0 ($1.6\\sqrt{25}$; 5.85 with the "
     "1.17 nV/√Hz measured in Cordell's application note, Table 1, p. 5, A-weighted with the test "
     "amplifier's second stage). Parts that are better by a factor of 1.79–2.95 per unit of capacitance "
     "on data-sheet values (1.31–2.16 against the measured 1.17; `sim/results/jfet_table3.json`), all in "
     "production:"),
    ("Two halves per side give 0.64 nV/√Hz per side at 26 pF, against about 1.17–1.6 nV/√Hz for one "
     "LSK389 half at 25 pF. Its matching (≤ 4 mV, ≤ 10 µV/°C) suits a DC-coupled differential input. Its "
     "gate current rises above about 6 V of $V_{DS}$, so it needs a cascode. It is the H front end's "
     "device, and the same part Spinelli and Haberman (2024) used in their 0.9 nV/√Hz, DC–100 kHz "
     "current-feedback amplifier.",
     "Two halves per side give $0.9/\\sqrt2$ = 0.64 nV/√Hz per side at 26 pF (Eq. (2)), against about "
     "1.17–1.6 nV/√Hz for one LSK389 half at 25 pF. Its matching (≤ 4 mV, ≤ 10 µV/°C; SLPS730B p. 5) "
     "suits a DC-coupled differential input. Its gate current rises above about 6 V of $V_{DS}$ "
     "(SLPS730B Fig. 6-6), so it needs a cascode. It is the H front end's device, and the same part "
     "Spinelli and Haberman (2024) used, two per side at 7 mA, in their current-feedback amplifier of "
     "0.9 nV/√Hz at 1 kHz (their Table 1, p. 2), designed for DC–100 kHz (their Section III, p. 4)."),
    ("(2SK170 types, FOM 4.0–4.5) and **LSK489** (4 pF, FOM 3.6, low $C_{rss}$ of 1.5–2 pF).",
     "(2SK170 types, FOM 4.0–4.5, the IF170's with its maximum $C_{iss}$) and **LSK489** (4 pF, FOM 3.6, "
     "low $C_{rss}$: 2 pF typical in its data sheet, p. 2, and 1.5 pF in Cordell's application note, "
     "p. 2)."),
    ("Twelve JFE150 reach the same 0.33 nV/√Hz differential at 288 pF per input, with lower 1/f per unit "
     "of capacitance than one IF3601 would need:",
     "Twelve JFE150 per side give $0.8/\\sqrt{12}$ = 0.23 nV/√Hz per side and 0.33 nV/√Hz differential "
     "at 288 pF per input, against 0.34 and $\\sqrt2 \\times 0.34$ = 0.48 nV/√Hz at 650 pF for one IF3601 "
     "per side, and with lower 1/f per unit of capacitance: $1.8\\sqrt{24}$ = 8.8 against "
     "$0.60\\sqrt{650}$ = 15.3 nV·√pF/√Hz at 10 Hz (`scripts/numbers_s1_3.py`):"),
    ("(dual, 0.85 pF, 4.3 nV/√Hz at 0.385 mA, self-biased gate), is aimed at high-impedance sensors and "
     "has a figure of merit of 4.0, as good as the LSK170.",
     "(dual, 0.85 pF, 4.3 nV/√Hz at 10 kHz with the gate grounded, i.e. at $I_{DSS}$, 0.385 mA typical, "
     "SLPS816A p. 5; self-biased gate), is aimed at high-impedance sensors and has a figure of merit of "
     "4.0, as good as the LSK170's."),
    # ---- Section 3.4 (line 233) ------------------------------------------------------------------
    ("ngspice's JFET model gives the channel the thermal noise $8kTg_m/3$, the thermal noise of RS and RD, "
     "and KF flicker noise. Each part was calibrated to its data sheet (`scripts/models.py`): a resistor "
     "RX in series with the gate is chosen so that the white noise at the data sheet's operating point "
     "equals the typical value, KF is chosen so that the noise at 10 Hz (or the data sheet's "
     "low-frequency point) equals the typical value, and CGS and CGD are solved from the data sheet's "
     "$C_{iss}$ and $C_{rss}$ at its bias (Table 4). Figure 5 checks the two TI parts against their data "
     "sheets' noise curves over two decades of current.",
     "ngspice's JFET model gives the channel the thermal noise $8kTg_m/3$, the thermal noise of RS and RD, "
     "and KF flicker noise (its \"standard thermal and flicker noise model\", ngspice-46 User's Manual, "
     "Section 7.4.4, p. 154; the JFE150 card alone gives 0.7045 nV/√Hz at 5 mA in ngspice, and "
     "$\\sqrt{4kT(2/(3g_m) + R_S)}$ = 0.7042 nV/√Hz with $g_m$ = 25.93 mS and RS = 4.2 Ω, "
     "`scripts/numbers_s1_3.py`). Each part was calibrated to its data sheet (`scripts/models.py`): a "
     "resistor RX in series with the gate is chosen so that the white noise at the data sheet's operating "
     "point equals the typical value, $R_X = (e_w^2 - e_m^2)/4kT$ with $e_m$ the card's own white noise; "
     "KF is chosen so that the noise at 10 Hz (or the data sheet's low-frequency point) equals the "
     "typical value, $K_F = (e_{lf}^2 - e_w^2)\\,g_m^2 f_{lf}/I_D$; and CGS and CGD are solved from the "
     "data sheet's $C_{iss}$ and $C_{rss}$ at its bias (Table 4). The JFE2325's table gives no "
     "low-frequency value, so its KF is fitted, as the JFE2140's, at 10 Hz, to the gate-grounded curve "
     "of SLPS816A Fig. 5-24 (32 nV/√Hz, read by eye); the card's own KF has 3.2 times that curve's 1/f "
     "power. Figure 5 checks the JFE150 and JFE2140 against their data sheets' noise curves over two "
     "decades of current; `sim/results/jfet_model_check.json` checks every calibrated model at its "
     "calibration point, and the JFE2325 against Fig. 5-24 from 1 Hz to 100 kHz."),
    # ---- Table 4 (lines 241-243) -----------------------------------------------------------------
    ("| LSBF862 | Linear Systems Rev 2 | 0 | 8.75e-17 → 1.74e-18 | 8 / 3.5 → 10.5 / 14.3 | 0.8 / 1.4 nV, "
     "2 mA, 8 V; $C_{iss}$ 11.5, $C_{rss}$ 3.5 pF |",
     "| LSBF862 | Linear Systems Rev 2 | 0 (clipped) | 8.75e-17 → 1.74e-18 | 8 / 3.5 → 10.5 / 14.3 | "
     "0.8 / 1.4 nV, 2 mA, 8 V, achieved 0.90 / 1.46 (the card alone gives 0.90, and KF was fitted for "
     "0.8); $C_{iss}$ 11.5, $C_{rss}$ 3.5 pF |"),
    ("| 2N5564 | LTspice standard.jft | 46.8 | 6.786e-11 → 4.30e-16 | 9.76 / 8.67 → 7.7 / 10.0 | 1.28 nV "
     "white, 3.6 nV at 1 kHz, 4.5 mA (Vishay curve) |",
     "| 2N5564 | LTspice standard.jft | 46.8 | 6.786e-11 → 4.30e-16 | 9.76 / 8.67 → 7.7 / 10.0 | 1.28 nV "
     "white, 3.6 nV at 1 kHz, at the SR560's 4.5 mA and 5.5 V (set by eye between Vishay's 1 and 10 mA "
     "curves, 70254 Rev. E p. 5); $C_{iss}$ 10, $C_{rss}$ 2.5 pF at 15 V (p. 2) |"),
    ("| JFE2325 | TI SLVMF24 | 67.0 | 40e-18 (kept) | 0.65 / 0.30 → 0.75 / 0.20 | 4.3 nV at 10 kHz; "
     "$C_{iss}$ 0.85, $C_{rss}$ 0.1 pF |",
     "| JFE2325 | TI SLVMF24 | 143.1 | 40e-18 → 12.6e-18 | 0.65 / 0.30 → 0.75 / 0.20 | 4.3 nV at 10 kHz "
     "(p. 5) and 32 nV at 10 Hz (Fig. 5-24), gate grounded ($V_{GS}$ = 0: the card's $I_{DSS}$, "
     "0.378 mA), 2.5 V; $C_{iss}$ 0.85, $C_{rss}$ 0.1 pF at 2 V |"),
    # ---- Figure 5 caption (line 247) -------------------------------------------------------------
    ("*Figure 5. The calibrated TI models against their data sheets:",
     "*Figure 5. The calibrated JFE150 and JFE2140 models against their data sheets "
     "(`sim/results/jfet_model_check.json`):"),
    # ---- Section 3.4 (line 249) ------------------------------------------------------------------
    ("keeps the junction grading exponent at 0.5 whatever M the card gives (ngspice accepts M without "
     "using it), so",
     "keeps the junction grading exponent at 0.5 whatever M the card gives (its gate capacitances vary "
     "as the −1/2 power of the junction voltage, ngspice-46 User's Manual, Section 7.4.4, p. 153; its "
     "parameter table, p. 154, has no grading coefficient, and `scripts/models.py` removes the vendors' "
     "M), so"),
]


def main() -> None:
    path = Path(sys.argv[1])
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s
    for old, new in R:
        assert s.count(old) == 1, f"not exactly once ({s.count(old)}): {old[:70]!r}"
        assert s.index(old) < s.index(SECTION_4), f"beyond line 252: {old[:70]!r}"
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")
    print(f"{len(R)} replacements applied to {path}")


if __name__ == "__main__":
    main()
