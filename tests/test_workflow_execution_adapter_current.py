from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_apply_and_verify_use_common_execution_adapter() -> None:
    apply_text = _read("patchops/workflows/apply_patch.py")
    verify_text = _read("patchops/workflows/verify_only.py")

    assert "execute_command_group(" in apply_text
    assert "execute_command_group(" in verify_text
    assert "from patchops.execution.process_runner import run_command" not in apply_text
    assert "from patchops.execution.process_runner import run_command" not in verify_text


def test_common_module_exposes_single_execution_adapter() -> None:
    common_text = _read("patchops/workflows/common.py")

    assert "def execute_command_group(" in common_text
    assert "classify_command_failure" in common_text
    assert "run_command(" in common_text
