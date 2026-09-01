#!/usr/bin/env python3
"""
parser.py — embedded-claims PoC, phase 2 step 3b: the PARSE layer.

Pinned CommonMark (markdown-it-py==4.2.0, preset "commonmark", no plugins) for
block structure / nesting / inertness, plus a strict PROTOCOL PROFILE over the raw
source spans for the things CommonMark cannot express (exact opener spelling,
explicit closing fence, live regions). Returns a typed ParseReport and NOTHING it
cannot structurally justify.

SCOPE (Codex 3b boundary): PARSE only. This finds regions, claims, capsules, raw
spans, and PARSE errors. It does NOT validate capsule schema, settle claims, or do
claim↔capsule association — DANGLING_CLAIM_REF / DUPLICATE_CLAIM_REF are the 3c
compiler's job. So specimens 09/15/16 are STRUCTURALLY parsed here, not fully judged;
this module never claims "01–17 fully pass".

Live demarcation (decided §8.1): claims/capsules are recognized only inside an
explicit `manifesto-claims:begin/end` region; a marker inside a fence or blockquote is
inert; no region ⇒ NO_LIVE_REGION.

Deterministic: same bytes + same pinned parser ⇒ same ParseReport.
"""
import hashlib
import os
import re

from markdown_it import MarkdownIt
import markdown_it

HERE = os.path.dirname(os.path.abspath(__file__))
LOCK = os.path.join(HERE, "requirements-parser.lock")

PROFILE = "manifesto.embedded-claims.v0"
OPENER = "```json capsule"                 # the exact raw opener (protocol profile)
BEGIN = re.compile(r"^<!--\s*manifesto-claims:begin\s+profile=(\S+)\s*-->\s*$")
END = re.compile(r"^<!--\s*manifesto-claims:end\s*-->\s*$")
# inline claim: ⟦class: payload⟧ optionally followed by {#local_id}
CLAIM = re.compile(r"⟦([a-z0-9_]+):\s*([^⟧]+)⟧(?:\{#([A-Za-z0-9_-]{1,64})\})?")


def parser_id():
    """Identity closure of the PARSE layer: parser.py + the pinned lock (which fixes
    the markdown-it-py/mdurl wheel hashes). Changing either rotates the id — the same
    discipline as the evaluator closure. The installed version is checked against 4.2.0
    so a drifting environment fails loudly rather than silently reparsing differently."""
    if markdown_it.__version__ != "4.2.0":
        raise RuntimeError(f"pinned markdown-it-py==4.2.0, found {markdown_it.__version__}")
    m = hashlib.sha256()
    for p in (os.path.abspath(__file__), LOCK):
        with open(p, "rb") as f:
            m.update(hashlib.sha256(f.read()).digest())
    return "parser://sha256:" + m.hexdigest()


def _md():
    return MarkdownIt("commonmark")


def parse(text):
    """Return a ParseReport dict:
      { parser, regions, claims, capsules, errors }
    where errors carry typed codes (NO_LIVE_REGION, UNKNOWN_PROFILE, UNEXPECTED_END,
    NESTED_OR_DUP_BEGIN, MISSING_END, UNCLOSED_FENCE, UNSUPPORTED_INLINE_DELIMITER)."""
    lines = text.split("\n")
    tokens = _md().parse(text)

    errors = []
    inert = set()          # line indices inside any fence/code block (claims inert here)
    fences = []            # (start_line, closed, info) for top-level fences
    markers = []           # (kind, line, profile) top-level region markers, in order

    depth = 0
    for t in tokens:
        if t.nesting == 1:
            depth += 1
            continue
        if t.nesting == -1:
            depth -= 1
            continue
        # leaf token
        if t.type in ("fence", "code_block") and t.map:
            a, b = t.map
            for ln in range(a, b):
                inert.add(ln)
            if t.type == "fence":
                closed = b - 1 < len(lines) and lines[b - 1].lstrip().startswith("```")
                fences.append((a, closed, t.info, t.content))
        if t.type == "html_block" and depth == 0 and t.map:
            raw = lines[t.map[0]]
            mb, me = BEGIN.match(raw), END.match(raw)
            if mb:
                markers.append(("begin", t.map[0], t.map[1], mb.group(1)))
            elif me:
                markers.append(("end", t.map[0], t.map[1], None))

    # --- build balanced, non-nested regions from the top-level markers ----------
    regions = []           # {profile, content_start, content_end}
    open_region = None
    for kind, l0, l1, profile in markers:
        if kind == "begin":
            if open_region is not None:
                errors.append({"code": "NESTED_OR_DUP_BEGIN", "line": l0,
                               "detail": "begin while a region is already open"})
                continue
            if profile != PROFILE:
                errors.append({"code": "UNKNOWN_PROFILE", "line": l0,
                               "detail": f"profile {profile!r} not implemented"})
                # still open the region structurally so we don't misread the end,
                # but mark it unusable by giving it no claims/capsules below.
                open_region = {"profile": profile, "content_start": l1,
                               "content_end": None, "usable": False}
            else:
                open_region = {"profile": profile, "content_start": l1,
                               "content_end": None, "usable": True}
        else:  # end
            if open_region is None:
                errors.append({"code": "UNEXPECTED_END", "line": l0,
                               "detail": "end with no open region"})
                continue
            open_region["content_end"] = l0
            regions.append(open_region)
            open_region = None
    if open_region is not None:
        errors.append({"code": "MISSING_END", "line": open_region["content_start"],
                       "detail": "region opened but never closed"})

    usable = [r for r in regions if r.get("usable")]
    if not usable and not errors:
        errors.append({"code": "NO_LIVE_REGION", "line": 0,
                       "detail": "document declares no live region"})

    # --- capsules: exact-opener fences inside a usable region -------------------
    capsules = []
    for start, closed, info, content in fences:
        raw_opener = lines[start].rstrip("\n")
        if raw_opener != OPENER:
            continue                                  # not a capsule candidate (raw check)
        if not closed:
            # an opened-but-unclosed capsule is a protocol violation regardless of
            # region (an unclosed fence also eats a following region end ⇒ MISSING_END).
            errors.append({"code": "UNCLOSED_FENCE", "line": start,
                           "detail": "capsule fence never closed"})
            continue
        region_idx = _region_of(start, usable)
        if region_idx is None:
            continue                                  # closed capsule outside a region ⇒ inert
        capsules.append({"line": start, "closed": closed, "region": region_idx,
                         "body_raw": content})

    # --- claims: inline glyphs in usable regions, outside inert spans -----------
    claims = []
    for ri, r in enumerate(usable):
        region_text_parts = []
        for ln in range(r["content_start"], r["content_end"]):
            if ln in inert:
                continue
            line = lines[ln]
            region_text_parts.append(line)
            for m in CLAIM.finditer(line):
                claims.append({"class": m.group(1), "payload": m.group(2).strip(),
                               "local_id": m.group(3), "line": ln, "region": ri})
        # stray closing glyph not consumed by a claim ⇒ delimiter injection (T7)
        joined = "\n".join(region_text_parts)
        consumed = sum(m.group(0).count("⟧") for m in CLAIM.finditer(joined))
        if joined.count("⟧") > consumed:
            errors.append({"code": "UNSUPPORTED_INLINE_DELIMITER",
                           "line": r["content_start"],
                           "detail": "a ⟧ appears outside a well-formed claim (v0: "
                                     "carry such text in a capsule)"})

    return {"parser": parser_id(), "regions": [
                {"profile": r["profile"], "content_start": r["content_start"],
                 "content_end": r["content_end"], "usable": r["usable"]} for r in regions],
            "claims": claims, "capsules": capsules, "errors": errors}


def _region_of(line, regions):
    for i, r in enumerate(regions):
        if r["content_start"] <= line < r["content_end"]:
            return i
    return None


def _codes(report):
    return sorted({e["code"] for e in report["errors"]})


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) != 2:
        print("usage: parser.py <file.md>", file=sys.stderr)
        sys.exit(2)
    with open(sys.argv[1], encoding="utf-8") as f:
        rep = parse(f.read())
    print(f"regions={len(rep['regions'])} claims={len(rep['claims'])} "
          f"capsules={len(rep['capsules'])} errors={_codes(rep)}")
    print(json.dumps(rep, ensure_ascii=False, sort_keys=True))
