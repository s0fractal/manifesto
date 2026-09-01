# Claim ledger — budgeted equality by normal-form address (paper B, v0.2 draft, rev after Codex review)

Every claim the v0.2 abstract may make is a row here. Status vocabulary and reproducibility classes
as in paper A. The load-bearing correction that shapes this whole ledger:

> **The headline figures come from a PERMISSIVE research harness (`tools/glyphlib.py`), which admits
> any lambda expression and carries no admission or receipt machinery. The safety profile
> `church@v0` is ADR-011 — a DRAFT / reference implementation at Sigma-Glyph commit
> `196c45a2f9074a472b96af1a6bae2c67533edbb1` (`v0.6.7-175-g196c45a`), non-normative, not gated, not
> adopted, and NOT in the published `sigma-glyph==0.6.7` wheel. It admits only written numerals and
> REFUSES `PLUS 7 5` — so it cannot settle the case this paper exists about.** No number may be
> presented as a `church@v0` fact if it was obtained only under the permissive harness; "released
> profile" must never be written of `church@v0`.

**Falsifier is typed (Codex S3):** only `integrity_break` (a figure fails to re-derive from the
exact executed term/receipt) and `within-sample_counterexample` (an admitted first-order term
settles a false verdict on the tested evaluator) falsify a claim as stated. `replication_failure`,
`scope_boundary`, `competitive_result`, `misuse_warning`, and `open_obligation` do not.

**Genre (Codex §7):** this is an **incident-and-repair note** — a reproduced cost gap, an executable
soundness boundary, an admitted-domain *contract*, and the discovery that the safe profile refuses
the motivating case. It is **not** a claim that the method is realized on an admitted domain.

| # | claim | status | exact evidence | surface | repro | falsifier (typed) | known loss |
|---|---|---|---|---|---|---|---|
| B1 | On the tested evaluator, comparing two normal-form addresses was vastly cheaper than deciding equality with the in-language Church predicate **`EQN(m,n)=AND(LEQ(m,n),LEQ(n,m))`** (LEQ=ISZERO∘SUB; the one-sided form is only an *order* predicate): the address idiom settled 7+5=12 for **601 ATP** while `EQN` cost **260,780 at 3+2**, **26,212,480 at 5+5**, and **exhausted a 50-million budget at 7+5**. | MEASUREMENT | `glyphlib.py` benchmark rows; figures bound to exact term hash (DEPOSIT §A) | **permissive harness `glyphlib.py`** (both sides) | replay | `integrity_break` (a figure fails to re-derive from the executed term hash) | the 601-ATP and predicate figures are the permissive harness's, **not** `church@v0`'s |
| B2 | The measured cost gap motivates an interface idiom for canonical data (settle equality by address instead of computing it in-language). | ENGINEERING FINDING (from B1) | paper §1 | permissive harness | — | `competitive_result` (a first-order canonicalizing comparator within ~10× — F3) | it is an idiom, not a theorem; nothing in CI protects the curve shape |
| B3 | Equal addresses do **not** imply equal inputs unconditionally: an executable counterexample settles `church(0)` PASS-equal to a constant function `λf.λx.X` (X the observation marker) at 27 ATP, both reducing to the same address at the observation point. | NEGATIVE RESULT (executable) | `aie_errata_check.py` C2/C6 + mutations M1/M2/M3 | permissive harness (marker addr `8785b7dd…`); church@v0 analogue `e37391c4…` | replay | `integrity_break` (the counterexample fails to settle PASS-equal on a clean evaluator — F6) | it is the marker of *this* profile, not constant functions in general (M2: a non-marker literal yields VIOLATION) |
| B4 | An admitted-domain **contract** is written down and argued: *on the admitted domain*, `same_address(O(a),O(b)) ⇒ a~b` (reflection). `church@v0` admits only written numerals (grammar/arity/binder-distinctness/freshness fixed), refuses marker-naming terms, and **refuses computed expressions** — it cannot settle `PLUS 7 5`. | **PROFILE OBLIGATION / ARGUED CONJECTURE** (not proved) | ADR-011 reference impl @196c45a (selftest 72/72); errata C6 | `church@v0` **DRAFT @196c45a** | — | `within-sample_counterexample` (an admitted term settles a false EQUAL) | reflection is ARGUED, inheriting an unproved λ→SKI compiler; the motivating case is in the admission gap (EXP-ADR011-01 open); testing 0–8 is not a domain proof |
| B5 | Preservation is a contract obligation too: *where the normal form is canonical for `~`*, `a~b ⇒ same_address(O(a),O(b))`. Higher-order/extensional function equality is out of scope. | **PROFILE OBLIGATION / ARGUED CONJECTURE** (not proved) | paper §4 | either | — | `within-sample_counterexample` (a canonical first-order `a~b` with differing admitted addresses) | out-of-scope η/higher-order terms are `scope_boundary`, not a falsifier; "a statement about canonical data, a falsehood about functions" |
| B6 | Budget exhaustion on either side is an **unsettled** evaluation outcome, not inequality; a receipt must carry both exit kinds; each side receives the full budget independently. | METHOD INVARIANT | `aie_errata_check` not-a-defect #1/#2 | either | replay | `integrity_break` (a receipt that treats `ATP_EXHAUSTED` as inequality, or an order-dependent sequential-budget verdict) | `DISSONANCE(ATP Exhausted)` collides across runs (`8bb0006f…`) — the exit check is mandatory to avoid a false EQUAL |
| B7 | One **stored** SKI check re-executes under the local Warrant: `warrant check 0597575d…` re-runs `(PLUS 74 1) F X → F⁷⁵(X)` to **PASS at 2,108 ATP**, and `warrant verify --settlement` reports 4 records, 0/0. The pack **as a whole** is `LEGACY_UNPINNED` (no dependency closure; not strict-replayable). | CONFORMANCE (per-check) + LEGACY-SEALED (pack) | `warrant check`/`verify`; `replay_pack.py replay → LEGACY_UNPINNED` (exit 1) | permissive/downstream | command | `integrity_break` (the stored check fails to re-execute to the stated ATP) | a **one-sided** check against a constant, **not** a two-sided equality receipt, adoption, or strict pack replay; the current checker only *reads* `manifest.json` — it must execute the check |
| B8 | The one unconditional statement is narrow and renamed **hash-relative observation identity** (a kernel representation invariant under named assumptions): two `normal_form` exits with the same result hash returned one canonically-addressed result, **modulo SHA-256 and evaluator correctness**, under a fixed canonicalization/encoding regime. It says nothing about the terms evaluated. | REPRESENTATION INVARIANT (named assumptions) | paper §4 | either | — | `integrity_break` (a `normal_form` exit returns a wrong result hash) | it is about *what came back*, not input equality, correct-normal-form-ness, cross-implementation agreement, or collision-freedom; not "unconditional" in any tautological sense |

## Claims explicitly NOT made (forbidden)

- unqualified "addressing is equality"; "nothing else needs to be believed";
- **`church@v0` as a "released profile"** (it is DRAFT @196c45a, unreleased, not in the 0.6.7 wheel);
- "unbounded advantage" / "linear thereafter" as a general complexity result (church@v0 ≈37
  ATP/unit on admitted numerals, permissive harness ≈50; the admitted family excludes `7+5`);
- treating **601 ATP as a released-profile fact** (it is the permissive harness);
- address equality as a proof of input extensional equality; completeness for functions;
- soundness/completeness as **proved** (they are argued profile obligations, B4/B5);
- ADR-011 as accepted, deployed, or standardized (DRAFT, non-normative, not gated, BLOCKED on the
  motivating case);
- a Warrant pass — or a strict pack replay — as a proof of the semantic theorem; the pack is
  `LEGACY_UNPINNED`;
- "the Σ-lemma is unconditional" (it is a hash-relative representation invariant under assumptions);
- novelty as established (it is OPEN pending external prior-art review).

## Open (named, not established)

- mechanical admission of computed Church expressions (there is none; EXP-ADR011-01 pre-registered);
- a single implementation that both admits the motivating family and emits a two-sided receipt
  (none exists: the harness has no admission, `church@v0` refuses the case);
- portable settlement across implementations (profile_commitment holds within one Python module,
  CPython 3.12/3.14 only; **no second implementation exists**);
- any asymptotic complexity claim outside the measured family;
- **novelty over prior art** — OPEN pending external review; a search log is required (DEPOSIT §B)
  and must cover, at minimum: hash-consing (Ershov/Filliâtre); NbE freshness/readback side-conditions
  (the §3.1 marker collision is that condition, de Bruijn levels/gensym); and **content-addressed
  identity in deployed systems — Dhall (semantic-integrity hash = hash of the normal form), Unison
  (content hash = definition identity), Nix derivation hashes, IPLD.** After that prior art the
  surviving candidate is only *priced settlement with a receipt*, not "addressing is identity";
- the correctness proof of the λ→SKI compilation that B4/B5 inherit;
- proofs (as opposed to selftests/arguments) of reflection and preservation for the admitted family.
