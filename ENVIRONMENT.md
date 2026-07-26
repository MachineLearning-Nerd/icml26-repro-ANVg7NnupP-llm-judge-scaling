# Environment

- Python 3.12; local CPU for the short baseline and Hugging Face
  `cpu-upgrade` for uncertain/cumulative runs; no GPU or model/API calls
- NumPy 2.3.5, SciPy 1.17.1, pandas 3.0.3, Matplotlib 3.11.0
- marimo 0.18.0 for the bounded tutorial notebook
- Environment manager: uv; project-local `.venv`; dependencies locked by
  `pyproject.toml` and `uv.lock`
- Paper PDF SHA-256: `ca9fd15ee9696e93d2d9f01317ae72f4c24eb6dcec56937fb3b4afe01521be39`
- Deterministic exact calculations plus seeded NumPy Monte Carlo
- Formal HF image: `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`
