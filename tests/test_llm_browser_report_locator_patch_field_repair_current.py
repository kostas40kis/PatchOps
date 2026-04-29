from __future__ import annotations

from pathlib import Path

from patchops.llm_browser.report_locator import parse_report_summary


def test_report_summary_patch_field_does_not_match_patchops_heading(tmp_path: Path) -> None:
    report = tmp_path / "patchops_run_package_20260429_191828.txt"
    report.write_text(
        """
PATCHOPS RUN-PACKAGE OUTER REPORT
---------------------------------
Result              : FAIL
Exit Code           : 1
Failure Category    : target_content_failure

RESULT
======
Patch      : D0.17 canonical report locator
""",
        encoding="utf-8",
    )

    summary = parse_report_summary(report)

    assert summary.patch == "D0.17 canonical report locator"


def test_report_summary_patch_is_none_when_only_heading_contains_patchops(tmp_path: Path) -> None:
    report = tmp_path / "patchops_run_package_20260429_191828.txt"
    report.write_text(
        """
PATCHOPS RUN-PACKAGE OUTER REPORT
---------------------------------
Result              : PASS
ExitCode            : 0
""",
        encoding="utf-8",
    )

    summary = parse_report_summary(report)

    assert summary.patch is None
    assert summary.passed is True
