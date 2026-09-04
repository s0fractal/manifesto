#!/usr/bin/env python3
"""Derive this repository's agent context view from its canonical owners.

Phase 3 of CONTROLLED-FORGETTING-0.1 asks for one thing: repo-local tooling that
separates DEFAULT retrieval from HISTORICAL retrieval. This is one specimen of
that, not a memory framework.

There is no second registry here. Every fact is derived, on demand, from owners
that already exist:

  surface/rows.json                          -- what the repository treats as
                                                operational, normative or retired
  drafts/retirement-records/<id>.json        -- the applied retirement act whose
                                                subjects and replacement operands
                                                form the one active/retired pair
                                                this specimen covers

Both owners are read through their own consumers -- `active_surface` and
`retirement_record_check` -- so their operands are recomputed from bytes rather
than believed. Nothing in this file is an oracle for them, and the document this
file prints is never an oracle for anything: `--check` derives the view in
process from freshly recomputed owners and is never handed a generated document
to trust. Output is on demand; no view artifact is committed, because no
consumer has been demonstrated for a checked-in copy.

THE TWO MODES

  default     the agent working set: the active surface rows and the live
              replacement operands. The record's five retired subjects are
              absent -- not their paths, not their digests, not their reasons.
              What remains is a pointer: the record's address and how many facts
              are withheld, which is the short tombstone status
              CONTROLLED-FORGETTING section 8.1 asks a default loader to carry.

  historical  the same set plus the retired subjects OF THIS PAIR ONLY, each
              wrapped in a typed envelope: retirement mode, loss, relation and
              replacement, the retrieval address, and the admission triple.
              Availability is not admission (I3): this mode hands over bytes
              with their status, and grants no credit. Retired facts the
              selected record does not address -- including the surface's own
              retired rows -- are outside this specimen and enter neither mode.

NOTHING MOVES A SUBJECT BACK INTO DEFAULT

This specimen implements no readmission door, and it is the narrower for it. The
canonical record's admission triple is bound exactly as it stands, with
`default: EXCLUDED`; any other state is refused as READOPTION_NOT_IMPLEMENTED.
A one-field edit from `EXCLUDED` to `INCLUDED` is not a governed transition: the
authority address the record already carries was given for the retirement, and
reusing it would let an ordinary field edit spend an act that never decided
this. Re-entry needs an explicit governed transition -- a decision identity of
its own -- and that is outside this specimen's scope, stated rather than
approximated. Historical retrieval stays open and stays non-crediting. Like the
record consumer, this file never certifies that any act was within anyone's
power (I6).

COUNTING GRAMMAR -- see `--measure`, and drafts/CONTEXT-POLICY-0.1.md.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import active_surface as surface  # noqa: E402
import retirement_record_check as records  # noqa: E402

VIEW = "manifesto.context-view@v0.1"

# The specimen is pinned HERE, in the consumer, and not read from the record:
# a record cannot tell this tool how much of itself must survive. Deleting the
# record, a subject or an operand must therefore fail closed rather than produce
# a smaller green set.
SPECIMEN_RECORD = "embedded-claims-lineage"
SPECIMEN_STATUS = "APPLIED"
SPECIMEN_SCOPE = "in-repo"
SPECIMEN_RELATION = "replaced-by"
SPECIMEN_SUBJECTS = 5
SPECIMEN_OPERANDS = 8
# The admission triple is pinned here too, exactly as the record declares it
# today. This specimen covers the EXCLUDED state and nothing else: readmission
# is not implemented, so any other triple is a refusal rather than a mode.
SPECIMEN_ADMISSION = {
    "default": "EXCLUDED",
    "historical_review": "ALLOWED_WITH_STATUS",
    "normative_use": "FORBIDDEN_WITHOUT_READOPTION",
}

ENVELOPE = ("HISTORICAL ARTIFACT: retired, EXCLUDED from default context. "
            "Cite with this status; do not treat as current precedent.")
# A retired row of the declared surface carries no admission field of its own.
# This admission is not invented here -- it is the adopted core of
# CONTROLLED-FORGETTING-0.1 (I2 default exclusion, I3 no implicit resurrection)
# applied to a row the surface itself classifies as retired.
ROW_ADMISSION = {
    "default": "EXCLUDED",
    "historical_review": "ALLOWED_WITH_STATUS",
    "normative_use": "FORBIDDEN_WITHOUT_READOPTION",
}
MODES = ("default", "historical")


class Refusal(Exception):
    pass


def render(doc) -> str:
    """One canonical serialization, so bytes are a measurement and not a mood."""
    return json.dumps(doc, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def digest_of(root: Path, rel: str) -> str:
    return hashlib.sha256((root / rel).read_bytes()).hexdigest()


def address(operand) -> str:
    """A source reduced to one address string. `path` is byte-pinned; `locator`
    is address-only and stays counted as unresolved."""
    if isinstance(operand, dict) and "path" in operand:
        return operand["path"]
    if isinstance(operand, dict) and "locator" in operand:
        return operand["locator"]
    raise Refusal("SOURCE_SHAPE_UNKNOWN")


def source_entry(operand) -> dict:
    if isinstance(operand, dict) and set(operand) == {"path", "sha256"}:
        return {"path": operand["path"], "sha256": operand["sha256"], "resolved": "byte-pinned"}
    if isinstance(operand, dict) and set(operand) == {"locator", "note"}:
        return {"locator": operand["locator"], "resolved": "address-only"}
    raise Refusal("SOURCE_SHAPE_UNKNOWN")


# --- owners ----------------------------------------------------------------

def load_owners(root: Path, records_dir: Path | None = None):
    """Read both owners through their own consumers, which recompute pinned
    bytes and git objects. An owner refusal is surfaced, never swallowed."""
    try:
        doc = surface.load(root / "surface" / "rows.json")
        rows = surface.validate_profile(root, doc)
    except surface.Refusal as exc:
        raise Refusal(f"OWNER_REFUSED:surface:{exc}") from exc

    try:
        loaded = records.load_records(records_dir or root / "drafts" / "retirement-records")
    except records.Refusal as exc:
        raise Refusal(f"OWNER_REFUSED:records:{exc}") from exc

    found = {}
    for path, record in loaded:
        rid = record.get("id")
        if not isinstance(rid, str) or not rid:
            raise Refusal(f"RECORD_ID_MISSING:{path.name}")
        if rid in found:
            raise Refusal(f"RECORD_ID_DUPLICATE:{rid}")
        found[rid] = record
    if SPECIMEN_RECORD not in found:
        # Claim starvation: the record this specimen names cannot be deleted
        # into a pass. Its absence is a refusal, not a smaller green set.
        raise Refusal(f"SPECIMEN_RECORD_MISSING:{SPECIMEN_RECORD}")
    return rows, found[SPECIMEN_RECORD]


def assert_no_readoption(record) -> None:
    """The gate this specimen actually has. It reads the record's admission and
    covers exactly one state: EXCLUDED as declared. An `INCLUDED` default is not
    a supported mode here -- the record's authority address was given for the
    retirement and says nothing about a later readmission, so honouring the flip
    would let an ordinary field edit spend an act that never decided it."""
    admission = record.get("admission")
    if not isinstance(admission, dict):
        raise Refusal("SPECIMEN_ADMISSION_UNEXPECTED:not-an-object")
    if admission.get("default") != SPECIMEN_ADMISSION["default"]:
        raise Refusal(f"READOPTION_NOT_IMPLEMENTED:{record.get('id')}:"
                      f"admission.default={admission.get('default')}")
    if admission != SPECIMEN_ADMISSION:
        raise Refusal(f"SPECIMEN_ADMISSION_UNEXPECTED:{sorted(admission.items())}")


def bind(record) -> None:
    """Bind the specimen record: the owner consumer first (it recomputes every
    subject digest from the git object at the before revision and every
    replacement operand from disk), then this specimen's own scope pins."""
    try:
        records.validate(record)
    except records.Refusal as exc:
        raise Refusal(f"OWNER_REFUSED:record:{exc}") from exc
    if record["status"] != SPECIMEN_STATUS:
        raise Refusal(f"SPECIMEN_STATUS_UNEXPECTED:{record['status']}")
    if record["subject_scope"] != SPECIMEN_SCOPE:
        raise Refusal(f"SPECIMEN_SCOPE_UNEXPECTED:{record['subject_scope']}")
    if record["replacement"]["relation"] != SPECIMEN_RELATION:
        raise Refusal(f"SPECIMEN_RELATION_UNEXPECTED:{record['replacement']['relation']}")
    assert_no_readoption(record)
    if len(record["subjects"]) != SPECIMEN_SUBJECTS:
        raise Refusal(f"SPECIMEN_SUBJECT_COUNT:{len(record['subjects'])}!={SPECIMEN_SUBJECTS}")
    operands = record["replacement"]["operands"]
    if len(operands) != SPECIMEN_OPERANDS:
        raise Refusal(f"SPECIMEN_OPERAND_COUNT:{len(operands)}!={SPECIMEN_OPERANDS}")
    seen = set()
    for operand in operands:
        key = address(operand)
        if key in seen:
            # The record consumer refuses duplicate SUBJECTS; duplicate operands
            # are this specimen's to refuse, because they inflate the active
            # side of the pair for free.
            raise Refusal(f"OPERAND_DUPLICATE:{key}")
        seen.add(key)


def recompute_operands(root: Path, record) -> dict[str, str]:
    """Recompute the active operands from bytes in this process. The digests
    that reach the view come from files read here, not from the record's own
    numbers -- missing, malformed and stale all fail closed."""
    out = {}
    for operand in record["replacement"]["operands"]:
        if not isinstance(operand, dict) or set(operand) != {"path", "sha256"}:
            if isinstance(operand, dict) and set(operand) == {"locator", "note"}:
                continue
            raise Refusal("OPERAND_MALFORMED")
        rel = operand["path"]
        if Path(rel).is_absolute() or ".." in Path(rel).parts or Path(rel).as_posix() != rel:
            raise Refusal(f"OPERAND_MALFORMED:{rel}")
        target = root / rel
        if not target.is_file():
            raise Refusal(f"OPERAND_MISSING:{rel}")
        actual = digest_of(root, rel)
        if actual != operand["sha256"]:
            raise Refusal(f"OPERAND_STALE:{rel}")
        out[rel] = actual
    return out


# --- the view --------------------------------------------------------------

def row_fact(row) -> dict:
    fact = {
        "kind": "surface-row",
        "id": row["id"],
        "class": row["class"],
        "statement": row["statement"],
        "sources": [source_entry(item) for item in row["sources"]],
    }
    if row["class"] == "retired":
        fact.update({
            "status": "RETIRED",
            "mode": row["mode"],
            "retired_on": row["retired_on"],
            "loss": [row["loss"]],
            "relation": "replaced-by" if row["successor"] else "none",
            "replacement": row["successor"],
            "source": address(row["record"]),
            "admission": ROW_ADMISSION,
            "admission_source": "CONTROLLED-FORGETTING-0.1 I2/I3, the adopted core",
            "envelope": ENVELOPE,
        })
    return fact


def operand_fact(record, rel: str, digest: str) -> dict:
    return {
        "kind": "replacement-operand",
        "id": rel,
        "role": f"active side of the pair recorded by {record['id']} "
                f"(relation {record['replacement']['relation']})",
        "sources": [{"path": rel, "sha256": digest, "resolved": "byte-pinned"}],
    }


def subject_fact(record, subject) -> dict:
    return {
        "kind": "retired-subject",
        "id": subject["path"],
        "status": "RETIRED",
        "mode": subject["mode"],
        "reason": subject["reason"],
        "loss": list(record["loss"]),
        "relation": record["replacement"]["relation"],
        "replacement": sorted(address(o) for o in record["replacement"]["operands"]),
        "source": f"git show {record['before_revision']}:{subject['path']}",
        "preservation": record["preservation"]["policy"],
        "admission": dict(record["admission"]),
        "admission_source": f"drafts/retirement-records/{record['id']}.json",
        "envelope": ENVELOPE,
    }


def build(rows, record, operands: dict[str, str], mode: str) -> dict:
    """Pure: already-bound owners in, one deterministic document out."""
    if mode not in MODES:
        raise Refusal(f"MODE_UNKNOWN:{mode}")
    assert_no_readoption(record)
    # The active surface is the substrate of both modes. Its retired rows are
    # NOT this specimen's history: they belong to no pair (successor: null) and
    # the selected record never addressed them. Historical mode expands exactly
    # the one pair it names, so the measured delta is that pair's and not a
    # class-wide sweep of everything the repository ever retired.
    facts = [row_fact(row) for row in rows if row["class"] != "retired"]
    facts += [operand_fact(record, rel, digest) for rel, digest in sorted(operands.items())]
    if mode == "historical":
        facts += [subject_fact(record, subject) for subject in record["subjects"]]

    seen = set()
    for fact in facts:
        key = (fact["kind"], fact["id"])
        if key in seen:
            raise Refusal(f"FACT_DUPLICATE:{fact['kind']}:{fact['id']}")
        seen.add(key)
    facts.sort(key=lambda fact: (fact["kind"], fact["id"]))

    doc = {
        "view": VIEW,
        "mode": mode,
        "derived_from": [
            "surface/rows.json",
            f"drafts/retirement-records/{record['id']}.json",
        ],
        "policy": ("Derived on demand from the owners above; the owners win on any "
                   "disagreement. Retrieval carries no semantic credit and no "
                   "document-level verdict."),
        "facts": facts,
    }
    if mode == "default":
        # The short tombstone status the default loader is allowed to carry: an
        # address and a count, never the retired facts themselves. The count is
        # this pair's withheld subjects -- it does not speak for retired facts
        # the record never addressed.
        doc["historical"] = {
            "record": f"drafts/retirement-records/{record['id']}.json",
            "retired_facts_withheld": len(record["subjects"]),
            "admission_default": record["admission"]["default"],
            "command": "python3 tools/context_view.py --mode historical",
        }
    return doc


def measure(doc) -> dict:
    facts = doc["facts"]
    unresolved = sum(1 for fact in facts for item in fact.get("sources", [])
                     if item.get("resolved") == "address-only")
    unresolved += sum(1 for fact in facts
                      if fact.get("status") == "RETIRED"
                      and not str(fact.get("source", "")).startswith("git show "))
    return {
        "facts": len(facts),
        "bytes": len(render(doc).encode("utf-8")),
        "retired_facts": sum(1 for fact in facts if fact.get("status") == "RETIRED"),
        "unresolved": unresolved,
    }


# --- invariants ------------------------------------------------------------

def assert_default_excludes(default_doc, rows, record) -> None:
    """The one invariant this specimen exists for. Checked against the rendered
    bytes, because a retired path smuggled into any field is still in the
    working set."""
    text = render(default_doc)
    # A retired row is excluded by its own class, whatever any record says.
    for row in rows:
        if row["class"] == "retired" and f'"{row["id"]}"' in text:
            raise Refusal(f"DEFAULT_ADMITS_RETIRED_ROW:{row['id']}")
    # No admission state exempts a caller from the rest of this check: an
    # `INCLUDED` record is refused here too, so a view built by some other path
    # cannot reach an agent by declaring itself readmitted.
    assert_no_readoption(record)
    for subject in record["subjects"]:
        for token in (subject["path"], subject["sha256"], subject["reason"]):
            if token and token in text:
                raise Refusal(f"DEFAULT_ADMITS_EXCLUDED_SUBJECT:{subject['path']}")
    if any(fact.get("status") == "RETIRED" for fact in default_doc["facts"]):
        raise Refusal("DEFAULT_CARRIES_RETIRED_FACT")


def assert_historical_envelope(historical_doc) -> None:
    """Historical availability must arrive with status, or it is resurrection
    with extra steps (I3, section 8.2)."""
    retired = [fact for fact in historical_doc["facts"] if fact.get("status") == "RETIRED"]
    if not retired:
        raise Refusal("HISTORICAL_MODE_CARRIES_NO_RETIRED_FACT")
    for fact in retired:
        for field in ("mode", "loss", "relation", "source", "admission", "envelope"):
            if not fact.get(field):
                raise Refusal(f"HISTORICAL_ENVELOPE_INCOMPLETE:{fact['id']}:{field}")
        admission = fact["admission"]
        if admission.get("normative_use") != "FORBIDDEN_WITHOUT_READOPTION":
            raise Refusal(f"HISTORICAL_FACT_GRANTS_NORMATIVE_USE:{fact['id']}")
        if admission.get("default") != "EXCLUDED":
            raise Refusal(f"HISTORICAL_FACT_CLAIMS_DEFAULT_ADMISSION:{fact['id']}")


def assert_one_pair(historical_doc, record) -> None:
    """The specimen says one pair, so the expansion must be one pair. Every
    retired fact historical mode hands over is a subject of the selected record;
    a retired fact from anywhere else -- another record, or a retired surface row
    that merely shares the class -- would silently widen both the claim and the
    measured delta."""
    addressed = {subject["path"] for subject in record["subjects"]}
    retired = [fact for fact in historical_doc["facts"] if fact.get("status") == "RETIRED"]
    for fact in retired:
        if fact.get("kind") != "retired-subject" or fact["id"] not in addressed:
            raise Refusal(f"HISTORICAL_ADMITS_UNRELATED_FACT:{fact['kind']}:{fact['id']}")
    if len(retired) != len(addressed):
        raise Refusal(f"HISTORICAL_PAIR_INCOMPLETE:{len(retired)}!={len(addressed)}")


def assert_scope_nonempty(default_doc, historical_doc) -> None:
    """F6: a view that shrank to nothing must not read as a clean one."""
    if not default_doc["facts"]:
        raise Refusal("DEFAULT_VIEW_EMPTY")
    retired = sum(1 for fact in historical_doc["facts"] if fact.get("status") == "RETIRED")
    if retired < SPECIMEN_SUBJECTS:
        raise Refusal(f"HISTORICAL_SCOPE_SHRANK:{retired}<{SPECIMEN_SUBJECTS}")
    if len(historical_doc["facts"]) <= len(default_doc["facts"]):
        raise Refusal("HISTORICAL_NOT_WIDER_THAN_DEFAULT")


def views(root: Path):
    rows, record = load_owners(root)
    bind(record)
    operands = recompute_operands(root, record)
    default = build(rows, record, operands, "default")
    historical = build(rows, record, operands, "historical")
    return rows, record, operands, default, historical


def check(root: Path) -> int:
    rows, record, operands, default, historical = views(root)
    assert_default_excludes(default, rows, record)
    assert_historical_envelope(historical)
    assert_one_pair(historical, record)
    assert_scope_nonempty(default, historical)
    # Determinism: the same owners must render the same bytes, or "bytes" is not
    # a measurement anyone can reproduce.
    if render(build(rows, record, operands, "default")) != render(default):
        raise Refusal("VIEW_NOT_DETERMINISTIC")

    before, after = measure(historical), measure(default)
    print(f"BOUND    record={record['id']} status={record['status']} "
          f"subjects={len(record['subjects'])} operands={len(operands)} "
          f"surface-rows={len(rows)} admission-default={record['admission']['default']}")
    print(f"DEFAULT  facts={after['facts']} bytes={after['bytes']} "
          f"retired-facts={after['retired_facts']} unresolved={after['unresolved']}")
    print(f"HISTORY  facts={before['facts']} bytes={before['bytes']} "
          f"retired-facts={before['retired_facts']} unresolved={before['unresolved']}")
    print(f"PASS context view: {before['retired_facts']} retired facts withheld from default; "
          f"every active operand recomputed from bytes; credit=none")
    return 0


def report_measure(root: Path) -> int:
    _, _, _, default, historical = views(root)
    before, after = measure(historical), measure(default)
    print("GRAMMAR  fact = one surface row, one replacement operand, or one retired "
          "subject named by the owners; bytes = utf-8 length of the canonical "
          "render (sorted keys, indent 2, trailing newline)")
    print(f"BEFORE   mode=historical facts={before['facts']} bytes={before['bytes']} "
          f"retired-facts={before['retired_facts']} unresolved={before['unresolved']}")
    print(f"AFTER    mode=default    facts={after['facts']} bytes={after['bytes']} "
          f"retired-facts={after['retired_facts']} unresolved={after['unresolved']}")
    print(f"DELTA    facts={after['facts'] - before['facts']} "
          f"bytes={after['bytes'] - before['bytes']} "
          f"retired-facts={after['retired_facts'] - before['retired_facts']} "
          f"scope=this specimen only; not a repository-level measurement")
    return 0


# --- controls --------------------------------------------------------------

def selftest(root: Path) -> int:
    rows, record, operands, default, historical = views(root)
    controls: list[str] = []

    def refuses(name, thunk, expected):
        try:
            thunk()
        except Refusal as exc:
            if expected not in str(exc):
                raise AssertionError(f"{name}: wrong refusal {exc}") from exc
            controls.append(name)
            return
        raise AssertionError(f"{name}: mutation survived")

    # --- P0: a retired subject does not re-enter default context -------------
    text = render(default)
    for subject in record["subjects"]:
        assert subject["path"] not in text and subject["sha256"] not in text, subject["path"]
    controls.append("default-carries-no-retired-subject")

    # ...and the exclusion is READ FROM the record, not luck: the one-field edit
    # the review reproduced is run through the live owner/check path here. The
    # owner consumer accepts it -- INCLUDED is a legal value of its enum and the
    # authority object is untouched -- and this specimen still refuses, because
    # a reused address is not a commitment to a decision it never made.
    readmitted = copy.deepcopy(record)
    readmitted["admission"]["default"] = "INCLUDED"
    records.validate(readmitted)  # the owner is satisfied; that is the point
    refuses("readmission-by-field-edit-is-refused",
            lambda: bind(readmitted), "READOPTION_NOT_IMPLEMENTED")
    refuses("readmission-cannot-build-a-default-view",
            lambda: build(rows, readmitted, operands, "default"), "READOPTION_NOT_IMPLEMENTED")
    refuses("readmission-cannot-pass-the-default-invariant",
            lambda: assert_default_excludes(default, rows, readmitted),
            "READOPTION_NOT_IMPLEMENTED")

    # Not only in memory: the same flip written to disk and read back through
    # the owner's real loader is refused on the live path an agent would use.
    with tempfile.TemporaryDirectory() as staging:
        (Path(staging) / f"{SPECIMEN_RECORD}.json").write_text(
            json.dumps(readmitted, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        def readmitted_from_disk():
            _, on_disk = load_owners(root, Path(staging))
            bind(on_disk)

        refuses("readmission-refused-on-the-live-load-path",
                readmitted_from_disk, "READOPTION_NOT_IMPLEMENTED")
    # The whole triple is bound, not just its first field: an owner-legal edit
    # that closes historical review would leave this specimen's prose describing
    # a policy the record no longer declares.
    drifted_admission = copy.deepcopy(record)
    drifted_admission["admission"]["historical_review"] = "FORBIDDEN"
    records.validate(drifted_admission)
    refuses("admission-triple-drift",
            lambda: bind(drifted_admission), "SPECIMEN_ADMISSION_UNEXPECTED")

    retired_rows = [row for row in rows if row["class"] == "retired"]
    assert retired_rows, "the surface has no retired row, so this control is vacuous"
    smuggled_row = copy.deepcopy(default)
    smuggled_row["facts"].append(row_fact(retired_rows[0]))
    refuses("default-admitting-a-retired-row",
            lambda: assert_default_excludes(smuggled_row, rows, record),
            "DEFAULT_ADMITS_RETIRED_ROW")

    # --- P1: the expansion is ONE pair, and only that pair -------------------
    addressed = {subject["path"] for subject in record["subjects"]}
    historical_retired = [fact for fact in historical["facts"] if fact.get("status") == "RETIRED"]
    assert {fact["id"] for fact in historical_retired} == addressed, (
        "historical mode expanded something other than the selected record's "
        "subjects", sorted(fact["id"] for fact in historical_retired))
    controls.append("historical-expands-exactly-the-selected-pair")
    assert not any(fact["kind"] == "surface-row" and fact.get("status") == "RETIRED"
                   for fact in historical["facts"]), (
        "a retired surface row entered the one-pair view merely by sharing the class")
    controls.append("retired-rows-outside-the-pair-enter-neither-mode")

    # A retired fact this record never addressed is refused even when it is
    # perfectly well formed -- sharing the class is not sharing the pair.
    unrelated = copy.deepcopy(historical)
    unrelated["facts"].append(row_fact(retired_rows[0]))
    refuses("historical-admitting-an-unrelated-retired-row",
            lambda: assert_one_pair(unrelated, record), "HISTORICAL_ADMITS_UNRELATED_FACT")
    foreign = copy.deepcopy(historical)
    foreign["facts"].append(subject_fact(
        record, {"path": "drafts/FROM-ANOTHER-RECORD.md", "mode": "superseded",
                 "reason": "retired by some other act", "sha256": "0" * 64}))
    refuses("historical-admitting-a-foreign-record-subject",
            lambda: assert_one_pair(foreign, record), "HISTORICAL_ADMITS_UNRELATED_FACT")
    partial = copy.deepcopy(historical)
    partial["facts"] = [fact for fact in partial["facts"]
                        if fact.get("kind") != "retired-subject" or fact["id"] != sorted(addressed)[0]]
    refuses("historical-dropping-half-the-pair",
            lambda: assert_one_pair(partial, record), "HISTORICAL_PAIR_INCOMPLETE")

    # A view that carries a retired fact while the record says EXCLUDED is a
    # refusal, whatever produced it.
    smuggled = copy.deepcopy(default)
    smuggled["facts"].append(subject_fact(record, record["subjects"][0]))
    refuses("default-admitting-an-excluded-subject",
            lambda: assert_default_excludes(smuggled, rows, record),
            "DEFAULT_ADMITS_EXCLUDED_SUBJECT")

    # And the owner's own floor holds underneath this specimen's refusal: an
    # applied record whose authority stops being addressed is refused by the
    # owner consumer, before any question about admission is reached.
    unaddressed = copy.deepcopy(record)
    unaddressed["authority"]["act"] = "   "
    refuses("record-without-addressed-authority",
            lambda: bind(unaddressed), "AUTHORITY_ACT_UNADDRESSED")

    # --- P0: starvation. Deleting the input must not shrink the green set ----
    thinner = copy.deepcopy(record)
    thinner["subjects"] = thinner["subjects"][:-1]
    refuses("subject-deleted-is-not-a-smaller-green-set",
            lambda: bind(thinner), "SPECIMEN_SUBJECT_COUNT")
    fewer = copy.deepcopy(record)
    fewer["replacement"]["operands"] = fewer["replacement"]["operands"][:-1]
    refuses("operand-deleted-is-not-a-smaller-green-set",
            lambda: bind(fewer), "SPECIMEN_OPERAND_COUNT")
    with tempfile.TemporaryDirectory() as empty:
        refuses("record-deleted-is-not-a-smaller-green-set",
                lambda: load_owners(root, Path(empty)), "SPECIMEN_RECORD_MISSING")
    starved = copy.deepcopy(historical)
    starved["facts"] = [fact for fact in starved["facts"] if fact["kind"] != "retired-subject"]
    refuses("historical-scope-shrank",
            lambda: assert_scope_nonempty(default, starved), "HISTORICAL_SCOPE_SHRANK")
    refuses("empty-default-view",
            lambda: assert_scope_nonempty({"facts": []}, historical), "DEFAULT_VIEW_EMPTY")

    # --- P0: operands are recomputed, never believed -------------------------
    stale = copy.deepcopy(record)
    stale["replacement"]["operands"][0]["sha256"] = "0" * 64
    refuses("operand-stale", lambda: recompute_operands(root, stale), "OPERAND_STALE")
    missing = copy.deepcopy(record)
    missing["replacement"]["operands"][0] = {"path": "drafts/NEVER-EXISTED.md",
                                             "sha256": "0" * 64}
    refuses("operand-missing", lambda: recompute_operands(root, missing), "OPERAND_MISSING")
    malformed = copy.deepcopy(record)
    malformed["replacement"]["operands"][0] = {"path": "README.md"}
    refuses("operand-malformed", lambda: recompute_operands(root, malformed), "OPERAND_MALFORMED")
    traversing = copy.deepcopy(record)
    traversing["replacement"]["operands"][0] = {"path": "../etc/passwd", "sha256": "0" * 64}
    refuses("operand-escaping-the-tree",
            lambda: recompute_operands(root, traversing), "OPERAND_MALFORMED")
    duplicated = copy.deepcopy(record)
    duplicated["replacement"]["operands"][1] = copy.deepcopy(
        duplicated["replacement"]["operands"][0])
    refuses("operand-duplicate", lambda: bind(duplicated), "OPERAND_DUPLICATE")

    # --- P0: an owner refusal is surfaced, not swallowed ---------------------
    drifted = copy.deepcopy(record)
    drifted["subjects"][0]["sha256"] = "0" * 64
    refuses("owner-refusal-propagates", lambda: bind(drifted),
            "OWNER_REFUSED:record:SUBJECT_DIGEST_MISMATCH")

    # --- P1: historical retrieval arrives with its envelope ------------------
    stripped = copy.deepcopy(historical)
    for fact in stripped["facts"]:
        if fact.get("status") == "RETIRED":
            fact["envelope"] = ""
            break
    refuses("historical-fact-without-envelope",
            lambda: assert_historical_envelope(stripped), "HISTORICAL_ENVELOPE_INCOMPLETE")
    promoted = copy.deepcopy(historical)
    for fact in promoted["facts"]:
        if fact.get("status") == "RETIRED":
            fact["admission"]["normative_use"] = "FORBIDDEN"
            break
    refuses("historical-fact-granting-normative-use",
            lambda: assert_historical_envelope(promoted),
            "HISTORICAL_FACT_GRANTS_NORMATIVE_USE")
    lossless = copy.deepcopy(historical)
    for fact in lossless["facts"]:
        if fact.get("status") == "RETIRED":
            fact["loss"] = []
            break
    refuses("historical-fact-without-loss",
            lambda: assert_historical_envelope(lossless), "HISTORICAL_ENVELOPE_INCOMPLETE")

    # --- P1: shape --------------------------------------------------------
    refuses("unknown-mode", lambda: build(rows, record, operands, "convenient"), "MODE_UNKNOWN")
    assert render(build(rows, record, operands, "historical")) == render(historical)
    controls.append("view-is-deterministic")
    before, after = measure(historical), measure(default)
    # The delta is the pair's: exactly the record's subjects, no more, so the
    # advertised number cannot quietly count retired facts from elsewhere.
    assert after["retired_facts"] == 0 and before["retired_facts"] == SPECIMEN_SUBJECTS, (
        before, after)
    assert before["facts"] - after["facts"] == SPECIMEN_SUBJECTS, (before, after)
    assert after["bytes"] < before["bytes"], (before, after)
    controls.append("measurement-separates-the-two-modes")

    print(f"ALL PASS ({len(controls)} context-view mutation controls)")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--mode", choices=MODES, default="default")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--measure", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv[1:])
    try:
        if args.selftest:
            return selftest(ROOT)
        if args.check:
            return check(ROOT)
        if args.measure:
            return report_measure(ROOT)
        rows, record, _, default, historical = views(ROOT)
        # A printed view is a checked view: the exclusion invariant runs before
        # anything reaches stdout, so no agent can be handed a default set that
        # quietly carries a retired fact.
        if args.mode == "historical":
            assert_historical_envelope(historical)
            assert_one_pair(historical, record)
            sys.stdout.write(render(historical))
        else:
            assert_default_excludes(default, rows, record)
            sys.stdout.write(render(default))
        return 0
    except (Refusal, AssertionError, ValueError) as exc:
        print(f"REFUSED  {exc}")
        return 1
    except Exception as exc:  # the LAST membrane, never the schema
        print(f"REFUSED  INTERNAL_UNTYPED:{type(exc).__name__}:{exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
