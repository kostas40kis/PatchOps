from __future__ import annotations

import json
import sys
from pathlib import Path


def test_l4_11_command_name_registered() -> None:
    from patchops.llm_browser import commands

    assert "browser-start-dry-run-handoff-l4-broad-validation" in commands.llm_browser_command_names()


def test_l4_11_parser_exposes_passive_command() -> None:
    from patchops.llm_browser import commands

    parser = commands.build_parser()
    action_choices = set()
    for action in getattr(parser, "_actions", []):
        choices = getattr(action, "choices", None)
        if isinstance(choices, dict):
            action_choices.update(choices)
    assert "browser-start-dry-run-handoff-l4-broad-validation" in action_choices


def test_l4_11_cli_readback_is_passive_json(capsys) -> None:
    from patchops.llm_browser import commands

    before = set(sys.modules)
    rc = commands.main([
        "browser-start-dry-run-handoff-l4-broad-validation",
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
    assert payload["patch"] == "L4.10"
    assert payload["next_patch"] == "L4.11 Live adapter browser-start dry-run handoff L4 broad validation checkpoint CLI/readback"
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
    assert payload["executed_validation_commands"] == [] if "executed_validation_commands" in payload else True
    assert payload["missing_commands"] == []
    assert payload["missing_l4_paths"] == []

    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    assert not any(name == root or name.startswith(root + ".") for root in forbidden_roots for name in newly_loaded)


def test_l4_11_cli_readback_text_is_operator_safe(capsys) -> None:
    from patchops.llm_browser import commands

    rc = commands.main([
        "browser-start-dry-run-handoff-l4-broad-validation",
        "--repo-root",
        ".",
    ])
    stdout = capsys.readouterr().out

    assert rc == 0
    assert "L4.10 Browser Start Dry-Run Handoff Broad Validation Checkpoint" in stdout
    assert "Status     : PASS" in stdout
    assert "Browser    : started=False" in stdout
    assert "ProfileDir : created=False" in stdout
    assert "Next patch : L4.11 Live adapter browser-start dry-run handoff L4 broad validation checkpoint CLI/readback" in stdout
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


def test_l4_11_cli_invocation_json_smoke() -> None:
    import subprocess

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            "browser-start-dry-run-handoff-l4-broad-validation",
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


def test_l4_11_docs_state_next_patch() -> None:
    doc = Path("docs/llm_browser_live_adapter_browser_start_dry_run_handoff_l4_broad_validation_cli_readback.md")
    assert doc.exists()
    text = doc.read_text(encoding="utf-8")
    required = [
        "L4.11 Live adapter browser-start dry-run handoff L4 broad validation checkpoint CLI/readback",
        "browser-start-dry-run-handoff-l4-broad-validation",
        "L4.1",
        "L4.3",
        "L4.5",
        "L4.7",
        "L4.8",
        "L4.9",
        "L4.10",
        "no browser start",
        "no Selenium import",
        "no profile directory creation",
        "no adapter filesystem writes",
        "L4.12 Live adapter browser-start dry-run handoff L4 final acceptance marker",
    ]
    for phrase in required:
        assert phrase in text
