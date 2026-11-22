# Literature notes: ultra-low-noise differential JFET voltage preamplifier

Compiled 2026-11-19 for the design report on a differential voltage preamplifier intended to improve on the SRS SR560 (4 nV/√Hz, 100 MΩ ∥ 25 pF, DC–1 MHz), with DC–10 MHz bandwidth and two front ends (high-impedance, about 20–40 pF; paralleled JFETs for 0.3–0.5 nV/√Hz).

**Conventions.** Page numbers are those printed on the document unless "PDF p." is given. Equation, figure and table numbers are the source's own. Every entry carries an **Access** line stating what was actually read: "full text", "pages …", "abstract only" or "citation only". Text marked **[derived]** is a short algebraic consequence written for this report and is not printed in the cited source. Files are in this folder unless another path is given; download URLs are listed in `README.md`.

**Layout.**
- Part A: *The Art of Electronics* (3rd ed.) and *The x-Chapters*: what could and could not be verified.
- Part B: Noise-matching theory (optimum source resistance, noise figure, capacitive matching, $\gamma$, gate-resistance and induced-gate noise, 1/f noise, ENC).
- Part C: Published low-noise JFET preamplifier designs and measurement methods.
- Part D: Vendor application notes, data sheets and reference designs.
- Part E: CMRR of difference and current-feedback instrumentation-amplifier topologies.
- Part F: Comparison table of measured designs.
- Part G: Gaps and items not accessed.

---

## Part A. *The Art of Electronics*, 3rd ed., and *The x-Chapters*

### A1. Horowitz and Hill, *The Art of Electronics*, 3rd ed. (2015)

- **Citation:** P. Horowitz and W. Hill, *The Art of Electronics*, 3rd ed., Cambridge University Press, Cambridge, 2015. ISBN 978-0-521-80926-9.
- **Files (author-hosted, free downloads from artofelectronics.net):** `Horowitz_2015_AoE3_TableOfContents.pdf` (17 pp., each page stamped "Sample from Horowitz and Hill: Art of Electronics 3rd edition. Copyright Cambridge University Press 2015"); `Horowitz_2016_AoE3_SubjectIndex_30Nov16.pdf` and `Horowitz_2016_AoE3_PartsIndex_30Nov16.pdf` (the authors' "FINAL" indexes, corrected 30 Nov 2016).
- **Access:** the book text itself was **not** read. Google Books shows "No preview available" for this edition (checked 2026-11-19). The table of contents (TOC pp. xiii–xiv and the List of Tables, p. xxii) was read as rendered page images; the two indexes were searched by text extraction. No pirated copy was consulted. The only sample chapter offered by the authors is Chapter 9 (voltage regulation), which was not used.
- **Verified from the table of contents (section, printed page):**
  - Chapter 8 "Low-Noise Techniques", p. 473.
  - 8.5 Low-noise design with bipolar transistors, 492; 8.5.6 Minimizing noise: BJTs, FETs, and transformers, 496; 8.5.9 An extreme low-noise design challenge, 505.
  - **8.6 Low-noise design with JFETs, 509**: 8.6.1 Voltage noise of JFETs, 509; 8.6.2 Current noise of JFETs, 511; **8.6.3 Design example: low-noise wideband JFET "hybrid" amplifiers, 512**; **8.6.4 Designs by the masters: SR560 low-noise preamplifier, 512**; **8.6.5 Selecting low-noise JFETs, 515**.
  - 8.7 Charting the bipolar–FET shootout, 517; 8.7.1 What about MOSFETs?, 519.
  - 8.8 Noise in differential and feedback amplifiers, 520.
  - 8.9 Noise in operational amplifier circuits, 521; 8.9.4 Low-noise instrumentation amplifiers and video amplifiers, 533; 8.9.5 Low-noise hybrid op-amps, 534.
  - 8.10 Signal transformers, 535; 8.10.1 A low-noise wideband amplifier with transformer feedback, 536.
  - 8.11 Noise in transimpedance amplifiers, 537; 8.11.3 The $e_nC$ noise problem, 538; 8.11.5 An example: wideband JFET photodiode amplifier, 540; 8.11.9 Reducing input capacitance: bootstrapping the transimpedance amplifier, 547; 8.11.10 Isolating input capacitance: cascoding the transimpedance amplifier, 548.
  - 8.12 Noise measurements and noise sources, 555; 8.13 Bandwidth limiting and rms voltage measurement, 561 (8.13.4 Finding the 1/f corner frequency, 566); 8.14 Signal-to-noise improvement by bandwidth narrowing, 574; 8.15 Power-supply noise, 578 (8.15.1 Capacitance multiplier, 578); 8.16 Interference, shielding, and grounding, 579.
  - List of Tables: **Table 8.2 "Low-noise Junction FETs (JFETs)", p. 516**; Table 8.1a Low-noise BJTs, 501; Table 8.1b Dual low-noise BJTs, 502; Tables 8.3a/b/c low-noise BJT-input, FET-input and high-speed op-amps, 522–524; Table 8.4 Noise integrals, 564; Table 3.1 JFET mini-table, 141; Table 3.7 Junction field-effect transistors, 217; Table 5.8 Selected instrumentation amplifiers, 363.
- **Verified from the subject index** (index legend: g = graph, n = footnote, t = tabular, T = table, ff = and following pages):
  - JFET noise: "reduction by paralleling, 509"; "vs BJT, 517".
  - JFET voltage noise: 346, 509–511, 518–520g; "theory vs measurement, 509g"; "vs frequency, 510g"; "vs transconductance, 509g". JFET 1/f noise: 510, 517g. Johnson noise "in JFET channel, 509".
  - JFET capacitance: 157, 164, 170, 510, 519. JFET current noise: 511g, 511. JFET gate current: 509, 511, 511g (among other pages).
  - JFET amplifier, instrumentation: 512, 513. JFET differential amplifier: 152, 343, 512, 513. JFET hybrid amplifier: 151, 153g, 155g, 343, 344, 512, 513, 544. Low-noise JFETs: 516t; selecting: 515.
  - "Designs by the masters … SR560 preamp, 512ff, 514".
  - Instrumentation amplifier entries: "hybrid, 513"; "JFET-input, 512"; "discrete, 361"; "roll-your-own, 359"; "CMRR vs Rsource mismatch, 366g"; "noise depends on gain, 358".
- **Verified from the parts index:**
  - SRS SR560: 492, 492g, 512, 514, 535.
  - LSK389: 154, 154g, 155, 155g, 160, 161g, 217T, 477n, 510, 510g, 512, 513, 514, 515, 516T, 517, 518g, 534, 535. 2SK389: 154n, 512n, 535 (cross-referenced to LSK389).
  - 2SK170 / LSK170: 2SK170 at 494, 510, 510g, 515, 516T, 517, 518g, 518n, 519, 520g; LSK170 at 510g, 515, 516T, 519.
  - IF3601: 510n, 516T, 518T, 519, 520g, 529g. IF3602: 516T, 544–546, 546g (and earlier pages). IFN146: 510, 516T, 517, 518g, 519. BF862: 516T, 518g, 536–550. PN4117: 510, 510g, 516T, 518g.
  - LT1028: 506, 508g, 513, 514, 521, … OP37: 514. INA103: 306n, 358, 363T, 364g, 366, 533.
- **What this establishes:** the book treats paralleling JFETs for lower noise (p. 509), plots JFET voltage noise against transconductance and against theory (p. 509 graphs) and against frequency (p. 510 graph), discusses JFET capacitance in the noise section (pp. 510, 519), has a measured-noise comparison graph of many JFET types (p. 518; IF3601, 2SK170, BF862, IFN146, PN4117 and others are indexed to 518g), a low-noise JFET selection table (Table 8.2, p. 516), JFET-input instrumentation and differential amplifiers (pp. 512–513), and a "Designs by the masters" description of the SR560 (pp. 512–514) in which LSK389/2SK389, LT1028 and OP37 are indexed on the same pages.
- **Not verified (book text not accessible):** the content of §8.6.3–8.6.5, the SR560 circuit description and its stated performance, the numbers in Table 8.2, the measured $e_n$-versus-$I_D$ values in the graphs, and any statement about the $e_n$–$C_{iss}$ trade-off beyond the index entries above. These should be read in a library or personal copy before being quoted.

### A2. Hill and Horowitz, *The Art of Electronics: The x-Chapters* (2020)

- **Citation:** W. Hill and P. Horowitz, *The Art of Electronics: The x-Chapters*, Cambridge University Press, Cambridge, 2020.
- **Files (author-hosted on x.artofelectronics.net):** `Hill_2020_AoE_xChapters_TableOfContents.pdf`, `Hill_2020_AoE_xChapters_SubjectIndex.pdf`, `Hill_2020_AoE_xChapters_PartsIndex.pdf`, and two free sample sections, `Hill_2020_AoE_xChapters_Sec2x1_BJT_JFET_Leakage_sample.pdf` (§2x.1) and `Hill_2020_AoE_xChapters_Sec9x14_LowNoise_Isolated_Power_sample.pdf` (§9x.14).
- **Access:** table of contents read as images (all 7 pp.); indexes searched by text; §2x.1 (1 p.) read as an image; §9x.14 first page read by text extraction. The book text otherwise not read.
- **Key finding: the published x-Chapters volume has no Chapter 8x.** Its chapters are ONE (1x, Real-World Passive Components), TWO (2x, Advanced BJT Topics), THREE (3x, Advanced FET Topics, p. 156), FOUR (4x, Advanced Topics in Operational Amplifiers) and NINE (9x, Advanced Topics in Power Control), followed by the parts and subject indexes (TOC pp. vii–xiii). Material on low-noise techniques that one might expect in an "8x" chapter is therefore not available in this volume.
- **Relevant sections (TOC):** 2x.1 What's the actual leakage current of BJTs and JFETs?, 102; 2x.2 Current-source problems and fixes, 103; 3x.1 A guided tour of JFETs, 161 (3x.1.1 Gate current, $I_{GSS}$ and $I_G$, 166); 3x.2 A closer look at JFET transconductance, 169 (3x.2.1 Dependence of $g_m$ on $I_D$, 169; 3x.2.4 Transconductance in the JFET source follower, 172); 3x.3 Measuring JFET transconductance, 174; 3x.4 A closer look at JFET output impedance, 175; **3x.4.6 Example: a low-noise open-loop differential amplifier, 178**; 4x.4.1 Stability of the composite amplifier, 299; 9x.14 Low-noise isolated power, 432; 9x.20 The capacitance multiplier, revisited, 451; 9x.21 Precision low-noise laboratory power supply, 453.
- **Indexes:** subject index lists "amplifier … JFET differential, 178, 179"; "low-noise, 178, 179". Parts index places LSK389 at 162T, 167g, 170g, 171t, 179 and LSK170 at 161, 162T, 165, 167g, 170g, so the §3x.4.6 low-noise open-loop differential amplifier (pp. 178–179) is indexed together with the LSK389; a JFET table on p. 162 lists, among others, 2SK170, LSK170, LSK389, BF861B, IFN146 (parts index "162T").
- **§2x.1 (sample, p. 102), read:** room-temperature measurements of off-state leakage. Fig. 2x.1: collector leakage of small-signal BJTs at $V_{BE}=0$, mostly well below 1 nA. Fig. 2x.2: channel (source) current versus gate–source voltage for JFETs in the off state (2N5457, 2N5460, J309, J175, 2SJ74BL, LSK170B, LSK389B, BF861A/B, BF862, PMBF4395) at $V_{DS}=5$ V, typically 0.05–3 pA; the text warns that leakage roughly doubles per 10 °C and that unspecified parameters cannot be relied on without incoming tests. Relevance here is limited (off-state leakage, not amplifier gate current).
- **§9x.14 (sample), first page read:** isolated DC–DC converters for low-level analog front ends inject common-mode switching noise; the section addresses that problem (useful for the supply design of the preamplifier).
- **Not verified:** the content and performance of the §3x.4.6 amplifier and of the p. 162 JFET table.

---

## Part B. Theory of noise matching for low-noise FET front ends (sources T1–T16)

Compiled 2026-11-19. Scope: optimum source resistance and noise figure, capacitive matching (constant current density versus constant total current), FET channel noise factor $\gamma$, gate-leakage and gate-resistance noise, induced gate noise, 1/f noise scaling, ENC formalism, paralleling of input devices.

Conventions. $e_n$, $i_n$ (or $v_n$, $V_n$, $I_n$) are input-referred noise densities as defined in each source. "p." is the page number printed on the document; "PDF p." is used only where the two differ and the distinction matters. Equations are transcribed with the source's own equation numbers. Anything marked **[derived]** is a short algebraic consequence written for this report and is not printed in the cited source.





### T1. Radeka (2020), open-access book chapter

- **Citation:** V. Radeka, "Signal Processing for Particle Detectors," Chapter 10 in C. W. Fabjan and H. Schopper (eds.), *Particle Physics Reference Library, Vol. 2: Detectors for Particles and Radiation*, Springer, Cham, 2020, pp. 439–484. DOI: 10.1007/978-3-030-35318-6_10. Licence: CC BY 4.0 (statement on p. 484; also in Crossref metadata).
- **File:** `Radeka_2020_Signal_Processing_for_Particle_Detectors.pdf`
- **Access:** full chapter downloaded. Printed pp. 450–453, 455–457 and 459–463 read as rendered page images; other pages only located by text search.
- **Contributions:**
  - Sect. 10.3.3, p. 450, Eq. (10.4): for 1/f noise $\sigma^2 \propto \int_{f_l}^{f_h} df/f = \ln(f_h/f_l)$, constant for fixed $f_h/f_l$; hence the 1/f contribution to ENC does not depend on the shaping time.
  - Sect. 10.4.1, pp. 450–451, Fig. 10.12: series white, series 1/f, parallel white and parallel "f" (dielectric) sources acting on $C_{in}=C_{det}+C_{par}+C_{amp}$. The text stresses that the different location of the series and parallel sources relative to the input capacitance is what makes their effect so different.
  - Sect. 10.4.2, p. 451, Eq. (10.5): $ENC^2=\tfrac12 e_n^2C_{in}^2 I_1+\pi C_{in}^2A_f I_2+\tfrac12 i_n^2 I_3$, with $e_n^2=4kTR_s$ (series noise resistance), series 1/f density $A_f/f$ [V²/Hz], and $i_n^2=2qI_0=4kT/R_p$.
  - p. 452, Eqs. (10.6)–(10.8): $I_1=\int[w'(t)]^2dt=\frac{1}{2\pi}\int|H(j\omega)|^2\omega^2d\omega=A_1/\tau$; $I_2=\int[w^{(1/2)}(t)]^2dt=\frac{1}{2\pi}\int|H|^2\omega\,d\omega=A_2$; $I_3=\int[w(t)]^2dt=\frac{1}{2\pi}\int|H|^2d\omega=A_3\tau$.
  - p. 453, Eq. (10.9): $\tau_{opt}=(R_sR_p)^{1/2}C_{in}(A_1/A_3)^{1/2}$, not affected by 1/f noise (Fig. 10.14: 1/f raises the ENC minimum but does not move it).
  - Sect. 10.4.4, p. 455, Eqs. (10.10)–(10.12): $ENC_s^2=\tfrac12e_n^2C_{in}^2I_1$, $I_1=2/t_m=A_1/t_m$ (triangle with peaking time $t_m$), $ENC_s=e_nC_{in}/t_m^{1/2}$.
  - p. 456, Eq. (10.13): noise slope versus input capacitance $\partial(ENC_s/q_e)/\partial C=e_n/t_m^{1/2}$ [rms electrons/pF]. Same page: "a primary objective of low noise amplifier design is to make the noise contributions of all other circuit components negligible compared to the input transistor" (paraphrase of the italic sentence). Eq. (10.14): $ENC_p=(q_eI_0t_G)^{1/2}$ for a gated integrator; $I_3=(2/3)t_m$ for a triangle.
  - p. 457: the "50 mV rule": a dc current $I_0$ that drops about 50 mV across $R_p$ gives shot noise equal to the thermal noise of $R_p$ ($R_pI_0=2kT/q_e$).
  - Sect. 10.4.6, p. 457, Eq. (10.15): $ENC_f^2=\pi C_{in}^2A_fA_2$. p. 459, Eqs. (10.19)–(10.23): Cauchy–Schwarz bound on $A_2$ (Eq. (10.20) is printed as $A_2\le(A_1A_2)^{1/2}$; from Eq. (10.19) the intended form is $(A_1A_3)^{1/2}$), $A_2\approx0.75(A_1A_3)^{1/2}$ (10.21), so $ENC_f^2\approx\pi C_{in}^2A_f\,(0.75\sqrt{A_1A_3})$ (10.23). $A_2=1.00$ (Gaussian), 0.88 (triangular), 1.02 (4th-order semi-Gaussian), 1.18 (CR–RC).
  - pp. 459–460: size-independent 1/f figure of merit $K_f=A_fC_{gs}$ [J]; "ranges from $10^{-27}$ J for junction field-effect transistors (JFETs) to ~$10^{-25}$ J for p-channel and ~$10^{-24}$ J for n-channel MOS transistors." Equivalently $A_f=K_f/C_{gs}$: within one technology the input-referred 1/f power density falls inversely with gate capacitance.
  - Sect. 10.4.7, p. 460, Eqs. (10.24)–(10.26): dielectric-loss noise $i_n^2=4kTG(\omega)=4kTD\omega C_{diel}$, $ENC_{diel}^2=2kTDC_{diel}A_2\approx2.4kTDC_{diel}$. Examples: 1 pF of glass-fibre board ($D\approx2\times10^{-2}$) gives about 86 rms electrons; Teflon, polystyrene or quartz ($D\approx5\times10^{-5}$) about 5. Relevant to the insulation at a high-impedance input.
  - Sect. 10.5.1, p. 461, Eq. (10.27): $C_{gs}=g_m\tau_e$, $f_T\approx1/(2\pi\tau_e)=(1/2\pi)(g_m/C_{gs})$.
  - Sect. 10.5.2, pp. 461–462: channel noise expressed as series noise resistance $\gamma/g_{ms}$ "with $\gamma$ typically in the range 0.5 to 1.0"; second term of Eq. (10.28) is induced gate noise with coefficient $\delta/5\gamma$, "for estimation purposes $(\delta/5\gamma)\sim1/3$"; usually negligible with capacitive sources, particularly when $C_{gs}/C_{in}$ is small. Eq. (10.28), p. 462 (NMOS, Fig. 10.20):
    $$\frac{R_{eq}}{\gamma/g_{ms}}=1+\frac{\delta}{5\gamma}\left(\frac{C_{gs}}{C_{in}}\right)^2+\frac{1}{\gamma}(R_gg_{ms})+(R_bg_{mb})\frac{g_{mb}}{g_{ms}}+\frac{1}{\gamma}(R_bg_{ms})\left(\frac{C_{gb}}{C_{in}}\right)^2 .$$
    For a JFET only the channel, induced-gate and gate-resistance terms have direct counterparts.
  - Sect. 10.5.3, pp. 462–463, Figs. 10.21–10.22: charge sharing among detector, amplifier and stray capacitance; control charge $\Delta Q_c=Q_s/[1+(C_{det}+C_{gsp}+C_{ds})/C_{gs}]$ (Fig. 10.22 caption). p. 463: scaling the device width "with no power limitation" for best S/N requires $C_{gs}=C_{det}$. Eq. (10.29): $ENC_{s\,opt}\cong2\sqrt2\sqrt{kTC_{gs}}\sqrt{\tau_e/t_m}$, assuming $\gamma\sim1$. Matching is said to be treated in detail in Ref. [10] (G. De Geronimo, "Low-Noise Electronics for Radiation Sensors," in K. Iniewski (ed.), *Medical Imaging*, Wiley, 2009, p. 127), which was not accessed.

### T2. Radeka (1988), Annual Review (not accessed)

- **Citation (verified from Crossref metadata and from Ref. [9] of T1):** V. Radeka, "Low-Noise Techniques in Detectors," *Annu. Rev. Nucl. Part. Sci.* 38 (1988) 217–277. DOI: 10.1146/annurev.ns.38.120188.001245 (the alias 10.1146/annurev.nucl.38.1.217 redirects to it).
- **Access:** not read. The publisher site refused automated access (HTTP 403) and Crossref lists no open licence. A copy on a third-party aggregator appeared in search results but was not downloaded because its permission status is unclear. T1 by the same author is the open, citable substitute for capacitive matching, ENC formalism and 1/f coefficients; obtain the 1988 review through a library if it must be cited directly.

### T3. Spieler (1999), lecture notes "Noise in Transistors"

- **Citation:** H. Spieler, "IX.5. A Semiconductor Device Primer – Noise in Transistors," course notes for *Introduction to Radiation Detectors and Electronics* (UC Berkeley Physics 198, Spring 1999), LBNL, dated 20 Apr 1999, 29 pp. URL: https://www-physics.lbl.gov/~spieler/physics_198_notes_1999/PDF/IX-5-Noise.pdf
- **File:** `Spieler_1999_Noise_in_Transistors_LectureNotes.pdf`
- **Access:** pp. 1–6, 8, 9 and 18–22 read as rendered images; p. 7 and p. 17 by text extraction only. Printed page numbers equal PDF pages.
- **Contributions:**
  - p. 1: drain noise current $i_{nd}^2=\frac{N_{C,tot}q_e}{L^2}\mu_0\,4k_BT_e$; with $g_m\propto(W/L)\mu N_{ch}d$ this becomes $i_{nd}^2=\gamma_n g_m 4k_BT_0$ ($T_0=300$ K), $\gamma_n$ semi-empirical, dependent on carrier concentration and geometry.
  - p. 2: in a JFET the gate noise current is the shot noise of the gate–channel reverse current (printed as $i_{ng}=2q_eI_G$, meaning the spectral density $i_{ng}^2=2q_eI_G$); gate and drain noise currents independent; an impedance $Z$ from gate to source turns $i_{ng}$ into a gate voltage, giving $v_{ni}^2=i_{nd}^2/g_m^2+(Zi_{ng})^2\equiv v_n^2+(Zi_n)^2$ (the last terms are printed as $Zi_{ng}^2$, $Zi_n^2$); referred to the input $v_n^2=4k_BT_0\gamma_n/g_m$.
  - p. 3: "The noise coefficient $\gamma_n$ is usually given as 2/3, but is typically in the range 0.5 to 1"; the expression applies to JFETs and MOSFETs. ENC: $Q_n^2=i_n^2F_iT_S+v_n^2C_i^2F_v/T_S$. Example JFET: $g_m=0.02$ S, $C_i=10$ pF, $I_G<150$ pA, $F_i=F_v=1$ gives $Q_n^2=1.9\times10^9T_S+3.25\times10^{-3}/T_S$; at $T_S=1\,\mu$s the current-noise part is 43 el and the voltage-noise part 3250 el.
  - p. 4 ("Optimization of Device Width"): at fixed $I_D/W$, $g_m\propto W$ and $C_i\propto W$, so $g_m/C_i$ is constant;
    $$\left(\frac SN\right)^2=\frac{(Q_s/C)^2}{v_n^2}=\frac{Q_s^2}{(C_{det}+C_i)^2}\frac{g_m}{4k_BT_0\Delta f}=\frac{Q_s^2}{\Delta f}\frac{1}{4k_BT_0}\left(\frac{g_m}{C_i}\right)\frac{1}{C_i\,(1+C_{det}/C_i)^2},$$
    maximized for $C_i=C_{det}$ ("capacitive matching"). Below the match, widening lowers $v_n$; above it $v_n$ falls only as $1/\sqrt W$ and the added capacitance wins. (These lines take $\gamma_n=1$ implicitly.)
  - p. 5: $v_{ni}^2=4k_BT(\gamma_n/g_m+R_G+R_S)$; noise stops improving with current once parasitic gate and source resistances matter. Because $R_G$ and $R_S$ scale as $1/W$, their relative weight is the same for all widths at constant $I_d/W$.
  - p. 6: therefore tailor the FET to the source by scaling $W$ at constant $I_d/W$. With $g_m'=g_m/W$, $C_i'=C_i/W$, $v_n'=v_n\sqrt W$:
    $Q_n^2=4k_BT_0\frac{\gamma_n}{Wg_m'}\frac{F_v}{T_S}(C_d+C_s+WC_i')^2$, minimum at $WC_i'=C_d+C_s$:
    $Q_{n,min}=\sqrt{\frac{16k_BT_0}{\kappa_n}\frac{F_v}{T_S}(C_d+C_s)}$, with the FET figure of merit $\kappa_n\equiv g_m/(\gamma_nC_i)$.
  - p. 7 (text extraction): CMOS example, 1.2 µm, $I_d/W=0.3$ A/m, $g_m/C_i=3\times10^9$ s⁻¹, $\gamma_n=1$, CR–RC 20 ns, $C_d+C_s=7.5$ pF: $Q_{n,min}=88$ aC = 546 el at $W=5$ mm and 1.5 mA.
  - p. 8: table of measured $\gamma_n$ for NMOS and PMOS (W = 75–1332 µm, L = 1.2–3.2 µm) at $I_d/W$ = 0.03, 0.1, 0.3 A/m. Unirradiated values: 0.50–0.81 at 0.03 A/m, 0.60–1.20 at 0.1 A/m, 0.77–2.00 at 0.3 A/m; short-channel NMOS highest. MOS data only; no JFET values on this page.
  - p. 9: 1/f adds a shaping-time-independent term $Q_{nf}^2\propto A_fC_{tot}^2$; "for some forms of 1/f noise" $A_f=K_f/(WLC_g^2)$ ($C_g$ = gate–channel capacitance per unit area); typical $K_f$: p-MOSFET $\approx10^{-32}$ C²/cm², n-MOSFET $\approx4\times10^{-31}$ C²/cm², JFET $\approx10^{-33}$ C²/cm². The model is not universal (several slopes are common in PMOS), but devices with larger gate area $W\cdot L$ tend to have better 1/f behaviour. (Note: this $K_f$ is normalized differently from the $K_f$ of T1 [J], so the numbers are not directly comparable.)
  - pp. 18–22 ("Noise Optimization – Capacitive Matching Revisited"), array of $n$ voltage-sensing amplifiers whose outputs are summed:
    - pp. 19–20, current noise: $i_n=\sqrt n\,i_n'$; $N(n)=A\,n\,i_n'Z_i$; $S(n)=nAi_sZ_i$; S/N equals that of one amplifier, so paralleling gives nothing when only current noise is present, and input capacitance is then irrelevant.
    - p. 20: voltage noise is not additive at the input (it originates inside each device and appears only across that device's own input).
    - p. 21: with per-amplifier $v_n'$, $C_i'$ and $C=C_{det}+nC_i'$: $\frac{S(n)}{N(n)}=\sqrt n\frac{S'}{N'}=\frac{Q_s}{v_n'/\sqrt n}\cdot\frac{1}{C_{det}+nC_i'}$, maximum at $C_{det}=nC_i'$; then $\frac SN=\frac{Q_s}{v_n'}\sqrt{\frac{C_{det}}{C_i'}}\frac{1}{2C_{det}}$.
    - p. 22: $\frac SN=\frac12\frac{Q_s}{v_n'\sqrt{C_i'}}\frac{1}{\sqrt{C_{det}}}$. Valid only if (1) the device noise decreases with increasing input capacitance and (2) the input capacitance is scaled with the source capacitance; "if the noise voltage of a device and its input capacitance are not correlated, capacitive matching is deleterious" (example: MOSFET in weak inversion).
    - p. 17 (text extraction): capacitive matching does not apply to bipolar transistors.

### T4. Spieler (2001), lecture notes "Electronic Noise"

- **Citation:** H. Spieler, "III. Electronic Noise," in *Radiation Detectors and Signal Processing*, lecture notes, Univ. Heidelberg, 8–12 Oct 2001, LBNL, 39 pp. URL: https://www-physics.lbl.gov/~spieler/Heidelberg_Notes_2001/pdf/III_Electronic_Noise.pdf
- **File:** `Spieler_2001_Electronic_Noise_LectureNotes.pdf`
- **Access:** pp. 23–26 read as rendered images (only the noise-matching pages).
- **Contributions:**
  - p. 23: $e_{ni}^2=4kTR_S+e_n^2+(i_nR_S)^2$; total input-circuit noise power $P_n=(4kT+e_n^2/R_S+i_n^2R_S)B$ is minimum at $R_S=e_n/i_n$, set by the amplifier alone. Derived for a real (resistive) source; for capacitive or inductive sources the condition may apply "but for other reasons".
  - p. 24: noise factor $F=\frac{e_{ni}^2}{4kTR_S}=1+\frac{e_n^2}{4kTR_S}+\frac{i_n^2R_S}{4kT}$, minimum at $R_S=e_n/i_n$; $NF=10\log F$; "In a matched system with a resistive source" $F_{opt}=1+\frac{e_ni_n}{2kT}$. Cautions: the minimum noise voltage always occurs at $R_S=0$; increasing the source resistance raises $e_{ni}$ without improving S/N; matching helps only when signal and source resistance are transformed together (transformer).
  - p. 25: transformer of ratio $N=N_S/N_P$: $e_{ni}^2=4kTR_SN^2+e_n^2+R_S^2N^4i_n^2$; $(S/N)^2=V_S^2/(4kTR_S+e_n^2/N^2+N^2R_S^2i_n^2)$, maximum at $R_SN^2=e_n/i_n$.
  - p. 26: noise resistance $R_n=(e_n^2+i_n^2R_S^2)/(4kT)$; noise temperature $T_n=\frac{e_n^2}{4kR_S}+\frac{i_n^2R_S}{4k}$, minimum at $R_S=e_n/i_n$ with $T_N=\frac{e_ni_n}{2k}$.

### T5. Spieler (2005), book table of contents (location pointers only)

- **Citation:** H. Spieler, *Semiconductor Detector Systems*, Oxford University Press, 2005. Author-hosted table of contents: https://www-physics.lbl.gov/~spieler/book/Semiconductor_Detector_Systems_TOC.pdf
- **File:** `Spieler_2005_Semiconductor_Detector_Systems_TOC.pdf`
- **Access:** table of contents only (read by text extraction); the book itself was not read.
- **Use:** section locations for citing the book: 3.9 Amplifier noise matching (p. 121), 3.9.1 Resistive sources (121), 3.9.2 Noise matching with a transformer (122), 3.10 Capacitive sources (123), 3.10.1 Noise vs. capacitance in a charge-sensitive amplifier (123), 3.10.2 S/N vs. input time constant (125), 6.3.1 Noise in field effect transistors (243), 6.3.2 Low-frequency excess noise ("1/f noise") (248), 6.3.4 Comparison between bipolar and field effect transistors (251), 6.3.5 Noise optimization – capacitive matching revisited (252), 6.4 Composite amplifiers (256). The section titles match those of T3/T4; whether the book text is identical was not checked.

### T6. O'Connor, Rehak and Gramegna (1997), Taos workshop slides

- **Citation:** P. O'Connor (BNL), P. Rehak (BNL), G. Gramegna (IMEC), "Monolithic Preamplifiers for Low-Capacitance Detectors," slides headed "Low-Capacitance Preamps – Taos Workshop Nov. 5, 1997," 12 pp., Brookhaven National Laboratory Instrumentation Division web pages (PDF created 3 Nov 1997). Original URL http://www.inst.bnl.gov/programs/microelec/PDF/taos.pdf, retrieved from the University of North Texas "End of Term 2008" web-archive capture.
- **File:** `OConnor_1997_Low_Capacitance_Preamps_Capacitive_Match.pdf`
- **Access:** slides 2 and 4 read as rendered images; slide 1 by text extraction.
- **Contributions:**
  - Slide 2, "Capacitive match":
    1. Constant current density (discrete FETs): $g_m/C_{gs}=\omega_T$ = const; $ENC=K\frac{C_D+C_{gs}}{\sqrt{g_m}}=K'\frac{C_D+C_{gs}}{\sqrt{C_{gs}}}$; $\frac{d\,ENC}{dC_{gs}}=0\Rightarrow C_{gs}=C_D$.
    2. Constant drain current (monolithic), strong inversion: $g_m=\sqrt{2\mu I_DC_{gs}/L^2}$; $ENC=K(C_{gs}+C_D)/g_m=K'(C_DC_{gs}^{-1/4}+C_{gs}^{3/4})$ (the middle expression is printed with $g_m$; the right-hand form corresponds to $1/\sqrt{g_m}$) $\Rightarrow C_{gs}=C_D/3$. Weak inversion: $g_m=I_D/(nU_T)$, independent of $C_{gs}$; $ENC=K(C_D+C_{gs})$, so $C_{gs}\to0$, which drives the device back into strong inversion; optimum at the strong/weak-inversion border, $C_{gs}=\frac{2I_DL^2C_{ox}}{K'(3U_T)^2}$.
  - Slide 4: minimum current for a strong-inversion match versus $C_D$ (0.5 µm NMOS, 1.2 µm PMOS). Example, 0.5 µm NMOS, $C_D=10$ pF, $I_D=0.2$ mA: the conventional $C_D/3$ match gives $W=1543$ µm, $g_m=5$ mS, $C_{gs}+C_D=13.3$ pF; sizing to the weak/strong border gives $W=281$ µm with the same $g_m=5$ mS and $C_{gs}+C_D=10.6$ pF. The $C/3$ rule therefore overestimates the optimum size when it would put the device in weak inversion.

### T7. BNL note "Capacitive matching for MOSFET charge-sensitive preamplifiers with constant current"

- **Citation:** [author not stated in the document], "Capacitive matching for MOSFET Charge-Sensitive Preamplifiers with Constant Current" (title of the first of 7 slides), file `ICFA95.fm.pdf` on the BNL Instrumentation Division microelectronics pages (PDF metadata: created 21 Feb 1997). Original URL http://www.inst.bnl.gov/programs/microelec/PDF/ICFA95.fm.pdf, retrieved from the UNT "End of Term 2008" web-archive capture. The year in the file name ("95") was not verified.
- **File:** `BNL_ICFA95_Capacitive_Matching_MOSFET_Constant_Current.pdf`
- **Access:** slides 1 and 3 read as rendered images; slide 2 by text extraction.
- **Contributions:**
  - Slide 1: Eq. (1) $ENC^2=\tfrac12e_n^2C_{in}^2\Im_1$ with $C_{in}=C_{det}+C_{ox}WL$, $e_n^2=4kTa_n/g_m$, "$a_n\approx2/3$ for FET", $g_m=\sqrt{2\mu C_{ox}(W/L)I_d}$ (strong inversion), $g_m=qI_d/nkT$ (weak inversion), $\Im_1=\int[h'(t)]^2dt$. With $I_d$, $L$, $h(t)$ fixed, Eq. (2) $d(ENC^2)/dW=0$ gives $C_{det}+C_{ox}WL=4C_{ox}WL$, i.e. Eq. (3) $C_{ox}WL=\tfrac13C_{det}$, $W_{opt}=C_{det}/(3C_{ox}L)$. Including weak inversion: $W_{opt}=\min\!\left(\frac{C_{det}}{3C_{ox}L},W_{wi}\right)$, $W_{wi}=\frac{2LI_d}{(3kT/q)^2\mu C_{ox}}$.
  - Slide 2 (text): $n$ (weak-inversion slope factor) is the ratio of bottom (JFET-like) to top (MOS) gate control, typically 1.2–1.5.
  - Slide 3 ("Noise"): drain thermal noise $i_n^2=8nkTg_m/3$; flicker $v_n^2=4kT\rho/(WLf)$; $4kTR_n=v_n^2+i_n^2/g_m^2$; $R_n=\rho/(WLf)+2/(3g_m)$ (the factor $n$ is dropped in this last line as printed). Sketch: at constant $I_D$, larger $WL$ lowers the 1/f part, larger $W/L$ lowers the white part.

### T8. Leach (1994), Proc. IEEE tutorial

- **Citation:** W. M. Leach, Jr., "Fundamentals of low-noise analog circuit design," *Proc. IEEE* 82(10), 1515–1538 (Oct. 1994). DOI: 10.1109/5.326411. Copy of the published version hosted on the author's Georgia Tech legacy website: https://leachlegacy.ece.gatech.edu/papers/AnalogNoise.pdf
- **File:** `Leach_1994_Fundamentals_Low_Noise_Analog_Circuit_Design.pdf`
- **Access:** pp. 1515, 1521, 1522, 1530, 1531 and 1532 read as rendered images; p. 1534 by text extraction.
- **Contributions:**
  - p. 1521, Sect. XI, Eq. (22): $NF=10\log\left[1+\frac{V_n^2+2\rho V_nI_nR_S+I_n^2R_S^2}{4kTR_S\Delta f}\right]$ ($\rho$ = correlation coefficient of $v_n$ and $i_n$); optimum source resistance $R_{S0}=V_n/I_n$. Adding series or shunt resistance to reduce NF always lowers SNR ("noise figure fallacy"); design should minimize the equivalent noise input voltage referred to the source.
  - p. 1521, Sect. XII, Fig. 6, Eqs. (23)–(24), $N$ identical input devices in parallel: $V_{ni}=\sqrt{4kTR_S\Delta f+\frac1NV_n^2+2\rho V_nI_nR_S+NI_n^2R_S^2}$; for $R_S=0$, $V_{ni}=V_n/\sqrt N$.
  - p. 1522, Eq. (25): optimum number of parallel devices $N=\frac{V_n}{I_nR_S}$; "the noise cannot be reduced by paralleling input devices if the source resistance is sufficiently large."
  - p. 1522, Sect. XIII, Eqs. (26)–(29): input transformer 1:n with winding resistances; for $R_S\gg R_1+R_2/n^2$, $V_{nis}\simeq\sqrt{4kTR_S\Delta f+\frac{1}{n^2}V_n^2+2\rho V_nI_nR_S+I_n^2n^2R_S^2}$ (28), minimized at $n=\sqrt{V_n/(I_nR_S)}$ (29), i.e. $n^2R_S=V_n/I_n$; winding resistance can cancel the benefit.
  - p. 1530, Sect. XXI: the JFET needs gate-current shot noise in addition to channel thermal and flicker noise; MOSFET flicker noise is usually larger (surface device, oxide traps), so the JFET is usually preferred at low frequencies; JFET and MOSFET noise models are otherwise the same. $i_D=K(1+\lambda v_{DS})(v_{GS}-V_{TO})^2$ with $K=I_{DSS}/V_{TO}^2$ (JFET) or $K=\mu_oC_{ox}W/2L$ (MOSFET); $g_m=2[K(1+\lambda V_{DS})I_D]^{1/2}\simeq2(KI_D)^{1/2}$; gate shot noise $I_{shg}=(2qI_G\Delta f)^{1/2}$.
  - p. 1531: channel thermal noise $I_{td}=[4kT(2g_m/3)\Delta f]^{1/2}$ (same as a resistor $3/(2g_m)$); flicker $I_{fd}=(K_fI_D\Delta f/fL^2C_{ox})^{1/2}$ for the MOSFET (typical $K_f=10^{-28}$ F·A) and $I_{fd}=(K_fI_D\Delta f/f)^{1/2}$ for the JFET. Eq. (64):
    $$V_{ni}=\left[4kT(R_1+R_2)\Delta f+2qI_G(R_1+R_2)^2\Delta f+\frac{4kT}{3\sqrt{KI_D}}\Delta f+\frac{K_f}{4KfL^2C_{ox}}\Delta f\right]^{1/2}$$
    ($I_G=0$ for the MOSFET; $L^2$ and $C_{ox}$ omitted for the JFET). Minimum noise needs low series resistance in the gate and source circuits, large $K$ and small $K_f$; the thermal part scales as $I_D^{-1/4}$ (1.5 dB lower per doubling of $I_D$). Gate current rises sharply above a device-dependent drain–gate voltage (the "$I_G$ breakpoint"), "typically in the range of 8 to 40 V". Examples: CD860 dual n-JFET, $I_{DSS}=100$ mA, $V_{TO}=-1.5$ V, $K=4.4\times10^{-2}$ A/V²; 2N5457, $I_{DSS}=3$ mA, $V_{TO}=-3$ V, $K=3.3\times10^{-4}$ A/V².
  - p. 1532, Eqs. (65)–(68): $V_n=\sqrt{\frac{4kT}{3\sqrt{KI_D}}\Delta f+\frac{K_f}{4KfL^2C_{ox}}\Delta f}$ (65), $I_n=\sqrt{2qI_G\Delta f}$ (66); flicker corner $f_f$ (where $V_n$ is up 3 dB) gives $K_f=\frac{16}{3}kTf_fL^2C_{ox}\sqrt{K/I_D}$ (67; $L^2C_{ox}$ omitted for the JFET); differential pair, Eq. (68): $V_{ni}=\sqrt2\left[4kT\left(\frac{R_{11}+R_{12}}{2}+R_2\right)\Delta f+2qI_G\Delta f\left(\frac{R_{11}+R_{12}}{2}+R_2\right)^2+\frac{4kT\Delta f}{3\sqrt{KI_D}}+\frac{K_f\Delta f}{4KfL^2C_{ox}}\right]^{1/2}$, i.e. 3 dB above a single device for equal source resistances.
  - p. 1534 (text): BJT versus FET at 1 mA; FET with $K=5\times10^{-4}$ A/V², $V_{TO}=-2$ V ($I_{DSS}=2$ mA): $V_{ni}=1.29\times10^{-10}\sqrt{R_E+471}$ V/√Hz (Eq. 75); BJT lower for small source resistance, similar for large source resistance if the BJT runs at its optimum current.

### T9. Perrott and Lee (2005), MIT OpenCourseWare lecture slides

- **Citation:** M. H. Perrott, "Lecture 10: Noise Modeling in Amplifiers," MIT 6.776 *High Speed Communication Circuits*, 8 Mar 2005 (slide footers "H.-S. Lee & M.H. Perrott, MIT OCW"), 44 slides. URL: https://ocw.mit.edu/courses/6-776-high-speed-communication-circuits-spring-2005/f84805c3059b889d31b7c8c2fff86030_lec10.pdf
- **File:** `Perrott_2005_MIT6776_Lecture10_Noise_Modeling.pdf`
- **Access:** slides 8 and 10 read as rendered images; slides 11–13 by text extraction.
- **Contributions (MOSFET-oriented; the functional forms are the classical long-channel FET results):**
  - Slide 8: $\overline{i_{nd}^2}|_{th}=4kT\gamma g_{do}\Delta f$; $\gamma$ "excess noise factor" = 2/3 in long channel, 2 to 3 (or higher) in short-channel NMOS, less in PMOS; $g_{do}=g_m/\alpha$.
  - Slide 10: induced gate noise $\overline{i_{ng}^2}=4kT\delta g_{do}\left(\frac{2\pi f}{\sqrt5/\alpha\,(g_m/C_{gs})}\right)^2\Delta f$, rising 20 dB/decade and crossing $4kT\delta g_{do}$ at $f=\sqrt5f_t/\alpha$; $\delta$ (gate noise coefficient) "typically assumed to be $2\gamma$"; correlated with the drain noise. **[derived]** Equivalent form: $\overline{i_{ng}^2}=4kT\delta\,\omega^2C_{gs}^2\Delta f/(5g_{do})$.
  - Slide 11: references for further reading (Wang et al., JSSC 1994; Goo, PhD thesis 2001 and IEDM 2000; Sepke, MS thesis 2002); not accessed.

### T10. Gotti (PhD thesis, arXiv 2018)

- **Citation:** C. Gotti, "Low Noise Readout Circuits for Particle and Radiation Sensors," PhD thesis, Università degli Studi di Firenze (international doctorate in RF, microwaves and electromagnetism, cycle XXV, 2010–2012; tutor G. Manes, co-tutor G. Pessina), arXiv:1807.02296 [physics.ins-det], posted 6 Jul 2018, 155 pp.
- **File:** `Gotti_2018_Low_Noise_Readout_Circuits_Thesis.pdf`
- **Access:** pp. 20–23 read as rendered images; pp. 98–105 by text extraction only; rest not read.
- **Contributions:**
  - pp. 20–21: 1/f noise mostly from carrier traps (impurities in bulk, oxide traps in MOS), individual traps giving generation–recombination Lorentzians; Fig. 1.8 (taken from the thesis's Ref. [10]) shows noise spectra of two high-quality JFETs (2SK146, SNJ3600) versus temperature with single-trap features; impurity-related 1/f level is technology- and even wafer-dependent; MOS has intrinsic oxide-trap 1/f.
  - p. 22, Eq. (1.18): $v_{FET}=\sqrt{A_f/f+8k_BT/(3g_m)}$; $A_f$ is usually much higher for MOS than for JFETs and, within a technology, inversely proportional to transistor area; the channel term "behaves as if due to a resistance of value $0.7\,g_m^{-1}$"; JFET/MOS gate current noise usually negligible. Eq. (1.17), BJT: $v_{BJT}=\sqrt{A_f/f+2k_BT/g_m+4k_BTR_{BB'}}$; Fig. 1.9 summarizes the device noise models.
  - pp. 98–99 (text): for cryogenic germanium-detector readout, JFETs at a few mA showed $g_m/C\approx2$ mA/(V·pF) at low temperature; BF862 quoted with 10 pF total gate capacitance and $g_m\approx20$ mA/V at a few mA (cryogenic context; thesis values).

### T11–T16. Items read at abstract or citation level only (no open full text found)

- **T11.** A. van der Ziel, "Thermal Noise in Field-Effect Transistors," *Proc. IRE* 50(8), 1808–1812 (1962). DOI: 10.1109/JRPROC.1962.288221. **Access: abstract only** (index record at manuscript.isc.ac). Channel thermal noise is the limiting mechanism; at zero drain voltage it equals the thermal noise of the drain conductance; because of modulation effects it is somewhat larger than the thermal noise of the dc drain conductance except at zero drain bias and beyond saturation; the noise resistance is "approximately equal to gmax/g,m2" as rendered in the index, most plausibly $g_{max}/g_m^2$ ($g_{max}$ = maximum transconductance); prefactors could not be checked.
- **T12.** A. van der Ziel, "Gate noise in field effect transistors at moderately high frequencies," *Proc. IEEE* 51(3), 461–467 (1963). DOI: 10.1109/PROC.1963.1849. **Access: abstract only** (index record). High-frequency gate noise is channel thermal noise coupled capacitively to the gate; gate and drain noise generators are correlated with an imaginary correlation coefficient of about 0.40j in saturation; $\overline{i_g^2}$ can be expressed through $R_n$ and $C_{gs}$; the correlation affects the noise figure only slightly, and $(F_{min}-1)$ varies as $\omega C_{gs}R_n$ over a wide frequency range.
- **T13.** W. C. Bruncke and A. van der Ziel, "Thermal noise in junction-gate field-effect transistors," *IEEE Trans. Electron Devices* ED-13(3), 323–329 (1966). DOI: 10.1109/T-ED.1966.15688. **Access: abstract only** (index record; volume from Crossref). Measured JFET parameters: high-frequency $g_{11}$ and $g_{12}$ vary as $f^2$ and show practically full thermal noise; a small gate–drain noise correlation exists and agrees with theory; an approximate noise-figure expression holds reasonably well up to the cutoff frequency. No numerical $\gamma$ in the abstract.
- **T14.** G. Bertuccio and A. Pullia, "A method for the determination of the noise parameters in preamplifying systems for semiconductor radiation detectors," *Rev. Sci. Instrum.* 64(11), 3294–3298 (1993). DOI: 10.1063/1.1144293. **Access: abstract only** (University of Milan record; full text not openly available to this search). Separates series white, parallel white, series 1/f and parallel "f" noise by a multiparameter least-squares fit of ENC versus shaping time measured with a charge amplifier.
- **T15.** G. Bertuccio, A. Pullia and G. De Geronimo, "Criteria of choice of the front-end transistor for low-noise preamplification of detector signals at sub-microsecond shaping times for X- and γ-ray spectroscopy," *Nucl. Instrum. Methods A* 380(1–2), 301–307 (1996). DOI: 10.1016/S0168-9002(96)00474-3. **Access: abstract only** (University of Milan record). Identifies the front-end transistor figures of merit for best resolution; shows that the correlation between gate and drain current noise in FETs plays a significant role in the ENC of a charge preamplifier; compares JFET, MOSFET, MESFET and HFET devices.
- **T16.** K. Kandiah and F. B. Whiting, "Low frequency noise in junction field effect transistors," *Solid-State Electronics* 21(8), 1079–1088 (1978). DOI: 10.1016/0038-1101(78)90188-0. **Access: citation only** (Crossref metadata; abstract not retrieved). Cited for completeness on JFET low-frequency noise physics; nothing about its content is claimed here.

Not obtained: ADI tutorials MT-047/MT-052 (analog.com did not respond to automated download within 60 s; not used). TI SLVA043B was checked and contains no noise-figure or optimum-source-resistance derivation, so it was discarded.



### Part B summary: key formulas with sources

1. **FET channel white noise and $\gamma$.** $e_n^2=4kT\gamma/g_m$ (equivalently $i_{nd}^2=4kT\gamma g_m$).
   - $\gamma=2/3$ for a long-channel device in saturation: T3 p. 3 ("usually given as 2/3"), T7 slide 1 ($a_n\approx2/3$ for FET), T8 p. 1531 ($I_{td}^2=4kT(2g_m/3)\Delta f$), T9 slide 8, T10 Eq. (1.18) ($8kT/3g_m$).
   - Typical/measured: "0.5 to 1" (T3 p. 3); "0.5 to 1.0" (T1 p. 461); "behaves as $0.7/g_m$" (T10 p. 22); measured MOSFET values 0.50–2.00 depending on $I_d/W$ and $L$ (T3 p. 8); short-channel NMOS 2–3 (T9 slide 8). No open source with measured $\gamma$ for discrete JFETs was found; van der Ziel's JFET results (T11, T13) were seen at abstract level only.
2. **Gate leakage noise.** $i_n^2=2qI_G$ (T3 p. 2; T8 Eq. (66), p. 1532). Gate current rises steeply above the "$I_G$ breakpoint", typically $V_{DG}$ = 8–40 V (T8 p. 1531).
3. **Gate and source resistance noise.** $v_{ni}^2=4k_BT(\gamma_n/g_m+R_G+R_S)$ (T3 p. 5); normalized form with the term $(1/\gamma)R_gg_m$ in Eq. (10.28) (T1 p. 462); external gate- and source-circuit resistances add $4kT(R_1+R_2)$ (T8 Eq. (64), p. 1531). Since $R_G,R_S\propto1/W$, their relative weight is unchanged when width is scaled at constant current density (T3 p. 5).
4. **Induced gate noise.** Term $\frac{\delta}{5\gamma}(C_{gs}/C_{in})^2$ in $R_{eq}/(\gamma/g_m)$ with $\delta/5\gamma\approx1/3$ (T1 Eq. (10.28), pp. 461–462); $\overline{i_{ng}^2}=4kT\delta g_{do}\left(\frac{2\pi f}{\sqrt5/\alpha\,(g_m/C_{gs})}\right)^2\Delta f$, $\delta\approx2\gamma$, correlated with drain noise (T9 slide 10); correlation about 0.40j in saturation and $(F_{min}-1)\propto\omega C_{gs}R_n$ (T12, abstract).
5. **1/f noise scaling.**
   - JFET model: drain flicker $I_{fd}^2=K_fI_D\Delta f/f$, input-referred $e_{nf}^2=K_f/(4Kf)$, independent of $I_D$ and inversely proportional to $K=I_{DSS}/V_{TO}^2$ (T8 Eqs. (64)–(65), pp. 1531–1532); $K_f=\frac{16}{3}kTf_f\sqrt{K/I_D}$ from the measured corner (T8 Eq. (67)).
   - Area scaling: $A_f=K_f/(WLC_g^2)$, $K_f\approx10^{-33}$ C²/cm² for JFETs versus $10^{-32}$ (p-MOS) and $4\times10^{-31}$ (n-MOS) (T3 p. 9); $K_f=A_fC_{gs}\approx10^{-27}$ J for JFETs versus $\sim10^{-25}$ J (p-MOS) and $\sim10^{-24}$ J (n-MOS) (T1 pp. 459–460); $A_f\propto1/\text{area}$ within a technology (T10 p. 22); $v_n^2=4kT\rho/(WLf)$ (T7 slide 3).
   - In charge measurement $ENC_f^2=\pi C_{in}^2A_fA_2$, independent of shaping time (T1 Eqs. (10.4), (10.15)).
   - **[derived]** For $N$ identical JFETs in parallel, each at the same drain current: $K\to NK$ and $C_{gs}\to NC_{gs}$, so both the white term ($\propto1/g_m$) and the 1/f term ($\propto1/K$ or $1/C_{gs}$) of $e_n^2$ fall as $1/N$, while $C_{iss}$ and the gate shot noise $2qI_G$ grow as $N$.
   - JFET 1/f noise physics (generation–recombination at traps, temperature signatures): T10 pp. 20–21; T16 (citation only). Measured dependence of JFET 1/f noise on drain current was not found in the open theory sources.
6. **Optimum source resistance and noise figure (resistive source).** $R_{opt}=e_n/i_n$; $F=1+\frac{e_n^2}{4kTR_S}+\frac{i_n^2R_S}{4kT}$; $F_{opt}=1+\frac{e_ni_n}{2kT}$; $T_{N,min}=\frac{e_ni_n}{2k}$ (T4 pp. 23–26). With correlation: T8 Eq. (22), $R_{S0}=V_n/I_n$ (p. 1521). **[derived]** From T8 Eq. (22), the minimum at $R_{S0}$ is $F_{min}=1+(1+\rho)\frac{e_ni_n}{2kT}$ per unit bandwidth; the location $R_{S0}$ does not depend on $\rho$. Caveat: the minimum input noise voltage is at $R_S=0$; never add resistance to "match" (T4 p. 24; T8 p. 1521). Transformer: $N^2R_S=e_n/i_n$ (T4 p. 25; T8 Eq. (29), p. 1522).
7. **Paralleling input devices with a resistive source.** $V_{ni}^2/\Delta f=4kTR_S+V_n^2/N+2\rho V_nI_nR_S+NI_n^2R_S^2$ (T8 Eq. (24), p. 1521); optimum $N=V_n/(I_nR_S)$ (T8 Eq. (25), p. 1522). **[derived]** This is the $N$ at which the array's own $R_{opt}=(V_n/\sqrt N)/(I_n\sqrt N)$ equals $R_S$.
8. **Capacitive matching.**
   - Constant current density (width scaled, or identical devices paralleled at the same per-device current): optimum when FET input capacitance equals the source capacitance, $C_i=C_{det}$ (T3 pp. 4 and 6; T6 slide 2; T1 p. 463). Array form: maximum S/N at $nC_i'=C_{det}$ (T3 p. 21).
   - Constant total drain current, strong inversion ($g_m\propto\sqrt{I_DC_{gs}}$): $C_{gs}=C_{det}/3$ (T6 slide 2; T7 Eq. (3)).
   - **[derived]** The JFET square law $g_m\simeq2\sqrt{KI_D}$ with $K\propto W$ (T8 p. 1530) has the same $\sqrt{I_DC_{gs}}$ scaling, so the $C/3$ result is expected to carry over to a JFET array at fixed total current; none of the sources states this for JFETs explicitly.
   - Weak inversion or any case where $g_m$ does not grow with device size: matching is harmful; optimum at the weak/strong-inversion border (T6 slides 2 and 4; T7 slide 1, $W_{wi}$; T3 p. 22). Not applicable to BJTs (T3 p. 17).
   - Conditions: device noise must fall as its capacitance grows, and the capacitance is scaled with the source; current noise alone gives no optimum (T3 pp. 20–22). The derivations assume a charge (capacitive) signal source; for a source whose signal is not attenuated by the added input capacitance the premise does not hold.
   - Limits: $Q_{n,min}=\sqrt{\frac{16k_BT_0}{\kappa_n}\frac{F_v}{T_S}(C_d+C_s)}$, $\kappa_n=g_m/(\gamma_nC_i)$ (T3 p. 6); $ENC_{s\,opt}\cong2\sqrt2\sqrt{kTC_{gs}}\sqrt{\tau_e/t_m}$ with $\gamma\sim1$ (T1 Eq. (10.29), p. 463). Device figure of merit $g_m/C_{gs}=\omega_T=2\pi f_T$ (T6 slide 2; T1 Eq. (10.27)).
9. **ENC relations.** $ENC^2=\tfrac12e_n^2C_{in}^2I_1+\pi C_{in}^2A_fI_2+\tfrac12i_n^2I_3$ (T1 Eq. (10.5)); $ENC_s=e_nC_{in}/\sqrt{t_m}$ (10.12); slope $e_n/\sqrt{t_m}$ per pF (10.13); $\tau_{opt}=(R_sR_p)^{1/2}C_{in}(A_1/A_3)^{1/2}$ (10.9); $Q_n^2=i_n^2F_iT_S+v_n^2C_i^2F_v/T_S$ (T3 p. 3).
10. **Differential pair.** Input noise of a JFET differential pair is $\sqrt2$ times that of one device for equal source resistances (T8 Eq. (68), p. 1532).
11. **Dielectric (insulator) noise at the input.** $i_n^2=4kTD\omega C_{diel}$; FR-4-class board $D\approx2\times10^{-2}$ versus $\approx5\times10^{-5}$ for Teflon, polystyrene, quartz (T1 Eqs. (10.24)–(10.26), p. 460).

### Part B gaps

- Radeka (1988) was not accessible; T1 is used in its place.
- No open document with measured channel-noise factor $\gamma$ for discrete low-noise JFETs (e.g. LSK170, IF3601, BF862) was found. A practical substitute is $\gamma_{eff}=e_n^2g_m/(4kT)$ computed from datasheet $e_n$ and $g_{fs}$ at the same bias; that calculation was not done here.
- JFET-specific induced-gate-noise coefficients (van der Ziel 1963) and Bertuccio et al. (1993, 1996) were seen at abstract level only.
- Measured drain-current dependence of JFET 1/f noise is not covered by the open theory sources above; device datasheets and the measurement papers handled under the other topics are the place to look.

---

## Part C. Published low-noise JFET preamplifier designs and measurement methods

### C1. Scandurra, Cannatà and Ciofi (2011), differential ultra-low-noise amplifier, AIP Advances

- **Citation:** G. Scandurra, G. Cannatà, C. Ciofi, "Differential ultra low noise amplifier for low frequency noise measurements," *AIP Advances* 1, 022144 (2011). DOI: 10.1063/1.3605716. Open access ("Free" on the publisher page).
- **Access:** full text read from the publisher's HTML article page (text and equations); the figure images themselves were not inspected. The PDF was not saved because the publisher site answered automated downloads with a JavaScript challenge.
- **Topology (Sect. II, Fig. 2, Table I):** two cascaded stages. First stage fully differential: an InterFET IF3602 dual JFET (JL, JR), each half common-source with drain load $R_{Dx}=2$ kΩ (five 10 kΩ in parallel), source resistor $R_{1x}=10$ Ω (wirewound, 0.1 %) to a common node fed by a 2N1711 current source ($R_{SS}=1.5$ kΩ), and feedback resistors $R_{2x}=1$ kΩ from the outputs of two INA131 instrumentation amplifiers (IA1, IA2, gain 100 each) back to the JFET sources. Second stage: AC-coupled INA131 (gain 100). Overall differential gain 80 dB. Supplies: 12 V lead-acid batteries.
- **Bias and loop (Eqs. (1), (2), (8)–(11)):** $I_{Dx}=I_C/2-V_{GSx}/R_{2x}$ with $I_C=(V_{SS}-V_{BE})/R_{SS}$ gives about 4.5 mA per JFET at $V_{DS}\approx2$ V; $g_m\approx70$ mA/V at 4–5 mA. Differential loop gain $T_D=-2g_mR_DG/(1+R_2/R_1+g_mR_2)$, $|T_{D0}|\approx165$ (Eq. (8)); pole–zero compensation $R_CC_C$ puts the loop pole at about 1.2 kHz. First-stage differential gain $\approx R_2/R_1=100$ (Eqs. (10)–(11)). JFET offset up to 100 mV is absorbed by the DC feedback to the sources.
- **Noise budget:** both JFETs add, $S^{J}_{in}=2S_{enJ}$ (Eq. (12)); drain resistors negligible, about 50 pV/√Hz (Eq. (15)); source/feedback resistors $S^{R12}_{in}\approx8kTR_1\approx0.33\times10^{-18}$ V²/Hz, i.e. about 0.6 nV/√Hz (Eq. (16)); instrumentation-amplifier noise suppressed by about $7\times10^{-5}$ below the loop pole (Eq. (20)) but rising as $f^2$ above it (about $0.8\times10^{-18}$ V²/Hz at 10 kHz).
- **Measured (Sect. III, Figs. 5, 6, 9):** equivalent input voltage noise 14 nV/√Hz (0.1 Hz), 2 nV/√Hz (1 Hz), 1.2 nV/√Hz (10 Hz), about 1 nV/√Hz from 100 Hz to about 2 kHz, below 3 nV/√Hz up to 40 kHz. Bandwidth above 30 kHz with a 10 kΩ source; about 20 kHz with a 100 kΩ differential source, from which a differential input capacitance of about **80 pF** is inferred. CMRR "in excess of 40 dB" in the flat band (100 kΩ common-mode test). Input current noise equal to the thermal noise of the 6.6 MΩ bias resistors (about 50 fA/√Hz) up to a few kHz, rising as $f^2$ above 10 kHz (attributed to gate-referred current noise of the large JFETs). Input AC-coupled at 2.2 mHz. Noise figure versus $R_S$ and $f$: Eq. (24), Fig. 10.
- **Relevance:** quantifies the 3 dB penalty of a feedback differential pair ($S_{in}=2S_{enJ}$), the $8kTR_1$ penalty of source degeneration, the $f^2$ rise of the second-stage noise beyond the loop pole, and the large input capacitance that comes with IF3602-class devices.

### C2. Cannatà, Scandurra and Ciofi (2009), ultralow-noise preamplifier, Rev. Sci. Instrum.

- **Citation:** G. Cannatà, G. Scandurra, C. Ciofi, "An ultralow noise preamplifier for low frequency noise measurements," *Rev. Sci. Instrum.* 80, 114702 (2009). DOI: 10.1063/1.3258197.
- **Access:** abstract only (publisher page; article is paywalled).
- **Contribution (abstract):** 80 dB gain, passband from a few tens of mHz to a few kHz; equivalent input voltage noise 14 nV/√Hz (100 mHz), 1.4 nV/√Hz (1 Hz), 1.0 nV/√Hz (10 Hz), 0.8 nV/√Hz (1 kHz), with standard components and no trimming; JFET input stage with equivalent input current noise below 4 fA/√Hz over the band. C3 (Table 2, p. 12) describes this design as using an IF3602 in a feedback configuration for the differential input stage at 4 mA, with 6, 1.4, 1, 0.9, 0.8 and 1.1 nV/√Hz at 0.2, 1, 10, 100, 1000 and 10 000 Hz.

### C3. Scandurra, Giusi and Ciofi (2019), single-JFET front end with cross-correlation gain calibration, Electronics

- **Citation:** G. Scandurra, G. Giusi, C. Ciofi, "Single JFET Front-End Amplifier for Low Frequency Noise Measurements with Cross Correlation-Based Gain Calibration," *Electronics* 8(10), 1197 (2019). DOI: 10.3390/electronics8101197 (open access).
- **File:** `Scandurra_2019_Single_JFET_FrontEnd_CrossCorrelation_Gain_Calibration_Electronics.pdf`
- **Access:** p. 12 (Fig. 9, Table 2) read as an image; pp. 1–11 by text extraction.
- **Contribution:** open-loop common-source stage with a single InterFET IF3601 (large-area JFET, $g_m$ of a few tens of mA/V at a few mA), source bypassed by a supercapacitor so that the low-frequency corner can be far below 1 Hz; bias $I_D=(-V_{GS}+V_{SS})/R_S$ (Eq. (1)). Gain spread of the open-loop stage is removed by cross-correlating its output with two auxiliary op-amp amplifiers (TLC070, gains 11 and 101, about 100 kHz bandwidth) connected to the same input. Measured EIVN (Table 2, p. 12): **6, 1.7, 0.7, 0.6, 0.5, 0.5 nV/√Hz at 0.2, 1, 10, 100, 1000, 10 000 Hz with one IF3601 at 2.5 mA**; "less than 1 nV/√Hz above 2 Hz" (p. 12). Input capacitance: IF3601 typical $C_{gs}\approx300$ pF and $C_{gd}\approx200$ pF (p. 7); the effective input capacitance of about **500 pF** produces a 6.4 kHz pole with a 50 kΩ source (p. 10). The paper's Table 2 also lists Levinzon (C6; single JFET, 5 mA, offline calibration needed: 4, 1.4, 0.6, 0.6, 0.5, 0.5 nV/√Hz) and Cannatà et al. (C2).
- **Relevance:** best published single-device JFET floor (0.5 nV/√Hz) and a clear illustration of the $e_n$–$C_{in}$ trade-off: sub-nV/√Hz with a single large JFET costs hundreds of pF.

### C4. Scandurra, Giusi and Ciofi (2019), ICNF conference paper

- **Citation:** G. Scandurra, G. Giusi, C. Ciofi, "Ultra-low noise, single JFET voltage pre-amplifier for low frequency noise measurements," ICNF 2019 full paper no. 69 (file hosted in EPFL Infoscience record 269259; conference proceedings details not checked).
- **File:** `Scandurra_2019_Single_JFET_Preamplifier_ICNF.pdf`
- **Access:** pp. 1–4 by text extraction.
- **Contribution:** conference version of C3. A single-transistor input stage avoids the doubling of input noise power inherent in a differential pair (p. 1). Auxiliary amplifiers: 61 dB gain, 16 mHz–100 kHz, about 10 nV/√Hz at 1 kHz (p. 3); cross-spectra between 100 Hz and 1 kHz gave $g_mR=2160$, i.e. $g_m=43$ mA/V (p. 4); response falls above about 2 kHz because of the large gate capacitance (p. 3).

### C5. Levinzon (2008), ultra-low-noise high-input-impedance amplifier, IEEE TCAS-I

- **Citation:** F. A. Levinzon, "Ultra-Low-Noise High-Input Impedance Amplifier for Low-Frequency Measurement Applications," *IEEE Trans. Circuits Syst. I* 55(7), 1815–1822 (Aug. 2008). DOI: 10.1109/TCSI.2008.918213 (bibliographic data confirmed in Crossref).
- **Access:** abstract only (index record; paywalled).
- **Contribution (abstract):** −3 dB range about 0.07 Hz to 110 kHz, gain about 83 dB; equivalent input noise about 5.6, 1.4, 0.6 and 0.5 nV/√Hz at 0.1, 1, 10 and 1000 Hz; noise analysis for active, capacitive and low-impedance sources, with the breakdown of amplifier and JFET noise contributions. C3 (Table 2) characterizes it as a single-JFET stage at 5 mA that needs offline gain calibration. The JFET type was not visible in the material read (a forum post names the IF9030; not verified).

### C6. Levinzon (2000), noise of the JFET amplifier, IEEE TCAS-I

- **Citation:** F. A. Levinzon, "Noise of the JFET amplifier," *IEEE Trans. Circuits Syst. I* 47(7), 981–985 (July 2000). DOI: 10.1109/81.855453.
- **Access:** abstract only.
- **Contribution (abstract):** engineering formulae for the input-referred noise of silicon JFET amplifiers for resistive and capacitive sources, predicted 0.5 Hz–50 kHz and compared with measurement; in modern low-noise JFETs 1/f noise exceeds channel thermal noise up to about 100 Hz; with a high-capacitance source the bias-resistor thermal noise dominates at low frequency; at and above 1 kHz the JFET channel thermal noise dominates.

### C7. Levinzon (2005), low-frequency noise of modern low-noise JFETs, IEEE TIM

- **Citation:** F. A. Levinzon, "Measurement of low-frequency noise of modern low-noise junction field effect transistors," *IEEE Trans. Instrum. Meas.* 54(6), 2427–2432 (Dec. 2005). DOI: 10.1109/TIM.2005.858534.
- **Access:** abstract only.
- **Contribution (abstract):** measurement system for 0.5 Hz–50 kHz with its own floor quoted as about 1.3, 0.6, 0.08 nV/√Hz at 0.5, 1, 10 Hz and ≤0.04 nV/√Hz from 100 Hz to 50 kHz. Best-sample JFET $e_n$: **IF9030 2.7 / 1.5 / 0.5, IF1801 3.2 / 2.1 / 0.4, IF3601 3.4 / 1.8 / 0.6, 2N4338 22 / 14 / 3.2 nV/√Hz at 0.5 Hz / 1 Hz / above 1 kHz**; 1/f below 10 Hz, channel thermal noise at and above 10 Hz. Drain currents and capacitances are not in the abstract.

### C8. Levinzon, piezoelectric-accelerometer noise (2004 paper; 2015 book)

- **Citations (verified in Crossref only):** F. A. Levinzon, "Fundamental noise limit of piezoelectric accelerometer," *IEEE Sensors J.* 4(1), 108–111 (2004), DOI 10.1109/JSEN.2003.820366; F. Levinzon, *Piezoelectric Accelerometers with Integral Electronics*, Springer, Cham, 2015, chapters "Fundamental Noise Limit of an IEPE Accelerometer" (pp. 107–116, DOI 10.1007/978-3-319-08078-9_6) and "Noise of an IEPE Accelerometer" (pp. 117–133, DOI 10.1007/978-3-319-08078-9_7).
- **Access:** citation only; content not read.

### C9. Callegaro, Pisani and Pollarolo (2008), very simple FET amplifier below 1 nV/√Hz, arXiv

- **Citation:** L. Callegaro, M. Pisani, A. Pollarolo, "Very simple FET amplifier with a voltage noise floor less than 1 nV/√Hz," arXiv:0811.2866v1 [physics.ins-det] (18 Nov 2008). Journal publication not checked.
- **File:** `Callegaro_2008_Simple_FET_Amplifier_Below_1nV_arXiv0811.2866.pdf`
- **Access:** pp. 2, 3, 5, 6 read as images (full text is 3 pp. plus references, table and figures).
- **Contribution:** a single JFET (prototype: 2SK170) in common source at $V_{GS}\approx0$, with an op-amp (OP27) acting as a transresistance stage ($R=1$ kΩ) that holds the drain at a battery-set voltage, i.e. a cascode without a Miller effect (p. 2, Fig. 1). Gain $G=+g_mR$ (sample-dependent; calibration may be needed). Measured: **3 dB bandwidth about 4 MHz, gain flat within 1 dB to 1 MHz** (Fig. 2 shows about 30 dB gain with a small peak near 2–3 MHz); **noise floor about 0.8 nV/√Hz** (Johnson noise of about 38 Ω), measured by two-channel cross-correlation; gate bias current 2–3 pA, i.e. shot noise below 1 fA/√Hz (p. 3). Single +24 V battery, about 15 mA. Input dynamic range only a few tens of mV before distortion (footnote, p. 2). Pseudo-differential wiring permits four-terminal DUT connection. Table 1 (p. 5, datasheet values): 2SK170BL / LSK170B / LSK389B $g_m$ 22 / 22 / 20 mS, $e_n$(1 kHz) 0.95 / 0.9 / 0.9 nV/√Hz, $C_{in}$ 30 / 20 / 25 pF, $I_{DSS}$ 6–12 mA.
- **Relevance:** demonstrates that a single low-capacitance JFET with an op-amp cascode reaches MHz bandwidth at sub-nV/√Hz; the closest open-literature example to the DC–10 MHz goal.

### C10. Jefferts and Walls (1987, 1989), very-low-noise FET cascode amplifier

- **Citations:** S. R. Jefferts and F. L. Walls, "A low noise cascode amplifier," *J. Res. Natl. Bur. Stand.* 92(6), Nov.–Dec. 1987 (page range not checked); S. R. Jefferts and F. L. Walls, "A very low-noise FET input amplifier," *Rev. Sci. Instrum.* 60(6), 1194 (June 1989) (first page and footer read).
- **Files:** `Jefferts_1987_Low_Noise_Cascode_Amplifier_JResNBS.pdf`, `Jefferts_1989_Very_Low_Noise_FET_Input_Amplifier_RSI.pdf` (NIST Time and Frequency Division reprints).
- **Access:** 1989 p. 1194 read as an image; other pages by text extraction.
- **Contribution:** single Toshiba 2SK117 in a cascode with a common-base BJT, followed by an OP-27; **< 1.2 nV/√Hz and 0.25 fA/√Hz from 500 Hz to 500 kHz** (1989 abstract; the 1987 paper quotes 500 Hz–50 kHz); figure of merit $e_ni_n\approx3\times10^{-25}$ W/Hz; usable "with modest changes" from 1 Hz to 30 MHz. Eq. (1) (p. 1194): $E_{ni}^2=E_{nQ1}^2+I_{ni}^2Z_g^2+E_{nRs}^2+(1/K_{Q1})^2(E_{nQ2}^2+I_{nQ2}^2R_{s1}^2)+(1/K_t)^2E_{nRd}^2$, with $K_t=g_{m1}R_d$ and $K_{Q1}\approx-(g_{m1}/g_{m2})(1+g_{m2}r_{d1})$. Input capacitance measured by inserting a known series capacitor and observing the gain change (p. 1194).

### C11. Spinelli and Haberman (2024), ultra-low-noise fully-differential JFET amplifier, IEEE TIM

- **Citation:** E. M. Spinelli, M. A. Haberman, "An ultra-low noise fully-differential amplifier," *IEEE Trans. Instrum. Meas.* 73, 1–8 (2024). DOI: 10.1109/TIM.2024.3485398. Open-access author version in CONICET Digital, http://hdl.handle.net/11336/262504 (CC BY-NC-SA 2.5 AR).
- **File:** `Spinelli_2024_UltraLowNoise_FullyDifferential_JFET_Amplifier_TIM.pdf` (repository version; layout differs from the journal version).
- **Access:** pp. 2 and 4 read as images; remaining pages by text extraction.
- **Topology:** the **current-feedback (Model 601 / AD524-type) instrumentation-amplifier topology built with discrete JFETs** (Fig. 1 BJT version, Fig. 2 JFET version, p. 2): each input JFET drives an op-amp transimpedance stage; a common-mode loop keeps the JFET currents constant, $I_D=(V_P-V_B)/R_D$ (Eq. (3)), and the differential loop sets **$G_n=1+2R_B/R_A$, independent of the JFET parameters** (Eq. (2)); bandwidth $f_c=g_m/(2\pi C_FG_n)$ (Eq. (15)).
- **Noise (p. 4):** Eq. (18) $e_i^2\approx2e_{FET}^2+e_{RA}^2+2(e_{RB}/G_n)^2+2(i_{nA}/g_m)^2+2\frac{e_{RD}^2+e_{nA}^2}{(g_mR_D)^2}$; simplified Eq. (19) $e_i^2\approx2e_{FET}^2+e_{RA}^2+2\frac{e_{RD}^2+e_{nA}^2}{(g_mR_D)^2}$, Eq. (20) $e_i^2\approx2e_{FET}^2+e_{RA}^2$, Eq. (21) $e_i\approx\sqrt2\,e_{FET}$; with $N$ JFETs in parallel per side, **Eq. (22) $e_i\approx\sqrt2\,e_{FET}/\sqrt N$, $i_i\approx\sqrt{2N}\,i_{FET}$**. The authors note that in single-ended circuits it is not enough to parallel JFETs; whole amplifiers must be paralleled, otherwise the bias sources' noise becomes significant (p. 4, citing their Ref. [4]). IF3602-class devices are called out for "several hundreds of pF" input capacitance and up to 100 mV offsets.
- **Built example (pp. 4–6):** TI JFE2140, **N = 2 per side, $I_D=7$ mA per JFET** ($e_{FET}\approx0.9$ nV/√Hz at 7 mA), $R_A=1$ Ω, $R_B=500$ Ω (G = 1001, 60 dB), $R_D=500$ Ω, $C_F=20$ pF, OPA211, ±12 V. Measured (Table 1, p. 2; Figs. 7–8): **$e_n=0.9$ nV/√Hz at 1 kHz; $i_n<10$ fA/√Hz (2.25 fA/√Hz expected); $C_{in}=23$ pF; CMRR 96 dB untrimmed with 1 % resistors, 109 dB after trimming the drain-resistor balance (1 kHz); PSRR 84 dB; $I_Q$ 45 mA; GBP 200 MHz; DC to 100 kHz**; with $R_A=10$ Ω (40 dB) the noise is 0.98 nV/√Hz (0.4 nV/√Hz from $R_A$). Offset −1.35 mV, bias current 2.7 pA. Table 1 also compares with commercial ICs (8 nV/√Hz JFET-input, 15 pF; 1.0–3.2 nV/√Hz BJT-input with 800–1100 fA/√Hz) and with earlier discrete JFET designs (e.g. 0.8 nV/√Hz with 460 pF; 1.0 nV/√Hz with 80 pF).
- **Relevance:** the closest published analogue of the planned paralleled-JFET differential front end with a gain set by resistors rather than by $g_m$; it gives the noise and CMRR budget equations directly.

### C12. Märki, Braem and Ihn (2017), temperature-stabilized differential amplifier

- **Citation:** P. Märki, B. A. Braem, T. Ihn, "Temperature-stabilized differential amplifier for low-noise DC measurements," arXiv:1708.06311v1 (22 Aug 2017). Journal version not checked.
- **File:** `Marki_2017_Temperature_Stabilized_Differential_Amplifier_arXiv1708.06311.pdf`
- **Access:** abstract and the specification table (p. 5) by text extraction.
- **Contribution (Table, p. 5):** IF3602 input pair, thermally stabilized; $e_n$ 10 / 1.7 / 1 nV/√Hz at 0.1 / 1 / 10 Hz, 4.7 nV rms (0.1–10 Hz); $i_n$ 1.7 fA/√Hz at 1 Hz; input capacitance $C_P,C_N=10$ pF each and differential $C_D<1$ pF (measured at 10 Hz); leakage < 100 fA; input resistance > 1 TΩ; bandwidth 100 kHz; CMRR > 140 dB; common-mode range ±1 V; drift about 100 nV/day. How the low input capacitance is obtained with an IF3602 was not read.

### C13. Sampietro, Fasoli and Ferrari (1999), cross-correlation spectrum analyzer

- **Citation:** M. Sampietro, L. Fasoli, G. Ferrari, "Spectrum analyzer with noise reduction by cross-correlation technique on two channels," *Rev. Sci. Instrum.* 70, 2520–2525 (1999). DOI: 10.1063/1.1149785.
- **Access:** abstract only.
- **Contribution:** two independent input amplifiers on the same DUT; uncorrelated amplifier noise suppressed by cross-correlation; sensitivity better than a few pV/√Hz (voltage) and below 1 fA/√Hz (current); 10 mHz–1 MHz; modular front ends for low- and high-impedance DUTs.

### C14. Ferrari and Sampietro (2002), correlation analyzer for device current noise

- **Citation:** G. Ferrari, M. Sampietro, "Correlation spectrum analyzer for direct measurement of device current noise," *Rev. Sci. Instrum.* 73, 2717–2723 (2002). DOI: 10.1063/1.1487891.
- **Access:** abstract only. Design rules for the input amplifiers (noise, dynamic range, stability, bandwidth) including DUTs with complex impedance.

### C15. Rubiola and Vernotte, the cross-spectrum method

- **Citation:** E. Rubiola, F. Vernotte, "The cross-spectrum experimental method," arXiv:1003.0113 (v1, 2010; the downloaded file's footer is dated 23 Oct 2018).
- **File:** `Rubiola_2010_Cross_Spectrum_Experimental_Method_arXiv1003.0113.pdf`
- **Access:** pp. 9–19 by text extraction (equations located and transcribed; not rendered).
- **Contribution:** Eq. (11), p. 9: $\langle S_{yx}\rangle_m=S_{cc}+O(\sqrt{1/m})$, the uncorrelated channel noise decreasing as $1/\sqrt m$; on a log scale the background of $|\langle S_{yx}\rangle_m|$ falls as $5\log_{10}m$ dB with a constant spread, Eq. (17), p. 18: $\mathrm{dev}/E=\sqrt{4/\pi-1}=0.523$; for the estimator $\Re\{\langle S_{yx}\rangle_m\}$, Eqs. (18)–(21), p. 19: $E=\kappa^2$, $\mathrm{dev}/E\approx(1+\kappa^2)/(\kappa^2\sqrt{2m})$ ($\kappa^2$ = DUT noise relative to single-channel background); with the DUT 20 dB below the background ($\kappa=0.1$) about $5\times10^3$ averages are needed for 0 dB SNR (p. 19).
- **Relevance:** sets the averaging time needed to verify a sub-nV/√Hz floor with a pair of amplifiers.

### C16. Achtenberg, Mikołajczyk and Bielecki (2020), FET-input amplifier, Metrol. Meas. Syst.

- **Citation:** K. Achtenberg, J. Mikołajczyk, Z. Bielecki, "FET input voltage amplifier for low frequency noise measurements," *Metrol. Meas. Syst.* 27(3), 531–540 (2020). DOI: 10.24425/mms.2020.132785 (open access).
- **Access:** pp. 1–3 by text extraction from a copy obtained during this session; the file was not saved because its download URL was not recorded.
- **Contribution:** measured $e_n$ about 24, 3, 0.95, 0.6 nV/√Hz at 0.1, 1, 10, 100 Hz; −3 dB band about 20 mHz–600 kHz (abstract). JFET noise model Eq. (2): $v_{nJFET}=\sqrt{v_{1/f}^2+4kT\frac{2}{3}\frac{1}{g_m}}$; gate shot noise Eq. (3): $i_{nJFET}=\sqrt{2qI_G}$, which grows with $V_{DG}$ through impact ionization. Table 1 (p. 3) lists common-source test conditions for several JFETs (e.g. BF862 at 14 mA, $g_m=35.6$ mS, $R_D=500$ Ω, gain 17.8).

### C17. Rescia (2016), Brookhaven low-noise front ends (InterFET-hosted slides)

- **Citation:** S. Rescia (Brookhaven National Laboratory), "Low Noise Front-End for HEP Experiments: from the Brookhaven Years to the Road Ahead — In Memoriam of Franco Manfredi 1935–2015," talk, Pavia, 5 Dec. 2016 (slide footer: "Detecting Signals into the Noise"); PDF hosted by InterFET.
- **File:** `Rescia_2016_LowNoise_FrontEnd_HEP_Manfredi_Symposium_InterFET.pdf` (31 slides; the same file is also in `refs/datasheets/jfet/InterFET/`).
- **Access:** slide 21 read as an image; slides 13–15 and 20 located by text search.
- **Contribution:** slide 21, "Franco's 200 pV/√Hz amplifier": front end with **six NJ3600-geometry JFETs in parallel**, white floor marked at **200 pV/√Hz**; the reproduced figure caption states measurements on the parallel combination of six JFETs at total standing currents of 2.5 mA and 28.7 mA; the original paper is not identified on the slide. Slides 13–15: JFET series-noise spectra versus temperature and radiation (NJFET W/L = 3350/3 with $C_{ISS}\approx15$ pF; another with $C_{ISS}\approx11$ pF, with $C_D=33$ pF). Slide 20 reproduces a Basel I-to-V converter datasheet (SP 983 with IF3602: 2 nV/√Hz at 10 Hz, 1.2 nV/√Hz at 1 kHz).

### C18–C21. Items not read

- **C18.** Neri, Pellegrini and Saletti, "Ultra low-noise preamplifier for low-frequency noise measurements in electron devices," *IEEE Trans. Instrum. Meas.* 40 (1991): **not accessed; bibliographic details not verified here.**
- **C19.** R. Pallàs-Areny and J. G. Webster, "Common mode rejection ratio in differential amplifiers," *IEEE Trans. Instrum. Meas.* 40(4), 669–676 (1991), DOI 10.1109/19.85332; and "Common mode rejection ratio for cascaded differential amplifier stages," ibid. 677–681, DOI 10.1109/19.85333: **citation verified in Crossref; text not read** (paywalled).
- **C20.** P. C. D. Hobbs, *Building Electro-Optical Systems: Making It All Work*, 2nd ed., Wiley, 2009 (front-end chapters), and "Photodiode front ends: the real story," *Optics & Photonics News* (2001): **not read in this pass.**
- **C21.** University of Basel Physics Electronic Lab (M. Steinacher), "Low noise / low drift differential amplifier SP 1'004," datasheet v1.0, April 2017: first page read from a copy obtained during this session (URL not recorded; file not saved). Specified DC–1 MHz, 4 / 1.5 / 1.0 nV/√Hz at 1 / 10 / >100 Hz, CMRR ≥ 100 dB at 100 Hz, gains 100/1000/10 000, input resistance 10 MΩ / 1 GΩ / ∞ (DC). A direct commercial-style competitor to the target instrument.

---

## Part D. Vendor application notes, data sheets and reference designs

### D1. Cordell, LSK389 application note (Linear Integrated Systems)

- **Citation:** B. Cordell, "Dual Monolithic JFET for Ultra-Low Noise Applications — LSK389 Application Note," Linear Integrated Systems, Rev. A4.
- **File:** `LinearSystems_Cordell_2024_LSK389_AppNote_RevA4.pdf`
- **Access:** all 14 pp. by text extraction (schematic values read from the extracted text, figures not rendered).
- **Contribution:**
  - Key data (p. 2): 1.3 nV/√Hz at 1 kHz and 1.5 nV/√Hz at 10 Hz ($I_D=2$ mA), $g_m=14$ mS at 2 mA, $C_{ISS}=25$ pF typ., $C_{RSS}=5.5$ pF typ., 100 % noise tested.
  - JFET basics (pp. 2–3): $I_D=\beta(V_{GS}-V_t)^2$, $g_m=2\sqrt{\beta I_D}$; voltage noise modelled as the thermal noise of $r_n\approx0.67/g_m$ (0.6 quoted from the literature, 0.67 from SPICE models), so $e_n\propto I_D^{-1/4}$; a measured part with $g_m=14.6$ mS at 2 mA gives $r_n=45.9$ Ω, i.e. 0.9 nV/√Hz theoretical. 10 Ω of ohmic source resistance would add 0.4 nV/√Hz (p. 4).
  - **Table 1 (p. 5), measured input noise versus drain current (two-stage LSK389 test amplifier, A-weighted, ENBW 13.5 kHz): 0.5 mA → 1.72, 1 mA → 1.44, 2 mA → 1.17, 4 mA → 1.11, 8 mA → 1.07 nV/√Hz**; the fall with current is slower than channel-noise theory, attributed to ohmic gate and source resistance; at 8 mA and 10 V the part runs warm (160 mW).
  - **Paralleling (p. 5):** two LSK389 devices at 4 mA each give about 0.8 nV/√Hz, better than one device at 8 mA (about 1.07 nV/√Hz). A differential pair is 3 dB noisier than a single JFET, and 6 dB noisier than the two halves of an LSK389 paralleled single-ended at the same total current (p. 8).
  - Gate shot noise $i_{shot}=0.57$ fA/√Hz per √pA; example: 4 fA/√Hz into 100 MΩ gives 400 nV/√Hz, comparable with the 1330 nV/√Hz Johnson noise of 100 MΩ, and quadrupling at 65 °C (leakage doubles per 10 °C) (p. 6). 1/f: a good JFET is about 6 dB up at 10 Hz, 3 dB corner near 40 Hz (p. 6).
  - Cascodes (Fig. 5, p. 10): BJT cascode, bootstrapped JFET cascode (common-mode signal fed to the cascode gates, suppressing the effect of $C_{gd}$ on input capacitance), and "driven cascode" for feedback amplifiers.
  - **Fig. 6 (pp. 11–12): ultra-low-noise differential amplifier using four paralleled LSK389 differential pairs, each with its own 4 mA tail current source (2 mA per JFET, 16 mA total in the input pairs), double folded cascode (NPN cascode with 100 Ω drain stoppers), no overall feedback, gain about 40 dB (about 100, set by the input-pair $g_m$ and a shunt load resistor), input-referred noise 0.7 nV/√Hz, bandwidth about 10 MHz, THD 0.005 % at 5 mV rms input.** Separate tail sources decouple the pairs and avoid gate-stopper resistors; a fifth (LSK489) pair can inject a DC-servo correction; gain may need trimming and has a modest temperature coefficient. Input capacitance is not stated.
- **Relevance:** the only document found with a measured paralleled-JFET **differential** amplifier at about 10 MHz bandwidth; directly relevant to the DC–10 MHz target.

### D2. Cordell, LSK489 application note

- **Citation:** B. Cordell, "LSK489 Application Note," Linear Integrated Systems, Rev. A2.
- **File:** `LinearSystems_Cordell_2026_LSK489_AppNote_RevA2.pdf`
- **Access:** text extraction of all pages (figures not rendered).
- **Contribution:** the $e_n$–$C_{in}$ trade-off between two duals: LSK389, about 1 nV/√Hz with an input capacitance "of over 20 pF", versus LSK489, 1.5 nV/√Hz at 1 kHz with 4 pF input capacitance and 1.5 pF gate–drain capacitance, $g_m$ about 3 mS at 2 mA, 60 V breakdown (p. 2). Theoretical noise for $g_m=3$ mS: $r_n=0.67/g_m=200$ Ω → about 1.8 nV/√Hz (p. 3). Nonlinear junction capacitance causes intermodulation with high source impedance; Miller multiplication of $C_{gd}$ argues for cascodes or low-$C_{rss}$ parts (p. 2). Discusses G–R and impact-ionization noise (p. 5, Fig. 1), common-substrate effects (p. 6), JFET op-amp front ends with LM4562 (Fig. 5), JFET cascodes including a driven cascode that removes $C_{rss}$ from the input (Fig. 6, p. 10), and microphone/phono/accelerometer examples.

### D3. Rough and McCune, CMRR in dual JFETs (Linear Integrated Systems)

- **Citation:** K. Rough, T. S. McCune, "Common Mode Rejection Ratio in Dual Junction Field Effect Transistors," Linear Integrated Systems, Rev. C1.4.
- **File:** `LinearSystems_Rough_2024_CMRR_in_Dual_JFETs_RevC1-4.pdf`
- **Access:** pp. 1–4 by text extraction.
- **Contribution:** qualitative only: interleaved (cross-coupled) monolithic duals track over temperature; CMRR = $A_{v(d)}/A_{cm}$; a constant-current tail keeps total drain current invariant and maximizes CMRR, whereas resistive tail bias lets the common-mode voltage modulate the gain (p. 3). No equations.

### D4. Quan, FETs for sensor applications (Linear Integrated Systems)

- **File:** `LinearSystems_Quan_2024_FETs_for_Sensor_Applications_RevA2.pdf` (20 pp.)
- **Access:** first page only. Discusses JFETs ahead of bipolar-input op-amps for photodiode, accelerometer and transducer front ends. Not reviewed further.

### D5. Texas Instruments JFE150 / JFE2140 application notes (files in `refs/datasheets/jfet/TI/`)

- **C. Featherstone, "JFE150 Ultra-Low-Noise Pre-Amp," TI SLPA018, Oct. 2021** (`TI_JFE150_appnote_UltraLowNoisePreAmp_SLPA018.pdf`). Access: text extraction of all pages. Single JFE150 at $I_{DS}=2$ mA in common source, OPA202 transimpedance stage ($R_1=1$ MΩ) closing the loop; $A_V=g_mR_1$ (Eq. 1); $g_m=15.7$ mS from simulation (Eq. 2); 60 dB gain, flat about 16 Hz–43 kHz; **simulated** input noise 1.99 nV/√Hz at 10 Hz and 1.18 nV/√Hz at 1 kHz (Fig. 3-1, p. 9).
- **C. Featherstone, "JFE2140 Ultra-Low-Noise Preamplifier," TI SBOA563, Mar. 2023** (`TI_JFE2140_appnote_UltraLowNoisePreAmplifier_SBOA563.pdf`). Access: text extraction. JFE2140 matched pair as a differential front end (2 mA tail, 1 mA each, measured $g_m\approx7.5$ mS at 1 mA) followed by OPA202 stages, closed-loop gain 60 dB; Table 2-1 (p. 6): **−3 dB at 17.3 kHz, 1.96 nV/√Hz at 1 kHz, 3.6 mA total**, versus OPA145 alone (5.56 kHz, 7.1 nV/√Hz) and OPA202 alone (988 Hz, 8.9 nV/√Hz).
- **C. Featherstone, "Ultra-Low-Noise JFET Preamplifier Design for High Impedance Sensors," TI SBOA589, May 2024** (`TI_appbrief_UltraLowNoiseJFETPreampHighImpedanceSensors_SBOA589.pdf`). Access: text extraction. JFE2140 source followers (1.59 mA each, $R_S=400$ Ω, $R_D=5$ kΩ) in front of an INA849 (gain 60 dB). Table 1 (p. 3): with $R_{source}=100$ kΩ the input-referred noise at 1 kHz falls from 162.07 to 57.63 nV/√Hz (−64.4 %) for a 47.2 % increase in supply current (6.71 → 9.88 mA). Crossover criterion Eqs. (1)–(2), p. 4: JFETs help when $R_{source}>4kT/i_n^2$, i.e. above 13.6 kΩ for the INA849's 1.1 pA/√Hz. Table 2 compares calculated totals versus $R_{source}$.

### D6. Kay and Rivera, impact of current noise in CMOS and JFET amplifiers (TI SBOA570, 2023)

- **File:** `TI_Kay_2023_SBOA570_Current_Noise_CMOS_JFET.pdf`
- **Access:** pp. 1–3 by text extraction.
- **Contribution:** current noise dominates when $R_s>4kT/i_n^2$ (p. 2); table (p. 3) of the source resistance at which current noise equals resistor noise: 1 fA/√Hz ↔ 16.5 GΩ, 10 fA/√Hz ↔ 165 MΩ, 100 fA/√Hz ↔ 1.65 MΩ, 1 pA/√Hz ↔ 16.5 kΩ. Later sections treat parasitic capacitance (not read).

### D7. Olson, optimizing CMRR with matched resistor pairs (TI SBOA582, 2023)

- **File:** `TI_2023_SBOA582_Optimizing_CMRR_Matched_Resistor_Pairs.pdf`
- **Access:** pp. 1–6 by text extraction. Equations are collected in Part E.

### D8. INA103 data sheet (TI, Rev. A, 2023; original Burr-Brown 1998)

- **File:** `TI_2023_INA103_datasheet_RevA.pdf`
- **Access:** specification table and applications pages by text extraction.
- **Contribution:** current-feedback BJT instrumentation amplifier: 1 nV/√Hz at 1 kHz, 1.2 nV/√Hz at 100 Hz, 2 nV/√Hz at 10 Hz ($R_S=0$), 2 pA/√Hz at 1 kHz; CMR (DC–60 Hz) 86 dB typ. at G = 1 and 125 dB typ. at G = 100 (100 dB min.); input impedance 60 MΩ ∥ 2 pF differential, 60 MΩ ∥ 5 pF common mode; 100 MHz GBW at G = 1000; a few ohms in series with the Sense or Ref pins degrade CMR; optional CMR trim (Fig. 10); a shield driver is shown to limit CMR degradation from distributed input-cable capacitance (p. 12).

### D9. THAT 1510/1512 data sheet (THAT Corp., Rev. 09, 2017)

- **File:** `THAT_2017_1510-1512_datasheet_Rev09.pdf`
- **Access:** pp. 1–7 by text extraction.
- **Contribution:** current-feedback in-amp (Fig. 1 equivalent circuit, p. 1). 1510: $e_n$ 57 / 7 / 1.7 / 1 nV/√Hz at 0 / 20 / 40 / 60 dB gain (1 kHz), $i_n$ 2.0 pA/√Hz (p. 3); **CMRR typ. 60 / 80 / 100 / 120 dB at 0 / 20 / 40 / 60 dB gain (DC–60 Hz; min. 45 / 65 / 85 / 105 dB)** (p. 3); −3 dB bandwidth 15 / 8 / 7 / 3 MHz at 0 / 20 / 40 / 60 dB gain (p. 3); 6 mA supply current. Applications (p. 6): with input coupling capacitors, the capacitor mismatch together with the common-mode input impedance forms unequal dividers that spoil low-frequency CMRR; a higher common-mode input impedance relaxes the matching requirement.

### D10. Williams, LT AN124 (2009): 775 nV noise measurement of a reference

- **Citation:** J. Williams, "775 Nanovolt Noise Measurement for a Low Noise Voltage Reference: Quantifying Silence," Linear Technology Application Note 124, July 2009.
- **File:** `LT_Williams_2009_AN124_775nV_Noise_Measurement.pdf`
- **Access:** pp. 1–5 by text extraction.
- **Contribution:** 0.1–10 Hz test set with a gain-of-$10^4$ preamplifier whose first stage is a **thermally mated 2SK369 pair (matched $V_{GS}$ within 10 %) or an LSK389 dual** (Fig. 3, p. 3); 160 nV p-p noise floor (0.1–10 Hz) obtained with special layout and thermal techniques (Fig. 6, p. 4); LTC6655 measured at 775 nV p-p (Fig. 8, p. 5).

### D11. Owen and Patel, LT AN159 (2016): measuring 2 nV/√Hz regulator noise

- **Citation:** T. Owen, A. Patel, "Measuring 2nV/√Hz Noise and 120dB Supply Rejection on Linear Regulators," Linear Technology Application Note 159, Feb. 2016 (an159fa).
- **File:** `LT_Owen_2016_AN159_Measuring_2nV_Noise_120dB_PSRR.pdf`
- **Access:** pp. 1–3 by text extraction.
- **Contribution:** to measure 2 nV/√Hz within 5 % the instrument needs about 1 nV/√Hz; within 1 %, about 450 pV/√Hz (p. 2). Their first stage: **two matched pairs of THAT300 BJTs in parallel** plus an LT1818, stage gain 25, giving about 800 pV/√Hz (p. 3); $\sqrt N$ reduction by paralleling. (BJT front end; useful as a measurement-instrument reference and for the rail-noise budget.)

### D12. Williams, chopped FET amplifier (Linear Technology Magazine, March 2006)

- **Citation:** J. Williams, "40nV P–P Noise, 0.05µV/°C Drift, Chopped FET Amplifier," *Linear Technology Magazine*, March 2006, p. 39 (Design Ideas).
- **File:** `LT_Williams_2006_Chopped_FET_Amplifier_40nVpp_LTMagazine.pdf` (1 p.)
- **Access:** text extraction of the single page.
- **Contribution:** an LSK389 pair in a 925 Hz chopper (carrier-modulation) scheme with an LTC6241 and LTC201 switches; 40 nV p-p in 0.1–10 Hz measured over 50 s (Fig. 2), 0.05 µV/°C drift; the low noise is attributed to the JFETs' die size and current density.

### D13. LT3045 and LT3094 ultralow-noise regulators (Analog Devices)

- **Files:** `ADI_2022_LT3045_Datasheet_RevD.pdf`, `ADI_2020_LT3094_Datasheet_RevB.pdf`
- **Access:** first page (features) by text extraction only.
- **Contribution:** LT3045 (positive, 20 V, 500 mA): 0.8 µV rms (10 Hz–100 kHz), 2 nV/√Hz at 10 kHz, PSRR 76 dB at 1 MHz, can be paralleled to reduce noise. LT3094 (negative, −20 V, 500 mA): 0.8 µV rms (10 Hz–100 kHz), 2.2 nV/√Hz at 10 kHz, PSRR 74 dB at 1 MHz, parallelable.

### D14. Siliconix AN106 (1997): low-noise JFETs versus bipolars

- **File:** `Siliconix_1997_AN106_LowNoise_JFETs_vs_Bipolars.pdf` (5 pp.)
- **Access:** first page only. Argues JFETs beat bipolars on low-frequency noise for source impedances down to about 5 kΩ and dramatically at higher source impedances; table of recommended parts. Not reviewed further.

### D15. JFET data sheets

JFET data sheets (InterFET IF3601/IF3602/IF9030/IFN146/IFN860, Linear Systems LSK170/LSK389/LSK489/LSBF862, TI JFE150/JFE2140/JFE2325 and others) were collected separately in `refs/datasheets/jfet/` and were not reviewed for these notes.

---

## Part E. CMRR of difference and current-feedback instrumentation-amplifier topologies

1. **Definition.** $\mathrm{CMRR}=A_D/A_{CM}$, in dB $20\log_{10}(A_D/A_{CM})$ (D7, Eqs. (3)–(4), p. 3; also D3, p. 2).
2. **Four-resistor difference amplifier (output subtractor of a classic in-amp).** Worst-case resistor-limited CMRR with four resistors of tolerance $t$: **$\mathrm{CMRR}_R=\frac{G+1}{4t}$** (D7, Eq. (7), p. 5); with a matched-ratio divider pair of ratio tolerance $t_m$: $\mathrm{CMRR}_R=\frac{G+1}{t_m}$ (D7, Eq. (9), p. 6); combination with the op-amp's own CMRR: **$\frac{1}{\mathrm{CMRR}_D}=\frac{1}{\mathrm{CMRR}_A}+\frac{1}{\mathrm{CMRR}_R}$** (D7, Eq. (8), p. 5); example: 0.5 % 1 kΩ resistors around an OPA387 give only about 40 dB worst case (p. 4), and at high frequency the falling op-amp $A_{OL}$ makes $\mathrm{CMRR}_A$ dominant (Fig. 2-4, p. 5).
3. **Current-feedback (transconductance) in-amp.** Gain $G_n=1+2R_B/R_A$, independent of the input-device parameters, with a common-mode loop that holds the device currents constant (C11, Eqs. (1)–(3), p. 2; Figs. 1–2). Measured with discrete JFE2140 pairs: 96 dB at 1 kHz untrimmed (1 % resistors), 109 dB after trimming the drain-resistor balance (C11, p. 6). Integrated BJT versions show CMRR rising about 20 dB per 20 dB of gain: THAT1510 typ. 60/80/100/120 dB at 0/20/40/60 dB (D9, p. 3); INA103 86 dB at G = 1 and 125 dB at G = 100 (D8, p. 2). **[derived]** This is the behaviour expected when the input stage passes common-mode signals at unity gain while amplifying differential signals by $G$, so that the subtractor's CMRR is multiplied by about $G$: $\mathrm{CMRR}_{tot}\approx G\cdot\mathrm{CMRR}_{sub}$, until limited by input-device mismatch or by frequency-dependent effects. None of the documents read states this formula explicitly.
4. **Source-impedance imbalance.** Unequal source or coupling impedances form unequal dividers with the common-mode input impedance $Z_{cm}$ and convert common-mode voltage into differential error (D9, p. 6). **[derived]** For a small imbalance $\Delta Z_s\ll Z_{cm}$, $\mathrm{CMRR}_Z\approx Z_{cm}/\Delta Z_s$; with $Z_{cm}$ dominated by input capacitance (for example 20 pF, about 8 kΩ at 1 MHz) a 10 Ω imbalance limits CMRR to about 58 dB at 1 MHz. The classic treatment (C19, Pallàs-Areny and Webster) was not read; AoE3 indexes a graph "CMRR vs Rsource mismatch" on p. 366 (A1), content not read.
5. **Discrete JFET pairs.** Constant-current (ideally cascoded, high-impedance) tails are needed to preserve CMRR; noise from the tail source largely cancels differentially (D1, p. 9; D3, p. 3). Measured CMRR of discrete designs: > 40 dB (C1, simple feedback pair), 109 dB trimmed (C11), > 140 dB (C12, thermally stabilized; method not read).

---

## Part F. Comparison of measured JFET-input preamplifiers (values as reported)

| Design (source) | Topology | Input devices; current | $e_n$ (white) | Low-frequency $e_n$ | $C_{in}$ | Bandwidth | Other |
|---|---|---|---|---|---|---|---|
| Cordell, Fig. 6 (D1, pp. 11–12) | differential, open loop, double folded cascode | 4 LSK389 pairs in parallel, 2 mA per JFET (16 mA in input pairs) | 0.7 nV/√Hz | not given | not given | about 10 MHz | gain about 40 dB; THD 0.005 % at 5 mV rms |
| Spinelli and Haberman (C11) | fully differential current-feedback in-amp | 2 JFE2140 per side, 7 mA each (28 mA in JFETs; 45 mA total) | 0.9 nV/√Hz at 1 kHz | Fig. 7 (values not transcribed) | 23 pF | DC–100 kHz (GBP 200 MHz) | $i_n$ < 10 fA/√Hz; CMRR 109 dB trimmed |
| Callegaro et al. (C9) | single-ended (pseudo-differential wiring), JFET + op-amp cascode | 1 × 2SK170, $V_{GS}\approx0$ | about 0.8 nV/√Hz | not given | about 30 pF (datasheet, Table 1) | 3 dB about 4 MHz; ±1 dB to 1 MHz | $i_n$ < 1 fA/√Hz; input range tens of mV |
| Scandurra et al. 2019 (C3) | single-ended open loop, CS | 1 × IF3601, 2.5 mA | 0.5 nV/√Hz (1–10 kHz) | 6 nV/√Hz at 0.2 Hz; 0.7 at 10 Hz | about 500 pF | to about 10 kHz | gain by cross-correlation |
| Levinzon 2008 (C5, abstract) | single JFET stage | 1 JFET, 5 mA (per C3) | 0.5 nV/√Hz at 1 kHz | 5.6 at 0.1 Hz; 1.4 at 1 Hz | not given | 0.07 Hz–110 kHz | gain about 83 dB |
| Scandurra et al. 2011 (C1) | differential, feedback | IF3602 pair, about 4.5 mA each | about 1 nV/√Hz | 14 at 0.1 Hz; 2 at 1 Hz | about 80 pF (differential) | > 30 kHz | CMRR > 40 dB |
| Cannatà et al. 2009 (C2, abstract) | differential (per C3), feedback | IF3602, 4 mA | 0.8 nV/√Hz at 1 kHz | 14 at 0.1 Hz; 1.4 at 1 Hz | not given | few tens of mHz to a few kHz | $i_n$ < 4 fA/√Hz |
| Märki et al. (C12) | differential DC amplifier | IF3602 | 1 nV/√Hz at 10 Hz | 10 at 0.1 Hz; 1.7 at 1 Hz | 10 pF per input, < 1 pF differential | 100 kHz | CMRR > 140 dB; $i_n$ 1.7 fA/√Hz |
| Jefferts and Walls (C10) | single-ended cascode | 1 × 2SK117 | < 1.2 nV/√Hz (0.5–500 kHz) | not given | measured, value not transcribed | to 500 kHz (1 Hz–30 MHz possible) | $i_n$ 0.25 fA/√Hz |
| Manfredi, via Rescia (C17) | single-ended | 6 × NJ3600-geometry JFETs; 2.5 mA and 28.7 mA total (two curves) | about 0.2 nV/√Hz | see slide 21 | not given | not given | slide only |
| TI SBOA563 (D5) | differential pair + op-amps, 60 dB | JFE2140 pair, 1 mA each | 1.96 nV/√Hz at 1 kHz | not given | not given | 17.3 kHz | 3.6 mA total |
| Basel SP 1'004 (C21) | differential lab amplifier | not stated on p. 1 | 1.0 nV/√Hz above 100 Hz | 4 at 1 Hz; 1.5 at 10 Hz | not stated | DC–1 MHz | CMRR ≥ 100 dB at 100 Hz |
| SR560 benchmark | for reference only | — | 4 nV/√Hz | — | 25 pF | DC–1 MHz | from the brief |

**[derived] Paralleling arithmetic checked against the sources.** With $N$ identical devices at the same per-device current the white noise power falls as $1/N$ while $C_{in}$ and gate shot noise grow as $N$ (Part B, items 7–8; C11 Eq. (22); D1 p. 5). D1 reports 1.17 nV/√Hz for one LSK389 at 2 mA and 0.7 nV/√Hz for a differential input with four pairs; $\sqrt2\times1.17/\sqrt4\approx0.83$ nV/√Hz, so the reported 0.7 nV/√Hz is somewhat better than this simple scaling (the A-weighted single-device figure in Table 1 includes test-circuit noise, which D1 itself suggests).

---

## Part G. Gaps and items not accessed

- *The Art of Electronics* 3rd ed. text (§8.6, Table 8.2, SR560 description) could not be read from a legitimate open source; only the TOC and indexes were verified (A1). There is no Chapter 8x in the published x-Chapters (A2).
- Radeka (1988) Annual Review not accessible (Part B, T2); Radeka (2020) used instead.
- Levinzon papers, Cannatà 2009, Sampietro 1999, Ferrari 2002: abstracts only. Neri et al. 1991 and Pallàs-Areny and Webster 1991: not read.
- Hobbs, *Building Electro-Optical Systems*: not read.
- ADI tutorials (MT-061/MT-065, Kitchin and Counts in-amp guide) could not be downloaded (server refused automated access).
- No open source with measured $\gamma$ for discrete low-noise JFETs; no open source giving a JFET-specific $C_{gs}=C_{det}/3$ derivation (Part B, gaps).
- Input capacitance of the Cordell four-pair amplifier (D1) is not stated; it should be estimated from LSK389 data ($C_{ISS}$ 25 pF, $C_{RSS}$ 5.5 pF per device) with the cascode and differential connection taken into account.
