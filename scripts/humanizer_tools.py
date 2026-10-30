#!/usr/bin/env python3
"""Audit tooling for the humanizer pass over the manuscript (plan: quality_reports/plans/harmonic-munching-lecun.md).

The humanizer plugin rewrites plain text, not LaTeX. This script lets it work on prose only and keeps a record of
every change:

  snapshot   copy the paper sources to quality_reports/humanizer/baseline_<date>/ with a SHA-256 manifest and stats
  prepare    cut the baseline into prose units, mask LaTeX (math, citations, macros, comments, footnote bodies,
             captions) behind placeholders {{M001}}, write one masked file per unit and units.csv
  finish     unmask the plugin's output for a unit, run the gates, write the diff and update the ledger
  selftest   check that segmentation and mask/unmask reproduce the baseline byte for byte

Nothing here edits the manuscript. Hard gates (G1 placeholders, G2 numbers, G3 reference keys, G7 marker comments)
mark a unit REJECT-CANDIDATE; flag gates (G4 claim-strength words, G5 size and novelty) go to the human reviewer.

Usage
-----
    python3 scripts/humanizer_tools.py snapshot [--date YYYY-MM-DD]
    python3 scripts/humanizer_tools.py selftest [--date YYYY-MM-DD]
    python3 scripts/humanizer_tools.py prepare  [--date YYYY-MM-DD]
    python3 scripts/humanizer_tools.py finish UNIT_ID [UNIT_ID ...]
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper-real-estate"
HUM = ROOT / "quality_reports" / "humanizer"
EXTRA_SOURCES = ["results/tables/attention_macros.tex", "results/tables/attention_mc_macros.tex"]

# Environments whose bodies are never sent to the plugin (math, statements, proofs, tables).
PROTECTED_ENVS = {
    "equation", "equation*", "align", "align*", "gather", "gather*", "multline", "multline*", "eqnarray", "eqnarray*",
    "proposition", "lemma", "corollary", "definition", "assumption", "remark", "theorem", "proof",
    "tabular", "tabular*", "tabularx", "thebibliography", "verbatim", "lstlisting", "tikzpicture", "abstract_unused",
}
KEEP_WRAPPERS = {"emph", "textit", "textbf", "textsc", "textsl", "textsf"}  # braces masked, inner prose visible
MARKER = "[AUTHOR REWRITE]"
MIN_PROSE_WORDS = 8
PH = re.compile(r"\{\{(M\d+|FN\d+)\}\}")
WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*")
NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
STOP = set("a an and are as at be been but by for from has have in is it its of on or so than that the their then there "
           "these this those to was were which while with within without".split())

LEXICON = {
    "modal": r"\b(may|might|could|can|cannot|must|should|would|will)\b",
    "negation": r"\b(not|no|never|neither|nor|without|none)\b",
    "quantifier": r"\b(all|every|each|any|some|most|only|exactly|always|whenever|whatever|at least|at most|if and only if)\b",
    "hedge": r"\b(suggests?|suggested|impl(?:y|ies|ied)|consistent with|bounds?|set-identified|upper bound|lower bound|"
             r"approximately|about|roughly|likely|probably|perhaps|possibly|largely|partly|mostly|nearly|essentially)\b",
    "number_word": r"\b(one|two|three|four|five|six|seven|eight|nine|ten|half|third|tenth|twice|double|triple|several|"
                   r"few|many|majority|minority)\b",
}
LEDGER_FIELDS = ["unit_id", "file", "section", "start_line", "end_line", "kind", "words_before", "words_after",
                 "g1_placeholders", "g2_numbers", "g3_keys", "g7_markers", "g4_flags", "g5_flags", "status",
                 "change_type", "decision", "reviewer_note", "applied"]


# ------------------------------------------------------------------------------------------------- masking
@dataclass
class Masked:
    text: str
    mapping: dict[str, str] = field(default_factory=dict)
    footnotes: list[str] = field(default_factory=list)  # original bodies, index k-1 for {{FNk}}

    def add(self, original: str) -> str:
        token = "{{M%03d}}" % (len(self.mapping) + 1)
        self.mapping[token[2:-2]] = original
        return token


def match_brace(s: str, i: int) -> int:
    """Index of the } closing the { at s[i], skipping escaped braces; -1 if unbalanced."""
    depth = 0
    j = i
    while j < len(s):
        if s[j] == "\\":
            j += 2
            continue
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return j
        j += 1
    return -1


def _mask_balanced(text: str, opener: str, m: Masked, extract: bool = False) -> str:
    """Replace every `opener{...}` (balanced) by a placeholder; with extract, footnote bodies are kept as units."""
    out, i = [], 0
    while True:
        k = text.find(opener + "{", i)
        if k < 0:
            out.append(text[i:])
            break
        b = match_brace(text, k + len(opener))
        if b < 0:
            out.append(text[i:])
            break
        out.append(text[i:k])
        if extract:
            m.footnotes.append(text[k + len(opener) + 1:b])
            out.append("{{FN%d}}" % len(m.footnotes))
        else:
            out.append(m.add(text[k:b + 1]))
        i = b + 1
    return "".join(out)


def _mask_commands(s: str, m: Masked) -> str:
    """Mask LaTeX commands, escapes and ties; wrappers like \\emph keep their inner text visible."""
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == "~":
            out.append(m.add("~"))
            i += 1
            continue
        if c != "\\":
            out.append(c)
            i += 1
            continue
        name = re.match(r"\\([A-Za-z@]+)\*?", s[i:])
        if name:
            j = i + name.end()
            if name.group(1) in KEEP_WRAPPERS and j < len(s) and s[j] == "{":
                k = match_brace(s, j)
                if k > 0:
                    out.append(m.add(s[i:j + 1]) + _mask_commands(s[j + 1:k], m) + m.add("}"))
                    i = k + 1
                    continue
            end = j
            while end < len(s) and s[end] in "[{":
                if s[end] == "[":
                    e = s.find("]", end)
                    if e < 0:
                        break
                    end = e + 1
                else:
                    e = match_brace(s, end)
                    if e < 0:
                        break
                    end = e + 1
            out.append(m.add(s[i:end]))
            i = end
            continue
        nxt = s[i + 1:i + 2]
        if nxt == "\\":
            e = re.match(r"\\\\(\[[^\]]*\])?", s[i:])
            out.append(m.add(e.group(0)))
            i += e.end()
        elif nxt and nxt in "'\"`^~=.":
            e = re.match(r"\\['\"`^~=.](\{[A-Za-z]\}|[A-Za-z])?", s[i:])
            out.append(m.add(e.group(0)))
            i += e.end()
        else:
            out.append(m.add(s[i:i + 2]))
            i += 2
    return "".join(out)


def mask(text: str) -> Masked:
    """Mask protected LaTeX in one block of prose; unmask(mask(t)) == t for every t."""
    m = Masked(text)
    t = _mask_balanced(text, r"\footnote", m, extract=True)                       # footnote bodies become own units (raw text)
    t = re.sub(r"(?<!\\)%[^\n]*", lambda x: m.add(x.group(0)), t)               # comments
    t = _mask_balanced(t, r"\caption", m)                                         # captions are titles: protected
    for pat in (r"\\\[.*?\\\]", r"\$\$.*?\$\$", r"\\\(.*?\\\)", r"(?<!\\)\$.*?(?<!\\)\$"):
        t = re.sub(pat, lambda x: m.add(x.group(0)), t, flags=re.S)               # math
    t = _mask_commands(t, m)
    t = re.sub(r"(?m)^[ \t]*[{}][ \t]*$", lambda x: m.add(x.group(0)), t)         # lone braces (e.g. \abs{ ... })
    m.text = t
    return m


def unmask(masked: str, m: Masked, footnote_bodies: list[str] | None = None) -> str:
    """Put the original spans back; footnote bodies default to the baseline text."""
    bodies = footnote_bodies if footnote_bodies is not None else m.footnotes

    def back(x: re.Match) -> str:
        key = x.group(1)
        if key.startswith("FN"):
            return "\\footnote{" + bodies[int(key[2:]) - 1] + "}"
        return m.mapping[key]

    out = masked
    for _ in range(20):                       # masked spans may contain other placeholders (math inside a title)
        new = PH.sub(back, out)
        if new == out:
            break
        out = new
    return out


# ------------------------------------------------------------------------------------------- segmentation
@dataclass
class Piece:
    kind: str    # gap | prose | marker
    text: str
    start: int   # 1-based first line
    end: int


def segment(tex: str) -> list[Piece]:
    """Split a file into alternating gaps (kept untouched) and paragraph blocks of unprotected prose."""
    lines = tex.splitlines(keepends=True)
    protected, stack, in_display = [], [], False
    for ln in lines:
        body = re.sub(r"(?<!\\)%.*", "", ln)
        for mo in re.finditer(r"\\(begin|end)\{([^}]+)\}", body):
            if mo.group(2) in PROTECTED_ENVS:
                stack.append(mo.group(2)) if mo.group(1) == "begin" else (stack.pop() if stack else None)
        if re.search(r"\\\[", body) and not re.search(r"\\\]", body):
            in_display = True
        is_prot = bool(stack) or in_display or bool(re.search(r"\\(begin|end)\{(" + "|".join(
            re.escape(e) for e in PROTECTED_ENVS) + r")\}", body))
        if in_display and re.search(r"\\\]", body):
            in_display = False
        protected.append(is_prot)
    pieces: list[Piece] = []
    i, n = 0, len(lines)
    marker_pending = False
    while i < n:
        if protected[i] or not lines[i].strip():
            j = i
            while j < n and (protected[j] or not lines[j].strip()):
                j += 1
            pieces.append(Piece("gap", "".join(lines[i:j]), i + 1, j))
            i = j
            continue
        j = i
        while j < n and not protected[j] and lines[j].strip():
            j += 1
        block = "".join(lines[i:j])
        comment_only = all(l.lstrip().startswith("%") for l in lines[i:j])
        has_marker = MARKER in block
        kind = "marker" if (has_marker or marker_pending) else "prose"
        marker_pending = comment_only and has_marker
        pieces.append(Piece(kind, block, i + 1, j))
        i = j
    return pieces


def section_of(rel: str, line: int, lines: list[str]) -> str:
    """Section key for reporting: file stem, or a part of main.tex located by its \\section anchors."""
    if rel != "main.tex":
        return Path(rel).stem
    def at(pat: str) -> int:
        return next((k + 1 for k, l in enumerate(lines) if re.search(pat, l)), 10 ** 9)
    abs_end, pol, concl, appx = at(r"^\\section\{Policy"), at(r"^\\section\{Policy"), at(r"^\\section\{Conclusion"), at(r"^\\input\{sections/A-robustness")
    if line < at(r"\\input\{sections/01"):
        return "main-abstract"
    if pol <= line < concl:
        return "main-policy"
    if concl <= line < appx:
        return "main-conclusion"
    return "main-appendix" if line >= appx else "main-other"


def words(text: str) -> list[str]:
    return WORD.findall(PH.sub(" ", text))


# ------------------------------------------------------------------------------------------------ gates
def lexicon_counts(text: str) -> dict[str, Counter]:
    plain = PH.sub(" ", text).lower()
    return {k: Counter(x if isinstance(x, str) else x[0] for x in re.findall(p, plain)) for k, p in LEXICON.items()}


def verify(before: str, after: str, m: Masked) -> dict:
    """Run the gates on masked before/after text. Hard failures make the unit a REJECT-CANDIDATE."""
    ph_b, ph_a = PH.findall(before), PH.findall(after)
    g1 = Counter(ph_b) == Counter(ph_a)
    order_changed = g1 and ph_b != ph_a
    strip = lambda s: NUMBER.findall(PH.sub(" ", s))
    g2 = Counter(strip(before)) == Counter(strip(after))
    keys = lambda s: sorted(re.findall(r"\\(?:ref|eqref|cite\w*|label)(?:\[[^\]]*\])*\{([^}]*)\}", unmask(s, m)))
    g3 = keys(before) == keys(after) if g1 else False
    cnt = lambda s, tag: unmask(s, m).count(tag)
    g7 = all(cnt(before, t) == cnt(after, t) for t in (MARKER, "% [CHECK]"))
    flags4 = []
    lb, la = lexicon_counts(before), lexicon_counts(after)
    for kind in LEXICON:
        for term in sorted(set(lb[kind]) | set(la[kind])):
            if lb[kind][term] != la[kind][term]:
                flags4.append(f"{kind}:{term} {lb[kind][term]}->{la[kind][term]}")
    dash = (before.count("---"), before.count("--"), after.count("---"), after.count("--"))
    if dash[0] != dash[2] or dash[1] != dash[3]:
        flags4.append(f"dashes --- {dash[0]}->{dash[2]}, -- {dash[1]}->{dash[3]}")
    wb, wa = words(before), words(after)
    sb = max(1, len(re.findall(r"[.?!](?:\s|$)", PH.sub(" ", before))))
    sa = max(1, len(re.findall(r"[.?!](?:\s|$)", PH.sub(" ", after))))
    new = sorted({w.lower() for w in wa} - {w.lower() for w in wb} - STOP)
    flags5 = []
    if len(wa) < 0.75 * len(wb):
        flags5.append(f"shrink {len(wb)}->{len(wa)} words")
    if len(wa) > 1.25 * len(wb):
        flags5.append(f"growth {len(wb)}->{len(wa)} words")
    if sa != sb:
        flags5.append(f"sentences {sb}->{sa}")
    if order_changed:
        flags5.append("placeholder order changed")
    if re.search(r"\n\s*\n", after.strip()):
        flags5.append("paragraph split")
    if new:
        flags5.append("new words: " + ", ".join(new[:15]) + (" …" if len(new) > 15 else ""))
    return dict(g1=g1, g2=g2, g3=g3, g7=g7, flags4=flags4, flags5=flags5, words_before=len(wb), words_after=len(wa),
                hard_pass=g1 and g2 and g3 and g7)


# --------------------------------------------------------------------------------------------- commands
def baseline_dir(date: str) -> Path:
    return HUM / f"baseline_{date}"


def source_files() -> list[str]:
    return ["main.tex"] + sorted(str(p.relative_to(PAPER)) for p in (PAPER / "sections").glob("*.tex"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cmd_snapshot(date: str) -> None:
    base = baseline_dir(date)
    if base.exists():
        sys.exit(f"{base} already exists: a baseline is never overwritten")
    (base / "paper-real-estate" / "sections").mkdir(parents=True)
    (base / "results" / "tables").mkdir(parents=True)
    manifest, stats = [], {"words": {}, "macro_use": {}, "labels": {}, "cites": {}, "refs": {}}
    for rel in source_files():
        shutil.copy2(PAPER / rel, base / "paper-real-estate" / rel)
    for rel in EXTRA_SOURCES:
        shutil.copy2(ROOT / rel, base / rel)
    for f in sorted(p for p in base.rglob("*") if p.is_file()):
        manifest.append(f"{sha(f)}  {f.relative_to(base)}")
    for rel in source_files():
        t = (PAPER / rel).read_text()
        stats["words"][rel] = len(t.split())
        stats["macro_use"][rel] = dict(Counter(re.findall(r"\\(att[A-Za-z]+)\{\}", t)))
        stats["labels"][rel] = sorted(re.findall(r"\\label\{([^}]*)\}", t))
        stats["cites"][rel] = sorted(re.findall(r"\\cite\w*(?:\[[^\]]*\])*\{([^}]*)\}", t))
        stats["refs"][rel] = sorted(re.findall(r"\\(?:ref|eqref)\{([^}]*)\}", t))
    pdf = PAPER / "main.pdf"
    if pdf.exists():
        (base / "baseline_text").mkdir()
        txt = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
        (base / "baseline_text" / "main.txt").write_text(txt)
        info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
        stats["pages"] = int(next((l.split()[1] for l in info.splitlines() if l.startswith("Pages:")), 0))
    (base / "MANIFEST.sha256").write_text("\n".join(manifest) + "\n")
    (base / "baseline_stats.json").write_text(json.dumps(stats, indent=1, sort_keys=True))
    print(f"snapshot written to {base} ({len(manifest)} files, {stats.get('pages', '?')} pages)")


def load_units(base: Path) -> list[dict]:
    """All prose units of the baseline: dicts with masked text and mapping (footnotes become child units)."""
    units = []
    for rel in source_files():
        tex = (base / "paper-real-estate" / rel).read_text()
        flines = tex.splitlines()
        for p in segment(tex):
            if p.kind == "gap":
                continue
            m = mask(p.text)
            sec = section_of(rel, p.start, flines)
            uid = f"{Path(rel).stem}:L{p.start}-{p.end}"
            n_words = len(words(m.text))
            units.append(dict(unit_id=uid, file=rel, section=sec, start=p.start, end=p.end, kind=p.kind, words=n_words,
                              eligible=p.kind == "prose" and n_words >= MIN_PROSE_WORDS, masked=m.text, m=m,
                              original=p.text))
            for k, body in enumerate(m.footnotes, 1):
                fm = mask(body)
                fw = len(words(fm.text))
                units.append(dict(unit_id=f"{uid}#fn{k}", file=rel, section=sec, start=p.start, end=p.end,
                                  kind="footnote" if p.kind == "prose" else "marker", words=fw,
                                  eligible=p.kind == "prose" and fw >= MIN_PROSE_WORDS, masked=fm.text, m=fm,
                                  original=body))
    return units


def cmd_selftest(date: str) -> None:
    base = baseline_dir(date)
    bad = 0
    for rel in source_files():
        tex = (base / "paper-real-estate" / rel).read_text()
        if "".join(p.text for p in segment(tex)) != tex:
            print(f"SEGMENT ROUND-TRIP FAILED: {rel}")
            bad += 1
    units = load_units(base)
    for u in units:
        if unmask(u["masked"], u["m"]) != (u["original"] if "#fn" not in u["unit_id"] else u["original"]):
            # parent units contain {{FNk}} placeholders resolved by unmask with baseline bodies
            print(f"MASK ROUND-TRIP FAILED: {u['unit_id']}")
            bad += 1
    el = [u for u in units if u["eligible"]]
    print(f"{len(units)} blocks, {len(el)} eligible prose units "
          f"({sum(u['words'] for u in el)} words), {sum(1 for u in units if u['kind'] == 'marker')} protected by marker; "
          f"round-trip failures: {bad}")
    sys.exit(1 if bad else 0)


def cmd_prepare(date: str) -> None:
    base = baseline_dir(date)
    units = load_units(base)
    HUM.mkdir(parents=True, exist_ok=True)
    rows = []
    for u in units:
        safe = re.sub(r"[^A-Za-z0-9_.-]", "_", u["unit_id"])
        d = HUM / "runs" / u["section"]
        d.mkdir(parents=True, exist_ok=True)
        if u["eligible"]:
            (d / f"{safe}.before.tex").write_text(u["original"])
            (d / f"{safe}.masked.txt").write_text(u["masked"])
            (d / f"{safe}.map.json").write_text(json.dumps({"mapping": u["m"].mapping, "footnotes": u["m"].footnotes}))
        rows.append(dict(unit_id=u["unit_id"], file=u["file"], section=u["section"], start_line=u["start"],
                         end_line=u["end"], kind=u["kind"], words=u["words"], eligible=u["eligible"],
                         placeholders=len(u["m"].mapping), sha8=hashlib.sha256(u["original"].encode()).hexdigest()[:8]))
    with (HUM / "units.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    by = Counter(r["section"] for r in rows if r["eligible"])
    print(f"{len(rows)} blocks, {sum(by.values())} eligible; per section:", dict(by))


def update_ledger(row: dict) -> None:
    path = HUM / "ledger.csv"
    rows = list(csv.DictReader(path.open())) if path.exists() else []
    rows = [r for r in rows if r["unit_id"] != row["unit_id"]] + [{k: row.get(k, "") for k in LEDGER_FIELDS}]
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: (r["file"], int(r["start_line"] or 0), r["unit_id"])))


def cmd_finish(unit_ids: list[str]) -> None:
    for uid in unit_ids:
        safe = re.sub(r"[^A-Za-z0-9_.-]", "_", uid)
        hits = list((HUM / "runs").glob(f"*/{safe}.masked.txt"))
        if len(hits) != 1:
            sys.exit(f"{uid}: expected one prepared unit, found {len(hits)}")
        d = hits[0].parent
        meta = json.loads((d / f"{safe}.map.json").read_text())
        m = Masked("", meta["mapping"], meta["footnotes"])
        before = hits[0].read_text()
        after_path = d / f"{safe}.after.masked.txt"
        if not after_path.exists():
            sys.exit(f"{uid}: write the plugin output to {after_path.name} first")
        after = after_path.read_text().rstrip("\n") if not before.endswith("\n") else after_path.read_text()
        res = verify(before, after, m)
        after_tex = unmask(after, m)
        (d / f"{safe}.after.tex").write_text(after_tex)
        orig = (d / f"{safe}.before.tex").read_text()
        diff = "".join(difflib.unified_diff(orig.splitlines(True), after_tex.splitlines(True), "before", "after", n=2))
        (d / f"{safe}.diff").write_text(diff)
        rows = list(csv.DictReader((HUM / "units.csv").open()))
        u = next(r for r in rows if r["unit_id"] == uid)
        status = "UNCHANGED" if orig == after_tex else ("REJECT-CANDIDATE" if not res["hard_pass"] else
                 ("REVIEW-FLAGS" if res["flags4"] or res["flags5"] else "CLEAN"))
        update_ledger(dict(unit_id=uid, file=u["file"], section=u["section"], start_line=u["start_line"],
                           end_line=u["end_line"], kind=u["kind"], words_before=res["words_before"],
                           words_after=res["words_after"], g1_placeholders=res["g1"], g2_numbers=res["g2"],
                           g3_keys=res["g3"], g7_markers=res["g7"], g4_flags="; ".join(res["flags4"]),
                           g5_flags="; ".join(res["flags5"]), status=status, decision="pending", applied="n"))
        print(f"{uid}: {status}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["snapshot", "selftest", "prepare", "finish"])
    ap.add_argument("units", nargs="*")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    a = ap.parse_args()
    {"snapshot": lambda: cmd_snapshot(a.date), "selftest": lambda: cmd_selftest(a.date),
     "prepare": lambda: cmd_prepare(a.date), "finish": lambda: cmd_finish(a.units)}[a.command]()


if __name__ == "__main__":
    main()
