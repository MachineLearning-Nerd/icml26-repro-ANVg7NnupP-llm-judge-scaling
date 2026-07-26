# Command and environment

```text
uv sync --frozen && uv run python reproduction/reproduce.py --output outputs && uv run pytest -q reproduction/test_reproduction.py
```

Pinned Python 3.12 environment from `uv.lock`; no GPU.
