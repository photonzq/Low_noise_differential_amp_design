# Fix phase 1a: archived simulation results (21 November 2026)

Every archived result with decks or curves behind it is reproduced bit for bit by an archived code path; no existing JSON value changed. Logs beside each JSON in sim/results/.

## 1. First-version oscillation — osc_check.py `first` (and `--ties`)
Entries record ci, cx, cnode, sink, v_sink, bench. osc_check.json:
- H100_first (50 Ω bench, C_I 6.19, C_X 4.42 pF, no C_node): 1.003 V pk-pk at 292.8 MHz, all common mode (cm_out 1.003 V, dm_out ≈ 0).
- L200_first (50 Ω bench, 13.4/7.8 pF, no C_node, first sinks MMBT3904 2 V): 0.780 V at 277.1 MHz, common mode.
- H10_first: 1.003 V at 292.8 MHz (same C_I + C_X = 10.61 pF as H100).
- H100_first_ties (inputs tied through 1 mΩ, the earliest bench): 1.026 V at 282.8 MHz; L200_first_ties: 0.795 V at 230.0 MHz. Frequency resolution f_res 1.43 MHz.
The archived H100_cnode0p (283 MHz) WAS the first version (deck 6.19/4.42 pF, ties bench), reproduced bit for bit by --ties; 283 vs 293 MHz is the bench, not the capacitors; 293 MHz (note line 451) is the 50 Ω bench.

## 2. THS4031 in S2, high reserve — da_compare.py `hr` (da_compare.json noise_H_HR.<S2>.H_HR_<gain>.en, e_post)
| S2, total gain | 10 Hz | 1 kHz | 10 kHz | 10 MHz (nV/√Hz) |
|---|---|---|---|---|
| THS4031, 100 | 4.68 | 2.06 | 2.02 | 3.03 |
| THS4031, 1000 | 4.20 | 2.04 | 2.01 | 3.02 |
| LM7171, 100 | 9.63 | 2.78 | 2.64 | 4.86 |
| LM7171, 1000 | 9.41 | 2.76 | 2.62 | 4.85 |
LM7171 rows = chain_noise.json. "2.0 nV/√Hz with the THS4031" holds only 1 kHz–1 MHz. da_compare.py docstring's stale data-sheet noise figures replaced.

## 3. R_UP test — cmrr_mc.py cases H100_jfet_rs0_R_UP, H100_jfet_rs0_ideal_I_BS (4 trials; H only, total gain 1000, JFET mismatch only, inputs driven directly; 16 decks byte-identical to sim/runs/cmrr_mc/test_rup_*)
cmrr_mc.json rup_test at 10 Hz / 100 Hz / 1 kHz: median_R_UP 106.2 / 111.8 / 129.1 dB; median_ideal_I_BS 138.0 / 137.9 / 137.5 dB; improvement_dB 31.8 / 26.1 / 8.4; R_BS_over_R_UP 0.321; f_BS 45.5 Hz.

## 4. L 10 V step and THS4031 file — large_signal.py (`--da`, `--l-sink first`, `--out`, `repro L1000_step`, `repro THS4031`); slew fix skips zero-length intervals (wrdata 8 significant digits)
L step: LM7171 in S2, L's first-design 2 V sinks; 1 V step fails on all four option sets; 10 V step only on the 50 Ω bench. THS4031 file: THS4031 was S2 before da_compare chose the LM7171; same first-design L sinks; H100 THD, step, overload, PSRR, plus L1000 THD. Both reproduce the archive exactly (rewritten under own names, byte-identical).
Key: L 10 V step 33.8 ns, 4.94 %, 106 / 164 ns, 274.7 V/µs; H with THS4031: 10 V slew 133.1 V/µs, recovery 0.193 µs; L at 10 MHz with THS4031: 0.0396 %.
Every archived L large-signal number predates the 6 V PZT3904 sinks; only PSRR redone with them.

## 5. L THD at 10 MHz and the floor — large_signal.py `floor` → large_signal_floor.json
The two values differ by S2: large_signal_log_L1000.txt = THS4031 run (L1000 entries of large_signal_THS4031.json); large_signal_log_2.txt = LM7171 run; same sinks and option set. L1000_10MHz_1Vpp: THS4031 0.0396 % (2 V sinks), 0.0401 % (6 V); LM7171 0.0078 % (2 V), 0.0072 % (6 V).
Floor: linear_reference (same sine, tran, options into ideal gain + RC): −158 to −179 dBc; grid_interpolation (resampling on the chain runs' own grids): worst −126 dBc (L, 1 MHz, 1 Vpp), typically −146 to −154 dBc; chain_settings (H at 1 kHz / 100 kHz / 1 MHz, 1 Vpp, under Gear, trapezoidal, reltol 2e-5, reltol 1e-5 with abstol 1e-11, 4× finer steps): −122.1, −121.0 to −121.4, −101.2 dBc; spread ≤ 0.4 dB. Note's "floor about −110 dBc" and "vary by several dB with integration settings" NOT supported.

## 6. Overload numbers — overload_detail.py `numbers` → overload_numbers.json (no simulation)
H (THS4031 in S2): recovery_us 0.193; output_during_V 11.362; op amps clip +13.422 / −12.970 V (26.393 V apart); after release oa min −2.147 V (−2.503 from rest), ob max +2.881 V (+2.526 from rest); whole run oa max +13.433, ob min −13.001; back within 12 mV of rest after 0.189 µs; output_ramp: delay 85.9 ns, 10–90 % slope 111.6 V/µs, peak 298.5 V/µs (single steps), 267.7 V/µs (5 ns average); sides: ΔV_GS +23.5 / −7.9 mV, summing nodes 8.993 → 8.562 / 9.134 V, current shift +0.718 mA (ΔV/R_D) vs +0.812 mA (g_m·ΔV_GS); servo: error −0.121 V, integrator change −2.41 µV, −0.334 V of output CM after 1 s, time constant 0.364 s; larger_overloads: gate reaches zero bias at 9.7× full scale.
L: recovery_us 0.153; undershoot −1.385 V at 87.7 ns, beyond −0.1 V for 33 ns (82–115 ns after release).
Disagreements with §6.5: "−1.9 / +2.6 V" → −2.15 / +2.88 V; ramp not a constant 133 V/µs slew (10–90 % 111.6, peak ≈ 268–299); "1.3 V for about 0.1 µs" → 1.38 V, 33 ns beyond −0.1 V.

## 7. chain_extras.py → chain_extras.json
(a) post: stages after the FE alone −3 dB at 116–156 MHz across the 7 allocations (S2 alone 193–210 MHz) → "beyond 100 MHz" holds.
(b) supply (ideal references draw nothing):
| | +15 V | −15 V | LT3045 at 2 / 3 V | LT3094 at 2 / 3 V |
|---|---|---|---|---|
| H, filters off | 76.7 mA | 76.2 mA | 0.15 / 0.23 W | 0.15 / 0.23 W |
| H, both filters on | 92.3 mA | 92.4 mA | 0.19 / 0.28 W | 0.19 / 0.28 W |
| L, filters off | 176.9 mA | 177.9 mA | 0.35 / 0.53 W | 0.36 / 0.53 W |
| L, both filters on | 192.6 mA | 194.0 mA | 0.39 / 0.58 W | 0.39 / 0.58 W |
L's drain resistors carry 120.1 mA.
(c) step: FE alone overshoots 8.82 % (10 V), 7.30 % (1 V); in the chain the FE reaches 9.48 % (S2 loads it); output 9.41 % (= large_signal.json). CONTRADICTS line 953 ("comes from the chain, not the front end"). Later stages limit slew: 395 V/µs at the FE vs 312 V/µs at the output; 10 Vpp full-power bandwidth 9.93 MHz.

## 8. Input admittance — collect_curves.py `zin` (+ `zin_net`) → curves_zin_network.npz, zin_numbers.json
C_eff (differential) at 1 k / 100 k / 300 k / 1 MHz: H bare 0.057 / 0.050 / 0.055 / 0.114 pF; H with network 20.06 / 20.05 / 20.04 / 19.93 pF; L bare 0.377 / 0.334 / 0.388 / 0.993 pF; L with network 250.4 / 250.3 / 250.3 / 250.1 pF.
Negative parallel resistance (Rpar_neg_min, _interp), bare: H −1049 Ω at 12.6 MHz (−1042 Ω interpolated, 13.3 MHz); L −110 Ω at 15.8 MHz; series minima ReZ_min.
NEW: with the network, H's Re(Y_in) stays negative from 0.14 to 25 MHz (minimum −1.64 kΩ at 12.6 MHz); L's positive everywhere.
sources_archived: 1 MΩ with network: H −21.9 dB at 100 kHz and −41.9 dB at 1 MHz; L −43.8 and −63.9 dB (line 861's "20 dB at 1 MHz" wrong). Peaking without network: 21.3 dB at 0.24 MHz (H, 1 MΩ), 16.0 dB at 2.63 MHz (L, 1 kΩ). Largest with network: 0.57 dB (network_largest_peak_db).

## Not reproduced / caveats
L's 1 V step fails on every bench (as archived); reltol 1e-5 with abstol 1e-12 fails at start-up (replaced by two tighter variants). models.py changed during the runs (JFE2325 RX only; unused here).

## README rows
| `osc_check.py` | adds `first [H10 H100 L200]` and `--ties`; entries record C_I, C_X, C_node, sink, bench | `osc_check.json` (`*_first*`), `osc_check_first_log.txt` |
| `da_compare.py` | adds `hr`: high-reserve noise at total gains 100 and 1000 with THS4031 and LM7171 in S2 | `da_compare.json` (`noise_H_HR`), `da_compare_hr_log.txt` |
| `cmrr_mc.py` | adds the R_UP test: `python cmrr_mc.py 4 H100_jfet_rs0_R_UP H100_jfet_rs0_ideal_I_BS` | `cmrr_mc.json` (`H100_jfet_rs0_*`, `rup_test`), `cmrr_mc_rup_log.txt` |
| `large_signal.py` | adds `--da`, `--l-sink first`, `--out`; `repro L1000_step`, `repro THS4031`; `floor [linear grid s2 settings]` | `large_signal_L1000_step.json`, `large_signal_THS4031.json`, `large_signal_floor.json`, logs |
| `overload_detail.py` | adds `numbers`: Section 6.5's overload numbers from the archived curves | `overload_numbers.json`, `overload_numbers_log.txt` |
| `collect_curves.py` | `zin` also runs `zin_net`: input admittance with and without the input network, Figure 10's numbers | `curves_zin_network.npz`, `zin_numbers.json`, `zin_numbers_log.txt` |
| `chain_extras.py` | stages after the FE alone, supply currents and regulator dissipation, FE step vs chain (`[post supply step]`) | `chain_extras.json`, `chain_extras_log.txt` |
Order additions: `osc_check.py first`, `da_compare.py hr`, `large_signal.py repro`, `large_signal.py floor`, `overload_detail.py numbers`, `chain_extras.py`.
