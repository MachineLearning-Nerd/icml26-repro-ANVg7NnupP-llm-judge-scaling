# Durable claim evidence

These files summarize the terminal OpenResearch runs. The fixed command for
every node was:

```text
uv sync --frozen && uv run python reproduction/reproduce.py --output outputs && uv run pytest -q reproduction/test_reproduction.py
```

The authoritative cumulative run is `585734a7-0b00-4bb3-87f7-9e951cf34514`
at Git commit `e0a6aa04e971eb1bf3516f484451e1f529b6f421`. It ran on Hugging
Face `cpu-upgrade` in 47 seconds (8.668 seconds scientific runtime), exposed
64 CPUs through affinity, and passed 12/12 tests. The workload was estimated
to need 2 cores; the larger allocation was provider-selected. No GPU was used.

Full baseline raw tables remain in `outputs/`. Claims 4 and 5 additionally
have claim-specific raw tables here. Every current verifier raises or exits
nonzero when any acceptance check fails.
