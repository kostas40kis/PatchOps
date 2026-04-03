from __future__ import annotations

import pytest

from patchops import cli


def test_init_project_doc_help_exposes_current_live_flags(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["init-project-doc", "--help"])

    assert exc.value.code == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err

    assert "usage: patchops init-project-doc" in text

    required_flags = [
        "--project-name",
        "--target-root",
        "--profile",
        "--runtime-path",
        "--initial-goal",
        "--output-path",
        "--wrapper-root",
    ]
    for flag in required_flags:
        assert flag in text
