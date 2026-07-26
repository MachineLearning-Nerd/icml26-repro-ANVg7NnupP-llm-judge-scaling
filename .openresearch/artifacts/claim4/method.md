# Claim 4 method

1. Reconstruct the derivative and curvature of
   `D-A*C1/t+A*B*C2/t^2`, with `A=1-1/k`, `B=1-2/k`.
2. Optimize the exact finite-`k` Gaussian ratio expectation over a fixed
   log-temperature interval `[1,512]` on a prespecified 4x4 grid.
3. Independently sample 120,000 candidate sets on ten fixed temperatures.
4. Remove the finite-`k` factor and test `k=2` as controls that must fail.

The search interval, grid, eligibility rule, and tolerances were fixed before
the run and were not selected from the formula's observed errors.
