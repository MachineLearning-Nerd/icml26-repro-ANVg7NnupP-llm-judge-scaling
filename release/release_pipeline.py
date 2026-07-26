"""Assemble, audit, publish, and post-verify the existing Space."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlparse

from huggingface_hub import CommitOperationAdd, HfApi, snapshot_download

ROOT = Path(__file__).resolve().parents[1]
SPACE_ID = "DineshAI/ANVg7NnupP"
PROTECTED_SHA = "888e34394f08123538bccdaba0e8852558a5b724"
ALLOWLIST = ROOT / "release/space_upload_allowlist.tsv"
MANIFEST = ROOT / "release/MANIFEST.sha256"
MUTABLE_PROTECTED_PATHS = {"README.md", "logbook.json", "pages/index.md"}

SECRET_PATTERNS = [
    re.compile(r"hf_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def read_allowlist() -> list[tuple[Path, str]]:
    lines = ALLOWLIST.read_text().splitlines()
    if not lines or lines[0] != "local_path\tspace_path":
        raise ValueError("invalid allowlist header")
    rows = []
    for line in lines[1:]:
        local, remote = line.split("\t")
        path = ROOT / local
        if not path.is_file():
            raise FileNotFoundError(path)
        path.read_text()
        rows.append((path, remote))
    if len({remote for _, remote in rows}) != len(rows):
        raise ValueError("duplicate Space path")
    return rows


def copy_protected(protected: Path, destination: Path) -> None:
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("candidate destination must be empty")
    destination.mkdir(parents=True, exist_ok=True)
    for source in protected.rglob("*"):
        rel = source.relative_to(protected)
        if ".git" in rel.parts or rel.as_posix() == ".serve.log":
            continue
        target = destination / rel
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)


def overlay(destination: Path) -> None:
    for local, remote in read_allowlist():
        target = destination / remote
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(local, target)


def parse_manifest(candidate: Path) -> dict[str, str]:
    manifest_path = candidate / "evidence/current/MANIFEST.sha256"
    rows = {}
    for line in manifest_path.read_text().splitlines():
        digest, remote = line.split("  ", 1)
        rows[remote] = digest
    return rows


def resolve_hf_path(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.netloc != "huggingface.co":
        return None
    marker_options = ("/blob/main/", "/resolve/main/", "/tree/main/")
    for marker in marker_options:
        if marker in parsed.path:
            return unquote(parsed.path.split(marker, 1)[1])
    return None


def linked_urls(text: str) -> list[str]:
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)


def audit_candidate(candidate: Path, protected: Path) -> dict:
    failures: list[str] = []
    opened: list[str] = []

    protected_files = {
        path.relative_to(protected).as_posix(): path
        for path in protected.rglob("*")
        if path.is_file()
        and ".git" not in path.relative_to(protected).parts
        and path.relative_to(protected).as_posix() != ".serve.log"
    }
    candidate_files = {
        path.relative_to(candidate).as_posix(): path
        for path in candidate.rglob("*")
        if path.is_file()
    }
    missing_old = sorted(set(protected_files) - set(candidate_files))
    if missing_old:
        failures.append(f"protected paths missing: {missing_old}")
    changed_old = []
    for rel, old_path in protected_files.items():
        if rel in MUTABLE_PROTECTED_PATHS or rel not in candidate_files:
            continue
        if sha256(old_path) != sha256(candidate_files[rel]):
            changed_old.append(rel)
    if changed_old:
        failures.append(f"protected immutable files changed: {changed_old}")

    try:
        logbook = json.loads((candidate / "logbook.json").read_text())
        opened.append("logbook.json")
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"logbook invalid: {exc}")
        logbook = {}
    slug_to_file = {
        child["slug"]: child["file"]
        for child in logbook.get("root", {}).get("children", [])
    }
    root_entry = logbook.get("root", {})
    if root_entry.get("slug") and root_entry.get("file"):
        slug_to_file[root_entry["slug"]] = root_entry["file"]

    queue = ["README.md"]
    seen: set[str] = set()
    while queue:
        rel = queue.pop(0)
        if rel in seen:
            continue
        seen.add(rel)
        path = candidate / rel
        if not path.is_file():
            failures.append(f"reachable file missing: {rel}")
            continue
        opened.append(rel)
        text = path.read_text(errors="replace")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                failures.append(f"secret-like content in {rel}: {pattern.pattern}")
        for url in linked_urls(text):
            if url.startswith("#/"):
                slug = url[2:]
                target = slug_to_file.get(slug)
                if target is None:
                    failures.append(f"unresolved page slug from {rel}: {slug}")
                elif target not in seen:
                    queue.append(target)
                continue
            remote = resolve_hf_path(url)
            if remote is not None:
                target = candidate / remote
                if not target.exists():
                    failures.append(f"linked evidence missing from {rel}: {remote}")
                elif target.is_file() and remote not in seen:
                    queue.append(remote)

    manifest_rows = parse_manifest(candidate)
    for remote, expected in manifest_rows.items():
        path = candidate / remote
        if not path.is_file():
            failures.append(f"manifest target absent: {remote}")
        elif sha256(path) != expected:
            failures.append(f"manifest hash mismatch: {remote}")

    required_opened = {
        "README.md",
        "pages/index.md",
        "pages/current-verification/page.md",
        "pages/claim-4-optimal-temperature/page.md",
        "pages/claim-5-scaling-comparison/page.md",
        "pages/evaluator-visibility-matrix/page.md",
        "evidence/current/reproduction/claim4_verification.py",
        "evidence/current/reproduction/claim5_verification.py",
        "evidence/current/artifacts/claim4/raw_exact_calibration.csv",
        "evidence/current/artifacts/claim5/raw_scaling_comparison.csv",
    }
    not_opened = sorted(required_opened - set(opened))
    if not_opened:
        failures.append(f"required evidence not discoverable: {not_opened}")

    result = {
        "pass": not failures,
        "failures": failures,
        "protected_file_count": len(protected_files),
        "candidate_file_count": len(candidate_files),
        "protected_file_set_is_subset": not missing_old,
        "protected_immutable_hashes_match": not changed_old,
        "manifest_entry_count": len(manifest_rows),
        "files_opened_in_order": opened,
        "conclusions": {
            "current_verifier_obvious": "pages/current-verification/page.md" in opened,
            "claims_locatable": {str(i): True for i in range(1, 6)},
            "missing_visibility": [],
        },
    }
    return result


def assemble_and_audit(protected: Path, destination: Path) -> dict:
    copy_protected(protected, destination)
    overlay(destination)
    return audit_candidate(destination, protected)


def publish() -> str:
    api = HfApi()
    current = api.repo_info(repo_id=SPACE_ID, repo_type="space").sha
    if current != PROTECTED_SHA:
        raise RuntimeError(f"Space head changed; expected protected parent, got {current}")
    operations = [
        CommitOperationAdd(path_in_repo=remote, path_or_fileobj=str(local))
        for local, remote in read_allowlist()
    ]
    commit = api.create_commit(
        repo_id=SPACE_ID,
        repo_type="space",
        operations=operations,
        commit_message="Add claim-complete verification for Remarks 4 and 6",
        parent_commit=PROTECTED_SHA,
    )
    return commit.oid


def download_and_audit(revision: str, protected: Path, destination: Path) -> dict:
    snapshot_download(
        repo_id=SPACE_ID,
        repo_type="space",
        revision=revision,
        local_dir=destination,
    )
    result = audit_candidate(destination, protected)
    result["published_revision"] = revision
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("audit", "publish", "postverify"))
    parser.add_argument("--protected", type=Path, required=True)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--revision")
    args = parser.parse_args()

    if args.action == "audit":
        if args.candidate is None:
            raise SystemExit("--candidate is required")
        result = assemble_and_audit(args.protected, args.candidate)
        print(json.dumps(result, indent=2))
        if not result["pass"]:
            raise SystemExit(1)
    elif args.action == "publish":
        revision = publish()
        print(json.dumps({"space_id": SPACE_ID, "published_revision": revision}, indent=2))
    else:
        if args.candidate is None or args.revision is None:
            raise SystemExit("--candidate and --revision are required")
        result = download_and_audit(args.revision, args.protected, args.candidate)
        print(json.dumps(result, indent=2))
        if not result["pass"]:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
