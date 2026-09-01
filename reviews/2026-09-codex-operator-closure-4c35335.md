# C2-MAP operator-closure review — `4c35335`

**Reviewer:** Codex (OpenAI), exact-HEAD adversarial closure pass, 2026-09-02  
**Exact subject:** `4c35335b1567429c5ee8bdb189d22d2664b65eb7` (`origin/main` equal at review time)  
**Disposition:** **NOT YET READY FOR THE OPERATOR ACT.** The span-verdict and serialized-L3
repairs close the previous evidence/result-address bypasses, and the committed empty root remains
safe. One positive-credit bypass remains: `CORPUS-OPERATOR-ACT.json` is required as a file, but its
claimed operator, authority, parent commit, and path-limited Git event are not authenticated or even
cross-checked against Git. Any caller can self-mint those strings and obtain `C2-MAP = CHECKED` in an
uncommitted directory.

## Accepted repairs and reproduced baseline

- Exact HEAD equals `origin/main`; the working tree was clean before this review file was written.
- All four exact-HEAD GitHub workflows are green:
  - `errata` — [run 33567697018](https://github.com/s0fractal/manifesto/actions/runs/33567697018);
  - `embedded-claims-poc` — [run 33567697010](https://github.com/s0fractal/manifesto/actions/runs/33567697010);
  - `consumer-boundary` — [run 33567697062](https://github.com/s0fractal/manifesto/actions/runs/33567697062);
  - `papers-deposit-check` — [run 33567697026](https://github.com/s0fractal/manifesto/actions/runs/33567697026).
- `papers/corpus/test_corpus.py` and `papers/test_deposit_check.py` pass locally.
- The live, committed state remains correctly non-crediting:
  - `C2-MAP = REFUSED: ACTIVATION_NOT_APPLIED`;
  - `C2-MEAS = REFUSED: MEASUREMENT_NOT_REPLAYED`;
  - `CORPUS-TRUST-ROOT.json` is still empty and `CORPUS-OPERATOR-ACT.json` is absent.
- Previous P0-1 is closed: a report with `all_verified=false`, any per-span `verified=false`, or a
  false `all_24_spans_verified` assertion now fails with `SPAN_VERDICT_NOT_POSITIVE`.
- Previous P0-2 is closed: the committed metadata-only L3 is strict-loaded, every record ID and the
  L3 ID are recomputed, L4 is rerun under the proposal-applied root, and the evaluation/vector must
  match. The forged result-address mutation now fails.
- The narrative narrowing is accepted. `C2-MAP` establishes an addressable governed 4x2 cohort over
  the four ROOT tokens and two observed models; it does **not** establish 1b/1c provenance and grants
  no measurement credit. `C2-MEAS` remains structurally separate and refused.
- The root application check is exact rather than subset-based, the quarantine receipt is strict
  loaded, and the readback refuses emission from a non-empty base.

## Finding

### P0-1 — The required operator act is still a self-issued assertion, not a verified governance event

`validate_operator_act` verifies the act's proposal/report/diff/root relations, which is useful. But
for the fields that are supposed to distinguish an operator act from an unattributed root edit it
only requires:

```python
operator_identity is a non-empty string
authority         is a non-empty string
parent_commit     is a non-empty string
authorized_paths  equals a declared list inside the same JSON
```

No layer verifies that `parent_commit` exists, that it is the actual parent of an activation commit,
that the activation commit changed exactly the two authorized paths, that its blobs equal the
validated root and act, or that the declared operator/authority controls that commit. The current
positive test makes the gap executable: at HEAD `4c35335` it deliberately passes the stale value
`parent_commit = "8b2eb65"` and still expects `CHECKED`.

I reproduced the stronger form in an isolated copy without creating a Git commit:

```text
operator_identity = mallory:anyone
authority         = self-asserted:anything
parent_commit     = not-a-git-commit
live root         = exact proposal-applied root
operator act      = self-generated JSON

strat_corpus_activation = CHECKED
```

Observed result:

```text
('CHECKED', None, {
  'operator': 'mallory:anyone',
  'authority': 'self-asserted:anything',
  'parent_commit': 'not-a-git-commit',
  ...
})
```

Thus the new file closes **absence of act**, but not **authorship/execution of act**. The consumer
still cannot distinguish the promised path-limited operator commit from two locally edited JSON
files containing arbitrary identity strings. Calling this `CHECKED` would spend positive credit on
an unverified governance assertion.

**Required repair:** separate the JSON intent from a machine-verifiable Git execution record. The
smallest honest model is the already-described two-commit form:

1. Activation commit contains exactly `CORPUS-TRUST-ROOT.json` and
   `CORPUS-OPERATOR-ACT.json`; the act names the exact pre-activation parent.
2. A separate readback artifact names the resulting activation commit (avoids the hash cycle).
3. Before returning `CHECKED`, the consumer verifies from the Git object database or an equivalent
   externally committed receipt that:
   - the activation commit exists and has exactly the named parent;
   - its changed-path set equals the closed two-path set;
   - the two committed blobs equal the validated live root and operator-act bytes;
   - the readback pins that activation commit;
   - the chosen operator-authority rule is explicit. If repository write authority is the rule,
     say so; if signer identity is claimed, verify a signature or another external credential.

If `.git` provenance is unavailable in a deposit/archive environment, fail closed with a typed
reason such as `OPERATOR_COMMIT_PROVENANCE_UNAVAILABLE` unless an exported, independently bound
commit receipt is supplied. Merely pinning an expected operator string in another unsigned JSON
would not close the self-issuance path.

**Required regression:** the exact `mallory / self-asserted / not-a-git-commit` construction above
must refuse with zero positive credit. The positive fixture must use a real temporary Git repository
and a real path-limited activation commit; the current stale-parent positive fixture should become a
negative.

## P1 hardening

### P1-2 — Readback may write activation artifacts after its own verification has failed

`main()` computes `ok = report_verified and resulting_trust_root_valid`, but checks `ok` only in the
final return code. `--emit` and `--emit-act` write files before that return. A bad report therefore
produces governance-looking artifacts and only then exits 1.

Move `if not ok: REFUSED` before either write. This is not currently a positive-credit bypass because
the deposit consumer re-verifies the report, but it is an avoidable operator-footgun at the most
sensitive boundary.

### P1-3 — The declared deposit operands and lifecycle text lag the executable contract

The C2-MAP claim manifest's `operands` list omits the now-required serialized L3 and future operator
act, even though the strategy consumes them. The list is currently descriptive only, but the report
therefore under-discloses the actual credit operands. Add:

```text
CORPUS-C2-MAP-L3-0.1.json
CORPUS-OPERATOR-ACT.json (after it exists)
the separate operator-commit readback/receipt (after it exists)
```

Also update `CORPUS-C2-MAP-CLAIM-0.1.md`: it still names the removed/nonexistent
`CORPUS-OPERATOR-ACT.md` instead of the JSON act plus the planned separate commit readback.

## Minimal repair order

1. Make the operator execution externally verifiable: real parent, exact changed paths, exact blobs,
   and a separate activation-commit readback/receipt.
2. Replace the synthetic positive operator fixture with a temporary real-Git fixture; make arbitrary
   identity/authority/parent and unrelated-path changes refuse.
3. Refuse `--emit`/`--emit-act` before writing whenever report/root validation fails.
4. Close the manifest/documentation operand list over L3, operator act, and commit readback.
5. Regenerate/pin affected identities, rerun the four suites, and request one short exact-HEAD pass.

## Final assessment

The scientific/data side of this activation is now substantially closed: the 24-span attestation is
positive, the L3/result identities are independently recomputed, the 4x2 address claim is narrower
than the unresolved measurement claim, and the live root is safely inactive. The remaining blocker
is governance rather than corpus semantics: **the system verifies what root would result, but not
that the named operator actually performed the named Git act.**

Do not apply the trust-root diff yet. Once the Git execution binding is real, this should genuinely
be a short final pass rather than another corpus redesign.
