from __future__ import annotations

import json
from pathlib import Path

import pytest

from patchops import cli


def test_setup_windows_env_help_exposes_current_live_flags(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["setup-windows-env", "--help"])

    assert exc.value.code == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err

    assert "usage: patchops setup-windows-env" in text
    assert "--wrapper-root" in text
    assert "--reports-root" in text
    assert "--bin-root" in text
    assert "--dry-run" in text
    assert r"Desktop\PatchOpsReports" in text
    assert r"%USERPROFILE%\bin\PatchOps" in text


def test_setup_windows_env_dry_run_prints_current_payload_shape(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    wrapper_root = tmp_path / "wrapper"
    reports_root = tmp_path / "Desktop" / "PatchOpsReports"
    bin_root = tmp_path / "bin" / "PatchOps"

    exit_code = cli.main(
        [
            "setup-windows-env",
            "--dry-run",
            "--wrapper-root",
            str(wrapper_root),
            "--reports-root",
            str(reports_root),
            "--bin-root",
            str(bin_root),
        ]
    )

    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["applied"] is False
    assert payload["dry_run"] is True
    assert payload["env_vars"]["PATCHOPS_WRAPPER_ROOT"] == str(wrapper_root.resolve())
    assert payload["env_vars"]["PATCHOPS_REPORTS_ROOT"] == str(reports_root)
    assert payload["env_vars"]["PATCHOPS_BIN"] == str(bin_root)
