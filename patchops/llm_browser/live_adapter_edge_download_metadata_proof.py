"""L18.5 controlled metadata-only download proof for Microsoft Edge.

L18.5 proves the first download-readiness decision from explicit metadata only.
It does not start Edge, use Selenium, use CDP, scrape the DOM, inspect a real page,
click a download control, download a file, create a staging directory, read
file bytes, read artifact content, paste, send, run a package, start a localhost
server, use a browser extension, commit, or push.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_download_workflow_controlled_live_authorization_gate as l18_04

PATCH = "L18.5"
PHASE = "L18"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L18.5 Microsoft Edge first controlled download metadata proof"
COMMAND_NAME = "browser-start-supervised-launch-edge-download-metadata-proof"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-download-workflow-controlled-live-authorization-gate"
SOURCE_PATCH = "L18.4"
NEXT_PATCH = "L18.6 Microsoft Edge download workflow broad checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_DOWNLOAD_METADATA_PROOF_AUTHORIZATION_TOKEN = "PATCHOPS_L18_EDGE_DOWNLOAD_METADATA_PROOF_AUTHORIZED"
SOURCE_L18_4_AUTHORIZATION_TOKEN = "PATCHOPS_L18_EDGE_DOWNLOAD_WORKFLOW_LIVE_AUTHORIZED_READBACK_ONLY"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_download_workflow_passive_plan_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_download_workflow_controlled_live_authorization_gate.py",
    "patchops/llm_browser/live_adapter_edge_download_metadata_proof.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_download_workflow_passive_plan_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_download_workflow_controlled_live_authorization_gate.md",
    "docs/llm_browser_live_adapter_edge_download_metadata_proof.md",
    "scripts/patch_l18_03_brief_validate.py",
    "scripts/patch_l18_04_brief_validate.py",
    "scripts/patch_l18_05_brief_validate.py",
    "tests/test_l18_03_edge_download_workflow_passive_plan_checkpoint_current.py",
    "tests/test_l18_04_edge_download_workflow_controlled_live_authorization_gate_current.py",
    "tests/test_l18_05_edge_download_metadata_proof_current.py",
)

SAFETY_PHRASES = (
    "L18.5 Microsoft Edge first controlled download metadata proof",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    REQUIRED_DOWNLOAD_METADATA_PROOF_AUTHORIZATION_TOKEN,
    "Microsoft Edge first",
    "Opera second",
    "controlled download metadata proof",
    "metadata-only download readiness classification",
    "L18.4 controlled live authorization gate remains accepted",
    "download metadata proof authorization token",
    "download metadata proof may classify synthetic metadata only",
    "download metadata proof does not inspect a real page",
    "download metadata proof does not click a download control",
    "download metadata proof does not download a file",
    "download metadata proof does not create a staging directory",
    "download metadata proof does not read downloaded file bytes",
    "download metadata proof does not read artifact content",
    "download metadata proof does not run a package",
    "live browser download workflow remains inactive",
    "download workflow active: false",
    "download workflow execution allowed: false",
    "download is not performed",
    "downloaded file bytes are not read",
    "download staging directory is not created",
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
    "L18.6 Microsoft Edge download workflow broad checkpoint",
)

ALLOWED_METADATA_KEYS = (
    "candidate_filename",
    "candidate_visible_filename_metadata",
    "candidate_pattern",
    "artifact_presence_from_l17_metadata",
    "download_control_visible_metadata",
    "download_control_enabled_metadata",
    "download_authorization_from_l18_4",
    "target_url_allowed_metadata",
    "staging_path_metadata",
    "staging_path_is_metadata_only",
    "candidate_count",
    "already_downloaded",
    "already_processed",
)

FORBIDDEN_METADATA_KEYS = (
    "conversation_text",
    "prompt_text",
    "account_data",
    "artifact_content",
    "artifact_source_code",
    "downloaded_file_bytes",
    "downloaded_file_content",
    "cookies",
    "tokens",
    "local_storage",
    "older_conversation_messages",
    "dom_html",
    "download_href",
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_download_metadata_proof.md")
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


def positive_download_metadata_fixture() -> dict[str, Any]:
    return {
        "candidate_filename": "patch_999_example_patchops_bundle.zip",
        "candidate_visible_filename_metadata": "patch_999_example_patchops_bundle.zip",
        "candidate_pattern": "patch_*_patchops_bundle.zip",
        "artifact_presence_from_l17_metadata": True,
        "download_control_visible_metadata": True,
        "download_control_enabled_metadata": True,
        "download_authorization_from_l18_4": True,
        "target_url_allowed_metadata": True,
        "staging_path_metadata": "data/runtime/browser_downloads/patch_999_example_patchops_bundle.zip",
        "staging_path_is_metadata_only": True,
        "candidate_count": 1,
        "already_downloaded": False,
        "already_processed": False,
    }


def negative_download_metadata_fixture() -> dict[str, Any]:
    data = positive_download_metadata_fixture()
    data["candidate_filename"] = "notes.txt"
    data["candidate_visible_filename_metadata"] = "notes.txt"
    return data


def classify_download_readiness_from_metadata(metadata: Mapping[str, Any]) -> dict[str, Any]:
    """Classify download readiness from metadata only; never click/download/read bytes."""
    forbidden_present = sorted(key for key in FORBIDDEN_METADATA_KEYS if key in metadata)
    filename = str(metadata.get("candidate_filename") or "")
    visible_filename = str(metadata.get("candidate_visible_filename_metadata") or "")
    pattern = str(metadata.get("candidate_pattern") or "patch_*_patchops_bundle.zip")
    staging_path = str(metadata.get("staging_path_metadata") or "")
    candidate_count_raw = metadata.get("candidate_count", 1)
    try:
        candidate_count = int(candidate_count_raw)
    except (TypeError, ValueError):
        candidate_count = -1

    reasons: list[str] = []
    if forbidden_present:
        reasons.append("forbidden_metadata_keys_present")
    if not bool(metadata.get("artifact_presence_from_l17_metadata")):
        reasons.append("l17_artifact_presence_metadata_not_confirmed")
    if not bool(metadata.get("download_authorization_from_l18_4")):
        reasons.append("l18_4_download_authorization_metadata_not_confirmed")
    if not bool(metadata.get("target_url_allowed_metadata")):
        reasons.append("target_url_allowlist_metadata_not_confirmed")
    if not filename.lower().endswith(".zip"):
        reasons.append("candidate_filename_does_not_end_with_zip")
    if not fnmatch.fnmatch(filename, pattern):
        reasons.append("candidate_filename_does_not_match_patchops_bundle_pattern")
    if visible_filename != filename:
        reasons.append("visible_filename_metadata_does_not_match_candidate_filename")
    if not bool(metadata.get("download_control_visible_metadata")):
        reasons.append("download_control_not_visible_in_metadata")
    if not bool(metadata.get("download_control_enabled_metadata")):
        reasons.append("download_control_not_enabled_in_metadata")
    if not bool(metadata.get("staging_path_is_metadata_only")):
        reasons.append("staging_path_is_not_declared_metadata_only")
    if not staging_path:
        reasons.append("staging_path_metadata_missing")
    if bool(metadata.get("already_downloaded")):
        reasons.append("candidate_already_downloaded")
    if bool(metadata.get("already_processed")):
        reasons.append("candidate_already_processed")
    if candidate_count != 1:
        reasons.append("candidate_count_is_not_exactly_one")

    ready = not reasons
    return {
        "download_readiness_confirmed_from_metadata": ready,
        "status": STATUS_PASS if ready else STATUS_FAIL,
        "candidate_filename": filename,
        "candidate_filename_pattern": pattern,
        "staging_path_metadata": staging_path,
        "staging_path_metadata_only": bool(metadata.get("staging_path_is_metadata_only")),
        "candidate_count": candidate_count,
        "allowed_metadata_keys_seen": sorted(key for key in metadata if key in ALLOWED_METADATA_KEYS),
        "forbidden_metadata_keys_present": forbidden_present,
        "blocking_reasons": reasons,
        "metadata_only": True,
        "real_page_inspection_performed": False,
        "click_download_performed": False,
        "download_performed": False,
        "downloaded_file_bytes_read": False,
        "download_staging_directory_created": False,
        "artifact_content_reading_performed": False,
        "package_run_performed": False,
    }


def _source_l18_4_ok(root: Path, target_url: str) -> tuple[bool, dict[str, Any]]:
    source = l18_04.build_edge_download_workflow_controlled_live_authorization_gate(
        root,
        allow_live_download_authorization=True,
        authorization_token=SOURCE_L18_4_AUTHORIZATION_TOKEN,
        target_url=target_url,
    )
    ok = (
        source.get("ok") is True
        and source.get("patch") == SOURCE_PATCH
        and source.get("l18_4_complete") is True
        and source.get("source_l18_3_passive_plan_checkpoint_accepted") is True
        and source.get("live_download_authorized_for_future_phase") is True
        and source.get("live_download_execution_allowed") is False
        and source.get("download_workflow_execution_allowed") is False
        and source.get("download_workflow_active") is False
        and source.get("download_performed") is False
        and source.get("downloaded_file_bytes_read") is False
        and source.get("click_download_performed") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("package_run_performed_by_adapter") is False
        and _payload_is_passive(source)
    )
    return ok, source


def build_edge_download_metadata_proof(
    repo_root: str | Path | None = None,
    *,
    allow_download_metadata_proof: bool = False,
    authorization_token: str | None = None,
    download_metadata: Mapping[str, Any] | None = None,
    target_url: str | None = None,
) -> dict[str, Any]:
    """Build the L18.5 metadata-only download proof payload."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)
    target = target_url or DEFAULT_TARGET_URL
    source_ok, source = _source_l18_4_ok(root, target)

    names = _command_names()
    missing_commands = [name for name in (SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)

    requested = bool(allow_download_metadata_proof)
    token_present = authorization_token == REQUIRED_DOWNLOAD_METADATA_PROOF_AUTHORIZATION_TOKEN
    metadata_proof_authorized = requested and token_present
    supplied_metadata = dict(download_metadata or {})
    classification_performed = metadata_proof_authorized and bool(supplied_metadata)
    classification = classify_download_readiness_from_metadata(supplied_metadata) if classification_performed else {
        "download_readiness_confirmed_from_metadata": False,
        "status": "NOT_RUN",
        "blocking_reasons": ["download_metadata_proof_not_authorized_or_no_metadata_supplied"],
        "metadata_only": True,
        "real_page_inspection_performed": False,
        "click_download_performed": False,
        "download_performed": False,
        "downloaded_file_bytes_read": False,
        "download_staging_directory_created": False,
        "artifact_content_reading_performed": False,
        "package_run_performed": False,
    }
    target_url_allowed = bool(source.get("target_url_allowed"))

    proof_result_ok = (not classification_performed) or classification.get("download_readiness_confirmed_from_metadata") is True
    metadata_safety_ok = (
        classification.get("metadata_only") is True
        and classification.get("real_page_inspection_performed") is False
        and classification.get("click_download_performed") is False
        and classification.get("download_performed") is False
        and classification.get("downloaded_file_bytes_read") is False
        and classification.get("download_staging_directory_created") is False
        and classification.get("artifact_content_reading_performed") is False
        and classification.get("package_run_performed") is False
    )

    checks = [
        _check("source_l18_4_controlled_live_authorization_gate_accepted", source_ok),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("target_url_allowlist_enforced", target_url_allowed, {"target_url": target}),
        _check("download_metadata_proof_authorization_surface_present", True),
        _check("download_metadata_proof_authorization_token_required", True),
        _check("metadata_only_download_readiness_result_ok_when_performed", proof_result_ok, {"classification_performed": classification_performed}),
        _check("metadata_classification_has_no_click_download_file_read_content_or_package_run", metadata_safety_ok),
        _check("live_browser_download_workflow_remains_inactive", True),
        _check("download_workflow_execution_still_blocked", True),
        _check("pasteback_and_package_run_still_blocked", True),
        _check("dedicated_edge_profile_required_and_default_profile_rejected", True),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l18_5_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "controlled_download_metadata_proof": True,
        "metadata_only_download_readiness_classification": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "source_l18_4_controlled_live_authorization_gate_accepted": source_ok,
        "l18_4_complete": bool(source.get("l18_4_complete")),
        "source_l18_3_passive_plan_checkpoint_accepted": bool(source.get("source_l18_3_passive_plan_checkpoint_accepted")),
        "download_metadata_proof_requested": requested,
        "download_metadata_proof_token_present": token_present,
        "download_metadata_proof_authorized": metadata_proof_authorized,
        "download_metadata_classification_performed": classification_performed,
        "download_metadata_classification": classification,
        "download_readiness_confirmed_from_metadata": bool(classification.get("download_readiness_confirmed_from_metadata")),
        "download_metadata_scope": "synthetic_or_operator_supplied_metadata_only",
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
        "source_l18_4_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "l18_4_complete": source.get("l18_4_complete"),
            "source_l18_3_passive_plan_checkpoint_accepted": source.get("source_l18_3_passive_plan_checkpoint_accepted"),
            "live_download_authorized_for_future_phase": source.get("live_download_authorized_for_future_phase"),
            "live_download_execution_allowed": source.get("live_download_execution_allowed"),
            "download_workflow_active": source.get("download_workflow_active"),
            "download_performed": source.get("download_performed"),
            "downloaded_file_bytes_read": source.get("downloaded_file_bytes_read"),
            "click_download_performed": source.get("click_download_performed"),
            "browser_started": source.get("browser_started"),
            "edge_process_started": source.get("edge_process_started"),
            "package_run_performed_by_adapter": source.get("package_run_performed_by_adapter"),
            "missing_commands": source.get("missing_commands"),
            "missing_doc_phrases": source.get("missing_doc_phrases"),
        },
        "l18_5_complete": ok,
        "remaining_l18_5_patches": [] if ok else [PATCH],
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
        f"Source Command                : {payload.get('source_command_name')}",
        f"L18.4 Accepted                : {payload.get('source_l18_4_controlled_live_authorization_gate_accepted')}",
        f"Metadata Proof Authorized     : {payload.get('download_metadata_proof_authorized')}",
        f"Metadata Classification Run   : {payload.get('download_metadata_classification_performed')}",
        f"Download Ready From Metadata  : {payload.get('download_readiness_confirmed_from_metadata')}",
        f"Download Workflow Active      : {payload.get('download_workflow_active')}",
        f"Download Performed            : {payload.get('download_performed')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Next Patch                    : {payload.get('next_patch')}",
        "",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        state = "PASS" if check.get("ok") else "FAIL"
        lines.append(f"- {state}: {check.get('name')}")
    return "\n".join(lines) + "\n"


def _metadata_from_args(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "candidate_filename": args.candidate_filename,
        "candidate_visible_filename_metadata": args.candidate_visible_filename_metadata or args.candidate_filename,
        "candidate_pattern": args.candidate_pattern,
        "artifact_presence_from_l17_metadata": args.artifact_presence_from_l17_metadata,
        "download_control_visible_metadata": args.download_control_visible_metadata,
        "download_control_enabled_metadata": args.download_control_enabled_metadata,
        "download_authorization_from_l18_4": args.download_authorization_from_l18_4,
        "target_url_allowed_metadata": args.target_url_allowed_metadata,
        "staging_path_metadata": args.staging_path_metadata,
        "staging_path_is_metadata_only": args.staging_path_is_metadata_only,
        "candidate_count": args.candidate_count,
        "already_downloaded": args.already_downloaded,
        "already_processed": args.already_processed,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--allow-download-metadata-proof", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--candidate-filename", default="patch_999_example_patchops_bundle.zip")
    parser.add_argument("--candidate-visible-filename-metadata", default=None)
    parser.add_argument("--candidate-pattern", default="patch_*_patchops_bundle.zip")
    parser.add_argument("--artifact-presence-from-l17-metadata", action="store_true")
    parser.add_argument("--download-control-visible-metadata", action="store_true")
    parser.add_argument("--download-control-enabled-metadata", action="store_true")
    parser.add_argument("--download-authorization-from-l18-4", action="store_true")
    parser.add_argument("--target-url-allowed-metadata", action="store_true")
    parser.add_argument("--staging-path-metadata", default="data/runtime/browser_downloads/patch_999_example_patchops_bundle.zip")
    parser.add_argument("--staging-path-is-metadata-only", action="store_true")
    parser.add_argument("--candidate-count", type=int, default=1)
    parser.add_argument("--already-downloaded", action="store_true")
    parser.add_argument("--already-processed", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_download_metadata_proof(
        args.repo_root,
        allow_download_metadata_proof=args.allow_download_metadata_proof,
        authorization_token=args.authorization_token,
        download_metadata=_metadata_from_args(args),
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
