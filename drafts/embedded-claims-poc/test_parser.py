#!/usr/bin/env python3
"""
test_parser.py — PARSE-layer oracle, capsule-only (after the pivot).

The canonical pipeline grants machine credit only to explicit in-region capsules; the
parser never scans prose. This asserts, per specimen: report `status`, the error-code
set, and — for VALID documents — the exact number of capsules, the `claim.local_id`
carried inside each (in order), and that every capsule's byte span slices back to its
raw body. Determinism is cross-PROCESS.

SCOPE: PARSE only. Schema validation of the v2 capsule and settlement of the contained
claim are the 3c compiler's job.

Run:  ../../.venv/bin/python test_parser.py   (needs: pip install --require-hashes
      -r requirements-parser.lock)
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import parser as P  # noqa: E402

V = "VALID"
# VALID: (status, codes, capsule_count, [claim.local_id per capsule])
# INVALID/INERT: (status, codes)
GOLDEN = {
    "01-illustration-vs-live.md": (V, [], 1, ["T"]),
    "02-multiple-claims.md": (V, [], 2, ["A", "B"]),
    "03-nested-fences.md": (V, [], 0, []),
    "04-info-string-variants.md": (V, [], 1, [None]),   # body has "note", no claim
    "05-unclosed-fence.md": ("INVALID", ["MISSING_END", "UNCLOSED_FENCE"]),
    "09-claim-inside-capsule.md": (V, [], 1, ["README-THESIS-COUNT"]),
    "10-no-live-region.md": ("INERT", ["NO_LIVE_REGION"]),
    "11-unknown-profile.md": ("INVALID", ["UNKNOWN_PROFILE"]),
    "12-unbalanced-region.md": ("INVALID", ["MISSING_END", "NESTED_OR_DUP_BEGIN"]),
    "13-marker-in-fence.md": ("INERT", ["NO_LIVE_REGION"]),
    "14-unexpected-end.md": ("INVALID", ["UNEXPECTED_END"]),
    "17-fake-end-in-fence.md": (V, [], 0, []),
    "20-noncloser-line.md": ("INVALID", ["MISSING_END", "UNCLOSED_FENCE"]),
}


def check(name, expect):
    raw = open(os.path.join(HERE, "fixtures/adversarial", name), "rb").read()
    rep = P.parse(raw.decode("utf-8"))
    problems = []
    if rep["status"] != expect[0]:
        problems.append(f"status={rep['status']} want {expect[0]}")
    got_codes = sorted({e["code"] for e in rep["errors"]})
    if got_codes != expect[1]:
        problems.append(f"codes={got_codes} want {expect[1]}")
    if expect[0] == V:
        want_n, want_ids = expect[2], expect[3]
        caps = rep["capsules"]
        if len(caps) != want_n:
            problems.append(f"capsules={len(caps)} want {want_n}")
        ids = []
        for c in caps:
            # span must slice back to the exact raw body
            if raw[c["span"][0]:c["span"][1]].decode("utf-8") != c["body_raw"]:
                problems.append(f"span does not match body at line {c['line']}")
            try:
                ids.append(json.loads(c["body_raw"]).get("claim", {}).get("local_id"))
            except Exception as e:
                problems.append(f"capsule body not JSON: {e}")
        if ids != want_ids:
            problems.append(f"claim local_ids={ids} want {want_ids}")
    return problems


def main():
    failures = 0
    for name, expect in GOLDEN.items():
        problems = check(name, expect)
        print(("ok   " if not problems else "FAIL ") + name)
        for p in problems:
            print("       " + p)
            failures += 1

    def report_line(path):
        out = subprocess.run([sys.executable, os.path.join(HERE, "parser.py"), path],
                             capture_output=True, text=True).stdout.strip().split("\n")
        return out[-1]
    f = os.path.join(HERE, "fixtures/adversarial/09-claim-inside-capsule.md")
    det = report_line(f) == report_line(f)
    print(("ok   " if det else "FAIL ") + "parse determinism (two SUBPROCESSES)")
    failures += 0 if det else 1

    pid_ok = P.parser_id().startswith("parser://sha256:") and P.parser_id() == P.parser_id()
    print(("ok   " if pid_ok else "FAIL ") + "parser_id binds installed dependency closure")
    failures += 0 if pid_ok else 1

    # line-ending ingress (Codex 3b.1): CRLF parses identically with faithful byte spans;
    # mixed / lone-CR is a typed failure, never a silent NO_LIVE_REGION.
    lf = open(os.path.join(HERE, "fixtures/adversarial/09-claim-inside-capsule.md"),
              "rb").read().decode("utf-8")
    crlf = lf.replace("\n", "\r\n")
    r = P.parse(crlf)
    raw = crlf.encode("utf-8")
    crlf_ok = (r["status"] == V and len(r["capsules"]) == 1
               and raw[r["capsules"][0]["span"][0]:r["capsules"][0]["span"][1]]
               .decode("utf-8") == r["capsules"][0]["body_raw"])
    print(("ok   " if crlf_ok else "FAIL ") + "CRLF ingress: VALID, one capsule, faithful span")
    failures += 0 if crlf_ok else 1

    def codes(rep):
        return sorted({e["code"] for e in rep["errors"]})
    mixed = P.parse(lf.replace("\n", "\r\n", 1))
    lone = P.parse("<!-- x -->\rmore\ntext")
    le_ok = (mixed["status"] == "INVALID" and codes(mixed) == ["UNSUPPORTED_LINE_ENDING"]
             and lone["status"] == "INVALID" and codes(lone) == ["UNSUPPORTED_LINE_ENDING"])
    print(("ok   " if le_ok else "FAIL ") + "mixed / lone-CR endings are typed UNSUPPORTED_LINE_ENDING")
    failures += 0 if le_ok else 1

    print(f"\n{'ALL PASS' if failures == 0 else str(failures) + ' FAILED'} "
          f"({len(GOLDEN)} PARSE specimens + 4 invariants) — capsule-only; COMPILE is 3c")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
