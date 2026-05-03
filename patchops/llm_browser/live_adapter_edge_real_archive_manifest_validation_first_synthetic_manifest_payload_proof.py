"""L23.7 first synthetic manifest payload proof.

This module follows accepted L23.6. It reads only the manifest.json payload from
the fixed synthetic archive fixture after explicit token authorization. It does
not read non-manifest member payloads, extract files, touch real downloaded
artifacts, start a browser, paste, send, or run packages.
"""
from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_validation_synthetic_manifest_payload_authorization_gate as l23_06

PATCH = "L23.7"
PHASE = "L23"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L23.7 Microsoft Edge real downloaded-archive manifest validation first synthetic manifest payload proof"
SOURCE_PATCH = "L23.6"
NEXT_PATCH = "L23.8 Microsoft Edge real downloaded-archive manifest validation synthetic payload broad checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_SYNTHETIC_ARCHIVE_RELATIVE_PATH = "data/runtime/browser_downloads/patch_l23_04_synthetic_archive_listing_fixture/patch_l23_04_synthetic_archive.zip"
REQUIRED_SYNTHETIC_MANIFEST_PAYLOAD_PROOF_TOKEN = "PATCHOPS_L23_EDGE_FIRST_SYNTHETIC_MANIFEST_PAYLOAD_PROOF_AUTHORIZED"
EXPECTED_MANIFEST_MEMBER_NAME = "manifest.json"
EXPECTED_SYNTHETIC_MANIFEST_PATCH_NAME = "l23_07_synthetic_manifest_payload_fixture"

ALWAYS_FALSE_FIELDS = (
    "non_manifest_member_bytes_read",
    "non_manifest_member_payload_read",
    "readme_member_payload_read",
    "downloaded_archive_extracted",
    "archive_extracted",
    "real_archive_manifest_read",
    "real_downloaded_manifest_read",
    "real_archive_opened",
    "real_downloaded_artifact_read",
    "downloaded_file_bytes_read",
    "downloaded_file_stat_performed",
    "downloaded_file_hash_performed",
    "candidate_archive_path_stat_performed",
    "candidate_archive_path_hash_performed",
    "synthetic_archive_hash_performed",
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


def _l23_06_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l23_06.build_synthetic_manifest_payload_authorization_gate(
            repo_root,
            allow_synthetic_manifest_payload_authorization=True,
            authorization_token=l23_06.REQUIRED_SYNTHETIC_MANIFEST_PAYLOAD_AUTHORIZATION_TOKEN,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L23.6 payload authorization readback failed: {type(exc).__name__}: {exc}"}


def _default_payload(root: Path, target_url: str) -> dict[str, Any]:
    source = _l23_06_authorized_payload(root, target_url)
    checks = [
        {"name": "source_l23_06_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l23_06_future_payload_authorized", "ok": source.get("synthetic_manifest_payload_authorization_granted_for_future_patch") is True},
        {"name": "source_l23_06_payload_execution_false", "ok": source.get("synthetic_manifest_payload_read_execution_allowed") is False},
        {"name": "default_payload_proof_is_passive", "ok": True},
    ]
    payload: dict[str, Any] = {
        "ok": bool(all(check.get("ok") for check in checks)),
        "status": STATUS_PASS if all(check.get("ok") for check in checks) else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l23_06_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_payload_authorized": source.get("synthetic_manifest_payload_authorization_granted_for_future_patch"),
            "payload_execution_allowed": source.get("synthetic_manifest_payload_read_execution_allowed"),
            "manifest_member_payload_read": source.get("manifest_member_payload_read"),
            "archive_member_bytes_read": source.get("archive_member_bytes_read"),
            "archive_extracted": source.get("archive_extracted"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "synthetic_manifest_payload_proof_requested": False,
        "synthetic_manifest_payload_proof_token_present": False,
        "synthetic_manifest_payload_proof_token_valid": False,
        "synthetic_manifest_payload_read_execution_allowed": False,
        "synthetic_manifest_payload_read_active": False,
        "synthetic_manifest_payload_read_performed": False,
        "synthetic_manifest_member_name": None,
        "synthetic_manifest_payload_size_bytes": 0,
        "synthetic_manifest_payload_sha256_performed": False,
        "synthetic_manifest_json_parsed": False,
        "synthetic_manifest_shape_validated": False,
        "synthetic_manifest_patch_name": None,
        "synthetic_manifest_scope": "default_readback_only_no_payload_read",
        "manifest_member_bytes_read": False,
        "manifest_member_payload_read": False,
        "manifest_member_content_read": False,
        "archive_member_bytes_read": False,
        "archive_member_payload_read": False,
        "archive_member_content_read": False,
        "synthetic_archive_opened": False,
        "synthetic_archive_contents_listed": False,
        "no_real_archive_permission_added_by_l23_7": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "next_patch": NEXT_PATCH,
    }
    for field in ALWAYS_FALSE_FIELDS:
        payload[field] = False
    return payload


def _read_synthetic_manifest_payload(path: Path, member_name: str) -> bytes:
    zip_module = importlib.import_module("zipfile")
    with zip_module.ZipFile(path, "r") as archive:
        # The only member payload read in L23.7 is the synthetic manifest member.
        return archive.read(member_name)


def build_first_synthetic_manifest_payload_proof(
    repo_root: str | Path | None = None,
    *,
    allow_synthetic_manifest_payload_proof: bool = False,
    authorization_token: str | None = None,
    synthetic_archive_relative_path: str = DEFAULT_SYNTHETIC_ARCHIVE_RELATIVE_PATH,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    if not allow_synthetic_manifest_payload_proof:
        return _default_payload(root, target_url)

    source = _l23_06_authorized_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_SYNTHETIC_MANIFEST_PAYLOAD_PROOF_TOKEN
    rel_is_fixed = synthetic_archive_relative_path == DEFAULT_SYNTHETIC_ARCHIVE_RELATIVE_PATH
    fixture_path = root / synthetic_archive_relative_path

    checks: list[dict[str, Any]] = [
        {"name": "source_l23_06_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l23_06_future_payload_authorized", "ok": source.get("synthetic_manifest_payload_authorization_granted_for_future_patch") is True},
        {"name": "source_l23_06_payload_execution_false", "ok": source.get("synthetic_manifest_payload_read_execution_allowed") is False},
        {"name": "payload_proof_token_present", "ok": token_present},
        {"name": "payload_proof_token_valid", "ok": token_valid},
        {"name": "synthetic_archive_relative_path_is_fixed", "ok": rel_is_fixed},
        {"name": "synthetic_archive_fixture_exists", "ok": fixture_path.exists()},
        {"name": "synthetic_archive_suffix_is_zip", "ok": fixture_path.suffix.lower() == ".zip"},
    ]

    payload_bytes = b""
    parsed: dict[str, Any] | None = None
    read_allowed = bool(all(check.get("ok") for check in checks))
    if read_allowed:
        try:
            payload_bytes = _read_synthetic_manifest_payload(fixture_path, EXPECTED_MANIFEST_MEMBER_NAME)
            parsed = json.loads(payload_bytes.decode("utf-8"))
            checks.append({"name": "synthetic_manifest_payload_nonempty", "ok": len(payload_bytes) > 0})
            checks.append({"name": "synthetic_manifest_json_parsed", "ok": isinstance(parsed, dict)})
            checks.append({"name": "synthetic_manifest_shape_valid", "ok": isinstance(parsed, dict) and parsed.get("manifest_version") == "1" and parsed.get("patch_name") == EXPECTED_SYNTHETIC_MANIFEST_PATCH_NAME})
        except Exception as exc:
            checks.append({"name": "synthetic_manifest_payload_read_and_parse", "ok": False, "error": f"{type(exc).__name__}: {exc}"})

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l23_06_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_payload_authorized": source.get("synthetic_manifest_payload_authorization_granted_for_future_patch"),
            "payload_execution_allowed": source.get("synthetic_manifest_payload_read_execution_allowed"),
            "manifest_member_payload_read": source.get("manifest_member_payload_read"),
            "archive_member_bytes_read": source.get("archive_member_bytes_read"),
            "archive_extracted": source.get("archive_extracted"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "synthetic_manifest_payload_proof_requested": True,
        "synthetic_manifest_payload_proof_token_present": token_present,
        "synthetic_manifest_payload_proof_token_valid": token_valid,
        "synthetic_manifest_payload_read_execution_allowed": read_allowed,
        "synthetic_manifest_payload_read_active": read_allowed,
        "synthetic_manifest_payload_read_performed": read_allowed,
        "synthetic_manifest_member_name": EXPECTED_MANIFEST_MEMBER_NAME if read_allowed else None,
        "synthetic_manifest_payload_size_bytes": len(payload_bytes),
        "synthetic_manifest_payload_sha256_performed": False,
        "synthetic_manifest_json_parsed": isinstance(parsed, dict),
        "synthetic_manifest_shape_validated": bool(isinstance(parsed, dict) and parsed.get("manifest_version") == "1" and parsed.get("patch_name") == EXPECTED_SYNTHETIC_MANIFEST_PATCH_NAME),
        "synthetic_manifest_patch_name": parsed.get("patch_name") if isinstance(parsed, dict) else None,
        "synthetic_manifest_scope": "fixed_synthetic_archive_manifest_payload_only",
        "manifest_member_bytes_read": read_allowed,
        "manifest_member_payload_read": read_allowed,
        "manifest_member_content_read": read_allowed,
        "archive_member_bytes_read": read_allowed,
        "archive_member_payload_read": read_allowed,
        "archive_member_content_read": read_allowed,
        "synthetic_archive_opened": read_allowed,
        "synthetic_archive_contents_listed": False,
        "no_real_archive_permission_added_by_l23_7": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "next_patch": NEXT_PATCH,
        "notes": [
            "L23.7 reads only manifest.json from the fixed synthetic archive fixture.",
            "No non-manifest member payload, extraction, real archive, browser, pasteback, send/submit, or package-run activity is performed.",
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
        f"Synthetic Scope               : {payload.get('synthetic_manifest_scope')}",
        f"Manifest Member               : {payload.get('synthetic_manifest_member_name')}",
        f"Payload Read                  : {payload.get('synthetic_manifest_payload_read_performed')}",
        f"JSON Parsed                   : {payload.get('synthetic_manifest_json_parsed')}",
        f"Shape Validated               : {payload.get('synthetic_manifest_shape_validated')}",
        f"Manifest Patch Name           : {payload.get('synthetic_manifest_patch_name')}",
        f"Non-Manifest Bytes Read       : {payload.get('non_manifest_member_bytes_read')}",
        f"Extraction                    : {payload.get('archive_extracted')}",
        f"Real Archive Manifest Read    : {payload.get('real_archive_manifest_read')}",
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
    parser.add_argument("--allow-synthetic-manifest-payload-proof", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--synthetic-archive-relative-path", default=DEFAULT_SYNTHETIC_ARCHIVE_RELATIVE_PATH)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_first_synthetic_manifest_payload_proof(
        args.repo_root,
        allow_synthetic_manifest_payload_proof=args.allow_synthetic_manifest_payload_proof,
        authorization_token=args.authorization_token,
        synthetic_archive_relative_path=args.synthetic_archive_relative_path,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
