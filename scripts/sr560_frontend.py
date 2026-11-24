"""The SR560's front end, as read from its schematic (SR560 manual, Rev. 3.1, 4/2023, sheet 560_1F.SCH,
manual p. 47 of the PDF), simulated in ngspice to see where its noise comes from.

Parts (schematic references):
  U106 = NPD5564 dual JFET (2N5564 pair; Linear Systems' 2N5564 card, calibrated in models.py)
  drains: R131 = R117 = 499 ohm from a node fed from +10 V through R119 = 165 ohm, C113 = 2.2 uF;
          R120 = 100 k from drain B to ground; C108 = 33 pF and R121 = 75 k (offset trim, its pot
          at 0 V here) at drain A
  sources: R113 = R114 = 110 ohm, R115 = R128 = 909 ohm, R135 = R137 = 10 ohm to the tail node,
          P101 (100 ohm CMRR trim) between the 909-ohm ends with its wiper on the tail (set to
          the middle: two 50-ohm halves); R111 = 1 k (+ P102, 20 ohm rheostat, set to 10 ohm)
          from source A to ground; R112 = 10 ohm and R118 = 1 k from U102's output to source B
  gain relay K102: in the x10 position the tops of R115 and R128 are joined (its second pole
          applies the low-gain offset trim through R134 in the x2 position; not modelled)
  U102 = OP37: + input at drain A, - input at drain B, C109 = 33 pF from output to - input;
          R116 = 499 ohm from U102's output to C116 = 150 pF (to ground): in the x2 position K102
          feeds the next stage's 499-ohm attenuator from there (a division by 2), in the x10 position
          directly from U102's output; R136 = 100 k from the top of R115 to ground
  U103 = LF411 tail servo: R129 = R127 = 100 k from the drains to its - input (their mean),
          + input at the 6.2 V zener reference through R125 = 49.9 k with C112 = 0.1 uF; output
          to the tail through R130 = 100 ohm, R122 = 1 k from its output to -10 V; C110 = 6.8 pF
          from the drains' mean to the tail
  inputs: R101 = R102 = 100 M to ground

The op amps are behavioural (blocks.opn) with the data sheets' typical figures at +/-15 V and
25 C.  The documents are in ../refs/datasheets/opamp/ (see the README there); "p." is the printed
page, which is also the PDF page (PyMuPDF index = p. - 1) in both documents cited here.
  OP37: ADI_op37_datasheet.pdf, Analog Devices OP37 data sheet Rev. B (C00319-0-12/02(B)).
    e_n 3.0 nV/rtHz at 1 kHz, i_n 0.4 pA/rtHz at 1 kHz, A_VO 1800 V/mV (R_L >= 2 k, V_O = +/-10 V),
    slew 17 V/us (R_L >= 2 k), GBW 63 MHz at f_O = 10 kHz: p. 3, Specifications, OP37A/E typ.
    1/f corners 2.7 Hz (voltage) and 140 Hz (current): stated on TPC 2 and TPC 8, p. 7.
    Modelling choices, not data-sheet values: fp2 = 40 MHz, rout = 20 ohm, vsat = 1.5 V, c1.  The
    data sheet gives R_O = 70 ohm and GBW = 40 MHz at f_O = 1 MHz (p. 3); its TPC 18 (p. 8) has
    |A| = 5 at 5.2 MHz with 71 deg of phase margin, where this model reaches |A| = 5.2 at 11.6 MHz
    (sr560_bw_check.py fits the plot and runs the chain with the fitted response).  The schematic
    sheets label U102, U201, U305 and U403 OP37; the manual's parts list (PDF p. 43) lists them as
    OPA37 (SRS 3-00382-340); TI's OPA27/OPA37 data sheet is archived as TI_opa37_datasheet.pdf.
  LF411: TI_lf411-n_datasheet.pdf, TI SNOSBH6E (LF411-N, the National Semiconductor LF411, Rev. E,
    Oct 2014, no longer published by TI).  GBW 4 MHz, slew 15 V/us, e_n 25 nV/rtHz (1 kHz,
    R_S = 100 ohm), i_n 0.01 pA/rtHz: p. 5, 6.6 AC Electrical Characteristics, LF411 typ;
    A_VOL 200 V/mV: p. 5, 6.5 DC Electrical Characteristics.  The 1/f corner fce = 100 Hz is a
    modelling choice: the data sheet states 50 Hz (p. 1, Features) and its Figure 18 (p. 8)
    gives 30-34 Hz (en^2 = 25^2 (1 + fc/f) through its readings at 10-200 Hz, listed in
    sr560_bw_check.json, datasheet_readings).  fp2 = 0,
    rout = 50 ohm, vsat = 1.5 V and c1 are modelling choices (V_O = +/-13.5 V into 10 k, p. 5).
    TI's current LF411 data sheet (TI_lf411_datasheet.pdf, SLOS011D, Oct 2025) describes a
    redesigned FET-input part (B1 4.5 MHz, slew 0.5 V/us, 10.8 nV/rtHz, 2 fA/rtHz: pp. 3-4);
    its JFET predecessor SLOS011C (TI_lf411_datasheet_SLOS011C.pdf, Oct 1997) gave 3 MHz,
    13 V/us, 18 nV/rtHz, 0.01 pA/rtHz (p. 3).

Usage: python sr560_frontend.py [gain10|gain2]
"""
from __future__ import annotations

import json
import math
import re
import sys

import numpy as np

import blocks
import models
import spice

# OP37, ADI data sheet Rev. B (ADI_op37_datasheet.pdf): gbw (63 MHz at 10 kHz), en (1 kHz), inoise
# (1 kHz), a0 (1800 V/mV), sr: p. 3, Specifications, OP37A/E typ; fce: p. 7, TPC 2; fci: p. 7,
# TPC 8.  fp2, rout (data sheet R_O = 70 ohm, p. 3), vsat, c1: modelling choices.
OP37 = blocks.opn("OP37", gbw=63e6, en=3.0e-9, inoise=0.4e-12, fce=2.7, fci=140.0, a0=1.8e6,
                  fp2=40e6, sr=17e6, c1=10e-12, vsat=1.5, rout=20.0)
# LF411, TI SNOSBH6E (TI_lf411-n_datasheet.pdf): gbw, sr, en (1 kHz), inoise: p. 5, 6.6 AC Electrical
# Characteristics, LF411 typ; a0 (200 V/mV): p. 5, 6.5.  fce = 100 Hz: modelling choice (data
# sheet: 50 Hz, p. 1; 30-34 Hz from Figure 18, p. 8).  fp2, rout, vsat, c1: modelling choices.
LF411 = blocks.opn("LF411", gbw=4e6, en=25e-9, inoise=0.01e-12, fce=100.0, a0=2e5, fp2=0,
                   sr=15e6, c1=10e-12, vsat=1.5, rout=50.0)


def front_end(gain10: bool = True, jfet: str = "2N5564", vtrim: float = 0.0) -> str:
    """Netlist body: inputs ina, inb; output out (U102's output).  vtrim is the voltage of the
    front-end offset trim P103 (wiper into drain A through R121)."""
    k102 = "RK102 xa xb 1m rnl\n" if gain10 else ""
    return f"""* --- SR560 front end (schematic 560_1F) ---
R101 ina 0 100Meg
R102 inb 0 100Meg
XJA da ina sa {jfet}
XJB db inb sb {jfet}
R119 p10 vtop 165
C113 vtop 0 2.2u
R131 vtop da 499
R117 vtop db 499
R120 db 0 100k
C108 da 0 33p
R121 da ptrim 75k
VTRIM ptrim 0 DC {vtrim:.6g}
R113 sa xa 110
R115 xa ya 909
R135 ya tail 10
R114 sb xb 110
R128 xb yb 909
R137 yb tail 10
RP101A ya tail 50
RP101B yb tail 50
{k102}R111 sa p102 1k
RP102 p102 0 10
R136 xa 0 100k
R112 sb fb 10
R118 fb out 1k
R116 out fo 499
C116 fo 0 150p
XU102 da db out p10 m10 OP37
C109 out db 33p
R129 da mid 100k
R127 db mid 100k
C110 mid tail 6.8p
VREF zref 0 DC 6.2
R125 zref ref 49.9k
C112 ref 0 0.1u
XU103 ref mid sv p10 m10 LF411
R130 tail sv 100
R122 sv m10 1k
VP p10 0 DC 10
VM m10 0 DC -10
"""


# The SR560 decks' operating point.  The decks first tied the inputs to their sources through 1 mOhm,
# which with abstol = 1e-15 A asks ngspice to resolve about 1e-18 V across them (the note's Appendix,
# "Tiny resistors and abstol"): on some decks ngspice's gmin and source stepping then failed, and its
# fallback, the transient op, returned a state that is not a DC solution (U103's reference input at
# 0.94 V instead of 6.2 V, U102 at its output limit), which spice.run does not flag, and whose value
# even varied between runs.  The input resistors are now 1 ohm (noiseless, as in the transients);
# besides, every deck starts Newton at the front end's normal state (NODESET: the zener reference
# and the servo's sensing node at 6.2 V, the drains at 6.2 V, the drain supply node at 8.5 V;
# sr560_chain.trimmed continues from converged solutions), and run_checked stops if the fallback
# still happens.  From either state Newton reaches the same, unique solution (sr560_variants.json,
# check_operating_point).
NODESET = ".nodeset v(ref)=6.2 v(mid)=6.2 v(da)=6.2 v(db)=6.2 v(vtop)=8.5\n"


def deck(title: str, body: str, src: str, control: str) -> str:
    return (f"* {title}\n{spice.OPTIONS}{spice.lib('jfets.lib')}{OP37}{LF411}{blocks.COMMON}"
            f"{src}{body}{NODESET}{control}.end\n")


def run_checked(name: str, text: str):
    """spice.run, then an error if the operating point fell back to the transient op."""
    f = spice.run(name, text)
    if spice.op_fallback(f):
        raise RuntimeError(f"{name}: the operating point fell back to the transient op")
    return f


GROUPS = [
    ("input JFETs", [r"^j\.xj[ab]\.j1", r"^r\.xj[ab]\.rx$"]),
    ("R113 + R114 (between the sources)", [r"^r113$", r"^r114$"]),
    ("R111 + P102 (source A to ground)", [r"^r111$", r"^rp102$"]),
    ("R118 + R112 (feedback)", [r"^r118$", r"^r112$"]),
    ("drain loads R131, R117", [r"^r131$", r"^r117$"]),
    ("U102 (OP37)", [r"^[rd]\.xu102\."]),
    ("tail network and servo", [r"^r115$", r"^r128$", r"^r135$", r"^r137$", r"^rp101[ab]$", r"^r130$",
                                r"^r122$", r"^r129$", r"^r127$", r"^r125$", r"^[rd]\.xu103\.", r"^r119$"]),
    ("other (R101, R102, R120, R121, R116, R136)", [r"^r10[12]$", r"^r120$", r"^r121$", r"^r116$", r"^r136$"]),
]


def group_of(name: str) -> str | None:
    for g, pats in GROUPS:
        if any(re.match(p, name) for p in pats):
            return g
    return None


def run_case(gain10: bool = True, jfet: str = "2N5564", edit=None, suffix: str = "") -> dict:
    """edit: an optional function applied to each deck's text before it is run (sr560_variants.py
    uses it for the corrected models); suffix: appended to the case tag, i.e. to the run folders
    and the curves file.  The defaults reproduce this script's own runs."""
    tag = f"sr560_{'x10' if gain10 else 'x2'}_{jfet}{suffix}"
    ed = edit or (lambda text: text)
    body = front_end(gain10, jfet)
    # operating point and differential gain (A = +1/2, B = -1/2)
    ctl = (".control\n" + spice.WR + "op\nprint v(da) v(db) v(sa) v(sb) v(tail) v(out) v(sv)\n"
           "print @j.xja.j1[id] @j.xjb.j1[id] @j.xja.j1[gm] @j.xjb.j1[gm]\n"
           "ac dec 20 1 100meg\nwrdata ac.txt v(out)\n.endc\n")
    f_ac = run_checked(f"{tag}/ac", ed(deck(tag, body, "VA ina0 0 DC 0 AC 0.5\nVB inb0 0 DC 0 AC -0.5\n"
                                               "RSA ina0 ina 1 rnl\nRSB inb0 inb 1 rnl\n", ctl)))
    ac = spice.read_table(f_ac / "ac.txt")
    f, h = ac["frequency"], ac["v(out)"]
    op = {k: spice.printed(f_ac, k) for k in ("v(da)", "v(db)", "v(sa)", "v(sb)", "v(tail)", "v(out)",
                                               "@j.xja.j1[id]", "@j.xja.j1[gm]")}
    # common-mode gain (A = B = 1)
    f_cm = run_checked(f"{tag}/cm", ed(deck(tag, body, "VA ina0 0 DC 0 AC 1\nRSA ina0 ina 1 rnl\n"
                                                   "RSB ina0 inb 1 rnl\n",
                                       ".control\n" + spice.WR + "ac dec 20 1 100meg\nwrdata cm.txt v(out)\n.endc\n")))
    cm = spice.read_table(f_cm / "cm.txt")["v(out)"]
    # noise, input A driven by VIN through 1 Ohm (noiseless), input B grounded
    f_n = run_checked(f"{tag}/noise", ed(deck(tag, body, "VIN ina0 0 DC 0 AC 1\nRSA ina0 ina 1 rnl\n"
                                                    "RSB 0 inb 1 rnl\n",
                                         spice.noise_control("out", "VIN", 0.1, 100e6, 20))))
    nz = spice.read_noise(f_n)
    fn, inn = nz["frequency"], nz["inoise_spectrum"]
    gain_n = np.abs(np.interp(np.log10(fn), np.log10(f), np.abs(h)))
    groups = {g: np.zeros_like(fn) for g, _ in GROUPS}
    other = {}
    for name, v in nz.items():
        if not name.startswith("onoise_") or name == "onoise_spectrum":
            continue
        base = name[len("onoise_"):]
        if re.search(r"_(1overf|thermal|rs|rd|id|flicker|1overfsw|idsw|rsw)$", base):
            continue
        g = group_of(base)
        if g is None:
            other[base] = float(spice.at(fn, v, 1e3))
            continue
        groups[g] += v ** 2
    res = dict(case=tag, op=op,
               gain_1k=float(spice.at(f, np.abs(h), 1e3)), f3db=spice.f3db(f, np.abs(h)),
               cmrr_db_1k=float(20 * math.log10(spice.at(f, np.abs(h), 1e3) / spice.at(f, np.abs(cm), 1e3))),
               en_in={str(f0): float(spice.at(fn, inn, f0)) for f0 in (1, 10, 100, 1e3, 1e4, 1e5, 1e6)},
               groups_1k={g: float(spice.at(fn, np.sqrt(v), 1e3) / spice.at(fn, gain_n, 1e3))
                          for g, v in groups.items()},
               unassigned_out_1k=other)
    spice.RESULTS.mkdir(parents=True, exist_ok=True)
    np.savez(spice.RESULTS / f"{tag}_curves.npz", f=f, h=h, cm=cm, fn=fn, inn=inn,
             **{f"g{i}": np.sqrt(groups[g]) / gain_n for i, (g, _) in enumerate(GROUPS)})
    return res


def main(args):
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    cases = args or ["gain10"]
    out = {}
    for c in cases:
        r = run_case(gain10=(c == "gain10"))
        out[r["case"]] = r
        print(json.dumps(r, indent=1))
    path = spice.RESULTS / "sr560_frontend.json"
    old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    old.update(out)
    path.write_text(json.dumps(old, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main(sys.argv[1:])
