from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from patchops.copilot_downloader.copied_script_static_validator import (
    BLOCKED_INVALID_SCRIPT,
    PASS_SCRIPT_VALIDATED_RUN_BLOCKED,
    find_latest_staged_script,
    safe_patchops_script_sample,
    validate_copied_script_static_file,
)
from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import DownloaderEvidenceRecord, DownloaderSafetyFlags
from patchops.copilot_downloader.script_payload_contract import REQUIRED_CONFIRMATION, sha256_text

PATCH_NAME = "d2_04_downloader_script_explicit_run_gate"
PASS_SCRIPT_RUN_AUTHORIZED = "PASS_SCRIPT_RUN_AUTHORIZED"
BLOCKED_RUN_NOT_AUTHORIZED = "BLOCKED_RUN_NOT_AUTHORIZED"
CONTROLLED_LABELS: frozenset[str] = frozenset({
    PASS_SCRIPT_VALIDATED_RUN_BLOCKED,
    PASS_SCRIPT_RUN_AUTHORIZED,
    BLOCKED_RUN_NOT_AUTHORIZED,
    BLOCKED_INVALID_SCRIPT,
})


def _repo_child(root: Path, *parts: str) -> Path:
    candidate = root.joinpath(*parts).resolve(strict=False)
    root_resolved = root.resolve(strict=False)
    candidate.relative_to(root_resolved)
    return candidate


def write_sample_staged_script(repo_root: str | Path, *, staging_root: str | Path | None = None) -> Path:
    root = Path(repo_root).resolve(strict=False)
    script_text = safe_patchops_script_sample()
    script_sha256 = sha256_text(script_text)
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
        "sample_staged_script": True,
        "staged_utc": datetime.now(timezone.utc).isoformat(),
        "script_sha256": script_sha256,
        "script_path": str(script_path),
        "validation_performed": True,
        "run_authorized": False,
        "script_executed": False,
        "patchops_invoked": False,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return script_path


def _select_staged_script(root: Path, explicit_path: str | Path | None, allow_sample_when_missing: bool) -> tuple[Path | None, bool]:
    if explicit_path is not None:
        return Path(explicit_path).resolve(strict=False), False
    latest = find_latest_staged_script(root)
    if latest is not None:
        return latest.resolve(strict=False), False
    if allow_sample_when_missing:
        return write_sample_staged_script(root), True
    return None, False


def _write_authorization_file(script_path: Path, validation_result: dict[str, Any], evidence_dir: Path) -> Path:
    authorization_path = (script_path.parent / "run_authorization.json").resolve(strict=False)
    payload = {
        "schema_version": 1,
        "producer": "patchops.copilot_downloader",
        "patch_name": PATCH_NAME,
        "authorized_utc": datetime.now(timezone.utc).isoformat(),
        "authorized": True,
        "requires_confirmation": REQUIRED_CONFIRMATION,
        "confirm_run_text_matched": True,
        "allow_run_supplied": True,
        "script_path": str(script_path),
        "script_sha256": validation_result.get("script_sha256"),
        "validation_result_label": validation_result.get("result_label"),
        "run_performed": False,
        "patchops_invoked": False,
        "bounded_runner_required_next": True,
        "evidence_dir": str(evidence_dir),
    }
    authorization_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return authorization_path


def _write_gate_evidence(evidence_dir: Path, label: str, safety: DownloaderSafetyFlags, details: dict[str, Any]) -> dict[str, str]:
    evidence = DownloaderEvidenceRecord(
        patch_name=PATCH_NAME,
        result_label=label,
        safety=safety,
        details=details,
    )
    return write_evidence_pair(evidence_dir, "script_run_gate", evidence)


def run_script_explicit_run_gate(
    *,
    repo_root: str | Path | None = None,
    evidence_root: str | Path | None = None,
    staged_script_path: str | Path | None = None,
    allow_run: bool = False,
    confirm_run_text: str = "",
    allow_sample_when_missing: bool = True,
    write_evidence: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else _repo_child(root, "data", "runtime", "copilot_downloader", "d2_04_script_run_gate")
    safety = DownloaderSafetyFlags()
    selected_script_path, used_sample = _select_staged_script(root, staged_script_path, allow_sample_when_missing)
    authorization_path: Path | None = None

    if selected_script_path is None:
        validation_payload: dict[str, Any] = {
            "ok": False,
            "result_label": BLOCKED_INVALID_SCRIPT,
            "issues": ["no staged script available for run gate"],
            "script_path": None,
            "raw_script_logged": False,
            "script_executed": False,
            "patchops_invoked": False,
        }
        label = BLOCKED_INVALID_SCRIPT
        issue = "staged_validated_script_required"
    else:
        validation = validate_copied_script_static_file(selected_script_path)
        validation_payload = validation.to_dict()
        if validation.result_label != PASS_SCRIPT_VALIDATED_RUN_BLOCKED:
            label = BLOCKED_INVALID_SCRIPT
            issue = "staged_script_static_validation_failed"
        elif allow_run and confirm_run_text == REQUIRED_CONFIRMATION:
            label = PASS_SCRIPT_RUN_AUTHORIZED
            issue = None
            authorization_path = _write_authorization_file(selected_script_path, validation_payload, evidence_dir)
        elif allow_run and confirm_run_text != REQUIRED_CONFIRMATION:
            label = BLOCKED_RUN_NOT_AUTHORIZED
            issue = "confirm_run_text_required"
        else:
            label = PASS_SCRIPT_VALIDATED_RUN_BLOCKED
            issue = "allow_run_required"

    authorized = label == PASS_SCRIPT_RUN_AUTHORIZED
    validation_label = validation_payload.get("result_label")
    validation_passed = validation_label == PASS_SCRIPT_VALIDATED_RUN_BLOCKED
    validation_blocked = validation_label == BLOCKED_INVALID_SCRIPT
    no_staged_script_block = issue == "staged_validated_script_required"
    invalid_script_block = issue == "staged_script_static_validation_failed"
    checks = {
        "run_gate_evaluated": True,
        "staged_script_required_or_controlled_block": selected_script_path is not None or no_staged_script_block,
        "static_validation_required": True,
        "static_validation_passed_or_controlled_block": validation_passed or validation_blocked,
        "invalid_script_not_authorized": validation_passed or validation_blocked and not authorized,
        "allow_run_flag_required_for_authorization": (not authorized) or allow_run,
        "confirm_run_text_required_for_authorization": (not authorized) or confirm_run_text == REQUIRED_CONFIRMATION,
        "authorization_only_after_validation_and_confirmation": (not authorized) or (validation_passed and allow_run and confirm_run_text == REQUIRED_CONFIRMATION),
        "run_not_authorized_unless_validated_and_confirmed": authorized or (not allow_run) or (confirm_run_text != REQUIRED_CONFIRMATION) or validation_blocked,
        "no_staged_script_never_authorized": (not no_staged_script_block) or not authorized,
        "invalid_script_with_confirmation_still_not_authorized": (not invalid_script_block) or not authorized,
        "authorization_metadata_written_when_authorized": (not authorized) or (authorization_path is not None and authorization_path.is_file()),
        "script_not_executed": not safety.artifact_executed,
        "patchops_not_invoked_by_downloader_runtime": not safety.patchops_invoked,
        "clipboard_not_read": not safety.clipboard_read,
        "clipboard_not_written": not safety.clipboard_written,
        "browser_not_used": not safety.browser_used,
        "conversation_text_not_logged": not safety.conversation_text_logged,
        "raw_script_not_logged": True,
        "uploader_not_imported": True,
    }
    details = {
        "checks": checks,
        "issue": issue,
        "allow_run": allow_run,
        "confirm_run_text_supplied": bool(confirm_run_text),
        "confirm_run_text_matched": confirm_run_text == REQUIRED_CONFIRMATION,
        "used_sample_staged_script": used_sample,
        "selected_staged_script_path": None if selected_script_path is None else str(selected_script_path),
        "authorization_path": None if authorization_path is None else str(authorization_path),
        "authorization_state": {
            "authorized": authorized,
            "run_performed": False,
            "bounded_runner_required_next": authorized,
        },
        "validation_result": validation_payload,
    }
    evidence_files = _write_gate_evidence(evidence_dir, label, safety, details) if write_evidence else {}
    return {
        "ok": label in CONTROLLED_LABELS and all(checks.values()),
        "result_label": label,
        "issue": issue,
        "allow_run": allow_run,
        "confirm_run_text_supplied": bool(confirm_run_text),
        "confirm_run_text_matched": confirm_run_text == REQUIRED_CONFIRMATION,
        "used_sample_staged_script": used_sample,
        "selected_staged_script_path": None if selected_script_path is None else str(selected_script_path),
        "authorization_path": None if authorization_path is None else str(authorization_path),
        "authorization_state": details["authorization_state"],
        "validation_result": validation_payload,
        "checks": checks,
        "safety": safety.to_dict(),
        "evidence_files": evidence_files,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.script_run_gate")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--staged-script-path", default=None)
    parser.add_argument("--allow-run", action="store_true")
    parser.add_argument("--confirm-run-text", default="")
    parser.add_argument("--no-sample-when-missing", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_script_explicit_run_gate(
        repo_root=args.repo_root,
        evidence_root=args.evidence_root,
        staged_script_path=args.staged_script_path,
        allow_run=args.allow_run,
        confirm_run_text=args.confirm_run_text,
        allow_sample_when_missing=not args.no_sample_when_missing,
        write_evidence=not args.no_write_evidence,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())