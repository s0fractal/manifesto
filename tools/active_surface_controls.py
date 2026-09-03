#!/usr/bin/env python3
"""Mutation controls for tools/active_surface.py.

    python3 tools/active_surface_controls.py

NON-NORMATIVE. Each control breaks exactly one predicate of one class and requires
the generator to refuse with the reason that names it. A green here means: the
label "active surface" is never wider than the predicate the generator checked.

The controls run against a self-contained fixture root (fake green/red checks,
fake authority file) so they do not depend on the repository's content. The first
control alone runs against the real repository: the committed ACTIVE-SURFACE.json
must be byte-fresh.
"""
from __future__ import annotations

import copy
import datetime as dt
import importlib.util
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("active_surface", ROOT / "tools" / "active_surface.py")
assert SPEC and SPEC.loader
AS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AS)

TODAY = dt.date(2026, 9, 3)
results: list[bool] = []


def chk(label: str, condition: bool, detail: str = "") -> None:
    results.append(bool(condition))
    print(("  OK    " if condition else "  FAIL  ") + label + (f" — {detail}" if detail and not condition else ""))


def refusal(root: Path, rows: dict, today: dt.date = TODAY) -> str:
    rows_path = root / "surface" / "rows.json"
    rows_path.parent.mkdir(parents=True, exist_ok=True)
    rows_path.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    try:
        AS.build(root, rows_path, today)
        return ""
    except AS.Refusal as exc:
        return str(exc)


def fixture_root(base: Path) -> Path:
    root = base / "repo"
    (root / "tools").mkdir(parents=True)
    (root / "checks").mkdir()
    shutil.copy(ROOT / "tools" / "active_surface.py", root / "tools" / "active_surface.py")
    (root / "checks" / "green.py").write_text("import sys; sys.exit(0)\n", encoding="utf-8")
    (root / "checks" / "red.py").write_text("import sys; sys.exit(7)\n", encoding="utf-8")
    (root / "AUTHORITY.md").write_text("accepted\n", encoding="utf-8")
    (root / "SOURCE.md").write_text("source bytes\n", encoding="utf-8")
    return root


def baseline() -> dict:
    return {
        "tag": AS.TAG_ROWS,
        "as_of": "2026-09-03",
        "rows": [
            {"id": "op", "class": "operational", "statement": "green check", "sources": [{"path": "SOURCE.md"}],
             "check": ["python3", "checks/green.py"], "falsifier": "the check goes red"},
            {"id": "norm", "class": "normative", "statement": "accepted rule", "sources": [{"path": "SOURCE.md"}],
             "authority": {"path": "AUTHORITY.md"}, "scope": "fixture", "revocation": "owner withdraws", "adopted": "2026-09-01", "by": "owner"},
            {"id": "want", "class": "intent", "statement": "open edge", "sources": [{"locator": "elsewhere"}],
             "origin": "fixture", "review_trigger": "before use", "expiry": "2026-12-31"},
            {"id": "gone", "class": "retired", "statement": "old thing", "sources": [{"locator": "elsewhere"}],
             "mode": "ARCHIVED", "retired_on": "2026-09-02", "loss": "its check has no home", "successor": "want",
             "record": {"locator": "tombstone elsewhere"}},
        ],
    }


def mutate(**patch):
    """Return baseline rows with one row patched (by id) or replaced."""
    rows = baseline()
    for rid, change in patch.items():
        for row in rows["rows"]:
            if row["id"] == rid:
                if change is None:
                    rows["rows"].remove(row)
                else:
                    row.update(change)
                    for key, value in list(row.items()):
                        if value == "<DEL>":
                            del row[key]
                break
    return rows


def main() -> int:
    print("active_surface controls")
    real = AS.verify(ROOT, ROOT / "surface" / "rows.json", ROOT / "ACTIVE-SURFACE.json")
    chk("real repository: committed ACTIVE-SURFACE.json is byte-fresh and every class carries its predicate", real == [], str(real))

    with tempfile.TemporaryDirectory(prefix="active-surface-controls-") as td:
        root = fixture_root(Path(td))

        chk("fixture baseline builds", refusal(root, baseline()) == "", refusal(root, baseline()))

        # operational
        r = refusal(root, mutate(op={"check": ["python3", "checks/red.py"]}))
        chk("operational: red check is refused, not demoted", r.startswith("OPERATIONAL_CHECK_RED:op"), r)
        r = refusal(root, mutate(op={"check": ["python3", "checks/absent.py"]}))
        chk("operational: missing check script is refused", r.startswith("OPERATIONAL_CHECK:op:MISSING"), r)
        r = refusal(root, mutate(op={"check": ["true"]}))
        chk("operational: a check with no pinnable script is refused", r.startswith("OPERATIONAL_CHECK_UNPINNED:op"), r)
        r = refusal(root, mutate(op={"falsifier": ""}))
        chk("operational: empty falsifier is refused", r.startswith("OPERATIONAL_FALSIFIER_EMPTY:op"), r)

        # normative
        r = refusal(root, mutate(norm={"revocation": "<DEL>"}))
        chk("normative: missing revocation condition is refused", r.startswith("ROW_FIELDS_NOT_CLOSED:norm"), r)
        r = refusal(root, mutate(norm={"scope": ""}))
        chk("normative: empty scope is refused", r.startswith("NORMATIVE_SCOPE_EMPTY:norm"), r)
        r = refusal(root, mutate(norm={"authority": {"path": "MISSING.md"}}))
        chk("normative: absent authority artifact is refused", r.startswith("NORMATIVE_AUTHORITY:norm:MISSING"), r)
        surface_before = AS.build(root, _write(root, baseline()), TODAY)
        (root / "AUTHORITY.md").write_text("accepted, then quietly edited\n", encoding="utf-8")
        surface_after = AS.build(root, _write(root, baseline()), TODAY)
        drift = surface_before["classes"]["normative"][0]["authority"]["sha256"] != surface_after["classes"]["normative"][0]["authority"]["sha256"]
        chk("normative: editing the authority bytes changes the pinned digest (drift is visible)", drift)
        (root / "AUTHORITY.md").write_text("accepted\n", encoding="utf-8")

        # intent
        r = refusal(root, mutate(want={"check": ["python3", "checks/green.py"]}))
        chk("intent: cannot carry a check (no validation credit)", r.startswith("ROW_FIELDS_NOT_CLOSED:want"), r)
        r = refusal(root, mutate(want={"review_trigger": None, "expiry": None}))
        chk("intent: unbounded (no trigger, no expiry) is refused", r.startswith("INTENT_UNBOUNDED:want"), r)
        r = refusal(root, mutate(want={"expiry": "2026-09-02"}))
        chk("intent: passed expiry is refused, forcing re-triage", r.startswith("INTENT_EXPIRED:want"), r)
        r = refusal(root, mutate(want={"expiry": "2026-09-02"}), today=dt.date(2026, 9, 1))
        chk("intent: same expiry before the date builds (clock, not text, decides)", r == "", r)
        ok = AS.build(root, _write(root, baseline()), TODAY)
        chk("intent: emitted credit is 'none' and never listed under validation",
            ok["classes"]["intent"][0]["credit"] == "none" and "want" not in ok["credit"]["validation"])

        # retired
        r = refusal(root, mutate(gone={"loss": ""}))
        chk("retired: missing loss record is refused", r.startswith("RETIRED_NO_LOSS:gone"), r)
        r = refusal(root, mutate(gone={"mode": "DELETED"}))
        chk("retired: mode outside CONTROLLED-FORGETTING vocabulary is refused", r.startswith("RETIRED_MODE_UNKNOWN:gone"), r)
        r = refusal(root, mutate(gone={"successor": "nobody"}))
        chk("retired: successor that does not resolve is refused", r.startswith("RETIRED_SUCCESSOR_UNKNOWN:gone"), r)
        r = refusal(root, mutate(gone={"successor": "gone"}))
        chk("retired: successor may not itself be retired", r.startswith("RETIRED_SUCCESSOR_RETIRED:gone"), r)
        r = refusal(root, mutate(gone={"mode": "REDACTED", "sources": [{"path": "SOURCE.md"}]}))
        chk("retired: REDACTED may not pin bytes (hash would be an oracle)", r.startswith("RETIRED_REDACTED_CARRIES_BYTES:gone"), r)

        # surface-level
        r = refusal(root, mutate(op={"class": "intent"}))
        chk("class relabel without matching fields is refused", r.startswith("ROW_FIELDS_NOT_CLOSED:op"), r)
        r = refusal(root, mutate(op={"class": "hypothesis"}))
        chk("unknown class is refused", r.startswith("ROW_CLASS_UNKNOWN:op"), r)
        dup = baseline(); dup["rows"].append(copy.deepcopy(dup["rows"][0]))
        r = refusal(root, dup)
        chk("duplicate id is refused", r.startswith("ROW_ID_DUPLICATE:op"), r)
        r = refusal(root, mutate(op={"validation_credit": 1}))
        chk("unknown field (credit smuggled in) is refused", r.startswith("ROW_FIELDS_NOT_CLOSED:op"), r)
        rows_path = _write(root, baseline())
        rows_path.write_text(rows_path.read_text(encoding="utf-8").replace('"class": "intent"', '"class": "operational", "class": "intent"', 1), encoding="utf-8")
        try:
            AS.build(root, rows_path, TODAY); r = ""
        except AS.Refusal as exc:
            r = str(exc)
        chk("duplicate JSON key fails before last-key-wins", r.startswith("DUPLICATE_JSON_KEY:class"), r)

        out = root / "ACTIVE-SURFACE.json"
        out.write_text(AS.render(AS.build(root, _write(root, baseline()), TODAY)), encoding="utf-8")
        chk("verify: fresh surface passes", AS.verify(root, rows_path, out, TODAY) == [])
        out.write_text(out.read_text(encoding="utf-8").replace('"credit": "none"', '"credit": "validation"', 1), encoding="utf-8")
        chk("verify: hand-edited surface (intent promoted to validation) is SURFACE_STALE",
            AS.verify(root, rows_path, out, TODAY) == ["SURFACE_STALE"])
        out.unlink()
        (root / "elsewhere.json").write_text("{}", encoding="utf-8")
        os.symlink(root / "elsewhere.json", out)
        chk("verify: surface behind a symlink is refused", AS.verify(root, rows_path, out, TODAY) == ["SURFACE_SYMLINK"])

    passed = sum(results)
    print(f"\n{'PASS' if all(results) else 'FAIL'} — active_surface controls: {passed}/{len(results)}")
    return 0 if all(results) else 1


def _write(root: Path, rows: dict) -> Path:
    rows_path = root / "surface" / "rows.json"
    rows_path.parent.mkdir(parents=True, exist_ok=True)
    rows_path.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    return rows_path


if __name__ == "__main__":
    sys.exit(main())
