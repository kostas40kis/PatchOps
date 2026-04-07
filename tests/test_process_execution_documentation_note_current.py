from __future__ import annotations

from pathlib import Path


def test_process_execution_documentation_note_keeps_python_owned_path_explicit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    text = (repo_root / "docs" / "overview.md").read_text(encoding="utf-8").lower()

    required_phrases = [
        "preferred internal path",
        "run_command_result",
        "normalize_execution_result",
        "executionresult",
        "patchops.execution.process_runner",
        "patchops.execution.result_model",
        "ad hoc subprocess loops",
        "powershell patch bodies",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"overview execution note missing required phrases: {missing}"
