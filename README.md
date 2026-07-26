# Demystifying LLM-as-a-Judge — claim-complete CPU reproduction

[![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/MachineLearning-Nerd/icml26-repro-ANVg7NnupP-llm-judge-scaling/blob/main/notebooks/llm_judge_scaling.py)

This clean-room reproduction tests all five judged claims in
[arXiv:2512.19905](https://arxiv.org/abs/2512.19905), including the two missing
from the previous 6/10 logbook: Remark 4's optimal high-temperature formula and
Remark 6's inference-versus-training-data scaling comparison.

The result is **VERIFIED** for both exact contracts. Claim 4's symbolic
certificate passes; among ten eligible high-temperature cases, the predicted
temperature differs from the exact finite-`k` optimum by 4.43% median and 8.57%
maximum, with an independent Monte Carlo maximum `|z|` of 0.443. Claim 5 gives
inference slope -2.000000000000001 versus maximum training-slope magnitude
`1.639e-6`, at least 1.22 million times smaller after auditing both assumptions.
The previously accepted Claims 1–3 still pass.

This is the paper's analytical Gaussian proxy, not an LLM benchmark or a
finite-dimensional retraining experiment. Claim 5 uses the stated proportional
limit; Claim 4 calibrates the truncated high-temperature expansion. Compute was
CPU-only: one short local baseline, followed by Hugging Face `cpu-upgrade` for
uncertain/cumulative runs; no GPU.

Read the [illustrated technical report](reports/claim-complete/report.md) or the
[self-contained marimo tutorial](notebooks/llm_judge_scaling.py).

## Experiment log

| Branch / experiment | Purpose or change | Exact run command | Assessment / outcome | Compute |
| --- | --- | --- | --- | --- |
| `main` | Public landing page and release surface | Not run as an experiment (publication surface) | Presentation only | None |
| [`orx/frozen-validated-baseline`](https://github.com/MachineLearning-Nerd/icml26-repro-ANVg7NnupP-llm-judge-scaling/tree/orx/frozen-validated-baseline) | Freeze and reproduce judged Claims 1–3 in the pinned uv environment | `uv sync --frozen && uv run python reproduction/reproduce.py --output outputs && uv run pytest -q reproduction/test_reproduction.py` | 8/8 tests; existing three claims preserved | Local CPU, 1 effective core, 1m10s total |
| [`orx/claim-4-exact-temperature-contract`](https://github.com/MachineLearning-Nerd/icml26-repro-ANVg7NnupP-llm-judge-scaling/tree/orx/claim-4-exact-temperature-contract) | Add exact Remark 4 contract, certificate, calibration, checker, and controls | `uv sync --frozen && uv run python reproduction/reproduce.py --output outputs && uv run pytest -q reproduction/test_reproduction.py` | VERIFIED; 10/10 tests | HF `cpu-upgrade`, 37s |
| [`orx/claim-5-inference-versus-data-scaling`](https://github.com/MachineLearning-Nerd/icml26-repro-ANVg7NnupP-llm-judge-scaling/tree/orx/claim-5-inference-versus-data-scaling) | Add exact Remark 6 proportional-limit reconstruction and controls | `uv sync --frozen && uv run python reproduction/reproduce.py --output outputs && uv run pytest -q reproduction/test_reproduction.py` | VERIFIED; 12/12 tests | HF `cpu-upgrade`, 42s |
| [`orx/release-candidate-and-blind-audit`](https://github.com/MachineLearning-Nerd/icml26-repro-ANVg7NnupP-llm-judge-scaling/tree/orx/release-candidate-and-blind-audit) | Package durable evidence, canonical pages, report, notebook, and blind audit | `uv sync --frozen && uv run python reproduction/reproduce.py --output outputs && uv run pytest -q reproduction/test_reproduction.py` | Release gate pending final cumulative run | HF `cpu-upgrade` |

## Reproduce

```bash
uv sync --frozen
uv run python reproduction/reproduce.py --output outputs
uv run pytest -q reproduction/test_reproduction.py
```

The run evaluates 36 aligned-reward curves and 90 reward-misspecification phase
curves by deterministic nested quadrature, cross-checks selected curves using
640,000 total independent Monte Carlo trials, and integrates exact best-of-k
order statistics through `k=16,384` for four teacher offsets.

For the interactive explanation:

```bash
uv run marimo edit notebooks/llm_judge_scaling.py
uv run marimo run notebooks/llm_judge_scaling.py
```
