#!/usr/bin/env python3
"""
test_parser.py — PARSE-layer oracle for the adversarial corpus (phase 2 step 3b).

Runs parser.parse() over every specimen and asserts the structural outcome:
(regions, claims, capsules, error-codes). This is the PARSE column of
fixtures/adversarial/EXPECTED.md made executable.

SCOPE: PARSE only. Specimens 09/15/16 are checked for correct STRUCTURE (claim/capsule
counts) — their COMPILE verdicts (DANGLING_CLAIM_REF, DUPLICATE_CLAIM_REF, association)
belong to the 3c compiler and are NOT asserted here. So this does not claim "01–17 fully
pass"; it claims the parse layer is correct.

Run:  ../../.venv/bin/python test_parser.py    (needs the pinned parser deps installed:
      pip install --require-hashes -r requirements-parser.lock)
Exit 0 iff every specimen matches.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import parser as P  # noqa: E402

# specimen -> (regions, claims, capsules, sorted error codes)
EXPECT = {
    "01-illustration-vs-live.md":      (1, 1, 0, []),
    "02-multiple-claims.md":           (1, 3, 0, []),
    "03-nested-fences.md":             (1, 0, 0, []),
    "04-info-string-variants.md":      (1, 0, 1, []),
    "05-unclosed-fence.md":            (0, 0, 0, ["MISSING_END", "UNCLOSED_FENCE"]),
    "06-glyph-in-code-fence.md":       (1, 1, 0, []),
    "07-delimiter-injection.md":       (1, 1, 0, ["UNSUPPORTED_INLINE_DELIMITER"]),
    "08-unicode-normalization.md":     (1, 1, 0, []),
    "09-claim-capsule-association.md": (1, 2, 2, []),   # association = 3c, not here
    "10-no-live-region.md":            (0, 0, 0, ["NO_LIVE_REGION"]),
    "11-unknown-profile.md":           (1, 0, 0, ["UNKNOWN_PROFILE"]),
    "12-unbalanced-region.md":         (0, 0, 0, ["MISSING_END", "NESTED_OR_DUP_BEGIN"]),
    "13-marker-in-fence.md":           (0, 0, 0, ["NO_LIVE_REGION"]),
    "14-unexpected-end.md":            (0, 0, 0, ["UNEXPECTED_END"]),
    "15-dangling-claim-ref.md":        (1, 1, 1, []),   # dangling = 3c, not here
    "16-duplicate-local-id.md":        (1, 1, 2, []),   # duplicate = 3c, not here
    "17-fake-end-in-fence.md":         (1, 2, 0, []),
}


def main():
    failures = 0
    for name, (er, ec, ecap, ecodes) in EXPECT.items():
        with open(os.path.join(HERE, "fixtures/adversarial", name), encoding="utf-8") as f:
            rep = P.parse(f.read())
        got = (len(rep["regions"]), len(rep["claims"]), len(rep["capsules"]),
               sorted({e["code"] for e in rep["errors"]}))
        ok = got == (er, ec, ecap, ecodes)
        print(("ok   " if ok else "FAIL ") + name)
        if not ok:
            print(f"       got regions/claims/capsules/errors = "
                  f"{got[0]}/{got[1]}/{got[2]}/{got[3]}")
            print(f"       want                                = "
                  f"{er}/{ec}/{ecap}/{ecodes}")
            failures += 1

    # determinism: two parses of one specimen are byte-identical reports
    import json
    f = os.path.join(HERE, "fixtures/adversarial/02-multiple-claims.md")
    t = open(f, encoding="utf-8").read()
    det = json.dumps(P.parse(t), sort_keys=True) == json.dumps(P.parse(t), sort_keys=True)
    print(("ok   " if det else "FAIL ") + "parse determinism (two runs)")
    failures += 0 if det else 1

    print(f"\n{'ALL PASS' if failures == 0 else str(failures) + ' FAILED'} "
          f"({len(EXPECT)} PARSE specimens + 1 determinism) — PARSE layer only, COMPILE is 3c")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
