from __future__ import annotations

import json
import sys
from pathlib import Path


def test_l3_11_command_name_registered() -> None:
    from patchops.llm_browser import commands

    assert "browser-start-authorization-l3-broad-validation" in commands.llm_browser_command_names()


def test_l3_11_parser_exposes_passive_command() -> None:
    from patchops.llm_browser import commands

    parser = commands.build_parser()
    action_choices = set()
    for action in getattr(parser, "_actions", []):
        choices = getattr(action, "choices", None)
        if isinstance(choices, dict):
            action_choices.update(choices)
    assert "browser-start-authorization-l3-broad-validation" in action_choices


def test_l3_11_cli_readback_is_passive_json(capsys) -> None:
    from patchops.llm_browser import commands

    before = set(sys.modules)
    rc = commands.main([
        "browser-start-authorization-l3-broad-validation",
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
    assert payload["patch"] == "L3.10"
    assert payload["next_patch"] == "L3.11 Live adapter browser-start authorization L3 broad validation checkpoint CLI/readback"
    assert payload["startup_authorized"] is False
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["selenium_imported"] is False
    assert payload["executed_validation_commands"] == []
    assert payload["missing_commands"] == []
    assert payload["missing_l1_l2_paths"] == []
    assert payload["missing_l3_paths"] == []

    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "playwright", "pyppeteer"}
    assert not any(name == root or name.startswith(root + ".") for root in forbidden_roots for name in newly_loaded)


def test_l3_11_docs_state_next_patch_and_boundary() -> None:
    doc = Path("docs/llm_browser_live_adapter_browser_start_authorization_l3_broad_validation_cli_readback.md")
    assert doc.exists()
    text = doc.read_text(encoding="utf-8")
    assert "browser-start-authorization-l3-broad-validation" in text
    assert "L3.12 Live adapter browser-start authorization L3 final acceptance marker" in text
    assert "no browser start" in text
    assert "no Selenium import" in text
    assert "no profile directory creation" in text
    assert "no click/download/paste/send/package-run side effect" in text
