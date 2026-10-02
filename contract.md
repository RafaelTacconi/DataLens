# contract.md — DataLens-v1

Status: DRAFT

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
| What it is for (the decision or work it supports, one or two sentences) |  |
| Who uses it (the people or systems that use it, in plain words) |  |
| Kind of project (application, command-line tool, library, service, batch job, other — say which) |  |
| How it runs (on demand, on a schedule, always on, imported by other code — and on what machine) |  |
| Scale (how many users, files, rows or requests — today and in twelve months) |  |
| Non-goals (what is explicitly NOT built) |  |

## Part 2 — What is at stake

*Drafted by the agent from Part 1 and shown once for correction — not an
interview. `not applicable — <why>` is a real answer.*

| Field | Answer |
|---|---|
| If it went wrong unnoticed (who is affected, and how long before they find out) |  |
| Does anything leave the organisation or move money (yes/no, and what) |  |
| How sensitive is the data (public / internal / confidential) |  |

*Confidential data means real samples are sanitised before they go into
`tests/fixtures/`.*

## Part 3 — Who owns it

| Field | Answer |
|---|---|
| Business owner (accountable for what it does) |  |
| Technical owner (builder) |  |
| Backup (can run and fix it when the owner is away) |  |
| Review date (YYYY-MM-DD — when someone re-reads this contract) |  |

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
| SDD-Natural-Language-SQLite-Data-Analyst-v1.md | c9e80dd5d5e6 | (filled in Phase B) | (filled in Phase B) |
| AI-Coding-Assistant-Implementation-Guide-v1.md | 76aa28f34211 | (filled in Phase B) | (filled in Phase B) |

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

## Part 6 — Requirements

*What the project must do, one row per requirement, in plain words a
colleague could check by hand. The checkpoint plan is minted from these rows
(B3) — every row becomes one or more checkpoints. When a document holds the
detail, the row names the section and stays short; it does not copy the
document. `On failure` says what the project does when this cannot be done
(stop, refuse with a message, fall back to …).*

| ID | Requirement | From | Accept (observable — a command, a test, or a thing a person can see) | On failure |
|---|---|---|---|---|

## Part 7 — Packages it needs to run

*Only what the project needs to RUN (installed from `requirements.txt`). Test
tools (`pytest`, `ruff`) are not rows here. A new package is a new row, agreed
with the builder BEFORE it is installed. Write `none — standard library only`
if there are none.*

| Library | Version | Why | What breaks without it |
|---|---|---|---|

## Part 8 — How it is checked

| Field | Answer |
|---|---|
| Test command | `python -m pytest -q` |
| Smoke command (proves it starts without doing real work; ends on its own — never a server; no pipes) |  |
| Primary output (what the artifact test builds and asserts on) |  |
| Real sample available? (a file name, or NONE — the fixture is then hand-built and flagged) |  |

*The smoke command is run by `scripts/verify_build.py` exactly as written, from
the project root, so it must work on a clean checkout with no credential and
no network. For a library: an import. For an application: a check mode or an
import of its entry module. `not applicable — <why>` if nothing can start.*

---

## Sign-off

| Role | Name | Date |
|---|---|---|
| Builder (technical owner) |  |  |

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
