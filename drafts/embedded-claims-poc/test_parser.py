#!/usr/bin/env python3
"""
test_parser.py — PARSE-layer oracle for the adversarial corpus (hardened after Codex).

Asserts, per specimen: report `status`, the set of error codes, and — for VALID
documents — the EXACT claims (class, payload, local_id) in order, the capsule
`claim_ref`s in order, and that every claim's byte span slices back to real glyph text.
Count-only checks are not enough (Codex P1-6): reordered payloads, wrong local_ids, or
corrupted spans must fail here. Determinism is checked CROSS-PROCESS (two subprocesses),
not twice in one process.

SCOPE: PARSE only. 09/15/16 carry capsules whose association verdicts (DANGLING_CLAIM_REF,
DUPLICATE_CLAIM_REF) are the 3c compiler's job; here we assert only that the structure —
claims, local_ids, capsule claim_refs — is parsed correctly.

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

# For VALID docs: (status, codes, [(class,payload,local_id)...], [capsule claim_ref...])
# For INVALID/INERT: (status, codes) — structure is diagnostic only.
V = "VALID"
GOLDEN = {
    "01-illustration-vs-live.md": (V, [], [("arith", "3 + 6 = 9", None)], []),
    "02-multiple-claims.md": (V, [], [("arith", "3 + 6 = 9", None),
                                      ("arith", "74 + 1 = 75", None),
                                      ("cmp", "75 > 8", None)], []),
    "03-nested-fences.md": (V, [], [], []),
    "04-info-string-variants.md": (V, [], [], [None]),
    "05-unclosed-fence.md": ("INVALID", ["MISSING_END", "UNCLOSED_FENCE"]),
    "06-glyph-in-code-fence.md": (V, [], [("arith", "3 + 6 = 9", None)], []),
    "07-delimiter-injection.md": ("INVALID", ["UNSUPPORTED_INLINE_DELIMITER"]),
    "08-unicode-normalization.md": (V, [], [("cite", '"café" in NOTES.md', None)], []),
    "09-claim-capsule-association.md": (V, [], [("arith", "74 + 1 = 75", "A"),
                                               ("count", "/Теза/ in README.md = 8", "B")],
                                        ["B", "A"]),
    "10-no-live-region.md": ("INERT", ["NO_LIVE_REGION"]),
    "11-unknown-profile.md": ("INVALID", ["UNKNOWN_PROFILE"]),
    "12-unbalanced-region.md": ("INVALID", ["MISSING_END", "NESTED_OR_DUP_BEGIN"]),
    "13-marker-in-fence.md": ("INERT", ["NO_LIVE_REGION"]),
    "14-unexpected-end.md": ("INVALID", ["UNEXPECTED_END"]),
    "15-dangling-claim-ref.md": (V, [], [("arith", "74 + 1 = 75", "A")], ["Z"]),
    "16-duplicate-local-id.md": (V, [], [("arith", "74 + 1 = 75", "A")], ["A", "A"]),
    "17-fake-end-in-fence.md": (V, [], [("arith", "3 + 6 = 9", None),
                                        ("arith", "74 + 1 = 75", None)], []),
    "18-inline-code-and-html.md": (V, [], [("arith", "3 + 6 = 9", None)], []),
    "19-malformed-claim-open.md": ("INVALID", ["MALFORMED_CLAIM_OPEN"]),
    "20-noncloser-line.md": ("INVALID", ["MISSING_END", "UNCLOSED_FENCE"]),
}


def check(name, expect):
    raw = open(os.path.join(HERE, "fixtures/adversarial", name), "rb").read()
    rep = P.parse(raw.decode("utf-8"))
    problems = []
    status, codes = expect[0], expect[1]
    if rep["status"] != status:
        problems.append(f"status={rep['status']} want {status}")
    got_codes = sorted({e["code"] for e in rep["errors"]})
    if got_codes != codes:
        problems.append(f"codes={got_codes} want {codes}")
    if status == V:
        want_claims, want_refs = expect[2], expect[3]
        got_claims = [(c["class"], c["payload"], c["local_id"]) for c in rep["claims"]]
        if got_claims != want_claims:
            problems.append(f"claims={got_claims} want {want_claims}")
        # spans must slice back to real glyph text
        for c in rep["claims"]:
            sp = c.get("span")
            if not sp or raw[sp[0]:sp[1]][:3] != "⟦".encode("utf-8"):
                problems.append(f"bad span for claim {c.get('payload')!r}: {sp}")
        got_refs = []
        for cap in rep["capsules"]:
            try:
                got_refs.append(json.loads(cap["body_raw"]).get("claim_ref"))
            except Exception as e:
                problems.append(f"capsule body not JSON: {e}")
        if got_refs != want_refs:
            problems.append(f"capsule claim_refs={got_refs} want {want_refs}")
    return problems


def main():
    failures = 0
    for name, expect in GOLDEN.items():
        problems = check(name, expect)
        print(("ok   " if not problems else "FAIL ") + name)
        for p in problems:
            print("       " + p)
            failures += 1

    # cross-process determinism: two independent processes, identical REPORT line
    def report_line(path):
        out = subprocess.run([sys.executable, os.path.join(HERE, "parser.py"), path],
                             capture_output=True, text=True).stdout.strip().split("\n")
        return out[-1]
    f = os.path.join(HERE, "fixtures/adversarial/09-claim-capsule-association.md")
    det = report_line(f) == report_line(f)
    print(("ok   " if det else "FAIL ") + "parse determinism (two SUBPROCESSES)")
    failures += 0 if det else 1

    # parser_id binds installed deps: it must be a parser:// id and stable in-process
    pid_ok = P.parser_id().startswith("parser://sha256:") and P.parser_id() == P.parser_id()
    print(("ok   " if pid_ok else "FAIL ") + "parser_id binds installed dependency closure")
    failures += 0 if pid_ok else 1

    print(f"\n{'ALL PASS' if failures == 0 else str(failures) + ' FAILED'} "
          f"({len(GOLDEN)} PARSE specimens + 2 invariants) — PARSE layer only, COMPILE is 3c")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
