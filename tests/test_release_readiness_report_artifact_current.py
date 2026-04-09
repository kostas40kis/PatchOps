from __future__ import annotations

import json
from pathlib import Path

from patchops.cli import main
from tests.test_release_readiness_command import _seed_release_ready_repo


def test_release_readiness_report_artifact_matches_current_contract(tmp_path: Path, capsys) -> None:
    _seed_release_ready_repo(tmp_path)
    report_path = tmp_path / "evidence" / "release_readiness.txt"

    exit_code = main(
        [
            "release-readiness",
            "--wrapper-root",
            str(tmp_path),
            "--profile",
            "trader",
            "--core-tests-green",
            "--report-path",
            str(report_path),
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    report_text = report_path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert payload["report_path"] == str(report_path.resolve())
    assert report_text.startswith("PATCHOPS RELEASE READINESS\n")
    assert f"Wrapper Project   : {tmp_path.resolve()}" in report_text
    assert "Focused Profile   : trader" in report_text
    assert "Status            : green" in report_text
    assert "Core Tests        : green" in report_text
    assert "Tests             : ok" in report_text
    assert "Bundle Docs       : ok" in report_text
    assert "Bundle Workflows  : ok" in report_text
    assert "Bundle Tests      : ok" in report_text
    assert "MISSING BUNDLE RELEASE DOCS" in report_text
    assert "MISSING BUNDLE RELEASE WORKFLOWS" in report_text
    assert "MISSING BUNDLE RELEASE TESTS" in report_text
    assert "NOTES" in report_text
    assert report_text.endswith(
        "Use --core-tests-green only when the green test state was already proven externally.\n"
    )
