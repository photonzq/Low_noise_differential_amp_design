"""Shared Matplotlib style for the figures of the low-noise preamplifier note.

The style follows the plotting guide used for all notes in this folder: Arial for text,
Computer Modern for mathematics (no external LaTeX), 8 pt everywhere, a restrained palette,
all four spines with inward ticks, no grid, 600 dpi PNG plus PDF with editable (Type 42) text.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.ticker import LogFormatterMathtext  # noqa: E402,F401

FONT_SIZE = 8.0

COLORS = {
    "primary": "#385C9E",
    "neutral": "#4D4D4D",
    "warm_accent": "#9E403D",
    "cool_accent": "#477A57",
    "purple_accent": "#6B5B95",
    "teal_accent": "#3F7F82",
    "brown_accent": "#7D5C46",
    "grey_accent": "#6F6F6F",
    "highlight": "#EED671",
    "annotation": "#767676",
    "text": "#272727",
    "axes": "#000000",
    "background": "#FFFFFF",
}
HIGHLIGHT_ALPHA = 0.24
MUTED_CLASSIC_COLORS = ["#385C9E", "#7891B8", "#C4CEDD", "#F7F7F4", "#E2C2BC", "#BE7773", "#9E403D"]
MUTED_CLASSIC_CMAP = LinearSegmentedColormap.from_list("muted_classic", MUTED_CLASSIC_COLORS, N=256)
COLOR_CYCLE = [COLORS[k] for k in ("primary", "warm_accent", "cool_accent", "purple_accent",
                                    "teal_accent", "brown_accent", "grey_accent")]
LW = 1.5
DASHED = (0, (5, 2))

FIGURES = Path(__file__).resolve().parent.parent / "figures"


def configure_plot_style() -> None:
    """Apply the project Matplotlib style without external LaTeX."""
    plt.rcParams.update({
        "figure.facecolor": COLORS["background"],
        "axes.facecolor": COLORS["background"],
        "axes.edgecolor": COLORS["axes"],
        "axes.labelcolor": COLORS["text"],
        "text.color": COLORS["text"],
        "xtick.color": COLORS["axes"],
        "ytick.color": COLORS["axes"],
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "DejaVu Sans", "sans-serif"],
        "font.size": FONT_SIZE,
        "axes.labelsize": FONT_SIZE,
        "axes.titlesize": FONT_SIZE,
        "xtick.labelsize": FONT_SIZE,
        "ytick.labelsize": FONT_SIZE,
        "legend.fontsize": FONT_SIZE,
        "axes.linewidth": 0.8,
        "axes.prop_cycle": plt.cycler(color=COLOR_CYCLE),
        "axes.spines.top": True,
        "axes.spines.right": True,
        "xtick.top": True,
        "ytick.right": True,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "legend.frameon": False,
        "axes.grid": False,
        "text.usetex": False,
        "mathtext.fontset": "cm",
        "axes.formatter.use_mathtext": True,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "savefig.facecolor": "white",
        "savefig.bbox": "tight",
        "lines.linewidth": LW,
    })


def export(fig, stem: str, folder: Path | None = None) -> Path:
    """Save stem.png (600 dpi) and stem.pdf into the figures folder; returns the PNG path."""
    out = (folder or FIGURES) / stem
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out.with_suffix(".png"), dpi=600)
    fig.savefig(out.with_suffix(".pdf"))
    plt.close(fig)
    return out.with_suffix(".png")


def panel_label(ax, text: str, x: float = -0.16, y: float = 1.02) -> None:
    """Bold panel letter in the upper left corner, outside the axes."""
    ax.text(x, y, text, transform=ax.transAxes, fontsize=FONT_SIZE, fontweight="bold",
            va="bottom", ha="left")


def fmt_sci(val: float, precision: int = 1) -> str:
    """Number as mathtext a x 10^b."""
    exponent = int(np.floor(np.log10(abs(val)))) if val != 0 else 0
    coeff = val / (10 ** exponent)
    return rf"${coeff:.{precision}f} \times 10^{{{exponent}}}$"
