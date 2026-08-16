# Demystifying LLM-as-a-Judge: Inference-Time Scaling

Independent ICML 2026 evidence audit for **Demystifying LLM-as-a-Judge:
Analytically Tractable Model for Inference-Time Scaling** by Indranil Halder
and Cengiz Pehlevan.

- Paper: arXiv 2512.19905v2
- OpenReview submission: ANVg7NnupP
- Repository: https://github.com/MachineLearning-Nerd/icml26-llm-judge-inference-scaling
- Historical evaluator space: https://huggingface.co/spaces/DineshAI/ANVg7NnupP
- Code status: independent clean-room reproduction of the paper’s analytical
  Gaussian proxy; the official repository is recorded in SOURCE_AUDIT.md but
  its Python files are not imported

The collection status is **VERIFIED_SCOPED_WITH_LIVE_SCORE_PENDING**. All five
current claim contracts pass their committed scientific checks. The previous
live evaluator score remains 6/10; the published evidence package is awaiting
a new live judge, so no score increase is claimed here.

## Current claim results

| Claim | Paper result audited | Current verdict | Evidence summary |
|---|---|---|---|
| 1 | Result 3, teacher-reward best-of-k | VERIFIED, scoped | Exact survival-integral curves through k = 16,384; tail slopes −1.997562 to −1.997545 and maximum coefficient error 0.2923% for k ≥ 1,024. |
| 2 | Result 2, aligned-reward monotonicity | VERIFIED, scoped | 36/36 declared curves are non-increasing; k = 1 identity error is at most 0.00003; independent 640,000-trial Monte Carlo error is at most 0.004079. |
| 3 | Remark 3, finite optimum under misspecification | VERIFIED, scoped | 23/90 configurations have an interior optimum with later harm; representative k* = 2 changes error from 1.040000 to 1.082730, a 5.809% degradation. |
| 4 | Remark 4, high-temperature optimal temperature | VERIFIED, scoped calibration | Symbolic certificate passes; 10 eligible high-temperature calibrations have 4.4303% median and 8.5676% maximum relative error; independent Monte Carlo maximum absolute z-score is 0.443. |
| 5 | Remark 6, inference versus training-data scaling | VERIFIED, proportional-limit scope | Inference log-slope −2.000000000000001, maximum training-slope magnitude 1.639e−6, and minimum separation 1,220,243× after both smallness assumptions pass. |

These are scoped numerical and symbolic audits of the paper’s Bayesian
regression proxy. They are not a new proof of the paper, a finite-dimensional
retraining study, or an LLM benchmark reproduction. Claim 3 explicitly does
not certify the separate threshold and k* approximation formulas. Claim 4
treats the high-temperature expression as the optimizer of the truncated
expansion, not as an arbitrary-temperature identity. Claim 5 is a
proportional-limit deterministic-equivalent audit, not finite-dimensional
training.

## Historical evaluator boundary

The historical record is kept separate from the current evidence:

- Previous live score: 6/10
- Protected judged parent: 888e34394f08123538bccdaba0e8852558a5b724
- Published evidence revision: e243be8375bd6139647f40f9b114ab1d59c9eaf2
- Publication mode: one additive text-only update to the existing Space
- Post-publication audit: passed; 20/20 protected paths preserved and 80/80
  upload hashes matched
- Current state: awaiting a new live judge; score remains 6/10

The forecast in the historical release report is not an earned result.

## Reproduce the evidence

The validated cumulative run used a pinned uv environment and one fixed command:

~~~bash
uv sync --frozen
uv run python reproduction/reproduce.py --output outputs
uv run pytest -q reproduction/test_reproduction.py
~~~

The suite covers the baseline curves plus the Claim 4 and Claim 5 contracts,
independent checkers, and intended-failure controls. The validated cumulative
run passed 13/13 tests, used 8.668 seconds of scientific runtime and 47
seconds total on a Hugging Face cpu-upgrade environment. No GPU or model/API
call was used.

The evaluator-visible release audit is also runnable locally:

~~~bash
uv run python release/audit_candidate.py
~~~

For the interactive explanation:

~~~bash
uv run marimo edit notebooks/llm_judge_scaling.py
~~~

## Repository map

- paper.pdf — local paper copy used by the source audit.
- reproduction/reproduce.py — analytical quadrature, best-of-k, misspecification,
  and claim-specific orchestration.
- reproduction/test_reproduction.py — fail-closed regression suite.
- reproduction/claim4_verification.py — Remark 4 contract, certificate,
  calibration, independent checker, and controls.
- reproduction/claim5_verification.py — Remark 6 contract, derivative audit,
  independent checker, and out-of-domain control.
- outputs/ — complete raw CSV tables and cumulative summary.
- .openresearch/artifacts/claim1 through claim5 — contracts, methods, raw
  evidence pointers, checkers, controls, source audits, runtimes, and limits.
- release/space_text/ — evaluator-visible pages and navigation for the
  published text-only Space update.
- release/final_release_report.md — historical release decision and forecast.
- release/postpublication_verification.md — published revision audit.
- reports/claim-complete/report.md — illustrated technical report.
- notebooks/llm_judge_scaling.py — self-contained marimo walkthrough.
- STATUS.md, claims.md, CLAIM_EVIDENCE.md — current state and production map.
- BRANCH_AUDIT.md, SOURCE_MANIFEST.md, CITATION.cff, EVIDENCE_MANIFEST.json —
  migration, provenance, citation, and machine-readable evidence metadata.

## Branches

Public branches use descriptive names. The legacy OpenResearch-style names and
their exact source tips are recorded in BRANCH_AUDIT.md.

| Branch | Purpose |
|---|---|
| main | Canonical five-claim evidence collection and documentation. |
| baseline/judged-6-of-10 | Frozen historical evaluator baseline for Claims 1–3. |
| audit/claim-4-temperature | Remark 4 exact temperature contract and calibration. |
| audit/claim-5-data-scaling | Remark 6 proportional-limit scaling contract. |
| release/evaluator-visible | Cumulative evaluator-visible raw evidence. |
| release/candidate-blind-audit | Release candidate, blind traversal, and fail-closed audit. |
| release/publication-manifest | Published revision manifest and post-publication verification. |

## Citation

~~~bibtex
@article{halder2026demystifying,
  title   = {Demystifying LLM-as-a-Judge: Analytically Tractable Model for Inference-Time Scaling},
  author  = {Halder, Indranil and Pehlevan, Cengiz},
  journal = {arXiv preprint arXiv:2512.19905},
  year    = {2026},
  url     = {https://arxiv.org/abs/2512.19905}
}
~~~

Please cite the paper when using its theory or this reproduction. The
repository’s software citation is also provided in CITATION.cff.

## Thank you

Thank you to Indranil Halder and Cengiz Pehlevan for developing and sharing an
analytically tractable model that makes inference-time scaling questions
precise. The paper’s explicit assumptions, asymptotic regimes, and reward
temperature structure make a careful independent audit possible. This
repository is an independent reproduction and audit, not an official
implementation or endorsement by the authors.

## Scope and limitations

The committed evidence supports the listed claims within their stated
contracts. It does not reproduce the paper’s illustrative GSM8K/model
experiments, infer unspecified finite-dimensional training behavior, or turn
finite numerical checks into universal proofs. The live evaluator, not this
repository, determines any future score.
