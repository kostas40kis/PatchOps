from __future__ import annotations

from pathlib import Path


def test_examples_doc_describes_current_handoff_export_usage() -> None:
    text = Path("docs/examples.md").read_text(encoding="utf-8")

    assert "Handoff-first continuation examples" in text
    assert "py -m patchops.cli export-handoff" in text
    assert "handoff/current_handoff.md" in text
    assert "handoff/current_handoff.json" in text
    assert "handoff/latest_report_copy.txt" in text
    assert "handoff/latest_report_index.json" in text
    assert "handoff/next_prompt.txt" in text
    assert "handoff/bundle/current/" in text
    assert "Do **not** use handoff as the first step when the job is to onboard a brand-new target project." in text
    assert "project packet = maintained target-facing contract" in text
    assert "report = evidence of what happened." in text
