#!/usr/bin/env python3
"""Break each replay/drift guarantee once, and require its own verdict.

    python3 tools/replay_controls.py --evaluator <receipt-or-wheel>

NON-NORMATIVE. Every mutation works on a COPY of the fixture, or restores the
checkout in a `finally`. Nothing here modifies the sealed SSD pack.

Three of these controls exist because the mutations passed. Before the pack was
bound to its evaluator and its profile, and before the receipt comparison was
closed and the paths contained:

    evaluator_artifact_sha256 -> ffff…   gave MATCH
    rhs_nf -> 0000…                      gave MATCH
    blob removed, embedded_path made an absolute path to a file next door
                                         gave MATCH

So `MATCH` meant less than it said, in the one place where that mattered most.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "drafts/replay-fixture-0.1"
LEGACY = ROOT / "drafts/ssd-pack"
RECEIPT_FIELDS = ("verdict", "atp_spent", "lhs_nf", "rhs_nf")
results = []


def chk(label, condition, detail=""):
    results.append(bool(condition))
    print(("  OK    " if condition else "  FAIL  ") + label
          + (f" — {detail}" if detail and not condition else ""))


def verdict(command, pack, evaluator=None):
    argv = [sys.executable, str(ROOT / "tools/replay_pack.py"), command,
            str(pack)]
    if evaluator and command == "replay":
        argv += ["--evaluator", str(evaluator)]
    done = subprocess.run(argv, capture_output=True, text=True,  # noqa: S603
                          cwd=str(ROOT))
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


def edit_pack(copy, change):
    pack = json.loads((copy / "pack.json").read_text())
    change(pack)
    (copy / "pack.json").write_text(json.dumps(pack, indent=2))


def control(label, mutate, expected, evaluator, command="replay"):
    work, copy = on_a_copy(mutate)
    try:
        got = verdict(command, copy, evaluator)
        chk(label, got == expected, f"expected {expected}, got {got}")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--evaluator", required=True)
    args = ap.parse_args()
    evaluator = args.evaluator

    print("Replay and drift, each guarantee broken once.\n")

    chk("baseline: the fixture replays MATCH",
        verdict("replay", FIXTURE, evaluator) == "MATCH",
        verdict("replay", FIXTURE, evaluator))
    chk("baseline: and its dependencies are SAME as the checkout",
        verdict("drift", FIXTURE) == "SAME", verdict("drift", FIXTURE))

    # --- the evaluator is an operand, not a decoration
    chk("no evaluator supplied is EVALUATOR_UNVERIFIED, never MATCH",
        verdict("replay", FIXTURE) == "EVALUATOR_UNVERIFIED",
        verdict("replay", FIXTURE))
    control("a pack pinning a DIFFERENT evaluator digest is EVALUATOR_MISMATCH "
            "(this mutation used to give MATCH)",
            lambda copy: edit_pack(copy, lambda p: p["runtime"].__setitem__(
                "evaluator_artifact_sha256", "f" * 64)),
            "EVALUATOR_MISMATCH", evaluator)

    # --- the profile is pinned by the sources that define it
    control("a changed profile source is PROFILE_MISMATCH",
            lambda copy: edit_pack(copy, lambda p: p["runtime"]["profile_sources"][0]
                                   .__setitem__("sha256", "a" * 64)),
            "PROFILE_MISMATCH", evaluator)

    # --- the receipt comparison is closed: every field, and only these fields
    for field in RECEIPT_FIELDS:
        def break_field(copy, field=field):
            def change(pack):
                value = pack["computation"]["receipt"][field]
                pack["computation"]["receipt"][field] = (
                    value + 1 if isinstance(value, int) else "0" * 64)
            edit_pack(copy, change)
        control(f"a changed receipt field {field!r} is REPLAY_MISMATCH"
                + (" (this mutation used to give MATCH)"
                   if field == "rhs_nf" else ""),
                break_field, "REPLAY_MISMATCH", evaluator)

    control("an EXTRA receipt field is a mismatch, so the set cannot grow "
            "unnoticed",
            lambda copy: edit_pack(copy, lambda p: p["computation"]["receipt"]
                                   .__setitem__("extra", 1)),
            "REPLAY_MISMATCH", evaluator)

    # --- containment
    def escape_absolute(copy):
        outside = copy.parent / "outside"
        outside.mkdir(exist_ok=True)
        for blob in (copy / "blobs").iterdir():
            shutil.move(str(blob), str(outside / blob.name))
            edit_pack(copy, lambda p, n=blob.name: p["dependencies"][0]
                      .__setitem__("embedded_path", str(outside / n)))

    control("an absolute embedded_path pointing outside the pack is "
            "MALFORMED_PACK (this mutation used to give MATCH)",
            escape_absolute, "MALFORMED_PACK", evaluator)

    control("a traversing embedded_path is MALFORMED_PACK",
            lambda copy: edit_pack(copy, lambda p: p["dependencies"][0]
                                   .__setitem__("embedded_path", "../source.md")),
            "MALFORMED_PACK", evaluator)

    def escaping_symlink(copy):
        outside = copy.parent / "escape"
        outside.mkdir(exist_ok=True)
        for blob in (copy / "blobs").iterdir():
            shutil.move(str(blob), str(outside / blob.name))
            blob.symlink_to(outside / blob.name)

    control("a symlink leaving the pack is MALFORMED_PACK, not followed",
            escaping_symlink, "MALFORMED_PACK", evaluator)

    # --- structure
    control("duplicate dependency ids are MALFORMED_PACK",
            lambda copy: edit_pack(copy, lambda p: p["dependencies"].append(
                dict(p["dependencies"][0]))),
            "MALFORMED_PACK", evaluator)
    control("a subject naming no pinned dependency is MALFORMED_PACK",
            lambda copy: edit_pack(copy, lambda p: p["subject"].__setitem__(
                "dependency_id", "drafts/not-pinned.md")),
            "MALFORMED_PACK", evaluator)
    control("a pack of this format missing a section is MALFORMED_PACK, NOT "
            "filed as legacy",
            lambda copy: edit_pack(copy, lambda p: p.pop("runtime")),
            "MALFORMED_PACK", evaluator)

    control("deleted pinned bytes are DEPENDENCY_MISSING, not a silent pass",
            lambda copy: [b.unlink() for b in (copy / "blobs").iterdir()],
            "DEPENDENCY_MISSING", evaluator)
    control("changed pinned bytes are REPLAY_MISMATCH",
            lambda copy: [b.write_bytes(b.read_bytes() + b"FLOW\n")
                          for b in (copy / "blobs").iterdir()],
            "REPLAY_MISMATCH", evaluator)
    control("a claim false ON THE PINNED BYTES is REPLAY_MISMATCH — this, and "
            "only this, is the shape a refutation would take",
            lambda copy: edit_pack(copy, lambda p: p["subject"].__setitem__(
                "claimed_occurrences", p["subject"]["claimed_occurrences"] + 1)),
            "REPLAY_MISMATCH", evaluator)

    # --- the sealed pack
    chk("the legacy SSD pack replays LEGACY_UNPINNED",
        verdict("replay", LEGACY, evaluator) == "LEGACY_UNPINNED",
        verdict("replay", LEGACY, evaluator))
    chk("...and drift says the same rather than inventing a comparison",
        verdict("drift", LEGACY) == "LEGACY_UNPINNED", verdict("drift", LEGACY))

    # --- THE ONE THAT MATTERS
    source = FIXTURE / "source.md"
    original = source.read_bytes()
    try:
        source.write_bytes(original + b"\nFLOW again, changing the file today.\n")
        drifted = verdict("drift", FIXTURE)
        replayed = verdict("replay", FIXTURE, evaluator)
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

    control("a dependency no longer in the checkout is CURRENT_MISSING, "
            "distinct from DRIFT",
            lambda copy: edit_pack(copy, lambda p: p["dependencies"][0]
                                   .__setitem__("dependency_id",
                                                "drafts/gone.md")),
            "MALFORMED_PACK", evaluator, command="replay")

    print()
    if all(results):
        print(f"REPLAY-CONTROLS: ALL PASS ({len(results)}/{len(results)})")
        return 0
    print(f"REPLAY-CONTROLS: FAILURES ({sum(results)}/{len(results)})")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
