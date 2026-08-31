# Review: FLOW-0.3 candidate-primitives register

## Review metadata

- **Reviewer:** OpenAI Codex
- **Review date:** 2026-08-31
- **Target:** `drafts/FLOW-0.3-CANDIDATES.md`
- **Target commit:** `e07ef05fffd10d360c2dc8ed594c916be22c26e3`
- **Target SHA-256:** `7ec4168de07e225ab076f07c8be15b28997a52dae66681d4a36f584a71107bf9`
- **Method:** adversarial technical, ontological, epistemic, ethical, governance, and provenance review against the current `FLOW.md`, glossary debts D5 and D15-D18, and the G6 findings. Current closure-season fixes were also spot-checked through bounded reproductions.
- **Scope boundary:** this review evaluates candidates. It does not adopt them into FLOW, close glossary debts, or establish external validation.

## Verdict

**Keep this document as a candidate register. Do not transfer Section A into `FLOW.md` yet.**

The register is already a meaningful improvement over immediately editing the specification: it labels the material as candidate work and preserves an explicit OVERREACH section. But none of the three main candidates is ready for adoption as written. The carrier proposal has the right problem but the wrong type shape; the endogenous-change proposal collapses several independent dimensions and still loses its canonical rock counterexample; the intervention proposal usefully names a contrast class but risks defining reflexivity circularly.

This is not a rejection of the mined material. It is a recommendation to preserve it as discovery evidence while refusing to convert recurrence into validation credit.

## Executive disposition

| Candidate | Disposition | Reason | Gate before adoption |
|---|---|---|---|
| D5/D16 constraint carrier | **REVISE** | A function from constraint to one carrier category cannot represent multiplicity, time, scope, role, or concrete carrier identity. | Replace with a scoped many-to-many relation and pass the listed countermodels. |
| D17 endogenous change | **REJECT CURRENT SYNTHESIS** | The three channels mix what changed, causal origin, carrier locus, boundary crossing, and mechanism. | Redesign as orthogonal axes and classify the required fixtures without residue. |
| D15 intervention notation | **REVISE** | External analyst intervention and agent-reachable operation are conflated. | Separate `do_ext` from `enact_A`; derive reachability from a prior transition system. |
| D18 meta-admissibility | **KEEP OPEN** | The proposal does not yet state the exact relatum of `H` or its relation to `pi`, `G`, and the six steering levels. | Specify relatum, layer mapping, scope, and time semantics. |
| `Evidence_t` status | **ADOPT ONLY AS TYPED STATUS RECORD** | The taxonomy is useful, but evidence, warrant, decision, and truth must not collapse into one terminal state. | Parameterize verifier, policy, world snapshot, dependencies, and retraction. |

## 1. D5/D16: a carrier is not a single-valued function

The current proposal is approximately:

```text
carrier(C_i): Constraint -> {
  InternalState(S_in)
  | RelationState(A<->B)
  | EnvironmentRecord
  | ProvenanceDAG
}
```

This direction is valuable because FLOW needs to distinguish a constraint from the place or process through which it persists. The proposed function shape is nevertheless too weak and, in some cases, ontologically misleading.

### Problems

1. **Multiplicity is normal, not exceptional.** One constraint may be represented on several nodes, authorized by one institution, enforced by another process, evidenced by a receipt, and cached elsewhere. Conversely, one carrier may participate in many constraints.
2. **The codomain contains categories, not concrete references.** `EnvironmentRecord` does not identify which record, revision, boundary, or validity interval carries the constraint.
3. **Distinct roles are conflated.** Representation, authority, enforcement, evidence, and cache are not interchangeable kinds of carriage.
4. **The removal test is not an essence test.** Destroying one record may leave deployed enforcement intact; revoking authority may leave a stale cache active; a social norm may survive its original authors. Removal can reveal a carrier role without proving that the removed object was the unique carrier.
5. **`ProvenanceDAG` is not parallel to `InternalState`.** One is a structural evidence relation; the other names a state locus. They should not be alternatives in one flat sum type.

### Recommended shape

```text
Carries(
  carrier_ref,
  constraint_ref,
  role,
  boundary,
  valid_time
)

role in {
  representation,
  authority,
  enforcement,
  evidence,
  cache
}
```

`carrier_ref` and `constraint_ref` should be concrete, revision-addressable references. `Carries` should be many-to-many. If provenance is needed, it should qualify or evidence an instance of this relation rather than masquerade as one of its loci.

### Required countermodels

The candidate is not ready until its semantics distinguish all of the following:

- one policy duplicated across two nodes;
- a record deleted while enforcement continues;
- authority revoked while a cached policy is still applied;
- a physical constraint with no explicit record;
- a social norm that survives its initial authors;
- a relational constraint whose state is distributed across both parties.

**Disposition: REVISE before G7 adoption.**

## 2. D17: endogenous change needs orthogonal axes

The proposed three-channel synthesis does not yet solve the debt. It mixes several independent questions:

- what changed;
- where the relevant carrier is located;
- what caused the change;
- whether a boundary was crossed;
- which mechanism implemented the transition.

### Fatal counterexample

The rock case still falls through the classification:

- the rock's state `x` changes;
- the change may occur through its internal transition law `T`, under an environmental input `e_t`;
- no message needs to cross the modeled boundary;
- the change is not a self-caused choice;
- neither a constraint nor an invariant necessarily changes.

It is therefore neither adequately described as “external physical change via `M`” nor as “self-caused `Delta C` / `Delta I`.” A taxonomy that cannot classify this deliberately simple case should not become a primitive.

### Additional semantic conflations

- A choice often selects an action already present in `A(x)`; it does not necessarily install a constraint.
- A commitment may update a policy, a constraint, or future admissibility. Those effects need not be identical.
- Self-classification does not automatically become a constraint merely because the classification is about the self.

### Recommended product decomposition

```text
ChangeKind      = State | Constraint | Invariant | Policy | UpdateLaw
CarrierLocus    = Internal | External | Relational | Shared
CausalOrigin    = Self | Other | Environment | Mixed | Unattributed
CrossesBoundary = Yes | No
Mechanism       = T | e | M | pi | G | H
```

This is a starting vocabulary, not yet a claim that every axis is complete or mutually exclusive. The point is to prevent one label from silently answering five different questions.

Minimum classifications should include:

```text
rock:
  State x Internal x Environment x No x T/e

choice:
  action selection, normally without Constraint change

commitment:
  Policy and/or Constraint update, with explicit future scope
```

**Disposition: REJECT the current three-channel synthesis; preserve the source notes and redesign.**

## 3. D15/D18: intervention is not automatically agency

The proposal makes useful progress by demanding a named contrast class, provenance, and a reachable `G'`. The central remaining problem is circularity.

If a system is called reflexive because a modified `G'` is reachable, while `G'` is called reachable because self-modification is already assumed to be in the system's repertoire, the definition certifies itself.

Pearl-style `do` notation also describes an analyst's external counterfactual operation. Its mathematical availability does not imply that the modeled agent can perform the corresponding operation.

### Required distinction

```text
do_ext(G := G')  # external diagnostic intervention by an analyst
enact_A(u)       # operation actually available to agent A
```

Reflexivity should require an independently witnessed path:

```text
exists u, tau:
  u in Avail_A(x)
  tau in Reach_A(x, u)
  tau changes G
```

`Avail_A` and `Reach_A` must be derived from the transition system that existed before the reflexivity claim. The witness must not be introduced solely by the definition it is meant to satisfy.

### D18 remains open

The current text also does not yet close the meta-admissibility debt:

- What exactly is the relatum of `H`?
- How do the six steering levels map to `pi`, `G`, and `H`?
- Is an intervention scoped to a point, a trace, a regime, or a validity interval?
- Does `H` constrain updates to `G`, replace `G`, or govern which replacement operations are admissible?

These are type and authority questions, not optional explanatory prose.

**Disposition: REVISE D15; keep D18 explicitly open.**

## 4. `Evidence_t`: useful status, dangerous terminality

The proposed evidence-status distinction can prevent illegal casts, but only if it preserves these boundaries:

```text
evidence != warrant != decision != truth
```

In particular, `Settled` cannot mean context-free or irreversible truth. It should be parameterized at least by:

- verifier identity and revision;
- settlement policy and revision;
- world or dependency snapshot;
- subject and claim identifier;
- evidence closure;
- validity interval or observation time;
- invalidation and retraction conditions.

The record should inherit the repository's dependency-bound receipt and semantic-binding requirements. A green historical receipt does not become current evidence merely because its status field says `Settled`.

**Disposition: ADOPT only as a typed, retractable status record; reject any interpretation as a terminal truth primitive.**

## 5. Section B: disposition by candidate

### Adopt early, with precise revision

- **`Impossible != Forbidden`; `NoKnownPath != NoPath`.** Preserve the distinction, but separate objective modality from the observer's epistemic state.
- **Epistemic status system.** Parameterize it by verifier, policy, and world snapshot; make it non-monotonic where evidence can expire or be defeated.
- **Compositional non-admissibility.** Keep the problem, but define batch or trace admissibility, or serializability. Global context can already be part of `x`; the important question is which composition operator is being evaluated.
- **Unaccounted translation loss.** Keep as a mandatory disclosure category.
- **Mandatory invalidation condition.** Keep as an evidence/metadata contract, not as an ontological primitive.
- **`Reach_perceived != Reach`.** Keep, while representing both under-approximation and over-approximation.

### Hold or revise

- **`Urgency = -d Reach(G)/dt`.** `Reach(G)` is a set, so this derivative is undefined without a measure, topology, and time-indexed model. Use something like `-d m_t(Reach(G))/dt` only after defining `m_t`; otherwise move this item to OVERREACH.
- **Certainty monotonicity under translation.** This may hold for a specific lossy translation profile without inference or external evidence. It is not a general primitive.
- **Values as path constraints.** Values may be soft rankings, costs, defeasible commitments, or mutually conflicting considerations. Do not universalize them as hard constraints.
- **Trust/consent as capability.** A capability can model delegated authorization. It does not by itself establish trust or valid consent. Consent additionally requires capacity, informedness, voluntariness, scope, and revocability. Rename this candidate to **delegated authorization capability** unless those conditions are modeled.
- **Viability kernel.** Specify horizon, dynamics, disturbance quantifiers, and control assumptions. Authorized shutdown and corrigibility are separate normative policies, not consequences that viability theory supplies automatically.

## 6. Provenance and independence claims

The phrase “several independent notes converge” overstates the evidence.

The Monday corpus is one correlated generative trajectory. Several notes within that corpus are not independent observations. Multiple readers mining the same corpus—especially readers from the same or related model lineage—may improve recall and expose disagreements, but they do not manufacture independent validation.

Use this language instead:

> The motif recurs internally across the corpus and was recovered by multiple reading passes.

Treat recurrence as **discovery priority with zero validation credit**. Adoption should require at least one of:

- an executable witness;
- an adversarial countermodel test;
- an exact mapping to an independently developed formalism, including a translation-loss report;
- review by an independent reviewer who did not share the originating corpus trajectory.

If the document relies on “three parallel readers” as part of its method, preserve their prompts, raw outputs, model identities/versions, and synthesis procedure as source artifacts. Without those artifacts, the methodological claim cannot be audited.

There is also a temporal provenance ambiguity: the file states synthesis date `2026-08-31`, while its introducing commit is timestamped `2026-08-30T22:04:44+03:00`. Correct the date or explain the clock/time-zone/source chronology. This is minor for the mathematics but material to a repository that treats provenance as part of the claim.

## 7. Section C is the strongest section

The OVERREACH section shows the right discipline: some attractive language does not yet type, and the repository should retain the right to say so.

Keep this section. Move the urgency derivative from Section B into it until a measure over reachability and its temporal semantics are defined.

## 8. Required G7 review packets

Do not draft FLOW-0.3 adoption prose first. Produce three bounded packets whose claims can fail independently.

### G7-CARRIER

Required contents:

- a many-to-many carrier relation;
- concrete, revision-addressable references;
- explicit roles, boundaries, and validity time;
- positive fixtures;
- all six countermodels listed in Section 1;
- a statement of what deletion, revocation, and invalidation each do and do not prove.

### G7-CHANGE

Required contents:

- the orthogonal-axes matrix;
- a rule for multi-label or mixed-origin cases;
- fixtures for a rock state change, ordinary choice, commitment, external message, and internal random mutation;
- at least one negative fixture that the taxonomy must refuse to classify without additional information.

### G7-INTERVENTION

Required contents:

- separate syntax and semantics for `do_ext` and `enact_A`;
- an independently derived witness of agent-reachable self-modification;
- explicit relatum and authority semantics for `H`;
- exact mapping from the six steering levels to `pi`, `G`, and `H`;
- point, trace, regime, and time-scope distinctions where applicable.

### Shared acceptance criteria

Each packet must satisfy all of the following:

1. No debt is marked closed merely by prose.
2. Every candidate states domain, codomain, scope, time semantics, and authority boundary.
3. Every adopted rule has at least one positive fixture and one negative counterexample.
4. Glossary dispositions and FLOW changes land together, preserving D19.
5. The final adoption package receives an independent audit.

## 9. Current implementation boundary

As a limited consistency check, the prior P0 closure-season repairs were re-run at the reviewed head:

- path escape was rejected as `UNSETTLED`;
- a forged receipt produced `match: false` with reason `supplied body hash mismatch`;
- `python3 tools/receipt_freshness.py MISSION.receipt.json` reported `FRESH` with one dependency unchanged.

These checks support the bounded behavior of the current tools. They do not validate the candidate ontology, settle the debts above, or provide independent review of FLOW-0.3.

## Final status

**REGISTER: KEEP**  
**SECTION A ADOPTION: BLOCKED PENDING G7**  
**SECTION B: SPLIT INTO ADOPT-EARLY, REVISE, AND OVERREACH**  
**SECTION C: KEEP AND EXPAND**

The important move now is not to make the vocabulary sound more complete. It is to make each proposed primitive expose exactly what could falsify, underdetermine, or revoke it.
