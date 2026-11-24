"""Overload and recovery in detail (Section 6.5 of the note): a differential input step of three
times full scale (30 V at the output) held for 20 us, then removed, with the inputs driven from
50-ohm sources through the input network.  Saves the output and the front end's internal nodes
(outputs oa/ob, source nodes sa/sb, summing nodes ca/cb)
so that the note can say which stage saturates, what the front end does meanwhile, and how each
node recovers.  Recovery: the last time after the input returns at which the output is more than
1 % of full scale (0.1 V) away from its final value.  With ngspice's default solver (Sparse 1.3) H at
a gain of 100 with the LM7171 in S2 did not converge on any bench; with the KLU solver (ATTEMPTS) it
does, and so does L.

Writes the overload entries of ../sim/results/large_signal.json and ../sim/results/overload_curves.npz.
Without the servo both H and L stop with Gear and the default solver at the onset of the overload, and
run with the second attempt (KLU, abstol 1e-11 A).  `--h-ths4031` runs the H case with the THS4031 in S2
and 1-ohm sources, the comparison kept from when the LM7171 version did not converge.
Usage: python overload_detail.py [H100] [L1000]      or      python overload_detail.py --h-ths4031

`numbers` (no simulation): every number of Section 6.5 on the overloads, from the archived curves
  H: the H100_* curves of overload_curves.npz (LM7171 in S2, 50-ohm sources, this script's run), and for
     comparison overload_curves_H100_THS4031.npz (THS4031 in S2, 1-ohm sources; key H100_THS4031);
  L: the L1000_* curves of overload_curves.npz (LM7171 in S2, 50-ohm sources).  overload_curves.npz
     holds only the cases whose run converged in the last call (in the re-run of 22 November 2026, L
     only; in the re-run without the servo of 23 November 2026, both).
  The input: a differential step of 3 x full scale, v_in = 3 * 10 V / G (G the chain's gain), i.e.
  +/- v_in / 2 at the two gates (the gate follows its source; 50 ohm into the input network), from t_on = 2 us
  (10 ns edge) to t_off = 22.01 us (10 ns edge).  Windows: rest t < 1.9 us, during 15-20 us,
  final t > 38 us; x_rest, x_during, x_final are the means of a node over them.
    recovery            t_rec = last t > t_off with |v_out - v_out,final| > 0.1 V (1 % of 10 V), - t_off;
                        for the front end's nodes the same with 10 mV and 12 mV about x_rest
    output ramp         excursion E = v_out,during - v_out,final; t_X the first time after t_off at
                        which v_out - v_out,final <= X E (X = 0.99, 0.9, 0.1): delay t_0.99 - t_off,
                        10-90 % slope 0.8 E / (t_0.1 - t_0.9), peak slope max |dv/dt| between
                        t_off and t_off + t_rec (intervals with t_{i+1} > t_i), and the same over 5 ns:
                        max |v(t + 5 ns) - v(t)| / 5 ns (v resampled every 0.5 ns)
    undershoot (L)      depth min(v_out - v_out,final) after t_off, its time, and the interval in which
                        v_out - v_out,final < -0.1 V
    op-amp outputs      clip levels v_oa,during, v_ob,during and v_oa - v_ob; after the release
                        min v_oa and max v_ob (absolute and minus x_rest) and their times; over the
                        whole run max v_oa and min v_ob
    source nodes        dv_s = v_s,during - v_s,rest against the gate's step +/- v_in / 2:
                        dV_GS = dv_g - dv_s per side; V_GS,rest = v_g - v_s = -v_s,rest (gates at 0 V)
    JFET current        from the summing node: dI = -(v_c,during - v_c,rest) / R_D (R_D carries the
                        JFETs' current once the op amp's integrator is clipped); small-signal
                        estimate dI = g_m dV_GS with g_m of one side (fe_gain_derived.json)
    servo               the front ends have none (a fixed, adjusted reference); what a servo of the sinks'
                        reference (Appendix B of the note: G_INT 1 uS into C_INT 1 uF) would do: the
                        error it would see, e = (v_oa + v_ob - v_sa - v_sb) / 2 during the overload; its
                        rate G_INT e / C_INT and its change over the run, the integral of G_INT e / C_INT dt;
                        after an overload of 1 s the sinks' reference would move by G_INT e (1 s) / C_INT and
                        the outputs' common mode by (R_F / R_T) that, and the servo loop's time constant
                        would be tau = (C_INT / G_INT) (R_T / R_F)
    bootstrap           tau_BS = R_BS C_BS
    larger overloads    with the op amps clipped, the source nodes follow the divider R_F - R_G - R_F:
                        v_s,d = (v_oa - v_ob) R_G / (2 R_F + R_G), so dV_GS ~ (v_in - v_s,d) / 2 per side
                        (the JFETs' own current change neglected); the overdrive at which dV_GS reaches
                        |V_GS,rest| (zero gate bias): v_in = 2 |V_GS,rest| + v_s,d
  Writes ../sim/results/overload_numbers.json.   Usage: python overload_detail.py numbers
"""
from __future__ import annotations

import json
import sys

import numpy as np

import chain
import large_signal as L
import models
import spice

NODES = "v(out) v(oa) v(ob) v(da) v(sa) v(sb) v(ca) v(cb)"


# attempts, in order: (options, input edge time, largest time step); each runs in a child process
# with a time limit, since a transient that struggles can take hours in the shared library.  The
# second and third (the KLU solver, abstol 1e-11 A) are large_signal.TRIES' sets for the decks that
# stop within their first steps without the servo.
ATTEMPTS = [(".options abstol=1e-12 method=gear\n", "10n", "2n"),
            (".options abstol=1e-11 method=gear klu\n", "10n", "2n"),
            (".options abstol=1e-11 method=gear\n", "10n", "2n"),
            (".options abstol=1e-12 method=gear reltol=1e-3\n", "10n", "2n"),
            (".options abstol=1e-12 reltol=1e-3\n", "10n", "1n"),
            (".options abstol=1e-12 method=gear\n", "100n", "2n"),
            (".options abstol=1e-12 method=gear reltol=1e-3\n", "100n", "1n")]


def run(name: str, k: int = 0) -> dict:
    mode, g = L.CASES[name]
    s = chain.allocate(g, mode)
    amp = 3 * 10.0 / s.gain
    opt, edge, tmax = ATTEMPTS[k]
    src = (opt + f"VA ina 0 DC 0 PULSE(0 {amp / 2:g} 2u {edge} {edge} 20u 100u)\n"
           f"VB inb 0 DC 0 PULSE(0 {-amp / 2:g} 2u {edge} {edge} 20u 100u)\n"
           "RIA ina ga 50 rnl\nRIB inb gb 50 rnl\n")
    ctl = ".control\n" + spice.WR + f"tran {tmax} 40u 0 {tmax}\nwrdata tran.txt {NODES}\n.endc\n"
    f = spice.check_dc(spice.run(f"large/{name}_overload_detail", chain.deck(s, f"overload {name}", src, ctl)))
    d = spice.read_table(f / "tran.txt")
    t, v = d["time"], d["v(out)"]
    vfin = float(np.mean(v[t > 38e-6]))
    t_off = 22.01e-6
    after = t > t_off
    bad = np.where(np.abs(v[after] - vfin) > 0.1)[0]
    trec = float(t[after][bad[-1]] - t_off) if len(bad) else 0.0
    mid = (t > 15e-6) & (t < 20e-6)
    res = dict(input_overdrive=3, bench="50 ohm sources and input network", options=opt.strip(),
               input_edge=edge, recovery_us=trec * 1e6,
               v_during=float(np.mean(v[mid])),
               fe_out_during=float(np.mean((d["v(oa)"] - d["v(ob)"])[mid])),
               oa_ob_during=[float(np.mean(d["v(oa)"][mid])), float(np.mean(d["v(ob)"][mid]))],
               sa_sb_during=[float(np.mean(d["v(sa)"][mid])), float(np.mean(d["v(sb)"][mid]))],
               ca_cb_during=[float(np.mean(d["v(ca)"][mid])), float(np.mean(d["v(cb)"][mid]))],
               ca_cb_before=[float(np.mean(d["v(ca)"][t < 1.9e-6])), float(np.mean(d["v(cb)"][t < 1.9e-6]))])
    for node in ("oa", "ob", "ca", "cb", "sa", "sb"):
        x = d[f"v({node})"]
        x0 = float(np.mean(x[t < 1.9e-6]))
        dev = np.where(np.abs(x[after] - x0) > 0.01)[0]
        res[f"{node}_recovery_us"] = float(t[after][dev[-1]] - t_off) * 1e6 if len(dev) else 0.0
    return res, {k: v for k, v in d.items()}


def run_h_ths4031() -> dict:
    """The H overload with the THS4031 in S2 and 1-ohm sources (the bench of large_signal.py), which
    converges where the LM7171 version does not; the front end is the same, and S2 clips only after
    it.  Saves overload_curves_H100_THS4031.npz; the note's description of the front end's internal
    nodes during an overload comes from this run."""
    chain.DA_OPAMP = "THS4031"
    mode, g = L.CASES["H100"]
    s = chain.allocate(g, mode)
    amp = 3 * 10.0 / s.gain
    src = (L.TRAN_OPTIONS + f"VA ina 0 DC 0 PULSE(0 {amp / 2:g} 2u 10n 10n 20u 100u)\n"
           f"VB inb 0 DC 0 PULSE(0 {-amp / 2:g} 2u 10n 10n 20u 100u)\nRIA ina ga 1 rnl\nRIB inb gb 1 rnl\n")
    ctl = ".control\n" + spice.WR + f"tran 2n 40u 0 2n\nwrdata tran.txt {NODES}\n.endc\n"
    f = spice.run("large/H100_overload_THS4031_nodes", chain.deck(s, "overload H100 THS4031", src, ctl))
    d = spice.read_table(f / "tran.txt")
    np.savez(spice.RESULTS / "overload_curves_H100_THS4031.npz", **d)
    return d


T_ON, T_OFF, FS = 2e-6, 22.01e-6, 10.0


def _windows(t: np.ndarray) -> dict:
    return dict(rest=t < 1.9e-6, during=(t > 15e-6) & (t < 20e-6), final=t > 38e-6, after=t > T_OFF)


def _settle(t: np.ndarray, x: np.ndarray, ref: float, tol: float) -> float:
    """Last time after T_OFF at which |x - ref| > tol, minus T_OFF (s); 0 if never."""
    a = t > T_OFF
    bad = np.where(np.abs(x[a] - ref) > tol)[0]
    return float(t[a][bad[-1]] - T_OFF) if len(bad) else 0.0


def _ramp(t: np.ndarray, v: np.ndarray, w: dict, t_rec: float) -> dict:
    """The output's return after the release (see the module docstring)."""
    v_dur, v_fin = float(np.mean(v[w["during"]])), float(np.mean(v[w["final"]]))
    exc = v_dur - v_fin
    a = w["after"]
    ta, rel = t[a], (v[a] - v_fin) / exc

    def first_below(x):
        return float(ta[np.argmax(rel <= x)])
    t99, t90, t10 = first_below(0.99), first_below(0.9), first_below(0.1)
    m = (t >= T_OFF) & (t <= T_OFF + t_rec)
    dt, dv = np.diff(t[m]), np.diff(v[m])
    ok = dt > 0
    k = int(np.argmax(np.abs(dv[ok] / dt[ok])))
    tu = np.arange(T_OFF, T_OFF + t_rec, 0.5e-9)
    vu = np.interp(tu, t, v)
    s5 = np.abs(vu[10:] - vu[:-10]) / 5e-9
    return dict(excursion_V=exc, delay_to_1pct_ns=(t99 - T_OFF) * 1e9, t90_ns=(t90 - T_OFF) * 1e9,
                t10_ns=(t10 - T_OFF) * 1e9, slope_10_90_V_us=0.8 * exc / (t10 - t90) / 1e6,
                peak_slope_V_us=float(np.abs(dv[ok] / dt[ok])[k] / 1e6),
                peak_slope_at_ns=float((t[m][:-1][ok][k] - T_OFF) * 1e9),
                peak_slope_5ns_V_us=float(s5.max() / 1e6))


def numbers() -> dict:
    """Section 6.5's overload numbers from the archived curves (module docstring)."""
    import frontend as F
    res = {}
    gm_side = json.loads((spice.RESULTS / "fe_gain_derived.json").read_text(encoding="utf-8"))[
        "g_m one side from the operating point (S)"]
    # ---- H, gain 100: the LM7171 in S2 (the note's numbers; this script's run, 50-ohm sources, the KLU
    # solver) and, for comparison, the THS4031 in S2 (overload_curves_H100_THS4031.npz, 1-ohm sources)
    dd = np.load(spice.RESULTS / "overload_curves.npz")
    h_sets = {"H100": ({k[len("H100_"):]: dd[k] for k in dd.files if k.startswith("H100_")},
                       "overload_curves.npz, H100_* (LM7171 in S2, 50-ohm sources, the KLU solver)"),
              "H100_THS4031": (np.load(spice.RESULTS / "overload_curves_H100_THS4031.npz"),
                               "overload_curves_H100_THS4031.npz (THS4031 in S2, 1-ohm sources)")}
    for key, (d, source) in h_sets.items():
        t = d["time"]
        w = _windows(t)
        mean = {n: {k: float(np.mean(d[f"v({n})"][w[k]])) for k in ("rest", "during", "final")}
                for n in ("out", "oa", "ob", "da", "sa", "sb", "ca", "cb")}
        mode, g = L.CASES["H100"]
        s = chain.allocate(g, mode)
        p = F.CASES[s.fe]
        v_in = 3 * FS / s.gain
        rec = _settle(t, d["v(out)"], mean["out"]["final"], 0.01 * FS)
        h = dict(source=source, gain=s.gain,
                 input_step_V=v_in, gate_step_V=[v_in / 2, -v_in / 2], means=mean, recovery_us=rec * 1e6)
        h["output_ramp"] = _ramp(t, d["v(out)"], w, rec)
        h["output_during_V"] = mean["out"]["during"]
        h["output_max_V"], h["output_min_V"] = float(d["v(out)"].max()), float(d["v(out)"].min())
        # the output's undershoot below its final value after the release (as for L below)
        rel_h = d["v(out)"][w["after"]] - mean["out"]["final"]
        t_h = t[w["after"]]
        iu = int(np.argmin(rel_h))
        bu = np.where(rel_h < -0.1)[0]
        h["undershoot"] = dict(depth_V=float(rel_h[iu]), at_ns=float((t_h[iu] - T_OFF) * 1e9),
                               beyond_minus_0p1V_duration_ns=float((t_h[bu[-1]] - t_h[bu[0]]) * 1e9) if len(bu) else 0.0,
                               overshoot_after_V=float(rel_h[iu:].max()))
        h["S2_out_during_V"] = mean["da"]["during"]
        oa, ob, a = d["v(oa)"], d["v(ob)"], w["after"]
        ia, ib = int(np.argmin(oa[a])), int(np.argmax(ob[a]))
        h["opamp_outputs"] = dict(
            oa_during_V=mean["oa"]["during"], ob_during_V=mean["ob"]["during"],
            difference_during_V=mean["oa"]["during"] - mean["ob"]["during"],
            oa_min_after_V=float(oa[a][ia]), oa_min_after_from_rest_V=float(oa[a][ia] - mean["oa"]["rest"]),
            oa_min_after_at_ns=float((t[a][ia] - T_OFF) * 1e9),
            ob_max_after_V=float(ob[a][ib]), ob_max_after_from_rest_V=float(ob[a][ib] - mean["ob"]["rest"]),
            ob_max_after_at_ns=float((t[a][ib] - T_OFF) * 1e9),
            oa_max_V=float(oa.max()), ob_min_V=float(ob.min()),
            dev_at_0p2us_mV=[1e3 * (float(np.interp(T_OFF + 0.2e-6, t, x)) - mean[n]["rest"])
                             for n, x in (("oa", oa), ("ob", ob))],
            within_12mV_after_us=[_settle(t, x, mean[n]["rest"], 0.012) * 1e6 for n, x in (("oa", oa), ("ob", ob))],
            within_10mV_after_us=[_settle(t, x, mean[n]["rest"], 0.010) * 1e6 for n, x in (("oa", oa), ("ob", ob))])
        dvg = {"a": v_in / 2, "b": -v_in / 2}
        src = {}
        for x in "ab":
            dvs = mean[f"s{x}"]["during"] - mean[f"s{x}"]["rest"]
            dvc = mean[f"c{x}"]["during"] - mean[f"c{x}"]["rest"]
            r_d = (p.vp - p.vref) / (p.n * p.id)
            sx, cx = d[f"v(s{x})"], d[f"v(c{x})"]
            src[x] = dict(dv_source_V=dvs, dv_gate_V=dvg[x], dV_GS_V=dvg[x] - dvs,
                          source_max_dev_V=float(np.max(np.abs(sx - mean[f"s{x}"]["rest"]))),
                          summing_rest_V=mean[f"c{x}"]["rest"], summing_during_V=mean[f"c{x}"]["during"],
                          dv_summing_V=dvc, R_D=r_d, dI_from_R_D_mA=-dvc / r_d * 1e3,
                          dI_gm_estimate_mA=gm_side * (dvg[x] - dvs) * 1e3,
                          summing_extremes_V=[float(cx.min()), float(cx.max())],
                          summing_within_10mV_after_us=_settle(t, cx, mean[f"c{x}"]["rest"], 0.010) * 1e6,
                          source_within_10mV_after_us=_settle(t, sx, mean[f"s{x}"]["rest"], 0.010) * 1e6)
        h["sides"] = src
        h["V_GS_rest_V"] = -mean["sa"]["rest"]
        h["g_m_one_side_S"] = gm_side
        err = (oa + ob - d["v(sa)"] - d["v(sb)"]) / 2
        g_int, c_int = 1e-6, 1e-6
        r_t = p.v_sink / (p.n * p.id + p.i_bs)
        e_dur = float(np.mean(err[w["during"]]))
        integral = float(np.trapezoid(g_int * err / c_int, t))
        h["servo"] = dict(outputs_mean_during_V=(mean["oa"]["during"] + mean["ob"]["during"]) / 2,
                          sources_mean_during_V=(mean["sa"]["during"] + mean["sb"]["during"]) / 2,
                          error_during_V=e_dur, rate_V_per_s=g_int * e_dur / c_int,
                          integrator_change_uV=integral * 1e6,
                          after_1s_reference_V=g_int * e_dur * 1.0 / c_int, R_F=p.rf, R_T=r_t,
                          after_1s_output_cm_V=g_int * e_dur * 1.0 / c_int * p.rf / r_t,
                          loop_time_constant_s=(c_int / g_int) * r_t / p.rf)
        r_bs = p.vbs / p.i_bs
        h["bootstrap_time_constant_ms"] = r_bs * p.c_bs * 1e3
        v_sd = h["opamp_outputs"]["difference_during_V"] * p.rg / (2 * p.rf + p.rg)
        h["larger_overloads"] = dict(
            source_difference_with_clipped_outputs_V=v_sd,
            dV_GS_estimate_at_3x_V=(v_in - v_sd) / 2,
            dV_GS_estimate_at_10x_V=(10 * FS / s.gain - v_sd) / 2,
            input_for_zero_gate_bias_V=2 * abs(h["V_GS_rest_V"]) + v_sd,
            overdrive_for_zero_gate_bias=(2 * abs(h["V_GS_rest_V"]) + v_sd) / (FS / s.gain))
        res[key] = h
    # ---- L, gain 1000, LM7171 in S2
    d = np.load(spice.RESULTS / "overload_curves.npz")
    t = d["L1000_time"]
    w = _windows(t)
    mean = {n: {k: float(np.mean(d[f"L1000_v({n})"][w[k]])) for k in ("rest", "during", "final")}
            for n in ("out", "oa", "ob", "da")}
    mode, g = L.CASES["L1000"]
    s = chain.allocate(g, mode)
    v = d["L1000_v(out)"]
    rec = _settle(t, v, mean["out"]["final"], 0.01 * FS)
    a = w["after"]
    rel = v[a] - mean["out"]["final"]
    i = int(np.argmin(rel))
    below = np.where(rel < -0.1)[0]
    lo = dict(source="overload_curves.npz, L1000_* (LM7171 in S2, 50-ohm sources)", gain=s.gain,
              input_step_V=3 * FS / s.gain, means=mean, recovery_us=rec * 1e6,
              output_during_V=mean["out"]["during"], output_max_V=float(v.max()),
              fe_out_during_V=mean["oa"]["during"] - mean["ob"]["during"], S2_out_during_V=mean["da"]["during"],
              undershoot=dict(depth_V=float(rel[i]), at_ns=float((t[a][i] - T_OFF) * 1e9),
                              beyond_minus_0p1V_from_ns=float((t[a][below[0]] - T_OFF) * 1e9),
                              beyond_minus_0p1V_to_ns=float((t[a][below[-1]] - T_OFF) * 1e9),
                              beyond_minus_0p1V_duration_ns=float((t[a][below[-1]] - t[a][below[0]]) * 1e9),
                              overshoot_after_V=float(rel[i:].max()),
                              overshoot_after_at_ns=float((t[a][i + int(np.argmax(rel[i:]))] - T_OFF) * 1e9)))
    lo["output_ramp"] = _ramp(t, v, w, rec)
    res["L1000"] = lo
    return res


def print_numbers(r: dict) -> None:
    h, lo = r["H100"], r["L1000"]
    oo, rp = h["opamp_outputs"], h["output_ramp"]
    print(f"H, gain {h['gain']:.4g} ({h['source']}): input step {h['input_step_V']:.4f} V, gates +/-{h['input_step_V'] / 2:.4f} V")
    print(f"  output during {h['output_during_V']:.4f} V (max {h['output_max_V']:.4f}, min {h['output_min_V']:.4f}); "
          f"S2 output during {h['S2_out_during_V']:.3f} V; recovery to 0.1 V {h['recovery_us']:.4f} us")
    print(f"  output ramp: excursion {rp['excursion_V']:.3f} V, delay to 1 % {rp['delay_to_1pct_ns']:.1f} ns, 90 % at "
          f"{rp['t90_ns']:.1f} ns, 10 % at {rp['t10_ns']:.1f} ns, 10-90 % slope {rp['slope_10_90_V_us']:.1f} V/us, "
          f"peak slope {rp['peak_slope_V_us']:.1f} V/us at {rp['peak_slope_at_ns']:.1f} ns (over 5 ns {rp['peak_slope_5ns_V_us']:.1f} V/us)")
    print(f"  op amps clip at {oo['oa_during_V']:+.3f} / {oo['ob_during_V']:+.3f} V ({oo['difference_during_V']:.3f} V between); "
          f"after the release oa min {oo['oa_min_after_V']:+.3f} V ({oo['oa_min_after_from_rest_V']:+.3f} from rest) at "
          f"{oo['oa_min_after_at_ns']:.1f} ns, ob max {oo['ob_max_after_V']:+.3f} V ({oo['ob_max_after_from_rest_V']:+.3f}) at "
          f"{oo['ob_max_after_at_ns']:.1f} ns; whole run oa max {oo['oa_max_V']:+.3f}, ob min {oo['ob_min_V']:+.3f} V")
    print(f"  deviation from rest at 0.2 us: {oo['dev_at_0p2us_mV'][0]:+.2f} / {oo['dev_at_0p2us_mV'][1]:+.2f} mV; within 12 mV after "
          f"{oo['within_12mV_after_us'][0]:.3f} / {oo['within_12mV_after_us'][1]:.3f} us, within 10 mV after "
          f"{oo['within_10mV_after_us'][0]:.3f} / {oo['within_10mV_after_us'][1]:.3f} us")
    for x, sd in h["sides"].items():
        print(f"  side {x}: gate {sd['dv_gate_V'] * 1e3:+.1f} mV, source {sd['dv_source_V'] * 1e3:+.1f} mV, dV_GS "
              f"{sd['dV_GS_V'] * 1e3:+.1f} mV; summing node {sd['summing_rest_V']:.3f} -> {sd['summing_during_V']:.3f} V "
              f"(dI = {sd['dI_from_R_D_mA']:+.3f} mA from R_D {sd['R_D']:.0f} ohm, g_m dV_GS {sd['dI_gm_estimate_mA']:+.3f} mA); "
              f"summing node within 10 mV after {sd['summing_within_10mV_after_us']:.3f} us")
    sv = h["servo"]
    print(f"  V_GS at rest {h['V_GS_rest_V']:+.4f} V; servo: outputs' mean {sv['outputs_mean_during_V']:+.4f} V, sources' mean "
          f"{sv['sources_mean_during_V']:+.4f} V, error {sv['error_during_V']:+.4f} V, rate {sv['rate_V_per_s']:+.4f} V/s, "
          f"a servo's integrator would change by {sv['integrator_change_uV']:+.2f} uV over the run")
    print(f"  after 1 s: reference {sv['after_1s_reference_V']:+.4f} V, outputs' CM {sv['after_1s_output_cm_V']:+.4f} V "
          f"(R_F/R_T = {sv['R_F']:.0f}/{sv['R_T']:.2f}), servo time constant {sv['loop_time_constant_s']:.3f} s; "
          f"bootstrap R_BS C_BS {h['bootstrap_time_constant_ms']:.2f} ms")
    lg = h["larger_overloads"]
    print(f"  larger overloads: v_s,d with clipped outputs {lg['source_difference_with_clipped_outputs_V']:.4f} V; dV_GS ~ "
          f"{lg['dV_GS_estimate_at_3x_V'] * 1e3:.1f} mV at 3x, {lg['dV_GS_estimate_at_10x_V'] * 1e3:.1f} mV at 10x; zero gate bias at "
          f"{lg['input_for_zero_gate_bias_V']:.3f} V ({lg['overdrive_for_zero_gate_bias']:.2f} x full scale)")
    hu = h["undershoot"]
    print(f"  undershoot {hu['depth_V']:+.4f} V at {hu['at_ns']:.1f} ns, more than 0.1 V below the final value for "
          f"{hu['beyond_minus_0p1V_duration_ns']:.1f} ns, then {hu['overshoot_after_V']:+.4f} V")
    t31 = r.get("H100_THS4031")
    if t31:
        print(f"H with the THS4031 in S2 ({t31['source']}): recovery to 0.1 V {t31['recovery_us']:.4f} us, output during "
              f"{t31['output_during_V']:.4f} V, 10-90 % slope {t31['output_ramp']['slope_10_90_V_us']:.1f} V/us")
    u, rp = lo["undershoot"], lo["output_ramp"]
    print(f"L, gain {lo['gain']:.4g} ({lo['source']}): output during {lo['output_during_V']:.4f} V, front end's outputs "
          f"{lo['fe_out_during_V']:.4f} V apart, S2 output {lo['S2_out_during_V']:.4f} V; recovery {lo['recovery_us']:.4f} us")
    print(f"  undershoot {u['depth_V']:+.4f} V at {u['at_ns']:.1f} ns; beyond -0.1 V from {u['beyond_minus_0p1V_from_ns']:.1f} to "
          f"{u['beyond_minus_0p1V_to_ns']:.1f} ns ({u['beyond_minus_0p1V_duration_ns']:.1f} ns); then {u['overshoot_after_V']:+.4f} V "
          f"at {u['overshoot_after_at_ns']:.1f} ns")
    print(f"  output ramp: delay to 1 % {rp['delay_to_1pct_ns']:.1f} ns, 10-90 % slope {rp['slope_10_90_V_us']:.1f} V/us, "
          f"peak slope {rp['peak_slope_V_us']:.1f} V/us at {rp['peak_slope_at_ns']:.1f} ns (over 5 ns {rp['peak_slope_5ns_V_us']:.1f} V/us)")


def _child(name: str, k: int) -> None:
    r, d = run(name, k)
    (spice.RESULTS / f"_overload_{name}.json").write_text(json.dumps(r), encoding="utf-8")
    np.savez(spice.RESULTS / f"_overload_{name}.npz", **d)


def main(args):
    import subprocess
    sys.stdout.reconfigure(encoding="utf-8")
    if args and args[0] == "--child":
        _child(args[1], int(args[2]))
        return
    if args and args[0] == "--h-ths4031":
        run_h_ths4031()
        return
    if args and args[0] == "numbers":
        r = numbers()
        print_numbers(r)
        (spice.RESULTS / "overload_numbers.json").write_text(json.dumps(r, indent=1), encoding="utf-8", newline="\n")
        return
    models.prepare()
    path = spice.RESULTS / "large_signal.json"
    curves = {}
    for name in args or list(L.CASES):
        r = None
        for k in range(len(ATTEMPTS)):
            tmp = spice.RESULTS / f"_overload_{name}.json"
            tmp.unlink(missing_ok=True)
            proc = subprocess.Popen([sys.executable, "-u", __file__, "--child", name, str(k)])
            try:
                proc.wait(timeout=300)
            except subprocess.TimeoutExpired:
                proc.kill()
                print(f"{name}: attempt {k} timed out", flush=True)
                continue
            if tmp.exists():
                r = json.loads(tmp.read_text(encoding="utf-8"))
                d = np.load(spice.RESULTS / f"_overload_{name}.npz")
                for kk in d.files:
                    curves[f"{name}_{kk}"] = d[kk]
                print(f"{name}: attempt {k} ran", json.dumps(r), flush=True)
                break
            print(f"{name}: attempt {k} failed", flush=True)
        res = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        res.setdefault(name, {})["overload"] = r if r else dict(failed="no attempt converged")
        path.write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    np.savez(spice.RESULTS / "overload_curves.npz", **curves)


if __name__ == "__main__":
    main(sys.argv[1:])
