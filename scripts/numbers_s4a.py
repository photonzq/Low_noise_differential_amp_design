"""Numbers of Sections 4.1-4.3.1 of the note (the chain, Table 6, the front end, the sinks' summary,
the loops, Tables 7, 7a, 7b, 7c, Figures 9-12) that are not a direct readout of one archived result:
arithmetic, ratios, unit conversions, single roundings, readouts of the archived JSON/npz files
named below, data-sheet constants (each cited where it is defined), the front ends' operating
points, and one noise run of H with NPN cascodes.

Constants: k = 1.380649e-23 J/K, q = 1.602176634e-19 C, T = 300.15 K (ngspice's 27 C).
Roundings: half up, once, from the unrounded value (the 'shown' field of an entry).

Section 4.1, the chain (chain_noise.json, Table 10):
    headroom of H_HR over H_LN         20 log10(G_FE,LN / G_FE,HR) = 20 log10(100 / 10)
    noise ratio                         r(f, G) = e_HR(f, G) / e_LN(f, G),  f = 1 kHz, 100 kHz (Table 10's
                                        columns), total gain G = 100 and 1000
Table 6 and Section 4.2 (operating point: frontend.check_op, and an op deck that prints the JFETs'
intrinsic junction voltages @j.<inst>[vgs], [vgd]):
    g_m per JFET                        @j.xja1.j1[gm];   N g_m per side
    JFET capacitance per input          data sheets: N C_iss, C_iss = 13 pF (JFE2140, TI SLPS730B,
                                        Sec. 6.5, p. 5, V_DS = 5 V) and 24 pF (JFE150, TI SLPS732B,
                                        Sec. 6.5, p. 5, V_DS = 5 V)
                                        model at the operating point: N [C(CGS, V_GS) + C(CGD, V_GD)],
                                        C(C0, V) = C0 / sqrt(1 - V / PB)  (V < FC PB; ngspice's JFET
                                        keeps the grading exponent at 0.5), cards in _lib/jfets.lib
    source-node and R_T currents        I_C = N I_D + I_BS,  I_BS = (V_P - V(b)) / R_UP,
                                        R_UP = (V_P - 0.6 V - V_BS) / 1 mA (frontend.side);
                                        I_T (R_T's current, base current included) from sink_power.json
The common-mode servo (Section 4.2):
    output error of a sink error eps    dV_o = eps (N I_D + I_BS) R_F    (eps = 1 % and an assumed 3 %;
                                        N I_D + I_BS = 11 mA (H), 61 mA (L), the design values)
    V_BE drift (H)                      dV_BE/dT from fe_closed_forms.json (drift, H100, 2 V);
                                        dI/I = |dV_BE/dT| / V_RT;  dI/dT = |dV_BE/dT| / R_T;
                                        R_F dI/dT (closed form) against the simulated output drift
                                        (fe_closed_forms.json, output_mV_per_K)
    sink mismatch (H)                   dI = m (N I_D + I_BS), m = 0.05 % (assumed);
                                        dV_o = dI R_F,  dV_in = dV_o / G
    servo loop                          f_int = g / (2 pi C_int) (g = 1 uS, C_int = 1 uF);
                                        f_filt = 1 / (2 pi R C) (1 kohm, 10 uF);
                                        T(f) = (R_F / R_T) (f_int / jf) / (1 + jf / f_filt)
                                        f_c = (R_F / R_T) f_int;  PM = 90 deg - atan(f_c / f_filt)
                                        (f_c well below f_filt, so |T(f_c)| = 1 to 0.04 %)
    servo clamp                         V_M + 1 V ... V_M + V_RT + 3 V (frontend.netlist, BSNK);
                                        the sinks' bases (v_ctrl in sink_power.json) relative to V_M
    averaging resistors                 i_n = sqrt(4kT / 100 kohm)
    bootstrap corner                    f_BS = 1 / (2 pi R_BS C_BS),  R_BS = V_BS / I_BS
    NPN cascode (run here)              H100 with the cascodes replaced by MMBTH10 (frontend.FE's
                                        default NPN), everything else as adopted (bootstrap 3.5 V, so
                                        the input JFETs' V_DS is 2.5 V instead of 3.9 V): the base
                                        current @qca1[ib] at the operating point; the input-referred
                                        noise of the group 'cascodes' (frontend.noise_groups) and of
                                        the cascodes' base-current sub-generators (onoise_qc*_ib) at
                                        10 kHz; the JFET cascodes' group from fe_gain_options.json
    Eq. (9)'s first two terms           JFET and R_G groups at 10 kHz: H from fe_gain_options.json,
                                        L from curves_noise.npz (front end alone)
    Spinelli and Haberman (2024)        R_B / G_n = 500 ohm / 1001 against 1 / g_m = 1 / 30 mS
                                        (repository version, p. 5: R_A = 1 ohm, R_B = 500 ohm,
                                        G_n = 1001, g_m ~ 30 mS; p. 4: DC-100 kHz, JFE2140)
Section 4.2.1:
    V_CE,min                            0.5 V, a design margin above V_CE(sat) <= 0.2 V at 10 mA and
                                        <= 0.3 V at 50 mA (onsemi MMBT3904LT1/D Rev. 15, p. 2;
                                        PZT3904T1/D Rev. 7, p. 2)
Section 4.3 (Eqs. (10)-(10b)):
    k_DM = g_m R_G / (2 + g_m R_G)      g_m = 2 x @j.xja1.j1[gm] (one side of H);  1 / k_DM
    C_par = N C(CGD_c, V_GD,c) + C_i    the cascodes' gate-drain capacitance at their bias (LSBF862
                                        card) and the THS4021's input capacitance C_i = 1.5 pF
                                        (TI SLOS265F, Sec. 5.6, p. 7)
    beta_CM = S / (S + C_node + C_par), beta_DM = D / (S + C_node + C_par),  S = C_I + C_X,
                                        D = C_I - C_X; first version (osc_check.FIRST) and final
    f_local,DM = GBW beta_DM            GBW = 2 GHz (SLOS265F, p. 1)
    Eq. (10b)                           GBW k_DM beta_CM,max,  beta_CM,max = 1 / 10 (stable at gains
                                        >= 10 V/V, SLOS265F, p. 1)
    D / S                               adopted H100: 4 / 14
    loop margins (curves_loop.npz)      outer loop (frontend.check_loop's convention): f_c = first
                                        point with |T| < 1, PM = 180 deg + arg T there, GM =
                                        -20 log10|T| at the point before the first -180 deg crossing;
                                        complete loop: frontend._margins (first point past each
                                        crossing); f_180 = the -180 deg crossing, unwrapped phase
                                        interpolated linearly in log f between the sweep points
    oscillation (osc_check.json)        H100_first (50-ohm bench), H100_first_ties (inputs tied
                                        through 1 milliohm), L200_first; final values H100_cnode220p
    bandwidth                           chain at total gain 100 with the first front end
                                        (da_compare_before_cnode.json, ac_H100, LM7171 in S2) against
                                        chain_ac.json H_LN_100; front ends alone (fe_gain_options.json,
                                        sink_power.json L200 | 6 V)
    comp_search sets                    number of entries in comp_search_{H100,L200,H10}.json
Section 4.3.1:
    Table 7a                            stability_corners.json, raw
    C_node E12 values                   270/220, 330/220, 560/470, 680/470; 1.3 and 1.5 times 220 and 470
    the R_F route's bandwidth           fe_gain_options.json f3db
    output current at full swing        I_o = V_o / R_F, V_o = 12 V (THS4021 V_O >= +-12 V into
                                        250 ohm, SLOS265F, Sec. 5.6, p. 7; I_O >= 80 mA, p. 7)
    unity-gain-stable op amps           f_local,DM <= f_u k_DM beta_max:  THS4031 f_u = 120 MHz,
                                        unity-gain stable (TI SLOS224L, p. 1); LM7171 stable for gains
                                        >= +2 (TI SNOS760D, p. 1), so beta_max = 1/2, f_u = 160 MHz
                                        (A grade) or 200 MHz (B grade) (SNOS760D, Sec. 5.5, p. 5);
                                        the outer loop scaled by the adopted ratio:
                                        f_outer = f_c,DM,outer x f_local,new / f_local,adopted
    low-voltage option                  lv_option_range.json, lv_option.json, opamp_noise_check.json:
                                        V_od,max = 2 (V_OH - V_GS1) at V_CM = 0; ranges at V_od = 1 and
                                        10 V; the model's swing; the corrected ADA4899 noise
    sensitivity peak                    f where |1 + T| is smallest (stability_corners.json f_modulus)
    modulus margin 0.5                  20 log10(1 / 0.5) dB

Writes ../sim/results/numbers_s4a.json and prints a table "section | quantity | value | shown | unit |
source" (kept as ../sim/results/numbers_s4a_log.txt).  Runs ngspice for the operating points of H100
and L200 and for H100 with NPN cascodes (op, AC and noise; a few seconds), with decks under
../sim/runs/numbers_s4a/ and ../sim/runs/fe/.
Usage: python numbers_s4a.py > ../sim/results/numbers_s4a_log.txt
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import replace
from decimal import ROUND_HALF_UP, Decimal

import numpy as np

import fe_closed_forms as FC
import frontend as F
import gain_options as GO
import spice

K, Q, T = 1.380649e-23, 1.602176634e-19, 300.15
R = spice.RESULTS
VCM_LO, VCM_HI = -8.0, 3.0        # servo_check.py's input common modes (VCM)

# ---- data-sheet and literature constants ----
THS4021 = dict(gbw=2e9,          # 2 GHz gain-bandwidth product: TI SLOS265F (rev. July 2024), p. 1, Sec. 1
               g_min=10.0,       # "Stable at gains >= 10 V/V": SLOS265F, p. 1, Sec. 1
               c_i=1.5e-12,      # input capacitance, typ.: SLOS265F, Sec. 5.6, p. 7
               v_o_min=12.0,     # output swing >= +-12 V at V_CC = +-15 V, R_L = 250 ohm: SLOS265F, p. 7
               i_o_min=80e-3)    # output current >= 80 mA at V_CC = +-15 V, R_L = 10 ohm: SLOS265F, p. 7
THS4031_FU = 120e6               # "unity-gain stable with 120MHz bandwidth": TI SLOS224L, p. 1, Sec. 3
LM7171 = dict(g_min=2.0,         # "stable for gains as low as +2 or -1": TI SNOS760D, p. 1, Sec. 3
              f_u_a=160e6,       # unity-gain bandwidth, LM7171A: SNOS760D, Sec. 5.5, p. 5
              f_u_b=200e6)       # unity-gain bandwidth, LM7171B: SNOS760D, Sec. 5.5, p. 5
C_ISS = {"H": 13e-12,            # JFE2140 C_iss at V_DS = 5 V: TI SLPS730B, Sec. 6.5, p. 5
         "L": 24e-12}            # JFE150 C_iss at V_DS = 5 V: TI SLPS732B, Sec. 6.5, p. 5
V_CE_SAT = {"10 mA": 0.2,        # V_CE(sat) max at I_C 10 mA, I_B 1 mA: onsemi MMBT3904LT1/D Rev. 15, p. 2,
            "50 mA": 0.3}        # and PZT3904T1/D Rev. 7, p. 2; 0.3 V at I_C 50 mA, I_B 5 mA (same pages)
SPINELLI = dict(r_a=1.0, r_b=500.0, g_n=1001.0,   # Spinelli and Haberman (2024), repository version, p. 5
                g_m=30e-3)                         # "g_m ~ 30 mS", p. 5
FIRST = {"H100": dict(ci=6.19e-12, cx=4.42e-12), "L200": dict(ci=13.4e-12, cx=7.8e-12)}   # osc_check.FIRST

OUT: dict = {}
ROWS: list = []


def rnd(x: float, nd: int) -> str:
    """x rounded half up to nd decimals (nd < 0: to tens, hundreds, ...), as a string.  x is first
    written with 12 significant digits, so that a product such as 0.03 x 11 mA x 500 ohm, which binary
    floating point gives as 0.16499999999999998, rounds as the exact 0.165 does."""
    q = Decimal(1).scaleb(-nd)
    return format(Decimal(f"{float(x):.12g}").quantize(q, rounding=ROUND_HALF_UP), "f")


def gm_txt(x: float, nd: int) -> str:
    """A gain margin for the 'shown' field; NaN (no -180 deg crossing with |T| < 1 after the crossover)
    as a dash."""
    return "-" if math.isnan(x) else f"{rnd(x, nd)} dB"


def put(section: str, name: str, value, unit: str, source: str, shown: str | None = None):
    entry = dict(value=value, unit=unit, source=source)
    if shown is not None:
        entry["shown"] = shown
    OUT.setdefault(section, {})[name] = entry
    ROWS.append((section, name, value, unit, shown, source))


def load(name: str) -> dict:
    return json.loads((R / name).read_text(encoding="utf-8"))


def cj(c0: float, v: float, pb: float, fc: float = 0.5) -> float:
    """ngspice's JFET junction capacitance with grading exponent 0.5 (valid for V < FC PB)."""
    assert v < fc * pb, (v, fc * pb)
    return c0 / math.sqrt(1 - v / pb)


def junction_op(p: F.FE) -> dict:
    """The operating point's intrinsic junction voltages of the first input JFET and its cascode."""
    keys = ("@j.xja1.j1[vgs]", "@j.xja1.j1[vgd]", "@j.xca1.j1[vgs]", "@j.xca1.j1[vgd]", "@j.xja1.j1[gm]")
    ctl = ".control\n" + spice.WR + "op\nprint " + " ".join(keys) + "\n.endc\n"
    f = spice.run(f"numbers_s4a/{p.name}_junctions", F.deck(p, f"junction voltages {p.name}", F.SRC_DM, ctl),
                  allow=(r"q\.xua",))
    return {k: spice.printed(f, k) for k in keys}


def outer_margins(fr: np.ndarray, t: np.ndarray) -> dict:
    """frontend.check_loop's convention, on an archived curve."""
    mag = np.abs(t)
    i = int(np.where(mag < 1)[0][0])
    ph = np.unwrap(np.angle(t))
    gm = float("nan")
    for j in range(i, len(fr) - 1):
        if ph[j] > -math.pi >= ph[j + 1] or ph[j] < -math.pi <= ph[j + 1]:
            gm = -20 * math.log10(mag[j])
            break
    pm = 180 + math.degrees(np.angle(t[i]))
    return dict(f_c=float(fr[i]), pm=float(pm if pm <= 180 else pm - 360), gm_db=gm)


def f_minus180(fr: np.ndarray, t: np.ndarray) -> list:
    """Frequencies where the unwrapped phase crosses -180 deg (mod 360) while |T| < 1, interpolated
    linearly in log f between the sweep points; with the sweep point past each crossing."""
    mag = np.abs(t)
    ph = np.degrees(np.unwrap(np.angle(t)))
    out = []
    for j in range(len(fr) - 1):
        for k in range(-3, 4):
            lvl = -180 + 360 * k
            if (ph[j] - lvl) * (ph[j + 1] - lvl) <= 0 and ph[j] != ph[j + 1] and mag[j + 1] < 1:
                x = (lvl - ph[j]) / (ph[j + 1] - ph[j])
                lf = math.log10(fr[j]) + x * (math.log10(fr[j + 1]) - math.log10(fr[j]))
                out.append(dict(f_interp=10 ** lf, f_sweep=float(fr[j + 1]),
                                gm_db_sweep=float(-20 * math.log10(mag[j + 1]))))
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    cn = load("chain_noise.json")
    fgo = load("fe_gain_options.json")
    fgd = load("fe_gain_derived.json")
    fcf = load("fe_closed_forms.json")
    sp = load("sink_power.json")
    osc = load("osc_check.json")
    sc = load("stability_corners.json")
    lvr = load("lv_option_range.json")
    lvo = load("lv_option.json")
    onc = load("opamp_noise_check.json")
    dab = load("da_compare_before_cnode.json")
    cac = load("chain_ac.json")
    cnz = np.load(R / "curves_noise.npz")
    clp = np.load(R / "curves_loop.npz")
    pH, pL = F.CASES["H100"], F.CASES["L200"]

    # ================= Section 4.1 =================
    s = "4.1 chain"
    put(s, "headroom of H_HR over H_LN, 20 log10(100/10)", 20 * math.log10(100 / 10), "dB", "arithmetic", "20")
    ratios = {}
    for g in (100, 1000):
        for f0 in ("1000.0", "100000.0"):
            ratios[f"gain {g}, {float(f0):g} Hz"] = cn[f"H_HR_{g}"]["en"][f0] / cn[f"H_LN_{g}"]["en"][f0]
    put(s, "noise ratio H_HR / H_LN at 1 kHz and 100 kHz, gains 100 and 1000", ratios, "",
        "chain_noise.json (Table 10)", f"{rnd(min(ratios.values()), 1)}-{rnd(max(ratios.values()), 1)}")

    # ================= operating points (Table 6) =================
    s = "Table 6"
    op = {c: F.check_op(F.CASES[c]) for c in ("H100", "L200")}
    jn = {c: junction_op(F.CASES[c]) for c in ("H100", "L200")}
    for c, p in (("H100", pH), ("L200", pL)):
        gm = op[c]["@j.xja1.j1[gm]"]
        put(s, f"{c}: g_m per JFET", gm * 1e3, "mS", "frontend.check_op, @j.xja1.j1[gm]", rnd(gm * 1e3, 1))
        put(s, f"{c}: N g_m per side (N = {p.n})", p.n * gm * 1e3, "mS", "N x g_m",
            rnd(p.n * gm * 1e3, 0))
    cards = {"H": FC.card("JFE2140_M", "jfets.lib"), "L": FC.card("JFE150_M", "jfets.lib")}
    casc = FC.card("LSBF862_M", "jfets.lib")
    for key, c, p in (("H", "H100", pH), ("L", "L200", pL)):
        ds = p.n * C_ISS[key]
        put(s, f"{c}: N C_iss, data sheet ({p.n} x {C_ISS[key] * 1e12:g} pF)", ds * 1e12, "pF",
            "SLPS730B p. 5 (JFE2140) / SLPS732B p. 5 (JFE150), C_iss at V_DS = 5 V", rnd(ds * 1e12, 0))
        cd = cards[key]
        vgs, vgd = jn[c]["@j.xja1.j1[vgs]"], jn[c]["@j.xja1.j1[vgd]"]
        cgs, cgd = cj(cd["CGS"], vgs, cd["PB"]), cj(cd["CGD"], vgd, cd["PB"])
        put(s, f"{c}: input JFET V_GS, V_GD (intrinsic)", [vgs, vgd], "V", "op deck, @j.xja1.j1[vgs], [vgd]")
        put(s, f"{c}: model C_gs + C_gd per JFET at the operating point", (cgs + cgd) * 1e12, "pF",
            "C0 / sqrt(1 - V / PB), card in _lib/jfets.lib", rnd((cgs + cgd) * 1e12, 2))
        put(s, f"{c}: N (C_gs + C_gd), model at the operating point", p.n * (cgs + cgd) * 1e12, "pF",
            "N x the above", rnd(p.n * (cgs + cgd) * 1e12, 0))
    for c, p, spk in (("H100", pH, "H100 | 2 V"), ("L200", pL, "L200 | 6 V")):
        r_up = (p.vp - (0.6 + p.vbs)) / p.i_bs
        i_bs = (p.vp - op[c]["v(ba)"]) / r_up
        i_c = p.n * op[c]["@j.xja1.j1[id]"] + i_bs
        i_t = sp[spk]["op"]["i_sink"]
        put(s, f"{c}: source-node current N I_D + I_BS", i_c * 1e3, "mA",
            "check_op: N @j.xja1.j1[id] + (V_P - v(ba)) / R_UP", rnd(i_c * 1e3, 1))
        put(s, f"{c}: R_T current I_T (base current included)", i_t * 1e3, "mA",
            f"sink_power.json, {spk}, i_sink", rnd(i_t * 1e3, 1))
        put(s, f"{c}: sink base current I_T - I_C", (i_t - i_c) * 1e3, "mA", "difference", rnd((i_t - i_c) * 1e3, 2))

    # ================= Section 4.2: servo =================
    s = "4.2 servo"
    for c, p, i_nom in (("H", pH, 11e-3), ("L", pL, 61e-3)):
        for eps in (0.01, 0.03):
            dv = eps * i_nom * p.rf
            put(s, f"{c}: output error, {eps:.0%} of {i_nom * 1e3:g} mA x R_F {p.rf:g} ohm", dv * 1e3, "mV",
                "eps (N I_D + I_BS) R_F", rnd(dv * 1e3, 0) if eps == 0.01 else rnd(dv, 2) + " V")
    d = fcf["drift"]["H100, 2 V"]
    dvbe = d["dVBE_dT_mV"]
    put(s, "H: dV_BE/dT of the MMBT3904 sink", dvbe, "mV/K", "fe_closed_forms.json, drift, H100, 2 V",
        rnd(dvbe, 1))
    put(s, "H: dI/I per kelvin = |dV_BE/dT| / V_RT (2 V)", abs(dvbe) / 2000 * 100, "%/K", "arithmetic",
        rnd(abs(dvbe) / 2000 * 100, 2))
    di = abs(dvbe) * 1e-3 / d["R_T"]
    put(s, "H: dI/dT = |dV_BE/dT| / R_T", di * 1e6, "uA/K", "arithmetic", rnd(di * 1e6, 1))
    put(s, "H: R_F dI/dT (closed form)", di * pH.rf * 1e3, "mV/K", "arithmetic", rnd(di * pH.rf * 1e3, 1))
    put(s, "H: output drift per kelvin, simulated", d["output_mV_per_K"], "mV/K",
        "fe_closed_forms.json, drift, H100, 2 V, output_mV_per_K", rnd(d["output_mV_per_K"], 1))
    dl = fcf["drift"]["L, 6 V"]
    put(s, "L (6 V): output drift per kelvin, simulated", dl["output_mV_per_K"], "mV/K",
        "fe_closed_forms.json, drift, L, 6 V, output_mV_per_K", rnd(dl["output_mV_per_K"], 1))
    m = 0.0005
    di_m = m * 11e-3
    put(s, "H: sink mismatch, an assumed 0.05 % of 11 mA", di_m * 1e6, "uA", "assumption x design current",
        rnd(di_m * 1e6, 1))
    put(s, "H: differential output offset dI R_F", di_m * pH.rf * 1e3, "mV", "arithmetic", rnd(di_m * pH.rf * 1e3, 2))
    put(s, "H: referred to the input, dI R_F / G", di_m * pH.rf / pH.gain * 1e6, "uV", "G = 1 + 2 R_F / R_G",
        rnd(di_m * pH.rf / pH.gain * 1e6, 1))
    f_int = 1e-6 / (2 * math.pi * 1e-6)
    f_filt = 1 / (2 * math.pi * 1e3 * 10e-6)
    put(s, "integrator unity-gain frequency g / (2 pi C)", f_int, "Hz", "1 uS, 1 uF (frontend.netlist)", rnd(f_int, 2))
    put(s, "filter corner 1 / (2 pi R C)", f_filt, "Hz", "1 kohm, 10 uF (frontend.netlist)", rnd(f_filt, 0))
    for c, p, spk in (("H", pH, "H100 | 2 V"), ("L", pL, "L200 | 6 V")):
        r_t = p.v_sink / (p.n * p.id + p.i_bs)
        ratio = p.rf / r_t
        fc_ = ratio * f_int
        lag = math.degrees(math.atan(fc_ / f_filt))
        put(s, f"{c}: R_T = V_RT / (N I_D + I_BS)", r_t, "ohm", "frontend.side", rnd(r_t, 1))
        put(s, f"{c}: R_F / R_T", ratio, "V/V", "arithmetic", rnd(ratio, 2))
        put(s, f"{c}: servo crossover (R_F / R_T) f_int", fc_, "Hz", "arithmetic", rnd(fc_, 2))
        put(s, f"{c}: filter's phase lag at the crossover", lag, "deg", "atan(f_c / f_filt)", rnd(lag, 1))
        put(s, f"{c}: servo phase margin 90 - lag", 90 - lag, "deg", "arithmetic", rnd(90 - lag, 0))
        lo, hi = p.vm + 1, p.vm + p.v_sink + 3
        put(s, f"{c}: servo clamp V_M + 1 V ... V_M + V_RT + 3 V", [lo, hi], "V", "frontend.netlist, BSNK",
            f"V_M + 1 V ... V_M + {p.v_sink + 3:g} V")
        vb = sp[spk]["op"]["v_ctrl"]
        put(s, f"{c}: sink base (vsink) at the operating point, relative to V_M", vb - p.vm, "V",
            f"sink_power.json, {spk}, v_ctrl", rnd(vb - p.vm, 1))
    i100k = math.sqrt(4 * K * T / 100e3)
    put(s, "noise current of 100 kohm, sqrt(4kT / R)", i100k * 1e12, "pA/rtHz", "arithmetic", rnd(i100k * 1e12, 1))

    # ================= Section 4.2: what the servo sets, and the latch (servo_check.py) =================
    s = "4.2 servo check"
    svc = load("servo_check.json")
    hr = fcf["headroom"]
    cm_range = {"H": (hr["V_CM_min H (2 V)"], hr["H100"]["V_CM_max"]), "L": (hr["V_CM_min L (6 V)"], hr["L200"]["V_CM_max"])}
    for c, case, p in (("H", "H100", pH), ("L", "L200", pL)):
        r = svc["role"][case]
        sv, de = r["servo"], r["design"]
        put(s, f"{c}: outputs - sources with the servo (largest of every servo case)",
            max(abs(r[k]["cm_offset"]) for k in r if k.startswith("servo")) * 1e6, "uV",
            "servo_check.json role, servo*: cm_offset", rnd(max(abs(r[k]["cm_offset"]) for k in r if k.startswith("servo")) * 1e6, 0))
        put(s, f"{c}: signal path, servo against the reference fixed at its value (f3dB, noise: largest rel. diff.)",
            [r["signal_path"]["rel_diff_f3db"], r["signal_path"]["max_rel_diff_en"]], "-", "servo_check.json signal_path",
            f"{r['signal_path']['rel_diff_f3db']:.0e}, {r['signal_path']['max_rel_diff_en']:.0e}")
        put(s, f"{c}: the servo's settled reference / the design value V_M + V_RT + 0.66 V", [sv["v_ref"], de["v_ref"]], "V",
            "servo_check.json servo, design: v_ref", f"{rnd(sv['v_ref'], 2)} / {rnd(de['v_ref'], 2)}")
        i_b, i_c = sv["i_base"], sv["i_sink"][0]
        i_e = i_c + i_b
        r_t = p.v_sink / (p.n * p.id + p.i_bs)
        v_be = sv["v_base"] - sv["v_emitter"]
        parts = dict(base_current_in_1k=2 * i_b * 1e3, v_be_minus_0p66=v_be - 0.66, emitter_current_excess=(i_e - p.v_sink / r_t) * r_t)
        put(s, f"{c}: settled - design reference: 2 I_B x 1 kohm, V_BE - 0.66 V, (I_E - V_RT/R_T) R_T", parts, "V",
            "servo_check.json servo: i_base, v_base - v_emitter, i_sink + i_base",
            ", ".join(rnd(x, 2) for x in parts.values()) + f" (sum {rnd(sum(parts.values()), 2)} V)")
        put(s, f"{c}: beta = I_C / I_B at the operating point", i_c / i_b, "-", "servo_check.json servo", rnd(i_c / i_b, 0))
        put(s, f"{c}: outputs - sources with the reference at the design value", de["cm_offset"], "V",
            "servo_check.json design: cm_offset", rnd(de["cm_offset"], 2))
        sn = r["sens"]
        put(s, f"{c}: outputs per 20 mV of reference (or of V_BE)", sn["per_mV_ref"] * 20 * 1e3, "mV",
            "servo_check.json sens.per_mV_ref x 20 mV", rnd(sn["per_mV_ref"] * 20 * 1e3, 0))
        put(s, f"{c}: outputs per kelvin, reference fixed / with the servo", [sn["per_K_fixed"] * 1e3, sn["per_K_servo"] * 1e3],
            "mV/K", "servo_check.json sens (27 -> 52 C)", f"{rnd(sn['per_K_fixed'] * 1e3, 1)} / {sn['per_K_servo'] * 1e3:.1e}")
        put(s, f"{c}: outputs over +25 K, reference fixed", r["fixed_52C"]["cm_offset"] - r["fixed"]["cm_offset"], "V",
            "servo_check.json fixed_52C - fixed", rnd(r["fixed_52C"]["cm_offset"] - r["fixed"]["cm_offset"], 2))
        put(s, f"{c}: base current change over +25 K (beta rises), x 2 x 1 kohm",
            2 * (r["fixed_52C"]["i_base"] - r["fixed"]["i_base"]) * 1e3, "V", "servo_check.json fixed_52C, fixed: i_base",
            rnd(2 * (r["fixed_52C"]["i_base"] - r["fixed"]["i_base"]) * 1e3, 3))
        put(s, f"{c}: outputs per volt of input common mode, reference fixed / with the servo",
            [sn["per_V_cm_fixed"] * 1e3, sn["per_V_cm_servo"] * 1e3], "mV/V", "servo_check.json sens (-8 V, +3 V)",
            f"{rnd(sn['per_V_cm_fixed'] * 1e3, 0)} / {sn['per_V_cm_servo'] * 1e3:.1e}")
        lo, hi = cm_range[c]
        put(s, f"{c}: over the input common-mode range {rnd(lo, 1)} ... {rnd(hi, 1)} V, reference fixed",
            sn["per_V_cm_fixed"] * (hi - lo), "V", "per_V_cm_fixed x range (fe_closed_forms.json headroom)",
            rnd(sn["per_V_cm_fixed"] * (hi - lo), 2))
        dvc = VCM_HI - VCM_LO
        put(s, f"{c}: R_UP's current per volt of input common mode", sn["i_up_per_V_cm"] * 1e6, "uA/V",
            "servo_check.json sens.i_up_per_V_cm (-1 / (R_UP + R_BS))", rnd(sn["i_up_per_V_cm"] * 1e6, 0))
        di_s = (r[f"fixed_cm_{VCM_HI:+g}V"]["i_sink"][0] - r[f"fixed_cm_{VCM_LO:+g}V"]["i_sink"][0]) / dvc
        put(s, f"{c}: a fixed sink's own current per volt of collector voltage (Early effect)", di_s * 1e6, "uA/V",
            "servo_check.json fixed_cm_*: i_sink", rnd(di_s * 1e6, 0))
        # the latch: the servo loop opened (sweep) and closed
        sw, cl = svc["latch"][case]["sweep"], svc["latch"][case]["closed"]
        put(s, f"{c}: zeros of e(reference), loop opened: reference, slope", [[z["v_ref"], z["slope"]] for z in sw["zeros"]],
            "V, V/V", "servo_check.json latch.sweep.zeros", "; ".join(f"{rnd(z['v_ref'], 2)} V, {rnd(z['slope'], 2)}" for z in sw["zeros"]))
        put(s, f"{c}: e at the design clamp's limits and at +-14 V", [sw["e_at_design_lo"], sw["e_at_design_hi"], sw["e_at_rail_lo"],
            sw["e_at_rail_hi"]], "V", "servo_check.json latch.sweep",
            f"{rnd(sw['e_at_design_lo'], 1)} / {rnd(sw['e_at_design_hi'], 2)}; {rnd(sw['e_at_rail_lo'], 1)} / {rnd(sw['e_at_rail_hi'], 1)}")
        put(s, f"{c}: e above the zero (min) and below it (max)", [sw["e_min_above_zero"], sw["e_max_below_zero"]], "V",
            "servo_check.json latch.sweep", f"{sw['e_min_above_zero']:.1e} / {sw['e_max_below_zero']:.1e}")
        put(s, f"{c}: saturation (V_BC > 0.5 V) from a reference of", sw["saturation_onset_v_ref"], "V",
            "servo_check.json latch.sweep", rnd(sw["saturation_onset_v_ref"], 1))
        put(s, f"{c}: sink emitter current and R_T's dissipation: nominal / design clamp top / +14 V",
            [sw["i_sink_nominal"], sw["i_emitter_at_design_hi"], sw["i_emitter_at_rail_hi"], sw["p_rt_nominal"],
             sw["p_rt_at_design_hi"], sw["p_rt_at_rail_hi"]], "A, W", "servo_check.json latch.sweep",
            f"{rnd(sw['i_sink_nominal'] * 1e3, 0)} / {rnd(sw['i_emitter_at_design_hi'] * 1e3, 0)} / {rnd(sw['i_emitter_at_rail_hi'] * 1e3, 0)} mA; "
            f"{rnd(sw['p_rt_nominal'] * 1e3, 0)} / {rnd(sw['p_rt_at_design_hi'] * 1e3, 0)} / {rnd(sw['p_rt_at_rail_hi'] * 1e3, 0)} mW")
        cls = {k: x for k, x in cl.items() if isinstance(x, dict)}
        put(s, f"{c}: closed loop from no .nodeset and from the bases at +14 V (design clamp, +-14 V): same state, no fallback",
            all(abs(x["v_base"] - cls["design_clamp"]["v_base"]) < 1e-6 and not x["fallback"] for x in cls.values()), "-",
            "servo_check.json latch.closed", str(all(abs(x["v_base"] - cls["design_clamp"]["v_base"]) < 1e-6 and not x["fallback"]
                                                       for x in cls.values())))

    # ================= Section 4.2: bootstrap and cascode =================
    s = "4.2 cascode"
    r_bs = pH.vbs / pH.i_bs
    f_bs = 1 / (2 * math.pi * r_bs * pH.c_bs)
    put(s, "bootstrap corner 1 / (2 pi R_BS C_BS)", f_bs, "Hz", "R_BS 3.5 kohm, C_BS 1 uF (frontend.side)",
        rnd(f_bs, 0))
    q = replace(pH, name="H100_cascode_MMBTH10", cascode="MMBTH10")
    keys = ("@qca1[ib]", "@qca1[ic]", "v(sa)", "v(da1)")
    ctl = ".control\n" + spice.WR + "op\nprint " + " ".join(keys) + "\n.endc\n"
    fo = spice.run(f"numbers_s4a/{q.name}_op", F.deck(q, f"op {q.name}", F.SRC_DM, ctl), allow=(r"q\.xua",))
    npn = {k: spice.printed(fo, k) for k in keys}
    put(s, "MMBTH10 cascode: base current at the operating point", npn["@qca1[ib]"] * 1e6, "uA",
        "op deck, @qca1[ib]", rnd(npn["@qca1[ib]"] * 1e6, 0))
    put(s, "MMBTH10 cascode: collector current", npn["@qca1[ic]"] * 1e3, "mA", "op deck, @qca1[ic]",
        rnd(npn["@qca1[ic]"] * 1e3, 2))
    put(s, "MMBTH10 cascode: input JFETs' V_DS", npn["v(da1)"] - npn["v(sa)"], "V", "v(da1) - v(sa)",
        rnd(npn["v(da1)"] - npn["v(sa)"], 1))
    ac = F.check_ac(q)
    nz, gain, how = GO.noise_checked(q, ac)
    fr = nz["f"]
    grp = F.noise_groups(nz["nz"], gain)
    ib2 = np.zeros_like(fr)
    for name, v in nz["nz"].items():
        if name.startswith("onoise_qc") and name.endswith("_ib"):
            ib2 = ib2 + v ** 2
    e_casc = spice.at(fr, grp["cascodes"], 1e4)
    e_ib = spice.at(fr, np.sqrt(ib2) / gain, 1e4)
    put(s, "MMBTH10 cascodes: input-referred noise at 10 kHz (group 'cascodes')", e_casc * 1e9, "nV/rtHz",
        f"run here (noise run: {how})", rnd(e_casc * 1e9, 2))
    put(s, "MMBTH10 cascodes: of which base-current shot noise (onoise_qc*_ib)", e_ib * 1e9, "nV/rtHz",
        "run here", rnd(e_ib * 1e9, 2))
    put(s, "MMBTH10 cascodes: front end's total at 10 kHz", spice.at(fr, nz["inn"], 1e4) * 1e9, "nV/rtHz",
        "run here", rnd(spice.at(fr, nz["inn"], 1e4) * 1e9, 2))
    put(s, "MMBTH10 cascodes: front end's -3 dB bandwidth", ac["f3db"] / 1e6, "MHz", "run here",
        rnd(ac["f3db"] / 1e6, 1))
    put(s, "LSBF862 cascodes (adopted): group 'cascodes' at 10 kHz",
        fgo["H, gain 100 (adopted)"]["groups"]["cascodes"]["10000"], "nV/rtHz", "fe_gain_options.json",
        rnd(fgo["H, gain 100 (adopted)"]["groups"]["cascodes"]["10000"], 3))

    # ================= Section 4.2: noise, Eq. (9) =================
    s = "4.2 noise"
    a = fgo["H, gain 100 (adopted)"]["groups"]
    for g, lab in (("input JFETs", "JFETs"), ("R_G", "R_G"), ("drain-side R_D", "R_D"),
                   ("loop op amps", "op amps"), ("current sinks", "sinks")):
        put(s, f"H100: {lab} at 10 kHz", a[g]["10000"], "nV/rtHz", "fe_gain_options.json (Table 7c)",
            rnd(a[g]["10000"], 2))
    fL = cnz["L200_f"]
    for g, lab in (("input JFETs", "JFETs"), ("R_G", "R_G")):
        v = spice.at(fL, cnz[f"L200_g_{g}"], 1e4) * 1e9
        put(s, f"L200: {lab} at 10 kHz", v, "nV/rtHz", "curves_noise.npz", rnd(v, 2))
    put(s, "Spinelli and Haberman: R_B / G_n", SPINELLI["r_b"] / SPINELLI["g_n"], "ohm", "p. 5, arithmetic",
        rnd(SPINELLI["r_b"] / SPINELLI["g_n"], 2))
    put(s, "Spinelli and Haberman: 1 / g_m", 1 / SPINELLI["g_m"], "ohm", "p. 5, arithmetic",
        rnd(1 / SPINELLI["g_m"], 0))

    # ================= Section 4.2.1 =================
    s = "4.2.1 sinks"
    put(s, "V_CE(sat) max, 10 mA / 50 mA (data sheets)", [V_CE_SAT["10 mA"], V_CE_SAT["50 mA"]], "V",
        "MMBT3904LT1/D Rev. 15 p. 2; PZT3904T1/D Rev. 7 p. 2", "0.2 / 0.3")
    put(s, "V_CE,min (design margin)", 0.5, "V", "design choice (sink_options.V_SAT_BJT)", "0.5")

    # ================= Section 4.3 =================
    s = "4.3 loops"
    gm_side = 2 * op["H100"]["@j.xja1.j1[gm]"]
    k = gm_side * pH.rg / (2 + gm_side * pH.rg)
    put(s, "H100: k_DM = g_m R_G / (2 + g_m R_G)", k, "", "g_m of one side from the operating point", rnd(k, 2))
    put(s, "H100: 1 / k_DM", 1 / k, "", "arithmetic", rnd(1 / k, 1))
    cpar = {}
    for c, p in (("H100", pH), ("L200", pL)):
        vgd = jn[c]["@j.xca1.j1[vgd]"]
        cgd = cj(casc["CGD"], vgd, casc["PB"])
        cpar[c] = p.n * cgd + THS4021["c_i"]
        put(s, f"{c}: cascode V_GD (intrinsic)", vgd, "V", "op deck, @j.xca1.j1[vgd]", rnd(vgd, 1))
        put(s, f"{c}: cascode C_gd at its bias", cgd * 1e12, "pF",
            f"LSBF862 card CGD {casc['CGD'] * 1e12:.4g} pF, PB {casc['PB']:g} V", rnd(cgd * 1e12, 1))
        put(s, f"{c}: C_par = N C_gd + C_i(THS4021 1.5 pF)", cpar[c] * 1e12, "pF", "arithmetic; SLOS265F p. 7",
            rnd(cpar[c] * 1e12, 1))
        for tag, ci, cx, cn in (("first", FIRST[c]["ci"], FIRST[c]["cx"], 0.0), ("final", p.ci, p.cx, p.cnode)):
            ssum, dd = ci + cx, ci - cx
            tot = ssum + cn + cpar[c]
            put(s, f"{c} {tag}: beta_CM = S / (S + C_node + C_par)", ssum / tot, "",
                f"S {ssum * 1e12:.4g} pF, C_node {cn * 1e12:g} pF", rnd(ssum / tot, 3 if tag == "final" else 2))
            put(s, f"{c} {tag}: beta_DM = D / (S + C_node + C_par)", dd / tot, "",
                f"D {dd * 1e12:.4g} pF", rnd(dd / tot, 3))
            put(s, f"{c} {tag}: S + C_node + C_par", tot * 1e12, "pF", "arithmetic", rnd(tot * 1e12, 0))
    b_dm = (pH.ci - pH.cx) / (pH.ci + pH.cx + pH.cnode + cpar["H100"])
    f_loc = THS4021["gbw"] * b_dm
    put(s, "H100 final: f_local,DM = GBW beta_DM", f_loc / 1e6, "MHz", "GBW 2 GHz (SLOS265F p. 1)", rnd(f_loc / 1e6, 0))
    f10b = THS4021["gbw"] * k / THS4021["g_min"]
    put(s, "Eq. (10b): GBW k_DM / 10", f10b / 1e6, "MHz", "GBW 2 GHz, stable at gains >= 10 (SLOS265F p. 1)",
        rnd(f10b / 1e6, 0))
    put(s, "H100 adopted: D / S", (pH.ci - pH.cx) / (pH.ci + pH.cx), "", "4 pF / 14 pF",
        rnd((pH.ci - pH.cx) / (pH.ci + pH.cx), 2))
    # loop margins from the archived curves (Table 7, Figure 12)
    lp = {}
    for case in ("H100", "L200", "H100_nocross", "H100_old"):
        for mode in ("dm", "cm"):
            om = outer_margins(clp[f"outer_{case}_{mode}_f"], clp[f"outer_{case}_{mode}_T"])
            lp[f"outer {case} {mode}"] = om
            put(s, f"outer loop {case} {mode}: f_c, PM, GM", [om["f_c"] / 1e6, om["pm"], om["gm_db"]],
                "MHz, deg, dB", "curves_loop.npz, check_loop convention",
                f"{rnd(om['f_c'] / 1e6, 1)} MHz, {rnd(om['pm'], 0)} deg, {gm_txt(om['gm_db'], 0)}")
    for case in ("H100", "H10", "L200", "H100_old"):
        for mode in ("dm", "cm"):
            fr_, t_ = clp[f"out_{case}_{mode}_f"], clp[f"out_{case}_{mode}_T"]
            mg = F._margins(fr_, t_)
            x = min(mg["crossings"], key=lambda c_: c_["pm"])
            put(s, f"complete loop {case} {mode}: f_c, PM, GM", [x["f"] / 1e6, x["pm"], mg["gm_db"]],
                "MHz, deg, dB", "curves_loop.npz, frontend._margins",
                f"{rnd(x['f'] / 1e6, 1)} MHz, {rnd(x['pm'], 0)} deg, {gm_txt(mg['gm_db'], 1)}")
            for c180 in f_minus180(fr_, t_):
                put(s, f"complete loop {case} {mode}: -180 deg crossing (interpolated / sweep point)",
                    [c180["f_interp"] / 1e6, c180["f_sweep"] / 1e6, c180["gm_db_sweep"]], "MHz, MHz, dB",
                    "curves_loop.npz", f"{rnd(c180['f_interp'] / 1e6, 0)} MHz")
    x = min(F._margins(clp["outer_H100_nocross_cm_f"], clp["outer_H100_nocross_cm_T"])["crossings"],
            key=lambda c_: c_["pm"])
    put(s, "Figure 12 (a, d): CM outer loop without C_X, f_c and PM (frontend._margins)", [x["f"] / 1e6, x["pm"]],
        "MHz, deg", "curves_loop.npz (make_figures.fig_loop_gain)", f"{rnd(x['f'] / 1e6, 0)} MHz, {rnd(x['pm'], 0)} deg")
    # oscillation
    for key in ("H100_first", "H100_first_ties", "L200_first"):
        e = osc[key]
        put(s, f"oscillation {key}: cm_out pk-pk, frequency", [e["cm_out"]["pkpk"], e["cm_out"]["f_dom"] / 1e6],
            "V, MHz", f"osc_check.json ({e['bench']})", f"{rnd(e['cm_out']['pkpk'], 2)} V, {rnd(e['cm_out']['f_dom'] / 1e6, 0)} MHz")
    e = osc["H100_cnode220p"]
    put(s, "final values H100: output pk-pk", max(e["v(oa)"]["pkpk"], e["v(ob)"]["pkpk"]) * 1e6, "uV",
        "osc_check.json, H100_cnode220p", rnd(max(e["v(oa)"]["pkpk"], e["v(ob)"]["pkpk"]) * 1e6, 2))
    put(s, "final values H100: outputs' common mode, window mean minus start", e["cm_out"]["window_mean_minus_start"] * 1e3,
        "mV", "osc_check.json, H100_cnode220p cm_out.window_mean_minus_start",
        rnd(e["cm_out"]["window_mean_minus_start"] * 1e3, 2))
    e = osc["L200_cnode470p"]
    put(s, "final values L200: output pk-pk, and the run used", [max(e["v(oa)"]["pkpk"], e["v(ob)"]["pkpk"]) * 1e6,
                                                                 e.get("integration", "Gear")],
        "uV", "osc_check.json, L200_cnode470p", rnd(max(e["v(oa)"]["pkpk"], e["v(ob)"]["pkpk"]) * 1e6, 2))
    # bandwidth and noise
    put(s, "chain at total gain 100, first front end, LM7171 in S2: -3 dB", dab["LM7171"]["ac_H100"]["f3db"] / 1e6,
        "MHz", "da_compare_before_cnode.json", rnd(dab["LM7171"]["ac_H100"]["f3db"] / 1e6, 1))
    put(s, "chain at total gain 100, final front end: -3 dB", cac["H_LN_100"]["f3db"] / 1e6, "MHz",
        "chain_ac.json, H_LN_100", rnd(cac["H_LN_100"]["f3db"] / 1e6, 1))
    put(s, "chain bandwidth ratio final / first", cac["H_LN_100"]["f3db"] / dab["LM7171"]["ac_H100"]["f3db"], "",
        "arithmetic", rnd(cac["H_LN_100"]["f3db"] / dab["LM7171"]["ac_H100"]["f3db"], 2))
    for lab, v in (("H100", fgo["H, gain 100 (adopted)"]["f3db"]), ("H10", fgo["H, gain 10 (range)"]["f3db"]),
                   ("L200 (6 V sinks)", sp["L200 | 6 V"]["f3db"])):
        put(s, f"front end alone, {lab}: -3 dB", v / 1e6, "MHz", "fe_gain_options.json / sink_power.json",
            rnd(v / 1e6, 0))
    for lab, d_ in (("H100", fgo["H, gain 100 (adopted)"]["en"]), ("L200 (6 V sinks)", sp["L200 | 6 V"]["en"])):
        put(s, f"{lab}: noise at 10 kHz and 10 MHz", [d_["10000.0"], d_["10000000.0"]], "nV/rtHz",
            "fe_gain_options.json / sink_power.json", f"{rnd(d_['10000.0'], 2)} / {rnd(d_['10000000.0'], 2)}")
    nsets = sum(len(load(f"comp_search_{c}.json")) for c in ("H100", "L200", "H10"))
    put(s, "comp_search sets (H100, L200, H10)", nsets, "", "comp_search_*.json", str(nsets))

    # ================= Section 4.3.1 =================
    s = "4.3.1 mitigations"
    for key, v in sc.items():
        put(s, f"Table 7a: {key}", {m_: [v[m_]["pm"], v[m_]["gm_db"], v[m_]["modulus"]] for m_ in ("dm", "cm")},
            "deg, dB, -", "stability_corners.json",
            " | ".join(f"{rnd(v[m_]['pm'], 0)} deg, {rnd(v[m_]['gm_db'], 1)} dB, {rnd(v[m_]['modulus'], 2)}"
                       for m_ in ("dm", "cm")))
    for c, m_ in (("H100", "cm"), ("L200", "cm")):
        put(s, f"{c} {m_}: frequency of the smallest |1 + T|", sc[f"{c} | nominal"][m_]["f_modulus"] / 1e6, "MHz",
            "stability_corners.json, f_modulus", rnd(sc[f"{c} | nominal"][m_]["f_modulus"] / 1e6, -1))
    put(s, "modulus margin 0.5 as a sensitivity peak, 20 log10(1/0.5)", 20 * math.log10(2), "dB", "arithmetic", "6")
    for c, cn0, vals in (("H", 220.0, (270.0, 330.0)), ("L", 470.0, (560.0, 680.0))):
        put(s, f"{c}: E12 values / simulated C_node", [vals[0] / cn0, vals[1] / cn0], "", "arithmetic",
            f"{rnd(vals[0] / cn0, 2)}-{rnd(vals[1] / cn0, 2)}")
        put(s, f"{c}: 1.3 and 1.5 x C_node", [1.3 * cn0, 1.5 * cn0], "pF", "arithmetic",
            f"{rnd(1.3 * cn0, 0)}-{rnd(1.5 * cn0, 0)}")
    for c, key in (("H100", "S14_D4_CN330"), ("L200", "S30_D14_CN680")):
        e = load(f"comp_search_{c}.json")[key]
        put(s, f"comp_search {c} {key}: DM PM, GM; CM PM, GM; f3db",
            [e["dm"]["pm"], e["dm"]["gm_db"], e["cm"]["pm"], e["cm"]["gm_db"], e["f3db"] / 1e6],
            "deg, dB, deg, dB, MHz", f"comp_search_{c}.json",
            f"{rnd(e['dm']['pm'], 0)} deg, {rnd(e['dm']['gm_db'], 0)} dB | {rnd(e['cm']['pm'], 0)} deg, "
            f"{rnd(e['cm']['gm_db'], 1)} dB | {rnd(e['f3db'] / 1e6, 0)} MHz")
    g20 = fgo["R_G route, gain 20, D 8.33 pF"]
    put(s, "R_G route gain 20: noise at 10 Hz / 10 kHz / 10 MHz", [g20["en"]["10"], g20["en"]["10000.0"],
        g20["en"]["10000000.0"]], "nV/rtHz", "fe_gain_options.json",
        f"{rnd(g20['en']['10'], 2)} / {rnd(g20['en']['10000.0'], 2)} / {rnd(g20['en']['10000000.0'], 2)}")
    rise = fgd["white rise, gain 20 and 30"]
    put(s, "white rise, gains 20 and 30 (R_G route)", rise, "", "fe_gain_derived.json",
        f"+{rnd(rise[0] * 100, 0)} % / +{rnd(rise[1] * 100, 0)} %")
    for lab, gk, f0 in (("Table 7c: R_G, gain 100", "H, gain 100 (adopted)", "R_G"),
                        ("Table 7c: loop op amps, gain 20 (R_G)", "R_G route, gain 20, D 8.33 pF", "loop op amps"),
                        ("Table 7c: R_F, gain 10", "H, gain 10 (range)", "R_F")):
        v = fgo[gk]["groups"][f0]["10000"]
        put(s, lab, v, "nV/rtHz", "fe_gain_options.json, 10 kHz", rnd(v, 2))
    put(s, "R_F route gain 20 against adopted: -3 dB", [fgo["R_F route, gain 20, all capacitors x5.21"]["f3db"] / 1e6,
        fgo["H, gain 100 (adopted)"]["f3db"] / 1e6], "MHz", "fe_gain_options.json",
        f"{rnd(fgo['R_F route, gain 20, all capacitors x5.21']['f3db'] / 1e6, 0)} / "
        f"{rnd(fgo['H, gain 100 (adopted)']['f3db'] / 1e6, 0)}")
    rf20 = fgo["R_F route, gain 20, all capacitors x5.21"]["rf"]
    put(s, "output current V_o / R_F at V_o = 12 V, R_F route gain 20", THS4021["v_o_min"] / rf20 * 1e3, "mA",
        "V_O >= +-12 V into 250 ohm, I_O >= 80 mA (SLOS265F p. 7)", rnd(THS4021["v_o_min"] / rf20 * 1e3, 0))
    # unity-gain-stable op amps on +-15 V
    f_ths4031 = THS4031_FU * k * 1.0
    f_lm_a = LM7171["f_u_a"] * k / LM7171["g_min"]
    f_lm_b = LM7171["f_u_b"] * k / LM7171["g_min"]
    put(s, "THS4031: f_u k_DM x 1", f_ths4031 / 1e6, "MHz", "120 MHz (SLOS224L p. 1)", rnd(f_ths4031 / 1e6, 0))
    put(s, "LM7171A: f_u k_DM x 0.5", f_lm_a / 1e6, "MHz", "160 MHz (SNOS760D p. 5), gains >= +2 (p. 1)",
        rnd(f_lm_a / 1e6, 0))
    put(s, "LM7171B: f_u k_DM x 0.5", f_lm_b / 1e6, "MHz", "200 MHz (SNOS760D p. 5)", rnd(f_lm_b / 1e6, 0))
    f_out = lp["outer H100 dm"]["f_c"]
    put(s, "adopted ratio f_local,DM / f_c,DM,outer", f_loc / f_out, "", "arithmetic", rnd(f_loc / f_out, 1))
    outs = [f_out * f_new / f_loc / 1e6 for f_new in (f_lm_a, f_ths4031)]
    put(s, "outer DM crossover scaled to the LM7171A and THS4031 bounds", outs, "MHz", "estimate (adopted ratio)",
        f"{rnd(outs[0], 0)}-{rnd(outs[1], 0)}")
    # the low-voltage option
    lv = lvr["low-voltage (ADA4899, +/-5 V, V_ref 3 V, V_BS 1.2 V)"]
    ad = lvr["adopted (THS4021, +/-15 V, V_ref 9 V, V_BS 3.5 V)"]
    put(s, "LV: ADA4899 model swing into R_F (V_OH, V_OL)", [lv["swing"]["v_oh"], lv["swing"]["v_ol"]], "V",
        "lv_option_range.json, swing", f"+-{rnd(lv['swing']['v_oh'], 2)}")
    put(s, "LV: outputs above V_CM (V_GS1)", lv["stack"]["V_O_minus_V_CM"], "V", "lv_option_range.json",
        rnd(lv["stack"]["V_O_minus_V_CM"], 2))
    vod = 2 * (lv["swing"]["v_oh"] - lv["stack"]["V_GS1"])
    put(s, "LV: largest differential output at V_CM = 0, 2 (V_OH - V_GS1)", vod, "V",
        "lv_option_range.json (V_od_max_at_V_CM_0)", rnd(vod, 1))
    for row in lv["ranges"]:
        put(s, f"LV: CM range at V_od = {row['V_od']:g} V (1 V cascode margin; cascode at saturation)",
            [row["range_1V"][0], row["range_1V"][1], row["range"][1]], "V", "lv_option_range.json",
            "empty" if row["empty"] else f"{rnd(row['range_1V'][0], 1)} ... +{rnd(row['range_1V'][1], 2)} "
                                         f"(+{rnd(row['range'][1], 2)})")
    for row in ad["ranges"]:
        put(s, f"adopted: CM range at V_od = {row['V_od']:g} V (1 V cascode margin)", row["range_1V"], "V",
            "lv_option_range.json", f"{rnd(row['range_1V'][0], 1)} ... +{rnd(row['range_1V'][1], 1)}")
    ir = lvr["ADA4899 input common-mode range, +/-5 V"]
    put(s, "LV: ADA4899 model input common-mode range on +-5 V", [ir["v_in_min"], ir["v_in_max"]], "V",
        "lv_option_range.json", f"+-{rnd(ir['v_in_max'], 2)}")
    put(s, "LV: V_DS of the input JFETs and of the cascodes", [lv["stack"]["V_DS1"], lv["stack"]["V_DS2"]], "V",
        "lv_option_range.json", f"{rnd(lv['stack']['V_DS1'], 2)} / {rnd(lv['stack']['V_DS2'], 1)}")
    cr = onc["ADA4899 corrected for R_d"]
    put(s, "ADA4899 model corrected for its 4 kohm input resistor: e_n, i_n white",
        [cr["e_n_white_nV"], cr["i_n_white_pA"]], "nV/rtHz, pA/rtHz", "opamp_noise_check.json",
        f"{rnd(cr['e_n_white_nV'], 1)} / {rnd(cr['i_n_white_pA'], 1)}")
    put(s, "ADA4899 corrected at 10 Hz: e_n, i_n", [cr["e_n_10Hz_nV"], cr["i_n_10Hz_pA"]], "nV/rtHz, pA/rtHz",
        "opamp_noise_check.json", f"{rnd(cr['e_n_10Hz_nV'], 0)} / {rnd(cr['i_n_10Hz_pA'], 0)}")
    i21 = onc["THS4021"]["noise"]["10"]["i_n"] * 1e12
    put(s, "THS4021 (corrected model) i_n at 10 Hz", i21, "pA/rtHz", "opamp_noise_check.json", rnd(i21, 0))
    put(s, "LV front end against adopted: noise at 10 Hz", [lvo["en_LV"]["10"], lvo["en_THS4021"]["10"]], "nV/rtHz",
        "lv_option.json", f"{rnd(lvo['en_LV']['10'], 1)} / {rnd(lvo['en_THS4021']['10'], 1)}")
    a17 = onc["ADA4817"]["noise"]
    put(s, "ADA4817 model: e_n at 100 kHz and at 10 Hz", [a17["100000"]["e_n"] * 1e9, a17["10"]["e_n"] * 1e9],
        "nV/rtHz", "opamp_noise_check.json", f"{rnd(a17['100000']['e_n'] * 1e9, 1)} / {rnd(a17['10']['e_n'] * 1e9, -1)}")

    (R / "numbers_s4a.json").write_text(json.dumps(OUT, indent=1), encoding="utf-8", newline="\n")
    print("section | quantity | value | shown | unit | source")
    for sec, name, value, unit, shown, source in ROWS:
        if isinstance(value, float):
            val = f"{value:.6g}"
        elif isinstance(value, (list, tuple)):
            val = "[" + ", ".join(f"{x:.6g}" if isinstance(x, float) else str(x) for x in value) + "]"
        elif isinstance(value, dict):
            val = json.dumps({kk: ([round(y, 4) for y in vv] if isinstance(vv, list) else round(vv, 4))
                              for kk, vv in value.items()})
        else:
            val = str(value)
        print(f"{sec} | {name} | {val} | {shown if shown is not None else ''} | {unit} | {source}")


if __name__ == "__main__":
    main()
