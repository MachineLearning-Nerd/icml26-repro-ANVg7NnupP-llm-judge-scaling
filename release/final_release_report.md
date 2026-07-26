# Final release report

- Previous live judged score: `6/10`
- Conservative projected score range after the proposed change: `8–10/10`
- Best-supported possible new score: `10/10` — **forecast only, not a judge result**

| Claim | Current points | Possible points | Confidence | Evidence status | Basis and remaining risk |
| --- | ---: | ---: | --- | --- | --- |
| 1 | 2 | 2 | HIGH | VERIFIED | Preserved and rerun: slopes -1.997562 to -1.997545; coefficient error ≤0.2923%. Remaining risk is only evaluator interpretation of finite numerical evidence. |
| 2 | 2 | 2 | HIGH | VERIFIED | Preserved and rerun: 36/36 monotone; `k=1` identity; independent 640k-sample discrepancy ≤0.004079. |
| 3 | 2 | 2 | HIGH | VERIFIED | Preserved and rerun: 23/90 finite optima; representative `k*=2` and +5.809% later harm. The separate threshold and `k*` approximation formulas remain explicitly untested. |
| 4 | 0 | 2 | HIGH | VERIFIED | Exact truncated-expansion certificate plus ten eligible exact calibrations, independent 120k-sample checker, and two intended-failure controls. Risk: evaluator could interpret the formula as an exact finite-temperature identity despite its Result 2 context. |
| 5 | 0 | 2 | HIGH | VERIFIED | Exact asymptotic factorization, five assumption-audited `α` values, independent root/finite-difference checker, and out-of-domain control. Risk: this is the stated deterministic proportional limit, not finite-dimensional retraining. |

Current total score: **6/10**. Conservative projected total: **8–10/10**.
Best-supported possible total: **10/10, forecast only**. Claims 4 and 5 changed
from INCONCLUSIVE to internally VERIFIED. No claim is BLOCKED.

The exact publication action is a single Hugging Face Hub text-only commit to
the existing Space `DineshAI/ANVg7NnupP`, parented to protected revision
`888e34394f08123538bccdaba0e8852558a5b724`. It updates the canonical README,
index, and logbook navigation; adds four current pages; and uploads the exact
allowlisted text evidence under `evidence/current/`. It creates no new Space and
deletes no path.

## Experiment tree and winning evidence

The tree is stacked:

```text
Frozen validated baseline
└── Claim 4 exact temperature contract
    └── Claim 5 inference versus data scaling
        └── Evaluator-visible cumulative evidence
            └── Release candidate and blind audit
                └── Publication manifest and post-release verification
```

The winning validated verifier is branch
`orx/release-candidate-and-blind-audit`, commit
`e0a6aa04e971eb1bf3516f484451e1f529b6f421`, run
`585734a7-0b00-4bb3-87f7-9e951cf34514`.

Every formal node inherited this exact command:

```text
uv sync --frozen && uv run python reproduction/reproduce.py --output outputs && uv run pytest -q reproduction/test_reproduction.py
```

The winning run finished in 47 seconds on Hugging Face `cpu-upgrade`, exposed
64 CPUs through affinity after an estimated requirement of 2 cores, spent
8.668 seconds in the scientific suite, and passed 13/13 tests. The formal
campaign used 262 seconds of HF `cpu-upgrade` including failed infrastructure
or packaging attempts. At the official $0.03/hour rate, that is about $0.0022
by exact runtime or at most $0.0035 under conservative one-minute rounding per
job. Local baseline/presentation work used CPU only and incurred no metered
cloud cost. No GPU was used.

## Evidence and visibility

Internal evidence is under `.openresearch/artifacts/claim1` through `claim5`.
The evaluator-visible canonical page is
`pages/current-verification/page.md`; Claim 4, Claim 5, and visibility pages are
first in navigation. All raw CSV/JSON, executable code, exact environment,
checkers, controls, assumptions, source hashes, runtime, and limitations are
linked from those pages.

The pre-publication gate requires:

- protected file paths are a subset of the assembled candidate;
- all old pages except the intentionally updated entrypoints are byte-identical;
- candidate JSON parses and all canonical links resolve;
- the exact text allowlist matches its SHA-256 manifest;
- secret scanning returns no findings;
- two evaluator-blind traversals open only files reachable from the canonical
  entrypoint and leave no missing visibility cell.

After publication, the exact published revision will be freshly downloaded,
all uploaded hashes will be checked, and the same traversal will be rerun.
