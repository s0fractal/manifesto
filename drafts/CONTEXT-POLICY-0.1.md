# CONTEXT-POLICY-0.1 — one derived context view, default against historical

**Status:** draft, non-normative. It adopts nothing, retires nothing and grants
no authority. It is one specimen of what CONTROLLED-FORGETTING-0.1 calls Phase 3
— repo-local tooling that separates default retrieval from historical retrieval
— and it is deliberately smaller than that phase: **one** active/retired pair,
**one** derived view, generated on demand.

The rules an agent reads are in the root `AGENTS.md`, which stays thin on
purpose. The view is `tools/context_view.py`. Nothing is committed by it.

## The pair

Exactly one, and it is not invented here: the applied act recorded in
`drafts/retirement-records/embedded-claims-lineage.json`. That record already
names both sides — five retired subjects with per-subject modes and digests, and
eight live replacement operands under `relation: replaced-by`. This specimen
adds no third party to that pair and no per-subject pairing the record does not
state; the act is lineage-shaped, so the pair is the subject set against the
operand set.

Verified rather than assumed before choosing it: the two retired rows in
`surface/rows.json` both carry `successor: null`, so neither is half of a pair,
and the lineage record is the only place in this repository where a retired side
and a live side are bound to each other by bytes.

## The two owners, and why there is no third

`surface/rows.json` and `drafts/retirement-records/` are read through their own
consumers — `tools/active_surface.py` and `tools/retirement_record_check.py` —
so every pinned source is recomputed from disk and every retired subject's
digest is recomputed from the git object at the before revision. The view holds
no facts of its own; deleting it loses nothing but a projection. A second
active/retired registry is exactly what this specimen refuses to build.

## Default against historical

`default` is the working set: active rows and the live operands. The five
retired subjects are absent from it — not their paths, not their digests, not
their reasons — and so are the retired rows. What default carries instead is the
short tombstone status section 8.1 permits: the record's address, the number of
facts withheld, the declared admission, and the command that shows them.

`--mode historical` adds every retired fact with an inseparable envelope:
retirement mode, loss, relation and replacement, a retrieval address
(`git show <before-revision>:<path>`), and the admission triple. A historical
fact that grants `normative_use` or claims default admission is a refusal, not a
warning.

**Re-entry into default has exactly one door:** `admission.default` reading
`INCLUDED` in the canonical record. That is an edit to an owner record, which
its own consumer holds to an addressed authority and to subjects that still
bind. No such act exists, and none is fabricated here — the control flips the
field on an in-memory copy, sees the subjects appear, and the live record stays
`EXCLUDED`. As everywhere else in this repository, an addressed act is not a
proof that it was within anyone's power (I6).

## Counting grammar

Reproducible numbers need a closed definition of what is counted:

- A **fact** is one addressable item the owners already carry, of exactly three
  kinds: one `surface-row` (id = row id), one `replacement-operand` (id = path),
  one `retired-subject` (id = path). Prose, comments, this file and the tool's
  own output are not facts.
- **Retired facts** are the facts carrying `status: RETIRED`: the record's
  subjects plus rows of class `retired`.
- **Bytes** are the utf-8 length of the canonical render of the whole view —
  `json.dumps(sort_keys=True, indent=2, ensure_ascii=False)` plus one trailing
  newline. Any other serialization is a different number.
- **Unresolved** is per view: one for each source entry that is address-only (an
  external locator with no in-repo byte pin), plus one for each retired fact
  whose retrieval address is not a `git show` locator into this repository. It
  counts honesty, not failure — an operand that should resolve and does not is a
  refusal, and never reaches a count.
- **Before** is `--mode historical`: everything the two owners name. **After** is
  `--mode default`. The delta is this specimen's, not the repository's, and it
  is not a claim about any agent's real prompt.

Measured at the commit that introduced this file (`python3 tools/context_view.py
--measure`, and the numbers are a label — the command is the source of truth):

```
BEFORE   mode=historical facts=19 bytes=18482 retired-facts=7 unresolved=3
AFTER    mode=default    facts=12 bytes=7158 retired-facts=0 unresolved=0
DELTA    facts=-7 bytes=-11324 retired-facts=-7
```

The three unresolved links are external or chat-level addresses two retired rows
already carried; the specimen resolves none of them and claims none of them.

## Controls

`python3 tools/context_view.py --selftest` burns 23 mutations, including the two
a forgetting policy stands or falls on:

- **no silent resurrection** — a retired subject in the default view is
  `DEFAULT_ADMITS_EXCLUDED_SUBJECT` and a retired row is
  `DEFAULT_ADMITS_RETIRED_ROW`; flipping `admission.default` to `INCLUDED` is
  what makes the subjects appear, so the exclusion is read from the record and
  is not an accident of the generator; readmission with an unaddressed authority
  is refused by the owner consumer, and it reaches only the subjects that record
  addresses — a row it never named stays out.
- **no starvation** — deleting the record, a subject or an operand fails closed
  (`SPECIMEN_RECORD_MISSING`, `SPECIMEN_SUBJECT_COUNT`, `SPECIMEN_OPERAND_COUNT`)
  rather than producing a smaller green set. The scope counts are pinned in the
  consumer, where a record cannot edit them.

The rest cover stale, missing, malformed, escaping and duplicate operands, an
owner refusal being surfaced instead of swallowed, envelope loss on historical
facts, an empty or narrowed view, and render determinism.

## Limits, and what was deliberately not done

- No row was added to `surface/rows.json` for this specimen. That would pin the
  tool's digest into the surface and buy an operational credit this experiment
  does not need; the CI step is the live consumer instead.
- No re-adoption record type was introduced. The record's own `admission` field
  is the gate, and the difference between that field and a full Re-adoption
  Record (section 3.6) is not papered over here.
- No cross-repository consumer was touched; Phase 4 stays closed.
- The byte delta measures the derived document, not attention. Whether a smaller
  default view actually reduces zombie precedents is the falsifier below, and it
  is not answered by any number in this file.

**Falsifiers:** a retired subject reachable from the default view while the
record says `EXCLUDED`; a retired fact retrieved without its envelope; a deleted
record, subject or operand that still produces green; an operand believed rather
than recomputed; numbers that do not reproduce from the grammar above; or a
model given the default view that goes on citing retired artifacts as current —
which would falsify the specimen's whole premise, not just its implementation.
