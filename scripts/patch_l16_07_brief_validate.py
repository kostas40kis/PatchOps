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

from patchops.llm_browser import live_adapter_edge_real_page_metadata_detection_final_acceptance_marker as l16_07


def main() -> int:
    parser = argparse.ArgumentParser(description="Brief validation for L16.7 Edge real-page metadata final marker")
    parser.add_argument("--repo-root", default=None)
    args = parser.parse_args()
    root = Path(args.repo_root).resolve() if args.repo_root else _REPO_ROOT_FOR_IMPORTS
    payload = l16_07.build_edge_real_page_metadata_detection_final_acceptance_marker(root)
    summary = {
        "ok": payload.get("ok") is True,
        "patch": payload.get("patch"),
        "source_patch": payload.get("source_patch"),
        "l16_1_through_l16_6_accepted": payload.get("l16_1_through_l16_6_accepted"),
        "l16_metadata_detection_stream_complete": payload.get("l16_metadata_detection_stream_complete"),
        "metadata_only_page_detection_accepted": payload.get("metadata_only_page_detection_accepted"),
        "os_window_process_metadata_only_accepted": payload.get("os_window_process_metadata_only_accepted"),
        "artifact_detection_active": payload.get("artifact_detection_active"),
        "download_workflow_active": payload.get("download_workflow_active"),
        "browser_started": payload.get("browser_started"),
        "edge_process_started": payload.get("edge_process_started"),
        "chatgpt_url_opened": payload.get("chatgpt_url_opened"),
        "artifact_detection_performed": payload.get("artifact_detection_performed"),
        "download_performed": payload.get("download_performed"),
        "send_or_submit_performed": payload.get("send_or_submit_performed"),
        "package_run_performed_by_adapter": payload.get("package_run_performed_by_adapter"),
        "auto_send_allowed": payload.get("auto_send_allowed"),
        "missing_commands": payload.get("missing_commands"),
        "missing_doc_phrases": payload.get("missing_doc_phrases"),
        "required_repo_paths_ok": (payload.get("required_repo_paths") or {}).get("ok"),
        "next_patch": payload.get("next_patch"),
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
