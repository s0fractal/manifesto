# Fixture: duplicate capsule key is ambiguous identity (phase 2)

The capsule repeats the `verifier` key. `json.loads` would silently keep the last —
letting two different source texts map to one canonical body. The strict parser
rejects duplicate keys so identity stays unambiguous.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:605a1e8a147501ba16e3fe9033bd00a26b6dd8bb0750aab5a798e51b4112d7f7",
  "verifier": "settle-gate://sha256:0000000000000000000000000000000000000000000000000000000000000000"
}
```

Expected: execution=UNVERIFIED; execution_facts include CAPSULE_INVALID, with a note
about the duplicate object key.
