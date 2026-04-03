from __future__ import annotations

import pytest

from patchops import cli


def test_wrapper_retry_help_exposes_current_live_flags(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["wrapper-retry", "--help"])

    assert exc.value.code == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err

    assert "usage: patchops wrapper-retry" in text
    assert "manifest" in text.lower()
    assert "--wrapper-root" in text
    assert "--retry-reason" in text
