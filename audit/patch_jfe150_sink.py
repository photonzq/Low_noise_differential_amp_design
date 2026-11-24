"""Patch of low_noise_preamp.md for the JFE150 current sink at a gain of 100, and the SR560 trim's
numerical procedure (23 November 2026; after patch_sr560.py).

The JFE150 sink's "latched operating point" of Sections 5.1 and 6.1 and Table 8a's "not converged" were
ngspice's transient-op fallback: with the sources tied to the gates through 1 mOhm and abstol = 1e-15 A,
every deck of that variant failed gmin and source stepping, and the end state of the fallback (source
nodes at -0.95 V, input gates conducting) is not a DC solution.  With 1-ohm ties the decks converge
(sink_options.py evaluate_checked; sim/results/sink_options.json, 'H100 | JFE150, 6 V': r_in 1 ohm,
op_note): 1.07 nV/rtHz at 10 kHz, -3 dB at 15.1 MHz, the margins of every other variant, source nodes at
+0.355 V (numbers_s6_7.json, table8a).  Section 2.2 gains a paragraph on how the offset trim is computed
(sr560_chain.trimmed; numbers_s1_3.json SR560_trim_secant_G1000).

Every edit is an exact-string replacement whose old text occurs once.  A second run is refused.
Usage: python patch_jfe150_sink.py <path to low_noise_preamp.md>
"""
from __future__ import annotations

import sys
from pathlib import Path

EDITS: list[tuple] = [
    # ---- Section 2.2: how the trim is computed ------------------------------------------------------
    ("1.07–1.17 MHz.\n\nThe CMRR of the reproduced chain with ideal matching,",
     "1.07–1.17 MHz.\n\n"
     "**How the trim is set numerically.** The model sets P103 as the manual's offset adjustment does, to null "
     "the front end's output, with one secant step between two operating points (`trimmed` in "
     "`scripts/sr560_chain.py`). With both inputs tied to 0 V through 1 Ω, ngspice solves the circuit's DC "
     "operating point with the wiper at $V_\\mathrm{TRIM}$ = 0 and at 1 V; at a gain of 1000 the front end's "
     "output is $v_0$ = −37.13 mV and $v_1$ = −13.17 mV. $V_\\mathrm{TRIM}$ acts only through R121's current "
     "into drain A, so the output is very nearly a straight line in it, of slope 23.96 mV/V, and the line's zero, "
     "$V_\\mathrm{TRIM} = -v_0/(v_1 - v_0)$ = 1.5497 V, nulls it: a third operating point there leaves −6.6 µV "
     "at the front end's output (0.65 µV at its input) and 0.63 mV at the chain's output "
     "(`sim/results/sr560_variants.json`, `scripts/numbers_s1_3.py`). Nothing is swept or optimized: two "
     "points fix a line, and the residual shows how little the output departs from one. That third solution, "
     "with the vernier's code scaled from the nominal stage gains so that the total gain is the selected one, "
     "is the state from which every noise and AC deck of the setting starts; each gain setting is trimmed in "
     "the same way.\n\n"
     "The CMRR of the reproduced chain with ideal matching,"),
    # ---- Section 5.1 ---------------------------------------------------------------------------------
    ("With a JFE150 as current sink at a gain of 100 (Section 6.1), every deck settled with the source nodes at "
     "−0.95 V. Only the AC response gave it away, with a bandwidth of 322 MHz instead of 15.0 MHz, and "
     "`scripts/sink_options.py` rejects such a result.",
     "With a JFE150 as current sink at a gain of 100 (Section 6.1), every deck fell back in the same way and "
     "settled with the source nodes at −0.95 V and the input gates conducting; only the AC response gave it "
     "away, with a bandwidth of 322 MHz instead of 15.0 MHz. The cause was the 1 mΩ resistors that tie the "
     "sources to the gates: with abstol = 1e-15 A they leave the operating point to rounding, as in the SR560 "
     "reproduction (Appendix). With 1 Ω ties the same decks converge, with the source nodes at +0.355 V and "
     "−3 dB at 15.1 MHz (`sim/results/sink_options.json`), and `scripts/sink_options.py` now evaluates a "
     "variant again with 1 Ω ties whenever the operating point of one of its decks falls back."),
    # ---- Section 6.1 and Table 8a ---------------------------------------------------------------------
    ("- **With a JFE150 sink at a gain of 100, ngspice found only a latched operating point.** In every deck the "
     "source nodes sat at −0.95 V, with the input gates conducting (Section 5.1). That variant was not "
     "pursued.\n",
     "- **The JFE150 sink at a gain of 100 needed 1 Ω ties.** With the sources tied to the gates through 1 mΩ, "
     "the operating point of every deck fell back to a state that is not a DC solution, with the source nodes "
     "at −0.95 V and the input gates conducting, which the first version of this note took for a latched state "
     "(Section 5.1, Appendix). With 1 Ω ties it gives 1.07 nV/√Hz, the margins of the other variants and −3 dB "
     "at 15.1 MHz.\n"),
    ("`scripts/numbers_s6_7.py`).*\n\n| Sink |",
     "`scripts/numbers_s6_7.py`). The JFE150 at a gain of 100 runs with the sources tied to the gates through "
     "1 Ω instead of 1 mΩ (Section 5.1).*\n\n| Sink |"),
    ("| 1.77 / 3.65 / 2.86 | not converged | 2.69 |",
     "| 1.77 / 3.65 / 2.86 | 1.07 | 2.69 |"),
    # ---- Appendix --------------------------------------------------------------------------------------
    ("AC and noise runs of the new design were unaffected, but transients stopped",
     "AC and noise runs of the new design's adopted front ends were unaffected, but transients stopped"),
    ("In the SR560 reproduction the same resistors made some operating points fail (next item); its decks now "
     "use 1 Ω.\n",
     "In the SR560 reproduction and with the JFE150 sink of Section 6.1 the same resistors made operating "
     "points fail (next item); those decks now use 1 Ω.\n"),
    ("The wrong operating point of Section 5.1's gain-30 variant is the same fallback.\n",
     "The two wrong operating points of Section 5.1, the gain-30 variant's noise deck and every deck of the "
     "JFE150 sink, are the same fallback; the JFE150 sink's decks converge with 1 Ω ties, which "
     "`scripts/sink_options.py` now uses for a variant whose decks fall back.\n"),
    # ---- Section 8, Files ------------------------------------------------------------------------------
    ("| `scripts/op_pitfall.py` | Section 5.1: the two wrong operating points, reproduced,",
     "| `scripts/op_pitfall.py` | Section 5.1: the two wrong operating points, ngspice's transient-op fallback "
     "in both, reproduced,"),
    ("and the chain's noise for each (`python sink_options.py chain`); results in `sink_options.json` |",
     "and the chain's noise for each (`python sink_options.py chain`); a variant whose decks' operating points "
     "fall back is evaluated again with 1 Ω ties (`python sink_options.py only <entry>` re-runs "
     "single entries); results in `sink_options.json` |"),
]


def main() -> None:
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    assert "\r" not in text
    if "How the trim is set numerically" in text:
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
