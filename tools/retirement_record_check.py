#!/usr/bin/env python3
"""Check structured retirement records in drafts/retirement-records/.

The narrow general consumer CONTROLLED-FORGETTING-0.1 was missing: it reads a
RetirementRecord as data instead of reading prose about one. It checks that a
record is well formed and that its operands are exactly what it says they are;
it never checks that retiring the subjects was wise.

Deliberately absent: any document-level or repository-level retirement badge.
Output is per record. VALID means that record's operands bound and its
postconditions replayed green -- nothing about the repository as a whole.

v0.1 supports exactly two combinations, the two that fixtures exercise:
APPLIED + in-repo, and DRY_RUN + external. Every other combination is refused
rather than half-checked, because an unexercised path that returns VALID is
worth less than one that refuses.

The oracle is EXPECTED below and NOT the records: a record cannot certify its
own verdict, and the record set must match the manifest exactly, so deleting an
inconvenient fixture is a failure rather than a quiet pass.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "drafts" / "retirement-records"
PROFILE = "manifesto.retirement-record@v0.1"

# The closed external oracle. Ids, filenames and verdicts are all pinned here,
# in the checker, where a fixture cannot edit them.
EXPECTED = {
    "embedded-claims-lineage": "VALID",
    "bos-archive": "REFUSED:EXTERNAL_SUBJECT_IDENTITY_MISSING",
}

ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
REV_RE = re.compile(r"^[0-9a-f]{40}$")
STATUSES = {"APPLIED", "DRY_RUN"}
SCOPES = {"in-repo", "external"}
MODES = {"SUPERSEDED", "WITHDRAWN", "REFUTED", "ARCHIVED", "ABANDONED", "QUARANTINED", "REDACTED"}
RELATIONS = {"replaced-by", "extracted-from", "none"}
RUNNERS = {"python3"}
ADMISSION_DEFAULT = {"EXCLUDED", "INCLUDED"}
ADMISSION_REVIEW = {"ALLOWED_WITH_STATUS", "FORBIDDEN"}
ADMISSION_NORMATIVE = {"FORBIDDEN_WITHOUT_READOPTION", "FORBIDDEN"}
CORE_FIELDS = {"profile", "id", "status", "subject_scope", "subjects", "replacement",
               "loss", "preservation", "admission", "postconditions"}
TIMEOUT_SECONDS = 300


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


def string_list(value, code: str, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise Refusal(code)
    for item in value:
        nonempty(item, code)
    return value


def in_repo_path(rel, code: str) -> Path:
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
        raise Refusal(f"{code}:PATH_INVALID")
    if Path(rel).as_posix() != rel:
        raise Refusal(f"{code}:PATH_INVALID")
    cursor = ROOT
    for part in Path(rel).parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise Refusal(f"{code}:SYMLINK:{rel}")
    return ROOT / rel


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True)


def pinned_operand(operand, code: str) -> str:
    if not isinstance(operand, dict) or set(operand) != {"path", "sha256"}:
        raise Refusal(f"{code}:SCHEMA")
    rel, expected = operand["path"], operand["sha256"]
    target = in_repo_path(rel, code)
    if not isinstance(expected, str) or not HEX64_RE.fullmatch(expected):
        raise Refusal(f"{code}:PIN_INVALID")
    if not target.is_file():
        raise Refusal(f"{code}:MISSING:{rel}")
    if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
        raise Refusal(f"{code}:DIGEST_MISMATCH:{rel}")
    return rel


def historical_digest(revision: str, rel: str, code: str) -> str:
    """A retired subject's digest cannot come from the tree -- the file is gone,
    which is the point. It comes from the object git holds at the before
    revision, so the operand is exact rather than asserted."""
    proc = git("cat-file", "blob", f"{revision}:{rel}")
    if proc.returncode != 0:
        raise Refusal(f"{code}:SUBJECT_ABSENT_AT_BEFORE_REVISION:{rel}")
    return hashlib.sha256(proc.stdout).hexdigest()


def check_applied(record, revision: str) -> str:
    applied = record["applied"]
    if not isinstance(applied, dict) or set(applied) != {"apply_commit", "apply_tree", "receipt"}:
        raise Refusal("APPLIED_SCHEMA")
    for field in ("apply_commit", "apply_tree"):
        value = applied[field]
        if not isinstance(value, str) or not REV_RE.fullmatch(value):
            raise Refusal(f"APPLIED_{field.upper()}_INVALID")
    nonempty(applied["receipt"], "APPLIED_RECEIPT_EMPTY")
    parent = git("rev-parse", f"{applied['apply_commit']}^")
    if parent.returncode != 0 or parent.stdout.decode().strip() != revision:
        raise Refusal("APPLY_COMMIT_NOT_CHILD_OF_BEFORE_REVISION")
    tree = git("rev-parse", f"{applied['apply_commit']}^{{tree}}")
    if tree.returncode != 0 or tree.stdout.decode().strip() != applied["apply_tree"]:
        raise Refusal("APPLY_TREE_MISMATCH")
    return applied["apply_tree"]


def check_subjects(record, scope: str, revision, apply_tree) -> int:
    subjects = record["subjects"]
    if not isinstance(subjects, list) or not subjects:
        raise Refusal("SUBJECTS_EMPTY")
    seen = set()
    for subject in subjects:
        if not isinstance(subject, dict):
            raise Refusal("SUBJECT_NOT_AN_OBJECT")
        if subject.get("mode") not in MODES:
            raise Refusal(f"SUBJECT_MODE_UNKNOWN:{subject.get('mode')!r}")
        nonempty(subject.get("reason"), "SUBJECT_REASON_EMPTY")
        if scope == "in-repo":
            if set(subject) != {"path", "sha256", "mode", "reason"}:
                raise Refusal("SUBJECT_FIELDS_NOT_CLOSED")
            rel, expected = subject["path"], subject["sha256"]
            in_repo_path(rel, "SUBJECT")
            if not isinstance(expected, str) or not HEX64_RE.fullmatch(expected):
                raise Refusal(f"SUBJECT_PIN_INVALID:{rel}")
            # The transition itself, checked generically rather than trusted to
            # any subject-specific checker: the subject existed at the before
            # revision, and the named apply commit is where it stopped existing.
            if historical_digest(revision, rel, "SUBJECT") != expected:
                raise Refusal(f"SUBJECT_DIGEST_MISMATCH:{rel}")
            if git("cat-file", "-e", f"{apply_tree}:{rel}").returncode == 0:
                raise Refusal(f"SUBJECT_PRESENT_IN_APPLY_TREE:{rel}")
            if (ROOT / rel).exists():
                raise Refusal(f"RETIRED_SUBJECT_STILL_PRESENT:{rel}")
            key = rel
        else:
            if set(subject) != {"locator", "note", "mode", "reason"}:
                raise Refusal("SUBJECT_FIELDS_NOT_CLOSED")
            nonempty(subject["locator"], "SUBJECT_LOCATOR_EMPTY")
            nonempty(subject["note"], "SUBJECT_NOTE_EMPTY")
            key = subject["locator"]
        if key in seen:
            raise Refusal(f"SUBJECT_DUPLICATE:{key}")
        seen.add(key)
    return len(subjects)


def postcondition_argv(post) -> list[str]:
    """argv is CONSTRUCTED here, never taken from the record. A record that
    supplies its own argv can pin an entrypoint and then pass it as an inert
    argument to something else -- the pin looks bound and nothing runs."""
    if not isinstance(post, dict) or set(post) != {"runner", "entrypoint", "args", "falsifier"}:
        raise Refusal("POSTCONDITION_SCHEMA")
    runner = post["runner"]
    if runner not in RUNNERS:
        raise Refusal(f"POSTCONDITION_RUNNER_NOT_ALLOWED:{runner!r}")
    args = string_list(post["args"], "POSTCONDITION_ARGS_INVALID", allow_empty=True)
    nonempty(post["falsifier"], "POSTCONDITION_FALSIFIER_EMPTY")
    rel = pinned_operand(post["entrypoint"], "POSTCONDITION_ENTRYPOINT")
    return [runner, rel, *args]


def check_postconditions(record, status: str) -> list[list[str]]:
    posts = record["postconditions"]
    if not isinstance(posts, list):
        raise Refusal("POSTCONDITIONS_SCHEMA")
    if status == "DRY_RUN":
        if posts:
            raise Refusal("DRY_RUN_CARRIES_POSTCONDITIONS")
        return []
    if not posts:
        # An applied retirement whose only evidence is prose is the failure this
        # discipline exists to stop being.
        raise Refusal("APPLIED_WITHOUT_POSTCONDITION")
    return [postcondition_argv(post) for post in posts]


def validate(record) -> dict:
    if not isinstance(record, dict):
        raise Refusal("RECORD_NOT_AN_OBJECT")
    if record.get("profile") != PROFILE:
        raise Refusal("PROFILE_UNKNOWN")
    rid = record.get("id")
    if not isinstance(rid, str) or not ID_RE.fullmatch(rid):
        raise Refusal(f"RECORD_ID_INVALID:{rid!r}")
    status = record.get("status")
    if status not in STATUSES:
        raise Refusal(f"STATUS_UNKNOWN:{status!r}")
    scope = record.get("subject_scope")
    if scope not in SCOPES:
        raise Refusal(f"SUBJECT_SCOPE_UNKNOWN:{scope!r}")

    # Identity first (I1). The BOS trial's whole finding: a repository-shaped
    # external subject binds by declaration or not at all -- containment cannot
    # supply an identity that lives somewhere else.
    repository = record.get("repository")
    if scope == "external":
        if not (isinstance(repository, str) and repository.strip()):
            raise Refusal("EXTERNAL_SUBJECT_IDENTITY_MISSING")
    elif repository is not None:
        raise Refusal("IN_REPO_SUBJECT_DECLARES_REPOSITORY")

    if status == "APPLIED" and scope == "external":
        raise Refusal("EXTERNAL_APPLIED_UNSUPPORTED_IN_V0_1")
    if status == "DRY_RUN" and scope == "in-repo":
        raise Refusal("IN_REPO_DRY_RUN_UNSUPPORTED_IN_V0_1")
    if scope == "external" and record.get("before_revision") is not None:
        raise Refusal("EXTERNAL_SUBJECT_DECLARES_LOCAL_REVISION")
    if status == "DRY_RUN":
        if record.get("authority") is not None:
            raise Refusal("DRY_RUN_CLAIMS_AUTHORITY")
        if record.get("applied") is not None:
            raise Refusal("DRY_RUN_CLAIMS_APPLIED")

    # Exact shape, BEFORE anything indexes a field. A missing key must be a
    # typed refusal, not a traceback: a schema is the membrane, and a catch-all
    # is at best the last one.
    required = set(CORE_FIELDS)
    if scope == "in-repo":
        required.add("before_revision")
    if status == "APPLIED":
        required |= {"authority", "applied"}
    missing = sorted(required - set(record))
    if missing:
        raise Refusal(f"REQUIRED_FIELD_MISSING:{','.join(missing)}")
    unknown = sorted(set(record) - (required | {"repository"}))
    if unknown:
        raise Refusal(f"RECORD_FIELDS_UNKNOWN:{','.join(unknown)}")

    revision = apply_tree = None
    if scope == "in-repo":
        revision = record["before_revision"]
        if not isinstance(revision, str) or not REV_RE.fullmatch(revision):
            raise Refusal("BEFORE_REVISION_INVALID")
        if git("cat-file", "-e", f"{revision}^{{commit}}").returncode != 0:
            raise Refusal(f"BEFORE_REVISION_UNRESOLVABLE:{revision}")
        apply_tree = check_applied(record, revision)

    count = check_subjects(record, scope, revision, apply_tree)

    replacement = record["replacement"]
    if not isinstance(replacement, dict) or set(replacement) != {"relation", "operands"}:
        raise Refusal("REPLACEMENT_SCHEMA")
    relation = replacement["relation"]
    if relation not in RELATIONS:
        raise Refusal(f"RELATION_UNKNOWN:{relation!r}")
    operands = replacement["operands"]
    if not isinstance(operands, list):
        raise Refusal("REPLACEMENT_OPERANDS_SCHEMA")
    if relation == "none" and operands:
        raise Refusal("RELATION_NONE_CARRIES_OPERANDS")
    if relation != "none" and not operands:
        raise Refusal(f"RELATION_WITHOUT_OPERANDS:{relation}")
    # Operand shape follows the OPERAND, not the subject: a replacement living
    # in this repository is pinnable even when the retired thing was external.
    for operand in operands:
        if isinstance(operand, dict) and set(operand) == {"path", "sha256"}:
            pinned_operand(operand, "REPLACEMENT_OPERAND")
        elif isinstance(operand, dict) and set(operand) == {"locator", "note"}:
            nonempty(operand["locator"], "REPLACEMENT_OPERAND:LOCATOR_EMPTY")
            nonempty(operand["note"], "REPLACEMENT_OPERAND:NOTE_EMPTY")
        else:
            raise Refusal("REPLACEMENT_OPERAND:SCHEMA")

    # Loss is mandatory for every mode and every status. No shape of retirement
    # loses nothing; an empty list is unmeasured, not zero.
    string_list(record["loss"], "LOSS_EMPTY")

    preservation = record["preservation"]
    if not isinstance(preservation, dict) or set(preservation) != {"policy", "locator"}:
        raise Refusal("PRESERVATION_SCHEMA")
    nonempty(preservation["policy"], "PRESERVATION_POLICY_EMPTY")
    nonempty(preservation["locator"], "PRESERVATION_LOCATOR_EMPTY")

    admission = record["admission"]
    if not isinstance(admission, dict) or set(admission) != {"default", "historical_review", "normative_use"}:
        raise Refusal("ADMISSION_SCHEMA")
    if admission["default"] not in ADMISSION_DEFAULT:
        raise Refusal("ADMISSION_DEFAULT_UNKNOWN")
    if admission["historical_review"] not in ADMISSION_REVIEW:
        raise Refusal("ADMISSION_REVIEW_UNKNOWN")
    if admission["normative_use"] not in ADMISSION_NORMATIVE:
        raise Refusal("ADMISSION_NORMATIVE_UNKNOWN")

    if status == "APPLIED":
        # An ADDRESS for the act, never a proof that it was within anyone's
        # power. I6 stays a governance question; the record only says where to
        # look, and this checker never certifies legitimacy.
        authority = record["authority"]
        if not isinstance(authority, dict) or set(authority) != {"owner", "act"}:
            raise Refusal("AUTHORITY_SCHEMA")
        nonempty(authority["owner"], "AUTHORITY_OWNER_EMPTY")
        nonempty(authority["act"], "AUTHORITY_ACT_UNADDRESSED")

    argvs = check_postconditions(record, status)
    return {"id": rid, "status": status, "scope": scope, "subjects": count,
            "relation": relation, "argvs": argvs}


def replay(summary) -> int:
    for argv in summary["argvs"]:
        try:
            proc = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=TIMEOUT_SECONDS)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise Refusal(f"POSTCONDITION_ERROR:{type(exc).__name__}") from exc
        if proc.returncode != 0:
            raise Refusal(f"POSTCONDITION_RED:{' '.join(argv)}:exit={proc.returncode}")
    return len(summary["argvs"])


def verdict(record) -> tuple[str, dict | None]:
    try:
        summary = validate(record)
        replayed = replay(summary)
    except Refusal as exc:
        return f"REFUSED:{exc}", None
    summary["replayed"] = replayed
    return "VALID", summary


def check_manifest(found: dict[str, str]) -> None:
    """`found` maps record id -> filename stem. The record set must equal the
    oracle exactly, so a fixture cannot be deleted into a pass, and the filename
    must carry the id, so one file cannot quietly answer for another."""
    missing = sorted(set(EXPECTED) - set(found))
    if missing:
        raise Refusal(f"RECORD_MISSING:{','.join(missing)}")
    unexpected = sorted(set(found) - set(EXPECTED))
    if unexpected:
        raise Refusal(f"RECORD_NOT_IN_MANIFEST:{','.join(unexpected)}")
    for rid, stem in sorted(found.items()):
        if stem != rid:
            raise Refusal(f"RECORD_FILENAME_ID_MISMATCH:{stem}!={rid}")


def load_records(directory: Path = RECORDS) -> list[tuple[Path, dict]]:
    """Every way a file on disk can be hostile is answered with a typed refusal
    here, BEFORE anything downstream assumes a mapping. A record that is a list,
    a number or undecodable bytes must not reach run() and become an
    AttributeError; the loader is the membrane, and main()'s catch-all is only
    the last one."""
    if not directory.is_dir():
        raise Refusal("RECORDS_DIR_MISSING")
    out = []
    for path in sorted(directory.glob("*.json")):
        if path.is_symlink():
            raise Refusal(f"RECORD_SYMLINK:{path.name}")
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise Refusal(f"RECORD_UNREADABLE:{path.name}:{type(exc).__name__}") from exc
        record = strict_loads(text)
        if not isinstance(record, dict):
            raise Refusal(f"RECORD_NOT_AN_OBJECT:{path.name}")
        out.append((path, record))
    return out


def run(directory: Path = RECORDS) -> int:
    records = load_records(directory)
    found = {}
    for path, record in records:
        rid = record.get("id")
        if not isinstance(rid, str) or not rid:
            raise Refusal(f"RECORD_ID_MISSING:{path.name}")
        if rid in found:
            raise Refusal(f"RECORD_ID_DUPLICATE:{rid}")
        found[rid] = path.stem
    check_manifest(found)

    valid = refused = mismatched = 0
    for _, record in sorted(records, key=lambda item: item[1]["id"]):
        rid = record["id"]
        expect = EXPECTED[rid]
        actual, summary = verdict(record)
        if actual != expect:
            print(f"MISMATCH {rid}  expected={expect}  actual={actual}")
            mismatched += 1
        elif actual == "VALID":
            valid += 1
            print(f"VALID    {rid}  subjects={summary['subjects']} scope={summary['scope']} "
                  f"relation={summary['relation']} postconditions-replayed={summary['replayed']}")
        else:
            refused += 1
            print(f"REFUSED  {rid}  {actual.split(':', 1)[1]}  (expected)")
    # No document-level or repository-level retirement badge, by design: this
    # counts records and says nothing about the repository's forgetting.
    print(f"VECTOR   records={len(records)} valid={valid} refused-as-expected={refused} "
          f"mismatched={mismatched} semantic-credit=none")
    return 1 if mismatched else 0


def selftest() -> int:
    loaded = load_records()
    records = {r["id"]: r for _, r in loaded if isinstance(r.get("id"), str)}
    good = records.get("embedded-claims-lineage")
    if good is None:
        raise Refusal("SELFTEST_NEEDS_THE_POSITIVE_FIXTURE")
    controls = []
    # Both entry points answer to the same closed manifest. Otherwise deleting
    # the negative fixture leaves one of them green, and a half-green gate is
    # read as a green one.
    check_manifest({r["id"]: path.stem for path, r in loaded if isinstance(r.get("id"), str)})
    controls.append("live-record-set-matches-manifest")

    def refuses(name, mutate, expected):
        mutant = copy.deepcopy(good)
        mutate(mutant)
        try:
            validate(mutant)
        except Refusal as exc:
            if expected not in str(exc):
                raise AssertionError(f"{name}: wrong refusal {exc}") from exc
            controls.append(name)
            return
        raise AssertionError(f"{name}: mutation survived")

    def manifest_refuses(name, found, expected):
        try:
            check_manifest(found)
        except Refusal as exc:
            if expected not in str(exc):
                raise AssertionError(f"{name}: wrong refusal {exc}") from exc
            controls.append(name)
            return
        raise AssertionError(f"{name}: mutation survived")

    refuses("empty-loss", lambda r: r.__setitem__("loss", []), "LOSS_EMPTY")
    refuses("loss-of-blanks", lambda r: r.__setitem__("loss", ["   "]), "LOSS_EMPTY")
    refuses("subject-digest-drift",
            lambda r: r["subjects"][0].__setitem__("sha256", "0" * 64), "SUBJECT_DIGEST_MISMATCH")
    refuses("subject-absent-at-before-revision",
            lambda r: r["subjects"][0].__setitem__("path", "drafts/NEVER-EXISTED.md"),
            "SUBJECT_ABSENT_AT_BEFORE_REVISION")
    refuses("empty-subjects", lambda r: r.__setitem__("subjects", []), "SUBJECTS_EMPTY")
    refuses("unknown-relation",
            lambda r: r["replacement"].__setitem__("relation", "supersedes"), "RELATION_UNKNOWN")
    refuses("relation-none-with-operands",
            lambda r: r["replacement"].__setitem__("relation", "none"), "RELATION_NONE_CARRIES_OPERANDS")
    refuses("replacement-operand-drift",
            lambda r: r["replacement"]["operands"][0].__setitem__("sha256", "0" * 64),
            "REPLACEMENT_OPERAND:DIGEST_MISMATCH")
    refuses("replacement-operand-shapeless",
            lambda r: r["replacement"]["operands"].append({"path": "README.md"}),
            "REPLACEMENT_OPERAND:SCHEMA")
    refuses("external-without-repository",
            lambda r: r.__setitem__("subject_scope", "external"), "EXTERNAL_SUBJECT_IDENTITY_MISSING")
    refuses("authority-unaddressed",
            lambda r: r["authority"].__setitem__("act", "  "), "AUTHORITY_ACT_UNADDRESSED")
    refuses("applied-tree-drift",
            lambda r: r["applied"].__setitem__("apply_tree", "0" * 40), "APPLY_TREE_MISMATCH")
    refuses("before-revision-unresolvable",
            lambda r: r.__setitem__("before_revision", "0" * 40), "BEFORE_REVISION_UNRESOLVABLE")
    refuses("applied-without-postcondition",
            lambda r: r.__setitem__("postconditions", []), "APPLIED_WITHOUT_POSTCONDITION")
    refuses("dry-run-claiming-applied",
            lambda r: r.__setitem__("status", "DRY_RUN"), "IN_REPO_DRY_RUN_UNSUPPORTED")

    # --- P0: the entrypoint must be what actually runs -----------------------
    refuses("runner-not-allowed",
            lambda r: r["postconditions"][0].__setitem__("runner", "/usr/bin/true"),
            "POSTCONDITION_RUNNER_NOT_ALLOWED")
    refuses("postcondition-supplies-argv",
            lambda r: r["postconditions"][0].__setitem__("argv", ["/usr/bin/true", "x"]),
            "POSTCONDITION_SCHEMA")
    built = postcondition_argv(copy.deepcopy(good)["postconditions"][1])
    post = good["postconditions"][1]
    assert built == ["python3", post["entrypoint"]["path"], *post["args"]], built
    assert built[1] == post["entrypoint"]["path"], "the pinned entrypoint is not what runs"
    controls.append("constructed-argv-runs-the-pinned-entrypoint")

    # --- P1: a missing field is a refusal, not a traceback -------------------
    refuses("required-field-missing",
            lambda r: r.pop("subjects"), "REQUIRED_FIELD_MISSING:subjects")
    refuses("unknown-field", lambda r: r.__setitem__("expect", "VALID"), "RECORD_FIELDS_UNKNOWN")

    # --- P1: the transition itself, not a subject-specific checker's word ----
    still_there = "README.md"
    refuses("subject-present-in-apply-tree",
            lambda r: r["subjects"].append({
                "path": still_there,
                "sha256": historical_digest(r["before_revision"], still_there, "CONTROL"),
                "mode": "ARCHIVED", "reason": "never actually removed by the apply commit"}),
            "SUBJECT_PRESENT_IN_APPLY_TREE")

    # --- P0: the oracle is external and the record set is closed -------------
    manifest_refuses("manifest-record-deleted",
                     {"embedded-claims-lineage": "embedded-claims-lineage"}, "RECORD_MISSING:bos-archive")
    manifest_refuses("manifest-record-smuggled",
                     {**{k: k for k in EXPECTED}, "friendly-extra": "friendly-extra"},
                     "RECORD_NOT_IN_MANIFEST:friendly-extra")
    manifest_refuses("manifest-filename-id-mismatch",
                     {**{k: k for k in EXPECTED}, "bos-archive": "harmless-name"},
                     "RECORD_FILENAME_ID_MISMATCH")

    # --- P1: the loader is the membrane, exercised THROUGH the loader ---------
    def loader_refuses(name, filename, payload, expected):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / filename
            target.write_bytes(payload)
            try:
                load_records(Path(tmp))
            except Refusal as exc:
                if expected not in str(exc):
                    raise AssertionError(f"{name}: wrong refusal {exc}") from exc
                controls.append(name)
                return
            raise AssertionError(f"{name}: mutation survived")

    loader_refuses("loader-non-object-json", "x.json", b'["not", "a", "record"]',
                   "RECORD_NOT_AN_OBJECT")
    loader_refuses("loader-scalar-json", "x.json", b'42', "RECORD_NOT_AN_OBJECT")
    loader_refuses("loader-undecodable-bytes", "x.json", b'\xff\xfe{"id": "x"}',
                   "RECORD_UNREADABLE")
    loader_refuses("loader-malformed-json", "x.json", b'{ broken', "JSON_INVALID")
    loader_refuses("loader-duplicate-key", "x.json", b'{"id": "a", "id": "b"}',
                   "DUPLICATE_JSON_KEY")
    # ...and through run(), which is the entry point a consumer actually calls.
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "rogue.json").write_bytes(b'["not", "a", "record"]')
        try:
            run(Path(tmp))
        except Refusal as exc:
            assert "RECORD_NOT_AN_OBJECT" in str(exc), exc
            controls.append("run-refuses-non-object-record")
        else:
            raise AssertionError("run-refuses-non-object-record: mutation survived")

    # A green postcondition that is not actually run is the label-wider-than-
    # predicate failure in its purest form, so the red path is burned too.
    summary = validate(copy.deepcopy(good))
    with mock.patch.object(subprocess, "run", return_value=subprocess.CompletedProcess([], 1)):
        try:
            replay(summary)
        except Refusal as exc:
            assert "POSTCONDITION_RED" in str(exc)
            controls.append("red-postcondition")
        else:
            raise AssertionError("red-postcondition: mutation survived")

    print(f"ALL PASS ({len(controls)} retirement-record mutation controls)")
    return 0


def main(argv: list[str]) -> int:
    try:
        return selftest() if "--selftest" in argv else run()
    except (Refusal, AssertionError) as exc:
        print(f"REFUSED  {exc}")
        return 1
    except Exception as exc:  # the LAST membrane, never the schema
        # Reaching here means some input found a path the typed checks do not
        # cover. It must still fail closed rather than print a traceback, and it
        # is a defect to be named, not a category to live in.
        print(f"REFUSED  INTERNAL_UNTYPED:{type(exc).__name__}:{exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
