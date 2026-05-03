from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT_STR = str(REPO_ROOT)
if REPO_ROOT_STR not in sys.path:
    sys.path.insert(0, REPO_ROOT_STR)

from patchops.llm_browser.manual_download_zip_inbox_live_probe import AUTHORIZATION_TOKEN, PATCH

def _parse_last_json(stdout: str) -> dict[str, object]:
    lines = [line for line in stdout.splitlines() if line.strip()]
    if not lines:
        raise AssertionError("no JSON output from live filesystem probe")
    return json.loads(lines[-1])

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run L25.49A selected/latest zip live probe.")
    parser.add_argument("--download-dir", required=True)
    parser.add_argument("--zip-path", default="")
    parser.add_argument("--pattern", default="*.zip")
    parser.add_argument("--wait-seconds", type=int, default=300)
    parser.add_argument("--stable-seconds", type=float, default=2.0)
    parser.add_argument("--recent-minutes", type=int, default=180)
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    module_path = REPO_ROOT / "patchops" / "llm_browser" / "manual_download_zip_inbox_live_probe.py"
    command = [
        sys.executable,
        str(module_path),
        "--download-dir", args.download_dir,
        "--pattern", args.pattern,
        "--wait-seconds", str(args.wait_seconds),
        "--stable-seconds", str(args.stable_seconds),
        "--recent-minutes", str(args.recent_minutes),
        "--allow-live-filesystem",
        "--authorization-token", AUTHORIZATION_TOKEN,
        "--compact",
    ]
    if args.zip_path:
        command.extend(["--zip-path", args.zip_path])
    completed = subprocess.run(command, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    try:
        payload = _parse_last_json(completed.stdout)
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "patch": PATCH,
            "error": f"could not parse probe JSON: {exc}",
            "raw_stdout_tail": completed.stdout[-1000:],
            "raw_stderr_tail": completed.stderr[-1000:],
        }, sort_keys=True, separators=(",", ":") if args.compact else None))
        return 1
    if completed.returncode != 0 or payload.get("ok") is not True:
        print(json.dumps({
            "ok": False,
            "patch": PATCH,
            "manual_zip_path_or_latest_download_live_probe_failed": True,
            "subprocess_exit_code": completed.returncode,
            "payload": payload,
        }, sort_keys=True, separators=(",", ":") if args.compact else None))
        if completed.stderr:
            print(completed.stderr, file=sys.stderr)
        return 1
    required_true = {
        "manual_browser_download_bridge": True,
        "explicit_zip_path_or_latest_download_supported": True,
        "uses_real_download_as_main_proof": True,
        "stable_size_observed": True,
        "zip_container_validation_performed": True,
        "zip_container_valid": True,
    }
    required_false = {
        "synthetic_fixture_main_proof": False,
        "cloudflare_bypass_attempted": False,
        "browser_automation_used": False,
        "selenium_used": False,
        "dom_scraping_used": False,
        "download_click_automated": False,
        "artifact_payload_extracted": False,
        "archive_member_extracted": False,
        "run_package_invoked_by_l25_49a": False,
        "pasteback": False,
        "send_submit_performed": False,
        "localhost_server_started": False,
        "browser_extension_used": False,
        "git_commit_performed": False,
        "git_push_performed": False,
    }
    for key, expected in required_true.items():
        if payload.get(key) is not expected:
            raise AssertionError(f"{key}: expected {expected!r}, got {payload.get(key)!r}")
    for key, expected in required_false.items():
        if payload.get(key) is not expected:
            raise AssertionError(f"{key}: expected {expected!r}, got {payload.get(key)!r}")
    if int(payload.get("zip_size_bytes") or 0) <= 0:
        raise AssertionError("zip_size_bytes must be > 0")
    if payload.get("zip_source_mode") not in ("explicit_zip_path", "latest_recent_download"):
        raise AssertionError(f"unexpected zip_source_mode: {payload.get('zip_source_mode')!r}")
    print(json.dumps({
        "ok": True,
        "patch": PATCH,
        "manual_browser_download_bridge": True,
        "explicit_zip_path_or_latest_download_supported": True,
        "uses_real_download_as_main_proof": True,
        "zip_source_mode": payload.get("zip_source_mode"),
        "zip_name": payload.get("zip_name"),
        "zip_path": payload.get("zip_path"),
        "zip_size_bytes": payload.get("zip_size_bytes"),
        "stable_size_observed": True,
        "zip_container_valid": True,
        "cloudflare_bypass_attempted": False,
        "browser_automation_used": False,
        "download_click_automated": False,
        "archive_member_extracted": False,
        "run_package_invoked_by_l25_49a": False,
        "pasteback": False,
        "send_submit_performed": False,
        "localhost_server_started": False,
        "browser_extension_used": False,
        "git_commit_performed": False,
        "git_push_performed": False,
    }, sort_keys=True, separators=(",", ":") if args.compact else None))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

