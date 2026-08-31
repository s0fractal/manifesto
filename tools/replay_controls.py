#!/usr/bin/env python3
"""Break each replay/drift guarantee once, and require its own verdict.

    python3 tools/replay_controls.py

NON-NORMATIVE. Every mutation works on a COPY of the fixture, or restores the
checkout in a `finally`. Nothing here modifies the sealed SSD pack.

The verdict this set exists to protect is the last one: a pack whose pinned
bytes still reproduce its settlement is `MATCH` even when the current file has
changed. Reporting that situation as a refutation is the defect the format was
built to remove, and there is a control for exactly it.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "drafts/replay-fixture-0.1"
LEGACY = ROOT / "drafts/ssd-pack"
results = []


def chk(label, condition, detail=""):
    results.append(bool(condition))
    print(("  OK    " if condition else "  FAIL  ") + label
          + (f" — {detail}" if detail and not condition else ""))


def verdict(command, pack):
    done = subprocess.run([sys.executable, str(ROOT / "tools/replay_pack.py"),
                           command, str(pack)],
                          capture_output=True, text=True, cwd=str(ROOT))
    for line in reversed((done.stdout + done.stderr).splitlines()):
        if line.startswith(("REPLAY: ", "DRIFT: ")):
            return line.split(": ", 1)[1].strip()
    return f"<no verdict: {(done.stdout + done.stderr).strip()[-160:]}>"


def on_a_copy(mutate):
    work = Path(tempfile.mkdtemp(prefix="replay-control-"))
    copy = work / "fixture"
    shutil.copytree(FIXTURE, copy)
    mutate(copy)
    return work, copy


def main():
    print("Replay and drift, each guarantee broken once.\n")

    chk("baseline: the fixture replays MATCH", verdict("replay", FIXTURE) == "MATCH",
        verdict("replay", FIXTURE))
    chk("baseline: and its dependencies are SAME as the checkout",
        verdict("drift", FIXTURE) == "SAME", verdict("drift", FIXTURE))

    # The sealed pack. Refused, never reinterpreted.
    chk("the legacy SSD pack replays LEGACY_UNPINNED",
        verdict("replay", LEGACY) == "LEGACY_UNPINNED", verdict("replay", LEGACY))
    chk("...and drift says the same rather than inventing a comparison",
        verdict("drift", LEGACY) == "LEGACY_UNPINNED", verdict("drift", LEGACY))

    def delete_blob(copy):
        for blob in (copy / "blobs").iterdir():
            blob.unlink()

    work, copy = on_a_copy(delete_blob)
    try:
        chk("deleted pinned bytes give DEPENDENCY_MISSING, not a silent pass",
            verdict("replay", copy) == "DEPENDENCY_MISSING", verdict("replay", copy))
    finally:
        shutil.rmtree(work, ignore_errors=True)

    def corrupt_blob(copy):
        for blob in (copy / "blobs").iterdir():
            blob.write_bytes(blob.read_bytes() + b"FLOW\n")

    work, copy = on_a_copy(corrupt_blob)
    try:
        chk("changed pinned bytes give REPLAY_MISMATCH",
            verdict("replay", copy) == "REPLAY_MISMATCH", verdict("replay", copy))
    finally:
        shutil.rmtree(work, ignore_errors=True)

    def corrupt_receipt(copy):
        pack = json.loads((copy / "pack.json").read_text())
        pack["computation"]["receipt"]["atp_spent"] += 1
        (copy / "pack.json").write_text(json.dumps(pack, indent=2))

    work, copy = on_a_copy(corrupt_receipt)
    try:
        chk("a changed receipt gives REPLAY_MISMATCH",
            verdict("replay", copy) == "REPLAY_MISMATCH", verdict("replay", copy))
    finally:
        shutil.rmtree(work, ignore_errors=True)

    def corrupt_claim(copy):
        pack = json.loads((copy / "pack.json").read_text())
        pack["subject"]["claimed_occurrences"] += 1
        (copy / "pack.json").write_text(json.dumps(pack, indent=2))

    work, copy = on_a_copy(corrupt_claim)
    try:
        chk("a claim that is false ON THE PINNED BYTES gives REPLAY_MISMATCH — "
            "this, and only this, is the shape a refutation would take",
            verdict("replay", copy) == "REPLAY_MISMATCH", verdict("replay", copy))
    finally:
        shutil.rmtree(work, ignore_errors=True)

    # THE ONE THAT MATTERS. Change the CURRENT file only; the pack is untouched.
    source = FIXTURE / "source.md"
    original = source.read_bytes()
    try:
        source.write_bytes(original + b"\nFLOW again, changing the file today.\n")
        drifted = verdict("drift", FIXTURE)
        replayed = verdict("replay", FIXTURE)
        chk("changing only the current checkout gives DRIFT", drifted == "DRIFT",
            drifted)
        chk("...and the historical replay is STILL MATCH", replayed == "MATCH",
            replayed)
        chk("...so drift never becomes a refutation on its own",
            drifted == "DRIFT" and replayed not in ("REPLAY_MISMATCH", "REFUTED"),
            f"drift={drifted} replay={replayed}")
    finally:
        source.write_bytes(original)
    chk("the checkout is restored and drift is SAME again",
        verdict("drift", FIXTURE) == "SAME", verdict("drift", FIXTURE))

    def remove_current(copy):
        pack = json.loads((copy / "pack.json").read_text())
        pack["dependencies"][0]["dependency_id"] = "drafts/gone-from-the-tree.md"
        (copy / "pack.json").write_text(json.dumps(pack, indent=2))

    work, copy = on_a_copy(remove_current)
    try:
        chk("a dependency no longer in the checkout gives CURRENT_MISSING, "
            "distinct from DRIFT", verdict("drift", copy) == "CURRENT_MISSING",
            verdict("drift", copy))
    finally:
        shutil.rmtree(work, ignore_errors=True)

    print()
    if all(results):
        print(f"REPLAY-CONTROLS: ALL PASS ({len(results)}/{len(results)})")
        return 0
    print(f"REPLAY-CONTROLS: FAILURES ({sum(results)}/{len(results)})")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
