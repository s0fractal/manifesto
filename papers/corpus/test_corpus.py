#!/usr/bin/env python3
"""
test_corpus.py — acceptance oracle after the trust-root review (f532023).
Synthetic; no quarantine, no sigma-glyph. Runs the governance closure mutations:

  coherent invented report + commitment  -> REPORT_NOT_PINNED
  set_status=FAIL report                 -> REPORT_NOT_CLEAN
  implicit event subset                  -> SET_MISMATCH
  index address / remove-entry mutation  -> BUNDLE_ID_MISMATCH
  L2_REFUSED -> CLEAN flag flip          -> BUNDLE_ID_MISMATCH
  self-issued authority                  -> AUTHORITY_NOT_ADMITTED
  replacement one-unit manifest          -> MANIFEST_NOT_PINNED
  graph EXACT -> CONFLICTED              -> final record_id rotates
  serialized private L3 only             -> full record bodies present (L4 can replay)
  mapper/profile mutation                -> evaluation identity rotates
"""
import base64
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus_ids as ids                                              # noqa: E402
from corpus_extract import extract_blob, extract_from_quarantine, extraction_closure_id, BlobRefused  # noqa: E402
from corpus_map import (mint_l2_bundle, verify_bundle, build_l3, recompute_report_id,  # noqa: E402
                        make_public_projection, manifest_id, mapper_closure_id)

fails = []


def expect(name, cond):
    print(f"{'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        fails.append(name)


def blob(*objs):
    return ("\n".join(json.dumps(o) for o in objs) + "\n").encode()


GOOD = blob({"type": "user"}, {"type": "assistant"})
CLO = extraction_closure_id()
bid, evs = extract_blob(GOOD, CLO)
expect("repeat byte-identical", [e["event_id"] for e in evs] == [e["event_id"] for e in extract_blob(GOOD, CLO)[1]])
for bad, why in [(b'{"a":1,"a":2}\n', "DUPLICATE_KEY"), (b'{"x":NaN}\n', "NON_FINITE_CONSTANT")]:
    try:
        extract_blob(bad, CLO); expect(why, False)
    except BlobRefused as e:
        expect(f"strict {why}", e.reason == why)
d = Path(tempfile.mkdtemp()); sha = ids.raw_sha256(GOOD)
(d / "blobs").mkdir(parents=True); (d / "blobs" / (sha + ".jsonl")).write_bytes(GOOD)
inv = {"transcripts": [{"agent": "a", "sha256": sha, "experiment": "E"}]}
rec = {"records": [{"agent": "a", "status": "VERIFIED", "inventory_sha256": sha, "experiment": "E"}]}
_, rep = extract_from_quarantine(d, rec, inv)
expect("extraction has report_id + CLEAN", rep["set_status"] == "CLEAN" and rep["report_id"].startswith("erpt:"))
expect("report_id recomputes", recompute_report_id(rep) == rep["report_id"])

# ============================ governance path ============================ #
TCLO = "clo:extract:testcorpus"
AUTH = {"completeness": ["AUTH_C"], "publication": ["AUTH_P"], "mapping": ["AUTH_M"]}


def evrec(kind, eid, vs, ve, val):
    return {"kind": kind, "event_id": eid, "value_start": vs, "value_end": ve,
            "observed_value_digest": ids._h(b"value", val)}


def mk(lr, root, ver, run="run", exp="EXP-RVB-1c", status="EXACT", comp="COMPLETE",
       pub="CLEARED_FOR_PUBLICATION", cauth="AUTH_C", pauth="AUTH_P", mauth="AUTH_M",
       with_ev=True, adj=True, commit=None, root_id_none=False):
    b = "blob:" + lr
    parts = [("experiment_id", exp.encode()), ("root_digest", root.encode()),
             ("verifier_identity", ver.encode()), ("agent_run_occurrence", run.encode())]
    body = b"|".join(v for _, v in parts)
    eid = ids.event_id(TCLO, b, 0, len(body), ids.line_digest(body))
    ev, digs, off = [], [], 0
    for kind, val in parts:
        # experiment_id is not an evidence-gated component (narrowed 2026-09-02): assert, don't evidence.
        if with_ev and kind != "experiment_id":
            it = evrec(kind, eid, off, off + len(val), val)
            ev.append(it); digs.append(ids.json_digest({k: it[k] for k in
                      ("kind", "event_id", "value_start", "value_end", "observed_value_digest")}))
        off += len(val) + 1
    adjud = ({"adjudicator_identity": "r", "authority": mauth, "decision": "EXACT",
              "evidence_commitments": commit if commit is not None else digs} if adj else None)
    cand = {"local_ref": lr, "blob_id": b,
            "event_occurrences": [{"event_id": eid, "byte_start": 0, "byte_end": len(body)}],
            "experiment_id": exp, "root_digest": ids.raw_sha256(root.encode()),
            "verifier_identity": ver, "agent_run_occurrence": run, "mapping_status": status,
            "mapping_evidence": ev, "adjudication": adjud,
            "root_id": None if root_id_none else "root:" + root,
            "verifier_declared_identity": ver, "verifier_observed_identity": ver,
            "prompt_digest": "UNKNOWN", "response_digest": "UNKNOWN", "offspring_before_dedup": "UNKNOWN",
            "dedup_removal_decisions": "UNKNOWN", "selected_child_refs": [], "sampling": {},
            "completeness_decision": {"adjudicator_identity": "r", "authority": cauth, "decision": comp},
            "publication_decision": {"adjudicator_identity": "r", "authority": pauth, "decision": pub},
            "parent_local_ref": None}
    return cand, (b, body)


def corpus(pairs, drop=False):
    private, man = {}, []
    for i, (b, body) in enumerate(pairs):
        ld = ids.line_digest(body); eid = ids.event_id(TCLO, b, 0, len(body), ld)
        ev = {"event_index": 0, "blob_id": b, "byte_start": 0, "byte_end": len(body),
              "line_digest": ld, "event_type": "user", "unknown_event_type": False,
              "event_id": eid, "extraction_closure": TCLO, "raw_b64": base64.b64encode(body).decode()}
        private[f"a{i}"] = {"blob_id": b, "events": [ev]}
        man.append({"blob_id": b, "event_index": 0, "event_id": eid, "body_digest": ld})
    man.sort(key=lambda x: (x["blob_id"], x["event_index"]))
    commit = ids.json_digest({"closure": TCLO, "inventory": [], "events": man})
    invc = ids.json_digest([])
    report = {"set_status": "CLEAN", "set_faults": [], "extraction_closure": TCLO,
              "corpus_commitment": commit, "event_manifest": (man[:-1] if drop else man),
              "inventory_commitment": invc}
    report["report_id"] = recompute_report_id(report)
    report["_priv"] = private          # test-only; invisible to report_id (canonical keys only)
    return private, report


ROOTS, VERIF = ["0030", "0025", "FLOW15", "FLOW17"], ["Fable", "Sonnet"]
C2_MAN = {"claim": "C2", "paper_pin": "paper@x", "experiment_ids": ["EXP-RVB-1c"],
          "unit_key": ["root_digest", "verifier_identity"],
          "required_units": [[ids.raw_sha256(r.encode()), v] for r in ROOTS for v in VERIF],
          "allowed_exclusions": []}


from corpus_map import (decision_record_id, _content_subject, _mapping_subject,  # noqa: E402
                        mapper_closure_id, record_publishable as _publishable_body)
from corpus_l4 import validate_l3_bundle, l4_evaluate  # noqa: E402


def trust(report, admit=True, pin=True, register=None, mapper=None):
    prov = {"report_id": report["report_id"], "corpus_commitment": report["corpus_commitment"],
            "extraction_closure": report["extraction_closure"], "l2_bundle_id": "x",
            "authorities": {"completeness": [], "publication": [], "mapping": []},
            "pinned_manifests": {}, "decision_register": []}
    fid = mint_l2_bundle(report["_priv"], report, prov)["bundle_id"]     # pin the canonical full bundle
    tr = {"report_id": report["report_id"], "corpus_commitment": report["corpus_commitment"],
          "extraction_closure": report["extraction_closure"], "l2_bundle_id": fid,
          "authorities": AUTH if admit else {"completeness": [], "publication": [], "mapping": []},
          "pinned_manifests": {"C2": manifest_id(C2_MAN)} if pin else {},
          "decision_register": register or []}
    tr["mapper_closure"] = mapper if mapper is not None else mapper_closure_id()
    return tr


def full(**kw):
    table, pairs = [], []
    for r in ROOTS:
        for v in VERIF:
            c, pb = mk(f"{r}-{v}", r, v, run=f"run-{r}-{v}", **kw)   # distinct run per unit
            table.append(c); pairs.append(pb)
    priv, report = corpus(pairs)
    return table, priv, report


def pin_all_decisions(table, tr, bundle):
    """Simulate the governance act: pin the exact decision-record ids (kind-specific subjects
    over the FINAL record bodies) for every act."""
    reg = []
    for rec in build_l3(bundle, table, {"C2": C2_MAN}, tr)["private_l3"]["records"]:
        b = rec["body"]; cs = _content_subject(b); ms = _mapping_subject(b)
        reg += [decision_record_id("completeness", cs, b["completeness_decision"]),
                decision_record_id("publication", cs, b["publication_decision"]),
                decision_record_id("mapping", ms, b["mapping"]["adjudication"])]
    return reg


# valid EXACT rows, admitted authorities, pinned manifest — but EMPTY register -> REFUSED
tbl, priv, report = full()
tr0 = trust(report)
bundle = mint_l2_bundle(priv, report, tr0)
expect("real bundle CLEAN", bundle["status"] == "CLEAN")
import copy  # noqa: E402
out0 = build_l3(bundle, tbl, {"C2": C2_MAN}, tr0)
expect("admitted authority + empty register -> C2 REFUSED (no credit)",
       out0["metadata_report"]["views"]["C2"]["status"] == "REFUSED"
       and all(not _publishable_body(r["body"], tr0) for r in out0["private_l3"]["records"]))

# governance act: pin every decision-record id -> COMPLETE
reg_all = pin_all_decisions(tbl, tr0, bundle)
tr_gov = trust(report, register=reg_all)
out = build_l3(bundle, tbl, {"C2": C2_MAN}, tr_gov)
expect("fully governed (register pinned) -> C2 COMPLETE", out["metadata_report"]["views"]["C2"]["status"] == "COMPLETE")
expect("COMPLETE emits evaluation_id", "evaluation_id" in out["metadata_report"]["views"]["C2"])

# ---- L4: serialized-L3-only replay reproduces the exact vector ----
ok, reason, _ = validate_l3_bundle(out["private_l3"])
expect("L3 bundle validates", ok)
l4 = l4_evaluate(out["private_l3"], {"C2": C2_MAN}, tr_gov)   # NO candidate table
expect("L4 serialized-only reproduces COMPLETE", l4["views"]["C2"]["status"] == "COMPLETE"
       and l4["views"]["C2"].get("evaluation_id") == out["metadata_report"]["views"]["C2"]["evaluation_id"])
rm = copy.deepcopy(out["private_l3"]); rm["records"] = rm["records"][:-1]
expect("L3 record removal -> L3_BUNDLE_MISMATCH", validate_l3_bundle(rm)[1] == "L3_BUNDLE_MISMATCH")
tp = copy.deepcopy(out["private_l3"]); tp["records"][0]["body"]["root_id"] = "TAMPERED"
expect("L3 body tamper -> RECORD_ID_MISMATCH", validate_l3_bundle(tp)[1] == "RECORD_ID_MISMATCH")

# === the three mandatory activation regressions (Codex governance review) ===
# R1: remove mapping decisions from the root used by L4 -> typed refusal, zero credit
map_ids = {decision_record_id("mapping", _mapping_subject(r["body"]), r["body"]["mapping"]["adjudication"])
           for r in out["private_l3"]["records"]}
tr_nomap = trust(report, register=[d for d in reg_all if d not in map_ids])
expect("R1: L4 with mapping decisions removed -> REFUSED (not COMPLETE)",
       l4_evaluate(out["private_l3"], {"C2": C2_MAN}, tr_nomap)["views"]["C2"]["status"] == "REFUSED")
expect("R1: build_l3 also REFUSES", build_l3(bundle, tbl, {"C2": C2_MAN}, tr_nomap)["metadata_report"]["views"]["C2"]["status"] == "REFUSED")
# R2: mutate a decision-relevant record field -> old decisions no longer grant credit
tblF = copy.deepcopy(tbl); tblF[0]["response_digest"] = "sha256:" + "f" * 64
expect("R2: forged response_digest under old register -> REFUSED",
       build_l3(bundle, tblF, {"C2": C2_MAN}, tr_gov)["metadata_report"]["views"]["C2"]["status"] == "REFUSED")
# R3: mutating evidence commitments rotates the mapping decision id
b0 = out["private_l3"]["records"][0]["body"]
adj_a = b0["mapping"]["adjudication"]; adj_b = {**adj_a, "evidence_commitments": ["OTHER"]}
expect("R3: evidence-commitment change rotates mapping decision id",
       decision_record_id("mapping", _mapping_subject(b0), adj_a)
       != decision_record_id("mapping", _mapping_subject(b0), adj_b))
# P1: mapper-closure mutation -> not publishable (fork cannot return COMPLETE)
expect("mapper-closure mutation -> C2 REFUSED",
       build_l3(bundle, tbl, {"C2": C2_MAN}, trust(report, register=reg_all, mapper="clo:map:FORK")
                )["metadata_report"]["views"]["C2"]["status"] == "REFUSED")


def _reseal(pl3):
    pl3["local_ref_index"] = {r["body"]["local_ref"]: r["record_id"] for r in pl3["records"]}
    pl3["l3_bundle_id"] = "l3:" + ids.json_digest({"mapper_closure": pl3["mapper_closure"],
        "l2_bundle_id": pl3["l2_bundle_id"], "local_ref_index": pl3["local_ref_index"],
        "records": sorted(r["record_id"] for r in pl3["records"])})
    return pl3


# P0-4: swap mapping.act_id/status, coherently re-seal -> old decision no longer applies
f4 = copy.deepcopy(out["private_l3"]); b4 = f4["records"][0]["body"]
b4["mapping"]["act_id"] = "act:FORGED"; b4["mapping"]["status"] = "DERIVED"
f4["records"][0]["record_id"] = "rec:" + ids.json_digest(b4)
expect("P0-4: forged mapping.act_id/status -> L4 not COMPLETE",
       l4_evaluate(_reseal(f4), {"C2": C2_MAN}, tr_gov)["views"]["C2"]["status"] != "COMPLETE")
# P0-5: coherent re-forge of top-level mapper_closure / l2_bundle_id -> REFUSED
fm = _reseal({**copy.deepcopy(out["private_l3"]), "mapper_closure": "clo:map:FORGED"})
expect("P0-5: forged mapper_closure -> L4 REFUSED",
       l4_evaluate(fm, {"C2": C2_MAN}, tr_gov)["views"]["C2"]["status"] == "REFUSED")
fl = _reseal({**copy.deepcopy(out["private_l3"]), "l2_bundle_id": "bnd:FORGED"})
expect("P0-5: forged l2_bundle_id -> L4 REFUSED",
       l4_evaluate(fl, {"C2": C2_MAN}, tr_gov)["views"]["C2"]["status"] == "REFUSED")

# L4 without pinned decisions reproduces REFUSED (same vector as build_l3)
l4r = l4_evaluate(build_l3(bundle, tbl, {"C2": C2_MAN}, tr0)["private_l3"], {"C2": C2_MAN}, tr0)
expect("L4 reproduces REFUSED vector", l4r["views"]["C2"]["status"] == "REFUSED")
# duplicate run across units -> REFUSED (credit stays 0). Because agent_run_occurrence is
# evidenced, changing it also breaks EVIDENCE_VALUE_MISMATCH first; the view-level
# run-uniqueness check is the defense-in-depth for un-evidenced runs.
tdup = copy.deepcopy(tbl); tdup[1]["agent_run_occurrence"] = tdup[0]["agent_run_occurrence"]
odup = build_l3(bundle, tdup, {"C2": C2_MAN}, trust(report, register=pin_all_decisions(tdup, tr0, bundle)))["metadata_report"]
expect("duplicate run across units -> REFUSED, credit 0",
       odup["views"]["C2"]["status"] == "REFUSED"
       and sum(a["status"] == "EXACT" for a in odup["acts"]) < 8)

tr = tr_gov          # alias for the downstream mutation tests (valid pinned trust)

# self-issued authority -> AUTHORITY_NOT_ADMITTED (empty authorities)
tr_noauth = trust(report, admit=False)
out2 = build_l3(mint_l2_bundle(priv, report, tr_noauth), tbl, {"C2": C2_MAN}, tr_noauth)
expect("no admitted authority -> REFUSED", out2["metadata_report"]["views"]["C2"]["status"] == "REFUSED")
expect("self-issued authority faulted", any("AUTHORITY_NOT_ADMITTED" in a["faults"]
       for a in out2["metadata_report"]["acts"]))

# unpinned / replacement manifest -> MANIFEST_NOT_PINNED
tr_nopin = trust(report, pin=False)
expect("unpinned manifest -> MANIFEST_NOT_PINNED",
       build_l3(mint_l2_bundle(priv, report, tr_nopin), tbl, {"C2": C2_MAN}, tr_nopin
                )["metadata_report"]["views"]["C2"]["reason"] == "MANIFEST_NOT_PINNED")
one_man = {**C2_MAN, "required_units": [[ids.raw_sha256(b"0030"), "Fable"]]}
expect("one-unit replacement manifest -> MANIFEST_NOT_PINNED",
       build_l3(bundle, tbl, {"C2": one_man}, tr)["metadata_report"]["views"]["C2"]["reason"] == "MANIFEST_NOT_PINNED")

# coherent invented report + same trust root -> REPORT_NOT_PINNED
c0, pb0 = mk("x", "0030", "Fable")
priv_inv, rep_inv = corpus([pb0])
expect("invented report + pinned trust -> REPORT_NOT_PINNED",
       mint_l2_bundle(priv_inv, rep_inv, tr)["status"] == "REPORT_NOT_PINNED")

# set_status=FAIL -> REPORT_NOT_CLEAN
rep_fail = dict(report); rep_fail["set_status"] = "FAIL"; rep_fail["report_id"] = recompute_report_id(rep_fail)
tr_fail = trust(rep_fail)
expect("FAIL report -> REPORT_NOT_CLEAN", mint_l2_bundle(priv, rep_fail, tr_fail)["status"] == "REPORT_NOT_CLEAN")

# implicit subset -> SET_MISMATCH
priv_sub, rep_sub = corpus([pb0, mk("y", "0025", "Sonnet")[1]], drop=True)  # manifest missing 1
tr_sub = trust(rep_sub)
expect("subset of committed manifest -> SET_MISMATCH (or UNKNOWN_SOURCE)",
       mint_l2_bundle(priv_sub, rep_sub, tr_sub)["status"] != "CLEAN")

# bundle mutations
bmut = {**bundle, "body": {**bundle["body"], "status": "CLEAN",
        "events": [{**bundle["body"]["events"][0], "byte_start": 99}] + bundle["body"]["events"][1:]}}
expect("index-address mutation -> BUNDLE_ID_MISMATCH", verify_bundle(bmut, tr)[1] == "BUNDLE_ID_MISMATCH")
# L2_REFUSED -> CLEAN flip on a genuinely-refused bundle (bundle_id was over L2_REFUSED)
refused = mint_l2_bundle(priv_sub, rep_sub, tr_sub)   # status L2_REFUSED, id over that body
flipped = {**refused, "body": {**refused["body"], "status": "CLEAN"}}
expect("status flip -> BUNDLE_ID_MISMATCH", verify_bundle(flipped, tr_sub)[1] == "BUNDLE_ID_MISMATCH")
# index body tamper
btam = {**bundle, "raw_bodies": {k: v + b"X" for k, v in bundle["raw_bodies"].items()}}
expect("index body tamper -> INDEX_TAMPER", verify_bundle(btam, tr)[1] == "INDEX_TAMPER")

# coherent subset bundle under the real report -> BUNDLE_NOT_PINNED
sub_body = {**bundle["body"], "events": bundle["body"]["events"][:1]}
sub_bundle = {"bundle_id": "bnd:" + ids.json_digest(sub_body), "body": sub_body, "raw_bodies": bundle["raw_bodies"]}
expect("coherent subset bundle -> BUNDLE_NOT_PINNED", verify_bundle(sub_bundle, tr)[1] == "BUNDLE_NOT_PINNED")
# forged expected_closure -> BUNDLE_NOT_PINNED
fc_body = {**bundle["body"], "expected_closure": "clo:extract:FORGED"}
fc_bundle = {"bundle_id": "bnd:" + ids.json_digest(fc_body), "body": fc_body, "raw_bodies": bundle["raw_bodies"]}
expect("forged closure bundle -> BUNDLE_NOT_PINNED", verify_bundle(fc_bundle, tr)[1] == "BUNDLE_NOT_PINNED")
# malformed trust root -> TRUST_ROOT_INVALID
expect("malformed trust root -> TRUST_ROOT_INVALID", verify_bundle(bundle, {"bad": 1})[1] == "TRUST_ROOT_INVALID")
# permuted event_index inside a real multi-event blob -> EVENT_MANIFEST_MISMATCH
mb = "blob:multi"; b1, b2 = b"E0", b"E1"
ld1, ld2 = ids.line_digest(b1), ids.line_digest(b2)
e1 = ids.event_id(TCLO, mb, 0, len(b1), ld1); e2 = ids.event_id(TCLO, mb, len(b1), len(b1) + len(b2), ld2)
man = [{"blob_id": mb, "event_index": 0, "event_id": e1, "body_digest": ld1},
       {"blob_id": mb, "event_index": 1, "event_id": e2, "body_digest": ld2}]
def _ev(idx, s, e, eid, ld, raw):
    return {"event_index": idx, "blob_id": mb, "byte_start": s, "byte_end": e, "line_digest": ld,
            "event_type": "user", "unknown_event_type": False, "event_id": eid,
            "extraction_closure": TCLO, "raw_b64": base64.b64encode(raw).decode()}
priv_perm = {"a": {"blob_id": mb, "events": [_ev(1, 0, len(b1), e1, ld1, b1),         # index swapped
                                             _ev(0, len(b1), len(b1) + len(b2), e2, ld2, b2)]}}
commit = ids.json_digest({"closure": TCLO, "inventory": [], "events": sorted(man, key=lambda x: (x["blob_id"], x["event_index"]))})
rep_perm = {"set_status": "CLEAN", "set_faults": [], "extraction_closure": TCLO,
            "corpus_commitment": commit, "event_manifest": man, "inventory_commitment": ids.json_digest([])}
rep_perm["report_id"] = recompute_report_id(rep_perm); rep_perm["_priv"] = priv_perm
bperm = mint_l2_bundle(priv_perm, rep_perm, trust(rep_perm))
expect("permuted event_index -> EVENT_MANIFEST_MISMATCH", any(f["code"] == "EVENT_MANIFEST_MISMATCH" for f in bperm["faults"]))

# DERIVED never credits
tblD, privD, repD = full(status="DERIVED")
expect("all DERIVED -> C2 REFUSED",
       build_l3(mint_l2_bundle(privD, repD, trust(repD)), tblD, {"C2": C2_MAN}, trust(repD)
                )["metadata_report"]["views"]["C2"]["status"] == "REFUSED")

# null field -> SCHEMA_INVALID -> not EXACT
cn, pbn = mk("n", "0030", "Fable", root_id_none=True)
pn, rn = corpus([pbn])
expect("null field -> SCHEMA_INVALID",
       "SCHEMA_INVALID" in build_l3(mint_l2_bundle(pn, rn, trust(rn)), [cn], {}, trust(rn)
                                    )["metadata_report"]["acts"][0]["faults"])

# wrong adjudication commitment -> AMBIGUOUS
ca, pba = mk("a", "0030", "Fable", commit=["stale"])
pa, ra = corpus([pba])
expect("wrong adjudication -> AMBIGUOUS",
       build_l3(mint_l2_bundle(pa, ra, trust(ra)), [ca], {}, trust(ra)
                )["metadata_report"]["acts"][0]["status"] == "AMBIGUOUS")

# EXACT -> CONFLICTED: final record_id binds final status
cr1, p1 = mk("0030-Fable", "0030", "Fable", run="r1", status="DERIVED", with_ev=False, adj=False)
cr2, p2 = mk("0030-Fable-b", "0030", "Fable", run="r2", status="DERIVED", with_ev=False, adj=False)
pr, rr = corpus([p1, p2])
outr = build_l3(mint_l2_bundle(pr, rr, trust(rr)), [cr1, cr2], {}, trust(rr))
conf = [a for a in outr["metadata_report"]["acts"] if a["status"] == "CONFLICTED"]
expect("repeated run -> CONFLICTED", len(conf) == 2)
recbody = [r for r in outr["private_l3"]["records"] if r["record_id"] == conf[0]["record_id"]][0]["body"]
expect("record body binds final CONFLICTED status", recbody["final_status"] == "CONFLICTED")

# private L3 bundle is self-contained (L4 can replay)
recs = out["private_l3"]["records"]
expect("private L3 has full record bodies",
       out["private_l3"]["l3_bundle_id"].startswith("l3:") and recs
       and all(k in recs[0]["body"] for k in ("source", "completeness_decision", "mapping", "mapper_closure")))

# evaluation identity binds the mapper closure
ev_real = out["metadata_report"]["views"]["C2"]["evaluation_id"]
ev_fake = "eval:" + ids.json_digest({"mapper_closure": "clo:map:OTHER",
          "manifest_id": manifest_id(C2_MAN), "l2_bundle_id": bundle["bundle_id"],
          "corpus_commitment": tr["corpus_commitment"],
          "record_ids": sorted(r["record_id"] for r in recs)})
expect("evaluation_id binds mapper closure", ev_real != ev_fake)

# F8 + malformed table
expect("F8 reused id", make_public_projection("act:1", "p", b"B", {"l": 1}, proposed_id="act:1")["status"] == "FAIL")
try:
    r = build_l3(bundle, ["not a dict"], {}, tr)
    expect("malformed table typed no crash", r["metadata_report"]["fault_count"] >= 1)
except Exception as ex:  # noqa
    expect(f"malformed crashed: {ex!r}", False)

# ===================== production-operand gate (P0-2) ===================== #
# The committed 0.2 operand + its activation proposal are bound to an executable check, so
# deleting or one-byte-mutating either file fails CI (closes the stale-green hole). Structural
# only (no quarantine); raw-span revalidation stays machine-local.
import hashlib  # noqa: E402
PAPER = Path(__file__).resolve().parents[1] / "every-check-spawns-more"
try:
    opf = PAPER / "CORPUS-C2-MAPPING-0.2.json"
    prf = PAPER / "CORPUS-C2-MAP-ACTIVATION-0.1.json"
    op = json.loads(opf.read_text()); pr = json.loads(prf.read_text())
    rows_ = op["rows"]
    expect("prod operand has 8 rows", len(rows_) == 8)
    expect("prod operand: 24 evidence records (3/row)",
           sum(len(r["mapping_evidence"]) for r in rows_) == 24
           and all(len(r["mapping_evidence"]) == 3 for r in rows_))
    expect("prod operand: all rows DERIVED", all(r["mapping_status"] == "DERIVED" for r in rows_))
    expect("prod operand: exact 4x2 observed-model bijection",
           len({(r["root_digest"], r["verifier_identity"]) for r in rows_}) == 8
           and len({r["root_digest"] for r in rows_}) == 4
           and {r["verifier_identity"] for r in rows_} == {"claude-opus-5", "claude-sonnet-5"})
    expect("prod operand: evidence kinds are the 3 narrowed components",
           all({e["kind"] for e in r["mapping_evidence"]}
               == {"root_digest", "verifier_identity", "agent_run_occurrence"} for r in rows_))
    expect("activation proposal binds the exact operand digest",
           pr["operand_digest"] == "sha256:" + hashlib.sha256(opf.read_bytes()).hexdigest())
    from corpus_map import proposal_identity  # noqa: E402
    expect("activation proposal_id recomputes (CLOSED body: schema+for included, P1-6)",
           pr["proposal_id"] == proposal_identity(pr))
    expect("proposal_id rotates on a schema/for mutation (P1-6)",
           proposal_identity({**pr, "for": "C2-MEAS"}) != pr["proposal_id"]
           and proposal_identity({**pr, "schema": "x"}) != pr["proposal_id"])
    expect("proposal overlay is 8 EXACT rows over the same units",
           len(pr["overlay_rows"]) == 8
           and all(o["mapping_status"] == "EXACT" for o in pr["overlay_rows"])
           and {(o["root_digest"], o["verifier_identity"]) for o in pr["overlay_rows"]}
               == {(r["root_digest"], r["verifier_identity"]) for r in rows_})
    expect("proposal is for C2-MAP only (C2-MEAS not claimed)",
           pr["for"] == "C2-MAP" and pr["manifest"]["claim"] == "C2-MAP")
    # the machine-local ACTIVATION-REPORT (structural bind; span revalidation is machine-local)
    ar = json.loads((PAPER / "CORPUS-C2-MAP-ACTIVATION-REPORT-0.1.json").read_text())
    expect("activation report_id recomputes",
           ar["report_id"] == "arpt:" + ids.json_digest({k: v for k, v in ar.items() if k != "report_id"}))
    expect("activation report: all assertions true", all(ar["assertions"].values()) and ar["metadata_only"])
    expect("activation report binds the operand + proposal",
           ar["operand"]["digest"] == "sha256:" + hashlib.sha256(opf.read_bytes()).hexdigest()
           and ar["proposal"]["proposal_id"] == pr["proposal_id"])
    expect("activation report: C2-MEAS stays REFUSED (no laundering)",
           ar["result_vector"]["C2-MEAS"]["status"] == "REFUSED"
           and ar["result_vector"]["applied"]["C2-MAP"] == "COMPLETE"
           and ar["result_vector"]["baseline"]["C2-MAP"] == "REFUSED")
    expect("activation report: trust root still unchanged (empty)",
           ar["assertions"]["trust_root_unchanged"] and json.loads((PAPER / "CORPUS-TRUST-ROOT.json").read_text())["decision_register"] == [])
    # P0-1: the engine's ACTUAL reason is preserved, NOT overwritten by the authored projection
    meas = ar["result_vector"]["C2-MEAS"]
    expect("activation report: C2-MEAS keeps the engine reason (P0-1)",
           meas["engine_reason"] == "REQUIRED_UNITS_UNSPECIFIED"
           and meas["engine_reason"] != "MEASUREMENT_NOT_REPLAYED"
           and meas["policy_projection"] == "MEASUREMENT_NOT_REPLAYED")
    # P1-5: the applied vector discloses the exact L3 + 8 record ids
    app = ar["result_vector"]["applied"]
    expect("activation report: applied vector discloses l3 + 8 record ids (P1-5)",
           app["l3_bundle_id"].startswith("l3:") and len(app["record_ids"]) == 8
           and len(set(app["record_ids"])) == 8)

    # ============ P0-2: INDEPENDENT report verification + coherent-forge regression ============
    from corpus_activation_report import verify_activation_report  # noqa: E402
    vok, vf = verify_activation_report(PAPER)
    expect("independent verify_activation_report PASSES on the committed report", vok)
    if not vok:
        print("   faults:", vf)
    # a COHERENT single-file re-forge (forged l2 + emptied registers, only report_id recomputed)
    # must FAIL the independent verifier even though its own booleans stay green.
    import tempfile, shutil  # noqa: E402
    forged_dir = Path(tempfile.mkdtemp()) / "every-check-spawns-more"
    shutil.copytree(PAPER, forged_dir)
    fdoc = json.loads((forged_dir / "CORPUS-C2-MAP-ACTIVATION-REPORT-0.1.json").read_text())
    fdoc["provenance"]["l2_bundle_id"] = "bnd:FORGED"
    fdoc["activation"]["decision_register"] = []
    fdoc["activation"]["trust_root_diff"]["decision_register"] = []
    fbody = {k: v for k, v in fdoc.items() if k != "report_id"}
    fdoc["report_id"] = "arpt:" + ids.json_digest(fbody)      # re-forge ONLY the self-hash
    (forged_dir / "CORPUS-C2-MAP-ACTIVATION-REPORT-0.1.json").write_text(json.dumps(fdoc, indent=1))
    fok, ff = verify_activation_report(forged_dir)
    expect("coherent-forged report (self-hash recomputed) FAILS independent verify (P0-2)", not fok)
    expect("forge is caught by cross-checking l2 pin + register vs proposal",
           any(c in ff for c in ("L2_NOT_PINNED_TO_TRUST_ROOT", "REGISTER_MISMATCH", "REGISTER_NOT_24")))
    shutil.rmtree(forged_dir.parent)

    # ============ P0-3: C2-MAP / C2-MEAS as canonical deposit claims ============
    import importlib  # noqa: E402
    dc = importlib.import_module("deposit_check") if "deposit_check" in sys.modules else None
    if dc is None:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        import deposit_check as dc  # noqa: E402
    rep = dc.evaluate(PAPER / "claim-manifest.json")
    expect("deposit engine binds candidate + closed ledger incl. C2-MAP/C2-MEAS", rep["engine"] == "OK")
    byid = {c["id"]: c for c in rep["claims"]}
    expect("C2-MAP + C2-MEAS are registered canonical claims",
           "C2-MAP" in byid and "C2-MEAS" in byid)
    # before activation (trust root empty): C2-MAP is refused ACTIVATION_NOT_APPLIED
    expect("C2-MAP REFUSED: ACTIVATION_NOT_APPLIED (trust root still empty)",
           byid["C2-MAP"]["status"] == "REFUSED" and byid["C2-MAP"]["reason"] == "ACTIVATION_NOT_APPLIED")
    expect("C2-MEAS REFUSED: MEASUREMENT_NOT_REPLAYED (permanent, separate claim)",
           byid["C2-MEAS"]["status"] == "REFUSED" and byid["C2-MEAS"]["reason"] == "MEASUREMENT_NOT_REPLAYED")
    # positive path: SIMULATE the operator applying the diff into a temp corpus -> CHECKED,
    # while C2-MEAS stays refused (no laundering). The committed root is untouched.
    from corpus_operator_readback import applied_trust_root  # noqa: E402
    sim_dir = Path(tempfile.mkdtemp()) / "every-check-spawns-more"
    shutil.copytree(PAPER, sim_dir)
    base_tr = json.loads((sim_dir / "CORPUS-TRUST-ROOT.json").read_text())
    prop_s = json.loads((sim_dir / "CORPUS-C2-MAP-ACTIVATION-0.1.json").read_text())
    (sim_dir / "CORPUS-TRUST-ROOT.json").write_text(
        json.dumps(applied_trust_root(base_tr, prop_s["trust_root_diff"]), indent=1))
    repo_root = Path(__file__).resolve().parents[2]
    st, rs, _ = dc.strat_corpus_activation(repo_root, {"corpus_dir": str(sim_dir)})  # abs path -> temp
    expect("SIMULATED activation -> C2-MAP CHECKED (live-activated root + verified report)",
           st == "CHECKED")
    if st != "CHECKED":
        print("   got:", st, rs)
    # C2-MEAS must STILL be refused under the same activated root (composition-laundering guard)
    st2, rs2, _ = dc.strat_refused(sim_dir, {"reason": "MEASUREMENT_NOT_REPLAYED"})
    expect("under activation, C2-MEAS STILL REFUSED (no composition laundering)",
           st2 == "REFUSED" and rs2 == "MEASUREMENT_NOT_REPLAYED")
    shutil.rmtree(sim_dir.parent)
except FileNotFoundError as e:
    expect(f"production operand/proposal/report present: {e}", False)

print()
if fails:
    print(f"RED: {len(fails)} corpus failure(s): {fails}")
    sys.exit(1)
print("GREEN: extraction is mechanical; L2 is trust-bound; credit needs admitted authority.")
