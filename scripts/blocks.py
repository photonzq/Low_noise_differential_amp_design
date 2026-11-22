"""Behavioural building blocks written as ngspice subcircuits.

OPN: an op amp with calibrated noise and first-order dynamics.
  Input voltage noise (white part):  a 1-ohm noisy resistor shorted by a 0-V source; its noise
  current, sqrt(4kT/1 ohm) = 1.288e-10 A/rtHz at 27 C, is turned into a voltage in series with the
  non-inverting input by a current-controlled voltage source (H) of gain k = e_n / 1.288e-10.
  Input voltage noise (1/f part): the flicker noise of a diode biased at 10 uA (KF chosen so the
  1/f density equals the white density at the corner frequency fce), sensed through a large
  capacitor and turned into a series voltage the same way.  The diode's shot noise (1.79 pA/rtHz)
  adds to the white part; k_white is reduced so that the total white density stays e_n.
  Input current noise: one shorted noisy resistor per input, its current copied into the input
  by a current-controlled current source (F), with an optional 1/f part from a second diode.
  Dynamics: a transconductance gm1 = 2 pi GBW C1 into C1 || R1 (DC gain A0 = gm1 R1), limited to
  +/- Imax (slew rate Imax / C1), a second pole fp2, and an output stage clamped vsat inside the
  rails behind rout.  Input capacitances cdm (between the inputs) and ccm (each input to ground).
  The supplies draw no current: the model is for the signal path only.

All resistors that are not noise generators are written with the noiseless model rnl.
"""
from __future__ import annotations

import math

KT = 1.380649e-23 * 300.15
Q = 1.602176634e-19
I1OHM = math.sqrt(4 * KT / 1.0)          # noise current of a shorted 1-ohm resistor, A/rtHz
I_DIODE = 10e-6                          # bias of the flicker diodes
SHOT = math.sqrt(2 * Q * I_DIODE)        # shot noise of a flicker diode, A/rtHz

COMMON = ".model rnl r(noisy=0)\n"


def flicker_v(tag: str, n_plus: str, n_minus: str, density: float, f0: float) -> str:
    """A pure 1/f voltage generator between n_plus and n_minus (V(n_plus) - V(n_minus) = noise):
    the flicker current of a diode at I_DIODE, sensed through a large capacitor and turned into
    a voltage by an H source of gain k = 1 mOhm, with KF chosen so that the density is `density`
    at f0.  With so small a k the diode's shot noise contributes k * 1.79 pA/rtHz = 1.8 fV/rtHz,
    nothing."""
    k = 1e-3
    kf = density ** 2 * f0 / (k ** 2 * I_DIODE)
    return (f"If{tag} 0 f{tag} {I_DIODE:g}\nDf{tag} f{tag} 0 dfk_{tag}\nCf{tag} f{tag} fs{tag} 1000\n"
            f"Vf{tag} fs{tag} 0 0\nHf{tag} {n_plus} {n_minus} Vf{tag} {k:g}\n"
            f".model dfk_{tag} d(is=1e-14 n=1 kf={kf:.6g} af=1)\n")


def flicker_i(tag: str, node: str, density: float, f0: float) -> str:
    """A pure 1/f current generator into `node` (density A/rtHz at f0), built as flicker_v but
    with an F source of gain 1e-3 (the diode's flicker current scaled down)."""
    k = 1e-3
    kf = density ** 2 * f0 / (k ** 2 * I_DIODE)
    return (f"If{tag} 0 f{tag} {I_DIODE:g}\nDf{tag} f{tag} 0 dfk_{tag}\nCf{tag} f{tag} fs{tag} 1000\n"
            f"Vf{tag} fs{tag} 0 0\nFf{tag} 0 {node} Vf{tag} {k:g}\n"
            f".model dfk_{tag} d(is=1e-14 n=1 kf={kf:.6g} af=1)\n")


def _flicker_kf(density: float, k: float, fc: float) -> float:
    """KF of a diode at I_DIODE (AF = 1) whose flicker current, scaled by k, equals `density`
    at fc:  (k^2 KF I / fc) = density^2."""
    return density ** 2 * fc / (k ** 2 * I_DIODE)


def opn(name: str, gbw: float, en: float, inoise: float = 0.0, fce: float = 0.0, fci: float = 0.0,
        a0: float = 1e6, fp2: float = 0.0, sr: float = 100e6, c1: float = 10e-12,
        vsat: float = 1.5, rout: float = 10.0, cdm: float = 0.0, ccm: float = 0.0,
        rin_cm: float = 0.0) -> str:
    """ngspice subcircuit 'name' with pins inp inn out vcc vee (see the module docstring).
    gbw in Hz, en in V/rtHz, inoise in A/rtHz, fce / fci the 1/f corners (0: none), sr the slew
    rate in V/s (the transconductance stage is limited to sr * c1)."""
    gm1 = 2 * math.pi * gbw * c1
    imax = sr * c1
    r1 = a0 / gm1
    lines = [f".subckt {name} inp inn out vcc vee"]
    # --- input voltage noise
    if fce > 0:
        # the diode path carries a quarter of the white power (its shot noise, scaled by k_d);
        # the resistor supplies the rest, and the diode's flicker part equals en at fce
        k_d = 0.5 * en / SHOT
        kf = _flicker_kf(en, k_d, fce)
        white_left = math.sqrt(max(en ** 2 - (k_d * SHOT) ** 2, 0.0))
        lines += ["Rnv nv 0 1", "Vnv nv 0 0", f"Hnv inp ip1 Vnv {white_left / I1OHM:.6g}",
                  f"Ifv 0 fv {I_DIODE:g}", "Dfv fv 0 dflk_v", "Cfv fv fvs 1000", "Vfv fvs 0 0",
                  f"Hfv ip1 ip2 Vfv {k_d:.6g}",
                  f".model dflk_v d(is=1e-14 n=1 kf={kf:.6g} af=1)"]
    else:
        lines += ["Rnv nv 0 1", "Vnv nv 0 0", f"Hnv inp ip1 Vnv {en / I1OHM:.6g}", "Vfv ip1 ip2 0"]
    # --- input current noise, one generator per input (same construction, F sources)
    if inoise > 0:
        for pin, tag in (("inp", "p"), ("inn", "n")):
            if fci > 0:
                k_di = 0.5 * inoise / SHOT
                kfi = _flicker_kf(inoise, k_di, fci)
                white_i = math.sqrt(max(inoise ** 2 - (k_di * SHOT) ** 2, 0.0))
                lines += [f"Rni{tag} ni{tag} 0 1", f"Vni{tag} ni{tag} 0 0",
                          f"Fni{tag} 0 {pin} Vni{tag} {white_i / I1OHM:.6g}",
                          f"Ifi{tag} 0 fi{tag} {I_DIODE:g}", f"Dfi{tag} fi{tag} 0 dflk_i{tag}",
                          f"Cfi{tag} fi{tag} fis{tag} 1000", f"Vfi{tag} fis{tag} 0 0",
                          f"Ffi{tag} 0 {pin} Vfi{tag} {k_di:.6g}",
                          f".model dflk_i{tag} d(is=1e-14 n=1 kf={kfi:.6g} af=1)"]
            else:
                lines += [f"Rni{tag} ni{tag} 0 1", f"Vni{tag} ni{tag} 0 0",
                          f"Fni{tag} 0 {pin} Vni{tag} {inoise / I1OHM:.6g}"]
    # --- input capacitances and common-mode resistance
    if cdm > 0:
        lines.append(f"Cdm inp inn {cdm:g}")
    if ccm > 0:
        lines += [f"Ccmp inp 0 {ccm:g}", f"Ccmn inn 0 {ccm:g}"]
    if rin_cm > 0:
        lines += [f"Rcmp inp 0 {rin_cm:g} rnl", f"Rcmn inn 0 {rin_cm:g} rnl"]
    # --- dynamics
    lines += [f"Bg 0 n1 I={imax:g}*tanh({gm1:.6g}*(V(ip2)-V(inn))/{imax:g})",
              f"R1 n1 0 {r1:.6g} rnl", f"C1 n1 0 {c1:g}"]
    if fp2 > 0:
        lines += ["E2 n2 0 n1 0 1", "R2 n2 n3 1 rnl", f"C2 n3 0 {1 / (2 * math.pi * fp2):.6g}"]
    else:
        lines += ["E2 n3 0 n1 0 1"]
    lines += [f"Bo no 0 V=min(max(V(n3), V(vee)+{vsat:g}), V(vcc)-{vsat:g})",
              f"Ro no out {rout:g} rnl", COMMON.strip(), f".ends {name}"]
    return "\n".join(lines) + "\n"
