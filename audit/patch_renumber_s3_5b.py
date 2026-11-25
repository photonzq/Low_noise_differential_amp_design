"""Second renumbering for Section 3.5 (25 November 2026): its two new figures, the bipolar front end's schematic and
its noise-figure maps, become Figures 7 and 8, so the note's Figures 7-18 become 9-20 (tables unchanged).  Applied
before patch_bipolar_s3_5b.py inserts them.

The rules are patch_renumber_s3_5.py's, imported from it (the build's own REF_RE and exclusions, code spans left
alone, hyphen ranges in docstrings renumbered at both ends, the same files and the same three scripts excluded); only
the shift differs: figures numbered 7 and above move by two.
Usage: python patch_renumber_s3_5b.py <project root> [--apply]   (without --apply: a dry run)
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("renumber_a", HERE / "patch_renumber_s3_5.py")
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)

FIG_FROM, SHIFT = 7, 2


def shift_num(num: str, kind: str) -> str:
    m = re.fullmatch(r"(\d+)([a-z]?)", num)
    if not m or kind != "figure" or int(m.group(1)) < FIG_FROM:
        return num
    return f"{int(m.group(1)) + SHIFT}{m.group(2)}"


A.shift_num = shift_num        # renumber_line looks shift_num up in its module


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    root = Path(sys.argv[1])
    apply = "--apply" in sys.argv
    ns = A.build_regexes(root)
    note = root / "low_noise_preamp.md"
    text = note.read_text(encoding="utf-8")
    if "![Figure 7](figures/schematic_front_end_B.png)" in text:
        sys.exit("Section 3.5's Figure 7 already present: refusing to renumber")
    assert "### 3.5 Bipolar input stages" in text and "![Figure 20]" not in text
    skip = {"build_note.py", "sr560_bw_check.py", "ti_plot_check.py"}
    files = [note, root / "scripts" / "README.md"] + sorted(q for q in (root / "scripts").glob("*.py")
                                                              if q.name not in skip)
    total = 0
    for path in files:
        lines = path.read_text(encoding="utf-8").split("\n")
        new_lines, n_file = [], 0
        for i, ln in enumerate(lines):
            if path.suffix == ".md" and ln.startswith("#"):
                new_lines.append(ln)
                continue
            nl, c = A.renumber_line(ln, ns, code=path.suffix == ".py")
            if c and (path != note or "--list-note" in sys.argv):
                for ch in c:
                    print(f"{path.relative_to(root)}:{i + 1}: {ch}")
            new_lines.append(nl)
            n_file += len(c)
        if n_file:
            print(f"== {path.relative_to(root)}: {n_file} references renumbered")
            total += n_file
            if apply:
                path.write_text("\n".join(new_lines), encoding="utf-8", newline="\n")
    print(f"total {total} references{' (applied)' if apply else ' (dry run)'}")


if __name__ == "__main__":
    main()
