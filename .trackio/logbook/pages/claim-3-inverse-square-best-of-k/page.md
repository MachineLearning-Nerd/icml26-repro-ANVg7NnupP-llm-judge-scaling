# Claim 3 - Inverse-square best-of-k


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_a7232ee6b969", "created_at": "2026-07-16T16:39:22+00:00", "title": "VERIFIED by an independent survival integral"}
-->
## Verdict: VERIFIED

| delta/s | fitted slope | coefficient ratio at k=16384 |
|---:|---:|---:|
| 0.00 | -1.997562 | 0.999817 |
| 0.25 | -1.997562 | 0.999817 |
| 0.50 | -1.997561 | 0.999817 |
| 1.00 | -1.997545 | 0.999817 |

This calculation does not reuse the finite-temperature quadrature. It integrates
the survival function of the minimum squared Gaussian residual after a stable
`r=s*x/k` change of variables and compares against the paper's exact leading
coefficient `pi*s²*exp(delta²/s²)`.
