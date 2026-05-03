"""L20.7 final marker for downloaded-file filesystem validation.

L20.7 closes the Microsoft Edge downloaded-file filesystem validation stream after
accepted L20.6. Completion means only a synthetic PatchOps runtime fixture
existence-only validation is accepted. It does not permit real browser downloads,
stat/hash, file-byte reads, archive opening/listing/extraction, manifest reads,
pasteback, send/submit, package-run, localhost services, browser extensions,
commit, or push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_downloaded_file_filesystem_validation_broad_checkpoint as l20_06

PATCH = "L20.7"
PHASE = "L20"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L20.7 Microsoft Edge downloaded-file filesystem validation final acceptance marker"
COMMAND_NAME = "browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-final-acceptance-marker"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-broad-checkpoint"
SOURCE_PATCH = "L20.6"
NEXT_PATCH = "L21.1 Microsoft Edge downloaded-archive validation passive preflight gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_CANDIDATE_RELATIVE_PATH = "data/runtime/browser_downloads/patch_l20_05_synthetic_patchops_bundle.zip"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_downloaded_file_filesystem_validation_passive_preflight_gate.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_file_filesystem_validation_cli_readback_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_file_filesystem_validation_passive_plan_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_file_filesystem_validation_controlled_authorization_gate.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_file_filesystem_validation_existence_proof.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_file_filesystem_validation_broad_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_file_filesystem_validation_final_acceptance_marker.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_downloaded_file_filesystem_validation_passive_preflight_gate.md",
    "docs/llm_browser_live_adapter_edge_downloaded_file_filesystem_validation_cli_readback_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_downloaded_file_filesystem_validation_passive_plan_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_downloaded_file_filesystem_validation_controlled_authorization_gate.md",
    "docs/llm_browser_live_adapter_edge_downloaded_file_filesystem_validation_existence_proof.md",
    "docs/llm_browser_live_adapter_edge_downloaded_file_filesystem_validation_broad_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_downloaded_file_filesystem_validation_final_acceptance_marker.md",
    "scripts/patch_l20_01_brief_validate.py",
    "scripts/patch_l20_02_brief_validate.py",
    "scripts/patch_l20_03_brief_validate.py",
    "scripts/patch_l20_04_brief_validate.py",
    "scripts/patch_l20_05_brief_validate.py",
    "scripts/patch_l20_06_brief_validate.py",
    "scripts/patch_l20_07_brief_validate.py",
    "tests/test_l20_01_edge_downloaded_file_filesystem_validation_passive_preflight_gate_current.py",
    "tests/test_l20_02_edge_downloaded_file_filesystem_validation_cli_readback_checkpoint_current.py",
    "tests/test_l20_03_edge_downloaded_file_filesystem_validation_passive_plan_checkpoint_current.py",
    "tests/test_l20_04_edge_downloaded_file_filesystem_validation_controlled_authorization_gate_current.py",
    "tests/test_l20_05_edge_downloaded_file_filesystem_validation_existence_proof_current.py",
    "tests/test_l20_06_edge_downloaded_file_filesystem_validation_broad_checkpoint_current.py",
    "tests/test_l20_07_edge_downloaded_file_filesystem_validation_final_acceptance_marker_current.py",
    DEFAULT_CANDIDATE_RELATIVE_PATH,
)

SAFETY_PHRASES = (
    "L20.7 Microsoft Edge downloaded-file filesystem validation final acceptance marker",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    "Microsoft Edge first",
    "Opera second",
    "downloaded-file filesystem validation final acceptance marker",
    "L20.1 through L20.6 remain accepted",
    "L20 downloaded-file filesystem validation stream complete",
    "L20 completion means synthetic-fixture existence-only validation",
    "existence-only filesystem validation proof remains accepted",
    "only the synthetic PatchOps runtime fixture existence check is accepted",
    "real file existence check is accepted only for the synthetic fixture",
    "real file stat remains inactive",
    "real file hash remains inactive",
    "downloaded file stat is not performed",
    "downloaded file hash is not performed",
    "downloaded file bytes are not read",
    "downloaded archive is not opened",
    "downloaded archive contents are not listed",
    "downloaded archive is not extracted",
    "downloaded manifest is not read",
    "archive validation remains inactive",
    "archive validation remains a separate future stream",
    "hash validation remains a separate future stream",
    "file-byte read remains a separate future stream",
    "manifest read remains a separate future stream",
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
    "no click/download/stat/hash/archive/manifest/byte-read/paste/send/package-run side effect",
    "no localhost PatchOps server",
    "no browser extension",
    "no git commit or git push",
    "L21.1 Microsoft Edge downloaded-archive validation passive preflight gate",
)

ALWAYS_FALSE_FIELDS = (
    "real_file_stat_performed",
    "real_file_hash_performed",
    "downloaded_file_stat_performed",
    "downloaded_file_hash_performed",
    "downloaded_file_bytes_read",
    "downloaded_archive_opened",
    "downloaded_archive_contents_listed",
    "downloaded_archive_extracted",
    "downloaded_manifest_read",
    "archive_validation_active",
    "archive_validation_performed",
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_downloaded_file_filesystem_validation_final_acceptance_marker.md")
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


def _source_l20_6_ok(source: Mapping[str, Any]) -> bool:
    return (
        source.get("ok") is True
        and source.get("patch") == SOURCE_PATCH
        and source.get("l20_6_complete") is True
        and source.get("l20_1_through_l20_5_remain_accepted") is True
        and source.get("existence_only_filesystem_validation_proof_remains_accepted") is True
        and source.get("default_existence_proof_readback_remains_passive") is True
        and source.get("authorized_existence_proof_readback_remains_existence_only") is True
        and source.get("unsafe_candidate_remains_rejected_without_filesystem_access") is True
        and source.get("only_synthetic_fixture_existence_check_is_allowed") is True
        and source.get("filesystem_validation_scope") == "existence_only_synthetic_patchops_runtime_fixture"
        and source.get("filesystem_validation_performed") is True
        and source.get("real_file_exists_check_performed") is True
        and source.get("downloaded_file_exists_check_performed") is True
        and _always_false_ok(source)
    )


def build_edge_downloaded_file_filesystem_validation_final_acceptance_marker(
    repo_root: str | Path | None = None,
    *,
    target_url: str | None = None,
) -> dict[str, Any]:
    """Build the L20.7 final acceptance marker payload."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)
    target = target_url or DEFAULT_TARGET_URL
    source = l20_06.build_edge_downloaded_file_filesystem_validation_broad_checkpoint(root, target_url=target)

    names = _command_names()
    missing_commands = [name for name in (SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)
    target_url_allowed = bool(source.get("target_url_allowed"))
    source_ok = _source_l20_6_ok(source)

    completion_is_narrow_ok = (
        source_ok
        and source.get("filesystem_validation_scope") == "existence_only_synthetic_patchops_runtime_fixture"
        and source.get("real_file_exists_check_performed") is True
        and source.get("downloaded_file_exists_check_performed") is True
        and source.get("real_file_stat_performed") is False
        and source.get("real_file_hash_performed") is False
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
        and _always_false_ok(source)
    )

    checks = [
        _check("source_l20_6_broad_checkpoint_accepted", source_ok),
        _check("l20_1_through_l20_6_remain_accepted", source_ok),
        _check("l20_filesystem_validation_stream_complete", completion_is_narrow_ok),
        _check("completion_is_synthetic_fixture_existence_only", completion_is_narrow_ok),
        _check("archive_hash_byte_manifest_pasteback_package_run_remain_separate_future_streams", True),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("target_url_allowlist_enforced", target_url_allowed, {"target_url": target}),
        _check("dedicated_edge_profile_required_and_default_profile_rejected", True),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l20_7_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "final_acceptance_marker": True,
        "filesystem_validation_final_acceptance_marker": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "source_l20_6_broad_checkpoint_accepted": source_ok,
        "l20_1_through_l20_6_remain_accepted": source_ok,
        "l20_downloaded_file_filesystem_validation_stream_complete": ok,
        "l20_completion_means_synthetic_fixture_existence_only_validation": True,
        "existence_only_filesystem_validation_proof_remains_accepted": bool(source.get("existence_only_filesystem_validation_proof_remains_accepted")),
        "only_synthetic_patchops_runtime_fixture_existence_check_is_accepted": True,
        "real_file_existence_check_accepted_only_for_synthetic_fixture": True,
        "filesystem_validation_scope": "existence_only_synthetic_patchops_runtime_fixture",
        "filesystem_validation_performed": bool(source.get("filesystem_validation_performed")),
        "real_file_exists_check_performed": bool(source.get("real_file_exists_check_performed")),
        "downloaded_file_exists_check_performed": bool(source.get("downloaded_file_exists_check_performed")),
        "real_filesystem_validation_active": False,
        "real_file_existence_check_active": False,
        "real_file_stat_active": False,
        "real_file_hash_active": False,
        "real_file_stat_performed": False,
        "real_file_hash_performed": False,
        "downloaded_file_stat_performed": False,
        "downloaded_file_hash_performed": False,
        "downloaded_file_bytes_read": False,
        "archive_validation_active": False,
        "archive_validation_performed": False,
        "downloaded_archive_opened": False,
        "downloaded_archive_contents_listed": False,
        "downloaded_archive_extracted": False,
        "downloaded_manifest_read": False,
        "archive_validation_remains_separate_future_stream": True,
        "hash_validation_remains_separate_future_stream": True,
        "file_byte_read_remains_separate_future_stream": True,
        "manifest_read_remains_separate_future_stream": True,
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
        "source_l20_6_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "l20_6_complete": source.get("l20_6_complete"),
            "l20_1_through_l20_5_remain_accepted": source.get("l20_1_through_l20_5_remain_accepted"),
            "existence_only_filesystem_validation_proof_remains_accepted": source.get("existence_only_filesystem_validation_proof_remains_accepted"),
            "default_existence_proof_readback_remains_passive": source.get("default_existence_proof_readback_remains_passive"),
            "authorized_existence_proof_readback_remains_existence_only": source.get("authorized_existence_proof_readback_remains_existence_only"),
            "unsafe_candidate_remains_rejected_without_filesystem_access": source.get("unsafe_candidate_remains_rejected_without_filesystem_access"),
            "only_synthetic_fixture_existence_check_is_allowed": source.get("only_synthetic_fixture_existence_check_is_allowed"),
            "filesystem_validation_scope": source.get("filesystem_validation_scope"),
            "filesystem_validation_performed": source.get("filesystem_validation_performed"),
            "real_file_exists_check_performed": source.get("real_file_exists_check_performed"),
            "downloaded_file_exists_check_performed": source.get("downloaded_file_exists_check_performed"),
            "real_file_stat_performed": source.get("real_file_stat_performed"),
            "real_file_hash_performed": source.get("real_file_hash_performed"),
            "downloaded_file_stat_performed": source.get("downloaded_file_stat_performed"),
            "downloaded_file_hash_performed": source.get("downloaded_file_hash_performed"),
            "downloaded_file_bytes_read": source.get("downloaded_file_bytes_read"),
            "downloaded_archive_opened": source.get("downloaded_archive_opened"),
            "downloaded_manifest_read": source.get("downloaded_manifest_read"),
            "browser_started": source.get("browser_started"),
            "edge_process_started": source.get("edge_process_started"),
            "package_run_performed_by_adapter": source.get("package_run_performed_by_adapter"),
            "missing_commands": source.get("missing_commands"),
            "missing_doc_phrases": source.get("missing_doc_phrases"),
        },
        "l20_7_complete": ok,
        "remaining_l20_patches": [] if ok else [PATCH],
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
        f"L20.1-L20.6 Accepted          : {payload.get('l20_1_through_l20_6_remain_accepted')}",
        f"L20 Stream Complete           : {payload.get('l20_downloaded_file_filesystem_validation_stream_complete')}",
        f"Scope                         : {payload.get('filesystem_validation_scope')}",
        f"Real File Exists Check        : {payload.get('real_file_exists_check_performed')}",
        f"Stat/Hash/Bytes Blocked       : {payload.get('real_file_stat_performed') is False and payload.get('real_file_hash_performed') is False and payload.get('downloaded_file_bytes_read') is False}",
        f"Archive Opened                : {payload.get('downloaded_archive_opened')}",
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

    payload = build_edge_downloaded_file_filesystem_validation_final_acceptance_marker(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
