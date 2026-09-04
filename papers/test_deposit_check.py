#!/usr/bin/env python3
"""
test_deposit_check.py — mechanism tests for the closed-manifest deposit gate.

This proves the ENGINE is mechanism-correct: it CHECKS a clean fixture and, more
importantly, it FAILS CLOSED / REFUSES under every mutation the operator required
(Codex closure P0-4, go 2026-09-01):

  delete candidate · change a number keeping the old literal · claim-ID drift ·
  profile swap · missing vendored profile · receipt/source mismatch · duplicate id.

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
# B7 — Warrant conformance: the two observations, and every way they refuse.
#
# Hermetic by construction. These build a throwaway venv and hand-install a
# SYNTHETIC `warrant-verify` distribution into it, so no control here consults
# ambient PATH, a developer source checkout, the network, or the real released
# wheel. The mechanism is what is under test: that identity is bound before
# output is read, that status / result / ATP are compared independently, and
# that a per-check pass is never spent as credit for the pack.
#
# The REAL positive (the released `warrant-verify==0.9.0` re-executing the
# stored check) is the opt-in tail of this section: set
# MANIFESTO_WARRANT_PYTHON to a clean 3.12 interpreter that has it installed.
# =========================================================================== #
import base64
import os
import venv

from deposit_check import STRATEGIES  # noqa: E402

B7_ID = "0597575d21d62c2db265c0d17e3a2c8c1b2db880342b117a403af7e9c4c03c87"
B7_RESULT = "e0419cc5112a95f9e35a019539b25f00eccbea33122a5736a20897d8eea5bf00"
B7_LINE = f"pass  result={B7_RESULT}  atp_spent=2108"

# A synthetic CLI that answers the ONE stored check id and nothing else. It is a
# stand-in for the released artifact, never a claim about it.
FAKE_WARRANT = '''
import sys
ID = "%s"
def main(argv):
    if "check" not in argv:
        return 2
    if argv[argv.index("check") + 1] != ID:
        return 2
    print(%%r)
    return 0
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
''' % B7_ID


def _record_line(rel, data: bytes) -> str:
    h = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode().rstrip("=")
    return f"{rel},sha256={h},{len(data)}"


def install_fake_dist(site, *, dist="warrant-verify", version="0.9.0", body=None):
    """Hand-install a synthetic distribution: module + METADATA + RECORD."""
    for old in site.glob("*.dist-info"):
        shutil.rmtree(old)
    for old in list(site.glob("*.pth")) + list(site.glob("warrant.py")):
        old.unlink()
    # Same-length mutations rewritten inside one mtime tick would otherwise
    # re-execute a stale .pyc and the "mutation" would not reach the engine.
    shutil.rmtree(site / "__pycache__", ignore_errors=True)
    src = (body if body is not None else FAKE_WARRANT % B7_LINE).encode()
    (site / "warrant.py").write_bytes(src)
    di = site / f"{dist.replace('-', '_')}-{version}.dist-info"
    di.mkdir()
    meta = f"Metadata-Version: 2.1\nName: {dist}\nVersion: {version}\n".encode()
    (di / "METADATA").write_bytes(meta)
    (di / "RECORD").write_text(
        _record_line("warrant.py", src) + "\n"
        + _record_line(f"{di.name}/METADATA", meta) + "\n"
        + f"{di.name}/RECORD,,\n")
    return site / "warrant.py"


def b7_manifest(root, interp, **over):
    """A manifest whose ONLY claim is B7, pointed at the real pack and replay."""
    repo = Path(__file__).resolve().parents[1]
    cand = root / "cand.md"
    cand.write_bytes(b"b7 fixture\n")
    (root / "LEDGER.md").write_text("| # | c |\n|---|---|\n| B7 | warrant |\n")
    spec = {
        "strategy": "warrant_conformance", "class": "conformance",
        "title": "b7 fixture",
        "python_env_var": "B7_TEST_PYTHON",
        "distribution": "warrant-verify", "version": "0.9.0", "module": "warrant",
        "module_sha256": sha((FAKE_WARRANT % B7_LINE).encode()),
        "pack": "drafts/ssd-pack", "store": ".warrants", "check_id": B7_ID,
        "expect_status": "pass", "expect_result": B7_RESULT, "expect_atp": 2108,
        "pack_replay": {"script": "tools/replay_pack.py",
                        "args": ["replay", "drafts/ssd-pack"],
                        "expect_rc": 1, "expect_status_line": "REPLAY: LEGACY_UNPINNED"},
        "operands": ["drafts/ssd-pack/.warrants"],
    }
    spec.update(over)
    mf = {"paper": "b7-fixture", "base": str(repo),
          "candidate": {"path": str(cand), "sha256": sha(cand.read_bytes())},
          "ledger": {"path": str(root / "LEDGER.md"), "closed_ids": ["B7"]},
          "claims": {"B7": spec}}
    (root / "manifest.json").write_text(json.dumps(mf, indent=2))
    return root / "manifest.json"


def run_b7(root, interp, *, set_env=True, **over):
    m = b7_manifest(root, interp, **over)
    prev = os.environ.get("B7_TEST_PYTHON")
    if set_env:
        os.environ["B7_TEST_PYTHON"] = str(interp)
    else:
        os.environ.pop("B7_TEST_PYTHON", None)
    try:
        return status_of(evaluate(m), "B7")
    finally:
        if prev is None:
            os.environ.pop("B7_TEST_PYTHON", None)
        else:
            os.environ["B7_TEST_PYTHON"] = prev


B7ROOT = Path(tempfile.mkdtemp())
VENV = B7ROOT / "venv"
venv.EnvBuilder(with_pip=False).create(VENV)
INTERP = VENV / "bin" / "python"
SITE = next((VENV / "lib").glob("python3.*")) / "site-packages"
MODULE = install_fake_dist(SITE)

d = B7ROOT / "case"
d.mkdir()

# --- positive (synthetic): both observations bind -> CHECKED --------------- #
c = run_b7(d, INTERP)
expect("b7 synthetic positive CHECKED", c["status"] == "CHECKED")
expect("b7 evidence binds the distribution identity",
       c["evidence"]["artifact"]["distribution"] == "warrant-verify==0.9.0")
expect("b7 evidence carries BOTH observations separately",
       c["evidence"]["stored_check"]["atp_spent"] == 2108
       and c["evidence"]["pack_replay"]["status_line"] == "REPLAY: LEGACY_UNPINNED")

# --- no environment named -> REFUSED, and never from PATH ------------------ #
c = run_b7(d, INTERP, set_env=False)
expect("b7 unbound env REFUSED WARRANT_ENV_NOT_PROVIDED",
       c["status"] == "REFUSED" and c["reason"] == "WARRANT_ENV_NOT_PROVIDED")

# --- an interpreter that is not one -> REFUSED ----------------------------- #
c = run_b7(d, B7ROOT / "no-such-python")
expect("b7 absent interpreter REFUSED WARRANT_ENV_UNUSABLE",
       c["reason"] == "WARRANT_ENV_UNUSABLE")

# --- wrong distribution name -> REFUSED ------------------------------------ #
c = run_b7(d, INTERP, distribution="warrant-verify-fork")
expect("b7 wrong distribution REFUSED WARRANT_DISTRIBUTION_ABSENT",
       c["reason"] == "WARRANT_DISTRIBUTION_ABSENT")

# --- wrong version -> REFUSED (0.8.0 installed, 0.9.0 demanded) ------------ #
install_fake_dist(SITE, version="0.8.0")
c = run_b7(d, INTERP)
expect("b7 wrong version REFUSED WARRANT_VERSION_MISMATCH",
       c["reason"] == "WARRANT_VERSION_MISMATCH"
       and c["evidence"]["observed"] == "0.8.0")
install_fake_dist(SITE)

# --- SHADOW artifact: same name, not the distribution's file --------------- #
shadow = B7ROOT / "shadow"
shadow.mkdir()
(shadow / "warrant.py").write_bytes((FAKE_WARRANT % B7_LINE).encode())   # byte-identical!
(SITE / "zz-shadow.pth").write_text(
    f"import sys; sys.path.insert(0, {str(shadow)!r})\n")
c = run_b7(d, INTERP)
expect("b7 shadow artifact REFUSED WARRANT_ARTIFACT_SHADOWED",
       c["reason"] == "WARRANT_ARTIFACT_SHADOWED")
(SITE / "zz-shadow.pth").unlink()

# --- artifact mutated in place (pin stale) -> REFUSED ---------------------- #
MODULE.write_bytes((FAKE_WARRANT % B7_LINE).encode() + b"# touched\n")
c = run_b7(d, INTERP)
expect("b7 mutated artifact REFUSED WARRANT_ARTIFACT_MISMATCH",
       c["reason"] == "WARRANT_ARTIFACT_MISMATCH")
install_fake_dist(SITE)

# --- RECORD disagrees with the installed bytes -> REFUSED ------------------ #
# A second, independent binding: what the wheel recorded vs what is on disk.
rec = next(SITE.glob("*.dist-info")) / "RECORD"
rec.write_text(rec.read_text().replace(
    rec.read_text().split(",")[1], "sha256=" + "A" * 43, 1))
c = run_b7(d, INTERP)
expect("b7 RECORD/disk disagreement REFUSED WARRANT_ARTIFACT_RECORD_MISMATCH",
       c["reason"] == "WARRANT_ARTIFACT_RECORD_MISMATCH")
install_fake_dist(SITE)

# --- output mutations: status, result, ATP each refuse SEPARATELY ---------- #
for label, line, reason in [
    ("status", f"fail  result={B7_RESULT}  atp_spent=2108",
     "STORED_CHECK_STATUS_MISMATCH"),
    ("result", "pass  result=" + "0" * 64 + "  atp_spent=2108",
     "STORED_CHECK_RESULT_MISMATCH"),
    ("atp", f"pass  result={B7_RESULT}  atp_spent=2109",
     "STORED_CHECK_ATP_MISMATCH"),
]:
    body = FAKE_WARRANT % line
    install_fake_dist(SITE, body=body)
    c = run_b7(d, INTERP, module_sha256=sha(body.encode()))
    expect(f"b7 output mutation ({label}) REFUSED {reason}", c["reason"] == reason)

# --- output SHAPE drift (an extra line, an unparseable line) --------------- #
for label, line in [("extra-line", B7_LINE + "\nand another thing"),
                    ("unparseable", "OK 2108 atp")]:
    body = FAKE_WARRANT % line
    install_fake_dist(SITE, body=body)
    c = run_b7(d, INTERP, module_sha256=sha(body.encode()))
    expect(f"b7 output drift ({label}) REFUSED STORED_CHECK_OUTPUT_DRIFT",
           c["reason"] == "STORED_CHECK_OUTPUT_DRIFT")

# --- the stored check itself failing to re-execute -------------------------- #
body = "import sys\nsys.exit(3)\n"
install_fake_dist(SITE, body=body)
c = run_b7(d, INTERP, module_sha256=sha(body.encode()))
expect("b7 non-executing check REFUSED STORED_CHECK_FAILED",
       c["reason"] == "STORED_CHECK_FAILED")
install_fake_dist(SITE)

# --- LOSS OF THE PACK-LEVEL REFUSAL: the decisive control ------------------ #
# The per-check pass is real and is still reported. It buys nothing: if the pack
# stops answering LEGACY_UNPINNED, B7 refuses.
for label, stub, args in [
    ("exit 0", "import sys\nprint('REPLAY: MATCH')\n", ["replay", "drafts/ssd-pack"]),
    ("another refusal", "import sys\nprint('REPLAY: DEPENDENCY_MISSING')\nsys.exit(1)\n",
     ["replay", "drafts/ssd-pack"]),
    ("status drift", "import sys\nprint('REPLAY: LEGACY_UNPINNED (probably)')\nsys.exit(1)\n",
     ["replay", "drafts/ssd-pack"]),
]:
    stub_path = B7ROOT / "stub_replay.py"
    stub_path.write_text(stub)
    c = run_b7(d, INTERP, pack_replay={
        "script": str(stub_path), "args": args,
        "expect_rc": 1, "expect_status_line": "REPLAY: LEGACY_UNPINNED"})
    expect(f"b7 pack no longer LEGACY_UNPINNED ({label}) REFUSED",
           c["status"] == "REFUSED" and c["reason"] == "PACK_NOT_LEGACY_UNPINNED")
    expect(f"b7 per-check pass is NOT credit for the pack ({label})",
           c["evidence"]["stored_check"]["atp_spent"] == 2108)

# --- the pack-level refusal is read from the REAL replay tool -------------- #
c = run_b7(d, INTERP)
expect("b7 real replay_pack.py answers LEGACY_UNPINNED at exit 1",
       c["evidence"]["pack_replay"]["rc"] == 1
       and c["evidence"]["pack_replay"]["status_line"] == "REPLAY: LEGACY_UNPINNED")

# --- no `which(name) + rc==0` path survives in the engine ------------------ #
expect("the generic `command` strategy is gone",
       "command" not in STRATEGIES)

shutil.rmtree(B7ROOT)

# --- OPT-IN: the real released artifact, in a clean environment ------------- #
# Not a fixture. Set MANIFESTO_WARRANT_PYTHON to a clean Python 3.12 that has
# `warrant-verify==0.9.0` installed (see DEPOSIT-AND-AUDIT §D).
_real = os.environ.get("MANIFESTO_WARRANT_PYTHON")
if _real:
    r = evaluate(HERE / "addressing-is-equality" / "claim-manifest.json")
    rc = status_of(r, "B7")
    expect("REAL warrant-verify==0.9.0 B7 CHECKED", rc["status"] == "CHECKED")
    expect("REAL B7 exact result + ATP",
           rc["status"] == "CHECKED"
           and rc["evidence"]["stored_check"]["result"] == B7_RESULT
           and rc["evidence"]["stored_check"]["atp_spent"] == 2108)
else:
    print("skip  REAL warrant-verify==0.9.0 positive "
          "(set MANIFESTO_WARRANT_PYTHON; see DEPOSIT-AND-AUDIT §D)")

print()
if fails:
    print(f"RED: {len(fails)} mechanism failure(s): {fails}")
    sys.exit(1)
print("GREEN: the deposit-check mechanism checks and fails-closed correctly.")
