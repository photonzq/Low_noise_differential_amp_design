"""Patch for Sections 4.4-5 of low_noise_preamp.md (lines 584-767 of the note as audited on
21 November 2026: from the heading "### 4.4 The input: ..." up to, not including, "## 6. Results").

Every replacement is an exact string, guarded by assert s.count(old) == 1 within that block; the
rest of the note is left byte for byte as it is.  The numbers come from ../sim/results/ (the JSON
named next to them) and from scripts/numbers_s4b_5.py (numbers_s4b_5.json).

Usage: python patch_s4b_5.py <path to low_noise_preamp.md>
"""
from __future__ import annotations

import sys
from pathlib import Path

START = "### 4.4 The input: bootstrapping, negative conductance and damping\n"
END = "## 6. Results\n"

REPL: list[tuple[str, str]] = [
    # ---- 4.4: bare input capacitance (line 586)
    (r"""The effective input capacitance of the bare H front end, $\mathrm{Im}(Y_{in})/\omega$, is 0.05 pF between 1 kHz and 1 MHz, against the JFETs' own 26 pF; L's is 0.33 pF against 288 pF (Figure 10a). Below about 300 Hz it rises toward $C_{gd}$, because $C_{BS}$ no longer holds the cascode's gate to the source; above a few MHz it rises as the loop gain falls.""",
     r"""The effective input capacitance of the bare H front end, $\mathrm{Im}(Y_{in})/\omega$ with the other input grounded, is 0.050–0.057 pF from 1 kHz to 300 kHz (0.11 pF at 1 MHz), against the JFETs' own $NC_{iss}$ = 2 × 13 = 26 pF (SLPS730B §6.5, p. 5); L's is 0.33–0.39 pF (0.99 pF at 1 MHz) against 12 × 24 = 288 pF (SLPS732B §6.5, p. 5) (Figure 10a, `zin_numbers.json`). Below 355 Hz it rises above twice its minimum, toward $C_{gd}$, because $C_{BS}$ no longer holds the cascode's gate to the source; above 0.89 MHz (H) and 0.71 MHz (L) it does so as the loop gain falls (`protection.json`)."""),
    # ---- 4.4: negative parallel resistance (line 595)
    (r"""which falls as $1/f^2$ in resistance (Figure 10b): −1.1 kΩ at its minimum near 13 MHz for H and −110 Ω for L.""",
     r"""which falls as $1/f^2$ in resistance (Figure 10b): to −1.05 kΩ at its smallest, at 12.6 MHz, for H and to −110 Ω at 15.8 MHz for L (on the simulated grid, `zin_numbers.json`)."""),
    (r"""and a 1 kΩ source by 16 dB at 2.6 MHz on L (Figure 10c).""",
     r"""and a 1 kΩ source by 16 dB at 2.6 MHz on L (Figure 10c, `zin_numbers.json`)."""),
    # ---- 4.4: the input network (line 597)
    (r"""The input network supplies enough positive conductance where it is needed. A series $R_Z$ + $C_Z$ to ground has $\mathrm{Re}\,Y = \omega^2C_Z^2R_Z/(1+\omega^2C_Z^2R_Z^2)$, rising as $f^2$ like Eq. (11), and its thermal noise is shorted by $C_Z$ at low frequencies. With $R_Z$ = 2.2 kΩ and $C_Z$ = 10 pF (H) and 47 Ω with 220 pF (L), and the connector's and relay's $C_P$ of 10 and 30 pF, no source from 50 Ω to 1 MΩ peaks by more than 0.6 dB (Figure 10c). The network then dominates the input capacitance: about 20 pF for H and 250 pF for L, against 25 pF for the SR560 and 35 pF for the NF 5307.""",
     r"""The input network damps these poles. A series $R_Z$ + $C_Z$ to ground has $\mathrm{Re}\,Y = \omega^2C_Z^2R_Z/(1+\omega^2C_Z^2R_Z^2)$, rising as $f^2$ like Eq. (11) up to $1/R_Z$, and its thermal noise is shorted by $C_Z$ at low frequencies. The values are $R_Z$ = 2.2 kΩ and $C_Z$ = 10 pF (H) and 47 Ω with 220 pF (L), with a $C_P$ of 10 and 30 pF for the connector, the relay and the protection (an assumed allowance, not from data sheets). L's input conductance is then positive at every frequency, but H's is not: the network's conductance, 0.34 mS at 12.6 MHz and at most $1/R_Z$ = 0.45 mS, cancels only part of the bare front end's −0.95 mS there, and H's input conductance stays negative from 0.14 to 25 MHz, with −1.64 kΩ at 12.6 MHz (`zin_numbers.json`, `scripts/numbers_s4b_5.py`). The responses stay flat all the same, with the network's capacitance now dominating the input: none of the three sources simulated, 50 Ω, 1 kΩ and 1 MΩ, peaks by more than 0.57 dB (H, 1 kΩ, at 5.0 MHz; Figure 10c). The input capacitance is then $C_P + C_Z$, 20 pF for H and 250 pF for L below $1/(2\pi R_ZC_Z)$ = 7.2 and 15 MHz (simulated: 20.0 and 250.3 pF at 100 kHz), against 25 pF for the SR560 (manual Rev. 3.1, p. 5) and less than 35 pF for the NF 5307 (operation manual, §5.1, p. 31)."""),
    # ---- Figure 10 caption (line 601)
    (r"""*Figure 10. (a) Effective input capacitance of the bare front ends, against the JFETs' own capacitance. (b) The negative parallel resistance from the bootstrap's phase lag, Eq. (11). (c) Response from a 1 MΩ and a 1 kΩ source (H) and a 50 Ω source (L), without (dashed) and with the input network.*""",
     r"""*Figure 10. (a) Effective input capacitance of the bare front ends (the other input grounded), against the JFETs' own capacitance $NC_{iss}$, 2 × 13 pF (H) and 12 × 24 pF (L) (SLPS730B and SLPS732B §6.5, p. 5). (b) The negative parallel resistance from the bootstrap's phase lag, Eq. (11). (c) Response from a 1 MΩ and a 1 kΩ source (H) and from a 50 Ω and a 1 kΩ source (L), without (dashed) and with the input network (`scripts/collect_curves.py`, `curves_zin.npz`, `curves_sources.npz`; numbers in `zin_numbers.json`).*"""),
    # ---- protection (lines 605-635)
    (r"""Table 6d gives the numbers, with the input capacitance of the input networks (about 20 pF for H, 250 pF for L).""",
     r"""Table 6d gives the numbers, with the input capacitance of the input networks, $C_P + C_Z$ (20 pF for H, 250 pF for L)."""),
    (r"""*Table 6d. A series protection resistor in each input (closed forms; noise added in quadrature to the simulated white floors of 1.08 and 0.42 nV/√Hz; the noise figure for H with a 1 kΩ source).*""",
     r"""*Table 6d. A series protection resistor in each input (closed forms, `scripts/protection.py`, `protection.json`: $\sqrt{2\cdot 4kTR_s}$ added in quadrature to the chain's simulated white floors at a total gain of 1000, 1.08 and 0.42 nV/√Hz, from `chain_noise.json`; the poles $1/(2\pi R_sC_{in})$; the noise figure for H with a 1 kΩ source).*"""),
    (r"""For L that is intended, since its sources are below 300 Ω.""",
     r"""For L that is intended, since L is meant for low source resistances: it is the quieter input only below about 95 Ω at 10 MHz, 0.70 kΩ at 1 MHz and 27–71 kΩ at 1 kHz and 10 Hz, where the two inputs' noise curves cross (Section 6.2; `noise_vs_source.json`, `scripts/numbers_s4b_5.py`)."""),
    (r"""For H, whose sources are 300 Ω and up, 10–22 Ω costs 13–28 % of the floor""",
     r"""For H, the quieter input above its crossovers with L (Section 6.2), 10–22 Ω costs 13–27 % of the floor"""),
    (r"""A clamp diode adds its junction capacitance to $C_P$: 1–3 pF for small-signal low-leakage diodes, a few nanofarads for TVS diodes.""",
     r"""A clamp diode adds its junction capacitance to $C_P$: of the order of 1–3 pF for small-signal low-leakage diodes and a few nanofarads for TVS diodes (orders of magnitude assumed here; no diode data sheet was read)."""),
    (r"""It also adds an offset $I_LR_S$ that doubles every 10 °C. H's own current noise is set by its 100 MΩ bias resistor, 12.9 fA/√Hz, so leakage below about 100 pA costs nothing measurable.""",
     r"""It also adds an offset $I_LR_S$ that typically doubles every 10 °C (Hill and Horowitz 2020, §2x.1, p. 102). H's own current noise is set by its 100 MΩ bias resistor, 12.9 fA/√Hz: a leakage of 10 pA adds 1 % to it and 100 pA adds 9 % (`protection.json`)."""),
    (r"""(Eqs. (8c) and (9b)). Above +3.7 V the cascodes run out of headroom""",
     r"""(Eqs. (8c) and (9b); `protection.json`). Above +3.7 V (H) or +3.6 V (L) the cascodes run out of headroom"""),
    (r"""enough that the standing $|V_{GS}|$ leaves each of them below about 0.2 V of forward bias.""",
     r"""enough that the standing $|V_{GS}|$ leaves each of them below about 0.2 V of forward bias, a margin chosen here: two diodes take 0.18 V each for H and three take 0.19 V for L (`protection.json`)."""),
    # ---- 4.5: Figure 11 caption (line 649)
    (r"""drawn for the H front end at a total gain of 1000 with""",
     r"""drawn for the H front end at a total gain of 5000 ($G_{FE}$ = 100, $a_3 = a_4$ = 1/2 and $a_5$ = 2/5 in Eq. (7)) with"""),
    # ---- 4.5: S2 (line 651)
    (r"""An LM7171 (A grade, 4100 V/µs, 200 MHz) with four 499 Ω resistors from one 0.01 % network. The LM7171 was chosen over the lower-noise THS4031 after the distortion comparison of Section 6.4: at a total gain of 100, where S2 carries the full output level, the THS4031 gave 1.3 % distortion at 10 MHz and 1 Vpp against 0.012 % for the LM7171, and it limited the 10 V step to 133 V/µs.""",
     r"""An LM7171 (A grade: 4100 V/µs and a unity-gain bandwidth of 160 MHz, SNOS760D §5.5, p. 5; it is not unity-gain stable but stable at gains of +2 or more, p. 1, which the difference amplifier's noise gain of 1 + 499/499 = 2 meets) with four 499 Ω resistors from one 0.01 % network. The LM7171 was chosen over the lower-noise THS4031 after the distortion comparison of Section 6.5 (Table 14): at a total gain of 100, where S2 carries the full output level, the THS4031 gave 1.3 % distortion at 10 MHz and 1 Vpp against 0.012 % for the LM7171 (`da_compare.json`), and it limited the 10 V step to 133 V/µs (`large_signal_THS4031.json`)."""),
    # ---- 4.5: F1, F2, S3, S4, S5 (lines 652-654)
    (r"""with 20 pF of relay and layout capacitance at the filter node and a THS4031 follower""",
     r"""with 20 pF of relay and layout capacitance at the filter node (an assumed allowance) and a THS4031 follower"""),
    (r"""A 249 Ω attenuator tapped through a 1 Ω switch, then a THS4021 at a gain of 10 (220 Ω and 24.4 Ω).""",
     r"""A 249 Ω attenuator tapped through a switch, simulated as 1 Ω, then a THS4021 at a gain of 10 (220 Ω and 24.4 Ω). The switch is idealised: a TMUX6219, for example, has 2.1 Ω typical and 148 pF on (SCDS420E §5.6–5.7, pp. 6–7), and no switch capacitance is simulated."""),
    (r"""49.9 Ω to the output, ±10 V into a high impedance and ±5 V into 50 Ω.""",
     r"""49.9 Ω to the output, ±10 V into a high impedance and ±5 V into 50 Ω. The latter needs ±10 V and 100 mA at the THS3091, which swings at least ±12.1 V into 100 Ω and drives at least 200 mA at ±15 V (SLOS423K §7.5, p. 7); only a 1 MΩ load was simulated."""),
    # ---- 4.5: the output stage's current noise (line 656)
    (r"""At the lowest gains the THS3091's inverting-input current noise in its 1 kΩ feedback resistor, 14 pA/√Hz white and about 200 pA/√Hz at 10 Hz, dominates: 24.6 nV/√Hz white and 650 nV/√Hz at 1 Hz at a total gain of 1.""",
     r"""At the lowest gains the THS3091's inverting-input current noise in its 1 kΩ feedback resistor matters: 14 pA/√Hz white (SLOS423K §7.5, p. 6) and about 200 pA/√Hz at 10 Hz (Fig. 7-16, p. 12) give 14 nV/√Hz and, with the 1/f continued below 10 Hz as in the corrected model, about 630 nV/√Hz at 1 Hz. At a total gain of 1 the chain has 24.6 nV/√Hz white and 650 nV/√Hz at 1 Hz (`chain_noise.json`), so this term is a third of the white noise power and 94 % of it at 1 Hz (`scripts/numbers_s4b_5.py`)."""),
    # ---- 4.6: offset and the Monte Carlo's JFET mismatch (line 660)
    (r"""The front end amplifies the difference of the two sides' $V_{GS}$ by its gain. For H, the JFE2140's halves match to 4 mV at most (10 µV/°C), and the Monte Carlo of Section 6.3, with 0.85 mV of $V_{TO}$ and 1 % of $\beta$ mismatch within a dual, gives an output offset of 3.4 V rms at a total gain of 1000, i.e. 3.4 mV at the input. For L, unsorted JFE150 do not work. With the 85 mV spread of $V_{TO}$ that the data sheet's $V_{GS(off)}$ range implies, the two sides' mean $V_{GS}$ differ by about 35 mV rms, the gain of 201 drives the chain into saturation, and in one trial of the first Monte Carlo ngspice found no DC solution at all. The 24 JFE150 must come from one $V_{GS}$ bin (±5 mV at 5 mA), which leaves 2.3 V rms of offset at a gain of 1000 (2.3 mV at the input).""",
     r"""The front end amplifies the difference of the two sides' $V_{GS}$ by its gain. For H, the JFE2140's halves match to 4 mV at most and 1 mV typically, and drift apart by at most 10 µV/°C (SLPS730B §6.5, p. 5). The Monte Carlo of Section 6.4 (`scripts/cmrr_mc.py`) shifts the $V_{TO}$ and $\beta$ of each dual by a common amount (σ 100 mV and 5 %) and those of each half by its own (σ 0.85 mV and 1 %), so that the two halves of a dual differ by σ = 1.2 mV and 1.4 %. These σ are assumptions; for $\beta$ in particular the data sheet gives no matching, only an $I_{DSS}$ ratio. They put its limits, 4 mV and an $I_{DSS}$ ratio of 0.95–1.05 (p. 5), at 3.3σ and 3.5σ of the difference, and make the mean magnitude of the $V_{GS}$ difference, $\sigma\sqrt{2/\pi}$ = 0.96 mV, close to the typical 1 mV. The Monte Carlo gives an output offset of 3.4 V rms at a total gain of 1000, i.e. 3.4 mV at the input (`cmrr_mc.json`, 12 trials). Most of it comes from the assumed $\beta$ mismatch. At a fixed current $\Delta V_{GS} = \Delta V_{TO} - \tfrac12(V_{GS}-V_{TO})\,\Delta\beta/\beta$, with $V_{GS}-V_{TO} = \sqrt{I_D/\beta}$ = 0.59 V, so the two sides, with two duals each, differ by 3.0 mV rms from $\beta$ and by 0.85 mV rms from $V_{TO}$ (`scripts/numbers_s4b_5.py`). For L, unsorted JFE150 would not work. Taking the data sheet's $V_{GS(off)}$ range, −1.5 to −0.9 V (SLPS732B §6.5, p. 5), as ±3.5σ gives σ = 0.6 V/7 = 86 mV per device (an assumption); the means of the two sides' twelve then differ by $86\ \mathrm{mV}\cdot\sqrt{2/12}$ = 35 mV rms, which a total gain of 1000 turns into 35 V rms: the chain saturates. The 24 JFE150 must therefore come from one $V_{GS}$ bin, here ±5 mV at 5 mA (a design choice). The Monte Carlo draws each of them within the bin with σ 3 mV of $V_{TO}$ (a uniform ±5 mV spread has $5\ \mathrm{mV}/\sqrt3$ = 2.9 mV) and 2 % of $\beta$ (assumed), and leaves 2.3 V rms of offset at a total gain of 1000, i.e. 2.2 mV at the input (2.26 V/1005)."""),
    # ---- 4.6: offset trim with Eq. (9)'s full weight (line 662)
    (r"""A current injected into one summing node shifts that side's $V_{GS}$ by $\Delta I/(Ng_m)$: for H, a 12-bit DAC at ±10 V through 100 kΩ gives ±100 µA, i.e. ±2.9 mV at the input in 1.4 µV steps, and the 100 kΩ adds 0.4 pA/√Hz, i.e. 0.01 nV/√Hz at the input. For L, 10 kΩ gives ±1 mA, i.e. ±3.2 mV.""",
     r"""A current $\Delta I$ injected into one summing node shifts the input by $\Delta I\,w$, with the weight of Eq. (9) for a current entering that node, $w = 1/(Ng_m) + R_F/G$. Read from the simulated noise of $R_D$, which enters the same node ($e_{R_D} = \sqrt2\,w\sqrt{4kT/R_D}$ for both sides, Table 8's runs, `curves_noise.npz`), $w$ is 38 Ω for H at a gain of 100, 83 Ω at a gain of 10 and 4.8 Ω for L. Eq. (9) gives these values only with the cards' source resistance in series with $1/g_m$: for H, $(1/17.26\ \mathrm{mS} + 8\ \Omega)/2 + 5.0\ \Omega$ = 38.0 Ω, against 34.0 Ω without it. For H, a 12-bit DAC at ±10 V through 100 kΩ gives ±100 µA, i.e. ±3.8 mV at the input at a gain of 100 and ±8.3 mV at a gain of 10, in steps ($2\Delta I\,w/2^{12}$) of 1.9 and 4.0 µV, and the 100 kΩ adds $\sqrt{4kT/100\ \mathrm{k\Omega}}$ = 0.41 pA/√Hz, i.e. 0.016 and 0.034 nV/√Hz at the input. For L, 10 kΩ gives ±1 mA, i.e. ±4.8 mV (`scripts/numbers_s4b_5.py`)."""),
    # ---- 4.6: drift of the JFE2140's halves (line 676)
    (r"""For comparison, the JFE2140's two halves drift apart by at most 10 µV/°C.""",
     r"""For comparison, the JFE2140's two halves drift apart by at most 10 µV/°C (SLPS730B §6.5, p. 5)."""),
    # ---- 4.7: regulators (lines 692-696)
    (r"""The LT3094 (data sheet Rev. 0, pp. 1, 4–5, a public mirror of ADI's document; the LT3045 figures are from ADI's product page, its data sheet could not be downloaded) gives:""",
     r"""That is 100 µA × 150 kΩ = 15 V, the top of the LT3045's output range, and the SET current's ±1 % initial accuracy allows 1.01 × 15 V = 15.15 V (LT3045 data sheet Rev. D, p. 1). The LT3094 (data sheet Rev. 0, pp. 1, 4–5, a public mirror of ADI's document; ADI's Rev. B in `refs/literature/` gives the same values) gives, with the LT3045's values (Rev. D, pp. 1, 3) in parentheses:"""),
    (r"""- noise 70 nV/√Hz at 10 Hz and 2.2 nV/√Hz at 10 kHz ($C_{SET}$ = 4.7 µF), 0.8 µV rms from 10 Hz to 100 kHz (LT3045: 2 nV/√Hz at 10 kHz, 0.8 µV rms);""",
     r"""- noise 70 nV/√Hz at 10 Hz and 0.8 µV rms from 10 Hz to 100 kHz with $C_{SET}$ = 4.7 µF, and 2.2 nV/√Hz at 10 kHz with $C_{SET}$ = 0.47 µF (LT3045: the same 70 nV/√Hz and 0.8 µV rms, and 2 nV/√Hz);"""),
    (r"""- ripple rejection of 108 dB at 120 Hz, 94 dB at 10 kHz, 75 dB at 100 kHz, 74 dB at 1 MHz and 28 dB at 10 MHz (LT3045: 76 dB at 1 MHz);""",
     r"""- ripple rejection, with 2 V of headroom and 500 mA, of 108 dB at 120 Hz ($C_{SET}$ = 4.7 µF), and 94 dB at 10 kHz, 75 dB at 100 kHz, 74 dB at 1 MHz and 28 dB at 10 MHz ($C_{SET}$ = 0.47 µF) (LT3045: 76 dB at 1 MHz);"""),
    # ---- 4.7: supply rejection, regulator noise, power (line 698)
    (r"""The preamplifier's own supply rejection, referred to its input, is 98–101 dB up to 100 kHz, 81–86 dB at 1 MHz and 61–66 dB at 10 MHz (H, gain 100; L is better by 10–20 dB; Section 6.5). The regulators' noise therefore reaches the input at a level of picovolts per root hertz: 70 nV/√Hz at 10 Hz becomes 0.6 pV/√Hz, far below the amplifier's own nanovolts. The supply's ripple is rejected by the regulator and the amplifier in series, about 155 dB at 1 MHz. Above 10 MHz the regulators' rejection fades, so a ferrite and a few microfarads per rail at each stage are still needed. The L front end draws 120 mA from +15 V through its drain resistors alone, and about 200 mA from each rail in all; with 2–3 V of headroom each regulator dissipates up to about 0.6 W, which the MSOP's exposed pad handles with a copper area of a few square centimetres.""",
     r"""The preamplifier's own supply rejection, referred to its input, is 98–101 dB up to 100 kHz, 81–86 dB at 1 MHz and 61–66 dB at 10 MHz (H, gain 100, `large_signal.json`; L at 1000 with its 6 V sinks is better by 9–20 dB, `sink_power.json`; Section 6.5). The regulators' noise therefore reaches the input at a level of picovolts per root hertz: taking the rejection at 100 Hz, the lowest frequency simulated, 70 nV/√Hz at 10 Hz becomes $70\ \mathrm{nV}\cdot10^{-101.3/20}$ = 0.60 pV/√Hz on +15 V and 0.65 pV/√Hz on −15 V (100.7 dB), far below the amplifier's own nanovolts. The supply's ripple is rejected by the regulator and the amplifier in series: at 1 MHz by 76 + 81 = 157 dB on +15 V and 74 + 86 = 160 dB on −15 V. Above 10 MHz the regulators' rejection fades, so a ferrite and a few microfarads per rail at each stage are still needed. The L front end draws 120 mA from +15 V through its drain resistors alone; the preamplifier with L draws 177 mA from +15 V and 178 mA from −15 V, and 193 and 194 mA with both filters on (with H 76–92 mA; operating points with ideal references, `scripts/chain_extras.py`, `chain_extras.json`). With 2–3 V of headroom each regulator then dissipates 0.35–0.58 W with L (0.15–0.28 W with H), which raises the MSOP's junction by 19–20 K: its $\theta_{JA}$ is 33 °C/W with 2500 mm² and 35 °C/W with 100 mm² of top copper on the data sheets' four-layer test board (LT3094 Rev. 0, p. 3 and Table 4, p. 28; LT3045 Rev. D, p. 2 and Table 4, p. 22; `scripts/numbers_s4b_5.py`)."""),
    # ---- 4.8: the THS4021 (line 702)
    (r"""The THS4021 is there for its bandwidth: a decompensated 1.6 GHz amplifier with 1.5 nV/√Hz. Its data sheet's 1/f is moderate (4 nV/√Hz and 20 pA/√Hz at 10 Hz), but in the front end its current noise appears as $i_{n,A}/(Ng_m)$ per side and its voltage noise through the outer loop, and at a front-end gain of 10 the op amps contribute more than the JFETs at 1 and 10 Hz.""",
     r"""The THS4021 is there for its bandwidth: a decompensated amplifier, stable at gains of 10 or more, with a gain–bandwidth product of 2 GHz and 1.2 nV/√Hz (SLOS265F p. 1; 1.5 nV/√Hz in the DGN package, §5.7, p. 8). Its data sheet's 1/f is moderate (about 4 nV/√Hz and 20 pA/√Hz at 10 Hz, Figs. 5-11 and 5-12, p. 11), but in the front end its current noise appears with the weight $1/(Ng_m) + R_F/G$ of Eq. (9) per side and its voltage noise through the outer loop, and at a front-end gain of 10 the op amps contribute more than the JFETs at 1 and 10 Hz (7.8 against 7.0 and 2.5 against 2.4 nV/√Hz, `curves_noise.npz`)."""),
    # ---- 4.8: the DC-1 MHz case (line 706)
    (r"""a FET-input op amp of 50–100 MHz on ±15 V (OPA2810-class) removes the current-noise term, and a bipolar one with a low 1/f corner (OPA1612-class, 40 MHz) the voltage term. The projected noise is the simulated noise without the op amps' group: H at a gain of 100 falls from 2.70 to 2.43 nV/√Hz at 10 Hz and from 7.9 to 7.0 at 1 Hz; H at a gain of 10 from 3.8 to 2.9 at 10 Hz and from 10.6 to 7.2 at 1 Hz; L from 0.83 to 0.77 at 10 Hz and from 2.3 to 2.1 at 1 Hz.""",
     r"""a FET-input op amp of 50–100 MHz on ±15 V removes the current-noise term (the OPA2810, 70 MHz, comes close but runs on 4.75–27 V, SBOS789C p. 1), and a bipolar one with a low 1/f corner (OPA1612-class, 40 MHz, SBOS450C p. 1) the voltage term. The projected noise is the simulated noise without the op amps' group, $\sqrt{e_n^2 - e_{n,op}^2}$ (`curves_noise.npz`, `scripts/numbers_s4b_5.py`): H at a gain of 100 falls from 2.70 to 2.45 nV/√Hz at 10 Hz and from 7.9 to 7.1 at 1 Hz; H at a gain of 10 from 3.8 to 2.9 at 10 Hz and from 10.6 to 7.2 at 1 Hz; L from 0.83 to 0.78 at 10 Hz and from 2.3 to 2.1 at 1 Hz."""),
    (r"""The larger lever at low frequencies is the JFET: JFE150 instead of JFE2140 in H (1.8 against 2.4 nV/√Hz at 10 Hz per device, at about twice the capacitance), or IF3601-class parts in L (0.6 nV/√Hz at 10 Hz per device).""",
     r"""The larger lever at low frequencies is the JFET: JFE150 instead of JFE2140 in H (at 10 Hz and 2 mA, 1.6 against 2.4 nV/√Hz per device, and 1.8 for the JFE150 at 5 mA, SLPS732B and SLPS730B §6.5, p. 5; at 1.8 times the capacitance, 24 against 13 pF), or IF3601-class parts in L (0.6 nV/√Hz at 10 Hz per device at 5 mA, IF35076.R01, p. 3)."""),
    # ---- 5.1 (lines 721-722)
    (r"""- **CMRR** by Monte Carlo (12 trials per case) with""",
     r"""- **CMRR** by Monte Carlo (12 trials per case, 6 for the cases with one class of mismatch and 4 for the $R_{UP}$ test) with"""),
    (r"""distortion of 1 and 10 Vpp sines from 1 kHz to 10 MHz,""",
     r"""distortion of 1 Vpp sines from 1 kHz to 10 MHz and of 10 Vpp sines from 1 kHz to 1 MHz,"""),
    # ---- 5.2 (line 729)
    (r"""and LTspice's Linear Systems cards (2N5564, LSK389, LSK170, LSK489),""",
     r"""and the Linear Systems cards of LTspice's `standard.jft` (2N5564, LSK389, LSK170, LSK489; LTspice 26.1.1.0, library file of 20 September 2026, `model_defects.json`),"""),
    # ---- 5.3: Table 7 (lines 738-756)
    (r"""*Table 7. Defects found in the vendor models used, measured with each model alone in ngspice against its data sheet's typical values (`scripts/models.py`; the op-amp figures from two-gain noise runs that separate the voltage and current noise).*

| Model | Quantity | Model gives | Data sheet | Error | Correction |
|---|---|---|---|---|---|
| TI JFE2140 (SLPM355) | 1/f, KF | 0.2e-18: 1.2 nV/√Hz at 10 Hz, 2 mA | 2.4 nV/√Hz (SLPS730B Table 6.5) | 1/f power 14× too low | KF = 2.9e-18 |
| TI JFE2140 | $C_{iss}$, $C_{rss}$ at 5 V | 8.6 pF, 1.25 pF | 13 pF, 4.2 pF (Fig. 6-17) | 0.66×, 0.30× | CGS, CGD refitted |
| TI JFE150 (SLPM349I) | 1/f, KF | 3.25e-18 | 1.8 nV/√Hz at 10 Hz, 5 mA | consistent (7 %) | KF = 3.5e-18 |
| TI JFE150 | $C_{iss}$, $C_{rss}$ at 5 V | 17.8 pF, 2.3 pF | 24 pF, 4.5 pF (Fig. 6-12) | 0.74×, 0.50× | refitted |
| Linear Systems LSBF862 (Rev 2, 2026) | 1/f, KF | 8.75e-17: about 9 nV/√Hz at 10 Hz | 1.4 nV/√Hz typ, 4.0 max | 1/f power 50× too high (above the maximum) | KF = 1.74e-18 |
| Linear Systems LSBF862 | $C_{iss}$, $C_{rss}$ at 8 V | 6.5 pF, 0.87 pF | 11.5 pF, 3.5 pF | 0.56×, 0.25× | refitted |
| LTspice standard.jft 2N5564 | KF | 67860f = 6.786e-11 | Linear Systems' own listing: 6.786e-002f = 6.786e-17 | × 10⁶ (unit prefix) | KF refitted to Vishay's curve |
| LTspice standard.jft J310 | KF | 46340f = 4.634e-11: about 0.6 µV/√Hz gate-referred at 10 kHz and 11 mA | – (data sheet not read) | implausible for any JFET; probably the same unit-prefix error as the 2N5564 | none; the J310 sink was dropped (Section 6.1) |
| Linear Systems LSK170/LSK389 cards (LTspice) | channel noise | NLEV = 3, GDSNOI = 5–8 | – | LTspice-only noise equation; in ngspice 1.41 vs 0.86 nV/√Hz | NLEV, GDSNOI removed, RX calibration |
| TI THS4021 (SLOJ004, 1999) | $e_n$, $i_n$ at 10 Hz | 18.2 nV/√Hz, 293 pA/√Hz | 4 nV/√Hz, 20 pA/√Hz (SLOS265F Figs. 5-11, 5-12) | 4.6×, 15× | KF = 0, 1/f generators fitted |
| TI THS4031 (SLOJ005A) | $e_n$, $i_n$ at 10 Hz | 22.2 nV/√Hz, 300 pA/√Hz | 4 nV/√Hz, 20 pA/√Hz (SLOS224L Figs. 5-13, 5-14) | 5.5×, 15× | KF = 0, 1/f generators fitted |
| TI THS4031 | HD3 at 10 MHz | −37 dBc at 1 Vpp (in S2) | about −50 dBc at 2 Vpp, G = 2 (Fig. 5-15) | about 20 dB too high | none; LM7171 chosen |
| TI THS3091 (SLOM418) | $e_n$, $i_{n-}$ at 10 Hz | 37 nV/√Hz, 317 pA/√Hz | 6.5 nV/√Hz, 200 pA/√Hz (SLOS423K Fig. 7-16) | 5.7×, 1.6× | KF = 0, 1/f generators fitted |
| TI THS3091 | white $i_{n-}$ | 1.5 pA/√Hz | 14 pA/√Hz (Sec. 6.5) | 0.11× | white generator added |
| TI LM7171 (SNOM205A, National) | white $e_n$; 1/f | 4.1 nV/√Hz; none | 8.5 nV/√Hz (A grade); 43 nV/√Hz at 10 Hz (Fig. 5-16) | 0.48×; missing | white and 1/f generators added |""",
     r"""*Table 7. Defects found in the vendor models used, measured with each model alone in ngspice against its data sheet's typical values (`scripts/opamp_noise_check.py` and `scripts/model_defects.py`, with the results in `opamp_noise_check.json` and `model_defects.json`; the op-amp figures from two-gain noise runs that separate the voltage and current noise; the JFET calibration by `scripts/models.py`). Data-sheet values cited by figure are read by eye from its curves.*

| Model | Quantity | Model gives | Data sheet | Error | Correction |
|---|---|---|---|---|---|
| TI JFE2140 (SLPM355) | 1/f, KF | 0.2e-18: 1.2 nV/√Hz at 10 Hz, 2 mA | 2.4 nV/√Hz (SLPS730B §6.5, p. 5) | 1/f power 14× too low | KF = 2.9e-18 |
| TI JFE2140 | $C_{iss}$, $C_{rss}$ at 5 V | 8.6 pF, 1.25 pF | 13 pF (§6.5, p. 5), 4.2 pF (Fig. 6-17, p. 8) | 0.67×, 0.30× | CGS, CGD refitted |
| TI JFE150 (SLPM349I) | 1/f, KF | 3.25e-18: 1.75 nV/√Hz at 10 Hz, 5 mA (with the calibrated white) | 1.8 nV/√Hz at 10 Hz, 5 mA (SLPS732B §6.5, p. 5) | consistent: the calibrated KF is 7.5 % higher | KF = 3.5e-18 |
| TI JFE150 | $C_{iss}$, $C_{rss}$ at 5 V | 17.8 pF, 2.3 pF | 24 pF (§6.5, p. 5), 4.5 pF (Fig. 6-12, p. 7) | 0.74×, 0.50× | refitted |
| Linear Systems LSBF862 (Rev 2, 2026) | 1/f, KF | 8.75e-17: 9.1 nV/√Hz at 10 Hz (Eq. (1)) | 1.4 nV/√Hz typ, 4.0 max (Doc 201195 Rev A2, p. 2) | 1/f power 50× too high (above the maximum) | KF = 1.74e-18 |
| Linear Systems LSBF862 | $C_{iss}$, $C_{rss}$ at 8 V | 6.5 pF, 0.87 pF | 11.5 pF, 3.5 pF (p. 2) | 0.56×, 0.25× | refitted |
| LTspice standard.jft 2N5564 | KF | 67860f = 6.786e-11 | Linear Systems' own listing (`sim/models/LinearSystems/2N5564/`): 6.786e-002f = 6.786e-17 | × 10⁶ (unit prefix); 1/f corner 1.14 GHz | KF refitted to Vishay's curve (70254 Rev. E, p. 5) |
| LTspice standard.jft J310 | KF | 46340f = 4.634e-11: 0.59 µV/√Hz gate-referred at 10 kHz (Eq. (1)), 0.54 in ngspice at 11 mA | – (data sheet not read) | implausible for any JFET; probably the same unit-prefix error as the 2N5564; as H's sink at a gain of 10, 60.7 nV/√Hz at 10 kHz | none; the J310 sink was dropped (`scripts/sink_options.py`) |
| Linear Systems LSK170/LSK389 cards (LTspice) | channel noise | NLEV = 3, GDSNOI = 5–8; in ngspice the LSK389B gives 1.41 nV/√Hz with them and 0.86 without (2 mA, 10 V) | 1.6 nV/√Hz at 1 kHz (LSK389, Doc 201122 Rev A27, p. 2) | white noise set by an optional equation: 0.88× the data sheet with it, 0.54× without | NLEV, GDSNOI removed, RX calibration |
| TI THS4021 (SLOJ004, 1999) | $e_n$, $i_n$ at 10 Hz; white $i_n$ | 18.2 nV/√Hz, 293 pA/√Hz; 1.18 pA/√Hz | 4 nV/√Hz, 20 pA/√Hz (SLOS265F Figs. 5-11, 5-12, p. 11); 2.3 pA/√Hz (§5.6, p. 6) | 4.6×, 15×; 0.52× | KF = 0, 1/f generators fitted; white kept |
| TI THS4031 (SLOJ005A) | $e_n$, $i_n$ at 10 Hz; white $i_n$ | 22.2 nV/√Hz, 300 pA/√Hz; 1.12 pA/√Hz | 4 nV/√Hz, 20 pA/√Hz (SLOS224L Figs. 5-13, 5-14, p. 12); 2.3 pA/√Hz (§5.6, p. 6) | 5.5×, 15×; 0.49× | KF = 0, 1/f generators fitted; white kept |
| TI THS4031 | HD3 at 10 MHz | −38 dBc at 1 Vpp (in S2) | about −50 dBc at 2 Vpp, G = 2 (SLOS224L Fig. 5-15, p. 12) | 12 dB above the curve as read; 24 dB after scaling to 2 Vpp (HD3 ∝ $V^2$) | none; LM7171 chosen |
| TI THS3091 (SLOM418) | $e_n$, $i_{n-}$ at 10 Hz | 37 nV/√Hz, 317 pA/√Hz | 6.5 nV/√Hz, 200 pA/√Hz (SLOS423K Fig. 7-16, p. 12) | 5.7×, 1.6× | KF = 0, 1/f generators fitted |
| TI THS3091 | white $i_{n-}$ | 1.5 pA/√Hz | 14 pA/√Hz (SLOS423K §7.5, p. 6) | 0.11× | white generator added |
| TI LM7171 (SNOM205A, National) | white $e_n$; 1/f | 4.1 nV/√Hz; none | 8.5 nV/√Hz (A grade, SNOS760D §5.5, p. 5); 43 nV/√Hz at 10 Hz (Fig. 5-16, p. 10, at ±5 V) | 0.48×; missing | white and 1/f generators added |"""),
    # ---- 5.3: TI JFET paragraph (line 758)
    (r"""TI's JFE150 card has KF = 3.25e-18 with β = 31 mA/V², and it reproduces its data sheet's 1.8 nV/√Hz at 10 Hz.""",
     r"""TI's JFE150 card has KF = 3.25e-18 with β = 31 mA/V², and with the calibrated white noise it gives 1.75 nV/√Hz at 10 Hz against its data sheet's 1.8."""),
    (r"""ngspice ignores the grading exponent M = 0.33, so CGS and CGD evaluated with an exponent of 0.5 at 5 V are too small,""",
     r"""ngspice ignores the cards' grading exponent M = 0.33: its JFET has no such parameter, and its junction capacitances vary as the −1/2 power of the junction voltage (ngspice-46 manual, §7.4.4, pp. 153–154). CGS and CGD evaluated with an exponent of 0.5 at 5 V are therefore too small,"""),
    # ---- 5.3: TI op-amp paragraph (line 760)
    (r"""the model's current-noise 1/f corner sits near 100 kHz instead of about 1 kHz. In this front end the op amps' current noise appears at the input as $i_{n,A}/(Ng_m)$. With the published THS4021 model, the H front end showed 11.3 nV/√Hz at 10 Hz, four times the 2.7 nV/√Hz it has with the corrected model.""",
     r"""the model's current-noise 1/f corner, $f_0\,(i_n(f_0)/i_{n,w})^2$ with $f_0$ = 10 Hz and the model's own white $i_{n,w}$, sits at 0.61 MHz (THS4021) and 0.72 MHz (THS4031) instead of the data sheets' 0.76 kHz (`scripts/numbers_s4b_5.py`). In this front end the op amps' current noise appears at the input with the weight $1/(Ng_m) + R_F/G$ of Eq. (9). With the published THS4021 model, the H front end at a gain of 100 has 16.2 nV/√Hz at 10 Hz, six times the 2.70 nV/√Hz it has with the corrected model (`opamp_noise_check.json`)."""),
    (r"""sized to the data sheet's curves, over the model's own white noise.""",
     r"""sized to the data sheet's curves, over the model's own white noise. That white current noise, 1.18 pA/√Hz in the THS4021 and 1.12 in the THS4031, is 0.52 and 0.49 times the data sheets' 2.3 pA/√Hz (SLOS265F and SLOS224L §5.6, p. 6), and the correction keeps it: through Eq. (9) the THS4021's shortfall makes the front ends' simulated white noise 0.5 % too low for H at a gain of 100, 0.7 % at a gain of 10 and 0.05 % for L (`scripts/numbers_s4b_5.py`)."""),
    (r"""its voltage noise, a tenth of the data sheet's white inverting-input current noise,""",
     r"""its voltage noise, 0.11 times the data sheet's white inverting-input current noise,"""),
    (r"""and a current-noise 1/f only 1.6 times high; at low gains, where the THS3091 output stage dominates, it put the noise at 1 Hz too high by a factor of 1.8.""",
     r"""and a current-noise 1/f only 1.6 times high; at a total gain of 1, where its current noise sets the chain's noise at 1 Hz (Section 4.5), the published model puts that noise too high by a factor of 1.76 (1.65 at a gain of 10; `opamp_noise_check.json`)."""),
    (r"""so its voltage noise is half the data sheet's and its 1/f is missing.""",
     r"""so its white voltage noise is 0.48 times the data sheet's and its 1/f is missing; the correction adds both, but not the 1/f of the data sheet's current noise (Fig. 5-17, p. 10)."""),
    # ---- 5.3: Linear Systems and LTspice paragraph (line 762)
    (r"""The LSBF862 card of February 2026 has the KF of NXP's old BF862 model, 8.75e-17, which gives about 9 nV/√Hz at 10 Hz, above the data sheet's 4.0 nV/√Hz maximum. LTspice's library copy of Linear Systems' 2N5564 card lists KF as "67860f", 6.786e-11, where Linear Systems' own listing has "6.786e-002f", 6.786e-17. A factor of a million in KF puts the 1/f corner of a 2N5564 in the megahertz range, so an SR560 reproduction with the library card would be absurdly noisy. The library's J310 card has a value of the same kind, KF = "46340f", 4.634e-11. As a current sink at 11 mA it alone would set the H front end's noise at a gain of 10 to 61 nV/√Hz at 10 kHz (Section 6.1, where it was dropped). The Linear Systems cards in LTspice's library also use NLEV = 3 and GDSNOI, LTspice's alternative channel-noise equation; ngspice does not implement it the same way (an LSK389 card gave 1.41 nV/√Hz instead of 0.86), so they are removed and the white noise is calibrated with RX instead.""",
     r"""The LSBF862 card of February 2026 has the KF of NXP's old BF862 model (`BF862.prm`, file header of March 2007, KF = 87.5E-18; transcribed in `sim/models/README_InterFET_NXP_others.md`, the file itself not archived), 8.75e-17, which gives 9.1 nV/√Hz at 10 Hz by Eq. (1), above the data sheet's 4.0 nV/√Hz maximum. LTspice's library copy of Linear Systems' 2N5564 card (`lib/cmp/standard.jft` of LTspice 26.1.1.0, dated 20 September 2026, SHA-256 82bdc4a4…3557, whose change log's last JFET entry is "06/26/23 Updated JFET device models from Linear Systems"; `model_defects.json`, `ltspice_library`) lists KF as "67860f", 6.786e-11, where Linear Systems' own listing has "6.786e-002f", 6.786e-17. A factor of a million in KF puts the 1/f corner of a 2N5564 at 1.14 GHz (Eq. (1) with the calibrated white noise of 1.28 nV/√Hz; 43 nV/√Hz at 1 MHz), so an SR560 reproduction with the library card would be absurdly noisy. The library's J310 card has a value of the same kind, KF = "46340f", 4.634e-11. As a current sink at 11 mA it alone would set the H front end's noise at a gain of 10 to 60.7 nV/√Hz at 10 kHz (`scripts/model_defects.py`); it was dropped before the sink study of Section 6.1 (`scripts/sink_options.py`). The Linear Systems cards in LTspice's library also use NLEV = 3 and GDSNOI = 5–8, an alternative channel-noise equation that ngspice implements too (ngspice-46 manual, §7.4.4, p. 154): in ngspice the LSK389B card gives 1.41 nV/√Hz with them and 0.86 without, at 2 mA and 10 V, against the data sheet's 1.6 at 1 kHz (`model_defects.json`). Whether LTspice evaluates them the same way was not checked, so they are removed and the white noise is calibrated with RX instead."""),
]


def main() -> None:
    path = Path(sys.argv[1])
    text = path.read_bytes().decode("utf-8")
    assert "\r" not in text, "the note is expected to have \\n newlines"
    assert text.count(START) == 1 and text.count(END) == 1
    i0 = text.index(START)
    i1 = text.index(END)
    assert i0 < i1
    head, s, tail = text[:i0], text[i0:i1], text[i1:]
    n_lines = text.count("\n")
    for old, new in REPL:
        assert s.count(old) == 1, f"not found exactly once in Sections 4.4-5: {old[:90]!r}"
        assert old.count("\n") == new.count("\n"), f"would change the line count: {old[:90]!r}"
        s = s.replace(old, new)
    assert (head + s + tail).count("\n") == n_lines
    path.write_bytes((head + s + tail).encode("utf-8"))
    print(f"{len(REPL)} replacements in Sections 4.4-5 of {path}")


if __name__ == "__main__":
    main()
