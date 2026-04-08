\
from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import patchops.reporting.sections as reporting_sections


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _test_header_section_delegates_directly_to_render_report_header() -> None:
    sentinel = object()

    def fail_build_report_header_metadata(*args, **kwargs):
        raise AssertionError("header_section should no longer pre-build metadata directly")

    def fake_render_report_header(value):
        _assert(value is sentinel, "header_section no longer forwards the original value directly to render_report_header")
        return "HEADER TEXT"

    original_build = reporting_sections.build_report_header_metadata
    original_render = reporting_sections.render_report_header
    try:
        reporting_sections.build_report_header_metadata = fail_build_report_header_metadata
        reporting_sections.render_report_header = fake_render_report_header
        _assert(reporting_sections.header_section(sentinel) == "HEADER TEXT", "header_section no longer returns render_report_header output directly")
    finally:
        reporting_sections.build_report_header_metadata = original_build
        reporting_sections.render_report_header = original_render


def _test_sections_module_current_source_uses_shared_header_renderer_helper() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    text = (repo_root / "patchops" / "reporting" / "sections.py").read_text(encoding="utf-8")

    _assert("def header_section(result: WorkflowResult) -> str:" in text, "header_section definition drifted")
    _assert("return render_report_header(result)" in text, "header_section no longer delegates directly to render_report_header(result)")
    _assert("render_report_header(build_report_header_metadata(result))" not in text, "header_section reverted to pre-building header metadata inline")


def main() -> int:
    _test_header_section_delegates_directly_to_render_report_header()
    _test_sections_module_current_source_uses_shared_header_renderer_helper()
    print("report-header-renderer truth-lock validation PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
