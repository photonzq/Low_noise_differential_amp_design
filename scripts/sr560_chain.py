"""The complete SR560 signal path reproduced in ngspice from its schematics (manual Rev. 3.1, sheets
560_1F, 560_2F, 560_3F and 560_4F), as the benchmark for the new design.

Path (schematic references):
  front end     sr560_frontend.front_end(): U106 (NPD5564), U102 (OP37), U103 (LF411); gain relay
                K102: x10 (U102's output feeds the next attenuator directly) or x2 (through R116,
                499 ohm, which halves the signal with the next stage's 499-ohm attenuator)
  U105          LT1028 at 1 + R123/R124 = 1 + 909/100 = 10.09 (C111 68 pF across R123); input
                attenuator R108 249, R109 150, R110 100 tapped by DG444 U101A-C (taps 1, 0.501, 0.200)
  U104          74HC4053 blanking switch, three sections in parallel  -> FRONT OUT
  filter 1      RC bank behind the 74HC4051 multiplexers U202/U203 (bypassed by DG444 U205D), LF356
                follower U204; attenuator R220 604, R221 200, R222 200 (U205A-C) into OP37 U201 at
                1 + R217/R215 = 1 + 845/200 = 5.23, with R229 4.3 k + C201 68 pF across R217
  filter 2      the same with U303 (LF356), U304, R318/R319/R320, OP37 U305 (R315 845, R313 200,
                R330 3.3 k + C301 6.8 pF), output through R328 10 ohm
  U402          LT1028 at 1 + R403/R404 = 1 + 845/200 (C401 47 pF across R403), attenuator
                R409 604, R410 200, R411 200 (U401)
  vernier       AD7528 multiplying DAC U405A with LF411 U404: modelled as an inverting stage with
                a 10-kohm ladder (input resistor 10 k / code) and its 10-kohm feedback resistor,
                code 1 (unity) or 1/2; R423 10 ohm after it
  U403/U406     OP37 U403 driving the LM6321 buffer U406 inside its loop, 1 + R408/R425 =
                1 + 422/100 = 5.22, attenuator R412 604, R413 200, R415 200 (U409), R437 220 between
                U403 and U406; the 50-ohm output through R438 49.9
Switch on-resistances (typical, room temperature): DG444 50 ohm, 74HC4053 and 74HC4051 at +/-6 V
about 70 ohm (the 4053's three parallel sections: 23 ohm); the multiplexers' 80 pF at the filter
node is included, as the manual says SRS does.
Op amps: behavioural (blocks.opn) with typical data-sheet figures at +/-15 V and 25 C; OP37 and LF411
as in sr560_frontend.py (sources there).  Documents in ../refs/datasheets/opamp/ (README there);
"p." is the printed page, equal to the PDF page (PyMuPDF index = p. - 1) unless stated.
  LT1028: ADI_lt1028_datasheet.pdf, LT1028/LT1128 data sheet Rev. D (1028fd, 10/15).  e_n 0.85
    nV/rtHz and i_n 1.0 pA/rtHz at 1 kHz, A_VOL 30 V/uV (R_L >= 2 k), slew 15 V/us (A_VCL = -1),
    GBW 75 MHz at f_O = 20 kHz: p. 3, Electrical Characteristics, LT1028AM/AC typ (non-A grade:
    0.9 nV/rtHz).  1/f corners 3.5 Hz (voltage; p. 1, Voltage Noise vs Frequency, typical) and
    250 Hz (current; p. 6, Current Noise Spectrum, typical).  Modelling choices: fp2 = 60 MHz,
    rout = 20 ohm (data sheet Z_O = 80 ohm, p. 3), vsat = 1.5 V (V_OUT +/-13.0 V into 2 k, p. 3),
    c1.  The data sheet's Gain, Phase vs Frequency plot (p. 8) has 20 dB of gain at about 2.6 MHz
    with about 45 deg of phase margin (also stated on p. 15), where this model has about 7.4 MHz.
  LF356: TI_lf356_datasheet.pdf, TI SNOSBH0D (LF15x/LF35x, Nov 2015).  GBW 5 MHz, slew 12 V/us,
    e_n 12 nV/rtHz at 1 kHz (15 at 100 Hz), i_n 0.01 pA/rtHz: p. 5, 6.5 AC Electrical
    Characteristics, LFx56 typ; A_VOL 200 V/mV: p. 6, 6.7.  fce = 100 Hz is not stated; the
    table's 15 and 12 nV/rtHz give 56 Hz, Figure 33 (p. 13) 10-160 Hz depending on the frequency
    read, since the plotted curve is not of the 1/f-plus-white form (sr560_bw_check.json,
    datasheet_readings).  fp2 = 0, rout = 50 ohm (Figure 17, p. 10: about 40 ohm open loop),
    vsat, c1: modelling choices.
  LM6321: TI_lm6321_datasheet.pdf, TI SNOSC10B (LM6121/LM6221/LM6321, National data sheet 9223,
    obsolete Oct 2011): -3 dB bandwidth 50 MHz typ (R_L = 50 ohm, C_L <= 10 pF): printed p. 4 = PDF
    page 5 (a cover page precedes it), AC Electrical Characteristics.  Modelled as an ideal unity
    buffer with a single 50 MHz pole (A_V1 0.990, R_O 3 ohm on printed p. 3 are not modelled;
    both lie inside U403's loop).

Gain allocation (not documented by SRS; inferred from the manual's description and its table of
noise against gain): low-noise mode: front end x10 from a gain of 100 up, gain placed as early as
possible; high-reserve mode: front end x2 and gain placed as late as possible; the vernier's
code 1/2 for a gain of 1.  Usage: python sr560_chain.py ac|noise|cmrr|all
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass

import numpy as np

import blocks
import models
import spice
import sr560_frontend as FE

# LT1028, data sheet Rev. D (ADI_lt1028_datasheet.pdf): gbw (75 MHz at 20 kHz), en, inoise (1 kHz),
# a0 (30 V/uV), sr: p. 3, Electrical Characteristics, A grade typ; fce: p. 1, Voltage Noise vs
# Frequency; fci: p. 6, Current Noise Spectrum.  fp2, rout (Z_O = 80 ohm, p. 3), vsat, c1: modelling.
LT1028 = blocks.opn("LT1028", gbw=75e6, en=0.85e-9, inoise=1.0e-12, fce=3.5, fci=250.0, a0=3e7,
                    fp2=60e6, sr=15e6, c1=10e-12, vsat=1.5, rout=20.0)
# LF356, TI SNOSBH0D (TI_lf356_datasheet.pdf): gbw, sr, en (1 kHz), inoise: p. 5, 6.5, LFx56 typ;
# a0 (200 V/mV): p. 6, 6.7.  fce = 100 Hz: modelling choice (no stated corner; 56 Hz from the
# table, 10-160 Hz from Figure 33, p. 13).  fp2 (none), rout, vsat, c1: modelling choices.
LF356 = blocks.opn("LF356", gbw=5e6, en=12e-9, inoise=0.01e-12, fce=100.0, a0=2e5, sr=12e6,
                   c1=10e-12, vsat=1.5, rout=50.0)
RON_DG444, RON_HC = 50, 70
TAPS_105 = (1.0, 0.501, 0.2004)          # R108/R109/R110
TAPS_5 = (1.0, 0.3984, 0.1992)           # 604/200/200


@dataclass
class SRSetting:
    fe10: bool
    t105: int          # index into TAPS_105
    t201: int
    t305: int
    t402: int
    t403: int
    dac: float = 1.0
    f1: tuple | None = None
    f2: tuple | None = None
    vtrim: float = 0.0
    nodeset: str | None = None   # the decks' .nodeset: None FE.NODESET, "" none, else this line
                                 # (trimmed(): the trimmed state's solution)

    @property
    def nominal(self) -> float:
        front = (10.18 if self.fe10 else 2.0 * 0.5) * TAPS_105[self.t105] * 10.09
        s = 5.225 * TAPS_5[self.t201] * 5.225 * TAPS_5[self.t305] * 5.225 * TAPS_5[self.t402]
        return front * s * self.dac * 5.22 * TAPS_5[self.t403]

    @property
    def tag(self) -> str:
        return (f"fe{'10' if self.fe10 else '2'}_{self.t105}{self.t201}{self.t305}{self.t402}{self.t403}"
                f"_dac{self.dac:g}").replace(".", "p")


def _att(pre: str, nin: str, nout: str, r: tuple, tap: int) -> str:
    """Three-resistor attenuator from nin to ground, tap selected by a DG444 section into nout."""
    r1, r2, r3 = r
    t = ["%s" % nin, f"{pre}t1", f"{pre}t2"][tap]
    return (f"R{pre}1 {nin} {pre}t1 {r1}\nR{pre}2 {pre}t1 {pre}t2 {r2}\nR{pre}3 {pre}t2 0 {r3}\n"
            f"R{pre}SW {t} {nout} {RON_DG444}\n")


def _filter(pre: str, nin: str, flt) -> str:
    """Filter bank node with the multiplexers' on-resistance and 80 pF; bypass through a DG444."""
    if not flt:
        return f"R{pre}BYP {nin} {pre}x {RON_DG444}\nC{pre}MUX {pre}x 0 80p\n"
    kind, fc = flt
    r = 15.8e3
    c = 1 / (2 * math.pi * r * fc)
    if kind == "LP":
        return (f"R{pre}F {nin} {pre}r {r}\nR{pre}MX {pre}r {pre}x {RON_HC}\nC{pre}F {pre}r 0 {c - 80e-12:.6g}\n"
                f"C{pre}MUX {pre}x 0 80p\n")
    return (f"C{pre}F {nin} {pre}r {c:.6g}\nR{pre}F {pre}r 0 {r}\nR{pre}MX {pre}r {pre}x {RON_HC}\n"
            f"C{pre}MUX {pre}x 0 80p\n")


def netlist(s: SRSetting) -> str:
    front = FE.front_end(s.fe10, vtrim=s.vtrim)
    k102o = "out" if s.fe10 else "fo"
    body = front + f"""* ---- U105 (LT1028, x10.09) with its input attenuator
{_att("A105", k102o, "p105", (249, 150, 100), s.t105)}XU105 p105 n105 o105 p10 m10 LT1028
R123 o105 n105 909
C111 o105 n105 68p
R124 n105 0 100
RU104 o105 ft {RON_HC / 3:g}
* ---- filter 1, LF356 follower U204, attenuator, OP37 U201 (x5.23)
{_filter("F1", "ft", s.f1)}XU204 F1x b1 b1 p10 m10 LF356
{_att("A201", "b1", "p201", (604, 200, 200), s.t201)}XU201 p201 n201 f1o p10 m10 OP37
R217 f1o n201 845
R229 f1o c201 4.3k
C201 c201 n201 68p
R215 n201 0 200
* ---- filter 2, LF356 follower U303, attenuator, OP37 U305 (x5.23)
{_filter("F2", "f1o", s.f2)}XU303 F2x b2 b2 p10 m10 LF356
{_att("A305", "b2", "p305", (604, 200, 200), s.t305)}XU305 p305 n305 o305 p10 m10 OP37
R315 o305 n305 845
R330 o305 c301 3.3k
C301 c301 n305 6.8p
R313 n305 0 200
R328 o305 f2o 10
* ---- U402 (LT1028, x5.23)
{_att("A402", "f2o", "p402", (604, 200, 200), s.t402)}XU402 p402 n402 o402 p10 m10 LT1028
R403 o402 n402 845
C401 o402 n402 47p
R404 n402 0 200
* ---- vernier: AD7528 ladder (10 k / code) and its 10-k feedback around LF411 U404
RDAC o402 n404 {10e3 / s.dac:.6g}
RFB o404 n404 10k
C407 o404 n404 3p
XU404 0 n404 o404 p10 m10 LF411
R423 o404 v403 10
* ---- U403 (OP37) with the LM6321 buffer U406 in its loop (x5.22), outputs
{_att("A403", "v403", "p403", (604, 200, 200), s.t403)}XU403 p403 n403 o403 p10 m10 OP37
R437 o403 i406 220
E406 b406 0 i406 0 1
R406P b406 c406 1 rnl
C406P c406 0 3.18n
E406B o406 0 c406 0 1
R408 o406 n403 422
R425 n403 0 100
R438 o406 out50 49.9
RL out50 0 1Meg
"""
    return body


def deck(s: SRSetting, title: str, src: str, control: str) -> str:
    return (f"* {title}\n{spice.OPTIONS}{spice.lib('jfets.lib')}{FE.OP37}{FE.LF411}{LT1028}{LF356}"
            f"{blocks.COMMON}{src}{netlist(s)}{FE.NODESET if s.nodeset is None else s.nodeset}{control}.end\n")


def all_nodes(folder) -> str:
    """A .nodeset line with the top-level node voltages that a deck's 'print all' wrote to its log
    (the deck's operating point; subcircuit-internal nodes are left out, so that the line also fits
    decks whose op-amp models differ, as in sr560_bw_check.py)."""
    import re
    log = (folder / "run.log").read_text(encoding="utf-8")
    pairs = [(n, v) for n, v in re.findall(r"stdout ([A-Za-z0-9_.]+) = ([-+0-9.eE]+)", log) if "." not in n]
    return ".nodeset " + " ".join(f"v({n})={v}" for n, v in pairs) + "\n"


# the last converged trimmed state of each (runs folder, front-end position): a starting point for the
# next setting's trim decks, whose front end is the same
_ANCHOR: dict = {}


def _op(name: str, make_text, starts: list, edit):
    """Run the deck make_text(nodeset) from each starting point in turn (a .nodeset line; None for
    FE.NODESET, "" for none) until ngspice's operating point does not fall back to the transient op;
    an error if it falls back, or the run fails, from every one."""
    seen, last = [], ""
    for ns in starts:
        if ns in seen:
            continue
        seen.append(ns)
        text = make_text(ns)
        try:
            f = spice.run(name, edit(text) if edit else text)
        except RuntimeError as e:          # e.g. a .nodeset node that this deck does not have
            last = str(e).splitlines()[-1][:200]
            continue
        if not spice.op_fallback(f):
            return f
        last = "fell back to the transient op"
    raise RuntimeError(f"{name}: no starting point gave an operating point ({last})")


# the sources reach the inputs through 1 ohm, noiseless (sr560_frontend.NODESET: 1 mOhm with
# abstol = 1e-15 A made ngspice's operating point fail on some decks)
SRC_DM = "VA ina0 0 DC 0 AC 0.5\nVB inb0 0 DC 0 AC -0.5\nRSA ina0 ina 1 rnl\nRSB inb0 inb 1 rnl\n"
SRC_CM = "VA ina0 0 DC 0 AC 1\nRSA ina0 ina 1 rnl\nRSB ina0 inb 1 rnl\n"


def allocate(g: int, mode: str = "LN") -> SRSetting:
    """Gain allocation (see the module docstring)."""
    front_opts = []
    for fe10 in (False, True):
        for t in range(3):
            front_opts.append((fe10, t, (10 if fe10 else 1) * [10, 5, 2][t]))
    stage = [5, 2, 1]
    # the vernier DAC is used only where the switched gains cannot make the gain (code 1 first,
    # then 0.8, then 1/2)
    for dac in (1.0, 0.8, 0.5):
        best = None
        for fe10, t105, fg in front_opts:
            if mode == "LN" and fe10 != (g >= 100):
                continue
            if mode == "HDR" and fe10:
                continue
            for a in range(3):
                for b in range(3):
                    for c in range(3):
                        for d in range(3):
                            tot = fg * stage[a] * stage[b] * stage[c] * stage[d] * dac
                            if abs(tot - g) > 1e-9:
                                continue
                            gains = (fg, stage[a], stage[b], stage[c], stage[d])
                            # LN: gain early (lexicographically largest); HDR: gain late
                            key = tuple(-x for x in gains) if mode == "LN" else gains
                            if best is None or key < best[0]:
                                best = (key, SRSetting(fe10, t105, a, b, c, d, dac))
        if best is not None:
            return best[1]
    raise ValueError(f"SR560 gain {g} not reachable in {mode}")


GAINS_LN = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]
GAINS_HDR = [10, 20, 50, 100, 200, 500, 1000, 2000]
# the manual's table (p. 21 of the manual, "Input Noise (nV/rtHz)" at each gain and mode)
MANUAL = {"LN": {1: 60, 2: 40, 5: 25, 10: 13, 20: 11, 50: 10, 100: 4, 200: 4, 500: 4, 1000: 4, 2000: 4,
                 5000: 4, 10000: 4, 20000: 4, 50000: 4},
          "HDR": {10: 25, 20: 25, 50: 25, 100: 20, 200: 18, 500: 15, 1000: 15, 2000: 10}}


def trimmed(s: SRSetting, g: float | None = None, runs: str = "sr560_chain", edit=None) -> SRSetting:
    """The setting with the front-end offset trim P103 set to null the front end's output (the
    adjustment of the manual's offset procedure) and, if g is given, the vernier code scaled so
    that the gain is the nominal g (the calibration the manual describes: the switched stages'
    lowest setting is 1.04, not 1, so the uncalibrated gains run up to 20 % high).  runs: the
    folder under ../sim/runs/ for the two operating-point decks (another script passes its own,
    so that this script's archived decks are not rewritten); edit: as in run_ac.
    The operating points start from converged ones (continuation): each deck is tried from the
    solution of the previous deck (VTRIM = 0 -> 1 V -> the trimmed state), then from the last
    converged trimmed state of the same runs folder and front-end position (_ANCHOR), then from
    those of the other runs folders (other models) with the same front-end position, then from
    FE.NODESET, then from none; the returned setting carries the trimmed state's solution as its .nodeset, so that
    every analysis deck starts there.  From FE.NODESET alone, ngspice's gmin and source stepping
    fail on some of these decks, and its transient-op fallback returns a state that is not a DC
    solution (sr560_variants.json, check_operating_point); _op tries the next starting point when
    that happens and stops with an error if every one falls back."""
    import dataclasses
    v = []
    src = "VA ina0 0 DC 0\nRSA ina0 ina 1 rnl\nRSB ina0 inb 1 rnl\n"
    ctl = ".control\nop\nprint v(out)\nprint all\n.endc\n"
    key = (runs, s.fe10)
    others = [ns for (r, fe), ns in reversed(list(_ANCHOR.items())) if fe == s.fe10 and r != runs]
    starts = ([_ANCHOR[key]] if key in _ANCHOR else []) + others + [None, ""]
    for vt in (0.0, 1.0):
        f = _op(f"{runs}/{s.tag}/trim{vt:g}",
                lambda ns, vt=vt: deck(dataclasses.replace(s, vtrim=vt, nodeset=ns), "trim", src, ctl), starts, edit)
        v.append(spice.printed(f, "v(out)"))
        starts = [all_nodes(f)] + starts
    vt = -v[0] / (v[1] - v[0])
    dac = s.dac * g / s.nominal if g else s.dac
    f = _op(f"{runs}/{s.tag}/trimmed",
            lambda ns: deck(dataclasses.replace(s, vtrim=vt, dac=dac, nodeset=ns), "trimmed", src, ctl), starts, edit)
    _ANCHOR[key] = all_nodes(f)
    return dataclasses.replace(s, vtrim=vt, dac=dac, nodeset=_ANCHOR[key])


def run_noise(s: SRSetting, runs: str = "sr560_chain", edit=None) -> dict:
    """Input-referred noise at out50 (runs, edit: as in run_ac)."""
    import dataclasses
    f = _op(f"{runs}/{s.tag}/noise",
            lambda ns: deck(dataclasses.replace(s, nodeset=ns), f"sr560 noise {s.tag}",
                            "VIN ina0 0 DC 0 AC 1\nRSA ina0 ina 1 rnl\nRSB 0 inb 1 rnl\n",
                            spice.noise_control("out50", "VIN", 0.1, 30e6, 20)), [s.nodeset, None, ""], edit)
    nz = spice.read_noise(f)
    fr, inn = nz["frequency"], nz["inoise_spectrum"]
    return dict(f=fr, inn=inn, en={str(f0): spice.at(fr, inn, f0) for f0 in (1, 10, 100, 1e3, 1e4, 1e5)})


def run_ac(s: SRSetting, src=SRC_DM, tag="ac", runs: str = "sr560_chain", edit=None) -> dict:
    """AC response at out50.  runs: the folder under ../sim/runs/ (as in trimmed()); edit: an
    optional function applied to the deck text before it is run (sr560_bw_check.py uses it to
    swap op-amp models).  The defaults reproduce this script's own runs."""
    import dataclasses
    ctl = ".control\n" + spice.WR + "op\nprint v(out50)\nac dec 40 1 100meg\nwrdata ac.txt v(out50)\n.endc\n"
    f = _op(f"{runs}/{s.tag}/{tag}", lambda ns: deck(dataclasses.replace(s, nodeset=ns), f"sr560 {tag} {s.tag}", src, ctl),
            [s.nodeset, None, ""], edit)
    d = spice.read_table(f / "ac.txt")
    return dict(f=d["frequency"], h=d["v(out50)"])


def main(args):
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    what = args[0] if args else "all"
    path = spice.RESULTS / "sr560_chain.json"
    res = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    if what in ("noise", "all"):
        rows = {}
        for mode, gl in (("LN", GAINS_LN), ("HDR", GAINS_HDR)):
            for g in gl:
                s = trimmed(allocate(g, mode), g)
                r = run_noise(s)
                rows[f"{mode}_{g}"] = dict(mode=mode, gain=g, setting=s.tag, nominal=s.nominal, en=r["en"],
                                           manual=MANUAL[mode].get(g))
                print(f"SR560 {mode:3s} G {g:>6}: {s.tag:22s} en(1k) {r['en']['1000.0'] * 1e9:6.2f}  en(100k) "
                      f"{r['en']['100000.0'] * 1e9:6.2f}  en(10) {r['en']['10'] * 1e9:7.2f}  (manual {MANUAL[mode].get(g)})")
                if mode == "LN" and g in (100, 1000):
                    np.savez(spice.RESULTS / f"sr560_chain_noise_{mode}_{g}.npz", f=r["f"], inn=r["inn"])
        res["noise"] = rows
    if what in ("ac", "all"):
        acs = {}
        for g in (1, 10, 100, 1000, 10000, 50000):
            s = trimmed(allocate(g, "LN"), g)
            r = run_ac(s)
            mag = np.abs(r["h"])
            ref = spice.at(r["f"], mag, 1e3)
            acs[str(g)] = dict(setting=s.tag, gain_1k=ref, f3db=spice.f3db(r["f"], mag, ref),
                               db_300k=float(20 * np.log10(spice.at(r["f"], mag, 3e5) / ref)),
                               db_1M=float(20 * np.log10(spice.at(r["f"], mag, 1e6) / ref)))
            print(f"SR560 AC G {g:>6}: gain(1k) {ref:.4g}  f3dB {acs[str(g)]['f3db'] / 1e6:.2f} MHz  "
                  f"300 kHz {acs[str(g)]['db_300k']:+.2f} dB  1 MHz {acs[str(g)]['db_1M']:+.2f} dB")
            np.savez(spice.RESULTS / f"sr560_chain_ac_{g}.npz", f=r["f"], h=r["h"])
        res["ac"] = acs
    if what in ("cmrr", "all"):
        s = trimmed(allocate(1000, "LN"), 1000)
        dm = run_ac(s)
        cm = run_ac(s, SRC_CM, "cm")
        cmrr = 20 * np.log10(np.abs(dm["h"]) / np.abs(cm["h"]))
        res["cmrr_ideal_matching"] = {str(f0): float(spice.at(dm["f"], cmrr, f0)) for f0 in (10, 1e3, 1e4, 1e5, 1e6)}
        print("SR560 CMRR (ideal matching) at G 1000:", res["cmrr_ideal_matching"])
        np.savez(spice.RESULTS / "sr560_chain_cmrr.npz", f=dm["f"], cmrr=cmrr)
    path.write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main(sys.argv[1:])
