"""Closed forms behind the numbers of Sections 4.2 (headroom), 4.2.1 (the sinks' heat and copper),
4.6 (the sinks' drift) and 6.1 (the sinks' noise) of the note.  No simulation of its own: the
inputs are the archived results of frontend.py (operating point), sink_options.py, sink_power.py,
chain.py and sr560_frontend.py, the model cards in ../sim/models/_lib/, and the data sheet values
named below.  k = 1.380649e-23 J/K, q = 1.602176634e-19 C, T = 300.15 K (ngspice's 27 C).

Headroom of the front end (Section 4.2):
    V_GS = V(s) - V(g), V_DS,J = V(d) - V(s)                         from the operating point
    V_GS,c = V_TO + sqrt(I_D / beta),  V_DS,sat = V_GS,c - V_TO       LSBF862 card (square law)
    V_CM,max = V_ref - V_GS - V_DS,J - V_DS,c,min,  V_DS,c,min = 1 V   (cascode: V_DS,sat plus room)
    V_CM,min = V_E + V_CE,min - V_GS,  V_CE,min = 0.5 V                 (sink: emitter at V_E)
    V_RD = V_P - V_ref;  SR560: V_DS = V(d) - V(s) of its reproduction

The sinks' heat, common-mode range and copper (Section 4.2.1, Eqs. (9a)-(9c)):
    R_T = V_RT / (N I_D + I_BS);  P_T + P_RT = (V_S - V_M) I_T;  dT_J = P_T R_thJA     (9a)
    P_RD = (V_P - V_ref) N I_D
    V_CM,min = V_E + V_CE,min - V_GS                                                  (9b)
    C_tab = eps0 eps_r A / d;  CMRR = 1 / (omega dC R_F / G)                          (9c)
        (eps_r = 4.4 and d = 0.2 mm assumed: FR-4 between the tab's copper and a ground plane)

The sinks' drift (Section 4.6, Eqs. (11a)-(11b)):
    dV_BE/dT = -(E_G - V_BE + X_TI V_T) / T          (Gummel-Poon with IS ~ T^X_TI exp(-E_G/V_T))
    dV_in/d(dT) = (|dV_BE/dT| / R_T) R_F / G                                          (11a)
    e_in = sqrt(2) (e_n / R_T) R_F / G   (an op amp of e_n setting the sink's current) (11b)

The sinks' noise (Section 6.1, Eqs. (12)-(12a)):
    i_shot = sqrt(2 q I)
    i_RT = sqrt(4kT / R_T) = i_shot sqrt(2 V_T / V_RT)    (any resistor setting I with V across it)
    i_b = sqrt(2 q I / beta),  i_c = i_shot (V_T / V_RT + 1 / beta),  i_rb = sqrt(4kT r_b) / R_T
    i_T^2 / i_shot^2 = 2 V_T / V_RT + 1 / beta + (V_T / V_RT + 1 / beta)^2   (+ r_b's part)   (12)
    e_in = sqrt(2) i_T R_F / G          (both sides, at the input)
    e_without = sqrt(e_tot^2 - e_sinks^2);  e_after = sqrt(e_chain^2 - e_FE^2)
    D' = D (R_F / R_F') (k' / k),  S' = S R_F / R_F'   (compensation for R_F halved at a gain of 10)

Writes ../sim/results/fe_closed_forms.json.  Usage: python fe_closed_forms.py
"""
from __future__ import annotations

import json
import math
import re
import sys

import frontend as F
import spice

K, Q, T = 1.380649e-23, 1.602176634e-19, 300.15
VT = K * T / Q
EPS0 = 8.8541878128e-12
GM_SIDE = 2 * 0.01726                 # one side of H, as in gain_options.py


def card(name: str, lib: str) -> dict:
    text = (spice.LIB / lib).read_text(encoding="utf-8", errors="replace")
    m = re.search(rf"^\.model\s+{re.escape(name)}_?M?\s+\w+\s*\((.*?)\)\s*$", text, re.M | re.I | re.S)
    if not m:
        m = re.search(rf"^\.model\s+{re.escape(name)}\s+\w+\s*\((.*?)\)\s*$", text, re.M | re.I)
    pairs = re.findall(r"(\w+)\s*=\s*([-+0-9.eE]+[a-zA-Z]*)", m.group(1))
    return {k.upper(): spice_num(v) for k, v in pairs}


def spice_num(s: str) -> float:
    m = re.match(r"([-+0-9.eE]+)([a-zA-Z]*)", s)
    x = float(m.group(1))
    suf = m.group(2).lower()
    for p, f in (("meg", 1e6), ("f", 1e-15), ("p", 1e-12), ("n", 1e-9), ("u", 1e-6), ("m", 1e-3), ("k", 1e3), ("g", 1e9)):
        if suf.startswith(p):
            return x * f
    return x


def rfg(case: str) -> float:
    p = F.CASES[case]
    return p.rf / p.gain


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    R = spice.RESULTS
    so = json.loads((R / "sink_options.json").read_text(encoding="utf-8"))
    sp = json.loads((R / "sink_power.json").read_text(encoding="utf-8"))
    cn = json.loads((R / "chain_noise.json").read_text(encoding="utf-8"))
    sr = json.loads((R / "sr560_frontend.json").read_text(encoding="utf-8"))
    out = {}

    # ---- headroom (Section 4.2) ----
    lsbf = card("LSBF862_M", "jfets.lib")
    hd = {}
    for case in ("H100", "L200"):
        p = F.CASES[case]
        op = F.check_op(p)
        vgs = op["v(sa)"]
        vds_j = op["v(da1)"] - op["v(sa)"]
        vgs_c = lsbf["VTO"] + math.sqrt(p.id / lsbf["BETA"])
        vds_sat = vgs_c - lsbf["VTO"]
        vcm_max = p.vref - vgs - vds_j - 1.0
        hd[case] = dict(V_GS=vgs, V_DS_J=vds_j, V_GS_c=vgs_c, V_DS_sat_c=vds_sat, V_CM_max=vcm_max,
                        V_RD=p.vp - p.vref)
    hd["SR560 V_DS"] = sr["sr560_x10_2N5564"]["op"]["v(da)"] - sr["sr560_x10_2N5564"]["op"]["v(sa)"]
    hd["V_CM_min H (2 V)"] = so["H10 | MMBT3904, 2 V (adopted)"]["op"]["vcm_min"]
    hd["V_CM_min L (6 V)"] = sp["L200 | 6 V"]["op"]["vcm_min"]
    out["headroom"] = hd

    # ---- heat and copper (Section 4.2.1) ----
    heat = {}
    for key, o in (("H, 2 V", so["H10 | MMBT3904, 2 V (adopted)"]["op"]),
                   ("L, 2 V", sp["L200 | 2 V"]["op"]), ("L, 4 V", sp["L200 | 4 V"]["op"]),
                   ("L, 6 V", sp["L200 | 6 V"]["op"]), ("L, 8 V", sp["L200 | 8 V"]["op"])):
        heat[key] = dict(I_T=o["i_sink"], P_total=o["p_transistor"] + o["p_rt"], P_T=o["p_transistor"],
                         P_RT=o["p_rt"], rise_SOT23=o["p_transistor"] * 556.0,
                         rise_SOT223=o["p_transistor"] * 83.3, V_CM_min=o["vcm_min"])
    pL = F.CASES["L200"]
    heat["R_T, L (6 V)"] = pL.v_sink / (pL.n * pL.id + pL.i_bs)
    heat["P_RD, L"] = (pL.vp - pL.vref) * pL.n * pL.id
    heat["P_RD, H"] = (F.CASES["H100"].vp - F.CASES["H100"].vref) * F.CASES["H100"].n * F.CASES["H100"].id
    c_tab = EPS0 * 4.4 * 713e-6 / 0.2e-3
    heat["C_tab (713 mm2, eps_r 4.4, 0.2 mm)"] = c_tab
    heat["dC/C for 1 pF"] = 1e-12 / c_tab
    for case in ("L200", "H100"):
        heat[f"CMRR, 1 pF, 1 MHz, {case}"] = 20 * math.log10(1 / (2 * math.pi * 1e6 * 1e-12 * rfg(case)))
    ps2, ps6 = sp["L200 | 2 V"]["psrr_L1000"]["VM"], sp["L200 | 6 V"]["psrr_L1000"]["VM"]
    heat["PSRR(-15 V) 2 V -> 6 V, 1 kHz"] = (-ps2["1000.0"], -ps6["1000.0"], ps6["1000.0"] - ps2["1000.0"])
    heat["PSRR(-15 V) 2 V -> 6 V, 1 MHz"] = (-ps2["1000000.0"], -ps6["1000000.0"], ps6["1000000.0"] - ps2["1000000.0"])
    out["heat"] = heat

    # ---- drift (Section 4.6) ----
    q3904 = card("MMBT3904", "bjts.lib")
    dr = {}
    for key, case, vrt, o, sim in (("H100, 2 V", "H100", 2.0, sp["H100 | 2 V"]["op"], sp["H100 | 2 V"]["drift_uV_per_K"]),
                                   ("H10, 2 V", "H10", 2.0, sp["H10 | 2 V"]["op"], sp["H10 | 2 V"]["drift_uV_per_K"]),
                                   ("H100, 6 V", "H100", 6.0, sp["H100 | 6 V"]["op"], sp["H100 | 6 V"]["drift_uV_per_K"]),
                                   ("H10, 6 V", "H10", 6.0, sp["H10 | 6 V"]["op"], sp["H10 | 6 V"]["drift_uV_per_K"]),
                                   ("L, 2 V", "L200", 2.0, sp["L200 | 2 V"]["op"], sp["L200 | 2 V"]["drift_uV_per_K"]),
                                   ("L, 6 V", "L200", 6.0, sp["L200 | 6 V"]["op"], sp["L200 | 6 V"]["drift_uV_per_K"])):
        p = F.CASES[case]
        vbe = o["v_ctrl"] - o["v_ea"]
        dvbe = -(q3904["EG"] - vbe + q3904["XTI"] * VT) / T
        r_t = vrt / (p.n * p.id + p.i_bs)
        analytic = abs(dvbe) / r_t * rfg(case) * 1e6
        dr[key] = dict(V_BE=vbe, dVBE_dT_mV=dvbe * 1e3, R_T=r_t, analytic_uV_per_K=analytic,
                       simulated_uV_per_K=sim, output_mV_per_K=sim * p.gain * 1e-3)
    for key, case, vrt in (("op-amp sink, L, 6 V", "L200", 6.0), ("op-amp sink, H10, 2 V", "H10", 2.0)):
        p = F.CASES[case]
        r_t = vrt / (p.n * p.id + p.i_bs)
        dr[key] = dict(e_n_nV=5.0, e_in_nV=math.sqrt(2) * 5e-9 / r_t * rfg(case) * 1e9)
    out["drift"] = dr

    # ---- noise (Section 6.1) ----
    nz = {}
    for key, case, part, vrt, beta, rb, simkey in (
            ("H, MMBT3904, 2 V", "H10", "MMBT3904", 2.0, card("MMBT3904", "bjts.lib")["BF"], card("MMBT3904", "bjts.lib")["RBM"],
             "H10 | MMBT3904, 2 V (adopted)"),
            ("H, MMBT3904, 6 V", "H10", "MMBT3904", 6.0, card("MMBT3904", "bjts.lib")["BF"], card("MMBT3904", "bjts.lib")["RBM"],
             "H10 | MMBT3904, 6 V"),
            ("H, BC817-25, 6 V", "H10", "BC817-25", 6.0, card("BC817-25", "bjts.lib")["BF"], card("BC817-25", "bjts.lib")["RB"],
             "H10 | BC817-25, 6 V")):
        o = so[simkey]["op"]
        i_t = o["i_sink"]
        r_t = vrt / i_t
        ish = math.sqrt(2 * Q * i_t)
        i_rt = math.sqrt(4 * K * T / r_t)
        i_b = math.sqrt(2 * Q * i_t / beta)
        i_c = ish * (VT / vrt + 1 / beta)
        i_rb = math.sqrt(4 * K * T * rb) / r_t
        tot = math.sqrt(i_rt ** 2 + i_b ** 2 + i_c ** 2 + i_rb ** 2)
        eq12 = 2 * VT / vrt + 1 / beta + (VT / vrt + 1 / beta) ** 2
        w = math.sqrt(2) * rfg(case)
        sim = so[simkey]["split"]
        nz[key] = dict(I_T=i_t, beta=beta, r_b=rb, i_shot_pA=ish * 1e12, i_RT_pA=i_rt * 1e12, i_b_pA=i_b * 1e12,
                       i_c_pA=i_c * 1e12, i_rb_pA=i_rb * 1e12, i_T_pA=tot * 1e12, eq12_ratio=math.sqrt(eq12),
                       sqrt_2VT_over_V=math.sqrt(2 * VT / vrt), one_over_sqrt_beta=1 / math.sqrt(beta),
                       e_in_gain10_nV=tot * w * 1e9, sim_sinks_gain10_nV=so[simkey]["sinks"]["10000"],
                       sim_R_T_nV=sim["R_T"]["10000"], sim_transistor_nV=sim["transistor"]["10000"],
                       e_RT_gain10_nV=i_rt * w * 1e9, e_b_gain10_nV=i_b * w * 1e9)
    for case in ("H100", "L200"):
        p = F.CASES[case]
        r_d = (p.vp - p.vref) / (p.n * p.id)
        i_rd = math.sqrt(4 * K * T / r_d)
        ish = math.sqrt(2 * Q * p.n * p.id)
        nz[f"R_D, {case}"] = dict(R_D=r_d, i_RD_pA=i_rd * 1e12, i_shot_pA=ish * 1e12, ratio=i_rd / ish,
                                  sqrt_2VT_over_V=math.sqrt(2 * VT / (p.vp - p.vref)))
    a = so["H10 | MMBT3904, 2 V (adopted)"]
    nz["without sink noise, gain 10"] = math.sqrt(a["en"]["10000.0"] ** 2 - a["sinks"]["10000"] ** 2)
    nz["stages after the front end, H_HR 100, 1 kHz"] = math.sqrt((cn["H_HR_100"]["en"]["1000.0"] * 1e9) ** 2
                                                                   - a["en"]["1000.0"] ** 2)
    rel = {}
    for lab in ("MMBT3904, 4 V", "MMBT3904, 6 V", "BC817-25, 4 V", "BC817-25, 6 V", "JFE150, 6 V"):
        rel[f"front end, {lab}"] = so[f"H10 | {lab}"]["en"]["10000.0"] / a["en"]["10000.0"] - 1
    base = so["chain | MMBT3904, 2 V (adopted) | H_HR 100"]["en"]["1000.0"]
    for lab in ("BC817-25, 4 V", "BC817-25, 6 V", "JFE150, 6 V", "R_F 250 ohm (MMBT3904, 2 V)"):
        rel[f"chain H_HR 100, {lab}"] = so[f"chain | {lab} | H_HR 100"]["en"]["1000.0"] / base - 1
    nz["relative changes"] = rel
    k10 = GM_SIDE * F.CASES["H10"].rg / (2 + GM_SIDE * F.CASES["H10"].rg)
    rg_new = 2 * 250.0 / 9
    k_new = GM_SIDE * rg_new / (2 + GM_SIDE * rg_new)
    p10 = F.CASES["H10"]
    d_new = (p10.ci - p10.cx) * (p10.rf / 250.0) * (k_new / k10)
    s_new = (p10.ci + p10.cx) * (p10.rf / 250.0)
    nz["R_F 250 for the gain-10 range"] = dict(R_G=rg_new, k=k10, k_new=k_new, D_new_pF=d_new * 1e12,
                                               S_new_pF=s_new * 1e12, C_node_new_pF=p10.cnode * 2 * 1e12)
    out["noise"] = nz

    (R / "fe_closed_forms.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
