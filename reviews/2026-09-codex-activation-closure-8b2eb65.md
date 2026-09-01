# C2-MAP activation closure review — `8b2eb65`

**Reviewer:** Codex (OpenAI), short exact-HEAD closure pass, 2026-09-02  
**Exact subject:** `8b2eb65a640d3dd5737d28acbe263cf23953400c` (`origin/main` equal at review time)  
**Disposition:** **NOT YET READY FOR OPERATOR ACT.** The previous three P0 repairs are materially
correct, the live root remains safely empty, and the machine-local evidence report genuinely
reproduces. Three narrower positive-credit paths remain open in the quarantine-free verifier and
deposit consumer.

## Accepted repairs and reproduced baseline

- All four exact-HEAD GitHub workflows are green:
  - `errata` — `33566543228`;
  - `embedded-claims-poc` — `33566543178`;
  - `consumer-boundary` — `33566543202`;
  - `papers-deposit-check` — `33566543241`.
- The machine-local generator reran byte-identically
  (`sha256:ebb3a12088bb348db6da7af27c4a782bf63574b531a2e3b4b8daeb03112c5aa4`),
  all 24 raw spans verified, and `verify_activation_report` passed the committed report.
- `engine_reason = REQUIRED_UNITS_UNSPECIFIED` and
  `policy_projection = MEASUREMENT_NOT_REPLAYED` are now correctly separated.
- The exact claim split is registered. With the committed empty root:
  - `C2-MAP = REFUSED: ACTIVATION_NOT_APPLIED`;
  - `C2-MEAS = REFUSED: MEASUREMENT_NOT_REPLAYED`.
- The proposal identity now binds `schema` and `for`; governance JSON uses strict loading on the
  principal proposal/report/root paths.
- The proposed 24-decision register is the exact closed set needed by the eight records.
- Operator readback currently resolves to:
  - base root `tr:723fb49b2492fa9b26b811271e7aae0bff927bd9dfc56c37fbbd801e7859325a`;
  - proposal `prop:75ba7e8717d155e660461d8efef9b5ca12bd2bf931fd37f7c33bfd1a5d5dad6d`;
  - report `arpt:9977891dbe399935e14f146a21205f9bc292bf0f1258e8247beacf9cdb9cb34e`;
  - diff `diff:0138b40555ea30ed3aa663fab0d8b0f5e42ffe39eee10684f723e1b708ac3596`;
  - proposed root `tr:67052a79590dab9ae733e4acbb0d02a0e0278e8f6f15483780cd0adca59756e5`.

These facts are accepted. The findings below concern what the quarantine-free positive consumer
still accepts after root activation.

## Findings

### P0-1 — A report that explicitly says every raw span failed still yields `CHECKED`

`verify_activation_report` compares the closed span-address set with the operand, but never requires:

```text
evidence.all_verified == true
evidence.span_count == 24
every evidence.spans[*].verified == true
assertions.all_24_spans_verified == true
```

Executable mutation in an isolated corpus copy:

1. Apply the proposal root.
2. Keep all span addresses/digests unchanged.
3. Set `evidence.all_verified = false`, every per-span `verified = false`, and
   `assertions.all_24_spans_verified = false`.
4. Recompute only `report_id`.

Observed:

```text
verify_activation_report = True
strat_corpus_activation  = CHECKED
```

This is not merely a missing assertion check. The claim's evidence class explicitly says the raw
span truth was machine-locally revalidated. A report that denies that fact cannot support the claim.

**Required repair:** independently require the exact positive evidence result, count, per-span
status, and corresponding assertion. Add this precise negative-report mutation to CI. Because raw
bytes are unavailable in CI, the verifier is checking the committed machine-local attestation — but
it must at least refuse an attestation whose own typed verdict is negative.

### P0-2 — Forged L3, record, and evaluation IDs remain independently “verified”

The verifier now discloses `l3_bundle_id` and eight record IDs, but checks only their shape/count:

```text
l3_bundle_id starts with "l3:"
eight record_ids are distinct
evaluation_id is non-empty
```

It neither recomputes them nor checks them against an independently pinned serialized L3/result
artifact. I replaced all three result identities with arbitrary strings, recomputed only the report
self-hash, and applied the valid root:

```text
l3_bundle_id = l3:FORGED
evaluation_id = eval:FORGED
record_ids = [rec:FORGED-0 ... rec:FORGED-7]
```

Observed:

```text
verify_activation_report = True
strat_corpus_activation  = CHECKED
```

This falsifies the verifier's docstring claim that it recomputes every non-raw relation. The report
currently publishes result addresses without a quarantine-free operand capable of validating them.

**Required repair:** emit a metadata-only serialized activation L3/result artifact containing the
eight full record bodies (no transcript bytes), or bind an equivalent independently generated closed
record manifest. The quarantine-free verifier must:

- recompute every record ID;
- validate/recompute `l3_bundle_id`;
- rerun L4 with the proposed root and manifest;
- recompute the evaluation ID and exact vector;
- require exact equality with the report.

Then add the forged-ID mutation above. Merely pinning the current strings in another self-authored
field is insufficient unless that field is an independently addressed proposal/record operand.

### P0-3 — The deposit consumer does not require an operator governance act

The stated lifecycle requires a path-limited operator commit plus `CORPUS-OPERATOR-ACT.md` readback.
But `strat_corpus_activation` checks only current root state + proposal + report. In the positive test,
copying the proposed trust root into a temporary directory is enough to return `CHECKED`; no operator
act file exists.

Observed in the same mutation environment:

```text
operator_act_exists       = False
strat_corpus_activation   = CHECKED
```

Thus `corpus_operator_readback.py` is advisory, not part of the credit boundary. A manual or
unattributed root edit is indistinguishable from the promised governance act.

**Required repair:** make a closed machine-readable operator-act artifact a required operand of the
deposit strategy. It must bind at least:

- exact base trust-root digest;
- proposal ID and activation-report ID;
- exact diff digest;
- resulting trust-root digest;
- operator identity/authority and act status;
- the authorized path set;
- parent commit identity or an equivalent external commitment.

The consumer must independently recompute the live root digest and refuse when the act is absent,
malformed, unpinned, or names another base/proposal/report/result.

The act cannot contain its own resulting Git commit ID without a hash cycle. Choose and document one
honest form:

1. one activation commit whose Git tree/parent is the external commitment, with the resulting commit
   ID reported outside that same tree; or
2. an activation commit followed by a separate readback/attestation commit that names the first.

Do not describe “fill both commit IDs after committing” as a single-commit operation.

## P1 semantic/operational findings

### P1-4 — “crossed transcripts” reintroduces the excluded provenance claim

The closed C2-MAP body and ledger call the eight acts “crossed transcripts,” while the exclusions say
`EXP-RVB-1c` provenance is asserted, not evidenced, and 1b/1c is ambiguous. The map proves the four
ROOT-token × observed-model pairs, not that these exact runs belong to the crossed experiment.

Use wording such as “the eight preserved transcripts selected for the governed 4×2 cohort” or
“transcripts over the four roots used in the crossed comparison.” Keep the explicit statement that
run-level 1b/1c provenance is not established.

### P1-5 — Readback does not fail closed on the expected base root

`corpus_operator_readback.py` prints `base_is_empty` and the base digest, but exits successfully based
only on report verification and resulting-root schema validity. A changed-but-valid base root can be
used without typed refusal.

Bind the expected base digest in the activation plan/operator-act contract and make `--emit` refuse
unless the current base equals it and is in the expected pre-activation state.

### P1-6 — Quarantine receipt still uses permissive JSON in the raw generator

The principal governance operands use `load_strict_json`, but the generator loads
`CORPUS-QUARANTINE-RECEIPT.json` with plain `json.loads`. Since the receipt is a provenance operand
whose digest is recorded by the report, use the same strict duplicate-key/non-finite profile there.

## Minimal repair order

1. Require the positive raw-verification fields and add the negative-verdict mutation.
2. Commit a metadata-only serialized L3/record manifest and independently recompute result IDs/L4 in
   `verify_activation_report`; add the forged-ID mutation.
3. Define the operator-act artifact/commit model and make it mandatory in `corpus_activation`.
4. Fail readback on the wrong base root; use strict receipt loading; narrow “crossed transcripts.”
5. Regenerate report/proposal identities as required, then run one genuinely final small pass.

## Final assessment

The current empty-root state is safe and the scientific address evidence remains accepted. The last
remaining gap is now extremely specific: the positive consumer must require a positive raw
attestation, verified result addresses, and an actual operator act — not merely a root that happens to
look activated.

Until those three checks exist, do not apply the trust-root diff.
