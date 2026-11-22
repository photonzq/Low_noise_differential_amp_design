"""Transient check for parasitic oscillation in the front end: the front end alone with both inputs
quiet, run for 1 us at 0.05 ns steps; reports the peak-to-peak swing of the outputs, of the summing
node and of the source node after 0.3 us, and the dominant frequency.  An AC loop-gain run
(frontend.check_loop) breaks only the outer loop and does not show an instability of the op amp's
own local loop, which is what this check found in the first version of the front ends (THS4021 at a
high-frequency noise gain near 1 + C_node / (C_I + C_X), below its minimum stable gain of 10): an
oscillation near 280-290 MHz with about 1 V peak-to-peak at each output, in common mode.

Measures, for each saved node voltage v(t) (v(oa), v(ob), v(ca), v(sa)) and for the outputs'
common and differential parts  v_cm = (v(oa) + v(ob)) / 2,  v_dm = v(oa) - v(ob):
    window   0.3 us < t <= 1 us  (the start from the operating point excluded)
    pkpk   = max v - min v  over the window
    f_dom  = k_max / T_w,  k_max = argmax_{k >= 1} |sum_n w_n (v_n - <v>) exp(-2 pi j k n / N)|
             with v resampled linearly onto N = 8192 uniform points of the window (length T_w),
             w the Hann window; the resolution 1 / T_w = 1.43 MHz is stored as f_res
    An oscillation in common mode shows in v_cm with v_dm near zero.

Benches (the source network of the run):
    network   both inputs driven from 50-ohm sources through the input network of chain.INPUT_NET
              (C_P, R_Z + C_Z per input), with Gear integration and abstol = 1e-12 A, as in use
    ties      both inputs tied to ground through 1 milliohm, the global options only (trapezoidal):
              the bench of the first runs, H100_cnode0p ... H100_cnode150p of osc_check.json (gates
              tied through 1 milliohm, with abstol = 1e-15 A, ask ngspice to resolve about 1e-18 V
              at the gate, and with C_node 100 or 150 pF the transient stopped with "timestep too
              small"; the network bench was adopted after that)

The first version of the front ends (the comment above frontend.CASES; `first` mode): no C_node and
    H10   C_I 9.19 pF, C_X 1.42 pF          H100  C_I 6.19 pF, C_X 4.42 pF
    L200  C_I 13.4 pF, C_X 7.8 pF, and L's first current sinks: an MMBT3904 with 2 V across R_T
          (the adopted PZT3904 with 6 V came later, Section 4.2.1 of the note)
    everything else as in frontend.CASES.
Every entry written records ci, cx, cnode (F), the sink, the voltage across R_T and the bench.

Usage: python osc_check.py <case> [cnode_pF ...] [--ties]      a case of frontend.CASES with C_node
                                                                replaced (key <case>_cnode<C>p)
       python osc_check.py first [case ...] [--ties]           the first version (key <case>_first,
                                                                <case>_first_ties)
Writes ../sim/results/osc_check.json (entries merged into the existing file).
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import replace

import numpy as np

import frontend as F
import spice


TRAN_OPTIONS = ".options abstol=1e-12 method=gear\n"
NODES = "v(oa) v(ob) v(ca) v(sa)"
T_SKIP = 0.3e-6
N_FFT = 8192
FIRST = {
    "H10": dict(ci=9.19e-12, cx=1.42e-12, cnode=0.0),
    "H100": dict(ci=6.19e-12, cx=4.42e-12, cnode=0.0),
    "L200": dict(ci=13.4e-12, cx=7.8e-12, cnode=0.0, sink="MMBT3904", v_sink=2.0),
}
BENCHES = {"network": "50 ohm sources and input network (chain.INPUT_NET), Gear, abstol 1e-12",
           "ties": "inputs tied to ground through 1 milliohm, global options only (trapezoidal)"}


def source(p: F.FE, bench: str = "network") -> str:
    """The source part of the deck.  network: both inputs driven from 50-ohm sources through the
    input network of chain.INPUT_NET, as in use.  ties: both gates tied to ground through
    1 milliohm (the first runs' bench)."""
    if bench == "ties":
        return "VA ina 0 DC 0\nRIA ina ga 1m rnl\nRIB ina gb 1m rnl\n"
    import chain
    net = chain.INPUT_NET[p.name[0]]
    return (TRAN_OPTIONS + "VA ina 0 DC 0\nRIA ina ga 50 rnl\nRIB ina gb 50 rnl\n"
            f"CPA ga 0 {net['cp']:g}\nCPB gb 0 {net['cp']:g}\nRZA ga za {net['rz']:g}\nCZA za 0 {net['cz']:g}\n"
            f"RZB gb zb {net['rz']:g}\nCZB zb 0 {net['cz']:g}\n")


def swing(t: np.ndarray, v: np.ndarray) -> dict:
    """pkpk and dominant frequency of v over the window t > T_SKIP (see the module docstring)."""
    m = t > T_SKIP
    tu = np.linspace(t[m][0], t[m][-1], N_FFT)
    vu = np.interp(tu, t[m], v[m])
    vu = vu - vu.mean()
    sp = np.abs(np.fft.rfft(vu * np.hanning(len(vu))))
    fr = np.fft.rfftfreq(len(vu), tu[1] - tu[0])
    k = int(np.argmax(sp[1:]) + 1)
    return dict(pkpk=float(np.ptp(v[m])), f_dom=float(fr[k]))


def run(p: F.FE, bench: str = "network") -> dict:
    """One transient of the front end p on the given bench; the measures of the module docstring.
    On the network bench, a run that Gear integration stops with "timestep too small" is repeated
    with trapezoidal integration in its own folder (osc/<name>_trap), and the entry records it
    ('integration'); a failure of that run too is raised."""
    global TRAN_OPTIONS
    ctl = ".control\n" + spice.WR + f"tran 0.05n 1u 0 0.05n\nwrdata tran.txt {NODES}\n.endc\n"
    integration = None
    try:
        f = spice.run(f"osc/{p.name}", F.deck(p, f"osc {p.name}", source(p, bench), ctl))
    except RuntimeError as e:
        if bench != "network" or "timestep too small" not in str(e).lower():
            raise
        m = re.search(r"time = ([-+0-9.eE]+)", str(e))
        saved, TRAN_OPTIONS = TRAN_OPTIONS, TRAN_OPTIONS.replace("method=gear", "method=trap")
        try:
            f = spice.run(f"osc/{p.name}_trap", F.deck(p, f"osc {p.name}, trapezoidal", source(p, bench), ctl))
        finally:
            TRAN_OPTIONS = saved
        integration = ("trapezoidal: Gear stopped with 'timestep too small'"
                       + (f" at {float(m.group(1)) * 1e9:.0f} ns" if m else ""))
    d = spice.read_table(f / "tran.txt")
    t = d["time"]
    out = {n: swing(t, d[n]) for n in NODES.split()}
    out["cm_out"] = swing(t, (d["v(oa)"] + d["v(ob)"]) / 2)
    out["dm_out"] = swing(t, d["v(oa)"] - d["v(ob)"])
    m = t > T_SKIP
    out["f_res"] = float(1 / (t[m][-1] - t[m][0]))
    if integration:
        out["integration"] = integration
    return out


def record(p: F.FE, bench: str) -> dict:
    """The parameters every entry carries."""
    return dict(ci=p.ci, cx=p.cx, cnode=p.cnode, sink=p.sink, v_sink=p.v_sink, bench=BENCHES[bench])


def main(args):
    sys.stdout.reconfigure(encoding="utf-8")
    bench = "ties" if "--ties" in args else "network"
    args = [a for a in args if a != "--ties"]
    suffix = "_ties" if bench == "ties" else ""
    path = spice.RESULTS / "osc_check.json"
    res = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    if args and args[0] == "first":
        jobs = [replace(F.CASES[c], name=f"{c}_first{suffix}", **FIRST[c]) for c in (args[1:] or list(FIRST))]
    else:
        case = args[0]
        jobs = [replace(F.CASES[case], name=f"{case}_cnode{cn * 1e12:g}p{suffix}", cnode=cn)
                for cn in ([float(x) * 1e-12 for x in args[1:]] or [F.CASES[case].cnode])]
    for p in jobs:
        rec = record(p, bench)
        print(f"{p.name}: C_I {p.ci * 1e12:g} pF, C_X {p.cx * 1e12:g} pF, C_node {p.cnode * 1e12:g} pF, "
              f"sink {p.sink} at {p.v_sink:g} V; {rec['bench']}", flush=True)
        try:
            r = run(p, bench)
            for n in NODES.split() + ["cm_out", "dm_out"]:
                print(f"  {n:7s} {r[n]['pkpk'] * 1e3:10.4f} mV pk-pk, dominant {r[n]['f_dom'] / 1e6:7.2f} MHz",
                      flush=True)
            print(f"  (frequency resolution {r['f_res'] / 1e6:.2f} MHz)", flush=True)
        except RuntimeError as e:
            lines = str(e).splitlines()
            r = dict(failed=(lines[1] if len(lines) > 1 else lines[0])[:160])
            print(p.name, "failed:", r["failed"], flush=True)
        res[p.name] = {**rec, **r}
        path.write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main(sys.argv[1:])
