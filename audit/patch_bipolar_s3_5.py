"""Patch of low_noise_preamp.md after patch_renumber_s3_5.py (25 November 2026): the new Section 3.5, "Bipolar input
stages and 1/f noise", with its Table 5 and Figure 6; a paragraph at the end of Section 4.1.1; the papers on 1/f
noise and the bipolar data sheets in the References; the new scripts and files in Section 8.

Every number comes from sim/results/numbers_s3_5.json (scripts/numbers_s3_5.py), which reads bipolar_inputs.json,
bipolar_fe.json and bipolar_fe.npz (scripts/bipolar_inputs.py) and the data-sheet readings with their pages.
Every edit is an exact-string replacement whose old text occurs once.  A second run is refused.
Usage: python patch_bipolar_s3_5.py <path to low_noise_preamp.md>
"""
from __future__ import annotations

import sys
from pathlib import Path

SECTION = r"""

### 3.5 Bipolar input stages and 1/f noise

L's twelve JFE150 per side set its noise floor: 0.33 nV/√Hz white and 2.13 nV/√Hz at 1 Hz from the JFETs alone, most of the latter 1/f noise. A bipolar transistor has less voltage noise for a given current, since its transconductance is $I_C/V_T$, but adds the shot and 1/f noise of its base current. This section asks whether matched bipolar transistors in production would serve the lowest source resistances better than L, and how their 1/f noise decides the answer. It is a study of a possible third input; the bipolar front end B below is not part of the design.

**Location of the 1/f noise.** In a silicon bipolar transistor the low-frequency noise is a fluctuation of the base current. Kleinpenning's review concludes that in high-quality transistors it is 1/f noise in the base current, normally proportional to $I_B$ as the mobility-fluctuation model predicts, with deviations at high currents that come from the series resistances (Kleinpenning 1994, p. 1990); its magnitude $fS_{I_B}/I_B$ spans $10^{-17}$ to $10^{-12}$ A in conventional transistors (p. 1987). In polysilicon-emitter transistors with an interfacial oxide it grows as $I_B^2$ and as the inverse of the emitter area, from sources spread over the emitter (Markus and Kleinpenning 1995, p. 722, Figs. 3 and 4). Measuring the noise in the base and collector leads together, Bruce, Vandamme and Rydberg (1999, p. 998) locate the dominant source in the base–emitter junction, on the emitter side, and not in the base or emitter resistance. The source thus sits at the internal base, behind the base spreading resistance $r_{bb'}$, as in Leach's model: his Eqs. (43)–(44) give the voltage noise $e_n^2 = 4kTr_{bb'} + 2kTV_T/I_C$, with no 1/f term, and the current noise $i_n^2 = 2qI_B + K_FI_B/f$ (Leach 1994, p. 1525). The base current's 1/f noise reaches the input as $S_{I_B,f}\,(R_S + r_{bb'})^2$: through $r_{bb'}$ as voltage noise and through the source as $i_nR_S$, the two parts adding coherently. ngspice's Gummel–Poon model places its flicker noise $K_FI_B^{A_F}/f$ in the same way; on one transistor its $e_n$ and $i_n$ agree with these expressions to within 0.2 % (`scripts/bipolar_inputs.py`). In a JFET the 1/f noise is a fluctuation of the channel's conductance; in most semiconductor devices such noise comes from fluctuations in the number of carriers by charge exchange with defects (Fleetwood 2015, p. 1462). It is referred to the gate as a voltage, whatever the source (Leach's Eqs. (64)–(65)), and the gate current carries only shot noise. The two devices therefore put their 1/f noise in opposite generators, a JFET in $e_n$ and a bipolar transistor in $i_n$, and a bipolar input can be the quieter at low frequencies only with source resistances small enough that its $i_nR_S$ stays below the JFETs' 1/f voltage. Leach (1994, p. 1534) makes the same comparison: the bipolar transistor is better with small source resistances, and the FET usually has more flicker noise.

**Matched pairs in production.** Table 5 lists the matched bipolar pairs and arrays in production that give noise data. Only Analog Devices' SSM2212 and the MAT12, the same transistors in a TO-78 can, combine a low $r_{bb'}$, 28 Ω typical, with a high current gain, 605 typical at 1 mA. Linear Systems' LS3250 implies about 23 Ω, but its data sheet gives only two noise values, one of them 2.7 nV/√Hz at 100 Hz; the LS310–LS313 imply 68–90 Ω and Analog Devices' MAT14 about 184 Ω ($r_{bb'} = e_n^2/4kT - r_e/2$, Leach's Eq. (43) inverted). The PNP pairs give a noise figure only. THAT Corporation's 300-series arrays, 32 Ω for the NPN, were put on end-of-life status on 1 September 2026, and their last-time buy closed on 30 September 2026. Discrete large-area transistors reach lower, about 2 Ω for Rohm's 2SB737 and 4 Ω for its 2SD786 (data book p. 188), but they are not matched pairs and are not studied here. No part in production publishes its current noise against frequency, and none of the vendor models read (THAT's, the LS350's and the MAT03's) has flicker noise; the MAT12's and SSM2212's models sit behind a licence agreement and were not read.

*Table 5. Matched bipolar pairs and arrays with noise data: typical values from their data sheets (`refs/datasheets/bjt/`), at 25 °C; $r_{bb'}$ marked "derived" is Leach's Eq. (43) inverted from the stated $e_n$ (`scripts/numbers_s3_5.py`). Status from the manufacturers' product pages and THAT's memo, 24 November 2026.*

| Part | Type | $r_{bb'}$ (Ω) | $h_{FE}$ at 1 mA | $e_n$ (nV/√Hz) | $i_n$ against frequency | Status |
|---|---|---|---|---|---|---|
| Analog Devices SSM2212 (SOIC-8, LFCSP-16) | NPN dual | 28; 22–31 derived | 605 (SOIC); 1300 at $V_{CB}$ = 0 and 1800 at 15 V (LFCSP) | 1.6 / 0.85 at 10 Hz / 1 kHz (table), 0.74 / 0.76 (curve); 1 mA | none; shot noise at 1 kHz (its Fig. 5) | in production |
| Analog Devices MAT12 (TO-78) | NPN dual, the SSM2212's transistors | 28 | 605 | as the SSM2212 | none | in production |
| Linear Systems LS3250A/B/C | NPN dual, up to 50 mA | 23 derived | ≥ 150, 100, 50 | 2.7 at 100 Hz, 0.7 at 1 kHz; 2 mA | none | listed |
| Linear Systems LS310–LS313 | NPN dual | 68–90 derived | ≥ 150 to 400 | 1.5 / 1.3 at 10 Hz / 1 kHz; 1 mA | none | listed |
| Analog Devices MAT14 | NPN quad | 184 derived | 600 | 2 / 1.8 at 10 Hz / 1 kHz; 1 mA | none | in production |
| Linear Systems LS350–LS352, LS3550 | PNP duals | not given | ≥ 100 to 200; ≥ 50 to 150 | noise figure ≤ 3 dB at 100 µA only | none | listed |
| THAT 300, 320, 340 | NPN, PNP and mixed quads | 32 (NPN) | 100 (NPN) | 0.8 at 1 kHz (NPN); 1 mA | none | end of life, 1 September 2026 |

**Calibration of the SSM2212.** Its Gummel–Poon card (`scripts/bipolar_inputs.py`) takes the stated typical $r_{bb'}$ of 28 Ω, which with the bulk resistance of 0.3 Ω gives 0.82 nV/√Hz at 1 mA, between the typical curve's 0.76 and the table's 0.85 nV/√Hz; the current gain of 605, flat from 1 µA to 1 mA; $V_{BE}$, the output conductance and the junction capacitances from its curves (the emitter–base capacitance, which it does not give, from the MAT02's); and $f_T$ = 200 MHz at 10 mA. The data sheet gives no base-current noise against frequency, and its two statements of the voltage noise at 10 Hz disagree: 1.6 nV/√Hz typical in its table and about 0.74 on its curve. The table's value cannot come from the base current: to reach 1.6 nV/√Hz through 28 Ω, the base current's 1/f noise would be 6.6 times its shot noise at 1 kHz, whereas the data sheet's curve of total noise against current with a 100 kΩ source (its Fig. 5) puts the current noise at 1 kHz at 0.97–1.49 times the shot-noise power from 0.1 to 1 mA, so the base current's 1/f corner lies below a few hundred hertz at these currents. Comparable parts' corners near 1 mA are about 180 Hz for Rohm's 2SB737 (its Fig. 15), 340 Hz or 1.8 kHz for the discontinued MAT03 (its TPC 10, read as a pair or as one transistor), about 1.6 kHz for the discontinued LM394, 140 Hz for the OP37's input stage and 250 Hz typical, 800 Hz maximum, for the LT1028's (their data sheets' p. 7 and pp. 6 and 11). The card therefore puts the corner at 200 Hz for 1 mA and the study brackets it from 30 Hz to 1 kHz. The corner is scaled with current by $A_F$ = 1.3, between the 1.28 and 1.22 that the rise of the 2SB737's and LM394's corners with current implies and Kleinpenning's 1, as $K_F = 2qf_{c}I_{B0}^{1-A_F}$ with $I_{B0}$ the base current at 1 mA.

**Input devices alone.** A testbench simulates the input devices without the rest of the front end: a differential pair of $N$ devices per side on an ideal tail current, with noiseless current readout, and a noiseless source resistance in series with input A; at each frequency the runs over the source resistance are fitted as a noisy two-port, $v_a^2 = e_n^2 + 2R_S\,\mathrm{Re}(e_ni_n^*) + R_S^2i_n^2$ (`scripts/bipolar_inputs.py`). With L's twelve JFE150 it reproduces the input JFETs' share of L's simulated noise to within 0.02 % from 1 Hz to 100 kHz, and the bipolar arrays' white noise agrees with Leach's Eqs. (43)–(44) to within 0.3 % in $e_n$ and 0.7 % in $i_n$. At L's current, 60 mA per side, 12, 24 and 48 SSM2212 per side (5, 2.5 and 1.25 mA each) give 0.29, 0.22 and 0.16 nV/√Hz white against L's 0.33, and 0.44, 0.26 and 0.18 nV/√Hz at 1 Hz against 2.13 (Figure 6a). Their current noise is the same when white, 5.6 pA/√Hz per input, since the total base current is the same, and rises to 81–99 pA/√Hz at 1 Hz, or 35–200 pA/√Hz for 24 per side across the corner's bracket (Figure 6b); the LFCSP version's higher current gain would lower it to 3.7 pA/√Hz white. The SSM2212's $r_{bb'}$ makes many devices necessary: twelve per side lower the white noise by only 11 %, 24 per side by 34 % and 48 per side by 50 %.

![Figure 6](figures/fig_bipolar_inputs.png)

*Figure 6. Bipolar input stages against L (`scripts/bipolar_inputs.py`). (a) Differential input voltage noise and (b) current noise per input of the input devices alone, in the testbench, at L's 60 mA per side: L's twelve JFE150, and 12, 24 and 48 SSM2212 per side (dashed: the LFCSP version's higher current gain). The lines take a base-current 1/f corner of 200 Hz at 1 mA, the band spans 30 Hz to 1 kHz for 24 per side. L's current noise, 0.35 fA/√Hz at 1 kHz from the JFETs and 41 fA/√Hz with its 10 MΩ bias resistors, lies far below panel (b). (c) Noise figure, for a source at 290 K, against the source resistance at 1 Hz, 10 Hz and 1 kHz, of the front ends L and B (L with 24 SSM2212 per side); the band spans the corner's bracket for B at 1 Hz. (d) The source resistance below which B is quieter than L, against frequency.*

**A complete bipolar front end.** B is L's front end (Section 4.2, Figure 9) with 24 SSM2212 per side at 2.5 mA in place of the twelve JFE150 at 5 mA, and the same $R_F$ and $R_G$, cascodes, bootstrap, sinks and op amps; each dual gives one transistor to each side, as H's JFE2140 duals do (`scripts/frontend.py`, whose input devices can now be a bipolar card, and `scripts/bipolar_inputs.py`). Its operating point is L's, with the source node 0.59 V below the inputs instead of above them and 3.97 V across each transistor. The array's transconductance, 2.3 S per side against the JFETs' 0.31 S, raises the loops' gain, so the compensation was scanned again as in Section 4.3.1: with $C_I$ = 75 pF, $C_X$ = 7.5 pF and $C_{node}$ = 2.2 nF the margins at the op amps' output pins are 65.6° and 16.3 dB in differential mode and 61.1° and 14.6 dB in common mode, against L's 63° and 17 dB, 51° and 10 dB (Table 7), and the front end has a gain of 201.0 and a bandwidth of 13.2 MHz without peaking. With the inputs shorted it gives 0.54, 0.33 and 0.30 nV/√Hz at 1 Hz, 10 Hz and 1 kHz against L's 2.33, 0.83 and 0.41, and 0.30–0.31 against 0.41 nV/√Hz up to 1 MHz; at 10 MHz it is the noisier, 0.56 against 0.50 nV/√Hz. Two contributions change their weight. $R_G$'s noise, 0.20 nV/√Hz in both, now nearly equals the input devices' 0.22 nV/√Hz at 1 kHz, while the op amps' falls by a factor of 2.9 with the larger transconductance. And the base current's noise flows through $R_G/2$ as well as through $r_{bb'}/N$: in the front end the input devices give 0.375 nV/√Hz at 1 Hz against 0.262 in the testbench, as $e^2 = e_{tb}^2 + 2i_{side}^2\left[(r/N + R_G/2)^2 - (r/N)^2\right]$ predicts (0.375 nV/√Hz, with $r$ = 28.3 Ω and $i_{side}$ the testbench's current noise per input). A smaller $R_G$, with $R_F$ scaled with it, would lower both.

**Noise with a source resistance.** Figure 6c compares the noise figures of B and L, at the front-end level, with a source resistance in series with input A (`scripts/bipolar_inputs.py`, fitted as above), and Figure 6d gives the source resistance below which B is the quieter: with the corner of 200 Hz, 23 Ω at 1 Hz, 24 Ω at 10 Hz, 31 Ω at 100 Hz, 42 Ω at 1 kHz and 46 Ω from 10 to 100 kHz; across the corner's bracket, 9–63 Ω at 1 Hz and 31–47 Ω at 1 kHz. Above about 46 Ω L is quieter at every frequency. With 10 Ω the noise figure at 1 Hz is 10.1 dB for B (5.4–16.3 dB across the bracket) against 15.4 dB for L, at 10 Hz 3.9 dB (2.5–7.5 dB) against 7.3 dB, and at 1 kHz 2.1 against 3.2 dB. With 1 Ω, B gains 11.9 dB at 1 Hz (7.7–13.7 dB) and 2.4 dB at 1 kHz; with 100 Ω it loses 10.9 dB at 1 Hz and 0.7 dB at 1 kHz.

**Costs and open questions.** B draws 96 µA of base current per input, which must flow through the source: 0.96 mV of offset with 10 Ω. L's 10 MΩ bias resistors (Section 4.4) would be impossible; a DC path of a few kilohms, or a bias-current cancellation with its own noise, would take their place. Its input network would have to be designed anew. The bare front end's input has a negative resistance at high frequencies, −1.2 kΩ at 1 MHz and −28 Ω at 10 MHz against L's −13.5 kΩ and −172 Ω, and its response peaks by 4.1 dB at 6.0 MHz with a plain 10 Ω source (L: 0.25 dB), by 26 dB at 3.3 MHz with 50 Ω and 1 µH (L: 9.9 dB) and by 21 dB at 6.6 MHz through 1 m of cable from 10 Ω (L: 17.6 dB). L's network of Section 4.4 damps these for L; B would need its own, which is not designed here. B needs 24 SSM2212, as many packages as L has JFE150. Below 10 Hz neither part's data are consistent. The JFE150's noise at 1 Hz is 5.2, 9.1 or 14 nV/√Hz per device according to whether its 10 Hz table value is extended as 1/f noise (the calibration of Section 3.4), its 0.1–10 Hz peak-to-peak value is matched, or its Fig. 6-9 is read; for L's JFETs this means 2.1, 3.7 or 5.7 nV/√Hz at 1 Hz, and a larger value would widen B's advantage there. The SSM2212's 0.1–10 Hz value, 0.4 µV peak to peak at 1 mA, is 12 times what its own curve integrates to. The decisive quantity, the SSM2212's base-current noise against frequency, is not published: a measurement of $i_n$ with a source of 100 kΩ to 1 MΩ from 0.1 Hz, and of $e_n$ with a shorted pair, would settle whether a third input B is worth building, for sources below about 20 Ω such as thermocouples, low-resistance samples and current shunts."""

S411 = r"""

**A bipolar input for the lowest source resistances.** Section 3.5 studies a third input stage, B: L's front end with 24 SSM2212 matched bipolar pairs per side in place of its JFETs. B is quieter than L below about 23 Ω of source resistance at 1 Hz and about 46 Ω above 10 kHz (9–63 Ω at 1 Hz across the uncertainty in the base current's 1/f noise), most of all at low frequencies: with 10 Ω its noise figure at 1 Hz is 10.1 dB against L's 15.4 dB, and with a shorted input its noise is 0.54 against 2.33 nV/√Hz at 1 Hz and 0.30 against 0.41 nV/√Hz at 1 kHz. Above about 46 Ω L is quieter at every frequency. B is not part of the design: its advantage rests on base-current 1/f noise that no bipolar pair in production publishes, and it would need its own input network (Section 3.5)."""

EDITS = [
    # Section 3.5, after Section 3.4
    ("The calibration fits the two capacitances at the bias where the data sheet gives them, which is what matters "
     "for the circuit.\n\n---\n\n## 4. The new design",
     "The calibration fits the two capacitances at the bias where the data sheet gives them, which is what matters "
     "for the circuit." + SECTION + "\n\n---\n\n## 4. The new design"),
    # Section 4.1.1
    ("Between about 3 kΩ and 200 kΩ at 1 kHz the two differ in noise by less than 1 % (Section 6.2), and either input "
     "may be used.\n\n### 4.2 ",
     "Between about 3 kΩ and 200 kΩ at 1 kHz the two differ in noise by less than 1 % (Section 6.2), and either input "
     "may be used." + S411 + "\n\n### 4.2 "),
    # Section 8
    ("| `scripts/jfet_model_check.py`, `scripts/jfet_data.py`, `scripts/noise_theory.py` | Figure 5 and the calibration "
     "check, Tables 2 and 3, and the closed forms of Section 1 (`jfet_model_check.json`, `jfet_table3.json`, "
     "`noise_theory.json`) |\n",
     "| `scripts/jfet_model_check.py`, `scripts/jfet_data.py`, `scripts/noise_theory.py` | Figure 5 and the calibration "
     "check, Tables 2 and 3, and the closed forms of Section 1 (`jfet_model_check.json`, `jfet_table3.json`, "
     "`noise_theory.json`) |\n"
     "| `scripts/bipolar_inputs.py` | Section 3.5 and Figure 6: the SSM2212's calibrated card "
     "(`sim/models/_lib/bipolar_inputs.lib`), the check of ngspice's flicker noise on one transistor, the input-stage "
     "testbench of L's JFETs and the SSM2212 arrays (`bipolar_inputs.json`, `bipolar_inputs.npz`), and the bipolar front "
     "end B: its compensation scan, margins, operating point and noise groups, its and L's noise over the source "
     "resistance, input impedance and response with real sources (`bipolar_comp_search.json`, `bipolar_fe.json`, "
     "`bipolar_fe.npz`, `bipolar_fe_noise.npz`) |\n"),
    ("| `scripts/numbers_s1_3.py`, `scripts/numbers_s4a.py`, `scripts/numbers_s4b_5.py`, `scripts/numbers_s6_7.py` | "
     "the derived numbers of the summary and Sections 1–3, of Sections 4.1–4.3.1,",
     "| `scripts/numbers_s1_3.py`, `scripts/numbers_s3_5.py`, `scripts/numbers_s4a.py`, `scripts/numbers_s4b_5.py`, "
     "`scripts/numbers_s6_7.py` | the derived numbers of the summary and Sections 1–3, of Section 3.5 and Table 5, of "
     "Sections 4.1–4.3.1,"),
    ("| `scripts/make_figures.py`, `scripts/plot_style.py` | Figures 1, 3–5, 10, 11 and 13–18 |",
     "| `scripts/make_figures.py`, `scripts/plot_style.py` | Figures 1, 3–6, 10, 11 and 13–18 |"),
    ("the JFET, op-amp, switch, relay and regulator data sheets (`datasheets/`)",
     "the JFET, bipolar, op-amp, switch, relay and regulator data sheets (`datasheets/`, with THAT's end-of-life memo "
     "of its 300 series in `datasheets/bjt/`)"),
    # References
    ("- The full list of sources read, with what was read of each, is in `refs/literature/literature_notes.md`.\n\n"
     "**Data sheets.**",
     "- The full list of sources read, with what was read of each, is in `refs/literature/literature_notes.md`.\n\n"
     "**Papers on 1/f noise in bipolar transistors and JFETs.**\n"
     "- T. G. M. Kleinpenning, \"Low-frequency noise in modern bipolar transistors: impact of intrinsic transistor and "
     "parasitic series resistances\", *IEEE Trans. Electron Devices* 41(11), 1981–1991 (1994), "
     "https://doi.org/10.1109/16.333815.\n"
     "- H. A. W. Markus and T. G. M. Kleinpenning, \"Low-frequency noise in polysilicon emitter bipolar transistors\", "
     "*IEEE Trans. Electron Devices* 42(4), 720–727 (1995), https://doi.org/10.1109/16.372077.\n"
     "- S. P. O. Bruce, L. K. J. Vandamme and A. Rydberg, \"Measurement of low-frequency base and collector current "
     "noise and coherence in SiGe heterojunction bipolar transistors using transimpedance amplifiers\", *IEEE Trans. "
     "Electron Devices* 46(5), 993–1000 (1999), https://doi.org/10.1109/16.760408.\n"
     "- D. M. Fleetwood, \"1/f noise and defects in microelectronic materials and devices\", *IEEE Trans. Nucl. Sci.* "
     "62(4), 1462–1486 (2015), https://doi.org/10.1109/TNS.2015.2405852.\n"
     "- The notes on these and on the other sources read on 1/f noise, with page references, are in "
     "`refs/literature/bjt_1f_notes.md`.\n\n"
     "**Data sheets.**"),
    ("and BCP56 (BCP56T1/D, Rev. 16, 2024), in `refs/datasheets/bjt/`.",
     "and BCP56 (BCP56T1/D, Rev. 16, 2024); for Section 3.5, Analog Devices SSM2212 (Rev. C), MAT12 (Rev. A) and "
     "MAT14 (Rev. A), and the discontinued MAT02 (Rev. E) and MAT03 (Rev. C); Linear Systems LS3250A/B/C (Doc 201128 "
     "Rev A8), LS310–LS313 (Doc 201121 Rev A15), LS350–LS352 (Rev A5) and LS3550 (Doc 201129 Rev A6); THAT "
     "Corporation 300 Series (Doc 600041 Rev 04) and its memo \"End of Life for several THAT ICs\" of 1 September "
     "2026; National Semiconductor LM194/LM394 (TI literature SNLS385A, obsolete); and Rohm 2SB737 and 2SD786 (data "
     "book pp. 185–188); all in `refs/datasheets/bjt/`."),
]


def main() -> None:
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    assert "\r" not in text
    if "### 3.5 Bipolar input stages" in text:
        sys.exit("already patched: refusing a second run")
    assert "*Table 5." not in text and "![Figure 6]" not in text, "renumber first (patch_renumber_s3_5.py)"
    for old, new in EDITS:
        c = text.count(old)
        assert c == 1, (c, old[:90])
        text = text.replace(old, new)
    print(f"{len(EDITS)} edits applied to {path.name}")
    path.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
