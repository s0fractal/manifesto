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
| [`every-check-spawns-more/`](every-check-spawns-more/) | the reflexive verification bound ($\lambda_G < (1-\mu)\lambda_V$, phase transition at $\mu = 1$, delegation-invariant anchor); $\mu$ measured for LLM verifiers ($\approx$ 2–3 on informal claims at every depth to 4, $\approx$ 0.14 on well-founded controls, 0 compiled); the settlement gate, the correction loop, the sealed evidence pack; addressing-is-equality with its measured $10^5$ asymmetry |

None is deposited yet. Deposit target is **Zenodo** (as with sigma-glyph and
warrant; no arXiv endorsement is sought): a DOI buys a permanent address and
a frozen artifact — no venue, no peer review — and this README will record
which commit each deposit froze.

Candidate companions, mined from material already in this repository (listed
so the flagship does not silently absorb their scope):

- **addressing-is-equality** — the AIE principle as a standalone note with
  the full benchmark curve and the ADR-011 proposal history
  (`drafts/ADDRESSING-IS-EQUALITY.md` is the seed);
- **the distinction graph** — measured mixing of human terms (Value 40,
  Authority 34, …), re-derived distinctions as amortization priorities, and
  the corpus's clean bill on self-consistency
  (`drafts/TERM-GRAPH-0.1.md` + `tools/term_graph.py`);
- **the glossary contraction loop** — repair→audit iterations as a measured
  convergent recursion (debt 6 → 3 → 3 smaller), with the auditor's catches
  of the amortizing document itself.
