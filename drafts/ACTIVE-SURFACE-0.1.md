# ACTIVE-SURFACE-0.1 — what this repository treats as working, by kind of evidence

**Status:** draft, non-normative. The surface is `surface/rows.json`. The check is
`tools/active_surface.py`, about sixty lines. `AGENTS.md` is untouched.

Not every standing thing needs an executable falsifier; that rule would make the
manifesto a registry of tests. Four kinds, one predicate each. The check refuses a
row whose fields do not match its kind, so a row cannot claim more than it carries.

| kind | predicate the check applies | credit |
|---|---|---|
| `operational` | the named check exits 0 now; a falsifier is written | validation |
| `normative` | the authority file exists here; scope and revocation are written | authority |
| `intent` | a review trigger, or an expiry that has not passed; a `check` field is not admitted | none |
| `retired` | a mode from CONTROLLED-FORGETTING §2; a loss record; a successor that resolves or `null` | none |

A red operational check is refused, not demoted; the author re-classifies by hand.
An expired intent is refused by the clock, so forgetting has a date. External
things (census rows, the SEV envelope) are named in the statement and are not
verified: a name is an address, not evidence.

Specimen as of 2026-09-03: six rows, every kind present. Found while writing it:
`MISSION.receipt.json` is stale against the current README; that is an intent row,
not an operational one.

What falsifies this draft: a row the check accepts whose kind is wider than its
fields; a kind whose predicate cannot be stated in one line.
