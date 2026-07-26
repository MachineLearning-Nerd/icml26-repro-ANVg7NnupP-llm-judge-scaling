# Evaluator-blind pre-publication review

The reviewer was given only an assembled candidate directory and the rubric.
It was not told where current evidence was stored. Traversal began at
`README.md` and followed only reachable page and evidence links.

## Pass 1 — blocked

Fresh candidate: `/tmp/orx-candidate-prepub-773fa691`
Protected parent: `888e34394f08123538bccdaba0e8852558a5b724`

Files opened, in order:

1. `logbook.json`
2. `README.md`
3. `pages/current-verification/page.md`
4. `evidence/current/outputs/summary.json`
5. `evidence/current/reproduction/reproduce.py`
6. `evidence/current/reproduction/test_reproduction.py`
7. `evidence/current/pyproject.toml`
8. `evidence/current/uv.lock`
9. `evidence/current/MANIFEST.sha256`
10. `pages/evaluator-visibility-matrix/page.md`

Blocked conclusion: the current summary was obvious, but `pages/index.md`, the
detailed Claim 4/5 pages, their verifier sources, and their raw claim-specific
tables were not reachable from that path. Release was stopped.

Fix: README now links the page index, the current summary links both detailed
claim pages, and the traversal resolves the logbook root slug. No acceptance
threshold or scientific result changed.

## Pass 2 — complete after fixes

Fresh candidate: `/tmp/orx-candidate-prepub-fixed-773fa691`

The traversal opened:

1. `logbook.json`
2. `README.md`
3. `pages/current-verification/page.md`
4. `pages/index.md`
5. `pages/claim-4-optimal-temperature/page.md`
6. `pages/claim-5-scaling-comparison/page.md`
7. `evidence/current/outputs/summary.json`
8. `evidence/current/reproduction/reproduce.py`
9. `evidence/current/reproduction/test_reproduction.py`
10. `evidence/current/pyproject.toml`
11. `evidence/current/uv.lock`
12. `evidence/current/MANIFEST.sha256`
13. `pages/evaluator-visibility-matrix/page.md`
14. all eight preserved judged pages
15. Claim 4 verifier, contract, two raw CSVs, certificate, checker, control,
    source audit, runtime, and limitations
16. Claim 5 verifier, contract, raw CSV, certificate, checker, control, source
    audit, runtime, and limitations

Conclusions:

- current verifier obvious: **yes**
- exact Claim 4 and Claim 5 contracts locatable: **yes**
- code and raw data locatable: **yes**
- independent checkers and intended-failure controls locatable: **yes**
- assumptions, command, environment, seeds, CPU/runtime, and limitations:
  **yes**
- protected file set is a subset of candidate: **yes** (20/20)
- immutable protected file hashes match: **yes**
- exact manifest entries match: **yes** (80 entries plus manifest)
- missing visibility cells: **none**

Reviewer verdicts: Claims 1–5 **VERIFIED**. This is a pre-publication review,
not the live judge result.
