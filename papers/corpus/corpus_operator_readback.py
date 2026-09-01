#!/usr/bin/env python3
"""
corpus_operator_readback.py — the operator-act readback for the C2-MAP activation (P1-4).

The activation `trust_root_diff` carries no proposal_id / report id; that binding is supplied
by the OPERATOR COMMIT itself, which must be an addressable governance act. This tool computes,
from the committed artifacts, exactly what that commit records:

  - base trust-root content digest (the committed EMPTY root);
  - the proposal_id and the activation-report `arpt:` id;
  - the exact diff content digest;
  - the RESULTING trust-root content digest (base with the diff applied);
  - the authorized paths the commit is allowed to touch.

Read-only by default (prints the readback). With `--emit <path>` it writes the exact resulting
trust-root JSON the operator would commit — applying it is still the operator's separate act.
The two commit ids (parent + resulting) are filled in by the operator after committing.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus_ids as ids
from corpus_map import load_strict_json, validate_trust_root
from corpus_activation_report import verify_activation_report

PAPER = Path(__file__).resolve().parents[1] / "every-check-spawns-more"
AUTHORIZED_PATHS = ["papers/every-check-spawns-more/CORPUS-TRUST-ROOT.json",
                    "papers/every-check-spawns-more/CORPUS-OPERATOR-ACT.json"]


EMPTY_AUTH = {"completeness": [], "publication": [], "mapping": []}
OPERATOR_ACT_FIELDS = {"schema", "base_trust_root_digest", "proposal_id", "activation_report_id",
                       "diff_digest", "resulting_trust_root_digest", "operator_identity",
                       "authority", "act_status", "authorized_paths", "parent_commit"}
OPERATOR_ACT_SCHEMA = "manifesto.corpus.operator-act.v0.1"


def applied_trust_root(base, diff):
    """Base with ONLY the four credit-bearing governance fields replaced (path-limited)."""
    return {**base, "authorities": diff["authorities"],
            "pinned_manifests": diff["pinned_manifests"],
            "mapper_closure": diff["mapper_closure"],
            "decision_register": diff["decision_register"]}


def _reconstructed_base(live_root):
    """The pre-activation empty base implied by a resulting root: drop the mapper closure and
    reset the three credit collections. If the operator changed anything OTHER than the four
    credit fields, applied_trust_root(base, diff) will not re-equal the live root."""
    base = {k: v for k, v in live_root.items() if k != "mapper_closure"}
    base["authorities"] = dict(EMPTY_AUTH)
    base["pinned_manifests"] = {}
    base["decision_register"] = []
    return base


def build_operator_act(live_root, prop, ar, operator_identity, authority, parent_commit):
    base = _reconstructed_base(live_root)
    return {"schema": OPERATOR_ACT_SCHEMA,
            "base_trust_root_digest": "tr:" + ids.json_digest(base),
            "proposal_id": prop["proposal_id"], "activation_report_id": ar["report_id"],
            "diff_digest": "diff:" + ids.json_digest(prop["trust_root_diff"]),
            "resulting_trust_root_digest": "tr:" + ids.json_digest(live_root),
            "operator_identity": operator_identity, "authority": authority,
            "act_status": "ACTIVATED", "authorized_paths": AUTHORIZED_PATHS,
            "parent_commit": parent_commit}


def validate_operator_act(act, live_root, prop, ar):
    """The operator act is a REQUIRED credit operand (P0-3): a manual/unattributed root edit must be
    distinguishable from the promised governance act. Recomputes the live root digest and refuses
    when the act is absent, malformed, unpinned, or names another base/proposal/report/result."""
    F = []

    def need(c, code):
        if not c:
            F.append(code)
        return c
    if not (isinstance(act, dict) and set(act) == OPERATOR_ACT_FIELDS):
        return False, ["OPERATOR_ACT_MALFORMED"]
    need(act["schema"] == OPERATOR_ACT_SCHEMA, "OPERATOR_ACT_SCHEMA")
    need(act["act_status"] == "ACTIVATED", "OPERATOR_ACT_NOT_ACTIVATED")
    need(act["proposal_id"] == prop.get("proposal_id"), "OPERATOR_ACT_PROPOSAL_MISMATCH")
    need(act["activation_report_id"] == ar.get("report_id"), "OPERATOR_ACT_REPORT_MISMATCH")
    need(act["diff_digest"] == "diff:" + ids.json_digest(prop["trust_root_diff"]), "OPERATOR_ACT_DIFF_MISMATCH")
    # recompute the live (resulting) root digest and the implied base; require the diff applied EXACTLY
    need(act["resulting_trust_root_digest"] == "tr:" + ids.json_digest(live_root), "OPERATOR_ACT_RESULT_MISMATCH")
    base = _reconstructed_base(live_root)
    need(act["base_trust_root_digest"] == "tr:" + ids.json_digest(base), "OPERATOR_ACT_BASE_MISMATCH")
    need(applied_trust_root(base, prop["trust_root_diff"]) == live_root, "OPERATOR_ACT_UNAUTHORIZED_CHANGE")
    need(isinstance(act["operator_identity"], str) and act["operator_identity"], "OPERATOR_ACT_NO_IDENTITY")
    need(isinstance(act["authority"], str) and act["authority"], "OPERATOR_ACT_NO_AUTHORITY")
    need(act["authorized_paths"] == AUTHORIZED_PATHS, "OPERATOR_ACT_PATHS")
    need(isinstance(act["parent_commit"], str) and act["parent_commit"], "OPERATOR_ACT_NO_PARENT")
    return len(F) == 0, F


def readback():
    base = load_strict_json(PAPER / "CORPUS-TRUST-ROOT.json")
    prop = load_strict_json(PAPER / "CORPUS-C2-MAP-ACTIVATION-0.1.json")
    ar = load_strict_json(PAPER / "CORPUS-C2-MAP-ACTIVATION-REPORT-0.1.json")
    diff = prop["trust_root_diff"]
    ok, faults = verify_activation_report(PAPER)
    applied = applied_trust_root(base, diff)
    tr_bad = validate_trust_root(applied)
    return {
        "report_verified": ok, "report_faults": faults,
        "base_trust_root_digest": "tr:" + ids.json_digest(base),
        "base_is_empty": base.get("decision_register") == [] and not (base.get("authorities") or {}).get("mapping"),
        "proposal_id": prop["proposal_id"],
        "activation_report_id": ar["report_id"],
        "diff_digest": "diff:" + ids.json_digest(diff),
        "resulting_trust_root_digest": "tr:" + ids.json_digest(applied),
        "resulting_trust_root_valid": tr_bad is None,
        "authorized_paths": AUTHORIZED_PATHS,
        "applied": applied,
    }


def _arg(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv else default


def main(argv):
    r = readback()
    print("# C2-MAP operator-act readback\n")
    print(f"report_verified            : {r['report_verified']}"
          + ("" if r["report_verified"] else f"  FAULTS={r['report_faults']}"))
    print(f"base_trust_root_digest     : {r['base_trust_root_digest']}  (empty={r['base_is_empty']})")
    print(f"proposal_id                : {r['proposal_id']}")
    print(f"activation_report_id       : {r['activation_report_id']}")
    print(f"diff_digest                : {r['diff_digest']}")
    print(f"resulting_trust_root_digest: {r['resulting_trust_root_digest']}  (valid={r['resulting_trust_root_valid']})")
    print(f"authorized_paths           : {r['authorized_paths']}")
    print("commit model               : one activation commit whose parent (pre-activation HEAD) is")
    print("                             the external commitment; record the resulting commit id in a")
    print("                             SEPARATE readback commit (no hash cycle — see P0-3).")

    # P1-5: fail closed unless the current base is the expected empty pre-activation state.
    ok = r["report_verified"] and r["resulting_trust_root_valid"]
    if not r["base_is_empty"]:
        print("\nREFUSED: base trust root is NOT the expected empty pre-activation state — will not emit.")
        return 1
    emit = _arg(argv, "--emit")
    emit_act = _arg(argv, "--emit-act")
    if emit:
        Path(emit).write_text(json.dumps(r["applied"], indent=1, ensure_ascii=False))
        print(f"\nwrote resulting trust root -> {emit} (applying/committing it is the operator's act)")
    if emit_act:
        who = _arg(argv, "--operator", "")
        auth = _arg(argv, "--authority", "")
        parent = _arg(argv, "--parent", "")
        if not (who and auth and parent):
            print("REFUSED: --emit-act requires --operator, --authority, and --parent <pre-activation HEAD>.")
            return 1
        prop = load_strict_json(PAPER / "CORPUS-C2-MAP-ACTIVATION-0.1.json")
        ar = load_strict_json(PAPER / "CORPUS-C2-MAP-ACTIVATION-REPORT-0.1.json")
        act = build_operator_act(r["applied"], prop, ar, who, auth, parent)
        Path(emit_act).write_text(json.dumps(act, indent=1, ensure_ascii=False))
        print(f"wrote operator act -> {emit_act} (base={act['base_trust_root_digest'][:16]}…, "
              f"result={act['resulting_trust_root_digest'][:16]}…)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
