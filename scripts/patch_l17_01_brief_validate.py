from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _discover_repo_root() -> Path:
    here = Path(__file__).resolve()
    candidates = [Path.cwd().resolve(), *here.parents]
    for candidate in candidates:
        if (candidate / "patchops").is_dir() and (candidate / "pyproject.toml").exists():
            return candidate
    return here.parents[1]


_REPO_ROOT_FOR_IMPORTS = _discover_repo_root()
if str(_REPO_ROOT_FOR_IMPORTS) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT_FOR_IMPORTS))

from patchops.llm_browser import live_adapter_edge_artifact_detection_passive_preflight_gate as l17_01

TOKEN = "PATCHOPS_L17_EDGE_ARTIFACT_DETECTION_PREFLIGHT_AUTHORIZED"


def main() -> int:
    parser = argparse.ArgumentParser(description="Brief validation for L17.1 Edge artifact detection passive preflight gate")
    parser.add_argument("--repo-root", default=None)
    args = parser.parse_args()
    root = Path(args.repo_root).resolve() if args.repo_root else _REPO_ROOT_FOR_IMPORTS
    default_payload = l17_01.build_edge_artifact_detection_passive_preflight_gate(root)
    authorized_payload = l17_01.build_edge_artifact_detection_passive_preflight_gate(
        root,
        allow_artifact_detection_preflight=True,
        authorization_token=TOKEN,
        target_url="https://chatgpt.com/",
    )
    ok = (
        default_payload.get("ok") is True
        and authorized_payload.get("ok") is True
        and default_payload.get("source_l16_7_final_marker_accepted") is True
        and default_payload.get("l16_metadata_detection_stream_complete") is True
        and authorized_payload.get("artifact_detection_preflight_authorized") is True
        and authorized_payload.get("artifact_detection_execution_allowed") is False
        and authorized_payload.get("artifact_detection_active") is False
        and authorized_payload.get("download_workflow_active") is False
        and authorized_payload.get("browser_started") is False
        and authorized_payload.get("edge_process_started") is False
        and authorized_payload.get("chatgpt_url_opened") is False
        and authorized_payload.get("artifact_detection_performed") is False
    )
    summary = {
        "ok": ok,
        "patch": default_payload.get("patch"),
        "source_patch": default_payload.get("source_patch"),
        "source_l16_7_final_marker_accepted": default_payload.get("source_l16_7_final_marker_accepted"),
        "l16_metadata_detection_stream_complete": default_payload.get("l16_metadata_detection_stream_complete"),
        "default_artifact_preflight_authorized": default_payload.get("artifact_detection_preflight_authorized"),
        "authorized_artifact_preflight_authorized": authorized_payload.get("artifact_detection_preflight_authorized"),
        "artifact_detection_execution_allowed": authorized_payload.get("artifact_detection_execution_allowed"),
        "artifact_detection_active": authorized_payload.get("artifact_detection_active"),
        "download_workflow_active": authorized_payload.get("download_workflow_active"),
        "browser_started": authorized_payload.get("browser_started"),
        "edge_process_started": authorized_payload.get("edge_process_started"),
        "chatgpt_url_opened": authorized_payload.get("chatgpt_url_opened"),
        "artifact_detection_performed": authorized_payload.get("artifact_detection_performed"),
        "download_performed": authorized_payload.get("download_performed"),
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
