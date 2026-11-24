"""Noise-figure maps: the noise figure against source resistance and frequency, in the format of the SR560 data
sheet's plot (sr560_nf_datasheet.py), for H (mode H_LN) and L at a total gain of 1000 and for two SR560 models
in the low-noise mode at a gain of 1000, offset trimmed as in sr560_chain.py: the reproduction as drawn, with the
NPD5564 of the manual (key SR560; sr560_chain.py), and the corrected model with the LSK389B of newer units (key
SR560_LSK389B; sr560_variants.py's deck edit "corrected_lsk389b").  The LSK389B model's decks (its offset trim
and its 41 noise runs) run with abstol = 1e-12 A instead of the project's 1e-15 A: with 1e-15 A the operating
point of its 1 kOhm deck failed Newton, dynamic and true gmin stepping and source stepping, and ngspice's
transient-op fallback then crawled (stopped after 10 minutes at 35 %); with 1e-12 A, the first rung of
frontend.op_checked's ladder, the same deck converges at once.  The archived check below (its 1 ohm run against
sr560_variants.py's run at 1e-15 A) bounds the change in the noise.

As in the data sheet and in noise_vs_source.py, the source is a resistor R_S in series with input A, input B is
grounded, and the input networks are included (chain.INPUT_NET; the SR560's 100 Mohm input resistors).  Unlike
noise_vs_source.py, the source resistor is noiseless (model rnl), so ngspice's input-referred noise (the output
noise over the gain from the source's EMF) is the amplifier's alone, v_a^2; the noise figure is referred to the
standard temperature T0 = 290 K of the data sheet's plot:

    F = 1 + v_a^2 / (4 k T0 R_S).

(noise_vs_source.py and Table 10 take the source's noise at the simulator's 300.15 K, F = v_n^2 / (4 k 300.15 K
R_S) with v_n^2 = v_a^2 + 4 k 300.15 K R_S; "table10_check" below compares the two runs on that basis.)

R_S: 1 ohm to 100 Mohm, five values per decade (41 runs per amplifier).  Two checks are recorded:
  two_port_fit   for a linear noisy two-port driven from a real source impedance, v_a^2 = S_e + R_S S_x + R_S^2 S_i
                 at each frequency, with S_e = |e_n|^2, S_i = |i_n|^2 and S_x = 2 Re(e_n i_n*) (the equivalent input
                 generators and their correlation, the noiseless input impedance included in them).  Fitted at
                 each frequency to the 41 runs: the largest deviation of a run from the fit, in dB of noise figure,
                 over the maps' band, 1 Hz to 10 MHz (BAND).  Above it the SR560 models' gain from the source
                 falls so far (their bandwidth is about 1 MHz) that their input-referred noise is not a property
                 of a two-port: the LSK389B model's runs depart from any fit above 18 MHz.
                 The fit also gives the optimum source resistance sqrt(S_e / S_i) and the minimum noise figure.
  table10_check  the runs at the resistances of Table 10 against noise_vs_source.json, at 300.15 K.
  archived_check (the SR560 models) the 1 ohm run, whose deck is the model's archived noise deck, against the
                 archived spectrum (sr560_chain_noise_LN_1000.npz; sr560_variants_corrected_lsk389b_noise_LN_1000.npz):
                 the largest difference in dB of noise power.
And for the SR560 models ("low_frequency", from the 1 ohm run; for the data sheet from its fit): e_n at 1, 10 and
100 Hz, 1 kHz and 100 kHz; the 1/f corner f (e_n^2 - e_w^2) / e_w^2 at 10 Hz, 100 Hz and 1 kHz, with e_w the
100 kHz value; and the share of the output noise from the input JFETs' flicker generators (ngspice's generators of
the subcircuits XJA and XJB whose names end in _1overf).  Also ("tail_servo_share_rs_1e6"), with a 1 Mohm source at
10 kHz, 100 kHz and 1 MHz, the share of the output noise from the pair's tail servo: U103 (its subcircuit's
generators) and R125, R127, R129 and R130 (sr560_frontend.py); and the same share with the source balanced
("balanced_...": 1 Mohm, noiseless, also from input B to ground; one more run per model), where the servo's noise
is common mode at both gates.
Against the SR560 data sheet ("vs_datasheet"; its plot as a two-port fit, sr560_nf_datasheet.json, on the same
frequency grid from 1 Hz to 1 MHz): the difference in noise figure, amplifier minus data sheet, over the data
sheet's plane (1 Hz to 1 MHz, 1 ohm to 100 Mohm, 0.01 decade of R_S): its extremes, and the fractions of the
plane (in log f and log R_S) where the amplifier is lower by more than 0.1 dB, within 0.1 dB, or higher; and at
10 Hz, 1 kHz, 100 kHz and 1 MHz the resistances where each has 1 and 3 dB, and its minimum noise figure.
Writes ../sim/results/nf_map.npz (f_<key>, va2_<key> [V^2/Hz, one row per R_S], coef_<key> [S_e, S_x, S_i at each
frequency], rs) and nf_map.json.
Usage: python nf_map.py [H] [L] [SR560] [SR560_LSK389B]   (runs the named amplifiers, default all four, then
                                                           the summary)
       python nf_map.py balanced           (only the balanced-source run of each SR560 model, then the summary)
       python nf_map.py summary            (the summary from the saved nf_map.npz, without running ngspice)
"""
from __future__ import annotations

import contextlib
import json
import sys
import time

import numpy as np

import chain
import models
import spice
import sr560_chain as SR

K_B = 1.380649e-23
T0 = 290.0
RS = np.array([10 ** (k / 5) for k in range(41)])          # 1 ohm to 100 Mohm, five per decade
F_REPORT = (10.0, 1e3, 1e5, 1e6, 1e7)
BAND = (1.0, 1e7)                                           # the maps' frequency range (Figure 14)


def rs_name(rs: float) -> str:
    return f"rs_{rs:.4g}".replace("+", "")


def run_chain(mode: str, rs: float) -> tuple[np.ndarray, np.ndarray]:
    """H (H_LN) or L at a gain of 1000, R_S noiseless in series with input A, input B grounded through 1 mOhm."""
    s = chain.allocate(1000, mode)
    src = f"VIN ina 0 DC 0 AC 1\nRIA ina ga {rs:.6g} rnl\nRIB 0 gb 1m rnl\n"
    folder = spice.check_dc(spice.run(f"nf_map/{s.tag}/{rs_name(rs)}",
                                      chain.deck(s, f"nf map {s.tag} R_S {rs:.6g}", src,
                                                 spice.noise_control("out", "VIN", 0.1, 100e6, 20))))
    nz = spice.read_noise(folder)
    return nz["frequency"], nz["inoise_spectrum"] ** 2


KEYS = ("H", "L", "SR560", "SR560_LSK389B")
# the SR560 models: runs folder under nf_map/, sr560_variants.py's model (None: as drawn), archived noise run,
# abstol of their decks (None: spice.OPTIONS as it is, 1e-15 A)
SR560_MODELS = {"SR560": ("sr560", None, "sr560_chain_noise_LN_1000.npz", None),
                "SR560_LSK389B": ("sr560_lsk389b", "corrected_lsk389b",
                                  "sr560_variants_corrected_lsk389b_noise_LN_1000.npz", 1e-12)}


def sr560_model(key: str):
    """(runs folder, deck edit or None) of a SR560 model."""
    folder, model, _, _ = SR560_MODELS[key]
    if model is None:
        return f"nf_map/{folder}", None
    import sr560_variants as V
    subs, _ = V.opamp_dynamics()
    return f"nf_map/{folder}", V.edits(model, subs)[0]


def sr560_setting(runs: str, model_edit):
    return SR.trimmed(SR.allocate(1000, "LN"), 1000, runs=runs, edit=model_edit)


def run_sr560(s, rs: float, runs: str, model_edit) -> tuple[np.ndarray, np.ndarray]:
    """A SR560 model's noise deck (sr560_chain.run_noise, with the model's edit) with its 1-ohm source resistor
    RSA set to R_S."""
    def edit(text: str) -> str:
        old = "RSA ina0 ina 1 rnl\n"
        assert text.count(old) == 1, "source resistor not found once"
        text = text.replace(old, f"RSA ina0 ina {rs:.6g} rnl\n")
        return model_edit(text) if model_edit else text
    r = SR.run_noise(s, runs=f"{runs}/{rs_name(rs)}", edit=edit)
    return r["f"], r["inn"] ** 2


def sr560_context(key: str):
    """The options in force for a SR560 model's decks (its abstol)."""
    abstol = SR560_MODELS[key][3]
    return spice.options_replaced("abstol=1e-15", f"abstol={abstol:g}") if abstol else contextlib.nullcontext()


def run_balanced(key: str) -> None:
    """A SR560 model's noise deck with 1 Mohm (noiseless) in series with input A and from input B to ground."""
    with sr560_context(key):
        runs, model_edit = sr560_model(key)
        s = sr560_setting(runs, model_edit)

        def edit(text: str) -> str:
            for old, new in (("RSA ina0 ina 1 rnl\n", "RSA ina0 ina 1e+06 rnl\n"),
                             ("RSB 0 inb 1 rnl\n", "RSB 0 inb 1e+06 rnl\n")):
                assert text.count(old) == 1, old
                text = text.replace(old, new)
            return model_edit(text) if model_edit else text
        SR.run_noise(s, runs=f"{runs}/balanced_{rs_name(1e6)}", edit=edit)


def low_frequency(f: np.ndarray, e: np.ndarray) -> dict:
    """e_n at 1, 10, 100 Hz, 1 kHz and 100 kHz, and the 1/f corner f (e^2 - e_w^2) / e_w^2 at 10 Hz, 100 Hz and
    1 kHz with e_w = e(100 kHz); f and e (V/rtHz) on a grid that has these frequencies."""
    def at(f0):
        j = int(np.argmin(np.abs(np.log10(f) - np.log10(f0))))
        assert abs(f[j] / f0 - 1) < 1e-6, (f[j], f0)
        return float(e[j])
    ew = at(1e5)
    return dict(e_n={str(f0): at(f0) for f0 in (1.0, 10.0, 100.0, 1e3, 1e5)},
                corner_hz={str(f0): f0 * (at(f0) ** 2 - ew ** 2) / ew ** 2 for f0 in (10.0, 100.0, 1e3)})


def sr560_checks(key: str, f: np.ndarray, va2: np.ndarray) -> dict:
    """archived_check and low_frequency (with the JFETs' flicker share) of a SR560 model, from its 1 ohm run."""
    import glob
    folder, _, archived, _ = SR560_MODELS[key]
    assert RS[0] == 1.0
    arch = np.load(spice.RESULTS / archived)
    assert np.allclose(arch["f"], f, rtol=1e-9)
    diff = float(np.abs(10 * np.log10(va2[0] / arch["inn"] ** 2)).max())
    out = dict(archived_check=dict(file=archived, max_abs_diff_db=diff),
               low_frequency=low_frequency(f, np.sqrt(va2[0])))
    found = glob.glob(str(spice.RUNS / "nf_map" / folder / rs_name(1.0) / "*" / "noise"))
    assert len(found) == 1, found
    nz = spice.read_noise(spice.Path(found[0]))
    flick = [n for n in nz if n.startswith("onoise_") and (".xja." in n or ".xjb." in n) and n.endswith("_1overf")]
    share = {}
    for f0 in (10.0, 100.0, 1e3, 1e4):
        k = int(np.argmin(np.abs(nz["frequency"] - f0)))
        share[str(f0)] = float(sum(nz[n][k] ** 2 for n in flick) / nz["onoise_spectrum"][k] ** 2)
    out["low_frequency"]["jfet_flicker_share"] = share
    out["low_frequency"]["flicker_generators"] = sorted(n[7:] for n in flick)
    for name, sub in (("tail_servo_share_rs_1e6", rs_name(1e6)), ("balanced_tail_servo_share_rs_1e6",
                                                                 f"balanced_{rs_name(1e6)}")):
        found = glob.glob(str(spice.RUNS / "nf_map" / folder / sub / "*" / "noise"))
        assert len(found) == 1, found
        nz = spice.read_noise(spice.Path(found[0]))
        # leaf generators only (a device's total is listed beside its parts): the last name component has a suffix
        leaves = [n for n in nz if n.startswith("onoise_") and n != "onoise_spectrum" and "_" in n[7:].split(".")[-1]]
        servo = [n for n in leaves if ".xu103." in n or n[7:].split("_")[0] in ("r125", "r127", "r129", "r130")]
        share = {}
        for f0 in (1e4, 1e5, 1e6):
            k = int(np.argmin(np.abs(nz["frequency"] - f0)))
            share[str(f0)] = float(sum(nz[n][k] ** 2 for n in servo) / nz["onoise_spectrum"][k] ** 2)
        out[name] = share
    return out


def nf_db(va2: np.ndarray, rs: np.ndarray, t: float = T0) -> np.ndarray:
    """Noise figure (dB) from the amplifier's input-referred noise va2 (rows: rs)."""
    return 10 * np.log10(1 + va2 / (4 * K_B * t * rs[:, None]))


def two_port(rs: np.ndarray, va2: np.ndarray, f: np.ndarray | None = None) -> tuple[np.ndarray, float]:
    """S_e, S_x, S_i at each frequency (columns), fitted to va2 (rows: rs) with relative weights; and the largest
    deviation of a run from the fit, in dB of noise figure at T0 (with f given: over BAND only)."""
    a = np.stack([np.ones_like(rs), rs, rs ** 2], axis=1)
    coef = np.empty((3, va2.shape[1]))
    for j in range(va2.shape[1]):
        w = 1 / va2[:, j]
        aw = a * w[:, None]
        scale = np.linalg.norm(aw, axis=0)          # the columns span 16 decades: scale them to unit norm
        coef[:, j] = np.linalg.lstsq(aw / scale, va2[:, j] * w, rcond=None)[0] / scale
    fit = a @ coef
    dev = np.abs(nf_db(fit, rs) - nf_db(va2, rs))
    if f is not None:
        dev = dev[:, (f >= BAND[0] * (1 - 1e-9)) & (f <= BAND[1] * (1 + 1e-9))]
    return coef, float(dev.max())


def crossings(coef: np.ndarray, level_db: float) -> tuple[float, ...]:
    """The source resistances where the fitted noise figure equals level_db: (low side, high side), or () where
    the noise figure stays above level_db."""
    s_e, s_x, s_i = coef
    g = (10 ** (level_db / 10) - 1) * 4 * K_B * T0
    # S_i R^2 + (S_x - g) R + S_e = 0
    disc = (s_x - g) ** 2 - 4 * s_i * s_e
    if s_i <= 0 or disc <= 0:
        return ()
    r1 = ((g - s_x) - np.sqrt(disc)) / (2 * s_i)
    r2 = ((g - s_x) + np.sqrt(disc)) / (2 * s_i)
    return tuple(float(r) for r in (r1, r2) if r > 0)


def nf_fit_db(coef: np.ndarray, r: np.ndarray) -> np.ndarray:
    """Noise figure (dB) of fitted two-ports (columns of coef) at the resistances r (rows)."""
    va2 = coef[0][None, :] + r[:, None] * coef[1][None, :] + r[:, None] ** 2 * coef[2][None, :]
    return nf_db(va2, r)


def datasheet() -> tuple[np.ndarray, np.ndarray]:
    """The SR560 data sheet's plot as a two-port fit: log10 f and the coefficients (3 x n)."""
    d = json.loads((spice.RESULTS / "sr560_nf_datasheet.json").read_text(encoding="utf-8"))["two_port_fit"]
    return np.array(d["log10_f"]), np.array([d["S_e"], d["S_x"], d["S_i"]])


def vs_datasheet(f: np.ndarray, coef: np.ndarray) -> dict:
    """The amplifier (fitted two-port at frequencies f) against the data sheet's plot, on its plane."""
    lf_ds, coef_ds = datasheet()
    idx = [int(np.flatnonzero(np.abs(np.log10(f) - x) < 1e-6)[0]) for x in lf_ds]
    r = 10 ** np.round(np.arange(801) / 100, 2)                  # 1 ohm to 100 Mohm, 0.01 decade
    diff = nf_fit_db(coef[:, idx], r) - nf_fit_db(coef_ds, r)     # rows: r, columns: frequency
    lo, hi = np.unravel_index(diff.argmin(), diff.shape), np.unravel_index(diff.argmax(), diff.shape)
    worse = diff > 0.1
    box = None
    if worse.any():
        rows, cols = np.nonzero(worse)
        box = dict(f_hz=[float(10 ** lf_ds[cols.min()]), float(10 ** lf_ds[cols.max()])],
                   r_ohm=[float(r[rows.min()]), float(r[rows.max()])])
    # where the difference changes sign, at the reporting frequencies (log-linear interpolation in R_S)
    cross = {}
    for f0 in F_REPORT:
        j = np.flatnonzero(np.abs(lf_ds - np.log10(f0)) < 1e-6)
        if not len(j):
            continue
        d = diff[:, j[0]]
        k = np.flatnonzero(np.sign(d[:-1]) * np.sign(d[1:]) < 0)
        cross[str(f0)] = [float(10 ** (np.log10(r[i]) + d[i] / (d[i] - d[i + 1]) * 0.01)) for i in k]
    return dict(min_db=dict(value=float(diff[lo]), f_hz=float(10 ** lf_ds[lo[1]]), r_ohm=float(r[lo[0]])),
                max_db=dict(value=float(diff[hi]), f_hz=float(10 ** lf_ds[hi[1]]), r_ohm=float(r[hi[0]])),
                fraction_lower=float((diff < -0.1).mean()), fraction_within_0p1=float((np.abs(diff) <= 0.1).mean()),
                fraction_higher=float(worse.mean()), higher_region_bounds=box, equal_at_r_ohm=cross)


def datasheet_at() -> dict:
    """The data sheet's plot (two-port fit) at the reporting frequencies: as summary()'s rows."""
    lf, coef = datasheet()
    out = {}
    for f0 in F_REPORT:
        if np.log10(f0) > lf.max() + 1e-9:
            continue
        j = int(np.argmin(np.abs(lf - np.log10(f0))))
        out[str(f0)] = level_row(coef[:, j])
    return out


def level_row(c: np.ndarray) -> dict:
    s_e, s_x, s_i = c
    f_min = 1 + (2 * np.sqrt(s_e * s_i) + s_x) / (4 * K_B * T0)
    row = dict(e_n=float(np.sqrt(s_e)), i_n=float(np.sqrt(s_i)), corr=float(s_x / (2 * np.sqrt(s_e * s_i))),
               r_opt=float(np.sqrt(s_e / s_i)), nf_min_db=float(10 * np.log10(f_min)))
    for lv in (0.5, 1.0, 3.0):
        row[f"below_{lv:g}dB"] = list(crossings(c, lv))
    return row


def summary(f: np.ndarray, va2: np.ndarray) -> dict:
    coef, dev = two_port(RS, va2, f)
    out = dict(two_port_fit_max_dev_db=dev, two_port_fit_band_hz=list(BAND), at={}, coef=coef)
    for f0 in F_REPORT:
        if f0 > f.max():
            continue
        j = int(np.argmin(np.abs(np.log10(f) - np.log10(f0))))
        assert abs(f[j] / f0 - 1) < 1e-6, (f[j], f0)
        out["at"][str(f0)] = level_row(coef[:, j])
    out["vs_datasheet"] = vs_datasheet(f, coef)
    return out


def input_network(key: str, at: dict) -> dict:
    """H's and L's noise current at 100 kHz, 1 MHz and 10 MHz against that of their input networks' resistors
    (chain.INPUT_NET), at the simulator's 300.15 K: the damping resistor R_Z through C_Z, sqrt(4kT Re Y_Z) with
    Re Y_Z = w^2 C_Z^2 R_Z / (1 + w^2 C_Z^2 R_Z^2), and the bias resistor, sqrt(4kT / R_bias); and the share of the
    output noise that ngspice attributes to input A's R_Z (generator rza) with sources of 1 kOhm and 100 kOhm."""
    net = chain.INPUT_NET[key]
    s = chain.allocate(1000, {"H": "H_LN", "L": "L"}[key])
    runs = {rs: spice.read_noise(spice.RUNS / f"nf_map/{s.tag}/{rs_name(rs)}") for rs in (1e3, 1e5)}
    out = {}
    for f0 in (1e5, 1e6, 1e7):
        w = 2 * np.pi * f0
        re_y = w ** 2 * net["cz"] ** 2 * net["rz"] / (1 + (w * net["cz"] * net["rz"]) ** 2)
        row = dict(i_n=at[str(f0)]["i_n"], i_rz=float(np.sqrt(4 * spice.KT * re_y)),
                   i_bias=float(np.sqrt(4 * spice.KT / net["rbias"])))
        for rs, nz in runs.items():
            k = int(np.argmin(np.abs(nz["frequency"] - f0)))
            row[f"rza_share_of_output_noise_rs_{rs:g}"] = float(nz["onoise_rza"][k] ** 2 / nz["onoise_spectrum"][k] ** 2)
        out[str(f0)] = row
    return out


def table10_check(f: np.ndarray, va2: np.ndarray, mode: str) -> dict:
    """NF at 300.15 K from these runs against noise_vs_source.json (noisy source), at the common resistances."""
    t10 = json.loads((spice.RESULTS / "noise_vs_source.json").read_text(encoding="utf-8"))[mode]
    worst, n = 0.0, 0
    for row in t10:
        k = np.flatnonzero(np.abs(RS / row["rs"] - 1) < 1e-9)
        if not len(k):
            continue
        for fk, nf in row["nf_db"].items():
            va = spice.at(f, np.sqrt(va2[k[0]]), float(fk))
            mine = 10 * np.log10(1 + va ** 2 / (4 * spice.KT * row["rs"]))
            worst = max(worst, abs(mine - nf))
            n += 1
    return dict(points=n, max_abs_diff_db=worst)


def main(args: list[str]) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    keys = [] if args[:1] in (["summary"], ["balanced"]) else [a for a in args if a in KEYS] or list(KEYS)
    if args[:1] == ["balanced"]:
        for key in SR560_MODELS:
            run_balanced(key)
    npz = spice.RESULTS / "nf_map.npz"
    data = dict(np.load(npz)) if npz.exists() else {}
    for key in keys:
        t0 = time.time()
        rows, f = [], None
        with (sr560_context(key) if key in SR560_MODELS else contextlib.nullcontext()):
            if key in SR560_MODELS:
                runs, model_edit = sr560_model(key)
                s = sr560_setting(runs, model_edit)
            for rs in RS:
                fr, va2 = (run_sr560(s, rs, runs, model_edit) if key in SR560_MODELS
                           else run_chain({"H": "H_LN", "L": "L"}[key], rs))
                assert f is None or np.array_equal(fr, f)
                f = fr
                rows.append(va2)
                print(f"{key} R_S {rs:10.4g}: v_a(1 kHz) {spice.at(f, np.sqrt(va2), 1e3) * 1e9:8.3f} nV/rtHz  "
                      f"({time.time() - t0:5.0f} s)", flush=True)
        if key in SR560_MODELS:
            run_balanced(key)
        data[f"f_{key}"], data[f"va2_{key}"] = f, np.array(rows)
        data["rs"] = RS
        np.savez(npz, **data)
    res = dict(t0_kelvin=T0, rs_per_decade=5, rs_range=[float(RS[0]), float(RS[-1])],
               setting=dict(H=chain.allocate(1000, "H_LN").tag, L=chain.allocate(1000, "L").tag,
                            SR560=SR.allocate(1000, "LN").tag, SR560_LSK389B=SR.allocate(1000, "LN").tag),
               datasheet=dict(at=datasheet_at()))
    lf_ds, coef_ds = datasheet()
    res["datasheet"]["low_frequency"] = low_frequency(10 ** lf_ds, np.sqrt(coef_ds[0]))

    def show(name, rows):
        for f0, row in rows.items():
            print(f"  {name:6s} {float(f0):>8g} Hz: e_n {row['e_n'] * 1e9:7.3f} nV, i_n {row['i_n'] * 1e15:9.3f} fA, "
                  f"corr {row['corr']:+.3f}, R_opt {row['r_opt']:9.3g}, NF_min {row['nf_min_db']:6.3f} dB, <1 dB "
                  f"[{', '.join(f'{v:.4g}' for v in row['below_1dB'])}], <3 dB "
                  f"[{', '.join(f'{v:.4g}' for v in row['below_3dB'])}]")

    show("sheet", res["datasheet"]["at"])
    for key in KEYS:
        if f"va2_{key}" not in data:
            continue
        f, va2 = data[f"f_{key}"], data[f"va2_{key}"]
        res[key] = summary(f, va2)
        data[f"coef_{key}"] = res[key].pop("coef")
        if key in SR560_MODELS:
            res[key].update(sr560_checks(key, f, va2))
        else:
            res[key]["table10_check"] = table10_check(f, va2, {"H": "H_LN", "L": "L"}[key])
            res[key]["input_network"] = input_network(key, res[key]["at"])
        print(f"{key}: two-port fit within {res[key]['two_port_fit_max_dev_db']:.2g} dB"
              + (f"; Table 10 check {res[key]['table10_check']}" if key not in SR560_MODELS else
                 f"; archived check {res[key]['archived_check']}; low frequency {res[key]['low_frequency']}"))
        show(key, res[key]["at"])
        for f0, row in res[key].get("input_network", {}).items():
            print(f"  input network {float(f0):g} Hz: i_n {row['i_n'] * 1e15:.0f} fA, R_Z {row['i_rz'] * 1e15:.0f} fA, bias "
                  f"{row['i_bias'] * 1e15:.1f} fA; R_Z's share of the output noise {row['rza_share_of_output_noise_rs_1000']:.1%}"
                  f" (1 kOhm), {row['rza_share_of_output_noise_rs_100000']:.1%} (100 kOhm)")
        v = res[key]["vs_datasheet"]
        print(f"  vs data sheet: from {v['min_db']} to {v['max_db']}; lower on {v['fraction_lower']:.1%}, within 0.1 dB "
              f"on {v['fraction_within_0p1']:.1%}, higher on {v['fraction_higher']:.1%} ({v['higher_region_bounds']})")
    np.savez(npz, **data)
    (spice.RESULTS / "nf_map.json").write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main(sys.argv[1:])
