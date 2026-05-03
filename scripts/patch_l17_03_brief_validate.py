from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT_TEXT = str(_REPO_ROOT)
if _REPO_ROOT_TEXT not in sys.path:
    sys.path.insert(0, _REPO_ROOT_TEXT)

from patchops.llm_browser import live_adapter_edge_artifact_detection_passive_plan_checkpoint as l17_03


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Brief L17.3 validation")
    parser.add_argument("--repo-root", default=str(_REPO_ROOT))
    parser.add_argument("--target-url", default="https://chatgpt.com/")
    args = parser.parse_args(argv)

    payload = l17_03.build_edge_artifact_detection_passive_plan_checkpoint(
        Path(args.repo_root).resolve(),
        target_url=args.target_url,
    )
    summary = {
        "ok": payload.get("ok"),
        "patch": payload.get("patch"),
        "source_patch": payload.get("source_patch"),
        "source_l17_2_cli_readback_checkpoint_accepted": payload.get("source_l17_2_cli_readback_checkpoint_accepted"),
        "l17_2_complete": payload.get("l17_2_complete"),
        "l17_1_passive_preflight_gate_accepted": payload.get("l17_1_passive_preflight_gate_accepted"),
        "artifact_presence_definition_blocks_content_and_download": payload.get("artifact_presence_definition_blocks_content_and_download"),
        "artifact_presence_definition_forbids_sensitive_observations": payload.get("artifact_presence_definition_forbids_sensitive_observations"),
        "future_artifact_presence_plan_is_planned_not_executed": payload.get("future_artifact_presence_plan_is_planned_not_executed"),
        "future_artifact_presence_plan_blocks_download_paste_send_package_run": payload.get("future_artifact_presence_plan_blocks_download_paste_send_package_run"),
        "artifact_detection_execution_allowed": payload.get("artifact_detection_execution_allowed"),
        "artifact_detection_active": payload.get("artifact_detection_active"),
        "artifact_detection_performed": payload.get("artifact_detection_performed"),
        "download_workflow_active": payload.get("download_workflow_active"),
        "download_performed": payload.get("download_performed"),
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
