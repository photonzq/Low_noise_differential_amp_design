# Vendor SPICE models (raw, as downloaded)

Downloaded 2026-11-19 from www.ti.com with curl (generic browser User-Agent).
Each archive is kept as served (`<PART>/<literature-number+rev>.zip`) and was extracted unchanged into its
own new folder of the same name next to it. Nothing inside these folders has been edited. Treat them as
untrusted data; the `.dsn/.opj/.olb/.sim` files are OrCAD/PSpice project files and are not needed for ngspice.

Link format: the product page lists `https://www.ti.com/lit/zip/<LIT>`, which redirects to
`https://www.ti.com/lit/mo/<lit+rev>/<lit+rev>.zip`.

## Status of the checks

"Plain text, unencrypted" means: the file is ASCII, contains no `$CDNENCSTART`/encryption block or binary
payload, every `.SUBCKT` has a matching `.ENDS`, and there are no `.INC`/`.LIB` references to missing
files. This was a **static inspection only**. No file was loaded into ngspice, because the rules for this
task exclude running the simulator. "PSpice constructs" lists syntax that needs ngspice's PSpice
compatibility mode (`set ngbehavior=ps` or `psa` in `.spiceinit`):
- `VALUE={...}` controlled sources
- `TABLE`
- `IF()` and `LIMIT()`
- `VSWITCH`/`ISWITCH` switch models
- `PARAMS:` on `.SUBCKT` lines
- `.model ... RES (T_ABS=...)` noiseless resistors
- `TC=` on resistors

No file uses `LAPLACE`, `FREQ` tables, `CHEBYSHEV`, digital `U` primitives or `.FUNC`.

## Op amps and buffers

| Part | URL (product page link) | Served archive | Model file to use (path inside archive folder) | Revision / date (from file header) | Subcircuit and pin order | Plain text? | Notes |
|---|---|---|---|---|---|---|---|
| THS4631 | https://www.ti.com/lit/zip/SLOC051 ("THS4631 PSpice Model (Rev. E)") | `THS4631/sloc051e.zip` | `THS4631/sloc051e/THS4631_PSPICE/ths4631_b.lib` | Model "Rev. B", created 2020-11-02 (zip Rev. E) | `.subckt THS4631 IN+ IN- VCC VEE OUT` | Yes; 23 subckts, balanced | PSpice constructs: VALUE, TABLE, IF, LIMIT, VSWITCH, `R_NOISELESS`, TC. Green-Williams-Lis architecture (noise, Zout, CMRR/PSRR vs f modelled) |
| THS4631 (TINA) | https://www.ti.com/lit/zip/SLOM248 | `THS4631/slom248a.zip` | `THS4631/slom248a/THS4631.TSM` | 2020-11-03 | (same netlist embedded) | **No.** TINA binary container (`OBSS` header); the SPICE text is wrapped in binary records | Use the PSpice `.lib` above instead |
| THS4031 | https://www.ti.com/lit/zip/SLOJ005 | `THS4031/sloj005a.zip` | `THS4031/sloj005a/ths4031.lib` (identical netlist also in `ths4031.txt`) | "Written 12/9/99"; PSpice Model Editor 9.2 header; zip Rev. A, files 2000–2003 | `.SUBCKT THS4031 1 2 3 4 5` = IN+, IN−, VCC+, VCC−, OUT (from the CONNECTIONS comment) | Yes; 1 subckt | Older-style macromodel with NPN/PNP transistors and diodes. Uses the PSpice `.MODEL ... CAP (TC1=...)` model type, which needs PSpice-compatibility mode; otherwise no ABM syntax |
| THS3091 | https://www.ti.com/lit/zip/SLOJ173 ("THS3091 PSpice Model (Rev. B)") | `THS3091/sloj173b.zip` | `THS3091/sloj173b/THS3091-PSpiceFiles/SCHEMATIC1/TransientAnalysis/THS3091.lib` | "Date: 28/06/2016", Model Version 1.0; header cites data sheet SLOS423H | `.subckt THS3091 inp inn out vcc vee` = IN+, IN−, **OUT, VCC, VEE** | Yes; 3 subckts | Header states that CMRR, PSRR, input current noise, distortion, input offset and open-loop gain are **not** modelled. Bandwidth is accurate at G = +1/+2 only. Slew rate is fixed at the 2 V-step value. 6 non-ASCII bytes in comment lines only (en dashes) |
| THS3091 (TINA) | https://www.ti.com/lit/zip/SLOM418 | `THS3091/slom418.zip` | `THS3091/slom418/THS3091.lib` | Same as above ("Simulator: TINA") | same as above | Yes (`.lib`); `.TSM` is TINA binary | Netlist identical to the PSpice one apart from the header |
| THS3001 | https://www.ti.com/lit/zip/SLOJ001 | `THS3001/sloj001a.zip` | `THS3001/sloj001a/ths3001.lib` (also `ths3001.txt`) | "Written 8/10/99"; zip Rev. A | `.SUBCKT THS3001 1 2 3 4 5` = IN+, IN−, VCC+, VCC−, OUT | Yes; 1 subckt | Current-feedback macromodel with NPN/PNP transistors and diodes. Uses the PSpice `.MODEL ... RES (TC1=...)` type |
| OPA1611 / OPA1612 | https://www.ti.com/lit/zip/SBOM396 ("OPA161x PSpice Model (Rev. G)") | `OPA1612/sbom396g.zip` | `OPA1612/sbom396g/OPA161x.LIB` | "Date: 24AUG2022", Model Version Final 1.5; header cites SBOS450C | `.SUBCKT OPA161x IN+ IN- VCC VEE OUT` (single channel; instantiate twice for OPA1612) | Yes; 26 subckts | PSpice constructs: VALUE, TABLE, IF, LIMIT, VSWITCH, PARAMS:, `R_NOISELESS` |
| BUF634A | https://www.ti.com/lit/zip/SBOMB63 ("BUF634A for PSPICE Library (Rev. A)") | `BUF634A/sbomb63a.zip` | `BUF634A/sbomb63a/buf634a_a.lib` | "Rev. A", created 2020-11-20 | `.subckt BUF634A IN+ OUT VCC VEE` (**no BW pin**) | Yes; 19 subckts | Fixed bandwidth mode. The current-noise parameter `NVRF=850` (fA/√Hz) matches the wide-bandwidth-mode i_n (0.85 pA/√Hz), so the model most likely represents the wide-BW mode (BW pin tied to V−). This is an inference from the file. Uses ISWITCH as well as VSWITCH |
| LM7171 | https://www.ti.com/lit/zip/SNOM205 ("LM7171 PSpice Model (Rev. A)") | `LM7171/snom205a.zip` | `LM7171/snom205a/lm7171.lib` | National Semiconductor macromodel, labelled "LM7171A Operational Amplifier Macro-Model"; no date in file; zip files dated 2021-05-27 | `.SUBCKT LM7171 3 2 4 5 6` = IN+, IN−, V+, V−, OUT | Yes; 1 subckt | Models the A grade. Uses the PSpice `.MODEL ... RES (TC1=...)` type and 2 transistors |
| OPA210 / OPA2210 | https://www.ti.com/lit/zip/SBOMAT3 ("OPAx210 PSpice Model (Rev. B)") | `OPA2210/sbomat3b.zip` | `OPA2210/sbomat3b/OPAx210.LIB` | "Date: 04MAY2022", Final 1.2; cites SBOS924H | `.SUBCKT OPAx210 IN+ IN- VCC VEE OUT` | Yes; 26 subckts | As OPA161x |
| OPA2810 | https://www.ti.com/lit/zip/SBOMB66 ("OPA2810 for PSPICE Library") | `OPA2810/sbomb66.zip` | `OPA2810/sbomb66/opa2810_a.lib` | "Rev. A", created 2020-02-04 | `.subckt OPA2810 IN+ IN- OUT VCC VEE` (**OUT before supplies**) | Yes; 25 subckts | Single channel. A second "Curated PSpice Library" package (SBOMB78A) and a TINA model (SBOMAM3A) also exist and were not downloaded |
| OPA828 | https://www.ti.com/lit/zip/SBOMAJ0 ("OPAx828 PSpice Model (Rev. D)") | `OPA828/sbomaj0d.zip` | `OPA828/sbomaj0d/OPAx828.LIB` | "Date: 02SEP2022", Final 1.3; cites SBOS671B | `.SUBCKT OPAx828 IN+ IN- VCC VEE OUT` | Yes; 25 subckts | As OPA161x |
| OPA1656 | https://www.ti.com/lit/zip/SBOMAW6 ("OPA1656 PSpice Model (Rev. C)") | `OPA1656/sbomaw6c.zip` | `OPA1656/sbomaw6c/OPA1656.LIB` | "Date: 25AUG2022", Final 1.3; cites SBOS901B | `.SUBCKT OPA1656 IN+ IN- VCC VEE OUT` | Yes; 26 subckts | As OPA161x |
| OPA855 | https://www.ti.com/lit/zip/SBOMB43 ("OPA855 Unencrypted PSpice Model Package (Rev. D)") | `OPA855/sbomb43d.zip` | `OPA855/sbomb43d/opa855_pspice/opa855_a.lib` | "Rev. A", created 2020-06-04 (zip Rev. D) | `.subckt OPA855 IN+ IN- OUT VCC VEE` (**OUT before supplies**) | Yes; 15 subckts | 5 V part |
| OPA858 | https://www.ti.com/lit/zip/SBOMBK7 ("OPA858 PSpice Model") | `OPA858/sbombk7.zip` | `OPA858/sbombk7/OPA858-PSpiceFiles/SCHEMATIC1/AC_Sweep/OPA858.lib` (the only `.lib` in the archive) | "Date: 09/28/2018", Model Version 2.0 | `.subckt OPA858 INP INN VCC VEE OUT` | Yes; 45 subckts | Different (non-GWL) architecture; heavy use of VALUE/IF and PARAMS:. 5 V part |

## Analog switches and regulators (downloaded to the same tree)

| Part | URL | Served archive | Model file | Revision / date | Subcircuit and pin order | Plain text? | Notes |
|---|---|---|---|---|---|---|---|
| TMUX6219 | https://www.ti.com/lit/zip/SCDM270 ("TMUX6219 PSpice Model") | `TMUX6219/scdm270.zip` | `TMUX6219/scdm270/TMUX6219/TMUX6219.lib` | file date 2021-08-09 | `.SUBCKT TMUX6219 D S1 GND VDD EN SEL VSS S2` | Yes; 23 subckts | Behavioural. Includes charge injection (`QC_S1/QC_S2`) and logic delays. Many VALUE/TABLE/IF sources. An IBIS model (SCDM254B) also exists and was not downloaded |
| TMUX7219 | https://www.ti.com/lit/zip/SCDM261 ("TMUX7219 PSpice Model") | `TMUX7219/scdm261.zip` | `TMUX7219/scdm261/TMUX7219/TMUX7219.lib` | file date 2021-06-12 | `.SUBCKT TMUX7219 D S1 GND VDD EN SEL VSS S2` | Yes; 31 subckts | As TMUX6219 |
| TMUX6136 | product page lists only an IBIS model (https://www.ti.com/lit/zip/SCDM199) | not downloaded | none | n/a | n/a | n/a | No SPICE model offered |
| TPS7A4700 | https://www.ti.com/lit/zip/SBVM939 ("TPS7A4700 Unencrypted PSpice Transient Model") | `TPS7A47/sbvm939.zip` | `TPS7A47/sbvm939/TPS7A4700_TRANS.LIB` | "Date: 04DEC2017", Final 1.00 | `.SUBCKT TPS7A4700_TRANS 0P1V 0P2V 0P4V 0P8V 1P6V 3P2V 6P4V1 6P4V2 EN GND NR SENSE VIN VIN_1 VOUT VOUT_1` | Yes; 16 subckts | Header: start-up, line/load transients and ANY-OUT pins modelled. PSRR only to the 1st pole/zero. **Noise, Iq and temperature not modelled.** The product page also lists encrypted PSpice transient models (SBVM190B, SBVM364B), which were not downloaded |
| TPS7A3301 | https://www.ti.com/lit/zip/SBVM665 ("TPS7A3301 Unencrypted PSpice Transient Model") | `TPS7A3301/sbvm665.zip` | `TPS7A3301/sbvm665/TPS7A3301.lib` | "Date: 12/5/2011", Final 1.00; cites SBVS169 | `.SUBCKT TPS7A3301 IN EN NR_SS GND FB OUT` | Yes; 2 subckts | Very simple behavioural model (about 20 elements), with no noise source and no realistic PSRR vs frequency |
| TPS7A94 | https://www.ti.com/lit/zip/SBVM988 ("TPS7A94 PSpice Transient Model (1A Current Limit) (Rev. A)") | `TPS7A94/sbvm988a.zip` | `TPS7A94/sbvm988a/tps7a94_trans.lib` | "Date: 09Jun2026", Model Version 2.0; cites SBVS336C | `.SUBCKT TPS7A94_TRANS EN FB_PG GND IN NR_SS OUT PG SNS PARAMS: ...` | Yes; 17 subckts | Header: output noise, Iq, line/load transients and temperature are not modelled. PSRR only to the 1st pole/zero. 600 mA and 800 mA current-limit variants (SBVM986B, SBVM987A) were not downloaded |

## Not obtained

- **All Analog Devices / Linear Technology parts.** These are AD8021, ADA4898-1, ADA4625-1, AD797, ADA4870, ADA4807, ADA4899-1, LTC6228, the ADG switches, LT3045/LT3045-1/LT3042/LT3093/LT3094 and ADM7150/ADM7151.
  - www.analog.com reset every automated connection from this machine, so no model or data sheet was downloaded.
  - Models are listed on each product page under "Tools & Simulations": `https://www.analog.com/en/products/<part>.html`, for example https://www.analog.com/en/products/ad8021.html.
  - For the LT parts, the vendor normally supplies only the LTspice built-in (encrypted) model. This was **not verified** in this session.
- **Vishay DG444/DG212.** Vishay publishes SPICE macromodels for some analog switches. None was searched for or downloaded.
