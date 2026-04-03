from __future__ import annotations

import pytest

from patchops import cli


def test_refresh_project_doc_help_exposes_artifact_inputs_and_mutable_overrides(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["refresh-project-doc", "--help"])

    assert exc.value.code == 0
    captured = capsys.readouterr()
    text = captured.out + captured.err

    assert "Refresh the mutable section of an existing project packet under docs/projects/" in text
    assert "Refresh the mutable packet state from explicit inputs and optional handoff/report artifacts." in text

    required_flags = [
        "--packet-path",
        "--handoff-json-path",
        "--report-path",
        "--current-phase",
        "--current-objective",
        "--latest-passed-patch",
        "--latest-attempted-patch",
        "--current-recommendation",
        "--next-action",
        "--blocker",
        "--wrapper-root",
        "--project-name",
    ]
    for flag in required_flags:
        assert flag in text
