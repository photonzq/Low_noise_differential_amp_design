# Low-noise discrete JFET survey: InterFET, NXP BF862/BF861 and clones, Vishay/Siliconix legacy and second sources, other makers

Compiled 2026-11-19 for the input-stage selection of an SR560-class differential preamplifier (DC to 10 MHz; high-impedance front end with about 20 to 40 pF input capacitance; paralleled-JFET low-noise front end with 0.3 to 1 nF).
Companion survey (separate document): TI JFE150/JFE2140, Linear Integrated Systems LSK389/LSK489/LSK170, Toshiba/Hitachi legacy, onsemi/Sanyo. LSK389 numbers are therefore not repeated here; the InterFET IF389 (same N0132L geometry class, sold as an LSK389/2SK389 replacement) is used below as the in-scope proxy.

## Conventions

- Every value was read from the rendered page image of the cited file. File paths are relative to `refs/datasheets/jfet/`. "p." is the 1-based PDF page.
- "typ", "min", "max" are as printed. "(read by eye)" marks values read off a plotted curve; log/lin refers to the axis. Curve readings carry roughly +/-5 % (linear axes) to +/-15 % (log axes) uncertainty; BF862 Fig. 9 is coarser (see that section).
- "not given" means the document has no such entry. Nothing is inferred from other parts unless explicitly labelled "derived".
- 1/f corner: unless stated otherwise it is the frequency where the plotted $e_n$ equals $\sqrt{2}$ times the white floor (floor taken at the highest plotted frequency). Many of these curves fall more slowly than $f^{-1/2}$, so the asymptote-intersection definition is ill-defined; the $\sqrt{2}$ criterion is used throughout for comparability.
- Derived figures of merit (summary section): $e_n\sqrt{C_{iss}}$ (nV/$\sqrt{\mathrm{Hz}}\cdot\sqrt{\mathrm{pF}}$), which is invariant under paralleling identical devices at fixed current per device, and $f_T = g_{fs}/(2\pi C_{iss})$.
- Status: "listed" means the part appears on the vendor website selection table read on 2026-11-19. Mouser/Digi-Key price and stock were not checked.
- Values marked [D] were extracted from the same files at 300 dpi by a second reader during this survey and cross-checked against my own reading where marked "(checked)".

---

## 1. InterFET (Carrollton TX, USA)

General observations for all InterFET documents read:

- No InterFET data sheet carries an active/NRND/obsolete statement. All parts below were listed on interfet.com selection tables on 2026-11-19 (ordering column "Mouser" or "Direct"), so they are treated as active. The full JFET master table is served dynamically (25 rows per page); only the first page of each table was captured.
- InterFET SPICE models (CTC-023 / `interfet-spice-models.xlsx`) contain no KF/AF; SPICE noise from them is channel thermal noise only (see `sim/models/README_InterFET_NXP_others.md`).
- None of the InterFET data sheets read gives gate current versus $V_{DG}$ at drain current (impact ionisation). Only $I_{GSS}$ (and, for some, $I_{GSS}$ versus $V_{GDS}$ at $I_D=0$) is given. This is a gap for a high-impedance front end at $V_{DG}$ of 5 to 10 V and several mA.
- Geometry-level curves are partly templated (output families identical in shape across geometries; straight-line $C_{rss}$ curves on suppressed-zero axes). Treat curve readings from InterFET documents as indicative.

### 1.1 IF3601 (single, N3600L geometry)

File: `InterFET/InterFET_IF3601_datasheet_IF35076-R01.pdf` (Doc. IF35076.R01, April 2022, 4 pp.)

- Polarity/config: N-channel, single; TO-39 (IF3601T39), bare die COT/CFT 100/waffle pack (p.1 ordering table). Status: listed (IF3601T39, Mouser).
- Features (p.1): "Ultra Low Noise 0.35 nV/rtHz typical", "High Gain 175 mS typical", "Low Rds(on) 2.0 ohm typical". Product-summary column is mislabelled "IFN3601 Min" (p.1).
- Max ratings (p.2): $V_{RGS}$ -20 V; $I_{FG}$ 10 mA; $P_D$ 300 mW, derating 2 mW/°C; $T_J$ -55 to 125 °C; $T_{STG}$ -65 to 200 °C.
- $V_{(BR)GSS}$: -20 V min ($V_{DS}=0$, $I_G=-1$ µA) (p.2 Static).
- $I_{GSS}$: -0.1 nA max ($V_{GS}=-10$ V, $V_{DS}=0$, 25 °C); no typ, no elevated-T value (p.2).
- $V_{GS(off)}$: -0.35 V min to -2.0 V max ($V_{DS}=10$ V, $I_D=0.5$ nA) (p.2).
- $I_{DSS}$: 30 mA min, 300 mA typ ($V_{GS}=0$, $V_{DS}=10$ V, pulsed) (p.2).
- $g_{fs}$: 175 mS typ ($V_{DS}=10$ V, $V_{GS}=0$, f = 1 kHz) (p.2 Dynamic). No $g_{fs}$ vs $I_D$ curve.
- $C_{iss}$: 650 pF typ; $C_{rss}$: 80 pF typ ($V_{DS}=0$, $V_{GS}=-4$ V, 1 MHz) (p.2).
- $e_n$: 0.35 nV/$\sqrt{\mathrm{Hz}}$ typ ($V_{DS}=3$ V, $I_D=5$ mA, f = 100 Hz) (p.2). No max.
- "Typical Noise" curve, $V_{DS}=3$ V, $I_D=5$ mA, log f 10 Hz to 100 kHz, linear y (p.3, read by eye): 10 Hz 0.60; 20 Hz 0.52; 50 Hz 0.43; 100 Hz 0.37; 1 kHz 0.34; 10 kHz 0.335; 100 kHz 0.33 nV/$\sqrt{\mathrm{Hz}}$. 1/f corner ($\sqrt2$ criterion) about 30 Hz.
- "Typical Ciss - VGS", $V_{DS}=5$ V, 1 MHz (p.3, read by eye, linear): $V_{GS}$ = 0: 890 pF; -1 V: 600; -2 V: 410; -3 V: 320; -4 V: 290; -6 V: 270; -10 V: 250 pF.
- "Typical Crss - VGS", $V_{DS}=5$ V, 1 MHz (p.3, read by eye): 0 V: 84 pF; -2 V: 74; -4 V: 64; -6 V: 58; -10 V: 52 pF.
- "Typical IDSS - VGS(OFF)" (p.3, read by eye): about 85 mA at $V_{GS(off)}=-0.75$ V rising linearly to about 550 mA at -2.0 V. Output curves (p.3): $I_{DSS}$ about 170 to 180 mA for a $V_{GS(off)}=-1.0$ V device, about 540 to 560 mA for -2.0 V.
- Gate current at operating point / vs $V_{DG}$: not given. Duals data: n/a. SPICE text in document: none (models in CTC-023/xlsx: IF3601-M, IF3601-H).
- Doubts: (1) Table $C_{iss}$ 650 pF at $V_{DS}=0$, $V_{GS}=-4$ V versus curve 290 pF at $V_{DS}=5$ V, $V_{GS}=-4$ V; the extra 5 V on the drain cannot explain a factor 2.2. (2) The table $e_n$ is specified at 100 Hz but the curve gives about 0.37 there. (3) InterFET's web table lists $C_{iss}$ max 300 pF and $e_n$ 0.40 for IF3601; both disagree with the data sheet (650 pF typ, 0.35).

### 1.2 IF3602 (dual, N3600L geometry)

File: `InterFET/InterFET_IF3602_datasheet_IF35077-RevA01.pdf` (Doc. IF35077 Rev A01, December 2023, 5 pp.)

- Dual matched N-channel, TO-78 (IF3602T78), bare die 30/waffle pack, "bare die... designed for matched specifications but not 100 % tested" (p.1). "InterFET exclusive", similar part IF3601. Applications include hydrophone preamplifiers. Description: "presently the lowest noise JFET on the market" (p.1). Status: listed (IF3602T78, Mouser).
- Features (p.1): 0.35 nV/$\sqrt{\mathrm{Hz}}$ typ, 175 mS typ, "Low VGS(OFF) -1.5 typical", "Typical IDSS 300 mA", "Typical BVGSS -30 V", "High radiation tolerance".
- Max ratings (p.2, TO-78): $V_{RGS}$ -20 V; $I_{FG}$ 50 mA; $P_D$ 500 mW, derating 3.3 mW/°C (footnote: gate pin thermally connected to pad/internal layer); $T_J$ and $T_{STG}$ -65 to 175 °C.
- $V_{(BR)GSS}$ -20 V min; $I_{GSS}$ -0.5 nA max ($V_{GS}=-10$ V); $V_{GS(off)}$ -0.35 to -3.0 V ($V_{DS}=10$ V, $I_D=0.5$ nA); $I_{DSS}$ 30 mA min, 300 typ (p.2 Static).
- $g_{fs}$ 175 mS typ; $C_{iss}$ 650 pF typ; $C_{rss}$ 80 pF typ; $e_n$ 0.35 nV/$\sqrt{\mathrm{Hz}}$ typ — all at the same conditions as IF3601 (p.2 Dynamic).
- $|V_{GS1}-V_{GS2}|$: 100 mV max ($V_{DS}=10$ V, $I_D=500$ pA) (p.2). No drift, $I_{DSS}$ ratio, CMRR or $g_{fs}$ ratio given.
- Curves (p.3): identical to the IF3601 page (same noise, $C_{iss}$, $C_{rss}$, $I_{DSS}$ and output plots); readings as in 1.1.
- Doubts: "Typical BVGSS -30 V" (p.1) versus $V_{(BR)GSS}$ -20 V min and $V_{RGS}$ -20 V (p.2) - not contradictory but the rating is -20 V. Matching at $I_D=500$ pA says nothing about matching at a mA operating point; 100 mV is loose for a DC-coupled differential stage. $C_{iss}$ inconsistency as in 1.1.

### 1.3 IF9030 (single, N0903L geometry)

File: `InterFET/InterFET_IF9030_datasheet_IF35074-R01.pdf` (Doc. IF35074.R01, 5 pp.)

- Features (p.1): 0.7 nV/$\sqrt{\mathrm{Hz}}$ typ; 150 mS typ; $R_{DS(on)}$ 6.0 ohm typ. Single N-channel.
- Max (p.2): $V_{RGS}$ -20 V; $I_{FG}$ 10 mA; $P_D$ 300 mW, 2.4 mW/°C; $T_J$ -55 to 125 °C; $T_{STG}$ -65 to 200 °C.
- $V_{(BR)GSS}$ -20 V min; $I_{GSS}$ -0.1 nA max ($V_{GS}=-10$ V); $V_{GS(off)}$ -0.35 to -2.0 V ($V_{DS}=10$ V, 0.5 nA); $I_{DSS}$ 30 min / 100 typ / 300 max mA ($V_{DS}=10$ V, pulsed) (p.2).
- $g_{fs}$ 80 mS min, 150 typ ($V_{DS}=10$ V, $V_{GS}=0$, 1 kHz); $C_{iss}$ 60 pF max, $C_{rss}$ 20 pF max ($V_{DS}=10$ V, $I_D=5$ mA, 1 MHz); $e_n$ 0.7 typ ($V_{DS}=4$ V, $I_D=5$ mA, 1 kHz) (p.2).
- "Typical GFS - VGS(OFF)" ($V_{GS}=0$, $V_{DS}=10$ V, 1 kHz; p.3, read by eye): $V_{GS(off)}$ -0.5 V: 25 mS; -1.0 V: 150; -1.5 V: 205; -2.5 V: 232 mS. "Typical IDSS - VGS(OFF)": about 40 mA at -0.75 V to about 330 mA at -2.5 V (read by eye).
- No noise-vs-frequency or capacitance curves; gate current vs $V_{DG}$ not given. Web table values for IF9034/IF9035 (same geometry, dual) agree with these limits.

### 1.4 IF4500 (single, N0450L geometry)

File: `InterFET/InterFET_IF4500_datasheet_IF35069-RevA01.pdf` (Doc. IF35069 Rev A01, 7 pp.)

- Features (p.1): 0.85 nV/$\sqrt{\mathrm{Hz}}$ typ; "High gain 65 mS typical"; "Low gate leakage 1.5 pA typical @10V"; $V_{GS(off)}$ -1.0 V typ; $I_{DSS}$ 30 mA typ; "Typical BVGSS -35 V"; high radiation tolerance. Packages TO-18 and SOT-23. Status: listed (IF4500ST3, Mouser).
- Max (p.2): $V_{RGS}$ -20 V; $I_{FG}$ 50 mA; $P_D$ 500 mW (TO-18) / 350 mW (SOT-23), derating 3.3 / 2.8 mW/°C; $T_J$ -65 to 175 °C (TO-18), -55 to 150 °C (SOT-23).
- $V_{(BR)GSS}$ -20 V min; $I_{GSS}$ -0.1 nA max ($V_{GS}=-20$ V); $V_{GS(off)}$ -0.35 to -1.5 V ($V_{DS}=15$ V, 0.5 nA); $I_{DSS}$ 5 mA min, 30 typ ($V_{DS}=15$ V) (p.2).
- $g_{fs}$ 15 mS min, 70 typ ($V_{DS}=15$ V, $I_D=5$ mA, 1 kHz); $C_{iss}$ 35 pF max, $C_{rss}$ 15 pF max ($V_{DS}=15$ V, $V_{GS}=0$, 1 MHz); $e_n$ 0.85 typ ($V_{DS}=4$ V, $I_D=5$ mA, 1 kHz) (p.2).
- "Typical Noise", $I_D=5$ mA, $V_{DS}=4$ V (p.4, read by eye, log f, linear y): 10 Hz 1.10; 100 Hz 0.97; 1 kHz 0.88; 10 kHz 0.83; 100 kHz 0.80 nV/$\sqrt{\mathrm{Hz}}$. 1/f corner about 10 Hz.
- "Typical Ciss vs VGS @ 1 MHz" (p.4, read by eye): $V_{DS}=5$ V: 0 V 58 pF; -1 V 36; -2 V 31; -5 V 23; -10 V 19 pF. $V_{DS}=10$ V: 0 V 55 pF; -1 V 33. $V_{DS}=15$ V: about 52 pF at 0 V.
- "Typical Crss vs VGS" (p.4, read by eye): $V_{DS}=5$ V: 0 V 25 pF; -2 V 19; -5 V 12; -10 V 10 pF. $V_{DS}=10$ V: 23.5 pF at 0 V.
- "Typical IGSS vs VGDSS" (p.4, read by eye): -4 V: 0.5 pA; -10 V: 1.3 pA; -20 V: 4 pA. $I_G$ at drain current: not given.
- Doubts: (1) Curve $C_{iss}$ about 52 to 58 pF at $V_{GS}=0$ exceeds the table maximum of 35 pF at the same nominal condition. (2) $g_{fs}$ 70 mS typ at 5 mA implies $g_m/I_D = 14$ V$^{-1}$, implausibly high for a strongly-on JFET; p.1 says 65 mS. (3) SPICE model (xlsx) uses CGS = CGD = 38 pF at zero bias, consistent with the curves rather than the 35 pF table maximum.

### 1.5 IFN860 (dual, N0450L geometry) — not a BF862 replacement

File: `InterFET/InterFET_IFN860_datasheet_IF35070-R00.pdf` (Doc. IF35070.R00, April 2020, 4 pp.)

- Dual N-channel: TO-71 (IFN860), SOIC-8 (SMP860, SMP860TR), bare die 70/waffle pack (p.1). Application "Similar to Crystalonics CD860"; no BF862 claim anywhere in the document.
- Features (p.1): 0.9 nV/$\sqrt{\mathrm{Hz}}$ typ (no conditions); 40 mS typ; -20 V part.
- Max (p.2): $V_{RGS}$ -20 V; $I_{FG}$ 50 mA; $P_D$ 400 mW, 2.3 mW/°C; $T_J$ -55 to 125 °C; $T_{STG}$ -65 to 200 °C.
- $V_{(BR)GSS}$ -20 V min; $I_{GSS}$ 3 nA max ($V_{GS}=-10$ V); $V_{GS(off)}$ -0.3 to -3 V ($V_{DS}=10$ V, $I_D=100$ µA); $I_{DSS}$ 10 mA min (p.2).
- $|V_{GS1}-V_{GS2}|$ 25 mV max ($V_{DS}=10$ V, $I_D=100$ µA) (p.2).
- $g_{fs}$ 25 mS min, 40 typ; $C_{iss}$ 30 typ / 35 max pF; $C_{rss}$ 17 typ / 20 max pF — all at $V_{DS}=10$ V, $I_D$ "-10 mA" (sign typo), 1 kHz / 1 MHz (p.2).
- $e_n$: 2 nV/$\sqrt{\mathrm{Hz}}$ max ($V_{DG}=3$ V, $I_D=10$ mA, 1 kHz); no typ in the table (p.2).
- No curves; gate current vs $V_{DG}$ not given.
- Note: $f_T$ derived from the table at one consistent operating point (10 mA): $40\,\mathrm{mS}/(2\pi\cdot30\,\mathrm{pF}) \approx 210$ MHz. $C_{rss}/C_{iss} = 0.57$ is unusually large (strong Miller multiplication unless cascoded).

### 1.6 IFN146 (dual, N0450H geometry) and IFN147 (single)

Files: `InterFET/InterFET_IFN146_datasheet_IF35066-R00.pdf` (Doc. IF35066.R00, December 2018, 4 pp.); `InterFET/InterFET_IFN147_datasheet_IF35067-R00.pdf` (Doc. IF35067.R00, 5 pp.)

IFN146:
- Dual N-channel, TO-71 and SOIC-8 (SMP146), bare die; "replacement for the Japanese 2SK146"; "Gate leakages are typically less than 50 pA at room temperatures" (p.1). Status: listed (Mouser).
- Features (p.1): 1.1 nV/$\sqrt{\mathrm{Hz}}$ typ (no conditions), 30 mS typ. Product summary: $I_{DSS}$ "30 (max)".
- Max (p.2): $V_{RGS}$ -40 V; $I_{FG}$ 10 mA; $P_D$ 375 mW, 3 mW/°C; $T_J$ -55 to 125 °C.
- $V_{(BR)GSS}$ -40 V min; $I_{GSS}$ -1 nA max at 25 °C and -1 µA max at 150 °C ($V_{GS}=-30$ V); $V_{GS(off)}$ -0.3 to -1.2 V ($V_{DS}=10$ V, 1 µA); $I_{DSS}$ 30 mA max (p.2).
- $g_{fs}$ 20 mS min, 30 typ ($V_{DS}=10$ V, $V_{GS}=0$, "$I_{DSS}=5$ mA", 1 kHz); $C_{iss}$ 75 pF max ($V_{DS}=10$ V, $V_{GS}=0$, f = 1 kHz); $C_{rss}$ 15 pF max ($V_{DS}=10$ V, $I_D=0$, 1 kHz); NF 1 dB typ ($V_{DS}=10$ V, $I_D=5$ mA, $R_G=100$ ohm, 1 kHz); $|V_{GS1}-V_{GS2}|$ 20 mV max ($V_{DS}=10$ V, $I_D=5$ mA) (p.2).
- $e_n$ in table: not given (only the p.1 feature value). No curves.
- Derived check: NF = 1 dB with $R_G=100$ ohm implies $e_n \approx 0.65$ nV/$\sqrt{\mathrm{Hz}}$ (with $4kTR_G$ = 1.29 nV/$\sqrt{\mathrm{Hz}}$ at 300 K); 1.1 nV/$\sqrt{\mathrm{Hz}}$ would give NF about 2.4 dB. The two numbers are not mutually consistent.

IFN147:
- Single N-channel, "Replacement for Japanese 2SK147"; 1.1 nV/$\sqrt{\mathrm{Hz}}$ typ, 30 mS typ (p.1).
- Max (p.2): $V_{RGS}$ -40 V; $I_{FG}$ 10 mA; $P_D$ 300 mW, 2.4 mW/°C; $T_J$ -55 to 125 °C.
- Static table (p.2) is headed "IFN113" (copy error): $V_{(BR)GSS}$ -40 V min; $I_{GSS}$ -1 nA (25 °C) / -1 µA (150 °C) max at $V_{GS}=-30$ V; $V_{GS(off)}$ -0.3 to -1.2 V; $I_{DSS}$ 5 to 30 mA.
- $g_{fs}$ 20 min / 30 typ mS; $C_{iss}$ 75 pF max; $C_{rss}$ 15 pF max (same conditions as IFN146); NF 1 dB typ at 1 kHz and 10 dB max at 100 Hz ($V_{DS}=10$ V, $I_D=5$ mA, $R_G=100$ ohm) (p.2).

### 1.7 IF170A/B/C/D (single, N0132L geometry; 2SK170-type)

File: `InterFET/InterFET_IF170A-B-C-D_datasheet_docno-SP_Apr2024.pdf` (document number printed as "SP" placeholder, April 2024, 8 pp.)

- Single N-channel, -30 V; TO-72, TO-92, SOT-23, bare die (p.1). Industry crosses (p.1): 2SK152, 2SK170, 2N6451, 2N6452, 2N3972, MMBF4393, NSVJ3557SA3, NSVJ5908DSG5, NSVJ2394SA3. Dual option IF389x.
- Features (p.1): 1.0 nV/$\sqrt{\mathrm{Hz}}$ typ; 22 mS typ; "Low gate leakage 750 fA typical @10V"; high radiation tolerance.
- Max (p.2): $V_{RGS}$ -30 V; $I_{FG}$ 50 mA; $P_D$ 500 mW (TO-72), 350 mW (SOT-23), 500 mW (TO-92); derating 3.3 / 2.8 / 4 mW/°C; $T_J$ -65 to 175 (TO-72), -55 to 150 °C (SOT-23, TO-92).
- $V_{(BR)GSS}$ -30 V min; $I_{GSS}$ -0.1 nA max ($V_{GS}=-10$ V); $V_{GS(off)}$ -0.2 to -2.0 V ($V_{DS}=10$ V, 1 nA); $I_{DSS}$ A 2.6-6.5, B 6.0-12.0, C 10.0-20.0, D 18.0-30.0 mA ($V_{DS}=10$ V) (p.2).
- $g_{fs}$ 14 mS min ($V_{DS}=10$ V, $V_{GS}=0$, 1 kHz); "GFS(TYP)" 6 mS min ($V_{DS}=15$ V, $I_D=1$ mA); $C_{iss}$ 20 pF max, $C_{rss}$ 4.5 pF max ($V_{DS}=10$ V, $I_D=2$ mA, 1 MHz); $e_n$ 1.0 typ ($V_{DS}=10$ V, $I_D=2$ mA, 1 kHz) (p.2).
- "Typical Noise", $I_D=5$ mA, $V_{DS}=4$ V (p.4, read by eye): 10 Hz 1.70 (re-read on 2026-11-21; first reading 1.72); 100 Hz 1.20; 1 kHz 1.00; 10 kHz 0.95; 100 kHz 0.92 nV/$\sqrt{\mathrm{Hz}}$. Corner about 60 Hz.
- "Typical Ciss vs VGS @ 1 MHz" (p.4, read by eye): $V_{DS}=5$ V: 0 V 17.5; -1 V 12.5; -2 V 10.2; -4 V 9.0; -10 V 7.3 pF. $V_{DS}=10$ V: 0 V 16.5; -2 V 9.6; -10 V 7.0. $V_{DS}=15$ V: 0 V 16; -10 V 6.9 pF.
- "Typical Crss vs VGS" (p.4, read by eye): $V_{DS}=5$ V: 0 V 8.0; -1 V 5.0; -2 V 4.4; -5 V 4.0; -10 V 3.6 pF. $V_{DS}=10$ V: 7.2 / 4.0 (-2 V) / 2.9 (-10 V). $V_{DS}=15$ V: 6.3 / 3.6 / 2.7 pF.
- "Typical IGSS vs VGDSS" (p.4, read by eye): -4 V 0.18 pA; -10 V 0.62 pA; -20 V 2.1 pA.
- "Typical GFS vs VGS(OFF)" (p.3, read by eye; $g_{fs}$ at $I_{DSS}$): -0.6 V 15 mS; -1 V 22; -2 V 32; -3 V 37; -5 V 40.5 mS.

### 1.8 IF389A/B/C/D (dual, N0132 geometry; 2SK389/LSK389-type)

File: `InterFET/InterFET_IF389A-B-C-D_datasheet_IF35111-R00.pdf` (Doc. IF35111.R00, February 2020, 6 pp.)

- Matched dual, TO-71 and SOIC-8 ("thermally optimised", pin-out differs from LSK389x), bare die; "Replacement Parts for 2SK389 and LSK389x" (p.1). Status: listed ("Direct" ordering).
- Features (p.1): 1.0 nV/$\sqrt{\mathrm{Hz}}$ typ; 24 mS typ; cut-off 2.0 V max. Product summary $g_{fs}$ (typ): A 15, B 20, C 24, D 28 mS.
- Max (p.2): $V_{RGS}$ -30 V; $I_{FG}$ 10 mA; $P_D$ 300 mW, 1.8 mW/°C; $T_J$ -55 to 135 °C; $T_{STG}$ -65 to 200 °C.
- $V_{(BR)GSS}$ -30 V min; $I_{GSS}$ -0.1 nA max ($V_{GS}=-10$ V); $V_{GS(off)}$ -0.2 to -2.0 V; $I_{DSS}$ A 2.6-6.5, B 6.0-12.0, C 10.0-20.0, D 18.0-30.0 mA (p.2).
- $g_{fs}$ 14 mS min ($V_{DS}=10$ V, $V_{GS}=0$); "GFS(TYP)" 6 mS min (15 V, 1 mA); $C_{iss}$ 20 pF max, $C_{rss}$ 4.5 pF max (10 V, 2 mA, 1 MHz); $e_n$ 1.0 typ (10 V, 2 mA, 1 kHz); $|V_{GS1}-V_{GS2}|$ 30 mV max ($V_{DS}=10$ V, $I_D=1$ mA) (p.2). No drift or CMRR spec.
- "Typical Noise", $V_{DS}=4$ V, $I_D=5$ mA (p.4, read by eye): 10 Hz 2.05; 100 Hz 1.35; 1 kHz 1.00; 10 kHz 0.95; 100 kHz 0.90 nV/$\sqrt{\mathrm{Hz}}$. Corner about 120 Hz.
- "Typical Ciss - VGS", $V_{DS}=10$ V, 1 MHz (p.4, read by eye): 0 V 19.5; -2 V 13.2; -4 V 9.7; -6 V 8.2; -10 V 7.6 pF. "Typical Crss - VGS": 3.7 pF at 0 V, 3.2 at -5 V, 2.7 at -10 V (straight line).
- Doubt: the IF170 and IF389 data sheets share the N0132L geometry and identical tables, but their typical noise curves differ at 10 Hz (1.70 vs 2.05 nV/$\sqrt{\mathrm{Hz}}$).

### 1.9 IF150A/B/C (single, N0014LX geometry; low-capacitance)

File: `InterFET/InterFET_IF150A-B-C_datasheet_IF35119-RevA01.pdf` (Doc. IF35119 Rev A01, 7 pp.)

- Single N-channel; TO-72 and SOT-23 (p.1). Crosses: IF142, BF512, SST4416, SST4416A, MMBF4416, MMBF4416A, MMBF5485, SSTJ211; similar parts include IF140/IF140A; dual parts IFN5911/IFN5912 (p.1). Status: listed ("Direct").
- Features (p.1): "Low gate leakage 100 fA typical @5V"; "Low Ciss 3 pF typical"; "Typical noise 3.0 nV/rtHz"; "Typical gain 7 mS"; high radiation tolerance.
- Max (p.2): $V_{RGS}$ -10 V (low!); $I_{FG}$ 50 mA; $P_D$ 500 mW (TO-72) / 350 mW (SOT-23); derating 3.3 / 2.8 mW/°C; $T_J$ -65 to 175 / -55 to 150 °C.
- $V_{(BR)GSS}$ -10 V min; $I_{GSS}$ -5 pA max at 25 °C, -200 pA max at 150 °C ($V_{GS}=-5$ V); $V_{GS(F)}$ 1 V max (p.2).
- $V_{GS(off)}$ ($V_{DS}=8$ V, 5 nA): A -0.8 to -2.0; B -1.8 to -3.2; C -3.0 to -6.0 V. $I_{DSS}$ ($V_{DS}=8$ V): A 0.5-3.5; B 3.0-10; C 8-22 mA (p.2).
- $g_{fs}$ min ($V_{DS}=8$ V, $V_{GS}=0$, 1 kHz): A 1.0, B 3.0, C 5.0 mS; $g_{os}$ 0.05 mS max; $C_{iss}$ 3 pF max; $C_{rss}$ 1.2 pF max ($V_{DS}=8$ V, $V_{GS}=0$, 1 MHz); $e_n$ 3 nV/$\sqrt{\mathrm{Hz}}$ typ at **10 Hz** ($V_{DS}=8$ V, $V_{GS}=0$) (p.2).
- "Typical Noise", $I_D=500$ µA, $V_{DS}=4$ V (p.4, read by eye): 10 Hz 5.5; 100 Hz 4.1; 1 kHz 3.4; 10 kHz 3.0; 100 kHz 2.85 nV/$\sqrt{\mathrm{Hz}}$. Corner about 120 Hz.
- "Typical Ciss vs VGS @ 1 MHz" (p.4, read by eye): $V_{DS}=5$ V: 0 V 2.9; -2 V 2.15; -4 V 1.98; -10 V 1.85 pF; $V_{DS}=10$ V: 2.83 at 0 V, 1.80 at -10 V.
- "Typical Crss vs VGS" (p.4, read by eye): $V_{DS}=5$ V: 1.41 (0 V), 1.20 (-2 V), 1.10 (-5 V), 1.07 pF (-10 V); $V_{DS}=10$ V: 1.27 (0 V), 1.04 pF (-10 V).
- "Typical IGSS vs VGDSS" (p.4, read by eye): -5 V about 0.09 pA; -10 V about 0.18 pA.
- "Typical GFS vs VGS(OFF)" (p.3, read by eye): -1 V 2.9; -2 V 5.1; -4 V 8.1; -6 V 8.6 mS. "IDSS vs VGS(OFF)": -1 V 1.2; -2 V 4.8; -4 V 14; -6 V 24 mA.
- Doubts: the table's 3 nV/$\sqrt{\mathrm{Hz}}$ at 10 Hz is at $I_D=I_{DSS}$; the only curve (500 µA) gives 5.5 at 10 Hz. $I_{GSS}$ rising only 40x from 25 to 150 °C (-5 pA to -200 pA max) is far below the usual ~1000x and may be a limit rather than a characteristic. $V_{(BR)GSS}$ of -10 V restricts $V_{DG}$ headroom.

### 1.10 IFN5564/IFN5565/IFN5566 (dual, N0072S geometry)

File: `InterFET/InterFET_IFN5564-IFN5565-IFN5566_datasheet_IF35051-R00.pdf` (Doc. IF35051.R00, December 2018, 4 pp.); geometry `InterFET/InterFET_geometry_N0072S_IF35511-R02.pdf` (Doc. IF35511.R02, March 2020).

- Dual matched, TO-71 and SOIC-8 (SMP556x; ordering table wrongly labels SOIC-8 "Through-Hole"), bare die (p.1). Status: listed (IFN5564, Mouser).
- Features (p.1): 2.5 nV/$\sqrt{\mathrm{Hz}}$ typ (no conditions); "Low leakage 10 pA typ"; "Low input capacitance 6.5 pF typ".
- Max (p.2): $V_{RGS}$ -40 V; $I_{FG}$ 50 mA; $P_D$ 650 mW, 3.3 mW/°C; $T_J$ -55 to 150 °C; $T_{STG}$ -65 to 200 °C.
- $V_{(BR)GSS}$ -40 V min; $I_{GSS}$ -100 pA max (25 °C), -200 nA max (150 °C) at $V_{GS}=-20$ V; $V_{GS(off)}$ -0.5 to -3 V ($V_{DS}=15$ V, 1 nA); $V_{GS(F)}$ 1 V max; $I_{DSS}$ 5 to 30 mA; $R_{DS(on)}$ 100 ohm max (p.2) (checked).
- $g_{fs}$ 7000 µmho min, 12500 max ($V_{DS}=15$ V, $I_D=2$ mA, 1 kHz) and 7000 min at 100 MHz; $g_{os}$ 45 µmho max; $C_{iss}$ 12 pF max; $C_{rss}$ 3 pF max ($V_{DS}=15$ V, $I_D=2$ mA, 1 MHz); NF 1 dB max (10 Hz, $R_G=1$ MΩ); $e_n$ 50 nV/$\sqrt{\mathrm{Hz}}$ max at 10 Hz ($V_{DS}=15$ V, $I_D=2$ mA) (p.2) (checked).
- Matching (p.2): $I_{DSS1}/I_{DSS2}$ 0.95-1; $|V_{GS1}-V_{GS2}|$ 5 / 10 / 20 mV max; drift printed as "0.8 | 1", "2 | 2.5", "4 | 5" with unit "mV/°C" for the spans 25 to -55 °C and 25 to 125 °C - these are total mV changes, i.e. 10 / 25 / 50 µV/°C (unit error in the document); $g_{fs1}/g_{fs2}$ 0.95-1 (5564), 0.9-1 (5565/66).
- Geometry N0072S, "Typical Noise" $I_D=5$ mA, $V_{DS}=15$ V (p.4, read by eye) [D]: 10 Hz 3.6; 100 Hz 2.7; 1 kHz 2.0; 10 kHz 1.85; 100 kHz 1.77 nV/$\sqrt{\mathrm{Hz}}$; corner 130 to 175 Hz. Geometry table: $e_n$ 2.0 typ (15 V, 5 mA, 1 kHz); $C_{iss}$ 7 pF typ, $C_{rss}$ 2.5 pF typ ($V_{DS}=0$, $V_{GS}=-10$ V); $I_{GSS}$ -10 pA typ (p.2) [D].
- Geometry $C_{iss}$ vs $V_{GS}$, $V_{DS}=10$ V (p.4) [D]: 0 V 9.2; -1 V 7.2; -2 V 6.2; -4 V 5.0; -10 V 4.7 pF. $C_{rss}$: 2.6 pF (0 V) to 2.35 pF (-10 V).
- Doubts: the only guaranteed noise number is 50 nV/$\sqrt{\mathrm{Hz}}$ max at 10 Hz; geometry ratings differ from the part ($I_{FG}$ 10 vs 50 mA, $V_{(BR)GSS}$ -30 min for the die vs -40 V for the part).

### 1.11 2N4391/2N4392/2N4393 (InterFET, N0132S geometry) — low-noise reference only [D]

File: `InterFET/InterFET_2N4391-2N4392-2N4393_datasheet_IF35060-R00.pdf` (Doc. IF35060.R00, December 2018); geometry `InterFET/InterFET_geometry_N0132S_IF35514-R01.pdf`.

- 2N4393: $V_{GS(off)}$ -0.5 to -3 V; $I_{DSS}$ 5 to 30 mA; $V_{(BR)GSS}$ -40 V; $I_{GSS}$ -100 pA max (conditions printed as "VDS = -20V, VGS = 0V", evidently swapped); $C_{iss}$ 14 pF max ($V_{DS}=20$ V, $V_{GS}=0$); $C_{rss}$ 3.5 pF max; $R_{DS(on)}$ 100 ohm max (p.2). No $g_{fs}$ or $e_n$ in the data sheet (p.1 feature: 1.2 nV/$\sqrt{\mathrm{Hz}}$ typ, no conditions).
- Geometry N0132S: $e_n$ 1.2 typ ($V_{DS}=4$ V, $I_D=5$ mA, 1 kHz); curve 10 Hz 2.30, 100 Hz 1.60, 1 kHz 1.10, 10 kHz 1.05, 100 kHz 1.00 (read by eye); $C_{iss}$ 13 pF typ ($V_{DS}=10$ V, $V_{GS}=0$); $g_{fs}$ 32 mS typ at $I_{DSS}$; $I_{GSS}$ -50 pA typ (p.2, p.4).

### 1.12 U310 (InterFET, N0072L geometry) [D]

File: `InterFET/InterFET_U310_datasheet_IF35047-R00.pdf` (Doc. IF35047.R00, June 2019); geometry `InterFET/InterFET_geometry_N0072L_IF35512-R02.pdf`.

- $V_{(BR)GSS}$ -25 V; $I_{GSS}$ -150 pA max ($V_{GS}=-15$ V); $V_{GS(off)}$ -2.5 to -6 V; $I_{DSS}$ 24 to 60 mA; $g_{fs}$ 10 min / 17 typ mS ($V_{DS}=10$ V, $I_D=10$ mA, 1 kHz); $C_{gs}$ 5 pF max, $C_{dg}$ 2.5 pF max ($V_{DS}=10$ V, $V_{GS}=-10$ V); $e_n$ "10 nV/$\sqrt{\mathrm{Hz}}$ typ at 100 kHz" (p.2, probably an error: p.1 says 2 nV/$\sqrt{\mathrm{Hz}}$; geometry curve 1.7 at 100 kHz, 1.95 at 1 kHz, 3.4 at 10 Hz for 5 mA, 15 V). Geometry document lists U430/U431 as standard parts on N0072L.

### 1.13 Other InterFET parts in scope, downloaded but not read in detail

Values below are from InterFET's "Low-Noise High-Gain" web selection table (https://interfet.com/low-noise-high-gain/, read 2026-11-19), not from the data sheets; they are not authoritative.

| Part | File | Web table: BVgss / Vgs(off) / Idss / Gm min / $e_n$ typ / Ciss max |
|---|---|---|
| 2N6451, 2N6452 | `InterFET_2N6451-2N6452_datasheet_IF35054-RevA01.pdf` | -20/-25 V; -0.5 to -3.5 V; 5-20 mA; 15 mS; 1.0; 25 pF |
| 2N6453, 2N6454 | `InterFET_2N6453-2N6454_datasheet_IF35055-RevA01.pdf` | -20/-25 V; -0.75 to -5.0 V; 15-50 mA; 20 mS; 1.0; 25 pF |
| 2N6550 | `InterFET_2N6550_datasheet_IF35068-RevA01.pdf` | -20 V; -0.3 to -3.0 V; 10-100 mA; 25 mS; 0.9; 35 pF |
| IF1320 | `InterFET_IF1320_datasheet_IF35056-RevA01.pdf` | -20 V; -0.35 to -1.5 V; 5-20 mA; 15 mS; 1.0; 20 pF |
| IF1322/IF1322A (dual) | `InterFET_IF1322-IF1322A_datasheet_IF35095-R01.pdf` | -20 V; -0.8 to -1.5 V; 8-25 mA; 10 mS; 2.0; 15 pF |
| IF140/IF140A | `InterFET_IF140-IF140A_datasheet_IF35005-RevA01.pdf` | -20 V; -2.5 to -6.0 V (IF140A); 5-15 mA; 3.5 mS; 4.0; 3 pF |
| IF9034/IF9035 (dual) | `InterFET_IF9034-IF9035_datasheet_IF35108-R00.pdf` | -20 V; -0.35 to -2.0 V; 30-300 mA; 80 mS; 0.70; 60 pF |
| IFN152 | `InterFET_IFN152_datasheet_docno-blank.pdf` (document number field blank) | not in the captured table rows |

- IF142: no InterFET data sheet on interfet.com (URL pattern returns 404); IF142 is listed as an "industry standard cross" for IF150 (IF150 data sheet p.1).
- IF1801 and IFN421: no InterFET data sheet found on interfet.com (404 for the usual URL patterns); only 1999-era copies on third-party aggregator sites, not downloaded and not used.
- IFN170: no such part found; the 2SK170-type part is IF170 (section 1.7). "IFN2N4393" corresponds to InterFET 2N4393 (section 1.11).
- Geometry documents downloaded (N3600L, N0903L, N0450L, N0450H, N0450S, N0132L, N0132S, N0132H, N0014L, N0014X, N0072S, N0072L, N0026L, N0026S, N9000L); only N0072S, N0132S, N0072L were read [D]. N0450L and N0450H both carry document number IF35518.R00; the file served as "n9000l" is a one-page sheet whose PDF title is "jfet-n0001h-geometry-interfet".

---

## 2. NXP BF862 / BF861 and BF862 replacements

### 2.1 NXP BF862 (single, SOT-23)

File: `NXP/NXP_BF862_product-data-sheet_2000-01-05_NXP-rev3.1-2010.pdf` (Product specification dated 2000 Jan 05, supersedes 1999 Jun 29; NXP product page lists it as data sheet Rev 3.1, 2010-12-02; 11 pp.)

- Status: "No Longer Manufactured" on https://www.nxp.com/products/BF862 (read 2026-11-19; no date given). Nexperia does not list JFETs.
- Symmetrical N-channel JFET, SOT-23, drain/source interchangeable; marking 2Ap; aimed at AM car-radio preamplifiers (p.2).
- Limiting values (p.3): $V_{DS}$ 20 V; $V_{DG}$ 20 V; $V_{GS}$ -20 V; $I_{DS}$ 40 mA; $I_G$ 10 mA; $P_{tot}$ 300 mW at $T_s \le 90$ °C (heat via gate lead); $T_{stg}$ -65 to +150 °C; $T_j$ 150 °C; $R_{th\,j\text{-}s}$ 200 K/W.
- Static (p.4, $T_j=25$ °C): $V_{(BR)GSS}$ -20 V min; $V_{GS}$ forward 1 V max ($I_G=1$ mA); $V_{GSoff}$ -0.3 min / -0.8 typ / -1.2 max V ($V_{DS}=8$ V, $I_D=1$ µA); $I_{GSS}$ -1 nA max ($V_{GS}=-15$ V); $I_{DSS}$ 10 to 25 mA ($V_{DS}=8$ V).
- Dynamic (p.4, common source, $V_{GS}=0$, $V_{DS}=8$ V, i.e. at $I_D=I_{DSS}$): $|y_{fs}|$ 35 min / 45 typ mS; $g_{os}$ 180 typ / 400 max µS; $C_{iss}$ 10 pF typ; $C_{rss}$ 1.9 pF typ (1 MHz); $e_n$ 0.8 nV/$\sqrt{\mathrm{Hz}}$ typ at **100 kHz**; $f_T$ 715 MHz typ.
- No $e_n$ versus frequency or versus $I_D$ curve; 10 Hz and 1 kHz noise not given in the data sheet.
- Fig.3 (p.5, read by eye): $I_{DSS}$ 0 at $V_{GSoff}\approx-0.42$ V, 15 mA at -0.75 V, 25 mA at -1.0 V, 32 mA at -1.25 V.
- Fig.4 (p.5): $g_{os}$ about 118 µS at $I_{DSS}=10$ mA to about 245 µS at 25 mA.
- Fig.6, $|y_{fs}|$ vs $I_D$, $V_{DS}=8$ V (p.5, read by eye, linear): 2 mA 19; 5 mA 28; 10 mA 37; 15 mA 42; 20 mA 46; 25 mA 48 mS.
- Fig.10, $C_{is}$ and $C_{rs}$ vs $V_{GS}$, $V_{DS}=8$ V, 1 MHz (p.6, read by eye): $C_{is}$ 10.5 pF at 0 V; 5.5 at -0.5 V; 5.0 at -1 V; 4.5 at -2 V; 4.0 at -4 V; 3.4 pF at -7.5 V. $C_{rs}$ about 1.9 pF at 0 V to 1.6 pF at -7.5 V.
- Fig.9, $I_G$ vs $V_{DG}$ for $I_D$ = 0.1, 1, 10, 20 mA (p.6, log y from -0.1 pA to -10 µA with labels every two decades; read by eye, coarse, about factor 3): $I_{GSS}$ about 2 to 5 pA at 1 to 5 V rising to about 10 pA at 20 V. With drain current the gate current leaves the $I_{GSS}$ line at $V_{DG}\approx4$ V (20 mA), 5 V (1 mA), 6 V (0.1 mA). At $V_{DG}=10$ V: roughly 0.1 nA at 0.1 mA, a few nA at 1 mA, tens of nA at 10 to 20 mA. At $V_{DG}=15$ V: roughly 10 to 30 nA (0.1 mA), 0.1 to 0.3 µA (1 mA), about 1 to 3 µA (10 to 20 mA). Caption says "$V_{DS}=8$ V" although the x-axis is $V_{DG}$ (inconsistent).
- SPICE: NXP BF862.prm (Rev 1.0, 2014-12-30 per NXP page; header "MARCH 2007"); parameters in the models README. Model $C_{GS}$ 8.289 pF and $C_{GD}$ 7.400 pF zero-bias plus 1.05/0.201 pF package capacitors.
- Practical consequence: at the BF862's natural operating point ($I_D$ several mA) impact-ionisation gate current already dominates leakage above $V_{DG}\approx5$ V; keep $V_{DG}\lesssim3$ to 4 V (cascode) for a high-impedance input.

### 2.2 NXP BF861A/B/C (single, SOT-23)

File: `NXP/NXP_BF861A-B-C_data-sheet_Rev5_2011-09-15.pdf` (Product data sheet Rev. 5, 15 September 2011, 14 pp.)

- Status: "No Longer Manufactured (discontinued)", data sheet marked "Archived" on https://www.nxp.com/products/BF861A (read 2026-11-19).
- Table 7 ($T_j=25$ °C, $V_{DS}=8$ V, $V_{GS}=0$) (p.3-4): $V_{(BR)GSS}$ -25 V min; $V_{GSoff}$ ($I_D=1$ µA) A -0.2 to -1, B -0.5 to -1.5, C -0.8 to -2 V; forward $V_{GS}$ 1 V max; $I_{DSS}$ A 2-6.5, B 6-15, C 12-25 mA; $I_{GSS}$ -1 nA max ($V_{GS}=-20$ V); $|y_{fs}|$ A 12-20, B 16-25, C 20-30 mS; $g_{os}$ max A 200, B 250, C 300 µS; $C_{iss}$ 10 pF max; $C_{rss}$ 2.1 typ / 2.7 max pF (1 MHz); $V_n/\sqrt{B}$ 1.5 nV/$\sqrt{\mathrm{Hz}}$ typ at **1 MHz**.
- $R_{th(j-a)}$ 500 K/W on FR4 (Table 6, p.3).
- Fig.14, equivalent input noise vs f, $V_{DS}=8$ V, $V_{GS}=0$ (p.8, read by eye, log f 10 Hz to 1 MHz, linear y): 10 Hz 6.5; 100 Hz 4.0; 1 kHz 2.1; 10 kHz 1.3; 100 kHz 1.0; 1 MHz 1.0 nV/$\sqrt{\mathrm{Hz}}$. Corner about 8 kHz.
- Doubt: table 1.5 nV/$\sqrt{\mathrm{Hz}}$ at 1 MHz versus Fig.14 about 1.0 at 1 MHz.

### 2.3 Linear Integrated Systems LSBF862 (single, SOT-23) — current BF862 replacement

File: `Other/LIS_LSBF862_datasheet_RevA2_2026-02-17.pdf` (Doc 201195, 02/17/2026, Rev# A2, ECN# LSBF862, 2 pp.)

- "Improved replacement for NXP BF862" (p.1). SOT-23 3L and die; select option "SELXXXX" (special screening of $V_{GS}$, $I_{DSS}$) (p.2). Status: active (product page https://www.linearsystems.com/jfetamplifierssingles/lsbf862; announced December 2025).
- Absolute maximum (p.1, two tables that disagree): box: $T_{stg}$ -55 to +150 °C, $T_j$ -55 to +135 °C, $P_D$ 400 mW, $I_{G(F)}$ 10 mA, $V_{GSS}$ 40 V, $V_{GDS}$ 40 V; table: $V_{DS}$ ("Gate-Source or Gate-Drain Voltage") 40 V, $V_{DG}$ ("Drain-Source Voltage") 40 V, $I_{SG}$ 10 mA, $I_{DS}$ 40 mA, $P_{tot}$ 300 mW (derate 2 mW/°C above 25 °C), $T_{stg}$ -55 to +150 °C, $T_j$ "+300 °C".
- Electrical (p.2, 25 °C): $BV_{GSS}$ -40 V min ($V_{DS}=0$, $I_{GS}=-1$ µA); $V_{GS(OFF)}$ -0.3 to -1.2 V ($V_{DS}=8$ V, 1 µA); forward $V_{GS}$ 1 V max; $I_{DSS}$ 10.0 to 25.0 mA ($V_{DS}=8$ V); $I_{GSS}$ -1.0 nA max ($V_{GS}=-15$ V); $Y_{fs}$ 42.0 mS typ ($V_{DS}=10$ V, $V_{GS}=0$); $G_{os}$ 180 µS typ ($V_{DS}=15$ V, $I_D=1$ mA); $e_n$ 0.8 typ at 10 kHz and 1.4 typ / 4.0 max at 10 Hz ($V_{DS}=8$ V, $I_D=2$ mA, NBW 1 Hz); $C_{ISS}$ 11.5 pF typ, $C_{RSS}$ 3.5 pF typ ($V_{DS}=8$ V, $V_{GS}=0$, 1 MHz).
- No curves; gate current at operating point not given.
- Note 7 (p.2): "Voltage specifications are not tested 100 %, but guaranteed by lot sampling".
- Doubts: $T_j$ "+300 °C" and $P_{tot}$ 300 vs 400 mW are internal contradictions; symbol labels in the absolute-maximum table are swapped; page 2 footer reads "Page 1 of 2". $C_{rss}$ 3.5 pF vs BF862 1.9 pF typ: the LSBF862 is not a capacitance-identical drop-in. The vendor SPICE model (Rev 2) predicts much higher 10 Hz noise than the data sheet (models README).

### 2.4 InterFET IFN860

Not a BF862 clone: it is a dual (TO-71/SOIC-8) "similar to Crystalonics CD860" (section 1.5). No InterFET BF862 replacement was found on interfet.com.

---

## 3. Vishay/Siliconix legacy parts and second sources

Status: Vishay no longer serves these documents (https://www.vishay.com/docs/70247/70247.pdf, .../70249/..., .../70254/... return HTTP 404 on 2026-11-19; same on wwwlegacy.vishay.com). Linear Systems data sheets state "Replacement for SILICONIX & NATIONAL: 2N5564 Series". Treated as discontinued at Vishay; copies used are distributor mirrors of the Vishay originals.

### 3.1 Vishay 2N5564/2N5565/2N5566 (matched pair, two-chip, TO-71)

File: `Vishay/Vishay_2N5564-2N5565-2N5566_70254_RevE_mirror.pdf` (Doc. 70254, S-50150 Rev. E, 24-Jan-05, 6 pp.)

- "Two-Chip Design" in TO-71 (p.1). Product summary: $V_{GS(off)}$ -0.5 to -3 V; $V_{(BR)GSS}$ -40 V min; $g_{fs}$ 7.5 mS min; $I_G$ -3 pA typ; $|V_{GS1}-V_{GS2}|$ 5 / 10 / 20 mV max (p.1). Features: "Low Noise 12 nV/rtHz @ 10 Hz", "Good CMRR 76 dB".
- Absolute max (p.1): gate-drain/gate-source -40 V; gate-gate ±80 V; gate current 50 mA; $P_D$ 325 mW per side (derate 2.6 mW/°C), 650 mW total (5.2 mW/°C); $T_J$ -55 to 150 °C; storage -65 to 200 °C.
- Specifications (p.2, $T_A=25$ °C; typ = "design aid only"): $V_{(BR)GSS}$ -55 typ / -40 min; $V_{GS(off)}$ -2 typ, -0.5 to -3 V ($V_{DS}=15$ V, 1 nA); $I_{DSS}$ 20 typ, 5 to 30 mA ($V_{DS}=15$ V); $I_{GSS}$ -5 pA typ / -100 pA max ($V_{GS}=-20$ V), -10 nA typ / -200 nA max at 150 °C; $I_G$ -3 pA typ ($V_{DG}=15$ V, $I_D=2$ mA), -1 nA typ at 125 °C; $r_{DS(on)}$ 50 typ / 100 max ohm; $V_{GS}$ -1.2 V typ ($V_{DG}=15$ V, 2 mA); $V_{GS(F)}$ 0.7 typ / 1 max V.
- Dynamic (p.2, $V_{DS}=15$ V, $I_D=2$ mA): $g_{fs}$ 9 typ, 7.5 to 12.5 mS (1 kHz); $g_{os}$ 35 typ / 45 max µS; $g_{fs}$ 8.5 typ / 7 min mS at 100 MHz (not production tested); $C_{iss}$ 10 typ / 12 max pF; $C_{rss}$ 2.5 typ / 3 max pF (1 MHz); $e_n$ 12 typ / 50 max nV/$\sqrt{\mathrm{Hz}}$ at 10 Hz; NF 1 dB max ($R_G=10$ MΩ).
- Matching (p.2): $|V_{GS1}-V_{GS2}|$ 5 / 10 / 20 mV max ($V_{DG}=15$ V, 2 mA); drift 10 / 25 / 50 µV/°C max (-55 to 125 °C); $I_{DSS}$ ratio 0.98 typ, 0.95 min; $g_{fs}$ ratio 0.98 typ, 0.95 / 0.90 / 0.90 min; CMRR 76 dB typ ($V_{DG}=10$ to 20 V).
- Noise Voltage vs Frequency, $V_{DS}=15$ V (p.5, log-log, read by eye): $I_D=10$ mA: 10 Hz 8.7; 100 Hz 7.0; 1 kHz 3.1; 10 kHz 1.6; 100 kHz 1.2 nV/$\sqrt{\mathrm{Hz}}$. $I_D=1$ mA: 10 Hz 15; 100 Hz 10; 1 kHz 4.2; 10 kHz 2.1; 100 kHz 1.35. Corner ($\sqrt2$ criterion) about 5 kHz (10 mA) and 15 kHz (1 mA) - the excess noise is not a clean 1/f line.
- Capacitance vs $V_{GS}$, $V_{DS}=0$, 1 MHz (p.4, read by eye): $C_{iss}$ 22.5 pF at 0 V, 10 at -4 V, 7.5 at -8 V, 6.8 at -12 V, 6.0 at -20 V; $C_{rss}$ 9 pF at 0 V, 4.6 at -4 V, 3.2 at -8 V, 2.2 at -20 V.
- Gate Leakage Current vs $V_{DG}$ (p.4, log y, read by eye): 25 °C, $I_{G(on)}$ at $I_D=10$ mA: about 1.6 pA at 6 V, 2.5 pA at 12 V, 5 pA at 15 V, 15 pA at 18 V, 70 pA at 21 V, 0.5 nA at 23 V; at 1 mA: about 1.1 pA up to 15 V, 3 pA at 18 V, 25 pA at 21 V, 0.25 nA at 24 V; $I_{GSS}$ about 1 pA at 4 V to 4 pA at 30 V. 125 °C: about 0.2 to 1 nA over 2 to 30 V.
- Transconductance vs Drain Current, $V_{DS}=15$ V, $V_{GS(off)}=-2$ V (p.5, log-log, read by eye): 25 °C: about 1.5 mS at 0.1 mA, 6 mS at 1 mA, 14 mS at 10 mA. Transfer characteristic (p.4): $I_{DSS}\approx20$ mA at 25 °C for $V_{GS(off)}=-2$ V.
- RF: common-gate y-parameters 100 to 1000 MHz at $V_{DG}=15$ V, $I_D=10$ mA (p.4-5).

### 3.2 Linear Systems LS5564 series (2N5564 replacement; monolithic)

File: `Other/LIS_2N5564-series_datasheet_RevA4.pdf` (Doc 201187, 07/25/2019, Rev#A4, ECN# LS5564 Series, 2 pp.)

- Title "LS5564 SERIES, Monolithic Dual N-Channel JFET Amplifier"; "Replacement for SILICONIX & NATIONAL: 2N5564 Series"; TO-71 (p.1). Status: active (https://www.linearsystems.com/jfet-amplifiers-duals/2n5564-series).
- Max (p.1): storage and $T_J$ -55 to +150 °C; 500 mW total (derate 4 mW/°C); gate current 50 mA; gate-drain and gate-source -40 V.
- Matching (p.1): $|V_{GS1}-V_{GS2}|$ 5 / 10 / 20 mV max and drift 10 / 25 / 50 µV/°C max ($V_{DG}=15$ V, 2 mA); $I_{DSS}$ ratio 0.95-1; $g_{fs}$ ratio 0.95 / 0.90 / 0.90 to 1; CMRR 76 dB typ.
- Static (p.1): $BV_{GSS}$ -40 V min; $V_{GS(off)}$ -0.5 to -3.0 V; $V_{GS(F)}$ 0.7 typ / 1 max; $V_{GS}$ -1.2 typ; $I_{DSS}$ 7 to 40 mA ($V_{DS}=10$ V); $I_{GSS}$ -100 pA max ($V_{GS}=-20$ V); $I_G$ -3 pA typ ($V_{DG}=10$ V, $I_D=5$ mA); $R_{DS(on)}$ 50 typ / 100 max ohm; gate-to-gate isolation ±1 µA at ±80 V.
- Dynamic (p.2, $V_{DS}=15$ V, $I_D=2$ mA): $g_{fs}$ 9 typ, 7.5 to 20 mS (1 kHz); $g_{os}$ 55 typ / 100 max µS (1 kHz), 120 µS typ (100 MHz); $C_{iss}$ **25 pF typ**; $C_{rss}$ **5.5 pF typ** (1 MHz); NF 1 dB typ (10 Hz, $R_G=10$ MΩ); $e_n$ 12 typ / 50 max nV/$\sqrt{\mathrm{Hz}}$ at 10 Hz.
- Contradiction with Vishay 2N5564: monolithic vs two-chip; $C_{iss}$ 25 vs 10 pF typ (12 max); $C_{rss}$ 5.5 vs 2.5 pF typ; $I_{DSS}$ max 40 vs 30 mA; $g_{fs}$ max 20 vs 12.5 mS. The LS5564 is not capacitance-equivalent to the Vishay part.

### 3.3 Vishay U401/U404/U406 (monolithic dual) and SST404/SST406

File: `Vishay/Vishay_SST-U401-series_70247_RevF_mirror-farnell.pdf` (Doc. 70247, S-04031 Rev. F, 04-Jun-01, 6 pp.)

- Product summary (p.1): $V_{GS(off)}$ -0.5 to -2.5 V; $V_{(BR)GSS}$ -40 V min; $g_{fs}$ 1 mS min; $I_G$ -2 pA typ; $|V_{GS1}-V_{GS2}|$ max 5 (U401), 15 (SST/U404), 40 mV (SST/U406). Features: low gate leakage 2 pA, high CMRR 102 dB. TO-71 (U) and SO-8 (SST).
- Absolute max (p.1): gate-drain/gate-source -40 V; gate current 10 mA; $T_J$ -55 to 150 °C; storage -65 to 200 °C (U), -55 to 150 °C (SST); 300 mW per side (2.4 mW/°C), 500 mW total (4 mW/°C).
- Static (p.2): $V_{(BR)GSS}$ -58 typ / -40 min; $V_{(BR)G1-G2}$ ±45 typ / ±30 min; $V_{GS(off)}$ -1.5 typ ($V_{DS}=15$ V, 1 nA); $I_{DSS}$ 3.5 typ, 0.5 to 10 mA ($V_{DS}=10$ V); $I_{GSS}$ -2 pA typ / -25 pA max ($V_{GS}=-30$ V), -1 nA typ at 125 °C; $I_G$ -2 pA typ / -15 pA max ($V_{DG}=15$ V, $I_D=200$ µA), -0.8 nA typ / -10 nA max at 125 °C; $r_{DS(on)}$ 250 ohm typ; $V_{GS}$ -1 typ / -2.3 max V (15 V, 200 µA).
- Dynamic (p.2): $g_{fs}$ 1.5 typ, 1 to 2 mS and $g_{os}$ 1.3 typ / 2 max µS ($V_{DS}=15$ V, $I_D=200$ µA, 1 kHz); $g_{fs}$ 4 typ, 2 to 7 mS and $g_{os}$ 5 typ / 30 max µS ($V_{DS}=10$ V, $V_{GS}=0$); $C_{iss}$ 4 typ / 8 max pF; $C_{rss}$ 1.5 typ / 3 max pF ($V_{DS}=15$ V, 200 µA, 1 MHz); $e_n$ 10 typ / 20 max nV/$\sqrt{\mathrm{Hz}}$ at 10 Hz (15 V, 200 µA).
- Matching (p.2): drift 10 / 25 / 80 µV/°C max (U401/U404/U406; $V_{DG}=10$ V, 200 µA, -55 to 125 °C), SST404 20 and SST406 40 µV/°C typ; CMRR 102 typ, 95 dB min ($V_{DG}=10$ to 20 V).
- Equivalent input noise vs f, $V_{DG}=15$ V (p.5, linear y, read by eye; checked against [D]): $I_D=200$ µA: 10 Hz 14; 100 Hz 7.3 to 8.5; 1 kHz 4.2 to 4.5; 10 kHz 2.9 to 3.0; 100 kHz 2.4 to 2.5. $V_{GS}=0$ ($I_D=I_{DSS}$, value not stated): 10 Hz 10; 100 Hz 5.2 to 5.8; 1 kHz 2.9 to 3.2; 10 kHz 2.0 to 2.1; 100 kHz 1.75 to 1.8. Corner about 2.5 to 3 kHz.
- $C_{iss}$ vs $V_{GS}$, 1 MHz (p.5, read by eye): $V_{DS}=0$: 10 pF (0 V), 4.0 (-4 V), 2.45 (-20 V); $V_{DS}=5$ V: 6.4, 3.0, 2.2; $V_{DS}=15$ V: 5.0, 2.5, 1.9 pF. $C_{rss}$: $V_{DS}=0$: 5.5, 2.4, 1.9; 5 V: 2.45, 1.75, 1.65; 15 V: 1.75, 1.35, 1.1 pF.
- Gate leakage vs $V_{DG}$ (p.3) [D]: 25 °C $I_{GSS}$ 0.44 pA at 5 V, 0.64 pA at 10 V, 0.74 at 15 V; at $I_D=500$ µA (curve labelled "500 mA", evidently µA) $I_G$ follows $I_{GSS}$ to about 10 V, then 5.9 pA at 15 V, 72 pA at 20 V, 0.53 nA at 25 V.
- $g_{fs}$ vs $I_D$, $V_{GS(off)}=-1.5$ V (p.5) [D]: 25 °C about 1.0 mS at 0.1 mA, 1.4 at 0.2 mA, 2.2 at 0.5 mA, 3.1 mS at 0.95 mA.
- Doubt: table $e_n$ typ 10 at 10 Hz for 200 µA but the 200 µA curve gives about 14; 10 belongs to the $V_{GS}=0$ curve.

### 3.4 Vishay U430/U431 (matched pair, two-chip, TO-78)

File: `Vishay/Vishay_U430-U431_70249_RevE_mirror-digikey.pdf` (Doc. 70249, S-04031 Rev. E, 04-Jun-01; legal page revision 18-Jul-08; 7 pp.)

- Product summary (p.1): $V_{GS(off)}$ U430 -1 to -4 V, U431 -2 to -6 V; $V_{(BR)GSS}$ -25 V min; $g_{fs}$ 10 mS min; $I_G$ -15 pA typ; $|V_{GS1}-V_{GS2}|$ 25 mV **typ** (no max). "Good power gain even at frequencies beyond 250 MHz"; CMRR 75 dB.
- Absolute max (p.1): gate-drain/gate-source -25 V; gate current 10 mA; storage -65 to 200 °C; $T_J$ -55 to 150 °C; 300 mW per side (2.4 mW/°C), 500 mW total (4 mW/°C).
- Static (p.2): $V_{(BR)GSS}$ -35 typ / -25 min; $V_{GS(off)}$ as above ($V_{DS}=10$ V, 1 nA); $I_{DSS}$ U430 12 to 30, U431 24 to 60 mA; $I_{GSS}$ -5 pA typ / -150 pA max ($V_{GS}=-15$ V), -10 nA typ / -150 nA max at 150 °C; $I_G$ -15 pA typ ($V_{DG}=10$ V, $I_D=5$ mA), -10 nA typ at 150 °C; $V_{GS(F)}$ 0.8 typ / 1 max V.
- Dynamic (p.2): $g_{fs}$ 15 typ / 10 min mS and $g_{os}$ 100 typ / 250 max µS ($V_{DS}=10$ V, $I_D=10$ mA, 1 kHz); $C_{iss}$ 4.5 typ / 5 max pF and $C_{rss}$ 2 typ / 2.5 max pF ($V_{GS}=-10$ V, $V_{DS}=0$, 1 MHz); $e_n$ 6 nV/$\sqrt{\mathrm{Hz}}$ typ ($V_{DS}=10$ V, $I_D=10$ mA, 100 Hz). 100 MHz: $g_{fs}$ 14 mS, $g_{os}$ 0.13 mS, $g_{ig}$ 12 mS typ.
- Matching (p.2): $|V_{GS1}-V_{GS2}|$ 25 mV typ ($V_{DG}=10$ V, 10 mA); $I_{DSS}$ ratio 0.95 typ / 0.9 min; $g_{fs}$ ratio 0.95 / 0.9; $V_{GS(off)}$ ratio 0.95 / 0.9; $|I_{G1}-I_{G2}|$ -2 pA typ; CMRR 75 dB typ ($V_{DG}=5$ to 10 V, 10 mA).
- Equivalent input noise vs f, $V_{DS}=10$ V (p.6, linear y, read by eye): $I_D=10$ mA: 10 Hz 12; 100 Hz 5.6; 1 kHz 3.3; 10 kHz 2.0; 100 kHz 1.1 (still falling); $I_D=1$ mA: 16; 7.5; 4.7; 3.4; 2.8 nV/$\sqrt{\mathrm{Hz}}$. Corner about 20 kHz (10 mA) and 3 kHz (1 mA).
- $C_{iss}$ vs $V_{GS}$, 1 MHz (p.5, read by eye): $V_{DS}=0$: 11.5 pF (0 V), 6.3 (-4 V), 5.2 (-8 V), 3.6 (-20 V); $V_{DS}=5$ V: 8.0, 5.1, 4.6, 3.2 pF. $C_{rss}$: $V_{DS}=0$: 6.6, 3.1, 1.9 (-20 V); 5 V: 3.6, 2.2, 1.6 pF.
- InterFET's N0072L geometry document lists U430/U431 as standard parts on that geometry [D]; InterFET xlsx has U430/U431 models (no noise parameters).

### 3.5 Other Vishay files downloaded, not read

- `Vishay/Vishay_J-SST-U308-series_70237_RevH_mirror-farnell.pdf` (J308-J310, SST308-310, U309/U310; Doc. 70237 Rev. H 24-Jan-05).
- `Vishay/Vishay_2N4416-2N4416A-SST4416_70242_RevH_mirror-farnell.pdf` (Doc. 70242 Rev. H).
- `Vishay/Vishay_2N-PN-SST4391-series_70241_RevF_mirror-xdevs.pdf` (Doc. 70241 Rev. F).
- Siliconix application notes AN101 (10-Mar-97), AN104 (01-Jan-94, SPICE for JFETs, one page only), AN106 "Low-Noise JFETs - Superior Performance to Bipolars" (10-Mar-97), hosted by InterFET: downloaded, not read.

### 3.6 Calogic (Fremont CA) — second source, active

Calogic data sheets (2 pp. each, Rev A, Corel Ventura originals 1997-1998, PDF modified 2004) were downloaded but not read. The following is Calogic's web selection table (https://calogic.net/products/jfet-amplifiers/, read 2026-11-19), not the data sheets:

| Part | Package | BV min | IGSS max | IDSS | VGS(off) | Comment on web page |
|---|---|---|---|---|---|---|
| U401-U406 (dual) | TO-71 | -50 V | -25 pA | 0.5-10 mA | -0.5 to -2.5 V | — |
| SST404/405/406 (dual) | SO-8 | -50 V | -25 pA | 0.5-10 mA | -0.5 to -2.5 V | "Very Low Noise" |
| U440/U441 (dual) | TO-71 | -50 V | -500 pA | 6-30 mA | -1 to -6 V | "High Gain, Low Leakage" |
| U443/U444 (dual) | TO-78 | -25 V | -500 pA | 6-30 mA | -1 to -6 V | "High Gain, Low Leakage" |
| 2N5911/2N5912 (dual) | TO-78 | -25 V | -100 pA | 7-40 mA | -1 to -5 V | "Good Matching" |
| U308/U309/U310 | TO-52 | -25 V | -150 pA | 12-60 / 12-30 / 24-60 mA | -1 to -6 / -1 to -4 / -2.5 to -6 V | "High Power Gain, Low Noise" |
| J308-J310, SST308-310 | TO-92, SOT-23 | -25 V | -1000 pA | as U308-U310 | -1 to -6.5 V | "High Power Gain, Low Noise" |
| 2N4416/2N4416A, SST4416 | TO-72, SOT-23 | -30/-35 V | -100 pA | 5-15 mA | to -6 V | "Low Noise" |

- Calogic does not list 2N5564, U430 or U431. Web BV -50 V for U401 differs from Vishay's -40 V min.

### 3.7 Micross

- No JFET data sheets are hosted on micross.com (site search for 2N5564 returned no product, 2026-11-19). Micross-branded JFET sheets found on aggregator sites (LSU401, LSK389, J310, 2N5564) are rebadged Linear Systems documents; not downloaded. Treat Linear Systems as the current source.

### 3.8 Central Semiconductor

- Product brief `Central/Central_JFET_product-brief_PB-JFET_R0-0520.pdf` (PB JFET R0 0520) lists 2N3819, 2N5486, PN4091-4093, PN4391-4393, 2N4416/2N4416A, CMPF4391-4393, CMPF4416A, CMPF5484-5486, CMPFJ175/176, 2N3971/2N3972, 2N4091-4093, 2N4391-4393, 2N4856-2N4861(A). No 2N5564-type, U401-type or U430-type dual and no dedicated ultra-low-noise part.
- `Central/Central_2N4416-2N4416A_datasheet.pdf` downloaded, not read.

---

## 4. Other current makers

Searches (2026-11-19) for "ultra low noise JFET" 2023-2026, "lowest noise JFET", replacements for 2SK170/2SK369/LSK389, BF862 equivalents and Chinese 2SK208/LSK389 clones found:

- Linear Integrated Systems: LSBF862 (December 2025, section 2.3), LS5564 (section 3.2), U401 series (`Other/LIS_U401-series_datasheet_RevA9.pdf`, Rev A9, downloaded, not read); LSK-series parts are in the companion survey. The full 2026 Linear Systems data book (347 pp.) is in `Other/`.
- TI JFE150/JFE2140/JFE2325: companion survey.
- InterFET: section 1.
- No data sheet was found for a Chinese or Taiwanese low-noise audio-class JFET (2SK170/2SK208/LSK389/BF862 class). Unisonic (UTC) data sheets exist only for general-purpose/HF JFETs (2SK303, 2SK508; not opened). No Nexperia, Microchip, Diodes Inc. or Semtech low-noise JFET was found. No part is listed here without a data sheet.

## 5. Application data read

### 5.1 Brookhaven 200 pV/$\sqrt{\mathrm{Hz}}$ amplifier (six paralleled NJ3600 = InterFET N3600 geometry)

File: `InterFET/InterFET-hosted_Rescia_BNL_200pV-amplifier_slide21.pdf` (slide 21 of S. Rescia, "Detecting Signals into the Noise", Pavia, 5 Dec. 2016; reproduces Fig. 2 and Fig. 4 of an earlier report).

- Front end: "x6 NJ3600" JFETs in parallel, followed by a bipolar and JFET loop (Fig. 2, schematic).
- Fig. 4, $S_e^{1/2}$ vs f, 0.1 Hz to 100 kHz, log-log (read by eye, coarse): curve b) six JFETs at total standing current 2.5 mA: about 1 nV/$\sqrt{\mathrm{Hz}}$ at 10 Hz, 0.5 at 100 Hz, 0.25 to 0.3 at 1 kHz, about 0.2 nV/$\sqrt{\mathrm{Hz}}$ from roughly 3 to 100 kHz (red line labelled "200 pV/rtHz"). Curve c) same six JFETs at 28.7 mA total: about 10 nV/$\sqrt{\mathrm{Hz}}$ at 1 Hz, 3 at 10 Hz, about 0.8 at 100 Hz, merging with b) above roughly 1 to 3 kHz. Curve a) calculated contribution of the rest of the front end, annotation "$g_mR = 305$".
- Design-relevant: with this geometry the white floor of 0.2 nV/$\sqrt{\mathrm{Hz}}$ was reached at only about 0.42 mA per device, and raising the current tenfold increased the low-frequency excess noise.

### 5.2 Not read

InterFET AN-015, AN-017, AN-105, the full 31-slide BNL deck, Siliconix AN101/AN104/AN106 and TI AN-104 (SNVA515C) were downloaded but not read for numbers.

---

## 6. Summary table

$e_n$ in nV/$\sqrt{\mathrm{Hz}}$; capacitances in pF; "c" = read by eye from a curve; conditions abbreviated. Status as of 2026-11-19.

| part | vendor | status | type | $e_n$ @1 kHz ($I_D$) | $e_n$ @10 Hz | $g_{fs}$ ($I_D$) | $C_{iss}$ | $C_{rss}$ | $I_{DSS}$ range | $V_{GS(off)}$ range | $I_G$ | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| IF3601 | InterFET | listed (Mouser) | N single, TO-39 | 0.34 c (5 mA, 3 V); 0.35 typ @100 Hz | 0.60 c (5 mA) | 175 mS typ (IDSS) | 650 typ (VDS 0, VGS -4); 890 c (VGS 0, VDS 5) | 80 typ; 84 c (VGS 0) | 30 min, 300 typ mA | -0.35 to -2.0 V | IGSS ≤0.1 nA @-10 V; no IG(on) | BV -20 V; table/curve Ciss conflict; web Ciss 300 pF conflicts |
| IF3602 | InterFET | listed (Mouser) | N dual, TO-78 | as IF3601 | as IF3601 | 175 typ | 650 typ | 80 typ | 30 min, 300 typ | -0.35 to -3.0 V | IGSS ≤0.5 nA | match ≤100 mV @500 pA only |
| IF9030 | InterFET | listed | N single | 0.7 typ (5 mA, 4 V) | not given | 80 min/150 typ (IDSS) | ≤60 (5 mA) | ≤20 | 30-300 mA | -0.35 to -2.0 V | IGSS ≤0.1 nA | IF9034/35 = dual |
| IF4500 | InterFET | listed (Mouser) | N single, TO-18/SOT-23 | 0.85 typ; 0.88 c (5 mA, 4 V) | 1.10 c (5 mA) | 70 typ (5 mA, doubtful) | ≤35 table; 52-58 c (VGS 0) | ≤15; 25 c | ≥5, 30 typ | -0.35 to -1.5 V | IGSS 1.3 pA c @10 V | lowest 1/f corner (~10 Hz) |
| IFN860 | InterFET | listed | N **dual** TO-71/SOIC-8 | ≤2.0 (10 mA, VDG 3 V); 0.9 typ p.1 | not given | 25 min/40 typ (10 mA) | 30 typ/35 max (10 mA) | 17/20 | ≥10 mA | -0.3 to -3 V | IGSS ≤3 nA | ≈CD860, not BF862; match ≤25 mV |
| IFN146 | InterFET | listed (Mouser) | N dual, 2SK146 repl. | 1.1 typ p.1 (no cond.) | not given | 20 min/30 typ | ≤75 (VGS 0, VDS 10) | ≤15 | ≤30 mA | -0.3 to -1.2 V | IGSS ≤1 nA @-30 V; "<50 pA typ" | NF 1 dB @100 Ω; match ≤20 mV |
| IFN147 | InterFET | listed | N single, 2SK147 repl. | 1.1 typ p.1 | not given | 20/30 | ≤75 | ≤15 | 5-30 mA | -0.3 to -1.2 V | IGSS ≤1 nA | table mislabelled IFN113 |
| IF170A-D | InterFET | listed | N single, 2SK170-type | 1.0 typ (2 mA, 10 V); 1.0 c (5 mA) | 1.70 c (5 mA) | ≥14 (IDSS); ≥6 (1 mA) | ≤20 (2 mA); 16.5 c (VGS 0, 10 V) | ≤4.5; 7.2 c | A 2.6-6.5 … D 18-30 | -0.2 to -2.0 V | 0.62 pA c @10 V | BV -30 V |
| IF389A-D | InterFET | listed (Direct) | N dual, LSK389-type | 1.0 typ (2 mA) / 1.0 c (5 mA) | 2.05 c (5 mA) | ≥14 (IDSS); ≥6 (1 mA) | ≤20; 19.5 c (VGS 0) | ≤4.5; 3.7 c | as IF170 | -0.2 to -2.0 V | IGSS ≤0.1 nA | match ≤30 mV @1 mA |
| IF150A/B/C | InterFET | listed (Direct) | N single, low-C | 3.4 c (0.5 mA, 4 V) | 3 typ (IDSS); 5.5 c (0.5 mA) | ≥1/3/5 (IDSS); 7 typ | ≤3; 2.9 c | ≤1.2 | 0.5-3.5 / 3-10 / 8-22 | -0.8..-2 / -1.8..-3.2 / -3..-6 | 100 fA typ @5 V; ≤5 pA | BV only -10 V |
| IFN5564-66 | InterFET | listed (Mouser) | N dual | 2.0 typ geom. (5 mA) | ≤50 (2 mA); 3.6 c geom. | 7-12.5 (2 mA) | ≤12; 6.5 typ p.1 | ≤3 | 5-30 mA | -0.5 to -3 V | IGSS ≤100 pA | drift unit error |
| BF862 | NXP | no longer manufactured | N single, SOT-23 | not given (0.8 typ @100 kHz, IDSS) | not given | 35 min/45 typ (IDSS); 37 c @10 mA | 10 typ (VGS 0); 4.5-5 c (VGS -1…-2) | 1.9 typ | 10-25 mA | -0.3 to -1.2 V | IGSS ≤1 nA; IG(on) ≫ IGSS above VDG≈5 V | fT 715 MHz typ |
| BF861A/B/C | NXP | discontinued (archived) | N single, SOT-23 | 2.1 c (IDSS) | 6.5 c | 12-30 by grade | ≤10 | 2.1 typ | 2-25 by grade | -0.2 to -2 V | IGSS ≤1 nA | 1/f corner ~8 kHz |
| LSBF862 | Linear Systems | active (2025-12) | N single, SOT-23 | not given (0.8 typ @10 kHz, 2 mA) | 1.4 typ / 4.0 max (2 mA) | 42 typ (IDSS) | 11.5 typ | 3.5 typ | 10-25 mA | -0.3 to -1.2 V | IGSS ≤1 nA | BV -40 V; internal Tj/Ptot conflicts |
| 2N5564/5/6 | Vishay | discontinued | N dual, 2-chip TO-71 | ~3.9 c @2 mA (4.2 c @1 mA, 3.1 c @10 mA) | 12 typ/50 max (2 mA); 8.7-15 c | 7.5-12.5 (2 mA) | 10 typ/12 max (2 mA, 15 V) | 2.5/3 | 5-30 mA | -0.5 to -3 V | 3 pA typ (15 V, 2 mA); 5 pA c @15 V, 10 mA | corner ~5-15 kHz |
| LS5564 series | Linear Systems | active | N dual, monolithic TO-71 | not given | 12 typ/50 max (2 mA) | 7.5-20 (2 mA) | **25 typ** | 5.5 typ | 7-40 mA | -0.5 to -3 V | 3 pA typ (10 V, 5 mA) | not C-equivalent to Vishay part |
| U401/U404/U406 | Vishay | discontinued | N dual, monolithic | 4.2-4.5 c (200 µA); 2.9-3.2 c (IDSS) | 10 typ/20 max (200 µA); 14 c | 1-2 (200 µA); 2-7 (IDSS) | 4 typ/8 max (200 µA) | 1.5/3 | 0.5-10 mA | -0.5 to -2.5 V | 2 pA typ, ≤15 pA (15 V, 200 µA) | drift ≤10 µV/°C (U401); CMRR 102 dB |
| U430/U431 | Vishay | discontinued | N dual, 2-chip TO-78 | 3.3 c (10 mA); 4.7 c (1 mA) | 12 c (10 mA); 16 c (1 mA) | 10 min/15 typ (10 mA) | 4.5 typ/5 max (VGS -10, VDS 0); 11.5 c (VGS 0) | 2/2.5 | 12-30 / 24-60 mA | -1..-4 / -2..-6 V | 15 pA typ (10 V, 5 mA) | 6 typ @100 Hz; BV -25 V |

Derived figures of merit (from the table values above; mixed conditions where noted; not vendor data):

| part | $e_n\sqrt{C_{iss}}$ (nV/$\sqrt{\mathrm{Hz}}\cdot\sqrt{\mathrm{pF}}$) @1 kHz | basis | $f_T=g_{fs}/(2\pi C_{iss})$ | 1/f corner ($\sqrt2$ criterion) |
|---|---|---|---|---|
| IF3601/IF3602 | 8.7 (650 pF) to 10.1 (890 pF) | 0.34 c @5 mA | 43 MHz (175 mS, 650 pF; mixed) | ~30 Hz @5 mA |
| IF9030 | 5.4 | 0.7 typ, 60 pF max | ~400 MHz (150 mS @IDSS vs 60 pF @5 mA; optimistic) | not given |
| IF4500 | 5.0 (35 pF) to 6.3 (55 pF) | 0.85 typ | 320 MHz (70 mS, 35 pF; doubtful) | ~10 Hz @5 mA |
| IFN860 | 4.9 (typ 0.9, 30 pF) / 11.8 (max 2.0, 35 pF) | p.1 typ / table max | 210 MHz (40 mS, 30 pF @10 mA) | not given |
| IFN146 | 9.5 | 1.1 typ, 75 pF max | 64 MHz (30 mS, 75 pF) | not given |
| IF170 / IF389 | 4.5 | 1.0 typ, 20 pF max | 111 MHz (14 mS min, 20 pF max) | ~60 Hz / ~120 Hz @5 mA |
| IF150 | 5.8 | 3.4 c @0.5 mA, 2.9 pF | 370 MHz (7 mS typ, 3 pF) | ~120 Hz @0.5 mA |
| IFN5564 | 5.1 (6.5 pF typ) to 6.9 (12 pF max) | 2.0 geom. | 93 MHz (7 mS min, 12 pF) | ~150 Hz @5 mA |
| BF862 | 2.5 (white, @100 kHz) | 0.8 typ, 10 pF | 716 MHz (45 mS, 10 pF; vendor 715) | not given |
| LSBF862 | 2.7 (white, @10 kHz) | 0.8 typ, 11.5 pF | 580 MHz (42 mS, 11.5 pF) | ~20 Hz if $e_n^2$ = white + 1/f (from 1.4 @10 Hz) |
| 2N5564 (Vishay) | 12 @1 kHz; 3.8 @100 kHz | 3.9 c / 1.2 c, 10 pF | 143 MHz (9 mS, 10 pF @2 mA) | ~5 kHz @10 mA |
| LS5564 (LIS) | not given @1 kHz; 60 @10 Hz | 12 typ, 25 pF | 57 MHz (9 mS, 25 pF @2 mA) | not given |
| U401 | 8.4-9.0 (200 µA) | 4.2-4.5 c, 4 pF | 60 MHz (1.5 mS, 4 pF @200 µA) | ~3 kHz |
| U430 | 7.0 (4.5 pF) to 11 (11.5 pF) | 3.3 c @10 mA | 530 MHz (15 mS, 4.5 pF; Ciss at VGS -10 V understates) | ~20 kHz @10 mA |

## 7. Contradictions and doubts collected

1. IFN860 is a dual "similar to Crystalonics CD860" (IFN860 data sheet p.1), not a BF862 replacement as assumed in the brief.
2. IF3601/IF3602: $C_{iss}$ 650 pF typ in the table vs 290 pF on the curve at $V_{GS}=-4$ V; web table "Ciss max 300 pF". p.1 "Typical BVGSS -30 V" vs rating -20 V (IF3602).
3. IF4500: curve $C_{iss}$ (52 to 58 pF at $V_{GS}=0$) exceeds the table maximum 35 pF; $g_{fs}$ 70 mS at 5 mA implausible; p.1 says 65 mS.
4. IFN146: NF 1 dB at $R_G=100$ ohm implies about 0.65 nV/$\sqrt{\mathrm{Hz}}$, inconsistent with the 1.1 nV/$\sqrt{\mathrm{Hz}}$ feature value. IFN147 static table headed "IFN113".
5. IF170 vs IF389 (same N0132L geometry, identical tables): 10 Hz noise 1.70 vs 2.05 nV/$\sqrt{\mathrm{Hz}}$ on their typical curves. IF170 document number printed as "SP"; IFN152 document number blank; N0450L and N0450H share IF35518.R00.
6. IFN5564: drift printed in mV/°C (values are total mV over the span); only guaranteed noise is ≤50 nV/$\sqrt{\mathrm{Hz}}$ at 10 Hz.
7. Vishay 2N5564 (two-chip, $C_{iss}$ 10 typ/12 max) vs Linear Systems LS5564 "2N5564 series" (monolithic, $C_{iss}$ 25 typ, $C_{rss}$ 5.5 typ, $I_{DSS}$ to 40 mA).
8. Vishay U401: table $e_n$ 10 typ at 10 Hz for 200 µA vs 14 on the 200 µA curve; gate-leakage curve labels "500 mA"/"50 mA" must be µA.
9. BF861: table 1.5 nV/$\sqrt{\mathrm{Hz}}$ at 1 MHz vs Fig.14 about 1.0.
10. LSBF862: $T_j$ +135 °C vs "+300 °C"; $P_{tot}$ 400 vs 300 mW; vendor SPICE KF predicts about 9 nV/$\sqrt{\mathrm{Hz}}$ at 10 Hz vs 1.4 typ / 4.0 max in the data sheet; KF is numerically identical to NXP's BF862 model.
11. BF862 Fig.9 caption "$V_{DS}=8$ V" while the abscissa is $V_{DG}$.
12. U310 (InterFET): $e_n$ "10 nV/$\sqrt{\mathrm{Hz}}$ typ at 100 kHz" vs p.1 "2 nV/$\sqrt{\mathrm{Hz}}$ typ" and geometry curve 1.7 at 100 kHz.
