"""Patch of low_noise_preamp.md after the re-run without the servo (23 November 2026; after
patch_noservo.py): the operating-point pitfall as the re-run found it.

Without the servo, the gain-30 variant's noise deck and the JFE150 sink's decks converge, and the loop
decks of the two gain-20 variants with a smaller R_F fall back to ngspice's transient op instead (1-ohm
ties do not help them; abstol = 1e-12 A does).  Section 5.1's paragraph is rewritten as a whole (both ends
asserted), with the earlier cases kept as what the netlists with the servo do (op_pitfall.py reproduces
both); Section 6.1's JFE150 bullet, Appendix A's two operating-point items and the Files rows follow.
Every other edit is an exact-string replacement whose old text occurs the stated number of times (once
unless given).  A second run is refused.  Usage: python patch_noservo_rerun.py <path to low_noise_preamp.md>
"""
from __future__ import annotations

import sys
from pathlib import Path

START = "**A pitfall: a wrong operating point without an error.** For one variant of Section 4.3.1"
END = ("and `scripts/sink_options.py` now evaluates a variant again with 1 Ω ties whenever the operating point "
       "of one of its decks falls back.\n")

PITFALL = r"""**A pitfall: a wrong operating point without an error.** When gmin stepping and source stepping both fail, ngspice-46 falls back to a transient operating point: the end of a 10 µs transient, which it notes only in the log and which need not be a DC solution (Appendix A). For the two variants of Section 4.3.1 with a smaller $R_F$ at a gain of 20, the decks of the complete loop (the injection at the op amps' outputs) fell back in this way, while the AC and noise decks of the same circuits converged. In the fallback's state the 10 µF of the sinks' reference filter and the 1 µF bootstrap capacitors are still almost uncharged, against time constants of milliseconds (10 ms for the filter's 1 kΩ and 10 µF). The sinks' bases sit at −0.13 V instead of −12.24 V, the saturated sinks pull the source nodes to −1.49 V instead of +0.355 V, the input gates conduct 50 mA each, and the op amps sit at −10.0 V. Kirchhoff's current law at the bootstrap node fails by 1.51 mA, $R_{UP}$'s whole current, which in the transient is still charging $C_{BS}$. The loop gain is then near zero at every frequency: the margins come out as no crossover and 36 dB of gain margin, where the circuit has 50.4° at 17.8 MHz. Tying the gates through 1 Ω instead of 1 mΩ does not help here. With abstol = 1e-12 A instead of 1e-15 A the decks converge, to the margins of Table 6b: 50.4° and 21.5 dB at 17.8 MHz in differential mode, 42.1° and 10.6 dB at 54.0 MHz in common mode (`scripts/op_pitfall.py` reproduces every number of this paragraph, `sim/results/op_pitfall.json`). Which deck falls back cannot be told from the circuit. With the servo of Appendix B in the netlists, these loop decks converged and two other decks fell back instead. The noise deck of the gain-30 variant gave 64.0 nV/√Hz instead of 1.07, with the same uncharged bootstrap (1.49 mA of $R_{UP}$'s 1.50 mA), while its AC deck converged. The decks of the JFE150 sink at a gain of 100 (Section 6.1) settled with the source nodes at −0.95 V and the input gates conducting, which only the AC response gave away, with a bandwidth of 322 MHz instead of 15.0 MHz; those decks converged with 1 Ω ties. Without the servo, both converge as they are. `scripts/gain_options.py` and `scripts/sink_options.py` therefore check the log of every deck they run, and repeat a case whose decks fell back with abstol = 1e-12 A, then with 1 Ω ties, then with both (`op_checked` in `scripts/frontend.py`); each entry records what it took. `gain_options.py` also compares each noise run's own gain with the AC run's at 1 kHz and repeats a run that disagrees from the AC run's operating point (`.nodeset`), the check that caught the gain-30 case.
"""

TRANSIENTS = (
    "- **Transients that fail at the start, and the matrix solver.** A few decks stopped with \"timestep too small\" in "
    "the first tens of nanoseconds with one set of options and ran with another. Without the servo (Section 4.2), many "
    "more stopped in this way, with Gear and with trapezoidal integration, many of them within their first nanosecond "
    "and most in the convergence test of an input JFET: H's distortion at 1 kHz, 1 MHz and 10 MHz at 1 Vpp (also with "
    "the LM7171 in S2 in Table 14's comparison), H's 1 V step, the front end's steps alone, L's distortion at 100 kHz, "
    "1 MHz and 10 MHz, L's steps, L's oscillation check (Section 4.3) and both overloads. Their operating points were "
    "DC solutions, and the same decks with the servo's elements put back ran and gave the archived results, so the "
    "circuits were not the cause; an element that only reads four node voltages into its own resistor, connected to "
    "nothing else, made seven of the first eight decks tested run as well, which points at the order in which ngspice's "
    "default direct solver, Sparse 1.3, eliminates the matrix. Of the options in the ngspice-46 User's Manual (pp. 45–46 and 316–321), tighter or looser "
    "tolerances (reltol, vntol, abstol, chgtol, trtol, gmin), Gear orders 3 to 6, damped trapezoidal integration (xmu), "
    "backward Euler, other pivoting thresholds and other shunt resistors failed again or ran with a different result: "
    "H's THD at 10 MHz came out between 1.06 × 10⁻⁴ and 1.96 × 10⁻⁴ against 1.19 × 10⁻⁴. What made them run was the "
    "other direct solver, KLU (`.options klu`), with abstol = 1e-11 A. KLU reproduces the archived results to four or "
    "five digits (H's THD at 10 MHz 1.1919 × 10⁻⁴ against 1.1918 × 10⁻⁴; L's steps settle in 105.4 and 162.6 ns "
    "against 105.6 and 162.8 ns), agrees with the default solver to the same precision on the decks that run with "
    "both, and starts a transient at its operating point, where the default solver moves H's outputs by 1.05 mV in "
    "common mode within the first 0.3 µs (Section 4.3). Three exceptions remain. KLU's own operating point falls back "
    "to the transient op for the front end alone and for the chains with the THS4031 or the THS3091 in S2, and the run "
    "then reports no error and holds a chain without signal; those decks run with the default solver at abstol = "
    "1e-11 A or with trapezoidal integration. And L at 10 MHz runs only with KLU at reltol = 3e-4 or 1e-3, with the "
    "same result to four digits at the normal and at a four times finer time step: 0.0072 %, where the default solver "
    "with the servo in the netlist had given 0.0100 % and, with the finer step, stops (Section 6.5). The transient "
    "benches now try, in order, Gear; Gear with KLU and abstol = 1e-11 A; the same with reltol = 3e-4; trapezoidal "
    "integration; Gear with abstol = 1e-11 A; Gear with itl4 = 1000 and reltol = 2e-4; and last the inputs driven "
    "from 50 Ω, with Gear and then with KLU (`TRIES` in `scripts/large_signal.py`; the oscillation check, the front "
    "end's step and the overload runs use the same order). They take no run whose operating point fell back "
    "(`check_dc` in `scripts/spice.py`) and record which one ran.")

EDITS: list[tuple] = [
    # ---- Section 6.1: the JFE150 sink -----------------------------------------------------------------------
    ("- **The JFE150 sink at a gain of 100 needed 1 Ω ties.** With the sources tied to the gates through 1 mΩ, "
     "the operating point of every deck fell back to a state that is not a DC solution, with the source nodes at "
     "−0.95 V and the input gates conducting, which the first version of this note took for a latched state "
     "(Section 5.1, Appendix A). With 1 Ω ties it gives 1.07 nV/√Hz, the margins of the other variants and −3 dB "
     "at 15.1 MHz.",
     "- **The JFE150 sink at a gain of 100** gives 1.07 nV/√Hz, the margins of the other variants and −3 dB at "
     "15.0 MHz. With the servo of Appendix B in its netlists, the operating point of every deck fell back to a "
     "state that is not a DC solution, with the source nodes at −0.95 V and the input gates conducting, which the "
     "first version of this note took for a latched state (Section 5.1)."),
    # ---- Appendix A: the two operating-point items ------------------------------------------------------------
    ("In the SR560 reproduction and with the JFE150 sink of Section 6.1 the same resistors made operating points "
     "fail (next item); those decks now use 1 Ω.",
     "In the SR560 reproduction, and with the JFE150 sink of Section 6.1 while the servo of Appendix B was in the "
     "netlists, the same resistors made operating points fail (next item); those decks now use 1 Ω."),
    ("The two wrong operating points of Section 5.1, the gain-30 variant's noise deck and every deck of the JFE150 "
     "sink, are the same fallback; the JFE150 sink's decks converge with 1 Ω ties, which `scripts/sink_options.py` "
     "now uses for a variant whose decks fall back.",
     "The wrong operating points of Section 5.1 are the same fallback: in the front ends of this note, the loop "
     "decks of the gain-20 variants with a smaller $R_F$, which converge with abstol = 1e-12 A but not with 1 Ω "
     "ties; with the servo of Appendix B in the netlists, the gain-30 variant's noise deck and every deck of the "
     "JFE150 sink, which converged with 1 Ω ties. A front-end case whose decks fall back is now repeated with "
     "abstol = 1e-12 A, then with 1 Ω ties, then with both (`op_checked` in `scripts/frontend.py`, used by "
     "`scripts/gain_options.py` and `scripts/sink_options.py`)."),
    # ---- Table 8a: the JFE150 runs as the others ---------------------------------------------------------------
    (" The JFE150 at a gain of 100 runs with the sources tied to the gates through 1 Ω instead of 1 mΩ (Section 5.1).*",
     "*"),
    # ---- Section 4.3: the oscillation check of the final values -----------------------------------------------
    ("A transient run with the final values shows no oscillation (≤ 1 µV peak to peak at the outputs, "
     "`scripts/osc_check.py`; for L with trapezoidal integration, because Gear integration stops partway through, a "
     "numerical failure described in Appendix A); the same bench,",
     "A transient run with the final values shows no oscillation (`scripts/osc_check.py`). After the first 0.3 µs H's "
     "outputs stay within 1.05 µV peak to peak, the tail of a 1.05 mV common-mode shift that ngspice's default matrix "
     "solver puts into the start of the run, and L's, run with the KLU solver because Gear integration with the "
     "default solver stops partway through, stay within 0.04 µV (both numerical, Appendix A); the same bench,"),
    # ---- Section 5.1: the transients' options -----------------------------------------------------------------
    ("and Gear integration with abstol = 1e-12 A for transients. Every deck is written",
     "and Gear integration with abstol = 1e-12 A for transients, followed, where a transient stops, by the KLU "
     "solver and the further option sets of Appendix A. Every deck is written"),
    # ---- Table 13 -----------------------------------------------------------------------------------------------
    ("| THD, 1 MHz, 1 / 10 Vpp | 0.0009 % / 0.025 % | 0.0009 % / 0.023 % |",
     "| THD, 1 MHz, 1 / 10 Vpp | 0.0009 % / 0.025 % | 0.0008 % / 0.023 % |"),
    ("| THD, 10 MHz, 1 Vpp | 0.012 % (fundamental 0.961 Vpp) | 0.0100 % (fundamental 0.916 Vpp) |",
     "| THD, 10 MHz, 1 Vpp | 0.012 % (fundamental 0.961 Vpp) | 0.0072 % (fundamental 0.916 Vpp) |"),
    ("| 34 ns, 4.7 %, 106 / 163 ns (50 Ω sources; 2 V sinks) |", "| 34 ns, 4.7 %, 105 / 163 ns (50 Ω sources; 2 V sinks) |"),
    # ---- Section 6.5: distortion and the floor ---------------------------------------------------------------
    ("L's value at 10 MHz depends on S2 and, less, on the sinks: 0.0100 % with the LM7171 and 0.0369 % with the "
     "THS4031 with the 6 V sinks, 0.0072 % and 0.0376 % with the first design's 2 V sinks (`scripts/large_signal.py "
     "floor`, `sim/results/large_signal_floor.json`).",
     "L's value at 10 MHz depends on S2, not on the sinks: 0.0072 % with the LM7171 and 0.0377 % with the THS4031 "
     "with the 6 V sinks, 0.0072 % and 0.0373 % with the first design's 2 V sinks (`scripts/large_signal.py floor`, "
     "`sim/results/large_signal_floor.json`; an earlier 0.0100 % for the LM7171 with the 6 V sinks came from ngspice's "
     "default solver, which does not run that deck with a finer time step, Appendix A)."),
    ("and five integration settings (Gear, trapezoidal, two tighter tolerances, four times finer steps) change H's THD at "
     "1 Vpp by at most 0.1 dB: −122.0 to −122.1 dBc at 1 kHz, −121.0 to −121.2 dBc at 100 kHz and −101.2 to −101.3 dBc "
     "at 1 MHz (`large_signal_floor.json`; at 100 kHz the setting with reltol = 1e-5 and abstol = 1e-11 stopped, "
     "Appendix A).",
     "but the integration of the nonlinear chain varies more. Of six integration settings (Gear, trapezoidal, two "
     "tighter tolerances, four times finer steps, and Gear with the KLU solver), the two or three that run at each "
     "frequency give H's THD at 1 Vpp as −122.0 to −122.1 dBc at 1 kHz, −119.9 to −121.0 dBc at 100 kHz and −100.3 to "
     "−101.2 dBc at 1 MHz, a spread of up to 1.1 dB (`large_signal_floor.json`); the others stop with \"timestep too "
     "small\", most within their first nanoseconds (Appendix A)."),
    # ---- Section 6.5: overloads --------------------------------------------------------------------------------
    ("stays more than 0.1 V below its final value for 33 ns,", "stays more than 0.1 V below its final value for 32 ns,"),
    ("returns with a 10–90 % slope of 111 V/µs and peaks of 268 V/µs", "returns with a 10–90 % slope of 113 V/µs and peaks of 268 V/µs"),
    ("after 86 ns the output returns with a 10–90 % slope of 111 V/µs;", "after 86 ns the output returns with a 10–90 % slope of 113 V/µs;"),
    ("or ran past its time limit, on both benches and with every integration setting tried (Appendix A, \"Transients "
     "that stop or crawl\"); since the front end and the THS4031 version run normally, this is taken to be a numerical "
     "failure of the run, not a property of the circuit.)",
     "or ran past its time limit, on both benches and with every integration setting of ngspice's default solver "
     "(Appendix A, \"Transients that stop or crawl\"); with the KLU solver it runs, with 50 Ω sources, and the output "
     "recovers within 0.16 µs (`large_signal.json`), so the failure was numerical, not a property of the circuit.)"),
    # ---- Appendix A: the transients -----------------------------------------------------------------------------
    ("- **Transients that fail at the start.** A few decks stopped with \"timestep too small\" in the first tens of "
     "nanoseconds with one set of options and ran with another. The large-signal benches try three sets of options in "
     "turn and then the inputs driven from 50 Ω (`tran` in `scripts/large_signal.py`), and record which one ran.",
     TRANSIENTS),
    ("trapezoidal integration runs the full 1 µs at 0.075 µV. `scripts/osc_check.py` now repeats a run that Gear stops "
     "in this way with trapezoidal integration, in its own folder, and records it in the entry (`integration`).",
     "trapezoidal integration runs the full 1 µs at 0.075 µV. Without the servo, Gear stops it at 308 ns and "
     "trapezoidal integration at 373 ns, and Gear with the KLU solver runs it at 0.04 µV. `scripts/osc_check.py` now "
     "repeats a run that Gear stops in this way, in the order of the previous item, each retry in its own folder, and "
     "records the one that ran in the entry (`integration`)."),
    ("which runs in a few seconds (`overload_detail.py --h-ths4031`; S2 clips only after the front end). L's overload "
     "ran with the first attempt.",
     "which runs in a few seconds (`overload_detail.py --h-ths4031`; S2 clips only after the front end). L's overload "
     "ran with the first attempt. Without the servo both overloads stop with Gear, and both run with the KLU solver of "
     "the previous item, H with the LM7171 in S2 included (50 Ω sources; recovery 0.16 µs, Section 6.5)."),
    ("both steps ran on the 50 Ω bench, where before the recalibration the 1 V step had failed on every bench; Table 13 "
     "quotes those. H's steps ran as before.",
     "both steps ran on the 50 Ω bench, where before the recalibration the 1 V step had failed on every bench; Table 13 "
     "quotes those. H's steps ran as before. Without the servo, Gear stops L's steps on both benches; with the KLU "
     "solver they run on the 50 Ω bench, with the archived result to one 0.2 ns time step."),
    # ---- Files ------------------------------------------------------------------------------------------------
    ("| `scripts/op_pitfall.py` | Section 5.1: the two wrong operating points, ngspice's transient-op fallback in "
     "both, reproduced, with Kirchhoff's current law at the bootstrap node (`op_pitfall.json`) |",
     "| `scripts/op_pitfall.py` | Section 5.1: the wrong operating points, ngspice's transient-op fallback in each, "
     "reproduced without the servo (the gain-20 loop decks, as run, with 1 Ω ties and with abstol = 1e-12 A) and "
     "with it (the gain-30 noise deck, the JFE150 sink), with Kirchhoff's current law at the bootstrap node "
     "(`op_pitfall.json`) |"),
    ("a variant whose decks' operating points fall back is evaluated again with 1 Ω ties (`python sink_options.py "
     "only <entry>` re-runs single entries)",
     "a variant whose decks' operating points fall back is evaluated again with abstol = 1e-12 A, then 1 Ω ties "
     "(`op_checked` in `scripts/frontend.py`; `python sink_options.py only <entry>` re-runs single entries)"),
    ("with each noise run's operating point checked against its AC run (`fe_gain_scan.json`, "
     "`fe_gain_options.json`) |",
     "with each case's operating points checked (`op_checked` in `scripts/frontend.py`) and each noise run's "
     "against its AC run (`fe_gain_scan.json`, `fe_gain_options.json`) |"),
]


def main() -> None:
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    assert "\r" not in text
    if "`op_checked` in `scripts/frontend.py`" in text:
        sys.exit("already patched: refusing a second run")
    assert text.count(START) == 1 and text.count(END) == 1
    a, b = text.index(START), text.index(END) + len(END)
    text = text[:a] + PITFALL + text[b:]
    for e in EDITS:
        old, new = e[0], e[1]
        n = e[2] if len(e) > 2 else 1
        c = text.count(old)
        assert c == n, (c, n, old[:90])
        text = text.replace(old, new)
    print(f"{len(EDITS) + 1} edits applied to {path.name}")
    path.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
