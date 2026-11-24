"""Patch of low_noise_preamp.md for the SR560 models and the operating-point fallback (23 November 2026).

What changed: the SR560 reproduction is given in three models (scripts/sr560_variants.py): as drawn;
corrected (C406 = 82 pF added, C301 = 47 pF as the parts list gives it, every op amp with its data
sheet's open-loop gain and phase); and corrected with the LSK389B that a user found in a newer unit
(EEVblog forum, 18 March 2024), modelled by Linear Systems' updated LSK389 card (Rev 2, 18 May 2026)
calibrated to the LSK389 data sheet (Doc 201122 Rev A27).  The CMRR of the first version came from an
untrimmed chain: the second deck of the offset trim at a gain of 1000 had fallen back to ngspice's
transient operating point, which is not a DC solution, and the trim stayed at -4.7 mV instead of
1.55 V; the SR560 decks now tie their inputs through 1 ohm, start from a .nodeset or a converged
neighbour, and rerun a deck whose log shows the fallback (sr560_chain._op, spice.op_fallback).

Every new value is the quoted form of an entry of sim/results/numbers_s1_3.json or numbers_s6_7.json,
or of the results file the note names next to it (sr560_chain.json, sr560_frontend.json,
sr560_bw_check.json, sr560_variants.json, jfet_calibration.json), rounded as the note rounds it.
Every edit is an exact-string replacement whose old text occurs the stated number of times (once
unless given).  A second run is refused.
Usage: python patch_sr560.py <path to low_noise_preamp.md>
"""
from __future__ import annotations

import sys
from pathlib import Path

# (old, new) or (old, new, count)
EDITS: list[tuple] = [
    # ---- summary -------------------------------------------------------------------------------
    ("Against the SR560 reproduced in the same simulator (5.7 nV/√Hz at 1 kHz, 3.2 nV/√Hz white, −3 dB at "
     "0.73–0.79 MHz), H is $5.7/1.11$ = 5.1 times quieter at 1 kHz and L $5.7/0.43$ = 13.3 times (gain 1000), "
     "with $14.82/0.73$ = 20 times (H, gain 100) and $16.5/0.73$ = 23 times (L, gain 1000) the reproduced "
     "SR560's bandwidth at the same gain, and 15–17 times the 1 MHz of the SR560's manual",
     "Against the SR560 reproduced in the same simulator (Section 2.2), H is $3.23/1.11$ = 2.9 to $5.7/1.11$ = "
     "5.1 times quieter at 1 kHz and L $3.23/0.43$ = 7.5 to $5.7/0.43$ = 13.3 times (gain 1000): the "
     "reproduction gives 5.7 nV/√Hz at 1 kHz (3.2 nV/√Hz white) with the NPD5564 of the SR560's manual, and "
     "3.23 nV/√Hz (3.21 white) with the LSK389B that a user found in a newer unit. Its bandwidth, 0.73–0.79 MHz "
     "as drawn, becomes 1.04–1.17 MHz once C406 and C301 are set as the parts list gives them and the op amps "
     "get their data sheets' open-loop gain and phase. The new chain has $14.82/1.09$ to $14.82/1.04$ = 14 "
     "times (H, gain 100) and $16.5/1.09$ to $16.5/1.04$ = 15–16 times (L, gain 1000) the bandwidth of these "
     "corrected models at the same gain ($14.82/0.73$ = 20 and $16.5/0.73$ = 23 times that of the model as "
     "drawn), and 15–17 times the 1 MHz of the SR560's manual"),
    # ---- Section 2.2: the three models -------------------------------------------------------------
    ("reproduces the manual's table of noise against gain (Table 1).\n",
     "reproduces the manual's table of noise against gain (Table 1). Three models of it are compared "
     "(`scripts/sr560_variants.py`, `sim/results/sr560_variants.json`):\n\n"
     "- **As drawn**: the netlist as read from the schematics, with the behavioural op amps.\n"
     "- **Corrected**: the same netlist with C406 added and C301 at the parts list's 47 pF (both below), and "
     "every op amp with the open-loop gain and phase fitted to its data sheet's plots instead of the behavioural "
     "model's poles. Its noise is that of the model as drawn to within 0.2 % at every gain "
     "(`scripts/numbers_s1_3.py`); only its bandwidth differs.\n"
     "- **Corrected, with the LSK389B**: the corrected model with U106 an LSK389B, modelled by Linear Systems' "
     "updated LSK389B card calibrated to the LSK389 data sheet (Section 3.4, Table 4). The manual (Rev. 3.1, "
     "4/2023) lists the NPD5564 (PDF pp. 17, 21 and 43), but a user who opened two units of different serial "
     "numbers found the NPD5564 in the older and an LSK389B in the newer (EEVblog forum, 18 March 2024; a user "
     "report, not an SRS document).\n"),
    ("*Table 1. The SR560 reproduction against its manual: input noise at 1 kHz (nV/√Hz) in the low-noise and "
     "high-reserve modes. Manual: the table on printed p. 21. Model: `sim/results/sr560_chain.json`, with its "
     "white level (100 kHz) for the low-noise mode.*",
     "*Table 1. The SR560 reproduction against its manual: input noise at 1 kHz (nV/√Hz) in the low-noise and "
     "high-reserve modes, and the white level (100 kHz) in the low-noise mode. Manual: the table on printed "
     "p. 21. NPD5564: the model as drawn (`sim/results/sr560_chain.json`), whose noise the corrected model shares "
     "to within 0.2 %. LSK389B: the corrected model with the LSK389B (`sim/results/sr560_variants.json`).*"),
    ("| Low noise, model, 1 kHz | 52 | 36 | 17 | 11.5 | 9.9 | 9.4 | 5.7 |\n"
     "| Low noise, model, 100 kHz | 51 | 35 | 16 | 10.4 | 8.7 | 8.2 | 3.2 |\n",
     "| Low noise, NPD5564, 1 kHz | 52 | 36 | 17 | 11.5 | 9.9 | 9.4 | 5.7 |\n"
     "| Low noise, NPD5564, 100 kHz | 51 | 35 | 16 | 10.4 | 8.7 | 8.2 | 3.2 |\n"
     "| Low noise, LSK389B, 1 kHz | 52 | 36 | 16 | 10.3 | 8.6 | 8.0 | 3.2–3.3 |\n"
     "| Low noise, LSK389B, 100 kHz | 51 | 35 | 16 | 10.2 | 8.6 | 8.0 | 3.2–3.3 |\n"),
    ("| High reserve, model, 1 kHz | 35 | 25.5 | 22 | 19.9 | 16.6 | 16.4 | 9.4 | 9.4 |\n",
     "| High reserve, NPD5564, 1 kHz | 35 | 25.5 | 22 | 19.9 | 16.6 | 16.4 | 9.4 | 9.4 |\n"
     "| High reserve, LSK389B, 1 kHz | 35 | 25.0 | 21 | 19.3 | 15.9 | 15.6 | 8.0 | 8.0 |\n"),
    ("The model is within 30 % of the manual in 11 of the 15 columns",
     "With the NPD5564 the model is within 30 % of the manual in 11 of the 15 columns"),
    ("The benchmark comparison is therefore made at 1 kHz and in the white region.\n",
     "The benchmark comparison is therefore made at 1 kHz and in the white region.\n\n"
     "With the LSK389B the model is within 30 % of the manual in 12 of the 15 columns (the exceptions: the "
     "low-noise gain of 5, −35 %, and the high-reserve gains of 10, +39 %, and 1000, −46 %). From a gain of 100 "
     "up it gives 3.2–3.3 nV/√Hz at 1 kHz, 18–19 % below the manual's 4, and 5.2 nV/√Hz at 10 Hz (Figure 3b). "
     "The LSK389B removes the excess noise that the 2N5564 card carries at 1 kHz, which takes the JFETs' share "
     "at 1 kHz from 5.1 to 2.2 nV/√Hz, but not the floor: the white level, 3.21 nV/√Hz, is within 1 % of the "
     "NPD5564 model's 3.18, which the resistors and the single pair set in both (Section 2.3). The user's two "
     "units, after the manual's CMRR and offset adjustments, gave about 4.0 nV/√Hz at 1 kHz and a gain of 1000 "
     "with the NPD5564 and about 3.5 with the LSK389B (measured with an Audio Precision APx515; EEVblog forum, "
     "18 March 2024). The LSK389B model is 7.6 % below the second; the NPD5564 model is 43 % above the first, as "
     "it is above the manual. These are single measurements of two units by one user; they suggest that the "
     "LSK389B model is close and that the NPD5564 model overstates the noise at 1 kHz, as the comparison with "
     "the manual suggests too.\n"),
    # ---- Section 2.2: the front end ------------------------------------------------------------------
    ("Its −3 dB bandwidth is 2.44 MHz, and the CMRR with ideal matching is 102.6 dB at 1 kHz "
     "(`sim/results/sr560_frontend.json`).",
     "Its −3 dB bandwidth is 2.44 MHz (2.48 MHz with the OP37's and LF411's data-sheet dynamics), and the CMRR "
     "with ideal matching is 102.6 dB at 1 kHz with the offset trim at 0 V (`sim/results/sr560_frontend.json`; "
     "on the trim, below). With the LSK389B the JFETs contribute 2.2 nV/√Hz, 1.55 per device. That is 4.7 % "
     "below the 1.62 nV/√Hz of the card's calibration point (1 kHz, 2 mA, 10 V), about as Cordell's LSK389 "
     "measurements fall from 2 to 4 mA (1.17 to 1.11 nV/√Hz, 5.1 %; LSK389 application note, Table 1), because "
     "the calibration puts most of the white noise in the gate resistor RX (106 Ω, 1.33 nV/√Hz by itself; "
     "Section 3.4). The LSK389B's larger transconductance at the SR560's 4.5 mA, 21.3 against 13.1 mS (its data "
     "sheet's Fig. 17 shows about 20.5 mS at 5 mA for the B grade, read by eye), refers the drain loads "
     "(1.2 nV/√Hz) and the OP37 (0.9) to the input with 0.84 times the weight they have with the NPD5564, as "
     "the two sides' effective transconductances $g_m/(1 + g_m R_{113})$ predict, and R113 + R114 (1.7 nV/√Hz) "
     "become the second-largest term. That front end gives 3.23 nV/√Hz at 1 kHz, −3 dB at 3.12 MHz and a CMRR "
     "of 104.6 dB at 1 kHz, also with the trim at 0 V (`sim/results/sr560_variants.json`, "
     "`scripts/numbers_s1_3.py`)."),
    # ---- Section 2.2: bandwidth and CMRR -------------------------------------------------------------
    ("The chain's −3 dB bandwidth is 0.73–0.79 MHz at every gain (Figure 3c)",
     "The chain's −3 dB bandwidth as drawn is 0.73–0.79 MHz at every gain (Figure 3c)"),
    ("With C406 added and C301 at 47 pF, the data-sheet op amps give 1.04–1.16 MHz; R422 changes U402's gain, "
     "which the vernier's calibration absorbs, not the bandwidth. The CMRR of the reproduced chain with ideal "
     "matching is 105, 102.5, 86.5, 67.7 and 61.6 dB at 10 Hz, 1 kHz, 10 kHz, 100 kHz and 1 MHz "
     "(`sim/results/sr560_chain.json`), against a specification falling at 6 dB per octave above 1 kHz from more "
     "than 90 dB in the manual (printed p. 5) or from 100 dB in the data sheet (p. 3, at a gain of 100 in the "
     "low-noise mode).",
     "With C406 added and C301 at 47 pF, the data-sheet op amps give 1.04–1.16 MHz: the corrected model "
     "(Figure 3c, Table 11). R422 changes U402's gain, which the vernier's calibration absorbs, not the bandwidth, "
     "and is left out. With the LSK389B the corrected model reaches 1.07–1.17 MHz.\n\n"
     "The CMRR of the reproduced chain with ideal matching, at a gain of 1000 with the offset trimmed as the "
     "manual's procedure does, is 150.3, 110.4, 90.4, 71.6 and 65.6 dB at 10 Hz, 1 kHz, 10 kHz, 100 kHz and "
     "1 MHz as drawn (`sim/results/sr560_chain.json`; the corrected model is within 0.5 dB of these, and the "
     "model with the LSK389B 1.2–1.6 dB above them, Table 12), against a specification falling at 6 dB per "
     "octave above 1 kHz from more than 90 dB in the manual (printed p. 5) or from 100 dB in the data sheet "
     "(p. 3, at a gain of 100 in the low-noise mode). With ideal matching, the CMRR depends on the offset trim. "
     "P103's wiper feeds drain A through R121 (75 kΩ), while R120 (100 kΩ) loads drain B to ground, and the "
     "servo holds both drains at 6.2 V, so the trim sets how the tail current divides between the two JFETs. "
     "At 0 V, 6.2 V/(75 kΩ) − 6.2 V/(100 kΩ) = 20.7 µA more flows into R121 than into R120, so JFET A carries "
     "0.46 % less current than JFET B and its $g_m$ is 0.23 % lower; nulling the output offset puts the wiper at "
     "6.2 V × (1 − 75/100) = 1.55 V, where the two currents are equal. Untrimmed, the chain's CMRR is 105.0, "
     "102.6, 86.5, 67.7 and 61.7 dB, which matches the front end's 102.6 dB at 1 kHz with the trim at 0 V; "
     "trimmed, it is 7.9 dB higher at 1 kHz (`sim/results/sr560_variants.json`, `check_cmrr_trim`). The first "
     "version of this note quoted those untrimmed figures, to within 0.03 dB, as the trimmed ones: the second "
     "of the trim's two operating points had silently come from ngspice's transient fallback, a state that is "
     "not a DC solution, and the trim had stayed at −4.7 mV instead of 1.55 V (Appendix)."),
    ("*Figure 3. The benchmark. (a) Input noise at 1 kHz against gain: the SR560's manual (circles), its "
     "reproduction at 1 kHz and 100 kHz, and the new design's H and L inputs. (b) Input noise spectra at a gain "
     "of 1000, with the SR560 manual's typical curve (printed p. 20, read by eye). (c) Frequency response at a "
     "gain of 100 (SR560 and H) and 1000 (L), normalised at 1 kHz.*",
     "*Figure 3. The benchmark. (a) Input noise at 1 kHz against gain: the SR560's manual (circles), its "
     "reproduction as drawn at 1 kHz and 100 kHz (the corrected model's noise is the same to within 0.2 %), the "
     "corrected model with the LSK389B at 1 kHz, and the new design's H and L inputs. (b) Input noise spectra at "
     "a gain of 1000, with the SR560 manual's typical curve (printed p. 20, read by eye). (c) Frequency response "
     "at a gain of 100 (SR560 and H) and 1000 (L), normalised at 1 kHz: the SR560 as drawn, corrected (dashed, "
     "over the curve of the model with the LSK389B) and with the LSK389B.*"),
    # ---- Section 2.3 ---------------------------------------------------------------------------------
    ("by Eq. (2) and the data sheets' 0.9 and 0.8 nV/√Hz at 5 mA (Table 3; `scripts/noise_theory.py`).\n",
     "by Eq. (2) and the data sheets' 0.9 and 0.8 nV/√Hz at 5 mA (Table 3; `scripts/noise_theory.py`). The "
     "LSK389B of newer units does not lower the SR560's white floor (Section 2.2): 3.21 against 3.18 nV/√Hz.\n"),
    # ---- Section 3.4, Table 4 ------------------------------------------------------------------------
    ("Vishay's 1 and 10 mA curves, 70254 Rev. E p. 5); $C_{iss}$ 10, $C_{rss}$ 2.5 pF at 15 V (p. 2) |\n",
     "Vishay's 1 and 10 mA curves, 70254 Rev. E p. 5); $C_{iss}$ 10, $C_{rss}$ 2.5 pF at 15 V (p. 2) |\n"
     "| LSK389B | Linear Systems, updated LSK389 card, Rev 2 (18 May 2026), B grade | 106.3 | 8.2e-18 → 8.02e-18 | "
     "19.5 / 5.5 → 20.7 / 18.2 | 1.6 / 3.2 nV at 1 kHz / 10 Hz, 2 mA, 10 V (LSK389 data sheet, Doc 201122 "
     "Rev A27, p. 2); $C_{iss}$ 25 pF at 10 V, $C_{rss}$ 5.5 pF at $V_{DG}$ = 10 V; for the SR560 model of "
     "Section 2.2 only |\n"),
    # ---- Section 5.1 ---------------------------------------------------------------------------------
    ("so the solution was apparently taken from a transient with the bootstrap capacitors still uncharged.",
     "so the solution was taken from a transient with the bootstrap capacitors still uncharged: the deck's log "
     "shows that ngspice's gmin and source stepping had failed and that it had fallen back to its transient "
     "operating point (Appendix)."),
    # ---- Section 5.2 ---------------------------------------------------------------------------------
    ("Linear Systems' LSBF862 (Rev 2, 2026) and the Linear Systems cards of LTspice's `standard.jft`",
     "Linear Systems' LSBF862 (Rev 2, 2026) and updated LSK389 (B grade, Rev 2, 2026; for the SR560 model with "
     "the LSK389B, Section 2.2) cards, and the Linear Systems cards of LTspice's `standard.jft`"),
    ("gain-bandwidth, slew rate and output limits: OP37, LF411, LT1028, LF356.\n",
     "gain-bandwidth, slew rate and output limits: OP37, LF411, LT1028, LF356; in its corrected models, with "
     "the open-loop gain and phase fitted to their data sheets' plots (`scripts/sr560_bw_check.py`; "
     "Section 2.2).\n"),
    # ---- Section 6.1 ---------------------------------------------------------------------------------
    ("and 1.1 against 5.7 from 1000 up. In the high-reserve mode,",
     "and 1.1 against 5.7 from 1000 up (52, 10.3, 3.3 and 3.2 for the SR560 with the LSK389B). In the "
     "high-reserve mode,"),
    ("against the SR560's 9.4–20 at 1 kHz.",
     "against the SR560's 9.4–20 at 1 kHz (8.0–19.3 with the LSK389B)."),
    # ---- Section 6.3, Table 11 ------------------------------------------------------------------------
    ("the SR560 row from `scripts/sr560_chain.py`, `sim/results/sr560_chain.json`, its peaking from "
     "`sr560_chain_ac_*.npz` by `scripts/numbers_s6_7.py`)",
     "the SR560 rows from `scripts/sr560_chain.py` (`sim/results/sr560_chain.json`; its peaking from "
     "`sr560_chain_ac_*.npz` by `scripts/numbers_s6_7.py`) and `scripts/sr560_variants.py` "
     "(`sim/results/sr560_variants.json`); Section 2.2)"),
    ("| SR560 reproduction | 1 – 50 000 | 0.73–0.79 MHz | −4.2 to −4.8 dB | – | none |\n",
     "| SR560 reproduction, as drawn | 1 – 50 000 | 0.73–0.79 MHz | −4.2 to −4.8 dB | – | none |\n"
     "| SR560, corrected | 1 – 50 000 | 1.04–1.16 MHz | −2.4 to −2.8 dB | – | none |\n"
     "| SR560, corrected, LSK389B | 1 – 50 000 | 1.07–1.17 MHz | −2.3 to −2.7 dB | – | none |\n"),
    # ---- Section 6.4, Table 12 and Figure 15 ------------------------------------------------------------
    ("The SR560 reproduction's row is from `scripts/sr560_chain.py` (`sim/results/sr560_chain.json`, ideal "
     "matching).",
     "The SR560 rows are from `scripts/sr560_chain.py` and `scripts/sr560_variants.py` "
     "(`sim/results/sr560_chain.json`, `sr560_variants.json`), with ideal matching and the offset trimmed "
     "(Section 2.2)."),
    ("| SR560 reproduction, ideal matching | 105 | 102.5 | 86.5 | 67.7 | 61.6 | – |\n",
     "| SR560 as drawn, ideal matching | 150.3 | 110.4 | 90.4 | 71.6 | 65.6 | – |\n"
     "| SR560 corrected, ideal matching | 150.3 | 110.4 | 90.4 | 71.6 | 66.1 | – |\n"
     "| SR560 corrected with LSK389B, ideal matching | 151.9 | 112.0 | 92.0 | 73.0 | 67.3 | – |\n"),
    ("against the SR560 (reproduction and specification) and the NF 5307's plot",
     "against the SR560 (its reproduction as drawn, with ideal matching and the offset trimmed, and its "
     "specification) and the NF 5307's plot"),
    # ---- Section 6.6, Table 15 ------------------------------------------------------------------------
    ("This design: Tables 9, 11 and 12; input capacitance $C_P + C_Z$ (`protection.json`).*",
     "SR560 reproduction: Section 2.2 and Tables 1, 11 and 12 (NPD5564: the model as drawn; LSK389B: the "
     "corrected model with it; bandwidth: as drawn and corrected). This design: Tables 9, 11 and 12; input "
     "capacitance $C_P + C_Z$ (`protection.json`).*"),
    ("| Input noise, white / 1 kHz, gain ≥ 1000 | 4 (1 kHz) | 3.2 / 5.7 |",
     "| Input noise, white / 1 kHz, gain ≥ 1000 | 4 (1 kHz) | 3.2 / 5.7 (NPD5564); 3.2 / 3.2 (LSK389B) |"),
    ("| Input noise at 10 Hz, gain ≥ 1000 | ≈ 11 (typical curve) | 48 (model's 1/f overstated) |",
     "| Input noise at 10 Hz, gain ≥ 1000 | ≈ 11 (typical curve) | 48 (NPD5564, its card's 1/f overstated); "
     "5.2 (LSK389B) |"),
    ("| Input noise at gain 10 | 13 | 11.5 |",
     "| Input noise at gain 10 | 13 | 11.5 (NPD5564); 10.3 (LSK389B) |"),
    ("| Bandwidth (−3 dB) | 1 MHz (1.2 MHz typ., data sheet) | 0.73–0.79 MHz |",
     "| Bandwidth (−3 dB) | 1 MHz (1.2 MHz typ., data sheet) | 0.73–0.79 MHz as drawn; 1.04–1.17 MHz "
     "corrected |"),
    ("| 102.5 / 61.6 dB (matched) |",
     "| 110.4 / 65.6 dB (matched, trimmed; 112.0 / 67.3 with LSK389B) |"),
    # ---- Appendix ------------------------------------------------------------------------------------
    ("AC and noise runs were unaffected, but transients stopped with \"timestep too small\" at the gate nodes. "
     "Transients use 1 Ω (or the real source) and abstol = 1e-12 A.\n",
     "AC and noise runs of the new design were unaffected, but transients stopped with \"timestep too small\" at "
     "the gate nodes. Transients use 1 Ω (or the real source) and abstol = 1e-12 A. In the SR560 reproduction "
     "the same resistors made some operating points fail (next item); its decks now use 1 Ω.\n"
     "- **An operating point that is not one.** When gmin stepping and source stepping both fail, ngspice-46 "
     "falls back to a transient operating point: by default a transient of 10 µs at 10 ns steps, whose end is "
     "used as the operating point of the AC, noise or transient analysis that follows (ngspice-46 User's "
     "Manual, Section 11.3.5, pp. 327–328). The log records it only as two notes, \"Transient op started\" and "
     "\"Transient op finished successfully\", and the end state need not be a DC solution: in a circuit whose "
     "capacitors take longer than 10 µs to charge, it is not. In the SR560 reproduction, the second deck of the "
     "offset trim at a gain of 1000 (VTRIM = 1 V) ended with the reference node at 0.94 V, although the 6.2 V "
     "zener feeds it through R125 with no DC load (R125 and C112 have a time constant of 5.0 ms), the node that "
     "feeds the drain loads at 1.39 V instead of 8.49 V (R119 and C113: 0.36 ms), and the front end's output at "
     "−8.0 V instead of −13 mV (`sim/results/sr560_variants.json`, "
     "`check_operating_point`). The same deck converges to the DC solution with its inputs tied through 1 Ω "
     "instead of 1 mΩ, with abstol = 1e-12 A instead of 1e-15 A, from a `.nodeset` near the solution, or from "
     "the fallback's own end state; every start that converges gives the same solution. The trim then "
     "interpolated between the true output at 0 V and the false one at 1 V and set VTRIM to −4.7 mV instead of "
     "1.55 V: the chain stayed untrimmed, and the first version of this note gave its CMRR (105, 102.5, 86.5, "
     "67.7 and 61.6 dB from 10 Hz to 1 MHz) as the trimmed chain's (150.3, 110.4, 90.4, 71.6 and 65.6 dB; "
     "Section 2.2). The SR560 decks now tie the inputs through 1 Ω, start from a `.nodeset` (`NODESET` in "
     "`scripts/sr560_frontend.py`) or from the solution of the previous converged deck, and are rerun from the "
     "next starting point whenever the log shows the fallback; a deck that falls back from every start stops "
     "the run with an error (`_op` in `scripts/sr560_chain.py`, `op_fallback` in `scripts/spice.py`). "
     "`scripts/export_netlists.py` checks its netlists the same way. The wrong operating point of Section 5.1's "
     "gain-30 variant is the same fallback.\n"),
    # ---- Section 8, Files -----------------------------------------------------------------------------
    ("| `scripts/sr560_frontend.py`, `scripts/sr560_chain.py`, `scripts/sr560_bw_check.py` | the SR560 "
     "reproduction of Section 2 (`sr560_frontend.json`, `sr560_chain.json`), and what sets its bandwidth: each "
     "op amp faster or ideal, or fitted to its data sheet's open-loop curves, and the netlist's departures from "
     "the schematics (`sr560_bw_check.json`) |",
     "| `scripts/sr560_frontend.py`, `scripts/sr560_chain.py`, `scripts/sr560_bw_check.py`, "
     "`scripts/sr560_variants.py` | the SR560 reproduction of Section 2 (`sr560_frontend.json`, "
     "`sr560_chain.json`); what sets its bandwidth: each op amp faster or ideal, or fitted to its data sheet's "
     "open-loop curves, and the netlist's departures from the schematics (`sr560_bw_check.json`); the corrected "
     "model and the model with the LSK389B, and the checks of the operating point and of the CMRR against the "
     "offset trim (`sr560_variants.json`) |"),
    ("| `refs/` | the SR560's manual and data sheet (`benchmark/`),",
     "| `refs/` | the SR560's manual and data sheet and the forum report on its JFETs (`benchmark/`),"),
    # ---- References -----------------------------------------------------------------------------------
    ("and the SR560 data sheet.\n- NF Corporation, 5307 differential amplifier:",
     "and the SR560 data sheet.\n"
     "- EEVblog Electronics Community Forum, \"SR560 Low noise amp -- Noise Calculation\", thread opened by the "
     "user sky2city on 18 March 2024, https://www.eevblog.com/forum/testgear/sr560_noise-calculation/ (saved "
     "on 23 November 2026, `refs/benchmark/`): the front-end JFETs of two SR560s (the NPD5564 in the older, an "
     "LSK389B in the newer) and their noise at 1 kHz and a gain of 1000, measured after the manual's CMRR and "
     "offset adjustments; a user report, not an SRS document.\n"
     "- NF Corporation, 5307 differential amplifier:"),
    ("Linear Systems LSBF862 Rev 2 (9 February 2026) and the Linear Systems cards in LTspice's `standard.jft`",
     "Linear Systems LSBF862 Rev 2 (9 February 2026), Linear Systems' updated LSK389 A/B/C/D card, Rev 2 "
     "(18 May 2026), and the Linear Systems cards in LTspice's `standard.jft`"),
    ("§7.4.4 (the JFET level 1 model), pp. 152–154",
     "§7.4.4 (the JFET level 1 model), pp. 152–154, and §11.3.5 (the operating point and its transient "
     "fallback), pp. 327–328"),
]


def main() -> None:
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    assert "\r" not in text
    if "Three models of it are compared" in text:
        sys.exit("already patched: refusing a second run")
    for e in EDITS:
        old, new = e[0], e[1]
        n = e[2] if len(e) > 2 else 1
        c = text.count(old)
        assert c == n, (c, n, old[:90])
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"{len(EDITS)} replacements applied to {path.name}")


if __name__ == "__main__":
    main()
