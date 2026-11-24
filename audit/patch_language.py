"""Patch of low_noise_preamp.md after patch_h_l_roles.py (24 November 2026):

- The front ends' gain ranges in their descriptions (the summary's bullets and Section 4.1.1): H's two ranges,
  x10 and x100, selected by a relay that switches R_G (111 or 10.1 ohm with R_F = 500 ohm; G_FE = 1 + 2 R_F / R_G),
  which range each gain mode uses, and L's single gain of 201 (R_F = 249 ohm, R_G = 2.49 ohm); from Table 5,
  Section 4.1 and Table 9.
- Descriptive headings and run-in labels in place of questions and colloquial phrases ("What is better than the
  LSK389", "Why two front ends, and what each is for", "How robust the adopted fix is", ...), and two colloquial
  sentences of Section 4.1.1.  No heading number changes; the build links sections by number, and no other file
  names these headings.
Every edit is an exact-string replacement whose old text occurs once.  A second run is refused.
Usage: python patch_language.py <path to low_noise_preamp.md>
"""
from __future__ import annotations

import sys
from pathlib import Path

GAIN = [
    # the summary's bullets
    ("0.11 pF at 1 MHz; `sim/results/zin_numbers.json`).\n- **L** (low impedance)",
     "0.11 pF at 1 MHz; `sim/results/zin_numbers.json`). Its front end has two selectable gain ranges, ×10 and "
     "×100: a relay switches $R_G$ between 111 Ω and 10.1 Ω with $R_F$ = 500 Ω, so that $G_{FE} = 1 + 2R_F/R_G$ = "
     "10.0 or 100.0 (Table 5). The low-noise mode uses ×100 from a total gain of 100 up and ×10 below; the "
     "high-reserve mode keeps ×10 at total gains of 100–1000, for 20 dB more headroom at the input at 2.3–2.5 times "
     "the noise (Table 9). H covers total gains from 1 to 50 000.\n- **L** (low impedance)"),
    ("Input noise **0.42 nV/√Hz** white (0.43 at 1 kHz, 0.96 at 10 Hz; gain 1000). It has the lower noise",
     "Input noise **0.42 nV/√Hz** white (0.43 at 1 kHz, 0.96 at 10 Hz; gain 1000). Its front end has a single gain "
     "of 201 ($R_F$ = 249 Ω, $R_G$ = 2.49 Ω), so L covers total gains from 200 to 100 000. It has the lower noise"),
    # Section 4.1.1
    ("Its front end has a fixed gain of 201, so it serves total gains from 200 to 100 000.",
     "Its front end has a single, fixed gain of 201 ($R_F$ = 249 Ω, $R_G$ = 2.49 Ω; Table 5), so it serves total "
     "gains from 200 to 100 000."),
    ("Its front end switches between gains of 10 and 100, so it serves total gains from 1 to 50 000, and from 100 to "
     "1000 in the high-reserve mode, with 20 dB more headroom at the input (Section 4.1).",
     "Its front end has two gain ranges, ×10 and ×100, selected by a relay that switches $R_G$ between 111 Ω and "
     "10.1 Ω ($R_F$ = 500 Ω; $G_{FE} = 1 + 2R_F/R_G$ = 10.0 or 100.0; Table 5). In the low-noise mode the front end "
     "runs at ×100 from a total gain of 100 up and at ×10 below; in the high-reserve mode it stays at ×10 at total "
     "gains of 100–1000, for 20 dB more headroom at the input at 2.3–2.5 times the noise (Section 4.1, Table 9). H "
     "thus serves total gains from 1 to 50 000."),
    ("The wrong input costs most at the two ends and little in between.",
     "The penalty for the wrong input is largest at the two ends of the source range and small in between."),
    ("the two differ in noise by less than 1 % (Section 6.2), and either serves.",
     "the two differ in noise by less than 1 % (Section 6.2), and either input may be used."),
]

HEADINGS = [
    ("## 1. What sets the noise floor of a voltage preamplifier", "## 1. The noise floor of a voltage preamplifier"),
    ("### 1.3 The source decides", "### 1.3 Noise matching to the source"),
    ("### 1.5 What else adds noise in a feedback front end", "### 1.5 Further noise sources in a feedback front end"),
    ("### 2.3 What limits the SR560, and what a successor can change",
     "### 2.3 Limits of the SR560 and improvements for a successor"),
    ("## 3. Choosing JFETs today", "## 3. Selection of low-noise JFETs"),
    ("### 3.1 The parameters, and how to use them", "### 3.1 Selection parameters"),
    ("### 3.2 The survey\n", "### 3.2 Survey of low-noise JFETs\n"),
    ("### 3.3 What is better than the LSK389", "### 3.3 JFETs that outperform the LSK389"),
    ("### 3.4 Calibrating the JFET models", "### 3.4 Calibration of the JFET models"),
    ("#### 4.1.1 Why two front ends, and what each is for", "#### 4.1.1 Roles of the two front ends"),
    ("### 4.3 The loops, and why the first version oscillated", "### 4.3 Feedback loops and the first version's oscillation"),
    ("#### 4.3.1 Mitigations: making the front end's stability robust",
     "#### 4.3.1 Robust stability: margins, alternatives and bench tests"),
    ("### 4.5 The rest of the chain", "### 4.5 Signal chain after the front end"),
    ("## 5. How the design was simulated", "## 5. Simulation methods"),
    ("### 5.3 Vendor models that were wrong, and how", "### 5.3 Defects of the vendor models"),
    ("### 6.2 Noise with a source\n", "### 6.2 Noise with a source resistance\n"),
    ("### 6.6 How the design compares", "### 6.6 Comparison with the SR560 and the NF 5307"),
    ("## 7. What is not verified, and the next steps", "## 7. Unverified aspects and next steps"),
]

LABELS = [
    ("**Why two front ends.**", "**Roles of the two front ends.**"),
    ("**How the trim is set numerically.**", "**Numerical setting of the trim.**"),
    ("**Why the summing node sits at +9 V.**", "**The summing-node voltage of +9 V.**"),
    ("**The root cause in one line.**", "**The root cause.**"),
    ("**How robust the adopted fix is.**", "**Robustness of the adopted fix.**"),
    ("**Other cures, and what each costs.**", "**Other cures and their costs.**"),
    ("*Not recommended.*", "*Options not recommended.*"),
    ("**Design rules that would have caught it.**", "**Design rules against this failure.**"),
    ("**On the bench.**", "**Bench tests.**"),
    ("**Input protection, and what it costs.**", "**Input protection and its costs.**"),
    ("**How the TI JFET models are wrong.**", "**Defects of the TI JFET models.**"),
    ("**How the TI op-amp models are wrong.**", "**Defects of the TI op-amp models.**"),
    ("**How the Linear Systems and LTspice cards are wrong.**", "**Defects of the Linear Systems and LTspice cards.**"),
    ("**What sets a current sink's noise.**", "**Noise of a current sink.**"),
    ("**Quieter sinks, and what they are worth.**", "**Quieter sinks and their benefit.**"),
    ("**About 1 MHz, high source resistances: how the noise becomes an input current.**",
     "**About 1 MHz, high source resistances: the conversion of noise into an input current.**"),
    ("Where the reproductions and the data sheet's plot disagree, and why (Figure 14h and i):",
     "Differences between the reproductions and the data sheet's plot, and their causes (Figure 14h and i):"),
    ("**What it would do.**", "**Function.**"),
    ("**No latch, but a limit.**", "**Output limit, without latch-up.**"),
]

EDITS = GAIN + HEADINGS + LABELS


def main() -> None:
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    assert "\r" not in text
    if "#### 4.1.1 Roles of the two front ends" in text:
        sys.exit("already patched: refusing a second run")
    for e in EDITS:
        old, new = e[0], e[1]
        n = e[2] if len(e) > 2 else 1
        c = text.count(old)
        assert c == n, (c, n, old[:90])
        text = text.replace(old, new)
    print(f"{len(EDITS)} edits applied to {path.name} ({len(GAIN)} gain, {len(HEADINGS)} headings, {len(LABELS)} labels)")
    path.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
