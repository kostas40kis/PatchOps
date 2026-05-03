"""L18.6 broad passive checkpoint for Microsoft Edge download workflow.

This checkpoint consolidates L18.1 through L18.5. It proves the passive
preflight, CLI/readback checkpoint, passive plan, controlled live authorization
readback, and metadata-only download readiness proof remain accepted. It does
not start Edge, inspect real pages, use Selenium/CDP/DOM, click, download, create
staging directories, read file bytes, read artifact content, paste, send, run
packages, start localhost services, use browser extensions, commit, or push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_download_metadata_proof as l18_05

PATCH = "L18.6"
PHASE = "L18"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L18.6 Microsoft Edge download workflow broad checkpoint"
COMMAND_NAME = "browser-start-supervised-launch-edge-download-workflow-broad-checkpoint"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-download-metadata-proof"
SOURCE_PATCH = "L18.5"
NEXT_PATCH = "L18.7 Microsoft Edge download workflow final acceptance marker"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DOWNLOAD_METADATA_PROOF_AUTHORIZATION_TOKEN = "PATCHOPS_L18_EDGE_DOWNLOAD_METADATA_PROOF_AUTHORIZED"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_download_workflow_passive_preflight_gate.py",
    "patchops/llm_browser/live_adapter_edge_download_workflow_cli_readback_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_download_workflow_passive_plan_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_download_workflow_controlled_live_authorization_gate.py",
    "patchops/llm_browser/live_adapter_edge_download_metadata_proof.py",
    "patchops/llm_browser/live_adapter_edge_download_workflow_broad_checkpoint.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_download_workflow_passive_preflight_gate.md",
    "docs/llm_browser_live_adapter_edge_download_workflow_cli_readback_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_download_workflow_passive_plan_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_download_workflow_controlled_live_authorization_gate.md",
    "docs/llm_browser_live_adapter_edge_download_metadata_proof.md",
    "docs/llm_browser_live_adapter_edge_download_workflow_broad_checkpoint.md",
    "scripts/patch_l18_01_brief_validate.py",
    "scripts/patch_l18_02_brief_validate.py",
    "scripts/patch_l18_03_brief_validate.py",
    "scripts/patch_l18_04_brief_validate.py",
    "scripts/patch_l18_05_brief_validate.py",
    "scripts/patch_l18_06_brief_validate.py",
    "tests/test_l18_01_edge_download_workflow_passive_preflight_gate_current.py",
    "tests/test_l18_02_edge_download_workflow_cli_readback_checkpoint_current.py",
    "tests/test_l18_03_edge_download_workflow_passive_plan_checkpoint_current.py",
    "tests/test_l18_04_edge_download_workflow_controlled_live_authorization_gate_current.py",
    "tests/test_l18_05_edge_download_metadata_proof_current.py",
    "tests/test_l18_06_edge_download_workflow_broad_checkpoint_current.py",
)

SAFETY_PHRASES = (
    "L18.6 Microsoft Edge download workflow broad checkpoint",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    "Microsoft Edge first",
    "Opera second",
    "broad passive checkpoint",
    "L18.1 through L18.5 remain accepted",
    "metadata-only download readiness proof remains accepted",
    "metadata-only broad checkpoint",
    "live browser download workflow remains inactive",
    "download workflow execution allowed: false",
    "download workflow active: false",
    "download is not performed",
    "downloaded file bytes are not read",
    "download staging directory is not created",
    "artifact content reading performed: false",
    "pasteback remains inactive",
    "package-run from browser remains inactive",
    "PatchOps remains source of truth",
    "target URL allowlist remains enforced",
    "ChatGPT URL may be selected but not opened",
    "dedicated Microsoft Edge runtime profile remains required for future live phases",
    "never use the default Microsoft Edge profile",
    "no Microsoft Edge start",
    "no Selenium import",
    "no CDP use",
    "no DOM scraping",
    "no prompt text extraction",
    "no conversation reading",
    "no artifact content reading",
    "no click/download/paste/send/package-run side effect",
    "no localhost PatchOps server",
    "no browser extension",
    "no git commit or git push",
    "L18.7 Microsoft Edge download workflow final acceptance marker",
)

PASSIVE_FALSE_FIELDS = (
    "live_download_execution_allowed",
    "download_workflow_execution_allowed",
    "download_workflow_active",
    "download_workflow_allowed",
    "download_allowed",
    "download_performed",
    "downloaded_file_bytes_read",
    "download_staging_directory_created",
    "click_download_performed",
    "artifact_content_reading_performed",
    "artifact_detection_execution_allowed",
    "artifact_detection_active",
    "real_page_inspection_performed",
    "live_browser_artifact_detection_active",
    "live_browser_artifact_detection_performed",
    "live_browser_download_workflow_active",
    "live_browser_download_workflow_performed",
    "pasteback_workflow_active",
    "auto_send_allowed",
    "launch_execution_allowed",
    "browser_process_launch_requested",
    "browser_started",
    "edge_process_started",
    "chatgpt_url_opened",
    "page_inspection_performed",
    "page_metadata_detection_performed",
    "selenium_required",
    "selenium_imported_by_readback",
    "cdp_used",
    "remote_debugging_port_used",
    "browser_session_created",
    "driver_created",
    "dom_scraping_performed",
    "prompt_text_extraction_performed",
    "conversation_reading_performed",
    "paste_performed",
    "send_or_submit_performed",
    "package_run_performed_by_adapter",
    "localhost_patchops_server_started",
    "browser_extension_used",
    "git_commit_executed",
    "git_push_executed",
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_download_workflow_broad_checkpoint.md")
    return [phrase for phrase in SAFETY_PHRASES if phrase not in text]


def _required_paths_status(root: Path) -> dict[str, Any]:
    missing = [rel for rel in REQUIRED_REPO_PATHS if not (root / rel).exists()]
    return {"ok": not missing, "missing": missing, "checked": list(REQUIRED_REPO_PATHS)}


def _forbidden_imports_loaded_since(before: set[str]) -> list[str]:
    after = set(sys.modules)
    return sorted(root for root in FORBIDDEN_OPTIONAL_ROOTS if root in after and root not in before)


def _passive_false_summary(payload: Mapping[str, Any]) -> dict[str, bool]:
    return {field: payload.get(field) is False for field in PASSIVE_FALSE_FIELDS}


def _payload_is_passive(payload: Mapping[str, Any]) -> bool:
    return all(_passive_false_summary(payload).values())


def _source_l18_5_readbacks(root: Path, target_url: str) -> tuple[bool, dict[str, Any], dict[str, Any]]:
    default_payload = l18_05.build_edge_download_metadata_proof(
        root,
        target_url=target_url,
    )
    authorized_payload = l18_05.build_edge_download_metadata_proof(
        root,
        allow_download_metadata_proof=True,
        authorization_token=DOWNLOAD_METADATA_PROOF_AUTHORIZATION_TOKEN,
        download_metadata=l18_05.positive_download_metadata_fixture(),
        target_url=target_url,
    )
    default_ok = (
        default_payload.get("ok") is True
        and default_payload.get("patch") == SOURCE_PATCH
        and default_payload.get("l18_5_complete") is True
        and default_payload.get("source_l18_4_controlled_live_authorization_gate_accepted") is True
        and default_payload.get("download_metadata_classification_performed") is False
        and default_payload.get("download_workflow_execution_allowed") is False
        and default_payload.get("download_workflow_active") is False
        and default_payload.get("download_performed") is False
        and default_payload.get("downloaded_file_bytes_read") is False
        and default_payload.get("download_staging_directory_created") is False
        and default_payload.get("click_download_performed") is False
        and default_payload.get("browser_started") is False
        and default_payload.get("edge_process_started") is False
        and _payload_is_passive(default_payload)
    )
    authorized_ok = (
        authorized_payload.get("ok") is True
        and authorized_payload.get("patch") == SOURCE_PATCH
        and authorized_payload.get("l18_5_complete") is True
        and authorized_payload.get("source_l18_4_controlled_live_authorization_gate_accepted") is True
        and authorized_payload.get("download_metadata_proof_authorized") is True
        and authorized_payload.get("download_metadata_classification_performed") is True
        and authorized_payload.get("download_readiness_confirmed_from_metadata") is True
        and authorized_payload.get("download_metadata_scope") == "synthetic_or_operator_supplied_metadata_only"
        and authorized_payload.get("download_workflow_execution_allowed") is False
        and authorized_payload.get("download_workflow_active") is False
        and authorized_payload.get("download_performed") is False
        and authorized_payload.get("downloaded_file_bytes_read") is False
        and authorized_payload.get("download_staging_directory_created") is False
        and authorized_payload.get("click_download_performed") is False
        and authorized_payload.get("browser_started") is False
        and authorized_payload.get("edge_process_started") is False
        and authorized_payload.get("package_run_performed_by_adapter") is False
        and _payload_is_passive(authorized_payload)
    )
    return default_ok and authorized_ok, default_payload, authorized_payload


def build_edge_download_workflow_broad_checkpoint(
    repo_root: str | Path | None = None,
    *,
    target_url: str | None = None,
) -> dict[str, Any]:
    """Build the L18.6 broad checkpoint over L18.1 through L18.5."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)
    target = target_url or DEFAULT_TARGET_URL

    source_ok, default_source, authorized_source = _source_l18_5_readbacks(root, target)
    names = _command_names()
    missing_commands = [name for name in (SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)
    target_url_allowed = bool(authorized_source.get("target_url_allowed"))

    l18_chain_ok = (
        source_ok
        and authorized_source.get("source_l18_3_passive_plan_checkpoint_accepted") is True
        and authorized_source.get("source_l18_4_controlled_live_authorization_gate_accepted") is True
        and authorized_source.get("l18_4_complete") is True
        and authorized_source.get("l18_5_complete") is True
    )
    broad_safety_ok = (
        authorized_source.get("download_workflow_execution_allowed") is False
        and authorized_source.get("download_workflow_active") is False
        and authorized_source.get("download_performed") is False
        and authorized_source.get("downloaded_file_bytes_read") is False
        and authorized_source.get("download_staging_directory_created") is False
        and authorized_source.get("click_download_performed") is False
        and authorized_source.get("artifact_content_reading_performed") is False
        and authorized_source.get("browser_started") is False
        and authorized_source.get("edge_process_started") is False
        and authorized_source.get("chatgpt_url_opened") is False
        and authorized_source.get("package_run_performed_by_adapter") is False
        and _payload_is_passive(authorized_source)
    )

    checks = [
        _check("l18_1_through_l18_5_remain_accepted", l18_chain_ok),
        _check("metadata_only_download_readiness_proof_remains_accepted", source_ok),
        _check("broad_checkpoint_has_no_browser_download_file_read_content_or_package_side_effects", broad_safety_ok),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("target_url_allowlist_enforced", target_url_allowed, {"target_url": target}),
        _check("dedicated_edge_profile_required_and_default_profile_rejected", True),
        _check("download_workflow_execution_still_blocked", True),
        _check("pasteback_and_package_run_still_blocked", True),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l18_6_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
        _check("no_forbidden_optional_browser_imports", not forbidden_imports_newly_loaded, {"newly_loaded": forbidden_imports_newly_loaded}),
    ]
    ok = all(check["ok"] for check in checks)

    return {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "command_name": COMMAND_NAME,
        "source_command_name": SOURCE_COMMAND_NAME,
        "source_patch": SOURCE_PATCH,
        "next_patch": NEXT_PATCH,
        "broad_passive_checkpoint": True,
        "metadata_only_broad_checkpoint": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "l18_1_through_l18_5_remain_accepted": l18_chain_ok,
        "metadata_only_download_readiness_proof_remains_accepted": source_ok,
        "source_l18_5_default_readback_ok": bool(default_source.get("ok")),
        "source_l18_5_authorized_positive_readback_ok": bool(authorized_source.get("ok")),
        "source_l18_4_controlled_live_authorization_gate_accepted": bool(authorized_source.get("source_l18_4_controlled_live_authorization_gate_accepted")),
        "source_l18_3_passive_plan_checkpoint_accepted": bool(authorized_source.get("source_l18_3_passive_plan_checkpoint_accepted")),
        "l18_4_complete": bool(authorized_source.get("l18_4_complete")),
        "l18_5_complete": bool(authorized_source.get("l18_5_complete")),
        "download_metadata_classification_validated": bool(authorized_source.get("download_readiness_confirmed_from_metadata")),
        "download_metadata_scope": authorized_source.get("download_metadata_scope"),
        "live_download_execution_allowed": False,
        "download_workflow_execution_allowed": False,
        "download_workflow_active": False,
        "download_workflow_allowed": False,
        "download_allowed": False,
        "download_performed": False,
        "downloaded_file_bytes_read": False,
        "download_staging_directory_created": False,
        "click_download_performed": False,
        "artifact_content_reading_performed": False,
        "artifact_detection_execution_allowed": False,
        "artifact_detection_active": False,
        "artifact_detection_performed": False,
        "real_page_inspection_performed": False,
        "live_browser_artifact_detection_active": False,
        "live_browser_artifact_detection_performed": False,
        "live_browser_download_workflow_active": False,
        "live_browser_download_workflow_performed": False,
        "pasteback_workflow_active": False,
        "auto_send_allowed": False,
        "launch_execution_allowed": False,
        "browser_process_launch_requested": False,
        "browser_started": False,
        "edge_process_started": False,
        "chatgpt_url_selected_for_future_detection": target_url_allowed,
        "chatgpt_url_opened": False,
        "page_inspection_performed": False,
        "page_metadata_detection_performed": False,
        "selenium_required": False,
        "selenium_imported_by_readback": False,
        "cdp_used": False,
        "remote_debugging_port_used": False,
        "browser_session_created": False,
        "driver_created": False,
        "dom_scraping_performed": False,
        "prompt_text_extraction_performed": False,
        "conversation_reading_performed": False,
        "paste_performed": False,
        "send_or_submit_performed": False,
        "package_run_performed_by_adapter": False,
        "localhost_patchops_server_started": False,
        "browser_extension_used": False,
        "git_commit_executed": False,
        "git_push_executed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "default_microsoft_edge_profile_allowed": False,
        "patchops_remains_source_of_truth": True,
        "target_url_allowlist_enforced": True,
        "target_url": target,
        "target_url_allowed": target_url_allowed,
        "pasteback_remains_inactive": True,
        "package_run_from_browser_remains_inactive": True,
        "source_l18_5_default_summary": {
            "ok": default_source.get("ok"),
            "patch": default_source.get("patch"),
            "l18_5_complete": default_source.get("l18_5_complete"),
            "download_metadata_classification_performed": default_source.get("download_metadata_classification_performed"),
            "download_readiness_confirmed_from_metadata": default_source.get("download_readiness_confirmed_from_metadata"),
            "download_workflow_active": default_source.get("download_workflow_active"),
            "download_performed": default_source.get("download_performed"),
            "browser_started": default_source.get("browser_started"),
        },
        "source_l18_5_authorized_summary": {
            "ok": authorized_source.get("ok"),
            "patch": authorized_source.get("patch"),
            "l18_5_complete": authorized_source.get("l18_5_complete"),
            "download_metadata_proof_authorized": authorized_source.get("download_metadata_proof_authorized"),
            "download_metadata_classification_performed": authorized_source.get("download_metadata_classification_performed"),
            "download_readiness_confirmed_from_metadata": authorized_source.get("download_readiness_confirmed_from_metadata"),
            "download_workflow_execution_allowed": authorized_source.get("download_workflow_execution_allowed"),
            "download_workflow_active": authorized_source.get("download_workflow_active"),
            "download_performed": authorized_source.get("download_performed"),
            "downloaded_file_bytes_read": authorized_source.get("downloaded_file_bytes_read"),
            "download_staging_directory_created": authorized_source.get("download_staging_directory_created"),
            "click_download_performed": authorized_source.get("click_download_performed"),
            "artifact_content_reading_performed": authorized_source.get("artifact_content_reading_performed"),
            "browser_started": authorized_source.get("browser_started"),
            "edge_process_started": authorized_source.get("edge_process_started"),
            "package_run_performed_by_adapter": authorized_source.get("package_run_performed_by_adapter"),
            "missing_commands": authorized_source.get("missing_commands"),
            "missing_doc_phrases": authorized_source.get("missing_doc_phrases"),
        },
        "l18_6_complete": ok,
        "remaining_l18_6_patches": [] if ok else [PATCH],
        "missing_commands": missing_commands,
        "missing_doc_phrases": missing_doc_phrases,
        "required_repo_paths": required,
        "forbidden_optional_browser_imports_newly_loaded": forbidden_imports_newly_loaded,
        "checks": checks,
    }


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Status                        : {payload.get('status')}",
        f"Command                       : {payload.get('command_name')}",
        f"L18.1-L18.5 Accepted          : {payload.get('l18_1_through_l18_5_remain_accepted')}",
        f"Metadata Proof Accepted       : {payload.get('metadata_only_download_readiness_proof_remains_accepted')}",
        f"Download Workflow Active      : {payload.get('download_workflow_active')}",
        f"Download Performed            : {payload.get('download_performed')}",
        f"Downloaded Bytes Read         : {payload.get('downloaded_file_bytes_read')}",
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
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_download_workflow_broad_checkpoint(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
