from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence

from patchops.copilot_downloader.browser_target_config import load_browser_target_config
from patchops.copilot_downloader.clipboard_probe import CLIPBOARD_CONFIRM_TEXT, read_clipboard_text_with_tkinter
from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import DownloaderEvidenceRecord, DownloaderSafetyFlags
from patchops.copilot_downloader.script_payload_contract import (
    BLOCKED_SCRIPT_PAYLOAD_CONTRACT_INVALID,
    PASS_SCRIPT_PAYLOAD_CONTRACT_VALIDATED,
    SCRIPT_BEGIN,
    SCRIPT_END,
    sha256_text,
    validate_script_payload_contract_text,
)

PATCH_NAME = "d2_02_downloader_copied_script_extractor_no_run"
PASS_SCRIPT_EXTRACTED_RUN_BLOCKED = "PASS_SCRIPT_EXTRACTED_RUN_BLOCKED"
BLOCKED_SCRIPT_EXTRACTION_NOT_AUTHORIZED = "BLOCKED_SCRIPT_EXTRACTION_NOT_AUTHORIZED"
BLOCKED_SCRIPT_EXTRACTION_EMPTY = "BLOCKED_SCRIPT_EXTRACTION_EMPTY"
BLOCKED_SCRIPT_EXTRACTION_TOO_LARGE = "BLOCKED_SCRIPT_EXTRACTION_TOO_LARGE"
BLOCKED_SCRIPT_EXTRACTION_INVALID = "BLOCKED_SCRIPT_EXTRACTION_INVALID"
BLOCKED_SCRIPT_EXTRACTION_CLIPBOARD_UNAVAILABLE = "BLOCKED_SCRIPT_EXTRACTION_CLIPBOARD_UNAVAILABLE"
CONTROLLED_LABELS: frozenset[str] = frozenset({
    PASS_SCRIPT_EXTRACTED_RUN_BLOCKED,
    BLOCKED_SCRIPT_EXTRACTION_NOT_AUTHORIZED,
    BLOCKED_SCRIPT_EXTRACTION_EMPTY,
    BLOCKED_SCRIPT_EXTRACTION_TOO_LARGE,
    BLOCKED_SCRIPT_EXTRACTION_INVALID,
    BLOCKED_SCRIPT_EXTRACTION_CLIPBOARD_UNAVAILABLE,
})
DEFAULT_MAX_CHARS = 512_000
INVOCATION_RE = re.compile(r"(?s)&\s*\{.*\}\s*$")


def _repo_child(root: Path, *parts: str) -> Path:
    candidate = root.joinpath(*parts).resolve(strict=False)
    root_resolved = root.resolve(strict=False)
    candidate.relative_to(root_resolved)
    return candidate


def _extract_marked_payload(text: str) -> str:
    begin = text.index(SCRIPT_BEGIN)
    end = text.index(SCRIPT_END) + len(SCRIPT_END)
    return text[begin:end]


def _extract_script_from_valid_payload(text: str) -> str:
    begin = text.index(SCRIPT_BEGIN)
    end = text.index(SCRIPT_END)
    inner = text[begin + len(SCRIPT_BEGIN):end].strip("\r\n")
    match = INVOCATION_RE.search(inner)
    if match is None:
        raise ValueError("valid payload unexpectedly lacked invocation block")
    return match.group(0).rstrip() + "\n"


def stage_extracted_script(
    *,
    repo_root: str | Path,
    script_text: str,
    payload_text: str,
    contract_result: dict[str, Any],
    staging_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root).resolve(strict=False)
    script_sha256 = sha256_text(script_text)
    payload_sha256 = sha256_text(payload_text)
    stage_root = Path(staging_root).resolve(strict=False) if staging_root is not None else _repo_child(root, "data", "runtime", "copilot_downloader", "copied_scripts", "staged")
    stage_dir = (stage_root / script_sha256).resolve(strict=False)
    stage_dir.relative_to(root.resolve(strict=False))
    stage_dir.mkdir(parents=True, exist_ok=True)
    script_path = stage_dir / "extracted_script.ps1"
    metadata_path = stage_dir / "metadata.json"
    script_path.write_text(script_text, encoding="utf-8")
    metadata = {
        "schema_version": 1,
        "producer": "patchops.copilot_downloader",
        "patch_name": PATCH_NAME,
        "staged_utc": datetime.now(timezone.utc).isoformat(),
        "script_sha256": script_sha256,
        "payload_sha256": payload_sha256,
        "script_size_chars": len(script_text),
        "payload_size_chars": len(payload_text),
        "script_path": str(script_path),
        "contract_result": contract_result,
        "validation_performed": False,
        "run_authorized": False,
        "script_executed": False,
        "patchops_invoked": False,
        "raw_clipboard_text_logged": False,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "script_sha256": script_sha256,
        "payload_sha256": payload_sha256,
        "stage_dir": str(stage_dir),
        "script_path": str(script_path),
        "metadata_path": str(metadata_path),
        "script_size_chars": len(script_text),
        "payload_size_chars": len(payload_text),
        "validation_performed": False,
        "run_authorized": False,
        "script_executed": False,
        "patchops_invoked": False,
    }


def _write_extractor_evidence(evidence_dir: Path, label: str, safety: DownloaderSafetyFlags, details: dict[str, Any]) -> dict[str, str]:
    evidence = DownloaderEvidenceRecord(
        patch_name=PATCH_NAME,
        result_label=label,
        safety=safety,
        details=details,
    )
    return write_evidence_pair(evidence_dir, "copied_script_extractor", evidence)


def _base_checks(safety: DownloaderSafetyFlags) -> dict[str, bool]:
    return {
        "clipboard_read_requires_confirmation": True,
        "clipboard_not_written": not safety.clipboard_written,
        "browser_not_used": not safety.browser_used,
        "selenium_not_used": not safety.selenium_used,
        "webdriver_not_used": not safety.webdriver_used,
        "dom_automation_not_used": not safety.browser_dom_automation_used,
        "conversation_text_not_logged": not safety.conversation_text_logged,
        "raw_clipboard_text_not_logged": True,
        "script_not_validated_static_yet": True,
        "script_not_executed": not safety.artifact_executed,
        "patchops_not_invoked_by_downloader_runtime": not safety.patchops_invoked,
        "uploader_not_imported": True,
    }


def _blocked_payload(
    *,
    label: str,
    issue: str,
    repo_root: Path,
    browser_target: dict[str, Any],
    safety: DownloaderSafetyFlags | None = None,
    contract_result: dict[str, Any] | None = None,
    evidence_files: dict[str, str] | None = None,
) -> dict[str, Any]:
    actual_safety = safety or DownloaderSafetyFlags()
    checks = _base_checks(actual_safety)
    checks["no_stage_on_blocked_extraction"] = True
    return {
        "ok": label in CONTROLLED_LABELS and all(checks.values()),
        "result_label": label,
        "repo_root": str(repo_root),
        "browser_target": browser_target,
        "issue": issue,
        "contract_result": contract_result,
        "staged_script": None,
        "checks": checks,
        "safety": actual_safety.to_dict(),
        "evidence_files": evidence_files or {},
    }


def run_copied_script_extractor(
    *,
    repo_root: str | Path | None = None,
    browser_config_path: str | Path = "data/config/copilot_downloader_browser_target.json",
    evidence_root: str | Path | None = None,
    live_clipboard: bool = False,
    confirm_clipboard_text: str = "",
    max_chars: int = DEFAULT_MAX_CHARS,
    write_evidence: bool = True,
    clipboard_provider: Callable[[], str] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    config = load_browser_target_config(browser_config_path, repo_root=root, create_dirs=True)
    browser_target = config.to_evidence_dict()
    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else _repo_child(root, "data", "runtime", "copilot_downloader", "d2_02_copied_script_extractor")

    if not live_clipboard:
        label = BLOCKED_SCRIPT_EXTRACTION_NOT_AUTHORIZED
        safety = DownloaderSafetyFlags()
        payload = _blocked_payload(label=label, issue="live_clipboard_flag_required", repo_root=root, browser_target=browser_target, safety=safety)
        if write_evidence:
            payload["evidence_files"] = _write_extractor_evidence(evidence_dir, label, safety, {"issue": payload["issue"], "checks": payload["checks"], "browser_target": browser_target})
        return payload
    if confirm_clipboard_text != CLIPBOARD_CONFIRM_TEXT:
        label = BLOCKED_SCRIPT_EXTRACTION_NOT_AUTHORIZED
        safety = DownloaderSafetyFlags()
        payload = _blocked_payload(label=label, issue="clipboard_confirmation_required", repo_root=root, browser_target=browser_target, safety=safety)
        if write_evidence:
            payload["evidence_files"] = _write_extractor_evidence(evidence_dir, label, safety, {"issue": payload["issue"], "checks": payload["checks"], "browser_target": browser_target})
        return payload

    safety = DownloaderSafetyFlags(clipboard_read=True)
    try:
        provider = clipboard_provider or read_clipboard_text_with_tkinter
        clipboard_text = str(provider())
    except Exception as exc:
        label = BLOCKED_SCRIPT_EXTRACTION_CLIPBOARD_UNAVAILABLE
        payload = _blocked_payload(label=label, issue=f"clipboard_read_failed:{exc}", repo_root=root, browser_target=browser_target, safety=safety)
        if write_evidence:
            payload["evidence_files"] = _write_extractor_evidence(evidence_dir, label, safety, {"issue": payload["issue"], "checks": payload["checks"], "browser_target": browser_target})
        return payload

    if clipboard_text == "":
        label = BLOCKED_SCRIPT_EXTRACTION_EMPTY
        payload = _blocked_payload(label=label, issue="clipboard_empty", repo_root=root, browser_target=browser_target, safety=safety)
        if write_evidence:
            payload["evidence_files"] = _write_extractor_evidence(evidence_dir, label, safety, {"issue": payload["issue"], "checks": payload["checks"], "browser_target": browser_target})
        return payload
    if len(clipboard_text) > max_chars:
        label = BLOCKED_SCRIPT_EXTRACTION_TOO_LARGE
        payload = _blocked_payload(label=label, issue="clipboard_too_large", repo_root=root, browser_target=browser_target, safety=safety)
        if write_evidence:
            payload["evidence_files"] = _write_extractor_evidence(evidence_dir, label, safety, {"issue": payload["issue"], "checks": payload["checks"], "browser_target": browser_target, "clipboard_sha256": sha256_text(clipboard_text), "clipboard_size_chars": len(clipboard_text)})
        return payload

    contract = validate_script_payload_contract_text(clipboard_text)
    contract_payload = contract.to_dict()
    if contract.result_label != PASS_SCRIPT_PAYLOAD_CONTRACT_VALIDATED:
        label = BLOCKED_SCRIPT_EXTRACTION_INVALID
        payload = _blocked_payload(label=label, issue="script_payload_contract_invalid", repo_root=root, browser_target=browser_target, safety=safety, contract_result=contract_payload)
        if write_evidence:
            payload["evidence_files"] = _write_extractor_evidence(evidence_dir, label, safety, {"issue": payload["issue"], "checks": payload["checks"], "browser_target": browser_target, "contract_result": contract_payload})
        return payload

    payload_text = _extract_marked_payload(clipboard_text)
    script_text = _extract_script_from_valid_payload(clipboard_text)
    staged = stage_extracted_script(repo_root=root, script_text=script_text, payload_text=payload_text, contract_result=contract_payload)
    label = PASS_SCRIPT_EXTRACTED_RUN_BLOCKED
    checks = _base_checks(safety)
    checks.update({
        "clipboard_read_performed_after_confirmation": safety.clipboard_read and confirm_clipboard_text == CLIPBOARD_CONFIRM_TEXT,
        "exactly_one_marked_payload_extracted": True,
        "script_staged": Path(staged["script_path"]).is_file(),
        "metadata_written": Path(staged["metadata_path"]).is_file(),
        "script_hash_recorded": len(str(staged["script_sha256"])) == 64,
        "payload_hash_recorded": len(str(staged["payload_sha256"])) == 64,
        "stop_before_static_validation": staged["validation_performed"] is False,
        "stop_before_run": staged["script_executed"] is False and staged["run_authorized"] is False,
    })
    details = {
        "checks": checks,
        "browser_target": browser_target,
        "contract_result": contract_payload,
        "staged_script": staged,
        "raw_clipboard_text_logged": False,
        "raw_script_text_logged": False,
    }
    evidence_files = _write_extractor_evidence(evidence_dir, label, safety, details) if write_evidence else {}
    return {
        "ok": label in CONTROLLED_LABELS and all(checks.values()),
        "result_label": label,
        "repo_root": str(root),
        "browser_target": browser_target,
        "issue": None,
        "contract_result": contract_payload,
        "staged_script": staged,
        "checks": checks,
        "safety": safety.to_dict(),
        "evidence_files": evidence_files,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.copied_script_extractor")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--browser-config-path", default="data/config/copilot_downloader_browser_target.json")
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--live-clipboard", action="store_true")
    parser.add_argument("--confirm-clipboard-text", default="")
    parser.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_copied_script_extractor(
        repo_root=args.repo_root,
        browser_config_path=args.browser_config_path,
        evidence_root=args.evidence_root,
        live_clipboard=args.live_clipboard,
        confirm_clipboard_text=args.confirm_clipboard_text,
        max_chars=args.max_chars,
        write_evidence=not args.no_write_evidence,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())