# Claim 5: inference versus training-data scaling

Verdict: **VERIFIED**  
Confidence: **HIGH**

## Exact contract

Remark 6 (`#Thmlemma6`, equations `#S3.E23`, `#S3.E24`) assumes:

- `d,n→∞` with fixed `α=d/n<1`;
- exact teacher reward and ordered limits `T→0`, then `k→∞`;
- `(γ²/d)Tr(B_RΣ) << σ²`;
- renormalized ridge `R << σ²`.

Under those assumptions, the tested comparison is
`|∂logδ/∂logk|=2 >> |∂logδ/∂logn|`.
The qualitative symbols are made executable before running: each dimensionless
condition ratio must be at most 0.1 and exponent separation at least 200x.

## Observed evidence

For isotropic `Σ=S²I`, `||w||²=d`, `σ²=S²=1`, `γ²=100`, five prespecified
`α` values give:

| α | n/d | predictive ratio | ridge ratio | training exponent | separation |
| ---: | ---: | ---: | ---: | ---: | ---: |
| .005 | 200 | .005025 | .000050 | -5.075e-9 | 394,089,751x |
| .010 | 100 | .010100 | .000101 | -2.061e-8 | 97,059,700x |
| .020 | 50 | .020404 | .000204 | -8.495e-8 | 23,544,599x |
| .040 | 25 | .041649 | .000417 | -3.612e-7 | 5,536,897x |
| .080 | 12.5 | .086874 | .000869 | -1.639e-6 | 1,220,243x |

The inference exponent is -2.000000000000001. An independent Brent solution of
the implicit ridge equation plus central `log(n)` differences agrees with the
analytic derivative within `8.54e-12`.

## Control that must fail

The out-of-domain configuration `α=.2`, `σ²=.1`, `γ²=.1` has condition ratios
.1926 and 2.3852, violating both gates. Its training exponent magnitude is
2.6669, larger than the inference magnitude 2, so the verifier rejects the
dominance conclusion for the intended reason.

## Files

- [Verifier source](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/reproduction/claim5_verification.py)
- [Claim contract](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/artifacts/claim5/claim_contract.json)
- [Raw scaling CSV](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/resolve/main/evidence/current/artifacts/claim5/raw_scaling_comparison.csv)
- [Proof certificate](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/artifacts/claim5/proof_certificate.json)
- [Independent checker](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/artifacts/claim5/independent_checker.json)
- [Negative control](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/artifacts/claim5/negative_control.json)
- [Source audit](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/artifacts/claim5/source_audit.md)
- [Runtime](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/artifacts/claim5/runtime.json) and [limitations](https://huggingface.co/spaces/DineshAI/ANVg7NnupP/blob/main/evidence/current/artifacts/claim5/limitations_and_deviations.md)
