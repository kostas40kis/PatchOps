from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

COMMAND = "browser-start-supervised-launch-edge-dedicated-profile-lifecycle-broad-validation-checkpoint"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-dedicated-profile-lifecycle-aggregate-gate-cli-readback"
L14_TESTS = [
    "tests/test_l14_01_edge_launch_readiness_consolidation_current.py",
    "tests/test_l14_02_edge_launch_authorization_gate_current.py",
    "tests/test_l14_03_edge_launch_dry_run_plan_readback_current.py",
    "tests/test_l14_04_edge_dedicated_profile_lifecycle_preflight_current.py",
    "tests/test_l14_05_edge_dedicated_profile_lifecycle_cli_readback_current.py",
    "tests/test_l14_06_edge_dedicated_profile_lifecycle_aggregate_gate_current.py",
    "tests/test_l14_07_edge_dedicated_profile_lifecycle_aggregate_gate_cli_readback_current.py",
    "tests/test_l14_08_edge_dedicated_profile_lifecycle_broad_validation_checkpoint_current.py",
]


def run_cmd(args: list[str], cwd: Path, timeout: int = 180) -> dict[str, Any]:
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


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    existing_tests = [rel for rel in L14_TESTS if (root / rel).exists()]
    missing_tests = [rel for rel in L14_TESTS if not (root / rel).exists()]
    commands = [
        [sys.executable, "-m", "compileall", "patchops/llm_browser", *existing_tests, "scripts/patch_l14_08_brief_validate.py"],
        [sys.executable, "-m", "patchops.cli", "llm-browser", SOURCE_COMMAND, "--repo-root", str(root), "--json", "--compact"],
        [sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(root), "--json", "--compact"],
    ]
    results = [run_cmd(args, root) for args in commands]
    parse_errors: list[str] = []
    parsed: list[dict[str, Any]] = []
    for item in results[1:]:
        if item["exit_code"] == 0:
            try:
                parsed.append(parse_json_stdout(item))
            except Exception as exc:  # noqa: BLE001 - validator diagnostic
                parse_errors.append(str(exc))
    source_payload = parsed[0] if len(parsed) >= 1 else {}
    checkpoint_payload = parsed[1] if len(parsed) >= 2 else {}
    ok = all(item["exit_code"] == 0 for item in results)
    ok = ok and not missing_tests and not parse_errors and len(parsed) == 2
    ok = ok and source_payload.get("patch") == "L14.7"
    ok = ok and source_payload.get("profile_aggregate_cli_readback_truthful") is True
    ok = ok and source_payload.get("profile_aggregate_cli_readback_is_passive") is True
    ok = ok and source_payload.get("profile_directory_created") is False
    ok = ok and source_payload.get("profile_directory_mutated") is False
    ok = ok and source_payload.get("launch_execution_allowed") is False
    ok = ok and checkpoint_payload.get("patch") == "L14.8"
    ok = ok and checkpoint_payload.get("source_patch") == "L14.7"
    ok = ok and checkpoint_payload.get("profile_broad_checkpoint_truthful") is True
    ok = ok and checkpoint_payload.get("profile_broad_checkpoint_is_passive") is True
    ok = ok and checkpoint_payload.get("planned_broad_validation_commands_are_passive") is True
    ok = ok and checkpoint_payload.get("broad_validation_commands_executed_by_checkpoint") is False
    ok = ok and checkpoint_payload.get("profile_directory_created") is False
    ok = ok and checkpoint_payload.get("profile_directory_mutated") is False
    ok = ok and checkpoint_payload.get("filesystem_writes_performed") == []
    ok = ok and checkpoint_payload.get("adapter_filesystem_writes_performed") == []
    ok = ok and checkpoint_payload.get("launch_execution_allowed") is False
    ok = ok and checkpoint_payload.get("browser_started") is False
    ok = ok and checkpoint_payload.get("edge_process_started") is False
    ok = ok and checkpoint_payload.get("selenium_imported_by_readback") is False
    summary = {
        "ok": ok,
        "patch": "L14.8",
        "command": COMMAND,
        "source_command": SOURCE_COMMAND,
        "command_exit_codes": [item["exit_code"] for item in results],
        "parsed_payload_count": len(parsed),
        "parse_errors": parse_errors,
        "existing_l14_tests": existing_tests,
        "missing_l14_tests": missing_tests,
        "source_patch": source_payload.get("patch"),
        "checkpoint_patch": checkpoint_payload.get("patch"),
        "profile_broad_checkpoint_truthful": checkpoint_payload.get("profile_broad_checkpoint_truthful"),
        "profile_broad_checkpoint_passive": checkpoint_payload.get("profile_broad_checkpoint_is_passive"),
        "planned_broad_validation_commands_are_passive": checkpoint_payload.get("planned_broad_validation_commands_are_passive"),
        "broad_validation_commands_executed_by_checkpoint": checkpoint_payload.get("broad_validation_commands_executed_by_checkpoint"),
        "profile_created": checkpoint_payload.get("profile_directory_created"),
        "profile_mutated": checkpoint_payload.get("profile_directory_mutated"),
        "filesystem_writes": checkpoint_payload.get("filesystem_writes_performed"),
        "launch_execution_allowed": checkpoint_payload.get("launch_execution_allowed"),
        "browser_started": checkpoint_payload.get("browser_started"),
        "edge_process_started": checkpoint_payload.get("edge_process_started"),
        "next_patch": checkpoint_payload.get("next_patch"),
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    if not ok:
        diag = [{"args": item["args"], "exit_code": item["exit_code"], "stdout_tail": item["stdout_tail"], "stderr_tail": item["stderr_tail"]} for item in results]
        print(json.dumps({"parse_errors": parse_errors, "missing_l14_tests": missing_tests, "commands": diag}, indent=2), file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
