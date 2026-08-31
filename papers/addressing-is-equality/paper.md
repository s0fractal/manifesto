---
title: "Addressing Is Equality: Settling Equality of Canonical Data by Normal-Form Address in a Budgeted Content-Addressed Machine"
author: "Serhii Glova (independent) — sergey.glova@gmail.com"
date: 2026-08-30
keywords:
  - content-addressed computation
  - hash-consing
  - normalization by evaluation
  - combinatory logic
  - deterministic evaluation
  - verifiable computation
classification: cs.LO, cs.PL, cs.CR
bibliography: references.bib
---

# Abstract

In a content-addressed machine with deterministic, total, budget-priced
evaluation, equality of canonical data does not need to be *expressed*; it
can be *settled*: reduce both sides to canonical normal form and compare
addresses. We state the idiom precisely — soundness holds only on an admitted domain (NOT unconditionally: see the correction below)
(modulo the hash function, which sits in the trust anchor); completeness
holds **only** where the normal form is canonical for the equivalence class
in question (first-order data at a generic point, not higher-order terms);
nontermination is priced, not decided — and we measure why the statement
matters. On the Σ-GLYPH reference machine, equality of two-digit Church
numerals expressed *inside* the object language (subtraction and zero-test)
costs 260,780 ATP at $3+2$, 26,212,480 at $5+5$, and exhausts a 50-million
budget at $7+5$; the address idiom settles $7+5=12$ for **601 ATP** and is
linear thereafter (~50 ATP per unit; 19,997 at $200+200$) — five orders of
magnitude at two digits, unbounded beyond. The components are classical
(hash-consing, Merkle identity, normalization by evaluation); the
composition claimed is equality as a *priced settlement with a receipt*: the
two normal-form addresses are the evidence and the spend is part of the
verdict. We show the idiom is already executable downstream without any
format change: a raw check whose expected value is a non-boolean normal-form
hash was filed into a live Warrant evidence pack and re-executes to *pass*
(2,108 ATP) under the unmodified verifier, alongside a bit-vector-fold
predicate (501 ATP) that represents the complementary answer to the same
cost problem. A specification note — not a new primitive — is what we
propose; a draft (ADR-011) is on file with the upstream project. Every
figure above is recounted from the repository by the paper's claims checker.

# 1. The incident

While building a settlement gate for machine-checkable claims (companion
paper, `every-check-spawns-more`), we needed to settle `7+5=12` on Σ-GLYPH
[@sigma-glyph]: a content-addressed SKI machine whose evaluation is
deterministic, integer-only, total at the semantic layer, and priced by a
uint32 budget (ATP) that bounds both work and peak materialized size.

The textbook route encodes equality inside the object language:
$\mathrm{EQ}\ m\ n = \mathrm{ISZERO}(\mathrm{SUB}\ m\ n) \wedge
\mathrm{ISZERO}(\mathrm{SUB}\ n\ m)$, with SUB as an iterated pair-encoded
predecessor. Measured costs on the reference oracle:

| fact | in-language EQ (ATP) |
|---|---|
| $3+2=5$ | 260,780 |
| $5+5=10$ | 26,212,480 |
| $7+5=12$ | > 59,452,030 — ATP Exhausted |

The blow-up mechanism is instructive: under lazy tree-semantics reduction
the *computed* argument ($\mathrm{PLUS}\ 7\ 5$, an unevaluated closure) is
duplicated by every predecessor application, and the equality proof pays
for the argument's structure again at each of its own steps. Building the
proof of equality inside the language makes the proof's cost multiply the
data's cost.

# 2. The idiom

Both sides are applied to fresh inert literals and reduced:

$$(\mathrm{PLUS}\ 7\ 5)\,F\,X \;\longrightarrow\; F^{12}(X)
\;\longleftarrow\; \mathrm{church}(12)\,F\,X$$

Two conforming machines that reach different normal forms have violated
determinism, not equality; content addressing therefore makes the
comparison a comparison of **addresses**. Measured: 601 ATP at $7+5$,
linear at ~50 ATP per unit of result (1,997 at $20+20$; 9,997 at
$100+100$; 19,997 at $200+200$; multiplication 2,213 at $6\times7$, 21,453
at $20\times20$). The receipt is the pair of addresses plus the spends —
nothing else needs to be believed, because everything else re-executes.

In a content-addressed machine, addressing is not a transport layer on top
of equality: it is **identity of what came back** — and that becomes an
equality verdict *only* on an admitted domain (§3.1). The slogan names the
engineering finding, not a theorem.

# 3. Precise semantics — where the slogan is true and where it is false

The two directions of the comparison have different standing, and a
specification that fails to say so will mint receipts that overclaim.

1. **Soundness, only on an admitted domain (corrected 2026-08-31, ADR-011).**
   The earlier draft claimed equal addresses ⟹ equal values *unconditionally*.
   That is false, and the counterexample runs on this repository's own
   evaluator: let $a = \lambda f.\lambda x.x$ (Church zero) and
   $b = \lambda f.\lambda x.X$ (the constant returning the profile's marker
   $X$). These are different functions, yet observed at $(F,X)$ both reduce to
   the same address `8785b7dd…` — because Church zero's second argument *is*
   $X$ — while at $(F,Y)$ they differ. Equal addresses prove **identity of what
   came back**, not equality of the inputs. Soundness holds only when the
   submitted terms lie in an *admitted domain* that refuses terms naming the
   markers (an `EqualityProfile` with an `admitted_domain` check). Collision
   resistance of SHA-256 remains assumed on top of that. "Addressing is
   equality" is the historical name of the engineering finding, not a theorem.
2. **Completeness, conditional.** Different addresses ⟹ different values
   **only when the normal form is canonical for the intended equivalence
   class.** For first-order data evaluated at a generic point — Church
   numerals as $F^k(X)$, tuples of such, tagged sums — normal forms are
   canonical and the method is complete. For arbitrary higher-order terms
   it is not: syntactically distinct normal forms can be extensionally
   equal (η and beyond). "Addressing is equality" is a theorem about
   canonical data, a falsehood about functions.
3. **Termination, priced.** The idiom is defined when both sides normalize
   within budget; `ATP Exhausted` on either side is a canonical outcome,
   not a verdict of inequality. This interacts with receipt design: a
   settle-equality receipt must carry the exit kind of *both*
   evaluations.

# 4. Prior art, and the claimed sliver

Every component is classical. Hash-consing gives $O(1)$ equality of
already-constructed terms and dates to Ershov [@ershov1958], with the
modern statement in Filliâtre–Conchon [@filliatre2006]; Merkle trees
[@merkle1987] and every content-addressed store (git, Nix, IPFS) identify
data by root hash; normalization by evaluation [@berger1991] decides
conversion by evaluating at a generic point, which is exactly our
$F, X$ trick. What we have not found stated is the composition that matters
for machine-verifiable records: **equality as a settlement carrying a
price and a receipt** — evaluate under an explicit budget on a machine
whose spends are part of the canonical result, and let the two normal-form
addresses *be* the evidence. The five-orders measurement is then not a
performance note but a design argument: any ecosystem that makes agents
express equality in-language taxes them $10^5$ at two digits, so the idiom
deserves specification, not rediscovery.

We would welcome a prior statement; the repository's falsifier F1 stands
ready to downgrade this note to a citation.

# 5. Executed downstream: the idiom inside Warrant, today

Warrant [@warrant] records decisions whose justifications can be
re-executable checks; its `ski@v1` checks are `{ski, term, atp, expect}`
blobs re-run on a bundled Σ-GLYPH oracle. Two facts make the idiom
deployable there **without any format change**, and we verified both by
execution rather than by reading:

1. The validator requires only that `expect` be a NodeHash; the runner
   compares plain result hashes. Nothing demands a Church boolean.
2. We filed a raw address-equality check —
   $\mathrm{term} = (\mathrm{PLUS}\ 74\ 1)\,F\,X$,
   $\mathrm{expect} = \mathrm{hash}(F^{75}(X))$, atp 2,108 — into a live
   evidence pack (the companion paper's sealed correction-loop episode).
   `warrant check` re-executes it to *pass*; the pack's settlement-grade
   verification stays at 0 errors, 0 warnings, with the signed records
   untouched.

The same pack carries the complementary approach: Warrant's own WPL
compiler encodes integer comparison as bit-vector folds (~one stored blob
per bit), settling a three-clause acceptance predicate for 501 ATP. The
two are answers to the same enemy — in-language Church arithmetic — with
different shapes: bit-folds for *predicates over small facts*, address
comparison for *equality of computed data*. A specification note covering
scope §3 is drafted as ADR-011 in the upstream project's proposals
directory, with idiom-first (no kernel change) as the recommendation.

# 6. Consequences

*For semantic mass.* This repository's earlier notion of a concept's mass —
a weighted sum over the *unique* hashes of its dependency closure — is
operationally grounded by the idiom: deduplication-by-address is what makes
"a million pointers to one invariant cost one unit" true rather than
rhetorical.

*For settlement gates.* The gate of the companion paper settles arithmetic
claims of live generated text at 441–3,893 ATP each *on the real machine*;
without the idiom those claims would be unsettleable in practice, and the
gate's "priced check per claim" design collapses.

*A speculative generalization, typed as such.* Wherever data can be
canonicalized, internal equality predicates are a smell: expensive equality
is a symptom of uncanonicalized data. We do not defend this beyond the
measurements above.

# Falsifiers

- **F1.** A prior statement of the settlement composition (priced,
  receipted equality-by-address) exists → this note reduces to a citation.
- **F2.** A class of first-order canonical data on which normal-form
  address comparison yields a false inequality → §3.2's scope is wrong,
  not merely narrow.
- **F3.** A compiler brings in-language equality within ~10× of the idiom
  → the design argument collapses to convenience.
- **F4.** The Warrant execution proves format-legality, not upstream
  endorsement; if the upstream project's gate rejects ADR-011's scope
  note, §5's "deployable today" claim must be re-qualified as "executable
  but unspecified".

# Provenance

As with the companion paper: measurements, code and text produced by Claude
(Anthropic, "Fable 5") operating this repository interactively on
2026-08-30 under the human author's direction and editorial
responsibility. `check_claims.py` re-runs every benchmark figure above
against the machine rather than quoting it.
