# Adversarial 03 — nested fences (T4)

A capsule shown INSIDE a wider fence, as documentation of how to write one. The inner
closing fence must not be mistaken for the capsule's terminator, and the whole thing
is an illustration, not a live capsule.

````markdown
Here is how you attach a capsule:

```json capsule
{"verifier": "glyph://sha256:deadbeef..."}
```
````

Expected: the non-greedy `​```json capsule ... ``` ` regex would capture a TRUNCATED
body and treat this as a live capsule. A conformant parser tracks fence nesting/info
strings via CommonMark block structure: this capsule is inside a fenced code block, so
it is inert. No live capsule is found in this document.
