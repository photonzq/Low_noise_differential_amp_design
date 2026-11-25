"""The current-feedback JFET front end of the low-noise differential preamplifier, as a netlist
generator, and its test benches.

Topology (per side X = a, b; the two sides are identical):
  - n JFETs in parallel, gates on the input gX (each through an optional gate stopper rg_stop),
    sources on the source node sX (each through an optional source resistor rs_dev)
  - each JFET's drain cascoded by its own NPN (emitter on the drain, collector on the summing
    node cX), whose base sits on the bootstrap node bX: bX is held vbs above the source node by
    R_BS || C_BS fed with I_BS from +V through R_UP, so V_DS of every JFET is constant whatever
    the input voltage (the cascode removes the Miller effect, the bootstrap removes C_gd and the
    channel-length modulation from the common-mode path)
  - the summing node cX is held at vref by an op amp with the integrating capacitor CI from its
    output oX to cX; R_D from +V into cX supplies the JFETs' DC current, so the op amp carries
    only the signal; optional CNODE from cX to ground sets the op amp's high-frequency noise gain
  - the op amp drives the source node through R_F (oX to sX); R_G joins the two source nodes;
    a current sink (NPN with emitter resistor R_T to -V, base on a fixed reference) takes the
    JFETs' and the bootstrap's DC current out of each source node
  Each loop holds its JFETs' drain current constant, so V_GS is constant and the source node
  follows the gate: the differential input appears across R_G, and its current V_d/R_G flows in
  both R_F, so  v_oa - v_ob = (1 + 2 R_F / R_G) (v_a - v_b).  The outputs follow the input's
  common mode with unity gain; the difference amplifier that follows removes it.

Usage:  python frontend.py <case> [checks...]      (cases in CASES, checks: op ac cm noise zin step)
"""
from __future__ import annotations

import json
import math
import re
import sys
from dataclasses import asdict, dataclass, field, replace

import numpy as np

import blocks
import models
import spice


@dataclass
class FE:
    name: str
    jfet: str = "LSK389B"
    n: int = 1                 # JFETs per side
    id: float = 5e-3           # drain current per JFET
    rg_stop: float = 0.0       # gate stopper per JFET (0: none)
    rs_dev: float = 0.0        # source resistor per JFET (0: none)
    cascode: str = "MMBTH10"
    vbs: float = 4.7           # bootstrap: cascode base above the source node
    i_bs: float = 1e-3         # bootstrap current
    c_bs: float = 1e-6
    vref: float = 9.0          # summing-node DC level
    vp: float = 15.0
    vm: float = -15.0
    opamp: str = "THS4021"     # vendor model name, or 'OPN' (behavioural, see opn_kw)
    opn_kw: dict = field(default_factory=dict)
    rf: float = 500.0
    rg: float = 10.1           # gain resistor between the source nodes (0 or None: open)
    ci: float = 1.1e-12        # integrating capacitor, output to own summing node
    cx: float = 0.0            # cross-coupled capacitor, output to the other side's summing node:
                               # the differential loop sees ci - cx, the common-mode loop ci + cx
    cnode: float = 0.0
    sink: str = "MMBT3904"     # source-node current sink: an NPN model, or "J:<subckt>" for an N-JFET
    v_sink: float = 2.0        # voltage across the sink's emitter (source) resistor R_T
    v_be_sink: float = 0.66    # the sink's base-emitter (gate-source) voltage: where the reference's adjustment
                               # (sink_reference), or the servo, starts: V_M + V_RT + v_be_sink
    cm_servo: bool = False     # True: a slow servo of the sinks' reference (Appendix B of the note); False: the
                               # reference is a fixed voltage, v_ref_sink, adjusted once (sink_reference)
    oa_rail: float = 0.0       # 0: the loop op amps run on vp/vm; > 0: on their own +/- oa_rail (nodes
                               # vpa, vma), for a low-voltage op amp (Section 4.3, the low-voltage option)
    r_in: float = 1e-3         # the noiseless resistors that tie the sources to the gates (RIA, RIB); 1 ohm
                               # where 1 mOhm with abstol = 1e-15 A defeats ngspice's operating point and it
                               # falls back to its transient op (sink_options.py; the note's Appendix)
    v_ref_sink: float | None = None   # the sinks' fixed base reference (vsink0), V; None: the adjusted value
                                      # (sink_reference); not used with cm_servo
    bjt: str = ""              # "" (the designs of the note): the input devices are the JFET subcircuits `jfet`;
                               # otherwise an NPN model name, and the input devices are that BJT (collector on the
                               # cascode, emitter on the source node), for the bipolar input stage of Section 3.5
    extra_lib: str = ""        # a further model library under sim/models/_lib (the calibrated bipolar cards)

    @property
    def device(self) -> str:
        return self.bjt or self.jfet

    @property
    def extra(self) -> str:
        return spice.lib(self.extra_lib) if self.extra_lib else ""

    @property
    def oa_rails(self) -> str:
        return "vpa vma" if self.oa_rail else "vp vm"

    @property
    def gain(self) -> float:
        return 1 + 2 * self.rf / self.rg if self.rg else 1.0


def bjt_lib() -> str:
    """Generic small-signal BJT cards from LTspice's standard.bjt (by name)."""
    import re
    raw = models.LTSPICE_BJT_LIB.read_bytes()
    try:
        text = raw.decode("utf-16")
    except UnicodeError:
        text = raw.decode("latin-1")
    out = []
    for name in ("BC847B", "BC857B", "2N3904", "2N3906", "BC817-25", "BC807-25"):
        for line in text.splitlines():
            m = re.match(r"\s*\.model\s+(\S+)\s+(NPN|PNP)\s*\((.*)\)\s*$", line, re.I)
            if m and m.group(1).upper() == name.upper():
                params = re.sub(r"\b(vceo|icrating|mfg)\s*=\s*\S+", "", m.group(3), flags=re.I)
                out.append(f".model {name} {m.group(2)}({' '.join(params.split())})")
    return "\n".join(out) + "\n"


def side(p: FE, x: str) -> str:
    """One side's netlist (x = 'a' or 'b')."""
    g, s, c, b, o = f"g{x}", f"s{x}", f"c{x}", f"b{x}", f"o{x}"
    lines = [f"* --- side {x}"]
    for k in range(1, p.n + 1):
        gk = f"{g}{k}" if p.rg_stop else g
        sk = f"{s}{k}" if p.rs_dev else s
        dk = f"d{x}{k}"
        if p.rg_stop:
            lines.append(f"RGS{x}{k} {g} {gk} {p.rg_stop:g}")
        if p.rs_dev:
            lines.append(f"RSS{x}{k} {sk} {s} {p.rs_dev:g}")
        if p.bjt:
            lines.append(f"QJ{x}{k} {dk} {gk} {sk} {p.bjt}")
        else:
            lines.append(f"XJ{x}{k} {dk} {gk} {sk} {p.jfet}")
        if p.cascode.startswith("J:"):          # JFET cascode (no gate current, no base-current noise)
            lines.append(f"XC{x}{k} {c} {b} {dk} {p.cascode[2:]}")
        else:
            lines.append(f"QC{x}{k} {c} {b} {dk} {p.cascode}")
    # bootstrap: R_BS || C_BS from the base node to the source node, I_BS from +V via R_UP
    r_bs = p.vbs / p.i_bs
    v_b0 = (-0.65 if p.bjt else 0.6) + p.vbs   # base node at the source node + vbs (zero input): the JFETs' source
                                                # about 0.6 V above the gate, an NPN's emitter about 0.65 V below
    r_up = (p.vp - v_b0) / p.i_bs
    lines += [f"RBS{x} {b} {s} {r_bs:.6g}", f"CBS{x} {b} {s} {p.c_bs:g}",
              f"RUP{x} vp {b} {r_up:.6g}"]
    # summing node: R_D from +V, op amp, integrator
    i_tot = p.n * p.id
    r_d = (p.vp - p.vref) / i_tot
    lines += [f"RD{x} vp {c} {r_d:.6g}", f"CI{x} {o} {c} {p.ci:g}"]
    if p.cx:
        other = "b" if x == "a" else "a"
        lines.append(f"CX{x} o{other} {c} {p.cx:g}")
    if p.cnode:
        lines.append(f"CN{x} {c} 0 {p.cnode:g}")
    lines.append(f"XU{x} vref {c} {o} {p.oa_rails} {opamp_name(p)}")
    lines.append(f"RF{x} {o} {s} {p.rf:g}")
    # current sink: the JFETs' current plus the bootstrap current
    i_sink = i_tot + p.i_bs
    r_t = p.v_sink / i_sink
    if p.sink.startswith("J:"):        # JFET sink: no base current, so no base-current shot noise
        lines += [f"XT{x} {s} vsink e{x} {p.sink[2:]}", f"RT{x} e{x} vm {r_t:.6g}"]
    else:
        lines += [f"QT{x} {s} vsink e{x} {p.sink}", f"RT{x} e{x} vm {r_t:.6g}"]
    return "\n".join(lines) + "\n"


def opamp_name(p: FE) -> str:
    return "OPN_FE" if p.opamp == "OPN" else f"OA_{p.opamp}"


def netlist(p: FE) -> str:
    """Front end with inputs ga, gb and outputs oa, ob; supplies vp, vm; references vref, vsink."""
    head = (f"* ===== front end {p.name}: {p.n} x {p.device} per side at {p.id * 1e3:g} mA, R_F {p.rf:g}, "
            f"R_G {p.rg:g}, gain {p.gain:.4g}\n")
    rg = f"RG sa sb {p.rg:g}\n" if p.rg else ""
    # sink base reference: vm + v_sink + V_BE (ideal source, filtered)
    refs = (f"VP vp 0 DC {p.vp:g}\nVM vm 0 DC {p.vm:g}\n"
            + (f"VPA vpa 0 DC {p.oa_rail:g}\nVMA vma 0 DC {-p.oa_rail:g}\n" if p.oa_rail else "")
            + f"VREF vref0 0 DC {p.vref:g}\nRREF vref0 vref 1k rnl\nCREF vref 0 10u\n")
    v0 = p.vm + p.v_sink + p.v_be_sink
    if p.cm_servo:
        # common-mode DC servo (ideal integrator, crossover well below 1 Hz): drives the sinks'
        # base reference so that the mean DC current in the two R_F is zero (the outputs' mean
        # equals the sources' mean); in a build, a precision op-amp integrator
        # The servo's output is clamped to vm + 1 ... vm + v_sink + 3 V (vm + 5 V with the 2 V of
        # R_T of the adopted design).  The clamp bounds the sinks' current, and R_T's dissipation,
        # during start-up and overloads; the loop does not need it to be stable: its error has a
        # single zero, with the restoring sign everywhere else, also with the sinks saturated
        # (servo_check.py; the latched state that an early version reported is not reproduced).
        refs += ("BERR nerr 0 V=(V(oa)+V(ob)-V(sa)-V(sb))/2\nGINT 0 nint nerr 0 1e-6\nCINT nint 0 1u\n"
                 f"RINT nint 0 1e12 rnl\nBSNK vsink0 0 V=max(min({v0:g}-V(nint), {p.vm + p.v_sink + 3:g}), {p.vm + 1:g})\n"
                 "RSNK vsink0 vsink 1k rnl\nCSNK vsink 0 10u\n")
    else:
        # the sinks' base reference: a fixed voltage, adjusted once so that the sinks take the JFETs' and
        # the bootstrap's current (sink_reference), through the same 1 kOhm and 10 uF filter
        v_ref = p.v_ref_sink if p.v_ref_sink is not None else sink_reference(p)
        refs += f"VSNK vsink0 0 DC {v_ref:.9g}\nRSNK vsink0 vsink 1k rnl\nCSNK vsink 0 10u\n"
    return head + refs + side(p, "a") + side(p, "b") + rg


def ties(src: str, p: FE) -> str:
    """The source text with its gate ties (RIA, RIB: 1 mOhm, noiseless) at p.r_in."""
    if p.r_in == 1e-3:
        return src
    return re.sub(r"^(RI[AB] \S+ \S+) 1m rnl$", rf"\g<1> {p.r_in:g} rnl", src, flags=re.M)


# what op_checked tries, in turn: (label, OPTIONS replacement or None, gate ties r_in or None)
OP_LADDER = (("as given", None, None),
             ("abstol = 1e-12 A", ("abstol=1e-15", "abstol=1e-12"), None),
             ("1-ohm ties", None, 1.0),
             ("abstol = 1e-12 A and 1-ohm ties", ("abstol=1e-15", "abstol=1e-12"), 1.0))


def op_checked(fn, p: FE, *args, keep=None, **kw) -> tuple:
    """fn(p, *args, **kw) with the operating points of its decks checked.  When gmin and source stepping
    both fail, ngspice-46 falls back to a transient op, a 10 us transient whose end state need not be a DC
    solution, and notes it only in the log (spice.op_fallback, spice.FALLBACKS); Section 5.1 and Appendix A
    of the note.  If any deck of the call fell back, fn runs again with abstol = 1e-12 A instead of 1e-15 A,
    then with the sources tied to the gates through 1 ohm instead of 1 mOhm (FE.r_in, noiseless), then
    with both (OP_LADDER).  Returns (result, label, note) of the first call in which no deck fell back:
    the label of its OP_LADDER step, and a note of the decks that fell back before ('' if none did).  A
    RuntimeError of fn is re-raised unless a deck of that call fell back; a fallback in every step raises
    RuntimeError.  keep(result) gives run folders (relative to spice.RUNS, '/'-separated) whose fallback
    the caller has handled itself (gain_options.noise_checked reruns a noise deck from .nodeset)."""
    import contextlib
    notes = []
    for label, opt, r_in in OP_LADDER:
        q = replace(p, r_in=r_in) if r_in else p
        n0 = len(spice.FALLBACKS)
        try:
            with (spice.options_replaced(*opt) if opt else contextlib.nullcontext()):
                r, err = fn(q, *args, **kw), None
        except RuntimeError as exc:
            r, err = None, exc
        bad = sorted({f.relative_to(spice.RUNS).as_posix() for f in spice.FALLBACKS[n0:]}
                     - (set(keep(r)) if keep is not None and r is not None else set()))
        if not bad:
            if err is not None:
                raise err
            return r, label, "; ".join(notes)
        notes.append(f"{label}: {', '.join(bad)} fell back to ngspice's transient op")
    raise RuntimeError(f"{p.name}: " + "; ".join(notes))


def deck(p: FE, title: str, src: str, control: str) -> str:
    opn = blocks.opn("OPN_FE", **p.opn_kw) if p.opamp == "OPN" else ""
    return (f"* {title}\n{spice.OPTIONS}.options rshunt=1e12\n{spice.lib('jfets.lib')}{spice.lib('opamps.lib')}"
            f"{spice.lib('bjts.lib')}{p.extra}{opn}{blocks.COMMON}{ties(src, p)}{netlist(p)}{control}.end\n")


SRC_DM = "VA ina 0 DC 0 AC 0.5\nVB inb 0 DC 0 AC -0.5\nRIA ina ga 1m rnl\nRIB inb gb 1m rnl\n"
SRC_CM = "VA ina 0 DC 0 AC 1\nRIA ina ga 1m rnl\nRIB ina gb 1m rnl\n"
SRC_NOISE = "VIN ina 0 DC 0 AC 1\nRIA ina ga 1m rnl\nRIB 0 gb 1m rnl\n"

# the sinks' adjusted reference of each circuit (sink_reference), in memory and on disk
_REF: dict = {}
REF_FILE = spice.RESULTS / "sink_reference.json"


def _ref_key(p: FE) -> str:
    """The circuit a reference is adjusted for: the netlist without its name and reference value, and the
    model libraries it includes, so that a change of either is a new circuit."""
    import hashlib
    h = hashlib.sha256(netlist(replace(p, name="ref", cm_servo=False, v_ref_sink=0.0, v_be_sink=0.0)).encode())
    for lib in ("jfets.lib", "opamps.lib", "bjts.lib") + ((p.extra_lib,) if p.extra_lib else ()):
        h.update((spice.LIB / lib).read_bytes())
    return h.hexdigest()[:20]


def sink_reference(p: FE) -> float:
    """The sinks' base reference at which they take exactly the JFETs' and the bootstrap's current, so that
    no DC current flows in R_F and the outputs sit at their sources, e = [(v_oa - v_sa) + (v_ob - v_sb)] / 2
    = 0 (Section 4.2 of the note): the adjustment a build makes once, here by secant steps between
    operating points at zero input and 27 C, from V_M + V_RT + v_be_sink and 50 mV above, until
    |e| < 1 uV.  The inputs are tied through 1 ohm (DC as with 1 mOhm), and abstol is 1e-12 A for a deck
    whose operating point falls back to the transient op.  Cached by circuit (_ref_key)."""
    key = _ref_key(p)
    if key in _REF:
        return _REF[key]["v_ref"]
    disk = json.loads(REF_FILE.read_text(encoding="utf-8")) if REF_FILE.exists() else {}
    if key in disk:
        _REF[key] = disk[key]
        return disk[key]["v_ref"]
    q = replace(p, cm_servo=False, r_in=1.0)
    ctl = ".control\n" + spice.WR + "op\nprint v(oa) v(ob) v(sa) v(sb)\n.endc\n"

    def e_at(x: float, k: int) -> float:
        text = deck(replace(q, v_ref_sink=x), f"sink reference {p.name} {x:.9g}", SRC_DM, ctl)
        f = spice.run(f"sink_ref/{p.name}/{k}", text)
        if spice.op_fallback(f):
            f = spice.run(f"sink_ref/{p.name}/{k}", text.replace("abstol=1e-15", "abstol=1e-12"))
            if spice.op_fallback(f):
                raise RuntimeError(f"{p.name}: the operating point at a sink reference of {x:.4f} V fell back")
        v = {n: spice.printed(f, f"v({n})") for n in ("oa", "ob", "sa", "sb")}
        return ((v["oa"] - v["sa"]) + (v["ob"] - v["sb"])) / 2

    design = p.vm + p.v_sink + p.v_be_sink
    x0, x1 = design, design + 0.05
    e0, e1 = e_at(x0, 0), e_at(x1, 1)
    k = 2
    while abs(e1) > 1e-6 and k < 12:
        x0, e0, x1 = x1, e1, x1 - e1 * (x1 - x0) / (e1 - e0)
        e1 = e_at(x1, k)
        k += 1
    if abs(e1) > 1e-6:
        raise RuntimeError(f"{p.name}: the sink reference did not converge (e = {e1:.3g} V at {x1:.6f} V)")
    rec = dict(v_ref=x1, e=e1, operating_points=k, case=p.name, design_value=design)
    _REF[key] = rec
    disk = json.loads(REF_FILE.read_text(encoding="utf-8")) if REF_FILE.exists() else {}
    disk[key] = rec
    models._atomic_write(REF_FILE, json.dumps(disk, indent=1, sort_keys=True), "utf-8")
    return x1


def check_op(p: FE) -> dict:
    ctl = (".control\n" + spice.WR + "op\n"
           "print v(ga) v(sa) v(sb) v(ba) v(da1) v(ca) v(cb) v(oa) v(ob)\n"
           "print @j.xja1.j1[id] @j.xjb1.j1[id] @j.xja1.j1[gm] @q.xua.x1.q1[ic]\n.endc\n")
    try:
        f = spice.run(f"fe/{p.name}/op", deck(p, f"op {p.name}", SRC_DM, ctl), allow=(r"q\.xua",))
    except RuntimeError as exc:
        return dict(error=str(exc)[:400])
    keys = ["v(sa)", "v(sb)", "v(ba)", "v(da1)", "v(ca)", "v(cb)", "v(oa)", "v(ob)",
            "@j.xja1.j1[id]", "@j.xjb1.j1[id]", "@j.xja1.j1[gm]"]
    out = {}
    for k in keys:
        try:
            out[k] = spice.printed(f, k)
        except KeyError:
            pass
    return out


def check_ac(p: FE) -> dict:
    ctl = ".control\n" + spice.WR + "ac dec 40 1 1g\nwrdata ac.txt v(oa) v(ob)\n.endc\n"
    f = spice.run(f"fe/{p.name}/ac", deck(p, f"ac {p.name}", SRC_DM, ctl))
    d = spice.read_table(f / "ac.txt")
    fr, h = d["frequency"], d["v(oa)"] - d["v(ob)"]
    mag = np.abs(h)
    peak = float(20 * np.log10(mag.max() / mag[0]))
    return dict(gain_dc=float(mag[0]), gain_1k=spice.at(fr, mag, 1e3), f3db=spice.f3db(fr, mag),
                peak_db=peak, g10M_db=float(20 * math.log10(spice.at(fr, mag, 10e6) / mag[0])),
                curve=(fr, h))


def check_cm(p: FE) -> dict:
    ctl = ".control\n" + spice.WR + "ac dec 20 1 1g\nwrdata cm.txt v(oa) v(ob)\n.endc\n"
    f = spice.run(f"fe/{p.name}/cm", deck(p, f"cm {p.name}", SRC_CM, ctl))
    d = spice.read_table(f / "cm.txt")
    fr = d["frequency"]
    return dict(cm_out=(fr, (d["v(oa)"] + d["v(ob)"]) / 2), dm_from_cm=(fr, d["v(oa)"] - d["v(ob)"]))


def check_noise(p: FE, fstop=100e6) -> dict:
    f = spice.run(f"fe/{p.name}/noise",
                  deck(p, f"noise {p.name}", SRC_NOISE,
                       ".control\n" + spice.WR + f"noise v(oa,ob) VIN dec 20 0.1 {fstop:g} 1\nsetplot noise1\n"
                       "wrdata noise.txt all\n.endc\n"))
    nz = spice.read_noise(f)
    fr, inn = nz["frequency"], nz["inoise_spectrum"]
    return dict(f=fr, inn=inn, nz=nz,
                en={str(f0): spice.at(fr, inn, f0) for f0 in (1, 10, 100, 1e3, 1e4, 1e5, 1e6, 1e7)})


NOISE_GROUPS = [
    ("input JFETs", [r"^j\.xj[ab]\d+\.j1", r"^r\.xj[ab]\d+\.rx$", r"^qj[ab]\d+$"]),   # the last: bipolar inputs
    ("gate stoppers and source resistors", [r"^rgs[ab]\d+$", r"^rss[ab]\d+$"]),
    ("R_G", [r"^rg$"]),
    ("R_F", [r"^rf[ab]$"]),
    ("cascodes", [r"^q\.?c[ab]\d+$", r"^qc[ab]\d+$", r"^j\.xc[ab]\d+\.j1", r"^r\.xc[ab]\d+\.rx$"]),
    ("bootstrap (R_BS, R_UP)", [r"^rbs[ab]$", r"^rup[ab]$"]),
    ("drain-side R_D", [r"^rd[ab]$"]),
    ("current sinks", [r"^qt[ab]$", r"^rt[ab]$", r"^j\.xt[ab]\.j1", r"^r\.xt[ab]\.rx$"]),
    ("loop op amps", [r"^.*\.xu[ab]\."]),
]


def noise_groups(nz: dict, gain: np.ndarray) -> dict:
    """Input-referred density of each group of generators (gain: |H| on the noise grid)."""
    import re as _re
    fr = nz["frequency"]
    acc = {g: np.zeros_like(fr) for g, _ in NOISE_GROUPS}
    other = {}
    for name, v in nz.items():
        if not name.startswith("onoise_") or name == "onoise_spectrum":
            continue
        base = name[len("onoise_"):]
        if _re.search(r"_(1overf|thermal|rs|rd|id|flicker|1overfsw|idsw|rsw|rb|ib|ic|rc|re)$", base):
            continue
        for g, pats in NOISE_GROUPS:
            if any(_re.match(pt, base) for pt in pats):
                acc[g] += v ** 2
                break
        else:
            other[base] = v
    out = {g: np.sqrt(v) / gain for g, v in acc.items()}
    if other:
        out["other"] = np.sqrt(sum(v ** 2 for v in other.values())) / gain
    return out


def check_loop(p: FE, mode: str = "dm") -> dict:
    """Loop gain by Middlebrook's double injection at side a's R_F (between oa and R_F).  In
    'dm' mode side b is driven in antiphase by the same injections (mirror), so the loop seen is
    the differential one; in 'cm' mode in phase."""
    res = {}
    for inj in ("v", "i"):
        q = replace(p)
        text = netlist(q)
        # break both R_F: oX -- [Vinj] -- fX -- R_F -- sX, current injection into fX
        sgn = -1 if mode == "dm" else 1
        text = text.replace(f"RFa oa sa {p.rf:g}", f"VJa oa fa DC 0 AC {1 if inj == 'v' else 0}\n"
                                                    f"IJa 0 fa DC 0 AC {1 if inj == 'i' else 0}\nRFa fa sa {p.rf:g}")
        text = text.replace(f"RFb ob sb {p.rf:g}", f"VJb ob fb DC 0 AC {sgn if inj == 'v' else 0}\n"
                                                    f"IJb 0 fb DC 0 AC {sgn if inj == 'i' else 0}\nRFb fb sb {p.rf:g}")
        opn = blocks.opn("OPN_FE", **p.opn_kw) if p.opamp == "OPN" else ""
        dk = (f"* loop {p.name} {mode} {inj}\n{spice.OPTIONS}.options rshunt=1e12\n{spice.lib('jfets.lib')}"
              f"{spice.lib('opamps.lib')}{spice.lib('bjts.lib')}{p.extra}{opn}{blocks.COMMON}"
              + ties("VA ina 0 DC 0\nRIA ina ga 1m rnl\nRIB ina gb 1m rnl\n", p) + text +
              ".control\n" + spice.WR + "ac dec 40 1k 2g\nwrdata loop.txt v(oa) v(fa) i(VJa)\n.endc\n.end\n")
        f = spice.run(f"fe/{p.name}/loop_{mode}_{inj}", dk)
        res[inj] = spice.read_table(f / "loop.txt")
    fr = res["v"]["frequency"]
    # voltage injection: Tv = -v(oa)/v(fa); current injection: Ti = -i_back/i_fwd
    tv = -res["v"]["v(oa)"] / res["v"]["v(fa)"]
    # with the current injection, i(VJa) flows from oa into fa (op-amp side) ; the current into
    # R_F is i(VJa) + 1, so Ti = i_return / i_forward = i(VJa) / (-(i(VJa) + 1))  (Middlebrook)
    ivj = res["i"]["i(VJa)"]
    ti = -ivj / (ivj + 1.0)
    t = (tv * ti - 1) / (tv + ti + 2)
    mag = np.abs(t)
    idx = np.where(mag < 1)[0]
    if len(idx) == 0 or idx[0] == 0:
        return dict(T=(fr, t), fc=float("nan"), pm=float("nan"))
    i = idx[0]
    fc = fr[i]
    pm = 180 + math.degrees(np.angle(t[i]))
    # gain margin: |T| where the phase crosses -180 after crossover
    ph = np.unwrap(np.angle(t))
    gm = float("nan")
    for j in range(i, len(fr) - 1):
        if ph[j] > -math.pi >= ph[j + 1] or ph[j] < -math.pi <= ph[j + 1]:
            gm = -20 * math.log10(mag[j])
            break
    return dict(T=(fr, t), fc=float(fc), pm=float(pm), gm_db=gm, t_1k=float(mag[0]))


def _margins(fr, t) -> dict:
    """Crossovers and margins of a return ratio: every crossing of |T| = 1 with its phase margin,
    and the gain margin at every -180 degree crossing while |T| < 1 (the first point of the sweep
    past each crossing, as in check_loop)."""
    mag = np.abs(t)
    ph = np.degrees(np.unwrap(np.angle(t)))
    xs = [dict(f=float(fr[j + 1]), pm=float(180 + ph[j + 1])) for j in range(len(fr) - 1)
          if mag[j] >= 1 > mag[j + 1]]
    gms = []
    for j in range(len(fr) - 1):
        for k in range(-3, 4):
            lvl = -180 + 360 * k
            if (ph[j] - lvl) * (ph[j + 1] - lvl) <= 0 and ph[j] != ph[j + 1] and mag[j + 1] < 1:
                gms.append(dict(f=float(fr[j + 1]), gm_db=float(-20 * math.log10(mag[j + 1]))))
    return dict(crossings=xs, gain_margins=gms,
                pm=min((x["pm"] for x in xs), default=float("nan")),
                gm_db=min((g["gm_db"] for g in gms), default=float("nan")))


def loop_out_deck(p: FE, mode: str, inj: str, control: str) -> str:
    """check_loop_out's deck for one injection (inj 'v' or 'i'), with the given control block: both gates
    tied to ground (through p.r_in), and each op amp's output pin broken by a voltage source VJx (DC 0) with
    a current source IJx (DC 0) into its output node; side b's injection in antiphase in 'dm' mode."""
    sgn = -1 if mode == "dm" else 1
    text = netlist(p)
    for x, s in (("a", 1), ("b", sgn)):
        old = f"XU{x} vref c{x} o{x} {p.oa_rails} {opamp_name(p)}"
        assert old in text, old
        text = text.replace(old, f"XU{x} vref c{x} u{x} {p.oa_rails} {opamp_name(p)}\n"
                                 f"VJ{x} u{x} o{x} DC 0 AC {s if inj == 'v' else 0}\n"
                                 f"IJ{x} 0 o{x} DC 0 AC {s if inj == 'i' else 0}")
    opn = blocks.opn("OPN_FE", **p.opn_kw) if p.opamp == "OPN" else ""
    return (f"* loop at op-amp output {p.name} {mode} {inj}\n{spice.OPTIONS}.options rshunt=1e12\n"
            f"{spice.lib('jfets.lib')}{spice.lib('opamps.lib')}{spice.lib('bjts.lib')}{p.extra}{opn}{blocks.COMMON}"
            + ties("VA ina 0 DC 0\nRIA ina ga 1m rnl\nRIB ina gb 1m rnl\n", p) + text + control + ".end\n")


def check_loop_out(p: FE, mode: str = "dm") -> dict:
    """Return ratio at the op amp's output pin, by Middlebrook's double injection: each op amp's
    output (driving C_I, C_X and R_F) is the one point that both the outer loop (through the
    JFETs) and the op amp's own local loop (through C_I and C_X to its inverting input) pass
    through, so this break shows an instability of either.  check_loop breaks only R_F, i.e. the
    outer loop with the local loop closed, and cannot see a local-loop instability.  In 'dm' mode
    side b is injected in antiphase, in 'cm' mode in phase."""
    res = {}
    for inj in ("v", "i"):
        dk = loop_out_deck(p, mode, inj, ".control\n" + spice.WR +
                           "ac dec 50 1k 3g\nwrdata loop.txt v(ua) v(oa) i(VJa)\n.endc\n")
        f = spice.run(f"fe/{p.name}/loopout_{mode}_{inj}", dk)
        res[inj] = spice.read_table(f / "loop.txt")
    fr = res["v"]["frequency"]
    tv = -res["v"]["v(ua)"] / res["v"]["v(oa)"]
    ivj = res["i"]["i(VJa)"]
    ti = -ivj / (ivj + 1.0)
    t = (tv * ti - 1) / (tv + ti + 2)
    return dict(T=(fr, t), **_margins(fr, t))


SOURCES = {
    # name: per-input source network from the generator node (ina / inb) to the gate (ga / gb)
    "50ohm": "RSA ina ga 50\nRSB inb gb 50\n",
    "1k": "RSA ina ga 1k\nRSB inb gb 1k\n",
    "1Meg": "RSA ina ga 1Meg\nRSB inb gb 1Meg\n",
    "50ohm_1uH": "RSA ina na 50\nLSA na ga 1u\nRSB inb nb 50\nLSB nb gb 1u\n",
    # 1 m of 50-ohm coaxial cable (5 ns), driven through 1 Meg at the far end: an open cable
    "cable1m_open": "RSA ina na 1Meg\nTA na 0 ga 0 Z0=50 TD=5n\nRSB inb nb 1Meg\nTB nb 0 gb 0 Z0=50 TD=5n\n",
    "cable3m_open": "RSA ina na 1Meg\nTA na 0 ga 0 Z0=50 TD=15n\nRSB inb nb 1Meg\nTB nb 0 gb 0 Z0=50 TD=15n\n",
}


def check_sources(p: FE, names=None, extra_net: str = "") -> dict:
    """Differential response from the generator to the output with each source network of
    SOURCES (DM drive), and the largest peak above the low-frequency gain.  A peak far above the
    source's own resonance flags a pole pair near the axis (a passive source cannot do that)."""
    out = {}
    for nm in names or SOURCES:
        src = ("VA ina 0 DC 0 AC 0.5\nVB inb 0 DC 0 AC -0.5\nRBA ga 0 100Meg rnl\nRBB gb 0 100Meg rnl\n"
               + SOURCES[nm] + extra_net)
        ctl = ".control\n" + spice.WR + "ac dec 50 10 1g\nwrdata ac.txt v(oa) v(ob)\n.endc\n"
        f = spice.run(f"fe/{p.name}/src_{nm}", deck(p, f"source {nm}", src, ctl))
        d = spice.read_table(f / "ac.txt")
        fr, h = d["frequency"], np.abs(d["v(oa)"] - d["v(ob)"])
        i = int(np.argmax(h))
        out[nm] = dict(f=fr, h=h, peak_db=float(20 * np.log10(h[i] / h[0])), f_peak=float(fr[i]))
    return out


def check_zin(p: FE) -> dict:
    """Input impedance of input a, with input b grounded (differential drive of one input), and
    with both inputs driven together (common mode): AC current 1 A into the input node."""
    out = {}
    for mode, src in (("dm", "IA 0 ga DC 0 AC 1\nRIB 0 gb 1m rnl\nRBIAS ga 0 1e12 rnl\n"),
                      ("cm", "IA 0 ga DC 0 AC 1\nRIB ga gb 1m rnl\nRBIAS ga 0 1e12 rnl\n")):
        ctl = ".control\n" + spice.WR + "ac dec 20 10 1g\nwrdata zin.txt v(ga)\n.endc\n"
        f = spice.run(f"fe/{p.name}/zin_{mode}", deck(p, f"zin {p.name} {mode}", src, ctl))
        d = spice.read_table(f / "zin.txt")
        fr, z = d["frequency"], d["v(ga)"]
        # effective parallel capacitance: Im(1/Z) / omega
        c_eff = np.imag(1 / z) / (2 * np.pi * fr)
        out[mode] = dict(f=fr, z=z, c_eff=c_eff)
    return out


# The designs of the note.  H: two JFE2140 per side (one from each of two duals), 5 mA each;
# R_G switched between 111 ohm (gain 10) and 10.1 ohm (gain 100); a 4 pF capacitor per side is
# moved by the same relay between the cross position (gain 100: CI 9 pF, CX 5 pF) and the
# integrator position (gain 10: CI 13 pF, CX 1 pF).  L: twelve JFE150 per side, 5 mA each,
# R_F 249 ohm, R_G 2.49 ohm (gain 201).  Both: BF862-class JFET cascodes (LSBF862 card),
# bootstrap 3.5 V, THS4021 loop op amps on +/-15 V, summing nodes at +9 V.
# CNODE (summing node to ground) keeps the THS4021's own loop stable: in common mode its feedback
# capacitance is CI + CX, and the op amp needs a high-frequency noise gain of about 10 or more
# (1 + CNODE / (CI + CX)); without CNODE the common-mode loop oscillated near 280 MHz in a
# transient run (osc_check.py), which neither the AC response nor the loop gain at R_F revealed.
# The values come from comp_search.py (margins at the op amp's output pin, check_loop_out).
# Earlier values without CNODE (unstable): H10 CI 9.19 / CX 1.42 pF, H100 6.19 / 4.42 pF, L200
# 13.4 / 7.8 pF.
H_COMMON = dict(jfet="JFE2140", n=2, id=5e-3, rf=500.0, cascode="J:LSBF862", vbs=3.5, cnode=220e-12)
CASES = {
    "H10": FE("H10", rg=111.0, ci=13e-12, cx=1e-12, **H_COMMON),
    "H100": FE("H100", rg=10.1, ci=9e-12, cx=5e-12, **H_COMMON),
    # L's sinks carry 62 mA each: PZT3904 (SOT-223) with 6 V across R_T, so that the transistor
    # takes 0.59 W and R_T 0.38 W (Section 4.2.1 of the note; the first design, an MMBT3904 with
    # 2 V, put 0.84 W into a SOT-23)
    "L200": FE("L200", jfet="JFE150", n=12, id=5e-3, rf=249.0, rg=2.49, cascode="J:LSBF862", vbs=3.5,
               ci=22e-12, cx=8e-12, cnode=470e-12, sink="PZT3904", v_sink=6.0),
    "H_lsk389": FE("H_lsk389", ci=5.5e-12, cx=4.4e-12),
}


def main(args):
    sys.stdout.reconfigure(encoding="utf-8")
    models.prepare()
    name = args[0] if args else "H100"
    p = CASES[name]
    checks = args[1:] or ["op", "ac", "noise"]
    print(f"{p.name}: gain {p.gain:.4g}")
    if "op" in checks:
        print("op", json.dumps(check_op(p), indent=1))
    if "ac" in checks:
        r = check_ac(p)
        print("ac", {k: v for k, v in r.items() if k != "curve"})
    if "noise" in checks:
        r = check_noise(p)
        print("noise", {k: f"{v * 1e9:.3f} nV" for k, v in r["en"].items()})


if __name__ == "__main__":
    main(sys.argv[1:])
