"""L21.6 broad checkpoint for downloaded-archive validation.

This broad checkpoint consolidates L21.1 through L21.5. It proves the passive
preflight, CLI/readback checkpoint, passive plan, controlled authorization gate,
and first controlled archive metadata-only proof remain accepted. The only
archive operation allowed by this stream so far is opening/listing metadata for
the synthetic PatchOps runtime archive fixture. It does not extract archive
members, read manifests, read archive member bytes, run packages, start Edge,
inspect pages, click, download, paste, send, start localhost services, use
browser extensions, commit, or push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_downloaded_archive_validation_metadata_proof as l21_05

PATCH = "L21.6"
PHASE = "L21"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L21.6 Microsoft Edge downloaded-archive validation broad checkpoint"
COMMAND_NAME = "browser-start-supervised-launch-edge-downloaded-archive-validation-broad-checkpoint"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-downloaded-archive-validation-metadata-proof"
SOURCE_PATCH = "L21.5"
NEXT_PATCH = "L21.7 Microsoft Edge downloaded-archive validation final acceptance marker"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_ARCHIVE_METADATA_PROOF_AUTHORIZATION_TOKEN = "PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_METADATA_PROOF_AUTHORIZED"
DEFAULT_CANDIDATE_RELATIVE_PATH = "data/runtime/browser_downloads/patch_l21_05_synthetic_archive_patchops_bundle.zip"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_passive_preflight_gate.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_cli_readback_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_passive_plan_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_controlled_authorization_gate.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_metadata_proof.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_broad_checkpoint.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_downloaded_archive_validation_passive_preflight_gate.md",
    "docs/llm_browser_live_adapter_edge_downloaded_archive_validation_cli_readback_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_downloaded_archive_validation_passive_plan_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_downloaded_archive_validation_controlled_authorization_gate.md",
    "docs/llm_browser_live_adapter_edge_downloaded_archive_validation_metadata_proof.md",
    "docs/llm_browser_live_adapter_edge_downloaded_archive_validation_broad_checkpoint.md",
    "scripts/patch_l21_01_brief_validate.py",
    "scripts/patch_l21_02_brief_validate.py",
    "scripts/patch_l21_03_brief_validate.py",
    "scripts/patch_l21_04_brief_validate.py",
    "scripts/patch_l21_05_brief_validate.py",
    "scripts/patch_l21_06_brief_validate.py",
    "tests/test_l21_01_edge_downloaded_archive_validation_passive_preflight_gate_current.py",
    "tests/test_l21_02_edge_downloaded_archive_validation_cli_readback_checkpoint_current.py",
    "tests/test_l21_03_edge_downloaded_archive_validation_passive_plan_checkpoint_current.py",
    "tests/test_l21_04_edge_downloaded_archive_validation_controlled_authorization_gate_current.py",
    "tests/test_l21_05_edge_downloaded_archive_validation_metadata_proof_current.py",
    "tests/test_l21_06_edge_downloaded_archive_validation_broad_checkpoint_current.py",
    DEFAULT_CANDIDATE_RELATIVE_PATH,
)

SAFETY_PHRASES = (
    "L21.6 Microsoft Edge downloaded-archive validation broad checkpoint",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    REQUIRED_ARCHIVE_METADATA_PROOF_AUTHORIZATION_TOKEN,
    "Microsoft Edge first",
    "Opera second",
    "downloaded-archive validation broad checkpoint",
    "broad archive validation checkpoint",
    "L21.1 through L21.5 remain accepted",
    "archive metadata-only validation proof remains accepted",
    "default archive metadata proof readback remains passive",
    "authorized archive metadata proof readback remains metadata-only",
    "unsafe archive candidate remains rejected without archive access",
    "only the synthetic PatchOps runtime archive metadata listing is allowed",
    "downloaded archive may be opened only for metadata listing of the synthetic fixture",
    "downloaded archive contents may be listed as metadata only",
    "downloaded archive is not extracted",
    "downloaded manifest is not read",
    "archive member bytes are not read",
    "downloaded file bytes are not read",
    "downloaded file stat is not performed",
    "downloaded file hash is not performed",
    "package-run from browser remains inactive",
    "pasteback remains inactive",
    "download workflow remains inactive",
    "real browser download remains inactive",
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
    "no click/download/stat/hash/archive-extract/manifest-read/member-byte-read/paste/send/package-run side effect",
    "no localhost PatchOps server",
    "no browser extension",
    "no git commit or git push",
    "L21.7 Microsoft Edge downloaded-archive validation final acceptance marker",
)

ALWAYS_FALSE_FIELDS = (
    "downloaded_archive_extracted",
    "downloaded_manifest_read",
    "archive_member_bytes_read",
    "downloaded_file_bytes_read",
    "downloaded_file_stat_performed",
    "downloaded_file_hash_performed",
    "real_file_stat_performed",
    "real_file_hash_performed",
    "hash_validation_active",
    "manifest_read_active",
    "package_run_from_browser_active",
    "download_workflow_execution_allowed",
    "download_workflow_active",
    "download_workflow_allowed",
    "download_allowed",
    "download_performed",
    "download_staging_directory_created",
    "click_download_performed",
    "artifact_content_reading_performed",
    "artifact_detection_execution_allowed",
    "artifact_detection_active",
    "artifact_detection_performed",
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_downloaded_archive_validation_broad_checkpoint.md")
    return [phrase for phrase in SAFETY_PHRASES if phrase not in text]


def _required_paths_status(root: Path) -> dict[str, Any]:
    missing = [rel for rel in REQUIRED_REPO_PATHS if not (root / rel).exists()]
    return {"ok": not missing, "missing": missing, "checked": list(REQUIRED_REPO_PATHS)}


def _forbidden_imports_loaded_since(before: set[str]) -> list[str]:
    after = set(sys.modules)
    return sorted(root for root in FORBIDDEN_OPTIONAL_ROOTS if root in after and root not in before)


def _always_false_summary(payload: Mapping[str, Any]) -> dict[str, bool]:
    return {field: payload.get(field) is False for field in ALWAYS_FALSE_FIELDS}


def _always_false_ok(payload: Mapping[str, Any]) -> bool:
    return all(_always_false_summary(payload).values())


def _compact_source_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    result = payload.get("archive_metadata_validation_result") or {}
    candidate = payload.get("candidate_safety") or {}
    return {
        "ok": payload.get("ok"),
        "patch": payload.get("patch"),
        "l21_5_complete": payload.get("l21_5_complete"),
        "source_l21_4_controlled_authorization_gate_accepted": payload.get("source_l21_4_controlled_authorization_gate_accepted"),
        "archive_metadata_proof_requested": payload.get("archive_metadata_proof_requested"),
        "archive_metadata_proof_authorized": payload.get("archive_metadata_proof_authorized"),
        "candidate_safe_for_l21_5_metadata_only_proof": candidate.get("candidate_safe_for_l21_5_metadata_only_proof"),
        "archive_metadata_validation_performed": result.get("archive_metadata_validation_performed"),
        "archive_validation_ready": result.get("archive_validation_ready"),
        "archive_entry_count": result.get("archive_entry_count"),
        "archive_entry_names": result.get("archive_entry_names"),
        "manifest_entry_detected_from_listing": result.get("manifest_entry_detected_from_listing"),
        "archive_validation_scope": payload.get("archive_validation_scope"),
        "archive_validation_performed": payload.get("archive_validation_performed"),
        "downloaded_archive_opened": payload.get("downloaded_archive_opened"),
        "downloaded_archive_contents_listed": payload.get("downloaded_archive_contents_listed"),
        "downloaded_archive_extracted": payload.get("downloaded_archive_extracted"),
        "downloaded_manifest_read": payload.get("downloaded_manifest_read"),
        "archive_member_bytes_read": payload.get("archive_member_bytes_read"),
        "downloaded_file_bytes_read": payload.get("downloaded_file_bytes_read"),
        "downloaded_file_stat_performed": payload.get("downloaded_file_stat_performed"),
        "downloaded_file_hash_performed": payload.get("downloaded_file_hash_performed"),
        "browser_started": payload.get("browser_started"),
        "edge_process_started": payload.get("edge_process_started"),
        "package_run_performed_by_adapter": payload.get("package_run_performed_by_adapter"),
        "missing_commands": payload.get("missing_commands"),
        "missing_doc_phrases": payload.get("missing_doc_phrases"),
    }


def build_edge_downloaded_archive_validation_broad_checkpoint(
    repo_root: str | Path | None = None,
    *,
    target_url: str | None = None,
) -> dict[str, Any]:
    """Build the L21.6 broad checkpoint over L21.1 through L21.5."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)
    target = target_url or DEFAULT_TARGET_URL

    default_payload = l21_05.build_edge_downloaded_archive_validation_metadata_proof(
        root,
        target_url=target,
    )
    authorized_payload = l21_05.build_edge_downloaded_archive_validation_metadata_proof(
        root,
        allow_archive_metadata_proof=True,
        authorization_token=REQUIRED_ARCHIVE_METADATA_PROOF_AUTHORIZATION_TOKEN,
        candidate_path_metadata=DEFAULT_CANDIDATE_RELATIVE_PATH,
        target_url=target,
    )
    unsafe_payload = l21_05.build_edge_downloaded_archive_validation_metadata_proof(
        root,
        allow_archive_metadata_proof=True,
        authorization_token=REQUIRED_ARCHIVE_METADATA_PROOF_AUTHORIZATION_TOKEN,
        candidate_path_metadata="docs/not_a_patchops_bundle.txt",
        target_url=target,
    )

    names = _command_names()
    missing_commands = [name for name in (SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)
    target_url_allowed = bool(authorized_payload.get("target_url_allowed"))

    default_ok = (
        default_payload.get("ok") is True
        and default_payload.get("patch") == SOURCE_PATCH
        and default_payload.get("l21_5_complete") is True
        and default_payload.get("source_l21_4_controlled_authorization_gate_accepted") is True
        and default_payload.get("archive_metadata_proof_authorized") is False
        and default_payload.get("archive_validation_performed") is False
        and default_payload.get("downloaded_archive_opened") is False
        and default_payload.get("downloaded_archive_contents_listed") is False
        and _always_false_ok(default_payload)
    )
    authorized_result = authorized_payload.get("archive_metadata_validation_result") or {}
    authorized_ok = (
        authorized_payload.get("ok") is True
        and authorized_payload.get("patch") == SOURCE_PATCH
        and authorized_payload.get("l21_5_complete") is True
        and authorized_payload.get("source_l21_4_controlled_authorization_gate_accepted") is True
        and authorized_payload.get("archive_metadata_proof_authorized") is True
        and authorized_payload.get("archive_validation_scope") == "metadata_listing_only_synthetic_patchops_runtime_archive_fixture"
        and authorized_payload.get("candidate_safety", {}).get("candidate_safe_for_l21_5_metadata_only_proof") is True
        and authorized_result.get("archive_metadata_validation_performed") is True
        and authorized_result.get("archive_validation_ready") is True
        and authorized_result.get("archive_entry_count", 0) >= 1
        and authorized_payload.get("archive_validation_performed") is True
        and authorized_payload.get("downloaded_archive_opened") is True
        and authorized_payload.get("downloaded_archive_contents_listed") is True
        and _always_false_ok(authorized_payload)
    )
    unsafe_ok = (
        unsafe_payload.get("ok") is False
        and unsafe_payload.get("archive_metadata_proof_authorized") is False
        and unsafe_payload.get("candidate_safety", {}).get("candidate_safe_for_l21_5_metadata_only_proof") is False
        and (unsafe_payload.get("archive_metadata_validation_result") or {}).get("archive_metadata_validation_performed") is False
        and unsafe_payload.get("archive_validation_performed") is False
        and unsafe_payload.get("downloaded_archive_opened") is False
        and unsafe_payload.get("downloaded_archive_contents_listed") is False
        and _always_false_ok(unsafe_payload)
    )
    l21_chain_ok = default_ok and authorized_ok and unsafe_ok

    checks = [
        _check("l21_1_through_l21_5_remain_accepted", l21_chain_ok),
        _check("default_archive_metadata_proof_readback_remains_passive", default_ok, _compact_source_summary(default_payload)),
        _check("authorized_archive_metadata_proof_readback_remains_metadata_only", authorized_ok, _compact_source_summary(authorized_payload)),
        _check("unsafe_archive_candidate_rejected_without_archive_access", unsafe_ok, _compact_source_summary(unsafe_payload)),
        _check("only_synthetic_archive_metadata_listing_is_allowed", authorized_ok),
        _check("extract_manifest_member_byte_read_package_run_still_blocked", _always_false_ok(authorized_payload), _always_false_summary(authorized_payload)),
        _check("browser_download_pasteback_package_run_still_blocked", True),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("target_url_allowlist_enforced", target_url_allowed, {"target_url": target}),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l21_6_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "broad_archive_validation_checkpoint": True,
        "archive_metadata_only_stream_checkpoint": True,
        "synthetic_patchops_runtime_archive_fixture_only": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "l21_1_through_l21_5_remain_accepted": l21_chain_ok,
        "archive_metadata_only_validation_proof_remains_accepted": authorized_ok,
        "default_archive_metadata_proof_readback_remains_passive": default_ok,
        "authorized_archive_metadata_proof_readback_remains_metadata_only": authorized_ok,
        "unsafe_archive_candidate_remains_rejected_without_archive_access": unsafe_ok,
        "only_synthetic_patchops_runtime_archive_metadata_listing_is_allowed": True,
        "archive_validation_scope": "metadata_listing_only_synthetic_patchops_runtime_archive_fixture",
        "archive_validation_execution_allowed": bool(authorized_payload.get("archive_validation_execution_allowed")),
        "archive_validation_active": False,
        "archive_validation_performed": bool(authorized_payload.get("archive_validation_performed")),
        "downloaded_archive_opened": bool(authorized_payload.get("downloaded_archive_opened")),
        "downloaded_archive_contents_listed": bool(authorized_payload.get("downloaded_archive_contents_listed")),
        "archive_entry_count": authorized_result.get("archive_entry_count", 0),
        "archive_entry_names": authorized_result.get("archive_entry_names", []),
        "manifest_entry_detected_from_listing": authorized_result.get("manifest_entry_detected_from_listing", False),
        "downloaded_archive_extracted": False,
        "downloaded_manifest_read": False,
        "archive_member_bytes_read": False,
        "downloaded_file_bytes_read": False,
        "downloaded_file_stat_performed": False,
        "downloaded_file_hash_performed": False,
        "real_file_stat_performed": False,
        "real_file_hash_performed": False,
        "hash_validation_active": False,
        "manifest_read_active": False,
        "package_run_from_browser_active": False,
        "live_download_execution_allowed": False,
        "download_workflow_execution_allowed": False,
        "download_workflow_active": False,
        "download_workflow_allowed": False,
        "download_allowed": False,
        "download_performed": False,
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
        "real_browser_download_remains_inactive": True,
        "pasteback_remains_inactive": True,
        "package_run_from_browser_remains_inactive": True,
        "source_default_summary": _compact_source_summary(default_payload),
        "source_authorized_summary": _compact_source_summary(authorized_payload),
        "source_unsafe_summary": _compact_source_summary(unsafe_payload),
        "l21_6_complete": ok,
        "remaining_l21_6_patches": [] if ok else [PATCH],
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
        f"L21.1-L21.5 Accepted          : {payload.get('l21_1_through_l21_5_remain_accepted')}",
        f"Metadata Proof Accepted       : {payload.get('archive_metadata_only_validation_proof_remains_accepted')}",
        f"Archive Validation Scope      : {payload.get('archive_validation_scope')}",
        f"Archive Opened/List Metadata  : {payload.get('downloaded_archive_opened')}/{payload.get('downloaded_archive_contents_listed')}",
        f"Extract/Manifest/Bytes Blocked: {payload.get('downloaded_archive_extracted') is False and payload.get('downloaded_manifest_read') is False and payload.get('archive_member_bytes_read') is False}",
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

    payload = build_edge_downloaded_archive_validation_broad_checkpoint(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
