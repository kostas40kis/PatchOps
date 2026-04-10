from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_combined_proof_inputs_exist() -> None:
    required = [
        "handoff/final_future_llm_source_bundle.txt",
        "handoff/self_hosted_proof_lock.txt",
        "tests/test_future_llm_source_bundle_truth_lock_current.py",
        "tests/test_bundle_root_launcher_lock_current.py",
        "tests/test_generated_test_path_assertion_audit_current.py",
        "tests/test_self_hosted_proof_lock_current.py",
        "tests/test_suspicious_run_detector_current.py",
        "tests/test_suspicious_artifact_report_mention_current.py",
        "patchops/suspicious_runs.py",
        "patchops/suspicious_artifacts.py",
    ]
    missing = [path for path in required if not (PROJECT_ROOT / path).exists()]
    assert not missing, f"missing combined proof inputs: {missing}"


def test_future_llm_and_self_hosted_handoff_surfaces_remain_truthful() -> None:
    future_bundle = _read("handoff/final_future_llm_source_bundle.txt").lower()
    self_hosted = _read("handoff/self_hosted_proof_lock.txt").lower()

    assert "preferred history-compression artifact" in future_bundle
    assert "module tree" in future_bundle or "modular package" in future_bundle
    assert "self-hosted proof" in self_hosted
    assert "run-package" in self_hosted


def test_suspicious_run_support_surfaces_still_exist() -> None:
    suspicious_runs = _read("patchops/suspicious_runs.py")
    suspicious_artifacts = _read("patchops/suspicious_artifacts.py")

    assert "def detect_suspicious_run" in suspicious_runs
    assert "SuspiciousRunFinding" in suspicious_runs
    assert "Suspicious-run artifact emitted" in suspicious_artifacts


def test_operator_runner_surface_still_points_at_canonical_runner() -> None:
    operator_runner_doc = PROJECT_ROOT / "docs" / "run_package_operator_runner.md"
    assert operator_runner_doc.exists(), "missing run-package operator runner doc"
    text = operator_runner_doc.read_text(encoding="utf-8").lower()

    assert "canonical operator-facing runner" in text
    assert "invoke-quietrunpackage.ps1" in text
