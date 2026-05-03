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

from patchops.llm_browser import live_adapter_edge_real_page_detection_passive_plan_checkpoint as l16_03


def main() -> int:
    parser = argparse.ArgumentParser(description="Brief validation for L16.3 Edge real-page detection passive plan checkpoint")
    parser.add_argument("--repo-root", default=None)
    args = parser.parse_args()
    root = Path(args.repo_root).resolve() if args.repo_root else _REPO_ROOT_FOR_IMPORTS
    payload = l16_03.build_edge_real_page_detection_passive_plan_checkpoint(root)
    summary = {
        "ok": payload.get("ok") is True,
        "patch": payload.get("patch"),
        "source_patch": payload.get("source_patch"),
        "source_l16_2_cli_readback_checkpoint_surface_present": payload.get("source_l16_2_cli_readback_checkpoint_surface_present"),
        "nested_cli_readbacks_performed": payload.get("nested_cli_readbacks_performed"),
        "future_detection_plan_is_passive": payload.get("future_detection_plan_is_passive"),
        "future_detection_plan_is_metadata_only": payload.get("future_detection_plan_is_metadata_only"),
        "real_page_detection_active": payload.get("real_page_detection_active"),
        "target_url_allowlisted": (payload.get("target_url_status") or {}).get("ok"),
        "browser_started": payload.get("browser_started"),
        "edge_process_started": payload.get("edge_process_started"),
        "page_inspection_performed": payload.get("page_inspection_performed"),
        "chatgpt_url_opened": payload.get("chatgpt_url_opened"),
        "artifact_detection_performed": payload.get("artifact_detection_performed"),
        "selenium_imported_by_readback": payload.get("selenium_imported_by_readback"),
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
