# Models of the low-noise preamplifier note

The vendors' SPICE models are not redistributed with the note; each must be downloaded from its vendor (the sources, revisions and dates are in the two survey READMEs below) and saved under the name given there. `../../scripts/models.py` then writes ngspice-ready copies into `_lib/`, and documents every change it makes and why.

| Folder or file | Content | Sources |
|---|---|---|
| `TI/` | TI JFET models: JFE150 (SLPM349I), JFE2140 (SLPM355), JFE2325 (SLVMF24) | `README_TI_LIS_Toshiba_onsemi.md` |
| `LinearSystems/` | Linear Systems' published cards (LSBF862 Rev 2, LSK389, LSK170, LSK489, LSJ689, LS844, 2N5564) as PDFs | `README_TI_LIS_Toshiba_onsemi.md`, `README_InterFET_NXP_others.md` |
| `InterFET/`, `Nexperia/`, `onsemi/` | further JFET models (not used in the design; no 1/f noise in the InterFET models) | `README_InterFET_NXP_others.md`, `README_TI_LIS_Toshiba_onsemi.md` |
| `onsemi_bjt/` | onsemi MMBT3904, MMBTH10, MMBTH81, MMBT2369, MMBT3906 (`https://www.onsemi.com/download/models/lib/<part>.lib`); the MMBT3904 file lacks its `.MODEL` line, which `models.py` adds | – |
| `vendor_opamps_raw/` | the op-amp model archives as downloaded, with `README.md` (URLs, revisions, pin orders) | `vendor_opamps_raw/README.md` |
| `vendor_opamps/` | the model files extracted from those archives, unchanged | as above |
| `_lib/` | written by `models.py`: `jfets.lib` (calibrated wrappers), `opamps.lib` (translated, noise-corrected wrappers `OA_<part>`), `bjts.lib` | – |

Corrections made by `models.py` (Section 5.3 of the note, Table 8):

- **JFETs.** Every JFET card is wrapped with a gate resistor RX that sets its white noise to the data sheet's typical value, KF is refitted to the data sheet's 10 Hz value (JFE2140: 0.2e-18 → 2.9e-18; LSBF862: 8.75e-17 → 1.74e-18; 2N5564 from LTspice's library: 6.786e-11 → 4.3e-16), and CGS and CGD are solved from the data sheet's $C_{iss}$ and $C_{rss}$ at its bias. LTspice-only parameters (NLEV, GDSNOI, MFG, ISR, NR, ALPHA, VK, M, MJ, ZXTI) are removed. The calibration results are in `../results/jfet_calibration.json`.
- **Op amps.** THS4021 and THS4031: all KF set to zero and 1/f voltage and current generators added to match the data sheets (4 nV/√Hz and 20 pA/√Hz at 10 Hz). THS3091: KF set to zero, white inverting- and non-inverting-input current noise added (13.9 and 15 pA/√Hz), and 1/f generators of 6.4 nV/√Hz, 199.5 pA/√Hz and 98.9 pA/√Hz at 10 Hz. LM7171: white voltage noise of 7.45 nV/√Hz and a 1/f generator of 42.2 nV/√Hz at 10 Hz added. PSpice constructs are translated (T_ABS noiseless resistors to `noisy=0`, CAP to C).
