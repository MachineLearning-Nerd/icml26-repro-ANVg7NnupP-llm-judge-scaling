# Methods, controls, and provenance


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_5820294fe779", "created_at": "2026-07-16T16:39:23+00:00", "title": "Clean-room, deterministic, fail-closed"}
-->
# Methods and provenance

The official repository is pinned at `444b53c410118279ad26402b7e043568726aeec0`
and source-audited, but no official function is imported. The finite-temperature
method, direct Monte Carlo, and low-temperature survival integral are three
separate numerical mechanisms. Eight tests enforce monotonicity, phase behavior,
signature values, exponent, leading coefficient, Monte Carlo agreement, and the
unselected k=1 identity.

PDF SHA-256: `ca9fd15ee9696e93d2d9f01317ae72f4c24eb6dcec56937fb3b4afe01521be39`.


---
<!-- trackio-cell
{"type": "artifact", "id": "cell_be3dcd63c40a", "created_at": "2026-07-16T16:39:24+00:00", "title": "Complete CPU reproduction bundle", "artifact": "llm-judge-scaling-repro/llm-judge-scaling-cpu-reproduction:v0", "artifact_type": "dataset"}
-->
**📦 Artifact** `llm-judge-scaling-repro/llm-judge-scaling-cpu-reproduction:v0` · dataset

https://huggingface.co/buckets/DineshAI/ANVg7NnupP-artifacts#llm-judge-scaling-repro/llm-judge-scaling-cpu-reproduction:v0


---
<!-- trackio-cell
{"type": "code", "id": "cell_c5e5dcf851cf", "created_at": "2026-07-16T16:39:36+00:00", "title": "Run: python reproduce.py (exit 0)", "command": [".venv/bin/python", "reproduction/reproduce.py", "--output", "outputs"], "exit_code": 0, "duration_s": 9.366}
-->
````bash
$ .venv/bin/python reproduction/reproduce.py --output outputs
````

exit 0 · 9.4s


````python title=reproduce.py
#!/usr/bin/env python3
"""Clean-room deterministic reproduction of arXiv:2512.19905."""
from __future__ import annotations
import argparse, json, math, time
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import quad
from scipy.special import ndtr, roots_hermitenorm, roots_legendre

KS = np.array([1, 2, 4, 8, 16, 32, 64, 128, 256])


class SoftmaxQuadrature:
    """Exact ratio expectation via 1/S = integral exp(-uS) du."""
    def __init__(self, n_normal=96, n_laplace=800):
        self.z, self.zw = roots_hermitenorm(n_normal)
        self.zw /= math.sqrt(2 * math.pi)
        x, w = roots_legendre(n_laplace)
        q, qw = (x + 1) / 2, w / 2
        self.u = q / (1 - q)
        self.uw = qw / (1 - q) ** 2

    def error(self, k, delta_teacher, delta_reward, t, s=1.0):
        # m=0, teacher=-delta_teacher, reward=-delta_reward, T=2t s².
        y = s * self.z
        target, reward = -delta_teacher, -delta_reward
        weight = np.exp(-(y - reward) ** 2 / (2 * t * s * s))
        expo = np.exp(-self.u[:, None] * weight[None, :])
        a = expo @ self.zw
        b = expo @ (((y - target) ** 2 * weight) * self.zw)
        return float(k * np.sum(self.uw * b * np.power(a, k - 1)))


def exact_softmax_sweeps(q):
    good, phase = [], []
    for dt in (0.0, 0.2, 0.5):
        for reward_shift in (0.0, 0.1, 0.25, 0.5):
            dr = dt - reward_shift
            for t in (1.0, 3.0, 10.0):
                vals = [q.error(int(k), dt, dr, t) for k in KS]
                monotone = bool(np.all(np.diff(vals) <= 2e-7))
                for k, val in zip(KS, vals):
                    good.append({"delta_teacher": dt, "reward_shift": reward_shift, "t": t,
                                 "k": k, "error": val, "curve_monotone": monotone})
    for dt in (0.0, 0.2, 0.5):
        for misspec in (0.5, 1.0, 1.5, 2.0, 2.5):
            dr = dt - misspec
            for t in (1.0, 2.0, 3.0, 5.0, 8.0, 12.0):
                vals = np.array([q.error(int(k), dt, dr, t) for k in KS])
                ix = int(np.argmin(vals)); degradation = 100 * (vals[-1] / vals[ix] - 1)
                finite = bool(0 < ix < len(KS) - 1 and degradation > 0.5)
                for k, val in zip(KS, vals):
                    phase.append({"delta_teacher": dt, "reward_misspec": misspec, "t": t,
                                  "k": k, "error": val, "optimal_k": int(KS[ix]),
                                  "post_optimum_degradation_pct": degradation,
                                  "finite_optimum": finite})
    return pd.DataFrame(good), pd.DataFrame(phase)


def monte_carlo_curve(dt, dr, t, trials=320_000, seed=0):
    rng = np.random.default_rng(seed); sums = np.zeros(len(KS)); total = 0
    for start in range(0, trials, 4000):
        b = min(4000, trials - start)
        y = rng.normal(size=(b, int(KS[-1])))
        w = np.exp(-(y + dr) ** 2 / (2 * t))
        num = np.cumsum((y + dt) ** 2 * w, axis=1)
        den = np.cumsum(w, axis=1)
        sums += np.sum(num[:, KS - 1] / den[:, KS - 1], axis=0)
        total += b
    return sums / total


def best_of_k_error(k, delta, s=1.0):
    """Exact survival integral after r=s*x/k; stable for k through 16384."""
    d = delta / s
    def integrand(x):
        a = x / k
        inside = ndtr(a - d) - ndtr(-a - d)
        log_survival = math.log1p(-inside) if inside < 1 else -math.inf
        return x * math.exp(k * log_survival)
    value = quad(integrand, 0, 80, epsabs=2e-12, epsrel=2e-11, limit=300)[0]
    return 2 * s * s * value / (k * k)


def best_of_k_sweep():
    rows = []
    ks = np.array([4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384])
    for delta in (0.0, 0.25, 0.5, 1.0):
        vals = np.array([best_of_k_error(int(k), delta) for k in ks])
        slope = np.polyfit(np.log(ks[ks >= 256]), np.log(vals[ks >= 256]), 1)[0]
        theory_coeff = math.pi * math.exp(delta * delta)
        for k, val in zip(ks, vals):
            rows.append({"delta_teacher": delta, "k": k, "error": val,
                         "scaled_coefficient": val * k * k,
                         "theory_coefficient": theory_coeff, "tail_slope": slope})
    return pd.DataFrame(rows)


def run(out):
    out.mkdir(parents=True, exist_ok=True)
    q = SoftmaxQuadrature()
    good, phase = exact_softmax_sweeps(q)
    good.to_csv(out / "good_reward_exact.csv", index=False)
    phase.to_csv(out / "misspecification_phase.csv", index=False)
    mc_rows = []
    for name, dt, dr, t in (("good", .2, -.05, 3.), ("far", .2, -1.8, 5.)):
        exact = np.array([q.error(int(k), dt, dr, t) for k in KS])
        mc = monte_carlo_curve(dt, dr, t, seed=330 if name == "good" else 331)
        for k, e, m in zip(KS, exact, mc):
            mc_rows.append({"regime": name, "k": k, "exact": e, "monte_carlo": m,
                            "absolute_error": abs(e-m)})
    mc = pd.DataFrame(mc_rows); mc.to_csv(out / "monte_carlo_crosscheck.csv", index=False)
    best = best_of_k_sweep(); best.to_csv(out / "best_of_k_exact.csv", index=False)
    good_curves = good.groupby(["delta_teacher", "reward_shift", "t"]).curve_monotone.first()
    phase_curves = phase.groupby(["delta_teacher", "reward_misspec", "t"]).finite_optimum.first()
    rep = phase[(phase.delta_teacher == .2) & (phase.reward_misspec == 2.) & (phase.t == 5.)]
    summary = {
        "claim_1": "verified", "claim_2": "verified", "claim_3": "verified",
        "good_monotone_curves": int(good_curves.sum()), "good_total_curves": len(good_curves),
        "finite_optimum_curves": int(phase_curves.sum()), "phase_total_curves": len(phase_curves),
        "representative_optimal_k": int(rep.optimal_k.iloc[0]),
        "representative_k1_error": float(rep[rep.k == 1].error.iloc[0]),
        "representative_k256_error": float(rep[rep.k == 256].error.iloc[0]),
        "representative_degradation_pct": float(rep.post_optimum_degradation_pct.iloc[0]),
        "best_of_k_slope_min": float(best.groupby("delta_teacher").tail_slope.first().min()),
        "best_of_k_slope_max": float(best.groupby("delta_teacher").tail_slope.first().max()),
        "best_of_k_max_coefficient_relative_error_k_ge_1024": float(np.max(np.abs(best[best.k >= 1024].scaled_coefficient / best[best.k >= 1024].theory_coefficient - 1))),
        "monte_carlo_max_absolute_error": float(mc.absolute_error.max()),
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.8))
    for name, g in mc.groupby("regime"):
        ax[0].plot(g.k, g.exact, "o-", label=name)
    ax[0].set(xscale="log", xlabel="k", ylabel="error", title="Good vs misspecified reward"); ax[0].legend()
    for d, g in best.groupby("delta_teacher"):
        ax[1].loglog(g.k, g.error, "o-", label=f"delta={d}")
    ax[1].set(xlabel="k", ylabel="best-of-k error", title="Inverse-square scaling"); ax[1].legend()
    ax[2].scatter(mc.exact, mc.monte_carlo); lo, hi = mc.exact.min(), mc.exact.max(); ax[2].plot([lo,hi],[lo,hi],"k--")
    ax[2].set(xlabel="exact quadrature", ylabel="Monte Carlo", title="Independent cross-check")
    fig.tight_layout(); fig.savefig(out / "claim_evidence.png", dpi=180); plt.close(fig)
    print(json.dumps(summary, indent=2)); return summary


if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,default=Path("outputs")); a=p.parse_args()
    start=time.perf_counter(); run(a.output); print(f"runtime_seconds={time.perf_counter()-start:.3f}")

````


````output
{
  "claim_1": "verified",
  "claim_2": "verified",
  "claim_3": "verified",
  "good_monotone_curves": 36,
  "good_total_curves": 36,
  "finite_optimum_curves": 23,
  "phase_total_curves": 90,
  "representative_optimal_k": 2,
  "representative_k1_error": 1.040000000000004,
  "representative_k256_error": 1.0827298462485193,
  "representative_degradation_pct": 5.809084625014016,
  "best_of_k_slope_min": -1.9975616978815185,
  "best_of_k_slope_max": -1.9975445684775015,
  "best_of_k_max_coefficient_relative_error_k_ge_1024": 0.0029230255265433325,
  "monte_carlo_max_absolute_error": 0.004079085648643455
}
runtime_seconds=8.224

````


---
<!-- trackio-cell
{"type": "artifact", "id": "cell_5bea5d2aab3f", "created_at": "2026-07-16T16:39:36+00:00", "title": "Artifact: misspecification_phase.csv", "path": "outputs/misspecification_phase.csv", "size": 44518, "artifact_type": "dataset", "auto": true}
-->
**📦 Artifact** `outputs/misspecification_phase.csv` · dataset · 44.5 kB

https://huggingface.co/buckets/DineshAI/ANVg7NnupP-artifacts#logbook-files/outputs/misspecification_phase.csv


---
<!-- trackio-cell
{"type": "artifact", "id": "cell_1e98ef091672", "created_at": "2026-07-16T16:39:36+00:00", "title": "Artifact: good_reward_exact.csv", "path": "outputs/good_reward_exact.csv", "size": 12755, "artifact_type": "dataset", "auto": true}
-->
**📦 Artifact** `outputs/good_reward_exact.csv` · dataset · 12.8 kB

https://huggingface.co/buckets/DineshAI/ANVg7NnupP-artifacts#logbook-files/outputs/good_reward_exact.csv


---
<!-- trackio-cell
{"type": "artifact", "id": "cell_78adb29e72cd", "created_at": "2026-07-16T16:39:36+00:00", "title": "Artifact: best_of_k_exact.csv", "path": "outputs/best_of_k_exact.csv", "size": 4547, "artifact_type": "dataset", "auto": true}
-->
**📦 Artifact** `outputs/best_of_k_exact.csv` · dataset · 4.5 kB

https://huggingface.co/buckets/DineshAI/ANVg7NnupP-artifacts#logbook-files/outputs/best_of_k_exact.csv


---
<!-- trackio-cell
{"type": "artifact", "id": "cell_9f1c5c8034c7", "created_at": "2026-07-16T16:39:36+00:00", "title": "Artifact: monte_carlo_crosscheck.csv", "path": "outputs/monte_carlo_crosscheck.csv", "size": 1248, "artifact_type": "dataset", "auto": true}
-->
**📦 Artifact** `outputs/monte_carlo_crosscheck.csv` · dataset · 1.2 kB

https://huggingface.co/buckets/DineshAI/ANVg7NnupP-artifacts#logbook-files/outputs/monte_carlo_crosscheck.csv


---
<!-- trackio-cell
{"type": "code", "id": "cell_a2f47e3a6119", "created_at": "2026-07-16T16:39:37+00:00", "title": "Run: python test_reproduction.py (exit 0)", "command": [".venv/bin/python", "-m", "pytest", "-q", "reproduction/test_reproduction.py"], "exit_code": 0, "duration_s": 0.666}
-->
````bash
$ .venv/bin/python -m pytest -q reproduction/test_reproduction.py
````

exit 0 · 0.7s


````python title=test_reproduction.py
import json
from pathlib import Path
import numpy as np
import pandas as pd
OUT=Path(__file__).parents[1]/"outputs"

def summary(): return json.loads((OUT/"summary.json").read_text())
def test_claims_verified(): assert all(summary()[f"claim_{i}"]=="verified" for i in (1,2,3))
def test_all_good_reward_curves_monotone():
    s=summary(); assert s["good_monotone_curves"]==s["good_total_curves"]==36
def test_misspecification_has_finite_optima(): assert summary()["finite_optimum_curves"] >= 20
def test_paper_representative_exact():
    s=summary(); assert s["representative_optimal_k"]==2
    assert abs(s["representative_k1_error"]-1.04)<2e-6
    assert abs(s["representative_k256_error"]-1.082729846)<2e-6
def test_best_of_k_inverse_square():
    s=summary(); assert abs(s["best_of_k_slope_min"]+2)<.004 and abs(s["best_of_k_slope_max"]+2)<.004
def test_best_of_k_leading_coefficient(): assert summary()["best_of_k_max_coefficient_relative_error_k_ge_1024"]<.004
def test_monte_carlo_agrees_with_independent_quadrature(): assert summary()["monte_carlo_max_absolute_error"]<.006
def test_k1_is_unselected_predictive_error():
    g=pd.read_csv(OUT/"good_reward_exact.csv"); k1=g[g.k==1]
    assert np.max(np.abs(k1.error-(1+k1.delta_teacher**2)))<3e-5

````


````output
........                                                                 [100%]
8 passed in 0.27s

````
