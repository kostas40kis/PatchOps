from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_launch_readiness_consolidation as l14_01

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-launch-readiness-consolidation"
SOURCE_COMMAND = "browser-start-supervised-launch-post-l13-frontier-selection"


def _assert_passive(payload: dict) -> None:
    assert payload["browser_process_launch_requested"] is False
    assert payload["browser_process_launch_authorized"] is False
    assert payload["launch_execution_allowed"] is False
    assert payload["selenium_required"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["adapter_filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["click_download_performed"] is False
    assert payload["download_performed"] is False
    assert payload["paste_performed"] is False
    assert payload["send_or_submit_performed"] is False
    assert payload["package_run_performed_by_adapter"] is False
    assert payload["git_commit_executed"] is False
    assert payload["git_push_executed"] is False
    assert payload["localhost_patchops_server_started"] is False
    assert payload["browser_extension_used"] is False
    assert payload["executed_validation_commands"] == []


def test_l14_01_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l14_01_readiness_consolidates_post_l13_without_launch() -> None:
    payload = l14_01.build_edge_launch_readiness_consolidation(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L14.1"
    assert payload["phase"] == "L14"
    assert payload["source_patch"] == "post-L13"
    assert payload["source_l13_complete"] is True
    assert payload["remaining_l13_patches"] == []
    assert payload["active_frontier"] == "l14_01_edge_launch_readiness_consolidation"
    assert payload["source_recommended_safe_next_patch_name"] == "l14_01_edge_launch_readiness_consolidation"
    assert payload["launch_readiness_consolidated"] is True
    assert payload["missing_readiness_gates"] == []
    assert payload["operator_review_required_before_live_start"] is True
    assert payload["microsoft_edge_first"] is True
    assert payload["opera_second"] is True
    _assert_passive(payload)
    assert payload["next_patch"] == "L14.2 Microsoft Edge supervised launch authorization gate, still no launch by default"


def test_l14_01_cli_compact_json_is_parseable_and_passive() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(PROJECT_ROOT), "--json", "--compact"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L14.1"
    assert payload["launch_readiness_consolidated"] is True
    assert payload["launch_execution_allowed"] is False
    _assert_passive(payload)


def test_l14_01_doc_mentions_required_boundaries() -> None:
    text = (PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_launch_readiness_consolidation.md").read_text(encoding="utf-8")
    for phrase in [
        "L14.1 Microsoft Edge launch-readiness consolidation",
        COMMAND,
        SOURCE_COMMAND,
        "post-L13 frontier selection remains accepted",
        "L13 complete",
        "remaining L13 patches: none",
        "Microsoft Edge first",
        "Opera second",
        "launch readiness consolidated",
        "browser process launch requested: false",
        "browser process launch authorized: false",
        "launch execution allowed: false",
        "operator review required before live start",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no browser session creation",
        "no driver creation",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "no git commit or git push",
        "no localhost PatchOps server",
        "no browser extension",
        "L14.2 Microsoft Edge supervised launch authorization gate, still no launch by default",
    ]:
        assert phrase in text
