"""Patch of low_noise_preamp.md after patch_nf_map.py (24 November 2026): Section 6.2, where the SR560
reproductions and the data sheet's noise-figure plot disagree, and why, as an explicit list (Figure 14h and i):

- low frequencies, low source resistances: the JFET model's 1/f noise;
- mid frequencies, high source resistances: the tail servo's noise, made differential by the unbalanced source;
  the disagreement is between the reproduction's circuit and the data sheet's plot, and no measurement tells
  which a real SR560 does;
- about 1 MHz, high source resistances: the input capacitance (the cause of this difference had been dropped when
  the paragraph was rewritten; numbers_s6_7.py now derives the capacitance);
- the white level: the reproductions below the plot, not traced to a part of the circuit.
Numbers from numbers_s6_7.py, group "s6.2 Figure 14".
Every edit is an exact-string replacement whose old text occurs once.  A second run is refused.
Usage: python patch_nf_map_sources.py <path to low_noise_preamp.md>
"""
from __future__ import annotations

import sys
from pathlib import Path

OLD = (
    " Both reproductions also depart from the data sheet with high source resistances at mid frequencies (the red "
    "regions at the upper right of Figure 14h and i), where the LSK389B model's noise figure is up to 6.9 dB above "
    "it (63 kHz, 100 MΩ) and its noise current at 100 kHz is 0.187 pA/√Hz (0.100 as drawn), against the data "
    "sheet's 0.087. That noise is the pair's tail servo's: with 1 MΩ in input A, U103 (an LF411) with R125, R127, "
    "R129 and R130 gives 97 % (NPD5564) and 98 % (LSK389B) of the output noise at 100 kHz. It sits on the JFETs' "
    "common source node, where a balanced source rejects it as common mode: with 1 MΩ also from input B to ground, "
    "its share falls to 0.03 and 0.04 %. With input B grounded, gate A follows its source through the gate–source "
    "capacitance and gate B cannot, so the servo's noise appears across the pair, the more with the LSK389B's "
    "larger capacitances; the data sheet's plot, whose current noise is that of a single 38 pF, has no such term. "
    "At 1 MHz both reproductions are below the data sheet again (noise currents 0.37 and 0.74 pA/√Hz, against "
    "0.86), and beyond its plot and the SR560's bandwidth their minimum noise figure reaches 29 and 43 dB at "
    "10 MHz, where H's is 2.42 dB (at 440 Ω) and L's 3.43 dB (at 37 Ω)."
)

NEW = (
    "\n"
    "\n"
    "Where the reproductions and the data sheet's plot disagree, and why (Figure 14h and i):\n"
    "\n"
    "- **Low frequencies, low source resistances: the JFET model.** The reproduction as drawn is up to 16.0 dB "
    "above the data sheet (10 Hz, 1 Ω), from its JFET model's 1/f noise (above); with the LSK389B it is below the "
    "data sheet there, by up to 10.3 dB (1 Hz, 1 Ω).\n"
    "- **Mid frequencies, high source resistances: the tail servo.** Both reproductions are above the data sheet "
    "there (the red regions at the upper right of Figure 14h and i), by up to 6.9 dB (LSK389B, 63 kHz, 100 MΩ); "
    "at 100 kHz the LSK389B model's noise current is 0.187 pA/√Hz (0.100 as drawn), against the data sheet's "
    "0.087. That noise is the pair's tail servo's: with 1 MΩ in input A, U103 (an LF411) with R125, R127, R129 "
    "and R130 gives 97 % (NPD5564) and 98 % (LSK389B) of the output noise at 100 kHz. It sits on the JFETs' common "
    "source node, where a balanced source rejects it as common mode: with 1 MΩ also from input B to ground, its "
    "share falls to 0.03 and 0.04 %. With input B grounded, gate A follows its source through the gate–source "
    "capacitance and gate B cannot, so the servo's noise appears across the pair, the more with the LSK389B's "
    "larger capacitances. The disagreement is thus between the reproduction's circuit, which has the servo of the "
    "schematic, and the data sheet's plot, which Eq. (5a) reproduces with $e_n$, the input resistors' thermal "
    "noise and a single 38 pF and which has no such term; no measurement here tells whether a real SR560 shows "
    "it.\n"
    "- **About 1 MHz, high source resistances: the input capacitance.** Both reproductions are below the data "
    "sheet there: their noise current at 1 MHz is 0.37 and 0.74 pA/√Hz, against 0.86. Without the servo's share "
    "(79 and 82 % of the output noise with 1 MΩ), what is left is 0.17 and 0.32 pA/√Hz, an $e_n\\omega C$ with "
    "$C$ = 8.5 pF (NPD5564) and 15.7 pF (LSK389B), against the plot's 38 pF and the specified 25 pF: the model's "
    "inputs have no capacitance beyond the JFETs', no connector, protection or wiring.\n"
    "- **The white level.** At 100 kHz the reproductions are 11.6 % (NPD5564) and 10.9 % (LSK389B) below the "
    "plot's 3.60 nV/√Hz and within 0.76 % of each other, since the resistors and the single pair set this level "
    "in both (Section 2.3); the plot lies between them and the manual's \"about 4 nV/√Hz\". This difference is "
    "not traced here to a part of the circuit.\n"
    "\n"
    "Beyond the data sheet's plot and the SR560's bandwidth, the reproductions' minimum noise figure reaches 29 "
    "and 43 dB at 10 MHz, where H's is 2.42 dB (at 440 Ω) and L's 3.43 dB (at 37 Ω)."
)

EDITS: list[tuple] = [(OLD, NEW)]


def main() -> None:
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    assert "\r" not in text
    if "Where the reproductions and the data sheet's plot disagree" in text:
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
