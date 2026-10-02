# memory.md — DataLens-v1 build log
Status: IN PROGRESS
Current checkpoint: C21
Last updated: 2026-10-02T20:37:00Z

## Environment
*Recorded ONCE, at A2, and read by every session afterwards. Shell and path
conventions were got wrong on the first attempt in four or more separate
instances across two real builds, re-discovered every time, and never written
down.*

- **Shell:** Windows cmd.exe (the default shell). Commands are written for
  cmd.exe; `&&` chains conditionally.
- **Path separator:** `\` on Windows. Forward slashes work in most Python and
  git contexts.
- **Activate the venv:** `.venv\Scripts\activate`
- **Anything that bit last time:** none yet. LF→CRLF warnings on `git add`
  are expected and harmless (`.gitattributes` keeps the hook's line endings LF).

## Handoff state
Current phase: C — Build
Phase done condition: the artifact test FIRST (C0), then test-first checkpoints C1..Cn
Phase status: PASSED TO: C

## Blockers (current)
- none

## Resume instructions
FIRST: activate the venv — Windows: .venv\Scripts\activate
Next action: C0 — write the artifact test first (tests/test_artifact.py)
against the synthetic fixture with a scripted LLM stand-in, then build the
checkpoints C1..Cn test-first.

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
| C0 | STRICT | Part 8 / rule 6 | The artifact test: builds the primary output from the synthetic fixture with a scripted LLM stand-in and asserts on its content. | `python -m pytest tests/test_artifact.py` — red now, green once the pipeline exists. | |
| C1 | DEFAULT | R1 | Configuration module (`app/config/settings.py`) loading every setting from the environment. | Test: config loads; no absolute path in code. | |
| C2 | DEFAULT | R2 | Metadata store schema (`app/metadata/store.py`, `models.py`) — WAL SQLite with all tables. | Test: every table exists. | |
| C3 | DEFAULT | R3 | Audit append-only (`app/metadata/audit.py`). | Test: UPDATE/DELETE on audit rows fail. | |
| C4 | DEFAULT | R4 | Identity resolution (`app/core/permissions.py`). | Test: resolves the OS user and records the source. | |
| C5 | DEFAULT | R5 | Workspace membership, roles, last-Owner protection (`app/core/permissions.py`). | Test: role matrix and last-Owner protection. | |
| C6 | DEFAULT | R6 | Path policy (`app/db/path_policy.py`). | Test: rejects each bad path. | |
| C7 | DEFAULT | R7 | Guarded read-only connection (`app/db/connection.py`). | Test: read-only; connections not shared. | |
| C8 | DEFAULT | R8 | Authorizer (`app/db/authorizer.py`). | Test: each prohibited action rejected. | |
| C9 | DEFAULT | R9 | SQL validator (`app/sql/validator.py`). | Test: rejects unsafe/mismatched; accepts valid. | |
| C10 | DEFAULT | R10 | Canonical SQL (`app/sql/canonical.py`). | Test: displayed equals executed; hash matches. | |
| C11 | DEFAULT | R11 | Executor (`app/db/executor.py`). | Test: Polars DataFrame; fetch cap enforced. | |
| C12 | DEFAULT | R12 | Audit logging of governance and query actions. | Test: an audited action leaves a row. | |
| C13 | DEFAULT | R13 | Turn state machine (`app/core/state.py`). | Test: a rerun repeats no LLM call or query. | |
| C14 | DEFAULT | R14 | LLM provider interface (`app/llm/provider.py`). | Test: a stand-in provider runs the pipeline. | |
| C15 | DEFAULT | R43 | Typed data contracts (`app/models/contracts.py`). | Test: each model constructs; malformed input rejected. | |
| C16 | DEFAULT | R35 | Egress policy (`app/llm/egress.py`). | Test: the level controls what is sent; default safest. | |
| C17 | DEFAULT | R15 | Schema inspection (`app/db/schema.py`). | Test: fixture tables and columns found. | |
| C18 | DEFAULT | R16 | Catalog, business context and business terms. | Test: store/retrieve; a not-exposed object is hidden and rejected. | |
| C19 | DEFAULT | R17 | Query understanding (`app/llm/structured_output.py`). | Test: a stand-in interpretation parses into the model. | |
| C20 | DEFAULT | R18 | Clarification (`app/core/orchestrator.py`). | Test: an ambiguous question yields a clarification. | |
| C21 | DEFAULT | R19 | Query plan (`app/sql/plan_checker.py`). | Test: a plan is built and shown. | |
| C22 | DEFAULT | R20 | SQL generation (`app/llm/prompts.py`). | Test: the draft passes validation before execution. | |
| C23 | DEFAULT | R21 | Result display (`app/ui/chat.py`). | Test: table equals the DataFrame; 30-row cap. | |
| C24 | DEFAULT | R22 | CSV export (`app/utils/export.py`). | Test: CSV matches the DataFrame. | |
| C25 | DEFAULT | R23 | Transparency panel (`app/ui/transparency.py`). | Test: all 13 items present. | |
| C26 | DEFAULT | R13 | Streamlit app shell (`app/main.py`) wiring the views. | Test: `AppTest` imports `app.main` and renders. | |
| C27 | DEFAULT | R16, R5 | Workspace view (`app/ui/workspace.py`). | Test: `AppTest` shows workspace/context; role-gated. | |
| C28 | DEFAULT | R36 | Caching (`app/core/cache.py`). | Test: a file change is not served stale; membership checked. | |
| C29 | DEFAULT | R37 | Database update behavior. | Test: a file change yields fresh data with no restart. | |
| C30 | DEFAULT | R24 | Time resolution (`app/core/time_resolution.py`). | Test: each relative date resolved against a fixed clock and timezone. | |
| C31 | DEFAULT | R25 | Profiles (`app/db/profiles.py`). | Test: sensitive columns excluded. | |
| C32 | DEFAULT | R26 | Facts payload (`app/analysis/facts.py`). | Test: facts built from a result. | |
| C33 | DEFAULT | R27 | Number verifier (`app/analysis/verifier.py`). | Test: an invented number fails; a correct one passes. | |
| C34 | DEFAULT | R28 | Feedback (`app/core/orchestrator.py`). | Test: feedback creates a new turn and an audit row. | |
| C35 | DEFAULT | R29 | Query history storage. | Test: a run is stored and retrievable. | |
| C36 | DEFAULT | R29 | History view (`app/ui/history.py`). | Test: `AppTest` shows stored runs. | |
| C37 | DEFAULT | R30 | Verified query library (`app/accuracy/verified_queries.py`). | Test: promote; a schema change marks needs_recheck. | |
| C38 | DEFAULT | R31 | Evaluation set (`app/accuracy/evals.py`). | Test: a case runs and compares results. | |
| C39 | DEFAULT | R32 | Analysis mode. | Test: a multi-step analysis; each output names its source. | |
| C40 | DEFAULT | R33 | Execution tiers (`app/core/tiers.py`). | Test: classification; Extended requires confirmation. | |
| C41 | DEFAULT | R34 | Charts (`app/analysis/charts.py`). | Test: a chart is built from a result. | |
| C42 | DEFAULT | R38 | Error handling (`app/core/orchestrator.py`). | Test: attempt limit, timeout message and each refusal. | |
| C43 | DEFAULT | R40 | Honest execution metrics. | Test: only measured metrics are shown. | |
| C44 | DEFAULT | R41 | Follow-ups. | Test: a follow-up changes the plan and the change is shown. | |
| C45 | DEFAULT | R42 | Prompt versioning (`app/llm/prompts.py`). | Test: the version is recorded on a turn. | |
| C46 | DEFAULT | R39 | Security test suite (`tests/test_security.py`). | Test: each control is attacked and holds. | |

## Checkpoint log
| CP | Status | Date | Receipt | Evidence / notes |
|----|--------|------|---------|------------------|
| A0 | DONE | 2026-10-02 | — | venv created, pytest installed; `sys.prefix != sys.base_prefix` = True |
| A1 | DONE | 2026-10-02 | — | git init, identity Rafael Tacconi <tacconirafael@gmail.com>, framework files stamped, hook installed, docs registered, pushed to origin (github.com:RafaelTacconi/DataLens) |
| A2 | DONE | 2026-10-02 | — | environment recorded; handed to Phase B |
| B0 | DONE | 2026-10-02 | — | both source documents read end to end; Parts 1, 2, 4, 6, 7, 8 drafted |
| B1 | DONE | 2026-10-02 | — | gaps asked and answered; decisions recorded in Part 5 |
| B2 | DONE | 2026-10-02 | — | contract signed at G0 (Rafael Tacconi, 2026-10-02) |
| B3 | DONE | 2026-10-02 | — | checkpoint plan (C0–C46) and artifact test approved at G1 |
| B4 | PASS | 2026-10-02 | 20261002T164736Z_check.json | CONTRACT PASS; Status CONFIRMED; handed to Phase C |
| C0 | PASS | 2026-10-02 | 20261002T183634Z_check.json | ARTIFACT WRITTEN + CONTRACT PASS; artifact test red for the right reason (no `app` yet); fixtures synthetic |
| C1 | PASS | 2026-10-02 | 20261002T184440Z_check.json | CONTRACT + TESTS PASS; config module loads every setting; no absolute path |
| C2 | PASS | 2026-10-02 | 20261002T185326Z_check.json | CONTRACT + TESTS PASS; metadata store WAL with all tables |
| C3 | PASS | 2026-10-02 | 20261002T190140Z_check.json | CONTRACT + TESTS PASS; audit append-only via triggers (IntegrityError on UPDATE/DELETE) |
| C4 | PASS | 2026-10-02 | 20261002T192013Z_check.json | CONTRACT + TESTS PASS; identity resolved from OS, source recorded |
| C5 | PASS | 2026-10-02 | 20261002T192502Z_check.json | CONTRACT + TESTS PASS; role matrix + last-Owner protection |
| C6 | PASS | 2026-10-02 | 20261002T192746Z_check.json | CONTRACT + TESTS PASS; path policy rejects bad paths |
| C7 | PASS | 2026-10-02 | 20261002T192921Z_check.json | CONTRACT + TESTS PASS; guarded read-only connection, not shared |
| C8 | PASS | 2026-10-02 | 20261002T193240Z_check.json | CONTRACT + TESTS PASS; authorizer rejects writes/attach/pragma, enforces allow-list; blocks load_extension only, not built-in functions |
| C9 | PASS | 2026-10-02 | 20261002T194041Z_check.json | CONTRACT + TESTS PASS; sqlglot validator rejects unsafe SQL, unknown/hidden tables/columns; sqlglot==30.21.0 pinned |
| C10 | PASS | 2026-10-02 | 20261002T194410Z_check.json | CONTRACT + TESTS PASS; canonical SQL deterministic, hash stored |
| C11 | PASS | 2026-10-02 | 20261002T194634Z_check.json | CONTRACT + TESTS PASS; executor returns Polars DataFrame, fetch cap enforced; polars==1.44.2 pinned |
| C12 | PASS | 2026-10-02 | 20261002T194839Z_check.json | CONTRACT + TESTS PASS; query-run audit logging leaves a row |
| C13 | PASS | 2026-10-02 | 20261002T195124Z_check.json | CONTRACT + TESTS PASS; turn state machine, rerun does not repeat work |
| C14 | PASS | 2026-10-02 | 20261002T195317Z_check.json | CONTRACT + TESTS PASS; provider-neutral LLM Protocol, stand-in accepted |
| C15 | PASS | 2026-10-02 | 20261002T200027Z_check.json | CONTRACT + TESTS PASS; 13 typed Pydantic contracts, malformed rejected; pydantic==2.13.5 pinned |
| C16 | PASS | 2026-10-02 | 20261002T201802Z_check.json | CONTRACT + TESTS PASS; egress levels, default safest, sensitive columns filtered |
| C17 | PASS | 2026-10-02 | 20261002T202035Z_check.json | CONTRACT + TESTS PASS; schema inspection reads tables and columns |
| C18 | PASS | 2026-10-02 | 20261002T202324Z_check.json | CONTRACT + TESTS PASS; catalog/context/terms stored; not-exposed hidden from allow-list |
| C19 | PASS | 2026-10-02 | 20261002T203238Z_check.json | CONTRACT + TESTS PASS; structured interpretation parsed, malformed rejected |
| C20 | PASS | 2026-10-02 | 20261002T203651Z_check.json | CONTRACT + TESTS PASS; clarification decision in orchestrator |

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
| B | B0–B4 (5) | 4 (B1 batch, proposals, G0, G1) | none — the batched B1 questions and the two approval turns were all necessary |

**Be blunt in the last column.** "B1 — three turns re-asking what the design
document already said" is worth more than "fine".

## Decisions made (with rationale)
- **A1 — Framework version: `project-core v1.1`.** The phase files and
  `scripts/verify_build.py` in this repo came from it. Update this line only
  when the project deliberately takes an upgrade.
- 2026-10-02 — Build on the framework's core (`project-core v1.1`), chosen by
  the builder over plain Roo Code. — **BUILDER**
- 2026-10-02 — Approved-data-root path check DROPPED; any SQLite file the user
  can access is accepted. Safety comes from read-only access, schema-only
  egress and sensitive-column exclusion instead. — **BUILDER** (deliberate
  departure from SDD §6.1/§43)
- 2026-10-02 — Timezone is the end-user's machine timezone (read from the
  browser once per session, server fallback), not a single configured value.
  — **BUILDER** (departs from SDD §18/§45)
- 2026-10-02 — LLM access is OpenAI through OpenRouter only; the model string
  lives in `.env` as `LLM_MODEL`; the API key is supplied by the builder and
  never requested. — **BUILDER**
- 2026-10-02 — Caps and retention: 30 rows in chat, 10,000-row CSV export,
  30 s query timeout, 1 year audit retention, 30 days query-history retention.
  — **BUILDER**
- 2026-10-02 — Execution tiers: Simple (0–1 joins, no analysis), Standard
  (2–3 joins or 1–2 analysis steps), Extended (4+ joins, nested subqueries or
  3+ steps; shows the plan and asks for confirmation). — **BUILDER**
- 2026-10-02 — Release scope: all four V1 phases (SDD §44); Phase 5 stays
  future work. — **BUILDER**
- 2026-10-02 — Identity is the OS user (UID + username), fetched, never asked.
  — **BUILDER**
- 2026-10-02 — Tests live in `tests/` at the project root (the framework's
  fixed point); the SDD §40 suggestion of `app/tests/` is not followed.
  — **AGENT**
- 2026-10-02 — Contract signed at G0 (Rafael Tacconi, 2026-10-02). — **BUILDER**
- 2026-10-02 — Checkpoint plan (47 checkpoints, C0–C46) and the artifact test
  approved at G1. — **BUILDER**

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

- 2026-10-02 — The artifact-test fixture is SYNTHETIC (no real sample was
  provided, contract Part 8). Built by `tests/fixtures/make_fixture.py`; two
  variants. — ASKED (B1) / answered: build a synthetic fixture, flagged.

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
- 2026-10-02 — Approved-data-root check dropped (SDD §6.1/§43). Recorded as a
  builder decision in contract Part 5; R6 amended.
- 2026-10-02 — Timezone per user machine, not centrally configured (SDD
  §18/§45). Recorded in contract Part 5; R24 amended.
- 2026-10-02 — Chat row cap is 30, not the SDD §24 "at most 50". Recorded in
  contract Part 5; R21 amended.
