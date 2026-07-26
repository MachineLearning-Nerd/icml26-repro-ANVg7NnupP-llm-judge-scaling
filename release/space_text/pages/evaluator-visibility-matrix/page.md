# Evaluator visibility matrix

Traversal starts only from `README.md`, then `pages/index.md`, then the linked
current pages. No OpenResearch dashboard knowledge is required.

| Claim | Canonical page | Code visible | Data inline | Raw link | Checker | Control | Exact claim tested | Reviewer verdict |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Current verification | Yes | Yes | Yes | Survival integral | Tail-window control | Result 3 coefficient and exponent | VERIFIED |
| 2 | Current verification | Yes | Yes | Yes | 640k seeded Monte Carlo | `k=1` identity | Result 2 aligned monotonic regime | VERIFIED |
| 3 | Current verification | Yes | Yes | Yes | Prefix-coupled Monte Carlo | Aligned-reward contrast | Remark 3 finite-optimum consequence; threshold formulas explicitly limited | VERIFIED |
| 4 | Claim 4 page | Yes | Yes | Yes | Direct Monte Carlo | Wrong formula and `k=2` | Remark 4 truncated high-T optimum | VERIFIED |
| 5 | Claim 5 page | Yes | Yes | Yes | Implicit root and finite difference | Out-of-domain case | Remark 6 derivative comparison with all assumptions | VERIFIED |

## Reviewer-visible provenance

- Fixed command is inline on the current page.
- Python and dependencies are downloadable from `pyproject.toml` and `uv.lock`.
- Raw tables, certificates, checkers, controls, source audits, runtime metadata,
  and limitations are linked from the canonical pages.
- Scientific commit: `02de86848c638d3280fa89f4cff416cde9664c1e`.
- Cumulative run: `6f3196eb-7767-48ce-8c25-86fefac1f11a`, 42 seconds on
  Hugging Face `cpu-upgrade`, 64-CPU affinity visible, 8.392-second scientific
  runtime, 12/12 tests.
- Exact source HTML SHA-256:
  `e08754be87ff444711e592ec8d1a358e8362e86dacfab9cb8bd874fdcfd7d353`.

No current cell is labeled as an old rejected verifier. Previously accepted
pages remain preserved, while this matrix and the current verifier appear
first in navigation.
