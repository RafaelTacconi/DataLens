# Software Design Document — Natural-Language SQLite Data Analyst

**Version:** 1.0  
**Status:** V1 implementation specification  
**Audience:** AI coding assistant, builder, reviewer, tester  
**Primary goal:** Build a safe, transparent Streamlit application that lets non-technical users ask questions about SQLite data in natural language.

---

## 1. Product Summary

### 1.1 What this product is

A **Streamlit + Python data analyst**.

A user connects the application to a SQLite database file, provides business context, and asks questions in normal language.

The application turns:

**User question → interpretation → query plan → SQL → validation → SQLite execution → result → explanation**

The user can inspect the evidence behind the answer.

### 1.2 What this product is not

It is **not primarily a chatbot**.

Chat is the user interface. The actual product is:

> A transparent natural-language query and analysis layer over SQLite.

The system must never invent data to make an answer look complete.

---

# 2. V1 Scope

## 2.1 Supported data source

V1 supports **SQLite database files accessible by the machine running Streamlit**.

Supported examples:

- A SQLite file on a shared/network drive accessible to the Streamlit server.
- A SQLite file on the Streamlit server's local disk.
- A OneDrive-synced SQLite file, if the synced path is accessible to the Streamlit server.

### Important

"Local `C:\...`" means local to the **machine running Streamlit**.

A browser user's personal `C:\...` path is not automatically accessible to a remote Streamlit server.

## 2.2 Not supported in V1

Do not implement:

- PostgreSQL/MySQL/etc.
- Remote database APIs.
- Generic database connectors.
- Cloud database discovery.
- Vector databases.
- Background workers.
- Excel/PDF export.
- LLM-generated Python or shell execution.

These may be future work.

## 2.3 Database selection

The user must provide/select the SQLite file path.

For V1, "registering a database" simply means:

1. User creates or selects a workspace.
2. User provides the SQLite file path.
3. Application validates the path.
4. Application connects read-only.
5. Application inspects the schema.

Do not introduce a separate database-registration service.

---

# 3. Core Design Principles

These rules are mandatory.

1. **LLM interprets.**
2. **Python controls.**
3. **SQLite retrieves.**
4. **Polars analyzes.**
5. **User validates.**

Additional rules:

- Trust is more important than conversational completeness.
- If the system cannot reliably answer, say so.
- Never fabricate rows, figures, dates, or conclusions.
- Do not use fake confidence scores.
- Show concrete evidence instead.
- Security guarantees must be enforced in code, not only by prompts.
- The LLM never gets database credentials or direct database access.
- The exact SQL shown to the user must be the SQL executed.
- Result tables and CSV files must come directly from Python query results, never from LLM-generated text.
- Every important guarantee must have an automated test.

---

# 4. High-Level Architecture

```text
                         ┌──────────────────────┐
                         │      Streamlit UI    │
                         │ Chat + Transparency  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Application Layer  │
                         │ orchestration/state  │
                         └───────┬───────┬──────┘
                                 │       │
                   ┌─────────────┘       └──────────────┐
                   ▼                                    ▼
          ┌─────────────────┐                  ┌─────────────────┐
          │       LLM       │                  │ Python Controls │
          │ interpretation  │                  │ validation      │
          │ planning        │                  │ time resolution │
          │ SQL drafting    │                  │ execution       │
          │ explanation     │                  │ verification    │
          └─────────────────┘                  └────────┬────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────┐
                                              │  Guarded SQLite │
                                              │     read-only   │
                                              └────────┬────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │      Polars     │
                                              │ facts / charts  │
                                              │ export          │
                                              └─────────────────┘

          ┌─────────────────────────────────────────────────────┐
          │ Separate Metadata SQLite                             │
          │ workspaces / members / context / catalog / history │
          │ evaluations / verified queries / audit              │
          └─────────────────────────────────────────────────────┘
```

The metadata database must be a **different SQLite file** from every target business database.

---

# 5. End-to-End Query Flow

For every user question:

1. Check that the user can access the workspace.
2. Load current workspace configuration/context.
3. Detect whether the target SQLite file changed.
4. Refresh schema/profile information if needed.
5. Retrieve relevant catalog/context information.
6. Ask the LLM for a structured interpretation.
7. Detect material ambiguity.
8. Ask the user for clarification when required.
9. Resolve relative dates in Python.
10. Create a structured query plan.
11. Generate SQL from the plan.
12. Validate SQL using `sqlglot`.
13. Canonicalize the SQL.
14. Run the canonical SQL through the guarded read-only SQLite executor.
15. Convert results to a Polars DataFrame.
16. Apply result/row limits.
17. Build a Python facts payload.
18. If explanation is needed, give only permitted facts to the LLM.
19. Verify every number in the explanation against the facts payload.
20. Display:
   - answer,
   - exact result table,
   - assumptions,
   - tables/columns used,
   - canonical SQL,
   - execution information,
   - provenance.
21. Store query history and audit information.
22. Accept user feedback.

---

# 6. Database Rules

## 6.1 Path policy

A target database path must:

- Resolve to a real file.
- Be inside an approved data root.
- Remain inside the root after symlink resolution.
- Be a SQLite database.
- Not be the metadata database.
- Not be the metadata database's `-wal` or `-shm` file.

Reject paths outside approved roots.

## 6.2 Read-only enforcement

Use all of these:

- SQLite `mode=ro`.
- `PRAGMA query_only`.
- SQLite authorizer callback.
- SQL AST validation.

The authorizer must reject:

- INSERT
- UPDATE
- DELETE
- CREATE
- DROP
- ALTER
- ATTACH
- DETACH
- PRAGMA
- extension loading
- any other non-read operation

The authorizer must also enforce the workspace's exposed-table allow-list.

## 6.3 Latest data requirement

The application must query the **current contents of the SQLite file**.

Do not cache query results indefinitely.

Schema/profile/query cache keys must include the database file identity/change information, at minimum:

- resolved path
- modification time (`mtime_ns`)
- file size

Query-result caching must also include canonical SQL.

When the file changes, stale schema/profile/query caches must not be reused.

---

# 7. Workspace

A workspace represents:

> **One target SQLite database + the business knowledge needed to query it.**

A workspace contains:

- target database path
- business context
- schema/catalog descriptions
- business terms and rules
- exposed/not-exposed tables and columns
- data profiles
- verified queries
- evaluation cases
- query history
- audit records
- members and roles
- LLM data-egress policy

Multiple workspaces may point to the same SQLite file.

---

# 8. Roles

V1 has three workspace roles.

| Action | Viewer | Contributor | Owner |
|---|---:|---:|---:|
| Ask questions | Yes | Yes | Yes |
| View results/history | Yes | Yes | Yes |
| Give feedback | Yes | Yes | Yes |
| Edit business context | No | Yes | Yes |
| Edit catalog | No | Yes | Yes |
| Edit business terms | No | Yes | Yes |
| Manage verified queries | No | Yes | Yes |
| Manage evaluation cases | No | Yes | Yes |
| Change database path | No | Yes | Yes |
| Manage members | No | No | Yes |
| Change egress policy | No | No | Yes |
| Archive/restore workspace | No | No | Yes |

The application must enforce permissions in Python.

The UI hiding a button is **not** an authorization mechanism.

---

# 9. Identity and Access

The host platform controls who can open the application.

Inside the application, workspace membership controls workspace access.

The application must have a stable user identifier for audit and permissions.

If identity is self-declared, treat it as weak attribution:

- Do not expose platform-admin functions.
- Do not treat a typed user ID as strong identity.
- Record the identity source.

Do not build a large enterprise identity system in V1.

---

# 10. Metadata Store

Use a separate SQLite database in WAL mode.

It stores at least:

- workspaces
- memberships
- context versions
- catalog
- business terms
- profiles
- verified queries
- evaluation cases
- query runs
- audit events

Rules:

- Target-database SQL must never reach the metadata database.
- Target database paths must not point at the metadata database.
- Metadata access is always workspace-scoped.
- `st.session_state` must not be the source of truth for membership, roles, or configuration.

---

# 11. Audit Logging

Audit important governance and query actions.

Examples:

- workspace created
- member added/removed
- role changed
- database path changed
- context changed
- catalog changed
- business term changed
- egress policy changed
- query run
- validation failure
- user feedback
- verified query promoted
- evaluation run

Audit records must be append-only.

Application code must not be able to update/delete audit rows.

Every audit event records:

- event type
- workspace
- actor
- identity source
- timestamp
- optional target/reference
- before/after values where relevant

---

# 12. LLM Responsibilities

The LLM may:

- interpret the user's request
- identify metrics/entities
- identify ambiguity
- create a query plan
- draft SQL
- explain verified results

The LLM may **not**:

- connect to SQLite
- receive SQLite credentials
- execute SQL
- execute Python
- execute shell commands
- choose files outside the application controls
- bypass access checks
- decide whether SQL is safe
- create result tables from imagination

The LLM is an untrusted planner, not an authority.

---

# 13. LLM Data Egress

Some workspace information may be sent to an external LLM.

The workspace must have an explicit egress policy.

Suggested V1 levels:

### `schema_only`

May send:

- schema
- table/column descriptions
- business terms
- business rules
- resolved time bounds
- safe metadata

Do not send result rows.

### `aggregates`

May additionally send:

- aggregated result values
- derived facts
- safe profiles

### `samples`

May additionally send approved sample rows.

Sensitive columns must never be profiled or sent.

Default should be the safest configured level until the data owner explicitly chooses otherwise.

---

# 14. Business Context and Catalog

Each workspace may contain:

- plain-language database description
- table descriptions
- column descriptions
- business definitions
- business rules
- relationships
- preferred reporting layers

Example:

> Trading volume = SUM(gold_trades.notional_value), monetary unless the user specifies another measure.

Tables/columns may be marked **not exposed**.

Not-exposed objects must be:

- hidden from LLM context
- rejected by SQL validation
- rejected by the SQLite authorizer

---

# 15. Context Retrieval

V1 does not need a vector database.

Use deterministic retrieval such as:

- keyword matching
- entity matching
- table/column names
- business terms
- relationships
- profiles
- verified query examples

Only relevant context should be sent to the LLM.

---

# 16. Query Understanding

The LLM must return structured data.

Minimum interpretation:

- user intent
- entity
- metrics
- dimensions
- filters
- ranking
- time intent
- requested output
- ambiguities

Do not accept free-form interpretation as the internal source of truth.

---

# 17. Clarification

If an ambiguity can materially change the result:

**Do not guess. Ask the user.**

Examples:

- "Revenue" could mean gross or net.
- "Activity" could mean count or monetary volume.
- "Customers" could mean all customers or active customers.

Minor ambiguity may be resolved by an existing business rule, but the assumption must be shown to the user.

Unknown filter values should also trigger clarification when profiling proves the value does not exist.

---

# 18. Dates and Time

Relative dates must be resolved by Python, not by the LLM.

Examples:

- today
- this week
- this month
- this year
- last month
- year to date

Python converts these into explicit start/end values.

The resolved period must appear in the transparency panel.

Example:

> "This year" → `2026-01-01` through the current configured date boundary.

The application timezone is configured centrally.

---

# 19. Query Plan

The LLM produces a structured `QueryPlan`.

The plan should contain:

- intent
- tables
- columns
- joins
- filters
- metrics
- grouping
- ordering
- limits
- resolved time bounds
- expected output
- analysis steps if applicable

The plan is displayed to the user in plain language.

---

# 20. SQL Generation

The LLM converts the approved plan into SQLite SQL.

Allowed query form:

- exactly one statement
- `SELECT`
- or `WITH ... SELECT`

The generated SQL is only a **draft**.

It is never executed directly.

---

# 21. SQL Validation

Use `sqlglot` with the SQLite dialect.

Validation must check:

1. Exactly one statement.
2. Statement is read-only.
3. Only SELECT/WITH-SELECT.
4. Tables exist.
5. Columns exist.
6. Tables are exposed.
7. No hidden second statement.
8. No prohibited functions/features.
9. Joins meet the plan's declared relationships where required.
10. SQL matches the query plan.
11. Resolved date literals match Python's date resolution.
12. Output column names are valid and unambiguous.

After validation, render **canonical SQL**.

Only canonical SQL may be executed.

**Displayed SQL = executed SQL.**

---

# 22. Query Execution

Open a fresh SQLite connection for each target query.

Do not share SQLite connections between Streamlit sessions/threads.

Execution controls:

- read-only URI
- `query_only`
- authorizer
- progress-handler timeout
- row fetch cap
- export cap
- exposed-table allow-list

Do not use `fetchall()` for potentially large results.

Use a capped fetch strategy.

---

# 23. Honest Execution Metrics

Show only metrics the system can actually measure.

Allowed examples:

- wall-clock duration
- rows returned
- result truncated yes/no
- query plan shape
- cached table size information
- approximate VM-step information if implemented

Do **not** display "rows scanned" unless a real reliable measurement is implemented.

---

# 24. Result Handling

The exact SQLite result becomes a Polars DataFrame.

Rules:

- LLM does not create the result table.
- UI table comes from the DataFrame.
- CSV comes from the DataFrame.
- Values must not be changed for presentation.
- Mixed/problematic types should be handled explicitly and noted.
- Display at most 50 rows in chat.
- Larger results show a preview and offer capped CSV export.
- If the result was truncated, say so clearly.

---

# 25. Facts and Explanation

Before asking the LLM to explain a result, Python creates a **facts payload**.

The facts payload contains only facts that the explanation is allowed to use.

The explanation LLM must not invent additional numbers.

A deterministic number verifier must check every numerical claim against the facts payload.

If verification fails:

- do not show the unverified explanation as factual;
- either regenerate within the allowed repair policy or show a safe fallback based on verified facts.

---

# 26. Analysis Mode

V1 supports two modes.

### Query mode

One user question → one main query → result.

### Analysis mode

Question → analysis plan → multiple queries and/or Polars transformations → facts → evidence-backed explanation.

Analysis plans must be shown before execution when the execution tier requires confirmation.

Every analysis output must identify which query/transformation produced it.

---

# 27. Execution Tiers

Use one deterministic tier system.

The tier is calculated by Python from the query plan and `EXPLAIN QUERY PLAN`.

Never trust an LLM-generated "complexity" label.

At minimum:

### Simple

- one read query
- normal filters/aggregations
- small result

Runs automatically.

### Standard

- more joins/grouping
- moderate result
- analysis with several safe steps

Runs automatically within configured limits.

### Extended

- expensive or multi-step analysis
- larger limits
- potentially expensive operations

Show the plan and require user confirmation.

Exact thresholds are configuration, not prompt instructions.

---

# 28. Transparency Panel

Every completed turn must show:

1. User request
2. What the system understood
3. Tables/data sources used
4. Why those sources were chosen
5. Columns used
6. Query/analysis plan
7. Canonical executed SQL
8. Execution information
9. Assumptions
10. Resolved time period
11. Exact result
12. Validation status
13. Provenance

Provenance should include where applicable:

- context version
- model/provider
- prompt-template version
- egress level
- correction/retry attempts

Do not expose chain-of-thought.

"Why this answer?" means a short method summary derived from the plan, not hidden reasoning.

---

# 29. User Feedback

Every result supports:

- **Correct**
- **Not what I meant**

For "Not what I meant":

1. Capture correction text.
2. Create a new turn.
3. Rebuild interpretation/plan/SQL.
4. Do not silently modify the previous turn.
5. Audit the feedback.

Correct results may be promoted to the verified query library by Contributors/Owners.

---

# 30. Conversation Follow-Ups

Follow-ups modify the previous **structured plan**, not previous prose.

Example:

User:

> Show sales by country.

Follow-up:

> Now only Europe.

The application changes the structured filter and generates a new query.

Transparency should say:

> Added filter: region = Europe.

Every turn remains independently auditable.

---

# 31. Verified Query Library

A verified query stores:

- original question
- structured plan
- canonical SQL
- context version
- result expectation/status

Members may mark results correct.

Only Contributors/Owners may promote a result into the verified library.

Use the top few relevant verified examples as LLM examples.

If schema/context changes affect a verified query, mark it `needs_recheck` and do not use it until re-verified.

---

# 32. Evaluation Set

Each workspace can maintain small golden questions.

Each case stores:

- natural-language question
- expected result columns
- expected result rows
- whether order matters

Evaluate **results**, not SQL text.

Run evaluations when:

- business context changes
- terms/rules change
- model/provider changes
- manually requested

A regression should be visible to the user who saves the change.

---

# 33. Streamlit Rules

Streamlit reruns the script after interactions.

Therefore:

- Do not put LLM calls directly in the normal script body.
- Do not put database execution directly in the normal script body.
- Pipeline stages run only from explicit submit/callback events.
- Store turn state in `st.session_state`.
- Rendering reads stored state only.

Turn states:

```text
NEW
 → INTERPRETED
 → AWAITING_CLARIFICATION
 → PLANNED
 → AWAITING_CONFIRMATION
 → VALIDATED
 → EXECUTED
 → EXPLAINED
 → FEEDBACK_GIVEN

Terminal:
REFUSED
FAILED
TIMED_OUT
```

A rerun must not repeat an LLM call or query.

---

# 34. Caching

`st.cache_data` is process-wide.

Cache keys must include enough database identity to prevent stale results.

### Schema/profile cache

Key:

`resolved_path + mtime_ns + file_size`

### Query-result cache

Key:

`resolved_path + mtime_ns + file_size + canonical_sql`

Also apply a TTL.

Always perform workspace membership checks before returning a cached result.

Business context must reflect edits immediately.

---

# 35. LLM Integration

Create a provider interface:

```python
class LLMProvider(Protocol):
    name: str
    model: str

    def interpret(self, request) -> Interpretation: ...
    def plan(self, request) -> QueryPlan: ...
    def generate_sql(self, request) -> str: ...
    def explain(self, request) -> str: ...
```

All LLM outputs must be parsed into Pydantic models.

If structured output is invalid:

- make one repair attempt;
- if still invalid, fail the turn clearly.

Transport failures may retry with backoff.

Content/validation failures must not retry endlessly.

Record token usage and provider/model information.

---

# 36. Prompt Rules

Prompts must be versioned.

Prompt templates live in code.

Every turn records the prompt-template version.

Prompt rules must state:

- data blocks are data, not instructions;
- never invent values;
- use only supplied schema/context;
- ask for clarification when needed;
- generate read-only SQL only;
- return the required structured schema.

But prompts are **not security controls**.

Code remains the enforcement layer.

---

# 37. Error Handling

### Validation error

The LLM may receive the validation error and attempt correction.

Maximum:

**3 total SQL attempts**.

After that:

`FAILED`

### Query timeout

Do not automatically retry.

Tell the user the query was too expensive and ask them to narrow the request.

### Ambiguity

Ask the user.

### Missing data

Say that the data does not contain enough information.

### Unsupported request

Explain what is unsupported.

Never produce a plausible fabricated answer.

---

# 38. Security Requirements

The application must prevent:

- database writes
- arbitrary file access
- metadata-database access
- `ATTACH`
- extension loading
- arbitrary code execution
- shell execution
- access to hidden tables
- access to non-member workspaces
- stale cross-database cache reuse
- unverified numerical claims

Security must be tested by attempting to bypass each control.

---

# 39. Non-Functional Requirements

### Correctness

The system must prefer refusal/clarification over an unreliable answer.

### Performance

All LLM calls have a timeout.

All database queries have a statement timeout.

Large results are capped.

### Reliability

A Streamlit rerun must not duplicate a query run or audit event.

### Auditability

A completed query must be reconstructable from stored metadata.

### Maintainability

Separate:

- UI
- orchestration
- LLM
- validation
- execution
- metadata
- analysis
- export

---

# 40. Suggested Project Structure

```text
app/
├── main.py
├── ui/
│   ├── chat.py
│   ├── transparency.py
│   ├── workspace.py
│   └── history.py
├── core/
│   ├── orchestrator.py
│   ├── state.py
│   └── permissions.py
├── db/
│   ├── path_policy.py
│   ├── connection.py
│   ├── authorizer.py
│   ├── executor.py
│   ├── schema.py
│   └── profiles.py
├── sql/
│   ├── validator.py
│   ├── canonical.py
│   └── plan_checker.py
├── metadata/
│   ├── store.py
│   ├── models.py
│   └── audit.py
├── llm/
│   ├── provider.py
│   ├── prompts.py
│   ├── structured_output.py
│   └── providers/
├── analysis/
│   ├── facts.py
│   ├── verifier.py
│   └── charts.py
├── accuracy/
│   ├── verified_queries.py
│   └── evals.py
├── models/
│   └── contracts.py
├── utils/
│   └── export.py
├── config/
│   └── settings.py
└── tests/
```

---

# 41. Core Data Contracts

Use typed models for at least:

- `Interpretation`
- `Ambiguity`
- `QueryPlan`
- `QueryStep`
- `ExecutionMetrics`
- `FactsPayload`
- `TransparencyRecord`
- `Turn`
- `AuditEvent`
- `Workspace`
- `Membership`
- `VerifiedQuery`
- `EvaluationCase`

The exact Python/Pydantic definitions should be kept in the implementation contract document.

---

# 42. Testing

Minimum security tests:

- INSERT/UPDATE/DELETE rejected
- CREATE/DROP rejected
- ATTACH rejected
- PRAGMA rejected
- extension loading rejected
- hidden table rejected
- unknown table rejected
- unknown column rejected
- multiple statements rejected
- comment-based SQL bypass rejected
- metadata DB path rejected
- symlink escape rejected
- timeout enforced
- fetch cap enforced

Minimum correctness tests:

- date resolution
- result preservation
- display/export parity
- number verification
- role permissions
- last-Owner rule
- audit append-only behavior
- Streamlit rerun behavior
- cache invalidation after DB change
- NL→SQL evaluation cases

---

# 43. V1 Acceptance Criteria

V1 is complete only when all are true:

### Database

- User can select/provide an approved SQLite path.
- Shared-drive/local/OneDrive-synced paths work when accessible to Streamlit.
- Current database contents are used.
- Database is opened read-only.
- Unsafe paths are rejected.

### Natural language

- User can ask a normal-language question.
- System produces structured interpretation.
- Material ambiguity causes clarification.
- Relative dates are resolved by Python.
- SQL is generated and validated.

### Safety

- LLM cannot execute SQL.
- SQL validator rejects unsafe SQL.
- SQLite authorizer independently rejects unsafe actions.
- Only exposed tables are readable.
- No arbitrary code execution exists.

### Results

- Results come directly from SQLite.
- Results are represented by Polars.
- Displayed SQL equals executed SQL.
- Large results are capped.
- CSV is generated from actual results.
- Explanations cannot invent numbers.

### Transparency

- User sees interpretation.
- User sees tables/columns.
- User sees plan.
- User sees SQL.
- User sees assumptions.
- User sees execution information.
- User can inspect provenance.

### Governance

- Workspace membership works.
- Roles are enforced.
- Important actions are audited.
- Audit records cannot be edited/deleted by normal application code.

### Streamlit

- Reruns do not repeat expensive operations.
- Query state survives reruns.
- Cache invalidates when the target database changes.

### Testing

- Security and core correctness test suites pass.

---

# 44. V1 Delivery Order

## Phase 1 — Foundation

Build first:

1. Project structure.
2. Configuration.
3. Metadata SQLite store.
4. User identity.
5. Workspace and membership.
6. Path policy.
7. SQLite read-only connection.
8. Authorizer.
9. SQL validator.
10. Query executor.
11. Basic audit logging.
12. Streamlit turn state.
13. Basic LLM provider interface.

**Do not build a sophisticated chat experience before these controls work.**

## Phase 2 — Basic Analyst

Build:

1. Schema inspection.
2. Catalog.
3. Business context.
4. Business terms.
5. Query understanding.
6. Clarification.
7. Query plan.
8. SQL generation.
9. Result display.
10. CSV export.
11. Transparency panel.

## Phase 3 — Accuracy and Trust

Build:

1. Time resolution.
2. Profiles.
3. Facts payload.
4. Number verifier.
5. Feedback.
6. Query history.
7. Verified query library.
8. Evaluation set.

## Phase 4 — Analysis

Build:

1. Analysis mode.
2. Multiple queries.
3. Polars transformations.
4. Charts.
5. Execution tiers.
6. Confirmation flow.

## Phase 5 — Future

Possible later work:

- remote/API databases
- other database engines
- vector retrieval
- larger-scale analytics
- background jobs
- Excel/PDF export

---

# 45. Open Configuration Decisions

These are configuration decisions, not reasons to redesign the architecture:

- approved data-root paths
- company timezone
- identity source
- LLM provider/model
- default egress level
- query timeouts
- row/result caps
- execution-tier thresholds
- audit retention
- query-history retention

If a value is not yet decided, put it in configuration with a documented default. Do not invent business policy inside prompts or UI code.

---

# 46. Final Product Definition

The final V1 experience is:

```text
User:
"Analyze trading activity this year."

System:
"Do you mean number of trades, monetary volume, or both?"

User:
"Both."

System:
- understands the request
- resolves "this year" using Python
- chooses approved tables
- creates a query plan
- generates SQL
- validates SQL
- executes it read-only
- returns exact results
- calculates facts
- explains the result
- verifies every number

User sees:

ANSWER
+ EXACT RESULT
+ TABLES USED
+ QUERY PLAN
+ EXECUTED SQL
+ ASSUMPTIONS
+ EXECUTION INFO
+ PROVENANCE
```

The core philosophy is:

> **AI-assisted, but not AI-dependent.**

Every important guarantee is enforced by application code.
