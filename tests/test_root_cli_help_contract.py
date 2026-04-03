from __future__ import annotations

import pytest

from patchops import cli


def test_root_help_exposes_current_live_operator_surface(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["--help"])

    assert exc.value.code == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err

    assert "usage: patchops" in text

    required_commands = [
        "apply",
        "verify",
        "wrapper-retry",
        "profiles",
        "doctor",
        "examples",
        "schema",
        "check",
        "inspect",
        "plan",
        "template",
        "export-handoff",
        "bootstrap-target",
        "recommend-profile",
        "starter",
        "init-project-doc",
        "refresh-project-doc",
        "release-readiness",
    ]
    for command in required_commands:
        assert command in text
