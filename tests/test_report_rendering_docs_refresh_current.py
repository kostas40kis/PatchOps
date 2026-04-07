from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_report_rendering_contract_doc_contains_current_helper_truth() -> None:
    doc_path = PROJECT_ROOT / "docs" / "report_rendering_contract.md"
    text = doc_path.read_text(encoding="utf-8").lower()

    required_phrases = [
        "one canonical desktop txt report",
        "render_report_header",
        "render_report_command_output_section",
        "render_command_output_section",
        "build_report_command_section",
        "empty stdout",
        "empty stderr",
        "fail-closed",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"report_rendering_contract.md is missing required phrases: {missing}"
