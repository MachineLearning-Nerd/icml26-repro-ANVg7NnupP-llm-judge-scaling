# Claim 2 method

Deterministic nested quadrature evaluates 36 prespecified curves: three teacher
offsets, four reward shifts, three temperatures, and `k=1..256`. Prefix-coupled
seeded Monte Carlo independently checks representative aligned and far-reward
curves. The unselected `k=1` identity is a structural control.
