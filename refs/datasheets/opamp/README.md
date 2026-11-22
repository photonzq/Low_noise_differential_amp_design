# Op-amp and buffer data sheets

All files were downloaded on 2026-11-19 with curl. Each one is the vendor's current revision on that date.

| File | URL | Document / revision |
|---|---|---|
| TI_ths4631_datasheet.pdf | https://www.ti.com/lit/ds/symlink/ths4631.pdf | SLOS451D (Dec 2004, rev. Mar 2026) |
| TI_ths4021_datasheet.pdf | https://www.ti.com/lit/ds/symlink/ths4021.pdf | SLOS265F (Aug 1999, rev. Jul 2024): p. 1 (stable at gains ≥ 10 V/V, 2 GHz gain–bandwidth, 1.2 nV/√Hz), §5.6 p. 6 (bandwidth, noise), p. 7 (V_O ±12 V min into 250 Ω, I_O 80 mA min, C_i 1.5 pF), §5.7 p. 8 (DGN package: 1.5 nV/√Hz) |
| TI_ths4031_datasheet.pdf | https://www.ti.com/lit/ds/symlink/ths4031.pdf | SLOS224L (Jun 1999, rev. Jul 2024) |
| TI_ths3091_datasheet.pdf | https://www.ti.com/lit/ds/symlink/ths3091.pdf | SLOS423K (Sep 2003, rev. Apr 2023) |
| TI_ths3001_datasheet.pdf | https://www.ti.com/lit/ds/symlink/ths3001.pdf | SLOS217I (Jul 1998, rev. Dec 2024) |
| TI_lm7171_datasheet.pdf | https://www.ti.com/lit/ds/symlink/lm7171.pdf | SNOS760D (May 1999, rev. Feb 2024) |
| TI_buf634a_datasheet.pdf | https://www.ti.com/lit/ds/symlink/buf634a.pdf | SBOS948F (Feb 2019, rev. May 2021) |
| TI_opa2810_datasheet.pdf | https://www.ti.com/lit/ds/symlink/opa2810.pdf | SBOS789C (Aug 2017, rev. Feb 2020) |
| TI_opa1611-opa1612_datasheet.pdf | https://www.ti.com/lit/ds/symlink/opa1611.pdf and https://www.ti.com/lit/ds/symlink/opa1612.pdf (byte-identical; one copy kept) | SBOS450C (Jul 2009, rev. Aug 2014) |
| TI_opa2210_datasheet.pdf | https://www.ti.com/lit/ds/symlink/opa2210.pdf | SBOS924H (Sep 2018, rev. Aug 2021) |
| TI_opa828_datasheet.pdf | https://www.ti.com/lit/ds/symlink/opa828.pdf | SBOS671D (Sep 2018, rev. Dec 2022) |
| TI_opa1656_datasheet.pdf | https://www.ti.com/lit/ds/symlink/opa1656.pdf | SBOS901C (Mar 2019, rev. Sep 2022) |
| TI_opa855_datasheet.pdf | https://www.ti.com/lit/ds/symlink/opa855.pdf | SBOS622D (Jul 2018, rev. May 2025) |
| TI_opa858_datasheet.pdf | https://www.ti.com/lit/ds/symlink/opa858.pdf | SBOS629B (Apr 2018, rev. May 2025) |

## Not downloaded

www.analog.com reset every automated connection on 2026-11-19, so the following were not downloaded. Get them from the product pages:
- AD8021 — https://www.analog.com/en/products/ad8021.html
- ADA4898-1 — https://www.analog.com/en/products/ada4898-1.html
- ADA4625-1 — https://www.analog.com/en/products/ada4625-1.html
- AD797 — https://www.analog.com/en/products/ad797.html
- ADA4870 — https://www.analog.com/en/products/ada4870.html
- ADA4807 — https://www.analog.com/en/products/ada4807-1.html
- ADA4899-1 — https://www.analog.com/en/products/ada4899-1.html
- LTC6228 — https://www.analog.com/en/products/ltc6228.html

## Added 2026-11-22: the op amps of the SR560 reproduction

Obtained on 2026-11-22. www.analog.com still refuses connections from curl, so the two Analog Devices files are the Internet Archive's copies of the ADI URLs; each is byte-identical (SHA-256 below) to the file the ADI URL served to a web browser on 2026-11-22, and the ADI product pages (analog.com/en/products/op37.html, /lt1028.html) list that file as the current data sheet. TI no longer publishes the LF411-N or the LM6321 (both symlink URLs return 404); those files, and TI's previous LF411 revision, are the Internet Archive's copies of TI's own URLs. The TI files whose URL is given without an archive copy were downloaded from ti.com with curl. Page numbers are printed page numbers; they equal the PDF page numbers except in TI_lm6321_datasheet.pdf, where a TI cover sheet comes first (printed p. N = PDF p. N + 1).

| File | URL | Document / revision |
|---|---|---|
| ADI_op37_datasheet.pdf | https://www.analog.com/media/en/technical-documentation/data-sheets/op37.pdf (copy: https://web.archive.org/web/20260215224947id_/https://www.analog.com/media/en/technical-documentation/data-sheets/OP37.pdf) | Analog Devices OP37 Rev. B, C00319-0-12/02(B) (Dec 2002): p. 3 Specifications (e_n, i_n, A_VO, SR, GBW 63 MHz at 10 kHz and 40 MHz at 1 MHz, R_O 70 Ω), p. 7 TPC 2 and TPC 8 (1/f corners 2.7 Hz, 140 Hz), p. 8 TPC 16-18 (open-loop gain and phase) |
| ADI_lt1028_datasheet.pdf | https://www.analog.com/media/en/technical-documentation/data-sheets/1028fd.pdf (copy: https://web.archive.org/web/20261013161701id_/https://www.analog.com/media/en/technical-documentation/data-sheets/1028fd.pdf) | LT1028/LT1128 Rev. D, 1028fd (Rev. D 10/15): p. 1 Voltage Noise vs Frequency (1/f corner 3.5 Hz), p. 3 Electrical Characteristics, p. 6 Current Noise Spectrum (250 Hz), p. 8 Gain, Phase vs Frequency, p. 15 Frequency Response |
| TI_lf356_datasheet.pdf | https://www.ti.com/lit/ds/symlink/lf356.pdf | SNOSBH0D (LF155/LF156/LF256/LF257/LF355/LF356/LF357; May 2000, rev. Nov 2015): p. 5 §6.5 AC Electrical Characteristics, p. 6 §6.7, p. 10 Figures 14 and 17, p. 11 Figure 24, p. 12 Figure 26 (Bode plot), p. 13 Figures 32-33 (noise) |
| TI_lf411_datasheet.pdf | https://www.ti.com/lit/ds/symlink/lf411.pdf | SLOS011D (Mar 1987, rev. Oct 2025): pp. 3-4 §5.3; p. 5 revision history (a FET-input redesign: B1 4.5 MHz, SR 0.5 V/µs, 10.8 nV/√Hz, 2 fA/√Hz) |
| TI_lf411_datasheet_SLOS011C.pdf | https://web.archive.org/web/20250128132910id_/https://www.ti.com/lit/ds/symlink/lf411.pdf (TI's URL as of 2025-01-28) | SLOS011C (JFET-input LF411; Mar 1987, rev. Oct 1997), superseded by SLOS011D: p. 2 electrical characteristics, p. 3 operating characteristics (3 MHz, 13 V/µs, 18 nV/√Hz, 0.01 pA/√Hz) |
| TI_lf411-n_datasheet.pdf | https://www.ti.com/lit/ds/symlink/lf411-n.pdf, withdrawn (copy: https://web.archive.org/web/20171030222708id_/http://www.ti.com:80/lit/ds/symlink/lf411-n.pdf) | SNOSBH6E (LF411-N, the National Semiconductor LF411; Apr 1998, rev. Oct 2014): p. 1 Features (1/f corner 50 Hz), p. 5 §6.5-6.6 (the model's LF411 figures), p. 7 Figures 10-12 (Bode plot), p. 8 Figure 18 (noise) |
| TI_lm6321_datasheet.pdf | https://www.ti.com/lit/ds/symlink/lm6321.pdf, withdrawn (copy: https://web.archive.org/web/20120813042038id_/http://www.ti.com:80/lit/ds/symlink/lm6321.pdf) | SNOSC10B (LM6121/LM6221/LM6321, TI listing date 3 Oct 2011; National data sheet 9223 Version 4 Revision 1, marked obsolete 3 Oct 2011), the last version TI published: printed p. 3 DC and p. 4 AC Electrical Characteristics (-3 dB bandwidth 50 MHz) |
| TI_opa37_datasheet.pdf | https://www.ti.com/lit/ds/symlink/opa37.pdf | SBOS135D (OPA27, OPA37; Jan 1984, rev. Oct 2026): p. 5 §5.3 (GBW 33 MHz, SR 11 V/µs, e_n 3 nV/√Hz, i_n 0.4 pA/√Hz); the plots on pp. 7-8 are labelled "Legacy Die". Kept because the SR560 parts list (manual Rev. 2.8, PDF p. 43) names U102, U201, U305 and U403 "OPA37" (SRS 3-00382-340), while the schematics say OP37; not used by the model |

SHA-256 (bytes): ADI_op37_datasheet.pdf 18823f402e631d64eadee4a256f3ea3cd5dfdc97a47edf1db325a4aae53da838 (574 818); ADI_lt1028_datasheet.pdf 27731e02a9b187d0b5e022d6da7ef0cb843b4ffb20ffc884d0ddda9326fcae67 (730 011); TI_lf356_datasheet.pdf b7bfdd210bd856300cc527fead5de3d726a01f01d5c7adc24ff9b0428aa60c29 (2 187 683); TI_lf411_datasheet.pdf a0240b42c30a83c2c0223a0a004e887c325d4d0328314151b959aa4a5d496e10 (817 866); TI_lf411_datasheet_SLOS011C.pdf 2eaf67e030faa8e427a16dcc8b74ee83a61a8157df8a8319b1b000f82570fac7 (474 306); TI_lf411-n_datasheet.pdf 0add78f34c5d44619f56aa775dc56faa363218bb4f28729fed34454f7d87cbe0 (953 672); TI_lm6321_datasheet.pdf 338e52625022127aaee0d0c40cd46e417fd6b345bf6c9878c4b9d4bc2490b3fc (489 309); TI_opa37_datasheet.pdf 9613373cb041f36c1a2f02a7e2988bcaede844d216edeca88d5b7a62dca5cfff (1 691 699).
