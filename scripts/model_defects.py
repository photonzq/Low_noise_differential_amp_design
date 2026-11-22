"""Table 7 of the note (Section 5.3): every number of the table and of its explanatory paragraphs,
computed from the archived results and from small runs of the cards and models as published.

Inputs: ../sim/results/jfet_calibration.json (models.py: the cards' capacitances, g_m, the calibrated
RX and KF), ../sim/results/opamp_noise_check.json (run opamp_noise_check.py first: the published
op-amp models in the two-gain fixture, the H front end with the published THS4021, the chain with the
published THS3091), ../sim/results/da_compare.json (the THS4031's distortion in S2), the vendor files
in ../sim/models/ and LTspice's standard.jft (read at run time from the local LTspice installation;
no card is copied into this project).  k = 1.380649e-23 J/K, T = 300.15 K (ngspice's 27 C).

JFET cards (Eq. (1) of the note; square law I_D = beta (1 + lambda V_DS) (V_GS - V_TO)^2):
    gate-referred 1/f density   e_f^2 = KF I_D / (f g_m^2)
                                 = KF / (4 beta f)                       (g_m = 2 sqrt(beta I_D))
                                 = KF / (4 beta (1 + lambda V_DS) f)     (with channel-length modulation)
    1/f corner against a white level e_w      f_c = KF / (4 beta e_w^2)   (or KF I_D / (g_m^2 e_w^2))
    the card's density at f                    e(f) = sqrt(e_m^2 + e_f^2(f)), e_m its own white noise
    the same card with the calibrated white    sqrt(e_w^2 + e_f^2(f))
    1/f power ratio, data sheet / card          (e_DS(f)^2 - e_w^2) / e_f^2(f) = KF_cal / KF_card
                                               (the two use the same g_m; KF_cal from models.py)
    capacitance ratio                          C_card / C_DS (C_iss, C_rss at the data sheet's V_DS,
                                               ngspice, models.caps)
Small runs (models.bare_noise: drain current from a current source, V_DS held, KF as given):
    JFE2140 and JFE150 cards as published at the data sheets' operating points; the LSBF862 card
    (NLEV, GDSNOI and the other LTspice-only parameters removed, as in models.py); the J310 card at
    11 mA and the V_DS of the J310 current sink.
    LSK389A/B/C cards from LTspice's library at the LSK389 data sheet's noise condition (I_D 2 mA,
    V_DS 10 V; Doc 201122 Rev A27 p. 2): once with NLEV = 3 and GDSNOI as in the card ('with'), once
    without them ('without', the white noise of ngspice's standard channel noise 8kT g_m / 3 plus
    RS and RD); every other LTspice-only parameter (Mfg, Isr, Nr, Alpha, Vk, M, Mj) removed in both.
    The LSK170 cards are compared with the LSK389 cards (identical parameter text: same results).
J310 current sink (the note's Section 6.1 remark): H at a gain of 10 (frontend.CASES['H10']) with a
J310 sink and 6 V across R_T, replace(CASES['H10'], sink='J:J310', v_sink=6.0, v_be_sink=-1.6), AC and
noise runs as in gain_options.noise_checked: the input noise at 10 kHz and the sinks' share.

Op amps (from opamp_noise_check.json, values at 10 Hz unless stated; i: inverting input):
    error ratio = model / data sheet; the data-sheet values and pages are opamp_noise_check.DATASHEET.
    THS4031 HD3 at 10 MHz in S2 (da_compare.json, 1 Vpp at the output): HD3 = 20 log10(h3) dBc; the
    data sheet's figure is at 2 Vpp (G = +2, R_L 1 kohm); a third-order term scales as V_out^2, so
    the model's value at 2 Vpp is HD3 + 20 log10(2^2) = HD3 + 12.04 dB.

Writes ../sim/results/model_defects.json.  Usage: python model_defects.py
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import math
import re
import sys
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import models
import spice

R = spice.RESULTS
KT4 = 4 * spice.KT
LT_ONLY = re.compile(r"\b(mfg|isr|nr|zxti|alpha|vk|m|mj)\s*=\s*\S+", re.I)
NOISE_PARAMS = re.compile(r"\b(gdsnoi|nlev)\s*=\s*\S+", re.I)
LSK389_DS = dict(id=2e-3, vds=10.0, en_1k=1.6e-9, en_10=3.2e-9,
                 src="Linear Systems LSK389 data sheet, Doc 201122 Rev A27 (2023-06-23), p. 2: e_n 1.6 nV/rtHz "
                     "typ at 1 kHz and 3.2 at 10 Hz, V_DS 10 V, I_D 2 mA")
LS_2N5564_PDF = spice.ROOT / "sim" / "models" / "LinearSystems" / "2N5564" / "Copy_2N5564_NJF.txt.pdf"


def num(card: str, key: str, default: float = 0.0) -> float:
    return models._get(card, key, default)


def token(card: str, key: str) -> str | None:
    """A parameter as written in the card (e.g. 'Kf=67860f')."""
    m = re.search(rf"\b{key}\s*=\s*\S+", card, re.I)
    return m.group(0) if m else None


def file_version(path: Path) -> str | None:
    """The file version of a Windows executable (VS_FIXEDFILEINFO), or None."""
    try:
        ver = ctypes.windll.version
        size = ver.GetFileVersionInfoSizeW(str(path), None)
        if not size:
            return None
        buf = ctypes.create_string_buffer(size)
        ver.GetFileVersionInfoW(str(path), 0, size, buf)
        ptr, n = ctypes.c_void_p(), ctypes.c_uint()
        ver.VerQueryValueW(buf, "\\", ctypes.byref(ptr), ctypes.byref(n))
        ffi = ctypes.cast(ptr, ctypes.POINTER(ctypes.c_uint32 * 13)).contents
        ms, ls = ffi[2], ffi[3]
        return f"{ms >> 16}.{ms & 0xffff}.{ls >> 16}.{ls & 0xffff}"
    except (AttributeError, OSError):
        return None


def shown(p: Path) -> str:
    """A path under %LOCALAPPDATA% as written in the results (no user name)."""
    try:
        return str(Path("%LOCALAPPDATA%") / p.relative_to(models.LOCAL_APPDATA))
    except ValueError:
        return p.name


def ltspice_record() -> dict:
    """Where the LTspice cards come from, for the citation: the library file (path, size, date,
    SHA-256, header line), the LTspice version installed, and the change log's JFET entries."""
    lib = models.LTSPICE_JFT
    raw = lib.read_bytes()
    try:
        text = raw.decode("utf-16")
    except UnicodeError:
        text = raw.decode("latin-1")
    head = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    rec = dict(library=shown(lib), size_bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
               modified_utc=datetime.fromtimestamp(lib.stat().st_mtime, timezone.utc).isoformat(timespec="seconds"),
               header=head)
    exe = models.LOCAL_APPDATA / "Programs" / "ADI" / "LTspice" / "LTspice.exe"
    if exe.exists():
        rec.update(ltspice_exe=shown(exe), ltspice_version=file_version(exe),
                   ltspice_exe_modified_utc=datetime.fromtimestamp(exe.stat().st_mtime, timezone.utc)
                   .isoformat(timespec="seconds"))
    log = lib.parents[2] / "ChangeLog.txt"
    if log.exists():
        lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
        rec.update(changelog=shown(log), changelog_latest_entry=lines[0].strip() if lines else None,
                   changelog_jfet_entries=[ln.strip() for ln in lines if re.search(r"\bJFET\b|\.jft\b", ln, re.I)])
    return rec


def ls_listing_kf() -> str | None:
    """The KF token of Linear Systems' own 2N5564 listing (a one-page PDF, read at run time)."""
    try:
        import pymupdf
    except ImportError:
        return None
    if not LS_2N5564_PDF.exists():
        return None
    text = " ".join(page.get_text() for page in pymupdf.open(LS_2N5564_PDF))
    m = re.search(r"\bKf\s*=\s*\S+", text, re.I)
    return m.group(0) if m else None


def vendor_kf(part: str) -> list[str]:
    """The KF tokens of a vendor op-amp file outside comment lines."""
    text = (models.VENDOR_DIR / models.VENDOR_OPAMPS[part]["file"]).read_text(encoding="latin-1")
    return sorted({m.group(0) for ln in text.splitlines() if not ln.lstrip().startswith("*")
                   for m in re.finditer(r"\bKF\s*=\s*[-+0-9.eE]+", ln, re.I)})


def eq1(kf: float, beta: float, f: float, lam_vds: float = 0.0) -> float:
    """Eq. (1): gate-referred 1/f density, square law (with optional 1 + lambda V_DS)."""
    return math.sqrt(kf / (4 * beta * (1 + lam_vds) * f))


# ------------------------------------------------------------------------------------------------
def jfet_rows(cal: dict) -> dict:
    out = {}
    pub = {p: models.PARTS[p]["card"] for p in ("JFE2140", "JFE150", "LSBF862", "2N5564", "J310")}
    # --- JFE2140: 1/f as published, capacitances
    c, k = cal["JFE2140"], pub["JFE2140"]
    ds = models.PARTS["JFE2140"]["cal"]
    run = models.bare_noise("JFE2140", k, ds["id"], ds["vds"], kf_zero=False, tag="_published")
    e_f2 = run["en_10"] ** 2 - run["en_100k"] ** 2
    kf_card, beta = num(k, "kf"), num(k, "beta")
    out["JFE2140 1/f"] = dict(
        card="TI SLPM355 (JFEx140 card)", kf_card=kf_card, kf_calibrated=c["kf"], beta=beta,
        e_1f_10Hz_eq1=eq1(kf_card, beta, 10.0), e_10Hz_eq1_with_card_white=math.hypot(c["en_model_white"], eq1(kf_card, beta, 10.0)),
        e_10Hz_card_ngspice=run["en_10"], e_white_card_ngspice=run["en_100k"],
        e_10Hz_card_with_calibrated_white=math.sqrt(ds["en_w"] ** 2 + e_f2),
        datasheet_10Hz=ds["en_lf"], datasheet_white=ds["en_w"], op=dict(id=ds["id"], vds=ds["vds"]),
        one_over_f_power_ratio_datasheet_to_card=(ds["en_lf"] ** 2 - ds["en_w"] ** 2) / e_f2,
        kf_ratio_calibrated_to_card=c["kf"] / kf_card,
        density_ratio_card_to_datasheet_10Hz=run["en_10"] / ds["en_lf"],
        src=c["src"], note_text="0.2e-18: 1.2 nV/rtHz at 10 Hz, 2 mA | 2.4 | 1/f power 14x too low | KF = 2.9e-18")
    out["JFE2140 capacitances"] = dict(
        ciss_card=c["ciss_card"], crss_card=c["crss_card"], ciss_ds=c["ciss_target"], crss_ds=c["crss_target"],
        vds=ds["vds_c"], ratio_ciss=c["ciss_card"] / c["ciss_target"], ratio_crss=c["crss_card"] / c["crss_target"],
        note_text="8.6 pF, 1.25 pF | 13 pF, 4.2 pF (Fig. 6-17) | 0.66x, 0.30x")
    # --- JFE150: KF consistent, capacitances
    c, k = cal["JFE150"], pub["JFE150"]
    ds = models.PARTS["JFE150"]["cal"]
    run = models.bare_noise("JFE150", k, ds["id"], ds["vds"], kf_zero=False, tag="_published")
    e_f2 = run["en_10"] ** 2 - run["en_100k"] ** 2
    kf_card, beta150 = num(k, "kf"), num(k, "beta")
    out["JFE150 1/f"] = dict(
        card="TI SLPM349I", kf_card=kf_card, kf_calibrated=c["kf"], beta=beta150,
        kf_ratio_calibrated_to_card=c["kf"] / kf_card, kf_difference_percent=100 * (c["kf"] / kf_card - 1),
        e_1f_10Hz_eq1=eq1(kf_card, beta150, 10.0),
        e_10Hz_card_ngspice=run["en_10"], e_white_card_ngspice=run["en_100k"],
        e_10Hz_card_with_calibrated_white=math.sqrt(ds["en_w"] ** 2 + e_f2),
        datasheet_10Hz=ds["en_lf"], op=dict(id=ds["id"], vds=ds["vds"]),
        density_difference_percent_card_with_calibrated_white=100 * (math.sqrt(ds["en_w"] ** 2 + e_f2) / ds["en_lf"] - 1),
        note_text="3.25e-18 | 1.8 nV/rtHz at 10 Hz, 5 mA | consistent (7 %) | KF = 3.5e-18")
    out["JFE150 capacitances"] = dict(
        ciss_card=c["ciss_card"], crss_card=c["crss_card"], ciss_ds=c["ciss_target"], crss_ds=c["crss_target"],
        vds=ds["vds_c"], ratio_ciss=c["ciss_card"] / c["ciss_target"], ratio_crss=c["crss_card"] / c["crss_target"],
        note_text="17.8 pF, 2.3 pF | 24 pF, 4.5 pF (Fig. 6-12) | 0.74x, 0.50x")
    # --- the process argument of the TI paragraph
    out["TI process argument"] = dict(
        beta_JFE150=beta150, beta_JFE2140=beta, beta_ratio=beta150 / beta,
        kf_card_ratio_JFE150_to_JFE2140=kf_card / out["JFE2140 1/f"]["kf_card"],
        kf_calibrated_JFE2140=cal["JFE2140"]["kf"], kf_card_JFE150=kf_card, kf_calibrated_JFE150=c["kf"],
        crss_ratios=[out["JFE2140 capacitances"]["ratio_crss"], out["JFE150 capacitances"]["ratio_crss"]],
        density_ratio_JFE2140_card_to_datasheet_10Hz=out["JFE2140 1/f"]["density_ratio_card_to_datasheet_10Hz"],
        grading_M_in_cards={p: ti_raw_param(p, "m") for p in ("JFE150", "JFE2140")},
        note_text="beta = 31 mA/V^2; beta = 14.24 mA/V^2; KF 0.2e-18 'sixteen times less'; 1.2 against 2.4; "
                  "KF 2.9e-18; 'half the true 1/f noise'; C_rss 30-50 % of the data sheet's; M = 0.33")
    # --- LSBF862: KF of NXP's BF862 model, capacitances
    c, k = cal["LSBF862"], pub["LSBF862"]
    ds = models.PARTS["LSBF862"]["cal"]
    run = models.bare_noise("LSBF862", k, ds["id"], ds["vds"], kf_zero=False, tag="_published")
    kf_card, beta, lam = num(k, "kf"), num(k, "beta"), num(k, "lambda")
    out["LSBF862 1/f"] = dict(
        card="Linear Systems LSBF862, Rev 2 (2026-02-09)", kf_card=kf_card, kf_calibrated=c["kf"], beta=beta,
        lambda_=lam, e_1f_10Hz_eq1=eq1(kf_card, beta, 10.0),
        e_1f_10Hz_eq1_with_lambda=eq1(kf_card, beta, 10.0, lam * ds["vds"]),
        e_10Hz_card_ngspice=run["en_10"], e_white_card_ngspice=run["en_100k"], op=dict(id=ds["id"], vds=ds["vds"]),
        datasheet_10Hz_typ=ds["en_lf"], datasheet_10Hz_max=4.0e-9,
        kf_ratio_card_to_calibrated=kf_card / c["kf"],
        one_over_f_power_ratio_card_to_datasheet=(run["en_10"] ** 2 - run["en_100k"] ** 2) / (ds["en_lf"] ** 2 - ds["en_w"] ** 2),
        kf_of_NXP_BF862_model=87.5e-18,
        calibration=dict(en_target_white=c["en_target_white"], en_achieved_white=c["en_achieved_white"],
                         rx=c["rx"], rx_clipped=c["rx_clipped"], en_achieved_10Hz=c["en_achieved_lf"]),
        src=c["src"] + "; maximum 4.0 nV/rtHz at 10 Hz on the same page",
        note_text="8.75e-17: about 9 nV/rtHz at 10 Hz | 1.4 typ, 4.0 max | 1/f power 50x too high | KF = 1.74e-18")
    out["LSBF862 capacitances"] = dict(
        ciss_card=c["ciss_card"], crss_card=c["crss_card"], ciss_ds=c["ciss_target"], crss_ds=c["crss_target"],
        vds=ds["vds_c"], ratio_ciss=c["ciss_card"] / c["ciss_target"], ratio_crss=c["crss_card"] / c["crss_target"],
        note_text="6.5 pF, 0.87 pF | 11.5 pF, 3.5 pF | 0.56x, 0.25x")
    # --- 2N5564 (LTspice) KF: unit prefix
    c, k = cal["2N5564"], pub["2N5564"]
    raw = models.ltspice_raw("2N5564")
    kf_lt, beta = num(raw, "kf"), num(raw, "beta")
    ls_tok = ls_listing_kf()
    kf_ls = num(ls_tok, "kf") if ls_tok else 6.786e-17
    e_w = c["en_target_white"]
    out["2N5564 KF"] = dict(
        ltspice_token=token(raw, "kf"), kf_ltspice=kf_lt, linear_systems_token=ls_tok, kf_linear_systems=kf_ls,
        linear_systems_listing=str(LS_2N5564_PDF.relative_to(spice.ROOT)), ratio=kf_lt / kf_ls, beta=beta,
        e_1f_eq1={f"{f:g}": eq1(kf_lt, beta, f) for f in (10.0, 1e3, 1e6)},
        corner_eq1_with_calibrated_white=kf_lt / (4 * beta * e_w ** 2),
        corner_eq1_with_card_white=kf_lt / (4 * beta * c["en_model_white"] ** 2),
        corner_ngspice_gm_with_calibrated_white=kf_lt * c["id"] / (c["gm"] ** 2 * e_w ** 2),
        kf_calibrated=c["kf"], calibrated_white=e_w, op=dict(id=c["id"], vds=c["vds"], gm=c["gm"]),
        note_text="67860f = 6.786e-11 | 6.786e-002f = 6.786e-17 | x 10^6 (unit prefix); "
                  "paragraph: 'puts the 1/f corner ... in the megahertz range'")
    return out


def j310(cal: dict) -> dict:
    """The J310 card's KF, its gate-referred 1/f at 10 kHz and 11 mA, and the J310 sink run."""
    import frontend as F
    import gain_options as GO
    import sink_options as SO
    raw = models.ltspice_raw("J310")
    card = models.PARTS["J310"]["card"]
    kf, beta, lam = num(card, "kf"), num(card, "beta"), num(card, "lambda")
    p = replace(F.CASES["H10"], name="H10_sink_J310_6V", sink="J:J310", v_sink=6.0, v_be_sink=-1.6)
    op = SO.op_point(p)
    i_sink, vds = op["i_sink"], op["v_ce"]
    run = models.bare_noise("J310", card, i_sink, vds, kf_zero=False, tag="_sink")
    ac = F.check_ac(p)
    nz, gain, how = GO.noise_checked(p, ac)
    grp = F.noise_groups(nz["nz"], gain)
    fr = nz["f"]
    sinks = {f"{f0:g}": spice.at(fr, grp["current sinks"], f0) for f0 in (10.0, 1e3, 1e4, 1e5)}
    res = dict(
        ltspice_token=token(raw, "kf"), kf=kf, beta=beta, lambda_=lam,
        e_1f_10kHz_eq1=eq1(kf, beta, 1e4), e_1f_10kHz_eq1_with_lambda=eq1(kf, beta, 1e4, lam * vds),
        e_10kHz_card_ngspice=run["en_10k"], gm_card_ngspice=run["gm"],
        e_1f_10kHz_ngspice_gm=math.sqrt(kf * i_sink / (1e4 * run["gm"] ** 2)),
        sink_op=op, sink_current=i_sink, sink_vds=vds,
        sink_run=dict(case="replace(frontend.CASES['H10'], sink='J:J310', v_sink=6.0, v_be_sink=-1.6)",
                      noise_op=how, f3db=ac["f3db"], gain_1k=ac["gain_1k"],
                      en={k: v for k, v in nz["en"].items()}, sinks=sinks),
        note_text="46340f = 4.634e-11: about 0.6 uV/rtHz gate-referred at 10 kHz and 11 mA; "
                  "61 nV/rtHz at 10 kHz (H, gain 10)")
    print(f"J310: KF {kf:.4g} ({res['ltspice_token']}); Eq. (1) at 10 kHz {res['e_1f_10kHz_eq1'] * 1e6:.3f} uV/rtHz "
          f"(with lambda V_DS {res['e_1f_10kHz_eq1_with_lambda'] * 1e6:.3f}); card in ngspice at {i_sink * 1e3:.2f} mA, "
          f"V_DS {vds:.2f} V: {run['en_10k'] * 1e6:.3f} uV/rtHz.  Sink run: input noise at 10 kHz "
          f"{nz['en']['10000.0'] * 1e9:.2f} nV/rtHz (sinks {sinks['10000'] * 1e9:.2f}) [{how}]", flush=True)
    return res


def lsk389_nlev() -> dict:
    """The LSK389 cards with and without NLEV/GDSNOI at the data sheet's noise condition."""
    out = {}
    for part in ("LSK389A", "LSK389B", "LSK389C"):
        raw = models.ltspice_raw(part)
        with_ = " ".join(LT_ONLY.sub("", raw).split())
        without = " ".join(NOISE_PARAMS.sub("", with_).split())
        a = models.bare_noise(part, with_, LSK389_DS["id"], LSK389_DS["vds"], kf_zero=False, tag="_nlev3")
        b = models.bare_noise(part, without, LSK389_DS["id"], LSK389_DS["vds"], kf_zero=False, tag="_nonlev")
        twin = part.replace("389", "170")
        out[part] = dict(
            nlev=token(raw, "nlev"), gdsnoi=token(raw, "gdsnoi"), kf=token(raw, "kf"), gm=a["gm"],
            with_nlev_gdsnoi=dict(en_white_100k=a["en_100k"], en_1k=a["en_1k"], en_10=a["en_10"]),
            without_nlev_gdsnoi=dict(en_white_100k=b["en_100k"], en_1k=b["en_1k"], en_10=b["en_10"]),
            ratio_white_with_to_without=a["en_100k"] / b["en_100k"],
            same_card_as=twin if models.ltspice_raw(twin) == raw else None)
        print(f"{part} ({out[part]['nlev']}, {out[part]['gdsnoi']}) at 2 mA, 10 V: white {a['en_100k'] * 1e9:.3f} nV/rtHz "
              f"with NLEV/GDSNOI, {b['en_100k'] * 1e9:.3f} without (1 kHz {a['en_1k'] * 1e9:.3f} / {b['en_1k'] * 1e9:.3f})",
              flush=True)
    out["datasheet"] = LSK389_DS
    out["note_text"] = "NLEV = 3, GDSNOI = 5-8 ... in ngspice 1.41 vs 0.86 nV/rtHz (an LSK389 card gave 1.41 instead of 0.86)"
    return out


def jfe2325_flicker(cal: dict) -> dict:
    """Not in Table 7: the JFE2325 card's 1/f (KF kept by models.py) against the data sheet's curve,
    by Eq. (1) with the calibration's g_m and I_D (V_GS = 0); the simulated spectrum is in
    jfet_model_check.json ('JFE2325')."""
    from jfet_model_check import FIG_5_24
    c = cal["JFE2325"]
    # the card as published: models.py now fits the JFE2325's KF to Fig. 5-24 and keeps the card's own
    # KF as 'kf_card' (the calibrated card's KF would make this comparison circular)
    kf = c["kf_card"] if "kf_card" in c else num(c["card"], "kf")
    e10 = math.sqrt(kf * c["id"] / (10.0 * c["gm"] ** 2))
    fig = dict(FIG_5_24)
    p_ds = (fig[10.0] ** 2 - fig[1e5] ** 2) * 1e-18
    return dict(kf=kf, id=c["id"], gm=c["gm"], e_1f_10Hz_model=e10, e_10Hz_datasheet_fig=fig[10.0] * 1e-9,
                e_white_datasheet_fig=fig[1e5] * 1e-9, one_over_f_power_ratio_10Hz=e10 ** 2 / p_ds,
                src="SLPS816A Fig. 5-24, p. 9 (gate connected to ground), read by eye (jfet_model_check.FIG_5_24)",
                remark="not in Table 7: the card's 1/f power at 10 Hz against the data sheet's curve")


def ti_raw_param(part: str, key: str) -> str | None:
    """A parameter of a TI JFET card as written in TI's file (M is removed from the cleaned card)."""
    path = {"JFE150": ("JFE150", "slpm349i", "jfe150.lib"), "JFE2140": ("JFE2140", "slpm355", "jfex140.lib")}[part]
    text = (models.VENDOR_JFET / "TI").joinpath(*path).read_text(encoding="latin-1")
    m = re.search(r"^\.model\s+\S+\s+NJF\s*\((.*?)\)", text, re.I | re.M | re.S)
    return token(m.group(1).replace("\n+", " "), key) if m else None


# ------------------------------------------------------------------------------------------------
def opamp_rows(onc: dict) -> dict:
    import opamp_noise_check as O
    t7 = onc["table7"]
    out = {}
    for part in models.PUBLISHED:
        r, ds = t7[part], O.DATASHEET[part]
        row = dict(model=r["model"], kf_tokens_in_file=vendor_kf(part),
                   e_n_10=r["e_n_10"], i_n_10=r["i_n_10"], e_n_white=r["e_n_white_kf0"], i_n_white=r["i_n_white_kf0"],
                   datasheet=ds,
                   ratio_e_10=r["e_n_10"] / ds["e_10"], ratio_i_10=(r["i_n_10"] / ds["i_10"]) if ds["i_10"] else None,
                   ratio_e_white=r["e_n_white_kf0"] / ds["e_w"], ratio_i_white=r["i_n_white_kf0"] / ds["i_w"],
                   corner_i_model=r["corner_i_model"], corner_i_model_vs_datasheet_white=r["corner_i_model_vs_datasheet_white"],
                   corner_i_model_100kHz_as_white=r["corner_i_model_100kHz_as_white"],
                   corner_i_datasheet=r["corner_i_datasheet"], corner_e_model=r["corner_e_model"],
                   corner_e_datasheet=r["corner_e_datasheet"], note_table7=r["note_table7"])
        out[part] = row
    da = json.loads((R / "da_compare.json").read_text(encoding="utf-8"))
    h3 = next(t["h3"] for t in da["THS4031"]["thd"] if t["f0"] == 1e7 and t["vout_pp"] == 1.0)
    hd3 = 20 * math.log10(h3)
    ds_hd3 = -50.0
    out["THS4031 HD3"] = dict(
        h3=h3, hd3_dBc_1Vpp=hd3, hd3_dBc_scaled_to_2Vpp=hd3 + 20 * math.log10(4.0), datasheet_dBc_2Vpp=ds_hd3,
        excess_unscaled_dB=hd3 - ds_hd3, excess_scaled_dB=hd3 + 20 * math.log10(4.0) - ds_hd3,
        datasheet_src="SLOS224L Fig. 5-15, p. 12 (+/-15 V, G = +2, R_L 1 kohm, 2 Vpp): the HD3 curve reaches the "
                      "plot's top edge, -50 dBc, at 10 MHz (read by eye)",
        model_src="da_compare.json THS4031.thd (10 MHz, 1 Vpp at the output, S2 at unity gain)",
        note_text="-37 dBc at 1 Vpp (in S2) | about -50 dBc at 2 Vpp, G = 2 (Fig. 5-15) | about 20 dB too high")
    fe = onc["H100 front end, published THS4021"]
    ch = onc["chain, published THS3091"]
    out["THS4021 in the H front end"] = dict(
        en_10Hz_published=fe["published"]["en"]["10"], en_10Hz_corrected=fe["corrected"]["en"]["10"],
        ratio_10Hz=fe["ratio_published_to_corrected"]["10"], en_1Hz_published=fe["published"]["en"]["1"],
        en_1Hz_corrected=fe["corrected"]["en"]["1"], loop_op_amps_10Hz_published=fe["published"]["groups_10Hz"]["loop op amps"],
        loop_op_amps_10Hz_corrected=fe["corrected"]["groups_10Hz"]["loop op amps"],
        note_text="the H front end showed 11.3 nV/rtHz at 10 Hz, four times the 2.7 nV/rtHz it has with the corrected model")
    out["THS3091 in the chain"] = dict(
        {k: dict(ratio_1Hz=v["ratio_published_to_corrected"]["1"], published_1Hz=v["published"]["1"],
                 corrected_1Hz=v["corrected"]["1"], ratio_10Hz=v["ratio_published_to_corrected"]["10"],
                 ratio_10kHz=v["ratio_published_to_corrected"]["10000"], setting=v["setting"])
         for k, v in ch.items()},
        note_text="at low gains, where the THS3091 output stage dominates, it put the noise at 1 Hz too high by a factor of 1.8")
    return out


def table_rows(j: dict, o: dict) -> list[dict]:
    """Table 7 as rows: model value, data sheet, error (with the JSON keys they come from)."""
    n, p = 1e9, 1e12
    rows = [
        ("TI JFE2140 (SLPM355)", "1/f, KF", f"{j['JFE2140 1/f']['kf_card']:.2g}: {j['JFE2140 1/f']['e_10Hz_card_ngspice'] * n:.3f} nV/rtHz at 10 Hz "
         f"(card's white; Eq. (1) {j['JFE2140 1/f']['e_10Hz_eq1_with_card_white'] * n:.3f}; with the calibrated white "
         f"{j['JFE2140 1/f']['e_10Hz_card_with_calibrated_white'] * n:.3f})", "2.4 nV/rtHz (SLPS730B Table 6.5)",
         f"1/f power {j['JFE2140 1/f']['one_over_f_power_ratio_datasheet_to_card']:.2f}x too low", "jfet/JFE2140 1/f"),
        ("TI JFE2140", "C_iss, C_rss at 5 V", f"{j['JFE2140 capacitances']['ciss_card'] * p:.3f} pF, {j['JFE2140 capacitances']['crss_card'] * p:.3f} pF",
         "13 pF, 4.2 pF", f"{j['JFE2140 capacitances']['ratio_ciss']:.3f}x, {j['JFE2140 capacitances']['ratio_crss']:.3f}x",
         "jfet/JFE2140 capacitances"),
        ("TI JFE150 (SLPM349I)", "1/f, KF", f"{j['JFE150 1/f']['kf_card']:.3g} (10 Hz: {j['JFE150 1/f']['e_10Hz_card_with_calibrated_white'] * n:.3f} "
         f"nV/rtHz with the calibrated white)", "1.8 nV/rtHz at 10 Hz, 5 mA",
         f"KF {j['JFE150 1/f']['kf_difference_percent']:+.1f} % (calibrated {j['JFE150 1/f']['kf_calibrated']:.4g})", "jfet/JFE150 1/f"),
        ("TI JFE150", "C_iss, C_rss at 5 V", f"{j['JFE150 capacitances']['ciss_card'] * p:.3f} pF, {j['JFE150 capacitances']['crss_card'] * p:.3f} pF",
         "24 pF, 4.5 pF", f"{j['JFE150 capacitances']['ratio_ciss']:.3f}x, {j['JFE150 capacitances']['ratio_crss']:.3f}x",
         "jfet/JFE150 capacitances"),
        ("Linear Systems LSBF862 (Rev 2)", "1/f, KF", f"{j['LSBF862 1/f']['kf_card']:.3g}: {j['LSBF862 1/f']['e_1f_10Hz_eq1'] * n:.2f} nV/rtHz at 10 Hz "
         f"by Eq. (1) ({j['LSBF862 1/f']['e_10Hz_card_ngspice'] * n:.2f} in ngspice, with lambda V_DS)", "1.4 typ, 4.0 max",
         f"1/f power {j['LSBF862 1/f']['kf_ratio_card_to_calibrated']:.1f}x too high", "jfet/LSBF862 1/f"),
        ("Linear Systems LSBF862", "C_iss, C_rss at 8 V", f"{j['LSBF862 capacitances']['ciss_card'] * p:.3f} pF, {j['LSBF862 capacitances']['crss_card'] * p:.3f} pF",
         "11.5 pF, 3.5 pF", f"{j['LSBF862 capacitances']['ratio_ciss']:.3f}x, {j['LSBF862 capacitances']['ratio_crss']:.3f}x",
         "jfet/LSBF862 capacitances"),
        ("LTspice standard.jft 2N5564", "KF", f"{j['2N5564 KF']['ltspice_token']} = {j['2N5564 KF']['kf_ltspice']:.4g}",
         f"Linear Systems' listing: {j['2N5564 KF']['linear_systems_token']} = {j['2N5564 KF']['kf_linear_systems']:.4g}",
         f"x {j['2N5564 KF']['ratio']:.3g}; 1/f corner {j['2N5564 KF']['corner_eq1_with_calibrated_white'] / 1e9:.2f} GHz", "jfet/2N5564 KF"),
        ("LTspice standard.jft J310", "KF", f"{j['J310']['ltspice_token']} = {j['J310']['kf']:.4g}: {j['J310']['e_1f_10kHz_eq1'] * 1e6:.3f} uV/rtHz "
         f"gate-referred at 10 kHz (Eq. (1)); {j['J310']['e_10kHz_card_ngspice'] * 1e6:.3f} in ngspice at "
         f"{j['J310']['sink_current'] * 1e3:.1f} mA", "-",
         f"H at a gain of 10 with a J310 sink: {j['J310']['sink_run']['en']['10000.0'] * n:.1f} nV/rtHz at 10 kHz", "jfet/J310"),
        ("Linear Systems LSK389B (LTspice)", "channel noise", f"{j['LSK389']['LSK389B']['nlev']}, {j['LSK389']['LSK389B']['gdsnoi']}",
         "1.6 nV/rtHz (Rev A27 p. 2)",
         f"ngspice at 2 mA, 10 V: {j['LSK389']['LSK389B']['with_nlev_gdsnoi']['en_white_100k'] * n:.3f} with NLEV/GDSNOI, "
         f"{j['LSK389']['LSK389B']['without_nlev_gdsnoi']['en_white_100k'] * n:.3f} without", "jfet/LSK389"),
    ]
    for part, ds_txt in (("THS4021", "4 nV/rtHz, 18.6 pA/rtHz (SLOS265F Figs. 5-11, 5-12)"),
                         ("THS4031", "4 nV/rtHz, 18.6 pA/rtHz (SLOS224L Figs. 5-13, 5-14)"),
                         ("THS3091", "6.5 nV/rtHz, 200 pA/rtHz (SLOS423K Fig. 7-16)")):
        r = o[part]
        rows.append((f"TI {part}", "e_n, i_n- at 10 Hz", f"{r['e_n_10'] * n:.2f} nV/rtHz, {r['i_n_10'] * p:.1f} pA/rtHz", ds_txt,
                     f"{r['ratio_e_10']:.2f}x, {r['ratio_i_10']:.2f}x", f"opamp/{part}"))
    rows.append(("TI THS4031", "HD3 at 10 MHz", f"{o['THS4031 HD3']['hd3_dBc_1Vpp']:.1f} dBc at 1 Vpp (in S2)",
                 "about -50 dBc at 2 Vpp, G = 2 (Fig. 5-15)",
                 f"{o['THS4031 HD3']['excess_unscaled_dB']:.1f} dB as read; {o['THS4031 HD3']['excess_scaled_dB']:.1f} dB "
                 "after scaling to 2 Vpp", "opamp/THS4031 HD3"))
    r = o["THS3091"]
    rows.append(("TI THS3091", "white i_n-", f"{r['i_n_white'] * p:.3f} pA/rtHz", "14 pA/rtHz (SLOS423K Sec. 7.5, p. 6)",
                 f"{r['ratio_i_white']:.3f}x", "opamp/THS3091"))
    r = o["LM7171"]
    rows.append(("TI LM7171 (SNOM205A)", "white e_n; 1/f", f"{r['e_n_white'] * n:.3f} nV/rtHz; none (10 Hz: {r['e_n_10'] * n:.3f})",
                 "8.5 nV/rtHz (A grade, SNOS760D Sec. 5.5 p. 5); 43 nV/rtHz at 10 Hz (Fig. 5-16)",
                 f"{r['ratio_e_white']:.3f}x; missing", "opamp/LM7171"))
    return [dict(model=a, quantity=b, model_gives=c, data_sheet=d, error=e, json_key=f) for a, b, c, d, e, f in rows]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    cal = json.loads((R / "jfet_calibration.json").read_text(encoding="utf-8"))
    onc = json.loads((R / "opamp_noise_check.json").read_text(encoding="utf-8"))
    if "table7" not in onc:
        raise SystemExit("run opamp_noise_check.py first (opamp_noise_check.json has no 'table7')")
    j = jfet_rows(cal)
    j["J310"] = j310(cal)
    j["LSK389"] = lsk389_nlev()
    j["JFE2325 1/f (not in Table 7)"] = jfe2325_flicker(cal)
    o = opamp_rows(onc)
    lt = ltspice_record()
    lt["cards"] = {p: dict(kf=token(models.ltspice_raw(p), "kf"), nlev=token(models.ltspice_raw(p), "nlev"),
                           gdsnoi=token(models.ltspice_raw(p), "gdsnoi"))
                   for p in ("2N5564", "J310", "LSK389A", "LSK389B", "LSK389C", "LSK170A", "LSK170B", "LSK170C")}
    # the summary list of the note's line 19, from the rows above
    summary = {
        "JFE2140 1/f power too low (KF ratio)": j["JFE2140 1/f"]["kf_ratio_calibrated_to_card"],
        "LSBF862 1/f power too high (KF ratio)": j["LSBF862 1/f"]["kf_ratio_card_to_calibrated"],
        "2N5564 KF factor (LTspice / Linear Systems)": j["2N5564 KF"]["ratio"],
        "e_n at 10 Hz, model / data sheet (THS4021, THS4031, THS3091)": [o[p]["ratio_e_10"] for p in ("THS4021", "THS4031", "THS3091")],
        "i_n- at 10 Hz, model / data sheet (THS4021, THS4031)": [o[p]["ratio_i_10"] for p in ("THS4021", "THS4031")],
        "THS3091 white i_n-, model / data sheet": o["THS3091"]["ratio_i_white"],
        "LM7171 white e_n, model / data sheet": o["LM7171"]["ratio_e_white"],
        "LSK389B white e_n in ngspice, with / without NLEV and GDSNOI (nV/rtHz)": (
            j["LSK389"]["LSK389B"]["with_nlev_gdsnoi"]["en_white_100k"] * 1e9,
            j["LSK389"]["LSK389B"]["without_nlev_gdsnoi"]["en_white_100k"] * 1e9),
        "H front end at 10 Hz, published / corrected THS4021 (nV/rtHz, ratio)": (
            o["THS4021 in the H front end"]["en_10Hz_published"] * 1e9, o["THS4021 in the H front end"]["en_10Hz_corrected"] * 1e9,
            o["THS4021 in the H front end"]["ratio_10Hz"]),
        "chain at a gain of 1, 1 Hz, published / corrected THS3091": o["THS3091 in the chain"]["H_LN_1"]["ratio_1Hz"],
        "J310 sink, H at a gain of 10: input noise at 10 kHz (nV/rtHz)": j["J310"]["sink_run"]["en"]["10000.0"] * 1e9,
        "2N5564 1/f corner with KF = 67860f, Eq. (1) with the calibrated white (Hz)": j["2N5564 KF"]["corner_eq1_with_calibrated_white"],
        "J310 gate-referred 1/f at 10 kHz, Eq. (1) (V/rtHz)": j["J310"]["e_1f_10kHz_eq1"],
        "LSBF862 card at 10 Hz, Eq. (1) (V/rtHz)": j["LSBF862 1/f"]["e_1f_10Hz_eq1"],
        "JFE2140 card at 10 Hz, ngspice, card's own white (V/rtHz)": j["JFE2140 1/f"]["e_10Hz_card_ngspice"],
        "JFE150 KF, calibrated / card": j["JFE150 1/f"]["kf_ratio_calibrated_to_card"],
    }
    res = dict(table7=table_rows(j, o), jfet=j, opamp=o, ltspice_library=lt, summary=summary)
    for row in res["table7"]:
        print(f"{row['model']:34s} | {row['quantity']:20s} | {row['model_gives']} | {row['data_sheet']} | {row['error']}")
    print(json.dumps(summary, indent=1))
    print(json.dumps({k: v for k, v in lt.items() if k != "cards"}, indent=1))
    (R / "model_defects.json").write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
