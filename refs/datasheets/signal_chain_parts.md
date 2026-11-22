# Signal-chain parts after the input stage: data-sheet values

Compiled 2026-11-19 for the DC–10 MHz preamplifier (SR560 class; ±15 V analog rails; ngspice-46 in PSpice-compatibility mode).

## How to read the tables

- **Sources.** Every value was read from rendered page images of the data sheets in the subfolders `opamp/`, `switches/`, `relays/` and `regulators/`. "p.N" is the 1-based PDF page index; for these files it equals the printed page number. TI tables are cited by section number (§) because they are not numbered.
- **Typical values.** Values are typical at 25 °C unless a max/min is given ("typ/max").
- **Plot readings.** "~" marks a value read off a log-scale plot (about ±10 %, or ±2–3 dB for dB plots).
- **Missing values.** "n.s." means not specified in the data sheet.
- **Status.** "Active" is the lifecycle status shown on the TI product page on 2026-11-19.
- **Models.** Model files, revisions and pin orders are listed in `../../sim/models/vendor_opamps_raw/README.md`. Pin orders are repeated in table A2.
- **Analog Devices parts were not obtained.** All ADI parts (AD8021, ADA4898-1, ADA4625-1, AD797, ADA4870, ADA4807, ADA4899-1, LTC6228, ADG14xx/ADG1206/ADG1236/ADG5419/ADG16xx, LT304x/LT309x, ADM715x) are missing because www.analog.com reset every automated connection. Product-page URLs are in the folder READMEs. No ADI values appear in these tables.

---

## A. Op amps and buffers

### A1. Data-sheet values

The column headings stand for:
- **GBW / BW; min gain**: gain-bandwidth or −3 dB bandwidth, and the minimum stable gain.
- **SR**: slew rate.
- **e_n white / 10 Hz**: input voltage noise, white level and at 10 Hz.
- **i_n**: input current noise.
- **V_OS; drift**: input offset voltage and its temperature drift.
- **CMR**: input common-mode range.
- **C_in**: input capacitance.
- **HD @ ~1 MHz**: harmonic distortion (HD2/HD3) at or near 1 MHz.
- **I_Q / amp**: quiescent current per amplifier.

#### High-speed parts

| Part (type) | Supply (rec.; abs max) | GBW / BW; min gain | SR | e_n white / 10 Hz | i_n | V_OS; drift | Output swing | Output current | CMR | C_in | HD @ ~1 MHz | I_Q / amp | Status | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **THS4631** (JFET-input VFA) | ±5 to ±15 V (spec'd to ±16.5 V); 33 V abs | GBW 210 MHz (G ≥ 20); BW 325 MHz at G = 1, 105 MHz at G = 2, 25 MHz at G = 10; unity-gain stable | 550 V/µs (G = 2, 2 V step); 900 V/µs (10 V step) | 7 nV/√Hz (f > 10 kHz) / ~50 nV/√Hz | 20 fA/√Hz (f > 10 kHz; the plot shows ~15 fA at 100 kHz and ~2 fA at 10 Hz) | ±260/±500 µV; 2.5 (12 max) µV/°C; I_B 50 pA | ±13.5 V (1 kΩ); ±11 V (100 Ω) | 180 mA typ / 120 min into 20 Ω (abs max I_O 150 mA) | −13 to +12 V | 3.9 pF ∥ 1 GΩ (diff and CM) | G = 2, 2 Vpp, 1 kΩ: HD2 ~−103 / HD3 ~−72 dBc; 100 Ω: ~−94 / ~−68 dBc | 12.5/14.5 mA | Active | TI_ths4631_datasheet.pdf (SLOS451D): p.4 §6.1, §6.3; p.5–6 §6.5; p.8 Fig 6-7, 6-8, 6-12; p.13, p.17 |
| **THS4031** (bipolar VFA, offset-null pins) | ±4.5 to ±16 V; 33 V abs; differential input ±1.5 V abs | UGBW 120 MHz; −3 dB BW 100 MHz at G = 2 or −1; unity-gain stable; FPBW 1.6 MHz at 20 Vpp | 100 V/µs (G = −1, 20 V step) | 1.2 / ~4.0 nV/√Hz | 2.3 pA/√Hz (f > 10 kHz); ~18 pA/√Hz at 10 Hz | 0.3/2 mV; 2 µV/°C; I_B 9 µA | ±13.6 V (1 kΩ); ±12.9 V (250 Ω) | 200 mA typ / 60 min into 10 Ω | ±14.3 V typ (±13.5 min) | 1.5 pF, 2 MΩ | THD −96 dBc (1 kΩ), −81 dBc (150 Ω) at G = 2, 2 Vpp; HD2/HD3 ~−97/~−98 dBc (1 kΩ) | 7.5/10 mA | Active | TI_ths4031_datasheet.pdf (SLOS224L): p.4 §5.1, §5.3; p.6–9 §5.6–5.7; p.12 Fig 5-13 to 5-17 |
| **THS3091** (CFA) | ±5 to ±16 V; 33 V abs | −3 dB BW (±15 V, 100 Ω): 715 MHz (DDA) / 600 MHz (DGN) at G = 1 with R_F = 1.78 kΩ; 305 MHz at G = 2 (1.21 kΩ); 205 MHz at G = 5 (1 kΩ); 190 MHz at G = 10 (866 Ω). Unity-gain stable with the specified R_F | 3600 V/µs (G = 2, 10 V); 6000 V/µs (G = 5, 20 V) | 1.1 / ~6.5 nV/√Hz | 15 pA/√Hz (+in), 14 pA/√Hz (−in) at f > 10 kHz; ~100 / ~200 pA/√Hz at 10 Hz | 0.9/3 mV; ±19 µV/°C; I_B 4 µA | ±13.2 V (1 kΩ); ±12.5 V (100 Ω) | 310 mA typ (225 source / 200 sink min) into 40 Ω | ±13.6 V | +in 0.7 MΩ ∥ 2.4 pF; −in 30 Ω ∥ 1.4 pF | 1 MHz, 4 Vpp, G = 2: ~−89/−89 dBc (100 Ω), ~−108/−113 dBc (1 kΩ). 10 MHz, 2 Vpp: HD2 −72 / HD3 −70 dBc (100 Ω) | 9.5/10.5 mA | Active | TI_ths3091_datasheet.pdf (SLOS423K): p.5 §7.1, §7.3; p.6–7 §7.5; p.11 Fig 7-8 to 7-11; p.12 Fig 7-16; p.20 Table 8-1 |
| **THS3001** (CFA) | ±4.5 to ±16 V; 33 V abs | 420 MHz at G = 1 (R_F = 1 kΩ); 385 MHz at G = 2 (680 Ω); 350 MHz at G = 5 (560 Ω); FPBW 31 MHz at 20 Vpp. R_F is mandatory | 6300–6500 V/µs (20 Vpp, G = ±5) | 1.6 nV/√Hz (10 kHz) / n.s. (~3.0 nV/√Hz at 100 Hz, the lowest frequency plotted) | 13 (+in) / 16 (−in) pA/√Hz at 10 kHz | 1/3 mV; 5 µV/°C | ±13.1 V (1 kΩ); ±12.8 V (150 Ω) | 120 mA typ / 85 min into 75 Ω | ±13.2 V | +in 1.5 MΩ; −in 15 Ω; 7.5 pF diff | 1 MHz, G = 2, 150 Ω: ~−105/−114 dBc (2 Vpp), ~−90/−93 dBc (10 Vpp). THD −80 dBc at 10 MHz, 2 Vpp | 6.6/9 mA | Active | TI_ths3001_datasheet.pdf (SLOS217I): p.4–6 §5.1–5.5; p.9 Fig 5-10; p.10 Fig 5-17; p.16 Table 7-1; p.19 |
| **LM7171** (VFA, high slew) | 5.5–36 V total; 36 V abs | UGBW 160 MHz (A grade) / 200 MHz (B grade); BW 220 MHz at A_V = +2. **Not unity-gain stable: noise gain ≥ 2** | 4100 V/µs (A_V = 2, 13 Vpp) | 8.5 (A) / 14 (B) nV/√Hz at 10 kHz; 10 Hz ~43 (A, ±5 V plot only) and ~95–100 (B, ±15 V) | 1 (A) / 1.5 (B) pA/√Hz | 0.2/1 mV (A), 0.2/3 mV (B); 35 µV/°C | +13.3/−13.2 V (1 kΩ); +11.8/−10.5 V (100 Ω) | 100 mA linear; I_SC 140/135 mA | ±13.35 V | n.s. (R_in 320 MΩ CM, 18 MΩ diff) | A, 100 Ω: ~−103/~−122 dBc (amplitude not stated). B, A_V = 2, 1 Vpp in, 100 Ω: ~−92/~−71 dBc | 6.5/8.5 mA | Active | TI_lm7171_datasheet.pdf (SNOS760D): p.3–5 §5.1–5.5; p.10 Fig 5-16, 5-17; p.13 Fig 5-36; p.17–18; p.23 Fig 5-90; p.24–25 |
| **BUF634A** (open-loop buffer, G ≈ 1) | ±2.25 to ±18 V; 40 V abs | Wide-BW mode 210 MHz (1 kΩ) / 200 MHz (100 Ω); low-I_Q mode 35/31 MHz. Gain 0.99 (1 kΩ), 0.95 (100 Ω) | 3750 V/µs (20 V step) | Wide-BW 3.4 nV/√Hz at 1 kHz (plot ~3.0 white) / ~18 nV/√Hz. Low-I_Q 8.1 / ~14 nV/√Hz | 0.85 pA/√Hz (wide-BW, 100 kHz); ~10 pA/√Hz at 10 Hz | 36/65 mV; 175 µV/°C | Headroom to rails 1.6 V at 10 mA, 2.0 V at 100 mA, 2.2 V at 150 mA | 250 mA continuous; I_SC 375 mA typ | Linear input −13 to +13 V (1 kΩ) | 5 pF ∥ 180 MΩ (wide-BW) | Open loop, 10 Vpp: ~−72/~−79 dBc (1 kΩ); ~−64/~−60 dBc (100 Ω) | 8.5/12 mA (wide-BW); 1.5/2.3 mA (low-I_Q) | Active | TI_buf634a_datasheet.pdf (SBOS948F): p.4–6 §7.1–7.6; p.8 Fig 7-9 to 7-12; p.9 Fig 7-17; p.15 §8.4.1; p.16; p.19 |
| **OPA2810** (dual JFET RRIO VFA) | 4.75–27 V total (±13.5 V max). The abs-max row is printed "±14 V (total bipolar supplies)". **Cannot run on ±15 V** | GBW 70 MHz (G = 11); 75 MHz at G = 1; unity-gain stable | 226–243 V/µs (±12 V, G = 2) | 6 nV/√Hz (500 kHz) / ~150 nV/√Hz | 5 fA/√Hz | 0.1/1.5 mV; 1.5 µV/°C | Rail −0.22 / +0.15 V (667 Ω, ±12 V) | 64 mA linear (48 min); I_SC 108 mA | V− − 0.2 to V+ + 0.2 V (JFET stage only up to V+ − 2.5 V) | 2.5 pF CM; 0.5 pF diff | ±12 V, G = 2, 1 kΩ: −105/−103 dBc (2 Vpp); −92/−86 dBc (10 Vpp) | 3.7/4.1 mA | Active | TI_opa2810_datasheet.pdf (SBOS789C): p.4 §7.1, §7.3; p.8–10 §7.6; p.22 Fig 49; p.27 §8.4.1 |

#### Precision and audio parts

| Part (type) | Supply (rec.; abs max) | GBW / BW; min gain | SR | e_n white / 10 Hz | i_n | V_OS; drift | Output swing | Output current | CMR | C_in | HD @ ~1 MHz | I_Q / amp | Status | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **OPA1611 / OPA1612** (bipolar audio VFA) | ±2.25 to ±18 V; 40 V abs | GBW 80 MHz (G = 100); 40 MHz at G = 1; unity-gain stable | 27 V/µs | 1.1 nV/√Hz (1 kHz) / 2 nV/√Hz | 1.7 pA/√Hz (1 kHz); 3 pA/√Hz at 10 Hz | ±100/±500 µV; 1 (4 max) µV/°C | V± 0.6 V (2 kΩ) | "±30 mA" (p.1); ~45 mA holds ±14.2 V (Fig 27); I_SC +55/−62 mA | V± 2 V | 8 pF ∥ 20 kΩ diff; 2 pF ∥ 1 GΩ CM | n.s. at 1 MHz. THD+N ~0.0004 % at 100 kHz (G = 1, 600 Ω) | 3.6/4.5 mA | Active | TI_opa1611-opa1612_datasheet.pdf (SBOS450C): p.4 §6.1, §6.3; p.5–6 §6.4; p.7–11 |
| **OPA2210** (super-beta bipolar precision VFA) | ±2.25 to ±18 V; 40 V abs | GBW 18 MHz; unity-gain stable | 6.4 V/µs | 2.2 nV/√Hz (1 kHz) / 2.5 nV/√Hz; 0.1–10 Hz 90 nVpp | 400 fA/√Hz | ±5/±35 µV; 0.1 (0.5 max) µV/°C | V± 0.2 V (10 kΩ); V± 0.6 V (600 Ω) | I_SC ±65 mA; collapses at ~45–50 mA (plot) | V± 1.5 V | 9 pF ∥ 400 kΩ diff; 0.5 pF ∥ 1 GΩ CM | n.s. (data only up to 20 kHz) | 2.2/2.5 mA | Active | TI_opa2210_datasheet.pdf (SBOS924H): p.4 §6.1, §6.3; p.6–7 §6.6; p.8; p.12–13 |
| **OPA828** (JFET VFA) | ±4 to ±18 V; 40 V abs | GBW = UGBW = 45 MHz; G = +1 specified (8 % overshoot) | 150 V/µs (10 V step) | 4 nV/√Hz (1 kHz) / 7.5 nV/√Hz | 1.2 fA/√Hz | ±50/±300 µV (D package), ±25/±125 µV (DGN package); 0.45 / 0.2 µV/°C | 0.9 V from rail (10 kΩ); 1.2 V (600 Ω) (the table does not say "from rail"; inferred) | ±30 mA linear; I_SC ±50 mA | V− + 2.5 to V+ − 3.5 V | 6 pF diff; 9 pF CM | 500 kHz, 5 Vpp, G = 1: HD2 −90 / HD3 −105 dBc | 5.5/6.2 mA | Active | TI_opa828_datasheet.pdf (SBOS671D): p.4 §6.1, §6.3; p.5–6 §6.5; p.8; p.12; p.15 |
| **OPA1656** (CMOS audio VFA) | ±2.25 to ±18 V; 40 V abs | GBW 53 MHz (G = 100); UGBW 20 MHz | 24 V/µs | 2.9 nV/√Hz (10 kHz), 4.3 nV/√Hz (1 kHz) / ~37 nV/√Hz | 6 fA/√Hz | ±0.5/±1 mV; 0.3 (2 max) µV/°C | V± 0.25 V (2 kΩ) | I_SC ±100 mA; ~88–98 mA (plot) | V− to V+ − 2.25 V | 9.1 pF diff; 1.9 pF CM | n.s. (data only up to 20 kHz) | 3.9/4.6 mA | Active | TI_opa1656_datasheet.pdf (SBOS901C): p.4 §6.1, §6.3; p.6–7 §6.6; p.8–9; p.13 |

#### 5 V reference parts (cannot run on ±15 V)

| Part (type) | Supply (rec.; abs max) | GBW / BW; min gain | SR | e_n white / 10 Hz | i_n | V_OS; drift | Output swing | Output current | CMR | C_in | HD @ ~1 MHz | I_Q / amp | Status | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **OPA855** (bipolar, decompensated) | 3.3–5.25 V; 5.5 V abs. **No ±15 V** | GBWP 8 GHz; SSBW 2.5 GHz; **G ≥ 7 V/V** | 2750 V/µs | 0.98 nV/√Hz (1 MHz) / n.s. (~2.8 nV/√Hz at 1 kHz) | 2.5 pA/√Hz (1 MHz) | ±0.2/±1.5 mV; 0.5 µV/°C | ~1.05 to 4.1 V on 5 V (200 Ω) | 80 mA linear; I_SC 105 mA | 1.1–4.6 V (5 V supply) | 0.6 pF CM; 0.2 pF diff | 2 Vpp, G = 7: HD2 ~−108 / HD3 ~−95 dBc | 17.8 mA | Active | TI_opa855_datasheet.pdf (SBOS622D): p.1; p.5–7 §6.1–6.5; p.9–10 Fig 6-11, 6-13, 6-14 |
| **OPA858** (CMOS, decompensated) | 3.3–5.25 V; 5.5 V abs. **No ±15 V** | GBWP 5.5 GHz; SSBW 1.2 GHz; **G ≥ 7 V/V** | 2000 V/µs | 2.5 nV/√Hz (1 MHz) / n.s. (~25 nV/√Hz at 1 kHz) | ~0.5 fA/√Hz (1 kHz); ~50 fA/√Hz (1 MHz), from plot | ±0.8/±5 mV; 2 µV/°C | as OPA855 | 80 mA linear; I_SC 105 mA | 0–3.6 V (5 V supply) | 0.62 pF CM; 0.2 pF diff | 2 Vpp, G = 7: ~−105 / ~−93.5 dBc | 20.5 mA | Active | TI_opa858_datasheet.pdf (SBOS629B): p.1–2; p.5–7; p.9–10; p.19 Fig 8-8 |

Data-sheet quirks found while reading:
- **THS4631:** the tabulated i_n (20 fA/√Hz) and the plot (~15 fA/√Hz at 100 kHz) disagree.
- **THS3091:** the HD values in the table are printed without minus signs.
- **THS3001:** Fig 5-18 is captioned "vs Frequency" but plots against V_out and duplicates Fig 5-17.
- **LM7171:** the A-grade noise plots exist only at ±5 V.
- **BUF634A:** the table gives 3.4 nV/√Hz, but the plot flattens at ~3.0 nV/√Hz.

### A2. Models and status

| Part | Model available | Model file (relative to `sim/models/vendor_opamps_raw/`) | Subcircuit pin order | Model limitations stated in the file |
|---|---|---|---|---|
| THS4631 | Y (PSpice, plain text) | THS4631/sloc051e/THS4631_PSPICE/ths4631_b.lib | `THS4631 IN+ IN- VCC VEE OUT` | Green-Williams-Lis architecture with noise, Zout, CMRR/PSRR(f) |
| THS4031 | Y | THS4031/sloj005a/ths4031.lib | `THS4031 1 2 3 4 5` = IN+ IN− VCC+ VCC− OUT | 1999 transistor-level macromodel |
| THS3091 | Y | THS3091/sloj173b/.../TransientAnalysis/THS3091.lib | `THS3091 inp inn out vcc vee` (**out before supplies**) | No CMRR, PSRR, i_n, distortion or A_OL. BW is correct only at G = 1–2 |
| THS3001 | Y | THS3001/sloj001a/ths3001.lib | `THS3001 1 2 3 4 5` = IN+ IN− VCC+ VCC− OUT | 1999 transistor-level macromodel |
| LM7171 | Y | LM7171/snom205a/lm7171.lib | `LM7171 3 2 4 5 6` = IN+ IN− V+ V− OUT | Models the A grade |
| BUF634A | Y | BUF634A/sbomb63a/buf634a_a.lib | `BUF634A IN+ OUT VCC VEE` (no BW pin) | Appears to model the wide-BW mode (inferred from the i_n parameter) |
| OPA2810 | Y | OPA2810/sbomb66/opa2810_a.lib | `OPA2810 IN+ IN- OUT VCC VEE` (**out before supplies**) | One channel |
| OPA1611/1612 | Y | OPA1612/sbom396g/OPA161x.LIB | `OPA161x IN+ IN- VCC VEE OUT` | One channel |
| OPA2210 | Y | OPA2210/sbomat3b/OPAx210.LIB | `OPAx210 IN+ IN- VCC VEE OUT` | One channel |
| OPA828 | Y | OPA828/sbomaj0d/OPAx828.LIB | `OPAx828 IN+ IN- VCC VEE OUT` | |
| OPA1656 | Y | OPA1656/sbomaw6c/OPA1656.LIB | `OPA1656 IN+ IN- VCC VEE OUT` | One channel |
| OPA855 | Y | OPA855/sbomb43d/opa855_pspice/opa855_a.lib | `OPA855 IN+ IN- OUT VCC VEE` (**out before supplies**) | |
| OPA858 | Y | OPA858/sbombk7/.../AC_Sweep/OPA858.lib | `OPA858 INP INN VCC VEE OUT` | |
| AD8021, ADA4898-1, ADA4625-1, AD797, ADA4870, ADA4807, ADA4899-1, LTC6228 | not obtained | none (www.analog.com blocked automated access) | — | — |

All TI models were inspected statically only: they are unencrypted text with balanced `.SUBCKT`/`.ENDS`, and no ngspice load was attempted. The newer ones use PSpice ABM syntax (VALUE/TABLE/IF/LIMIT/VSWITCH), so ngspice must run in PSpice-compatibility mode. The two TINA `.TSM` files are binary containers and are not usable directly.

---

## B. Analog switches and multiplexers (±15 V operation)

| Part | Configuration | Supply | R_ON typ/max (±15 V) | R_ON flatness; ΔR_ON | C_S(OFF) / C_D(OFF) / C_ON | Charge injection | −3 dB BW | Off-isolation at 1 MHz / 10 MHz | Crosstalk at 1 MHz / 10 MHz | Leakage at 25 °C (typ/max) | t_ON / t_OFF | SPICE model | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **TMUX6219** | 1× SPDT (2:1) with EN and SEL | ±4.5 to ±18 V; 4.5–36 V single; 38 V abs | 2.1/2.9 Ω (V_S = ±10 V, 10 mA) | 0.5/0.6 Ω; 0.05/0.25 Ω | 33 / 48 / 148 pF | −10 pC (V_D = 0, C_L = 1 nF) | 40 MHz (50 Ω, 5 pF); plot ~36 MHz | −55 dB (table) / ~−38 dB (plot); RL = 50 Ω | −106 dB (table, matches the switch-OFF plot) / ~−68 dB. Switch-ON plot: ~−58 / ~−40 dB | I_S(OFF) 0.05/±0.2 nA; I_D(OFF) 0.05/±1 nA; I_D(ON) 0.04/±1 nA (±16.5 V) | t_ON(EN) 100/170 ns; t_OFF(EN) 100/180 ns; t_TRAN 120/175 ns | Y: PSpice plain text, `TMUX6219 D S1 GND VDD EN SEL VSS S2` | TI_tmux6219_datasheet.pdf (SCDS420E): p.4–7 §5.4–5.7; p.19–20 Fig 5-23 to 5-28 |
| **TMUX7219** (latch-up immune) | 1× SPDT with EN and SEL | ±4.5 to ±22 V; 4.5–44 V single; 48 V abs | 2.1/2.9 Ω | 0.5/0.6 Ω; 0.05/0.25 Ω | 33 / 48 / 148 pF | −10 pC | 40 MHz; plot ~36 MHz | −55 dB / ~−38 dB | −106 dB / ~−68 dB (switch OFF). Switch ON: ~−59 / ~−39 dB | I_S(OFF) 0.05/±0.15 nA; I_D(OFF) 0.05/±1 nA; I_D(ON) 0.04/±1 nA | as TMUX6219 | Y: PSpice plain text, `TMUX7219 D S1 GND VDD EN SEL VSS S2` | TI_tmux7219_datasheet.pdf (SCDS407F): p.4–7; p.17–18 Fig 5-23 to 5-28 |
| **TMUX6136** | 2× SPDT (SEL1, SEL2; no EN) | ±5 to ±16.5 V; 10–16.5 V single; 36 V abs | 120/135 Ω (V_S = 0, 1 mA); 140/160 Ω (V_S = ±10 V) | 23/33 Ω; 2.5/6 Ω | 2.4 (3.3 max) / n.s. / 5.5 (7.5 max) pF | −0.4 pC | 670 MHz (50 Ω; the −7 dB insertion loss at 1 MHz is the R_ON divider) | −85 dB / ~−63 dB | Inter-channel −105 dB / ~−81 dB; intra-channel −92 dB / ~−71 dB | I_S(OFF) 0.005/±0.05 nA; I_D(ON) 0.008/±0.06 nA | t_TRAN 66/78 ns; t_BBM 40 ns | IBIS only (no SPICE) | TI_tmux6136_datasheet.pdf (SCDS397B): p.4–6 §5.4–5.6; p.10–11 Fig 5-9, 5-10, 5-13 |
| **DG444** (Vishay; DG445 is the NO version) | Quad SPST, NC | ±5 to ±20 V; +5 to +36 V single; 44 V abs | 50/85 Ω (±13.5 V, V_D = ±8.5 V); plot ~35–44 Ω over ±15 V | n.s. | 4 / 4 / 16 pF | −1 pC at V_S = 0; ~−22 to +28 pC over ±10 V | n.s. | 60 dB / ~40 dB (50 Ω) | 100 dB / ~78 dB | I_S(OFF) ±0.01/±0.5 nA; I_D(OFF) ±0.01/±0.5 nA; I_D(ON) ±0.08/±0.5 nA | 120/250 ns; 110/140 ns | not searched | Vishay_DG444-DG445_70054_RevJ.pdf: p.1–2, p.4–5, p.9 |
| **DG212B** (Vishay; plain DG212 not covered) | Quad SPST, NO | ±4.5 to ±22 V; +4.5 to +25 V single; 44 V abs | 45/85 Ω (±10 V, 1 mA) | n.s. (plot ~35–48 Ω over ±15 V); ΔR_ON 2 Ω | 5 / 5 / 16 pF | 1 pC at 0 V; ~−22 to +9 pC over ±15 V | n.s. | ~70 dB / ~50 dB (plot, 50 Ω). Table: 90 dB at 100 kHz | n.s. at 1 MHz (95 dB at 100 kHz) | ±0.01/±0.5 nA (S and D off); ±0.02/±0.5 nA (D on) | 300 ns max / 200 ns max | not searched | Vishay_DG211B-DG212B_70040_RevI.pdf: p.1–5 |
| ADG1419, ADG1206/1207, ADG1611/1612, ADG5419, ADG1236 | not obtained (www.analog.com blocked) | | | | | | | | | | | | |

Notes:
- **TMUX6219/TMUX7219 C_ON.** The 148 pF on-capacitance and ~−38 dB off-isolation at 10 MHz into 50 Ω make these low-R_ON switches poor at 10 MHz unless they sit at a low-impedance node and the isolation is improved with a T arrangement (series–shunt–series).
- **TMUX6136.** Its low capacitance (2.4/5.5 pF) and −63 dB at 10 MHz suit high-impedance nodes. It is the best 10 MHz isolation/capacitance option among the obtained parts, but its R_ON (120–140 Ω) and R_ON flatness (23 Ω) must be inside a feedback loop or in series with a high-impedance load to avoid gain error and distortion.

---

## C. Signal relays

| Relay | Contact form | Contact resistance (max initial) | Thermal EMF | Open-contact C | Contact–coil C | Insulation resistance | Switching rating | Operate / release | Coil (5 V version) | RF data | Magnetic shield | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Omron G6K-2F** | DPDT, bifurcated crossbar, Ag + Au-alloy | 100 mΩ (10 mA, 1 V); typical ~40–60 mΩ in the test histograms | n.s. | n.s. | n.s. | 1000 MΩ min at 500 VDC | 1 A at 30 VDC; 0.3 A at 125 VAC; min load 10 µA at 10 mV | 3 ms / 3 ms max (typ ~1.2–1.8 ms) | 237 Ω, 21.1 mA, ~100 mW (latching G6KU-2F-Y also ~100 mW) | Isolation ~86 dB at 1 MHz, ~67 dB at 10 MHz. Insertion loss ~0.06 dB at 10 MHz (G6K-2G sample) | No; external-field shift ±6 % at ±800 A/m | Omron_G6K_datasheet_K106-E1-11.pdf: p.2–5, p.9 |
| **Coto 9800** (9802/9814 1 Form A; 9852 1 Form C; coaxial 50 Ω) | Reed, dry | 0.125 Ω static (9852: 0.150 Ω); 0.150 Ω dynamic | n.s. | 0.2 pF (9852: 1.0 pF), with the shield guarding | 0.5 pF open (9852: 1.0 pF) | 10¹² Ω (9852: 10⁹ Ω) at 100 V | 100 V (9852: 30 V), 0.25 A (9852: 0.1 A), 3 W | 0.25 ms / 0.05 ms typ (9852: 0.26 ms) | 150 Ω (9852: 110 Ω), ~167 mW derived from V²/R | "up to 6 GHz" claim; no numbers | Yes: magnetic shield plus coaxial shield pin | Coto_9800-series_datasheet_farnell-mirror-91349.pdf (2003): p.1–2 |
| **Pickering 104** (high voltage, SIL) | 1A / 1B / 2A; 104ES electrostatic-screened version | 0.15 Ω (1A); 0.20 Ω (1B, 2A) | n.s. ("controlled thermal EMF" is a build option) | 0.1 pF (guarded) | 2.5 pF closed switch to coil | 10¹² Ω | 1000 VDC, 1 A, 25 W; stand-off 1.5–5 kV | 1.0 ms / 0.3 ms | 375 Ω (1A, switch 1–2), ~67 mW derived | 104ES isolation −62.2 dB at 1 MHz, −60.9 dB at 10 MHz | Yes, internal mu-metal | Pickering_104-high-voltage-sil-reed-relays.pdf (Issue 4.3, Oct 2026): p.1–7, p.10 |
| **Pickering 111** (Pico SIL; 111P plastic; 111RF coaxial) | 1 Form A | 0.15 Ω | n.s. ("controlled thermal EMF" is a build option) | 0.15 pF (guarded) | 1.5 pF | 10¹² Ω | 170 V, 0.5 A, 10 W | 0.5 ms / 0.2 ms | 500 Ω (111), 400 Ω (111P), 180 Ω (111RF); 50–139 mW derived | 111RF: −3 dB at 3.5 GHz; 10 MHz not resolvable on the plot | Yes, mu-metal | Pickering_111-pico-sil-reed-relays.pdf (Issue 1.6, May 2025): p.1–5, p.7 |
| Panasonic TQ2-L; Coto 9900 | not obtained (Panasonic site reset the connection; Coto URLs 404) | | | | | | | | | | | |

No obtained relay data sheet gives a thermal-EMF figure. That number has to come from the manufacturers on request, or from a measurement.

---

## D. Low-noise regulators

| Part | Polarity | V_IN max (rec.; abs) | I_OUT max | Dropout | Noise density at 10 Hz / 1 kHz / 100 kHz | Integrated noise, 10 Hz–100 kHz | PSRR at 1 kHz / 100 kHz / 1 MHz / 10 MHz | SPICE model | Source |
|---|---|---|---|---|---|---|---|---|---|
| **TPS7A4700/4701** | + | 35 V; 36 V abs; V_OUT 1.4–20.5 V (ANY-OUT) or 1.4–34 V (adjustable, 4701) | 1 A | 307/450 mV at 1 A; 216 mV at 0.5 A | ~2.4 / ~0.056 / ~0.012 µV/√Hz (V_OUT = 15 V, 0.5 A, C_NR = 1 µF, C_OUT = 50 µF; the 100 kHz value is at the plot floor) | 4.17 µV_RMS (V_O = 1.4 V); 4.67 µV_RMS (V_O = 5 V); 12.28 µV_RMS at V_OUT = 15 V (Fig 5-1 legend) | Table: 78 dB at 1 kHz (16 V in, 15 V out, 0.5 A). Plot (15 V, 0.5 A): ~78 / ~64 / ~45 / ~57 dB. The 1 MHz value sits next to a ~30 dB notch near 0.8 MHz. At 1 A: ~76 / ~65 / ~46 / ~57 dB | Y: unencrypted PSpice transient (SBVM939); noise not modelled | TI_tps7a47_datasheet.pdf (SBVS204G): p.1, p.4–7 §5.1–5.5, Fig 5-1; p.9 Fig 5-17, 5-18 |
| **TPS7A3301** | − | −35 V; −36 V abs; V_OUT −1.18 to −33 V | 1 A | 290 mV at 0.5 A; 325/800 mV at 1 A | ~1.0–1.2 / ~0.1 / ~0.024 µV/√Hz (V_OUT = −15 V, 1 A, C_FF = 10 nF, C_OUT = 20 µF) | 16 µV_RMS (V_OUT = V_REF, table); 17.6 µV_RMS at −15 V (Fig 34) | Table: 72 dB at 10 kHz only. Plot (−15 V, 1 A): ~64 / ~55 / ~42 / ~9 dB | Y: unencrypted PSpice (SBVM665); very simple, no noise or PSRR(f) | TI_tps7a33_datasheet.pdf (SBVS169D): p.5–6 §6.1–6.5; p.10 Fig 22; p.19 Fig 33, 34 |
| **TPS7A94** | + (low voltage) | 5.7 V; 6.0 V abs. **Not for ±15 V rails** | 1 A | 150/240 mV at 1 A | Table (1.2 V out): 6.6 nV/√Hz at 100 Hz, 1.3 nV/√Hz at 1 kHz. Plot (5 V out, 1 A): ~270 / ~1.6 / ~1.7 nV/√Hz | 0.46 µV_RMS (1.2 V, 1 A); 0.63–0.84 µV_RMS at 5 V | Table: 51 dB at 1 MHz (3.3 V, 750 mA). Plot (5 V, 1 A): ~105 / ~63 / ~49 / ~30 dB. At 100 mA: ~108 / ~81 / ~51 / ~46 dB | Y: PSpice transient (SBVM988A; noise not modelled) | TI_tps7a94_datasheet.pdf (SBVS336C): p.1, p.4–8 §6.1–6.5, Fig 6-4; p.10 Fig 6-18 |
| LT3045, LT3045-1, LT3094, LT3042, LT3093, ADM7150, ADM7151 | | not obtained (www.analog.com blocked) | | | | | | Expected to be LTspice-only for the LT parts; **not verified** | |

---

## Selection notes (from the values above only)

These notes cover only the parts obtained in this session.

**(i) ±15 V unity-gain-stable difference amplifier, ≥ 300 V/µs and ≤ 3 nV/√Hz**
- No obtained voltage-feedback part meets both limits. THS4031 is 1.2 nV/√Hz but 100 V/µs. LM7171 is 4100 V/µs but 8.5–14 nV/√Hz and needs a noise gain of at least 2. THS4631 is 7 nV/√Hz.
- THS3091 and THS3001 (CFAs) meet the e_n and SR figures. In a unity-gain difference amplifier, however, R_F is fixed at 1–1.8 kΩ, and the inverting-input current noise times R_F dominates: 14 pA/√Hz × 1.78 kΩ ≈ 25 nV/√Hz for the THS3091, and 16 pA/√Hz × 1 kΩ ≈ 16 nV/√Hz for the THS3001, both output-referred. So the in-circuit noise is well above 3 nV/√Hz.

**(ii) ±15 V gain-of-10 stage with ≥ 100 MHz GBW**
- **THS3091.** 190 MHz at G = 10 with R_F = 866 Ω. Its inverting i_n × R_F ≈ 12 nV/√Hz output-referred, which is ≈ 1.2 nV/√Hz input-referred at G = 10. It is a CFA, so DC precision is poor (V_OS 3 mV max, 19 µV/°C).
- **THS4631.** 210 MHz GBW gives 25 MHz at G = 10. JFET input with 7 nV/√Hz.
- **THS4031.** 120 MHz UGBW gives roughly 10–12 MHz closed-loop at G = 10 (approximately UGBW/10). 1.2 nV/√Hz, which is marginal for 10 MHz flatness.

**(iii) 50 Ω output driver, 10 Vpp at 10 MHz**
- Requirements: 10 Vpp at the amplifier into 50 Ω + 50 Ω needs ±50 mA and ≥ 314 V/µs. 10 Vpp at the load needs 20 Vpp at the amplifier, ±100 mA and ≥ 628 V/µs.
- **THS3091.** 310 mA, ±12.5 V into 100 Ω, 3600–6000 V/µs. HD2/HD3 is −72/−70 dBc at 10 MHz, 2 Vpp, 100 Ω.
- **THS3001.** 120 mA, ±12.8 V into 150 Ω, 6300 V/µs.
- **BUF634A** in wide-BW mode inside an op-amp loop. 250 mA continuous, 3750 V/µs, 200 MHz. Open-loop HD at 1 MHz, 10 Vpp, 100 Ω is −64/−60 dBc, which the loop must correct.

**Switch for 10 MHz paths**
- **TMUX6136** at high-impedance nodes: 2.4/5.5 pF; −85 dB isolation at 1 MHz and ~−63 dB at 10 MHz.
- **TMUX7219/TMUX6219** only where the low R_ON is essential and the 148 pF on-capacitance can be tolerated.
