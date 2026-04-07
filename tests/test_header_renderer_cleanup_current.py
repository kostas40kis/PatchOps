from __future__ import annotations

from pathlib import Path

import patchops.reporting.sections as reporting_sections


def test_header_section_delegates_directly_to_render_report_header(monkeypatch) -> None:
    sentinel = object()

    def fail_build_report_header_metadata(*args, **kwargs):
        raise AssertionError("header_section should no longer pre-build metadata directly")

    def fake_render_report_header(value):
        assert value is sentinel
        return "HEADER TEXT"

    monkeypatch.setattr(reporting_sections, "build_report_header_metadata", fail_build_report_header_metadata)
    monkeypatch.setattr(reporting_sections, "render_report_header", fake_render_report_header)

    assert reporting_sections.header_section(sentinel) == "HEADER TEXT"


def test_sections_module_current_source_uses_shared_header_renderer_helper() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    text = (repo_root / "patchops" / "reporting" / "sections.py").read_text(encoding="utf-8")

    assert "def header_section(result: WorkflowResult) -> str:" in text
    assert "return render_report_header(result)" in text
    assert "render_report_header(build_report_header_metadata(result))" not in text
