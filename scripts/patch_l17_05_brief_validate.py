from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT_TEXT = str(_REPO_ROOT)
if _REPO_ROOT_TEXT not in sys.path:
    sys.path.insert(0, _REPO_ROOT_TEXT)

from patchops.llm_browser import live_adapter_edge_artifact_presence_metadata_proof as l17_05


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Brief L17.5 validation")
    parser.add_argument("--repo-root", default=str(_REPO_ROOT))
    parser.add_argument("--target-url", default="https://chatgpt.com/")
    args = parser.parse_args(argv)

    default_payload = l17_05.build_edge_artifact_presence_metadata_proof(
        Path(args.repo_root).resolve(),
        target_url=args.target_url,
    )
    authorized_payload = l17_05.build_edge_artifact_presence_metadata_proof(
        Path(args.repo_root).resolve(),
        allow_artifact_presence_metadata_proof=True,
        authorization_token=l17_05.REQUIRED_METADATA_PROOF_AUTHORIZATION_TOKEN,
        candidate_metadata=l17_05.positive_metadata_fixture(),
        target_url=args.target_url,
    )
    ok = (
        default_payload.get("ok") is True
        and authorized_payload.get("ok") is True
        and default_payload.get("artifact_presence_metadata_classification_performed") is False
        and authorized_payload.get("artifact_presence_metadata_proof_authorized") is True
        and authorized_payload.get("artifact_presence_metadata_classification_performed") is True
        and authorized_payload.get("artifact_presence_detected_from_metadata") is True
        and authorized_payload.get("real_page_inspection_performed") is False
        and authorized_payload.get("live_browser_artifact_detection_active") is False
        and authorized_payload.get("artifact_content_reading_performed") is False
        and authorized_payload.get("download_workflow_active") is False
        and authorized_payload.get("download_performed") is False
        and authorized_payload.get("click_download_performed") is False
        and authorized_payload.get("browser_started") is False
        and authorized_payload.get("edge_process_started") is False
    )
    summary = {
        "ok": ok,
        "patch": authorized_payload.get("patch"),
        "source_patch": authorized_payload.get("source_patch"),
        "source_l17_4_controlled_live_authorization_gate_accepted": authorized_payload.get("source_l17_4_controlled_live_authorization_gate_accepted"),
        "l17_4_complete": authorized_payload.get("l17_4_complete"),
        "default_artifact_presence_metadata_classification_performed": default_payload.get("artifact_presence_metadata_classification_performed"),
        "authorized_artifact_presence_metadata_proof_authorized": authorized_payload.get("artifact_presence_metadata_proof_authorized"),
        "authorized_artifact_presence_metadata_classification_performed": authorized_payload.get("artifact_presence_metadata_classification_performed"),
        "artifact_presence_detected_from_metadata": authorized_payload.get("artifact_presence_detected_from_metadata"),
        "artifact_presence_detection_scope": authorized_payload.get("artifact_presence_detection_scope"),
        "real_page_inspection_performed": authorized_payload.get("real_page_inspection_performed"),
        "live_browser_artifact_detection_active": authorized_payload.get("live_browser_artifact_detection_active"),
        "live_browser_artifact_detection_performed": authorized_payload.get("live_browser_artifact_detection_performed"),
        "artifact_content_reading_performed": authorized_payload.get("artifact_content_reading_performed"),
        "download_workflow_active": authorized_payload.get("download_workflow_active"),
        "download_performed": authorized_payload.get("download_performed"),
        "click_download_performed": authorized_payload.get("click_download_performed"),
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
