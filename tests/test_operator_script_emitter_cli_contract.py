from __future__ import annotations

import pytest

from patchops import cli


def test_emit_operator_script_help_exposes_current_flags(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["emit-operator-script", "--help"])

    assert excinfo.value.code == 0
    text = capsys.readouterr().out
    assert "usage: patchops emit-operator-script" in text
    assert "run-package-zip" in text
    assert "maintenance-gate" in text
    assert "--wrapper-root" in text
    assert "--bundle-zip-path" in text
