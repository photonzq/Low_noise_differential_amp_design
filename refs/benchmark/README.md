# The benchmark: SR560 documents

| File | Source | What it is |
|---|---|---|
| `SRS_SR560_manual.pdf` | https://www.thinksrs.com/downloads/pdfs/manuals/SR560m.pdf | Stanford Research Systems, *Model SR560 Low-Noise Preamplifier*, operating manual, Revision 3.1 (4/2023), 56 pp.; byte-identical to the file on SRS's site on 23 November 2026. U106 is listed as the NPD5564 in the circuit description (PDF p. 17), the repair section (PDF p. 21) and the parts list (PDF p. 43). |
| `SRS_SR560_datasheet.pdf` | https://www.thinksrs.com/downloads/pdfs/catalog/SR560c.pdf | SRS SR560 data sheet, 3 pp.; byte-identical to the file on SRS's site on 23 November 2026. |
| `EEVblog_SR560_noise_calculation_thread_2024.html` | https://www.eevblog.com/forum/testgear/sr560_noise-calculation/ | EEVblog forum thread "SR560 Low noise amp -- Noise Calculation", first post 18 March 2024, saved 23 November 2026. The poster opened two SR560s of different serial numbers and found an LSK389B as the front-end pair of the newer one and the NPD5564 in the older one; after the manual's CMRR and offset adjustments they measured about 3.5 and 4.0 nV/√Hz at 1 kHz at a gain of 1000 (Audio Precision APx515). A user report, not an SRS document. |

The files are not redistributed in the repository (see the top-level README); each is listed here with its source.
