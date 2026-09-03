# Embedded claims lineage — bounded retirement 0.1

**Status:** applied controlled-forgetting specimen. This is a tombstone and
transition record, not the embedded-claims specification. The current operational
surface is [`embedded-claims-poc/README.md`](embedded-claims-poc/README.md).

## Decision

At repository revision
`2a6e54d81a493623a32521ead5850e3ff7d8b92f`, five documents competed to describe
the embedded-claims format. Several retained pre-pivot requirements—inline
claims, `claim_ref`, a pending parser, and schematic receipts—after the executable
pipeline had adopted capsule containment and completed parse → compile → run.

They are removed from the default tree as one bounded lineage retirement. This
changes their admission status, not their historical existence or truth value.

| Historical subject | SHA-256 at the before revision | Mode | Reason |
|---|---|---|---|
| `drafts/EMBED-FORMAT-DESIGN.md` | `ee60c7ac375b4ea8d7931688d84840c4ee7bd0d066f5f3e32715b6bb3f6992cc` | `SUPERSEDED` | exploratory inline/recipe format no longer defines authoring eligibility |
| `drafts/EMBEDDING-SETTLEMENT.md` | `1740691754bef4383a91e7e85cdc6976c36160a1db5ca3459f181008eb43b57a` | `SUPERSEDED` | direct inline settlement survives only as legacy fixture substrate |
| `drafts/EMBEDDED-CLAIMS-ARCHITECTURE-0.1.md` | `57cc4f47d362bc4c296f866d06430ea482c7aa21d058db359b337c163fdcb726` | `SUPERSEDED` | a proposal and build plan was being mistaken for the implemented current route |
| `drafts/EMBEDDED-CLAIMS-REVIEW-0.1.md` | `5aac3a25db34c852a1b8cd51e6fd1c109f044b16ecd6f6d85f7c517cd73edc94` | `ARCHIVED` | review evidence informed the implementation but is not a current requirements document |
| `drafts/embedded-claims-poc/PARSER-THREAT-MODEL.md` | `789decea49df4bdf782de6bfce4ff9a2e4bea635b86f3ced3b3fef7424526dc9` | `ARCHIVED` | its pivot banner contradicted the inline requirements retained below it; executable adversarial fixtures now carry the active boundary |

`SUPERSEDED` means replacement of the active role, not semantic equivalence.
`ARCHIVED` means excluded from default reasoning, not refuted.

## Replacement and preserved evidence

The replacement is deliberately small:

- `drafts/embedded-claims-poc/README.md` — current human operational boundary;
- `drafts/embedded-claims-poc/fixtures/adversarial/EXPECTED.md` — executable
  parser/compiler oracle;
- `drafts/embedded-claims-poc/{parser,compiler,runner,claims}.py` — current route;
- `drafts/EMBEDDED-CLAIMS-E2E-0.1.md` — non-vacuous real-document specimen;
- `.github/workflows/embedded-claims-poc.yml` — clean-environment consumer.

The phase-1 inline harness remains present as explicitly
`LEGACY-NONCANONICAL` evidence. It preserves mutation, freshness, binding, effect,
and mismatch falsifiers; it does not license inline authoring in the canonical
route.

## Known loss

Default readers no longer receive:

- the long MYC/Trinity/SPORE design genealogy;
- rejected syntax alternatives and the chronological review conversation;
- the complete prose derivation of every threat and identity distinction;
- the original build phases and open-decision queue.

Those losses are accepted because the implemented code, executable negative
fixtures, and compact operational boundary now carry the active obligations.
Historical research remains allowed with status.

## Historical retrieval

The exact bytes can be recovered while the Git object remains available:

```sh
git show 2a6e54d81a493623a32521ead5850e3ff7d8b92f:<historical-path>
```

Any retrieved subject must carry this envelope:

```text
HISTORICAL EMBEDDED-CLAIMS ARTIFACT
retired from default surface after 2a6e54d
current admission: EXCLUDED
current operational replacement: drafts/embedded-claims-poc/README.md
do not treat as current precedent without an explicit re-adoption act
```

Git availability is best-effort; this record does not promise permanent storage.

## Applied transition

- exact before revision: `2a6e54d81a493623a32521ead5850e3ff7d8b92f`
- apply commit: `PENDING-RECEIPT-COMMIT`
- apply tree: `PENDING-RECEIPT-TREE`
- authority: repository owner instruction in the working session
- changed scope: the five retired subjects, the operational README, its active
  references, the bounded falling consumer, and verifier pins rotated only if
  closure bytes changed

The apply commit and tree are filled by a separate receipt commit so this record
does not attempt to contain its own commit identity.

## Executable postconditions

`tools/embedded_claims_surface_check.py` verifies that:

- all five retired paths are absent;
- no non-historical tracked file cites them as current;
- the replacement declares capsule-only eligibility, the legacy boundary, and no
  document-level verdict;
- the workflow runs this check and retains the non-empty CLI oracle;
- mutation controls prove the checker fails on subject resurrection, zombie
  reference, and replacement-boundary loss.

The existing parse, compile, runner, CLI, and phase-1 fixture suites must also
remain green. Their success proves only the preserved bounded behavior, not that
retirement was wise or that the remaining ontology is complete.
