# SSD pack — status

**Non-normative. Nothing in this directory is modified by this note.** The
pack's receipt, its numbers, its acceptance verdict and its dependency metadata
stand exactly as they were accepted on 2026-08-30.

## What this pack is, and what it is not

The pack is **historically sealed**: it records a real decision chain, and the
settlement it carries was really performed. What it does **not** carry is a
**dependency closure** — the bytes its claims were evaluated against were never
written down.

That has a consequence, and it is better stated than discovered:

> **A strict replay of this pack is impossible.** Changing a file it once
> counted is **drift**, not a retroactive refutation of the original
> settlement.

Re-running the gate today reads *today's* files. Three `layer: repo` counts no
longer hold, because the files grew:

```text
/FLOW/ in FLOW.md              = 12   today 14
/RVB/ in drafts/RVB-0.1-….md   = 12   today 13
/Теза/ in README.md            =  7   today  8
```

`atp_total` is identical at 5638 — the Σ-GLYPH layer is stable. The three
differences are about mutable files, not about the machine.

## What was NOT done here

- The receipt was not edited.
- The `settled_true: 11 / refuted: 0` tally was not revised.
- **No sidecar was written claiming these dependencies were pinned at
  settlement time.** They were not, and a document asserting otherwise would be
  a fabricated history — the one repair that would be worse than the gap.

## How the tooling treats it

`tools/replay_pack.py` refuses this pack by name:

```text
$ python3 tools/replay_pack.py replay drafts/ssd-pack
REPLAY: LEGACY_UNPINNED
```

It does not read current files and call the difference `REFUTED`, does not
simulate a successful replay, and does not reconstruct the missing pins after
the fact. `drift` answers `LEGACY_UNPINNED` for the same reason: with nothing
pinned, there is nothing to compare the checkout against.

Both behaviours are controls in `tools/replay_controls.py`.

## What replaces it going forward

New packs carry their dependency bytes with them, and replay and drift are two
operations that cannot be confused:

```text
replay -> MATCH | REPLAY_MISMATCH | DEPENDENCY_MISSING | EVALUATOR_UNVERIFIED
          | EVALUATOR_MISMATCH | PROFILE_MISMATCH | MALFORMED_PACK
          | LEGACY_UNPINNED
drift  -> SAME  | DRIFT | CURRENT_MISSING | MALFORMED_PACK | LEGACY_UNPINNED
```

A `MATCH` there requires the pinned dependency bytes; the pinned **evaluator
artifact**, supplied as a **wheel** and checked to be the engine that actually
runs — a receipt describes an artifact and is not accepted as one; the pinned
**profile sources**, whose set and `profile_id` must be this profile's rather
than whatever the pack chose to list; and every field of a **closed** receipt.

A pack of the new format that is broken — including a `pack.json` that exists
and will not parse — is `MALFORMED_PACK`. That is not the same as being
historical: a defect must not be filed as an era.

`drafts/replay-fixture-0.1/` is the first such pack. Its historical replay stays
`MATCH` while its current checkout reports `DRIFT`, which is the combination
this pack could not express and the reason the format changed.

Migrating the existing packs is not in scope, and this note is not a plan to do
it.
