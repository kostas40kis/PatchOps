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

from patchops.llm_browser import live_adapter_edge_first_controlled_open_proof as l15_03


def main() -> int:
    parser = argparse.ArgumentParser(description="Brief validation for L15.3 first controlled Edge open proof")
    parser.add_argument("--repo-root", default=None)
    args = parser.parse_args()
    root = Path(args.repo_root).resolve() if args.repo_root else _REPO_ROOT_FOR_IMPORTS
    payload = l15_03.build_edge_first_controlled_open_proof(root)
    summary = {
        "ok": payload.get("ok") is True,
        "patch": payload.get("patch"),
        "source_patch": payload.get("source_patch"),
        "dry_readback": True,
        "launch_execution_allowed": payload.get("launch_execution_allowed"),
        "browser_started": payload.get("browser_started"),
        "edge_process_started": payload.get("edge_process_started"),
        "live_open_smoke_executed": payload.get("live_open_smoke_executed"),
        "live_open_smoke_proven": payload.get("live_open_smoke_proven"),
        "profile_candidate_under_allowed_runtime_root": payload.get("profile_candidate_under_allowed_runtime_root"),
        "default_edge_profile_rejected": payload.get("default_edge_profile_rejected"),
        "open_url_is_about_blank": payload.get("open_url_is_about_blank"),
        "edge_executable_discovered": (payload.get("edge_executable_discovery") or {}).get("ok"),
        "selenium_imported_by_readback": payload.get("selenium_imported_by_readback"),
        "chatgpt_url_opened": payload.get("chatgpt_url_opened"),
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
