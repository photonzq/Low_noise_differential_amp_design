"""Standalone netlists in ../netlists/: the same text that the simulations use, with the model
libraries included by a path relative to the netlist (../sim/models/_lib/), a header that names
the circuit and its parts, and a control block for an AC sweep and a noise run.  Each file is run
once after writing (from its own folder) to check that it runs as written.

  sr560_front_end_x10.cir     the SR560's front end (Section 2), K102 at x10
  sr560_chain_gain1000.cir    the SR560 reproduction at a gain of 1000, low-noise mode
  front_end_H100.cir          front end H at a gain of 100 (Figure 7), inputs driven directly
  front_end_H10.cir           front end H at a gain of 10
  front_end_L200.cir          front end L (Figure 8)
  chain_H_gain1000.cir        the complete chain with front end H, total gain 1000
  chain_L_gain1000.cir        the complete chain with front end L, total gain 1000

They run in ngspice (ngspice -b <file>) after scripts/models.py has written sim/models/_lib/.
The op amps of the SR560 reproduction are behavioural (scripts/blocks.py) and are written into
the netlist itself.
Usage: python export_netlists.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import blocks
import chain
import frontend as F
import models
import spice
import sr560_chain as SC
import sr560_frontend as SF

OUT = spice.ROOT / "netlists"


def relative_includes(text: str) -> str:
    """Absolute .include paths of the prepared libraries -> paths relative to netlists/."""
    lib = spice.LIB.as_posix()
    return text.replace(f'.include "{lib}/', '.include "../sim/models/_lib/')


def write(name: str, header: str, deck: str) -> Path:
    OUT.mkdir(exist_ok=True)
    path = OUT / name
    body = relative_includes(deck)
    lines = body.splitlines()
    text = "* " + header.replace("\n", "\n* ") + "\n" + "\n".join(lines[1:]) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


CTL_FE = (".control\nset wr_singlescale\nset wr_vecnames\nop\nac dec 40 1 1g\nwrdata ac.txt v(oa) v(ob)\n"
          "noise v(oa,ob) VIN dec 20 1 100meg\nsetplot noise2\nprint onoise_total\n.endc\n")
CTL_CHAIN = (".control\nset wr_singlescale\nset wr_vecnames\nop\nprint v(out)\nac dec 40 1 300meg\n"
             "wrdata ac.txt v(out)\nnoise v(out) VIN dec 20 1 100meg\nsetplot noise2\n"
             "print onoise_total\n.endc\n")
SRC_NOISE = "VIN ina 0 DC 0 AC 1\nRIA ina ga 1m rnl\nRIB 0 gb 1m rnl\n"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    files = []
    # new front ends
    for case in ("H100", "H10", "L200"):
        p = F.CASES[case]
        head = (f"Front end {case} of the low-noise differential preamplifier note: {p.n} x {p.jfet} per side at "
                f"{p.id * 1e3:g} mA, LSBF862 cascodes bootstrapped {p.vbs:g} V above the source node,\n"
                f"THS4021 loop op amps, R_F {p.rf:g} ohm, R_G {p.rg:g} ohm (gain {p.gain:.4g}), C_I {p.ci * 1e12:g} pF, "
                f"C_X {p.cx * 1e12:g} pF, C_node {p.cnode * 1e12:g} pF.\n"
                "Input A driven (VIN, AC 1), input B grounded; outputs oa, ob.  Section 4.2 of the note.")
        files.append(write(f"front_end_{case}.cir", head, F.deck(p, f"front end {case}", SRC_NOISE, CTL_FE)))
    # complete chains
    for mode, g, tag in (("H_LN", 1000, "H"), ("L", 1000, "L")):
        s = chain.allocate(g, mode)
        head = (f"Complete chain of the low-noise differential preamplifier note, front end {s.fe}, total gain "
                f"{s.gain:.4g} (a3 {s.a3:g}, a4 {s.a4:g}, a5 {s.a5:g}), filters off.\n"
                f"S2 {chain.DA_OPAMP}, S3/S4 THS4021, F1/F2 THS4031 followers (bypassed), S5 THS3091.  Section 4.5.")
        files.append(write(f"chain_{tag}_gain1000.cir", head, chain.deck(s, f"chain {tag}", SRC_NOISE, CTL_CHAIN)))
    # SR560
    fe = SF.front_end(True)
    deck = (f"* sr560 front end\n{spice.OPTIONS}{spice.lib('jfets.lib')}{SF.OP37}{SF.LF411}{blocks.COMMON}"
            "VIN ina 0 DC 0 AC 1\nVB inb 0 DC 0\n" + fe + SF.NODESET +
            ".control\nset wr_singlescale\nset wr_vecnames\nop\nac dec 40 1 100meg\nwrdata ac.txt v(out)\n"
            "noise v(out) VIN dec 20 1 10meg\nsetplot noise2\nprint onoise_total\n.endc\n.end\n")
    files.append(write("sr560_front_end_x10.cir",
                       "SR560 front end, redrawn from SRS sheet 560_1F (manual Rev. 3.1), K102 at x10; NPD5564 as the\n"
                       "recalibrated 2N5564 card; OP37 and LF411 behavioural.  Section 2.1 of the note.", deck))
    s = SC.allocate(1000, "LN") if hasattr(SC, "allocate") else None
    if s is not None and hasattr(SC, "deck"):
        try:
            d = SC.deck(SC.trimmed(s, 1000) if hasattr(SC, "trimmed") else s, "sr560 chain",
                        "VIN ina 0 DC 0 AC 1\nVB inb 0 DC 0\n", CTL_CHAIN.replace("v(out)", "v(out)"))
            files.append(write("sr560_chain_gain1000.cir",
                               "SR560 reproduction, low-noise mode, gain 1000 (Section 2.2 of the note).", d))
        except Exception as e:  # noqa: BLE001
            print("sr560 chain netlist not written:", e)
    # run each once, from netlists/
    ok = True
    for f in files:
        out = spice.ng().run_deck(f)
        bad = [ln for ln in re.split(r"(?=std(?:out|err) )", out) if spice.ERRORS.search(ln)
               and "warning" not in ln.lower()]
        if "Transient op" in out:     # gmin and source stepping failed: not a DC solution (note, Appendix)
            bad.append("the operating point is ngspice's transient-op fallback")
        m = re.findall(r"inoise_total\s*=\s*([-+0-9.eE]+)", out)
        print(f"{f.name}: {'ran' if not bad else 'PROBLEMS: ' + bad[0][:120]}"
              + (f", output noise {float(m[-1]) * 1e3:.3g} mV rms (1 Hz to the sweep end)" if m else ""))
        ok &= not bad
        for junk in f.parent.glob("ac.txt"):
            junk.unlink()
    print("all netlists ran" if ok else "SOME NETLISTS FAILED")


if __name__ == "__main__":
    main()
