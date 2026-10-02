"""The artifact test - strict rule 6 (house rule 18).

STAMPED AT A1. Phase C writes it FIRST, at checkpoint C0, before any other
code - the commit hook refuses project code while this file is still the
stamped placeholder.

--------------------------------------------------------------------------
WHY THIS FILE EXISTS
--------------------------------------------------------------------------
Every other check in this framework asks whether the code has the right
SHAPE: the right files, a signed contract, a passing test suite. This is the
only one that asks whether it does the right THING. A project once passed
every other check and shipped an output that was 297 characters of nothing,
because its tests validated the code against the author's own (wrong)
understanding of its input.

--------------------------------------------------------------------------
WHAT "THE PRIMARY OUTPUT" MEANS - whatever the kind of project
--------------------------------------------------------------------------
It is named in contract.md Part 8. Examples:
  - a report or file generator: the file it writes;
  - an application: the answer a user gets for one realistic request - for
    a question-answering app, the exact result and the record shown with it;
  - a library: the value its main entry point returns for a realistic input;
  - a service: the response to one realistic request.

--------------------------------------------------------------------------
WHAT MAKES THIS TEST DIFFERENT FROM THE ONES IN THE REST OF tests/
--------------------------------------------------------------------------
1. REALISTIC INPUT - derived from a real sample where one exists (sanitised,
   trimmed, structurally genuine). If none exists, hand-build it, say so in
   this docstring, and record it in memory.md under Open questions.
2. THE WHOLE PATH, entry point to output, the way a user or caller reaches it.
   No monkeypatching of the project's own internals.
3. NO CREDENTIAL AND NO NETWORK. An external service (an AI model, an API) is
   replaced by a scripted stand-in at its boundary - the one place the
   contract says the outside world enters - never inside the logic.
4. ASSERT ON CONTENT, not on exit code: a specific value derived from this
   specific input must appear in the output.
5. TWO FIXTURES, DIFFERENT CONTENT: if two inputs give the same output, the
   program is reciting, not deriving.

--------------------------------------------------------------------------
HOW TO REPLACE THIS
--------------------------------------------------------------------------
Delete `test_artifact_placeholder` below - all of it, including the sentence
in its failure message - and write the two tests agreed at B3. Keep a
docstring on each: the next person needs to know what the assertions mean.

IMPORT THE PROJECT INSIDE EACH TEST FUNCTION, not at the top of this file.
At C0 the code does not exist yet; a top-level import that fails stops pytest
collecting ANY test, and every checkpoint after it would look red.
"""

import pytest


def test_artifact_placeholder():
    """The stamped placeholder. It fails on purpose until C0 replaces it."""
    pytest.fail(
        "ARTIFACT TEST NOT WRITTEN YET - strict rule 6 (house rule 18). "
        "Replace tests/test_artifact.py at C0 with a test that builds this "
        "project's primary output (contract.md Part 8) from a realistic "
        "input, with no credential and no network, and asserts on its "
        "CONTENT. See project-core phase_C_build.md, C0."
    )
