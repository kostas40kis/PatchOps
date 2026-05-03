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

from patchops.llm_browser.operator_pasted_edge_download_presence_probe import AUTHORIZATION_TOKEN, PATCH

def parse_last_json(stdout: str) -> dict[str, object]:
    lines = [line for line in stdout.splitlines() if line.strip()]
    if not lines:
        raise AssertionError("no JSON output from operator-pasted Edge probe")
    return json.loads(lines[-1])

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run L25.49C operator-pasted Edge download-presence probe.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--profile-dir", default="")
    parser.add_argument("--download-dir", default="")
    parser.add_argument("--wait-seconds", type=int, default=420)
    parser.add_argument("--keep-open", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    module_path = REPO_ROOT / "patchops" / "llm_browser" / "operator_pasted_edge_download_presence_probe.py"
    command = [
        sys.executable,
        str(module_path),
        "--repo-root", str(Path(args.repo_root).resolve()),
        "--wait-seconds", str(args.wait_seconds),
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
        payload = parse_last_json(completed.stdout)
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
            "operator_pasted_edge_download_presence_probe_failed": True,
            "subprocess_exit_code": completed.returncode,
            "payload": payload,
        }, sort_keys=True, separators=(",", ":") if args.compact else None))
        if completed.stderr:
            print(completed.stderr, file=sys.stderr)
        return 1
    required_true = {
        "l25_49b_html_quoting_indentation_repaired": True,
        "operator_pasted_edge_download_presence_probe": True,
        "edge_opened_for_operator_manual_navigation": True,
        "operator_pastes_link_manually": True,
        "operator_handles_cloudflare_manually": True,
        "uses_real_browser_as_main_proof": True,
        "download_candidate_found": True,
        "dedicated_profile_used": True,
        "minimal_dom_download_presence_detection_performed": True,
    }
    required_false = {
        "patchops_pasted_link": False,
        "synthetic_fixture_main_proof": False,
        "default_profile_used": False,
        "cloudflare_bypass_attempted": False,
        "download_click_automated": False,
        "download_performed_by_patchops": False,
        "artifact_bytes_read": False,
        "archive_member_extracted": False,
        "run_package_invoked_by_l25_49c": False,
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
    if int(payload.get("download_candidate_count") or 0) < 1:
        raise AssertionError("download_candidate_count must be >= 1")
    print(json.dumps({
        "ok": True,
        "patch": PATCH,
        "l25_49b_html_quoting_indentation_repaired": True,
        "operator_pasted_edge_download_presence_probe": True,
        "edge_opened_for_operator_manual_navigation": True,
        "operator_pastes_link_manually": True,
        "operator_handles_cloudflare_manually": True,
        "download_candidate_found": True,
        "download_candidate_count": payload.get("download_candidate_count"),
        "current_url_host": payload.get("current_url_host"),
        "uses_real_browser_as_main_proof": True,
        "patchops_pasted_link": False,
        "download_click_automated": False,
        "download_performed_by_patchops": False,
        "artifact_bytes_read": False,
        "archive_member_extracted": False,
        "run_package_invoked_by_l25_49c": False,
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

