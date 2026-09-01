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

print()
if fails:
    print(f"RED: {len(fails)} mechanism failure(s): {fails}")
    sys.exit(1)
print("GREEN: the deposit-check mechanism checks and fails-closed correctly.")
