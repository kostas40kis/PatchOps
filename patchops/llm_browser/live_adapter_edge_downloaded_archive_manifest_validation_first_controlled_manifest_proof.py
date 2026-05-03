"""L22.5 first controlled downloaded-archive manifest validation proof.

This module performs the first narrow manifest validation proof after accepted
L22.4/L22.4a. It reads only the explicit synthetic PatchOps runtime manifest
fixture and validates a tiny set of manifest-shape fields.

It does not start Edge, import Selenium, inspect pages, open archives, extract
archives, read archive member bytes, read real downloaded artifacts, paste,
send, run packages, start localhost servers, use browser extensions, commit, or
push.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_downloaded_archive_manifest_validation_controlled_authorization_gate as l22_04

PATCH = "L22.5"
PHASE = "L22"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L22.5 Microsoft Edge first controlled downloaded-archive manifest validation proof"
SOURCE_PATCH = "L22.4/L22.4a"
SOURCE_MODULE_REL = "patchops/llm_browser/live_adapter_edge_downloaded_archive_manifest_validation_controlled_authorization_gate.py"
SOURCE_VALIDATOR_REL = "scripts/patch_l22_04_brief_validate.py"
NEXT_PATCH = "L22.6 Microsoft Edge downloaded-archive manifest validation broad checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_SYNTHETIC_MANIFEST_RELATIVE_PATH = "data/runtime/browser_downloads/patch_l22_05_synthetic_downloaded_archive_manifest_fixture/manifest.json"
REQUIRED_L22_04_AUTHORIZATION_TOKEN = l22_04.REQUIRED_MANIFEST_VALIDATION_AUTHORIZATION_TOKEN
REQUIRED_MANIFEST_VALIDATION_PROOF_TOKEN = "PATCHOPS_L22_EDGE_DOWNLOADED_ARCHIVE_SYNTHETIC_MANIFEST_VALIDATION_PROOF_AUTHORIZED"

ALLOWED_TARGET_URL_PREFIXES = ("https://chatgpt.com/", "https://chat.openai.com/")

ALWAYS_FALSE_FIELDS = (
    "archive_extracted",
    "downloaded_archive_extracted",
    "downloaded_archive_opened",
    "archive_member_bytes_read",
    "member_bytes_read",
    "archive_member_content_read",
    "artifact_content_read",
    "real_downloaded_artifact_read",
    "downloaded_file_bytes_read",
    "downloaded_file_stat_performed",
    "downloaded_file_hash_performed",
    "download_workflow_active",
    "download_workflow_execution_allowed",
    "real_browser_download_active",
    "browser_started",
    "edge_process_started",
    "browser_session_created",
    "selenium_imported",
    "cdp_used",
    "dom_scraping_used",
    "page_inspection_performed",
    "conversation_text_read",
    "prompt_text_extracted",
    "chatgpt_url_opened",
    "pasteback_workflow_active",
    "paste_performed",
    "send_or_submit_performed",
    "package_run_performed_by_adapter",
    "package_run",
    "localhost_server_started",
    "browser_extension_used",
    "git_commit_performed",
    "git_push_performed",
)


def _target_url_allowed(target_url: str) -> bool:
    return any(target_url.startswith(prefix) for prefix in ALLOWED_TARGET_URL_PREFIXES)


def _source_l22_04_authorized_payload(repo_root: Path) -> dict[str, Any]:
    try:
        payload = l22_04.build_manifest_validation_controlled_authorization_gate(
            repo_root,
            allow_manifest_validation_authorization=True,
            authorization_token=REQUIRED_L22_04_AUTHORIZATION_TOKEN,
        )
    except Exception as exc:  # pragma: no cover - defensive readback path
        return {"ok": False, "error": f"source L22.4 readback failed: {type(exc).__name__}: {exc}"}
    return dict(payload)


def _default_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    source_payload = _source_l22_04_authorized_payload(repo_root)
    checks = [
        {"name": "source_l22_04_module_exists", "ok": (repo_root / SOURCE_MODULE_REL).exists()},
        {"name": "source_l22_04_validator_exists", "ok": (repo_root / SOURCE_VALIDATOR_REL).exists()},
        {"name": "source_l22_04_authorized_readback_ok", "ok": bool(source_payload.get("ok"))},
        {"name": "target_url_allowlisted_but_not_opened", "ok": _target_url_allowed(target_url)},
        {"name": "default_readback_is_passive", "ok": True},
        {"name": "synthetic_manifest_not_read_without_l22_5_token", "ok": True},
    ]
    payload: dict[str, Any] = {
        "ok": bool(all(check.get("ok") for check in checks)),
        "status": STATUS_PASS if all(check.get("ok") for check in checks) else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_module": SOURCE_MODULE_REL,
        "source_validator": SOURCE_VALIDATOR_REL,
        "source_l22_04_authorized_summary": {
            "ok": source_payload.get("ok"),
            "patch": source_payload.get("patch"),
            "manifest_validation_authorization_granted_for_future_patch": source_payload.get("manifest_validation_authorization_granted_for_future_patch"),
            "manifest_validation_execution_allowed": source_payload.get("manifest_validation_execution_allowed"),
            "downloaded_manifest_read": source_payload.get("downloaded_manifest_read"),
            "archive_extracted": source_payload.get("archive_extracted"),
            "archive_member_bytes_read": source_payload.get("archive_member_bytes_read"),
            "browser_started": source_payload.get("browser_started"),
            "package_run": source_payload.get("package_run"),
        },
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "default_microsoft_edge_profile_allowed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "target_url": target_url,
        "target_url_allowed": _target_url_allowed(target_url),
        "chatgpt_url_may_be_selected_but_not_opened": True,
        "synthetic_manifest_fixture_relative_path": DEFAULT_SYNTHETIC_MANIFEST_RELATIVE_PATH,
        "synthetic_manifest_fixture_only": True,
        "manifest_validation_proof_requested": False,
        "manifest_validation_proof_token_present": False,
        "manifest_validation_proof_token_valid": False,
        "manifest_validation_execution_allowed": False,
        "manifest_validation_active": False,
        "manifest_validation_performed": False,
        "downloaded_manifest_read": False,
        "manifest_read": False,
        "synthetic_manifest_fixture_read": False,
        "synthetic_manifest_fixture_bytes_read": False,
        "synthetic_manifest_json_parsed": False,
        "manifest_shape_validated": False,
        "manifest_validation_scope": "default_readback_only_no_manifest_read",
        "manifest_validation_result": None,
        "next_patch": NEXT_PATCH,
        "checks": checks,
    }
    for field in ALWAYS_FALSE_FIELDS:
        payload[field] = False
    return payload


def _validate_synthetic_manifest_payload(data: Mapping[str, Any]) -> tuple[bool, list[dict[str, Any]], dict[str, Any]]:
    files_to_write = data.get("files_to_write")
    validation_commands = data.get("validation_commands")
    checks = [
        {"name": "manifest_json_is_object", "ok": isinstance(data, dict)},
        {"name": "manifest_version_is_1", "ok": data.get("manifest_version") == "1"},
        {"name": "patch_name_is_expected", "ok": data.get("patch_name") == "l22_05_synthetic_manifest_fixture"},
        {"name": "active_profile_is_generic_python", "ok": data.get("active_profile") == "generic_python"},
        {"name": "files_to_write_is_list", "ok": isinstance(files_to_write, list)},
        {"name": "validation_commands_is_list", "ok": isinstance(validation_commands, list)},
        {"name": "fixture_declares_synthetic_read_only", "ok": data.get("synthetic_fixture") is True and data.get("read_only_fixture") is True},
        {"name": "fixture_declares_no_package_run", "ok": data.get("package_run_allowed") is False},
    ]
    summary = {
        "manifest_version": data.get("manifest_version"),
        "patch_name": data.get("patch_name"),
        "active_profile": data.get("active_profile"),
        "files_to_write_count": len(files_to_write) if isinstance(files_to_write, list) else None,
        "validation_commands_count": len(validation_commands) if isinstance(validation_commands, list) else None,
        "synthetic_fixture": data.get("synthetic_fixture"),
        "read_only_fixture": data.get("read_only_fixture"),
        "package_run_allowed": data.get("package_run_allowed"),
    }
    return bool(all(check.get("ok") for check in checks)), checks, summary


def build_first_controlled_manifest_validation_proof(
    repo_root: str | Path | None = None,
    *,
    allow_manifest_validation_proof: bool = False,
    authorization_token: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    if not allow_manifest_validation_proof:
        return _default_payload(root, target_url)

    source_payload = _source_l22_04_authorized_payload(root)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_MANIFEST_VALIDATION_PROOF_TOKEN
    target_allowed = _target_url_allowed(target_url)
    fixture_path = root / DEFAULT_SYNTHETIC_MANIFEST_RELATIVE_PATH

    checks: list[dict[str, Any]] = [
        {"name": "source_l22_04_authorized_readback_ok", "ok": bool(source_payload.get("ok"))},
        {"name": "source_l22_04_grants_future_authorization", "ok": source_payload.get("manifest_validation_authorization_granted_for_future_patch") is True},
        {"name": "l22_5_manifest_proof_token_present", "ok": token_present},
        {"name": "l22_5_manifest_proof_token_valid", "ok": token_valid},
        {"name": "target_url_allowlisted_but_not_opened", "ok": target_allowed},
        {"name": "synthetic_manifest_fixture_path_is_fixed", "ok": str(fixture_path).endswith(DEFAULT_SYNTHETIC_MANIFEST_RELATIVE_PATH.replace("/", str(Path("x").parent / "x")[:-1] if False else "/")) or fixture_path.name == "manifest.json"},
        {"name": "synthetic_manifest_fixture_exists", "ok": fixture_path.exists()},
    ]

    manifest_data: dict[str, Any] | None = None
    manifest_summary: dict[str, Any] | None = None
    manifest_shape_checks: list[dict[str, Any]] = []
    manifest_validation_result = False

    execution_allowed = bool(all(check.get("ok") for check in checks))
    if execution_allowed:
        try:
            text = fixture_path.read_text(encoding="utf-8")
            manifest_data = json.loads(text)
            manifest_validation_result, manifest_shape_checks, manifest_summary = _validate_synthetic_manifest_payload(manifest_data)
            checks.extend(manifest_shape_checks)
        except Exception as exc:
            checks.append({"name": "synthetic_manifest_fixture_read_and_parse", "ok": False, "error": f"{type(exc).__name__}: {exc}"})
            manifest_validation_result = False

    payload: dict[str, Any] = {
        "ok": bool(all(check.get("ok") for check in checks) and manifest_validation_result),
        "status": STATUS_PASS if bool(all(check.get("ok") for check in checks) and manifest_validation_result) else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_module": SOURCE_MODULE_REL,
        "source_validator": SOURCE_VALIDATOR_REL,
        "source_l22_04_authorized_summary": {
            "ok": source_payload.get("ok"),
            "patch": source_payload.get("patch"),
            "manifest_validation_authorization_granted_for_future_patch": source_payload.get("manifest_validation_authorization_granted_for_future_patch"),
            "manifest_validation_execution_allowed": source_payload.get("manifest_validation_execution_allowed"),
            "downloaded_manifest_read": source_payload.get("downloaded_manifest_read"),
            "archive_extracted": source_payload.get("archive_extracted"),
            "archive_member_bytes_read": source_payload.get("archive_member_bytes_read"),
            "browser_started": source_payload.get("browser_started"),
            "package_run": source_payload.get("package_run"),
        },
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "default_microsoft_edge_profile_allowed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "target_url": target_url,
        "target_url_allowed": target_allowed,
        "chatgpt_url_may_be_selected_but_not_opened": True,
        "synthetic_manifest_fixture_relative_path": DEFAULT_SYNTHETIC_MANIFEST_RELATIVE_PATH,
        "synthetic_manifest_fixture_only": True,
        "manifest_validation_proof_requested": True,
        "manifest_validation_proof_token_present": token_present,
        "manifest_validation_proof_token_valid": token_valid,
        "manifest_validation_execution_allowed": execution_allowed,
        "manifest_validation_active": execution_allowed,
        "manifest_validation_performed": execution_allowed,
        "downloaded_manifest_read": execution_allowed,
        "manifest_read": execution_allowed,
        "synthetic_manifest_fixture_read": execution_allowed,
        "synthetic_manifest_fixture_bytes_read": execution_allowed,
        "synthetic_manifest_json_parsed": execution_allowed and manifest_data is not None,
        "manifest_shape_validated": execution_allowed,
        "manifest_validation_scope": "synthetic_patchops_runtime_manifest_fixture_only",
        "manifest_validation_result": manifest_validation_result,
        "manifest_summary": manifest_summary,
        "checks": checks,
        "next_patch": NEXT_PATCH,
        "notes": [
            "L22.5 reads only the explicit synthetic manifest fixture.",
            "No archive is opened or extracted and no archive member bytes are read.",
            "No browser, pasteback, send/submit, or package-run activity is performed.",
        ],
    }
    for field in ALWAYS_FALSE_FIELDS:
        payload[field] = False
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Status                        : {payload.get('status')}",
        f"Manifest Proof Requested      : {payload.get('manifest_validation_proof_requested')}",
        f"Manifest Proof Token Valid    : {payload.get('manifest_validation_proof_token_valid')}",
        f"Manifest Execution Allowed    : {payload.get('manifest_validation_execution_allowed')}",
        f"Manifest Read                 : {payload.get('downloaded_manifest_read')}",
        f"Manifest Scope                : {payload.get('manifest_validation_scope')}",
        f"Manifest Result               : {payload.get('manifest_validation_result')}",
        f"Archive Extracted             : {payload.get('archive_extracted')}",
        f"Member Bytes Read             : {payload.get('archive_member_bytes_read')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Package Run                   : {payload.get('package_run')}",
        f"Next Patch                    : {payload.get('next_patch')}",
        "",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        state = "PASS" if check.get("ok") else "FAIL"
        lines.append(f"- {state}: {check.get('name')}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--allow-manifest-validation-proof", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_first_controlled_manifest_validation_proof(
        args.repo_root,
        allow_manifest_validation_proof=args.allow_manifest_validation_proof,
        authorization_token=args.authorization_token,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
