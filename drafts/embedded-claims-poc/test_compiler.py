#!/usr/bin/env python3
"""
test_compiler.py — COMPILE-layer oracle (phase 2 step 3c).

parse → compile, then assert: the compile `status`, the emitted record `local_id`s (in
order), and the error-code set. STRUCTURAL only — no settlement is run here (that is 3d;
COMPILED must not mean REPLAYED).

The mandatory negative (Codex): a ParseReport with status != VALID — INVALID or INERT,
even if it diagnostically carried a candidate capsule — must be REFUSED as a whole, with
zero records.

Run:  ../../.venv/bin/python test_compiler.py   (needs the pinned parser deps)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import parser as P      # noqa: E402
import compiler as C    # noqa: E402

# name -> (compile_status, local_ids | None, error codes)
GOLDEN = {
    "01-illustration-vs-live.md": ("COMPILED", ["T"], []),
    "02-multiple-claims.md": ("COMPILED", ["A", "B"], []),
    "03-nested-fences.md": ("COMPILED", [], []),
    "09-claim-inside-capsule.md": ("COMPILED", ["README-THESIS-COUNT"], []),
    "17-fake-end-in-fence.md": ("COMPILED", [], []),
    # mandatory negative: parser status != VALID => whole report refused
    "05-unclosed-fence.md": ("REFUSED", None, ["PRECONDITION_NOT_VALID"]),
    "10-no-live-region.md": ("REFUSED", None, ["PRECONDITION_NOT_VALID"]),
    "11-unknown-profile.md": ("REFUSED", None, ["PRECONDITION_NOT_VALID"]),
    "13-marker-in-fence.md": ("REFUSED", None, ["PRECONDITION_NOT_VALID"]),
    "14-unexpected-end.md": ("REFUSED", None, ["PRECONDITION_NOT_VALID"]),
    # compile-layer negatives
    "21-capsule-bad-json.md": ("INVALID", None, ["CAPSULE_NOT_STRICT_JSON"]),
    "22-capsule-schema-invalid.md": ("INVALID", None, ["CAPSULE_SCHEMA_INVALID"]),
    "23-duplicate-local-id.md": ("INVALID", None, ["DUPLICATE_LOCAL_ID"]),
}


def compile_file(name):
    with open(os.path.join(HERE, "fixtures/adversarial", name), "rb") as f:
        pr = P.parse(f.read().decode("utf-8"))
    return C.compile_report(pr)


def main():
    failures = 0
    for name, (status, ids, codes) in GOLDEN.items():
        rep = compile_file(name)
        problems = []
        if rep["status"] != status:
            problems.append(f"status={rep['status']} want {status}")
        got_codes = sorted({e["code"] for e in rep["errors"]})
        if got_codes != codes:
            problems.append(f"codes={got_codes} want {codes}")
        if status == "COMPILED":
            got_ids = [r["local_id"] for r in rep["records"]]
            if got_ids != ids:
                problems.append(f"local_ids={got_ids} want {ids}")
            for r in rep["records"]:
                if not (str(r["claim_id"]).startswith("sha256:")
                        and str(r["plan_id"]).startswith("sha256:")):
                    problems.append(f"record {r['local_id']} missing content-addressed ids")
        else:
            if rep["records"]:
                problems.append(f"non-COMPILED report emitted {len(rep['records'])} records")
        print(("ok   " if not problems else "FAIL ") + name)
        for p in problems:
            print("       " + p)
            failures += 1

    print("\n-- invariants --")

    # claim_id is deterministic and distinct for distinct predicates
    r1 = compile_file("02-multiple-claims.md")
    r2 = compile_file("02-multiple-claims.md")
    a, b = r1["records"][0], r1["records"][1]
    det_ok = ([x["claim_id"] for x in r1["records"]] == [x["claim_id"] for x in r2["records"]]
              and a["claim_id"] != b["claim_id"])
    print(("ok   " if det_ok else "FAIL ")
          + "claim_id deterministic + distinct for distinct predicates")
    failures += 0 if det_ok else 1

    # a REFUSED report carries zero records even though the parser had a candidate
    ref = compile_file("11-unknown-profile.md")
    refuse_ok = ref["status"] == "REFUSED" and ref["records"] == []
    print(("ok   " if refuse_ok else "FAIL ")
          + "INVALID parse report is REFUSED whole, zero records (mandatory negative)")
    failures += 0 if refuse_ok else 1

    cid_ok = C.compiler_id().startswith("compiler://sha256:") and C.compiler_id() == C.compiler_id()
    print(("ok   " if cid_ok else "FAIL ") + "compiler_id binds compiler+canonical closure")
    failures += 0 if cid_ok else 1

    print(f"\n{'ALL PASS' if failures == 0 else str(failures) + ' FAILED'} "
          f"({len(GOLDEN)} COMPILE specimens + 3 invariants) — structural; settlement is 3d")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
