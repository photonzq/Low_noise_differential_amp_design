"""The derived numbers of Sections 6 (results, Tables 8-15, Figures 12-17) and 7 and of the
Appendix of the note (not Section 8): every number there that is not a plain readout of an
archived JSON file is computed here, from the archived results only (no simulation), and every
data-sheet value used is a constant below with its document, page, table or figure.

Rounding: a value is rounded once, half up, from its stored value (Decimal of its repr), to the
decimals the note quotes; a range "a-b" is the rounded minimum and maximum over the cases it covers.
Frequencies are read on each file's own grid (the nearest point; every quoted frequency is a grid
point).  Densities in nV/rtHz, CMRR and THD in dB / dBc, k = 1.380649e-23 J/K, q = 1.602176634e-19 C,
T = 300.15 K (ngspice's 27 C).

Formulas, in the order of the note:
  Table 8        e_x(f) of each group of curves_noise.npz (collect_curves.py noise), x 1e9
  Eq. (2)        e_diff = sqrt(2) e_1 / sqrt(N): H, N = 2 JFE2140 per side; L, N = 12 JFE150
  ranking        the groups of H10 at 10 kHz sorted by size (which term follows R_G)
  V_T            V_T = kT / q
  Table 8a       readouts of sink_options.json at 10 kHz; the bound row at a gain of 100:
                 e_without = sqrt(e_tot^2 - e_sinks^2) (H100, 10 kHz)
  stages after   e_post = sqrt(e_chain^2 - e_FE^2) (fe_closed_forms.json; da_compare.json e_post)
  Table 9        ranges over the gains of a row of chain_noise.json
  headroom       20 log10(G_FE,LN / G_FE,HR) = 20 log10(100 / 10)
  Figure 14      readouts of nf_map.json and sr560_nf_datasheet.json (the noise-figure maps and the
                 SR560 data sheet's two-port fit), resistances to two or three significant figures;
                 a deviation's bound rounded up to one significant figure; the SR560 models' noise current
                 at 1 MHz without the tail servo's share, i = sqrt(1 - s) i_n with s the servo's share of the
                 output noise with 1 Mohm (where i_n R_S dominates e_n), and the capacitance it corresponds
                 to, C = sqrt(i^2 - i_n(1 kHz)^2) / (2 pi f e_n) (i_n(1 kHz): the input resistors' noise);
                 the white levels' ratios 100 (1 - e_w / e_w,sheet) and 100 (e_w,LSK389B / e_w,NPD5564 - 1);
                 readouts of sr560_nf_sources.json (the SR560 models' input capacitance, JFET A's C_gs + C_gd
                 at its bias, and the effective capacitance sqrt(S_i / S_e) / w of each group of noise sources),
                 and the ratios LSK389B / NPD5564 of the servo's noise current and of the input capacitance
  Section 6.2    crossover of NF_H - NF_L (noise_vs_source.json): the two source resistances of
                 Table 10 (and of the full grid) between which the sign changes, per frequency
  Table 11       ranges of chain_ac.json over the gains of a row; SR560 peaking
                 20 log10(max|H| / |H(1 kHz)|) from sr560_chain_ac_<gain>.npz
  CMRR, Delta C  per input sigma_C = s sqrt(C_P^2 + C_Z^2) (C_P and C_Z drawn independently with
                 s = 2.5 %), Delta C_rms = sqrt(2) sigma_C, median |Delta C| = 0.6745 Delta C_rms
                 (the median of |N(0, 1)|), CMRR = 20 log10(1 / (2 pi f R_S Delta C))
  CMRR, JFETs    JFE2140: each half drawn with sigma_h about its dual's common offset (cmrr_mc.py),
                 the halves' difference sigma_d = sqrt(2) sigma_h, mean |dV_GS| = sigma_d sqrt(2/pi);
                 JFE150 bin of +-w: a uniform spread has sigma = w / sqrt(3)
  CMRR, SR560    specification CMRR(f) = 100 dB - 20 log10(f / 1 kHz) for f > 1 kHz (100 dB to 1 kHz,
                 6 dB per octave above, data sheet p. 3)
  CMRR, others   differences of medians (trimmed - 50 ohm; network - discrete; ideal I_BS - R_UP)
  Table 13       THD (%) = 100 thd; THD (dBc) = 20 log10(thd); the floor: min and max of the linear
                 reference's dBc, and per frequency max - min of the chain's dBc over the settings
  full power     f_FP = SR / (pi V_pp) at V_pp = 10 V
  overload       servo rate = G_INT e / C_INT (G_INT 1 uS, C_INT 1 uF: GINT, CINT of frontend.py);
                 its change over 20 us; after 1 s the reference moves by rate x 1 s and the outputs'
                 common mode by (R_F / R_T) that; servo time constant (C_INT / G_INT)(R_T / R_F);
                 bootstrap R_BS C_BS; with the outputs clipped v_s,d = (v_oa - v_ob) R_G / (2 R_F + R_G),
                 dV_GS ~ (v_in - v_s,d) / 2, zero gate bias at v_in = 2 |V_GS,rest| + v_s,d
                 (overload_detail.py numbers; repeated here from overload_numbers.json)
  Table 14       HD3 (dBc) = 20 log10(h3); the data sheet's HD3 at 2 Vpp scaled to 1 Vpp with
                 HD3 ~ V^2: HD3(1 Vpp) = HD3(2 Vpp) + 20 log10((1/2)^2); ratio = 10^(dB / 20)
  Section 7      the common-mode gain-margin point: frontend._margins on curves_loop.npz gives the
                 first grid point past each -180 degree crossing; the crossing itself is
                 interpolated linearly in log f between that point and the one before, and quoted to
                 the nearest 5 MHz
Writes ../sim/results/numbers_s6_7.json and prints a table: quantity | value | source.
Usage: python numbers_s6_7.py
"""
from __future__ import annotations

import json
import math
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import frontend as F  # noqa: E402  (only _margins is used: no simulation, no model preparation)

R = Path(__file__).resolve().parent.parent / "sim" / "results"
K_B, Q_E, T = 1.380649e-23, 1.602176634e-19, 300.15
MINUS = "−"

# ---- data-sheet and document constants (each with its source) ---------------------------------
# JFETs, white noise at 1 kHz and 5 mA
E1_JFE2140 = 0.9      # nV/rtHz, TI JFE2140 data sheet SLPS730B p. 1 (Features: 0.9 nV/rtHz at 1 kHz, I_DS = 5 mA)
E1_JFE150 = 0.8       # nV/rtHz, TI JFE150 data sheet SLPS732B p. 5, Table 6.5 (I_DS = 5 mA, V_DS = 5 V, 1 kHz)
N_H, N_L = 2, 12      # JFETs per side, Table 5 of the note (frontend.CASES)
# JFE2140 matching, SLPS730B p. 5, Table 6.5 (I_DS = 2 mA): dV_GS 1 mV typ, 4 mV max; I_DSS1/I_DSS2 0.95-1.05
DVGS_TYP_MV, DVGS_MAX_MV = 1.0, 4.0
IDSS_RATIO = (0.95, 1.05)
SIGMA_HALF_MV = 0.85  # cmrr_mc.py: each JFE2140 half's V_TO about its dual's common offset (assumption)
BIN_HALF_MV = 5.0     # the JFE150 V_GS bin, +-5 mV (design choice, Section 4.6 of the note)
SIGMA_BIN_MV = 3.0    # cmrr_mc.py: V_TO sigma within the bin (assumption)
# Op amps for S2 (Table 14)
THS4031_EN, THS4031_BW_MHZ = 1.2, 100   # SLOS224L p. 1 (1.2 nV/rtHz; 100 MHz, G = 2 or -1) and p. 6, Sec. 5.6
THS4031_HD3_DS_DBC = -50.0              # SLOS224L Fig. 5-15, p. 12: HD3 at 10 MHz, G = +2, R_L 1 kohm, 2 Vpp (read by eye)
LM7171A_EN, LM7171_SR, LM7171A_UGBW_MHZ = 8.5, 4100, 160   # SNOS760D Sec. 5.5, p. 5 (A grade; e_n at 10 kHz)
THS3091_EN = 1.1                         # SLOS423K p. 1 and p. 6, Sec. 7.5 (f > 10 kHz)
# SR560 (refs/benchmark): manual (specifications chart, printed p. 5 = PDF p. 9; input voltage noise
# curve, printed p. 20 = PDF p. 24; noise table, printed p. 21 = PDF p. 25) and data sheet (p. 3)
SR560_EN = 4.0                 # manual p. 5 "<4 nV/rtHz at 1 kHz"; data sheet p. 3 "4 nV/rtHz at 1 kHz"
SR560_EN_10HZ = 11.0           # manual printed p. 20, typical curve at 10 Hz (read by eye: 10.7-11.3)
SR560_EN_G10 = 13.0            # manual printed p. 21, table, gain 10, low noise
SR560_CIN_PF = 25.0            # manual p. 5 and data sheet p. 3: 100 Mohm + 25 pF
SR560_BW_MHZ, SR560_BW_TYP_MHZ = 1.0, 1.2   # manual p. 5 (-3 dB at 1 MHz, 1 Vpp); data sheet p. 3 (1.2 MHz typ.)
SR560_CMRR_DS, SR560_CMRR_MAN = 100.0, 90.0  # data sheet p. 3 (100 dB DC-1 kHz, -6 dB/oct to 1 MHz); manual p. 5 (>90 dB to 1 kHz, -20 dB/decade)
# NF 5307 (refs/commercial_preamps/NF_Corporation)
NF_EN_SPEC = 4.0          # NF_5307_specifications_EN.pdf: 4 nV/rtHz typ. at 1 kHz, input short-circuited, gain 1000
NF_CIN_PF = 35.0          # same sheet: 1 Mohm +-2 % shunted by less than 35 pF
NF_CMRR_SPEC = 120.0      # same sheet: 120 dB or greater, DC to 1 kHz, gain 1000
NF_GAINS = (10, 1000)     # same sheet: 10 to 1000 in 1-2-5 sequence
# Instruction manual (NF_5307_instruction_manual_EN.pdf) Fig. 4.7, PDF p. 37 (printed p. 25), read by eye.
# The scan's log axis is not uniform: read against the printed minor ticks (log interpolation between
# them) and against a uniform scale between the frame lines 1 n and 1 u, the curves give (low, high):
# gain 100 x1, flat from 100 Hz to 100 kHz, 2.8-3.1 nV/rtHz; the same curve at 10 Hz 5.6-5.9; gain 10 x1,
# flat, 15.1-15.7
NF_EN_PLOT_G100, NF_EN_PLOT_G100_10HZ, NF_EN_PLOT_G10 = (2.8, 3.1), (5.6, 5.9), (15.1, 15.7)
# Fig. 46 of NF's data-sheet web page (NF_5307_datasheet_fig46.jpg), CMRR, gain 100 x1 curve, read by
# eye against its grid at the frequencies of Table 12.  The curve stops at about 0.9 MHz, short of the
# 1 MHz frame line (85.9 dB at 888 kHz); the 1 MHz value is its straight-line extrapolation from 0.4 to
# 0.95 MHz by scripts/nf5307_plot_check.py (nf5307_plot_check.json, fig46_cmrr), 84.8 dB, where the
# earlier reading by eye, 86.4, was the curve's end.  The pixel check gives 136.1, 135.3, 125.9 and
# 106.6 dB at the other four frequencies, within 0.4 dB of the readings by eye.
NF_CMRR_PLOT = {10: 136.2, 1e3: 135.7, 1e4: 125.9, 1e5: 107.0, 1e6: 84.8}
# front end (Table 5 of the note; frontend.CASES), servo integrator (frontend.py: GINT 1e-6, CINT 1u)
G_INT, C_INT = 1e-6, 1e-6
R_BS, C_BS = 3.5e3, 1e-6

# The SR560 reproduction's NPD5564 is the 2N5564 card recalibrated in models.py to Vishay's 2N5564 data sheet
# (Doc. 70254 Rev. E): its targets, 1.28 nV/rtHz white (100 kHz) and 3.6 nV/rtHz at 1 kHz at 4.5 mA, give one 1/f
# line, e(f) = sqrt(e_w^2 + (e_lf^2 - e_w^2) f_lf / f).  Vishay's Noise Voltage vs Frequency (p. 5, V_DS = 15 V),
# read by eye in refs/datasheets/jfet/survey_InterFET_NXP_others.md, Section 3.1, nV/rtHz per device, at 1 and
# 10 mA; interpolated to 4.5 mA log-log in current, e(4.5 mA) = e(1 mA) (e(10 mA) / e(1 mA))^log10(4.5), the
# interpolation that models.py quotes (1.25 and 3.44 at 100 kHz and 1 kHz).
CARD_2N5564 = dict(id=4.5e-3, e_w=1.28, e_lf=3.6, f_lf=1e3)
VISHAY_2N5564_EN = {1e-3: {10.0: 15.0, 100.0: 10.0, 1e3: 4.2, 1e4: 2.1, 1e5: 1.35},
                    10e-3: {10.0: 8.7, 100.0: 7.0, 1e3: 3.1, 1e4: 1.6, 1e5: 1.2}}

OUT: dict = {}
ROWS: list = []


def rhu(x: float, nd: int) -> float:
    """x rounded once, half up, to nd decimals (from its repr, so 2.335 stays 2.335 before rounding)."""
    return float(Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def f(x: float, nd: int) -> str:
    v = rhu(x, nd)
    s = f"{0.0 if v == 0 else v:.{nd}f}"          # no "-0.00"
    return s.replace("-", MINUS)


def sig(x: float, n: int) -> str:
    """x to n significant figures, half up."""
    if x == 0:
        return "0"
    nd = n - 1 - int(math.floor(math.log10(abs(x))))
    return f(x, max(nd, 0)) if nd > 0 else f(rhu(x, nd), 0)


def _join(a: str, b: str, neg: bool) -> str:
    if a == b:
        return a
    return f"{a} to {b}" if neg else f"{a}–{b}"


def rng(vals, nd: int) -> str:
    """Rounded range of vals; negative values as "-0.40 to -0.41" (the one nearer zero first)."""
    neg = max(vals) < 0
    return _join(f(max(vals) if neg else min(vals), nd), f(min(vals) if neg else max(vals), nd), neg)


def srng(vals, n: int) -> str:
    """The same with n significant figures."""
    neg = max(vals) < 0
    return _join(sig(max(vals) if neg else min(vals), n), sig(min(vals) if neg else max(vals), n), neg)


def put(group: str, name: str, value, text: str, source: str):
    OUT.setdefault(group, {})[name] = dict(value=value, text=text, source=source)
    ROWS.append((f"{group}: {name}", text, source))


def load(name: str):
    p = R / name
    return np.load(p, allow_pickle=True) if p.suffix == ".npz" else json.loads(p.read_text(encoding="utf-8"))


def at(fr, y, f0: float) -> float:
    i = int(np.argmin(np.abs(np.asarray(fr) - f0)))
    assert abs(fr[i] / f0 - 1) < 1e-6, f"{f0} Hz is not a grid point"
    return float(y[i])


def dbc(x: float) -> float:
    return 20 * math.log10(x)


# ---- Section 6.1: Table 8 and its paragraphs -------------------------------------------------
def table8():
    d = load("curves_noise.npz")
    cols = (("Total", "total"), ("Input JFETs", "g_input JFETs"), ("R_G", "g_R_G"),
            ("Loop op amps", "g_loop op amps"), ("R_D", "g_drain-side R_D"),
            ("Current sinks", "g_current sinks"), ("R_F", "g_R_F"))
    rows = (("H100", (1, 10, 1e3, 1e6, 1e7)), ("H10", (10, 1e3, 1e7)), ("L200", (1, 10, 1e3, 1e7)))
    src = "curves_noise.npz (collect_curves.py noise), nV/rtHz at the grid point"
    for case, fs in rows:
        fr = d[f"{case}_f"]
        for f0 in fs:
            vals = [at(fr, d[f"{case}_{k}"], f0) * 1e9 for _, k in cols]
            put("table8", f"{case} {f0:g} Hz", vals, " | ".join(f(v, 2) for v in vals),
                src + "; columns " + ", ".join(c for c, _ in cols))
    # the JFETs in the white region (1 MHz for H, 1 kHz and 10 MHz for L)
    jh = at(d["H100_f"], d["H100_g_input JFETs"], 1e6) * 1e9
    jl = [at(d["L200_f"], d["L200_g_input JFETs"], x) * 1e9 for x in (1e3, 1e4, 1e7)]
    put("table8", "JFETs white, H", jh, f(jh, 2), "curves_noise.npz H100, 1 MHz")
    put("table8", "JFETs white, L", jl, rng(jl, 2), "curves_noise.npz L200, 1 kHz, 10 kHz, 10 MHz")
    # which term follows R_G at a front-end gain of 10 (white region, 10 kHz)
    fr = d["H10_f"]
    order = sorted(((k[len("H10_g_"):], at(fr, d[k], 1e4) * 1e9) for k in d.files
                    if k.startswith("H10_g_")), key=lambda t: -t[1])
    put("table8", "H10 groups at 10 kHz, largest first", order,
        ", ".join(f"{g} {f(v, 2)}" for g, v in order[:5]), "curves_noise.npz H10, 10 kHz")
    # Eq. (2) with the data sheets
    eh = math.sqrt(2) * E1_JFE2140 / math.sqrt(N_H)
    el = math.sqrt(2) * E1_JFE150 / math.sqrt(N_L)
    put("eq2", "H: sqrt(2) x 0.9 / sqrt(2)", eh, f(eh, 2), "SLPS730B p. 1 (0.9 nV/rtHz, 5 mA); N = 2 (Table 5)")
    put("eq2", "L: sqrt(2) x 0.8 / sqrt(12)", el, f(el, 2), "SLPS732B p. 5, Table 6.5 (0.8 nV/rtHz, 5 mA); N = 12")
    nt = load("noise_theory.json")["Eq. (2)"]
    assert abs(nt["H: 2 x JFE2140 per side"]["e_diff"] * 1e9 - eh) < 1e-9
    assert abs(nt["L: 12 x JFE150 per side"]["e_diff"] * 1e9 - el) < 1e-9
    card = [r for r in load("jfet_model_check.json")["JFE2140"]["model"] if abs(r["id"] - 5e-3) < 1e-9][0]
    put("eq2", "JFE2140 card, white at 5 mA (10 V)", card["en_white"] * 1e9, f(card["en_white"] * 1e9, 2),
        "jfet_model_check.json JFE2140.model (id 5 mA)")
    vt = K_B * T / Q_E * 1e3
    put("eq12", "V_T = kT/q (mV)", vt, f(vt, 1), "T = 300.15 K (ngspice 27 C), as fe_closed_forms.py")


def table8a():
    d = load("sink_options.json")
    rows = ("H10 | MMBT3904, 2 V (adopted)", "H10 | MMBT3904, 4 V", "H10 | MMBT3904, 6 V", "H10 | BC817-25, 2 V",
            "H10 | BC817-25, 4 V", "H10 | BC817-25, 6 V", "H10 | JFE150, 6 V",
            "H10 | R_F 250 ohm for this range (MMBT3904, 2 V)")
    for k in rows:
        v = d[k]
        s, rt, tr = v["sinks"]["10000"], v["split"]["R_T"]["10000"], v["split"]["transistor"]["10000"]
        en = v["en"]
        txt = (f"{f(s, 2)} ({f(rt, 2)} / {f(tr, 2)}) | {f(en['10000.0'], 2)} / {f(en['10'], 2)} / "
               f"{f(en['10000000.0'], 2)} | V_CM,min {f(v['op']['vcm_min'], 1)} V | {f(v['op']['p_transistor'] * 1e3, 0)} mW")
        put("table8a", k, dict(sinks=s, R_T=rt, transistor=tr, en_10k=en["10000.0"], en_10=en["10"],
                               en_10M=en["10000000.0"], vcm_min=v["op"]["vcm_min"]), txt,
            "sink_options.json, 10 kHz unless stated")
    # the gain-100 column, and what the JFE150 sink needed there (sink_options.py evaluate_checked)
    for k in rows[:7]:
        k100 = "H100 | " + k.split(" | ", 1)[1]
        v = d[k100]
        dm, cm = v["loop"]["dm"], v["loop"]["cm"]
        put("table8a", f"{k100}: front end at 10 kHz | f3dB | margins | source node | ties",
            dict(en_10k=v["en"]["10000.0"], f3db=v["f3db"], v_sa=v["op"]["v_sa"], r_in=v.get("r_in", 1e-3),
                 op_note=v.get("op_note", "")),
            f"{f(v['en']['10000.0'], 2)} | {f(v['f3db'] / 1e6, 1)} MHz | DM {dm['pm']} deg, {dm['gm_db']} dB; CM "
            f"{cm['pm']} deg, {cm['gm_db']} dB | {f(v['op']['v_sa'], 3)} V | {v.get('r_in', 1e-3):g} ohm",
            "sink_options.json, 10 kHz; r_in 1 ohm where 1 mOhm made the operating point fall back (op_note)")
    loops = [d[k]["loop"] for k in d if k.startswith("H100 | ") and "loop" in d[k]]
    put("table8a", "H100: the loop margins are the same in every sink variant", all(x == loops[0] for x in loops),
        str(all(x == loops[0] for x in loops)), "sink_options.json H100 | *.loop")
    a10, a100 = d["H10 | MMBT3904, 2 V (adopted)"], d["H100 | MMBT3904, 2 V (adopted)"]
    b10 = math.sqrt(a10["en"]["10000.0"] ** 2 - a10["sinks"]["10000"] ** 2)
    b100 = math.sqrt(a100["en"]["10000.0"] ** 2 - a100["sinks"]["10000"] ** 2)
    put("table8a", "bound, gain 10: sqrt(e_tot^2 - e_sinks^2)", b10, f(b10, 2), "sink_options.json H10 adopted, 10 kHz")
    put("table8a", "bound, gain 100: sqrt(e_tot^2 - e_sinks^2)", b100, f(b100, 2), "sink_options.json H100 adopted, 10 kHz")


def stages_after():
    fc = load("fe_closed_forms.json")["noise"]["stages after the front end, H_HR 100, 1 kHz"]
    put("s6.1", "stages after a gain-10 front end, LM7171, 1 kHz", fc, f(fc, 1),
        "fe_closed_forms.json: sqrt(2.7786^2 - 1.9255^2)")
    hr = load("da_compare.json")["noise_H_HR"]
    t = hr["THS4031"]
    ep = [t[g]["e_post"]["1000.0"] * 1e9 for g in ("H_HR_100", "H_HR_1000")]
    put("s6.1", "stages after, THS4031 in S2, 1 kHz (gains 100, 1000)", ep, f(ep[0], 2),
        "da_compare.json noise_H_HR.THS4031.H_HR_100.e_post (gain 100)")
    bands = (("1 kHz - 1 MHz", ("1000.0", "10000.0", "100000.0", "1000000.0")), ("10 Hz", ("10",)),
             ("10 MHz", ("10000000.0",)))
    for s2 in ("THS4031", "LM7171"):
        for lab, keys in bands:
            vals = [hr[s2][g]["en"][k] * 1e9 for g in ("H_HR_100", "H_HR_1000") for k in keys]
            nd = 2 if (s2 == "LM7171" and lab == "10 MHz") else 1
            put("s6.1", f"H_HR 100-1000, {s2} in S2, {lab}", vals, rng(vals, nd), "da_compare.json noise_H_HR")
    th, lm = hr["THS4031"]["H_HR_100"]["en"], hr["LM7171"]["H_HR_100"]["en"]
    put("s6.5", "H_HR 100 at 1 MHz: LM7171 against THS4031", (lm["1000000.0"] * 1e9, th["1000000.0"] * 1e9),
        f"{f(lm['1000000.0'] * 1e9, 1)} against {f(th['1000000.0'] * 1e9, 1)}", "da_compare.json noise_H_HR")
    vals_lm = [hr["LM7171"][g]["en"]["1000.0"] * 1e9 for g in ("H_HR_100", "H_HR_1000")]
    vals_th = [hr["THS4031"][g]["en"]["1000.0"] * 1e9 for g in ("H_HR_100", "H_HR_1000")]
    put("s6.5", "H_HR 100-1000 at 1 kHz: LM7171 against THS4031", (vals_lm, vals_th),
        f"{rng(vals_lm, 1)} against {rng(vals_th, 1)}", "da_compare.json noise_H_HR")


def table9():
    d = load("chain_noise.json")
    # the precision of each cell as Table 9 quotes it: 1 Hz to two significant figures; 10 Hz of the
    # high-reserve row to one decimal; everything else to two decimals
    rows = (("H_LN 1000-50000", ("H_LN_1000", "H_LN_10000", "H_LN_50000"), 2),
            ("H_HR 100-1000", ("H_HR_100", "H_HR_1000"), 1), ("L 1000-100000", ("L_1000", "L_10000", "L_100000"), 2))
    for lab, keys, nd10 in rows:
        for fk, nd in (("1", None), ("10", nd10), ("1000.0", 2), ("100000.0", 2), ("10000000.0", 2)):
            vals = [d[k]["en"][fk] * 1e9 for k in keys]
            put("table9", f"{lab}, {float(fk):g} Hz", vals, rng(vals, nd) if nd is not None else srng(vals, 2),
                "chain_noise.json")
    # the single-gain rows, each cell with the precision Table 9 prints (s: significant figures,
    # d: decimals), and the output noise column (mV rms, 1 Hz - 10 MHz)
    single = (("H_LN_1", ("s3", "s3", "s3", "s3", "s3")), ("H_LN_10", ("s2", "s3", "s3", "s3", "s3")),
              ("H_LN_100", ("s3", "s3", "s3", "s3", "s3")), ("L_200", ("s3", "s3", "d2", "d2", "d2")))
    for k, spec in single:
        for fk, p in zip(("1", "10", "1000.0", "100000.0", "10000000.0"), spec):
            v = d[k]["en"][fk] * 1e9
            put("table9", f"{k}, {float(fk):g} Hz", v, sig(v, int(p[1])) if p[0] == "s" else f(v, int(p[1])),
                "chain_noise.json")
    for k, p in (("H_LN_1", "d2"), ("H_LN_10", "d2"), ("H_LN_100", "d2"), ("H_LN_1000", "s2"), ("H_HR_100", "d2"),
                 ("L_200", "d2"), ("L_1000", "d2")):
        v = d[k]["out_rms_10M"] * 1e3
        put("table9", f"{k}, output 1 Hz - 10 MHz (mV rms)", v, sig(v, int(p[1])) if p[0] == "s" else f(v, int(p[1])),
            "chain_noise.json out_rms_10M")
    w = [d[k]["en"][fk] * 1e9 for k in ("H_HR_100", "H_HR_1000") for fk in ("100000.0", "1000000.0")]
    k1 = [d[k]["en"]["1000.0"] * 1e9 for k in ("H_HR_100", "H_HR_1000")]
    put("s6.1", "H_HR 100-1000: white (100 kHz, 1 MHz) and 1 kHz", (w, k1),
        f"{srng(w, 2)} white; {srng(k1, 2)} at 1 kHz", "chain_noise.json")
    sr = load("sr560_chain.json")["noise"]
    hdr = [sr[f"HDR_{g}"]["en"]["1000.0"] * 1e9 for g in (100, 200, 500, 1000)]
    put("s6.1", "SR560 reproduction, high reserve, gains 100-1000, 1 kHz", hdr, srng(hdr, 2),
        "sr560_chain.json noise.HDR_*")
    hd = 20 * math.log10(100 / 10)
    put("s6.1", "input headroom of H_HR: 20 log10(100/10) (dB)", hd, f(hd, 0), "front-end gains 100 and 10 (Table 5)")


# ---- Section 6.2 -------------------------------------------------------------------------------
def section62():
    d = load("noise_vs_source.json")
    table10_rs = (10, 30, 100, 300, 1e3, 1e4, 1e5, 1e6)
    for fk in ("10", "1000.0", "1000000.0", "10000000.0"):
        for grid, lab in ((table10_rs, "Table 10 rows"), (None, "full grid")):
            hs = [r for r in d["H_LN"] if grid is None or r["rs"] in grid]
            ls = [r for r in d["L"] if grid is None or r["rs"] in grid]
            diff = [(h["rs"], h["nf_db"][fk] - l["nf_db"][fk]) for h, l in zip(hs, ls)]
            sign = [(a, b) for (a, x), (b, y) in zip(diff, diff[1:]) if x > 0 >= y]
            put("s6.2", f"NF crossover at {float(fk):g} Hz ({lab})", sign,
                "; ".join(f"L better below, between {a:g} and {b:g} ohm" for a, b in sign),
                "noise_vs_source.json, NF_H - NF_L changes sign")
    for mode, key in (("H", "H_LN"), ("L", "L")):
        for rs, fk in ((100, "1000000.0"), (1e5, "10000000.0")):
            v = [r for r in d[key] if r["rs"] == rs][0]["nf_db"][fk]
            put("table10", f"{mode}, {rs:g} ohm, {float(fk):g} Hz", v, f(v, 1), "noise_vs_source.json")
    # every cell of Table 10, as it prints them: one decimal from 1 dB up, two below
    for mode, key in (("H", "H_LN"), ("L", "L")):
        for r in d[key]:
            if r["rs"] not in table10_rs:
                continue
            cells = [r["nf_db"][fk] for fk in ("10", "1000.0", "1000000.0", "10000000.0")]
            put("table10", f"{mode}, {r['rs']:g} ohm: 10 Hz | 1 kHz | 1 MHz | 10 MHz", cells,
                " | ".join(f(v, 1) if v >= 1 else f(v, 2) for v in cells), "noise_vs_source.json nf_db")
    z = load("zin_numbers.json")
    for fe in ("H100", "L200"):
        s = z[fe]["sources_archived"]["network_1Meg"]
        put("s6.2", f"{fe}, 1 Mohm with the network: attenuation at 100 kHz / 1 MHz (dB)",
            (s["db_100k"], s["db_1M"]), f"{f(-s['db_100k'], 1)} / {f(-s['db_1M'], 1)}",
            "zin_numbers.json sources_archived.network_1Meg (collect_curves.py zin)")


# ---- Section 6.2: Figure 14, the noise-figure maps against the SR560 data sheet's -----------------
def bound(x: float) -> str:
    """An upper bound of x rounded up to one significant figure, as "2e-05" (0: "0")."""
    if x <= 0:
        return "0"
    e = math.floor(math.log10(x))
    return f"{math.ceil(x / 10 ** e)}e{e:+03d}"


def section62_nf_map():
    m, s = load("nf_map.json"), load("sr560_nf_datasheet.json")
    sm, ss = "nf_map.json", "sr560_nf_datasheet.json"
    g = "s6.2 Figure 14"
    cal, fit, mod = s["calibration"], s["two_port_fit"], s["model"]
    put(g, "data sheet: largest residual of the tick calibration (pt)", cal["max_tick_residual_pt"],
        f(cal["max_tick_residual_pt"], 2), ss + " calibration")
    put(g, "data sheet: two-port fit, largest deviation (decade of R_S | dB)", (fit["max_dev_decades"], fit["max_dev_db"]),
        f"{f(fit['max_dev_decades'], 2)} | {f(fit['max_dev_db'], 2)}", ss + " two_port_fit")
    e = {float(k): v["e_n"] * 1e9 for k, v in mod["at"].items()}
    put(g, "data sheet: e_n at 1 MHz (white) | 1 kHz | 10 Hz | 1 Hz (nV/rtHz)", e,
        f"{f(e[1e6], 2)} | {f(e[1e3], 2)} | {f(e[10.0], 1)} | {sig(e[1.0], 2)}", ss + " model.at")
    put(g, "data sheet: i_n at low frequencies (fA/rtHz); the resistance with that thermal noise at 290 K (Mohm)",
        (mod["i_n_low"], mod["r_equiv_ohm"]), f"{f(mod['i_n_low'] * 1e15, 1)}; {sig(mod['r_equiv_ohm'] / 1e6, 2)}",
        ss + " model; R = 4 k T0 / i_n^2")
    put(g, "data sheet: C of the e_n w C term, 100 kHz to 1 MHz (pF)", mod["c_eff_pf_100k_1M"],
        rng(mod["c_eff_pf_100k_1M"], 0), ss + " model; C = sqrt(i_n^2 - i_n,low^2) / (e_n 2 pi f)")
    worst = max(m[k]["two_port_fit_max_dev_db"] for k in ("H", "L", "SR560"))
    put(g, "simulated (H, L, SR560 as drawn): largest deviation of a run from its two-port fit, 1 Hz to 10 MHz "
           "(dB, bound)", worst, bound(worst), sm)
    worst = m["SR560_LSK389B"]["two_port_fit_max_dev_db"]
    put(g, "simulated (SR560 with the LSK389B): the same (dB, bound)", worst, bound(worst), sm)
    worst = max(m[k]["archived_check"]["max_abs_diff_db"] for k in ("SR560", "SR560_LSK389B"))
    put(g, "SR560 models: the 1 ohm run against the archived noise run, largest difference (dB of noise power; "
           "both written with 7 digits)",
        worst, bound(worst), sm + " archived_check")
    worst = max(m[k]["table10_check"]["max_abs_diff_db"] for k in ("H", "L"))
    put(g, "simulated at 300.15 K against Table 10: largest difference (dB, bound)", worst, bound(worst),
        sm + " table10_check")

    def lo_hi(rows, f0, lev):
        v = rows[f0][f"below_{lev:g}dB"]
        return (v[0], v[1]) if len(v) == 2 else (None, None)

    ds = m["datasheet"]["at"]
    for who, rows in (("data sheet", ds), ("H", m["H"]["at"]), ("L", m["L"]["at"]), ("SR560 reproduction", m["SR560"]["at"]),
                      ("SR560_LSK389B reproduction", m["SR560_LSK389B"]["at"])):
        for f0 in ("10.0", "1000.0", "100000.0", "1000000.0", "10000000.0"):
            if f0 not in rows:
                continue
            r = rows[f0]
            l1, h1 = lo_hi(rows, f0, 1.0)
            l3, h3 = lo_hi(rows, f0, 3.0)
            txt = (f"3 dB {sig(l3, 2) if l3 else '-'} / 1 dB {sig(l1, 2) if l1 else '-'} ohm (low side); "
                   f"1 dB {sig(h1, 3) if h1 else '-'} / 3 dB {sig(h3, 2) if h3 else '-'} ohm (high side); "
                   f"min {f(r['nf_min_db'], 2 if r['nf_min_db'] < 10 else 0)} dB at {sig(r['r_opt'], 2)} ohm; e_n {sig(r['e_n'] * 1e9, 3)} nV, "
                   f"i_n {sig(r['i_n'] * 1e12, 3)} pA")
            put(g, f"{who}, {float(f0):g} Hz", r, txt, (ss + " via " if who == "data sheet" else "") + sm +
                (" datasheet.at" if who == "data sheet" else f" {who.split()[0]}.at"))
    # the low-resistance contours scale with e_n^2 (R_S = e_n^2 / ((F - 1) 4 k T0) where i_n is negligible)
    e_ds, e_h, e_l = (rows["1000.0"]["e_n"] for rows in (ds, m["H"]["at"], m["L"]["at"]))
    put(g, "1 kHz: (e_n,sheet / e_n,H)^2 | (e_n,H / e_n,L)^2", ((e_ds / e_h) ** 2, (e_h / e_l) ** 2),
        f"{f((e_ds / e_h) ** 2, 1)} | {f((e_h / e_l) ** 2, 1)}", sm + " datasheet.at, H.at, L.at")
    for key in ("H", "L", "SR560", "SR560_LSK389B"):
        v = m[key]["vs_datasheet"]
        put(g, f"{key} minus the data sheet: fraction of the plane lower by > 0.1 dB | within 0.1 dB | higher (%)",
            (v["fraction_lower"], v["fraction_within_0p1"], v["fraction_higher"]),
            " | ".join(f(100 * x, 0) for x in (v["fraction_lower"], v["fraction_within_0p1"], v["fraction_higher"])),
            sm + " vs_datasheet")
        put(g, f"{key} minus the data sheet: extremes (dB) at (Hz, ohm)", (v["min_db"], v["max_db"]),
            f"{f(v['min_db']['value'], 1)} at ({v['min_db']['f_hz']:.3g}, {v['min_db']['r_ohm']:.3g}); "
            f"{f(v['max_db']['value'], 1)} ({f(v['max_db']['value'], 2)}) at ({v['max_db']['f_hz']:.3g}, "
            f"{v['max_db']['r_ohm']:.3g})", sm + " vs_datasheet")
        eq = v["equal_at_r_ohm"]
        put(g, f"{key} equal to the data sheet at (ohm): 10 Hz | 1 kHz | 100 kHz | 1 MHz", eq,
            " | ".join(",".join(sig(x, 2) for x in eq[k]) or "-" for k in ("10.0", "1000.0", "100000.0", "1000000.0")),
            sm + " vs_datasheet.equal_at_r_ohm")
    # the SR560 low-frequency noise: the data sheet's plot and the two reproductions (1 ohm runs)
    for who, lf in (("data sheet", m["datasheet"]["low_frequency"]), ("SR560", m["SR560"]["low_frequency"]),
                    ("SR560_LSK389B", m["SR560_LSK389B"]["low_frequency"])):
        e = {float(k): v * 1e9 for k, v in lf["e_n"].items()}
        put(g, f"{who}: e_n at 1 Hz | 10 Hz | 100 Hz | 1 kHz | 100 kHz (nV/rtHz)", e,
            " | ".join(sig(e[k], 3) for k in (1.0, 10.0, 100.0, 1e3, 1e5)), sm + " low_frequency.e_n")
        c = {float(k): v for k, v in lf["corner_hz"].items()}
        put(g, f"{who}: 1/f corner f (e^2 - e_w^2) / e_w^2 from 10 Hz | 100 Hz | 1 kHz (Hz)", c,
            " | ".join(sig(c[k], 2) for k in (10.0, 100.0, 1e3)), sm + " low_frequency.corner_hz")
        if "jfet_flicker_share" in lf:
            sh = {float(k): v for k, v in lf["jfet_flicker_share"].items()}
            put(g, f"{who}: the input JFETs' flicker share of the output noise at 10 Hz | 100 Hz | 1 kHz | 10 kHz (%)",
                sh, " | ".join(f(100 * sh[k], 1) for k in (10.0, 100.0, 1e3, 1e4)), sm + " low_frequency")
    for key in ("SR560", "SR560_LSK389B"):
        for name, lab in (("tail_servo_share_rs_1e6", "1 Mohm in input A, input B grounded"),
                          ("balanced_tail_servo_share_rs_1e6", "1 Mohm in input A and from input B to ground")):
            sh = {float(k): v for k, v in m[key][name].items()}
            put(g, f"{key}: the tail servo's share of the output noise, {lab}, at 10 kHz | 100 kHz | 1 MHz (%)",
                sh, " | ".join(f(100 * sh[k], 2 if sh[k] < 0.01 else 0) for k in (1e4, 1e5, 1e6)), sm + " " + name)
    # at 1 MHz with 1 Mohm: the SR560 models' noise current without the tail servo's share, as e_n w C
    for key in ("SR560", "SR560_LSK389B"):
        a = m[key]["at"]["1000000.0"]
        sh = m[key]["tail_servo_share_rs_1e6"]["1000000.0"]
        i_rest = math.sqrt(1 - sh) * a["i_n"]
        i_low = m[key]["at"]["1000.0"]["i_n"]
        c = math.sqrt(max(i_rest ** 2 - i_low ** 2, 0.0)) / (2 * math.pi * 1e6 * a["e_n"])
        put(g, f"{key} at 1 MHz: i_n without the servo's share (pA/rtHz); the C with which the plot's form, the "
               f"whole e_n times w C, would give it (pF)", (i_rest, c),
            f"{f(i_rest * 1e12, 2)}; {f(c * 1e12, 1)}", sm + " at, tail_servo_share_rs_1e6")
    # the SR560 models' input capacitance and their noise current by source (sr560_nf_sources.py)
    q, sq = load("sr560_nf_sources.json"), "sr560_nf_sources.json"
    fk = ("1000.0", "10000.0", "100000.0", "1000000.0")
    for key in ("SR560", "SR560_LSK389B"):
        z = q[key]["zin"]
        put(g, f"{key}: input capacitance (input A, input B grounded) at 1 kHz | 10 kHz | 100 kHz | 1 MHz (pF)",
            z, " | ".join(f(z[k]["c_in_pf"], 1) for k in fk), sq + " zin")
        c = q[key]["jfet_a_capacitance"]
        put(g, f"{key}: JFET A's C_gs + C_gd at its bias (pF)", c, f"{f(c['c_gs_pf'], 2)} + {f(c['c_gd_pf'], 2)} = "
            f"{f(c['sum_pf'], 2)}", sq + " jfet_a_capacitance")
        gr = q[key]["noise"]["groups"]
        ch = [gr["JFET A, channel"][k]["c_eff_pf"] for k in fk[1:]]
        put(g, f"{key}: JFET A's channel noise, effective capacitance at 10 kHz | 100 kHz | 1 MHz (pF)", ch,
            " | ".join(f(x, 2) for x in ch), sq + " noise.groups")
        rx = gr["JFET A, gate resistor RX"]["1000000.0"]["c_eff_pf"]
        put(g, f"{key}: JFET A's gate resistor RX (in series with the driven gate), effective capacitance at 1 MHz "
               "(pF)", rx, f(rx, 2), sq + " noise.groups")
        oth = {n: gr[n]["1000000.0"]["c_eff_pf"] for n in ("JFET B, channel", "JFET B, gate resistor RX",
                                                          "input pair, other", "U102", "rest")}
        put(g, f"{key}: the other sources' effective capacitances at 1 MHz, JFET B, the input pair's other "
               "generators, U102 and the rest (pF), range", oth, rng(list(oth.values()), 1), sq + " noise.groups")
    rat = {}
    for k in fk[1:]:
        i_l, i_d = (q[m_]["noise"]["groups"]["tail servo"][k]["i_n"] for m_ in ("SR560_LSK389B", "SR560"))
        c_l, c_d = (q[m_]["zin"][k]["c_in_pf"] for m_ in ("SR560_LSK389B", "SR560"))
        rat[k] = (i_l / i_d, c_l / c_d)
    put(g, "LSK389B over NPD5564 at 10 kHz | 100 kHz | 1 MHz: the servo's noise current; the input capacitance", rat,
        " | ".join(f(v[0], 2) for v in rat.values()) + "; " + " | ".join(f(v[1], 2) for v in rat.values()),
        sq + " noise.groups[tail servo], zin")
    # the white level (100 kHz): the reproductions against the plot, and against each other
    ew = {k: m[k]["low_frequency"]["e_n"]["100000.0"] for k in ("SR560", "SR560_LSK389B")}
    ew_ds = m["datasheet"]["low_frequency"]["e_n"]["100000.0"]
    below = {k: 100 * (1 - v / ew_ds) for k, v in ew.items()}
    mutual = 100 * (ew["SR560_LSK389B"] / ew["SR560"] - 1)
    put(g, "white level at 100 kHz: the reproductions below the plot, NPD5564 | LSK389B (%); the LSK389B model "
           "above the NPD5564 model (%)", (below, mutual),
        f"{f(below['SR560'], 1)} | {f(below['SR560_LSK389B'], 1)}; {f(mutual, 2)}", sm + " low_frequency.e_n")
    # per device: the 2N5564 card's single 1/f line against Vishay's curve at 4.5 mA
    cd = CARD_2N5564
    card = {f0: math.sqrt(cd["e_w"] ** 2 + (cd["e_lf"] ** 2 - cd["e_w"] ** 2) * cd["f_lf"] / f0) for f0 in (10.0, 100.0, 1e3)}
    x = math.log10(cd["id"] / 1e-3)
    vis = {f0: VISHAY_2N5564_EN[1e-3][f0] * (VISHAY_2N5564_EN[10e-3][f0] / VISHAY_2N5564_EN[1e-3][f0]) ** x
           for f0 in (10.0, 100.0, 1e3)}
    corner = cd["f_lf"] * (cd["e_lf"] ** 2 - cd["e_w"] ** 2) / cd["e_w"] ** 2
    put(g, "2N5564 card per device: its 1/f corner (kHz); e_n at 10 Hz | 100 Hz | 1 kHz, card / Vishay at 4.5 mA "
           "(nV/rtHz) and their ratio", dict(corner=corner, card=card, vishay=vis),
        f"{f(corner / 1e3, 1)}; " + " | ".join(f"{f(card[k], 1)} / {f(vis[k], 1)} = {f(card[k] / vis[k], 2)}"
                                              for k in (10.0, 100.0, 1e3)),
        "CARD_2N5564 (models.py targets), VISHAY_2N5564_EN (data sheet p. 5, survey Section 3.1)")
    # Vishay 10 kHz/10 mA style check: the excess power of the curve from 10 to 100 Hz at 10 mA
    v10 = VISHAY_2N5564_EN[10e-3]
    ratio = (v10[10.0] ** 2 - v10[1e5] ** 2) / (v10[100.0] ** 2 - v10[1e5] ** 2)
    put(g, "Vishay 2N5564 at 10 mA: excess power above the 100 kHz level, 10 Hz over 100 Hz (a 1/f line: 10)",
        ratio, f(ratio, 1), "VISHAY_2N5564_EN")
    put(g, "the pair from the card at 10 Hz: sqrt(2) e_card(10 Hz) (nV/rtHz)", math.sqrt(2) * card[10.0],
        f(math.sqrt(2) * card[10.0], 1), "CARD_2N5564")
    # the pair with Vishay's curve instead of the card at 10 Hz: the card's flicker replaced, the rest kept
    e10 = m["SR560"]["low_frequency"]["e_n"]["10.0"] * 1e9
    s10 = m["SR560"]["low_frequency"]["jfet_flicker_share"]["10.0"]
    pair = math.sqrt(2 * vis[10.0] ** 2 + (1 - s10) * e10 ** 2)
    put(g, "SR560 as drawn at 10 Hz with the JFETs of Vishay's curve: sqrt(2 e_V^2 + (1 - share) e^2) (nV/rtHz)",
        pair, f(pair, 0), "nf_map.json SR560.low_frequency, VISHAY_2N5564_EN")
    for key in ("H", "L"):
        for f0, row in m[key]["input_network"].items():
            put(g, f"{key}, {float(f0):g} Hz: i_n | R_Z's sqrt(4kT Re Y_Z) (pA/rtHz); R_Z's share of the output "
                   "noise with 1 kOhm | 100 kOhm (%)", row,
                f"{f(row['i_n'] * 1e12, 2)} | {f(row['i_rz'] * 1e12, 2)}; {f(100 * row['rza_share_of_output_noise_rs_1000'], 0)}"
                f" | {f(100 * row['rza_share_of_output_noise_rs_100000'], 0)}", sm + " input_network")


# ---- Section 6.3 -------------------------------------------------------------------------------
def section63():
    d = load("chain_ac.json")
    rows = (("H x10", ("H_LN_1", "H_LN_10", "H_HR_1", "H_HR_10", "H_HR_100", "H_HR_1000")),
            ("H x100", ("H_LN_100", "H_LN_1000", "H_LN_10000", "H_LN_50000")),
            ("L", ("L_200", "L_1000", "L_10000", "L_100000")))
    for lab, keys in rows:
        f3 = [d[k]["f3db"] / 1e6 for k in keys]
        nd = 2 if lab == "H x100" else 1
        put("table11", f"{lab}: -3 dB (MHz)", f3, rng(f3, nd), "chain_ac.json")
        for q, nd2 in (("db_1M", 2), ("db_10M", 2), ("peak_db", 2)):
            v = [d[k][q] for k in keys]
            put("table11", f"{lab}: {q}", v, rng(v, nd2), "chain_ac.json")
    s = load("sr560_chain.json")["ac"]
    f3 = [v["f3db"] / 1e6 for v in s.values()]
    d1 = [v["db_1M"] for v in s.values()]
    put("table11", "SR560: -3 dB (MHz)", f3, rng(f3, 2), "sr560_chain.json ac")
    put("table11", "SR560: at 1 MHz (dB)", d1, rng(d1, 1), "sr560_chain.json ac")
    pk = []
    for g in s:
        a = load(f"sr560_chain_ac_{g}.npz")
        h = np.abs(a["h"])
        pk.append(20 * math.log10(h.max() / at(a["f"], h, 1e3)))
    put("table11", "SR560: peaking (dB)", pk, f"{max(pk):.1e} dB at most (none)", "sr560_chain_ac_<gain>.npz, 1 Hz - 100 MHz")
    # the two further SR560 models (sr560_variants.py): corrected, and corrected with the LSK389B
    sv = load("sr560_variants.json")["models"]
    for m, lab in (("corrected", "SR560 corrected"), ("corrected_lsk389b", "SR560 corrected, LSK389B")):
        a = sv[m]["ac"]
        f3 = [v["f3db"] / 1e6 for v in a.values()]
        d1 = [v["db_1M"] for v in a.values()]
        pk = [v["peak_db"] for v in a.values()]
        put("table11", f"{lab}: -3 dB (MHz)", f3, rng(f3, 2), f"sr560_variants.json models.{m}.ac")
        put("table11", f"{lab}: at 1 MHz (dB)", d1, rng(d1, 1), f"sr560_variants.json models.{m}.ac")
        put("table11", f"{lab}: peaking (dB)", pk, f"{max(pk):.1e} dB at most", f"sr560_variants.json models.{m}.ac.*.peak_db")
        c = sv[m]["cmrr_ideal_matching"]
        put("table12", f"{lab}, ideal matching: 10 Hz | 1 kHz | 10 kHz | 100 kHz | 1 MHz (dB)", list(c.values()),
            " | ".join(f(v, 1) for v in c.values()), f"sr560_variants.json models.{m}.cmrr_ideal_matching")
    c = load("sr560_chain.json")["cmrr_ideal_matching"]
    put("table12", "SR560 reproduction (as drawn), ideal matching: 10 Hz | 1 kHz | 10 kHz | 100 kHz | 1 MHz (dB)",
        list(c.values()), " | ".join(f(v, 1) for v in c.values()), "sr560_chain.json cmrr_ideal_matching")
    post = [v["out"]["f3db"] / 1e6 for v in load("chain_extras.json")["post"].values()]
    put("s6.3", "stages after the front end alone: -3 dB (MHz)", post, rng(post, 0),
        "chain_extras.json post (chain_extras.py post)")
    pk = {fe: load("zin_numbers.json")[fe]["network_largest_peak_db"] for fe in ("H100", "L200")}
    put("s6.3", "largest peaking with the input network (dB)", pk, f"H {f(pk['H100'], 2)}, L {f(pk['L200'], 3)}",
        "zin_numbers.json network_largest_peak_db (sources 50 ohm, 1 kohm, 1 Mohm)")


# ---- Section 6.4 -------------------------------------------------------------------------------
def section64():
    c = load("cmrr_mc.json")
    tr = {k: v["trials"] for k, v in c.items() if isinstance(v, dict) and "trials" in v and k != "rup_test"}
    put("s6.4", "trials per case", tr, "12 (full cases), 6 (one class), 4 (R_UP test)", "cmrr_mc.json trials")
    assert {tr[k] for k in tr if "_only_" in k} == {6} and tr["H100"] == 12 and tr["H100_jfet_rs0_R_UP"] == 4
    # the JFE2140 halves and the JFE150 bin
    sd = math.sqrt(2) * SIGMA_HALF_MV
    mean_abs = sd * math.sqrt(2 / math.pi)
    put("s6.4", "JFE2140: sigma of the halves' difference (mV)", sd, f(sd, 2), "sqrt(2) x 0.85 mV (cmrr_mc.py)")
    put("s6.4", "JFE2140: mean |dV_GS| (mV)", mean_abs, f(mean_abs, 2),
        "sigma_d sqrt(2/pi); data sheet 1 mV typ, 4 mV max (SLPS730B p. 5)")
    ub = BIN_HALF_MV / math.sqrt(3)
    put("s6.4", "JFE150: sigma of a uniform +-5 mV bin (mV)", ub, f(ub, 1), "w / sqrt(3); cmrr_mc.py uses 3 mV")
    # input networks' Delta C (L)
    zl = load("zin_numbers.json")["L200"]["network"]
    cp, cz, s, rs, f0 = zl["cp"], zl["cz"], 0.025, 50.0, 1e6
    sig_c = s * math.hypot(cp, cz)
    dc = math.sqrt(2) * sig_c
    z75 = 0.6744897501960817          # median of |N(0, 1)| = Phi^-1(0.75)
    cm_rms = 20 * math.log10(1 / (2 * math.pi * f0 * rs * dc))
    cm_med = 20 * math.log10(1 / (2 * math.pi * f0 * rs * z75 * dc))
    sim_med = at(c["L200_only_c"]["freq"], c["L200_only_c"]["median"], 1e6)
    put("s6.4", "L: Delta C rms = sqrt(2) 2.5 % sqrt(C_P^2 + C_Z^2) (pF)", dc * 1e12, f(dc * 1e12, 1),
        "C_P 30 pF, C_Z 220 pF (zin_numbers.json L200.network), 2.5 % (cmrr_mc.py)")
    put("s6.4", "L: CMRR at 1 MHz, 50 ohm, Delta C rms (dB)", cm_rms, f(cm_rms, 0), "1 / (2 pi f R_S Delta C)")
    put("s6.4", "L: CMRR at 1 MHz, 50 ohm, median |Delta C| (dB)", cm_med, f(cm_med, 0), "0.6745 Delta C_rms")
    put("s6.4", "L: capacitor-only runs, median at 1 MHz (dB)", sim_med, f(sim_med, 0), "cmrr_mc.json L200_only_c")
    old = 20 * math.log10(1 / (2 * math.pi * f0 * rs * math.sqrt(2) * s * (cp + cz)))
    put("s6.4", "for reference: 250 pF as one part (dB)", old, f(old, 1), "the note's earlier estimate")
    # trimmed against untrimmed (L, 1 MHz), 10 Hz and 1 kHz levels, discrete resistors
    rec = at(c["L200_trimmed"]["freq"], c["L200_trimmed"]["median"], 1e6) - at(c["L200"]["freq"], c["L200"]["median"], 1e6)
    put("s6.4", "L: trimming recovers at 1 MHz (dB)", rec, f(rec, 0), "cmrr_mc.json L200_trimmed - L200")
    for k in ("H100", "L200", "H10", "H100_rs0", "L200_rs0"):
        v = (at(c[k]["freq"], c[k]["median"], 10), at(c[k]["freq"], c[k]["median"], 1e3))
        put("s6.4", f"{k}: median at 10 Hz / 1 kHz (dB)", v, f"{f(v[0], 0)} / {f(v[1], 0)}", "cmrr_mc.json")
    disc = at(c["H100"]["freq"], c["H100"]["median"], 1e3) - at(c["H100_discrete"]["freq"], c["H100_discrete"]["median"], 1e3)
    put("s6.4", "discrete S2 resistors: cost at 1 kHz (dB)", disc, f(disc, 0), "cmrr_mc.json H100 - H100_discrete")
    put("s6.4", "H100 network / discrete at 1 kHz (dB)",
        (at(c["H100"]["freq"], c["H100"]["median"], 1e3), at(c["H100_discrete"]["freq"], c["H100_discrete"]["median"], 1e3)),
        f"{f(at(c['H100']['freq'], c['H100']['median'], 1e3), 1)} / {f(at(c['H100_discrete']['freq'], c['H100_discrete']['median'], 1e3), 1)}",
        "cmrr_mc.json")
    r = [at(c["H100_only_r"]["freq"], c["H100_only_r"]["median"], x) for x in (10, 1e3, 1e4, 1e5)]
    put("s6.4", "H100 resistors only, 10 Hz - 100 kHz (dB)", r, rng(r, 0), "cmrr_mc.json H100_only_r")
    # the R_UP test
    rt = c["rup_test"]
    put("s6.4", "R_BS / R_UP", rt["R_BS_over_R_UP"], f(rt["R_BS_over_R_UP"], 2), "cmrr_mc.json rup_test (3.5 k / 10.9 k)")
    put("s6.4", "f_BS = 1/(2 pi R_BS C_BS) (Hz)", rt["f_BS"], f(rt["f_BS"], 0), "cmrr_mc.json rup_test")
    for i, f0 in enumerate(rt["freq"]):
        put("s6.4", f"R_UP test at {f0:g} Hz: R_UP -> ideal I_BS (improvement)",
            (rt["median_R_UP"][i], rt["median_ideal_I_BS"][i], rt["improvement_dB"][i]),
            f"{f(rt['median_R_UP'][i], 1)} -> {f(rt['median_ideal_I_BS'][i], 1)} ({f(rt['improvement_dB'][i], 1)})",
            "cmrr_mc.json rup_test")
    a, b = c["H100_jfet_rs0_R_UP"], c["H100_jfet_rs0_ideal_I_BS"]
    hi = [abs(at(b["freq"], b["median"], x) - at(a["freq"], a["median"], x)) for x in (1e4, 1e5, 1e6, 3e6, 1e7)]
    put("s6.4", "R_UP test: largest change from 10 kHz to 10 MHz (dB)", max(hi), f(max(hi), 2),
        "cmrr_mc.json H100_jfet_rs0_*")
    # SR560 specification and the NF 5307 plot
    sp = {x: SR560_CMRR_DS - 20 * math.log10(x / 1e3) for x in (1e4, 1e5, 1e6)}
    put("s6.4", "SR560 specification above 1 kHz (dB)", sp, ", ".join(f"{f(v, 0)} at {x:g} Hz" for x, v in sp.items()),
        "100 dB - 20 log10(f / 1 kHz), SR560 data sheet p. 3")
    sm = SR560_CMRR_MAN - 20 * math.log10(1e6 / 1e3)
    put("s6.4", "SR560 manual: CMRR at 1 MHz (dB)", sm, f"> {f(sm, 0)}", ">90 dB to 1 kHz, -20 dB/decade (manual p. 5)")
    put("s6.4", "NF 5307 plot, gain 100 (dB)", NF_CMRR_PLOT, " | ".join(f(v, 0) for v in NF_CMRR_PLOT.values()),
        "NF_5307_datasheet_fig46.jpg, read by eye, at 10 Hz, 1 kHz, 10 kHz, 100 kHz, 1 MHz")


# ---- Section 6.5 -------------------------------------------------------------------------------
def section65():
    ls = load("large_signal.json")
    for fe in ("H100", "L1000"):
        for r in ls[fe]["thd"]:
            nd = 4 if r["thd"] * 100 < 0.01 else 3
            put("table13", f"{fe} THD {r['f0']:g} Hz {r['vout_pp']} Vpp (%)", r["thd"] * 100, f(r["thd"] * 100, nd),
                "large_signal.json")
    fl = load("large_signal_floor.json")
    for r in fl["L1000_10MHz_1Vpp"]:
        put("s6.5", f"L1000 10 MHz 1 Vpp, S2 {r['S2']}, sinks {r['l_sink']} (%)", r["thd"] * 100,
            f(r["thd"] * 100, 4), "large_signal_floor.json L1000_10MHz_1Vpp")
    lin = [dbc(x["thd"]) for fe in ("H100", "L1000") for x in fl["linear_reference"][fe]["rows"]]
    put("s6.5", "floor: linear reference, dBc (max / min)", (max(lin), min(lin)), f"{f(max(lin), 0)} to {f(min(lin), 0)}",
        "large_signal_floor.json linear_reference (H100 and L1000)")
    by_f: dict = {}
    failed = []
    for x in fl["chain_settings"]:
        if "thd" not in x:                     # a setting whose transient stopped (recorded, skipped)
            failed.append(f"{x['settings']} at {x['f0']:g} Hz")
            continue
        by_f.setdefault(x["f0"], []).append(dbc(x["thd"]))
    put("s6.5", "floor: chain settings that stopped", failed, "; ".join(failed) or "none",
        "large_signal_floor.json chain_settings ('failed' entries)")
    for f0, v in by_f.items():
        put("s6.5", f"floor: chain settings at {f0:g} Hz, dBc (range; spread dB)", v,
            f"{rng(v, 1)} dBc; spread {f(max(v) - min(v), 2)} dB", "large_signal_floor.json chain_settings (5 settings)")
    spread = max(max(v) - min(v) for v in by_f.values())
    put("s6.5", "floor: largest spread over the settings (dB)", spread, f(spread, 1), "large_signal_floor.json chain_settings")
    # steps: chain against the front end alone (chain_extras.json step)
    st = load("chain_extras.json")["step"]
    for vk in ("1 V", "10 V"):
        for node in ("front_end_alone", "chain_fe_out", "chain_S2_out", "chain_out"):
            x = st[vk][node]
            put("s6.5", f"step {vk}, {node}: overshoot (%) / slew (V/us)", (x["overshoot"], x["slew_v_us"]),
                f"{f(x['overshoot'] * 100, 1)} % / {f(x['slew_v_us'], 0)} V/us", "chain_extras.json step")
    sr = ls["H100"]["step"][1]["slew_v_us"]
    fp = sr * 1e6 / (math.pi * 10) / 1e6
    put("s6.5", "full-power bandwidth, 10 Vpp: SR / (pi 10 V) (MHz)", fp, f(fp, 2), "large_signal.json H100 step 10 V")
    # L's steps with its adopted sinks (large_signal.py L1000 step: they run with the KLU solver on the 50-ohm
    # bench), and with the first design's 2 V sinks (large_signal_L1000_step.json), which give the same
    ls_l = ls["L1000"]["step"][1]
    put("table13", "L 10 V step: rise, overshoot, 1 % / 0.1 %, slew", ls_l,
        f"{f(ls_l['rise_ns'], 0)} ns, {f(ls_l['overshoot'] * 100, 1)} %, {f(ls_l['settle_ns_1'], 0)} / "
        f"{f(ls_l['settle_ns_0p1'], 0)} ns, {f(ls_l['slew_v_us'], 0)} V/us", "large_signal.json L1000 step (6 V sinks)")
    ls_l1 = ls["L1000"]["step"][0]
    put("table13", "L 1 V step: rise, overshoot, 1 % / 0.1 %", ls_l1,
        f"{f(ls_l1['rise_ns'], 0)} ns, {f(ls_l1['overshoot'] * 100, 1)} %, {f(ls_l1['settle_ns_1'], 0)} / "
        f"{f(ls_l1['settle_ns_0p1'], 0)} ns", "large_signal.json L1000 step (6 V sinks)")
    put("table13", "L steps: bench and options", [x.get("bench", "1 ohm sources") for x in ls["L1000"]["step"]],
        "; ".join(x.get("bench", "1 ohm sources") for x in ls["L1000"]["step"]), "large_signal.json L1000 step")
    two = load("large_signal_L1000_step.json")
    dmax = max(abs(a[k] - b[k]) for a, b in zip(ls["L1000"]["step"], two) for k in ("settle_ns_1", "settle_ns_0p1", "rise_ns"))
    put("table13", "L steps, 6 V against 2 V sinks: largest difference in rise and settling (ns)", dmax, f(dmax, 2),
        "large_signal.json L1000 step against large_signal_L1000_step.json")
    for i, vk in enumerate(("1 V", "10 V")):
        s_ = ls["H100"]["step"][i]
        put("table13", f"H {vk} step: rise, overshoot, 1 % / 0.1 %, slew", s_,
            f"{f(s_['rise_ns'], 0)} ns, {f(s_['overshoot'] * 100, 1)} %, {f(s_['settle_ns_1'], 0)} / "
            f"{f(s_['settle_ns_0p1'], 0)} ns, {f(s_['slew_v_us'], 0)} V/us", "large_signal.json H100 step")
    for fe in ("H100", "L1000"):
        for r in ls[fe]["thd"]:
            if r["f0"] == 1e7:
                put("table13", f"{fe} fundamental at 10 MHz, 1 Vpp (Vpp)", r["fund_pp"], f(r["fund_pp"], 3),
                    "large_signal.json")
    for r in ls["H100"]["thd"]:
        if (r["f0"], r["vout_pp"]) in ((1e6, 10), (1e7, 1)):
            put("s6.5", f"H100 THD {r['f0']:g} Hz {r['vout_pp']} Vpp: H3 / H2 (%)", (r["h3"] * 100, r["h2"] * 100),
                f"{r['h3'] * 100:.2g} / {r['h2'] * 100:.2g}", "large_signal.json (h2, h3: harmonic / fundamental)")
    t31 = load("large_signal_THS4031.json")["H100"]
    put("s6.5", "H recovery with the THS4031 in S2, 1-ohm sources (us)", t31["overload"]["recovery_us"],
        f(t31["overload"]["recovery_us"], 2), "large_signal_THS4031.json")
    ho = ls["H100"]["overload"]  # with the LM7171 in S2: runs only with the KLU solver (overload_detail.py)
    put("table13", "H recovery (LM7171 in S2) (us); options; bench", [ho["recovery_us"], ho["options"], ho["bench"]],
        f(ho["recovery_us"], 2), "large_signal.json H100.overload (overload_detail.py)")
    lo_ = ls["L1000"]["overload"]
    put("table13", "L recovery (us); options; bench", [lo_["recovery_us"], lo_["options"], lo_["bench"]],
        f(lo_["recovery_us"], 2), "large_signal.json L1000.overload (overload_detail.py)")
    put("table14", "THS4031 slew rate, 10 V step (V/us)", t31["step"][1]["slew_v_us"], f(t31["step"][1]["slew_v_us"], 0),
        "large_signal_THS4031.json")
    # overload (overload_numbers.json and the formulas above)
    o = load("overload_numbers.json")
    h, l = o["H100"], o["L1000"]
    op = h["opamp_outputs"]
    put("s6.5", "H: op-amp clip levels and difference (V)", (op["oa_during_V"], op["ob_during_V"], op["difference_during_V"]),
        f"+{f(op['oa_during_V'], 1)} / {f(op['ob_during_V'], 1)}; {f(op['difference_during_V'], 1)}", "overload_numbers.json")
    put("s6.5", "H: outputs after the release, min oa / max ob (V; from rest)",
        (op["oa_min_after_V"], op["ob_max_after_V"], op["oa_min_after_from_rest_V"], op["ob_max_after_from_rest_V"]),
        f"{f(op['oa_min_after_V'], 2)} / +{f(op['ob_max_after_V'], 2)} ({f(op['oa_min_after_from_rest_V'], 2)} / "
        f"+{f(op['ob_max_after_from_rest_V'], 2)})", "overload_numbers.json")
    put("s6.5", "H: outputs within 12 mV of rest after (us)", op["within_12mV_after_us"], f(max(op["within_12mV_after_us"]), 2),
        "overload_numbers.json")
    ra = h["output_ramp"]
    put("s6.5", "H: output ramp: delay (ns), 10-90 % slope, peak over 5 ns (V/us)",
        (ra["delay_to_1pct_ns"], ra["slope_10_90_V_us"], ra["peak_slope_5ns_V_us"], ra["peak_slope_V_us"]),
        f"{f(ra['delay_to_1pct_ns'], 0)} ns, {f(ra['slope_10_90_V_us'], 0)} V/us, {f(ra['peak_slope_5ns_V_us'], 0)} V/us",
        "overload_numbers.json output_ramp")
    sa, sb = h["sides"]["a"], h["sides"]["b"]
    put("s6.5", "H: dV_GS side a / b (mV)", (sa["dV_GS_V"], sb["dV_GS_V"]),
        f"+{f(sa['dV_GS_V'] * 1e3, 1)} / {f(sb['dV_GS_V'] * 1e3, 1)}", "overload_numbers.json sides")
    put("s6.5", "H: JFET current shift dI = -dV_c / R_D, side a / b (mA)", (sa["dI_from_R_D_mA"], sb["dI_from_R_D_mA"]),
        f"+{f(sa['dI_from_R_D_mA'], 2)} / {f(sb['dI_from_R_D_mA'], 2)}", "overload_numbers.json sides, R_D 600 ohm")
    put("s6.5", "H: g_m dV_GS, side a / b (mA)", (sa["dI_gm_estimate_mA"], sb["dI_gm_estimate_mA"]),
        f"+{f(sa['dI_gm_estimate_mA'], 2)} / {f(sb['dI_gm_estimate_mA'], 2)}", "overload_numbers.json sides")
    put("s6.5", "H: summing nodes rest -> during, a / b (V)", (sa["summing_rest_V"], sa["summing_during_V"], sb["summing_during_V"]),
        f"{f(sa['summing_rest_V'], 2)} -> {f(sa['summing_during_V'], 2)} / {f(sb['summing_during_V'], 2)}",
        "overload_numbers.json sides")
    put("s6.5", "H: summing nodes within 10 mV after (us)", sa["summing_within_10mV_after_us"],
        f(sa["summing_within_10mV_after_us"], 2), "overload_numbers.json sides")
    vgs = -h["V_GS_rest_V"]
    put("s6.5", "H: |V_GS| at rest (V)", vgs, f(vgs, 2), "overload_numbers.json V_GS_rest_V")
    sv = h["servo"]
    e = sv["error_during_V"]
    rate = G_INT * e / C_INT
    put("s6.5", "H: outputs' mean / sources' mean during the overload (V)",
        (sv["outputs_mean_during_V"], sv["sources_mean_during_V"]),
        f"+{f(sv['outputs_mean_during_V'], 2)} / +{f(sv['sources_mean_during_V'], 2)}", "overload_numbers.json servo")
    put("s6.5", "servo: error e (V); rate G_INT e / C_INT (V/s)", (e, rate), f"{f(e, 2)} V; {f(rate, 2)} V/s",
        "overload_numbers.json servo; G_INT 1 uS, C_INT 1 uF (frontend.py)")
    put("s6.5", "servo (Appendix B, if used): change over 20 us (uV), formula / error integral",
        (rate * 20e-6 * 1e6, sv["integrator_change_uV"]),
        f"{f(rate * 20e-6 * 1e6, 1)} / {f(sv['integrator_change_uV'], 2)}", "rate x 20 us; overload_numbers.json")
    ratio = sv["R_F"] / sv["R_T"]
    cm1 = ratio * rate * 1.0
    tau = (C_INT / G_INT) * (sv["R_T"] / sv["R_F"])
    put("s6.5", "servo after 1 s: reference (V), R_F / R_T, outputs' CM (V), tau (s)", (rate * 1.0, ratio, cm1, tau),
        f"{f(rate, 2)} V; {f(ratio, 2)}; {f(cm1, 2)} V; {f(tau, 2)} s", "overload_numbers.json servo (R_F 500, R_T 181.8 ohm)")
    put("s6.5", "bootstrap R_BS C_BS (ms)", R_BS * C_BS * 1e3, f(R_BS * C_BS * 1e3, 1), "Table 5: 3.5 kohm, 1 uF")
    lo = h["larger_overloads"]
    vsd = op["difference_during_V"] * 10.1 / (2 * 500 + 10.1)
    assert abs(vsd - lo["source_difference_with_clipped_outputs_V"]) < 1e-9
    put("s6.5", "larger overloads: v_s,d (V), dV_GS at 10x (V), zero bias at (V; x full scale)",
        (vsd, lo["dV_GS_estimate_at_10x_V"], lo["input_for_zero_gate_bias_V"], lo["overdrive_for_zero_gate_bias"]),
        f"{f(vsd, 2)}; {f(lo['dV_GS_estimate_at_10x_V'], 2)}; {f(lo['input_for_zero_gate_bias_V'], 2)} V "
        f"({f(lo['overdrive_for_zero_gate_bias'], 1)} x)", "overload_numbers.json larger_overloads; R_G 10.1, R_F 500 ohm")
    u = l["undershoot"]
    hu = h["undershoot"]
    put("s6.5", "H: undershoot (V), time beyond -0.1 V (ns), overshoot after (V), recovery (us)",
        (hu["depth_V"], hu["beyond_minus_0p1V_duration_ns"], hu["overshoot_after_V"], h["recovery_us"]),
        f"{f(-hu['depth_V'], 2)}; {f(hu['beyond_minus_0p1V_duration_ns'], 0)}; {f(hu['overshoot_after_V'], 2)}; "
        f"{f(h['recovery_us'], 2)}", "overload_numbers.json H100")
    put("s6.5", "L: undershoot (V), time beyond -0.1 V (ns), recovery (us), FE outputs apart (V)",
        (u["depth_V"], u["beyond_minus_0p1V_duration_ns"], l["recovery_us"], l["fe_out_during_V"]),
        f"{f(-u['depth_V'], 2)}; {f(u['beyond_minus_0p1V_duration_ns'], 0)}; {f(l['recovery_us'], 2)}; "
        f"{f(l['fe_out_during_V'], 1)}", "overload_numbers.json L1000")
    # Table 14 and its paragraph
    dc = load("da_compare.json")
    h3 = {s2: dbc(dc[s2]["thd"][0]["h3"]) for s2 in ("THS4031", "LM7171", "THS3091")}
    for s2, v in h3.items():
        put("table14", f"{s2}: HD3 at 10 MHz, 1 Vpp (dBc)", v, f(v, 1), "da_compare.json thd[0].h3")
    scaled = THS4031_HD3_DS_DBC + 20 * math.log10((1 / 2) ** 2)
    put("table14", "THS4031 data sheet HD3 scaled to 1 Vpp (dBc)", scaled, f(scaled, 1),
        "-50 dBc at 2 Vpp (SLOS224L Fig. 5-15, p. 12) + 20 log10((1/2)^2)")
    put("table14", "THS4031 model above the data sheet: as read / scaled (dB)",
        (h3["THS4031"] - THS4031_HD3_DS_DBC, h3["THS4031"] - scaled),
        f"{f(h3['THS4031'] - THS4031_HD3_DS_DBC, 1)} / {f(h3['THS4031'] - scaled, 1)}", "as model_defects.json opamp/THS4031 HD3")
    for lab, ref in (("scaled", scaled), ("as read", THS4031_HD3_DS_DBC)):
        dd = ref - h3["LM7171"]
        put("table14", f"THS4031 data sheet ({lab}) above the LM7171 (dB; ratio)", (dd, 10 ** (dd / 20)),
            f"{f(dd, 1)} dB; {f(10 ** (dd / 20), 1)} times", "data sheet value - da_compare.json LM7171 h3")
    for s2 in ("THS4031", "LM7171", "THS3091"):
        r1, r2 = dc[s2]["thd"][0], dc[s2]["thd"][1]
        n10, n100 = dc[s2]["noise"]["H_HR_10"], dc[s2]["noise"]["H_LN_100"]
        put("table14", f"{s2}: THD 10 MHz 1 Vpp / 1 MHz 10 Vpp (%); noise gain 10, 100: 1 MHz / 1 kHz",
            None, f"{sig(r1['thd'] * 100, 2 if s2 != 'THS4031' else 3)} / {sig(r2['thd'] * 100, 3 if s2 == 'THS4031' else 2)} | "
            f"{f(n10['1000000.0'] * 1e9, 2)} / {f(n10['1000.0'] * 1e9, 2)} | {f(n100['1000000.0'] * 1e9, 2)} / "
            f"{f(n100['1000.0'] * 1e9, 2)}", "da_compare.json")
    md = load("model_defects.json")["opamp"]["THS3091"]["e_n_white"] * 1e9
    put("table14", "THS3091 model, white e_n (nV/rtHz)", md, f(md, 1), "model_defects.json opamp.THS3091.e_n_white")
    put("table14", "data sheets: THS4031 e_n, BW; LM7171A e_n, SR, UGBW; THS3091 e_n",
        (THS4031_EN, THS4031_BW_MHZ, LM7171A_EN, LM7171_SR, LM7171A_UGBW_MHZ, THS3091_EN),
        f"{THS4031_EN} nV, {THS4031_BW_MHZ} MHz; {LM7171A_EN} nV, {LM7171_SR} V/us, {LM7171A_UGBW_MHZ} MHz; {THS3091_EN} nV",
        "SLOS224L pp. 1, 6; SNOS760D Sec. 5.5 p. 5; SLOS423K pp. 1, 6")


# ---- Section 6.6, Table 15 ---------------------------------------------------------------------
def table15():
    cn = load("chain_noise.json")
    h = [cn[k]["en"] for k in ("H_LN_1000", "H_LN_10000", "H_LN_50000")]
    l = [cn[k]["en"] for k in ("L_1000", "L_10000", "L_100000")]
    put("table15", "H, gain >= 1000: white (100 kHz) / 1 kHz", None,
        f"{rng([x['100000.0'] * 1e9 for x in h], 2)} / {rng([x['1000.0'] * 1e9 for x in h], 2)}", "chain_noise.json")
    put("table15", "L, gain >= 1000: white (100 kHz) / 1 kHz", None,
        f"{rng([x['100000.0'] * 1e9 for x in l], 2)} / {rng([x['1000.0'] * 1e9 for x in l], 2)}", "chain_noise.json")
    put("table15", "H, gain 100: white / 1 kHz", None,
        f"{f(cn['H_LN_100']['en']['100000.0'] * 1e9, 2)} / {f(cn['H_LN_100']['en']['1000.0'] * 1e9, 2)}", "chain_noise.json")
    put("table15", "10 Hz, gain >= 1000: H / L", None,
        f"{rng([x['10'] * 1e9 for x in h], 2)} / {rng([x['10'] * 1e9 for x in l], 2)}", "chain_noise.json")
    g10 = cn["H_LN_10"]["en"]
    put("table15", "H, gain 10: white (100 kHz) to 1 kHz", None,
        f"{f(g10['100000.0'] * 1e9, 1)}–{f(g10['1000.0'] * 1e9, 1)}", "chain_noise.json")
    sr = load("sr560_chain.json")["noise"]
    put("table15", "SR560 reproduction, gain >= 1000: white / 1 kHz / 10 Hz; gain 10 at 1 kHz", None,
        f"{rng([sr[f'LN_{g}']['en']['100000.0'] * 1e9 for g in (1000, 10000, 50000)], 1)} / "
        f"{rng([sr[f'LN_{g}']['en']['1000.0'] * 1e9 for g in (1000, 10000, 50000)], 1)} / "
        f"{rng([sr[f'LN_{g}']['en']['10'] * 1e9 for g in (1000, 10000, 50000)], 0)}; {f(sr['LN_10']['en']['1000.0'] * 1e9, 1)}",
        "sr560_chain.json noise")
    for m in ("corrected", "corrected_lsk389b"):
        sm = load("sr560_variants.json")["models"][m]
        n = sm["noise"]
        put("table15", f"SR560 {m}, gain >= 1000: white / 1 kHz / 10 Hz; gain 10 at 1 kHz", None,
            f"{rng([n[f'LN_{g}']['en']['100000.0'] * 1e9 for g in (1000, 10000, 50000)], 1)} / "
            f"{rng([n[f'LN_{g}']['en']['1000.0'] * 1e9 for g in (1000, 10000, 50000)], 1)} / "
            f"{rng([n[f'LN_{g}']['en']['10'] * 1e9 for g in (1000, 10000, 50000)], 1)}; {f(n['LN_10']['en']['1000.0'] * 1e9, 1)}",
            f"sr560_variants.json models.{m}.noise")
        f3 = [v["f3db"] / 1e6 for v in sm["ac"].values()]
        c = sm["cmrr_ideal_matching"]
        put("table15", f"SR560 {m}: bandwidth (MHz); CMRR 1 kHz / 1 MHz (dB)", None,
            f"{rng(f3, 2)} MHz; {f(c['1000.0'], 1)} / {f(c['1000000.0'], 1)} dB", f"sr560_variants.json models.{m}")
    c = load("sr560_chain.json")["cmrr_ideal_matching"]
    put("table15", "SR560 reproduction (as drawn): CMRR 1 kHz / 1 MHz (dB)", None,
        f"{f(c['1000.0'], 1)} / {f(c['1000000.0'], 1)} dB", "sr560_chain.json cmrr_ideal_matching")
    pr = load("protection.json")["input_capacitance"]
    put("table15", "input capacitance C_P + C_Z: H / L (pF)", (pr["H"]["C_in"], pr["L"]["C_in"]),
        f"{f(pr['H']['C_in'] * 1e12, 0)} / {f(pr['L']['C_in'] * 1e12, 0)}", "protection.json input_capacitance")
    c = load("cmrr_mc.json")
    for k in ("H100_rs0", "L200_rs0"):
        v = (at(c[k]["freq"], c[k]["median"], 1e3), at(c[k]["freq"], c[k]["median"], 1e6))
        put("table15", f"CMRR {k}: 1 kHz / 1 MHz (dB)", v, f"{f(v[0], 0)} / {f(v[1], 0)}", "cmrr_mc.json")
    put("table15", "SR560 specification", None,
        f"{SR560_EN:g} nV at 1 kHz; {SR560_EN_10HZ:g} at 10 Hz (curve); {SR560_EN_G10:g} at gain 10; {SR560_CIN_PF:g} pF; "
        f"{SR560_BW_MHZ:g} MHz ({SR560_BW_TYP_MHZ:g} typ.)", "SR560 manual printed pp. 5, 20, 21; data sheet p. 3")
    put("table15", "NF 5307 specification and plots", None,
        f"{NF_EN_SPEC:g} nV (spec., gain 1000); {srng(NF_EN_PLOT_G100, 1)} (plot, gain 100); {srng(NF_EN_PLOT_G100_10HZ, 1)} "
        f"at 10 Hz; {srng(NF_EN_PLOT_G10, 2)} at gain 10; < {NF_CIN_PF:g} pF; >= {NF_CMRR_SPEC:g} dB; gains "
        f"{NF_GAINS[0]}-{NF_GAINS[1]}", "NF_5307_specifications_EN.pdf; manual Fig. 4.7 (PDF p. 37); data-sheet page Fig. 46")


# ---- Section 7 and the Appendix ----------------------------------------------------------------
def section7():
    d = load("curves_loop.npz")
    for fe in ("H100", "L200"):
        fr, t = d[f"out_{fe}_cm_f"], d[f"out_{fe}_cm_T"]
        m = F._margins(fr, t)
        g = min(m["gain_margins"], key=lambda x: x["gm_db"])
        j = int(np.argmin(np.abs(fr - g["f"])))           # the grid point past the crossing
        ph = np.degrees(np.unwrap(np.angle(t)))
        lvl = -180 + 360 * round((ph[j] + 180) / 360)
        x = (lvl - ph[j - 1]) / (ph[j] - ph[j - 1])
        fx = 10 ** (math.log10(fr[j - 1]) + x * (math.log10(fr[j]) - math.log10(fr[j - 1])))
        put("s7", f"{fe}: CM gain margin (dB) at the grid point past -180 deg (MHz)", (g["gm_db"], g["f"] / 1e6),
            f"{f(g['gm_db'], 1)} dB at {f(g['f'] / 1e6, 1)} MHz", "curves_loop.npz out_*_cm, frontend._margins")
        put("s7", f"{fe}: CM -180 deg crossing, interpolated (MHz; nearest 5 MHz)", fx / 1e6,
            f"{f(fx / 1e6, 1)} ({f(5 * rhu(fx / 5e6, 0), 0)})", "log-f interpolation between the grid points around it")
    oc = load("osc_check.json")
    for k in ("H100_first", "H100_first_ties", "L200_first", "L200_first_ties"):
        put("appendix", f"{k}: dominant frequency (MHz), output pk-pk (V)", (oc[k]["cm_out"]["f_dom"], oc[k]["cm_out"]["pkpk"]),
            f"{f(oc[k]['cm_out']['f_dom'] / 1e6, 0)} MHz, {f(oc[k]['cm_out']['pkpk'], 2)} V", f"osc_check.json {k} ({oc[k]['bench']})")
    pr = load("protection.json")
    rx = pr["H_R_x_current_equals_voltage_noise"]
    put("s7", "H: source impedance where current noise = 1.08 nV/rtHz (kohm): bias only / with 1 nA",
        (rx["bias only"], rx["bias + 1e-09 A leakage"]), f"{f(rx['bias only'] / 1e3, 0)} / {f(rx['bias + 1e-09 A leakage'] / 1e3, 0)}",
        "protection.json H_R_x_current_equals_voltage_noise")
    bn = pr["bias_resistor_noise"]["1e+08"] * 1e15
    put("s7", "100 Mohm: sqrt(4kT/R) (fA/rtHz)", bn, sig(bn, 2), "protection.json bias_resistor_noise (300.15 K)")
    hc = pr["H_current_noise_with_leakage"]
    put("s7", "H current noise, bias + 1 pA ... 1 nA (fA/rtHz)", hc, rng([v * 1e15 for v in hc.values()], 1), "protection.json")
    lib = load("model_defects.json")["ltspice_library"]
    put("appendix", "LTspice library record", lib,
        f"LTspice {lib['ltspice_version']}, standard.jft {lib['modified_utc'][:10]}, SHA-256 {lib['sha256'][:8]}...{lib['sha256'][-4:]}, "
        f"{lib['cards']['2N5564']['kf']}", "model_defects.json ltspice_library")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    for step in (table8, table8a, stages_after, table9, section62, section62_nf_map, section63, section64, section65,
                 table15, section7):
        step()
    (R / "numbers_s6_7.json").write_text(json.dumps(OUT, indent=1, default=float), encoding="utf-8", newline="\n")
    w = max(len(q) for q, _, _ in ROWS)
    print(f"{'quantity':<{w}} | value | source")
    for q, v, s in ROWS:
        print(f"{q:<{w}} | {v} | {s}")
    print(f"\n{len(ROWS)} quantities; written {R / 'numbers_s6_7.json'}")


if __name__ == "__main__":
    main()
