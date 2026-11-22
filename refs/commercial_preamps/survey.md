# Commercial low-noise voltage preamplifiers and differential amplifiers: benchmark survey

Access date for all sources: 2026-11-19. Purpose: benchmark data for a DC–10 MHz differential voltage preamplifier intended to beat the SRS SR560 (4 nV/√Hz, 100 MΩ ∥ 25 pF, DC–1 MHz), with a high-impedance front end (about 20–40 pF) and a paralleled-JFET low-noise front end.

Conventions

- $e_n$ is the input-referred voltage noise density, $i_n$ the input current noise density. "typ" and "max" are as printed by the maker.
- File paths are relative to this folder (`refs/commercial_preamps/`). "PDF p. N" is the 1-based page index in the PDF file; the printed page number is given where it differs.
- "(plot)" marks a value read by eye from a published graph; such values are approximate (about ±20 % on log axes).
- "(derived)" marks a number computed here from published numbers; the formula is given.
- "not given" means the opened document does not state the quantity.
- Prices are list prices printed in the cited document, without date verification.

---

## 1. NF Corporation (Yokohama, Japan; formerly NF Circuit Design Block / エヌエフ回路設計ブロック)

### 1.1 Line-up overview

- Current voltage-input preamplifier line-up (index page): SA series (0.25 nV/√Hz best, up to DC–20 MHz for SA-440F5), CA5360 (DC–1 MHz, 5 nV/√Hz, ×100), LI-75A (DC–1 MHz, 2.5 nV/√Hz, ×100), 5307 differential amplifier (DC–10 MHz, 4 nV/√Hz, ×10 to ×1000 in 1-2-5 steps). Current-input models (SA-600, LI-76, CA5350/CA5351) are outside the scope. — `NF_Corporation/NF_preamplifier_index_EN.html`. Note: the LI-75A noise is given as 2.5 nV/√Hz on this index page but 2 nV/√Hz on the LI-75A specification page and in the 2025 Japanese catalogue (see 1.4).
- Archived 2004 line-up page (Wayback capture 2004-08-24): 5307 "DC to 10MHz, 20 to 60dB, Differential/Single ended, 4nV/√Hz"; BX-31A wide-band preamplifier "DC to 150MHz, 20/40dB, Single ended (50 ohm/1M ohm), 5nV/√Hz"; LI-75A "DC to 1MHz, 40dB, Differential/Single ended, 2nV/√Hz"; SA-200F3 (DC–800 kHz, 0.5 nV/√Hz); SA-400F3 (DC–700 kHz, differential, 0.75 nV/√Hz); SA-220F5 (300 Hz–100 MHz, 0.5 nV/√Hz); SA-230F5 (400 Hz–140 MHz, NF ≤ 0.6 dB); SA-430F5 (400 Hz–110 MHz, differential 50 Ω, NF ≤ 1.1 dB). — `NF_Corporation/NF_preamplifier_lineup_EN_archived_20040824.html`.
- No 1980s-era NF differential amplifier model number other than the 5307 lineage was found in any opened document (see 1.3).

### 1.2 NF 5307 differential amplifier (current product; the only NF DC–10 MHz differential amplifier found)

Primary source: `NF_Corporation/NF_5307_specifications_EN.pdf` (1 page, image-only scan; PDF created 2021-11-08), cross-checked with `NF_Corporation/NF_5307_catalog_JP.pdf` (catalogue "current as of 2025-04-01", PDF p. 2).

- Input configuration: balanced differential A−B on two BNC connectors; single-ended modes A, −B, A−Offset, −B+Offset; GND (input shorted); selectable from the front panel.
- Input impedance: 1 MΩ ±2 % shunted by less than 35 pF; capacitance matching between A and B ±3 pF; 100 MΩ possible by moving an internal shorting plug. The manual gives 33 pF typical input capacitance and the input-RC bandwidth estimate $B_W \approx 160/(R_S\,[\mathrm{k\Omega}] \cdot C_C\,[\mathrm{pF}])$ MHz, with $C_C$ = cable + input capacitance (example: 500 Ω source and 1 m RG-58C/U gives about 2.41 MHz). — `NF_Corporation/NF_5307_instruction_manual_EN.pdf`, PDF p. 21 (printed p. 11).
- Input bias current: 3 nA typ (23 °C), doubling every 10 °C increase (the doubling law is characteristic of JFET gate leakage).
- Input device: FET. NF's own comparison charts (dated "UPDATE: November 29, 2018") mark the 5307 with the "FET" symbol (legend: Input Device (transistor) Bipolar / FET, all differential). — `NF_Corporation/NF_technical_note_preamp_fig01_noise_vs_cutoff.png`, `NF_Corporation/NF_technical_note_preamp_fig02_noise_vs_input_impedance.png` (figures of `NF_technical_note_preamp_EN.html`, posted 2020-03-11).
- Maximum allowable input: ±50 V (input protector operates at ±10.5 V and recovers automatically about 5 s after the overvoltage is removed). Common-mode input range: ±10 V (linear).
- CMRR: ≥120 dB, DC–1 kHz (gain 1000, common-mode voltage ±5 V). CMRR vs frequency (plot, datasheet figure `NF_Corporation/NF_5307_datasheet_fig46.jpg`; read by eye, then checked on 2026-11-22 against the image's pixels by `../../scripts/nf5307_plot_check.py`, results in `../../sim/results/nf5307_plot_check.json`): gain 100×1 about 136 dB at 10 Hz, 135 dB at 100 Hz, 135–136 dB at 1 kHz, 126 dB at 10 kHz, 120 dB at 20 kHz, 107 dB at 100 kHz, 100 dB at 200 kHz and 85 dB at 1 MHz; gain 10×1 about 126 dB at 10 Hz, 120 dB at 100 Hz, 107 dB at 1 kHz, 97 dB at 3 kHz, 76 dB at 30 kHz and 48 dB at 1 MHz. The curves stop at about 0.9 MHz, short of the 1 MHz grid line, so the 1 MHz values are straight-line extrapolations of their last 0.4 decade. (The first reading by eye, corrected here, gave 118 dB at 20 kHz and 86 dB at 1 MHz for gain 100, and 100 dB at 3 kHz, 80 dB at 30 kHz and 50 dB at 1 MHz for gain 10.)
- $e_n$ (spec): 4 nV/√Hz typ at 1 kHz, input short-circuited, gain 1000.
- $e_n$ (manual plot, Fig. 4.7, "Measured by LI-575 [lock-in amplifier], short by set input panel switch"; "equivalent input noise does not vary in the ×1 and ×10 mode"): gain 100×1 about 2.8–3.1 nV/√Hz flat from about 100 Hz to 100 kHz, 5.6–5.9 nV/√Hz at 10 Hz, 33–35 nV/√Hz at 1 Hz; gain 10×1 about 15–16 nV/√Hz white (plot). The plot's axes are not drawn on a uniform log scale (its minor ticks sit up to about 0.04 decade from where a log scale between the decade lines puts them), so each range spans the reading against the printed ticks and on a uniform scale between the decade lines (`../../scripts/nf5307_plot_check.py`, 2026-11-22; the first reading by eye, corrected here, gave 2.5–3 nV/√Hz flat and about 4 nV/√Hz at 10 Hz). — `NF_Corporation/NF_5307_instruction_manual_EN.pdf`, PDF p. 37 (printed p. 25).
- Output noise: 20 mVrms max, input short-circuited, gain 1000, 10 MHz bandwidth, 50 Ω load. Equivalent average input noise over 10 MHz: $20\,\mathrm{mV}/1000/\sqrt{10^7\,\mathrm{Hz}} \approx 6.3$ nV/√Hz (derived, upper bound).
- Gain: 10 to 1000 (with 50 Ω load) in 1-2-5 sequence; realised as a first stage of 10/20/50/100 followed by ×1 or ×10 (datasheet figure labels "10 x1 time" … "100 x10 times"). Gain accuracy ±3 % (1 kHz, $R_L \ge$ 1 MΩ); gain stability ±200 ppm/°C.
- Bandwidth: DC–10 MHz, +0.2/−3 dB ($R_L$ = 50 Ω, $V_o$ = ±1 V), at all gains; plots show the −3 dB point at roughly 15–20 MHz for both ×1 and ×10 settings (`NF_5307_datasheet_fig41.jpg`, `fig42.jpg`). Full-power bandwidth DC–3 MHz (±5 V into 50 Ω).
- Filter: band-limiting low-pass 1 MHz ±10 % (−3 dB), −18 dB/oct, phase-linear, on/off from the front panel. No high-pass filter; DC offset cancellation up to ±5 V (referred to input, single-ended use), offset cancellation ranges ±0.5 V / ±5 V.
- Output: single-ended BNC, 50 Ω ±2 %; rated ±5 V into 50 Ω, ±10 V into ≥1 MΩ (DC–3 MHz); max ±100 mA; slew rate 150 V/µs (50 Ω), 300 V/µs (1 MΩ); distortion 0.02 % max (1 kHz, 50 Ω, ±5 V, gain 10); settling 300 ns typ (5 V step, 1 %); propagation delay 55 ns typ (filter off).
- Overload: overload reset time 10 µs max (gain 10–100, ×1), 50 µs max (×10), after a ±5 V, 10 ms input; overvoltage detection ±5 V at the output.
- DC: offset adjustable to zero (±0.5 mV RTI range); offset stability ±8 µV/°C typ RTI (gain 1000).
- Power: AC line 100/120/220/240 V, 30 VA; not battery-powered. 215 × 88 × 350 mm, 4.5 kg.
- Year: the Japanese instruction manual carries "Copyright 1998-2016, NF Corporation" (`NF_Corporation/NF_5307_instruction_manual_JP.pdf`, PDF p. 73); the 5307 is in the archived 2004 line-up. No earlier date was found. The English manual PDF is a scan created 2005-11-11.
- Price: not given in the opened NF documents (reseller prices appeared only in search-result snippets and were not verified).
- Status: current (listed on the NF index page and in the 2025 catalogue).

### 1.3 The remembered 1980s DC–10 MHz differential amplifier with Toshiba 2SK389: search result

Not found. What was established:

- No opened NF document (current English/Japanese product pages, 2004 archived line-up and SA pages, 2008 and 2026 SA catalogues, 5307 manuals and catalogues, technical notes) names any DC–10 MHz differential amplifier other than the 5307, and none names the 2SK389 or any input transistor type.
- The 5307 matches every remembered attribute except the date: DC–10 MHz, differential, FET input (NF's own chart), JFET-like bias current (3 nA typ doubling every 10 °C), spec 4 nV/√Hz with NF's own published curve at about 3 nV/√Hz (2.8–3.1, gain 100). The earliest date found for it is the 1998 manual copyright. It is therefore possible that the remembered unit is the 5307 itself (late 1990s rather than 1980s), or an undocumented predecessor; nothing found distinguishes the two.
- The 5307 figures (JFET-like bias current of 3 nA typ, about 3 nV/√Hz) are compatible with a dual-JFET differential input stage of the 2SK389 class, but no document confirms the device type, the number of JFETs in parallel, or the drain current.
- Searches without result: model numbers 5302/5303/5304/5305/5306 (English and Japanese), "2SK389" with エヌエフ / NF回路, Transistor Gijutsu / CQ articles on 2SK389 differential measurement amplifiers, patents assigned to NF Corporation on paralleled-FET input stages, Japanese auction/used listings, Wayback Machine captures of nfcorp.co.jp from 1997–2003 (the 1999 catalogue page is image-only; further CDX queries were rate-limited by the archive).
- A reseller listing (valuetronics.com product record for "P-61 NF Corporation Differential Amplifier", read online, not saved) shows an NF "P-61" differential amplifier: balanced differential, 100 MΩ, gain 1–1000 in 1-2-5 steps, CMRR ≥120 dB (DC–120 Hz), frequency response ±0.1 dB DC–10 kHz and +0.5/−3 dB DC–100 kHz. It is a low-bandwidth DC amplifier, not the 10 MHz unit; no NF document for it was found.

### 1.4 NF LI-75A low-noise preamplifier (lock-in companion; current)

Sources: `NF_Corporation/NF_LI-75A_specifications_EN.html`; `NF_Corporation/NF_LI-75A_catalog_JP.pdf` (catalogue current as of 2025-04-01), PDF p. 2; `NF_Corporation/NF_LI-75A_EN_archived_20040824.html`.

- Input: balanced; AC/DC coupling switchable; differential / single-ended grounded / floating (JP catalogue).
- Input impedance: 100 MΩ ∥ 50 pF (EN page; JP catalogue "100 MΩ, ≤50 pF in parallel"; AC coupling capacitor 0.016 µF).
- CMRR: 120 dB (DC–100 Hz). Common-mode range ±5 V (JP catalogue).
- $e_n$: 2 nV/√Hz at 1 kHz, input shorted (EN spec page, 2004 page, 2025 JP catalogue); 2.5 nV/√Hz on the current index page. Offset drift 10 µV/°C.
- Gain: ×100 (40 dB) ±1 % (400 Hz), fixed.
- Bandwidth: DC–1 MHz (DC coupling), 0.2 Hz–1 MHz (AC coupling).
- Output: ±10 V into 2 kΩ (DC–200 kHz); output impedance about 50 Ω. THD ≤0.03 % (1 kHz, 5 Vrms out) (JP catalogue).
- Power: from the NF lock-in amplifier (LI5640, LI5630, 5610B) or the PS-70A supply; 1.15 kg.
- Input device: FET (NF technical-note charts).
- Year: not given (described as "one of the best-selling items over the years", `NF_technical_note_preamp_EN.html`). Status: current.

### 1.5 NF CA5360 low-noise preamplifier (current)

Source: `NF_Corporation/NF_CA5360_specifications_EN.pdf` (PDF created 2017-08-24), p. 1.

- Input: AC/DC, BNC; A−B balanced, A (float) or A (GND) unbalanced; 100 MΩ nominal ∥ ≤50 pF (A and B); common-mode range ±5 V (DC–100 Hz); CMRR ≥100 dB (DC–100 Hz).
- $e_n$ ≤5 nV/√Hz at 1 kHz, input short (with LP5390-series supply). Offset adjustable ±10 mV, 10 µV/°C.
- Gain ×100 (40 dB) ±1 %; DC–1 MHz (DC), 0.2 Hz–1 MHz (AC), +1/−3 dB; THD ≤0.03 % (1 kHz).
- Output ±5 V into ≥2 kΩ (DC–500 kHz), 50 Ω. Power ±15/±20/±24 V ±5 %, ±50 mA (from NF lock-ins or LP539x supplies). Input device FET (technical-note charts).

### 1.6 NF SA-200 series (single-ended) and SA-400 series (differential) low-noise amplifiers

Sources: 2026 catalogue `NF_Corporation/NF_SA_series_en_sa_series.pdf` ("current as of July 9th, 2026", PDF p. 7), specification tables PDF p. 4, noise plots and source-resistance charts PDF p. 3; summary sheet `NF_Corporation/NF_SA_series_specifications_en.pdf`; 2008 catalogue `NF_Corporation/NF_SA_series_catalog_e_SA.pdf` (PDF created 2008-03-10, modified 2012-11-14), PDF p. 2 for SA-400F3 and SA-230F5; selection guide `NF_Corporation/NF_SA-200_special_order_EN.html`. All at ±15 V, 23 °C unless noted; all external-supply modules (NF LP5393/LP5394 low-noise supplies recommended), SMA connectors.

| Model | Band | Input | $Z_{in}$ ∥ $C_{in}$ | CMRR | $e_n$ | $i_n$ | Gain | Output |
|---|---|---|---|---|---|---|---|---|
| SA-200F3 | DC–800 kHz | SE, DC, bipolar | 1k/10k/100 kΩ ∥ ≤150 pF | — | 0.7 max / 0.5 typ (1 kHz) | 2.2 pA (10 kHz) | 40 dB | ±10 V into 1 kΩ |
| SA-220F5 | 1 kHz–80 MHz | SE, AC, FET | 1 MΩ ∥ 57 pF | — | 0.7 max (100 kHz) / 0.5 typ (10 kHz–1 MHz) | 200 fA (100 kHz) | 46 dB | 2 Vpp into 50 Ω |
| SA-230F5 (2008 cat.) | 1 kHz–100 MHz | SE, AC, bipolar | 50 Ω | — | 0.35 max (100 kHz) / 0.25 typ | 5 pA | 46 dB | 2 Vpp / 50 Ω; NF 0.6 dB typ (10 MHz) |
| SA-240F5 | DC–20 MHz | SE, DC, FET | 1 MΩ / 100 MΩ / open ∥ 60 pF | — | 1.2 (1 kHz) | 5 fA (100 Hz) | 40 dB | ±10 V into 1 kΩ |
| SA-250F6 / SA-251F6 | 100 Hz–250 MHz / 1 kHz–500 MHz | SE, AC | 50 Ω | — | 0.25 max (1 MHz) | 5 / 8 pA | 40 dB | 2 Vpp; NF 0.6 / 0.9 dB (10 MHz) |
| SA-400F3 (2008 cat.) | DC–600 kHz | diff, DC, bipolar | 1k/10k/100 kΩ ∥ 80 pF | 110 dB min, 120 typ (50 Hz); 80 typ (100 kHz) | 0.9 max / 0.75 typ (1 kHz) | 3.0 pA (10 kHz) | 40 dB | ±10 V / 1 kΩ |
| SA-410F3 | DC–1 MHz | diff, DC, bipolar | 1k/10k/100 kΩ ∥ 100 pF | ≥110 dB (55 Hz); 80 dB typ (100 kHz) | 0.75 typ (1 kHz) | 4.5 pA (10 kHz) | 40 dB | ±10 V / 1 kΩ |
| SA-420F5 | 1 kHz–70 MHz | diff, AC, FET | 1 MΩ ∥ 15 pF | ≥55 dB (1 kHz–10 MHz) | 1.2 max (100 kHz) / 0.9 typ (100 kHz–10 MHz) | 100 fA (1 kHz) | 46 dB | 2 Vpp / 50 Ω |
| SA-421F5 | 30 Hz–30 MHz | diff, AC, FET | 1 MΩ ∥ 85 pF | ≥46 dB (1 kHz–10 MHz) | 0.7 max (100 kHz) / 0.5 typ (100 kHz–10 MHz) | 100 fA (100 Hz) | 46 dB | 2 Vpp / 50 Ω |
| SA-440F5 | DC–20 MHz | diff, DC, FET | 1 MΩ / 100 MΩ / open ∥ 60 pF | 90 dB (10 Hz–10 kHz), 60 dB (1 MHz) | 1.8 (1 kHz) | 25 fA (100 Hz) | 40 dB | ±10 V / 1 kΩ |
| SA-430F5 | 1 kHz–100 MHz | diff, AC, bipolar | 50 Ω | ≥80 dB (100 kHz); 90 typ (100 kHz), 80 typ (10 MHz) | 0.45 max (100 kHz) / 0.35 typ | 7 pA | 46 dB | 2 Vpp / 50 Ω; NF 1.10 dB typ (10 MHz) |

Further SA details:

- Maximum input (non-destructive): SA-200F3 ±0.5 V; SA-220F5/SA-240F5 ±1 V; SA-410F3 differential ±1 V, common-mode ±15 V; SA-440F5 differential ±1 V, common-mode ±7.5 V; SA-420F5/SA-421F5 differential ±10 V DC or 4 Vpp AC, common-mode ±10 V DC or 6 Vpp AC (2026 catalogue, PDF p. 4).
- Noise plots (2026 catalogue PDF p. 3, plot): SA-440F5 about 2 nV/√Hz at 100 Hz, about 1.6 nV/√Hz from 10 kHz to 300 kHz, about 2 nV/√Hz at 10 MHz; SA-240F5 about 1.5 nV/√Hz at 100 Hz, about 1.2 nV/√Hz flat with a bump to about 1.7 nV/√Hz near 2 MHz; SA-410F3 about 0.8 nV/√Hz from 100 Hz to 300 kHz, about 1.1 nV/√Hz at 1 MHz; SA-200F3 about 1.2 nV/√Hz at 1 Hz, about 0.6 nV/√Hz at 10 Hz, 0.5 nV/√Hz at 1 kHz, rising to about 2.3 nV/√Hz at 1 MHz.
- Customisation (selection guide page): SA-240F5 DC–20 MHz can be extended to DC–40 MHz; SA-220F5 to 1 kHz–130 MHz; SA-230F5 to 1 kHz–110 MHz; reduced overload recovery for MRI/NMR.
- Year: SA-200F3, SA-220F5, SA-230F5, SA-400F3, SA-430F5 are in the 2004 archived pages (`NF_SA_series_EN_archived_20040824.html`); introduction years not given.

### 1.7 NF design approach (documented)

- SA series: "a proprietary circuit configuration using negative feedback technology" (2008 catalogue, PDF p. 2).
- SA-230F5/SA-430F5 technical note (`NF_Corporation/NF_SA_series_technical_info.pdf`, PDF created 2017-03-23, pp. 1–2): bipolar input transistor without emitter degeneration resistor (to avoid its noise); collector current set by a DC servo (differential integrator) so $I_C = V_{REF}/R_C$; since $g_m = qI_C/kT$, the gain $A = g_m R_C = qV_{REF}/kT$ is made temperature-independent by making $V_{REF} \propto T$; 50 Ω input match by "active input impedance" $Z_{in} = R_f/(1+A)$ (feedback termination), which keeps the noise figure well below the 3 dB of a resistive termination (SA-230F5 NF about 0.6 dB, plotted 10–110 MHz).
- Bipolar vs FET by source resistance (2026 catalogue PDF p. 3, Fig. 1 and Fig. 2; plot): single-ended SA-200F3 (bipolar) about 0.5 nV/√Hz up to about 100 Ω source resistance, crossing the flat SA-240F5 (FET, about 1.2 nV/√Hz to about 100 kΩ) at about 600 Ω; differential SA-410F3 (bipolar, about 0.75 nV/√Hz) crosses SA-440F5 (FET, about 1.8 nV/√Hz) at about 400 Ω. NF's text: "For low signal source resistances, the bipolar input has a better noise characteristic. On the other hand, the FET input's characteristic is stable over a wide range."
- Technical note "Preamplifier" (`NF_Corporation/NF_technical_note_preamp_EN.html`, posted 2020-03-11): NF positions its preamplifiers as wide-band and low-noise (to be followed by a band-limiting filter), and gives two charts of $e_n$ versus cut-off frequency and versus input impedance for NF and anonymised competitors (Companies A–G), with input device type marked.
- 5307 manual (PDF p. 21): stresses balancing source impedance and cable capacitance between A and B to keep CMRR, and the input-RC bandwidth limit (formula in 1.2).
- No NF document found describes paralleled JFET input stages, JFET count, or drain currents for any model.

---

## 2. Stanford Research Systems (SRS)

### 2.1 SR560 low-noise voltage preamplifier (benchmark; data sheet only)

Source: `../benchmark/SRS_SR560_datasheet.pdf` (file held in `refs/benchmark/`, not duplicated here), PDF p. 3.

- Inputs: AC or DC coupled, single-ended or differential; 100 MΩ + 25 pF; maximum input 3 Vpp.
- CMRR: 100 dB from DC to 1 kHz (100 mV common-mode input at 1 kHz, gain 100, low-noise mode), decreasing 6 dB/oct from 1 kHz to 1 MHz.
- $e_n$: 4 nV/√Hz at 1 kHz. Short-circuit noise plot (plot): about 12 nV/√Hz at 10 Hz, about 5 nV/√Hz at 100 Hz, about 4 nV/√Hz above 1 kHz. Noise-figure contours given for 1 Ω–100 MΩ sources.
- Gain 1 to 50,000 in 1-2-5 sequence, vernier in 0.5 % steps; gain stability 200 ppm/°C.
- Bandwidth: −3 dB at 1.2 MHz (typ); flatness ±0.3 dB to 300 kHz (gains up to 1000).
- Filters: two configurable 6 dB/oct low-pass or high-pass filters, −3 dB points 0.03 Hz–1 MHz in 1-3-10 sequence; gain allocation "High Dynamic Reserve" or "Low Noise".
- Output: 10 Vpp into 50 Ω and 600 Ω. DC drift 5 µV/°C RTI (DC coupled). Distortion 0.01 % at 1 kHz.
- Power: 100/120/220/240 VAC, or internal batteries giving 15 h. Price USD 3,095 (O560SB spare battery set USD 200).

### 2.2 SR550, SR551, SR552 lock-in preamplifiers

Source: `SRS/SRS_SR550_SR551_SR552_manual.pdf` ("Revision 2.7 (Jan 2017)", PDF p. 1) and `SRS/SRS_SR552_datasheet.pdf`.

- SR550 (FET, PDF p. 4): 100 MΩ + 25 pF; single-ended or differential; overload 250 mV rms; $e_n$ 3.6 nV/√Hz at 1 kHz, 4.0 at 100 Hz, 13 at 10 Hz (typ); common-mode range 1 V peak, CMRR 90 dB at 100 Hz (typical CMRR curve PDF p. 6: about 100 dB at 100–300 Hz, about 55 dB at 100 kHz, plot); gain 1, 2, 5, 10; gain accuracy 2 % (2 Hz–100 kHz); output 600 Ω, 7 Vpp; powered by the lock-in.
- SR550 input stage (schematic PDF p. 10, "SR550 Low Noise Preamp", original drawing dated Jan 9, 1985): a single 2N5564 matched dual JFET (Q1A/Q1B) long-tailed pair with 106 Ω source resistors, followed by an LT1007; inputs AC-coupled through 0.1 µF with 100 MΩ bias resistors.
- SR551 (PDF p. 13): >1 TΩ + 7 pF; ×10; 1 MHz (−3 dB); $I_b$ <1 pA; $e_n$ 12 nV/√Hz at 1 kHz; $i_n$ 0.6 fA/√Hz; CMRR <−90 dB at 1 kHz; common-mode −4 to +4 V; output 8 Vp balanced differential, 50 Ω; ±20 V from lock-in.
- SR552 (bipolar; datasheet p. 1 and manual PDF p. 18): 100 kΩ + 25 pF; single-ended or differential; overload 70 mV rms, damage 50 VDC/20 VAC; $e_n$ 1.4 nV/√Hz at 1 kHz, 1.6 at 100 Hz, 2.5 at 10 Hz (typ); AC coupled (0.016 Hz); CMRR 100 dB at 100 Hz (1 V input); gain 10, 20, 50, 100; gain accuracy 2 % (2 Hz–100 kHz); −3 dB bandwidth not given; output 600 Ω, 10 Vpp; powered from SRS lock-ins or ±20 VDC, +5 VDC; price USD 750. Status: product page live on thinksrs.com on the access date (`SRS/SRS_SR552_product_page.html`).

### 2.3 SR554 transformer preamplifier

Source: `SRS/SRS_SR554_datasheet.pdf`, pp. 1–2.

- Single-ended or differential; $e_n$ 0.1 nV/√Hz; recommended source 0.05 Ω–1 kΩ; CMRR >120 dB below 1 kHz; primary can float to ±100 VDC.
- Gain 100× (transformer only, passive) or 500× (transformer and buffer); 0.1 Hz–40 kHz; isolation >40 dB DC–500 MHz.
- Output single-ended or differential; 100 Vpp (transformer only) or 20 Vpp (with buffer); output impedance >5 kΩ (transformer only), <1 Ω (buffer).
- Power from SRS lock-ins or external ±20 VDC. Price USD 2,695 (U.S. list).

### 2.4 SR555, SR556

Current preamplifiers (SR555 "10 V/µA fixed gain, 120 kHz bandwidth"; SR556 "1 V/nA fixed gain, 5 fA/√Hz input noise"), not voltage-mode, so excluded. — `SRS/SRS_SR555_datasheet.pdf` p. 1, `SRS/SRS_SR556_datasheet.pdf` p. 1.

### 2.5 Lock-in amplifier voltage inputs

- SR830 (`SRS/SRS_SR830_datasheet.pdf` p. 3): single-ended or differential; 10 MΩ + 25 pF, AC or DC; $e_n$ 6 nV/√Hz at 1 kHz (typ); CMRR 100 dB to 10 kHz, decreasing 6 dB/oct above 10 kHz; dynamic reserve >100 dB; reference 1 mHz–102.4 kHz.
- SR860 (`SRS/SRS_SR860_datasheet.pdf` p. 4): single-ended or differential; 10 MΩ + 25 pF; voltage input range 10 mV–1 V (peak); $e_n$ 2.5 nV/√Hz at 1 kHz (10 mV input range, typ); CMRR 90 dB to 1 kHz (DC coupled, 10–100 mV ranges); dynamic reserve 120 dB; reference 1 mHz–500 kHz.
- SR865A (`SRS/SRS_SR865A_datasheet.pdf` p. 4): as SR860, with reference to 4 MHz and gain accuracy ±2 % to 4 MHz.

---

## 3. FEMTO Messtechnik (Berlin)

All models: external ±15 V supply (LEMO), BNC signal connectors, test conditions ±15 V, 25 °C, unless noted. Current data sheets downloaded from femto.de; revision codes from the page footers.

### 3.1 DLPVA series (DC–100 kHz / DC–500 kHz variable gain)

- DLPVA-101-B (current; `FEMTO/FEMTO_DLPVA-101-B_datasheet.pdf`, footer "DLPVA-101-B_R01T1/TH,UH,MW/27FEB2024", pp. 2–4): versions -B-S (single-ended, BNC) and -B-D (true differential, LEMO 1S); bipolar input, recommended source <1 kΩ (-S) or <10 kΩ (-D); gain 20/40/60/80 dB ±0.05 dB; DC or 1.5 Hz lower cut-off; upper −3 dB 100 kHz or 1 kHz, 12 dB/oct, independent of gain; $Z_{in}$ 1 MΩ ∥ 105 pF; $e_n$ at 40/60/80 dB 2.0 nV/√Hz (-S), 3.0 nV/√Hz (-D), at 20 dB 5.0 nV/√Hz (both); $i_n$ 2 pA/√Hz; 1/f corner 80 Hz; $I_b$ 0.8 µA; (-D) common-mode range ±8 V, CMRR 120 dB at 100 Hz, 100 dB at 10 kHz, 80 dB at 60 kHz; output ±10 V into ≥100 kΩ, 50 Ω; overload recovery 0.5 ms after 20× overload; abs. max input ±4.5 V (-S), differential ±3 V and common-mode ±9 V (-D); ±75 mA typ.
- DLPVA-100-B (predecessor; `FEMTO/FEMTO_DLPVA-100-B_datasheet_archived2023.pdf`, footer "DE-DLPVA-100-B_R7/MvB,JM,TB/06JUN18", p. 2): same structure; $Z_{in}$ 1 MΩ, $C_{in}$ 105 pF; $e_n$ at 60/80 dB 2.4 (-S) / 3.6 (-D), 40 dB 6.4 / 7.3, 20 dB 60 / 60 nV/√Hz; CMRR as -101; output <100 Ω.
- DLPVA-101-F (current; `FEMTO/FEMTO_DLPVA-101-F_datasheet.pdf`, footer "DLPVA-101-F_R03/TH/04NOV2025", pp. 3–4): FET input; $Z_{in}$ 1 TΩ ∥ 18 pF; $e_n$ at 40/60/80 dB 5.0 (-S) / 6.5 (-D), at 20 dB 6.5 / 7.5 nV/√Hz; $i_n$ 1.6 fA/√Hz; 1/f corner 80 Hz; $I_b$ 3 pA typ; CMRR (-D) 120 dB at 100 Hz, 100 dB at 10 kHz, 80 dB at 60 kHz; recommended source <100 MΩ; abs. max ±15 V, transient ±3 kV (5 nF source); DC–100 kHz / 1 kHz.
- DLPVA-100-F (predecessor; `FEMTO/FEMTO_DLPVA-100-F_datasheet_archived2023.pdf`, footer "DE-DLPVA-100-F_R6/MvB,JM,TB/30MAY18", p. 2): 1 TΩ, 18 pF; $e_n$ 60/80 dB 5.5 (-S) / 6.9 (-D), 40 dB 8 / 10 nV/√Hz.
- DLPVA-500-B and DLPVA-500-F (`FEMTO/FEMTO_DLPVA-500-B_datasheet.pdf` footer "DLPVA-500-B_R1/TH/04AUG2026"; `FEMTO/FEMTO_DLPVA-500-F_datasheet.pdf` footer "DLPVA-500-F_R1/TH/04AUG2026"; p. 3): as DLPVA-101-B/-F but upper cut-off 500 kHz (or 1 kHz), rise time 0.7 µs; same noise (B: 2.0/3.0 nV/√Hz; F: 5.0/6.5 nV/√Hz), same $Z_{in}$ (1 MΩ ∥ 105 pF; 1 TΩ ∥ 18 pF), same CMRR figures.
- DLPVA-101-BLN-S (current; `FEMTO/FEMTO_DLPVA-101-BLN-S_datasheet.pdf`, footer "DLPVA-101-BLN-S_R01T1/TH,UH/19FEB2024", pp. 3–4): single-ended, bipolar low-noise; gain 40/60/80/100 dB; DC/1.5 Hz to 100 kHz/1 kHz; $Z_{in}$ 1 MΩ ∥ 13 pF; $e_n$ 0.8 nV/√Hz (40 dB), 0.7 nV/√Hz (60–100 dB); $i_n$ 3 pA/√Hz; 1/f corner 80 Hz; $I_b$ 1 µA; use source <100 Ω; abs. max input ±0.7 V.
- DLPVA-500-BLN-S (`FEMTO/FEMTO_DLPVA-500-BLN-S_datasheet.pdf`, footer "DLPVA-500-BLN-S_R01/TH/04AUG2026", p. 3): as -101-BLN-S, upper cut-off 450 kHz; 1 MΩ ∥ 13 pF; 0.8/0.7 nV/√Hz; 1/f corner 100 Hz.
- DLPVA-100-BLN-S (predecessor; `FEMTO/FEMTO_DLPVA-100-BLN-S_datasheet_archived2021.pdf`, footer "DE-DLPVA-100-BLN-S_R6/MvB,TH,JM/30MAY2018", p. 2): $e_n$ (100 Hz–100 kHz) 700 pV/√Hz (100 dB), 730 (80 dB), 860 (60 dB), 6 nV/√Hz (40 dB); 1 MΩ, 13 pF.
- DLPVA-100-BUN-S (current; `FEMTO/FEMTO_DLPVA-100-BUN-S_datasheet.pdf`, footer "DE-DLPVA-100-BUN-S_R5/LK,JMi/17OKT2019", p. 2): "ultra-low-noise"; gain 40–100 dB; AC only (1.5 Hz) to 100 kHz; $Z_{in}$ 1 kΩ typ; $e_n$ 400 pV/√Hz (100 dB), 420 pV/√Hz (80 dB), 800 pV/√Hz (60 dB), 6 nV/√Hz (40 dB); $i_n$ 5.5 pA/√Hz; $I_b$ 30 µA; source must be below 200 Ω; abs. max ±4 V.
- History (catalogues): `FEMTO/FEMTO_catalog_2003_archived.pdf` p. 4 lists DLPVA-100 BUN-S 0.4 nV/√Hz (1 kΩ), BLN-S 0.7, B-S 2.4, B-D 3.6 (CMRR 120 dB), F-S 5.0 and F-D 6.9 nV/√Hz (then 100 MΩ input); `FEMTO/FEMTO_amplifier_catalog_2005_archived.pdf` p. 6 lists the F versions at 1 TΩ.

### 3.2 HVA series (fixed/switchable gain, wide band)

- HVA-10M-60-B (`FEMTO/FEMTO_HVA-10M-60-B_datasheet.pdf`, footer "DE-HVA-10M-60-B_R4/JM/25FEB2019", pp. 1–2): gain 40/60 dB; DC or 1 kHz lower cut-off; upper 10 MHz (35 ns rise); $Z_{in}$ 50 Ω ∥ 12 pF; $e_n$ 0.9 nV/√Hz (2 MHz, 60 dB), 1.8 nV/√Hz (2 MHz, 40 dB); integrated 20 µVpp (60 dB); $I_b$ 18 µA; output ±3.5 V into 50 Ω; abs. max input ±5 V; ±70 mA.
- HVA-10M-60-F (`FEMTO/FEMTO_HVA-10M-60-F_datasheet.pdf`, footer "DE-HVA-10M-60-F_R5/JM/25FEB2019"): FET; $Z_{in}$ 1 MΩ ∥ 15 pF; DC or 1 Hz to 10 MHz; $e_n$ 4.7 nV/√Hz (2 MHz); 100 µVpp integrated; $I_b$ 2 pA; ±3.5 V into 50 Ω; transient 200 V (200 pF source).
- HVA-200M-40-B / -F (footers "DE-HVA-200M-40-B_R5…21FEB2019", "HVA-200M-40-F_R5/JM/25FEB2019"): gain 20/40 dB, DC–200 MHz; B: 50 Ω ∥ 12 pF, $e_n$ 1.2 nV/√Hz (50 MHz, 40 dB), 3.5 nV/√Hz (20 dB); F: 1 MΩ ∥ 15 pF, $e_n$ 4.5 nV/√Hz (40 dB), 5.5 nV/√Hz (20 dB); output ±1 V into 50 Ω.
- HVA-500M-20-B ("DE-HVA-500M-20-B_R5/JM/25FEB2019"): 20 dB, DC–500 MHz, 50 Ω ∥ 3 pF, 3.0 nV/√Hz (200 MHz).
- Earlier values (2005 catalogue p. 6): HVA-10M-60-B 0.9, -F 4.7; HVA-200M-40-B 1.0, -F 4.8; HVA-500M-20-B 2.7 nV/√Hz. HVA was not in the 2003 catalogue, so it appeared between 2003 and 2005.

### 3.3 DHPVA (variable gain, DC–100/200 MHz), DUPVA and HSA (AC, GHz), HLVA

- DHPVA-101 (`FEMTO/FEMTO_DHPVA-101_datasheet.pdf`, footer "DE-DHPVA-101_R1/…/15DEC2016", p. 2): gain 10–60 dB in 10 dB steps; DC or 10 Hz lower cut-off; DC–100 MHz switchable to 10 MHz, bandwidth independent of gain; $Z_{in}$ 50 Ω; $e_n$ 2.3 nV/√Hz (30–60 dB); $i_n$ 3.0 pA/√Hz; 1/f corner 20 kHz; output 2 Vpp linear into 50 Ω; abs. max ±5 V; ±120 mA typ. DHPVA-201: same but 200 MHz / 20 MHz.
- DHPVA-100 / -200 (archived; footers "DE-DHPVA-100_20/R 20/MB/11.Oct. 06", "DE-DHPVA-200_20…"): 50 Ω ∥ 5 pF; 2.5 nV/√Hz (30–60 dB); 1/f corner 15 kHz.
- DUPVA-1-70 (`FEMTO/FEMTO_DUPVA-1-70_datasheet.pdf`, footer "DE-DUPVA-1-70_R17/MvB,TH,JMi/23MAR2020", p. 2): gain 30–70 dB; 1 kHz–1.1 GHz; 50 Ω (AC), 100 kΩ (DC); NF 1.9 dB (70 dB); $e_n$ 330 pV/√Hz (70 dB), 400 pV/√Hz (40–60 dB); 1/f corner 20 kHz. DUPVA-1-60: 1 kHz–1.2 GHz, 450–500 pV/√Hz.
- HSA-X/HSA-Y fixed-gain modules (10 kHz–1 to 2.5 GHz, 50 Ω): $e_n$ 310–680 pV/√Hz depending on model (data sheets in `FEMTO/`, footers 2015–2026).
- HLVA-100 (`FEMTO/FEMTO_HLVA-100_datasheet.pdf`, "DE-HLVA-100_R2/JM/03JAN2019"): logarithmic DC–100 MHz, 50 Ω, 2 nV/√Hz.

---

## 4. Signal Recovery / AMETEK (formerly EG&G Princeton Applied Research)

All Signal Recovery preamplifiers below are listed under "Legacy Products" on the AMETEK Scientific Instruments site (archived pages `SignalRecovery_AMETEK/SignalRecovery_5113_legacy_page_archived_20240705.html`, `…5184_…20250701.html`, `…5186_…20250701.html`), i.e. discontinued.

- 5113 low-noise voltage preamplifier (`SignalRecovery_AMETEK/SignalRecovery_5113_datasheet.pdf`, footer "CatIss7Web:0710UK", pp. 2–3; identical figures in `SignalRecovery_5113A_datasheet.pdf` ©2024, p. 3): A or A−B; AC or DC; 10 MΩ or 100 MΩ ∥ 25 pF; max input without damage +10/−9 V (DC); linear common-mode 1 V peak; differential max 1 V–10 mV depending on coarse gain and filter reserve (Table 1); CMRR >120 dB DC–1 kHz, then −6 dB/oct to 1 MHz; $e_n$ "typically 4 nV/√Hz at 1 kHz" with noise contours; gain 5–50,000 (1-2-5) plus fine gain; DC–1 MHz flat mode; one low-pass and one high-pass filter, 0.03 Hz–300 kHz (1-3-10), 6 or 12 dB/oct; output 2 Vpp into 50 Ω, 50 Ω; internal sealed lead-acid batteries, about 30 h, plus external supply PS0108; RS232 control. The optional Model 1900 transformer (×100 or ×1000) gives "a minimum of 0.03 nV/√Hz".
- 5184 ultra-low-noise preamplifier (`SignalRecovery_AMETEK/SignalRecovery_5184_datasheet.pdf`, "CatIss7Web:0710UK", p. 1): AC coupled, pseudo-differential ("asymmetrical differential"); 5 MΩ ∥ 50 pF; 0.5 Hz–1 MHz; CMRR >80 dB (100 Hz–1 kHz); max differential input 10 mV pk-pk, common-mode 300 mV pk-pk; $e_n$ typ 800 pV/√Hz at 1 kHz (noise figure contours); gain ×1000 fixed ±1 %; output 450 Ω, >10 V pk-pk, >22 V/µs; four 9 V alkaline batteries (about 8 h) or ±15/±18 V.
- 5185 wideband preamplifier (`SignalRecovery_AMETEK/SignalRecovery_5185_manual.pdf`, ©2002, PDF p. 11 = printed A-1): single-ended; 50 Ω or 1 MΩ ∥ 25 pF; DC–200 MHz ±1 dB (50 Ω), DC–100 MHz ±1 dB (1 MΩ DC); $e_n$ 10 nV/√Hz (50 Ω input) and 30 nV/√Hz (1 MΩ input) at 10 kHz; gain ×10 or ×100; max input 100 mV pk-pk (×10), 10 mV pk-pk (×100).
- 5186 differential voltage preamplifier (`SignalRecovery_AMETEK/SignalRecovery_5186_datasheet.pdf`, "CatIss7Web:0710UK", p. 1): true differential, AC coupled; 100 MΩ ∥ 20 pF; 0.5 Hz–1 MHz; CMRR >110 dB (×1000, 100 Hz–1 kHz) and >90 dB (×10, ×100), both degrading 6 dB/oct above 1 kHz; max common-mode 5 V pk-pk (×1000); $e_n$ typ 4 nV/√Hz at 1 kHz (×1000), 10 nV/√Hz at 1 kHz (×10 or ×100); gain ×10/×100/×1000; output 450 Ω, >10 V pk-pk; four 9 V batteries (about 12 h) or external.
- 5182 is a current preamplifier (excluded). An EG&G-era 5113 manual copy is stored as `SignalRecovery_AMETEK/EGG_5113_manual_MIT_copy.pdf` (not read).

## 5. PAR / EG&G Princeton Applied Research (classic)

- PAR 113 low-noise preamplifier (`PAR_EGG/PAR_113_specifications_TEC.pdf`, printed pp. I-1, I-2; undated, EG&G PARC era): two inputs with AC/GND/DC switches, single-ended or differential; 100 MΩ ∥ 15 pF (AC, through 0.1 µF), 1 GΩ ∥ 15 pF (DC); max DC common-mode ±10 V, differential ±7.5 V; linear common-mode 1 V rms; differential ±500 mV (gains 10–100), ±50 mV (200–10k); CMRR for gain >200: 120 dB min DC–100 Hz, 100 dB at 1 kHz, 80 dB at 10 kHz, 60 dB at 100 kHz (20 dB less for gain <200); gain ×10 to ×10⁴ (1-2-5), ±2 %; DC–300 kHz; LF roll-off 0.03 Hz–1 kHz, HF 3 Hz–300 kHz, 6 dB/oct; noise specified only as noise figure: 0.3 dB max at 10 Hz with 2 MΩ source, 0.2 dB max at 1 kHz with 1 MΩ source ($e_n$ not given); output 10 V pk-pk, 600 Ω; NiCd batteries about 30 h or line 5 W. For sources <100 Ω the AM-1, AM-2 (1:100) or 190 (1:10:100) transformers are recommended.
- PAR 116 plug-in preamplifier (`PAR_EGG/PAR_116_specifications_TEC.pdf`, catalogue pp. II-26 to II-28, undated): plug-in for Model 124/126 lock-ins and 114; direct mode 100 MΩ SE/DE, transformer mode low-Z SE/DE; bandwidth direct 0.2 Hz–210 kHz; 1 dB noise-figure contour direct 4 kΩ–20 MΩ (1 Hz–210 kHz), transformer 15 mΩ–100 Ω (20 Hz–10 kHz); CMRR direct 120 dB at 60 Hz, transformer 140 dB; price USD 400 (chart).
- EG&G 181 is a current-to-voltage preamplifier (excluded; `PAR_EGG/EGG_PAR_181_specifications_TEC.pdf`).
- PAR 5003 and 5004: not obtained (only reseller index pages without specifications were found).

## 6. Ithaco / DL Instruments 1201

Source: `Ithaco_DL/DL_Ithaco_1201_datasheet_artisan.pdf` (DL Instruments data sheet in an Artisan Technology Group reseller wrapper), PDF pp. 2–10.

- Input: differential or single-ended, AC or DC; >1 GΩ (typ 5 GΩ) DC coupled, 100 MΩ AC coupled; input current <10 pA; max common-mode 10 V pk-pk (200 VDC in AC mode); max differential/single-ended ±750 mV (×10–×100), ±75 mV (×200–×10k).
- CMRR (minimum) for gain >200 / <200: 125/115 dB DC–100 Hz, 105/95 dB at 1 kHz, 85/75 dB at 10 kHz, 65/55 dB at 100 kHz, 55/45 dB at 200 kHz, 50/40 dB at 400 kHz.
- Noise: "less than 15 nV/√Hz at 10 Hz, less than 7 nV/√Hz at 1 kHz; less than 4 fA/√Hz below 100 Hz"; noise figure <0.4 dB at 1 kHz with 1 MΩ source; current-noise plot rising from about 2 fA/√Hz (1 Hz) to about 600 fA/√Hz (700 kHz) (PDF p. 3, plot).
- Gain ×10–×10,000 (1-2-5-10), continuous to ×25,000; DC–400 kHz (−3 dB); high-pass DC or 0.03 Hz–3 kHz, low-pass 3 Hz–300 kHz, 6 dB/oct.
- Outputs 600 Ω (two), Lo-Z (25 mA), unity-gain monitor; line 100–240 VAC 10 W, optional internal NiCd pack (Option 10, >25 h). Status: offered by DL Instruments at the time of the data sheet (date not given).

## 7. Krohn-Hite 7000 / 7008 (current)

Source: `Krohn-Hite/KrohnHite_7000_datasheet.pdf` (footer "7000Data.doc Jul/2024 V1.5"), pp. 1–3; `Krohn-Hite/KrohnHite_7008_datasheet_V21.pdf` (Feb/2014 V2.1) for the 8-channel version.

- FET instrumentation-amplifier front end; single-ended and differential; AC (0.16 Hz) or DC; 1 MΩ ∥ 40 pF (7008: 1 GΩ with option 10); bias 15 pA typ; max input 10 V peak (×1), safe ±30 V.
- CMRR: >90 dB (gain 1) / >105 dB (gain 10–1k) at 50 Hz; >75 / >90 dB at 10 kHz; >60 / >75 dB at 50 kHz; ">100 dB at 1 kHz" headline.
- $e_n$ 7 nV/√Hz typical (×1k, filters off); wideband noise RTI 10 µV rms (×100/×1k, 2 MHz detector), 3.2 µV with 100 kHz filter.
- Gain ×1/×10/×100/×1000; DC–1 MHz; filters 12 dB/oct, 1 kHz high-pass, 100 Hz/3 kHz/30 kHz/100 kHz low-pass; output ±10 V peak, 50 Ω; line powered.

## 8. Tektronix (classic oscilloscope differential amplifiers)

- 7A22 differential amplifier plug-in (`Tektronix/Tektronix_7A22_manual_070-0931-00.pdf`, "First Printing JUL 1969, Revised SEP 1986", PDF pp. 7–9 = printed 1-1 to 1-3): 10 µV/div–10 V/div; DC–1 MHz (within 10 %); HF −3 dB 100 Hz–1 MHz in 9 steps, LF −3 dB 0.1 Hz–10 kHz in 6 steps; 1 MΩ ±1 % ∥ about 47 pF; CMRR ≥100,000:1 DC–100 kHz (10 µV–10 mV/div, DC coupled; plot PDF p. 8); common-mode range ≥±10 V (most sensitive ranges); gate current ±20 pA (25 °C); noise "16 µV or 0.1 div, tangentially measured" (1 MHz bandwidth, source ≤25 Ω); recovery ≤10 µs to 0.5 %. Produced 1969–1991 (`Tektronix/TekWiki_7A22_webpage.html`).
- AM502 differential amplifier, TM500 series (`Tektronix/Tektronix_AM502_manual_070-1582-01.pdf`, "First Printing MAY 1983, Revised OCT 1986", PDF pp. 12–14 = printed 2-1 to 2-3): gain 100–100,000 (1-2-5), /100 mode 1–1000; DC–1 MHz, reducing to 500 kHz at 50K and 250 kHz at 100K gain; HF/LF filters as 7A22; 1 MΩ ∥ about 47 pF; CMRR 100 dB DC–50 kHz (normal mode, ±5 V common-mode range); gate current 50 pA; noise ≤25 µV tangential (source ≤25 Ω, 10 Hz–1 MHz) and "typically ≤6.0 nV/√Hz above 1 kHz"; output ±5 V, 20 mA. Produced 1974–1995 (TekWiki page).
- ADA400A differential preamplifier (`Tektronix/Tektronix_ADA400A_manual_070-9164-02.pdf`, PDF pp. 33–38 = printed 21–26; `Tektronix/Tektronix_ADA400A_datasheet_60W-10387-6.pdf`, 17 Feb 2016): gain 0.1/1/10/100; bandwidth limits 100 Hz, 3 kHz, 100 kHz, full ≥1 MHz; 1 MΩ ∥ about 55 pF (∞ selectable at ×10, ×100); CMRR ≥100,000:1 DC–10 kHz (datasheet), warranted 90 dB at 100 Hz/10 kHz and 60 dB at 100 kHz (gain 100); RMS noise ≤30 µV (1 MHz BW, gain 100), ≤10 µV (100 kHz BW, gain 100), datasheet "typically ≤30 µVrms at 100× gain (referred to input)"; 10 µVrms in 100 kHz corresponds to about 32 nV/√Hz (derived); powered from TEKPROBE oscilloscopes or 1103 supply. Introduced 1995 (TekWiki).

## 9. LeCroy DA1855A / DA1850A

Sources: `LeCroy/LeCroy_DA1855A_operators_manual_2015-08.pdf` (Teledyne LeCroy, August 2015), PDF pp. 10–13 and 87 (printed 4–7, 81); `LeCroy/LeCroy_2001_catalog.pdf` PDF p. 114.

- True differential; AC/off(precharge)/DC per input; 1 MΩ or 100 MΩ (÷1), 1 MΩ (÷10); 20 pF.
- Gain ×1 or ×10, attenuator ÷1 or ÷10; bandwidth >100 MHz (×1, warranted), 100 MHz (×10); bandwidth-limit filters 100 kHz, 1 MHz, 20 MHz (3-pole Bessel; 2001 catalogue lists 10 MHz, 1 MHz, 100 kHz).
- CMRR warranted ≥50,000:1 (94 dB) at 70 Hz and 100 kHz, ≥316:1 (50 dB) at 10 MHz; typical curve (Fig. 22) about 128 dB (×10) / 112 dB (×1) at 100 Hz, about 90/80 dB at 1 MHz, about 70/55 dB at 10 MHz (plot).
- $e_n$ (Fig. 23, referred to input, plot): ×10 about 4–5 nV/√Hz from about 500 kHz to 30 MHz, about 6 nV/√Hz to 100 MHz, rising to about 70 nV/√Hz at 10 kHz; ×1 about 12–13 nV/√Hz from 1 to 30 MHz. 2001 catalogue: "Typical Input Noise (×10 GAIN): 4 nV/√Hz @ 1 MHz".
- Differential range ±50 mV (×10, ÷1) to ±5 V; common-mode range ±15.5 V (÷1), ±155 V (÷10); input protection ±250 V with automatic disconnect; overdrive recovery to 1 mV RTI within 100 ns after 4 V (×10); built-in precision voltage generator (±15.5 V, 100 µV resolution) for true differential offset (DA1855A only; DA1850A lacks it).
- Line powered (about 28 W).

## 10. Zurich Instruments lock-in inputs

- MFLI (`ZurichInstruments/ZI_MFLI_MFIA_specifications_web.html`; `ZurichInstruments/ZI_MFLI_user_manual.pdf` Revision 26.10, PDF p. 237): 2 BNC, single-ended and differential; shield floating or ground (±1 V); 50 Ω or 10 MΩ, 27 pF (range ≥300 mV) / 40 pF (range ≤100 mV); DC–500 kHz (DC–5 MHz with MF-F5M); anti-alias 3 dB at 12 MHz; $e_n$ typ 2.5 nV/√Hz above 1 kHz, 7 nV/√Hz at 10 Hz, 40 nV/√Hz at 1 Hz (1 mV, 3 mV ranges), max 3.2 nV/√Hz above 1 kHz; 1/f corner about 100 Hz (range ≤10 mV); bias ±10 pA typ; ranges ±1 mV–±3 V; AC coupling 1.6 Hz. CMRR: not found in the specification text.
- UHFLI (`ZurichInstruments/ZI_UHF_user_manual.pdf` Revision 26.10, PDF pp. 269–270 = printed 263–264, PDF p. 277 = printed 271): BNC single-ended; 50 Ω or 1 MΩ ∥ 16 pF; DC–600 MHz (50 Ω), DC–100 MHz (1 MΩ); $e_n$ 4 nV/√Hz (>100 kHz, 10 mV range, 50 Ω); 1 MΩ white floor "below 8 nV/√Hz"; 1/f corner about 100 kHz; dynamic reserve 100 dB typ; 12 bit, 1.8 GSa/s.
- HF2LI (`ZurichInstruments/ZI_HF2_user_manual.pdf` Revision 26.10, PDF p. 224): $e_n$ 5 nV/√Hz (>10 kHz, AC coupling, 50 Ω and 1 MΩ).
- Introduction: UHFLI announced in a Laser Focus World news item of 4 May 2012 (`ZurichInstruments/LFW_2012-05-04_UHFLI_announcement.html`); MFLI in an item of 26 June 2015 (`ZurichInstruments/LFW_2015-06-26_MFLI_announcement.html`).

## 11. Liquid Instruments Moku:Pro

Sources: `LiquidInstruments/LI_MokuPro_datasheet.pdf` (©2026), p. 1; `LiquidInstruments/LI_MokuPro_full_specifications_v23-0321.pdf` PDF pp. 5, 34, 38.

- Inputs 50 Ω / 1 MΩ, AC/DC (AC corner 16 Hz into 1 MΩ); max 40 Vpp into 1 MΩ; 300 MHz or 600 MHz analog bandwidth; blended 10-bit 5 GSa/s and 18-bit 10 MSa/s ADCs; single-ended.
- $e_n$: 30 nV/√Hz at 100 Hz; 20 nV/√Hz at 10 MHz (1.25 GSa/s); 13 nV/√Hz at 10 MHz (5 GSa/s) (datasheet p. 1). Instrument specs: "<30 nV/√Hz above 10 Hz" and "<20 nV/√Hz above 1 MHz" at the 400 mVpp range (lock-in, PDF p. 34).
- Introduced 23 June 2021 (press release, `LiquidInstruments/PR_2021-06-23_MokuPro_launch_TMCnet.html`).

## 12. Stahl-Electronics PR-E3 ("PRE") room-temperature preamplifier (current)

Sources: `StahlElectronics/Stahl_PR-E3_4MHz_datasheet_v3.12.pdf` (PDF created 2024-12-05), PDF pp. 3, 5, 12; `StahlElectronics/Stahl_PR-E3_40MHz_datasheet_v3.22.pdf`, PDF pp. 4–5; `StahlElectronics/Stahl_PRE_product_page.html`.

- Architecture (4 MHz datasheet p. 3): one or two independent inverting paths; input stage "pre-selected low noise FET transistors" followed by amplifier and buffer, with independent feedback loops for biasing; DC-blocking capacitors at the inputs. Both inputs may be connected together ("single channel mode") to lower $e_n$ by √2 at the cost of √2 higher $i_n$: an explicit paralleled-FET technique. Not a true differential amplifier (two single-ended channels; differential signals handled by using both channels).
- 4 MHz version (p. 5): 0.5 kHz or 1.5 kHz to 4.0 MHz (±3 dB), 10 MHz at −10 dB; gain ×250 ±4 %; input >300 MΩ (DC), 150 MΩ capacitively coupled ∥ 16.4 pF ±2 pF; $e_n$ 1.05 nV/√Hz per channel and 0.69 nV/√Hz with both channels connected (100 kHz, 300 K, $V_{DD}$ = 12 V); $i_n$ 12 fA/√Hz per channel, 22 fA/√Hz both (10 kHz); output 50 Ω, 3.8 Vpp; supply +4.5…+9 V / −2.4…−5 V, mains unit +12/−3 V, about 2.6 W; 130 g. Noise plot p. 12 (plot): single-channel-mode $e_n$ about 0.6 nV/√Hz from about 30 kHz to 3 MHz at $V_{DD}$ = 9 V, rising steeply below about 10 kHz (about 15–20 nV/√Hz at 2.5 kHz). Product page headline: "0.6 nV/√Hz at 1 MHz single channel mode; 12 fA/√Hz at 10 kHz".
- 40 MHz version (p. 4): 1.5 kHz–45 MHz (±3 dB, 50 Ω load); ×250 (×125 into 50 Ω); input >300 MΩ (DC), 30 MΩ capacitively coupled ∥ 30 pF ±6 pF; $e_n$ 0.85 nV/√Hz (1 MHz); $i_n$ 25 fA/√Hz (100 kHz); noise figure 0.2 dB with 1 kΩ source, 2.7 dB with 50 Ω (1 MHz); abs. max input 25 Vpk vs GND, 400 V DC (p. 5).
- Price: not given in the opened files.
- Related cryogenic product, for reference only: CX-4 "20MHz Differential Version" cryogenic low-noise amplifier (`StahlElectronics/Stahl_CX-4_20MHz_differential_datasheet_v2.8.pdf`, V. 2.8, October 2025, PDF p. 4): differential low-noise input stage, 1.2 kHz–20 MHz at 4.2 K, CMRR >55 dB at 1 MHz, input capacitance 4.3 pF (300 K) / 1.0 pF (4.2 K) per input, $e_n$ 0.82 nV/√Hz at 1 MHz and $i_n$ 7 fA/√Hz at 100 kHz, both at 4.2 K; gain about 10 times lower at 300 K. Not a room-temperature benchmark. A 4 MHz CX-4 data sheet is also saved (not read).

## 13. Basel Precision Instruments SP1004 low-noise low-drift differential amplifier (current)

Sources: `BaselPrecisionInstruments/BasPI_product_catalogue_2026_V4p3_SP1004.pdf` (PDF title "2026_BASPI_productCatalogue-V4p3-draft", created 2026-03-11), pp. 1–2; `BaselPrecisionInstruments/UniBasel_SP1004_LNLD_differential_amplifier_datasheet_v1.0.pdf` (University of Basel electronics lab, "Datasheet Version 1.0", 2017), pp. 2, 4, 6, 13.

- Input stage: "discrete dual J-FET (IF 3602) in the input stage with a fixed gain of ×100", followed by switchable ×1/×10/×100 and a variable low-pass filter; active input-offset correction (UniBasel p. 2).
- $e_n$: 1.0 nV/√Hz for f >1 kHz, 1.8 nV/√Hz at 10 Hz, 6.5 nV/√Hz at 1 Hz (catalogue p. 2); UniBasel p. 13: 1.0 nV/√Hz above 100 Hz, 1.5 at 10 Hz, 4.0 at 1 Hz; white about 0.9 nV/√Hz, 1/f corner 15 Hz (p. 4).
- $i_n$ 6 fA/√Hz at 10 Hz, 12 fA/√Hz at 1 kHz (input resistor ∞) (catalogue); input current ±15 pA at 20 °C.
- Input: true differential, floating instrument; DC or AC (0.03 Hz); input resistor 10 MΩ, 10 GΩ or ∞ (catalogue) or 10 MΩ / 1 GΩ / ∞ (UniBasel 2017); input capacitance 125 pF to GND, 3.5 pF between inputs (UniBasel p. 13).
- Common-mode range ±1 V; CMRR >100 dB at 100 Hz (example 112 dB at 150 Hz, UniBasel p. 6).
- Gain 10², 10³, 10⁴ (remote controllable); low-pass 100 Hz–1 MHz (2nd order); bandwidth 1 MHz max; drift 0.3 µV/K; output ±10 V, 22 Ω; supply ±15 V floating, ±75 mA.

## 14. Other makers and recent products

- Turtle Industry T-01LNA (Japan; `TurtleIndustry/Turtle_T-01LNA_product_page_JP.html`, page dated 2022-06-24): single channel, BNC; input resistance 100 kΩ; $e_n$ about 2.5–3.0 nV/√Hz at 1 kHz; gain ×10/×31.6/×100; bandwidth DC–about 15 MHz (×10), 7 MHz (×31.6), 2 MHz (×100); output 50 Ω, ±4 V pk; 9 V (006P) battery, about 40 h alkaline, 12 mA. Single-ended. Catalogue and manual PDFs saved, not read.
- Sine Scientific Instruments (SSI, China) OE4011 (`SineScientific/SSI_OE4011_product_page.html`): JFET input; DC–5 MHz; single-ended or differential, AC/DC; 10 MΩ; $e_n$ about 3 nV/√Hz at 10 kHz; CMRR up to 113 dB; gain 20–80 dB in 4 steps; 2nd-order low-pass 1 Hz–1 MHz plus full bandwidth; ±10 V output. OE4003 (`SineScientific/SSI_OE4003_performance_specification_sheet_CN.pdf`, 2020): 100 kΩ; single-ended or differential; AC (0.016 Hz); $e_n$ 16.96 nV/√Hz (10 Hz), 7.65 (1 kHz), 2.411 (10 kHz), 2.2 (100 kHz); CMRR 77.32 dB (100 Hz); gain 10/20/50/100 (text extraction of a 1-page sheet).
- Alpha Lab LNA10 (`AlphaLab/AlphaLab_LNA10_product_page.html`): true differential, CMRR >90 dB; 1 MΩ; ≤4 nV/√Hz above 100 Hz; gain 10/100/1000; single-pole low-pass 1 Hz–1 MHz; AC (0.3 Hz) or DC.
- SPECS Nanonis MCVA5 (`SPECS_Nanonis/Nanonis_MCVA5_product_page.html`): 4 differential channels; >10 TΩ, <2 pA bias; $e_n$ <4 nV/√Hz (SE), <5.5 nV/√Hz (differential) at 10 kHz, gain 100/1000; CMRR >125 dB at 10 Hz, >120 dB at 100 Hz, >100 dB at 1 kHz, >80 dB at 10 kHz; DC–500 kHz linear, DC–1 MHz (−3 dB); gain 1–1000.
- SENIS NVM-01 nanovolt amplifier (`SENIS_GMW/SENIS_NVM-01_nanovolt_amplifier_datasheet_rev1.21.pdf`, Rev. 1.21, March 2018, p. 3): differential; 1 MΩ ∥ 6 pF; optimal source <100 Ω; $e_n$ ≤1 nV/√Hz for f >1 Hz; 0.1–10 Hz offset fluctuation ≤4 nV rms; output low-pass 10 or 40 Hz (low-frequency instrument).
- Lake Shore MeasureReady M81 VM-10 module (`LakeShore/LakeShore_VM-10_product_page.html`): 3.2 nV/√Hz at 1 kHz single-ended, 4.1 nV/√Hz differential (10 mV range); >1 TΩ, 120 pF (DC coupled); CMRR 80 dB up to 1 kHz.
- EM Electronics (UK) DC nanovolt amplifiers (`EMElectronics/EM_A20a_product_page.html`, `EMElectronics/EM_A23_product_page.html`; A23 data sheet PDF 2016-04-18 saved, not read): A20a equivalent noise resistance <3 Ω, input >30 MΩ rising to 1 GΩ; A23 about 35 Ω. Equivalent $e_n = \sqrt{4kTR}$ ≈ 0.22 and 0.76 nV/√Hz (derived, 300 K). DC/low-frequency only (A23 open-loop unity gain at 10 kHz).
- Keysight E4727A/B low-frequency noise analyzers, Picotest J2180A, Lake Shore M81-SSM manual, Nanonis MCVA5 pre-order blog and Mimea release notes, Turtle T-01LNA catalogue/manual, Stahl CX-4 4 MHz data sheet, FEMTO web pages, Krohn-Hite 7000 manual, SRS manuals other than the SR55x pages cited: saved for reference, not extracted for this survey.

## 15. Not obtained

- NF 1980s DC–10 MHz differential amplifier with 2SK389 (see 1.3); internal design (JFET count, bias current) of the 5307.
- PAR 5003, 5004; Brookdeal preamplifiers (no data sheet found; empty folder removed).
- Introduction years for most NF, FEMTO, Signal Recovery models; prices for most current products.
- CMRR of Zurich Instruments MFLI inputs.

---

## 16. Comparison table

$e_n$ in nV/√Hz, input-referred, typical unless "max". "SE" single-ended, "diff" differential (true differential unless noted). Year/status from the cited documents; "–" = not given.

| Instrument | Maker | Year / status | $e_n$ white | $e_n$ @ 10 Hz | $Z_{in}$ / $C_{in}$ | Diff? | CMRR | BW (vs gain) | Gain range | Power | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SR560 | SRS | current, USD 3,095 | 4 (1 kHz) | ≈12 (plot) | 100 MΩ ∥ 25 pF | SE/diff | 100 dB DC–1 kHz, −6 dB/oct to 1 MHz | 1.2 MHz −3 dB; ±0.3 dB to 300 kHz (G ≤1000) | 1–50,000 (1-2-5) | battery 15 h / line | ../benchmark/SRS_SR560_datasheet.pdf p. 3 |
| 5307 | NF | ©1998; current | 4 spec (G 1000); 2.5–3 (plot, G 100) | ≈4 (plot) | 1 MΩ (100 MΩ opt.) ∥ <35 pF (33 typ) | SE/diff, FET | ≥120 dB DC–1 kHz; ≈86 dB @1 MHz (G 100, plot) | DC–10 MHz (+0.2/−3 dB) at all gains | 10–1000 (1-2-5) | line 30 VA | NF_5307_specifications_EN.pdf; manual PDF p. 37 |
| LI-75A | NF | current | 2 (1 kHz) [index page 2.5] | – | 100 MΩ ∥ ≤50 pF | diff/SE/float, FET | 120 dB DC–100 Hz | DC–1 MHz | ×100 fixed | from lock-in / PS-70A | NF_LI-75A_catalog_JP.pdf p. 2 |
| CA5360 | NF | current | ≤5 (1 kHz) | – | 100 MΩ ∥ ≤50 pF | diff/SE, FET | ≥100 dB DC–100 Hz | DC–1 MHz | ×100 fixed | ±15–24 V ext. | NF_CA5360_specifications_EN.pdf |
| SA-440F5 | NF | current | 1.8 (1 kHz); ≈1.6 (10–300 kHz, plot) | ≈2 at 100 Hz (plot) | 1 M/100 M/open ∥ 60 pF | diff DC, FET | 90 dB 10 Hz–10 kHz; 60 dB 1 MHz | DC–20 MHz | 40 dB fixed | ±15 V ext. | NF_SA_series_en_sa_series.pdf pp. 3–4 |
| SA-240F5 | NF | current | 1.2 (1 kHz) | ≈1.5 at 100 Hz (plot) | 1 M/100 M/open ∥ 60 pF | SE DC, FET | – | DC–20 MHz | 40 dB fixed | ±15 V ext. | same |
| SA-410F3 | NF | current | 0.75 (1 kHz) | – | 1k/10k/100 kΩ ∥ 100 pF | diff DC, bipolar | ≥110 dB 55 Hz; 80 dB 100 kHz | DC–1 MHz | 40 dB fixed | ±15 V ext. | same |
| SA-420F5 | NF | current | 0.9 (100 kHz–10 MHz) | AC only (≥1 kHz) | 1 MΩ ∥ 15 pF | diff AC, FET | ≥55 dB 1 kHz–10 MHz | 1 kHz–70 MHz | 46 dB fixed | ±15 V ext. | same |
| SA-421F5 | NF | current | 0.5 (100 kHz–10 MHz) | AC (≥30 Hz) | 1 MΩ ∥ 85 pF | diff AC, FET | ≥46 dB 1 kHz–10 MHz | 30 Hz–30 MHz | 46 dB fixed | ±15 V ext. | same |
| SA-200F3 | NF | ≤2004; current | 0.5 (1 kHz) | ≈0.6 (plot) | 1k/10k/100 kΩ ∥ ≤150 pF | SE DC, bipolar | – | DC–800 kHz | 40 dB fixed | ±15 V ext. | same |
| SR552 | SRS | current, USD 750 | 1.4 (1 kHz) | 2.5 | 100 kΩ + 25 pF | SE/diff, BJT | 100 dB @100 Hz | gain acc. 2 % 2 Hz–100 kHz | 10–100 | from lock-in | SRS_SR552_datasheet.pdf |
| SR550 | SRS | schematic dated 1985; manual rev. 2017 | 3.6 (1 kHz) | 13 | 100 MΩ + 25 pF | SE/diff, dual JFET | 90 dB @100 Hz | 2 Hz–100 kHz (2 %) | 1–10 | from lock-in | SR550/551/552 manual pp. 4, 10 |
| SR554 | SRS | current, USD 2,695 | 0.1 | – (0.1 Hz–40 kHz) | transformer, source 0.05 Ω–1 kΩ | SE/diff | >120 dB <1 kHz | 0.1 Hz–40 kHz | 100 / 500 | from lock-in | SRS_SR554_datasheet.pdf p. 2 |
| DLPVA-101-B | FEMTO | 2024 rev; current | 2.0 (S) / 3.0 (D) | 1/f corner 80 Hz | 1 MΩ ∥ 105 pF | S or D, bipolar | 120 dB 100 Hz; 100 dB 10 kHz; 80 dB 60 kHz | DC–100 kHz (gain-indep.) | 20–80 dB (20 dB steps) | ±15 V ext. | FEMTO_DLPVA-101-B_datasheet.pdf p. 3 |
| DLPVA-101-F | FEMTO | 2025 rev; current | 5.0 (S) / 6.5 (D) | 1/f corner 80 Hz | 1 TΩ ∥ 18 pF | S or D, FET | as above | DC–100 kHz | 20–80 dB | ±15 V ext. | FEMTO_DLPVA-101-F_datasheet.pdf p. 3 |
| DLPVA-500-B/F | FEMTO | 2026 rev; current | B 2.0/3.0; F 5.0/6.5 | 1/f corner 80 Hz | 1 MΩ ∥ 105 pF / 1 TΩ ∥ 18 pF | S or D | as above | DC–500 kHz | 20–80 dB | ±15 V ext. | FEMTO_DLPVA-500-*_datasheet.pdf p. 3 |
| DLPVA-101-BLN-S | FEMTO | 2024 rev; current | 0.7 (60–100 dB) | 1/f corner 80 Hz | 1 MΩ ∥ 13 pF; $I_b$ 1 µA | SE, bipolar | – | DC–100 kHz | 40–100 dB | ±15 V ext. | FEMTO_DLPVA-101-BLN-S_datasheet.pdf p. 3 |
| DLPVA-100-BUN-S | FEMTO | 2019 rev; current | 0.40 (100 dB) | 1/f corner 100 Hz | 1 kΩ; $I_b$ 30 µA | SE, AC | – | 1.5 Hz–100 kHz | 40–100 dB | ±15 V ext. | FEMTO_DLPVA-100-BUN-S_datasheet.pdf p. 2 |
| HVA-10M-60-B | FEMTO | 2019 rev; current | 0.9 (60 dB), 1.8 (40 dB) at 2 MHz | – | 50 Ω ∥ 12 pF | SE | – | DC–10 MHz | 40/60 dB | ±15 V ext. | FEMTO_HVA-10M-60-B_datasheet.pdf p. 1 |
| HVA-10M-60-F | FEMTO | 2019 rev; current | 4.7 (2 MHz) | – | 1 MΩ ∥ 15 pF | SE, FET | – | DC–10 MHz | 40/60 dB | ±15 V ext. | FEMTO_HVA-10M-60-F_datasheet.pdf p. 1 |
| HVA-200M-40-F | FEMTO | 2019 rev; current | 4.5 (40 dB), 5.5 (20 dB) | – | 1 MΩ ∥ 15 pF | SE, FET | – | DC–200 MHz | 20/40 dB | ±15 V ext. | FEMTO_HVA-200M-40-F_datasheet.pdf p. 1 |
| DHPVA-101 | FEMTO | 2016 rev; current | 2.3 (30–60 dB) | 1/f corner 20 kHz | 50 Ω | SE | – | DC–100 MHz / 10 MHz (gain-indep.) | 10–60 dB | ±15 V ext. | FEMTO_DHPVA-101_datasheet.pdf p. 2 |
| 5113 | Signal Recovery | legacy (discont.) | 4 (1 kHz) | – | 10 or 100 MΩ ∥ 25 pF | A or A−B | >120 dB DC–1 kHz, −6 dB/oct | DC–1 MHz | 5–50,000 | battery ~30 h / line | SignalRecovery_5113_datasheet.pdf p. 2 |
| 5184 | Signal Recovery | legacy | 0.8 (1 kHz) | contour plot | 5 MΩ ∥ 50 pF | pseudo-diff, AC | >80 dB 100 Hz–1 kHz | 0.5 Hz–1 MHz | ×1000 | 4×9 V battery ~8 h | SignalRecovery_5184_datasheet.pdf |
| 5186 | Signal Recovery | legacy | 4 (×1000), 10 (×10/×100) at 1 kHz | contour plot | 100 MΩ ∥ 20 pF | diff, AC | >110 dB (×1000) 100 Hz–1 kHz, −6 dB/oct | 0.5 Hz–1 MHz | ×10/100/1000 | battery ~12 h | SignalRecovery_5186_datasheet.pdf |
| 5185 | Signal Recovery | ©2002; legacy | 10 (50 Ω), 30 (1 MΩ) at 10 kHz | – | 50 Ω or 1 MΩ ∥ 25 pF | SE | – | DC–200 MHz (50 Ω), DC–100 MHz (1 MΩ) | ×10/×100 | ±15/18 V ext. | SignalRecovery_5185_manual.pdf p. 11 |
| PAR 113 | PAR / EG&G | classic | NF 0.2 dB (1 kHz, 1 MΩ) only | NF 0.3 dB (10 Hz, 2 MΩ) | 100 MΩ ∥ 15 pF (AC), 1 GΩ ∥ 15 pF (DC) | SE/diff | 120 dB DC–100 Hz … 60 dB 100 kHz (G >200) | DC–300 kHz | 10–10⁴ | NiCd ~30 h / line | PAR_113_specifications_TEC.pdf pp. I-1–I-2 |
| 1201 | Ithaco / DL | classic | <7 (1 kHz) | <15 | >1 GΩ (DC), 100 MΩ (AC) | SE/diff | 125 dB DC–100 Hz … 50 dB 400 kHz (G >200) | DC–400 kHz | 10–10,000 (to 25,000) | line / NiCd option | DL_Ithaco_1201_datasheet_artisan.pdf pp. 7–9 |
| 7000 | Krohn-Hite | 2024 rev; current | 7 (×1k) | – | 1 MΩ ∥ 40 pF | SE/diff, FET | >105 dB 50 Hz, >90 dB 10 kHz, >75 dB 50 kHz | DC–1 MHz | ×1/10/100/1000 | line | KrohnHite_7000_datasheet.pdf pp. 1–2 |
| 7A22 | Tektronix | 1969–1991 | 16 µV tangential (1 MHz BW) | – | 1 MΩ ∥ 47 pF | diff | ≥100,000:1 DC–100 kHz | DC–1 MHz | 10 µV/div–10 V/div | 7000 mainframe | Tektronix_7A22_manual PDF pp. 7–9 |
| AM502 | Tektronix | 1974–1995 | ≤6.0 (>1 kHz) | – | 1 MΩ ∥ 47 pF | diff | 100 dB DC–50 kHz | DC–1 MHz (250 kHz at 100K) | 100–100,000 | TM500 mainframe | Tektronix_AM502_manual_070-1582-01 PDF p. 13 |
| ADA400A | Tektronix | 1995; – | ≤30 µVrms (1 MHz BW, ×100) | – | 1 MΩ ∥ 55 pF (∞ at ×10/×100) | diff | ≥100,000:1 DC–10 kHz | ≥1 MHz | 0.1–100 | from scope (TEKPROBE) | ADA400A manual PDF pp. 33–37 |
| DA1855A | LeCroy | ©2015 manual; – | ≈4–5 (×10, 0.5–30 MHz, plot); 4 @1 MHz (2001 cat.) | – (≈70 at 10 kHz) | 1 MΩ or 100 MΩ ∥ 20 pF | diff | ≥94 dB 70 Hz & 100 kHz; ≥50 dB 10 MHz | >100 MHz | ×1/×10 (÷1/÷10) | line 28 W | LeCroy DA1855A manual PDF pp. 12–13, 87 |
| SR830 | SRS | current | 6 (1 kHz) | – | 10 MΩ + 25 pF | SE/diff | 100 dB to 10 kHz | to 102 kHz | – | line | SRS_SR830_datasheet.pdf p. 3 |
| SR860 / SR865A | SRS | current | 2.5 (1 kHz, 10 mV range) | – | 10 MΩ + 25 pF | SE/diff | 90 dB to 1 kHz | 500 kHz / 4 MHz | – | line | SRS_SR860/SR865A_datasheet.pdf p. 4 |
| MFLI | Zurich Instr. | 2015; current | 2.5 typ, 3.2 max (>1 kHz) | 7 | 10 MΩ (or 50 Ω) ∥ 27–40 pF | SE/diff | not found | DC–500 kHz (5 MHz opt.) | ranges ±1 mV–±3 V | line | ZI_MFLI_MFIA_specifications_web.html |
| UHFLI | Zurich Instr. | 2012; current | 4 (>100 kHz, 50 Ω); <8 (1 MΩ) | 1/f corner ~100 kHz | 50 Ω or 1 MΩ ∥ 16 pF | SE | – | DC–600 MHz (50 Ω), 100 MHz (1 MΩ) | – | line | ZI_UHF_user_manual.pdf PDF pp. 269–277 |
| Moku:Pro | Liquid Instr. | 2021; current | 13–20 (10 MHz) | 30 at 100 Hz | 50 Ω / 1 MΩ | SE | – | 300/600 MHz | – | line | LI_MokuPro_datasheet.pdf p. 1 |
| PR-E3 (4 MHz) | Stahl-Electronics | 2024 rev; current | 1.05 per channel, 0.69 both channels (100 kHz); ≈0.6 (plot, 1 MHz) | AC only (≥0.5 kHz) | 150 MΩ ∥ 16.4 pF (AC) | 2 × SE (inverting), FET | – | 0.5 kHz–4 MHz | ×250 fixed | mains unit | Stahl_PR-E3_4MHz_datasheet_v3.12.pdf p. 5 |
| PR-E3 (40 MHz) | Stahl-Electronics | current | 0.85 (1 MHz) | AC only | 30 MΩ ∥ 30 pF (AC) | 2 × SE | – | 1.5 kHz–45 MHz | ×250 | mains unit | Stahl_PR-E3_40MHz_datasheet_v3.22.pdf p. 4 |
| SP1004 | Basel Precision Instr. | 2017 (UniBasel v1.0); current | 1.0 (>1 kHz) | 1.8 (cat.) / 1.5 (UniBasel) | 10 MΩ/1–10 GΩ/∞; 125 pF to GND | diff, dual JFET IF3602 | >100 dB @100 Hz | DC–1 MHz | 10²–10⁴ | ±15 V ext. (floating) | BasPI catalogue p. 2; UniBasel pp. 2, 13 |
| T-01LNA | Turtle Industry | 2022; current | 2.5–3.0 (1 kHz) | – | 100 kΩ | SE | – | DC–15 MHz (×10), 7 MHz (×31.6), 2 MHz (×100) | ×10/31.6/100 | 9 V battery ~40 h | Turtle_T-01LNA_product_page_JP.html |
| OE4011 | SSI (China) | current | ≈3 (10 kHz) | – | 10 MΩ | SE/diff, JFET | up to 113 dB | DC–5 MHz | 20–80 dB | – | SSI_OE4011_product_page.html |
| MCVA5 | SPECS Nanonis | current | <4 (SE), <5.5 (diff) at 10 kHz | – | >10 TΩ | 4 × diff | >120 dB 100 Hz; >80 dB 10 kHz | DC–1 MHz (−3 dB) | 1–1000 | – | Nanonis_MCVA5_product_page.html |
| LNA10 | Alpha Lab | current | ≤4 (>100 Hz) | – | 1 MΩ | diff | >90 dB | 1 Hz–1 MHz LPF | 10/100/1000 | – | AlphaLab_LNA10_product_page.html |

Observations relevant to the design target:

- Dedicated preamplifiers with a DC-coupled ≥1 MΩ input and ≥10 MHz bandwidth: NF 5307 (diff, 4 nV/√Hz spec, about 2.5–3 nV/√Hz plotted at gain 100, <35 pF), NF SA-440F5 (diff, 1.8 nV/√Hz, 60 pF, DC–20 MHz, CMRR 60 dB at 1 MHz), NF SA-240F5 (SE, 1.2 nV/√Hz, 60 pF), FEMTO HVA-10M-60-F and HVA-200M-40-F (SE, 4.7 and 4.5 nV/√Hz, 15 pF), Signal Recovery 5185 (SE, 30 nV/√Hz) and LeCroy DA1855A (diff, about 4–5 nV/√Hz only above about 500 kHz, 20 pF). Only the NF SA units are below 2 nV/√Hz, and among the differential ones only the 5307 combines <35 pF, DC–10 MHz and ≥120 dB low-frequency CMRR.
- Sub-nV/√Hz high-impedance figures exist only with AC coupling or reduced bandwidth: NF SA-421F5 (0.5 nV/√Hz, 1 MΩ ∥ 85 pF, 30 Hz–30 MHz), Stahl PR-E3 (0.6–0.7 nV/√Hz with two FET channels paralleled, 16 pF, 0.5 kHz–4 MHz), FEMTO DLPVA-101-BLN-S (0.7 nV/√Hz but bipolar, $I_b$ 1 µA, 100 kHz), BasPI SP1004 (1.0 nV/√Hz, DC–1 MHz, but 125 pF).
- The input capacitance accompanying about 0.5 nV/√Hz with FETs is 57–85 pF (NF SA-220F5/SA-421F5); the low-capacitance designs (FEMTO -F series 15–18 pF, Stahl 16 pF, NF SA-420F5 15 pF) sit at 0.7–5 nV/√Hz.
