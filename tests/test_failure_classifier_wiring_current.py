from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_common_workflow_path_keeps_classifier_helper_visible() -> None:
    common_text = _read("patchops/workflows/common.py")

    assert "def execute_command_group(" in common_text
    assert "classify_command_failure" in common_text
    assert "CommandResult" in common_text


def test_verify_only_stable_path_still_routes_through_common_execution_group() -> None:
    verify_text = _read("patchops/workflows/verify_only.py")

    assert "execute_command_group(" in verify_text
    assert "from patchops.workflows.common import" in verify_text


def test_apply_path_remains_on_same_common_execution_surface() -> None:
    apply_text = _read("patchops/workflows/apply_patch.py")

    assert "execute_command_group(" in apply_text
    assert "from patchops.workflows.common import" in apply_text
