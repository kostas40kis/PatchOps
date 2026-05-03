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

from patchops.llm_browser import live_adapter_edge_real_page_detection_controlled_live_plan_authorization_gate as l16_04

TOKEN = "PATCHOPS_L16_EDGE_REAL_PAGE_DETECTION_EXECUTION_AUTHORIZED"


def main() -> int:
    parser = argparse.ArgumentParser(description="Brief validation for L16.4 Edge real-page detection live-plan authorization gate")
    parser.add_argument("--repo-root", default=None)
    args = parser.parse_args()
    root = Path(args.repo_root).resolve() if args.repo_root else _REPO_ROOT_FOR_IMPORTS
    default_payload = l16_04.build_edge_real_page_detection_controlled_live_plan_authorization_gate(root)
    authorized_payload = l16_04.build_edge_real_page_detection_controlled_live_plan_authorization_gate(
        root,
        allow_real_page_detection_execution=True,
        authorization_token=TOKEN,
        target_url="https://chatgpt.com/",
    )
    ok = (
        default_payload.get("ok") is True
        and authorized_payload.get("ok") is True
        and default_payload.get("source_l16_3_passive_plan_checkpoint_accepted") is True
        and default_payload.get("real_page_detection_execution_authorized") is False
        and authorized_payload.get("real_page_detection_execution_authorized") is True
        and authorized_payload.get("execution_authorization_is_readback_only_in_l16_4") is True
        and authorized_payload.get("page_detection_execution_allowed") is False
        and authorized_payload.get("real_page_detection_active") is False
        and authorized_payload.get("browser_started") is False
        and authorized_payload.get("edge_process_started") is False
        and authorized_payload.get("page_inspection_performed") is False
        and authorized_payload.get("chatgpt_url_opened") is False
        and authorized_payload.get("selenium_imported_by_readback") is False
    )
    summary = {
        "ok": ok,
        "patch": default_payload.get("patch"),
        "source_patch": default_payload.get("source_patch"),
        "source_l16_3_passive_plan_checkpoint_accepted": default_payload.get("source_l16_3_passive_plan_checkpoint_accepted"),
        "default_authorized": default_payload.get("real_page_detection_execution_authorized"),
        "authorized_readback_authorized": authorized_payload.get("real_page_detection_execution_authorized"),
        "execution_authorization_is_readback_only_in_l16_4": authorized_payload.get("execution_authorization_is_readback_only_in_l16_4"),
        "page_detection_execution_allowed": authorized_payload.get("page_detection_execution_allowed"),
        "real_page_detection_active": authorized_payload.get("real_page_detection_active"),
        "browser_started": authorized_payload.get("browser_started"),
        "edge_process_started": authorized_payload.get("edge_process_started"),
        "page_inspection_performed": authorized_payload.get("page_inspection_performed"),
        "chatgpt_url_opened": authorized_payload.get("chatgpt_url_opened"),
        "artifact_detection_performed": authorized_payload.get("artifact_detection_performed"),
        "selenium_imported_by_readback": authorized_payload.get("selenium_imported_by_readback"),
        "auto_send_allowed": authorized_payload.get("auto_send_allowed"),
        "missing_commands": authorized_payload.get("missing_commands"),
        "missing_doc_phrases": authorized_payload.get("missing_doc_phrases"),
        "required_repo_paths_ok": (authorized_payload.get("required_repo_paths") or {}).get("ok"),
        "next_patch": authorized_payload.get("next_patch"),
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
