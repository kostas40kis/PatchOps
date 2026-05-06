from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from patchops.copilot_downloader.config import load_downloader_config
from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import (
    BLOCKED_DUPLICATE_ARTIFACT,
    PASS_HASH_LEDGER_RECORDED,
    DownloaderEvidenceRecord,
)
from patchops.copilot_downloader.safety_policy import default_safety_flags
from patchops.copilot_downloader.stable_detector import STABLE_PASS_LABEL, run_stable_artifact_scan

PATCH_NAME = "d0_05_downloader_hash_duplicate_ledger"
CONTROLLED_LABELS: frozenset[str] = frozenset({
    PASS_HASH_LEDGER_RECORDED,
    BLOCKED_DUPLICATE_ARTIFACT,
    "BLOCKED_NO_ARTIFACT",
    "BLOCKED_UNSTABLE_FILE",
    "BLOCKED_AMBIGUOUS_ARTIFACTS",
})


@dataclass(frozen=True)
class LedgerEntry:
    schema_version: int
    recorded_utc: str
    artifact_sha256: str
    artifact_path: str
    source: str
    extension: str
    size_bytes: int
    status: str
    duplicate_allowed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "recorded_utc": self.recorded_utc,
            "artifact_sha256": self.artifact_sha256,
            "artifact_path": self.artifact_path,
            "source": self.source,
            "extension": self.extension,
            "size_bytes": self.size_bytes,
            "status": self.status,
            "duplicate_allowed": self.duplicate_allowed,
        }


def compute_sha256(path: str | Path, *, chunk_size: int = 1024 * 1024) -> str:
    artifact_path = Path(path)
    digest = hashlib.sha256()
    with artifact_path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def read_ledger_entries(ledger_path: str | Path) -> tuple[dict[str, Any], ...]:
    path = Path(ledger_path)
    if not path.exists():
        return ()
    entries: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            payload = {"schema_version": 0, "invalid_line_number": line_number, "raw_line": line}
        if isinstance(payload, dict):
            entries.append(payload)
    return tuple(entries)


def find_duplicate_entry(ledger_path: str | Path, artifact_sha256: str) -> dict[str, Any] | None:
    normalized = artifact_sha256.lower()
    for entry in read_ledger_entries(ledger_path):
        if str(entry.get("artifact_sha256", "")).lower() == normalized:
            return entry
    return None


def append_ledger_entry(ledger_path: str | Path, entry: LedgerEntry) -> Path:
    path = Path(ledger_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(entry.to_dict(), sort_keys=True) + "\n")
    return path


def build_ledger_entry(
    *,
    artifact_sha256: str,
    candidate: dict[str, Any],
    status: str,
    duplicate_allowed: bool,
) -> LedgerEntry:
    return LedgerEntry(
        schema_version=1,
        recorded_utc=datetime.now(timezone.utc).isoformat(),
        artifact_sha256=artifact_sha256.lower(),
        artifact_path=str(candidate["path"]),
        source=str(candidate.get("source", "unknown")),
        extension=str(candidate.get("extension", "")),
        size_bytes=int(candidate.get("size_bytes", 0)),
        status=status,
        duplicate_allowed=bool(duplicate_allowed),
    )


def run_hash_ledger_scan(
    *,
    repo_root: str | Path | None = None,
    config_path: str | Path = "data/config/copilot_downloader_config.json",
    evidence_root: str | Path | None = None,
    create_dirs: bool = True,
    write_evidence: bool = True,
    sample_count: int = 3,
    interval_seconds: float = 0.2,
    allow_duplicate: bool = False,
    max_candidates: int = 50,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    config = load_downloader_config(config_path, repo_root=root, create_dirs=create_dirs)
    safety = default_safety_flags()
    stable_payload = run_stable_artifact_scan(
        repo_root=root,
        config_path=config.config_path,
        evidence_root=evidence_root,
        create_dirs=create_dirs,
        write_evidence=False,
        sample_count=sample_count,
        interval_seconds=interval_seconds,
        max_candidates=max_candidates,
    )

    label = str(stable_payload["result_label"])
    artifact_sha256: str | None = None
    duplicate_entry: dict[str, Any] | None = None
    ledger_entry: LedgerEntry | None = None
    ledger_written = False

    if label == STABLE_PASS_LABEL:
        candidate = stable_payload["stable_validation"]["candidate"]
        artifact_path = Path(candidate["path"])
        artifact_sha256 = compute_sha256(artifact_path)
        duplicate_entry = find_duplicate_entry(config.duplicate_ledger_path, artifact_sha256)
        if duplicate_entry is not None and not allow_duplicate:
            label = BLOCKED_DUPLICATE_ARTIFACT
        else:
            status = "duplicate_allowed_recorded" if duplicate_entry is not None else "recorded"
            ledger_entry = build_ledger_entry(
                artifact_sha256=artifact_sha256,
                candidate=candidate,
                status=status,
                duplicate_allowed=allow_duplicate,
            )
            append_ledger_entry(config.duplicate_ledger_path, ledger_entry)
            ledger_written = True
            label = PASS_HASH_LEDGER_RECORDED

    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else config.evidence_dir / "d0_05_hash_ledger"
    checks = {
        "browser_not_used": not safety.browser_used,
        "clipboard_not_used": not safety.clipboard_read and not safety.clipboard_written,
        "artifact_not_executed": not safety.artifact_executed,
        "staging_not_performed": True,
        "patchops_not_invoked_by_downloader_runtime": not safety.patchops_invoked,
        "ledger_parent_ready": config.duplicate_ledger_path.parent.exists(),
    }
    evidence = DownloaderEvidenceRecord(
        patch_name=PATCH_NAME,
        result_label=label,
        safety=safety,
        details={
            "checks": checks,
            "config": config.to_dict(),
            "stable_payload": stable_payload,
            "artifact_sha256": artifact_sha256,
            "duplicate_entry": duplicate_entry,
            "ledger_entry": None if ledger_entry is None else ledger_entry.to_dict(),
            "ledger_path": str(config.duplicate_ledger_path),
            "ledger_written": ledger_written,
            "allow_duplicate": allow_duplicate,
        },
    )
    evidence_files: dict[str, str] = {}
    if write_evidence:
        evidence_files = write_evidence_pair(evidence_dir, "hash_ledger", evidence)

    return {
        "ok": label in CONTROLLED_LABELS and all(checks.values()),
        "result_label": label,
        "artifact_sha256": artifact_sha256,
        "duplicate_found": duplicate_entry is not None,
        "duplicate_entry": duplicate_entry,
        "ledger_written": ledger_written,
        "ledger_path": str(config.duplicate_ledger_path),
        "ledger_entry": None if ledger_entry is None else ledger_entry.to_dict(),
        "checks": checks,
        "safety": safety.to_dict(),
        "stable_payload": stable_payload,
        "evidence_files": evidence_files,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.ledger")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--config-path", default="data/config/copilot_downloader_config.json")
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--no-create-dirs", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    parser.add_argument("--sample-count", type=int, default=3)
    parser.add_argument("--interval-seconds", type=float, default=0.2)
    parser.add_argument("--allow-duplicate", action="store_true")
    parser.add_argument("--max-candidates", type=int, default=50)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_hash_ledger_scan(
        repo_root=args.repo_root,
        config_path=args.config_path,
        evidence_root=args.evidence_root,
        create_dirs=not args.no_create_dirs,
        write_evidence=not args.no_write_evidence,
        sample_count=args.sample_count,
        interval_seconds=args.interval_seconds,
        allow_duplicate=args.allow_duplicate,
        max_candidates=args.max_candidates,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())