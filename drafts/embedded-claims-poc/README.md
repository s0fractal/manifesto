# embedded-claims PoC — phase 1 (rev 3)

A working core for the embedded-claims design
([ARCHITECTURE-0.1](../EMBEDDED-CLAIMS-ARCHITECTURE-0.1.md) +
[REVIEW-0.1](../EMBEDDED-CLAIMS-REVIEW-0.1.md)). Working-core-first, not a full
ontology: it exercises the accepted review deltas on real fixtures and stops.

**Status:** phase-1 PoC, rev 3 after two Codex review passes. Rev 2 closed two P0
identity bugs; rev 3 closes a third P0 (world claims must pin their dependency)
plus verifier-closure, effect-digest, and result-identity findings. NOT a spec,
NOT a conformance certificate, NOT a claim of full closure. Passing fixtures show
the deltas behave as intended on these cases — nothing more.

## What it demonstrates

A fixture is Markdown with one inline claim `⟦class: payload⟧` and an optional
fenced ` ```json capsule ` of AUTHOR ASSERTIONS: the pinned verifier, a dependency
for freshness, the `result_id` the author bets on, a semantic binding. Assertions
are **claims, not verdicts**. `verify.py` recomputes and reports on two axes:

```
execution ∈ {REPLAYED, MISMATCH, STALE, UNVERIFIED, DECLARED}
binding   ∈ {UNTIED, ASSERTED}          (REVIEWED/CONTESTED need a review record)
```

Execution is a **summary over independent facts** (`execution_facts`), so several
faults at once are all visible, not hidden by which check fired first:

```
VERIFIER_MISSING · VERIFIER_MISMATCH
DEPENDENCY_MISSING · DEPENDENCY_PATH_MISMATCH · DEPENDENCY_STALE
RESULT_MATCH · RESULT_MISMATCH · RESULT_UNSETTLED · ADDRESS_MISMATCH
```

Identity is split so no field carries two meanings: `claim_id` (predicate),
`plan_id` (claim+verifier), `dependency_id` (world bytes read — freshness, not an
address), `result_value_id` (the canonical result value), and `evaluation_id`
(claim-bound: claim+plan+dependency+value+verdict — the address the author pins).

`verify.py` is a thin layer over the existing engine (`tools/settle_gate.py`,
`glyphlib.py`, and the real Σ-GLYPH runtime) — no new runtime.

| Δ / property | what | fixture |
|---|---|---|
| D1 | self-contained inline claim, address = result_id, **no CAS** | `valid/arith-self.md` |
| D2 | execution never upgrades binding | `invalid/wrong-binding.md` |
| D3 / P0-1 | verifier identity is a **per-class code closure** (dispatch + resolver included); missing OR wrong pin ⇒ no replay credit | `invalid/missing-verifier.md`, `invalid/wrong-verifier.md` |
| P0 (rev 3) | world classes **require** an exact `path`+`digest` dependency pin; missing/wrong path ⇒ no replay credit | `invalid/world-missing-dep.md`, `invalid/world-path-mismatch.md` |
| P0-2 / P2 | input digest is `dependency_id`, not an address; `result_value_id` (value) and `evaluation_id` (claim-bound) are separate; distinct predicates get distinct `claim_id`/`evaluation_id` | `valid/world-claim-a.md` + `-b.md` |
| P1-4 | raw capsule may only `ASSERTED`; self-declared `REVIEWED` is clamped | `invalid/self-declared-reviewed.md` |
| P1-4 | independent facts, nothing hidden by if-order | `invalid/combined-verifier-stale-mismatch.md` |
| P2-6 | false claim cannot borrow a true claim's address (evaluation_id binds verdict + both normal forms via result_value_id) | `invalid/mismatch-result-address.md` |
| D6 | effects settle on observed post-state, not stdout | `invalid/stdout-same-effect-different.md` |
| P1-5 | …and post-state observation is NOT enforcement (blind spot) | `limits/effect-invisible-effect.md` |
| freshness | pinned dependency changed ⇒ STALE, never silent green | `invalid/stale-dependency.md` |
| — | false claim caught (raw→MISMATCH) | `invalid/expected-mismatch.md` |
| — | world claim + semantic binding, replayable | `valid/repo-count.md` |

## Run

The Σ-GLYPH runtime is consumed as a **version-pinned released package**. The
fixture verifier-identities are a code closure that includes the evaluator's
bytes, so they are pinned against `sigma-glyph==0.6.7` — the same version the CI
gate (`.github/workflows/embedded-claims-poc.yml`) installs. One-time setup (the
venv is gitignored):

```sh
# from the manifesto repo root
python3 -m venv .venv
.venv/bin/pip install "sigma-glyph==0.6.7"          # the pinned, reproducible evaluator
```

Bumping Sigma is deliberate: a different evaluator changes the closure digest, so
the glyph/settle-gate fixtures go UNVERIFIED until the pins are recomputed. That
is the closure discipline working, not a flake. Verifier ids are **path-independent**
(the closure is sorted by content digest, not by file path), so any 0.6.7 install
— any venv, any machine, CI — reproduces the same ids.

Then:

```sh
cd drafts/embedded-claims-poc
../../.venv/bin/python test_poc.py                       # 17 fixtures + 4 invariants
../../.venv/bin/python verify.py fixtures/valid/arith-self.md   # one fixture, human report
```

`test_poc.py` exits 0 iff every fixture lands on its exact `(execution, binding)`
and required facts, AND three invariants hold: identity does not alias
(world-same-input), the report is byte-deterministic across runs, and the body
commitment detects field mutation.

## What actually stood up (verified)

- Σ-GLYPH really reduces `74+1=75 → e0419…`; the self-contained address recomputes.
- A stale dependency is never silently green.
- A correct execution does not upgrade a wrong binding.
- The post-state fixture shows convincingly why stdout is insufficient.
- Distinct predicates over one file no longer alias to one address.
- Reports are byte-deterministic; the commitment catches mutation.

## What this PoC does NOT establish (honest boundary)

- **`REPORT`, not a receipt.** The printout carries a body commitment (mutation is
  detectable), but there is no replay-verifier, no committed capsule bytes, no
  gate/profile version binding. It is called `REPORT` on purpose.
- **Effects are OBSERVED, not enforced (P1-5).** A `TemporaryDirectory` is not a
  sandbox. `limits/effect-invisible-effect.md` settles REPLAYED despite a real
  write-then-delete side effect, because nothing survives in the observed tree —
  and writes outside the dir, network calls, and metadata changes are equally
  invisible. The credit is "observed post-state differs", never "effects enforced".
- **No canonicalization / hash / info-string pinned** (§17 #1/#2/#4). Phase 1 uses
  the runtime's native hashing and hand-written capsules. A general Markdown
  parser + closed schema + canonical record IDs is phase 2, and every `record_id`
  depends on those three decisions — the current shapes are NOT stable.
- **Verifier closure is code, not environment.** The identities digest the `.py`
  files on the settlement path — dispatch/renderer (`verify.py`), gate, glyphlib,
  resolver (`sigma_boundary.py`), and evaluator — but NOT the interpreter build,
  OS, or editable-package/import state. That closure is deliberately open, and the
  identity claim is scoped to code accordingly. The engine is **lazy-loaded**: the
  effect path imports neither `settle_gate` nor Sigma (`effect-sandbox://` runs
  under `python -S` with no Sigma package — a suite invariant); every non-effect
  class shares one bootstrap import, and its whole closure is bound into the ID.
- **Effect address is display-strict but not enforced.** An identity-bearing
  effect commitment now requires a full 64-hex digest (an 8-hex prefix no longer
  earns credit), but see the enforcement limit above.
- **Semantic adequacy is open.** REPLAYED establishes only the content-address,
  never that the claim supports the prose. `binding` stays separate by construction.
- **Not a distributed-trust system.** Single operator, deterministic runtimes.
- **Does not certify its own design.** These fixtures are not independent validation.

## Files

```
verify.py       thin verifier: 2 axes + facts + identity block + verifier closure
                + freshness + binding clamp + D6 effect (observed post-state)
test_poc.py     16 fixtures + 3 invariants (aliasing, determinism, mutation)
fixtures/valid/     arith-self, repo-count, world-claim-a, world-claim-b
fixtures/invalid/   expected-mismatch, stale-dependency, world-missing-dep,
                    world-path-mismatch, wrong-verifier, missing-verifier,
                    wrong-binding, self-declared-reviewed, mismatch-result-address,
                    combined-verifier-stale-mismatch, stdout-same-effect-different,
                    effect-short-digest
fixtures/limits/    effect-invisible-effect   (a demonstrated blind spot)
```
