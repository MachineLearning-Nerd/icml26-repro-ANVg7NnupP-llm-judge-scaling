# Claim 4: optimal high-temperature formula

Verdict: **VERIFIED**  
Confidence: **HIGH**

## Exact contract

Remark 4 (`#Thmlemma4`, equation `#S3.E22`) is interpreted in Result 2's
high-temperature domain. Pointwise in `x`, for fixed `k>2`, `C1>0`, `C2>0`,
the second-order expansion

```text
delta_2(t) = D - (1-1/k) C1/t + (1-1/k)(1-2/k) C2/t^2
```

has its unique positive minimum at
`t*=2(1-2/k)C2/C1`. It is not treated as an exact arbitrary-temperature
identity.

## Certificate and calibration

Multiplying the derivative by positive `t^3` gives
`(1-1/k)(C1*t-2(1-2/k)C2)`. The sole positive root is the displayed `t*`;
curvature times `t*^4` is
`2(1-1/k)(1-2/k)C2>0`. Fifteen positive cases and three invalid-domain cases
pass the executable certificate.

| Eligible exact calibrations | Median relative error | Maximum relative error |
| ---: | ---: | ---: |
| 10 | 4.4303% | 8.5676% |

Eligibility is the preregistered numerical audit `predicted t>=20`. All 16
rows, including six lower-temperature rows excluded from approximation
acceptance, remain downloadable.

The independent checker samples 120,000 Gaussian candidate sets at ten fixed
temperatures with seed 251219905. For `k=10`, `Δ_R=4`, formula `t*=27.2` is
bracketed by 24 and 32, and the observed grid minimum is 24. Maximum
quadrature-versus-Monte-Carlo `|z|` is 0.443.

## Control that must fail

At `k=3`, `Δ_R=6`, removing `(1-2/k)` predicts 74 while the exact optimum is
25.820596, a 186.59% error. Calling the formula at `k=2` raises. Both intended
failures are required for a pass.

## Files

- [Verifier source](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/reproduction/claim4_verification.py)
- [Claim contract](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/artifacts/claim4/claim_contract.json)
- [Raw exact calibration CSV](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/resolve/main/evidence/current/artifacts/claim4/raw_exact_calibration.csv)
- [Raw Monte Carlo CSV](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/resolve/main/evidence/current/artifacts/claim4/raw_monte_carlo.csv)
- [Proof certificate](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/artifacts/claim4/proof_certificate.json)
- [Independent checker](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/artifacts/claim4/independent_checker.json)
- [Negative control](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/artifacts/claim4/negative_control.json)
- [Source audit](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/artifacts/claim4/source_audit.md)
- [Runtime](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/artifacts/claim4/runtime.json) and [limitations](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/artifacts/claim4/limitations_and_deviations.md)
