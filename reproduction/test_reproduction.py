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
