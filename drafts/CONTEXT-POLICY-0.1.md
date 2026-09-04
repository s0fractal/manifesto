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

`default` is the working set: the active surface rows and the live operands. The
five retired subjects are absent from it — not their paths, not their digests,
not their reasons. What default carries instead is the short tombstone status
section 8.1 permits: the record's address, the number of its subjects withheld,
the declared admission, and the command that shows them.

`--mode historical` adds the five subjects of that one record, each with an
inseparable envelope: retirement mode, loss, relation and replacement, a
retrieval address (`git show <before-revision>:<path>`), and the admission
triple. A historical fact that grants `normative_use` or claims default
admission is a refusal, not a warning.

**The expansion is the pair, and only the pair.** The surface's own two retired
rows (`multi-model-raid-promised`, `sev-projection-repo`) are *not* this
specimen's history: they belong to no pair, and the selected record never
addressed them. They enter neither mode, and the before/after delta below is the
pair's rather than a class-wide sweep of everything this repository ever
retired. A retired fact from outside the record — another act's subject, or a
retired row that merely shares the class — is `HISTORICAL_ADMITS_UNRELATED_FACT`.
Those rows keep their own owner and their own consumer; nothing here withholds
or resolves them.

**Re-entry into default has no door here, and that is the specimen's honest
edge.** The record's admission triple is bound exactly as it stands, with
`default: EXCLUDED`; `INCLUDED` is refused as `READOPTION_NOT_IMPLEMENTED`
rather than honoured. An earlier draft of this specimen treated that one field
as the gate, so an ordinary field edit — leaving the existing `authority` object
byte-for-byte unchanged — resurrected all five subjects into the default set and
passed every check. That is laundering, not governance: the authority the record
cites was addressed to the retirement and made no decision about a later return,
and reusing its address spends an act that never happened. Readmission needs an
explicit governed transition with a decision identity of its own; this specimen
does not implement one, does not approximate one, and the gap to section 3.6 is
named here rather than papered over. Historical retrieval stays open and stays
non-crediting. As everywhere else in this repository, an addressed act is not a
proof that it was within anyone's power (I6).

## Counting grammar

Reproducible numbers need a closed definition of what is counted:

- A **fact** is one addressable item the owners already carry, of exactly three
  kinds: one `surface-row` (id = row id), one `replacement-operand` (id = path),
  one `retired-subject` (id = path). Prose, comments, this file and the tool's
  own output are not facts.
- **Retired facts** are the facts carrying `status: RETIRED`, which in this
  specimen are exactly the selected record's five subjects. Rows of class
  `retired` are not counted here at all, in either mode, because they are not
  this pair.
- **Bytes** are the utf-8 length of the canonical render of the whole view —
  `json.dumps(sort_keys=True, indent=2, ensure_ascii=False)` plus one trailing
  newline. Any other serialization is a different number.
- **Unresolved** is per view: one for each source entry that is address-only (an
  external locator with no in-repo byte pin), plus one for each retired fact
  whose retrieval address is not a `git show` locator into this repository. It
  counts honesty, not failure — an operand that should resolve and does not is a
  refusal, and never reaches a count.
- **Before** is `--mode historical`: the working set plus the selected pair's
  retired subjects — not everything the owners name, and not everything the
  repository ever retired. **After** is `--mode default`. The delta is this one
  pair's, not the repository's, and it is not a claim about any agent's real
  prompt.

Measured on the tree that carries this file (`python3 tools/context_view.py
--measure`, and the numbers are a label — the command is the source of truth):

```
BEFORE   mode=historical facts=17 bytes=15110 retired-facts=5 unresolved=0
AFTER    mode=default    facts=12 bytes=7158 retired-facts=0 unresolved=0
DELTA    facts=-5 bytes=-7952 retired-facts=-5
```

The retired-fact delta is 5 — the pair's subjects — and not 7. An earlier draft
reported 7 because historical mode also swept in the two retired surface rows,
which this specimen never selected; that number was measuring more than the one
pair it advertised. Unresolved is 0 in both modes here: the address-only links
in this repository belong to those two rows, so this specimen neither resolves
them nor counts them, and they stay their owner's business.

## Controls

`python3 tools/context_view.py --selftest` burns 31 mutations, including the
three this specimen stands or falls on:

- **no silent resurrection** — a retired subject in the default view is
  `DEFAULT_ADMITS_EXCLUDED_SUBJECT` and a retired row is
  `DEFAULT_ADMITS_RETIRED_ROW`. The exclusion is read from the record rather
  than produced by luck: the one-field edit runs through the live owner and
  check path, the owner consumer accepts it — `INCLUDED` is a legal value of its
  enum and the `authority` object is untouched — and this specimen still refuses
  it as `READOPTION_NOT_IMPLEMENTED`, at `bind`, at `build`, at the default
  invariant, and again when the same flip is written to disk and read back
  through the owner's real loader. The whole admission triple is bound, so an
  owner-legal edit that
  quietly closed historical review is `SPECIMEN_ADMISSION_UNEXPECTED`.
- **no widening past the pair** — a well-formed retired fact the record never
  addressed, whether a retired surface row or another act's subject, is
  `HISTORICAL_ADMITS_UNRELATED_FACT`; dropping half the pair is
  `HISTORICAL_PAIR_INCOMPLETE`. The advertised delta cannot grow by importing
  facts that merely share a class.
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
- No re-adoption record type was introduced, and no readmission path of any kind
  exists in this specimen. A record's `admission` field is *not* treated as the
  gate — that was the earlier draft's mistake — so a subject retired under this
  record has no implemented way back into the default set. Section 3.6's
  Re-adoption Record remains unbuilt, and this specimen refuses rather than
  approximates it.
- The two retired surface rows were left entirely alone. This specimen neither
  withholds nor expands them; that is one pair's scope, not a repository-wide
  forgetting policy.
- No cross-repository consumer was touched; Phase 4 stays closed.
- The byte delta measures the derived document, not attention. Whether a smaller
  default view actually reduces zombie precedents is the falsifier below, and it
  is not answered by any number in this file.

**Falsifiers:** a retired subject reachable from the default view; any state
other than the declared `EXCLUDED` admission producing a view instead of a
refusal; a retired fact in the historical view that the selected record never
addressed; a retired fact retrieved without its envelope; a deleted
record, subject or operand that still produces green; an operand believed rather
than recomputed; numbers that do not reproduce from the grammar above; or a
model given the default view that goes on citing retired artifacts as current —
which would falsify the specimen's whole premise, not just its implementation.
