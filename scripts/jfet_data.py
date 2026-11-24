"""Low-noise JFETs and commercial preamplifiers: the typical data-sheet values used in the note's
tables and figures.  Every number is from the surveys in ../refs/datasheets/jfet/survey_*.md and
../refs/commercial_preamps/survey.md, which give the document, page and figure of each (c = read off
a curve by eye).  e_n is the input noise density at 1 kHz (or the white level where stated) at the
drain current id; en10 at 10 Hz; ciss the input capacitance in pF at the data sheet's conditions.

Figure of merit for a capacitance budget (Eq. (6) of the note):  FOM = e_n sqrt(C_iss), in
nV sqrt(pF)/rtHz.  'About twice as good per unit of capacitance' (Sections 3.3 and the summary)
compares the LSK389's FOM with the others' as the ratio FOM_LSK389 / FOM_part, once with the
LSK389's data-sheet value (1.6 nV/rtHz) and once with the 1.17 nV/rtHz measured in Cordell's
application note (LIS_appnote_LSK389_Cordell_RevA4, Table 1, p. 5).

`python jfet_data.py` prints Table 3 of the note (sorted by FOM) and those ratios, and writes
../sim/results/jfet_table3.json.
"""
from __future__ import annotations

import json
import math
import sys

# part: (vendor, status, e_n nV/rtHz, id mA, en10 nV/rtHz or None, ciss pF, note)
JFETS = {
    "LSK389":  ("Linear Systems", "active", 1.6, 2.0, 3.2, 25.0, "dual; Rev A27 table (app note: 1.17 measured, "
                "A-weighted, with its test amplifier's second stage)"),
    "LSK170":  ("Linear Systems", "active", 0.9, 2.0, 1.4, 20.0, "single"),
    "LSK489":  ("Linear Systems", "active", 1.8, 2.0, 3.5, 4.0, "dual, low capacitance"),
    "LSBF862": ("Linear Systems", "active", 0.8, 2.0, 1.4, 11.5, "single; e_n at 10 kHz"),
    "JFE150":  ("TI", "active", 0.8, 5.0, 1.8, 24.0, "single; C_iss at V_DS = 5 V"),
    "JFE2140": ("TI", "active", 0.9, 5.0, 2.4, 13.0, "matched dual; e_n at 5 mA off Fig. 6-16 (c), 10 Hz at 2 mA"),
    "JFE2325": ("TI", "active", 4.3, 0.385, None, 0.85, "dual, self-biased gate; e_n at 10 kHz with the gate "
                "grounded, I_D = I_DSS (0.385 mA typ)"),
    "IF3601":  ("InterFET", "active", 0.34, 5.0, 0.60, 650.0, "single (IF3602 dual); c; C_iss table 650, curve 890"),
    "IF4500":  ("InterFET", "active", 0.85, 5.0, 1.10, 55.0, "single; C_iss off curve (table max 35)"),
    "IF9030":  ("InterFET", "active", 0.7, 5.0, None, 60.0, "single; C_iss max"),
    # IF170: 10 Hz from the p. 4 "Typical Noise" curve at 5 mA, 4 V: 1.70 nV/rtHz (read off the
    # curve's vector path; an earlier reading gave 1.72)
    "IF170":   ("InterFET", "active", 1.0, 2.0, 1.70, 20.0, "single, 2SK170 type; C_iss max; 10 Hz at 5 mA"),
    "IF150":   ("InterFET", "active", 3.4, 0.5, 5.5, 2.9, "single, low capacitance; c"),
    "2SK170":  ("Toshiba", "discontinued", 0.95, 1.0, None, 30.0, "single"),
    "2SK369":  ("Toshiba", "discontinued", 0.78, 3.0, None, 75.0, "single; c"),
    # BF862: e_n, C_iss at V_GS = 0, V_DS = 8 V, i.e. at I_D = I_DSS, 10-25 mA (NXP data sheet p. 4);
    # 15 mA is a mid-range value for display only (nothing here uses it)
    "BF862":   ("NXP", "discontinued", 0.8, 15.0, None, 10.0, "single; e_n at 100 kHz at V_GS = 0 (I_DSS, 10-25 mA)"),
    "2N5564":  ("Vishay", "discontinued", 3.9, 2.0, 12.0, 10.0, "dual (SR560: NPD5564); 1 kHz, c"),
    "U401":    ("Vishay", "discontinued", 4.3, 0.2, 10.0, 4.0, "dual; c"),
}


def fom(part: str) -> float:
    v = JFETS[part]
    return v[2] * math.sqrt(v[5])


# commercial instruments: (e_n white nV/rtHz, input capacitance pF, bandwidth, coupling, note)
COMMERCIAL = {
    "SRS SR560":           (4.0, 25.0, "DC-1 MHz", "DC", "1 kHz, gains >= 100"),
    "NF 5307":             (4.0, 35.0, "DC-10 MHz", "DC", "spec; about 3 (2.8-3.1) in NF's plot, gain 100"),
    "NF SA-440F5":         (1.8, 60.0, "DC-20 MHz", "DC", ""),
    "NF SA-421F5":         (0.5, 85.0, "30 Hz-30 MHz", "AC", ""),
    "NF LI-75A":           (2.0, 50.0, "DC-1 MHz", "DC", ""),
    "FEMTO DLPVA-101-B":   (2.0, 105.0, "DC-100 kHz", "DC", ""),
    "Signal Recovery 5113": (4.0, 25.0, "DC-1 MHz", "AC or DC", "1 kHz; about 8 at 1 kHz in its own noise-figure plot"),
    "Signal Recovery 5184": (0.8, 50.0, "0.5 Hz-1 MHz", "AC", ""),
    "Stahl PR-E3":         (0.69, 16.4, "0.5 kHz-4 MHz", "AC", "two channels tied"),
    "BasPI SP1004":        (1.0, 125.0, "DC-1 MHz", "DC", ""),
}

# Figure 1a plots differential input noise against the capacitance per input as connected.  Where
# COMMERCIAL's values (as Table 2 lists them) are on another basis, the figure uses these instead:
FIG1_BASIS = {
    # the -D (true differential) version: 3.0 nV/rtHz at 40-80 dB; the 2.0 of Table 2 is the
    # single-ended -S version (DLPVA-101-B data sheet, DLPVA-101-B_R01T1/TH,UH,MW/27FEB2024, p. 3)
    "FEMTO DLPVA-101-B": dict(en=3.0),
    # 0.69 nV/rtHz is with both channels connected (two inputs in parallel), so the input carries both
    # channels' 16.4 pF (each "at either input"): Stahl PR-E3 4 MHz data sheet v3.12, p. 5, Table 2
    "Stahl PR-E3": dict(cin=2 * 16.4),
}
CORDELL_LSK389 = 1.17        # nV/rtHz measured (A-weighted band, second stage included), LSK389 app note Rev A4, Table 1, p. 5


def fig1_point(name: str) -> tuple[float, float]:
    """(e_n, C per input) of a commercial instrument on Figure 1a's basis."""
    en, cin = COMMERCIAL[name][:2]
    b = FIG1_BASIS.get(name, {})
    return b.get("en", en), b.get("cin", cin)


def table3() -> list[dict]:
    """Table 3 of the note, with the FOM, sorted by FOM."""
    rows = [dict(part=p, vendor=v[0], status=v[1], en=v[2], id_mA=v[3], en10=v[4], ciss_pF=v[5], fom=fom(p), note=v[6])
            for p, v in JFETS.items()]
    return sorted(rows, key=lambda r: r["fom"])


def lsk389_ratios() -> dict:
    """FOM of the LSK389 (data sheet and Cordell's measurement) over every other part's."""
    ref = fom("LSK389")
    ref_m = CORDELL_LSK389 * math.sqrt(JFETS["LSK389"][5])
    return dict(fom_lsk389_datasheet=ref, fom_lsk389_measured=ref_m,
                ratio_datasheet={p: ref / fom(p) for p in JFETS if p != "LSK389"},
                ratio_measured={p: ref_m / fom(p) for p in JFETS if p != "LSK389"})


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    import spice
    rows = table3()
    print(f"{'Part':8s} {'Vendor':15s} {'Status':13s} {'e_n':>5s} {'I_D':>6s} {'e_n10':>6s} {'C_iss':>6s} {'FOM':>5s}  Note")
    for r in rows:
        print(f"{r['part']:8s} {r['vendor']:15s} {r['status']:13s} {r['en']:5.2f} {r['id_mA']:6.3g} "
              f"{r['en10'] if r['en10'] is not None else '-':>6} {r['ciss_pF']:6.3g} {r['fom']:5.2f}  {r['note']}")
    rat = lsk389_ratios()
    print(f"LSK389 FOM {rat['fom_lsk389_datasheet']:.2f} (data sheet), {rat['fom_lsk389_measured']:.2f} (Cordell, 1.17 nV/rtHz)")
    for p in ("JFE2140", "JFE150", "LSBF862", "BF862", "LSK489", "LSK170", "IF170"):
        print(f"  LSK389 / {p:8s}: {rat['ratio_datasheet'][p]:.2f} (data sheet), {rat['ratio_measured'][p]:.2f} (measured)")
    out = dict(table3=rows, lsk389_ratios=rat,
               fig1_basis={n: dict(zip(("en", "cin"), fig1_point(n))) for n in COMMERCIAL},
               fom_definition="e_n sqrt(C_iss), nV sqrt(pF)/rtHz (Eq. (6))")
    (spice.RESULTS / "jfet_table3.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
