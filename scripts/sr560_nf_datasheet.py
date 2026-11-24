"""The noise-figure contours of the SR560 data sheet (refs/benchmark/SRS_SR560_datasheet.pdf, printed page 3 =
PyMuPDF index 2, "SR560 Noise Figure"), read from the PDF's vector paths, so that the note can draw them on the
same axes as its own noise-figure maps (nf_map.py).  Nothing is traced by eye.

The plot is drawn as straight line segments: the frame and its tick marks with thin lines (0.22 pt), the frame
and the contours with 0.89 pt lines.  The contours are recovered by chaining their segments end to end.  The
axes are calibrated on the tick marks, one per decade, whose labels are read from the page: frequency 1 Hz to
10^6 Hz ("Frequency (Hz)"), source resistance 1 ohm to 10^8 ohm ("SOURCE RESISTANCE IN OHMS AT 290K").  Each
contour's level is the label printed on it: the labels sit in white boxes that hide the line under them, so the
contour nearest to a label's centre is the one it names.  The five contours in the upper right corner carry no
label; there the noise figure rises towards the corner (the source's signal and noise are both shunted by the
input capacitance), so they take the levels above the 3 dB contour that bounds them, 6, 10, 15, 20 and 25 dB,
in order towards the corner: the levels of the labelled contours on the low-resistance side.

The contours are those of a noisy two-port: at each frequency, F = 1 + (S_e + R_S S_x + R_S^2 S_i) / (4 k T0 R_S)
(T0 = 290 K; S_e = |e_n|^2, S_i = |i_n|^2, S_x = 2 Re(e_n i_n*), as in nf_map.py) fits the points where the
contours cross that frequency to within a few thousandths of a decade of R_S, the precision of the drawing.
The fit, on nf_map.py's frequency grid (20 points per decade, 1 Hz to 1 MHz), is the data sheet's noise figure
between its contours, from which the note's figure draws differences; it also shows what SRS's plot assumes
(e_n, the input resistors' noise current, an effective input capacitance; "model" in the output).

Writes ../sim/results/sr560_nf_datasheet.json: the calibration, per contour its level and its points as
(log10(f / Hz), log10(R_S / ohm)), and the two-port fit with its largest deviations.
Usage: python sr560_nf_datasheet.py [--check out.png]   (--check: the extracted contours drawn over a render of
the page, for inspection; the render is of SRS's figure, so keep it out of the repository)
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict

import numpy as np
import pymupdf

import spice

PDF = spice.ROOT / "refs" / "benchmark" / "SRS_SR560_datasheet.pdf"
PAGE = 2                                   # PyMuPDF index; printed page 3
LEVELS = (0.05, 0.15, 0.5, 1.0, 3.0, 6.0, 10.0, 15.0, 20.0, 25.0)
CORNER_LEVELS = (6.0, 10.0, 15.0, 20.0, 25.0)
K_B, T0 = 1.380649e-23, 290.0
LOG_F = np.round(np.arange(121) / 20, 4)   # 1 Hz to 1 MHz, 20 per decade (nf_map.py's grid)


def plot_frame(page) -> pymupdf.Rect:
    """The plot's frame: the area between the title "SR560 Noise Figure" and the axis label "Frequency (Hz)",
    narrowed to the extent of the thin tick drawings found there."""
    title = page.search_for("SR560 Noise Figure")
    assert len(title) == 1, title
    xlab = sorted((r for r in page.search_for("Frequency (Hz)") if r.y0 > title[0].y1), key=lambda r: r.y0)
    assert xlab, "no axis label below the title"   # the page's other plot has its own "Frequency (Hz)", above
    area = pymupdf.Rect(title[0].x0 - 120, title[0].y1, title[0].x1 + 120, xlab[0].y0)
    thin = [d for d in page.get_drawings() if d.get("width") and d["width"] < 0.5 and d["rect"] in area]
    r = thin[0]["rect"]
    for d in thin[1:]:
        r |= d["rect"]
    return r


def ticks(page, frame: pymupdf.Rect) -> tuple[list[float], list[float]]:
    """Positions of the vertical and horizontal thin segments in the frame (the tick marks and grid edges).
    The ticks on opposite edges of the frame differ by up to 0.04 pt: positions within 0.2 pt are one tick,
    at their mean."""
    xs, ys = [], []
    for d in page.get_drawings():
        if not (d.get("width") and d["width"] < 0.5 and d["rect"] in frame + (-1, -1, 1, 1)):
            continue
        for it in d["items"]:
            if it[0] != "l":
                continue
            a, b = it[1], it[2]
            if abs(a.x - b.x) < 0.01:
                xs.append((a.x + b.x) / 2)
            elif abs(a.y - b.y) < 0.01:
                ys.append((a.y + b.y) / 2)

    def merged(v):
        groups = []
        for x in sorted(v):
            if groups and x - groups[-1][-1] < 0.2:
                groups[-1].append(x)
            else:
                groups.append([x])
        return [float(np.mean(g)) for g in groups]

    return merged(xs), merged(ys)


def tick_labels(page, frame: pymupdf.Rect) -> tuple[dict, dict]:
    """The decade labels below and left of the frame: '1' (10^0), '10' (10^1), '10' with a superscript n (10^n).
    Returns {exponent: centre position} for the frequency axis (x) and the resistance axis (y)."""
    spans = []
    for b in page.get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            if ln["dir"] != (1.0, 0.0):
                continue
            for sp in ln["spans"]:
                spans.append((sp["text"].strip(), pymupdf.Rect(sp["bbox"]), sp["size"]))
    base = [s for s in spans if s[0] in ("1", "10") and s[2] > 4.0]
    sup = [s for s in spans if s[0].isdigit() and s[2] < 4.0]
    xl, yl = {}, {}
    for t, r, _ in base:
        below = frame.y1 < r.y0 + 2 < frame.y1 + 6 and frame.x0 - 4 < r.x0 < frame.x1 + 4
        left = r.x1 < frame.x0 and frame.y0 - 6 < r.y0 < frame.y1 + 2
        if not (below or left):
            continue
        n = 0 if t == "1" else 1
        hit = [s for s in sup if abs(s[1].x0 - r.x1) < 1.0 and abs(s[1].y0 - r.y0) < 2.0]
        if hit:
            n = int(hit[0][0])
            r = r | hit[0][1]
        (xl if below else yl)[n] = ((r.x0 + r.x1) / 2) if below else ((r.y0 + r.y1) / 2)
    return xl, yl


def calibrate(xs: list[float], ys: list[float], xl: dict, yl: dict) -> dict:
    """Linear maps from page coordinates to decades, fitted on the tick marks, each tick matched to its label."""
    assert len(xs) == len(xl) == 7 and len(ys) == len(yl) == 9, (xs, xl, ys, yl)
    assert sorted(xl) == list(range(7)) and sorted(yl) == list(range(9))
    for n, x in enumerate(xs):                        # frequency: decade n at the n-th tick from the left
        assert abs(xl[n] - x) < 3.0, (n, xl[n], x)
    ys_up = ys[::-1]                                  # resistance: decade n at the n-th tick from the bottom
    for n, y in enumerate(ys_up):
        assert abs(yl[n] - y) < 3.0, (n, yl[n], y)
    bx, ax = np.polyfit(np.arange(7), xs, 1)
    by, ay = np.polyfit(np.arange(9), ys_up, 1)
    res_x = np.abs(np.polyval([bx, ax], np.arange(7)) - xs).max()
    res_y = np.abs(np.polyval([by, ay], np.arange(9)) - ys_up).max()
    return dict(x0_pt=ax, pt_per_decade_x=bx, y0_pt=ay, pt_per_decade_y=by,
                max_tick_residual_pt=float(max(res_x, res_y)), ticks_x_pt=xs, ticks_y_pt=ys)


def chains(page, frame: pymupdf.Rect) -> list[list[tuple[float, float]]]:
    """The 0.89 pt segments in the frame, chained end to end into polylines; the frame itself is dropped."""
    segs = []
    for d in page.get_drawings():
        if d.get("width") and d["width"] > 0.8 and d["rect"].intersects(frame):
            segs += [(it[1], it[2]) for it in d["items"] if it[0] == "l"]
    key = lambda p: (round(p.x, 2), round(p.y, 2))   # noqa: E731
    ends = defaultdict(list)
    for i, (a, b) in enumerate(segs):
        ends[key(a)].append(i)
        ends[key(b)].append(i)
    used = [False] * len(segs)
    lines = []
    for i in range(len(segs)):
        if used[i]:
            continue
        used[i] = True
        pts = [key(segs[i][0]), key(segs[i][1])]
        for forward in (True, False):
            while True:
                cur = pts[-1] if forward else pts[0]
                nxt = [j for j in ends[cur] if not used[j]]
                if not nxt:
                    break
                used[nxt[0]] = True
                a, b = key(segs[nxt[0]][0]), key(segs[nxt[0]][1])
                other = b if a == cur else a
                if forward:
                    pts.append(other)
                else:
                    pts.insert(0, other)
        lines.append(pts)

    def on_frame(p):
        return min(abs(p[0] - frame.x0), abs(p[0] - frame.x1), abs(p[1] - frame.y0), abs(p[1] - frame.y1)) < 0.2

    return [ln for ln in lines if not all(on_frame(p) for p in ln)]


def distance(p, line) -> float:
    """Shortest distance from point p to a polyline."""
    best = np.inf
    px, py = p
    for (x1, y1), (x2, y2) in zip(line[:-1], line[1:]):
        dx, dy = x2 - x1, y2 - y1
        t = 0.0 if dx == dy == 0 else max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        best = min(best, float(np.hypot(px - x1 - t * dx, py - y1 - t * dy)))
    return best


def levels(page, frame: pymupdf.Rect, lines: list) -> tuple[list, list]:
    """Each polyline's level (dB) and how it was found ('label' with the label's distance in pt, or 'corner')."""
    labels = []
    for b in page.get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            t = "".join(sp["text"] for sp in ln["spans"]).strip()
            r = pymupdf.Rect(ln["bbox"])
            if t.endswith("dB") and r in frame:
                labels.append((float(t[:-2]), ((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)))
    assert len(labels) == 15, labels
    lev, how = [None] * len(lines), [None] * len(lines)
    for value, c in labels:
        d = [distance(c, ln) for ln in lines]
        k = int(np.argmin(d))
        assert d[k] < 2.0 and sorted(d)[1] > d[k] + 1.0, (value, sorted(d)[:3])   # unambiguous
        assert lev[k] in (None, value), (k, lev[k], value)
        lev[k] = value
        how[k] = f"label at ({c[0]:.1f}, {c[1]:.1f}) pt, {d[k]:.2f} pt away"
    rest = [k for k in range(len(lines)) if lev[k] is None]
    assert len(rest) == len(CORNER_LEVELS), rest
    for k in rest:                  # each runs from the top edge to the right edge of the frame
        (xa, ya), (xb, yb) = lines[k][0], lines[k][-1]
        assert {round(ya, 1), round(xb, 1)} <= {round(frame.y0, 1), round(frame.x1, 1)} or \
               {round(yb, 1), round(xa, 1)} <= {round(frame.y0, 1), round(frame.x1, 1)}, (k, lines[k][0], lines[k][-1])
    # towards the corner: the point where each meets the top edge moves right
    order = sorted(rest, key=lambda k: min(p[0] for p in lines[k] if abs(p[1] - frame.y0) < 0.2))
    for k, value in zip(order, CORNER_LEVELS):
        lev[k] = value
        how[k] = "corner (unlabelled; levels in order towards the upper right corner)"
    assert sorted(set(lev)) == sorted(LEVELS), lev
    return lev, how


def crossings(contours: list, x0: float, tol: float = 0.003) -> list[tuple[float, float]]:
    """(level, log10 R_S) where each contour meets log10(f) = x0.  A contour that ends on the frame's left or
    right edge ends within tol (0.1 pt) of 0 or 6 after the calibration: its end point counts there.  A vertex
    on the line is found by both of its segments: values within 0.001 decade are one crossing."""
    out = []
    for c in contours:
        x, y = np.array(c["points"]).T
        found = [y[k] + (x0 - x[k]) / (x[k + 1] - x[k]) * (y[k + 1] - y[k]) for k in range(len(x) - 1)
                 if (x[k] - x0) * (x[k + 1] - x0) <= 0 and x[k] != x[k + 1]]
        found += [y[k] for k in (0, -1) if abs(x[k] - x0) <= tol]
        merged = []
        for v in sorted(found):
            if not merged or v - merged[-1] > 1e-3:
                merged.append(v)
        out += [(c["level_db"], float(v)) for v in merged]
    return sorted(out)


def level_roots(coef, level_db: float) -> list[float]:
    """The resistances (ohm) where the two-port's noise figure is level_db."""
    s_e, s_x, s_i = coef
    g = (10 ** (level_db / 10) - 1) * 4 * K_B * T0
    disc = (s_x - g) ** 2 - 4 * s_i * s_e
    if s_i <= 0 or disc < 0:
        return []
    return [r for r in (((g - s_x) - np.sqrt(disc)) / (2 * s_i), ((g - s_x) + np.sqrt(disc)) / (2 * s_i)) if r > 0]


def two_port_fit(contours: list) -> dict:
    """S_e, S_x, S_i at each frequency of LOG_F, fitted to the contours' crossings (relative weights), and the
    largest deviations of a crossing from the fit: in dB of noise figure, and in decades of R_S (the distance
    to the nearest resistance where the fit has that level)."""
    rows, dev_db, dev_dec = [], 0.0, 0.0
    for x0 in LOG_F:
        pts = crossings(contours, x0)
        lv = np.array([p[0] for p in pts])
        r = 10 ** np.array([p[1] for p in pts])
        g = (10 ** (lv / 10) - 1) * 4 * K_B * T0 * r          # = S_e + S_x R + S_i R^2 on each contour
        a = np.stack([np.ones_like(r), r, r ** 2], axis=1) / g[:, None]
        scale = np.linalg.norm(a, axis=0)
        coef = np.linalg.lstsq(a / scale, np.ones_like(g), rcond=None)[0] / scale
        fit = np.stack([np.ones_like(r), r, r ** 2], axis=1) @ coef
        dev_db = max(dev_db, float(np.abs(10 * np.log10(1 + fit / (4 * K_B * T0 * r)) - lv).max()))
        for (level, y) in pts:
            roots = level_roots(coef, level)
            assert roots, (x0, level)
            dev_dec = max(dev_dec, min(abs(np.log10(q) - y) for q in roots))
        rows.append((len(pts), *coef))
    n, s_e, s_x, s_i = (np.array(c) for c in zip(*rows))
    assert n.min() >= 6, n.min()
    return dict(log10_f=LOG_F.tolist(), S_e=s_e.tolist(), S_x=s_x.tolist(), S_i=s_i.tolist(),
                crossings_per_frequency=[int(n.min()), int(n.max())], max_dev_db=dev_db, max_dev_decades=dev_dec)


def implied_model(fit: dict) -> dict:
    """What the fit says SRS assumed: e_n and i_n at a few frequencies, the resistance whose thermal noise at T0
    is the low-frequency i_n, the capacitance C with i_n^2 = i_n(low)^2 + (e_n 2 pi f C)^2 at high frequencies,
    and the largest |correlation| S_x / (2 sqrt(S_e S_i))."""
    lf = np.array(fit["log10_f"])
    s_e, s_x, s_i = (np.array(fit[k]) for k in ("S_e", "S_x", "S_i"))
    at = {}
    for f0 in (1.0, 10.0, 100.0, 1e3, 1e4, 1e5, 1e6):
        j = int(np.argmin(np.abs(lf - np.log10(f0))))
        at[str(f0)] = dict(e_n=float(np.sqrt(s_e[j])), i_n=float(np.sqrt(s_i[j])))
    i_low = float(np.sqrt(np.median(s_i[(lf >= 1) & (lf <= 3)])))
    hf = lf >= 5
    c = np.sqrt(np.maximum(s_i[hf] - i_low ** 2, 0) / s_e[hf]) / (2 * np.pi * 10 ** lf[hf])
    return dict(at=at, i_n_low=i_low, r_equiv_ohm=4 * K_B * T0 / i_low ** 2, c_eff_pf_100k_1M=[float(c.min() * 1e12),
                float(c.max() * 1e12)], max_abs_corr=float(np.abs(s_x / (2 * np.sqrt(s_e * s_i))).max()))


def extract() -> dict:
    page = pymupdf.open(PDF)[PAGE]
    frame = plot_frame(page)
    xs, ys = ticks(page, frame)
    xl, yl = tick_labels(page, frame)
    cal = calibrate(xs, ys, xl, yl)
    lines = chains(page, frame)
    lev, how = levels(page, frame, lines)
    to_dec = lambda p: (round((p[0] - cal["x0_pt"]) / cal["pt_per_decade_x"], 4),   # noqa: E731
                        round((p[1] - cal["y0_pt"]) / cal["pt_per_decade_y"], 4))
    contours = sorted(({"level_db": lv, "found": h, "n_points": len(ln), "points": [to_dec(p) for p in ln]}
                       for ln, lv, h in zip(lines, lev, how)), key=lambda c: (c["level_db"], c["points"][0]))
    fit = two_port_fit(contours)
    return dict(source="refs/benchmark/SRS_SR560_datasheet.pdf", page_index=PAGE, printed_page=3,
                title="SR560 Noise Figure", x_axis="Frequency (Hz), 1 to 10^6", y_axis=
                "SOURCE RESISTANCE IN OHMS AT 290K, 1 to 10^8", levels_db=list(LEVELS),
                frame_pt=[frame.x0, frame.y0, frame.x1, frame.y1], calibration=cal,
                coordinates="points: (log10(f / Hz), log10(R_S / ohm))", contours=contours,
                two_port_fit=fit, model=implied_model(fit))


def check(res: dict, png: str) -> None:
    """The extracted contours, mapped back to page coordinates, over a 600 dpi render of the plot."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    page = pymupdf.open(PDF)[PAGE]
    x0, y0, x1, y1 = res["frame_pt"]
    clip = pymupdf.Rect(x0 - 30, y0 - 25, x1 + 10, y1 + 25)
    pix = page.get_pixmap(dpi=600, clip=clip)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    s = 600 / 72
    cal = res["calibration"]
    fig, ax = plt.subplots(figsize=(pix.width / 200, pix.height / 200), dpi=200)
    ax.imshow(img, extent=(clip.x0, clip.x1, clip.y1, clip.y0))
    cmap = plt.get_cmap("tab10")
    for c in res["contours"]:
        p = np.array(c["points"])
        ax.plot(cal["x0_pt"] + p[:, 0] * cal["pt_per_decade_x"], cal["y0_pt"] + p[:, 1] * cal["pt_per_decade_y"],
                lw=0.6, color=cmap(LEVELS.index(c["level_db"])), alpha=0.8)
        ax.text(cal["x0_pt"] + p[len(p) // 2, 0] * cal["pt_per_decade_x"],
                cal["y0_pt"] + p[len(p) // 2, 1] * cal["pt_per_decade_y"], f"{c['level_db']:g}",
                fontsize=4, color=cmap(LEVELS.index(c["level_db"])))
    ax.set_axis_off()
    fig.savefig(png, bbox_inches="tight", pad_inches=0)
    print(f"check image {png} ({s:.2f} px/pt)")


def main(args: list[str]) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    res = extract()
    cal = res["calibration"]
    print(f"frame {res['frame_pt']}; {cal['pt_per_decade_x']:.3f} pt/decade (f), {cal['pt_per_decade_y']:.3f} pt/decade "
          f"(R); largest tick residual {cal['max_tick_residual_pt']:.3f} pt")
    for c in res["contours"]:
        p = np.array(c["points"])
        print(f"{c['level_db']:5g} dB: {c['n_points']:4d} points, f 10^{p[:, 0].min():.2f}-10^{p[:, 0].max():.2f} Hz, "
              f"R 10^{p[:, 1].min():.2f}-10^{p[:, 1].max():.2f} ohm; {c['found']}")
    fit, m = res["two_port_fit"], res["model"]
    print(f"two-port fit: {fit['crossings_per_frequency']} crossings per frequency, largest deviation "
          f"{fit['max_dev_db']:.3f} dB, {fit['max_dev_decades']:.4f} decade of R_S")
    print("implied: " + ", ".join(f"{float(k):g} Hz: e_n {v['e_n'] * 1e9:.2f} nV, i_n {v['i_n'] * 1e15:.1f} fA"
                                  for k, v in m["at"].items()))
    print(f"         i_n at low frequencies {m['i_n_low'] * 1e15:.2f} fA = thermal noise of {m['r_equiv_ohm'] / 1e6:.1f} "
          f"Mohm at 290 K; C_eff {m['c_eff_pf_100k_1M'][0]:.1f}-{m['c_eff_pf_100k_1M'][1]:.1f} pF (100 kHz-1 MHz); "
          f"largest |correlation| {m['max_abs_corr']:.3f}")
    (spice.RESULTS / "sr560_nf_datasheet.json").write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    if args[:1] == ["--check"]:
        check(res, args[1])


if __name__ == "__main__":
    main(sys.argv[1:])
