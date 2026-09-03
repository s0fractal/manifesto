#!/usr/bin/env python3
"""active_surface.py — build and verify `ACTIVE-SURFACE.json` from `surface/rows.json`.

    python3 tools/active_surface.py build     # regenerate ACTIVE-SURFACE.json
    python3 tools/active_surface.py verify    # refuse if stale, drifted, red or expired

NON-NORMATIVE (draft, `drafts/ACTIVE-SURFACE-0.1.md`). This tool changes nothing but
`ACTIVE-SURFACE.json`, and only under `build`.

A row DECLARES a class; the generator REFUSES when the row's evidence does not carry
that class. It never promotes or demotes silently. Four classes, four predicates:

  operational  an executable check exists in this repository and exits 0 now
  normative    an in-repo authority artifact is byte-pinned, with scope and a revocation
               condition
  intent       zero validation credit; must carry a review trigger or an expiry that has
               not passed
  retired      a CONTROLLED-FORGETTING-0.1 mode, a loss record, and a successor that
               resolves (or null)

External locators are recorded as `locator-only` and are NOT verified — they carry no
credit, only an address. Every refusal is typed so a control can name it.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROWS = ROOT / "surface" / "rows.json"
OUT = ROOT / "ACTIVE-SURFACE.json"
TAG_ROWS = "manifesto.active-surface-rows@v0.1"
TAG_OUT = "manifesto.active-surface@v0.1"
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CLASSES = ("operational", "normative", "intent", "retired")
RETIRED_MODES = ("SUPERSEDED", "WITHDRAWN", "REFUTED", "ARCHIVED", "ABANDONED", "QUARANTINED", "REDACTED")
COMMON = {"id", "class", "statement", "sources"}
CLASS_FIELDS = {
    "operational": {"check", "falsifier"},
    "normative": {"authority", "scope", "revocation", "adopted", "by"},
    "intent": {"origin", "review_trigger", "expiry"},
    "retired": {"mode", "retired_on", "loss", "successor", "record"},
}
CHECK_TIMEOUT = 180


class Refusal(Exception):
    pass


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def loads_closed(text: str):
    def hook(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise Refusal(f"DUPLICATE_JSON_KEY:{k}")
            out[k] = v
        return out
    return json.loads(text, object_pairs_hook=hook)


def nonempty(value, code: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Refusal(code)
    return value


def bind_path(root: Path, rel: str, code: str) -> dict:
    """Pin an in-repo file by digest. Refuses escapes, symlinks and absent files."""
    if not isinstance(rel, str) or rel.startswith("/") or ".." in Path(rel).parts:
        raise Refusal(f"{code}:PATH_INVALID:{rel}")
    target = root / rel
    if target.is_symlink():
        raise Refusal(f"{code}:SYMLINK:{rel}")
    if not target.is_file():
        raise Refusal(f"{code}:MISSING:{rel}")
    return {"path": rel, "sha256": sha256_file(target), "binding": "sha256"}


def bind_source(root: Path, src, rid: str) -> dict:
    if not isinstance(src, dict) or not ({"path"} <= set(src) <= {"path", "note"}
                                         or {"locator"} <= set(src) <= {"locator", "note"}):
        raise Refusal(f"SOURCE_SCHEMA:{rid}")
    if "path" in src:
        bound = bind_path(root, src["path"], f"SOURCE:{rid}")
    else:
        bound = {"locator": nonempty(src["locator"], f"SOURCE_LOCATOR_EMPTY:{rid}"), "binding": "locator-only"}
    if "note" in src:
        bound["note"] = nonempty(src["note"], f"SOURCE_NOTE_EMPTY:{rid}")
    return bound


def run_check(root: Path, argv, rid: str) -> dict:
    if not isinstance(argv, list) or not argv or not all(isinstance(a, str) and a for a in argv):
        raise Refusal(f"OPERATIONAL_CHECK_SCHEMA:{rid}")
    script = next((a for a in argv if a.endswith(".py") or a.endswith(".sh")), None)
    if script is None:
        raise Refusal(f"OPERATIONAL_CHECK_UNPINNED:{rid}")
    pinned = bind_path(root, script, f"OPERATIONAL_CHECK:{rid}")
    try:
        proc = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=CHECK_TIMEOUT)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Refusal(f"OPERATIONAL_CHECK_ERROR:{rid}:{type(exc).__name__}")
    if proc.returncode != 0:
        raise Refusal(f"OPERATIONAL_CHECK_RED:{rid}:exit={proc.returncode}")
    return {"argv": argv, "script": pinned, "exit": 0}


def compile_row(root: Path, row, today: dt.date) -> dict:
    if not isinstance(row, dict):
        raise Refusal("ROW_SCHEMA:not-an-object")
    rid = row.get("id")
    if not isinstance(rid, str) or not ID_RE.fullmatch(rid):
        raise Refusal(f"ROW_ID_INVALID:{rid!r}")
    cls = row.get("class")
    if cls not in CLASSES:
        raise Refusal(f"ROW_CLASS_UNKNOWN:{rid}:{cls!r}")
    allowed = COMMON | CLASS_FIELDS[cls]
    if set(row) != allowed:
        extra = sorted(set(row) - allowed)
        missing = sorted(allowed - set(row))
        raise Refusal(f"ROW_FIELDS_NOT_CLOSED:{rid}:extra={extra}:missing={missing}")
    out = {
        "id": rid,
        "class": cls,
        "statement": nonempty(row["statement"], f"ROW_STATEMENT_EMPTY:{rid}"),
        "sources": [bind_source(root, s, rid) for s in (row["sources"] if isinstance(row["sources"], list) else [None])],
    }
    if cls == "operational":
        out["falsifier"] = nonempty(row["falsifier"], f"OPERATIONAL_FALSIFIER_EMPTY:{rid}")
        out["check"] = run_check(root, row["check"], rid)
        out["credit"] = "validation"
    elif cls == "normative":
        auth = row["authority"]
        if not isinstance(auth, dict) or set(auth) != {"path"}:
            raise Refusal(f"NORMATIVE_AUTHORITY_SCHEMA:{rid}")
        out["authority"] = bind_path(root, auth["path"], f"NORMATIVE_AUTHORITY:{rid}")
        out["scope"] = nonempty(row["scope"], f"NORMATIVE_SCOPE_EMPTY:{rid}")
        out["revocation"] = nonempty(row["revocation"], f"NORMATIVE_REVOCATION_EMPTY:{rid}")
        out["by"] = nonempty(row["by"], f"NORMATIVE_BY_EMPTY:{rid}")
        if not isinstance(row["adopted"], str) or not DATE_RE.fullmatch(row["adopted"]):
            raise Refusal(f"NORMATIVE_ADOPTED_INVALID:{rid}")
        out["adopted"] = row["adopted"]
        out["credit"] = "authority"
    elif cls == "intent":
        out["origin"] = nonempty(row["origin"], f"INTENT_ORIGIN_EMPTY:{rid}")
        trigger, expiry = row["review_trigger"], row["expiry"]
        if trigger is None and expiry is None:
            raise Refusal(f"INTENT_UNBOUNDED:{rid}")
        if trigger is not None:
            out["review_trigger"] = nonempty(trigger, f"INTENT_TRIGGER_EMPTY:{rid}")
        else:
            out["review_trigger"] = None
        if expiry is not None:
            if not isinstance(expiry, str) or not DATE_RE.fullmatch(expiry):
                raise Refusal(f"INTENT_EXPIRY_INVALID:{rid}")
            if dt.date.fromisoformat(expiry) < today:
                raise Refusal(f"INTENT_EXPIRED:{rid}:{expiry}")
        out["expiry"] = expiry
        out["credit"] = "none"
    else:  # retired
        if row["mode"] not in RETIRED_MODES:
            raise Refusal(f"RETIRED_MODE_UNKNOWN:{rid}:{row['mode']!r}")
        out["mode"] = row["mode"]
        if not isinstance(row["retired_on"], str) or not DATE_RE.fullmatch(row["retired_on"]):
            raise Refusal(f"RETIRED_ON_INVALID:{rid}")
        out["retired_on"] = row["retired_on"]
        out["loss"] = nonempty(row["loss"], f"RETIRED_NO_LOSS:{rid}")
        if row["successor"] is not None and (not isinstance(row["successor"], str) or not ID_RE.fullmatch(row["successor"])):
            raise Refusal(f"RETIRED_SUCCESSOR_INVALID:{rid}")
        out["successor"] = row["successor"]
        out["record"] = bind_source(root, row["record"], rid)
        if row["mode"] == "REDACTED" and any("path" in s for s in out["sources"]):
            raise Refusal(f"RETIRED_REDACTED_CARRIES_BYTES:{rid}")
        out["credit"] = "retired"
    return out


def build(root: Path, rows_path: Path, today: dt.date | None = None) -> dict:
    today = today or dt.date.today()
    if rows_path.is_symlink():
        raise Refusal("ROWS_SYMLINK")
    if not rows_path.is_file():
        raise Refusal("ROWS_MISSING")
    doc = loads_closed(rows_path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or set(doc) != {"tag", "as_of", "rows"}:
        raise Refusal("ROWS_SCHEMA:top-level fields are not closed")
    if doc["tag"] != TAG_ROWS:
        raise Refusal(f"ROWS_TAG:{doc['tag']!r}")
    if not isinstance(doc["as_of"], str) or not DATE_RE.fullmatch(doc["as_of"]):
        raise Refusal("ROWS_AS_OF_INVALID")
    if not isinstance(doc["rows"], list) or not doc["rows"]:
        raise Refusal("ROWS_EMPTY")

    compiled: dict[str, dict] = {}
    for row in doc["rows"]:
        entry = compile_row(root, row, today)
        if entry["id"] in compiled:
            raise Refusal(f"ROW_ID_DUPLICATE:{entry['id']}")
        compiled[entry["id"]] = entry
    for entry in compiled.values():
        if entry["class"] == "retired" and entry["successor"] is not None:
            succ = compiled.get(entry["successor"])
            if succ is None:
                raise Refusal(f"RETIRED_SUCCESSOR_UNKNOWN:{entry['id']}:{entry['successor']}")
            if succ["class"] == "retired":
                raise Refusal(f"RETIRED_SUCCESSOR_RETIRED:{entry['id']}:{entry['successor']}")

    classes = {c: sorted((e for e in compiled.values() if e["class"] == c), key=lambda e: e["id"]) for c in CLASSES}
    generator = Path(__file__).resolve()
    return {
        "tag": TAG_OUT,
        "as_of": doc["as_of"],
        "generated_from": {
            "rows": {"path": rows_path.relative_to(root).as_posix(), "sha256": sha256_file(rows_path)},
            "generator": {"path": generator.relative_to(root).as_posix() if generator.is_relative_to(root) else generator.name,
                          "sha256": sha256_file(generator)},
        },
        "credit": {
            "validation": [e["id"] for e in classes["operational"]],
            "authority": [e["id"] for e in classes["normative"]],
            "none": [e["id"] for e in classes["intent"]],
            "retired": [e["id"] for e in classes["retired"]],
        },
        "classes": classes,
    }


def render(surface: dict) -> str:
    return json.dumps(surface, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def verify(root: Path, rows_path: Path, out_path: Path, today: dt.date | None = None) -> list[str]:
    try:
        expected = render(build(root, rows_path, today))
    except Refusal as exc:
        return [str(exc)]
    if out_path.is_symlink():
        return ["SURFACE_SYMLINK"]
    if not out_path.is_file():
        return ["SURFACE_MISSING"]
    if out_path.read_text(encoding="utf-8") != expected:
        return ["SURFACE_STALE"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["build", "verify"])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--rows", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--today", default=None, help="ISO date override (controls only)")
    args = parser.parse_args()
    root = args.root.resolve()
    rows = (args.rows or root / "surface" / "rows.json").resolve()
    out = (args.out or root / "ACTIVE-SURFACE.json").resolve()
    today = dt.date.fromisoformat(args.today) if args.today else None

    if args.command == "build":
        try:
            surface = build(root, rows, today)
        except Refusal as exc:
            print(f"REFUSED  {exc}")
            return 1
        out.write_text(render(surface), encoding="utf-8")
        counts = {c: len(v) for c, v in surface["classes"].items()}
        print(f"BUILT    {out.relative_to(root) if out.is_relative_to(root) else out}  {counts}")
        return 0

    errors = verify(root, rows, out, today)
    for error in errors:
        print(f"REFUSED  {error}")
    if errors:
        return 1
    print("CHECKED  ACTIVE-SURFACE.json is fresh: every declared class carries its predicate; intent carries no credit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
