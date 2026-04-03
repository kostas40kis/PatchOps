from __future__ import annotations

import pytest

from patchops import cli


def _help_text(args: list[str], capsys: pytest.CaptureFixture[str]) -> str:
    with pytest.raises(SystemExit) as exc:
        cli.main(args)
    assert exc.value.code == 0
    captured = capsys.readouterr()
    return captured.out + captured.err


def test_recommend_profile_help_exposes_current_live_flags(capsys: pytest.CaptureFixture[str]) -> None:
    text = _help_text(["recommend-profile", "--help"], capsys)

    assert "usage: patchops recommend-profile" in text

    required_flags = [
        "--target-root",
        "--wrapper-root",
    ]
    for flag in required_flags:
        assert flag in text


def test_starter_help_exposes_current_live_flags(capsys: pytest.CaptureFixture[str]) -> None:
    text = _help_text(["starter", "--help"], capsys)

    assert "usage: patchops starter" in text

    required_flags = [
        "--profile",
        "--intent",
        "--target-root",
        "--patch-name",
        "--wrapper-root",
    ]
    for flag in required_flags:
        assert flag in text
