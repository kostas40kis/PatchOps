from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT_TEXT = str(_REPO_ROOT)
if _REPO_ROOT_TEXT not in sys.path:
    sys.path.insert(0, _REPO_ROOT_TEXT)

from patchops.llm_browser import live_adapter_edge_artifact_detection_final_acceptance_marker as l17_07


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Brief L17.7 validation")
    parser.add_argument("--repo-root", default=str(_REPO_ROOT))
    parser.add_argument("--target-url", default="https://chatgpt.com/")
    args = parser.parse_args(argv)

    payload = l17_07.build_edge_artifact_detection_final_acceptance_marker(
        Path(args.repo_root).resolve(),
        target_url=args.target_url,
    )
    summary = {
        "ok": payload.get("ok"),
        "patch": payload.get("patch"),
        "source_patch": payload.get("source_patch"),
        "source_l17_6_broad_checkpoint_accepted": payload.get("source_l17_6_broad_checkpoint_accepted"),
        "l17_1_through_l17_6_remain_accepted": payload.get("l17_1_through_l17_6_remain_accepted"),
        "l17_artifact_detection_stream_complete": payload.get("l17_artifact_detection_stream_complete"),
        "artifact_detection_stream_completion_is_metadata_only": payload.get("artifact_detection_stream_completion_is_metadata_only"),
        "metadata_only_artifact_presence_proof_accepted": payload.get("metadata_only_artifact_presence_proof_accepted"),
        "artifact_presence_metadata_classification_validated": payload.get("artifact_presence_metadata_classification_validated"),
        "download_workflow_is_next_separate_stream": payload.get("download_workflow_is_next_separate_stream"),
        "download_workflow_active": payload.get("download_workflow_active"),
        "download_performed": payload.get("download_performed"),
        "click_download_performed": payload.get("click_download_performed"),
        "pasteback_workflow_active": payload.get("pasteback_workflow_active"),
        "package_run_from_browser_remains_inactive": payload.get("package_run_from_browser_remains_inactive"),
        "package_run_performed_by_adapter": payload.get("package_run_performed_by_adapter"),
        "real_page_inspection_performed": payload.get("real_page_inspection_performed"),
        "live_browser_artifact_detection_active": payload.get("live_browser_artifact_detection_active"),
        "artifact_content_reading_performed": payload.get("artifact_content_reading_performed"),
        "browser_started": payload.get("browser_started"),
        "edge_process_started": payload.get("edge_process_started"),
        "chatgpt_url_opened": payload.get("chatgpt_url_opened"),
        "missing_commands": payload.get("missing_commands"),
        "missing_doc_phrases": payload.get("missing_doc_phrases"),
        "required_repo_paths_ok": (payload.get("required_repo_paths") or {}).get("ok"),
        "remaining_l17_patches": payload.get("remaining_l17_patches"),
        "next_patch": payload.get("next_patch"),
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
