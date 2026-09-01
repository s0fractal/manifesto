# Fixture: duplicate capsule key is ambiguous identity (phase 2)

The capsule repeats the `verifier` key. `json.loads` would silently keep the last —
letting two different source texts map to one canonical body. The strict parser
rejects duplicate keys so identity stays unambiguous.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:7a678c25452c23f91f6193b68e78cca09faea917b0b2b433cd36ea0878a95c90",
  "verifier": "settle-gate://sha256:0000000000000000000000000000000000000000000000000000000000000000"
}
```

Expected: execution=UNVERIFIED; execution_facts include CAPSULE_INVALID, with a note
about the duplicate object key.
