"""Render reader-facing figures from committed reproduction evidence."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
IMAGES = HERE / "images"

COLORS = {
    "blue": "#2563eb",
    "green": "#059669",
    "amber": "#d97706",
    "red": "#dc2626",
    "slate": "#475569",
}


def save(fig: plt.Figure, name: str) -> None:
    IMAGES.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(IMAGES / name, dpi=180, bbox_inches="tight")
    plt.close(fig)


def headline() -> None:
    c4 = pd.read_csv(ROOT / ".openresearch/artifacts/claim4/raw_exact_calibration.csv")
    c5 = pd.read_csv(ROOT / ".openresearch/artifacts/claim5/raw_scaling_comparison.csv")
    eligible = c4[c4.high_temperature_eligible.astype(str).str.lower() == "true"]

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.2))
    axes[0].scatter(
        eligible.predicted_t,
        eligible.exact_optimal_t,
        c=eligible.k,
        cmap="viridis",
        s=65,
        edgecolor="white",
        linewidth=0.7,
    )
    lo = min(eligible.predicted_t.min(), eligible.exact_optimal_t.min())
    hi = max(eligible.predicted_t.max(), eligible.exact_optimal_t.max())
    axes[0].plot([lo, hi], [lo, hi], "--", color=COLORS["slate"], label="exact agreement")
    axes[0].set(
        xlabel="Remark 4 predicted temperature",
        ylabel="Exact finite-k optimum",
        title="Claim 4: formula tracks exact optima",
    )
    axes[0].legend(frameon=False)

    axes[1].semilogy(
        c5.n_over_d,
        np.abs(c5.training_log_slope_analytic),
        "o-",
        color=COLORS["amber"],
        label="training-data exponent",
    )
    axes[1].axhline(2, color=COLORS["blue"], linewidth=2, label="inference exponent")
    axes[1].set(
        xlabel="training samples per dimension (n/d)",
        ylabel="absolute log-slope",
        title="Claim 5: inference exponent dominates",
    )
    axes[1].legend(frameon=False)
    fig.suptitle("Two previously missing claims now have direct, fail-closed evidence", fontsize=14)
    save(fig, "headline_missing_claims.png")


def inverse_square() -> None:
    rows = pd.read_csv(ROOT / "outputs/best_of_k_exact.csv")
    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    for delta, group in rows.groupby("delta_teacher"):
        ax.loglog(group.k, group.error, "o-", markersize=3, label=f"ΔT/s={delta:g}")
    reference_k = np.array([256, 16384])
    anchor = rows[(rows.delta_teacher == 0) & (rows.k == 256)].error.iloc[0]
    ax.loglog(
        reference_k,
        anchor * (reference_k / 256) ** -2,
        "--",
        color="black",
        label="slope −2",
    )
    ax.set(xlabel="inference samples k", ylabel="best-of-k error", title="Claim 1: inverse-square tail")
    ax.legend(frameon=False, ncol=2)
    save(fig, "claim1_inverse_square.png")


def claim4_temperature() -> None:
    exact = pd.read_csv(ROOT / ".openresearch/artifacts/claim4/raw_exact_calibration.csv")
    mc = pd.read_csv(ROOT / ".openresearch/artifacts/claim4/raw_monte_carlo.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.1))
    for k, group in exact.groupby("k"):
        axes[0].plot(group.predicted_t, 100 * group.relative_error, "o-", label=f"k={k}")
    axes[0].axhline(20, color=COLORS["red"], linestyle="--", label="20% gate")
    axes[0].set(
        xlabel="predicted t*",
        ylabel="exact-optimum relative error (%)",
        title="High-temperature calibration",
    )
    axes[0].legend(frameon=False, ncol=2)
    axes[1].errorbar(
        mc.t,
        mc.monte_carlo_error,
        yerr=mc.standard_error,
        fmt="o",
        color=COLORS["green"],
        label="120k direct samples",
    )
    axes[1].plot(mc.t, mc.exact_error, "-", color=COLORS["blue"], label="quadrature")
    axes[1].axvline(27.2, color=COLORS["amber"], linestyle="--", label="formula t*=27.2")
    axes[1].set(xlabel="temperature t", ylabel="error", title="Independent Monte Carlo checker")
    axes[1].legend(frameon=False)
    save(fig, "claim4_temperature_evidence.png")


def claim5_assumptions() -> None:
    rows = pd.read_csv(ROOT / ".openresearch/artifacts/claim5/raw_scaling_comparison.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.1))
    axes[0].semilogy(
        rows.alpha_d_over_n,
        rows.condition_gamma2_trace_over_sigma2,
        "o-",
        label="predictive ratio",
    )
    axes[0].semilogy(
        rows.alpha_d_over_n,
        rows.condition_ridge_over_sigma2,
        "s-",
        label="ridge ratio",
    )
    axes[0].axhline(0.1, color=COLORS["red"], linestyle="--", label="domain gate")
    axes[0].set(xlabel="α=d/n", ylabel="dimensionless ratio", title="Both assumptions audited")
    axes[0].legend(frameon=False)
    axes[1].semilogy(
        rows.alpha_d_over_n,
        rows.inference_to_training_magnitude_ratio,
        "o-",
        color=COLORS["green"],
    )
    axes[1].axhline(200, color=COLORS["red"], linestyle="--", label="acceptance gate")
    axes[1].set(xlabel="α=d/n", ylabel="inference/training slope ratio", title="Exponent separation")
    axes[1].legend(frameon=False)
    save(fig, "claim5_assumption_audit.png")


def controls() -> None:
    c4 = json.loads((ROOT / ".openresearch/artifacts/claim4/negative_control.json").read_text())
    c5 = json.loads((ROOT / ".openresearch/artifacts/claim5/negative_control.json").read_text())
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.0))
    axes[0].bar(
        ["correct exact\noptimum", "wrong formula\nprediction"],
        [c4["exact_optimal_t"], c4["wrong_predicted_t"]],
        color=[COLORS["green"], COLORS["red"]],
    )
    axes[0].set(ylabel="temperature", title="Claim 4 control: omit finite-k factor")
    axes[1].bar(
        ["inference\nmagnitude", "training\nmagnitude"],
        [c5["inference_slope_magnitude"], c5["training_slope_magnitude"]],
        color=[COLORS["blue"], COLORS["red"]],
    )
    axes[1].set(ylabel="absolute log-slope", title="Claim 5 control: leave valid domain")
    fig.suptitle("Controls fail for the intended scientific reasons", fontsize=14)
    save(fig, "negative_controls.png")


def main() -> None:
    headline()
    inverse_square()
    claim4_temperature()
    claim5_assumptions()
    controls()
    print(f"rendered 5 figures in {IMAGES}")


if __name__ == "__main__":
    main()
