"""Patch of low_noise_preamp.md: the front ends without the common-mode servo (23 November 2026; after
patch_servo.py).

The sinks' common base reference becomes a fixed voltage, adjusted once (frontend.sink_reference, in the
simulations for every circuit; in the Monte Carlo for every trial); every new-design simulation was re-run
without the servo.  Section 4.2 keeps Kirchhoff's law at the source node, the adjustment and what it does not
follow (temperature, the input's common mode); the servo, corrected, moves to a new Appendix B as an option,
and the ngspice appendix becomes Appendix A.  Eq. (8b) becomes (B.1).

The block of Section 4.2 from "**The common-mode servo.**" to the build's last item is replaced as a whole
(both ends asserted); every other edit is an exact-string replacement whose old text occurs the stated number
of times (once unless given); the remaining references to "the Appendix" become "Appendix A".  A second run
is refused.  Usage: python patch_noservo.py <path to low_noise_preamp.md>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

START = "**The common-mode servo.** Each source node obeys Kirchhoff's current law,"
END = "- its output range limited by a clamp to the window above, then the RC filter to the sinks' bases.\n"

MAIN = r"""**The sinks' reference.** Each source node obeys Kirchhoff's current law,

$$
I_{sink} = N I_D + I_{BS} + I_{R_F},
\tag{8a}
$$

where the integrator fixes the JFETs' current $NI_D = (V_P - V_{ref})/R_D$ and $R_{UP}$ fixes the bootstrap current $I_{BS}$. Whatever the sink takes beyond these two must come from the op amp through $R_F$, and the output sits at $v_o = v_s + R_F I_{R_F}$. Nothing else in the loop defines this DC level. The two sinks' common base reference (vsink in Figure 7) is therefore adjusted once, with a trimmer, until the outputs sit at their sources; the mean DC current in $R_F$ is then zero, and the outputs' mean sits $V_{S0}$ above the input's common mode, +0.36 V for H and +0.56 V for L. The adjusted reference is −12.06 V for H and −6.40 V for L, 0.28 V and 1.94 V above its design value $V_M + V_{RT}$ + 0.66 V: the sinks' base currents (β = 119 and 72 in the models) drop 0.18 V and 1.70 V across the 1 kΩ of the reference's filter, their $V_{BE}$ is 0.07 V and 0.15 V above 0.66 V, and $R_T$ carries their base current too (0.02 and 0.09 V). At the design value, unadjusted, H's outputs would sit 0.68 V below their sources and L's 3.43 V below. In the simulations every circuit's reference is adjusted in the same way, numerically, to 1 µV (`sink_reference` in `scripts/frontend.py`, `sim/results/sink_reference.json`), and in the Monte Carlo of Section 6.4 every trial's separately.

The adjustment holds at its own temperature and input common mode (`scripts/servo_check.py`, `sim/results/servo_check.json`):

- **Temperature.** 25 K above 27 °C moves the outputs by 0.16 V (H) and 0.44 V (L), 6.5 and 17.5 mV/K: the sinks' $V_{BE}$ falls, and their β rises, which lowers the drop across the 1 kΩ by 16 mV (H) and 128 mV (L) over the 25 K.
- **The input's common mode.** $R_{UP}$'s current, part of what the sinks must take, falls by 69 µA per volt of input common mode, as $1/(R_{UP} + R_{BS})$, while a sink's own current rises with its collector voltage, by 16 µA/V (H) and 241 µA/V (L) (the Early effect). The outputs move by 43 mV (H) and 77 mV (L) per volt of common mode: 0.70 V over H's range of −12.8 to +3.7 V and 0.97 V over L's of −9.0 to +3.6 V.
- **The reference's own drift.** Each 20 mV of it, or of a sink's $V_{BE}$, moves the outputs by 49 mV (H) and 34 mV (L).

These shifts are common mode: S2 removes them, and none reaches the signal. What they cost is the op amps' output swing and the input's common-mode range, by as much. A stiffer reference would remove the base-current parts, not the $V_{BE}$ and not the common mode. A mismatch $\Delta I$ between the two sinks' currents is not common mode: it appears as a differential output offset $\Delta I\,R_F$, an assumed 0.05 % of 11 mA, 5.5 µA, giving 2.75 mV at H's outputs and 27.5 µV referred to the input, which the offset trim of Section 4.6 removes. A slow servo of the reference would hold the outputs at their sources at every temperature and common mode, without the trimmer, and might help, L above all; Appendix B describes it, with its limits. The front ends here do without it.
"""

APPENDIX_B = r"""## Appendix B. A common-mode servo for the sinks' reference

The two sinks of each front end share a fixed base reference, adjusted once (Section 4.2), which holds the outputs at their sources only at the temperature and the input common mode of the adjustment. A slow common-mode servo of the reference would hold them there at every temperature and common mode, and would replace the trimmer. An earlier version of this design had one; what was worked out for it is kept here, corrected, as an option (`scripts/servo_check.py`, `sim/results/servo_check.json`; the servo is `FE.cm_servo` in `scripts/frontend.py`).

**What it would do.** It senses the common part of the DC voltage across the two feedback resistors,

$$
e = \tfrac12\left[(v_{oa} - v_{sa}) + (v_{ob} - v_{sb})\right] = \tfrac12 R_F\,(I_{R_F,a} + I_{R_F,b}),
\tag{B.1}
$$

integrates it, and lowers or raises the sinks' reference until $e$ = 0: the adjustment of Section 4.2, made continuously. The sign is such that outputs above their sources (current flowing from the op amps into the source nodes) make the integrator lower the reference, so the sinks take less current. It settles to the adjusted reference of Section 4.2 to within 1 µV, and with the reference fixed at that value the front ends' operating point, bandwidth and noise are the same to every printed digit: the servo is not in the signal path. Where the adjusted fixed reference leaves the outputs 0.16 V (H) and 0.44 V (L) away from their sources at 25 K above 27 °C, and 43 and 77 mV away per volt of input common mode (Section 4.2), the servo keeps them within 5 µV.

What it would not do:

- **It does not correct a difference between the sinks.** It moves both sinks together, so the differential offset $\Delta I\,R_F$ of a mismatch between them (Section 4.2) remains for the offset trim of Section 4.6.
- **It does not act on signals.** An input common-mode signal moves the sources and the outputs together, so $e$ does not change. Its loop would cross over at about 0.4 Hz (below), far below any signal of interest.
- **Its noise would move both sinks together,** i.e. in common mode. S2 rejects it; only the sinks' mismatch converts a small part of it to a differential signal.

**The loop.** In the simulations the servo is ideal. $e$ drives a transconductance $G_{INT}$ of 1 µS into $C_{INT}$ = 1 µF, an integrator with unity gain at 1 µS/(2π × 1 µF) = 0.16 Hz, and its output sets the reference through the same 1 kΩ and 10 µF as the fixed reference, a 1/(2π × 1 kΩ × 10 µF) = 16 Hz filter that keeps the integrator's noise from the sinks. A change of the reference changes each sink's current by $\Delta V/R_T$ and each output by $(R_F/R_T)\,\Delta V$: 500 Ω/181.8 Ω = 2.75 V per volt for H, 249 Ω/98.4 Ω = 2.53 for L. The loop therefore crosses over at 2.75 × 0.16 Hz = 0.44 Hz for H (0.40 Hz for L), where the 16 Hz filter takes 1.6° of phase, leaving 88° of phase margin (`scripts/numbers_s4a.py`).

**No latch, but a limit.** The servo's output would be limited, here to between $V_M$ + 1 V and $V_M + V_{RT}$ + 3 V: $V_M$ + 5 V for H and $V_M$ + 9 V for L, around the adjusted references at $V_M$ + 2.94 V (H) and $V_M$ + 8.60 V (L). The limit is not needed for the loop's stability. With the loop opened and the reference swept from −14 V to +14 V, the error $e$ crosses zero once, at −12.06 V for H and −6.40 V for L, rising there (the servo's equilibrium), and keeps its restoring sign everywhere else: negative below, so that the servo raises the reference, and positive above, also where the sinks saturate (from a reference of +2.3 V for H and +9.9 V for L). A saturated sink takes far more current than it should, since its emitter then follows the source node, so the servo still lowers its reference. Solved from no `.nodeset` and from the sinks' bases at +14 V, with the limit or with only an op-amp integrator's ±14 V, the closed loop reaches the same state in every case. The first version of this note reported a second, latched state with the sinks saturated; it is not reproduced, and its decks are not archived (it was most likely ngspice's transient-op fallback, Appendix A). The limit is there for the parts: it bounds the sinks' current during start-up and overloads. At its upper end H's sinks would take 21 mA and $R_T$ would dissipate 81 mW (11 mA and 22 mW at the operating point), where an integrator free to reach +14 V would drive 76 mA and 1.06 W; L's would take 65 mA and 0.41 W (61 mA and 0.37 W) against 154 mA and 2.3 W. For L the upper end is tight: at −8 V of input common mode the servo needs $V_M$ + 8.99 V, against the limit's $V_M$ + 9 V, so for L's full range the limit would be set higher, or the 1 kΩ that carries the bases' 1.7 mA made smaller. A build would use:

- a precision, low-offset op amp as the integrator, comparing the average of the two outputs with the average of the two source nodes;
- four equal resistors of about 100 kΩ for the two averages; they load the nodes negligibly, and each adds $\sqrt{4kT/100\ \mathrm{k\Omega}}$ = 0.4 pA/√Hz into a low-impedance source node;
- its output range limited by a clamp to the window above, then the RC filter to the sinks' bases.

**Overloads.** During the threefold overload of Section 6.5 the two op amps clip at different levels, and the outputs' mean (+0.23 V) leaves the sources' mean (+0.35 V). A servo would see this −0.12 V as its error and integrate it at $G_{INT}e/C_{INT}$ = 0.12 V/s: 2.4 µV over the 20 µs simulated, but after an overload of one second it would have moved the reference by 0.12 V, i.e. the outputs' common mode by $R_F/R_T$ = 2.75 times that, 0.33 V, which would then decay with the loop's time constant $(C_{INT}/G_{INT})(R_T/R_F)$ = 0.36 s (`overload_numbers.json`). S2 rejects this common-mode shift, but it uses up swing; a build should freeze the servo while an overload detector is active. Its power-on behaviour is not simulated.

"""

EDITS: list[tuple] = [
    # ---- the overview ----------------------------------------------------------------------------------------
    ("Section 7 lists what is not verified, and the Appendix collects the ngspice pitfalls met on the way.",
     "Section 7 lists what is not verified. Appendix A collects the ngspice pitfalls met on the way, and Appendix B "
     "describes a common-mode servo that the front ends could add."),
    # ---- Table 5 ----------------------------------------------------------------------------------------------
    ("| Current sink | MMBT3904, $R_T$ 182 Ω (2 V) to −15 V | PZT3904 (SOT-223), $R_T$ 98.4 Ω (6 V, 1 W) to −15 V "
     "(Section 4.2.1) |\n",
     "| Current sink | MMBT3904, $R_T$ 182 Ω (2 V) to −15 V | PZT3904 (SOT-223), $R_T$ 98.4 Ω (6 V, 1 W) to −15 V "
     "(Section 4.2.1) |\n"
     "| Sinks' base reference | −12.06 V, adjusted once (Section 4.2) | −6.40 V, adjusted once |\n"),
    # ---- Section 4.2 ------------------------------------------------------------------------------------------
    ("A slow common-mode servo sets the two sinks' common base reference (below).",
     "The two sinks share one base reference, a fixed voltage adjusted once (below)."),
    ("The base is held at AC ground by the servo's filter,", "The base is held at AC ground by its reference's filter,"),
    ("vsink (the common-mode servo's output)", "vsink (the sinks' adjusted base reference)"),
    # ---- Section 4.6 ------------------------------------------------------------------------------------------
    (r"A sink's current depends on its $V_{BE}$. The servo corrects the two sinks together, not their difference. "
     r"A temperature difference $\Delta T$ between them therefore leaves a current difference, which flows through "
     r"$R_F$ (Section 4.2) and appears at the input with the weight $R_F/G$:",
     r"A sink's current depends on its $V_{BE}$. A temperature change common to the two sinks moves the outputs in "
     r"common mode (Section 4.2); a temperature difference $\Delta T$ between them leaves a current difference, which "
     r"flows through $R_F$ and appears at the input with the weight $R_F/G$:"),
    # ---- Section 6.1 ------------------------------------------------------------------------------------------
    ("The sink's base is held at AC ground by the servo's filter.", "The sink's base is held at AC ground by its reference's filter."),
    # ---- Section 6.4 ------------------------------------------------------------------------------------------
    ("The common-mode servo plays no part, since a common-mode signal leaves its error signal, Eq. (8b), unchanged. ", ""),
    # ---- Section 6.5 ------------------------------------------------------------------------------------------
    (r"during the overload. The common-mode servo sees this −0.12 V as its error $e$ and integrates it, with its "
     r"transconductance $G_{INT}$ = 1 µS into $C_{INT}$ = 1 µF (Section 4.2), at $G_{INT}e/C_{INT}$ = 0.12 V/s, which "
     r"is 2.4 µV over 20 µs but would matter for an overload lasting seconds (below).",
     "during the overload; with the fixed sink reference nothing integrates this, and it ends with the overload (a "
     "servo of the reference would integrate it: Appendix B)."),
    (r"- **Overloads lasting seconds.** Because the op amps clip unequally, the common-mode servo (Section 4.2) "
     r"integrates a −0.12 V error during an overload. After one second it would have moved the sinks' reference by "
     r"$G_{INT}e\,(1\ \mathrm{s})/C_{INT}$ = 0.12 V, i.e. the outputs' common mode by $R_F/R_T$ = 500 Ω/182 Ω = 2.75 "
     r"times that, 0.33 V, which then decays with the servo loop's time constant $(C_{INT}/G_{INT})(R_T/R_F)$ = 0.36 s "
     r"(`overload_numbers.json`). S2 rejects this common-mode shift, but it uses up swing. A build should freeze the "
     r"servo while an overload detector is active." "\n", ""),
    # ---- Section 7 --------------------------------------------------------------------------------------------
    ("the overload indicators, the power-on behaviour of the common-mode servo, the thermal coupling",
     "the overload indicators, the thermal coupling"),
    # ---- Section 8, Files -------------------------------------------------------------------------------------
    ("| `scripts/frontend.py` | the front ends H and L as a netlist generator (`FE`, `CASES`), and their checks:",
     "| `scripts/frontend.py` | the front ends H and L as a netlist generator (`FE`, `CASES`), the sinks' adjusted "
     "reference (`sink_reference`, `sink_reference.json`; Section 4.2), and their checks:"),
    ("| `scripts/servo_check.py` | Section 4.2: what the common-mode servo sets, from the front ends with the sinks' "
     "reference fixed instead (at the servo's value, at the design value, ±20 mV, +25 K, the input's common mode), "
     "and whether it can latch (the loop opened and swept from −14 to +14 V; the closed loop from the sinks' bases "
     "at +14 V) (`servo_check.json`) |",
     "| `scripts/servo_check.py` | Section 4.2 and Appendix B: the sinks' fixed reference against the servo of "
     "Appendix B (at the servo's value, at the design value, ±20 mV, +25 K, the input's common mode), and whether "
     "the servo can latch (the loop opened and swept from −14 to +14 V; the closed loop from the sinks' bases at "
     "+14 V) (`servo_check.json`) |"),
    ("and 6–7 with the Appendix:", "and 6–7 with the appendices:"),
    ("a numerical failure described in the Appendix)", "a numerical failure described in Appendix A)"),
    # ---- Appendix A -------------------------------------------------------------------------------------------
    ("the normal state (Section 4.2, `scripts/servo_check.py`).", "the normal state (Appendix B, `scripts/servo_check.py`)."),
]


def main() -> None:
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    assert "\r" not in text
    if "## Appendix B." in text:
        sys.exit("already patched: refusing a second run")
    # Section 4.2's servo block -> the fixed, adjusted reference
    assert text.count(START) == 1 and text.count(END) == 1
    a, b = text.index(START), text.index(END) + len(END)
    text = text[:a] + MAIN + text[b:]
    for e in EDITS:
        old, new = e[0], e[1]
        n = e[2] if len(e) > 2 else 1
        c = text.count(old)
        assert c == n, (c, n, old[:90])
        text = text.replace(old, new)
    # Appendix B, before the references
    anchor = "\n---\n\n## References"
    assert text.count(anchor) == 1
    text = text.replace(anchor, "\n---\n\n" + APPENDIX_B.rstrip("\n") + "\n" + anchor)
    # every remaining "Appendix" not followed by A or B is the ngspice appendix
    text, n = re.subn(r"\bAppendix\b(?! [AB]\b)", "Appendix A", text)
    print(f"{len(EDITS) + 2} edits and {n} references to Appendix A applied to {path.name}")
    path.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
