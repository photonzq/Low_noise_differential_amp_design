"""Patch of low_noise_preamp.md after the four range patches of 21-22 November 2026 (patch_s1_3.py,
patch_s4a.py, patch_s4b_5.py, patch_s6_7.py): the wording that crosses ranges, the NF 5307's CMRR at
1 MHz after the pixel check, and the reference list.

  - 14.8 -> 14.85 MHz in Section 4.3 (the summary and Table 11 quote 14.85; chain_ac.json 14.849 MHz).
  - Section 7's heading: the common-mode loops' -180 deg crossings at 251 and 204 MHz, as in
    Sections 4.3 and 5 (numbers_s4a.json; numbers_s6_7.json 250.8 / 204.4 MHz).
  - Eq. (9)'s weights with the cards' source resistances (numbers_s4b_5.json: H100_trim_weight_ohm,
    H100_weight_closed_form_ohm, H_Ngm_effective_mS, L200_Ngm_effective_mS).
  - NF 5307 CMRR at 1 MHz: 86 -> 85 dB (numbers_s6_7.py, NF_CMRR_PLOT; nf5307_plot_check.json): the
    curve stops at about 0.9 MHz and the reading by eye had taken its end.
  - The plot readings' check named in the captions of Tables 12 and 15.
  - References: SR560 manual revision and pages; NF documents; x-Chapters section 2x.1; the BNL
    "ICFA95" slides and the ngspice-46 manual, both cited in the text; data sheets and models cited
    in the text but not listed.

Every edit is an exact-string replacement whose old text occurs exactly once.  The reference list
gains lines; nothing else does.  UTF-8 with \n newlines.  A second run is refused.
Usage: python patch_post.py <path to low_noise_preamp.md>
"""
from __future__ import annotations

import sys
from pathlib import Path

EDITS: list[tuple[str, str]] = [
    # ---- Section 4.3: the chain's bandwidth at a total gain of 100, as elsewhere -------------------
    ("to 14.8 MHz (`chain_ac.json`)", "to 14.85 MHz (`chain_ac.json`)"),
    # ---- Section 7: the crossings as in Sections 4.3 and 5 ------------------------------------------
    ("**The common-mode local loop near 250 MHz (H) and 205 MHz (L).**",
     "**The common-mode local loop at 251 MHz (H) and 204 MHz (L).**"),
    # ---- Section 4.2: Eq. (9)'s weights and the cards' source resistances ---------------------------
    ("Both weights are small here, because $Ng_m$ is large (2 × 17.3 = 35 mS per side for H and 12 × 25.7 "
     "= 308 mS for L, Table 5) and $R_G$ is small.",
     "Both weights are small here, because $Ng_m$ is large (2 × 17.3 = 35 mS per side for H and 12 × 25.7 "
     "= 308 mS for L, Table 5) and $R_G$ is small. In the models each JFET's source resistance (8 Ω in the "
     "JFE2140 card, 4.2 Ω in the JFE150's) adds to its $1/g_m$, so that the effective $Ng_m$ is 30.2 mS for H "
     "and 277 mS for L; with it, Eq. (9) gives the weight that the simulated noise of $R_D$ shows to within "
     "0.3 % (37.97 against 38.08 Ω for H at a gain of 100, `scripts/numbers_s4b_5.py`)."),
    # ---- NF 5307 CMRR at 1 MHz -----------------------------------------------------------------------
    ("against about 86 dB at 1 MHz and a gain of 100 in NF's plot",
     "against about 85 dB at 1 MHz and a gain of 100 in NF's plot"),
    ("| NF 5307 (plot, gain 100) | 136 | 136 | 126 | 107 | 86 | – |",
     "| NF 5307 (plot, gain 100) | 136 | 136 | 126 | 107 | 85 | – |"),
    ("beyond the NF 5307's 86 dB.", "beyond the NF 5307's 85 dB."),
    ("/ 86 dB (plot, gain 100)", "/ 85 dB (plot, gain 100)"),
    ("(`refs/commercial_preamps/NF_Corporation/NF_5307_datasheet_fig46.jpg`), read by eye at the table's "
     "frequencies.*",
     "(`refs/commercial_preamps/NF_Corporation/NF_5307_datasheet_fig46.jpg`), read by eye at the table's "
     "frequencies and checked against the image's pixels (`scripts/nf5307_plot_check.py`, within 0.4 dB up "
     "to 100 kHz). The curve stops at about 0.9 MHz; its value at 1 MHz is the straight-line extrapolation "
     "of its last 0.4 decade.*"),
    ("CMRR plot, Fig. 46 of NF's data-sheet page; the plots read by eye.",
     "CMRR plot, Fig. 46 of NF's data-sheet page; the plots read by eye and checked against the images' "
     "pixels (`scripts/nf5307_plot_check.py`)."),
    # ---- References -------------------------------------------------------------------------------------
    ("- Stanford Research Systems, *Model SR560 Low-Noise Preamplifier*, operating manual and programming "
     "reference, Rev. 2.8 (schematics on PDF pp. 46–56; specifications and noise table on printed pp. "
     "20–21), and the SR560 data sheet.",
     "- Stanford Research Systems, *Model SR560 Low-Noise Preamplifier*, operating manual and programming "
     "reference, Revision 3.1 (4/2023) (specifications chart on printed p. 5, PDF p. 9; input noise curve and "
     "noise table on printed pp. 20–21, PDF pp. 24–25; board layout on PDF p. 46 and schematics on PDF pp. "
     "47–56), and the SR560 data sheet."),
    ("- NF Corporation, 5307 differential amplifier: specifications, catalogue (2025) and instruction manual "
     "(English and Japanese; Fig. 4.7 noise, Fig. 46 CMRR); NF technical note on preamplifiers (2020). "
     "Further instruments in `refs/commercial_preamps/survey.md`.",
     "- NF Corporation, 5307 differential amplifier: specifications sheet, catalogue (current as of 1 April "
     "2025), *5307 Differential Amplifier Operation Manual* (English edition, D: 507571: Section 3.2.1 on PDF "
     "p. 21; Fig. 4.7, equivalent input noise density, on printed p. 25, PDF p. 37; Section 5.1, input "
     "specifications, on printed p. 31, PDF p. 43; and the Japanese edition), and the CMRR plot, Fig. 46, of "
     "NF's 5307 data-sheet web page; NF technical note on preamplifiers (2020). The two plots are read in "
     "`scripts/nf5307_plot_check.py`. Further instruments in `refs/commercial_preamps/survey.md`."),
    ("- W. Hill and P. Horowitz, *The Art of Electronics: The x-Chapters*, Cambridge University Press, 2020, "
     "§3x.4.6 \"A low-noise open-loop differential amplifier\" (table of contents only).",
     "- W. Hill and P. Horowitz, *The Art of Electronics: The x-Chapters*, Cambridge University Press, 2020: "
     "§2x.1 \"What's the Actual Leakage Current of BJTs and JFETs?\", p. 102 (read in the authors' free "
     "sample of that section), and §3x.4.6 \"A low-noise open-loop differential amplifier\" (table of "
     "contents only)."),
    ("- W. M. Leach, Jr., \"Fundamentals of low-noise analog circuit design\", *Proc. IEEE* 82(10), "
     "1515–1538 (1994), https://doi.org/10.1109/5.326411.\n",
     "- W. M. Leach, Jr., \"Fundamentals of low-noise analog circuit design\", *Proc. IEEE* 82(10), "
     "1515–1538 (1994), https://doi.org/10.1109/5.326411.\n"
     "- Brookhaven National Laboratory, Instrumentation Division, \"Capacitive matching for MOSFET "
     "Charge-Sensitive Preamplifiers with Constant Current\" (the \"ICFA95\" slides; author not stated), "
     "originally at http://www.inst.bnl.gov/programs/microelec/PDF/ICFA95.fm.pdf, read from the University "
     "of North Texas web-archive capture of 16 September 2008.\n"),
    ("- JFETs: TI JFE150 (SLPS732B), JFE2140 (SLPS730B), JFE2325 (SLPS816A); Linear Systems LSK389 (Doc 201122 "
     "Rev A27), LSK170, LSK489, LSBF862 (Doc 201195 Rev A2); InterFET IF3601, IF4500,",
     "- JFETs: TI JFE150 (SLPS732B), JFE2140 (SLPS730B), JFE2325 (SLPS816A); Linear Systems LSK389 (Doc 201122 "
     "Rev A27), LSK170, LSK489, LSBF862 (Doc 201195 Rev A2); InterFET IF3601 (IF35076.R01), IF4500,"),
    ("LM7171 (SNOS760D), OPA1612, OPA2810, OPA855; and the others in `refs/datasheets/opamp/README.md`.",
     "LM7171 (SNOS760D), OPA1612 (SBOS450C), OPA2810 (SBOS789C), OPA855; and the others in "
     "`refs/datasheets/opamp/README.md`."),
    ("- Regulators: Analog Devices LT3094 (Rev. 0, 2018, read from a public mirror) and the LT3045 product page "
     "(read on 19 November 2026; data sheet Rev. D not downloaded); TI TPS7A47, TPS7A33, TPS7A94.",
     "- Analog switches: TI TMUX6219 (SCDS420E), and the others in `refs/datasheets/switches/README.md`.\n"
     "- Regulators: Analog Devices LT3045 (Rev. D, 2022) and LT3094 (Rev. 0, 2018, read from a public mirror; "
     "Rev. B, 2020, also archived), in `refs/literature/` and `refs/datasheets/regulators/`; TI TPS7A47 "
     "(SBVS204G), TPS7A33 (SBVS169D), TPS7A94 (SBVS336C)."),
    ("onsemi MMBT3904 and MMBTH10. Sources and dates in `sim/models/README_*.md`.",
     "onsemi MMBT3904 and MMBTH10; NXP's BF862 model (`BF862.prm`, file header of March 2007), transcribed in "
     "`sim/models/README_InterFET_NXP_others.md` but not archived. Sources and dates in "
     "`sim/models/README_*.md`.\n\n"
     "**Simulator.** H. Vogt, G. Atkinson, D. Warning and P. Nenzi, *Ngspice User's Manual*, Version 46, "
     "31 March 2026, §7.4.4 (the JFET level 1 model), pp. 152–154 "
     "(`refs/literature/ngspice_2026_Users_Manual_v46.pdf`)."),
]


def main() -> None:
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    assert "\r" not in text
    if "**The common-mode local loop at 251 MHz (H) and 204 MHz (L).**" in text:
        sys.exit("already patched: refusing a second run")
    n_lines = text.count("\n")
    added = 0
    for old, new in EDITS:
        c = text.count(old)
        assert c == 1, (c, old[:90])
        added += new.count("\n") - old.count("\n")
        text = text.replace(old, new)
    assert text.count("\n") == n_lines + added
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"{len(EDITS)} replacements applied to {path.name}; {added} lines added (reference list)")


if __name__ == "__main__":
    main()
