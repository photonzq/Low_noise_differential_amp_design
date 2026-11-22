"""Figures of the low-noise preamplifier note, from saved results only (../sim/results/).

  fig_jfet_landscape       e_n against C_iss of the surveyed JFETs, lines of constant e_n sqrt(C)
  fig_jfet_calibration     the calibrated TI models against their data sheets' e_n(I_D) curves
  fig_noise_vs_capacitance differential noise against input capacitance: paralleled JFETs, the two
                           new front ends, commercial instruments; the optimum JFET count
  fig_sr560_benchmark      the SR560 reproduction: noise against gain (manual vs simulation vs the
                           new design), noise spectra, frequency response
  fig_loop_gain            front-end loop gains, with and without the cross-coupled capacitors
  fig_input_admittance     effective input capacitance and parallel resistance; source peaking
  fig_noise_breakdown      noise spectra of H10, H100, L200 with their contributions
  fig_noise_vs_source      noise figure against source resistance
  fig_frequency_response   the chain at every gain
  fig_cmrr                 CMRR (Monte Carlo) against frequency, with the SR560 and NF 5307
  fig_large_signal         distortion and steps
Usage: python make_figures.py [name ...]
"""
from __future__ import annotations

import json
import math
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter, LogFormatterMathtext

import frontend as F
import jfet_data as JD
import plot_style as PS
import spice

R = spice.RESULTS
C = PS.COLORS
# The JFETs' own input capacitance per input, N C_iss (Figures 1 and 10):
#   H: two JFE2140 halves of 13 pF each (TI SLPS730B, p. 5, Sec. 6.5: C_iss at V_DS = 5 V)
#   L: twelve JFE150 of 24 pF each (TI SLPS732B, p. 5, Table 6.5: C_iss at V_DS = 5 V)
N_CISS = {"H": (2, 13.0), "L": (12, 24.0)}
C_JFETS = {k: n * c for k, (n, c) in N_CISS.items()}        # pF per input
# Figure 1's stars: the front end alone (curves_noise.npz, front-end noise runs), at this frequency
# (the white floor; 1.07 and 0.41 nV/rtHz)
F_STAR = 1e4


def _log_axes(ax):
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.xaxis.set_major_formatter(LogFormatterMathtext())
    ax.yaxis.set_major_formatter(LogFormatterMathtext())


def fig_jfet_landscape():
    """e_n against C_iss of the surveyed JFETs.  Parts in the crowded middle of each panel are
    labelled in a column to the right, with leader lines."""
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.4), constrained_layout=True)
    panels = ((axs[0], 2, r"$e_n$ at 1 kHz or white (nV/$\sqrt{\mathrm{Hz}}$)", (0.1, 10), 0.15,
               dict(cmin=8, cmax=90, emin=0.6, emax=1.15), (190, 8.2, 1.3)),
              (axs[1], 4, r"$e_n$ at 10 Hz (nV/$\sqrt{\mathrm{Hz}}$)", (0.3, 30), 0.42,
               dict(cmin=8, cmax=90, emin=1.0, emax=2.6), (160, 9.0, 2.6)))
    for ax, col, ylabel, ylim, e_lab, box, (x_col, y_top, y_bot) in panels:
        cs = np.logspace(-0.3, 3.3, 50)
        for fom_v in (2, 4, 8, 16):
            ax.plot(cs, fom_v / np.sqrt(cs), color=C["annotation"], lw=0.8, ls=PS.DASHED, zorder=1)
            x_t = min(1500.0, (fom_v / e_lab) ** 2)
            ax.text(x_t, fom_v / math.sqrt(x_t) * 1.06, f"{fom_v}", color=C["annotation"], ha="center",
                    va="bottom", fontsize=PS.FONT_SIZE - 1.5)
        crowded = []
        for part, v in JD.JFETS.items():
            if v[col] is None:
                continue
            active = v[1] == "active"
            col_ = C["primary"] if v[0] in ("TI",) else (C["warm_accent"] if v[0] == "Linear Systems" else
                                                          (C["cool_accent"] if v[0] == "InterFET" else C["grey_accent"]))
            ax.plot(v[5], v[col], "o" if active else "s", ms=4.5, mfc=col_ if active else "white", mec=col_,
                    zorder=3)
            if box["cmin"] <= v[5] <= box["cmax"] and box["emin"] <= v[col] <= box["emax"]:
                crowded.append((v[col], v[5], part))
            else:
                ax.annotate(part, (v[5], v[col]), xytext=(3, 3), textcoords="offset points",
                            fontsize=PS.FONT_SIZE - 1, color=C["text"])
        crowded.sort(reverse=True)
        ys = np.logspace(math.log10(y_top), math.log10(y_bot), max(len(crowded), 2))
        for (e, c, part), y in zip(crowded, ys):
            ax.annotate(part, (c, e), xytext=(x_col, y), textcoords="data", fontsize=PS.FONT_SIZE - 1.5,
                        color=C["text"], va="center",
                        arrowprops=dict(arrowstyle="-", color=C["annotation"], lw=0.4, shrinkA=0, shrinkB=2))
        _log_axes(ax)
        ax.set_xlim(0.5, 2500)
        ax.set_ylim(*ylim)
        ax.set_xlabel(r"Input capacitance $C_{iss}$ (pF)")
        ax.set_ylabel(ylabel)
    PS.panel_label(axs[0], "a")
    PS.panel_label(axs[1], "b")
    axs[0].text(0.6, 0.115, "dashed: $e_n\\sqrt{C_{iss}}$ = 2, 4, 8, 16 nV$\\cdot\\sqrt{\\mathrm{pF}}/\\sqrt{\\mathrm{Hz}}$\n"
                "filled: in production; open: discontinued\nblue TI, red Linear Systems, green InterFET",
                fontsize=PS.FONT_SIZE - 1.5, color=C["annotation"])
    return PS.export(fig, "fig_jfet_landscape")


def fig_jfet_calibration():
    d = json.loads((R / "jfet_model_check.json").read_text(encoding="utf-8"))
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.0), constrained_layout=True)
    for ax, part, tag in ((axs[0], "JFE150", "a"), (axs[1], "JFE2140", "b")):
        x = d[part]
        ids = np.array([m["id"] for m in x["model"]]) * 1e3
        ax.plot(ids, np.array([m["en_white"] for m in x["model"]]) * 1e9, color=C["primary"],
                label="model, white")
        ax.plot(ids, np.array([m["en_10"] for m in x["model"]]) * 1e9, color=C["warm_accent"],
                label="model, 10 Hz")
        ax.plot(np.array([c["id"] for c in x["curve"]]) * 1e3, np.array([c["en"] for c in x["curve"]]) * 1e9,
                "o", ms=4, mfc="white", mec=C["neutral"], label="data-sheet curve, 1 kHz")
        ax.plot(np.array([t["id"] for t in x["table"]]) * 1e3, np.array([t["en_1k"] for t in x["table"]]) * 1e9,
                "s", ms=4, color=C["neutral"], label="data-sheet table, 1 kHz")
        ax.plot(np.array([t["id"] for t in x["table"]]) * 1e3, np.array([t["en_10"] for t in x["table"]]) * 1e9,
                "^", ms=4, color=C["warm_accent"], label="data-sheet table, 10 Hz")
        _log_axes(ax)
        # the e_n axis spans less than two decades: plain numbers at 1 and at 2, 3, 5 times a decade
        # (instead of 2 x 10^0 and so on)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
        ax.yaxis.set_minor_formatter(FuncFormatter(
            lambda v, _: f"{v:g}" if round(v / 10 ** math.floor(math.log10(v)), 6) in (2.0, 3.0, 5.0) else ""))
        ax.set_xlabel(r"Drain current $I_D$ (mA)")
        ax.set_ylabel(r"$e_n$ (nV/$\sqrt{\mathrm{Hz}}$)")
        ax.set_title(f"{part} (V$_{{DS}}$ = {x['vds']:g} V)")
        PS.panel_label(ax, tag)
    axs[1].legend(loc="lower left", fontsize=PS.FONT_SIZE - 1.5)
    return PS.export(fig, "fig_jfet_calibration")


def fig_noise_vs_capacitance():
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.3), constrained_layout=True)
    ax = axs[0]
    parts = ["JFE150", "JFE2140", "LSBF862", "LSK170", "LSK389", "IF3601", "IF4500", "LSK489"]
    cols = [C["primary"], C["teal_accent"], C["warm_accent"], C["brown_accent"], C["grey_accent"],
            C["cool_accent"], C["purple_accent"], C["neutral"]]
    for part, col in zip(parts, cols):
        v = JD.JFETS[part]
        n = np.logspace(0, 2.2, 60)
        c = n * v[5]
        e = math.sqrt(2) * v[2] / np.sqrt(n)
        m = c <= 3000
        ax.plot(c[m], e[m], color=col, lw=1.2, label=f"{part} ({v[3]:g} mA)")
    offs = {"SRS SR560": (-4, 3, "right"), "NF 5307": (4, 3, "left"), "NF LI-75A": (-4, 6, "right"),
            "FEMTO DLPVA-101-B": (4, 3, "left"), "NF SA-440F5": (4, -8, "left"),
            "Signal Recovery 5184": (4, -9, "left"), "Stahl PR-E3": (-4, -8, "right"),
            "NF SA-421F5": (-4, -9, "right"), "BasPI SP1004": (4, 2, "left")}
    for name in JD.COMMERCIAL:
        # differential noise and capacitance per input as connected (jfet_data.FIG1_BASIS: the FEMTO
        # at its -D value, 3.0 nV/rtHz; the Stahl PR-E3 with both channels, 2 x 16.4 pF)
        en, cin = JD.fig1_point(name)
        ax.plot(cin, en, "D", ms=4, mfc="white", mec=C["text"], zorder=4)
        dx, dy, ha = offs.get(name, (3, 2, "left"))
        ax.annotate(name, (cin, en), xytext=(dx, dy), textcoords="offset points", fontsize=PS.FONT_SIZE - 2,
                    ha=ha)
    # the new front ends: the JFETs' own capacitance and the front end's simulated noise at F_STAR
    cn = np.load(R / "curves_noise.npz")
    for key, lab, case in (("H", "H (2 × JFE2140)", "H100"), ("L", "L (12 × JFE150)", "L200")):
        en_t = spice.at(cn[f"{case}_f"], cn[f"{case}_total"], F_STAR) * 1e9
        ax.plot(C_JFETS[key], en_t, "*", ms=9, color=C["warm_accent"], zorder=5)
        ax.annotate(lab, (C_JFETS[key], en_t), xytext=(-6, 7) if key == "H" else (6, -11),
                    textcoords="offset points", fontsize=PS.FONT_SIZE - 1, color=C["warm_accent"],
                    ha="right" if key == "H" else "left")
    ax.text(0.97, 0.97, f"stars: front ends alone, simulated, {F_STAR / 1e3:g} kHz", transform=ax.transAxes,
            ha="right", va="top", fontsize=PS.FONT_SIZE - 2, color=C["warm_accent"])
    _log_axes(ax)
    ax.set_xlim(2, 3000)
    ax.set_ylim(0.1, 10)
    ax.set_xlabel("Capacitance per input (pF)")
    ax.set_ylabel(r"Differential input noise (nV/$\sqrt{\mathrm{Hz}}$)")
    ax.legend(loc="lower left", fontsize=PS.FONT_SIZE - 1.5, ncol=2, handlelength=1.4, columnspacing=0.8)
    PS.panel_label(ax, "a")
    # optimum number of JFE150 against source resistance and frequency
    ax = axs[1]
    rs = np.logspace(0, 5, 200)
    c1 = N_CISS["L"][1] * 1e-12            # one JFE150 (SLPS732B p. 5)
    for f0, col in ((1e3, C["primary"]), (1e5, C["cool_accent"]), (1e6, C["warm_accent"]), (1e7, C["purple_accent"])):
        nopt = 1 / (2 * np.pi * f0 * c1 * rs)
        ax.plot(rs, nopt, color=col, label=f"{f0 / 1e6:g} MHz" if f0 >= 1e6 else f"{f0 / 1e3:g} kHz")
    ax.axhline(12, color=C["annotation"], lw=0.8, ls=PS.DASHED)
    ax.text(1.5, 14, "L front end: 12 per side", color=C["annotation"], fontsize=PS.FONT_SIZE - 1)
    _log_axes(ax)
    ax.set_ylim(0.3, 1e5)
    ax.set_xlabel(r"Source resistance $R_S$ ($\Omega$)")
    ax.set_ylabel(r"Optimum number of JFE150, $N_{opt} = 1/(\omega C_1 R_S)$")
    ax.legend(loc="upper right", title="frequency")
    PS.panel_label(ax, "b")
    return PS.export(fig, "fig_noise_vs_capacitance")


def fig_sr560_benchmark():
    sr = json.loads((R / "sr560_chain.json").read_text(encoding="utf-8"))
    new = json.loads((R / "chain_noise.json").read_text(encoding="utf-8"))
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.7), constrained_layout=True)
    ax = axs[0]
    rows = [v for v in sr["noise"].values() if v["mode"] == "LN"]
    g = np.array([v["gain"] for v in rows])
    ax.plot(g, [v["manual"] for v in rows], "o", ms=4, mfc="white", mec=C["neutral"], label="SR560 manual")
    ax.plot(g, [v["en"]["1000.0"] * 1e9 for v in rows], color=C["grey_accent"], label="SR560 model, 1 kHz")
    ax.plot(g, [v["en"]["100000.0"] * 1e9 for v in rows], color=C["grey_accent"], ls=PS.DASHED,
            label="SR560 model, 100 kHz")
    for mode, col, lab in (("H_LN", C["primary"], "new, H"), ("L", C["warm_accent"], "new, L")):
        pts = sorted((int(k.split("_")[-1]), v["en"]["1000.0"] * 1e9) for k, v in new.items()
                     if k.startswith(mode + "_"))
        ax.plot([p[0] for p in pts], [p[1] for p in pts], "-o", ms=3, color=col, label=lab)
    _log_axes(ax)
    ax.set_xlabel("Gain")
    ax.set_ylabel(r"Input noise at 1 kHz (nV/$\sqrt{\mathrm{Hz}}$)")
    ax.legend(fontsize=PS.FONT_SIZE - 1.5)
    PS.panel_label(ax, "a")
    ax = axs[1]
    d = np.load(R / "sr560_chain_noise_LN_1000.npz")
    ax.plot(d["f"], d["inn"] * 1e9, color=C["grey_accent"], label="SR560 model (G 1000)")
    # the SR560 manual's typical curve (printed p. 20, read by eye)
    ax.plot([1, 2, 3, 5, 10, 20, 50, 100, 200, 500, 1000], [42, 35, 28, 19, 11, 9, 7.5, 6.5, 5.8, 5.2, 5.0], "o",
            ms=3.5, mfc="white", mec=C["neutral"], label="SR560 manual, typical")
    cn = np.load(R / "curves_noise.npz")
    ax.plot(cn["chain_H_LN_1000_f"], cn["chain_H_LN_1000_inn"] * 1e9, color=C["primary"], label="new, H (G 1000)")
    ax.plot(cn["chain_L_1000_f"], cn["chain_L_1000_inn"] * 1e9, color=C["warm_accent"], label="new, L (G 1000)")
    _log_axes(ax)
    ax.set_xlim(0.1, 3e7)
    ax.set_ylim(0.2, 300)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel(r"Input noise (nV/$\sqrt{\mathrm{Hz}}$)")
    ax.legend(fontsize=PS.FONT_SIZE - 1.5)
    PS.panel_label(ax, "b")
    ax = axs[2]
    d = np.load(R / "sr560_chain_ac_100.npz")
    m = np.abs(d["h"])
    ax.plot(d["f"], 20 * np.log10(m / spice.at(d["f"], m, 1e3)), color=C["grey_accent"], label="SR560, G 100")
    ca = np.load(R / "curves_ac.npz")
    for key, col, lab in (("H_LN_100", C["primary"], "H, G 100"), ("L_1000", C["warm_accent"], "L, G 1000")):
        f, h = ca[key + "_f"], np.abs(ca[key + "_h"])
        ax.plot(f, 20 * np.log10(h / spice.at(f, h, 1e3)), color=col, label=lab)
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(LogFormatterMathtext())
    ax.set_xlim(1e3, 1e8)
    ax.set_ylim(-12, 2)
    ax.axhline(-3, color=C["annotation"], lw=0.6, ls=":")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Response (dB)")
    ax.legend(fontsize=PS.FONT_SIZE - 1.5, loc="lower left")
    PS.panel_label(ax, "c")
    return PS.export(fig, "fig_sr560_benchmark")


def fig_loop_gain():
    """Three steps of the front end's compensation (H100): (a) without the cross-coupled
    capacitors, loop broken at R_F; (b) with them but without C_node, loop broken at the op amp's
    output; (c) the final values, loop broken at the op amp's output.  The crossover and phase
    margin printed in each phase panel follow Table 6's convention, frontend._margins on the same
    archived curves: the first point of the sweep past each crossing of |T| = 1, with the phase
    unwrapped from 1 kHz (the crossing with the smallest margin is printed)."""
    d = np.load(R / "curves_loop.npz")
    fig, axs = plt.subplots(2, 3, figsize=(7.4, 4.6), constrained_layout=True, sharex="col")
    cols = (("outer_H100_nocross", "(1) $C_I$ = 1.1 pF only;\nloop broken at $R_F$"),
            ("out_H100_old", "(2) $C_I$ = 6.19, $C_X$ = 4.42 pF;\nloop broken at op-amp output"),
            ("out_H100", "(3) $C_I$ = 9, $C_X$ = 5, $C_{node}$ = 220 pF;\nloop broken at op-amp output"))
    for j, (case, title) in enumerate(cols):
        for i, (mode, col, lab) in enumerate((("dm", C["primary"], "differential"),
                                              ("cm", C["warm_accent"], "common mode"))):
            f, t = d[f"{case}_{mode}_f"], d[f"{case}_{mode}_T"]
            ph = np.degrees(np.unwrap(np.angle(t)))
            axs[0, j].plot(f, np.abs(t), color=col, label=lab)
            axs[1, j].plot(f, ph, color=col)
            mg = F._margins(f, t)
            if mg["crossings"]:
                x = min(mg["crossings"], key=lambda c: c["pm"])
                pm_txt = f"{x['pm']:.0f}".replace("-", "−")
                axs[1, j].text(0.04, 0.22 - 0.11 * i, f"{mode.upper()}: $f_c$ {x['f'] / 1e6:.3g} MHz, PM {pm_txt}$^\\circ$",
                               transform=axs[1, j].transAxes, color=col, fontsize=PS.FONT_SIZE - 1.5)
        axs[0, j].set_xscale("log")
        axs[0, j].set_yscale("log")
        axs[0, j].axhline(1, color=C["annotation"], lw=0.6, ls=":")
        axs[0, j].set_ylim(1e-2, 1e5)
        axs[0, j].set_title(title, fontsize=PS.FONT_SIZE - 1)
        axs[1, j].axhline(-180, color=C["annotation"], lw=0.6, ls=":")
        axs[1, j].set_ylim(-400, 0)
        axs[1, j].set_xlim(1e3, 3e9)
        axs[1, j].set_xlabel("Frequency (Hz)")
        axs[1, j].xaxis.set_major_formatter(LogFormatterMathtext())
        axs[0, j].yaxis.set_major_formatter(LogFormatterMathtext())
    axs[0, 0].set_ylabel("|Loop gain|")
    axs[1, 0].set_ylabel("Phase (degrees)")
    axs[0, 0].legend(fontsize=PS.FONT_SIZE - 1.5, loc="lower left")
    for ax, t in zip(axs.flat, "abcdef"):
        PS.panel_label(ax, t, x=-0.2)
    return PS.export(fig, "fig_loop_gain")


def fig_input_admittance():
    z = np.load(R / "curves_zin.npz")
    s = np.load(R / "curves_sources.npz")
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.7), constrained_layout=True)
    for case, col in (("H100", C["primary"]), ("L200", C["warm_accent"])):
        f, zz = z[f"{case}_dm_f"], z[f"{case}_dm_z"]
        y = 1 / zz
        ceff = np.imag(y) / (2 * np.pi * f) * 1e12
        axs[0].plot(f, ceff, color=col, label=f"{case}")
        g = np.real(y)
        axs[1].plot(f[g < 0], -1 / g[g < 0], color=col, label=f"{case}")
    for key, col in (("H", C["primary"]), ("L", C["warm_accent"])):
        n, c1 = N_CISS[key]
        axs[0].axhline(C_JFETS[key], color=col, lw=0.6, ls=":")
        axs[0].text(20, C_JFETS[key] * 1.15, f"{key}: JFETs' own {n} × {c1:g} = {C_JFETS[key]:g} pF", color=col,
                    fontsize=PS.FONT_SIZE - 1.5)
    for ax in axs[:2]:
        _log_axes(ax)
        ax.set_xlim(10, 3e7)
        ax.set_xlabel("Frequency (Hz)")
    axs[0].set_ylim(0.01, 1000)
    axs[0].set_ylabel(r"Effective $C_{in}$ = Im$(Y_{in})/\omega$ (pF)")
    axs[1].set_ylabel(r"Negative parallel resistance $-1/$Re$(Y_{in})$ ($\Omega$)")
    axs[0].legend(loc="center left", bbox_to_anchor=(0.3, 0.5))
    axs[2].plot([], [], color=C["neutral"], ls=PS.DASHED, label="dashed: no input network")
    for key, col, lab in (("H100_{}_1Meg", C["primary"], r"H100, 1 M$\Omega$"),
                          ("H100_{}_1k", C["cool_accent"], r"H100, 1 k$\Omega$"),
                          ("L200_{}_50ohm", C["warm_accent"], r"L200, 50 $\Omega$"),
                          ("L200_{}_1k", C["purple_accent"], r"L200, 1 k$\Omega$")):
        for tag, ls in (("bare", PS.DASHED), ("network", "-")):
            k = key.format(tag)
            f, h = s[k + "_f"], np.abs(s[k + "_h"])
            axs[2].plot(f, 20 * np.log10(h / h[0]), color=col, ls=ls,
                        label=lab if tag == "network" else None)
    axs[2].set_xscale("log")
    axs[2].xaxis.set_major_formatter(LogFormatterMathtext())
    axs[2].set_xlim(1e3, 1e8)
    axs[2].set_ylim(-20, 30)
    axs[2].set_xlabel("Frequency (Hz)")
    axs[2].set_ylabel("Response from the source (dB)")
    axs[2].legend(fontsize=PS.FONT_SIZE - 1.5, loc="upper left", handlelength=1.6)
    for ax, t in zip(axs, "abc"):
        PS.panel_label(ax, t, x=-0.2)
    return PS.export(fig, "fig_input_admittance")


def fig_noise_breakdown():
    d = np.load(R / "curves_noise.npz")
    fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.9), constrained_layout=True, sharey=True)
    groups = ["input JFETs", "R_G", "drain-side R_D", "loop op amps", "cascodes", "current sinks", "R_F",
              "bootstrap (R_BS, R_UP)", "gate stoppers and source resistors"]
    cols = [C["primary"], C["warm_accent"], C["cool_accent"], C["purple_accent"], C["teal_accent"],
            C["brown_accent"], C["neutral"], C["grey_accent"], C["highlight"]]
    styles = ["-"] * 6 + [PS.DASHED, ":", "-"]
    for ax, case, t in zip(axs, ("H10", "H100", "L200"), "abc"):
        f = d[f"{case}_f"]
        ax.plot(f, d[f"{case}_total"] * 1e9, color=C["text"], lw=1.6, label="total")
        for gname, col, ls in zip(groups, cols, styles):
            key = f"{case}_g_{gname}"
            if key in d.files:
                v = d[key] * 1e9
                if v.max() > 0.01:
                    ax.plot(f, v, color=col, lw=1.0, ls=ls, label=gname.replace("R_G", "$R_G$").replace("R_D", "$R_D$")
                            .replace("R_F", "$R_F$").replace("R_BS", "$R_{BS}$").replace("R_UP", "$R_{UP}$"))
        _log_axes(ax)
        ax.set_xlim(1, 3e7)
        ax.set_ylim(0.01, 30)
        ax.set_xlabel("Frequency (Hz)")
        ax.set_title(case)
        PS.panel_label(ax, t)
    axs[0].set_ylabel(r"Input-referred noise (nV/$\sqrt{\mathrm{Hz}}$)")
    axs[2].legend(fontsize=PS.FONT_SIZE - 2, loc="upper right")
    return PS.export(fig, "fig_noise_breakdown")


def fig_noise_vs_source():
    d = json.loads((R / "noise_vs_source.json").read_text(encoding="utf-8"))
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.0), constrained_layout=True)
    for mode, col, lab in (("H_LN", C["primary"], "H"), ("L", C["warm_accent"], "L")):
        rows = d[mode]
        rs = np.array([r["rs"] for r in rows])
        for fk, ls in (("1000.0", "-"), ("1000000.0", PS.DASHED), ("10000000.0", ":")):
            nf = np.array([r["nf_db"][fk] for r in rows])
            vn = np.array([r["vn"][fk] for r in rows])
            fl = {"1000.0": "1 kHz", "1000000.0": "1 MHz", "10000000.0": "10 MHz"}[fk]
            axs[0].plot(rs, nf, color=col, ls=ls, label=f"{lab}, {fl}")
            axs[1].plot(rs, vn * 1e9, color=col, ls=ls, label=f"{lab}, {fl}")
    rs = np.logspace(0, 7, 100)
    axs[1].plot(rs, np.sqrt(4 * spice.KT * rs) * 1e9, color=C["annotation"], lw=0.8, label="source alone")
    # SR560 (manual: noise approximates a 1 kOhm resistor, 4 nV/rtHz)
    en, inn = 4e-9, 0.0
    axs[0].plot(rs, 10 * np.log10(1 + en ** 2 / (4 * spice.KT * rs)), color=C["grey_accent"], lw=1.0,
                label=r"SR560 at 1 kHz ($e_n$ = 4 nV/$\sqrt{\mathrm{Hz}}$ only)")
    axs[0].set_xscale("log")
    axs[0].xaxis.set_major_formatter(LogFormatterMathtext())
    axs[0].set_ylim(0, 20)
    axs[0].set_xlabel(r"Source resistance $R_S$ ($\Omega$)")
    axs[0].set_ylabel("Noise figure (dB)")
    h0, l0 = axs[0].get_legend_handles_labels()
    h1, l1 = axs[1].get_legend_handles_labels()
    axs[1].legend(h0 + h1[-1:], l0 + l1[-1:], fontsize=PS.FONT_SIZE - 1.5, loc="upper left")
    _log_axes(axs[1])
    axs[1].set_xlabel(r"Source resistance $R_S$ ($\Omega$)")
    axs[1].set_ylabel(r"Total input noise (nV/$\sqrt{\mathrm{Hz}}$)")
    PS.panel_label(axs[0], "a")
    PS.panel_label(axs[1], "b")
    return PS.export(fig, "fig_noise_vs_source")


def fig_frequency_response():
    d = np.load(R / "curves_ac.npz")
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.9), constrained_layout=True)
    keys = sorted({k[:-2] for k in d.files})
    pal = [C["primary"], C["cool_accent"], C["warm_accent"], C["purple_accent"], C["teal_accent"], C["brown_accent"]]
    for ax, mode in ((axs[0], "H_LN"), (axs[1], "L")):
        ks = sorted([k for k in keys if k.startswith(mode + "_")], key=lambda k: int(k.split("_")[-1]))
        for k, col in zip(ks, pal):
            f, h = d[k + "_f"], np.abs(d[k + "_h"])
            g = int(k.split("_")[-1])
            ax.plot(f, 20 * np.log10(h), color=col)
            ax.text(2, 20 * np.log10(g) + 2.5, f"gain {g}", color=col, fontsize=PS.FONT_SIZE - 1.5)
        ax.set_ylim(top=20 * np.log10(max(int(k.split("_")[-1]) for k in ks)) + 12)
        ax.set_xscale("log")
        ax.xaxis.set_major_formatter(LogFormatterMathtext())
        ax.set_xlim(1, 3e8)
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Gain (dB)")
        ax.axvline(10e6, color=C["annotation"], lw=0.6, ls=":")
        ax.set_title("H input" if mode == "H_LN" else "L input")
    PS.panel_label(axs[0], "a")
    PS.panel_label(axs[1], "b")
    return PS.export(fig, "fig_frequency_response")


def fig_cmrr():
    d = json.loads((R / "cmrr_mc.json").read_text(encoding="utf-8"))
    fig, axs = plt.subplots(1, 3, figsize=(7.4, 3.0), constrained_layout=True, sharey=True)
    fs = np.logspace(0, 7, 200)
    sr_spec = np.where(fs < 1e3, 100, 100 - 20 * np.log10(fs / 1e3))
    # NF 5307, gain 100 x1: Table 12's row, Fig. 46 of NF's data-sheet page read at the table's frequencies
    # (numbers_s6_7.py, NF_CMRR_PLOT; checked against the image's pixels by nf5307_plot_check.py)
    nf = json.loads((R / "numbers_s6_7.json").read_text(encoding="utf-8"))["s6.4"]["NF 5307 plot, gain 100 (dB)"]["value"]
    nf_f, nf_c = [float(k) for k in nf], [float(v) for v in nf.values()]
    sr = np.load(R / "sr560_chain_cmrr.npz")
    for ax, fe, extra, col, title in ((axs[0], "H100", "H10", C["primary"], "H input (H100; H10)"),
                                      (axs[1], "L200", None, C["warm_accent"], "L input (L200)")):
        for key, ls, lab in ((fe, "-", r"50 $\Omega$ sources"), (f"{fe}_trimmed", PS.DASHED, r"50 $\Omega$, $C_P$/$C_Z$ trimmed"),
                             (f"{fe}_rs0", ":", r"inputs driven directly")):
            if key in d:
                ax.plot(d[key]["freq"], d[key]["median"], color=col, ls=ls, marker="o", ms=2.5, label=lab)
        if extra and extra in d:
            ax.plot(d[extra]["freq"], d[extra]["median"], color=C["cool_accent"], marker="o", ms=2.5,
                    label=r"H10, 50 $\Omega$")
        ax.plot(sr["f"], sr["cmrr"], color=C["grey_accent"], lw=1.0, label="SR560 model (matched)")
        ax.plot(fs, sr_spec, color=C["neutral"], lw=0.8, ls=(0, (1, 1)), label="SR560 specification")
        ax.plot(nf_f, nf_c, "D", ms=3.5, mfc="white", mec=C["text"], label="NF 5307 (plot, gain 100)",
                clip_on=False)                     # the 10 Hz point lies on the axis edge
        ax.set_title(title)
    axs[2].set_title("H100 and L200: one class of mismatch")
    for fe, col in (("H100", C["primary"]), ("L200", C["warm_accent"])):
        for cls, ls in (("jfet", "-"), ("r", PS.DASHED), ("c", ":")):
            key = f"{fe}_only_{cls}"
            if key in d:
                axs[2].plot(d[key]["freq"], d[key]["median"], color=col, ls=ls, marker="o", ms=2.5,
                            label=f"{fe}: " + {"jfet": "JFETs", "r": "resistors", "c": "capacitors"}[cls])
    for ax, t in zip(axs, "abc"):
        ax.set_xscale("log")
        ax.xaxis.set_major_formatter(LogFormatterMathtext())
        ax.set_xlim(10, 1e7)
        ax.set_ylim(20, 170)
        ax.set_xlabel("Frequency (Hz)")
        ax.legend(fontsize=PS.FONT_SIZE - 2.5, loc="lower left")
        PS.panel_label(ax, t)
    axs[0].set_ylabel("CMRR, median of the trials (dB)")
    return PS.export(fig, "fig_cmrr")


def fig_large_signal():
    """THD against frequency (1 and 10 Vpp at the output), the output steps of H100, and the
    input-referred supply rejection, from large_signal.json and the saved step waveforms."""
    d = json.loads((R / "large_signal.json").read_text(encoding="utf-8"))
    fig, axs2 = plt.subplots(2, 2, figsize=(7.0, 5.4), constrained_layout=True)
    axs = axs2.flat
    ax = axs[0]
    for name, col, lab in (("H100", C["primary"], "H, gain 100"), ("L1000", C["warm_accent"], "L, gain 1000")):
        rows = d.get(name, {}).get("thd", [])
        for vpp, ls, mk in ((1, "-", "o"), (10, PS.DASHED, "s")):
            pts = sorted((r["f0"], 100 * r["thd"]) for r in rows if r.get("vout_pp") == vpp and "thd" in r)
            if pts:
                ax.plot([q[0] for q in pts], [q[1] for q in pts], color=col, ls=ls, marker=mk, ms=3,
                        label=f"{lab}, {vpp} Vpp")
    _log_axes(ax)
    ax.set_xlim(500, 2e7)
    ax.set_ylim(5e-5, 5)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("THD (%)")
    ax.legend(fontsize=PS.FONT_SIZE - 2, loc="upper left")
    PS.panel_label(ax, "a")
    ax = axs[1]
    for vstep, col in ((1.0, C["primary"]), (10.0, C["cool_accent"])):
        f = spice.RUNS / "large" / f"H100_step_{vstep:g}" / "tran.txt"
        if not f.exists():
            continue
        w = spice.read_table(f)
        t, v = w["time"], w["v(out)"]
        v0 = np.mean(v[(t > 0.8e-6) & (t < 0.99e-6)])
        v1 = np.mean(v[(t > 3.5e-6) & (t < 4e-6)])
        m = (t > 0.95e-6) & (t < 1.4e-6)
        ax.plot((t[m] - 1e-6) * 1e9, (v[m] - v0) / (v1 - v0), color=col, label=f"{vstep:g} V step")
    ax.axhline(1, color=C["annotation"], lw=0.6, ls=":")
    ax.set_xlim(-50, 400)
    ax.set_xlabel("Time after the input step (ns)")
    ax.set_ylabel("Normalised output, H, gain 100")
    ax.legend(fontsize=PS.FONT_SIZE - 1.5, loc="lower right")
    PS.panel_label(ax, "b")
    ax = axs[2]
    for name, col in (("H100", C["primary"]), ("L1000", C["warm_accent"])):
        ps = d.get(name, {}).get("psrr")
        if not ps:
            continue
        for rail, ls, mk in (("VP", "-", "o"), ("VM", PS.DASHED, "s")):
            f = sorted(float(k) for k in ps[rail])
            ax.plot(f, [ps[rail][str(x) if str(x) in ps[rail] else f"{x:g}"] if False else
                        ps[rail][next(k for k in ps[rail] if float(k) == x)] for x in f],
                    color=col, ls=ls, marker=mk, ms=3, label=f"{name}, {'+15 V' if rail == 'VP' else '−15 V'} rail")
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(LogFormatterMathtext())
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Input-referred supply rejection (dB)")
    ax.legend(fontsize=PS.FONT_SIZE - 2, loc="upper left")
    PS.panel_label(ax, "c")
    ax = axs[3]
    # H from its run with the THS4031 in S2 (with the LM7171 the transient does not converge, Section 6.5
    # of the note), L from overload_curves.npz (LM7171 in S2); both release the overload at 22.01 us
    for name, fname, pre, col in (("H100", "overload_curves_H100_THS4031.npz", "", C["primary"]),
                                  ("L1000", "overload_curves.npz", "L1000_", C["warm_accent"])):
        f = R / fname
        if not f.exists():
            continue
        w = np.load(f)
        if f"{pre}time" not in w.files:
            continue
        t = (w[f"{pre}time"] - 22.01e-6) * 1e9
        m = (t > -60) & (t < 400)
        ax.plot(t[m], w[f"{pre}v(out)"][m], color=col, label=f"{name}: output")
        ax.plot(t[m], (w[f"{pre}v(oa)"] - w[f"{pre}v(ob)"])[m], color=col, ls=PS.DASHED, lw=1.0,
                label=f"{name}: front end, $v_{{oa}} - v_{{ob}}$")
    ax.axhline(0, color=C["annotation"], lw=0.6, ls=":")
    ax.set_xlim(-60, 400)
    ax.set_xlabel("Time after the overload is removed (ns)")
    ax.set_ylabel("Voltage (V)")
    ax.set_title("Recovery from a threefold overload held for 20 µs", fontsize=PS.FONT_SIZE - 1)
    ax.legend(fontsize=PS.FONT_SIZE - 2, loc="upper right")
    PS.panel_label(ax, "d")
    return PS.export(fig, "fig_large_signal")


FIGS = {k: v for k, v in globals().items() if k.startswith("fig_")}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    PS.configure_plot_style()
    for name in sys.argv[1:] or list(FIGS):
        try:
            print(name, FIGS[name]())
        except FileNotFoundError as exc:
            print(name, "missing data:", exc)
