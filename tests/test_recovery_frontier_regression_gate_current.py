from pathlib import Path


def test_recovery_frontier_regression_gate_targets_expected_surfaces() -> None:
    expected = [
        Path("tests/test_maintenance_gate_cli_contract.py"),
        Path("tests/test_maintenance_gate_command.py"),
        Path("tests/test_setup_windows_env_cli_contract.py"),
        Path("tests/test_bundle_manifest_regression_gate_current.py"),
        Path("tests/test_run_package_outer_truth_current.py"),
        Path("tests/test_run_package_canonical_report_unification_current.py"),
        Path("tests/test_run_package_preflight_current.py"),
        Path("tests/test_bundle_generated_helper_syntax_gate_current.py"),
        Path("tests/test_patchops_entry_live_smoke_proof_current.py"),
    ]
    missing = [str(path) for path in expected if not path.exists()]
    assert not missing, f"Missing expected frontier regression targets: {missing}"
