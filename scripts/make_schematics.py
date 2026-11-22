"""Schematics of the low-noise preamplifier note, drawn with schematic_style.py and checked against
the netlists the simulations use (schematics.check_geometry / check_netlist).

Sheets (PNG at 600 dpi and PDF, in ../figures/):
  schematic_front_end_H   one side of the current-feedback front end with the H values (side b is
                          identical; R_G and the cross-coupled C_X join the sides), the common-mode
                          servo as a block
  schematic_front_end_L   the same with the L values
  schematic_chain         difference amplifier, filters, gain stages and output driver
  schematic_sr560         the SR560's front end as read from its schematic (x10 position)
  schematic_topology      the topology in its basic form and its differential noise half-circuit
                          (a drawing for the text, without a netlist; 'python make_schematics.py
                          topology' draws only this sheet)

The n paralleled JFETs of each side, and their cascodes, are drawn as one JFET and one cascode
marked x n: before the comparison, the netlist's per-device instances XJa1..XJan and XCa1..XCan
and their drain nodes da1..dan are collapsed into XJa1, XCa1 and da1 (they connect identically).
Usage: python make_schematics.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import chain
import frontend as F
import schematic_style as ss
import sr560_frontend
from schematics import Sch, fmt_c, fmt_r, parse_top, report

OUT = Path(__file__).resolve().parent.parent / "figures"
JX, JD, JS = 0.66, 0.66, 0.30        # JFET (gate on the left): channel 0.66 right, drain up, source down


def collapse(text: str, n: int) -> str:
    """Per-device instances of the paralleled JFETs and cascodes folded into the first."""
    keep = []
    for line in text.splitlines():
        m = re.match(r"\s*X([JC])([ab])(\d+)\b", line)
        if m and int(m.group(3)) > 1:
            continue
        keep.append(re.sub(r"\bd([ab])\d+\b", r"d\g<1>1", line))
    return "\n".join(keep)


# ---------------------------------------------------------------------- front end, side a --
def sheet_front_end(case: str) -> tuple[Sch, dict, list]:
    p = F.CASES[case]
    S = Sch(f"schematic_front_end_{case[0]}")
    # input JFET array (gate on the left) and its cascode array (gate on the right)
    jg = (1.6, 3.0)
    J = S.J("XJa1", p.jfet, jg, label=(-0.95, -0.55, "right", "top"),
            show=f"XJa1…XJa{p.n}  (× {p.n})", mirror=True)
    cg = (2.92, 5.0)
    C = S.J("XCa1", p.cascode[2:], cg, label=(-0.85, 0.35, "right", "center"),
            show=f"XCa1…XCa{p.n}  (× {p.n})", mirror=False)
    S.wire(J.drain, C.source)
    S.offsheet((-0.2, 3.0), "ga", side="left", text="input a (ga)")
    S.wire((-0.2, 3.0), jg)
    # summing node, R_D, op amp with C_I and C_X
    ys = 7.6
    S.wire(C.drain, (C.drain[0], ys))
    r_d = (p.vp - p.vref) / (p.n * p.id)
    S.R("RDa", r_d, (C.drain[0], 9.4), (C.drain[0], ys), side="left")
    S.rail((C.drain[0], 9.4), p.vp, "vp")
    xb1, xb2 = 4.0, 6.0
    oa_in = (8.0, ys)                      # inverting input at the bottom: vref enters from above
    U = S.OA("XUa", "THS4021", oa_in, minus_on_top=False, name="XUa\nTHS4021", name_dxy=(0.0, -1.05))
    S.wire((C.drain[0], ys), (3.6, ys), (4.4, ys), (5.3, ys), oa_in)
    S.dot((C.drain[0], ys))
    # C_node: summing node to ground (keeps the op amp's own loop at a noise gain of about 10)
    if p.cnode:
        S.C("CNa", p.cnode, (5.3, ys), (5.3, 6.35), side="left")
        S.gnd((5.3, 6.35))
        S.dot((5.3, ys))
    S.offsheet((U.in2[0] - 1.0, U.in2[1]), "vref", side="left", text="vref (+9 V)")
    S.wire((U.in2[0] - 1.0, U.in2[1]), U.in2)
    xo = U.out[0] + 0.8
    S.wire(U.out, (xo, U.out[1]))
    # C_I (own output to own summing node), C_X (other side's output to this summing node)
    yci, ycx = 9.7, 11.0
    S.wire((xo, U.out[1]), (xo, 8.9), (xo, yci))
    S.C("CIa", p.ci, (xo, yci), (4.4, yci), side="top")
    S.wire((4.4, yci), (4.4, ys))
    S.dot((4.4, ys))
    S.offsheet((xo + 0.6, ycx), "ob", side="right", text="ob (output b)")
    S.wire((xo + 0.6, ycx), (6.2, ycx))
    S.C("CXa", p.cx, (6.2, ycx), (3.6, ycx), side="top")
    S.wire((3.6, ycx), (3.6, ys))
    S.dot((3.6, ys))
    S.dot((xo, U.out[1]))
    S.offsheet((xo + 1.4, 8.9), "oa", side="right", text="oa (output a)")
    S.wire((xo, 8.9), (xo + 1.4, 8.9))
    S.dot((xo, 8.9))
    # bootstrap: R_BS || C_BS from the cascode gates to the source node, R_UP from +15 V
    yb = cg[1]
    S.wire(cg, (xb1, yb), (xb2, yb))
    S.dot((xb1, yb))
    ysa = 1.6
    S.R("RBSa", p.vbs / p.i_bs, (xb1, yb), (xb1, ysa + 0.4), side="right")
    S.wire((xb1, ysa + 0.4), (xb1, ysa))
    S.C("CBSa", p.c_bs, (xb2, yb), (xb2, ysa + 0.4), side="right")
    S.wire((xb2, ysa + 0.4), (xb2, ysa))
    r_up = (p.vp - (0.6 + p.vbs)) / p.i_bs
    S.R("RUPa", r_up, (xb2, yb), (xb2, 6.6), side="right")
    S.rail((xb2, 6.6), p.vp, "vp", side="right")
    S.dot((xb2, yb))
    # source node bus, R_F from the output, R_G to side b, current sink
    S.wire(J.source, (J.source[0], ysa))
    xs = 8.6
    S.wire((J.source[0], ysa), (xb1, ysa), (xb2, ysa), (xs, ysa), (xo, ysa))
    S.dot((xb1, ysa))
    S.dot((xb2, ysa))
    S.R("RFa", p.rf, (xo, 5.6), (xo, 3.6), side="right")
    S.wire((xo, U.out[1]), (xo, 5.6))
    S.wire((xo, 3.6), (xo, ysa))
    S.dot((xo, ysa))
    S.R("RG", p.rg, (xo, ysa), (xo + 2.2, ysa), side="bottom")
    S.offsheet((xo + 2.8, ysa), "sb", side="right", text="sb (side b)")
    S.wire((xo + 2.2, ysa), (xo + 2.8, ysa))
    Q = S.Q("QTa", p.sink, (xs - 0.54, ysa - 1.0), label=(0.62, -0.1, "left", "center"))
    S.wire(Q.collector, (Q.collector[0], ysa))
    S.dot((Q.collector[0], ysa))
    r_t = p.v_sink / (p.n * p.id + p.i_bs)
    S.R("RTa", r_t, Q.emitter, (Q.emitter[0], Q.emitter[1] - 1.6), side="right")
    S.rail((Q.emitter[0], Q.emitter[1] - 1.6), p.vm, "vm")
    S.offsheet((Q.base[0] - 1.6, Q.base[1]), "vsink", side="left", text="vsink (CM servo)")
    S.wire((Q.base[0] - 1.6, Q.base[1]), Q.base)
    S.text((-0.2, -3.1), f"Front end {case[0]}: {p.n} × {p.jfet} per side at {p.id * 1e3:g} mA; "
                         f"gain 1 + 2 R_F / R_G = {p.gain:.4g}", ha="left", va="center")
    # netlist (front end plus the chain's input network) and the parts of side a in scope
    text = collapse(F.netlist(p), p.n)
    net = parse_top(text)
    scope = ["XJa1", "XCa1", "RDa", "CIa", "CXa", "XUa", "RFa", "RBSa", "CBSa", "RUPa", "QTa", "RTa", "RG"]
    if p.cnode:
        scope.append("CNa")
    return S, net, scope


# ---------------------------------------------------------- front end, both sides --
def _fe_half(S: Sch, p, x: str, Y, fl: bool) -> dict:
    """One side of the front end; side a as on the one-sided sheet (Y(y) = y, fl False), side b
    its mirror image about a horizontal axis (Y(y) = 2 y_m - y, fl True).  Returns the points
    where the side joins the rest of the sheet."""
    def P(xx, yy):
        return (xx, Y(yy))

    def lab(dx, dy, ha, va):
        return (dx, -dy if fl else dy, ha, {"top": "bottom", "bottom": "top"}.get(va, va) if fl else va)

    other = "b" if x == "a" else "a"
    jg = P(1.6, 3.0)
    J = S.J(f"XJ{x}1", p.jfet, jg, label=lab(-0.95, -0.55, "right", "top"),
            show=f"XJ{x}1…XJ{x}{p.n}  (× {p.n})", mirror=True, flip=fl)
    cg = P(2.92, 5.0)
    C = S.J(f"XC{x}1", p.cascode[2:], cg, label=lab(-0.85, 0.35, "right", "center"),
            show=f"XC{x}1…XC{x}{p.n}  (× {p.n})", mirror=False, flip=fl)
    S.wire(J.drain, C.source)
    S.offsheet(P(-0.2, 3.0), f"g{x}", side="left", text=f"input {x.upper()} (g{x})")
    S.wire(P(-0.2, 3.0), jg)
    ys = 7.6
    S.wire(C.drain, (C.drain[0], Y(ys)))
    r_d = (p.vp - p.vref) / (p.n * p.id)
    S.R(f"RD{x}", r_d, (C.drain[0], Y(9.4)), (C.drain[0], Y(ys)), side="left")
    S.rail((C.drain[0], Y(9.4)), p.vp, "vp", up=not fl)
    U = S.OA(f"XU{x}", "THS4021", P(8.0, ys), minus_on_top=fl, name=f"XU{x}\nTHS4021",
             name_dxy=(0.0, 1.05 if fl else -1.05))
    S.wire((C.drain[0], Y(ys)), P(3.6, ys), P(4.4, ys), P(5.3, ys), P(8.0, ys))
    S.dot((C.drain[0], Y(ys)))
    if p.cnode:
        S.C(f"CN{x}", p.cnode, P(5.3, ys), P(5.3, 6.35), side="left")
        S.gnd(P(5.3, 6.35), flip=fl)
        S.dot(P(5.3, ys))
    S.offsheet((U.in2[0] - 1.0, U.in2[1]), "vref", side="left", text="vref (+9 V)")
    S.wire((U.in2[0] - 1.0, U.in2[1]), U.in2)
    xo = U.out[0] + 0.8
    S.wire(U.out, (xo, U.out[1]))
    yci, ycx = 9.7, 11.0
    S.wire((xo, U.out[1]), P(xo, 8.9), P(xo, yci))
    S.C(f"CI{x}", p.ci, P(xo, yci), P(4.4, yci), side="bottom" if fl else "top")
    S.wire(P(4.4, yci), P(4.4, ys))
    S.dot(P(4.4, ys))
    S.C(f"CX{x}", p.cx, P(6.2, ycx), P(3.6, ycx), side="bottom" if fl else "top")
    S.wire(P(3.6, ycx), P(3.6, ys))
    S.dot(P(3.6, ys))
    S.dot((xo, U.out[1]))
    S.dot(P(xo, 8.9))
    yb = 5.0
    xb1, xb2 = 4.0, 6.0
    S.wire(cg, P(xb1, yb), P(xb2, yb))
    S.dot(P(xb1, yb))
    ysa = 1.6
    S.R(f"RBS{x}", p.vbs / p.i_bs, P(xb1, yb), P(xb1, ysa + 0.4), side="right")
    S.wire(P(xb1, ysa + 0.4), P(xb1, ysa))
    S.C(f"CBS{x}", p.c_bs, P(xb2, yb), P(xb2, ysa + 0.4), side="right")
    S.wire(P(xb2, ysa + 0.4), P(xb2, ysa))
    r_up = (p.vp - (0.6 + p.vbs)) / p.i_bs
    S.R(f"RUP{x}", r_up, P(xb2, yb), P(xb2, 6.6), side="right")
    S.rail(P(xb2, 6.6), p.vp, "vp", side="right", up=not fl)
    S.dot(P(xb2, yb))
    S.wire(J.source, (J.source[0], Y(ysa)))
    xs = 8.6
    S.wire((J.source[0], Y(ysa)), P(xb1, ysa), P(xb2, ysa), P(xs, ysa), P(xo, ysa))
    S.dot(P(xb1, ysa))
    S.dot(P(xb2, ysa))
    S.R(f"RF{x}", p.rf, P(xo, 5.6), P(xo, 3.6), side="right")
    S.wire((xo, U.out[1]), P(xo, 5.6))
    S.wire(P(xo, 3.6), P(xo, ysa))
    Q = S.Q(f"QT{x}", p.sink, P(xs - 0.54, ysa - 1.0), label=lab(0.62, -0.1, "left", "center"), flip=fl)
    S.wire(Q.collector, (Q.collector[0], Y(ysa)))
    S.dot((Q.collector[0], Y(ysa)))
    r_t = p.v_sink / (p.n * p.id + p.i_bs)
    y_rt = Q.emitter[1] + (1.6 if fl else -1.6)
    S.R(f"RT{x}", r_t, Q.emitter, (Q.emitter[0], y_rt), side="right")
    S.rail((Q.emitter[0], y_rt), p.vm, "vm", up=fl)
    S.offsheet((Q.base[0] - 1.6, Q.base[1]), "vsink", side="left", text="vsink (CM servo)")
    S.wire((Q.base[0] - 1.6, Q.base[1]), Q.base)
    return dict(xo=xo, src=P(xo, ysa), out=P(xo, 8.9), cx_end=P(6.2, ycx))


def sheet_front_end_full(case: str) -> tuple[Sch, dict, list]:
    """Both sides of a front end: side A on top, side B its mirror image below; R_G joins the two
    source nodes across the axis of symmetry, and each C_X runs from one side's output to the
    other side's summing node."""
    p = F.CASES[case]
    S = Sch(f"schematic_front_end_{case[0]}_both")
    y_m = -3.0
    A = _fe_half(S, p, "a", lambda y: y, False)
    B = _fe_half(S, p, "b", lambda y: 2 * y_m - y, True)
    xo = A["xo"]
    # R_G across the axis of symmetry, between the two source nodes
    x_rg = xo + 1.0
    S.wire(A["src"], (x_rg, A["src"][1]), (x_rg, y_m + 1.0))
    S.R("RG", p.rg, (x_rg, y_m + 1.0), (x_rg, y_m - 1.0), side="left")
    S.wire((x_rg, y_m - 1.0), (x_rg, B["src"][1]), B["src"])
    S.dot(A["src"])
    S.dot(B["src"])
    # outputs to S2, and the cross-coupled capacitors: C_Xa from output b, C_Xb from output a
    x_cxa, x_cxb, x_out = xo + 2.0, xo + 2.6, xo + 3.2
    S.wire(A["out"], (x_out, A["out"][1]))
    S.wire(B["out"], (x_out, B["out"][1]))
    S.offsheet((x_out, A["out"][1]), "oa", side="right", text="oa (to S2)")
    S.offsheet((x_out, B["out"][1]), "ob", side="right", text="ob (to S2)")
    S.wire(A["cx_end"], (x_cxa, A["cx_end"][1]), (x_cxa, B["out"][1]))
    S.dot((x_cxa, B["out"][1]))
    S.wire(B["cx_end"], (x_cxb, B["cx_end"][1]), (x_cxb, A["out"][1]))
    S.dot((x_cxb, A["out"][1]))
    S.text((-0.6, y_m + 0.32), "axis of symmetry", ha="left", va="center", color=ss.COLORS["annotation"])
    S.line((-0.6, y_m), (x_rg - 2.4, y_m), color=ss.COLORS["annotation"], dashed=True)
    S.text((-0.2, 2 * y_m - 11.0 - 1.4),
           f"Front end {case[0]}, both sides: {p.n} × {p.jfet} per side at {p.id * 1e3:g} mA; "
           f"gain 1 + 2 R_F / R_G = {p.gain:.4g}", ha="left", va="center")
    text = collapse(F.netlist(p), p.n)
    net = parse_top(text)
    scope = [f"{r}{x}" for x in "ab" for r in ("XJ", "XC", "RD", "CI", "CX", "XU", "RF", "RBS", "CBS", "RUP",
                                               "QT", "RT")]
    scope = [s if not s.startswith(("XJ", "XC")) else s + "1" for s in scope] + ["RG"]
    if p.cnode:
        scope += ["CNa", "CNb"]
    return S, net, scope


# ------------------------------------------------------------------------ signal chain --
CHAIN_SETTING = chain.Setting("H100", a3=0.5, a4=0.5, a5=0.4, f1=("LP", 1e5), f2=("HP", 100))


def _noninv(S: Sch, pre: str, part: str, nin, gain_parts, att):
    """Attenuator (top, bottom, 1-ohm switch) feeding a non-inverting stage whose '+' input is at
    the top; returns the output point.  nin is the input point (left)."""
    rt, rb, rs, rf, rg = att + gain_parts
    x0, y0 = nin
    xt = x0 + 2.0                     # attenuator tap
    S.R(f"R{pre}T", rt, (x0, y0), (xt, y0), side="top", show=f"R{pre}T")
    S.dot((xt, y0))
    S.R(f"R{pre}B", rb, (xt, y0), (xt, y0 - 2.0), side="right", show=f"R{pre}B")
    S.gnd((xt, y0 - 2.0))
    xi = xt + 1.7
    S.R(f"R{pre}S", rs, (xt, y0), (xi, y0), side="top", show=f"R{pre}S", text="1 Ω (switch)")
    # op amp with '+' on top: in2 at y0, in1 0.9 below
    xin = xi + 0.4
    U = S.OA(f"X{pre}", part, (xin, y0 - 0.9), minus_on_top=False, name=f"X{pre}\n{part}",
             name_dxy=(0.0, 1.15))
    S.wire((xi, y0), U.in2)
    xo = U.out[0] + 0.5
    yfb = y0 - 2.1
    S.wire(U.out, (xo, U.out[1]), (xo, yfb))
    S.dot((xo, U.out[1]))
    S.R(f"R{pre}F", rf, (xo, yfb), (xin - 0.5, yfb), side="bottom", show=f"R{pre}F")
    S.wire((xin - 0.5, yfb), (xin - 0.5, U.in1[1]), U.in1)
    S.dot((xin - 0.5, yfb))
    S.R(f"R{pre}G", rg, (xin - 0.5, yfb), (xin - 0.5, yfb - 1.9), side="left", show=f"R{pre}G")
    S.gnd((xin - 0.5, yfb - 1.9))
    return (xo, U.out[1])


def _filter(S: Sch, pre: str, kind: str, nin, r, c):
    """One RC section (LP: R in series, C to ground; HP: the reverse), the 20 pF of the switches
    and layout, and a THS4031 follower; returns the output point."""
    x0, y0 = nin
    xn = x0 + 2.4
    if kind == "LP":
        S.R(f"R{pre}", r, (x0, y0), (xn, y0), side="top")
        S.C(f"C{pre}", c, (xn, y0), (xn, y0 - 2.0), side="left")
    else:
        S.C(f"C{pre}", c, (x0, y0), (xn, y0), side="top")
        S.R(f"R{pre}", r, (xn, y0), (xn, y0 - 2.0), side="left")
    S.gnd((xn, y0 - 2.0))
    S.dot((xn, y0))
    xp = xn + 1.2
    S.C(f"C{pre}P", 20e-12, (xp, y0), (xp, y0 - 2.0), side="right", text="20 pF")
    S.gnd((xp, y0 - 2.0))
    S.dot((xp, y0))
    xin = xp + 2.6
    U = S.OA(f"X{pre}B", "THS4031", (xin, y0 - 0.9), minus_on_top=False, name=f"X{pre}B\nTHS4031",
             name_dxy=(0.0, 1.15))
    S.wire((xn, y0), (xp, y0), U.in2)
    xo = U.out[0] + 0.5
    S.wire(U.out, (xo, U.out[1]), (xo, y0 - 1.8), (xin - 0.4, y0 - 1.8), (xin - 0.4, U.in1[1]), U.in1)
    S.dot((xo, U.out[1]))
    return (xo, U.out[1])


def sheet_chain() -> tuple[Sch, dict, list]:
    s = CHAIN_SETTING
    S = Sch("schematic_chain")
    net_text = chain.netlist(s)
    net = parse_top(net_text)
    vals = {k: v["value"] for k, v in net.items() if "value" in v}
    # ---- row 1: S2 difference amplifier and F1
    y1 = 12.0
    S.offsheet((0.0, y1), "ob", side="left", text="ob")
    S.R("RD1", vals["rd1"], (0.0, y1), (2.4, y1), side="top")
    U = S.OA("XS2", chain.DA_OPAMP, (3.0, y1), minus_on_top=True, name=f"XS2\n{chain.DA_OPAMP}",
             name_dxy=(0.0, -1.25))
    S.wire((2.4, y1), U.in1)
    S.dot((2.4, y1))
    xo = U.out[0] + 0.5
    S.wire((2.4, y1), (2.4, y1 + 1.6))
    S.R("RD2", vals["rd2"], (2.4, y1 + 1.6), (xo, y1 + 1.6), side="top")
    S.wire((xo, y1 + 1.6), (xo, U.out[1]))
    S.wire(U.out, (xo, U.out[1]))
    ylo = U.in2[1] - 1.4
    S.offsheet((0.0, ylo), "oa", side="left", text="oa")
    S.R("RD3", vals["rd3"], (0.0, ylo), (2.0, ylo), side="top")
    S.wire((2.0, ylo), (2.7, ylo), (2.7, U.in2[1]), U.in2)
    S.dot((2.0, ylo))
    S.R("RD4", vals["rd4"], (2.0, ylo), (2.0, ylo - 2.0), side="left")
    S.gnd((2.0, ylo - 2.0))
    S.dot((xo, U.out[1]))
    xf = xo + 0.8
    S.wire((xo, U.out[1]), (xf, U.out[1]))
    o1 = _filter(S, "F1", "LP", (xf, U.out[1]), vals["rf1"], vals["cf1"])
    S.offsheet((o1[0] + 0.8, o1[1]), "f1", side="right", text="f1 → S3")
    S.wire(o1, (o1[0] + 0.8, o1[1]))
    # ---- row 2: S3 and F2
    y2 = 5.0
    S.offsheet((0.0, y2), "f1", side="left", text="f1")
    o3 = _noninv(S, "S3", "THS4021", (0.0, y2),
                 (vals["rs3f"], vals["rs3g"]), (vals["rs3t"], vals["rs3b"], vals["rs3s"]))
    o2 = _filter(S, "F2", "HP", (o3[0] + 0.8, o3[1]), vals["rf2"], vals["cf2"])
    S.wire(o3, (o3[0] + 0.8, o3[1]))
    S.offsheet((o2[0] + 0.8, o2[1]), "f2", side="right", text="f2 → S4")
    S.wire(o2, (o2[0] + 0.8, o2[1]))
    # ---- row 3: S4 and S5 with the output network
    y3 = -2.0
    S.offsheet((0.0, y3), "f2", side="left", text="f2")
    o4 = _noninv(S, "S4", "THS4021", (0.0, y3),
                 (vals["rs4f"], vals["rs4g"]), (vals["rs4t"], vals["rs4b"], vals["rs4s"]))
    S.wire(o4, (o4[0] + 0.8, o4[1]))
    o5 = _noninv(S, "S5", "THS3091", (o4[0] + 0.8, o4[1]),
                 (vals["rs5f"], vals["rs5g"]), (vals["rs5t"], vals["rs5b"], vals["rs5s"]))
    S.R("RO50", vals["ro50"], o5, (o5[0] + 1.9, o5[1]), side="top")
    S.offsheet((o5[0] + 2.2, o5[1]), "out", side="right", text="OUT")
    S.wire((o5[0] + 1.9, o5[1]), (o5[0] + 2.2, o5[1]))
    scope = ["RD1", "RD2", "RD3", "RD4", "XS2", "RF1", "CF1", "CF1P", "XF1B", "RS3T", "RS3B", "RS3S",
             "XS3", "RS3F", "RS3G", "CF2", "RF2", "CF2P", "XF2B", "RS4T", "RS4B", "RS4S", "XS4", "RS4F",
             "RS4G", "RS5T", "RS5B", "RS5S", "XS5", "RS5F", "RS5G", "RO50"]
    return S, net, scope


# ------------------------------------------------------------------------ SR560 front end --
SR560_OMITTED = ["R120", "R121", "C108", "R116", "C116", "C110", "R136"]


def sheet_sr560() -> tuple[Sch, dict, list]:
    """The SR560 front end in the x10 position (K102 closed), as simulated in sr560_frontend.py.
    Not drawn: the offset trim at drain A (R121 from the trim pot, C108), R120 (drain B to
    ground), the front-out divider R116/C116 and C110 (6.8 pF, drains' mean to tail)."""
    S = Sch("schematic_sr560")
    xa, xb = 3.0, 9.0
    ja = S.J("XJA", "2N5564", (xa - JX, 8.0), label=(-0.75, 0.75, "right", "bottom"), show="U106A", mirror=True)
    jb = S.J("XJB", "2N5564", (xb + JX, 8.0), label=(0.75, 0.52, "left", "bottom"), show="U106B", mirror=False)
    # inputs with their 100-Mohm bias resistors
    S.offsheet((-1.3, 8.0), "ina", side="left", text="A")
    S.wire((-1.3, 8.0), (-0.4, 8.0), ja.gate)
    S.dot((-0.4, 8.0))
    S.R("R101", 100e6, (-0.4, 8.0), (-0.4, 6.4), side="left")
    S.gnd((-0.4, 6.4))
    S.offsheet((13.2, 8.0), "inb", side="right", text="B")
    S.wire(jb.gate, (12.2, 8.0), (13.2, 8.0))
    S.dot((12.2, 8.0))
    S.R("R102", 100e6, (12.2, 8.0), (12.2, 6.4), side="right")
    S.gnd((12.2, 6.4))
    # drain loads from the filtered +10 V node
    yt = 13.0
    S.wire((xa, yt), (6.0, yt), (7.4, yt), (xb, yt))
    S.R("R119", 165, (6.0, 14.8), (6.0, yt), side="left")
    S.rail((6.0, 14.8), 10, "p10")
    S.dot((6.0, yt))
    S.C("C113", 2.2e-6, (7.4, yt), (7.4, yt - 1.6), side="left")
    S.gnd((7.4, yt - 1.6))
    S.dot((7.4, yt))
    S.R("R131", 499, (xa, yt), (xa, 11.0), side="left")
    S.R("R117", 499, (xb, yt), (xb, 11.0), side="right")
    S.wire((xa, 11.0), (xa, 9.5), ja.drain)
    S.wire((xb, 11.0), (xb, 10.4), jb.drain)
    S.label((xa, 10.3), "da", dxy=(-0.15, 0.0), ha="right")
    S.label((xb, 10.75), "db", dxy=(0.15, 0.0), ha="left")
    # U102: + from drain A, - from drain B, C109 from the output to the - input
    U = S.OA("XU102", "OP37", (11.8, 10.4), minus_on_top=True, name="U102\nOP37", name_dxy=(0.0, -1.2))
    S.wire((xa, 9.5), (11.8, 9.5))
    S.dot((xa, 9.5))
    S.wire((xb, 10.4), (11.2, 10.4), U.in1)
    S.dot((xb, 10.4))
    xo = U.out[0] + 0.6
    S.wire(U.out, (xo, U.out[1]), (xo, 11.6))
    S.C("C109", 33e-12, (xo, 11.6), (11.2, 11.6), side="top")
    S.wire((11.2, 11.6), (11.2, 10.4))
    S.dot((11.2, 10.4))
    S.dot((xo, U.out[1]))
    # sources: R111 + P102 to ground on A, R112 + R118 from the output on B, R113/R114 to the
    # gain-relay node, R115/R128 and the P101/R135/R137 trim to the tail
    ys = 6.8
    S.wire(ja.source, (xa, ys))
    S.wire(jb.source, (xb, ys))
    S.R("R111", 1e3, (xa, ys), (xa - 1.8, ys), side="bottom")
    S.dot((xa, ys))
    S.R("RP102", 10, (xa - 1.8, ys), (xa - 1.8, ys - 2.0), side="left", show="P102", text="10 Ω (set)")
    S.gnd((xa - 1.8, ys - 2.0))
    S.R("R112", 10, (xb, ys), (xb + 1.8, ys), side="bottom")
    S.dot((xb, ys))
    yf = 5.4
    S.wire((xb + 1.8, ys), (xb + 1.8, yf))
    # label below: above it sits R102's ground
    S.R("R118", 1e3, (xb + 1.8, yf), (xb + 4.0, yf), side="bottom")
    S.wire((xb + 4.0, yf), (xo, yf))
    S.wire((xo, U.out[1]), (xo, yf))
    S.offsheet((xo + 1.2, 8.4), "out", side="right", text="front out")
    S.wire((xo, 8.4), (xo + 1.2, 8.4))
    S.dot((xo, 8.4))
    yx = 4.8
    S.R("R113", 110, (xa, ys), (xa, yx), side="right")
    S.R("R114", 110, (xb, ys), (xb, yx), side="left")
    S.wire((xa, yx), (5.0, yx))
    S.R("RK102", 1e-3, (5.0, yx), (7.0, yx), side="top", show="K102", text="closed (×10)", check=False)
    S.wire((7.0, yx), (xb, yx))
    S.dot((xa, yx))
    S.dot((xb, yx))
    yy = 2.8
    S.R("R115", 909, (xa, yx), (xa, yy), side="left")
    S.R("R128", 909, (xb, yx), (xb, yy), side="right")
    ytl = 0.6
    S.R("R135", 10, (xa, yy), (xa, ytl), side="left")
    S.wire((xa, yy), (4.3, yy))
    S.dot((xa, yy))
    S.R("RP101A", 50, (4.3, yy), (4.3, ytl), side="right", show="P101", text="2 × 50 Ω")
    S.R("R137", 10, (xb, yy), (xb, ytl), side="right")
    S.wire((xb, yy), (7.7, yy))
    S.dot((xb, yy))
    S.R("RP101B", 50, (7.7, yy), (7.7, ytl), side="left", show="", text="")
    S.wire((xa, ytl), (4.3, ytl), (6.0, ytl), (7.7, ytl), (xb, ytl))
    S.dot((4.3, ytl))
    S.dot((7.7, ytl))
    S.dot((6.0, ytl))
    S.R("R130", 100, (6.0, ytl), (6.0, ytl - 2.0), side="right")
    S.offsheet((6.0, ytl - 2.6), "sv", side="bottom", text="sv (U103 out)")
    S.wire((6.0, ytl - 2.0), (6.0, ytl - 2.6))
    # tail servo U103: the drains' mean against the 6.2 V reference (one unit below R118, so that
    # R129's label is not read as R118's)
    x0, y0 = 14.0, 1.0
    S.offsheet((x0 - 2.2, y0 + 2.2), "da", side="left", text="da")
    S.offsheet((x0 - 2.2, y0 + 0.5), "db", side="left", text="db")
    S.R("R129", 100e3, (x0 - 2.2, y0 + 2.2), (x0, y0 + 2.2), side="top")
    S.R("R127", 100e3, (x0 - 2.2, y0 + 0.5), (x0, y0 + 0.5), side="top")
    U3 = S.OA("XU103", "LF411", (x0 + 0.5, y0 + 0.5), minus_on_top=True, name="U103\nLF411",
              name_dxy=(0.0, 1.15))
    S.wire((x0, y0 + 2.2), (x0, y0 + 0.5), U3.in1)
    S.dot((x0, y0 + 0.5))
    # reference: D101's 6.2 V through R125, filtered by C112
    S.wire(U3.in2, (x0 - 0.4, U3.in2[1]), (x0 - 1.6, U3.in2[1]))
    S.R("R125", 49.9e3, (x0 - 1.6, U3.in2[1]), (x0 - 1.6, U3.in2[1] - 2.0), side="left")
    S.rail((x0 - 1.6, U3.in2[1] - 2.0), 6.2, "zref", up=False, text="+6.2 V (D101)")
    S.C("C112", 0.1e-6, (x0 - 0.4, U3.in2[1]), (x0 - 0.4, U3.in2[1] - 1.6), side="right")
    S.gnd((x0 - 0.4, U3.in2[1] - 1.6))
    S.dot((x0 - 0.4, U3.in2[1]))
    xs3 = U3.out[0] + 0.6
    S.wire(U3.out, (xs3, U3.out[1]))
    S.R("R122", 1e3, (xs3, U3.out[1]), (xs3, U3.out[1] - 2.0), side="right")
    S.rail((xs3, U3.out[1] - 2.0), -10, "m10")
    S.offsheet((xs3 + 0.9, U3.out[1]), "sv", side="right", text="sv")
    S.wire((xs3, U3.out[1]), (xs3 + 0.9, U3.out[1]))
    S.dot((xs3, U3.out[1]))
    S.text((-0.4, -2.9), "SR560 front end, gain relay K102 in the ×10 position (redrawn from SRS sheet "
                         "560_1F)", ha="left", va="center")
    net = parse_top(sr560_frontend.front_end(True))
    scope = [k.upper() for k, v in net.items() if v["type"] in "rcqx" and k.upper() not in SR560_OMITTED
             and k.upper() != "RK102"]
    return S, net, scope


# ------------------------------------------------- topology and noise half-circuit --
def sheet_topology() -> ss.Sheet:
    """Figure 6 of the note.  (a) The current-feedback topology in its basic form, both sides,
    one JFET per side (the paralleled JFETs, their cascodes and the bootstrap of Figures 7 and 8
    left out), with a DC current sink at each source node.  (b) Its differential half-circuit
    with the noise generators of Eq. (9): the supplies and V_ref are AC ground, and in
    differential mode the midpoint of R_G is a virtual ground, so each side sees R_G / 2.  Drawn
    after Spinelli and Haberman (2024), Figs. 2 and 4, in this note's symbols, with the current
    sink and C_node added.  A drawing for the text: it has no netlist to check against."""
    S = ss.Sheet()
    ax = 9.4                                    # axis of symmetry of panel (a)

    def side(m: bool) -> float:
        def X(x):
            return 2 * ax - x if m else x

        def P_(x, y):
            return (X(x), y)

        def lab(s):
            return {"left": "right", "right": "left"}.get(s, s) if m else s

        sg = -1.0 if m else 1.0
        tag = "b" if m else "a"
        yc, ys = 7.4, 2.0
        g = P_(2.4, 4.6)
        S.terminal(P_(0.6, 4.6), f"$v_{tag}$", side=lab("left"))
        S.wire(P_(0.6, 4.6), g)
        J = S.njfet(g, mirror=not m)            # mirror=True: gate on the left
        xj = J.drain[0]
        S.wire(J.drain, (xj, yc))
        S.dot((xj, yc))
        S.text((xj + sg * 0.15, yc + 0.2), f"$c_{tag}$", ha="left" if not m else "right", va="bottom")
        S.wire((xj, yc), (xj, 7.9))
        S.res((xj, 7.9), (xj, 9.7), text="$R_D$", side=lab("left"))
        S.supply((xj, 9.7), "$+V$")
        U = S.opamp(P_(4.6, yc), minus_on_top=True, left=m)
        S.wire((xj, yc), P_(4.0, yc), U.in1)
        S.dot(P_(4.0, yc))
        vr = (U.in2[0], U.in2[1] - 0.7)
        S.wire(U.in2, vr)
        S.text((vr[0], vr[1] - 0.1), "$V_{ref}$", ha="center", va="top")
        xo, yo = U.out[0] + sg * 0.5, U.out[1]
        S.wire(U.out, (xo, yo))
        S.dot((xo, yo))
        S.wire((xo, yo), (xo, 9.0))
        S.cap((xo, 9.0), P_(4.0, 9.0), text="$C_I$", side="top")
        S.wire(P_(4.0, 9.0), P_(4.0, yc))
        to = (xo + sg * 0.7, yo)
        S.wire((xo, yo), to)
        S.terminal(to, f"$o_{tag}$", side="top")
        S.wire((xo, yo), (xo, 5.6))
        S.res((xo, 5.6), (xo, 3.6), text="$R_F$", side=lab("right"))
        S.wire((xo, 3.6), (xo, ys))
        S.dot((xo, ys))
        S.wire(J.source, (xj, ys), (xo, ys))
        S.dot((xj, ys))
        S.text((xj - sg * 0.15, ys + 0.2), f"$s_{tag}$", ha="right" if not m else "left", va="bottom")
        S.wire((xj, ys), (xj, 1.4))
        S.isource((xj, 1.4), (xj, -0.4), text="$I_D$", side=lab("left"))
        S.supply((xj, -0.4), "$-V$", up=False)
        return xo

    S.text((-0.4, 10.5), "(a)", ha="left", va="center")
    xo_a = side(False)
    side(True)
    S.wire((xo_a, 2.0), (ax - 1.0, 2.0))
    S.res((ax - 1.0, 2.0), (ax + 1.0, 2.0), text="$R_G$", side="bottom")
    S.wire((ax + 1.0, 2.0), (2 * ax - xo_a, 2.0))
    S.text((ax, -0.9), "$G = 1 + 2R_F/R_G$", ha="center", va="center")

    # (b) the differential half-circuit with its noise generators
    dy = -0.8
    S.text((-0.4, -2.6 + dy), "(b)", ha="left", va="center")
    g = (3.4, -9.0 + dy)
    J = S.njfet(g, mirror=True)
    xj = J.drain[0]
    yc, ys = -6.2 + dy, -11.5 + dy
    S.wire(g, (2.2, g[1]))
    S.vsource((2.2, g[1] - 1.8), (2.2, g[1] - 0.4), text="$e_{FET}$", side="left")
    S.wire((2.2, g[1] - 0.4), (2.2, g[1]))
    S.ground((2.2, g[1] - 1.8))
    S.wire(J.drain, (xj, yc))
    S.wire((xj, yc), (xj, yc + 0.4))
    S.res((xj, yc + 0.4), (xj, yc + 2.0), text="$R_D$", side="right")
    S.ground((xj, yc + 2.0), flip=True)
    xi = xj - 1.4
    S.isource((xi, yc + 2.0), (xi, yc + 0.4), text="$i_{n,RD}$", side="left")
    S.ground((xi, yc + 2.0), flip=True)
    S.wire((xi, yc + 0.4), (xi, yc), (xj, yc))
    S.dot((xj, yc))
    S.text((xj + 0.15, yc + 0.2), "$c$", ha="left", va="bottom")
    xa, xn, xin = xj + 1.2, xj + 2.0, xj + 2.8
    U = S.opamp((xj + 3.6, yc), minus_on_top=False)
    S.wire((xj, yc), (xa, yc), (xn, yc), (xin, yc), U.in1)
    for x in (xa, xn, xin):
        S.dot((x, yc))
    S.cap((xn, yc), (xn, yc - 1.4), text="$C_{node}$", side="left")
    S.ground((xn, yc - 1.4))
    S.wire((xin, yc), (xin, yc - 0.3))
    S.isource((xin, yc - 0.3), (xin, yc - 1.9), text="$i_{n,A}$", side="right")
    S.ground((xin, yc - 1.9))
    S.wire(U.in2, (U.in2[0], U.in2[1] + 0.3))
    S.vsource((U.in2[0], U.in2[1] + 0.3), (U.in2[0], U.in2[1] + 1.7), text="$e_{n,A}$", side="right")
    S.ground((U.in2[0], U.in2[1] + 1.7), flip=True)
    xo, yo = U.out[0] + 0.5, U.out[1]
    yci = U.in2[1] + 2.7
    S.wire(U.out, (xo, yo))
    S.dot((xo, yo))
    S.wire((xo, yo), (xo, yci))
    S.cap((xo, yci), (xa, yci), text="$C_I$", side="top")
    S.wire((xa, yci), (xa, yc))
    S.wire((xo, yo), (xo + 0.9, yo))
    S.terminal((xo + 0.9, yo), "$e_o$", side="right")
    S.wire((xo, yo), (xo, yo - 0.8))
    S.vsource((xo, yo - 0.8), (xo, yo - 2.2), text="$e_{n,RF}$", side="right")
    S.wire((xo, yo - 2.2), (xo, yo - 2.6))
    S.res((xo, yo - 2.6), (xo, yo - 4.2), text="$R_F$", side="right")
    S.wire((xo, yo - 4.2), (xo, ys))
    S.wire(J.source, (xj, ys), (xo, ys))
    S.dot((xj, ys))
    S.text((xj - 0.15, ys + 0.2), "$s$", ha="right", va="bottom")
    xt = xj + 1.8
    S.dot((xt, ys))
    S.wire((xt, ys), (xt, ys - 0.4))
    S.isource((xt, ys - 0.4), (xt, ys - 2.0), text="$i_{n,T}$", side="right")
    S.ground((xt, ys - 2.0))
    S.wire((xj, ys), (xj, ys - 0.4))
    S.res((xj, ys - 0.4), (xj, ys - 2.0), text="$R_G/2$", side="left")
    S.wire((xj, ys - 2.0), (xj, ys - 2.3))
    S.vsource((xj, ys - 3.7), (xj, ys - 2.3), text="$e_{n,RG/2}$", side="left")
    S.ground((xj, ys - 3.7))

    # (c) a current sink's noise generators: base at AC ground (the servo's filter), so for noise
    # the transistor is a common-base stage from its emitter node to its collector (the source node)
    S.text((12.2, -2.6 + dy), "(c)", ha="left", va="center")
    bq = (14.6, -8.6 + dy)
    Q = S.npn(bq)
    xc = Q.collector[0]
    y_top = Q.collector[1] + 1.2
    y_e = Q.emitter[1] - 1.4
    S.wire(Q.collector, (xc, y_top))
    S.terminal((xc, y_top), "to $s$", side="top")
    S.wire(bq, (13.3, bq[1]), (13.3, bq[1] + 0.6))
    S.ground((13.3, bq[1] + 0.6), flip=True)
    S.dot((13.9, bq[1]))
    S.isource((13.9, bq[1] - 0.3), (13.9, y_e + 0.3), text="$i_{n,b}$", side="left")
    S.wire((13.9, bq[1]), (13.9, bq[1] - 0.3))
    S.wire((13.9, y_e + 0.3), (13.9, y_e), (xc, y_e))
    S.wire(Q.emitter, (xc, y_e))
    S.dot((xc, y_e))
    S.wire((xc, y_e), (xc, y_e - 0.3))
    S.res((xc, y_e - 0.3), (xc, y_e - 1.9), text="$R_T$", side="left")
    S.ground((xc, y_e - 1.9))
    xn = xc + 1.4
    yc_n = Q.collector[1] + 0.6
    S.wire((xc, yc_n), (xn, yc_n))
    S.dot((xc, yc_n))
    S.isource((xn, yc_n - 0.2), (xn, y_e + 0.2), text="$i_{n,c}$", side="right")
    S.wire((xn, yc_n), (xn, yc_n - 0.2))
    S.wire((xn, y_e + 0.2), (xn, y_e), (xc, y_e))
    S.dot((xn, y_e))
    S.wire((xn, y_e), (xn, y_e - 0.3))
    S.isource((xn, y_e - 1.9), (xn, y_e - 0.3), text="$i_{n,RT}$", side="right")
    S.ground((xn, y_e - 1.9))
    return S


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ss.configure()
    S = sheet_topology()
    S.save(OUT / "schematic_topology")
    if sys.argv[1:] == ["topology"]:
        return
    ok = True
    for case in ("L200",):          # H is drawn with both sides (sheet_front_end_full)
        S, net, scope = sheet_front_end(case)
        ok &= report(S, net, scope, model_alias={"THS4021": "OA_THS4021"})
        S.save(OUT / S.name)
    S, net, scope = sheet_front_end_full("H100")
    ok &= report(S, net, scope, model_alias={"THS4021": "OA_THS4021"})
    S.save(OUT / S.name)
    S, net, scope = sheet_chain()
    ok &= report(S, net, scope, model_alias={"THS4021": "OA_THS4021", "THS4031": "OA_THS4031", "LM7171": "OA_LM7171",
                                             "THS3091": "OA_THS3091"})
    S.save(OUT / S.name)
    S, net, scope = sheet_sr560()
    ok &= report(S, net, scope)
    S.save(OUT / S.name)
    print("all checks passed" if ok else "CHECK FAILURES")


if __name__ == "__main__":
    main()
