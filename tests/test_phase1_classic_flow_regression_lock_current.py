from __future__ import annotations

from pathlib import Path

PHASE1_CLASSIC_REGRESSION_TARGETS = [
    "tests/test_apply_cli_contract.py",
    "tests/test_verify_only_flow.py",
    "tests/test_reporting.py",
    "tests/test_profile_resolution.py",
    "tests/test_apply_bundle_command_current.py",
    "tests/test_apply_bundle_report_chain_current.py",
    "tests/test_bundle_launcher_invoker_current.py",
    "tests/test_run_package_outer_truth_current.py",
]


def test_phase1_classic_regression_targets_exist() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    missing = [
        relative_path
        for relative_path in PHASE1_CLASSIC_REGRESSION_TARGETS
        if not (repo_root / relative_path).is_file()
    ]
    assert missing == []


def test_phase1_classic_regression_targets_cover_expected_surfaces() -> None:
    assert "tests/test_apply_cli_contract.py" in PHASE1_CLASSIC_REGRESSION_TARGETS
    assert "tests/test_verify_only_flow.py" in PHASE1_CLASSIC_REGRESSION_TARGETS
    assert "tests/test_reporting.py" in PHASE1_CLASSIC_REGRESSION_TARGETS
    assert "tests/test_profile_resolution.py" in PHASE1_CLASSIC_REGRESSION_TARGETS
    assert "tests/test_run_package_outer_truth_current.py" in PHASE1_CLASSIC_REGRESSION_TARGETS
    assert len(set(PHASE1_CLASSIC_REGRESSION_TARGETS)) == len(PHASE1_CLASSIC_REGRESSION_TARGETS)
