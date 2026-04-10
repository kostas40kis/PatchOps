import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PATCH_NAME = "patch_47a_self_hosted_proof_lock_bundle_meta_repair"
BUNDLE_NAME = "patch_47a_self_hosted_proof_lock_bundle_meta_repair_bundle"


def _latest_bundle_root() -> Path:
    package_runs = PROJECT_ROOT / "data" / "runtime" / "package_runs"
    candidates = sorted(
        package_runs.glob(f"{BUNDLE_NAME}_*"),
        key=lambda path: path.stat().st_mtime,
    )
    assert candidates, f"expected at least one package run workspace for {BUNDLE_NAME}"
    return candidates[-1] / "extracted" / BUNDLE_NAME


def test_self_hosted_proof_note_exists_and_mentions_core_truth() -> None:
    proof_note = PROJECT_ROOT / "handoff" / "self_hosted_proof_lock.txt"
    assert proof_note.exists(), "missing self-hosted proof note"
    text = proof_note.read_text(encoding="utf-8").lower()

    required_phrases = [
        "self-hosted proof",
        "run-package",
        "canonical report truth",
        "inner report",
        "wrapper_owned_write_engine",
        "check-bundle -> check -> inspect -> plan -> apply",
        "future handoff use",
    ]
    for phrase in required_phrases:
        assert phrase in text, f"missing proof phrase: {phrase}"


def test_current_bundle_workspace_proves_run_package_exercised() -> None:
    bundle_root = _latest_bundle_root()
    assert bundle_root.exists(), "missing extracted bundle root"
    assert (bundle_root / "run_with_patchops.ps1").exists(), "missing root launcher"
    assert (bundle_root / "manifest.json").exists(), "missing manifest"
    assert (bundle_root / "bundle_meta.json").exists(), "missing bundle metadata"
    assert (bundle_root / "content" / "handoff" / "self_hosted_proof_lock.txt").exists(), "missing staged proof note"
    assert (bundle_root / "content" / "tests" / "test_self_hosted_proof_lock_current.py").exists(), "missing staged proof test"


def test_current_manifest_stays_wrapper_self_hosted() -> None:
    manifest_path = _latest_bundle_root() / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["patch_name"] == PATCH_NAME
    assert manifest["active_profile"] == "generic_python"
    assert manifest["target_project_root"].replace("\\", "/").endswith("/patchops")

    written_paths = {entry["path"] for entry in manifest["files_to_write"]}
    assert "handoff/self_hosted_proof_lock.txt" in written_paths
    assert "tests/test_self_hosted_proof_lock_current.py" in written_paths

    validation = manifest["validation_commands"]
    assert len(validation) == 1
    assert validation[0]["program"] == "py"
    assert validation[0]["args"] == [
        "-m",
        "pytest",
        "-q",
        "tests/test_self_hosted_proof_lock_current.py",
    ]


def test_existing_future_bundle_surface_still_exists_for_continuation() -> None:
    final_bundle = PROJECT_ROOT / "handoff" / "final_future_llm_source_bundle.txt"
    assert final_bundle.exists(), "missing existing future-LLM continuation bundle"
    text = final_bundle.read_text(encoding="utf-8").lower()
    assert "preferred history-compression artifact" in text
