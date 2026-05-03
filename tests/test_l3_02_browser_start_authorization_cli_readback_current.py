from __future__ import annotations

import argparse
import importlib
import json
import sys


COMMAND = "browser-start-authorization"


def _commands():
    return importlib.import_module("patchops.llm_browser.commands")


def _subcommands(parser: argparse.ArgumentParser) -> set[str]:
    for action in getattr(parser, "_actions", []):
        if action.__class__.__name__ == "_SubParsersAction":
            return set(getattr(action, "choices", {}).keys())
    raise AssertionError("llm-browser parser did not expose subcommands")


def test_l3_2_command_name_is_registered():
    commands = _commands()
    assert COMMAND in commands.llm_browser_command_names()
    assert COMMAND in _subcommands(commands.build_parser())


def test_l3_2_cli_readback_is_passive_json(capsys):
    commands = _commands()
    exit_code = commands.main([COMMAND, "--repo-root", ".", "--json", "--compact"])
    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["patch"] == "L3.1"
    assert payload["ok"] is True
    assert payload["startup_authorized"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert "L3.2 Live adapter explicit browser-start authorization CLI/readback" in payload["next_patch"]


def test_l3_2_modelled_permission_flags_do_not_start_browser(capsys):
    commands = _commands()
    exit_code = commands.main([
        COMMAND,
        "--repo-root",
        ".",
        "--browser",
        "opera",
        "--ack-all",
        "--allow-browser-start",
        "--allow-profile-directory-creation",
        "--allow-live-driver-session",
        "--json",
        "--compact",
    ])
    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    requested = payload["requested_decision"]
    assert requested["requested_browser"] == "opera"
    assert requested["startup_authorized"] is False
    assert requested["browser_started"] is False
    assert requested["browser_session_created"] is False
    assert requested["profile_directory_created"] is False
    assert requested["side_effects_performed"] == []
    assert requested["filesystem_writes_performed"] == []
    assert "live_side_effects_requested_but_modelled_only" in requested["blocked_reasons"]


def test_l3_2_cli_readback_does_not_import_selenium_or_optional_browser_dependencies(capsys):
    before = set(sys.modules)
    commands = _commands()
    exit_code = commands.main([COMMAND, "--repo-root", ".", "--json", "--compact"])
    assert exit_code == 0
    capsys.readouterr()
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {
        root
        for root in forbidden_roots
        if any(name == root or name.startswith(root + ".") for name in newly_loaded)
    }
    assert imported == set()


def test_l3_2_help_text_does_not_expose_live_start_commands():
    commands = _commands()
    parser = commands.build_parser()
    command_parser = None
    for action in getattr(parser, "_actions", []):
        if action.__class__.__name__ == "_SubParsersAction":
            command_parser = getattr(action, "choices", {})[COMMAND]
            break
    assert command_parser is not None
    help_text = command_parser.format_help().lower()
    forbidden = (
        "run-once",
        "watch-downloads",
        "click-download",
        "paste-to-composer",
        "send-or-submit",
        "git commit",
        "git push",
    )
    assert all(fragment not in help_text for fragment in forbidden)
