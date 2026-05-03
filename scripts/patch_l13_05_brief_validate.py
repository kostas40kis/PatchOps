from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-aggregate-gate"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-fixture-matrix-readback"


def run_cmd(args: list[str], cwd: Path, timeout: int = 120) -> dict[str, Any]:
    completed = subprocess.run(args, cwd=cwd, text=True, capture_output=True, timeout=timeout)
    return {
        "args": args,
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "stdout_len": len(completed.stdout),
        "stderr_len": len(completed.stderr),
        "stdout_tail": completed.stdout[-2000:],
        "stderr_tail": completed.stderr[-2000:],
    }


def parse_json_stdout(item: dict[str, Any]) -> dict[str, Any]:
    text = str(item.get("stdout") or "").strip()
    if not text:
        raise ValueError("command produced no stdout JSON")
    candidates = [text]
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        candidates.extend(reversed(lines))
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        candidates.append(text[first:last + 1])
    last_error: Exception | None = None
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError as exc:
            last_error = exc
            continue
        if isinstance(parsed, dict):
            return parsed
        last_error = ValueError("JSON stdout was not an object")
    raise ValueError(f"could not parse JSON stdout; stdout_len={item.get('stdout_len')}; last_error={last_error}")


def _candidate_truthful(payload: dict[str, Any]) -> bool:
    selected = payload.get("edge_executable_selected_path")
    candidates = payload.get("edge_executable_probe_candidates") or []
    if payload.get("edge_executable_path_selected") is True:
        return any(
            isinstance(item, dict)
            and item.get("path") == selected
            and item.get("exists") is True
            and item.get("is_file") is True
            for item in candidates
        )
    return selected is None


def _no_launch(payload: dict[str, Any]) -> bool:
    false_fields = [
        "edge_executable_launch_attempted",
        "startup_allowed",
        "live_start_performed",
        "browser_started",
        "edge_process_started",
        "browser_session_created",
        "driver_created",
        "profile_directory_created",
        "click_download_performed",
        "download_performed",
        "paste_performed",
        "send_or_submit_performed",
        "package_run_performed_by_adapter",
        "git_commit_executed",
        "git_push_executed",
        "selenium_imported_by_readback",
    ]
    list_fields = ["filesystem_writes_performed", "adapter_filesystem_writes_performed", "side_effects_performed", "forbidden_optional_imports_observed"]
    return all(payload.get(field) is False for field in false_fields) and all(payload.get(field) == [] for field in list_fields)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    profile = root / "data" / "runtime" / "browser_profiles" / "edge_l13_05_brief"
    existing = root / "data" / "runtime" / "edge_probe_fixture" / "msedge_l13_05_brief.exe"
    missing = root / "data" / "runtime" / "edge_probe_fixture" / "missing-msedge-l13-05-brief.exe"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("fixture executable placeholder", encoding="utf-8")

    commands: list[dict[str, Any]] = []
    commands.append(run_cmd([sys.executable, "-m", "compileall", "patchops/llm_browser", "tests/test_l13_03_edge_executable_filesystem_probe_execution_fixture_matrix_current.py", "tests/test_l13_04_edge_executable_filesystem_probe_execution_fixture_matrix_cli_readback_current.py", "tests/test_l13_05_edge_executable_filesystem_probe_execution_aggregate_gate_current.py", "scripts/patch_l13_05_brief_validate.py"], root))
    commands.append(run_cmd([sys.executable, "-m", "patchops.cli", "llm-browser", SOURCE_COMMAND, "--repo-root", str(root), "--allow-live-start", "--profile-dir", str(profile), "--allow-executable-probe", "--activate-executable-filesystem-probe", "--allow-real-filesystem-probe", "--allow-executable-filesystem-probe-execution", "--extra-candidate", str(missing), "--extra-candidate", str(existing), "--json", "--compact"], root))
    commands.append(run_cmd([sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(root), "--allow-live-start", "--profile-dir", str(profile), "--allow-executable-probe", "--activate-executable-filesystem-probe", "--allow-real-filesystem-probe", "--allow-executable-filesystem-probe-execution", "--extra-candidate", str(missing), "--extra-candidate", str(existing), "--json", "--compact"], root))

    parse_errors: list[str] = []
    parsed: list[dict[str, Any]] = []
    for item in commands[1:]:
        if item["exit_code"] == 0:
            try:
                parsed.append(parse_json_stdout(item))
            except Exception as exc:  # noqa: BLE001 - validator diagnostic
                parse_errors.append(str(exc))

    ok = all(item["exit_code"] == 0 for item in commands)
    ok = ok and not parse_errors and len(parsed) == 2
    source_payload = parsed[0] if len(parsed) >= 1 else {}
    aggregate_payload = parsed[1] if len(parsed) >= 2 else {}
    ok = ok and source_payload.get("patch") == "L13.4"
    ok = ok and source_payload.get("source_patch") == "L13.3"
    ok = ok and source_payload.get("edge_executable_filesystem_probe_performed") is True
    ok = ok and _candidate_truthful(source_payload)
    ok = ok and _no_launch(source_payload)
    ok = ok and aggregate_payload.get("patch") == "L13.5"
    ok = ok and aggregate_payload.get("source_patch") == "L13.4"
    ok = ok and aggregate_payload.get("source_l13_04_fixture_matrix_readback_remains_accepted") is True
    ok = ok and aggregate_payload.get("edge_executable_filesystem_probe_performed") is True
    ok = ok and aggregate_payload.get("truthful_selected_path_existing_reported_candidate") is True
    ok = ok and aggregate_payload.get("filesystem_probe_only_when_l12_execution_preflight_ready") is True
    ok = ok and _candidate_truthful(aggregate_payload)
    ok = ok and _no_launch(aggregate_payload)

    summary = {
        "ok": ok,
        "patch": "L13.5",
        "command": COMMAND,
        "source_command": SOURCE_COMMAND,
        "command_exit_codes": [item["exit_code"] for item in commands],
        "stdout_lengths": [item["stdout_len"] for item in commands],
        "stderr_lengths": [item["stderr_len"] for item in commands],
        "parsed_payload_count": len(parsed),
        "parse_errors": parse_errors,
        "source_patch": source_payload.get("patch"),
        "aggregate_patch": aggregate_payload.get("patch"),
        "source_probe_performed": source_payload.get("edge_executable_filesystem_probe_performed"),
        "aggregate_probe_performed": aggregate_payload.get("edge_executable_filesystem_probe_performed"),
        "aggregate_truthful_selection": aggregate_payload.get("truthful_selected_path_existing_reported_candidate"),
        "aggregate_no_launch": _no_launch(aggregate_payload) if aggregate_payload else False,
        "next_patch": "L13.6 Live adapter Microsoft Edge executable filesystem probe execution aggregate gate CLI/readback",
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    if not ok:
        diagnostic = []
        for item in commands:
            diagnostic.append({
                "args": item["args"],
                "exit_code": item["exit_code"],
                "stdout_len": item["stdout_len"],
                "stderr_len": item["stderr_len"],
                "stdout_tail": item["stdout_tail"],
                "stderr_tail": item["stderr_tail"],
            })
        print(json.dumps({"parse_errors": parse_errors, "commands": diagnostic}, indent=2), file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
