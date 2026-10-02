# DataLens-v1 — release history

**Newest release on TOP** — add each new row directly under the header. The
top row is read as the running version by the logs, the release badge and the
release gate (wave 40).

| Version | Date | Builder | Branch/tag | Description (hotfix rows: add one root-cause sentence) |
|---------|------|---------|-----------|--------------------------------------------------------|


**A row describes what the tag CONTAINS, never what happened afterwards
(wave 39).** In a real build `v1.0` was tagged, and the fixes that real data
demanded — a source column holding a filename, an empty numeric field, a
dimension that fanned the fact out — landed in later commits. Read in order,
the build log implied `v1.0` had been validated against real data. It had not.

**So: if a run happened AFTER the tag was cut, it belongs in the NEXT row, not
in this one.** A release ledger that borrows later evidence is the same defect
class as a checkpoint row claiming a deployment that never happened — the one
evidence receipts exist to stop.
