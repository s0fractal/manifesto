#!/usr/bin/env python3
"""
test_cli.py — orchestration CLI negatives + the real-specimen exact scope.

The load-bearing negative (Codex P0): `--strict` must NOT be vacuously green on an empty
result vector — a RUN with zero records is a fail under --strict, so a regression that stops
extracting capsules cannot leave the gate green. Also confirms the E2E specimen runs a
non-empty EXACT scope (one record, the expected local_id, REPLAYED).

Run:  ../../.venv/bin/python test_cli.py
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E2E = os.path.normpath(os.path.join(HERE, "..", "EMBEDDED-CLAIMS-E2E-0.1.md"))
EMPTY = [os.path.join(HERE, "fixtures/adversarial", f)
         for f in ("03-nested-fences.md", "17-fake-end-in-fence.md")]


def cli(*args):
    return subprocess.run([sys.executable, os.path.join(HERE, "claims.py"), *args],
                          capture_output=True, text=True)


def main():
    failures = 0

    def inv(ok, label):
        nonlocal failures
        print(("ok   " if ok else "FAIL ") + label)
        failures += 0 if ok else 1

    for f in EMPTY:
        name = os.path.basename(f)
        r = cli("run", "--strict", f)
        inv(r.returncode != 0, f"empty vector + --strict ⇒ non-zero exit ({name})")
        r2 = cli("run", f)   # non-strict: a RUN with no records is fine, exit 0
        rep = json.loads(r2.stdout)
        inv(r2.returncode == 0 and rep["status"] == "RUN" and rep["results"] == [],
            f"empty vector, no --strict ⇒ exit 0, empty vector ({name})")

    r = cli("run", "--strict", E2E)
    inv(r.returncode == 0, "E2E specimen + --strict ⇒ exit 0")

    r2 = cli("run", E2E)
    rep = json.loads(r2.stdout)
    inv(rep["status"] == "RUN" and rep["evaluator_invocations"] == 1
        and len(rep["results"]) == 1
        and rep["results"][0]["local_id"] == "README-THESIS-HEADING-COUNT"
        and rep["results"][0]["execution"] == "REPLAYED",
        "E2E runs a non-empty EXACT scope (1 record, README-THESIS-HEADING-COUNT, REPLAYED)")

    r3 = cli("run")   # usage error
    inv(r3.returncode == 2, "missing document ⇒ usage error (exit 2)")

    print(f"\n{'ALL PASS' if failures == 0 else str(failures) + ' FAILED'} (CLI checks)")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
