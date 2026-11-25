"""Patch of low_noise_preamp.md (25 November 2026): the classic papers on the location of 1/f noise in bipolar
transistors cited in Section 3.5 and listed in the References, each at abstract level (their full texts are closed):
Plumb and Chenette (1963), Jaeger and Brodersen (1970), van der Ziel, Zhang and Pawlikiewicz (1986) and Pawlikiewicz and
van der Ziel (1987).  Each DOI was checked against Crossref (authors, title, volume, issue, pages, year) and each
abstract read on IEEE Xplore (documents 1473505, 1476121, 1485889, 1486899) for this patch.
Exact-string edits, each old text once; a second run refused.
Usage: python patch_bjt_classics.py <path to low_noise_preamp.md>
"""
from __future__ import annotations

import sys
from pathlib import Path

TEXT = (" Plumb and Chenette (1963) found that for many transistors the flicker noise is represented adequately by a "
        "single noise-current generator in parallel with the emitter–base junction. Jaeger and Brodersen (1970), "
        "measuring purpose-built tetrode transistors, separated two 1/f sources, one at the surface and one in the "
        "active base region, from burst noise at the forward-biased emitter–base junction. Van der Ziel, Zhang and "
        "Pawlikiewicz (1986) described the general case by three independent noise-current generators, between base "
        "and emitter, base and collector, and emitter and collector, with a method that tells them apart by the "
        "emitter's feedback; Pawlikiewicz and van der Ziel (1987) applied it to two transistors, in one of which "
        "generation–recombination noise dominated and in the other, less noisy one, diffusion noise. (These four are "
        "cited from their abstracts.)")

REFS = ("- J. L. Plumb and E. R. Chenette, \"Flicker noise in transistors\", *IEEE Trans. Electron Devices* 10(5), "
        "304–308 (1963), https://doi.org/10.1109/T-ED.1963.15202 (abstract only).\n"
        "- R. C. Jaeger and A. J. Brodersen, \"Low-frequency noise sources in bipolar junction transistors\", *IEEE "
        "Trans. Electron Devices* 17(2), 128–134 (1970), https://doi.org/10.1109/T-ED.1970.16937 (abstract only).\n"
        "- A. van der Ziel, X. Zhang and A. H. Pawlikiewicz, \"Location of 1/f noise sources in BJT's and HBJT's—I. "
        "Theory\", *IEEE Trans. Electron Devices* 33(9), 1371–1376 (1986), https://doi.org/10.1109/T-ED.1986.22672 "
        "(abstract only); A. H. Pawlikiewicz and A. van der Ziel, \"Location of 1/f noise sources in BJT's—II. "
        "Experiment\", *IEEE Trans. Electron Devices* 34(9), 2009–2012 (1987), https://doi.org/10.1109/T-ED.1987.23188 "
        "(abstract only).\n")

EDITS = [
    ("In a silicon bipolar transistor the low-frequency noise is a fluctuation of the base current. Kleinpenning",
     "In a silicon bipolar transistor the low-frequency noise is a fluctuation of the base current." + TEXT
     + " Kleinpenning"),
    ("**Papers on 1/f noise in bipolar transistors and JFETs.**\n- T. G. M. Kleinpenning,",
     "**Papers on 1/f noise in bipolar transistors and JFETs.**\n" + REFS + "- T. G. M. Kleinpenning,"),
]


def main() -> None:
    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    assert "\r" not in text
    if "Plumb and Chenette (1963)" in text:
        sys.exit("already patched: refusing a second run")
    for old, new in EDITS:
        c = text.count(old)
        assert c == 1, (c, old[:90])
        text = text.replace(old, new)
    print(f"{len(EDITS)} edits applied to {path.name}")
    path.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
