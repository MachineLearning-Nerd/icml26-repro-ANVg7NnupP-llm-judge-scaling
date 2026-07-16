# Source audit

## Primary sources

- Paper: arXiv:2512.19905, PDF SHA-256 `ca9fd15ee9696e93d2d9f01317ae72f4c24eb6dcec56937fb3b4afe01521be39`
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

The implementation uses the independent identity `1/S = integral exp(-uS) du`
to reduce the ratio expectation to Gaussian and Laplace quadrature. Best-of-k is
separately computed from the survival function of the minimum absolute Gaussian
residual. Neither official Python file is imported.

## Scope

The scored claims concern the solvable Bayesian-regression proxy, which is fully
covered. The paper's illustrative GSM8K/model experiment is not rerun and is not
used as evidence. Numerical checks support the claims within their stated
conditional regimes and do not replace the theoretical proofs.

