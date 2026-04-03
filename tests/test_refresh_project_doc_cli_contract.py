from __future__ import annotations

import pytest

from patchops import cli


def test_refresh_project_doc_help_exposes_current_live_flags(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["refresh-project-doc", "--help"])

    assert exc.value.code == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err

    assert "usage: patchops refresh-project-doc" in text

    required_flags = [
        "--project-name",
        "--wrapper-root",
        "--packet-path",
        "--current-phase",
        "--current-objective",
        "--latest-passed-patch",
        "--latest-attempted-patch",
        "--current-recommendation",
        "--next-action",
        "--risk",
    ]
    for flag in required_flags:
        assert flag in text
