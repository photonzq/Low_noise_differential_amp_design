"""What sets the -3 dB bandwidth of the SR560 reproduction (sr560_chain.py): AC runs only.

The note's Section 2.2 gives the reproduced chain's -3 dB bandwidth as 0.73-0.79 MHz at every gain,
against the manual's 1 MHz, and attributes the shortfall to the first-order LF356 and LF411
models.  This script tests that with AC analyses of the unchanged netlist (sr560_chain.netlist and
sr560_chain.deck, run through sr560_chain.trimmed and sr560_chain.run_ac), each a few seconds of
ngspice; no transient, noise or Monte Carlo analysis.

(a) Reproduction: the chain at gains of 1, 100 and 1000 (low-noise mode), trimmed and calibrated
    exactly as sr560_chain.py does (trimmed(allocate(g, "LN"), g)), against the archived
    sr560_chain.json ac.<g>.f3db and the archived curves sr560_chain_ac_<g>.npz.
(b) The LF356 (U204, U303) and LF411 (U103, U404) ten times faster.
(c) One stage at a time ten times faster; then every op amp after the front end, and finally
    every op amp, 1000 times faster ("ideal"), with the LM6321's pole moved likewise.
(d) The front end alone (sr560_frontend.front_end, x10 and x2, output v(out), the source and
    the analysis of sr560_frontend.run_case), against the archived sr560_frontend.json, and with
    its OP37 faster or fitted to the OP37 data sheet.
(e) Op-amp dynamics taken from the data sheets instead of the model's poles: the OP37 and LT1028
    fitted to their gain-phase plots (vector curves read from the archived PDFs, see
    fit_gain_phase), the LF356 and LF411 as two-pole fits to readings of their bitmap Bode plots
    (BITMAP_READINGS); and the data sheets' open-loop output resistances.
(f) Documentation checks (ADD_C406, C301_47P): C406 = 82 pF around U403, drawn on the schematic and
    in the parts list but not in the netlist, and C301 at the parts list's 47 pF instead of the
    schematic's 6.8 pF; alone, with ideal op amps and with the data-sheet dynamics of (e).  These
    test the reading of the documents, not the op-amp models.

"k times faster": every internal time constant of the behavioural op amp (blocks.opn) divided by
k, i.e. its C1 and C2 divided by k.  At fixed gm1 and R1 this multiplies the gain-bandwidth
product, the second pole and the slew rate by k and leaves the DC gain A0 and the input stage's
linear range sr / (2 pi gbw) unchanged, so the operating point and the offset trim are those of
the archived runs.  Raising the GBW alone would move an OP37 or LT1028 loop's crossover beyond its
second pole and make the stage ring.

Passive closed forms (passive_closed_forms): the feedback and filter-node networks with ideal op
amps, from the component values of sr560_chain.netlist().

Data sheets (../refs/datasheets/opamp/, README there): ADI_op37_datasheet.pdf (OP37 Rev. B),
ADI_lt1028_datasheet.pdf (LT1028/LT1128 Rev. D), TI_lf356_datasheet.pdf (SNOSBH0D),
TI_lf411-n_datasheet.pdf (SNOSBH6E), TI_lm6321_datasheet.pdf (SNOSC10B).

Usage: python sr560_bw_check.py      (about 90 ngspice runs, each a few seconds; needs SciPy and
PyMuPDF for the plot fits).  Results: ../sim/results/sr560_bw_check.json and
sr560_bw_check_log.txt; decks under ../sim/runs/sr560_bw_check/.
"""
from __future__ import annotations

import json
import math
import re
import sys

import numpy as np

import spice
import sr560_chain as SC
import sr560_frontend as FE

RUNS = "sr560_bw_check"
GAINS = (1, 100, 1000)
OUT = spice.RESULTS / "sr560_bw_check.json"
LOG = spice.RESULTS / "sr560_bw_check_log.txt"
DS = spice.ROOT / "refs" / "datasheets" / "opamp"
BASE = {"OP37": FE.OP37, "LF411": FE.LF411, "LT1028": SC.LT1028, "LF356": SC.LF356}
F_REPORT = (3e5, 7.3e5, 1e6)          # frequencies at which closed forms are tabulated

_LOG: list[str] = []


def log(msg: str = "") -> None:
    print(msg)
    _LOG.append(msg)


# ------------------------------------------------------------------------------------------------
# SPICE values and subcircuit text
# ------------------------------------------------------------------------------------------------
_SUFFIX = {"t": 1e12, "g": 1e9, "meg": 1e6, "k": 1e3, "m": 1e-3, "u": 1e-6, "n": 1e-9, "p": 1e-12,
           "f": 1e-15}


def spice_value(text: str) -> float:
    """A SPICE number with an optional scale suffix (3.18n, 4.3k, 100Meg)."""
    m = re.fullmatch(r"([-+0-9.eE]+)(meg|[tgkmunpf])?[a-z]*", text.strip().lower())
    if not m:
        raise ValueError(f"not a SPICE value: {text!r}")
    return float(m.group(1)) * _SUFFIX.get(m.group(2) or "", 1.0)


def component(netlist: str, name: str) -> float:
    """Value of the two-terminal element `name` (R, C) in a netlist."""
    m = re.search(rf"^{re.escape(name)} \S+ \S+ (\S+)", netlist, re.M)
    if not m:
        raise KeyError(name)
    return spice_value(m.group(1))


def _val(text: str, pattern: str) -> float:
    m = re.search(pattern, text, re.M)
    if not m:
        raise ValueError(f"{pattern!r} not found")
    return float(m.group(1))


def _sub1(text: str, pattern: str, repl: str) -> str:
    new, n = re.subn(pattern, repl, text, flags=re.M)
    if n != 1:
        raise ValueError(f"{pattern!r} matched {n} times")
    return new


def _rename(text: str, new: str) -> str:
    old = re.search(r"^\.subckt (\S+) ", text, re.M).group(1)
    return text.replace(f".subckt {old} ", f".subckt {new} ").replace(f".ends {old}", f".ends {new}")


def opn_params(text: str) -> dict:
    """GBW (dominant pole extrapolated), A0, fp2 and rout of a blocks.opn subcircuit, read back from
    its text: gbw = gm1 / (2 pi C1), A0 = gm1 R1, fp2 = 1 / (2 pi R2 C2) with R2 = 1 ohm."""
    gm1 = _val(text, r"tanh\(([-+0-9.eE]+)\*")
    c1 = _val(text, r"^C1 n1 0 (\S+)$")
    r1 = _val(text, r"^R1 n1 0 (\S+) rnl$")
    c2 = re.search(r"^C2 n3 0 (\S+)$", text, re.M)
    return dict(gbw=gm1 / (2 * math.pi * c1), a0=gm1 * r1,
                fp2=1 / (2 * math.pi * float(c2.group(1))) if c2 else 0.0,
                rout=_val(text, r"^Ro no out (\S+) rnl$"))


def opn_noise(text: str) -> dict:
    """en, fce, inoise, fci of a blocks.opn subcircuit, read back from its generators (inverse of
    blocks.opn): with a 1/f part, Hfv's gain is k_d = en / (2 SHOT) and the diode's
    KF = en^2 fce / (k_d^2 I_DIODE); without one, Hnv's gain is en / I1OHM.  Likewise for the
    current noise of the non-inverting input (Ffip, dflk_ip; or Fnip alone)."""
    import blocks
    out = {}
    m = re.search(r"^Hfv ip1 ip2 Vfv (\S+)$", text, re.M)
    if m:
        kd = float(m.group(1))
        en = 2 * kd * blocks.SHOT
        kf = _val(text, r"^\.model dflk_v d\(.*kf=(\S+) af=1\)$")
        out.update(en=en, fce=kf * kd ** 2 * blocks.I_DIODE / en ** 2)
    else:
        out.update(en=_val(text, r"^Hnv inp ip1 Vnv (\S+)$") * blocks.I1OHM, fce=0.0)
    m = re.search(r"^Ffip 0 inp Vfip (\S+)$", text, re.M)
    if m:
        kd = float(m.group(1))
        i_n = 2 * kd * blocks.SHOT
        kf = _val(text, r"^\.model dflk_ip d\(.*kf=(\S+) af=1\)$")
        out.update(inoise=i_n, fci=kf * kd ** 2 * blocks.I_DIODE / i_n ** 2)
    elif re.search(r"^Fnip 0 inp Vnip ", text, re.M):
        out.update(inoise=_val(text, r"^Fnip 0 inp Vnip (\S+)$") * blocks.I1OHM, fci=0.0)
    else:
        out.update(inoise=0.0, fci=0.0)
    return out


def faster(model: str, k: float, name: str) -> str:
    """The blocks.opn subcircuit of `model` with C1 and C2 divided by k (module docstring)."""
    t = _rename(BASE[model], name)
    t = _sub1(t, r"^C1 n1 0 \S+$", f"C1 n1 0 {_val(t, r'^C1 n1 0 (\S+)$') / k:.6g}")
    if re.search(r"^C2 n3 0 ", t, re.M):
        t = _sub1(t, r"^C2 n3 0 \S+$", f"C2 n3 0 {_val(t, r'^C2 n3 0 (\S+)$') / k:.6g}")
    return t


def refit(model: str, name: str, gbw: float, poles=(), doublet=None) -> str:
    """The blocks.opn subcircuit of `model` with its dynamics replaced: dominant pole extrapolated
    to `gbw` (C1 scaled; A0, the input stage and the noise generators unchanged), the second-pole
    stage replaced by `poles` (Hz; each a unity buffer driving 1 ohm into a capacitor) and, if
    given, a lag doublet (fp, fz), fp < fz: a unity buffer, Ra in series, Rb and Cd to ground,
    H = (1 + s Rb Cd) / (1 + s (Ra + Rb) Cd)."""
    t = _rename(BASE[model], name)
    c1 = _val(t, r"^C1 n1 0 (\S+)$")
    t = _sub1(t, r"^C1 n1 0 \S+$", f"C1 n1 0 {c1 * opn_params(BASE[model])['gbw'] / gbw:.6g}")
    t, n = re.subn(r"^E2 n2 0 n1 0 1\nR2 n2 n3 1 rnl\nC2 n3 0 \S+\n", "", t, flags=re.M)
    if n == 0:
        t = _sub1(t, r"^E2 n3 0 n1 0 1\n", "")
    lines, node = [], "n1"
    for i, fp in enumerate(poles, 1):
        lines += [f"Ep{i} pq{i} 0 {node} 0 1", f"Rp{i} pq{i} pr{i} 1 rnl",
                  f"Cp{i} pr{i} 0 {1 / (2 * math.pi * fp):.6g}"]
        node = f"pr{i}"
    if doublet:
        fp, fz = doublet
        cd = 1e-9
        rb = 1 / (2 * math.pi * fz * cd)
        ra = 1 / (2 * math.pi * fp * cd) - rb
        lines += [f"Ed dq0 0 {node} 0 1", f"Rda dq0 dq1 {ra:.6g} rnl", f"Rdb dq1 dq2 {rb:.6g} rnl",
                  f"Cdb dq2 0 {cd:g}"]
        node = "dq1"
    t = _sub1(t, r"^Bo no 0 V=min\(max\(V\(n3\),", "\n".join(lines) + f"\nBo no 0 V=min(max(V({node}),")
    return t


def with_rout(model: str, name: str, rout: float) -> str:
    return _sub1(_rename(BASE[model], name), r"^Ro no out \S+ rnl$", f"Ro no out {rout:g} rnl")


def open_loop(gbw, poles=(), doublet=None):
    """A(f) of the dynamics used by faster/refit (dominant pole far below the band of interest)."""
    def a(f):
        f = np.asarray(f, dtype=float)
        jf = 1j * f
        h = gbw / jf
        for fp in poles:
            h = h / (1 + jf / fp)
        if doublet:
            h = h * (1 + jf / doublet[1]) / (1 + jf / doublet[0])
        return h
    return a


def crossing(a, level: float, lo=1e4, hi=1e9) -> tuple[float, float]:
    """Frequency where |a(f)| = level (bisection in log f) and the phase margin 180 + arg a there."""
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        if abs(a(mid)) > level:
            lo = mid
        else:
            hi = mid
    f = math.sqrt(lo * hi)
    return f, 180.0 + math.degrees(float(np.angle(a(f))))


# ------------------------------------------------------------------------------------------------
# Deck edits
# ------------------------------------------------------------------------------------------------
def make_edit(models: dict[str, str], subckts: dict[str, str], pole406: float | None = None,
              replace: dict[str, str] | None = None, add: list[str] | None = None):
    """Deck editor: instance (U102, ...) -> new model name, the new subcircuits' text, an
    optional factor by which the LM6321's pole capacitor C406P is divided, element lines to
    replace (regex of the whole line -> new line, each matching once) and element lines to add."""
    def edit(deck: str) -> str:
        for inst, new in models.items():
            deck = _sub1(deck, rf"^(X{inst} .* )\S+$", rf"\g<1>{new}")
        if pole406:
            c = spice_value(re.search(r"^C406P c406 0 (\S+)$", deck, re.M).group(1))
            deck = _sub1(deck, r"^C406P c406 0 \S+$", f"C406P c406 0 {c / pole406:.6g}")
        for pat, new in (replace or {}).items():
            deck = _sub1(deck, pat, new)
        if add:
            deck = _sub1(deck, r"^\.control$", "\n".join(add) + "\n.control")
        head, rest = deck.split("\n", 1)
        return head + "\n" + "".join(subckts.values()) + rest
    return edit


def compose(*edits):
    def edit(deck: str) -> str:
        for e in edits:
            deck = e(deck)
        return deck
    return edit


# Parts of the SR560's documentation that the reproduction's netlist does not follow (manual
# Rev. 2.8): C406 = 82 pF from U403's output (pin 6) to its inverting input, drawn on sheet
# 560_4F (PDF p. 50) and listed as 82P in the parts list (PDF p. 36), is not in
# sr560_chain.netlist; C301 is drawn as 6.8 pF on sheet 560_3F (PDF p. 49), as modelled, but
# listed as 47P (5-00017-501, the part number of the 47 pF C401) in the parts list (PDF p. 35).
ADD_C406 = make_edit({}, {}, add=["C406 o403 n403 82p"])
C301_47P = make_edit({}, {}, replace={r"^C301 c301 n305 \S+$": "C301 c301 n305 47p"})


STAGES = [("U102", ["U102"], False, "front end: OP37 U102"),
          ("U103", ["U103"], False, "front-end tail servo: LF411 U103"),
          ("U105", ["U105"], False, "LT1028 U105 (x10.09, C111 68 pF)"),
          ("U204", ["U204"], False, "filter-1 buffer: LF356 U204"),
          ("U201", ["U201"], False, "OP37 U201 (x5.23, R229 + C201 across R217)"),
          ("U303", ["U303"], False, "filter-2 buffer: LF356 U303"),
          ("U305", ["U305"], False, "OP37 U305 (x5.23, R330 + C301 across R315)"),
          ("U402", ["U402"], False, "LT1028 U402 (x5.23, C401 47 pF)"),
          ("U404", ["U404"], False, "vernier: LF411 U404 (C407 3 pF)"),
          ("U403+U406", ["U403"], True, "output stage: OP37 U403 and the LM6321 U406 in its loop")]
OPAMP_OF = {"U102": "OP37", "U103": "LF411", "U105": "LT1028", "U204": "LF356", "U201": "OP37",
            "U303": "LF356", "U305": "OP37", "U402": "LT1028", "U404": "LF411", "U403": "OP37"}


def speedup(insts: list[str], k: float, lm6321: bool) -> tuple:
    models, subs = {}, {}
    for i in insts:
        m = OPAMP_OF[i]
        nm = f"{m}_X{k:g}"
        models[i] = nm
        subs[nm] = faster(m, k, nm)
    return make_edit(models, subs, k if lm6321 else None)


# ------------------------------------------------------------------------------------------------
# Data-sheet readings and fits
# ------------------------------------------------------------------------------------------------
# Bitmap plots (scanned figures): readings of the curve centres, in nV/rtHz or dB and degrees,
# from pixel columns of the page rendered at 600 dpi with the plot's own gridlines as the scale.
BITMAP_READINGS = {
    "LF356 noise": dict(
        doc="TI_lf356_datasheet.pdf (SNOSBH0D)", page="p. 13 (PyMuPDF index 12)",
        figure="Figure 33, Equivalent Input Noise Voltage (Expanded Scale), LF156/LF357 curve",
        white_nV=12.0, white_source="p. 5, 6.5: e_n 12 nV/rtHz at 1 kHz (LFx56 typ)",
        points=[(15, 41.0), (20, 33.1), (30, 25.7), (50, 19.7), (100, 14.7), (200, 12.3), (1e4, 12.0)],
        table=[(100, 15.0), (1000, 12.0)], table_source="p. 5, 6.5: e_n 15 at 100 Hz, 12 at 1 kHz"),
    "LF411 noise": dict(
        doc="TI_lf411-n_datasheet.pdf (SNOSBH6E)", page="p. 8 (PyMuPDF index 7)",
        figure="Figure 18, Equivalent Input Noise Voltage",
        white_nV=25.0, white_source="p. 5, 6.6: e_n 25 nV/rtHz at 1 kHz (LF411 typ)",
        points=[(10.5, 51.5), (15, 44.3), (20, 40.2), (30, 36.1), (50, 32.0), (100, 28.6), (200, 26.8),
                (1000, 25.1), (5e4, 24.8)],
        stated_corner_Hz=50.0, stated_source="p. 1, Features: Low 1/f noise corner 50 Hz"),
    "LF356 Bode": dict(
        doc="TI_lf356_datasheet.pdf (SNOSBH0D)", page="p. 12 (PyMuPDF index 11)",
        figure="Figure 26, Bode Plot, LF156, Vs = +/-15 V (open loop measured at a gain of -100)",
        points=[(4.57e6, 0.48, 77.4), (5.21e6, -0.41, 74.4)],
        note="(f, gain dB, phase deg); the phase axis reads 50 deg at 0 dB, i.e. phase margin"),
    "LF411 Bode": dict(
        doc="TI_lf411-n_datasheet.pdf (SNOSBH6E)", page="p. 7 (PyMuPDF index 6)",
        figure="Figure 11, Bode Plot, R_L = 2 k, C_L = 100 pF",
        points=[(2.375e6, 4.89, 74.5), (2.85e6, 3.26, 68.0), (3.21e6, 2.2, 63.4), (3.62e6, 1.15, 58.2),
                (4.63e6, -0.8, 46.2)],
        note="(f, gain dB, phase deg); phase axis reads 0 deg at 0 dB, i.e. phase margin; the 100 pF"
             " load lowers the phase above 3 MHz, so the fit uses the 2.375 MHz point, where the"
             " vernier's loop crosses over (noise gain 1.4-1.8)"),
}

# Vector plots: curves extracted from the PDF drawing commands (no reading by eye).
VECTOR_PLOTS = {
    "OP37": dict(pdf="ADI_op37_datasheet.pdf", index=7, printed=8,
                 figure="TPC 18, Gain, Phase Shift vs. Frequency (T_A = 25 C, Vs = +/-15 V)",
                 hint=(390, 455, 600, 615), f=(1e5, 1e8), gain=(60.0, -10.0), phase=(-80.0, -220.0),
                 margin=False, fmax=10e6, guess=(55e6, 0.8e6, 1.5e6, 18e6)),
    "LT1028": dict(pdf="ADI_lt1028_datasheet.pdf", index=7, printed=8,
                   figure="LT1028 Gain, Phase vs Frequency (1028 G20; Vs = +/-15 V, C_L = 10 pF)",
                   hint=(210, 115, 400, 305), f=(1e4, 1e8), gain=(70.0, -10.0), phase=(70.0, -10.0),
                   margin=True, fmax=20e6, guess=(86e6, 0.75e6, 2.7e6, 21e6, 40e6)),
}


def _bezier(p0, p1, p2, p3, n=24):
    t = np.linspace(0, 1, n)[:, None]
    p = [np.array([q.x, q.y]) for q in (p0, p1, p2, p3)]
    return (1 - t) ** 3 * p[0] + 3 * (1 - t) ** 2 * t * p[1] + 3 * (1 - t) * t ** 2 * p[2] + t ** 3 * p[3]


def vector_curves(spec: dict) -> dict:
    """Gain and phase curves of a vector plot: the frame is the largest single rectangle near
    spec['hint'] (points); the curves are the stroked Bezier paths inside it; the gain curve is the
    one that starts further left.  Frame edges = the axis limits printed on the figure."""
    import pymupdf
    page = pymupdf.open(DS / spec["pdf"])[spec["index"]]
    hint = pymupdf.Rect(*spec["hint"])
    draws = page.get_drawings()
    frames = [d for d in draws if d["rect"].intersects(hint) and len(d["items"]) == 1
              and d["items"][0][0] == "re"]
    fr = max(frames, key=lambda d: d["rect"].width * d["rect"].height)["rect"]
    paths = []
    for d in draws:
        if not d["rect"].intersects(fr) or not any(i[0] == "c" for i in d["items"]):
            continue
        pts = [_bezier(*i[1:5]) if i[0] == "c" else np.array([[i[1].x, i[1].y], [i[2].x, i[2].y]])
               for i in d["items"] if i[0] in ("c", "l")]
        paths.append(np.concatenate(pts))
    if len(paths) != 2:
        raise RuntimeError(f"{spec['pdf']}: expected 2 curves, found {len(paths)}")
    paths.sort(key=lambda p: p[:, 0].min())
    out = {}
    for key, p, (top, bot) in (("gain", paths[0], spec["gain"]), ("phase", paths[1], spec["phase"])):
        f = spec["f"][0] * (spec["f"][1] / spec["f"][0]) ** ((p[:, 0] - fr.x0) / (fr.x1 - fr.x0))
        v = top - (top - bot) * (p[:, 1] - fr.y0) / (fr.y1 - fr.y0)
        o = np.argsort(f)
        out[key] = (f[o], v[o])
    out["frame_pt"] = [round(float(x), 2) for x in (fr.x0, fr.y0, fr.x1, fr.y1)]
    return out


def fit_gain_phase(spec: dict) -> dict:
    """Least-squares fit of A(f) = GBW / (j f) (1 + j f/fz) / (1 + j f/fp) prod 1/(1 + j f/f_k) to the
    plotted gain (dB) and phase (deg, weight 0.2 dB per degree) up to spec['fmax']."""
    from scipy.optimize import least_squares
    c = vector_curves(spec)
    fg, g = c["gain"]
    fph, ph = c["phase"]
    mg, mp = fg <= spec["fmax"], fph <= spec["fmax"]

    def model(p, f):
        v = np.exp(p)
        return open_loop(v[0], poles=tuple(v[3:]), doublet=(v[1], v[2]))(f)

    def res(p):
        r1 = 20 * np.log10(np.abs(model(p, fg[mg]))) - g[mg]
        phs = np.degrees(np.unwrap(np.angle(model(p, fph[mp]))))
        if spec["margin"]:
            phs = 180 + phs
        return np.concatenate([r1, 0.2 * (phs - ph[mp])])

    r = least_squares(res, np.log(spec["guess"]))
    v = np.exp(r.x)
    fit = dict(gbw=float(v[0]), doublet=(float(v[1]), float(v[2])), poles=tuple(float(x) for x in v[3:]))
    a = open_loop(fit["gbw"], fit["poles"], fit["doublet"])
    plot_at = {}
    for f0 in (1e5, 7.3e5, 1e6, 2e6, 5e6, 1e7):
        if fg[0] <= f0 <= fg[-1]:
            gd = float(np.interp(math.log10(f0), np.log10(fg), g))
            pd = float(np.interp(math.log10(f0), np.log10(fph), ph)) if fph[0] <= f0 <= fph[-1] else None
            af = complex(a(f0))
            pf = math.degrees(math.atan2(af.imag, af.real))
            plot_at[f"{f0:g}"] = dict(plot_dB=round(gd, 2), plot_phase=None if pd is None else round(pd, 1),
                                      fit_dB=round(20 * math.log10(abs(af)), 2),
                                      fit_phase=round(180 + pf if spec["margin"] else pf, 1))
    return dict(figure=spec["figure"], pdf=spec["pdf"], printed_page=spec["printed"],
                pymupdf_index=spec["index"], frame_pt=c["frame_pt"],
                axes=dict(f_Hz=spec["f"], gain_dB_top_bottom=spec["gain"],
                          phase_deg_top_bottom=spec["phase"],
                          phase_kind="phase margin" if spec["margin"] else "phase shift"),
                fit_range_Hz=[float(fg[0]), spec["fmax"]], fit=fit,
                rms_residual=float(np.sqrt(np.mean(r.fun ** 2))), max_residual=float(np.abs(r.fun).max()),
                plot_vs_fit=plot_at, curves=dict(gain=c["gain"], phase=c["phase"]))


def plot_crossing(fit: dict, level_dB: float) -> dict:
    """Where the plotted gain curve crosses level_dB, and the plotted phase there."""
    fg, g = fit["curves"]["gain"]
    fph, ph = fit["curves"]["phase"]
    k = int(np.where(g < level_dB)[0][0])
    lf = float(np.interp(level_dB, [g[k], g[k - 1]], [math.log10(fg[k]), math.log10(fg[k - 1])]))
    return dict(f_MHz=round(10 ** lf / 1e6, 3), phase=round(float(np.interp(lf, np.log10(fph), ph)), 1))


def two_pole(f: float, gain_dB: float, pm: float) -> dict:
    """GBW and second pole of A = GBW / (j f (1 + j f/fp2)) through one reading (f, |A|, margin)."""
    fp2 = f / math.tan(math.radians(90.0 - pm))
    return dict(gbw=10 ** (gain_dB / 20) * f * math.sqrt(1 + (f / fp2) ** 2), fp2=fp2)


def datasheet_readings() -> dict:
    out = {}
    for key in ("LF356 noise", "LF411 noise"):
        r = dict(BITMAP_READINGS[key])
        w = r["white_nV"]
        r["corner_Hz_from_points"] = {f"{f:g}": round(f * ((e / w) ** 2 - 1), 1) for f, e in r["points"]
                                      if f <= 300}
        r["corner_equation"] = "e^2 = w^2 (1 + fc/f)  ->  fc = f ((e/w)^2 - 1), w = white level"
        if "table" in r:
            (f1, e1), (f2, e2) = r["table"]
            # two points, both on e^2 = w^2 (1 + fc/f): solve for fc and w
            ratio = (e1 / e2) ** 2
            fc = (ratio - 1) / (1 / f1 - ratio / f2)
            r["corner_from_table_Hz"] = dict(white_12_assumed=round(f1 * ((e1 / w) ** 2 - 1), 1),
                                             two_point_solution=round(fc, 1),
                                             white_two_point=round(e2 / math.sqrt(1 + fc / f2), 2))
        out[key] = r
    lf356 = BITMAP_READINGS["LF356 Bode"]["points"]
    (fa, ga, pa), (fb, gb, pb) = lf356
    x = ga / (ga - gb)                                      # 0 dB crossing, interpolated in log f
    fc = 10 ** (math.log10(fa) + x * (math.log10(fb) - math.log10(fa)))
    pm = pa + x * (pb - pa)
    out["LF356 Bode"] = dict(BITMAP_READINGS["LF356 Bode"], crossover_MHz=round(fc / 1e6, 3),
                             phase_margin=round(pm, 1), two_pole=two_pole(fc, 0.0, pm))
    f0, g0, p0 = BITMAP_READINGS["LF411 Bode"]["points"][0]
    pts = BITMAP_READINGS["LF411 Bode"]["points"]
    (fa, ga, pa), (fb, gb, pb) = pts[-2], pts[-1]
    x = ga / (ga - gb)
    fcx = 10 ** (math.log10(fa) + x * (math.log10(fb) - math.log10(fa)))
    out["LF411 Bode"] = dict(BITMAP_READINGS["LF411 Bode"], crossover_MHz=round(fcx / 1e6, 3),
                             phase_margin_at_crossover=round(pa + x * (pb - pa), 1),
                             two_pole=two_pole(f0, g0, p0), two_pole_point=dict(f=f0, gain_dB=g0, pm=p0))
    return out


# ------------------------------------------------------------------------------------------------
# Closed forms of the passive networks (ideal op amps)
# ------------------------------------------------------------------------------------------------
def passive_closed_forms(netlist: str, x2: bool) -> dict:
    """|H(f) / H(0)| in dB of each network of the signal path with ideal op amps, from the
    component values of the netlist (equations in 'eq')."""
    v = {n: component(netlist, n) for n in ("R123", "C111", "R124", "R217", "R229", "C201", "R215",
                                             "R315", "R330", "C301", "R313", "R403", "C401", "R404",
                                             "RFB", "C407", "R116", "C116", "RA1051", "RA1052", "RA1053",
                                             "RU104", "RF1BYP", "CF1MUX", "RF2BYP", "CF2MUX")}
    w = lambda f: 2 * math.pi * f
    par = lambda a, b: a * b / (a + b)
    zc = lambda c, f: 1 / (1j * w(f) * c)
    nets = {
        "U105 (R123 || C111, R124)": ("1 + (R123 || 1/(jwC111)) / R124",
                                      lambda f: 1 + par(v["R123"], zc(v["C111"], f)) / v["R124"]),
        "U201 (R217 || (R229 + C201), R215)": ("1 + (R217 || (R229 + 1/(jwC201))) / R215",
                                               lambda f: 1 + par(v["R217"], v["R229"] + zc(v["C201"], f)) / v["R215"]),
        "U305 (R315 || (R330 + C301), R313)": ("1 + (R315 || (R330 + 1/(jwC301))) / R313",
                                               lambda f: 1 + par(v["R315"], v["R330"] + zc(v["C301"], f)) / v["R313"]),
        "U402 (R403 || C401, R404)": ("1 + (R403 || 1/(jwC401)) / R404",
                                      lambda f: 1 + par(v["R403"], zc(v["C401"], f)) / v["R404"]),
        "vernier (RFB || C407)": ("(RFB || 1/(jwC407)) / RDAC", lambda f: par(v["RFB"], zc(v["C407"], f))),
        "filter-1 node (RU104 + RF1BYP, CF1MUX)": ("1 / (1 + jw (RU104 + RF1BYP) CF1MUX)",
                                                   lambda f: 1 / (1 + 1j * w(f) * (v["RU104"] + v["RF1BYP"]) * v["CF1MUX"])),
        "filter-2 node (RF2BYP, CF2MUX)": ("1 / (1 + jw RF2BYP CF2MUX)",
                                           lambda f: 1 / (1 + 1j * w(f) * v["RF2BYP"] * v["CF2MUX"])),
    }
    if x2:
        ra = v["RA1051"] + v["RA1052"] + v["RA1053"]
        nets["K102 x2 path (R116, C116, A105 load)"] = (
            "Ra / (R116 + Ra + jw R116 Ra C116), Ra = RA1051 + RA1052 + RA1053",
            lambda f: ra / (v["R116"] + ra + 1j * w(f) * v["R116"] * ra * v["C116"]))
    # documentation checks, not in the netlist (see ADD_C406, C301_47P): U403 with C406 = 82 pF across
    # R408 (ideal op amp and buffer, R437 neglected), and U305 with C301 = 47 pF
    r408, r425 = component(netlist, "R408"), component(netlist, "R425")
    checks = {
        "U403 with C406 = 82 pF (not in the netlist)": (
            "1 + (R408 || 1/(jw 82 pF)) / R425", lambda f: 1 + par(r408, zc(82e-12, f)) / r425),
        "U305 with C301 = 47 pF (parts list) instead of 6.8 pF": (
            "1 + (R315 || (R330 + 1/(jw 47 pF))) / R313",
            lambda f: 1 + par(v["R315"], v["R330"] + zc(47e-12, f)) / v["R313"]),
    }
    out = {}
    tot = {f"{f / 1e6:g}": 0.0 for f in F_REPORT}
    for name, (eq, h) in list(nets.items()) + list(checks.items()):
        h0 = h(1.0)
        d = {f"{f / 1e6:g}": round(20 * math.log10(abs(h(f) / h0)), 3) for f in F_REPORT}
        if name in nets:
            for k_ in tot:
                tot[k_] += d[k_]
        out[name] = dict(eq=eq, dB_at_MHz=d)
    out["sum"] = {k_: round(x, 3) for k_, x in tot.items()}
    out["sum_note"] = "sum over the networks of the netlist (not the two documentation checks)"
    out["values"] = v | dict(R408=r408, R425=r425)
    return out


# ------------------------------------------------------------------------------------------------
# Runs
# ------------------------------------------------------------------------------------------------
def summarize(f: np.ndarray, h: np.ndarray, ref_1k: bool = True) -> dict:
    mag = np.abs(h)
    ref = spice.at(f, mag, 1e3) if ref_1k else float(mag[0])
    db = 20 * np.log10(mag / ref)
    k = int(np.argmax(db))
    return dict(f3db_MHz=spice.f3db(f, mag, ref) / 1e6, gain_ref=ref,
                dB_300k=float(np.interp(math.log10(3e5), np.log10(f), db)),
                dB_1M=float(np.interp(math.log10(1e6), np.log10(f), db)),
                peak_dB=float(db[k]), f_peak_MHz=float(f[k] / 1e6))


def chain_run(s: SC.SRSetting, name: str, edit) -> dict:
    r = SC.run_ac(s, tag=name, runs=f"{RUNS}/chain", edit=edit)
    res = summarize(r["f"], r["h"])
    res["op_out50"] = spice.printed(spice.RUNS / RUNS / "chain" / s.tag / name, "v(out50)")
    return res, r


FE_CTL = ".control\n" + spice.WR + "op\nprint v(out)\nac dec 20 1 100meg\nwrdata ac.txt v(out)\n.endc\n"


def fe_run(gain10: bool, name: str, edit) -> dict:
    """The front end alone with sr560_frontend.run_case's source and AC sweep (20 points per
    decade, -3 dB from the 1 Hz value), output v(out)."""
    tag = f"{RUNS}/frontend/{'x10' if gain10 else 'x2'}/{name}"
    deck = FE.deck(tag, FE.front_end(gain10), SC.SRC_DM, FE_CTL)
    folder = spice.run(tag, edit(deck) if edit else deck)
    d = spice.read_table(folder / "ac.txt")
    res = summarize(d["frequency"], d["v(out)"], ref_1k=False)
    res["gain_1k"] = spice.at(d["frequency"], np.abs(d["v(out)"]), 1e3)
    res["op_out"] = spice.printed(folder, "v(out)")
    return res


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if not (spice.LIB / "jfets.lib").exists():
        raise SystemExit("../sim/models/_lib/jfets.lib missing: run models.py first")
    res: dict = dict(
        description=__doc__.split("\n\n")[0],
        archived_inputs=dict(chain="sim/results/sr560_chain.json, key ac.<gain>.f3db (Hz); curves "
                                   "sr560_chain_ac_<gain>.npz",
                             frontend="sim/results/sr560_frontend.json, key sr560_x10_2N5564.f3db (Hz)"))
    # ---- data-sheet readings and fits (no simulation)
    log("== Data-sheet readings")
    ds = datasheet_readings()
    fits = {m: fit_gain_phase(VECTOR_PLOTS[m]) for m in VECTOR_PLOTS}
    model_x = {}
    for m, level in (("OP37", 5.225), ("LT1028", 10.09), ("LT1028 at 5.23", 5.225), ("LF356", 1.0),
                     ("LF411", 1.0)):
        p = opn_params(BASE[m.split()[0]])
        a = open_loop(p["gbw"], (p["fp2"],) if p["fp2"] else ())
        fx, pm = crossing(a, level)
        model_x[m] = dict(level=level, f_MHz=round(fx / 1e6, 3), phase_margin=round(pm, 1),
                          gbw=p["gbw"], fp2=p["fp2"], a0=p["a0"], rout=p["rout"])
    for m in fits:
        x = fits[m]
        log(f"{m}: {x['figure']} (printed p. {x['printed_page']}, PyMuPDF index {x['pymupdf_index']}); fit "
            f"GBW {x['fit']['gbw'] / 1e6:.1f} MHz, doublet {x['fit']['doublet'][0] / 1e6:.3f}/"
            f"{x['fit']['doublet'][1] / 1e6:.3f} MHz, poles {[round(q / 1e6, 1) for q in x['fit']['poles']]} MHz; "
            f"rms residual {x['rms_residual']:.2f} (dB, 5 deg = 1)")
        for f0, row in x["plot_vs_fit"].items():
            log(f"   {float(f0) / 1e6:6.3f} MHz: plot {row['plot_dB']:6.2f} dB {row['plot_phase']}, "
                f"fit {row['fit_dB']:6.2f} dB {row['fit_phase']}")
    fits["OP37"]["plot_crossing_x5"] = plot_crossing(fits["OP37"], 20 * math.log10(5))
    fits["LT1028"]["plot_crossing_20dB"] = plot_crossing(fits["LT1028"], 20.0)
    fits["LT1028"]["plot_crossing_x5.23"] = plot_crossing(fits["LT1028"], 20 * math.log10(5.225))
    fits["LT1028"]["plot_crossing_0dB"] = plot_crossing(fits["LT1028"], 0.0)
    log(f"OP37 plot |A| = 5 at {fits['OP37']['plot_crossing_x5']}; model (gbw/fp2) |A| = 5.225 at "
        f"{model_x['OP37']['f_MHz']} MHz, margin {model_x['OP37']['phase_margin']}")
    log(f"LT1028 plot 20 dB at {fits['LT1028']['plot_crossing_20dB']}, 14.4 dB at "
        f"{fits['LT1028']['plot_crossing_x5.23']}, 0 dB at {fits['LT1028']['plot_crossing_0dB']}; model "
        f"|A| = 10.09 at {model_x['LT1028']['f_MHz']} MHz, margin {model_x['LT1028']['phase_margin']}")
    for k_ in ("LF356 noise", "LF411 noise"):
        log(f"{k_}: corners from {ds[k_]['figure']}: {ds[k_]['corner_Hz_from_points']}"
            + (f"; from the table {ds[k_]['corner_from_table_Hz']}" if "corner_from_table_Hz" in ds[k_] else ""))
    log(f"LF356 Bode: crossover {ds['LF356 Bode']['crossover_MHz']} MHz, margin {ds['LF356 Bode']['phase_margin']}"
        f" -> two-pole {ds['LF356 Bode']['two_pole']}")
    log(f"LF411 Bode: crossover {ds['LF411 Bode']['crossover_MHz']} MHz, margin "
        f"{ds['LF411 Bode']['phase_margin_at_crossover']} (C_L = 100 pF); two-pole through "
        f"{ds['LF411 Bode']['two_pole_point']}: {ds['LF411 Bode']['two_pole']}")
    res["datasheet_readings"] = ds
    res["gain_phase_fits"] = {m: {k_: v for k_, v in x.items() if k_ != "curves"} for m, x in fits.items()}
    res["model_crossovers"] = model_x
    # noise densities of the models at 1 kHz (blocks.opn: e^2 = en^2 (1 + fce/f)), parameters read
    # back from the subcircuits
    res["model_noise_at_1kHz"] = {}
    for m, text in BASE.items():
        p = opn_noise(text)
        res["model_noise_at_1kHz"][m] = dict(
            en_nV=round(p["en"] * math.sqrt(1 + p["fce"] / 1e3) * 1e9, 3),
            in_pA=round(p["inoise"] * math.sqrt(1 + p["fci"] / 1e3) * 1e12, 4),
            equation="e(f) = en sqrt(1 + fce/f), i(f) = inoise sqrt(1 + fci/f) (blocks.opn)",
            parameters_read_back={k_: float(f"{v:.5g}") for k_, v in p.items()})
        log(f"{m} model at 1 kHz: e_n {res['model_noise_at_1kHz'][m]['en_nV']} nV/rtHz, i_n "
            f"{res['model_noise_at_1kHz'][m]['in_pA']} pA/rtHz (parameters {res['model_noise_at_1kHz'][m]['parameters_read_back']})")

    # ---- variants
    tp356, tp411 = ds["LF356 Bode"]["two_pole"], ds["LF411 Bode"]["two_pole"]
    ds_sub = {"LF356_DS": refit("LF356", "LF356_DS", tp356["gbw"], poles=(tp356["fp2"],)),
              "LF411_DS": refit("LF411", "LF411_DS", tp411["gbw"], poles=(tp411["fp2"],)),
              "OP37_DS": refit("OP37", "OP37_DS", fits["OP37"]["fit"]["gbw"], poles=fits["OP37"]["fit"]["poles"],
                               doublet=fits["OP37"]["fit"]["doublet"]),
              "LT1028_DS": refit("LT1028", "LT1028_DS", fits["LT1028"]["fit"]["gbw"],
                                 poles=fits["LT1028"]["fit"]["poles"], doublet=fits["LT1028"]["fit"]["doublet"])}
    by_type = {"LF356": ["U204", "U303"], "LF411": ["U103", "U404"], "OP37": ["U102", "U201", "U305", "U403"],
               "LT1028": ["U105", "U402"]}

    def ds_edit(types):
        models, subs = {}, {}
        for t in types:
            for i in by_type[t]:
                models[i] = f"{t}_DS"
            subs[f"{t}_DS"] = ds_sub[f"{t}_DS"]
        return make_edit(models, subs)

    variants = {"baseline": ("(a) the archived models", None)}
    variants["b_lf356_lf411_x10"] = ("(b) LF356 U204, U303 and LF411 U103, U404 ten times faster",
                                     speedup(["U204", "U303", "U103", "U404"], 10, False))
    for key, insts, lm, desc in STAGES:
        variants[f"c_{key}_x10"] = (f"(c) {desc}, ten times faster" + (" (LM6321 pole too)" if lm else ""),
                                    speedup(insts, 10, lm))
    after_fe = ["U105", "U204", "U201", "U303", "U305", "U402", "U404", "U403"]
    variants["c_after_fe_ideal"] = ("(c) every op amp after the front end and the LM6321 pole 1000 times faster",
                                    speedup(after_fe, 1000, True))
    variants["c_all_ideal"] = ("(c) every op amp and the LM6321 pole 1000 times faster (passive networks and JFETs)",
                               speedup(["U102", "U103"] + after_fe, 1000, True))
    variants["e_lf356_lf411_datasheet"] = ("(e) LF356 and LF411 with two-pole fits to their data-sheet Bode plots",
                                           ds_edit(["LF356", "LF411"]))
    variants["e_op37_datasheet"] = ("(e) all four OP37 fitted to the data sheet's TPC 18", ds_edit(["OP37"]))
    variants["e_lt1028_datasheet"] = ("(e) both LT1028 fitted to the data sheet's gain-phase plot", ds_edit(["LT1028"]))
    variants["e_all_datasheet"] = ("(e) every op amp with its data-sheet dynamics", ds_edit(["LF356", "LF411", "OP37", "LT1028"]))
    variants["e_rout_datasheet"] = ("(e) OP37 R_O = 70 ohm and LT1028 Z_O = 80 ohm (data sheets, p. 3 of each)",
                                    make_edit({i: "OP37_RO" for i in by_type["OP37"]} | {i: "LT1028_RO" for i in by_type["LT1028"]},
                                              {"OP37_RO": with_rout("OP37", "OP37_RO", 70.0),
                                               "LT1028_RO": with_rout("LT1028", "LT1028_RO", 80.0)}))
    all_ds = ds_edit(["LF356", "LF411", "OP37", "LT1028"])
    variants["f_add_C406"] = ("(f) documentation check: C406 = 82 pF across U403 added (sheet 560_4F, parts list)",
                              ADD_C406)
    variants["f_C301_47p"] = ("(f) documentation check: C301 = 47 pF (parts list) instead of 6.8 pF (sheet 560_3F)",
                              C301_47P)
    variants["f_ideal_add_C406"] = ("(f) every op amp ideal as in c_all_ideal, with C406 added",
                                    compose(speedup(["U102", "U103"] + after_fe, 1000, True), ADD_C406))
    variants["f_datasheet_add_C406"] = ("(f) data-sheet dynamics (e_all_datasheet) with C406 added",
                                        compose(all_ds, ADD_C406))
    variants["f_datasheet_add_C406_C301_47p"] = ("(f) data-sheet dynamics, C406 added and C301 = 47 pF",
                                                 compose(all_ds, ADD_C406, C301_47P))
    res["variants"] = {k_: v[0] for k_, v in variants.items()}

    # ---- (a)-(c), (e): the chain
    arch = json.loads((spice.RESULTS / "sr560_chain.json").read_text(encoding="utf-8"))["ac"]
    chain: dict = {}
    for g in GAINS:
        s = SC.trimmed(SC.allocate(g, "LN"), g, runs=f"{RUNS}/chain")
        log(f"\n== Chain, gain {g}: setting {s.tag}, vtrim {s.vtrim:.6g} V, vernier code {s.dac:.6g}")
        rows = {}
        for name, (desc, edit) in variants.items():
            r, raw = chain_run(s, name, edit)
            rows[name] = r
            if name == "baseline":
                a = arch[str(g)]
                old = np.load(spice.RESULTS / f"sr560_chain_ac_{g}.npz")
                same_grid = len(old["f"]) == len(raw["f"]) and np.allclose(old["f"], raw["f"])
                dmax = float(np.max(np.abs(20 * np.log10(np.abs(raw["h"]) / np.abs(old["h"]))))) if same_grid else None
                r["archived"] = dict(setting=a["setting"], f3db_MHz=a["f3db"] / 1e6, db_300k=a["db_300k"],
                                     db_1M=a["db_1M"], key=f"sr560_chain.json ac.{g}.f3db")
                r["rel_diff_f3db"] = r["f3db_MHz"] / (a["f3db"] / 1e6) - 1
                r["max_abs_diff_dB_vs_archived_curve"] = dmax
                log(f"   baseline f3dB {r['f3db_MHz']:.4f} MHz (archived {a['f3db'] / 1e6:.4f}, "
                    f"{a['setting']}; rel. diff {r['rel_diff_f3db']:.2e}; curve max |diff| {dmax} dB)")
            log(f"   {name:28s} f3dB {r['f3db_MHz']:.3f} MHz  300 kHz {r['dB_300k']:+.2f} dB  1 MHz "
                f"{r['dB_1M']:+.2f} dB  peak {r['peak_dB']:+.2f} dB at {r['f_peak_MHz']:.3g} MHz  "
                f"v(out50) {r['op_out50']:.4g}")
        base = rows["baseline"]["f3db_MHz"]
        for name in rows:
            rows[name]["delta_f3db_MHz"] = rows[name]["f3db_MHz"] - base
            rows[name]["delta_dB_1M"] = rows[name]["dB_1M"] - rows["baseline"]["dB_1M"]
        chain[str(g)] = dict(setting=s.tag, vtrim=s.vtrim, dac=s.dac, results=rows,
                             passive_closed_forms=passive_closed_forms(SC.netlist(s), not s.fe10))
        pc = chain[str(g)]["passive_closed_forms"]
        log("   passive networks with ideal op amps (dB at 0.3 / 0.73 / 1 MHz): "
            + "; ".join(f"{n}: {d['dB_at_MHz']['0.3']:+.2f} / {d['dB_at_MHz']['0.73']:+.2f} / "
                        f"{d['dB_at_MHz']['1']:+.2f}" for n, d in pc.items() if n not in ("sum", "sum_note", "values"))
            + f"; sum {pc['sum']}")
    res["chain"] = chain

    # ---- (d): the front end alone
    fe_old = json.loads((spice.RESULTS / "sr560_frontend.json").read_text(encoding="utf-8"))["sr560_x10_2N5564"]
    fe_variants = {"baseline": None,
                   "U102_x10": speedup(["U102"], 10, False),
                   "U102_x1000": speedup(["U102"], 1000, False),
                   "U102_datasheet": make_edit({"U102": "OP37_DS"}, {"OP37_DS": ds_sub["OP37_DS"]})}
    fe = {}
    log("\n== Front end alone (output v(out), -3 dB from the 1 Hz value, as sr560_frontend.run_case)")
    for pos in (True, False):
        rows = {}
        for name, edit in fe_variants.items():
            r = fe_run(pos, name, edit)
            if pos and name == "baseline":
                r["archived"] = dict(f3db_MHz=fe_old["f3db"] / 1e6, gain_1k=fe_old["gain_1k"],
                                     key="sr560_frontend.json sr560_x10_2N5564.f3db")
                r["rel_diff_f3db"] = r["f3db_MHz"] / (fe_old["f3db"] / 1e6) - 1
            rows[name] = r
            log(f"   {'x10' if pos else 'x2 '} {name:16s} f3dB {r['f3db_MHz']:.3f} MHz  gain(1 kHz) "
                f"{r['gain_1k']:.4f}  1 MHz {r['dB_1M']:+.2f} dB  peak {r['peak_dB']:+.2f} dB at "
                f"{r['f_peak_MHz']:.3g} MHz" + (f"  (archived {fe_old['f3db'] / 1e6:.4f} MHz)"
                                               if pos and name == "baseline" else ""))
        fe["x10" if pos else "x2"] = rows
    res["frontend_alone"] = fe

    # ---- ranking of the single-stage speed-ups
    rank = {}
    for g in GAINS:
        rows = chain[str(g)]["results"]
        rank[str(g)] = sorted(((k_[2:-4], round(rows[k_]["delta_f3db_MHz"], 4), round(rows[k_]["delta_dB_1M"], 3))
                               for k_ in rows if k_.startswith("c_") and k_.endswith("_x10")),
                              key=lambda t: -t[1])
    res["single_stage_ranking"] = dict(note="(stage, change of the -3 dB frequency in MHz, change of the "
                                            "response at 1 MHz in dB) when that stage alone is ten times faster",
                                       by_gain=rank)
    log("\n== Single stage ten times faster: change of f3dB (MHz) and of the 1 MHz response (dB)")
    for g in GAINS:
        log(f"   gain {g}: " + ", ".join(f"{n} {d:+.3f} ({db:+.2f} dB)" for n, d, db in rank[str(g)]))
    OUT.write_text(json.dumps(res, indent=1, default=float), encoding="utf-8", newline="\n")
    LOG.write_text("\n".join(_LOG) + "\n", encoding="utf-8", newline="\n")
    log(f"\nwritten {OUT.name}, {LOG.name}")


if __name__ == "__main__":
    main()
