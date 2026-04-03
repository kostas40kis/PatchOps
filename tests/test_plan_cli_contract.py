from __future__ import annotations

import pytest

from patchops import cli


def test_plan_help_exposes_current_live_flags(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["plan", "--help"])

    assert exc.value.code == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err

    assert "usage: patchops plan" in text
    assert "manifest" in text.lower()

    required_fragments = [
        "--wrapper-root",
        "--mode",
        "--retry-reason",
        "wrapper_retry",
    ]
    for fragment in required_fragments:
        assert fragment in text
