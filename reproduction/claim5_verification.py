"""Fail-closed verification of Remark 6's compute-scaling comparison."""
from __future__ import annotations

import json
import math
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq

PAPER_HTML_SHA256 = "e08754be87ff444711e592ec8d1a358e8362e86dacfab9cb8bd874fdcfd7d353"
SOURCE_URL = "https://ar5iv.labs.arxiv.org/html/2512.19905"
RETRIEVED_DATE = "2026-07-26"
VALID_ALPHAS = (0.005, 0.01, 0.02, 0.04, 0.08)
SIGMA2 = 1.0
GAMMA2 = 100.0
S2 = 1.0
K_REFERENCE = 4096


def closed_form_ridge(alpha: float, sigma2: float, gamma2: float, s2: float) -> float:
    """Equation 12 for isotropic sample covariance Sigma=s2*I."""
    hat_r = (sigma2 / gamma2) * alpha
    scaled_hat = hat_r / s2
    discriminant = (1 - alpha - scaled_hat) ** 2 + 4 * scaled_hat
    return 0.5 * s2 * (alpha + scaled_hat - 1 + math.sqrt(discriminant))


def implicit_ridge(alpha: float, sigma2: float, gamma2: float, s2: float) -> float:
    """Independent root solution of equation 11, not equation 12."""
    hat_r = (sigma2 / gamma2) * alpha

    def residual(ridge: float) -> float:
        m_sigma = s2 / (s2 + ridge)
        return ridge * (1 - alpha * m_sigma) - hat_r

    upper = max(10 * s2, 10 * hat_r / max(1 - alpha, 1e-8))
    return float(brentq(residual, 0.0, upper, xtol=1e-14, rtol=1e-14))


def q_per_dimension(ridge: float, s2: float) -> float:
    """(u^T Sigma u)/d for ||w||^2=d and isotropic Sigma."""
    return s2 * (ridge / (ridge + s2)) ** 2


def asymptotic_delta(
    alpha: float,
    k: float,
    sigma2: float = SIGMA2,
    gamma2: float = GAMMA2,
    s2: float = S2,
    *,
    use_implicit_ridge: bool = False,
) -> float:
    ridge_fn = implicit_ridge if use_implicit_ridge else closed_form_ridge
    ridge = ridge_fn(alpha, sigma2, gamma2, s2)
    qd = q_per_dimension(ridge, s2)
    radicand = 1 - 2 * qd / sigma2
    if radicand <= 0:
        raise ValueError("Remark 5 leading constant is not real in this configuration")
    return math.pi * sigma2 / (k * k * math.sqrt(radicand))


def analytic_training_slope(alpha: float, sigma2: float, gamma2: float, s2: float) -> dict:
    ridge = closed_form_ridge(alpha, sigma2, gamma2, s2)
    m_sigma = s2 / (s2 + ridge)
    m_prime = -s2 / (s2 + ridge) ** 2
    denominator_r_prime = (1 - alpha * m_sigma) - alpha * ridge * m_prime
    ridge_prime = (sigma2 / gamma2 + ridge * m_sigma) / denominator_r_prime
    qd = q_per_dimension(ridge, s2)
    qd_prime_r = 2 * s2 * s2 * ridge / (ridge + s2) ** 3
    slope_n = -alpha * qd_prime_r * ridge_prime / (sigma2 - 2 * qd)
    return {
        "ridge": ridge,
        "ridge_prime_alpha": ridge_prime,
        "q_per_dimension": qd,
        "training_log_slope": slope_n,
    }


def finite_difference_training_slope(
    alpha: float, sigma2: float, gamma2: float, s2: float, h: float = 1e-4
) -> float:
    """Central difference in log(n); alpha=d/n changes in the opposite direction."""
    delta_n_plus = asymptotic_delta(
        alpha * math.exp(-h), K_REFERENCE, sigma2, gamma2, s2, use_implicit_ridge=True
    )
    delta_n_minus = asymptotic_delta(
        alpha * math.exp(h), K_REFERENCE, sigma2, gamma2, s2, use_implicit_ridge=True
    )
    return (math.log(delta_n_plus) - math.log(delta_n_minus)) / (2 * h)


def algebraic_certificate() -> dict:
    k_values = np.array([512.0, 1024.0, 2048.0, 4096.0, 8192.0, 16384.0])
    alpha = 0.04
    deltas = np.array([asymptotic_delta(alpha, k) for k in k_values])
    fitted_slope = float(np.polyfit(np.log(k_values), np.log(deltas), 1)[0])
    ratio_invariant = deltas * np.square(k_values)
    return {
        "factorization": "delta(alpha,k)=C(alpha)*k^-2",
        "universal_derivative": "d log(delta)/d log(k)=-2",
        "fixed_k_grid_selected_without_target_slope": k_values.tolist(),
        "fitted_slope": fitted_slope,
        "max_relative_variation_of_delta_k2": float(
            np.max(np.abs(ratio_invariant / ratio_invariant[0] - 1))
        ),
        "training_chain_rule": (
            "dlog(delta)/dlog(n)=-alpha*d_alpha(uT Sigma u)/(sigma2*d-2*uT Sigma u)"
        ),
        "pass": abs(fitted_slope + 2) < 1e-12
        and np.max(np.abs(ratio_invariant / ratio_invariant[0] - 1)) < 1e-12,
    }


def valid_domain_sweep() -> pd.DataFrame:
    rows = []
    for alpha in VALID_ALPHAS:
        analytic = analytic_training_slope(alpha, SIGMA2, GAMMA2, S2)
        ridge_closed = analytic["ridge"]
        ridge_implicit = implicit_ridge(alpha, SIGMA2, GAMMA2, S2)
        b_scalar = ridge_closed / (ridge_closed + S2)
        condition_predictive = GAMMA2 * b_scalar * S2 / SIGMA2
        condition_ridge = ridge_closed / SIGMA2
        finite_difference = finite_difference_training_slope(alpha, SIGMA2, GAMMA2, S2)
        training_magnitude = abs(analytic["training_log_slope"])
        rows.append(
            {
                "alpha_d_over_n": alpha,
                "n_over_d": 1 / alpha,
                "sigma2": SIGMA2,
                "gamma2": GAMMA2,
                "sample_covariance_s2": S2,
                "ridge_closed_form": ridge_closed,
                "ridge_implicit": ridge_implicit,
                "ridge_absolute_difference": abs(ridge_closed - ridge_implicit),
                "condition_gamma2_trace_over_sigma2": condition_predictive,
                "condition_ridge_over_sigma2": condition_ridge,
                "inference_log_slope": -2.0,
                "training_log_slope_analytic": analytic["training_log_slope"],
                "training_log_slope_finite_difference": finite_difference,
                "slope_absolute_difference": abs(
                    analytic["training_log_slope"] - finite_difference
                ),
                "inference_to_training_magnitude_ratio": 2 / max(training_magnitude, 1e-300),
                "delta_at_k4096": asymptotic_delta(alpha, K_REFERENCE),
            }
        )
    return pd.DataFrame(rows)


def negative_control() -> dict:
    """A deliberately out-of-domain case must not show inference dominance."""
    alpha, sigma2, gamma2, s2 = 0.2, 0.1, 0.1, 1.0
    analytic = analytic_training_slope(alpha, sigma2, gamma2, s2)
    ridge = analytic["ridge"]
    b_scalar = ridge / (ridge + s2)
    condition_predictive = gamma2 * b_scalar * s2 / sigma2
    condition_ridge = ridge / sigma2
    training_magnitude = abs(analytic["training_log_slope"])
    return {
        "purpose": "violate both smallness assumptions",
        "alpha_d_over_n": alpha,
        "sigma2": sigma2,
        "gamma2": gamma2,
        "ridge": ridge,
        "condition_gamma2_trace_over_sigma2": condition_predictive,
        "condition_ridge_over_sigma2": condition_ridge,
        "inference_slope_magnitude": 2.0,
        "training_slope": analytic["training_log_slope"],
        "training_slope_magnitude": training_magnitude,
        "assumptions_rejected": condition_predictive > 0.1 and condition_ridge > 0.1,
        "inference_dominance_rejected": training_magnitude >= 2.0,
        "expected_failure_observed": (
            condition_predictive > 0.1 and condition_ridge > 0.1 and training_magnitude >= 2.0
        ),
    }


def _write_static_artifacts(artifact_dir: Path) -> None:
    contract = {
        "claim_id": 5,
        "statement": "Under Remark 6's assumptions, |dlog(delta)/dlog(k)|=2 is much larger than |dlog(delta)/dlog(n)|.",
        "source_anchor": "ar5iv HTML #Thmlemma6, equations #S3.E23 and #S3.E24; Remark 5 #Thmlemma5",
        "quantifiers": {
            "limit": "d,n->infinity with alpha=d/n<1 fixed",
            "selection": "exact teacher reward; T->0 followed by k->infinity",
            "conditions": [
                "(gamma^2/d)Tr(B_R Sigma) << sigma^2",
                "R << sigma^2",
            ],
        },
        "numerical_audit_of_much_less_than": {
            "each_dimensionless_condition_max": 0.1,
            "minimum_exponent_magnitude_ratio": 200,
        },
        "acceptance": {
            "algebraic_inference_certificate": "pass",
            "closed_vs_implicit_ridge_max_absolute_difference": 1e-12,
            "analytic_vs_finite_difference_slope_max_absolute_difference": 1e-8,
            "training_slope_max_magnitude": 0.01,
            "negative_control": "both assumptions and dominance must be rejected",
        },
    }
    (artifact_dir / "claim_contract.json").write_text(json.dumps(contract, indent=2) + "\n")
    (artifact_dir / "source_audit.md").write_text(
        f"""# Claim 5 source audit

- Source: `{SOURCE_URL}`
- Retrieved: `{RETRIEVED_DATE}` with an explicit browser User-Agent
- SHA-256: `{PAPER_HTML_SHA256}`
- Anchor: Remark 6 `#Thmlemma6`, equations `#S3.E23` and `#S3.E24`
- Leading error: Remark 5 `#Thmlemma5`, equation `#S3.Ex2`
- Ridge definitions: Result 1, equations `#S3.E10`–`#S3.E13`

The claim is in the proportional limit `d,n->infinity`, `alpha=d/n<1`, with
exact teacher reward and ordered limits `T->0` then `k->infinity`. It further
requires both predictive-variance and renormalized-ridge contributions to be
small relative to `sigma^2`. The comparison is explicitly between magnitudes
of local logarithmic derivatives.
"""
    )
    (artifact_dir / "method.md").write_text(
        """# Claim 5 method

1. Factor the Remark 5 error into `C(alpha) k^-2` and verify the exact `-2`.
2. Reconstruct `R(alpha)` from the isotropic closed form and differentiate the
   implicit deterministic-equivalent equation.
3. Independently solve that equation with Brent's method and compute the
   training exponent by central differences in `log(n)`.
4. Audit both dimensionless assumptions on five prespecified `alpha` values.
5. Require an out-of-domain control to lose inference-time dominance.
"""
    )
    (artifact_dir / "limitations_and_deviations.md").write_text(
        """# Claim 5 limitations and deviations

- This verifies the paper's proportional-limit deterministic equivalent, not
  a finite-dimensional training experiment.
- The qualitative symbols `<<` and `>>` are operationalized conservatively as
  each assumption ratio at most 0.1 and exponent separation at least 200x.
- The finite-difference checker uses an independently solved implicit ridge;
  it does not reuse the displayed isotropic closed form.
"""
    )


def run_claim5(out: Path, artifact_dir: Path) -> dict:
    start = time.perf_counter()
    artifact_dir.mkdir(parents=True, exist_ok=True)
    _write_static_artifacts(artifact_dir)
    certificate = algebraic_certificate()
    rows = valid_domain_sweep()
    control = negative_control()
    checks = {
        "algebraic_certificate": certificate["pass"],
        "predictive_condition": bool(
            (rows.condition_gamma2_trace_over_sigma2 <= 0.1).all()
        ),
        "ridge_condition": bool((rows.condition_ridge_over_sigma2 <= 0.1).all()),
        "ridge_checker": float(rows.ridge_absolute_difference.max()) <= 1e-12,
        "slope_checker": float(rows.slope_absolute_difference.max()) <= 1e-8,
        "training_slope_small": float(rows.training_log_slope_analytic.abs().max()) <= 0.01,
        "dominance": float(rows.inference_to_training_magnitude_ratio.min()) >= 200,
        "negative_control": control["expected_failure_observed"],
    }
    summary = {
        "claim_id": 5,
        "status": "VERIFIED" if all(checks.values()) else "BLOCKED",
        "checks": checks,
        "inference_log_slope": certificate["fitted_slope"],
        "training_log_slope_magnitude_max": float(
            rows.training_log_slope_analytic.abs().max()
        ),
        "minimum_inference_to_training_magnitude_ratio": float(
            rows.inference_to_training_magnitude_ratio.min()
        ),
        "maximum_predictive_condition_ratio": float(
            rows.condition_gamma2_trace_over_sigma2.max()
        ),
        "maximum_ridge_condition_ratio": float(rows.condition_ridge_over_sigma2.max()),
        "maximum_slope_checker_absolute_difference": float(
            rows.slope_absolute_difference.max()
        ),
        "negative_control_expected_failure_observed": control["expected_failure_observed"],
        "cpu_affinity_count": (
            len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count()
        ),
        "runtime_seconds": time.perf_counter() - start,
    }
    rows.to_csv(out / "claim5_scaling_comparison.csv", index=False)
    rows.to_csv(artifact_dir / "raw_scaling_comparison.csv", index=False)
    (artifact_dir / "proof_certificate.json").write_text(json.dumps(certificate, indent=2) + "\n")
    (artifact_dir / "independent_checker.json").write_text(
        json.dumps(
            {
                "method": "implicit Brent root plus central log(n) differences",
                "max_ridge_absolute_difference": float(rows.ridge_absolute_difference.max()),
                "max_slope_absolute_difference": float(rows.slope_absolute_difference.max()),
                "pass": checks["ridge_checker"] and checks["slope_checker"],
            },
            indent=2,
        )
        + "\n"
    )
    (artifact_dir / "negative_control.json").write_text(json.dumps(control, indent=2) + "\n")
    (artifact_dir / "runtime.json").write_text(
        json.dumps(
            {
                "backend_policy": "hf cpu-upgrade for cumulative uncertain runtime",
                "estimated_required_cores": 2,
                "visible_cpu_affinity_count": summary["cpu_affinity_count"],
                "runtime_seconds": summary["runtime_seconds"],
                "deterministic": True,
            },
            indent=2,
        )
        + "\n"
    )
    (artifact_dir / "EVAL.md").write_text(
        f"""# Claim 5 evaluation

Verdict: **{summary['status']}**

- Inference exponent: {summary['inference_log_slope']:.12f}
- Largest training exponent magnitude: {summary['training_log_slope_magnitude_max']:.6g}
- Smallest inference/training magnitude ratio: {summary['minimum_inference_to_training_magnitude_ratio']:.1f}x
- Maximum assumption ratios: predictive
  {summary['maximum_predictive_condition_ratio']:.6g}, ridge
  {summary['maximum_ridge_condition_ratio']:.6g}
- Independent slope-checker discrepancy:
  {summary['maximum_slope_checker_absolute_difference']:.3g}
- Out-of-domain control rejected dominance:
  `{summary['negative_control_expected_failure_observed']}`
"""
    )
    print("CLAIM5_EVIDENCE_BEGIN")
    print(json.dumps(summary, indent=2))
    print("CLAIM5_ALL_ROWS")
    print(rows.to_csv(index=False).strip())
    print("CLAIM5_NEGATIVE_CONTROL")
    print(json.dumps(control, indent=2))
    print("CLAIM5_EVIDENCE_END")
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise AssertionError(f"Claim 5 fail-closed verifier rejected: {failed}")
    return summary

