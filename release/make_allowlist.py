"""Create the exact text-only Space upload allowlist and hash manifest."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = ROOT / "release/space_upload_allowlist.tsv"
MANIFEST = ROOT / "release/MANIFEST.sha256"

TEXT_SUFFIXES = {"", ".csv", ".json", ".md", ".py", ".toml", ".tsv", ".txt", ".lock", ".sha256"}


def mapping() -> list[tuple[str, str]]:
    rows = [
        ("release/space_text/README.md", "README.md"),
        ("release/space_text/logbook.json", "logbook.json"),
        ("release/space_text/pages/index.md", "pages/index.md"),
        (
            "release/space_text/pages/current-verification/page.md",
            "pages/current-verification/page.md",
        ),
        (
            "release/space_text/pages/claim-4-optimal-temperature/page.md",
            "pages/claim-4-optimal-temperature/page.md",
        ),
        (
            "release/space_text/pages/claim-5-scaling-comparison/page.md",
            "pages/claim-5-scaling-comparison/page.md",
        ),
        (
            "release/space_text/pages/evaluator-visibility-matrix/page.md",
            "pages/evaluator-visibility-matrix/page.md",
        ),
        (".python-version", "evidence/current/.python-version"),
        ("pyproject.toml", "evidence/current/pyproject.toml"),
        ("uv.lock", "evidence/current/uv.lock"),
        ("ENVIRONMENT.md", "evidence/current/ENVIRONMENT.md"),
        ("SOURCE_AUDIT.md", "evidence/current/SOURCE_AUDIT.md"),
        ("claims.md", "evidence/current/claims.md"),
        ("release/final_release_report.md", "evidence/current/FINAL_RELEASE_REPORT.md"),
        ("release/red_team_review.md", "evidence/current/RED_TEAM_REVIEW.md"),
        ("release/command_log.md", "evidence/current/COMMAND_LOG.md"),
        (
            "release/space_upload_allowlist.tsv",
            "evidence/current/UPLOAD_ALLOWLIST.tsv",
        ),
        ("release/MANIFEST.sha256", "evidence/current/MANIFEST.sha256"),
    ]
    for path in sorted((ROOT / ".openresearch/artifacts").rglob("*")):
        if path.is_file():
            rel = path.relative_to(ROOT).as_posix()
            suffix = path.suffix.lower()
            if suffix not in TEXT_SUFFIXES:
                raise ValueError(f"non-text artifact in release: {rel}")
            remote = "evidence/current/artifacts/" + path.relative_to(
                ROOT / ".openresearch/artifacts"
            ).as_posix()
            rows.append((rel, remote))
    for rel in (
        "outputs/best_of_k_exact.csv",
        "outputs/good_reward_exact.csv",
        "outputs/misspecification_phase.csv",
        "outputs/monte_carlo_crosscheck.csv",
        "outputs/summary.json",
        "reproduction/reproduce.py",
        "reproduction/claim4_verification.py",
        "reproduction/claim5_verification.py",
        "reproduction/test_reproduction.py",
    ):
        rows.append((rel, "evidence/current/" + rel))
    return rows


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> None:
    rows = mapping()
    local_paths = [row[0] for row in rows]
    remote_paths = [row[1] for row in rows]
    if len(local_paths) != len(set(local_paths)):
        raise ValueError("duplicate local allowlist path")
    if len(remote_paths) != len(set(remote_paths)):
        raise ValueError("duplicate remote allowlist path")

    missing_before_generated = [
        rel
        for rel, _ in rows
        if rel not in {"release/space_upload_allowlist.tsv", "release/MANIFEST.sha256"}
        and not (ROOT / rel).is_file()
    ]
    if missing_before_generated:
        raise FileNotFoundError(missing_before_generated)

    text = "local_path\tspace_path\n" + "".join(
        f"{local}\t{remote}\n" for local, remote in rows
    )
    ALLOWLIST.write_text(text)

    lines = []
    for local, remote in rows:
        if local == "release/MANIFEST.sha256":
            continue
        path = ROOT / local
        if not path.is_file():
            raise FileNotFoundError(path)
        if path.suffix.lower() not in TEXT_SUFFIXES:
            raise ValueError(f"upload is not text allowlisted: {local}")
        path.read_text()
        lines.append(f"{sha256(path)}  {remote}")
    MANIFEST.write_text("\n".join(lines) + "\n")
    print(f"allowlisted {len(rows)} text paths")
    print(f"manifested {len(lines)} uploaded paths plus the manifest itself")


if __name__ == "__main__":
    main()
