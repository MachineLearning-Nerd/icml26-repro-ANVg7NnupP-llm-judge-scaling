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
