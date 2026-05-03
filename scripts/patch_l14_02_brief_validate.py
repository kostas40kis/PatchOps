from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

COMMAND = "browser-start-supervised-launch-edge-launch-authorization-gate"
TOKEN = "EDGE_LAUNCH_AUTH_REVIEWED_NO_EXECUTION"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    commands = [
        [sys.executable, "-m", "compileall", "patchops/llm_browser", "tests/test_l14_01_edge_launch_readiness_consolidation_current.py", "tests/test_l14_02_edge_launch_authorization_gate_current.py", "scripts/patch_l14_02_brief_validate.py"],
        [sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(root), "--json", "--compact"],
        [sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(root), "--request-launch-authorization", "--operator-confirmation-token", TOKEN, "--json", "--compact"],
    ]
    results = []
    for args in commands:
        completed = subprocess.run(args, cwd=root, text=True, capture_output=True, timeout=120)
        results.append({"args": args, "exit_code": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr})
    default_payload = json.loads(results[1]["stdout"]) if results[1]["exit_code"] == 0 else {}
    token_payload = json.loads(results[2]["stdout"]) if results[2]["exit_code"] == 0 else {}
    ok = all(item["exit_code"] == 0 for item in results)
    ok = ok and default_payload.get("ok") is True
    ok = ok and default_payload.get("patch") == "L14.2"
    ok = ok and default_payload.get("request_launch_authorization_observed") is False
    ok = ok and default_payload.get("launch_execution_allowed") is False
    ok = ok and default_payload.get("browser_started") is False
    ok = ok and token_payload.get("launch_authorization_granted_for_future_stage") is True
    ok = ok and token_payload.get("launch_authorization_effective_for_execution") is False
    ok = ok and token_payload.get("launch_execution_allowed") is False
    ok = ok and TOKEN not in results[2]["stdout"]
    summary = {
        "ok": ok,
        "patch": "L14.2",
        "command": COMMAND,
        "command_exit_codes": [item["exit_code"] for item in results],
        "default_requested": default_payload.get("request_launch_authorization_observed"),
        "default_launch_execution_allowed": default_payload.get("launch_execution_allowed"),
        "token_future_stage_granted": token_payload.get("launch_authorization_granted_for_future_stage"),
        "token_execution_effective": token_payload.get("launch_authorization_effective_for_execution"),
        "token_echoed": TOKEN in results[2]["stdout"],
        "browser_started": token_payload.get("browser_started"),
        "edge_process_started": token_payload.get("edge_process_started"),
        "next_patch": token_payload.get("next_patch"),
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    if not ok:
        diag = [{"args": item["args"], "exit_code": item["exit_code"], "stdout_tail": item["stdout"][-2000:], "stderr_tail": item["stderr"][-2000:]} for item in results]
        print(json.dumps(diag, indent=2), file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
