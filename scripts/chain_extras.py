"""Three checks of the complete chain (chain.py, frontend.py) that the note quotes without a run of
their own.  chain.py and frontend.py are imported, not changed.

post    The stages after the front end alone (S2, F1, S3, F2, S4, S5 and the output's 49.9 ohm into
        1 Mohm): the front end and the input network removed, S2's inputs oa and ob driven
        differentially by ideal sources (+1/2 and -1/2 V AC), the supplies +/-15 V.  For each node
        x of da (S2), s3, s4 and out:
            H_x(f) = v(x) / (v_oa - v_ob),
            f_3dB  where |H_x| = |H_x(1 kHz)| / sqrt(2) (spice.f3db with the 1 kHz reference),
            peak   20 log10(max |H_x| / |H_x(1 kHz)|),  and 20 log10(|H_x(f)| / |H_x(1 kHz)|) at 10,
                   30 and 100 MHz,
        for every allocation (a3, a4, a5) that chain.allocate makes at the gains of chain.py (modes
        H_LN, H_HR, L; filters off).  AC from 1 Hz to 1 GHz, 40 points per decade.
supply  The supply currents at the operating point, with ideal references (V_ref, the sinks' base
        reference and the common-mode servo are ideal sources in the netlist and draw nothing from
        the rails):
            I(+15 V) = -i(VP),  I(-15 V) = i(VM)   (ngspice's branch current flows from + to -
                                                    through the source)
        split into the front end's branches, from the operating point's node voltages,
            drain resistors  I_RD = (V_P - v(c)) / R_D,   bootstrap  I_UP = (V_P - v(b)) / R_UP,
            sinks            I_T = (v(e) - V_M) / R_T     (per side),
        and each op amp's supply pins (a 0-V source in series with each op amp's V+ and V- pin:
        i(VSP_<X>) into V+, i(VSM_<X>) out of V-).  The regulators (LT3045 for +15 V, LT3094 for
        -15 V) dissipate
            P_reg = (V_in - V_out) I = V_headroom I     at V_headroom = 2 V and 3 V
        (their own ground current is not included).  For H at total gains of 1000 (H_LN, H100) and
        100 (H_HR, H10), and L at 1000 (L200 with the adopted 6 V sinks), each with the filters off
        (F1 and F2 wires) and on (both LP 1 MHz: their THS4031 followers in the circuit).
step    The front end alone against the chain at a total gain of 100 (H_LN: H100, a3 = a4 = 0.1,
        a5 = 0.2), for steps of 1 V and 10 V at the output: the sources, options and measures of
        large_signal.py (differential pulse at 1 us with 1 ns edges, inputs through 1 ohm,
        tran 0.2 ns 4 us, Gear and abstol 1e-12 first; 10-90 % rise, overshoot, settling to 1 % and
        0.1 %, slew rate; large_signal.step_metrics), on
            the front end alone   v(oa) - v(ob), with the input network of chain.INPUT_NET, outputs
                                  unloaded (no S2)
            the chain             v(oa) - v(ob) (the front end loaded by S2), v(da) (S2's output) and
                                  v(out)
        The input amplitude is the chain's, V_step / G, so the front end's output steps by
        V_step G_FE / G = V_step (G_FE = 100.01 = G).  Full-power bandwidth from the 10 V step's slew
        rate SR, for a sine of 10 Vpp:  f_FP = SR / (pi * 10 V).
Writes ../sim/results/chain_extras.json.
Usage: python chain_extras.py [post] [supply] [step]          (none: all three)
"""
from __future__ import annotations

import json
import math
import re
import sys

import numpy as np

import blocks
import chain
import frontend as F
import large_signal as L
import spice

GAINS = {"H_LN": [1, 10, 100, 1000, 10000, 50000], "H_HR": [1, 10, 100, 1000], "L": [200, 1000, 10000, 100000]}


def libs() -> str:
    return f"{spice.lib('jfets.lib')}{spice.lib('opamps.lib')}{spice.lib('bjts.lib')}"


def post_netlist(s: chain.Setting) -> str:
    """chain.netlist(s) from S2 on (front end and input network removed)."""
    body = chain.netlist(s)
    k = body.index("* S2 difference amplifier")
    return body[k:]


def run_post() -> dict:
    allocs: dict[tuple, list] = {}
    for mode, gl in GAINS.items():
        for g in gl:
            s = chain.allocate(g, mode)
            allocs.setdefault((s.a3, s.a4, s.a5), []).append(f"{mode} {g:g} ({s.fe})")
    out = {}
    for (a3, a4, a5), users in allocs.items():
        s = chain.Setting("H100", a3, a4, a5)
        tag = f"a3_{a3:g}_a4_{a4:g}_a5_{a5:g}".replace(".", "p")
        deck = (f"* stages after the front end {tag}\n{spice.OPTIONS}.options rshunt=1e12\n{libs()}{blocks.COMMON}"
                "VP vp 0 DC 15\nVM vm 0 DC -15\nVOA oa 0 DC 0 AC 0.5\nVOB ob 0 DC 0 AC -0.5\n"
                + post_netlist(s) + ".control\n" + spice.WR +
                "ac dec 40 1 1g\nwrdata ac.txt v(da) v(s3) v(s4) v(out)\n.endc\n.end\n")
        f = spice.run(f"chain/extras_post_{tag}", deck)
        d = spice.read_table(f / "ac.txt")
        fr = d["frequency"]
        r = dict(a3=a3, a4=a4, a5=a5, used_by=users, gain_after_fe=10 * a3 * 10 * a4 * 5 * a5)
        for node in ("da", "s3", "s4", "out"):
            mag = np.abs(d[f"v({node})"])
            ref = spice.at(fr, mag, 1e3)
            r[node] = dict(gain_1k=ref, f3db=spice.f3db(fr, mag, ref),
                           peak_db=float(20 * np.log10(mag.max() / ref)),
                           f_peak=float(fr[int(np.argmax(mag))]),
                           **{f"db_{lab}": float(20 * np.log10(spice.at(fr, mag, f0) / ref))
                              for lab, f0 in (("10M", 10e6), ("30M", 30e6), ("100M", 100e6))})
        out[tag] = r
        o = r["out"]
        print(f"after the front end, {tag} (gain {o['gain_1k']:.4g}; {', '.join(users)}): f3dB at da "
              f"{r['da']['f3db'] / 1e6:.1f}, s3 {r['s3']['f3db'] / 1e6:.1f}, s4 {r['s4']['f3db'] / 1e6:.1f}, out "
              f"{o['f3db'] / 1e6:.1f} MHz; out peak {o['peak_db']:.2f} dB at {o['f_peak'] / 1e6:.1f} MHz, "
              f"10 MHz {o['db_10M']:+.2f} dB, 30 MHz {o['db_30M']:+.2f} dB, 100 MHz {o['db_100M']:+.2f} dB", flush=True)
    return out


SUPPLY_SETTINGS = [("H_LN", 1000), ("H_HR", 100), ("L", 1000)]


def instrument_supplies(text: str) -> tuple[str, list[str]]:
    """A 0-V source in series with each op amp's supply pins (vp, vm) in the netlist text."""
    names = []

    def sub(m):
        x = m.group(1)
        names.append(x)
        return (f"{x}{m.group(2)} vp_{x} vm_{x} {m.group(3)}\nVSP_{x} vp vp_{x} 0\nVSM_{x} vm_{x} vm 0")
    new = re.sub(r"^(X\S+)(.*) vp vm (OA_\S+)$", sub, text, flags=re.M)
    return new, names


def run_supply() -> dict:
    out = {}
    for mode, g in SUPPLY_SETTINGS:
        for filt in (False, True):
            s0 = chain.allocate(g, mode)
            s = chain.Setting(s0.fe, s0.a3, s0.a4, s0.a5, *((("LP", 1e6), ("LP", 1e6)) if filt else (None, None)))
            p = F.CASES[s.fe]
            text, ops = instrument_supplies(chain.netlist(s))
            probes = ["i(vp)", "i(vm)"] + [f"i(vsp_{x.lower()})" for x in ops] + [f"i(vsm_{x.lower()})" for x in ops]
            nodes = ["v(ca)", "v(cb)", "v(ba)", "v(bb)", "v(ea)", "v(eb)"]
            deck = (f"* supply currents {s.tag}\n{spice.OPTIONS}.options rshunt=1e12\n{libs()}{blocks.COMMON}"
                    "VA ina 0 DC 0\nRIA ina ga 1m rnl\nRIB ina gb 1m rnl\n" + text +
                    ".control\n" + spice.WR + "op\nprint " + " ".join(probes + nodes) + "\n.endc\n.end\n")
            f = spice.run(f"chain/extras_supply_{s.tag}", deck)
            val = {k: spice.printed(f, k) for k in probes + nodes}
            r_d = (p.vp - p.vref) / (p.n * p.id)
            r_up = (p.vp - (0.6 + p.vbs)) / p.i_bs
            r_t = p.v_sink / (p.n * p.id + p.i_bs)
            i_p, i_m = -val["i(vp)"], val["i(vm)"]
            fe = dict(R_D=r_d, R_UP=r_up, R_T=r_t,
                      I_RD=[(p.vp - val["v(ca)"]) / r_d, (p.vp - val["v(cb)"]) / r_d],
                      I_UP=[(p.vp - val["v(ba)"]) / r_up, (p.vp - val["v(bb)"]) / r_up],
                      I_T=[(val["v(ea)"] - p.vm) / r_t, (val["v(eb)"] - p.vm) / r_t])
            opamps = {x: dict(model=re.search(rf"^{x}\b.* (OA_\S+)$", text, re.M).group(1),
                              I_plus=val[f"i(vsp_{x.lower()})"], I_minus=val[f"i(vsm_{x.lower()})"]) for x in ops}
            key = f"{mode}_{g}" + ("_filters_on" if filt else "")
            out[key] = dict(tag=s.tag, I_plus15=i_p, I_minus15=i_m, front_end=fe, opamps=opamps,
                            I_RD_total=sum(fe["I_RD"]),
                            opamps_plus_total=sum(o["I_plus"] for o in opamps.values()),
                            opamps_minus_total=sum(o["I_minus"] for o in opamps.values()),
                            P_LT3045={f"{h:g} V": h * i_p for h in (2.0, 3.0)},
                            P_LT3094={f"{h:g} V": h * i_m for h in (2.0, 3.0)})
            o = out[key]
            print(f"supply {key} ({s.tag}): +15 V {i_p * 1e3:.2f} mA, -15 V {i_m * 1e3:.2f} mA; drain resistors "
                  f"{o['I_RD_total'] * 1e3:.2f} mA, R_UP {sum(fe['I_UP']) * 1e3:.3f} mA, sinks {sum(fe['I_T']) * 1e3:.2f} mA; "
                  f"op amps +{o['opamps_plus_total'] * 1e3:.2f} / -{o['opamps_minus_total'] * 1e3:.2f} mA ("
                  + ", ".join(f"{x} {v['model'][3:]} {v['I_plus'] * 1e3:.2f}/{v['I_minus'] * 1e3:.2f}" for x, v in opamps.items())
                  + f"); LT3045 {o['P_LT3045']['2 V']:.3f} / {o['P_LT3045']['3 V']:.3f} W, LT3094 "
                  f"{o['P_LT3094']['2 V']:.3f} / {o['P_LT3094']['3 V']:.3f} W at 2 / 3 V of headroom", flush=True)
    return out


def fe_step(vstep: float, s: chain.Setting) -> dict:
    """The front end alone (module docstring), with the option sets of large_signal.tran."""
    p = F.CASES[s.fe]
    net = chain.INPUT_NET[s.fe[0]]
    inp = (f"CPA ga 0 {net['cp']:g}\nCPB gb 0 {net['cp']:g}\nRZA ga za {net['rz']:g}\nCZA za 0 {net['cz']:g}\n"
           f"RZB gb zb {net['rz']:g}\nCZB zb 0 {net['cz']:g}\nRBA ga 0 {net['rbias']:g}\nRBB gb 0 {net['rbias']:g}\n")
    src = L.step_source(s.gain, vstep) + inp
    ctl = ".control\n" + spice.WR + "tran 0.2n 4u 0 0.2n\nwrdata tran.txt v(oa) v(ob)\n.endc\n"
    for k, opt in enumerate(L.TRIES[:3]):
        try:
            f = spice.run(f"chain/extras_fe_step_{vstep:g}", F.deck(p, f"front end step {vstep:g} V", opt + src, ctl))
            d = spice.read_table(f / "tran.txt")
            return dict(options=opt.strip(), **L.step_metrics(d["time"], d["v(oa)"] - d["v(ob)"]))
        except RuntimeError:
            if k == 2:
                raise


def run_step() -> dict:
    s = chain.allocate(100, "H_LN")
    out = dict(tag=s.tag, gain=s.gain, gain_fe=F.CASES[s.fe].gain)
    for vstep in (1.0, 10.0):
        r = dict(front_end_alone=fe_step(vstep, s))
        tag = f"extras/H100_step_{vstep:g}"
        d = L.tran(s, tag, L.step_source(s.gain, vstep), 4e-6, 0.2e-9, "v(out) v(oa) v(ob) v(da)")
        t = d["time"]
        r["chain_options"] = L.LAST_TRY[tag]
        r["chain_fe_out"] = L.step_metrics(t, d["v(oa)"] - d["v(ob)"])
        r["chain_S2_out"] = L.step_metrics(t, d["v(da)"])
        r["chain_out"] = L.step_metrics(t, d["v(out)"])
        if vstep == 10.0:
            r["full_power_bandwidth_10Vpp_MHz"] = {k: r[k]["slew_v_us"] * 1e6 / (math.pi * 10.0) / 1e6
                                                   for k in ("front_end_alone", "chain_fe_out", "chain_S2_out", "chain_out")}
            print("full-power bandwidth for 10 Vpp, SR / (pi 10 V): " + ", ".join(
                f"{k} {v:.2f} MHz" for k, v in r["full_power_bandwidth_10Vpp_MHz"].items()), flush=True)
        out[f"{vstep:g} V"] = r
        for k, lab in (("front_end_alone", "front end alone"), ("chain_fe_out", "front end in the chain"),
                       ("chain_S2_out", "S2's output (da)"), ("chain_out", "chain output")):
            x = r[k]
            print(f"step {vstep:g} V, {lab:24s}: step {x['dv']:.4f} V, rise {x['rise_ns']:.1f} ns, overshoot "
                  f"{x['overshoot'] * 100:.2f} %, settle 1 % {x['settle_ns_1']:.0f} ns, 0.1 % {x['settle_ns_0p1']:.0f} ns, "
                  f"slew {x['slew_v_us']:.0f} V/us", flush=True)
    return out


PARTS = dict(post=run_post, supply=run_supply, step=run_step)


def main(args):
    sys.stdout.reconfigure(encoding="utf-8")
    path = spice.RESULTS / "chain_extras.json"
    res = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    for part in args or list(PARTS):
        res[part] = PARTS[part]()
        path.write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main(sys.argv[1:])
