# Bipolar transistor data sheets

Downloaded on 19 and 20 November 2026 for the current-sink studies (Sections 4.2.1 and 6.1 of the note, `scripts/sink_power.py`, `scripts/sink_options.py`).

| File | Source | Document |
|---|---|---|
| `onsemi_MMBT3904LT1_datasheet.pdf` | https://www.onsemi.com/pdf/datasheet/mmbt3904lt1-d.pdf | onsemi MMBT3904L, SMMBT3904L, publication MMBT3904LT1/D, Rev. 15, September 2026 (11 pp.). Read: p. 1 (maximum ratings: I_C 200 mA; P_D 225 mW on FR-5 at 25 °C, derate 1.8 mW/°C, R_θJA 556 °C/W; 300 mW on alumina) and p. 2 (h_FE 100–300 at 10 mA, 60 min at 50 mA). |
| `onsemi_BC817_datasheet.pdf` | https://www.onsemi.com/pdf/datasheet/bc817-16lt1-d.pdf | onsemi BC817-16L/-25L/-40L, publication BC817-16LT1/D, Rev. 19, September 2026 (14 pp.). Read: p. 1 (I_C 500 mA; the same P_D and R_θJA as the MMBT3904) and p. 2 (h_FE at 100 mA: 100–250 (-16), 160–400 (-25), 250–600 (-40); f_T ≥ 100 MHz; C_obo 10 pF). |
| `onsemi_PZT3904_datasheet.pdf` | https://www.onsemi.com/pdf/datasheet/pzt3904t1-d.pdf | onsemi PZT3904T1G, publication PZT3904T1/D, Rev. 7, October 2024 (8 pp.). Read: p. 1 (I_C 200 mA, V_CEO 40 V; P_D 1.5 W at 25 °C, derate 12 mW/°C, R_θJA 83.3 °C/W, all on FR-4 with 1 oz and 713 mm² of copper; R_θJL 35 °C/W) and p. 2 (the same electrical characteristics as the MMBT3904L: h_FE 100–300 at 10 mA, f_T ≥ 300 MHz, C_obo ≤ 5 pF). Downloaded 20 November 2026. |
| `onsemi_BCP56_datasheet.pdf` | https://www.onsemi.com/pdf/datasheet/bcp56t1-d.pdf | onsemi BCP56 series, publication BCP56T1/D, Rev. 16, August 2024 (6 pp.). Read: p. 1 (80 V, 1 A; P_D 1.5 W at 25 °C and R_θJA 83.3 °C/W on FR-4 1.575 in square with a 0.93 sq in collector pad). Downloaded 20 November 2026; not used in the design. |

A first attempt at Nexperia's BC817 series data sheet (assets.nexperia.com) returned an HTML page instead of the PDF; it was deleted.

## Matched pairs and low-noise transistors for Section 3.5 (downloaded on 24 November 2026)

Read for the bipolar input stages of Section 3.5 of the note (`scripts/bipolar_inputs.py`, `scripts/numbers_s3_5.py`). Production status as listed on the manufacturers' product pages on 24 November 2026; the pages read are the ones the note cites. The vendor SPICE models are kept for reference only and are not redistributed (`.gitignore`).

| File | Source | Document and pages read |
|---|---|---|
| `ADI_SSM2212_datasheet_RevC.pdf` | analog.com, SSM2212 product page | Analog Devices SSM2212, Rev. C (12 pp.); in production. Read: pp. 1, 3 (Table 1, SOIC), 4 (Table 2, LFCSP), 6 (Figs. 3–8: noise against frequency and against $I_C$, $h_{FE}$, $V_{BE}$). |
| `ADI_MAT12_datasheet_RevA_mirror-xdevs.pdf` | xdevs.com mirror, byte-identical to analog.com/media/en/technical-documentation/data-sheets/MAT12.pdf (SHA-256) | Analog Devices MAT12, Rev. A (12 pp.); in production. Read: pp. 1, 3 (Table 1), 5 (Figs. 2–7), 6 (Figs. 8–13). |
| `ADI_MAT14_datasheet_RevA.pdf` | analog.com, MAT14 product page | Analog Devices MAT14, Rev. A; in production. Read: p. 3 (Table 1). |
| `ADI_MAT02_datasheet_RevE_obsolete.pdf` | analog.com, obsolete products | Analog Devices MAT02, Rev. E (obsolete). Read: pp. 4–5 (TPC 1–17). |
| `ADI_MAT03_datasheet_RevC.pdf` | analog.com, obsolete products | Analog Devices MAT03, Rev. C (obsolete). Read: pp. 2, 5 (TPC 7–11), 7. |
| `ADI_SSM2220_datasheet_RevC.pdf` | analog.com, obsolete products | Analog Devices SSM2220, Rev. C (obsolete), with the MAT03's tables and curves. Not cited in the note. |
| `LIS_LS3250_datasheet_Doc201128_RevA8_2020-11-23.pdf` | linearsystems.com, LS3250 product page | Linear Systems LS3250A/B/C, Doc 201128 Rev A8, 23 November 2020 (5 pp.). Read: p. 2. |
| `LIS_LS310-LS313_datasheet_Doc201121_RevA15_2021-01-06.pdf` | linearsystems.com, LS310 product page | Linear Systems LS310–LS313, Doc 201121 Rev A15, 6 January 2021 (6 pp.). Read: p. 2. |
| `LIS_LS350-LS352_datasheet_RevA5_2020-10-14.pdf` | linearsystems.com, LS350 product page | Linear Systems LS350–LS352, Rev A5, 14 October 2020 (2 pp.). Read: p. 1. |
| `LIS_LS350_SPICE-model_Rev2_2026-07-27.pdf` | linearsystems.com, LS350 product page | Linear Systems LS350 SPICE model, Rev. 2, 27 July 2026 (1 p.): a Gummel–Poon card without KF or AF. |
| `LIS_LS3550_datasheet_Doc201129_RevA6_2020-10-14.pdf` | linearsystems.com, LS3550 product page | Linear Systems LS3550A/B/C, Doc 201129 Rev A6, 14 October 2020 (2 pp.). Read: p. 2. |
| `THAT_300-Series_datasheet_Doc600041_Rev04.pdf` | https://www.thatcorp.com/datashts/THAT_300-Series_Datasheet.pdf | THAT Corporation 300 Series, Doc 600041 Rev 04 (8 pp.). Read: p. 2 (NPN characteristics). |
| `THAT_EOL-Memo_2026-09-01.pdf` | https://www.thatcorp.com/wp-content/uploads/2026/09/THAT-EOL-Memo.pdf | THAT Corporation, "End of Life for several THAT ICs", 1 September 2026 (1 p.): the 300-series arrays on end-of-life status, last-time buy until 30 September 2026. Read in full. |
| `THAT_380G_die_datasheet_Doc600042_Rev03.pdf`, `THAT_DN109_MicPreamp_THAT320_Rev01_2017.pdf` | https://www.thatcorp.com/datashts/THAT_380G_Datasheet.pdf, https://www.thatcorp.com/datashts/dn109.pdf | THAT 380G die data sheet, Doc 600042 Rev 03; design note DN109 (a THAT 320 microphone preamplifier). Not cited in the note. |
| `THAT_MacroModels-Rev05.zip`, `THAT_300-Series_Macro_01_from-THATMacroModels-Rev05.lib` | thatcorp.com, macromodel package Rev 05 | THAT's SPICE macromodels (licensed for use, not redistributed): Gummel–Poon cards without KF or AF. |
| `NSC-TI_LM194-LM394_datasheet_SNLS385A_mirror-xdevs.pdf` | https://xdevs.com/doc/Keithley/2182A/doc/LM194%2C394.pdf | National Semiconductor LM194/LM394, TI literature SNLS385A (obsolete). Read: pp. 1, 3, 7 (base current noise against frequency). |
| `Rohm_2SB737_datasheet_databook-pp185-188_undated_mirror-radioradar.pdf`, `Rohm_2SD786_datasheet_JP_p1-only_undated_mirror-radioradar.pdf` | radioradar.net mirrors | Rohm 2SB737 (data book pp. 185–188) and 2SD786 (p. 1 only). Read: p. 188 (Figs. 13–15; $r_{bb'}$ of about 2 and 4 Ω). |
| `Toshiba_2SC3329_datasheet_1998-12-17_mirror-radioradar.pdf`, `Toshiba_2SA1316_datasheet_1997-04-10_mirror-radioradar.pdf` | radioradar.net mirrors | Toshiba 2SC3329 and 2SA1316. Not cited in the note. |
| `Diodes_ZTX851_datasheet_DS33311_Rev3-3_2026-08.pdf`, `Zetex-Diodes_ZTX951_datasheet_Issue4_1994-06.pdf` | diodes.com | Diodes ZTX851 (DS33311 Rev. 3-3) and Zetex ZTX951 (Issue 4). Not cited in the note. |
