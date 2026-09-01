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
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import corpus_ids as ids
from corpus_map import load_strict_json, validate_trust_root
from corpus_activation_report import verify_activation_report

PAPER = Path(__file__).resolve().parents[1] / "every-check-spawns-more"
AUTHORIZED_PATHS = ["papers/every-check-spawns-more/CORPUS-TRUST-ROOT.json",
                    "papers/every-check-spawns-more/CORPUS-OPERATOR-ACT.json"]
COMMIT_RECEIPT = "CORPUS-C2-MAP-COMMIT-RECEIPT.json"
RECEIPT_PATH = "papers/every-check-spawns-more/CORPUS-C2-MAP-COMMIT-RECEIPT.json"
COMMIT_RECEIPT_FIELDS = {"schema", "activation_commit", "parent_commit", "changed_paths",
                         "trust_root_blob_digest", "operator_act_blob_digest",
                         "proposal_id", "activation_report_id", "resulting_trust_root_digest"}
COMMIT_RECEIPT_SCHEMA = "manifesto.corpus.activation-commit-receipt.v0.1"


def _sha256_bytes(b):
    return "sha256:" + hashlib.sha256(b).hexdigest()


def _git(repo, *args):
    """Run a read-only git command; return (rc, stdout_bytes). rc!=0 -> git said no."""
    try:
        p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
        return p.returncode, p.stdout
    except (OSError, FileNotFoundError):
        return 127, b""


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


def build_commit_receipt(activation_commit, act, live_root_bytes, act_bytes):
    """The SEPARATE readback (second commit) that names the resulting activation commit — this is
    where the commit id lives, so the operator act itself never contains its own commit id (no cycle)."""
    return {"schema": COMMIT_RECEIPT_SCHEMA, "activation_commit": activation_commit,
            "parent_commit": act["parent_commit"], "changed_paths": list(AUTHORIZED_PATHS),
            "trust_root_blob_digest": _sha256_bytes(live_root_bytes),
            "operator_act_blob_digest": _sha256_bytes(act_bytes),
            "proposal_id": act["proposal_id"], "activation_report_id": act["activation_report_id"],
            "resulting_trust_root_digest": act["resulting_trust_root_digest"]}


def verify_activation_commit_core(repo_root, commit, act, live_root_bytes, act_bytes):
    """Local Git-execution integrity of the ACTIVATION commit alone: it exists, has exactly the named
    parent, changed exactly the two authorized paths, and its two committed blobs are byte-identical to
    the validated live root + operator act. Returns (ok, faults). Does NOT prove authority."""
    F = []

    def need(c, code):
        if not c:
            F.append(code)
        return c
    rc, _ = _git(repo_root, "rev-parse", "--git-dir")
    if rc != 0:
        return False, ["OPERATOR_COMMIT_PROVENANCE_UNAVAILABLE"]
    rc, _ = _git(repo_root, "cat-file", "-e", commit + "^{commit}")
    if not need(rc == 0, "ACTIVATION_COMMIT_MISSING"):
        return False, F
    rc, out = _git(repo_root, "rev-parse", commit + "^")
    rc2, want_parent = _git(repo_root, "rev-parse", act["parent_commit"])
    need(rc == 0 and rc2 == 0 and out.strip() and out.strip() == want_parent.strip(), "ACTIVATION_COMMIT_WRONG_PARENT")
    rc, out = _git(repo_root, "diff-tree", "--no-commit-id", "--name-only", "-r", commit)
    changed = sorted(x for x in out.decode().splitlines() if x)
    need(rc == 0 and changed == sorted(AUTHORIZED_PATHS), "ACTIVATION_COMMIT_PATHS")
    rc, root_at = _git(repo_root, "show", f"{commit}:{AUTHORIZED_PATHS[0]}")
    need(rc == 0 and root_at == live_root_bytes, "ACTIVATION_COMMIT_ROOT_BLOB")
    rc, act_at = _git(repo_root, "show", f"{commit}:{AUTHORIZED_PATHS[1]}")
    need(rc == 0 and act_at == act_bytes, "ACTIVATION_COMMIT_ACT_BLOB")
    return len(F) == 0, F


def _authority_ok(repo_root, commits, trust_anchor):
    """EXPLICIT authority contract (P0-2). Local reachability is NOT authority. Credit requires a
    declared external trust anchor: the given commits must be ancestors of the PINNED repository's
    fetched remote-tracking ref (a declared policy input — the fetched ref of the pinned remote — NOT
    cryptographic proof). Absent/attacker-local `.git` with no matching remote fails closed."""
    if not (isinstance(trust_anchor, dict) and trust_anchor.get("repo") and trust_anchor.get("ref")):
        return False, ["AUTHORITY_ANCHOR_REQUIRED"]
    rc, url = _git(repo_root, "config", "--get", "remote.origin.url")
    if rc != 0 or trust_anchor["repo"] not in url.decode().strip():
        return False, ["AUTHORITY_REMOTE_MISMATCH"]
    rc, _ = _git(repo_root, "rev-parse", "--verify", trust_anchor["ref"])
    if rc != 0:
        return False, ["AUTHORITY_REF_UNAVAILABLE"]
    for c in commits:
        rc, _ = _git(repo_root, "merge-base", "--is-ancestor", c, trust_anchor["ref"])
        if rc != 0:
            return False, ["AUTHORITY_COMMIT_NOT_PUSHED"]
    return True, []


def verify_activation_commit(repo_root, corpus_dir, act, receipt, live_root_bytes, act_bytes,
                             receipt_bytes, trust_anchor):
    """Bind the operator act to a REAL, path-limited TWO-COMMIT Git governance act (P0-1) with an
    EXPLICIT authority anchor (P0-2). Verifies both the activation commit AND the receipt commit as
    execution events, then requires the declared external authority anchor. Returns (ok, faults)."""
    F = []

    def need(c, code):
        if not c:
            F.append(code)
        return c
    # the commit receipt must be well-formed and agree with the operator act
    if not (isinstance(receipt, dict) and set(receipt) == COMMIT_RECEIPT_FIELDS):
        return False, ["COMMIT_RECEIPT_MALFORMED"]
    need(receipt["schema"] == COMMIT_RECEIPT_SCHEMA, "COMMIT_RECEIPT_SCHEMA")
    need(receipt["parent_commit"] == act["parent_commit"], "COMMIT_RECEIPT_PARENT_MISMATCH")
    need(receipt["proposal_id"] == act["proposal_id"], "COMMIT_RECEIPT_PROPOSAL_MISMATCH")
    need(receipt["activation_report_id"] == act["activation_report_id"], "COMMIT_RECEIPT_REPORT_MISMATCH")
    need(receipt["resulting_trust_root_digest"] == act["resulting_trust_root_digest"], "COMMIT_RECEIPT_RESULT_MISMATCH")
    need(receipt["changed_paths"] == list(AUTHORIZED_PATHS), "COMMIT_RECEIPT_PATHS")
    need(receipt["trust_root_blob_digest"] == _sha256_bytes(live_root_bytes), "COMMIT_RECEIPT_ROOT_BLOB")
    need(receipt["operator_act_blob_digest"] == _sha256_bytes(act_bytes), "COMMIT_RECEIPT_ACT_BLOB")
    if F:
        return False, F

    commit = receipt["activation_commit"]
    core_ok, core_f = verify_activation_commit_core(repo_root, commit, act, live_root_bytes, act_bytes)
    if not core_ok:
        return False, core_f

    # P0-1: the receipt COMMIT R (not just the working-tree file). R is the immediate descendant of the
    # activation commit on the path to HEAD; it must change EXACTLY the receipt path, and the committed
    # receipt blob must equal both the strict-loaded bytes AND the live working-tree bytes.
    rc, out = _git(repo_root, "rev-list", "--reverse", "--ancestry-path", f"{commit}..HEAD")
    chain = out.decode().split()
    R = chain[0] if rc == 0 and chain else None
    if not need(R is not None, "RECEIPT_COMMIT_MISSING"):
        return False, F
    rc, pout = _git(repo_root, "rev-parse", R + "^")
    need(rc == 0 and pout.decode().strip() == commit, "RECEIPT_COMMIT_WRONG_PARENT")
    rc, out = _git(repo_root, "diff-tree", "--no-commit-id", "--name-only", "-r", R)
    changed = sorted(x for x in out.decode().splitlines() if x)
    need(rc == 0 and changed == [RECEIPT_PATH], "RECEIPT_COMMIT_PATHS")
    rc, rec_at = _git(repo_root, "show", f"{R}:{RECEIPT_PATH}")
    need(rc == 0 and rec_at == receipt_bytes, "RECEIPT_COMMIT_BLOB")
    if F:
        return False, F

    # P0-2: explicit external authority anchor — both commits pushed to the pinned repository.
    auth_ok, auth_f = _authority_ok(repo_root, [commit, R], trust_anchor)
    if not auth_ok:
        return False, auth_f
    return True, []


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

    # POST-activation phase: emit the separate commit receipt naming the resulting activation commit.
    # (Runs after the operator commit, so the base is the resulting root, not empty — hence a distinct
    # branch that does not go through the empty-base guard below.)
    emit_receipt = _arg(argv, "--emit-receipt")
    if emit_receipt:
        commit = _arg(argv, "--commit", "")
        act_p, root_p = PAPER / "CORPUS-OPERATOR-ACT.json", PAPER / "CORPUS-TRUST-ROOT.json"
        if not (commit and act_p.exists()):
            print("REFUSED: --emit-receipt requires --commit <activation commit> and a committed operator act.")
            return 1
        # P1-3: refuse BEFORE writing unless the report verifies AND the named activation commit is a
        # real, path-limited activation commit with the expected blobs.
        if not r["report_verified"]:
            print(f"REFUSED: report verification failed ({r['report_faults']}) — will not emit receipt.")
            return 1
        rc, top = _git(PAPER, "rev-parse", "--show-toplevel")
        act = load_strict_json(act_p)
        core_ok, core_f = (verify_activation_commit_core(top.decode().strip(), commit, act,
                           root_p.read_bytes(), act_p.read_bytes()) if rc == 0 else (False, ["NO_GIT"]))
        if not core_ok:
            print(f"REFUSED: named activation commit does not verify ({core_f}) — will not emit receipt.")
            return 1
        rec = build_commit_receipt(commit, act, root_p.read_bytes(), act_p.read_bytes())
        Path(emit_receipt).write_text(json.dumps(rec, indent=1, ensure_ascii=False))
        print(f"\nwrote commit receipt -> {emit_receipt} (activation_commit={commit}); commit it SEPARATELY.")
        return 0

    # P1-2 + P1-5: fail closed BEFORE writing anything if verification failed or the base is not the
    # expected empty pre-activation state — never leave governance-looking artifacts from a bad run.
    ok = r["report_verified"] and r["resulting_trust_root_valid"]
    if not ok:
        print(f"\nREFUSED: report/root verification failed ({r['report_faults']}) — will not emit.")
        return 1
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
