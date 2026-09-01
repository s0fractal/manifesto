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
                    "papers/every-check-spawns-more/CORPUS-OPERATOR-ACT.md"]


def applied_trust_root(base, diff):
    """Base with ONLY the four credit-bearing governance fields replaced (path-limited)."""
    return {**base, "authorities": diff["authorities"],
            "pinned_manifests": diff["pinned_manifests"],
            "mapper_closure": diff["mapper_closure"],
            "decision_register": diff["decision_register"]}


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


def main(argv):
    r = readback()
    emit = None
    if "--emit" in argv:
        emit = argv[argv.index("--emit") + 1]
    print("# C2-MAP operator-act readback\n")
    print(f"report_verified            : {r['report_verified']}"
          + ("" if r["report_verified"] else f"  FAULTS={r['report_faults']}"))
    print(f"base_trust_root_digest     : {r['base_trust_root_digest']}  (empty={r['base_is_empty']})")
    print(f"proposal_id                : {r['proposal_id']}")
    print(f"activation_report_id       : {r['activation_report_id']}")
    print(f"diff_digest                : {r['diff_digest']}")
    print(f"resulting_trust_root_digest: {r['resulting_trust_root_digest']}  (valid={r['resulting_trust_root_valid']})")
    print(f"authorized_paths           : {r['authorized_paths']}")
    print("parent_commit_id           : <fill in after `git commit`>")
    print("resulting_commit_id        : <fill in after `git commit`>")
    if emit:
        Path(emit).write_text(json.dumps(r["applied"], indent=1, ensure_ascii=False))
        print(f"\nwrote resulting trust root -> {emit} (applying/committing it is the operator's act)")
    return 0 if r["report_verified"] and r["resulting_trust_root_valid"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
