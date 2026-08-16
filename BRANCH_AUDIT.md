# Branch audit and migration map

## Repository rename

The repository started as
icml26-repro-ANVg7NnupP-llm-judge-scaling and is normalized to
icml26-llm-judge-inference-scaling. The old repository name is historical
metadata only; the final public URL is documented in README.md and
SOURCE_MANIFEST.md.

## Source rationale

The old main tip b45369d8baea7508df5a3543509de03a8dedb0d9 is the publication
manifest and post-release verification surface. It contains the cumulative
claim artifacts and is the source base for the final main documentation. The
older evaluator-visible tip exposes only the pre-release raw surface; it is
preserved as a separate final branch.

## Legacy-to-final branch map

| Final branch | Legacy branch | Source tip before migration | Role |
|---|---|---|---|
| main | publication-manifest-and-post-release-verificati | b45369d8baea7508df5a3543509de03a8dedb0d9 | Canonical five-claim evidence collection and documentation. |
| release/publication-manifest | orx/publication-manifest-and-post-release-verificati | b45369d8baea7508df5a3543509de03a8dedb0d9 | Published revision manifest and post-publication verification. |
| baseline/judged-6-of-10 | orx/frozen-validated-baseline | 1ede9a0a27b9ac2250e4c51d71230dd28d598418 | Frozen historical baseline and previous live evaluator surface. |
| audit/claim-4-temperature | orx/claim-4-exact-temperature-contract | ac285f961476e3c26f18387af854cf1c6ad564d6 | Remark 4 symbolic and calibration route. |
| audit/claim-5-data-scaling | orx/claim-5-inference-versus-data-scaling | 7f1bb19cfbdcfe31334b42e7c9271556d59f51b0 | Remark 6 scaling route. |
| release/evaluator-visible | orx/evaluator-visible-cumulative-evidence | 02de86873f7b24582307e5968ddeb0ec9b94b6a7 | Evaluator-visible cumulative raw evidence. |
| release/candidate-blind-audit | orx/release-candidate-and-blind-audit | e0a6aa04e971eb1bf3516f484451e1f529b6f421 | Release candidate, blind traversal, and fail-closed audit. |

Legacy branch names are retained here to make the migration inspectable. They
are not intended to remain as public branches after normalization.

## Final invariants

- The final public inventory contains exactly the seven descriptive branches
  in the table above.
- main and release/publication-manifest expose the cumulative documentation
  and evidence package.
- baseline/judged-6-of-10 remains a historical comparison point, not the
  current live score.
- Claim 4 and Claim 5 routes remain independently reachable.
- The published Space revision and post-publication audit are evidence of
  release integrity, not a new evaluator score.
- All reachable commits are rewritten to the canonical MachineLearning-Nerd
  author and committer identity with no co-author trailers.
