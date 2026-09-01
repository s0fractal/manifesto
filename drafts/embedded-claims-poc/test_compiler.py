#!/usr/bin/env python3
"""
test_compiler.py — COMPILE-layer oracle (phase 2 step 3c / 3c.1).

parse → compile, then assert the compile `status`, the emitted record `local_id`s (in
order), and the error-code set. STRUCTURAL only — no settlement (that is 3d; COMPILED
must not mean REPLAYED).

3c.1 invariants (Codex):
  - a binding is bound to its claim (same relation/target/status on different claims ⇒
    different binding_id — no composition laundering, §13.11);
  - the compiled bundle is SELF-CONTAINED: a 3d runner can drive settlement from the
    serialized records (id + canonical body) with the source Markdown deleted;
  - the same byte span in different documents ⇒ different occurrence identity;
  - the same canonical bytes in different record domains ⇒ different IDs.

Run:  ../../.venv/bin/python test_compiler.py   (needs the pinned parser deps)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import parser as P      # noqa: E402
import compiler as C    # noqa: E402
import canonical        # noqa: E402

GOLDEN = {
    "01-illustration-vs-live.md": ("COMPILED", ["T"], []),
    "02-multiple-claims.md": ("COMPILED", ["A", "B"], []),
    "03-nested-fences.md": ("COMPILED", [], []),
    "09-claim-inside-capsule.md": ("COMPILED", ["README-THESIS-COUNT"], []),
    "17-fake-end-in-fence.md": ("COMPILED", [], []),
    "24-binding-same-target.md": ("COMPILED", ["C1", "C2"], []),
    "05-unclosed-fence.md": ("REFUSED", None, ["PRECONDITION_NOT_VALID"]),
    "10-no-live-region.md": ("REFUSED", None, ["PRECONDITION_NOT_VALID"]),
    "11-unknown-profile.md": ("REFUSED", None, ["PRECONDITION_NOT_VALID"]),
    "13-marker-in-fence.md": ("REFUSED", None, ["PRECONDITION_NOT_VALID"]),
    "14-unexpected-end.md": ("REFUSED", None, ["PRECONDITION_NOT_VALID"]),
    "21-capsule-bad-json.md": ("INVALID", None, ["CAPSULE_NOT_STRICT_JSON"]),
    "22-capsule-schema-invalid.md": ("INVALID", None, ["CAPSULE_SCHEMA_INVALID"]),
    "23-duplicate-local-id.md": ("INVALID", None, ["DUPLICATE_LOCAL_ID"]),
}


def compile_file(name):
    with open(os.path.join(HERE, "fixtures/adversarial", name), "rb") as f:
        src = f.read()
    return C.compile_report(P.parse(src.decode("utf-8")), src)


def main():
    failures = 0
    for name, (status, ids, codes) in GOLDEN.items():
        rep = compile_file(name)
        problems = []
        if rep["status"] != status:
            problems.append(f"status={rep['status']} want {status}")
        if sorted({e["code"] for e in rep["errors"]}) != codes:
            problems.append(f"codes={sorted({e['code'] for e in rep['errors']})} want {codes}")
        if status == "COMPILED":
            got = [r["local_id"] for r in rep["records"]]
            if got != ids:
                problems.append(f"local_ids={got} want {ids}")
            for r in rep["records"]:
                if not (str(r["claim"]["id"]).startswith("sha256:")
                        and str(r["plan"]["id"]).startswith("sha256:")):
                    problems.append(f"record {r['local_id']} missing content-addressed ids")
        elif rep["records"]:
            problems.append(f"non-COMPILED report emitted {len(rep['records'])} records")
        print(("ok   " if not problems else "FAIL ") + name)
        for p in problems:
            print("       " + p)
            failures += 1

    print("\n-- invariants --")

    def inv(ok, label):
        nonlocal failures
        print(("ok   " if ok else "FAIL ") + label)
        failures += 0 if ok else 1

    # claim_id deterministic + distinct for distinct predicates
    r = compile_file("02-multiple-claims.md")
    r2 = compile_file("02-multiple-claims.md")
    inv([x["claim"]["id"] for x in r["records"]] == [x["claim"]["id"] for x in r2["records"]]
        and r["records"][0]["claim"]["id"] != r["records"][1]["claim"]["id"],
        "claim_id deterministic + distinct for distinct predicates")

    # P0: binding bound to its claim — same target, different claims ⇒ different binding_id
    rb = compile_file("24-binding-same-target.md")
    inv(rb["records"][0]["binding"]["id"] != rb["records"][1]["binding"]["id"],
        "binding_id differs for same target on different claims (no laundering)")

    # self-contained bundle: a runner can drive settlement from serialized records alone
    r09 = json.loads(json.dumps(compile_file("09-claim-inside-capsule.md")))  # round-trip
    rec = r09["records"][0]
    inv(rec["claim"]["body"]["class"] == "count"
        and rec["plan"]["body"]["verifier"].startswith("settle-gate://")
        and rec["dependency"]["body"]["sha256"]
        and "document" in rec["occurrence"],
        "compiled bundle is self-contained (verifier + dep body present; no source needed)")

    def synth(body_raw, prefix):
        src = prefix + body_raw.encode("utf-8")
        span = [len(prefix), len(prefix) + len(body_raw.encode("utf-8"))]
        pr = {"status": "VALID", "regions": [], "errors": [], "parser": "parser://sha256:t",
              "capsules": [{"line": 0, "span": span, "region": 0, "body_raw": body_raw}]}
        return pr, src

    CAP = ('{"schema_version":"manifesto.capsule.v2",'
           '"claim":{"local_id":"X","class":"arith","payload":"1 + 1 = 2"}}')

    # same span (equal-length prefixes), different documents ⇒ different occurrence id
    pa, sa = synth(CAP, b"AAAA")
    pb, sb = synth(CAP, b"BBBB")
    oa = C.compile_report(pa, sa)["records"][0]["occurrence_id"]
    ob = C.compile_report(pb, sb)["records"][0]["occurrence_id"]
    inv(oa != ob, "same span in different documents ⇒ different occurrence identity")

    # P0: plan names its inputs — changing the dependency rotates plan_id
    c1 = ('{"schema_version":"manifesto.capsule.v2","claim":{"local_id":"P","class":'
          '"count","payload":"/x/ in R = 1"},"verifier":"settle-gate://sha256:' + "a" * 64
          + '","dep":{"path":"R","sha256":"' + "1" * 64 + '"}}')
    c2 = c1.replace("1" * 64, "2" * 64)  # only the dependency digest differs
    p1, s1 = synth(c1, b""); p2, s2 = synth(c2, b"")
    r1 = C.compile_report(p1, s1)["records"][0]; r2 = C.compile_report(p2, s2)["records"][0]
    inv(r1["dependency"]["id"] != r2["dependency"]["id"]
        and r1["plan"]["id"] != r2["plan"]["id"],
        "changing the dependency rotates plan_id (plan names its inputs)")

    # P0: forged body_raw (≠ source[span]) is refused
    pf = {"status": "VALID", "regions": [], "errors": [], "parser": "parser://sha256:t",
          "capsules": [{"line": 0, "span": [0, 10], "region": 0, "body_raw": CAP}]}
    rf = C.compile_report(pf, b"YYYYYYYYYY")
    inv(rf["status"] == "INVALID" and rf["records"] == []
        and sorted({e["code"] for e in rf["errors"]}) == ["SOURCE_OCCURRENCE_MISMATCH"],
        "forged body_raw (≠ source[span]) ⇒ SOURCE_OCCURRENCE_MISMATCH, whole compile INVALID")

    # domain separation: identical canonical bytes in different domains ⇒ different IDs
    body = {"x": 1, "y": [2, 3]}
    inv(canonical.record_id("claim", body) != canonical.record_id("plan", body),
        "same canonical bytes in different record domains ⇒ different IDs")

    # end-to-end provenance: the compile report carries parser_id
    inv(str(compile_file("09-claim-inside-capsule.md").get("parser_id", ""))
        .startswith("parser://sha256:"),
        "compile report carries parser_id provenance")

    inv(C.compiler_id().startswith("compiler://sha256:") and C.compiler_id() == C.compiler_id(),
        "compiler_id binds compiler+canonical closure")

    print(f"\n{'ALL PASS' if failures == 0 else str(failures) + ' FAILED'} "
          f"({len(GOLDEN)} COMPILE specimens + 9 invariants) — structural; settlement is 3d")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
