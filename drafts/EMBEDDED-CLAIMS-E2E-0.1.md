# EMBEDDED-CLAIMS-E2E-0.1 — the first real live capsule

This document is the first end-to-end specimen of the embedded-claims pipeline running on
real repository content. Everything above and below the region is ordinary prose and
carries no machine credit. Inside the region is one explicit capsule with a **world
claim**: it counts the top-level thesis headings in the root `README.md` and pins the
exact bytes it was settled against.

Run it through the whole chain with the orchestration CLI:

```sh
cd drafts/embedded-claims-poc
../../.venv/bin/python claims.py run ../EMBEDDED-CLAIMS-E2E-0.1.md
# or, as a CI policy projection:
../../.venv/bin/python claims.py run --strict ../EMBEDDED-CLAIMS-E2E-0.1.md
```

<!-- manifesto-claims:begin profile=manifesto.embedded-claims.v0 -->

```json capsule
{
  "schema_version": "manifesto.capsule.v2",
  "claim": {
    "local_id": "README-THESIS-HEADING-COUNT",
    "class": "count",
    "payload": "/^## Теза [0-9]+:/ in README.md = 7"
  },
  "verifier": "settle-gate://sha256:52800283f80b20eb10db18503676301b8d4f104436ee1b00b9f0a309bb90045c",
  "dep": {
    "path": "README.md",
    "sha256": "0c9e3eddf93a12acfaa15a6b9b91a161e3d7275b3a3110202bc0e0c218144ae2"
  }
}
```

<!-- manifesto-claims:end -->

## What this REPLAYED does and does NOT mean

A `REPLAYED` here means exactly one thing: **against the pinned snapshot of `README.md`,
the regex `^## Теза [0-9]+:` matches seven lines.** It does NOT mean the seven theses are
true, independent, complete, or good; it does not "green" the theses or the README. There
is no `binding` in this capsule, so the binding axis is `UNTIED` — the count is not even
claimed to *measure* anything about the theses beyond the literal heading count. The
document as a whole gets no verdict; the runner emits a one-record vector.

## Honest boundaries carried over

- The `verifier` id is a code closure bound to `sigma-glyph==0.6.7` and the current
  settlement engine; a change to either rotates it and this capsule goes `UNVERIFIED`
  until re-pinned. That is the closure discipline, not a flake.
- The `dep` digest pins a snapshot; if `README.md` changes, this result becomes `STALE`
  (and the runner reports the observed digest), never a silent green.
- This is a `REPORT`, not a receipt. Content addressing catches an incoherent mutation of
  the compiled bundle, but a fully recomputed, schema-valid bundle is a new bundle;
  distinguishing it from this historical original needs an external commitment /
  signature / receipt — a separate phase this pipeline does not claim.

The point is not that a number is green. The point is that this one sentence — "README
has seven thesis headings under this regex, against this snapshot" — is re-executable by
anyone, from the serialized bundle, without trusting this document.
