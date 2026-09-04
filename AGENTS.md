# AGENTS.md

Rules for any agent working in this repository. This file is deliberately thin
and stable: rules, commands and links only. It carries no digests, no copied
facts, no status summaries and no generated context — those rotate, and a
confidently stale instruction file is worse than none. Everything that rotates
lives in the owners below and is derived on demand.

This file is not an act of adoption and grants no authority to anyone. It
records how to read what the repository already declares.

## Canonical owners

- `surface/rows.json` — what this repository currently treats as operational,
  normative or retired, one typed predicate per row. Consumer:
  `tools/active_surface.py`.
- `drafts/retirement-records/` — structured retirement records: which subjects
  left the active surface, by which addressed act, with which loss, and what
  holds the role now. Consumer: `tools/retirement_record_check.py`.
- `CONTROLLED-FORGETTING-0.1.md` — the retirement policy those records answer
  to. Its adopted scope, and the parts that stay non-normative, are named in its
  own status section; read that before treating any of it as binding.

There is no second registry. Nothing derived from these owners is committed. If
a derived view and an owner disagree, the owner wins and the check fails.

## Retrieval

**Default** — the working set. Retired subjects are not in it, by policy, not by
accident:

```sh
python3 tools/context_view.py
```

**Explicit historical** — the same set plus every retired fact, each arriving
with its retirement mode, loss, relation and replacement, retrieval address and
admission status:

```sh
python3 tools/context_view.py --mode historical
```

Regenerate and verify from a cold start — no state is needed beyond a full
clone, and `--check` recomputes every operand from bytes rather than believing
any document:

```sh
python3 tools/context_view.py --check      # bind the owners, verify the view
python3 tools/context_view.py --selftest   # the mutation controls
python3 tools/context_view.py --measure    # default vs historical, in facts and bytes
```

Scope and counting grammar: `drafts/CONTEXT-POLICY-0.1.md`.

## Rules

1. **Historical mode is archaeology, not precedent.** Availability is not
   admission. Quote a retired artifact only with its status attached: a
   withdrawn revision said X; the current surface does not adopt it.
2. **Do not hand a retired subject back into the default set.** Re-entry is an
   owner act on the record it was retired by, not an edit to a view, a tool or
   this file. Proposing one is allowed; performing one is not.
3. **Do not commit generated context.** The view is printed on demand. A checked
   artifact needs a demonstrated consumer first.
4. **Run any check that reads `git ls-files` after `git add`.** Before staging it
   sees a different world, and passes for the wrong reason.
5. **Branch work is non-canonical.** Push, merge, tag, release, deposit and
   publication are owner acts.
6. **Do not add a second registry, schema or framework** to carry something an
   existing owner already carries. Extend the owner, or say why you cannot.
7. **No document-level verdicts.** Checks report per-row, per-record, per-fact
   vectors; green means the named predicate held, never that a document is true.
