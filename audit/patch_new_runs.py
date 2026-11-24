"""Patch of low_noise_preamp.md after patch_noservo_rerun.py (23 November 2026): Table 13 and Section 6.5 take the
runs that converge with the KLU solver, and the KLU solver is cited.

- L's steps with the adopted 6 V sinks (large_signal.py L1000 step: on the 50-ohm bench with KLU; the same to
  0.01 ns as the first design's 2 V sinks of large_signal_L1000_step.json).
- H's overload with the LM7171 in S2 (overload_detail.py, 50-ohm sources, KLU), in place of the run with the
  THS4031 in S2 and 1-ohm sources, which is kept as a comparison (overload_numbers.json H100_THS4031).
- The KLU solver: the manual's sections on it and the paper that describes it, in Appendix A and the references.
Every edit is an exact-string replacement whose old text occurs once.  A second run is refused.
Usage: python patch_new_runs.py <path to low_noise_preamp.md>
"""
from __future__ import annotations

import sys
from pathlib import Path

EDITS: list[tuple] = [
    # ---- Table 13 ---------------------------------------------------------------------------------------------
    ("*Table 13. Large-signal results (`scripts/large_signal.py`; `sim/results/large_signal.json`; L's steps from "
     "`large_signal_L1000_step.json` and H's recovery from `large_signal_THS4031.json`, both reproduced by "
     "`scripts/large_signal.py repro`; rounded by `scripts/numbers_s6_7.py`). THD includes harmonics 2–9 of a "
     "differential sine, at the output; H at a total gain of 100 (front end ×100, S2 at the full output level), L at "
     "1000. S2 is the LM7171 unless stated. L's entries are simulated with the 6 V PZT3904 sinks of Section 4.2.1, "
     "except the steps: with these sinks the step transients did not complete (Appendix A, \"Transients that stop or "
     "crawl\"), so L's steps are those of the first design's 2 V sinks (MMBT3904), with which the loop margins and the "
     "bandwidth are the same (`sink_power.json`).*",
     "*Table 13. Large-signal results (`scripts/large_signal.py`; `sim/results/large_signal.json`, the recoveries from "
     "`scripts/overload_detail.py`; rounded by `scripts/numbers_s6_7.py`). THD includes harmonics 2–9 of a differential "
     "sine, at the output; H at a total gain of 100 (front end ×100, S2 at the full output level), L at 1000. S2 is "
     "the LM7171, and L has the 6 V PZT3904 sinks of Section 4.2.1. Several entries ran with ngspice's KLU solver "
     "(Appendix A, \"Transients that fail at the start, and the matrix solver\"). L's steps run only with the inputs "
     "driven from 50 Ω; with the first design's 2 V sinks (MMBT3904) they are the same to 0.01 ns "
     "(`large_signal_L1000_step.json`).*"),
    ("| 34 ns, 4.7 %, 105 / 163 ns (50 Ω sources; 2 V sinks) |", "| 34 ns, 4.7 %, 105 / 163 ns (50 Ω sources) |"),
    ("| 34 ns, 4.7 %, 106 / 163 ns, 275 V/µs (50 Ω sources; 2 V sinks) |",
     "| 34 ns, 4.7 %, 106 / 163 ns, 275 V/µs (50 Ω sources) |"),
    ("| Recovery from a threefold overload held for 20 µs, to 1 % | 0.19 µs (THS4031 in S2; 1 Ω sources) | 0.15 µs (50 Ω sources) |",
     "| Recovery from a threefold overload held for 20 µs, to 1 % | 0.16 µs (50 Ω sources) | 0.15 µs (50 Ω sources) |"),
    # ---- Section 6.5: H's overload with the LM7171 ----------------------------------------------------------------
    ("When the input returns, the front end's outputs swing to −2.13 V (side A) and +2.86 V (side B), 2.49 and 2.51 V "
     "from rest, and are back within 12 mV of rest after 0.19 µs. The output is within 0.1 V after 0.19 µs: after a "
     "delay of 86 ns it returns with a 10–90 % slope of 113 V/µs and peaks of 268 V/µs over 5 ns, not at a constant "
     "slew rate (Figure 16d). (These waveforms are from the run with the THS4031 in S2, "
     "`sim/results/overload_curves_H100_THS4031.npz`, and the numbers from `scripts/overload_detail.py numbers`, "
     "`sim/results/overload_numbers.json`. The front end is the same with either S2, and S2 clips only after it. With "
     "the LM7171 in S2, the same transient stopped with \"timestep too small\" at the onset of the overload (in an "
     "input JFET or in the model of S3's op amp) or ran past its time limit, on both benches and with every "
     "integration setting of ngspice's default solver (Appendix A, \"Transients that stop or crawl\"); with the KLU "
     "solver it runs, with 50 Ω sources, and the output recovers within 0.16 µs (`large_signal.json`), so the failure "
     "was numerical, not a property of the circuit.)",
     "When the input returns, the front end's outputs swing to −2.58 V (side A) and +3.42 V (side B), 2.93 and 3.06 V "
     "from rest, and are back within 12 mV of rest after 0.20 µs. The output, after a delay of 63 ns, returns with a "
     "10–90 % slope of 325 V/µs and peaks of 356 V/µs over 5 ns, about the chain's slew rate (312 V/µs on the 10 V "
     "step, Table 13), undershoots by 3.30 V, stays more than 0.1 V below its final value for 26 ns, overshoots by "
     "0.73 V and is within 0.1 V after 0.16 µs (Figure 16d). (Waveforms and numbers from "
     "`scripts/overload_detail.py`, `sim/results/overload_curves.npz` and `sim/results/overload_numbers.json`, with "
     "50 Ω sources and the KLU solver. With ngspice's default solver this transient stopped with \"timestep too "
     "small\" at the onset of the overload (in an input JFET or in the model of S3's op amp) or ran past its time "
     "limit, on both benches and with every integration setting tried (Appendix A). The earlier version of this "
     "section therefore used the same front end with the THS4031 in S2 and 1 Ω sources, which ran: its output "
     "recovers within 0.19 µs, returning with a 10–90 % slope of 113 V/µs.)"),
    ("In the H run they still follow to within +23.5 mV (side A) and −7.9 mV (side B),",
     "In the H run they still follow to within +23.4 mV (side A) and −8.0 mV (side B),"),
    ("from 8.99 V to 8.56 V (side A) and 9.13 V (side B), i.e. $\\Delta I = -\\Delta V/R_D$ = +0.72 mA and −0.23 mA "
     "with $R_D$ = 600 Ω ($g_m\\Delta V_{GS}$ gives +0.81 and −0.27 mA). Nothing winds up beyond this: the summing "
     "nodes are back within 10 mV of rest 0.11 µs after the input returns.",
     "from 8.99 V to 8.56 V (side A) and 9.14 V (side B), i.e. $\\Delta I = -\\Delta V/R_D$ = +0.71 mA and −0.24 mA "
     "with $R_D$ = 600 Ω ($g_m\\Delta V_{GS}$ gives +0.81 and −0.28 mA). Nothing winds up beyond this: the summing "
     "nodes are back within 10 mV of rest 0.12 µs after the input returns."),
    ("(H with the THS4031 in S2: after 86 ns the output returns with a 10–90 % slope of 113 V/µs; L with the LM7171, "
     "driven from 50 Ω; `overload_numbers.json`).*",
     "(both with the LM7171 in S2, driven from 50 Ω and run with the KLU solver: H's output returns after 63 ns with a "
     "10–90 % slope of 325 V/µs; `overload_numbers.json`).*"),
    ("The L results of Sections 4 and 6 are simulated with the 6 V sinks, except the steps of Table 13, which did not "
     "complete with them (Appendix A) and come from the first design's 2 V sinks; with either sink design the loop "
     "margins and the bandwidth are the same (`scripts/sink_power.py`), and the sinks' output impedance only rises "
     "with $R_T$.",
     "The L results of Sections 4 and 6 are simulated with the 6 V sinks, the steps of Table 13 included (they run "
     "with the KLU solver, Appendix A, and the first design's 2 V sinks give the same to 0.01 ns); with either sink "
     "design the loop margins and the bandwidth are the same (`scripts/sink_power.py`), and the sinks' output "
     "impedance only rises with $R_T$."),
    # ---- Appendix A ----------------------------------------------------------------------------------------------
    ("What made them run was the other direct solver, KLU (`.options klu`), with abstol = 1e-11 A.",
     "What made them run was the other direct solver that ngspice offers, KLU (T. A. Davis and E. Palamadai "
     "Natarajan, ACM Transactions on Mathematical Software 37, 2010; `.options klu`, User's Manual p. 316, where it "
     "is not available for noise analyses, which therefore stay with Sparse 1.3), with abstol = 1e-11 A."),
    ("H's overload figures therefore come from the same front end with the THS4031 in S2 and 1 Ω sources, which runs "
     "in a few seconds (`overload_detail.py --h-ths4031`; S2 clips only after the front end). L's overload ran with "
     "the first attempt. Without the servo both overloads stop with Gear, and both run with the KLU solver of the "
     "previous item, H with the LM7171 in S2 included (50 Ω sources; recovery 0.16 µs, Section 6.5).",
     "H's overload figures therefore came from the same front end with the THS4031 in S2 and 1 Ω sources, which runs "
     "in a few seconds (`overload_detail.py --h-ths4031`; S2 clips only after the front end). L's overload ran with "
     "the first attempt. Without the servo both overloads stop with Gear, and both run with the KLU solver of the "
     "previous item, H with the LM7171 in S2 included; Section 6.5 now quotes that run (50 Ω sources; recovery "
     "0.16 µs, against 0.19 µs with the THS4031)."),
    ("both steps ran on the 50 Ω bench, where before the recalibration the 1 V step had failed on every bench; Table 13 "
     "quotes those. H's steps ran as before. Without the servo, Gear stops L's steps on both benches; with the KLU "
     "solver they run on the 50 Ω bench, with the archived result to one 0.2 ns time step.",
     "both steps ran on the 50 Ω bench, where before the recalibration the 1 V step had failed on every bench; Table 13 "
     "quoted those. H's steps ran as before. Without the servo, Gear stops L's steps on both benches; with the KLU "
     "solver they run on the 50 Ω bench, with the archived result to one 0.2 ns time step, and so do the steps with "
     "the 6 V sinks, which Table 13 now quotes: they are the same to 0.01 ns."),
    # ---- References ----------------------------------------------------------------------------------------------
    ("**Simulator.** H. Vogt, G. Atkinson, D. Warning and P. Nenzi, *Ngspice User's Manual*, Version 46, 31 March 2026, "
     "§7.4.4 (the JFET level 1 model), pp. 152–154, and §11.3.5 (the operating point and its transient fallback), "
     "pp. 327–328 (`refs/literature/ngspice_2026_Users_Manual_v46.pdf`).",
     "**Simulator.** H. Vogt, G. Atkinson, D. Warning and P. Nenzi, *Ngspice User's Manual*, Version 46, 31 March 2026, "
     "§1.4 (the convergence criteria), pp. 45–46, §7.4.4 (the JFET level 1 model), pp. 152–154, §11.1 (the options, "
     "with §11.1.1 on the Sparse 1.3 and KLU solvers), pp. 316–321, and §11.3.5 (the operating point and its "
     "transient fallback), pp. 327–328 (`refs/literature/ngspice_2026_Users_Manual_v46.pdf`). T. A. Davis and E. "
     "Palamadai Natarajan, \"Algorithm 907: KLU, a direct sparse solver for circuit simulation problems\", *ACM "
     "Transactions on Mathematical Software* **37**(3), Article 36 (2010), https://doi.org/10.1145/1824801.1824814 "
     "(the KLU solver; cited in the manual, p. 562)."),
]


def main() -> None:
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    assert "\r" not in text
    if "Algorithm 907: KLU" in text:
        sys.exit("already patched: refusing a second run")
    for e in EDITS:
        old, new = e[0], e[1]
        n = e[2] if len(e) > 2 else 1
        c = text.count(old)
        assert c == n, (c, n, old[:90])
        text = text.replace(old, new)
    print(f"{len(EDITS)} edits applied to {path.name}")
    path.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
