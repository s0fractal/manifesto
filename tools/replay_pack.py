#!/usr/bin/env python3
"""Replay a dependency-bound pack, and — separately — check it for drift.

    python3 tools/replay_pack.py build   <pack-dir>
    python3 tools/replay_pack.py replay  <pack-dir>
    python3 tools/replay_pack.py drift   <pack-dir>

NON-NORMATIVE, and deliberately small: enough for one fixture, not a general
evidence framework.

TWO OPERATIONS, NEVER ONE ENUM
------------------------------
    replay(pack)  -> MATCH | REPLAY_MISMATCH | DEPENDENCY_MISSING | LEGACY_UNPINNED
    drift(pack)   -> SAME  | DRIFT           | CURRENT_MISSING

`replay` reads ONLY the bytes the pack pinned. It never opens the current
checkout, so a file edited afterwards cannot change a historical verdict.
`drift` reads the current checkout and says whether it still matches what was
pinned. Both can be true at once, and that combination is normal:

    historical replay = MATCH,  current checkout = DRIFT

Neither, alone or together, is `REFUTED`. `REFUTED` would mean the subject
predicate is false on the operands the pack itself declared — which is a
statement `replay` can make, and `drift` cannot.

WHY THE OLD PACKS CANNOT BE REPLAYED
------------------------------------
The sealed SSD pack recorded no dependency closure. Its settlement was real,
its numbers were real, and the bytes it depended on were never written down. So
a strict replay is impossible, and pretending otherwise would mean inventing a
history. Such a pack is refused with `LEGACY_UNPINNED`. The tool does not read
current files and call the difference `REFUTED`; that conflation is the defect
this format exists to remove.
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = Path(__file__).resolve().parents[1]
PACK_KIND = "manifesto/replay-pack@v0"

MATCH, REPLAY_MISMATCH = "MATCH", "REPLAY_MISMATCH"
DEPENDENCY_MISSING, LEGACY_UNPINNED = "DEPENDENCY_MISSING", "LEGACY_UNPINNED"
SAME, DRIFT, CURRENT_MISSING = "SAME", "DRIFT", "CURRENT_MISSING"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def count_token(data, token):
    """The subject predicate's operand: how often `token` occurs in `data`."""
    return data.decode("utf-8").count(token)


def load(pack_dir):
    path = Path(pack_dir) / "pack.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text())
    except ValueError:
        return None


def is_legacy(pack_dir):
    """A pack that predates pinned dependencies, recognised by what it lacks."""
    pack = load(pack_dir)
    if pack is not None and pack.get("kind") == PACK_KIND:
        return False
    return True


def build(pack_dir, token="FLOW"):
    """Write a pack whose dependency bytes travel inside it."""
    from glyphlib import church, settle_nat_eq

    pack_dir = Path(pack_dir)
    (pack_dir / "blobs").mkdir(parents=True, exist_ok=True)
    dependency = "drafts/replay-fixture-0.1/source.md"
    data = (ROOT / dependency).read_bytes()
    digest = sha256(data)
    (pack_dir / "blobs" / digest).write_bytes(data)

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
             "sha256": digest,
             "embedded_path": f"blobs/{digest}"},
        ],
        "computation": {
            "evaluator_artifact_sha256": os.environ.get(
                "SIGMA_ARTIFACT_SHA256", "not-recorded-in-this-fixture"),
            "profile_id": "manifesto/glyphlib/settle_nat_eq@v0",
            "budget": budget,
            "receipt": {"verdict": verdict, "atp_spent": atp,
                        "lhs_nf": meta["lhs"]["expect"],
                        "rhs_nf": meta["rhs"]["expect"]},
        },
    }
    (pack_dir / "pack.json").write_text(json.dumps(pack, indent=2) + "\n")
    print(f"  dependency  {dependency}  sha256 {digest[:16]}…")
    print(f"  claim       {token} occurs {occurrences} times")
    print(f"  receipt     {verdict}  {atp} ATP")
    print(f"REPLAY-PACK: built {pack_dir}")
    return 0


def replay(pack_dir):
    """Only the pinned bytes. The current checkout is not opened."""
    pack_dir = Path(pack_dir)
    if is_legacy(pack_dir):
        print(f"  {LEGACY_UNPINNED}: this pack recorded no dependency closure, "
              f"so the bytes its settlement rested on are not available. A "
              f"strict replay is impossible, and reading today's files instead "
              f"would be a different operation with a different meaning.")
        print(f"REPLAY: {LEGACY_UNPINNED}")
        return LEGACY_UNPINNED

    pack = load(pack_dir)
    for dependency in pack["dependencies"]:
        blob = pack_dir / dependency["embedded_path"]
        if not blob.is_file():
            print(f"  {DEPENDENCY_MISSING}: {dependency['dependency_id']} is "
                  f"pinned at {dependency['sha256'][:16]}… but "
                  f"{dependency['embedded_path']} is not in the pack")
            print(f"REPLAY: {DEPENDENCY_MISSING}")
            return DEPENDENCY_MISSING
        data = blob.read_bytes()
        if sha256(data) != dependency["sha256"]:
            print(f"  {REPLAY_MISMATCH}: the embedded bytes for "
                  f"{dependency['dependency_id']} hash to {sha256(data)[:16]}…, "
                  f"the pack pins {dependency['sha256'][:16]}…")
            print(f"REPLAY: {REPLAY_MISMATCH}")
            return REPLAY_MISMATCH

    subject = pack["subject"]
    pinned = pack_dir / next(d["embedded_path"] for d in pack["dependencies"]
                             if d["dependency_id"] == subject["dependency_id"])
    occurrences = count_token(pinned.read_bytes(), subject["token"])
    if occurrences != subject["claimed_occurrences"]:
        print(f"  {REPLAY_MISMATCH}: the pack claims {subject['token']} occurs "
              f"{subject['claimed_occurrences']} times in the pinned bytes; it "
              f"occurs {occurrences}")
        print(f"REPLAY: {REPLAY_MISMATCH}")
        return REPLAY_MISMATCH

    from glyphlib import church, settle_nat_eq
    computation = pack["computation"]
    verdict, atp, meta = settle_nat_eq(church(occurrences), church(occurrences),
                                       computation["budget"])
    recorded = computation["receipt"]
    if (verdict != recorded["verdict"] or atp != recorded["atp_spent"]
            or meta["lhs"]["expect"] != recorded["lhs_nf"]):
        print(f"  {REPLAY_MISMATCH}: re-executing the settlement over the "
              f"pinned bytes gives {verdict}/{atp} ATP, the pack records "
              f"{recorded['verdict']}/{recorded['atp_spent']}")
        print(f"REPLAY: {REPLAY_MISMATCH}")
        return REPLAY_MISMATCH

    print(f"  the pinned bytes reproduce the recorded settlement: "
          f"{verdict}, {atp} ATP, {subject['token']} × {occurrences}")
    print(f"REPLAY: {MATCH}")
    return MATCH


def drift(pack_dir):
    """The pinned bytes against the current checkout. A separate question."""
    pack_dir = Path(pack_dir)
    if is_legacy(pack_dir):
        print(f"  {LEGACY_UNPINNED}: nothing was pinned, so there is nothing to "
              f"compare the current checkout against")
        print(f"DRIFT: {LEGACY_UNPINNED}")
        return LEGACY_UNPINNED

    pack = load(pack_dir)
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
    args = ap.parse_args()
    if args.command == "build":
        return build(args.pack)
    outcome = replay(args.pack) if args.command == "replay" else drift(args.pack)
    return 0 if outcome in (MATCH, SAME) else 1


if __name__ == "__main__":
    raise SystemExit(main())
