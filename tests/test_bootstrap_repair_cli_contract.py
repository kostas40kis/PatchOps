from __future__ import annotations

import argparse

from patchops import cli
from patchops.bootstrap_repair import build_parser as build_bootstrap_repair_parser


def _subparser_choices() -> dict[str, argparse.ArgumentParser]:
    parser = cli.build_parser()
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return dict(action.choices)
    raise AssertionError("PatchOps parser did not expose a subcommand action.")


def test_bootstrap_repair_subcommand_is_exposed() -> None:
    assert "bootstrap-repair" in _subparser_choices()


def test_bootstrap_repair_help_mentions_narrow_recovery_and_py_compile() -> None:
    help_text = _subparser_choices()["bootstrap-repair"].format_help()
    assert "narrow bootstrap recovery payload" in help_text
    assert "--path" in help_text
    assert "--py-compile-path" in help_text


def test_direct_bootstrap_repair_module_parser_mentions_broken_cli_case() -> None:
    parser = build_bootstrap_repair_parser()
    help_text = parser.format_help()
    assert "normal PatchOps CLI import chain is too broken" in help_text
    assert "--target-root" in help_text
