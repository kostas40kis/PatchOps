from __future__ import annotations

import pytest

from patchops import cli


def test_inspect_help_exposes_current_live_surface(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["inspect", "--help"])

    assert exc.value.code == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err

    assert "usage: patchops inspect" in text
    assert "inspect" in text.lower()
