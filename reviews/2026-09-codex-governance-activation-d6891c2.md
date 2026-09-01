# Governance-activation review — `d6891c2`

**Reviewer:** Codex (OpenAI), adversarial closure pass, 2026-09-02  
**Exact subject:** `d6891c2b65037922365fc9610594cae01c070ef5` (`origin/main` equal at review time)  
**Scope:** `CORPUS-C2-MAPPING-0.1.json`, decision register, serialized private L3, L4 replay,
trust-root boundary, and whether the operator activation act may now mint `EXACT` credit.  
**Disposition:** **BLOCKED FOR GOVERNANCE ACTIVATION.** Keep the committed empty trust root. The
pre-governance state is fail-closed, but the positive-credit path is not yet closed.

This is not a rejection of the corpus apparatus. It is the apparatus doing useful work: all current
production rows still carry zero credit, and the review found the remaining laundering paths before
an authority/manifest/decision activation made them live.

## Baseline reproduced

- `HEAD == origin/main == d6891c2b65037922365fc9610594cae01c070ef5`.
- `python3 papers/corpus/test_corpus.py` is green.
- All four exact-HEAD GitHub workflows are green:
  - `errata` — run `33559962651`;
  - `papers-deposit-check` — run `33559962605`;
  - `consumer-boundary` — run `33559962589`;
  - `embedded-claims-poc` — run `33559962557`.
- The committed `CORPUS-TRUST-ROOT.json` has empty authorities, manifests, and decision register;
  consequently the real C2 view remains non-crediting. That state is honest and should remain
  canonical until the findings below are closed.

Green mechanism tests establish the intended baseline. They do not establish that the positive
governance path rejects adversarially re-addressed decisions or a coherently rebuilt L3.

## Findings

### P0-1 — L4 accepts `EXACT` records after the mapping decisions are removed

`build_l3` validates mapping evidence and requires a pinned mapping-decision ID before it emits an
`EXACT` act. Serialized L4 reconstructs only `final_status`, faults, the completeness decision, and
the publication decision. It never rechecks the mapping adjudication or its decision-register entry.

Executable mutation against the existing test corpus:

1. Build the fully governed synthetic L3 used by `test_corpus.py`.
2. Remove all eight mapping-decision IDs from an otherwise unchanged trust root.
3. Re-run `build_l3` from candidates: `REFUSED: INCOMPLETE_TREE` — correct.
4. Run `l4_evaluate` on the previously serialized L3 with that same reduced trust root:
   `COMPLETE` — incorrect.

Observed:

```text
build_without_mapping_decisions=REFUSED INCOMPLETE_TREE
l4_prior_exact_bundle_without_mapping_decisions=COMPLETE
```

The claimed “same `_view` logic” is not the same epistemic operation: `_view` treats serialized
`final_status == EXACT` as an input fact. A content-addressed L3 proves self-consistency, not that the
mapping decision currently exists in the governance root.

This is also the broader L3-authentication gap. `validate_l3_bundle` recomputes record and bundle IDs,
but the trust root pins neither the accepted `l3_bundle_id` nor the mapper closure, and L4 has no L2
bytes/evidence with which to reproduce `_check_evidence`. An attacker can therefore coherently mint a
different L3, recompute its IDs, and submit it as a new self-consistent bundle.

**Required repair:** explicitly choose one of two contracts:

1. **Committed replay:** L4 verifies a separately committed/authorized L3 receipt and governance-root
   identity, checks each record's mapping-decision ID against that exact root, and states that it
   replays a prior adjudication rather than independently revalidating evidence; or
2. **Independent revalidation:** L4 receives the authenticated evidence operands needed to rerun the
   mapping validator.

For the current “serialized-L3-only” design, option 1 is the smaller honest repair. Avoid a hash
cycle by separating the governance-policy root from a later activation/acceptance commitment that
pins `{governance_root_id, l3_bundle_id, mapper_closure}`.

Regression required: removing any mapping-decision ID from the root used by L4 must produce a typed
refusal and zero credit, even when the serialized record says `EXACT`.

### P0-2 — Decision records authorize an occurrence, not the decision's actual subject

All three decision IDs are bound to `subject_act_id`. `act_id` addresses the source event occurrence;
it does not bind the full ActRecord facts to which completeness, publication, or mapping credit is
being granted.

I changed only one content-bearing field in a governed candidate:

```text
response_digest := sha256:ffff...ffff
```

Observed:

```text
act_id_same=True
record_id_rotated=True
view_after_response_digest_forge=COMPLETE
```

The content-addressed record correctly rotated, but the pinned completeness/publication/mapping
decisions did not. The old governance act was silently inherited by a new record. The same class
includes `prompt_digest`, offspring/dedup facts, selected children, observed verifier fields, and
other record content that does not alter the source-occurrence `act_id`.

**Required repair:** define a non-circular, kind-specific `decision_subject_id` over the exact
pre-decision proposition:

- mapping: act occurrence + all four asserted mapping components + exact evidence commitment;
- completeness: the exact act/tree facts and scope being declared complete;
- publication: the exact record/public projection, redaction profile, and loss boundary being
  cleared.

Then hash the full closed decision record against that subject ID. A decision about one record must
not transfer merely because another record points at the same raw occurrence.

Regression required: changing any decision-relevant ActRecord field must rotate the relevant subject
and decision ID or produce a typed refusal; it must never preserve `COMPLETE` under the old register.

### P0-3 — Mapping decision identity omits `evidence_commitments`

`_adjudication_ok` compares `evidence_commitments` with the evidence validated in the current build,
but `decision_record_id` hashes only:

```text
kind, subject act_id, decision, adjudicator_identity, authority
```

Changing the exact committed evidence does **not** rotate the decision ID:

```text
evidence_commitments_change_rotates_decision_id=False
```

Thus the decision register does not pin the “exact decision-record” it claims to pin. This is a
direct address alias, independent of whether a particular bad evidence mutation also fails elsewhere
today.

**Required repair:** use a closed schema per decision kind and hash its complete canonical body.
For mapping, that body must include the exact evidence commitments and the P0-2 mapping-subject ID.
Reject unknown/missing decision fields rather than silently projecting only four selected keys.

Regression required: any change in evidence commitments, authority, adjudicator, verdict, subject
mapping, or schema version rotates the decision ID.

### P0-4 — The frozen eight-row operand is not an activation operand yet

Each production C2 row remains `DERIVED` and carries evidence for only:

```text
root_digest, verifier_identity
```

But `EXACT` requires four independently validated components:

```text
experiment_id, root_digest, verifier_identity, agent_run_occurrence
```

The existing row review already records two substantive residuals:

- `root_digest` names the ROOT-file token, not the exact root claim;
- `EXP-RVB-1c` is asserted and cannot currently be distinguished from 1b from identical prompts.

In addition, `agent_run_occurrence` is structurally present and uniqueness-tested, but the frozen rows
contain no `agent_run_occurrence` evidence record. Therefore the promised transition “admit authority
+ pin manifest/decision IDs → reviewed rows become EXACT” cannot happen over this frozen table. The
table must change, or the scientific claim/scope must narrow.

This is not a defect in its current `DERIVED` status. It is an activation blocker: an operator act
cannot substitute authority for missing provenance.

**Required repair:** create a new versioned mapping operand rather than rewriting the reviewed
`0.1` table. Evidence all four required components. If crossed-design provenance is irrecoverably
ambiguous, keep that component `AMBIGUOUS` and narrow C2 to the actually evidenced 4x2 observed-model
unit, or leave C2 refused. For the root, either evidence/hash the exact claim text or explicitly rename
the unit to “ROOT-file token” and narrow the paper claim accordingly.

## P1 hardening before activation

1. Make the trust-root and L3 schemas truly closed at every nested level. Authority entries and
   decision-register entries currently need only be strings; decision bodies have no closed schema.
2. Bind L3 to an approved mapper closure. Merely rotating `evaluation_id` on mapper mutation makes the
   fork visible but still lets the fork return `COMPLETE`.
3. Add the exact positive production test only after the new evidence operand exists. Synthetic
   `COMPLETE` is valuable mechanism coverage, not evidence that the real C2 rows are activation-ready.

## Minimal repair order

1. Replace bare-`act_id` decision subjects with kind-specific pre-decision subject IDs.
2. Hash and validate full closed decision bodies, including mapping evidence commitments.
3. Close the L4 contract: pin governance-root + L3 + mapper closure in a separate activation
   commitment, and recheck mapping decision membership during L4 replay.
4. Add the three mutations from this review to CI:
   - remove mapping decisions before L4 → typed refusal;
   - mutate a decision-relevant record field → old decisions no longer grant credit;
   - mutate evidence commitments → decision ID rotates.
5. Produce and adversarially review a new C2 mapping operand with all four evidence components, or
   formally narrow the claim where evidence cannot exist.
6. Only then perform a separate operator activation act and review that exact act/commitment.

## What is accepted

- Preservation, authenticated L2 extraction, the frozen `DERIVED` C2 table, and the current empty
  trust root remain useful and honestly non-crediting.
- Record and L3 IDs correctly expose incoherent edits/removals.
- The serialized representation is sufficient to reproduce the current `_view` computation.
- Run uniqueness is now enforced at the view layer.

The remaining issue is narrower but decisive: **reproducing a computation over self-consistent L3
records is not yet reproducing the authority/evidence path that allowed those records to say
`EXACT`.** Until that membrane is closed, keep `CORPUS-TRUST-ROOT.json` empty and do not activate or
deposit C2 as checked.
