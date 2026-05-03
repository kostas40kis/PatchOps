from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

COMMAND = "browser-start-supervised-launch-edge-launch-dry-run-plan-readback"
TOKEN = "EDGE_LAUNCH_AUTH_REVIEWED_NO_EXECUTION"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    commands = [
        [sys.executable, "-m", "compileall", "patchops/llm_browser", "tests/test_l14_02_edge_launch_authorization_gate_current.py", "tests/test_l14_03_edge_launch_dry_run_plan_readback_current.py", "scripts/patch_l14_03_brief_validate.py"],
        [sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(root), "--request-launch-authorization", "--operator-confirmation-token", TOKEN, "--json", "--compact"],
    ]
    results = []
    for args in commands:
        completed = subprocess.run(args, cwd=root, text=True, capture_output=True, timeout=120)
        results.append({"args": args, "exit_code": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr})
    payload = json.loads(results[1]["stdout"]) if results[1]["exit_code"] == 0 else {}
    ok = all(item["exit_code"] == 0 for item in results)
    ok = ok and payload.get("ok") is True
    ok = ok and payload.get("patch") == "L14.3"
    ok = ok and payload.get("launch_authorization_granted_for_future_stage") is True
    ok = ok and payload.get("dry_run_plan_is_passive") is True
    ok = ok and payload.get("dry_run_plan_executed") is False
    ok = ok and payload.get("dry_run_plan_materialized_as_process_args") is False
    ok = ok and payload.get("real_subprocess_invocation_built") is False
    ok = ok and payload.get("launch_execution_allowed") is False
    ok = ok and payload.get("browser_started") is False
    ok = ok and payload.get("edge_process_started") is False
    ok = ok and payload.get("selenium_imported_by_readback") is False
    ok = ok and TOKEN not in results[1]["stdout"]
    summary = {
        "ok": ok,
        "patch": "L14.3",
        "command": COMMAND,
        "command_exit_codes": [item["exit_code"] for item in results],
        "future_stage_granted": payload.get("launch_authorization_granted_for_future_stage"),
        "dry_run_plan_is_passive": payload.get("dry_run_plan_is_passive"),
        "dry_run_plan_executed": payload.get("dry_run_plan_executed"),
        "process_args_built": payload.get("dry_run_plan_materialized_as_process_args"),
        "launch_execution_allowed": payload.get("launch_execution_allowed"),
        "browser_started": payload.get("browser_started"),
        "edge_process_started": payload.get("edge_process_started"),
        "token_echoed": TOKEN in results[1]["stdout"],
        "next_patch": payload.get("next_patch"),
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    if not ok:
        diag = [{"args": item["args"], "exit_code": item["exit_code"], "stdout_tail": item["stdout"][-2000:], "stderr_tail": item["stderr"][-2000:]} for item in results]
        print(json.dumps(diag, indent=2), file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
