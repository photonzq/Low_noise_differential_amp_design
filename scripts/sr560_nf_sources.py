"""Where the SR560 reproductions' input noise current comes from, and their input capacitance (Figure 14,
Section 6.2): a check of the statement that, without the tail servo's share, their noise current at 1 MHz is the
e_n w C of their input capacitance.  It is not: see (2).

(1) zin: the input admittance at input A with input B grounded through 1 ohm, as in nf_map.py's noise runs: an AC
current of 1 A into input A (the source resistor RSA set to 1e12 ohm, noiseless, so that the deck keeps its nodes
and the trimmed state's .nodeset), Y = 1 / V(ina) - 1e-12 S.  C_in = Im(Y) / w; the conductance G without R101's
10 nS.  Both SR560 models of nf_map.py (the corrected LSK389B model's decks with abstol = 1e-12 A, as there), 1 kHz
to 30 MHz.
(2) noise: the noise by generator, from nf_map.py's 41 runs per model (sim/runs/nf_map/<model>/rs_*/; no ngspice).
Each of ngspice's noise generators (the leaves: a device's total is listed beside its parts) is referred to the
input by the run's own gain, onoise / inoise, and fitted at each frequency like the total (Eq. (5a)): S_e, S_x, S_i
per generator; independent generators add, so the generators' sums must reproduce the total's fit
("sum_check").  Grouped by side (A: the driven input; B: grounded through 1 ohm): each JFET's channel noise (_id)
and its wrapper's gate resistor RX, then the rest of the input pair (_rd, _rs and flicker generators), the tail
servo (U103, R125, R127, R129, R130), the input resistors (R101, R102), U102 (OP37), and the rest.  For each group
the effective capacitance sqrt(S_i / S_e) / w, the capacitance through which its noise becomes an input current.
What the groups show (the physics, which the first version of this docstring had wrong):
  - a noise voltage in series with the driven gate (RX of input A) lies in the source's loop: R_S and the input
    capacitance divide it exactly like the signal, so it gives no current at all (its effective capacitance is
    0; only R101's e/R101 is left), whatever the input capacitance;
  - JFET A's channel noise, a drain current, needs a gate voltage that charges the device's own capacitances, so
    its current is e_ch w (C_gs + C_gd) at the JFET's bias, the textbook FET result: c_gs_plus_c_gd_pf below,
    from the model card (C = C0 / sqrt(1 - V / PB), the level 1 JFET's grading 0.5) and the trimmed operating
    point, against the group's effective capacitance;
  - noise on the grounded side (JFET B) and elsewhere is not divided at input A like the signal, and reaches it
    with its own effective capacitance; the tail servo's common-mode noise through the source's imbalance.
The input capacitance C_in of (1) is thus not the capacitance of any of these terms.
Writes ../sim/results/sr560_nf_sources.json.
Usage: python sr560_nf_sources.py [zin] [noise]   (default both)
"""
from __future__ import annotations

import dataclasses
import glob
import json
import math
import sys

import numpy as np

import models
import nf_map as NM
import spice
import sr560_chain as SR

F_AT = (1e4, 1e5, 1e6)
OUT = spice.RESULTS / "sr560_nf_sources.json"


def zin(key: str) -> dict:
    runs, model_edit = NM.sr560_model(key)
    with NM.sr560_context(key):
        s = NM.sr560_setting(runs, model_edit)
        src = "VIN ina0 0 DC 0\nRSA ina0 ina 1e12 rnl\nIA 0 ina DC 0 AC 1\nRSB 0 inb 1 rnl\n"
        ctl = ".control\n" + spice.WR + "op\nac dec 40 1k 30meg\nwrdata zin.txt v(ina)\n.endc\n"
        folder = SR._op(f"{runs}/zin", lambda ns: SR.deck(dataclasses.replace(s, nodeset=ns), f"sr560 zin {s.tag}",
                                                          src, ctl), [s.nodeset, None, ""], model_edit)
    d = spice.read_table(folder / "zin.txt")
    f, v = d["frequency"], d["v(ina)"]
    y = 1 / v - 1e-12
    c, g = y.imag / (2 * np.pi * f), y.real - 1e-8
    out = {}
    for f0 in (1e3,) + F_AT + (1e7,):
        j = int(np.argmin(np.abs(np.log10(f) - np.log10(f0))))
        out[str(f0)] = dict(c_in_pf=float(c[j] * 1e12), g_without_r101_us=float(g[j] * 1e6))
    return out


def group(name: str) -> str:
    n = name[len("onoise_"):]
    dev = n.split("_")[0]
    for side in ("a", "b"):
        if n == f"j.xj{side}.j1_id":
            return f"JFET {side.upper()}, channel"
        if n.startswith(f"r.xj{side}.rx"):
            return f"JFET {side.upper()}, gate resistor RX"
    if ".xja." in n or ".xjb." in n:
        return "input pair, other"
    if ".xu103." in n or dev in ("r125", "r127", "r129", "r130"):
        return "tail servo"
    if dev in ("r101", "r102"):
        return "input resistors"
    if ".xu102." in n:
        return "U102"
    return "rest"


def noise(key: str) -> dict:
    folder = NM.SR560_MODELS[key][0]
    rows, gens = [], None
    for rs in NM.RS:
        found = glob.glob(str(spice.RUNS / "nf_map" / folder / NM.rs_name(rs) / "*" / "noise"))
        assert len(found) == 1, found
        nz = spice.read_noise(spice.Path(found[0]))
        f = nz["frequency"]
        idx = [int(np.argmin(np.abs(f - f0))) for f0 in F_AT]
        gain = nz["onoise_spectrum"][idx] / nz["inoise_spectrum"][idx]
        if gens is None:
            gens = sorted(n for n in nz if n.startswith("onoise_") and n != "onoise_spectrum"
                          and "_" in n[len("onoise_"):].split(".")[-1])
        rows.append((nz["inoise_spectrum"][idx] ** 2, {n: (nz[n][idx] / gain) ** 2 for n in gens}))
    total = np.array([r[0] for r in rows])                       # rows: R_S, columns: F_AT
    coef_total, _ = NM.two_port(NM.RS, total)
    sums = {gname: np.zeros((len(NM.RS), len(F_AT))) for gname in
            ("JFET A, channel", "JFET A, gate resistor RX", "JFET B, channel", "JFET B, gate resistor RX",
             "input pair, other", "tail servo", "input resistors", "U102", "rest")}
    for n in gens:
        sums[group(n)] += np.array([r[1][n] for r in rows])
    sum_coef = np.zeros_like(coef_total)
    out = dict(groups={}, sum_check={})
    for gname, va2 in sums.items():
        coef, dev = NM.two_port(NM.RS, np.maximum(va2, 1e-60))
        sum_coef += coef
        out["groups"][gname] = {str(f0): dict(e_n=float(math.sqrt(max(coef[0, j], 0))),
                                              i_n=float(math.sqrt(max(coef[2, j], 0))),
                                              c_eff_pf=float(math.sqrt(max(coef[2, j], 0) / max(coef[0, j], 1e-300))
                                                             / (2 * math.pi * f0) * 1e12),
                                              fit_dev_db=dev)
                                for j, f0 in enumerate(F_AT)}
    for j, f0 in enumerate(F_AT):
        out["sum_check"][str(f0)] = dict(i_n_total=float(math.sqrt(coef_total[2, j])),
                                         i_n_sum_of_groups=float(math.sqrt(sum_coef[2, j])),
                                         e_n_total=float(math.sqrt(coef_total[0, j])),
                                         e_n_sum_of_groups=float(math.sqrt(sum_coef[0, j])))
    return out


def c_gs_plus_c_gd(key: str) -> dict:
    """JFET A's C_gs and C_gd at the trimmed operating point (pF): the card's zero-bias values (sim/models/_lib/
    jfets.lib, the wrapper's model) and C = C0 / sqrt(1 - V / PB), with V_GS = V(ina) - V(sa) and V_GD = V(ina) -
    V(da) from the trimmed deck's log (RX, RD and RS carry no DC current to speak of)."""
    import re
    part = {"SR560": "2N5564", "SR560_LSK389B": "LSK389B_LIS"}[key]
    lib = (spice.ROOT / "sim" / "models" / "_lib" / "jfets.lib").read_text(encoding="utf-8")
    card = re.search(rf"^\.model {part}_M NJF\((.*)\)$", lib, re.M | re.I).group(1)
    val = {k.lower(): float(v) for k, v in re.findall(r"(\w+)=([-+0-9.eE]+)", card)}
    log = glob.glob(str(spice.RUNS / "nf_map" / NM.SR560_MODELS[key][0] / "*" / "trimmed" / "run.log"))
    assert len(log) == 1, log
    text = open(log[0], encoding="utf-8").read()
    v = {n: float(re.search(rf"stdout {n} = ([-+0-9.eE]+)", text).group(1)) for n in ("ina", "sa", "da")}
    vgs, vgd = v["ina"] - v["sa"], v["ina"] - v["da"]
    pb = val["pb"]
    cgs, cgd = val["cgs"] / math.sqrt(1 - vgs / pb), val["cgd"] / math.sqrt(1 - vgd / pb)
    return dict(part=part, v_gs=vgs, v_gd=vgd, c_gs_pf=cgs * 1e12, c_gd_pf=cgd * 1e12, sum_pf=(cgs + cgd) * 1e12)


def main(args: list[str]) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    what = args or ["zin", "noise"]
    res = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    for key in NM.SR560_MODELS:
        res.setdefault(key, {})
        if "zin" in what:
            res[key]["zin"] = zin(key)
        if "noise" in what:
            res[key]["noise"] = noise(key)
            res[key]["jfet_a_capacitance"] = c_gs_plus_c_gd(key)
        print(f"== {key}")
        for f0, row in res[key].get("zin", {}).items():
            print(f"  C_in at {float(f0):>8g} Hz: {row['c_in_pf']:7.2f} pF, G without R101 {row['g_without_r101_us']:.3g} uS")
        if "jfet_a_capacitance" in res[key]:
            c = res[key]["jfet_a_capacitance"]
            print(f"  JFET A ({c['part']}): V_GS {c['v_gs']:.3f} V, V_GD {c['v_gd']:.3f} V, C_gs {c['c_gs_pf']:.2f} + C_gd "
                  f"{c['c_gd_pf']:.2f} = {c['sum_pf']:.2f} pF")
        nz = res[key].get("noise", {})
        for f0, row in nz.get("sum_check", {}).items():
            print(f"  {float(f0):>8g} Hz: i_n total {row['i_n_total'] * 1e15:7.1f} fA, sum of groups "
                  f"{row['i_n_sum_of_groups'] * 1e15:7.1f} fA; e_n total {row['e_n_total'] * 1e9:.3f} nV, sum "
                  f"{row['e_n_sum_of_groups'] * 1e9:.3f} nV")
            for gname, g in nz["groups"].items():
                r = g[f0]
                print(f"      {gname:20s} e_n {r['e_n'] * 1e9:7.3f} nV  i_n {r['i_n'] * 1e15:8.1f} fA  "
                      f"C_eff {r['c_eff_pf']:9.2f} pF")
    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main(sys.argv[1:])
