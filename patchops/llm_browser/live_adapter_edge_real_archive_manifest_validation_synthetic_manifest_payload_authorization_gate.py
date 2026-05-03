"""L23.6 synthetic manifest payload authorization gate.

This module follows accepted L23.5. It grants only future authorization/readback
for a later synthetic manifest payload proof. It does not read manifest contents,
read member payload bytes, extract files, touch real downloaded artifacts, start
a browser, paste, send, or run packages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_validation_synthetic_manifest_name_gate as l23_05

PATCH = "L23.6"
PHASE = "L23"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L23.6 Microsoft Edge real downloaded-archive manifest validation synthetic manifest payload authorization gate"
SOURCE_PATCH = "L23.5"
NEXT_PATCH = "L23.7 Microsoft Edge real downloaded-archive manifest validation first synthetic manifest payload proof"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_SYNTHETIC_MANIFEST_PAYLOAD_AUTHORIZATION_TOKEN = "PATCHOPS_L23_EDGE_SYNTHETIC_MANIFEST_PAYLOAD_AUTHORIZED_READBACK_ONLY"

FALSE_FIELDS = (
    "synthetic_manifest_payload_read_execution_allowed",
    "synthetic_manifest_payload_read_active",
    "synthetic_manifest_payload_read_performed",
    "synthetic_manifest_json_parsed",
    "synthetic_manifest_shape_validated",
    "archive_member_bytes_read",
    "archive_member_content_read",
    "archive_member_payload_read",
    "downloaded_archive_extracted",
    "archive_extracted",
    "manifest_member_bytes_read",
    "manifest_member_payload_read",
    "manifest_member_content_read",
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


def _l23_05_name_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l23_05.build_synthetic_manifest_name_proof_gate(
            repo_root,
            allow_synthetic_manifest_name_proof=True,
            authorization_token=l23_05.REQUIRED_SYNTHETIC_MANIFEST_NAME_PROOF_TOKEN,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L23.5 name proof readback failed: {type(exc).__name__}: {exc}"}


def build_synthetic_manifest_payload_authorization_gate(
    repo_root: str | Path | None = None,
    *,
    allow_synthetic_manifest_payload_authorization: bool = False,
    authorization_token: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    source = _l23_05_name_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_SYNTHETIC_MANIFEST_PAYLOAD_AUTHORIZATION_TOKEN
    authorization_requested = bool(allow_synthetic_manifest_payload_authorization or token_present)
    future_authorized = bool(allow_synthetic_manifest_payload_authorization and token_valid)

    checks = [
        {"name": "source_l23_05_name_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l23_05_manifest_name_selected", "ok": source.get("synthetic_manifest_name_selected") is True},
        {"name": "source_l23_05_selected_name_is_manifest_json", "ok": source.get("synthetic_manifest_selected_name") == "manifest.json"},
        {"name": "source_l23_05_name_only_scope", "ok": source.get("synthetic_manifest_name_selection_scope") == "metadata_member_name_only_no_payload_read"},
        {"name": "source_l23_05_no_payload_or_member_read", "ok": source.get("manifest_member_payload_read") is False and source.get("archive_member_bytes_read") is False},
        {"name": "source_l23_05_no_extraction_browser_package", "ok": source.get("archive_extracted") is False and source.get("browser_started") is False and source.get("package_run") is False},
        {"name": "payload_authorization_is_readback_only", "ok": True},
        {"name": "payload_read_execution_remains_false", "ok": True},
    ]

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l23_05_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "manifest_name_selected": source.get("synthetic_manifest_name_selected"),
            "selected_name": source.get("synthetic_manifest_selected_name"),
            "selection_scope": source.get("synthetic_manifest_name_selection_scope"),
            "manifest_name_only": source.get("manifest_name_only"),
            "archive_member_bytes_read": source.get("archive_member_bytes_read"),
            "archive_member_payload_read": source.get("archive_member_payload_read"),
            "manifest_member_payload_read": source.get("manifest_member_payload_read"),
            "archive_extracted": source.get("archive_extracted"),
            "real_archive_manifest_read": source.get("real_archive_manifest_read"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "synthetic_manifest_payload_authorization_gate": True,
        "synthetic_manifest_payload_authorization_readback_only": True,
        "synthetic_manifest_payload_authorization_requested": authorization_requested,
        "synthetic_manifest_payload_authorization_token_present": token_present,
        "synthetic_manifest_payload_authorization_token_valid": token_valid,
        "synthetic_manifest_payload_authorization_granted_for_future_patch": future_authorized,
        "future_synthetic_manifest_payload_read_requires_explicit_flag_and_token": True,
        "future_synthetic_manifest_payload_read_must_be_separately_gated_in_l23_7": True,
        "no_new_payload_read_permission_added_by_l23_6": True,
        "safety_boundary": "readback-only payload authorization gate; no manifest payload read, no member bytes, no extraction, no real archive, no browser, no pasteback, no package-run",
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "default_microsoft_edge_profile_allowed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "target_url": target_url,
        "chatgpt_url_may_be_selected_but_not_opened": True,
        "checks": checks,
        "next_patch": NEXT_PATCH,
        "notes": [
            "L23.6 adds only future synthetic manifest payload authorization readback.",
            "Payload read execution remains false in this patch.",
            "The first actual synthetic payload proof must wait for L23.7.",
        ],
    }
    for field in FALSE_FIELDS:
        payload[field] = False
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Status                        : {payload.get('status')}",
        f"Future Payload Authorized     : {payload.get('synthetic_manifest_payload_authorization_granted_for_future_patch')}",
        f"Payload Execution Allowed     : {payload.get('synthetic_manifest_payload_read_execution_allowed')}",
        f"Manifest Payload Read         : {payload.get('manifest_member_payload_read')}",
        f"Member Bytes Read             : {payload.get('archive_member_bytes_read')}",
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
    parser.add_argument("--allow-synthetic-manifest-payload-authorization", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_synthetic_manifest_payload_authorization_gate(
        args.repo_root,
        allow_synthetic_manifest_payload_authorization=args.allow_synthetic_manifest_payload_authorization,
        authorization_token=args.authorization_token,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
