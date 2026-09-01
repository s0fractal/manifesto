# C2-MAP final activation-readiness review — `34819ce`

**Reviewer:** Codex (OpenAI), exact-HEAD closure pass, 2026-09-02  
**Exact subject:** `34819cebaec51f9fec2c1bb503da0d4a020487fa` (`origin/main` equal at review time)  
**Disposition:** **THE CREDIT BOUNDARY IS CLOSED UNDER ITS DECLARED POLICY, BUT DO NOT RUN THE
OPERATOR RECIPE YET.** No remaining positive-credit bypass was found in the two-commit execution
model. One operational activation blocker remains: the production deposit workflow uses a shallow
checkout and therefore will not possess the activation commit and pre-activation parent that the new
verifier correctly requires.

## Accepted closure

- All four exact-HEAD GitHub workflows are green:
  - `errata` — [run 33569806060](https://github.com/s0fractal/manifesto/actions/runs/33569806060);
  - `embedded-claims-poc` — [run 33569806079](https://github.com/s0fractal/manifesto/actions/runs/33569806079);
  - `consumer-boundary` — [run 33569806071](https://github.com/s0fractal/manifesto/actions/runs/33569806071);
  - `papers-deposit-check` — [run 33569806058](https://github.com/s0fractal/manifesto/actions/runs/33569806058).
- Local `test_corpus.py` and `test_deposit_check.py` pass.
- The live root remains empty; operator act and commit receipt remain absent:
  - `C2-MAP = REFUSED: ACTIVATION_NOT_APPLIED`;
  - `C2-MEAS = REFUSED: MEASUREMENT_NOT_REPLAYED`.
- Previous P0-1 is closed:
  - an untracked receipt returns `RECEIPT_COMMIT_MISSING`;
  - a receipt commit touching an unrelated path returns `RECEIPT_COMMIT_PATHS`;
  - the verified receipt commit is the immediate child of the activation commit, changes exactly
    the receipt path, and contains the exact consumed receipt bytes.
- Previous P0-2 is closed **under the explicitly declared non-cryptographic policy input**:
  - no trust anchor refuses;
  - no remote/ref refuses;
  - locally committed but unpushed commits refuse against the declared fetched remote ref;
  - both activation and receipt commits must be ancestors of that ref.
- Previous P1-3 is closed: `--emit-receipt` verifies the report and the named path-limited activation
  commit before writing.
- The real two-commit positive fixture and the five advertised negative fixtures execute as stated.

The corpus/L3/claim-scope side needs no further repair for this activation.

## Remaining activation blocker

### P1-1 — The production CI checkout cannot evaluate the activated state

`.github/workflows/papers-deposit-check.yml` uses `actions/checkout` without `fetch-depth`, whose
effective checkout is shallow. Today the live root is empty, so `strat_corpus_activation` returns
`ACTIVATION_NOT_APPLIED` before it needs historical Git objects and the workflow stays green.

After the two operator commits, the checker must read:

- the receipt commit at/under the trusted ref;
- its activation-commit parent;
- the activation commit's pre-activation parent;
- both commits' trees/diffs.

I reproduced the future production shape with the valid two-commit history pushed to a bare remote,
then cloned it at depth 1. The remote-tracking ref existed, but only the receipt commit was present:

```text
git rev-list --count HEAD = 1
strat_corpus_activation   = REFUSED: OPERATOR_COMMIT_UNVERIFIED
fault                     = ACTIVATION_COMMIT_MISSING
```

This is safe fail-closed behavior, not a credit bypass. But following the current operator recipe
would make the live deposit workflow red instead of demonstrating the intended
`C2-MAP = CHECKED / C2-MEAS = REFUSED` transition.

**Required repair before activation:** fetch sufficient history in the deposit workflow. Prefer the
unambiguous form:

```yaml
- uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8
  with:
    fetch-depth: 0
```

Alternatively fetch the exact receipt, activation, and parent objects plus the declared
`refs/remotes/origin/main`, but that is more brittle. Add a small preflight or CI fixture showing
that the activated two-commit history verifies in the same checkout topology used by the workflow.
This workflow repair must be committed **before** the operator act, because the activation commit is
restricted to the exact two governance paths.

## Declared trust-anchor boundary (accepted, with wording hardening recommended)

The new anchor is honestly documented as a policy input, not cryptographic proof. Under that stated
model I do not treat local ref mutability as a new P0. The exact guarantee is:

> the commits are ancestors of a locally available remote-tracking ref whose configured origin URL
> matches the manifest's repository selector.

It is **not independently proven** that the ref was fetched from GitHub or that the operator owns
repository-write authority. I confirmed that a local repository can configure
`https://github.com/s0fractal/manifesto.git`, set `refs/remotes/origin/main` with `git update-ref`, and
obtain `CHECKED` without network push. That is consistent only if the fetched ref/config is explicitly
trusted as environmental input.

Two small hardenings are recommended, but are not blockers under the accepted policy:

1. Replace substring matching (`repo in remote_url`) with exact normalized allowlisted HTTPS/SSH
   repository identities; the current check also accepts lookalike URLs containing
   `s0fractal/manifesto` as a substring.
2. Use reason/claim wording such as `IN_DECLARED_REMOTE_REF` rather than mechanically claiming
   `PUSHED` or authenticated operator identity. The current code proves ref membership under a
   trusted local anchor, not network provenance. A signed tag/commit or GitHub attestation remains
   the correct later authenticity upgrade.

## Minimal final sequence

1. Commit the workflow history-depth repair while the trust root is still empty.
2. Confirm that exact HEAD is green and `origin/main` equals it.
3. Generate root + act with that exact HEAD as parent.
4. Make the exact two-path activation commit.
5. Generate the receipt and make the exact one-path receipt commit.
6. Push both, then require live CI to report:
   - `C2-MAP = CHECKED` with the two verified commit identities;
   - `C2-MEAS = REFUSED: MEASUREMENT_NOT_REPLAYED`;
   - no document-level global badge.

## Final assessment

The adversarial activation construction itself is now coherent and bounded. The only pre-`go`
blocker found at `34819ce` is mundane but real: the official checker currently cannot see the Git
history it has been taught to verify. Fix the checkout depth first; then the operator act can proceed
without another architecture round.
