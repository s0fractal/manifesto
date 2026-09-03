#!/usr/bin/env python3
"""Check the small, declared repository surface in surface/rows.json.

This checks evidence predicates, not the truth of each human statement. Output is
per-row; there is deliberately no document-level truth badge.

TIME. A wall clock is not a source of governance truth here, and three axes are
kept apart:

  causal order   git -- commit and tree digests, parent ancestry, pinned
                 authority bytes. Which act preceded which needs no clock.
  human dates    LABELS. Shape is checked; ordering against `now` is not
                 authority and grants nothing. This tool used to refuse
                 AS_OF_IN_FUTURE / ADOPTED_IN_FUTURE / RETIRED_IN_FUTURE, and
                 that cost a real refusal of a legitimate act: an adoption taken
                 at 00:25+03:00 was "in the future" against now(UTC). Those
                 gates guarded nothing -- no predicate downstream reads a date --
                 so they are gone.
  external mark  not implemented here, and not needed by anything yet.

`expiry` is the one place a clock still bites, and it bites in its own room:
structural validity is clock-free, and `--due` is a separate projection that
reports overdue review debts and exits non-zero. An overdue intent is a debt,
not a malformed row, and the two must not be reported by the same word.
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


def stamp(value, code: str) -> dt.datetime:
    """Parse a date LABEL and return the instant it denotes, for projections
    only. Two shapes are accepted:

      YYYY-MM-DD              a day, read as ending at 23:59:59Z
      RFC 3339 with offset    an instant, e.g. 2026-09-04T00:25:17+03:00

    A datetime WITHOUT an offset is refused. That is the exact ambiguity that
    bit this surface: a date-only label was compared against `now(UTC)`, so an
    act taken at 00:25+03:00 was refused as being in the future. If you need an
    instant, say which instant; if a day is enough, a day is fine.

    Shape is checked here. Ordering against a wall clock is NOT authority --
    see the module docstring.
    """
    if not isinstance(value, str):
        raise Refusal(code)
    try:
        if len(value) == 10:
            return dt.datetime.combine(dt.date.fromisoformat(value),
                                       dt.time(23, 59, 59), tzinfo=dt.UTC)
        parsed = dt.datetime.fromisoformat(value)
    except ValueError as exc:
        raise Refusal(code) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise Refusal(f"{code}:OFFSET_MISSING")
    return parsed


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


def validate_profile(root: Path, doc):
    if not isinstance(doc, dict) or set(doc) != {"profile", "as_of", "rows"}:
        raise Refusal("PROFILE_SCHEMA")
    if doc["profile"] != PROFILE:
        raise Refusal("PROFILE_UNKNOWN")
    stamp(doc["as_of"], "AS_OF_INVALID")
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
            stamp(raw["adopted"], f"ADOPTED_INVALID:{rid}")
        elif cls == "intent":
            nonempty(raw["origin"], f"ORIGIN_EMPTY:{rid}")
            trigger, expiry = raw["review_trigger"], raw["expiry"]
            if trigger is None and expiry is None:
                raise Refusal(f"INTENT_UNBOUNDED:{rid}")
            if trigger is not None:
                nonempty(trigger, f"TRIGGER_EMPTY:{rid}")
            if expiry is not None:
                # Shape only. Whether the date has PASSED is a clock-dependent
                # projection (see due()), never structural validity: an overdue
                # review is a debt, not a malformed row.
                stamp(expiry, f"EXPIRY_INVALID:{rid}")
        else:
            if not isinstance(raw["mode"], str) or raw["mode"] not in MODES:
                raise Refusal(f"RETIRED_MODE_UNKNOWN:{rid}")
            stamp(raw["retired_on"], f"RETIRED_ON_INVALID:{rid}")
            nonempty(raw["loss"], f"LOSS_EMPTY:{rid}")
            if raw["successor"] is not None and (
                not isinstance(raw["successor"], str) or not ID_RE.fullmatch(raw["successor"])
            ):
                raise Refusal(f"SUCCESSOR_INVALID:{rid}")
            source(root, raw["record"], f"RETIREMENT_RECORD:{rid}")
            if raw["mode"] == "REDACTED" and any(item is not None for item in bound_sources):
                raise Refusal(f"REDACTED_CARRIES_BYTE_PIN:{rid}")
        rows.append(raw)

    # The class vocabulary is CLOSED (an unknown class is refused per row, above)
    # but occupancy is NOT COMPULSORY. Requiring one row of every class made the
    # vector keep a class alive for the checker's sake: when the open edge that
    # justified the only `intent` row was actually closed, the row could not be
    # deleted without tripping this, so a false statement stayed on the surface
    # to satisfy a shape rule. A closed vocabulary is about which classes may
    # appear, never about which must.
    by_id = {row["id"]: row for row in rows}
    for row in rows:
        if row["class"] == "retired" and row["successor"] is not None:
            successor = by_id.get(row["successor"])
            if successor is None:
                raise Refusal(f"SUCCESSOR_UNKNOWN:{row['id']}:{row['successor']}")
            if successor["class"] == "retired":
                raise Refusal(f"SUCCESSOR_RETIRED:{row['id']}:{row['successor']}")
    return rows


def due(rows, now: dt.datetime | None = None):
    """Clock-dependent projection, deliberately NOT part of validity.

    Kept with teeth on purpose: `--due` exits non-zero when a review debt has
    come due. A deadline that can no longer fail is not a deadline, and moving
    expiry out of validation must not quietly turn it into one.
    """
    now = now or dt.datetime.now(dt.UTC)
    overdue = []
    for row in rows:
        if row["class"] != "intent" or row["expiry"] is None:
            continue
        if now > stamp(row["expiry"], f"EXPIRY_INVALID:{row['id']}"):
            overdue.append((row["id"], row["expiry"]))
    return overdue


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


def selftest(doc) -> None:
    controls = []

    def refuses(name, candidate, expected):
        try:
            validate_profile(ROOT, candidate)
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
    # Synthetic, so the control does not depend on a live intent row existing:
    # a class may legitimately be empty, and a control that quietly stops running
    # when its class empties is a control that reports nothing while passing.
    synthetic_intent = {
        "id": "synthetic-intent-control", "class": "intent",
        "statement": "control row, never part of the live vector",
        "sources": [{"locator": "selftest fixture", "note": "synthetic; address only"}],
        "origin": "active_surface selftest", "review_trigger": None, "expiry": None,
    }
    mutant = copy.deepcopy(doc); mutant["rows"].append(copy.deepcopy(synthetic_intent))
    refuses("unbounded-intent", mutant, "INTENT_UNBOUNDED")
    # An expired intent is a DEBT, not a malformed row: structural validation
    # must admit it, and the clock-dependent projection must report it. Both
    # halves are burned, because demoting the clock is only correct if the
    # deadline still bites somewhere.
    expired = copy.deepcopy(synthetic_intent); expired["expiry"] = "1999-01-01"
    mutant = copy.deepcopy(doc); mutant["rows"].append(copy.deepcopy(expired))
    rows_with_debt = validate_profile(ROOT, mutant)
    controls.append("expired-intent-is-not-a-validity-failure")
    overdue = due(rows_with_debt)
    assert [rid for rid, _ in overdue] == ["synthetic-intent-control"], (
        f"due-projection lost its teeth: an expiry of 1999-01-01 produced {overdue}")
    controls.append("due-projection-reports-the-overdue-intent")
    fresh = copy.deepcopy(synthetic_intent); fresh["expiry"] = "2999-01-01"
    mutant = copy.deepcopy(doc); mutant["rows"].append(fresh)
    assert due(validate_profile(ROOT, mutant)) == [], (
        "due-projection reported a debt for an expiry in the year 2999")
    controls.append("due-projection-stays-quiet-when-nothing-is-owed")

    # Dates are labels now. A future adoption date is admitted -- burned here so
    # the removed gate cannot creep back without a control going red.
    mutant = copy.deepcopy(doc); mutant["rows"][pick("normative")]["adopted"] = "2999-01-01"
    validate_profile(ROOT, mutant)
    controls.append("future-date-is-not-a-validity-failure")
    mutant = copy.deepcopy(doc); mutant["rows"][pick("normative")]["adopted"] = "2026-09-04T00:25:17+03:00"
    validate_profile(ROOT, mutant)
    controls.append("rfc3339-with-offset-admitted")
    mutant = copy.deepcopy(doc); mutant["rows"][pick("normative")]["adopted"] = "2026-09-04T00:25:17"
    refuses("offsetless-datetime", mutant, "OFFSET_MISSING")
    mutant = copy.deepcopy(doc); mutant["rows"][pick("normative")]["adopted"] = "the fourth"
    refuses("malformed-date", mutant, "ADOPTED_INVALID")
    # The vocabulary stays closed even though occupancy is not compulsory.
    mutant = copy.deepcopy(doc); mutant["rows"][pick("operational")]["class"] = "speculative"
    refuses("class-outside-vocabulary", mutant, "ROW_CLASS_UNKNOWN")
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
    rows = validate_profile(ROOT, doc)
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
        doc = load(ROOT / "surface" / "rows.json")
        if "--selftest" in argv:
            selftest(doc)
            return 0
        rows = validate_profile(ROOT, doc)
        if "--due" in argv:
            # A separate room on purpose: this is the only reading that consults
            # a clock, and it never speaks about validity.
            overdue = due(rows)
            for rid, when in overdue:
                print(f"DUE      {rid}  expiry={when} has passed; the review it names is owed")
            print(f"PROJECTION due={len(overdue)} clock=wall-clock authority=none")
            return 1 if overdue else 0
        for rid, cls, predicate, credit in execute(rows, ROOT):
            print(f"CHECKED  {rid}  class={cls} predicate={predicate} credit={credit}")
        print(f"VECTOR   rows={len(rows)} checked={len(rows)} refused=0 semantic-credit=none")
        return 0
    except (Refusal, AssertionError, ValueError) as exc:
        print(f"REFUSED  {exc}")
        return 1
    except Exception as exc:  # the LAST membrane, never the schema
        # Reaching here means an input found a path the typed checks miss. Fail
        # closed and name it; do not print a traceback and do not treat this as
        # a category anything is allowed to live in.
        print(f"REFUSED  INTERNAL_UNTYPED:{type(exc).__name__}:{exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
