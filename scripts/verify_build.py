"""verify_build.py - the go/no-go gate of a project-core project.

Stamped into <project>/scripts/ at A1. Run from the project root:

    python scripts/verify_build.py              the go/no-go (DEV mode)
    python scripts/verify_build.py --release    the release gate (phase R)
    python scripts/verify_build.py --hook       the pre-commit checks
    python scripts/verify_build.py --hash FILE  the hash to write in the
                                                contract for a source document

WHY THIS GATE EXISTS (wave 43). The framework used to have two ways in: a
Power BI pipeline or a file automation. A real project that was neither - an
interactive application specified by a detailed design document - fitted no
door, so the agent built three thousand lines with no contract, no tests, no
memory.md and a made-up git identity, and nothing stopped it. The two
pillars' gates could not have helped: each is built around its own project
shape (`etl/`, `core/` + `run.py`). This gate checks only what EVERY project
owes, whatever its shape, so any project can carry the framework's practices.

Checks (each prints PASS/FAIL; exit 0 only if all PASS):
  1. STRUCTURE    the framework's own files exist
  2. GIT          a real identity (never a made-up one), the commit hook is
                  installed, and no data/ or .env file is tracked
  3. PLACEHOLDER  no __SENTINEL__ survives in a stamped file or in code
  4. CONTRACT     contract.md: CONFIRMED, signed, foundation fields answered,
                  every source document unchanged since it was signed, every
                  open decision answered, at least one requirement
  5. TESTS        pytest passes, and at least one test exists
  6. ARTIFACT     tests/test_artifact.py builds the primary output from a
                  realistic input and asserts on its CONTENT (strict rule 6)
  7. SMOKE        the contract's smoke command exits 0 (or is declined with
                  a reason)
  8. MARKERS      no scaffold residue in code or README
  9. ENCODING     no cp1252 round trip (house rule 1)
 10. README       written for a reader who has never heard of this framework
 11. NO ABSOLUTE PATHS  in source code (tests are exempt: a test may need to
                  prove a path is REJECTED)
 12. DEPENDENCIES requirements.txt, contract Part 7 and the imports agree
 13. EVIDENCE     every PASS row in memory.md cites a receipt; at --release
                  every cited receipt is committed
 14. RELEASE LINEAGE (--release)  version.md newest-first, earlier releases
                  contained in HEAD, no moved tag
 15. PUSHED and CLEAN (--release)  the release is cut from committed code
                  that is already on the remote

--hook runs what must hold at EVERY commit, and writes no receipt:
STRUCTURE, GIT identity of the commit being made, PLACEHOLDER, ENCODING, NO
ABSOLUTE PATHS, and the two ORDER rules that make the build discipline
mechanical instead of a promise:
  - no project code before the contract is signed (strict rule 1);
  - no project code before the artifact test is written (C0 comes first).

Every run prints the SHA-256 of this script, and every receipt records it,
so a pasted result says which gate produced it (register F-54).
"""

import ast
import datetime
import getpass
import hashlib
import json
import os
import pathlib
import re
import shlex
import socket
import subprocess
import sys
from datetime import date

CARD = "contract.md"
REQUIRED = [
    CARD, "memory.md", "version.md", "AGENTS.md", "README.md", ".gitignore",
    ".env.example", "requirements.txt", "tests", "scripts/verify_build.py",
    "hooks/pre-commit",
]
SENTINEL = re.compile(r"__[A-Z][A-Z0-9_]*__")
STAMPED_FILES = [CARD, "memory.md", "version.md", "README.md", "AGENTS.md",
                 "requirements.txt"]

# Folders that are never project source: tooling, data, output, history.
SKIP_DIRS = {".git", ".venv", "venv", "env", "__pycache__", "node_modules",
             "build", "dist", ".evidence", "data", "logs", "skills_output",
             "_workbench", ".pytest_cache", ".mypy_cache", ".ruff_cache",
             ".roo", ".vscode", ".idea"}
# Folders that hold the framework's own machinery, not the project's code.
FRAMEWORK_DIRS = {"scripts", "hooks"}

# Scaffold residue (wave 31): a template instruction that reaches a running
# application is an unfinished build, not a style question.
MARKERS = [
    "# PROJECT:", "# SKELETON-COPY:", "OPTION A", "OPTION B", "REPLACE ME",
]

# A drive letter or a UNC share. The lookbehind is deliberate (wave 43): the
# pillar gates' pattern has no lookbehind, so the "s:/" inside "https://"
# matches it and every URL in code fails as an "absolute path".
# "Q:\nA:" inside a string is a newline escape, not a drive: a backslash
# followed by n, t or r (and not a second backslash) is skipped. A real path
# in source is written "C:\\Data" or r"C:\Data\x" - both still match. The
# one miss: a raw string whose first folder starts with n, t or r
# (r"C:\new"); the release review and the builder's eye catch that one.
ABSOLUTE_PATH = re.compile(
    r"""(?:(?<![A-Za-z0-9])[A-Za-z]:(?:/|\\(?![ntr])|\\\\)|\\\\[A-Za-z0-9._-]+[\\/])""")
# Inside a RAW string (r"C:\temp\x.db") a backslash is a backslash, so the
# escape exception above does not apply there: raw strings are matched with
# this stricter pattern (found by the independent check's second pass - the
# exception had let r"C:\temp\data.db" through).
ABSOLUTE_PATH_RAW = re.compile(
    r"""(?:(?<![A-Za-z0-9])[A-Za-z]:[\\/]|\\\\[A-Za-z0-9._-]+[\\/])""")
# A line that genuinely needs an absolute path says so, with a reason.
ABS_PATH_OK = re.compile(r"#\s*abs-path-ok:\s*(\S.*)?$")

# The stamped artifact test carries this string until C0 replaces it.
ARTIFACT_NOT_WRITTEN = "ARTIFACT TEST NOT WRITTEN YET"

RESULTS = []
CHECK_NAMES = []
TEST_COUNT = None

# ---------------------------------------------------------------- README rules
README_JARGON = ("stamped template", "accept condition", "checkpoint",
                 "phase file", "scaffold skill")
CHECKPOINT_ID = re.compile(r"\b[A-G]\d[a-z]?\b")
BADGE_START = "<!-- badges:start"
BADGE_END = "<!-- badges:end -->"
BADGE_IMG = re.compile(r"!\[[^\]]*\]\([^)]*shields\.io[^)]*\)")
BADGE_ONLY_LINE = re.compile(
    r"^\s*(?:!\[[^\]]*\]\([^)]*shields\.io[^)]*\)\s*)+$")


def _readme_regions(lines):
    """(opening, badge) line-index sets for README.md."""
    h1 = first_h2 = None
    for n, line in enumerate(lines):
        if h1 is None and line.startswith("# "):
            h1 = n
        elif line.startswith("## "):
            first_h2 = n
            break
    opening = set(range((h1 or 0) + 1, first_h2)) if first_h2 else set()

    badge, inside = set(), False
    for n, line in enumerate(lines):
        if BADGE_START in line:
            inside = True
        if inside:
            badge.add(n)
        if BADGE_END in line:
            inside = False
    return opening, badge


# ---------------------------------------------------------------------------
# SHARED HELPERS. The checker's gate-parity rule names each of these and
# requires it in every gate (the two pillars' and this one), so a fix cannot
# land in one gate only.
# ---------------------------------------------------------------------------

def _gate_identity():
    """(full sha256, 12-char prefix) of THIS script (register F-54)."""
    try:
        digest = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
    except OSError:
        return None, "unknown"
    return digest, digest[:12]


def _code_text(path):
    """The file's text with comments and docstrings blanked (register F-19).

    Line numbers are preserved, so a finding still names the right line. Only
    Python files are touched; anything else comes back unchanged. If the file
    does not parse, the original text is returned, so a broken file is
    checked MORE strictly, never less.
    """
    import io
    import tokenize
    p = pathlib.Path(path)
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    if p.suffix != ".py":
        return text
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return text
    doc_starts = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            body = getattr(node, "body", None) or []
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                doc_starts.add(body[0].lineno)
    spans = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT or (
                    tok.type == tokenize.STRING and tok.start[0] in doc_starts):
                spans.append((tok.start, tok.end))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return text
    rows = [list(line) for line in text.splitlines(keepends=True)]
    for (r0, c0), (r1, c1) in spans:
        for r in range(r0, r1 + 1):
            if r - 1 >= len(rows):
                break
            row = rows[r - 1]
            lo = c0 if r == r0 else 0
            hi = c1 if r == r1 else len(row)
            for i in range(lo, min(hi, len(row))):
                if row[i] not in "\r\n":
                    row[i] = " "
    return "".join("".join(r) for r in rows)


def _placeholder_text(path):
    """What the placeholder check may read in `path` (register F-19).

    A .py file: code only. memory.md: only the stamped lines (the title and
    the "Framework version:" decision) - the rest is the agent's own log, and
    a log that records a false positive must not itself fail the gate.
    """
    p = pathlib.Path(path)
    if p.name == "memory.md":
        try:
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            return ""
        return "\n".join(line if (i == 0 or "Framework version:" in line)
                         else "" for i, line in enumerate(lines))
    return _code_text(p)


_VERSION_RE = re.compile(r"^v?(\d+)\.(\d+)(?:\.(\d+))?$")


def _vkey(value):
    """(major, minor, patch) for 'v1.2.3' / '1.2', or None."""
    m = _VERSION_RE.match((value or "").strip())
    return tuple(int(x or 0) for x in m.groups()) if m else None


def _version_rows(root):
    """Version cells of every version.md release row, in FILE order."""
    try:
        text = (pathlib.Path(root) / "version.md").read_text(
            encoding="utf-8", errors="replace")
    except OSError:
        return []
    rows = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if cells and _vkey(cells[0]) is not None:
            rows.append(cells[0])
    return rows


def _git(root, *args):
    """A completed git process, or None when git cannot run here."""
    try:
        return subprocess.run(["git", *args], cwd=str(root),
                              capture_output=True, text=True, timeout=60,
                              encoding="utf-8", errors="replace")
    except (OSError, subprocess.SubprocessError):
        return None


def _release_lineage_problems(root):
    """What is wrong with the release being cut, as a list (F-67, F-68).

    The release being cut is version.md's TOP row. Rows must be newest-first;
    every release with a LOWER version number must already be contained in
    HEAD; and a tag that already exists for this version must point at HEAD,
    because a pushed tag is never moved - a correction is a new patch version.
    """
    problems = []
    rows = _version_rows(root)
    if not rows:
        return ["version.md has no release row. The release being cut is "
                "its TOP row - add it before the release gate (phase R, R3)."]
    keys = [_vkey(v) for v in rows]
    if keys != sorted(keys, reverse=True):
        return [f"version.md rows are not newest-first ({', '.join(rows)}). "
                f"The top row is read as THE version - by the release badge "
                f"and by phase R's Accept - so an oldest-first file makes "
                f"every later release report itself as {rows[0]}. Put the "
                f"newest release on top."]
    if len(set(keys)) != len(keys):
        problems.append("version.md lists the same version twice - one row "
                        "per release, and a release is never re-cut.")
    releasing, rkey = rows[0], keys[0]
    listed = _git(root, "tag", "--list")
    head = _git(root, "rev-parse", "HEAD")
    if (listed is None or listed.returncode != 0
            or head is None or head.returncode != 0):
        problems.append(
            "git could not be read here, so the release lineage cannot be "
            "checked. A release is cut from the project's repository - run "
            "the gate inside it.")
        return problems
    head = head.stdout.strip()
    for tag in (t.strip() for t in listed.stdout.splitlines()):
        tkey = _vkey(tag)
        if tkey is None:
            continue
        if tkey == rkey:
            at = _git(root, "rev-parse", f"{tag}^{{commit}}")
            at = at.stdout.strip() if at and at.returncode == 0 else ""
            if at and at != head:
                problems.append(
                    f"tag {tag} already exists at {at[:7]} and HEAD is "
                    f"{head[:7]}. A pushed tag is never moved: anyone who "
                    f"fetched it keeps the old commit, and the two copies of "
                    f"'{tag}' silently differ. Cut a new patch version.")
        elif tkey < rkey:
            anc = _git(root, "merge-base", "--is-ancestor", tag, "HEAD")
            if anc is not None and anc.returncode == 1:
                problems.append(
                    f"HEAD does not contain {tag}. Releasing {releasing} from "
                    f"here would drop what {tag} shipped. Merge first, then "
                    f"tag (phase M, M4).")
    return problems


def _untracked(root, relpath):
    """True if `relpath` exists but git does not track it; None if unknown."""
    r = _git(root, "ls-files", "--error-unmatch", str(relpath))
    if r is None:
        return None
    return r.returncode != 0


def check(name, fn):
    """Run one check, print PASS/FAIL, and record the result by name."""
    CHECK_NAMES.append(name)
    try:
        fn()
        print(f"  PASS  {name}")
        RESULTS.append(True)
    except Exception as err:
        print(f"  FAIL  {name}: {err}")
        RESULTS.append(False)


# ------------------------------------------------------------ project files

def _walk_py(include_framework=False):
    """Every .py file of the project, as relative POSIX paths, sorted."""
    found = []
    for dirpath, dirnames, filenames in os.walk("."):
        rel = pathlib.Path(dirpath)
        dirnames[:] = sorted(
            d for d in dirnames
            if d not in SKIP_DIRS and not d.startswith(".")
            and not (rel == pathlib.Path(".") and not include_framework
                     and d in FRAMEWORK_DIRS))
        for fn in sorted(filenames):
            if fn.endswith(".py"):
                found.append((rel / fn).as_posix())
    return found


def _is_test_file(relpath):
    """True for a test module or anything under a tests/ folder."""
    p = pathlib.PurePosixPath(relpath)
    return ("tests" in p.parts or p.name.startswith("test_")
            or p.name.endswith("_test.py") or p.name == "conftest.py")


def _source_files():
    """Project code: every .py file that is not a test and not tooling."""
    return [f for f in _walk_py() if not _is_test_file(f)]


# ---------------------------------------------------------- contract helpers

# The order rules (no code before the contract, none before the artifact
# test) count EVERY code file, not only Python under the obvious folders: an
# independent check committed code before a signed contract from scripts/,
# hooks/, a dot-folder, tests/, a root conftest.py, .ipynb, .sql and .js
# files, and the hook let every one through.
CODE_SUFFIXES = {".py", ".pyw", ".ipynb", ".js", ".mjs", ".cjs", ".ts",
                 ".tsx", ".jsx", ".sql", ".ps1", ".psm1", ".bat", ".cmd",
                 ".sh", ".r", ".java", ".cs", ".go", ".rb"}
# Never project code: version control, caches, real data, receipts, output.
ORDER_SKIP_DIRS = {".git", "__pycache__", "node_modules", ".pytest_cache",
                   ".mypy_cache", ".ruff_cache", ".evidence", "data",
                   "skills_output", "_workbench", ".roo", ".vscode", ".idea",
                   "build", "dist", "logs"}
# The framework's own files - stamped at A1, never the project's code.
FRAMEWORK_FILES = {"scripts/verify_build.py", "tests/__init__.py"}


def _source_documents():
    """Paths the contract's Part 4 lists as the builder's own material."""
    try:
        part4 = _section(_card_text(), "Part 4")
    except OSError:
        return set()
    names = set()
    for cells in _table_rows(part4):
        first = _strip_ticks(cells[0]) if cells else ""
        if first and not first.lower().startswith(("none", "file")):
            rel = first.replace("\\", "/")
            names.add(rel[2:] if rel.startswith("./") else rel)
    return names


def _code_files(include_tests=True):
    """Every code file a person or agent wrote, as relative POSIX paths.

    A folder holding `pyvenv.cfg` is a virtual environment, whatever its
    name, and is skipped; so are the folders above. The stamped artifact
    test counts only once it is no longer the placeholder. Material the
    builder BROUGHT - a schema, a helper script, an old report - is listed in
    contract Part 4 at A1 and is not code written before the contract
    (independent check, second pass: a `docs/sample_schema.sql` beside the
    design documents blocked the A1 commit).
    """
    brought = _source_documents()
    found = []
    for dirpath, dirnames, filenames in os.walk("."):
        dirnames[:] = sorted(
            d for d in dirnames
            if d not in ORDER_SKIP_DIRS
            and not os.path.isfile(os.path.join(dirpath, d, "pyvenv.cfg")))
        for fn in sorted(filenames):
            rel = (pathlib.Path(dirpath) / fn).as_posix()
            rel = rel[2:] if rel.startswith("./") else rel
            if pathlib.PurePosixPath(fn).suffix.lower() not in CODE_SUFFIXES:
                continue
            if rel in FRAMEWORK_FILES or rel in brought:
                continue
            if rel == "tests/test_artifact.py":
                try:
                    body = pathlib.Path(rel).read_text(encoding="utf-8",
                                                       errors="replace")
                except OSError:
                    continue
                if ARTIFACT_NOT_WRITTEN in body:
                    continue
            if not include_tests and _is_test_file(rel):
                continue
            found.append(rel)
    return found


def _card_text():
    with open(CARD, "r", encoding="utf-8") as fh:
        return fh.read()


def _field(text, label):
    """Value of a 2-column row: | <label...> | value |  (prefix match)."""
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 2 and cells[0].startswith(label):
            return cells[1]
    return None


def _section(text, heading):
    """The body of the '## <heading>...' section, or None if absent."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("## ") and line[3:].strip().startswith(heading):
            body = []
            for nxt in lines[i + 1:]:
                if nxt.startswith("## "):
                    break
                body.append(nxt)
            return "\n".join(body)
    return None


def _table_rows(body):
    """Data rows of the first markdown table in `body`, as lists of cells."""
    rows, header_seen = [], False
    for line in (body or "").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if header_seen and rows:
                break
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not header_seen:
            header_seen = True
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        if not any(cells):
            continue
        rows.append(cells)
    return rows


_PLACEHOLDER_RE = re.compile(
    r"""^(
          <.*>                      # <name>, <who>, <YYYY-MM-DD>
        | \[.*\]                    # [name]
        | \{.*\}                    # {name}
        | __.*__                    # __SENTINEL__
        | tbd | tba | t\.b\.d\.?
        | n/?a | none | null | nil
        | \?+ | -+ | \.+ | _+
        | xxx+ | todo | pending | unknown
        | fill\s*(this\s*)?in
      )$""",
    re.IGNORECASE | re.VERBOSE,
)


def _is_placeholder(value):
    """True when a field is technically non-empty but says nothing."""
    return bool(value) and bool(_PLACEHOLDER_RE.match(value.strip()))


NOT_SURE = "not sure yet"
NOT_APPLICABLE = "not applicable"


def _declined(value):
    """(is_declined, reason) for a 'not applicable - <why>' answer."""
    stripped = value.strip().lower()
    if not stripped.startswith(NOT_APPLICABLE):
        return False, ""
    return True, value.strip()[len(NOT_APPLICABLE):].lstrip(": -\u2014").strip()


FOUNDATION_FIELDS = (
    "What it is for", "Who uses it", "Kind of project", "How it runs",
    "Scale", "Non-goals",
)
DECLINABLE_FIELDS = (
    "If it went wrong unnoticed", "Does anything leave", "How sensitive",
    "Business owner (accountable", "Technical owner (builder",
    "Backup (can run", "Review date",
)


def _open_questions():
    """The text of memory.md's '## Open questions' section, lower-cased."""
    try:
        body = pathlib.Path("memory.md").read_text(
            encoding="utf-8", errors="replace")
    except OSError:
        return ""
    lower = body.lower()
    start = lower.find("## open questions")
    if start == -1:
        return ""
    end = lower.find("\n## ", start + 1)
    return lower[start:end if end != -1 else len(lower)]


def _signoff(text, label):
    """(name, date) of a 3-column sign-off row (prefix match on role)."""
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[0].startswith(label):
            return cells[1], cells[2]
    return None, None


def _parse_date(value):
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", value or "")
    if not m:
        raise AssertionError(f"date not YYYY-MM-DD: {value!r}")
    return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))


def _strip_ticks(value):
    return (value or "").strip().strip("`").strip()


def document_hash(path):
    """The 12-character hash a contract records for a source document.

    CRLF is normalised to LF first, the same rule as contract_hash(): git on
    Windows may check a file out with different line endings, and a document
    is not "changed" because a checkout re-wrote its line endings.
    """
    data = pathlib.Path(path).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()[:12]


# ------------------------------------------------------------- git identity

_PLACEHOLDER_NAMES = {
    "builder", "the builder", "user", "username", "name", "your name",
    "admin", "administrator", "root", "agent", "ai", "assistant", "bot",
    "developer", "dev", "test", "tester", "unknown", "nobody", "me",
    "someone", "default", "author",
    # An AI tool or model is not a person (the independent check committed
    # as "Roo Code" and as "Claude" and both passed).
    "roo", "roo code", "zoo code", "kilo", "kilo code", "cline", "claude",
    "claude code", "deepseek", "copilot", "github copilot", "cursor", "gpt",
    "chatgpt", "openai", "codex", "gemini", "llm", "ai agent",
    "coding agent", "ai assistant",
}
_PLACEHOLDER_DOMAINS = {
    "local", "localhost", "localdomain", "example.com", "example.org",
    "example.net", "invalid", "test", "none", "(none)",
    # AI vendors' addresses: an agent's own git identity, never the builder's.
    "anthropic.com", "openai.com", "deepseek.com", "roocode.com",
    "kilocode.ai",
}


def _identity_problem(name, email):
    """Why a git identity is not a real person's, or None if it looks real.

    WAVE 43. A real build committed as `builder <builder@local>` with
    `git -c user.name=... -c user.email=...` on the command line - an
    identity typed by the agent, attributed to nobody. Every commit of a
    project carries its author forever; an invented one is a small
    fabrication repeated in every line of the history.
    """
    name = (name or "").strip()
    email = (email or "").strip().strip("<>")
    if not name or name.lower() in _PLACEHOLDER_NAMES or _is_placeholder(name):
        return f"name {name!r} is not a person's name"
    if {w.strip(".,()[]").lower() for w in name.split()} & {"bot", "llm",
                                                             "assistant"}:
        return f"name {name!r} names a program, not a person"
    if "@" not in email:
        return f"email {email!r} is not an email address"
    domain = email.rsplit("@", 1)[1].lower()
    if (domain in _PLACEHOLDER_DOMAINS or "(none)" in domain
            or domain.endswith((".local", ".localdomain", ".invalid",
                                ".example", ".test"))):
        return f"email {email!r} uses a placeholder domain"
    if "." not in domain:
        return (f"email {email!r} has no real domain - this is what git "
                f"invents from the machine name when nobody configured it")
    return None


def _ident_from_var(var):
    """(name, email) from `git var GIT_AUTHOR_IDENT`-style output, or None."""
    r = _git(".", "var", var)
    if r is None or r.returncode != 0:
        return None
    m = re.match(r"^(.*?)\s*<([^>]*)>", r.stdout.strip())
    return (m.group(1), m.group(2)) if m else None


# ---------------------------------------------------------------- the checks

def structure():
    """The framework's own files exist."""
    missing = [p for p in REQUIRED if not os.path.exists(p)]
    if missing:
        raise AssertionError(
            f"missing: {missing} - these are stamped at phase A (A1) and "
            f"every later check reads them.")


def gitignore_guards():
    """data/, .env and .evidence/ stay out of git (house rules 11 and 19b)."""
    try:
        lines = {line.strip() for line in pathlib.Path(".gitignore").read_text(
            encoding="utf-8", errors="replace").splitlines()}
    except OSError:
        raise AssertionError(".gitignore missing")
    wanted = {"data/": "real business files", ".env": "the real secrets",
              ".evidence/": "uncited receipts"}
    missing = [f"{p} ({why})" for p, why in wanted.items() if p not in lines]
    if missing:
        raise AssertionError(
            f".gitignore no longer ignores {missing}. Restore the line(s) "
            f"from the template - each one keeps something out of git that "
            f"must never be in it.")
    tracked = _git(".", "ls-files", "--", "data", ".env")
    if tracked is not None and tracked.returncode == 0 and tracked.stdout.strip():
        raise AssertionError(
            f"git tracks {tracked.stdout.split()[:5]} - real data or a "
            f"secret is committed. Remove it from the index "
            f"(git rm --cached <file>) and, if it was a key, rotate it: a "
            f"committed key has leaked.")


def git_identity(hook=False):
    """The commit being made, and every commit so far, names a real person.

    In --hook mode only the identity of the commit about to be made is read
    (`git var` sees `git -c user.name=...` overrides too, so typing a
    made-up identity on the command line is caught at the commit itself).
    """
    problems = []
    for var in ("GIT_AUTHOR_IDENT", "GIT_COMMITTER_IDENT"):
        ident = _ident_from_var(var)
        if ident is None:
            problems.append(
                "git has no identity configured. Set it once - "
                "git config user.name \"<your name>\" and "
                "git config user.email \"<your email>\" - using the "
                "builder's real name and email. Never invent one.")
            break
        why = _identity_problem(*ident)
        if why:
            problems.append(
                f"the commit would be recorded as {ident[0]} <{ident[1]}>: "
                f"{why}. Ask the builder for their real name and email and "
                f"set them with git config. Never type an identity with "
                f"`git -c user.name=...`.")
            break
    if not hook:
        log = _git(".", "log", "--format=%an%x09%ae%x09%cn%x09%ce%x09%h")
        if log is not None and log.returncode == 0:
            bad = []
            for line in log.stdout.splitlines():
                parts = line.split("\t")
                if len(parts) != 5:
                    continue
                an, ae, cn, ce, sha = parts
                why = _identity_problem(an, ae) or _identity_problem(cn, ce)
                if why:
                    bad.append(f"{sha} ({why})")
            if bad:
                problems.append(
                    f"{len(bad)} commit(s) in the history carry an identity "
                    f"that is not a real person's: {bad[:4]}. The history "
                    f"has to be corrected by the builder - ask before "
                    f"rewriting anything that is already pushed.")
        hooks = _git(".", "config", "core.hooksPath")
        value = hooks.stdout.strip() if hooks and hooks.returncode == 0 else ""
        if value.rstrip("/\\") != "hooks":
            problems.append(
                "the commit hook is not installed (git config core.hooksPath "
                "is not 'hooks'). Run: git config core.hooksPath hooks. "
                "Without it the rules below are checked only when somebody "
                "remembers to run the gate.")
        problems.extend(_hook_runnable_problems())
    if problems:
        raise AssertionError("; ".join(problems))


def _hook_runnable_problems():
    """Reasons the installed hook would be skipped by git, as a list.

    WAVE 43, found by the planted-defect suite. Git on Linux and macOS
    IGNORES a hook file that is not executable - it prints a one-line hint
    and commits anyway - so a hook copied without its mode bit enforces
    nothing while looking installed. Git for Windows runs any hook that
    starts with "#!", so the working-tree bit is checked only off Windows;
    the committed mode is checked everywhere, because it decides whether a
    clone on another machine gets a working hook.
    """
    problems = []
    hook = pathlib.Path("hooks") / "pre-commit"
    if not hook.is_file():
        return problems
    if os.name != "nt" and not os.access(hook, os.X_OK):
        problems.append(
            "hooks/pre-commit is not executable, so git skips it without "
            "an error. Run: chmod +x hooks/pre-commit")
    staged = _git(".", "ls-files", "-s", "--", "hooks/pre-commit")
    mode = (staged.stdout.split() or [""])[0] if (
        staged and staged.returncode == 0) else ""
    if mode and mode != "100755":
        problems.append(
            f"git records hooks/pre-commit with mode {mode}, so a clone on "
            f"Linux or macOS gets a hook git will skip. Run: git "
            f"update-index --chmod=+x hooks/pre-commit, then commit.")
    return problems


def placeholders():
    """No __SENTINEL__ survives in a stamped file or in project code."""
    survivors = []
    paths = STAMPED_FILES + _walk_py()
    for path in paths:
        if not os.path.exists(path):
            continue
        for hit in SENTINEL.findall(_placeholder_text(path)):
            if hit not in ("__init__", "__name__", "__main__", "__file__"):
                survivors.append(f"{path}:{hit}")
    if survivors:
        raise AssertionError(f"unstamped sentinels: {survivors[:8]}")


def code_needs_signed_contract():
    """Strict rule 1 at commit time: no project code before the signature.

    WAVE 43. The rule "no code ships without a signed spec" was an
    instruction, and a real build wrote three thousand lines before any spec
    existed. At commit time it is a fact the machine can read: project code
    exists, and the contract does not say CONFIRMED. Writing the contract is
    phase B; nothing in phase B creates a code file.
    """
    source = _code_files(include_tests=True)
    if not source:
        return
    try:
        text = _card_text()
    except OSError:
        raise AssertionError(f"{CARD} is missing and project code exists")
    status = re.search(r"^Status:\s*(\S+)", text, re.MULTILINE)
    signed = _signature_problem(text)
    if status and status.group(1) == "CONFIRMED" and signed:
        raise AssertionError(
            f"project code exists ({source[:3]}) and {CARD} says CONFIRMED, "
            f"but {signed}. CONFIRMED is written at the B4 seal, after the "
            f"builder signs in their own message - a status line alone is "
            f"not a signature.")
    if not status or status.group(1) != "CONFIRMED":
        raise AssertionError(
            f"project code exists ({source[:3]}) but {CARD} is not CONFIRMED "
            f"(Status: {status.group(1) if status else 'missing'}). No code "
            f"before a signed contract - strict rule 1. Finish phase B "
            f"(contract, sign-off, plan) first. If the contract was "
            f"re-opened for a correction, re-sign it before more code.")


def _signature_problem(text):
    """Why the Builder sign-off row is not a signature, or None."""
    name_b, date_b = _signoff(text, "Builder (technical owner)")
    if not name_b or not date_b:
        return "the Builder sign-off row has no name and date"
    if _is_placeholder(name_b) or name_b.lower() in _PLACEHOLDER_NAMES:
        return f"the Builder sign-off name {name_b!r} is a placeholder"
    try:
        _parse_date(date_b)
    except AssertionError as err:
        return f"the Builder sign-off {err}"
    return None


def _artifact_written_problem(body):
    """Why tests/test_artifact.py is not yet a real artifact test, or None.

    Checked by the hook before any project code (C0 first) and by the
    ARTIFACT checks. A real test has a test function holding an assertion
    that reads something computed (a name, an attribute, a call) - never
    only constants, so `assert True` and `assert 1 == 1` do not count - and
    imports something to test: a module that is not the standard library and
    not a test tool. Importing the project INSIDE the test functions is fine
    and recommended: the rest of the suite still runs while it is red.
    """
    if ARTIFACT_NOT_WRITTEN in body:
        return "it is still the stamped placeholder"
    try:
        tree = ast.parse(body)
    except SyntaxError as err:
        return f"it does not parse: {err}"

    def _reads_something(expr):
        return any(isinstance(n, (ast.Name, ast.Attribute, ast.Call,
                                  ast.Subscript))
                   for n in ast.walk(expr))

    def _asserts(fn):
        for node in ast.walk(fn):
            if isinstance(node, ast.Assert) and _reads_something(node.test):
                return True
            if isinstance(node, ast.Call):
                name = getattr(node.func, "attr", None) or getattr(
                    node.func, "id", "")
                if (str(name).lower().startswith("assert")
                        and any(_reads_something(a) for a in node.args)):
                    return True
        return False

    tests_found = [n for n in ast.walk(tree)
                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                   and n.name.startswith("test")]
    if not tests_found:
        return "it defines no test function"
    if not any(_asserts(t) for t in tests_found):
        return ("no test function asserts on anything computed - an assert "
                "over constants only (`assert True`, `assert 1 == 1`), or a "
                "body of `pass`, proves nothing about the output")
    stdlib = set(getattr(sys, "stdlib_module_names", ()))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            imports.add(node.module.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.level > 0:
            imports.add(".")
    imports -= {"pytest", "__future__", "tests"} | _TEST_TOOLS
    if stdlib:
        imports -= stdlib
    if not imports and not _runs_a_program(tree):
        return ("it imports nothing to test and runs no program - the "
                "artifact test drives the project's own entry point, by "
                "importing it or by running it (subprocess, Streamlit's "
                "AppTest)")
    return None


def _runs_a_program(tree):
    """True when a test runs the project as a program instead of importing
    it: `subprocess.run([...])` and friends, or Streamlit's
    `AppTest.from_file(...)`. A command-line tool's most whole-path test runs
    it exactly the way a user does (independent check, second pass)."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func,
                                                            ast.Attribute):
            continue
        owner = node.func.value
        owner_name = getattr(owner, "id", None) or getattr(owner, "attr", "")
        if owner_name == "subprocess" and node.func.attr in (
                "run", "Popen", "check_output", "check_call", "call"):
            return True
        if owner_name == "AppTest" and node.func.attr.startswith("from_"):
            return True
    return False


def code_needs_artifact_test():
    """C0 comes first: no project code before the artifact test exists.

    The artifact test is the build's target. Written after the code, it is
    an exam the same session sets itself from the same understanding; written
    first, every checkpoint has something real to fail against.
    """
    source = _code_files(include_tests=False)
    if not source:
        return
    path = pathlib.Path("tests") / "test_artifact.py"
    try:
        body = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        raise AssertionError(
            f"project code exists ({source[:3]}) and tests/test_artifact.py "
            f"is missing. Restore it from the template and write it first "
            f"(phase C, C0).")
    why = _artifact_written_problem(body)
    if why:
        raise AssertionError(
            f"project code exists ({source[:3]}) but tests/test_artifact.py "
            f"is not a real artifact test yet: {why}. Write it FIRST (phase "
            f"C, C0): it is the target the rest of the build aims at, not a "
            f"final exam.")


def contract():
    """contract.md is CONFIRMED, signed, complete, and still matches its sources."""
    text = _card_text()
    problems = []

    status = re.search(r"^Status:\s*(\S+)", text, re.MULTILINE)
    if not status or status.group(1) != "CONFIRMED":
        problems.append(
            f"Status is {status.group(1) if status else 'missing'}, must be "
            f"CONFIRMED")

    questions = _open_questions()
    for label in FOUNDATION_FIELDS:
        value = _field(text, label)
        if value is None:
            problems.append(f"Part 1 has no '{label}' row - restore it from "
                            f"the template")
        elif not value:
            problems.append(
                f"Part 1 blank: {label}. A blank cell is an UNASKED question. "
                f"If the answer is not known yet, write 'not sure yet' and "
                f"open a matching row under '## Open questions' in memory.md.")
        elif _is_placeholder(value):
            problems.append(f"Part 1 {label} is a placeholder, not an "
                            f"answer: {value!r}")
        elif value.strip().lower().startswith(NOT_SURE):
            if label.lower() not in questions:
                problems.append(
                    f"Part 1 {label} says 'not sure yet', which is allowed - "
                    f"but memory.md's '## Open questions' has no row "
                    f"mentioning '{label}'. Add the row.")

    for label in DECLINABLE_FIELDS:
        value = _field(text, label)
        if value is None:
            problems.append(f"no '{label}' row - restore it from the template")
            continue
        if not value:
            problems.append(f"blank: {label}")
            continue
        declined, reason = _declined(value)
        if declined:
            if not reason:
                problems.append(
                    f"{label} says 'not applicable' with no reason. Say why in "
                    f"the same cell - for example 'not applicable - solo "
                    f"builder, no second person to name'.")
            continue
        if _is_placeholder(value):
            problems.append(
                f"{label} is a placeholder, not an answer: {value!r}. If it "
                f"genuinely does not apply, write 'not applicable - <why>'.")
        elif label == "Review date":
            try:
                if _parse_date(value) < date.today():
                    problems.append(f"Review date in the past: {value}")
            except AssertionError as err:
                problems.append(f"Review date: {err}")

    # Part 4 - the documents the builder brought are PART of the contract.
    docs = _section(text, "Part 4")
    if docs is None:
        problems.append("no '## Part 4' (source documents) section")
    else:
        for cells in _table_rows(docs):
            if len(cells) < 2:
                continue
            name, recorded = _strip_ticks(cells[0]), _strip_ticks(cells[1])
            if not name or _is_placeholder(name):
                continue
            if name.lower().startswith("none"):
                continue
            if not os.path.isfile(name):
                problems.append(
                    f"Part 4 lists {name!r}, which is not in the project. A "
                    f"document the contract rests on travels with it.")
                continue
            if _untracked(".", name):
                problems.append(
                    f"Part 4 lists {name!r}, which is not committed - a "
                    f"clean checkout would not have it. git add it.")
            actual = document_hash(name)
            if not re.fullmatch(r"[0-9a-f]{12}", recorded):
                problems.append(
                    f"Part 4 records {recorded!r} as the hash of {name!r}. "
                    f"Write its real hash: python scripts/verify_build.py "
                    f"--hash {name}")
            elif recorded != actual:
                problems.append(
                    f"{name!r} changed after the contract recorded it (hash "
                    f"{recorded} in the contract, {actual} on disk). A "
                    f"signed contract cannot rest on a document that moved: "
                    f"re-read the change, update the contract, record the new "
                    f"hash and re-sign.")

    # Part 5 - every decision the documents left open has an answer.
    decisions = _section(text, "Part 5")
    if decisions is None:
        problems.append("no '## Part 5' (open decisions) section")
    else:
        for cells in _table_rows(decisions):
            if len(cells) < 2 or not cells[0] or _is_placeholder(cells[0]):
                continue
            topic, answer = cells[0], cells[1]
            declined, reason = _declined(answer)
            if not answer or (_is_placeholder(answer) and not declined):
                problems.append(f"Part 5 decision {topic!r} has no answer")
            elif declined and not reason:
                problems.append(f"Part 5 decision {topic!r} says 'not "
                                f"applicable' with no reason")
            elif answer.strip().lower().startswith(NOT_SURE):
                key = re.sub(r"\W+", " ", topic.split("(")[0].lower()).strip()
                if key not in re.sub(r"\W+", " ", questions):
                    problems.append(
                        f"Part 5 decision {topic!r} is 'not sure yet' but "
                        f"memory.md's '## Open questions' has no row naming "
                        f"it. Add the row.")

    # Part 6 - at least one requirement, each with an observable Accept.
    reqs = _section(text, "Part 6")
    if reqs is None:
        problems.append("no '## Part 6' (requirements) section")
    else:
        real = [c for c in _table_rows(reqs)
                if len(c) >= 4 and c[0] and not _is_placeholder(c[0])]
        if not real:
            problems.append(
                "Part 6 has no requirement rows. The checkpoint plan is "
                "minted from Part 6; with no rows there is nothing to build "
                "against.")
        for cells in real:
            if not cells[1] or _is_placeholder(cells[1]):
                problems.append(f"requirement {cells[0]} says nothing")
            if not cells[3] or _is_placeholder(cells[3]):
                problems.append(
                    f"requirement {cells[0]} has no Accept test - a "
                    f"requirement nobody can check is a wish")

    smoke = _field(text, "Smoke command")
    if smoke is None:
        problems.append("Part 8 has no 'Smoke command' row")
    elif not smoke or (_is_placeholder(smoke)
                       and not _declined(smoke)[0]):
        problems.append(
            "Part 8 Smoke command is blank. Name the one command that proves "
            "the project starts without doing real work, or write "
            "'not applicable - <why>'.")
    elif _declined(smoke)[0] and not _declined(smoke)[1]:
        problems.append("Part 8 Smoke command says 'not applicable' with no "
                        "reason. Say why in the same cell.")

    name_b, date_b = _signoff(text, "Builder (technical owner)")
    if not name_b or not date_b:
        problems.append("Builder sign-off incomplete (name AND date required)")
    elif _is_placeholder(name_b) or name_b.lower() in _PLACEHOLDER_NAMES:
        problems.append(f"Builder sign-off name is a placeholder: {name_b!r}. "
                        f"A signature is a real person's name.")
    else:
        try:
            _parse_date(date_b)
        except AssertionError as err:
            problems.append(f"Builder sign-off {err}")

    if problems:
        raise AssertionError("; ".join(problems))


def tests():
    """Every test except the artifact test passes; at least one is collected.

    The artifact test is written FIRST (C0) and stays red until the
    checkpoints it drives exist, so it has its own line (ARTIFACT). Run in
    one pytest call, a red artifact test - or one whose import fails at
    collection - made every checkpoint's suite fail, and no checkpoint could
    ever show green (found by the independent check).
    """
    global TEST_COUNT
    r = subprocess.run([sys.executable, "-m", "pytest", "-q",
                        "--ignore=" + os.path.join("tests", "test_artifact.py")],
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode == 5:
        raise AssertionError(
            "pytest collected no tests besides the artifact test. Every "
            "checkpoint writes its own test first (phase C), so from C1 on "
            "this line is green.")
    if r.returncode != 0:
        raise AssertionError(
            f"pytest exit {r.returncode}\n{(r.stdout + r.stderr)[-800:]}")
    m = re.search(r"(\d+) passed", r.stdout)
    TEST_COUNT = int(m.group(1)) if m else None


def artifact_written():
    """C0's claim: tests/test_artifact.py is a real artifact test (it may
    still be red - the code it drives is built in the checkpoints after it).
    """
    path = os.path.join("tests", "test_artifact.py")
    if not os.path.exists(path):
        raise AssertionError(
            "tests/test_artifact.py missing - strict rule 6 (house rule 18). "
            "One end-to-end test must build the primary output from a "
            "realistic input and assert on its CONTENT. See phase C, C0.")
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        body = fh.read()
    why = _artifact_written_problem(body)
    if why:
        raise AssertionError(f"tests/test_artifact.py: {why}. See phase C, C0.")


def artifact():
    """Strict rule 6: the artifact test drives the project and passes."""
    artifact_written()
    path = os.path.join("tests", "test_artifact.py")
    body = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    # The project's own names: every folder and module under its source
    # files, so `src/datalens/...` (import datalens) and `app/core/...` with
    # app/ on the path (import core) both count - not only the first folder.
    local = set()
    for f in _source_files():
        parts = pathlib.PurePosixPath(f)
        local.add(parts.stem)
        local.update(parts.parts[:-1])
    tree = ast.parse(body)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            imported.add(node.module.split(".")[0])
    if local and not (imported & local) and not _runs_a_program(tree):
        raise AssertionError(
            f"tests/test_artifact.py imports none of the project's own code "
            f"({sorted(local)[:5]}) - it must build the output through the "
            f"project's real entry point, not re-implement it.")
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", path],
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise AssertionError(
            f"artifact test failed:\n{(r.stdout + r.stderr)[-1500:]}")


def smoke():
    """The contract's smoke command runs and exits 0."""
    value = _field(_card_text(), "Smoke command")
    declined, reason = _declined(value or "")
    if declined:
        if not reason:
            raise AssertionError("Smoke command says 'not applicable' with "
                                 "no reason")
        return
    command = _strip_ticks(value)
    if not command or _is_placeholder(command):
        raise AssertionError("contract Part 8 names no smoke command")
    try:
        argv = shlex.split(command, posix=not (os.name == "nt"
                                               and "\\" in command))
    except ValueError as err:
        raise AssertionError(f"smoke command does not parse: {err}")
    if argv and argv[0].lower() in ("python", "python3", "py", "python.exe"):
        argv[0] = sys.executable          # the project's own interpreter
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=120,
                           encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"`{command}` did not finish in 120 seconds. A smoke command must "
            f"end on its own - starting a server or a screen (`streamlit "
            f"run`) is not a smoke command. Import the entry module instead, "
            f"or give it a check flag that exits.")
    except (OSError, subprocess.SubprocessError) as err:
        raise AssertionError(f"smoke command could not run: {err}")
    if r.returncode != 0:
        raise AssertionError(
            f"`{command}` exit {r.returncode}\n"
            f"{(r.stdout + r.stderr)[-800:]}")


def markers():
    """No scaffold marker survives in project code or the README."""
    survivors = []
    for path in _walk_py() + ["README.md"]:
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for n, line in enumerate(fh, 1):
                for m in MARKERS:
                    if m in line:
                        survivors.append(f"{path}:{n}: {m}")
    if survivors:
        raise AssertionError(
            "scaffold markers still in the code - finish the stamping: "
            + "; ".join(survivors[:6]))


MOJIBAKE = ("\u00e2\u20ac", "\u00c3\u00a2", "\u00c3\u00a9", "\u00c3\u00a7",
            "\u00c3\u00a3", "\u00c3\u00a1", "\u00c3\u00b5", "\u00c3\u00a0",
            "\u00c2\u00a0")
ENCODING_SCAN_SUFFIXES = (".md", ".py", ".csv", ".txt", ".json", ".yaml",
                          ".toml")
ENCODING_SKIP_DIRS = {".venv", "venv", "dist", "build", "landing", "data",
                      "__pycache__", ".git", "logs", "node_modules",
                      ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def check_encoding():
    """House rule 1, made checkable (wave 33): no cp1252 round trip."""
    hits = []
    for dirpath, dirnames, filenames in os.walk("."):
        dirnames[:] = [d for d in dirnames if d not in ENCODING_SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith(ENCODING_SCAN_SUFFIXES):
                continue
            path = os.path.join(dirpath, fn)
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as fh:
                    for n, line in enumerate(fh, 1):
                        if any(m in line for m in MOJIBAKE):
                            hits.append(f"{path}:{n}")
            except OSError:
                continue
    if hits:
        raise AssertionError(
            f"encoding corruption at {hits[:5]} - a UTF-8 file was read as "
            f"cp1252 and written back, almost certainly by "
            f"`Get-Content | Set-Content` in Windows PowerShell. Do NOT "
            f"retype the characters: fix it by reversing the round trip - "
            f"raw = p.read_text(encoding='utf-8'); "
            f"p.write_text(raw.encode('cp1252').decode('utf-8'), "
            f"encoding='utf-8').")


def readme_written(release=False):
    """The README says something about THIS project, to a stranger.

    The "When it goes wrong" table is exempt from the placeholder check until
    --release: its real messages only exist once the project runs. At release
    it is checked like everything else.
    """
    if not os.path.exists("README.md"):
        raise AssertionError("README.md missing")
    with open("README.md", "r", encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()
    opening, badge_lines = _readme_regions(lines)

    left = []
    in_failures = False
    for n, line in enumerate(lines, 1):
        low = line.lower()
        if low.startswith("## "):
            in_failures = "goes wrong" in low
        if in_failures and not release:
            continue
        if line.lstrip().startswith(">") and (n - 1) not in opening:
            continue
        if re.search(r"<[a-z][^>]{4,}>", line):
            left.append(f"line {n}")
    if left:
        raise AssertionError(
            f"README.md still holds template placeholders at {left[:5]} - "
            "it is written for a stranger at phase R (R2), not stamped and "
            "left.")

    fenced = False
    for n, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced or (n - 1) in badge_lines:
            continue
        low = line.lower()
        hit = next((w for w in README_JARGON if w in low), None)
        if hit is None and CHECKPOINT_ID.search(line):
            hit = CHECKPOINT_ID.search(line).group(0)
        if hit:
            raise AssertionError(
                f"README.md contains framework vocabulary ({hit!r}) at line "
                f"{n}. This file is read by someone who has never heard of "
                f"this framework.")

    if not any(lines[i].lstrip().startswith(">") for i in opening):
        raise AssertionError(
            "README.md has no opening 'one thing to know first' line. The "
            "most consequential fact about a tool must not be discoverable "
            "only by reading an error table.")

    for n, line in enumerate(lines, 1):
        if BADGE_IMG.search(line) and (n - 1) not in badge_lines:
            raise AssertionError(
                f"README.md has a badge at line {n} outside the "
                f"'{BADGE_START}' markers. Badges are written by "
                f"verify_build.py --release from facts it has just gated, "
                f"never typed.")
    for i in sorted(badge_lines):
        line = lines[i]
        if BADGE_START in line or BADGE_END in line or not line.strip():
            continue
        if not BADGE_ONLY_LINE.match(line):
            raise AssertionError(
                f"README.md line {i + 1} sits between the badge markers but "
                f"is not a badge the gate wrote. Put your own text outside "
                f"them.")


def _raw_string_spans(path):
    """(start, end) positions of every raw string literal in a Python file."""
    import io
    import tokenize
    try:
        text = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
        spans = []
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.STRING:
                prefix = re.match(r"[A-Za-z]*", tok.string).group(0)
                if "r" in prefix.lower():
                    spans.append((tok.start, tok.end))
        return spans
    except (OSError, tokenize.TokenError, IndentationError, SyntaxError):
        return []


def no_absolute_paths():
    """Source code holds no absolute path (house rules 1 and 2).

    Tests are exempt on purpose: a test of a path policy has to feed the code
    the very paths it must reject. A source line that truly needs one carries
    `# abs-path-ok: <reason>` - the reason is required.
    """
    hits = []
    for path in _source_files():
        raw = pathlib.Path(path).read_text(
            encoding="utf-8", errors="replace").splitlines()
        raw_spans = _raw_string_spans(path)
        for n, line in enumerate(_code_text(path).splitlines(), 1):
            in_raw = any(
                (r0, c0) <= (n, m.start()) < (r1, c1)
                for m in ABSOLUTE_PATH_RAW.finditer(line)
                for (r0, c0), (r1, c1) in raw_spans)
            if not in_raw and not ABSOLUTE_PATH.search(line):
                continue
            original = raw[n - 1] if n - 1 < len(raw) else ""
            ok = ABS_PATH_OK.search(original)
            if ok and (ok.group(1) or "").strip():
                continue
            hits.append(f"{path}:{n}")
    if hits:
        raise AssertionError(
            f"hardcoded absolute path in {hits[:5]} - locations come from "
            f"configuration (an environment variable, .env, or the project's "
            f"own location), never from a literal in code. If one line truly "
            f"needs it, end it with '# abs-path-ok: <reason>'.")


# Import name -> distribution name, for the packages where they differ.
_DIST_ALIAS = {
    "extract_msg": "extract-msg", "yaml": "pyyaml", "dateutil":
    "python-dateutil", "pil": "pillow", "fitz": "pymupdf", "dotenv":
    "python-dotenv", "sklearn": "scikit-learn", "bs4": "beautifulsoup4",
    "cv2": "opencv-python", "docx": "python-docx", "pptx": "python-pptx",
    "jwt": "pyjwt", "win32com": "pywin32", "pythoncom": "pywin32",
    "google": "google-api-python-client",
}
_TEST_TOOLS = {"pytest", "pytest-cov", "ruff", "pytest-mock", "coverage"}


def _canon(name):
    """A distribution name in PEP 503 form: lower case, runs of -_. as '-'."""
    return re.sub(r"[-_.]+", "-", (name or "").strip().lower())


def dependencies():
    """requirements.txt, contract Part 7 and the actual imports agree.

    A requirements line may end with `# not imported: <why>` for a package
    the project needs but never imports (a plugin, a runtime extra). The
    reason is required.
    """
    if not os.path.exists("requirements.txt"):
        raise AssertionError("requirements.txt missing")
    declared, exempt = set(), set()
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        for raw in fh:
            spec, _, comment = raw.partition("#")
            spec = spec.strip()
            if not spec or spec.startswith("-"):
                continue
            name = _canon(re.split(r"[<>=!~\[; ]", spec)[0])
            if not name:
                continue
            declared.add(name)
            note = re.match(r"\s*not imported:\s*(\S.*)", comment or "")
            if note:
                exempt.add(name)

    imported = set()
    local = set()
    for path in _walk_py(include_framework=True):
        p = pathlib.PurePosixPath(path)
        local.add(p.stem.lower())
        local.update(part.lower() for part in p.parts[:-1])
        try:
            tree = ast.parse(pathlib.Path(path).read_text(
                encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.name.split(".")[0].lower())
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    imported.add(node.module.split(".")[0].lower())
    stdlib = {m.lower() for m in getattr(sys, "stdlib_module_names", ())}
    as_dist = {_canon(_DIST_ALIAS.get(m, m)) for m in imported}

    problems = []
    unused = declared - as_dist - _TEST_TOOLS - exempt
    if unused:
        problems.append(
            f"declared but never imported: {sorted(unused)} - remove them "
            f"from requirements.txt and contract Part 7, import them, or end "
            f"the line with '# not imported: <why>'.")
    if stdlib:
        undeclared = sorted(
            _canon(_DIST_ALIAS.get(m, m)) for m in imported
            if m not in local and m not in stdlib and not m.startswith("_")
            and _canon(_DIST_ALIAS.get(m, m)) not in declared)
        if undeclared:
            problems.append(
                f"imported but not in requirements.txt: {undeclared} - a "
                f"clean checkout cannot install what is not declared.")

    card_libs = set()
    try:
        part7 = _section(_card_text(), "Part 7")
    except OSError:
        part7 = None
    if part7 is not None:
        for cells in _table_rows(part7):
            first = _strip_ticks(cells[0]).lower() if cells else ""
            if not first or first == "library" or _is_placeholder(first):
                continue
            if first.startswith("none"):
                continue
            if first in stdlib:
                continue          # sqlite3, csv ... ship with Python
            card_libs.add(_canon(re.split(r"[<>=!~\[; ]", first)[0]))
        shipped = declared - _TEST_TOOLS
        if card_libs - shipped:
            problems.append(
                f"contract Part 7 names {sorted(card_libs - shipped)} but "
                f"requirements.txt does not - the signed contract and the "
                f"install list disagree.")
        if shipped - card_libs:
            problems.append(
                f"requirements.txt ships {sorted(shipped - card_libs)} with "
                f"no contract Part 7 row - every library that ships gets a "
                f"row the builder signed.")
    if problems:
        raise AssertionError("; ".join(problems))


def pushed():
    """The release is cut from committed code that is already on the remote.

    Register F-61: in real builds a checkpoint reported as "pushed" was not,
    three times in one build and five more in the next. A release that
    exists only on one disk is not a release anybody else can check.
    """
    status = _git(".", "status", "--porcelain", "--untracked-files=no")
    if status is None or status.returncode != 0:
        raise AssertionError("git status could not run here")
    dirty = [line[3:] for line in status.stdout.splitlines() if line.strip()]
    if dirty:
        raise AssertionError(
            f"uncommitted changes to tracked files: {dirty[:6]}. A release "
            f"is cut from committed code. If the only change is README.md's "
            f"badge line, this gate wrote it on the last passing run: "
            f"commit it, push, and run --release again.")
    upstream = _git(".", "rev-parse", "--abbrev-ref", "@{u}")
    if upstream is None or upstream.returncode != 0:
        raise AssertionError(
            "this branch has no remote to push to. Ask the builder where "
            "the repository lives, add it (git remote add origin <url>), "
            "and push - a release nobody else can fetch is not a release.")
    ahead = _git(".", "rev-list", "--count", "@{u}..HEAD")
    count = ahead.stdout.strip() if ahead and ahead.returncode == 0 else "?"
    if count != "0":
        raise AssertionError(
            f"{count} commit(s) are not pushed to "
            f"{upstream.stdout.strip()}. Push, then run --release again.")


def builder_identity() -> str:
    """Who ran this release. Read, never asked (wave 33).

    STATED ASSUMPTION: this identifies an ACCOUNT ON A MACHINE, not a person,
    and it is not an authentication claim.
    """
    return f"{getpass.getuser()}@{socket.gethostname()}"


def _framework_version():
    """The pinned framework version, read from memory.md's Decisions line."""
    try:
        with open("memory.md", "r", encoding="utf-8", errors="replace") as fh:
            m = re.search(r"Framework version: `([^`]+)`", fh.read())
        return m.group(1) if m else None
    except OSError:
        return None


def _latest_release():
    """(version, date) from the newest version.md row, or (None, None)."""
    try:
        with open("version.md", "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                cells = [c.strip() for c in line.split("|")[1:-1]]
                if len(cells) >= 2 and re.match(r"^v?\d+\.\d+", cells[0]):
                    return cells[0], cells[1]
    except OSError:
        pass
    return None, None


def _kind():
    """The contract's 'Kind of project' answer, first few words, or None."""
    try:
        value = _field(_card_text(), "Kind of project") or ""
    except OSError:
        return None
    words = re.findall(r"[A-Za-z][A-Za-z-]*", value)
    return " ".join(words[:2]).lower() if words else None


def _shield(label, message, colour):
    def esc(s):
        return str(s).replace("-", "--").replace("_", "__").replace(" ", "_")
    return (f"![{label}](https://img.shields.io/badge/"
            f"{esc(label)}-{esc(message)}-{colour})")


def write_badges():
    """Replace the badge block with facts THIS run just gated (wave 33).

    Writes only when the line would change, and says so: the release gate
    then fails CLEAN until the new line is committed, so the tag always
    contains the badge that describes it.
    """
    if not os.path.exists("README.md"):
        return
    py = f"{sys.version_info.major}.{sys.version_info.minor}"
    badges = [_shield("python", py + "+", "blue"),
              _shield("gate", "GO", "brightgreen")]
    if TEST_COUNT is not None:
        badges.append(_shield("tests", f"{TEST_COUNT} passed", "brightgreen"))
    fw = _framework_version()
    if fw:
        badges.append(_shield("framework", fw, "informational"))
    ver, when = _latest_release()
    if ver:
        badges.append(_shield("released", f"{ver} {when}", "blue"))
    kind = _kind()
    if kind:
        badges.append(_shield("kind", kind, "lightgrey"))

    with open("README.md", "r", encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()
    out, inside, wrote = [], False, False
    for line in lines:
        if BADGE_START in line:
            inside, wrote = True, True
            out.append(line)
            out.append(" ".join(badges) + "\n")
            continue
        if BADGE_END in line:
            inside = False
            out.append(line)
            continue
        if not inside:
            out.append(line)
    if not wrote or out == lines:
        return
    with open("README.md", "w", encoding="utf-8") as fh:
        fh.writelines(out)
    print("  badges written - README.md changed: commit it, push, and run "
          "--release again before tagging")


# ------------------------------------------------------- evidence receipts

EVIDENCE_DIR_NAME = ".evidence"
_COMMITISH = ("commit ", "sha ", "hash ")
CONTRACT_NAME = CARD
UNVERIFIABLE = "UNVERIFIABLE"


ADDITIONS_HEADING = b"\n## Additions after sign-off"


def _without_additions(data):
    """The contract bytes minus the '## Additions after sign-off' section.

    An addition is agreed DURING the build, by design without re-signing
    the contract (phase C, ADDING). Hashing it made every earlier receipt -
    the B4 seal included - "made against a different contract" at release
    (found by the independent check). The signed Parts stay hashed; the
    additions table is history, recorded beside them.
    """
    start = data.find(ADDITIONS_HEADING)      # only a real heading line,
    if start == -1:                          # never the words quoted in a Part
        return data
    rest = data[start + len(ADDITIONS_HEADING):]
    ends = [i for i in (rest.find(b"\n## "), rest.find(b"\n---")) if i != -1]
    end = start + len(ADDITIONS_HEADING) + min(ends) if ends else len(data)
    return data[:start] + data[end:]


def contract_hash():
    """SHA-256 of the contract, CRLF normalised to LF (register F-72), with
    the Additions-after-sign-off section left out (wave 43)."""
    path = pathlib.Path(CONTRACT_NAME)
    if not path.is_file():
        return None
    return hashlib.sha256(_without_additions(
        path.read_bytes().replace(b"\r\n", b"\n"))).hexdigest()


def _contract_hash_legacy():
    """Raw-byte and CRLF forms of the contract hash, so no receipt written
    in a CRLF working tree is invalidated by a checkout's line endings."""
    path = pathlib.Path(CONTRACT_NAME)
    if not path.is_file():
        return set()
    raw = path.read_bytes()
    lf = raw.replace(b"\r\n", b"\n")
    return {hashlib.sha256(raw).hexdigest(),
            hashlib.sha256(lf.replace(b"\n", b"\r\n")).hexdigest()}


def _git_sha():
    """The current commit, or None outside a repository. Never raises."""
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"],
                                capture_output=True, text=True, timeout=10,
                                encoding="utf-8", errors="replace")
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def write_receipt(kind, exit_code, checks=None, row_counts=None, note=None):
    """Write one machine receipt into `.evidence/` and return its path.

    NEVER raises: a gate that crashed because it could not write its own
    paperwork would be exactly the ceremony house rule 18 forbids.
    """
    try:
        out_dir = pathlib.Path(EVIDENCE_DIR_NAME)
        out_dir.mkdir(exist_ok=True)
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y%m%dT%H%M%SZ")
        path = out_dir / f"{stamp}_{kind}.json"
        suffix = 2
        while path.exists():
            path = out_dir / f"{stamp}_{kind}_{suffix}.json"
            suffix += 1
        receipt = {
            "kind": kind,
            "written_at": datetime.datetime.now(
                datetime.timezone.utc).isoformat(),
            "command": " ".join(sys.argv),
            "exit_code": exit_code,
            "checks": checks or {},
            "row_counts": row_counts or {},
            "git_sha": _git_sha(),
            "builder": builder_identity(),
            "contract_file": CONTRACT_NAME,
            "contract_sha256": contract_hash(),
            "gate_sha256": _gate_identity()[0],
            "note": note,
        }
        path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        return path
    except OSError:
        return None


def _checkpoint_log_table(text):
    """(header, rows) of memory.md's '## Checkpoint log' table."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("## checkpoint log"):
            start = i
            break
    if start is None:
        return None, []
    header, rows = None, []
    for line in lines[start + 1:]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        if not any(cells):
            continue
        rows.append(dict(zip(header, cells)))
    return header, rows


# What a row's receipt must show, by the row's id (wave 43). A receipt that
# exists, is committed and matches the contract is not enough: an
# independent check cited, on a passing checkpoint, a receipt whose own
# TESTS line said FAIL. Each kind of row now cites a run in which the thing
# it claims was actually green. First match wins; the names are check-name
# prefixes; "GO" means the whole run passed.
ROW_NEEDS = (
    (r"^(B4|M2)\b", ("CONTRACT",)),
    (r"^C0\b", ("CONTRACT", "ARTIFACT WRITTEN")),
    (r"^(C\d|M-C|M-D|M3)", ("CONTRACT", "TESTS")),
    (r"^R1\b", ("CONTRACT", "TESTS", "ARTIFACT (")),
    (r"^R2\b", ("README",)),
    (r"^(R3|M0|M4)\b", ("GO",)),
)


def _receipt_shortfall(cp, receipt):
    """What `receipt` fails to show for checkpoint row `cp`, or None."""
    for pattern, needs in ROW_NEEDS:
        if re.match(pattern, cp):
            break
    else:
        return None
    if needs == ("GO",):
        if receipt.get("exit_code") != 0:
            return "its run was NO-GO, and this row claims a GO"
        return None
    checks = receipt.get("checks") or {}
    missing = []
    for need in needs:
        hits = [v for k, v in checks.items() if k.startswith(need)]
        if not hits or any(v != "PASS" for v in hits):
            missing.append(need.rstrip(" ("))
    if missing:
        return (f"its run did not pass {missing}, which this row claims - "
                f"re-run the gate once they are green and cite that receipt")
    return None


def check_evidence(release=False):
    """A checkpoint row claiming PASS must cite a receipt that exists.

    At --release: a PASS row citing nothing, citing a missing or uncommitted
    receipt, or citing one made against a different contract fails. A row no
    machine can back writes `UNVERIFIABLE: <reason>` - never a fake receipt.
    """
    path = pathlib.Path("memory.md")
    if not path.is_file():
        raise AssertionError("memory.md not found - the checkpoint log "
                             "lives there")
    text = path.read_text(encoding="utf-8", errors="replace")
    header, rows = _checkpoint_log_table(text)

    if header is None:
        raise AssertionError("memory.md has no '## Checkpoint log' table")
    receipt_col = next((c for c in header if c.startswith("receipt")), None)
    if receipt_col is None:
        raise AssertionError(
            "the '## Checkpoint log' table has no Receipt column. Copy the "
            "current table header from the template.")
    if not release:
        return
    status_col = next((c for c in header if c.startswith("status")), None)
    if status_col is None:
        raise AssertionError(
            "the '## Checkpoint log' table has no Status column")
    if not rows:
        raise AssertionError(
            "releasing with an empty checkpoint log. A release means every "
            "row of the approved plan was reached.")

    cp_col = header[0]
    current = contract_hash()
    evidence_dir = pathlib.Path(EVIDENCE_DIR_NAME)
    problems = []

    # Rows above the newest recorded release (an R3 or M4 PASS row) were
    # proven by that release against the contract of the day. A later change
    # that re-signs the contract (phase M, M2) must not turn them into
    # "a different contract" - only rows after the last release are held to
    # the contract on disk.
    last_release = -1
    for i, row in enumerate(rows):
        cp_i = (row.get(cp_col) or "").strip("*` ")
        if (re.match(r"^(R3|M4)\b", cp_i)
                and "PASS" in (row.get(status_col) or "").upper()):
            last_release = i
    # The same for a re-signed contract: the LATEST seal (B4, or M2 when a
    # change re-signs it) must itself match the contract on disk; every row
    # before it was made against the contract in force at the time, and is
    # history. Without this an honest M0 baseline - run on the unchanged
    # code before M2 - fails at the next release (independent check, second
    # pass). A seal row that dodges its receipt never counts as a seal.
    for i, row in enumerate(rows):
        cp_i = (row.get(cp_col) or "").strip("*` ")
        cited_i = (row.get(receipt_col) or "").strip().strip("`")
        if (not re.match(r"^(B4|M2)\b", cp_i)
                or "PASS" not in (row.get(status_col) or "").upper()
                or not cited_i or cited_i.upper().startswith(UNVERIFIABLE)):
            continue
        try:
            seal = json.loads((evidence_dir / cited_i).read_text(
                encoding="utf-8"))
        except (OSError, ValueError):
            continue
        sealed = seal.get("contract_sha256")
        if sealed and (sealed == current
                       or sealed in _contract_hash_legacy()):
            last_release = max(last_release, i)

    for index, row in enumerate(rows):
        cp = row.get(cp_col, "?") or "?"
        status = (row.get(status_col) or "").upper()
        cited = (row.get(receipt_col) or "").strip().strip("`")
        # DONE is for set-up and writing steps (A, B0-B3), which make no
        # claim a receipt could back. A build, release or change row that
        # says DONE is a PASS that dodged its receipt.
        if "DONE" in status and not re.match(r"^(A\d|B[0-3])\b",
                                             cp.strip("*` ")):
            problems.append(
                f"{cp} says DONE. DONE is only for set-up and contract-writing "
                f"rows (A, B0-B3); a build, release or change row claims PASS "
                f"and cites the receipt that proves it.")
            continue
        if "PASS" not in status:
            continue

        if cited.upper().startswith(UNVERIFIABLE):
            reason = cited[len(UNVERIFIABLE):].lstrip(": -").strip()
            if not reason:
                problems.append(
                    f"{cp} is marked UNVERIFIABLE with no reason.")
            continue

        low = cited.lower()
        if low.startswith(_COMMITISH) or (len(cited) in range(7, 41)
                                          and all(c in "0123456789abcdef"
                                                  for c in low)):
            problems.append(
                f"{cp} cites {cited!r}, which is a git commit, not a receipt. "
                f"A commit proves CODE CHANGED. It does not prove a command "
                f"ran, what it returned, or which version of the contract it "
                f"ran against. Cite the `{EVIDENCE_DIR_NAME}/` file the run "
                f"wrote, and commit it (`git add -f`).")
            continue

        if not cited or _is_placeholder(cited):
            problems.append(
                f"{cp} claims {status} and cites no receipt. Cite the "
                f"`.evidence/` file the run wrote, or write "
                f"`UNVERIFIABLE: <why>`. Do not invent a receipt.")
            continue

        target = evidence_dir / cited
        if not target.is_file():
            problems.append(
                f"{cp} cites receipt {cited!r}, which is not in "
                f"{EVIDENCE_DIR_NAME}/.")
            continue

        if _untracked(".", target):
            problems.append(
                f"{cp} cites {cited!r}, which exists on disk but is not "
                f"committed. A clean checkout of this release will not have "
                f"it. Commit it: git add -f {EVIDENCE_DIR_NAME}/{target.name}")
            continue

        try:
            receipt = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, ValueError) as err:
            problems.append(f"{cp} cites {cited!r}, which is unreadable: {err}")
            continue

        stamped = receipt.get("contract_sha256")
        if (index > last_release and current and stamped
                and stamped != current
                and stamped not in _contract_hash_legacy()):
            problems.append(
                f"{cp} cites {cited!r}, but that receipt was produced against "
                f"a DIFFERENT {CONTRACT_NAME} (receipt {stamped[:12]}..., on "
                f"disk {current[:12]}...). Re-run the check and re-cite it.")
            continue

        short = _receipt_shortfall(cp.strip("*` "), receipt)
        if short:
            problems.append(f"{cp} cites {cited!r}, but {short}.")

    if problems:
        raise AssertionError("; ".join(problems))


def _safe_console():
    """Never die on a character the console cannot print (wave 43).

    On Windows, Python writes to a PIPE in the locale encoding (cp1252) -
    and the commit hook always reads this script through a pipe. A failure
    message quotes contract text, and a design document is full of arrows
    and symbols cp1252 has no byte for: the gate then crashed with a
    UnicodeEncodeError instead of printing the failure. Unprintable
    characters are now written as escapes; the verdict is unaffected.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="backslashreplace")
        except (AttributeError, ValueError):
            pass


def main(argv=None):
    _safe_console()
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "--hash":
        if len(argv) != 2 or not os.path.isfile(argv[1]):
            print("usage: python scripts/verify_build.py --hash <file>")
            return 2
        print(document_hash(argv[1]))
        return 0
    release = "--release" in argv
    hook = "--hook" in argv and not release
    full, short = _gate_identity()
    mode = "RELEASE" if release else ("HOOK" if hook else "DEV")
    print(f"verify_build ({mode} mode) · core gate · sha256 {full}")
    if hook:
        check("STRUCTURE", structure)
        check("GIT (a real identity on this commit)",
              lambda: git_identity(hook=True))
        check("GITIGNORE (data, secrets and receipts stay out of git)",
              gitignore_guards)
        check("PLACEHOLDER survival", placeholders)
        check("ENCODING (house rule 1: no cp1252 round trip)", check_encoding)
        check("NO ABSOLUTE PATHS", no_absolute_paths)
        check("ORDER: no code before the contract is signed",
              code_needs_signed_contract)
        check("ORDER: no code before the artifact test (C0)",
              code_needs_artifact_test)
        failed = RESULTS.count(False)
        print(f"verify_build --hook: {'PASS' if failed == 0 else 'FAIL'} "
              f"({len(RESULTS) - failed}/{len(RESULTS)}). The contract, "
              f"tests, README and evidence run at the go/no-go.")
        return 0 if failed == 0 else 1
    check("STRUCTURE", structure)
    check("GIT (identity, hook installed)", git_identity)
    check("GITIGNORE (data, secrets and receipts stay out of git)",
          gitignore_guards)
    check("PLACEHOLDER survival", placeholders)
    check("CONTRACT (contract.md)", contract)
    check("TESTS (pytest)", tests)
    check("ARTIFACT WRITTEN (C0: a real test, not the placeholder)",
          artifact_written)
    check("ARTIFACT (strict rule 6: the output is right)", artifact)
    check("SMOKE (the contract's smoke command)", smoke)
    check("MARKERS (no scaffold residue)", markers)
    check("ENCODING (house rule 1: no cp1252 round trip)", check_encoding)
    check("README (written for a reader, not the builder)",
          lambda: readme_written(release))
    check("NO ABSOLUTE PATHS", no_absolute_paths)
    check("DEPENDENCIES (declared == imported == contract)", dependencies)
    check("EVIDENCE (every PASS row cites a receipt)",
          lambda: check_evidence(release))
    if release:
        def _lineage():
            problems = _release_lineage_problems(".")
            if problems:
                raise AssertionError("; ".join(problems))
        check("RELEASE LINEAGE (version.md order, earlier tags, no moved tag)",
              _lineage)
        check("PUSHED and CLEAN (committed, and on the remote)", pushed)
    failed = RESULTS.count(False)
    if release and failed == 0:
        write_badges()

    receipt = write_receipt(
        "check", 0 if failed == 0 else 1,
        checks=dict(zip(CHECK_NAMES, ["PASS" if r else "FAIL"
                                      for r in RESULTS])),
        note="RELEASE gate" if release else "DEV gate")
    if receipt:
        print(f"receipt: {EVIDENCE_DIR_NAME}/{receipt.name}")

    print(f"verify_build: {'GO' if failed == 0 else 'NO-GO'} "
          f"({len(RESULTS) - failed}/{len(RESULTS)} passed)")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
