from __future__ import annotations

import pytest

from patchops import cli


def test_check_help_exposes_current_live_surface(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["check", "--help"])

    assert exc.value.code == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err

    assert "usage: patchops check" in text
    assert "manifest" in text.lower()
    assert "starter placeholders" in text.lower()
    assert "before apply or verify" in text.lower()
