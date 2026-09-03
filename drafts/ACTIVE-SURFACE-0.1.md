# ACTIVE-SURFACE-0.1 — a small declared surface with typed evidence

**Status:** draft, non-normative. The surface is `surface/rows.json`; the falling
consumer is `tools/active_surface.py`. There is no generated duplicate and
`AGENTS.md` is untouched.

The file answers one bounded question: **what does this repository currently
treat as operational, normative, intended, or retired, and what predicate does
each classification carry?** It does not prove the prose in `statement` true.

| class | predicate checked | emitted credit |
|---|---|---|
| `operational` | closed argv; exact in-repo entrypoint digest; exit 0 now; falsifier named | execution of that check only |
| `normative` | exact authority bytes; scope, revocation, date and actor declaration | repository-declared authority only |
| `intent` | origin plus a trigger or an expiry naming an instant; closed shape excludes a check | none |
| `retired` | CONTROLLED-FORGETTING mode, date, loss, and a successor that resolves to a live non-retired row or is explicitly `null` | none |

Every in-repo source is SHA-256 pinned. External locators are address-only and
cannot earn credit. The class vocabulary is closed, but occupancy is not
compulsory: an unknown class is refused, and a class with no rows is fine. The
earlier rule requiring one row of each class made the vector keep a class alive
for the checker's sake — when the open edge behind the only `intent` row closed,
the row could not be deleted without tripping it, so a false statement stayed on
the surface to satisfy a shape rule. The profile is non-empty, rejects duplicate
JSON keys and IDs, and refuses source drift, authority drift, unbounded intent,
dangling successor, an empty loss on a retired row of any mode, a red
operational check, or a `REDACTED` row that keeps an in-repo byte pin (a digest
of secret bytes may itself be an oracle).

**Time is not authority here.** Three axes are kept apart. *Causal order* is
git — commit and tree digests, parent ancestry, pinned authority bytes — and
needs no clock to say which act preceded which. *Human dates* are labels: their
shape is checked, and their ordering against `now` grants nothing. This checker
used to refuse `AS_OF_IN_FUTURE`, `ADOPTED_IN_FUTURE` and `RETIRED_IN_FUTURE`,
and that cost a real refusal of a legitimate act — an adoption taken at
`00:25+03:00` was "in the future" against `now(UTC)`. Those gates read a field
no predicate downstream depends on, so they are gone.

Two kinds of date, and the difference is whether anything executes it. A human
**label** — `as_of`, `adopted`, `retired_on` — may be `YYYY-MM-DD` or RFC 3339
with an explicit offset; a datetime with no offset is refused, because that
implicit timezone is exactly what bit. An **executable instant** — `expiry`, the
only date this repository compares against a clock — must be RFC 3339 with an
explicit offset, and a bare day is refused. Reading `2026-12-31` as `23:59:59Z`
looked harmless and was the same defect one level down: UTC stops being the
judge and returns as the deadline's unstated jurisdiction. Normalising two
defined instants to UTC to compare them is fine; inventing a zone for a zoneless
date is not. *External marking* (an OpenTimestamps-style proof that exact
bytes existed before block N) is deliberately **not** implemented, and the
condition for revisiting it is stated so nobody has to re-derive it: there must
be a frozen deposit candidate **and** a specific external assertion of the form
*these bytes existed no later than T*. A Zenodo deposit is a moment to ask the
question again, not a trigger — Zenodo is itself an external mark with a
custodian, so if the deposit only buys publication and a DOI, no temporal
machinery is needed at all. What OTS would add is existence that does not depend
on trusting one custodian, and it would attest existence-by-block regardless:
never the instant of a decision, its author, or its legitimacy. If the condition
is ever met, the shape is one frozen manifest, one verified root, one stamp, and
a separately recorded `PENDING -> UPGRADED/VERIFIED` — not per-commit stamping.

The single place a clock still bites has its own room: `--due` is a projection,
not a validity check. An intent past its instant is a **debt**, not a malformed
row, so structural validation admits it and `--due` reports it and exits
non-zero. Both halves are burned by controls — moving expiry out of validation
would otherwise turn a deadline into something that can no longer fail.

The output is a per-row vector. `CHECKED` means only that row's typed predicate
held; it never means the statement, the file, or Manifesto as a whole is true.

Current specimen: five rows — two operational, one normative, none intent, two
retired. The receipt-freshness row is the one that moved: while
`MISSION.receipt.json` was stale against `README.md` it could only be an
`intent`, because there was nothing green to run. Re-settling it on the current
bytes bought exactly one thing — a check that goes red, rather than quietly
stale, the next time `README.md` moves under it. The `intent` class is now empty
and that is a result, not a gap: the open edge it held was closed by
`tools/retirement_record_check.py`, so the row was deleted rather than reworded.

Run:

```sh
python3 tools/active_surface.py            # structural, clock-free
python3 tools/active_surface.py --selftest
python3 tools/active_surface.py --due      # clock-dependent projection, no authority
```

Falsifiers: a changed pinned operand that stays checked; an empty vector that
passes; a red command reported as operational; an overdue intent that `--due`
does not report; a wall clock deciding structural validity again; or any
consumer interpreting the vector as document-level semantic credit.
