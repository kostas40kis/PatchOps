from __future__ import annotations

import argparse

from patchops import cli


EXPECTED_SUBCOMMANDS = {
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
    "make-bundle",
    "build-bundle",
    "bundle-doctor",
    "bundle-entry",
    "init-project-doc",
    "refresh-project-doc",
    "release-readiness",
    "check-launcher",
    "check-bundle",
    "inspect-bundle",
    "plan-bundle",
    "apply-bundle",
    "verify-bundle",
    "run-package",
}


def _subcommand_names() -> set[str]:
    parser = cli.build_parser()
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return set(action.choices.keys())
    raise AssertionError("PatchOps parser did not expose a subcommand action.")


def test_exact_cli_subcommand_set_remains_explicit() -> None:
    assert _subcommand_names() == EXPECTED_SUBCOMMANDS


def test_exact_cli_subcommand_count_remains_stable() -> None:
    assert len(EXPECTED_SUBCOMMANDS) == 29
