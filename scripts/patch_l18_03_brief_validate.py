from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT_TEXT = str(_REPO_ROOT)
if _REPO_ROOT_TEXT not in sys.path:
    sys.path.insert(0, _REPO_ROOT_TEXT)

from patchops.llm_browser import live_adapter_edge_download_workflow_passive_plan_checkpoint as l18_03


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Brief L18.3 validation")
    parser.add_argument("--repo-root", default=str(_REPO_ROOT))
    parser.add_argument("--target-url", default="https://chatgpt.com/")
    args = parser.parse_args(argv)

    payload = l18_03.build_edge_download_workflow_passive_plan_checkpoint(
        Path(args.repo_root).resolve(),
        target_url=args.target_url,
    )
    summary = {
        "ok": payload.get("ok"),
        "patch": payload.get("patch"),
        "source_patch": payload.get("source_patch"),
        "source_l18_2_cli_readback_checkpoint_accepted": payload.get("source_l18_2_cli_readback_checkpoint_accepted"),
        "l18_2_complete": payload.get("l18_2_complete"),
        "l18_1_passive_preflight_gate_accepted": payload.get("l18_1_passive_preflight_gate_accepted"),
        "download_candidate_definition_blocks_download_file_read_package_run": payload.get("download_candidate_definition_blocks_download_file_read_package_run"),
        "future_download_plan_is_planned_not_executed": payload.get("future_download_plan_is_planned_not_executed"),
        "future_download_plan_blocks_click_download_file_read_paste_send_package_run": payload.get("future_download_plan_blocks_click_download_file_read_paste_send_package_run"),
        "download_workflow_execution_allowed": payload.get("download_workflow_execution_allowed"),
        "download_workflow_active": payload.get("download_workflow_active"),
        "download_allowed": payload.get("download_allowed"),
        "download_performed": payload.get("download_performed"),
        "downloaded_file_bytes_read": payload.get("downloaded_file_bytes_read"),
        "download_staging_path_metadata_only": payload.get("download_staging_path_metadata_only"),
        "download_staging_directory_created": payload.get("download_staging_directory_created"),
        "click_download_performed": payload.get("click_download_performed"),
        "artifact_content_reading_performed": payload.get("artifact_content_reading_performed"),
        "browser_started": payload.get("browser_started"),
        "edge_process_started": payload.get("edge_process_started"),
        "chatgpt_url_opened": payload.get("chatgpt_url_opened"),
        "package_run_performed_by_adapter": payload.get("package_run_performed_by_adapter"),
        "missing_commands": payload.get("missing_commands"),
        "missing_doc_phrases": payload.get("missing_doc_phrases"),
        "required_repo_paths_ok": (payload.get("required_repo_paths") or {}).get("ok"),
        "next_patch": payload.get("next_patch"),
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
