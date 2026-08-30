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
import sigma_glyph as wsg  # noqa: E402  (warrant's bundled Book I oracle)

# glyphlib is used ONLY for its pure lambda layer (compile_l, church, PLUS, A);
# its own `import sigma_glyph` resolves to warrant's bundle already in
# sys.modules, which is exactly what we want for byte-identical terms.
sys.path.insert(0, str(MANIFESTO / "tools"))
import glyphlib as gl  # noqa: E402

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


def build_aie_check(store):
    """AIE-0.1 as a raw ski@v1 check: term = (PLUS 74 1) F X, expect = the
    NodeHash of its normal form F^75(X) — a NON-boolean expect, legal per
    validate_ski_blob and per run_ski_check's plain hash comparison. This is
    the 'addressing is equality' idiom carried verbatim into a warrant record:
    re-execution reproduces the canonical 75-mark or the check fails.
    Returns (check_hex, term_hex, expect_hex, atp)."""
    tree = gl.compile_l(gl.A(gl.PLUS, gl.church(74), gl.church(1),
                             ("lit", b"F"), ("lit", b"X")))

    def to_w(t):
        if t[0] == "a":
            return ("app", to_w(t[1]), to_w(t[2]))
        if t[0] in ("S", "K", "I"):
            return ("lit", wsg.sha(t[0].encode()))
        if t[0] == "lit":
            return ("lit", wsg.sha(t[1]))
        raise ValueError(t)

    term = to_w(tree)

    def materialize(t, put):
        if t[0] == "app":
            materialize(t[1], put)
            materialize(t[2], put)
        return put(wsg.term_bytes(t))

    term_hex = materialize(term, store.put_blob)

    priv = wsg.Store()
    for b in (wsg.I_BYTES, wsg.K_BYTES, wsg.S_BYTES):
        priv.put(b)

    def load(t):
        if t[0] == "app":
            load(t[1]); load(t[2])
        priv.put(wsg.term_bytes(t))
    load(term)
    result, atp = wsg.eval_hash(bytes.fromhex(term_hex), 100_000, priv)
    expect_hex = wsg.term_hash(result).hex()
    doc = {"ski": 1, "term": term_hex, "atp": atp, "expect": expect_hex}
    raw = json.dumps(doc, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=False).encode("utf-8")
    assert w.validate_ski_blob(json.loads(raw)) is None
    check_hex = store.put_blob(raw)
    return check_hex, term_hex, expect_hex, atp


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
    aie_check, aie_term, aie_expect, aie_atp = build_aie_check(store)

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
                                 "the SSD-DEMO-0.2 receipt tally -> Church TRUE"},
                       {"check": aie_check, "term": aie_term,
                        "expect": aie_expect, "atp": aie_atp,
                        "means": "AIE-0.1 raw NF check (non-boolean expect): "
                                 "(PLUS 74 1) F X normalizes to the 75-mark "
                                 "F^75(X) — the demo claim 74+1=75, settled by "
                                 "addressing"}],
        "expected_verification": {"errors": 0},
        "how_to_verify": "cd drafts/ssd-pack && warrant --store .warrants verify "
                         "&& warrant --store .warrants check <ski_checks[0].check>; "
                         "stronger: verify --settlement --trust-config trust.json",
    }
    (PACK / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"records": [w1, w2, w3, w4], "ski_check": check.blob,
                      "atp": d["atp"], "expect": d["expect"][:12],
                      "aie_check": aie_check, "aie_atp": aie_atp,
                      "aie_expect": aie_expect[:12]}, indent=2))


if __name__ == "__main__":
    main()
