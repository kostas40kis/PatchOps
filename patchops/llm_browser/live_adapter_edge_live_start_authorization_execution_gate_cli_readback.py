"""L15.2 CLI/readback checkpoint for the passive Edge live-start gate.

L15.2 proves that the accepted L15.1 authorization/execution gate can be read
through compact CLI JSON in both no-authorization and explicitly-authorized
readback modes. It remains passive and does not cross the live browser-start
execution boundary.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH = "L15.2"
PHASE = "L15"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L15.2 Microsoft Edge live-start authorization/execution gate CLI readback"
COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-authorization-execution-gate-cli-readback"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-authorization-execution-gate"
L14_SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-dedicated-profile-lifecycle-final-acceptance-marker"
NEXT_PATCH = "L15.3 first controlled Microsoft Edge open proof using dedicated profile only"
REQUIRED_AUTHORIZATION_TOKEN = "PATCHOPS_L15_EDGE_LIVE_START_AUTHORIZED"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_dedicated_profile_lifecycle_final_acceptance_marker.py",
    "patchops/llm_browser/live_adapter_edge_live_start_authorization_execution_gate.py",
    "patchops/llm_browser/live_adapter_edge_live_start_authorization_execution_gate_cli_readback.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_live_start_authorization_execution_gate.md",
    "docs/llm_browser_live_adapter_edge_live_start_authorization_execution_gate_cli_readback.md",
    "scripts/patch_l15_01_brief_validate.py",
    "scripts/patch_l15_02_brief_validate.py",
    "tests/test_l15_01_edge_live_start_authorization_execution_gate_current.py",
    "tests/test_l15_02_edge_live_start_authorization_execution_gate_cli_readback_current.py",
)

SAFETY_PHRASES = (
    "L15.2 Microsoft Edge live-start authorization/execution gate CLI readback",
    SOURCE_COMMAND_NAME,
    L14_SOURCE_COMMAND_NAME,
    "Microsoft Edge first",
    "Opera second",
    "compact JSON readback",
    "no-authorization readback",
    "explicitly-authorized readback",
    "authorization is readback-only in L15.2",
    "launch execution allowed: false",
    "L15.2 is passive",
    "no Selenium import",
    "no browser start",
    "no Edge process start",
    "no browser session creation",
    "no driver creation",
    "no profile directory creation",
    "no profile directory mutation",
    "no click/download/paste/send/package-run side effect",
    "no localhost PatchOps server",
    "no browser extension",
    "no git commit or git push",
    NEXT_PATCH,
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_live_start_authorization_execution_gate_cli_readback.md")
    return [phrase for phrase in SAFETY_PHRASES if phrase not in text]


def _required_paths_status(root: Path) -> dict[str, Any]:
    missing = [rel for rel in REQUIRED_REPO_PATHS if not (root / rel).exists()]
    return {"ok": not missing, "missing": missing, "checked": list(REQUIRED_REPO_PATHS)}


def _forbidden_imports_loaded_since(before: set[str]) -> list[str]:
    after = set(sys.modules)
    return sorted(root for root in FORBIDDEN_OPTIONAL_ROOTS if root in after and root not in before)


def _json_from_stdout(stdout: str) -> dict[str, Any]:
    text = (stdout or "").strip()
    if not text:
        return {}
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        for line in reversed(text.splitlines()):
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    value = json.loads(line)
                    return value if isinstance(value, dict) else {}
                except json.JSONDecodeError:
                    continue
    return {}


def _invoke_l15_1_cli(root: Path, *, authorized: bool) -> dict[str, Any]:
    args = [
        sys.executable,
        "-m",
        "patchops.cli",
        "llm-browser",
        SOURCE_COMMAND_NAME,
        "--repo-root",
        str(root),
        "--json",
        "--compact",
    ]
    if authorized:
        args.extend(["--allow-live-start", "--authorization-token", REQUIRED_AUTHORIZATION_TOKEN])
    completed = subprocess.run(args, cwd=root, text=True, capture_output=True, timeout=45)
    payload = _json_from_stdout(completed.stdout)
    return {
        "ok": completed.returncode == 0 and bool(payload.get("ok")),
        "returncode": completed.returncode,
        "stdout_preview": completed.stdout[:500],
        "stderr_preview": completed.stderr[:500],
        "payload": payload,
    }


def _summarize_l15_1_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "ok",
        "status",
        "patch",
        "phase",
        "command_name",
        "source_patch",
        "source_l14_09_final_marker_accepted",
        "microsoft_edge_first",
        "opera_second",
        "opera_active_implementation_target",
        "dedicated_profile_candidate_inherited_from_l14_09",
        "default_edge_profile_rejected",
        "explicit_live_start_authorization_flag_present",
        "explicit_live_start_authorization_token_present",
        "live_start_operator_authorization_complete",
        "authorization_missing_keeps_execution_blocked",
        "authorization_present_is_readback_only_in_l15_1",
        "launch_execution_allowed",
        "browser_process_launch_requested",
        "browser_process_launch_authorized",
        "browser_started",
        "edge_process_started",
        "browser_session_created",
        "driver_created",
        "selenium_required",
        "selenium_imported_by_readback",
        "profile_directory_created",
        "profile_directory_mutated",
        "filesystem_writes_performed",
        "adapter_filesystem_writes_performed",
        "side_effects_performed",
        "auto_send_allowed",
        "missing_commands",
        "missing_doc_phrases",
        "next_patch",
    )
    return {key: payload.get(key) for key in keys}


def _l15_1_payload_is_passive(summary: Mapping[str, Any]) -> bool:
    return (
        summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("patch") == "L15.1"
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("source_l14_09_final_marker_accepted") is True
        and summary.get("microsoft_edge_first") is True
        and summary.get("opera_second") is True
        and summary.get("opera_active_implementation_target") is False
        and summary.get("dedicated_profile_candidate_inherited_from_l14_09") is True
        and summary.get("default_edge_profile_rejected") is True
        and summary.get("launch_execution_allowed") is False
        and summary.get("browser_process_launch_requested") is False
        and summary.get("browser_started") is False
        and summary.get("edge_process_started") is False
        and summary.get("browser_session_created") is False
        and summary.get("driver_created") is False
        and summary.get("selenium_required") is False
        and summary.get("selenium_imported_by_readback") is False
        and summary.get("profile_directory_created") is False
        and summary.get("profile_directory_mutated") is False
        and summary.get("filesystem_writes_performed") == []
        and summary.get("adapter_filesystem_writes_performed") == []
        and summary.get("side_effects_performed") == []
        and summary.get("auto_send_allowed") is False
        and summary.get("missing_commands") == []
        and summary.get("missing_doc_phrases") == []
    )


def build_edge_live_start_authorization_execution_gate_cli_readback(
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Run and verify the compact CLI readback for the passive L15.1 gate."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    no_auth_run = _invoke_l15_1_cli(root, authorized=False)
    auth_run = _invoke_l15_1_cli(root, authorized=True)
    no_auth = _summarize_l15_1_payload(no_auth_run.get("payload", {}))
    authorized = _summarize_l15_1_payload(auth_run.get("payload", {}))

    required = _required_paths_status(root)
    names = _command_names()
    missing_commands = [name for name in (SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)

    no_auth_readback_ok = (
        no_auth_run["returncode"] == 0
        and _l15_1_payload_is_passive(no_auth)
        and no_auth.get("explicit_live_start_authorization_flag_present") is False
        and no_auth.get("explicit_live_start_authorization_token_present") is False
        and no_auth.get("live_start_operator_authorization_complete") is False
        and no_auth.get("authorization_missing_keeps_execution_blocked") is True
        and no_auth.get("authorization_present_is_readback_only_in_l15_1") is False
        and no_auth.get("browser_process_launch_authorized") is False
    )
    authorized_readback_ok = (
        auth_run["returncode"] == 0
        and _l15_1_payload_is_passive(authorized)
        and authorized.get("explicit_live_start_authorization_flag_present") is True
        and authorized.get("explicit_live_start_authorization_token_present") is True
        and authorized.get("live_start_operator_authorization_complete") is True
        and authorized.get("authorization_present_is_readback_only_in_l15_1") is True
        and authorized.get("authorization_missing_keeps_execution_blocked") is False
        and authorized.get("browser_process_launch_authorized") is True
        and authorized.get("launch_execution_allowed") is False
    )

    checks = [
        _check("source_l15_1_no_auth_cli_readback_passive", no_auth_readback_ok, {"returncode": no_auth_run["returncode"]}),
        _check("source_l15_1_authorized_cli_readback_passive", authorized_readback_ok, {"returncode": auth_run["returncode"]}),
        _check("authorization_is_readback_only", authorized.get("live_start_operator_authorization_complete") is True and authorized.get("launch_execution_allowed") is False),
        _check("no_auth_keeps_execution_blocked", no_auth.get("live_start_operator_authorization_complete") is False and no_auth.get("launch_execution_allowed") is False),
        _check("l15_2_command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l15_2_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "l14_source_command_name": L14_SOURCE_COMMAND_NAME,
        "source_patch": "L15.1",
        "next_patch": NEXT_PATCH,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "cli_readback_only": True,
        "compact_json_readback": True,
        "no_authorization_readback_ok": no_auth_readback_ok,
        "authorized_readback_ok": authorized_readback_ok,
        "authorization_is_readback_only_in_l15_2": authorized.get("live_start_operator_authorization_complete") is True and authorized.get("launch_execution_allowed") is False,
        "launch_execution_allowed": False,
        "browser_process_launch_requested": False,
        "browser_started": False,
        "edge_process_started": False,
        "browser_session_created": False,
        "driver_created": False,
        "selenium_required": False,
        "selenium_imported_by_readback": False,
        "profile_directory_creation_allowed": False,
        "profile_directory_mutation_allowed": False,
        "profile_directory_created": False,
        "profile_directory_mutated": False,
        "filesystem_writes_performed": [],
        "adapter_filesystem_writes_performed": [],
        "side_effects_performed": [],
        "click_download_performed": False,
        "download_performed": False,
        "paste_performed": False,
        "send_or_submit_performed": False,
        "package_run_performed_by_adapter": False,
        "localhost_patchops_server_started": False,
        "browser_extension_used": False,
        "git_commit_executed": False,
        "git_push_executed": False,
        "auto_send_allowed": False,
        "operator_review_required_before_live_start": True,
        "l15_2_complete": ok,
        "remaining_l15_2_patches": [] if ok else [PATCH],
        "missing_commands": missing_commands,
        "missing_doc_phrases": missing_doc_phrases,
        "required_repo_paths": required,
        "forbidden_optional_browser_imports_newly_loaded": forbidden_imports_newly_loaded,
        "no_auth_readback": no_auth,
        "authorized_readback": authorized,
        "checks": checks,
    }


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Patch                   : {payload.get('patch')}",
        f"Status                  : {payload.get('status')}",
        f"Command                 : {payload.get('command_name')}",
        f"Source Command          : {payload.get('source_command_name')}",
        f"No-Auth Readback OK     : {payload.get('no_authorization_readback_ok')}",
        f"Authorized Readback OK  : {payload.get('authorized_readback_ok')}",
        f"Readback Only           : {payload.get('authorization_is_readback_only_in_l15_2')}",
        f"Launch Allowed          : {payload.get('launch_execution_allowed')}",
        f"Browser Started         : {payload.get('browser_started')}",
        f"Edge Process Started    : {payload.get('edge_process_started')}",
        f"Selenium Imported       : {payload.get('selenium_imported_by_readback')}",
        f"Next Patch              : {payload.get('next_patch')}",
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
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_live_start_authorization_execution_gate_cli_readback(args.repo_root)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
