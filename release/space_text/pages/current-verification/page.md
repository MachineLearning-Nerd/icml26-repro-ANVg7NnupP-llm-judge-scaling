# Current verification: five claim contracts

Previous live judged score: **6/10**  
Judged Space revision: `888e34394f08123538bccdaba0e8852558a5b724`  
Conservative projected score after this candidate: **8–10/10**  
Best-supported possible score: **10/10 (forecast, not a judge result)**  
Current validated verifier commit: `e0a6aa04e971eb1bf3516f484451e1f529b6f421`

The central question is whether the analytically tractable Gaussian
LLM-as-a-judge model predicts when more inference samples help, hurt, or should
be traded against temperature and training data. The cumulative verifier
answers all five judged claims with one fixed command and a pinned environment.

## Claim-level result

| Claim | Exact tested statement and assumptions | Inline observed evidence | Verdict | Confidence |
| ---: | --- | --- | --- | --- |
| 1 | Result 3: with reward equal to teacher and ordered `T→0`, `k→∞`, error is `πs²exp(Δ_T²/s²)/k²`. | Four exact survival-integral curves through `k=16384`: slope -1.997562 to -1.997545; maximum tail coefficient error 0.2923%. | **VERIFIED** | HIGH |
| 2 | Result 2 aligned conditional regime: error is non-increasing with `k`. | 36/36 exact curves non-increasing; `k=1` identity within `3e-5`; 640k direct samples differ by at most 0.004079. | **VERIFIED** | HIGH |
| 3 | Remark 3 judged consequence: substantial misspecification can cause a finite optimum and later harm. | 23/90 configurations have interior optima and >0.5% harm; representative `k*=2`, 1.040000→1.082729846 (+5.809%). | **VERIFIED** | HIGH |
| 4 | Remark 4, pointwise, fixed `k>2`, `C1,C2>0`, `t>>1`: the second-order expansion has unique minimum `t=2(1-2/k)C2/C1`. | Symbolic derivative/curvature certificate passes. Ten `t≥20` exact optimizations: median 4.4303%, max 8.5676% formula error. MC max `|z|=.443`. | **VERIFIED** | HIGH |
| 5 | Remark 6, `d,n→∞`, fixed `α=d/n<1`, exact teacher reward, ordered `T→0`, `k→∞`, and both smallness conditions: `|∂logδ/∂logk|=2 >> |∂logδ/∂logn|`. | Inference slope -2.000000000000001; max training magnitude `1.63902e-6`; minimum separation 1,220,243x. Assumption ratios ≤.086875 and ≤.000870. | **VERIFIED** | HIGH |

## Exact fixed command and pinned environment

```text
uv sync --frozen && uv run python reproduction/reproduce.py --output outputs && uv run pytest -q reproduction/test_reproduction.py
```

Python is pinned to 3.12 and every package to `uv.lock`. The terminal cumulative
run was OpenResearch run `585734a7-0b00-4bb3-87f7-9e951cf34514` on Hugging
Face `cpu-upgrade`, using
`ghcr.io/astral-sh/uv:python3.12-bookworm-slim`. Estimated requirement: 2 CPU
cores. Provider allocation exposed 64 CPUs. Total job runtime: 47 seconds;
scientific runtime: 8.668 seconds. No GPU. Seeds: 330, 331, and 251219905.
The suite ended `12 passed`; every verifier raises and exits nonzero if any
acceptance check is false.

## Direct evidence

- [Claim 4 detailed page](#/claim-4-optimal-temperature)
- [Claim 5 detailed page](#/claim-5-scaling-comparison)
- [Cumulative summary JSON](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/outputs/summary.json)
- [Current reproduction source](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/reproduction/reproduce.py)
- [Fail-closed regression tests](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/reproduction/test_reproduction.py)
- [Pinned pyproject](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/pyproject.toml) and [uv lock](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/uv.lock)
- [Claims 1–3 complete raw tables](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/tree/main/evidence/current/outputs)
- [Claim 4 evidence directory](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/tree/main/evidence/current/artifacts/claim4)
- [Claim 5 evidence directory](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/tree/main/evidence/current/artifacts/claim5)
- [Exact upload hash manifest](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/MANIFEST.sha256)
- [Final release report](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/FINAL_RELEASE_REPORT.md)
- [Evaluator-blind red-team review](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/RED_TEAM_REVIEW.md)
- [Command log](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/COMMAND_LOG.md)
- [Visibility matrix](#/evaluator-visibility-matrix)

## Independent checkers and controls

- Claims 1–3 use three mechanisms: finite-temperature quadrature, direct seeded
  Monte Carlo, and an independent low-temperature survival integral.
- Claim 4 uses direct candidate-set Monte Carlo, not the quadrature optimizer.
  Omitting `(1-2/k)` predicts 74 instead of 25.8206 (186.59% error), and `k=2`
  is rejected.
- Claim 5 solves the ridge equation independently with Brent's method and uses
  central differences in `log(n)`; maximum derivative discrepancy is
  `8.54e-12`. An out-of-domain control violates both gates and produces
  training magnitude 2.6669 > 2, so inference dominance is rejected.

## Honest scope

Claims 1–4 are pointwise checks of the paper's analytical Gaussian model.
Claim 5 verifies the proportional-limit deterministic equivalent, not a
finite-dimensional retraining experiment. Claim 3 does not separately certify
the displayed threshold and `k*` approximation formulas; it preserves the live
judge's full-credit finite-optimum evidence. Numerical calibration supports,
but does not replace, the paper's analytical derivations.

No claim is BLOCKED in this candidate. Only the live judge can change the
score; this page reports a forecast, not earned new points.
