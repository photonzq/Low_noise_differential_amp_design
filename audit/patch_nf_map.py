"""Patch of low_noise_preamp.md after patch_new_runs.py (23 November 2026): the noise-figure maps of Figure 14,
against the SR560 data sheet's own noise-figure plot (data sheet p. 3).

- Section 6.2: Figure 14 and its text (scripts/sr560_nf_datasheet.py, scripts/nf_map.py; numbers from
  numbers_s6_7.py, group "s6.2 Figure 14"); Eq. (5a), Eq. (5) with the generators' correlation; the SR560
  reproduction as drawn (NPD5564) and with the LSK389B, why the first has far more 1/f noise than the data sheet's
  plot (its JFET model's single 1/f term fitted at 1 kHz to Vishay's 2N5564 curve, which is not 1/f-shaped), and
  the tail servo's noise that both show with an unbalanced high-resistance source.
- Appendix A: the LSK389B model's noise decks with abstol = 1e-12 A (the transient-op fallback crawled).
- Table 10's caption: the source's noise at the simulator's 300.15 K (Figure 14: 290 K).
- Figures 14, 15 and 16 become 15, 16 and 17.
- Section 8 and the references: the two new scripts; the data sheet's plot.
Every edit is an exact-string replacement whose old text occurs once.  A second run is refused.
Usage: python patch_nf_map.py <path to low_noise_preamp.md>
"""
from __future__ import annotations

import sys
from pathlib import Path

NEW_TEXT = (
    "Figure 14 maps the noise figure over source resistance and frequency at once, in the format of the SR560 "
    "data sheet's own plot (\"SR560 Noise Figure\", data sheet p. 3), which panel (a) redraws: the same axes, "
    "extended to 10 MHz, the same contour levels from 0.05 to 25 dB, and the same temperature of the source, "
    "$T_0$ = 290 K. The data sheet's contours are read from the vector paths of its PDF, not traced by eye: the "
    "axes are calibrated on the tick marks (to within 0.02 pt), each contour takes the level printed on it, and "
    "the five unlabelled ones in the upper right corner take 6 to 25 dB in order towards the corner "
    "(`scripts/sr560_nf_datasheet.py`, `sim/results/sr560_nf_datasheet.json`). The maps of H, L and two SR560 "
    "reproductions come from 41 noise runs each at a gain of 1000, with a noiseless source resistor from 1 Ω to "
    "100 MΩ, five per decade, in series with input A and with input B grounded, as in Table 10 "
    "(`scripts/nf_map.py`, `sim/results/nf_map.npz` and `nf_map.json`). With $v_a$ the amplifier's "
    "input-referred noise and $e_n$, $i_n$ its equivalent input generators, the input network included, Eq. (5) "
    "with the generators' correlation reads\n"
    "\n"
    "$$\n"
    "F = 1 + \\frac{v_a^2}{4kT_0R_S}, \\qquad v_a^2 = |e_n|^2 + 2R_S\\,\\mathrm{Re}\\,(e_n i_n^*) + R_S^2\\,|i_n|^2 .\n"
    "\\tag{5a}\n"
    "$$\n"
    "\n"
    "Fitted at each frequency from 1 Hz to 10 MHz, the second expression reproduces every run within "
    "$2\\times10^{-5}$ dB (0.003 dB for the reproduction with the LSK389B), and the "
    "maps are drawn from these fits; with the source's noise taken at the simulator's 300.15 K instead of 290 K, "
    "the runs reproduce Table 10 within $2\\times10^{-6}$ dB. The data sheet's contours obey Eq. (5a) as well, "
    "within 0.01 decade of $R_S$ (0.03 dB), so the fit gives the data sheet's noise figure between its contours, "
    "which Figure 14e, f, h and i subtract. The fit also shows what the plot corresponds to: $e_n$ = 3.60 nV/√Hz "
    "white (3.64 at 1 kHz, 7.6 at 10 Hz and 43 at 1 Hz), and $i_n$ = 12.7 fA/√Hz at low frequencies, the "
    "thermal noise of 99 MΩ at 290 K, i.e. of the 100 MΩ input resistors, rising at high frequencies as "
    "$e_n\\omega C$, with $C$ = 38 pF from 100 kHz to 1 MHz (25 pF specified; manual, printed p. 5). That $e_n$ is below the manual's "
    "\"about 4 nV/√Hz\" and its typical curve, about 5 nV/√Hz at 1 kHz and 11 at 10 Hz (printed p. 20; "
    "Section 2.2): Figure 14 compares H and L with the SR560's most favourable published figure.\n"
    "\n"
    "Side by side (Figure 14a–c), the three maps have the same shape, set by the same three things: $e_n$ with "
    "low source resistances, the resistors from the inputs to ground with high ones, and above about 100 kHz the "
    "input's capacitance or network. H's low-resistance contours lie about a decade below the data sheet's, by "
    "the square of the ratio of their $e_n$ at 1 kHz, a factor of 10.7: at 1 kHz its noise figure is 3 dB with "
    "78 Ω and 1 dB with 300 Ω, against 830 Ω and 3.2 kΩ (at 10 Hz, 500 Ω and 1.9 kΩ against 3.6 and 14 kΩ). Its "
    "100 MΩ bias resistors give it the SR560's high-resistance boundary: at 1 kHz, 1 dB with 25.0 against "
    "25.6 MΩ, and 3 dB with 96 against 98 MΩ. At 1 MHz, where the data sheet's SR560 reaches 1 dB with no "
    "source resistance (its minimum there is 1.42 dB, at 4.2 kΩ, and it is below 3 dB only from 850 Ω to "
    "21 kΩ), H is below 1 dB from 290 Ω to 21.8 kΩ, with a minimum of 0.25 dB at 2.5 kΩ. Over the data sheet's "
    "whole plane (1 Hz to 1 MHz and 1 Ω to 100 MΩ, in equal steps of $\\log f$ and $\\log R_S$), H's noise figure "
    "is lower by more than 0.1 dB on 72 % of it and within 0.1 dB on the rest (Figure 14e); it is the higher only "
    "above 1.8 MΩ at 1 kHz (3.5 MΩ at 10 Hz), by at most 0.07 dB, because its bias resistors are at the "
    "simulator's 300.15 K and the data sheet's input resistors at 290 K.\n"
    "\n"
    "L's low-resistance contours lie lower again, by the square of the ratio of H's and L's $e_n$, a factor of "
    "6.8: at 1 kHz 3 dB with 11 Ω and 1 dB "
    "with 44 Ω, and at 1 MHz L is below 1 dB from 44 Ω to 1.75 kΩ (minimum 0.34 dB at 280 Ω). Its 10 MΩ bias "
    "resistors bring the high-resistance boundary down by a decade (1 dB with 2.5 MΩ and 3 dB with 9.6 MΩ, from "
    "10 Hz to 1 kHz), and its noise current at 1 MHz is 1.51 pA/√Hz, against 0.43 pA/√Hz for H, mostly from its "
    "input network (next paragraph). L's noise figure is therefore below the data sheet's only up to 94 kΩ at "
    "1 kHz (190 kΩ at 10 Hz, 28 kΩ at 100 kHz, 2.9 kΩ at 1 MHz), and above it with larger sources, by up to "
    "7.5 dB at 100 MΩ (Figure 14f; below on 57 % of the plane, above on 35 %): L is for low source resistances "
    "(Section 4.4), and H for the others.\n"
    "\n"
    "Above about 100 kHz, the high-resistance side of both inputs' low-noise region is bounded mostly by the "
    "damping networks' resistors $R_Z$ (Section 4.4), whose thermal noise $C_Z$ shorts only at low frequencies. "
    "Their noise current, $\\sqrt{4kT\\,\\mathrm{Re}\\,Y}$ with the $\\mathrm{Re}\\,Y$ of Section 4.4, is 0.38 of "
    "H's 0.43 pA/√Hz at 1 MHz and 1.22 of L's 1.51 pA/√Hz; with a 100 kΩ source, ngspice attributes 76 % (H) and "
    "65 % (L) of the output noise at 1 MHz to input A's $R_Z$, and with 1 kΩ, 10 % and 59 %. The damping thus "
    "costs noise figure at megahertz frequencies for sources above the optimum source resistance there, 2.5 kΩ "
    "for H and 280 Ω for L.\n"
    "\n"
    "The SR560 reproduction as drawn, simulated in the same way (Figure 14d, and h for its difference from the "
    "data sheet), has the data sheet's high-resistance boundary, from the same 100 MΩ input resistors (1 dB with "
    "24.8 MΩ at 1 kHz), but far more noise at low frequencies: with the NPD5564 of the manual, 47.7 nV/√Hz at "
    "10 Hz and 5.71 at 1 kHz, against the data sheet's 7.56 and 3.64. Its 3 dB contour lies at 2.0 kΩ at 1 kHz "
    "and 140 kΩ at 10 Hz, against 830 Ω and 3.6 kΩ, and its noise figure is up to 16.0 dB above the data sheet's "
    "(10 Hz, 1 Ω). The excess is a 1/f noise with a corner of 2.2 kHz, against 23–34 Hz in the data sheet's plot, "
    "and it comes from the input JFETs: their flicker generators give 99.5 % of the output noise at 10 Hz, "
    "95.8 % at 100 Hz and 69.6 % at 1 kHz. Their model has the JFET model's single 1/f term, "
    "$K_F I_D^{A_F}/f$, fitted at one point of Vishay's 2N5564 curve, 3.6 nV/√Hz per device at 1 kHz and "
    "4.5 mA above a white 1.28 nV/√Hz (Section 3.4), which makes a corner of 6.9 kHz. Vishay's measured noise "
    "is not 1/f-shaped: at 10 mA its excess power above the 100 kHz level grows only 1.6 times from 100 Hz down "
    "to 10 Hz, where a 1/f line grows 10 times. The line through 1 kHz therefore gives 33.7 nV/√Hz per device at "
    "10 Hz where Vishay's curve, interpolated to 4.5 mA, shows 10.5, 3.20 times as much (1.35 times at 100 Hz), "
    "and $\\sqrt2\\cdot33.7$ = 47.6 nV/√Hz for the pair, nearly all of the reproduction's 47.7. With Vishay's "
    "curve itself the pair would give about 15 nV/√Hz at 10 Hz, still above the manual's typical 11 and the "
    "plot's 7.6: the SR560's NPD5564 is not Vishay's part, no noise curve of it is published, and it evidently "
    "has less excess noise (Section 2.2).\n"
    "\n"
    "With the LSK389B that the forum user found in a newer unit (Figure 14g and i; the corrected model of "
    "Section 2.2), the reproduction's 1/f corner falls to 16 Hz, below the plot's, and its low-resistance "
    "contours lie near the data sheet's: 5.17 nV/√Hz at 10 Hz, 3.23 at 1 kHz and 3.21 white, against 7.56, 3.64 "
    "and 3.60, so that 3 dB is reached with 660 Ω at 1 kHz (830 Ω) and 1.7 kΩ at 10 Hz (3.6 kΩ). The data "
    "sheet's 3.64 nV/√Hz at 1 kHz lies between the two reproductions' 5.71 and 3.23, and between the 4.0 and "
    "3.5 nV/√Hz that the forum user measured on units with these two JFETs (Section 2.2). Both reproductions "
    "also depart from the data sheet with high source resistances at mid frequencies (the red regions at the "
    "upper right of Figure 14h and i), where the LSK389B model's noise figure is up to 6.9 dB above it (63 kHz, "
    "100 MΩ) and its noise current at 100 kHz is 0.187 pA/√Hz (0.100 as drawn), against the data sheet's 0.087. "
    "That noise is the pair's tail servo's: with 1 MΩ in input A, U103 (an LF411) with R125, R127, R129 and "
    "R130 gives 97 % (NPD5564) and 98 % (LSK389B) of the output noise at 100 kHz. It sits on the JFETs' common "
    "source node, where a balanced source rejects it as common mode: with 1 MΩ also from input B to ground, its "
    "share falls to 0.03 and 0.04 %. With input B grounded, gate A follows its source through the gate–source "
    "capacitance and gate B cannot, so the servo's noise appears across the pair, the more with the LSK389B's "
    "larger capacitances; the data sheet's plot, whose current noise is that of a single 38 pF, has no such term. "
    "At 1 MHz both reproductions are below the data sheet again (noise currents 0.37 and 0.74 pA/√Hz, against "
    "0.86), and beyond its plot and the SR560's bandwidth their minimum noise figure reaches 29 and 43 dB at "
    "10 MHz, where H's is 2.42 dB (at 440 Ω) and L's 3.43 dB (at 37 Ω).\n"
    "\n"
    "![Figure 14](figures/fig_nf_map.png)\n"
    "\n"
    "*Figure 14. Noise figure against source resistance and frequency at a gain of 1000, in the format of the "
    "SR560 data sheet's plot (p. 3): the same axes, extended to 10 MHz, and the same contour levels (dB), "
    "labelled where they cross 2 kHz and 50 Hz; the source at 290 K, in series with input A, input B grounded. "
    "(a) The data sheet's contours, read from its PDF. (b) H, (c) L, and the SR560 reproduction of Section 2.2 "
    "(d) as drawn, with the NPD5564, and (g) corrected, with the LSK389B, simulated (dotted: the data sheet's "
    "1 MHz limit). (e, f, h, i) The noise figure of (b), (c), (d) and (g) minus the data sheet's, on its range: "
    "blue where lower than the data sheet's. (`scripts/sr560_nf_datasheet.py`, `scripts/nf_map.py`, "
    "`sim/results/nf_map.json`; numbers rounded by `scripts/numbers_s6_7.py`.)*"
)

EDITS: list[tuple] = [
    # ---- Section 6.2 -----------------------------------------------------------------------------------------
    ("rounded by `scripts/numbers_s6_7.py`; source resistance in series with input A, input B grounded).*",
     "rounded by `scripts/numbers_s6_7.py`; source resistance in series with input A, input B grounded; the "
     "source's noise at the simulator's 300.15 K, where Figure 14 takes the standard 290 K).*"),
    ("(b) Total input noise against source resistance, with the source's own thermal noise.*\n\n"
     "### 6.3 Frequency response and stability",
     "(b) Total input noise against source resistance, with the source's own thermal noise.*\n\n" + NEW_TEXT +
     "\n\n### 6.3 Frequency response and stability"),
    # ---- Figures 14-16 become 15-17 ----------------------------------------------------------------------------
    ("the gain-bandwidth trade of a single op amp does not apply (Figure 14).",
     "the gain-bandwidth trade of a single op amp does not apply (Figure 15)."),
    ("![Figure 14](figures/fig_frequency_response.png)", "![Figure 15](figures/fig_frequency_response.png)"),
    ("*Figure 14. Frequency response of the chain", "*Figure 15. Frequency response of the chain"),
    ("![Figure 15](figures/fig_cmrr.png)", "![Figure 16](figures/fig_cmrr.png)"),
    ("*Figure 15. CMRR against frequency", "*Figure 16. CMRR against frequency"),
    ("is within 0.1 V after 0.16 µs (Figure 16d).", "is within 0.1 V after 0.16 µs (Figure 17d)."),
    ("![Figure 16](figures/fig_large_signal.png)", "![Figure 17](figures/fig_large_signal.png)"),
    ("*Figure 16. (a) THD against frequency", "*Figure 17. (a) THD against frequency"),
    # ---- Section 8 ---------------------------------------------------------------------------------------------
    ("the curves behind Figures 9, 10, 12 and 14 (`curves_*.npz`)", "the curves behind Figures 9, 10, 12 and 15 (`curves_*.npz`)"),
    ("| `scripts/noise_vs_source.py` | Table 10 and Figure 13 (`noise_vs_source.json`) |\n",
     "| `scripts/noise_vs_source.py` | Table 10 and Figure 13 (`noise_vs_source.json`) |\n"
     "| `scripts/nf_map.py`, `scripts/sr560_nf_datasheet.py` | Figure 14 and its numbers (Section 6.2): the "
     "noise-figure maps of H, L and the SR560 reproduction as drawn and with the LSK389B, 41 source resistances "
     "each, with each frequency's two-port fit, the comparison with the data sheet, the SR560 models' 1/f noise "
     "and the noise of their tail servo (`nf_map.npz`, `nf_map.json`); the SR560 data sheet's "
     "noise-figure contours read from the vector paths of its PDF, with their two-port fit "
     "(`sr560_nf_datasheet.json`) |\n"),
    ("| `scripts/make_figures.py`, `scripts/plot_style.py` | Figures 1, 3–5, 9, 10 and 12–16 |",
     "| `scripts/make_figures.py`, `scripts/plot_style.py` | Figures 1, 3–5, 9, 10 and 12–17 |"),
    ("| `figures/` | Figures 1–16 as PNG and PDF |", "| `figures/` | Figures 1–17 as PNG and PDF |"),
    # ---- Appendix A ----------------------------------------------------------------------------------------------
    ("Fixed-step gmin stepping (`gminsteps`) failed fast but also made good trials fail; no deck of that attempt "
     "is archived.",
     "Fixed-step gmin stepping (`gminsteps`) failed fast but also made good trials fail; no deck of that attempt "
     "is archived. A noise deck of Figure 14's SR560 model with the LSK389B (a source resistance of 1 kΩ) hung in "
     "the transient-op fallback instead: after Newton, both kinds of gmin stepping and source stepping had failed, "
     "the transient op crawled (about 35 % of its transient after a minute, the run still in it after ten), so "
     "that no next starting point could be tried. With abstol = 1e-12 A instead of 1e-15 A the same deck "
     "converges at once, and all of that model's decks run with it; its 1 Ω run reproduces the archived run at "
     "1e-15 A to the seven digits that ngspice writes (`scripts/nf_map.py`)."),
    # ---- References --------------------------------------------------------------------------------------------
    ("board layout on PDF p. 46 and schematics on PDF pp. 47–56), and the SR560 data sheet.",
     "board layout on PDF p. 46 and schematics on PDF pp. 47–56), and the SR560 data sheet, 3 pp. (its "
     "noise-figure plot, p. 3, is read in `scripts/sr560_nf_datasheet.py`)."),
]


def main() -> None:
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    assert "\r" not in text
    if "fig_nf_map.png" in text:
        sys.exit("already patched: refusing a second run")
    for e in EDITS:
        old, new = e[0], e[1]
        n = e[2] if len(e) > 2 else 1
        c = text.count(old)
        assert c == n, (c, n, old[:90])
        text = text.replace(old, new)
    print(f"{len(EDITS)} edits applied to {path.name}")
    path.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
