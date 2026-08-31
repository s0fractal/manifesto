# Fixture: missing verifier — no replay credit (P0-1)

The arithmetic is true and would recompute, but the author pinned NO verifier at
all. Fail-closed: without an author commitment to a verifier, there is no replay
credit. This is the case the old "unpinned-verifier" fixture failed to cover — it
tested a *wrong* verifier, not a *missing* one.

⟦arith: 74+1=75⟧

Expected: execution=UNVERIFIED (facts include VERIFIER_MISSING).
