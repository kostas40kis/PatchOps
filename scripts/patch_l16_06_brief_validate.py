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

from patchops.llm_browser import live_adapter_edge_real_page_metadata_detection_broad_checkpoint as l16_06


def main() -> int:
    parser = argparse.ArgumentParser(description="Brief validation for L16.6 Edge real-page metadata broad checkpoint")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--execute-live-checkpoint", action="store_true")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve() if args.repo_root else _REPO_ROOT_FOR_IMPORTS
    payload = l16_06.build_edge_real_page_metadata_detection_broad_checkpoint(root, execute_live_checkpoint=args.execute_live_checkpoint)
    summary = {
        "ok": payload.get("ok") is True,
        "patch": payload.get("patch"),
        "source_patch": payload.get("source_patch"),
        "explicit_live_metadata_checkpoint": payload.get("explicit_live_metadata_checkpoint"),
        "l16_1_through_l16_5_accepted": payload.get("l16_1_through_l16_5_accepted"),
        "l16_3_passive_plan_checkpoint_still_green": payload.get("l16_3_passive_plan_checkpoint_still_green"),
        "l16_4_authorization_gate_still_green": payload.get("l16_4_authorization_gate_still_green"),
        "l16_5_dry_metadata_detection_readback_still_green": payload.get("l16_5_dry_metadata_detection_readback_still_green"),
        "l16_5_live_metadata_detection_green_when_requested": payload.get("l16_5_live_metadata_detection_green_when_requested"),
        "page_detection_execution_allowed": payload.get("page_detection_execution_allowed"),
        "real_page_detection_active": payload.get("real_page_detection_active"),
        "browser_started": payload.get("browser_started"),
        "edge_process_started": payload.get("edge_process_started"),
        "chatgpt_url_opened": payload.get("chatgpt_url_opened"),
        "page_metadata_detection_proven": payload.get("page_metadata_detection_proven"),
        "selenium_imported_by_readback": payload.get("selenium_imported_by_readback"),
        "cdp_used": payload.get("cdp_used"),
        "dom_scraping_performed": payload.get("dom_scraping_performed"),
        "conversation_reading_performed": payload.get("conversation_reading_performed"),
        "artifact_detection_performed": payload.get("artifact_detection_performed"),
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
