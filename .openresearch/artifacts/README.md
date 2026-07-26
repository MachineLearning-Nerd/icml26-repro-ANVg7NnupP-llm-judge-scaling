# Durable claim evidence

These files summarize the terminal OpenResearch runs. The fixed command for
every node was:

```text
uv sync --frozen && uv run python reproduction/reproduce.py --output outputs && uv run pytest -q reproduction/test_reproduction.py
```

The authoritative cumulative run is `6f3196eb-7767-48ce-8c25-86fefac1f11a`
at Git commit `02de86848c638d3280fa89f4cff416cde9664c1e`. It ran on Hugging
Face `cpu-upgrade` in 42 seconds (8.392 seconds scientific runtime), exposed
64 CPUs through affinity, and passed 12/12 tests. The workload was estimated
to need 2 cores; the larger allocation was provider-selected. No GPU was used.

Full baseline raw tables remain in `outputs/`. Claims 4 and 5 additionally
have claim-specific raw tables here. Every current verifier raises or exits
nonzero when any acceptance check fails.
