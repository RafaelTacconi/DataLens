# DataLens-v1

<!-- badges:start · written by verify_build.py --release · do not edit -->
![python](https://img.shields.io/badge/python-3.12+-blue) ![gate](https://img.shields.io/badge/gate-GO-brightgreen) ![tests](https://img.shields.io/badge/tests-128_passed-brightgreen) ![framework](https://img.shields.io/badge/framework-project--core_v1.1-informational) ![released](https://img.shields.io/badge/released-v1.0.0_2026--10--03-blue) ![kind](https://img.shields.io/badge/kind-application_an-lightgrey)
<!-- badges:end -->

> **The one thing to know first:** the app never runs SQL the language model
> wrote until that SQL has been checked by the application's own safety rules,
> and it opens your database read-only — it cannot change your data.

## What this does

DataLens is a small web application that lets you ask questions about a
SQLite database in plain language. You point it at a database file, type a
question like "total trading volume by region this year", and it returns the
exact answer, the SQL it ran, and the reasoning behind it — so you can see
exactly where the number came from.

It is built for people who know their data but do not want to write SQL. It
is not a general chatbot: it only answers from the database you connect, and
it never makes up a number.

## How it works

1. You open the app in a browser and choose a SQLite database file.
2. You type a question in normal language.
3. The app asks a language model to interpret the question into a structured
   plan (what to count, group by, and over what time period).
4. If the question is genuinely ambiguous, the app asks you to choose rather
   than guessing.
5. The app drafts SQL from the plan, then checks it: it must be a single
   read-only query against tables you are allowed to see.
6. The checked SQL is run against your database in read-only mode.
7. The app shows the exact result table, the SQL that was run, the tables and
   columns used, and the assumptions it made.

## How to run it

**To start it:**

```
streamlit run app/main.py
```

Then open the address the terminal prints (usually http://localhost:8501).

**To check it is healthy without changing anything:**

```
python -c "import app.main"
```

**What it needs on the machine that runs it:** Python 3.12. The environment
variables it reads are `LLM_MODEL` (the model to call) and the `DATALENS_*`
settings (row caps, timeouts, retention). Put the API key in a `.env` file
next to the project — never in the code.

## When it goes wrong

| What you see | What it means | What to do |
|---|---|---|
| "path is not a SQLite database" | The file you chose is not a SQLite database. | Choose a real SQLite file. |
| "The query was too expensive" | The query took too long. | Narrow the question (add a filter or a shorter time period). |
| "not a member of this workspace" | You are not allowed to use that workspace. | Ask the workspace owner to add you. |
| The app says it cannot answer | The question is ambiguous or the data does not contain the answer. | Rephrase, or check the data. |

## Who owns this

**Business owner:** Rafael Tacconi

**Technical owner:** Rafael Tacconi

**Credentials:** the language-model API key lives in `.env` as the value for
`LLM_MODEL`'s provider; the builder renews it.

## For a developer picking this up

The signed contract is `contract.md`, the build log is `memory.md`, and
releases are in `version.md`.

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q
python scripts/verify_build.py
```

`data/`, `.env` and `.venv/` are git-ignored. The last command is the gate:
it must print GO before a release.

### Where things live

```
app/main.py        # the Streamlit entry point
app/core/          # the pipeline: orchestrator, state, permissions, tiers
app/db/            # read-only connections, the authorizer, the executor
app/sql/           # SQL validation and canonicalisation
app/llm/           # the language-model interface, prompts, egress policy
app/metadata/      # the app's own database: workspaces, history, audit
app/analysis/      # facts, number verification, charts
app/ui/            # the chat, transparency, workspace and history views
tests/             # pytest; test_artifact.py proves the output is right
scripts/           # verify_build.py, the go/no-go
contract.md        # what this must do, signed
