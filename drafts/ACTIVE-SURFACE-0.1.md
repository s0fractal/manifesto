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
cannot earn credit. The profile is non-empty, contains all four classes, rejects
duplicate JSON keys and IDs, and refuses source drift, authority drift, expired
intent, dangling successor, a red operational check, or a `REDACTED` row that
keeps an in-repo byte pin (a digest of secret bytes may itself be an oracle).

The output is a per-row vector. `CHECKED` means only that row's typed predicate
held; it never means the statement, the file, or Manifesto as a whole is true.

Current specimen: six rows. Its useful live finding is that
`MISSION.receipt.json` is stale against current `README.md`; the row is therefore
an `intent`, not an operational or normative upgrade.

Run:

```sh
python3 tools/active_surface.py
python3 tools/active_surface.py --selftest
```

Falsifiers: a changed pinned operand that stays checked; an empty vector that
passes; a red command reported as operational; an intent that survives its
expiry; or any consumer interpreting the vector as document-level semantic
credit.
