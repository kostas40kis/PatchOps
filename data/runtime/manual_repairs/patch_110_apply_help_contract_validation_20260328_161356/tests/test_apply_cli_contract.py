from __future__ import annotations

import pytest

from patchops import cli


def test_apply_help_exposes_current_live_flags(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["apply", "--help"])

    assert exc.value.code == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err

    assert "usage: patchops apply" in text
    assert "manifest" in text.lower()
    assert "--wrapper-root" in text
