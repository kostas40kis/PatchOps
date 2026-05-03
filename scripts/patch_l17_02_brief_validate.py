from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# L17.2a repair: when this validator is executed as a script path
# (py scripts/patch_l17_02_brief_validate.py), Python puts scripts/ on
# sys.path[0]. Add the repository root explicitly before importing patchops.
_REPO_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT_TEXT = str(_REPO_ROOT)
if _REPO_ROOT_TEXT not in sys.path:
    sys.path.insert(0, _REPO_ROOT_TEXT)

from patchops.llm_browser import live_adapter_edge_artifact_detection_cli_readback_checkpoint as l17_02


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Brief L17.2 validation")
    parser.add_argument("--repo-root", default=str(_REPO_ROOT))
    parser.add_argument("--target-url", default="https://chatgpt.com/")
    args = parser.parse_args(argv)

    payload = l17_02.build_edge_artifact_detection_cli_readback_checkpoint(
        Path(args.repo_root).resolve(),
        target_url=args.target_url,
    )
    summary = {
        "ok": payload.get("ok"),
        "patch": payload.get("patch"),
        "source_patch": payload.get("source_patch"),
        "l17_1_passive_preflight_gate_accepted": payload.get("l17_1_passive_preflight_gate_accepted"),
        "l17_1_default_compact_readback_ok": payload.get("l17_1_default_compact_readback_ok"),
        "l17_1_authorized_compact_readback_ok": payload.get("l17_1_authorized_compact_readback_ok"),
        "default_artifact_preflight_authorized": payload.get("default_artifact_preflight_authorized"),
        "authorized_artifact_preflight_authorized": payload.get("authorized_artifact_preflight_authorized"),
        "artifact_detection_execution_allowed": payload.get("artifact_detection_execution_allowed"),
        "artifact_detection_active": payload.get("artifact_detection_active"),
        "artifact_detection_performed": payload.get("artifact_detection_performed"),
        "download_workflow_active": payload.get("download_workflow_active"),
        "download_performed": payload.get("download_performed"),
        "browser_started": payload.get("browser_started"),
        "edge_process_started": payload.get("edge_process_started"),
        "chatgpt_url_opened": payload.get("chatgpt_url_opened"),
        "package_run_performed_by_adapter": payload.get("package_run_performed_by_adapter"),
        "avoid_nested_cli_validation_cascades": payload.get("avoid_nested_cli_validation_cascades"),
        "missing_commands": payload.get("missing_commands"),
        "missing_doc_phrases": payload.get("missing_doc_phrases"),
        "required_repo_paths_ok": (payload.get("required_repo_paths") or {}).get("ok"),
        "next_patch": payload.get("next_patch"),
        "validator_import_context_repaired": True,
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
