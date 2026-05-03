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

from patchops.llm_browser import live_adapter_edge_first_controlled_real_page_metadata_detection_proof as l16_05


def main() -> int:
    parser = argparse.ArgumentParser(description="Brief validation for L16.5 Edge first real-page metadata detection proof")
    parser.add_argument("--repo-root", default=None)
    args = parser.parse_args()
    root = Path(args.repo_root).resolve() if args.repo_root else _REPO_ROOT_FOR_IMPORTS
    payload = l16_05.build_edge_first_controlled_real_page_metadata_detection_proof(root)
    summary = {
        "ok": payload.get("ok") is True,
        "patch": payload.get("patch"),
        "source_patch": payload.get("source_patch"),
        "source_l16_4_authorization_gate_accepted": payload.get("source_l16_4_authorization_gate_accepted"),
        "dry_readback": True,
        "page_detection_execution_allowed": payload.get("page_detection_execution_allowed"),
        "real_page_detection_active": payload.get("real_page_detection_active"),
        "page_metadata_detection_performed": payload.get("page_metadata_detection_performed"),
        "page_metadata_detection_proven": payload.get("page_metadata_detection_proven"),
        "chatgpt_url_opened": payload.get("chatgpt_url_opened"),
        "browser_started": payload.get("browser_started"),
        "edge_process_started": payload.get("edge_process_started"),
        "selenium_imported_by_readback": payload.get("selenium_imported_by_readback"),
        "cdp_used": payload.get("cdp_used"),
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
