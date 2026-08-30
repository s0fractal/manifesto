---
title: "Every Check Spawns More: A Reflexive Verification Model (Conjectural), Its Measured Coefficient, and a Gate That Crosses the Gap"
author: "Serhii Glova (independent) — sergey.glova@gmail.com"
date: 2026-08-30
keywords:
  - verification
  - LLM agents
  - hallucination
  - epistemology
  - queueing
  - branching processes
  - content-addressed computation
  - scalable oversight
  - deterministic evaluation
classification: cs.AI, cs.LO, cs.SE
bibliography: references.bib
---

# Abstract

An act of verification is not free of consequences for the verifier: checking
one claim surfaces new load-bearing assumptions — about the method, the
instruments, the meanings of terms — that themselves admit checking. We model
this with one parameter, the *reflexivity coefficient* $\mu$: the mean number
of new, load-bearing, checkable assertions introduced by a single verification
act. Elementary results follow. A system that generates claims at rate
$\lambda_G$ and verifies at rate $\lambda_V$ is stable only if
$\lambda_G < (1-\mu)\lambda_V$; at $\mu \ge 1$ no finite budget suffices, and
the fraction of claims never fully verified is bounded below by
$1 - (1-\mu)\lambda_V/\lambda_G$. Independently of rates, any sound verifier
with acyclic warrants rests on a nonempty set of claims accepted without
verification, and delegation relocates that anchor rather than removing it.
The mathematics is standard (branching processes, queueing, the Agrippan
trilemma); the contribution we claim is the composition, and above all the
**measurement**. Using a fixed protocol (a removal test for load-bearingness,
strict deduplication against the whole verification tree), we measured $\mu$
for large-language-model verifiers over a philosophical corpus: $\mu \approx
2$–$3$ at every depth probed (to depth 4), stable across claim types, with a
verifier effect (about $3.2$ for one model, $2.1$ for another). A negative
control on well-founded claims (arithmetic, a proved theorem, a specification,
a settled physical constant) yields $\mu \approx 0.14$ with chains that
terminate by themselves — so the plateau is a property of the claims'
distance from checkable form, not of model verbosity. We then cross the gap
in practice: a single informal claim (confidence monotonicity across
summarization) is compiled to a deterministic, budget-priced check on a
content-addressed machine, and its measured $\mu$ drops from $\approx 3$ to
$0$ (verification = byte-identical replay). A *settlement gate* built on this
idiom catches 4 of 11 claims of a live, verification-forbidden generator
(all four failures are world-facts from memory; all internal arithmetic
survives), repairs them from the gate's own measured values, and reaches 11/11
on the second pass; the full episode is then sealed as a signed, hash-linked
decision chain whose acceptance predicate re-executes offline. Along the way
we record an engineering asymmetry we believe deserves its own statement:
in a content-addressed machine, equality of canonical data settles by
comparing normal-form addresses at linear cost, while the same equality
expressed inside the object language explodes combinatorially — five orders
of magnitude at two-digit addends. We are explicit about what is *not*
established: all verifiers measured are LLMs from a single vendor lineage;
$\mu$ is a property of the (verifier, corpus) pair, not of thought; the
supercritical conclusion assumes claims do not expire unverified; and the
theorem's only asymptotic escape — amortization by abstraction — is
demonstrated, not exhausted.

# 1. Introduction

That machine generation now outruns verification is a commonplace; the term
*verification debt* names the qualitative gap [@cacm-verification-debt]. The
blockchain literature's *verifier's dilemma* [@luu2015demystifying] treats a
related but orthogonal problem: verifiers who *could* check but rationally
will not. This paper is about verifiers who *want* to check and cannot
finish — because the act of checking is itself generative.

The observation is old. Agrippa's trilemma says every justification ends in
an unjustified anchor, an infinite regress, or a circle; Gödel's second
incompleteness theorem and Löb's theorem sharpen the anchor's status for
systems that can talk about their own soundness; the *de Bruijn criterion*
in proof engineering [@barendregt2005challenge] responds by minimizing the
trusted kernel rather than pretending to eliminate it. What these traditions
did not do is treat the *rate* at which checking spawns obligations as a
measurable quantity, or ask what value it takes for the verifiers we now
deploy at scale — large language models reviewing each other's claims.

We do three things.

1. **State the bound** (§2). One parameter $\mu$ turns the folklore into
   inequalities with proofs: a stability condition
   $\lambda_G < (1-\mu)\lambda_V$, a phase transition at $\mu = 1$, a
   closed-form lower bound on the never-verified core, and a
   delegation-invariant anchor.
2. **Measure $\mu$** (§3). Across 100+ verification acts under a fixed
   protocol, LLM verifiers on informal claims sit at $\mu \approx 2$–$3$
   per act at every depth to 4; on well-founded claims the same verifiers,
   same protocol, drop to $\mu \approx 0.14$ and stop on their own. We also
   measure the two levers the theorem predicts matter: verifier identity
   and amortization (a glossary that closes defect *families* turns diverging
   chains into converging ones).
3. **Cross the gap** (§4–§5). We compile one informal claim to a
   deterministic check on Σ-GLYPH, a content-addressed budgeted machine
   [@sigma-glyph], measure the compiled form at $\mu = 0$, build a settlement
   gate on the idiom, run it against a live generator, close the
   generate–settle–repair loop, and seal the episode as Warrant decision
   records [@warrant] whose acceptance predicate any reader re-executes.

Everything countable in this paper is recounted from the repository by
`check_claims.py` in the paper's directory; the classes it cannot check
(subagent-run measurements, external citations) it lists rather than
implying coverage.

# 2. The reflexive verification bound

## 2.1 Model

A *reflexive verifier* is a triple $R = (\lambda_G, \lambda_V, \mu)$:

- claims are generated by the system's own activity as a point process with
  rate $\lambda_G$;
- verification acts execute at rate $\lambda_V$ (i.i.d. durations, mean
  $1/\lambda_V$), one act per claim;
- an act additionally spawns $N$ new claims that must be verified for the
  original claim to be *closed* — meta-claims about the method, instruments,
  side conditions — with $N$ i.i.d., $\mathbb{E}[N] = \mu \ge 0$.

The closure of a claim is then a Galton–Watson tree with offspring mean
$\mu$. Write $g = \lambda_G / \lambda_V$ and let $\gamma$ be the asymptotic
fraction of generated claims never closed.

## 2.2 Statement

> **Status (revised after external review, Codex 2026-08).** What follows is a
> **conjectural model, not a theorem.** An external reviewer produced explicit
> counterexamples to (C) and (D) as originally stated: both depend on an
> unstated *scheduler and abandonment policy*. A scheduler that preferentially
> completes short (small-$N$) closures beats the mean-size accounting the
> renewal–reward argument assumes. Concretely (reviewer's example): with
> $P(N{=}0)=\tfrac34,\,P(N{=}2)=\tfrac14$ ($\mu=0.5$), $g=0.8$, checking each
> root once immediately closes 75% while (C)'s bound $\gamma\ge 1-(1-\mu)/g =
> 0.375$ demands ≥37.5% unclosed — violated. And with
> $P(N{=}0)=0.4,\,P(N{=}2)=0.6$ ($\mu=1.2\ge 1$), 40% of roots close on the
> first act, so (D)'s "throughput → 0" fails. The anchor leg (A) also needs
> **well-foundedness**, not mere acyclicity (an acyclic chain
> $c_0\leftarrow c_1\leftarrow\cdots$ can descend forever without reaching
> $\mathcal{A}$). The statements below are kept as written, with the repair
> conditions named inline, because the *measurement* (§3) is what this paper
> actually establishes; the closed forms are the conjecture the measurement
> motivates, not a proven bound. A dedicated probability reviewer is the
> registered next step.


**(A) Anchor.** If acceptance requires a warrant (a verification act or
membership in an axiom set $\mathcal{A}$), and the warrant relation is
acyclic, then whenever anything is accepted, $\mathcal{A} \neq \emptyset$;
and if the claim language can express the verifier's own soundness,
$\mathcal{A}$ cannot be certified internally (Gödel II / Löb). Adding an
external verifier $O$ moves the claim "$O$ is sound" into $\mathcal{A}$:
the anchor is invariant under delegation.

**(B) Subcritical.** If $\mu < 1$ and $g < 1 - \mu$, the backlog is stable,
but the expected instantaneous unverified frontier is at least
$g/(1-\mu) > 0$ (Little's law with sojourn $\ge$ mean service
$1/(\lambda_V(1-\mu))$). The frontier is empty only for a dead system.

**(C) Supercritical.** If $\mu < 1$ and $g > 1 - \mu$, then
$\gamma \ge 1 - (1-\mu)/g$: a constant positive fraction of self-generated
claims never closes. *Proof:* at most $\lambda_V t(1+o(1))$ acts occur by
time $t$; each completed closure consumes on average $1/(1-\mu)$ acts
(Galton–Watson mean size, renewal–reward), so completions are at most
$\lambda_V(1-\mu)t(1+o(1))$ against $\lambda_G t(1+o(1))$ arrivals. ∎

**(D) Phase transition.** If $\mu \ge 1$, closed-verification throughput
tends to zero for any finite $\lambda_V$: at $\mu = 1$ closures are finite
almost surely but with infinite mean; at $\mu > 1$ a single claim's closure
is infinite with positive probability. No budget suffices.

## 2.3 What the bound does and does not say

The model has three honest apertures, found partly by the measurement
apparatus itself (§3.5).

*Obsolescence.* The backlog is assumed conservative. If claims expire
unverified at per-claim rate $\delta > 0$, the backlog equilibrates at
$(\lambda_G - (1-\mu)\lambda_V)/\delta$ and (C)'s divergence reading fails;
$\gamma$ then counts *never verified*, not *forever pending*. The bound
governs claim classes where debt does not burn off — obligations, safety
claims, specifications.

*Amortization.* One act that verifies a **quantified class** — a proof, a
type, an invariant — breaks the one-act-per-claim assumption and is the only
asymptotic escape from (C)–(D) inside the model's vocabulary. §3.4 measures
this escape working; §4 industrializes it.

*What $\mu$ is a property of.* $\mu$ attaches to the pair (verifier,
corpus), not to the corpus alone and not to "reasoning" in the abstract.
Our measurements make this concrete: two verifiers differ by ~50% on the
same claims (§3.2).

# 3. Measuring μ

## 3.1 Protocol

A *verification act* on a claim produces (i) a verdict — VALID, INVALID, or
UNVERIFIABLE-AS-STATED — supported by actual verification work (attempted
proof, counterexample search, or evidence assessment), and (ii) the act's
*offspring*: the new load-bearing checkable assertions the verification
relies on. Three counting rules discipline the offspring list:

- **checkable** — the assertion has truth conditions;
- **load-bearing** — a removal test: if the assertion were false, the
  verdict would fall; decorative candidates are dropped;
- **novel** — strict deduplication against every assertion already recorded
  anywhere in the same verification tree.

Verifiers were instances of two Anthropic models (Claude "Fable" and Claude
"Sonnet" generations current in August 2026), one isolated agent per tree or
chain, explicitly instructed to be strict and told the corpus had never
faced criticism. The corpus is this repository's *Monday* dialogue notes:
~75 files of speculative philosophy generated as an unchallenged monologue
(the prompter only ever said "continue"), i.e., a pure generator with
$\lambda_V$ literally zero prior to these experiments.

## 3.2 Results on informal claims

**Round 1 (trees, depth 2).** Twelve root claims stratified by type (4
formal, 4 empirical, 4 conceptual); each root verified, two offspring
expanded at depth 0, one per node at depth 1; 60 acts total.

| depth | acts | mean offspring $\mu_d$ | spread |
|---|---|---|---|
| 0 | 12 | 5.42 | 4–7 |
| 1 | 24 | 3.38 | 3–4 |
| 2 | 24 | 2.50 | 2–3 |

By type at depth 0: formal 5.50, empirical 5.50, conceptual 5.25 — $\mu$ is
stable across claim types. Verdicts: 0 VALID, 8 INVALID, 4
UNVERIFIABLE-AS-STATED. The 60 acts generated 206 new load-bearing
assertions and closed 48: verifying 12 claims left roughly 13 obligations
open per claim closed. The experiment about verification debt produced
verification debt, as the model says it must.

**Round 2 (chains, depth 4, 2×2 design).** Eight narrow chains (one
offspring expanded per act) to depth 4, crossing verifier (Fable / Sonnet)
with counting instruction (standard / "0, 1 or 12 are all acceptable
answers"), roots quoted verbatim from source files:

| depth | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| $\mu_d$ (all 8 chains) | 3.50 | 2.75 | 2.50 | 2.13 | 2.25 |

The decay *flattens* near 2 instead of crossing 1: the geometric
extrapolation from round 1 is disconfirmed, and within the probed range the
regime stays supercritical. Effects: verifier Fable $\bar\mu = 3.15$ vs
Sonnet $2.10$ (the coefficient is verifier-relative); counting instruction
2.80 vs 2.45 (the round-1 clustering was not a list-length artifact);
verbatim roots lowered Fable's depth-0 mean from 5.42 to 4.25 (extraction
bias is real and worth ~20%). Two roots — confidence monotonicity and a
modal reachability core — were the only VALID verdicts among 20 informal
roots tested across both rounds; both were verified by Sonnet.

**Crossed design.** We resolved the confound by crossing: the two
Sonnet-VALID roots re-verified by Fable, the two Fable-UNVERIFIABLE roots
re-verified by Sonnet. Negative verdicts replicated (2/2); positive
verdicts did not (0/2) — after crossing, **no informal corpus claim is
VALID under both verifiers**. The flips are not taste: Fable produced
concrete counterexamples (a valid evidence-free inference can raise
certainty, $P(A \lor B) > \max(P(A),P(B))$, refuting the monotonicity
claim as a general law; budget-bounded reachability is non-transitive by
a three-node construction, so the modal core's implicit S4 fails). The
verifier-μ profiles, meanwhile, replicated on the crossed roots (the
stricter verifier ≈ 3.2, the other ≈ 2.1, per root family as before):
$\mu$ is verifier-stable per model, verdicts are not — and within a
single vendor lineage, which sharpens rather than softens the
multi-verifier caution of §3.5.

**Across all 100 acts of both rounds, no act returned zero offspring.**

## 3.3 Negative control: the instrument, validated

Same verifiers, same protocol, roots where verification *should* terminate:
$2+2=4$ in Peano arithmetic; the infinitude of primes; SHA-256's digest
width per FIPS 180-4; water's boiling point at one atmosphere; "all
bachelors are unmarried"; git SHA-1 hash length (verified by the agent
recomputing the HEAD hash from raw bytes). Offspring counts: 0, 1→0, 0, 0,
0, 0 — $\mu_{\text{control}} \approx 0.14$, chains terminating at depth 0–1
by exhibiting the discharging computation in the act itself.

The contrast — 0.14 versus 2.1–3.2 under an identical measurement
operator — is the paper's central empirical fact. $\mu$ measures a claim's
**distance from a form in which checking terminates**, not the verbosity of
the model doing the checking.

**Style control.** Because the control claims differ from the corpus in
style as well as in groundedness, we ran a second control: four genuinely
well-founded claims dressed in the corpus's own register (mixed-language
conceptual prose, boxed formulas, rhetorical framing), with the prediction
registered before the results. Two claims dischargeable by an exhibited
finite computation ($\pi(100)=25$; a pattern count in a repository file)
stayed at $n=0$ even in costume — the verifiers *twice, in writing,
classified the rhetorical framing as non-load-bearing and refused it
offspring*. The other two rose (chains 2,2,2,1,0 and 3,3,3,2,2; overall
$\mu_0 = 1.25$), and the offspring show why, and it is not verbosity: the
costume itself smuggled checkable content (an "addresses in
content-addressed systems" gloss that overgeneralizes — real CAS addresses
are not bare digests; a "recoverable by any agent from the axioms"
quantifier), and the Pythagorean theorem's closure genuinely contains its
axiomatics (the parallel postulate behind similarity, SAS as an axiom,
line-unboundedness with a spherical countermodel). The refined statement:
style adds $\mu$ only by adding content, and well-founded claims differ in
their distance-to-discharge — a finite computation is self-discharging, a
theorem "from the axioms" is not. No plateau of contentless paraphrase was
observed on any well-founded claim.

## 3.4 Amortization, measured

The theorem's escape hatch predicts that one act closing a defect *family*
should convert diverging chains into converging ones. We wrote a glossary
and errata document for the corpus's framework file (symbol table, an
operator's two conflated senses split, definitional-status typing) and
re-measured the three round-2 roots whose offspring had been dominated by
definitional gaps:

| root | before (depths 0…) | after |
|---|---|---|
| framework central thesis | 4,3,3,3,3 — no end | 3,3,**0** — terminated |
| agent definition | 4,3,3,2,2 — no end | 4,2,1 + verdict flipped VALID |
| representability claim | 4,3,3,3,4 — no end | 4,2,**0** — terminated |

Two of three chains reached natural $n=0$ termination — the first such
terminations on corpus material in 100+ acts — and the residual offspring
migrated from defects *of the corpus* to defects *of the glossary itself*,
which were then ledgered as open debts with closure conditions. An
adversarial audit of the glossary's own closure claims returned INVALID with
its own converging chain (5, 2, 1), catching, among other things, a symbol
carrying three roles inside the amortizing document. Across three
repair–audit iterations the debt count went 6 → 3 → 3 strictly smaller
items: the recursion the theorem says cannot end can, with amortization, be
made to **contract**. A fourth iteration then measured the honest caveat: a
hasty repair (a definition added without amending the norms it contradicted,
grounded in a downstream schema quoted from memory rather than re-read)
drove the count back to 7 before a careful fifth pass — contraction is a
property of diligent iterations, not of the loop itself, and the loop
punishes haste measurably.

## 3.5 Threats to validity

All verifiers are LLMs from one vendor lineage; agreement between them is
not independent confirmation, and $\mu$ for human verifiers, or for models
from other lineages, is unmeasured. Sample sizes are small (12 + 8 + 6 + 3
roots). Offspring counts cluster in 2–7 and, although the anti-quantization
instruction moved them only 0.35, a subtler list-length prior cannot be
excluded. Depth stops at 4; $\mu_\infty$ is extrapolated, not observed. The
negative control's distribution mismatch with the corpus is partly
addressed by the style control above (which we ran against our own
threat model, prediction pre-registered); what remains unaddressed is a
control matched on *both* style and topical domain simultaneously, and
replication with non-Anthropic verifiers. The corpus is a single,
stylistically uniform document set. Finally, the protocol's own extraction step measurably
inflates $\mu$ (§3.2), and one control chain (V7 in the repository data)
drifted off its assigned root — recorded, not silently dropped.

# 4. Crossing the gap: compilation to μ = 0

The claim that fared best in early verification — *confidence must be
monotone across translation and summarization layers unless evidence is
added* — was carried end-to-end from prose to settlement. (The crossed
design of §3.2 later refuted this claim *as a universal law*; the compiled
version below is untouched by that counterexample, because compilation
scopes the disjunct: "evidence" becomes an explicit record on a declared
trace. Compilation did not merely make the claim checkable — it made it
true, by paying for scope. We keep the chronology honest rather than
retrofitting.)

1. **Stipulation.** The audit's open questions (whose confidence? what
   counts as evidence? what is a layer?) were paid down by definition:
   a trace is a sequence of (claim-hash, confidence in ppm as u32,
   optional evidence-hash); the invariant is
   $\mathrm{conf}[i{+}1] \le \mathrm{conf}[i] \lor \mathrm{evidence}[i{+}1] \neq \varnothing$.
2. **Integer checker.** A total, deterministic, float-free checker with a
   canonical receipt; two runs produce byte-identical bytes.
3. **Machine settlement.** Per-trace instance checks compile (bracket
   abstraction, Church encodings) to closed terms of Σ-GLYPH — a
   content-addressed SKI machine whose evaluation is deterministic,
   integer-only, total at the semantic layer, and priced by an explicit
   budget (ATP) [@sigma-glyph]. Verdicts come back as content-addressed
   literals with exact spends: a clean summarization trace settles PASS at
   4,151,277 ATP; a confidence-laundering trace settles VIOLATION at
   554,678 ATP; a trace whose confidence jump carries an evidence record
   settles PASS at **25 ATP** — lazy evaluation short-circuits the
   comparison the evidence makes unnecessary. Checking costs exactly as
   much checking as the claim requires, and the cost is part of the
   verdict.

The compiled claim was then measured under the §3.1 protocol: the verifier
re-ran the script, compared receipt bytes, and stopped with zero offspring.

**What this does and does not show (corrected after review, Codex F6).** The
prose claim measured $\mu \approx 3$; the compiled artifact measures
$\mu = 0$. It is **not** "the same semantic content" — an earlier draft said
so, and that was wrong. The compiled version is a *weaker, stipulated
specification* (the prose asserted a universal law, later refuted in §3.2;
the compiled invariant holds because its scope was narrowed until it did).
And $\mu = 0$ proves only that *this particular checker terminates*: a
trivial `return true` also has $\mu = 0$. Termination is not adequacy.
**Semantic binding** — that the checker's computation actually captures the
prose claim's content, that its facts derive from cited evidence, that its
result entails what the document asserts — is the real open bridge, and this
compilation does not close it; it relocates the claim to a form where the
*termination* half is free. That is genuinely useful (a settleable artifact
where there was none) and genuinely partial. §5's gate inherits exactly this
limit, which §5.2's own failures then make measurable.

# 5. The settlement gate

## 5.1 Design

If compilation crosses the gap for one claim, a *gate* industrializes it:
text carries inline claims in a trivial markup
(`⟦arith: 74 + 1 = 75⟧`, `⟦cmp: a <= b⟧`, `⟦count: /re/ in file = N⟧`,
`⟦cite: "quote" in file⟧`, `⟦mono: confidence chain⟧`, `⟦sha256: file =
prefix⟧`); the gate settles every claim deterministically — small arithmetic
on the real Σ-GLYPH machine, the rest on integer/repo layers — and rewrites
the text with badges: settled-true (with layer and ATP), REFUTED (with the
measured actual value), or unsettled (the claim stays typed as
speculation). A canonical receipt accompanies the output.

**The gate's honest boundary, made concrete by review (Codex F3).** A
document can carry a fully-settled receipt and still assert falsehoods,
because the gate settles only *marked* claims and binds only what the markup
names. The `SSD-DEMO-0.2` fixture of §5.2 shows `11/11 ⚓` yet its prose
claims "3 root files and 6 directories" via `⟦arith: 3 + 6 = 9⟧` — the
arithmetic is true and the operands are never bound to the sets they
purportedly count (actual: 8 and 8); its unmarked claims about directory
sizes are simply wrong. So the falsifiers this paper filed as *future*
(F2 Goodhart, F2c selective markup) have in fact *already fired* in our own
canonical success case. Two consequences we now hold as load-bearing: a
receipt binds to *marked, supported* claims only (never to a document's full
truth), and a receipt is only as current as the world it was computed
against — the `SSD-DEMO-0.2` receipt froze a `count(/FLOW/)` value the
repository has since drifted past, so a live re-run of that same fixture now
reports `10 settled / 1 refuted`. Both facts argue for **dependency-bound
receipts** (committing to the digest of every file read, the repo SHA, the
checker version and oracle fingerprint), not merely to source text — a
change registered in the closure-season plan, not yet built.

## 5.2 Live episode

A generator model was asked to write a technical summary of this repository
with at least ten embedded claims, **forbidden to verify anything** (it
could list file names, not open contents). It produced 11 claims. The gate
settled 7 and refuted 4 — and the split is the theorem's picture drawn by
hand: *every* internal computation (arithmetic over the generator's own
numbers, comparisons) survived; *all four* refutations were world-facts
recalled from impression (pattern counts guessed as 42/37/8/12 against
measured 12/12/67/7). Settlement cost: 5,638 ATP, ~0.05 s.

A corrector was then given the badged text with one rule: the only
admissible source of truth is the measured values inside the refutation
badges. The second gate pass settled **11/11 with zero refutations**. The
loop — generate, settle, repair from the gate's own measurements, settle
again — closed for 11,276 ATP total. The gate is not a detector; it is a
repair supplier.

A second experiment aimed the gate at the corpus itself: an extractor read
only the dialogue index and predicted distinctive phrases that should occur
verbatim in the indexed files. Of 30 predictions, 2 held verbatim, 10
failed only on capitalization, and 18 phrases do not occur in the files at
all — the index is an interpretive layer whose introduced vocabulary was
never declared. The gate measures translation loss between an index and its
sources, which is the same defect class the corpus's own framework warns
about.

## 5.3 Sealing

The full episode was filed as Warrant decision records [@warrant]: propose
(generator) → reject (gate; the failing check and the round-1 receipt
pinned as transcript) → propose (corrector) → accept (gate). The accept's
justification is not prose: it is a re-executable check compiled from a
14-line policy source (`refuted == 0 && unsettled == 0 && claims >= 1` over
the receipt tally) that the Warrant verifier re-runs offline on its bundled
Σ-GLYPH oracle — pass, 501 ATP. With the shipped trust configuration the
pack verifies at settlement grade: 0 errors, 0 warnings, every signature
bound to its actor. Rejection is a first-class record: the episode's "no,
because" survives with the same integrity as its "yes".

# 6. Addressing is equality

One engineering incident during gate construction deserves separate
statement. Settling $7+5=12$ via equality *expressed inside the object
language* (Church-numeral subtraction and zero-test) exhausted a 50-million
ATP budget; measured costs grow combinatorially (260,780 ATP for $3+2$;
26,212,480 for $5+5$; over 59 million, exhausted, for $7+5$), because lazy
reduction duplicates the unevaluated computed argument at every predecessor
step. The same fact settles for **601 ATP** by the idiom: reduce both sides
applied to fresh inert literals — $(\mathrm{PLUS}\ 7\ 5)\,F\,X$ and
$\mathrm{church}(12)\,F\,X$ both normalize to $F^{12}(X)$ — and compare the
**addresses** of the normal forms. Cost is linear (~50 ATP per unit;
19,997 ATP at $200+200$). In a content-addressed machine, addressing is not
transport laid over equality; it *is* the equality mechanism.

The semantics must be stated precisely, or receipts overclaim. Hash
equality implies equality unconditionally (modulo the hash function, which
is in the trust anchor). Hash *in*equality implies inequality **only when
the normal form is canonical for the equivalence class in question** —
true for first-order data evaluated at a generic point, false in general
for higher-order terms (η). Nontermination is priced, not decided: budget
exhaustion is the honest outcome. The components are classical —
hash-consing [@ershov1958; @filliatre2006], Merkle identity [@merkle1987],
normalization by evaluation [@berger1991] — and the composition we claim is
only this: equality as a *priced settlement with a receipt*, in which the
two normal-form addresses are the evidence and the ATP spend is part of the
verdict. The idiom is already legal downstream: a raw check with a
non-boolean expected hash ($\mathrm{term} = (\mathrm{PLUS}\ 74\ 1)FX$,
expect $= \mathrm{hash}(F^{75}(X))$, 2,108 ATP) was filed into the §5.3
evidence pack and re-executes to *pass* under the unmodified Warrant
verifier.

# 7. Related work

The anchor leg composes Agrippa, Gödel II and Löb with the de Bruijn
criterion's engineering stance [@barendregt2005challenge]; we add nothing
to those results beyond the delegation-invariance remark and the pairing
with a throughput model. Queueing and branching mathematics is textbook.
*Verifier's dilemma* [@luu2015demystifying] concerns incentives, not
capacity; *verification debt* [@cacm-verification-debt] names the gap
without a model or a measured coefficient. Logical induction
[@garrabrant2016] gives bounded reasoners asymptotic self-trust guarantees
but no throughput accounting. Scalable-oversight proposals — debate
[@irving2018debate], iterated amplification [@christiano2018amplification]
— are, in this paper's vocabulary, $\mu$-reduction engineering; our
measurements suggest evaluating them by whether they push the *effective*
$\mu$ of their verification steps below 1, which is a measurable target
rather than an aspiration. On the settlement side, Σ-GLYPH [@sigma-glyph]
and Warrant [@warrant] supply the deterministic, budgeted, re-executable
substrate this paper leans on; the gate and the measurements are the new
layer. We searched for a prior statement of the threshold
$\lambda_G < (1-\mu)\lambda_V$ with a measured $\mu$ and did not find one;
we would welcome a correction, and falsifier F1 of the repository notes
stands ready to downgrade the theorem to a citation.

# 8. Conclusion

Checking ends by decision, not by completion: that much is ancient. What is
new here is a number. For today's LLM verifiers on informal claims the
reflexivity coefficient sits near 2–3 and does not fall below 1 within
measurable depth — so chains of "AI checks AI" do not converge on their
own, at any budget. The same instruments on well-founded claims read
~0.14 and stop unaided, and a claim compiled to a content-addressed,
budget-priced check reads exactly 0: the gap is real, measured, and
crossable, claim by claim, at a price that can be itemized. The
architecture this points to is unglamorous: a generative layer that
proposes, a settlement layer that prices and replays, receipts that outlive
both, and speculation that survives — welcome, even — so long as it wears
its type. Every check spawns more; the craft is choosing which checks are
worth an anchor, and making that choice a record someone else can re-run.

# Provenance and authorship

The theorem statement, all experiments, all tooling, and this text were
produced by Claude (Anthropic, "Fable 5" generation) operating the
repository interactively on 2026-08-30 under the direction, review, and
final editorial responsibility of the human author. Verifier and generator
roles inside the experiments were played by separately instantiated Claude
agents (Fable and Sonnet generations) with role-specific instructions,
as recorded in the repository's experiment notes. The measurement data,
receipts, evidence pack, and every tool are in the repository at the commit
this deposit archives; `check_claims.py` recounts the countable figures
from those artifacts. Numbers that live only in subagent transcripts
(the per-act offspring tables of §3) are recorded in
`drafts/EXP-RVB-1-RESULTS.md` and are re-runnable in kind but not
byte-reproducible, LLM sampling being what it is — a limitation the paper's
own thesis predicts, and prices.
