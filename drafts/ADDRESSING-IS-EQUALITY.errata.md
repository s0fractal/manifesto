# AIE-0.1 — errata and supersession

**Status:** errata for `ADDRESSING-IS-EQUALITY.md` (AIE-0.1) and for the surfaces
that inherited its claims. The original draft is **not rewritten**: it stands as
the historical record of what was found on 2026-08-30 and what was believed
about it. This file states what is false in it, what is narrower than it says,
and what is still open.

**Origin.** The upstream review of `sigma-glyph:proposals/ADR-011` produced
eleven items. They are treated here as claims about *this* repository,
reproduced against this checkout rather than copied.

```text
source repo      sigma-glyph
source commit    81ff660566b8354eccbda849aa21ef35aceedc07
source path      proposals/adr-011/MANIFESTO-CORRECTIONS.md
source sha256    ccd0ced49cf6d2b633108070e90048ab5ea65ce8da35bd50fe04ba9f41152d59
receiving base   443324f842959f73679916bbc900ffc5e8fbab33   (manifesto/main)
```

The binding is commit-plus-path-plus-digest. Nothing here reads a sibling
checkout at runtime, so this repository does not acquire a dependency on where
`sigma-glyph` happens to be on disk.

**Executable part:** `python3 tools/aie_errata_check.py`.

```text
executable correction IDs: C2, C5, C6, C11
documentation-only IDs:    C1, C3, C4, C7, C8, C9, C10
controls/mutations:        11/11 pass
```

Eight controls plus three mutations, each mutation required to flip its own
control. **Eleven checks are not eleven corrections decided.** They decide four
of the eleven IDs; the other seven are editorial and no control touches them.
Reading `11/11` beside "eleven corrections" as eleven corrections proved is
exactly the defect this errata exists to correct, so the tool prints the split
on every run.

---

## The correction in one sentence

> An address settles equality only after an admitted profile has made the
> observation canonical.

Equal addresses prove **identity of what came back**. Carrying that back to the
inputs is a property of a profile with a domain, not of addressing.

## What reproduces here, right now

```text
settle_nat_eq(church(0), λf.λx.X)  ->  PASS   27 ATP
  lhs normal form 8785b7dd416cbd01…
  rhs normal form 8785b7dd416cbd01…
```

Two different functions, one address, verdict PASS. `tools/glyphlib.py` has no
admission step, so nothing refuses a term that names the observation marker.
The mutation `M1` adds one and the verdict becomes `REFUSED`; the mutation `M2`
names a non-marker literal instead and the collision disappears — so the
counterexample is about naming *this harness's* marker, not about constant
functions in general.

```text
settle_nat_eq(PLUS 7 5, church(12)) ->  PASS  601 ATP
```

The headline figure is real and belongs **to this permissive harness**, which
admits any lambda expression. The upstream safety profile `church@v0` admits
only literally written numerals and **refuses** this term, so it cannot settle
the case AIE-0.1 was written about.

## Two things AIE-0.1 is NOT wrong about

Stated first, so this errata cannot be read as a longer list of defects than it
found. `settle_nat_eq` already:

- **checks each side's exit** before comparing addresses — the ADR's defect 2
  does not reproduce here;
- **gives each side the full budget independently** — the ADR's defect 3 does
  not reproduce here.

Both are controls in `tools/aie_errata_check.py`, and `M3` shows the first is
read from the code rather than asserted.

---

## C1–C11, per item, per file

Legend: **OPEN** — still says the wrong thing. **CLOSED** — already corrected in
this tree. **PARTIAL** — corrected in one surface, not in another.

| | Item | Status | Where |
| --- | --- | --- | --- |
| C1 | Promises a kernel `EQ(h₁,h₂,atp)` primitive. ADR-011 proposes **none**, and adding one was out of its scope. | **PARTIAL** | OPEN in `drafts/ADDRESSING-IS-EQUALITY.md:3` (status line) and `:48` (§5.1). CLOSED in `papers/addressing-is-equality/paper.md:167`, which already recommends idiom-first, no kernel change. |
| C2 | §1 states the principle with no profile, no exit condition, no per-side budget. | **PARTIAL** | OPEN in the draft §1. CLOSED in the paper `:95–108`, corrected 2026-08-31 citing ADR-011. Note the *code* already satisfies the exit and budget halves. |
| C3 | The two columns of the §2 table come from different harnesses, unlabelled; `~250`/`~500` are approximate beside an exact `601`. | **OPEN** | `drafts/…:20–28`, `papers/…:29`, `:79–80`. |
| C4 | `~50 ATP/unit` is a per-harness constant presented as a property of the idiom. | **OPEN** | `drafts/…:30`, `papers/…:30`, `:80`. Upstream `church@v0` measures ≈37 on the same shape. |
| C5 | The collision digest `8785b7dd…` is cited beside `EqualityProfile`, which does not produce it. | **OPEN** | `drafts/…:38`, `papers/…:101`. **Now settled by execution:** `8785b7dd…` is exactly what `tools/glyphlib.py`'s ad-hoc `("lit", b"X")` marker produces (control C5). It is a genuine digest of the *wrong marker set*. |
| C6 | The admitted domain is described as "terms that do not name the markers" — far wider than `church@v0`, which admits literally written numerals only. | **OPEN** | `drafts/…:38`, `papers/…:104`. |
| C7 | "the method is **complete**" for first-order data is asserted, not established; upstream files it under NOT ESTABLISHED, and reflection/preservation under ARGUED. | **OPEN** | `drafts/…:39`, `papers/…:110–112`. |
| C8 | §5.2–§5.4 (semantic mass, SSD gate, Warrant dedup) inherit the unconditional reading. | **OPEN** | `drafts/…:49–51`, `papers/…:170–180`. |
| C9 | The title/slogan asserts a theorem the text later retracts. | **PARTIAL** | The draft concedes it in §3 but asserts it in the title and status line. The paper concedes it at `:87`. |
| C10 | **F3 is closer to live than the draft suggests.** The EQN blow-up is attributed in §2 to lazy reduction without sharing — a property of the reducer that measured it, not of the language. The 10⁵ ratio is therefore an artifact of one compiler-plus-reducer pair until re-measured on another, which is F3's own condition. Not refuted; not dormant either. | **OPEN** | `drafts/…:57` (F3). Say that F3 has not been tested and that the ratio is harness-relative. No control here decides it: testing F3 means re-measuring on a second compiler+reducer, which this errata does not do. |
| C11 | **Cross-agent dedup needs portable settlement, which is blocked.** Two agents agreeing on an address settled the same thing only if they settled under the same profile — and naming a profile is not identifying one. Upstream answers with a `profile_commitment` that holds *within one Python module* and explicitly not across implementations. Cross-agent dedup is precisely the cross-implementation case. | **OPEN** | `drafts/…:51`. Control `C11` shows the local harness is a step behind even that: a verdict here carries **no** profile id, no commitment and no Book anchor at all, so there is nothing to compare profiles by. |

---

## Two further findings, not in C1–C11

### E1 — the replayable badge calls its result "settled"

`ts-sigma/replayable-badge.html` recomputes seven canonical node addresses in
the browser and renders `7/7 settled`. It runs **no evaluator**: no budget, no
exit, no receipt. "Settled" is the word ADR-011 narrowed to mean a verdict
backed by two receipts with exits and budgets under a named profile. What the
badge does is **recompute and match addresses** — which is a real and useful
thing, and is not a settlement.

The page's own honesty section is otherwise good, and says it "does not run the
ATP-priced evaluator". One clause in it goes further than the code:

> "two constructions reaching the same normal form share one address
> (equality-by-address)"

The page computes no normal forms. That sentence is about evaluation, which
this layer explicitly does not do.

**Suggested:** `7/7 addresses verified`, and drop "equality-by-address" from a
layer that settles no equality.

### E2 — the SSD pack does not regenerate

Running the repository's own declared command on the pinned source:

```text
python3 tools/settle_gate.py --no-write drafts/SSD-DEMO-0.2.md
{"atp_total": 5638, "claims": 11, "refuted": 3, "settled_true": 8, "unsettled": 0}
```

The committed receipt records `refuted: 0, settled_true: 11`. `atp_total` is
identical, so **the Σ-GLYPH layer is stable**; all three refutations are
`layer: repo` substring counts over files that have changed since:

```text
/FLOW/ in FLOW.md            = 12   actual 14
/RVB/ in drafts/RVB-0.1-….md = 12   actual 13
/Теза/ in README.md          =  7   actual  8
```

The pack's acceptance predicate is `refuted == 0 && unsettled == 0 && claims >= 1`,
so today's run does not satisfy the predicate the pack was accepted under.

The cause is not a Σ defect. The committed receipt records only
`source_sha256` of the input document; today's `settle_gate.py` records a
per-claim `dep.sha256`, and then re-reads the *current* file rather than the
pinned bytes. A repo-layer claim is therefore a statement about a moving
target with a digest recorded beside it and not enforced.

**Nothing here was regenerated or committed, and E2 is not fixed in this
change.** The sealed pack is historical evidence of a decision taken on
2026-08-30; rewriting it would destroy what it is for. The regeneration was run
in a scratch copy and the working tree restored.

The requirement it implies belongs to the consumer boundary, not to an errata:

> **Repo-layer dependencies must be content-addressed and re-executed from the
> pinned bytes.** Replaying a historical receipt reads the bytes the receipt
> names. Reading the *current* file is a different operation — a drift check —
> and must be reported as drift, never as a refutation of the original
> settlement.

That is carried into `ADR-012` as a boundary requirement rather than patched
here.

---

## What this errata does not establish

- That the corrected sentences are well argued. It checks that the old ones are
  false or wider than their evidence.
- Anything about C1, C3, C4, C7, C8, C9 or C10 by execution: those are
  documentation items, listed above as such, and no control here decides them.
  C10 in particular would need the 10⁵ ratio re-measured on a second
  compiler-plus-reducer pair — that is what testing F3 means, and it is not
  done here.
- That `tools/glyphlib.py` should change. It is an experimental harness that
  argues no domain; the correction is to the *claims made about it*, not
  necessarily to it.
