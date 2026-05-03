from __future__ import annotations

import json
import sys
from pathlib import Path


def test_l4_08_command_name_registered() -> None:
    from patchops.llm_browser import commands

    assert "browser-start-dry-run-handoff-l4-readiness" in commands.llm_browser_command_names()


def test_l4_08_parser_exposes_passive_command() -> None:
    from patchops.llm_browser import commands

    parser = commands.build_parser()
    action_choices = set()
    for action in getattr(parser, "_actions", []):
        choices = getattr(action, "choices", None)
        if isinstance(choices, dict):
            action_choices.update(choices)
    assert "browser-start-dry-run-handoff-l4-readiness" in action_choices


def test_l4_08_cli_readback_is_passive_json(capsys) -> None:
    from patchops.llm_browser import commands

    before = set(sys.modules)
    rc = commands.main([
        "browser-start-dry-run-handoff-l4-readiness",
        "--repo-root",
        ".",
        "--json",
        "--compact",
    ])
    out = capsys.readouterr().out
    payload = json.loads(out)
    after = set(sys.modules)

    assert rc == 0
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["phase"] == "L4"
    assert payload["patch"] == "L4.7"
    assert payload["next_patch"] == "L4.8 Live adapter browser-start dry-run handoff L4 aggregate readiness gate CLI/readback"
    assert payload["source_contract_patch"] == "L4.1"
    assert payload["source_fixture_matrix_patch"] == "L4.3"
    assert payload["source_contract_gate_patch"] == "L4.5"
    assert payload["dry_run_only"] is True
    assert payload["startup_authorized"] is False
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["selenium_imported"] is False
    assert payload["executed_validation_commands"] == []

    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    assert not any(name == root or name.startswith(root + ".") for root in forbidden_roots for name in newly_loaded)


def test_l4_08_cli_readback_text_is_operator_safe(capsys) -> None:
    from patchops.llm_browser import commands

    rc = commands.main([
        "browser-start-dry-run-handoff-l4-readiness",
        "--repo-root",
        ".",
    ])
    stdout = capsys.readouterr().out

    assert rc == 0
    assert "L4.7 Browser Start Dry-Run Handoff Aggregate Readiness Gate" in stdout
    assert "Status          : PASS" in stdout
    assert "Browser Started : False" in stdout
    assert "Profile Created : False" in stdout
    assert "Selenium Import : False" in stdout
    assert "Next Patch      : L4.8 Live adapter browser-start dry-run handoff L4 aggregate readiness gate CLI/readback" in stdout
    forbidden = [
        "Starting browser",
        "selenium webdriver",
        "click_download",
        "paste_to_composer",
        "send_or_submit",
        "run-package ",
        "git commit",
        "git push",
    ]
    lowered = stdout.lower()
    for fragment in forbidden:
        assert fragment.lower() not in lowered


def test_l4_08_cli_invocation_json_smoke() -> None:
    import subprocess

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            "browser-start-dry-run-handoff-l4-readiness",
            "--repo-root",
            ".",
            "--json",
            "--compact",
        ],
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["browser_started"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["selenium_imported"] is False


def test_l4_08_docs_state_next_patch() -> None:
    doc = Path("docs/llm_browser_live_adapter_browser_start_dry_run_handoff_l4_readiness_cli_readback.md")
    assert doc.exists()
    text = doc.read_text(encoding="utf-8")
    required = [
        "L4.8 Live adapter browser-start dry-run handoff L4 aggregate readiness gate CLI/readback",
        "browser-start-dry-run-handoff-l4-readiness",
        "L4.1",
        "L4.3",
        "L4.5",
        "L4.7",
        "no browser start",
        "no Selenium import",
        "no profile directory creation",
        "no adapter filesystem writes",
        "L4.9 Live adapter browser-start dry-run handoff L4 documentation freeze/readiness checkpoint",
    ]
    for phrase in required:
        assert phrase in text
