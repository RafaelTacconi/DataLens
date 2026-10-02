# contract.md — DataLens-v1

Status: CONFIRMED

*This is the project's contract: what it must do, who owns it, and how anyone
can check that it does. It is signed by the builder before any code is written
(gate G0) and every checkpoint of the build is minted from Part 6. If the
builder brought written documents (a design document, a spec, notes, an
email), they are PART of this contract — Part 4 lists them and records a hash
of each, so a document that changes after signing is caught, not followed
silently.*

*How to fill it: every answer comes from the builder's words or from a
document listed in Part 4 — quote where it came from. A field nobody can fill
yet says `not sure yet` and gets a row under `## Open questions` in
`memory.md`. A field that does not apply says `not applicable — <why>`. A
blank, `TBD`, `<name>` or `N/A` is not an answer, and
`scripts/verify_build.py` refuses it.*

---

## Part 1 — What it is

| Field | Answer |
|---|---|
| What it is for (the decision or work it supports, one or two sentences) | A safe, transparent Streamlit application that lets non-technical users ask questions about SQLite data in natural language, turning a question into interpretation → query plan → validated SQL → read-only execution → explained result, with the evidence shown. (SDD §1.1) |
| Who uses it (the people or systems that use it, in plain words) | Non-technical business users (Viewer), plus Contributors and Owners, within a workspace. (SDD §1.1, §8) |
| Kind of project (application, command-line tool, library, service, batch job, other — say which) | Application — an interactive Streamlit web app. (ROUTING) |
| How it runs (on demand, on a schedule, always on, imported by other code — and on what machine) | On demand: a Streamlit server that users open in a browser; runs on the machine running Streamlit. (SDD §2.1, §33) |
| Scale (how many users, files, rows or requests — today and in twelve months) | Single user; modest databases. Design for that and do not over-engineer. (B1) |
| Non-goals (what is explicitly NOT built) | PostgreSQL/MySQL and other engines, remote database APIs, generic connectors, cloud discovery, vector databases, background workers, Excel/PDF export, LLM-generated Python or shell execution. (SDD §2.2, §44 Phase 5) |

## Part 2 — What is at stake

*Drafted by the agent from Part 1 and shown once for correction — not an
interview. `not applicable — <why>` is a real answer.*

| Field | Answer |
|---|---|
| If it went wrong unnoticed (who is affected, and how long before they find out) | A user acts on a wrong-but-plausible number; the people relying on the analysis are affected, and it may not be found out until a decision is questioned. The design refuses rather than fabricates, but a plausible wrong answer is the risk. |
| Does anything leave the organisation or move money (yes/no, and what) | Data may leave to an external LLM under the workspace egress policy (schema/aggregates/samples). No money moves. (SDD §13) |
| How sensitive is the data (public / internal / confidential) | confidential — business/trading data; sensitive columns must never be profiled or sent. (SDD §13) |

*Confidential data means real samples are sanitised before they go into
`tests/fixtures/`.*

## Part 3 — Who owns it

| Field | Answer |
|---|---|
| Business owner (accountable for what it does) | Rafael Tacconi (the Builder) |
| Technical owner (builder) | Rafael Tacconi (the Builder) |
| Backup (can run and fix it when the owner is away) | not applicable — sole builder, no separate reviewer |
| Review date (YYYY-MM-DD — when someone re-reads this contract) | not applicable — sole builder |

## Part 4 — Source documents

*Every document the builder brought that this contract rests on. The hash is
written by a command, never typed by hand:
`python scripts/verify_build.py --hash <file>`. If a document changes after
signing, the gate fails until the contract is re-read, the hash updated and
the contract re-signed. Documents stay in the project and are committed. If
the builder brought nothing, write one row: `none — interview only`.*

*Precedence says which document wins when two disagree (for example "the
design document is the product contract; the implementation guide wins on
how to build it"). Where a document disagrees with itself or with another and
precedence does not settle it, that is a question for the builder.*

| File | Hash (12 characters) | What it covers | Precedence |
|---|---|---|---|
| SDD-Natural-Language-SQLite-Data-Analyst-v1.md | c9e80dd5d5e6 | The product contract: what the product is, scope, architecture, requirements, acceptance criteria and delivery order. (SDD §1–§46) | Product behaviour. The guide says "Treat SDD-v1.md as the product contract." (Guide §1) |
| AI-Coding-Assistant-Implementation-Guide-v1.md | 76aa28f34211 | The implementation contract: how to build it — non-negotiable rules, implementation sequence, module responsibilities, checklists. (Guide §1–§18) | How to build it. "Treat this document as the implementation contract." (Guide §1). Safety requirements win over both (Guide §1). |

## Part 5 — Decisions the documents leave open

*Every value the documents leave to be decided — a path, a timezone, a
provider, a limit, a retention period — and every material ambiguity found
while reading. One row each, answered by the builder. `use the documented
default (<value>)` is an answer when a document gives a default. `not sure
yet` is an answer if `memory.md`'s `## Open questions` has a row naming the
decision. With no documents, record here the decisions the interview settled
that are not obvious from Part 6.*

| Decision | Answer | Where the answer came from |
|---|---|---|
| Approved data-root paths | DROPPED. The user points the app at any SQLite file they can access. The safety guardrail is instead: sensitive columns are never profiled or sent, and egress is schema-only by default. (Deliberate departure from SDD §6.1/§43.) | B1 — BUILDER |
| Company timezone | The end-user's machine timezone, read from the browser once per session, falling back to the server's timezone if it cannot be read. (Departs from SDD §18/§45 "configured centrally".) | B1 — BUILDER |
| Identity source | The user's OS UID and username, fetched automatically, never asked; the identity source is recorded as `os`. | B1 — BUILDER |
| LLM provider and model | OpenAI, accessed through OpenRouter; the exact model string lives in `.env` as `LLM_MODEL`; the API key is supplied later by the Builder and is never requested. | B1 — BUILDER |
| Default egress level | `schema_only` (the SDD's stated safest default). | B1 — BUILDER |
| Query timeouts | 30 seconds per statement. | B1 — BUILDER |
| Row/result caps | 30 rows shown in chat (chat is also exportable); CSV export cap 10,000 rows. | B1 — BUILDER |
| Execution-tier thresholds | Simple: 0–1 joins, one query, no analysis steps. Standard: 2–3 joins, or 1–2 analysis steps. Extended: 4+ joins, nested subqueries, or 3+ analysis steps, which shows the plan and asks for confirmation. | B1 — BUILDER |
| Audit retention | 1 year. | B1 — BUILDER |
| Query-history retention | 30 days. | B1 — BUILDER |
| Scale | Single user, modest databases. Do not over-engineer. | B1 — BUILDER |
| Release scope | All four V1 phases (SDD §44); Phase 5 stays future work. | B1 — BUILDER |
| Real sample | None. Build a synthetic fixture, flagged as synthetic. | B1 — BUILDER |
| Credentials | `.env.example` carries the variable name only; a git-ignored `.env` holds the value, filled by the Builder. The value is never sent. | B1 — BUILDER |

## Part 6 — Requirements

*What the project must do, one row per requirement, in plain words a
colleague could check by hand. The checkpoint plan is minted from these rows
(B3) — every row becomes one or more checkpoints. When a document holds the
detail, the row names the section and stays short; it does not copy the
document. `On failure` says what the project does when this cannot be done
(stop, refuse with a message, fall back to …).*

| ID | Requirement | From | Accept (observable — a command, a test, or a thing a person can see) | On failure |
|---|---|---|---|---|
| R1 | Configuration: settings for metadata DB path, approved data roots, timezone, row cap, export cap, query timeout, LLM timeout, provider/model, egress default, tier thresholds; no hard-coded environment paths. | SDD §45; Guide §3 Step 1 | A config module loads every setting; a test asserts no absolute path is hard-coded in code. | Refuse to start, naming the missing setting. |
| R2 | Metadata store: a separate SQLite DB in WAL mode holding workspaces, memberships, context versions, catalog, business terms, profiles, verified queries, evaluation cases, query runs, audit events. | SDD §10; Guide §3 Step 2 | A test opens the metadata DB and finds every table. | Stop; the app cannot run without its metadata store. |
| R3 | Audit append-only: audit events cannot be updated or deleted by application code. | SDD §11 | A test attempts UPDATE and DELETE on audit rows and both fail. | Refuse the operation and log the attempt. |
| R4 | Identity: a stable user identifier for audit and permissions; a self-declared identity is weak attribution and its source is recorded. | SDD §9; Guide §3 Step 3 | A test resolves a user and records the identity source. | Treat as weak attribution; expose no admin functions. |
| R5 | Workspace membership and roles: Viewer/Contributor/Owner enforced in Python; last-Owner protection. | SDD §7, §8; Guide §3 Step 3 | Tests assert each role's allowed and denied actions, and that the last Owner cannot be removed. | Deny the action with a clear message. |
| R6 | Path policy: a target path must be a real file, a SQLite DB, and not the metadata DB or its -wal/-shm. (The approved-data-root check is dropped by builder decision — see Part 5.) | SDD §6.1 (amended by builder); Guide §3 Step 4 | Tests reject nonexistent, directory, non-SQLite, metadata-DB and -wal/-shm paths. | Reject the path, naming the reason. |
| R7 | Guarded read-only connection: mode=ro, query_only, authorizer, progress handler; one connection per query; never shared via st.cache_resource. | SDD §6.2, §22; Guide §3 Step 5 | A test opens a connection and asserts read-only; a test asserts connections are not shared. | Refuse to execute. |
| R8 | Authorizer: reject INSERT/UPDATE/DELETE/CREATE/DROP/ALTER/ATTACH/DETACH/PRAGMA/extension loading; enforce the exposed-table allow-list. | SDD §6.2; Guide §7 | Tests send each prohibited action directly to the connection and all are rejected. | Reject the action. |
| R9 | SQL validator: sqlglot SQLite dialect; one statement; SELECT or WITH-SELECT; tables/columns exist and are exposed; no hidden second statement; no prohibited functions; joins meet the plan; SQL matches the plan; date literals match Python's resolution; output columns valid. | SDD §21; Guide §6 | Tests reject each unsafe or mismatched case and accept a valid query. | Reject the SQL and return the validation error. |
| R10 | Canonical SQL: render one canonical string, store its hash, execute exactly that string; displayed SQL equals executed SQL. | SDD §21; Guide §6 | A test asserts the displayed string equals the executed string and the stored hash matches. | Refuse to execute. |
| R11 | Executor: canonical SQL + allowed tables → Polars DataFrame + execution metrics; capped fetch, never fetchall. | SDD §22, §24; Guide §3 Step 7 | A test executes a query and asserts a Polars DataFrame and that the fetch cap is enforced. | Stop the query and report the cap. |
| R12 | Basic audit logging of governance and query actions. | SDD §11 | A test performs an audited action and finds the audit row. | Log the failure; never drop it silently. |
| R13 | Streamlit turn state machine: states NEW→…→FEEDBACK_GIVEN with terminal REFUSED/FAILED/TIMED_OUT; a rerun must not repeat an LLM call or query; state in st.session_state. | SDD §33; Guide §3 Step 11, §5 | A test simulates a rerun and asserts no repeated LLM call or query. | Keep the stored state; do not re-run. |
| R14 | LLM provider interface: a provider-neutral Protocol (interpret/plan/generate_sql/explain); prompts separate from business logic. | SDD §35; Guide §3 Step 8 | A test substitutes a stand-in provider and the pipeline runs. | Fail the turn clearly. |
| R15 | Schema inspection: read the target DB's tables and columns. | SDD §44 Phase 2 | A test inspects a fixture DB and finds its tables and columns. | Report that the schema could not be read. |
| R16 | Catalog, business context and business terms per workspace; objects may be marked not exposed. | SDD §14 | A test stores and retrieves context; a not-exposed object is hidden from LLM context and rejected by validation and the authorizer. | Exclude the object; reject queries touching it. |
| R17 | Query understanding: the LLM returns a structured interpretation (intent, entity, metrics, dimensions, filters, ranking, time intent, output, ambiguities). | SDD §16 | A test parses a stand-in interpretation into the typed model. | Fail the turn clearly. |
| R18 | Clarification: material ambiguity asks the user; minor ambiguity resolved by a rule shows the assumption. | SDD §17 | A test with an ambiguous question produces a clarification, not a guess. | Ask the user. |
| R19 | Query plan: a structured QueryPlan displayed to the user in plain language. | SDD §19 | A test builds a plan and the transparency record shows it. | Fail the turn clearly. |
| R20 | SQL generation: the LLM drafts SQLite SQL from the approved plan; the draft is never executed directly. | SDD §20 | A test asserts the draft passes through validation before execution. | Reject and retry within the attempt limit. |
| R21 | Result display: the exact result table comes from the DataFrame; at most 30 rows in chat; truncation is stated. | SDD §24 (cap amended by builder); Part 5 | A test asserts the displayed table equals the DataFrame and the 30-row cap. | Show a preview and state truncation. |
| R22 | CSV export: generated from the DataFrame, capped. | SDD §24 | A test exports a result and asserts the CSV matches the DataFrame. | Refuse export beyond the cap. |
| R23 | Transparency panel: every completed turn shows request, understanding, sources, why chosen, columns, plan, canonical SQL, execution info, assumptions, resolved period, exact result, validation status, provenance. | SDD §28 | A test builds a transparency record from stored state and finds all 13 items. | Fail the turn clearly. |
| R24 | Time resolution: Python resolves relative dates (today, this week/month/year, last month, YTD) into explicit start/end, using the end-user's machine timezone (Part 5); the resolved period is shown. | SDD §18; Guide §11; Part 5 | A test resolves each relative date against a fixed clock and timezone and asserts the bounds. | Ask the user or refuse. |
| R25 | Profiles: safe data profiles per workspace; sensitive columns never profiled. | SDD §44 Phase 3, §13 | A test profiles a fixture and asserts sensitive columns are excluded. | Skip the column. |
| R26 | Facts payload: Python builds the facts the explanation may use. | SDD §25 | A test builds a facts payload from a result and asserts its values. | Fail the turn clearly. |
| R27 | Number verifier: every numerical claim in the explanation is checked against the facts payload; on failure the explanation is not shown as factual. | SDD §25 | A test with an invented number fails verification; a correct explanation passes. | Regenerate within policy or show a safe fallback. |
| R28 | Feedback: Correct / Not what I meant; a correction creates a new turn and is audited; the previous turn is not silently modified. | SDD §29 | A test records feedback and asserts a new turn and an audit row. | Record the failure. |
| R29 | Query history: completed runs are stored and viewable. | SDD §44 Phase 3 | A test runs a query and finds it in history. | Report that history could not be stored. |
| R30 | Verified query library: Contributors/Owners promote a result; a schema/context change marks it needs_recheck and it is not used until re-verified. | SDD §31 | A test promotes a query, changes the schema, and asserts needs_recheck. | Exclude the query from examples. |
| R31 | Evaluation set: golden questions per workspace; evaluate results, not SQL text; a regression is visible to the user who saved the change. | SDD §32 | A test runs an evaluation case and asserts the result comparison. | Report the regression. |
| R32 | Analysis mode: question → analysis plan → multiple queries/Polars steps → facts → evidence-backed explanation; every output identifies its source. | SDD §26 | A test runs a multi-step analysis and asserts each output names its source. | Fail the turn clearly. |
| R33 | Execution tiers: Simple/Standard/Extended computed by Python from the plan and EXPLAIN QUERY PLAN; Extended shows the plan and requires confirmation. | SDD §27 | A test classifies queries and asserts Extended requires confirmation. | Require confirmation. |
| R34 | Charts: charts built from the result DataFrame. | SDD §44 Phase 4 | A test builds a chart from a result. | Show the table instead. |
| R35 | LLM data egress policy: schema_only/aggregates/samples; sensitive columns never profiled or sent; default is the safest configured level. | SDD §13 | A test asserts the egress level controls what is sent and the default is safest. | Send nothing beyond the policy. |
| R36 | Caching: schema/profile key = resolved_path+mtime_ns+file_size; query-result key adds canonical_sql; TTL; membership checked before a cached result. | SDD §34; Guide §8 | A test changes the file and asserts the cache is not reused; a test asserts membership is checked. | Recompute. |
| R37 | Database update behavior: detect a changed file, invalidate schema/profile/query caches, refresh on next use, no restart. | Guide §9 | A test changes the file and asserts fresh data without a restart. | Recompute. |
| R38 | Error handling: validation error allows up to 3 total SQL attempts then FAILED; timeout is not auto-retried; ambiguity asks; missing data says so; unsupported explains. | SDD §37 | Tests assert the attempt limit, the timeout message and each refusal. | Refuse with a clear message. |
| R39 | Security tests: each control is tested by attempting to bypass it. | SDD §38, §42; Guide §14 | The security test suite passes. | Fail the build. |
| R40 | Honest execution metrics: only metrics the system measures (duration, rows returned, truncated, plan shape); never "rows scanned" unless measured. | SDD §23 | A test asserts only measured metrics are shown. | Omit the metric. |
| R41 | Conversation follow-ups: a follow-up modifies the previous structured plan, not prose; transparency states the change. | SDD §30 | A test applies a follow-up and asserts the plan changed and the change is shown. | Fail the turn clearly. |
| R42 | Prompt versioning: prompts are versioned and every turn records the prompt-template version. | SDD §36 | A test asserts the version is recorded on a turn. | Fail the turn clearly. |
| R43 | Typed data contracts: Pydantic models for Interpretation, Ambiguity, QueryPlan, QueryStep, ExecutionMetrics, FactsPayload, TransparencyRecord, Turn, AuditEvent, Workspace, Membership, VerifiedQuery, EvaluationCase. | SDD §41; Guide §3 Step 9 | A test constructs each model and rejects malformed input. | Reject malformed output. |

## Part 7 — Packages it needs to run

*Only what the project needs to RUN (installed from `requirements.txt`). Test
tools (`pytest`, `ruff`) are not rows here. A new package is a new row, agreed
with the builder BEFORE it is installed. Write `none — standard library only`
if there are none.*

| Library | Version | Why | What breaks without it |
|---|---|---|---|
| streamlit | pin at first install (C0) | The user interface. | No screen. |
| polars | pin at first install (C0) | Result DataFrames, facts, charts, export. | No result handling. |
| sqlglot | pin at first install (C0) | SQL parsing, validation, canonicalization. | No SQL validation. |
| pydantic | pin at first install (C0) | Typed LLM and data contracts. | No structured contracts. |
| openai | pin at first install (C0) | Client for OpenAI through OpenRouter. | No interpretation, planning or explanation. |

## Part 8 — How it is checked

| Field | Answer |
|---|---|
| Test command | `python -m pytest -q` |
| Smoke command (proves it starts without doing real work; ends on its own — never a server; no pipes) | python -c "import app.main" |
| Primary output (what the artifact test builds and asserts on) | The executed query result (a Polars DataFrame) plus the transparency record for a known question against a fixture SQLite DB, with the LLM replaced by a scripted stand-in. |
| Real sample available? (a file name, or NONE — the fixture is then hand-built and flagged) | none — no real sample was provided; the main test fixture is hand-built, synthetic and flagged as synthetic. (B1) |

*The smoke command is run by `scripts/verify_build.py` exactly as written, from
the project root, so it must work on a clean checkout with no credential and
no network. For a library: an import. For an application: a check mode or an
import of its entry module. `not applicable — <why>` if nothing can start.*

---

## Sign-off

| Role | Name | Date |
|---|---|---|
| Builder (technical owner) | Rafael Tacconi | 2026-10-02 |

*The builder signs by stating, in their own message, that every field above is
correct — never in the same message that presents the contract. "Looks good"
answers "do you want this", not "is every field correct". The agent writes the
name and date the builder gave; it never invents either.*

## Additions after sign-off

*Something the contract never contained, agreed during the build. One row
each; the signed Parts above stay as signed. Three additions in one phase
means the contract no longer describes the project: re-open it and re-sign.*

| Date | What was added | Why | Checkpoint |
|---|---|---|---|

---

*Footer rule: any change to Parts 1–6 after sign-off flips `Status` back to
`DRAFT` and needs a fresh sign-off before more code is written. The commit
hook enforces it: no project code is committed while this file is not
CONFIRMED.*
