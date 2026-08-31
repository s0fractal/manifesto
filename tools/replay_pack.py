#!/usr/bin/env python3
"""Replay a dependency-bound pack, and — separately — check it for drift.

    python3 tools/replay_pack.py build  <pack> --evaluator <receipt-or-wheel>
    python3 tools/replay_pack.py replay <pack> --evaluator <receipt-or-wheel>
    python3 tools/replay_pack.py drift  <pack>

NON-NORMATIVE, and deliberately small: enough for one fixture, not a general
evidence framework.

TWO OPERATIONS, NEVER ONE ENUM
------------------------------
    replay -> MATCH | REPLAY_MISMATCH | DEPENDENCY_MISSING | EVALUATOR_UNVERIFIED
              | EVALUATOR_MISMATCH | PROFILE_MISMATCH | MALFORMED_PACK
              | LEGACY_UNPINNED
    drift  -> SAME  | DRIFT | CURRENT_MISSING | MALFORMED_PACK | LEGACY_UNPINNED

`replay` reads ONLY the bytes the pack pinned; it never opens the current
checkout. `drift` reads the current checkout and says whether it still matches.
Both can be true at once — `replay = MATCH` with `drift = DRIFT` is normal —
and neither is `REFUTED`. `REFUTED` would mean the subject predicate is false on
the operands the pack itself declared, which is `REPLAY_MISMATCH` here.

WHAT `MATCH` NOW REQUIRES, AND DID NOT
--------------------------------------
Three holes made `MATCH` cheap, and each is closed by something checked rather
than described:

1. The pack recorded `evaluator_artifact_sha256` and NOTHING READ IT. Setting it
   to `ffff…` still produced `MATCH`. Replay now takes the evaluator as an
   explicit operand and compares its digest to the pinned one BEFORE executing
   anything; an absent or mismatched evaluator is a named refusal.
2. `profile_id` was a name with nothing behind it. The pack now pins the digests
   of the sources that DEFINE the profile — the boundary, the settlement
   library, and this file — and a change to any of them is `PROFILE_MISMATCH`.
3. Only three receipt fields were compared, so corrupting `rhs_nf` still gave
   `MATCH`. The comparison is now a CLOSED list: every recorded field must be
   present and equal, and an unexpected field is itself a mismatch.

Dependency paths are contained: relative, canonical, inside the pack, symlinks
that escape refused. `embedded_path` was used as given, so a blob deleted from
the pack and replaced by an absolute path to a file next door still replayed
`MATCH` — which made "reads only bytes carried inside the pack" false.
"""
import argparse
import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = Path(__file__).resolve().parents[1]
PACK_KIND = "manifesto/replay-pack@v0"

MATCH, REPLAY_MISMATCH = "MATCH", "REPLAY_MISMATCH"
DEPENDENCY_MISSING, LEGACY_UNPINNED = "DEPENDENCY_MISSING", "LEGACY_UNPINNED"
EVALUATOR_UNVERIFIED = "EVALUATOR_UNVERIFIED"
EVALUATOR_MISMATCH, PROFILE_MISMATCH = "EVALUATOR_MISMATCH", "PROFILE_MISMATCH"
MALFORMED_PACK = "MALFORMED_PACK"
SAME, DRIFT, CURRENT_MISSING = "SAME", "DRIFT", "CURRENT_MISSING"

# The sources that DEFINE what `profile_id` means here. A profile named but not
# pinned is a label; these are what a reader would have to read to know what was
# executed.
PROFILE_SOURCES = ("tools/sigma_boundary.py", "tools/glyphlib.py",
                   "tools/replay_pack.py")
PROFILE_ID = "manifesto/glyphlib/settle_nat_eq@v0"

# Closed. Every one must be present and equal; anything else recorded is itself
# a mismatch, so a field cannot be added without the comparison noticing.
RECEIPT_FIELDS = ("verdict", "atp_spent", "lhs_nf", "rhs_nf")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def count_token(data, token):
    """The subject predicate's operand: how often `token` occurs in `data`."""
    return data.decode("utf-8").count(token)


def contained(root, relative, what):
    """`root/relative`, or a refusal. Relative, canonical, inside `root`."""
    if not isinstance(relative, str) or not relative:
        return None, f"{what} is not a path: {relative!r}"
    if os.path.isabs(relative):
        return None, f"{what} must be relative to the pack, not absolute: {relative!r}"
    if os.pardir in Path(relative).parts:
        return None, f"{what} may not traverse upwards: {relative!r}"
    target = Path(root) / relative
    try:
        resolved = target.resolve()
    except OSError as failure:
        return None, f"{what} cannot be resolved: {failure}"
    base = Path(root).resolve()
    if base != resolved and base not in resolved.parents:
        return None, (f"{what} resolves outside the pack ({resolved}); a symlink "
                      f"leaving the pack is refused, not followed")
    return resolved, None


def load(pack_dir):
    path = Path(pack_dir) / "pack.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text())
    except ValueError:
        return None


def classify(pack_dir):
    """`(pack, verdict_or_None, reason)`.

    A pack with no `pack.json` at all is LEGACY — it predates the format. A
    pack that CLAIMS this format and is broken is MALFORMED, which is a
    different thing and must not be filed under history.
    """
    pack = load(pack_dir)
    if pack is None:
        return None, LEGACY_UNPINNED, (
            "this pack recorded no dependency closure, so the bytes its "
            "settlement rested on are not available. A strict replay is "
            "impossible, and reading today's files instead would be a "
            "different operation with a different meaning")
    if pack.get("kind") != PACK_KIND:
        return None, LEGACY_UNPINNED, (
            f"this pack is not {PACK_KIND}; it predates pinned dependencies")

    for field in ("subject", "dependencies", "runtime", "computation"):
        if field not in pack:
            return None, MALFORMED_PACK, (
                f"the pack claims {PACK_KIND} but has no {field!r}. A broken "
                f"pack of this format is not a historical one")

    seen = set()
    for dependency in pack["dependencies"]:
        identifier = dependency.get("dependency_id")
        if identifier in seen:
            return None, MALFORMED_PACK, (
                f"duplicate dependency_id {identifier!r}: which of the two "
                f"entries a replay used would not be determined")
        seen.add(identifier)
    subject_id = pack["subject"].get("dependency_id")
    if list(seen).count(subject_id) != 1 and subject_id not in seen:
        return None, MALFORMED_PACK, (
            f"the subject names {subject_id!r}, which is not among the pinned "
            f"dependencies")
    return pack, None, ""


def evaluator_digest(operand):
    """The artifact digest an operand names: a wheel, or a receipt naming one."""
    path = Path(operand)
    if not path.exists():
        return None, f"the evaluator operand {operand} does not exist"
    if path.is_file() and path.suffix == ".whl":
        if not zipfile.is_zipfile(path):
            return None, f"{operand} is not a wheel"
        return sha256(path.read_bytes()), None
    if path.is_dir():
        path = path / "candidate-receipt.json"
    try:
        document = json.loads(Path(path).read_text())
    except (OSError, ValueError) as failure:
        return None, f"cannot read an artifact digest from {operand}: {failure}"
    digest = document.get("artifact_sha256")
    if not digest:
        return None, f"{operand} records no artifact_sha256"
    return digest, None


def _say(operation, verdict, reason=""):
    if reason:
        print(f"  {verdict}: {reason}")
    print(f"{operation}: {verdict}")
    return verdict


def _check_runtime(pack, evaluator):
    """Evaluator and profile, both pinned, both checked before execution."""
    runtime = pack["runtime"]
    if evaluator is None:
        return EVALUATOR_UNVERIFIED, (
            f"this pack pins evaluator artifact "
            f"{runtime['evaluator_artifact_sha256'][:16]}…, and no evaluator "
            f"was supplied to check against it. Pass --evaluator; replaying "
            f"against whatever happens to be installed would be a different "
            f"claim")
    digest, refusal = evaluator_digest(evaluator)
    if refusal:
        return EVALUATOR_UNVERIFIED, refusal
    if digest != runtime["evaluator_artifact_sha256"]:
        return EVALUATOR_MISMATCH, (
            f"the pack was settled with artifact "
            f"{runtime['evaluator_artifact_sha256'][:16]}…, the supplied "
            f"evaluator is {digest[:16]}…")

    for source in runtime["profile_sources"]:
        current = ROOT / source["path"]
        if not current.is_file():
            return PROFILE_MISMATCH, (f"{source['path']} defines this profile "
                                      f"and is not in the checkout")
        now = sha256(current.read_bytes())
        if now != source["sha256"]:
            return PROFILE_MISMATCH, (
                f"{source['path']} defines this profile and has changed: pinned "
                f"{source['sha256'][:16]}…, now {now[:16]}…. `profile_id` alone "
                f"is a label; these digests are what it means")
    return None, ""


def _check_dependencies(pack, pack_dir):
    for dependency in pack["dependencies"]:
        blob, refusal = contained(pack_dir, dependency.get("embedded_path"),
                                  f"embedded_path for "
                                  f"{dependency.get('dependency_id')}")
        if refusal:
            return MALFORMED_PACK, refusal, None
        if not blob.is_file():
            return DEPENDENCY_MISSING, (
                f"{dependency['dependency_id']} is pinned at "
                f"{dependency['sha256'][:16]}… but "
                f"{dependency['embedded_path']} is not in the pack"), None
        data = blob.read_bytes()
        if sha256(data) != dependency["sha256"]:
            return REPLAY_MISMATCH, (
                f"the embedded bytes for {dependency['dependency_id']} hash to "
                f"{sha256(data)[:16]}…, the pack pins "
                f"{dependency['sha256'][:16]}…"), None
    return None, "", True


def _compare_receipt(recorded, produced):
    """Closed comparison: same field set, every value equal."""
    if set(recorded) != set(RECEIPT_FIELDS):
        return (f"the recorded receipt has fields {sorted(recorded)}, this "
                f"format's closed set is {sorted(RECEIPT_FIELDS)}")
    for field in RECEIPT_FIELDS:
        if recorded[field] != produced[field]:
            return (f"receipt field {field!r}: pack records "
                    f"{recorded[field]!r}, re-execution gives "
                    f"{produced[field]!r}")
    return None


def build(pack_dir, evaluator, token="FLOW"):
    """Write a pack whose dependency bytes and runtime both travel with it."""
    from glyphlib import church, settle_nat_eq

    digest, refusal = evaluator_digest(evaluator)
    if refusal:
        print(f"REPLAY-PACK: {refusal}", file=sys.stderr)
        return 1

    pack_dir = Path(pack_dir)
    (pack_dir / "blobs").mkdir(parents=True, exist_ok=True)
    dependency = "drafts/replay-fixture-0.1/source.md"
    data = (ROOT / dependency).read_bytes()
    blob_digest = sha256(data)
    (pack_dir / "blobs" / blob_digest).write_bytes(data)

    occurrences = count_token(data, token)
    budget = 5_000_000
    verdict, atp, meta = settle_nat_eq(church(occurrences), church(occurrences),
                                       budget)
    head = os.popen("git -C %s rev-parse HEAD" % ROOT).read().strip()  # noqa

    pack = {
        "kind": PACK_KIND,
        "subject": {
            "predicate": "count_token",
            "token": token,
            "dependency_id": dependency,
            "claimed_occurrences": occurrences,
        },
        "dependencies": [
            {"dependency_id": dependency,
             "sha256": blob_digest,
             "embedded_path": f"blobs/{blob_digest}"},
        ],
        "runtime": {
            "evaluator_artifact_sha256": digest,
            "consumer_commit": head,
            "profile_id": PROFILE_ID,
            "profile_sources": [
                {"path": path, "sha256": sha256((ROOT / path).read_bytes())}
                for path in PROFILE_SOURCES],
        },
        "computation": {
            "budget": budget,
            "receipt": {"verdict": verdict, "atp_spent": atp,
                        "lhs_nf": meta["lhs"]["expect"],
                        "rhs_nf": meta["rhs"]["expect"]},
        },
    }
    (pack_dir / "pack.json").write_text(json.dumps(pack, indent=2) + "\n")
    print(f"  dependency  {dependency}  sha256 {blob_digest[:16]}…")
    print(f"  evaluator   {digest[:16]}…")
    print(f"  claim       {token} occurs {occurrences} times")
    print(f"  receipt     {verdict}  {atp} ATP")
    print(f"REPLAY-PACK: built {pack_dir}")
    return 0


def replay(pack_dir, evaluator=None):
    """Only the pinned bytes, and only the pinned evaluator and profile."""
    pack_dir = Path(pack_dir)
    pack, verdict, reason = classify(pack_dir)
    if verdict:
        return _say("REPLAY", verdict, reason)

    verdict, reason = _check_runtime(pack, evaluator)
    if verdict:
        return _say("REPLAY", verdict, reason)

    verdict, reason, _ok = _check_dependencies(pack, pack_dir)
    if verdict:
        return _say("REPLAY", verdict, reason)

    subject = pack["subject"]
    blob, _ = contained(pack_dir,
                        next(d["embedded_path"] for d in pack["dependencies"]
                             if d["dependency_id"] == subject["dependency_id"]),
                        "subject dependency")
    occurrences = count_token(blob.read_bytes(), subject["token"])
    if occurrences != subject["claimed_occurrences"]:
        return _say("REPLAY", REPLAY_MISMATCH,
                    f"the pack claims {subject['token']} occurs "
                    f"{subject['claimed_occurrences']} times in the pinned "
                    f"bytes; it occurs {occurrences}")

    from glyphlib import church, settle_nat_eq
    computation = pack["computation"]
    got_verdict, atp, meta = settle_nat_eq(church(occurrences),
                                           church(occurrences),
                                           computation["budget"])
    produced = {"verdict": got_verdict, "atp_spent": atp,
                "lhs_nf": meta["lhs"]["expect"], "rhs_nf": meta["rhs"]["expect"]}
    problem = _compare_receipt(computation["receipt"], produced)
    if problem:
        return _say("REPLAY", REPLAY_MISMATCH, problem)

    print(f"  the pinned bytes, the pinned evaluator and the pinned profile "
          f"reproduce the recorded receipt: {got_verdict}, {atp} ATP, "
          f"{subject['token']} × {occurrences}")
    return _say("REPLAY", MATCH)


def drift(pack_dir):
    """The pinned bytes against the current checkout. A separate question."""
    pack_dir = Path(pack_dir)
    pack, verdict, reason = classify(pack_dir)
    if verdict:
        return _say("DRIFT", verdict,
                    reason if verdict != LEGACY_UNPINNED else
                    "nothing was pinned, so there is nothing to compare the "
                    "current checkout against")

    outcome = SAME
    for dependency in pack["dependencies"]:
        current = ROOT / dependency["dependency_id"]
        if not current.is_file():
            print(f"  {CURRENT_MISSING}: {dependency['dependency_id']} is not "
                  f"in the checkout any more")
            outcome = CURRENT_MISSING
            continue
        now = sha256(current.read_bytes())
        if now != dependency["sha256"]:
            print(f"  {DRIFT}: {dependency['dependency_id']} was "
                  f"{dependency['sha256'][:16]}… when pinned, is {now[:16]}… now")
            if outcome == SAME:
                outcome = DRIFT
        else:
            print(f"  {SAME}: {dependency['dependency_id']} is unchanged")
    print(f"DRIFT: {outcome}")
    return outcome


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=("build", "replay", "drift"))
    ap.add_argument("pack")
    ap.add_argument("--evaluator", help="a wheel, or a receipt naming one")
    args = ap.parse_args()
    if args.command == "build":
        return build(args.pack, args.evaluator)
    if args.command == "replay":
        return 0 if replay(args.pack, args.evaluator) == MATCH else 1
    return 0 if drift(args.pack) == SAME else 1


if __name__ == "__main__":
    raise SystemExit(main())
