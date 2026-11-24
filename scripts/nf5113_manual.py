"""The noise-figure contours of the Signal Recovery Model 5113, read from the pixels of its manual's plot, so that the
note can set them beside H and L (Figure 14j-l, Section 6.2): instruction manual 222144-A-MNL-F (©2002 AMETEK Advanced
Measurement Technology), Appendix A, printed p. A-2 = PyMuPDF index 27, "Figure A-1, Typical Noise Figure Contours at
Gain = x1000, AC Coupling and 10s Coupling Time-Constant, Flat Filter Mode"
(refs/commercial_preamps/SignalRecovery_AMETEK/SignalRecovery_5113_manual_2002.pdf).  The 2010 data sheet
(CatIss7Web:0710UK, p. 1) and the 2024 5113A data sheet (AMT-C00007, p. 2) carry the same plot; the 1992 EG&G manual
(222144-A-MNL-C) has none.  All four specify 4 nV/rtHz at 1 kHz ("4 nV/rtHz at 1 kHz referred to input", p. A-2).

The plot is a 1-bit image of 965 x 941 pixels (about 300 dpi), which the page shows flipped vertically; the page has
no usable text layer (its font maps no Unicode), so the page and the image are fixed here and checked by their size,
and the flipped image is checked against a render of the page ("image_check").  Nothing is traced by eye:
  calibration  the frame and the dashed decade grid: the columns and rows with more than 250 ink pixels, 8 vertical
               lines (0.1 Hz to 1 MHz) and 9 horizontal ones (100 Mohm at the top to 1 ohm), fitted linearly
  cleaning     inside the frame only: the grid lines removed and restored where ink lies on both sides of them (a
               contour crossing them); the labels' characters (components no larger than 15 x 15 px) removed and
               merged into labels (gaps under 14 px)
  bridging     the ten labels at 10 kHz (0.1 to 20 dB) sit inside their contours: each is replaced by a straight line,
               two pixels thick, from the contour's last pixel on its left to its first on its right
  levels       an in-line label names the contour it interrupts; each of the three labels near 1 ohm (50, 40, 30 dB)
               the nearest contour on its left, at its mid-height; the five unlabelled contours of the upper right
               corner, which run from the top edge to the right edge, take 6, 10, 15, 20 and 30 dB in order towards
               the corner (the plot's levels above the 3 dB contour that bounds them), as for the SR560's plot
               (sr560_nf_datasheet.py).  Check ("corner_check"): where they meet the 1 MHz edge, their resistances
               stand in the ratios of F - 1, as they must where a noise current dominates (F - 1 ~ R_S i_n^2).
  contours     each contour thinned to a line one pixel wide (T. Y. Zhang and C. Y. Suen, "A fast parallel algorithm
               for thinning digital patterns", Commun. ACM 27(3), 236-239 (1984), https://doi.org/10.1145/357994.358023)
               and traced from end to end (a closed one opened at its leftmost pixel and closed again), in decades,
               (log10(f / Hz), log10(R_S / ohm)); a straight run of the trace is kept by its two ends
  two-port     at each frequency of nf_map.py's grid (20 per decade) from 0.1 Hz to 1 MHz, the noisy two-port of
               nf_map.py, F = 1 + (S_e + R_S S_x + R_S^2 S_i) / (4 k T0 R_S), T0 = 290 K, fitted to the points where
               the contours cross that frequency (relative weights, columns scaled; S_e, S_i >= 0).  A contour that
               ends within 0.035 decade (3.5 px) of the frame's left or right edge counts there, extended to the edge
               along its last pixels unless it runs along the edge ("edge_points"); crossings within 0.03 decade of
               the top or bottom edge are left out.  Where the plot draws both sides of the minimum ("both_sides": a
               crossing below the fitted optimum and at least two above it) all three terms are fitted; below that,
               where it draws only the low-resistance side, S_x = 0 and S_i = the median of the fitted S_i from 5 Hz
               to 5 kHz are held and S_e alone is fitted, to the crossings below 10 Mohm where S_i R_S^2 is at most a
               tenth of S_e: in the decade under the top edge the plot's contours turn vertical at these frequencies
               (6 dB at 1 Hz, 10 dB at 0.5 Hz, 15 dB at 0.25 Hz, 20 dB at 0.13 Hz), which no two-port does; they
               are the trace of a coarse frequency grid (the low-resistance contours are straight in log-log between
               whole decades and bend only there: "e_n_stray_from_decade_chords_decades").
Derived ("model", "spec_check", "ac_coupling_check"): e_n, i_n, the minimum noise figure and the 1 and 3 dB
crossings at whole decades; the i_n of low frequencies and the resistance with that thermal noise at T0; the
capacitance C of i_n^2 = i_n,low^2 + (e_n w C)^2 at 100 kHz, 316 kHz and 1 MHz; the slope of S_e over each decade and
how far S_e strays from the straight line (in log-log) between whole decades; the 1/f corner f (e^2 - e_w^2) / e_w^2
at 10 Hz, 100 Hz and 1 kHz (e_w at 100 kHz); against the specification at 1 kHz, the ratio of e_n and where the 3 dB
contour would lie for 4 nV/rtHz with the plot's i_n; for the AC coupling (0.1 uF in series and the 100 Mohm input
resistance of the 10 s time constant, manual p. A-1), the plot's i_n through 1 / (w 0.1 uF) and the signal transfer
w tau / sqrt(1 + (w tau)^2) at 0.1 Hz.
Against H and L (nf_map.npz) and the SR560 data sheet's plot (sr560_nf_datasheet.json), "versus": their noise
figure minus the 5113 plot's on the plane where the plot draws both sides of the minimum, 1 ohm to 100 Mohm in
0.01 decade (as nf_map.vs_datasheet): the fractions of the plane lower by more than 0.1 dB, within 0.1 dB and
higher, the extremes, the box of the higher region, and the resistances where the difference changes sign at
10 Hz, 100 Hz, 1 kHz, 10 kHz, 100 kHz and 1 MHz.
Writes ../sim/results/nf5113_manual.json.
Usage: python nf5113_manual.py [--check out.png]   (--check: the traced contours over the plot's image, for
inspection; the image is AMETEK's figure, so keep it out of the repository)
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pymupdf
from scipy import ndimage as ndi
from scipy.optimize import lsq_linear

import spice

PDF = spice.ROOT / "refs" / "commercial_preamps" / "SignalRecovery_AMETEK" / "SignalRecovery_5113_manual_2002.pdf"
PAGE = 27                                   # PyMuPDF index; printed p. A-2
IMAGE_SIZE = (965, 941)
RIGHT_LABELS = (0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 6.0, 10.0, 15.0, 20.0)   # at 10 kHz, top to bottom
BOTTOM_LABELS = (50.0, 40.0, 30.0)                                       # near 1 ohm, left to right
CORNER_LEVELS = (6.0, 10.0, 15.0, 20.0, 30.0)                            # unlabelled, towards the corner
LEVELS = (0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 6.0, 10.0, 15.0, 20.0, 30.0, 40.0, 50.0)
K_B, T0 = 1.380649e-23, 290.0
G4 = 4 * K_B * T0
LOG_F = np.round(np.arange(141) / 20 - 1, 4)   # 0.1 Hz to 1 MHz, 20 per decade (nf_map.py's grid)
EDGE_TOL = 0.035   # decade: a contour ending this near the left or right edge ends there (3.5 px: the frame line, 2 px
                   # wide, is cut away, and the thinning shortens a line's end by a pixel or two)
EDGE_R = 0.03      # decade: crossings this near the top or bottom edge are left out
SPEC_EN_1K = 4e-9                              # V/rtHz at 1 kHz, manual p. A-2 (and p. 2 of the 1992 manual)
C_COUPLING = 0.1e-6                            # F, "in series with 0.1 uF", manual p. A-1
R_IN = 100e6                                   # ohm: the input resistance of the 10 s coupling time constant
TAU = 10.0                                     # s
DECADES = (0.1, 1.0, 10.0, 100.0, 1e3, 1e4, 1e5, 1e6)


# ---- the image -------------------------------------------------------------------------------------------------
def load() -> tuple[np.ndarray, dict]:
    """The plot as a boolean array (True = ink), upright, and the check against a render of the page: the fraction
    of the image's ink that lies within one pixel of ink in the render at the image's own scale."""
    doc = pymupdf.open(PDF)
    page = doc[PAGE]
    imgs = page.get_images(full=True)
    assert len(imgs) == 1, imgs
    xref = imgs[0][0]
    info = doc.extract_image(xref)
    assert (info["width"], info["height"], info["bpc"]) == (*IMAGE_SIZE, 1), info
    pix = pymupdf.Pixmap(info["image"])
    raw = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, 0]
    ink = (raw < 128)[::-1, :].copy()
    rect = page.get_image_rects(xref)[0]
    mat = pymupdf.Matrix(IMAGE_SIZE[0] / rect.width, IMAGE_SIZE[1] / rect.height)
    rp = page.get_pixmap(matrix=mat, clip=rect, colorspace=pymupdf.csGRAY)
    ren = np.frombuffer(rp.samples, dtype=np.uint8).reshape(rp.height, rp.width)[:IMAGE_SIZE[1], :IMAGE_SIZE[0]] < 128
    near = ndi.binary_dilation(ren, structure=np.ones((3, 3)))
    agree = float(near[ink].mean())
    flipped_agree = float(ndi.binary_dilation(ren, structure=np.ones((3, 3)))[ink[::-1, :]].mean())
    assert agree > 0.95 > flipped_agree, (agree, flipped_agree)
    return ink, dict(xref=xref, size_px=list(IMAGE_SIZE), placed_pt=[rect.x0, rect.y0, rect.x1, rect.y1],
                     ink_within_1px_of_render=agree, the_same_unflipped=flipped_agree)


def groups(counts: np.ndarray, thr: int) -> list[list[int]]:
    out: list[list[int]] = []
    for i in np.flatnonzero(counts > thr):
        if out and i - out[-1][-1] == 1:
            out[-1].append(int(i))
        else:
            out.append([int(i)])
    return out


def calibrate(ink: np.ndarray) -> dict:
    """Frame and grid: 8 vertical lines, 0.1 Hz to 1 MHz; 9 horizontal ones, 100 Mohm to 1 ohm.  Rows of long
    horizontal contour portions pass the threshold too: the grid's rows are those nearest to an even spacing between
    the top and bottom of the frame."""
    gx, gy = groups(ink.sum(axis=0), 250), groups(ink.sum(axis=1), 250)
    assert len(gx) == 8, gx
    cx = np.array([np.mean(g) for g in gx])
    cand = [(float(np.mean(g)), g) for g in gy]
    top, bottom = cand[0][0], cand[-1][0]
    cy, rows = [], []
    for w in top + (bottom - top) * np.arange(9) / 8:
        c, g = min(cand, key=lambda t: abs(t[0] - w))
        assert abs(c - w) < 3, (w, c)
        cy.append(c)
        rows.append(g)
    cy = np.array(cy)
    bx, ax = np.polyfit(np.arange(-1, 7), cx, 1)
    by, ay = np.polyfit(np.arange(8, -1, -1), cy, 1)
    res = max(np.abs(np.polyval([bx, ax], np.arange(-1, 7)) - cx).max(),
              np.abs(np.polyval([by, ay], np.arange(8, -1, -1)) - cy).max())
    assert res < 1.0, res
    return dict(x_lines_px=gx, y_lines_px=rows, x_centres_px=cx.tolist(), y_centres_px=cy.tolist(),
                px_per_decade_f=float(bx), x_px_at_1hz=float(ax), px_per_decade_r=float(by), y_px_at_1ohm=float(ay),
                max_residual_px=float(res))


def to_dec(cal: dict, col, row):
    return ((np.asarray(col, dtype=float) - cal["x_px_at_1hz"]) / cal["px_per_decade_f"],
            (np.asarray(row, dtype=float) - cal["y_px_at_1ohm"]) / cal["px_per_decade_r"])


def clean(ink: np.ndarray, cal: dict) -> tuple[np.ndarray, np.ndarray]:
    """Inside the frame; grid removed and restored where a contour crosses it; characters split off.  Returns
    (contours, characters)."""
    xl, yl = cal["x_lines_px"], cal["y_lines_px"]
    a = np.zeros_like(ink)
    r0, r1, c0, c1 = max(yl[0]) + 1, min(yl[-1]) - 1, max(xl[0]) + 1, min(xl[-1]) - 1
    a[r0:r1 + 1, c0:c1 + 1] = ink[r0:r1 + 1, c0:c1 + 1]
    gcols = [c for g in xl[1:-1] for c in g]
    grows = [r for g in yl[1:-1] for r in g]
    b = a.copy()
    b[:, gcols] = False
    b[grows, :] = False
    for c in gcols:
        left = ndi.maximum_filter1d(b[:, c - 1].astype(np.uint8), 3).astype(bool)
        right = ndi.maximum_filter1d(b[:, c + 1].astype(np.uint8), 3).astype(bool)
        b[:, c] = a[:, c] & left & right
    for r in grows:
        up = ndi.maximum_filter1d(b[r - 1, :].astype(np.uint8), 3).astype(bool)
        down = ndi.maximum_filter1d(b[r + 1, :].astype(np.uint8), 3).astype(bool)
        b[r, :] = a[r, :] & up & down
    lab, n = ndi.label(b, structure=np.ones((3, 3)))
    small = np.zeros(n + 1, dtype=bool)
    for k, s in enumerate(ndi.find_objects(lab), start=1):
        small[k] = s[0].stop - s[0].start <= 15 and s[1].stop - s[1].start <= 15
    chars = small[lab]
    return b & ~chars, b & chars


def labels(chars: np.ndarray) -> list[tuple[int, int, int, int]]:
    """The labels (x0, x1, y0, y1): characters merged when less than 14 px apart and overlapping vertically; stray
    marks (merged boxes 20 px wide or less) dropped."""
    lab, _ = ndi.label(chars, structure=np.ones((3, 3)))
    boxes = sorted((s[1].start, s[1].stop - 1, s[0].start, s[0].stop - 1) for s in ndi.find_objects(lab))
    merged: list[list[int]] = []
    for b in boxes:
        for m in merged:
            if b[0] - m[1] < 14 and b[2] <= m[3] and b[3] >= m[2]:
                m[1], m[2], m[3] = max(m[1], b[1]), min(m[2], b[2]), max(m[3], b[3])
                break
        else:
            merged.append(list(b))
    return [tuple(m) for m in merged if m[1] - m[0] > 20]


def bridge(img: np.ndarray, box) -> dict:
    """A straight line, two pixels thick, across an in-line label: from the rightmost contour pixel just left of it
    to the leftmost one just right of it (rows of the label +- 6 px)."""
    x0, x1, y0, y1 = box
    rows = slice(y0 - 6, y1 + 7)
    left, right = np.argwhere(img[rows, x0 - 15:x0 + 3]), np.argwhere(img[rows, x1 - 3:x1 + 31])
    assert len(left) and len(right), box
    xl, xr = left[:, 1].max(), right[:, 1].min()
    yl = float(np.median(left[left[:, 1] == xl, 0])) + y0 - 6
    yr = float(np.median(right[right[:, 1] == xr, 0])) + y0 - 6
    xl, xr = int(xl + x0 - 15), int(xr + x1 - 3)
    xs = np.arange(xl, xr + 1)
    ys = yl + (yr - yl) * (xs - xl) / max(xr - xl, 1)
    for dy in (-0.5, 0.5):
        img[np.round(ys + dy).astype(int), xs] = True
    return dict(label_box_px=[int(v) for v in box], from_px=[xl, yl], to_px=[xr, yr])


def assign(img: np.ndarray, boxes: list, cal: dict) -> tuple[np.ndarray, dict, dict, list]:
    """Bridge the in-line labels, then give each contour its level (see the module's docstring)."""
    right = sorted([b for b in boxes if 0 <= b[0] - cal["x_centres_px"][5] < 25
                    and b[2] < cal["y_centres_px"][-2] + 20], key=lambda b: b[2])
    bottom = sorted([b for b in boxes if b[2] > cal["y_centres_px"][-2] + 20], key=lambda b: b[0])
    assert len(right) == len(RIGHT_LABELS) and len(bottom) == len(BOTTOM_LABELS), (right, bottom)
    bridges = [bridge(img, b) for b in right]
    lab, n = ndi.label(img, structure=np.ones((3, 3)))
    level: dict[int, float] = {}
    how: dict[int, str] = {}
    for b, lv, br in zip(right, RIGHT_LABELS, bridges):
        k = int(lab[int(round(br["from_px"][1])), br["from_px"][0]])
        assert k and level.get(k, lv) == lv, (lv, k, level.get(k))
        level[k], how[k] = lv, f"in-line label at {b[0]}-{b[1]}, {b[2]}-{b[3]} px (x, y)"
    for b, lv in zip(bottom, BOTTOM_LABELS):
        row = lab[(b[2] + b[3]) // 2, :b[0]]
        hit = np.flatnonzero(row)
        assert len(hit), b
        k = int(row[hit[-1]])
        assert k not in level, (lv, k)
        level[k], how[k] = lv, f"label {b[0] - hit[-1]} px to its right at {b[0]}-{b[1]}, {b[2]}-{b[3]} px (x, y)"
    sizes = ndi.sum(np.ones_like(lab), lab, index=np.arange(1, n + 1))
    rest = [k for k in range(1, n + 1) if k not in level and sizes[k - 1] >= 8]
    top_x = {}
    for k in rest:
        ys, xs = np.nonzero(lab == k)
        assert ys.min() <= cal["y_centres_px"][0] + 3 and xs.max() >= cal["x_centres_px"][-1] - 3, (k, ys.min(), xs.max())
        top_x[k] = float(xs[ys == ys.min()].mean())
    assert len(rest) == len(CORNER_LEVELS), rest
    for k, lv in zip(sorted(rest, key=lambda k: top_x[k]), CORNER_LEVELS):
        level[k], how[k] = lv, "unlabelled, upper right corner: levels in order towards the corner"
    assert sorted(set(level.values())) == sorted(LEVELS), sorted(set(level.values()))
    return lab, level, how, bridges


# ---- the contours as lines ---------------------------------------------------------------------------------------
def thin(mask: np.ndarray) -> np.ndarray:
    """Zhang and Suen's two-subiteration thinning (1984), vectorised."""
    a = np.pad(mask.astype(np.uint8), 1)
    while True:
        changed = False
        for step in (0, 1):
            p2, p3, p4, p5 = a[:-2, 1:-1], a[:-2, 2:], a[1:-1, 2:], a[2:, 2:]
            p6, p7, p8, p9 = a[2:, 1:-1], a[2:, :-2], a[1:-1, :-2], a[:-2, :-2]
            ring = [p2, p3, p4, p5, p6, p7, p8, p9, p2]
            b = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
            t = sum(((ring[i] == 0) & (ring[i + 1] == 1)).astype(np.uint8) for i in range(8))
            c = ((p2 * p4 * p6 == 0) & (p4 * p6 * p8 == 0)) if step == 0 else ((p2 * p4 * p8 == 0) & (p2 * p6 * p8 == 0))
            m = (a[1:-1, 1:-1] == 1) & (b >= 2) & (b <= 6) & (t == 1) & c
            if m.any():
                a[1:-1, 1:-1][m] = 0
                changed = True
        if not changed:
            return a[1:-1, 1:-1].astype(bool)


def trace(skel: np.ndarray) -> np.ndarray:
    """The longest path through a one-pixel line, as (row, col) pixels in order; a closed line is opened at its
    leftmost pixel and closed again."""
    pts = set(map(tuple, np.argwhere(skel)))

    def nb(p):
        return [(p[0] + i, p[1] + j) for i in (-1, 0, 1) for j in (-1, 0, 1) if (i or j) and (p[0] + i, p[1] + j) in pts]
    closed = not any(len(nb(p)) == 1 for p in pts)
    p0 = min(pts, key=lambda p: (p[1], p[0]))
    if closed:
        pts.discard(p0)

    def farthest(s):
        par, order = {s: None}, [s]
        for p in order:
            for q in nb(p):
                if q not in par:
                    par[q] = p
                    order.append(q)
        return order[-1], par
    u, _ = farthest(next(iter(pts)))
    v, par = farthest(u)
    path = [v]
    while par[path[-1]] is not None:
        path.append(par[path[-1]])
    if closed:
        path = [p0] + path + [p0]
    return np.array(path)


def runs_ends(path: np.ndarray) -> np.ndarray:
    """The path with each straight run of pixels kept by its two ends (lossless)."""
    d = np.diff(path, axis=0)
    keep = np.ones(len(path), dtype=bool)
    keep[1:-1] = np.any(d[1:] != d[:-1], axis=1)
    return path[keep]


def edge_points(lf: np.ndarray, lr: np.ndarray) -> list[list]:
    """Where a traced line ends within EDGE_TOL of the frame's left or right edge (0.1 Hz, 1 MHz): its value on the
    edge.  It is extended to the edge along the straight line through its pixels 3 to 9 from the end (the last two
    left out, which the thinning may bend) when that stretch advances at least 0.02 decade towards the edge; a line
    that runs along the edge there (the loops' ends at 1 MHz) counts as it ends."""
    out = []
    for sl, end in ((slice(0, 9), 0), (slice(-9, None), -1)):
        for edge in (-1.0, 6.0):
            if abs(lf[end] - edge) > EDGE_TOL:
                continue
            x, y = lf[sl], lr[sl]
            a, b = (x[2], x[8]) if end == 0 else (x[-3], x[-9])
            ya, yb = (y[2], y[8]) if end == 0 else (y[-3], y[-9])
            if abs(a - b) >= 0.02:
                out.append([edge, round(float(ya + (yb - ya) / (b - a) * (edge - a)), 4), "extended"])
            else:
                out.append([edge, round(float(lr[end]), 4), "as it ends"])
    return out


def contour_lines(lab: np.ndarray, level: dict, how: dict, cal: dict) -> list[dict]:
    union = np.isin(lab, list(level))
    skel = thin(union)
    out = []
    for k in sorted(level, key=lambda k: (level[k], k)):
        path = trace(skel & (lab == k))
        lf_all, lr_all = to_dec(cal, path[:, 1], path[:, 0])
        p = runs_ends(path)
        lf, lr = to_dec(cal, p[:, 1], p[:, 0])
        out.append(dict(level_db=level[k], found=how[k], n_points=len(p),
                        points=[[round(float(a), 4), round(float(b), 4)] for a, b in zip(lf, lr)],
                        edge_points=edge_points(lf_all, lr_all)))
    return out


# ---- the two-port at each frequency ----------------------------------------------------------------------------
def crossings(contours: list, x0: float) -> list[tuple[float, float]]:
    """(level, log10 R_S) where the contours meet log10 f = x0: interpolated on each segment that spans x0; at the
    frame's left and right edges (x0 = -1 or 6), the contours' edge points.  Points within EDGE_R decade of the top
    or bottom edge are left out: there the thinning bends the lines' ends."""
    out = []
    for c in contours:
        x, y = np.array(c["points"]).T
        found = [y[k] + (x0 - x[k]) / (x[k + 1] - x[k]) * (y[k + 1] - y[k]) for k in range(len(x) - 1)
                 if (x[k] - x0) * (x[k + 1] - x0) <= 0 and x[k] != x[k + 1]]
        if x0 in (-1.0, 6.0):
            found += [e[1] for e in c["edge_points"] if e[0] == x0]
        merged: list[float] = []
        for v in sorted(found):
            if not merged or v - merged[-1] > 1e-3:
                merged.append(v)
        out += [(c["level_db"], float(v)) for v in merged if EDGE_R <= v <= 8 - EDGE_R]
    return sorted(out)


def roots(coef, level_db: float) -> list[float]:
    """The source resistances (ohm) where the two-port's noise figure is level_db."""
    s_e, s_x, s_i = coef
    g = (10 ** (level_db / 10) - 1) * G4
    if s_i <= 0:
        return [s_e / (g - s_x)] if g > s_x else []
    disc = (s_x - g) ** 2 - 4 * s_i * s_e
    if disc < 0:
        return []
    return [r for r in (((g - s_x) - np.sqrt(disc)) / (2 * s_i), ((g - s_x) + np.sqrt(disc)) / (2 * s_i)) if r > 0]


def nf_db(coef, r) -> np.ndarray:
    s_e, s_x, s_i = coef
    return 10 * np.log10(1 + (s_e + r * s_x + r ** 2 * s_i) / (G4 * r))


def fit_three(pts) -> np.ndarray:
    lv = np.array([p[0] for p in pts])
    r = 10 ** np.array([p[1] for p in pts])
    g = (10 ** (lv / 10) - 1) * G4 * r                      # = S_e + S_x R + S_i R^2 on each contour
    a = np.stack([np.ones_like(r), r, r ** 2], axis=1) / g[:, None]
    scale = np.linalg.norm(a, axis=0)
    sol = lsq_linear(a / scale, np.ones_like(g), bounds=([0, -np.inf, 0], [np.inf, np.inf, np.inf]))
    return sol.x / scale


LOW_SIDE_R_MAX = 1e7   # ohm: below 3.98 Hz, crossings above this (the decade under the top edge, where the plot's
                       # contours turn vertical) are left out of the fit of S_e


def fit_se(pts, s_i: float) -> tuple[np.ndarray, list]:
    """S_e alone, with S_x = 0 and S_i held (relative weights), from the crossings below LOW_SIDE_R_MAX where the held
    term S_i R_S^2 is at most a tenth of S_e (iterated from the crossings below 1 Mohm).  Returns the coefficients and
    the crossings used."""
    lv_all = np.array([p[0] for p in pts])
    r_all = 10 ** np.array([p[1] for p in pts])
    r_max = 1e6
    for _ in range(5):
        use = r_all <= r_max
        lv, r = lv_all[use], r_all[use]
        g = (10 ** (lv / 10) - 1) * G4 * r
        w = 1 / g
        s_e = float(np.sum(w * (1 - s_i * r ** 2 * w)) / np.sum(w * w))
        r_max = min(np.sqrt(0.1 * s_e / s_i), LOW_SIDE_R_MAX)
    use = r_all <= r_max
    return np.array([s_e, 0.0, s_i]), [p for p, u in zip(pts, use) if u]


def deviations(coef, pts) -> tuple[float, float]:
    """Largest deviation of a crossing from the fit: in dB of noise figure, and in decades of R_S (to the nearest
    resistance where the fit has that level)."""
    lv = np.array([p[0] for p in pts])
    r = 10 ** np.array([p[1] for p in pts])
    db = float(np.abs(nf_db(coef, r) - lv).max())
    dec = 0.0
    for level, y in pts:
        q = roots(coef, level)
        dec = max(dec, min(abs(np.log10(v) - y) for v in q) if q else np.inf)
    return db, float(dec)


def two_port(contours: list) -> dict:
    rows = []
    for x0 in LOG_F:
        pts = crossings(contours, float(x0))
        coef = fit_three(pts) if len(pts) >= 3 else None
        both = False
        if coef is not None and coef[2] > 0:
            ropt = np.sqrt(coef[0] / coef[2])
            both = bool(any(10 ** y < ropt for _, y in pts) and sum(10 ** y > ropt for _, y in pts) >= 2)
        rows.append(dict(x0=float(x0), pts=pts, coef=coef, both=both))
    first = next(i for i, r in enumerate(rows) if r["both"])
    assert all(r["both"] for r in rows[first:]), [round(r["x0"], 2) for r in rows[first:] if not r["both"]]
    plateau = [r["coef"][2] for r in rows[first:] if np.log10(5.0) - 1e-9 <= r["x0"] <= np.log10(5e3) + 1e-9]
    s_i_low = float(np.median(plateau))
    for r in rows[:first]:
        r["coef"], r["used"] = fit_se(r["pts"], s_i_low)
    devs = [deviations(r["coef"], r.get("used", r["pts"])) for r in rows]
    return dict(log10_f=LOG_F.tolist(), S_e=[float(r["coef"][0]) for r in rows], S_x=[float(r["coef"][1]) for r in rows],
                S_i=[float(r["coef"][2]) for r in rows], fitted=["S_e, S_x, S_i" if r["both"] else "S_e (S_x = 0, S_i "
                                                                 "held)" for r in rows],
                both_sides=[r["both"] for r in rows], crossings=[len(r["pts"]) for r in rows],
                crossings_used=[len(r.get("used", r["pts"])) for r in rows],
                max_dev_db=[d[0] for d in devs], max_dev_decades=[d[1] for d in devs],
                both_sides_from_hz=float(10 ** rows[first]["x0"]), s_i_low=s_i_low,
                s_i_low_range=[float(min(plateau)), float(max(plateau))],
                largest_dev_both_sides=dict(db=max(d[0] for d in devs[first:]), decades=max(d[1] for d in devs[first:])),
                largest_dev_low_side=dict(db=max(d[0] for d in devs[:first]), decades=max(d[1] for d in devs[:first])),
                _points={round(r["x0"], 4): r["pts"] for r in rows})


# ---- what the fit says ------------------------------------------------------------------------------------------
def idx(fit: dict, f0: float) -> int:
    j = int(np.argmin(np.abs(np.array(fit["log10_f"]) - np.log10(f0))))
    assert abs(fit["log10_f"][j] - np.log10(f0)) < 1e-6, f0
    return j


def coef_at(fit: dict, j: int) -> np.ndarray:
    return np.array([fit["S_e"][j], fit["S_x"][j], fit["S_i"][j]])


def model(fit: dict) -> dict:
    at = {}
    for f0 in DECADES:
        j = idx(fit, f0)
        c = coef_at(fit, j)
        pts = fit["_points"][round(fit["log10_f"][j], 4)]
        row = dict(e_n=float(np.sqrt(c[0])), fitted=fit["fitted"][j],
                   drawn_1db_ohm=[float(10 ** y) for lv, y in pts if lv == 1.0],
                   drawn_3db_ohm=[float(10 ** y) for lv, y in pts if lv == 3.0])
        if fit["both_sides"][j]:
            fmin = 1 + (2 * np.sqrt(c[0] * c[2]) + c[1]) / G4
            row.update(i_n=float(np.sqrt(c[2])), corr=float(c[1] / (2 * np.sqrt(c[0] * c[2]))),
                       r_opt=float(np.sqrt(c[0] / c[2])), nf_min_db=float(10 * np.log10(fmin)),
                       fit_1db_ohm=roots(c, 1.0), fit_3db_ohm=roots(c, 3.0))
        at[str(f0)] = row
    i_low = np.sqrt(fit["s_i_low"])
    c_eff = {}
    for f0 in (1e5, 10 ** 5.5, 1e6):
        c = coef_at(fit, idx(fit, f0))
        c_eff[f"{f0:.6g}"] = float(np.sqrt(max(c[2] - i_low ** 2, 0)) / (2 * np.pi * f0 * np.sqrt(c[0])))
    lse = np.log10(np.array(fit["S_e"]))
    lf = np.array(fit["log10_f"])
    slope, stray = {}, {}
    for d0 in range(-1, 6):
        a, b = idx(fit, 10.0 ** d0), idx(fit, 10.0 ** (d0 + 1))
        slope[f"{10.0 ** d0:g}-{10.0 ** (d0 + 1):g}"] = float(lse[b] - lse[a])
        chord = lse[a] + (lse[b] - lse[a]) * (lf[a:b + 1] - lf[a])
        stray[f"{10.0 ** d0:g}-{10.0 ** (d0 + 1):g}"] = float(np.abs(lse[a:b + 1] - chord).max() / 2)
    ew = np.sqrt(fit["S_e"][idx(fit, 1e5)])
    corner = {str(f0): float(f0 * (fit["S_e"][idx(fit, f0)] / ew ** 2 - 1)) for f0 in (10.0, 100.0, 1e3)}
    return dict(at=at, i_n_low=float(i_low), i_n_low_range=[float(np.sqrt(v)) for v in fit["s_i_low_range"]],
                r_equiv_ohm=float(G4 / i_low ** 2), i_n_of_100mohm_at_t0=float(np.sqrt(G4 / R_IN)),
                c_eff_pf={k: v * 1e12 for k, v in c_eff.items()},
                s_e_slope_per_decade=slope, e_n_stray_from_decade_chords_decades=stray, corner_hz=corner,
                e_w_100khz=float(ew))


def spec_check(fit: dict) -> dict:
    """The plot against the specification at 1 kHz."""
    j = idx(fit, 1e3)
    c = coef_at(fit, j)
    pts = fit["_points"][round(fit["log10_f"][j], 4)]
    drawn = min(10 ** y for lv, y in pts if lv == 3.0)
    spec = roots(np.array([SPEC_EN_1K ** 2, 0.0, c[2]]), 3.0)[0]
    per_contour = {f"{lv:g}": float(np.sqrt((10 ** (lv / 10) - 1) * G4 * 10 ** y)) for lv, y in pts
                   if lv >= 3.0 and 10 ** y < np.sqrt(c[0] / c[2])}
    return dict(spec_e_n=SPEC_EN_1K, plot_e_n=float(np.sqrt(c[0])), ratio=float(np.sqrt(c[0]) / SPEC_EN_1K),
                e_n_from_each_low_side_contour_3db_up=per_contour, drawn_3db_low_ohm=float(drawn),
                spec_3db_low_ohm=float(spec))


def corner_check(contours: list) -> dict:
    """The unlabelled corner contours where they meet the 1 MHz edge: their resistances against F - 1."""
    pts = [(lv, 10 ** y) for lv, y in crossings([c for c in contours if c["found"].startswith("unlabelled")], 6.0)]
    pts = sorted(pts)
    assert [p[0] for p in pts] == list(CORNER_LEVELS), pts
    r0, g0 = pts[0][1], 10 ** (pts[0][0] / 10) - 1
    return dict(r_ohm={f"{lv:g}": float(r) for lv, r in pts},
                r_over_r_6db={f"{lv:g}": float(r / r0) for lv, r in pts},
                f_minus_1_over_6db={f"{lv:g}": float((10 ** (lv / 10) - 1) / g0) for lv, _ in pts})


def ac_coupling_check(fit: dict, mod: dict) -> dict:
    f0 = 0.1
    w = 2 * np.pi * f0
    v = mod["i_n_low"] / (w * C_COUPLING)
    return dict(f_hz=f0, i_n_through_coupling_v=float(v), e_n_plot_v=float(np.sqrt(fit["S_e"][idx(fit, f0)])),
                ratio=float(np.sqrt(fit["S_e"][idx(fit, f0)]) / v),
                signal_transfer=float(w * TAU / np.sqrt(1 + (w * TAU) ** 2)))


def versus(fit: dict) -> dict:
    """H, L and the SR560 data sheet's plot minus the 5113 plot, where the plot draws both sides."""
    nz = np.load(spice.RESULTS / "nf_map.npz")
    ds = json.loads((spice.RESULTS / "sr560_nf_datasheet.json").read_text(encoding="utf-8"))["two_port_fit"]
    others = {"H": (np.log10(nz["f_H"]), nz["coef_H"]), "L": (np.log10(nz["f_L"]), nz["coef_L"]),
              "SR560 data sheet": (np.array(ds["log10_f"]), np.array([ds["S_e"], ds["S_x"], ds["S_i"]]))}
    r = 10 ** np.round(np.arange(801) / 100, 2)
    lf5 = np.array(fit["log10_f"])
    mine = [j for j in range(len(lf5)) if fit["both_sides"][j]]
    out = {}
    for name, (lf, co) in others.items():
        cols, pairs = [], []
        for j in mine:
            k = np.flatnonzero(np.abs(lf - lf5[j]) < 1e-6)
            if len(k):
                cols.append(j)
                pairs.append((coef_at(fit, j), co[:, k[0]]))
        diff = np.stack([nf_db(c_o, r) - nf_db(c_m, r) for c_m, c_o in pairs], axis=1)   # rows r, columns f
        lo, hi = np.unravel_index(diff.argmin(), diff.shape), np.unravel_index(diff.argmax(), diff.shape)
        worse = diff > 0.1
        box = None
        if worse.any():
            rr, cc = np.nonzero(worse)
            box = dict(f_hz=[float(10 ** lf5[cols[cc.min()]]), float(10 ** lf5[cols[cc.max()]])],
                       r_ohm=[float(r[rr.min()]), float(r[rr.max()])])
        # where the difference changes sign at the reporting frequencies (log-linear interpolation in R_S)
        cross = {}
        for f0 in (10.0, 100.0, 1e3, 1e4, 1e5, 1e6):
            k = [i for i, j in enumerate(cols) if abs(lf5[j] - np.log10(f0)) < 1e-6]
            if k:
                dd = diff[:, k[0]]
                s = np.flatnonzero(np.sign(dd[:-1]) * np.sign(dd[1:]) < 0)
                cross[str(f0)] = [float(10 ** (np.log10(r[i]) + dd[i] / (dd[i] - dd[i + 1]) * 0.01)) for i in s]
        out[name] = dict(f_hz=[float(10 ** lf5[cols[0]]), float(10 ** lf5[cols[-1]])],
                         min_db=dict(value=float(diff[lo]), f_hz=float(10 ** lf5[cols[lo[1]]]), r_ohm=float(r[lo[0]])),
                         max_db=dict(value=float(diff[hi]), f_hz=float(10 ** lf5[cols[hi[1]]]), r_ohm=float(r[hi[0]])),
                         fraction_lower=float((diff < -0.1).mean()), fraction_within_0p1=float((np.abs(diff) <= 0.1).mean()),
                         fraction_higher=float(worse.mean()), higher_region_bounds=box, equal_at_r_ohm=cross)
    return out


def extract() -> dict:
    ink, check = load()
    cal = calibrate(ink)
    img, chars = clean(ink, cal)
    boxes = labels(chars)
    lab, level, how, bridges = assign(img, boxes, cal)
    contours = contour_lines(lab, level, how, cal)
    fit = two_port(contours)
    mod = model(fit)
    res = dict(source="refs/commercial_preamps/SignalRecovery_AMETEK/SignalRecovery_5113_manual_2002.pdf",
               document="Signal Recovery Model 5113 instruction manual 222144-A-MNL-F (2002)", page_index=PAGE,
               printed_page="A-2", title="Figure A-1, Typical Noise Figure Contours at Gain = x1000, AC Coupling and "
               "10s Coupling Time-Constant, Flat Filter Mode", x_axis="FREQUENCY, 0.1 Hz to 1 MHz",
               y_axis="SOURCE RESISTANCE, 1 ohm to 100 Mohm", levels_db=list(LEVELS), image_check=check,
               calibration=cal, labels_px=[list(map(int, b)) for b in boxes], bridges=bridges,
               coordinates="points: (log10(f / Hz), log10(R_S / ohm))", contours=contours,
               two_port_fit={k: v for k, v in fit.items() if not k.startswith("_")}, model=mod,
               spec_check=spec_check(fit), corner_check=corner_check(contours),
               ac_coupling_check=ac_coupling_check(fit, mod), versus=versus(fit))
    return res, (ink, lab, level)


def check_png(res: dict, ink: np.ndarray, png: str) -> None:
    """The traced contours over the plot's image (pixel coordinates), coloured by level."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import plot_style as PS
    cal = res["calibration"]
    cyc = PS.COLOR_CYCLE
    h, w = ink.shape
    fig = plt.figure(figsize=(w / 100, h / 100), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(np.where(ink, 0.75, 1.0), cmap="gray", vmin=0, vmax=1, interpolation="nearest")
    for c in res["contours"]:
        p = np.array(c["points"])
        col = cyc[LEVELS.index(c["level_db"]) % len(cyc)]
        ax.plot(cal["x_px_at_1hz"] + p[:, 0] * cal["px_per_decade_f"], cal["y_px_at_1ohm"] + p[:, 1] * cal["px_per_decade_r"],
                lw=0.5, color=col)
        m = p[len(p) // 2]
        ax.text(cal["x_px_at_1hz"] + m[0] * cal["px_per_decade_f"] + 3, cal["y_px_at_1ohm"] + m[1] * cal["px_per_decade_r"] - 3,
                f"{c['level_db']:g}", fontsize=4, color=col)
    ax.set_axis_off()
    fig.savefig(png, dpi=200)
    plt.close(fig)
    print(f"check image {png}")


def main(args: list[str]) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    res, (ink, _, _) = extract()
    cal, fit, mod = res["calibration"], res["two_port_fit"], res["model"]
    print(f"image check: {res['image_check']['ink_within_1px_of_render']:.4f} of the ink within 1 px of the page render "
          f"({res['image_check']['the_same_unflipped']:.4f} unflipped)")
    print(f"calibration: {cal['px_per_decade_f']:.3f} px/decade (f), {cal['px_per_decade_r']:.3f} (R); largest residual "
          f"{cal['max_residual_px']:.2f} px")
    for c in res["contours"]:
        p = np.array(c["points"])
        print(f"{c['level_db']:5g} dB: {c['n_points']:4d} points, f 10^{p[:, 0].min():.2f}-10^{p[:, 0].max():.2f} Hz, "
              f"R 10^{p[:, 1].min():.2f}-10^{p[:, 1].max():.2f} ohm; {c['found']}")
    print(f"two-port: both sides from {fit['both_sides_from_hz']:.3g} Hz; largest deviation there "
          f"{fit['largest_dev_both_sides']['db']:.3f} dB, {fit['largest_dev_both_sides']['decades']:.4f} decade; below, "
          f"{fit['largest_dev_low_side']['db']:.3f} dB, {fit['largest_dev_low_side']['decades']:.4f} decade")
    for f0, row in mod["at"].items():
        extra = (f", i_n {row['i_n'] * 1e15:.2f} fA, corr {row['corr']:+.3f}, R_opt {row['r_opt']:.3g}, NF_min "
                 f"{row['nf_min_db']:.3f} dB, fit 1 dB {[f'{v:.3g}' for v in row['fit_1db_ohm']]}, 3 dB "
                 f"{[f'{v:.3g}' for v in row['fit_3db_ohm']]}") if "i_n" in row else ""
        print(f"  {float(f0):>8g} Hz: e_n {row['e_n'] * 1e9:9.3f} nV{extra}; drawn 1 dB "
              f"{[f'{v:.3g}' for v in row['drawn_1db_ohm']]}, 3 dB {[f'{v:.3g}' for v in row['drawn_3db_ohm']]}")
    print(f"i_n low {mod['i_n_low'] * 1e15:.2f} fA ({mod['i_n_low_range'][0] * 1e15:.2f}-{mod['i_n_low_range'][1] * 1e15:.2f}) "
          f"= 4kT0/R, R = {mod['r_equiv_ohm'] / 1e6:.1f} Mohm (100 Mohm: {mod['i_n_of_100mohm_at_t0'] * 1e15:.2f} fA); "
          f"C_eff {mod['c_eff_pf']}")
    print("S_e slope per decade:", {k: round(v, 3) for k, v in mod["s_e_slope_per_decade"].items()})
    print("e_n off the decade chords (decade):", {k: round(v, 4) for k, v in mod["e_n_stray_from_decade_chords_decades"].items()})
    print("corner (Hz):", {k: round(v) for k, v in mod["corner_hz"].items()})
    print("spec:", res["spec_check"])
    print("corner check:", res["corner_check"])
    print("AC coupling:", res["ac_coupling_check"])
    for k, v in res["versus"].items():
        print(f"{k} minus 5113: {v['f_hz'][0]:.3g}-{v['f_hz'][1]:.3g} Hz; lower {v['fraction_lower']:.1%}, within "
              f"{v['fraction_within_0p1']:.1%}, higher {v['fraction_higher']:.1%} ({v['higher_region_bounds']}); min "
              f"{v['min_db']}, max {v['max_db']}")
    (spice.RESULTS / "nf5113_manual.json").write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    if args[:1] == ["--check"]:
        check_png(res, ink, args[1])


if __name__ == "__main__":
    main(sys.argv[1:])
