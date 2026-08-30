# Reviews

Adversarial review is this repository's intended next phase: the owner plans
to attack the RVB/SSD/AIE line of work with models from other vendors. This
directory is where those reviews land, in the discipline of
`warrant/reviews/`: one file per review, named
`YYYY-MM-<vendor-or-model>-<slug>.md`, filed verbatim (including the parts
that are wrong), with responses in separate files, never edits to the
original. A review that kills a claim is a *contribution*; the falsifier
registers below say exactly what each kill would demote.

## Attack surface (ranked by expected yield)

A reviewer's time goes furthest at these joints. Each entry names the claim,
the artifact to re-run, and the registered falsifier that fires on a hit.

1. **Novelty of the RVB composition** (`drafts/RVB-0.1…`, paper
   `every-check-spawns-more` §2, §7). Find a prior statement of
   $\lambda_G < (1-\mu)\lambda_V$ with a defined, measured $\mu$ —
   verification-debt, software-inspection, or proof-engineering literature
   are the likeliest hiding places. *Fires:* RVB F1 → theorem demotes to
   citation.
2. **The counting operator behind μ** (§3.1 protocol). The 2–7 clustering
   survived one anti-quantization control, but a subtler list-length prior
   would poison every μ figure. Strongest attack: replicate 3–5 chains with
   a non-Anthropic verifier under the same removal-test/dedup rules and
   compare distributions. *Fires:* RVB F2 (μ unstable ⇒ model vacuous) or
   confirms verifier-relativity with a second vendor point.
3. **Negative-control comparability** (§3.3). The control claims differ
   from the corpus in *distribution*, not just in groundedness. Construct
   well-founded claims that are stylistically corpus-like (long, mixed
   language, hedged) and check whether μ stays near 0. A μ ≈ 2 result would
   re-open the verbosity interpretation the control claims to close.
4. **AIE completeness scope** (`papers/addressing-is-equality` §3).
   Exhibit first-order canonical data where normal-form address comparison
   yields a false inequality on the actual machine. *Fires:* AIE F2 —
   the scope section is wrong, not narrow.
5. **The glossary contraction claim** (`drafts/FLOW-GLOSSARY.md` §5,
   EXP-RVB-2). Three points (6 → 3 → 3) is weak evidence of convergence.
   Run the repair→audit loop two more iterations; divergence or a plateau
   of same-size debts breaks the "contraction" reading.
6. **Gate Goodhart** (SSD-PLAN falsifier F2). Prompt a generator to convey
   the same false content while avoiding every gate-parseable claim class;
   measure how much refutable content escapes markup. A high escape rate
   demotes the gate from "settlement layer" to "settlement theater".
7. **Warrant pack semantics** (`drafts/ssd-pack`). The pack verifies at
   0 errors / 0 warnings — attack the *binding*, not the crypto: does the
   accept's WPL predicate actually entail the decision? (Upstream calls
   this the semantic-binding gap and does not claim to close it; a reviewer
   showing our pack *exploits* the gap — facts in the WPL check that do not
   derive from the pinned receipt — lands a real hit.)
8. **Self-application** (everywhere). The papers' claims checkers recount
   figures — find a *class* of claim the checkers do not cover and that is
   wrong. The checkers print their own blind spots; start there.

## How to re-run everything

```bash
python3 papers/every-check-spawns-more/check_claims.py   # 30 figures, GREEN expected
python3 papers/addressing-is-equality/check_claims.py    # benchmarks re-execute
python3 tools/term_graph.py                              # distinction graph + collisions
python3 tools/conf_mono_settle.py                        # COMPILE-0030 receipts
python3 tools/settle_gate.py drafts/SSD-DEMO-0.2.md      # gate, second pass
pip install warrant-verify && cd drafts/ssd-pack && \
  warrant --store .warrants verify --settlement --trust-config trust.json
```

μ-measurement chains are LLM-run and reproducible in kind, not byte-exact;
their protocol is in the papers §3.1 and the raw per-act tables in
`drafts/EXP-RVB-1-RESULTS.md`.
