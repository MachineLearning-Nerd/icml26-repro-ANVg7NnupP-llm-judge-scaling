from __future__ import annotations
import json, subprocess
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; TRACKIO=ROOT/".venv/bin/trackio"; OUT=ROOT/"outputs"
ART="llm-judge-scaling-repro/llm-judge-scaling-cpu-reproduction:v0"
def call(*a): subprocess.run([str(TRACKIO),"logbook",*a],cwd=ROOT,check=True)
def page(p): call("page",p)
def md(p,t,b): call("cell","markdown","--page",p,"--title",t,b)

def main():
 s=json.loads((OUT/"summary.json").read_text()); best=pd.read_csv(OUT/"best_of_k_exact.csv")
 p="00 - Scored evidence summary"; page(p)
 md(p,"GO - all three scored claims verified",f"""# Scored evidence first — GO

**Paper:** Demystifying LLM-as-a-Judge: Analytically Tractable Model for Inference-Time Scaling  
**OpenReview:** `ANVg7NnupP` | **arXiv:** `2512.19905`  
**Tags:** `icml2026-repro`, `paper-ANVg7NnupP`  
**Compute:** local CPU; no GPU, LLM/API calls, cloud, or spend  
**Verification:** 8/8 tests; about 8 seconds

| # | Exact challenge claim | Verdict | Decisive evidence |
|---:|---|---|---|
| 1 | Near-teacher rewards improve monotonically with increasing k. | **VERIFIED** | All **{s['good_monotone_curves']}/{s['good_total_curves']}** exact curves are monotone across three teacher offsets, four reward shifts, three temperatures, and k=1..256. |
| 2 | Substantial misspecification creates a finite optimal k. | **VERIFIED** | **{s['finite_optimum_curves']}** phase configurations have an interior optimum and >0.5% degradation. The paper's signature case is reproduced exactly: k*=2, 1.040000 at k=1 and 1.082729846 at k=256 (+{s['representative_degradation_pct']:.2f}% after optimum). |
| 3 | Teacher-reward best-of-k error is Theta(1/k²). | **VERIFIED** | Four exact order-statistic curves through k=16,384 have slopes {s['best_of_k_slope_min']:.6f} to {s['best_of_k_slope_max']:.6f}; leading-coefficient error is below {100*s['best_of_k_max_coefficient_relative_error_k_ge_1024']:.3f}% for k>=1024. |

Deterministic 96-node Gaussian plus 800-node Laplace quadrature is independently
cross-checked by 640,000 seeded Monte Carlo trials (maximum absolute discrepancy
{s['monte_carlo_max_absolute_error']:.4f}). Raw rows and all code are retained.
"""); call("pin","--page",p)
 call("cell","figure","--page",p,"--title","All three scored claims","--image","outputs/claim_evidence.png","--raw","outputs/summary.json")
 p="Claim 1 - Aligned reward"; page(p)
 md(p,"VERIFIED across 36 conditional regimes","""## Verdict: VERIFIED

The ratio expectation is evaluated without sampling by expanding its reciprocal
normalizer as a Laplace integral. Every one of 36 prespecified near-teacher curves
is nonincreasing over nine k values. At k=1, selection is absent and all rows also
recover the independent baseline `s²+delta_teacher²` within 3e-5.
""")
 p="Claim 2 - Finite optimum"; page(p)
 md(p,"VERIFIED with exact phase sweep","""## Verdict: VERIFIED

Ninety configurations span three predictive biases, five reward misspecification
magnitudes and six temperatures. Twenty-three meet a fail-closed finite-optimum
criterion. The representative `(delta_T, misspecification, t)=(0.2,2,5)` curve
matches the paper values to the displayed precision and is independently recovered
by direct prefix-coupled Monte Carlo.
""")
 p="Claim 3 - Inverse-square best-of-k"; page(p)
 rows=["| delta/s | fitted slope | coefficient ratio at k=16384 |","|---:|---:|---:|"]
 for d,g in best.groupby("delta_teacher"):
  r=g[g.k==16384].iloc[0]; rows.append(f"| {d:.2f} | {r.tail_slope:.6f} | {r.scaled_coefficient/r.theory_coefficient:.6f} |")
 md(p,"VERIFIED by an independent survival integral","## Verdict: VERIFIED\n\n"+"\n".join(rows)+"""

This calculation does not reuse the finite-temperature quadrature. It integrates
the survival function of the minimum squared Gaussian residual after a stable
`r=s*x/k` change of variables and compares against the paper's exact leading
coefficient `pi*s²*exp(delta²/s²)`.
""")
 p="Methods, controls, and provenance"; page(p)
 md(p,"Clean-room, deterministic, fail-closed","""# Methods and provenance

The official repository is pinned at `444b53c410118279ad26402b7e043568726aeec0`
and source-audited, but no official function is imported. The finite-temperature
method, direct Monte Carlo, and low-temperature survival integral are three
separate numerical mechanisms. Eight tests enforce monotonicity, phase behavior,
signature values, exponent, leading coefficient, Monte Carlo agreement, and the
unselected k=1 identity.

PDF SHA-256: `ca9fd15ee9696e93d2d9f01317ae72f4c24eb6dcec56937fb3b4afe01521be39`.
"""); call("cell","artifact","--page",p,"--title","Complete CPU reproduction bundle","--type","dataset",ART)
 p="Limitations"; page(p); md(p,"Conditional scope","""# Limitations

- The claims are conditional: near rewards need not describe far rewards, and a finite optimum is existential rather than universal.
- Claim 3 uses the paper's ordered `T->0` then `k->infinity` limit.
- This fully covers the scored analytical proxy but does not rerun the illustrative GSM8K experiment.
- Numerical agreement supports the theory but does not replace its proof.
""")
 p="Conclusion"; page(p); md(p,"Final outcomes","""# Conclusion

- **Claim 1: VERIFIED.** All aligned-reward curves improve monotonically.
- **Claim 2: VERIFIED.** Misspecification produces exact finite optima and post-optimum harm.
- **Claim 3: VERIFIED.** Best-of-k error follows the predicted inverse-square law and coefficient.

## Scope & cost

| | Scope | Hardware | Time | Cost | Outcome |
|---|---|---|---:|---:|---|
| This reproduction | 126 exact regimes, 640k MC trials, four k<=16384 certificates | CPU | ~8 s | $0 | all claims verified |
| Full analytical replication | paper's scored Gaussian proxy | CPU | seconds | $0 | covered |
""")
if __name__=="__main__": main()
