"""Common-mode rejection of the complete chain with component mismatch (Monte Carlo).

For each trial every toleranced part of the netlist of chain.netlist() is scaled by a random
factor (Gaussian, the sigma below, clipped at 3 sigma), the JFETs get their own cards with VTO and
BETA shifted, and the chain's response to a differential input (A = +1/2, B = -1/2) and to a
common-mode input (A = B = 1) is computed; CMRR(f) = |H_dm| / |H_cm| at the output.  Both inputs
are driven from 50-ohm sources (the input networks' mismatch acts on the source impedance).

Tolerances (sigma):
  resistors of the front end and of the gain stages   0.05 % (0.1 % parts)
  difference-amplifier resistors RD1-RD4              0.005 % (0.01 % network) or 0.05 % ('discrete')
  integrating and cross capacitors CI, CX             1 %   (2 % C0G)
  input network C_P, C_Z                              2.5 % (5 %); R_Z 0.5 %
  JFETs: H, JFE2140 duals: the two halves of one dual share a common VTO offset (sigma 100 mV,
         BETA 5 %) and differ by sigma 0.85 mV (VTO) and 1 % (BETA) [data sheet: |dV_GS| 1 mV
         typ, 4 mV max]; L, JFE150 singles:
         all 24 from one V_GS bin (the bin itself: VTO sigma 85 mV, BETA 5 %, common to all),
         within the bin VTO sigma 3 mV (a +/-5 mV bin) and BETA 2 %.  Unsorted JFE150 (85 mV
         each) do not work: the difference of the two sides' mean V_GS (about 35 mV rms) times
         the gain of 200 saturates the chain, and some trials then have no DC solution at all
         (seed 5 of the first run hung in ngspice's dynamic gmin stepping).
  BF862 cascodes: VTO sigma 50 mV, BETA 5 %
Cases: H100, H10, L200 and H100 with discrete 0.1 % difference-amplifier resistors, all driven
from 50-ohm sources; H100 and L200 with one class of mismatch at a time; H100 and L200 driven
directly (0 ohm); H100 and L200 with the input-network capacitors trimmed (0.1 % residual).
Measure: CMRR(f) = 20 log10(|H_dm(f)| / |H_cm(f)|) at the output, H_dm the response to A = +1/2,
B = -1/2 and H_cm to A = B = 1; per case the median, the 10th percentile and the worst over the
trials at the frequencies FREQ, and the rms output DC offset sqrt(mean(V_out,dc^2)).

The R_UP test (Section 6.4 of the note): R_UP feeds the bootstrap from +15 V, so the bootstrap
current changes with the input common mode by dI_BS = -dV_CM / R_UP; through R_BS this moves the
cascodes' gates by -(R_BS / R_UP) dV_CM relative to the sources (R_BS 3.5 k, R_UP 10.9 k: -0.32),
below the corner f_BS = 1 / (2 pi R_BS C_BS) (45 Hz with C_BS = 1 uF), where C_BS no longer holds
that voltage.  The test replaces R_UP of each side by an ideal current source I_BS (1 mA, the
bootstrap current of frontend.FE) and compares with R_UP in place: H at a total gain of 1000,
JFET mismatch only ('jfet'), inputs driven directly (0 ohm), 4 trials (seeds 0-3) each, the same
JFETs in both (the replacement is made after the random draws).  Cases H100_jfet_rs0_R_UP and
H100_jfet_rs0_ideal_I_BS; the summary key rup_test holds the medians at 10 Hz, 100 Hz and 1 kHz,
their difference, R_BS / R_UP and f_BS, and the same medians recomputed from the archived decks of
the first test (../sim/runs/cmrr_mc/test_rup_R_UP and test_rup_ideal_I_BS), where they exist.
Usage: python cmrr_mc.py [trials [case ...]]   writes ../sim/results/cmrr_mc.json (with case
names: only those are run, and merged into the existing file); the R_UP test always runs 4 trials:
python cmrr_mc.py 4 H100_jfet_rs0_R_UP H100_jfet_rs0_ideal_I_BS
"""
from __future__ import annotations

import json
import math
import multiprocessing as mp
import queue
import re
import sys

import numpy as np

import chain
import frontend as F
import models
import spice

FREQ = [10, 100, 1e3, 1e4, 1e5, 1e6, 3e6, 1e7]
RUP_TRIALS = 4
RUP_CASES = ("H100_jfet_rs0_R_UP", "H100_jfet_rs0_ideal_I_BS")
RUP_ARCHIVE = {"H100_jfet_rs0_R_UP": "test_rup_R_UP", "H100_jfet_rs0_ideal_I_BS": "test_rup_ideal_I_BS"}
RUP_FREQ = [10, 100, 1e3]


def sources(rs: float) -> tuple[str, str]:
    """Differential and common-mode drive through rs in each input (rs = 0: a 1-milliohm
    noiseless wire, the inputs driven directly as in a CMRR test with the inputs shorted)."""
    r = f"{rs:g}" if rs > 0 else "1m rnl"
    dm = f"VA ina 0 DC 0 AC 0.5\nVB inb 0 DC 0 AC -0.5\nRIA ina ga {r}\nRIB inb gb {r}\n"
    cm = f"VA ina 0 DC 0 AC 1\nRIA ina ga {r}\nRIB ina gb {r}\n"
    return dm, cm


def jfet_card(part: str) -> tuple[str, float]:
    lib = (spice.LIB / "jfets.lib").read_text(encoding="utf-8")
    m = re.search(rf"\.subckt {part} d g s\nJ1 d gi s {part}_M\nRX g gi (\S+)\n\.model {part}_M NJF\((.*?)\)", lib)
    return m.group(2), float(m.group(1))


def shift(card: str, dvto: float, kbeta: float) -> str:
    vto = models._get(card, "vto")
    beta = models._get(card, "beta")
    return models._set(models._set(card, "vto", vto + dvto), "beta", beta * kbeta)


def scale_value(line: str, k: float) -> str:
    tok = line.split()
    v = models._get(f"x={tok[3]}", "x")
    tok[3] = f"{v * k:.9g}"
    return " ".join(tok)


def perturb(text: str, s: chain.Setting, rng: np.random.Generator, da: str = "network", only: str = "",
            cnet: float = 0.025) -> str:
    """only: '' (all classes), 'jfet' (JFETs and cascodes), 'r' (resistors), 'c' (capacitors)."""
    def g(sigma, cls="r"):
        if only and cls != only:
            return 0.0
        return float(np.clip(rng.normal(0, sigma), -3 * sigma, 3 * sigma))

    out, extra = [], []
    fe = F.CASES[s.fe]
    card, rx = jfet_card(fe.jfet)
    ccard, crx = jfet_card(fe.cascode[2:])
    # JFET offsets per device
    offs = {}
    for k in range(1, fe.n + 1):
        if fe.jfet == "JFE2140":
            common_v, common_b = g(0.100, "jfet"), g(0.05, "jfet")
            for x in "ab":
                offs[(x, k)] = (common_v + g(0.00085, "jfet"), (1 + common_b) * (1 + g(0.01, "jfet")))
        else:
            if k == 1:
                bin_v, bin_b = g(0.085, "jfet"), g(0.05, "jfet")
            for x in "ab":
                offs[(x, k)] = (bin_v + g(0.003, "jfet"), (1 + bin_b) * (1 + g(0.02, "jfet")))
    for line in text.splitlines():
        name = line.split()[0] if line.strip() and not line.startswith("*") else ""
        up = name.upper()
        m = re.match(r"XJ([ab])(\d+)$", name)
        mc = re.match(r"XC([ab])(\d+)$", name)
        if m:
            x, k = m.group(1), int(m.group(2))
            dv, kb = offs[(x, k)]
            sub = f"JM{x}{k}"
            extra.append(f".subckt {sub} d g s\nJ1 d gi s {sub}_M\nRX g gi {max(rx, 1e-3):.6g}\n"
                         f".model {sub}_M NJF({shift(card, dv, kb)})\n.ends {sub}")
            tok = line.split()
            tok[-1] = sub
            line = " ".join(tok)
        elif mc:
            x, k = mc.group(1), int(mc.group(2))
            sub = f"CM{x}{k}"
            extra.append(f".subckt {sub} d g s\nJ1 d gi s {sub}_M\nRX g gi {max(crx, 1e-3):.6g}\n"
                         f".model {sub}_M NJF({shift(ccard, g(0.05, "jfet"), 1 + g(0.05, "jfet"))})\n.ends {sub}")
            tok = line.split()
            tok[-1] = sub
            line = " ".join(tok)
        elif up.startswith(("RD1", "RD2", "RD3", "RD4")):
            line = scale_value(line, 1 + g(0.00005 if da == "network" else 0.0005))
        elif up.startswith(("CIA", "CIB", "CXA", "CXB")):
            line = scale_value(line, 1 + g(0.01, "c"))
        elif up.startswith(("CPA", "CPB", "CZA", "CZB")):
            line = scale_value(line, 1 + g(cnet, "c"))
        elif up.startswith(("RZA", "RZB")):
            line = scale_value(line, 1 + g(0.005))
        elif (up.startswith("R") and not up.startswith(("RIA", "RIB", "RREF", "RSNK", "RINT", "RLOAD"))
              and "rnl" not in line.split()[3:] and len(line.split()) >= 4):
            line = scale_value(line, 1 + g(0.0005))
        out.append(line)
    return "\n".join(out) + "\n" + "\n".join(extra) + "\n"


def ideal_bootstrap(net: str, s: chain.Setting) -> str:
    """R_UP of each side (RUPa, RUPb: +V to the bootstrap node) replaced by an ideal current source
    of the front end's bootstrap current I_BS."""
    i_bs = F.CASES[s.fe].i_bs
    new, k = re.subn(r"^RUP([ab]) (\S+) (\S+) \S+$", lambda m: f"IUP{m.group(1)} {m.group(2)} {m.group(3)} "
                     f"DC {i_bs * 1e3:g}m", net, flags=re.M)
    assert k == 2, "R_UP lines not found"
    return new


def run_trial(label: str, s: chain.Setting, seed: int, da: str, only: str = "", rs: float = 50.0,
              cnet: float = 0.025, rup: str = "R_UP") -> dict:
    rng = np.random.default_rng(seed)
    net = perturb(chain.netlist(s), s, rng, da, only, cnet)
    if rup == "ideal":
        net = ideal_bootstrap(net, s)
    res = {}
    for kind, src in zip(("dm", "cm"), sources(rs)):
        deck = (f"* cmrr mc {s.tag} {seed} {kind}\n{spice.OPTIONS}.options rshunt=1e12\n{spice.lib('jfets.lib')}"
                f"{spice.lib('opamps.lib')}{spice.lib('bjts.lib')}.model rnl r(noisy=0)\n{src}{net}"
                ".control\n" + spice.WR + "op\nprint v(out)\nac dec 10 1 30meg\nwrdata ac.txt v(out)\n.endc\n.end\n")
        f = spice.run(f"cmrr_mc/{label}/{seed}_{kind}", deck)
        d = spice.read_table(f / "ac.txt")
        res[kind] = (d["frequency"], d["v(out)"])
        if kind == "dm":
            res["vout_dc"] = spice.printed(f, "v(out)")
    fr = res["dm"][0]
    cmrr = 20 * np.log10(np.abs(res["dm"][1]) / np.abs(res["cm"][1]))
    return dict(f=fr, cmrr=cmrr, vout_dc=res["vout_dc"])


def _worker(q, case, seed):
    try:
        r = run_trial(case["label"], case["s"], seed, case["da"], case["only"], case["rs"], case["cnet"],
                      case.get("rup", "R_UP"))
        q.put(("ok", r))
    except Exception as e:  # noqa: BLE001 - reported to the parent
        lines = str(e).splitlines()
        q.put(("error", (lines[1] if len(lines) > 1 else lines[0])[:120]))


def guarded_trial(case: dict, seed: int, timeout: float = 120.0):
    """One trial in a child process: a trial whose operating point does not converge can keep
    ngspice's dynamic gmin stepping busy for hours (seed 5 of L200 with unsorted JFE150 did), and
    the shared library cannot be interrupted from Python.  Returns (result or None, message)."""
    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=_worker, args=(q, case, seed), daemon=True)
    p.start()
    try:
        status, val = q.get(timeout=timeout)
    except queue.Empty:
        p.terminate()
        p.join(5)
        return None, f"no result within {timeout:.0f} s (operating point not found)"
    p.join(5)
    return (val, "") if status == "ok" else (None, val)


def main(args):
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    trials = int(args[0]) if args else 20
    want = args[1:]
    path = spice.RESULTS / "cmrr_mc.json"
    out = json.loads(path.read_text(encoding="utf-8")) if path.exists() and want else {}
    sh, sl, s10 = chain.allocate(1000, "H_LN"), chain.allocate(1000, "L"), chain.allocate(100, "H_HR")

    def case(label, s, da="network", only="", nt=trials, rs=50.0, cnet=0.025, rup="R_UP"):
        return dict(label=label, s=s, da=da, only=only, nt=nt, rs=rs, cnet=cnet, rup=rup)

    cases = [case("H100", sh), case("H10", s10), case("L200", sl), case("H100_discrete", sh, da="discrete")]
    # the same with one class of mismatch at a time (which class limits the CMRR)
    for fe, s0 in (("H100", sh), ("L200", sl)):
        for only in ("jfet", "r", "c"):
            cases.append(case(f"{fe}_only_{only}", s0, only=only, nt=max(trials // 2, 2)))
    # inputs driven directly (0 ohm, the usual condition of a CMRR specification), and with the
    # input-network capacitors trimmed to a residual mismatch of 0.1 % (50-ohm sources)
    for fe, s0 in (("H100", sh), ("L200", sl)):
        cases.append(case(f"{fe}_rs0", s0, rs=0.0))
        cases.append(case(f"{fe}_trimmed", s0, cnet=0.001))
    # the R_UP test: JFET mismatch only, inputs driven directly, R_UP or an ideal I_BS (4 trials)
    cases.append(case(RUP_CASES[0], sh, only="jfet", nt=RUP_TRIALS, rs=0.0))
    cases.append(case(RUP_CASES[1], sh, only="jfet", nt=RUP_TRIALS, rs=0.0, rup="ideal"))
    for c in cases:
        label, s, nt = c["label"], c["s"], c["nt"]
        if want and label not in want:
            continue
        rows = []
        failed = []
        for seed in range(nt):
            r, msg = guarded_trial(c, seed)
            if r is None:                      # no DC solution: counted, reported
                failed.append(seed)
                print(f"{label} seed {seed}: failed ({msg})", flush=True)
                continue
            rows.append([spice.at(r["f"], r["cmrr"], f0) for f0 in FREQ] + [r["vout_dc"]])
        a = np.array(rows)
        extra = dict(only=c["only"], bootstrap_feed=("ideal current source I_BS" if c["rup"] == "ideal"
                                                     else "R_UP")) if label in RUP_CASES else {}
        out[label] = dict(freq=FREQ, gain=s.gain, trials=nt, failed=failed, rs=c["rs"], cnet=c["cnet"], **extra,
                          median=np.median(a[:, :-1], axis=0).tolist(),
                          p10=np.percentile(a[:, :-1], 10, axis=0).tolist(),
                          worst=a[:, :-1].min(axis=0).tolist(),
                          vout_dc_rms=float(np.sqrt(np.mean(a[:, -1] ** 2))),
                          all=a.tolist())
        print(f"{label}: CMRR median " + " ".join(f"{f0:g}:{v:.0f}" for f0, v in zip(FREQ, out[label]['median'])))
        print(f"{label}: CMRR 10 %   " + " ".join(f"{f0:g}:{v:.0f}" for f0, v in zip(FREQ, out[label]['p10'])))
        print(f"{label}: output DC offset rms {out[label]['vout_dc_rms']:.3f} V at gain {s.gain:.0f}", flush=True)
        if all(k in out for k in RUP_CASES) and label in RUP_CASES:
            out["rup_test"] = rup_summary(out)
        path.write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")


def archived_rup_medians(folder: str) -> dict | None:
    """Medians of the CMRR at RUP_FREQ from the archived decks of the first R_UP test (each seed's
    dm and cm ac.txt), or None if they are not there."""
    base = spice.RUNS / "cmrr_mc" / folder
    rows = []
    for seed in range(RUP_TRIALS):
        try:
            dm = spice.read_table(base / f"{seed}_dm" / "ac.txt")
            cm = spice.read_table(base / f"{seed}_cm" / "ac.txt")
        except OSError:
            return None
        c = 20 * np.log10(np.abs(dm["v(out)"]) / np.abs(cm["v(out)"]))
        rows.append([spice.at(dm["frequency"], c, f0) for f0 in RUP_FREQ])
    return dict(freq=RUP_FREQ, median=np.median(np.array(rows), axis=0).tolist(), trials=len(rows))


def rup_summary(out: dict) -> dict:
    """The R_UP test's medians at 10 Hz, 100 Hz and 1 kHz (module docstring)."""
    fe = F.CASES["H100"]
    r_bs = fe.vbs / fe.i_bs
    r_up = (fe.vp - (0.6 + fe.vbs)) / fe.i_bs          # as frontend.side() sizes it
    idx = [FREQ.index(f0) for f0 in RUP_FREQ]
    med = {lab: [out[lab]["median"][i] for i in idx] for lab in RUP_CASES}
    res = dict(freq=RUP_FREQ, trials=RUP_TRIALS, case="H, total gain 1000, JFET mismatch only, inputs driven directly",
               median_R_UP=med[RUP_CASES[0]], median_ideal_I_BS=med[RUP_CASES[1]],
               improvement_dB=[b - a for a, b in zip(med[RUP_CASES[0]], med[RUP_CASES[1]])],
               R_BS=r_bs, R_UP=r_up, R_BS_over_R_UP=r_bs / r_up, f_BS=1 / (2 * math.pi * r_bs * fe.c_bs))
    arch = {lab: archived_rup_medians(RUP_ARCHIVE[lab]) for lab in RUP_CASES}
    if all(arch.values()):
        res["archived_decks"] = {RUP_ARCHIVE[lab]: v["median"] for lab, v in arch.items()}
    print("R_UP test, CMRR medians (dB) at " + ", ".join(f"{f0:g} Hz" for f0 in RUP_FREQ) + ": "
          f"R_UP {[round(v, 1) for v in res['median_R_UP']]}, ideal I_BS {[round(v, 1) for v in res['median_ideal_I_BS']]}, "
          f"improvement {[round(v, 1) for v in res['improvement_dB']]}", flush=True)
    if "archived_decks" in res:
        print("  the same medians from the archived decks of the first test: "
              + ", ".join(f"{k} {[round(v, 1) for v in m]}" for k, m in res["archived_decks"].items()), flush=True)
    print(f"  R_BS / R_UP = {r_bs:.0f} / {r_up:.0f} = {r_bs / r_up:.3f};  f_BS = 1/(2 pi R_BS C_BS) = "
          f"{res['f_BS']:.1f} Hz", flush=True)
    return res


if __name__ == "__main__":
    main(sys.argv[1:])
