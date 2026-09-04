# Sprint 01 Retirement Evaluation

## 1. `embedded-claims-lineage`

- **Subject Identity**: current embedded record sha256 85e30ca3d02ad68c74fbb5918cd74485677f59238a873fa3f2bb8bdb5acb0e6a.
- **Git Operands**: Before `2a6e54d81a493623a32521ead5850e3ff7d8b92f`, After `b2c0a1573be5fcaff8d188befd52abc446c91f6b`.
- **Reason**: Exploratory inline/recipe format no longer defines authoring eligibility; a proposal and build plan was being mistaken for the implemented current route.
- **Known Loss**: The long MYC/Trinity/SPORE design genealogy, rejected syntax alternatives and the chronological review conversation, the complete prose derivation of every threat and identity distinction, the original build phases and open-decision queue.
- **Replacement/Relation**: `replaced-by` 8 operands (`drafts/embedded-claims-poc/README.md`, etc.).
- **Authority Address**: s0fractal (repository owner), operator directive in the working session, as recorded in `drafts/EMBEDDED-CLAIMS-RETIREMENT-0.1.md` under 'Applied transition'.
- **Postcondition**: `tools/embedded_claims_surface_check.py` (executes the relevant operands to ensure retired subjects don't re-enter the tree).
- **Commands**:
  ```sh
  git diff-tree -r --name-only 2a6e54d81a493623a32521ead5850e3ff7d8b92f b2c0a1573be5fcaff8d188befd52abc446c91f6b
  git show b2c0a1573be5fcaff8d188befd52abc446c91f6b
  ```
- **Measured Maintenance Cost**:
  - Measured: The seven listed refinement commits (`b2c0a15`, `ab4c7dd`, `97f7489`, `eb1502c`, `e1f9a4e`, `e3de2b8`, `1128c93`) are a lower-bound sample, not the full refinement.
  - Prose Inference: The bulk of deletions relates to the removal of the superseded/archived subjects, while insertions relate to the tombstone and the 8 replacing operands. The retirement and general consumer were refined across these multiple named commits.

## 2. `multi-model-raid-promised`

- **Subject Identity**: The retired surface row plus the two MISSION locations retyped by the later owner act.
- **Git Operands**:
  - `cfce442^ -> cfce442`: the row becomes `retired/WITHDRAWN` with null successor. (cfce442^ surface/rows.json 1bbecff37c9d45da1385b6519d15f30998e6138c94d551582e8bfbd1157cfb6c; cfce442 surface/rows.json f9a3f82d4bdc65e6e16328a4facb890ca41dee52118c35c4d9d817ebb0fc9727)
  - `0feb0d8^ -> 0feb0d8`: the two MISSION statements are retyped/removed and the authority receipt/pins rotate. (0feb0d8^ MISSION.md ed3fe3c7a81669cd350f30f65a1a9711b31cd2138ff1d34cfa6588dacddd0a39; 0feb0d8 MISSION.md 54031a17395b60d4bdd0b9b0412696d424780192d21ace5bb24cc8b106e1fdb4)
- **Reason**: The multi-model raid is withdrawn without being run.
- **Known Loss**: The manifesto attack surface keeps no adversarial pass over it, so its theses carry no external counterexample search, and 'рейд → перегляд статей' is gone from MISSION.md's goal candidates along with the input it named.
- **Replacement/Relation**: `successor: null`.
- **Authority Address**: operator directive, working session 2026-09-03: broad multi-model attacks refused.
- **Postcondition**: `POSTCONDITION_NOT_BOUND`
- **Commands**:
  ```sh
  git show cfce44226c38a95ea28aae2ac8be7c0784437d05
  git show 0feb0d86b924d0f63fc7a06e7e0d1a222e11f3d8
  ```
- **Measured Maintenance Cost**:
  - Measured: 2 commits / 7 files is the sum of two individual shortstats rather than the range, and is not a contiguous transition cost.
  - Prose Inference: Withdrawing the promise cleanly took multiple file edits to ensure the repository state didn't drift from the stated mission.

## Vector and Decision

VECTOR embedded-claims-lineage BOUND
VECTOR multi-model-raid-promised POSTCONDITION_NOT_BOUND

Stopping Decision: The second specimen provides no new executable falsifier under current consumers. I stop here and refuse to invent authority. I will not add a registry, schema, generic consumer, new RetirementRecord shape, or CI job merely to make the row green.
