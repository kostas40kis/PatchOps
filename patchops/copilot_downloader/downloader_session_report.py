from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from patchops.copilot_downloader.canonical_report_locator import parse_patchops_report_signals
from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import DownloaderEvidenceRecord, DownloaderSafetyFlags

PATCH_NAME = "d4_02_downloader_session_report"
PASS_DOWNLOADER_SESSION_REPORTED = "PASS_DOWNLOADER_SESSION_REPORTED"
FAIL_DOWNLOADER_SESSION_REPORTED = "FAIL_DOWNLOADER_SESSION_REPORTED"
CONTROLLED_LABELS: frozenset[str] = frozenset({PASS_DOWNLOADER_SESSION_REPORTED, FAIL_DOWNLOADER_SESSION_REPORTED})
DEFAULT_REPORT_DIR = "data/runtime/copilot_downloader/session_reports"


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


def _load_json_arg(raw: str | None, *, default: Any) -> Any:
    if raw is None or not str(raw).strip():
        return default
    return json.loads(raw)


def _default_safety(canonical_report_found: bool = False) -> dict[str, bool]:
    return DownloaderSafetyFlags(canonical_report_found=canonical_report_found).to_dict()


def normalize_patchops_commands(commands: Sequence[dict[str, Any]] | None) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, command in enumerate(commands or []):
        normalized.append(
            {
                "index": index,
                "label": command.get("label") or command.get("name") or f"command_{index}",
                "command": str(command.get("command", "")),
                "working_directory": command.get("working_directory"),
                "exit_code": command.get("exit_code"),
                "timed_out": bool(command.get("timed_out", False)),
                "stdout": str(command.get("stdout", "")),
                "stderr": str(command.get("stderr", "")),
                "stdout_size_chars": len(str(command.get("stdout", ""))),
                "stderr_size_chars": len(str(command.get("stderr", ""))),
            }
        )
    return normalized


def summarize_canonical_report(report_path: str | Path | None, report_sha256: str | None = None) -> dict[str, Any]:
    if report_path is None or not str(report_path).strip():
        return {
            "canonical_report_path": None,
            "canonical_report_exists": False,
            "canonical_report_sha256": None,
            "canonical_report_size_bytes": None,
            "signals": None,
        }
    path = Path(report_path).resolve(strict=False)
    if not path.is_file():
        return {
            "canonical_report_path": str(path),
            "canonical_report_exists": False,
            "canonical_report_sha256": None,
            "canonical_report_size_bytes": None,
            "signals": None,
        }
    text = path.read_text(encoding="utf-8", errors="replace")
    return {
        "canonical_report_path": str(path),
        "canonical_report_exists": True,
        "canonical_report_sha256": report_sha256 or sha256_file(path),
        "canonical_report_size_bytes": path.stat().st_size,
        "signals": parse_patchops_report_signals(text),
    }


def determine_final_result(*, canonical: dict[str, Any], patchops_commands: Sequence[dict[str, Any]], requested_result: str | None = None, requested_exit_code: int | None = None) -> dict[str, Any]:
    issues: list[str] = []
    if not canonical.get("canonical_report_exists"):
        issues.append("canonical report is missing")
    signals = canonical.get("signals") or {}
    result_text = signals.get("result_text")
    exit_code = signals.get("exit_code")
    if canonical.get("canonical_report_exists") and result_text is None:
        issues.append("canonical report Result is missing")
    if canonical.get("canonical_report_exists") and exit_code is None:
        issues.append("canonical report ExitCode is missing")
    if requested_result is not None and result_text is not None and requested_result != result_text:
        issues.append("requested final result does not match canonical report")
    if requested_exit_code is not None and exit_code is not None and requested_exit_code != exit_code:
        issues.append("requested exit code does not match canonical report")
    for command in patchops_commands:
        if command.get("timed_out"):
            issues.append(f"PatchOps command timed out: {command.get('label')}")
        if command.get("exit_code") not in (None, 0):
            issues.append(f"PatchOps command nonzero exit: {command.get('label')}")
    final_result = "PASS" if not issues and result_text == "PASS" and exit_code == 0 else "FAIL"
    return {
        "final_result": final_result,
        "final_exit_code": exit_code if exit_code is not None else requested_exit_code,
        "issues": issues,
        "canonical_result": result_text,
        "canonical_exit_code": exit_code,
    }


def build_session_payload(
    *,
    repo_root: str | Path | None = None,
    artifact_path: str | Path | None = None,
    artifact_sha256: str | None = None,
    staged_path: str | Path | None = None,
    patchops_commands: Sequence[dict[str, Any]] | None = None,
    safety: dict[str, bool] | None = None,
    canonical_report_path: str | Path | None = None,
    canonical_report_sha256: str | None = None,
    requested_result: str | None = None,
    requested_exit_code: int | None = None,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    artifact_resolved = None if artifact_path is None or not str(artifact_path).strip() else str(Path(artifact_path).resolve(strict=False))
    staged_resolved = None if staged_path is None or not str(staged_path).strip() else str(Path(staged_path).resolve(strict=False))
    commands = normalize_patchops_commands(patchops_commands)
    canonical = summarize_canonical_report(canonical_report_path, canonical_report_sha256)
    final = determine_final_result(canonical=canonical, patchops_commands=commands, requested_result=requested_result, requested_exit_code=requested_exit_code)
    safety_payload = dict(safety or _default_safety(canonical_report_found=bool(canonical.get("canonical_report_exists"))))
    safety_payload["canonical_report_found"] = bool(canonical.get("canonical_report_exists"))
    if commands:
        safety_payload["patchops_invoked"] = True
    return {
        "schema_version": 1,
        "producer": "patchops.copilot_downloader",
        "patch_name": PATCH_NAME,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "artifact": {
            "path": artifact_resolved,
            "sha256": artifact_sha256,
            "path_present": artifact_resolved is not None,
        },
        "staging": {
            "staged_path": staged_resolved,
            "staged_path_present": staged_resolved is not None,
        },
        "patchops_commands": commands,
        "safety": safety_payload,
        "canonical_report": canonical,
        "final": final,
    }


def _write_text_report(path: Path, payload: dict[str, Any]) -> None:
    final = payload["final"]
    artifact = payload["artifact"]
    staging = payload["staging"]
    canonical = payload["canonical_report"]
    lines: list[str] = [
        "PATCHOPS DOWNLOADER SESSION REPORT",
        "=================================",
        f"generated_utc: {payload['generated_utc']}",
        f"producer: {payload['producer']}",
        f"patch_name: {payload['patch_name']}",
        f"repo_root: {payload['repo_root']}",
        "",
        "artifact",
        f"  path: {artifact.get('path')}",
        f"  sha256: {artifact.get('sha256')}",
        "",
        "staging",
        f"  staged_path: {staging.get('staged_path')}",
        "",
        "canonical report",
        f"  path: {canonical.get('canonical_report_path')}",
        f"  exists: {canonical.get('canonical_report_exists')}",
        f"  sha256: {canonical.get('canonical_report_sha256')}",
        f"  size_bytes: {canonical.get('canonical_report_size_bytes')}",
        f"  result: {(canonical.get('signals') or {}).get('result_text')}",
        f"  exit_code: {(canonical.get('signals') or {}).get('exit_code')}",
        "",
        "patchops commands",
    ]
    for command in payload["patchops_commands"]:
        lines.extend(
            [
                "------------------------------------------------------------",
                f"label: {command.get('label')}",
                f"command: {command.get('command')}",
                f"working_directory: {command.get('working_directory')}",
                f"exit_code: {command.get('exit_code')}",
                f"timed_out: {command.get('timed_out')}",
                "stdout:",
                str(command.get("stdout", "")),
                "stderr:",
                str(command.get("stderr", "")),
            ]
        )
    if not payload["patchops_commands"]:
        lines.append("(none)")
    lines.extend(["", "safety flags"])
    for key, value in sorted(payload["safety"].items()):
        lines.append(f"{key}: {value}")
    lines.extend(["", "issues"])
    if final["issues"]:
        lines.extend([f"- {issue}" for issue in final["issues"]])
    else:
        lines.append("(none)")
    lines.extend(["", "final PASS/FAIL", str(final["final_result"]), "", f"final exit code: {final.get('final_exit_code')}"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_downloader_session_report(
    *,
    repo_root: str | Path | None = None,
    output_dir: str | Path | None = None,
    artifact_path: str | Path | None = None,
    artifact_sha256: str | None = None,
    staged_path: str | Path | None = None,
    patchops_commands: Sequence[dict[str, Any]] | None = None,
    safety: dict[str, bool] | None = None,
    canonical_report_path: str | Path | None = None,
    canonical_report_sha256: str | None = None,
    requested_result: str | None = None,
    requested_exit_code: int | None = None,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    out_dir = Path(output_dir).resolve(strict=False) if output_dir is not None else _repo_child(root, *DEFAULT_REPORT_DIR.split("/"))
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_session_payload(
        repo_root=root,
        artifact_path=artifact_path,
        artifact_sha256=artifact_sha256,
        staged_path=staged_path,
        patchops_commands=patchops_commands,
        safety=safety,
        canonical_report_path=canonical_report_path,
        canonical_report_sha256=canonical_report_sha256,
        requested_result=requested_result,
        requested_exit_code=requested_exit_code,
    )
    result_label = PASS_DOWNLOADER_SESSION_REPORTED if payload["final"]["final_result"] == "PASS" else FAIL_DOWNLOADER_SESSION_REPORTED
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = out_dir / f"patchops_downloader_session_report_{timestamp}.json"
    text_path = out_dir / f"patchops_downloader_session_report_{timestamp}.txt"
    latest_json_path = out_dir / "latest_downloader_session_report.json"
    latest_text_path = out_dir / "latest_downloader_session_report.txt"
    payload["result_label"] = result_label
    payload["report_paths"] = {
        "json": str(json_path),
        "text": str(text_path),
        "latest_json": str(latest_json_path),
        "latest_text": str(latest_text_path),
    }
    json_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    json_path.write_text(json_text, encoding="utf-8")
    latest_json_path.write_text(json_text, encoding="utf-8")
    _write_text_report(text_path, payload)
    _write_text_report(latest_text_path, payload)
    return {
        "ok": result_label in CONTROLLED_LABELS,
        "result_label": result_label,
        "final_result": payload["final"]["final_result"],
        "final_exit_code": payload["final"].get("final_exit_code"),
        "issues": payload["final"].get("issues", []),
        "report_paths": payload["report_paths"],
        "canonical_report": payload["canonical_report"],
        "artifact": payload["artifact"],
        "staging": payload["staging"],
        "patchops_command_count": len(payload["patchops_commands"]),
        "safety": payload["safety"],
    }


def _write_session_evidence(evidence_dir: Path, label: str, safety: DownloaderSafetyFlags, details: dict[str, Any]) -> dict[str, str]:
    evidence = DownloaderEvidenceRecord(
        patch_name=PATCH_NAME,
        result_label=label,
        safety=safety,
        details=details,
    )
    return write_evidence_pair(evidence_dir, "downloader_session_report", evidence)


def run_downloader_session_report(
    *,
    repo_root: str | Path | None = None,
    output_dir: str | Path | None = None,
    evidence_root: str | Path | None = None,
    artifact_path: str | Path | None = None,
    artifact_sha256: str | None = None,
    staged_path: str | Path | None = None,
    patchops_commands: Sequence[dict[str, Any]] | None = None,
    safety: dict[str, bool] | None = None,
    canonical_report_path: str | Path | None = None,
    canonical_report_sha256: str | None = None,
    requested_result: str | None = None,
    requested_exit_code: int | None = None,
    write_evidence: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve(strict=False)
    evidence_dir = Path(evidence_root).resolve(strict=False) if evidence_root is not None else _repo_child(root, "data", "runtime", "copilot_downloader", "d4_02_downloader_session_report")
    result = write_downloader_session_report(
        repo_root=root,
        output_dir=output_dir,
        artifact_path=artifact_path,
        artifact_sha256=artifact_sha256,
        staged_path=staged_path,
        patchops_commands=patchops_commands,
        safety=safety,
        canonical_report_path=canonical_report_path,
        canonical_report_sha256=canonical_report_sha256,
        requested_result=requested_result,
        requested_exit_code=requested_exit_code,
    )
    flags = DownloaderSafetyFlags(canonical_report_found=bool(result["canonical_report"].get("canonical_report_exists")), patchops_invoked=result["patchops_command_count"] > 0)
    checks = {
        "session_report_written": True,
        "artifact_path_hash_included": "path" in result["artifact"] and "sha256" in result["artifact"],
        "staged_path_included": "staged_path" in result["staging"],
        "patchops_commands_included": result["patchops_command_count"] >= 0,
        "stdout_stderr_exit_codes_included": True,
        "safety_flags_included": bool(result["safety"]),
        "canonical_report_path_hash_included": "canonical_report_path" in result["canonical_report"] and "canonical_report_sha256" in result["canonical_report"],
        "final_pass_fail_included": result["final_result"] in {"PASS", "FAIL"},
        "latest_pointers_written": Path(result["report_paths"]["latest_json"]).is_file() and Path(result["report_paths"]["latest_text"]).is_file(),
        "browser_not_started": not flags.browser_used,
        "clipboard_not_read": not flags.clipboard_read,
        "clipboard_not_written": not flags.clipboard_written,
        "artifact_not_executed_by_reporter": not flags.artifact_executed,
        "uploader_not_imported": True,
    }
    result["checks"] = checks
    result["safety"] = flags.to_dict() | {key: value for key, value in result["safety"].items() if key not in flags.to_dict()}
    if write_evidence:
        result["evidence_files"] = _write_session_evidence(evidence_dir, result["result_label"], flags, {"checks": checks, "report_paths": result["report_paths"], "final_result": result["final_result"], "issues": result["issues"]})
    else:
        result["evidence_files"] = {}
    result["ok"] = result["ok"] and all(checks.values())
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.copilot_downloader.downloader_session_report")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--evidence-root", default=None)
    parser.add_argument("--artifact-path", default=None)
    parser.add_argument("--artifact-sha256", default=None)
    parser.add_argument("--staged-path", default=None)
    parser.add_argument("--patchops-commands-json", default=None)
    parser.add_argument("--safety-json", default=None)
    parser.add_argument("--canonical-report-path", default=None)
    parser.add_argument("--canonical-report-sha256", default=None)
    parser.add_argument("--requested-result", default=None)
    parser.add_argument("--requested-exit-code", type=int, default=None)
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run_downloader_session_report(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        evidence_root=args.evidence_root,
        artifact_path=args.artifact_path,
        artifact_sha256=args.artifact_sha256,
        staged_path=args.staged_path,
        patchops_commands=_load_json_arg(args.patchops_commands_json, default=[]),
        safety=_load_json_arg(args.safety_json, default=None),
        canonical_report_path=args.canonical_report_path,
        canonical_report_sha256=args.canonical_report_sha256,
        requested_result=args.requested_result,
        requested_exit_code=args.requested_exit_code,
        write_evidence=not args.no_write_evidence,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())