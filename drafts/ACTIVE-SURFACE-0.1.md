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
| `intent` | origin plus trigger or unexpired date; closed shape excludes a check | none |
| `retired` | CONTROLLED-FORGETTING mode, date, loss, and a successor that resolves to a live non-retired row or is explicitly `null` | none |

Every in-repo source is SHA-256 pinned. External locators are address-only and
cannot earn credit. The class vocabulary is closed, but occupancy is not
compulsory: an unknown class is refused, and a class with no rows is fine. The
earlier rule requiring one row of each class made the vector keep a class alive
for the checker's sake — when the open edge behind the only `intent` row closed,
the row could not be deleted without tripping it, so a false statement stayed on
the surface to satisfy a shape rule. The profile is non-empty, rejects duplicate
JSON keys and IDs, and refuses source drift, authority drift, unbounded or
expired intent, dangling successor, an empty loss on a retired row of any mode,
a red operational check, or a `REDACTED` row that keeps an in-repo byte pin (a
digest of secret bytes may itself be an oracle).

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
python3 tools/active_surface.py
python3 tools/active_surface.py --selftest
```

Falsifiers: a changed pinned operand that stays checked; an empty vector that
passes; a red command reported as operational; an intent that survives its
expiry; or any consumer interpreting the vector as document-level semantic
credit.
