# embedded-claims PoC — phase 1 (rev 3) + phase 2 step 1

A working core for the embedded-claims design
([ARCHITECTURE-0.1](../EMBEDDED-CLAIMS-ARCHITECTURE-0.1.md) +
[REVIEW-0.1](../EMBEDDED-CLAIMS-REVIEW-0.1.md)). Working-core-first, not a full
ontology: it exercises the accepted review deltas on real fixtures and stops.

**Status:** phase-1 PoC (rev 3, after two Codex review passes) plus phase-2 step 1
(closed canonicalization + closed capsule schema). Rev 2 closed two P0 identity
bugs; rev 3 closed a third P0 (world claims must pin their dependency) plus
verifier-closure, effect-digest, and result-identity findings; phase-2 step 1 adds
fail-closed capsule parsing and pinned record identities. NOT a spec, NOT a
conformance certificate, NOT a claim of full closure. Passing fixtures show the
deltas behave as intended on these cases — nothing more.

## What it demonstrates

A fixture is Markdown with one inline claim `⟦class: payload⟧` and an optional
fenced ` ```json capsule ` of AUTHOR ASSERTIONS: the pinned verifier, a dependency
for freshness, the `evaluation_id` the author bets on, a semantic binding. Assertions
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

**Phase 2 step 1 (canonicalization + closed schema).** The capsule is parsed by
`canonical.loads_strict` (duplicate keys rejected) and validated against a **closed
schema** (`schema.py`, `additionalProperties: false`): an unknown field or bad shape
is `CAPSULE_INVALID` and fails closed. `canonical.py` pins the §17 decisions —
a closed custom JSON profile (sorted keys, `(",",":")`, UTF-8, no floats/dup-keys),
SHA-256, domain-separated record IDs (§8.1). JCS/RFC 8785 stays a later, reversible
choice; not adopted. Both modules are stdlib-only, so the CI gate needs no package
beyond the evaluator.

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
../../.venv/bin/python test_poc.py                       # 22 fixtures + 5 invariants
../../.venv/bin/python verify.py fixtures/valid/arith-self.md   # one fixture, human report
```

**Pivot (step 3b):** the canonical pipeline is **capsule-only** — the parser grants
machine credit only to an explicit `json capsule` inside a live region, and the capsule
CONTAINS its claim. The inline `⟦…⟧` form above (`verify.py`, the 22 fixtures) is now
LEGACY authoring / the settlement core, not the canonical extraction path; it is not
auto-migrated. See `PARSER-THREAT-MODEL.md` and `fixtures/adversarial/EXPECTED.md`.

The PARSE layer (step 3b) needs pinned Markdown deps (this ends the stdlib-only
property, deliberately, for the parser):

```sh
.venv/bin/pip install --require-hashes -r drafts/embedded-claims-poc/requirements-parser.lock
../../.venv/bin/python test_parser.py     # 13 PARSE specimens (capsule-only) over fixtures/adversarial/
../../.venv/bin/python parser.py fixtures/adversarial/02-multiple-claims.md   # one file
```

`test_poc.py` exits 0 iff every fixture lands on its exact `(execution, binding)`
and required facts, AND five invariants hold: identity does not alias
(world-same-input), the report is byte-deterministic across runs, the body
commitment detects field mutation, the effect path is Sigma-independent (runs under
`python -S`), and canonicalization rejects floats/dup-keys/surrogates/big-ints.

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
- **Canonicalization + hash pinned (phase 2 step 1); full parser still pending.**
  `canonical.py` fixes the closed JSON profile and SHA-256 domain-separated record
  IDs (§17 #1/#2); the info-string stays `json capsule` (#4). What remains: a
  general Markdown parser that finds capsules structurally (not by regex), the
  capsule→records compiler, and conformance vectors. Record shapes are stabilizing
  but not frozen.
- **Verifier closure is code, not environment.** The identities digest the `.py`
  files that determine a verdict — the verdict core (`settle_core.py`),
  `canonical.py`, `schema.py`, gate, glyphlib, resolver (`sigma_boundary.py`), and
  evaluator. `verify.py` (CLI + renderer) is deliberately **out** of the closure, so
  editing a docstring or a print never rotates a verifier id. The closure omits the
  interpreter build,
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
verify.py       CLI + renderer (OUT of the verifier closure)
settle_core.py  the verdict core: parse/schema/dispatch/identities/facts (IN closure)
                + freshness + binding clamp + D6 effect (observed post-state)
canonical.py    closed JSON canonicalization + domain-separated record IDs (§17 #1/#2)
schema.py       closed capsule schema (additionalProperties:false), stdlib-only
parser.py       PARSE layer (step 3b): pinned CommonMark + protocol profile over raw spans
requirements-parser.lock   hash-locked markdown-it-py==4.2.0 + mdurl==0.1.2
test_poc.py     22 fixtures + 6 invariants (aliasing, determinism, mutation, -S, canonical)
test_parser.py  13 PARSE specimens + 4 invariants (capsule-only: status, capsule count/local_id/span)
fixtures/valid/     arith-self, repo-count, world-claim-a, world-claim-b
fixtures/invalid/   expected-mismatch, stale-dependency, world-missing-dep,
                    world-path-mismatch, wrong-verifier, missing-verifier,
                    wrong-binding, self-declared-reviewed, mismatch-result-address,
                    combined-verifier-stale-mismatch, stdout-same-effect-different,
                    effect-short-digest, capsule-unknown-field, capsule-dup-key,
                    capsule-malformed-json, capsule-bad-binding-type, capsule-lone-surrogate
fixtures/limits/    effect-invisible-effect   (a demonstrated blind spot)
```
