from __future__ import annotations

import argparse

from patchops import cli


OPERATOR_SUBCOMMANDS = {
    "apply",
    "verify",
    "wrapper-retry",
    "profiles",
    "doctor",
    "examples",
    "schema",
    "check",
    "inspect",
    "plan",
    "template",
    "export-handoff",
    "bootstrap-target",
    "recommend-profile",
    "starter",
    "init-project-doc",
    "refresh-project-doc",
    "release-readiness",
}


def _subcommand_names() -> set[str]:
    parser = cli.build_parser()
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return set(action.choices.keys())
    raise AssertionError("PatchOps parser did not expose a subcommand action.")


def test_operator_subcommands_remain_shipped() -> None:
    subcommands = _subcommand_names()
    assert OPERATOR_SUBCOMMANDS.issubset(subcommands)


def test_operator_subcommand_inventory_stays_explicit() -> None:
    subcommands = _subcommand_names()
    discovered = {name for name in subcommands if name in OPERATOR_SUBCOMMANDS}
    assert discovered == OPERATOR_SUBCOMMANDS
