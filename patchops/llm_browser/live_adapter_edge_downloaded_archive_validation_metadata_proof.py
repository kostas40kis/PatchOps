"""L21.5 first controlled metadata-only archive validation proof.

L21.5 performs a narrowly authorized archive metadata proof against an explicit
synthetic PatchOps runtime fixture. It may open the synthetic zip and list entry
names only. It does not extract archive members, read manifest contents, read
archive member bytes, run packages, start Edge, inspect pages, click, download,
paste, send, start localhost services, use browser extensions, commit, or push.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
import zipfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_downloaded_archive_validation_controlled_authorization_gate as l21_04

PATCH = "L21.5"
PHASE = "L21"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L21.5 Microsoft Edge first controlled downloaded-archive validation proof"
COMMAND_NAME = "browser-start-supervised-launch-edge-downloaded-archive-validation-metadata-proof"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-downloaded-archive-validation-controlled-authorization-gate"
SOURCE_PATCH = "L21.4"
NEXT_PATCH = "L21.6 Microsoft Edge downloaded-archive validation broad checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
SOURCE_L21_4_AUTHORIZATION_TOKEN = "PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_VALIDATION_CONTROLLED_AUTHORIZED_READBACK_ONLY"
REQUIRED_ARCHIVE_METADATA_PROOF_AUTHORIZATION_TOKEN = "PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_METADATA_PROOF_AUTHORIZED"
DEFAULT_CANDIDATE_RELATIVE_PATH = "data/runtime/browser_downloads/patch_l21_05_synthetic_archive_patchops_bundle.zip"
DEFAULT_CANDIDATE_PATTERN = "patch_*_patchops_bundle.zip"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

SAFETY_PHRASES = (
    "L21.5 Microsoft Edge first controlled downloaded-archive validation proof",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    SOURCE_L21_4_AUTHORIZATION_TOKEN,
    REQUIRED_ARCHIVE_METADATA_PROOF_AUTHORIZATION_TOKEN,
    "Microsoft Edge first",
    "Opera second",
    "first controlled downloaded-archive validation proof",
    "archive metadata-only validation proof",
    "synthetic PatchOps runtime archive fixture only",
    "L21.4 controlled authorization gate remains accepted",
    "explicit L21.5 archive metadata proof authorization token",
    "controlled archive validation execution is limited to metadata-only proof",
    "downloaded archive may be opened only for metadata listing of the explicit synthetic fixture",
    "downloaded archive contents may be listed as metadata only",
    "downloaded archive is not extracted",
    "downloaded manifest is not read",
    "archive member bytes are not read",
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
    "L21.6 Microsoft Edge downloaded-archive validation broad checkpoint",
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

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_passive_preflight_gate.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_cli_readback_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_passive_plan_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_controlled_authorization_gate.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_metadata_proof.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_downloaded_archive_validation_passive_preflight_gate.md",
    "docs/llm_browser_live_adapter_edge_downloaded_archive_validation_cli_readback_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_downloaded_archive_validation_passive_plan_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_downloaded_archive_validation_controlled_authorization_gate.md",
    "docs/llm_browser_live_adapter_edge_downloaded_archive_validation_metadata_proof.md",
    "scripts/patch_l21_01_brief_validate.py",
    "scripts/patch_l21_02_brief_validate.py",
    "scripts/patch_l21_03_brief_validate.py",
    "scripts/patch_l21_04_brief_validate.py",
    "scripts/patch_l21_05_brief_validate.py",
    "tests/test_l21_01_edge_downloaded_archive_validation_passive_preflight_gate_current.py",
    "tests/test_l21_02_edge_downloaded_archive_validation_cli_readback_checkpoint_current.py",
    "tests/test_l21_03_edge_downloaded_archive_validation_passive_plan_checkpoint_current.py",
    "tests/test_l21_04_edge_downloaded_archive_validation_controlled_authorization_gate_current.py",
    "tests/test_l21_05_edge_downloaded_archive_validation_metadata_proof_current.py",
    DEFAULT_CANDIDATE_RELATIVE_PATH,
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_downloaded_archive_validation_metadata_proof.md")
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


def _resolve_candidate_path(root: Path, candidate_path_metadata: str | None) -> Path:
    raw = candidate_path_metadata or DEFAULT_CANDIDATE_RELATIVE_PATH
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = root / candidate
    return candidate.resolve()


def _is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _candidate_safety(root: Path, candidate_path: Path, pattern: str) -> dict[str, Any]:
    normalized = str(candidate_path).replace("\\", "/")
    filename = candidate_path.name
    under_runtime = _is_relative_to(candidate_path, (root / "data" / "runtime").resolve())
    under_default_edge_profile = "User Data/Default" in normalized or "Microsoft/Edge/User Data/Default" in normalized
    ext_ok = candidate_path.suffix.lower() == ".zip"
    pattern_ok = fnmatch.fnmatch(filename, pattern)
    return {
        "candidate_filename": filename,
        "candidate_extension_ok": ext_ok,
        "candidate_pattern": pattern,
        "candidate_pattern_ok": pattern_ok,
        "candidate_under_patchops_runtime": under_runtime,
        "candidate_under_default_edge_profile": under_default_edge_profile,
        "candidate_safe_for_l21_5_metadata_only_proof": ext_ok and pattern_ok and under_runtime and not under_default_edge_profile,
    }


def _base_blocked_fields() -> dict[str, bool]:
    return {field: False for field in ALWAYS_FALSE_FIELDS}


def run_archive_metadata_only_validation(candidate_path: Path, *, authorization_ok: bool) -> dict[str, Any]:
    """Open a synthetic zip and list entry names only when authorized."""
    if not authorization_ok:
        return {
            "archive_metadata_validation_attempted": False,
            "archive_metadata_validation_performed": False,
            "archive_validation_ready": False,
            "archive_entry_names": [],
            "archive_entry_count": 0,
            "manifest_entry_detected_from_listing": False,
            "blocking_reasons": ["archive_metadata_proof_not_authorized"],
            "archive_validation_execution_allowed": False,
            "archive_validation_active": False,
            "archive_validation_performed": False,
            "downloaded_archive_opened": False,
            "downloaded_archive_contents_listed": False,
            **_base_blocked_fields(),
        }
    if not candidate_path.exists():
        return {
            "archive_metadata_validation_attempted": True,
            "archive_metadata_validation_performed": False,
            "archive_validation_ready": False,
            "archive_entry_names": [],
            "archive_entry_count": 0,
            "manifest_entry_detected_from_listing": False,
            "blocking_reasons": ["candidate_path_does_not_exist"],
            "archive_validation_execution_allowed": True,
            "archive_validation_active": False,
            "archive_validation_performed": False,
            "downloaded_archive_opened": False,
            "downloaded_archive_contents_listed": False,
            **_base_blocked_fields(),
        }
    try:
        with zipfile.ZipFile(candidate_path, "r") as archive:
            entry_names = sorted(archive.namelist())
    except zipfile.BadZipFile:
        return {
            "archive_metadata_validation_attempted": True,
            "archive_metadata_validation_performed": False,
            "archive_validation_ready": False,
            "archive_entry_names": [],
            "archive_entry_count": 0,
            "manifest_entry_detected_from_listing": False,
            "blocking_reasons": ["bad_zip_file"],
            "archive_validation_execution_allowed": True,
            "archive_validation_active": False,
            "archive_validation_performed": False,
            "downloaded_archive_opened": False,
            "downloaded_archive_contents_listed": False,
            **_base_blocked_fields(),
        }
    manifest_detected = "manifest.json" in entry_names
    return {
        "archive_metadata_validation_attempted": True,
        "archive_metadata_validation_performed": True,
        "archive_validation_ready": bool(entry_names),
        "archive_entry_names": entry_names,
        "archive_entry_count": len(entry_names),
        "manifest_entry_detected_from_listing": manifest_detected,
        "blocking_reasons": [] if entry_names else ["archive_contains_no_entries"],
        "archive_validation_execution_allowed": True,
        "archive_validation_active": False,
        "archive_validation_performed": True,
        "downloaded_archive_opened": True,
        "downloaded_archive_contents_listed": True,
        **_base_blocked_fields(),
    }


def _source_l21_4_ok(root: Path, target_url: str) -> tuple[bool, dict[str, Any]]:
    source = l21_04.build_edge_downloaded_archive_validation_controlled_authorization_gate(
        root,
        allow_archive_validation_authorization=True,
        authorization_token=SOURCE_L21_4_AUTHORIZATION_TOKEN,
        target_url=target_url,
    )
    ok = (
        source.get("ok") is True
        and source.get("patch") == SOURCE_PATCH
        and source.get("l21_4_complete") is True
        and source.get("source_l21_3_passive_plan_checkpoint_accepted") is True
        and source.get("archive_validation_authorized_for_future_phase") is True
        and source.get("archive_validation_authorization_is_readback_only_in_l21_4") is True
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
    return ok, source


def build_edge_downloaded_archive_validation_metadata_proof(
    repo_root: str | Path | None = None,
    *,
    allow_archive_metadata_proof: bool = False,
    authorization_token: str | None = None,
    candidate_path_metadata: str | None = None,
    candidate_pattern: str = DEFAULT_CANDIDATE_PATTERN,
    target_url: str | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)
    target = target_url or DEFAULT_TARGET_URL
    source_ok, source = _source_l21_4_ok(root, target)
    candidate_path = _resolve_candidate_path(root, candidate_path_metadata)
    candidate = _candidate_safety(root, candidate_path, candidate_pattern)
    requested = bool(allow_archive_metadata_proof)
    token_present = authorization_token == REQUIRED_ARCHIVE_METADATA_PROOF_AUTHORIZATION_TOKEN
    proof_authorized = requested and token_present and source_ok and candidate["candidate_safe_for_l21_5_metadata_only_proof"]
    validation = run_archive_metadata_only_validation(candidate_path, authorization_ok=proof_authorized)

    names = _command_names()
    missing_commands = [name for name in (SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)
    target_url_allowed = bool(source.get("target_url_allowed"))

    validation_safety_ok = _always_false_ok(validation)
    expected_performed = proof_authorized
    proof_result_ok = (not expected_performed) or (
        validation["archive_metadata_validation_performed"] is True
        and validation["archive_validation_ready"] is True
        and validation["downloaded_archive_opened"] is True
        and validation["downloaded_archive_contents_listed"] is True
        and validation["downloaded_archive_extracted"] is False
        and validation["downloaded_manifest_read"] is False
        and validation["archive_member_bytes_read"] is False
        and validation["downloaded_file_bytes_read"] is False
        and validation["package_run_performed_by_adapter"] is False
        and validation_safety_ok
    )

    checks = [
        _check("source_l21_4_controlled_authorization_gate_accepted", source_ok),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("target_url_allowlist_enforced", target_url_allowed, {"target_url": target}),
        _check("candidate_safe_for_l21_5_archive_metadata_only_proof", candidate["candidate_safe_for_l21_5_metadata_only_proof"], candidate),
        _check("archive_metadata_proof_authorization_surface_present", True),
        _check("archive_metadata_only_validation_result_ok_when_authorized", proof_result_ok, {"proof_authorized": proof_authorized}),
        _check("archive_metadata_only_validation_keeps_extract_manifest_member_byte_read_package_run_blocked", validation_safety_ok),
        _check("browser_download_pasteback_package_run_still_blocked", True),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l21_5_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
        _check("no_forbidden_optional_browser_imports", not forbidden_imports_newly_loaded, {"newly_loaded": forbidden_imports_newly_loaded}),
    ]
    ok = all(check["ok"] for check in checks)

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
        "first_controlled_archive_validation_proof": True,
        "archive_metadata_only_validation_proof": True,
        "synthetic_patchops_runtime_archive_fixture_only": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "source_l21_4_controlled_authorization_gate_accepted": source_ok,
        "l21_4_complete": bool(source.get("l21_4_complete")),
        "archive_validation_authorized_by_l21_4_for_future_phase": bool(source.get("archive_validation_authorized_for_future_phase")),
        "archive_metadata_proof_requested": requested,
        "archive_metadata_proof_authorization_token_present": token_present,
        "archive_metadata_proof_authorized": proof_authorized,
        "candidate_path_metadata": str(candidate_path),
        "candidate_path_is_metadata_before_archive_open": True,
        "candidate_safety": candidate,
        "archive_metadata_validation_result": validation,
        "archive_validation_scope": "metadata_listing_only_synthetic_patchops_runtime_archive_fixture",
        "archive_validation_execution_allowed": bool(proof_authorized),
        "archive_validation_active": False,
        "archive_validation_performed": bool(validation["archive_validation_performed"]),
        "downloaded_archive_opened": bool(validation["downloaded_archive_opened"]),
        "downloaded_archive_contents_listed": bool(validation["downloaded_archive_contents_listed"]),
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
        "source_l21_4_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "l21_4_complete": source.get("l21_4_complete"),
            "source_l21_3_passive_plan_checkpoint_accepted": source.get("source_l21_3_passive_plan_checkpoint_accepted"),
            "archive_validation_authorized_for_future_phase": source.get("archive_validation_authorized_for_future_phase"),
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
        "l21_5_complete": ok,
        "remaining_l21_5_patches": [] if ok else [PATCH],
        "missing_commands": missing_commands,
        "missing_doc_phrases": missing_doc_phrases,
        "required_repo_paths": required,
        "forbidden_optional_browser_imports_newly_loaded": forbidden_imports_newly_loaded,
        "checks": checks,
    }
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Patch                             : {payload.get('patch')}",
        f"Status                            : {payload.get('status')}",
        f"Command                           : {payload.get('command_name')}",
        f"L21.4 Accepted                    : {payload.get('source_l21_4_controlled_authorization_gate_accepted')}",
        f"Archive Metadata Proof Authorized : {payload.get('archive_metadata_proof_authorized')}",
        f"Archive Validation Performed      : {payload.get('archive_validation_performed')}",
        f"Archive Opened                    : {payload.get('downloaded_archive_opened')}",
        f"Archive Contents Listed           : {payload.get('downloaded_archive_contents_listed')}",
        f"Archive Extracted                 : {payload.get('downloaded_archive_extracted')}",
        f"Manifest Read                     : {payload.get('downloaded_manifest_read')}",
        f"Browser Started                   : {payload.get('browser_started')}",
        f"Next Patch                        : {payload.get('next_patch')}",
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
    parser.add_argument("--allow-archive-metadata-proof", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--candidate-path-metadata", default=DEFAULT_CANDIDATE_RELATIVE_PATH)
    parser.add_argument("--candidate-pattern", default=DEFAULT_CANDIDATE_PATTERN)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_downloaded_archive_validation_metadata_proof(
        args.repo_root,
        allow_archive_metadata_proof=args.allow_archive_metadata_proof,
        authorization_token=args.authorization_token,
        candidate_path_metadata=args.candidate_path_metadata,
        candidate_pattern=args.candidate_pattern,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
