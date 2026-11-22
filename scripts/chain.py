"""The complete signal chain of the low-noise preamplifier: front end (frontend.py) with its input
network, difference amplifier, two configurable RC filters, two gain stages with switched input
attenuators, and the output driver.  Netlist generator and test benches.

Blocks (node names in brackets):
  input network  per input: C_P (connector, relay, clamps) and the damping network R_Z + C_Z
                 to ground (frontend.py, Section "input network" of the note), bias resistor
  front end      H10, H100 or L200 of frontend.CASES  (inputs ga, gb; outputs oa, ob)
  S2  difference amplifier, LM7171 (A grade), gain 1, four 499-ohm resistors  [da]
  F1  filter 1: off, or one RC section (LP or HP) at fc, buffered by a THS4031 follower  [f1]
  S3  attenuator (a3 of 249 ohm) and a THS4021 at a gain of 10 (R_F 220, R_G 24.4)  [s3]
  F2  filter 2 (as F1)  [f2]
  S4  attenuator (a4) and a THS4021 at a gain of 10  [s4]
  S5  attenuator (a5 = 1, 2/5 or 1/5) and the output driver, THS3091 at a gain of 5 (R_F 1 k,
      R_G 250), 49.9 ohm to the 50-ohm output  [out]
Total gain  G = G_FE * (10 a3) * (10 a4) * (5 a5); a3 and a4 take 1, 1/2, 1/5, 1/10, 1/20, 1/50,
1/100.
All op amps on +/-15 V.  Switches and relays are modelled by their on-resistance where they carry
signal (attenuators: 1 ohm in series with the tap) and by their capacitance where it matters
(filters: 20 pF from the filter node to ground in every setting, the capacitance of a
low-capacitance relay plus layout).

Usage: python chain.py ac|noise|table
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass, replace

import numpy as np

import blocks
import frontend as F
import models
import spice

ATT = (1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01)
DA_OPAMP = "LM7171"           # the difference amplifier S2: da_compare.py, the note's section on distortion
INPUT_NET = {
    # C_P, R_Z, C_Z, bias resistor
    "H": dict(cp=10e-12, rz=2.2e3, cz=10e-12, rbias=100e6),
    "L": dict(cp=30e-12, rz=47.0, cz=220e-12, rbias=10e6),
}


@dataclass
class Setting:
    fe: str              # 'H10', 'H100' or 'L200'
    a3: float = 1.0
    a4: float = 1.0
    a5: float = 1.0
    f1: tuple | None = None    # ('LP' or 'HP', fc)
    f2: tuple | None = None

    @property
    def gain(self) -> float:
        return F.CASES[self.fe].gain * 10 * self.a3 * 10 * self.a4 * 5 * self.a5

    @property
    def tag(self) -> str:
        t = f"{self.fe}_a3_{self.a3:g}_a4_{self.a4:g}_a5_{self.a5:g}"
        for nm, flt in (("f1", self.f1), ("f2", self.f2)):
            if flt:
                t += f"_{nm}{flt[0]}{flt[1]:g}"
        return t.replace(".", "p")


def allocate(total: float, mode: str = "H_LN") -> Setting:
    """Gain allocation: H_LN puts as much gain as possible in the front end (H100 from 100 up),
    H_HR keeps the front end at 10 (larger inputs, more noise), L uses L200.  The remaining gain is
    taken first by S3, then by S4."""
    if mode == "L":
        fe = "L200"
        g_fe = 200.0
    elif mode == "H_LN" and total >= 100:
        fe, g_fe = "H100", 100.0
    else:
        fe, g_fe = "H10", 10.0
    rest = total / g_fe
    # No stage after the front end may run at a higher level than the output (or than the front
    # end's own output, when the front end's gain exceeds the total gain): with that constraint,
    # gain is put as early as possible (lowest noise).
    top = max(total, g_fe) * (1 + 1e-9)
    best = None
    for a3 in ATT:
        for a4 in ATT:
            for a5 in (1.0, 0.4, 0.2):
                g = 100 * a3 * a4 * 5 * a5
                if abs(g / rest - 1) > 1e-9:
                    continue
                if g_fe * 10 * a3 > top or g_fe * 100 * a3 * a4 > top:
                    continue
                key = (-a3, -a4, -a5)          # gain as early as possible
                if best is None or key < best[0]:
                    best = (key, a3, a4, a5)
    if best is None:
        raise ValueError(f"gain {total} not reachable in mode {mode}")
    return Setting(fe, best[1], best[2], best[3])


def stage_filter(name: str, nin: str, nout: str, flt) -> str:
    """One filter section and its THS4031 follower (or a wire)."""
    if not flt:
        return f"R{name}W {nin} {nout} 1m rnl\n"
    kind, fc = flt
    r = 1e3 if fc >= 1e3 else 10e3
    c = 1 / (2 * math.pi * r * fc) - 20e-12 if kind == "LP" else 1 / (2 * math.pi * r * fc)
    nf = f"{name}x"
    if kind == "LP":
        txt = f"R{name} {nin} {nf} {r:g}\nC{name} {nf} 0 {c:.6g}\n"
    else:
        txt = f"C{name} {nin} {nf} {c:.6g}\nR{name} {nf} 0 {r:g}\n"
    txt += f"C{name}P {nf} 0 20p\nX{name}B {nf} {nout} {nout} vp vm OA_THS4031\n"
    return txt


def gain_stage(name: str, nin: str, nout: str, a: float) -> str:
    """Attenuator (249 ohm, tap through a 1-ohm switch) and a THS4021 at a gain of 10."""
    if a >= 1.0:
        att = f"R{name}T {nin} {name}i 1 rnl\n"
    else:
        rt, rb = 249 * (1 - a), 249 * a
        att = f"R{name}T {nin} {name}t {rt:.6g}\nR{name}B {name}t 0 {rb:.6g}\nR{name}S {name}t {name}i 1\n"
    return (att + f"X{name} {name}i {name}n {nout} vp vm OA_THS4021\n"
            f"R{name}F {nout} {name}n 220\nR{name}G {name}n 0 24.4\n")


def netlist(s: Setting, load: float = 1e6) -> str:
    fe = F.CASES[s.fe]
    net = INPUT_NET[s.fe[0]]
    inp = (f"* input network ({s.fe[0]})\nCPA ga 0 {net['cp']:g}\nCPB gb 0 {net['cp']:g}\n"
           f"RZA ga za {net['rz']:g}\nCZA za 0 {net['cz']:g}\nRZB gb zb {net['rz']:g}\nCZB zb 0 {net['cz']:g}\n"
           f"RBA ga 0 {net['rbias']:g}\nRBB gb 0 {net['rbias']:g}\n")
    body = (F.netlist(fe) + inp +
            f"* S2 difference amplifier ({DA_OPAMP}, gain 1)\n"
            f"RD1 ob dn 499\nRD2 dn da 499\nRD3 oa dp 499\nRD4 dp 0 499\nXS2 dp dn da vp vm OA_{DA_OPAMP}\n"
            "* F1\n" + stage_filter("F1", "da", "f1", s.f1) +
            "* S3\n" + gain_stage("S3", "f1", "s3", s.a3) +
            "* F2\n" + stage_filter("F2", "s3", "f2", s.f2) +
            "* S4\n" + gain_stage("S4", "f2", "s4", s.a4) +
            "* S5 attenuator and output driver (THS3091, gain 5)\n"
            + (f"RS5T s4 s5t {249 * (1 - s.a5):.6g}\nRS5B s5t 0 {249 * s.a5:.6g}\nRS5S s5t s5i 1\n"
               if s.a5 < 1 else "RS5S s4 s5i 1 rnl\n")
            + "XS5 s5i s5n s5 vp vm OA_THS3091\nRS5F s5 s5n 1k\nRS5G s5n 0 250\nRO50 s5 out 49.9\n"
            f"RLOAD out 0 {load:g}\n")
    return body


def deck(s: Setting, title: str, src: str, control: str, load: float = 1e6) -> str:
    return (f"* {title}\n{spice.OPTIONS}.options rshunt=1e12\n{spice.lib('jfets.lib')}{spice.lib('opamps.lib')}"
            f"{spice.lib('bjts.lib')}{blocks.COMMON}{src}{netlist(s, load)}{control}.end\n")


SRC_DM = "VA ina 0 DC 0 AC 0.5\nVB inb 0 DC 0 AC -0.5\nRIA ina ga 1m rnl\nRIB inb gb 1m rnl\n"


def run_ac(s: Setting) -> dict:
    ctl = ".control\n" + spice.WR + "op\nprint v(out) v(da) v(s3) v(s4)\nac dec 40 1 300meg\nwrdata ac.txt v(out) v(da)\n.endc\n"
    f = spice.run(f"chain/{s.tag}/ac", deck(s, f"chain ac {s.tag}", SRC_DM, ctl))
    d = spice.read_table(f / "ac.txt")
    fr, h = d["frequency"], d["v(out)"]
    mag = np.abs(h)
    ref = spice.at(fr, mag, 1e3)
    return dict(f=fr, h=h, gain_1k=ref, nominal=s.gain, f3db=spice.f3db(fr, mag, ref),
                peak_db=float(20 * np.log10(mag.max() / ref)),
                db_10M=float(20 * np.log10(spice.at(fr, mag, 10e6) / ref)),
                db_1M=float(20 * np.log10(spice.at(fr, mag, 1e6) / ref)),
                vout_dc=spice.printed(f, "v(out)"))


def run_noise(s: Setting, rs: float = 0.0, run_suffix: str = "") -> dict:
    """Input-referred noise (DM, input A driven, B grounded) with an optional source resistor in
    each input (noisy, as a real source).  run_suffix keeps a variant's deck in its own folder."""
    # single-ended source: input A through rs (noisy, as a real source), input B grounded
    rs_txt = (f"RIA ina ga {rs:g}\nRIB 0 gb 1m rnl\n" if rs else "RIA ina ga 1m rnl\nRIB 0 gb 1m rnl\n")
    src = "VIN ina 0 DC 0 AC 1\n" + rs_txt
    f = spice.run(f"chain/{s.tag}{run_suffix}/noise_rs{rs:g}",
                  deck(s, f"chain noise {s.tag}", src, spice.noise_control("out", "VIN", 0.1, 100e6, 20)))
    nz = spice.read_noise(f)
    fr, inn, on = nz["frequency"], nz["inoise_spectrum"], nz["onoise_spectrum"]
    return dict(f=fr, inn=inn, onoise=on,
                en={str(f0): spice.at(fr, inn, f0) for f0 in (1, 10, 100, 1e3, 1e4, 1e5, 1e6, 1e7)},
                out_rms_10M=spice.integrate(fr, on, 1.0, 10e6))


def main(args):
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    what = args[0] if args else "ac"
    gains = {"H_LN": [1, 10, 100, 1000, 10000, 50000], "H_HR": [1, 10, 100, 1000], "L": [200, 1000, 10000, 100000]}
    out = {}
    for mode, gl in gains.items():
        for g in gl:
            s = allocate(g, mode)
            if what == "ac":
                r = run_ac(s)
                print(f"{mode:5s} G {g:>7g}: {s.tag:28s} gain(1k) {r['gain_1k']:.4g}  f3dB {r['f3db']/1e6:6.2f} MHz  "
                      f"1M {r['db_1M']:+.2f} dB  10M {r['db_10M']:+.2f} dB  peak {r['peak_db']:.2f} dB  Vout_dc {r['vout_dc']*1e3:.1f} mV")
                out[f"{mode}_{g}"] = {k: v for k, v in r.items() if k not in ("f", "h")}
            else:
                r = run_noise(s)
                print(f"{mode:5s} G {g:>7g}: " + " ".join(f"{k}:{v*1e9:.2f}" for k, v in r["en"].items()) +
                      f"  out rms(1 Hz-10 MHz) {r['out_rms_10M']*1e3:.2f} mV")
                out[f"{mode}_{g}"] = dict(en=r["en"], out_rms_10M=r["out_rms_10M"])
    path = spice.RESULTS / f"chain_{what}.json"
    path.write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main(sys.argv[1:])
