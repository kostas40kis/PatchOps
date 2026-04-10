from __future__ import annotations

import argparse

from patchops import cli


LAUNCHER_BACKED_COMMANDS = {
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
    "release-readiness",
}

PYTHON_ONLY_HELPER_COMMANDS = {
    "bootstrap-target",
    "recommend-profile",
    "starter",
    "init-project-doc",
    "refresh-project-doc",
    "setup-windows-env",
}

EXPECTED_OPERATOR_SURFACE = LAUNCHER_BACKED_COMMANDS | PYTHON_ONLY_HELPER_COMMANDS


def _subcommand_names() -> set[str]:
    parser = cli.build_parser()
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return set(action.choices.keys())
    raise AssertionError("PatchOps parser did not expose a subcommand action.")


def test_operator_surface_partitions_remain_disjoint() -> None:
    overlap = LAUNCHER_BACKED_COMMANDS.intersection(PYTHON_ONLY_HELPER_COMMANDS)
    assert not overlap, f"Operator surface partitions must stay disjoint: {sorted(overlap)}"


def test_operator_surface_partitions_cover_current_operator_map() -> None:
    subcommands = _subcommand_names()
    discovered = {name for name in subcommands if name in EXPECTED_OPERATOR_SURFACE}
    assert discovered == EXPECTED_OPERATOR_SURFACE


def test_operator_surface_partition_size_stays_explicit() -> None:
    assert len(LAUNCHER_BACKED_COMMANDS) == 13
    assert len(PYTHON_ONLY_HELPER_COMMANDS) == 6
    assert len(EXPECTED_OPERATOR_SURFACE) == 19
