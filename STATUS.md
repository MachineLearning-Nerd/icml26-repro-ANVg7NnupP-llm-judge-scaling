# Status

## Current collection

- Repository: https://github.com/MachineLearning-Nerd/icml26-llm-judge-inference-scaling
- State: VERIFIED_SCOPED_WITH_LIVE_SCORE_PENDING
- Claims 1–5: VERIFIED within their explicit analytical contracts
- Code: independent clean-room reproduction of the Gaussian proxy
- Official source repository: recorded and pinned in SOURCE_AUDIT.md; not imported
- Attribution target: MachineLearning-Nerd <MachineLearning-Nerd@users.noreply.github.com>

## Claim boundaries

1. Result 3 is tested in the ordered teacher-reward, low-temperature,
   large-k limit with exact survival integrals.
2. Result 2 is tested on 36 declared aligned conditional Gaussian curves and
   independently checked with seeded Monte Carlo.
3. Remark 3 is tested for its finite-optimum and later-harm consequence; its
   separate threshold and k* approximation formulas remain out of scope.
4. Remark 4 is tested as a truncated high-temperature expansion optimizer with
   t >= 20 as the executable high-temperature gate.
5. Remark 6 is tested in the proportional limit with exact teacher reward and
   both smallness assumptions explicitly audited.

## Historical publication and evaluator state

- Space: https://huggingface.co/spaces/DineshAI/ANVg7NnupP
- Previous live judged score: 6/10
- Protected judged parent: 888e34394f08123538bccdaba0e8852558a5b724
- Published revision: e243be8375bd6139647f40f9b114ab1d59c9eaf2
- Publication: additive text-only update; no deletions
- Post-publication audit: passed with 20/20 protected paths and 80/80 hashes
- Live judge: not rerun after publication; no score increase is claimed
- Validated scientific commit: e0a6aa04e971eb1bf3516f484451e1f529b6f421
- Validated run: 585734a7-0b00-4bb3-87f7-9e951cf34514
- Runtime: 8.668 scientific seconds, 47 total seconds, CPU-only
