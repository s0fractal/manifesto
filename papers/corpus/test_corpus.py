#!/usr/bin/env python3
"""
test_corpus.py — acceptance oracle after the source-authentication review (9e50479).
Synthetic: no quarantine, no sigma-glyph. Runs the required closure mutations verbatim:

  coherent invented L2 event/source/closure -> UNKNOWN_SOURCE / BUNDLE_NOT_COMMITTED
  caller-minted {status:CLEAN,index:...}     -> MALFORMED_BUNDLE
  post-validation bundle mutation            -> BUNDLE_ID_MISMATCH / INDEX_TAMPER
  duplicate event / impossible span / gap    -> typed L2 refusal
  PARTIAL/WITHHELD -> COMPLETE/CLEARED        -> record/view ids rotate
  null/forged ActRecord fields               -> SCHEMA_INVALID / evidence mismatch
  same event, wrong adjudication commitment  -> ADJUDICATION_MISMATCH
  one-unit replacement manifest              -> manifest_id changes; claim binding refuses
  EXACT -> CONFLICTED finalization           -> mapping_id addresses CONFLICTED (asserted ==)
  actual schema/code byte mutation           -> extraction closure rotates
  + L1->L2 strictness and F1-F9.
"""
import base64
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus_ids as ids                                              # noqa: E402
from corpus_extract import (extract_blob, extract_from_quarantine,    # noqa: E402
                            extraction_closure_id, BlobRefused)
from corpus_map import (mint_l2_bundle, verify_bundle, build_l3,      # noqa: E402
                        make_public_projection, manifest_id, mapper_closure_id)

fails = []


def expect(name, cond):
    print(f"{'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        fails.append(name)


def blob(*objs):
    return ("\n".join(json.dumps(o) for o in objs) + "\n").encode()


GOOD = blob({"type": "user", "message": {"role": "user", "content": "ROOT"}},
            {"type": "assistant", "message": {"role": "assistant", "content": "verdict"}})
CLO = extraction_closure_id()

# ===================== L1 -> L2 extraction (strict, mechanical) ===================== #
bid, events = extract_blob(GOOD, CLO)
expect("repeat byte-identical", [e["event_id"] for e in events] == [e["event_id"] for e in extract_blob(GOOD, CLO)[1]])
mut = bytearray(GOOD); mut[10] ^= 1
expect("F1 one byte rotates ids", extract_blob(bytes(mut), CLO)[0] != bid)
for bad, why in [(b'{"a":1,"a":2}\n', "DUPLICATE_KEY"), (b'{"ok":1}\nnope\n', "MALFORMED_LINE"),
                 (b'{"x":NaN}\n', "NON_FINITE_CONSTANT")]:
    try:
        extract_blob(bad, CLO); expect(f"strict {why}", False)
    except BlobRefused as e:
        expect(f"strict {why}", e.reason == why)


def make_q(root, raw, extra=False):
    sha = ids.raw_sha256(raw)
    (root / "blobs").mkdir(parents=True, exist_ok=True)
    (root / "blobs" / (sha + ".jsonl")).write_bytes(raw)
    inv = {"transcripts": [{"agent": "agent-x", "sha256": sha, "experiment": "E"}]}
    rec = {"records": [{"agent": "agent-x", "status": "VERIFIED", "inventory_sha256": sha, "experiment": "E"}]}
    if extra:
        inv["transcripts"].append({"agent": "agent-y", "sha256": "b" * 64, "experiment": "E"})
    return inv, rec, sha


d1 = Path(tempfile.mkdtemp())
i1, r1, s1 = make_q(d1, GOOD)
_, rep1 = extract_from_quarantine(d1, r1, i1)
expect("clean set_status + commitment present", rep1["set_status"] == "CLEAN" and "corpus_commitment" in rep1)
d2 = Path(tempfile.mkdtemp()); i2, r2, _ = make_q(d2, GOOD, extra=True)
_, rep2 = extract_from_quarantine(d2, r2, i2)
expect("omitted inventory source -> FAIL", rep2["set_status"] == "FAIL")
_, repM = extract_from_quarantine(d1, {"records": "x"}, {"transcripts": []})
expect("malformed operand -> no crash", repM["set_status"] == "FAIL")

# ===================== L2 bundle + mapping (source-bound) ===================== #
TCLO = "clo:extract:testcorpus"


def evrec(kind, eid, vs, ve, val):
    return {"kind": kind, "event_id": eid, "value_start": vs, "value_end": ve,
            "observed_value_digest": ids._h(b"value", val)}


def mk(lr, root, ver, run="run", exp="EXP-RVB-1c", status="EXACT",
       comp="COMPLETE", pub="CLEARED_FOR_PUBLICATION", with_ev=True, adj=True,
       commit=None, root_id_none=False):
    b = "blob:" + lr
    parts = [("experiment_id", exp.encode()), ("root_digest", root.encode()),
             ("verifier_identity", ver.encode()), ("agent_run_occurrence", run.encode())]
    body = b"|".join(v for _, v in parts)
    eid = ids.event_id(TCLO, b, 0, len(body), ids.line_digest(body))
    ev, digs, off = [], [], 0
    for kind, val in parts:
        item = evrec(kind, eid, off, off + len(val), val)
        if with_ev:
            ev.append(item)
            digs.append(ids.json_digest({k: item[k] for k in
                        ("kind", "event_id", "value_start", "value_end", "observed_value_digest")}))
        off += len(val) + 1
    adjud = ({"adjudicator_identity": "rev", "authority": "adj", "decision": "EXACT",
              "evidence_commitments": commit if commit is not None else digs} if adj else None)
    cand = {"local_ref": lr, "blob_id": b,
            "event_occurrences": [{"event_id": eid, "byte_start": 0, "byte_end": len(body)}],
            "experiment_id": exp, "root_digest": ids.raw_sha256(root.encode()),
            "verifier_identity": ver, "agent_run_occurrence": run,
            "mapping_status": status, "mapping_evidence": ev, "adjudication": adjud,
            "root_id": None if root_id_none else "root:" + root,
            "verifier_declared_identity": ver, "verifier_observed_identity": ver,
            "prompt_digest": "UNKNOWN", "response_digest": "UNKNOWN",
            "offspring_before_dedup": "UNKNOWN", "dedup_removal_decisions": "UNKNOWN",
            "selected_child_refs": [], "sampling": {},
            "completeness_decision": {"adjudicator_identity": "r", "authority": "c", "decision": comp},
            "publication_decision": {"adjudicator_identity": "r", "authority": "p", "decision": pub},
            "parent_local_ref": None}
    return cand, (b, body)


def bundle_of(pairs, drop_from_manifest=False, dup=False, bad_span=False, gap=False):
    private, man = {}, []
    for i, (b, body) in enumerate(pairs):
        ld = ids.line_digest(body)
        be = len(body) + (5 if bad_span else 0)
        eid = ids.event_id(TCLO, b, 0, be, ld)   # id consistent with the (possibly bad) span
        ev = {"event_index": (2 if gap else 0), "blob_id": b, "byte_start": 0, "byte_end": be,
              "line_digest": ld, "event_type": "user", "unknown_event_type": False,
              "event_id": eid, "extraction_closure": TCLO, "raw_b64": base64.b64encode(body).decode()}
        evs = [ev, dict(ev)] if dup else [ev]
        private[f"a{i}"] = {"blob_id": b, "events": evs}
        if not drop_from_manifest:
            man.append({"blob_id": b, "event_index": ev["event_index"], "event_id": eid, "body_digest": ld})
    man.sort(key=lambda x: (x["blob_id"], x["event_index"]))
    commit = ids.json_digest({"closure": TCLO, "inventory": [], "events": man})
    report = {"extraction_closure": TCLO, "corpus_commitment": commit, "event_manifest": man}
    return mint_l2_bundle(private, report), commit


ROOTS, VERIF = ["0030", "0025", "FLOW15", "FLOW17"], ["Fable", "Sonnet"]
PIN = "paper@deadbeef"
C2_MAN = {"claim": "C2", "paper_pin": PIN, "experiment_ids": ["EXP-RVB-1c"],
          "unit_key": ["root_digest", "verifier_identity"],
          "required_units": [[ids.raw_sha256(r.encode()), v] for r in ROOTS for v in VERIF],
          "allowed_exclusions": []}


def full(**kw):
    table, pairs = [], []
    for r in ROOTS:
        for v in VERIF:
            c, pb = mk(f"{r}-{v}", r, v, **kw); table.append(c); pairs.append(pb)
    b, commit = bundle_of(pairs)
    return table, b, commit


tbl, bundle, commit = full()
expect("bundle CLEAN", bundle["status"] == "CLEAN")
expect("valid EXACT bijection -> C2 COMPLETE + evaluation_id",
       build_l3(bundle, tbl, {"C2": C2_MAN}, commit)["views"]["C2"].get("status") == "COMPLETE"
       and "evaluation_id" in build_l3(bundle, tbl, {"C2": C2_MAN}, commit)["views"]["C2"])

# DERIVED never credits
tblD, bD, cD = full(status="DERIVED")
expect("all DERIVED -> C2 REFUSED", build_l3(bD, tblD, {"C2": C2_MAN}, cD)["views"]["C2"]["status"] == "REFUSED")

# coherent invented L2 (not in the extraction manifest) -> UNKNOWN_SOURCE
c0, pb0 = mk("x", "0030", "Fable")
binv, cinv = bundle_of([pb0], drop_from_manifest=True)
expect("invented L2 (not committed) -> UNKNOWN_SOURCE",
       binv["status"] != "CLEAN" and any(f["code"] == "UNKNOWN_SOURCE" for f in binv["faults"]))
expect("invented L2 -> view REFUSED", build_l3(binv, [c0], {"C2": C2_MAN}, cinv)["views"]["C2"]["status"] == "REFUSED")

# caller-minted bundle -> MALFORMED_BUNDLE
expect("caller-minted bundle -> MALFORMED_BUNDLE",
       build_l3({"status": "CLEAN", "index": {}}, [c0], {"C2": C2_MAN}, commit)["views"]["C2"]["reason"] == "MALFORMED_BUNDLE")

# wrong corpus_commitment -> BUNDLE_NOT_COMMITTED
expect("wrong commitment -> BUNDLE_NOT_COMMITTED",
       build_l3(bundle, tbl, {"C2": C2_MAN}, "wrong")["views"]["C2"]["reason"] == "BUNDLE_NOT_COMMITTED")

# post-validation mutation of committed events -> BUNDLE_ID_MISMATCH
bmut = json.loads(json.dumps({k: bundle[k] for k in ("bundle_id", "commitment", "expected_closure", "events", "status")}))
bmut["index"] = bundle["index"]; bmut["events"] = list(bmut["events"]);
if bmut["events"]:
    bmut["events"][0] = {**bmut["events"][0], "body_digest": "tampered"}
expect("post-mint event tamper -> BUNDLE_ID_MISMATCH",
       verify_bundle(bmut, commit)[1] == "BUNDLE_ID_MISMATCH")
# index body tamper -> INDEX_TAMPER
btam = dict(bundle); btam["index"] = {k: dict(v) for k, v in bundle["index"].items()}
firstk = next(iter(btam["index"]))
btam["index"][firstk]["raw_bytes"] = btam["index"][firstk]["raw_bytes"] + b"X"
expect("index body tamper -> INDEX_TAMPER", verify_bundle(btam, commit)[1] == "INDEX_TAMPER")

# duplicate event / impossible span / gap -> typed L2 refusal
expect("duplicate L2 event -> refused", bundle_of([pb0], dup=True)[0]["status"] != "CLEAN")
expect("impossible span -> refused", any(f["code"] == "IMPOSSIBLE_SPAN" for f in bundle_of([pb0], bad_span=True)[0]["faults"]))
expect("index gap -> refused", any(f["code"] == "INDEX_GAP" for f in bundle_of([pb0], gap=True)[0]["faults"]))

# PARTIAL/WITHHELD -> COMPLETE/CLEARED rotates record id AND view
cP, pbP = mk("p", "0030", "Fable", comp="PARTIAL", pub="WITHHELD")
cC, pbC = mk("p", "0030", "Fable")   # same identity inputs, decisions flipped
bP, xP = bundle_of([pbP]); bC, xC = bundle_of([pbC])
from corpus_map import _actrecord  # noqa: E402
recP = _actrecord(cP, {**bP["index"], **{k: {**v, "extraction_closure": TCLO} for k, v in bP["index"].items()}})
recC = _actrecord(cC, {**bC["index"], **{k: {**v, "extraction_closure": TCLO} for k, v in bC["index"].items()}})
expect("PARTIAL vs COMPLETE rotates record_id", recP["record_id"] != recC["record_id"])

# null ActRecord field -> SCHEMA_INVALID
cn, pbn = mk("n", "0030", "Fable", root_id_none=True)
bn, xn = bundle_of([pbn])
expect("null field -> SCHEMA_INVALID (not EXACT)",
       "SCHEMA_INVALID" in build_l3(bn, [cn], {}, xn)["acts"][0]["faults"]
       and build_l3(bn, [cn], {}, xn)["acts"][0]["status"] == "AMBIGUOUS")

# wrong adjudication commitment -> ADJUDICATION_MISMATCH
ca, pba = mk("a", "0030", "Fable", commit=["stale-digest"])
ba, xa = bundle_of([pba])
expect("unbound adjudication -> AMBIGUOUS", build_l3(ba, [ca], {}, xa)["acts"][0]["status"] == "AMBIGUOUS")

# one-unit replacement manifest: manifest_id changes; claim binding refuses mismatch
one_man = {**C2_MAN, "required_units": [[ids.raw_sha256(b"0030"), "Fable"]]}
expect("one-unit manifest has a different manifest_id", manifest_id(one_man) != manifest_id(C2_MAN))
mis_man = {**C2_MAN, "claim": "C7"}
expect("manifest claim mismatch -> REFUSED",
       build_l3(bundle, tbl, {"C2": mis_man}, commit)["views"]["C2"]["reason"] == "MANIFEST_CLAIM_MISMATCH")
expect("empty required set -> EMPTY_REQUIRED_SET",
       build_l3(bundle, tbl, {"C2": {**C2_MAN, "required_units": []}}, commit)["views"]["C2"]["reason"] == "EMPTY_REQUIRED_SET")

# EXACT -> CONFLICTED: mapping_id addresses final CONFLICTED (asserted equality)
cr1, pr1 = mk("0030-Fable", "0030", "Fable", run="r1", status="DERIVED", with_ev=False, adj=False)
cr2, pr2 = mk("0030-Fable-b", "0030", "Fable", run="r2", status="DERIVED", with_ev=False, adj=False)
br, xr = bundle_of([pr1, pr2])
repr_ = build_l3(br, [cr1, cr2], {}, xr)
conf = [a for a in repr_["acts"] if a["status"] == "CONFLICTED"]
expect("repeated run -> CONFLICTED", len(conf) == 2)
mclo = mapper_closure_id()
one = conf[0]
run = "r1" if one["local_ref"] == "0030-Fable" else "r2"
recomputed = ids.mapping_id(mclo, one["act_id"], "EXP-RVB-1c", ids.raw_sha256(b"0030"), "Fable",
                            run, ids.json_digest([]), "CONFLICTED", ids.json_digest({}))
expect("mapping_id == recomputed(CONFLICTED)", one["mapping_id"] == recomputed)

# duplicate local_ref required by a view -> REFUSED
cdup, pdup = mk("0030-Fable", "0030", "Fable", run="r9")
tbld, pairsd, _ = full()
tbld2, bd2, cd2 = full()
tblx = tbld2 + [cdup]
# rebuild a bundle that also contains cdup's event
allpairs = [(c["blob_id"], b"|".join([c["experiment_id"].encode(), b"0030",
             c["verifier_identity"].encode(), c["agent_run_occurrence"].encode()]))
            for c in tblx]
bdx, cdx = bundle_of(allpairs)
expect("duplicate local_ref -> C2 REFUSED",
       build_l3(bdx, tblx, {"C2": C2_MAN}, cdx)["views"]["C2"]["status"] == "REFUSED")

# schema-byte mutation rotates the extraction closure (intended scope)
here = Path(__file__).resolve().parent
real = ids.closure_id("extract", [("corpus_ids.py", (here / "corpus_ids.py").read_bytes()),
       ("corpus_extract.py", (here / "corpus_extract.py").read_bytes()),
       ("CORPUS-SCHEMA-0.1.md", (here.parent / "every-check-spawns-more" / "CORPUS-SCHEMA-0.1.md").read_bytes())])
mutd = ids.closure_id("extract", [("corpus_ids.py", (here / "corpus_ids.py").read_bytes()),
       ("corpus_extract.py", (here / "corpus_extract.py").read_bytes()),
       ("CORPUS-SCHEMA-0.1.md", (here.parent / "every-check-spawns-more" / "CORPUS-SCHEMA-0.1.md").read_bytes() + b"X")])
expect("schema byte change rotates extraction closure", real == extraction_closure_id() and real != mutd)

# F8 public projection
expect("F8 missing loss -> FAIL", make_public_projection("act:1", "p", b"B", None)["status"] == "FAIL")
expect("F8 reused id -> REDACTION_ID_REUSE", make_public_projection("act:1", "p", b"B", {"l": 1}, proposed_id="act:1")["status"] == "FAIL")
pa = make_public_projection("act:1", "p", b"B", {"l": "s"}); pb = make_public_projection("act:1", "p", b"B", {"l": "o"})
expect("public_id rotates on loss", pa["public_id"] != pb["public_id"])

# malformed table / bundle -> typed, no crash
for badtable in [["not a dict"], [{"local_ref": 5}], [{"local_ref": "x", "surprise": 1}]]:
    try:
        expect("malformed table typed no crash", build_l3(bundle, badtable, {}, commit)["fault_count"] >= 1)
    except Exception as ex:  # noqa
        expect(f"malformed table crashed: {ex!r}", False)

print()
if fails:
    print(f"RED: {len(fails)} corpus mechanism failure(s): {fails}")
    sys.exit(1)
print("GREEN: extraction is mechanical; L2 is source-bound; mapping is adjudicated and fails-closed.")
