"""Noise of the op-amp models quoted in Section 4.3.1 of the note (the low-voltage alternative) and in
Table 8 of Section 5.3 (the vendor models as published): the input voltage noise e_n and the
inverting-input current noise i_n- of each model, separated by two noise runs of one non-inverting
stage at two feedback resistances (the method of Section 5.3).

Fixture: OA_<part> (../sim/models/_lib/opamps.lib) as a non-inverting amplifier of gain
G = 1 + R_F / R_G (R_G = R_F / (G - 1)), every resistor noiseless (model rnl), the non-inverting
input driven through 1 mohm (AC ground for noise).  The inverting input sees R_F || R_G = R_F / G and
the noise gain is G, so the output noise density is
    v_o^2 = G^2 e_n^2 + (i_n- R_F)^2                                                  (1)
(the non-inverting input's current noise flows in 1 mohm: nothing).  Two runs, R_F1 < R_F2:
    i_n-^2 = (v_o2^2 - v_o1^2) / (R_F2^2 - R_F1^2)
    e_n^2  = (v_o1^2 - i_n-^2 R_F1^2) / G^2                                           (2)
at 10 Hz, 100 Hz, 1 kHz, 10 kHz and 100 kHz ('white': 100 kHz).  These are the values the note
quotes.  An AC run of each fixture gives its DC gain and -3 dB bandwidth.  (For a current-feedback
op amp, the THS3091, (1) holds as well: the loop holds the inverting input at the non-inverting
one, so i_n- flows through R_F.)

A model with a resistance R_d between its inputs (the ADI macromodels: RinDiff, 4 kohm in the
ADA4899, 5 Mohm in the ADA4817) gives e_n a larger noise gain, G_n = 1 + R_F / (R_G || R_d)
= G + R_F / R_d, while the signal gain stays G (the signal puts no voltage across R_d), so
    v_o^2 = (G + R_F / R_d)^2 e_n^2 + (i_n- R_F)^2                                    (3)
and (2) books part of e_n as current noise.  Solving (3) for the two runs (a 2 x 2 linear system in
e_n^2 and i_n-^2, with R_d read from the model file) gives the model's own generators; for R_d
infinite it is (2).  The ADA4899's values corrected this way (Eq. (3)) are also stored under
'ADA4899 corrected for R_d'.

  ADA4899  ADI model as published, +/-5 V, G = 5, R_F = 500 and 1000 ohm
  ADA4817  ADI model as published, +/-5 V, G = 5, R_F = 500 and 1000 ohm
  THS4021  TI model with its noise corrected (models.py: KF = 0, 1/f generators of 3.82 nV/rtHz and
           19.9 pA/rtHz at 10 Hz), +/-15 V, G = 10 (it is stable only at noise gains of about 10
           and more), R_F = 1 and 2 kohm; no explicit R_d (transistor input stage): (2) only
The ADA4817 has a FET input: with R_F of 1 kohm its current noise (fA/rtHz) is about 1e-4 of the
output noise power or less, below what two runs can separate (its i_n- from that pair is numerical
residue).  A second pair at G = 5, R_F = 1 and 10 Mohm, solved with (3), resolves it at 1 kHz; at
10 Hz the model's 1/f voltage noise still outweighs it by about 1e3 in power and the solution is
numerical residue (a negative share), and above a few kHz the input capacitance against
R_F || R_G changes the noise gain again.  The same pair's e_n agrees with the first pair's.

Table 8: the vendor models as published.  models.prepare_published_opamps() writes
../sim/models/_lib/opamps_published.lib from the vendor files (translated for ngspice exactly as
for opamps.lib, but without any noise correction): OA_<part>_PUB as published and OA_<part>_PUBKF0
with every KF of the file set to zero, which leaves the model's own white noise.  Fixtures:
  THS4021  TI SLOJ004 (1999)   +/-15 V, G = 10, R_F = 1 and 2 kohm
  THS4031  TI SLOJ005A         +/-15 V, G = 2,  R_F = 300 and 600 ohm (unity-gain stable)
  THS3091  TI SLOM418          +/-15 V, G = 5,  R_F = 1 and 2 kohm (current feedback)
  LM7171   TI SNOM205A         +/-15 V, G = 5,  R_F = 1 and 10 kohm (all its KF are 0, so the
                               published model is its own white-noise model: no KF-0 run)
Stored for each: e_n and i_n- at 10 Hz and at 100 kHz (published), the white levels e_n,w and
i_n,w (KF 0, at 100 kHz; for the LM7171 the published model at 100 kHz), and the 1/f corners at
f_0 = 10 Hz, for x = e_n and x = i_n-:
    f_c = f_0 (x(f_0) / x_w)^2                 (the note's approximation, valid for x >> x_w)
    f_c = f_0 ((x(f_0) / x_w)^2 - 1)           (exact for x^2 = x_w^2 (1 + f_c / f))
once with the model's own white level and once with the data sheet's (DATASHEET below, with its
pages); the data sheet's own corner is f_0 (x_DS(f_0) / x_DS,w)^2 likewise.

Two circuit runs with a published model, each against the same run with the corrected model:
  - the H front end at a gain of 100 (frontend.CASES['H100']) with OA_THS4021_PUB as its two loop op
    amps: the front end's input noise from 1 Hz to 10 kHz (noise run as frontend.check_noise; the
    run's own gain onoise/inoise at 1 kHz must equal the front end's gain within 5 %);
  - the complete chain (chain.py) at total gains of 1 and 10 (allocation H_LN), where the output
    stage S5 dominates, with OA_THS3091_PUB in S5: the input noise at 1 Hz and 10 Hz.
Each ratio is published / corrected at the same frequency.

Writes ../sim/results/opamp_noise_check.json.  Usage: python opamp_noise_check.py
"""
from __future__ import annotations

import json
import math
import re
import sys

import numpy as np

import models
import spice

FREQS = (10, 100, 1e3, 1e4, 1e5)
FIXTURES = {
    # label: (supply, gain, (R_F1, R_F2), frequencies at which the pair is valid)
    "ADA4899": (5.0, 5, (500.0, 1000.0), FREQS),
    "ADA4817": (5.0, 5, (500.0, 1000.0), FREQS),
    "THS4021": (15.0, 10, (1000.0, 2000.0), FREQS),
    "ADA4817 (R_F 1 and 10 Mohm)": (5.0, 5, (1e6, 1e7), (10, 1e3)),
}
PUB_FREQS = (10, 100, 1e3, 1e4, 1e5, 1e6)
PUBLISHED_FIXTURES = {
    # label: (part, wrapper suffix, supply, gain, (R_F1, R_F2))
    "THS4021 published": ("THS4021", "_PUB", 15.0, 10, (1000.0, 2000.0)),
    "THS4021 published, KF 0": ("THS4021", "_PUBKF0", 15.0, 10, (1000.0, 2000.0)),
    "THS4031 published": ("THS4031", "_PUB", 15.0, 2, (300.0, 600.0)),
    "THS4031 published, KF 0": ("THS4031", "_PUBKF0", 15.0, 2, (300.0, 600.0)),
    "THS3091 published": ("THS3091", "_PUB", 15.0, 5, (1000.0, 2000.0)),
    "THS3091 published, KF 0": ("THS3091", "_PUBKF0", 15.0, 5, (1000.0, 2000.0)),
    "LM7171 published": ("LM7171", "_PUB", 15.0, 5, (1000.0, 10000.0)),
}
# Data-sheet typical values (V/rtHz, A/rtHz; i: inverting input), with their pages.  Values at 10 Hz
# are read off the figures by eye.
DATASHEET = {
    "THS4021": dict(e_10=4.0e-9, i_10=18.6e-12, e_w=1.2e-9, i_w=2.3e-12,
                    src="SLOS265F: 10 Hz from Figs. 5-11 and 5-12, p. 11 (e_n read by eye; i_n read from the "
                        "pixels at the 10 Hz frame edge, 18.5-18.8 pA, where the reading by eye gave 20); "
                        "white from the electrical characteristics, p. 6 (f > 10 kHz)"),
    "THS4031": dict(e_10=4.0e-9, i_10=18.6e-12, e_w=1.2e-9, i_w=2.3e-12,
                    src="SLOS224L: 10 Hz from Figs. 5-13 and 5-14, p. 12 (e_n read by eye; i_n read from the "
                        "pixels at the 10 Hz frame edge, 18.5-18.8 pA, where the reading by eye gave 20); white from the "
                        "electrical characteristics, Sec. 5.6, p. 6 (f > 10 kHz: 1.2 nV, 2.3 pA; the 2.1 pA "
                        "read earlier off Fig. 5-14 at 100 kHz is replaced by the table's value)"),
    "THS3091": dict(e_10=6.5e-9, i_10=200e-12, e_w=1.1e-9, i_w=14e-12, i_w_noninv=15e-12,
                    src="SLOS423K: 10 Hz from Fig. 7-16, p. 12 (inverting input, read by eye); white from "
                        "Sec. 7.5, p. 6 (f > 10 kHz: 1.1 nV, 15 pA non-inverting, 14 pA inverting)"),
    "LM7171": dict(e_10=43e-9, i_10=None, e_w=8.5e-9, i_w=1e-12,
                   src="SNOS760D: white from Sec. 5.5, p. 5 (A grade, 10 kHz: 8.5 nV, 1 pA); 10 Hz from "
                       "Fig. 5-16, p. 10 (+/-5 V, read by eye)"),
}
# the values printed in Table 8 of the note, for comparison only
NOTE_TABLE7 = {"THS4021": dict(e_10=18.2e-9, i_10=293e-12), "THS4031": dict(e_10=22.2e-9, i_10=300e-12),
               "THS3091": dict(e_10=37e-9, i_10=317e-12, i_w=1.5e-12), "LM7171": dict(e_w=4.1e-9)}


def r_diff(part: str) -> float:
    """The resistance between the inputs in the model file (RinDiff), or infinity."""
    text = (models.VENDOR_DIR / models.VENDOR_OPAMPS[part]["file"]).read_text(encoding="latin-1")
    m = re.search(r"^\s*RinDiff\s+\S+\s+\S+\s+(?:Rideal\s+)?([-+0-9.eE]+)\s*$", text, re.M | re.I)
    return float(m.group(1)) if m else math.inf


def fixture(part: str, vs: float, gain: int, rf: float, wrapper: str | None = None,
            lib: str = "opamps.lib") -> str:
    """The deck of the two-gain fixture, with an operating point and an AC run as control block.
    wrapper: the subcircuit to use (default OA_<part>); lib: the library that defines it."""
    return (f"* {part} noise rf={rf}\n{spice.OPTIONS}.options rshunt=1e12\n"
            f"{spice.lib(lib)}.model rnl r(noisy=0)\n"
            f"VP vp 0 {vs:g}\nVM vm 0 {-vs:g}\nVIN in 0 DC 0 AC 1\nRS in i 1m rnl\n"
            f"X1 i n out vp vm {wrapper or 'OA_' + part}\n"
            f"RF out n {rf:g} rnl\nRG n 0 {rf / (gain - 1):g} rnl\n"
            ".control\nset wr_singlescale\nset wr_vecnames\nop\nprint v(out)\nac dec 20 1k 3g\n"
            "wrdata ac.txt v(out)\n.endc\n.end\n")


def two_gain_runs(label: str, part: str, vs: float, gain: int, rfs, freqs, run_tag: str,
                  wrapper: str | None = None, lib: str = "opamps.lib", rd: float = math.inf) -> dict:
    """The two fixture runs (AC and noise for each R_F) and the solution of (2) and (3)."""
    out, spec = {}, {}
    for rf in rfs:
        deck = fixture(part, vs, gain, rf, wrapper, lib)
        f = spice.run(f"checks/{run_tag}_ac_rf{rf:g}", deck)
        d = spice.read_table(f / "ac.txt")
        fr, h = d["frequency"], np.abs(d["v(out)"])
        f3 = fr[np.nonzero(h < h[0] / np.sqrt(2))[0][0]]
        deck2 = deck.replace("op\nprint v(out)\nac dec 20 1k 3g\nwrdata ac.txt v(out)\n.endc",
                             "noise v(out) VIN dec 10 1 1meg 1\nsetplot noise1\nwrdata noise.txt all\n.endc")
        f2 = spice.run(f"checks/{run_tag}_noise_rf{rf:g}", deck2)
        nz = spice.read_noise(f2)
        spec[rf] = (nz["frequency"], nz["onoise_spectrum"])
        out[f"R_F {rf:g}"] = dict(gain_dc=float(h[0]), f3db=float(f3), vout_dc=spice.printed(f, "v(out)"))
        print(f"{label} G={gain} RF={rf:g}: gain {h[0]:.3f}, f3dB {f3 / 1e6:.0f} MHz, "
              f"vout_dc {spice.printed(f, 'v(out)'):.4f}", flush=True)
    fr, o1 = spec[rfs[0]]
    _, o2 = spec[rfs[1]]
    # (2): the fixture's formula, as used for the note
    i2 = (o2 ** 2 - o1 ** 2) / (rfs[1] ** 2 - rfs[0] ** 2)
    e2 = (o1 ** 2 - i2 * rfs[0] ** 2) / gain ** 2
    # (3): with the model's resistance between its inputs
    a1, a2 = (gain + rfs[0] / rd) ** 2, (gain + rfs[1] / rd) ** 2
    b1, b2 = rfs[0] ** 2, rfs[1] ** 2
    det = a1 * b2 - a2 * b1
    e2d = (o1 ** 2 * b2 - o2 ** 2 * b1) / det
    i2d = (a1 * o2 ** 2 - a2 * o1 ** 2) / det
    print(f"   R_d (RinDiff) = {rd:g} ohm: noise gains {math.sqrt(a1):.4f}, {math.sqrt(a2):.4f} against G = {gain}")
    rows = {}
    for f0 in freqs:
        k = int(np.argmin(abs(fr - f0)))
        e_n, i_n = float(np.sqrt(max(e2[k], 0))), float(np.sqrt(max(i2[k], 0)))
        e_nd, i_nd = float(np.sqrt(max(e2d[k], 0))), float(np.sqrt(max(i2d[k], 0)))
        # the share of the output noise power that the current noise makes up in the larger-R_F run
        share = float(i2d[k] * rfs[1] ** 2 / o2[k] ** 2)
        rows[f"{f0:g}"] = dict(e_n=e_n, i_n=i_n, e_n_with_Rd=e_nd, i_n_with_Rd=i_nd, i_share_of_vo2=share)
        print(f"   {f0:>7g} Hz  Eq. (2): e_n {e_n * 1e9:7.3f} nV, i_n- {i_n * 1e12:9.4f} pA   "
              f"Eq. (3): e_n {e_nd * 1e9:7.3f} nV, i_n- {i_nd * 1e12:9.4f} pA   "
              f"(i_n- R_F2)^2 / v_o2^2 = {share:.2e}", flush=True)
    return dict(supply=vs, gain=gain, rf=list(rfs), r_diff=rd if math.isfinite(rd) else None,
                fixture_runs=out, noise=rows)


def two_gain(label: str) -> dict:
    vs, gain, rfs, freqs = FIXTURES[label]
    part = label.split()[0]
    tag = "" if label == part else "_hiR"
    return two_gain_runs(label, part, vs, gain, rfs, freqs, f"{part}{tag}", rd=r_diff(part))


def published(label: str) -> dict:
    part, suffix, vs, gain, rfs = PUBLISHED_FIXTURES[label]
    r = two_gain_runs(label, part, vs, gain, rfs, PUB_FREQS, f"{part}{suffix}", wrapper=f"OA_{part}{suffix}",
                      lib="opamps_published.lib")
    r.update(part=part, model=models.VENDOR_OPAMPS[part]["src"],
             variant="every KF set to 0" if suffix == "_PUBKF0" else "as published")
    return r


def corners(x0: float, xw: float, f0: float = 10.0) -> dict:
    """1/f corner from the density x0 at f0 and the white level xw: the note's approximation and the
    exact value (see the module docstring)."""
    if not xw or not x0:
        return dict(approx=None, exact=None)
    return dict(approx=f0 * (x0 / xw) ** 2, exact=f0 * ((x0 / xw) ** 2 - 1))


def table7(res: dict) -> dict:
    """Per part: the published model's e_n and i_n- at 10 Hz and 100 kHz, its own white levels (KF 0),
    the data sheet's values and the corners."""
    out = {}
    for part in models.PUBLISHED:
        pub = res["published"][f"{part} published"]["noise"]
        kf0 = res["published"].get(f"{part} published, KF 0", res["published"][f"{part} published"])["noise"]
        ds = DATASHEET[part]
        row = dict(model=models.VENDOR_OPAMPS[part]["src"],
                   e_n_10=pub["10"]["e_n"], i_n_10=pub["10"]["i_n"],
                   e_n_100k=pub["100000"]["e_n"], i_n_100k=pub["100000"]["i_n"],
                   e_n_1M=pub["1e+06"]["e_n"], i_n_1M=pub["1e+06"]["i_n"],
                   e_n_white_kf0=kf0["100000"]["e_n"], i_n_white_kf0=kf0["100000"]["i_n"],
                   e_n_white_kf0_10k=kf0["10000"]["e_n"], i_n_white_kf0_10k=kf0["10000"]["i_n"],
                   white_from="KF-0 model at 100 kHz" if f"{part} published, KF 0" in res["published"]
                   else "published model at 100 kHz (no KF in the file)",
                   datasheet=ds, note_table7=NOTE_TABLE7.get(part, {}))
        row["corner_e_model"] = corners(row["e_n_10"], row["e_n_white_kf0"])
        row["corner_i_model"] = corners(row["i_n_10"], row["i_n_white_kf0"])
        row["corner_e_model_vs_datasheet_white"] = corners(row["e_n_10"], ds["e_w"])
        row["corner_i_model_vs_datasheet_white"] = corners(row["i_n_10"], ds["i_w"])
        row["corner_i_model_100kHz_as_white"] = corners(row["i_n_10"], row["i_n_100k"])
        row["corner_e_datasheet"] = corners(ds["e_10"], ds["e_w"])
        row["corner_i_datasheet"] = corners(ds["i_10"], ds["i_w"]) if ds["i_10"] else dict(approx=None, exact=None)
        out[part] = row
        print(f"{part}: published e_n {row['e_n_10'] * 1e9:.2f} nV, i_n- {row['i_n_10'] * 1e12:.1f} pA at 10 Hz; "
              f"own white {row['e_n_white_kf0'] * 1e9:.3f} nV, {row['i_n_white_kf0'] * 1e12:.3f} pA; "
              f"i corner {row['corner_i_model']['approx'] / 1e3 if row['corner_i_model']['approx'] else float('nan'):.1f} kHz "
              f"(own white), data sheet {row['corner_i_datasheet']['approx'] or float('nan'):.0f} Hz", flush=True)
    return out


def _with_published(deck: str, replace_from: str | None = None, replace_to: str | None = None) -> str:
    """The deck with opamps_published.lib included after opamps.lib, and one subcircuit name
    swapped (each occurrence)."""
    inc = spice.lib("opamps.lib")
    assert inc in deck
    deck = deck.replace(inc, inc + spice.lib("opamps_published.lib"), 1)
    if replace_from:
        assert replace_from in deck, replace_from
        deck = deck.replace(replace_from, replace_to)
    return deck


def fe_published_ths4021() -> dict:
    """The H front end at a gain of 100 with the published THS4021 as its loop op amps, against the
    corrected THS4021 (see the module docstring)."""
    from dataclasses import replace
    import frontend as F
    out = {}
    base = F.CASES["H100"]
    ctl = (".control\n" + spice.WR + "noise v(oa,ob) VIN dec 20 0.1 1e6 1\nsetplot noise1\n"
           "wrdata noise.txt all\n.endc\n")
    for tag, opamp in (("corrected", "THS4021"), ("published", "THS4021_PUB")):
        p = replace(base, name=f"H100_ths4021_{tag}", opamp=opamp)
        deck = F.deck(p, f"noise {p.name}", F.SRC_NOISE, ctl)
        if opamp.endswith("_PUB"):
            deck = _with_published(deck)
        f = spice.run(f"checks/fe_H100_ths4021_{tag}", deck)
        nz = spice.read_noise(f)
        fr, inn, on = nz["frequency"], nz["inoise_spectrum"], nz["onoise_spectrum"]
        g1k = spice.at(fr, on / inn, 1e3)
        if abs(g1k / p.gain - 1) > 0.05:
            raise RuntimeError(f"{p.name}: noise run's gain {g1k:.2f} against {p.gain:.2f}")
        # contributions by group (frontend.noise_groups; the run's own gain onoise/inoise is |H|)
        grp = F.noise_groups(nz, on / inn)
        out[tag] = dict(opamp=f"OA_{opamp}", gain_1k=g1k,
                        en={f"{f0:g}": spice.at(fr, inn, f0) for f0 in (1, 10, 100, 1e3, 1e4)},
                        groups_10Hz={g: spice.at(fr, v, 10.0) for g, v in grp.items()})
        print(f"H100 front end, {tag} THS4021: " + ", ".join(f"{k} Hz {v * 1e9:.3f} nV" for k, v in out[tag]["en"].items())
              + f" (gain {g1k:.2f}); at 10 Hz: " + ", ".join(f"{g} {v * 1e9:.2f}" for g, v in out[tag]["groups_10Hz"].items()
                                                            if v > 0.05e-9), flush=True)
    out["ratio_published_to_corrected"] = {k: out["published"]["en"][k] / out["corrected"]["en"][k]
                                           for k in out["corrected"]["en"]}
    return out


def chain_published_ths3091(gains=(1, 10)) -> dict:
    """The complete chain at low total gains with the published THS3091 in S5, against the corrected one."""
    import chain
    out = {}
    src = "VIN ina 0 DC 0 AC 1\nRIA ina ga 1m rnl\nRIB 0 gb 1m rnl\n"      # as chain.run_noise (rs = 0)
    for g in gains:
        s = chain.allocate(g, "H_LN")
        row = dict(setting=s.tag, gain=s.gain)
        for tag in ("corrected", "published"):
            deck = chain.deck(s, f"chain noise {s.tag} THS3091 {tag}", src,
                              spice.noise_control("out", "VIN", 0.1, 1e6, 20))
            if tag == "published":
                deck = _with_published(deck, "OA_THS3091", "OA_THS3091_PUB")
            f = spice.run(f"checks/chain_{s.tag}_ths3091_{tag}", deck)
            nz = spice.read_noise(f)
            fr, inn = nz["frequency"], nz["inoise_spectrum"]
            row[tag] = {f"{f0:g}": spice.at(fr, inn, f0) for f0 in (1, 10, 100, 1e3, 1e4, 1e5)}
        row["ratio_published_to_corrected"] = {k: row["published"][k] / row["corrected"][k] for k in row["corrected"]}
        out[f"H_LN_{g}"] = row
        print(f"chain H_LN gain {g} ({s.tag}): 1 Hz {row['corrected']['1'] * 1e9:.1f} -> "
              f"{row['published']['1'] * 1e9:.1f} nV (x{row['ratio_published_to_corrected']['1']:.2f}), "
              f"10 Hz x{row['ratio_published_to_corrected']['10']:.2f}, 10 kHz "
              f"x{row['ratio_published_to_corrected']['10000']:.2f}", flush=True)
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    models.prepare_published_opamps()
    res = {label: two_gain(label) for label in FIXTURES}
    a, t = res["ADA4899"]["noise"], res["THS4021"]["noise"]
    hi = res["ADA4817 (R_F 1 and 10 Mohm)"]["noise"]
    summary = {
        "ADA4899 white (100 kHz): e_n nV, i_n- pA, Eq. (2)": (a["100000"]["e_n"] * 1e9, a["100000"]["i_n"] * 1e12),
        "ADA4899 10 Hz: e_n nV, i_n- pA, Eq. (2)": (a["10"]["e_n"] * 1e9, a["10"]["i_n"] * 1e12),
        "ADA4899 white (100 kHz): e_n nV, i_n- pA, Eq. (3)": (a["100000"]["e_n_with_Rd"] * 1e9,
                                                              a["100000"]["i_n_with_Rd"] * 1e12),
        "ADA4899 10 Hz: e_n nV, i_n- pA, Eq. (3)": (a["10"]["e_n_with_Rd"] * 1e9, a["10"]["i_n_with_Rd"] * 1e12),
        "ADA4817 white (100 kHz): e_n nV": res["ADA4817"]["noise"]["100000"]["e_n"] * 1e9,
        "ADA4817 10 Hz: e_n nV": res["ADA4817"]["noise"]["10"]["e_n"] * 1e9,
        "ADA4817 (R_F 1 and 10 Mohm, Eq. (3)) i_n- fA at 1 kHz (at 10 Hz not resolved)":
            hi["1000"]["i_n_with_Rd"] * 1e15,
        "ADA4817 (R_F 1 and 10 Mohm, Eq. (3)) e_n nV at 10 Hz, 1 kHz":
            (hi["10"]["e_n_with_Rd"] * 1e9, hi["1000"]["e_n_with_Rd"] * 1e9),
        "THS4021 (corrected) 10 Hz: e_n nV, i_n- pA": (t["10"]["e_n"] * 1e9, t["10"]["i_n"] * 1e12),
        "THS4021 (corrected) white (100 kHz): e_n nV, i_n- pA": (t["100000"]["e_n"] * 1e9, t["100000"]["i_n"] * 1e12),
    }
    # the ADA4899 model's own generators, corrected for its 4 kohm RinDiff (Eq. (3))
    res["ADA4899 corrected for R_d"] = dict(
        r_diff=res["ADA4899"]["r_diff"], equation="(3)",
        e_n_white_nV=a["100000"]["e_n_with_Rd"] * 1e9, i_n_white_pA=a["100000"]["i_n_with_Rd"] * 1e12,
        e_n_10Hz_nV=a["10"]["e_n_with_Rd"] * 1e9, i_n_10Hz_pA=a["10"]["i_n_with_Rd"] * 1e12,
        white_frequency_Hz=1e5)
    res["published"] = {label: published(label) for label in PUBLISHED_FIXTURES}
    res["table7"] = table7(res)
    res["H100 front end, published THS4021"] = fe_published_ths4021()
    res["chain, published THS3091"] = chain_published_ths3091()
    t7, fe, ch = res["table7"], res["H100 front end, published THS4021"], res["chain, published THS3091"]
    summary.update({
        "ADA4899 corrected for R_d: e_n white nV, i_n- white pA, i_n- 10 Hz pA": (
            res["ADA4899 corrected for R_d"]["e_n_white_nV"], res["ADA4899 corrected for R_d"]["i_n_white_pA"],
            res["ADA4899 corrected for R_d"]["i_n_10Hz_pA"]),
        **{f"{p} published 10 Hz: e_n nV, i_n- pA": (t7[p]["e_n_10"] * 1e9, t7[p]["i_n_10"] * 1e12)
           for p in models.PUBLISHED},
        **{f"{p} published white (KF 0, 100 kHz): e_n nV, i_n- pA": (t7[p]["e_n_white_kf0"] * 1e9,
                                                                    t7[p]["i_n_white_kf0"] * 1e12)
           for p in models.PUBLISHED},
        **{f"{p} published i_n- 1/f corner, f_0 (i_n(f_0)/i_n,w)^2 with its own white, Hz":
           t7[p]["corner_i_model"]["approx"] for p in models.PUBLISHED},
        "H100 front end 10 Hz: published THS4021 nV, corrected nV, ratio": (
            fe["published"]["en"]["10"] * 1e9, fe["corrected"]["en"]["10"] * 1e9,
            fe["ratio_published_to_corrected"]["10"]),
        **{f"chain {k} 1 Hz: published THS3091 nV, corrected nV, ratio": (
            v["published"]["1"] * 1e9, v["corrected"]["1"] * 1e9, v["ratio_published_to_corrected"]["1"])
           for k, v in ch.items()},
    })
    res["summary"] = summary
    print(json.dumps(summary, indent=1))
    (spice.RESULTS / "opamp_noise_check.json").write_text(json.dumps(res, indent=1), encoding="utf-8",
                                                          newline="\n")


if __name__ == "__main__":
    main()
