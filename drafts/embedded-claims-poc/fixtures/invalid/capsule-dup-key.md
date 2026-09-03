# Fixture: duplicate capsule key is ambiguous identity (phase 2)

The capsule repeats the `verifier` key. `json.loads` would silently keep the last —
letting two different source texts map to one canonical body. The strict parser
rejects duplicate keys so identity stays unambiguous.

⟦arith: 74+1=75⟧

```json capsule
{
  "verifier": "glyph://sha256:52800283f80b20eb10db18503676301b8d4f104436ee1b00b9f0a309bb90045c",
  "verifier": "settle-gate://sha256:0000000000000000000000000000000000000000000000000000000000000000"
}
```

Expected: execution=UNVERIFIED; execution_facts include CAPSULE_INVALID, with a note
about the duplicate object key.
