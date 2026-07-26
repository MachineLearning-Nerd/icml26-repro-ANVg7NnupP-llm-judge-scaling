# Source audit

## Primary sources

- Paper HTML: `https://ar5iv.labs.arxiv.org/html/2512.19905`, retrieved
  2026-07-26 with an explicit browser User-Agent, SHA-256
  `e08754be87ff444711e592ec8d1a358e8362e86dacfab9cb8bd874fdcfd7d353`
- Paper PDF: arXiv:2512.19905, SHA-256
  `ca9fd15ee9696e93d2d9f01317ae72f4c24eb6dcec56937fb3b4afe01521be39`
- Official repository: `I-Halder/Demystifying-LLM-as-a-Judge-Analytically-Tractable-Model-for-Inference-Time-Scaling`
- Pinned commit: `444b53c410118279ad26402b7e043568726aeec0`
- `BLR_non_zero_T.py`: SHA-256 `d1164b306d45d0f2eead1b590cad6e1e3c5a086732160f865074140b894a79c9`
- `BLR_zero_T.py`: SHA-256 `e00ee396b844526482dece6de47c3d8ffb26491d84899cee15c63dccb2646fad`

## Equation mapping

- Result 1 defines generalization error as the expectation of a softmax-weighted
  squared teacher error over `k` Gaussian posterior-predictive samples.
- Result 2 and Remark 3 predict monotone improvement near the teacher and a
  finite optimum under sufficient misspecification.
- Result 3 predicts teacher-reward best-of-k error
  `pi*s²*exp(delta²/s²)/k²` in the ordered low-temperature, large-k limit.
- Remark 4 (`#Thmlemma4`, equation `#S3.E22`) gives the fixed-`k>2`
  high-temperature optimum `t=2(1-2/k)C2/C1`.
- Remark 6 (`#Thmlemma6`, equations `#S3.E23`–`#S3.E24`) compares local
  log-derivatives in the proportional limit under two explicit smallness
  conditions.

The implementation uses the independent identity `1/S = integral exp(-uS) du`
to reduce the ratio expectation to Gaussian and Laplace quadrature. Best-of-k is
separately computed from the survival function of the minimum absolute Gaussian
residual. Neither official Python file is imported.

## Scope

The judged claims concern the solvable Bayesian-regression proxy. The paper's
illustrative GSM8K/model experiment is not rerun and is not used as evidence.
Claim 5 verifies the proportional-limit deterministic equivalent, not a
finite-dimensional training curve. Numerical checks support claims within
their stated regimes and do not replace theoretical proofs.
