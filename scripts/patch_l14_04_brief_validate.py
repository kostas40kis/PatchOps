from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

COMMAND = "browser-start-supervised-launch-edge-dedicated-profile-lifecycle-preflight"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    commands = [
        [sys.executable, "-m", "compileall", "patchops/llm_browser", "tests/test_l14_03_edge_launch_dry_run_plan_readback_current.py", "tests/test_l14_04_edge_dedicated_profile_lifecycle_preflight_current.py", "scripts/patch_l14_04_brief_validate.py"],
        [sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(root), "--json", "--compact"],
    ]
    results = []
    for args in commands:
        completed = subprocess.run(args, cwd=root, text=True, capture_output=True, timeout=120)
        results.append({"args": args, "exit_code": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr})
    payload = json.loads(results[1]["stdout"]) if results[1]["exit_code"] == 0 else {}
    ok = all(item["exit_code"] == 0 for item in results)
    ok = ok and payload.get("ok") is True
    ok = ok and payload.get("patch") == "L14.4"
    ok = ok and payload.get("profile_candidate_under_allowed_runtime_root") is True
    ok = ok and payload.get("profile_lifecycle_steps_are_passive") is True
    ok = ok and payload.get("profile_directory_created") is False
    ok = ok and payload.get("profile_directory_mutated") is False
    ok = ok and payload.get("filesystem_writes_performed") == []
    ok = ok and payload.get("launch_execution_allowed") is False
    ok = ok and payload.get("browser_started") is False
    ok = ok and payload.get("edge_process_started") is False
    ok = ok and payload.get("selenium_imported_by_readback") is False
    summary = {
        "ok": ok,
        "patch": "L14.4",
        "command": COMMAND,
        "command_exit_codes": [item["exit_code"] for item in results],
        "profile_allowed": payload.get("profile_candidate_under_allowed_runtime_root"),
        "profile_created": payload.get("profile_directory_created"),
        "profile_mutated": payload.get("profile_directory_mutated"),
        "filesystem_writes": payload.get("filesystem_writes_performed"),
        "launch_execution_allowed": payload.get("launch_execution_allowed"),
        "browser_started": payload.get("browser_started"),
        "edge_process_started": payload.get("edge_process_started"),
        "next_patch": payload.get("next_patch"),
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    if not ok:
        diag = [{"args": item["args"], "exit_code": item["exit_code"], "stdout_tail": item["stdout"][-2000:], "stderr_tail": item["stderr"][-2000:]} for item in results]
        print(json.dumps(diag, indent=2), file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
