# KELVIN-LAYERS-0.1 — Temperature as declared remaining obligation

**Status:** design draft / proposal. Not repository policy, not a version scheme anyone has adopted,
not a list of layers to freeze. Nothing in any repository changes because this file exists.

**Origin:** the owner proposed Kelvin versioning (Urbit's countdown-to-zero scheme) and "temperature
layers" on 2026-09-02, and noticed that `0K` reads as **OK** — a layer with no open obligation.
Written by Claude Fable 5.1 the same day, against the state recorded in
`trajectory-audit-fable-5.1-2026-09/`. The crossing rule applies: nothing here inherits credit from
Urbit, from the audit, or from the repositories it describes; every claim about a layer below is
`OBSERVED` from a path or marked otherwise.

**Principle in one sentence:**

> A layer's temperature is the number of normative changes its owner still admits owing it;
> it only counts down; `0K` means no open edge remains — the layer is *OK*, which says nothing
> about whether it is *right*.

---

## 0. Why this is worth a draft

Three facts from the audit, none of which SemVer expresses:

1. `sigma-glyph/spec/VERSIONS.md` carries **six version numbers in three schemes** and needs a
   tool (`version_check.py`) to say which means what. A Book can sit at 0.6.0 inside a v0.7.0
   bundle and both are correct. The numbers describe the past; none states how much future change
   the owner still expects.
2. `warrant/SPEC.md` §13.1 already contains a Kelvin rule without the name: "*A tag is immutable. A
   semantic change … is a NEW tag, never a redefinition. `ski@v1` names Book I v0.5; Book I v0.6
   would be `ski@v2`.*" `ski@v1` is at `0K` by construction. The rule applies to runtime tags only;
   nothing says which other surfaces are meant to be that cold.
3. The W1 episode: the evaluator behind the immutable `ski@v1` tag was swapped for a v0.7.0-era
   module without a SPEC change, and the provenance record names `adopted_bundle: v0.7.0`. Vector
   agreement is 66/66; a closed-domain equivalence is unproven. A frozen *name* over a moving
   *implementation* is exactly the case a temperature scheme has to make visible, because SemVer
   has no slot for "this may not move at all".

And one structural fact: `spec/GOV-anchors.md` is STANDARD — the coldest thing the stack claims —
and it depends on warrant records, the `warrant-sig-v1` message and a verify CLI from a SPEC marked
v0.4 DRAFT with an open settlement defect (expect-flip). **The cold depends on the hot.** SemVer
cannot say this is wrong. A dependency rule over temperature says it in one line.

---

## 1. Definitions

### 1.1 Layer

A **layer** is a named normative surface with (a) anchored bytes or a closed schema, (b) a
conformance predicate a stranger can run, and (c) a declared owner. A layer is **not** a repository,
a file, a release bundle or a package. Repositories are containers of layers at different
temperatures; a bundle is a *set* of layer states, as `spec/ANCHORS.txt` already treats it.

### 1.2 Temperature

`T(L) ∈ ℕ` — the owner's declared upper bound on the number of *normative* changes still owed to
layer `L`. Equivalently, following Monday 0040 ("obligation = memory with an open edge"): the number
of open edges the owner admits on that layer's contract. `T` is a **declaration about the future**,
signed, and therefore a hypothesis about the owner's own behaviour (OPERATOR-AS-HYPOTHESIS: the
owner's word is a class-(c) anchor — legitimate, and booked explicitly, not assumed).

Rules:

- `T` only decreases. A decrement is a governance act (§4), never a commit message.
- `T = 0` ("`0K`", "OK"): no open edge; the layer's bytes and semantics are frozen under this name.
- Breaking a `0K` layer is impossible by definition; what happens instead is a **new name**
  (`ski@v2`, `verify-report@v1`) with its own temperature. This is §13.1 generalised.
- `T` is per layer. Two layers in one file can have different temperatures; then the file is not
  the unit and should be split, or the colder part anchored separately.

### 1.3 What temperature is not

- Not validation. `0K` says the owner has stopped moving it; not that it is correct, adequate, or
  reviewed. Freeze ≠ validation exactly as retirement ≠ refutation (CONTROLLED-FORGETTING I5).
- Not maturity in the marketing sense. A hot layer can be excellent; a cold one can be wrong and
  merely finished.
- Not a per-repository score. A repository has no temperature.

---

## 2. The dependency rule

> A layer may depend normatively only on layers **at least as cold** as itself:
> for every normative dependency `D` of `L`, `T(D) ≤ T(L)`.

"Normative dependency" = `L`'s conformance predicate cannot be evaluated without `D`'s bytes or
semantics (the `runtime_depends_on` / `conforms_to` edges of the audit's edge ledger). Citation,
co-development, and experiments are not dependencies for this rule.

Consequences:

- Freezing proceeds bottom-up. You cannot honestly declare `GOV-anchors` at `0K` while the warrant
  signature message it verifies with is at some `T > 0`.
- An **inversion** (`T(D) > T(L)`) is not forbidden on day one; it is *named*. The first job of the
  scheme is to list inversions, not to fix them.
- Swapping the implementation under a `0K` name is allowed only with an executable equivalence gate
  on the closed admitted domain (the W1 obligation); otherwise it is a re-warm, and re-warms do not
  exist — the honest move is a new name.

---

## 3. Candidate temperature map (observed classes, no numbers assigned)

Numbers are the owner's to declare. What can be observed today is the *class* each layer already
behaves as. Sources: the audit's `02-CANONICAL-OWNERSHIP-MATRIX.md`, `03-SEMANTIC-BREAKS.md`,
`03-CROSS-REPO-EDGE-LEDGER.json`.

| Layer | Owner surface | Observed class | Why | Inversions / notes |
|---|---|---|---|---|
| Σ-GLYPH Book I byte layer: node serialization, §4.1 validation, NodeHash, genesis atoms | `sigma-glyph/spec/book-1-truth.md` §4–5 + `MachineBytes.lean`, `Sha256.lean` | **cold** (candidate for first declared `T`) | unchanged across v0.5→v0.7; Lean-pinned; 49 vector ids identical between v0.6.7 and v0.7.0 | none |
| Book I evaluation semantics (hash-thunk, size-priced ATP, three exits) | Book I §3 + `EvalMachine.lean` | **cold-warm** | results unchanged on all 66 eval vectors; *interface* changed 08-30 (env input, Receipt) | the interface change was a real break (B4) — temperature must count interface, not only results |
| `ski@v1` runtime tag | `warrant/SPEC.md` §3.1, §13.1 | **`0K` by rule** | tag immutable; "later Book I is a different tag" | **inversion by implementation**: bundled evaluator moved (W1) without a name change; provenance says v0.7.0, SPEC says v0.5 |
| `warrant.verify-report@v0` | `warrant/SPEC.md` §11 | **`0K` by rule** | "CLOSED schema … any additive field ships under a new tag" | consumers (oaip, sev) rely on exactly this property |
| Warrant record core: body schema `0.1/0.2`, JCS §4, WarrantID, `warrant-sig-v1` message, integer domain | `warrant/SPEC.md` §2, §4, §5 | **cold candidate** | two protocol breaks in July (B1, B2); none since; every sibling pins it | GOV-anchors (STANDARD) depends on it → this is the layer whose freeze unblocks the inversion below |
| Warrant settlement §7, §9, key-state §5.1 | `warrant/SPEC.md` (v0.3 DRAFT) + WRT-005 | **hot** | expect-flip open; WRT-005 unadopted; Lean covers the rule's algebra, not any verifier | must stay hot; assigning a number here would be theatre |
| GOV-anchors (threshold adoption of anchor sets) | `sigma-glyph/spec/GOV-anchors.md` v1.0.2 STANDARD | **declared cold, actually inverted** | depends on warrant core (cold candidate) *and* on the warrant verify CLI at a pin (hot tooling) | first target for the dependency check |
| Book II (wave), Book III (federation) | sigma-glyph spec | **warm** | moved 0.6.1→0.7.0 (oracle precedence removed); one exercised consumer | Book III depends on warrant v0.3 records → inversion candidate |
| OAIP record types + cardinal rule | `oaip/SPEC.md` v0.1 | **hot, dormant** | one implementation; pinned to a pre-0.9.0 warrant; SPEC still says int64 | dormancy is not coldness: an unmaintained hot layer is the most dangerous class |
| Trinity CNP-0-JCS (RFC-0003 Tranche A3) | `trinity/docs/rfc/0003/01-…` | **warm** | ratified by steward; reuses warrant's JCS profile *by path* | depends on warrant core without a pin → temperature undefined until pinned |
| Agent-autonomy policy, settlement policy, gate tooling | `warrant/policies/*`, `tools/*` | **hot by design** | operational; should never carry a temperature | — |
| Manifesto drafts (FLOW, RVB, AIE, this file) | `manifesto/drafts/*` | **hot by design** | "speculative working model"; retract freely | a temperature here would contradict the manifesto's own genre |

Reading the table: the stack already has two `0K` layers by rule, one cold candidate that nobody has
named as such (the warrant record core), and one advertised-cold layer sitting on hot ground. That is
the whole diagnosis a temperature map buys, and it is available before any number is declared.

---

## 4. The decrement as a governance act

A decrement closes one admitted obligation. It is recorded, not announced:

```yaml
type: KelvinRecord
schema_version: manifesto.kelvin.v0
layer:
  name: warrant-record-core
  owner: s0fractal/warrant
  anchored_bytes: [SPEC.md §2, §4, §5 at <commit>, examples/canon-vectors.json <digest>, examples/signature-vectors.json <digest>]
temperature: { from: 3, to: 2 }
obligation_closed:
  summary: "integer domain fixed at ±(2^53−1); no further canonical-bytes change admitted"
  evidence:
    - kind: conformance
      locator: conformance pack 1.1.0, vectors <ids>
    - kind: review-finding
      locator: reviews/<file>
remaining_obligations:          # what T still counts
  - "signature-creation-time row in the threat model (SA proposal)"
  - "…"
dependency_check:
  colder_or_equal: [sigma-book1-bytes]
  inversions: []                 # or listed, never omitted
authority:
  warrant: <threshold warrant id>   # the roster act, as for anchor-set adoption
```

Properties:

- `remaining_obligations` is mandatory and non-empty unless `to: 0`. A temperature without the
  list of what it counts is a number, not a declaration (failure mode F1 below).
- The record is a Warrant record like any adoption; `T` is therefore itself under the stack's
  own governance and inherits its custody caveats (SA-5, SA-5b). A decrement signed by one custody
  is one custody's promise.
- Reaching `0K` is the same act with an empty remaining list. The owner says **OK**: no open edge.
  Monday 0040 in one glyph.

---

## 5. Relations to existing disciplines

- **CONTROLLED-FORGETTING-0.1.** Two ends of one instrument: forgetting reduces the number of
  *past* surfaces admitted into context; temperature reduces the number of *future* changes admitted
  to a layer. Both change admission, neither changes truth. A frozen layer is the easiest thing to
  retire *around*: its consumers pin a `0K` name and never need a migration record.
- **OPERATOR-AS-HYPOTHESIS.** A temperature is the owner's forecast about the owner. It is a
  class-(c) input booked explicitly. The dependency check is what keeps it from being merely
  performative: a forecast that contradicts the dependency graph is refused at the map.
- **The crossing rule.** Temperature carries no credit across repositories. Consuming a `0K` layer
  transfers "these bytes will not move under this name" and nothing else.
- **Warrant §13.1.** This draft changes nothing there; it proposes that the runtime-tag rule become
  the general rule for every layer that wants to be called cold.
- **Urbit.** The scheme is borrowed in shape (countdown, colder-only dependencies). It is not
  borrowed in ambition: Urbit freezes a kernel it intends to be the last one; this stack freezes
  contracts so that siblings can pin them. Nothing here claims Nock-like permanence for anything.

---

## 6. Failure modes

| # | Failure | Control |
|---|---|---|
| F1 | **Theatre Kelvin** — numbers assigned without an obligations list | a KelvinRecord without `remaining_obligations` is invalid |
| F2 | **Freeze as validation** — `0K` read as "verified" | every `0K` carries the same non-claims the layer already states; the map prints validation status in a separate column, never merged |
| F3 | **Hidden re-warm** — implementation swapped under a frozen name (the W1 shape) | provenance record must reference the layer name and temperature; an implementation change under `0K` needs an equivalence gate or a new name |
| F4 | **Inversion laundering** — a hot dependency hidden as "tooling" | the dependency check reads the conformance predicate's actual inputs (pins in CI), not the prose |
| F5 | **Temperature by repository** — "warrant is 12K" | the schema has no repository field for `layer.name`; repos are owners, not layers |
| F6 | **Obligation inflation** — padding the remaining list to avoid `0K` | remaining obligations must each name a falsifier or a consumer that would fall; decoration is a review finding |
| F7 | **Kelvin bureaucracy** (the RVB objection) | no record for hot layers; records only at decrements; the map is one generated table |
| F8 | **Cold dormancy** — an unmaintained hot layer mistaken for a cold one (OAIP today) | dormancy is a separate observed field; `T` is declared, never inferred from inactivity |

---

## 7. Minimal rollout

- **Phase 0 — this document.** No layer gets a number.
- **Phase 1 — the map.** One generated table in `protocol-ecosystem` with columns: layer, owner
  surface, observed class, declared `T` (empty), dependencies, inversions. Generated from CI pins
  and anchor files, not hand-written. Expected output: the two `0K`-by-rule layers, the warrant-core
  candidate, and the GOV-anchors inversion.
- **Phase 2 — the falling check.** One CI job in the map repo: fail if any layer with declared `T`
  depends on a layer with greater `T` or with no declared `T`. Before any declaration it runs green
  vacuously; that is acceptable only because Phase 3 follows.
- **Phase 3 — one decrement.** Choose the warrant record core. Write its `remaining_obligations`
  honestly (the threat-model row, the int-domain follow-ups, whatever the reviews still hold open).
  Declare `T` by roster warrant. The check now has a subject.
- **Phase 4 — resolve the inversion.** Either GOV-anchors depends only on the now-declared warrant
  core (and the verify CLI becomes a pinned *tool*, not a normative dependency), or GOV-anchors
  declares itself warm. Both are honest; the current state is neither.
- **Not planned:** freezing settlement, OAIP, Books II/III, or anything in `manifesto/drafts`.

---

## 8. Falsifiers of the design

Drop or simplify this draft if:

1. the Phase 1 map shows no inversion and no cold candidate — then SemVer plus §13.1 was enough;
2. declared temperatures are broken (re-warmed) within a quarter without a new name — the forecast
   channel is not credible from this owner and should not be published;
3. the obligations lists become longer than the specs they annotate (F7);
4. consumers do not change behaviour — nobody pins by layer name where they pinned by commit;
5. the W1-class question ("is the implementation under the frozen name equivalent?") turns out to
   need a proof the stack cannot produce; then `0K` names should be reserved for byte-level layers
   only and evaluation semantics stay warm indefinitely.

---

## 9. Shortest form

```text
temperature  = admitted remaining obligations on a layer
decrement    = one obligation closed, by roster act, with evidence
0K           = no open edge = OK (not: correct)
dependency   = only on layers at least as cold
frozen name  + moved implementation = re-warm → new name, or an equivalence gate
repositories have no temperature; layers do
```

---

## Appendix A — Lore (non-normative; status `SPECULATION` unless marked)

Recorded because the owner supplied it on 2026-09-02 as a precedent, and because dialogue
provenance is preserved here rather than absorbed (sigma-glyph-world `PROVENANCE.md` rule:
a dialogue is evidence of a conversation, not evidence for the claims inside it).

**The 64-zone scheme (owner's recollection, ~2025, with Claude and Gemini).** Sixty-four zones
on one axis. Zone 32 (≈ π·10) was "near-zero temperature, but runtime". Zones 32–64: fast and
ephemeral — tweets, passing thoughts. Zones 0–32: "negentropy" — mathematical invariants that
*deconstruct and redirect the energy* of the warm zones. The white and black cones of Thesis 7
were then pictured as a black hole with a hyperbolic surface and horizons. No artifact of this
scheme is in any repository this draft can cite; it is attributed recollection, `UNKNOWN` in every
provenance field.

**What this draft takes from it (one thing).** The old scheme was *dynamic* where §3's map is
static: warm material is **fuel** for cold layers. A decrement (§4) is exactly the moment when
warm-zone material — drafts, reviews, gate rounds, counterexamples, tweets — has been digested
into one closed obligation. The cold layer grows by consuming the warm; it does not grow on its
own. That is Thesis 7's black cone stated in temperature terms, and it gives §4 its missing
input: a KelvinRecord's `evidence` list *is* the digested warm material. `DERIVATION` from the
draft's own definitions, once the recollection is granted as a premise.

**What it does not take.** (1) The number 64 and π·10: decoration; the operational content is
three bands — ephemeral / runtime-near-zero / invariant — and §3 already has them as hot / `0K`-by-
rule / cold. (2) Temperature as a property of *content* ("this thought is ephemeral"): here it is
a property of the owner's *commitment*, which is the only thing that can be signed. (3) The
black-hole geometry: not because it is wrong, but because Book II's wave layer and `spec/LORE.md`
already hold that cosmology as a non-normative view, and this draft should not mint a second one.

**One observation the precedent makes sharper.** "Near-zero but runtime" at the boundary is
precisely `ski@v1`: a frozen name with a running implementation underneath. The old scheme put
that boundary at a single zone; the W1 episode shows why the boundary needs an equivalence gate
rather than a coordinate.
