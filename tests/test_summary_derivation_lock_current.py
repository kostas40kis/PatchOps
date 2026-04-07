from __future__ import annotations

from pathlib import Path

from patchops.reporting.summary import render_summary


def test_render_summary_preserves_exact_pass_shape() -> None:
    text = render_summary(0, "PASS")

    assert text == "\n".join(
        [
            "SUMMARY",
            "-------",
            "ExitCode : 0",
            "Result   : PASS",
        ]
    )


def test_render_summary_preserves_exact_fail_shape() -> None:
    text = render_summary(7, "FAIL")

    assert text == "\n".join(
        [
            "SUMMARY",
            "-------",
            "ExitCode : 7",
            "Result   : FAIL",
        ]
    )


def test_summary_integrity_stream_records_fail_closed_rules() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    doc_path = repo_root / "docs" / "summary_integrity_repair_stream.md"
    text = doc_path.read_text(encoding="utf-8").lower()

    required_phrases = [
        "required validation failure outside `allowed_exit_codes` forces rendered summary `fail`",
        "required smoke failure outside `allowed_exit_codes` forces rendered summary `fail`",
        "the first required failure remains sticky even if later required commands succeed",
        "explicitly tolerated non-zero exits still remain `pass`",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"summary-integrity stream doc is missing required phrases: {missing}"
