# AGENTS.md — DataLens-v1

> **Read this before changing anything in this repository.**
> It exists so that ANY AI coding tool — not only the one that built this —
> learns the rules before it edits. Kept short on purpose: only what a tool
> could not work out by reading the code.

## What this is

A project built and governed by the roo framework's core
(`project-core v1.1`). The released artifact is this repository at a tag,
run from a clean checkout. The framework does not prescribe how a project is
deployed; the builder does that.

## The contract lives in a file, and it is not this one

- **`contract.md`** — what this project must do, who owns it, the documents it
  rests on, and how it is checked. It is signed. **It is the specification.**
- **`memory.md`** — the build log and the checkpoint plan: what is done, what
  is next, what was decided and why.
- **`version.md`** — what has been released.

**Read `contract.md` before proposing a change.** Code that disagrees with the
contract is a defect in one of them, and which one is a human decision.

## Rules that bind any agent working here

1. **No code before a signed contract, and no code before the artifact test.**
   The commit hook refuses both once it is installed — in a fresh clone run
   `git config core.hooksPath hooks` first (it is per-clone git config). Do not bypass it with `--no-verify` to get
   past either rule.
2. **Write the test first.** Each piece of work starts with a failing test
   for what the contract asks, then the smallest code that passes it.
3. **Do not put an absolute path or a secret in code.** Locations and keys
   come from configuration (`.env`, environment variables); `.env` is never
   committed.
4. **Do not weaken a test to make it pass.** A failing test is information.
5. **`data/` is git-ignored and may hold real business files.** Never commit
   its contents, never `git add -f` them.
6. **Commit as the builder, never as an invented identity.** The hook refuses
   names like `builder` and addresses like `builder@local`.
7. **If this project is released** (see `version.md`), a change is not a free
   edit: it goes through the framework's change cycle — scan, written change,
   approval, then a branch. Ask before starting one.

## Commands

```
python -m venv .venv                  # first time only
.venv\Scripts\activate                # Windows — ALWAYS first, every session
pip install -r requirements.txt
python -m pytest -q                   # all tests
python scripts/verify_build.py        # the go/no-go; read its output
```

The project's own start and smoke commands are in `contract.md`, Part 8.

## If you are an agent that did not build this

Say so, read `contract.md` and `memory.md` first, and ask before editing.
Several of the rules above are checked mechanically by
`scripts/verify_build.py` and by the commit hook; a change that breaks one
fails rather than passing quietly.
