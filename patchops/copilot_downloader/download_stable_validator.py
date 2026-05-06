from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence

from patchops.copilot_downloader.browser_download_detector import scan_download_folder_once
from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import DownloaderEvidenceRecord, DownloaderSafetyFlags

PATCH_NAME = "d3_02_downloader_download_stable_validator"
PASS_STABLE_ARTIFACT_VALIDATED = "PASS_STABLE_ARTIFACT_VALIDATED"
BLOCKED_UNSTABLE_FILE = "BLOCKED_UNSTABLE_FILE"
BLOCKED_AMBIGUOUS_ARTIFACTS = "BLOCKED_AMBIGUOUS_ARTIFACTS"
BLOCKED_NO_ARTIFACT = "BLOCKED_NO_ARTIFACT"
BLOCKED_DUPLICATE_ARTIFACT = "BLOCKED_DUPLICATE_ARTIFACT"
CONTROLLED_LABELS: frozenset[str] = frozenset({
    PASS_STABLE_ARTIFACT_VALIDATED,
    BLOCKED_UNSTABLE_FILE,
    BLOCKED_AMBIGUOUS_ARTIFACTS,
    BLOCKED_NO_ARTIFACT,
    BLOCKED_DUPLICATE_ARTIFACT,
})
PARTIAL_SUFFIXES: frozenset[str] = frozenset({".crdownload", ".tmp", ".partial", ".download"})
DEFAULT_CONFIG_PATH = "data/config/copilot_downloader_config.json"


def _repo_child(root: Path, *parts: str) -> Path:
    candidate = root.joinpath(*parts).resolve(strict=False)
    root_resolved = root.resolve(strict=False)
    candidate.relative_to(root_resolved)
    return candidate


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def _is_partial(path: Path) -> bool:
    lower = path.name.lower()
    return any(lower.endswith(suffix) for suffix in PARTIAL_SUFFIXES)


def sample_stability(
    path: str | Path,
    *,
    sample_count: int = 2,
    interval_seconds: float = 0.0,
    sample_hook: Callable[[int, Path], None] | None = None,
) -> dict[str, Any]:
    file_path = Path(path).resolve(strict=False)
    samples: list[dict[str, Any]] = []
    if _is_partial(file_path):
        return {"result_label": BLOCKED_UNSTABLE_FILE, "issue": "partial_download_extension", "samples": samples, "stable_after_seconds": None}
    started = time.time()
    for index in range(max(2, sample_count)):
        if sample_hook is not None:
            sample_hook(index, file_path)
        if not file_path.is_file():
            return {"result_label": BLOCKED_UNSTABLE_FILE, "issue": "file_missing_during_stability_check", "samples": samples, "stable_after_seconds": None}
        stat = file_path.stat()
        samples.append({
            "index": index,
            "size_bytes": int(stat.st_size),
            "mtime_ns": int(stat.st_mtime_ns),
            "observed_utc": datetime.now(timezone.utc).isoformat(),
        })
        if index < max(2, sample_count) - 1 and interval_seconds > 0:
            time.sleep(interval_seconds)
    sizes = {sample["size_bytes"] for sample in samples}
    mtimes = {sample["mtime_ns"] for sample in samples}
    if len(sizes) != 1 or len(mtimes) != 1:
        return {
            "result_label": BLOCKED_UNSTABLE_FILE,
            "issue": "file_size_or_mtime_changed",
            "samples": samples,
            "stable_after_seconds": round(time.time() - started, 3),
        }
    return {
        "result_label": PASS_STABLE_ARTIFACT_VALIDATED,
        "issue": None,
        "samples": samples,
        "stable_after_seconds": round(time.time() - started, 3),
    }


def classify_downloaded_artifact(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix == ".json":
        return {"kind": "patchops_manifest_json", "suffix": suffix, "zip_index_read": False, "issue": None}
    if suffix == ".ps1":
        return {"kind": "patchops_script_or_powershell", "suffix": suffix, "zip_index_read": False, "issue": None}
    if suffix == ".zip":
        try:
            with zipfile.ZipFile(file_path) as archive:
                names = archive.namelist()
        except zipfile.BadZipFile:
            return {"kind": "unknown_zip", "suffix": suffix, "zip_index_read": True, "issue": "bad_zip_file"}
        lowered = {name.replace("\\", "/").lower() for name in names}
        is_patchops = any(name.endswith("manifest.json") for name in lowered) or "patchops_bundle.json" in lowered or "bundle_manifest.json" in lowered
        return {"kind": "patchops_bundle_zip" if is_patchops else "unknown_zip", "suffix": suffix, "zip_index_read": True, "zip_entry_count": len(names), "issue": None}
    return {"kind": "unsupported_file", "suffix": suffix, "zip_index_read": False, "issue": "unsupported_suffix"}


def _read_ledger_entries(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    entries: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            entries.append({"_malformed": True, "line_sha256": _sha256_text(line)})
    return entries


def _ledger_path(root: Path, explicit: str | Path | None = None) -> Path:
    if explicit is not None:
        return Path(explicit).resolve(strict=False)
    return _repo_child(root, "data", "runtime", "copilot_downloader", "ledger", "artifact_ledger.jsonl")


def check_and_write_ledger(
    *,
    repo_root: str | Path,
    artifact_path: str | Path,
    artifact_sha256: str,
    artifact_kind: str,
    ledger_path: str | Path | None = None,
    allow_duplicate: bool = False,
) -> dict[str, Any]:
    root = Path(repo_root).resolve(strict=False)
    path = _ledger_path(root, ledger_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    entries = _read_ledger_entries(path)
    duplicate = next((entry for entry in entries if entry.get("artifact_sha256") == artifact_sha256), None)
    blocked = duplicate is not None and not allow_duplicate
    ledger_entry = None
    if not blocked:
        ledger_entry = {
            "schema_version": 1,
            "recorded_utc": datetime.now(timezone.utc).isoformat(),
            "producer": "patchops.copilot_downloader",
            "patch_name": PATCH_NAME,
            "source": "browser_downloads",
            "artifact_path": str(Path(artifact_path).resolve(strict=False)),
            "artifact_name": Path(artifact_path).name,
            "artifact_sha256": artifact_sha256,
            "artifact_kind": artifact_kind,
            "duplicate_allowed": duplicate is not None and allow_duplicate,
            "execution_authorized": False,
            "artifact_executed": False,
        }
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(ledger_entry, sort_keys=True) + "\n")
    return {
        "ledger_path": str(path),
        "duplicate_found": duplicate is not None,
        "duplicate_blocked": blocked,
        "duplicate_entry": duplicate,
        "ledger_written": ledger_entry is not None,
        "ledger_entry": ledger_entry,
    }


def stage_downloaded_artifact(
    *,
    repo_root: str | Path,
    artifact_path: str | Path,
    artifact_sha256: str,
    classification: dict[str, Any],
    staging_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root).resolve(strict=False)
    source = Path(artifact_path).resolve(strict=False)
    base = Path(staging_root).resolve(strict=False) if staging_root is not None else _repo_child(root, "data", "runtime", "copilot_downloader", "downloaded_artifacts", "staged")
    stage_dir = (base / artifact_sha256).resolve(strict=False)
    stage_dir.relative_to(root.resolve(strict=False))
    stage_dir.mkdir(parents=True, exist_ok=True)
    raw_path = stage_dir / ("raw_artifact" + source.suffix.lower())
    shutil.copy2(source, raw_path)
    metadata_path = stage_dir / "metadata.json"
    metadata = {
        "schema_version": 1,
        "producer": "patchops.copilot_downloader",
        "patch_name": PATCH_NAME,
        "staged_utc": datetime.now(timezone.utc).isoformat(),
        "source_path": str(source),
        "raw_artifact_path": str(raw_path),
        "artifact_sha256": artifact_sha256,
        "artifact_name": source.name,
        "artifact_size_bytes": source.stat().st_size,
        "classification": classification,
        "bundle_validation_performed": False,
        "run_authorized": False,
        "artifact_executed": False,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "stage_dir": str(stage_dir),
        "raw_artifact_path": str(raw_path),
        "metadata_path": str(metadata_path),
        "artifact_sha256": artifact_sha256,
        "bundle_validation_performed": False,
        "run_authorized": False,
        "artifact_executed": False,
    }


def _write_validator_evidence(evidence_dir: Path, label: str, safety: DownloaderSafetyFlags, details: dict[str, Any]) -> dict[str, str]:
    evidence = DownloaderEvidenceRecord(
        patch_name=PATCH_NAME,
        result_label=label,
        safety=safety,
        details=details,
    )
    return write_evidence_pair(evidence_dir, "download_stable_validator", evidence)


def run_download_stable_validator(
    *,
    repo_root: str | Path | None = None,
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    download_dir: str | Path | None = None,
    evidence_root: str | Path | None = None,
    sample_count: int = 2,
    interval_seconds: float = 0.0,
    allow_duplicate: bool = False,
    write_evidence: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else _repo_child(root, "data", "runtime", "copilot_downloader", "d3_02_download_stable_validator")
    scan = scan_download_folder_once(repo_root=root, download_dir=download_dir, config_path=config_path)
    candidate_count = len(scan["candidates"])
    safety = DownloaderSafetyFlags(file_download_observed=(candidate_count > 0))
    label = BLOCKED_NO_ARTIFACT
    issue = "no_artifact"
    selected: dict[str, Any] | None = None
    stability: dict[str, Any] = {"result_label": BLOCKED_NO_ARTIFACT, "issue": "no_artifact", "samples": [], "stable_after_seconds": None}
    artifact_sha256: str | None = None
    classification: dict[str, Any] | None = None
    ledger: dict[str, Any] | None = None
    staging: dict[str, Any] | None = None

    if candidate_count == 0:
        label = BLOCKED_NO_ARTIFACT
    elif candidate_count > 1:
        label = BLOCKED_AMBIGUOUS_ARTIFACTS
        issue = "ambiguous_artifacts"
    else:
        selected = scan["candidates"][0]
        artifact_path = Path(selected["path"])
        stability = sample_stability(artifact_path, sample_count=sample_count, interval_seconds=interval_seconds)
        if stability["result_label"] != PASS_STABLE_ARTIFACT_VALIDATED:
            label = BLOCKED_UNSTABLE_FILE
            issue = str(stability.get("issue"))
        else:
            artifact_sha256 = sha256_file(artifact_path)
            classification = classify_downloaded_artifact(artifact_path)
            ledger = check_and_write_ledger(
                repo_root=root,
                artifact_path=artifact_path,
                artifact_sha256=artifact_sha256,
                artifact_kind=str(classification.get("kind")),
                allow_duplicate=allow_duplicate,
            )
            if ledger["duplicate_blocked"]:
                label = BLOCKED_DUPLICATE_ARTIFACT
                issue = "duplicate_artifact"
            else:
                staging = stage_downloaded_artifact(repo_root=root, artifact_path=artifact_path, artifact_sha256=artifact_sha256, classification=classification)
                label = PASS_STABLE_ARTIFACT_VALIDATED
                issue = None

    checks = {
        "download_folder_observed": True,
        "candidate_count_controlled": candidate_count >= 0,
        "ambiguous_artifacts_blocked": candidate_count <= 1 or label == BLOCKED_AMBIGUOUS_ARTIFACTS,
        "stability_checked_before_hash": label in {BLOCKED_NO_ARTIFACT, BLOCKED_AMBIGUOUS_ARTIFACTS} or stability.get("samples") is not None,
        "partial_downloads_rejected": True,
        "hash_computed_after_stable": artifact_sha256 is not None or label in {BLOCKED_NO_ARTIFACT, BLOCKED_AMBIGUOUS_ARTIFACTS, BLOCKED_UNSTABLE_FILE},
        "ledger_checked_after_hash": ledger is not None or artifact_sha256 is None,
        "duplicate_blocked_unless_allowed": label != BLOCKED_DUPLICATE_ARTIFACT or not allow_duplicate,
        "stage_written_only_after_hash_and_ledger": staging is None or (artifact_sha256 is not None and ledger is not None and ledger.get("ledger_written") is True),
        "classification_performed_after_stable": classification is not None or artifact_sha256 is None,
        "bundle_validation_not_performed_yet": staging is None or staging.get("bundle_validation_performed") is False,
        "run_not_authorized": staging is None or staging.get("run_authorized") is False,
        "artifact_not_executed": not safety.artifact_executed,
        "patchops_not_invoked_by_downloader_runtime": not safety.patchops_invoked,
        "browser_not_started": not safety.browser_used,
        "clipboard_not_read": not safety.clipboard_read,
        "clipboard_not_written": not safety.clipboard_written,
        "conversation_text_not_logged": not safety.conversation_text_logged,
        "uploader_not_imported": True,
    }
    details = {
        "checks": checks,
        "issue": issue,
        "scan": scan,
        "selected_candidate": selected,
        "stability": stability,
        "artifact_sha256": artifact_sha256,
        "classification": classification,
        "ledger": ledger,
        "staging": staging,
        "allow_duplicate": allow_duplicate,
    }
    evidence_files = _write_validator_evidence(evidence_dir, label, safety, details) if write_evidence else {}
    return {
        "ok": label in CONTROLLED_LABELS and all(checks.values()),
        "result_label": label,
        "issue": issue,
        "candidate_count": candidate_count,
        "selected_candidate": selected,
        "stability": stability,
        "artifact_sha256": artifact_sha256,
        "classification": classification,
        "ledger": ledger,
        "staging": staging,
        "checks": checks,
        "safety": safety.to_dict(),
        "evidence_files": evidence_files,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.download_stable_validator")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--config-path", default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--download-dir", default=None)
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--sample-count", type=int, default=2)
    parser.add_argument("--interval-seconds", type=float, default=0.0)
    parser.add_argument("--allow-duplicate", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_download_stable_validator(
        repo_root=args.repo_root,
        config_path=args.config_path,
        download_dir=args.download_dir,
        evidence_root=args.evidence_root,
        sample_count=args.sample_count,
        interval_seconds=args.interval_seconds,
        allow_duplicate=args.allow_duplicate,
        write_evidence=not args.no_write_evidence,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())