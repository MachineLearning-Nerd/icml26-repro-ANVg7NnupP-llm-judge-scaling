# Paper source audit

## Primary source

- Title: Demystifying LLM-as-a-Judge: Analytically Tractable Model for
  Inference-Time Scaling
- Authors: Indranil Halder and Cengiz Pehlevan
- arXiv: https://arxiv.org/abs/2512.19905
- Local version: v2, 11 February 2026
- Primary HTML: https://ar5iv.labs.arxiv.org/html/2512.19905
- HTML retrieved: 2026-07-26 with an explicit browser User-Agent
- Primary HTML SHA-256: e08754be87ff444711e592ec8d1a358e8362e86dacfab9cb8bd874fdcfd7d353
- Local PDF: paper.pdf
- PDF SHA-256: ca9fd15ee9696e93d2d9f01317ae72f4c24eb6dcec56937fb3b4afe01521be39
- Pages: 11
- Official repository: I-Halder/Demystifying-LLM-as-a-Judge-Analytically-Tractable-Model-for-Inference-Time-Scaling
- Official pinned commit: 444b53c410118279ad26402b7e043568726aeec0

The official repository and two source files were audited for provenance, but
this collection’s producers are clean-room code and do not import those
Python files. The paper’s realistic GSM8K/model experiment is outside the
current reproduction scope.

## Claim anchors

- Result 1, equations 9–13: deterministic-equivalent Gaussian posterior
  predictive and reward-weighted sampling model.
- Result 2, equation 15: high-temperature expansion and aligned-reward
  monotonic regime.
- Remark 2, equation 18: optimal reward can differ from the teacher.
- Remark 3, equations 20–21: finite optimum under reward misspecification.
- Result 3, equation 17: teacher-reward best-of-k inverse-square asymptotic.
- Remark 4, equation S3.E22: fixed-k high-temperature temperature optimum.
- Remark 6, equations S3.E23–S3.E24: inference-versus-training-data
  derivative comparison.
- Result 1 equations 10–13: posterior predictive quantities and ridge
  definitions used by Claim 5.

## Interpretation

The tested claims concern the solvable Bayesian-regression proxy and its
stated asymptotic or high-temperature domains. The numerical results are
evidence within those contracts. They do not replace the paper’s proofs,
expand the quantifiers beyond the declared regimes, or certify the
illustrative LLM experiments.
