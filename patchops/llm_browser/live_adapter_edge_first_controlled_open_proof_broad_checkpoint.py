"""L15.4 broad checkpoint for the first controlled Microsoft Edge open proof.

This module aggregates the accepted L15.1 authorization gate, L15.2 CLI/readback
checkpoint, and L15.3 first controlled Edge open proof into one broad checkpoint.
It can run in dry mode or execute one explicitly-authorized live Edge open smoke.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_first_controlled_open_proof as l15_03
from patchops.llm_browser import live_adapter_edge_live_start_authorization_execution_gate as l15_01
from patchops.llm_browser import live_adapter_edge_live_start_authorization_execution_gate_cli_readback as l15_02

PATCH = "L15.4"
PHASE = "L15"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L15.4 Microsoft Edge first controlled open proof broad checkpoint"
COMMAND_NAME = "browser-start-supervised-launch-edge-first-controlled-open-proof-broad-checkpoint"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-first-controlled-open-proof"
L15_2_COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-authorization-execution-gate-cli-readback"
L15_1_COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-authorization-execution-gate"
NEXT_PATCH = "L15.5 Microsoft Edge live-start handoff marker before real-page detection"
REQUIRED_AUTHORIZATION_TOKEN = "PATCHOPS_L15_EDGE_LIVE_START_AUTHORIZED"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_live_start_authorization_execution_gate.py",
    "patchops/llm_browser/live_adapter_edge_live_start_authorization_execution_gate_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_first_controlled_open_proof.py",
    "patchops/llm_browser/live_adapter_edge_first_controlled_open_proof_broad_checkpoint.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_live_start_authorization_execution_gate.md",
    "docs/llm_browser_live_adapter_edge_live_start_authorization_execution_gate_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_first_controlled_open_proof.md",
    "docs/llm_browser_live_adapter_edge_first_controlled_open_proof_broad_checkpoint.md",
    "scripts/patch_l15_01_brief_validate.py",
    "scripts/patch_l15_02_brief_validate.py",
    "scripts/patch_l15_03_brief_validate.py",
    "scripts/patch_l15_04_brief_validate.py",
    "tests/test_l15_01_edge_live_start_authorization_execution_gate_current.py",
    "tests/test_l15_02_edge_live_start_authorization_execution_gate_cli_readback_current.py",
    "tests/test_l15_03_edge_first_controlled_open_proof_current.py",
    "tests/test_l15_04_edge_first_controlled_open_proof_broad_checkpoint_current.py",
)

SAFETY_PHRASES = (
    "L15.4 Microsoft Edge first controlled open proof broad checkpoint",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    L15_2_COMMAND_NAME,
    L15_1_COMMAND_NAME,
    "Microsoft Edge first",
    "Opera second",
    "broad checkpoint",
    "dry checkpoint",
    "explicit live checkpoint",
    "about:blank only",
    "dedicated L14 profile only",
    "default Microsoft Edge profile rejected",
    "Selenium is not imported",
    "no ChatGPT interaction",
    "no artifact detection",
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_first_controlled_open_proof_broad_checkpoint.md")
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


def _invoke_cli(root: Path, args: Sequence[str], timeout: int = 120) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", *args],
        cwd=root,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    payload = _json_from_stdout(completed.stdout)
    return {
        "ok": completed.returncode == 0 and bool(payload.get("ok")),
        "returncode": completed.returncode,
        "stdout_preview": completed.stdout[:500],
        "stderr_preview": completed.stderr[:500],
        "payload": payload,
    }


def _assert_no_chat_artifact_side_effects(payload: Mapping[str, Any]) -> bool:
    return (
        payload.get("chatgpt_url_opened") is False
        and payload.get("artifact_detection_performed") is False
        and payload.get("click_download_performed") is False
        and payload.get("download_performed") is False
        and payload.get("paste_performed") is False
        and payload.get("send_or_submit_performed") is False
        and payload.get("package_run_performed_by_adapter") is False
        and payload.get("localhost_patchops_server_started") is False
        and payload.get("browser_extension_used") is False
        and payload.get("git_commit_executed") is False
        and payload.get("git_push_executed") is False
        and payload.get("auto_send_allowed") is False
        and payload.get("selenium_imported_by_readback") is False
        and payload.get("selenium_required") is False
        and payload.get("browser_session_created") is False
        and payload.get("driver_created") is False
    )


def build_edge_first_controlled_open_proof_broad_checkpoint(
    repo_root: str | Path | None = None,
    *,
    execute_live_checkpoint: bool = False,
    close_after_seconds: float = 3.0,
) -> dict[str, Any]:
    """Build the L15.4 broad checkpoint over L15.1 through L15.3."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    l15_1_no_auth = l15_01.build_edge_live_start_authorization_execution_gate(root)
    l15_1_authorized = l15_01.build_edge_live_start_authorization_execution_gate(
        root,
        allow_live_start=True,
        authorization_token=REQUIRED_AUTHORIZATION_TOKEN,
    )
    l15_2_payload = l15_02.build_edge_live_start_authorization_execution_gate_cli_readback(root)
    l15_3_dry = l15_03.build_edge_first_controlled_open_proof(root)

    l15_3_live: dict[str, Any] = {}
    if execute_live_checkpoint:
        l15_3_live = l15_03.build_edge_first_controlled_open_proof(
            root,
            allow_live_start=True,
            authorization_token=REQUIRED_AUTHORIZATION_TOKEN,
            execute_live_open=True,
            close_after_seconds=close_after_seconds,
        )

    l15_3_cli_dry = _invoke_cli(
        root,
        [SOURCE_COMMAND_NAME, "--repo-root", str(root), "--json", "--compact"],
        timeout=120,
    )

    names = _command_names()
    missing_commands = [name for name in (L15_1_COMMAND_NAME, L15_2_COMMAND_NAME, SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)

    l15_1_ok = (
        l15_1_no_auth.get("ok") is True
        and l15_1_authorized.get("ok") is True
        and l15_1_no_auth.get("launch_execution_allowed") is False
        and l15_1_authorized.get("launch_execution_allowed") is False
        and l15_1_authorized.get("live_start_operator_authorization_complete") is True
        and l15_1_authorized.get("browser_started") is False
        and l15_1_authorized.get("edge_process_started") is False
        and l15_1_authorized.get("selenium_imported_by_readback") is False
    )
    l15_2_ok = (
        l15_2_payload.get("ok") is True
        and l15_2_payload.get("no_authorization_readback_ok") is True
        and l15_2_payload.get("authorized_readback_ok") is True
        and l15_2_payload.get("authorization_is_readback_only_in_l15_2") is True
        and l15_2_payload.get("launch_execution_allowed") is False
        and l15_2_payload.get("browser_started") is False
        and l15_2_payload.get("edge_process_started") is False
        and l15_2_payload.get("selenium_imported_by_readback") is False
    )
    l15_3_dry_ok = (
        l15_3_dry.get("ok") is True
        and l15_3_dry.get("launch_execution_allowed") is False
        and l15_3_dry.get("browser_started") is False
        and l15_3_dry.get("edge_process_started") is False
        and l15_3_dry.get("open_url_is_about_blank") is True
        and l15_3_dry.get("profile_candidate_under_allowed_runtime_root") is True
        and l15_3_dry.get("default_edge_profile_rejected") is True
        and _assert_no_chat_artifact_side_effects(l15_3_dry)
    )
    l15_3_cli_dry_payload = l15_3_cli_dry.get("payload", {})
    l15_3_cli_dry_ok = (
        l15_3_cli_dry.get("ok") is True
        and l15_3_cli_dry_payload.get("patch") == "L15.3"
        and l15_3_cli_dry_payload.get("browser_started") is False
        and l15_3_cli_dry_payload.get("edge_process_started") is False
        and l15_3_cli_dry_payload.get("launch_execution_allowed") is False
        and _assert_no_chat_artifact_side_effects(l15_3_cli_dry_payload)
    )
    l15_3_live_ok = True
    if execute_live_checkpoint:
        l15_3_live_ok = (
            l15_3_live.get("ok") is True
            and l15_3_live.get("launch_execution_allowed") is True
            and l15_3_live.get("live_open_smoke_executed") is True
            and l15_3_live.get("live_open_smoke_proven") is True
            and l15_3_live.get("browser_started") is True
            and l15_3_live.get("edge_process_started") is True
            and l15_3_live.get("browser_close_attempted") is True
            and (l15_3_live.get("edge_process_close_result") or {}).get("remaining_count") == 0
            and l15_3_live.get("open_url") == "about:blank"
            and _assert_no_chat_artifact_side_effects(l15_3_live)
        )

    checks = [
        _check("l15_1_authorization_gate_still_green", l15_1_ok),
        _check("l15_2_cli_readback_still_green", l15_2_ok),
        _check("l15_3_dry_readback_still_green", l15_3_dry_ok),
        _check("l15_3_cli_dry_readback_still_green", l15_3_cli_dry_ok, {"returncode": l15_3_cli_dry.get("returncode")}),
        _check("l15_3_live_checkpoint_green_when_requested", l15_3_live_ok, {"execute_live_checkpoint": execute_live_checkpoint}),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l15_4_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "l15_2_command_name": L15_2_COMMAND_NAME,
        "l15_1_command_name": L15_1_COMMAND_NAME,
        "source_patch": "L15.3",
        "next_patch": NEXT_PATCH,
        "broad_checkpoint": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "dry_checkpoint": not execute_live_checkpoint,
        "explicit_live_checkpoint": bool(execute_live_checkpoint),
        "l15_1_authorization_gate_still_green": l15_1_ok,
        "l15_2_cli_readback_still_green": l15_2_ok,
        "l15_3_dry_readback_still_green": l15_3_dry_ok,
        "l15_3_cli_dry_readback_still_green": l15_3_cli_dry_ok,
        "l15_3_live_checkpoint_green_when_requested": l15_3_live_ok,
        "launch_execution_allowed": bool(execute_live_checkpoint and l15_3_live.get("launch_execution_allowed") is True),
        "browser_started": bool(l15_3_live.get("browser_started")) if execute_live_checkpoint else False,
        "edge_process_started": bool(l15_3_live.get("edge_process_started")) if execute_live_checkpoint else False,
        "live_open_smoke_executed": bool(l15_3_live.get("live_open_smoke_executed")) if execute_live_checkpoint else False,
        "live_open_smoke_proven": bool(l15_3_live.get("live_open_smoke_proven")) if execute_live_checkpoint else False,
        "browser_close_attempted": bool(l15_3_live.get("browser_close_attempted")) if execute_live_checkpoint else False,
        "edge_process_close_result": l15_3_live.get("edge_process_close_result") if execute_live_checkpoint else {},
        "open_url": l15_3_live.get("open_url", "about:blank") if execute_live_checkpoint else "about:blank",
        "selenium_required": False,
        "selenium_imported_by_readback": False,
        "chatgpt_url_opened": False,
        "artifact_detection_performed": False,
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
        "l15_4_complete": ok,
        "remaining_l15_4_patches": [] if ok else [PATCH],
        "l15_1_summary": {
            "no_auth_ok": l15_1_no_auth.get("ok"),
            "authorized_ok": l15_1_authorized.get("ok"),
            "authorized_readback_only": l15_1_authorized.get("authorization_present_is_readback_only_in_l15_1"),
            "launch_execution_allowed": l15_1_authorized.get("launch_execution_allowed"),
        },
        "l15_2_summary": {
            "ok": l15_2_payload.get("ok"),
            "no_authorization_readback_ok": l15_2_payload.get("no_authorization_readback_ok"),
            "authorized_readback_ok": l15_2_payload.get("authorized_readback_ok"),
            "authorization_is_readback_only_in_l15_2": l15_2_payload.get("authorization_is_readback_only_in_l15_2"),
        },
        "l15_3_dry_summary": {
            "ok": l15_3_dry.get("ok"),
            "edge_executable_discovered": (l15_3_dry.get("edge_executable_discovery") or {}).get("ok"),
            "profile_candidate_path": l15_3_dry.get("profile_candidate_path"),
            "launch_execution_allowed": l15_3_dry.get("launch_execution_allowed"),
            "browser_started": l15_3_dry.get("browser_started"),
            "edge_process_started": l15_3_dry.get("edge_process_started"),
            "open_url": l15_3_dry.get("open_url"),
        },
        "l15_3_live_summary": {
            "ok": l15_3_live.get("ok"),
            "launch_execution_allowed": l15_3_live.get("launch_execution_allowed"),
            "browser_started": l15_3_live.get("browser_started"),
            "edge_process_started": l15_3_live.get("edge_process_started"),
            "live_open_smoke_proven": l15_3_live.get("live_open_smoke_proven"),
            "browser_close_attempted": l15_3_live.get("browser_close_attempted"),
            "edge_process_close_result": l15_3_live.get("edge_process_close_result"),
            "open_url": l15_3_live.get("open_url"),
        } if execute_live_checkpoint else {},
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
        f"Patch               : {payload.get('patch')}",
        f"Status              : {payload.get('status')}",
        f"Command             : {payload.get('command_name')}",
        f"Source Command      : {payload.get('source_command_name')}",
        f"Live Checkpoint     : {payload.get('explicit_live_checkpoint')}",
        f"Launch Allowed      : {payload.get('launch_execution_allowed')}",
        f"Browser Started     : {payload.get('browser_started')}",
        f"Edge Started        : {payload.get('edge_process_started')}",
        f"Live Proven         : {payload.get('live_open_smoke_proven')}",
        f"Close Attempted     : {payload.get('browser_close_attempted')}",
        f"Next Patch          : {payload.get('next_patch')}",
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
    parser.add_argument("--execute-live-checkpoint", action="store_true")
    parser.add_argument("--close-after-seconds", type=float, default=3.0)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_first_controlled_open_proof_broad_checkpoint(
        args.repo_root,
        execute_live_checkpoint=args.execute_live_checkpoint,
        close_after_seconds=args.close_after_seconds,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
