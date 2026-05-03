
"""L22.1e passive preflight marker for downloaded-archive manifest validation.

This module intentionally avoids commands.py registration and older L-stream imports.
It is readback-only: no manifest read, no archive extraction, no member-byte read,
no browser activity, no pasteback, and no package-run.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

PATCH = "L22.1e"
PHASE = "L22"
NAME = "L22.1e Microsoft Edge downloaded-archive manifest validation passive preflight apply-bypass marker"
AUTH_TOKEN = "PATCHOPS_L22_EDGE_DOWNLOADED_ARCHIVE_MANIFEST_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY"
NEXT_PATCH = "L22.2 Microsoft Edge downloaded-archive manifest validation CLI/readback checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"

FALSE_FIELDS = (
    "manifest_validation_execution_allowed",
    "manifest_validation_active",
    "manifest_validation_performed",
    "downloaded_manifest_read",
    "downloaded_archive_opened",
    "downloaded_archive_contents_listed",
    "downloaded_archive_extracted",
    "downloaded_archive_member_bytes_read",
    "downloaded_file_bytes_read",
    "downloaded_file_stat_performed",
    "downloaded_file_hash_performed",
    "browser_started",
    "edge_process_started",
    "chatgpt_url_opened",
    "download_performed",
    "paste_performed",
    "send_or_submit_performed",
    "package_run_performed_by_adapter",
    "localhost_patchops_server_started",
    "browser_extension_used",
    "git_commit_executed",
    "git_push_executed",
)


def _target_url_allowed(url: str) -> bool:
    return url in {"https://chatgpt.com/", "https://chat.openai.com/"}


def build_manifest_validation_passive_preflight_apply_bypass(
    repo_root: str | Path | None = None,
    *,
    allow_manifest_validation_preflight: bool = False,
    authorization_token: str | None = None,
    target_url: str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    target = target_url or DEFAULT_TARGET_URL
    requested = bool(allow_manifest_validation_preflight)
    token_present = authorization_token == AUTH_TOKEN
    authorized = requested and token_present
    target_allowed = _target_url_allowed(target)
    checked = [
        "patchops/llm_browser/live_adapter_edge_downloaded_archive_manifest_validation_passive_preflight_apply_bypass.py",
        "docs/llm_browser_live_adapter_edge_downloaded_archive_manifest_validation_passive_preflight_apply_bypass.md",
        "scripts/patch_l22_01e_brief_validate.py",
    ]
    missing = [rel for rel in checked if not (root / rel).exists()]
    payload: dict[str, Any] = {
        "ok": target_allowed and not missing,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "next_patch": NEXT_PATCH,
        "l22_1e_minimal_apply_bypass_marker": True,
        "manifest_validation_passive_preflight_gate": True,
        "manifest_validation_preflight_requested": requested,
        "manifest_validation_preflight_authorization_token_present": token_present,
        "manifest_validation_preflight_authorized": authorized,
        "manifest_validation_preflight_authorization_is_readback_only": True,
        "target_url": target,
        "target_url_allowed": target_allowed,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "default_microsoft_edge_profile_allowed": False,
        "no_old_l_stream_imports": True,
        "no_commands_py_registration": True,
        "required_repo_paths": {"ok": not missing, "checked": checked, "missing": missing},
        "safety_boundary": "readback-only manifest preflight; no manifest read, archive extraction, member-byte read, browser activity, pasteback, or package-run",
    }
    for field in FALSE_FIELDS:
        payload[field] = False
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--allow-manifest-validation-preflight", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_manifest_validation_passive_preflight_apply_bypass(
        args.repo_root,
        allow_manifest_validation_preflight=args.allow_manifest_validation_preflight,
        authorization_token=args.authorization_token,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
