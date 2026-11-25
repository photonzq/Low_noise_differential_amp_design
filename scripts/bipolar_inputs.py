"""Bipolar input stages for the lowest source resistances, against L's JFET array (Section 3.5 of the note).

Stage 1, the input-stage testbench.  The question is the input devices alone, so they are simulated in a circuit
in which nothing else makes noise: a differential pair of N devices per side, the two sides' sources (emitters)
joined and fed by an ideal tail current source (ngspice's independent sources are noiseless), every drain
(collector) of a side returned to a fixed voltage through a 0 V source that measures the side's current, and the
output the difference of the two currents, v(out) = 1000 ohm x (i_A - i_B), by a behavioural source (noiseless).
The source is a noiseless resistor R_S (model rnl) in series with input A, input B is grounded through 1 mOhm, as in
nf_map.py, so that ngspice's input-referred noise is the input pair's own v_a.  In the current-feedback front end
the loop holds each device's current constant, and its channel (collector) noise appears at the input exactly as in
this pair, i_d / g_m; the base or gate current's noise flows through R_S in both (and, in the front end, also
through R_G / 2: stage 2).  What the testbench leaves out (R_G, R_D, the op amps, the sinks, the input network) is
simulated in stage 2.
At each frequency the runs over R_S are fitted with the noisy two-port of nf_map.py,
v_a^2 = S_e + R_S S_x + R_S^2 S_i (S_e = |e_n|^2, S_i = |i_n|^2, S_x = 2 Re(e_n i_n*)), and the largest deviation of
a run from the fit is recorded.  ngspice's generators are grouped by kind (channel or collector shot noise, base
shot noise, 1/f, base resistance, gate resistor) on the shorted input.

Checks: the JFE150 array of L (12 per side, 5 mA each, V_DS 3.85 V) against the input-JFET group of L's front end at
a total gain of 200 (curves_noise.npz, L200_g_input JFETs); each bipolar array's white noise against Leach's
Eqs. (43)-(44) (Proc. IEEE 82(10), 1515-1538, 1994) at its simulated operating point, per device
e_n^2 = 4kT (RB + RE) + 2kT V_T / I_C and i_n^2 = 2 q I_B, differential e_n^2 x 2 / N and i_n^2 x N.

Stage 2 (argument "fe"): the complete front end with the SSM2212 array (frontend.FE with bjt = the calibrated card;
the same topology, R_F, R_G, cascodes, bootstrap, sinks and op amps as L200): a scan of its compensation, its
margins, bandwidth, operating point and noise groups, its and L200's noise over the source resistance, input
impedance and response with real sources (fe_stage).

Writes ../sim/results/bipolar_inputs.npz (f_<key>, va2_<key> [rows: R_S], coef_<key>) and bipolar_inputs.json
(stage 1); bipolar_comp_search.json, bipolar_fe.npz, bipolar_fe_noise.npz and bipolar_fe.json (stage 2); and the
calibrated cards to ../sim/models/_lib/bipolar_inputs.lib.
Usage: python bipolar_inputs.py [key ...]   (stage 1; default: every configuration in CONFIGS)
       python bipolar_inputs.py fe          (stage 2, after stage 1)
"""
from __future__ import annotations

import json
import math
from dataclasses import replace
import re
import sys
import time

import numpy as np

import models
import spice

RS = 10 ** (np.arange(-2, 13) / 2)               # 0.1 ohm to 1 Mohm, two per decade
F_LO, F_HI, PPD = 0.1, 10e6, 20
F_REPORT = (1.0, 10.0, 100.0, 1e3, 1e4, 1e5, 1e6)

# key: kind ("jfet": an N-JFET subcircuit; "npn", "pnp": a BJT model), part (subcircuit or model name), devices per
# side, current per device (A), the magnitude of the drain-source (collector-emitter) voltage, the source (emitter)
# node's voltage at the operating point (to set the drain or collector supply), and the library or, for a BJT, the
# .model card itself
Q_E = 1.602176634e-19

# The SSM2212's card (Analog Devices SSM2212 Rev. C; the MAT12, Rev. A, is the same die in a TO-78 can: its
# Table 1 and Figs. 3-5 are the SSM2212's Table 1 and Figs. 4-6).  Gummel-Poon, ngspice level 1, at T = 27 C:
#   RB   28 ohm      "rbb' is typically 28 ohm" (SSM2212 p. 1), taken as constant (no RBM/IRB data); with r_e/2 it
#                    gives e_n = 0.82 nV/rtHz at 1 mA, between the typical curve (0.76, Fig. 4) and the table (0.85)
#   RE   0.3 ohm     bulk resistance R_BE, typical (MAT12 Table 1)
#   BF   605         h_FE typical at 1 mA, SOIC (Table 1), flat from 1 uA to 1 mA (Fig. 6); the LFCSP's h_FE is
#                    1300 at V_CB = 0 and 1800 at 15 V (Table 2), about 1400 at V_CB ~ 3 V (interpolated)
#   IS   3.66e-13 A  V_BE = 0.562 V at 1 mA (Fig. 8, V_CE 5 V), ideality 1
#   VAF  100 V       h_oe about 10 uS at 1 mA (MAT12 Fig. 9)
#   CJC  29 pF, VJC 0.75, MJC 0.30: C_CB 29 pF at 0 V, 13 pF at 10 V, 10 pF at 40 V (MAT12 Fig. 12)
#   CJS  42 pF, VJS 0.75, MJS 0.30: twice the collector-to-collector capacitance, 21 pF at 0 V (MAT12 Fig. 13)
#   CJE  82 pF, VJE 0.75, MJE 0.33: not given for the SSM2212 or MAT12; the MAT02's C_EB at 0 V (MAT02 TPC 17)
#   TF   0.44 ns     f_T 200 MHz at 10 mA, V_CE 10 V (Table 1), less the junction capacitances' share
#   KF, AF           base-current flicker noise, S_IB = 2 q I_B + KF I_B^AF / f.  No data sheet in production gives i_n
#                    against frequency.  The SSM2212's total noise against I_C at 1 kHz with 100 kOhm (Fig. 5) puts
#                    i_n(1 kHz) at the base current's shot noise from 0.1 to 1 mA (within reading accuracy, about 20 %
#                    in power), so the corner at these currents is below a few hundred hertz.  Comparable parts' corners
#                    at about 1 mA (Section 3.5): MAT03 ~340 Hz (TPC 10), 2SB737 ~180 Hz (Fig. 15), LM394 ~1.2 kHz,
#                    OP37 140 Hz, LT1028 250 Hz; their rise with current gives AF ~1.3 (LM394 1.35, 2SB737 1.28).
#                    AF = 1.3, and KF from the corner f_c0 at I_C = 1 mA: KF = 2 q f_c0 I_B0^(1 - AF), I_B0 = 1 mA / BF;
#                    f_c0 = 200 Hz (central), 30 Hz and 1 kHz (the bracket)
SSM2212 = dict(rb=28.0, re=0.3, bf=605.0, bf_lfcsp=1400.0, is_=3.66e-13, vaf=100.0, cjc=29e-12, vjc=0.75, mjc=0.30,
               cjs=42e-12, vjs=0.75, mjs=0.30, cje=82e-12, vje=0.75, mje=0.33, tf=0.44e-9, af=1.3, fc0=200.0,
               i0=1e-3)


def ssm2212_card(name: str, fc0: float = SSM2212["fc0"], bf: float = SSM2212["bf"], af: float = SSM2212["af"]) -> str:
    c = SSM2212
    kf = 2 * Q_E * fc0 * (c["i0"] / bf) ** (1 - af)
    return (f".model {name} NPN(IS={c['is_']:.4g} BF={bf:g} NF=1 VAF={c['vaf']:g} RB={c['rb']:g} RE={c['re']:g} "
            f"RC=5 CJE={c['cje']:.4g} VJE={c['vje']:g} MJE={c['mje']:g} CJC={c['cjc']:.4g} VJC={c['vjc']:g} "
            f"MJC={c['mjc']:g} CJS={c['cjs']:.4g} VJS={c['vjs']:g} MJS={c['mjs']:g} TF={c['tf']:.4g} "
            f"KF={kf:.6g} AF={af:g})")


def _bjt(n: int, fc0: float = SSM2212["fc0"], bf: float = SSM2212["bf"], tag: str = "") -> dict:
    """An SSM2212 array of n per side at L's current, 60 mA per side, V_CE 3.8 V (the cascode's, as in L)."""
    i_dev = 60e-3 / n
    v_be = 0.025865 * np.log(i_dev / SSM2212["is_"])
    name = f"QSSM{tag}{n}_{fc0:g}"
    return dict(kind="npn", part=name, n=n, i_dev=i_dev, v_ds=3.8, v_src=-v_be, card=ssm2212_card(name, fc0, bf),
                fc0=fc0, bf=bf)


CONFIGS = {
    "JFE150_L": dict(kind="jfet", part="JFE150", n=12, i_dev=5e-3, v_ds=3.85, v_src=0.56, lib="jfets.lib"),
    # SSM2212 arrays at L's 60 mA per side: the central calibration with 12, 24 and 48 per side
    "SSM2212_12": _bjt(12),
    "SSM2212_24": _bjt(24),
    "SSM2212_48": _bjt(48),
    # the base-current 1/f bracket at 24 per side
    "SSM2212_24_fc30": _bjt(24, fc0=30.0),
    "SSM2212_24_fc1k": _bjt(24, fc0=1000.0),
    # the LFCSP's higher current gain (same KF: its base current, and with it the flicker noise, are lower)
    "SSM2212L_24": _bjt(24, bf=SSM2212["bf_lfcsp"], tag="L"),
}


def rs_name(rs: float) -> str:
    return f"rs_{rs:.4g}".replace("+", "")


_IB_SIDE: dict = {}


def ib_side(key: str) -> float:
    """Side A's DC input current (the base currents of its n transistors; 0 for a JFET side) at the operating
    point, signed as the current into the devices (negative for a PNP side)."""
    if key not in _IB_SIDE:
        c = CONFIGS[key]
        _IB_SIDE[key] = 0.0 if c["kind"] == "jfet" else c["n"] * operating_point(key)["ib"]
    return _IB_SIDE[key]


def deck(key: str, rs: float) -> str:
    """The testbench's deck.  R_S (noiseless) connects input A to the generator directly.  For a bipolar side an
    ideal current source IBA (noiseless, an open circuit in AC) supplies side A's base current at the operating
    point, so that no DC current flows in R_S and the operating point is the same at every R_S: an ideal, noiseless
    bias path, and the base current's noise still flows in R_S.  (A first version passed R_S through 1 MF and gave
    input A a 1 GH inductor to ground instead; their admittances, up to 1e13, spoiled the matrix's conditioning
    above about 1 MHz, visibly in L200's runs with large R_S, which alternated from one frequency point to the
    next.)"""
    lines = [f"* input-stage testbench {key}, R_S {rs:g}"] + circuit(key)
    lines[1:1] = [f"RSA ina ga {rs:.6g} rnl"] + ([f"IBA 0 ga DC {ib_side(key):.9g}"] if ib_side(key) else [])
    lines.append(spice.noise_control("out", "VIN", F_LO, F_HI, PPD).rstrip())
    lines.append(".end")
    return "\n".join(lines) + "\n"


def circuit(key: str) -> list[str]:
    """The testbench without R_S and analysis: the pair, its supplies and the noiseless readout (see deck)."""
    c = CONFIGS[key]
    n, i_dev = c["n"], c["i_dev"]
    p_type = c["kind"] == "pnp"
    vsup = c["v_src"] - c["v_ds"] if p_type else c["v_src"] + c["v_ds"]
    tail = (f"ITAIL vrail s DC {2 * n * i_dev:.6g}", "VRAIL vrail 0 DC 10") if p_type else \
        (f"ITAIL s vrail DC {2 * n * i_dev:.6g}", "VRAIL vrail 0 DC -10")
    lib = c["card"] if "card" in c else spice.lib(c["lib"]).rstrip()
    lines = [spice.OPTIONS.rstrip(), lib, ".model rnl r(noisy=0)",
             "VIN ina 0 DC 0 AC 1", "RSB 0 gb 1m rnl",
             f"VSUP vsup 0 DC {vsup:.6g}", "VMA vsup da DC 0", "VMB vsup db DC 0", *tail,
             "BOUT out 0 V = 1000 * (i(VMA) - i(VMB))"]
    for side, g, d in (("A", "ga", "da"), ("B", "gb", "db")):
        for k in range(n):
            if c["kind"] == "jfet":
                lines.append(f"X{side}{k} {d} {g} s {c['part']}")
            else:
                lines.append(f"Q{side}{k} {d} {g} s {c['part']}")
    return lines


def operating_point(key: str) -> dict:
    """One device's operating point in the testbench (R_S 1 mOhm, no IBA): currents, voltages, g_m, and for a BJT
    beta, r_pi and the base resistance ngspice uses (rx, with RBM and IRB the current-dependent value)."""
    c = CONFIGS[key]
    dev = "@j.xa0.j1" if c["kind"] == "jfet" else "@qa0"
    qs = ["id", "gm", "vgs", "vgd"] if c["kind"] == "jfet" else ["ic", "ib", "gm", "gpi", "gx", "vbe", "vbc", "cpi", "cmu"]
    ctl = ".control\n" + spice.WR + "op\nprint " + " ".join(f"{dev}[{q}]" for q in qs) + " v(s)\n.endc\n"
    text = "\n".join([f"* operating point {key}", "RSA ina ga 1m rnl"] + circuit(key) + [ctl, ".end"]) + "\n"
    folder = spice.check_dc(spice.run(f"bipolar_inputs/{key}/op", text))
    out = {q: spice.printed(folder, f"{dev}[{q}]") for q in qs}
    out["v(s)"] = spice.printed(folder, "v(s)")
    if c["kind"] != "jfet":
        out["beta"] = out["ic"] / out["ib"]
        out["r_x"] = 1 / out["gx"] if out["gx"] else 0.0
    return out


# ngspice lists each device's total (onoise_<device>) beside its parts (onoise_<device>_<part>); only the parts are
# summed.  Device names: j... JFET, q... BJT, r... resistor (the JFET subcircuit's RX, the excess white gate noise)
# matched against "<device letter>:<last dot-separated part of the name>", e.g. j:j1_id, q:qa0_ib, r:rx_thermal
KINDS = (
    ("JFET channel thermal noise", r"^j:.*_id$"),
    ("collector shot noise", r"^q:.*_ic$"),
    ("base shot noise", r"^q:.*_ib$"),
    ("1/f noise", r"^[jq]:.*_1overf$"),
    ("base resistance", r"^q:.*_rb$"),
    ("JFET gate resistor RX", r"^r:rx_thermal$"),
    ("series resistances", r"^[jq]:.*_(rd|rs|rc|re)$"),
    ("resistor 1/f noise", r"^r:.*_1overf$"),
)


def groups(nz: dict) -> dict:
    """Output-noise power of each kind of generator (V^2/Hz at the output), summed over the leaf generators."""
    out: dict[str, np.ndarray] = {}
    for name, v in nz.items():
        if not name.startswith("onoise_") or name == "onoise_spectrum":
            continue
        base = name[len("onoise_"):]
        if not re.search(r"_(1overf|id|ic|ib|rb|rd|rs|rc|re|thermal)$", base):
            continue                                   # a device's or resistor's total
        key = f"{base[0]}:{base.split('.')[-1]}"
        for kind, pat in KINDS:
            if re.search(pat, key):
                out[kind] = out.get(kind, 0) + v ** 2
                break
        else:
            raise ValueError(f"unclassified noise generator {name}")
    return out


def run(key: str) -> tuple[np.ndarray, np.ndarray, dict]:
    rows, f, grp = [], None, None
    t0 = time.time()
    for rs in RS:
        folder = spice.check_dc(spice.run(f"bipolar_inputs/{key}/{rs_name(rs)}", deck(key, rs)))
        nz = spice.read_noise(folder)
        assert f is None or np.array_equal(nz["frequency"], f)
        f = nz["frequency"]
        rows.append(nz["inoise_spectrum"] ** 2)
        if rs == RS[0]:
            gain2 = nz["onoise_spectrum"] ** 2 / nz["inoise_spectrum"] ** 2
            grp = {k: np.sqrt(v / gain2) for k, v in groups(nz).items()}
        print(f"{key} R_S {rs:10.4g}: v_a(1 kHz) {spice.at(f, nz['inoise_spectrum'], 1e3) * 1e9:8.4f} nV/rtHz "
              f"({time.time() - t0:5.1f} s)", flush=True)
    return f, np.array(rows), grp


def crossover(coef_a: np.ndarray, coef_b: np.ndarray) -> np.ndarray:
    """At each frequency, the source resistance where two fitted two-ports (rows S_e, S_x, S_i) have the same
    input-referred noise: the smallest positive root of dS_i R^2 + dS_x R + dS_e = 0 (nan where there is none)."""
    out = np.full(coef_a.shape[1], np.nan)
    for j in range(coef_a.shape[1]):
        d = coef_a[:, j] - coef_b[:, j]
        roots = [r.real for r in np.roots([d[2], d[1], d[0]]) if abs(r.imag) < 1e-9 * max(abs(r.real), 1) and r.real > 0]
        if roots:
            out[j] = min(roots)
    return out


def nf_db(coef: np.ndarray, rs, t0: float = 290.0) -> np.ndarray:
    """Noise figure (dB) of a fitted two-port with a source R_S at t0 (290 K, as nf_map.py), per frequency."""
    rs = np.asarray(rs, dtype=float)
    va2 = coef[0] + rs * coef[1] + rs ** 2 * coef[2]
    return 10 * np.log10(1 + va2 / (4 * 1.380649e-23 * t0 * rs))


def two_port(rs: np.ndarray, va2: np.ndarray) -> tuple[np.ndarray, float]:
    """As nf_map.two_port: S_e, S_x, S_i per frequency (relative weights, columns scaled) and the largest deviation
    of a run from the fit in dB of noise figure (source at 290 K)."""
    a = np.stack([np.ones_like(rs), rs, rs ** 2], axis=1)
    coef = np.empty((3, va2.shape[1]))
    for j in range(va2.shape[1]):
        w = 1 / va2[:, j]
        aw = a * w[:, None]
        scale = np.linalg.norm(aw, axis=0)
        coef[:, j] = np.linalg.lstsq(aw / scale, va2[:, j] * w, rcond=None)[0] / scale
    g4 = 4 * 1.380649e-23 * 290.0
    nf = lambda v: 10 * np.log10(1 + v / (g4 * rs[:, None]))      # noqa: E731
    return coef, float(np.abs(nf(a @ coef) - nf(va2)).max())


# ------------------------------------------------------------------------------------------------------------------
# Stage 2: the complete current-feedback front end with an SSM2212 array in place of L's JFETs (frontend.FE with
# bjt = the calibrated card): the same topology, R_F, R_G, cascodes, bootstrap, sinks and op amps as L200
LIB_NAME = "bipolar_inputs.lib"


def write_lib() -> None:
    """The calibrated cards of CONFIGS, as the front end's extra library (frontend.FE.extra_lib)."""
    cards = [c["card"] for c in CONFIGS.values() if "card" in c]
    models._atomic_write(spice.LIB / LIB_NAME, "* bipolar input cards calibrated in bipolar_inputs.py\n"
                         + "\n".join(cards) + "\n", "utf-8")


def fe_case(key: str, **kw):
    """L200 with the input array of CONFIGS[key] (devices per side, current per device), other values in kw."""
    import frontend as F
    c = CONFIGS[key]
    return replace(F.CASES["L200"], name=f"B_{key}", bjt=c["part"], n=c["n"], id=c["i_dev"], extra_lib=LIB_NAME,
                   **kw)


def fe_op(p) -> dict:
    """The bipolar front end's operating point: node voltages and the first device of each side."""
    import frontend as F
    keys = ["v(ga)", "v(sa)", "v(sb)", "v(ba)", "v(da1)", "v(ca)", "v(cb)", "v(oa)", "v(ob)",
            "@qja1[ic]", "@qja1[ib]", "@qja1[gm]", "@qjb1[ic]"]
    ctl = ".control\n" + spice.WR + "op\nprint " + " ".join(keys[:9]) + "\nprint " + " ".join(keys[9:]) + "\n.endc\n"
    f = spice.run(f"fe/{p.name}/op", F.deck(p, f"op {p.name}", F.SRC_DM, ctl), allow=(r"q\.xua",))
    if spice.op_fallback(f):
        raise RuntimeError(f"{p.name}: the operating point fell back to the transient op")
    return {k: spice.printed(f, k) for k in keys}


def fe_noise(p) -> dict:
    """Input-referred noise of the front end and its groups (frontend.noise_groups, the DM gain of check_ac)."""
    import frontend as F
    ac = F.check_ac(p)
    nz = F.check_noise(p)
    fr = nz["f"]
    gain = np.abs(np.interp(np.log10(fr), np.log10(ac["curve"][0]), np.abs(ac["curve"][1])))
    return dict(f=fr, inn=nz["inn"], groups=F.noise_groups(nz["nz"], gain), ac=ac)


# The bipolar front end's compensation: bipolar_comp_search.json (scan_comp), C_I + C_X = 82.5 pF, C_I - C_X =
# 67.5 pF and C_node = 2.2 nF, next to the scan's point S 80 / D 65 pF / 2.2 nF, rounded to E24 values
B_COMP = dict(ci=75e-12, cx=7.5e-12, cnode=2.2e-9)
# front ends compared over the source resistance: L200 as designed, and B (L200 with the SSM2212 array, B_COMP) with
# the central calibration and the two ends of the base-current 1/f bracket
FE_KEYS = {"L200": None, "B": "SSM2212_24", "B_fc30": "SSM2212_24_fc30", "B_fc1k": "SSM2212_24_fc1k"}
FE_RS = 10 ** (np.arange(-2, 13) / 2)             # 0.1 ohm to 1 Mohm, two per decade


def fe_p(tag: str):
    import frontend as F
    key = FE_KEYS[tag]
    return F.CASES["L200"] if key is None else fe_case(key, **B_COMP)


def fe_check_quiescent(folder, what: str, tol: float = 0.1) -> None:
    """A deck's printed v(oa), v(ob), v(sa), v(sb): each output within tol of its source node (no DC differential
    input driving the front end off its quiescent point), else RuntimeError."""
    v = {n: spice.printed(folder, f"v({n})") for n in ("oa", "ob", "sa", "sb")}
    if abs(v["oa"] - v["sa"]) > tol or abs(v["ob"] - v["sb"]) > tol:
        raise RuntimeError(f"{what}: outputs off their quiescent point: {v}")


_FE_IB: dict = {}


def fe_ib(p) -> float:
    """A side's DC input current in the front end p: its n base currents at the operating point (fe_op), 0 for
    JFETs (their gate current, picoamperes, is left to flow in the source)."""
    if not p.bjt:
        return 0.0
    if p.name not in _FE_IB:
        _FE_IB[p.name] = p.n * fe_op(p)["@qja1[ib]"]
    return _FE_IB[p.name]


def fe_rs_run(p, rs: float) -> tuple[np.ndarray, np.ndarray]:
    """The front end's input-referred noise power (V^2/Hz) with a noiseless R_S in series with input A and input B
    grounded through 1 mOhm; for a bipolar side, IBA (ideal, noiseless) supplies input A's base current, as in the
    testbench (deck())."""
    import frontend as F
    ib = fe_ib(p)
    src = (f"VIN ina 0 DC 0 AC 1\nRSA ina ga {rs:.6g} rnl\n" + (f"IBA 0 ga DC {ib:.9g}\n" if ib else "")
           + "RIB 0 gb 1m rnl\n")
    ctl = (".control\n" + spice.WR + "op\nprint v(oa) v(ob) v(sa) v(sb)\n"
           "noise v(oa,ob) VIN dec 20 0.1 100e6 1\nsetplot noise1\nwrdata noise.txt all\n.endc\n")
    folder = spice.run(f"fe/{p.name}/rs/{rs_name(rs)}", F.deck(p, f"fe noise {p.name} R_S {rs:g}", src, ctl))
    if spice.op_fallback(folder):
        raise RuntimeError(f"{p.name}, R_S {rs:g}: the operating point fell back to the transient op")
    fe_check_quiescent(folder, f"{p.name}, R_S {rs:g}")
    nz = spice.read_noise(folder)
    return nz["frequency"], nz["inoise_spectrum"] ** 2


R_ZIN_BIAS = 1e6


def fe_zin(p) -> dict:
    """Input impedance as frontend.check_zin (1 A AC into input A; B grounded through 1 mOhm, or tied to A for the
    common mode), with the test source's DC value the inputs' base current (fe_ib; check_zin's 1 TOhm, through which
    a bipolar side's 0.1 mA cannot flow, would cut side A off) and a noiseless R_ZIN_BIAS from input A to ground for
    the DC operating point, whose admittance is subtracted from the result.  R_ZIN_BIAS is 1 MOhm because the
    injected current matches the base current only to the printed operating point's precision (about 1e-10 A): with
    1 GOhm the remainder put 0.13 V of differential input on the front end and drove its outputs to the rails.  Each
    deck's outputs are checked to sit within 0.1 V of the source node (fe_check_quiescent)."""
    import frontend as F
    out = {}
    ib = fe_ib(p)
    for mode, src in (("dm", f"IA 0 ga DC {ib:.9g} AC 1\nRIB 0 gb 1m rnl\nRBIAS ga 0 {R_ZIN_BIAS:g} rnl\n"),
                      ("cm", f"IA 0 ga DC {2 * ib:.9g} AC 1\nRIB ga gb 1m rnl\nRBIAS ga 0 {R_ZIN_BIAS:g} rnl\n")):
        ctl = (".control\n" + spice.WR + "op\nprint v(oa) v(ob) v(sa) v(sb)\nac dec 20 10 1g\nwrdata zin.txt v(ga)\n"
               ".endc\n")
        f = spice.run(f"fe/{p.name}/zin_ideal_bias_{mode}", F.deck(p, f"zin {p.name} {mode}", src, ctl))
        if spice.op_fallback(f):
            raise RuntimeError(f"{p.name} zin {mode}: the operating point fell back to the transient op")
        fe_check_quiescent(f, f"{p.name} zin {mode}")
        d = spice.read_table(f / "zin.txt")
        fr = d["frequency"]
        z = 1 / (1 / d["v(ga)"] - 1 / R_ZIN_BIAS)
        out[mode] = dict(f=fr, z=z, c_eff=np.imag(1 / z) / (2 * np.pi * fr))
    return out


# source networks for the bipolar front end's stability with real sources (as frontend.SOURCES), per input from the
# generator node (ina, inb) to the input (ga, gb); its domain is a few ohms to a few tens of ohms
B_SOURCES = {
    "10ohm": "RSA ina ga 10\nRSB inb gb 10\n",
    "1ohm_1uH": "RSA ina na 1\nLSA na ga 1u\nRSB inb nb 1\nLSB nb gb 1u\n",
    "10ohm_1uH": "RSA ina na 10\nLSA na ga 1u\nRSB inb nb 10\nLSB nb gb 1u\n",
    "50ohm_1uH": "RSA ina na 50\nLSA na ga 1u\nRSB inb nb 50\nLSB nb gb 1u\n",
    # 1 m of 50-ohm coaxial cable (5 ns), driven from 10 ohm at the far end
    "cable1m_10ohm": "RSA ina na 10\nTA na 0 ga 0 Z0=50 TD=5n\nRSB inb nb 10\nTB nb 0 gb 0 Z0=50 TD=5n\n",
}


def fe_sources(p, names=None) -> dict:
    """As frontend.check_sources (DM drive through each source network; the largest peak above the low-frequency
    gain), the source networks being the DC paths (they all pass DC) and, for a bipolar side, ideal current sources
    IBA, IBB supplying the base currents (fe_ib), instead of check_sources' 100 MOhm bias resistors, through which a
    bipolar side's base current cannot flow."""
    import frontend as F
    out = {}
    ib = fe_ib(p)
    bias = f"IBA 0 ga DC {ib:.9g}\nIBB 0 gb DC {ib:.9g}\n" if ib else ""
    for nm in names or B_SOURCES:
        src = "VA ina 0 DC 0 AC 0.5\nVB inb 0 DC 0 AC -0.5\n" + bias + B_SOURCES[nm]
        ctl = (".control\n" + spice.WR + "op\nprint v(oa) v(ob) v(sa) v(sb)\nac dec 50 10 1g\n"
               "wrdata ac.txt v(oa) v(ob)\n.endc\n")
        f = spice.run(f"fe/{p.name}/bsrc_{nm}", F.deck(p, f"source {nm}", src, ctl))
        if spice.op_fallback(f):
            raise RuntimeError(f"{p.name} source {nm}: the operating point fell back to the transient op")
        fe_check_quiescent(f, f"{p.name} source {nm}")
        d = spice.read_table(f / "ac.txt")
        fr, h = d["frequency"], np.abs(d["v(oa)"] - d["v(ob)"])
        i = int(np.argmax(h))
        out[nm] = dict(f=fr, h=h, peak_db=float(20 * np.log10(h[i] / h[0])), f_peak=float(fr[i]),
                       f3db=spice.f3db(fr, h))
    return out


def fe_sweep(tags=tuple(FE_KEYS)) -> dict:
    """Each front end over FE_RS and its two-port fit, written to bipolar_fe.npz; returns the fits' deviations."""
    write_lib()
    out, res = {"rs": FE_RS}, {}
    for tag in tags:
        p = fe_p(tag)
        rows, f = [], None
        for rs in FE_RS:
            fr, va2 = fe_rs_run(p, rs)
            assert f is None or np.array_equal(fr, f)
            f = fr
            rows.append(va2)
        va2 = np.array(rows)
        coef, dev = two_port(FE_RS, va2)
        out.update({f"f_{tag}": f, f"va2_{tag}": va2, f"coef_{tag}": coef})
        res[tag] = dict(case=p.name, two_port_max_dev_db=dev)
        print(f"{tag}: {p.name}, two-port fit within {dev:.2g} dB", flush=True)
    np.savez(spice.RESULTS / "bipolar_fe.npz", **out)
    return res


# the compensation scan of the bipolar front end: (C_I + C_X, C_I - C_X, C_node), as comp_search.py's grids
COMP_GRID = dict(S=[60e-12, 80e-12, 100e-12], D=[38e-12, 50e-12, 65e-12], CN=[1.0e-9, 1.5e-9, 2.2e-9])


def scan_comp() -> dict:
    """comp_search.evaluate (margins at the op amps' output pins in both modes, then the -3 dB bandwidth and the
    peak) over COMP_GRID for the SSM2212 front end; written to bipolar_comp_search.json."""
    import itertools
    import comp_search as cs
    res = {}
    for s, d, cn in itertools.product(COMP_GRID["S"], COMP_GRID["D"], COMP_GRID["CN"]):
        key = f"S{s * 1e12:g}_D{d * 1e12:g}_CN{cn * 1e12:g}"
        p = replace(fe_case("SSM2212_24", ci=(s + d) / 2, cx=(s - d) / 2, cnode=cn), name=f"B_SSM2212_24_{key}")
        r = cs.evaluate(p)
        res[key] = dict(r, ci=(s + d) / 2, cx=(s - d) / 2, cnode=cn)
        print(key, {m: (round(r[m]["pm"], 1), round(r[m]["gm_db"], 1)) for m in ("dm", "cm")},
              f"f3dB {r.get('f3db', float('nan')) / 1e6:.1f} MHz, peak {r.get('peak_db', float('nan')):.2f} dB",
              flush=True)
    (spice.RESULTS / "bipolar_comp_search.json").write_text(json.dumps(res, indent=1, default=float),
                                                           encoding="utf-8", newline="\n")
    return res


def _at(f: np.ndarray, y: np.ndarray, f0: float):
    """y at the grid point nearest f0 (float, or complex for a complex y)."""
    v = y[int(np.argmin(np.abs(np.log10(f) - np.log10(f0))))]
    return complex(v) if np.iscomplexobj(y) else float(v)


def fe_stage() -> None:
    """Stage 2: the compensation scan; for B (B_COMP) its margins, bandwidth, operating point and noise groups; for
    L200 and B their noise over the source resistance (fe_sweep), input impedance (fe_zin) and response with real
    sources (fe_sources).  Writes bipolar_comp_search.json, bipolar_fe.npz, bipolar_fe_noise.npz, bipolar_fe.json."""
    import comp_search as cs
    write_lib()
    scan_comp()
    pb = fe_p("B")
    res = dict(b_comp=B_COMP, b_case=pb.name)
    r = cs.evaluate(pb)
    res["b_margins"] = {m: dict(pm=r[m]["pm"], gm_db=r[m]["gm_db"]) for m in ("dm", "cm")}
    res["b_f3db"], res["b_peak_db"], res["b_g10M_db"] = r["f3db"], r["peak_db"], r["g10M_db"]
    res["b_op"] = fe_op(pb)
    nz = fe_noise(pb)
    np.savez(spice.RESULTS / "bipolar_fe_noise.npz", f=nz["f"], inn=nz["inn"],
             **{f"g_{g}": v for g, v in nz["groups"].items()})
    res["b_gain_1k"] = nz["ac"]["gain_1k"]
    res["b_noise"] = {f"{f0:g}": dict(total=_at(nz["f"], nz["inn"], f0),
                                     groups={g: _at(nz["f"], v, f0) for g, v in nz["groups"].items()})
                      for f0 in (1.0, 10.0, 100.0, 1e3, 1e4, 1e5, 1e6, 1e7)}
    res["sweep"] = fe_sweep()
    for tag in ("L200", "B"):
        p = fe_p(tag)
        z = fe_zin(p)
        res[f"zin_{tag}"] = {}
        for mode in ("dm", "cm"):
            row = {}
            for f0 in (10.0, 1e3, 1e5, 1e6, 1e7):
                zz = _at(z[mode]["f"], z[mode]["z"], f0)
                row[f"{f0:g}"] = dict(abs_z=abs(zz), r_par=float(1 / np.real(1 / zz)),
                                      c_eff=_at(z[mode]["f"], z[mode]["c_eff"], f0))
            res[f"zin_{tag}"][mode] = row
        s = fe_sources(p)
        res[f"sources_{tag}"] = {k: dict(peak_db=v["peak_db"], f_peak=v["f_peak"], f3db=v["f3db"])
                                 for k, v in s.items()}
        print(tag, "sources:", {k: round(v["peak_db"], 2) for k, v in s.items()}, flush=True)
    (spice.RESULTS / "bipolar_fe.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8",
                                                  newline="\n")


def flicker_check() -> dict:
    """ngspice's Gummel-Poon flicker noise on one NPN (IS 1e-14 A, BF 300, RB 20 ohm; emitter at 1 mA, AC-grounded
    by 1 kF), with R_S of 1 mOhm and 100 kOhm, for (KF, AF) = (1e-12, 1) and (1e-8, 2): e_n and i_n against
    i_n^2 = 2 q I_B + KF I_B^AF / f and e_n^2 = 4kT RB + 2kT V_T / I_C + (KF I_B^AF / f) RB^2 (the source behind RB,
    Leach's Eqs. (43)-(44) with flicker noise); returns the largest relative deviation of each."""
    kt = 1.380649e-23 * 300.15
    dev_e, dev_i = 0.0, 0.0
    for kf, af in ((1e-12, 1.0), (1e-8, 2.0)):
        res = {}
        for rs in (1e-3, 1e5):
            text = (f"* flicker check KF {kf:g} AF {af:g} R_S {rs:g}\n{spice.OPTIONS}.model rnl r(noisy=0)\n"
                    f".model QT NPN(IS=1e-14 BF=300 RB=20 KF={kf:g} AF={af:g})\n"
                    f"VIN in 0 DC 0 AC 1\nRS in b {rs:g} rnl\nVC vc 0 DC 5\nVM vc c DC 0\nQ1 c b e QT\n"
                    "IE e vneg DC 1m\nCE e 0 1k\nVNEG vneg 0 DC -5\nBOUT out 0 V = 1000*i(VM)\n"
                    + spice.noise_control("out", "VIN", 1.0, 1e5, 10) + ".end\n")
            res[rs] = spice.read_noise(spice.check_dc(spice.run(f"bipolar_inputs/check_kf/af{af:g}_rs_{rs:g}", text)))
        fr = res[1e-3]["frequency"]
        ib = 1e-3 / 301
        for f0 in (1.0, 10.0, 100.0, 1e3, 1e4):
            va0, va1 = spice.at(fr, res[1e-3]["inoise_spectrum"], f0), spice.at(fr, res[1e5]["inoise_spectrum"], f0)
            i_n = math.sqrt(max(va1 ** 2 - va0 ** 2, 0)) / 1e5
            s_f = kf * ib ** af / f0
            e_x = math.sqrt(4 * kt * 20 + 2 * kt * (kt / Q_E) / 1e-3 + s_f * 20 ** 2)
            i_x = math.sqrt(2 * Q_E * ib + s_f)
            dev_e, dev_i = max(dev_e, abs(va0 / e_x - 1)), max(dev_i, abs(i_n / i_x - 1))
    return dict(max_dev_e_n=dev_e, max_dev_i_n=dev_i)


def main(args: list[str]) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    keys = [a for a in args if a in CONFIGS] or list(CONFIGS)
    npz = spice.RESULTS / "bipolar_inputs.npz"
    data = dict(np.load(npz)) if npz.exists() else {}
    js = spice.RESULTS / "bipolar_inputs.json"
    res = json.loads(js.read_text(encoding="utf-8")) if js.exists() else {}
    for key in keys:
        f, va2, grp = run(key)
        coef, dev = two_port(RS, va2)
        data.update({f"f_{key}": f, f"va2_{key}": va2, f"coef_{key}": coef, "rs": RS})
        at = {}
        for f0 in F_REPORT:
            j = int(np.argmin(np.abs(np.log10(f) - np.log10(f0))))
            s_e, s_x, s_i = coef[:, j]
            at[f"{f0:g}"] = dict(e_n=float(np.sqrt(s_e)), i_n=float(np.sqrt(max(s_i, 0))),
                                 corr=float(s_x / (2 * np.sqrt(s_e * s_i))) if s_i > 0 else None,
                                 groups_shorted_input={k: float(v[j]) for k, v in grp.items()})
        res[key] = dict(config=CONFIGS[key], two_port_max_dev_db=dev, at=at)
        if CONFIGS[key]["kind"] != "jfet":
            # Leach's white e_n and i_n at the simulated operating point, against the fit at 100 kHz
            op = operating_point(key)
            kt, n = 1.380649e-23 * 300.15, CONFIGS[key]["n"]
            vt = kt / Q_E
            r_s = SSM2212["rb"] + SSM2212["re"]
            en2 = 2 / n * (4 * kt * r_s + 2 * kt * vt / abs(op["ic"]))
            in2 = n * 2 * Q_E * abs(op["ib"])
            w = at["100000"]
            res[key]["op"] = op
            res[key]["analytic_check"] = dict(e_n=float(np.sqrt(en2)), i_n=float(np.sqrt(in2)),
                                              e_n_ratio=w["e_n"] / float(np.sqrt(en2)),
                                              i_n_ratio=w["i_n"] / float(np.sqrt(in2)))
            print(f"{key}: against Leach (43)-(44) at 100 kHz: e_n x {w['e_n'] / np.sqrt(en2):.4f}, "
                  f"i_n x {w['i_n'] / np.sqrt(in2):.4f}")
        print(f"{key}: two-port fit within {dev:.2g} dB")
        for f0, row in at.items():
            print(f"  {float(f0):>9g} Hz: e_n {row['e_n'] * 1e9:7.4f} nV, i_n {row['i_n'] * 1e15:10.3f} fA; shorted input: "
                  + ", ".join(f"{k} {v * 1e9:.4f}" for k, v in row["groups_shorted_input"].items()))
    np.savez(npz, **data)
    res["flicker_check"] = flicker_check()
    print("flicker check on one NPN:", res["flicker_check"])
    if "JFE150_L" in res:
        cn = np.load(spice.RESULTS / "curves_noise.npz")
        fl, jl = cn["L200_f"], cn["L200_g_input JFETs"]
        chk = {}
        for f0 in F_REPORT[:6]:
            mine = res["JFE150_L"]["at"][f"{f0:g}"]["e_n"]
            ref = float(jl[int(np.argmin(np.abs(np.log10(fl) - np.log10(f0))))])
            chk[f"{f0:g}"] = dict(testbench=mine, front_end_group=ref, ratio=mine / ref)
        res["check_JFE150_L_against_L200"] = chk
        print("check against L200_g_input JFETs:", {k: round(v["ratio"], 4) for k, v in chk.items()})
    js.write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    if sys.argv[1:2] == ["fe"]:
        sys.stdout.reconfigure(encoding="utf-8")
        models.prepare()
        fe_stage()
    else:
        main(sys.argv[1:])
