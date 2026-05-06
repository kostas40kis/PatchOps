from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from patchops.copilot_downloader.copied_script_static_validator import PASS_SCRIPT_VALIDATED_RUN_BLOCKED, validate_copied_script_static_file
from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import DownloaderEvidenceRecord, DownloaderSafetyFlags
from patchops.copilot_downloader.script_payload_contract import sha256_text
from patchops.copilot_downloader.script_run_gate import write_sample_staged_script

PATCH_NAME = "d2_05_downloader_copied_script_bounded_runner"
PASS_PATCHOPS_RUN_COMPLETED = "PASS_PATCHOPS_RUN_COMPLETED"
FAIL_PATCHOPS_RUN = "FAIL_PATCHOPS_RUN"
BLOCKED_RUN_NOT_AUTHORIZED = "BLOCKED_RUN_NOT_AUTHORIZED"
CONTROLLED_LABELS: frozenset[str] = frozenset({PASS_PATCHOPS_RUN_COMPLETED, FAIL_PATCHOPS_RUN, BLOCKED_RUN_NOT_AUTHORIZED})
DEFAULT_TIMEOUT_SECONDS = 60


def _repo_child(root: Path, *parts: str) -> Path:
    candidate = root.joinpath(*parts).resolve(strict=False)
    root_resolved = root.resolve(strict=False)
    candidate.relative_to(root_resolved)
    return candidate


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _powershell_exe() -> str:
    if os.name == "nt":
        return "powershell.exe"
    return "pwsh"


def _write_desktop_report(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "PATCHOPS DOWNLOADER COPIED SCRIPT BOUNDED RUN REPORT",
        "====================================================",
        f"generated_utc: {datetime.now(timezone.utc).isoformat()}",
        f"patch_name: {PATCH_NAME}",
        f"result_label: {payload.get('result_label')}",
        f"ok: {str(payload.get('ok')).lower()}",
        f"script_path: {payload.get('script_path')}",
        f"script_sha256: {payload.get('script_sha256')}",
        f"exit_code: {(payload.get('run_result') or {}).get('exit_code')}",
        f"timed_out: {(payload.get('run_result') or {}).get('timed_out')}",
        "checks:",
    ]
    for key, value in sorted((payload.get("checks") or {}).items()):
        lines.append(f"  {key}: {value}")
    lines.append("safety:")
    for key, value in sorted((payload.get("safety") or {}).items()):
        lines.append(f"  {key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def validate_run_authorization(script_path: str | Path, authorization_path: str | Path | None = None) -> tuple[bool, tuple[str, ...], dict[str, Any] | None, Path | None]:
    path = Path(script_path).resolve(strict=False)
    auth_path = Path(authorization_path).resolve(strict=False) if authorization_path is not None else (path.parent / "run_authorization.json").resolve(strict=False)
    issues: list[str] = []
    if not path.is_file():
        issues.append("staged script is missing")
    if not auth_path.is_file():
        issues.append("run authorization metadata is missing")
        return False, tuple(issues), None, auth_path
    try:
        authorization = _read_json(auth_path)
    except Exception as exc:
        issues.append(f"run authorization metadata is unreadable: {exc}")
        return False, tuple(issues), None, auth_path
    if authorization.get("authorized") is not True:
        issues.append("run authorization authorized=true is required")
    if authorization.get("run_performed") is True:
        issues.append("run authorization was already consumed")
    if authorization.get("validation_result_label") != PASS_SCRIPT_VALIDATED_RUN_BLOCKED:
        issues.append("static validation PASS label is required")
    if authorization.get("confirm_run_text_matched") is not True:
        issues.append("confirm run text match is required")
    if authorization.get("allow_run_supplied") is not True:
        issues.append("allow-run flag is required")
    script_sha256 = None
    if path.is_file():
        script_sha256 = sha256_text(path.read_text(encoding="utf-8"))
        if authorization.get("script_sha256") != script_sha256:
            issues.append("authorized script sha256 does not match staged script")
    authorized_path = authorization.get("script_path")
    if authorized_path and Path(str(authorized_path)).resolve(strict=False) != path:
        issues.append("authorized script path does not match requested script path")
    return not issues, tuple(issues), authorization, auth_path


def run_powershell_script_bounded(script_path: str | Path, *, timeout_seconds: int, working_directory: str | Path) -> dict[str, Any]:
    path = Path(script_path).resolve(strict=False)
    cwd = Path(working_directory).resolve(strict=False)
    command = [_powershell_exe(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(path)]
    started = time.time()
    timed_out = False
    try:
        process = subprocess.Popen(
            command,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
            exit_code = int(process.returncode)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                process.kill()
            except Exception:
                pass
            stdout, stderr = process.communicate()
            exit_code = 124
    except FileNotFoundError as exc:
        stdout = ""
        stderr = str(exc)
        exit_code = 127
    elapsed = time.time() - started
    return {
        "command": " ".join(command),
        "working_directory": str(cwd),
        "exit_code": exit_code,
        "timed_out": timed_out,
        "elapsed_seconds": round(elapsed, 3),
        "stdout": stdout,
        "stderr": stderr,
        "stdout_sha256": sha256_text(stdout),
        "stderr_sha256": sha256_text(stderr),
        "stdout_size_chars": len(stdout),
        "stderr_size_chars": len(stderr),
    }


def _write_runner_evidence(evidence_dir: Path, label: str, safety: DownloaderSafetyFlags, details: dict[str, Any]) -> dict[str, str]:
    evidence = DownloaderEvidenceRecord(
        patch_name=PATCH_NAME,
        result_label=label,
        safety=safety,
        details=details,
    )
    return write_evidence_pair(evidence_dir, "copied_script_bounded_runner", evidence)


def _blocked_payload(
    *,
    issue: str,
    issues: Sequence[str],
    script_path: Path | None,
    authorization_path: Path | None,
    safety: DownloaderSafetyFlags,
    evidence_files: dict[str, str] | None = None,
    desktop_report_path: str | None = None,
) -> dict[str, Any]:
    checks = {
        "authorization_required": True,
        "run_not_started_without_authorization": True,
        "timeout_configured": True,
        "stdout_stderr_exit_capture_configured": True,
        "clipboard_not_read": not safety.clipboard_read,
        "clipboard_not_written": not safety.clipboard_written,
        "browser_not_used": not safety.browser_used,
        "conversation_text_not_logged": not safety.conversation_text_logged,
        "uploader_not_imported": True,
    }
    return {
        "ok": all(checks.values()),
        "result_label": BLOCKED_RUN_NOT_AUTHORIZED,
        "issue": issue,
        "issues": list(issues),
        "script_path": None if script_path is None else str(script_path),
        "script_sha256": None,
        "authorization_path": None if authorization_path is None else str(authorization_path),
        "run_result": None,
        "checks": checks,
        "safety": safety.to_dict(),
        "evidence_files": evidence_files or {},
        "desktop_report_path": desktop_report_path,
    }


def run_copied_script_bounded_runner(
    *,
    repo_root: str | Path | None = None,
    evidence_root: str | Path | None = None,
    desktop_report_dir: str | Path | None = None,
    staged_script_path: str | Path | None = None,
    authorization_path: str | Path | None = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    allow_execute: bool = False,
    write_evidence: bool = True,
    write_desktop_report: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else _repo_child(root, "data", "runtime", "copilot_downloader", "d2_05_copied_script_bounded_runner")
    report_dir = Path(desktop_report_dir).resolve(strict=False) if desktop_report_dir is not None else evidence_dir
    safety = DownloaderSafetyFlags()

    selected_script = Path(staged_script_path).resolve(strict=False) if staged_script_path is not None else None
    if selected_script is None:
        blocked = _blocked_payload(issue="staged_script_path_required", issues=("staged script path is required for bounded runner",), script_path=None, authorization_path=None, safety=safety)
        if write_evidence:
            blocked["evidence_files"] = _write_runner_evidence(evidence_dir, BLOCKED_RUN_NOT_AUTHORIZED, safety, {"checks": blocked["checks"], "issue": blocked["issue"], "issues": blocked["issues"]})
        if write_desktop_report:
            report_path = report_dir / f"patchops_downloader_copied_script_bounded_runner_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            blocked["desktop_report_path"] = str(_write_desktop_report(report_path, blocked))
        return blocked

    authorized, auth_issues, authorization, resolved_auth_path = validate_run_authorization(selected_script, authorization_path)
    static_validation = validate_copied_script_static_file(selected_script)
    if not authorized or static_validation.result_label != PASS_SCRIPT_VALIDATED_RUN_BLOCKED or not allow_execute:
        issues = list(auth_issues)
        issue = "run_authorization_required"
        if static_validation.result_label != PASS_SCRIPT_VALIDATED_RUN_BLOCKED:
            issue = "staged_script_static_validation_failed"
            issues.extend(static_validation.issues)
        elif not allow_execute:
            issue = "allow_execute_required"
            issues.append("bounded runner requires allow_execute=True in addition to run authorization metadata")
        blocked = _blocked_payload(issue=issue, issues=issues, script_path=selected_script, authorization_path=resolved_auth_path, safety=safety)
        blocked["validation_result"] = static_validation.to_dict()
        if write_evidence:
            blocked["evidence_files"] = _write_runner_evidence(evidence_dir, BLOCKED_RUN_NOT_AUTHORIZED, safety, {"checks": blocked["checks"], "issue": blocked["issue"], "issues": blocked["issues"], "validation_result": static_validation.to_dict()})
        if write_desktop_report:
            report_path = report_dir / f"patchops_downloader_copied_script_bounded_runner_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            blocked["desktop_report_path"] = str(_write_desktop_report(report_path, blocked))
        return blocked

    run_result = run_powershell_script_bounded(selected_script, timeout_seconds=timeout_seconds, working_directory=root)
    safety = DownloaderSafetyFlags(artifact_executed=True, patchops_invoked=True)
    label = PASS_PATCHOPS_RUN_COMPLETED if run_result["exit_code"] == 0 and not run_result["timed_out"] else FAIL_PATCHOPS_RUN
    script_text = selected_script.read_text(encoding="utf-8")
    script_sha256 = sha256_text(script_text)
    checks = {
        "authorization_required": True,
        "authorization_validated": True,
        "static_validation_required": True,
        "static_validation_passed": True,
        "allow_execute_required": allow_execute,
        "bounded_execution_used": timeout_seconds > 0,
        "timeout_seconds_recorded": True,
        "stdout_captured": run_result["stdout"] is not None,
        "stderr_captured": run_result["stderr"] is not None,
        "exit_code_captured": isinstance(run_result["exit_code"], int),
        "script_sha256_verified": authorization is not None and authorization.get("script_sha256") == script_sha256,
        "desktop_report_requested": write_desktop_report,
        "clipboard_not_read": not safety.clipboard_read,
        "clipboard_not_written": not safety.clipboard_written,
        "browser_not_used": not safety.browser_used,
        "conversation_text_not_logged": not safety.conversation_text_logged,
        "uploader_not_imported": True,
    }
    details = {
        "checks": checks,
        "authorization_path": None if resolved_auth_path is None else str(resolved_auth_path),
        "script_path": str(selected_script),
        "script_sha256": script_sha256,
        "validation_result": static_validation.to_dict(),
        "timeout_seconds": timeout_seconds,
        "run_result": run_result,
    }
    evidence_files = _write_runner_evidence(evidence_dir, label, safety, details) if write_evidence else {}
    payload = {
        "ok": label == PASS_PATCHOPS_RUN_COMPLETED and all(checks.values()),
        "result_label": label,
        "issue": None if label == PASS_PATCHOPS_RUN_COMPLETED else "bounded_run_failed",
        "issues": [],
        "script_path": str(selected_script),
        "script_sha256": script_sha256,
        "authorization_path": None if resolved_auth_path is None else str(resolved_auth_path),
        "validation_result": static_validation.to_dict(),
        "run_result": run_result,
        "checks": checks,
        "safety": safety.to_dict(),
        "evidence_files": evidence_files,
        "desktop_report_path": None,
    }
    if write_desktop_report:
        report_path = report_dir / f"patchops_downloader_copied_script_bounded_runner_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        payload["desktop_report_path"] = str(_write_desktop_report(report_path, payload))
    if resolved_auth_path is not None and resolved_auth_path.is_file():
        updated_auth = _read_json(resolved_auth_path)
        updated_auth["run_performed"] = True
        updated_auth["run_completed_utc"] = datetime.now(timezone.utc).isoformat()
        updated_auth["run_result_label"] = label
        updated_auth["run_exit_code"] = run_result["exit_code"]
        updated_auth["run_timed_out"] = run_result["timed_out"]
        _write_json(resolved_auth_path, updated_auth)
    return payload


def write_authorized_test_script(repo_root: str | Path, *, exit_code: int = 0, sleep_seconds: float = 0.0) -> tuple[Path, Path]:
    root = Path(repo_root).resolve(strict=False)
    script_path = write_sample_staged_script(root)
    sleep_line = f"    Start-Sleep -Seconds {sleep_seconds}\n" if sleep_seconds > 0 else ""
    script_text = (
        "& {\n"
        "    Set-StrictMode -Version Latest\n"
        "    $ErrorActionPreference = \"Stop\"\n"
        "    # test-only PatchOps CLI marker for static validation; not executed in temp repos:\n"
        "    # .\\.venv\\Scripts\\python.exe -m patchops.cli check data/runtime/direct_patches/example/manifest.json\n"
        "    Write-Host \"PatchOps bounded runner test harness\"\n"
        f"{sleep_line}"
        f"    exit {exit_code}\n"
        "}\n"
    )
    script_path.write_text(script_text, encoding="utf-8")
    script_sha256 = sha256_text(script_text)
    auth_path = script_path.parent / "run_authorization.json"
    auth_payload = {
        "schema_version": 1,
        "producer": "patchops.copilot_downloader",
        "patch_name": PATCH_NAME,
        "authorized_utc": datetime.now(timezone.utc).isoformat(),
        "authorized": True,
        "requires_confirmation": "PATCHOPS_CONFIRM_RUN",
        "confirm_run_text_matched": True,
        "allow_run_supplied": True,
        "script_path": str(script_path),
        "script_sha256": script_sha256,
        "validation_result_label": PASS_SCRIPT_VALIDATED_RUN_BLOCKED,
        "run_performed": False,
        "patchops_invoked": False,
        "bounded_runner_required_next": True,
        "test_harness_script": True,
    }
    _write_json(auth_path, auth_payload)
    return script_path, auth_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.copied_script_bounded_runner")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--desktop-report-dir", default=None)
    parser.add_argument("--staged-script-path", default=None)
    parser.add_argument("--authorization-path", default=None)
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--allow-execute", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    parser.add_argument("--no-desktop-report", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_copied_script_bounded_runner(
        repo_root=args.repo_root,
        evidence_root=args.evidence_root,
        desktop_report_dir=args.desktop_report_dir,
        staged_script_path=args.staged_script_path,
        authorization_path=args.authorization_path,
        timeout_seconds=args.timeout_seconds,
        allow_execute=args.allow_execute,
        write_evidence=not args.no_write_evidence,
        write_desktop_report=not args.no_desktop_report,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else (0 if payload.get("result_label") == BLOCKED_RUN_NOT_AUTHORIZED else 1)


if __name__ == "__main__":
    raise SystemExit(main())