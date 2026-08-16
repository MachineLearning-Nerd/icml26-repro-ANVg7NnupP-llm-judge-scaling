# Claim-to-evidence production map

Each claim follows the same auditable path:

paper statement → explicit domain contract → deterministic producer → raw
CSV/JSON → independent checker → intended-failure control → scoped verdict

The claim-specific packages under .openresearch/artifacts are the durable
record. outputs/ contains the complete raw tables produced by the cumulative
runner.

## Summary

| Claim | Contract | Producer | Raw evidence | Independent check and control | Verdict |
|---|---|---|---|---|---|
| 1 | Result 3, ordered teacher-reward best-of-k limit | reproduction/reproduce.py best_of_k_sweep plus independent survival integral | outputs/best_of_k_exact.csv and claim1 raw_results.json | Independent survival-integral mechanism; pre-asymptotic tail control | VERIFIED, scoped |
| 2 | Result 2, aligned conditional monotonic regime | SoftmaxQuadrature exact sweeps and seeded Monte Carlo | outputs/good_reward_exact.csv and monte_carlo_crosscheck.csv | 640,000 direct trials; k = 1 identity control | VERIFIED, scoped |
| 3 | Remark 3, finite optimum under misspecification | Exact phase sweep and prefix-coupled Monte Carlo | outputs/misspecification_phase.csv | Representative direct Monte Carlo; near-teacher monotonic contrast | VERIFIED, scoped |
| 4 | Remark 4 and Result 2 high-temperature contract | reproduction/claim4_verification.py | claim4 raw exact calibration and Monte Carlo CSVs | Symbolic certificate, independent 120,000-trial checker, wrong-formula and k = 2 controls | VERIFIED, scoped calibration |
| 5 | Remark 6 and Remark 5 proportional-limit derivative comparison | reproduction/claim5_verification.py | claim5 raw scaling comparison CSV | Independent Brent root and finite-difference checker; out-of-domain control | VERIFIED, proportional-limit scope |

## Claim 1 — teacher-reward best-of-k

The runner computes the exact survival-function integral for the minimum
squared Gaussian residual at four teacher offsets and 13 k values through
16,384. It fits the large-k log-log slope and compares delta times k squared
with the paper’s leading coefficient.

- Producer: reproduction/reproduce.py, best_of_k_error and best_of_k_sweep.
- Raw table: outputs/best_of_k_exact.csv.
- Contract: .openresearch/artifacts/claim1/claim_contract.json.
- Independent mechanism: .openresearch/artifacts/claim1/independent_checker.json
  records the rescaled survival integral, independent of the finite-temperature
  ratio quadrature and Monte Carlo.
- Negative control: .openresearch/artifacts/claim1/negative_control.json
  requires the pre-asymptotic coefficient error to be larger than the tail
  acceptance window.
- Result: slopes range from −1.9975616979 to −1.9975445685; maximum coefficient
  error at k >= 1,024 is 0.0029230255.
- Limitation: a numerical certificate for the analytical pointwise model and
  ordered limit, not a proof or an LLM benchmark.

## Claim 2 — aligned-reward monotonicity

The exact producer evaluates 36 prespecified combinations of teacher offset,
reward shift, temperature, and k. The output is independently checked with
prefix-coupled seeded Monte Carlo on aligned and far-reward curves.

- Producer: reproduction/reproduce.py, SoftmaxQuadrature and exact_softmax_sweeps.
- Raw tables: outputs/good_reward_exact.csv and
  outputs/monte_carlo_crosscheck.csv.
- Contract: .openresearch/artifacts/claim2/claim_contract.json.
- Structural control: k = 1 must equal unselected predictive error independent
  of reward; maximum observed identity error is 0.00003.
- Independent checker: 640,000 seeded trials, seeds 330 and 331; maximum
  absolute discrepancy is 0.0040790856 against a 0.006 threshold.
- Negative control: .openresearch/artifacts/claim2/negative_control.json.
- Limitation: 36 declared pointwise conditional regimes do not establish a
  universal alignment region.

## Claim 3 — finite optimum under reward misspecification

The exact phase producer sweeps 90 declared misspecification configurations.
An interior optimum counts only when later k values increase error by more than
0.5%. A representative curve is checked by prefix-coupled Monte Carlo.

- Producer: reproduction/reproduce.py, exact_softmax_sweeps.
- Raw table: outputs/misspecification_phase.csv.
- Contract: .openresearch/artifacts/claim3/claim_contract.json.
- Independent checker: .openresearch/artifacts/claim3/independent_checker.json.
- Contrast control: near-teacher aligned curves remain non-increasing.
- Result: 23/90 configurations have finite optima; the representative has
  k* = 2 and 5.809084625% later degradation.
- Limitation: the separate threshold t < 3C2/C1 and approximate k* formula are
  explicitly not certified by this package.

## Claim 4 — optimal high-temperature temperature

The verifier first reconstructs the derivative and curvature of the truncated
second-order expansion, then optimizes the exact finite-k Gaussian ratio
expectation on a fixed log-temperature interval and fixed 4x4 grid. Ten rows
with predicted t >= 20 enter calibration acceptance; lower-temperature rows
remain visible but are excluded from the high-temperature claim.

- Producer/checker: reproduction/claim4_verification.py.
- Contract: .openresearch/artifacts/claim4/claim_contract.json.
- Raw exact calibration: .openresearch/artifacts/claim4/raw_exact_calibration.csv.
- Raw Monte Carlo: .openresearch/artifacts/claim4/raw_monte_carlo.csv.
- Certificate: .openresearch/artifacts/claim4/proof_certificate.json.
- Independent check: seed 251219905, 120,000 candidate sets, maximum absolute
  z-score 0.4429977152.
- Controls: omit the finite-k factor to produce a 186.59% error and reject k=2.
- Result: 15 positive certificate cases, 3 invalid cases rejected, median
  calibration error 4.4303%, maximum 8.5676%.
- Limitation: calibration of a truncated expansion, not an exact
  arbitrary-temperature identity.

## Claim 5 — inference versus training-data scaling

The verifier factorizes the Remark 5 error expression as C(alpha) times k^-2,
reconstructs the ridge from its closed form and implicit deterministic-
equivalent equation, and independently checks the training derivative with a
Brent root and central differences in log(n). Five prespecified alpha values
are audited.

- Producer/checker: reproduction/claim5_verification.py.
- Contract: .openresearch/artifacts/claim5/claim_contract.json.
- Raw table: .openresearch/artifacts/claim5/raw_scaling_comparison.csv.
- Certificate: .openresearch/artifacts/claim5/proof_certificate.json.
- Independent checker: .openresearch/artifacts/claim5/independent_checker.json;
  maximum slope discrepancy is 8.5433607e-12.
- Controls: .openresearch/artifacts/claim5/negative_control.json violates both
  smallness assumptions and must reject inference dominance.
- Result: inference slope −2.000000000000001; maximum training-slope magnitude
  1.63902e-6; minimum accepted separation 1,220,243x.
- Limitation: proportional-limit deterministic equivalent, not finite-dimensional
  retraining; the qualitative << and >> are explicit gates of 0.1 and 200x.

## Published release evidence

release/space_text is the text-only Space candidate that was published in one
additive update. release/release_pipeline.py protects the parent tree, checks
the allowlist and hashes, traverses all links from the README, and requires
all five current claim pages and raw/checker evidence to be discoverable.
release/postpublication_verification.md records the fresh download audit:
20/20 protected paths and 80/80 upload hashes passed. The recorded live score
remains 6/10 because no new judge result is claimed.
