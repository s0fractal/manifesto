# CHORD-CAPSULE-0.1 — one format for statements-from-what-was-seen, spoken in two channels

**Status:** `WITHDRAWN` by the owner on 2026-09-03. Preserved as a historical design probe; it is
not a candidate schema, a rule anyone enforces, or a change to the embedded-claims pipeline.

**Disposition.** The proposal imported `speaker`, `hears`, channel identity, and related chord
structure from Trinity before establishing a Manifesto-native need, an explicit cross-protocol
mapping, or a loss report. It also starts from the transitional `manifesto.capsule.v1` /
`claim_ref` surface; the current canonical route is capsule-only `manifesto.capsule.v2`, where the
claim lives inside the capsule and association is containment. Adopting this draft would therefore
reopen retired association machinery and enlarge the semantic surface without a demonstrated
consumer or falsifier. No implementation, schema, generated context, or verification credit may
derive from this document.

The narrow question that survives is whether a statement summarized in chat can be checked against
the artifact written to the repository. That remains an unadmitted future intent and does not
inherit the chord vocabulary or this proposed schema.

The body below is retained unchanged as the proposal that was evaluated. It was written by Claude
Fable 5.1 on 2026-09-02 at the owner's request for critique by the owner and Codex.

**Origin.** Three surfaces already carry most of this and do not know about each other:
`manifesto.capsule.v1` (embedded-claims PoC: a claim pins its verifier and the evaluation it bets
on), trinity chords (a voice's claim with `hears`, `falsifiers`, a speaker), and the audit's
`OBSERVED` label (a statement is backed by a repository, a revision, a path and a digest). The owner's
question: can these be one format, so that a review, an opinion and an objection are the same object
distinguished by a field rather than by a folder — and so that what a model *says in chat* can be
checked against what it *wrote to the file*.

**Principle in one sentence:**

> A statement is a capsule: what was seen (by digest), what is claimed about it (by relation to a
> target), what would check it (by verifier digest), what would kill it (falsifiers), whose voice it
> is (declared and observed), and which earlier capsules it heard. The same capsule is emitted in
> every channel it is spoken in; a second channel may abridge it only by pointing at the full one.

---

## 0. What exists, exactly

| Surface | Fields it already has | What it lacks for this purpose |
|---|---|---|
| `manifesto.capsule.v1` (`drafts/embedded-claims-poc/schema.py`, closed) | `claim_ref`, `verifier` (`glyph\|settle-gate\|effect-sandbox://sha256:…`), `evaluation_id`, `dep{path,sha256}`, `binding{relation ∈ supports\|refutes\|defines\|instantiates\|measures, target, status}` | who speaks; what was seen beyond one `dep` in one repo; predecessors; falsifiers; a second channel |
| trinity chord frontmatter (`src/x1300_…myc.md`) | `speaker`, `hears`, `claim.summary`, `falsifiers` (prose), `mode` (RIFF/AYE/…), `energy`, `tension`, `confidence`, `receipt: file` | a pinned verifier; an evaluation id; anything executable (`suggested_commands: []`) |
| audit labels (`trajectory-audit…/*`) | `OBSERVED` = path + revision; `DERIVED` = named operands + derivation | a machine form; any check |
| corpus schema (`papers/every-check-spawns-more/CORPUS-SCHEMA-0.1.md`) | `verifier_declared_identity` vs `verifier_observed_identity`; L1 transcript as immutable blob, L2–L4 regenerable | applied to papers only, not to everyday statements |

`binding.relation` already answers "review, opinion or objection?": an objection is `refutes` with
a verifier; agreement is `supports`; a measurement is `measures`. No folders. The rest of this
draft adds exactly four things and one rule.

## 1. The extension (a superset of `manifesto.capsule.v1`)

```json capsule
{
  "schema": "manifesto.chord-capsule.v0",
  "claim_ref": "pypi-067-equals-tag-module",
  "binding": {"relation": "measures", "target": "impl/sigma_glyph_v05.py is the published Book I v0.5 module"},
  "observed": [
    {"repo": "s0fractal/sigma-glyph", "revision": "16a1355142d0234ba0dcc519d674bb26b42a1d82", "path": "impl/sigma_glyph.py",
     "sha256": "80299d6869e7c93ece3455db32c0a6a1346a8b7162e6ef0954a4bd425497bab5"},
    {"repo": "s0fractal/warrant", "revision": "ae77cf2", "path": "impl/sigma_glyph_v05.py",
     "sha256": "80299d6869e7c93ece3455db32c0a6a1346a8b7162e6ef0954a4bd425497bab5"},
    {"repo": "pypi:sigma-glyph==0.6.7", "revision": "sigma_glyph-0.6.7-py3-none-any.whl", "path": "sigma_glyph.py",
     "sha256": "80299d6869e7c93ece3455db32c0a6a1346a8b7162e6ef0954a4bd425497bab5"}
  ],
  "verifier": "UNPINNED-DRAFT (observe://sha256:<digest of the byte-equality script>; scheme not yet in schema.py)",
  "evaluation_id": "UNPINNED-DRAFT",
  "falsifiers": [
    {"text": "any of the three digests differs at the named revision", "check": "re-hash the three paths at the pinned revisions"},
    {"text": "the PyPI wheel is yanked or re-uploaded with a different module", "check": "wheel sha256 c3b7bc32… no longer resolves on PyPI", "kind": "external"}
  ],
  "hears": ["wrt-007-rev1-§2", "audit-07-§1.2"],
  "speaker": {"declared": "claude-fable-5-1", "observed": null},
  "channel": "file"
}
```

That is a real statement from 2026-09-02 (WRT-007 §2; warrant PR #49). Two fields are honestly
`UNPINNED-DRAFT`, following the PoC's own convention (§7.2 of the architecture draft): the verifier
for "these bytes are equal" does not exist as a pinned artifact yet, and inventing a digest for it
would be the exact move the format exists to forbid.

### 1.1 Field by field — reason, and what removes it

| Field | From | Why it is here | Remove it if… |
|---|---|---|---|
| `schema`, `claim_ref`, `binding`, `verifier`, `evaluation_id`, `dep` | capsule.v1 | unchanged; `dep` stays for backward compatibility of existing fixtures | — |
| **`observed[]`** `{repo, revision, path, sha256}` | audit `OBSERVED` | a statement about something seen names the thing by digest; `dep` is one path in one repo, `observed` is N paths across repos and registries (`pypi:`, `git:`, a wheel filename as revision) | the critique shows `dep[]` (a list) covers it — then `observed` is a rename, not a field |
| **`falsifiers[]`** `{text, check?, kind?}` | chord | a claim without a stated killer is an opinion; `check` makes the killer runnable; `kind: external` marks the ones only the world can run (a yank, a collision) | a claim with a pinned `verifier` and a `refutes` counter-capsule already *is* a falsifier — then `falsifiers` is redundant with the graph and should go |
| **`hears[]`** (capsule ids) | chord `hears` / warrant `prior` | the graph edge; what this statement was built on; the thing a model may skip re-reading once the heard capsule replays | it duplicates `binding.target` in practice |
| **`speaker`** `{declared, observed}` | corpus schema | "who says so" split into what the text claims and what the transcript metadata shows; the Fable/Opus mislabel (F-C2-1) is exactly this split; `observed` is filled only by the double-ledger tool, never by the author | the owner decides voice identity is not worth a field outside papers |
| **`channel`** `file \| chat`, **`abridged_of`** | new | the double ledger (§2); a chat capsule is either byte-identical to the file capsule or an abridgement that names it | the double ledger is not adopted — then both fields go |

### 1.2 Deliberately NOT taken from the chord

`energy`, `tension`, `confidence`, `mode`, `receipt: file`, `suggested_commands`,
`expected_after_running`. `mode` is `binding.relation`; `confidence` without a verifier is prose and
with one is redundant; `energy`/`tension` are the voice's affect and belong to LORE, not to a
checkable statement; `receipt: file` says the file is its own evidence, which is the failure the
format exists to end. If the critique wants any of them back, the burden is a falsifier for it.

## 2. The double ledger — one capsule, two channels

**Rule (proposed for `AGENTS.md`, three lines):** a statement a model makes to the owner in chat
that it also records in a file MUST be the same capsule in both — byte-identical after canonical
JSON — or a chat capsule carrying `abridged_of: <evaluation_id or claim digest>` that resolves to
the file capsule. Simplifying for the reader is legal; substituting a concept is not; the recipe is
always complete in the file.

**Mechanism (`tools/double_ledger.py`, not written yet):**

```text
L1  the session transcript (~/.claude/projects/<proj>/<session>.jsonl) — an immutable blob,
    NEVER committed (corpus rule: raw L1 stays quarantined)
L2  extract ONLY fenced ```json capsule blocks from `assistant` text parts; record for each:
    session_id, message uuid, timestamp, message.model  →  speaker.observed
    (nothing else is read from the transcript: no prose, no thinking, no tool output)
L3  canonicalize (sorted keys, no whitespace, UTF-8), digest; pair with file capsules by
    claim_ref (or evaluation_id when present)
verdict per pair:
    MATCH                 chat digest == file digest
    ABRIDGED_OK           chat capsule has abridged_of → resolves to the file capsule; the file capsule
                          is the superset (every chat field equal to the file's)
    SUBSTITUTED           same claim_ref, different digest, no abridged_of  ← the defect this exists for
    ABRIDGEMENT_DANGLING  abridged_of does not resolve
    ORPHAN_CHAT           spoken, never written (allowed for pure opinion; flagged for measures/refutes)
    SPEAKER_MISMATCH      speaker.declared ≠ message.model (F-C2-1 class; a finding, not a failure)
```

What this establishes: that the model told the owner the same thing it wrote down, at the level of
the capsule. What it does not establish: that either is true (that is the verifier's job), or that
the prose around the capsule agrees with it (out of scope; prose is not checked).

Privacy boundary, stated because it is the one place this could go wrong: the extractor reads
capsule fences only; it emits ids and digests, never text; L1 never leaves the machine.

## 3. What this replaces, and what it does not

- Replaces: the need for `reviews/` vs `talks/` vs `quotes/` folders for *statements about
  artifacts* — a review is capsules with `refutes`/`supports` and `observed`; the folder can stay
  as a place, but the type lives in the capsule.
- Replaces: prose-only falsifiers in chords with falsifiers that carry a `check`.
- Does not replace: warrant records (a chord-capsule is not signed and settles nothing; when a
  statement must carry authority it becomes a warrant whose `subject` is the capsule digest), the
  settle gate (which is one verifier scheme among the capsule's), or `RESULT.md`/`RETIREMENT.md`
  as human documents.
- Does not decide: adoption, credit, or truth. A capsule with `verifier: UNPINNED-DRAFT` is a typed
  speculation (Thesis 7), legal as long as it says so.

## 4. Relation to the trust-node idea

A capsule whose verifier replays is a node a later model may *act on without re-reading its
`hears`*: the check is bounded and mechanical, so re-verification costs milliseconds and spawns no
prose (paper A, C5: the terminal sub-act). A capsule whose verifier is `UNPINNED-DRAFT` is a leaf
opinion: it may be heard, not acted on. That single distinction is what keeps the graph out of the
meta-verification minimum (ô ≈ 2–3 on prose). "Compressing songs" later is retirement of capsules
whose falsifiers have run and not fired: they keep their `evaluation_id` and lose their bytes from
default context (CONTROLLED-FORGETTING I2/I3).

## 5. Falsifiers of the design

1. A real week of statements produces capsules whose `falsifiers` are all `kind: external` or
   prose → the field is decoration; remove it and rely on `refutes` counter-capsules.
2. The double ledger over one real session reports only `MATCH`/`ORPHAN_CHAT` and never
   `SUBSTITUTED` → either models do not substitute, or the capsule is too coarse to catch it; either
   way the rule earns nothing and should not be added to `AGENTS.md`.
3. Authors stop writing `observed` because it costs more than the statement is worth → the field
   is an obligation nobody pays; keep `dep` only.
4. Two capsules with identical `observed` and `verifier` and opposite `relation` cannot be told
   apart by any check → the format captures form, not disagreement; the chord's prose was doing
   real work and this draft should not replace it.
5. `speaker.observed` never differs from `speaker.declared` outside the one known corpus → drop
   the split from everyday capsules, keep it in papers.

## 6. Open decisions (for the critique, not for the author)

1. `observed[]` vs `dep[]`: one list or two? (My bet: one, named `observed`, with `dep` kept as an
   alias for existing fixtures.)
2. A verifier scheme for byte/digest observations (`observe://`) — new scheme in `schema.py`, or is
   `settle-gate://` with a `sha256:` claim class already that?
3. Whether a chat capsule needs `channel: chat` at all, or whether "found in a transcript" is the
   channel.
4. Capsule identity for `hears`: `evaluation_id` (only exists after a run) or a digest of the
   canonical capsule body (exists at authoring)?
5. Whether the first specimen should be this file's own capsule (§1) verified by a script that does
   not exist, or a smaller one whose verifier is already pinned (`settle-gate://` arithmetic).

## 7. Minimal rollout

- Phase 0 — this document. No schema change, no tool.
- Phase 1 — `tools/double_ledger.py` over **one** session (this one), read-only over L1, emitting
  the verdict table above for the capsule in §1 (which was also spoken in chat when this draft
  was delivered). Expected: `MATCH` or `ABRIDGED_OK`; if `SUBSTITUTED`, the author is the first
  finding.
- Phase 2 — the three-line rule in `AGENTS.md`, only if Phase 1 caught something or the owner
  wants the discipline regardless.
- Not planned: migrating trinity chords, a chord registry, CI.

## 8. Shortest form

```text
capsule   = observed (by digest) + relation to target + verifier (by digest) + falsifiers
          + hears + speaker{declared, observed}
one voice = same capsule in every channel; abridge only by pointer
no folders: relation is the type
no verifier: typed speculation, may be heard, not acted on
```
