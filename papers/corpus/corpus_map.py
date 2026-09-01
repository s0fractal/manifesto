#!/usr/bin/env python3
"""
corpus_map.py — L2 -> L3. EXPLICIT, REVIEWABLE MAPPING (a separate pass).

Extraction (corpus_extract.py) is mechanical and makes no root/verifier/experiment
claim. This pass turns L2 events into an L3 act graph ONLY through an explicit
mapping table with exact evidence spans — never by guessing from content, and never
from counts/verdicts.

Rules enforced (see CORPUS-SCHEMA-0.1.md / CORPUS-NEGATIVE-FIXTURES.md):
- an act cites the exact L2 events composing it; a referenced event absent from L2
  breaks the mapping (DANGLING_EVIDENCE / DANGLING_REF);
- mapping_status EXACT is allowed ONLY when all four components
  (experiment_id, root_digest, verifier_identity, agent_run_occurrence) each have a
  mapping_evidence span present in L2; an EXACT claim without them becomes AMBIGUOUS;
- counts/verdicts are forbidden as disambiguation evidence;
- the auto-proposer may assign DERIVED, never EXACT;
- two EXACT/DERIVED acts sharing (experiment, root, verifier) with different runs are
  CONFLICTED (repeated-run threat);
- duplicate act_id -> DUPLICATE_ID; dangling parent/child -> DANGLING_REF (fail-closed);
- a PARTIAL act stays PARTIAL; a claim view is COMPLETE only if every required unit is
  present, COMPLETE, and CLEARED_FOR_PUBLICATION;
- C2 requires a PROVEN unique bijection over the four crossed roots x two verifiers;
  any ambiguity leaves C2 REFUSED.
"""
from corpus_ids import act_id as mk_act_id, public_id as mk_public_id, _h

REQUIRED_COMPONENTS = ("experiment_id", "root_digest", "verifier_identity", "agent_run_occurrence")
FORBIDDEN_EVIDENCE = {"count", "verdict"}
VALID_STATUS = {"EXACT", "DERIVED", "AMBIGUOUS", "CONFLICTED"}


def _canonical_body(event_ids):
    return _h(b"act-body", *sorted(event_ids))


def _resolve_status(entry, l2_event_ids):
    """Downgrade an over-claimed status to what the evidence actually supports."""
    faults = []
    ev = entry.get("mapping_evidence", [])
    if any(e.get("kind") in FORBIDDEN_EVIDENCE for e in ev):
        faults.append("FORBIDDEN_EVIDENCE")
        return "AMBIGUOUS", faults
    have = {e["kind"] for e in ev
            if e.get("event_id") in l2_event_ids and e.get("kind") in REQUIRED_COMPONENTS}
    dangling = [e["event_id"] for e in ev if e.get("event_id") not in l2_event_ids]
    if dangling:
        faults.append("DANGLING_EVIDENCE")
    complete_evidence = all(c in have for c in REQUIRED_COMPONENTS)
    claimed = entry.get("mapping_status", "DERIVED")
    if claimed not in VALID_STATUS:
        faults.append("BAD_STATUS")
        claimed = "AMBIGUOUS"
    if claimed == "EXACT" and not complete_evidence:
        faults.append("EXACT_WITHOUT_EVIDENCE")
        return "AMBIGUOUS", faults
    if dangling:
        return "AMBIGUOUS", faults
    return claimed, faults


def build_l3(l2_event_ids, table, extractor_id):
    """
    l2_event_ids: set of event_ids present in the private L2.
    table: list of explicit mapping entries.
    Returns a metadata report (no content): acts, faults, per-claim views.
    """
    l2_event_ids = set(l2_event_ids)
    acts, faults = [], []
    by_local = {}
    seen_act_ids = {}

    for entry in table:
        lr = entry.get("local_ref", "?")
        eids = entry.get("event_ids", [])
        f = []
        missing = [e for e in eids if e not in l2_event_ids]
        if not eids:
            f.append("NO_EVENTS")
        if missing:
            f.append("DANGLING_REF")             # act body references absent L2 events
        status, sf = _resolve_status(entry, l2_event_ids)
        f += sf
        # SILENT_DEFAULT: a concrete sampling value must be evidenced, else it must be UNKNOWN.
        ev = entry.get("mapping_evidence", [])
        for k, v in (entry.get("sampling") or {}).items():
            if v != "UNKNOWN" and not any(
                    e.get("kind") == f"sampling.{k}" and e.get("event_id") in l2_event_ids
                    for e in ev):
                f.append("SILENT_DEFAULT")
                break
        aid = mk_act_id(extractor_id, entry.get("blob_id", ""),
                        int(entry.get("byte_start", 0)), int(entry.get("byte_end", 0)),
                        _canonical_body(eids).encode())
        if aid in seen_act_ids:
            f.append("DUPLICATE_ID")
        seen_act_ids[aid] = lr
        act = {
            "local_ref": lr, "act_id": aid,
            "experiment_id": entry.get("experiment_id"),
            "root_digest": entry.get("root_digest"),
            "verifier_identity": entry.get("verifier_identity"),
            "agent_run_occurrence": entry.get("agent_run_occurrence"),
            "mapping_status": status,
            "completeness_status": entry.get("completeness_status", "UNKNOWN"),
            "publication_eligibility": entry.get("publication_eligibility", "UNREVIEWED"),
            "parent_local_ref": entry.get("parent_local_ref"),
            "selected_child_refs": entry.get("selected_child_refs", []),
            "faults": f,
        }
        acts.append(act)
        by_local[lr] = act
        if f:
            faults.append({"local_ref": lr, "faults": f})

    # structural resolution: parent/child must resolve (fail-closed)
    for a in acts:
        if a["parent_local_ref"] is not None and a["parent_local_ref"] not in by_local:
            a["faults"].append("DANGLING_PARENT")
            faults.append({"local_ref": a["local_ref"], "faults": ["DANGLING_PARENT"]})
        for c in a["selected_child_refs"]:
            if c not in by_local:
                a["faults"].append("DANGLING_CHILD")
                faults.append({"local_ref": a["local_ref"], "faults": ["DANGLING_CHILD"]})

    # repeated-run detection: same (experiment, root, verifier), different run -> CONFLICTED
    from collections import defaultdict
    groups = defaultdict(list)
    for a in acts:
        if a["mapping_status"] in ("EXACT", "DERIVED"):
            groups[(a["experiment_id"], a["root_digest"], a["verifier_identity"])].append(a)
    for key, g in groups.items():
        runs = {a["agent_run_occurrence"] for a in g}
        if len(runs) > 1:
            for a in g:
                a["mapping_status"] = "CONFLICTED"
                a["faults"].append("REPEATED_RUN")

    views = {c: _view(c, acts) for c in ("C1", "C3", "C2", "C4", "C7")}
    return {
        "schema": "manifesto.corpus.act-graph-report.v0",
        "layer": "L2->L3 (explicit mapping)",
        "extractor_id": extractor_id,
        "act_count": len(acts),
        "fault_count": len(faults),
        "faults": faults,
        "views": views,
        "acts": [{k: a[k] for k in ("local_ref", "act_id", "experiment_id",
                  "mapping_status", "completeness_status", "publication_eligibility",
                  "faults")} for a in acts],
        "note": "metadata only. A mapping table is REQUIRED; with no table every view is REFUSED.",
    }


def make_public_projection(source_act_id, redaction_profile_id, loss_report):
    """A redacted/public projection gets a NEW id + a loss report; the original id is
    never reused (F8). Returns a typed result."""
    if not loss_report:
        return {"status": "FAIL", "reason": "MISSING_LOSS_REPORT"}
    pid = mk_public_id(redaction_profile_id, source_act_id)
    if pid == source_act_id:                       # different domain prefix; belt-and-suspenders
        return {"status": "FAIL", "reason": "REDACTION_ID_REUSE"}
    return {"status": "OK", "public_id": pid, "derived_from": source_act_id,
            "loss_report": loss_report}


def _publishable_complete(a):
    return (not a["faults"] and a["completeness_status"] == "COMPLETE"
            and a["publication_eligibility"] == "CLEARED_FOR_PUBLICATION"
            and a["mapping_status"] in ("EXACT", "DERIVED"))


def _view(claim, acts):
    """Per-claim completeness. C2 additionally demands a proven unique bijection."""
    if claim == "C2":
        crossed = [a for a in acts if a["experiment_id"] == "EXP-RVB-1c"]
        if not crossed:
            return {"status": "REFUSED", "reason": "FROZEN_CORPUS_NOT_DEPOSITED",
                    "detail": "no crossed acts mapped"}
        bad = [a["local_ref"] for a in crossed
               if a["mapping_status"] in ("AMBIGUOUS", "CONFLICTED") or a["faults"]]
        if bad:
            return {"status": "REFUSED", "reason": "AMBIGUOUS_C2_MAPPING", "acts": bad}
        # proven unique bijection: 4 roots x 2 verifiers = 8 EXACT/DERIVED acts
        pairs = {(a["root_digest"], a["verifier_identity"]) for a in crossed}
        roots = {a["root_digest"] for a in crossed}
        verifiers = {a["verifier_identity"] for a in crossed}
        if not (len(roots) == 4 and len(verifiers) == 2 and len(pairs) == 8
                and len(crossed) == 8):
            return {"status": "REFUSED", "reason": "INCOMPLETE_C2_BIJECTION",
                    "have": {"roots": len(roots), "verifiers": len(verifiers),
                             "pairs": len(pairs), "acts": len(crossed)}}
        if not all(_publishable_complete(a) for a in crossed):
            return {"status": "REFUSED", "reason": "INCOMPLETE_TREE"}
        return {"status": "COMPLETE", "acts": 8}
    # C1/C3/C4/C7: present-and-complete over their experiments (required_units authored
    # in the mapping table's "required" section is a later refinement; here we refuse on
    # any fault / partial / uncleared).
    exp_for = {"C1": ("EXP-RVB-1", "EXP-RVB-1b"), "C3": ("EXP-RVB-1b",),
               "C4": ("EXP-RVB-1-NC", "EXP-RVB-NC2"), "C7": ("EXP-RVB-2",)}
    rel = [a for a in acts if a["experiment_id"] in exp_for[claim]]
    if not rel:
        return {"status": "REFUSED", "reason": "FROZEN_CORPUS_NOT_DEPOSITED"}
    if not all(_publishable_complete(a) for a in rel):
        return {"status": "REFUSED", "reason": "INCOMPLETE_TREE",
                "partial": [a["local_ref"] for a in rel if not _publishable_complete(a)]}
    return {"status": "COMPLETE", "acts": len(rel)}
