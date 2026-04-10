from __future__ import annotations

import pytest

from patchops import cli
from patchops.package_runner import cli_main


def test_package_runner_exports_cli_main() -> None:
    assert callable(cli_main)


def test_run_package_help_survives_cli_import_chain(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["run-package", "--help"])

    assert exc.value.code == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err

    assert "usage: patchops run-package" in text
    assert "--wrapper-root" in text
