#!/usr/bin/env python3
"""
test_poc.py — asserts every fixture settles to its EXPECTED two-axis verdict and
required facts, plus three cross-cutting invariants Codex flagged as unprotected:
  - world-same-input-different-claim: identity does not alias (P0-2);
  - report byte-determinism across two runs (P1-3);
  - commitment detects report field mutation (P1-3).

Run:  ../../.venv/bin/python test_poc.py     (from this directory)
Exit 0 iff everything holds.
"""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verify as V  # noqa: E402

# path -> (execution, binding, required-fact substrings, required-note substr)
CASES = {
    "fixtures/valid/arith-self.md":        ("REPLAYED",   "UNTIED",   ["RESULT_MATCH"], None),
    "fixtures/valid/repo-count.md":        ("REPLAYED",   "ASSERTED", ["RESULT_MATCH"], "NOT established by execution"),
    "fixtures/valid/world-claim-a.md":     ("REPLAYED",   "UNTIED",   ["RESULT_MATCH"], None),
    "fixtures/valid/world-claim-b.md":     ("REPLAYED",   "UNTIED",   ["RESULT_MATCH"], None),
    "fixtures/invalid/expected-mismatch.md":            ("MISMATCH",   "UNTIED",   ["RESULT_MISMATCH"], None),
    "fixtures/invalid/stale-dependency.md":             ("STALE",      "UNTIED",   ["DEPENDENCY_STALE", "RESULT_MATCH"], "changed since pin"),
    "fixtures/invalid/world-missing-dep.md":            ("UNVERIFIED", "UNTIED",   ["DEPENDENCY_MISSING", "RESULT_MATCH"], "without a pinned dependency"),
    "fixtures/invalid/world-path-mismatch.md":          ("UNVERIFIED", "UNTIED",   ["DEPENDENCY_PATH_MISMATCH", "RESULT_MATCH"], "path actually read"),
    "fixtures/invalid/wrong-verifier.md":               ("UNVERIFIED", "UNTIED",   ["VERIFIER_MISMATCH"], None),
    "fixtures/invalid/missing-verifier.md":             ("UNVERIFIED", "UNTIED",   ["VERIFIER_MISSING"], "replay credit refused"),
    "fixtures/invalid/wrong-binding.md":                ("REPLAYED",   "ASSERTED", ["RESULT_MATCH"], "NOT established by execution"),
    "fixtures/invalid/self-declared-reviewed.md":       ("REPLAYED",   "ASSERTED", ["RESULT_MATCH"], "clamped to ASSERTED"),
    "fixtures/invalid/mismatch-result-address.md":      ("MISMATCH",   "UNTIED",   ["ADDRESS_MISMATCH"], "does not reproduce"),
    "fixtures/invalid/combined-verifier-stale-mismatch.md": ("UNVERIFIED", "UNTIED", ["VERIFIER_MISMATCH", "DEPENDENCY_STALE", "RESULT_MISMATCH"], None),
    "fixtures/invalid/stdout-same-effect-different.md": ("MISMATCH",   "UNTIED",   ["RESULT_MISMATCH"], "stdout-only digest WOULD have matched"),
    "fixtures/invalid/effect-short-digest.md":          ("UNVERIFIED", "UNTIED",   ["RESULT_UNSETTLED"], "malformed effect"),
    "fixtures/invalid/capsule-unknown-field.md":        ("UNVERIFIED", "UNTIED",   ["CAPSULE_INVALID"], "unknown field capsule.surprise"),
    "fixtures/invalid/capsule-dup-key.md":              ("UNVERIFIED", "UNTIED",   ["CAPSULE_INVALID"], "duplicate object key"),
    "fixtures/invalid/capsule-malformed-json.md":       ("UNVERIFIED", "UNTIED",   ["CAPSULE_INVALID"], None),
    "fixtures/invalid/capsule-bad-binding-type.md":     ("UNVERIFIED", "UNTIED",   ["CAPSULE_INVALID"], "binding.relation"),
    "fixtures/invalid/capsule-lone-surrogate.md":       ("UNVERIFIED", "UNTIED",   ["CAPSULE_INVALID"], "lone surrogate"),
    "fixtures/limits/effect-invisible-effect.md":       ("REPLAYED",   "UNTIED",   ["RESULT_MATCH"], None),
}


def check_case(rel, exp_exec, exp_bind, req_facts, note_sub):
    r = V.verify_file(os.path.join(HERE, rel))
    facts = r.get("execution_facts", [])
    notes = " ".join(r.get("notes", []))
    problems = []
    if r.get("execution") != exp_exec:
        problems.append(f"execution={r.get('execution')} want {exp_exec}")
    if r.get("binding") != exp_bind:
        problems.append(f"binding={r.get('binding')} want {exp_bind}")
    for f in req_facts:
        if f not in facts:
            problems.append(f"missing fact {f} (facts={facts})")
    if note_sub and note_sub not in notes:
        problems.append(f"missing note {note_sub!r}")
    return problems


def main():
    failures = 0
    for rel, (ee, eb, rf, ns) in CASES.items():
        problems = check_case(rel, ee, eb, rf, ns)
        print(("ok   " if not problems else "FAIL ") + rel)
        for p in problems:
            print("       " + p)
            failures += 1

    print("\n-- invariants --")

    # P0-2: same bytes, different predicate => same dependency_id, distinct ids
    a = V.verify_file(os.path.join(HERE, "fixtures/valid/world-claim-a.md"))["identity"]
    b = V.verify_file(os.path.join(HERE, "fixtures/valid/world-claim-b.md"))["identity"]
    # same bytes AND same result value (both count 7) => dependency_id and
    # result_value_id alias (correct!), but the CLAIM-BOUND identities must not:
    # this is precisely the P2 value-vs-evaluation split.
    inv_ok = (a["dependency_id"] == b["dependency_id"]
              and a["result_value_id"] == b["result_value_id"]
              and a["claim_id"] != b["claim_id"]
              and a["evaluation_id"] != b["evaluation_id"])
    print(("ok   " if inv_ok else "FAIL ")
          + "world-same-input-same-value: dependency+value alias, claim+evaluation distinct")
    failures += 0 if inv_ok else 1

    # P1-3: report byte-determinism across two runs
    import json
    f = os.path.join(HERE, "fixtures/valid/arith-self.md")
    r1 = json.dumps(V.verify_file(f), sort_keys=True, ensure_ascii=False)
    r2 = json.dumps(V.verify_file(f), sort_keys=True, ensure_ascii=False)
    det_ok = r1 == r2
    print(("ok   " if det_ok else "FAIL ") + "report byte-determinism (two runs)")
    failures += 0 if det_ok else 1

    # P1-3: commitment detects field mutation
    rep = V.verify_file(f)
    good = rep["commitment"] == V.commit(rep)
    tampered = copy.deepcopy(rep)
    tampered["execution"] = "REPLAYED_TAMPERED"
    caught = tampered["commitment"] != V.commit(tampered)
    mut_ok = good and caught
    print(("ok   " if mut_ok else "FAIL ")
          + "commitment: valid over body, and mutation is detected")
    failures += 0 if mut_ok else 1

    # P1 (rev 3): the effect path must run with Sigma unavailable. Under `-S`
    # site-packages (incl. the editable sigma-glyph) are gone; if effect still
    # settles, it genuinely does not depend on the evaluator.
    import subprocess
    r = subprocess.run(
        [sys.executable, "-S", os.path.join(HERE, "verify.py"),
         os.path.join(HERE, "fixtures/limits/effect-invisible-effect.md")],
        capture_output=True, text=True)
    indep_ok = r.returncode == 0 and "REPLAYED" in r.stdout
    print(("ok   " if indep_ok else "FAIL ")
          + "effect path is Sigma-independent (runs under python -S)")
    failures += 0 if indep_ok else 1

    # phase 2: canonicalization is deterministic, domain-separated, fail-closed
    import canonical as C
    b = {"a": 1, "b": [2, 3], "t": True}
    canon_ok = (C.record_id("claim", b) == C.record_id("claim", b)
                and C.record_id("claim", b) != C.record_id("plan", b))
    for bad in (lambda: C.canonicalize({"x": 1.0}),          # float
                lambda: C.loads_strict('{"a":1,"a":2}'),     # duplicate key
                lambda: C.loads_strict(r'{"s":"\ud800"}'),   # lone surrogate
                lambda: C.canonicalize({"big": 2 ** 63})):   # out of i64 range
        try:
            bad(); canon_ok = False
        except C.CanonicalError:
            pass
    print(("ok   " if canon_ok else "FAIL ")
          + "canonical: deterministic + domain-separated + rejects float/dup/surrogate/bigint")
    failures += 0 if canon_ok else 1

    # phase-2 step-3 oracle: adversarial 09's two capsules must be schema-valid under
    # capsule.v1 (they were red before — `unknown field capsule.claim_ref`).
    import re as _re
    import schema as _S
    txt = open(os.path.join(HERE, "fixtures/adversarial/09-claim-capsule-association.md"),
               encoding="utf-8").read()
    bodies = _re.findall(r"```json capsule\s*\n(.*?)\n```", txt, _re.S)
    try:
        parsed = [C.loads_strict(b) for b in bodies]
        oracle_ok = (len(parsed) == 2
                     and all(not _S.validate_capsule(p) for p in parsed)
                     and sorted(p.get("claim_ref") for p in parsed) == ["A", "B"])
    except C.CanonicalError:
        oracle_ok = False
    print(("ok   " if oracle_ok else "FAIL ")
          + "adversarial 09: both capsules schema-valid, claim_ref A/B (capsule.v1)")
    failures += 0 if oracle_ok else 1

    print(f"\n{'ALL PASS' if failures == 0 else str(failures) + ' FAILED'} "
          f"({len(CASES)} fixtures + 6 invariants)")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
