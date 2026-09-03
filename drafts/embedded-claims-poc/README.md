# Embedded claims — current operational surface

**Status:** implemented research pipeline, capsule-only. This is the current
operational description of the code in this directory. It is not a protocol
standard, a proof of semantic adequacy, or a document-level truth badge.

Historical design drafts and the pre-pivot parser threat model were removed from
the default surface by the bounded retirement recorded in
[`../EMBEDDED-CLAIMS-RETIREMENT-0.1.md`](../EMBEDDED-CLAIMS-RETIREMENT-0.1.md).
They remain retrievable from Git with their retirement status.

## Canonical route

```text
explicit document
  → exact live region
  → fenced json capsule.v2 containing its claim
  → PARSE
  → COMPILE into a self-contained addressed bundle
  ── epistemic membrane ──
  → RUN each record
  → vector REPORT
```

The canonical route is **CAPSULE-ONLY**:

- a file is processed only when explicitly named; there is no repository sweep;
- machine eligibility exists only inside exact
  `manifesto-claims:begin/end` markers;
- the exact fence opener is ` ```json capsule `;
- the closed `manifesto.capsule.v2` body contains `claim.local_id`,
  `claim.class`, and `claim.payload`;
- prose outside a live capsule is inert, including claims, metaphors, examples,
  values, and marketing language;
- an inline `⟦class: payload⟧` expression is **LEGACY-NONCANONICAL** and never
  receives credit through this route.

The format makes an authorial verification request explicit. It does not infer
what surrounding prose “really claims”.

## Layer boundaries

| Layer | Input → output | What it cannot claim |
|---|---|---|
| `parser.py` | named Markdown bytes → regions, capsule spans, `VALID/INVALID/INERT` | schema validity, execution |
| `compiler.py` | `VALID` parse report → strict capsule.v2 → addressed, self-contained records | replay or truth |
| `runner.py` | `COMPILED` bundle → one execution result per record | document-level verdict |
| `claims.py` | orchestration of parse → compile → run | new verification semantics |

The runner rechecks every record identity and link before invoking an evaluator.
A malformed or incoherently mutated bundle is refused before execution. A
coherently rebuilt schema-valid bundle is a new bundle; authenticity requires an
external commitment or receipt and is not claimed here.

## Status and credit boundary

Execution results are per-record:

```text
REPLAYED | MISMATCH | STALE | UNVERIFIED | DECLARED
```

Binding remains separate:

```text
UNTIED | ASSERTED
```

Execution never upgrades a binding. A document receives **NO DOCUMENT-LEVEL
VERDICT**: several `REPLAYED` records do not make their composition true, safe,
legal, complete, or semantically adequate. `--strict` is only an exit-code policy
over a non-empty vector; the JSON output remains per-record.

## Canonicalization and identities

`canonical.py` pins the implemented closed JSON profile:

- sorted Unicode-code-point keys and compact separators;
- UTF-8 without BOM;
- duplicate keys, floats, lone surrogates, and out-of-range integers refused;
- SHA-256 record IDs with domain separation.

The compiler separates claim, plan, dependency, binding, occurrence, capsule,
result-value, and evaluation identities. In particular:

- changing dependency bytes rotates the dependency and plan;
- identical values may share a value identity;
- distinct predicates cannot share an evaluation identity merely because their
  observed value is equal;
- occurrence identity binds document digest plus exact source span;
- binding identity is claim-bound.

The parser identity binds the installed `markdown-it-py==4.2.0` and
`mdurl==0.1.2` package bytes plus the hash-locked dependency file. Settlement
verifier identities bind the verdict-determining Python closure and the released
`sigma-glyph==0.6.7` evaluator bytes. They do not bind the interpreter build or
operating system.

## Run

From the repository root:

```sh
python3 -m venv .venv
.venv/bin/pip install "sigma-glyph==0.6.7"
.venv/bin/pip install --require-hashes \
  -r drafts/embedded-claims-poc/requirements-parser.lock

.venv/bin/python drafts/embedded-claims-poc/claims.py run \
  drafts/EMBEDDED-CLAIMS-E2E-0.1.md
.venv/bin/python drafts/embedded-claims-poc/claims.py run --strict \
  drafts/EMBEDDED-CLAIMS-E2E-0.1.md
```

The live specimen contains one world claim that counts a pinned snapshot of the
root README headings. `REPLAYED` establishes only that count under that regex,
dependency snapshot, and verifier closure.

The executable oracles are:

```sh
.venv/bin/python tools/embedded_claims_surface_check.py
.venv/bin/python tools/embedded_claims_surface_check.py --selftest
.venv/bin/python drafts/embedded-claims-poc/test_poc.py
.venv/bin/python drafts/embedded-claims-poc/test_parser.py
.venv/bin/python drafts/embedded-claims-poc/test_compiler.py
.venv/bin/python drafts/embedded-claims-poc/test_runner.py
.venv/bin/python drafts/embedded-claims-poc/test_cli.py
```

The CI workflow runs the same layers against a clean installation and requires a
non-empty exact-scope end-to-end result.

## Preserved legacy substrate

`verify.py`, `settle_core.py`, `schema.py`, and `fixtures/{valid,invalid,limits}`
form the earlier inline phase-1 harness. It remains executable because it carries
useful negative evidence: freshness, wrong binding, verifier mismatch, state
observation, and the demonstrated write-then-delete blind spot. It is not an
alternative authoring standard and does not feed the capsule-only parser.

This boundary is deliberate: preserving a falsifier is not the same as admitting
its old syntax as current precedent.

## Honest limits

- A `REPORT` is not an authenticity receipt.
- Effects are observed, not sandbox-enforced; transient or external effects may
  be invisible.
- Semantic adequacy and prose binding remain open.
- The implementation is single-operator and not a distributed trust system.
- Passing its own fixtures is not independent validation.
- `sigma-glyph==0.6.7` is a deliberate evaluator pin; changing it rotates the
  verifier identities and requires an explicit re-pin.
