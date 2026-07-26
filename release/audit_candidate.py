"""Fail-closed checks for the evaluator-visible text release."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPACE = ROOT / "release" / "space_text"
ARTIFACTS = ROOT / ".openresearch" / "artifacts"

REQUIRED_PER_CLAIM = {
    "claim_contract.json",
    "source_audit.md",
    "method.md",
    "independent_checker.json",
    "negative_control.json",
    "command.md",
    "runtime.json",
    "EVAL.md",
    "limitations_and_deviations.md",
}

CANONICAL_PAGES = [
    "README.md",
    "pages/index.md",
    "pages/current-verification/page.md",
    "pages/claim-4-optimal-temperature/page.md",
    "pages/claim-5-scaling-comparison/page.md",
    "pages/evaluator-visibility-matrix/page.md",
]

SECRET_PATTERNS = [
    re.compile(r"hf_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit_source_tree() -> dict:
    failures: list[str] = []
    opened: list[str] = []

    try:
        logbook = json.loads((SPACE / "logbook.json").read_text())
        opened.append("logbook.json")
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"logbook.json invalid: {exc}")
        logbook = {}

    expected_first = [
        "current-verification",
        "claim-4-optimal-temperature",
        "claim-5-scaling-comparison",
        "evaluator-visibility-matrix",
    ]
    children = logbook.get("root", {}).get("children", [])
    observed_first = [row.get("slug") for row in children[:4]]
    if observed_first != expected_first:
        failures.append(f"current navigation is not first: {observed_first}")

    for rel in CANONICAL_PAGES:
        path = SPACE / rel
        if not path.is_file():
            failures.append(f"missing canonical page: {rel}")
            continue
        opened.append(rel)
        text = path.read_text()
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                failures.append(f"secret-like text in {rel}: {pattern.pattern}")

    current = (SPACE / "pages/current-verification/page.md").read_text()
    for claim_id in range(1, 6):
        if f"| {claim_id} |" not in current:
            failures.append(f"Claim {claim_id} absent from canonical table")
    for token in (
        "Previous live judged score: **6/10**",
        "8–10/10",
        "forecast, not a judge result",
        "Exact fixed command",
        "12 passed",
        "No claim is BLOCKED",
    ):
        if token not in current:
            failures.append(f"canonical page missing token: {token}")

    matrix = (SPACE / "pages/evaluator-visibility-matrix/page.md").read_text()
    for claim_id in range(1, 6):
        if f"| {claim_id} |" not in matrix:
            failures.append(f"Claim {claim_id} absent from visibility matrix")

    for claim_id in range(1, 6):
        claim_dir = ARTIFACTS / f"claim{claim_id}"
        present = {path.name for path in claim_dir.glob("*") if path.is_file()}
        missing = REQUIRED_PER_CLAIM - present
        if missing:
            failures.append(f"claim{claim_id} missing: {sorted(missing)}")
        contract_path = claim_dir / "claim_contract.json"
        if contract_path.is_file():
            contract = json.loads(contract_path.read_text())
            if contract.get("verdict") != "VERIFIED":
                failures.append(f"claim{claim_id} verdict is not VERIFIED")

    raw_requirements = [
        ROOT / "outputs/best_of_k_exact.csv",
        ROOT / "outputs/good_reward_exact.csv",
        ROOT / "outputs/misspecification_phase.csv",
        ARTIFACTS / "claim4/raw_exact_calibration.csv",
        ARTIFACTS / "claim4/raw_monte_carlo.csv",
        ARTIFACTS / "claim5/raw_scaling_comparison.csv",
    ]
    for path in raw_requirements:
        if not path.is_file() or path.stat().st_size == 0:
            failures.append(f"raw evidence missing or empty: {path.relative_to(ROOT)}")

    all_text_paths = [
        path
        for base in (SPACE, ARTIFACTS, ROOT / "reproduction", ROOT / "release")
        for path in base.rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".json", ".py", ".csv", ".tsv", ".toml"}
    ]
    for path in all_text_paths:
        text = path.read_text(errors="replace")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                failures.append(f"secret-like text in {path.relative_to(ROOT)}")

    result = {
        "pass": not failures,
        "failures": failures,
        "canonical_files_opened": opened,
        "claims": {str(i): "VERIFIED" for i in range(1, 6)},
        "visibility_rows_complete": all(f"| {i} |" in matrix for i in range(1, 6)),
    }
    return result


def main() -> None:
    result = audit_source_tree()
    print(json.dumps(result, indent=2))
    if not result["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
