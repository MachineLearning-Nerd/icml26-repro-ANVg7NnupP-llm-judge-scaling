"""Fail-closed verification for the normalized ICML reproduction repository."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXPECTED_REPO = "MachineLearning-Nerd/icml26-llm-judge-inference-scaling"
EXPECTED_IDENTITY = "MachineLearning-Nerd <MachineLearning-Nerd@users.noreply.github.com>"
EXPECTED_PAPER_SHA256 = (
    "ca9fd15ee9696e93d2d9f01317ae72f4c24eb6dcec56937fb3b4afe01521be39"
)
EXPECTED_BRANCHES = {
    "main",
    "baseline/judged-6-of-10",
    "audit/claim-4-temperature",
    "audit/claim-5-data-scaling",
    "release/evaluator-visible",
    "release/candidate-blind-audit",
    "release/publication-manifest",
}
EXPECTED_CLAIM_STATUSES = {
    "claim_1": "VERIFIED_SCOPED",
    "claim_2": "VERIFIED_SCOPED",
    "claim_3": "VERIFIED_SCOPED",
    "claim_4": "VERIFIED_SCOPED_CALIBRATION",
    "claim_5": "VERIFIED_SCOPED_PROPORTIONAL_LIMIT",
}
DOC_FILES = (
    "README.md",
    "STATUS.md",
    "claims.md",
    "CLAIM_EVIDENCE.md",
    "BRANCH_AUDIT.md",
    "SOURCE_AUDIT.md",
    "SOURCE_MANIFEST.md",
    "ENVIRONMENT.md",
    "CITATION.cff",
    "EVIDENCE_MANIFEST.json",
)


class VerificationError(Exception):
    pass


def run(*args: str, cwd: Path = ROOT) -> str:
    result = subprocess.run(
        list(args),
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise VerificationError(f"command failed ({' '.join(args)}): {detail}")
    return result.stdout.strip()


def load_json(relative: str) -> dict:
    path = ROOT / relative
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"invalid JSON {relative}: {exc}") from exc
    if not isinstance(value, dict):
        raise VerificationError(f"JSON object expected: {relative}")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def branch_inventory() -> set[str]:
    refs = run(
        "git",
        "for-each-ref",
        "--format=%(refname)",
        "refs/heads",
        "refs/remotes/origin",
    ).splitlines()
    names: set[str] = set()
    for ref in refs:
        if ref.startswith("refs/heads/"):
            names.add(ref.removeprefix("refs/heads/"))
            continue
        if ref.startswith("refs/remotes/origin/"):
            name = ref.removeprefix("refs/remotes/origin/")
            if name not in {"HEAD", ""}:
                names.add(name)
    return names


def check_git_state() -> dict:
    require(not run("git", "status", "--porcelain"), "working tree is not clean")
    require(run("git", "symbolic-ref", "--short", "HEAD") == "main", "HEAD is not main")
    remote = run("git", "config", "--get", "remote.origin.url")
    require(
        remote.rstrip("/").removesuffix(".git")
        in {
            f"https://github.com/{EXPECTED_REPO}",
            f"git@github.com:{EXPECTED_REPO}",
        },
        f"origin is not the final repository: {remote}",
    )
    observed = branch_inventory()
    require(observed == EXPECTED_BRANCHES, f"branch inventory mismatch: {sorted(observed)}")

    identity_lines = run(
        "git",
        "log",
        "--all",
        "--format=%an <%ae>|%cn <%ce>",
    ).splitlines()
    expected_line = f"{EXPECTED_IDENTITY}|{EXPECTED_IDENTITY}"
    require(bool(identity_lines), "no reachable commits found")
    require(
        set(identity_lines) == {expected_line},
        f"non-canonical author or committer identity found: {sorted(set(identity_lines))}",
    )
    messages = run("git", "log", "--all", "--format=%B")
    require("co-authored-by:" not in messages.lower(), "co-author trailer found")
    return {
        "remote": remote,
        "branches": sorted(observed),
        "canonical_identity": EXPECTED_IDENTITY,
        "reachable_commit_count": len(identity_lines),
    }


def check_docs_and_manifest() -> tuple[dict, dict]:
    for relative in DOC_FILES:
        require((ROOT / relative).is_file(), f"required documentation missing: {relative}")

    manifest = load_json("EVIDENCE_MANIFEST.json")
    repository = manifest.get("repository", {})
    require(repository.get("name") == EXPECTED_REPO, "manifest repository name is stale")
    require(repository.get("default_branch") == "main", "manifest default branch is not main")
    require(repository.get("attribution") == EXPECTED_IDENTITY, "manifest attribution is stale")
    require(repository.get("independent_code") is True, "independent-code audit is not asserted")
    require(repository.get("official_source_audited") is True, "official source audit is missing")
    require(
        manifest.get("collection_status") == "VERIFIED_SCOPED_WITH_LIVE_SCORE_PENDING",
        "manifest collection status is unexpected",
    )
    claims = manifest.get("claims", {})
    require(set(claims) == set(EXPECTED_CLAIM_STATUSES), "manifest claim set is incomplete")
    for claim_id, expected_status in EXPECTED_CLAIM_STATUSES.items():
        claim = claims[claim_id]
        require(claim.get("status") == expected_status, f"{claim_id} status is stale")
        for relative in claim.get("evidence", []):
            require((ROOT / relative).is_file(), f"{claim_id} evidence is missing: {relative}")

    release_gate = manifest.get("release_gate", {})
    require(release_gate.get("all_current_claims_terminal") is True, "claims are not terminal")
    require(release_gate.get("published_text_only_update") is True, "published update is not text-only")
    require(release_gate.get("postpublication_audit_passed") is True, "postpublication audit did not pass")
    require(release_gate.get("live_judge_pending") is True, "live-score boundary is missing")
    require("Thank you" in manifest.get("thank_you", ""), "manifest thank-you note is missing")

    stale_tokens = (
        "icml26-repro-ANVg7NnupP-llm-judge-scaling",
        "orx/",
    )
    for relative in DOC_FILES:
        if relative in {"BRANCH_AUDIT.md", "EVIDENCE_MANIFEST.json"}:
            continue
        text = (ROOT / relative).read_text(errors="replace")
        for token in stale_tokens:
            require(token not in text, f"stale migration token in {relative}: {token}")

    report = (ROOT / "reports/claim-complete/report.md").read_text(errors="replace")
    require("icml26-llm-judge-inference-scaling" in report, "technical report lacks final repository links")
    require("icml26-repro-ANVg7NnupP-llm-judge-scaling" not in report, "technical report has old repository links")
    require("/tree/orx/" not in report, "technical report has old branch links")
    require("Thank you" in (ROOT / "README.md").read_text(), "README thank-you note is missing")
    require("icml26-llm-judge-inference-scaling" in (ROOT / "CITATION.cff").read_text(), "CITATION.cff URL is stale")

    return manifest, claims


def check_paper_and_artifacts() -> dict:
    paper = ROOT / "paper.pdf"
    require(paper.is_file(), "paper.pdf is missing")
    paper_hash = sha256(paper)
    require(paper_hash == EXPECTED_PAPER_SHA256, f"paper.pdf hash mismatch: {paper_hash}")

    claim1_checker = load_json(".openresearch/artifacts/claim1/independent_checker.json")
    claim1_negative = load_json(".openresearch/artifacts/claim1/negative_control.json")
    require(claim1_checker.get("exponent_pass") is True, "Claim 1 exponent checker failed")
    require(claim1_checker.get("coefficient_pass") is True, "Claim 1 coefficient checker failed")
    require(claim1_negative.get("observed") is True, "Claim 1 negative control failed")

    claim2_checker = load_json(".openresearch/artifacts/claim2/independent_checker.json")
    claim2_negative = load_json(".openresearch/artifacts/claim2/negative_control.json")
    require(claim2_checker.get("pass") is True, "Claim 2 independent checker failed")
    require(claim2_negative.get("expected_failure_observed") is True, "Claim 2 negative control failed")

    claim3_checker = load_json(".openresearch/artifacts/claim3/independent_checker.json")
    claim3_negative = load_json(".openresearch/artifacts/claim3/negative_control.json")
    require(claim3_checker.get("qualitative_finite_optimum_recovered") is True, "Claim 3 checker failed")
    require(claim3_negative.get("expected_behavior_observed") is True, "Claim 3 negative control failed")

    claim4_proof = load_json(".openresearch/artifacts/claim4/proof_certificate.json")
    claim4_checker = load_json(".openresearch/artifacts/claim4/independent_checker.json")
    claim4_negative = load_json(".openresearch/artifacts/claim4/negative_control.json")
    require(claim4_proof.get("pass") is True, "Claim 4 proof certificate failed")
    require(claim4_checker.get("pass") is True, "Claim 4 independent checker failed")
    require(claim4_negative.get("expected_failure_observed") is True, "Claim 4 negative control failed")

    claim5_proof = load_json(".openresearch/artifacts/claim5/proof_certificate.json")
    claim5_checker = load_json(".openresearch/artifacts/claim5/independent_checker.json")
    claim5_negative = load_json(".openresearch/artifacts/claim5/negative_control.json")
    require(claim5_proof.get("pass") is True, "Claim 5 proof certificate failed")
    require(claim5_checker.get("pass") is True, "Claim 5 independent checker failed")
    require(claim5_negative.get("expected_failure_observed") is True, "Claim 5 negative control failed")

    summary = load_json("outputs/summary.json")
    require(summary.get("claim_1") == "verified", "summary Claim 1 is not verified")
    require(summary.get("claim_2") == "verified", "summary Claim 2 is not verified")
    require(summary.get("claim_3") == "verified", "summary Claim 3 is not verified")
    require(summary.get("good_monotone_curves") == 36, "summary Claim 2 curve count changed")
    require(summary.get("finite_optimum_curves") == 23, "summary Claim 3 count changed")
    return {
        "paper_sha256": paper_hash,
        "claim_statuses": {f"claim_{i}": "verified" for i in range(1, 6)},
    }


def check_release_audit() -> dict:
    result = subprocess.run(
        [sys.executable, "release/audit_candidate.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise VerificationError(
            f"release audit failed: {result.stderr.strip() or result.stdout.strip()}"
        )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise VerificationError(f"release audit did not emit JSON: {exc}") from exc
    require(payload.get("pass") is True, "release audit returned pass=false")
    require(payload.get("visibility_rows_complete") is True, "release visibility matrix is incomplete")
    return {"pass": True, "visibility_rows_complete": True}


def main() -> None:
    git_state = check_git_state()
    manifest, claims = check_docs_and_manifest()
    evidence = check_paper_and_artifacts()
    release = check_release_audit()
    result = {
        "pass": True,
        "repository": EXPECTED_REPO,
        "branches": git_state["branches"],
        "canonical_identity": EXPECTED_IDENTITY,
        "reachable_commit_count": git_state["reachable_commit_count"],
        "paper_sha256": evidence["paper_sha256"],
        "claim_statuses": {claim_id: claims[claim_id]["status"] for claim_id in sorted(claims)},
        "collection_status": manifest["collection_status"],
        "release_audit": release,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except VerificationError as exc:
        print(json.dumps({"pass": False, "error": str(exc)}, indent=2))
        raise SystemExit(1)
