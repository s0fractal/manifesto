# AGENTS.md

Rules for any agent working in this repository. This file is deliberately thin
and stable: rules, commands and links only. It carries no digests, no copied
facts and no generated views — those live in `.warrant/` and are verified on
demand by Warrant 3.

This file is not an act of adoption and grants no authority to anyone. It
records how to read what the repository already declares.

## Canonical owner: `.warrant/` (Warrant 3)

Active surface claims (`claim@1`), distilled research ideas and ontology debts
(`obligation@1`), and controlled-forgetting retirements (`retirement@1`) live
as signed, content-addressed Warrant 3 records in `.warrant/records.jsonl`,
verified under `.warrant/v3.json`.

- **Verify the store:**
  ```sh
  python3 -m warrant verify --root .
  ```
- **Inspect lineages / open obligations / retirements:**
  ```sh
  python3 -m warrant graph --root .
  ```
- **Policy for retirements:** `CONTROLLED-FORGETTING-0.1.md` (§§1–10: modes and
  invariants I1–I10), now represented by `retirement@1` lineages in `.warrant/`.

There is no second registry. Do not re-introduce unsigned JSON surfaces,
ad-hoc receipt scripts or committed generated views (`dist/`, `*.settled.md`).

## Rules

1. **Historical mode is archaeology, not precedent.** Availability in Git
   history (`7ad7d454400ab4cc0693b10055c4ababaa2f3928` or earlier tags) is not
   admission. Quote a retired artifact only with its `retirement@1` mode and
   known loss attached.
2. **No silent readmission door.** A `retirement@1` lineage moves from
   `retired` to `readopted` only by a signed successor accepted by `pr/owner`.
   Restoring bytes from Git grants no authority.
3. **Never claim review authority you do not hold.** Sign only with your own
   bound key in `.warrant/v3.json`. Passing hygiene/store checks is not an
   independent review.
4. **Owner paths stay the owner's.** `.github/`, `.warrant/v3.json` trust/role
   changes, tags, releases and DOI deposits are owner acts (prepared as PRs,
   never self-merged).
5. **No document-level truth verdicts.** Checks verify record signatures,
   schemas, path hygiene and local links — never that prose is true.

## Repository hygiene

After staging changes, run:

```sh
python3 tools/absolute_path_check.py --selftest
python3 tools/absolute_path_check.py
lychee --offline README.md AGENTS.md CONTROLLED-FORGETTING-0.1.md artifacts/ONTOLOGY-FORMALIZATION-0.1.md
```

Keep link-check configuration in `lychee.toml`; do not add `.lycheeignore`.
