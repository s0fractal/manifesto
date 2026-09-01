# Governance-activation review — `ecda7f0`

**Reviewer:** Codex (OpenAI), adversarial activation pass, 2026-09-02  
**Exact subject:** `ecda7f076a0d66e4fdd9e2324f016016c4f90ffb` (`origin/main` equal at review time)  
**Scope:** repaired credit path, production `CORPUS-C2-MAPPING-0.2.json`, its 24 evidence
spans, activation simulation, serialized L3/L4, and the proposed `REFUSED → CHECKED` transition.  
**Disposition:** **C2 ADDRESS MAP ACCEPTED; C2 MEASUREMENT ACTIVATION BLOCKED.** Keep the committed
trust root empty. The 0.2 operand is a valid non-crediting address/evidence map, but the current
activation claim exceeds what that map proves and the production activation path is not yet closed.

## Baseline and positive result

- `HEAD == origin/main == ecda7f076a0d66e4fdd9e2324f016016c4f90ffb`.
- `python3 papers/corpus/test_corpus.py` is green.
- All four exact-HEAD GitHub workflows are green:
  - `papers-deposit-check` — run `33562658044`;
  - `consumer-boundary` — run `33562658071`;
  - `embedded-claims-poc` — run `33562658089`;
  - `errata` — run `33562658078`.
- I independently rebuilt L2 from the 55 quarantined blobs. The rebuilt report matched the committed
  `report_id`, corpus commitment, and extraction closure; all 1239 events and the pinned L2 bundle ID
  matched.
- All eight production 0.2 rows validate with zero mapping faults. All 24 evidence records are unique
  and value-valid:
  - 8 ROOT-file-token occurrences;
  - 8 observed `message.model` occurrences;
  - 8 transcript `agentId` occurrences.
- The addressed set is exactly four ROOT tokens × two observed models; the eight run occurrences are
  distinct.
- With the committed empty trust root, all rows remain `DERIVED`, zero rows are `EXACT`, and C2 is
  refused. That state is correct.

This closes the evidence part of the prior P0-4 for the **address-map subclaim**. The remaining
findings concern what is activated, which artifact is activated, and whether L4 preserves the exact
provenance/decision meaning.

## Findings

### P0-1 — The activated view proves cohort addressing, not the paper's C2 measurement

The paper/claim manifest defines C2 as a measurement claim about ô, the Opus/Sonnet split, its
confounding, and the crossed comparison. The 0.2 records validate only three identity components:

```text
root_digest, verifier_identity, agent_run_occurrence
```

Every production row still carries:

```text
offspring_before_dedup = UNKNOWN
dedup_removal_decisions = UNKNOWN
prompt_digest = UNKNOWN
response_digest = UNKNOWN
```

Nevertheless, the activation simulation returns:

```text
C2 COMPLETE
8 EXACT acts
```

No evaluator in this path extracts offspring, applies the removal/dedup protocol, re-derives ô, or
checks the paper's reported values. `COMPLETE` therefore means “the required 4×2 address units are
present and governed,” not “C2's measurement is checked.” Wiring this view directly into
`deposit_check` as C2 `CHECKED` would be composition laundering: locally green identity predicates
would lend their credit to an unexecuted measurement predicate.

**Required repair:** split the claim and the credit explicitly:

- `C2-MAP`: eight authenticated transcript acts form the admitted ROOT-token × observed-model 4×2
  cohort, with unique run occurrences. The 0.2 operand can support this claim.
- `C2-MEAS`: offspring counts, dedup/removal decisions, ô derivation, reported aggregates, and the
  limited comparison. This remains `REFUSED`/`OPEN` until those values are extracted, addressed, and
  replayed.

The paper's C2 may present the vector, but the deposit checker must not collapse it to one global
`CHECKED`. A valid first activation is `C2-MAP = CHECKED` adjacent to
`C2-MEAS = REFUSED: MEASUREMENT_NOT_REPLAYED`.

### P0-2 — The production operand and its proof are absent from every executable gate

`test_corpus.py` uses a synthetic `full()` table. No test or workflow opens
`CORPUS-C2-MAPPING-0.2.json`. The JSON's `proof` object is descriptive metadata, not a generated or
verified receipt.

Executable stale-green mutation in an isolated archive of exact HEAD:

```text
baseline test_corpus.py                         exit 0
move CORPUS-C2-MAPPING-0.2.json out of the repo exit 0
```

Both runs end with the identical green summary. Thus CI success does not establish that the
production operand exists, has eight rows, has 24 valid spans, or supports the claimed activation
simulation.

**Required repair:** add a production-operand gate that at minimum binds the exact file digest,
closed schema, exact 8-row closed set, 24 evidence records, unit bijection, and the expected
non-crediting baseline. The machine-local full pass should emit a metadata-only activation report
bound to:

```text
operand digest + extraction report + L2 bundle + manifest + mapper closure
+ exact record IDs + decision IDs + result vector
```

CI can verify the report/closed artifacts; it must honestly label raw-span revalidation as
machine-local until a publication-cleared evidence projection is deposited. Deletion or one-byte
mutation of the production operand must fail closed.

### P0-3 — Filling the trust root does not promote the committed 0.2 operand

The committed rows are `mapping_status: DERIVED` with `adjudication: null`. Merely admitting
authorities and pinning a manifest/decision register does not change their status. Against a fully
populated simulated root:

```text
transformed governed candidate derived from 0.2  -> COMPLETE, 8 EXACT
unchanged committed 0.2 rows under the same root -> REFUSED, 0 EXACT
```

The simulation silently performs an additional semantic mutation: it changes each row to `EXACT`
and constructs an adjudication. Therefore the promised next step — “only populate trust root and C2
becomes checked” — is not the implemented transition. The actual governed operand/overlay does not
exist yet and is not reviewable.

**Required repair:** keep 0.2 immutable as the reviewed `DERIVED` evidence map. Create an explicit
activation proposal/overlay (or a new governed operand version) that references the 0.2 digest and
contains the exact mapping decisions, evidence commitments, authority identities, required-unit
manifest, mapper closure, and proposed decision-register entries. Generate the trust-root change
from that proposal, not from an unrecorded one-off transformation. The operator act must pin the
activation proposal ID.

### P0-4 — Mapping decision subjects still omit live mapping fields

`_mapping_subject` claims to bind “the act + components + evidence commitment,” but it does not hash
`mapping.act_id` or `mapping.status`; `_content_subject` omits the entire `mapping` object.
`record_publishable` checks `final_status == EXACT` but does not require
`mapping.status == final_status`.

I took an activated serialized L3, changed only:

```text
mapping.act_id = act:FORGED
mapping.status = DERIVED
```

then coherently recomputed the record ID, local-ref index, and L3 bundle ID. The old governance
decision IDs still applied:

```text
validate_l3_bundle = true
l4_evaluate C2     = COMPLETE
```

This is the same transfer class as the prior `response_digest` finding, through two fields left out
of the repaired subject.

**Required repair:** define a closed pre-decision mapping proposition containing at least the source
act ID, asserted components, exact evidence commitment, mapping profile/schema, and proposed mapping
status. Hash all of it into the mapping subject. During L4 validation require the internal
consistency invariant:

```text
mapping.status == final_status == EXACT
```

and reject unknown/missing mapping fields. Mutation of `mapping.act_id`, `mapping.status`, or the
mapping profile must rotate/refuse the old decision.

### P0-5 — L4 does not compare its top-level L2/mapper operands with the trust root or records

`validate_l3_bundle` self-hashes top-level `l2_bundle_id` and `mapper_closure`, but L4 does not require:

```text
private_l3.l2_bundle_id == trust_root.l2_bundle_id
private_l3.mapper_closure == trust_root.mapper_closure
record.body.mapper_closure == private_l3.mapper_closure
```

Two coherent re-forges against the original activated decision register both validate and remain
`COMPLETE`:

```text
top-level mapper_closure := clo:map:FORGED
  validate_l3_bundle = true; L4 = COMPLETE; evaluation_id rotates

top-level l2_bundle_id := bnd:FORGED
  validate_l3_bundle = true; L4 = COMPLETE; report says l2_bundle_id=bnd:FORGED
```

Rotating the evaluation ID makes a fork visible, but it does not justify returning positive credit
under an unapproved provenance operand. The L2 mutation is worse: the result explicitly names a
bundle that supplied none of the record evidence.

**Required repair:** before view evaluation, require equality to the pinned trust-root operands and
cross-check every record's mapper closure with the top-level closure. For any positive-credit root,
`mapper_closure` must be mandatory, not optional. Prefer additionally binding an activation/proposal
ID into the L3/evaluation report.

### P1-6 — `experiment_id` is declared non-evidenced but remains a selection predicate

The narrative correctly says 1b/1c provenance is ambiguous and narrows C2 to the observed-model 4×2.
Yet `_view` still selects relevant acts through `manifest.experiment_ids`, and the simulated manifest
uses asserted `EXP-RVB-1c`. Thus the result computationally depends on a label the claim says is not
evidenced.

For `C2-MAP`, select the exact eight governed record IDs/units directly, or introduce a claim-specific
cohort ID whose stipulated/governed status is explicit. Do not let `EXP-RVB-1c` silently restore a
crossed-experiment provenance claim. If it remains as descriptive metadata, exclude it from the
selection predicate and keep the 1b/1c ambiguity adjacent in the paper.

## Minimal repair order

1. Split `C2-MAP` from `C2-MEAS`; forbid the address-map result from marking the measurement claim
   checked.
2. Add a real production-operand gate; deletion/mutation of 0.2 must make the activation check fail.
3. Materialize a closed activation proposal/overlay and required-unit manifest bound to the 0.2
   digest. Do not mutate `DERIVED → EXACT` only inside an unrecorded simulation.
4. Complete the mapping decision subject and enforce `mapping.status == final_status`.
5. Bind top-level L2 and mapper closure to the trust root and to each record; add the two coherent
   re-forge mutations above.
6. Remove asserted `experiment_id` from the C2-MAP selection predicate or type it as a governed
   cohort stipulation, not raw provenance.
7. Re-run the 24-span production validator and file a generated activation report.
8. Review the exact activation proposal and exact trust-root diff. Only then may the operator activate
   `C2-MAP`. Keep `C2-MEAS` refused until the measurement derivation exists.

## Accepted scope

- The three old credit-laundering regressions are genuinely closed for the fields they cover.
- Decision bodies now bind evidence commitments and are schema-closed at the top decision level.
- L4 now rechecks decision-register membership instead of blindly trusting `final_status`.
- The production 0.2 address map itself is clean against the machine-local quarantined bytes:
  24/24 evidence spans validate, no reuse, exact 4×2, unique runs.
- Narrowing away unevidenced 1b/1c provenance is directionally correct.

The apparatus has earned a useful first positive claim, but it is a narrower one than “paper C2 is
checked”: **we know exactly which eight transcript occurrences form the governed 4×2 cohort. We do
not yet know, through this pipeline, that the paper's ô measurements were correctly extracted and
derived from them.**
