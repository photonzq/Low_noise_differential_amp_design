# JFET survey: Texas Instruments, Linear Integrated Systems, Toshiba (incl. parts listed as Hitachi), onsemi

Compiled 2026-11-19 for the low-noise differential preamplifier design (DC–10 MHz; high-impedance front end with 20–40 pF source capacitance; paralleled-JFET front end for 0.3–1 nF sources).

## Conventions

- "p.N" is the PDF page index (1-based) of the cited file. Where the printed page number differs (Toshiba data-book pages), the printed number is also given.
- All files cited are in `refs/datasheets/jfet/<vendor>/` (relative to the project folder); file names are listed in `README_TI_LIS_Toshiba_onsemi.md`.
- "read by eye" marks values read off a plotted curve; they carry roughly ±10 % (linear axes) or ±20 % (log axes) reading uncertainty.
- "not given" means the opened document does not state the quantity.
- Unless stated otherwise, $e_n$ is input-referred voltage noise density in nV/$\sqrt{\text{Hz}}$, $T_A = 25\,^\circ$C.
- 1/f corner "from table" is computed as $f_c = f_{lo}\left[(e_{n,lo}/e_{n,1k})^2 - 1\right]$, assuming $e_n^2 = e_w^2 (1 + f_c/f)$ and treating the 1 kHz value as the white level $e_w$. It is a derived number, not a datasheet value.
- NF-to-$e_n$ conversions are marked "derived" and use $e_n = \sqrt{(10^{NF/10}-1)\,4kTR_G}$ with $T = 290$ K, neglecting the device current noise (valid for the low $R_G$ used in those tests). They are rough because NF is printed or plotted to about ±0.1–0.5 dB.
- Figure of merit used in the summary: $e_n\sqrt{C_{iss}}$ in nV/$\sqrt{\text{Hz}}\cdot\sqrt{\text{pF}}$. For $N$ identical devices paralleled on a source capacitance $C_s$, the capacitive-matching optimum ($N C_{iss} \approx C_s$) gives an input-referred noise proportional to $e_n\sqrt{C_{iss}}$, so a lower product means lower achievable noise for a given source capacitance. Datasheet $C_{iss}$ conditions differ between vendors (often $V_{GS}=0$), so the products are indicative only.

---

## 1. Texas Instruments

### 1.1 JFE150 (TI_JFE150_datasheet_SLPS732B.pdf; SLPS732B, June 2021, revised April 2023)

- Polarity / type: N-channel, single, discrete JFET (title, p.1).
- Packages: SOT-23-5 (DBV), SC70-5 (DCK) (p.4 thermal table; ti.com product page). Extra pins VCH/VCL are ESD clamp-diode rails.
- Status: Active (ti.com/product/JFE150, read 2026-11-19). Price/stock: not checked.
- $I_{DSS}$: 24 min / 35 typ / 46 max mA ($V_{DS}=10$ V, $V_{GS}=0$); 22–57 mA over −40…125 °C (p.5, §6.5).
- $V_{GS(off)}$ ($V_{GSC}$): −1.5 min / −1.2 typ / −0.9 max V ($V_{DS}=10$ V, $I_{DS}=0.1\,\mu$A) (p.5). $V_{GS}$ at 2 mA: −1.1 to −0.5 V; at 100 µA: −1.3 to −0.7 V (p.5).
- $g_m$: 3 mS typ at 100 µA; 18 mS typ at 2 mA ($V_{DS}=10$ V) (p.5). $G_{FS}$ (full conduction, $V_{GS}=0$): 55 / 68 / 80 mS (p.5).
- $g_m$ vs $I_D$ (Fig. 6-4, p.6, $V_{DS}=5$ V, read by eye): ≈11 mS at 1 mA, ≈16 mS at 2 mA, ≈19.5 mS at 3 mA, ≈24 mS at 5 mA, ≈29 mS at 9 mA, ≈33 mS at 15 mA.
- $e_n$ (p.5, $V_{DS}=5$ V): 100 µA: 3 (10 Hz), 2 (1 kHz); 2 mA: 1.6 (10 Hz), 0.9 (1 kHz); 5 mA: 1.8 (10 Hz), 0.8 (1 kHz). 0.1–10 Hz: 0.19 / 0.09 / 0.13 µV$_{pp}$ at 0.1 / 2 / 5 mA. All typical; no maximum given.
- $e_i$: 1.8 fA/$\sqrt{\text{Hz}}$ at 1 kHz, $V_{DS}=5$ V (p.5).
- $e_n$ vs $f$ (Fig. 6-9, p.7, read by eye): 2 mA curve ≈25 nV at 0.1 Hz, ≈1.0 at 100 Hz, ≈0.9 flat above ~300 Hz; 5 mA curve ≈0.75 flat. 1/f corner from table: ≈22 Hz (2 mA), ≈41 Hz (5 mA), ≈12 Hz (0.1 mA).
- $e_n$ vs $I_D$ at 1 kHz (Fig. 6-11, p.7, read by eye): ≈2.6 at 0.05 mA, ≈1.7 at 0.2 mA, ≈1.05 at 1 mA, ≈0.9 at 2 mA, ≈0.82 at 4–7 mA, rising to ≈1.0 at 20 mA.
- Capacitance (p.5): $C_{iss}$ 30 pF ($V_{DS}=0$), 24 pF ($V_{DS}=5$ V); $C_{rss}$ 7 pF ($V_{DS}=0$); $C_{oss}$ 8 pF ($V_{DS}=5$ V). Default condition $I_{DS}=2$ mA per table header.
- Capacitance vs $V_{DS}$ (Fig. 6-12, p.7, read by eye): $C_{iss}$ ≈29.5 pF at 0.5 V, ≈27.5 at 1 V, ≈23 at 10 V, ≈19.5 at 40 V; $C_{rss}$ ≈7 pF at 0.5 V, ≈3.5 at 10 V, ≈1.3 at 40 V; $C_{oss}$ ≈10.5 → ≈5 pF over 0.5–40 V.
- Gate current (p.5): 0.2 pA typ, ±10 pA max at $V_{DS}=2$ V, $V_{GS}=-0.7$ V; 0.2 pA typ at $V_{DS}=0$, $V_{GS}=-30$ V, ±2 nA max (−40…85 °C), ±10 nA max (−40…125 °C).
- Gate current vs $V_{DS}$ (Fig. 6-5, p.6, log axis in nA, read by eye): ≈0.5–1 pA for $V_{DS}\le 5$ V; impact-ionization rise starts at ≈6 V; at 8 V ≈50 pA (1 mA) to ≈0.4 nA (10 mA); at 10 V ≈1 nA (1 mA), ≈2–3 nA (2 mA), ≈6 nA (10 mA); ≈1–10 µA at 30–40 V. Practical consequence: keep $V_{DS}\lesssim 5$ V (cascode).
- $R_{IN}$: 1 TΩ typ (p.5).
- Breakdown / ratings: $V_{GSS}$ breakdown −40 V max-spec (p.5); $V_{DSS}\ge 40$ V (p.5); abs. max $V_{DS}$ ±40 V, $V_{GS},V_{GD}$ −40…+0.9 V, $I_{DS}$ ±50 mA, $I_{GS}$ ±20 mA (p.4, §6.1). $P_D$: not given; $R_{\theta JA}$ 183.8 °C/W (DBV), 197.1 °C/W (DCK) (p.4).
- SPICE: TI SLPM349 Rev I (PSpice), SLPM366 (generic SPICE), SLPM350 Rev B (TINA); identical model card (see `sim/models/README_TI_LIS_Toshiba_onsemi.md`): `BETA=31m VTO=-975m LAMBDA=16.95m RD=3.5 RS=4.2 CGS=20.3p CGD=6.3p PB=0.705 FC=0.5 KF=3.25e-18 AF=1`, plus weak/strong corner models.
- App notes: SLPA018 (Oct 2021) analyses a JFE150 composite preamp; its noise plot (Fig. 3-1) is a simulation, not a device measurement (text, p.1/p.9 list of figures). SLPU009 (EVM guide, Feb 2022) contains circuit/BOM/layout; no device characterization was found by text search.

### 1.2 JFE2140 (TI_JFE2140_datasheet_SLPS730B.pdf; SLPS730B, August 2021, revised August 2023)

- Type: N-channel, matched monolithic dual (title, p.1). Packages: SOIC-8 (D), WSON-8 (DSG) (p.3).
- Status: Active (ti.com/product/JFE2140, read 2026-11-19). The product page states the JFE150 is the single-channel version.
- $I_{DSS}$: 12 / 18 / 23 mA ($V_{GS}=0$); 10–28 mA over −40…125 °C; $I_{DSS1}/I_{DSS2}$ 0.95–1.05 (p.5, §6.5).
- $V_{GS(off)}$: −1.5 / −1.15 / −0.9 V ($V_{DS}=10$ V, 0.1 µA); $V_{GS}$ at 2 mA −1.1 / −0.6 / −0.5 V (p.5).
- $g_m$: 2.1 mS (100 µA), 10 mS (2 mA); $G_{FS}$ 24 min / 30 typ mS ($V_{GS}=0$) (p.5). Fig. 6-4 (p.6, read by eye, $V_{DS}=10$ V): ≈8.3 mS at 1 mA, ≈11.5 at 2 mA, ≈13.8 at 3 mA, ≈16.8 at 5 mA, ≈21 at 10 mA. SBOA563 p.3 states a measured $g_m$ ≈7.5 mS at 1 mA.
- $e_n$ (p.5, $V_{DS}=10$ V per table header): 100 µA: 2.5 (1 kHz), 5.4 (10 Hz), 0.26 µV$_{pp}$ (0.1–10 Hz); 2 mA: 1.1 (1 kHz), 2.4 (10 Hz), 0.12 µV$_{pp}$. Feature list p.1: 0.9 nV/$\sqrt{\text{Hz}}$ at 5 mA. $e_i$ 1.6 fA/$\sqrt{\text{Hz}}$ (1 kHz, 2 mA, $V_{DS}=5$ V).
- $e_n$ vs $f$ (Fig. 6-14, p.8, read by eye): 2 mA ≈12 nV at 0.1 Hz, ≈1.3 at 100 Hz, ≈1.15 flat above ~300 Hz; 5 mA ≈0.9 flat. 1/f corner from table ≈38 Hz (2 mA), ≈37 Hz (0.1 mA).
- $e_n$ vs $I_D$ at 1 kHz (Fig. 6-16, p.8, read by eye): ≈3.3 (0.05 mA), ≈2.6 (0.1), ≈1.9 (0.2), ≈1.5 (0.5), ≈1.3 (1), ≈1.07 (2), ≈0.9 (5), ≈1.25 (10 mA).
- Capacitance (p.5): $C_{iss}$ 17 pF ($V_{DS}=0$), 13 pF ($V_{DS}=5$ V); $C_{oss}$ 4.5 pF (2 mA); $C_{rss}$ not in the table. Fig. 6-17 (p.8, read by eye): $C_{iss}$ ≈17 pF at 0.5 V, ≈13 at 10 V, ≈11.5 at 40 V; $C_{rss}$ ≈5.3 pF at 0.5 V, ≈3.5 at 10 V, ≈2.5 at 40 V.
- Gate current (p.5): 1 pA typ, ±10 pA max at $V_{DS}=2$ V; 0.2 pA typ / ±60 pA max at $V_{DS}=0$, $V_{GS}=-30$ V; 0.85 nA (−40…85 °C), 9 nA (−40…125 °C) max.
- Gate current vs $V_{DS}$ (Fig. 6-6, p.6, read by eye): ≈0.5 pA below ≈6 V; ≈1 nA (1 mA) to ≈10 nA (10 mA) at 10 V. Same curve reproduced in SBOA589 Fig. 5 (p.5).
- Matching (p.5): $\Delta V_{GS}$ 1 typ / 4 max mV (2 mA); 1.1 / 4.2 mV over −40…125 °C; drift 1.7 typ / ±10 max µV/°C.
- Ratings (p.4): $V_{DS}$ ±40 V; $V_{GS},V_{GD}$ −40…+0.1 V; $I_{DS}$ ±50 mA; $V_{DSS}$ 40 min / 43 typ V (p.5). $P_D$: not given.
- SPICE: SLPM355 (PSpice) / SLPM357 (TINA), model `JFEx140` (one half of the pair): `BETA=14.24m VTO=-975m LAMBDA=11.9m RD=10 RS=8 CGS=9.2p CGD=3.5p PB=0.705 FC=0.5 KF=0.2e-18 AF=1`. See contradiction C9.

### 1.3 JFE2325 (TI_JFE2325_datasheet_SLPS816A.pdf; SLPS816A, January 2026, revised June 2026) — newest TI discrete JFET found

- Type: N-channel monolithic matched dual with self-biased gates (integrated gate diode) for electret microphones (p.1). Package X2SON-6 (DTQ), 1 × 0.8 mm.
- Status: Active, marked "NEW" on ti.com (read 2026-11-19). No other TI discrete JFET launched 2021–2026 was found besides JFE150, JFE2140, JFE2325.
- Test conditions (p.5): $V_{DS}=2.5$ V, $C_{IN}=5$ pF, $R_D=2.2$ kΩ.
- $I_{DSS}$ 220 / 385 / 500 µA; ratio 0.95–1.05. $G_{FS}$ 0.44 / 0.7 mS. $V_{GSC}$ −1.2 / −1.0 / −0.7 V (p.5).
- $C_{iss}$ 0.85 pF, $C_{rss}$ 0.1 pF ($V_{DS}=2$ V); $C_{oss}$ 1 pF (p.5).
- $e_n$ 4.3 nV/$\sqrt{\text{Hz}}$ at 10 kHz, gate grounded (p.5). Fig. 5-24 (p.9, read by eye, gate grounded; re-read on 2026-11-21 for the model calibration, `scripts/jfet_model_check.py`, FIG_5_24, with a pixel check giving 31.3 at 10 Hz): ≈101 at 1 Hz, ≈32 at 10 Hz, ≈10 at 100 Hz, ≈5.2 at 1 kHz, ≈4.4 at 10 kHz, ≈4.25 at 100 kHz; 1/f corner ≈560 Hz (10 Hz × (32² − 4.25²)/4.25²). The first reading, ≈40 at 10 Hz and a corner of ≈500 Hz, was high. With 5 pF source the noise is far higher (≈1.5 µV at 1 Hz, dominated by the gate bias diode).
- $R_{IN}$ ≥ 400 GΩ; $\Delta V_{GS}$ ±10 typ / ±30 max mV; drift ±10 / ±70 µV/°C (p.5).
- Ratings (p.4): $V_{DS}$ ±55 V, $V_{GS}$ ±0.5 V, $V_{GD}$ −55…+0.5 V, $I_{DS}$ 1 mA. $V_{(BR)GDO}$ −30 V typ (p.5).
- SPICE: SLVMF24/SLVMF26/SLVMF68 (identical card) `BETA=308u VTO=-1.1 LAMBDA=7m RD=5 RS=4 CGS=650f CGD=300f KF=40e-18 AF=1`; header requires GMIN = 1e-16.
- Relevance: the gate is diode-clamped and $V_{GS}$ is limited to ±0.5 V, so it is not a drop-in for a DC-coupled instrument input; listed for completeness.

### 1.4 TI application documents (device-level content)

- SBOA563 (March 2023), JFE2140 preamplifier: measured $g_m$ ≈7.5 mS at 1 mA (p.3); remaining content is loop/stability analysis and measured closed-loop gain (p.5).
- SBOA589 (May 2024), JFE2140 + INA849 preamplifier: noise comparison vs source resistance (Fig. 3, p.3; whole-circuit, not device-level), Table 1 (p.3): 57.63 nV/$\sqrt{\text{Hz}}$ total at 1 kHz with $R_s = 100$ kΩ vs 162.07 for the INA alone; Fig. 5 (p.5) gate current vs $V_{DS}$ identical to JFE2140 Fig. 6-6.
- No TI document with paralleling measurements or $e_n$ vs $I_D$ beyond the data sheets was found.

---

## 2. Linear Integrated Systems (LIS)

Status for all LIS parts: each part has a live product page on linearsystems.com (HTTP 200 on 2026-11-19); LIS publishes no lifecycle flag. Price/stock: not checked.

### 2.1 LSK389 A/B/C/D (LIS_LSK389_datasheet_Doc201122_RevA27_2023-06-23.pdf; Doc 201122 Rev A27, 06/23/2023)

- Type: N-channel monolithic dual. Packages: TO-71 6L and SOIC 8L (p.1, p.8 ordering). "Improved second source replacement for 2SK389" (p.1).
- $I_{DSS}$ ($V_{DS}=10$ V, $V_{GS}=0$): A 2.6–6.5, B 6–12, C 10–20, D 17–30 mA (p.2).
- $V_{GS(off)}$: −0.3 to −1.6 V ($V_{DS}=10$ V, $I_D=0.1\,\mu$A) (p.2).
- $G_{fs}$ (full conduction, $V_{DS}=10$ V, $V_{GS}=0$, 1 kHz): 8 min / 20 typ mS (p.2).
- $g_{fs}$ vs $I_D$ (read by eye): Fig. 17 (p.7) A: ≈15.5 mS at 2 mA, ≈20 at 3.5 mA; B: ≈13 at 2 mA, ≈20.5 at 5 mA, ≈27 at 10 mA. Fig. 18 (p.7) C: ≈15 at 4 mA, ≈24 at 12 mA, ≈33 at 28 mA; D: ≈21 at 4 mA, ≈32.5 at 12 mA, ≈40 at 22 mA.
- $e_n$ ($V_{DS}=10$ V, $I_D=2$ mA): 1.6 typ / 1.9 max at 1 kHz; 3.2 typ / 4.0 max at 10 Hz (p.2). 1/f corner from table ≈30 Hz.
- $e_n$ vs $f$ (Fig. 22, p.8, bias not stated on the plot, read by eye): ≈3.15 at 10 Hz, ≈2.4 at 30 Hz, ≈1.8 at 100 Hz, ≈1.7 at 200 Hz–1 kHz, ≈1.55 at 10 kHz; $e_n = \sqrt{2}\,e_w$ reached at ≈30 Hz.
- $C_{iss}$ 25 pF typ ($V_{DS}=10$ V, $V_{GS}=0$, 1 MHz); $C_{rss}$ 5.5 pF typ ($V_{DG}=10$ V, $I_D=0$) (p.2). No C–V curves.
- $I_{GSS}$ −100 typ / −300 max pA ($V_{GS}=-25$ V) (p.2); gate-to-gate isolation ±1 / ±50 nA at ±45 V.
- Gate current vs $V_{DS}$ (Figs. 1–4, p.3, read by eye): A grade (0.04–3 mA): ≈1–2 pA up to 12 V, ≈15–20 pA at 16 V (2.2 mA), ≈300 pA at 20 V; B: ≈3–5 pA up to 12 V; C and D: ≈1 pA up to ≈10–12 V, rising thereafter. Onset of impact ionization ≈12–14 V.
- Matching (p.2): $|V_{GS1}-V_{GS2}|$ 6 typ / 15 max mV ($V_{DS}=10$ V, 1 mA); $I_{DSS1}/I_{DSS2}$ 0.9 / 1.0 / 1.1. Drift: not given.
- Ratings (p.1–2): $V_{GSS}$ 40 V, $V_{GDS}$ 40 V, $BV_{GSS}$ −40 V min, $P_D$ 400 mW (per device or total not stated), $I_{G(F)}$ 10 mA.
- SPICE: LIS "Updated LSK389 A/B/C/D" Rev 2, 05/18/2026 (PDF): A `VTO=-0.401 BETA=30.7m LAMBDA=16.7m`, B `-0.702 / 23.7m / 10.2m`, C `-0.645 / 26.0m / 12.5m`, D `-1.092 / 17.5m / 15.2m`; common `RD=2 RS=2 CGS=19.5p CGD=5.5p PB=1.0 FC=0.5 M=0.4 KF=8.2e-18 AF=1`.
- App note (LIS_appnote_LSK389_Cordell_RevA4.pdf, Rev A4): "key specifications" 1.3 nV/$\sqrt{\text{Hz}}$ at 1 kHz and 1.5 at 10 Hz, 2 mA; 14 mS at 2 mA (p.2). Measured two-stage amplifier (Fig. 1, p.4; $V_{DS}\approx 10$ V): 1.17 nV/$\sqrt{\text{Hz}}$ (A-weighted ENBW 13.5 kHz, includes second stage) at 2 mA. Table 1 (p.5): input noise 1.72 / 1.44 / 1.17 / 1.11 / 1.07 nV/$\sqrt{\text{Hz}}$ at 0.5 / 1 / 2 / 4 / 8 mA. Paralleling (p.5): two devices at 4 mA each ≈0.8 nV/$\sqrt{\text{Hz}}$ vs one at 8 mA ≈1.07.
- Older revision (LIS_LSK389_datasheet_old-undated_PDF2005-12-07_mirror-cordellaudio.pdf; third-party copy, PDF created 2005-12-07): $e_n$ 0.9 typ / 1.9 max (1 kHz), 2.5 typ / 4 max (10 Hz); $C_{iss}$ 25, $C_{rss}$ 5.5 pF; grades A–C only (p.2).

### 2.2 LSK170 A/B/C/D (LIS_LSK170_datasheet_Doc201110_RevA22_2019-11-19.pdf; Doc 201110 Rev A22, 11/19/2019)

- Type: N-channel single. Packages: TO-92, SOT-23, SOT-89 (p.1). "Direct pin-for-pin replacement of Toshiba's 2SK170" (p.1).
- $I_{DSS}$: A 2.6–6.5, B 6–12, C 10–20, D 18–30 mA (p.2).
- $V_{GS(off)}$ −0.2 to −2.0 V ($V_{DS}=10$ V, 1 nA); $V_{GS}$ 0.5 V typ (magnitude) at 1 mA (p.2).
- $G_{fs}$ 14 min / 22 typ mS (full conduction); 6 min / 10 typ mS at $V_{DS}=15$ V, $I_D=1$ mA (p.2).
- $e_n$ ($V_{DS}=10$ V, 2 mA): 0.9 typ / 1.9 max (1 kHz); 1.4 typ / 4.0 max (10 Hz) (p.2). 1/f corner from table ≈14 Hz.
- $e_n$ vs $f$ (p.6, $V_{DS}=10$ V, 2 mA, read by eye): ≈1.37 at 10 Hz, ≈1.1 at 50 Hz, ≈0.97 at 100 Hz, ≈0.91 at 300 Hz, ≈0.93 at 1 kHz, ≈0.92 at 10 kHz, ≈0.90 at 100 kHz.
- $C_{iss}$ 20 pF typ, $C_{rss}$ 5 pF typ ($V_{DS}=15$ V, $I_D=100\,\mu$A, 1 MHz) (p.2); feature list says "22 pF max" (p.1).
- $I_G$ −0.5 nA max ($V_{DG}=10$ V, 1 mA); $I_{GSS}$ −1.0 nA max ($V_{GS}=-10$ V) (p.2). $I_G$ vs $V_{DS}$ curves (p.3, LSK170A/B) appear identical to LSK389 Figs. 1–2.
- Ratings: $V_{GSS}$, $V_{GDS}$ 40 V; $P_D$ 400 mW; $T_j$ max 135 °C (p.1).
- SPICE: LIS "LSK170A Spice Model" 03/16/2026: `Beta=34.97m Vto=-0.351 Lambda=0.03 Rd=7.5 Rs=7.5 Cgd=19p Cgs=27p Fc=0.5 M=320m Pb=0.6 Kf=0.004f Af=1 Gdsnoi=8 Nlev=3` (LTspice-specific noise parameters).

### 2.3 LSK489 A/B (LIS_LSK489_datasheet_Doc201151_RevA40_2022-04-12.pdf; Doc 201151 Rev A40, 04/12/2022)

- Type: N-channel monolithic dual, low capacitance. Packages: TO-71 6L, SOIC-8, SOT-23 6L; TO-71/SOIC pin compatible with LSK389 (p.1). Single version: LSK189.
- $I_{DSS}$ ($V_{DG}=15$ V): A 2.5 / 5.5 / 8.5 mA; B 8.0 / 11.5 / 15.0 mA (p.2).
- $V_{GS(off)}$ −1.5 to −3.5 V ($V_{DS}=15$ V, 1 nA); $V_{GS}$ −0.5 to −3.5 V at 500 µA (p.2).
- $G_{fs}$ ≥1500 µS (full conduction, $V_{DG}=15$ V); 1000 min / 1500 typ µS at 500 µA (p.2). Fig. "gfs vs drain current" (p.7, $V_{GS(off)}=-3$ V, $V_{DS}=10$ V, read by eye, 25 °C): ≈1.3 mS at 0.1 mA, ≈3.6 at 1 mA, ≈4.8 at 2 mA, ≈7.3 mS at 10 mA.
- $e_n$ ($V_{DS}=15$ V, 2 mA): 1.8 typ at 1 kHz, 3.5 typ at 10 Hz; no max (p.2). 1/f corner from table ≈28 Hz.
- $e_n$ vs $f$ (p.4, $V_{DS}=15$ V, 2 mA, read by eye): ≈3.6 at 10 Hz, ≈2.0 at 100 Hz, ≈1.8 at 1 kHz, ≈1.75 at 10–100 kHz; $\sqrt{2}\,e_w$ at ≈35 Hz.
- $C_{iss}$ 4 pF, $C_{rss}$ 2 pF ($V_{DS}=15$ V, $I_D=500\,\mu$A, 1 MHz) (p.2).
- $C_{iss}$ vs $V_{GS}$ (p.5, read by eye): $V_{DS}=0$: ≈6.3 pF at $V_{GS}=0$, ≈2.3 pF at −20 V; $V_{DS}=5$ V: ≈4.8 pF at 0 V; $V_{DS}=15$ V: ≈4.2 pF at 0 V, ≈2.7 at −4 V, ≈1.6 at −16 V. $C_{rss}$ vs $V_{GS}$ (p.7): $V_{DS}=0$ ≈2.6 pF, 5 V ≈1.65 pF, 15 V ≈1.3 pF (at $V_{GS}=0$), ≈1.05 pF at −8 V.
- Gate current (p.2): $I_G$ −2 typ / −25 max pA ($V_{DG}=15$ V, 200 µA); −0.8 / −10 nA at 125 °C; $I_{GSS}$ −100 pA max ($V_{DG}=-15$ V). Operating gate current plot (p.4, read by eye): ≈1.5–2 pA at 25 °C up to $V_{DG}\approx 10$ V for 0.1–5 mA, rising above ≈11–13 V (5 mA earliest); $I_{GSS}$ ≈1–2 pA up to 25 V; ≈100 pA at 125 °C.
- Matching (p.2): $|V_{GS1}-V_{GS2}|$ 8 typ / 20 max mV ($V_{DS}=10$ V, 1 mA); $I_{DSS}$ ratio 0.9–1.0; CMRR 95 / 102 dB. Drift vs $I_D$ (p.6, read by eye): ≈19 µV/°C at 0.1 mA to ≈16 µV/°C at 10 mA.
- Ratings (p.1–2): $V_{GSS}$, $V_{GDS}$ 60 V; $BV_{GSS}$ −60 V; gate-to-gate ±30 min / ±45 typ V; $P_D$ 300 mW per side, 500 mW total.
- SPICE: "Copy_LSK489A NJF" (undated): `Beta=2.2m Vto=-1.13 Lambda=4.3m Rd=11 Rs=30 Cgd=3.19p Cgs=2.92p Mj=0.32 Pb=0.8 Fc=0.5 Kf=0.0009f Af=1 Alpha=30u VK=120 Gdsnoi=2.15 Nlev=3`.
- App note (LIS_appnote_LSK489_Cordell_RevA2.pdf, Rev A2): LSK489 1.5 nV/$\sqrt{\text{Hz}}$ at 1 kHz vs LSK389 1.0; 4 pF input capacitance; gate-drain capacitance 1.5 pF; 3 mS at 2 mA (p.2). No device-level measurement plots; the rest is circuit material (p.7–16).

### 2.4 LSK189 (LIS_LSK189_datasheet_Doc201150_RevA20_2019-07-24.pdf; Doc 201150 Rev A20, 07/24/2019)

- Exists: single N-channel version of the LSK489 (p.1). Packages TO-92, SOT-23 (p.1).
- $I_{DSS}$ 2.5 / 5 / 15 mA ($V_{DS}=15$ V); $V_{GS(off)}$ −1.5 to −3.5 V (p.1).
- $G_{fs}$ ≥1500 µS (full conduction); 1000 / 1500 µS at 500 µA (p.1).
- $e_n$ ($V_{DS}=15$ V, 2 mA): 1.8 typ / 2.0 max (1 kHz); 2.8 typ / 3.5 max (10 Hz) (p.1). 1/f corner from table ≈14 Hz. NF 0.5 dB max ($R_G=10$ MΩ, 100 Hz).
- $C_{iss}$ 4 typ / 8 max pF; $C_{rss}$ 3 max pF ($V_{DS}=15$ V, 500 µA) (p.1).
- $I_G$ −2 / −25 pA ($V_{DG}=15$ V, 200 µA); −0.8 / −10 nA at 125 °C; $I_{GSS}$ −100 pA max (p.1).
- Ratings: $V_{GSO}$, $V_{GDO}$ 60 V; $P_D$ 300 mW (p.1).
- Typical curves pp.3–5: not read in detail. SPICE: not found on the product page.

### 2.5 LSJ689 (LIS_LSJ689_datasheet_Doc201180_RevA9_2019-07-23.pdf; Doc 201180 Rev A9, 07/23/19)

- Type: P-channel monolithic dual (complement of LSK489). Packages SOT-23 6L, TO-71, SOIC-8 (p.1).
- $I_{DSS}$ −2.5 to −30 mA ($V_{DS}=-15$ V); $V_{GS(off)}$ 1.5 to 5.0 V (p.2).
- $G_{fs}$ ≥1500 µS (full conduction); 1500 µS typ at −200 µA (p.2). Fig. (p.4, $V_{DS}=-10$ V, read by eye): ≈3.6 mS at 1.5 mA, ≈4.6 mS at 3 mA, ≈9 mS at 15 mA.
- $e_n$ ($V_{DS}=-15$ V, −2 mA): 1.9 typ (1 kHz), 2.2 typ (100 Hz) (p.2); feature box: 2.0 (p.1). $e_n$ vs $f$ (p.5, read by eye): ≈4.3 at 10 Hz, ≈2.1 at 100 Hz, ≈1.75 at 1 kHz, ≈1.7 at 10 kHz, ≈1.6 at 100 kHz; $\sqrt{2}\,e_w$ at ≈60 Hz.
- $C_{iss}$ 8 pF, $C_{rss}$ 3 pF ($V_{DS}=-15$ V, $I_D=-200\,\mu$A) (p.2). Curves (p.5, $V_{GS}=0$, read by eye): $C_{iss}$ ≈33 pF near 0 V, ≈20 pF at −15 V; $C_{rss}$ ≈15 pF at ~0 V, ≈4 pF at 15–20 V (see C6).
- $I_G$ 2 pA typ ($V_{DG}=-15$ V, −200 µA); $I_{GSS}$ 0.9 typ / 100 max pA (p.2).
- Matching: $|V_{GS1}-V_{GS2}|$ 20 mV max; $I_{DSS}$ ratio 0.90–1.0; CMRR 95 / 102 dB (p.2).
- Ratings: $V_{GS}$, $V_{GD}$ 50 V; $P_D$ 300 mW per side / 500 mW total (p.1).
- SPICE: two different LIS cards (see C8). Datasheet p.2: `LSJ689_4 PJF (BETA=28E-4 VTO=-2.75 LAMBDA=2E-3 IS=4.5E-16 RD=73 RS=35 CGD=6E-12 CGS=11E-12 PB=0.25 MJ=0.3 FC=0.5 KF=2E-18 AF=1)`; product-page file "Copy_LSJ689A PJF": `Beta=3.5m Vto=-1.40 Lambda=1.1m Rd=111 Rs=40 Cgd=10p Cgs=9p Mj=0.3 Pb=0.25 Fc=0.5 Kf=0.0011f Af=1 Gdsnoi=2.95 Nlev=3`.
- App note (LIS_appnote_LSJ689_RevA7.pdf): ≈2 nV/$\sqrt{\text{Hz}}$, $C_{rss}$ ≈3 pF, 3 mS at 1 mA (p.2; located via text layer).

### 2.6 LSJ74 / SST74 (LIS_LSJ74_datasheet_Doc201175_RevA9_2021-02-03.pdf; Doc 201175 Rev A9, 02/03/2021)

- Type: P-channel single; TO-92 (LSJ74), SOT-89 (SST74) (p.1). "Improved second source replacement for 2SJ74".
- $I_{DSS}$ ($V_{DG}=-10$ V): A −2.6…−6.5, B −6…−12, C −10…−20, D −17…−30 mA; $V_{GS(off)}$ 0.15–2 V (p.1).
- $G_{fs}$ 8 min / 22 typ mS (full conduction) (p.1). Fig. (p.3, $V_{GS}=0$, read by eye): ≈20 mS for $I_{DSS}$ ≈2 mA, ≈34 mS at 15 mA.
- $e_n$ ($V_{DS}=-10$ V, −2 mA): 1.9 typ (1 kHz), 4 typ (10 Hz) (p.1 table); feature box: 0.9 (p.1) (see C5). 1/f corner from table ≈34 Hz. Curves (p.4) have unlabeled log axes (0.5–5 nV): ≈1.0 at 10 kHz and ≈2.6–3.0 at 10 Hz (read by eye, low confidence).
- $C_{iss}$ 105 pF ($V_{DS}=-10$ V, $V_{GS}=0$); $C_{rss}$ 32 pF ($V_{DS}=-10$ V, $I_D=0$) (p.1). Curves (p.4, read by eye): $C_{iss}$ ≈78 pF at −0.5 V, ≈53 pF at −10 V; $C_{rss}$ ≈32 pF at 0.5 V, ≈11 pF at 10 V.
- $I_G$ 50 pA typ ($V_{DG}=-10$ V, −1 mA); $I_{GSS}$ 1 nA max ($V_{GS}=25$ V) (p.1).
- Ratings: $V_{GDS}$, $V_{GSS}$ 25 V; $P_D$ 400 mW (p.1). SPICE: not found.

### 2.7 LS844 series (LS844/LS845) and LS843

- LIS_LS844series_datasheet_Doc201144_RevA17_2022-08-22.pdf (Doc 201144 Rev A17, 08/22/2022): N-channel monolithic dual, low capacitance. Packages SOIC-8, PDIP-8, SOT-23-6, TO-71, TO-78 (p.1).
- $e_n$: 2.5 typ (p.1); 3.0 max at 1 kHz, 7.0 max at 10 Hz ($V_{DS}=15$ V, 2 mA) (p.3). Not an ultra-low-noise part.
- $C_{iss}$ 3 typ (p.1) / 8 max pF; $C_{rss}$ 3 max pF ($V_{DS}=15$ V, 500 µA); $C_{DD}$ 0.5 pF (p.1, p.3).
- $I_{DSS}$ 1.5 / 5 / 15 mA; $V_{GS(off)}$ −1 to −3.5 V; $G_{fs}$ 1000 / 1500 µS at 500 µA (p.2).
- $I_G$ 15 typ / 50 max pA ($V_{DG}=15$ V, 500 µA); 5 / 30 pA at $V_{DG}=3$ V; 50 nA max at 125 °C (p.2).
- Matching: $|V_{GS1-2}|$ 5 mV (LS844) / 15 mV (LS845) max; drift 10 / 25 µV/°C max; $I_{DSS}$ mismatch 1 typ / 5 max %; $g_{fs}$ mismatch 0.6 / 3 % (p.2). Ratings: 60 V; $P_D$ 400 mW total.
- SPICE: the LS844 product page links a card named LS845 with `Kf=0` (no flicker noise).
- LS843: not on current LIS product pages (LS840-series page covers LS840/LS841/LS842 only, LIS_LS840-LS842_datasheet_Doc201143_RevA9_2016-04-21.pdf, $e_n$ 8 nV typ, p.1). Not pursued further.

### 2.8 Other LIS parts checked

- LSK170X (LIS_LSK170X_datasheet_preliminary_Doc201179_RevA7_2021-02-03.pdf): preliminary; $e_n$ 1.9 nV/$\sqrt{\text{Hz}}$ at 1 kHz (p.1). Not surveyed further.
- LSK589 (LIS_LSK589_datasheet_Doc201186_RevA6_2019-07-23.pdf): dual, $C_{iss}$ 5 pF, $e_n$ 4 nV (10 kHz) / 7 nV (100 Hz) at 5 mA (p.1) — not ultra-low-noise. Its product-page model link returns a PDF stating the file is not available.
- LSBF862 (LIS_LSBF862_datasheet_Doc201195_RevA2_2026-02-17.pdf, Rev A2 02/17/2026) exists, with a SPICE model Rev 2 (02/09/2026). Treated as a BF862 equivalent and left to the BF862 survey.
- No newer LIS ultra-low-noise JFET than those above was found on the product listing.

---

## 3. Toshiba (including the parts requested as Hitachi)

The three parts requested as Hitachi (2SK146, 2SK147, 2SJ72) are Toshiba parts in the documents obtained: their outline tables give Toshiba package codes (2SK146: 2-6E1A; 2SK147 and 2SJ72: 2-5J1B), and 2SK147/2SJ72 are stated complements of each other. No Hitachi-made sheet for these numbers was found; the Hitachi folder is empty.

Status (toshiba.semicon-storage.com, read 2026-11-19): 2SK209, 2SK880, 2SK2145 "Not Recommended for New Design" (product pages; datasheets carry an NRND watermark). 2SK170, 2SK369, 2SK389, 2SJ74: product pages return "page not found" (no longer listed). 2SK146, 2SK147, 2SJ72: not checked; data-book era parts. No Toshiba SPICE models are offered for any of them (2SK209/2SK880/2SK2145 pages list none).

### 3.1 2SK170 (Toshiba_2SK170_datasheet_2007-11-01_mirror-jiepei.pdf; sheet dated 2007-11-01)

- N-channel single, TO-92 (2-5F1D) (p.1).
- $I_{DSS}$ 2.6–20 mA (GR 2.6–6.5, BL 6.0–12, V 10–20) ($V_{DS}=10$ V); $V_{GS(off)}$ −0.2 to −1.5 V (p.1).
- $|Y_{fs}|$ 22 mS typ ($V_{DS}=10$ V, $V_{GS}=0$, $I_{DSS}=3$ mA) (p.1). $|Y_{fs}|$–$I_D$ (p.2, read by eye): ≈20 mS at 2 mA, ≈32 at 5.6 mA, ≈40 at 10 mA.
- $E_n$ 0.95 typ ($V_{DS}=10$ V, $I_D=1$ mA, 1 kHz) (p.1). $E_n$–$I_D$ (p.3, read by eye): ≈1.45 (0.2 mA), ≈1.2 (0.5 mA), ≈1.0 (1 mA), ≈0.9 (2 mA), ≈0.87 (3 mA), ≈0.85 (10 mA).
- NF (p.1): NF(1) 1.0 typ / 10 max dB and NF(2) 0.5 typ / 2 max dB, both printed as $V_{DS}=10$ V, $I_D=1$ mA, $R_G=1$ kΩ, $f=1$ kHz (see C7). NF–$f$ (p.4): ≈1.1 dB at 10 Hz for $R_G=1$ kΩ → derived $e_n$ ≈2.1 nV at 10 Hz (1 mA).
- $C_{iss}$ 30 pF ($V_{DS}=10$ V, $V_{GS}=0$); $C_{rss}$ 6 pF ($V_{DG}=10$ V, $I_D=0$) (p.1). Curves (p.3, read by eye): $C_{iss}$ ≈48 pF at 0.3 V, ≈43 at 1 V, ≈30 at 10 V, ≈27 at 30 V; $C_{rss}$ ≈25 pF at −0.3 V, ≈10 at −3 V, ≈6 at −10 V, ≈4 at −30 V.
- $I_{GSS}$ −1 nA max ($V_{GS}=-30$ V) (p.1). Gate excess current $I_{GSX}$–$V_{DS}$ (p.4, read by eye at 200 dpi): ≈1–2 pA at 8 V; at 10 V ≈5 pA (1 mA) / ≈25 pA (10 mA); at 12 V ≈30 pA (1 mA) / ≈250 pA (10 mA); ≈10 nA at 20 V.
- Ratings: $V_{GDS}$ −40 V; $P_D$ 400 mW; $T_j$ 125 °C (p.1).
- Older sheet seen: an xdevs.com copy dated 2003-03-25 exists (not used).

### 3.2 2SK369 (Toshiba_2SK369_datasheet_2007-11-01_mirror-jiepei.pdf; 2007-11-01)

- N-channel single, TO-92 (p.1).
- $I_{DSS}$ 5–30 mA (GR 5–10, BL 8–16, V 14–30); $V_{GS(off)}$ −0.3 to −1.2 V (p.1).
- $|Y_{fs}|$ 25 min / 40 typ mS ($I_{DSS}=5$ mA) (p.1). $|Y_{fs}|$–$I_D$ (p.2, read by eye): ≈25 mS at 2 mA, ≈42 at 5 mA, ≈52 at 10 mA, ≈65 at 20 mA.
- Noise: NF 1.0 dB typ ($V_{DS}=10$ V, $I_D=5$ mA, 1 kHz, $R_G=100\,\Omega$) (p.1 features); NF(1) 5 typ / 10 max dB at 100 Hz, NF(2) 1 / 2 dB at 1 kHz ($R_G=100\,\Omega$, 5 mA) (p.1). $E_n$–$I_D$ (p.3, 1 kHz, read by eye): ≈1.2 (0.25 mA), ≈0.9 (1 mA), ≈0.78 (3 mA), ≈0.71 (10 mA), ≈0.70 (15 mA). NF–$f$ (p.4, 3 mA, $R_G=100\,\Omega$): ≈3.1 dB at 10 Hz → derived $e_n$ ≈1.3 nV at 10 Hz.
- $C_{iss}$ 75 pF, $C_{rss}$ 15 pF (p.1). Curves (p.3, read by eye): $C_{iss}$ ≈110 pF at 0.4 V, ≈72 at 10 V, ≈63 at 20 V; $C_{rss}$ ≈17 pF at −10 V.
- $I_{GSS}$ −1 nA max (p.1). $I_{GSX}$–$V_{DS}$ (p.4, read by eye at 200 dpi): ≈1 pA at 4 V; at 8 V ≈5 pA (1 mA) / ≈20 pA (10 mA); at 10 V ≈50 pA (1 mA) / ≈0.6 nA (10 mA); at 12 V ≈250 pA / ≈2.5 nA. Note 2 (p.1): use $V_{DS}<15$ V for low noise.
- Ratings: $V_{GDS}$ −40 V; $P_D$ 400 mW (p.1).

### 3.3 2SK389 (Toshiba_2SK389_datasheet_1997-04-10_mirror-jiepei.pdf; 1997-04-10, scanned)

- N-channel monolithic dual, 7-pin SIP (2-10M1A); complement 2SJ109 (p.1).
- $I_{DSS}$ 2.6–20 mA (GR 2.6–6.5, BL 6–12, V 10–20); $V_{GS(off)}$ −0.15 to −2.0 V (p.2).
- $|Y_{fs}|$ 8 min / 20 typ mS ($I_{DSS}=3$ mA); $|Y_{fs}|$ ratio ≥0.9 (p.2). $|Y_{fs}|$–$I_D$ (p.3, read by eye): ≈18 mS at 2 mA, ≈24 at 4 mA, ≈28 at 6 mA, ≈31 at 9 mA.
- NF(1) 1.5 typ / 10 max dB (10 Hz), NF(2) 0.5 / 2 dB (1 kHz) ($V_{DS}=10$ V, $R_G=1$ kΩ, 1 mA) (p.2). $E_n$–$I_D$ (p.4, 1 kHz, read by eye): ≈1.43 (0.3 mA), ≈1.27 (1 mA), ≈1.15 (3 mA), ≈1.12 (10 mA). NF(1) 1.5 dB → derived $e_n$ ≈2.6 nV at 10 Hz (1 mA).
- $C_{iss}$ 25 pF, $C_{rss}$ 5.5 pF (p.2). Curves (p.4): $C_{iss}$ ≈40 pF at 0.3 V, ≈27 at 10 V; $C_{rss}$ ≈15 pF at −0.3 V, ≈6 at −10 V.
- $I_{GSS}$ −1 nA max (p.2). $I_{GSX}$ (p.4, read by eye): ≈5–7 pA at 10 V, ≈10–20 pA at 12 V, ≈70–300 pA at 16 V.
- Matching: $|V_{GS1}-V_{GS2}|$ 20 mV max ($V_{DS}=10$ V, 1 mA); $I_{DSS}$ ratio ≥0.9 (p.2). Drift: not given.
- Ratings: $V_{GDS}$ −50 V; $P_D$ 200 mW (p.1).

### 3.4 2SK146 (Toshiba_2SK146_datasheet_databook-pp685-688_undated_mirror-datasheet4u.pdf; data-book pp. 685–688, undated)

- N-channel dual (two 2SK369-class devices), 6-pin package 2-6E1A (p.1 = printed 685).
- $I_{DSS}$ 5–30 mA (GR 5–10, BL 8–16, V 14–30); $V_{GS(off)}$ −0.3 to −1.2 V (p.1).
- $|Y_{fs}|$ 30 min / 40 typ mS ($I_{DSS}=5$ mA) (p.1); $|Y_{fs}|$–$I_D$ (p.2, read by eye) ≈42 mS at 5 mA, ≈55 at 10 mA.
- NF 1.0 dB typ (1 kHz, $R_g=100\,\Omega$, 5 mA); NF(1) 5 / 10 dB at 100 Hz; NF(2) 1 / 2 dB at 1 kHz (p.1). $E_n$–$I_D$ (p.3, read by eye): ≈1.2 (0.25 mA), ≈0.9 (1 mA), ≈0.76 (3 mA), ≈0.71 (10 mA).
- $C_{iss}$ 75 pF, $C_{rss}$ 15 pF (p.1); curves p.3 ≈110 pF at 0.3 V, ≈75 at 10 V.
- $I_{GSS}$ −1 nA max; $I_{GX}$–$V_{DS}$ (p.4) similar in shape to 2SK369 (≈1 pA below 6 V, steep rise from ≈8 V).
- Matching: $|V_{GS1}-V_{GS2}|$ 20 mV max ($V_{DS}=10$ V, 5 mA) (p.1). Ratings: $V_{GDS}$ −40 V, $P_D$ 600 mW × 2 (p.1).

### 3.5 2SK147 (Toshiba_2SK147_datasheet_databook-p883_undated_mirror-radioradar.pdf; one page, data-book p. 883)

- N-channel single, TO-92MOD (2-5J1B); complement of 2SJ72 (p.1).
- $I_{DSS}$ 5–30 mA (GR/BL/V as 2SK369); $V_{GS(off)}$ −0.3 to −1.2 V; $|Y_{fs}|$ 30 / 40 mS; $C_{iss}$ 75 pF; $C_{rss}$ 15 pF; NF(1) 5 / 10 dB (100 Hz), NF(2) 1 / 2 dB (1 kHz) at $R_g=100\,\Omega$, 5 mA; $I_{GSS}$ −1 nA max; $V_{GDS}$ −40 V; $P_D$ 600 mW (p.1). Only page 1 was available; no curves. $e_n$ in nV: not given.

### 3.6 2SJ74 (Toshiba_2SJ74_datasheet_2007-11-01_mirror-jiepei.pdf; 2007-11-01)

- P-channel single, TO-92; complement of 2SK170 (p.1).
- $I_{DSS}$ −2.6 to −20 mA (GR, BL, V); $V_{GS(off)}$ 0.15–2.0 V (p.1).
- $|Y_{fs}|$ 8 / 22 mS ($I_{DSS}=-3$ mA) (p.1); $|Y_{fs}|$–$I_D$ (p.2, read by eye): ≈26 mS at 2 mA, ≈33 at 4 mA, ≈40 at 8 mA, ≈48 at 16 mA.
- $E_n$ 0.95 typ ($V_{DS}=-10$ V, $I_D=-1$ mA, 1 kHz) (p.1). $E_n$–$I_D$ (p.3, read by eye): ≈1.13 (0.3 mA), ≈0.95 (1 mA), ≈0.8 (3 mA), ≈0.74 (10 mA). NF(1) 1.0 / 10 dB (10 Hz), NF(2) 0.5 / 2 dB (1 kHz) at $R_G=1$ kΩ, 1 mA (p.1); NF–$I_D$ curve ≈1.7 dB at 10 Hz (p.3).
- $C_{iss}$ 105 pF, $C_{rss}$ 32 pF (p.1). Curves (p.3): $C_{iss}$ ≈170 pF at −0.5 V, ≈100 at −10 V; $C_{rss}$ ≈75 pF at 0.5 V, ≈32 at 10 V, ≈25 at 25 V.
- $I_{GSS}$ 1.0 nA max ($V_{GS}=25$ V). $I_{GSX}$ (p.3, read by eye): ≈2–3 pA at −4 V, ≈5 pA at −10 V (10 mA), ≈20 pA at −20 V.
- Ratings: $V_{GDS}$ 25 V; $P_D$ 400 mW (p.1).

### 3.7 2SJ72 (Toshiba_2SJ72_datasheet_databook-pp599-601_undated_mirror-datasheet4u.pdf; data-book pp. 599–601)

- P-channel single, TO-92MOD (2-5J1B); complement of 2SK147 (p.1).
- $I_{DSS}$ −5 to −30 mA (GR, BL, V); $V_{GS(off)}$ 0.3–2.0 V; $|Y_{fs}|$ 30 / 40 mS ($I_{DSS}=-5$ mA) (p.1).
- NF 1.0 dB typ (1 kHz, 100 Ω, −5 mA); NF(1) 5 / 10 dB at 100 Hz (p.1). $e_n$–$I_D$ (p.3 = printed 601, read by eye): ≈0.9 (0.7 mA), ≈0.86 (1 mA), ≈0.7 (3 mA), ≈0.65 (10–20 mA).
- $C_{iss}$ 185 pF, $C_{rss}$ 55 pF ($V_{DG}=-10$ V) (p.1). $I_{GSS}$ 1 nA max. $I_{GX}$ (p.3): ≈2–3 pA up to −10 V.
- Ratings: $V_{GDS}$ 25 V; $P_D$ 600 mW (p.1). Page 2 (static curves) not read.

### 3.8 2SK209 / 2SK880 / 2SK2145 (Toshiba official sheets; footer date 2026-04-14; the Toshiba web listing gives "Mar, 2014")

- 2SK209: N-ch single, S-Mini (SOT-23/SC-59). 2SK880: same parameters in USM (SC-70). 2SK2145: two devices, common source, SMV 5-pin. Status NRND (see above).
- $I_{DSS}$ 1.2–14 mA (Y 1.2–3.0, GR 2.6–6.5, BL 6.0–14); $V_{GS(off)}$ −0.2 to −1.5 V; $|Y_{fs}|$ 4.0 min / 15 typ mS ($V_{GS}=0$) (2SK209 p.1; 2SK880 p.1; 2SK2145 p.2).
- $C_{iss}$ 13 pF, $C_{rss}$ 3 pF (same pages). 2SK209 curves (p.3): $C_{iss}$ ≈20 pF at 0.5 V, ≈14 at 10 V; $C_{rss}$ ≈7 pF at −0.5 V, ≈3 at −10 V.
- NF(1) 5 dB typ (10 Hz), NF(2) 1 dB typ (1 kHz), $V_{DS}=10$ V, $R_G=1$ kΩ, $I_D=0.5$ mA (same pages); NF 1 dB → derived $e_n$ ≈2.0 nV at 1 kHz (0.5 mA). $e_n$ in nV: not given.
- $I_{GSS}$ −1 nA max ($V_{GS}=-30$ V). $V_{GDS}$ −50 V. $P_D$: 150 mW (2SK209), 100 mW (2SK880), 300 mW total (2SK2145).
- 2SK2145 matching: not given (no $\Delta V_{GS}$ specification) (p.2).

---

## 4. onsemi (ex-Sanyo)

### 4.1 2SK3557 (onsemi_2SK3557_datasheet_2SK3557-D_Rev3_2024-09.pdf; 2SK3557/D Rev. 3, September 2024)

- N-channel single, CP (SC-59/SOT-23) (p.1). Applications: AM tuner RF amplification, low-noise amplifier (p.1).
- Status: Active (onsemi product page, read 2026-11-19); 2SK3557-6-TB-E USD 0.132, 2SK3557-7-TB-E USD 0.1333 (quantity basis not stated), shown as unavailable from stock. An automotive variant NSVJ3557SA3 exists (onsemi_NSVJ3557SA3_datasheet_..., not surveyed in detail).
- $I_{DSS}$ 10–32 mA (rank 6: 10–20, rank 7: 16–32) ($V_{DS}=5$ V); $V_{GS(off)}$ −0.3 / −0.7 / −1.5 V ($V_{DS}=5$ V, $I_D=100\,\mu$A) (p.2).
- $|y_{fs}|$ 24 min / 35 typ mS ($V_{DS}=5$ V, $V_{GS}=0$, 1 kHz) (p.2). Fig. 5 (p.3, $V_{DS}=5$ V, read by eye): ≈7.5 mS at 0.5 mA, ≈11 at 1 mA, ≈16 at 2 mA, ≈20 at 3 mA, ≈33 at 10 mA.
- $C_{iss}$ 10.0 pF, $C_{rss}$ 2.9 pF ($V_{DS}=5$ V, $V_{GS}=0$) (p.2). Fig. 8 (p.4): $C_{iss}$ ≈14 pF at 1 V, ≈10.5 at 10 V; Fig. 9: $C_{rss}$ ≈5 pF at 1.1 V, ≈2.7 at 10 V, ≈2.2 at 20 V.
- NF 1.0 dB typ ($V_{DS}=5$ V, $R_g=1$ kΩ, $I_D=1$ mA, 1 kHz) (p.2) → derived $e_n$ ≈2.0 nV at 1 kHz. Fig. 10 NF–$f$ (p.4, read by eye): ≈3.2 dB at 10 Hz, ≈1.8 at 30 Hz, ≈1.1 at 100 Hz, ≈1.0 at 1 kHz, ≈1.2 at 100 kHz → derived $e_n$ ≈4.2 nV at 10 Hz; 1/f corner ≈35 Hz (derived, low confidence).
- $I_{GSS}$ −1.0 nA max ($V_{GS}=-10$ V) (p.2). Gate current vs $V_{DG}$: not given.
- Ratings: $V_{DSX}$ 15 V, $V_{GDS}$ −15 V, $I_D$ 50 mA, $P_D$ 200 mW (p.1).
- SPICE: onsemi rank-6 and rank-7 models (Jan 11 2021): `BETA=0.026 VTO=-0.76 (rank 6) / -1.04 (rank 7) LAMBDA=0.038 RD=5.6 RS=6.5 IS=0.558f CGS=7.62p CGD=7.62p M=0.33 PB=0.6 FC=0.5 N=1.016`; no KF/AF (no flicker noise), lead inductances in a subcircuit.

### 4.2 CPH3910 (onsemi_CPH3910_datasheet_CPH3910-D_Rev2_2022-02.pdf; CPH3910/D Rev. 2, February 2022)

- N-channel single, CPH3 (p.1). Applications: AM tuner RF amplification, low-noise amplifier.
- Status: product page shows "Active, Not Rec." (read 2026-11-19); CPH3910-TL-E USD 0.132. Automotive variant NSVJ3910SB3 exists.
- $I_{DSS}$ 20–40 mA; $V_{GS(off)}$ −0.6 / −1.2 / −1.8 V ($V_{DS}=5$ V, 100 µA); $|y_{fs}|$ 30 / 40 mS ($V_{GS}=0$) (p.1). Fig. 5 (p.2, $I_{DSS}=30$ mA, read by eye): ≈10 mS at 1 mA, ≈14 at 2 mA, ≈21 at 5 mA, ≈28 at 10 mA.
- $C_{iss}$ 6.0 pF, $C_{rss}$ 2.3 pF ($V_{DS}=5$ V, $V_{GS}=0$) (p.1). Figs. 8–9 (p.3): $C_{iss}$ ≈8.2 pF at 1 V, ≈5.6 at 10 V, ≈5.2 at 25 V; $C_{rss}$ ≈3.9 pF at 1 V, ≈2.3 at 10 V, ≈1.9 at 25 V.
- Noise: NF 2.1 typ / 2.8 max dB at 100 MHz only (p.1). Audio-band $e_n$: not given.
- $I_{GSS}$ −1.0 nA max ($V_{GS}=-10$ V). Ratings: $V_{DSX}$ 25 V, $V_{GDS}$ −25 V, $I_D$ 50 mA, $P_D$ 400 mW (p.1).
- SPICE: onsemi CPH3910-SPICE-D rev0 (Jul 04 2014): `BETA=0.0256 VTO=-1.23 LAMBDA=0.033 RD=7.6 RS=7.6 IS=10.3f CGS=5.6p CGD=5.6p M=0.36 PB=0.6 FC=0.5 N=1.111`; no KF/AF.

### 4.3 Other onsemi JFETs screened (page 1–2 text only; not rendered or surveyed in detail)

- 2SK2394 (CP, 15 V, 10–20 mA, 38 mS; NF 1.0 dB at 1 kHz, 1 kΩ, 1 mA), 2SK932 (CP, 15 V, 10–24 mA, 50 mS, $C_{iss}$ 10 pF; NF 1.5 dB at 1 kHz), MCH5908 (15 V, 10–32 mA, 35 mS, $C_{iss}$ 10.5 pF; NF 1.0 dB at 1 kHz), CPH6904 (dual CPH6, 25 V, 20–40 mA, 40 mS, $C_{iss}$ 6.0 pF; NF at 100 MHz only), MCH3914 (15 V, 16–50 mA, 29 mS, $C_{iss}$ 4.9 pF), and automotive NSVJ variants (NSVJ2394SA3, NSVJ3557SA3, NSVJ3910SB3, NSVJ5908DSG5, NSVJ6904DSB6). All are AM-tuner/RF-oriented with 15–25 V ratings and no audio-band nV specification; lifecycle status not checked individually.
- Also downloaded during screening but outside the low-noise scope: 2SK3738, 2SK545, TF412S, TF414 (infrared-sensor JFETs), BSR57, BSR58, J110, MMBF4117, MMBF5103, MMBF5457, MMBFJ201/J202, MMBFJ211, PF5102.

---

## 5. Contradictions and caveats found

- C1. LSK389 typical $e_n$ differs between LIS documents: datasheet Rev A27 1.6 (1 kHz) / 3.2 (10 Hz) nV; app note Rev A4 1.3 / 1.5 nV (p.2) and measured 1.17 nV (p.4); old datasheet (2005 PDF) 0.9 / 2.5 nV. Maximum limits (1.9 / 4.0) are the same in old and new sheets.
- C2. LSK170 (0.9 nV typ at 1 kHz, 1.4 nV at 10 Hz) versus LSK389 (1.6 / 3.2 nV) under the same conditions, although LIS calls the LSK389 the dual equivalent and the LSK170 $I_G$ curves are identical to the LSK389 Figs. 1–2. The LSK170 feature list gives $C_{iss}$ "22 pF max" while the table gives 20 pF typ.
- C3. LSK389 Fig. 21 (p.8) and LSK170 (p.6): the plotted $g_{fs}$ falls with $|V_{GS(off)}|$ while $I_{DSS}$ rises; this contradicts Figs. 17–18 and the square-law relation ($g_{fs0} = 2I_{DSS}/|V_{GS(off)}|$ rises with $I_{DSS}$). Treat that figure as unreliable.
- C4. LSK489: app note Rev A2 gives 1.5 nV, gate-drain capacitance 1.5 pF and 3 mS at 2 mA; datasheet gives 1.8 nV, $C_{rss}$ 2 pF and a $g_{fs}$ curve ≈4.8 mS at 2 mA (read by eye) with a 1.5 mS typ table value at 0.5 mA.
- C5. LSJ74: feature box $e_n$ = 0.9 nV, table 1.9 nV typ (both 1 kHz). $C_{iss}$ 105 pF in the table vs ≈53 pF on the curve at −10 V.
- C6. LSJ689: $C_{iss}$ 8 pF (table, $I_D=-200\,\mu$A) vs ≈20 pF on the $V_{GS}=0$ curve at −15 V; front page $e_n$ 2.0 vs table 1.9.
- C7. 2SK170 (2007 sheet, p.1): NF(1) and NF(2) are both printed with $f=1$ kHz although typ/max differ (1.0/10 dB vs 0.5/2 dB); the 2SJ74 and 2SK389 sheets give NF(1) at 10 Hz, which is the likely intent.
- C8. LSJ689 has two different LIS SPICE cards (datasheet `LSJ689_4` with KF = 2e-18, VTO = −2.75, BETA = 2.8m; web `LSJ689A` with Kf = 1.1e-18, Vto = −1.40, Beta = 3.5m).
- C9. JFE2140 SPICE (`KF=0.2e-18`) under-predicts the datasheet 1/f noise: with BETA = 14.24m at 2 mA ($g_m$ ≈10.7 mS) the model gives about 1.2 nV/$\sqrt{\text{Hz}}$ at 10 Hz versus 2.4 typ in the datasheet (implied corner ≈4 Hz vs ≈38 Hz). The JFE150 model (KF = 3.25e-18) gives ≈1.8 nV at 10 Hz versus 1.6 typ, which is consistent.
- C10. JFE2325: $V_{(BR)GDO}$ −30 V typ (p.5, feature list p.1) but absolute maximum $V_{GD}$ −55 V and $V_{DS}$ ±55 V (p.4).
- C11. The parts requested as Hitachi (2SK146, 2SK147, 2SJ72) are Toshiba parts in all documents found.
- C12. Toshiba 2SK209/2SK880/2SK2145: page footers carry 2026-04-14, the web listing gives "Mar, 2014" for the same files (file sizes match the listing).
- C13. Datasheet $C_{iss}$ is quoted at different biases ($V_{GS}=0$ for Toshiba/LSK389/onsemi; operating current for LSK489/LSK170/LSJ689; $V_{DS}=5$ V for TI), so cross-vendor $C_{iss}$ comparisons are approximate.

---

## 6. Summary table

$e_n$ in nV/$\sqrt{\text{Hz}}$ (typ unless marked), $g_{fs}$ in mS, capacitances in pF, $I_{DSS}$ in mA, $V_{GS(off)}$ in V. "FOM" = $e_n(1\,\text{kHz})\sqrt{C_{iss}}$ with the table values in this row (nV$\cdot\sqrt{\text{pF}}/\sqrt{\text{Hz}}$). r.b.e. = read by eye. Derived = from NF (rough).

| part | vendor | status (2026-11-19) | type | e_n@1kHz (I_D) | e_n@10Hz | g_fs (I_D) | C_iss | C_rss | I_DSS range | V_GS(off) range | I_G | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| JFE150 | TI | Active | N single, SOT-23-5/SC70-5 | 0.9 (2 mA); 0.8 (5 mA) | 1.6 (2 mA); 1.8 (5 mA) | 18 (2 mA); 68 at V_GS=0 | 24 (V_DS 5 V); 30 (0 V) | 7 (V_DS 0) | 24–46 | −1.5…−0.9 | 0.2 pA typ, 10 pA max (V_DS 2 V); ~1–3 nA at V_DS 10 V | FOM 4.4 (2 mA), 3.9 (5 mA); 1/f ≈22 Hz (2 mA); impact ionization from ≈6 V |
| JFE2140 | TI | Active | N matched dual, SOIC-8/WSON-8 | 1.1 (2 mA); 0.9 (5 mA) | 2.4 (2 mA) | 10 (2 mA); 30 at V_GS=0 | 13 (V_DS 5 V); 17 (0 V) | not in table; ≈3.5 at 10 V (r.b.e.) | 12–23 | −1.5…−0.9 | 1 pA typ, 10 pA max (V_DS 2 V); ~1 nA at 10 V | FOM 4.0 (2 mA), 3.2 (5 mA); ΔV_GS ≤4 mV, ≤10 µV/°C; 1/f ≈38 Hz; SPICE KF too low |
| JFE2325 | TI | Active (new 2026) | N dual, self-biased gate, X2SON-6 | 4.3 at 10 kHz (≈I_DSS, gate grounded) | ≈32 (r.b.e.) | 0.7 at V_GS=0 | 0.85 | 0.1 | 0.22–0.5 | −1.2…−0.7 | R_in ≥400 GΩ | FOM 4.0; 1/f ≈560 Hz; V_GS abs max ±0.5 V; microphone part |
| LSK389 A–D | LIS | Listed | N dual, TO-71/SOIC-8 | 1.6 (1.9 max) (2 mA) | 3.2 (4.0 max) | ≈15.5 A / ≈13 B (2 mA, r.b.e.); 20 at V_GS=0 | 25 | 5.5 | A 2.6–6.5, B 6–12, C 10–20, D 17–30 | −0.3…−1.6 | ≈1–5 pA to 12 V (r.b.e.); I_GSS 100 pA typ | FOM 8.0 (5.9 with AN 1.17 nV); ΔV_GS ≤15 mV; 1/f ≈30 Hz |
| LSK170 A–D | LIS | Listed | N single, TO-92/SOT-23/SOT-89 | 0.9 (1.9 max) (2 mA) | 1.4 (4.0 max) | 10 (1 mA, 15 V); 22 at V_GS=0 | 20 (22 max p.1) | 5 | A 2.6–6.5 … D 18–30 | −0.2…−2.0 | ≤0.5 nA max (V_DG 10 V, 1 mA) | FOM 4.0; 1/f ≈14 Hz; see C2 |
| LSK489 A/B | LIS | Listed | N dual, TO-71/SOIC-8/SOT-23-6 | 1.8 (2 mA, 15 V) | 3.5 | 1.5 (0.5 mA); ≈4.8 (2 mA, r.b.e.) | 4 (0.5 mA, 15 V) | 2 | A 2.5–8.5, B 8–15 | −1.5…−3.5 | 2 pA typ, 25 pA max (V_DG 15 V, 0.2 mA) | FOM 3.6; 60 V; ΔV_GS ≤20 mV; 1/f ≈28 Hz |
| LSK189 | LIS | Listed | N single, TO-92/SOT-23 | 1.8 (2.0 max) | 2.8 (3.5 max) | 1.5 (0.5 mA) | 4 (8 max) | 3 max | 2.5–15 | −1.5…−3.5 | 2 pA typ, 25 pA max | FOM 3.6; 1/f ≈14 Hz; single LSK489 |
| LSJ689 | LIS | Listed | P dual, SOT-23-6/TO-71/SOIC-8 | 1.9 (−2 mA) | 2.2 at 100 Hz; ≈4.3 r.b.e. | 1.5 (−0.2 mA); ≈4 (2 mA, r.b.e.) | 8 (−0.2 mA) | 3 | −2.5…−30 | 1.5…5.0 | 2 pA typ | FOM 5.4 (table) / ≈8.5 (curve C_iss); see C6, C8 |
| LSJ74 | LIS | Listed | P single, TO-92/SOT-89 | 1.9 table / 0.9 front page | 4 | 22 at V_GS=0 | 105 | 32 | A −2.6…−6.5 … D −17…−30 | 0.15…2 | 50 pA typ (V_DG −10 V, −1 mA) | FOM 19 (table); see C5 |
| LS844/845 | LIS | Listed | N dual | 2.5 typ, 3.0 max (2 mA) | 7.0 max | 1.5 (0.5 mA) | 3 typ, 8 max | 3 max | 1.5–15 | −1…−3.5 | 15 pA typ, 50 max | not ultra-low-noise; LS843 not listed |
| 2SK170 | Toshiba | Not listed (discontinued) | N single, TO-92 | 0.95 (1 mA); ≈0.85 (≥3 mA, r.b.e.) | ≈2.1 derived (1 mA) | 22 at V_GS=0 (I_DSS 3 mA); ≈20 (2 mA, r.b.e.) | 30 | 6 | 2.6–20 (GR/BL/V) | −0.2…−1.5 | I_GSX ≈5 pA (1 mA) / 25 pA (10 mA) at 10 V | FOM 5.2 (1 mA) |
| 2SK369 | Toshiba | Not listed | N single, TO-92 | ≈0.78 (3 mA), ≈0.71 (10 mA) r.b.e.; NF 1 dB @100 Ω | ≈1.3 derived (3 mA) | 40 at V_GS=0 (I_DSS 5 mA); ≈25 (2 mA) | 75 | 15 | 5–30 | −0.3…−1.2 | I_GSX ≈50 pA (1 mA) / 0.6 nA (10 mA) at 10 V | FOM ≈6.5; keep V_DS ≲ 6–8 V |
| 2SK389 | Toshiba | Not listed | N dual, SIP-7 | ≈1.27 (1 mA), ≈1.15 (3 mA) r.b.e. | ≈2.6 derived (1 mA) | 20 at V_GS=0; ≈18 (2 mA) | 25 | 5.5 | 2.6–20 | −0.15…−2.0 | I_GSX ≈5–7 pA at 10 V | FOM ≈6.4; ΔV_GS ≤20 mV |
| 2SK146 | Toshiba (requested as Hitachi) | Not checked | N dual, 6-pin | ≈0.76 (3 mA) r.b.e. | not given (NF 5 dB @100 Hz) | 40 at V_GS=0 | 75 | 15 | 5–30 | −0.3…−1.2 | like 2SK369 | FOM ≈6.6; ΔV_GS ≤20 mV |
| 2SK147 | Toshiba (requested as Hitachi) | Not checked | N single, TO-92MOD | not given (NF 1 dB @1 kHz, 100 Ω) | not given | 40 at V_GS=0 | 75 | 15 | 5–30 | −0.3…−1.2 | I_GSS ≤1 nA | 1-page sheet only |
| 2SJ74 | Toshiba | Not listed | P single, TO-92 | 0.95 (1 mA); ≈0.8 (3 mA) r.b.e. | NF 1.0 dB @1 kΩ (≈2 nV derived) | 22 at V_GS=0; ≈26 (2 mA) | 105 | 32 | −2.6…−20 | 0.15…2.0 | I_GSX ≈5 pA at −10 V | FOM ≈9.7 |
| 2SJ72 | Toshiba (requested as Hitachi) | Not checked | P single, TO-92MOD | ≈0.7 (3 mA) r.b.e. | not given (NF 5 dB @100 Hz) | 40 at V_GS=0 | 185 | 55 | −5…−30 | 0.3…2.0 | I_GX ≈2–3 pA to −10 V | FOM ≈9.5 |
| 2SK209 / 2SK880 / 2SK2145 | Toshiba | NRND | N single SOT-23 / SC-70 / dual SMV | ≈2.0 derived (0.5 mA, NF 1 dB @1 kΩ) | NF 5 dB @1 kΩ | 15 at V_GS=0 | 13 | 3 | 1.2–14 | −0.2…−1.5 | I_GSS ≤1 nA | FOM ≈7 (derived); 2SK2145 has no match spec |
| 2SK3557 | onsemi | Active | N single, CP (SC-59) | ≈2.0 derived (1 mA, 5 V) | ≈4.2 derived | 35 at V_GS=0; ≈16 (2 mA, r.b.e.) | 10.0 (V_GS 0, 5 V) | 2.9 | 10–32 (ranks 6/7) | −0.3…−1.5 | I_GSS ≤1 nA | FOM ≈6.4 (derived); 15 V max; model has no 1/f |
| CPH3910 | onsemi | "Active, Not Rec." | N single, CPH3 | not given (NF at 100 MHz only) | not given | 40 at V_GS=0; ≈14 (2 mA, r.b.e.) | 6.0 | 2.3 | 20–40 | −0.6…−1.8 | I_GSS ≤1 nA | RF part; no audio noise data |

## 7. Observations for choosing a JFET that beats the LSK389 on noise per unit input capacitance

1. On datasheet typical values the LSK389 has $e_n\sqrt{C_{iss}}$ ≈8 nV$\cdot\sqrt{\text{pF}}/\sqrt{\text{Hz}}$ (≈5.9 with the 1.17 nV app-note measurement). Parts that are lower by roughly 2× on paper: JFE2140 (≈4.0 at 2 mA, ≈3.2 at 5 mA), JFE150 (≈4.4 / 3.9), LSK489/LSK189 (≈3.6), LSK170 (≈4.0, but see C2). Among the large-die Toshiba parts, 2SK170 (≈5.2) and 2SK369/2SK146 (≈6.5) are better than the LSK389 sheet values but are no longer listed.
2. For the 20–40 pF front end, capacitive matching favors per-device $C_{iss}$ of order 5–20 pF: one or two JFE2140 halves (13 pF each, 1.1 nV at 2 mA) or a few LSK489/LSK189 (4 pF, 1.8 nV, $C_{rss}$ 2 pF, 60 V). For 0.3–1 nF, many parallel devices are needed; per-device current then matters: e.g. ≈12–40 JFE150 (24 pF each, 2–5 mA each) versus ≈4–13 2SK369-class devices (75 pF each) for the same 0.3–1 nF total.
3. 1/f corner (from typical table values): LSK170 and LSK189 ≈14 Hz, JFE150 ≈22 Hz at 2 mA (≈41 Hz at 5 mA), LSK489 ≈28 Hz, LSK389 ≈30 Hz, JFE2140 ≈38 Hz, LSJ689 ≈35–60 Hz, JFE2325 ≈500 Hz. TI gives 0.1–10 Hz peak-to-peak noise (0.09–0.13 µV$_{pp}$ for JFE150), LIS does not.
4. Gate current is the main difference at realistic drain voltages: TI JFE150/JFE2140 rise from sub-pA to ~1–10 nA between 6 V and 10 V (Figs. 6-5/6-6), so they require $V_{DS}\lesssim 5$ V (cascode) to keep $I_G$ in the pA range. LSK389/LSK170 stay at ≈1–5 pA up to ≈12 V; LSK489 ≈2 pA to ≈10 V; 2SK170 ≈5 pA at 10 V; 2SK369/2SK146 already ≈50 pA–0.6 nA at 10 V. At 1 pA the shot noise is $\sqrt{2qI_G}$ ≈0.57 fA/$\sqrt{\text{Hz}}$; at 1 nA it is ≈18 fA/$\sqrt{\text{Hz}}$, which matters for the high-impedance front end.
5. Availability: only the TI parts (Active) and LIS parts (listed) are current through-hole/SMD low-noise choices among these vendors; Toshiba's audio JFETs are discontinued or NRND, and the onsemi parts are RF-oriented (15–25 V, NF specified at 1 kΩ or 100 MHz) without audio-band $e_n$ or 1/f data.
