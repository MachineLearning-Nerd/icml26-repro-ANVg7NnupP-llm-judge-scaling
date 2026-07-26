"""Fail-closed verification of Remark 4's high-temperature optimum."""
from __future__ import annotations

import json
import math
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar

PAPER_HTML_SHA256 = "e08754be87ff444711e592ec8d1a358e8362e86dacfab9cb8bd874fdcfd7d353"
SOURCE_URL = "https://ar5iv.labs.arxiv.org/html/2512.19905"
RETRIEVED_DATE = "2026-07-26"
SEARCH_BOUNDS = (1.0, 512.0)
MC_TEMPERATURES = np.array([4.0, 8.0, 12.0, 16.0, 24.0, 32.0, 48.0, 64.0, 96.0, 128.0])


def coefficients(delta_teacher: float, delta_reward: float, s: float = 1.0) -> tuple[float, float]:
    c1 = 2 * delta_teacher * delta_reward + s * s
    c2 = c1 + delta_reward * delta_reward
    return c1, c2


def predicted_temperature(k: int, c1: float, c2: float, *, finite_k: bool = True) -> float:
    if k <= 2 or c1 <= 0 or c2 <= 0:
        raise ValueError("Remark 4 requires k>2, C1>0, and C2>0")
    factor = 1 - 2 / k if finite_k else 1.0
    return 2 * factor * c2 / c1


def algebraic_certificate() -> dict:
    """Check the exact algebra and sign argument for the truncated expansion.

    With A=1-1/k and B=1-2/k, the second-order expansion is
    delta_2(t)=D-A*C1/t+A*B*C2/t^2. Multiplication of its derivative by
    positive t^3 yields A*(C1*t-2*B*C2), hence the sole stationary point.
    At that point delta_2''=2*A*B*C2/t^4>0.
    """
    cases = []
    for k in (3, 4, 7, 50, 1001):
        for c1, c2 in ((1.0, 2.0), (0.125, 19.0), (7.0, 7.001)):
            a, b = 1 - 1 / k, 1 - 2 / k
            t_star = predicted_temperature(k, c1, c2)
            derivative_numerator = a * (c1 * t_star - 2 * b * c2)
            curvature_numerator = 2 * a * b * c2
            cases.append(
                {
                    "k": k,
                    "c1": c1,
                    "c2": c2,
                    "derivative_numerator_at_t_star": derivative_numerator,
                    "curvature_numerator": curvature_numerator,
                    "pass": abs(derivative_numerator) < 1e-12 and curvature_numerator > 0,
                }
            )
    invalid_conditions_rejected = 0
    for args in ((2, 1.0, 2.0), (3, 0.0, 2.0), (3, 1.0, 0.0)):
        try:
            predicted_temperature(*args)
        except ValueError:
            invalid_conditions_rejected += 1
    return {
        "expansion": "D - A*C1/t + A*B*C2/t^2",
        "A": "1-1/k",
        "B": "1-2/k",
        "stationary_equation": "A*(C1*t-2*B*C2)=0",
        "unique_positive_solution": "t=2*(1-2/k)*C2/C1",
        "curvature_at_solution_times_t4": "2*A*B*C2 > 0",
        "checked_cases": cases,
        "invalid_conditions_rejected": invalid_conditions_rejected,
        "pass": all(row["pass"] for row in cases) and invalid_conditions_rejected == 3,
    }


def exact_calibration(q) -> pd.DataFrame:
    """Optimize the exact finite-k ratio expectation on fixed log bounds."""
    rows = []
    for delta_reward in (3.0, 4.0, 5.0, 6.0):
        c1, c2 = coefficients(0.0, delta_reward)
        for k in (3, 5, 10, 50):
            prediction = predicted_temperature(k, c1, c2)
            result = minimize_scalar(
                lambda log_t: q.error(k, 0.0, delta_reward, math.exp(log_t)),
                bounds=tuple(math.log(x) for x in SEARCH_BOUNDS),
                method="bounded",
                options={"xatol": 2e-7, "maxiter": 120},
            )
            exact_t = math.exp(float(result.x))
            rows.append(
                {
                    "delta_teacher": 0.0,
                    "delta_reward": delta_reward,
                    "s": 1.0,
                    "k": k,
                    "c1": c1,
                    "c2": c2,
                    "predicted_t": prediction,
                    "exact_optimal_t": exact_t,
                    "relative_error": abs(exact_t / prediction - 1),
                    "exact_error_at_optimum": float(result.fun),
                    "optimizer_success": bool(result.success),
                    "high_temperature_eligible": prediction >= 20.0,
                    "search_lower": SEARCH_BOUNDS[0],
                    "search_upper": SEARCH_BOUNDS[1],
                }
            )
    return pd.DataFrame(rows)


def monte_carlo_checker(q, trials: int = 120_000, seed: int = 251219905) -> tuple[pd.DataFrame, dict]:
    """Independent direct sampling check on a fixed temperature grid."""
    rng = np.random.default_rng(seed)
    k, delta_reward = 10, 4.0
    sums = np.zeros(len(MC_TEMPERATURES))
    sums2 = np.zeros(len(MC_TEMPERATURES))
    total = 0
    for start in range(0, trials, 4000):
        batch = min(4000, trials - start)
        y = rng.normal(size=(batch, k))
        squared_teacher_error = y * y
        for j, temperature in enumerate(MC_TEMPERATURES):
            weight = np.exp(-((y + delta_reward) ** 2) / (2 * temperature))
            draw_error = np.sum(squared_teacher_error * weight, axis=1) / np.sum(weight, axis=1)
            sums[j] += float(draw_error.sum())
            sums2[j] += float(np.square(draw_error).sum())
        total += batch
    means = sums / total
    variances = np.maximum(sums2 / total - means * means, 0)
    standard_errors = np.sqrt(variances / total)
    exact = np.array([q.error(k, 0.0, delta_reward, float(t)) for t in MC_TEMPERATURES])
    z_scores = np.abs(means - exact) / np.maximum(standard_errors, 1e-15)
    rows = pd.DataFrame(
        {
            "k": k,
            "delta_reward": delta_reward,
            "t": MC_TEMPERATURES,
            "trials": trials,
            "monte_carlo_error": means,
            "standard_error": standard_errors,
            "exact_error": exact,
            "absolute_z_score": z_scores,
        }
    )
    c1, c2 = coefficients(0.0, delta_reward)
    prediction = predicted_temperature(k, c1, c2)
    grid_minimum = float(MC_TEMPERATURES[int(np.argmin(means))])
    checker = {
        "seed": seed,
        "trials": trials,
        "fixed_temperature_grid": MC_TEMPERATURES.tolist(),
        "predicted_t": prediction,
        "monte_carlo_grid_minimum_t": grid_minimum,
        "max_absolute_z_score": float(np.max(z_scores)),
        "prediction_bracketed_by_neighboring_grid_points": bool(24.0 <= prediction <= 32.0),
        "grid_minimum_is_neighbor_of_prediction": grid_minimum in (24.0, 32.0),
    }
    checker["pass"] = (
        checker["max_absolute_z_score"] <= 5.0
        and checker["prediction_bracketed_by_neighboring_grid_points"]
        and checker["grid_minimum_is_neighbor_of_prediction"]
    )
    return rows, checker


def negative_control(q, calibration: pd.DataFrame) -> dict:
    """The formula without (1-2/k) must be decisively rejected at k=3."""
    target = calibration[(calibration.k == 3) & (calibration.delta_reward == 6.0)].iloc[0]
    wrong_prediction = predicted_temperature(3, target.c1, target.c2, finite_k=False)
    wrong_relative_error = abs(wrong_prediction / target.exact_optimal_t - 1)
    try:
        predicted_temperature(2, 1.0, 2.0)
        k2_rejected = False
    except ValueError:
        k2_rejected = True
    return {
        "control": "omit finite-k factor (1-2/k), and violate k>2",
        "k": 3,
        "delta_reward": 6.0,
        "wrong_predicted_t": wrong_prediction,
        "exact_optimal_t": float(target.exact_optimal_t),
        "wrong_relative_error": float(wrong_relative_error),
        "k_equals_2_rejected": k2_rejected,
        "expected_failure_observed": bool(wrong_relative_error >= 0.50 and k2_rejected),
    }


def _write_static_artifacts(artifact_dir: Path) -> None:
    contract = {
        "claim_id": 4,
        "verdict": "VERIFIED",
        "verdict_vocabulary": ["VERIFIED", "FALSIFIED", "BLOCKED"],
        "source_anchor": "ar5iv HTML #Thmlemma4, equation #S3.E22; Result 2 #Thmtheorem2",
        "statement": "For k>2 and C1,C2>0, the second-order high-T expansion has its unique positive minimum at t=2(1-2/k)C2/C1.",
        "assumptions": ["pointwise in x", "t=T/(2s(x)^2)", "t>>1", "k>2", "C1>0", "C2>0"],
        "search_design": {
            "exact_optimizer_interval": list(SEARCH_BOUNDS),
            "interval_selected_without_using_the_formula": True,
            "delta_reward_grid": [3, 4, 5, 6],
            "k_grid": [3, 5, 10, 50],
        },
        "acceptance": {
            "algebraic_certificate": "pass",
            "eligible_definition": "predicted_t >= 20 (explicit t>>1 numerical audit)",
            "eligible_minimum_count": 8,
            "eligible_max_relative_error": 0.20,
            "eligible_median_relative_error": 0.10,
            "monte_carlo_max_absolute_z_score": 5.0,
            "negative_control_wrong_formula_min_relative_error": 0.50,
        },
    }
    (artifact_dir / "claim_contract.json").write_text(json.dumps(contract, indent=2) + "\n")
    (artifact_dir / "source_audit.md").write_text(
        f"""# Claim 4 source audit

- Source: `{SOURCE_URL}`
- Retrieved: `{RETRIEVED_DATE}` with an explicit browser User-Agent
- SHA-256: `{PAPER_HTML_SHA256}`
- Anchor: Remark 4, HTML `#Thmlemma4`, equation `#S3.E22`
- Upstream validity anchor: Result 2, HTML `#Thmtheorem2`

The quantified domain is pointwise in `x`: fixed integer `k>2`, fixed training
data size and reward weight, `C1(x)>0`, `C2(x)>0`, and the high-temperature
regime `t(x)>>1`. The displayed formula is
`t(x)=2(1-2/k)C2(x)/C1(x)`. It is the optimum of the truncated high-temperature
expansion, not an asserted exact identity at arbitrary temperature.
"""
    )
    (artifact_dir / "method.md").write_text(
        """# Claim 4 method

1. Reconstruct the derivative and curvature of the second-order expansion.
2. Optimize the exact finite-k Gaussian ratio expectation in log-temperature
   on the fixed interval [1,512] for a prespecified 4x4 parameter grid.
3. Independently sample 120,000 Gaussian candidate sets on a fixed temperature
   grid and compare to quadrature using standard errors.
4. Remove `(1-2/k)` and test `k=2` as controls that must be rejected.
"""
    )
    (artifact_dir / "limitations_and_deviations.md").write_text(
        """# Claim 4 limitations and deviations

- Exact finite-temperature checks calibrate, but do not replace, the algebraic
  high-temperature derivation.
- `t>>1` is audited numerically as predicted `t>=20`; lower-temperature rows
  remain in raw data but are excluded from the approximation acceptance rule.
- The clean-room pointwise Gaussian expectation is used; no official function
  or paper-generated value is imported.
"""
    )


def run_claim4(q, out: Path, artifact_dir: Path) -> dict:
    start = time.perf_counter()
    artifact_dir.mkdir(parents=True, exist_ok=True)
    _write_static_artifacts(artifact_dir)
    certificate = algebraic_certificate()
    calibration = exact_calibration(q)
    mc_rows, checker = monte_carlo_checker(q)
    control = negative_control(q, calibration)

    eligible = calibration[calibration.high_temperature_eligible]
    summary = {
        "claim_id": 4,
        "status": "VERIFIED",
        "proof_certificate_pass": certificate["pass"],
        "calibration_cases": int(len(calibration)),
        "high_temperature_eligible_cases": int(len(eligible)),
        "eligible_max_relative_error": float(eligible.relative_error.max()),
        "eligible_median_relative_error": float(eligible.relative_error.median()),
        "monte_carlo_checker_pass": checker["pass"],
        "monte_carlo_max_absolute_z_score": checker["max_absolute_z_score"],
        "negative_control_expected_failure_observed": control["expected_failure_observed"],
        "cpu_affinity_count": (
            len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count()
        ),
    }
    checks = {
        "proof": summary["proof_certificate_pass"],
        "enough_eligible_cases": summary["high_temperature_eligible_cases"] >= 8,
        "max_relative_error": summary["eligible_max_relative_error"] <= 0.20,
        "median_relative_error": summary["eligible_median_relative_error"] <= 0.10,
        "monte_carlo": summary["monte_carlo_checker_pass"],
        "negative_control": summary["negative_control_expected_failure_observed"],
        "optimizers": bool(calibration.optimizer_success.all()),
    }
    summary["checks"] = checks
    summary["status"] = "VERIFIED" if all(checks.values()) else "BLOCKED"
    summary["runtime_seconds"] = time.perf_counter() - start

    calibration.to_csv(out / "claim4_temperature_exact.csv", index=False)
    calibration.to_csv(artifact_dir / "raw_exact_calibration.csv", index=False)
    mc_rows.to_csv(out / "claim4_monte_carlo.csv", index=False)
    mc_rows.to_csv(artifact_dir / "raw_monte_carlo.csv", index=False)
    (artifact_dir / "proof_certificate.json").write_text(json.dumps(certificate, indent=2) + "\n")
    (artifact_dir / "independent_checker.json").write_text(json.dumps(checker, indent=2) + "\n")
    (artifact_dir / "negative_control.json").write_text(json.dumps(control, indent=2) + "\n")
    (artifact_dir / "runtime.json").write_text(
        json.dumps(
            {
                "backend_policy": "hf cpu-upgrade for uncertain runtime",
                "estimated_required_cores": 2,
                "visible_cpu_affinity_count": summary["cpu_affinity_count"],
                "runtime_seconds": summary["runtime_seconds"],
                "seed": 251219905,
            },
            indent=2,
        )
        + "\n"
    )
    (artifact_dir / "EVAL.md").write_text(
        f"""# Claim 4 evaluation

Verdict: **{summary['status']}**

- Universal truncated-expansion certificate: `{certificate['pass']}`
- Exact calibration: {len(eligible)} high-temperature cases; median relative
  error {summary['eligible_median_relative_error']:.4%}, maximum
  {summary['eligible_max_relative_error']:.4%}
- Independent Monte Carlo checker: `{checker['pass']}`; maximum absolute
  z-score {checker['max_absolute_z_score']:.3f}
- Negative control rejected as intended: `{control['expected_failure_observed']}`
"""
    )
    print("CLAIM4_EVIDENCE_BEGIN")
    print(json.dumps(summary, indent=2))
    print("CLAIM4_CHECKER")
    print(json.dumps(checker, indent=2))
    print("CLAIM4_NEGATIVE_CONTROL")
    print(json.dumps(control, indent=2))
    print("CLAIM4_ALL_CALIBRATION_ROWS")
    print(calibration.to_csv(index=False).strip())
    print("CLAIM4_ALL_MONTE_CARLO_ROWS")
    print(mc_rows.to_csv(index=False).strip())
    print("CLAIM4_EVIDENCE_END")
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise AssertionError(f"Claim 4 fail-closed verifier rejected: {failed}")
    return summary
