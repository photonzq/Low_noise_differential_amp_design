# A differential low-noise voltage preamplifier, DC–10 MHz, with paralleled JFETs

Design study and ngspice simulations of a successor to the SR560 class of laboratory preamplifiers: a DC-coupled differential preamplifier with two switchable current-feedback JFET front ends (H, high impedance; L, low impedance), gains from 1 to 100 000 and a bandwidth beyond 10 MHz.

| Path | Content |
|---|---|
| `low_noise_preamp.pdf` | the note; `low_noise_preamp.md` is its source and `index.html` its web version |
| `figures/` | the note's figures (PNG and PDF) |
| `scripts/` | every simulation, closed form, derived number and figure of the note; `scripts/README.md` lists each script with its results and the order to reproduce everything |
| `netlists/` | standalone netlists of the front ends, the complete chain and the SR560 reproduction (`ngspice -b <file>`, after the models are prepared) |
| `sim/results/` | the archived results that the note's numbers are taken from |
| `audit/` | the number audit of the note: its findings and the patches that applied it |
| `refs/` | the READMEs and surveys of the references: document numbers, revisions, URLs and the pages read |

Not in this repository:

- the vendors' SPICE models: each remains under its vendor's terms and must be downloaded from its vendor as `sim/models/README*.md` describes; `scripts/models.py` then prepares them;
- `sim/results/jfet_calibration.json`, which embeds the vendors' JFET cards (`scripts/models.py` writes it);
- the data sheets, manuals, papers and web pages read for the note (their sources are in each `refs/` folder's README);
- `sim/runs/`, every deck with its log and data (about 0.5 GB), which the scripts regenerate.

Requirements: Python 3 with NumPy, SciPy, Matplotlib, schemdraw, PyMuPDF and Pillow; ngspice-46 as a shared library (`scripts/ngspice_shared.py` looks for KiCad's); LTspice's component library in `%LOCALAPPDATA%\LTspice\lib\cmp\` (the 2N5564 and other Linear Systems JFET cards, and the BJT cards); pandoc and Chrome for the build of the PDF and the web page (`scripts/build_note.py`, `scripts/make_web_html.py`).
