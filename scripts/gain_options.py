"""Ways to lower the H front end's gain, and where the noise of each comes from (Section 4.3.1 of
the note, Table 6b).

The gain is G = 1 + 2 R_F / R_G (gain 100: R_F 500 ohm, R_G 10.1 ohm).  Two ways to lower it:

  - R_G route: R_F fixed, R_G = 2 R_F / (G - 1).  The differential loop's current fraction
    k_DM = g_m R_G / (2 + g_m R_G) rises, so the cross-coupling can shrink and the front end gets
    faster; the common-mode loop does not involve R_G and keeps its margins.  C_I + C_X stays
    14 pF as at gain 100; D = C_I - C_X is k_DM x 14 pF (the two outer loops equalised) or 1.25
    times that; C_node 220 pF.  These cases reproduce fe_gain_scan.json.
  - R_F route: R_G fixed at 10.1 ohm, R_F = (G - 1) R_G / 2.  k_DM stays 0.15.  The outer loops'
    time constants R_F (C_I +- C_X) must not change, so C_I and C_X scale by 500 ohm / R_F, and
    C_node with them to keep the local loop's beta_CM = (C_I + C_X) / (C_I + C_X + C_node) as it
    is.  A second variant scales C_I and C_X only, to show why C_node must follow.

For each case: the complete loop's margins (frontend.check_loop_out), the front end's -3 dB
bandwidth, its input-referred noise, and that noise split into groups of generators
(frontend.noise_groups) at 10 Hz, 10 kHz, 1 MHz and 10 MHz.  'weight' is the input-referred
weight of a noise current injected at a summing node, 1/g_m + R_F/G per side (Eq. (9) of the
note).

Writes ../sim/results/fe_gain_scan.json (the R_G route, in the format Table 6b was made from) and
../sim/results/fe_gain_options.json (every case, with the noise split).
Usage: python gain_options.py
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace

import numpy as np

import frontend as F
import models
import spice

GM_SIDE = 2 * 0.01726      # transconductance of one side of H (two JFE2140 at 5 mA), operating point
FREQS = (10.0, 1e4, 1e6, 1e7)


def margins(p: F.FE) -> dict:
    out = {}
    for mode in ("dm", "cm"):
        r = F.check_loop_out(p, mode)
        fr, t = r["T"]
        out[mode] = dict(pm=round(r["pm"], 1), gm_db=round(r["gm_db"], 1),
                         fc=[round(x["f"] / 1e6, 1) for x in r["crossings"]],
                         mod=round(float(np.abs(1 + t).min()), 2))
    return out


def noise_checked(p: F.FE, ac: dict) -> tuple[dict, np.ndarray, str]:
    """frontend.check_noise, with a check of its operating point: the noise run's own gain
    (onoise / inoise) must match the AC run's at 1 kHz within 5 %.  For one case here (R_F route,
    gain 30) ngspice's operating point for the noise deck went astray: Kirchhoff's current law at
    the bootstrap node failed by R_UP's 1.5 mA, i.e. the 1 uF bootstrap capacitors were still
    uncharged, as in a transient-based operating point; the op amps sat at the negative rail and
    the JFETs' gates conducted.  The run is then repeated with .nodeset from the AC deck's
    operating point."""
    fstop = 100e6
    nz = F.check_noise(p, fstop)
    fr = nz["f"]
    g_ac = np.abs(np.interp(np.log10(fr), np.log10(ac["curve"][0]), np.abs(ac["curve"][1])))

    def consistent(d: dict) -> bool:
        g = d["onoise_spectrum"] / d["inoise_spectrum"]
        k = int(np.argmin(np.abs(np.log10(d["frequency"] / 1e3))))
        return abs(g[k] / g_ac[k] - 1) < 0.05

    if consistent(nz["nz"]):
        return nz, g_ac, "direct"
    # (A .nodeset that also fixes the servo and sink nodes, vsink, nint, ea and eb, was tried: it made
    # the gain-30 R_F-route case fail, which this one converges.)
    op = F.check_op(p)
    v = {k[2:-1]: val for k, val in op.items() if k.startswith("v(")}
    nodes = dict(sa=v["sa"], sb=v["sb"], ca=v["ca"], cb=v["cb"], oa=v["oa"], ob=v["ob"], ba=v["ba"], bb=v["ba"])
    nodes.update({f"d{x}{k}": v["da1"] for x in "ab" for k in range(1, p.n + 1)})
    ns = ".nodeset " + " ".join(f"v({n})={val:.6g}" for n, val in nodes.items()) + "\n"
    ctl = (".control\n" + spice.WR + f"noise v(oa,ob) VIN dec 20 0.1 {fstop:g} 1\nsetplot noise1\n"
           "wrdata noise.txt all\n.endc\n")
    f = spice.run(f"fe/{p.name}/noise_nodeset", F.deck(p, f"noise {p.name}", F.SRC_NOISE + ns, ctl))
    d = spice.read_noise(f)
    if not consistent(d):
        raise RuntimeError(f"{p.name}: noise run inconsistent with the AC run even with .nodeset")
    fr, inn = d["frequency"], d["inoise_spectrum"]
    nz = dict(f=fr, inn=inn, nz=d, en={str(f0): spice.at(fr, inn, f0) for f0 in (1, 10, 100, 1e3, 1e4, 1e5, 1e6, 1e7)})
    return nz, g_ac, "nodeset"


def evaluate(p: F.FE, noise: bool = True) -> dict:
    res = dict(name=p.name, gain=p.gain, rf=p.rf, rg=p.rg, ci=p.ci, cx=p.cx, cnode=p.cnode,
               k=GM_SIDE * p.rg / (2 + GM_SIDE * p.rg), weight=1 / GM_SIDE + p.rf / p.gain,
               beta_cm=(p.ci + p.cx) / (p.ci + p.cx + p.cnode), loop=margins(p))
    if noise:
        ac = F.check_ac(p)
        nz, gain, how = noise_checked(p, ac)
        fr = nz["f"]
        grp = F.noise_groups(nz["nz"], gain)
        res["noise_op"] = how
        res["f3db"] = ac["f3db"]
        res["en"] = {k: v * 1e9 for k, v in nz["en"].items()}
        res["groups"] = {g: {f"{f0:g}": float(np.interp(np.log10(f0), np.log10(fr), v)) * 1e9 for f0 in FREQS}
                         for g, v in grp.items()}
    return res


def cases() -> dict:
    base = F.CASES["H100"]
    s_sum = base.ci + base.cx
    out = {"H, gain 100 (adopted)": (base, True), "H, gain 10 (range)": (F.CASES["H10"], True)}
    for g in (20, 30):
        rg = 2 * base.rf / (g - 1)
        k = GM_SIDE * rg / (2 + GM_SIDE * rg)
        for fac in (1.0, 1.25):
            d = round(k * s_sum * 1e12 * fac, 2) * 1e-12
            p = replace(base, name=f"H_G{g}_D{d * 1e12:g}", rg=rg, ci=(s_sum + d) / 2, cx=(s_sum - d) / 2,
                        cnode=220e-12)
            out[f"R_G route, gain {g}, D {d * 1e12:.2f} pF"] = (p, True)
        rf = (g - 1) * base.rg / 2
        sc = base.rf / rf
        p = replace(base, name=f"H_RF{g}", rf=rf, ci=base.ci * sc, cx=base.cx * sc, cnode=base.cnode * sc)
        out[f"R_F route, gain {g}, all capacitors x{sc:.2f}"] = (p, True)
    rf = 19 * base.rg / 2
    sc = base.rf / rf
    p = replace(base, name="H_RF20_cnode220", rf=rf, ci=base.ci * sc, cx=base.cx * sc)
    out[f"R_F route, gain 20, C_I and C_X x{sc:.2f}, C_node 220 pF"] = (p, False)
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    res, scan = {}, {}
    for label, (p, noise) in cases().items():
        r = evaluate(p, noise)
        res[label] = r
        lp = r["loop"]
        line = (f"{label}: R_F {p.rf:.1f}, R_G {p.rg:.2f}, C_I {p.ci * 1e12:.2f}, C_X {p.cx * 1e12:.2f}, "
                f"C_node {p.cnode * 1e12:.0f} pF, k {r['k']:.3f}, weight {r['weight']:.1f} ohm, beta_CM {r['beta_cm']:.3f}\n"
                f"    DM {lp['dm']}  CM {lp['cm']}")
        if noise:
            e = r["en"]
            line += (f"\n    f3dB {r['f3db'] / 1e6:.1f} MHz; noise 10 Hz {e['10']:.2f}, 10 kHz {e['10000.0']:.3f}, "
                     f"1 MHz {e['1000000.0']:.3f}, 10 MHz {e['10000000.0']:.3f} nV/rtHz")
            for f0 in ("10000", "1e+07"):
                line += f"\n    groups at {f0} Hz: " + ", ".join(
                    f"{g} {v[f0]:.3f}" for g, v in r["groups"].items() if v[f0] > 0.005)
        print(line, flush=True)
        if label.startswith("R_G route"):
            scan[p.name] = dict(gain=p.gain, rg=p.rg, k=r["k"], D=p.ci - p.cx, loop=lp, f3db=r["f3db"], en=r["en"])
    (spice.RESULTS / "fe_gain_options.json").write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    (spice.RESULTS / "fe_gain_scan.json").write_text(json.dumps(scan, indent=1), encoding="utf-8", newline="\n")


def derived():
    """The numbers of Section 4.3.1's discussion that are computed from fe_gain_options.json:
        e_RG = ((G - 1) / G) sqrt(4kT R_G)          R_G's own noise at the input
        e_RF = sqrt(2 * 4kT R_F) / G                both R_F at the input
        share_x = (e_x,20^2 - e_x,100^2) / (e_20^2 - e_100^2)   share of the added noise power
        ratio_x = e_x,20 / e_x,100;  rise = e_20 / e_100 - 1
        I_o = V_o / R_F at V_o = 12 V;  scale = 500 ohm / R_F;  C_I + C_X after scaling
    and the transconductance of one side of H from the operating point (2 x gm of one JFE2140),
    against GM_SIDE.  Writes ../sim/results/fe_gain_derived.json."""
    import math
    sys.stdout.reconfigure(encoding="utf-8")
    k, t = 1.380649e-23, 300.15
    d = json.loads((spice.RESULTS / "fe_gain_options.json").read_text(encoding="utf-8"))
    a, b = d["H, gain 100 (adopted)"], d["R_G route, gain 20, D 8.33 pF"]
    c30 = d["R_G route, gain 30, D 6.53 pF"]
    rf20 = d["R_F route, gain 20, all capacitors x5.21"]
    out = {}
    for key, r in (("gain 100", a), ("gain 20, R_G", b), ("gain 30, R_G", c30), ("gain 10", d["H, gain 10 (range)"]),
                   ("gain 20, R_F", rf20)):
        g = r["gain"]
        out[f"e_RG {key}"] = (g - 1) / g * math.sqrt(4 * k * t * r["rg"]) * 1e9
        out[f"e_RF {key}"] = math.sqrt(2 * 4 * k * t * r["rf"]) / g * 1e9
    dtot = b["en"]["10000.0"] ** 2 - a["en"]["10000.0"] ** 2
    out["share of added power, gain 20 vs 100"] = {g: (b["groups"][g]["10000"] ** 2 - a["groups"][g]["10000"] ** 2) / dtot
                                                   for g in a["groups"]}
    out["ratio gain 20 / gain 100"] = {g: b["groups"][g]["10000"] / a["groups"][g]["10000"]
                                       for g in a["groups"] if a["groups"][g]["10000"] > 0}
    out["white rise, gain 20 and 30"] = (b["en"]["10000.0"] / a["en"]["10000.0"] - 1,
                                         c30["en"]["10000.0"] / a["en"]["10000.0"] - 1)
    out["I_o at 12 V, R_F 96 and 500 ohm (mA)"] = (12 / rf20["rf"] * 1e3, 12 / a["rf"] * 1e3)
    out["capacitor scale 500/R_F"] = 500.0 / rf20["rf"]
    out["C_I + C_X, R_F route gain 20 (pF)"] = (rf20["ci"] + rf20["cx"]) * 1e12
    op = F.check_op(F.CASES["H100"])
    out["g_m one side from the operating point (S)"] = 2 * op["@j.xja1.j1[gm]"]
    out["GM_SIDE used (S)"] = GM_SIDE
    (spice.RESULTS / "fe_gain_derived.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    if sys.argv[1:] == ["derived"]:
        derived()
    else:
        main()
