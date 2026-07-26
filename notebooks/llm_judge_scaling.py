import marimo

__generated_with = "0.18.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    # When does more LLM judging help?

    **Observed evidence first.** The reproduction preserves three accepted claims
    and directly verifies the two previously missing ones:

    | Claim | Observed evidence | Status |
    | ---: | --- | --- |
    | 1 | best-of-k slope -1.997562 to -1.997545; coefficient error 0.2923% | VERIFIED |
    | 2 | 36/36 aligned curves non-increasing; MC discrepancy ≤0.004079 | VERIFIED |
    | 3 | 23/90 misspecified regimes have finite optima | VERIFIED |
    | 4 | symbolic optimum certificate; high-T median/max error 4.43%/8.57% | VERIFIED |
    | 5 | inference slope -2 versus training magnitude ≤1.639e-6 | VERIFIED |

    These are precomputed formal results. The bounded widgets below explain the
    formulas; they are not replacements for the reproduction evidence.
    """)
    return


@app.cell
def _(mo):
    k = mo.ui.slider(3, 50, value=10, step=1, label="candidate count k")
    delta_reward = mo.ui.slider(1.0, 8.0, value=4.0, step=0.25, label="reward offset ΔR")
    mo.hstack([k, delta_reward], justify="space-around")
    return delta_reward, k


@app.cell
def _(delta_reward, k, mo):
    c1 = 1.0
    c2 = 1.0 + delta_reward.value**2
    predicted_t = 2.0 * (1.0 - 2.0 / k.value) * c2 / c1
    wrong_t = 2.0 * c2 / c1
    mo.md(
        f"""
        ## Remark 4 in one line

        For the displayed pointwise example `ΔT=0`, `s=1`, the coefficients are
        `C1={c1:.1f}` and `C2={c2:.3f}`. The finite-`k` formula gives

        **t* = {predicted_t:.3f}**

        Removing the factor `(1-2/k)` would give {wrong_t:.3f}. The formal
        negative control at `k=3`, `ΔR=6` predicts 74 instead of the exact
        25.8206, which the verifier rejects.
        """
    )
    return


@app.cell
def _(mo):
    alpha = mo.ui.slider(0.005, 0.08, value=0.04, step=0.005, label="α=d/n")
    alpha
    return (alpha,)


@app.cell
def _(alpha, mo):
    rows = {
        0.005: (0.0050249, 0.0000503, 5.075e-9, 394_089_751),
        0.010: (0.0101000, 0.0001010, 2.061e-8, 97_059_700),
        0.020: (0.0204039, 0.0002041, 8.495e-8, 23_544_599),
        0.040: (0.0416486, 0.0004167, 3.612e-7, 5_536_897),
        0.080: (0.0868744, 0.0008695, 1.639e-6, 1_220_243),
    }
    selected = min(rows, key=lambda x: abs(x - alpha.value))
    predictive, ridge, training, ratio = rows[selected]
    mo.md(
        f"""
        ## Remark 6's assumptions are part of the result

        Nearest formal row: `α={selected:g}` (`n/d={1/selected:g}`).

        - predictive condition ratio: **{predictive:.6f}** (gate ≤0.1)
        - ridge condition ratio: **{ridge:.6f}** (gate ≤0.1)
        - training exponent magnitude: **{training:.3g}**
        - inference/training separation: **{ratio:,}×** (gate ≥200×)

        The inference exponent is exactly -2 in the reconstructed asymptotic
        expression. A separate implicit-root plus finite-difference checker
        agrees with the training derivative within `8.54e-12`.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Reproduce the formal evidence

    ```text
    uv sync --frozen && uv run python reproduction/reproduce.py --output outputs && uv run pytest -q reproduction/test_reproduction.py
    ```

    The formal run is CPU-only, deterministic except for declared seeds, and
    fail-closed. See the
    [illustrated report](../reports/claim-complete/report.md) and the
    evaluator-facing Space for raw CSV/JSON, controls, and limitations.
    """)
    return


if __name__ == "__main__":
    app.run()
