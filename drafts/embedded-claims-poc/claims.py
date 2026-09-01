#!/usr/bin/env python3
"""
claims — orchestration CLI for the embedded-claims pipeline.

    claims run [--strict] <document.md>
      = read bytes → PARSE → COMPILE → RUN → JSON vector REPORT

Pure orchestration: it wires the four existing layers and adds NO verification logic,
NO automatic file writes, and NO document-level badge. The output is always the runner's
vector REPORT (one result per record); the process never emits a global document verdict.

`--strict` projects a CI exit policy: a non-zero exit when the report is not a clean RUN
or any record is not REPLAYED. That exit code is a POLICY PROJECTION over the vector, NOT
a global document MISMATCH — the JSON is still the per-record vector.

Receipt / authenticity is a separate phase and is deliberately NOT pulled into this CLI.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import parser as P      # noqa: E402
import compiler as C    # noqa: E402
import runner as R      # noqa: E402


def run_document(path, strict):
    with open(path, "rb") as f:
        src = f.read()
    report = R.run(C.compile_report(P.parse(src.decode("utf-8")), src))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    if not strict:
        return 0
    results = report.get("results")
    if report.get("status") != "RUN":
        return 1
    # a RUN with zero records is not a pass: all([]) is vacuously true, which would let a
    # regression that stops extracting capsules leave a --strict gate green (Codex P0).
    if not isinstance(results, list) or not results:
        return 1
    return 0 if all(r["execution"] == "REPLAYED" for r in results) else 1


def main():
    args = [a for a in sys.argv[1:] if a != "--strict"]
    strict = "--strict" in sys.argv
    if len(args) != 2 or args[0] != "run":
        print("usage: claims run [--strict] <document.md>", file=sys.stderr)
        return 2
    return run_document(args[1], strict)


if __name__ == "__main__":
    sys.exit(main())
