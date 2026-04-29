from __future__ import annotations

import argparse
import json
from pathlib import Path

from patchops import cli
from patchops.llm_browser import dependency_check


def _subcommand_names() -> set[str]:
    parser = cli.build_parser()
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return set(action.choices.keys())
    raise AssertionError("PatchOps parser did not expose a subcommand action.")


def test_llm_browser_subcommand_is_registered() -> None:
    assert "llm-browser" in _subcommand_names()


def test_llm_browser_doctor_cli_returns_json_without_real_browser_dependencies(monkeypatch, tmp_path: Path, capsys) -> None:
    edge = tmp_path / "msedge.exe"
    downloads = tmp_path / "Downloads"
    edge.write_text("", encoding="utf-8")
    downloads.mkdir()

    monkeypatch.setattr(dependency_check, "_module_available", lambda _module: True)
    monkeypatch.setenv("PATCHOPS_EDGE_PATH", str(edge))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    exit_code = cli.main(
        [
            "llm-browser",
            "doctor",
            "--browser",
            "edge",
            "--wrapper-root",
            str(tmp_path),
            "--download-dir",
            str(downloads),
            "--json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["result"] == "PASS"
    assert payload["ok"] is True


def test_llm_browser_doctor_help_does_not_start_browser(capsys) -> None:
    try:
        cli.main(["llm-browser", "doctor", "--help"])
    except SystemExit as exc:
        assert exc.code == 0

    captured = capsys.readouterr()
    text = captured.out + captured.err
    assert "usage:" in text
    assert "--browser" in text
    assert "--wrapper-root" in text
