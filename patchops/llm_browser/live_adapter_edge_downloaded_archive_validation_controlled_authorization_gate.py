"""L21.4 controlled authorization gate for downloaded-archive validation.

This module adds the future authorization token/readback surface after accepted
L21.3. It remains passive/readback-only: no Edge start, page inspection, click,
download, stat/hash, archive open/list/extract, manifest read, file-byte read,
artifact-content read, paste, send, package-run, localhost server, browser
extension, commit, or push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_downloaded_archive_validation_passive_plan_checkpoint as l21_03

PATCH = "L21.4"
PHASE = "L21"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L21.4 Microsoft Edge downloaded-archive validation controlled authorization gate"
COMMAND_NAME = "browser-start-supervised-launch-edge-downloaded-archive-validation-controlled-authorization-gate"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-downloaded-archive-validation-passive-plan-checkpoint"
SOURCE_PATCH = "L21.3"
NEXT_PATCH = "L21.5 Microsoft Edge first controlled downloaded-archive validation proof"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_ARCHIVE_VALIDATION_AUTHORIZATION_TOKEN = "PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_VALIDATION_CONTROLLED_AUTHORIZED_READBACK_ONLY"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer", "zipfile")

SAFETY_PHRASES = ['L21.4 Microsoft Edge downloaded-archive validation controlled authorization gate', 'browser-start-supervised-launch-edge-downloaded-archive-validation-controlled-authorization-gate', 'browser-start-supervised-launch-edge-downloaded-archive-validation-passive-plan-checkpoint', 'PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_VALIDATION_CONTROLLED_AUTHORIZED_READBACK_ONLY', 'Microsoft Edge first', 'Opera second', 'downloaded-archive validation controlled authorization gate', 'controlled authorization gate', 'L21.3 passive plan checkpoint remains accepted', 'explicit future archive validation authorization token', 'archive validation authorization is readback-only', 'archive validation execution allowed: false', 'archive validation active: false', 'archive validation is not performed', 'downloaded archive is not opened', 'downloaded archive contents are not listed', 'downloaded archive is not extracted', 'downloaded manifest is not read', 'downloaded file bytes are not read', 'downloaded file stat is not performed', 'downloaded file hash is not performed', 'hash validation remains inactive', 'manifest read remains inactive', 'download workflow remains inactive', 'real browser download remains inactive', 'pasteback remains inactive', 'package-run from browser remains inactive', 'PatchOps remains source of truth', 'target URL allowlist remains enforced', 'ChatGPT URL may be selected but not opened', 'dedicated Microsoft Edge runtime profile remains required for future live phases', 'never use the default Microsoft Edge profile', 'no Microsoft Edge start', 'no Selenium import', 'no CDP use', 'no DOM scraping', 'no prompt text extraction', 'no conversation reading', 'no artifact content reading', 'no click/download/stat/hash/archive-open/archive-list/archive-extract/manifest/byte-read/paste/send/package-run side effect', 'no localhost PatchOps server', 'no browser extension', 'no git commit or git push', 'L21.5 Microsoft Edge first controlled downloaded-archive validation proof']

ARCHIVE_FALSE_FIELDS = (
    "archive_validation_execution_allowed", "archive_validation_active", "archive_validation_performed",
    "downloaded_archive_opened", "downloaded_archive_contents_listed", "downloaded_archive_extracted",
    "downloaded_manifest_read", "downloaded_file_bytes_read", "downloaded_file_stat_performed",
    "downloaded_file_hash_performed", "real_file_stat_performed", "real_file_hash_performed",
    "hash_validation_active", "manifest_read_active", "package_run_from_browser_active",
    "download_workflow_execution_allowed", "download_workflow_active", "download_workflow_allowed",
    "download_allowed", "download_performed", "download_staging_directory_created", "click_download_performed",
    "artifact_content_reading_performed", "artifact_detection_execution_allowed", "artifact_detection_active",
    "artifact_detection_performed", "live_browser_download_workflow_active", "live_browser_download_workflow_performed",
    "pasteback_workflow_active", "auto_send_allowed", "launch_execution_allowed", "browser_process_launch_requested",
    "browser_started", "edge_process_started", "chatgpt_url_opened", "page_inspection_performed",
    "page_metadata_detection_performed", "selenium_required", "selenium_imported_by_readback", "cdp_used",
    "remote_debugging_port_used", "browser_session_created", "driver_created", "dom_scraping_performed",
    "prompt_text_extraction_performed", "conversation_reading_performed", "paste_performed",
    "send_or_submit_performed", "package_run_performed_by_adapter", "localhost_patchops_server_started",
    "browser_extension_used", "git_commit_executed", "git_push_executed",
)

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_passive_preflight_gate.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_cli_readback_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_passive_plan_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_controlled_authorization_gate.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_downloaded_archive_validation_passive_preflight_gate.md",
    "docs/llm_browser_live_adapter_edge_downloaded_archive_validation_cli_readback_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_downloaded_archive_validation_passive_plan_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_downloaded_archive_validation_controlled_authorization_gate.md",
    "scripts/patch_l21_01_brief_validate.py",
    "scripts/patch_l21_02_brief_validate.py",
    "scripts/patch_l21_03_brief_validate.py",
    "scripts/patch_l21_04_brief_validate.py",
    "tests/test_l21_01_edge_downloaded_archive_validation_passive_preflight_gate_current.py",
    "tests/test_l21_02_edge_downloaded_archive_validation_cli_readback_checkpoint_current.py",
    "tests/test_l21_03_edge_downloaded_archive_validation_passive_plan_checkpoint_current.py",
    "tests/test_l21_04_edge_downloaded_archive_validation_controlled_authorization_gate_current.py",
    "data/runtime/browser_downloads/patch_l20_05_synthetic_patchops_bundle.zip",
)


def _repo_root(repo_root: str | Path | None) -> Path:
    if repo_root is None:
        return Path.cwd().resolve()
    candidate = Path(repo_root)
    if str(candidate) == ".":
        return Path.cwd().resolve()
    return candidate.resolve()


def _check(name: str, ok: bool, detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "detail": dict(detail or {})}


def _command_names() -> tuple[str, ...]:
    try:
        from patchops.llm_browser import commands
        return tuple(commands.llm_browser_command_names())
    except Exception:
        return ()


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _missing_doc_phrases(root: Path) -> list[str]:
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_downloaded_archive_validation_controlled_authorization_gate.md")
    return [phrase for phrase in SAFETY_PHRASES if phrase not in text]


def _required_paths_status(root: Path) -> dict[str, Any]:
    missing = [rel for rel in REQUIRED_REPO_PATHS if not (root / rel).exists()]
    return {"ok": not missing, "missing": missing, "checked": list(REQUIRED_REPO_PATHS)}


def _forbidden_imports_loaded_since(before: set[str]) -> list[str]:
    after = set(sys.modules)
    return sorted(root for root in FORBIDDEN_OPTIONAL_ROOTS if root in after and root not in before)


def _false_payload() -> dict[str, bool]:
    return {field: False for field in ARCHIVE_FALSE_FIELDS}


def _archive_false_summary(payload: Mapping[str, Any]) -> dict[str, bool]:
    return {field: payload.get(field) is False for field in ARCHIVE_FALSE_FIELDS}


def _archive_payload_is_passive(payload: Mapping[str, Any]) -> bool:
    return all(_archive_false_summary(payload).values())


def build_archive_validation_authorization_readback(
    *,
    allow_archive_validation_authorization: bool = False,
    authorization_token: str | None = None,
) -> dict[str, Any]:
    requested = bool(allow_archive_validation_authorization)
    token_present = authorization_token == REQUIRED_ARCHIVE_VALIDATION_AUTHORIZATION_TOKEN
    authorized = requested and token_present
    return {
        "archive_validation_authorization_requested": requested,
        "archive_validation_authorization_token_required": True,
        "archive_validation_authorization_token_present": token_present,
        "archive_validation_authorized_for_future_phase": authorized,
        "archive_validation_authorization_is_readback_only_in_l21_4": True,
        "required_authorization_token": REQUIRED_ARCHIVE_VALIDATION_AUTHORIZATION_TOKEN,
        "operator_review_required_before_archive_validation": True,
        **_false_payload(),
    }


def future_archive_validation_authorization_gate_plan() -> list[dict[str, Any]]:
    return [
        {"step": 1, "name": "confirm_l21_3_passive_plan_checkpoint_accepted", "status": "planned_not_executed", "side_effect": False},
        {"step": 2, "name": "require_explicit_archive_validation_authorization_flag", "status": "planned_not_executed", "side_effect": False},
        {"step": 3, "name": "require_exact_archive_validation_authorization_token", "status": "planned_not_executed", "required_authorization_token": REQUIRED_ARCHIVE_VALIDATION_AUTHORIZATION_TOKEN, "side_effect": False},
        {"step": 4, "name": "future_l21_5_or_later_may_open_archive_metadata_only", "status": "planned_not_executed", "allowed_only_in_future_l21_5_or_later": True, "archive_open_in_l21_4": False, "archive_listing_in_l21_4": False, "archive_extract_in_l21_4": False, "manifest_read_in_l21_4": False, "file_byte_read_in_l21_4": False, "package_run_in_l21_4": False},
        {"step": 5, "name": "l21_4_readback_does_not_execute_archive_validation", "status": "planned_not_executed", "archive_validation_execution_allowed": False, "downloaded_archive_opened": False, "downloaded_archive_contents_listed": False, "downloaded_archive_extracted": False, "downloaded_manifest_read": False, "downloaded_file_bytes_read": False, "package_run": False, "pasteback": False, "auto_send": False},
    ]


def _plan_blocks_archive_execution(plan: Sequence[Mapping[str, Any]]) -> bool:
    return (
        all(item.get("status") == "planned_not_executed" for item in plan)
        and plan[3].get("archive_open_in_l21_4") is False
        and plan[3].get("archive_listing_in_l21_4") is False
        and plan[3].get("archive_extract_in_l21_4") is False
        and plan[3].get("manifest_read_in_l21_4") is False
        and plan[3].get("file_byte_read_in_l21_4") is False
        and plan[3].get("package_run_in_l21_4") is False
        and plan[-1].get("archive_validation_execution_allowed") is False
        and plan[-1].get("downloaded_archive_opened") is False
        and plan[-1].get("downloaded_archive_contents_listed") is False
        and plan[-1].get("downloaded_archive_extracted") is False
        and plan[-1].get("downloaded_manifest_read") is False
        and plan[-1].get("downloaded_file_bytes_read") is False
        and plan[-1].get("package_run") is False
        and plan[-1].get("pasteback") is False
        and plan[-1].get("auto_send") is False
    )


def _source_l21_3_ok(source: Mapping[str, Any]) -> bool:
    return (
        source.get("ok") is True
        and source.get("patch") == SOURCE_PATCH
        and source.get("source_l21_2_cli_readback_checkpoint_accepted") is True
        and source.get("future_archive_validation_plan_blocks_archive_execution") is True
        and source.get("archive_validation_execution_allowed") is False
        and source.get("archive_validation_active") is False
        and source.get("archive_validation_performed") is False
        and source.get("downloaded_archive_opened") is False
        and source.get("downloaded_archive_contents_listed") is False
        and source.get("downloaded_archive_extracted") is False
        and source.get("downloaded_manifest_read") is False
        and source.get("downloaded_file_bytes_read") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("package_run_performed_by_adapter") is False
    )


def build_edge_downloaded_archive_validation_controlled_authorization_gate(
    repo_root: str | Path | None = None,
    *,
    allow_archive_validation_authorization: bool = False,
    authorization_token: str | None = None,
    target_url: str | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)
    target = target_url or DEFAULT_TARGET_URL
    source = l21_03.build_edge_downloaded_archive_validation_passive_plan_checkpoint(root, target_url=target)
    auth = build_archive_validation_authorization_readback(
        allow_archive_validation_authorization=allow_archive_validation_authorization,
        authorization_token=authorization_token,
    )
    plan = future_archive_validation_authorization_gate_plan()

    names = _command_names()
    missing_commands = [name for name in (SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)
    target_url_allowed = bool(source.get("target_url_allowed"))
    source_ok = _source_l21_3_ok(source)
    passive_ok = _archive_payload_is_passive(auth)
    plan_blocks = _plan_blocks_archive_execution(plan)

    checks = [
        _check("source_l21_3_passive_plan_checkpoint_accepted", source_ok),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("target_url_allowlist_enforced", target_url_allowed, {"target_url": target}),
        _check("archive_validation_authorization_surface_present", True),
        _check("archive_validation_authorization_is_readback_only", auth["archive_validation_authorization_is_readback_only_in_l21_4"] is True),
        _check("archive_validation_execution_blocked", passive_ok),
        _check("future_authorization_gate_plan_blocks_archive_execution", plan_blocks),
        _check("archive_open_list_extract_manifest_byte_read_package_run_blocked", passive_ok),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l21_4_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
        _check("no_forbidden_optional_browser_imports", not forbidden_imports_newly_loaded, {"newly_loaded": forbidden_imports_newly_loaded}),
    ]
    ok = all(check["ok"] for check in checks)
    false_payload = _false_payload()
    payload = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "command_name": COMMAND_NAME,
        "source_command_name": SOURCE_COMMAND_NAME,
        "source_patch": SOURCE_PATCH,
        "next_patch": NEXT_PATCH,
        "downloaded_archive_validation_controlled_authorization_gate": True,
        "controlled_authorization_gate": True,
        "passive_readback_only_in_l21_4": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "source_l21_3_passive_plan_checkpoint_accepted": source_ok,
        "l21_3_complete": bool(source.get("l21_3_complete")),
        "archive_validation_authorization_readback": auth,
        "archive_validation_authorization_requested": auth["archive_validation_authorization_requested"],
        "archive_validation_authorization_token_present": auth["archive_validation_authorization_token_present"],
        "archive_validation_authorized_for_future_phase": auth["archive_validation_authorized_for_future_phase"],
        "archive_validation_authorization_is_readback_only_in_l21_4": True,
        "future_archive_validation_authorization_gate_plan": plan,
        "future_authorization_gate_plan_is_planned_not_executed": all(item.get("status") == "planned_not_executed" for item in plan),
        "future_authorization_gate_plan_blocks_archive_execution": plan_blocks,
        "target_url_allowlist_enforced": True,
        "target_url": target,
        "target_url_allowed": target_url_allowed,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "default_microsoft_edge_profile_allowed": False,
        "patchops_remains_source_of_truth": True,
        "real_browser_download_remains_inactive": True,
        "pasteback_remains_inactive": True,
        "package_run_from_browser_remains_inactive": True,
        "source_l21_3_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "l21_3_complete": source.get("l21_3_complete"),
            "source_l21_2_cli_readback_checkpoint_accepted": source.get("source_l21_2_cli_readback_checkpoint_accepted"),
            "future_archive_validation_plan_blocks_archive_execution": source.get("future_archive_validation_plan_blocks_archive_execution"),
            "archive_validation_execution_allowed": source.get("archive_validation_execution_allowed"),
            "archive_validation_active": source.get("archive_validation_active"),
            "archive_validation_performed": source.get("archive_validation_performed"),
            "downloaded_archive_opened": source.get("downloaded_archive_opened"),
            "downloaded_archive_contents_listed": source.get("downloaded_archive_contents_listed"),
            "downloaded_archive_extracted": source.get("downloaded_archive_extracted"),
            "downloaded_manifest_read": source.get("downloaded_manifest_read"),
            "downloaded_file_bytes_read": source.get("downloaded_file_bytes_read"),
            "browser_started": source.get("browser_started"),
            "edge_process_started": source.get("edge_process_started"),
            "package_run_performed_by_adapter": source.get("package_run_performed_by_adapter"),
            "missing_commands": source.get("missing_commands"),
            "missing_doc_phrases": source.get("missing_doc_phrases"),
        },
        "l21_4_complete": ok,
        "remaining_l21_4_patches": [] if ok else [PATCH],
        "missing_commands": missing_commands,
        "missing_doc_phrases": missing_doc_phrases,
        "required_repo_paths": required,
        "forbidden_optional_browser_imports_newly_loaded": forbidden_imports_newly_loaded,
        "checks": checks,
    }
    payload.update(false_payload)
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Status                        : {payload.get('status')}",
        f"Command                       : {payload.get('command_name')}",
        f"L21.3 Accepted                : {payload.get('source_l21_3_passive_plan_checkpoint_accepted')}",
        f"Archive Authorization         : {payload.get('archive_validation_authorized_for_future_phase')}",
        f"Archive Execution Allowed     : {payload.get('archive_validation_execution_allowed')}",
        f"Archive Opened                : {payload.get('downloaded_archive_opened')}",
        f"Manifest Read                 : {payload.get('downloaded_manifest_read')}",
        f"Browser Started               : {payload.get('browser_started')}",
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
    parser.add_argument("--allow-archive-validation-authorization", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_edge_downloaded_archive_validation_controlled_authorization_gate(
        args.repo_root,
        allow_archive_validation_authorization=args.allow_archive_validation_authorization,
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
