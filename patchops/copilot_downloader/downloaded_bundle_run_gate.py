from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence

from patchops.copilot_downloader.download_stable_validator import sha256_file
from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import DownloaderEvidenceRecord, DownloaderSafetyFlags
from patchops.copilot_downloader.patchops_bundle_validator import (
    NON_EXECUTING_SURFACES,
    find_latest_staged_downloaded_artifact,
    validate_staged_bundle_shape,
)
from patchops.copilot_downloader.script_payload_contract import REQUIRED_CONFIRMATION

PATCH_NAME = "d3_04_downloader_downloaded_bundle_run_gate"
PASS_PATCHOPS_RUN_COMPLETED = "PASS_PATCHOPS_RUN_COMPLETED"
FAIL_PATCHOPS_RUN = "FAIL_PATCHOPS_RUN"
BLOCKED_RUN_NOT_AUTHORIZED = "BLOCKED_RUN_NOT_AUTHORIZED"
CONTROLLED_LABELS: frozenset[str] = frozenset({PASS_PATCHOPS_RUN_COMPLETED, FAIL_PATCHOPS_RUN, BLOCKED_RUN_NOT_AUTHORIZED})
ALLOWED_RUN_SURFACES: frozenset[str] = frozenset({"apply-bundle", "run-package"})
REQUIRED_BUNDLE_SURFACES: frozenset[str] = frozenset(NON_EXECUTING_SURFACES)
DEFAULT_LEDGER_PATH = "data/runtime/copilot_downloader/ledger/artifact_ledger.jsonl"
DEFAULT_TIMEOUT_SECONDS = 180


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


def _read_ledger_entries(ledger_path: Path) -> list[dict[str, Any]]:
    if not ledger_path.is_file():
        return []
    entries: list[dict[str, Any]] = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            entries.append({"_malformed": True})
    return entries


def ledger_contains_sha(repo_root: str | Path, artifact_sha256: str | None, ledger_path: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root).resolve(strict=False)
    path = Path(ledger_path).resolve(strict=False) if ledger_path is not None else _repo_child(root, *DEFAULT_LEDGER_PATH.split("/"))
    entries = _read_ledger_entries(path)
    match = next((entry for entry in entries if entry.get("artifact_sha256") == artifact_sha256), None)
    return {
        "ledger_path": str(path),
        "ledger_exists": path.is_file(),
        "artifact_sha256": artifact_sha256,
        "sha_found": match is not None,
        "matching_entry": match,
        "entry_count": len(entries),
    }


def load_validated_bundle_metadata(metadata_path: str | Path) -> dict[str, Any]:
    path = Path(metadata_path).resolve(strict=False)
    payload = _read_json(path)
    payload["metadata_path"] = str(path)
    raw = payload.get("raw_artifact_path")
    if raw is not None:
        payload["raw_artifact_path"] = str(Path(str(raw)).resolve(strict=False))
    return payload


def validate_downloaded_bundle_run_gate(
    *,
    repo_root: str | Path,
    staged_metadata_path: str | Path | None,
    ledger_path: str | Path | None = None,
    allow_run: bool = False,
    confirm_run_text: str = "",
    run_surface: str = "apply-bundle",
) -> dict[str, Any]:
    root = Path(repo_root).resolve(strict=False)
    metadata_path = Path(staged_metadata_path).resolve(strict=False) if staged_metadata_path is not None else find_latest_staged_downloaded_artifact(root)
    issues: list[str] = []
    metadata: dict[str, Any] | None = None
    shape: dict[str, Any] | None = None
    ledger: dict[str, Any] | None = None
    raw_artifact_path: Path | None = None
    artifact_sha256: str | None = None

    if metadata_path is None or not metadata_path.is_file():
        issues.append("stable staged bundle metadata is required")
    else:
        metadata = load_validated_bundle_metadata(metadata_path)
        raw_value = metadata.get("raw_artifact_path")
        if not raw_value:
            issues.append("raw staged bundle path is required")
        else:
            raw_artifact_path = Path(str(raw_value)).resolve(strict=False)
            if not raw_artifact_path.is_file():
                issues.append("raw staged bundle is missing")
            else:
                artifact_sha256 = sha256_file(raw_artifact_path)
                if metadata.get("artifact_sha256") != artifact_sha256:
                    issues.append("staged bundle sha256 does not match metadata")
        if metadata.get("bundle_validation_performed") is not True:
            issues.append("bundle shape validation must be performed before run")
        if metadata.get("bundle_validation_ok") is not True:
            issues.append("bundle validation ok=true is required before run")
        surfaces = set(metadata.get("bundle_validation_surfaces") or [])
        if not REQUIRED_BUNDLE_SURFACES.issubset(surfaces):
            issues.append("check-bundle/inspect-bundle/plan-bundle pass evidence is required")
        if metadata.get("run_authorized") is True:
            issues.append("bundle metadata is already marked run_authorized")
        if metadata.get("artifact_executed") is True:
            issues.append("bundle metadata is already marked executed")
        shape = validate_staged_bundle_shape(metadata)
        if not shape.get("ok"):
            issues.append("staged bundle shape validation failed at run gate")
        ledger = ledger_contains_sha(root, artifact_sha256 or metadata.get("artifact_sha256"), ledger_path)
        if not ledger.get("sha_found"):
            issues.append("sha256 ledger entry is required before run")

    if run_surface not in ALLOWED_RUN_SURFACES:
        issues.append(f"unsupported run surface: {run_surface}")
    if not allow_run:
        issues.append("--allow-run is required")
    if confirm_run_text != REQUIRED_CONFIRMATION:
        issues.append("--confirm-run-text PATCHOPS_CONFIRM_RUN is required")

    authorized = not issues
    return {
        "authorized": authorized,
        "issues": issues,
        "metadata_path": None if metadata_path is None else str(metadata_path),
        "metadata": metadata,
        "raw_artifact_path": None if raw_artifact_path is None else str(raw_artifact_path),
        "artifact_sha256": artifact_sha256,
        "shape": shape,
        "ledger": ledger,
        "allow_run": allow_run,
        "confirm_run_text_matched": confirm_run_text == REQUIRED_CONFIRMATION,
        "run_surface": run_surface,
        "required_surfaces": sorted(REQUIRED_BUNDLE_SURFACES),
    }


def build_bundle_run_command(bundle_path: str | Path, *, run_surface: str = "apply-bundle") -> list[str]:
    if run_surface not in ALLOWED_RUN_SURFACES:
        raise ValueError(f"unsupported run surface: {run_surface}")
    return [sys.executable, "-m", "patchops.cli", run_surface, str(Path(bundle_path).resolve(strict=False))]


def _preview_command(command: Sequence[str]) -> str:
    return " ".join([f'"{item}"' if any(ch.isspace() for ch in item) else item for item in command])


def default_command_runner(command: Sequence[str], *, cwd: str | Path, timeout_seconds: int) -> dict[str, Any]:
    started = time.time()
    timed_out = False
    try:
        process = subprocess.Popen(
            list(command),
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
    return {
        "command": _preview_command(command),
        "exit_code": exit_code,
        "timed_out": timed_out,
        "elapsed_seconds": round(time.time() - started, 3),
        "stdout": stdout,
        "stderr": stderr,
        "stdout_size_chars": len(stdout),
        "stderr_size_chars": len(stderr),
    }


def extract_patchops_report_signal(stdout: str = "", stderr: str = "") -> dict[str, Any]:
    text = "\n".join([stdout or "", stderr or ""])
    report_match = re.search(r"(?im)^\s*Report Path\s*:\s*(.+?)\s*$", text)
    exit_match = re.search(r"(?im)^\s*ExitCode\s*:\s*(-?\d+)\s*$", text)
    result_match = re.search(r"(?im)^\s*Result\s*:\s*([A-Z]+)\s*$", text)
    return {
        "report_path": None if report_match is None else report_match.group(1).strip(),
        "exit_code_text": None if exit_match is None else exit_match.group(1).strip(),
        "result_text": None if result_match is None else result_match.group(1).strip(),
        "report_signal_found": report_match is not None,
        "result_signal_found": result_match is not None,
        "exit_code_signal_found": exit_match is not None,
    }


def _write_desktop_report(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    run_result = payload.get("run_result") or {}
    report_signal = payload.get("patchops_report_signal") or {}
    lines = [
        "PATCHOPS DOWNLOADER DOWNLOADED BUNDLE RUN REPORT",
        "=================================================",
        f"generated_utc: {datetime.now(timezone.utc).isoformat()}",
        f"patch_name: {PATCH_NAME}",
        f"result_label: {payload.get('result_label')}",
        f"ok: {str(payload.get('ok')).lower()}",
        f"issue: {payload.get('issue')}",
        f"metadata_path: {payload.get('metadata_path')}",
        f"raw_artifact_path: {payload.get('raw_artifact_path')}",
        f"artifact_sha256: {payload.get('artifact_sha256')}",
        f"run_surface: {payload.get('run_surface')}",
        f"run_exit_code: {run_result.get('exit_code')}",
        f"run_timed_out: {run_result.get('timed_out')}",
        f"patchops_report_path_signal: {report_signal.get('report_path')}",
        "checks:",
    ]
    for key, value in sorted((payload.get("checks") or {}).items()):
        lines.append(f"  {key}: {value}")
    lines.append("safety:")
    for key, value in sorted((payload.get("safety") or {}).items()):
        lines.append(f"  {key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _write_runner_evidence(evidence_dir: Path, label: str, safety: DownloaderSafetyFlags, details: dict[str, Any]) -> dict[str, str]:
    evidence = DownloaderEvidenceRecord(
        patch_name=PATCH_NAME,
        result_label=label,
        safety=safety,
        details=details,
    )
    return write_evidence_pair(evidence_dir, "downloaded_bundle_run_gate", evidence)


def _blocked_payload(
    *,
    issue: str,
    gate: dict[str, Any],
    safety: DownloaderSafetyFlags,
    checks: dict[str, bool],
    evidence_files: dict[str, str] | None = None,
    desktop_report_path: str | None = None,
) -> dict[str, Any]:
    return {
        "ok": all(checks.values()),
        "result_label": BLOCKED_RUN_NOT_AUTHORIZED,
        "issue": issue,
        "issues": gate.get("issues", []),
        "metadata_path": gate.get("metadata_path"),
        "raw_artifact_path": gate.get("raw_artifact_path"),
        "artifact_sha256": gate.get("artifact_sha256"),
        "run_surface": gate.get("run_surface"),
        "gate": gate,
        "run_result": None,
        "patchops_report_signal": None,
        "checks": checks,
        "safety": safety.to_dict(),
        "evidence_files": evidence_files or {},
        "desktop_report_path": desktop_report_path,
    }


def run_downloaded_bundle_gate_and_runner(
    *,
    repo_root: str | Path | None = None,
    evidence_root: str | Path | None = None,
    desktop_report_dir: str | Path | None = None,
    staged_metadata_path: str | Path | None = None,
    ledger_path: str | Path | None = None,
    allow_run: bool = False,
    confirm_run_text: str = "",
    run_surface: str = "apply-bundle",
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    command_runner: Callable[..., dict[str, Any]] | None = None,
    write_evidence: bool = True,
    write_desktop_report: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else _repo_child(root, "data", "runtime", "copilot_downloader", "d3_04_downloaded_bundle_run_gate")
    report_dir = Path(desktop_report_dir).resolve(strict=False) if desktop_report_dir is not None else evidence_dir
    safety = DownloaderSafetyFlags()
    gate = validate_downloaded_bundle_run_gate(
        repo_root=root,
        staged_metadata_path=staged_metadata_path,
        ledger_path=ledger_path,
        allow_run=allow_run,
        confirm_run_text=confirm_run_text,
        run_surface=run_surface,
    )
    blocked_checks = {
        "gate_evaluated": True,
        "run_not_started_without_authorization": not gate["authorized"],
        "stable_staged_bundle_required": True,
        "sha256_ledger_required": True,
        "shape_validation_required": True,
        "bundle_surfaces_required": True,
        "allow_run_and_confirm_required": True,
        "timeout_configured": timeout_seconds > 0,
        "stdout_stderr_exit_capture_configured": True,
        "artifact_not_executed": not safety.artifact_executed,
        "patchops_not_invoked_by_downloader_runtime": not safety.patchops_invoked,
        "browser_not_started": not safety.browser_used,
        "clipboard_not_read": not safety.clipboard_read,
        "clipboard_not_written": not safety.clipboard_written,
        "conversation_text_not_logged": not safety.conversation_text_logged,
        "uploader_not_imported": True,
    }
    if not gate["authorized"]:
        issue = "run_authorization_required"
        if gate.get("issues"):
            issue = str(gate["issues"][0]).replace(" ", "_").replace("-", "_").lower()
        blocked = _blocked_payload(issue=issue, gate=gate, safety=safety, checks=blocked_checks)
        if write_evidence:
            blocked["evidence_files"] = _write_runner_evidence(evidence_dir, BLOCKED_RUN_NOT_AUTHORIZED, safety, {"checks": blocked["checks"], "issue": issue, "gate": gate})
        if write_desktop_report:
            report_path = report_dir / f"patchops_downloader_downloaded_bundle_run_gate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            blocked["desktop_report_path"] = str(_write_desktop_report(report_path, blocked))
        return blocked

    runner = command_runner or default_command_runner
    command = build_bundle_run_command(str(gate["raw_artifact_path"]), run_surface=run_surface)
    run_result = runner(command, cwd=root, timeout_seconds=timeout_seconds)
    safety = DownloaderSafetyFlags(artifact_executed=True, patchops_invoked=True)
    report_signal = extract_patchops_report_signal(run_result.get("stdout", ""), run_result.get("stderr", ""))
    label = PASS_PATCHOPS_RUN_COMPLETED if run_result.get("exit_code") == 0 and not run_result.get("timed_out") else FAIL_PATCHOPS_RUN
    checks = {
        "gate_evaluated": True,
        "authorization_validated": True,
        "stable_staged_bundle_required": gate.get("metadata_path") is not None,
        "sha256_ledger_required": bool((gate.get("ledger") or {}).get("sha_found")),
        "shape_validation_required": bool((gate.get("shape") or {}).get("ok")),
        "bundle_surfaces_required": REQUIRED_BUNDLE_SURFACES.issubset(set(((gate.get("metadata") or {}).get("bundle_validation_surfaces") or []))),
        "allow_run_and_confirm_required": allow_run and confirm_run_text == REQUIRED_CONFIRMATION,
        "bounded_execution_used": timeout_seconds > 0,
        "stdout_captured": run_result.get("stdout") is not None,
        "stderr_captured": run_result.get("stderr") is not None,
        "exit_code_captured": isinstance(run_result.get("exit_code"), int),
        "run_surface_allowed": run_surface in ALLOWED_RUN_SURFACES,
        "report_signal_captured_or_deferred_to_d4": True,
        "browser_not_started": not safety.browser_used,
        "clipboard_not_read": not safety.clipboard_read,
        "clipboard_not_written": not safety.clipboard_written,
        "conversation_text_not_logged": not safety.conversation_text_logged,
        "uploader_not_imported": True,
    }
    payload = {
        "ok": label == PASS_PATCHOPS_RUN_COMPLETED and all(checks.values()),
        "result_label": label,
        "issue": None if label == PASS_PATCHOPS_RUN_COMPLETED else "patchops_bundle_run_failed",
        "issues": [],
        "metadata_path": gate.get("metadata_path"),
        "raw_artifact_path": gate.get("raw_artifact_path"),
        "artifact_sha256": gate.get("artifact_sha256"),
        "run_surface": run_surface,
        "gate": gate,
        "run_result": run_result,
        "patchops_report_signal": report_signal,
        "checks": checks,
        "safety": safety.to_dict(),
        "evidence_files": {},
        "desktop_report_path": None,
    }
    details = {
        "checks": checks,
        "gate": gate,
        "run_result": run_result,
        "patchops_report_signal": report_signal,
        "timeout_seconds": timeout_seconds,
    }
    if write_evidence:
        payload["evidence_files"] = _write_runner_evidence(evidence_dir, label, safety, details)
    if write_desktop_report:
        report_path = report_dir / f"patchops_downloader_downloaded_bundle_run_gate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        payload["desktop_report_path"] = str(_write_desktop_report(report_path, payload))
    metadata_path = Path(str(gate["metadata_path"]))
    if metadata_path.is_file():
        metadata = _read_json(metadata_path)
        metadata["run_authorized"] = True
        metadata["artifact_executed"] = True
        metadata["bundle_run_surface"] = run_surface
        metadata["bundle_run_result_label"] = label
        metadata["bundle_run_exit_code"] = run_result.get("exit_code")
        metadata["bundle_run_timed_out"] = run_result.get("timed_out")
        metadata["bundle_run_completed_utc"] = datetime.now(timezone.utc).isoformat()
        metadata["bundle_run_report_signal"] = report_signal
        _write_json(metadata_path, metadata)
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.downloaded_bundle_run_gate")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--desktop-report-dir", default=None)
    parser.add_argument("--staged-metadata-path", default=None)
    parser.add_argument("--ledger-path", default=None)
    parser.add_argument("--allow-run", action="store_true")
    parser.add_argument("--confirm-run-text", default="")
    parser.add_argument("--run-surface", choices=sorted(ALLOWED_RUN_SURFACES), default="apply-bundle")
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--no-write-evidence", action="store_true")
    parser.add_argument("--no-desktop-report", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_downloaded_bundle_gate_and_runner(
        repo_root=args.repo_root,
        evidence_root=args.evidence_root,
        desktop_report_dir=args.desktop_report_dir,
        staged_metadata_path=args.staged_metadata_path,
        ledger_path=args.ledger_path,
        allow_run=args.allow_run,
        confirm_run_text=args.confirm_run_text,
        run_surface=args.run_surface,
        timeout_seconds=args.timeout_seconds,
        write_evidence=not args.no_write_evidence,
        write_desktop_report=not args.no_desktop_report,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else (0 if payload.get("result_label") == BLOCKED_RUN_NOT_AUTHORIZED else 1)


if __name__ == "__main__":
    raise SystemExit(main())