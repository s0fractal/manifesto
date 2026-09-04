#!/usr/bin/env python3
"""
test_deposit_check.py — mechanism tests for the closed-manifest deposit gate.

This proves the ENGINE is mechanism-correct: it CHECKS a clean fixture and, more
importantly, it FAILS CLOSED / REFUSES under every mutation the operator required
(Codex closure P0-4, go 2026-09-01):

  delete candidate · change a number keeping the old literal · claim-ID drift ·
  profile swap · missing vendored profile · receipt/source mismatch · duplicate id.

It also carries the four B7 bypasses Codex reproduced against the (now removed)
`warrant_conformance` strategy as standing negative controls: an executable that
impersonates the Warrant environment, a bound front module that is not the runtime
closure, an in-tree replay tool used as its own success oracle, and an
opportunistic RECORD binding. None of them can move B7 out of REFUSED.

It is deliberately independent of sigma-glyph: it drives the engine with synthetic
`recount_source`, `receipt_tally`, and `vendored_profile` claims so "mechanism green"
never depends on "deposit clean". Run: `python3 papers/test_deposit_check.py`.
"""
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deposit_check import evaluate, exit_code  # noqa: E402

fails = []


def expect(name, cond):
    print(f"{'ok  ' if cond else 'FAIL'} {name}")
    if not cond:
        fails.append(name)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def build_fixture(root: Path):
    """A self-contained, evaluator-free fixture: candidate + ledger + 3 claims."""
    cand = b"candidate paper v1\n\nnumber: 3\n"
    (root / "candidate.md").write_bytes(cand)

    (root / "LEDGER.md").write_text(
        "| # | claim |\n|---|---|\n"
        "| K1 | recount |\n| K2 | receipt |\n| K3 | vendored |\n")

    src = b"## H a\n## H b\n## H c\n"          # 3 headings
    (root / "src.md").write_bytes(src)

    rsrc = b"index audit source\n"
    (root / "rsrc.md").write_bytes(rsrc)
    body = json.dumps({"source_sha256": sha(rsrc), "tally": {"refuted": 4}})
    (root / "rcpt.json").write_text(body + "\nRECEIPT_SHA256: " + sha(body.encode()))

    vend = root / "vend"
    vend.mkdir()
    (vend / "profile.py").write_text("# admitted domain\n")

    def dir_digest(d):
        h = hashlib.sha256()
        for f in sorted(d.rglob("*")):
            if f.is_file():
                h.update(sha(f.read_bytes()).encode())
        return h.hexdigest()

    manifest = {
        "paper": "fixture", "base": ".",
        "candidate": {"path": "candidate.md", "sha256": sha(cand)},
        "ledger": {"path": "LEDGER.md", "closed_ids": ["K1", "K2", "K3"]},
        "claims": {
            "K1": {"strategy": "recount_source", "source": "src.md",
                   "source_sha256": sha(src), "regex": "^## H", "expected": 3},
            "K2": {"strategy": "receipt_tally", "receipts": [
                {"receipt": "rcpt.json", "source": "rsrc.md",
                 "field": "tally.refuted", "expected": 4}]},
            "K3": {"strategy": "vendored_profile", "path": "vend",
                   "sha256": dir_digest(vend)},
        },
    }
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return root / "manifest.json"


def fresh():
    d = Path(tempfile.mkdtemp())
    return d, build_fixture(d)


def status_of(report, cid):
    return next(c for c in report["claims"] if c["id"] == cid)


# --- baseline: clean fixture is CHECKED and deposit-CLEAN ------------------- #
d, m = fresh()
r = evaluate(m)
expect("baseline engine OK", r["engine"] == "OK")
expect("baseline all CHECKED", r["summary"]["checked"] == ["K1", "K2", "K3"])
expect("baseline deposit CLEAN", r["deposit"] == "CLEAN")
expect("baseline exit 0", exit_code(r) == 0)
shutil.rmtree(d)

# --- mutation 1: delete candidate -> FAIL_CLOSED, exit 3 ------------------- #
d, m = fresh()
(d / "candidate.md").unlink()
r = evaluate(m)
expect("delete-candidate FAIL_CLOSED", r["engine"] == "FAIL_CLOSED")
expect("delete-candidate CANDIDATE_MISSING",
       r["engine_faults"][0]["code"] == "CANDIDATE_MISSING")
expect("delete-candidate exit 3", exit_code(r) == 3)
shutil.rmtree(d)

# --- mutation 2: change candidate bytes (stale pin) -> FAIL_CLOSED --------- #
d, m = fresh()
(d / "candidate.md").write_bytes(b"candidate paper v2 (tampered)\n")
r = evaluate(m)
expect("change-candidate DIGEST_MISMATCH",
       r["engine"] == "FAIL_CLOSED"
       and r["engine_faults"][0]["code"] == "CANDIDATE_DIGEST_MISMATCH")
expect("change-candidate exit 3", exit_code(r) == 3)
shutil.rmtree(d)

# --- mutation 3: change a number keeping the old literal/pin -> SOURCE_MISMATCH #
d, m = fresh()
(d / "src.md").write_bytes(b"## H a\n## H b\n## H c\n## H d\n")   # 4 now; pin/expected stale
r = evaluate(m)
expect("number-change K1 REFUSED SOURCE_MISMATCH",
       status_of(r, "K1")["status"] == "REFUSED"
       and status_of(r, "K1")["reason"] == "SOURCE_MISMATCH")
expect("number-change deposit BLOCKED", r["deposit"] == "BLOCKED" and exit_code(r) == 1)
shutil.rmtree(d)

# --- mutation 3b: pin updated but recount differs -> RESULT_MISMATCH -------- #
d, m = fresh()
newsrc = b"## H a\n## H b\n"          # only 2 now
(d / "src.md").write_bytes(newsrc)
mm = json.loads((d / "manifest.json").read_text())
mm["claims"]["K1"]["source_sha256"] = sha(newsrc)   # pin refreshed, literal (3) stale
(d / "manifest.json").write_text(json.dumps(mm))
r = evaluate(m)
expect("stale-literal K1 REFUSED RESULT_MISMATCH",
       status_of(r, "K1")["reason"] == "RESULT_MISMATCH")
shutil.rmtree(d)

# --- mutation 4: claim-ID drift (drop K3 from ledger) -> FAIL_CLOSED -------- #
d, m = fresh()
(d / "LEDGER.md").write_text("| # | claim |\n|---|---|\n| K1 | a |\n| K2 | b |\n")
r = evaluate(m)
expect("id-drift FAIL_CLOSED LEDGER_SET_DRIFT",
       r["engine"] == "FAIL_CLOSED"
       and any(f["code"] == "LEDGER_SET_DRIFT" for f in r["engine_faults"]))
expect("id-drift exit 3", exit_code(r) == 3)
shutil.rmtree(d)

# --- mutation 4b: duplicate claim id -> FAIL_CLOSED ------------------------ #
d, m = fresh()
(d / "LEDGER.md").write_text(
    "| # | c |\n|---|---|\n| K1 | a |\n| K2 | b |\n| K2 | dup |\n| K3 | c |\n")
r = evaluate(m)
expect("dup-id FAIL_CLOSED DUPLICATE_CLAIM_ID",
       any(f["code"] == "DUPLICATE_CLAIM_ID" for f in r["engine_faults"]))
shutil.rmtree(d)

# --- mutation 5: profile swap (wrong digest) -> PROFILE_MISMATCH ----------- #
d, m = fresh()
mm = json.loads((d / "manifest.json").read_text())
mm["claims"]["K3"]["sha256"] = "0" * 64
(d / "manifest.json").write_text(json.dumps(mm))
r = evaluate(m)
expect("profile-swap K3 REFUSED PROFILE_MISMATCH",
       status_of(r, "K3")["reason"] == "PROFILE_MISMATCH")
shutil.rmtree(d)

# --- mutation 6: missing vendored profile -> PROFILE_NOT_VENDORED ---------- #
d, m = fresh()
shutil.rmtree(d / "vend")
r = evaluate(m)
expect("missing-profile K3 REFUSED PROFILE_NOT_VENDORED",
       status_of(r, "K3")["reason"] == "PROFILE_NOT_VENDORED")
shutil.rmtree(d)

# --- mutation 7: receipt/source mismatch -> SOURCE_MISMATCH ---------------- #
d, m = fresh()
(d / "rsrc.md").write_bytes(b"index audit source CHANGED\n")   # receipt commitment now stale
r = evaluate(m)
expect("receipt-source-drift K2 REFUSED SOURCE_MISMATCH",
       status_of(r, "K2")["reason"] == "SOURCE_MISMATCH")
shutil.rmtree(d)

# --- mutation 7b: tampered receipt body -> RECEIPT_INTEGRITY_BREAK --------- #
d, m = fresh()
txt = (d / "rcpt.json").read_text()
idx = txt.rfind("RECEIPT_SHA256")
tampered = txt[:idx].replace('"refuted": 4', '"refuted": 999') + txt[idx:]
(d / "rcpt.json").write_text(tampered)
r = evaluate(m)
expect("tampered-receipt K2 REFUSED RECEIPT_INTEGRITY_BREAK",
       status_of(r, "K2")["reason"] == "RECEIPT_INTEGRITY_BREAK")
shutil.rmtree(d)

# --- an errored strategy must REFUSE, never pass --------------------------- #
d, m = fresh()
mm = json.loads((d / "manifest.json").read_text())
mm["claims"]["K1"] = {"strategy": "recount_source"}   # missing required keys
(d / "manifest.json").write_text(json.dumps(mm))
r = evaluate(m)
expect("errored-strategy K1 REFUSED CHECK_ERROR",
       status_of(r, "K1")["status"] == "REFUSED"
       and status_of(r, "K1")["reason"] == "CHECK_ERROR")
shutil.rmtree(d)

# --- sync guard: the REAL paper manifests must bind their current drafts ---- #
# Pure file ops (candidate digest + closed ledger set); no sigma-glyph needed.
# If a draft is edited without re-pinning its claim-manifest, this goes RED — that
# is the freshness discipline that closes Codex P0-4 for the papers themselves.
HERE = Path(__file__).resolve().parent
for name in ("every-check-spawns-more", "addressing-is-equality"):
    mf = HERE / name / "claim-manifest.json"
    if not mf.exists():
        expect(f"{name} manifest present", False)
        continue
    r = evaluate(mf)
    expect(f"{name} candidate + ledger BIND (engine OK)", r["engine"] == "OK")

# =========================================================================== #
# B7 — the four reproduced bypasses, as standing negative controls.
#
# The `warrant_conformance` strategy that once awarded B7 CHECKED was removed:
# Codex reproduced four ways to obtain that credit without the artifact. These
# controls keep it removed. They assert the SHAPE of the refusal — that nothing
# an attacker controls in the environment or in the tree can move B7 out of
# REFUSED — not merely that today's manifest happens to say `refused`.
#
# Hermetic by construction: each control builds its own hostile interpreter or
# tree under a temp root. Nothing consults ambient PATH, the network, a developer
# checkout, or the real released wheel.
# =========================================================================== #
import os
import subprocess

from deposit_check import STRATEGIES  # noqa: E402

B7_ID = "0597575d21d62c2db265c0d17e3a2c8c1b2db880342b117a403af7e9c4c03c87"
B7_RESULT = "e0419cc5112a95f9e35a019539b25f00eccbea33122a5736a20897d8eea5bf00"
B7_LINE = f"pass  result={B7_RESULT}  atp_spent=2108"
B7_REASON = "WARRANT_ARTIFACT_NOT_BINDABLE"

AIE = HERE / "addressing-is-equality" / "claim-manifest.json"
B7ROOT = Path(tempfile.mkdtemp())


def b7_under(env_overrides=None, manifest=AIE):
    """Evaluate the REAL paper-B manifest under a hostile environment."""
    prev = {k: os.environ.get(k) for k in (env_overrides or {})}
    os.environ.update(env_overrides or {})
    try:
        return status_of(evaluate(manifest), "B7")
    finally:
        for k, v in prev.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


# --- structural: no strategy in the engine can award B7 -------------------- #
# The two retired names, and the general property behind them: the engine holds
# no strategy that runs a foreign interpreter and reads its output as evidence.
expect("the generic `command` strategy is gone", "command" not in STRATEGIES)
expect("the `warrant_conformance` strategy is gone",
       "warrant_conformance" not in STRATEGIES)
expect("B7 consumes no strategy that can produce CHECKED",
       json.loads(AIE.read_text())["claims"]["B7"]["strategy"] == "refused")

# A manifest that still NAMES the removed strategy does not silently pass: an
# unknown strategy is a typed refusal, never credit.
d = B7ROOT / "unknown"
d.mkdir()
m = build_fixture(d)
mm = json.loads((d / "manifest.json").read_text())
mm["claims"]["K1"]["strategy"] = "warrant_conformance"
(d / "manifest.json").write_text(json.dumps(mm))
k = status_of(evaluate(m), "K1")
expect("a manifest naming `warrant_conformance` REFUSES UNKNOWN_STRATEGY",
       k["status"] == "REFUSED" and k["reason"] == "UNKNOWN_STRATEGY")

# --- baseline: the real B7 refuses, with the narrow reason ----------------- #
c = b7_under()
expect("B7 REFUSED with the narrow typed reason",
       c["status"] == "REFUSED" and c["reason"] == B7_REASON)
expect("B7 still names its operands", "tools/replay_pack.py" in c["operands"])

_r = evaluate(AIE)
expect("B7 is not in the CHECKED set", "B7" not in _r["summary"]["checked"])
expect("paper B still DEPOSIT: BLOCKED (B4 + B7)",
       _r["deposit"] == "BLOCKED" and {"B4", "B7"} <= set(_r["summary"]["refused"]))

# --- P0-1: an executable that impersonates the Warrant environment --------- #
# Codex's exact reproducer: a /bin/sh script that answers an identity probe with
# the pinned distribution/version/digest fields and then prints the exact
# `pass  result=…  atp_spent=2108` line. No Python, no Warrant, no wheel, no
# stored check. It used to award B7 CHECKED.
fake = B7ROOT / "fake-python"
fake.write_text(
    "#!/bin/sh\n"
    "if [ \"$2\" = \"-c\" ]; then\n"
    "  printf '%s\\n' '{\"dist_name\":\"warrant-verify\",\"version\":\"0.9.0\","
    "\"origin\":\"/tmp/not-warrant.py\",\"module_sha256\":"
    "\"0e6785679aa7b8133fc798794c8f72eb37bc3874b93cb494eadbd41f189d204a\","
    "\"owned_by_distribution\":true,\"record_sha256\":"
    "\"0e6785679aa7b8133fc798794c8f72eb37bc3874b93cb494eadbd41f189d204a\"}'\n"
    "  exit 0\n"
    "fi\n"
    f"printf '%s\\n' '{B7_LINE}'\n"
    "exit 0\n")
fake.chmod(0o755)
# the impersonator really does answer both probes convincingly ...
_probe = subprocess.run([str(fake), "-I", "-c", "x", "warrant-verify", "warrant"],
                        capture_output=True, text=True)
expect("P0-1 impersonator answers the identity probe (control is live)",
       '"version": "0.9.0"' in _probe.stdout.replace('":', '": '))
_run = subprocess.run([str(fake), "-I", "-m", "warrant", "check", B7_ID],
                      capture_output=True, text=True)
expect("P0-1 impersonator prints the exact pass line (control is live)",
       _run.stdout.strip() == B7_LINE and _run.returncode == 0)
# ... and buys nothing.
c = b7_under({"MANIFESTO_WARRANT_PYTHON": str(fake)})
expect("P0-1 impersonated environment CANNOT award B7",
       c["status"] == "REFUSED" and c["reason"] == B7_REASON)

# --- P0-2: a bound front module is not the runtime closure ----------------- #
# The old check pinned `warrant.py` only; mutating another installed file in the
# same environment (e.g. `sigma_glyph.py`) changed the bytes that compute the
# result while B7 stayed CHECKED. Nothing about an environment is read now, so
# there is no digest to satisfy and no closure to miss.
mutated = B7ROOT / "closure"
mutated.mkdir()
(mutated / "python3").write_text("#!/bin/sh\nprintf '%s\\n' '" + B7_LINE + "'\nexit 0\n")
(mutated / "python3").chmod(0o755)
c = b7_under({"MANIFESTO_WARRANT_PYTHON": str(mutated / "python3")})
expect("P0-2 no environment digest can award B7",
       c["status"] == "REFUSED" and c["reason"] == B7_REASON)
expect("P0-2 the report carries no environment evidence at all", c["evidence"] == {})

# --- P0-3: the pack-replay verifier lives in the tree it verifies ---------- #
# A four-line stub at `tools/replay_pack.py` printing `REPLAY: LEGACY_UNPINNED`
# and exiting 1 used to satisfy the second observation. Rebuild that tree — the
# real paper manifest, the real ledger and candidate, a stub replay tool — and
# confirm the stub buys nothing.
oracle = B7ROOT / "oracle"
(oracle / "tools").mkdir(parents=True)
(oracle / "papers" / "addressing-is-equality").mkdir(parents=True)
(oracle / "tools" / "replay_pack.py").write_text(
    "#!/usr/bin/env python3\nimport sys\nprint('REPLAY: LEGACY_UNPINNED')\nsys.exit(1)\n")
repo = HERE.parent
for rel in ("papers/addressing-is-equality/claim-manifest.json",
            "papers/addressing-is-equality/CLAIM-LEDGER.md"):
    shutil.copy2(repo / rel, oracle / rel)
shutil.copy2(repo / json.loads(AIE.read_text())["candidate"]["path"],
             oracle / json.loads(AIE.read_text())["candidate"]["path"])
_stub = subprocess.run([sys.executable, str(oracle / "tools" / "replay_pack.py"),
                        "replay", "drafts/ssd-pack"], capture_output=True, text=True)
expect("P0-3 stub replay tool emits the expected line at exit 1 (control is live)",
       _stub.stdout.strip() == "REPLAY: LEGACY_UNPINNED" and _stub.returncode == 1)
_or = evaluate(oracle / "papers/addressing-is-equality/claim-manifest.json")
expect("P0-3 the stub tree binds candidate + ledger (control is not vacuous)",
       _or["engine"] == "OK")
c = status_of(_or, "B7")
expect("P0-3 a stubbed in-tree replay tool CANNOT award B7",
       c["status"] == "REFUSED" and c["reason"] == B7_REASON)

# --- P1: no opportunistic binding is left to weaken ------------------------ #
# Emptying the wheel RECORD hash used to drop the second identity binding while
# B7 stayed CHECKED, because the cross-check was `if rec is not None`. The whole
# probe is gone; assert the engine reads no distribution metadata at all.
_engine = (HERE / "deposit_check.py").read_text()
for token in ("importlib.metadata", "record_sha256", "owned_by_distribution",
              "MANIFESTO_WARRANT_PYTHON", "python_env_var"):
    expect(f"P1 the engine no longer consults `{token}`", token not in _engine)

# --- the observations survive as observations, not as credit --------------- #
# The exact operands stay recorded in the manifest so the claim keeps its precise
# content; they are prose there, and no strategy reads them.
_b7 = json.loads(AIE.read_text())["claims"]["B7"]
expect("the stored-check observation is recorded verbatim",
       B7_RESULT in _b7["unbound_observations"]["stored_check"]
       and "atp_spent=2108" in _b7["unbound_observations"]["stored_check"])
expect("the pack observation is recorded verbatim",
       "REPLAY: LEGACY_UNPINNED" in _b7["unbound_observations"]["pack_replay"])
expect("recording an observation does not create a checked strategy field",
       "expect_result" not in _b7 and "module_sha256" not in _b7)

# --- a bound environment is STILL not credit ------------------------------- #
# CI installs the real warrant-verify==0.9.0 and runs both observations for the
# log. If MANIFESTO_WARRANT_PYTHON is set here, the ONLY assertion is that the
# report did not move: a real released artifact is not a back door either.
_real = os.environ.get("MANIFESTO_WARRANT_PYTHON")
if _real:
    c = b7_under()
    expect("REAL warrant-verify==0.9.0 present and B7 STILL REFUSED (non-crediting)",
           c["status"] == "REFUSED" and c["reason"] == B7_REASON)
else:
    print("skip  REAL warrant-verify==0.9.0 non-crediting control "
          "(set MANIFESTO_WARRANT_PYTHON; see DEPOSIT-AND-AUDIT §D)")

shutil.rmtree(B7ROOT)

print()
if fails:
    print(f"RED: {len(fails)} mechanism failure(s): {fails}")
    sys.exit(1)
print("GREEN: the deposit-check mechanism checks and fails-closed correctly.")
