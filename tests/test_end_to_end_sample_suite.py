import json
import subprocess
import sys
from pathlib import Path

from patchops.workflows.verify_only import build_verify_only_flow_state
from patchops.workflows.wrapper_retry import build_wrapper_only_retry_state, wrapper_only_retry_allows_writes


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APPLY_EXAMPLE = PROJECT_ROOT / "examples" / "generic_python_patch.json"
VERIFY_EXAMPLE = PROJECT_ROOT / "examples" / "generic_verify_patch.json"
FAILURE_GUIDE = PROJECT_ROOT / "docs" / "failure_repair_guide.md"


def _run_cli_plan(manifest_path: Path, mode: str | None = None) -> dict:
    args = [sys.executable, "-m", "patchops.cli", "plan", str(manifest_path)]
    if mode:
        args.extend(["--mode", mode])
    completed = subprocess.run(
        args,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(completed.stdout)


def test_apply_flow_sample_plan_is_coherent() -> None:
    payload = _run_cli_plan(APPLY_EXAMPLE)

    assert payload["patch_name"] == "generic_stage1_example_patch"
    assert payload["active_profile"] == "generic_python"
    assert payload["manifest_path"].endswith("generic_python_patch.json")
    assert len(payload["validation_commands"]) >= 1


def test_verify_only_flow_sample_plan_is_coherent_and_skips_writes() -> None:
    payload = _run_cli_plan(VERIFY_EXAMPLE, mode="verify")
    manifest = json.loads(VERIFY_EXAMPLE.read_text(encoding="utf-8"))
    state = build_verify_only_flow_state(manifest, PROJECT_ROOT)

    assert payload["mode"] == "verify"
    assert payload["patch_name"] == "generic_stage1_example_verify"
    assert state.mode == "verify"
    assert state.writes_skipped is True
    assert state.validation_command_count >= 1


def test_wrapper_retry_surface_is_visible_for_sample_manifest() -> None:
    manifest = json.loads(VERIFY_EXAMPLE.read_text(encoding="utf-8"))
    state = build_wrapper_only_retry_state(
        manifest,
        PROJECT_ROOT,
        reason="reporting failed after likely successful validation",
    )

    assert state.mode == "verify"
    assert state.writes_skipped is True
    assert wrapper_only_retry_allows_writes(state) is False


def test_failure_classification_surface_is_visible_in_guide() -> None:
    text = FAILURE_GUIDE.read_text(encoding="utf-8")
    assert "Content failure" in text
    assert "Wrapper failure" in text
    assert "Verification-only rerun" in text
    assert "Wrapper-only repair" in text


def test_end_to_end_sample_suite_proves_apply_verify_and_classification_together() -> None:
    apply_payload = _run_cli_plan(APPLY_EXAMPLE)
    verify_payload = _run_cli_plan(VERIFY_EXAMPLE, mode="verify")

    assert apply_payload["mode"] == "apply"
    assert verify_payload["mode"] == "verify"
    assert apply_payload["patch_name"] != verify_payload["patch_name"]
    assert "report_path_pattern" in apply_payload
    assert "report_path_pattern" in verify_payload
