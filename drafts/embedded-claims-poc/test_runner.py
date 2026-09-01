#!/usr/bin/env python3
"""
test_runner.py — 3d verifier/runner oracle: the frozen boundary as executable negatives.

Bundles are built at runtime with the ACTUAL runtime verifier ids (so nothing is pinned
to a committed hash), compiled through the real parser+compiler, then run. Checks:
  - status != COMPILED ⇒ whole-bundle refusal, evaluator invocations == 0;
  - any bundle mutation ⇒ typed refusal, evaluator invocations == 0;
  - a real claim replays (REPLAYED) and a false one MISMATCHes;
  - one REPLAYED + one MISMATCH ⇒ two separate results, NO document-level MATCH;
  - correct replay + binding ASSERTED ⇒ binding stays ASSERTED;
  - stale / missing dependency ⇒ no replay credit;
  - a serialized bundle runs after the source Markdown is gone;
  - the REPORT preserves parser_id, compiler_id, runner id, verifier identity, operand ids.

Run:  ../../.venv/bin/python test_runner.py   (needs pinned parser deps + sigma-glyph)
"""
import copy
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import parser as P        # noqa: E402
import compiler as C      # noqa: E402
import runner as R        # noqa: E402
import settle_core as sc  # noqa: E402

GLYPH = sc.verifier_id("sigma-glyph")
SETTLE = sc.verifier_id("repo")
README_SHA = hashlib.sha256(open(os.path.join(REPO, "README.md"), "rb").read()).hexdigest()


def _doc(capsules):
    blocks = "\n\n".join("```json capsule\n" + json.dumps(c, ensure_ascii=False) + "\n```"
                         for c in capsules)
    doc = ("<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->\n\n"
           + blocks + "\n\n<!-- manifesto-claims:end -->\n")
    return doc.encode("utf-8")


def compiled(*capsules):
    src = _doc(capsules)
    return C.compile_report(P.parse(src.decode("utf-8")), src)


def cap(local_id, cls, payload, verifier=None, dep=None, binding=None):
    c = {"schema_version": "manifesto.capsule.v2",
         "claim": {"local_id": local_id, "class": cls, "payload": payload}}
    if verifier:
        c["verifier"] = verifier
    if dep:
        c["dep"] = dep
    if binding:
        c["binding"] = binding
    return c


def main():
    failures = 0
    checks = 0

    def inv(ok, label):
        nonlocal failures, checks
        checks += 1
        print(("ok   " if ok else "FAIL ") + label)
        failures += 0 if ok else 1

    # a true self-contained arithmetic claim replays
    rep = R.run(compiled(cap("A", "arith", "74 + 1 = 75", verifier=GLYPH)))
    inv(rep["status"] == "RUN" and rep["evaluator_invocations"] == 1
        and rep["results"][0]["execution"] == "REPLAYED", "true arith claim ⇒ REPLAYED")

    # a false one mismatches
    rep = R.run(compiled(cap("A", "arith", "74 + 1 = 76", verifier=GLYPH)))
    inv(rep["results"][0]["execution"] == "MISMATCH", "false arith claim ⇒ MISMATCH")

    # vector: one REPLAYED + one MISMATCH, NO document-level MATCH
    rep = R.run(compiled(cap("A", "arith", "74 + 1 = 75", verifier=GLYPH),
                         cap("B", "arith", "1 + 1 = 3", verifier=GLYPH)))
    execs = {r["local_id"]: r["execution"] for r in rep["results"]}
    inv(len(rep["results"]) == 2 and execs["A"] == "REPLAYED" and execs["B"] == "MISMATCH"
        and "execution" not in rep and "status" in rep and rep["status"] == "RUN",
        "two records ⇒ two results, no document-level MATCH (vector)")

    # correct replay + binding ASSERTED ⇒ binding stays ASSERTED (never raised)
    rep = R.run(compiled(cap("A", "arith", "74 + 1 = 75", verifier=GLYPH,
                             binding={"relation": "measures", "target": "t", "status": "ASSERTED"})))
    inv(rep["results"][0]["execution"] == "REPLAYED"
        and rep["results"][0]["binding"] == "ASSERTED",
        "replay does not raise binding above ASSERTED")

    # world claim: correct dependency ⇒ REPLAYED; stale ⇒ STALE; missing ⇒ UNVERIFIED
    payload = "/^## Теза [0-9]+:/ in README.md = 7"
    ok = R.run(compiled(cap("A", "count", payload, verifier=SETTLE,
                            dep={"path": "README.md", "sha256": README_SHA})))
    stale = R.run(compiled(cap("A", "count", payload, verifier=SETTLE,
                               dep={"path": "README.md", "sha256": "0" * 64})))
    missing = R.run(compiled(cap("A", "count", payload, verifier=SETTLE)))
    inv(ok["results"][0]["execution"] == "REPLAYED", "world claim + fresh dep ⇒ REPLAYED")
    inv(stale["results"][0]["execution"] == "STALE", "world claim + stale dep ⇒ STALE")
    inv(missing["results"][0]["execution"] == "UNVERIFIED"
        and "DEPENDENCY_MISSING" in missing["results"][0]["execution_facts"],
        "world claim + missing dep ⇒ no replay credit")

    # status != COMPILED ⇒ whole-bundle refusal, evaluator invocations == 0
    invalid = C.compile_report({"status": "INERT", "capsules": [], "parser": "x"}, b"")
    rep = R.run(invalid)
    inv(rep["status"] == "REFUSED" and rep["reason"] == "NOT_COMPILED"
        and rep["evaluator_invocations"] == 0, "status != COMPILED ⇒ refused, 0 evaluator calls")

    # any mutation of an id/body/link ⇒ typed refusal, evaluator invocations == 0
    good = compiled(cap("A", "arith", "74 + 1 = 75", verifier=GLYPH))
    for mut_label, mutate in [
        ("claim.id", lambda b: b["records"][0]["claim"].__setitem__("id", "sha256:" + "d" * 64)),
        ("plan.body.verifier", lambda b: b["records"][0]["plan"]["body"].__setitem__("verifier", None)),
        ("capsule.body.payload", lambda b: b["records"][0]["capsule"]["body"]["claim"].__setitem__("payload", "9 + 9 = 18")),
        ("occurrence", lambda b: b["records"][0]["occurrence"].__setitem__("span", [0, 0])),
    ]:
        t = copy.deepcopy(good)
        mutate(t)
        rep = R.run(t)
        inv(rep["status"] == "REFUSED" and rep["reason"] == "BUNDLE_TAMPERED"
            and rep["evaluator_invocations"] == 0,
            f"mutation of {mut_label} ⇒ refused before evaluator (0 invocations)")

    # a serialized bundle runs after the source Markdown is gone (no reparse)
    serialized = json.dumps(compiled(cap("A", "arith", "74 + 1 = 75", verifier=GLYPH)))
    rep = R.run(json.loads(serialized))
    inv(rep["status"] == "RUN" and rep["results"][0]["execution"] == "REPLAYED",
        "serialized bundle runs with no source Markdown")

    # the REPORT preserves provenance and operand ids
    rep = R.run(compiled(cap("A", "arith", "74 + 1 = 75", verifier=GLYPH)))
    r0 = rep["results"][0]
    inv(str(rep["runner"]).startswith("runner://")
        and str(rep["parser_id"]).startswith("parser://")
        and str(rep["compiler_id"]).startswith("compiler://")
        and str(r0["verifier"]).startswith("glyph://")
        and str(r0["claim_id"]).startswith("sha256:")
        and str(r0["plan_id"]).startswith("sha256:")
        and str(r0["capsule_id"]).startswith("sha256:"),
        "REPORT preserves parser/compiler/runner/verifier ids + operand ids")

    print(f"\n{'ALL PASS' if failures == 0 else str(failures) + ' FAILED'} "
          f"({checks} runner-boundary checks) — prose→region→capsule→bundle→vector REPORT")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
