"""Runs the small simulations whose curves the figures need and saves them in ../sim/results/
(curves_*.npz), so that make_figures.py draws from saved data only.

  loop      front-end loop gains (differential and common mode) of H100 and L200, and H100 without
            the cross-coupled capacitors (CI 1.1 pF, CX 0)
  zin       input admittance of H100 and L200 (single input driven, and common mode): the bare front
            ends into curves_zin.npz, then the part zin_net
  zin_net   the input admittance of the front ends with and without the input network of
            chain.INPUT_NET (fresh runs of both, in run folders of their own), and the numbers that
            Section 4.4 and Figure 10 of the note quote; writes curves_zin_network.npz and
            zin_numbers.json and leaves curves_zin.npz as it is
  sources   H100 and L200 driven from 50 ohm, 1 k and 1 Meg with and without the input network
  noise     input-referred noise spectra with the groups of generators: H10, H100, L200 front ends
            and the full chain at a gain of 1000 (H) and 1000 (L)
  ac        the chain's response at the gains of chain.py

Input admittance (frontend.check_zin's bench: 1 A AC into input A; 'dm': input B grounded through
1 milliohm, 'cm': B tied to A; a 1e12-ohm DC path):
    Z_in = v(ga) / 1 A,   Y_in = 1 / Z_in,   C_eff = Im(Y_in) / w   (w = 2 pi f)
    parallel resistance  R_par = 1 / Re(Y_in)   (negative where Re(Y_in) < 0: the smallest |R_par| among
                         the negative values is the note's "minimum", Figure 10b, at the grid point
                         and from a parabola through Re(Y_in) at the three grid points about it, in
                         log10 f: R_par = 1 / G_vertex); the series resistance Re(Z_in) and its
                         minimum are given as well
    the input network per input (chain.INPUT_NET): C_P to ground, R_Z + C_Z in series to ground and
    the bias resistor R_B to ground,
        Y_net = j w C_P + j w C_Z / (1 + j w R_Z C_Z) + 1 / R_B,
        C_in ~ C_P + C_Z (+ the bare front end's C_eff) below f_Z = 1 / (2 pi R_Z C_Z)
        Re(Y_RZCZ) = w^2 C_Z^2 R_Z / (1 + w^2 C_Z^2 R_Z^2)
Sources (curves_sources.npz, archived; H(f) = |v(oa) - v(ob)| for a 1 V differential drive through
R_S in each input, the source part of frontend.check_sources):
    response  20 log10(|H(f)| / |H(10 Hz)|) at 100 kHz and 1 MHz; peaking 20 log10(max|H| / |H(10 Hz)|)
              and its frequency
    1 Mohm with the network, single pole: 20 log10 |1 / (1 + j w R_S C_in)|, C_in = C_P + C_Z + C_bare
Usage: python collect_curves.py [part ...]          (none: loop sources zin noise ac; zin needs
       the sources' curves, curves_sources.npz, for the input network)
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import replace

import numpy as np

import chain
import frontend as F
import models
import spice

R = spice.RESULTS


def loop():
    """Outer loop (broken at R_F, check_loop) and complete loop (broken at the op amp's output,
    check_loop_out) of the final front ends, and of two earlier, unstable versions of H100:
    without the cross-coupled capacitors (C_I 1.1 pF only: the common-mode outer loop is unstable)
    and with them but without C_node (C_I 6.19 pF, C_X 4.42 pF: the op amp's own common-mode
    loop is unstable near 300 MHz)."""
    out = {}
    nocross = replace(F.CASES["H100"], name="H100_nocross", ci=1.1e-12, cx=0.0, cnode=0.0)
    old = replace(F.CASES["H100"], name="H100_old", ci=6.19e-12, cx=4.42e-12, cnode=0.0)
    runs = [("outer", "H100", F.CASES["H100"]), ("outer", "L200", F.CASES["L200"]),
            ("outer", "H100_nocross", nocross), ("outer", "H100_old", old),
            ("out", "H100", F.CASES["H100"]), ("out", "H10", F.CASES["H10"]), ("out", "L200", F.CASES["L200"]),
            ("out", "H100_old", old)]
    for kind, k, p in runs:
        for mode in ("dm", "cm"):
            lp = F.check_loop(p, mode) if kind == "outer" else F.check_loop_out(p, mode)
            fr, t = lp["T"]
            out[f"{kind}_{k}_{mode}_f"] = fr
            out[f"{kind}_{k}_{mode}_T"] = t
            if kind == "outer":
                print(f"loop at R_F {k} {mode}: fc {lp['fc'] / 1e6:.1f} MHz, PM {lp['pm']:.1f}, GM {lp['gm_db']:.1f}")
            else:
                print(f"loop at op-amp output {k} {mode}: crossings "
                      f"{[(round(x['f'] / 1e6, 1), round(x['pm'], 1)) for x in lp['crossings']]}, GM {lp['gm_db']:.1f}")
    np.savez(R / "curves_loop.npz", **out)


def zin():
    out = {}
    for k in ("H100", "L200"):
        z = F.check_zin(F.CASES[k])
        for mode in ("dm", "cm"):
            out[f"{k}_{mode}_f"] = z[mode]["f"]
            out[f"{k}_{mode}_z"] = z[mode]["z"]
    np.savez(R / "curves_zin.npz", **out)
    zin_net()


ZIN_SRC = {"dm": "IA 0 ga DC 0 AC 1\nRIB 0 gb 1m rnl\nRBIAS ga 0 1e12 rnl\n",
           "cm": "IA 0 ga DC 0 AC 1\nRIB ga gb 1m rnl\nRBIAS ga 0 1e12 rnl\n"}
ZIN_FREQ = (1e3, 1e5, 3e5, 1e6)


def network_lines(n: dict) -> str:
    """The input network of chain.netlist, per input."""
    return (f"CPA ga 0 {n['cp']:g}\nCPB gb 0 {n['cp']:g}\nRZA ga za {n['rz']:g}\nCZA za 0 {n['cz']:g}\n"
            f"RZB gb zb {n['rz']:g}\nCZB zb 0 {n['cz']:g}\nRBA ga 0 {n['rbias']:g}\nRBB gb 0 {n['rbias']:g}\n")


def zin_run(p: F.FE, extra: str = "") -> dict:
    """frontend.check_zin's two benches, with optional extra lines (the input network)."""
    out = {}
    for mode, src in ZIN_SRC.items():
        ctl = ".control\n" + spice.WR + "ac dec 20 10 1g\nwrdata zin.txt v(ga)\n.endc\n"
        f = spice.run(f"fe/{p.name}/zin_{mode}", F.deck(p, f"zin {p.name} {mode}", src + extra, ctl))
        d = spice.read_table(f / "zin.txt")
        out[mode] = dict(f=d["frequency"], z=d["v(ga)"])
    return out


def admittance_numbers(f: np.ndarray, z: np.ndarray) -> dict:
    """C_eff at ZIN_FREQ, the minimum of Re(Z) and of Re(Y), the negative parallel resistance."""
    y = 1 / z
    w = 2 * np.pi * f
    ceff = np.imag(y) / w
    out = dict(C_eff={f"{f0:g}": spice.at(f, ceff, f0) for f0 in ZIN_FREQ})
    i = int(np.argmin(np.real(z)))
    out.update(ReZ_min=float(np.real(z)[i]), ReZ_min_f=float(f[i]))
    j = int(np.argmin(np.real(y)))
    out.update(ReY_min=float(np.real(y)[j]), ReY_min_f=float(f[j]))
    neg = np.real(y) < 0
    if neg.any():
        rp = 1 / np.real(y)
        k = int(np.argmax(np.where(neg, rp, -np.inf)))          # the negative value closest to zero
        out.update(Rpar_neg_min=float(rp[k]), Rpar_neg_min_f=float(f[k]),
                   ReY_negative_from=float(f[neg][0]), ReY_negative_to=float(f[neg][-1]))
        if 0 < k < len(f) - 1:
            # between the grid points: a parabola through Re(Y) at the three points about the
            # minimum, in x = log10 f, its vertex x_v and value G_v; R_par = 1 / G_v
            x, g = np.log10(f[k - 1:k + 2]), np.real(y)[k - 1:k + 2]
            a, b, c = np.polyfit(x, g, 2)
            xv = -b / (2 * a)
            out.update(Rpar_neg_min_interp=float(1 / (c - b * b / (4 * a))), Rpar_neg_min_interp_f=float(10 ** xv))
    else:
        out.update(Rpar_neg_min=None)
    return out


def zin_net():
    """Fresh bare and network runs, the numbers, curves_zin_network.npz and zin_numbers.json."""
    curves, res = {}, {}
    arch = np.load(R / "curves_zin.npz")
    src = np.load(R / "curves_sources.npz")
    for k in ("H100", "L200"):
        n = chain.INPUT_NET[k[0]]
        r = res[k] = dict(network=dict(n), C_P_plus_C_Z=n["cp"] + n["cz"],
                          f_Z=1 / (2 * math.pi * n["rz"] * n["cz"]))
        for tag, extra in (("bare", ""), ("network", network_lines(n))):
            z = zin_run(replace(F.CASES[k], name=f"{k}_zin_{tag}"), extra)
            for mode in ("dm", "cm"):
                curves[f"{k}_{tag}_{mode}_f"] = z[mode]["f"]
                curves[f"{k}_{tag}_{mode}_z"] = z[mode]["z"]
                r[f"{tag}_{mode}"] = admittance_numbers(z[mode]["f"], z[mode]["z"])
        for mode in ("dm", "cm"):
            r[f"bare_archived_{mode}"] = admittance_numbers(arch[f"{k}_{mode}_f"], arch[f"{k}_{mode}_z"])
        # the archived source responses (Figure 10c)
        c_bare = r["bare_archived_dm"]["C_eff"]["1000"]
        s = {}
        for tag in ("bare", "network"):
            for rs_name, rs in (("50ohm", 50.0), ("1k", 1e3), ("1Meg", 1e6)):
                fr, h = src[f"{k}_{tag}_{rs_name}_f"], np.abs(src[f"{k}_{tag}_{rs_name}_h"])
                i = int(np.argmax(h))
                e = dict(peak_db=float(20 * np.log10(h[i] / h[0])), f_peak=float(fr[i]),
                         **{f"db_{lab}": float(20 * np.log10(spice.at(fr, h, f0) / h[0]))
                            for lab, f0 in (("100k", 1e5), ("1M", 1e6))})
                if tag == "network":
                    c_in = n["cp"] + n["cz"] + c_bare
                    e.update({f"single_pole_db_{lab}": float(-10 * np.log10(1 + (2 * np.pi * f0 * rs * c_in) ** 2))
                              for lab, f0 in (("100k", 1e5), ("1M", 1e6))})
                s[f"{tag}_{rs_name}"] = e
        r["sources_archived"] = s
        r["network_largest_peak_db"] = max(v["peak_db"] for kk, v in s.items() if kk.startswith("network"))
    np.savez(R / "curves_zin_network.npz", **curves)
    (R / "zin_numbers.json").write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    for k, r in res.items():
        print(f"{k}: C_P + C_Z = {r['C_P_plus_C_Z'] * 1e12:.0f} pF, f_Z = 1/(2 pi R_Z C_Z) = {r['f_Z'] / 1e6:.2f} MHz")
        for tag in ("bare_archived", "bare", "network"):
            for mode in ("dm", "cm"):
                a = r[f"{tag}_{mode}"]
                rp = (f"R_par min {a['Rpar_neg_min']:.1f} ohm at {a['Rpar_neg_min_f'] / 1e6:.2f} MHz "
                      f"(interpolated {a.get('Rpar_neg_min_interp', float('nan')):.1f} ohm at "
                      f"{a.get('Rpar_neg_min_interp_f', float('nan')) / 1e6:.2f} MHz) "
                      f"(Re Y < 0 from {a['ReY_negative_from'] / 1e6:.3g} to {a['ReY_negative_to'] / 1e6:.3g} MHz)"
                      if a["Rpar_neg_min"] is not None else "Re Y > 0 everywhere")
                print(f"  {tag:13s} {mode}: C_eff " + ", ".join(f"{f0}: {v * 1e12:.4g} pF" for f0, v in a["C_eff"].items())
                      + f"; min Re Z {a['ReZ_min']:.4g} ohm at {a['ReZ_min_f'] / 1e6:.3g} MHz; {rp}")
        for kk, e in r["sources_archived"].items():
            extra = (f"; single pole {e['single_pole_db_100k']:+.1f} / {e['single_pole_db_1M']:+.1f} dB"
                     if "single_pole_db_1M" in e else "")
            print(f"  source {kk:16s}: peak {e['peak_db']:.2f} dB at {e['f_peak'] / 1e6:.3g} MHz; 100 kHz "
                  f"{e['db_100k']:+.2f} dB, 1 MHz {e['db_1M']:+.2f} dB{extra}")
        print(f"  largest peak with the network: {r['network_largest_peak_db']:.2f} dB")


def sources():
    out = {}
    nets = {"H100": chain.INPUT_NET["H"], "L200": chain.INPUT_NET["L"]}
    for k, n in nets.items():
        extra = (f"CPA ga 0 {n['cp']:g}\nCPB gb 0 {n['cp']:g}\nRZA ga za {n['rz']:g}\nCZA za 0 {n['cz']:g}\n"
                 f"RZB gb zb {n['rz']:g}\nCZB zb 0 {n['cz']:g}\n")
        for tag, ex in (("bare", ""), ("network", extra)):
            p = replace(F.CASES[k], name=f"{k}_src_{tag}")
            r = F.check_sources(p, ["50ohm", "1k", "1Meg"], ex)
            for nm, v in r.items():
                out[f"{k}_{tag}_{nm}_f"] = v["f"]
                out[f"{k}_{tag}_{nm}_h"] = v["h"]
                print(f"sources {k} {tag} {nm}: peak {v['peak_db']:.1f} dB at {v['f_peak'] / 1e6:.2f} MHz")
    np.savez(R / "curves_sources.npz", **out)


def noise():
    out = {}
    for k in ("H10", "H100", "L200"):
        p = F.CASES[k]
        ac = F.check_ac(p)
        nz = F.check_noise(p)
        fr = nz["f"]
        gain = np.abs(np.interp(np.log10(fr), np.log10(ac["curve"][0]), np.abs(ac["curve"][1])))
        grp = F.noise_groups(nz["nz"], gain)
        out[f"{k}_f"] = fr
        out[f"{k}_total"] = nz["inn"]
        for g, v in grp.items():
            out[f"{k}_g_{g}"] = v
    for mode, g in (("H_LN", 1000), ("L", 1000), ("H_HR", 1000)):
        r = chain.run_noise(chain.allocate(g, mode))
        out[f"chain_{mode}_{g}_f"] = r["f"]
        out[f"chain_{mode}_{g}_inn"] = r["inn"]
    np.savez(R / "curves_noise.npz", **out)


def ac():
    out = {}
    for mode, gl in (("H_LN", [1, 10, 100, 1000, 10000, 50000]), ("L", [200, 1000, 10000, 100000])):
        for g in gl:
            r = chain.run_ac(chain.allocate(g, mode))
            out[f"{mode}_{g}_f"] = r["f"]
            out[f"{mode}_{g}_h"] = r["h"]
    np.savez(R / "curves_ac.npz", **out)


PARTS = dict(loop=loop, zin=zin, zin_net=zin_net, sources=sources, noise=noise, ac=ac)
DEFAULT = ("loop", "sources", "zin", "noise", "ac")      # zin_net reads curves_sources.npz

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    for part in sys.argv[1:] or DEFAULT:
        PARTS[part]()
