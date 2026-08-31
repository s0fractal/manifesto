# Fixture: world claim without a dependency pin (P0, rev 3)

The count is correct and the verifier is correctly pinned — but the author pinned
NO dependency. A world-dependent claim that does not commit to the exact bytes it
read cannot earn replay credit: it would go green against any future README.
Fail-closed.

⟦count: /^## Теза [0-9]+:/ in README.md = 7⟧

```json capsule
{
  "verifier": "settle-gate://sha256:b4f33ca1ba18b005de4eeba34a550cd65e4481e54a3ce5885831cd6d239636cd"
}
```

Expected: execution=UNVERIFIED (facts include DEPENDENCY_MISSING).
