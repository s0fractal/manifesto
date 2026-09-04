# Deposit & audit — Addressing Is Equality v0.2

Consolidates deliverables §7.3–§7.8. Nothing here deposits, tags, licenses, or reserves a DOI.

## A. Checker — IMPLEMENTED as a closed-manifest deposit gate (Codex P0-S2 / P0-4 closed)

**Status (2026-09-01).** Built: `papers/deposit_check.py` + `papers/addressing-is-equality/claim-manifest.json`,
mechanism/mutation tests in `papers/test_deposit_check.py`. The old `check_claims.py` is now a
deprecation shim to the gate (it no longer reads `manifest.json` for the Warrant ATP, and no longer
depends on an absolute author-machine ADR path). **Current deposit report (BLOCKED, exit 1):**
`B1` **CHECKED** (glyphlib replay — 601 / 19,997 / 260,780 ATP, each bound to a term/AST hash + the
`glyphlib` digest + normal-form addresses); `B3`, `B6` **CHECKED** (`aie_errata_check.py` executed,
exit 0); `B2` **EXCLUDED: DERIVED_FROM_B1**; `B5` **EXCLUDED: ARGUED_OBLIGATION**; `B8` **EXCLUDED:
DEFINITIONAL**; `B4` **REFUSED: PROFILE_NOT_VENDORED** (church@v0 @196c45a is not vendored);
`B7` **REFUSED: WARRANT_ENV_NOT_PROVIDED** (no interpreter named — see below). Vendoring the DRAFT
profile flips B4 to CHECKED. The design the gate implements:

**The current checkers pass but decide much less than their banners claim.** `check_claims.py`
verifies the two Warrant ATP values by **reading `manifest.json`** — it does not execute the check,
yet the paper says "re-executes". The ADR-011 check is an **absolute, author-machine path**
(`/Users/s0fractal/Projects/sigma-glyph/proposals/ADR-011-…md`): a stranger's clean checkout cannot
satisfy it, and mere file existence establishes neither the proposal's digest, status, nor
implementation. The final banner says it matches `paper.md`, though the reviewed surface is the
unpromoted v0.2 file.

**Do not implement the old gap-list verbatim (Codex).** Replace the checkers so they *decide this
ledger*:

1. **Closed manifest → checks.** Compile `CLAIM-LEDGER.md` (B1–B8) into checks; bind every checked
   number to a claim ID, the exact executed **term/AST hash**, and its surface (permissive harness
   vs `church@v0` DRAFT). Emit exact `checked`, `excluded`, and `refused` sets. Profile-label every
   printed number so no permissive figure can be read as a `church@v0` fact.
2. **Execute, don't read — and bind the artifact first (B7, CLOSED).** The old `command` strategy
   awarded B7 for `which("warrant")` plus exit 0; it is **removed from the engine**, and no
   name-on-PATH path can award B7 again. `warrant_conformance` instead:
   (a) takes the interpreter from **`MANIFESTO_WARRANT_PYTHON`**, never from PATH — unset is
   `REFUSED: WARRANT_ENV_NOT_PROVIDED`, which is why the default report above still blocks;
   (b) reads that interpreter's own installed metadata and requires distribution
   **`warrant-verify==0.9.0`**, with the module actually imported owned by that distribution and at
   the pinned digest `0e6785679aa7b8133fc798794c8f72eb37bc3874b93cb494eadbd41f189d204a` (the
   `warrant.py` inside `warrant_verify-0.9.0-py3-none-any.whl`, sha256 `62c57f62…`) — a shadow
   module, a source checkout, another distribution or another version refuses **before** any output
   is read as evidence;
   (c) runs `-I -m warrant --store .warrants check 0597575d…` under the bound interpreter and parses
   the exact machine line, comparing **status**, **result hash** and **ATP** independently
   (`pass` / `e0419cc5…` / `2108`), each with its own typed refusal;
   (d) runs `python tools/replay_pack.py replay drafts/ssd-pack` **separately** and requires exactly
   `REPLAY: LEGACY_UNPINNED` at exit 1. Exit 0, another refusal, or output drift is
   `PACK_NOT_LEGACY_UNPINNED` and refuses B7 — the per-check pass is reported and buys nothing.
   Neither observation is ever credit for the other.
3. **Pin the DRAFT profile by content, not by path.** Vendor the ADR-011 reference implementation at
   commit `196c45a2…` into the deposit and verify it by content digest; a missing/re-pathed proposal
   is a **typed refusal** (`PROFILE_NOT_VENDORED`), never a string-presence pass. Split the evaluator
   wheel (`0.6.7`) from the unreleased profile in the environment record.
4. **`church@v0` admission fixtures.** Check that the vendored profile (a) admits written numerals
   0–8 and (b) **refuses `PLUS 7 5`** and marker-naming terms — the admission gap as a machine fact.
5. **Collision counterexample first-class.** Run the `aie_errata_check.py` marker collision (PASS,
   `8785b7dd…`) with M1(REFUSED)/M2(VIOLATION)/M3 as deposit-path checks equal in standing to the
   cost numbers.
6. **Measured-vs-fitted.** Print the raw points behind ≈50 / ≈37 ATP/unit; label the slope
   observed-over-range, never a fitted general law.
7. **Deposit gate invokes the v0.2 artifact**, not `paper.md`; and treats the historically-sealed
   SSD pack (errata E2: committed `refuted:0` vs re-run `refuted:3`, Σ stable 5,638 ATP) as archived,
   not regenerable.

## B. Bibliography audit

**Status (updated over the Kimi commit, Codex P1-3).** §6 now carries **four** `[@key]` markers —
`@ershov1958`, `@filliatre2006`, `@berger1991`, `@merkle1987`; a matching `references.bib` and
`--citeproc` resolution are still owed, and the deployed-systems rows (Dhall/Unison/Nix/IPLD, EVM) are
cited by name/URL in `novelty-search-log.md`, not yet as bib keys. (Paper A's body still has **no**
`[@key]`; the two papers differ here.) Each source is scoped to the *exact adjacent relation* it
supports:

| key | supports (exact relation) | over-reach to avoid | verdict |
|---|---|---|---|
| `ershov1958` | hash-consing origin (structural sharing) | not semantic equality of computed values | keep, scoped |
| `filliatre2006` | type-safe hash-consing / structural equality — "identical structure ⇒ shared address" | not the content-addressed *result-identity* claim | keep — the right authority for the address-sharing mechanism |
| `berger1991` | NbE for the typed λ-calculus (evaluation + readback) | does **not** establish this exact untyped Church-numeral `O(n)=nFX` probe is "the" NbE trick — that analogy is ours, flagged | keep, scoped |
| `merkle1987` | hash-tree lineage (a digital-signature construction) | **not** a direct authority for content-addressed result-identity as phrased | keep, lineage-only |
| `sigma-glyph` | the reference SKI machine / evaluator (`0.6.7`) | not the DRAFT profile (separate, unreleased, @196c45a) | keep |
| `warrant` | the conformance use case | conformance only, never validation of the semantic claim, never strict pack replay | keep, scoped |
| `luu2015demystifying`, `cacm-verification-debt`, `garrabrant2016`, `irving2018debate`, `christiano2018amplification`, `barendregt2005challenge` | — not cited in this paper's body | — | **drop** unless a sentence cites them (inherited from the companion paper) |

**Novelty search log (required, Codex P1-B5; systems from Fable 2026-09-01 §2.7).** Novelty is
**OPEN** until external prior-art review. Deposit must include a dated search log covering, at
minimum, and recording for each the exact relation it does/does not pre-empt:

- hash-consing / structural sharing (Ershov, Filliâtre–Conchon);
- **NbE freshness / readback side-conditions** — the §3.1 marker collision *is* this condition (de
  Bruijn levels, gensym), so it is prior art on the counterexample, not on the idiom;
- **content-addressed identity in deployed systems** — **Dhall** semantic-integrity hash (hash of the
  normalized expression — the idiom at the language level), **Unison** (content hash = definition
  identity), **Nix** derivation hashes, **IPLD**;
- budgeted/priced/receipted equality settlement (the only place the surviving sliver can live).

After that prior art the candidate is **"priced settlement with a receipt"**, not "addressing is
identity". The two-sided composition whose novelty is asked for must be vendored (the ADR-011 impl
@196c45a) or the novelty narrowed to a specification pattern not yet demonstrated end-to-end.

## C. Sentences depending on transcript-only / external-live / unverified evidence

- **All ATP figures** are `replay` (byte-identical evaluator replay under a pinned sigma-glyph),
  *not* transcript — safe to present as reproducible, **provided the profile label is attached.**
- **The Warrant credit is two different things (Codex P1-S1).** Under the bound
  `warrant-verify==0.9.0`, `check 0597575d…` re-executes one stored SKI check to `pass`,
  result `e0419cc5…`, `atp_spent=2108`. But `python tools/replay_pack.py replay drafts/ssd-pack`
  returns `LEGACY_UNPINNED` (exit 1): the pack as a whole is historically sealed. The gate requires
  **both** and spends neither as credit for the other. A one-sided check against a constant is not a
  two-sided equality receipt or endorsement. `warrant verify --settlement` (4 records, 0/0) is a
  third, **unbound** observation: it was dropped from the B7 row rather than reported as checked.
- **The `church@v0` per-unit ≈37 ATP figure** (DRAFT profile @196c45a, admitted numerals only — not
  the computed `7+5`) and the permissive ≈50 are `replay` over a measured range — label
  observed-over-range, not extrapolated, and never present `church@v0` as released.
- **External citation details** (Ershov/Filliâtre/Merkle/Berger) are `unverified by the checker` —
  human bibliography audit only (§B).
- **The `no second implementation exists` / portable-settlement-BLOCKED** claim is a stated
  limitation, not a measured negative; keep it as such.

## D. Clean-environment reproduction

```sh
python3 -m venv .venv
.venv/bin/pip install "sigma-glyph==0.6.7"
# idiom vs predicate costs, marker collision, mutations, Warrant pack:
.venv/bin/python papers/addressing-is-equality/check_claims.py     # after §A closed-manifest rewrite
.venv/bin/python tools/aie_errata_check.py                          # collision counterexample + M1/M2/M3
# per-check re-execution vs pack-level replay — the gate runs BOTH and reports them separately.
# B7 needs a clean interpreter that has the RELEASED distribution; it is named, never found on PATH,
# and nothing about it is committed (no venv, wheel, report or cache):
mise exec python@3.12 -- python -m venv /tmp/warrant-0.9.0
/tmp/warrant-0.9.0/bin/pip install "warrant-verify==0.9.0"
MANIFESTO_WARRANT_PYTHON=/tmp/warrant-0.9.0/bin/python \
  python3 papers/deposit_check.py papers/addressing-is-equality/claim-manifest.json   # B7 CHECKED
# what that binds, directly:
#   (cd drafts/ssd-pack && /tmp/warrant-0.9.0/bin/python -I -m warrant --store .warrants \
#      check 0597575d21d62c2db265c0d17e3a2c8c1b2db880342b117a403af7e9c4c03c87)
#     -> pass  result=e0419cc5112a95f9e35a019539b25f00eccbea33122a5736a20897d8eea5bf00  atp_spent=2108
#   python3 tools/replay_pack.py replay drafts/ssd-pack
#     -> REPLAY: LEGACY_UNPINNED (exit 1) — the expected typed boundary, NOT a failure of the run
# mechanism (hermetic; builds a synthetic distribution, touches no network and no PATH):
python3 papers/test_deposit_check.py
# and the same suite with the REAL artifact bound, which then asserts the real positive too:
MANIFESTO_WARRANT_PYTHON=/tmp/warrant-0.9.0/bin/python python3 papers/test_deposit_check.py
# DRAFT profile (NOT in the 0.6.7 wheel): vendor & pin by content, then exercise admission:
#   sigma-glyph @ 196c45a2f9074a472b96af1a6bae2c67533edbb1 (v0.6.7-175-g196c45a) ADR-011 selftest → 72/72
# record: exact repo revision; sigma-glyph release (0.6.7) SEPARATE from the DRAFT profile commit;
#         interpreter (CPython 3.12/3.14 only verified)
```

**Byte reproducibility is claimed for the evaluator replay (ATP, addresses) under a pinned
sigma-glyph, on CPython 3.12/3.14. It is NOT claimed across implementations — no second
implementation exists, and portable settlement is BLOCKED.**

## E. Deposit manifest proposal (not a deposit)

```yaml
paper: addressing-is-equality/paper-v0.2-draft.md    # promote to paper.md only on operator decision
revision: <GIT_REVISION_PLACEHOLDER>
evaluator: sigma-glyph==0.6.7
included:
  - LICENSE                                             # path-scoped license authority
  - LICENSES/AGPL-3.0-only.txt                          # executable deposit material
  - LICENSES/CC-BY-SA-4.0.txt                           # paper and documentary artifacts
  - papers/addressing-is-equality/paper-v0.2-draft.md
  - papers/addressing-is-equality/CLAIM-LEDGER.md
  - papers/addressing-is-equality/check_claims.py       # after §A additions
  - drafts/ADDRESSING-IS-EQUALITY.md                     # design doc
  - drafts/ADDRESSING-IS-EQUALITY.errata.md              # errata (history)
  - tools/aie_errata_check.py                            # collision counterexample + mutations
  - drafts/ssd-pack/                                     # Warrant pack (conformance only; LEGACY_UNPINNED)
  - vendored/adr-011@196c45a/                             # DRAFT profile impl + its upstream license,
                                                          #   pinned by content digest (NOT the 0.6.7 wheel)
  - papers/addressing-is-equality/novelty-search-log.md  # dated prior-art search (novelty is OPEN)
profile_implementation:                                   # kept SEPARATE from `evaluator` above
  source: sigma-glyph @ 196c45a2f9074a472b96af1a6bae2c67533edbb1  # v0.6.7-175-g196c45a, DRAFT, unreleased
  status: DRAFT — non-normative, not gated, not adopted, BLOCKED on PLUS 7 5
expected_checks:
  - build takes paper-v0.2-draft.md (NOT paper.md); abstract front-loaded; real [@key] citations resolve
  - check_claims.py exits 0 on a clean sigma-glyph==0.6.7 install, every figure bound to a term hash and surface
  - aie_errata_check.py settles the collision PASS and flips under M1/M2/M3
  - B7: under a bound warrant-verify==0.9.0 the stored check re-executes to pass / e0419cc5… /
    2108 ATP AND replay_pack separately reports LEGACY_UNPINNED (both required, neither credit
    for the other); an unnamed or unbound environment is REFUSED, never CHECKED
  - the vendored DRAFT profile admits numerals 0–8 and refuses PLUS 7 5
excluded:
  - any DOI reservation, release, tag, or claim of adoption / peer review
  - any presentation of 601 ATP as a church@v0 fact, or of church@v0 as a "released profile"
  - any presentation of the Warrant pass — or a strict pack replay — as a proof of the semantic theorem
status_note: >
  ADR-011 is a DRAFT proposal on file upstream, not accepted/deployed/standardized, and BLOCKED on
  the motivating case. Publication is a dated trajectory marker, not adoption. This paper is its own
  version series; the software/protocol snapshot is a separate artifact even at the same revision.
```

## G. Build surface & metadata (Codex P1-S4 — currently wrong)

- `build.sh` builds `paper.md`, not `paper-v0.2-draft.md`; the candidate build must take the exact
  reviewed draft (or promote first) and hash the *generated* paper plus every included artifact.
- The abstract is now **front-loaded** in the v0.2 draft.
- The v0.2 body's §6 must carry real `[@key]` markers or `--citeproc` resolves nothing while the
  bibliography audit's "in-text" column is false.
- Author, exact date, keywords, artifact revision, evaluator (`0.6.7`) **and** the DRAFT profile
  commit (`196c45a`) are front-matter fields; profile commit is separate from evaluator version.

## F. Acceptance-gate self-check (brief §8) — truthful status, not blanket "yes" (Codex P1-3/P0-4)

| gate | status | note |
|---|---|---|
| every abstract claim is a ledger row | **yes** | B1–B8 |
| no historical false claim outside history/counterexample | **yes** | unconditional soundness / bare 601 ATP / "released profile" / `ISZERO∘SUB` removed; typed blocklist; errata in §8 |
| assumptions adjacent | **yes** | §3 boundary; §4 contract stated as argued obligations |
| every number replayed or classified | **yes (implemented)** | the gate re-executes B1 and **binds each figure to a term/AST hash** + evaluator digest + normal-form addresses; B3/B6 execute `aie_errata_check.py`; nothing is string-presence |
| positive and negative fixtures both exercised | **yes** | cost matrix (B1) + marker collision + M1/M2/M3 + admission refusal (B3/B6 executed by the gate) |
| candidate paper bound to the checker | **yes (implemented)** | `deposit_check.py` binds the candidate by digest and the closed B1–B8 set; deleting/mutating the draft or a claim ID → `FAIL_CLOSED` exit 3 (Codex P0-4 closed) |
| DRAFT profile vendored + admission fixtures | **BLOCKED** | the gate REFUSES B4 as `PROFILE_NOT_VENDORED`; `church@v0` @196c45a must be vendored/pinned with admission/refusal fixtures |
| current/legacy and permissive/DRAFT-profile not conflated | **yes** | surface label throughout; evaluator wheel split from profile commit |
| CI/replay/review/publication/adoption distinct | **yes** | §0; §7 two Warrant credits; §8 |
| "what would weaken the central claim" | **yes** | §9 typed falsifiers |
| license scope + missing external validation visible | **yes** | §6, §9, §B, §E |
| no document-level green inferred from local green | **N/A** | single settlement method; checker rebuild pending (§A) so local green no longer borrows the "re-executes / released-profile" claim |

## H. Zenodo mechanics & record genre (operator decisions; from Fable review 2026-09-01 §2.8/§3)

Cross-paper Zenodo mechanics (**mixed-license uploads are supported — two linked records are a policy
choice, not a Zenodo requirement**; v0.2 as first version; author = accountable human + ORCID; ship
`reviews/` + `reviews/prompts/`; the build now refuses the SUPERSEDED source; stale `.html`) are
recorded once in the **flagship** `every-check-spawns-more/DEPOSIT-AND-AUDIT.md §H–§I`; they apply here
identically.

**Record genre for this paper.** Because no deposited implementation both admits the motivating case
and emits the two-sided receipt (the paper's own central finding), this belongs as
`upload_type: publication / technicalnote` — an **incident-and-repair note** — or as an appendix to
Paper A, **not** as a "paper" that would lead a reader to expect a realized method. **Review
provenance (updated over the Kimi commit):** Codex (OpenAI) and Kimi (Moonshot) are **out-of-lineage**;
Fable is **same-lineage** (within-lineage replication). "Two model readings, one out-of-lineage" —
never "two independent reviewers". A **human** prior-art / adversarial review is still owed.
