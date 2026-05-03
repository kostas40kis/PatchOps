from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l4_02_command_name_registered() -> None:
    from patchops.llm_browser import commands

    assert "browser-start-dry-run-handoff" in commands.llm_browser_command_names()


def test_l4_02_parser_exposes_passive_command() -> None:
    from patchops.llm_browser import commands

    parser = commands.build_parser()
    action_choices = set()
    for action in getattr(parser, "_actions", []):
        choices = getattr(action, "choices", None)
        if isinstance(choices, dict):
            action_choices.update(choices)
    assert "browser-start-dry-run-handoff" in action_choices


def test_l4_02_cli_readback_is_passive_json_edge(capsys) -> None:
    from patchops.llm_browser import commands

    before = set(sys.modules)
    rc = commands.main([
        "browser-start-dry-run-handoff",
        "--repo-root",
        str(PROJECT_ROOT),
        "--browser",
        "edge",
        "--json",
        "--compact",
    ])
    out = capsys.readouterr().out
    payload = json.loads(out)
    after = set(sys.modules)

    assert rc == 0
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L4.1"
    assert payload["next_patch"] == "L4.2 Live adapter browser-start dry-run handoff CLI/readback"
    assert payload["browser"] == "edge"
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
    forbidden_roots = {"selenium", "webdriver_manager", "playwright", "pyppeteer"}
    assert not any(name == root or name.startswith(root + ".") for root in forbidden_roots for name in newly_loaded)


def test_l4_02_cli_readback_models_opera_without_starting_browser(capsys) -> None:
    from patchops.llm_browser import commands

    rc = commands.main([
        "browser-start-dry-run-handoff",
        "--repo-root",
        str(PROJECT_ROOT),
        "--browser",
        "opera",
        "--json",
        "--compact",
    ])
    out = capsys.readouterr().out
    payload = json.loads(out)

    assert rc == 0
    assert payload["ok"] is True
    assert payload["browser"] == "opera"
    assert payload["handoff_request"]["kind"] == "browser_start_dry_run_handoff"
    assert payload["handoff_request"]["dry_run_only"] is True
    assert payload["handoff_request"]["startup_authorized"] is False
    assert payload["handoff_request"]["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["selenium_imported"] is False


def test_l4_02_command_plan_stays_readback_only(capsys) -> None:
    from patchops.llm_browser import commands

    rc = commands.main([
        "browser-start-dry-run-handoff",
        "--repo-root",
        str(PROJECT_ROOT),
        "--browser",
        "edge",
        "--json",
        "--compact",
    ])
    payload = json.loads(capsys.readouterr().out)
    command_text = "\n".join(payload["handoff_readback_commands"])

    assert rc == 0
    assert "live_adapter_browser_start_dry_run_handoff_contract" in command_text
    assert "--browser edge" in command_text
    assert "--browser opera" in command_text
    assert "git status --short --branch" in command_text
    assert "run-package" not in command_text
    assert "git commit" not in command_text
    assert "git push" not in command_text
    assert "selenium" not in command_text.lower()
    assert "webdriver" not in command_text.lower()
    assert "click_download" not in command_text
    assert "paste_to_composer" not in command_text
    assert "send_or_submit" not in command_text


def test_l4_02_docs_state_next_patch_and_boundary() -> None:
    doc = PROJECT_ROOT / "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_cli_readback.md"
    assert doc.exists()
    text = doc.read_text(encoding="utf-8")
    assert "browser-start-dry-run-handoff" in text
    assert "L4.3 Live adapter browser-start dry-run handoff fixture matrix" in text
    assert "no browser start" in text
    assert "no Selenium import" in text
    assert "no profile directory creation" in text
    assert "no click/download/paste/send/package-run side effect" in text
