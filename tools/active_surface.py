#!/usr/bin/env python3
"""Check the small, declared repository surface in surface/rows.json.

This checks evidence predicates, not the truth of each human statement. Output is
per-row; there is deliberately no document-level truth badge.
"""
from __future__ import annotations

import copy
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
PROFILE = "manifesto.active-surface@v0.1"
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEX_RE = re.compile(r"^[0-9a-f]{64}$")
CLASSES = {"operational", "normative", "intent", "retired"}
MODES = {"SUPERSEDED", "WITHDRAWN", "REFUTED", "ARCHIVED", "ABANDONED", "QUARANTINED", "REDACTED"}
COMMON = {"id", "class", "statement", "sources"}
FIELDS = {
    "operational": {"check", "falsifier"},
    "normative": {"authority", "scope", "revocation", "adopted", "by"},
    "intent": {"origin", "review_trigger", "expiry"},
    "retired": {"mode", "retired_on", "loss", "successor", "record"},
}
TIMEOUT_SECONDS = 180


class Refusal(Exception):
    pass


def strict_loads(text: str):
    def pairs_hook(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise Refusal(f"DUPLICATE_JSON_KEY:{key}")
            out[key] = value
        return out

    try:
        return json.loads(text, object_pairs_hook=pairs_hook)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Refusal(f"JSON_INVALID:{exc}") from exc


def nonempty(value, code: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Refusal(code)
    return value


def iso_date(value, code: str) -> dt.date:
    if not isinstance(value, str):
        raise Refusal(code)
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise Refusal(code) from exc


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pinned_path(root: Path, operand, code: str) -> tuple[str, str]:
    if not isinstance(operand, dict) or set(operand) != {"path", "sha256"}:
        raise Refusal(f"{code}:SCHEMA")
    rel, expected = operand["path"], operand["sha256"]
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
        raise Refusal(f"{code}:PATH_INVALID")
    if Path(rel).as_posix() != rel or not isinstance(expected, str) or not HEX_RE.fullmatch(expected):
        raise Refusal(f"{code}:PIN_INVALID")
    target = root / rel
    cursor = root
    for part in Path(rel).parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise Refusal(f"{code}:SYMLINK:{rel}")
    if not target.is_file():
        raise Refusal(f"{code}:MISSING:{rel}")
    actual = sha256(target)
    if actual != expected:
        raise Refusal(f"{code}:DIGEST_MISMATCH:{rel}")
    return rel, expected


def source(root: Path, operand, code: str) -> tuple[str, str] | None:
    if isinstance(operand, dict) and set(operand) == {"path", "sha256"}:
        return pinned_path(root, operand, code)
    if isinstance(operand, dict) and set(operand) == {"locator", "note"}:
        nonempty(operand["locator"], f"{code}:LOCATOR_EMPTY")
        nonempty(operand["note"], f"{code}:NOTE_EMPTY")
        return None
    raise Refusal(f"{code}:SCHEMA")


def validate_profile(root: Path, doc, today: dt.date):
    if not isinstance(doc, dict) or set(doc) != {"profile", "as_of", "rows"}:
        raise Refusal("PROFILE_SCHEMA")
    if doc["profile"] != PROFILE:
        raise Refusal("PROFILE_UNKNOWN")
    as_of = iso_date(doc["as_of"], "AS_OF_INVALID")
    if as_of > today:
        raise Refusal("AS_OF_IN_FUTURE")
    if not isinstance(doc["rows"], list) or not doc["rows"]:
        raise Refusal("ROWS_EMPTY")

    rows, ids = [], set()
    for raw in doc["rows"]:
        if not isinstance(raw, dict):
            raise Refusal("ROW_NOT_OBJECT")
        rid, cls = raw.get("id"), raw.get("class")
        if not isinstance(rid, str) or not ID_RE.fullmatch(rid):
            raise Refusal(f"ROW_ID_INVALID:{rid!r}")
        if rid in ids:
            raise Refusal(f"ROW_ID_DUPLICATE:{rid}")
        ids.add(rid)
        if not isinstance(cls, str) or cls not in CLASSES:
            raise Refusal(f"ROW_CLASS_UNKNOWN:{rid}:{cls!r}")
        if set(raw) != COMMON | FIELDS[cls]:
            raise Refusal(f"ROW_FIELDS_NOT_CLOSED:{rid}")
        nonempty(raw["statement"], f"STATEMENT_EMPTY:{rid}")
        if not isinstance(raw["sources"], list) or not raw["sources"]:
            raise Refusal(f"SOURCES_EMPTY:{rid}")
        bound_sources = [source(root, item, f"SOURCE:{rid}") for item in raw["sources"]]

        if cls == "operational":
            nonempty(raw["falsifier"], f"FALSIFIER_EMPTY:{rid}")
            check = raw["check"]
            if not isinstance(check, dict) or set(check) != {"argv", "entrypoint"}:
                raise Refusal(f"CHECK_SCHEMA:{rid}")
            argv = check["argv"]
            if not isinstance(argv, list) or not argv or not all(isinstance(arg, str) and arg for arg in argv):
                raise Refusal(f"CHECK_ARGV_INVALID:{rid}")
            entrypoint = pinned_path(root, check["entrypoint"], f"CHECK_ENTRYPOINT:{rid}")
            if entrypoint not in bound_sources or entrypoint[0] not in argv:
                raise Refusal(f"CHECK_ENTRYPOINT_UNBOUND:{rid}")
        elif cls == "normative":
            pinned_path(root, raw["authority"], f"AUTHORITY:{rid}")
            nonempty(raw["scope"], f"SCOPE_EMPTY:{rid}")
            nonempty(raw["revocation"], f"REVOCATION_EMPTY:{rid}")
            nonempty(raw["by"], f"BY_EMPTY:{rid}")
            if iso_date(raw["adopted"], f"ADOPTED_INVALID:{rid}") > today:
                raise Refusal(f"ADOPTED_IN_FUTURE:{rid}")
        elif cls == "intent":
            nonempty(raw["origin"], f"ORIGIN_EMPTY:{rid}")
            trigger, expiry = raw["review_trigger"], raw["expiry"]
            if trigger is None and expiry is None:
                raise Refusal(f"INTENT_UNBOUNDED:{rid}")
            if trigger is not None:
                nonempty(trigger, f"TRIGGER_EMPTY:{rid}")
            if expiry is not None and iso_date(expiry, f"EXPIRY_INVALID:{rid}") < today:
                raise Refusal(f"INTENT_EXPIRED:{rid}:{expiry}")
        else:
            if not isinstance(raw["mode"], str) or raw["mode"] not in MODES:
                raise Refusal(f"RETIRED_MODE_UNKNOWN:{rid}")
            if iso_date(raw["retired_on"], f"RETIRED_ON_INVALID:{rid}") > today:
                raise Refusal(f"RETIRED_IN_FUTURE:{rid}")
            nonempty(raw["loss"], f"LOSS_EMPTY:{rid}")
            if raw["successor"] is not None and (
                not isinstance(raw["successor"], str) or not ID_RE.fullmatch(raw["successor"])
            ):
                raise Refusal(f"SUCCESSOR_INVALID:{rid}")
            source(root, raw["record"], f"RETIREMENT_RECORD:{rid}")
            if raw["mode"] == "REDACTED" and any(item is not None for item in bound_sources):
                raise Refusal(f"REDACTED_CARRIES_BYTE_PIN:{rid}")
        rows.append(raw)

    present = {row["class"] for row in rows}
    if present != CLASSES:
        raise Refusal(f"CLASS_SET_NOT_CLOSED:{sorted(present)}")
    by_id = {row["id"]: row for row in rows}
    for row in rows:
        if row["class"] == "retired" and row["successor"] is not None:
            successor = by_id.get(row["successor"])
            if successor is None:
                raise Refusal(f"SUCCESSOR_UNKNOWN:{row['id']}:{row['successor']}")
            if successor["class"] == "retired":
                raise Refusal(f"SUCCESSOR_RETIRED:{row['id']}:{row['successor']}")
    return rows


def execute(rows, root: Path):
    out = []
    for row in rows:
        rid, cls = row["id"], row["class"]
        if cls == "operational":
            try:
                proc = subprocess.run(row["check"]["argv"], cwd=root, capture_output=True, timeout=TIMEOUT_SECONDS)
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise Refusal(f"CHECK_ERROR:{rid}:{type(exc).__name__}") from exc
            if proc.returncode != 0:
                raise Refusal(f"CHECK_RED:{rid}:exit={proc.returncode}")
            predicate, credit = "exit-zero-now", "operational-execution"
        elif cls == "normative":
            predicate, credit = "pinned-authority-declaration", "repository-declared-authority"
        elif cls == "intent":
            predicate, credit = "bounded-open-edge", "none"
        else:
            predicate, credit = "typed-retirement", "none"
        out.append((rid, cls, predicate, credit))
    return out


def load(path: Path):
    if path.is_symlink() or not path.is_file():
        raise Refusal("ROWS_MISSING_OR_SYMLINK")
    return strict_loads(path.read_text(encoding="utf-8"))


def selftest(doc, today: dt.date) -> None:
    controls = []

    def refuses(name, candidate, expected, at=today):
        try:
            validate_profile(ROOT, candidate, at)
        except Refusal as exc:
            if expected not in str(exc):
                raise AssertionError(f"{name}: wrong refusal {exc}") from exc
            controls.append(name)
            return
        raise AssertionError(f"{name}: mutation survived")

    try:
        strict_loads('{"a":1,"a":2}')
    except Refusal as exc:
        assert "DUPLICATE_JSON_KEY" in str(exc)
        controls.append("duplicate-json-key")
    else:
        raise AssertionError("duplicate-json-key: mutation survived")

    def pick(cls: str, want=None) -> int:
        """Address the row to mutate by class, never by position: ordinary
        surface acts reorder and retype rows, and a stale index mutates a row
        the control was not written for -- which passes, silently, for the
        wrong reason."""
        for index, row in enumerate(doc["rows"]):
            if row["class"] == cls and (want is None or want(row)):
                return index
        raise AssertionError(f"selftest needs a {cls} row it can mutate")

    byte_pinned = lambda row: any(set(item) == {"path", "sha256"} for item in row["sources"])

    mutant = copy.deepcopy(doc); mutant["rows"] = []
    refuses("empty-vector", mutant, "ROWS_EMPTY")
    mutant = copy.deepcopy(doc); mutant["rows"][pick("operational", byte_pinned)]["sources"][0]["sha256"] = "0" * 64
    refuses("source-drift", mutant, "DIGEST_MISMATCH")
    mutant = copy.deepcopy(doc); mutant["rows"][pick("normative")]["authority"]["sha256"] = "0" * 64
    refuses("authority-drift", mutant, "DIGEST_MISMATCH")
    mutant = copy.deepcopy(doc); intent = pick("intent")
    mutant["rows"][intent]["review_trigger"] = None; mutant["rows"][intent]["expiry"] = None
    refuses("unbounded-intent", mutant, "INTENT_UNBOUNDED")
    mutant = copy.deepcopy(doc); mutant["rows"][pick("retired")]["successor"] = "missing-row"
    refuses("dangling-successor", mutant, "SUCCESSOR_UNKNOWN")
    mutant = copy.deepcopy(doc); mutant["rows"][pick("operational")]["class"] = []
    refuses("malformed-class", mutant, "ROW_CLASS_UNKNOWN")
    mutant = copy.deepcopy(doc); mutant["rows"][pick("retired", byte_pinned)]["mode"] = "REDACTED"
    refuses("redacted-byte-oracle", mutant, "REDACTED_CARRIES_BYTE_PIN")
    # CONTROLLED-FORGETTING-0.1 I4: loss is first-class for EVERY mode, not just
    # SUPERSEDED. The refusal existed unburned; without this control the
    # invariant was prose that happened to be enforced.
    mutant = copy.deepcopy(doc); mutant["rows"][pick("retired")]["loss"] = "   "
    refuses("empty-loss", mutant, "LOSS_EMPTY")
    rows = validate_profile(ROOT, doc, today)
    with mock.patch.object(subprocess, "run", return_value=subprocess.CompletedProcess([], 1)):
        try:
            execute(rows, ROOT)
        except Refusal as exc:
            assert "CHECK_RED" in str(exc)
            controls.append("red-operational-check")
        else:
            raise AssertionError("red-operational-check: mutation survived")
    print(f"ALL PASS ({len(controls)} active-surface mutation controls)")


def main(argv: list[str]) -> int:
    try:
        today = dt.date.fromisoformat(argv[1]) if len(argv) > 1 and argv[1] != "--selftest" else dt.datetime.now(dt.UTC).date()
        doc = load(ROOT / "surface" / "rows.json")
        if "--selftest" in argv:
            selftest(doc, today)
            return 0
        rows = validate_profile(ROOT, doc, today)
        for rid, cls, predicate, credit in execute(rows, ROOT):
            print(f"CHECKED  {rid}  class={cls} predicate={predicate} credit={credit}")
        print(f"VECTOR   rows={len(rows)} checked={len(rows)} refused=0 semantic-credit=none")
        return 0
    except (Refusal, AssertionError, ValueError) as exc:
        print(f"REFUSED  {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
