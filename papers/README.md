# Papers

Write-ups about this repository, following the discipline of
`sigma-glyph/papers/` and `warrant/papers/`: source in `paper.md`,
bibliography in `references.bib`, a recorded `build.sh`, and a
`check_claims.py` that recounts the countable numbers the paper lists from
the repository itself — run before every build, red on any drift, printing
the claim classes it does *not* check rather than implying it covers
everything.

| | subject |
|---|---|
| [`every-check-spawns-more/`](every-check-spawns-more/) | a **verifier-reported** verification-load measurement (ô) on a **single** LLM monologue corpus ($\approx$ 2–3 over sampled paths to depth 4, $\approx$ 0.14 on termination controls) — the v0.1 branching-queue **theorem is retired** (scheduler counterexamples); a compiled check's terminal **zero-obligation** sub-act on a *separate axis* (not "$\mu=0$ compiled"); the settlement gate, the correction loop, the sealed evidence pack. **v0.2 draft; canonical `paper.md` still v0.1 (retirement pending).** |
| [`addressing-is-equality/`](addressing-is-equality/) | an **incident-and-repair note**: the measured cost gap (601 ATP on a permissive harness vs >59M at $7+5$), an executable soundness counterexample, and the discovery that the DRAFT `church@v0` profile **refuses** the motivating case; prior art (hash-consing, Merkle, NbE freshness, and content-addressed systems — Dhall/Unison/Nix) with novelty **OPEN**, sliver narrowed to *priced, receipted settlement*; executed inside Warrant without format change (2,108 ATP non-boolean check). **v0.2 draft.** |

None is deposited yet. Deposit target is **Zenodo** (as with sigma-glyph and
warrant; no arXiv endorsement is sought): a DOI buys a permanent address and
a frozen artifact — no venue, no peer review — and this README will record
which commit each deposit froze.

Paper source, generated paper formats, bibliographies, and documentary
evidence are licensed CC BY-SA 4.0. Executable checkers and other software are
AGPL-3.0-only. The repository-root [`LICENSE`](../LICENSE) is the path-scoped
authority; every deposit manifest includes it and both complete license texts.

Candidate companions, mined from material already in this repository (listed
so the flagship does not silently absorb their scope):

- **the distinction graph** — measured mixing of human terms (Value 40,
  Authority 34, …), re-derived distinctions as amortization priorities, and
  the corpus's clean bill on self-consistency
  (`drafts/TERM-GRAPH-0.1.md` + `tools/term_graph.py`);
- **the glossary contraction loop** — repair→audit iterations as a measured
  convergent recursion (debt 6 → 3 → 3 smaller), with the auditor's catches
  of the amortizing document itself.
