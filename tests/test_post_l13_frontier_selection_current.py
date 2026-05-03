from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import post_l13_frontier_selection as frontier

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-post-l13-frontier-selection"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-final-acceptance-marker"


def test_post_l13_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_post_l13_payload_is_passive_and_does_not_auto_select_frontier() -> None:
    payload = frontier.build_post_l13_frontier_selection(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["patch"] == "post-L13"
    assert payload["source_patch"] == "L13.8"
    assert payload["source_l13_complete"] is True
    assert payload["remaining_l13_patches"] == []
    assert payload["frontier_selected"] is False
    assert payload["frontier_selection_requires_review"] is True
    assert payload["recommended_safe_next_patch_name"] == "l14_01_edge_launch_readiness_consolidation"
    assert payload["no_selenium_import"] is True
    assert payload["no_browser_start"] is True
    assert payload["no_edge_process_start"] is True
    assert payload["no_browser_session_creation"] is True
    assert payload["no_driver_creation"] is True
    assert payload["no_profile_directory_creation"] is True
    assert payload["no_click_download_paste_send_package_run"] is True
    assert payload["no_git_commit_or_push"] is True
    assert payload["no_localhost_patchops_server"] is True
    assert payload["no_browser_extension"] is True
    assert payload["executed_validation_commands"] == []


def test_post_l13_cli_compact_json_is_parseable() -> None:
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
    assert payload["source_l13_complete"] is True
    assert payload["frontier_selected"] is False


def test_post_l13_doc_mentions_required_boundaries() -> None:
    text = (PROJECT_ROOT / "docs" / "llm_browser_post_l13_frontier_selection.md").read_text(encoding="utf-8")
    for phrase in [
        "Post-L13 Microsoft Edge browser-runner frontier selection",
        COMMAND,
        SOURCE_COMMAND,
        "L13.8 final acceptance marker remains accepted",
        "L13 complete",
        "remaining L13 patches: none",
        "frontier is not auto-selected",
        "Microsoft Edge first",
        "Opera second",
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
        "l14_01_edge_launch_readiness_consolidation",
    ]:
        assert phrase in text
