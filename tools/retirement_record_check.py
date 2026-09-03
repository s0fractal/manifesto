#!/usr/bin/env python3
"""Check structured retirement records in drafts/retirement-records/.

This is the narrow general consumer CONTROLLED-FORGETTING-0.1 was missing: it
reads a RetirementRecord as data instead of reading prose about one. It checks
that a record is well formed and that its operands are exactly what it says they
are; it never checks that retiring the subjects was wise.

Deliberately absent: any document-level or repository-level retirement badge.
Output is per record. A VALID record means that record's operands bound and its
postconditions replayed green -- nothing about the repository as a whole.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "drafts" / "retirement-records"
PROFILE = "manifesto.retirement-record@v0.1"
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
REV_RE = re.compile(r"^[0-9a-f]{40}$")
STATUSES = {"APPLIED", "DRY_RUN"}
SCOPES = {"in-repo", "external"}
MODES = {"SUPERSEDED", "WITHDRAWN", "REFUTED", "ARCHIVED", "ABANDONED", "QUARANTINED", "REDACTED"}
RELATIONS = {"replaced-by", "extracted-from", "none"}
ADMISSION_DEFAULT = {"EXCLUDED", "INCLUDED"}
ADMISSION_REVIEW = {"ALLOWED_WITH_STATUS", "FORBIDDEN"}
ADMISSION_NORMATIVE = {"FORBIDDEN_WITHOUT_READOPTION", "FORBIDDEN"}
TOP = {"profile", "id", "status", "expect", "subject_scope", "repository", "before_revision",
       "subjects", "replacement", "loss", "preservation", "admission", "authority",
       "applied", "postconditions"}
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


def string_list(value, code: str) -> list[str]:
    if not isinstance(value, list) or not value:
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


def pinned_operand(operand, code: str) -> tuple[str, str]:
    """A live operand: the file must exist NOW and hash to the recorded digest."""
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
    return rel, expected


def historical_digest(revision: str, rel: str, code: str) -> str:
    """The digest of a RETIRED subject cannot be recomputed from the tree -- the
    file is gone, which is the point. It is recomputed from the object git still
    holds at the before revision, so an operand is exact rather than asserted."""
    proc = subprocess.run(["git", "cat-file", "blob", f"{revision}:{rel}"],
                          cwd=ROOT, capture_output=True)
    if proc.returncode != 0:
        raise Refusal(f"{code}:HISTORICAL_BLOB_UNAVAILABLE:{rel}")
    return hashlib.sha256(proc.stdout).hexdigest()


def check_subjects(record, scope: str, revision):
    subjects = record["subjects"]
    if not isinstance(subjects, list) or not subjects:
        raise Refusal("SUBJECTS_EMPTY")
    seen = set()
    for subject in subjects:
        if not isinstance(subject, dict):
            raise Refusal("SUBJECT_NOT_AN_OBJECT")
        mode = subject.get("mode")
        if mode not in MODES:
            raise Refusal(f"SUBJECT_MODE_UNKNOWN:{mode!r}")
        nonempty(subject.get("reason"), "SUBJECT_REASON_EMPTY")
        if scope == "in-repo":
            if set(subject) != {"path", "sha256", "mode", "reason"}:
                raise Refusal("SUBJECT_FIELDS_NOT_CLOSED")
            rel, expected = subject["path"], subject["sha256"]
            in_repo_path(rel, "SUBJECT")
            if not isinstance(expected, str) or not HEX64_RE.fullmatch(expected):
                raise Refusal(f"SUBJECT_PIN_INVALID:{rel}")
            if (ROOT / rel).exists():
                raise Refusal(f"RETIRED_SUBJECT_STILL_PRESENT:{rel}")
            actual = historical_digest(revision, rel, "SUBJECT")
            if actual != expected:
                raise Refusal(f"SUBJECT_DIGEST_MISMATCH:{rel}")
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


def check_postconditions(record, status: str):
    posts = record["postconditions"]
    if not isinstance(posts, list):
        raise Refusal("POSTCONDITIONS_SCHEMA")
    if status == "DRY_RUN":
        if posts:
            raise Refusal("DRY_RUN_CARRIES_POSTCONDITIONS")
        return []
    if not posts:
        # An applied retirement whose only evidence is prose is the failure this
        # whole discipline exists to stop being.
        raise Refusal("APPLIED_WITHOUT_POSTCONDITION")
    checked = []
    for post in posts:
        if not isinstance(post, dict) or set(post) != {"argv", "entrypoint", "falsifier"}:
            raise Refusal("POSTCONDITION_SCHEMA")
        argv = post["argv"]
        if not isinstance(argv, list) or not argv or not all(isinstance(a, str) and a for a in argv):
            raise Refusal("POSTCONDITION_ARGV_INVALID")
        if any(ch in arg for arg in argv for ch in "|;&><$`"):
            # argv is a structured operand list, not a shell string
            raise Refusal("POSTCONDITION_ARGV_LOOKS_LIKE_SHELL")
        nonempty(post["falsifier"], "POSTCONDITION_FALSIFIER_EMPTY")
        rel, _ = pinned_operand(post["entrypoint"], "POSTCONDITION_ENTRYPOINT")
        if rel not in argv:
            raise Refusal(f"POSTCONDITION_ENTRYPOINT_UNBOUND:{rel}")
        checked.append(argv)
    return checked


def validate(record) -> dict:
    if not isinstance(record, dict):
        raise Refusal("RECORD_NOT_AN_OBJECT")
    if record.get("profile") != PROFILE:
        raise Refusal("PROFILE_UNKNOWN")
    if set(record) - TOP:
        raise Refusal(f"RECORD_FIELDS_UNKNOWN:{sorted(set(record) - TOP)}")
    rid = record.get("id")
    if not isinstance(rid, str) or not ID_RE.fullmatch(rid):
        raise Refusal(f"RECORD_ID_INVALID:{rid!r}")
    status = record.get("status")
    if status not in STATUSES:
        raise Refusal(f"STATUS_UNKNOWN:{status!r}")
    scope = record.get("subject_scope")
    if scope not in SCOPES:
        raise Refusal(f"SUBJECT_SCOPE_UNKNOWN:{scope!r}")

    # Identity first (I1). The whole point of the BOS trial: a repository-shaped
    # external subject binds by declaration or not at all -- containment cannot
    # supply an identity that lives somewhere else.
    repository = record.get("repository")
    if scope == "external":
        if repository is None or not (isinstance(repository, str) and repository.strip()):
            raise Refusal("EXTERNAL_SUBJECT_IDENTITY_MISSING")
    elif repository is not None:
        raise Refusal("IN_REPO_SUBJECT_DECLARES_REPOSITORY")

    revision = record.get("before_revision")
    if scope == "in-repo":
        if not isinstance(revision, str) or not REV_RE.fullmatch(revision):
            raise Refusal("BEFORE_REVISION_INVALID")
        if subprocess.run(["git", "cat-file", "-e", f"{revision}^{{commit}}"],
                          cwd=ROOT, capture_output=True).returncode != 0:
            raise Refusal(f"BEFORE_REVISION_UNRESOLVABLE:{revision}")
    elif revision is not None:
        raise Refusal("EXTERNAL_SUBJECT_DECLARES_LOCAL_REVISION")

    count = check_subjects(record, scope, revision)

    replacement = record.get("replacement")
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
    # Operand shape follows the OPERAND, not the subject: a replacement living in
    # this repository is pinnable even when the thing retired was external, and
    # pretending otherwise would throw away an exact digest we actually hold.
    for operand in operands:
        if isinstance(operand, dict) and set(operand) == {"path", "sha256"}:
            pinned_operand(operand, "REPLACEMENT_OPERAND")
        elif isinstance(operand, dict) and set(operand) == {"locator", "note"}:
            nonempty(operand["locator"], "REPLACEMENT_OPERAND:LOCATOR_EMPTY")
            nonempty(operand["note"], "REPLACEMENT_OPERAND:NOTE_EMPTY")
        else:
            raise Refusal("REPLACEMENT_OPERAND:SCHEMA")

    # Loss is mandatory for every mode and every status. There is no shape of
    # retirement that loses nothing; an empty list is unmeasured, not zero.
    string_list(record.get("loss"), "LOSS_EMPTY")

    preservation = record.get("preservation")
    if not isinstance(preservation, dict) or set(preservation) != {"policy", "locator"}:
        raise Refusal("PRESERVATION_SCHEMA")
    nonempty(preservation["policy"], "PRESERVATION_POLICY_EMPTY")
    nonempty(preservation["locator"], "PRESERVATION_LOCATOR_EMPTY")

    admission = record.get("admission")
    if not isinstance(admission, dict) or set(admission) != {"default", "historical_review", "normative_use"}:
        raise Refusal("ADMISSION_SCHEMA")
    if admission["default"] not in ADMISSION_DEFAULT:
        raise Refusal("ADMISSION_DEFAULT_UNKNOWN")
    if admission["historical_review"] not in ADMISSION_REVIEW:
        raise Refusal("ADMISSION_REVIEW_UNKNOWN")
    if admission["normative_use"] not in ADMISSION_NORMATIVE:
        raise Refusal("ADMISSION_NORMATIVE_UNKNOWN")

    authority = record.get("authority")
    applied = record.get("applied")
    if status == "APPLIED":
        # An ADDRESS for the act, not a proof that the act was within anyone's
        # power. This checker never certifies legitimacy; I6 stays a governance
        # question, and the record only has to say where to look.
        if not isinstance(authority, dict) or set(authority) != {"owner", "act"}:
            raise Refusal("AUTHORITY_SCHEMA")
        nonempty(authority["owner"], "AUTHORITY_OWNER_EMPTY")
        nonempty(authority["act"], "AUTHORITY_ACT_UNADDRESSED")
        if not isinstance(applied, dict) or set(applied) != {"apply_commit", "apply_tree", "receipt"}:
            raise Refusal("APPLIED_SCHEMA")
        for field in ("apply_commit", "apply_tree"):
            if not REV_RE.fullmatch(applied[field] if isinstance(applied[field], str) else ""):
                raise Refusal(f"APPLIED_{field.upper()}_INVALID")
        nonempty(applied["receipt"], "APPLIED_RECEIPT_EMPTY")
        parent = subprocess.run(["git", "rev-parse", f"{applied['apply_commit']}^"],
                                cwd=ROOT, capture_output=True, text=True)
        if parent.returncode != 0 or parent.stdout.strip() != revision:
            raise Refusal("APPLY_COMMIT_NOT_CHILD_OF_BEFORE_REVISION")
        tree = subprocess.run(["git", "rev-parse", f"{applied['apply_commit']}^{{tree}}"],
                              cwd=ROOT, capture_output=True, text=True)
        if tree.returncode != 0 or tree.stdout.strip() != applied["apply_tree"]:
            raise Refusal("APPLY_TREE_MISMATCH")
    else:
        if authority is not None:
            raise Refusal("DRY_RUN_CLAIMS_AUTHORITY")
        if applied is not None:
            raise Refusal("DRY_RUN_CLAIMS_APPLIED")

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


def verdict(record) -> tuple[str, str, dict | None]:
    try:
        summary = validate(record)
    except Refusal as exc:
        return "REFUSED", str(exc), None
    try:
        replayed = replay(summary)
    except Refusal as exc:
        return "REFUSED", str(exc), None
    summary["replayed"] = replayed
    return "VALID", "", summary


def load_records() -> list[tuple[Path, dict]]:
    if not RECORDS.is_dir():
        raise Refusal("RECORDS_DIR_MISSING")
    out = []
    for path in sorted(RECORDS.glob("*.json")):
        if path.is_symlink():
            raise Refusal(f"RECORD_SYMLINK:{path.name}")
        out.append((path, strict_loads(path.read_text(encoding="utf-8"))))
    if not out:
        raise Refusal("RECORDS_EMPTY")
    return out


def expectation(record) -> str:
    expect = record.get("expect")
    if not isinstance(expect, str) or not expect.strip():
        raise Refusal("EXPECT_MISSING")
    if expect != "VALID" and not expect.startswith("REFUSED:"):
        raise Refusal(f"EXPECT_MALFORMED:{expect}")
    return expect


def run() -> int:
    records = load_records()
    valid = refused = mismatched = 0
    for path, record in records:
        try:
            expect = expectation(record)
        except Refusal as exc:
            print(f"MISMATCH {path.name}  {exc}")
            mismatched += 1
            continue
        state, reason, summary = verdict(record)
        actual = "VALID" if state == "VALID" else f"REFUSED:{reason}"
        rid = record.get("id", path.stem)
        if actual != expect:
            print(f"MISMATCH {rid}  expected={expect}  actual={actual}")
            mismatched += 1
            continue
        if state == "VALID":
            valid += 1
            print(f"VALID    {rid}  subjects={summary['subjects']} scope={summary['scope']} "
                  f"relation={summary['relation']} postconditions-replayed={summary['replayed']}")
        else:
            refused += 1
            print(f"REFUSED  {rid}  {reason}  (expected)")
    # No document-level or repository-level retirement badge, by design: this
    # line counts records, and says nothing about the repository's forgetting.
    print(f"VECTOR   records={len(records)} valid={valid} refused-as-expected={refused} "
          f"mismatched={mismatched} semantic-credit=none")
    return 1 if mismatched else 0


def selftest() -> int:
    records = dict((r.get("id"), r) for _, r in load_records())
    good = records.get("embedded-claims-lineage")
    if good is None:
        raise Refusal("SELFTEST_NEEDS_THE_POSITIVE_FIXTURE")
    controls = []

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

    refuses("empty-loss", lambda r: r.__setitem__("loss", []), "LOSS_EMPTY")
    refuses("loss-of-blanks", lambda r: r.__setitem__("loss", ["   "]), "LOSS_EMPTY")
    refuses("subject-digest-drift",
            lambda r: r["subjects"][0].__setitem__("sha256", "0" * 64), "SUBJECT_DIGEST_MISMATCH")
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
    refuses("applied-commit-reparented",
            lambda r: r.__setitem__("before_revision", "0" * 40), "BEFORE_REVISION_UNRESOLVABLE")
    refuses("applied-without-postcondition",
            lambda r: r.__setitem__("postconditions", []), "APPLIED_WITHOUT_POSTCONDITION")
    refuses("postcondition-entrypoint-unbound",
            lambda r: r["postconditions"][0].__setitem__("argv", ["python3", "-c", "pass"]),
            "POSTCONDITION_ENTRYPOINT_UNBOUND")
    refuses("postcondition-as-shell-string",
            lambda r: r["postconditions"][0]["argv"].append("&& rm -rf /"),
            "POSTCONDITION_ARGV_LOOKS_LIKE_SHELL")
    refuses("dry-run-claiming-applied",
            lambda r: r.__setitem__("status", "DRY_RUN"), "DRY_RUN_CLAIMS_AUTHORITY")
    refuses("retired-subject-resurrected",
            lambda r: r["subjects"].append({"path": "README.md", "sha256": "0" * 64,
                                            "mode": "ARCHIVED", "reason": "resurrected"}),
            "RETIRED_SUBJECT_STILL_PRESENT")

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


if __name__ == "__main__":
    sys.exit(main(sys.argv))
