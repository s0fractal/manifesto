# ACTIVE-SURFACE-0.1 — what this repository currently treats as working, by class

**Status:** draft, non-normative. Generated artifact `ACTIVE-SURFACE.json`; source
`surface/rows.json`; generator `tools/active_surface.py`; controls
`tools/active_surface_controls.py`. `AGENTS.md` is untouched by this draft; if it
ever points here, it points, it does not copy.

**Why a generated file and not a hand-written registry.** A registry written by hand
drifts the day after it is written and nobody notices, because nothing refuses.
Here the rows are written by hand, but the *classification* is refused whenever the
row's evidence does not carry the class it declares. The surface is therefore never
wider than what the generator checked, and `verify` fails the moment the committed
file and a rebuild differ by one byte.

## 1. Four classes, four predicates

This replaces the earlier rule "every entry needs an executable falsifier", which
would have turned the manifesto into a registry of tests. Different kinds of
standing things carry different kinds of evidence.

| class | what it is | what the generator requires | credit emitted |
|---|---|---|---|
| `operational` | a claim about the world that a check can refute | `check` argv whose script is byte-pinned **and exits 0 now**; a nonempty `falsifier` | `validation` |
| `normative` | a decision someone with authority took | in-repo `authority` artifact byte-pinned; `scope`; `revocation` condition; `adopted` date; `by` | `authority` |
| `intent` | an open edge: wanted, promised, or flagged, not yet validated | `origin`; a `review_trigger` **or** an `expiry` that has not passed; **no** `check` field is admitted | `none` |
| `retired` | something removed from the default surface | a `mode` from CONTROLLED-FORGETTING-0.1 §2; `retired_on`; a nonempty `loss` record; a `successor` id that resolves to a non-retired row, or `null`; a `record` pointer | `retired` |

Two consequences worth stating:

- An operational row whose check goes red is **refused**, not demoted to intent. The
  author re-classifies by hand, and the diff shows it.
- An intent whose expiry has passed is **refused** by the clock, not by the text.
  Forgetting is a change of admission (CONTROLLED-FORGETTING-0.1 §1.3), and the
  admission here expires.

## 2. Bindings

Every `path` is in-repo, must exist, must not be a symlink, and is pinned by SHA-256.
Every `locator` is outside the repo and is recorded as `locator-only`: an address,
not evidence. The census in the trajectory audit and the SEV retirement envelope
enter this way. Nothing external earns credit by being named.

`REDACTED` rows may not pin bytes at all: a digest of a secret is an oracle
(CONTROLLED-FORGETTING-0.1 §2).

## 3. The specimen (`as_of` 2026-09-03)

| id | class | one line |
|---|---|---|
| `badge-addresses-recomputed` | operational | the Python route reproduces the badge page's pinned addresses; check runs green |
| `mission-accepted-2026-08-30` | normative | MISSION accepted by the operator, class-(c) act; authority `MISSION.settled.md` pinned |
| `mission-receipt-resettle` | intent | `MISSION.receipt.json` is **stale** against current README (found while building this surface) |
| `sev-loss-manifest-needs-home` | intent | the `loss_manifest` invariant has no live home after SEV's archival (census 09) |
| `multi-model-raid-promised` | intent | promised in MISSION Obligations; expires 2026-10-31 unless run or re-triaged |
| `sev-projection-repo` | retired | ARCHIVED 2026-09-02; loss named; successor is the intent above |

One specimen, six rows, every class present. Importing the rest of census 09 is a
follow-up and enters as `intent` by default, because the census itself says each
row must be re-verified before it drives an act.

## 4. What falsifies this draft

- A row classified wider than its evidence that `build` accepts. The controls burn
  28 such rows; a 29th that passes is a defect in the generator, not in the row.
- A hand edit to `ACTIVE-SURFACE.json` that `verify` does not catch.
- A class whose predicate cannot be stated as a refusal code. Then the class is
  wrong, not the generator.

## 5. Not in scope

Cross-repository verification (the surface does not run warrant's or sigma-glyph's
checks), CI wiring, changes to `AGENTS.md`, and any authority over other
repositories. The surface says what *this* repository treats as working today and
under which kind of evidence. It grants nothing to anyone else.
