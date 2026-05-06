from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import (
    CONFIG_INVALID_LABEL,
    CONFIG_MISSING_LABEL,
    CONFIG_VALIDATED_LABEL,
    DownloaderEvidenceRecord,
    DownloaderSafetyFlags,
)
from patchops.copilot_downloader.safety_policy import default_safety_flags, validate_foundation_boundary

PATCH_NAME = "d0_02_downloader_inbox_download_config"
REQUIRED_PATH_KEYS: tuple[str, ...] = (
    "inbox_dir",
    "browser_downloads_dir",
    "staging_dir",
    "evidence_dir",
    "duplicate_ledger_path",
)
REQUIRED_POLICY_KEYS: tuple[str, ...] = (
    "allow_browser_observation",
    "allow_clipboard_read",
    "allow_artifact_detection",
    "allow_artifact_execution",
)
REQUIRED_FALSE_POLICY_KEYS: tuple[str, ...] = (
    "allow_browser_observation",
    "allow_clipboard_read",
    "allow_artifact_execution",
)


class ConfigValidationError(ValueError):
    def __init__(self, result_label: str, issues: Sequence[str]):
        super().__init__("; ".join(issues) if issues else result_label)
        self.result_label = result_label
        self.issues = tuple(issues)


@dataclass(frozen=True)
class DownloaderConfig:
    schema_version: int
    producer: str
    config_path: Path
    repo_root: Path
    inbox_dir: Path
    browser_downloads_dir: Path
    staging_dir: Path
    evidence_dir: Path
    duplicate_ledger_path: Path
    policy: dict[str, bool]

    @property
    def allow_artifact_detection(self) -> bool:
        return bool(self.policy.get("allow_artifact_detection", False))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "producer": self.producer,
            "config_path": str(self.config_path),
            "repo_root": str(self.repo_root),
            "paths": {
                "inbox_dir": str(self.inbox_dir),
                "browser_downloads_dir": str(self.browser_downloads_dir),
                "staging_dir": str(self.staging_dir),
                "evidence_dir": str(self.evidence_dir),
                "duplicate_ledger_path": str(self.duplicate_ledger_path),
            },
            "policy": dict(self.policy),
        }


def default_config_payload() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "producer": "patchops.copilot_downloader",
        "description": "Local-only downloader config. D0.3 allows local artifact detection only; browser observation, clipboard, and execution remain disabled.",
        "paths": {
            "inbox_dir": "data/runtime/copilot_downloader/inbox",
            "browser_downloads_dir": "data/runtime/copilot_downloader/browser_downloads",
            "staging_dir": "data/runtime/copilot_downloader/staged",
            "evidence_dir": "data/runtime/copilot_downloader/evidence",
            "duplicate_ledger_path": "data/runtime/copilot_downloader/ledger/artifact_ledger.jsonl",
        },
        "policy": {
            "allow_browser_observation": False,
            "allow_clipboard_read": False,
            "allow_artifact_detection": True,
            "allow_artifact_execution": False,
        },
    }


def write_default_config(config_path: str | Path, *, overwrite: bool = False) -> Path:
    path = Path(config_path)
    if path.exists() and not overwrite:
        raise FileExistsError(f"config already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(default_config_payload(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _resolve_repo_child(repo_root: Path, raw_value: Any, key: str) -> Path:
    if not isinstance(raw_value, str) or not raw_value.strip():
        raise ConfigValidationError(CONFIG_INVALID_LABEL, [f"paths.{key} must be a non-empty string"])
    raw_path = Path(raw_value)
    candidate = raw_path if raw_path.is_absolute() else repo_root / raw_path
    resolved = candidate.resolve(strict=False)
    repo_resolved = repo_root.resolve(strict=False)
    try:
        resolved.relative_to(repo_resolved)
    except ValueError as exc:
        raise ConfigValidationError(CONFIG_INVALID_LABEL, [f"paths.{key} must resolve under repo root: {raw_value}"]) from exc
    return resolved


def _load_json(config_path: Path) -> dict[str, Any]:
    if not config_path.is_file():
        raise ConfigValidationError(CONFIG_MISSING_LABEL, [f"config file missing: {config_path}"])
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ConfigValidationError(CONFIG_INVALID_LABEL, [f"config JSON could not be parsed: {exc}"]) from exc
    if not isinstance(payload, dict):
        raise ConfigValidationError(CONFIG_INVALID_LABEL, ["config root must be a JSON object"])
    return payload


def load_downloader_config(
    config_path: str | Path,
    *,
    repo_root: str | Path | None = None,
    create_dirs: bool = False,
) -> DownloaderConfig:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    path = Path(config_path)
    path = path if path.is_absolute() else root / path
    payload = _load_json(path.resolve(strict=False))

    issues: list[str] = []
    if payload.get("schema_version") != 1:
        issues.append("schema_version must be 1")
    if payload.get("producer") != "patchops.copilot_downloader":
        issues.append("producer must be patchops.copilot_downloader")
    paths_payload = payload.get("paths")
    if not isinstance(paths_payload, dict):
        issues.append("paths must be a JSON object")
        paths_payload = {}
    policy_payload = payload.get("policy")
    if not isinstance(policy_payload, dict):
        issues.append("policy must be a JSON object")
        policy_payload = {}

    for key in REQUIRED_PATH_KEYS:
        if key not in paths_payload:
            issues.append(f"paths.{key} is required")
    for key in REQUIRED_POLICY_KEYS:
        if key not in policy_payload:
            issues.append(f"policy.{key} is required")
        elif not isinstance(policy_payload.get(key), bool):
            issues.append(f"policy.{key} must be boolean")
    for key in REQUIRED_FALSE_POLICY_KEYS:
        if policy_payload.get(key) is not False:
            issues.append(f"policy.{key} must be false for local downloader config")

    if issues:
        raise ConfigValidationError(CONFIG_INVALID_LABEL, issues)

    resolved_paths: dict[str, Path] = {}
    for key in REQUIRED_PATH_KEYS:
        try:
            resolved_paths[key] = _resolve_repo_child(root, paths_payload[key], key)
        except ConfigValidationError as exc:
            raise ConfigValidationError(CONFIG_INVALID_LABEL, list(exc.issues)) from exc

    config = DownloaderConfig(
        schema_version=1,
        producer="patchops.copilot_downloader",
        config_path=path.resolve(strict=False),
        repo_root=root,
        inbox_dir=resolved_paths["inbox_dir"],
        browser_downloads_dir=resolved_paths["browser_downloads_dir"],
        staging_dir=resolved_paths["staging_dir"],
        evidence_dir=resolved_paths["evidence_dir"],
        duplicate_ledger_path=resolved_paths["duplicate_ledger_path"],
        policy={key: bool(policy_payload[key]) for key in REQUIRED_POLICY_KEYS},
    )

    if create_dirs:
        config.inbox_dir.mkdir(parents=True, exist_ok=True)
        config.browser_downloads_dir.mkdir(parents=True, exist_ok=True)
        config.staging_dir.mkdir(parents=True, exist_ok=True)
        config.evidence_dir.mkdir(parents=True, exist_ok=True)
        config.duplicate_ledger_path.parent.mkdir(parents=True, exist_ok=True)

    return config


def validate_config_file(
    config_path: str | Path,
    *,
    repo_root: str | Path | None = None,
    create_dirs: bool = False,
) -> tuple[str, list[str], DownloaderConfig | None]:
    try:
        config = load_downloader_config(config_path, repo_root=repo_root, create_dirs=create_dirs)
    except ConfigValidationError as exc:
        return exc.result_label, list(exc.issues), None
    return CONFIG_VALIDATED_LABEL, [], config


def run_config_doctor(
    *,
    repo_root: str | Path | None = None,
    config_path: str | Path = "data/config/copilot_downloader_config.json",
    evidence_root: str | Path | None = None,
    create_dirs: bool = False,
    write_evidence: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else root / "data" / "runtime" / "copilot_downloader" / "d0_02_config"
    safety = default_safety_flags()
    boundary_issues = validate_foundation_boundary(safety)
    label, issues, config = validate_config_file(config_path, repo_root=root, create_dirs=create_dirs)

    checks: dict[str, bool] = {
        "config_validated": label == CONFIG_VALIDATED_LABEL,
        "safety_boundary_clean": not boundary_issues,
        "browser_observation_disabled": True,
        "clipboard_read_disabled": True,
        "artifact_execution_disabled": True,
        "uploader_module_not_imported": "patchops.chatgpt_uploader" not in sys.modules,
    }
    details: dict[str, Any] = {
        "repo_root": str(root),
        "config_path": str((root / config_path).resolve(strict=False) if not Path(config_path).is_absolute() else Path(config_path).resolve(strict=False)),
        "issues": issues,
        "boundary_issues": boundary_issues,
    }
    if config is not None:
        checks.update({
            "local_artifact_detection_enabled": config.allow_artifact_detection is True,
            "inbox_dir_ready": config.inbox_dir.is_dir() if create_dirs else True,
            "browser_downloads_dir_ready": config.browser_downloads_dir.is_dir() if create_dirs else True,
            "staging_dir_ready": config.staging_dir.is_dir() if create_dirs else True,
            "evidence_dir_ready": config.evidence_dir.is_dir() if create_dirs else True,
            "ledger_parent_ready": config.duplicate_ledger_path.parent.is_dir() if create_dirs else True,
        })
        details["config"] = config.to_dict()
    ok = all(checks.values()) and label == CONFIG_VALIDATED_LABEL

    evidence = DownloaderEvidenceRecord(
        patch_name=PATCH_NAME,
        result_label=label,
        safety=safety,
        details={"checks": checks, **details},
    )
    evidence_files: dict[str, str] = {}
    if write_evidence:
        evidence_files = write_evidence_pair(evidence_dir, "config_doctor", evidence)

    return {
        "ok": ok,
        "result_label": label,
        "checks": checks,
        "safety": safety.to_dict(),
        "issues": issues,
        "evidence_files": evidence_files,
        "details": details,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.config")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--config-path", default="data/config/copilot_downloader_config.json")
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--create-dirs", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_config_doctor(
        repo_root=args.repo_root,
        config_path=args.config_path,
        evidence_root=args.evidence_root,
        create_dirs=args.create_dirs,
        write_evidence=not args.no_write_evidence,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())