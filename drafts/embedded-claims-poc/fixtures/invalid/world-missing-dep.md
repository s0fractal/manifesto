# Fixture: world claim without a dependency pin (P0, rev 3)

The count is correct and the verifier is correctly pinned — but the author pinned
NO dependency. A world-dependent claim that does not commit to the exact bytes it
read cannot earn replay credit: it would go green against any future README.
Fail-closed.

⟦count: /^## Теза [0-9]+:/ in README.md = 7⟧

```json capsule
{
  "verifier": "settle-gate://sha256:52800283f80b20eb10db18503676301b8d4f104436ee1b00b9f0a309bb90045c"
}
```

Expected: execution=UNVERIFIED (facts include DEPENDENCY_MISSING).
