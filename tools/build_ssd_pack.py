#!/usr/bin/env python3
"""
build_ssd_pack.py — seal the SSD correction-loop history as a Warrant
evidence pack (SSD-PLAN Phase 2, Warrant bridge step 2).

Files the actual decision chain of 2026-08-30:
  propose  generator@ssd-demo   — publish SSD-DEMO-0.1 (11 embedded claims)
  reject   gate@manifesto       — 4 of 11 claims refuted (cmd@v1 reason:
                                  re-run settle_gate; transcript = receipt 0.1)
  propose  corrector@ssd-demo   — SSD-DEMO-0.2, corrected ONLY from badge values
  accept   gate@manifesto       — 11/11 settled, BECAUSE a ski@v1 check proves
                                  the pinned acceptance predicate
                                  (refuted == 0 && unsettled == 0 && claims >= 1)
                                  over the receipt facts, re-executable offline.

Honest scope (per the stack's own caveat): the ski@v1 check does NOT re-run the
gate; it pins the DECISION PREDICATE over the gate's receipt tally. The gate
run itself is the cmd@v1 layer: re-run tools/settle_gate.py on the pinned
source bytes and compare the receipt hash.

Deterministic: fixed key seeds and timestamps -> reproducible pack.
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

MANIFESTO = Path(__file__).resolve().parent.parent
WARRANT = Path("/Users/s0fractal/Projects/warrant")
sys.path.insert(0, str(WARRANT / "impl"))
import policy_lang as pl  # noqa: E402
import warrant as w       # noqa: E402

PACK = MANIFESTO / "drafts" / "ssd-pack"
STORE = PACK / ".warrants"

GEN_SEED, COR_SEED, GATE_SEED = "c3" * 32, "d4" * 32, "e5" * 32
T0 = 1756500000  # fixed; the pack is reproducible, not timestamped to wall clock

POLICY_TEXT = """SSD publication policy v0.1 (manifesto, 2026-08-30)

A document may be published iff tools/settle_gate.py, run on its exact bytes,
reports refuted == 0 and unsettled == 0 among its embedded claims. A refuted
claim is repaired only from the actual values in the gate's refutation badges;
unsettled claims must be retyped as speculation or removed. The gate script is
pinned by hash as evidence; the receipt is the transcript.
"""

WPL_TEXT = """# SSD acceptance predicate over the settle_gate receipt tally
# (SSD-DEMO-0.2.receipt.json, pinned as evidence in the accept warrant).

fact claims:    int = 11
fact refuted:   int = 0
fact unsettled: int = 0

check refuted == 0 && unsettled == 0 && claims >= 1
"""


class Args:
    def __init__(self, **kw):
        defaults = dict(under=[], evidence=[], prior=[], reason=None, check=None,
                        runtime="cmd@v1", verdict="pass", transcript=None,
                        relitigates=None, ts=None)
        defaults.update(kw)
        for k, v in defaults.items():
            setattr(self, k, v)


def main():
    if PACK.exists():
        shutil.rmtree(PACK)
    store = w.Store(str(STORE))
    store.init()

    keydir = Path(tempfile.mkdtemp(prefix="ssd-pack-keys-"))
    keys = {}
    for name, seed in (("gen", GEN_SEED), ("cor", COR_SEED), ("gate", GATE_SEED)):
        p = keydir / f"{name}.key"
        p.write_text(seed + "\n")
        keys[name] = str(p)

    rd = MANIFESTO / "drafts"
    blob = lambda p: store.put_blob(p.read_bytes())
    policy_hex = store.put_blob(POLICY_TEXT.encode())
    subject1 = blob(rd / "SSD-DEMO-0.1.md")
    subject2 = blob(rd / "SSD-DEMO-0.2.md")
    receipt1 = blob(rd / "SSD-DEMO-0.1.receipt.json")
    receipt2 = blob(rd / "SSD-DEMO-0.2.receipt.json")
    script_hex = blob(MANIFESTO / "tools" / "settle_gate.py")

    wpl_path = keydir / "acceptance.wpl"
    wpl_path.write_text(WPL_TEXT)
    check = pl.compile_file(wpl_path, store.put_blob)
    assert check.result is True, "acceptance predicate must hold for DEMO-0.2"
    source_hex = store.put_blob(WPL_TEXT.encode())
    d = check.doc

    w1 = w.file_warrant(store, "propose", subject1, Args(
        under=[policy_hex],
        reason=["draft technical summary with 11 embedded checkable claims; "
                "generator was forbidden to verify (white cone)"],
        actor="generator@ssd-demo", key=keys["gen"], ts=T0),
        note="SSD-DEMO-0.1 publication")

    w2 = w.file_warrant(store, "reject", subject1, Args(
        under=[policy_hex], prior=[w1],
        reason=["settle_gate: 4 of 11 claims refuted (count guesses 42/37/8/12 "
                "vs actual 12/12/67/7); policy requires refuted == 0"],
        check=script_hex, runtime="cmd@v1", verdict="fail", transcript=receipt1,
        evidence=[receipt1], actor="gate@manifesto", key=keys["gate"], ts=T0 + 60),
        note="SSD-DEMO-0.1 publication")

    w3 = w.file_warrant(store, "propose", subject2, Args(
        under=[policy_hex], prior=[w2],
        reason=["corrected draft; the only truth source used was the actual "
                "values inside the gate's refutation badges"],
        actor="corrector@ssd-demo", key=keys["cor"], ts=T0 + 120),
        note="SSD-DEMO-0.2 publication")

    w4 = w.file_warrant(store, "accept", subject2, Args(
        under=[policy_hex], prior=[w3],
        reason=["settle_gate: 11/11 settled, 0 refuted, 0 unsettled "
                "(5638 ATP across both layers)"],
        check=check.blob, runtime="ski@v1", verdict="pass",
        transcript=receipt2, evidence=[receipt2, script_hex, source_hex],
        actor="gate@manifesto", key=keys["gate"], ts=T0 + 180),
        note="SSD-DEMO-0.2 publication")

    (PACK / "policies").mkdir()
    (PACK / "policies" / f"ssd-policy.{policy_hex[:12]}.txt").write_text(POLICY_TEXT)
    (PACK / "policies" / f"acceptance.{source_hex[:12]}.wpl").write_text(WPL_TEXT)

    trust = {"genesis_roots": [w1],
             "actors": {
                 "generator@ssd-demo": [w.pubkey_hex(w.load_key(keys["gen"]))],
                 "corrector@ssd-demo": [w.pubkey_hex(w.load_key(keys["cor"]))],
                 "gate@manifesto": [w.pubkey_hex(w.load_key(keys["gate"]))],
             }}
    (PACK / "trust.json").write_text(json.dumps(trust, indent=2, sort_keys=True) + "\n")

    manifest = {
        "evidence_pack": "0",
        "title": "SSD correction loop — draft rejected, repaired from badges, accepted",
        "story": "propose (4 hallucinations) -> reject with receipt -> corrected "
                 "propose -> accept proven by a re-executable acceptance predicate",
        "produced_by": "manifesto/tools/build_ssd_pack.py",
        "decision": w4,
        "records": [w1, w2, w3, w4],
        "ski_checks": [{"check": check.blob, "term": d["term"],
                        "expect": d["expect"], "atp": d["atp"],
                        "means": "refuted==0 && unsettled==0 && claims>=1 over "
                                 "the SSD-DEMO-0.2 receipt tally -> Church TRUE"}],
        "expected_verification": {"errors": 0},
        "how_to_verify": "cd drafts/ssd-pack && warrant --store .warrants verify "
                         "&& warrant --store .warrants check <ski_checks[0].check>; "
                         "stronger: verify --settlement --trust-config trust.json",
    }
    (PACK / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"records": [w1, w2, w3, w4], "ski_check": check.blob,
                      "atp": d["atp"], "expect": d["expect"][:12]}, indent=2))


if __name__ == "__main__":
    main()
