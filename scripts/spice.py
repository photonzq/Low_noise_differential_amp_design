"""Deck writing, running and result reading for the low-noise preamplifier note.

Every deck is written into its own folder under ../sim/runs/<name>/ and sourced from there by
ngspice-46, loaded as the shared library that KiCad 10 installs (ngspice_shared.py).  The decks
are plain ngspice input; bulk results are written with wrdata (one shared first column, a header
line).  The console output of every run is kept beside the deck as run.log and searched for
errors.

Noise: the analysis is always run in a deck of its own with pts_per_summary = 1, so that the
noise plot holds one vector per noise generator (onoise_<device>[_<sub-generator>]) next to the
totals; read_noise() returns them all.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np

from ngspice_shared import NgSpice

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "sim" / "runs"
RESULTS = ROOT / "sim" / "results"
LIB = ROOT / "sim" / "models" / "_lib"
KT = 1.380649e-23 * 300.15          # ngspice's default temperature, 27 C
Q = 1.602176634e-19

OPTIONS = ".options reltol=1e-4 abstol=1e-15 vntol=1e-9 gmin=1e-14 itl1=500 itl4=200\n"
ERRORS = re.compile(r"error|singular|timestep too small|no convergence|aborted|unknown model|"
                    r"could not find|not found|fatal", re.I)

_NG: NgSpice | None = None


def ng() -> NgSpice:
    global _NG
    if _NG is None:
        _NG = NgSpice()
    return _NG


def lib(name: str) -> str:
    """Include line for a prepared model library, by absolute path in quotes (the volume
    that holds this folder has a space in its name and no short names)."""
    return f'.include "{(LIB / name).as_posix()}"\n'


def run(name: str, deck: str, allow: tuple[str, ...] = ()) -> Path:
    """Write deck.cir into RUNS/name, run it, keep run.log; raise on an error message
    (except lines matching one of the regular expressions in allow).  Returns the folder."""
    folder = RUNS / name
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("*.txt"):
        old.unlink()
    path = folder / "deck.cir"
    path.write_text(deck, encoding="utf-8", newline="\n")
    out = ng().run_deck(path)
    (folder / "run.log").write_text(out, encoding="utf-8", newline="\n")
    bad = []
    for line in re.split(r"(?=std(?:out|err) )", out):
        if ERRORS.search(line) and not any(re.search(a, line, re.I) for a in allow):
            if "warning" in line.lower() and "error" not in line.lower():
                continue
            bad.append(line.strip())
    if bad:
        raise RuntimeError(f"ngspice reported problems in {name}:\n" + "\n".join(bad[:12]))
    return folder


def printed(folder: Path, name: str) -> float:
    """A value printed with 'print name' in the run's log."""
    text = (folder / "run.log").read_text(encoding="utf-8")
    m = re.findall(re.escape(name) + r"\s*=\s*([-+0-9.eE]+)", text)
    if not m:
        raise KeyError(f"{name} not printed in {folder}")
    return float(m[-1])


def read_table(path: Path) -> dict[str, np.ndarray]:
    """A wrdata file with header (set wr_vecnames, wr_singlescale): name -> column.  Complex
    vectors take two columns; they are returned as complex arrays."""
    with open(path, encoding="utf-8") as fh:
        head = fh.readline().split()
    data = np.loadtxt(path, skiprows=1, ndmin=2)
    out: dict[str, np.ndarray] = {}
    # ngspice writes a complex vector as two columns (real, imaginary) under the same name
    k = 0
    while k < len(head):
        nm = head[k]
        if k + 1 < len(head) and head[k + 1] == nm:
            out.setdefault(nm, data[:, k] + 1j * data[:, k + 1])
            k += 2
        else:
            out.setdefault(nm, data[:, k])
            k += 1
    for key in ("frequency", "time"):
        if key in out and np.iscomplexobj(out[key]):
            out[key] = out[key].real
    return out


WR = "set wr_singlescale\nset wr_vecnames\noption numdgt=7\n"


def noise_control(out_node: str, src: str, fstart=1.0, fstop=100e6, ppd=20, extra="") -> str:
    """Control block of a noise run: output noise at out_node referred through src, every
    generator kept (pts_per_summary = 1)."""
    return (f".control\n{WR}noise v({out_node}) {src} dec {ppd} {fstart:g} {fstop:g} 1\n"
            f"setplot noise1\nwrdata noise.txt all\n{extra}.endc\n")


def read_noise(folder: Path) -> dict[str, np.ndarray]:
    """Noise vectors: frequency, onoise_spectrum, inoise_spectrum and every onoise_<generator>
    (densities in V/rtHz at the output; inoise in V/rtHz or A/rtHz at the source)."""
    return read_table(folder / "noise.txt")


def integrate(f: np.ndarray, s: np.ndarray, lo: float, hi: float) -> float:
    """rms of a density s over [lo, hi], with the end values interpolated in log f."""
    inside = (f > lo) & (f < hi)
    ends = np.interp(np.log10([lo, hi]), np.log10(f), s ** 2)
    return math.sqrt(float(np.trapezoid(np.concatenate([[ends[0]], s[inside] ** 2, [ends[1]]]),
                                        np.concatenate([[lo], f[inside], [hi]]))))


def at(f: np.ndarray, y: np.ndarray, f0: float) -> float:
    """Value at f0, interpolated in log f (real arrays)."""
    return float(np.interp(math.log10(f0), np.log10(f), y))


def at_c(f: np.ndarray, y: np.ndarray, f0: float) -> complex:
    re_ = np.interp(math.log10(f0), np.log10(f), y.real)
    im_ = np.interp(math.log10(f0), np.log10(f), y.imag)
    return complex(re_, im_)


def f3db(f: np.ndarray, mag: np.ndarray, ref: float | None = None) -> float:
    """First frequency where |H| falls 3 dB below ref (default: the value at the first point)."""
    ref = mag[0] if ref is None else ref
    lvl = ref / math.sqrt(2)
    idx = np.where(mag < lvl)[0]
    if len(idx) == 0:
        return float("nan")
    i = idx[0]
    if i == 0:
        return float(f[0])
    x0, x1 = math.log10(f[i - 1]), math.log10(f[i])
    y0, y1 = mag[i - 1], mag[i]
    return 10 ** (x0 + (lvl - y0) * (x1 - x0) / (y1 - y0))


def thermal(r: float) -> float:
    """Thermal noise density of a resistor at 27 C, V/rtHz."""
    return math.sqrt(4 * KT * r)
