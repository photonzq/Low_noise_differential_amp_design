"""Second patch of low_noise_preamp.md after the number audit (22 November 2026): the THS4021's and
THS4031's input current noise at 10 Hz, read from the pixels of their data sheets' curves.

SLOS265F Fig. 5-12 (p. 11) and SLOS224L Fig. 5-14 (p. 12) give 18.5-18.8 pA/rtHz at the 10 Hz frame edge;
the note quoted the reading by eye, 20 pA/rtHz, which is also what models.py's 1/f generators were fitted
to.  The data-sheet value becomes 18.6 pA/rtHz (opamp_noise_check.py, model_defects.py, numbers_s4b_5.py;
re-run), so the models' error at 10 Hz is 15.8x and 16.1x (16x, not 15x) and the data sheets' current-noise
corner 0.65 kHz (not 0.76).  The fit is kept: numbers_s4b_5.json (*_in10_fit_effect) bounds its effect on
the front ends' noise, which Section 5.3 now states.

Every edit is an exact-string replacement whose old text occurs exactly once; no line is added.
A second run is refused.  Usage: python patch_post2.py <path to low_noise_preamp.md>
"""
from __future__ import annotations

import sys
from pathlib import Path

EDITS: list[tuple[str, str]] = [
    ("the first two the current noise at 10 Hz by 15 times",
     "the first two the current noise at 10 Hz by 16 times"),
    ("(about 4 nV/√Hz and 20 pA/√Hz at 10 Hz, Figs. 5-11 and 5-12, p. 11)",
     "(about 4 nV/√Hz and 18.6 pA/√Hz at 10 Hz, Figs. 5-11 and 5-12, p. 11)"),
    ("4 nV/√Hz, 20 pA/√Hz (SLOS265F Figs. 5-11, 5-12, p. 11)",
     "4 nV/√Hz, 18.6 pA/√Hz (SLOS265F Figs. 5-11, 5-12, p. 11)"),
    ("| 4.6×, 15×; 0.52× |", "| 4.6×, 16×; 0.52× |"),
    ("4 nV/√Hz, 20 pA/√Hz (SLOS224L Figs. 5-13, 5-14, p. 12)",
     "4 nV/√Hz, 18.6 pA/√Hz (SLOS224L Figs. 5-13, 5-14, p. 12)"),
    ("| 5.5×, 15×; 0.49× |", "| 5.5×, 16×; 0.49× |"),
    ("against the data sheets' 4 nV/√Hz and 20 pA/√Hz: the model's current-noise 1/f corner",
     "against the data sheets' 4 nV/√Hz and 18.6 pA/√Hz: the model's current-noise 1/f corner"),
    ("instead of the data sheets' 0.76 kHz (`scripts/numbers_s4b_5.py`).",
     "instead of the data sheets' 0.65 kHz (`scripts/numbers_s4b_5.py`). The 1/f generators that replace it "
     "were fitted to 20 pA/√Hz at 10 Hz, the curves as first read by eye; read from their pixels, both curves "
     "give 18.5–18.8 pA/√Hz, so the corrected models' 1/f current noise is about 7 % high. Through Eq. (9) "
     "this raises the front ends' simulated noise at 10 Hz by 1.1 % (H at a gain of 100), 2.7 % (H at 10) and "
     "0.2 % (L), by at most 3.5 % at 1 Hz and by 0.1 % or less from 1 kHz up (`scripts/numbers_s4b_5.py`, "
     "$\\sqrt{e^2 - 2w^2(19.9^2 - (18.6^2 - 2.3^2))\\ \\mathrm{pA^2} \\cdot 10\\ \\mathrm{Hz}/f}$ with $w$ "
     "the weight of Eq. (9)): the low-frequency figures of this note are pessimistic by that much."),
]


def main() -> None:
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    assert "\r" not in text
    if "by 16 times" in text:
        sys.exit("already patched: refusing a second run")
    n_lines = text.count("\n")
    for old, new in EDITS:
        c = text.count(old)
        assert c == 1, (c, old[:90])
        text = text.replace(old, new)
    assert text.count("\n") == n_lines
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"{len(EDITS)} replacements applied to {path.name}")


if __name__ == "__main__":
    main()
