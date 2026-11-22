"""Check of the NF 5307 plot readings by locating the curves' pixels in the published images.

The note and refs/commercial_preamps/survey.md quote values read by eye from two NF 5307 plots
(scripts/numbers_s6_7.py, constants NF_CMRR_PLOT and NF_EN_PLOT_*):
  - CMRR vs frequency, Fig. 46 of NF's data-sheet web page
    (refs/commercial_preamps/NF_Corporation/NF_5307_datasheet_fig46.jpg);
  - equivalent input noise density, Fig. 4.7 of the English instruction manual
    (refs/commercial_preamps/NF_Corporation/NF_5307_instruction_manual_EN.pdf, PDF p. 37, printed p. 25).
This script reads the same curves from the pixels and writes sim/results/nf5307_plot_check.json.

Method.
  Fig. 46 (linear dB axis, log frequency axis): the grid lines are the columns and rows that are dark over
  most of the frame.  The frequency axis is a straight-line fit of the decade lines' x against
  log10(f); the dB axis a straight-line fit of the major rows' y against their labels (rows hidden by
  the curve labels are not used).  In each column, curves are the dark runs 3-6 px thick that are not
  on a grid row (grid lines are 1-2 px, label strokes and arrows 1-2 px or much thicker); columns
  within 2 px of a vertical grid line, or with other than four such runs, are skipped.  The four runs
  are, from the top, the gains 100, 50, 20 and 10 (x1) curves.  Each curve is fitted with a straight
  line over the columns within 8 px of the target frequency and read there.
  Fig. 4.7 (log-log, rendered at 400 dpi): the printed axes are not on a uniform log scale (the minor
  ticks sit up to about 0.04 decade from where a log scale between the decade lines puts them), so
  every value is read twice: by log interpolation between the printed ticks, and on a uniform log scale
  between the decade lines (frame top = 1 uV/rtHz, frame bottom = 1 nV/rtHz).  The two flat parts are
  the rows dark over a large part of the frame width; the sloped parts are read in columns with
  exactly two curve runs (4-30 px thick), the upper being gain 10 x1 and the lower gain 100 x1.
No simulation.  Usage: python nf5307_plot_check.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pymupdf
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
NF = ROOT / "refs" / "commercial_preamps" / "NF_Corporation"
OUT = ROOT / "sim" / "results" / "nf5307_plot_check.json"


def runs(col: np.ndarray, lo: int, hi: int, skip: set | None = None) -> list[tuple[float, int]]:
    """Dark runs (centre, thickness) of a boolean column between rows lo and hi."""
    skip = skip or set()
    out, y = [], lo
    while y < hi:
        if col[y] and y not in skip:
            y0 = y
            while y < hi and col[y] and y not in skip:
                y += 1
            out.append(((y0 + y - 1) / 2.0, y - y0))
        else:
            y += 1
    return out


def groups(ix: np.ndarray, gap: int = 2) -> list[float]:
    """Centres of groups of neighbouring indices."""
    out, cur = [], [int(ix[0])]
    for i in ix[1:]:
        if i - cur[-1] <= gap:
            cur.append(int(i))
        else:
            out.append(float(np.mean(cur)))
            cur = [int(i)]
    out.append(float(np.mean(cur)))
    return out


def fig46() -> dict:
    img = np.asarray(Image.open(NF / "NF_5307_datasheet_fig46.jpg").convert("L")).astype(float)
    dark = img < 110
    vlines = groups(np.where(dark[60:560, :].mean(axis=0) > 0.6)[0])
    hlines = groups(np.where(dark[:, 70:790].mean(axis=1) > 0.6)[0])
    # decade lines: 10 Hz ... 1 MHz are the 1st, 10th, 19th, ... of the detected vertical lines
    dec = [vlines[0]] + [vlines[i] for i in range(9, len(vlines), 9)]
    assert len(dec) == 6, dec
    ax, bx = np.polyfit(np.arange(1, 7), dec, 1)                       # x = ax*log10(f) + bx
    # major rows: 160, 140, 120, (100 hidden by a label), 80, 60, 40, 20 dB
    labels = {160: None, 140: None, 120: None, 80: None, 60: None, 40: None, 20: None}
    assert len(hlines) == 7, hlines
    for lab, y in zip(labels, hlines):
        labels[lab] = y
    ay, by = np.polyfit(list(labels.values()), list(labels.keys()), 1)  # dB = ay*y + by
    y100 = (100 - by) / ay
    grid_rows = set(int(round(y)) + d for y in list(labels.values()) + [y100] for d in (-2, -1, 0, 1, 2))
    vgrid = np.where(dark[60:560, :].mean(axis=0) > 0.35)[0]

    def read(f: float, span: tuple[int, int] | None = None) -> list[float]:
        """The four curves at f, from the columns within 8 px of it, or from the columns in span
        (an x range, for 1 MHz, which lies on the frame: a straight-line extrapolation)."""
        xc = ax * np.log10(f) + bx
        cols = []
        for x in (range(span[0], span[1] + 1) if span else range(int(xc) - 8, int(xc) + 9)):
            if x < 58 or x > 800 or np.min(np.abs(vgrid - x)) <= 2:
                continue
            r = [c for c, w in runs(dark[:, x], 37, 570, grid_rows) if 3 <= w <= 6]
            if len(r) != 4:
                # a curve lying on a grid row: keep the rows, so that the curve and the row make one
                # run 3-7 px thick, while a grid row alone (1-2 px) still drops out
                r = [c for c, w in runs(dark[:, x], 37, 570) if 3 <= w <= 7]
            if len(r) == 4:
                cols.append((x, r))
        if len(cols) < 2:
            return [float("nan")] * 4
        xs = np.array([c[0] for c in cols], float)
        vals = []
        for k in range(4):
            ys = np.array([c[1][k] for c in cols])
            p = np.polyfit(xs, ys, 1) if np.ptp(xs) > 0 else (0.0, ys.mean())
            vals.append(round(float(ay * np.polyval(p, xc) + by), 1))
        return vals

    freqs = [10, 100, 1e3, 3e3, 1e4, 2e4, 3e4, 1e5, 2e5, 5e5]
    names = ["gain_100x1", "gain_50x1", "gain_20x1", "gain_10x1"]
    table = {f"{f:g}": dict(zip(names, read(f))) for f in freqs}
    x_400k = int(ax * np.log10(4e5) + bx)
    table["1e+06 (straight-line extrapolation of 0.4-0.95 MHz)"] = dict(zip(names, read(1e6, (x_400k, 800))))
    return {"file": "refs/commercial_preamps/NF_Corporation/NF_5307_datasheet_fig46.jpg",
            "axes": {"x_per_decade_px": round(float(ax), 2), "dB_per_px": round(float(ay), 5),
                     "row_fit_residuals_dB": [round(float(ay * y + by - k), 2) for k, y in labels.items()]},
            "CMRR_dB": table,
            "note": "Curves from the top: gains 100, 50, 20 and 10 (x1). 1 MHz lies on the frame and is "
                    "extrapolated from the last 0.4 decade."}


def fig47() -> dict:
    doc = pymupdf.open(NF / "NF_5307_instruction_manual_EN.pdf")
    pix = doc[36].get_pixmap(dpi=400, colorspace=pymupdf.csGRAY)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width).astype(float)
    dark = img < 128
    # frame: left column and top/bottom rows
    xl = 600 + int(np.argmax(dark[600:1700, 600:700].mean(axis=0)))
    band = slice(400, 1900)                                        # Fig. 4.7 only (Fig. 4.8 is below it)
    frame_rows = groups(400 + np.where(dark[band, xl + 60:xl + 2160].mean(axis=1) > 0.9)[0])
    top, bottom = frame_rows[0], frame_rows[-1]
    # printed ticks on the left axis (thin runs just right of the frame)
    t = [c for c, w in runs(dark[:, xl + 12], int(top) + 8, int(bottom) - 8) if w <= 8]
    assert len(t) == 26, (len(t), t)          # 8 + 1 + 8 + 1 + 8 ticks between 1 uV and 1 nV
    ticks_y = [top] + t + [bottom]
    ticks_v = [1000, 900, 800, 700, 600, 500, 400, 300, 200, 100, 90, 80, 70, 60, 50, 40, 30, 20,
               10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    dec_y, dec_v = [top, ticks_y[9], ticks_y[18], bottom], [1000, 100, 10, 1]

    def v_ticks(y):
        return float(10 ** np.interp(y, ticks_y, np.log10(ticks_v)))

    def v_dec(y):
        return float(10 ** np.interp(y, dec_y, np.log10(dec_v)))

    vcols = groups(np.where(dark[int(top) + 5:int(bottom) - 5, :].mean(axis=0) > 0.55)[0])
    # decade lines: the frame edges, and every line that closes a decade (the 9-to-10 gap is short)
    # and opens the next (the 1-to-2 gap is the longest); labels hide some lines between 1 and 10 kHz
    xdec = [vcols[0]] + [vcols[i] for i in range(1, len(vcols) - 1)
                         if vcols[i] - vcols[i - 1] <= 30 and vcols[i + 1] - vcols[i] >= 100] + [vcols[-1]]
    assert len(xdec) == 6, xdec                                    # 1 Hz ... 100 kHz

    def x_of(f):
        return float(np.interp(np.log10(f), np.arange(6), xdec))

    vgrid = np.array(vcols)

    def read(f):
        xc = x_of(f)
        cols = []
        for x in range(int(xc) - 14, int(xc) + 15):
            if x <= xl + 2 or np.min(np.abs(vgrid - x)) <= 3:
                continue
            r = [c for c, w in runs(dark[:, x], int(top) + 6, int(bottom) - 6) if 4 <= w <= 30]
            if len(r) == 2:
                cols.append((x, r))
        xs = np.array([c[0] for c in cols], float)
        out = {}
        for k, name in ((0, "gain_10x1"), (1, "gain_100x1")):
            ys = np.array([c[1][k] for c in cols])
            y = float(np.polyval(np.polyfit(xs, ys, 1), xc))
            out[name] = {"ticks": round(v_ticks(y), 2), "uniform": round(v_dec(y), 2)}
        return out

    # flat parts: rows dark over a large part of the frame width
    frac = dark[:, int(xdec[0]) + 5:int(xdec[-1]) - 5].mean(axis=1)
    flat = [g for g in groups(np.where(frac > 0.45)[0]) if top + 10 < g < bottom - 10]
    assert len(flat) == 2, flat
    flat_out = {name: {"ticks": round(v_ticks(y), 2), "uniform": round(v_dec(y), 2)}
                for name, y in zip(("gain_10x1", "gain_100x1"), flat)}
    # 1 Hz: the lower curve extrapolated to the frame edge from the first columns right of it
    cols = []
    for x in range(xl + 29, xl + 61, 3):
        r = [c for c, w in runs(dark[:, x], int(top) + 6, int(bottom) - 6) if 4 <= w <= 30]
        if len(r) == 2:
            cols.append((x, r[1]))
    y1 = float(np.polyval(np.polyfit([c[0] for c in cols], [c[1] for c in cols], 1), xl + 2))
    return {"file": "refs/commercial_preamps/NF_Corporation/NF_5307_instruction_manual_EN.pdf, PDF p. 37 (400 dpi)",
            "noise_nV_rtHz": {"flat (gain 10x1: 1 kHz-100 kHz; gain 100x1: 100 Hz-100 kHz)": flat_out,
                              "2": read(2), "10": read(10), "100": read(100),
                              "1 (gain 100x1, frame edge)": {"ticks": round(v_ticks(y1), 2),
                                                             "uniform": round(v_dec(y1), 2)}},
            "note": "ticks = log interpolation between the printed minor ticks; uniform = uniform log scale "
                    "between the decade lines. The two bracket the reading."}


def main() -> None:
    res = {"fig46_cmrr": fig46(), "fig47_noise": fig47()}
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
