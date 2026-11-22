# Bipolar transistor data sheets

Downloaded on 19 and 20 November 2026 for the current-sink studies (Sections 4.2.1 and 6.1 of the note, `scripts/sink_power.py`, `scripts/sink_options.py`).

| File | Source | Document |
|---|---|---|
| `onsemi_MMBT3904LT1_datasheet.pdf` | https://www.onsemi.com/pdf/datasheet/mmbt3904lt1-d.pdf | onsemi MMBT3904L, SMMBT3904L, publication MMBT3904LT1/D, Rev. 15, September 2026 (11 pp.). Read: p. 1 (maximum ratings: I_C 200 mA; P_D 225 mW on FR-5 at 25 °C, derate 1.8 mW/°C, R_θJA 556 °C/W; 300 mW on alumina) and p. 2 (h_FE 100–300 at 10 mA, 60 min at 50 mA). |
| `onsemi_BC817_datasheet.pdf` | https://www.onsemi.com/pdf/datasheet/bc817-16lt1-d.pdf | onsemi BC817-16L/-25L/-40L, publication BC817-16LT1/D, Rev. 19, September 2026 (14 pp.). Read: p. 1 (I_C 500 mA; the same P_D and R_θJA as the MMBT3904) and p. 2 (h_FE at 100 mA: 100–250 (-16), 160–400 (-25), 250–600 (-40); f_T ≥ 100 MHz; C_obo 10 pF). |
| `onsemi_PZT3904_datasheet.pdf` | https://www.onsemi.com/pdf/datasheet/pzt3904t1-d.pdf | onsemi PZT3904T1G, publication PZT3904T1/D, Rev. 7, October 2024 (8 pp.). Read: p. 1 (I_C 200 mA, V_CEO 40 V; P_D 1.5 W at 25 °C, derate 12 mW/°C, R_θJA 83.3 °C/W, all on FR-4 with 1 oz and 713 mm² of copper; R_θJL 35 °C/W) and p. 2 (the same electrical characteristics as the MMBT3904L: h_FE 100–300 at 10 mA, f_T ≥ 300 MHz, C_obo ≤ 5 pF). Downloaded 20 November 2026. |
| `onsemi_BCP56_datasheet.pdf` | https://www.onsemi.com/pdf/datasheet/bcp56t1-d.pdf | onsemi BCP56 series, publication BCP56T1/D, Rev. 16, August 2024 (6 pp.). Read: p. 1 (80 V, 1 A; P_D 1.5 W at 25 °C and R_θJA 83.3 °C/W on FR-4 1.575 in square with a 0.93 sq in collector pad). Downloaded 20 November 2026; not used in the design. |

A first attempt at Nexperia's BC817 series data sheet (assets.nexperia.com) returned an HTML page instead of the PDF; it was deleted.
