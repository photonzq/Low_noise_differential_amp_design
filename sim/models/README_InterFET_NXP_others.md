# SPICE models: InterFET, NXP BF862, Linear Systems LSBF862 and 2N5564

All files downloaded 2026-11-19 and stored unmodified. Folder names are `<vendor>/<part or collection>/`. Other vendors' folders in this directory (TI, `_lib`) belong to a separate survey.

## Files

| local path (relative to `sim/models/`) | URL | header / revision | format |
|---|---|---|---|
| InterFET/CTC-023_all-geometries/jfet-spice-modeling-ctc-023-interfet.pdf | https://interfet.com/wp-content/uploads/jfet-spice-modeling-ctc-023-interfet.pdf | InterFET CTC-023 "SPICE models summarized by geometry", R00, PDF dated 2023-09-26, 25 pp. | PDF listing of .MODEL lines (with and without GMIN-compensated IS) |
| InterFET/spice-models-xlsx_all-parts/interfet-spice-models.xlsx | https://interfet.com/wp-content/uploads/interfet-spice-models.xlsx | sortable list, 283 rows: model name, geometry, part, Vgs(off) typ, Idss typ/min/max, model without GMIN, model with GMIN, suggested GMIN | Excel; models are SPICE2 `njf` .MODEL lines |
| LinearSystems/LSBF862/LSBF862_SPICE_Model_Rev2_2026-02-09.pdf | https://www.linearsystems.com/_files/ugd/4be30b_5d971df8fa7d4a8bb18a221098ddaf01.pdf (linked as "LSBF862 SPICE Model.pdf" from https://www.linearsystems.com/jfetamplifierssingles/lsbf862) | "Updated LSBF862 SPICE Model, Rev 2 as of 02/09/2026"; ".MODEL LSBF862_UPDATED NJF(" | model text inside a 1-page PDF |
| LinearSystems/2N5564/Copy_2N5564_NJF.txt.pdf | https://www.linearsystems.com/_files/ugd/7e8069_b396c3875b1f4d27a087d73d115bbafe.pdf (linked from https://www.linearsystems.com/jfet-amplifiers-duals/2n5564-series) | ".model 2N5564 NJF(...)", no date | model text inside a 1-page PDF |

Not saved (download blocked):

- NXP BF862: https://www.nxp.com/downloads/en/spice-model/BF862.prm (NXP page: "BF862 SPICE model, Rev 1.0, Dec 30, 2014"; file header "BF862 SPICE MODEL", "MARCH 2007", "NXP SEMICONDUCTORS", SOT23). Scripted requests receive HTTP 404 "Page not available". The text was viewed through a web fetch and the parameters are transcribed below for reference, but no raw file is stored; download it manually for simulation.
- NXP BF862 S-parameters: https://www.nxp.com/downloads/en/s-parameters/Spar_BF862.zip (Rev 1.0, 2019-04-23), not downloaded.
- No SPICE model was found for Vishay U401, U430/U431 or 2N5564 originals; Calogic and Central models were not searched.

## Model parameters

### NXP BF862 (from BF862.prm as viewed; not stored)

Subcircuit pins: 1 drain, 2 gate, 3 source. Package elements: Ld 1.1 nH, Ls 1.25 nH, Lg 0.78 nH, Rg 0.535 ohm, Cds 0.0001 pF, Cgs 1.05 pF, Cgd 0.201 pF, Co (drain-source, package side) 0.35092 pF; intrinsic device `JBF862`.

`.MODEL JBF862 NJF`: BETA = 47.8E-3; BETATCE = -0.5; RD = 0.8; RS = 7.5; LAMBDA = 37.3E-3; VTO = -0.57093; VTOTC = -2.0E-3; IS = 424.6E-12; ISR = 2.995p; N = 1; NR = 2; XTI = 3; ALPHA = -1.0E-3; VK = 59.97; CGD = 7.4002E-12; M = 0.6015; PB = 0.5; FC = 0.5; CGS = 8.289E-12; **KF = 87.5E-18; AF = 1**.

Implied: $I_{DSS} = \beta V_{TO}^2 = 15.6$ mA; $g_{m0} = 2\beta|V_{TO}| = 54.6$ mS (data sheet: $I_{DSS}$ 10-25 mA, $|y_{fs}|$ 45 mS typ). ALPHA is negative (unusual; impact-ionisation term disabled or sign-inverted depending on simulator).

### Linear Systems LSBF862 (Rev 2, 02/09/2026)

Comment lines: "LSBF862 Advanced N-Channel JFET Model", "Extracted VTO = -0.79V | Adjusted BETA for gfs = 42mS".

`.MODEL LSBF862_UPDATED NJF`: VTO = -0.79; BETA = 2.658E-2; VTOTC = -2.5m; BETATCE = -0.5; LAMBDA = 0.03; RD = 7.5; RS = 7.5; IS = 1E-14; ISR = 1E-13; N = 1; NR = 2; XTI = 3; ZXTI = 1; ALPHA = 1E-4; VK = 180; CGS = 8P; CGD = 3.5P; PB = 0.5; M = 0.33; MJ = 0.33; FC = 0.5; **KF = 8.75E-17; AF = 1**; GDSNOI = 2; NLEV = 3; MFG = Linear_Systems.

- ZXTI, MJ, GDSNOI and NLEV are not standard SPICE2/SPICE3 JFET parameters; some simulators will reject or ignore them.
- Implied: $I_{DSS} = 16.6$ mA, $g_{m0} = 42.0$ mS (matches data sheet 42 mS typ).

### Linear Systems 2N5564 (LS5564 series)

`.model 2N5564 NJF`: Beta = 9.109m; Betatce = -500m; Rd = 1; Rs = 1; Lambda = 7.5m; Vto = -1.447; Vtotc = -2.5m; Is = 94.42f; Isr = 921.9f; N = 1; Nr = 2; Xti = 3; Alpha = 88.38u; Vk = 171.6; Cgd = 8.67p; M = 474.2m; Pb = 1; Fc = 0.5; Cgs = 9.76p; **Kf = 6.786e-002f (= 6.786E-17); Af = 1**; Mfg = Linear_Systems.

- Implied: $I_{DSS} = 19.1$ mA; $g_m$ at 2 mA $= 2\sqrt{\beta I_D} = 8.5$ mS (data sheet 9 mS typ at 2 mA).

### InterFET (CTC-023 / xlsx)

- Format: `.MODEL <name> njf VTO BETA LAMBDA CGD CGS PB IS MFG=InterFET`; a second column gives the same model with IS reduced to emulate leakage without GMIN, plus a suggested GMIN. Several grades are modelled per part (-L/-M/-H = low/mid/high $I_{DSS}$ bins).
- **No KF, AF, RD, RS, FC or M in any InterFET model** (checked over all 283 rows): SPICE noise from these models is channel thermal noise only; 1/f noise must be added separately, e.g. fitted to the data-sheet noise curves.
- CGS = CGD per geometry (zero-bias), not per part.

| model | geometry | VTO | BETA | LAMBDA | CGS = CGD | PB | IS (no GMIN / GMIN) | suggested GMIN |
|---|---|---|---|---|---|---|---|---|
| IF3601-M | N3600SL | -526m | 479m | 3.20m | 216p | 3.77 | 1.00f / 2.44p | 1.32p |
| IF3601-H | N3600SL | -1.15 | 186m | 39.3m | 216p | 3.77 | 1.00f | — |
| IF3602 | N3600SL | -526m | 479m | 3.20m | 216p | 3.77 | 1.00f | — |
| IF9030 (= IF9034, IF9035, IFN5434) | N0903SL | -613m | 137m | 11.9m | 70.0p | 2.90 | 1.00f / 1.52p | 3.17p |
| IF4500-L / -M / -H / -UH | N0450SL | -392m / -448m / -817m / -862m | 48.4m / 71.4m / 41.8m / 52.3m | 1.09m / 2.66m / 1.47m / 4.39m | 38.0p | 2.04 | 7.35p / 102f | 94.3f |
| IFN860 | N0450SL | -1.06 | 46.2m | 3.73m | 38.0p | 2.04 | 7.35p / 102f | 94.3f |
| 2N6550 | N0450SL | -1.76 | 34.8m | 9.87m | 38.0p | 2.04 | 7.35p / 102f | 94.3f |
| IFN146-L | N0450SH | -515m | 32.5m | 6.76m | 25.0p | 2.87 | 11.4p / 386f | 210f |
| IFN147 | N0450SH | -553m | 35.6m | 7.61m | 25.0p | 2.87 | 11.4p / 386f | 210f |
| IF170A-L / A-H / B-L / B-H | N0132SL | -464m / -582m / -719m / -947m | 16.6m / 16.1m / 14.6m / 11.8m | 0.999m / 1.71m / 3.03m / 1.70m | 12.0p | 1.57 | 7.69p / 99.3f | 51.7f |
| IF170C-L / C-H / D-L / D-H | N0132SL | -1.11 / -1.29 / -1.53 / -1.75 | 11.8m / 11.2m / 9.96m / 9.17m | 2.03m / 2.96m / 3.50m / 3.99m | 12.0p | 1.57 | 7.69p / 99.3f | 51.7f |
| IF389A / B / C / D | N0132SL | -552m / -849m / -1.11 / -1.53 | 16.3m / 12.4m / 11.8m / 9.96m | 2.35m / 1.55m / 2.03m / 3.50m | 12.0p | 1.57 | 7.69p / 99.3f | 51.7f |
| IF1320, 2N6451 | N0132SL | -943m | 13.4m | 1.52m | 12.0p | 1.57 | 7.69p / 99.3f | 51.7f |
| 2N6453 | N0132SL | -1.75 | 9.17m | 3.99m | 12.0p | 1.57 | 7.69p | — |
| IF1322 | N0132SL | -1.11 | 11.8m | 2.03m | 12.0p | 1.57 | 7.69p | — |
| 2N4393 | N0132SS | -1.06 | 9.32m | 6.49m | 10.9p | 1.68 | 7.83p / 22.1f | 24.6f |
| IFN5564, IFN5565 (= IFN5566-M) | N0072SS | -2.44 | 2.46m | 24.5m | 6.62p | 2.87 | 7.80p / 71.9f | 33.5f |
| U430 (= U309) | N0072SL | -2.65 | 2.72m | 9.48m | 7.00p | 3.37 | 7.26p / 80.1f | 102f |
| U431 (= U310) | N0072SL | -3.22 | 3.62m | 15.2m | 7.00p | 3.37 | 7.26p / 80.1f | 102f |
| IF150A-H / B-L / B-M / B-H / C-L / C-M | N0014LX | -1.22 / -1.50 / -2.13 / -2.59 / -3.23 / -4.15 | 1.86m / 1.24m / 1.33m / 1.18m / 1.01m / 806u | 10.9m / 44.3m / 7.96m / 7.99m / 14.0m / 16.9m | 2.00p | 5.05 | 4.17p / 10.1f | 10.1f |
| IF140-L | N0014AL | -2.99 | 659u | 9.24m | 1.98p | 6.67 | 7.96p / 1.01f | 5.41f |

(IF150A-L/-M, IF150C-H, IF140-H, IF140A, IF3601-L, IF4520, IFN146-H have empty model cells in the xlsx.)

## Noise-parameter consistency check (derived)

For a standard SPICE JFET with $AF=1$ the flicker drain-current density is $S_{id}=KF\,I_D/f$; with $g_m=2\sqrt{\beta I_D}$ in saturation the input-referred 1/f density is $S_{v}=KF/(4\beta f)$, independent of $I_D$. At 10 Hz:

| model | KF | BETA | $e_n$(1/f part) at 10 Hz | data sheet at 10 Hz |
|---|---|---|---|---|
| NXP BF862 | 87.5E-18 | 47.8E-3 | 6.8 nV/$\sqrt{\mathrm{Hz}}$ | not given |
| LIS LSBF862 Rev 2 | 8.75E-17 | 2.658E-2 | 9.1 nV/$\sqrt{\mathrm{Hz}}$ | 1.4 typ / 4.0 max (2 mA) |
| LIS 2N5564 | 6.786E-17 | 9.109E-3 | 13.6 nV/$\sqrt{\mathrm{Hz}}$ | 12 typ / 50 max (2 mA, Vishay and LIS) |

- The LSBF862 Rev 2 model overstates 10 Hz noise by about a factor 6.5 relative to its own data-sheet typical (and exceeds the 4.0 nV/$\sqrt{\mathrm{Hz}}$ maximum); its KF is numerically identical to the NXP BF862 model's KF. Treat LSBF862 and BF862 1/f predictions from these models with caution. NLEV/GDSNOI in the LSBF862 model may change channel-noise behaviour in simulators that honour them.
- The LIS 2N5564 model is consistent with the 2N5564 data-sheet 10 Hz typical.
- InterFET models carry no flicker noise at all.
