"""Patch of low_noise_preamp.md after patch_nf_map_sources.py (24 November 2026): Section 6.2's list of where the
SR560 reproductions and the data sheet disagree, corrected after a check of the input capacitance
(scripts/sr560_nf_sources.py, sim/results/sr560_nf_sources.json; numbers from numbers_s6_7.py, group
"s6.2 Figure 14"):

- About 1 MHz: the list said the reproductions' noise current there was an e_n w C of their input capacitance,
  8.5 and 15.7 pF, smaller than the plot's 38 pF because the model has no connector, protection or wiring.  The
  check: their simulated input capacitance is 15.8 and 31.1 pF at 1 MHz, and it is not what makes the current.  A
  noise voltage in series with the driven gate gives none; JFET A's channel noise gives e_ch w (C_gs + C_gd) at its
  bias; the rest reaches the input through its own effective capacitances.  The 8.5 and 15.7 pF are what the plot's
  form would need, not a capacitance of the circuit.
- The tail servo: "the more with the LSK389B's larger capacitances" made precise: its noise current scales with the
  input capacitance (ratios 1.85, 1.88, 2.04 against 1.83, 1.80, 1.97).
- Section 8: the check script and its results.
Every edit is an exact-string replacement whose old text occurs once.  A second run is refused.
Usage: python patch_nf_map_capacitance.py <path to low_noise_preamp.md>
"""
from __future__ import annotations

import sys
from pathlib import Path

EDITS: list[tuple] = [
    # ---- the tail servo ----------------------------------------------------------------------------------------
    ("With input B grounded, gate A follows its source through the gate–source capacitance and gate B cannot, so "
     "the servo's noise appears across the pair, the more with the LSK389B's larger capacitances.",
     "With input B grounded, gate A follows the pair's internal nodes through its capacitances and gate B cannot, "
     "so the servo's noise appears across the pair in proportion to the input capacitance: the LSK389B model's "
     "servo noise current is 1.85, 1.88 and 2.04 times the NPD5564 model's at 10 kHz, 100 kHz and 1 MHz, and its "
     "input capacitance 1.83, 1.80 and 1.97 times (next item)."),
    # ---- about 1 MHz ---------------------------------------------------------------------------------------------
    ("- **About 1 MHz, high source resistances: the input capacitance.** Both reproductions are below the data "
     "sheet there: their noise current at 1 MHz is 0.37 and 0.74 pA/√Hz, against 0.86. Without the servo's share "
     "(79 and 82 % of the output noise with 1 MΩ), what is left is 0.17 and 0.32 pA/√Hz, an $e_n\\omega C$ with "
     "$C$ = 8.5 pF (NPD5564) and 15.7 pF (LSK389B), against the plot's 38 pF and the specified 25 pF: the model's "
     "inputs have no capacitance beyond the JFETs', no connector, protection or wiring.",
     "- **About 1 MHz, high source resistances: how the noise becomes an input current.** Both reproductions are "
     "below the data sheet there: their noise current at 1 MHz is 0.37 and 0.74 pA/√Hz, against 0.86. The data "
     "sheet's plot puts all of its $e_n$ behind one capacitance, $i_n = e_n\\omega C$ with $C$ = 38 pF. The "
     "reproductions' input capacitance, simulated at input A with input B grounded, is 15.8 and 31.1 pF at 1 MHz "
     "(3.7 and 6.8 pF at 1 kHz, where the front end's feedback hides most of the JFETs' capacitance), the LSK389B "
     "model's above the specified 25 pF; but it is not what turns their noise into an input current. Split by "
     "source (each noise generator of the 41 runs fitted like the total; `scripts/sr560_nf_sources.py`), a noise "
     "voltage in series with the driven gate, such as the gate resistor of JFET A's model, gives no current at all, "
     "since the source resistance and the input capacitance divide it exactly like the signal; JFET A's channel "
     "noise gives $e_{ch}\\omega C$ with $C$ = 9.55–9.56 and 25.14–25.15 pF from 10 kHz to 1 MHz, its own "
     "$C_{gs} + C_{gd}$ at its bias (5.84 + 3.72 = 9.56 pF and 18.41 + 6.79 = 25.20 pF from the model cards); and "
     "the noise of the grounded side, of U102 and of the rest of the circuit reaches input A through effective "
     "capacitances of 7.5–12.1 pF (NPD5564) and 12.5–24.7 pF (LSK389B). Without the servo's share (79 and 82 % of "
     "the output noise with 1 MΩ), the reproductions' noise current is thus 0.17 and 0.32 pA/√Hz, what the plot's "
     "form would give with 8.5 and 15.7 pF. A capacitance at the input terminal, ahead of every noise source, would "
     "turn the whole $e_n$ into current as the plot does; the model has none (no connector, protection or wiring), "
     "and the instrument's is not known."),
    # ---- Section 8 -----------------------------------------------------------------------------------------------
    ("| `scripts/nf_map.py`, `scripts/sr560_nf_datasheet.py` | Figure 14 and its numbers",
     "| `scripts/nf_map.py`, `scripts/sr560_nf_datasheet.py`, `scripts/sr560_nf_sources.py` | Figure 14 and its "
     "numbers"),
    ("with their two-port fit (`sr560_nf_datasheet.json`) |",
     "with their two-port fit (`sr560_nf_datasheet.json`); the SR560 models' input capacitance and their noise "
     "current by source (`sr560_nf_sources.json`) |"),
]


def main() -> None:
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    assert "\r" not in text
    if "how the noise becomes an input current" in text:
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
