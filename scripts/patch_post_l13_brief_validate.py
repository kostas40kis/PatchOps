from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

COMMAND = "browser-start-supervised-launch-post-l13-frontier-selection"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    commands = [
        [sys.executable, "-m", "compileall", "patchops/llm_browser", "tests/test_post_l13_frontier_selection_current.py", "scripts/patch_post_l13_brief_validate.py"],
        [sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(root), "--json", "--compact"],
    ]
    results = []
    for args in commands:
        completed = subprocess.run(args, cwd=root, text=True, capture_output=True, timeout=120)
        results.append({"args": args, "exit_code": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr})
    parsed = json.loads(results[1]["stdout"]) if results[1]["exit_code"] == 0 else {}
    ok = all(item["exit_code"] == 0 for item in results)
    ok = ok and parsed.get("ok") is True
    ok = ok and parsed.get("source_l13_complete") is True
    ok = ok and parsed.get("remaining_l13_patches") == []
    ok = ok and parsed.get("frontier_selected") is False
    ok = ok and parsed.get("no_browser_start") is True
    ok = ok and parsed.get("no_selenium_import") is True
    summary = {
        "ok": ok,
        "patch": "post-L13",
        "command": COMMAND,
        "command_exit_codes": [item["exit_code"] for item in results],
        "source_l13_complete": parsed.get("source_l13_complete"),
        "remaining_l13_patches": parsed.get("remaining_l13_patches"),
        "frontier_selected": parsed.get("frontier_selected"),
        "recommended_safe_next_patch_name": parsed.get("recommended_safe_next_patch_name"),
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    if not ok:
        diag = [{"args": item["args"], "exit_code": item["exit_code"], "stdout_tail": item["stdout"][-2000:], "stderr_tail": item["stderr"][-2000:]} for item in results]
        print(json.dumps(diag, indent=2), file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
