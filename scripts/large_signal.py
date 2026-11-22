"""Large-signal behaviour and supply rejection of the complete chain (chain.py).

  thd       harmonic distortion of the output for a differential sine at 1 kHz, 100 kHz, 1 MHz and
            10 MHz, at 1 Vpp and 10 Vpp output (10 MHz at 1 Vpp only), H at gain 100 and L at gain
            1000: differential input amplitude a = V_pp / (2 G); 3 periods to settle, then the last
            N_p = 4 periods resampled linearly onto 1024 points per period (t_n = 3/f0 + n/(1024 f0))
            and transformed (no window needed, an integer number of periods):
                c_k = (2/N) |sum_n v(t_n) exp(-2 pi j k n / N)|,  N = 4096,  fundamental c_4,
                H_m = c_{4m} / c_4,  THD = sqrt(sum_{m=2..9} H_m^2)
            transient: tran T/400 7T 0 T/400 (T = 1/f0)
  step      output step of 1 V and 10 V (10-90 % rise time, overshoot = max(v - v0)/(v1 - v0) - 1,
            settling to 1 % and 0.1 %: the last time |v - v1| > 1 % (0.1 %) of (v1 - v0) after the
            input step at 1 us; v0 the mean over 0.8-0.99 us, v1 over 3.5-4 us), slew rate
                SR = max |v_{i+1} - v_i| / (t_{i+1} - t_i)  over the intervals with t_{i+1} > t_i
            (wrdata prints the time with numdgt = 7, i.e. 7 decimals of the mantissa or 8 significant
            digits, so two internal time points closer than that, 1e-13 s at a few microseconds,
            are written as the same time; such intervals are skipped, they gave the 'slew nan' of
            the first L step run)
  overload  an input step three times larger than full scale (30 V at the output) held for 20 us,
            then removed: the time for the output to return within 1 % of full scale (0.1 V) of its
            final value (with Gear integration; at ten times the trapezoidal run of H100 stopped with
            "timestep too small" in one input JFET)
  psrr      the output's response to 1 V AC on the +15 V and on the -15 V rail, referred to the
            input: 20 log10(|v_out| / G) (dB below 1 V per volt of ripple) - the circuit alone, with
            ideal references
Every transient tries, in order, Gear with abstol 1e-12 A, trapezoidal with abstol 1e-12 A, Gear
with itl4 = 1000 and reltol 2e-4, and last Gear with the inputs driven from 50 ohm (the bench of
osc_check.py); the one that ran is printed, and a step entry records bench = "50 ohm sources and
input network" when only the last one ran.
Writes ../sim/results/large_signal.json.
Usage: python large_signal.py [H100 L1000] [thd step overload psrr] [options]

Options:
  --da <part>      the difference amplifier S2 of this run (default chain.DA_OPAMP, the LM7171);
                   its resistors stay at 499 ohm (the THS3091's 1 k are set by da_compare.py)
  --l-sink first   L200 with its first design's current sinks, an MMBT3904 with 2 V across R_T, as in
                   the two reproductions below and in every L run of this script made before the
                   switch to the PZT3904 with 6 V of Section 4.2.1; the default is frontend.CASES
                   (the 6 V sinks), with which large_signal.json's L entries were re-run on
                   22 November 2026
  --out <file>     results file in ../sim/results/ instead of large_signal.json

Reproductions of two archived results files that no earlier code path wrote (each rerun into
../sim/runs/large/repro_<name>/; the file is written under its archived name only if the rerun's
results equal the archive exactly, else as <name>_regen.json, and every difference is printed):
  python large_signal.py repro L1000_step   large_signal_L1000_step.json: the L 1 V and 10 V steps at a
        gain of 1000, LM7171 in S2, the first design's sinks; before the model recalibration of
        22 November 2026 the 1 V step failed on every bench and the 10 V step ran only on the 50-ohm
        bench (large_signal_log_L1000_step.txt); in the re-run with the recalibrated models both ran
        on the 50-ohm bench (large_signal_repro_L1000_step_log.txt), and that result is the archive
  python large_signal.py repro THS4031      large_signal_THS4031.json: H at a gain of 100 (thd, step,
        overload, psrr) and L at 1000 (thd) with the THS4031 in S2, the S2 of chain.py before
        da_compare.py chose the LM7171, and the first design's sinks (large_signal_log_L1000.txt,
        large_signal_log_H100psrr.txt)

The numerical floor of the THD measurement (Section 6.5 of the note):
  python large_signal.py floor   writes ../sim/results/large_signal_floor.json with
    linear_reference   the THD measurement above, with the same tran command, global options and
                       each of the first three option sets, on a purely linear reference: the same
                       sine sources (a = V_pp / (2 G)) into an ideal amplifier of the chain's gain G
                       (E source) and one RC low-pass at the chain's -3 dB frequency f_c
                       (chain_ac.json: H_LN_100 for H, L_1000 for L), R = 1 k, C = 1 / (2 pi R f_c);
                       any harmonic it shows is numerical (integration, time-step changes, the
                       printed precision of wrdata, the resampling)
    grid_interpolation the resampling alone on the time grids of the archived chain THD runs
                       (../sim/runs/large/<case>_thd_<f0>_<Vpp>/tran.txt, LM7171 in S2): the run's own
                       fundamental, v(t) = A cos(2 pi f0 (t - t0) + phi) from c_4, evaluated on the
                       run's time points (i) exactly and (ii) as wrdata prints it (numdgt = 7: value
                       to 8 significant digits, the true time within half a printed step of the
                       printed one, seed 1), then measured as above
    L1000_10MHz_1Vpp   the chain's THD at L, gain 1000, 10 MHz, 1 Vpp with each S2 (THS4031, LM7171)
                       and each L sink (first design 2 V, adopted 6 V): the two values archived
                       before the model recalibration, 0.0396 % (large_signal_log_L1000.txt) and
                       0.0078 % (large_signal.json of 19 November 2026), differ by the S2 of the run
    chain_settings     what a linear reference cannot show, the nonlinear solution's own accuracy: the
                       chain (H, gain 100, the default S2) at the three lowest-distortion points
                       (1 kHz, 100 kHz and 1 MHz at 1 Vpp) with each option set alone, no fallback:
                       Gear (the first try), trapezoidal, Gear with reltol 2e-5 (the Newton and
                       truncation-error tolerances five times tighter), Gear with reltol 1e-5 and
                       abstol 1e-11 A (ten times tighter; with abstol 1e-12 A it stopped with "timestep
                       too small" at the start), and Gear with tmax = T/1600
  python large_signal.py floor [linear grid s2 settings]      (none: all four)
"""
from __future__ import annotations

import contextlib
import json
import math
import sys
from dataclasses import replace

import numpy as np

import blocks
import chain
import frontend as F
import models
import spice

CASES = {"H100": ("H_LN", 100), "L1000": ("L", 1000)}
# Transients: Gear integration and abstol 1e-12 A, and the inputs driven through 1 ohm (not the
# 1 milliohm of the AC benches): with abstol = 1e-15 A a milliohm asks ngspice to resolve about
# 1e-18 V, and transients stopped with "timestep too small" at the gate nodes.
TRAN_OPTIONS = ".options abstol=1e-12 method=gear\n"
TRIES = [TRAN_OPTIONS, ".options abstol=1e-12\n", ".options abstol=1e-12 method=gear itl4=1000 reltol=2e-4\n",
         "50ohm"]
BENCH_50 = "50 ohm sources and input network"
THD_POINTS = ((1e3, 1), (1e3, 10), (1e5, 1), (1e5, 10), (1e6, 1), (1e6, 10), (1e7, 1))
LAST_TRY: dict[str, str] = {}          # tag -> the option set that ran (TRIES), for the records


def tran(s: chain.Setting, tag: str, src: str, tstop: float, tstep: float, save="v(out) v(oa) v(ob)") -> dict:
    ctl = (".control\n" + spice.WR + f"tran {tstep:g} {tstop:g} 0 {tstep:g}\n"
           f"wrdata tran.txt {save}\n.endc\n")
    # a few decks stopped with "timestep too small" at the very start (tens of ns) with one set of
    # options and ran with another; the options that ran are recorded in the run log
    for k, opt in enumerate(TRIES):
        try:
            if opt == "50ohm":
                # last resort: the inputs driven from 50 ohm (the chain's netlist already contains
                # the input network), the bench on which osc_check.py ran every front end cleanly
                src2 = src.replace(" 1 rnl", " 50 rnl")
                f = spice.run(f"large/{tag}", chain.deck(s, f"large {tag}", TRAN_OPTIONS + src2, ctl))
            else:
                f = spice.run(f"large/{tag}", chain.deck(s, f"large {tag}", opt + src, ctl))
            if k:
                print(f"  ({tag}: ran with '{opt.strip()}')", flush=True)
            LAST_TRY[tag] = opt.strip()
            return spice.read_table(f / "tran.txt")
        except RuntimeError:
            if k == len(TRIES) - 1:
                raise


def thd_measure(t: np.ndarray, v: np.ndarray, f0: float, nper_settle: int = 3, nper: int = 4) -> dict:
    """The THD measurement of the module docstring on a transient v(t)."""
    t0 = nper_settle / f0
    tt = t0 + np.arange(nper * 1024) / (1024 * f0)
    vv = np.interp(tt, t, v)
    spec = np.abs(np.fft.rfft(vv)) / len(vv) * 2
    h1 = spec[nper]
    harm = [spec[nper * k] for k in range(2, 10)]
    thd = math.sqrt(sum(h ** 2 for h in harm)) / h1
    return dict(fund_pp=2 * h1, thd=thd, h2=harm[0] / h1, h3=harm[1] / h1)


def thd_source(s_gain: float, f0: float, vout_pp: float, r_src: str = "1") -> str:
    amp = vout_pp / 2 / s_gain                      # differential input amplitude
    return (f"VA ina 0 DC 0 SIN(0 {amp / 2:g} {f0:g})\nVB inb 0 DC 0 SIN(0 {-amp / 2:g} {f0:g})\n"
            f"RIA ina ga {r_src} rnl\nRIB inb gb {r_src} rnl\n")


def thd_run(s: chain.Setting, tag: str, f0: float, vout_pp: float) -> dict:
    nper_settle, nper = 3, 4
    tstop = (nper_settle + nper) / f0
    tstep = 1 / f0 / 400
    d = tran(s, tag, thd_source(s.gain, f0, vout_pp), tstop, tstep, "v(out)")
    return dict(f0=f0, vout_pp=vout_pp, **thd_measure(d["time"], d["v(out)"], f0, nper_settle, nper))


def slew(t: np.ndarray, v: np.ndarray) -> float:
    """Largest |dv/dt| in V/us over the intervals with t_{i+1} > t_i (module docstring)."""
    dt, dv = np.diff(t), np.diff(v)
    ok = dt > 0
    return float(np.max(np.abs(dv[ok] / dt[ok])) / 1e6)


def step_metrics(t: np.ndarray, v: np.ndarray, t_step: float = 1e-6) -> dict:
    """Step measures of the module docstring (the input steps at t_step)."""
    v0 = float(np.mean(v[(t > 0.8e-6) & (t < 0.99e-6)]))
    v1 = float(np.mean(v[(t > 3.5e-6) & (t < 4e-6)]))
    dv = v1 - v0
    m = t > t_step
    tm, vm = t[m], (v[m] - v0) / dv
    t10 = tm[np.argmax(vm >= 0.1)]
    t90 = tm[np.argmax(vm >= 0.9)]
    over = float(vm.max() - 1)
    out_band = np.where(np.abs(vm - 1) > 1e-3)[0]
    ts = float(tm[out_band[-1]] - t_step) if len(out_band) else 0.0
    out_band1 = np.where(np.abs(vm - 1) > 1e-2)[0]
    ts1 = float(tm[out_band1[-1]] - t_step) if len(out_band1) else 0.0
    return dict(dv=dv, rise_ns=(t90 - t10) * 1e9, overshoot=over, settle_ns_0p1=ts * 1e9,
                settle_ns_1=ts1 * 1e9, slew_v_us=slew(t, v))


def step_source(s_gain: float, vstep: float) -> str:
    amp = vstep / s_gain
    return (f"VA ina 0 DC {-amp / 4:g} PULSE({-amp / 4:g} {amp / 4:g} 1u 1n 1n 5u 20u)\n"
            f"VB inb 0 DC {amp / 4:g} PULSE({amp / 4:g} {-amp / 4:g} 1u 1n 1n 5u 20u)\n"
            "RIA ina ga 1 rnl\nRIB inb gb 1 rnl\n")


def step_run(s: chain.Setting, tag: str, vstep: float) -> dict:
    d = tran(s, tag, step_source(s.gain, vstep), 4e-6, 0.2e-9, "v(out)")
    res = dict(vstep=vstep, **step_metrics(d["time"], d["v(out)"]))
    if LAST_TRY.get(tag) == "50ohm":
        res["bench"] = BENCH_50
    return res


def overload_run(s: chain.Setting, tag: str) -> dict:
    full = 10.0 / s.gain                            # input for 10 V at the output
    amp = 3 * full
    src = (".options method=gear\n"
           f"VA ina 0 DC 0 PULSE(0 {amp / 2:g} 2u 10n 10n 20u 100u)\n"
           f"VB inb 0 DC 0 PULSE(0 {-amp / 2:g} 2u 10n 10n 20u 100u)\n"
           "RIA ina ga 1 rnl\nRIB inb gb 1 rnl\n")
    d = tran(s, tag, src, 40e-6, 2e-9, "v(out) v(oa) v(ob) v(da)")
    t, v = d["time"], d["v(out)"]
    vfin = float(np.mean(v[(t > 38e-6)]))
    after = t > 22.01e-6
    bad = np.where(np.abs(v[after] - vfin) > 0.1)[0]          # 1 % of 10 V
    trec = float(t[after][bad[-1]] - 22.01e-6) if len(bad) else 0.0
    return dict(input_overdrive=3, recovery_us=trec * 1e6, v_during=float(np.mean(v[(t > 15e-6) & (t < 20e-6)])),
                fe_out_during=float(np.mean((d["v(oa)"] - d["v(ob)"])[(t > 15e-6) & (t < 20e-6)])))


def psrr_run(s: chain.Setting, tag: str) -> dict:
    out = {}
    for rail in ("VP", "VM"):
        ctl = ".control\n" + spice.WR + "ac dec 10 10 30meg\nwrdata ac.txt v(out)\n.endc\n"
        text = chain.deck(s, f"psrr {tag} {rail}", "VA ina 0 DC 0\nRIA ina ga 1m rnl\nRIB ina gb 1m rnl\n", ctl)
        val = "15" if rail == "VP" else "-15"
        text = text.replace(f"{rail} {rail.lower()} 0 DC {val}\n", f"{rail} {rail.lower()} 0 DC {val} AC 1\n")
        f = spice.run(f"large/{tag}_psrr_{rail}", text)
        d = spice.read_table(f / "ac.txt")
        fr, h = d["frequency"], np.abs(d["v(out)"]) / s.gain
        out[rail] = {str(f0): float(20 * np.log10(spice.at(fr, h, f0))) for f0 in (100, 1e3, 1e4, 1e5, 1e6, 1e7)}
    return out


@contextlib.contextmanager
def settings(da: str | None = None, l_sink: str | None = None):
    """The S2 part (chain.DA_OPAMP) and L200's sinks for the runs inside; restored afterwards."""
    old_da, old_l = chain.DA_OPAMP, F.CASES["L200"]
    try:
        if da:
            chain.DA_OPAMP = da
        if l_sink == "first":
            F.CASES["L200"] = replace(old_l, sink="MMBT3904", v_sink=2.0)
        elif l_sink not in (None, "adopted"):
            raise ValueError(f"unknown L sink {l_sink}")
        yield
    finally:
        chain.DA_OPAMP, F.CASES["L200"] = old_da, old_l


def run_suite(names, what, res: dict, prefix: str = "", save=None) -> dict:
    """The parts `what` for each case of `names`, into res[name]; run folders large/<prefix><tag>."""
    for name in names:
        mode, g = CASES[name]
        s = chain.allocate(g, mode)
        r = res.setdefault(name, {})
        if "thd" in what:
            rows = []
            for f0, vpp in THD_POINTS:
                x = thd_run(s, f"{prefix}{name}_thd_{f0:g}_{vpp:g}", f0, vpp)
                rows.append(x)
                print(f"{name} THD {f0:>8g} Hz {vpp:>3g} Vpp: {x['thd'] * 100:.4f} %  (H2 {20 * math.log10(x['h2'] + 1e-20):.0f} dBc, "
                      f"H3 {20 * math.log10(x['h3'] + 1e-20):.0f} dBc, fundamental {x['fund_pp']:.3f} Vpp)", flush=True)
            r["thd"] = rows
            save and save()
        if "step" in what:
            r["step"] = []
            for v in (1.0, 10.0):
                try:
                    x = step_run(s, f"{prefix}{name}_step_{v:g}", v)
                except RuntimeError as e:
                    r["step"].append(dict(vstep=v, failed=str(e).splitlines()[1][:160]))
                    print(f"{name} step {v:g} V failed: {r['step'][-1]['failed']}", flush=True)
                    continue
                r["step"].append(x)
                print(f"{name} step {x['vstep']:g} V: rise {x['rise_ns']:.1f} ns, overshoot {x['overshoot'] * 100:.1f} %, "
                      f"settle 1 % {x['settle_ns_1']:.0f} ns, 0.1 % {x['settle_ns_0p1']:.0f} ns, "
                      f"slew {x['slew_v_us']:.0f} V/us", flush=True)
            save and save()
        if "overload" in what:
            try:
                r["overload"] = overload_run(s, f"{prefix}{name}_overload")
                print(f"{name} overload x3: recovery {r['overload']['recovery_us']:.2f} us, "
                      f"output during {r['overload']['v_during']:.2f} V", flush=True)
            except RuntimeError as e:
                r["overload"] = dict(failed=str(e).splitlines()[1][:160])
                print(f"{name} overload x3 failed: {r['overload']['failed']}", flush=True)
            save and save()
        if "psrr" in what:
            r["psrr"] = psrr_run(s, f"{prefix}{name}")
            print(f"{name} PSRR (input-referred, dB): {r['psrr']}", flush=True)
            save and save()
    return res


# ---------------------------------------------------------------------------------------------
# reproductions of archived files
# ---------------------------------------------------------------------------------------------
REPRO = {
    "L1000_step": dict(file="large_signal_L1000_step.json", da="LM7171", l_sink="first"),
    "THS4031": dict(file="large_signal_THS4031.json", da="THS4031", l_sink="first"),
}


def differences(a, b, path="") -> list[tuple[str, object, object]]:
    """Every leaf where the archived a and the rerun b differ (structure or value)."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in list(a) + [k for k in b if k not in a]:
            if k not in a or k not in b:
                out.append((f"{path}/{k}", a.get(k, "<missing>"), b.get(k, "<missing>")))
            else:
                out += differences(a[k], b[k], f"{path}/{k}")
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [(path, f"list of {len(a)}", f"list of {len(b)}")]
        return [d for i, (x, y) in enumerate(zip(a, b)) for d in differences(x, y, f"{path}[{i}]")]
    return [] if a == b else [(path, a, b)]


def repro(which: str) -> None:
    cfg = REPRO[which]
    prefix = f"repro_{which}/"
    with settings(cfg["da"], cfg["l_sink"]):
        print(f"repro {which}: S2 {chain.DA_OPAMP}, L sinks {F.CASES['L200'].sink} at {F.CASES['L200'].v_sink:g} V",
              flush=True)
        if which == "L1000_step":
            s = chain.allocate(1000, "L")
            out = []
            for v in (1.0, 10.0):
                try:
                    x = step_run(s, f"{prefix}L1000_step_{v:g}", v)
                    out.append(x)
                    print(f"L1000 step {v:g} V: rise {x['rise_ns']:.1f} ns, overshoot {x['overshoot'] * 100:.2f} %, "
                          f"settle 1 % {x['settle_ns_1']:.0f} ns, 0.1 % {x['settle_ns_0p1']:.0f} ns, "
                          f"slew {x['slew_v_us']:.1f} V/us" + (f" ({x['bench']})" if "bench" in x else ""), flush=True)
                except RuntimeError as e:
                    out.append(dict(vstep=v, failed=str(e).splitlines()[1][:160]))
                    print(f"L1000 step {v:g} V failed: {out[-1]['failed']}", flush=True)
        else:
            out = {}
            run_suite(["H100"], ["thd", "step", "overload", "psrr"], out, prefix)
            run_suite(["L1000"], ["thd"], out, prefix)
    arch_path = spice.RESULTS / cfg["file"]
    archive = json.loads(arch_path.read_text(encoding="utf-8"))
    diffs = differences(archive, out)
    if not diffs:
        arch_path.write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
        print(f"{cfg['file']}: the rerun equals the archive in every value; written under its own name")
        return
    regen = arch_path.with_name(arch_path.stem + "_regen.json")
    regen.write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    print(f"{cfg['file']}: {len(diffs)} values differ from the archive; the rerun is in {regen.name}")
    for p, a, b in diffs:
        rel = ""
        if isinstance(a, float) and isinstance(b, float) and a:
            rel = f"  (relative {b / a - 1:+.2e})"
        print(f"  {p}: archive {a!r}, rerun {b!r}{rel}")


# ---------------------------------------------------------------------------------------------
# the floor of the THD measurement
# ---------------------------------------------------------------------------------------------
FLOOR_OPTIONS = {"gear": TRIES[0], "trap": TRIES[1], "gear_itl4_reltol2e-4": TRIES[2]}


def linear_reference(case: str, f0: float, vpp: float, optname: str, gain: float, fc: float) -> dict:
    """The THD measurement on the linear reference of the module docstring (one option set)."""
    c = 1 / (2 * math.pi * 1e3 * fc)
    tstep, tstop = 1 / f0 / 400, 7 / f0
    tag = f"floor/{case}_{f0:g}_{vpp:g}_{optname}"
    deck = (f"* thd floor {tag}\n{spice.OPTIONS}.options rshunt=1e12\n{blocks.COMMON}{FLOOR_OPTIONS[optname]}"
            + thd_source(gain, f0, vpp) +
            f"EG x 0 ga gb {gain:.9g}\nRF x out 1k\nCF out 0 {c:.6g}\n.control\n" + spice.WR +
            f"tran {tstep:g} {tstop:g} 0 {tstep:g}\nwrdata tran.txt v(out)\n.endc\n.end\n")
    f = spice.run(f"large/{tag}", deck)
    d = spice.read_table(f / "tran.txt")
    t, v = d["time"], d["v(out)"]
    m = t >= 3 / f0
    dt = np.diff(t[m])
    return dict(f0=f0, vout_pp=vpp, options=optname, **thd_measure(t, v, f0),
                points=int(m.sum()), dt_min_over_tmax=float(dt.min() / tstep), dt_max_over_tmax=float(dt.max() / tstep),
                share_at_tmax=float(np.mean(np.abs(dt / tstep - 1) < 0.01)))


def _round_sig(x: np.ndarray, digits: int = 8) -> np.ndarray:
    """x rounded to `digits` significant digits (wrdata with numdgt = 7 prints 8: d.ddddddde-xx)."""
    e = np.floor(np.log10(np.where(x == 0, 1.0, np.abs(x))))
    q = 10.0 ** (e - (digits - 1))
    return np.round(x / q) * q


def grid_interpolation(case: str, f0: float, vpp: float) -> dict | None:
    """The resampling alone, on an archived chain run's time grid (module docstring)."""
    folder = spice.RUNS / "large" / f"{case}_thd_{f0:g}_{vpp:g}"
    if not (folder / "tran.txt").exists():
        return None
    d = spice.read_table(folder / "tran.txt")
    t, v = d["time"], d["v(out)"]
    t0 = 3 / f0
    tt = t0 + np.arange(4 * 1024) / (1024 * f0)
    c1 = np.fft.rfft(np.interp(tt, t, v))[4] * 2 / len(tt)
    amp, phi = abs(c1), float(np.angle(c1))
    exact = amp * np.cos(2 * np.pi * f0 * (t - t0) + phi)
    rng = np.random.default_rng(1)
    q_t = 10.0 ** (np.floor(np.log10(np.where(t > 0, t, 1.0))) - 7)      # the printed time step
    t_true = t + (rng.random(len(t)) - 0.5) * q_t * (t > 0)
    printed = _round_sig(amp * np.cos(2 * np.pi * f0 * (t_true - t0) + phi))
    m = t >= t0
    dt = np.diff(t[m])
    return dict(f0=f0, vout_pp=vpp, run=folder.name, points=int(m.sum()),
                dt_min_over_tmax=float(dt.min() * f0 * 400), dt_max_over_tmax=float(dt.max() * f0 * 400),
                exact=thd_measure(t, exact, f0), printed=thd_measure(t, printed, f0),
                chain=thd_measure(t, v, f0))


SETTINGS_VARIANTS = {"gear": (TRIES[0], 400), "trap": (TRIES[1], 400),
                     "gear_reltol2e-5": (".options abstol=1e-12 method=gear reltol=2e-5\n", 400),
                     "gear_reltol1e-5_abstol1e-11": (".options abstol=1e-11 method=gear reltol=1e-5\n", 400),
                     "gear_tmax_T_1600": (TRIES[0], 1600)}
SETTINGS_POINTS = ((1e3, 1), (1e5, 1), (1e6, 1))


def thd_run_fixed(s: chain.Setting, tag: str, f0: float, vout_pp: float, opt: str, per_period: int) -> dict:
    """thd_run with one option set and tmax = T / per_period, no fallback."""
    tstep = 1 / f0 / per_period
    ctl = (".control\n" + spice.WR + f"tran {tstep:g} {7 / f0:g} 0 {tstep:g}\nwrdata tran.txt v(out)\n.endc\n")
    f = spice.run(f"large/{tag}", chain.deck(s, f"large {tag}", opt + thd_source(s.gain, f0, vout_pp), ctl))
    d = spice.read_table(f / "tran.txt")
    return dict(f0=f0, vout_pp=vout_pp, **thd_measure(d["time"], d["v(out)"], f0))


def _db(x: float) -> float:
    return 20 * math.log10(max(x, 1e-30))


def floor_linear() -> dict:
    ac = json.loads((spice.RESULTS / "chain_ac.json").read_text(encoding="utf-8"))
    fcs = {"H100": ac["H_LN_100"]["f3db"], "L1000": ac["L_1000"]["f3db"]}
    out = {}
    for case, (mode, g) in CASES.items():
        s = chain.allocate(g, mode)
        rows = []
        for f0, vpp in THD_POINTS:
            for optname in FLOOR_OPTIONS:
                x = linear_reference(case, f0, vpp, optname, s.gain, fcs[case])
                rows.append(x)
                print(f"linear reference {case} {f0:>8g} Hz {vpp:>3g} Vpp {optname:22s}: THD {x['thd'] * 100:.2e} % "
                      f"({_db(x['thd']):.0f} dBc; H2 {_db(x['h2']):.0f}, H3 {_db(x['h3']):.0f} dBc), "
                      f"steps {x['dt_min_over_tmax']:.2f}-{x['dt_max_over_tmax']:.2f} x tmax", flush=True)
        out[case] = dict(gain=s.gain, f_c=fcs[case], rows=rows)
    return out


def floor_grid() -> dict:
    out = {}
    for case in CASES:
        rows = []
        for f0, vpp in THD_POINTS:
            x = grid_interpolation(case, f0, vpp)
            if x is None:
                continue
            rows.append(x)
            print(f"grid {x['run']:22s}: steps {x['dt_min_over_tmax']:.3f}-{x['dt_max_over_tmax']:.2f} x tmax; THD "
                  f"exact {_db(x['exact']['thd']):.0f} dBc, as printed {_db(x['printed']['thd']):.0f} dBc, "
                  f"chain {_db(x['chain']['thd']):.0f} dBc", flush=True)
        out[case] = rows
    return out


def floor_s2() -> list:
    rows = []
    for da in ("THS4031", "LM7171"):
        for sink in ("first", "adopted"):
            with settings(da, sink):
                s = chain.allocate(1000, "L")
                tag = f"floor/L1000_thd_1e+07_1_{da}_{sink}"
                x = thd_run(s, tag, 1e7, 1.0)
                x.update(S2=da, l_sink=f"{F.CASES['L200'].sink}, {F.CASES['L200'].v_sink:g} V across R_T",
                         options=LAST_TRY[tag])
            rows.append(x)
            print(f"L1000 10 MHz 1 Vpp, S2 {da}, sinks {x['l_sink']}: THD {x['thd'] * 100:.4f} % (H2 {_db(x['h2']):.0f}, "
                  f"H3 {_db(x['h3']):.0f} dBc, fundamental {x['fund_pp']:.3f} Vpp; options '{x['options']}')", flush=True)
    return rows


def floor_settings() -> list:
    s = chain.allocate(100, "H_LN")
    rows = []
    for f0, vpp in SETTINGS_POINTS:
        for name, (opt, per) in SETTINGS_VARIANTS.items():
            tag = f"floor/H100_thd_{f0:g}_{vpp:g}_{name}"
            try:
                x = dict(settings=name, **thd_run_fixed(s, tag, f0, vpp, opt, per))
                print(f"chain H100 {f0:>8g} Hz {vpp:g} Vpp {name:18s}: THD {x['thd'] * 100:.2e} % ({_db(x['thd']):.1f} dBc; "
                      f"H2 {_db(x['h2']):.1f}, H3 {_db(x['h3']):.1f} dBc)", flush=True)
            except RuntimeError as e:
                x = dict(settings=name, f0=f0, vout_pp=vpp, failed=str(e).splitlines()[1][:160])
                print(f"chain H100 {f0:>8g} Hz {vpp:g} Vpp {name:18s}: failed: {x['failed']}", flush=True)
            rows.append(x)
    return rows


FLOOR_PARTS = {"linear": ("linear_reference", floor_linear), "grid": ("grid_interpolation", floor_grid),
               "s2": ("L1000_10MHz_1Vpp", floor_s2), "settings": ("chain_settings", floor_settings)}


def floor(parts=None) -> None:
    """The parts of the floor test (module docstring) into large_signal_floor.json."""
    path = spice.RESULTS / "large_signal_floor.json"
    res = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    for part in parts or list(FLOOR_PARTS):
        key, fn = FLOOR_PARTS[part]
        res[key] = fn()
        path.write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")


def main(args):
    sys.stdout.reconfigure(encoding="utf-8")
    da = l_sink = None
    out_name = "large_signal.json"
    rest = []
    it = iter(args)
    for a in it:
        if a == "--da":
            da = next(it)
        elif a == "--l-sink":
            l_sink = next(it)
        elif a == "--out":
            out_name = next(it)
        else:
            rest.append(a)
    models.prepare()
    if rest and rest[0] == "repro":
        for which in rest[1:] or list(REPRO):
            repro(which)
        return
    if rest and rest[0] == "floor":
        floor(rest[1:])
        return
    # arguments: any of the parts (thd step overload psrr) and any of the cases (H100 L1000);
    # none given means all
    what = [a for a in rest if a not in CASES] or ["thd", "step", "overload", "psrr"]
    names = [a for a in rest if a in CASES] or list(CASES)
    path = spice.RESULTS / out_name
    res = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    def save():
        path.write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    with settings(da, l_sink):
        run_suite(names, what, res, save=save)
    save()


if __name__ == "__main__":
    main(sys.argv[1:])
