from __future__ import annotations

import pytest

from patchops import cli


def test_export_handoff_help_exposes_current_live_flags(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["export-handoff", "--help"])

    assert exc.value.code == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err

    assert "usage: patchops export-handoff" in text

    required_flags = [
        "--report-path",
        "--wrapper-root",
        "--current-stage",
        "--bundle-name",
    ]
    for flag in required_flags:
        assert flag in text
