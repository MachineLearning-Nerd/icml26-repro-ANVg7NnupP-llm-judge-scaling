# Claim 4 command and environment

```text
uv sync --frozen && uv run python reproduction/reproduce.py --output outputs && uv run pytest -q reproduction/test_reproduction.py
```

Python 3.12, exact dependencies from `uv.lock`, official image
`ghcr.io/astral-sh/uv:python3.12-bookworm-slim`, Hugging Face
`cpu-upgrade`, no GPU.
