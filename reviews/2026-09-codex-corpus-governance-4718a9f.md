# Codex focused exact-HEAD review — pre-governance corpus at `4718a9f`

**Reviewer:** Codex / OpenAI  
**Date:** 2026-09-01  
**Reviewed commit:** `4718a9f1d4b153fda83563ac2c750dd9476e7b4b` (`origin/main`)  
**Disposition:** **PRE-GOVERNANCE SAFE. Approved for untrusted `DERIVED` mapping discovery. Not yet
approved for admitting authorities, canonical `EXACT`, pinned-manifest credit, L4, or auto-proposer.**

This is intentionally not another demand for “authority above authority.” The committed Git revision
and operator-selected `CORPUS-TRUST-ROOT.json` are an acceptable external trust anchor. With its actual
empty authority sets and empty pinned-manifest map, no claim can receive credit. The current state is
therefore honest and safe for discovery.

Before activating governance, two mechanical gaps and one issuance gap must be closed. They are finite
and adjacent to the planned governance act.

## Exact state and positive evidence

- `HEAD == origin/main == 4718a9f1d4b153fda83563ac2c750dd9476e7b4b`;
- all four GitHub workflows are green at that SHA;
- current corpus suite passes;
- live extraction is `CLEAN`, `55/55`, `1239 events`;
- live and committed reports are JSON-equal;
- the real 1239-event bundle mints `CLEAN` and verifies;
- committed trust root pins the real report ID, corpus commitment, and extraction closure;
- committed trust root admits zero mapping/completeness/publication authorities and pins zero
  manifests;
- every real empty-input view is currently `REFUSED: REQUIRED_UNITS_UNSPECIFIED`;
- no corpus claim has flipped to `CHECKED`.

The external trust-root boundary is accepted. Findings below are about what happens after that root is
selected.

## Findings before credit activation

### P0-1 — A coherent replacement bundle can inherit the real report commitment

`mint_l2_bundle()` now enforces full-set equality, but `verify_bundle()` does not have the committed
event manifest or a pinned expected bundle ID. It checks that a submitted body is self-addressed and
names the real report/commitment. A caller can therefore construct a different coherent body, recompute
its bundle ID, and inherit the real report commitment.

I started from the real 1239-event bundle and rebuilt it as a one-event bundle while retaining the real
`report_id` and `corpus_commitment`:

```text
coherent subset body: 1 of 1239 events
new self-consistent bundle_id
verify_bundle -> (True, None)
```

Likewise, replacing `expected_closure` with `clo:extract:FORGED`, recomputing `bundle_id`, and retaining
the real report/commitment also verified successfully.

This bypasses `mint_l2_bundle()` rather than forging hashes. The bundle is addressed but not admitted.

**Required repair:** pin the canonical full `l2_bundle_id` (or exact event-manifest ID) in the external
trust root and require equality in `verify_bundle()`. Alternatively pass the already verified report
into bundle verification and re-check exact event-set/closure equality. A projection must have a
separately pinned projection manifest and loss report; it cannot reuse the full-bundle role.

### P0-2 — `mint_l2_bundle()` does not bind `event_index` to its committed manifest row

Membership is checked using `(event_id, body_digest)` and final set equality uses event IDs. The
manifest's `event_index` is not compared with the submitted event. Swapping indices 0 and 1 inside a
real multi-event blob preserves a gap-free index set and all event IDs.

Live mutation result:

```text
event_index permutation applied = True
mint_l2_bundle status            = CLEAN
verify_bundle                    = (True, None)
```

Compare each canonical event row exactly with the pinned manifest row: blob ID, event index, event ID,
body digest, and occurrence/span as committed or derivable. This is a small exact-equality repair.

### P0-3 — Authority-name admission does not authenticate decision issuance

The trust root now controls which authority **labels** are admitted. That correctly blocks the current
empty-governance state. After a label is admitted, however, any candidate can write that string into
`authority` together with an arbitrary `adjudicator_identity`; `_admitted()` has no signature,
receipt, separately pinned decision ID, or trusted-source separation.

Thus “authority `operator-review` is admitted” currently means “any submitted dictionary claiming
`authority=operator-review` is accepted.” An auto-proposer or malformed mapping table could impersonate
the authority without modifying the trust root.

This does **not** require an infinite authority chain. The external governance act can close it by
pinning exact decision-record IDs (mapping/completeness/publication) in the trust root or a referenced
decision register, optionally backed by Warrant/signatures later. Git-reviewed immutable decision
artifacts are sufficient for the current phase; bare authority strings are not.

## Findings that may close with the L4 implementation

### P1-4 — The private L3 is emitted, but “L4 can replay” is not yet demonstrated

The new output finally contains `{record_id, body}` records and an L3 bundle ID. That is real progress.
The current test only checks that several body keys exist. There is no L3 bundle validator or L4
consumer proving round-trip replay.

Topology also remains encoded as `parent_local_ref` / `selected_child_refs`, while record bodies do not
carry their own `local_ref`; serialized consumers cannot reliably resolve those names to record IDs.
The frozen schema called for parent/child act IDs.

Before L4 credit:

- finalize topology to record/act IDs or include a closed local-ref index in the L3 bundle;
- validate every record ID/body and the exact record set against `l3_bundle_id`;
- run L4 using only serialized L3 + pinned manifest/trust operands after deleting the source candidate
  table;
- prove mutation/missing-record/dangling-topology failures.

### P1-5 — Trust-root and decision artifacts need closed schemas before their first non-empty version

The committed empty trust root is well-formed, but there is no closed validator for authority lists,
pinned manifest entries, duplicate values, decision registers, or unexpected fields. Add this before
the governance commit that first populates them. The trust root itself remains operator-selected; the
validator only prevents malformed or ambiguous interpretation.

## What is clean now

- report identity is recomputed and pinned externally;
- non-clean and non-pinned reports are refused;
- the current full real bundle is reproducible;
- stale/mutated bodies and incoherent bundle mutations are caught;
- record and mapping IDs bind final graph status and mapper closure;
- evidence-span adjudication is exact;
- unpinned replacement manifests are refused under the current pinned-manifest mechanism;
- full record bodies now leave `build_l3()`;
- the committed empty governance state cannot mint credit.

Therefore the project does not need a fifth *deep* repair cycle before corpus exploration. It can move
to a reviewable mapping table whose entries are forced to `DERIVED` and whose outputs are explicitly
non-crediting. The remaining repair belongs immediately before—or inside—the first governance/L4
activation.

## Finite next sequence

1. Produce `DERIVED` mapping candidates and evidence spans; no admitted authority, no pinned manifest.
2. Pin/verify the canonical full L2 bundle or exact manifest ID; close event-index equality.
3. Define a closed decision register and trust-root schema; pin exact decision IDs, not just labels.
4. Build the serialized-L3 validator and L4 replay against pinned manifests.
5. Request one governance-activation review of those concrete artifacts.
6. Only then enable canonical `EXACT`/credit; auto-proposer remains permanently `DERIVED`.

## Activation-gate mutations

```text
real report + coherently rebuilt subset bundle -> BUNDLE_NOT_PINNED / SET_MISMATCH
real report + forged expected_closure          -> CLOSURE_MISMATCH
permuted event_index with same event ids       -> EVENT_MANIFEST_MISMATCH
candidate impersonates admitted authority      -> DECISION_NOT_PINNED
malformed/non-closed trust root                 -> TRUST_ROOT_INVALID
serialized L3 body/record removal               -> L3_BUNDLE_MISMATCH
serialized L3 dangling topology                 -> DANGLING_REF
L4 without source candidate table               -> reproduces exact vector or typed refusal
```
