"""L19.5 metadata-only downloaded-file validation proof for Microsoft Edge.

L19.5 proves downloaded-file validation decisions from explicit metadata only.
It does not start Edge, use Selenium, use CDP, scrape the DOM, inspect a real
page, click, download, check whether a real file exists, stat/hash files, open
archives, list archive contents, extract archives, read manifests, read file
bytes, read artifact content, paste, send, run packages, start a localhost
server, use a browser extension, commit, or push.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_downloaded_file_validation_controlled_authorization_gate as l19_04

PATCH = "L19.5"
PHASE = "L19"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L19.5 Microsoft Edge first controlled downloaded-file metadata validation proof"
COMMAND_NAME = "browser-start-supervised-launch-edge-downloaded-file-metadata-validation-proof"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-downloaded-file-validation-controlled-authorization-gate"
SOURCE_PATCH = "L19.4"
NEXT_PATCH = "L19.6 Microsoft Edge downloaded-file validation broad checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_METADATA_VALIDATION_PROOF_AUTHORIZATION_TOKEN = "PATCHOPS_L19_EDGE_DOWNLOADED_FILE_METADATA_VALIDATION_PROOF_AUTHORIZED"
SOURCE_L19_4_AUTHORIZATION_TOKEN = "PATCHOPS_L19_EDGE_DOWNLOADED_FILE_VALIDATION_CONTROLLED_AUTHORIZED_READBACK_ONLY"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_downloaded_file_validation_passive_plan_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_file_validation_controlled_authorization_gate.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_file_metadata_validation_proof.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_downloaded_file_validation_passive_plan_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_downloaded_file_validation_controlled_authorization_gate.md",
    "docs/llm_browser_live_adapter_edge_downloaded_file_metadata_validation_proof.md",
    "scripts/patch_l19_03_brief_validate.py",
    "scripts/patch_l19_04_brief_validate.py",
    "scripts/patch_l19_05_brief_validate.py",
    "tests/test_l19_03_edge_downloaded_file_validation_passive_plan_checkpoint_current.py",
    "tests/test_l19_04_edge_downloaded_file_validation_controlled_authorization_gate_current.py",
    "tests/test_l19_05_edge_downloaded_file_metadata_validation_proof_current.py",
)

SAFETY_PHRASES = (
    "L19.5 Microsoft Edge first controlled downloaded-file metadata validation proof",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    REQUIRED_METADATA_VALIDATION_PROOF_AUTHORIZATION_TOKEN,
    "Microsoft Edge first",
    "Opera second",
    "controlled downloaded-file metadata validation proof",
    "metadata-only downloaded-file validation decision",
    "L19.4 controlled authorization gate remains accepted",
    "downloaded-file metadata validation proof authorization token",
    "downloaded-file metadata validation may classify synthetic metadata only",
    "downloaded-file metadata validation does not check whether a file exists",
    "downloaded-file metadata validation does not stat a file",
    "downloaded-file metadata validation does not hash a file",
    "downloaded-file metadata validation does not open a downloaded archive",
    "downloaded-file metadata validation does not list downloaded archive contents",
    "downloaded-file metadata validation does not extract a downloaded archive",
    "downloaded-file metadata validation does not read a downloaded manifest",
    "downloaded-file metadata validation does not read downloaded file bytes",
    "downloaded-file metadata validation does not run a package",
    "downloaded-file validation execution allowed: false",
    "downloaded-file validation active: false",
    "downloaded-file validation is not performed",
    "downloaded file bytes are not read",
    "downloaded archive is not opened",
    "downloaded manifest is not read",
    "download workflow remains inactive",
    "real browser download remains inactive",
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
    "no click/download/file-read/paste/send/package-run side effect",
    "no localhost PatchOps server",
    "no browser extension",
    "no git commit or git push",
    "L19.6 Microsoft Edge downloaded-file validation broad checkpoint",
)

ALLOWED_METADATA_KEYS = (
    "candidate_path_metadata",
    "candidate_filename_metadata",
    "candidate_pattern",
    "candidate_extension_metadata",
    "candidate_path_is_metadata_only",
    "downloaded_file_validation_authorization_from_l19_4",
    "download_metadata_proof_from_l18_5",
    "download_workflow_complete_from_l18_7",
    "target_url_allowed_metadata",
    "candidate_count",
    "already_validated",
    "already_processed",
    "operator_reviewed_metadata",
)

FORBIDDEN_METADATA_KEYS = (
    "file_exists",
    "file_stat",
    "file_size_bytes_from_disk",
    "file_hash",
    "file_bytes",
    "downloaded_file_bytes",
    "downloaded_file_content",
    "archive_members",
    "archive_bytes",
    "manifest_content",
    "manifest_json",
    "artifact_content",
    "artifact_source_code",
    "conversation_text",
    "prompt_text",
    "account_data",
    "cookies",
    "tokens",
    "local_storage",
    "dom_html",
    "download_href",
)

PASSIVE_FALSE_FIELDS = (
    "controlled_downloaded_file_validation_execution_allowed",
    "downloaded_file_metadata_validation_execution_allowed",
    "downloaded_file_metadata_validation_active",
    "downloaded_file_validation_execution_allowed",
    "downloaded_file_validation_active",
    "downloaded_file_validation_performed",
    "downloaded_file_exists_check_performed",
    "downloaded_file_stat_performed",
    "downloaded_file_hash_performed",
    "downloaded_file_bytes_read",
    "downloaded_archive_opened",
    "downloaded_archive_contents_listed",
    "downloaded_archive_extracted",
    "downloaded_manifest_read",
    "live_download_execution_allowed",
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

SOURCE_L19_4_PASSIVE_FALSE_FIELDS = tuple(
    field for field in PASSIVE_FALSE_FIELDS
    if field not in {"downloaded_file_metadata_validation_execution_allowed", "downloaded_file_metadata_validation_active"}
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_downloaded_file_metadata_validation_proof.md")
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


def _source_passive_false_summary(payload: Mapping[str, Any]) -> dict[str, bool]:
    return {field: payload.get(field) is False for field in SOURCE_L19_4_PASSIVE_FALSE_FIELDS}


def _source_payload_is_passive(payload: Mapping[str, Any]) -> bool:
    return all(_source_passive_false_summary(payload).values())


def positive_downloaded_file_metadata_fixture() -> dict[str, Any]:
    return {
        "candidate_path_metadata": "data/runtime/browser_downloads/patch_999_example_patchops_bundle.zip",
        "candidate_filename_metadata": "patch_999_example_patchops_bundle.zip",
        "candidate_pattern": "patch_*_patchops_bundle.zip",
        "candidate_extension_metadata": ".zip",
        "candidate_path_is_metadata_only": True,
        "downloaded_file_validation_authorization_from_l19_4": True,
        "download_metadata_proof_from_l18_5": True,
        "download_workflow_complete_from_l18_7": True,
        "target_url_allowed_metadata": True,
        "candidate_count": 1,
        "already_validated": False,
        "already_processed": False,
        "operator_reviewed_metadata": True,
    }


def negative_downloaded_file_metadata_fixture() -> dict[str, Any]:
    data = positive_downloaded_file_metadata_fixture()
    data["candidate_filename_metadata"] = "notes.txt"
    data["candidate_path_metadata"] = "data/runtime/browser_downloads/notes.txt"
    data["candidate_extension_metadata"] = ".txt"
    return data


def classify_downloaded_file_validation_from_metadata(metadata: Mapping[str, Any]) -> dict[str, Any]:
    """Classify downloaded-file validation readiness from metadata only."""
    forbidden_present = sorted(key for key in FORBIDDEN_METADATA_KEYS if key in metadata)
    candidate_path = str(metadata.get("candidate_path_metadata") or "")
    filename = str(metadata.get("candidate_filename_metadata") or "")
    pattern = str(metadata.get("candidate_pattern") or "patch_*_patchops_bundle.zip")
    extension = str(metadata.get("candidate_extension_metadata") or "")
    candidate_count_raw = metadata.get("candidate_count", 1)
    try:
        candidate_count = int(candidate_count_raw)
    except (TypeError, ValueError):
        candidate_count = -1

    reasons: list[str] = []
    if forbidden_present:
        reasons.append("forbidden_metadata_keys_present")
    if not bool(metadata.get("candidate_path_is_metadata_only")):
        reasons.append("candidate_path_is_not_declared_metadata_only")
    if not candidate_path:
        reasons.append("candidate_path_metadata_missing")
    if not filename:
        reasons.append("candidate_filename_metadata_missing")
    if filename and candidate_path and not candidate_path.replace("\\", "/").endswith("/" + filename):
        reasons.append("candidate_path_metadata_does_not_end_with_candidate_filename")
    if extension.lower() != ".zip":
        reasons.append("candidate_extension_metadata_is_not_zip")
    if filename and not filename.lower().endswith(".zip"):
        reasons.append("candidate_filename_does_not_end_with_zip")
    if filename and not fnmatch.fnmatch(filename, pattern):
        reasons.append("candidate_filename_does_not_match_patchops_bundle_pattern")
    if not bool(metadata.get("downloaded_file_validation_authorization_from_l19_4")):
        reasons.append("l19_4_downloaded_file_validation_authorization_metadata_not_confirmed")
    if not bool(metadata.get("download_metadata_proof_from_l18_5")):
        reasons.append("l18_5_download_metadata_proof_metadata_not_confirmed")
    if not bool(metadata.get("download_workflow_complete_from_l18_7")):
        reasons.append("l18_7_download_workflow_completion_metadata_not_confirmed")
    if not bool(metadata.get("target_url_allowed_metadata")):
        reasons.append("target_url_allowlist_metadata_not_confirmed")
    if not bool(metadata.get("operator_reviewed_metadata")):
        reasons.append("operator_reviewed_metadata_not_confirmed")
    if bool(metadata.get("already_validated")):
        reasons.append("candidate_already_validated")
    if bool(metadata.get("already_processed")):
        reasons.append("candidate_already_processed")
    if candidate_count != 1:
        reasons.append("candidate_count_is_not_exactly_one")

    ready = not reasons
    return {
        "downloaded_file_metadata_validation_ready": ready,
        "status": STATUS_PASS if ready else STATUS_FAIL,
        "candidate_path_metadata": candidate_path,
        "candidate_filename_metadata": filename,
        "candidate_filename_pattern": pattern,
        "candidate_extension_metadata": extension,
        "candidate_count": candidate_count,
        "allowed_metadata_keys_seen": sorted(key for key in metadata if key in ALLOWED_METADATA_KEYS),
        "forbidden_metadata_keys_present": forbidden_present,
        "blocking_reasons": reasons,
        "metadata_only": True,
        "file_exists_check_performed": False,
        "file_stat_performed": False,
        "file_hash_performed": False,
        "file_bytes_read": False,
        "archive_opened": False,
        "archive_contents_listed": False,
        "archive_extracted": False,
        "manifest_read": False,
        "package_run_performed": False,
        "pasteback_performed": False,
        "auto_send_performed": False,
    }


def _source_l19_4_ok(root: Path, target_url: str) -> tuple[bool, dict[str, Any]]:
    source = l19_04.build_edge_downloaded_file_validation_controlled_authorization_gate(
        root,
        allow_downloaded_file_validation_authorization=True,
        authorization_token=SOURCE_L19_4_AUTHORIZATION_TOKEN,
        target_url=target_url,
    )
    ok = (
        source.get("ok") is True
        and source.get("patch") == SOURCE_PATCH
        and source.get("l19_4_complete") is True
        and source.get("source_l19_3_passive_plan_checkpoint_accepted") is True
        and source.get("downloaded_file_validation_authorized_for_future_phase") is True
        and source.get("controlled_downloaded_file_validation_execution_allowed") is False
        and source.get("downloaded_file_validation_execution_allowed") is False
        and source.get("downloaded_file_validation_active") is False
        and source.get("downloaded_file_validation_performed") is False
        and source.get("downloaded_file_exists_check_performed") is False
        and source.get("downloaded_file_stat_performed") is False
        and source.get("downloaded_file_hash_performed") is False
        and source.get("downloaded_file_bytes_read") is False
        and source.get("downloaded_archive_opened") is False
        and source.get("downloaded_archive_contents_listed") is False
        and source.get("downloaded_archive_extracted") is False
        and source.get("downloaded_manifest_read") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("package_run_performed_by_adapter") is False
        and _source_payload_is_passive(source)
    )
    return ok, source


def build_edge_downloaded_file_metadata_validation_proof(
    repo_root: str | Path | None = None,
    *,
    allow_downloaded_file_metadata_validation_proof: bool = False,
    authorization_token: str | None = None,
    downloaded_file_metadata: Mapping[str, Any] | None = None,
    target_url: str | None = None,
) -> dict[str, Any]:
    """Build the L19.5 metadata-only downloaded-file validation proof payload."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)
    target = target_url or DEFAULT_TARGET_URL
    source_ok, source = _source_l19_4_ok(root, target)

    names = _command_names()
    missing_commands = [name for name in (SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)

    requested = bool(allow_downloaded_file_metadata_validation_proof)
    token_present = authorization_token == REQUIRED_METADATA_VALIDATION_PROOF_AUTHORIZATION_TOKEN
    proof_authorized = requested and token_present
    supplied_metadata = dict(downloaded_file_metadata or {})
    classification_performed = proof_authorized and bool(supplied_metadata)
    classification = classify_downloaded_file_validation_from_metadata(supplied_metadata) if classification_performed else {
        "downloaded_file_metadata_validation_ready": False,
        "status": "NOT_RUN",
        "blocking_reasons": ["downloaded_file_metadata_validation_proof_not_authorized_or_no_metadata_supplied"],
        "metadata_only": True,
        "file_exists_check_performed": False,
        "file_stat_performed": False,
        "file_hash_performed": False,
        "file_bytes_read": False,
        "archive_opened": False,
        "archive_contents_listed": False,
        "archive_extracted": False,
        "manifest_read": False,
        "package_run_performed": False,
        "pasteback_performed": False,
        "auto_send_performed": False,
    }
    target_url_allowed = bool(source.get("target_url_allowed"))

    proof_result_ok = (not classification_performed) or classification.get("downloaded_file_metadata_validation_ready") is True
    metadata_safety_ok = (
        classification.get("metadata_only") is True
        and classification.get("file_exists_check_performed") is False
        and classification.get("file_stat_performed") is False
        and classification.get("file_hash_performed") is False
        and classification.get("file_bytes_read") is False
        and classification.get("archive_opened") is False
        and classification.get("archive_contents_listed") is False
        and classification.get("archive_extracted") is False
        and classification.get("manifest_read") is False
        and classification.get("package_run_performed") is False
        and classification.get("pasteback_performed") is False
        and classification.get("auto_send_performed") is False
    )

    checks = [
        _check("source_l19_4_controlled_authorization_gate_accepted", source_ok),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("target_url_allowlist_enforced", target_url_allowed, {"target_url": target}),
        _check("downloaded_file_metadata_validation_proof_authorization_surface_present", True),
        _check("downloaded_file_metadata_validation_proof_authorization_token_required", True),
        _check("metadata_only_validation_result_ok_when_performed", proof_result_ok, {"classification_performed": classification_performed}),
        _check("metadata_validation_has_no_file_check_stat_hash_byte_archive_manifest_package_side_effect", metadata_safety_ok),
        _check("downloaded_file_validation_execution_still_blocked", True),
        _check("pasteback_and_package_run_still_blocked", True),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l19_5_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "controlled_downloaded_file_metadata_validation_proof": True,
        "metadata_only_downloaded_file_validation_decision": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "source_l19_4_controlled_authorization_gate_accepted": source_ok,
        "l19_4_complete": bool(source.get("l19_4_complete")),
        "source_l19_3_passive_plan_checkpoint_accepted": bool(source.get("source_l19_3_passive_plan_checkpoint_accepted")),
        "downloaded_file_metadata_validation_proof_requested": requested,
        "downloaded_file_metadata_validation_proof_token_present": token_present,
        "downloaded_file_metadata_validation_proof_authorized": proof_authorized,
        "downloaded_file_metadata_validation_classification_performed": classification_performed,
        "downloaded_file_metadata_validation_classification": classification,
        "downloaded_file_metadata_validation_ready": bool(classification.get("downloaded_file_metadata_validation_ready")),
        "downloaded_file_metadata_validation_scope": "synthetic_or_operator_supplied_metadata_only",
        "controlled_downloaded_file_validation_execution_allowed": False,
        "downloaded_file_metadata_validation_execution_allowed": False,
        "downloaded_file_metadata_validation_active": False,
        "downloaded_file_validation_execution_allowed": False,
        "downloaded_file_validation_active": False,
        "downloaded_file_validation_performed": False,
        "downloaded_file_exists_check_performed": False,
        "downloaded_file_stat_performed": False,
        "downloaded_file_hash_performed": False,
        "downloaded_file_bytes_read": False,
        "downloaded_archive_opened": False,
        "downloaded_archive_contents_listed": False,
        "downloaded_archive_extracted": False,
        "downloaded_manifest_read": False,
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
        "source_l19_4_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "l19_4_complete": source.get("l19_4_complete"),
            "source_l19_3_passive_plan_checkpoint_accepted": source.get("source_l19_3_passive_plan_checkpoint_accepted"),
            "downloaded_file_validation_authorized_for_future_phase": source.get("downloaded_file_validation_authorized_for_future_phase"),
            "controlled_downloaded_file_validation_execution_allowed": source.get("controlled_downloaded_file_validation_execution_allowed"),
            "downloaded_file_validation_execution_allowed": source.get("downloaded_file_validation_execution_allowed"),
            "downloaded_file_validation_active": source.get("downloaded_file_validation_active"),
            "downloaded_file_validation_performed": source.get("downloaded_file_validation_performed"),
            "downloaded_file_exists_check_performed": source.get("downloaded_file_exists_check_performed"),
            "downloaded_file_bytes_read": source.get("downloaded_file_bytes_read"),
            "downloaded_archive_opened": source.get("downloaded_archive_opened"),
            "downloaded_archive_contents_listed": source.get("downloaded_archive_contents_listed"),
            "downloaded_manifest_read": source.get("downloaded_manifest_read"),
            "browser_started": source.get("browser_started"),
            "edge_process_started": source.get("edge_process_started"),
            "package_run_performed_by_adapter": source.get("package_run_performed_by_adapter"),
            "missing_commands": source.get("missing_commands"),
            "missing_doc_phrases": source.get("missing_doc_phrases"),
        },
        "l19_5_complete": ok,
        "remaining_l19_5_patches": [] if ok else [PATCH],
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
        f"Patch                              : {payload.get('patch')}",
        f"Status                             : {payload.get('status')}",
        f"Command                            : {payload.get('command_name')}",
        f"L19.4 Accepted                     : {payload.get('source_l19_4_controlled_authorization_gate_accepted')}",
        f"Metadata Proof Authorized          : {payload.get('downloaded_file_metadata_validation_proof_authorized')}",
        f"Metadata Classification Run        : {payload.get('downloaded_file_metadata_validation_classification_performed')}",
        f"Ready From Metadata                : {payload.get('downloaded_file_metadata_validation_ready')}",
        f"File Validation Execution Allowed  : {payload.get('downloaded_file_validation_execution_allowed')}",
        f"Downloaded Bytes Read              : {payload.get('downloaded_file_bytes_read')}",
        f"Archive Opened                     : {payload.get('downloaded_archive_opened')}",
        f"Browser Started                    : {payload.get('browser_started')}",
        f"Next Patch                         : {payload.get('next_patch')}",
        "",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        state = "PASS" if check.get("ok") else "FAIL"
        lines.append(f"- {state}: {check.get('name')}")
    return "\n".join(lines) + "\n"


def _metadata_from_args(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "candidate_path_metadata": args.candidate_path_metadata,
        "candidate_filename_metadata": args.candidate_filename_metadata,
        "candidate_pattern": args.candidate_pattern,
        "candidate_extension_metadata": args.candidate_extension_metadata,
        "candidate_path_is_metadata_only": args.candidate_path_is_metadata_only,
        "downloaded_file_validation_authorization_from_l19_4": args.downloaded_file_validation_authorization_from_l19_4,
        "download_metadata_proof_from_l18_5": args.download_metadata_proof_from_l18_5,
        "download_workflow_complete_from_l18_7": args.download_workflow_complete_from_l18_7,
        "target_url_allowed_metadata": args.target_url_allowed_metadata,
        "candidate_count": args.candidate_count,
        "already_validated": args.already_validated,
        "already_processed": args.already_processed,
        "operator_reviewed_metadata": args.operator_reviewed_metadata,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--allow-downloaded-file-metadata-validation-proof", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--candidate-path-metadata", default="data/runtime/browser_downloads/patch_999_example_patchops_bundle.zip")
    parser.add_argument("--candidate-filename-metadata", default="patch_999_example_patchops_bundle.zip")
    parser.add_argument("--candidate-pattern", default="patch_*_patchops_bundle.zip")
    parser.add_argument("--candidate-extension-metadata", default=".zip")
    parser.add_argument("--candidate-path-is-metadata-only", action="store_true")
    parser.add_argument("--downloaded-file-validation-authorization-from-l19-4", action="store_true")
    parser.add_argument("--download-metadata-proof-from-l18-5", action="store_true")
    parser.add_argument("--download-workflow-complete-from-l18-7", action="store_true")
    parser.add_argument("--target-url-allowed-metadata", action="store_true")
    parser.add_argument("--operator-reviewed-metadata", action="store_true")
    parser.add_argument("--candidate-count", type=int, default=1)
    parser.add_argument("--already-validated", action="store_true")
    parser.add_argument("--already-processed", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_downloaded_file_metadata_validation_proof(
        args.repo_root,
        allow_downloaded_file_metadata_validation_proof=args.allow_downloaded_file_metadata_validation_proof,
        authorization_token=args.authorization_token,
        downloaded_file_metadata=_metadata_from_args(args),
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
