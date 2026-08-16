# Five-claim audit contract

The current contract follows the evaluator-facing claim numbering and makes
each theorem’s assumptions and evidence boundary explicit.

## Claim 1 — Result 3: teacher-reward best-of-k

With reward equal to the teacher, temperature tending to zero before k tends
to infinity, the pointwise Gaussian proxy predicts

delta(x) ~ pi s(x)^2 exp(Delta_T(x)^2 / s(x)^2) / k^2.

Verdict: VERIFIED, scoped. An independent survival-function integral evaluates
four teacher offsets through k = 16,384. Tail slopes range from
−1.9975616979 to −1.9975445685, and the largest leading-coefficient relative
error for k >= 1,024 is 0.0029230255.

Limitation: this is a numerical certificate for the analytical proxy and
ordered limit, not a replacement for the proof or an LLM benchmark.

## Claim 2 — Result 2: aligned-reward monotonicity

When the reward is sufficiently aligned with the teacher in the tested
high-temperature conditional Gaussian regime, generalization error should not
increase as the number of inference samples k grows.

Verdict: VERIFIED, scoped. All 36 prespecified curves are non-increasing. The
k = 1 structural identity has maximum error 0.00003, and independent
640,000-trial Monte Carlo differs from quadrature by at most 0.004079.

Limitation: the sweep is pointwise over declared conditional regimes and does
not establish a universal alignment region.

## Claim 3 — Remark 3: finite optimum under misspecification

Sufficient reward misspecification can make error non-monotone in k, producing
a finite optimum after which additional sampling harms performance.

Verdict: VERIFIED, scoped. Twenty-three of 90 prespecified configurations have
interior optima with more than 0.5% later degradation. The representative
configuration has delta_teacher = 0.2, reward misspecification = 2.0,
temperature t = 5.0, k* = 2, and 5.809084625% degradation by k = 256.

Limitation: the displayed threshold t < 3C2/C1 and approximation
k* ≈ 2t*/(t*−t) are not separately certified.

## Claim 4 — Remark 4: high-temperature optimal temperature

For fixed k > 2, C1 > 0, C2 > 0, and t >> 1, the second-order
high-temperature expansion has its unique positive minimum at

t* = 2(1 − 2/k) C2/C1.

Verdict: VERIFIED, scoped calibration. The derivative/curvature certificate
passes 15 positive and rejects 3 invalid cases. Ten eligible cases with
predicted t >= 20 have 4.4303% median and 8.5676% maximum relative error
against exact finite-temperature optimization; the independent 120,000-trial
checker has maximum absolute z-score 0.443.

Limitation: the calibration tests the truncated expansion in the declared
high-temperature domain; it is not an exact arbitrary-temperature identity.

## Claim 5 — Remark 6: inference versus training-data scaling

In the proportional limit with fixed alpha = d/n < 1, exact teacher reward,
ordered low-temperature/best-of-k limits, and both smallness conditions, the
magnitude of the inference log-slope is 2 and dominates the training-data
log-slope.

Verdict: VERIFIED, proportional-limit scope. Five prespecified alpha values
satisfy condition ratios at most 0.1 and separation at least 200x. The
inference slope is −2.000000000000001; the maximum training-slope magnitude is
1.63902e−6; and the independent root/finite-difference discrepancy is
8.54e−12.

Limitation: this is a deterministic-equivalent audit, not finite-dimensional
retraining. The qualitative << and >> assumptions are operationalized as
explicit acceptance gates.
