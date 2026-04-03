from __future__ import annotations

import pytest

from patchops import cli


def test_doctor_help_exposes_current_live_flags(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["doctor", "--help"])

    assert exc.value.code == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err

    assert "usage: patchops doctor" in text

    required_flags = [
        "--profile",
        "--target-root",
    ]
    for flag in required_flags:
        assert flag in text
