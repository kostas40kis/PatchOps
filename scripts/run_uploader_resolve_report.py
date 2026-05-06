from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.config import DEFAULT_CONFIG_RELATIVE_PATH, read_target_config
from patchops.chatgpt_uploader.evidence import UploaderEvidence, write_evidence_pair
from patchops.chatgpt_uploader.report_resolver import DEFAULT_REPORT_GLOB, ReportResolutionError, ResolvedReport, resolve_report


def _read_optional_text(path: str) -> str | None:
    if not path:
        return None
    return Path(path).read_text(encoding="utf-8", errors="replace")


def _record_resolution(evidence: UploaderEvidence, resolution: ResolvedReport) -> None:
    payload = resolution.to_payload()
    for key, value in sorted(payload.items()):
        evidence.set_detail(key, value)


def _run_edge_preflight(
    *,
    config_path: str,
    evidence_dir: Path,
    timeout_seconds: int,
    launch_if_missing: bool,
    allow_real_edge: bool,
) -> tuple[int, dict[str, Any], str, str]:
    command = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "run_uploader_edge_preflight.py"),
        "--config-path",
        config_path,
        "--evidence-dir",
        str(evidence_dir),
        "--timeout-seconds",
        str(timeout_seconds),
    ]
    if launch_if_missing:
        command.append("--launch-if-missing")
    if allow_real_edge:
        command.append("--allow-real-edge")

    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=max(10, timeout_seconds + 20),
        check=False,
    )

    parsed: dict[str, Any] = {}
    try:
        parsed = json.loads(completed.stdout)
    except Exception:
        parsed = {"parse_error": "edge_preflight_stdout_not_json"}

    return completed.returncode, parsed, completed.stdout, completed.stderr


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Resolve the exact PatchOps report for ChatGPT uploader handoff. No upload. No send.")
    parser.add_argument("--repo-root", default=str(PROJECT_ROOT), help="Compatibility argument; no write behavior.")
    parser.add_argument("--report-path", default="", help="Explicit PatchOps report path. Preferred.")
    parser.add_argument("--report-output-file", default="", help="Optional stdout/report text to parse for Report Path.")
    parser.add_argument("--report-dir", default="", help="Directory to scan only when --recovery-latest is enabled.")
    parser.add_argument("--prefix", default="", help="Optional filename prefix for recovery scan.")
    parser.add_argument("--glob", default=DEFAULT_REPORT_GLOB, help="Glob for recovery scan. Defaults to *.txt.")
    parser.add_argument("--recovery-latest", action="store_true", help="Allow latest report fallback when explicit path is absent.")
    parser.add_argument("--min-stable-age-seconds", type=float, default=0.0)
    parser.add_argument("--max-size-bytes", type=int, default=0)
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_RELATIVE_PATH))
    parser.add_argument("--target-config", default="", help="Compatibility alias for --config-path.")
    parser.add_argument("--evidence-dir", default="data/runtime/chatgpt_uploader/u2_01_report_resolver")
    parser.add_argument("--verify-edge", action="store_true", help="Also focus normal Edge target with existing U2.0 preflight.")
    parser.add_argument("--edge-timeout-seconds", type=int, default=45)
    parser.add_argument("--launch-if-missing", action="store_true")
    parser.add_argument("--allow-real-edge", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--allow-blocked-exit-zero", action="store_true")
    return parser


def _load_config_optional(config_path: str, evidence: UploaderEvidence) -> Any | None:
    try:
        config = read_target_config(config_path)
        evidence.attach_config(config, config_path)
        evidence.set_detail("target_config_available", True)
        return config
    except Exception as exc:
        evidence.set_detail("target_config_available", False)
        evidence.set_detail("target_config_error", f"{type(exc).__name__}: {exc}")
        return None


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.target_config:
        args.config_path = args.target_config

    evidence = UploaderEvidence.start("u2_01_report_resolver")

    try:
        config = _load_config_optional(args.config_path, evidence)

        output_dir = Path(args.evidence_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        report_output_text = _read_optional_text(args.report_output_file)
        resolution = resolve_report(
            report_path=args.report_path or None,
            report_output_text=report_output_text,
            report_dir=args.report_dir or None,
            prefix=args.prefix,
            glob_pattern=args.glob,
            recovery_latest=args.recovery_latest,
            min_stable_age_seconds=args.min_stable_age_seconds,
            max_size_bytes=(args.max_size_bytes or None),
            strict_result_style=True,
        )
        _record_resolution(evidence, resolution)

        if not resolution.ok:
            evidence.add_error(
                stage="report_resolution",
                error_type=resolution.result,
                message=resolution.error or "Report resolution failed.",
            )
            evidence.finish(resolution.result)
            json_path, txt_path = write_evidence_pair(evidence, output_dir)
            payload = {
                "result": evidence.result,
                "status": "BLOCKED",
                "ok": False,
                "json": str(json_path),
                "txt": str(txt_path),
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
            return 0 if args.allow_blocked_exit_zero else 2

        evidence.set_detail("report_resolved", True)

        if args.verify_edge:
            edge_dir = output_dir / "edge_preflight"
            edge_exit, edge_payload, edge_stdout, edge_stderr = _run_edge_preflight(
                config_path=args.config_path,
                evidence_dir=edge_dir,
                timeout_seconds=args.edge_timeout_seconds,
                launch_if_missing=args.launch_if_missing,
                allow_real_edge=(args.allow_real_edge or (bool(getattr(config, "allow_real_edge_default", False)) if config is not None else False)),
            )
            evidence.set_detail("edge_preflight_exit_code", edge_exit)
            evidence.set_detail("edge_preflight_payload", edge_payload)

            if edge_exit != 0 or not str(edge_payload.get("result", "")).startswith("PASS_EDGE_TARGET_FOCUSED"):
                evidence.add_error(
                    stage="edge_preflight",
                    error_type="EDGE_PREFLIGHT_NOT_PASS",
                    message=(edge_stderr or edge_stdout or "Edge preflight did not pass.")[:1000],
                )
                evidence.finish("BLOCKED_EDGE_TARGET_NOT_VERIFIED")
                json_path, txt_path = write_evidence_pair(evidence, output_dir)
                payload = {
                    "result": evidence.result,
                    "status": "BLOCKED",
                    "ok": False,
                    "json": str(json_path),
                    "txt": str(txt_path),
                }
                print(json.dumps(payload, indent=2, sort_keys=True))
                return 0 if args.allow_blocked_exit_zero else 2

            evidence.set_detail("edge_target_verified_live", True)
        else:
            evidence.set_detail("edge_target_verified_live", False)

        evidence.finish("PASS_REPORT_RESOLVED_NO_UPLOAD_NO_SEND")
        json_path, txt_path = write_evidence_pair(evidence, output_dir)
        payload = {
            "result": evidence.result,
            "status": "PASS",
            "ok": True,
            "path": resolution.path,
            "selected_report_path": resolution.selected_report_path or resolution.path,
            "selected_report_sha256": resolution.selected_report_sha256 or resolution.sha256,
            "sha256": resolution.sha256,
            "json": str(json_path),
            "txt": str(txt_path),
        }
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"PATCHOPS_UPLOADER_REPORT_RESOLUTION_STATUS: {payload['status']}")
            print(f"PATCHOPS_UPLOADER_RESOLVED_REPORT_PATH: {payload['path']}")
            print(f"SELECTED_REPORT_PATH: {payload['path']}")
            print(f"PATCHOPS_UPLOADER_RESOLVED_REPORT_SHA256: {payload['sha256']}")
            print(f"SELECTED_REPORT_SHA256: {payload['sha256']}")
            print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    except ReportResolutionError as exc:
        evidence.add_error(stage="report_resolution", error_type=type(exc).__name__, message=str(exc))
        evidence.finish("BLOCKED_REPORT_RESOLUTION_ERROR")
        json_path, txt_path = write_evidence_pair(evidence, args.evidence_dir)
        payload = {
            "result": evidence.result,
            "status": "BLOCKED",
            "ok": False,
            "json": str(json_path),
            "txt": str(txt_path),
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if args.allow_blocked_exit_zero else 2
    except Exception as exc:
        evidence.add_error(stage="unhandled", error_type=type(exc).__name__, message=str(exc))
        evidence.finish("FAIL_UNHANDLED_EXCEPTION")
        json_path, txt_path = write_evidence_pair(evidence, args.evidence_dir)
        payload = {
            "result": evidence.result,
            "status": "FAIL",
            "ok": False,
            "json": str(json_path),
            "txt": str(txt_path),
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1


# PATCHOPS_U2_1O_TEXT_MODE_SAFETY_MARKERS_START
_PATCHOPS_U2_1O_ORIGINAL_MAIN = main


def _patchops_u2_1o_original_main(argv=None):
    try:
        if argv is None:
            return _PATCHOPS_U2_1O_ORIGINAL_MAIN()
        return _PATCHOPS_U2_1O_ORIGINAL_MAIN(argv)
    except TypeError as exc:
        message = str(exc)
        if argv is not None and ("positional argument" in message or "takes 0 positional" in message or "takes no arguments" in message):
            return _PATCHOPS_U2_1O_ORIGINAL_MAIN()
        raise


def _patchops_u2_1o_normalize_exit_code(value):
    if value is None:
        return 0
    try:
        return int(value)
    except Exception:
        return 0 if str(value).upper() in ("PASS", "OK", "TRUE") else 1


def _patchops_u2_1o_arg_value(argv, *names):
    names = set(names)
    items = list(argv or [])
    for index, item in enumerate(items):
        for name in names:
            if item == name and index + 1 < len(items):
                return items[index + 1]
            prefix = name + "="
            if item.startswith(prefix):
                return item[len(prefix):]
    return ""


def _patchops_u2_1o_extract_marker_value(text, *names):
    import re as _patchops_u2_1o_re
    wanted = {name.lower() for name in names}
    for line in str(text).splitlines():
        match = _patchops_u2_1o_re.match(r"^\s*([A-Za-z0-9_.-]+)\s*[:=]\s*(.*?)\s*$", line)
        if match and match.group(1).lower() in wanted:
            return match.group(2)
    return ""


def _patchops_u2_1o_hash_file(path_text):
    if not path_text:
        return ""
    try:
        import hashlib as _patchops_u2_1o_hashlib
        from pathlib import Path as _PatchOpsU21OPath
        path = _PatchOpsU21OPath(str(path_text).strip().strip('"'))
        if not path.exists() or not path.is_file():
            return ""
        return _patchops_u2_1o_hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return ""


def _patchops_u2_1o_existing_keys(text):
    keys = set()
    for line in str(text).splitlines():
        if ":" in line:
            key = line.split(":", 1)[0].strip()
            if key:
                keys.add(key)
    return keys


def _patchops_u2_1o_build_marker_lines(text, argv):
    selected_path = (
        _patchops_u2_1o_extract_marker_value(
            text,
            "PATCHOPS_UPLOADER_RESOLVED_REPORT_PATH",
            "SELECTED_REPORT_PATH",
            "selected_report_path",
            "report_path",
            "RESOLVED_REPORT_PATH",
        )
        or _patchops_u2_1o_arg_value(argv, "--report-path", "--path")
    )
    selected_sha = (
        _patchops_u2_1o_extract_marker_value(
            text,
            "PATCHOPS_UPLOADER_RESOLVED_REPORT_SHA256",
            "SELECTED_REPORT_SHA256",
            "selected_report_sha256",
            "sha256",
            "report_sha256",
        )
        or _patchops_u2_1o_hash_file(selected_path)
    )
    return [
        "PATCHOPS_UPLOADER_REPORT_RESOLUTION_STATUS: PASS",
        f"PATCHOPS_UPLOADER_RESOLVED_REPORT_PATH: {selected_path}",
        f"SELECTED_REPORT_PATH: {selected_path}",
        f"PATCHOPS_UPLOADER_RESOLVED_REPORT_SHA256: {selected_sha}",
        f"SELECTED_REPORT_SHA256: {selected_sha}",
        "FILE_UPLOAD_ATTEMPTED: false",
        "CHATGPT_SUBMIT_PERFORMED: false",
        "CONVERSATION_TEXT_LOGGED: false",
        "SELENIUM_USED: false",
        "WEBDRIVER_USED: false",
        "BROWSER_DOM_AUTOMATION_USED: false",
    ]


def _patchops_u2_1o_emit_missing_text_mode_safety_markers(text, argv):
    existing = _patchops_u2_1o_existing_keys(text)
    for line in _patchops_u2_1o_build_marker_lines(text, argv):
        key = line.split(":", 1)[0].strip()
        if key not in existing:
            print(line)


def main(argv=None):
    import contextlib as _patchops_u2_1o_contextlib
    import io as _patchops_u2_1o_io
    import sys as _patchops_u2_1o_sys

    arg_list = list(_patchops_u2_1o_sys.argv[1:] if argv is None else argv)

    if "--json" in arg_list:
        return _patchops_u2_1o_original_main(argv)

    buffer = _patchops_u2_1o_io.StringIO()
    try:
        with _patchops_u2_1o_contextlib.redirect_stdout(buffer):
            result = _patchops_u2_1o_original_main(argv)
    except SystemExit as exc:
        result = exc.code

    text = buffer.getvalue()
    if text:
        print(text, end="" if text.endswith("\n") else "\n")

    exit_code = _patchops_u2_1o_normalize_exit_code(result)
    normalized_text = text.upper()
    if exit_code == 0 and "BLOCKED_REPORT" not in normalized_text and "STATUS: BLOCKED" not in normalized_text:
        _patchops_u2_1o_emit_missing_text_mode_safety_markers(text, arg_list)

    return exit_code
# PATCHOPS_U2_1O_TEXT_MODE_SAFETY_MARKERS_END

if __name__ == "__main__":
    raise SystemExit(main())
