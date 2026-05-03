
"""L22.2 apply-bypass CLI/readback checkpoint for archive manifest validation.

This module deliberately avoids commands.py registration and uses direct module
readback against the accepted L22.1e apply-bypass marker. It is readback-only:
no manifest read, no archive extraction, no archive member-byte read, no browser
activity, no pasteback, and no package-run.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH = "L22.2"
PHASE = "L22"
NAME = "L22.2 Microsoft Edge downloaded-archive manifest validation CLI/readback checkpoint apply-bypass"
SOURCE_PATCH = "L22.1e"
SOURCE_MODULE_REL = "patchops/llm_browser/live_adapter_edge_downloaded_archive_manifest_validation_passive_preflight_apply_bypass.py"
AUTH_TOKEN = "PATCHOPS_L22_EDGE_DOWNLOADED_ARCHIVE_MANIFEST_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY"
NEXT_PATCH = "L22.3 Microsoft Edge downloaded-archive manifest validation passive plan checkpoint"
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


def _load_source_module(repo_root: Path):
    path = repo_root / SOURCE_MODULE_REL
    spec = importlib.util.spec_from_file_location("l22_01e_manifest_source", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load source module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "ok": payload.get("ok"),
        "patch": payload.get("patch"),
        "manifest_validation_preflight_authorized": payload.get("manifest_validation_preflight_authorized"),
        "manifest_validation_preflight_authorization_is_readback_only": payload.get("manifest_validation_preflight_authorization_is_readback_only"),
        "downloaded_manifest_read": payload.get("downloaded_manifest_read"),
        "downloaded_archive_extracted": payload.get("downloaded_archive_extracted"),
        "downloaded_archive_member_bytes_read": payload.get("downloaded_archive_member_bytes_read"),
        "browser_started": payload.get("browser_started"),
        "package_run_performed_by_adapter": payload.get("package_run_performed_by_adapter"),
        "next_patch": payload.get("next_patch"),
    }


def _all_false(payload: Mapping[str, Any]) -> bool:
    return all(payload.get(field) is False for field in FALSE_FIELDS)


def _target_url_allowed(url: str) -> bool:
    return url in {"https://chatgpt.com/", "https://chat.openai.com/"}


def build_manifest_validation_cli_readback_apply_bypass(
    repo_root: str | Path | None = None,
    *,
    target_url: str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    target = target_url or DEFAULT_TARGET_URL
    target_allowed = _target_url_allowed(target)
    missing = []
    if not (root / SOURCE_MODULE_REL).exists():
        missing.append(SOURCE_MODULE_REL)

    default_payload: dict[str, Any] = {}
    authorized_payload: dict[str, Any] = {}
    source_load_ok = not missing
    source_error = ""
    if source_load_ok:
        try:
            source = _load_source_module(root)
            default_payload = source.build_manifest_validation_passive_preflight_apply_bypass(root, target_url=target)
            authorized_payload = source.build_manifest_validation_passive_preflight_apply_bypass(
                root,
                allow_manifest_validation_preflight=True,
                authorization_token=AUTH_TOKEN,
                target_url=target,
            )
        except Exception as exc:  # pragma: no cover - surfaced in payload
            source_load_ok = False
            source_error = f"{type(exc).__name__}: {exc}"

    default_ok = (
        bool(default_payload)
        and default_payload.get("ok") is True
        and default_payload.get("patch") == SOURCE_PATCH
        and default_payload.get("manifest_validation_preflight_authorized") is False
        and _all_false(default_payload)
    )
    authorized_ok = (
        bool(authorized_payload)
        and authorized_payload.get("ok") is True
        and authorized_payload.get("patch") == SOURCE_PATCH
        and authorized_payload.get("manifest_validation_preflight_authorized") is True
        and authorized_payload.get("manifest_validation_preflight_authorization_is_readback_only") is True
        and _all_false(authorized_payload)
    )
    ok = target_allowed and source_load_ok and default_ok and authorized_ok

    payload: dict[str, Any] = {
        "ok": ok,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "next_patch": NEXT_PATCH,
        "l22_2_apply_bypass_cli_readback_checkpoint": True,
        "l22_1e_marker_accepted": default_ok and authorized_ok,
        "source_module_present": not missing,
        "source_load_ok": source_load_ok,
        "source_error": source_error,
        "default_manifest_preflight_readback_ok": default_ok,
        "authorized_manifest_preflight_readback_ok": authorized_ok,
        "default_manifest_validation_preflight_authorized": default_payload.get("manifest_validation_preflight_authorized"),
        "authorized_manifest_validation_preflight_authorized": authorized_payload.get("manifest_validation_preflight_authorized"),
        "manifest_validation_preflight_authorization_remains_readback_only": True,
        "target_url": target,
        "target_url_allowed": target_allowed,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "default_microsoft_edge_profile_allowed": False,
        "no_commands_py_registration": True,
        "apply_bypass_style_preserved": True,
        "zero_patchops_validation_commands_expected": True,
        "safety_boundary": "readback-only manifest CLI/readback checkpoint; no manifest read, archive extraction, member-byte read, browser activity, pasteback, or package-run",
        "required_repo_paths": {"ok": not missing, "checked": [SOURCE_MODULE_REL], "missing": missing},
        "source_default_summary": _summary(default_payload),
        "source_authorized_summary": _summary(authorized_payload),
    }
    for field in FALSE_FIELDS:
        payload[field] = False
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_manifest_validation_cli_readback_apply_bypass(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
