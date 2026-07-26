# Judged claims

1. With best-of-`k` and teacher as reward in the ordered low-temperature,
   large-`k` limit, generalization error has the displayed `Theta(1/k^2)` rate
   and coefficient.
2. When reward is sufficiently aligned with the teacher, generalization error
   decreases monotonically with increasing inference samples `k`.
3. Substantial reward misspecification can induce a finite optimal `k` beyond
   which more sampling increases error.
4. For fixed `k>2` in the stated high-temperature expansion, the optimal
   reward-sampling temperature is `t=2(1-2/k)C2/C1`.
5. In the stated proportional limit and small-bias regime, the inference
   exponent magnitude 2 is much larger than the training-data exponent.
