"""Patch of low_noise_preamp.md after patch_renumber_s3_5b.py (25 November 2026): Section 3.5's two new figures, the
schematic of B's side A (Figure 7, scripts/make_schematics.py, checked against the simulated netlist) and B's
noise-figure maps (Figure 8, scripts/make_figures.py fig_bipolar_nf_map); the justification of B's cascodes; the
testbench's bias path (an ideal current source instead of the reactive path of the first version); Section 8's rows.
Every number comes from sim/results/numbers_s3_5.json.  Exact-string edits, each old text once; a second run refused.
Usage: python patch_bipolar_s3_5b.py <path to low_noise_preamp.md>
"""
from __future__ import annotations

import sys
from pathlib import Path

FIG7 = r"""

![Figure 7](figures/schematic_front_end_B.png)

*Figure 7. Side A of the bipolar front end B: L's front end of Figure 11 with 24 SSM2212 per side (one transistor of each dual) at 2.5 mA in place of its twelve JFE150, each transistor cascoded by its own LSBF862, and B's compensation ($C_I$ 75 pF, $C_X$ 7.5 pF, $C_{node}$ 2.2 nF). $R_{UP}$ is 12.2 kΩ against L's 10.9 kΩ because the source node sits 0.59 V below the input instead of above it. The 24 transistors and their cascodes are drawn as one, with the count beside them; side B is its mirror image as in Figure 10. Drawn and checked part by part, value by value and pin by pin against the simulated netlist (`scripts/make_schematics.py`).*"""

FIG8 = r"""

![Figure 8](figures/fig_bipolar_nf_map.png)

*Figure 8. Noise figure of the bipolar front end B against source resistance and frequency, for a source at 290 K, in the format of Figure 17 (the SR560 data sheet's contour levels and label positions), drawn from the two-port fits of its runs from 0.1 Ω to 1 MΩ, which they reproduce within 4 × 10⁻⁶ dB, on that range (`scripts/bipolar_inputs.py`). (a) The base-current 1/f corner of 200 Hz at 1 mA; (b) 30 Hz and (c) 1 kHz, the ends of its bracket. (d) B minus L, both as front ends without an input network (L swept as B), blue where B is the quieter; the solid line is equal noise with the corner of 200 Hz, the dashed lines with 30 Hz and 1 kHz.*"""

CASCODES = (" Figure 7 shows its side A, drawn from the simulated netlist and checked against it part by part and pin by "
            "pin. The cascodes serve B as they serve L. With their gates held 3.5 V above the source node by the bootstrap, "
            "they keep each transistor's collector–emitter voltage constant as the input moves, so that its collector–base "
            "capacitance, 17.4 pF at B's 3.39 V (the card's, from the MAT12's Fig. 12), does not load the input: with the "
            "collectors held fixed, by the summing node or by unbootstrapped cascodes, the 24 transistors of a side would "
            "put 0.42 nF on it, against the 10 pF that B shows at 1 kHz. They also keep the input from modulating, through "
            "the Early effect, the base current that flows in the source. Their number is L's, one per transistor; since a "
            "side's transistors share base, emitter and collector, fewer and larger cascodes would serve as well (twelve at "
            "L's 5 mA, for example). Their noise is negligible, 0.06 pV/√Hz at 1 kHz.")

EDITS = [
    # the testbench's bias path
    ("and a noiseless source resistance in series with input A; at each frequency the runs over the source resistance",
     "and a noiseless source resistance in series with input A, the base current coming from an ideal current source so "
     "that none flows in the source; at each frequency the runs over the source resistance"),
    # Figure 7 and the cascodes
    ("each dual gives one transistor to each side, as H's JFE2140 duals do (`scripts/frontend.py`, whose input devices "
     "can now be a bipolar card, and `scripts/bipolar_inputs.py`).",
     "each dual gives one transistor to each side, as H's JFE2140 duals do (`scripts/frontend.py`, whose input devices "
     "can now be a bipolar card, and `scripts/bipolar_inputs.py`)." + CASCODES),
    ("A smaller $R_G$, with $R_F$ scaled with it, would lower both.",
     "A smaller $R_G$, with $R_F$ scaled with it, would lower both." + FIG7),
    # Figure 8
    ("With 1 Ω, B gains 11.9 dB at 1 Hz (7.7–13.7 dB) and 2.4 dB at 1 kHz; with 100 Ω it loses 10.9 dB at 1 Hz and "
     "0.7 dB at 1 kHz.",
     "With 1 Ω, B gains 11.9 dB at 1 Hz (7.7–13.7 dB) and 2.4 dB at 1 kHz; with 100 Ω it loses 10.9 dB at 1 Hz and "
     "0.7 dB at 1 kHz. Figure 8 maps B's noise figure in the format of Figure 17, with the corner's bracket and the "
     "difference from L. B's minimum noise figure is 0.97 dB with 49 Ω at 1 kHz, 3.9 dB with 12 Ω at 10 Hz and 9.8 dB "
     "with 6 Ω at 1 Hz; at 1 kHz its optimum source resistance thus lies just above the crossover, where L is already "
     "slightly the quieter, and B's merit lies below its own optimum." + FIG8),
    # Section 8
    ("| `scripts/bipolar_inputs.py` | Section 3.5 and Figure 6:", "| `scripts/bipolar_inputs.py` | Section 3.5, Figures 6 and 8:"),
    ("| `scripts/make_figures.py`, `scripts/plot_style.py` | Figures 1, 3–6, 12, 13 and 15–20 |",
     "| `scripts/make_figures.py`, `scripts/plot_style.py` | Figures 1, 3–6, 8, 12, 13 and 15–20 |"),
    ("| `scripts/make_schematics.py`, `scripts/schematics.py`, `scripts/schematic_style.py` | Figures 2, 9–11 and 14,",
     "| `scripts/make_schematics.py`, `scripts/schematics.py`, `scripts/schematic_style.py` | Figures 2, 7, 9–11 and 14,"),
]


def main() -> None:
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    assert "\r" not in text
    if "![Figure 7](figures/schematic_front_end_B.png)" in text:
        sys.exit("already patched: refusing a second run")
    assert "![Figure 20](figures/fig_large_signal.png)" in text, "renumber first (patch_renumber_s3_5b.py)"
    for old, new in EDITS:
        c = text.count(old)
        assert c == 1, (c, old[:90])
        text = text.replace(old, new)
    print(f"{len(EDITS)} edits applied to {path.name}")
    path.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
