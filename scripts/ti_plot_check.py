"""Check of TI data-sheet plot readings (JFET capacitances, op-amp input noise) from the pixels.

scripts/models.py quotes values read from four TI data-sheet plots: C_rss (and C_iss) of the JFE150
and JFE2140 at V_DS = 5 V, and the THS4021's and THS4031's input noise at 10 Hz and their white
floors.  This script reads the same curves from the pixels and writes sim/results/ti_plot_check.json.
Figures (PDFs under refs/datasheets/; page index from 0, printed page number):
  - JFE150, SLPS732B, Fig. 6-12, index 6 (p. 7): C_iss, C_oss and C_rss vs V_DS, log V axis
    0.5-50 V, linear axis 0-50 pF; read at V_DS = 5 V.  jfet/TI/TI_JFE150_datasheet_SLPS732B.pdf
  - JFE2140, SLPS730B, Fig. 6-17, index 7 (p. 8): the same, 0.5-40 V and 0-30 pF; read at 5 V.
    jfet/TI/TI_JFE2140_datasheet_SLPS730B.pdf
  - THS4021, SLOS265F, Figs. 5-11 and 5-12, index 10 (p. 11): input-referred voltage noise
    (1-10 nV/rtHz) and current noise (1-50 pA/rtHz) vs frequency (10 Hz-100 kHz), log-log.
    opamp/TI_ths4021_datasheet.pdf
  - THS4031, SLOS224L, Figs. 5-13 and 5-14, index 11 (p. 12): the same.  opamp/TI_ths4031_datasheet.pdf
The JFET figures are raster images embedded at about 150 dpi (JFE150) and 316 dpi (JFE2140); the
op-amp figures are vector drawings.

Method.
  Page: the one page whose text holds the figure's caption, rendered by PyMuPDF at 400 dpi in memory.
  Frame: in a rough search box per figure (FIGS, PDF points), the frame lines are the outermost
  columns dark (grey < 100) over half the box height, and the outermost rows dark over 90 % of the
  width between them that stop at the right frame line (a table rule crossing the box runs on).
  Grid: inside the frame, the columns and rows in which neutral non-white pixels (channel spread
  < 30, mean < 255) cover more than half the frame height or width.  (The JFE150 image is a JPEG
  with a soft mask; some of its grid lines render as faint as grey 246-254, on a background of 255.)
  Their number must equal that of the grid the printed limits imply (log axis: m x 10^k,
  m = 1...9; linear axis: the label step), and they take those values in order.
  Axes: the printed limits (FIGS, x and y) sit on the frame lines.  The coordinate is log10(value)
  on a log axis and the value on a linear one.  Every value, abscissa included, is read with three
  calibrations: 'frame', the uniform scale through the two frame lines (grid not used); 'fit', the
  uniform scale fitted (least squares) to the frame and grid lines; 'local', linear interpolation
  between the neighbouring frame or grid lines.  The grid lines' largest offset from the 'frame'
  scale and the largest residual of the 'fit' are given per axis; where the grid sits off the
  frame's scale, the readings differ, and all three are kept.
  Curves: colour classes black (C_iss: channels < 90, spread < 30), red (C_oss and the noise curves:
  R > 150, G and B < 100) and blue-grey (C_rss: B - R > 20, R < 150).  In a column, a curve's centre
  is the mean row of the largest cluster of its class (gaps of 1 px bridged); a value is the median
  of the centres over the 13 columns within 6 px of the target abscissa.  In the raster figures a
  curve is a staircase of native pixels (steps of 1-2 px at 400 dpi), and a median takes the level
  of one step; beside it, 'line' is the least-squares straight line through the centres of the 31
  columns within 15 px, at the abscissa, which interpolates between the steps.
  Noise-plot edges: the frame lines at 10 Hz and 100 kHz hide the ends of the curves.  The value at
  an edge is the straight-line extrapolation (in log-log, a local power law) to the edge abscissa
  of the centres in 15 columns, starting 3 columns inwards of the first column that holds at least
  3 px of the curve (there the curve's butt end cuts the cross-section); that first column, read
  alone, is the 'first visible point' (10 Hz side) or the 'last visible point' (100 kHz side).
No simulation.  Usage: python ti_plot_check.py
"""
from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

import numpy as np
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
DS = ROOT / "refs" / "datasheets"
OUT = ROOT / "sim" / "results" / "ti_plot_check.json"
DPI = 400
PX_PER_PT = DPI / 72.0
INSET = 6                    # px from a frame-line centre to the first pixel read inside the frame
HALF = 6                     # a median reading uses the columns within HALF px of the target
LINE_HALF = 15               # the 'line' check fits the columns within LINE_HALF px of the target
EDGE_SKIP, EDGE_N = 3, 15    # edge extrapolation: columns skipped after the first visible, columns fitted

JFET = {"C_iss_pF": "black", "C_oss_pF": "red", "C_rss_pF": "bluegrey"}
# Per figure: PDF (under refs/datasheets), caption (finds the page), printed page number, rough
# search box (x0, y0, x1, y1 in PDF points: the frame and its labels, no other plot), the printed
# axis limits on the frame lines as (scale, low, high[, grid step of a linear axis]), the curves by
# colour class, and the abscissa to read at (JFET figures) or the edges to read (noise figures).
FIGS = {
    "JFE150 Fig. 6-12": dict(
        pdf="jfet/TI/TI_JFE150_datasheet_SLPS732B.pdf", printed_page=7, box=(330, 518, 535, 668),
        caption="Figure 6-12. Input, Output, and Reverse Transfer Capacitance",
        x=("log", 0.5, 50.0), y=("lin", 0.0, 50.0, 10.0), curves=JFET, at=5.0),
    "JFE2140 Fig. 6-17": dict(
        pdf="jfet/TI/TI_JFE2140_datasheet_SLPS730B.pdf", printed_page=8, box=(200, 536, 412, 690),
        caption="Figure 6-17. Input, Output, and Reverse Transfer Capacitance",
        x=("log", 0.5, 40.0), y=("lin", 0.0, 30.0, 10.0), curves=JFET, at=5.0),
    "THS4021 Fig. 5-11": dict(
        pdf="opamp/TI_ths4021_datasheet.pdf", printed_page=11, box=(80, 465, 300, 615),
        caption="Figure 5-11. Input-Referred Voltage Noise vs Frequency",
        x=("log", 10.0, 1e5), y=("log", 1.0, 10.0), curves={"e_n_nV_rtHz": "red"}),
    "THS4021 Fig. 5-12": dict(
        pdf="opamp/TI_ths4021_datasheet.pdf", printed_page=11, box=(325, 465, 550, 615),
        caption="Figure 5-12. Input-Referred Current Noise vs Frequency",
        x=("log", 10.0, 1e5), y=("log", 1.0, 50.0), curves={"i_n_pA_rtHz": "red"}),
    "THS4031 Fig. 5-13": dict(
        pdf="opamp/TI_ths4031_datasheet.pdf", printed_page=12, box=(80, 112, 300, 262),
        caption="Figure 5-13. Input-Referred Voltage Noise vs Frequency",
        x=("log", 10.0, 1e5), y=("log", 1.0, 10.0), curves={"e_n_nV_rtHz": "red"}),
    "THS4031 Fig. 5-14": dict(
        pdf="opamp/TI_ths4031_datasheet.pdf", printed_page=12, box=(325, 112, 550, 262),
        caption="Figure 5-14. Input-Referred Current Noise vs Frequency",
        x=("log", 10.0, 1e5), y=("log", 1.0, 50.0), curves={"i_n_pA_rtHz": "red"}),
}
HOWS = ("frame", "fit", "local")    # the three axis calibrations (see Axes in the docstring)


def find_page(pdf: str, caption: str) -> int:
    """Index (from 0) of the one page whose text holds the caption."""
    doc = pymupdf.open(DS / pdf)
    hits = [i for i, page in enumerate(doc) if caption in " ".join(page.get_text().split())]
    assert len(hits) == 1, (pdf, caption, hits)
    return hits[0]


@lru_cache(maxsize=1)                # figures on the same page follow each other in FIGS
def render(pdf: str, index: int) -> np.ndarray:
    """The page rendered at DPI: RGB, uint8, rows x columns x 3."""
    doc = pymupdf.open(DS / pdf)
    pix = doc[index].get_pixmap(dpi=DPI, colorspace=pymupdf.csRGB, alpha=False)
    return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)


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


def find_frame(gray: np.ndarray) -> tuple[float, float, float, float]:
    """Centres (px in the box) of the left, right, top and bottom frame lines."""
    dark = gray < 100
    cols = groups(np.where(dark.mean(axis=0) > 0.5)[0])
    left, right = cols[0], cols[-1]
    lo, hi = int(round(left)), int(round(right))
    past = min(hi + 12, gray.shape[1] - 1)                 # 12 px right of the right frame line
    rows = [y for y in groups(np.where(dark[:, lo:hi + 1].mean(axis=1) > 0.9)[0])
            if not dark[int(round(y)), past]]
    return left, right, rows[0], rows[-1]


def find_grid(rgb: np.ndarray, left: float, right: float, top: float, bottom: float
              ) -> tuple[list[float], list[float]]:
    """Grid columns and rows (px in the box) inside the frame."""
    x0, y0 = int(round(left)) + INSET, int(round(top)) + INSET
    sub = rgb[y0:int(round(bottom)) - INSET + 1, x0:int(round(right)) - INSET + 1]
    neutral = (np.ptp(sub, axis=2) < 30) & (sub.mean(axis=2) < 255)
    return ([x0 + c for c in groups(np.where(neutral.mean(axis=0) > 0.5)[0])],
            [y0 + c for c in groups(np.where(neutral.mean(axis=1) > 0.5)[0])])


def grid_values(spec: tuple) -> list[float]:
    """Values of the grid lines strictly between the printed limits."""
    scale, lo, hi = spec[:3]
    if scale == "lin":
        return [lo + k * spec[3] for k in range(1, round((hi - lo) / spec[3]))]
    out = []
    for k in range(math.floor(math.log10(lo)), math.ceil(math.log10(hi)) + 1):
        for m in range(1, 10):
            v = float(f"{m * 10.0 ** k:.10g}")
            if lo * (1 + 1e-9) < v < hi * (1 - 1e-9):
                out.append(v)
    return out


class Axis:
    """Calibrated axis: positions p (px, increasing) of the frame and grid lines, their coordinates
    u (log10 of the value on a log axis, the value on a linear one), and the uniform scales
    p = a u + b of the 'frame' and 'fit' calibrations."""

    def __init__(self, spec: tuple, lo_px: float, hi_px: float, grid_px: list[float]):
        vals = grid_values(spec)
        assert len(vals) == len(grid_px), (spec, len(vals), [round(g, 1) for g in grid_px])
        p = np.array([lo_px] + sorted(grid_px, reverse=lo_px > hi_px) + [hi_px])
        v = np.array([spec[1]] + vals + [spec[2]])
        self.log = spec[0] == "log"
        i = np.argsort(p)
        self.p, self.u = p[i], (np.log10(v) if self.log else v)[i]
        a = (self.p[-1] - self.p[0]) / (self.u[-1] - self.u[0])      # p[0], p[-1]: the frame lines
        self.scales = {"frame": (a, self.p[0] - a * self.u[0]),
                       "fit": tuple(np.polyfit(self.u, self.p, 1))}
        self.n_grid = len(grid_px)

    def px(self, value: float, how: str) -> float:
        u = math.log10(value) if self.log else value
        if how == "local":
            j = np.argsort(self.u)
            return float(np.interp(u, self.u[j], self.p[j]))
        a, b = self.scales[how]
        return float(a * u + b)

    def value(self, px: float, how: str) -> float:
        if how == "local":
            u = float(np.interp(px, self.p, self.u))
        else:
            a, b = self.scales[how]
            u = (px - b) / a
        return float(10.0 ** u if self.log else u)

    def info(self, spec: tuple) -> dict:
        unit = "decade" if self.log else "unit"
        a_f, b_f = self.scales["frame"]
        a_u, b_u = self.scales["fit"]
        off = float(np.max(np.abs(self.p - (a_f * self.u + b_f))))   # zero at the frame lines
        res = float(np.max(np.abs(self.p - (a_u * self.u + b_u))))
        return {"scale": spec[0], "limits_on_frame": list(spec[1:3]), "n_grid_lines": self.n_grid,
                f"px_per_{unit}": {"frame": round(float(a_f), 2), "fit": round(float(a_u), 2)},
                "grid_max_offset_from_frame_scale_px": round(off, 2),
                f"grid_max_offset_from_frame_scale_{unit}": round(off / abs(a_f), 4),
                "fit_max_residual_px": round(res, 2),
                f"fit_max_residual_{unit}": round(res / abs(a_u), 4)}


def class_mask(rgb: np.ndarray, cls: str, top: float, bottom: float) -> np.ndarray:
    """Pixels of a curve's colour class, in the rows inside the frame."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    if cls == "black":
        m = (rgb.max(axis=2) < 90) & (np.ptp(rgb, axis=2) < 30)
    elif cls == "red":
        m = (r > 150) & (g < 100) & (b < 100)
    elif cls == "bluegrey":
        m = (b - r > 20) & (r < 150)
    else:
        raise ValueError(cls)
    m[:int(round(top)) + INSET] = False
    m[int(round(bottom)) - INSET + 1:] = False
    return m


def centre(col: np.ndarray, min_px: int = 1) -> float | None:
    """Mean index of the largest cluster of True in a column (None if it is under min_px)."""
    ys = np.where(col)[0]
    if ys.size == 0:
        return None
    best = max(np.split(ys, np.where(np.diff(ys) > 2)[0] + 1), key=len)
    return float(best.mean()) if best.size >= min_px else None


def read_median(mask: np.ndarray, xc: float) -> tuple[float, int]:
    """Median centre of a curve over the columns within HALF px of xc, and the number of columns
    that hold it."""
    c = math.floor(xc + 0.5)
    ys = [y for x in range(c - HALF, c + HALF + 1) if (y := centre(mask[:, x])) is not None]
    return float(np.median(ys)), len(ys)


def read_line(mask: np.ndarray, xc: float) -> float:
    """Least-squares straight line through a curve's centres over the columns within LINE_HALF px
    of xc, evaluated at xc."""
    c = math.floor(xc + 0.5)
    pts = [(x, y) for x in range(c - LINE_HALF, c + LINE_HALF + 1)
           if (y := centre(mask[:, x])) is not None]
    return float(np.polyval(np.polyfit([p[0] for p in pts], [p[1] for p in pts], 1), xc))


def edge_fit(mask: np.ndarray, x_frame: float, step: int) -> tuple[int, float, np.ndarray]:
    """A curve's end hidden by the frame line at x_frame (step +1: left edge, -1: right edge): the
    first visible column, its centre, and the straight-line fit y = f[0] x + f[1] of the centres in
    EDGE_N columns from EDGE_SKIP columns inwards of it."""
    x = math.floor(x_frame + 0.5)
    for _ in range(40):
        x += step
        if (y_first := centre(mask[:, x], 3)) is not None:
            break
    else:
        raise RuntimeError("no curve within 40 px of the frame line")
    cols = [x + step * (EDGE_SKIP + k) for k in range(EDGE_N)]
    pts = [(c, y) for c in cols if (y := centre(mask[:, c])) is not None]
    return x, y_first, np.polyfit([p[0] for p in pts], [p[1] for p in pts], 1)


def read_jfet(fig: dict, ax: Axis, ay: Axis, masks: dict) -> dict:
    """The curves at the abscissa fig['at'] (V)."""
    out = {}
    for qty, m in masks.items():
        med, line, cols = {}, {}, []
        for how in HOWS:
            xc = ax.px(fig["at"], how)
            y, n = read_median(m, xc)
            med[how] = round(ay.value(y, how), 3)
            line[how] = round(ay.value(read_line(m, xc), how), 3)
            cols.append(n)
        out[qty] = {"median": med, "line": line, "median_columns_min": min(cols)}
    return {f"V_DS = {fig['at']:g} V": out}


def read_noise(fig: dict, ax: Axis, ay: Axis, masks: dict, left: float, right: float) -> dict:
    """The curve at the two frame edges (extrapolated) and at the visible columns nearest them."""
    (qty, m), = masks.items()
    out = {}
    for f_edge, x_frame, step, near in ((fig["x"][1], left, 1, "first visible point"),
                                        (fig["x"][2], right, -1, "last visible point")):
        x_vis, y_vis, line = edge_fit(m, x_frame, step)
        label = f"{f_edge / 1e3:g} kHz" if f_edge >= 1e3 else f"{f_edge:g} Hz"
        out[f"{label} (frame edge, extrapolated)"] = {
            how: round(ay.value(float(np.polyval(line, ax.px(f_edge, how))), how), 3) for how in HOWS}
        out[near] = {"f_Hz": {how: float(f"{ax.value(x_vis, how):.4g}") for how in HOWS},
                     "value": {how: round(ay.value(y_vis, how), 3) for how in HOWS}}
    return {qty: out}


def read_figure(fig: dict) -> dict:
    index = find_page(fig["pdf"], fig["caption"])
    bx0, by0, bx1, by1 = (int(v * PX_PER_PT) for v in fig["box"])
    rgb = render(fig["pdf"], index)[by0:by1, bx0:bx1].astype(int)     # px below are in this box
    left, right, top, bottom = find_frame(rgb.mean(axis=2))
    gcols, grows = find_grid(rgb, left, right, top, bottom)
    ax = Axis(fig["x"], left, right, gcols)
    ay = Axis(fig["y"], bottom, top, grows)
    masks = {qty: class_mask(rgb, cls, top, bottom) for qty, cls in fig["curves"].items()}
    if "at" in fig:
        readings = read_jfet(fig, ax, ay, masks)
    else:
        readings = read_noise(fig, ax, ay, masks, left, right)

    def pt(v: float, origin: int) -> float:
        return round((v + origin + 0.5) / PX_PER_PT, 2)        # px in the box -> PDF points

    return {"pdf": f"refs/datasheets/{fig['pdf']}", "caption": fig["caption"],
            "page": {"index_from_0": index, "printed": fig["printed_page"]}, "dpi": DPI,
            "search_box_pt": list(fig["box"]),
            "frame_pt": {"left": pt(left, bx0), "right": pt(right, bx0), "top": pt(top, by0),
                         "bottom": pt(bottom, by0)},
            "axes": {"x": ax.info(fig["x"]), "y": ay.info(fig["y"])},
            "readings": readings}


def summary(res: dict) -> list[str]:
    lines = [f"{'figure':19s} {'reading':52s}" + "".join(f"{h:>9s}" for h in HOWS)]

    def row(name: str, label: str, v: dict) -> None:
        lines.append(f"{name:19s} {label:52s}" + "".join(f"{v[h]:9.3f}" for h in HOWS))

    for name, r in res.items():
        for key, block in r["readings"].items():
            for sub, v in block.items():
                if "median" in v:                       # JFET figure: key 'V_DS = 5 V', sub the quantity
                    row(name, f"{sub} at {key}, median", v["median"])
                    row(name, f"{sub} at {key}, line (31 columns)", v["line"])
                elif "f_Hz" in v:                       # noise figure: key the quantity
                    f = v["f_Hz"]["fit"]
                    row(name, f"{key} at {sub} ({f / 1e3:.4g} kHz)" if f >= 1e3 else
                        f"{key} at {sub} ({f:.3g} Hz)", v["value"])
                else:
                    row(name, f"{key} at {sub}", v)
        for a in ("x", "y"):
            ax = r["axes"][a]
            lines.append(f"{'':19s} {a} axis: {ax['n_grid_lines']} grid lines, largest offset from the frame "
                         f"scale {ax['grid_max_offset_from_frame_scale_px']} px, fit residual "
                         f"{ax['fit_max_residual_px']} px")
    return lines


def main() -> None:
    res = {name: read_figure(fig) for name, fig in FIGS.items()}
    out = {"method": "Pixel reading of 400-dpi PyMuPDF renders, frame and grid lines found in the pixels.  "
                     "Axis calibrations: 'frame' = uniform scale through the two frame lines at the printed "
                     "limits; 'fit' = uniform scale fitted to the frame and grid lines; 'local' = interpolation "
                     "between neighbouring frame or grid lines.  Values: median of the curve centre over 13 "
                     "columns around the abscissa; at the noise plots' frame edges, straight-line (log-log) "
                     "extrapolation of the centres in 15 columns.  See the docstring of scripts/ti_plot_check.py.",
           "figures": res}
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print("\n".join(summary(res)))
    print(f"written: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
