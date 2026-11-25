"""Prepare the JFET models of the low-noise preamplifier note for ngspice.

Writes ../sim/models/_lib/jfets.lib, one subcircuit per part with the pins (drain, gate, source):

    .subckt <PART> d g s
    J1 d gi s <PART>_M          the vendor's or the note's .MODEL card
    RX g gi <rx>                 excess-noise gate resistor (thermal noise only), see below
    .ends

Why a wrapper.  ngspice's JFET (level 1) gives the channel the thermal noise 8kT g_m / 3 (the
long-channel factor gamma = 2/3), the thermal noise of RS and RD, and flicker noise
KF I_D^AF / f.  Real low-noise JFETs are noisier than 8kT/(3 g_m) by a factor that depends on the
part (gate resistance, short-channel effects, the measurement), so each part is calibrated to its
data sheet: RX is chosen so that the white input noise at the data sheet's operating point equals
the data sheet's typical value, and KF (AF = 1) so that the density at the data sheet's
low-frequency point equals its typical value.  RX is a real resistor in series with the gate; at a
few ohms it changes nothing else.  The calibration targets, the operating points and the sources
are listed in CAL below and printed by `python models.py`; the resulting values are written to
../sim/results/jfet_calibration.json.

The equations of the calibration, with e_m the card's own white input noise (ngspice, KF = 0, at
1 kHz) and g_m its transconductance at the data sheet's operating point (I_D, V_DS):
    RX = (e_w^2 - e_m^2) / (4kT), clipped at 0 when e_m > e_w (the card is already noisier)
    KF = (e_lf^2 - e_w^2) g_m^2 f_lf / I_D                                   (AF = 1)
and the values the calibrated subcircuit then gives (written as en_achieved_*):
    e_white = sqrt(e_m^2 + 4kT RX),   e(f) = sqrt(e_white^2 + KF I_D / (f g_m^2)).
When RX is clipped, e_white = e_m > e_w and every e(f) is higher than the target (LSBF862).
A part biased at a gate voltage instead of a current (cal['vgs'], the JFE2325, whose data sheet
measures its noise with the gate grounded) is calibrated at the drain current that the card
draws at that V_GS and V_DS (an operating point).  Where the data sheet's table has no
low-frequency value (the JFE2325), e_lf is read off its noise curve (Fig. 5-24 at 10 Hz).  The
card's own KF is kept in jfet_calibration.json as kf_card.

Cards from LTspice's standard.jft are Linear Integrated Systems' published cards.  LTspice-only
parameters are removed (Mfg, Isr, Nr, Alpha, Vk, M, Mj, Gdsnoi, Nlev): ngspice ignores or rejects
them, and Gdsnoi/Nlev select a noise equation that the calibration replaces.  ngspice's JFET keeps
the capacitance exponent at 0.5.

prepare_published_opamps() writes a second op-amp library, _lib/opamps_published.lib, with the
vendor models as published (translated for ngspice, noise not corrected) and with every KF set to
zero, for the checks of Table 8 of the note (opamp_noise_check.py); prepare() does not write it.
"""
from __future__ import annotations

import json

import numpy as np
import math
import os
import re
import sys
from pathlib import Path

import blocks
import spice

# LTspice's component library (its standard install under %LOCALAPPDATA%)
LOCAL_APPDATA = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
LTSPICE_JFT = LOCAL_APPDATA / "LTspice" / "lib" / "cmp" / "standard.jft"
LTSPICE_BJT_LIB = LOCAL_APPDATA / "LTspice" / "lib" / "cmp" / "standard.bjt"
DROP = re.compile(r"\b(mfg|isr|nr|zxti|alpha|vk|m|mj|gdsnoi|nlev)\s*=\s*\S+", re.I)


def ltspice_raw(name: str) -> str:
    """The parameter text of a .model card from LTspice's standard.jft as written there (read from
    the local LTspice installation at run time; the cards are not copied into this project)."""
    raw = LTSPICE_JFT.read_bytes()
    try:
        text = raw.decode("utf-16")
    except UnicodeError:
        text = raw.decode("latin-1")
    for line in text.splitlines():
        m = re.match(r"\s*\.model\s+(\S+)\s+NJF\s*\((.*)\)\s*$", line, re.I)
        if m and m.group(1).upper() == name.upper():
            return m.group(2)
    raise KeyError(name)


def ltspice_card(name: str) -> str:
    """The parameter text of a .model card from LTspice's standard.jft, cleaned for ngspice."""
    params = DROP.sub("", ltspice_raw(name))
    params = re.sub(r"\bmfg\s*=\s*\S+", "", params, flags=re.I)
    return " ".join(params.split())


# ----------------------------------------------------------------------------------------------
# Parts.  'card' is the parameter text of the NJF card; 'cal' the data-sheet targets (typical
# values at 25 C), each with its source:
#   ciss, crss, vds_c   C_iss and C_rss at V_GS = 0 and V_DS = vds_c; CGS and CGD of the card are
#                       scaled so that ngspice's capacitances match (ngspice ignores the junction
#                       grading M and keeps the exponent 0.5, so the vendors' CGS/CGD do not give
#                       the data-sheet values unchanged)
#   id, vds, en_w       white input noise density at that operating point (RX fitted)
#   en_lf, f_lf         density at a low frequency at the same point (KF fitted, AF = 1)
# ----------------------------------------------------------------------------------------------
PARTS: dict[str, dict] = {}
VENDOR_JFET = spice.ROOT / "sim" / "models"


def add(part: str, card: str, cal: dict | None = None, note: str = "") -> None:
    PARTS[part] = dict(card=card, cal=cal, note=note)


def ti_card(path: Path) -> str:
    """The NJF card of a TI JFET model file (Shichman-Hodges), cleaned for ngspice."""
    text = path.read_text(encoding="latin-1")
    m = re.search(r"^\.model\s+\S+\s+NJF\s*\((.*?)\)", text, re.I | re.M | re.S)
    params = DROP.sub("", m.group(1).replace("\n+", " "))
    return " ".join(params.split())


def default_parts() -> None:
    """Linear Systems cards from LTspice's library and TI's cards (calibration targets from the
    data sheets, refs/datasheets/jfet/)."""
    for p in ("2N5564", "LSK389A", "LSK389B", "LSK389C", "LSK170A", "LSK170B", "LSK170C",
              "LSK489A", "LSK489B", "LSK489C", "U401", "J310"):
        add(p, ltspice_card(p), None, "Linear Systems card (LTspice standard.jft)")
    # Linear Systems' updated LSBF862 card ("Updated LSBF862 SPICE Model", Rev 2, 2026-02-09),
    # as published (the BF862 cascodes and the wideband variant)
    # (its KF gives about 9 nV/rtHz at 10 Hz, against 1.4 typical in the data sheet; recalibrated)
    add("LSBF862", " ".join(DROP.sub("", "VTO=-0.79 BETA=2.658E-2 VTOTC=-2.5m BETATCE=-0.5 LAMBDA=0.03 "
        "RD=7.5 RS=7.5 IS=1E-14 ISR=1E-13 N=1 NR=2 XTI=3 ZXTI=1 ALPHA=1E-4 VK=180 CGS=8P CGD=3.5P PB=0.5 "
        "M=0.33 MJ=0.33 FC=0.5 KF=8.75E-17 AF=1 GDSNOI=2 NLEV=3 MFG=Linear_Systems").split()),
        dict(ciss=11.5e-12, crss=3.5e-12, vds_c=8.0, id=2e-3, vds=8.0, en_w=0.8e-9, f_w=1e4, en_lf=1.4e-9,
             f_lf=10.0,
             src="Linear Systems LSBF862 data sheet, Doc 201195 Rev A2 (2026-02-17), p. 2: e_n 0.8 nV/rtHz "
                 "at 10 kHz and 1.4 at 10 Hz typ (V_DS 8 V, I_D 2 mA); C_iss 11.5 pF, C_rss 3.5 pF (8 V)"),
        "Linear Systems LSBF862 card, Rev 2 (2026-02-09)")
    # The SR560's NPD5564: Vishay 2N5564 data (Doc. 70254 Rev. E): C_iss 10 pF, C_rss 2.5 pF at
    # V_DS 15 V (fitted here at V_GS = 0); noise curve at V_DS 15 V read by eye (p. 5): 1.2 and 1.35
    # nV/rtHz at 100 kHz and 3.1 and 4.2 at 1 kHz for 10 and 1 mA.  The targets, 1.28 white and 3.6
    # at 1 kHz at the SR560's 4.5 mA, were set by eye between those curves: a log-log interpolation
    # in current of these readings gives 1.25 and 3.44 (jfet_model_check.py, '2N5564 targets'); they
    # are kept, since every SR560 result rests on them.  Its excess noise is not a clean 1/f line
    # (corner 5-15 kHz), so KF is fitted at 1 kHz and the model overstates the 10 Hz value.
    add("2N5564", ltspice_card("2N5564"),
        dict(ciss=10e-12, crss=2.5e-12, vds_c=15.0, id=4.5e-3, vds=5.5, en_w=1.28e-9, f_w=1e5, en_lf=3.6e-9,
             f_lf=1e3,
             src="Vishay 2N5564 data sheet 70254 Rev. E: C_iss/C_rss p. 2; noise vs frequency p. 5 "
                 "(read by eye, interpolated to 4.5 mA)"),
        "Linear Systems 2N5564 card (LTspice standard.jft), recalibrated")
    # The front-end pair of newer SR560s: a teardown of two units of different serial numbers found
    # an LSK389B in the newer one and the NPD5564 in the older (EEVblog forum, "SR560 Low noise amp --
    # Noise Calculation", 18 March 2024); SRS's manual (Rev. 3.1, 4/2023) still lists the NPD5564.
    # Card: Linear Systems' "Updated LSK389 A/B/C/D" SPICE model, Rev 2 (2026-05-18), B grade, as
    # published (ISR, NR, ALPHA, VK, M and MFG dropped for ngspice).  Targets: LSK389 data sheet
    # Doc 201122 Rev A27 (2023-06-23), p. 2, typical: e_n 1.6 and 3.2 nV/rtHz at 1 kHz and 10 Hz
    # (V_DS 10 V, I_D 2 mA); C_iss 25 pF (V_DS 10 V, V_GS 0) and C_rss 5.5 pF (V_DG 10 V, I_D 0),
    # both fitted here at V_GS = 0 and V_DS = 10 V.  The 1 kHz value is taken as the white level,
    # as for the JFE150 and JFE2140 (the fitted 1/f then adds 1.5 % at 1 kHz).
    add("LSK389B_LIS", " ".join(DROP.sub("", "VTO=-0.702 VTOTC=-2.5m BETA=23.7m BETATCE=-0.5 LAMBDA=10.2m "
        "RD=2 RS=2 IS=67.4p ISR=674p N=1 NR=2 XTI=3 CGS=19.5p CGD=5.5p PB=1.0 FC=0.5 ALPHA=1e-4 VK=0 M=0.4 "
        "KF=8.2e-18 AF=1 MFG=Linear_Systems").split()),
        dict(ciss=25e-12, crss=5.5e-12, vds_c=10.0, id=2e-3, vds=10.0, en_w=1.6e-9, f_w=1e3, en_lf=3.2e-9,
             f_lf=10.0,
             src="Linear Systems LSK389 data sheet Doc 201122 Rev A27 (2023-06-23), p. 2, typ: e_n 1.6/3.2 "
                 "nV/rtHz at 1 kHz/10 Hz (V_DS 10 V, I_D 2 mA); C_iss 25 pF (V_DS 10 V, V_GS 0), C_rss 5.5 pF "
                 "(V_DG 10 V, I_D 0)"),
        "Linear Systems updated LSK389B card, Rev 2 (2026-05-18)")
    # the C_rss targets of the JFE150 and JFE2140 are pixel readings of their data sheets' figures,
    # archived as scripts/ti_plot_check.py (sim/results/ti_plot_check.json)
    ti = VENDOR_JFET / "TI"
    add("JFE150", ti_card(ti / "JFE150" / "slpm349i" / "jfe150.lib"),
        dict(ciss=24e-12, crss=4.1e-12, vds_c=5.0, id=5e-3, vds=5.0, en_w=0.8e-9, f_w=1e3, en_lf=1.8e-9,
             f_lf=10.0,
             src="TI JFE150 data sheet SLPS732B: Table 6.5 (e_n 0.8/1.8 nV/rtHz at 1 kHz/10 Hz, "
                 "5 mA, 5 V; C_iss 24 pF at 5 V); C_rss at 5 V read off Fig. 6-12 (p. 7) from its pixels, "
                 "4.13 pF (C_iss reads 23.9 pF there; the first reading by eye was 4.5 pF)"),
        "TI model SLPM349I (Final 1.2, 2024), NJF card only")
    add("JFE2140", ti_card(ti / "JFE2140" / "slpm355" / "jfex140.lib"),
        dict(ciss=13e-12, crss=3.9e-12, vds_c=5.0, id=2e-3, vds=10.0, en_w=1.1e-9, f_w=1e3, en_lf=2.4e-9,
             f_lf=10.0,
             src="TI JFE2140 data sheet SLPS730B: Table 6.5 (e_n 1.1/2.4 nV/rtHz at 1 kHz/10 Hz, "
                 "2 mA, 10 V; C_iss 13 pF at 5 V); C_rss at 5 V read off Fig. 6-17 (p. 8) from its pixels, "
                 "3.93 pF (C_iss reads 13.4 pF there; the first reading by eye was 4.2 pF)"),
        "TI model SLPM355 (JFEx140 card)")
    # JFE2325: the data sheet measures e_n (4.3 nV/rtHz at 10 kHz) with the gate connected to ground
    # (SLPS816A p. 5, Table 5.5, V_DS = 2.5 V), i.e. at V_GS = 0 and I_D = I_DSS (385 uA typical), so
    # the calibration runs at V_GS = 0, at the card's own I_DSS (vgs=0.0; an earlier version used the
    # 325 uA of the table's Delta V_GS condition, V_GS = -80 mV).  The table gives no low-frequency
    # value, so KF is fitted, as for the JFE2140, to the gate-grounded curve of Fig. 5-24 (p. 9) at
    # 10 Hz: 32 nV/rtHz read by eye (jfet_model_check.FIG_5_24, the same reading).  The card's own KF,
    # 40e-18, gives 3.2 times that curve's 1/f power at 10 Hz (jfet_model_check.json, 'JFE2325').
    add("JFE2325", ti_card(ti / "JFE2325" / "slvmf24" / "jfe2325.lib"),
        dict(ciss=0.85e-12, crss=0.1e-12, vds_c=2.0, vgs=0.0, vds=2.5, en_w=4.3e-9, f_w=1e4, en_lf=32e-9,
             f_lf=10.0,
             src="TI JFE2325 data sheet SLPS816A, p. 5, Table 5.5: e_n 4.3 nV/rtHz at 10 kHz with the gate "
                 "connected to ground (V_GS = 0, I_D = I_DSS, 385 uA typ), V_DS 2.5 V; C_iss 0.85 pF, "
                 "C_rss 0.1 pF at V_DS 2 V; p. 9, Fig. 5-24 (no C_IN, gate connected to ground): 32 nV/rtHz "
                 "at 10 Hz (read by eye)"),
        "TI model SLVMF24 (Final 1.0, 2026), NJF card only (the gate self-bias diode is not used)")


def subckt(part: str, rx: float, card: str) -> str:
    return (f".subckt {part} d g s\nJ1 d gi s {part}_M\nRX g gi {max(rx, 1e-3):.6g}\n"
            f".model {part}_M NJF({card})\n.ends {part}\n")


def _set(card: str, key: str, value: float) -> str:
    card = re.sub(rf"\b{key}\s*=\s*\S+", "", card, flags=re.I)
    return " ".join(card.split()) + f" {key}={value:.5g}"


def _get(card: str, key: str, default: float = 0.0) -> float:
    m = re.search(rf"\b{key}\s*=\s*([-+0-9.eE]+)([a-zA-Z]*)", card, re.I)
    if not m:
        return default
    v = float(m.group(1))
    suf = m.group(2).lower()
    mult = {"meg": 1e6, "f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3, "k": 1e3}
    for k in ("meg", "f", "p", "n", "u", "m", "k"):
        if suf.startswith(k):
            return v * mult[k]
    return v


def caps(part: str, card: str, vds: float) -> tuple[float, float]:
    """C_iss and C_rss of the card at V_GS = 0, V_DS = vds (ngspice, 1 MHz small signal), by the
    data sheets' definitions: C_iss from the gate current with the gate driven (drain and source
    at AC ground), C_rss from the gate current with the drain driven (gate and source at AC
    ground).  The drain current with the gate driven is not C_rss: ngspice's JFET shares the gate
    charge between source and drain, so it contains part of the gate-source charge."""
    w = 2 * math.pi * 1e6
    deck = (f"* caps {part}\n{spice.OPTIONS}.model M NJF({card})\n"
            f"VG g 0 DC 0 AC 1\nVD d 0 DC {vds}\nJ1 d g 0 M\n"
            f"VG2 g2 0 DC 0\nVD2 d2 0 DC {vds} AC 1\nJ2 d2 g2 0 M\n"
            ".control\nac lin 1 1meg 1meg\nprint imag(i(vg)) imag(i(vg2))\n.endc\n.end\n")
    f = spice.run(f"_models/caps_{part}", deck)
    ciss = abs(spice.printed(f, "imag(i(vg))")) / w
    crss = abs(spice.printed(f, "imag(i(vg2))")) / w
    return ciss, crss


def bare_noise(part: str, card: str, id_: float, vds: float, kf_zero: bool, tag: str = "") -> dict:
    """g_m, the white and 10-Hz input noise of the bare card at (id_, vds), by ngspice."""
    c = _set(card, "kf", 0.0) if kf_zero else card
    deck = (f"* bare noise {part}\n{spice.OPTIONS}.model M NJF({c})\n"
            f"VG g 0 DC 0 AC 1\nJ1 d g s M\nVD d d1 DC {vds}\nED d1 0 s 0 1\nIS1 s 0 DC {id_}\nCS s 0 1\n"
            "HOUT out 0 VD 1\n.control\nset wr_singlescale\nset wr_vecnames\nop\n"
            "print @j1[gm] @j1[id] v(s)\nnoise v(out) VG dec 10 1 1e6\nsetplot noise1\n"
            "wrdata noise.txt inoise_spectrum\n.endc\n.end\n")
    # the drain supply follows the source (ED), so V_DS is exact, and returns to ground, so the
    # drain current is the current source's id_
    folder = spice.run(f"_models/bare_{part}_{'w' if kf_zero else 'f'}{tag}", deck)
    d = spice.read_table(folder / "noise.txt")
    f, s = d["frequency"], d["inoise_spectrum"]
    return dict(gm=spice.printed(folder, "@j1[gm]"), vgs=-spice.printed(folder, "v(s)"),
                en_1k=spice.at(f, s, 1e3), en_10=spice.at(f, s, 10.0), en_10k=spice.at(f, s, 1e4),
                en_100k=spice.at(f, s, 1e5))


def drain_current(part: str, card: str, vgs: float, vds: float, tag: str = "") -> float:
    """Drain current of the card at (V_GS, V_DS), source grounded (an operating point)."""
    deck = (f"* drain current {part}\n{spice.OPTIONS}.model M NJF({card})\n"
            f"VG g 0 DC {vgs}\nVD d 0 DC {vds}\nJ1 d g 0 M\n.control\nop\nprint -i(vd)\n.endc\n.end\n")
    f = spice.run(f"_models/id_{part}{tag}", deck)
    return spice.printed(f, "-i(vd)")


def calibrate(part: str) -> dict:
    p = PARTS[part]
    cal = p["cal"]
    card = p["card"]
    if not cal:
        return dict(part=part, rx=0.0, card=card, calibrated=False)
    out = dict(part=part, src=cal.get("src", ""), note=p.get("note", ""), kf_card=_get(card, "kf"))
    if cal.get("id") is None:
        # biased at a gate voltage (the data sheet's condition): the card's drain current there
        cal = dict(cal, id=drain_current(part, card, cal["vgs"], cal["vds"]))
        out.update(bias=f"V_GS = {cal['vgs']:g} V, V_DS = {cal['vds']:g} V (drain current from the card)")
    out.update(id=cal["id"], vds=cal["vds"])
    # capacitances: ngspice's C_iss and C_rss are linear in CGS and CGD (but each depends on both,
    # as its JFET model shares the gate charge between the two terminals), so the card's values
    # are found from a 2 x 2 linear solve with three measurements
    if cal.get("ciss"):
        cgs0, cgd0 = _get(card, "cgs"), _get(card, "cgd")
        c0 = caps(part, card, cal["vds_c"])
        c1 = caps(part, _set(card, "cgs", 2 * cgs0), cal["vds_c"])
        c2 = caps(part, _set(card, "cgd", 2 * cgd0), cal["vds_c"])
        out.update(ciss_card=c0[0], crss_card=c0[1])
        # C = A [cgs, cgd]: column k is the change per unit of parameter k
        a = np.array([[(c1[0] - c0[0]) / cgs0, (c2[0] - c0[0]) / cgd0],
                      [(c1[1] - c0[1]) / cgs0, (c2[1] - c0[1]) / cgd0]])
        x = np.linalg.solve(a, np.array([cal["ciss"], cal["crss"]]))
        card = _set(_set(card, "cgs", float(x[0])), "cgd", float(x[1]))
        ciss, crss = caps(part, card, cal["vds_c"])
        out.update(ciss_model=ciss, crss_model=crss, ciss_target=cal["ciss"], crss_target=cal["crss"])
    w = bare_noise(part, card, cal["id"], cal["vds"], kf_zero=True)
    rx = max((cal["en_w"] ** 2 - w["en_1k"] ** 2) / (4 * spice.KT), 0.0)
    out.update(gm=w["gm"], vgs=w["vgs"], en_model_white=w["en_1k"], rx=rx, en_target_white=cal["en_w"])
    if cal.get("en_lf"):
        # flicker current density needed at f_lf: (en_lf^2 - en_w^2) gm^2 = KF id / f_lf
        kf = (cal["en_lf"] ** 2 - cal["en_w"] ** 2) * w["gm"] ** 2 * cal["f_lf"] / cal["id"]
        card = _set(_set(card, "kf", kf), "af", 1.0)
        out.update(kf=kf, en_target_lf=cal["en_lf"], f_lf=cal["f_lf"])
    # what the calibrated subcircuit gives (see the module docstring); RX is clipped at 0 when the
    # card alone is noisier than the target, and then every value is above its target
    e_wh = math.sqrt(w["en_1k"] ** 2 + 4 * spice.KT * rx)
    kf_now, af_now = _get(card, "kf"), _get(card, "af", 1.0)
    out.update(rx_clipped=bool(w["en_1k"] > cal["en_w"]), en_achieved_white=e_wh)
    if af_now == 1.0:
        def e_at(f: float) -> float:
            return math.sqrt(e_wh ** 2 + kf_now * cal["id"] / (f * w["gm"] ** 2))
        if cal.get("en_lf"):
            out["en_achieved_lf"] = e_at(cal["f_lf"])
        if cal.get("f_w"):
            out.update(f_w=cal["f_w"], en_achieved_at_f_w=e_at(cal["f_w"]))
        out["en_achieved_10Hz"] = e_at(10.0)
    out["card"] = card
    out["calibrated"] = True
    return out


def en_vs_id(part: str, currents, vds: float) -> list[tuple[float, float, float]]:
    """(I_D, white e_n (100 kHz), e_n at 10 Hz) of the calibrated subcircuit (RX included)."""
    lib = (spice.LIB / "jfets.lib").as_posix()
    rows = []
    for k, i in enumerate(currents):
        deck = (f"* en vs id {part}\n{spice.OPTIONS}.include \"{lib}\"\n"
                f"VG g 0 DC 0 AC 1\nXJ d g s {part}\nVD d d1 DC {vds}\nED d1 0 s 0 1\nIS1 s 0 DC {i}\nCS s 0 1\n"
                "HOUT out 0 VD 1\n.control\nset wr_singlescale\nset wr_vecnames\nop\n"
                "noise v(out) VG dec 10 1 1e6\nsetplot noise1\nwrdata noise.txt inoise_spectrum\n.endc\n.end\n")
        folder = spice.run(f"_models/envsid_{part}_{k}", deck)
        d = spice.read_table(folder / "noise.txt")
        f, s = d["frequency"], d["inoise_spectrum"]
        rows.append((i, spice.at(f, s, 1e5), spice.at(f, s, 10.0)))
    return rows


# ----------------------------------------------------------------------------------------------
# Vendor op-amp models.  Each is translated for ngspice (translate_model) and wrapped in a
# subcircuit OA_<PART> with the pins (inp inn out vcc vee), so that every position can take any
# part by name.  Files are read from ../sim/models/vendor_opamps/ (see the README there for
# their sources; they are not redistributed).
# ----------------------------------------------------------------------------------------------
VENDOR_OPAMPS = {
    # THS4021: the 1999 model's 1/f noise is about 20 times the data sheet's (its input
    # transistors carry KF = 2.5e-13); its KF are set to zero and 1/f generators are added that
    # give the data sheet's curves (SLOS265F, Figs. 5-11 and 5-12, p. 11): e_n 4 nV/rtHz at 10 Hz
    # (read by eye; 4.0-4.1 from the pixels) and i_n 18.6 pA/rtHz at 10 Hz (read from the pixels at the
    # 10 Hz frame edge, 18.5-18.8; the first reading by eye, 20, was high) over the curves' white floors
    # of 1.2 nV/rtHz and 2.1 pA/rtHz (at 100 kHz, from the pixels), i.e. 1/f parts of
    # sqrt(4^2 - 1.2^2) = 3.82 nV/rtHz and sqrt(18.6^2 - 2.1^2) = 18.5 pA/rtHz at 10 Hz
    # (the pixel readings of both op amps' curves: scripts/ti_plot_check.py, ti_plot_check.json)
    "THS4021": dict(file="ths4021.lib", inst="inp inn vcc vee out THS4021",
                    src="TI SLOJ004, THS4021 PSpice model (1999)",
                    flicker=dict(ev=3.82e-9, ii=18.5e-12, f0=10.0)),
    "ADA4899": dict(file="ada4899.cir", inst="inp inn vcc vee out out npd ADA4899",
                    src="ADI ADA4899 SPICE macro model, Rev. 3.0 (2015)"),
    "LMH6629": dict(file="LMH6629.MOD", inst="inp inn vcc vee out vcc LMH6629",
                    src="TI SNOM133, LMH6629 PSpice model (COMP pin high)"),
    "OPA855": dict(file="opa855_a.lib", inst="inp inn out vcc vee OPA855",
                   src="TI SBOMB43D, OPA855 unencrypted PSpice model (Rev. D)"),
    "ADA4817": dict(file="ada4817.cir", inst="inp inn vcc vee out out vcc ADA4817",
                    src="ADI ADA4817 SPICE macro model, Rev. 2.1 (2017)"),
    "THS4631": dict(file="ths4631_b.lib", inst="inp inn vcc vee out THS4631",
                    src="TI SLOC051E, THS4631 PSpice model"),
    # THS3091: the model's two input transistors carry KF = 1.5e-13, which gives 37 nV/rtHz and
    # 317 pA/rtHz (inverting input) at 10 Hz, against 6.5 nV/rtHz and 200 pA/rtHz in the data
    # sheet (SLOS423K, Fig. 7-16, +/-15 V, read by eye); its white inverting-input current noise
    # is 1.5 pA/rtHz against 14 pA/rtHz (Sec. 7.5, p. 6: 14 pA inverting, 15 pA non-inverting, 1.1
    # nV/rtHz).  KF set to zero; added: white current noise sqrt(14^2 - 1.5^2) = 13.9 pA/rtHz at
    # the inverting and 15 pA/rtHz at the non-inverting input, and 1/f generators of
    # sqrt(6.5^2 - 1.1^2) = 6.4 nV/rtHz, sqrt(200^2 - 14^2) = 199.5 pA/rtHz (inverting) and
    # sqrt(100^2 - 15^2) = 98.9 pA/rtHz (non-inverting) at 10 Hz.  The model's white voltage
    # noise (1.92 nV/rtHz, data sheet 1.1) is left as it is: it cannot be lowered by adding.
    "THS3091": dict(file="THS3091.lib", inst="inp inn out vcc vee THS3091",
                    src="TI SLOM418, THS3091 PSpice model",
                    white_i=(15e-12, 13.9e-12),
                    flicker=dict(ev=6.4e-9, iip=98.9e-12, iin=199.5e-12, f0=10.0)),
    "OPA1612": dict(file="OPA161x.LIB", inst="inp inn vcc vee out OPA161x",
                    src="TI SBOM396G, OPA161x PSpice model"),
    # THS4031: same 1999 model family and the same excess 1/f noise; data sheet SLOS224L,
    # Figs. 5-13 and 5-14 (p. 12): 4 nV/rtHz (read by eye; 4.0-4.1 from the pixels) and 18.6 pA/rtHz
    # (from the pixels, 18.5-18.8; 20 by eye) at 10 Hz over the curves' 1.2 nV/rtHz and 2.1 pA/rtHz
    # white (the table, Sec. 5.6 p. 6, gives 2.3 pA/rtHz for f > 10 kHz): the same 1/f parts as the THS4021
    "THS4031": dict(file="ths4031.lib", inst="inp inn vcc vee out THS4031",
                    src="TI SLOJ005A, THS4031 PSpice model",
                    flicker=dict(ev=3.82e-9, ii=18.5e-12, f0=10.0)),
    # LM7171: the National macromodel (A grade) has no noise sources beyond its two transistors and
    # resistors: 4.1 nV/rtHz white and no 1/f (all its KF are 0).  The data sheet (SNOS760D,
    # Sec. 5.5 and Fig. 5-16) gives 8.5 nV/rtHz at 10 kHz for the A grade and about 43 nV/rtHz at
    # 10 Hz (A grade, +/-5 V plot, read by eye).  Added: white sqrt(8.5^2 - 4.1^2) = 7.45 nV/rtHz
    # and a 1/f voltage generator of sqrt(43^2 - 8.5^2) = 42.2 nV/rtHz at 10 Hz.  The data sheet's
    # input current-noise curve (Fig. 5-17, p. 10) is not modelled: no 1/f current generator.
    "LM7171": dict(file="lm7171.lib", inst="inp inn vcc vee out LM7171",
                   src="TI SNOM205A, LM7171 PSpice model",
                   white=7.45e-9, flicker=dict(ev=42.2e-9, ii=0.0, f0=10.0)),
    "OPA2810": dict(file="opa2810_a.lib", inst="inp inn out vcc vee OPA2810",
                    src="TI SBOMB66, OPA2810 PSpice model"),
}
VENDOR_DIR = spice.ROOT / "sim" / "models" / "vendor_opamps"

_RES_TABS = re.compile(r"^(\s*\.model\s+)(\S+)(\s+)res\s*\(([^)]*?)\bt_abs\s*=\s*([-+0-9.eE]+)([^)]*)\)",
                       re.I | re.M)
_CAP_MODEL = re.compile(r"^(\s*\.model\s+\S+\s+)cap(\b)", re.I | re.M)


def translate_model(text: str) -> str:
    """Make a PSpice model read as intended by ngspice (from the photodiode-TIA notes): ngspice
    takes PSpice's T_ABS as an offset from 27 C, so 'noiseless' resistors (T_ABS = -273.15 C)
    would still be noisy at about 27 K; their cards become resistor models with noisy=0, other
    T_ABS resistors get the temperature as an instance parameter; PSpice's CAP model is C."""
    other = {}

    def card(m):
        name, t = m.group(2), float(m.group(5))
        rest = " ".join(re.sub(r"\btce\s*=\s*0+(\.0*)?\b", "", m.group(4) + " " + m.group(6), flags=re.I).split())
        if t <= -273.0:
            return f"{m.group(1)}{name}{m.group(3)}R ({rest + ' ' if rest else ''}noisy=0)"
        other[name.lower()] = t
        return f"{m.group(1)}{name}{m.group(3)}R ({rest})"

    text = _RES_TABS.sub(card, text)
    text = _CAP_MODEL.sub(r"\1C\2", text)
    if other:
        lines = text.splitlines()
        for i, ln in enumerate(lines):
            tok = ln.split()
            if len(tok) >= 5 and tok[0][:1].upper() == "R" and tok[3].lower() in other:
                lines[i] = ln + f" temp={other[tok[3].lower()]:g}"
        text = "\n".join(lines) + "\n"
    return text


def _atomic_write(path: Path, text: str, encoding: str) -> None:
    """Write to a temporary file and rename it, so that a simulation running in another process
    never reads a half-written library."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding=encoding, newline="\n")
    os.replace(tmp, path)


def prepare_opamps() -> None:
    out = ["* vendor op-amp models, translated for ngspice and wrapped as OA_<part> (inp inn out vcc vee)\n"]
    for part, m in VENDOR_OPAMPS.items():
        path = VENDOR_DIR / m["file"]
        if not path.exists():
            continue
        text = translate_model(path.read_text(encoding="latin-1"))
        fl = m.get("flicker")
        if fl:
            # the model's own flicker noise is replaced by pure 1/f generators fitted to the data
            # sheet (see VENDOR_OPAMPS): every KF in the file is set to zero
            text = re.sub(r"(\bKF\s*=\s*)[-+0-9.eE]+", r"\g<1>0", text, flags=re.I)
        out.append(f"* ---- {part}: {m['src']}\n" + text)
        wh = m.get("white", 0.0)
        wi = m.get("white_i", (0.0, 0.0))        # (non-inverting, inverting) A/rtHz
        if fl or wh or any(wi):
            gens, node = "", "inp"
            if wh:
                # extra white input voltage noise: a shorted 1-ohm noisy resistor read by an H source
                gens += (f"Rnw nw 0 1\nVnw nw 0 0\nHnw {node} inpw Vnw {wh / blocks.I1OHM:.6g}\n")
                node = "inpw"
            if fl:
                gens += blocks.flicker_v(f"{part}v", node, "inp2", fl["ev"], fl["f0"])
                node = "inp2"
                iip, iin = fl.get("iip", fl.get("ii", 0.0)), fl.get("iin", fl.get("ii", 0.0))
                if iip > 0:
                    gens += blocks.flicker_i(f"{part}p", node, iip, fl["f0"])
                if iin > 0:
                    gens += blocks.flicker_i(f"{part}n", "inn", iin, fl["f0"])
            for pin, tag, dens in ((node, "p", wi[0]), ("inn", "n", wi[1])):
                if dens > 0:
                    # extra white input current noise: a shorted 1-ohm noisy resistor read by an F source
                    gens += (f"Rniw{tag} niw{tag} 0 1\nVniw{tag} niw{tag} 0 0\n"
                             f"Fniw{tag} 0 {pin} Vniw{tag} {dens / blocks.I1OHM:.6g}\n")
            inst = m["inst"].replace("inp ", f"{node} ", 1)
            out.append(f".subckt OA_{part} inp inn out vcc vee\n{gens}X1 {inst}\n.ends OA_{part}\n")
        else:
            out.append(f".subckt OA_{part} inp inn out vcc vee\nX1 {m['inst']}\n.ends OA_{part}\n")
    _atomic_write(spice.LIB / "opamps.lib", "\n".join(out), "latin-1")


PUBLISHED = ("THS4021", "THS4031", "THS3091", "LM7171")


def _rename_subckts(text: str, suffix: str) -> str:
    """Append suffix to the name of every subcircuit defined in text, in its .subckt and .ends
    lines and wherever an instance (X line) calls it, so that a second copy of a model can sit in
    one deck next to the first."""
    names = {m.group(1).upper() for m in re.finditer(r"^\s*\.subckt\s+(\S+)", text, re.I | re.M)}
    out = []
    for ln in text.splitlines():
        s = ln.lstrip().lower()
        if s.startswith((".subckt", ".ends")) or s.startswith("x"):
            toks = ln.split()
            ln = " ".join(t + suffix if k > 0 and t.upper() in names else t for k, t in enumerate(toks))
        out.append(ln)
    return "\n".join(out) + "\n"


def prepare_published_opamps(parts=PUBLISHED) -> Path:
    """Write _lib/opamps_published.lib: each vendor model of `parts` as published, translated for
    ngspice only (translate_model, as in opamps.lib) and without any noise correction, wrapped as
    OA_<part>_PUB with the pins (inp inn out vcc vee); and the same model with every KF in its file
    set to zero, OA_<part>_PUBKF0, whose noise is the model's own white noise.  Every subcircuit of
    a model file is renamed with the suffix, so this library can be included together with
    opamps.lib.  The vendor files are read from ../sim/models/vendor_opamps/ at run time."""
    out = ["* vendor op-amp models as published (noise not corrected), translated for ngspice; "
           "written by models.py (prepare_published_opamps)\n"]
    for part in parts:
        m = VENDOR_OPAMPS[part]
        text = translate_model((VENDOR_DIR / m["file"]).read_text(encoding="latin-1"))
        for suffix, kf0 in (("_PUB", False), ("_PUBKF0", True)):
            t = re.sub(r"(\bKF\s*=\s*)[-+0-9.eE]+", r"\g<1>0", text, flags=re.I) if kf0 else text
            inst = m["inst"].split()
            inst[-1] += suffix
            out.append(f"* ---- {part}{suffix}: {m['src']}, " + ("every KF set to 0" if kf0 else "as published")
                       + "\n" + _rename_subckts(t, suffix))
            out.append(f".subckt OA_{part}{suffix} inp inn out vcc vee\nX1 {' '.join(inst)}\n"
                       f".ends OA_{part}{suffix}\n")
    path = spice.LIB / "opamps_published.lib"
    spice.LIB.mkdir(parents=True, exist_ok=True)
    _atomic_write(path, "\n".join(out), "latin-1")
    return path


# ----------------------------------------------------------------------------------------------
# Bipolar transistors: onsemi (Fairchild) cards downloaded from onsemi's model library
# (../sim/models/onsemi_bjt/, https://www.onsemi.com/download/models/lib/<part>.lib), and
# general-purpose cards from LTspice's standard.bjt.  The MMBT3904 file lacks its .MODEL line,
# which is added here; nothing else is changed.
# ----------------------------------------------------------------------------------------------
ONSEMI_BJT = {"MMBTH10": ("mmbth10.lib", "NPN"), "MMBTH81": ("mmbth81.lib", "PNP"),
              "MMBT2369": ("mmbt2369.lib", "NPN"), "MMBT3904": ("mmbt3904.lib", "NPN"),
              "MMBT3906": ("mmbt3906.lib", "PNP")}
LTSPICE_BJT = ("BC847B", "BC857B", "BC817-25", "BC807-25", "2N3904", "2N3906")


def prepare_bjts() -> None:
    folder = spice.ROOT / "sim" / "models" / "onsemi_bjt"
    out = ["* bipolar transistor cards for the low-noise preamplifier note (see models.py)"]
    for name, (fn, pol) in ONSEMI_BJT.items():
        path = folder / fn
        if not path.exists():
            continue
        text = path.read_text(encoding="latin-1").replace("\r", "")
        params = []
        for ln in text.splitlines():
            s = ln.strip()
            if s.startswith("+"):
                params.append(s[1:].strip())
        out.append(f".model {name} {pol}({' '.join(' '.join(params).split())})")
        if name == "MMBT3904":
            # the same die in SOT-223, for the L front end's current sinks (Section 4.2.1 of the note):
            # onsemi's PZT3904T1/D lists the same electrical characteristics as MMBT3904LT1/D
            out.append(f".model PZT3904 {pol}({' '.join(' '.join(params).split())})")
    raw = LTSPICE_BJT_LIB.read_bytes()
    try:
        lt = raw.decode("utf-16")
    except UnicodeError:
        lt = raw.decode("latin-1")
    for name in LTSPICE_BJT:
        for line in lt.splitlines():
            m = re.match(r"\s*\.model\s+(\S+)\s+(NPN|PNP)\s*\((.*)\)\s*$", line, re.I)
            if m and m.group(1).upper() == name.upper():
                params = re.sub(r"\b(vceo|icrating|mfg)\s*=\s*\S+", "", m.group(3), flags=re.I)
                out.append(f".model {name} {m.group(2)}({' '.join(params.split())})")
    _atomic_write(spice.LIB / "bjts.lib", "\n".join(out) + "\n", "utf-8")


class _PrepareLock:
    """A lock file around prepare(): scripts run side by side all call prepare() at start-up, and its
    calibration runs share the folders ../sim/runs/_models/.  A lock older than 15 minutes is taken
    to be left over from a killed process and removed."""

    def __init__(self, path: Path, stale_s: float = 900.0):
        self.path, self.stale_s = path, stale_s

    def __enter__(self):
        import time
        self.path.parent.mkdir(parents=True, exist_ok=True)
        while True:
            try:
                os.close(os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
                return self
            except FileExistsError:
                try:
                    if time.time() - self.path.stat().st_mtime > self.stale_s:
                        self.path.unlink(missing_ok=True)
                        continue
                except FileNotFoundError:
                    continue
                time.sleep(0.5)

    def __exit__(self, *exc):
        self.path.unlink(missing_ok=True)


def prepare(verbose: bool = False) -> dict:
    """Write _lib/jfets.lib with every part, calibrated where targets exist, _lib/opamps.lib and
    _lib/bjts.lib (under a lock file, so that scripts started side by side calibrate one at a time)."""
    with _PrepareLock(spice.RUNS / "_models" / ".prepare.lock"):
        return _prepare(verbose)


def _prepare(verbose: bool = False) -> dict:
    spice.LIB.mkdir(parents=True, exist_ok=True)
    prepare_opamps()
    prepare_bjts()
    if not PARTS:
        default_parts()
    spice.LIB.mkdir(parents=True, exist_ok=True)
    res, text = {}, ["* JFET subcircuits (pins d g s) for the low-noise preamplifier note; see models.py\n"]
    for part in PARTS:
        r = calibrate(part)
        res[part] = r
        text.append(subckt(part, r["rx"], r["card"]))
        if verbose:
            print(part, {k: v for k, v in r.items() if k != "card"})
    _atomic_write(spice.LIB / "jfets.lib", "\n".join(text), "utf-8")
    spice.RESULTS.mkdir(parents=True, exist_ok=True)
    (spice.RESULTS / "jfet_calibration.json").write_text(json.dumps(res, indent=1), encoding="utf-8",
                                                          newline="\n")
    return res


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    prepare(verbose=True)
