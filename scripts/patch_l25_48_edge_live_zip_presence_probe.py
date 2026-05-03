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

from patchops.llm_browser.live_adapter_edge_logged_in_target_chat_zip_presence_live_probe import (
    AUTHORIZATION_TOKEN,
    DEFAULT_TARGET_URL,
    PATCH,
)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run L25.48A Edge live zip-presence probe.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--profile-dir", default="")
    parser.add_argument("--download-dir", default="")
    parser.add_argument("--keep-open", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    module_path = REPO_ROOT / "patchops" / "llm_browser" / "live_adapter_edge_logged_in_target_chat_zip_presence_live_probe.py"
    command = [
        sys.executable,
        str(module_path),
        "--repo-root", str(Path(args.repo_root).resolve()),
        "--target-url", args.target_url,
        "--timeout-seconds", str(args.timeout_seconds),
        "--allow-live-browser",
        "--authorization-token", AUTHORIZATION_TOKEN,
        "--compact",
    ]
    if args.profile_dir:
        command.extend(["--profile-dir", args.profile_dir])
    if args.download_dir:
        command.extend(["--download-dir", args.download_dir])
    if args.keep_open:
        command.append("--keep-open")
    completed = subprocess.run(command, cwd=str(REPO_ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    try:
        payload = json.loads(completed.stdout.strip().splitlines()[-1])
    except Exception:
        payload = {
            "ok": False,
            "patch": PATCH,
            "error": "live probe did not emit parseable JSON",
            "raw_stdout_tail": completed.stdout[-800:],
            "raw_stderr_tail": completed.stderr[-800:],
        }
    if completed.returncode != 0 or payload.get("ok") is not True:
        print(json.dumps({
            "ok": False,
            "patch": PATCH,
            "live_edge_zip_presence_probe_failed": True,
            "subprocess_exit_code": completed.returncode,
            "payload": payload,
        }, sort_keys=True, separators=(",", ":") if args.compact else None))
        if completed.stderr:
            print(completed.stderr, file=sys.stderr)
        return 1
    required_true = {
        "l25_48_writer_quoting_repaired": True,
        "real_edge_live_target_chat_zip_presence_probe": True,
        "uses_real_browser_as_main_proof": True,
        "browser_started": True,
        "zip_candidate_found": True,
        "dedicated_profile_used": True,
        "minimal_dom_artifact_detection_performed": True,
    }
    required_false = {
        "synthetic_fixture_main_proof": False,
        "default_profile_used": False,
        "conversation_text_logged": False,
        "prompt_text_extracted": False,
        "artifact_content_reading_performed": False,
        "download_click_performed": False,
        "download_performed": False,
        "downloaded_file_bytes_read": False,
        "run_package_invoked_by_l25_48a": False,
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
    if int(payload.get("zip_candidate_count") or 0) < 1:
        raise AssertionError("zip_candidate_count must be >= 1")
    print(json.dumps({
        "ok": True,
        "patch": PATCH,
        "l25_48_writer_quoting_repaired": True,
        "real_edge_live_target_chat_zip_presence_probe": True,
        "uses_real_browser_as_main_proof": True,
        "zip_candidate_found": True,
        "zip_candidate_count": payload.get("zip_candidate_count"),
        "browser_started": True,
        "target_url": payload.get("target_url"),
        "profile_dir": payload.get("profile_dir"),
        "download_click_performed": False,
        "download_performed": False,
        "artifact_content_reading_performed": False,
        "run_package_invoked_by_l25_48a": False,
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

