---
title: "Budgeted Equality by Normal-Form Address: A Cost Gap, an Executable Soundness Boundary, and a Blocked Admitted-Domain Contract"
subtitle: "Revising the “Addressing Is Equality” Idiom"
status: v0.2 replacement draft — NOT the canonical paper.md; not deposited; not peer-reviewed
supersedes: paper.md (v0.1, "Addressing Is Equality", now carrying errata)
author: "<AUTHOR_PLACEHOLDER>"
date: "<DATE_PLACEHOLDER>"
keywords: [normal-form address, content-addressing, Church encoding, budgeted evaluation, equality settlement, admitted domain]
evaluator: "sigma-glyph==0.6.7 (published wheel)"
profile-implementation: "ADR-011 reference implementation at sigma-glyph commit 196c45a2f9074a472b96af1a6bae2c67533edbb1 (v0.6.7-175-g196c45a) — DRAFT, unreleased"
license: CC-BY-SA-4.0
---

> **Draft status.** A from-scratch replacement written from the evidence boundary inward (see
> `CLAIM-LEDGER.md`), not the v0.1 body under an errata banner. This is an **incident-and-repair
> note**, not a claim that the method is realized on an admitted domain. `paper.md` (v0.1) is
> retained as a historical comparator; see `MIGRATION-NOTES.md`. CC BY-SA 4.0 under the
> repository's path-scoped license; no deposit, DOI, or claim of adoption is made here.

## Abstract

Equality of canonical data need not be *computed in the language*; the "addressing is equality"
idiom instead reduces both sides to a canonical normal form at a generic observation point and
compares content addresses. On one tested evaluator the in-language Church comparator (measured
below to be `EQN(m,n) = AND(LEQ(m,n), LEQ(n,m))`, **not** `ISZERO∘SUB`) cost 260,780 ATP at 3+2 and
exhausted a 50-million budget at 7+5, while the address idiom settled 7+5=12 for **601 ATP**. That
figure belongs to a **permissive research harness** (`tools/glyphlib.py`), which admits any lambda
expression and has no admission, profile commitment, or two-sided receipt. The safety machinery
that would make the idiom trustworthy lives in a **DRAFT, unreleased** Sigma-Glyph proposal
(ADR-011, `church@v0`) at commit `196c45a` — 175 commits after the `v0.6.7` evaluator these
measurements use — and that profile **refuses `PLUS 7 5`**: it admits only written numerals, so
*no single implementation in the deposit both admits the motivating computation and emits the
budgeted two-sided receipt.* That gap is the paper's most trustworthy result, not an embarrassment:
the executable soundness boundary — Church zero settles PASS-equal to a constant function that
names the observation marker — forced an admitted-domain contract that remains **blocked on
computed terms**. Soundness and completeness are therefore stated as **profile obligations /
argued conjectures** on an admitted domain, not established propositions; budget exhaustion is an
*unsettled* outcome carried in the receipt, never inequality; higher-order equality is out of
scope. The one statement that survives unconditionally is narrow and renamed accordingly: a
**hash-relative observation identity** — two `normal_form` exits with the same result hash returned
one canonically-addressed result, modulo SHA-256 and evaluator correctness — which says nothing
about the terms evaluated. A named Warrant pack re-executes one stored SKI check (2,108 ATP) while
the pack as a whole is `LEGACY_UNPINNED`; this is conformance, not adoption or a proof of the
semantic claim. What we propose is a specification note and a failure boundary, not a new primitive
or a standard.

## 0. What this paper does and does not establish

| It establishes (for the tested evaluator / stated profile) | It does NOT establish |
|---|---|
| In-language Church equality was orders of magnitude costlier than comparing normal-form addresses. | That "addressing **is** equality" unconditionally, or for functions. |
| The gap motivates an interface idiom for canonical data. | That the idiom is "linear" as a general complexity result. |
| An **executable** counterexample refutes unconditional soundness when inputs can name the marker. | That equal addresses prove equal inputs. |
| An admitted-domain **contract** (soundness/completeness obligations) is *written down and argued*. | That soundness/completeness are **proved**, or hold beyond written numerals. |
| The DRAFT profile `church@v0` refuses the motivating `7+5` case — a real, reproduced boundary. | That any released profile can settle the motivating computation (none can). |
| Budget exhaustion is an *unsettled* outcome, carried in the receipt with both exit kinds. | That budget exhaustion means inequality. |
| One stored SKI check re-executes inside a named Warrant pack (conformance). | That a Warrant pass proves the theorem, that the pack strict-replays, or that anyone upstream adopted it. |

**Two surfaces, kept separate throughout.** The headline cost figures come from the **permissive
research harness** `tools/glyphlib.py`, which admits *any* lambda expression and carries no
admission or receipt machinery. The safety machinery lives in `church@v0` — **ADR-011, a DRAFT
proposal / reference implementation at Sigma-Glyph commit `196c45a2…` (`v0.6.7-175-g196c45a`),
non-normative, not gated, not adopted, and blocked on `PLUS 7 5`.** It is *not* in the published
`sigma-glyph==0.6.7` wheel (`git ls-tree -r v0.6.7` contains no ADR-011, `equality_profile.py`, or
`church@v0`). Every number below is labeled with the surface that produced it; none is presented as
a released-profile fact.

## 1. Incident and measured problem

Computing equality of canonical data *in the language* is combinatorially expensive on the
reference SKI machine. The exact comparator executed in `tools/glyphlib.py` is **not** `ISZERO∘SUB`;
it is a two-sided order conjunction:

```text
LEQ(m,n) = ISZERO(SUB(m,n))
EQN(m,n) = AND( LEQ(m,n), LEQ(n,m) )
```

With truncated Church subtraction the one-sided `LEQ` is an *order* predicate, not equality; only
the conjunction decides equality, and the cost figures below are for that exact `EQN` term (bound
by AST hash in `DEPOSIT-AND-AUDIT.md`). Comparing the **addresses** of the two canonical normal
forms is much cheaper:

| terms | in-language `EQN` (ATP) | address idiom (ATP) | surface |
|---|---|---|---|
| 3+2=5 | 260,780 | — | permissive harness |
| 5+5=10 | 26,212,480 | — | permissive harness |
| 7+5=12 | **> 59,452,030 — `ATP Exhausted`** (exhausts a 50-million budget) | **601** | permissive harness |
| 200+200=400 | — | 19,997 | permissive harness |

The idiom's advantage at two digits is about five orders of magnitude *on the permissive harness*.
That is the engineering motivation — and the ceiling on what it proves. It is **not** a complexity
theorem, and **nothing in CI protects the shape of the curve**.

## 2. Method, and the two surfaces

An equality settlement fixes six things before it runs:

- **observation context** — a profile-defined generic point `O(n) = n F X`, applying an admitted
  term to two inert markers so it reduces to a constructor spine `Fⁿ(X)`, injective in `n`;
- **admitted domain** — which terms the profile will accept (below);
- **intended equivalence relation `~`** — see §4 for its exact definition; address identity is a
  *candidate decision procedure* for `~`, not its definition;
- **address / hash anchor** — the content address of the normal form (modulo SHA-256);
- **exit kinds** — see the typed outcome table below;
- **budget policy** — each side normalized under its **own full budget**, independently.

**Typed outcomes (do not conflate the four vocabularies).** The permissive harness, the DRAFT
profile settlement, the evaluator, and the invariant checks each speak a different language:

| evaluator exit | harness comparison | profile settlement (ADR-011) | meaning / credit |
|---|---|---|---|
| `normal_form` + equal hash | (equal addresses) | `EQUAL` | both sides normalized; addresses match — backs equality only on the admitted domain |
| `normal_form` + unequal hash | `VIOLATION` | `UNEQUAL` | both normalized; addresses differ — the harness label is `VIOLATION`, the profile verdict is `UNEQUAL` |
| `ATP_EXHAUSTED` | (n/a) | `UNSETTLED` | a side did not normalize in budget — never inequality |
| — | (n/a) | `REFUSED` | term outside the admitted domain (e.g. `PLUS 7 5`, or a term naming a marker) |
| resource/shape fault | (n/a) | `FAULT` | malformed shape / resource fault — a non-verdict |

`VIOLATION` is an *ordinary* permissive-harness result for unequal observed addresses; it is **not**
a profile verdict. `FAULT`, `REFUSED`, and `UNSETTLED` are non-verdict outcomes. The receipt schema
must keep these columns distinct.

**`church@v0` admitted domain (DRAFT profile, commit `196c45a`).** A closed grammar with exact
arity, string binder names, binder distinctness (`λf.λf.…` and `λx.λx.x`=church 0 both refused), and
freshness: markers `F = SHA-256("sigma-glyph/adr-011/church@v0/F")`, `X = SHA-256(".../X")` are
fixed by the profile id before submission, so any term that *names* a marker is refused. Numerals
are admitted **as written** (0–8 confirmed by selftest). **Computed expressions are refused** —
`PLUS 7 5` does not pass admission, so `church@v0` **cannot settle the motivating case.** The
profile's current selftest is strong (`ADR-011-SELFTEST: ALL PASS (72/72)`, including admission,
per-side budget, profile commitment, anchor, malformed-shape and mutation controls) — but a passing
selftest on an unreleased DRAFT is implementation evidence, not a release fact. The profile is
*correct and insufficient*; a pre-registered experiment (`EXP-ADR011-01`) is on file to try to close
the admission gap.

## 3. Failure boundary first

The contract in §4 only makes sense against its boundary, so the boundary comes first.

**3.1 Marker collision (executable — refutes unconditional soundness).** Church zero
`a = λf.λx.x` and the constant function `b = λf.λx.X`, where `X` is the observation marker, settle
**PASS-equal at 27 ATP** — both reduce to the same address at `(F,X)` (`8785b7dd…` on the permissive
harness; the `church@v0` analogue collides at `e37391c4…`). At a second observation point `(F,Y)`
they differ. **Equal addresses prove identity of what came back, not equality of the inputs.** Three
mutations bound the claim: adding a marker-refusing admission flips the verdict to `REFUSED` (M1);
naming a *non-marker* literal yields `VIOLATION` with non-equal addresses (M2); a third control (M3)
flips its intended control as expected — so the collision is about naming *this profile's* marker,
not constant functions in general.

**3.2 Higher-order incompleteness.** The normal form is canonical only for first-order data at a
generic point. Two extensionally equal functions can have different admitted normal forms; η-equal
or higher-order terms are **out of scope**. "Addressing is equality" is at best a statement about
canonical first-order data and a falsehood about functions.

**3.3 Nontermination is priced, not decided.** `ATP_EXHAUSTED` on either side is a canonical
`UNSETTLED` outcome, never inequality. The receipt must carry both exit kinds: the stored form
`DISSONANCE(ATP Exhausted)` shares one address across runs (`8bb0006f…`), so without the exit check
`church(3)` vs `church(5)` at a tiny budget would falsely settle "equal". Sequential budget (second
side gets `atp − spent_left`) is a defect: it makes `church(12)` settle "UNEQUAL to itself" and
flips with argument order. Each side gets the full budget independently.

**3.4 Hash-collision assumption and profile/evaluator drift.** Soundness is "modulo SHA-256 and the
correctness of the implementations". The `profile_commitment` holds **within one Python module**
(verified on CPython 3.12 and 3.14 only); **no second implementation exists**, so
cross-implementation / cross-agent settlement is BLOCKED, and the linearity is harness-relative.

## 4. The admitted-domain contract (obligations, not proofs)

Let the intended relation be named exactly: for admitted first-order terms `a`, `b`, write `a ~ b`
iff they denote the same Church-encoded value — i.e. `β`-normalizing `O(a)` and `O(b)` yields
`α`-equal constructor spines `Fⁿ(X)`. This is the relation the address idiom is *supposed* to
decide; the propositions below are the **contract that a real admitted profile would have to
discharge**, stated as obligations because no deposited implementation both admits the motivating
family and proves them:

- **(Obligation) Domain-scoped soundness (reflection).** *On the admitted domain*,
  `same_address(O(a),O(b)) ⇒ a ~ b`, under the marker-freshness and collision assumptions. Would
  back an `EQUAL` verdict only for admitted terms. **Argued, not proved** (§3.1 shows it fails the
  moment admission is dropped).
- **(Obligation) Conditional completeness (preservation).** *Where the normal form is canonical for
  `~`*, `a ~ b ⇒ same_address(O(a),O(b))`. Would back `UNEQUAL`. Out of scope for higher-order
  equality. **Argued, not proved.**
- **Both inherit the correctness of the λ→SKI compilation, for which there is no general proof
  here.** Testing written numerals 0–8 is implementation evidence, not a domain-wide proof.

**The one unconditional statement (renamed).** Formerly "the Σ-lemma / the only unconditional
statement", it is precisely a **hash-relative observation identity** (a kernel representation
invariant under named assumptions): two evaluations that both exit `normal_form` with the same
result hash returned one canonically-addressed result, **modulo SHA-256 and evaluator correctness**,
under a fixed canonicalization / result-encoding regime. *It says nothing about the terms
evaluated*, does not establish that the result is the correct normal form, that two implementations
agree, or that the address is collision-free. "Unconditional" is reserved for a syntactic tautology
inside a fixed formal model; this is not that.

## 5. Measurements

Address idiom (permissive harness), exact ATP:

| terms | ATP | terms | ATP |
|---|---|---|---|
| 7+5=12 | 601 | 6×7=42 | 2,213 |
| 20+20=40 | 1,997 | 20×20=400 | 21,453 |
| 100+100=200 | 9,997 | 200+200=400 | 19,997 |

In-language `EQN = AND(LEQ,LEQ)` (permissive harness): 260,780 (3+2); 26,212,480 (5+5); exhausts
50M at 7+5. The observed idiom cost over the measured range is ≈50 ATP/unit **on this harness**. On
`church@v0`'s admitted family the per-unit cost of the *admitted numerals* is ≈37 ATP/unit — but
that family excludes the computed `7+5`, so it is not a substitute measurement of the motivating
case. These are **observed points over a measured range**, labeled as such — not extrapolated to a
general "linear" law. Commands re-derive every figure (see `DEPOSIT-AND-AUDIT.md`), which also binds
each figure to the exact executed term hash.

## 6. Prior art and novelty (OPEN)

The components are classical, and each source supports only the exact adjacent relation:

- **Hash-consing / structural sharing** — Ershov 1958 [@ershov1958]; Filliâtre–Conchon 2006
  [@filliatre2006] supports type-safe hash-consing and structural equality, the *narrow* relation
  "identical structure ⇒ shared address". It is the right authority for the address-sharing
  mechanism, not for semantic equality of computed values.
- **Normalization by evaluation** — Berger–Schwichtenberg 1991 [@berger1991] supports NbE
  (evaluation followed by readback) for the typed λ-calculus. It does **not** by itself establish
  that this exact *untyped Church-numeral* `O(n)=nFX` probe is "the" NbE observation trick; that
  connection is our analogy, flagged as such.
- **Content-addressing** — Merkle 1987 [@merkle1987] is a hash-based *digital-signature*
  construction; it is **not** a direct authority for content-addressed result-identity as phrased,
  and is cited only for the hash-tree lineage.

**Novelty candidate (narrow, treated as OPEN).** The candidate is the **budgeted, receipted
composition** — an equality settlement carrying both normal-form addresses, both exit kinds, the
ATP spends, and the machine/profile identity as the verdict. But the deposit does **not** currently
contain that composition end-to-end: the included Warrant pack is one-sided and `LEGACY_UNPINNED`,
and the two-sided implementation lives only in the external DRAFT proposal, which the manifest does
not yet vendor or pin by full content closure. **Novelty is therefore OPEN pending external
prior-art review**; a search log is required in `DEPOSIT-AND-AUDIT.md`. Falsifier F1: if the
composition reduces to an existing published technique, the novelty claim is withdrawn.

## 7. Downstream execution (conformance, not adoption)

The idiom re-executes inside a named Warrant evidence pack (`drafts/ssd-pack/`): a stored `aie`
check re-runs `(PLUS 74 1) F X → F⁷⁵(X)` to **PASS at 2,108 ATP**
(`warrant check 0597575d…`), and `warrant verify --settlement` reports 4 records, 0 errors, 0
warnings. **But the pack as a whole is historically sealed and records no dependency closure:**
`python tools/replay_pack.py replay drafts/ssd-pack` returns `REPLAY: LEGACY_UNPINNED` (exit 1).
Both credits are reported and neither cancels the other — a stored check re-executes, while the
complete historical bundle is not strict-replayable. What this shows: the `ski@v1` check format
permits a non-boolean `expect`, and one stored check re-executes. What it does **not** show: a
two-sided equality receipt (it is *one* execution against a constant, not two compared), domain
soundness, upstream endorsement, or adoption. Any dependency-closed pack must be a **new** artifact,
not repaired history. ADR-011 is a DRAFT proposal at commit `196c45a`; it is **not accepted,
deployed, or standardized**, and the profile it proposes cannot settle the case the proposal exists
for.

## 8. Errata history and epistemic status

The v0.1 body claimed equal addresses ⇒ equal values **unconditionally** and presented the 601-ATP
figure as *the* cost of the idiom. Both were repaired: soundness is now an admitted-domain
*obligation* (the collision counterexample runs on this repository's own evaluator), and 601 ATP
belongs to the permissive harness. Of eleven errata checks, **four correction IDs are executable
(C2, C5, C6, C11)** and **seven are documentation-only (C1, C3, C4, C7, C8, C9, C10)**; the check
suite is 8 controls + 3 mutations, and its own banner states it decides four of eleven IDs, not
eleven corrections. The binding is content-addressed: source `sigma-glyph@81ff660…`, correction
sha256 `ccd0ced4…`, ADR preserved-original sha256 `44c96961…`, Book I anchor `e3e5d008…` (v0.6.0,
adopted in anchor-set v0.7.0). **The repair trajectory is part of the publication, not a footnote to
hide.**

## 9. Artifact map, typed falsifiers, provenance

- **Evaluator (released).** Reference SKI machine `sigma-glyph==0.6.7` (published wheel); permissive
  harness `tools/glyphlib.py`.
- **Profile implementation (DRAFT, unreleased).** ADR-011 reference implementation at Sigma-Glyph
  commit `196c45a2…` (`v0.6.7-175-g196c45a`) — must be vendored/pinned into any deposit, with its
  license; it is not in the `0.6.7` wheel.
- **Checker.** `check_claims.py` re-runs the benchmark matrix; `tools/aie_errata_check.py` runs the
  collision counterexample and its mutations. (Both require the closed-manifest repair in
  `DEPOSIT-AND-AUDIT.md §A`; the ADR check must not depend on an absolute author-machine path.)
- **Falsifiers (typed — only `integrity_break` and `within-sample_counterexample` falsify a claim
  as stated).**

  | id | condition | type |
  |---|---|---|
  | F1 | the budgeted composition reduces to published prior art | `open_obligation` (novelty is OPEN, not a falsifier) |
  | F2 | a first-order canonical false-inequality on the admitted domain | `within-sample_counterexample` |
  | F3 | a compiler within ~10× collapses the cost argument | `competitive_result` |
  | F4 | Warrant execution read as endorsement | `misuse_warning` |
  | F5 | a released profile settles the motivating case at costs contradicting the gap | `scope_boundary` / `replication_failure` |
  | F6 | the collision counterexample fails to settle PASS-equal on a clean evaluator | `integrity_break` |
  | F7 | a benchmark ATP figure fails to re-derive from the exact executed term hash | `integrity_break` |

- **Provenance.** Produced with Anthropic's "Fable 5" generation; exact date, author, and revision
  are `<…_PLACEHOLDER>` until deposit.
- **Licensing.** This paper and its documentary artifacts are CC BY-SA 4.0; executable software in
  the deposit is AGPL-3.0-only. The repository `LICENSE` is the scope authority; the vendored
  ADR-011 snapshot carries its own upstream license.
