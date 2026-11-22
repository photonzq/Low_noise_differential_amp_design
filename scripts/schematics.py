"""Schematic drawing with a check against the simulated netlists.

Sch extends schematic_style.Sheet (the drawing style shared with the HV-amplifier and photodiode-
amplifier notes) with a registry of every electrical wire, part pin, junction dot and net tie.
From that registry the drawing's nets are rebuilt from its geometry alone (wires, T junctions,
pins, ground and rail symbols, off-sheet labels), and

  check_geometry   lists missing or superfluous junction dots, four-way junctions, wire crossings
                   (reported, allowed), wires that run over a two-terminal part or through a
                   transistor body, and pins that connect to nothing;
  check_netlist    compares the drawing with the netlist the simulations use: every drawn part
                   must exist in the netlist under the same name with the same value (0.5 %) and
                   model, every drawn net must correspond to exactly one netlist node (through
                   the part pins and the net ties), and two drawn nets may share a netlist node
                   only if both carry a tie to it (an off-sheet connection).  Netlist parts of the
                   sheet's scope that are not drawn are listed.
The geometry functions are those of the HV-amplifier note's make_schematics.py.
"""
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict

import schemdraw.elements as elm

import schematic_style as ss

OHM, MU, MINUS = "Ω", "µ", "−"
TOL = 2e-3


def fmt_r(v: float) -> str:
    if v >= 1e6:
        return f"{v / 1e6:.3g} M{OHM}"
    return f"{v / 1e3:.3g} k{OHM}" if v >= 1e3 else f"{v:.3g} {OHM}"


def fmt_c(v: float) -> str:
    for scale, pre in ((1e-6, MU), (1e-9, "n"), (1e-12, "p")):
        if v >= 0.999 * scale:
            return f"{v / scale:.3g} {pre}F"
    return f"{v * 1e15:.3g} fF"


def volts_text(v: float) -> str:
    return ("+" if v > 0 else (MINUS if v < 0 else "")) + f"{abs(v):g} V"


def P(p):
    return (round(float(p[0]), 4), round(float(p[1]), 4))


class Sch(ss.Sheet):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.comps: dict[str, dict] = {}
        self.wires: list[tuple] = []
        self.ties: list[tuple] = []
        self.dots: list[tuple] = []
        self._pts: list[tuple] = []

    def _snap(self, p):
        p = P(p)
        for q in self._pts:
            if abs(q[0] - p[0]) <= TOL and abs(q[1] - p[1]) <= TOL:
                return q
        self._pts.append(p)
        return p

    def text(self, p, s, ha="left", va="center", color=None, size=ss.FONT_SIZE):
        self.add(elm.Label().right().at(p).label(s, fontsize=size, color=color or ss.COLORS["text"],
                                                 halign=ha, valign=va, ofst=(-0.1, -0.1)))

    def wire(self, *pts, color=None, dashed=False, lw=None):
        super().wire(*pts, color=color, dashed=dashed, lw=lw)
        for a, b in zip(pts[:-1], pts[1:]):
            self.wires.append((self._snap(a), self._snap(b)))

    def line(self, *pts, color=None, dashed=False):
        ss.Sheet.wire(self, *pts, color=color, dashed=dashed)

    def dot(self, p, color=None):
        self.dots.append(self._snap(p))
        return super().dot(p, color)

    def _reg(self, ref, kind, pins, **kw):
        if ref in self.comps:
            raise ValueError(f"{self.name}: {ref} drawn twice")
        self.comps[ref] = dict(kind=kind, pins={k: self._snap(v) for k, v in pins.items()}, **kw)

    def R(self, ref, value, p1, p2, side=None, text=None, show=None, dashed=False, check=True):
        self.res(p1, p2, f"{show or ref}\n{text or fmt_r(value)}", side, dashed=dashed)
        self._reg(ref, "R", {"1": p1, "2": p2}, value=value, check=check)

    def C(self, ref, value, p1, p2, side=None, text=None, show=None, dashed=False, check=True):
        self.cap(p1, p2, f"{show or ref}\n{text or fmt_c(value)}", side, dashed=dashed)
        self._reg(ref, "C", {"1": p1, "2": p2}, value=value, check=check)

    def D(self, ref, part, p_anode, p_cathode, side=None, check=False):
        self.diode(p_anode, p_cathode, f"{ref}\n{part}", side)
        self._reg(ref, "D", {"a": p_anode, "k": p_cathode}, part=part, check=check)

    def J(self, ref, part, gate_at, label=(0.62, 0.0, "left", "center"), show=None, check=True,
          mirror=False, flip=False):
        """N-channel JFET with its gate at gate_at (drain up, source down; flip: drain down)."""
        e = self.njfet(gate_at, mirror=mirror, flip=flip)
        self._reg(ref, "njf", {"d": e.drain, "g": e.gate, "s": e.source}, part=part, check=check,
                  center=P(e.center))
        c = e.center
        dx, dy, ha, va = label
        self.text((c[0] + dx, c[1] + dy), f"{show or ref}\n{part}", ha=ha, va=va)
        return e

    def Q(self, ref, part, base_at, kind="npn", label=(0.62, 0.0, "left", "center"), show=None,
          check=True, mirror=False, flip=False):
        e = self.npn(base_at, mirror=mirror, flip=flip) if kind == "npn" else self.pnp(base_at, mirror=mirror)
        self._reg(ref, kind, {"c": e.collector, "b": e.base, "e": e.emitter}, part=part, check=check,
                  center=P(e.center))
        c = e.center
        dx, dy, ha, va = label
        self.text((c[0] + dx, c[1] + dy), f"{show or ref}\n{part}", ha=ha, va=va)
        return e

    def OA(self, ref, part, minus_at, minus_on_top=True, name=None, name_dxy=(0.0, 0.0), check=True,
           scale=0.72):
        e = self.opamp(minus_at, minus_on_top=minus_on_top, scale=scale)
        self._reg(ref, "OA", {"-": e.in1, "+": e.in2, "out": e.out}, part=part, check=check)
        if name:
            # centred 0.33 units toward the output from the symbol's middle, where the triangle is
            # narrow enough that a two-line name above or below it clears its slanted edges
            cx = 0.5 * (e.in1[0] + e.out[0]) + name_dxy[0]
            self.text((cx + 0.33, e.out[1] + name_dxy[1]), name, ha="center", va="center")
        return e

    def gnd(self, p, flip=False):
        self.ground(p, flip=flip)
        self.ties.append((self._snap(p), "0", "ground", "tie"))

    def rail(self, p, volts, net, up=None, side=None, text=None):
        up = volts > 0 if up is None else up
        txt = text or volts_text(volts)
        self.supply(p, txt, up=up, side=side)
        self.ties.append((self._snap(p), net, txt, "tie"))

    def label(self, p, net, text=None, dxy=(0.15, 0.0), ha="left", va="center"):
        """Net name written beside a wire (an off-sheet connection by name)."""
        self.text((p[0] + dxy[0], p[1] + dxy[1]), text or net, ha=ha, va=va)
        self.ties.append((self._snap(p), net, text or net, "label"))

    def offsheet(self, p, net, side="right", text=None):
        self.terminal(p, text or net, side=side)
        self.ties.append((self._snap(p), net, text or net, "tie"))


# ------------------------------------------------------------------ geometry (HV note) --
class UF:
    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


def on_seg(p, a, b) -> bool:
    (px, py), (ax, ay), (bx, by) = p, a, b
    L2 = (bx - ax) ** 2 + (by - ay) ** 2
    if L2 < TOL ** 2:
        return False
    L = math.sqrt(L2)
    if abs((bx - ax) * (py - ay) - (by - ay) * (px - ax)) / L > TOL:
        return False
    t = ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / L2
    return TOL / L < t < 1 - TOL / L


def crossing(a, b, c, d):
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = a, b, c, d
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-12:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    u = ((x1 - x3) * (y1 - y2) - (y1 - y3) * (x1 - x2)) / den
    l1, l2 = math.hypot(x2 - x1, y2 - y1), math.hypot(x4 - x3, y4 - y3)
    if TOL < t * l1 < l1 - TOL and TOL < u * l2 < l2 - TOL:
        return (round(x1 + t * (x2 - x1), 3), round(y1 + t * (y2 - y1), 3))
    return None


def overlap(a, b, p1, p2) -> bool:
    (ax, ay), (bx, by) = a, b
    L = math.hypot(bx - ax, by - ay)
    if L < TOL:
        return False
    for (px, py) in (p1, p2):
        if abs((bx - ax) * (py - ay) - (by - ay) * (px - ax)) / L > TOL:
            return False
    ux, uy = (bx - ax) / L, (by - ay) / L
    t1, t2 = sorted([(p1[0] - ax) * ux + (p1[1] - ay) * uy, (p2[0] - ax) * ux + (p2[1] - ay) * uy])
    return min(L, t2) - max(0.0, t1) > TOL


def sheet_points(S: Sch):
    pts = set()
    for a, b in S.wires:
        pts |= {a, b}
    for c in S.comps.values():
        pts |= set(c["pins"].values())
    for p, *_ in S.ties:
        pts.add(p)
    return pts


def build_nets(S: Sch) -> UF:
    uf = UF()
    pts = sheet_points(S)
    for p in pts:
        uf.find(p)
    for a, b in S.wires:
        uf.union(a, b)
        for p in pts:
            if p != a and p != b and on_seg(p, a, b):
                uf.union(p, a)
    return uf


def check_geometry(S: Sch) -> tuple[list[str], list]:
    out = []
    pts = sheet_points(S)
    deg = Counter()
    for a, b in S.wires:
        deg[a] += 1
        deg[b] += 1
        for p in pts:
            if p != a and p != b and on_seg(p, a, b):
                deg[p] += 2
    for c in S.comps.values():
        for p in c["pins"].values():
            deg[p] += 1
    for p, _, _, kind in S.ties:
        if kind != "label":
            deg[p] += 1
    need = {p for p, d in deg.items() if d >= 3}
    have = set(S.dots)
    for p in sorted(need - have):
        out.append(f"missing junction dot at {p}")
    for p in sorted(have - need):
        out.append(f"dot without a junction at {p}")
    for p, d in deg.items():
        if d >= 4:
            out.append(f"four-way junction at {p}")
    crosses = []
    for i, (a, b) in enumerate(S.wires):
        for c, d in S.wires[i + 1:]:
            x = crossing(a, b, c, d)
            if x:
                crosses.append(x)
    for ref, c in S.comps.items():
        if c["kind"] in ("R", "C", "D"):
            p1, p2 = list(c["pins"].values())
            for a, b in S.wires:
                if overlap(a, b, p1, p2):
                    out.append(f"wire {a}-{b} runs over {ref}")
        if c["kind"] in ("npn", "pnp", "njf"):
            cx, cy = c["center"]
            for a, b in S.wires:
                if a in c["pins"].values() or b in c["pins"].values():
                    continue
                (ax, ay), (bx, by) = a, b
                L2 = (bx - ax) ** 2 + (by - ay) ** 2
                t = max(0.0, min(1.0, ((cx - ax) * (bx - ax) + (cy - ay) * (by - ay)) / L2)) if L2 else 0
                if math.hypot(ax + t * (bx - ax) - cx, ay + t * (by - ay) - cy) < 0.45:
                    out.append(f"wire {a}-{b} passes through {ref}")
    uf = build_nets(S)
    members = defaultdict(int)
    for c in S.comps.values():
        for p in c["pins"].values():
            members[uf.find(p)] += 1
    for p, *_ in S.ties:
        members[uf.find(p)] += 1
    for ref, c in S.comps.items():
        for pin, p in c["pins"].items():
            if members[uf.find(p)] < 2:
                out.append(f"{ref} pin {pin} at {p} is connected to nothing")
    return out, crosses


# ------------------------------------------------------------------------ netlist side --
SI = {"f": 1e-15, "p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3, "k": 1e3, "meg": 1e6, "g": 1e9}


def num(s: str) -> float:
    m = re.match(r"^([-+]?[0-9]*\.?[0-9]+(?:e[-+]?[0-9]+)?)(meg|[fpnumkg])?", s.strip().lower())
    return float(m.group(1)) * (SI[m.group(2)] if m.group(2) else 1.0)


def parse_top(text: str) -> dict:
    """Top-level elements of a netlist text: name (lower case) -> dict(type, nodes, value, model)."""
    out, depth = {}, 0
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("*"):
            continue
        low = line.lower()
        if low.startswith(".subckt"):
            depth += 1
            continue
        if low.startswith(".ends"):
            depth -= 1
            continue
        if depth or line.startswith(".") or line.startswith("+"):
            continue
        t = line.split()
        ref, c = t[0].lower(), t[0][0].lower()
        if c in "rc" and len(t) >= 4:
            out[ref] = dict(type=c, nodes=[x.lower() for x in t[1:3]], value=num(t[3]))
        elif c == "q":
            out[ref] = dict(type="q", nodes=[x.lower() for x in t[1:4]], model=t[4].upper())
        elif c == "x":
            out[ref] = dict(type="x", nodes=[x.lower() for x in t[1:-1]], model=t[-1].upper())
        elif c in "vi":
            out[ref] = dict(type=c, nodes=[x.lower() for x in t[1:3]])
    return out


PINS = {"R": ("1", "2"), "C": ("1", "2"), "njf": ("d", "g", "s"), "npn": ("c", "b", "e"),
        "pnp": ("c", "b", "e"), "OA": ("+", "-", "out")}


def check_netlist(S: Sch, net: dict, scope: list[str] | None = None, model_alias=None) -> list[str]:
    """See the module docstring.  model_alias maps a drawn part name to the netlist model name."""
    uf = build_nets(S)
    errs = []
    drawn_to_node: dict = defaultdict(set)
    node_to_drawn: dict = defaultdict(set)
    tied = defaultdict(set)
    for p, node, *_ in S.ties:
        r = uf.find(p)
        drawn_to_node[r].add(node.lower())
        node_to_drawn[node.lower()].add(r)
        tied[node.lower()].add(r)
    for ref, c in S.comps.items():
        if not c.get("check", True):
            continue
        e = net.get(ref.lower())
        if e is None:
            errs.append(f"{ref}: drawn but not in the netlist")
            continue
        if c["kind"] in ("R", "C"):
            if e["type"] != c["kind"].lower():
                errs.append(f"{ref}: drawn as {c['kind']}, netlist has {e['type']}")
            elif abs(e["value"] / c["value"] - 1) > 5e-3:
                errs.append(f"{ref}: drawn {c['value']:g}, netlist {e['value']:g}")
            pins = [uf.find(c["pins"][k]) for k in ("1", "2")]
            nodes = e["nodes"]
            # a two-terminal part may be drawn either way round: take the order that agrees with
            # the nets already identified, else the netlist order
            if (pins[0] in drawn_to_node and nodes[1] in drawn_to_node[pins[0]]) or \
               (pins[1] in drawn_to_node and nodes[0] in drawn_to_node[pins[1]]):
                nodes = nodes[::-1]
            pairs = zip(pins, nodes)
        else:
            want = (model_alias or {}).get(c["part"], c["part"]).upper()
            if e.get("model", "").upper() != want:
                errs.append(f"{ref}: drawn {c['part']}, netlist {e.get('model')}")
            order = PINS[c["kind"]]
            pairs = [(uf.find(c["pins"][k]), e["nodes"][i]) for i, k in enumerate(order)]
        for r, node in pairs:
            drawn_to_node[r].add(node)
            node_to_drawn[node].add(r)
    for r, nodes in drawn_to_node.items():
        if len(nodes) > 1:
            errs.append(f"one drawn net is several netlist nodes: {sorted(nodes)}")
    for node, rs in node_to_drawn.items():
        if len(rs) > 1 and not all(r in tied[node] for r in rs):
            errs.append(f"netlist node {node} is drawn as {len(rs)} separate nets")
    for ref in scope or []:
        if ref.upper() not in {k.upper() for k in S.comps}:
            errs.append(f"{ref}: in the netlist but not drawn")
    return errs


def report(S: Sch, net: dict, scope=None, model_alias=None) -> bool:
    g, crosses = check_geometry(S)
    n = check_netlist(S, net, scope, model_alias)
    print(f"{S.name}: {len(S.comps)} parts, {len(S.wires)} wires; geometry problems {len(g)}, "
          f"netlist problems {len(n)}, wire crossings {len(crosses)}")
    for x in g + n:
        print("   ", x)
    return not g and not n
