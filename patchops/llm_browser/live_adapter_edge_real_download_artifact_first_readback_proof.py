"""L25.36 first controlled real downloaded artifact readback proof.

This follows accepted L25.35. It is the first proof that opens and reads a
controlled artifact file from the browser-download runtime area. The proof reads
artifact bytes, computes SHA-256, and lists ZIP member names only.

It does not start a browser, trigger a browser download, extract an archive,
read a manifest member, execute a package, invoke PatchOps run-package, paste or
send content, start localhost, use Selenium/CDP/DOM scraping, commit, or push.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence
import zipfile

PATCH = "L25.36"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.36 Microsoft Edge controlled runtime real-download artifact first readback proof"
SOURCE_PATCH = "L25.35"
NEXT_PATCH = "L25.37 Microsoft Edge controlled runtime real-download artifact manifest member readback gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_CONTROLLED_ARTIFACT_RELATIVE_PATH = "data/runtime/browser_downloads/l25_36_real_artifact/future_real_downloaded_package.zip"
REQUIRED_REAL_DOWNLOAD_ARTIFACT_READBACK_TOKEN = "PATCHOPS_L25_EDGE_REAL_DOWNLOAD_ARTIFACT_FIRST_READBACK_AUTHORIZED"
EXPECTED_PACKAGE_RUN_SCOPE = "controlled_runtime_package_run_only_supported_bundle_shape_synthetic_launcher_no_browser_no_pasteback_no_real_artifact"
MAX_ARTIFACT_BYTES = 262144
REQUIRED_MEMBER_NAMES = ("bundle/run_with_patchops.ps1", "bundle/bundle_meta.json", "bundle/README.txt", "bundle/manifest.json", "bundle/content/.keep")

FALSE_FIELDS = (
    "real_downloaded_manifest_read",
    "real_downloaded_manifest_member_opened",
    "real_downloaded_manifest_bytes_read",
    "real_downloaded_manifest_json_parsed",
    "real_archive_candidate_extracted",
    "adapter_archive_extraction_performed",
    "archive_member_extracted_to_project",
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
    "localhost_server_started",
    "browser_extension_used",
    "package_manifest_used_for_execution",
    "package_execution_allowed",
    "package_run_performed_by_adapter",
    "package_run",
    "patchops_cli_run_package_invoked_for_real_artifact",
    "git_commit_performed",
    "git_push_performed",
)


def _first(payload: Mapping[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in payload:
            return payload.get(name)
    return default


def _normalize_l25_35_source(source_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(source_payload or {})
    return {
        "ok": source.get("ok"),
        "patch": source.get("patch"),
        "authorization_gate": _first(source, "authorization_gate", "real_download_artifact_authorization_gate"),
        "authorization_readback_only": _first(source, "authorization_readback_only", "real_download_artifact_authorization_readback_only"),
        "future_authorized": _first(source, "authorized_summary_shape", "real_download_artifact_authorization_granted_for_future_patch"),
        "source_l25_34_final_acceptance": _first(source, "source_l25_34_final_acceptance", "accepted_controlled_package_run_ladder_final_acceptance"),
        "accepted_package_run_scope": source.get("accepted_package_run_scope"),
        "real_downloaded_artifact_read": source.get("real_downloaded_artifact_read", False),
        "real_downloaded_artifact_path_opened": source.get("real_downloaded_artifact_path_opened", False),
        "real_downloaded_artifact_bytes_read": source.get("real_downloaded_artifact_bytes_read", False),
        "real_archive_candidate_extracted": source.get("real_archive_candidate_extracted", False),
        "browser_started": source.get("browser_started", False),
        "package_execution_allowed": source.get("package_execution_allowed", False),
        "package_run": source.get("package_run", False),
        "pasteback": _first(source, "pasteback", "pasteback_workflow_active", default=False),
        "git_commit_performed": source.get("git_commit_performed", False),
        "git_push_performed": source.get("git_push_performed", False),
    }


def _artifact_under_runtime(root: Path, artifact_path: Path) -> bool:
    try:
        artifact_resolved = artifact_path.resolve()
        base = (root / "data" / "runtime" / "browser_downloads" / "l25_36_real_artifact").resolve()
        return str(artifact_resolved).startswith(str(base))
    except OSError:
        return False


def _read_artifact_summary(artifact_path: Path) -> dict[str, Any]:
    data = artifact_path.read_bytes()
    names: list[str] = []
    zip_ok = False
    try:
        with zipfile.ZipFile(artifact_path, "r") as archive:
            names = sorted(archive.namelist())
            zip_ok = True
    except zipfile.BadZipFile:
        names = []
        zip_ok = False
    return {
        "byte_count": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "zip_opened_for_member_names_only": zip_ok,
        "zip_member_names": names,
        "required_member_names_present": all(name in names for name in REQUIRED_MEMBER_NAMES),
    }


def build_real_download_artifact_first_readback_proof(
    repo_root: str | Path | None = None,
    *,
    source_payload: Mapping[str, Any] | None = None,
    allow_real_download_artifact_readback: bool = False,
    authorization_token: str | None = None,
    candidate_artifact_path: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    source = _normalize_l25_35_source(source_payload)
    artifact_path = Path(candidate_artifact_path) if candidate_artifact_path else root / DEFAULT_CONTROLLED_ARTIFACT_RELATIVE_PATH
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_REAL_DOWNLOAD_ARTIFACT_READBACK_TOKEN
    source_ok = bool(
        source.get("ok") is True
        and source.get("patch") == "L25.35"
        and source.get("authorization_gate") is True
        and source.get("authorization_readback_only") is True
        and source.get("future_authorized") is True
        and source.get("source_l25_34_final_acceptance") is True
        and source.get("accepted_package_run_scope") == EXPECTED_PACKAGE_RUN_SCOPE
        and source.get("real_downloaded_artifact_read") is False
        and source.get("real_downloaded_artifact_path_opened") is False
        and source.get("real_downloaded_artifact_bytes_read") is False
        and source.get("real_archive_candidate_extracted") is False
        and source.get("browser_started") is False
        and source.get("package_execution_allowed") is False
        and source.get("package_run") is False
        and source.get("pasteback") is False
        and source.get("git_commit_performed") is False
        and source.get("git_push_performed") is False
    )
    artifact_allowed = bool(
        source_ok
        and allow_real_download_artifact_readback
        and token_valid
        and artifact_path.exists()
        and artifact_path.is_file()
        and artifact_path.suffix.lower() == ".zip"
        and _artifact_under_runtime(root, artifact_path)
        and artifact_path.stat().st_size <= MAX_ARTIFACT_BYTES
    )

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_35_payload_ok", "ok": source_ok},
        {"name": "readback_token_present", "ok": token_present},
        {"name": "readback_token_valid", "ok": token_valid},
        {"name": "candidate_artifact_exists", "ok": artifact_path.exists()},
        {"name": "candidate_artifact_is_file", "ok": artifact_path.is_file()},
        {"name": "candidate_artifact_suffix_zip", "ok": artifact_path.suffix.lower() == ".zip"},
        {"name": "candidate_artifact_under_l25_36_runtime_downloads", "ok": _artifact_under_runtime(root, artifact_path)},
        {"name": "candidate_artifact_size_bounded", "ok": artifact_path.exists() and artifact_path.stat().st_size <= MAX_ARTIFACT_BYTES},
    ]

    artifact_summary: dict[str, Any] = {}
    if artifact_allowed:
        artifact_summary = _read_artifact_summary(artifact_path)
        checks.extend([
            {"name": "real_downloaded_artifact_path_opened", "ok": True},
            {"name": "real_downloaded_artifact_bytes_read", "ok": artifact_summary.get("byte_count", 0) > 0},
            {"name": "real_downloaded_artifact_hash_computed", "ok": isinstance(artifact_summary.get("sha256"), str) and len(artifact_summary.get("sha256", "")) == 64},
            {"name": "artifact_zip_opened_for_member_names_only", "ok": artifact_summary.get("zip_opened_for_member_names_only") is True},
            {"name": "required_member_names_present_without_extraction", "ok": artifact_summary.get("required_member_names_present") is True},
        ])

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "first_real_download_artifact_readback_proof": True,
        "source_l25_35_summary": source,
        "artifact_readback_requested": bool(allow_real_download_artifact_readback or token_present),
        "artifact_readback_token_present": token_present,
        "artifact_readback_token_valid": token_valid,
        "artifact_readback_allowed": artifact_allowed,
        "candidate_artifact_path": str(artifact_path),
        "candidate_artifact_relative_path": DEFAULT_CONTROLLED_ARTIFACT_RELATIVE_PATH,
        "candidate_artifact_under_runtime_downloads": _artifact_under_runtime(root, artifact_path),
        "candidate_artifact_size_bounded": artifact_path.exists() and artifact_path.stat().st_size <= MAX_ARTIFACT_BYTES,
        "real_downloaded_artifact_read": artifact_allowed,
        "real_downloaded_artifact_path_opened": artifact_allowed,
        "real_downloaded_artifact_bytes_read": artifact_allowed and artifact_summary.get("byte_count", 0) > 0,
        "real_downloaded_artifact_byte_count": artifact_summary.get("byte_count"),
        "real_downloaded_artifact_hash_computed": artifact_allowed and isinstance(artifact_summary.get("sha256"), str),
        "real_downloaded_artifact_sha256": artifact_summary.get("sha256"),
        "artifact_zip_opened_for_member_names_only": artifact_summary.get("zip_opened_for_member_names_only") is True,
        "artifact_zip_member_names_read": artifact_summary.get("zip_opened_for_member_names_only") is True,
        "artifact_zip_member_names": artifact_summary.get("zip_member_names", []),
        "artifact_required_member_names_present": artifact_summary.get("required_member_names_present") is True,
        "real_downloaded_manifest_read": False,
        "real_downloaded_manifest_member_opened": False,
        "real_downloaded_manifest_bytes_read": False,
        "real_downloaded_manifest_json_parsed": False,
        "real_archive_candidate_extracted": False,
        "adapter_archive_extraction_performed": False,
        "package_manifest_used_for_execution": False,
        "package_execution_allowed": False,
        "package_run": False,
        "patchops_cli_run_package_invoked_for_real_artifact": False,
        "no_browser_permission_added_by_l25_36": True,
        "no_download_permission_added_by_l25_36": True,
        "no_manifest_read_permission_added_by_l25_36": True,
        "no_archive_extraction_permission_added_by_l25_36": True,
        "no_package_execution_permission_added_by_l25_36": True,
        "no_pasteback_permission_added_by_l25_36": True,
        "no_git_permission_added_by_l25_36": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
    }
    for field in FALSE_FIELDS:
        if field not in payload:
            payload[field] = False
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    return "\n".join([
        NAME,
        "=" * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Status                        : {payload.get('status')}",
        f"Artifact Read                 : {payload.get('real_downloaded_artifact_read')}",
        f"Bytes Read                    : {payload.get('real_downloaded_artifact_byte_count')}",
        f"Hash Computed                 : {payload.get('real_downloaded_artifact_hash_computed')}",
        f"Manifest Read                 : {payload.get('real_downloaded_manifest_read')}",
        f"Archive Extracted             : {payload.get('real_archive_candidate_extracted')}",
        f"Package Run                   : {payload.get('package_run')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Next Patch                    : {payload.get('next_patch')}",
    ]) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--source-payload-json", default=None)
    parser.add_argument("--allow-real-download-artifact-readback", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--candidate-artifact-path", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    source_payload = json.loads(args.source_payload_json) if args.source_payload_json else None
    payload = build_real_download_artifact_first_readback_proof(
        args.repo_root,
        source_payload=source_payload,
        allow_real_download_artifact_readback=args.allow_real_download_artifact_readback,
        authorization_token=args.authorization_token,
        candidate_artifact_path=args.candidate_artifact_path,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
