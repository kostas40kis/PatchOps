from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_live_open_proof as l15_01

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-live-open-proof"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-dedicated-profile-lifecycle-final-acceptance-marker"


def _source_payload() -> dict:
    return {
        "ok": True,
        "status": "PASS",
        "patch": "L14.9",
        "l14_complete": True,
        "remaining_l14_patches": [],
        "profile_final_marker_truthful": True,
        "profile_final_marker_is_passive": True,
        "profile_candidate_under_allowed_runtime_root": True,
        "profile_lifecycle_steps_are_passive": True,
        "launch_execution_allowed": False,
        "browser_started": False,
        "edge_process_started": False,
        "driver_created": False,
        "selenium_imported_by_readback": False,
    }


class FakeProcess:
    pid = 4242

    def __init__(self) -> None:
        self.terminated = False

    def poll(self):
        return None

    def terminate(self) -> None:
        self.terminated = True

    def wait(self, timeout=None):
        return 0


def test_l15_01_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l15_01_default_readback_passes_safety_contract_without_side_effects() -> None:
    payload = l15_01.build_edge_live_open_proof(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L15.1"
    assert payload["source_patch"] == "L14.9"
    assert payload["l14_09_final_marker_remains_accepted"] is True
    assert payload["execution_mode"] == "readback_only"
    assert payload["browser_process_launch_requested"] is False
    assert payload["browser_process_launch_authorized"] is False
    assert payload["launch_execution_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["profile_directory_mutated"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["selenium_required"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert payload["page_scraping_performed"] is False
    assert payload["artifact_detection_performed"] is False
    assert payload["download_performed"] is False
    assert payload["paste_performed"] is False
    assert payload["send_or_submit_performed"] is False
    assert payload["package_run_performed_by_adapter"] is False
    assert payload["git_commit_executed"] is False
    assert payload["git_push_executed"] is False
    assert payload["localhost_patchops_server_started"] is False
    assert payload["browser_extension_used"] is False


def test_l15_01_rejects_disallowed_profile_path() -> None:
    payload = l15_01.build_edge_live_open_proof(
        PROJECT_ROOT,
        profile_relative_path="../outside_profile",
        source_l14_payload=_source_payload(),
    )
    assert payload["profile_candidate_under_allowed_runtime_root"] is False
    assert payload["profile_default_profile_rejected"] is True
    assert payload["launch_execution_allowed"] is False
    assert payload["browser_started"] is False


def test_l15_01_fake_live_execution_requires_all_explicit_gates_and_uses_dedicated_profile(tmp_path: Path) -> None:
    fake_edge = tmp_path / "msedge.exe"
    fake_edge.write_text("fake", encoding="utf-8")
    calls = []

    def fake_popen(args, *, cwd):
        calls.append({"args": list(args), "cwd": cwd})
        return FakeProcess()

    payload = l15_01.build_edge_live_open_proof(
        tmp_path,
        source_l14_payload=_source_payload(),
        edge_executable_path=fake_edge,
        execute_live_open=True,
        allow_live_edge_start=True,
        authorization_token=l15_01.AUTHORIZATION_TOKEN,
        close_after_seconds=0,
        popen_factory=fake_popen,
        sleep_func=lambda _seconds: None,
    )

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["execution_mode"] == "live_open"
    assert payload["explicit_gate_satisfied"] is True
    assert payload["launch_execution_allowed"] is True
    assert payload["browser_process_launch_requested"] is True
    assert payload["browser_process_launch_authorized"] is True
    assert payload["browser_started"] is True
    assert payload["edge_process_started"] is True
    assert payload["browser_session_created"] is True
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is True
    assert payload["profile_directory_mutated"] is True
    assert payload["profile_candidate_under_allowed_runtime_root"] is True
    assert payload["profile_default_profile_rejected"] is True
    assert payload["authorization_token_matches"] is True
    assert payload["authorization_token_echoed"] is False
    assert payload["selenium_required"] is False
    assert payload["page_scraping_performed"] is False
    assert payload["artifact_detection_performed"] is False
    assert payload["download_performed"] is False
    assert payload["paste_performed"] is False
    assert payload["send_or_submit_performed"] is False
    assert payload["package_run_performed_by_adapter"] is False
    assert calls
    assert any(str(tmp_path / "data" / "runtime" / "browser_profiles" / "edge_supervised_l14") in arg for arg in calls[0]["args"])


def test_l15_01_execute_with_missing_token_does_not_start(tmp_path: Path) -> None:
    fake_edge = tmp_path / "msedge.exe"
    fake_edge.write_text("fake", encoding="utf-8")
    calls = []
    payload = l15_01.build_edge_live_open_proof(
        tmp_path,
        source_l14_payload=_source_payload(),
        edge_executable_path=fake_edge,
        execute_live_open=True,
        allow_live_edge_start=True,
        authorization_token="wrong-token",
        popen_factory=lambda *args, **kwargs: calls.append((args, kwargs)),
    )
    assert payload["ok"] is False
    assert payload["authorization_token_matches"] is False
    assert payload["launch_execution_allowed"] is False
    assert payload["browser_started"] is False
    assert calls == []


def test_l15_01_cli_compact_json_is_parseable_and_non_executing() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(PROJECT_ROOT), "--json", "--compact"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["patch"] == "L15.1"
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["execution_mode"] == "readback_only"
    assert payload["launch_execution_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["send_or_submit_performed"] is False


def test_l15_01_doc_mentions_required_boundaries() -> None:
    text = (PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_live_open_proof.md").read_text(encoding="utf-8")
    for phrase in [
        "L15.1 Microsoft Edge live open proof explicit authorization gate",
        COMMAND,
        SOURCE_COMMAND,
        "L14.9 final acceptance marker remains accepted",
        "Microsoft Edge first",
        "Opera second",
        "Opera is not the active implementation target",
        "real browser start requires `--execute-live-open`",
        "real browser start requires `--allow-live-edge-start`",
        "PATCHOPS_L15_EDGE_LIVE_OPEN_PROOF",
        "authorization token is not echoed",
        "dedicated profile candidate is `data/runtime/browser_profiles/edge_supervised_l14`",
        "default Edge profile is rejected",
        "default CLI/readback mode is passive and starts no browser",
        "no Selenium import",
        "no driver creation",
        "no page scraping",
        "no ChatGPT interaction",
        "no artifact detection",
        "no click/download/paste/send/package-run side effect",
        "no auto-send",
        "no git commit or git push",
        "no localhost PatchOps server",
        "no browser extension",
        "Default JSON readback is allowed to return `PASS`",
        "`launch_execution_allowed: false`",
    ]:
        assert phrase in text
