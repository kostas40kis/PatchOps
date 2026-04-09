from __future__ import annotations

import pytest

from patchops import cli


def test_maintenance_gate_help_exposes_current_live_flags(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["maintenance-gate", "--help"])

    assert exc.value.code == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err

    assert "usage: patchops maintenance-gate" in text

    required_flags = [
        "--wrapper-root",
        "--profile",
        "--core-tests-green",
        "--report-path",
    ]
    for flag in required_flags:
        assert flag in text
