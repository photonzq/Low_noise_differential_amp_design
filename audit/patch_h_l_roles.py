"""Patch of low_noise_preamp.md after patch_nf_map_5113.py (24 November 2026):

- Why the design has two front ends, H and L, and what each is for: a paragraph in the summary and a new
  Section 4.1.1 (every number from Tables 5, 9 and 10 and Sections 4.2.1, 4.4 and 6.2 as they stand).
- References to other documents that the build linked to the note's own sections, tables and equations (its
  linker leaves a reference as text after a possessive, "its" or "their"; "§" is not a keyword): Brookhaven's
  Eq. (3), the InterFET/NXP survey's Section 3.1, the LSK389 application note's Table 1 (twice), the commercial
  survey's Section 1.2, the LT3094's and LT3045's Table 4, and the NF 5307 manual's Sections 3.2.1 and 5.1 in the
  references.
- Table 2: the 5113's coupling as the table gives it for the others, "DC" for an input that reaches DC (the SR560,
  whose COUPLING pushbutton also selects AC at 0.03 Hz, manual PDF p. 12, and the 5113 both also offer AC coupling).
Every edit is an exact-string replacement whose old text occurs once.  A second run is refused.
Usage: python patch_h_l_roles.py <path to low_noise_preamp.md>
"""
from __future__ import annotations

import sys
from pathlib import Path

EDITS: list[tuple] = [
    # ---- the summary --------------------------------------------------------------------------------------------
    ("Between about 3 kΩ and 200 kΩ at 1 kHz the two differ by less than 1 %.\n\n",
     "Between about 3 kΩ and 200 kΩ at 1 kHz the two differ by less than 1 %.\n\n"
     "**Why two front ends.** No single input is the quietest for every source. Paralleling JFETs is the only way to "
     "lower the voltage noise, which dominates with low source resistances, but it raises the input capacitance and "
     "the current noise, which dominate with high ones (Sections 1.2–1.4). L spends capacitance (250 pF per input) "
     "and current (60 mA of JFET current per side) on the lowest voltage noise, and is meant for low source "
     "resistances and small signals (total gains from 200 up). H keeps 20 pF and the 100 MΩ input of the SR560 "
     "class, serves the low gains and the high-reserve mode, and is the general-purpose input (Section 4.1.1).\n\n"),
    # ---- Section 4.1.1 ---------------------------------------------------------------------------------------------
    ("\n\n### 4.2 The current-feedback JFET front end",
     "\n\n#### 4.1.1 Why two front ends, and what each is for\n\n"
     "An amplifier adds noise in two ways, and they call for opposite input stages (Section 1.3). Its voltage noise "
     "$e_n$ adds to the signal whatever the source, and it dominates with low source resistances. Its current noise "
     "$i_n$ and its input capacitance act through the source's impedance, as $i_nR_s$ and $e_n\\omega C_{in}R_s$ "
     "(Eq. (3)), and they dominate with high ones. Only paralleling JFETs lowers $e_n$, as $1/\\sqrt N$, and it raises "
     "$C_{in}$ as $N$ and the gate-leakage noise as $\\sqrt N$ (Eq. (2)): at a given input capacitance the lowest "
     "$e_n$ is set by the device's figure of merit (Eq. (6)), and the best number of devices falls as the source "
     "resistance rises (Eq. (4), Figure 1b). No single input stage is therefore the quietest for every source. The "
     "design has two, of the same topology, at the two ends of this trade, and a relay selects one:\n\n"
     "- **L, for low source resistances and small signals.** Twelve JFE150 per side give 0.42 nV/√Hz white, 0.43 "
     "at 1 kHz and 0.96 at 10 Hz (Table 9), 2.6 times lower than H's. The price is 288 pF of JFETs per input, a "
     "damping network that leaves 250 pF at the input (Section 4.4), 10 MΩ bias resistors, and 60 mA of JFET current "
     "per side against H's 10 mA (Table 5), with current sinks that dissipate 0.96 W per side against 0.17 W "
     "(Section 4.2.1). Its front end has a fixed gain of 201, so it serves total gains from 200 to 100 000. With low "
     "source resistances its noise figure is far lower: 3.2 against 9.3 dB with 10 Ω at 1 kHz and 0.45 against "
     "2.4 dB with 100 Ω (Table 10), and its low-resistance contours in Figure 14 lie 6.8 times lower in source "
     "resistance than H's. It is the quieter input below about 27–70 kΩ of source resistance from 10 Hz to 1 kHz, "
     "0.70 kΩ at 1 MHz and 96 Ω at 10 MHz (Section 6.2): 50 Ω instruments and lines, resistive bridges and strain "
     "gauges (commonly 120 Ω to 1 kΩ), thermocouples, coils and low-resistance samples, for example.\n"
     "- **H, the general-purpose input.** Two JFE2140 halves per side give 1.08 nV/√Hz white, 1.11 at 1 kHz and 2.8 "
     "at 10 Hz (Table 9), with 20 pF at the input (the bootstrap hides the JFETs' 26 pF; Section 4.4) and 100 MΩ "
     "bias resistors, whose 12.9 fA/√Hz put its high-resistance limit where the SR560's input resistors put the "
     "SR560's (Section 6.2). Its front end switches between gains of 10 and 100, so it serves total gains from 1 to "
     "50 000, and from 100 to 1000 in the high-reserve mode, with 20 dB more headroom at the input (Section 4.1). It "
     "is the input for sources above L's crossovers, up to its 100 MΩ, for sources that must not be loaded "
     "(high-resistance sensors and samples, capacitive and piezoelectric sensors, electrodes, for example) and for "
     "large signals.\n\n"
     "The wrong input costs most at the two ends and little in between. With 1 MΩ at 1 kHz, L's noise figure is "
     "0.41 dB against H's 0.04 dB, and at 1 MHz 21.4 against 10.9 dB (Table 10); with a 1 kΩ source, L's 250 pF "
     "already make a pole at 0.64 MHz, where H's 20 pF make it at 8.0 MHz. With 10 Ω, H gives up 6.1 dB at 1 kHz. "
     "Between about 3 kΩ and 200 kΩ at 1 kHz the two differ in noise by less than 1 % (Section 6.2), and either "
     "serves."
     "\n\n### 4.2 The current-feedback JFET front end"),
    # ---- references to other documents, left as text -----------------------------------------------------------------
    ("(also Brookhaven's ICFA95 slides, Eq. (3))", "(also Brookhaven's ICFA95 slides, their Eq. (3))"),
    ("`refs/datasheets/jfet/survey_InterFET_NXP_others.md` Section 3.1)",
     "`refs/datasheets/jfet/survey_InterFET_NXP_others.md`, §3.1)"),
    ("5.1 %; LSK389 application note, Table 1)", "5.1 %; the LSK389 application note's Table 1)"),
    ("(survey Section 1.2)", "(the survey's Section 1.2)"),
    ("Cordell Rev. A4, Table 1, p. 5)", "Cordell's Table 1, Rev. A4, p. 5)"),
    ("measured in Cordell's application note, Table 1, p. 5,", "measured in Cordell's application note, its Table 1, p. 5,"),
    ("(LT3094 Rev. 0, p. 3 and Table 4, p. 28; LT3045 Rev. D, p. 2 and Table 4, p. 22;",
     "(LT3094 Rev. 0, p. 3 and its Table 4, p. 28; LT3045 Rev. D, p. 2 and its Table 4, p. 22;"),
    ("D: 507571: Section 3.2.1 on PDF p. 21;", "D: 507571: §3.2.1 on PDF p. 21;"),
    ("PDF p. 37; Section 5.1, input specifications,", "PDF p. 37; §5.1, input specifications,"),
    # ---- Table 2 --------------------------------------------------------------------------------------------------
    ("| Signal Recovery 5113 | 4 | 25 | DC–1 MHz | AC or DC |", "| Signal Recovery 5113 | 4 | 25 | DC–1 MHz | DC |"),
]


def main() -> None:
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    assert "\r" not in text
    if "#### 4.1.1 Why two front ends" in text:
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
