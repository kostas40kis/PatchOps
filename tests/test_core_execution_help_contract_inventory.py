from __future__ import annotations

import argparse
from pathlib import Path

from patchops import cli


ROOT = Path(__file__).resolve().parents[1]


def _subcommand_names() -> set[str]:
    parser = cli.build_parser()
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return set(action.choices.keys())
    raise AssertionError("PatchOps parser did not expose a subcommand action.")


def test_core_execution_subcommands_remain_shipped() -> None:
    subcommands = _subcommand_names()
    assert {"apply", "verify", "wrapper-retry"}.issubset(subcommands)


def test_core_execution_help_contract_tests_exist() -> None:
    expected_tests = (
        ROOT / "tests" / "test_apply_cli_contract.py",
        ROOT / "tests" / "test_verify_cli_contract.py",
        ROOT / "tests" / "test_wrapper_retry_help_contract.py",
    )
    missing = [str(path) for path in expected_tests if not path.exists()]
    assert not missing, f"Missing core execution help-contract tests: {missing}"
