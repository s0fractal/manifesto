# Codex closure review — papers v0.2 after Kimi pass

**Reviewer:** Codex / OpenAI  
**Date:** 2026-09-01  
**Reviewed commit:** `eee0938091bc3044e249064c782d110d6d91fe26` (`origin/main`)  
**Relation:** closure pass after `reviews/2026-09-codex-papers-v0.2.md` and
`reviews/2026-09-kimi-001.md`  
**Disposition:** **BLOCKED for promotion and deposit.** The v0.2 argumentative core is now largely
repairable and much better scoped, but HEAD is red, controlled forgetting has not removed v0.1 from
the canonical/build surface, Paper A has acquired an unverified queueing claim, and the deposit
checkers still do not decide the candidate papers.

This is not a request for another whole-paper rewrite. Keep the repaired evidence boundaries. Close
the findings below, then ask for a short exact-HEAD confirmation.

## What this pass checked

- diff and history from `d1d0a6c` through `eee0938`;
- both v0.2 drafts, claim ledgers, migration notes, deposit/audit documents, Kimi review/prompt, and
  the new novelty search log;
- the canonical `paper.md`, generated HTML, build scripts, current checkers, embedded-claims
  fixtures, and controlled-forgetting proposal;
- clean `sigma-glyph==0.6.7` runs of both paper checkers and `tools/replay_pack.py`;
- destructive-negative **in a temporary copy**: delete both v0.2 draft files and rerun both paper
  checkers;
- live GitHub Actions status and failed log at the reviewed SHA;
- primary/official sources for Dhall, Unison, Nix, Ethereum gas, Zenodo mixed licensing, and the
  queueing references named by the Kimi pass.

## Findings

### P0-1 — `eee0938` is red: the README repair correctly made the embedded-claims evidence stale

The root `README.md` edit changed the dependency bytes but did not rotate the pins that intentionally
commit to those bytes. Live GitHub Actions at the reviewed SHA reports:

- `errata`: success;
- `consumer-boundary`: success;
- `embedded-claims-poc`: **failure**.

Live run: <https://github.com/s0fractal/manifesto/actions/runs/33532397056>.

The failed job reports three formerly-valid fixtures as `STALE`:

- `drafts/embedded-claims-poc/fixtures/valid/repo-count.md`;
- `drafts/embedded-claims-poc/fixtures/valid/world-claim-a.md`;
- `drafts/embedded-claims-poc/fixtures/valid/world-claim-b.md`.

All three pin README digest `259f54a6…`; current `README.md` is
`sha256:f1bb9ae17192e42624d527c7c37b472c5bf4720631f5036ebd35f81860d86cc7`.
The real E2E specimen pins the same old digest. A clean local run of
`claims.py run --strict drafts/EMBEDDED-CLAIMS-E2E-0.1.md` exits 1 with a one-record vector:

```text
README-THESIS-HEADING-COUNT  execution=STALE
facts=[DEPENDENCY_STALE, RESULT_MATCH]
```

This is not a flaky gate; it is the freshness discipline working. Re-pin the three fixtures and the
E2E capsule through the normal tooling, rerun all layers, and require live Actions green before any
paper closure statement.

**Type:** `integrity_break` (current evidence no longer addresses current operand).  
**Action gate:** exact-HEAD `embedded-claims-poc` success, including non-empty E2E exact scope.

### P0-2 — the Kimi queue repair imports a new theorem-shaped conflation

`papers/every-check-spawns-more/paper-v0.2-draft.md:212–230` first says no replacement theorem is
validated, then asserts all of the following:

1. the process reduces to a standard branching-service / feedback queue;
2. `lambda_G < (1-mu)lambda_V` is the resulting stability condition;
3. the mean-load bound is tight under FIFO but false under SRPT;
4. `mu >= 1` implies a particular transience statement;
5. a minimal executable simulation “ships”.

The last statement is factually false at this SHA: no scheduler simulation exists; the ledger still
says “counterexample to ship” and `DEPOSIT-AND-AUDIT.md` still lists it as future work.

More importantly, item 3 mixes different observables. Under the stated reduction, if a root has
total service requirement `S` with `E[S]=1/(1-mu)`, workload load is
`lambda_G E[S]/lambda_V`. For ordinary work-conserving single-server queues, changing FIFO to SRPT
can change completion order, response-time distribution, and the fraction of short roots completed;
it does not by itself make the workload-capacity condition false. The original scheduler
counterexamples refute a bound on **fraction of roots unclosed / early completions**, not the
workload conservation condition. “Stability”, “throughput”, “fraction closed”, and “root completion
latency” must not share one sentence.

The named references are also not yet adjacent evidence for the exact proposition. Jagers and Mode
establish branching-process background; Disney–König is a queueing-network survey; the cited Takagi
volume is not presently connected to a precise theorem/page. Two LLMs locating a literature family
is good discovery credit, not validation of the reduction.

**Required repair:** either remove the new theorem-shaped paragraph and leave the question explicitly
open, or define one exact stochastic model and one observable, give a derivation/proof, and cite an
exact theorem/page that matches it. Keep the already-valid negative scheduler counterexamples, but do
not let them prove a replacement. Add the promised executable counterexample before saying it ships.

**Type:** `scope_boundary` plus `integrity_break` for the missing shipped artifact.  
**Action gate:** a named queue state, discipline, service law, proposition, proof/reproducer, and
matching source; or deletion of the positive reduction claim.

### P0-3 — README resurrection was fixed, but controlled forgetting has not retired the canonical surface

The Step-0 Kimi probe was productive: it found a real README leak, and `eee0938` closes that local
channel. It does **not** establish repository-wide retirement, because the probe intentionally read
only two READMEs.

Both canonical files still contain the complete v0.1 body after a tombstone banner:

- `papers/every-check-spawns-more/paper.md` — unchanged content digest
  `a464315782a3963a58747636a007b9b5a41b59ccbdab6cc1dc20567fe557f157`;
- `papers/addressing-is-equality/paper.md` — unchanged content digest
  `ac9fe215e694acd2d54166225ecd30796f85e7c0406f50b0af17488f57ed6ddc`.

The retired abstracts and claims remain literal text on the canonical source path, and both
`build.sh` files still build that path. The generated HTML likewise contains the v0.1 titles and
bodies. This directly violates the repository's own controlled-forgetting rule:
`drafts/CONTROLLED-FORGETTING-0.1.md:144–145` says a tombstone must not copy the retired artifact,
because it then becomes the resurrection channel.

Until promotion is authorized, choose one honest interim state:

- move the full v0.1 bodies to explicitly historical paths and leave minimal tombstones at the
  canonical paths; or
- keep them temporarily, but classify the operation as **retirement pending / quarantined**, remove
  them from default indexes and make the build refuse a superseded source.

At promotion, the already-written order is sound: archive/rename v0.1, make reviewed v0.2 the sole
canonical `paper.md`, regenerate outputs, and record exact loss. Git history remains historical
substrate; it need not compete in HEAD.

**Type:** `integrity_break` against controlled-forgetting I2/I3 and the tombstone contract.  
**Action gate:** a default-context/build probe must be unable to recover a retired claim without
explicitly requesting historical material.

### P0-4 — the candidate papers can disappear while both paper checkers remain green

The known stale-green finding is still open, and the mutation is now simpler than the original
literal test. In a temporary repository copy I deleted both:

```text
papers/every-check-spawns-more/paper-v0.2-draft.md
papers/addressing-is-equality/paper-v0.2-draft.md
```

Both checkers still exited 0:

```text
GREEN: every recounted figure matches paper.md.
GREEN: every benchmark figure re-executed and matched.
```

Therefore neither checker consumes, hashes, parses, or even requires the candidate it is supposed to
license for deposit. Paper B additionally says figures are “bound by AST hash”
(`paper-v0.2-draft.md:79–81, 204–210`), but the current checker emits no term/AST hashes. Paper A says
the scheduler counterexample ships, but no such artifact exists. The acceptance self-checks mark
these categories **yes** anyway; Paper A even names nonexistent ledger row C9 although its ledger is
C1–C8.

**Required repair:** implement the already-designed closed manifest. Its success object must contain
the exact candidate-paper digest, closed claim-ID set, checked/excluded/refused sets, profile/source
identity, and actual executed operand IDs. Until then, acceptance-gate rows for re-derivation,
fixtures, and candidate binding are **NO / BLOCKED**, not yes.

**Type:** `integrity_break` / stale-green.  
**Action gate:** deleting or mutating the candidate paper, a ledger row, a source commitment, or a
profile label makes the deposit gate fail closed for an addressed reason.

### P1-1 — the prior-art narrowing is useful, but the log merges three different hash relations

The new search log correctly kills the broad novelty claim. Keep that. But the sentence
“Dhall, Unison, and Nix already make the hash of the normal form the identity” is not supported by
the very rows above it:

- Dhall semantic integrity hashes a canonicalized/interpreted expression — this is the close
  normal-form precedent;
- Unison hashes a term/type declaration's internal syntax structure and dependencies — definition
  identity, not the normal form of a computed result;
- Nix distinguishes input-addressed derivations and content-addressed build outputs/realisations —
  build-product identity, not program normal-form identity.

The paper repeats the merged claim at `paper-v0.2-draft.md:242–245`, and the ledger repeats it under
OPEN. Replace the family slogan with three typed relations. They all narrow novelty, but by different
routes.

The Ethereum comparison also conflates **gas units / gas limit** with **gas price / fee**. The EVM has
a deterministic protocol gas schedule and transaction gas limit for a fixed execution context; the
wei price per gas is market/protocol-priced. The real near-miss boundary is that Ethereum receipts
record execution/state-transition facts and gas used, not a two-sided equality settlement over a
total canonicalizing evaluator. Say that, rather than “gas is market-priced, not a deterministic
budget bound”.

Finally, `novelty-search-log.md` is a useful comparison memo, not yet a reproducible search log: it
has no query strings, databases, search dates per query, URLs/DOIs for most rows, inclusion criteria,
or screened-result counts. Keep novelty OPEN and do not call the prior-art obligation closed.

**Type:** `scope_boundary` / `open_obligation`.  
**Action gate:** relation-specific wording plus a reproducible search appendix and independent human
verification.

### P1-2 — current Zenodo supports mixed-license uploads; two records are a policy choice, not a platform requirement

`papers/every-check-spawns-more/DEPOSIT-AND-AUDIT.md:147–156` says Zenodo has one license per record
and no mixed/path-scoped licensing, therefore two linked records are required. The companion audit
inherits that claim.

Current official Zenodo help explicitly documents **Mixed license uploads** and says all applicable
licenses may be declared for files under different licenses. The older REST API documentation shows
a singular legacy `license` field, but it is not a safe description of the current deposit UI/model.

Two linked publication/software records may still be the clearest design. Keep it if chosen for
genre, citation, and versioning reasons — not because Zenodo allegedly forbids a mixed-license
record. For either design, include the repository's path-scoped license authority and both complete
license texts in the curated artifact.

**Type:** `integrity_break` in deposit mechanics.  
**Action gate:** verify the chosen workflow against current Zenodo UI/API immediately before deposit.

### P1-3 — the audit documents were not closed over the Kimi commit

Several self-descriptions became false at `eee0938`:

- Paper A audit lines 172–175 and Paper B audit lines 186–191 say Codex is still the only
  out-of-lineage review and Kimi/Qwen is owed; Kimi is now filed.
- Paper A line 216 calls Fable and Kimi “two independent LLM reviewers”, while the audit correctly
  classifies Fable as same-lineage with the authoring model. Say “two model readings, one
  out-of-lineage”; lineage diversity is discovery credit, not independent validation.
- Paper B audit lines 43–45 and 150–156 say the body has no `[@key]` citations; §6 now contains four.
  Paper A still has none, so the status differs by paper.
- Paper A paper line 229 says the simulation ships while the ledger and audit say it is future work.
- Paper A self-check says ledger C1–C9 although only C1–C8 exist.
- Both acceptance self-checks say “yes” for evidence the same documents explicitly describe as not
  implemented (closed manifest, corpus-derived tables, vendored profile, candidate-bound build).

This is precisely a controlled-forgetting / SSoT problem at document scale: a finding was closed in
one surface while its old status remained active elsewhere. Replace unconditional “yes” with an
executable status generated from the deposit manifest, or at minimum a truthful `BLOCKED` table whose
rows point to the missing artifact.

**Type:** `integrity_break` / provenance drift.

## Findings from the earlier review that are genuinely closed

Do not reopen these unless a later edit regresses them:

- Paper A is scoped to one purposively sampled Monday/Fable monologue corpus; finite-depth,
  self-adjudicated ô is separated from asymptotics and from the terminal zero-obligation execution
  sub-act.
- The four-root crossed table and confounding are visible; Kimi's offspring-overlap and paraphrase
  questions are correctly marked blocked on the missing corpus.
- The v0.1 queue closed forms are retired by explicit scheduler counterexamples; they are not evidence
  for a replacement.
- Paper B separates permissive-harness measurements from the unreleased `church@v0` DRAFT profile;
  `PLUS 7 5` remains an admission gap.
- Marker collision, exit kinds, budget exhaustion as UNSETTLED, two-sided `EQN`, Warrant per-check
  replay versus pack `LEGACY_UNPINNED`, and hash-relative observation identity are now honestly typed.
- Novelty is OPEN and the broad “addressing is identity” claim has been withdrawn.

## Still-owed blockers (not regressions)

1. frozen Paper A act corpus with exact prompts, roots, offspring, selections, dedup/removal decisions,
   and model/sampling identity;
2. offspring-overlap and paraphrase-leak audits over that frozen corpus;
3. candidate-bound closed-manifest checkers for both papers;
4. Paper B vendored/pinned DRAFT profile plus admission/refusal fixtures and a single honest statement
   that no implementation currently both admits the motivating case and emits the proposed receipt;
5. exact bibliography/build/metadata closure and human prior-art verification;
6. promotion only after the old canonical/build surface is retired.

## Minimal repair order

1. Restore green by re-pinning the README-dependent embedded claims; verify live Actions.
2. Retract or formally settle the new queue paragraph; add the scheduler artifact before saying it
   ships.
3. Correct the prior-art relations, Ethereum wording, Zenodo mechanics, and stale provenance text.
4. Export the frozen act corpus and run the two construct-validity audits.
5. Implement candidate-bound closed-manifest checkers; turn acceptance tables into their output.
6. Perform controlled retirement/promotion, regenerate the build, then request an exact-HEAD closure
   pass.

## Primary-source anchors used in this pass

- Zenodo, mixed-license uploads: <https://help.zenodo.org/docs/deposit/describe-records/licenses/>
- Dhall semantic integrity: <https://docs.dhall-lang.org/tutorials/Language-Tour.html>
- Unison hashes: <https://www.unison-lang.org/docs/language-reference/hashes/>
- Nix RFC 0062: <https://github.com/NixOS/rfcs/blob/master/rfcs/0062-content-addressed-paths.md>
- Ethereum Yellow Paper: <https://ethereum.github.io/yellowpaper/paper.pdf>
- Disney, König & Schmidt, single-server feedback queues:
  <https://doi.org/10.2307/1427078>

## Closure condition

**Do not promote or deposit at `eee0938`.** A next pass can be short if it is bound to one commit and
is given: green workflow URLs, frozen corpus manifest, closed-manifest checker reports, corrected
queue/prior-art text, and the canonical-source retirement receipt. Publication may then be a truthful
trajectory marker; it should not freeze this intermediate contradiction set.
