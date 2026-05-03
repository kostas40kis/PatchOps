from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT_TEXT = str(_REPO_ROOT)
if _REPO_ROOT_TEXT not in sys.path:
    sys.path.insert(0, _REPO_ROOT_TEXT)

from patchops.llm_browser import live_adapter_edge_downloaded_file_validation_passive_preflight_gate as l19_01


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Brief L19.1 validation")
    parser.add_argument("--repo-root", default=str(_REPO_ROOT))
    parser.add_argument("--target-url", default="https://chatgpt.com/")
    args = parser.parse_args(argv)

    default_payload = l19_01.build_edge_downloaded_file_validation_passive_preflight_gate(
        Path(args.repo_root).resolve(),
        target_url=args.target_url,
    )
    authorized_payload = l19_01.build_edge_downloaded_file_validation_passive_preflight_gate(
        Path(args.repo_root).resolve(),
        allow_file_validation_preflight=True,
        authorization_token=l19_01.REQUIRED_FILE_VALIDATION_PREFLIGHT_AUTHORIZATION_TOKEN,
        target_url=args.target_url,
    )
    ok = (
        default_payload.get("ok") is True
        and authorized_payload.get("ok") is True
        and default_payload.get("downloaded_file_validation_preflight_authorized") is False
        and authorized_payload.get("downloaded_file_validation_preflight_authorized") is True
        and authorized_payload.get("downloaded_file_validation_execution_allowed") is False
        and authorized_payload.get("downloaded_file_validation_active") is False
        and authorized_payload.get("downloaded_file_validation_performed") is False
        and authorized_payload.get("downloaded_file_exists_check_performed") is False
        and authorized_payload.get("downloaded_file_bytes_read") is False
        and authorized_payload.get("downloaded_archive_opened") is False
        and authorized_payload.get("downloaded_archive_contents_listed") is False
        and authorized_payload.get("browser_started") is False
        and authorized_payload.get("edge_process_started") is False
    )
    summary = {
        "ok": ok,
        "patch": authorized_payload.get("patch"),
        "source_patch": authorized_payload.get("source_patch"),
        "source_l18_7_download_workflow_final_marker_accepted": authorized_payload.get("source_l18_7_download_workflow_final_marker_accepted"),
        "l18_download_workflow_stream_complete": authorized_payload.get("l18_download_workflow_stream_complete"),
        "default_downloaded_file_validation_preflight_authorized": default_payload.get("downloaded_file_validation_preflight_authorized"),
        "authorized_downloaded_file_validation_preflight_authorized": authorized_payload.get("downloaded_file_validation_preflight_authorized"),
        "downloaded_file_validation_preflight_authorization_is_readback_only_in_l19_1": authorized_payload.get("downloaded_file_validation_preflight_authorization_is_readback_only_in_l19_1"),
        "downloaded_file_validation_execution_allowed": authorized_payload.get("downloaded_file_validation_execution_allowed"),
        "downloaded_file_validation_active": authorized_payload.get("downloaded_file_validation_active"),
        "downloaded_file_validation_performed": authorized_payload.get("downloaded_file_validation_performed"),
        "downloaded_file_exists_check_performed": authorized_payload.get("downloaded_file_exists_check_performed"),
        "downloaded_file_bytes_read": authorized_payload.get("downloaded_file_bytes_read"),
        "downloaded_archive_opened": authorized_payload.get("downloaded_archive_opened"),
        "downloaded_archive_contents_listed": authorized_payload.get("downloaded_archive_contents_listed"),
        "download_workflow_active": authorized_payload.get("download_workflow_active"),
        "download_performed": authorized_payload.get("download_performed"),
        "click_download_performed": authorized_payload.get("click_download_performed"),
        "artifact_content_reading_performed": authorized_payload.get("artifact_content_reading_performed"),
        "browser_started": authorized_payload.get("browser_started"),
        "edge_process_started": authorized_payload.get("edge_process_started"),
        "chatgpt_url_opened": authorized_payload.get("chatgpt_url_opened"),
        "package_run_performed_by_adapter": authorized_payload.get("package_run_performed_by_adapter"),
        "missing_commands": authorized_payload.get("missing_commands"),
        "missing_doc_phrases": authorized_payload.get("missing_doc_phrases"),
        "required_repo_paths_ok": (authorized_payload.get("required_repo_paths") or {}).get("ok"),
        "next_patch": authorized_payload.get("next_patch"),
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
