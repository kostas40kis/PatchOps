from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from patchops.copilot_downloader.canonical_report_locator import parse_patchops_report_signals
from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import DownloaderEvidenceRecord, DownloaderSafetyFlags

PATCH_NAME = "d5_01_downloader_report_handoff_contract"
PASS_HANDOFF_WRITTEN = "PASS_HANDOFF_WRITTEN"
FAIL_HANDOFF_WRITE = "FAIL_HANDOFF_WRITE"
CONTROLLED_LABELS: frozenset[str] = frozenset({PASS_HANDOFF_WRITTEN, FAIL_HANDOFF_WRITE})
DEFAULT_HANDOFF_DIR = "data/runtime/copilot_handoff"
DEFAULT_HANDOFF_JSON = "latest_report_handoff.json"
DEFAULT_HANDOFF_TEXT = "latest_report_handoff.txt"
UPLOADER_IMPORT_NAMES: tuple[str, ...] = ("patchops.chatgpt_uploader", "patchops.copilot_uploader", "chatgpt_uploader")


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


def _read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str | Path, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def default_safety(*, canonical_report_found: bool = False, patchops_invoked: bool = False) -> dict[str, bool]:
    return DownloaderSafetyFlags(canonical_report_found=canonical_report_found, patchops_invoked=patchops_invoked).to_dict()


def uploader_modules_imported() -> dict[str, Any]:
    found: dict[str, bool] = {}
    for name in UPLOADER_IMPORT_NAMES:
        found[name] = importlib.util.find_spec(name) is not None
    # This detects availability only; the downloader deliberately never imports/calls uploader code here.
    return {
        "uploader_module_specs_visible": found,
        "uploader_import_performed": False,
        "uploader_called": False,
    }


def summarize_report(report_path: str | Path | None, expected_sha256: str | None = None) -> dict[str, Any]:
    if report_path is None or not str(report_path).strip():
        return {
            "canonical_report_path": None,
            "canonical_report_exists": False,
            "canonical_report_sha256": None,
            "canonical_report_sha256_matches": False,
            "canonical_report_size_bytes": None,
            "signals": None,
        }
    path = Path(report_path).resolve(strict=False)
    if not path.is_file():
        return {
            "canonical_report_path": str(path),
            "canonical_report_exists": False,
            "canonical_report_sha256": None,
            "canonical_report_sha256_matches": False,
            "canonical_report_size_bytes": None,
            "signals": None,
        }
    text = path.read_text(encoding="utf-8", errors="replace")
    actual_sha = sha256_file(path)
    return {
        "canonical_report_path": str(path),
        "canonical_report_exists": True,
        "canonical_report_sha256": actual_sha,
        "canonical_report_sha256_matches": expected_sha256 is None or expected_sha256 == actual_sha,
        "canonical_report_size_bytes": path.stat().st_size,
        "signals": parse_patchops_report_signals(text),
    }


def load_session_report(session_report_path: str | Path | None) -> dict[str, Any] | None:
    if session_report_path is None or not str(session_report_path).strip():
        return None
    path = Path(session_report_path).resolve(strict=False)
    if not path.is_file():
        return None
    payload = _read_json(path)
    payload["session_report_path"] = str(path)
    return payload


def extract_handoff_source(
    *,
    session_report: dict[str, Any] | None = None,
    canonical_report_path: str | Path | None = None,
    canonical_report_sha256: str | None = None,
    final_result: str | None = None,
    exit_code: int | None = None,
    safety: dict[str, bool] | None = None,
    artifact_kind: str | None = None,
    artifact_sha256: str | None = None,
) -> dict[str, Any]:
    session = session_report or {}
    canonical = session.get("canonical_report") if isinstance(session.get("canonical_report"), dict) else {}
    artifact = session.get("artifact") if isinstance(session.get("artifact"), dict) else {}
    final = session.get("final") if isinstance(session.get("final"), dict) else {}
    source_safety = session.get("safety") if isinstance(session.get("safety"), dict) else {}
    resolved_report_path = canonical_report_path or canonical.get("canonical_report_path")
    resolved_report_sha = canonical_report_sha256 or canonical.get("canonical_report_sha256")
    resolved_final = final_result or final.get("final_result") or session.get("final_result")
    resolved_exit = exit_code if exit_code is not None else final.get("final_exit_code")
    if resolved_exit is None:
        resolved_exit = canonical.get("signals", {}).get("exit_code") if isinstance(canonical.get("signals"), dict) else None
    resolved_artifact_sha = artifact_sha256 or artifact.get("sha256")
    resolved_artifact_kind = artifact_kind or artifact.get("kind") or artifact.get("artifact_kind") or "unknown"
    resolved_safety = dict(default_safety())
    resolved_safety.update(source_safety)
    resolved_safety.update(safety or {})
    return {
        "session_report_path": session.get("session_report_path"),
        "canonical_report_path": None if resolved_report_path is None else str(resolved_report_path),
        "canonical_report_sha256_expected": resolved_report_sha,
        "final_result": resolved_final,
        "exit_code": resolved_exit,
        "artifact_kind": resolved_artifact_kind,
        "artifact_sha256": resolved_artifact_sha,
        "safety": resolved_safety,
    }


def evaluate_uploader_ready(source: dict[str, Any], report_summary: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    signals = report_summary.get("signals") or {}
    report_exists = bool(report_summary.get("canonical_report_exists"))
    report_sha_matches = bool(report_summary.get("canonical_report_sha256_matches"))
    report_result = signals.get("result_text")
    report_exit_code = signals.get("exit_code")
    final_result = source.get("final_result")
    exit_code = source.get("exit_code")
    if not report_exists:
        issues.append("canonical report is missing")
    if not report_sha_matches:
        issues.append("canonical report sha256 does not match expected value")
    if report_result != "PASS":
        issues.append("canonical report Result must be PASS")
    if report_exit_code != 0:
        issues.append("canonical report ExitCode must be 0")
    if final_result != "PASS":
        issues.append("downloader final result must be PASS")
    if exit_code not in (0, None):
        issues.append("downloader exit code must be 0 or omitted when canonical report is PASS")
    safety = source.get("safety") or {}
    if safety.get("webdriver_used") is True:
        issues.append("webdriver_used must be false")
    if safety.get("selenium_used") is True:
        issues.append("selenium_used must be false")
    if safety.get("browser_dom_automation_used") is True:
        issues.append("browser_dom_automation_used must be false")
    if safety.get("cloudflare_bypass_attempted") is True:
        issues.append("cloudflare_bypass_attempted must be false")
    if safety.get("captcha_bypass_attempted") is True:
        issues.append("captcha_bypass_attempted must be false")
    if safety.get("file_upload_attempted") is True:
        issues.append("file_upload_attempted must be false for downloader handoff")
    if safety.get("chatgpt_submit_performed") is True:
        issues.append("chatgpt_submit_performed must be false for downloader handoff")
    return {
        "uploader_ready": not issues,
        "issues": issues,
        "report_result": report_result,
        "report_exit_code": report_exit_code,
    }


def build_handoff_payload(
    *,
    repo_root: str | Path | None = None,
    session_report_path: str | Path | None = None,
    canonical_report_path: str | Path | None = None,
    canonical_report_sha256: str | None = None,
    final_result: str | None = None,
    exit_code: int | None = None,
    safety: dict[str, bool] | None = None,
    artifact_kind: str | None = None,
    artifact_sha256: str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    session = load_session_report(session_report_path)
    source = extract_handoff_source(
        session_report=session,
        canonical_report_path=canonical_report_path,
        canonical_report_sha256=canonical_report_sha256,
        final_result=final_result,
        exit_code=exit_code,
        safety=safety,
        artifact_kind=artifact_kind,
        artifact_sha256=artifact_sha256,
    )
    report = summarize_report(source.get("canonical_report_path"), source.get("canonical_report_sha256_expected"))
    readiness = evaluate_uploader_ready(source, report)
    uploader_import = uploader_modules_imported()
    status = PASS_HANDOFF_WRITTEN if readiness["uploader_ready"] else FAIL_HANDOFF_WRITE
    safety_payload = dict(default_safety(canonical_report_found=bool(report.get("canonical_report_exists"))))
    safety_payload.update(source.get("safety") or {})
    safety_payload["canonical_report_found"] = bool(report.get("canonical_report_exists"))
    return {
        "schema_version": 1,
        "producer": "patchops.copilot_downloader",
        "patch_name": PATCH_NAME,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "status": status,
        "result_label": status,
        "uploader_ready": readiness["uploader_ready"],
        "handoff_contract": "file_only_no_uploader_import",
        "session_report_path": source.get("session_report_path"),
        "artifact_kind": source.get("artifact_kind"),
        "artifact_sha256": source.get("artifact_sha256"),
        "canonical_report_path": report.get("canonical_report_path"),
        "canonical_report_sha256": report.get("canonical_report_sha256"),
        "canonical_report_sha256_matches": report.get("canonical_report_sha256_matches"),
        "canonical_report_exists": report.get("canonical_report_exists"),
        "canonical_report_size_bytes": report.get("canonical_report_size_bytes"),
        "result": readiness.get("report_result") or source.get("final_result"),
        "exit_code": readiness.get("report_exit_code") if readiness.get("report_exit_code") is not None else source.get("exit_code"),
        "safety": safety_payload,
        "issues": readiness["issues"],
        "uploader_import": uploader_import,
    }


def _write_handoff_text(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "PATCHOPS DOWNLOADER REPORT HANDOFF",
        "==================================",
        f"generated_utc: {payload.get('generated_utc')}",
        f"producer: {payload.get('producer')}",
        f"status: {payload.get('status')}",
        f"uploader_ready: {payload.get('uploader_ready')}",
        f"canonical_report_path: {payload.get('canonical_report_path')}",
        f"canonical_report_sha256: {payload.get('canonical_report_sha256')}",
        f"result: {payload.get('result')}",
        f"exit_code: {payload.get('exit_code')}",
        f"artifact_kind: {payload.get('artifact_kind')}",
        f"artifact_sha256: {payload.get('artifact_sha256')}",
        "",
        "issues:",
    ]
    if payload.get("issues"):
        lines.extend([f"- {issue}" for issue in payload["issues"]])
    else:
        lines.append("(none)")
    lines.extend(["", "safety:"])
    for key, value in sorted((payload.get("safety") or {}).items()):
        lines.append(f"{key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_latest_report_handoff(
    *,
    repo_root: str | Path | None = None,
    handoff_dir: str | Path | None = None,
    session_report_path: str | Path | None = None,
    canonical_report_path: str | Path | None = None,
    canonical_report_sha256: str | None = None,
    final_result: str | None = None,
    exit_code: int | None = None,
    safety: dict[str, bool] | None = None,
    artifact_kind: str | None = None,
    artifact_sha256: str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    out_dir = Path(handoff_dir).resolve(strict=False) if handoff_dir is not None else _repo_child(root, *DEFAULT_HANDOFF_DIR.split("/"))
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / DEFAULT_HANDOFF_JSON
    text_path = out_dir / DEFAULT_HANDOFF_TEXT
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_json_path = out_dir / f"report_handoff_{timestamp}.json"
    archive_text_path = out_dir / f"report_handoff_{timestamp}.txt"
    payload = build_handoff_payload(
        repo_root=root,
        session_report_path=session_report_path,
        canonical_report_path=canonical_report_path,
        canonical_report_sha256=canonical_report_sha256,
        final_result=final_result,
        exit_code=exit_code,
        safety=safety,
        artifact_kind=artifact_kind,
        artifact_sha256=artifact_sha256,
    )
    payload["handoff_paths"] = {
        "json": str(json_path),
        "text": str(text_path),
        "archive_json": str(archive_json_path),
        "archive_text": str(archive_text_path),
    }
    _write_json(json_path, payload)
    _write_json(archive_json_path, payload)
    _write_handoff_text(text_path, payload)
    _write_handoff_text(archive_text_path, payload)
    return payload


def _write_handoff_evidence(evidence_dir: Path, label: str, safety: DownloaderSafetyFlags, details: dict[str, Any]) -> dict[str, str]:
    evidence = DownloaderEvidenceRecord(
        patch_name=PATCH_NAME,
        result_label=label,
        safety=safety,
        details=details,
    )
    return write_evidence_pair(evidence_dir, "report_handoff_contract", evidence)


def run_report_handoff_contract(
    *,
    repo_root: str | Path | None = None,
    handoff_dir: str | Path | None = None,
    evidence_root: str | Path | None = None,
    session_report_path: str | Path | None = None,
    canonical_report_path: str | Path | None = None,
    canonical_report_sha256: str | None = None,
    final_result: str | None = None,
    exit_code: int | None = None,
    safety: dict[str, bool] | None = None,
    artifact_kind: str | None = None,
    artifact_sha256: str | None = None,
    write_evidence: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else _repo_child(root, "data", "runtime", "copilot_downloader", "d5_01_report_handoff_contract")
    payload = write_latest_report_handoff(
        repo_root=root,
        handoff_dir=handoff_dir,
        session_report_path=session_report_path,
        canonical_report_path=canonical_report_path,
        canonical_report_sha256=canonical_report_sha256,
        final_result=final_result,
        exit_code=exit_code,
        safety=safety,
        artifact_kind=artifact_kind,
        artifact_sha256=artifact_sha256,
    )
    flags = DownloaderSafetyFlags(canonical_report_found=bool(payload.get("canonical_report_exists")))
    checks = {
        "handoff_json_written": Path(payload["handoff_paths"]["json"]).is_file(),
        "handoff_text_written": Path(payload["handoff_paths"]["text"]).is_file(),
        "canonical_report_path_included": "canonical_report_path" in payload,
        "report_sha256_included": "canonical_report_sha256" in payload,
        "final_result_included": "result" in payload,
        "exit_code_included": "exit_code" in payload,
        "safety_flags_included": bool(payload.get("safety")),
        "uploader_ready_true_only_when_valid": (not payload.get("uploader_ready")) or (payload.get("status") == PASS_HANDOFF_WRITTEN and not payload.get("issues") and payload.get("canonical_report_exists") is True and payload.get("canonical_report_sha256_matches") is True and payload.get("result") == "PASS" and payload.get("exit_code") == 0),
        "file_based_contract_only": payload.get("handoff_contract") == "file_only_no_uploader_import",
        "uploader_import_not_performed": payload.get("uploader_import", {}).get("uploader_import_performed") is False,
        "uploader_not_called": payload.get("uploader_import", {}).get("uploader_called") is False,
        "browser_not_started": not flags.browser_used,
        "clipboard_not_read": not flags.clipboard_read,
        "clipboard_not_written": not flags.clipboard_written,
        "artifact_not_executed_by_handoff": not flags.artifact_executed,
        "chatgpt_submit_not_performed": not flags.chatgpt_submit_performed,
        "file_upload_not_attempted": not flags.file_upload_attempted,
    }
    result = {
        "ok": payload.get("status") in CONTROLLED_LABELS and all(checks.values()),
        "result_label": payload.get("status"),
        "uploader_ready": payload.get("uploader_ready"),
        "issues": payload.get("issues", []),
        "handoff_paths": payload.get("handoff_paths"),
        "canonical_report_path": payload.get("canonical_report_path"),
        "canonical_report_sha256": payload.get("canonical_report_sha256"),
        "result": payload.get("result"),
        "exit_code": payload.get("exit_code"),
        "checks": checks,
        "safety": flags.to_dict() | {key: value for key, value in (payload.get("safety") or {}).items() if key not in flags.to_dict()},
        "evidence_files": {},
    }
    if write_evidence:
        result["evidence_files"] = _write_handoff_evidence(evidence_dir, str(payload.get("status")), flags, {"checks": checks, "handoff_paths": payload.get("handoff_paths"), "uploader_ready": payload.get("uploader_ready"), "issues": payload.get("issues", [])})
    return result


def _load_safety_json(raw: str | None) -> dict[str, bool] | None:
    if raw is None or not raw.strip():
        return None
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("--safety-json must decode to a JSON object")
    return {str(key): bool(value) for key, value in payload.items()}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.report_handoff_contract")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--handoff-dir", default=None)
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--session-report-path", default=None)
    parser.add_argument("--canonical-report-path", default=None)
    parser.add_argument("--canonical-report-sha256", default=None)
    parser.add_argument("--final-result", default=None)
    parser.add_argument("--exit-code", type=int, default=None)
    parser.add_argument("--safety-json", default=None)
    parser.add_argument("--artifact-kind", default=None)
    parser.add_argument("--artifact-sha256", default=None)
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_report_handoff_contract(
        repo_root=args.repo_root,
        handoff_dir=args.handoff_dir,
        evidence_root=args.evidence_root,
        session_report_path=args.session_report_path,
        canonical_report_path=args.canonical_report_path,
        canonical_report_sha256=args.canonical_report_sha256,
        final_result=args.final_result,
        exit_code=args.exit_code,
        safety=_load_safety_json(args.safety_json),
        artifact_kind=args.artifact_kind,
        artifact_sha256=args.artifact_sha256,
        write_evidence=not args.no_write_evidence,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())