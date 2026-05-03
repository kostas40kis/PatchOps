from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT_TEXT = str(_REPO_ROOT)
if _REPO_ROOT_TEXT not in sys.path:
    sys.path.insert(0, _REPO_ROOT_TEXT)

from patchops.llm_browser import live_adapter_edge_download_workflow_final_acceptance_marker as l18_07


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Brief L18.7 validation")
    parser.add_argument("--repo-root", default=str(_REPO_ROOT))
    parser.add_argument("--target-url", default="https://chatgpt.com/")
    args = parser.parse_args(argv)

    payload = l18_07.build_edge_download_workflow_final_acceptance_marker(
        Path(args.repo_root).resolve(),
        target_url=args.target_url,
    )
    summary = {
        "ok": payload.get("ok"),
        "patch": payload.get("patch"),
        "source_patch": payload.get("source_patch"),
        "source_l18_6_broad_checkpoint_accepted": payload.get("source_l18_6_broad_checkpoint_accepted"),
        "l18_1_through_l18_6_remain_accepted": payload.get("l18_1_through_l18_6_remain_accepted"),
        "l18_download_workflow_stream_complete": payload.get("l18_download_workflow_stream_complete"),
        "download_workflow_stream_completion_is_metadata_only": payload.get("download_workflow_stream_completion_is_metadata_only"),
        "metadata_only_download_readiness_proof_accepted": payload.get("metadata_only_download_readiness_proof_accepted"),
        "download_metadata_classification_validated": payload.get("download_metadata_classification_validated"),
        "downloaded_file_validation_is_next_separate_stream": payload.get("downloaded_file_validation_is_next_separate_stream"),
        "downloaded_file_validation_active": payload.get("downloaded_file_validation_active"),
        "downloaded_file_validation_performed": payload.get("downloaded_file_validation_performed"),
        "download_workflow_execution_allowed": payload.get("download_workflow_execution_allowed"),
        "download_workflow_active": payload.get("download_workflow_active"),
        "download_allowed": payload.get("download_allowed"),
        "download_performed": payload.get("download_performed"),
        "downloaded_file_bytes_read": payload.get("downloaded_file_bytes_read"),
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
        "remaining_l18_patches": payload.get("remaining_l18_patches"),
        "next_patch": payload.get("next_patch"),
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
