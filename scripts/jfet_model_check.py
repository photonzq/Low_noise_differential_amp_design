"""The calibrated JFET models against their data sheets (no design simulation).

For each calibrated part: the white input noise density (at 100 kHz, where the 1/f part is
negligible) and the density at 10 Hz against drain current, by ngspice on the subcircuit in
_lib/jfets.lib (RX included), next to the data sheets' typical values: the tables' points and the
curves of input-referred noise against drain current at 1 kHz, read by eye (figure numbers below).
Also I_DSS, V_GS and g_m at the data sheets' conditions.

Curve points (read by eye, nV/rtHz at 1 kHz, against I_D in mA):
  JFE150, SLPS732B Fig. 6-11 (V_DS = 5 V): 0.05: 2.65, 0.1: 2.25, 0.2: 1.72, 0.5: 1.3, 1: 1.05,
      2: 0.9, 3: 0.85, 5: 0.82, 7: 0.82, 10: 0.86, 20: 1.0
  JFE2140, SLPS730B Fig. 6-16 (V_DS = 10 V): 0.05: 3.3, 0.1: 2.6, 0.2: 1.9, 0.5: 1.5, 1: 1.3,
      2: 1.08, 3: 1.0, 5: 0.9, 10: 1.22

'calibration check': every calibrated part's subcircuit (RX and the calibrated KF) at its
calibration point (jfet_calibration.json: id, vds), simulated: the white density (100 kHz), the
density at the data sheet's white frequency f_w and low frequency f_lf, and at 10 Hz, against the
targets and against the closed forms of models.py (en_achieved_*).  For the LSBF862, whose card
alone is noisier than the data sheet's 0.80 nV/rtHz (RX clipped at 0), this is the achieved
calibration: white about 0.90 nV/rtHz and about 1.46 nV/rtHz at 10 Hz, since KF was fitted for a
white level of 0.80 (KF = (e_lf^2 - e_w^2) g_m^2 f_lf / I_D, models.py).

'JFE2325': the calibrated model at the data sheet's noise condition, V_GS = 0 (gate connected to
ground, I_D = the card's I_DSS) and V_DS = 2.5 V, against the gate-grounded curve of SLPS816A
Fig. 5-24, p. 9 (read by eye, FIG_5_24 below), from 1 Hz to 100 kHz, and the ratio of the 1/f
powers at 10 Hz, (e_model^2 - e_w,model^2) / (e_DS^2 - e_w,DS^2), e_w the 100 kHz values.  Since
models.py fits the JFE2325's KF to this curve at 10 Hz (32 nV/rtHz), the ratio is close to 1 by
construction.  The card as published (its own KF, kf_card = 40e-18) is evaluated with the closed
form of models.py at the same operating point, e(f) = sqrt(e_white^2 + KF I_D / (f g_m^2)):
its 1/f power at 10 Hz is 3.2 times the curve's ('published card').

'2N5564 targets' (the SR560's input JFET, Section 2 of the note): what the calibration used and
how it compares with Vishay's curves (70254 Rev. E, p. 5, noise voltage against frequency at
V_DS = 15 V, for I_D = 1 and 10 mA, read by eye).  The SR560 runs the 2N5564 at I = 4.5 mA.
Interpolation of a reading e(1 mA), e(10 mA) to I, with t = log10(I / 1 mA) (log scale in current):
    log-log      e = e(1 mA) (e(10 mA) / e(1 mA))^t
    lin-log      e = e(1 mA) + t (e(10 mA) - e(1 mA))
    linear       e = e(1 mA) + (I - 1 mA) / (9 mA) (e(10 mA) - e(1 mA))
for two readings: the one written in models.py (1.35 and 1.2 nV/rtHz white at 100 kHz, 4.2 and
3.1 at 1 kHz) and a second reading made for this check (1.35 and 1.24 at 100 kHz, 4.1 and 3.1 at
1 kHz).  The targets the calibration uses are the numbers in models.py (en_w = 1.28, en_lf = 3.6
nV/rtHz at f_lf = 1 kHz, I_D 4.5 mA, V_DS 5.5 V); the calibrated subcircuit's values at that
point are simulated.  (The 2N5564 is not recalibrated here: that would change the SR560 results.)

Writes ../sim/results/jfet_model_check.json.
"""
from __future__ import annotations

import json
import math
import sys

import models
import spice

CURVES = {
    "JFE150": dict(vds=5.0, pts=[(0.05, 2.65), (0.1, 2.25), (0.2, 1.72), (0.5, 1.3), (1, 1.05), (2, 0.9),
                                 (3, 0.85), (5, 0.82), (7, 0.82), (10, 0.86), (20, 1.0)],
                   table=[(0.1, 2.0, 3.0), (2, 0.9, 1.6), (5, 0.8, 1.8)],
                   src="SLPS732B Table 6.5 and Fig. 6-11"),
    "JFE2140": dict(vds=10.0, pts=[(0.05, 3.3), (0.1, 2.6), (0.2, 1.9), (0.5, 1.5), (1, 1.3), (2, 1.08),
                                   (3, 1.0), (5, 0.9), (10, 1.22)],
                    table=[(0.1, 2.5, 5.4), (2, 1.1, 2.4)],
                    src="SLPS730B Table 6.5 and Fig. 6-16"),
}
# SLPS816A Fig. 5-24, p. 9: input-referred noise density, "No C_IN, Gate Connected to Ground", read by
# eye (Hz, nV/rtHz)
FIG_5_24 = [(1.0, 101.0), (10.0, 32.0), (100.0, 10.1), (1e3, 5.2), (1e4, 4.4), (1e5, 4.25)]
# Vishay 2N5564 data sheet 70254 Rev. E, p. 5, noise voltage vs frequency at V_DS = 15 V, read by eye:
# (I_D mA): (white at 100 kHz, 1 kHz) in nV/rtHz
READ_2N5564 = {
    "reading in models.py": {1.0: (1.35, 4.2), 10.0: (1.2, 3.1)},
    "second reading (this check)": {1.0: (1.35, 4.1), 10.0: (1.24, 3.1)},
}
SPEC_FREQS = (1.0, 10.0, 100.0, 1e3, 1e4, 1e5)


def dc(part: str, vds: float, id_: float) -> dict:
    lib = (spice.LIB / "jfets.lib").as_posix()
    deck = (f"* dc {part}\n{spice.OPTIONS}.include \"{lib}\"\n"
            f"VG g 0 DC 0\nVD d 0 DC {vds}\nXJ d g 0 {part}\n"
            f"VG2 g2 0 DC 0\nXJ2 d2 g2 s2 {part}\nVD2 d2 d3 DC {vds}\nED d3 0 s2 0 1\nIS2 s2 0 DC {id_}\n"
            ".control\nop\nprint -i(vd) v(s2) @j.xj2.j1[gm]\n.endc\n.end\n")
    f = spice.run(f"_models/dc_{part}", deck)
    return dict(idss=spice.printed(f, "-i(vd)"), vgs=-spice.printed(f, "v(s2)"),
                gm=spice.printed(f, "@j.xj2.j1[gm]"))


def spectrum(part: str, id_: float, vds: float, tag: str, freqs=SPEC_FREQS) -> dict:
    """Input noise of the calibrated subcircuit (RX included) at (id_, vds), at freqs, and V_GS."""
    lib = (spice.LIB / "jfets.lib").as_posix()
    deck = (f"* spectrum {part}\n{spice.OPTIONS}.include \"{lib}\"\n"
            f"VG g 0 DC 0 AC 1\nXJ d g s {part}\nVD d d1 DC {vds}\nED d1 0 s 0 1\nIS1 s 0 DC {id_}\nCS s 0 1\n"
            "HOUT out 0 VD 1\n.control\nset wr_singlescale\nset wr_vecnames\nop\nprint v(s)\n"
            "noise v(out) VG dec 20 1 1e6\nsetplot noise1\nwrdata noise.txt inoise_spectrum\n.endc\n.end\n")
    folder = spice.run(f"_models/spectrum_{part}{tag}", deck)
    d = spice.read_table(folder / "noise.txt")
    f, s = d["frequency"], d["inoise_spectrum"]
    return dict(vgs=-spice.printed(folder, "v(s)"), en={f"{f0:g}": spice.at(f, s, f0) for f0 in freqs})


def calibration_check(cal: dict) -> dict:
    out = {}
    for part, c in cal.items():
        if not c.get("calibrated"):
            continue
        fr = sorted({10.0, 1e5, c.get("f_w", 1e5), c.get("f_lf", 10.0)})
        sp = spectrum(part, c["id"], c["vds"], "_cal", fr)
        e = sp["en"]
        row = dict(id=c["id"], vds=c["vds"], vgs=sp["vgs"], rx=c["rx"], rx_clipped=c.get("rx_clipped"),
                   en_white_100k=e["100000"], en_10Hz=e["10"],
                   en_target_white=c["en_target_white"], f_w=c.get("f_w"),
                   en_at_f_w=e[f"{c['f_w']:g}"] if c.get("f_w") else None,
                   en_achieved_at_f_w_closed_form=c.get("en_achieved_at_f_w"),
                   en_achieved_white_closed_form=c.get("en_achieved_white"))
        if c.get("en_target_lf"):
            row.update(f_lf=c["f_lf"], en_target_lf=c["en_target_lf"], en_at_f_lf=e[f"{c['f_lf']:g}"],
                       en_achieved_lf_closed_form=c.get("en_achieved_lf"))
        out[part] = row
        print(f"{part:8s} at {c['id'] * 1e3:.4g} mA, {c['vds']:g} V (V_GS {sp['vgs']:+.4f} V): white "
              f"{e['100000'] * 1e9:.4f} (target {c['en_target_white'] * 1e9:.3f}"
              + (", RX clipped" if c.get("rx_clipped") else "") + ")"
              + (f", at {c['f_w']:g} Hz {row['en_at_f_w'] * 1e9:.4f}" if c.get("f_w") else "")
              + (f", at {c['f_lf']:g} Hz {row['en_at_f_lf'] * 1e9:.4f} (target {c['en_target_lf'] * 1e9:.3f})"
                 if c.get("en_target_lf") else "")
              + f", 10 Hz {e['10'] * 1e9:.4f} nV/rtHz", flush=True)
    return out


def jfe2325(cal: dict) -> dict:
    c = cal["JFE2325"]
    sp = spectrum("JFE2325", c["id"], c["vds"], "_vgs0")
    e = sp["en"]
    ds = {f"{f:g}": v * 1e-9 for f, v in FIG_5_24}
    # the calibration's 10 Hz target (models.py) is this curve's reading
    assert abs(models.PARTS["JFE2325"]["cal"]["en_lf"] - ds["10"]) < 1e-15
    p_model = e["10"] ** 2 - e["100000"] ** 2
    p_ds = ds["10"] ** 2 - ds["100000"] ** 2
    # the card as published (KF = kf_card), closed form of models.py at the calibration's operating point
    kf_pub = c["kf_card"]
    e_pub = {f"{f:g}": math.sqrt(c["en_achieved_white"] ** 2 + kf_pub * c["id"] / (f * c["gm"] ** 2)) for f in SPEC_FREQS}
    p_pub = e_pub["10"] ** 2 - e_pub["100000"] ** 2
    out = dict(bias=c.get("bias"), id=c["id"], vds=c["vds"], vgs=sp["vgs"], kf=models._get(c["card"], "kf"),
               kf_card=kf_pub, kf_ratio_card_to_calibrated=kf_pub / models._get(c["card"], "kf"),
               rx=c["rx"], model=e, datasheet_fig_5_24=ds,
               ratio_model_to_datasheet={k: e[k] / ds[k] for k in e},
               one_over_f_power_ratio_10Hz=p_model / p_ds,
               published_card=dict(kf=kf_pub, en_closed_form=e_pub, one_over_f_power_ratio_10Hz=p_pub / p_ds,
                                   how="e(f) = sqrt(e_white^2 + KF I_D / (f g_m^2)), e_white, I_D, g_m of "
                                       "jfet_calibration.json (models.py)"),
               src="SLPS816A Fig. 5-24, p. 9, 'No C_IN, Gate Connected to Ground', read by eye; Table 5.5, p. 5: "
                   "4.3 nV/rtHz at 10 kHz, gate connected to ground")
    print("JFE2325 at V_GS = 0 (" + f"{c['id'] * 1e6:.1f} uA, V_GS {sp['vgs']:+.2e} V): "
          + ", ".join(f"{k} Hz {e[k] * 1e9:.2f} ({ds[k] * 1e9:.2f})" for k in e)
          + f" nV/rtHz, model (data sheet); 1/f power ratio at 10 Hz {out['one_over_f_power_ratio_10Hz']:.2f}; "
            f"KF {out['kf']:.4g} (card {kf_pub:.4g}, x{out['kf_ratio_card_to_calibrated']:.3f}); published card: "
            f"10 Hz {e_pub['10'] * 1e9:.2f} nV/rtHz, 1/f power ratio {p_pub / p_ds:.3f}", flush=True)
    return out


def targets_2n5564(cal: dict) -> dict:
    c = cal["2N5564"]
    i = c["id"] * 1e3
    t = math.log10(i)
    interp = {}
    for name, rd in READ_2N5564.items():
        (w1, k1), (w10, k10) = rd[1.0], rd[10.0]
        row = {}
        for label, fn in (("log-log", lambda a, b: a * (b / a) ** t), ("lin-log", lambda a, b: a + t * (b - a)),
                          ("linear", lambda a, b: a + (i - 1.0) / 9.0 * (b - a))):
            row[label] = dict(white=fn(w1, w10) * 1e-9, at_1kHz=fn(k1, k10) * 1e-9)
        interp[name] = dict(reading=dict(white_1mA=w1 * 1e-9, white_10mA=w10 * 1e-9, at_1kHz_1mA=k1 * 1e-9,
                                         at_1kHz_10mA=k10 * 1e-9), interpolated=row)
    sp = spectrum("2N5564", c["id"], c["vds"], "_sr560", (10.0, 1e3, 1e5))
    used = models.PARTS["2N5564"]["cal"]
    out = dict(id=c["id"], vds=c["vds"], t_log=t, readings=interp,
               targets_used=dict(en_w=used["en_w"], en_lf=used["en_lf"], f_lf=used["f_lf"],
                                 how="RX fitted so that the card's white noise (KF = 0, 1 kHz) is en_w; KF fitted so "
                                     "that the density at f_lf = 1 kHz is en_lf (models.calibrate)"),
               model=dict(en_white_100k=sp["en"]["100000"], en_1kHz=sp["en"]["1000"], en_10Hz=sp["en"]["10"],
                          rx=c["rx"], kf=c["kf"]),
               differential_white_used=math.sqrt(2) * used["en_w"],
               src="Vishay 2N5564 data sheet 70254 Rev. E (S-50150, 24-Jan-05), p. 5, 'Noise Voltage vs. "
                   "Frequency', V_DS 15 V, I_D 1 and 10 mA (read by eye)")
    ll = interp["reading in models.py"]["interpolated"]["log-log"]
    ll2 = interp["second reading (this check)"]["interpolated"]["log-log"]
    out["text"] = (f"targets {used['en_w'] * 1e9:.2f} nV/rtHz white and {used['en_lf'] * 1e9:.1f} nV/rtHz at 1 kHz at "
                   f"{i:g} mA, set by eye between Vishay's curves for 1 and 10 mA (70254 Rev. E p. 5); a log-log "
                   f"interpolation in current of the readings gives {ll['white'] * 1e9:.2f}-{ll2['white'] * 1e9:.2f} "
                   f"white and {ll2['at_1kHz'] * 1e9:.2f}-{ll['at_1kHz'] * 1e9:.2f} at 1 kHz")
    print("2N5564 at 4.5 mA: " + "; ".join(
        f"{n}: " + ", ".join(f"{lab} {v['white'] * 1e9:.3f}/{v['at_1kHz'] * 1e9:.3f}" for lab, v in r["interpolated"].items())
        for n, r in interp.items())
          + f"; used {used['en_w'] * 1e9:.2f}/{used['en_lf'] * 1e9:.2f}; model {sp['en']['100000'] * 1e9:.3f} white (100 kHz), "
            f"{sp['en']['1000'] * 1e9:.3f} at 1 kHz, {sp['en']['10'] * 1e9:.2f} at 10 Hz", flush=True)
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    out = {}
    for part, c in CURVES.items():
        currents = [i * 1e-3 for i, _ in c["pts"]]
        rows = models.en_vs_id(part, currents, c["vds"])
        out[part] = dict(src=c["src"], vds=c["vds"],
                         model=[dict(id=i, en_white=w, en_10=l) for i, w, l in rows],
                         curve=[dict(id=i * 1e-3, en=e * 1e-9) for i, e in c["pts"]],
                         table=[dict(id=i * 1e-3, en_1k=a * 1e-9, en_10=b * 1e-9) for i, a, b in c["table"]],
                         dc_10V=dc(part, 10.0, 2e-3), dc_5V_5mA=dc(part, 5.0, 5e-3))
        print(part, out[part]["dc_10V"], out[part]["dc_5V_5mA"])
        for (i, w, l), (_, e) in zip(rows, c["pts"]):
            print(f"  {i * 1e3:6.2f} mA  model white {w * 1e9:5.2f}  10 Hz {l * 1e9:5.2f}   curve (1 kHz) {e:5.2f}")
    cal = json.loads((spice.RESULTS / "jfet_calibration.json").read_text(encoding="utf-8"))
    out["calibration check"] = calibration_check(cal)
    out["JFE2325"] = jfe2325(cal)
    out["2N5564 targets"] = targets_2n5564(cal)
    (spice.RESULTS / "jfet_model_check.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
