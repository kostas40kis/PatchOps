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

from patchops.llm_browser import live_adapter_edge_live_start_authorization_execution_gate_cli_readback as l15_02


def main() -> int:
    parser = argparse.ArgumentParser(description="Brief validation for L15.2 Edge live-start gate CLI readback")
    parser.add_argument("--repo-root", default=None)
    args = parser.parse_args()
    root = Path(args.repo_root).resolve() if args.repo_root else _REPO_ROOT_FOR_IMPORTS
    payload = l15_02.build_edge_live_start_authorization_execution_gate_cli_readback(root)
    summary = {
        "ok": payload.get("ok") is True,
        "patch": payload.get("patch"),
        "source_patch": payload.get("source_patch"),
        "no_authorization_readback_ok": payload.get("no_authorization_readback_ok"),
        "authorized_readback_ok": payload.get("authorized_readback_ok"),
        "authorization_is_readback_only_in_l15_2": payload.get("authorization_is_readback_only_in_l15_2"),
        "launch_execution_allowed": payload.get("launch_execution_allowed"),
        "browser_started": payload.get("browser_started"),
        "edge_process_started": payload.get("edge_process_started"),
        "selenium_imported_by_readback": payload.get("selenium_imported_by_readback"),
        "profile_directory_created": payload.get("profile_directory_created"),
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
