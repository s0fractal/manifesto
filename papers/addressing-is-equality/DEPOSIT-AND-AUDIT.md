# Deposit & audit — Addressing Is Equality v0.2

Consolidates deliverables §7.3–§7.8. Nothing here deposits, tags, licenses, or reserves a DOI.

## A. The checkers are STALE-GREEN / machine-bound; replace them (Codex P0-S2)

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
2. **Execute, don't read.** The Warrant credit must come from actually running
   `warrant check 0597575d…` (PASS 2,108 ATP) — not from parsing `manifest.json` — and must also run
   `python tools/replay_pack.py replay drafts/ssd-pack` and report the `LEGACY_UNPINNED` pack status
   as a **typed** result beside the per-check PASS.
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

**None of these keys is connected to the v0.2 body through a Pandoc citation today (Codex P1-S4/B5).**
The `[@key]` markers in §6 must be added before any "in-text: yes" is true and before `--citeproc`
resolves anything. Each source is scoped to the *exact adjacent relation* it actually supports:

| key | supports (exact relation) | over-reach to avoid | verdict |
|---|---|---|---|
| `ershov1958` | hash-consing origin (structural sharing) | not semantic equality of computed values | keep, scoped |
| `filliatre2006` | type-safe hash-consing / structural equality — "identical structure ⇒ shared address" | not the content-addressed *result-identity* claim | keep — the right authority for the address-sharing mechanism |
| `berger1991` | NbE for the typed λ-calculus (evaluation + readback) | does **not** establish this exact untyped Church-numeral `O(n)=nFX` probe is "the" NbE trick — that analogy is ours, flagged | keep, scoped |
| `merkle1987` | hash-tree lineage (a digital-signature construction) | **not** a direct authority for content-addressed result-identity as phrased | keep, lineage-only |
| `sigma-glyph` | the reference SKI machine / evaluator (`0.6.7`) | not the DRAFT profile (separate, unreleased, @196c45a) | keep |
| `warrant` | the conformance use case | conformance only, never validation of the semantic claim, never strict pack replay | keep, scoped |
| `luu2015demystifying`, `cacm-verification-debt`, `garrabrant2016`, `irving2018debate`, `christiano2018amplification`, `barendregt2005challenge` | — not cited in this paper's body | — | **drop** unless a sentence cites them (inherited from the companion paper) |

**Novelty search log (required, Codex P1-B5).** Novelty is **OPEN** until external prior-art review.
Deposit must include a dated search log covering hash-consing, content-addressed evaluation/result
identity, NbE observation probes, and budgeted/receipted equality settlement, recording queries,
sources examined, and the exact relation each does/does not pre-empt. The two-sided composition whose
novelty is asked for must be vendored (the ADR-011 impl @196c45a) or the novelty narrowed to a
specification pattern not yet demonstrated end-to-end.

## C. Sentences depending on transcript-only / external-live / unverified evidence

- **All ATP figures** are `replay` (byte-identical evaluator replay under a pinned sigma-glyph),
  *not* transcript — safe to present as reproducible, **provided the profile label is attached.**
- **The Warrant credit is two different things (Codex P1-S1).** `warrant check 0597575d…` re-executes
  one stored SKI check to PASS at 2,108 ATP (`command`); `warrant verify --settlement` reports 4
  records, 0/0. But `python tools/replay_pack.py replay drafts/ssd-pack` returns `LEGACY_UNPINNED`
  (exit 1): the pack as a whole is historically sealed. Report both; neither cancels the other. A
  one-sided check against a constant is not a two-sided equality receipt or endorsement.
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
# per-check re-execution vs pack-level replay (report BOTH):
warrant check 0597575d...                                           # PASS, 2,108 ATP
python tools/replay_pack.py replay drafts/ssd-pack                  # REPLAY: LEGACY_UNPINNED (exit 1) — expected
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
  - warrant check re-executes to PASS 2,108 ATP AND replay_pack reports LEGACY_UNPINNED (both recorded)
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

## F. Acceptance-gate self-check (brief §8)

- every abstract claim is a ledger row — **yes** (B1–B8);
- no historical false claim outside history/counterexample — **unconditional soundness / bare 601 ATP
  / "released profile" / `ISZERO∘SUB` all removed**; errata trajectory in §8;
- assumptions adjacent — **yes** (§3 boundary, §4 contract stated as argued obligations);
- every number replayed or classified — **yes** (§C; ATP replay, surface-labeled, bound to term hash);
- positive and negative fixtures both exercised — **yes** (cost matrix + collision counterexample +
  mutations + admission refusal of `PLUS 7 5`);
- current/legacy and permissive/DRAFT-profile not conflated — **yes** (surface label throughout;
  evaluator wheel split from profile commit);
- CI/replay/review/publication/adoption distinct — **yes** (§0, §7 two Warrant credits, §8);
- one-paragraph "what would weaken the central claim" — **yes** (§9 typed falsifiers; only
  `integrity_break`/`within-sample_counterexample` falsify);
- license scope + missing external validation (no second implementation; novelty OPEN) visible —
  **yes** (§6, §9, §B search log, §E);
- no document-level green inferred from local green — **N/A** (single settlement method, not a
  document verdict), and the checker is being rebuilt so its local green no longer borrows the
  broader "re-executes / released-profile" claim (§A).
