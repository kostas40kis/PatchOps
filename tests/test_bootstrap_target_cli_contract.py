from __future__ import annotations

import pytest

from patchops import cli


def test_bootstrap_target_help_exposes_current_live_flags(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["bootstrap-target", "--help"])

    assert exc.value.code == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err

    assert "usage: patchops bootstrap-target" in text

    required_flags = [
        "--project-name",
        "--target-root",
        "--profile",
        "--wrapper-root",
        "--initial-goal",
    ]
    for flag in required_flags:
        assert flag in text
