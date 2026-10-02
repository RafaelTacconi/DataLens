# memory.md — DataLens-v1 build log
Status: IN PROGRESS | BLOCKED | COMPLETE
Current checkpoint: <e.g. C3>
Last updated: <ISO timestamp>

## Environment
*Recorded ONCE, at A2, and read by every session afterwards. Shell and path
conventions were got wrong on the first attempt in four or more separate
instances across two real builds, re-discovered every time, and never written
down.*

- **Shell:** <PowerShell 5.1 / pwsh 7 / bash — and which one the agent should
  assume when it writes a command>
- **Path separator:** <`\` on Windows; note any place forward slashes are
  required anyway>
- **Activate the venv:** <the exact line, e.g. `.venv\Scripts\activate`>
- **Anything that bit last time:** <one line per gotcha>

## Handoff state
Current phase: <e.g. C — Build>
Phase done condition: <copied verbatim from the PHASE MAP in project-core's SKILL.md>
Phase status: NOT READY | READY | PASSED TO: <next phase>

## Blockers (current)
- <what is blocking; what human input is needed>

## Resume instructions
FIRST: activate the venv — Windows: .venv\Scripts\activate
Next action: <exact next checkpoint and its first step>

*Everything above this line is CURRENT and gets overwritten. Everything below
is a RECORD and is only ever appended to.*

## Checkpoint plan
*Minted at B3 from contract.md Part 6 (gate G1) for a build — and re-minted
per change at M-spec. Same table, same columns, both occasions.*

**Tag column.** Every row carries `STRICT`, `DEFAULT` or `OPTIONAL`. `STRICT`
stops for a human; `DEFAULT` does not; `OPTIONAL` is not done unless the
builder turns it on. Nearly every minted row is `DEFAULT`.

**Additions after sign-off** get `From contract` = `ADDITION` and a SUFFIX id
(C12a, never a second C13), and a row in the contract's
`## Additions after sign-off` table.
| CP | Tag | From contract | What is built | Accept test (observable) | Approved |
|----|-----|---------------|---------------|--------------------------|----------|

## Checkpoint log
| CP | Status | Date | Receipt | Evidence / notes |
|----|--------|------|---------|------------------|

**Status values.** `PASS` claims something a command proved, and cites the
receipt. `DONE` is ONLY for set-up and contract-writing rows (A0–A2,
B0–B3): they make no claim a receipt could back, because the contract they
would be checked against does not exist yet. The first receipt-backed row is
B4, the seal. A build, release or change row is never `DONE` — the release
gate refuses it. `SKIPPED` and `DECLINED` also get a line under
`### Skipped or declined checkpoints`.

**The Receipt column.** A row that claims PASS cites the `.evidence/` file the
command wrote — for example `20261001T101500Z_check.json`. **Cite the
receipt; do not narrate instead.** Commit every receipt you cite, with its
checkpoint: `git add -f .evidence/<file>` (the folder is git-ignored so that
only cited receipts are committed). A commit hash is not a receipt: it proves
code changed, not that a command ran.

**A receipt proves a command ran and what it returned. It does not prove a
person did something.** A row like "the builder checked the screen" writes
`UNVERIFIABLE: <why>` in the Receipt column. **Never invent a receipt.**

`verify_build.py --release` fails if a PASS row cites nothing, cites a receipt
that is missing or uncommitted, or cites one made against a different
`contract.md` — which is how a contract edited after the evidence gets caught.
**The receipt must also show what the row claims:** B4 → `CONTRACT` PASS;
C0 → `CONTRACT` and `ARTIFACT WRITTEN` PASS; every other C row → `CONTRACT`
and `TESTS` PASS; R1 → `TESTS` and `ARTIFACT` PASS; R2 → `README` PASS; R3,
M0, M4 → a GO run. Rows above the newest released R3/M4 row stay valid when
a later change re-signs the contract.

## Checkpoint cost
*One line per phase, written at the phase's Done condition. Thirty seconds;
it is the only measurement this framework has of which steps earn their
place.*

| Phase | Checkpoints run | Back-and-forth exchanges | Which felt unnecessary |
|-------|-----------------|--------------------------|------------------------|
|       |                 |                          |                        |

**Be blunt in the last column.** "B1 — three turns re-asking what the design
document already said" is worth more than "fine".

## Decisions made (with rationale)
- **A1 — Framework version: `project-core v1.1`.** The phase files and
  `scripts/verify_build.py` in this repo came from it. Update this line only
  when the project deliberately takes an upgrade.
- <date> — <decision> — <why> — **BUILDER** or **AGENT**

*The last word says who decided: the BUILDER, or the AGENT with the builder
not objecting. The second is the real risk with one builder and no second
reader.*

*A later decision that overturns an earlier one does NOT delete it — append
`— SUPERSEDED <date>, see <the new decision>`. The reasoning that was true
then is why the code looks the way it does.*

*Do not edit framework files (phase files, SKILL.md, house rules) from inside
a project session. If a phase file is wrong, record it under Open questions
and under Template feedback — the framework changes in a wave, not mid-build.*

## Rejected approaches (do not re-propose without new information)
*What was CONSIDERED and not done, and why. One line each. The next session
will reach the same reasonable-looking idea; a rejection with its reason ends
that in one read.*

- <date> — <what was considered> — REJECTED: <the specific reason>

## Open questions (not blocking)
*A question worth an answer that is NOT stopping work. An unrecorded open
question gets silently assumed instead. A `not sure yet` in the contract
needs a row here naming the field or decision.*

- <date> — <the question> — <what it would change if answered> — ASKED / UNASKED

### Skipped or declined checkpoints
*Any checkpoint skipped, declined or deferred gets ONE line, with a reason.
"Not needed because X" is a reason. "Declined" is not.*

- <date> — <checkpoint id> — SKIPPED / DECLINED — <the reason, one line>

### Template feedback (did this project deviate from the framework?)
*Asked at the end of Phase R and of every change cycle: "this project did X
differently from the template — should the template change?" Record the
answer either way.*

- <date> — <what this project did differently> — TEMPLATE SHOULD CHANGE /
  PROJECT-SPECIFIC — <why>

## Deviations from plan
- <what differs and why; empty is the goal>
