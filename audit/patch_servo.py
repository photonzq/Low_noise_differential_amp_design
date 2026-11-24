"""Patch of low_noise_preamp.md: why the front ends' common-mode servo is there, and its clamp (23 November
2026; after patch_jfe150_sink.py).

scripts/servo_check.py (sim/results/servo_check.json; rounded in numbers_s4a.json, '4.2 servo check'):
the front ends with the sinks' reference fixed instead of servoed, at the servo's value (the same operating
point, bandwidth and noise), at the design value, +-20 mV, +25 K and at -8 and +3 V of input common mode;
and the servo loop opened and swept from -14 to +14 V, and closed from the sinks' bases at +14 V.  The
second, latched state that the first version reported without the clamp is not reproduced: the servo's
error has one zero and its restoring sign everywhere, also with the sinks saturated.  The clamp is kept
for the sinks' current and R_T's dissipation.  The two sentences of Section 4.2 that estimated the drift
from V_BE alone and from an assumed 3 % error give way to the simulated figures.

Every edit is an exact-string replacement whose old text occurs once.  A second run is refused.
Usage: python patch_servo.py <path to low_noise_preamp.md>
"""
from __future__ import annotations

import sys
from pathlib import Path

EDITS: list[tuple] = [
    # ---- Section 4.2: the error without a servo, now simulated below ---------------------------------------
    (r"In H, the sink's $V_{BE}$ falls by 1.7 mV/K (the MMBT3904 model at its operating point, "
     r"`fe_closed_forms.json`), so its current rises by 1.7 mV / 2 V ≈ 0.09 % per kelvin; the outputs move by "
     r"4.9 mV per kelvin, in H and in L alike (the simulated drift of Section 4.6). An error of 3 %, an assumed "
     r"figure, would put H's outputs 0.17 V and L's 0.46 V away from the sources.",
     "How far the outputs move without a servo, simulated, is below."),
    # ---- Section 4.2: why a servo --------------------------------------------------------------------------
    ("make the integrator lower the sinks' reference, so the sinks take less current.\n\nWhat the servo does not do:",
     "make the integrator lower the sinks' reference, so the sinks take less current.\n\n"
     r"**Why a servo, and not a fixed reference.** The servo is not in the signal path: with the sinks' "
     r"reference fixed at the value the servo settles to, the operating point is the same, and the front ends' "
     r"bandwidth and noise are the same to every printed digit (`scripts/servo_check.py`, "
     r"`sim/results/servo_check.json`). What it does is hold the outputs' DC level at the sources' while three "
     r"things move it that a fixed reference cannot follow. Simulated with the reference fixed instead (H at a "
     r"gain of 100, L at 201):" "\n\n"
     r"- **The right reference is not known in advance.** The reference at which the sinks take exactly "
     r"$NI_D + I_{BS}$ lies 0.28 V above its design value, $V_M + V_{RT}$ + 0.66 V, for H and 1.94 V above it "
     r"for L: the sinks' base currents (β = 119 and 72 in the models) drop 0.18 V and 1.70 V across the 1 kΩ "
     r"through which the reference feeds the bases, their $V_{BE}$ is 0.07 V and 0.15 V above 0.66 V, and "
     r"$R_T$ carries their base current too (0.02 and 0.09 V). At the design value, H's outputs sit 0.68 V "
     r"below their sources and L's 3.43 V below; each 20 mV of error in the reference, or in a sink's "
     r"$V_{BE}$, moves them by 49 mV (H) and 34 mV (L)." "\n"
     r"- **Temperature.** 25 K above 27 °C moves them by 0.16 V (H) and 0.44 V (L), 6.5 and 17.5 mV/K: the "
     r"sinks' $V_{BE}$ falls, and their β rises, which lowers the drop across the 1 kΩ by 16 mV (H) and 128 mV "
     r"(L) over the 25 K." "\n"
     r"- **The input's common mode.** $R_{UP}$'s current, part of what the sinks must take, falls by 69 µA per "
     r"volt of input common mode, as $1/(R_{UP} + R_{BS})$, while a fixed sink's own current rises with its "
     r"collector voltage, by 16 µA/V (H) and 241 µA/V (L) (the Early effect). The outputs move by 43 mV (H) and "
     r"77 mV (L) per volt of common mode: 0.70 V over H's range of −12.8 to +3.7 V and 0.97 V over L's of −9.0 "
     r"to +3.6 V." "\n\n"
     r"With the servo, the outputs stay within 5 µV of their sources in every one of these cases. The offsets "
     r"are common mode, so S2 removes them and none reaches the signal. What they cost is the front end's DC "
     r"operating point: the op amps' output swing and the input's common-mode range shrink by as much, and a "
     r"build without the servo would need its sinks' reference trimmed, front end by front end, and would still "
     r"drift with temperature and follow the common mode. A stiffer reference would remove the base-current "
     r"parts, not the $V_{BE}$ and not the common mode. The servo is therefore kept, not for gain, noise or "
     r"bandwidth, which it does not touch, but so that the DC operating point is the designed one without a "
     r"trim, in L above all." "\n\n"
     "What the servo does not do:"),
    # ---- Section 4.2: the clamp, and the latch that is not there ---------------------------------------------
    (r"Without the limit, ngspice also found a latched state in which the integrator had driven the sinks' bases "
     r"above their collectors. In that state the sinks are saturated, raising the base no longer lowers the "
     r"current, the loop's sign reverses, and the integrator stays at its limit. A build needs the same limit and "
     r"a defined start-up state. It would use:",
     r"The limit is not needed for the loop's stability. With the loop opened and the reference swept from "
     r"−14 V to +14 V, the error $e$ crosses zero once, at −12.06 V for H and −6.40 V for L, rising there (the "
     r"servo's equilibrium), and keeps its restoring sign everywhere else: negative below, so that the servo "
     r"raises the reference, and positive above, also where the sinks saturate (from a reference of +2.3 V for "
     r"H and +9.9 V for L). A saturated sink takes far more current than it should, since its emitter then "
     r"follows the source node, so the servo still lowers its reference. Solved from no `.nodeset` and from the "
     r"sinks' bases at +14 V, with the limit or with only an op-amp integrator's ±14 V, the closed loop reaches "
     r"the same state in every case (`scripts/servo_check.py`). The first version of this note reported a "
     r"second, latched state with the sinks saturated; it is not reproduced, and its decks are not archived (it "
     r"was most likely ngspice's transient-op fallback; Appendix). The limit is kept for the parts: it bounds "
     r"the sinks' current during start-up and overloads. At its upper end H's sinks take 21 mA and $R_T$ "
     r"dissipates 81 mW (11 mA and 22 mW at the operating point), where an integrator free to reach +14 V would "
     r"drive 76 mA and 1.06 W; L's take 65 mA and 0.41 W (61 mA and 0.37 W) against 154 mA and 2.3 W. A build "
     r"would use:"),
    ("The servo's output must be limited, here to between", "The servo's output is limited, here to between"),
    ("- its output range limited by its supply or by a clamp, then the RC filter to the sinks' bases.",
     "- its output range limited by a clamp to the window above, then the RC filter to the sinks' bases."),
    # ---- Appendix ---------------------------------------------------------------------------------------------
    ("- **A servo with two states.** The common-mode servo of the sinks has a second, latched state with the sinks "
     "saturated, where the loop's sign reverses; its output is clamped (Section 4.2).",
     "- **A latch that was not there.** The first version of this note reported that the sinks' common-mode servo, "
     "without a limit on its output, had a second, latched state with the sinks saturated. It is not reproduced: "
     "the servo's error has a single zero, and the closed loop solved from the sinks' bases at +14 V returns to "
     "the normal state (Section 4.2, `scripts/servo_check.py`). The decks that showed it are not archived; it was "
     "most likely the transient-op fallback described above (\"An operating point that is not one\")."),
    # ---- Section 8, Files ---------------------------------------------------------------------------------------
    ("| `scripts/sink_power.py` | Section 4.2.1, Table 5a, and Section 4.6:",
     "| `scripts/servo_check.py` | Section 4.2: what the common-mode servo sets, from the front ends with the "
     "sinks' reference fixed instead (at the servo's value, at the design value, ±20 mV, +25 K, the input's "
     "common mode), and whether it can latch (the loop opened and swept from −14 to +14 V; the closed loop from "
     "the sinks' bases at +14 V) (`servo_check.json`) |\n"
     "| `scripts/sink_power.py` | Section 4.2.1, Table 5a, and Section 4.6:"),
]


def main() -> None:
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    assert "\r" not in text
    if "Why a servo, and not a fixed reference" in text:
        sys.exit("already patched: refusing a second run")
    for e in EDITS:
        old, new = e[0], e[1]
        n = e[2] if len(e) > 2 else 1
        c = text.count(old)
        assert c == n, (c, n, old[:90])
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"{len(EDITS)} replacements applied to {path.name}")


if __name__ == "__main__":
    main()
