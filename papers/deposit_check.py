#!/usr/bin/env python3
"""
deposit_check.py — closed-manifest deposit gate for the papers.

Contract (Codex closure P0-4 + operator go, 2026-09-01):

- Binds the EXACT candidate paper by content digest and the EXACT closed ledger
  claim set (A: C1-C8, B: B1-B8). A missing/extra/duplicate claim ID, or a deleted
  or changed candidate draft, FAILS CLOSED — never green.
- Every claim resolves to CHECKED | EXCLUDED | REFUSED with a reason code and the
  operand ids it consumed. No aggregate "paper MATCH" is ever emitted.
- Paper A claims that depend on the not-yet-deposited frozen act corpus resolve to
  REFUSED: FROZEN_CORPUS_NOT_DEPOSITED — never a string-presence credit. When the
  corpus is later deposited, those rows move addressably from REFUSED to CHECKED.
- Executable claims bind to a term/AST hash, the evaluator identity, and an ACTUAL
  execution (not a manifest read). Where the executable is an EXTERNAL released
  distribution, its identity is bound first: the interpreter is named, never found
  on PATH, and a shadow module, a source checkout or another version refuses BEFORE
  its output is read as evidence. There is deliberately no `which(name) + rc == 0`
  strategy in this engine.
- Two DISTINCT notions, never merged:
    * mechanism-correct : the engine checks and refuses correctly (test_deposit_check.py);
    * deposit-clean     : the produced report has no blocking REFUSED.
- Emits a canonical machine-readable JSON report plus a short human summary.

Exit codes: 0 = deposit-clean; 1 = has blocking REFUSED (deposit BLOCKED); 3 = engine
fail-closed (candidate/ledger binding broken — the report itself cannot be trusted).
"""
import hashlib
import inspect
import json
import os
import re
import subprocess
import sys
from pathlib import Path

CHECKED, EXCLUDED, REFUSED = "CHECKED", "EXCLUDED", "REFUSED"
# claim ids are `C1`..`C8` and address-scoped sub-claims `C2-MAP` / `C2-MEAS`.
LEDGER_ID_RE = re.compile(r"^\|\s*([A-Z]+\d+(?:-[A-Z]+)?)\s*\|")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# --------------------------------------------------------------------------- #
# Ledger parsing: the closed set of claim ids, with duplicate detection.
# --------------------------------------------------------------------------- #
def parse_ledger_ids(ledger_text: str):
    ids, dupes, seen = [], [], set()
    for line in ledger_text.splitlines():
        m = LEDGER_ID_RE.match(line)
        if not m:
            continue
        cid = m.group(1)
        if cid in seen:
            dupes.append(cid)
        seen.add(cid)
        if cid not in ids:
            ids.append(cid)
    return ids, dupes


# --------------------------------------------------------------------------- #
# Receipt format: `{...json...}\nRECEIPT_SHA256: <hex>`, body carries source_sha256.
# --------------------------------------------------------------------------- #
def load_receipt(path: Path):
    txt = path.read_text()
    idx = txt.rfind("RECEIPT_SHA256")
    if idx < 0:
        raise ValueError("no RECEIPT_SHA256 trailer")
    body = txt[:idx].strip()
    committed = txt[idx:].split(":", 1)[1].strip()
    if sha256_bytes(body.encode()) != committed:
        raise ValueError("RECEIPT_INTEGRITY_BREAK")
    return json.loads(body), committed


def dig(obj, dotted):
    cur = obj
    for part in dotted.split("."):
        cur = cur[part]
    return cur


# --------------------------------------------------------------------------- #
# Evaluator identity (bound into every executable claim's evidence).
# --------------------------------------------------------------------------- #
def evaluator_identity(base: Path):
    tools = base / "tools"
    if str(tools) not in sys.path:
        sys.path.insert(0, str(tools))
    try:
        import glyphlib  # noqa
        import sigma_glyph  # noqa
    except Exception as e:  # pragma: no cover - environment-dependent
        return None, f"EVALUATOR_UNAVAILABLE: {e}"
    gd = sha256_file(Path(inspect.getfile(glyphlib)))
    return {"evaluator": "sigma-glyph==0.6.7", "glyphlib_sha256": gd}, None


def _term_hash(term) -> str:
    # glyphlib terms are plain nested tuples (S-expressions) -> canonical JSON.
    return sha256_bytes(json.dumps(term, separators=(",", ":")).encode())


# --------------------------------------------------------------------------- #
# Strategies. Each returns (status, reason, evidence_dict).
# Any exception is caught by the caller and becomes REFUSED: CHECK_ERROR.
# --------------------------------------------------------------------------- #
def strat_refused(base, spec):
    return REFUSED, spec["reason"], {}


def strat_excluded(base, spec):
    return EXCLUDED, spec["reason"], {}


def strat_recount_source(base, spec):
    src = base / spec["source"]
    if not src.exists():
        return REFUSED, "MISSING_SOURCE", {"source": spec["source"]}
    if "source_sha256" in spec and sha256_file(src) != spec["source_sha256"]:
        return REFUSED, "SOURCE_MISMATCH", {
            "source": spec["source"], "expected": spec["source_sha256"],
            "observed": sha256_file(src)}
    n = len(re.findall(spec["regex"], src.read_text(), re.M))
    if n != spec["expected"]:
        return REFUSED, "RESULT_MISMATCH", {"expected": spec["expected"], "recounted": n}
    return CHECKED, None, {"recounted": n, "source_sha256": sha256_file(src)}


def strat_receipt_tally(base, spec):
    evidence = {}
    for r in spec["receipts"]:
        rp = base / r["receipt"]
        if not rp.exists():
            return REFUSED, "MISSING_SOURCE", {"receipt": r["receipt"]}
        try:
            obj, _ = load_receipt(rp)
        except ValueError as e:
            return REFUSED, str(e), {"receipt": r["receipt"]}
        # the receipt commits the source it was computed over; re-verify it.
        src = base / r["source"]
        if not src.exists():
            return REFUSED, "MISSING_SOURCE", {"source": r["source"]}
        if obj.get("source_sha256") != sha256_file(src):
            return REFUSED, "SOURCE_MISMATCH", {
                "source": r["source"], "committed": obj.get("source_sha256"),
                "observed": sha256_file(src)}
        got = dig(obj, r["field"])
        if got != r["expected"]:
            return REFUSED, "RESULT_MISMATCH", {
                "receipt": r["receipt"], "field": r["field"],
                "expected": r["expected"], "got": got}
        evidence[r["receipt"]] = {"field": r["field"], "value": got}
    return CHECKED, None, evidence


def strat_vendored_profile(base, spec):
    path = base / spec["path"]
    if not path.exists():
        return REFUSED, "PROFILE_NOT_VENDORED", {
            "path": spec["path"], "commit": spec.get("commit")}
    if "sha256" in spec:
        observed = sha256_file(path) if path.is_file() else _dir_digest(path)
        if observed != spec["sha256"]:
            return REFUSED, "PROFILE_MISMATCH", {
                "path": spec["path"], "expected": spec["sha256"], "observed": observed}
    return CHECKED, None, {"path": spec["path"], "commit": spec.get("commit")}


def _dir_digest(d: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(d.rglob("*")):
        if f.is_file():
            h.update(sha256_file(f).encode())
    return h.hexdigest()


# --------------------------------------------------------------------------- #
# B7 — Warrant conformance. TWO deliberately separate observations, bound
# separately; neither may be spent as credit for the other.
#
#   (1) ONE STORED CHECK RE-EXECUTES. Not "something named `warrant` was on PATH
#       and exited 0" — the retired `command` strategy awarded credit for exactly
#       that. Here the interpreter is named explicitly (never resolved through
#       PATH), the distribution identity `warrant-verify==0.9.0` is read out of
#       that interpreter's own installed metadata, the module actually imported
#       must be the file that distribution installed at the pinned digest, and
#       the exact machine output is parsed with status, result hash and ATP each
#       compared independently.
#   (2) THE PACK AS A WHOLE IS STILL LEGACY-SEALED. `replay_pack.py replay` must
#       return the exact `LEGACY_UNPINNED` typed refusal at exit 1. Exit 0, a
#       different refusal, or output drift refuses B7: a strict pack replay
#       showing up here would mean the claim's second half had become false.
# --------------------------------------------------------------------------- #

# Runs INSIDE the named interpreter. Reports identity; it never judges it — every
# comparison is made here, against the manifest's pins.
WARRANT_IDENTITY_PROBE = r'''
import base64, hashlib, importlib.metadata as md, importlib.util, json, pathlib, sys
dist_name, module_name = sys.argv[1], sys.argv[2]
out = {}
try:
    dist = md.distribution(dist_name)
except Exception as e:
    print(json.dumps({"probe_error": "DISTRIBUTION_ABSENT", "detail": repr(e)}))
    raise SystemExit(0)
out["dist_name"] = dist.metadata["Name"]
out["version"] = dist.version
spec = importlib.util.find_spec(module_name)
if spec is None or not spec.origin:
    print(json.dumps({"probe_error": "MODULE_ABSENT", **out}))
    raise SystemExit(0)
origin = pathlib.Path(spec.origin).resolve()
out["origin"] = str(origin)
out["module_sha256"] = hashlib.sha256(origin.read_bytes()).hexdigest()
owned = None
for f in (dist.files or ()):
    if pathlib.Path(dist.locate_file(f)).resolve() == origin:
        owned = f
        break
out["owned_by_distribution"] = owned is not None
if owned is not None and owned.hash is not None and owned.hash.mode == "sha256":
    out["record_sha256"] = base64.urlsafe_b64decode(owned.hash.value + "==").hex()
print(json.dumps(out))
'''

# `pass  result=<64 hex>  atp_spent=<int>` — the whole line, nothing else.
STORED_CHECK_RE = re.compile(
    r"^(?P<status>[A-Za-z_]+)  result=(?P<result>[0-9a-f]{64})  "
    r"atp_spent=(?P<atp>\d+)$")


def _norm_dist(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _sealed_env():
    """A deterministic environment for both the probe and the execution.

    PATH is present only because a subprocess wants one; nothing here is ever
    LOOKED UP in it — the interpreter is invoked by absolute path and the CLI is
    reached as `-m <module>`. PYTHONPATH/PYTHONHOME are dropped so a developer
    checkout cannot shadow the installed distribution between probe and run.
    """
    env = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"}
    if "HOME" in os.environ:
        env["HOME"] = os.environ["HOME"]
    return env


def _bind_warrant_artifact(base, spec):
    """Bind the executed artifact to the named released distribution.

    Returns (identity, None) or (None, (reason, evidence)). A shadow module, a
    source checkout, another distribution or another version refuses HERE —
    before any output of that artifact is read as evidence of anything.
    """
    var = spec["python_env_var"]
    ev = {"python_env_var": var, "distribution": spec["distribution"],
          "expected_version": spec["version"], "module": spec["module"]}
    interp = os.environ.get(var)
    if not interp:
        return None, ("WARRANT_ENV_NOT_PROVIDED", ev)
    ip = Path(interp)
    ev["interpreter"] = str(ip)
    if not ip.is_file() or not os.access(ip, os.X_OK):
        return None, ("WARRANT_ENV_UNUSABLE", {**ev, "detail": "not an executable file"})
    # `-I` for the probe AND for the execution below: same isolation, same cwd, so
    # the module the probe resolved is exactly the module that then runs.
    probe = subprocess.run(
        [str(ip), "-I", "-c", WARRANT_IDENTITY_PROBE, spec["distribution"], spec["module"]],
        cwd=str(base / spec["pack"]), capture_output=True, text=True, env=_sealed_env())
    if probe.returncode != 0:
        return None, ("WARRANT_ENV_UNUSABLE",
                      {**ev, "rc": probe.returncode, "stderr": probe.stderr[-500:]})
    try:
        info = json.loads(probe.stdout)
    except ValueError:
        return None, ("WARRANT_ENV_UNUSABLE", {**ev, "stdout": probe.stdout[-500:]})
    if info.get("probe_error"):
        return None, ("WARRANT_DISTRIBUTION_ABSENT" if info["probe_error"] == "DISTRIBUTION_ABSENT"
                      else "WARRANT_MODULE_ABSENT", {**ev, **info})
    if _norm_dist(info["dist_name"]) != _norm_dist(spec["distribution"]):
        return None, ("WARRANT_DISTRIBUTION_MISMATCH", {**ev, "observed": info["dist_name"]})
    if info["version"] != spec["version"]:
        return None, ("WARRANT_VERSION_MISMATCH", {**ev, "observed": info["version"]})
    # The module that WOULD be imported must be the file the distribution installed.
    if not info.get("owned_by_distribution"):
        return None, ("WARRANT_ARTIFACT_SHADOWED", {**ev, "origin": info.get("origin")})
    if info["module_sha256"] != spec["module_sha256"]:
        return None, ("WARRANT_ARTIFACT_MISMATCH",
                      {**ev, "expected": spec["module_sha256"],
                       "observed": info["module_sha256"], "origin": info["origin"]})
    # Second, independent binding: the installed bytes vs the digest the wheel recorded.
    rec = info.get("record_sha256")
    if rec is not None and rec != info["module_sha256"]:
        return None, ("WARRANT_ARTIFACT_RECORD_MISMATCH",
                      {**ev, "record": rec, "observed": info["module_sha256"]})
    return {"distribution": f'{spec["distribution"]}=={info["version"]}',
            "module": spec["module"], "module_sha256": info["module_sha256"],
            "record_sha256": rec, "origin": info["origin"],
            "interpreter": str(ip), "python_env_var": var}, None


def _stored_check(base, spec, ident):
    """Observation 1: ONE stored check re-executes, to the exact stated result."""
    pack = base / spec["pack"]
    cmd = ["-I", "-m", spec["module"], "--store", spec["store"], "check", spec["check_id"]]
    out = subprocess.run([ident["interpreter"], *cmd], cwd=str(pack),
                         capture_output=True, text=True, env=_sealed_env())
    ev = {"argv": cmd, "cwd": spec["pack"], "check_id": spec["check_id"],
          "rc": out.returncode}
    if out.returncode != 0:
        return None, ("STORED_CHECK_FAILED", {**ev, "stderr": out.stderr[-500:]})
    lines = [ln for ln in out.stdout.splitlines() if ln.strip()]
    if len(lines) != 1:
        return None, ("STORED_CHECK_OUTPUT_DRIFT", {**ev, "lines": len(lines),
                                                    "stdout": out.stdout[-500:]})
    m = STORED_CHECK_RE.match(lines[0])
    if not m:
        return None, ("STORED_CHECK_OUTPUT_DRIFT", {**ev, "line": lines[0]})
    status, result, atp = m["status"], m["result"], int(m["atp"])
    ev.update({"status": status, "result": result, "atp_spent": atp})
    # Three independent comparisons, three distinct refusals: a wrong verdict, a
    # wrong result address and a wrong price are different failures of the claim.
    if status != spec["expect_status"]:
        return None, ("STORED_CHECK_STATUS_MISMATCH",
                      {**ev, "expected": spec["expect_status"]})
    if result != spec["expect_result"]:
        return None, ("STORED_CHECK_RESULT_MISMATCH",
                      {**ev, "expected": spec["expect_result"]})
    if atp != spec["expect_atp"]:
        return None, ("STORED_CHECK_ATP_MISMATCH", {**ev, "expected": spec["expect_atp"]})
    return ev, None


def _pack_replay(base, spec):
    """Observation 2: the pack as a whole is NOT strict replay evidence.

    The expected outcome is a refusal. Success here would not be better news —
    it would mean the pack stopped being the legacy-sealed artifact B7 describes,
    so exit 0 refuses B7 just as loudly as the wrong refusal does."""
    r = spec["pack_replay"]
    script = base / r["script"]
    if not script.is_file():
        return None, ("PACK_REPLAY_SCRIPT_MISSING", {"script": r["script"]})
    out = subprocess.run([sys.executable, str(script), *r["args"]], cwd=str(base),
                         capture_output=True, text=True)
    lines = [ln for ln in out.stdout.splitlines() if ln.strip()]
    ev = {"script": r["script"], "args": r["args"], "rc": out.returncode,
          "status_line": lines[-1] if lines else ""}
    if out.returncode != r["expect_rc"] or ev["status_line"] != r["expect_status_line"]:
        return None, ("PACK_NOT_LEGACY_UNPINNED",
                      {**ev, "expected_rc": r["expect_rc"],
                       "expected_status_line": r["expect_status_line"]})
    return ev, None


def strat_warrant_conformance(base, spec):
    store = base / spec["pack"] / spec["store"]
    if not store.is_dir():
        return REFUSED, "WARRANT_STORE_MISSING", {
            "store": f'{spec["pack"]}/{spec["store"]}'}
    ident, refusal = _bind_warrant_artifact(base, spec)
    if refusal:
        return REFUSED, refusal[0], refusal[1]
    stored, refusal = _stored_check(base, spec, ident)
    if refusal:
        return REFUSED, refusal[0], {"artifact": ident, **refusal[1]}
    replay, refusal = _pack_replay(base, spec)
    if refusal:
        # The per-check pass is NOT credit for the pack. It is reported and the
        # claim still refuses.
        return REFUSED, refusal[0], {"artifact": ident, "stored_check": stored,
                                     "pack_replay": refusal[1]}
    return CHECKED, None, {"artifact": ident, "stored_check": stored,
                           "pack_replay": replay}


def strat_evaluator_replay(base, spec):
    ident, err = evaluator_identity(base)
    if ident is None:
        return REFUSED, "EVALUATOR_UNAVAILABLE", {"detail": err}
    runner = spec["runner"]
    if runner == "compile_0030":
        script = base / spec["script"]
        out = subprocess.run([sys.executable, str(script)],
                             capture_output=True, text=True)
        if out.returncode != 0:
            return REFUSED, "EVALUATOR_FAILED", {"rc": out.returncode}
        body = json.loads(out.stdout[:out.stdout.rfind("RECEIPT_SHA256")].strip())
        tr = body["traces"]
        got_v = [tr[k]["machine_layer"]["verdict"] for k in sorted(tr)]
        got_a = {k: tr[k]["machine_layer"]["atp_spent"] for k in sorted(tr)}
        if got_v != spec["expect_verdicts"] or got_a != spec["expect_atp"]:
            return REFUSED, "RESULT_MISMATCH", {
                "expected": [spec["expect_verdicts"], spec["expect_atp"]],
                "got": [got_v, got_a]}
        return CHECKED, None, {"evaluator": ident, "verdicts": got_v, "atp": got_a}
    if runner == "glyphlib":
        import glyphlib as gl
        results = []
        for case in spec["cases"]:
            a, b, c = case["a"], case["b"], case["c"]
            op = gl.PLUS if case["op"] == "+" else gl.MULT
            term = gl.A(op, gl.church(a), gl.church(b))
            if case["kind"] == "nat_eq":
                v, s, meta = gl.settle_nat_eq(term, gl.church(c))
            else:  # bool_eqn
                v, s, meta = gl.settle_bool(
                    gl.A(gl.EQN, term, gl.church(c)), atp=case.get("atp", 60_000_000))
            th = _term_hash(term)
            if isinstance(meta, dict) and "lhs" in meta and "rhs" in meta:
                nf = {"lhs": meta["lhs"]["term"], "rhs": meta["rhs"]["term"]}
            else:  # settle_bool returns a single result address string
                nf = {"result": meta}
            ev = {"case": case["label"], "term_sha256": th, "verdict": v, "atp": s,
                  "normal_forms": nf}
            results.append(ev)
            if [v, s] != [case["expect_verdict"], case["expect_atp"]]:
                return REFUSED, "RESULT_MISMATCH", {
                    "case": case["label"], "expected": [case["expect_verdict"],
                    case["expect_atp"]], "got": [v, s], "term_sha256": th}
        return CHECKED, None, {"evaluator": ident, "cases": results}
    if runner == "script_exit0":
        script = base / spec["script"]
        out = subprocess.run([sys.executable, str(script)],
                             capture_output=True, text=True)
        if out.returncode != 0:
            return REFUSED, "EVALUATOR_FAILED", {"script": spec["script"], "rc": out.returncode}
        return CHECKED, None, {"evaluator": ident, "script": spec["script"]}
    raise ValueError(f"unknown runner {runner!r}")


def strat_corpus_activation(base, spec):
    """C2-MAP (cohort addressability) at the deposit boundary.

    Consumes the LIVE committed trust root plus the independently-verified activation report.
    The report's raw-span truth is machine-local; here we (a) re-verify every recomputable
    relation via verify_activation_report (a coherent single-file re-forge fails), and (b) check
    whether the LIVE trust root actually applies the proposal's activation. Before the operator
    applies the diff the trust root is empty -> REFUSED: ACTIVATION_NOT_APPLIED. After it is
    applied -> CHECKED. This NEVER touches C2-MEAS, which is a separate refused claim."""
    corpus_dir = (base / spec["corpus_dir"]).resolve()
    corpus_code = (base / "papers" / "corpus").resolve()
    if str(corpus_code) not in sys.path:
        sys.path.insert(0, str(corpus_code))
    try:
        from corpus_activation_report import verify_activation_report
        from corpus_map import load_strict_json, validate_trust_root
        from corpus_operator_readback import (validate_operator_act, applied_trust_root,
                                              _reconstructed_base, verify_activation_commit,
                                              COMMIT_RECEIPT, _git)
    except Exception as e:  # noqa
        return REFUSED, "CORPUS_ENGINE_UNAVAILABLE", {"detail": repr(e)}

    ok, faults = verify_activation_report(corpus_dir)
    if not ok:
        return REFUSED, "REPORT_UNVERIFIED", {"faults": faults}
    try:
        tr = load_strict_json(corpus_dir / "CORPUS-TRUST-ROOT.json")
        prop = load_strict_json(corpus_dir / "CORPUS-C2-MAP-ACTIVATION-0.1.json")
        ar = load_strict_json(corpus_dir / "CORPUS-C2-MAP-ACTIVATION-REPORT-0.1.json")
    except ValueError as e:
        return REFUSED, "STRICT_JSON", {"detail": str(e)}
    if validate_trust_root(tr) is not None:
        return REFUSED, "TRUST_ROOT_INVALID", {}

    diff = prop["trust_root_diff"]
    ev = {"report_id": ar["report_id"], "proposal_id": prop["proposal_id"],
          "l2_bundle_id": tr.get("l2_bundle_id"),
          "evaluation_id": ar["result_vector"]["applied"].get("evaluation_id")}
    # EXACT application (not subset): the live root must be the empty pinned base with ONLY the
    # diff's four credit fields applied, nothing else changed.
    if applied_trust_root(_reconstructed_base(tr), diff) != tr:
        return REFUSED, "ACTIVATION_NOT_APPLIED", ev
    # P0-3: a path-limited operator governance act is a REQUIRED operand. A manual/unattributed
    # root edit (no act, or one naming another base/proposal/report/result) is REFUSED.
    act_path = corpus_dir / "CORPUS-OPERATOR-ACT.json"
    if not act_path.exists():
        return REFUSED, "OPERATOR_ACT_ABSENT", ev
    try:
        act = load_strict_json(act_path)
    except ValueError as e:
        return REFUSED, "OPERATOR_ACT_STRICT_JSON", {"detail": str(e)}
    act_ok, act_faults = validate_operator_act(act, tr, prop, ar)
    if not act_ok:
        return REFUSED, "OPERATOR_ACT_INVALID", {**ev, "faults": act_faults}
    # P0-1: the act must be a REAL path-limited Git activation commit, not a self-minted JSON.
    receipt_path = corpus_dir / COMMIT_RECEIPT
    if not receipt_path.exists():
        return REFUSED, "OPERATOR_COMMIT_RECEIPT_ABSENT", ev
    try:
        receipt = load_strict_json(receipt_path)
    except ValueError as e:
        return REFUSED, "OPERATOR_COMMIT_RECEIPT_STRICT_JSON", {"detail": str(e)}
    rc, top = _git(corpus_dir, "rev-parse", "--show-toplevel")
    if rc != 0 or not top.strip():
        return REFUSED, "OPERATOR_COMMIT_PROVENANCE_UNAVAILABLE", ev
    repo_top = top.decode().strip()
    live_root_bytes = (corpus_dir / "CORPUS-TRUST-ROOT.json").read_bytes()
    act_bytes = act_path.read_bytes()
    receipt_bytes = receipt_path.read_bytes()
    commit_ok, commit_faults = verify_activation_commit(
        repo_top, corpus_dir, act, receipt, live_root_bytes, act_bytes,
        receipt_bytes, spec.get("trust_anchor"))
    if not commit_ok:
        return REFUSED, "OPERATOR_COMMIT_UNVERIFIED", {**ev, "faults": commit_faults}
    if ar["result_vector"]["applied"].get("C2-MAP") != "COMPLETE":
        return REFUSED, "REPORT_NOT_COMPLETE", ev
    return CHECKED, None, {**ev, "operator": act["operator_identity"], "authority": act["authority"],
                           "activation_commit": receipt["activation_commit"],
                           "parent_commit": act["parent_commit"]}


STRATEGIES = {
    "refused": strat_refused,
    "excluded": strat_excluded,
    "recount_source": strat_recount_source,
    "receipt_tally": strat_receipt_tally,
    "vendored_profile": strat_vendored_profile,
    "warrant_conformance": strat_warrant_conformance,
    "evaluator_replay": strat_evaluator_replay,
    "corpus_activation": strat_corpus_activation,
}


# --------------------------------------------------------------------------- #
# Engine.
# --------------------------------------------------------------------------- #
def evaluate(manifest_path):
    manifest_path = Path(manifest_path).resolve()
    manifest = json.loads(manifest_path.read_text())
    base = (manifest_path.parent / manifest["base"]).resolve()

    report = {"paper": manifest["paper"], "engine": "OK", "engine_faults": [],
              "candidate": {}, "ledger": {}, "claims": [], "summary": {},
              "deposit": None}

    # 1. Candidate binding (fail-closed).
    cand = base / manifest["candidate"]["path"]
    report["candidate"] = {"path": manifest["candidate"]["path"],
                           "expected_sha256": manifest["candidate"]["sha256"],
                           "observed_sha256": None, "bound": False}
    if not cand.exists():
        report["engine"] = "FAIL_CLOSED"
        report["engine_faults"].append({"code": "CANDIDATE_MISSING",
                                        "path": manifest["candidate"]["path"]})
        return report
    observed = sha256_file(cand)
    report["candidate"]["observed_sha256"] = observed
    if observed != manifest["candidate"]["sha256"]:
        report["engine"] = "FAIL_CLOSED"
        report["engine_faults"].append({"code": "CANDIDATE_DIGEST_MISMATCH",
                                        "expected": manifest["candidate"]["sha256"],
                                        "observed": observed})
        return report
    report["candidate"]["bound"] = True

    # 2. Closed ledger set (fail-closed on any drift).
    ledger = base / manifest["ledger"]["path"]
    declared = manifest["ledger"]["closed_ids"]
    manifest_ids = list(manifest["claims"].keys())
    report["ledger"] = {"path": manifest["ledger"]["path"], "declared": declared}
    if not ledger.exists():
        report["engine"] = "FAIL_CLOSED"
        report["engine_faults"].append({"code": "LEDGER_MISSING"})
        return report
    parsed, dupes = parse_ledger_ids(ledger.read_text())
    faults = []
    if dupes:
        faults.append({"code": "DUPLICATE_CLAIM_ID", "ids": sorted(set(dupes))})
    missing = [c for c in declared if c not in parsed]
    extra = [c for c in parsed if c not in declared]
    if missing:
        faults.append({"code": "LEDGER_SET_DRIFT", "kind": "missing_in_ledger", "ids": missing})
    if extra:
        faults.append({"code": "LEDGER_SET_DRIFT", "kind": "extra_in_ledger", "ids": extra})
    if sorted(manifest_ids) != sorted(declared):
        faults.append({"code": "MANIFEST_SET_DRIFT",
                       "manifest_only": [c for c in manifest_ids if c not in declared],
                       "declared_only": [c for c in declared if c not in manifest_ids]})
    if faults:
        report["engine"] = "FAIL_CLOSED"
        report["engine_faults"] = faults
        report["ledger"]["parsed"] = parsed
        return report

    # 3. Per-claim dispatch (fail-closed per claim, never green-on-error).
    for cid in declared:
        spec = manifest["claims"][cid]
        strat = STRATEGIES.get(spec["strategy"])
        try:
            if strat is None:
                status, reason, evidence = REFUSED, "UNKNOWN_STRATEGY", {"strategy": spec["strategy"]}
            else:
                status, reason, evidence = strat(base, spec)
        except Exception as e:  # never let an error read as pass
            status, reason, evidence = REFUSED, "CHECK_ERROR", {"error": repr(e)}
        report["claims"].append({
            "id": cid, "title": spec.get("title", ""), "class": spec.get("class", ""),
            "status": status, "reason": reason,
            "operands": spec.get("operands", []), "evidence": evidence})

    report["summary"] = {
        "checked": [c["id"] for c in report["claims"] if c["status"] == CHECKED],
        "excluded": [c["id"] for c in report["claims"] if c["status"] == EXCLUDED],
        "refused": [c["id"] for c in report["claims"] if c["status"] == REFUSED],
    }
    report["deposit"] = "BLOCKED" if report["summary"]["refused"] else "CLEAN"
    return report


def exit_code(report) -> int:
    if report["engine"] == "FAIL_CLOSED":
        return 3
    return 1 if report["deposit"] == "BLOCKED" else 0


def human_summary(report) -> str:
    lines = [f"# deposit-check: {report['paper']}"]
    c = report["candidate"]
    lines.append(f"candidate: {c['path']} bound={c['bound']} "
                 f"({(c.get('observed_sha256') or '')[:12]})")
    if report["engine"] == "FAIL_CLOSED":
        lines.append("ENGINE: FAIL_CLOSED (report untrustworthy) — "
                     + "; ".join(f["code"] for f in report["engine_faults"]))
        return "\n".join(lines)
    for cl in report["claims"]:
        tag = {"CHECKED": "ok  ", "EXCLUDED": "--  ", "REFUSED": "XX  "}[cl["status"]]
        r = f" [{cl['reason']}]" if cl["reason"] else ""
        lines.append(f"{tag}{cl['id']}: {cl['status']}{r}")
    s = report["summary"]
    lines.append(f"summary: {len(s['checked'])} CHECKED / {len(s['excluded'])} EXCLUDED "
                 f"/ {len(s['refused'])} REFUSED")
    lines.append(f"DEPOSIT: {report['deposit']}"
                 + ("" if report["deposit"] == "CLEAN"
                    else f" (blocking: {', '.join(s['refused'])})"))
    lines.append("NOTE: this is a per-claim vector, never an aggregate 'paper MATCH'.")
    return "\n".join(lines)


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    as_json = "--json" in argv
    manifest = [a for a in argv if not a.startswith("-")][0]
    report = evaluate(manifest)
    if as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(human_summary(report))
    return exit_code(report)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
