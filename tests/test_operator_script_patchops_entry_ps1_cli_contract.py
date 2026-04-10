from __future__ import annotations

import pytest

from patchops import cli


def test_emit_operator_script_help_exposes_patchops_entry_ps1_kind(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["emit-operator-script", "--help"])

    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err
    assert "usage: patchops emit-operator-script" in text
    assert "run-package-zip" in text
    assert "maintenance-gate" in text
    assert "patchops-entry-ps1" in text
