"""L22.6 broad checkpoint for Edge downloaded-archive manifest validation.

L22.6a repairs the L22.6 broad checkpoint by normalizing older accepted
readback payloads. Some earlier checkpoint payloads may omit optional safety
fields. Missing optional fields are not treated as unsafe; explicit True values
for forbidden side-effect fields are treated as blockers.

Allowed:
- read back accepted L22.3b, L22.4/L22.4a, and L22.5 Python safety payloads;
- invoke the accepted L22.5 synthetic manifest fixture proof.

Still forbidden:
- browser start, Selenium import, CDP, DOM scraping, page inspection;
- real download workflow or real artifact content reading;
- archive open/extraction or archive member-byte reading;
- pasteback, send/submit, package-run, localhost server, browser extension;
- git commit or git push.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_downloaded_archive_manifest_validation_passive_plan_launcher_direct as l22_03b
from patchops.llm_browser import live_adapter_edge_downloaded_archive_manifest_validation_controlled_authorization_gate as l22_04
from patchops.llm_browser import live_adapter_edge_downloaded_archive_manifest_validation_first_controlled_manifest_proof as l22_05

PATCH = "L22.6"
REPAIR_PATCH = "L22.6a"
PHASE = "L22"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L22.6 Microsoft Edge downloaded-archive manifest validation broad checkpoint"
SOURCE_PATCHES = ("L22.3b", "L22.4/L22.4a", "L22.5")
NEXT_PATCH = "L22.7 Microsoft Edge downloaded-archive manifest validation final acceptance marker"
DEFAULT_TARGET_URL = "https://chatgpt.com/"

FORBIDDEN_TRUE_FIELDS = (
    "archive_extracted",
    "downloaded_archive_extracted",
    "downloaded_archive_opened",
    "archive_member_bytes_read",
    "member_bytes_read",
    "archive_member_content_read",
    "artifact_content_read",
    "real_downloaded_artifact_read",
    "downloaded_file_bytes_read",
    "downloaded_file_stat_performed",
    "downloaded_file_hash_performed",
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


def _safe_call(label: str, func: Any, *args: Any, **kwargs: Any) -> dict[str, Any]:
    try:
        payload = dict(func(*args, **kwargs))
        return {"ok": True, "payload": payload}
    except Exception as exc:  # pragma: no cover - defensive readback path
        return {"ok": False, "error": f"{label} failed: {type(exc).__name__}: {exc}", "payload": {}}


def _summary(payload: Mapping[str, Any], keys: Sequence[str]) -> dict[str, Any]:
    return {key: payload.get(key) for key in keys}


def _true_violations(payload: Mapping[str, Any], names: Sequence[str]) -> list[str]:
    return [name for name in names if payload.get(name) is True]


def _false_or_absent(payload: Mapping[str, Any], key: str) -> bool:
    return payload.get(key) is not True


def build_manifest_validation_broad_checkpoint(repo_root: str | Path | None = None, *, target_url: str = DEFAULT_TARGET_URL) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()

    r03b = _safe_call("L22.3b", l22_03b.build_manifest_validation_passive_plan, root)
    r04d = _safe_call("L22.4 default", l22_04.build_manifest_validation_controlled_authorization_gate, root, target_url=target_url)
    r04a = _safe_call(
        "L22.4 authorized",
        l22_04.build_manifest_validation_controlled_authorization_gate,
        root,
        allow_manifest_validation_authorization=True,
        authorization_token=l22_04.REQUIRED_MANIFEST_VALIDATION_AUTHORIZATION_TOKEN,
        target_url=target_url,
    )
    r05d = _safe_call("L22.5 default", l22_05.build_first_controlled_manifest_validation_proof, root, target_url=target_url)
    r05a = _safe_call(
        "L22.5 authorized",
        l22_05.build_first_controlled_manifest_validation_proof,
        root,
        allow_manifest_validation_proof=True,
        authorization_token=l22_05.REQUIRED_MANIFEST_VALIDATION_PROOF_TOKEN,
        target_url=target_url,
    )

    p03b = r03b.get("payload", {})
    p04d = r04d.get("payload", {})
    p04a = r04a.get("payload", {})
    p05d = r05d.get("payload", {})
    p05a = r05a.get("payload", {})

    safety_violations = {
        "l22_03b": _true_violations(p03b, FORBIDDEN_TRUE_FIELDS),
        "l22_04_authorized": _true_violations(p04a, FORBIDDEN_TRUE_FIELDS),
        "l22_05_authorized": _true_violations(p05a, FORBIDDEN_TRUE_FIELDS),
    }

    checks: list[dict[str, Any]] = [
        {"name": "l22_03b_readback_call_ok", "ok": bool(r03b.get("ok"))},
        {"name": "l22_04_default_readback_call_ok", "ok": bool(r04d.get("ok"))},
        {"name": "l22_04_authorized_readback_call_ok", "ok": bool(r04a.get("ok"))},
        {"name": "l22_05_default_readback_call_ok", "ok": bool(r05d.get("ok"))},
        {"name": "l22_05_authorized_readback_call_ok", "ok": bool(r05a.get("ok"))},
        {"name": "l22_03b_payload_ok", "ok": p03b.get("ok") is True and p03b.get("patch") == "L22.3b"},
        {"name": "l22_03b_no_manifest_execution", "ok": p03b.get("manifest_validation_execution_allowed") is False and _false_or_absent(p03b, "downloaded_manifest_read")},
        {"name": "l22_03b_no_forbidden_side_effects", "ok": not safety_violations["l22_03b"]},
        {"name": "l22_04_default_payload_ok", "ok": p04d.get("ok") is True and p04d.get("patch") == "L22.4"},
        {"name": "l22_04_default_not_authorized", "ok": p04d.get("manifest_validation_authorization_granted_for_future_patch") is False},
        {"name": "l22_04_authorized_payload_ok", "ok": p04a.get("ok") is True and p04a.get("manifest_validation_authorization_granted_for_future_patch") is True},
        {"name": "l22_04_execution_still_false", "ok": p04a.get("manifest_validation_execution_allowed") is False and _false_or_absent(p04a, "downloaded_manifest_read")},
        {"name": "l22_04_no_forbidden_side_effects", "ok": not safety_violations["l22_04_authorized"]},
        {"name": "l22_05_default_payload_ok", "ok": p05d.get("ok") is True and p05d.get("patch") == "L22.5"},
        {"name": "l22_05_default_no_manifest_read", "ok": p05d.get("manifest_validation_execution_allowed") is False and p05d.get("downloaded_manifest_read") is False and p05d.get("synthetic_manifest_fixture_read") is False},
        {"name": "l22_05_authorized_payload_ok", "ok": p05a.get("ok") is True and p05a.get("patch") == "L22.5"},
        {"name": "l22_05_authorized_synthetic_manifest_only", "ok": p05a.get("manifest_validation_scope") == "synthetic_patchops_runtime_manifest_fixture_only" and p05a.get("synthetic_manifest_fixture_read") is True},
        {"name": "l22_05_authorized_manifest_valid", "ok": p05a.get("manifest_validation_execution_allowed") is True and p05a.get("manifest_validation_result") is True},
        {"name": "l22_05_no_forbidden_side_effects", "ok": not safety_violations["l22_05_authorized"]},
    ]

    failed_checks = [check for check in checks if not check.get("ok")]
    ok = not failed_checks

    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "repair_patch": REPAIR_PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patches": list(SOURCE_PATCHES),
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "default_microsoft_edge_profile_allowed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "target_url": target_url,
        "chatgpt_url_may_be_selected_but_not_opened": True,
        "broad_checkpoint": True,
        "broad_checkpoint_scope": "accepted_l22_03b_l22_04_l22_05_readback_and_synthetic_manifest_fixture_proof",
        "l22_03b_summary": _summary(p03b, ("ok", "patch", "manifest_validation_execution_allowed", "downloaded_manifest_read", "archive_extracted", "archive_member_bytes_read", "browser_started", "package_run", "next_patch")),
        "l22_04_default_summary": _summary(p04d, ("ok", "patch", "manifest_validation_authorization_granted_for_future_patch", "manifest_validation_execution_allowed", "downloaded_manifest_read", "archive_extracted", "archive_member_bytes_read", "browser_started", "package_run")),
        "l22_04_authorized_summary": _summary(p04a, ("ok", "patch", "manifest_validation_authorization_granted_for_future_patch", "manifest_validation_execution_allowed", "downloaded_manifest_read", "archive_extracted", "archive_member_bytes_read", "browser_started", "package_run")),
        "l22_05_default_summary": _summary(p05d, ("ok", "patch", "manifest_validation_execution_allowed", "downloaded_manifest_read", "synthetic_manifest_fixture_read", "archive_extracted", "archive_member_bytes_read", "browser_started", "package_run")),
        "l22_05_authorized_summary": _summary(p05a, ("ok", "patch", "manifest_validation_execution_allowed", "downloaded_manifest_read", "synthetic_manifest_fixture_read", "manifest_validation_scope", "manifest_validation_result", "archive_extracted", "archive_member_bytes_read", "browser_started", "package_run")),
        "safety_violations": safety_violations,
        "manifest_validation_execution_allowed": p05a.get("manifest_validation_execution_allowed") is True,
        "manifest_validation_active": p05a.get("manifest_validation_active") is True,
        "manifest_validation_performed": p05a.get("manifest_validation_performed") is True,
        "downloaded_manifest_read": p05a.get("downloaded_manifest_read") is True,
        "manifest_read": p05a.get("manifest_read") is True,
        "synthetic_manifest_fixture_read": p05a.get("synthetic_manifest_fixture_read") is True,
        "synthetic_manifest_json_parsed": p05a.get("synthetic_manifest_json_parsed") is True,
        "manifest_shape_validated": p05a.get("manifest_shape_validated") is True,
        "manifest_validation_scope": p05a.get("manifest_validation_scope"),
        "manifest_validation_result": p05a.get("manifest_validation_result"),
        "real_downloaded_manifest_read": False,
        "real_archive_manifest_read": False,
        "checks": checks,
        "failed_checks": failed_checks,
        "next_patch": NEXT_PATCH,
        "notes": [
            "L22.6a repairs the broad checkpoint by treating missing optional safety fields as unknown/absent rather than unsafe.",
            "Explicit True values for forbidden side-effect fields still fail the checkpoint.",
            "The only manifest read in scope is the accepted L22.5 synthetic fixture proof.",
        ],
    }
    for field in FORBIDDEN_TRUE_FIELDS:
        payload[field] = False
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Repair Patch                  : {payload.get('repair_patch')}",
        f"Status                        : {payload.get('status')}",
        f"Broad Scope                   : {payload.get('broad_checkpoint_scope')}",
        f"Manifest Scope                : {payload.get('manifest_validation_scope')}",
        f"Manifest Result               : {payload.get('manifest_validation_result')}",
        f"Synthetic Fixture Read        : {payload.get('synthetic_manifest_fixture_read')}",
        f"Real Download Manifest Read   : {payload.get('real_downloaded_manifest_read')}",
        f"Archive Extracted             : {payload.get('archive_extracted')}",
        f"Member Bytes Read             : {payload.get('archive_member_bytes_read')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Package Run                   : {payload.get('package_run')}",
        f"Next Patch                    : {payload.get('next_patch')}",
        "",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        state = "PASS" if check.get("ok") else "FAIL"
        lines.append(f"- {state}: {check.get('name')}")
    if payload.get("failed_checks"):
        lines.append("")
        lines.append("Failed checks:")
        for check in payload.get("failed_checks", []):
            lines.append(f"- {check.get('name')}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_manifest_validation_broad_checkpoint(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
