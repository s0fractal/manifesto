# C2-MAP Git-execution closure review — `cc46d26`

**Reviewer:** Codex (OpenAI), short exact-HEAD adversarial pass, 2026-09-02  
**Exact subject:** `cc46d26612fb13114c8c8f35232aa724c33b5003` (`origin/main` equal at review time)  
**Disposition:** **NOT YET READY FOR THE OPERATOR ACT.** The activation commit is now genuinely
bound to its parent, exact two-path diff, and exact committed blobs. The remaining gap has moved to
the second half of the advertised two-commit protocol: the commit receipt need not be committed at
all, and local `HEAD` reachability is presented as proof of pushed repository-write authority even
though an arbitrary local repository satisfies it.

## Accepted repairs and reproduced baseline

- All four exact-HEAD GitHub workflows are green:
  - `errata` — [run 33568764767](https://github.com/s0fractal/manifesto/actions/runs/33568764767);
  - `embedded-claims-poc` — [run 33568764722](https://github.com/s0fractal/manifesto/actions/runs/33568764722);
  - `consumer-boundary` — [run 33568764772](https://github.com/s0fractal/manifesto/actions/runs/33568764772);
  - `papers-deposit-check` — [run 33568764698](https://github.com/s0fractal/manifesto/actions/runs/33568764698).
- `papers/corpus/test_corpus.py` and `papers/test_deposit_check.py` pass locally.
- The live root remains empty and the operator act/commit receipt do not exist. Current live vector:
  - `C2-MAP = REFUSED: ACTIVATION_NOT_APPLIED`;
  - `C2-MEAS = REFUSED: MEASUREMENT_NOT_REPLAYED`.
- The previous self-issued **activation-commit** path is closed. `verify_activation_commit` now
  checks that the named activation commit exists, resolves the exact parent, changes exactly the two
  authorized paths, and contains byte-identical trust-root/operator-act blobs.
- The exact stale-parent construction now refuses, and absence of `.git` returns typed
  `OPERATOR_COMMIT_PROVENANCE_UNAVAILABLE`.
- The pre-activation `--emit`/`--emit-act` path now refuses before writing when report/root
  validation fails.
- L3, operator act, and commit receipt are disclosed as claim operands, and the claim definition now
  describes the intended two-commit model rather than the old nonexistent Markdown readback.

These repairs are accepted. The findings below concern only what is still accepted as the second
commit and as operator authority.

## Findings

### P0-1 — The “commit-receipt commit” may be an untracked working-tree file

`strat_corpus_activation` strict-loads `CORPUS-C2-MAP-COMMIT-RECEIPT.json` from the working tree and
uses it to verify the **activation** commit. It never verifies a Git commit containing the receipt.
Consequently the promised second commit is not part of the credit boundary.

Independent real-Git reproduction:

1. Create a baseline commit.
2. Create a valid path-limited activation commit containing exactly the root and operator act.
3. Write a valid commit receipt into the working tree, but do **not** `git add` or commit it.
4. Run `strat_corpus_activation`.

Observed:

```text
receipt_status = ?? papers/every-check-spawns-more/CORPUS-C2-MAP-COMMIT-RECEIPT.json
result         = CHECKED
```

I then committed that receipt together with an unrelated file:

```text
receipt commit changed paths =
  UNRELATED.txt
  papers/every-check-spawns-more/CORPUS-C2-MAP-COMMIT-RECEIPT.json

result = CHECKED
```

Thus the consumer verifies a one-commit activation plus a mutable working-tree assertion, not the
documented exact two-commit act.

**Required repair:** verify the receipt commit as an execution event too. At minimum derive or name a
commit `R` and require:

- `R` exists and `R^` is the verified activation commit;
- `R` changes exactly `CORPUS-C2-MAP-COMMIT-RECEIPT.json`;
- the receipt blob at `R` equals the strict-loaded bytes being consumed;
- the live receipt bytes equal that committed blob;
- `R` is on the selected trusted history.

There is no receipt self-hash cycle: the receipt names the activation commit, while the verifier can
derive `R` from the current history/path or bind it through a later external tag/release commitment.
If the immediate rule is “the receipt commit must be current `HEAD`,” say so explicitly; if later
commits must remain possible, define a unique historical lookup or an external pin.

**Required regressions:** an untracked receipt and a receipt commit with an unrelated changed path
must both refuse with zero positive credit.

### P0-2 — `ancestor of HEAD` does not establish pushed repository-write authority

The documented authority rule says:

```text
repository-write authority, evidenced by the activation commit being an ancestor
of the branch tip (accepted into the pushed history)
```

The implementation checks only:

```bash
git merge-base --is-ancestor <activation> HEAD
```

This proves reachability from the current local `HEAD`; it does not prove that `HEAD` is a branch,
that the repository is `s0fractal/manifesto`, that any remote exists, that the commit was pushed, or
that the declared operator had repository-write authority. The production positive fixture itself
runs in a newly initialized local repository with no remote and therefore demonstrates this gap.

I reproduced `CHECKED` in a no-remote repository with:

```text
operator_identity = mallory:local
authority         = self-issued:local
git remote        = <empty>
activation commit = ancestor of local HEAD
```

The object/parent/path/blob checks remain valuable: they establish local Git execution integrity.
They do not authenticate the repository or operator.

**Required repair:** choose one honest authority contract:

1. **Narrow the claim** to “accepted into the currently supplied local Git history,” explicitly
   dropping `pushed` and `repository-write authority`. This is reproducible but not authentication.
2. **Keep repository-write authority** and add an external trust anchor: for example a signed
   commit/tag under a pinned key, an official GitHub repository/ref attestation verified through an
   API or exported signed receipt, or an equivalent Warrant-backed commitment. A configured remote
   URL or mutable local `origin/main` ref alone is not cryptographic proof, though an explicitly
   trusted CI environment may be a declared policy input.

The deposit/archive path should refuse when that authority evidence is unavailable. Do not let an
attacker-created `.git` directory upgrade the same files from refused to checked.

**Required regression:** a newly initialized no-remote repository containing perfectly coherent
local commits under an arbitrary operator identity must not satisfy a claim that says “pushed
repository-write authority.”

## P1 operational hardening

### P1-3 — `--emit-receipt` bypasses the newly added pre-write verification guard

`main()` handles `--emit-receipt` before computing/checking `ok = report_verified and
resulting_trust_root_valid`. It can therefore write a governance-looking receipt even when the
activation report/root validation has failed; it also does not validate the supplied activation
commit before writing.

This does not independently yield credit because the consumer later checks the activation commit,
but it partially reintroduces the operator footgun closed for `--emit` and `--emit-act`. Require the
valid post-activation state and verify the named commit before emitting the receipt.

## Minimal repair order

1. Bring the receipt **commit**, not merely the receipt file, into `verify_activation_commit` (or a
   sibling verifier): exact parent, exact single path, exact blob.
2. Decide whether the authority claim is local-history acceptance or authenticated pushed
   repository authority. Implement the chosen evidence boundary and align the prose.
3. Add the untracked-receipt, unrelated-receipt-path, and no-remote/self-authority negatives.
4. Put `--emit-receipt` behind validation and verify the named activation commit before writing.
5. Regenerate affected proposal/report/paper pins, keep the live root empty, and request one final
   exact-HEAD pass.

## Final assessment

The first commit of the governance transition is now verified correctly. The remaining blocker is
smaller than the previous one but still credit-bearing: **the checker accepts a receipt that was
never committed, and mistakes local reachability for pushed operator authority.** Until the second
commit and the authority anchor are real, do not apply the trust-root diff.

No corpus, L3, measurement, or claim-scope redesign is needed for this repair.
