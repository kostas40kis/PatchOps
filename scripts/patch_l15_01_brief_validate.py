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
    # Last-resort fallback for the normal repository shape: scripts/<file>.py.
    return here.parents[1]


_REPO_ROOT_FOR_IMPORTS = _discover_repo_root()
if str(_REPO_ROOT_FOR_IMPORTS) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT_FOR_IMPORTS))

from patchops.llm_browser import live_adapter_edge_live_start_authorization_execution_gate as l15_01

TOKEN = "PATCHOPS_L15_EDGE_LIVE_START_AUTHORIZED"


def main() -> int:
    parser = argparse.ArgumentParser(description="Brief validation for L15.1 passive Edge live-start authorization gate")
    parser.add_argument("--repo-root", default=None)
    args = parser.parse_args()
    root = Path(args.repo_root).resolve() if args.repo_root else _REPO_ROOT_FOR_IMPORTS

    no_auth = l15_01.build_edge_live_start_authorization_execution_gate(root)
    authorized = l15_01.build_edge_live_start_authorization_execution_gate(root, allow_live_start=True, authorization_token=TOKEN)
    default_profile = l15_01.build_edge_live_start_authorization_execution_gate(
        root,
        allow_live_start=True,
        authorization_token=TOKEN,
        profile_relative_path="Microsoft/Edge/User Data/Default",
    )

    ok = (
        no_auth.get("ok") is True
        and no_auth.get("source_l14_09_final_marker_accepted") is True
        and no_auth.get("live_start_operator_authorization_complete") is False
        and no_auth.get("authorization_missing_keeps_execution_blocked") is True
        and no_auth.get("launch_execution_allowed") is False
        and no_auth.get("browser_started") is False
        and no_auth.get("edge_process_started") is False
        and no_auth.get("profile_directory_created") is False
        and authorized.get("ok") is True
        and authorized.get("live_start_operator_authorization_complete") is True
        and authorized.get("authorization_present_is_readback_only_in_l15_1") is True
        and authorized.get("launch_execution_allowed") is False
        and authorized.get("browser_started") is False
        and authorized.get("edge_process_started") is False
        and default_profile.get("ok") is False
        and default_profile.get("default_edge_profile_requested") is True
        and default_profile.get("default_profile_use_allowed") is False
        and default_profile.get("launch_execution_allowed") is False
    )

    payload = {
        "ok": ok,
        "patch": "L15.1",
        "repair": "L15.1b",
        "repo_root_for_imports": str(_REPO_ROOT_FOR_IMPORTS),
        "repo_root_used": str(root),
        "source_l14_09_final_marker_accepted": no_auth.get("source_l14_09_final_marker_accepted"),
        "no_auth_operator_authorized": no_auth.get("live_start_operator_authorization_complete"),
        "authorized_operator_authorized": authorized.get("live_start_operator_authorization_complete"),
        "authorized_readback_only": authorized.get("authorization_present_is_readback_only_in_l15_1"),
        "default_profile_requested_rejected": default_profile.get("default_edge_profile_requested") is True and default_profile.get("default_profile_use_allowed") is False,
        "launch_execution_allowed": authorized.get("launch_execution_allowed"),
        "browser_started": authorized.get("browser_started"),
        "edge_process_started": authorized.get("edge_process_started"),
        "profile_directory_created": authorized.get("profile_directory_created"),
        "selenium_imported_by_readback": authorized.get("selenium_imported_by_readback"),
        "auto_send_allowed": authorized.get("auto_send_allowed"),
        "next_patch": authorized.get("next_patch"),
        "missing_doc_phrases": no_auth.get("missing_doc_phrases"),
        "missing_commands": no_auth.get("missing_commands"),
        "required_repo_paths_ok": (no_auth.get("required_repo_paths") or {}).get("ok"),
    }
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
