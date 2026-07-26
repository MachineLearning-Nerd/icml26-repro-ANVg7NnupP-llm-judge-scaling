# Demystifying LLM-as-a-Judge — ICML 2026 reproduction

Clean-room CPU reproduction for OpenReview `ANVg7NnupP` / arXiv `2512.19905`.
It tests the three scored inference-time-scaling claims in the paper's exact
analytically tractable Gaussian predictive model—without LLM inference.

```bash
uv sync --frozen
uv run python reproduction/reproduce.py --output outputs
uv run pytest -q reproduction/test_reproduction.py
```

The run evaluates 36 aligned-reward curves and 90 reward-misspecification phase
curves by deterministic nested quadrature, cross-checks selected curves using
640,000 total independent Monte Carlo trials, and integrates exact best-of-k
order statistics through `k=16,384` for four teacher offsets.
