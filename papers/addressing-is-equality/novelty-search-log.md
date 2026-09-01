# Novelty search log — Addressing Is Equality (paper B)

**Purpose.** Deposit requires a dated prior-art search log (Codex P1-B5; `DEPOSIT-AND-AUDIT.md §B`)
before any novelty is asserted. F1 in `CLAIM-LEDGER.md` treats novelty as **OPEN**.

**Provenance & status.** The core search was produced by an **out-of-lineage** reviewer — Kimi Chat
(Moonshot AI), 2026-09-01, reviewing commit `25123df` (`reviews/2026-09-kimi-001.md`, Task 3). It is
recorded here as received. It is **one** search by **one** LLM reviewer, not an exhaustive or
human-verified survey; novelty stays **OPEN** until an independent (ideally human) prior-art review
confirms it. Each row states whether the candidate anticipates the *whole* claimed sliver or only a
component.

## Claimed sliver under test

> **Equality as a priced settlement with a two-sided receipt** — an equality settlement that carries
> both normal-form addresses, both exit kinds, the ATP budget spend on each side, and the
> machine/profile identity as part of the verdict, on a deterministic total evaluator where budget
> exhaustion is a canonical non-verdict outcome.

## Search log

| Candidate | Anticipates the sliver? | Note / source |
|---|---|---|
| **NbE freshness side-condition** (Berger–Schwichtenberg 1991; Abel 2013 habilitation) | **Component only.** The §3.1 marker collision *is* the classical NbE/readback freshness condition — residual markers must be fresh/unnameable (de Bruijn levels, gensym). Anticipates the counterexample, **not** the priced-receipt composition. | Berger–Schwichtenberg 1991; Abel 2013; PLS-Lab NbE survey |
| **Unison** | **Component only.** Content hash = a definition's identity ("the hash is its true name") — content-addressed identity of *code*, not computed normal-form equality with a budgeted receipt. | unison-lang.org docs |
| **Dhall** semantic-integrity hashes | **Component only.** Integrity check = hash of a *normalized* expression ("the hash is the true address, the path is a suggestion") — content-addressed identity of normal forms, but no priced evaluation, no two-sided comparison, no ATP-in-verdict. | Dhall.Tutorial (Hackage); Haskellforall 2017-11-03 |
| **Nix** derivation hashes (fixed-output / floating CA) | **Component only.** Hash = identity of the *build product*, not a runtime equality verdict with a receipt. | Nix RFC 0062 (2019); NixOS Wiki ca-derivations |
| **IPLD / Merkle identity** | **Component only.** Content-addressed identity of data structures; no pricing, no equality settlement, no receipt. | IPLD docs; IPFS Merkle-DAG docs; Merkle 1987 |
| **Hash-consing** (Ershov 1958; Filliâtre–Conchon 2006) | **Component only.** O(1) structural equality of already-constructed terms by sharing — the address-sharing mechanism, not semantic equality of computed values with a priced receipt. | Ershov 1958 (CACM); Filliâtre–Conchon 2006 (ACM ML) |
| **Gas-metered VMs (Ethereum EVM)** | **Nearest miss.** *Priced execution with a receipt* (per-op gas, `gasUsed` in a consensus receipt). But the receipt attests to *execution*, **not** to equality of two normal forms, and gas is market-priced, not a deterministic budget bound on a total evaluator. | Ethereum Yellow Paper; EVM docs |

## Verdict on F1 (as received from Kimi, endorsed pending independent review)

- Novelty **must not** be claimed for "addressing is equality" or for content-addressed identity —
  Dhall, Unison, and Nix already make the hash of the normal form the identity.
- The **only** surviving candidate is the *priced two-sided receipt composition*, and even that has a
  **near-miss** in Ethereum gas receipts (priced execution with a receipt, but not equality-specific).
- Therefore the abstract's sole novelty claim should be the narrowed sliver, flagged OPEN; F1 remains
  **`open_obligation`**, not closed.

## Still owed before deposit

- an **independent / human** prior-art check (this log is a single out-of-lineage LLM pass);
- a direct comparison against any equality-specific priced-receipt scheme (the gas near-miss must be
  distinguished explicitly, not just named);
- if the sliver survives, one sentence in the paper **narrower** than the paper's current phrasing.
