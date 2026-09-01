#!/usr/bin/env python3
"""
parser.py — embedded-claims PoC, phase 2 step 3b (hardened after Codex review).

Pinned CommonMark (markdown-it-py==4.2.0, preset "commonmark", no plugins) for block
AND inline structure, plus a strict PROTOCOL PROFILE over raw source spans for what
CommonMark cannot express (exact opener/closer, exact region markers). PARSE only:
regions, claims, capsules, byte spans, typed errors, and a report-level status. It does
NOT validate schema, settle, or associate — that is the 3c compiler.

Hardening (Codex):
  P0  parser_id binds the ACTUAL installed bytes of markdown_it AND mdurl (both
      versions checked), not just this file + the declared lock.
  P0  report-level `status` (VALID | INVALID | INERT); any fatal parse error makes the
      whole report INVALID (candidates kept for diagnostics, never for compile).
  P0  region references are STABLE ids into `regions`, correct even when an
      unusable (unknown-profile) region precedes a usable one.
  P1  claims come from CommonMark TEXT nodes only — inline code / inline HTML / fenced
      content are inert; an unmatched `⟦` is MALFORMED_CLAIM_OPEN, an unmatched `⟧` is
      UNSUPPORTED_INLINE_DELIMITER.
  P1  exact region markers (single ASCII spaces), exact closing-fence rule, and
      UNCLOSED_FENCE only for openers active inside an opened region span.
  P1  claims and capsules carry raw byte spans; capsule body is the raw source slice,
      not markdown-it's normalized token.content.
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
CLAIM = re.compile(r"⟦([a-z0-9_]+):\s*([^⟧]+)⟧(?:\{#([A-Za-z0-9_-]{1,64})\})?")

FATAL = {"UNKNOWN_PROFILE", "UNEXPECTED_END", "NESTED_OR_DUP_BEGIN", "MISSING_END",
         "UNCLOSED_FENCE", "UNSUPPORTED_INLINE_DELIMITER", "MALFORMED_CLAIM_OPEN"}
PINNED = {"markdown-it-py": "4.2.0", "mdurl": "0.1.2"}


def _pkg_digest(mod):
    """Path-independent digest of a package's installed .py bytes: (relpath, sha256)
    pairs sorted by relpath, so two installs of the same code agree and a modified
    same-version install does not."""
    base = os.path.dirname(os.path.abspath(mod.__file__))
    entries = []
    for root, _dirs, files in os.walk(base):
        for fn in sorted(files):
            if fn.endswith(".py"):
                p = os.path.join(root, fn)
                with open(p, "rb") as f:
                    entries.append((os.path.relpath(p, base).replace(os.sep, "/"),
                                    hashlib.sha256(f.read()).hexdigest()))
    entries.sort()
    return hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()


def parser_id():
    """Identity of the PARSE layer over its ACTUAL runtime: parser.py + the lock +
    the installed bytes and versions of markdown_it and mdurl. A drifting or
    tampered dependency rotates the id or fails loudly."""
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
    """Byte offset of the start of each line (UTF-8)."""
    offs, off = [], 0
    for ln in text.split("\n"):
        offs.append(off)
        off += len(ln.encode("utf-8")) + 1        # + newline
    return offs


def parse(text):
    lines = text.split("\n")
    offs = _line_offsets(text)
    md = MarkdownIt("commonmark")
    tokens = md.parse(text)

    errors = []
    fences = []            # (start_line, closed, raw_opener, content_lines)
    markers = []           # (kind, l0, l1, profile) top-level region markers

    depth = 0
    for t in tokens:
        if t.nesting == 1:
            depth += 1
            continue
        if t.nesting == -1:
            depth -= 1
            continue
        if t.type in ("fence", "code_block") and t.map:
            a, b = t.map
            if t.type == "fence":
                closed = (b - 1 < len(lines)) and bool(CLOSER.match(lines[b - 1]))
                fences.append((a, closed))
        if t.type == "html_block" and depth == 0 and t.map:
            raw = lines[t.map[0]]
            mb, me = BEGIN.match(raw), END.match(raw)
            if mb:
                markers.append(("begin", t.map[0], t.map[1], mb.group(1)))
            elif me:
                markers.append(("end", t.map[0], t.map[1], None))

    # --- regions: balanced, non-nested, STABLE ids into `regions` ---------------
    regions = []           # {id, profile, content_start, content_end, usable}
    spans = []             # (begin_content_start, end_line_or_EOF) — for UNCLOSED_FENCE
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

    # --- capsules: exact-opener fences ------------------------------------------
    capsules = []
    for start, closed in fences:
        if lines[start] != OPENER:                # exact raw opener (protocol profile)
            continue
        if not closed:
            if in_opened_span(start):             # only inside an opened region span
                errors.append({"code": "UNCLOSED_FENCE", "line": start,
                               "detail": "capsule fence never closed"})
            continue
        rid = region_id_at(start)
        if rid is None:
            continue                              # closed capsule outside a live region ⇒ inert
        # body = raw source slice between opener line and closer line (not token.content)
        body_start_line, body_end_line = start + 1, _closer_line(lines, start)
        b0 = offs[body_start_line]
        b1 = offs[body_end_line] - 1 if body_end_line < len(offs) else len(text.encode("utf-8"))
        body_raw = text.encode("utf-8")[b0:b1].decode("utf-8")
        capsules.append({"region": rid, "line": start, "closed": True,
                         "span": [b0, b1], "body_raw": body_raw})

    # --- claims: CommonMark TEXT nodes only, inside usable regions ---------------
    claims = []
    for t in tokens:
        if t.type != "inline" or not t.map:
            continue
        rid = region_id_at(t.map[0])
        if rid is None:
            continue
        text_only = "".join(c.content for c in (t.children or []) if c.type == "text")
        matched = list(CLAIM.finditer(text_only))
        # locate each match's raw byte span within the block's source lines
        block_raw = "\n".join(lines[t.map[0]:t.map[1]])
        block_b0 = offs[t.map[0]]
        cursor = 0
        for m in matched:
            pos = block_raw.find(m.group(0), cursor)
            if pos < 0:
                span = None
            else:
                cursor = pos + len(m.group(0))
                s = block_b0 + len(block_raw[:pos].encode("utf-8"))
                span = [s, s + len(m.group(0).encode("utf-8"))]
            claims.append({"class": m.group(1), "payload": m.group(2).strip(),
                           "local_id": m.group(3), "region": rid,
                           "line": t.map[0], "span": span})
        # stray delimiters, counted over TEXT nodes only
        if text_only.count("⟧") > len(matched):
            errors.append({"code": "UNSUPPORTED_INLINE_DELIMITER", "line": t.map[0],
                           "detail": "a ⟧ appears outside a well-formed claim "
                                     "(v0: carry such text in a capsule)"})
        if text_only.count("⟦") > len(matched):
            errors.append({"code": "MALFORMED_CLAIM_OPEN", "line": t.map[0],
                           "detail": "an unclosed ⟦ (opening glyph with no ⟧)"})

    usable_regions = [r for r in regions if r["usable"]]
    if not usable_regions and not errors:
        errors.append({"code": "NO_LIVE_REGION", "line": 0,
                       "detail": "document declares no live region"})

    codes = {e["code"] for e in errors}
    if codes & FATAL:
        status = "INVALID"
    elif usable_regions:
        status = "VALID"
    else:
        status = "INERT"

    return {"parser": parser_id(), "status": status,
            "regions": [{"id": r["id"], "profile": r["profile"],
                         "content_start": r["content_start"],
                         "content_end": r["content_end"], "usable": r["usable"]}
                        for r in regions],
            "claims": claims, "capsules": capsules, "errors": errors}


def _closer_line(lines, opener_line):
    """First valid closing-fence line after `opener_line` (or EOF)."""
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
    with open(sys.argv[1], encoding="utf-8") as f:
        rep = parse(f.read())
    print(f"status={rep['status']} regions={len(rep['regions'])} "
          f"claims={len(rep['claims'])} capsules={len(rep['capsules'])} "
          f"errors={_codes(rep)}")
    print(json.dumps(rep, ensure_ascii=False, sort_keys=True))
