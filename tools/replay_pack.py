#!/usr/bin/env python3
"""Replay a dependency-bound pack, and — separately — check it for drift.

    python3 tools/replay_pack.py build  <pack> --evaluator <wheel>
    python3 tools/replay_pack.py replay <pack> --evaluator <wheel>
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
    """`(pack, problem)`. A missing file and an unreadable one are different."""
    path = Path(pack_dir) / "pack.json"
    if not path.is_file():
        return None, None
    try:
        return json.loads(path.read_text()), None
    except (ValueError, OSError) as failure:
        return None, f"pack.json is present but cannot be read: {failure}"


def classify(pack_dir):
    """`(pack, verdict_or_None, reason)`.

    A pack with no `pack.json` at all is LEGACY — it predates the format. A
    pack that CLAIMS this format and is broken is MALFORMED, which is a
    different thing and must not be filed under history.
    """
    pack, unreadable = load(pack_dir)
    if unreadable:
        # A pack.json that exists and is broken is a DEFECT, not an era. Filing
        # it as legacy would put a corrupted new pack in the same bucket as a
        # settlement taken before the format existed.
        return None, MALFORMED_PACK, unreadable
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
    """The digest of a WHEEL. A receipt is not accepted as the artifact.

    `--evaluator` used to take any JSON carrying `artifact_sha256`, so the
    operand and the engine could be different things entirely: with the wheel of
    one commit installed and the receipt of another supplied, replay still said
    `MATCH`. A receipt describes an artifact; it is not one, and it is not
    accepted here. What is checked and what executes must be the same bytes.

    The pack carries its own expected digest, so no second operand is needed: a
    receipt may be what a reader consults to learn which wheel to fetch, but it
    never stands in for the wheel at replay time.
    """
    path = Path(operand)
    if not path.is_file():
        return None, f"the evaluator operand {operand} is not a file"
    if path.suffix != ".whl" or not zipfile.is_zipfile(path):
        return None, (f"the evaluator operand must be a wheel; {operand} is "
                      f"not one. A receipt describes an artifact and cannot "
                      f"stand in for it")
    return sha256(path.read_bytes()), None


def wheel_distribution(wheel):
    """`(name, version)` from the wheel's own METADATA."""
    with zipfile.ZipFile(wheel) as archive:
        meta = [n for n in archive.namelist()
                if n.endswith(".dist-info/METADATA")]
        if not meta:
            return None, None
        text = archive.read(meta[0]).decode()
    name = version = None
    for line in text.splitlines():
        if line.startswith("Name: "):
            name = line[6:].strip()
        elif line.startswith("Version: "):
            version = line[9:].strip()
        elif not line.strip():
            break
    return name, version


def executing_module_is(wheel, module):
    """Does the engine about to run come from THIS wheel?

    Comparing digests proves something about a file on disk. It proves nothing
    about the interpreter that is about to execute, which imports whatever is
    installed — so with wheel A supplied and wheel B installed, replay said
    `MATCH`.

    Two things are compared, and the second is why one is not enough. The module
    BYTES must be those the wheel carries; and the INSTALLED DISTRIBUTION must
    be the wheel's own name and version. Two candidate wheels built from
    different commits can carry a byte-identical `sigma_glyph.py` — the module
    did not change between them — so bytes alone cannot tell which artifact is
    installed. The version can: it carries the source commit.
    """
    installed = Path(getattr(module, "__file__", "") or "")
    if not installed.is_file():
        return "the imported evaluator has no readable file to compare"
    member = installed.name
    with zipfile.ZipFile(wheel) as archive:
        if member not in archive.namelist():
            return (f"the wheel does not carry {member}, so the running module "
                    f"cannot have come from it")
        carried = archive.read(member)
    if carried != installed.read_bytes():
        return (f"the running {member} ({sha256(installed.read_bytes())[:16]}…) "
                f"is not the one in the supplied wheel "
                f"({sha256(carried)[:16]}…): the operand and the engine are "
                f"different artifacts")

    name, version = wheel_distribution(wheel)
    if not name:
        return f"the wheel {wheel} carries no METADATA to identify it by"
    try:
        import importlib.metadata as metadata
        found = metadata.version(name)
    except Exception as failure:                      # noqa: BLE001 - reported
        return (f"cannot determine which distribution provides the running "
                f"evaluator: {failure}")
    if found != version:
        return (f"the running evaluator is {name} {found}, the supplied wheel "
                f"is {name} {version}. The module bytes happen to agree — they "
                f"are identical between these two artifacts — but the installed "
                f"distribution is a different one")
    return None


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

    # The wheel checked must be the engine that runs. Importing here, before any
    # settlement, so the comparison is against the module that will do the work.
    from sigma_boundary import sigma
    mismatch = executing_module_is(Path(evaluator), sigma())
    if mismatch:
        return EVALUATOR_MISMATCH, mismatch

    if runtime.get("profile_id") != PROFILE_ID:
        return PROFILE_MISMATCH, (
            f"the pack names profile {runtime.get('profile_id')!r}; this tool "
            f"implements {PROFILE_ID!r}. A pack may not choose which profile "
            f"it is replayed under")
    declared = {source["path"] for source in runtime.get("profile_sources", [])}
    if declared != set(PROFILE_SOURCES):
        return PROFILE_MISMATCH, (
            f"the pack pins {sorted(declared)}; this profile is defined by "
            f"{sorted(PROFILE_SOURCES)}. Checking only what the pack chose to "
            f"list means an empty list checks nothing")

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
        current, refusal = contained(ROOT, dependency.get("dependency_id"),
                                     "dependency_id")
        if refusal:
            return _say("DRIFT", MALFORMED_PACK, refusal)
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
    ap.add_argument("--evaluator",
                    help="the wheel that is installed in this interpreter; a "
                         "receipt is not accepted as an artifact")
    args = ap.parse_args()
    if args.command == "build":
        return build(args.pack, args.evaluator)
    if args.command == "replay":
        return 0 if replay(args.pack, args.evaluator) == MATCH else 1
    return 0 if drift(args.pack) == SAME else 1


if __name__ == "__main__":
    raise SystemExit(main())
