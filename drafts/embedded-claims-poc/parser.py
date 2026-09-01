#!/usr/bin/env python3
"""
parser.py — embedded-claims PoC, phase 2 step 3b (capsule-only, after the pivot).

PIVOT (operator + Codex): the canonical pipeline no longer scans prose for inline
`⟦…⟧` claims. Prose stays prose — metaphor, philosophy, speculation. Machine credit is
granted ONLY to an explicit fenced `json capsule` inside a live region; the capsule
itself carries the claim (class, payload, plan, dependency, binding). This deletes a
whole class of ambiguity — inline-code/HTML, `⟧` escaping, claim↔capsule association,
`{#local_id}` grammar, multiple-inline parsing — and the temptation to guess what a
rhetorical sentence "really asserted". The old inline `settle_gate` form and the SSD
demos remain as LEGACY authoring, not auto-migrated into this pipeline.

What this parser does (PARSE only): find live regions and the explicit capsules inside
them, with raw byte spans and a report-level fail-closed status. It does NOT validate
capsule schema or settle anything — that is the 3c compiler.

Retained from the hardening review (still load-bearing):
  - parser_id binds the ACTUAL installed bytes+versions of markdown_it and mdurl;
  - exact ASCII region markers; exact capsule opener and closing-fence rule;
  - CommonMark block structure, so a capsule inside an outer fence is inert;
  - raw byte span + raw source-slice body for each capsule (the source occurrence);
  - report-level status VALID | INVALID | INERT (compiler precondition: VALID).
"""
import hashlib
import json
import os
import re

from markdown_it import MarkdownIt
import markdown_it
import mdurl

HERE = os.path.dirname(os.path.abspath(__file__))
LOCK = os.path.join(HERE, "requirements-parser.lock")

PROFILE = "manifesto.embedded-claims.v0"
OPENER = "```json capsule"                 # the exact raw opener line (protocol profile)
BEGIN = re.compile(r"^<!-- manifesto-claims:begin profile=(\S+) -->$")   # exact ASCII
END = re.compile(r"^<!-- manifesto-claims:end -->$")
CLOSER = re.compile(r"^ {0,3}`{3,}[ \t]*$")   # a valid CommonMark closing fence

FATAL = {"UNKNOWN_PROFILE", "UNEXPECTED_END", "NESTED_OR_DUP_BEGIN", "MISSING_END",
         "UNCLOSED_FENCE", "UNSUPPORTED_LINE_ENDING"}
PINNED = {"markdown-it-py": "4.2.0", "mdurl": "0.1.2"}


def _pkg_digest(mod):
    """Path-independent digest of a package's installed .py bytes."""
    base = os.path.dirname(os.path.abspath(mod.__file__))
    entries = []
    for root, _dirs, files in os.walk(base):
        for fn in sorted(files):
            if fn.endswith(".py"):
                with open(os.path.join(root, fn), "rb") as f:
                    entries.append((os.path.relpath(os.path.join(root, fn), base)
                                    .replace(os.sep, "/"),
                                    hashlib.sha256(f.read()).hexdigest()))
    entries.sort()
    return hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()


def parser_id():
    if markdown_it.__version__ != PINNED["markdown-it-py"]:
        raise RuntimeError(f"pinned markdown-it-py=={PINNED['markdown-it-py']}, "
                           f"found {markdown_it.__version__}")
    if mdurl.__version__ != PINNED["mdurl"]:
        raise RuntimeError(f"pinned mdurl=={PINNED['mdurl']}, found {mdurl.__version__}")
    m = hashlib.sha256()
    for p in (os.path.abspath(__file__), LOCK):
        with open(p, "rb") as f:
            m.update(hashlib.sha256(f.read()).digest())
    m.update(_pkg_digest(markdown_it).encode())
    m.update(_pkg_digest(mdurl).encode())
    return "parser://sha256:" + m.hexdigest()


def _line_offsets(text):
    offs, off = [], 0
    for ln in text.split("\n"):
        offs.append(off)
        off += len(ln.encode("utf-8")) + 1
    return offs


def _line_ending_error(text):
    """Uniform LF or uniform CRLF are fine. A lone CR (old-Mac) or a mix of LF and
    CRLF is a typed failure — line endings must not silently change what the protocol
    sees (Codex): a CRLF document must not vanish into NO_LIVE_REGION."""
    total_nl = text.count("\n")
    crlf = text.count("\r\n")
    lone_cr = text.count("\r") - crlf
    if lone_cr > 0:
        return "lone CR (\\r not part of CRLF)"
    if crlf and crlf != total_nl:
        return "mixed LF and CRLF line endings"
    return None


def parse(text):
    le_err = _line_ending_error(text)
    if le_err:
        return {"parser": parser_id(), "status": "INVALID", "regions": [],
                "capsules": [],
                "errors": [{"code": "UNSUPPORTED_LINE_ENDING", "line": 0,
                            "detail": le_err}]}
    raw_lines = text.split("\n")
    # structural lines drop a single trailing CR (CRLF); byte offsets stay over the
    # ORIGINAL bytes, so spans are faithful regardless of line ending.
    lines = [ln[:-1] if ln.endswith("\r") else ln for ln in raw_lines]
    offs = _line_offsets(text)
    tokens = MarkdownIt("commonmark").parse(text)

    errors = []
    fences = []            # (start_line, closed)
    markers = []           # (kind, l0, l1, profile) — top-level region markers only

    depth = 0
    for t in tokens:
        if t.nesting == 1:
            depth += 1
            continue
        if t.nesting == -1:
            depth -= 1
            continue
        if t.type == "fence" and t.map:
            a, b = t.map
            closed = (b - 1 < len(lines)) and bool(CLOSER.match(lines[b - 1]))
            fences.append((a, closed))
        if t.type == "html_block" and depth == 0 and t.map:
            raw = lines[t.map[0]]
            mb, me = BEGIN.match(raw), END.match(raw)
            if mb:
                markers.append(("begin", t.map[0], t.map[1], mb.group(1)))
            elif me:
                markers.append(("end", t.map[0], t.map[1], None))

    regions = []           # {id, profile, content_start, content_end, usable}
    spans = []             # (content_start, end_or_EOF) for UNCLOSED_FENCE scoping
    open_reg = None
    for kind, l0, l1, profile in markers:
        if kind == "begin":
            if open_reg is not None:
                errors.append({"code": "NESTED_OR_DUP_BEGIN", "line": l0,
                               "detail": "begin while a region is already open"})
                continue
            usable = (profile == PROFILE)
            if not usable:
                errors.append({"code": "UNKNOWN_PROFILE", "line": l0,
                               "detail": f"profile {profile!r} not implemented"})
            open_reg = {"id": len(regions), "profile": profile,
                        "content_start": l1, "content_end": None, "usable": usable}
        else:
            if open_reg is None:
                errors.append({"code": "UNEXPECTED_END", "line": l0,
                               "detail": "end with no open region"})
                continue
            open_reg["content_end"] = l0
            spans.append((open_reg["content_start"], l0))
            regions.append(open_reg)
            open_reg = None
    if open_reg is not None:
        errors.append({"code": "MISSING_END", "line": open_reg["content_start"],
                       "detail": "region opened but never closed"})
        spans.append((open_reg["content_start"], len(lines)))
        open_reg["content_end"] = len(lines)
        regions.append(open_reg)

    def region_id_at(line):
        for r in regions:
            if r["usable"] and r["content_start"] <= line < r["content_end"]:
                return r["id"]
        return None

    def in_opened_span(line):
        return any(a <= line < b for a, b in spans)

    capsules = []
    for start, closed in fences:
        if lines[start] != OPENER:                # exact raw opener (protocol profile)
            continue
        if not closed:
            if in_opened_span(start):
                errors.append({"code": "UNCLOSED_FENCE", "line": start,
                               "detail": "capsule fence never closed"})
            continue
        rid = region_id_at(start)
        if rid is None:
            continue                              # closed capsule outside a live region ⇒ inert
        body_end_line = _closer_line(lines, start)
        b0 = offs[start + 1]
        b1 = offs[body_end_line] - 1 if body_end_line < len(offs) else len(text.encode("utf-8"))
        body_raw = text.encode("utf-8")[b0:b1].decode("utf-8")
        capsules.append({"region": rid, "line": start, "closed": True,
                         "span": [b0, b1], "body_raw": body_raw})

    usable_regions = [r for r in regions if r["usable"]]
    if not usable_regions and not errors:
        errors.append({"code": "NO_LIVE_REGION", "line": 0,
                       "detail": "document declares no live region"})

    codes = {e["code"] for e in errors}
    status = "INVALID" if (codes & FATAL) else ("VALID" if usable_regions else "INERT")

    return {"parser": parser_id(), "status": status,
            "regions": [{"id": r["id"], "profile": r["profile"],
                         "content_start": r["content_start"],
                         "content_end": r["content_end"], "usable": r["usable"]}
                        for r in regions],
            "capsules": capsules, "errors": errors}


def _closer_line(lines, opener_line):
    for i in range(opener_line + 1, len(lines)):
        if CLOSER.match(lines[i]):
            return i
    return len(lines)


def _codes(report):
    return sorted({e["code"] for e in report["errors"]})


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("usage: parser.py <file.md>", file=sys.stderr)
        sys.exit(2)
    with open(sys.argv[1], "rb") as f:          # raw bytes, not universal-newline text
        rep = parse(f.read().decode("utf-8"))
    print(f"status={rep['status']} regions={len(rep['regions'])} "
          f"capsules={len(rep['capsules'])} errors={_codes(rep)}")
    print(json.dumps(rep, ensure_ascii=False, sort_keys=True))
