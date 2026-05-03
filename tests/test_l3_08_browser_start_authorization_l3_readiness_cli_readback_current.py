from __future__ import annotations

import json
import sys
from pathlib import Path


def test_l3_08_command_name_registered() -> None:
    from patchops.llm_browser import commands

    assert "browser-start-authorization-l3-readiness" in commands.llm_browser_command_names()


def test_l3_08_parser_exposes_passive_command() -> None:
    from patchops.llm_browser import commands

    parser = commands.build_parser()
    action_choices = set()
    for action in getattr(parser, "_actions", []):
        choices = getattr(action, "choices", None)
        if isinstance(choices, dict):
            action_choices.update(choices)
    assert "browser-start-authorization-l3-readiness" in action_choices


def test_l3_08_cli_readback_is_passive_json(capsys) -> None:
    from patchops.llm_browser import commands

    before = set(sys.modules)
    rc = commands.main([
        "browser-start-authorization-l3-readiness",
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
    assert payload["patch"] == "L3.7"
    assert payload["next_patch"] == "L3.8 Live adapter browser-start authorization L3 aggregate readiness gate CLI/readback"
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["selenium_imported"] is False

    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager"}
    assert not any(name == root or name.startswith(root + ".") for root in forbidden_roots for name in newly_loaded)


def test_l3_08_docs_state_next_patch() -> None:
    doc = Path("docs/llm_browser_live_adapter_browser_start_authorization_l3_readiness_cli_readback.md")
    assert doc.exists()
    text = doc.read_text(encoding="utf-8")
    assert "browser-start-authorization-l3-readiness" in text
    assert "L3.9 Live adapter browser-start authorization L3 documentation freeze/readiness checkpoint" in text
    assert "no browser start" in text
    assert "no Selenium import" in text
