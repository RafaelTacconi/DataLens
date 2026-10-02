# DataLens-v1

<!-- badges:start · written by verify_build.py --release · do not edit -->
<!-- badges:end -->

> **The one thing to know first:** <the single biggest limitation or caveat, in one plain sentence>

*Every `<placeholder>` in this file is replaced with real text before the
release, and this line is deleted. Write for someone who has never seen this
project.*

## What this does

<two or three plain sentences: what it is, who uses it, what they get from it>

## How it works

<five to ten numbered steps in plain words, from what a user does to what they get back>

## How to run it

**To start it:** <the command, or the address to open>

**To check it is healthy without changing anything:** <the smoke command from the contract, or why there is none>

**What it needs on the machine that runs it:** <the Python version, and every environment variable by NAME, never a value>

## When it goes wrong

| What you see | What it means | What to do |
|---|---|---|
| <a real message this project produces> | <its plain meaning> | <who to tell, or what to fix> |

## Who owns this

**Business owner:** <name>

**Technical owner:** <name>

**Credentials:** <which environment variables carry a key, and who renews them, or none>

## For a developer picking this up

Contract: `contract.md` · Build log: `memory.md` · Releases: `version.md`

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q
python scripts/verify_build.py
```

`data/`, `.env` and `.venv/` are git-ignored. The last command is the gate: it
must print GO before a release.

### Where things live

```
<the project's directory tree, fifteen lines or fewer, one short comment each>
contract.md     # what this must do, signed
tests/          # pytest; test_artifact.py proves the output is right
scripts/        # verify_build.py, the go/no-go
```
