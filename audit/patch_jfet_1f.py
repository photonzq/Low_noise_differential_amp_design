"""Patch of low_noise_preamp.md (25 November 2026): the JFET models' 1/f noise below 10 Hz stated as the extrapolation
it is (Section 3.4), with the data that disagree with it in either direction, the JFE150's own curve and peak-to-peak
value (L, possibly optimistic) and a published measurement of H's configuration (H, likely pessimistic); the
qualification where the note quotes the front ends' 1 Hz noise (Section 4.8); and Section 7: the models' sentence, the
bipolar input's open items, and the measurement in the next steps.
Every number comes from sim/results/numbers_s3_5.json (its section34 group) or from the pages cited, read again for
this patch: SLPS732B pp. 5, 7 (Fig. 6-9) and 8 (Fig. 7-1); SLPS730B p. 8 (Fig. 6-14); Spinelli and Haberman (2024),
p. 5 (Fig. 7 and the bias); ngspice-46 User's Manual, Section 7.4.4, p. 154.
Exact-string edits, each old text once; a second run refused.
Usage: python patch_jfet_1f.py <path to low_noise_preamp.md>
"""
from __future__ import annotations

import sys
from pathlib import Path

S34 = r"""

**The JFET models below 10 Hz.** Each model's KF is fitted at one low frequency, 10 Hz for the JFE150, JFE2140 and LSBF862 (Table 4), and below it the model is pure 1/f noise: ngspice's JFET has no parameter for the frequency exponent, only KF and AF (ngspice-46 User's Manual, Section 7.4.4, p. 154). Other data disagree with that extension by a factor of two to three at 1 Hz, in both directions:

- *JFE150 (L), possibly optimistic.* The data sheet's curve (SLPS732B Fig. 6-9, p. 7), at 5 mA and 5 V, agrees with its table at 10 Hz but rises faster below it, to about 14 nV/√Hz per device at 1 Hz, where the model gives 5.2; the table's 0.1–10 Hz value of 0.13 µV peak to peak (p. 5) implies 9.1 nV/√Hz at 1 Hz for pure 1/f noise. For L's twelve JFETs per side these readings mean 2.1, 3.7 or 5.7 nV/√Hz at 1 Hz; for L's front end 2.3 (Table 9), 3.9 or 5.8 nV/√Hz, and for the chain at a gain of 1000 2.8 (Table 10), 4.1 or 6.0 nV/√Hz. TI measures through a 1 µF and 100 kΩ coupling, a high-pass at 1.6 Hz, with a 3 mF source bypass, and corrects the result by the circuit's measured gain (SLPS732B Fig. 7-1, p. 8), so its points below a few hertz rest on that correction.
- *JFE2140 (H), likely pessimistic.* The model agrees with the data sheet's curve at H's 5 mA (SLPS730B Fig. 6-14, p. 8: about 8 and 2.2 nV/√Hz per device at 1 and 10 Hz, against the model's 7.0 and 2.4 for H's two JFETs per side), but that curve is taken at 10 V. Spinelli and Haberman measured H's configuration, two JFE2140 per side at 7 mA with the drains at 5 V and OPA211 op amps: 3.2, 1.56 and 0.89 nV/√Hz at 1 Hz, 10 Hz and 1 kHz (their Fig. 7, p. 5, read by eye). That is 2.2 times lower than H's JFETs in the model at 1 Hz and 1.5 times at 10 Hz, with the same white level. Whether the difference lies in the bias (H's JFETs run at 3.9 V), in the samples or in the measurement, these two sources bracket H's JFET noise below 10 Hz.

Above about 10 Hz the models follow their data sheets (Figure 5); below it, only a measurement of the built front ends settles their noise (Section 7)."""

EDITS = [
    ("The calibration fits the two capacitances at the bias where the data sheet gives them, which is what matters "
     "for the circuit.\n\n### 3.5 Bipolar input stages and 1/f noise",
     "The calibration fits the two capacitances at the bias where the data sheet gives them, which is what matters "
     "for the circuit." + S34 + "\n\n### 3.5 Bipolar input stages and 1/f noise"),
    ("**Case DC–10 MHz (this design).** The values of Table 9: H 2.7 nV/√Hz at 10 Hz and 7.8 at 1 Hz (gain 100), "
     "L 0.83 and 2.3.",
     "**Case DC–10 MHz (this design).** The values of Table 9: H 2.7 nV/√Hz at 10 Hz and 7.8 at 1 Hz (gain 100), "
     "L 0.83 and 2.3. At 1 Hz the JFETs' share rests on the extrapolation of their 10 Hz calibration, which a "
     "published measurement puts 2.2 times too high for H's JFETs and the JFE150's own curve up to 2.7 times too low "
     "for L's (Section 3.4)."),
    ("The JFET models reproduce their data sheets' noise and capacitance at the data sheets' bias points, with "
     "ngspice's fixed junction grading exponent of 0.5; the capacitances at other voltages, and their nonlinearity, "
     "are approximate.",
     "The JFET models reproduce their data sheets' noise and capacitance at the data sheets' bias points, with "
     "ngspice's fixed junction grading exponent of 0.5; the capacitances at other voltages, and their nonlinearity, "
     "are approximate. Their noise below 10 Hz is the 1/f extension of their 10 Hz values, which other data put a "
     "factor of two to three either way at 1 Hz (Section 3.4).\n\n"
     "**The bipolar input of Section 3.5.** It is a study, not part of the design. Before it is built, the "
     "SSM2212's base-current noise must be measured against frequency (with a source of 100 kΩ to 1 MΩ, from "
     "0.1 Hz), and its voltage noise with a shorted pair, since its advantage rests on them; and its input network "
     "must be designed, since its bare input has a negative resistance at a few megahertz (Section 3.5)."),
    ("**Next steps.** A board of one front end (H, then L) with its difference amplifier, to measure the noise with "
     "shorted inputs by cross-correlation of two units (Rubiola and Vernotte 2010), the stability, and the CMRR; then "
     "the full chain.",
     "**Next steps.** A board of one front end (H, then L) with its difference amplifier, to measure the noise with "
     "shorted inputs by cross-correlation of two units (Rubiola and Vernotte 2010), down to 0.1 Hz to settle the "
     "JFETs' noise below 10 Hz (Section 3.4), the stability, and the CMRR; then the full chain."),
]


def main() -> None:
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    assert "\r" not in text
    if "**The JFET models below 10 Hz.**" in text:
        sys.exit("already patched: refusing a second run")
    for old, new in EDITS:
        c = text.count(old)
        assert c == 1, (c, old[:90])
        text = text.replace(old, new)
    print(f"{len(EDITS)} edits applied to {path.name}")
    path.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
