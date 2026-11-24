"""Patch of low_noise_preamp.md after patch_nf_map_capacitance.py (24 November 2026): the Signal Recovery 5113's
noise-figure plot (manual 222144-A-MNL-F, Fig. A-1) in the note, read from its pixels by scripts/nf5113_manual.py
(sim/results/nf5113_manual.json; numbers from numbers_s6_7.py, group "s6.2 Figure 14j-l"):

- Section 2.4: the 5113 in Table 2 (scripts/jfet_data.py COMMERCIAL, also Figure 1a) and a paragraph on it.
- Section 6.2: three paragraphs before Figure 14 (how the plot is read; what it says, against its own
  specification; H, L and the SR560 data sheet's plot against it), and Figure 14's caption for its fourth row (j-l);
  the figure, now 4 x 3, shown at 90 % of the width (class fitpage in the note's style block) to keep its caption on
  its page.  ("its appendix A" in the references, lower case: the build links "Appendix A" to the note's own.)
- Section 8: the script and its results in Figure 14's row.
- References: the 5113's documents.
Every edit is an exact-string replacement whose old text occurs once.  A second run is refused.
Usage: python patch_nf_map_5113.py <path to low_noise_preamp.md>
"""
from __future__ import annotations

import sys
from pathlib import Path

EDITS: list[tuple] = [
    # ---- Section 2.4: Table 2 and a paragraph ---------------------------------------------------------------------
    ("| Signal Recovery 5184 | 0.8 | 50 | 0.5 Hz–1 MHz | AC | |",
     "| Signal Recovery 5113 | 4 | 25 | DC–1 MHz | AC or DC | 1 kHz; about 8 at 1 kHz, and 4 only from 10 kHz, in its own "
     "noise-figure plot (Section 6.2) |\n"
     "| Signal Recovery 5184 | 0.8 | 50 | 0.5 Hz–1 MHz | AC | |"),
    ("\n\n---\n\n## 3. Choosing JFETs today",
     "\n\nThe Signal Recovery 5113 (AMETEK, formerly EG&G Princeton Applied Research: DC–1 MHz, internal batteries, a "
     "FET buffer on each input ahead of a differential gain stage of 4, 40 or 400 in the block diagram of its 1992 "
     "manual, Fig. 4-1) is specified like the SR560, at 4 nV/√Hz at 1 kHz with 25 pF. Its manual also publishes a "
     "noise-figure plot, and that plot implies about twice this noise at 1 kHz and far more below it (Section 6.2, "
     "Figure 14j–l)."
     "\n\n---\n\n## 3. Choosing JFETs today"),
    # ---- Section 6.2: the 5113's plot ------------------------------------------------------------------------------
    ("\n\n![Figure 14](figures/fig_nf_map.png)",
     "\n\nFigure 14j–l set H and L against a second published plot, the noise-figure contours of the Signal Recovery "
     "5113: \"Typical Noise Figure Contours at Gain = ×1000, AC Coupling and 10s Coupling Time-Constant, Flat Filter "
     "Mode\" (manual 222144-A-MNL-F, 2002, Fig. A-1, p. A-2; the same plot is in its 2010 data sheet and in the 2024 "
     "data sheet of the 5113A, and there is none in its 1992 EG&G manual). The plot is a 1-bit image, so it is read "
     "from its pixels (`scripts/nf5113_manual.py`, `sim/results/nf5113_manual.json`): the axes are calibrated on the "
     "frame and the dashed decade grid (100.0 pixels per decade on both axes, to within 0.4 px); the ten labels that "
     "sit inside their contours at 10 kHz are bridged; each contour takes the level printed on it or, near 1 Ω, "
     "beside it; and the five unlabelled contours in the upper right corner take 6, 10, 15, 20 and 30 dB in order "
     "towards the corner, which their resistances on the 1 MHz edge bear out: 0.20, 0.60, 2.1, 6.6 and 66 MΩ, in the "
     "ratios of $F - 1$ to within 1.9 %, as where a noise current dominates. Thinned to lines, the contours obey "
     "Eq. (5a) within 0.24 dB (0.034 decade of $R_S$) from 3.98 Hz, where the plot draws both sides of its minimum; "
     "below that it draws only the low-resistance side, which gives $e_n$ (within 0.48 dB, with $i_n$ held at its "
     "low-frequency value)."
     "\n\nRead this way, the plot disagrees with its own specification. The same page gives \"4 nV/√Hz at 1 kHz "
     "referred to input - see also figure A-1\" (so do the 1992 manual and both data sheets), but the contours give "
     "4 nV/√Hz only from 10 kHz up (4.03, 3.99 and 4.01 nV/√Hz at 10 kHz, 100 kHz and 1 MHz) and 7.94 nV/√Hz at "
     "1 kHz, 1.98 times the specification. Each low-resistance contour from 3 to 30 dB gives 7.85–8.02 nV/√Hz on its "
     "own, and the 3 dB contour lies at 3.87 kΩ, where 4 nV/√Hz would put it at 1.00 kΩ. Below 1 kHz the plotted "
     "noise rises steeply, to 29.9 nV/√Hz at 100 Hz, 101 at 10 Hz, 722 at 1 Hz and 8.2 µV/√Hz at 0.1 Hz. As a 1/f "
     "corner, $f\\,(e_n^2 - e_w^2)/e_w^2$ with $e_w$ at 100 kHz, that is 3.0 kHz from 1 kHz, 5.5 kHz from 100 Hz and "
     "6.4 kHz from 10 Hz, against 23–34 Hz in the SR560's plot, and below 10 Hz the noise power rises faster than "
     "1/f, as $f^{-1.71}$ from 1 to 10 Hz and $f^{-2.11}$ from 0.1 to 1 Hz. Between whole decades the low-resistance "
     "contours are straight in log–log (the fitted $e_n$ departs from the straight lines between the decades by at "
     "most 0.014 decade) and they bend only at the decades: the plot was drawn from values at whole decades, and its "
     "sharp corner at 10 kHz, where its low-resistance contours turn level, is the drawing's. The AC coupling of the "
     "plot's setting does not account for the low-frequency noise: the plot's own noise current through the 0.1 µF "
     "coupling capacitor gives 0.28 µV/√Hz at 0.1 Hz, 1/29 of the plotted $e_n$, and the 10 s high-pass passes 0.988 "
     "of the signal there. The plotted noise current is 17.7 fA/√Hz at low frequencies (17.5–18.0 from 5 Hz to "
     "5 kHz), the thermal noise of 51 MΩ at 290 K and 1.40 times the 12.7 fA/√Hz of the 100 MΩ input resistance that "
     "the 10 s time constant implies; the manual does not say where the rest comes from. Above 10 kHz it rises as "
     "$e_n\\omega C$ with $C$ = 19.5–20.1 pF from 100 kHz to 1 MHz (25 pF specified), about half the 38 pF of the "
     "SR560's plot."
     "\n\nAgainst this plot (Figure 14k and l, from 3.98 Hz to 1 MHz), H's noise figure is lower everywhere: by more "
     "than 0.1 dB on 92 % of the plane, by up to 34.1 dB (3.98 Hz, 1 Ω), and by 0.03–0.1 dB on the rest, around the "
     "5113's own optimum. At 1 kHz the 5113's plot reaches 3 dB with 3.9 kΩ and 1 dB with 15 kΩ, against H's 78 Ω "
     "and 300 Ω; at 10 Hz it reaches 3 dB only with 670 kΩ and 1 dB nowhere (its minimum there is 0.93 dB, at "
     "5.7 MΩ), against 500 Ω and 1.9 kΩ; at 1 MHz it is below 3 dB from 1.0 to 66 kΩ, H from 75 Ω to 85 kΩ. L is "
     "lower on 63 % of the plane, by up to 43.6 dB, and higher on 32 %, with sources above 2.9 MΩ at 10 Hz, 220 kΩ "
     "at 1 kHz, 27 kΩ at 100 kHz and 2.8 kΩ at 1 MHz, by up to 9.79 dB (1 MHz, 100 MΩ), from its 10 MΩ bias "
     "resistors and its input network. Even the SR560 data sheet's plot is lower than the 5113's on 76 % of the "
     "plane; it is higher on 13 %, from 20 kHz up, with sources above 25 kΩ at 100 kHz and 2.4 kΩ at 1 MHz, by up to "
     "4.88 dB (1 MHz, 100 MΩ), where the 5113's smaller capacitance, 20 against 38 pF, gives it the lower noise "
     "current. Like the SR560's, the 5113's plot is its maker's \"typical\" figure, and no measurement here tells "
     "which of its plot and its specification a real 5113 meets."
     "\n\n![Figure 14](figures/fig_nf_map.png){.fitpage}"),
    # Figure 14, now 4 x 3, at 90 % of the width, so that it and its caption fit one page of the PDF
    ("img.tall { width: 80%; }", "img.tall { width: 80%; }\nimg.fitpage { width: 90%; }"),
    # ---- Figure 14's caption ---------------------------------------------------------------------------------------
    ("(e, f, h, i) The noise figure of (b), (c), (d) and (g) minus the data sheet's, on its range: blue where lower "
     "than the data sheet's. (`scripts/sr560_nf_datasheet.py`, `scripts/nf_map.py`, `sim/results/nf_map.json`; numbers "
     "rounded by `scripts/numbers_s6_7.py`.)*",
     "(e, f, h, i) The noise figure of (b), (c), (d) and (g) minus the data sheet's, on its range: blue where lower "
     "than the data sheet's. (j) The Signal Recovery 5113's plot (manual Fig. A-1: gain 1000, AC coupled, 10 s), "
     "read from its pixels, at its own levels from 0.1 to 50 dB (40 and 50 dB, which do not reach 2 kHz, labelled at "
     "10 Hz). (k, l) The noise figure of H and L minus the 5113 plot's, from 3.98 Hz, where the plot draws both sides "
     "of its minimum (shaded below), to its 1 MHz limit: blue where lower than the 5113's. "
     "(`scripts/sr560_nf_datasheet.py`, `scripts/nf5113_manual.py`, `scripts/nf_map.py`, `sim/results/nf_map.json`, "
     "`nf5113_manual.json`; numbers rounded by `scripts/numbers_s6_7.py`.)*"),
    # ---- Section 8 -----------------------------------------------------------------------------------------------
    ("| `scripts/nf_map.py`, `scripts/sr560_nf_datasheet.py`, `scripts/sr560_nf_sources.py` | Figure 14 and its "
     "numbers",
     "| `scripts/nf_map.py`, `scripts/sr560_nf_datasheet.py`, `scripts/sr560_nf_sources.py`, `scripts/nf5113_manual.py` "
     "| Figure 14 and its numbers"),
    ("the SR560 models' input capacitance and their noise current by source (`sr560_nf_sources.json`) |",
     "the SR560 models' input capacitance and their noise current by source (`sr560_nf_sources.json`); the Signal "
     "Recovery 5113 manual's noise-figure plot read from its pixels, with its two-port fit and H, L and the SR560 data "
     "sheet's plot against it (`nf5113_manual.json`) |"),
    # ---- References --------------------------------------------------------------------------------------------------
    ("Further instruments in `refs/commercial_preamps/survey.md`.\n",
     "Further instruments in `refs/commercial_preamps/survey.md`.\n"
     "- Signal Recovery (AMETEK Advanced Measurement Technology), *Model 5113 Low Noise Preamplifier*, instruction "
     "manual 222144-A-MNL-F, 2002 (specifications, its appendix A, printed pp. A-1–A-6; noise-figure contours, Fig. A-1, "
     "p. A-2, read in `scripts/nf5113_manual.py`); EG&G Instruments, *Model 5113 Pre-Amplifier*, instruction manual "
     "222144-A-MNL-C, 1992 (specifications, p. 2; circuit description, p. 11; block diagram, Fig. 4-1, p. 13); the "
     "5113 data sheet \"CatIss7Web:0710UK\" (2010, p. 1) and the 5113A data sheet, AMT-C00007 (2024, p. 2); in "
     "`refs/commercial_preamps/SignalRecovery_AMETEK/`.\n"),
]


def main() -> None:
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    assert "\r" not in text
    if "Figure 14j–l set H and L against" in text:
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
