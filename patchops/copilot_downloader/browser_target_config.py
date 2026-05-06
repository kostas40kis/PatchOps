from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import urlparse

from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import (
    BLOCKED_BROWSER_TARGET_CONFIG_INVALID,
    BLOCKED_BROWSER_TARGET_CONFIG_MISSING,
    PASS_BROWSER_TARGET_CONFIGURED,
    BrowserTargetConfig,
    DownloaderEvidenceRecord,
)
from patchops.copilot_downloader.safety_policy import default_safety_flags, validate_foundation_boundary

PATCH_NAME = "d1_01_downloader_browser_target_config"
ALLOWED_HOSTS: frozenset[str] = frozenset({"chatgpt.com", "chat.openai.com"})
REQUIRED_FALSE_POLICY_KEYS: tuple[str, ...] = (
    "allow_browser_start",
    "allow_window_scan",
    "allow_dom_automation",
    "allow_clipboard_read",
    "allow_conversation_text_logging",
    "allow_submit_or_send",
)


class BrowserTargetConfigError(ValueError):
    def __init__(self, result_label: str, issues: Sequence[str]):
        super().__init__("; ".join(issues) if issues else result_label)
        self.result_label = result_label
        self.issues = tuple(issues)


def target_url_sha256(target_url: str) -> str:
    return hashlib.sha256(target_url.encode("utf-8")).hexdigest()


def redacted_target_display(target_url: str) -> str:
    parsed = urlparse(target_url)
    host = parsed.netloc.lower()
    if parsed.path and parsed.path != "/":
        return f"{parsed.scheme}://{host}/<redacted-path>"
    return f"{parsed.scheme}://{host}/"


def default_browser_target_payload() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "producer": "patchops.copilot_downloader",
        "description": "D1.1 browser target config. Stores the target URL locally, but evidence emits only a redacted display and URL sha256.",
        "target": {
            "target_url": "https://chatgpt.com/",
            "allowed_hosts": sorted(ALLOWED_HOSTS),
        },
        "paths": {
            "evidence_dir": "data/runtime/copilot_downloader/browser_target_config",
        },
        "policy": {
            "allow_browser_start": False,
            "allow_window_scan": False,
            "allow_dom_automation": False,
            "allow_clipboard_read": False,
            "allow_conversation_text_logging": False,
            "allow_submit_or_send": False,
        },
    }


def write_default_browser_target_config(config_path: str | Path, *, overwrite: bool = False) -> Path:
    path = Path(config_path)
    if path.exists() and not overwrite:
        raise FileExistsError(f"browser target config already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(default_browser_target_payload(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _resolve_repo_child(repo_root: Path, raw_value: Any, key: str) -> Path:
    if not isinstance(raw_value, str) or not raw_value.strip():
        raise BrowserTargetConfigError(BLOCKED_BROWSER_TARGET_CONFIG_INVALID, [f"paths.{key} must be a non-empty string"])
    raw_path = Path(raw_value)
    candidate = raw_path if raw_path.is_absolute() else repo_root / raw_path
    resolved = candidate.resolve(strict=False)
    repo_resolved = repo_root.resolve(strict=False)
    try:
        resolved.relative_to(repo_resolved)
    except ValueError as exc:
        raise BrowserTargetConfigError(BLOCKED_BROWSER_TARGET_CONFIG_INVALID, [f"paths.{key} must resolve under repo root: {raw_value}"]) from exc
    return resolved


def _load_json(config_path: Path) -> dict[str, Any]:
    if not config_path.is_file():
        raise BrowserTargetConfigError(BLOCKED_BROWSER_TARGET_CONFIG_MISSING, [f"browser target config missing: {config_path}"])
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise BrowserTargetConfigError(BLOCKED_BROWSER_TARGET_CONFIG_INVALID, [f"browser target config JSON could not be parsed: {exc}"]) from exc
    if not isinstance(payload, dict):
        raise BrowserTargetConfigError(BLOCKED_BROWSER_TARGET_CONFIG_INVALID, ["browser target config root must be a JSON object"])
    return payload


def validate_target_url(target_url: Any) -> tuple[str, list[str]]:
    issues: list[str] = []
    if not isinstance(target_url, str) or not target_url.strip():
        return "", ["target.target_url must be a non-empty string"]
    parsed = urlparse(target_url)
    if parsed.scheme != "https":
        issues.append("target.target_url must use https")
    host = parsed.netloc.lower()
    if host not in ALLOWED_HOSTS:
        issues.append(f"target.target_url host must be one of: {', '.join(sorted(ALLOWED_HOSTS))}")
    if parsed.username or parsed.password:
        issues.append("target.target_url must not include credentials")
    return target_url, issues


def load_browser_target_config(
    config_path: str | Path,
    *,
    repo_root: str | Path | None = None,
    create_dirs: bool = False,
) -> BrowserTargetConfig:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    path = Path(config_path)
    path = path if path.is_absolute() else root / path
    payload = _load_json(path.resolve(strict=False))

    issues: list[str] = []
    if payload.get("schema_version") != 1:
        issues.append("schema_version must be 1")
    if payload.get("producer") != "patchops.copilot_downloader":
        issues.append("producer must be patchops.copilot_downloader")

    target_payload = payload.get("target")
    if not isinstance(target_payload, dict):
        issues.append("target must be a JSON object")
        target_payload = {}
    paths_payload = payload.get("paths")
    if not isinstance(paths_payload, dict):
        issues.append("paths must be a JSON object")
        paths_payload = {}
    policy_payload = payload.get("policy")
    if not isinstance(policy_payload, dict):
        issues.append("policy must be a JSON object")
        policy_payload = {}

    target_url, target_issues = validate_target_url(target_payload.get("target_url"))
    issues.extend(target_issues)
    if "evidence_dir" not in paths_payload:
        issues.append("paths.evidence_dir is required")
    for key in REQUIRED_FALSE_POLICY_KEYS:
        if key not in policy_payload:
            issues.append(f"policy.{key} is required")
        elif policy_payload.get(key) is not False:
            issues.append(f"policy.{key} must be false for D1.1")

    if issues:
        raise BrowserTargetConfigError(BLOCKED_BROWSER_TARGET_CONFIG_INVALID, issues)

    evidence_dir = _resolve_repo_child(root, paths_payload["evidence_dir"], "evidence_dir")
    config = BrowserTargetConfig(
        config_path=path.resolve(strict=False),
        target_url=target_url,
        target_url_sha256=target_url_sha256(target_url),
        redacted_target_display=redacted_target_display(target_url),
        evidence_dir=evidence_dir,
        policy={key: False for key in REQUIRED_FALSE_POLICY_KEYS},
    )
    if create_dirs:
        config.evidence_dir.mkdir(parents=True, exist_ok=True)
    return config


def validate_browser_target_config_file(
    config_path: str | Path,
    *,
    repo_root: str | Path | None = None,
    create_dirs: bool = False,
) -> tuple[str, list[str], BrowserTargetConfig | None]:
    try:
        config = load_browser_target_config(config_path, repo_root=repo_root, create_dirs=create_dirs)
    except BrowserTargetConfigError as exc:
        return exc.result_label, list(exc.issues), None
    return PASS_BROWSER_TARGET_CONFIGURED, [], config


def run_browser_target_config_doctor(
    *,
    repo_root: str | Path | None = None,
    config_path: str | Path = "data/config/copilot_downloader_browser_target.json",
    evidence_root: str | Path | None = None,
    create_dirs: bool = True,
    write_evidence: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    safety = default_safety_flags()
    boundary_issues = validate_foundation_boundary(safety)
    label, issues, config = validate_browser_target_config_file(config_path, repo_root=root, create_dirs=create_dirs)

    checks: dict[str, bool] = {
        "target_config_validated": label == PASS_BROWSER_TARGET_CONFIGURED,
        "safety_boundary_clean": not boundary_issues,
        "browser_not_started": not safety.browser_used,
        "window_scan_not_performed": True,
        "dom_automation_disabled": not safety.browser_dom_automation_used,
        "clipboard_not_read": not safety.clipboard_read,
        "conversation_text_not_logged": not safety.conversation_text_logged,
        "submit_or_send_not_performed": not safety.chatgpt_submit_performed,
        "uploader_module_not_imported": "patchops.chatgpt_uploader" not in sys.modules,
    }
    details: dict[str, Any] = {
        "repo_root": str(root),
        "config_path": str((root / config_path).resolve(strict=False) if not Path(config_path).is_absolute() else Path(config_path).resolve(strict=False)),
        "issues": issues,
        "boundary_issues": boundary_issues,
    }
    if config is not None:
        checks["evidence_dir_ready"] = config.evidence_dir.is_dir() if create_dirs else True
        details["target"] = config.to_evidence_dict()
    ok = all(checks.values()) and label == PASS_BROWSER_TARGET_CONFIGURED

    evidence_files: dict[str, str] = {}
    if write_evidence:
        evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else (config.evidence_dir if config is not None else root / "data" / "runtime" / "copilot_downloader" / "browser_target_config")
        evidence = DownloaderEvidenceRecord(
            patch_name=PATCH_NAME,
            result_label=label,
            safety=safety,
            details={"checks": checks, **details},
        )
        evidence_files = write_evidence_pair(evidence_dir, "browser_target_config", evidence)

    return {
        "ok": ok,
        "result_label": label,
        "checks": checks,
        "safety": safety.to_dict(),
        "issues": issues,
        "target": None if config is None else config.to_evidence_dict(),
        "evidence_files": evidence_files,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.browser_target_config")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--config-path", default="data/config/copilot_downloader_browser_target.json")
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--create-dirs", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_browser_target_config_doctor(
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