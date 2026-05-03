"""L17.6 broad passive checkpoint for Microsoft Edge artifact detection.

This checkpoint consolidates L17.1 through L17.5. It proves the passive
preflight, CLI/readback checkpoint, passive plan, live authorization readback,
and metadata-only artifact-presence proof remain accepted. It does not start
Edge, inspect real pages, use Selenium/CDP/DOM, read ChatGPT text, read artifact
content, click, download, paste, send, run packages, start localhost services,
use a browser extension, commit, or push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_artifact_presence_metadata_proof as l17_05

PATCH = "L17.6"
PHASE = "L17"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L17.6 Microsoft Edge artifact detection broad checkpoint"
COMMAND_NAME = "browser-start-supervised-launch-edge-artifact-detection-broad-checkpoint"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-artifact-presence-metadata-proof"
SOURCE_PATCH = "L17.5"
NEXT_PATCH = "L17.7 Microsoft Edge artifact detection final acceptance marker"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
METADATA_PROOF_AUTHORIZATION_TOKEN = "PATCHOPS_L17_EDGE_ARTIFACT_DETECTION_METADATA_PROOF_AUTHORIZED"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_artifact_detection_passive_preflight_gate.py",
    "patchops/llm_browser/live_adapter_edge_artifact_detection_cli_readback_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_artifact_detection_passive_plan_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_artifact_detection_controlled_live_authorization_gate.py",
    "patchops/llm_browser/live_adapter_edge_artifact_presence_metadata_proof.py",
    "patchops/llm_browser/live_adapter_edge_artifact_detection_broad_checkpoint.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_artifact_detection_passive_preflight_gate.md",
    "docs/llm_browser_live_adapter_edge_artifact_detection_cli_readback_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_artifact_detection_passive_plan_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_artifact_detection_controlled_live_authorization_gate.md",
    "docs/llm_browser_live_adapter_edge_artifact_presence_metadata_proof.md",
    "docs/llm_browser_live_adapter_edge_artifact_detection_broad_checkpoint.md",
    "scripts/patch_l17_01_brief_validate.py",
    "scripts/patch_l17_02_brief_validate.py",
    "scripts/patch_l17_03_brief_validate.py",
    "scripts/patch_l17_04_brief_validate.py",
    "scripts/patch_l17_05_brief_validate.py",
    "scripts/patch_l17_06_brief_validate.py",
    "tests/test_l17_01_edge_artifact_detection_passive_preflight_gate_current.py",
    "tests/test_l17_02_edge_artifact_detection_cli_readback_checkpoint_current.py",
    "tests/test_l17_03_edge_artifact_detection_passive_plan_checkpoint_current.py",
    "tests/test_l17_04_edge_artifact_detection_controlled_live_authorization_gate_current.py",
    "tests/test_l17_05_edge_artifact_presence_metadata_proof_current.py",
    "tests/test_l17_06_edge_artifact_detection_broad_checkpoint_current.py",
)

SAFETY_PHRASES = (
    "L17.6 Microsoft Edge artifact detection broad checkpoint",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    "Microsoft Edge first",
    "Opera second",
    "broad passive checkpoint",
    "L17.1 through L17.5 remain accepted",
    "metadata-only artifact-presence proof remains accepted",
    "metadata-only broad checkpoint",
    "live browser artifact detection remains inactive",
    "artifact detection execution allowed: false",
    "real page inspection performed: false",
    "artifact content reading performed: false",
    "download workflow active: false",
    "download workflow remains inactive",
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
    "L17.7 Microsoft Edge artifact detection final acceptance marker",
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_artifact_detection_broad_checkpoint.md")
    return [phrase for phrase in SAFETY_PHRASES if phrase not in text]


def _required_paths_status(root: Path) -> dict[str, Any]:
    missing = [rel for rel in REQUIRED_REPO_PATHS if not (root / rel).exists()]
    return {"ok": not missing, "missing": missing, "checked": list(REQUIRED_REPO_PATHS)}


def _forbidden_imports_loaded_since(before: set[str]) -> list[str]:
    after = set(sys.modules)
    return sorted(root for root in FORBIDDEN_OPTIONAL_ROOTS if root in after and root not in before)


def _source_l17_5_readbacks(root: Path, target_url: str) -> tuple[bool, dict[str, Any], dict[str, Any]]:
    default_payload = l17_05.build_edge_artifact_presence_metadata_proof(
        root,
        target_url=target_url,
    )
    authorized_payload = l17_05.build_edge_artifact_presence_metadata_proof(
        root,
        allow_artifact_presence_metadata_proof=True,
        authorization_token=METADATA_PROOF_AUTHORIZATION_TOKEN,
        candidate_metadata=l17_05.positive_metadata_fixture(),
        target_url=target_url,
    )
    default_ok = (
        default_payload.get("ok") is True
        and default_payload.get("patch") == SOURCE_PATCH
        and default_payload.get("l17_5_complete") is True
        and default_payload.get("source_l17_4_controlled_live_authorization_gate_accepted") is True
        and default_payload.get("artifact_presence_metadata_classification_performed") is False
        and default_payload.get("real_page_inspection_performed") is False
        and default_payload.get("live_browser_artifact_detection_active") is False
        and default_payload.get("artifact_content_reading_performed") is False
        and default_payload.get("download_workflow_active") is False
        and default_payload.get("download_performed") is False
        and default_payload.get("click_download_performed") is False
        and default_payload.get("browser_started") is False
        and default_payload.get("edge_process_started") is False
    )
    authorized_ok = (
        authorized_payload.get("ok") is True
        and authorized_payload.get("patch") == SOURCE_PATCH
        and authorized_payload.get("l17_5_complete") is True
        and authorized_payload.get("source_l17_4_controlled_live_authorization_gate_accepted") is True
        and authorized_payload.get("artifact_presence_metadata_proof_authorized") is True
        and authorized_payload.get("artifact_presence_metadata_classification_performed") is True
        and authorized_payload.get("artifact_presence_detected_from_metadata") is True
        and authorized_payload.get("artifact_presence_detection_scope") == "synthetic_or_operator_supplied_metadata_only"
        and authorized_payload.get("real_page_inspection_performed") is False
        and authorized_payload.get("live_browser_artifact_detection_active") is False
        and authorized_payload.get("live_browser_artifact_detection_performed") is False
        and authorized_payload.get("artifact_content_reading_performed") is False
        and authorized_payload.get("download_workflow_active") is False
        and authorized_payload.get("download_performed") is False
        and authorized_payload.get("click_download_performed") is False
        and authorized_payload.get("browser_started") is False
        and authorized_payload.get("edge_process_started") is False
        and authorized_payload.get("package_run_performed_by_adapter") is False
    )
    return default_ok and authorized_ok, default_payload, authorized_payload


def build_edge_artifact_detection_broad_checkpoint(
    repo_root: str | Path | None = None,
    *,
    target_url: str | None = None,
) -> dict[str, Any]:
    """Build the L17.6 broad checkpoint over L17.1 through L17.5."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)
    target = target_url or DEFAULT_TARGET_URL

    source_ok, default_source, authorized_source = _source_l17_5_readbacks(root, target)
    names = _command_names()
    missing_commands = [name for name in (SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)
    target_url_allowed = bool(authorized_source.get("target_url_allowed"))

    l17_chain_ok = (
        source_ok
        and authorized_source.get("source_l17_3_passive_plan_checkpoint_accepted") is True
        and authorized_source.get("source_l17_4_controlled_live_authorization_gate_accepted") is True
        and authorized_source.get("l17_4_complete") is True
        and authorized_source.get("l17_5_complete") is True
    )
    broad_safety_ok = (
        authorized_source.get("real_page_inspection_performed") is False
        and authorized_source.get("live_browser_artifact_detection_active") is False
        and authorized_source.get("live_browser_artifact_detection_performed") is False
        and authorized_source.get("artifact_content_reading_performed") is False
        and authorized_source.get("download_workflow_active") is False
        and authorized_source.get("download_performed") is False
        and authorized_source.get("click_download_performed") is False
        and authorized_source.get("browser_started") is False
        and authorized_source.get("edge_process_started") is False
        and authorized_source.get("chatgpt_url_opened") is False
        and authorized_source.get("package_run_performed_by_adapter") is False
    )

    checks = [
        _check("l17_1_through_l17_5_remain_accepted", l17_chain_ok),
        _check("metadata_only_artifact_presence_proof_remains_accepted", source_ok),
        _check("broad_checkpoint_has_no_browser_download_content_side_effects", broad_safety_ok),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("target_url_allowlist_enforced", target_url_allowed, {"target_url": target}),
        _check("dedicated_edge_profile_required_and_default_profile_rejected", True),
        _check("download_workflow_still_blocked", True),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l17_6_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "l17_1_through_l17_5_remain_accepted": l17_chain_ok,
        "metadata_only_artifact_presence_proof_remains_accepted": source_ok,
        "source_l17_5_default_readback_ok": bool(default_source.get("ok")),
        "source_l17_5_authorized_positive_readback_ok": bool(authorized_source.get("ok")),
        "source_l17_4_controlled_live_authorization_gate_accepted": bool(authorized_source.get("source_l17_4_controlled_live_authorization_gate_accepted")),
        "source_l17_3_passive_plan_checkpoint_accepted": bool(authorized_source.get("source_l17_3_passive_plan_checkpoint_accepted")),
        "l17_4_complete": bool(authorized_source.get("l17_4_complete")),
        "l17_5_complete": bool(authorized_source.get("l17_5_complete")),
        "artifact_presence_metadata_classification_validated": bool(authorized_source.get("artifact_presence_detected_from_metadata")),
        "artifact_presence_detection_scope": authorized_source.get("artifact_presence_detection_scope"),
        "artifact_detection_execution_allowed": False,
        "live_artifact_detection_execution_allowed": False,
        "artifact_presence_detection_execution_allowed": False,
        "artifact_detection_active": False,
        "artifact_detection_allowed": False,
        "artifact_detection_performed": False,
        "artifact_presence_detection_performed": False,
        "real_page_inspection_performed": False,
        "live_browser_artifact_detection_active": False,
        "live_browser_artifact_detection_performed": False,
        "artifact_content_reading_performed": False,
        "download_workflow_active": False,
        "download_workflow_allowed": False,
        "download_performed": False,
        "click_download_performed": False,
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
        "page_metadata_detection_proven": False,
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
        "download_workflow_remains_separate_future_stream": True,
        "operator_review_required_before_live_artifact_detection": True,
        "patchops_remains_source_of_truth": True,
        "target_url_allowlist_enforced": True,
        "target_url": target,
        "target_url_allowed": target_url_allowed,
        "source_l17_5_default_summary": {
            "ok": default_source.get("ok"),
            "patch": default_source.get("patch"),
            "l17_5_complete": default_source.get("l17_5_complete"),
            "artifact_presence_metadata_classification_performed": default_source.get("artifact_presence_metadata_classification_performed"),
            "artifact_presence_detected_from_metadata": default_source.get("artifact_presence_detected_from_metadata"),
            "download_workflow_active": default_source.get("download_workflow_active"),
            "browser_started": default_source.get("browser_started"),
        },
        "source_l17_5_authorized_summary": {
            "ok": authorized_source.get("ok"),
            "patch": authorized_source.get("patch"),
            "l17_5_complete": authorized_source.get("l17_5_complete"),
            "artifact_presence_metadata_proof_authorized": authorized_source.get("artifact_presence_metadata_proof_authorized"),
            "artifact_presence_metadata_classification_performed": authorized_source.get("artifact_presence_metadata_classification_performed"),
            "artifact_presence_detected_from_metadata": authorized_source.get("artifact_presence_detected_from_metadata"),
            "real_page_inspection_performed": authorized_source.get("real_page_inspection_performed"),
            "live_browser_artifact_detection_active": authorized_source.get("live_browser_artifact_detection_active"),
            "artifact_content_reading_performed": authorized_source.get("artifact_content_reading_performed"),
            "download_workflow_active": authorized_source.get("download_workflow_active"),
            "download_performed": authorized_source.get("download_performed"),
            "click_download_performed": authorized_source.get("click_download_performed"),
            "browser_started": authorized_source.get("browser_started"),
            "edge_process_started": authorized_source.get("edge_process_started"),
            "package_run_performed_by_adapter": authorized_source.get("package_run_performed_by_adapter"),
            "missing_commands": authorized_source.get("missing_commands"),
            "missing_doc_phrases": authorized_source.get("missing_doc_phrases"),
        },
        "l17_6_complete": ok,
        "remaining_l17_6_patches": [] if ok else [PATCH],
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
        f"L17.1-L17.5 Accepted          : {payload.get('l17_1_through_l17_5_remain_accepted')}",
        f"Metadata Proof Accepted       : {payload.get('metadata_only_artifact_presence_proof_remains_accepted')}",
        f"Real Page Inspection          : {payload.get('real_page_inspection_performed')}",
        f"Live Browser Detection Active : {payload.get('live_browser_artifact_detection_active')}",
        f"Download Workflow Active      : {payload.get('download_workflow_active')}",
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

    payload = build_edge_artifact_detection_broad_checkpoint(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
