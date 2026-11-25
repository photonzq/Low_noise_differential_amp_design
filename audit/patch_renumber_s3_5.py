"""Renumbering for the new Section 3.5 of low_noise_preamp.md (25 November 2026): its figure becomes Figure 6 and its
table Table 5, so the note's Figures 6-17 become 7-18 and its Tables 5-15 become 6-16 (sub-tables such as 6a and
panel letters such as 14j follow their number).  Applied before the section is inserted (patch_bipolar_s3_5.py).

A reference is renumbered exactly when the build would link it (scripts/build_note.py): the build's REF_RE finds
"Figure 14", "Tables 8, 9 and 10", "Figures 12-17" and the like, and a match is a reference to another document,
left alone, when the build's EXTERNAL_BEFORE or EXTERNAL_AFTER matches the text before or after it on the line (a
possessive, "its", "their", a page number, an open citation bracket, ...).  Only whole numbers with an optional
letter are shifted: dotted numbers (Table 8.2, Section 6.2) and appendix numbers (Table A.8a) are not the note's
Figures 6-17 or Tables 5-15.  Text in code spans (`...`) is left alone: there the numbers are labels of archived
results files.  Headings carry no figure or table numbers.

Files: the note, scripts/README.md, and the comments and strings of scripts/*.py (their references to the note's
figures and tables), except build_note.py (its "Figure 12" are examples of the link syntax), sr560_bw_check.py (its
figures are the LF356's and LF411's data sheets') and ti_plot_check.py (TI's sub-numbered figures, "Figure 6-12").
In a script a reference followed by "(p." or ", p." is a data sheet's figure, and a range written with a hyphen in
a docstring ("Tables 8-15", "Figures 6-9") is renumbered at both ends.  The historical patches and reports under
audit/ are not touched.  The renumbered labels of the numbers scripts (e.g. the group "s6.2 Figure 14") take effect
when those scripts are run again.
Usage: python patch_renumber_s3_5.py <project root> [--apply]   (without --apply: a dry run that lists every change
outside the note and counts the note's)
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

FIG_FROM, TAB_FROM = 6, 5


def build_regexes(root: Path):
    """REF_RE, NUM, EXTERNAL_BEFORE and EXTERNAL_AFTER as scripts/build_note.py defines them (read from its source,
    so that the two cannot differ)."""
    src = (root / "scripts" / "build_note.py").read_text(encoding="utf-8")
    ns: dict = {"re": re}
    tag = re.search(r'^TAG = (.+)$', src, re.M)
    exec("TAG = " + tag.group(1), ns)
    for name in ("NUM", "SEP", "EQN", "REF_RE", "EXTERNAL_BEFORE", "EXTERNAL_AFTER"):
        m = re.search(rf"^{name} = (.+?)\n(?=\S)", src, re.M | re.S)
        exec(f"{name} = " + m.group(1), ns)
    return ns


def shift_num(num: str, kind: str) -> str:
    m = re.fullmatch(r"(\d+)([a-z]?)", num)
    if not m:
        return num                                  # dotted or appendix number: not one of the note's
    n = int(m.group(1))
    if kind == "figure" and n >= FIG_FROM or kind == "table" and n >= TAB_FROM:
        return f"{n + 1}{m.group(2)}"
    return num


def renumber_line(line: str, ns: dict, code: bool = False) -> tuple[str, list]:
    # protect code spans
    spans = [(m.start(), m.end()) for m in re.finditer(r"`[^`]*`", line)]
    out, pos, changes = [], 0, []
    for m in ns["REF_RE"].finditer(line):
        if not m.group("kw") or any(a <= m.start() < b for a, b in spans):
            continue
        if ns["EXTERNAL_BEFORE"].search(line[:m.start()]) or ns["EXTERNAL_AFTER"].search(line[m.end():]):
            continue
        if code and re.match(r"\s*(?:\(p\.|,\s*p\.)", line[m.end():]):
            continue                                 # in a script, "Figure 33 (p. 13)": a data sheet's figure
        kind = "figure" if m.group("kw").startswith("Figure") else "table" if m.group("kw").startswith("Table") else None
        if kind is None:
            continue
        # a range written with a hyphen in a script's docstring ("Tables 8-15"): the build's SEP knows only the en
        # dash, so the end of the range is taken here
        end = m.end("list")
        rng = re.match(r"-(\d+[a-z]?)(?![\w.])", line[end:])
        lst = m.group("list") + (rng.group(0) if rng else "")
        new_lst = re.sub(ns["NUM"], lambda mm: shift_num(mm.group(0), kind), lst)
        if new_lst != lst:
            out.append(line[pos:m.start("list")])
            out.append(new_lst)
            pos = end + (rng.end() if rng else 0)
            changes.append(f"...{line[max(0, m.start() - 50):m.start()]}[{m.group('kw')} {lst} -> {new_lst}]")
    out.append(line[pos:])
    return "".join(out), changes


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    root = Path(sys.argv[1])
    apply = "--apply" in sys.argv
    ns = build_regexes(root)
    note = root / "low_noise_preamp.md"
    text = note.read_text(encoding="utf-8")
    assert "\r" not in text
    if "### 3.5 " in text:
        sys.exit("Section 3.5 already present: refusing to renumber")
    # build_note.py's "Figure 12" are examples of its link syntax, and sr560_bw_check.py's figures are data sheets'
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
            nl, c = renumber_line(ln, ns, code=path.suffix == ".py")
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
