from pathlib import Path
import re
from textwrap import dedent

project_root = Path(r"C:\dev\patchops")
metadata_path = project_root / "patchops" / "reporting" / "metadata.py"
sections_path = project_root / "patchops" / "reporting" / "sections.py"
test_path = project_root / "tests" / "test_report_header_current.py"

metadata_text = dedent(
    """
    from __future__ import annotations

    from dataclasses import dataclass
    from datetime import datetime
    from pathlib import Path
    from typing import Any

    from patchops.models import WorkflowResult
    from patchops.workflows.common import infer_workspace_root


    @dataclass(frozen=True)
    class ReportMetadata:
        patch_name: str
        timestamp: str
        workspace_root: Path | None
        wrapper_project_root: Path | None
        target_project_root: Path
        active_profile: str | None
        runtime_path: Path | None
        report_path: Path
        manifest_path: Path | None


    def _coerce_path(value: Any) -> Path | None:
        if value in (None, ""):
            return None
        return Path(str(value))


    def _coerce_timestamp(value: Any) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, str) and value.strip():
            return value.strip()
        return "(unknown)"


    def build_report_metadata(result: WorkflowResult) -> ReportMetadata:
        target_project_root = Path(str(result.target_project_root))
        workspace_root = infer_workspace_root(target_project_root)

        wrapper_candidate = (
            getattr(result, "wrapper_project_root", None)
            or getattr(result, "wrapper_root", None)
        )
        wrapper_project_root = _coerce_path(wrapper_candidate)
        if wrapper_project_root is None:
            wrapper_project_root = workspace_root

        runtime_candidate = (
            getattr(result, "runtime_path", None)
            or getattr(result, "resolved_runtime_path", None)
            or getattr(result.profile, "runtime_path", None)
        )

        manifest_path = _coerce_path(getattr(result, "manifest_path", None))
        timestamp_value = (
            getattr(result, "generated_at", None)
            or getattr(result, "timestamp", None)
            or getattr(result, "started_at", None)
        )

        return ReportMetadata(
            patch_name=str(result.manifest.patch_name),
            timestamp=_coerce_timestamp(timestamp_value),
            workspace_root=workspace_root,
            wrapper_project_root=wrapper_project_root,
            target_project_root=target_project_root,
            active_profile=getattr(result.manifest, "active_profile", None),
            runtime_path=_coerce_path(runtime_candidate),
            report_path=Path(str(result.report_path)),
            manifest_path=manifest_path,
        )


    def render_report_header_lines(mode: str, metadata: ReportMetadata) -> tuple[str, ...]:
        lines: list[str] = [
            f"PATCHOPS {mode.upper()}",
            f"Patch Name           : {metadata.patch_name}",
            f"Timestamp            : {metadata.timestamp}",
        ]

        if metadata.workspace_root is not None:
            lines.append(f"Workspace Root       : {metadata.workspace_root}")
        if metadata.wrapper_project_root is not None:
            lines.append(f"Wrapper Project Root : {metadata.wrapper_project_root}")

        lines.append(f"Target Project Root  : {metadata.target_project_root}")

        if metadata.active_profile:
            lines.append(f"Active Profile       : {metadata.active_profile}")
        if metadata.runtime_path is not None:
            lines.append(f"Runtime Path         : {metadata.runtime_path}")

        lines.append(f"Report Path          : {metadata.report_path}")

        if metadata.manifest_path is not None:
            lines.append(f"Manifest Path        : {metadata.manifest_path}")

        return tuple(lines)
    """
).lstrip()

sections_text = sections_path.read_text(encoding="utf-8")

# If the import isn't present, insert it (unchanged)
if "from patchops.reporting.metadata import build_report_metadata, render_report_header_lines" not in sections_text:
    needle = "from patchops.models import BackupRecord, CommandResult, WorkflowResult, WriteRecord\n"
    replacement = needle + "from patchops.reporting.metadata import build_report_metadata, render_report_header_lines\n"
    if needle not in sections_text:
        raise RuntimeError("Could not find models import line in sections.py.")
    sections_text = sections_text.replace(needle, replacement, 1)

# Robustly locate the header_section definition and replace it up to the next top-level def
start_match = re.search(r"^def\s+header_section\(.*\):", sections_text, re.MULTILINE)
if not start_match:
    raise RuntimeError("Could not locate header_section block in sections.py.")

start_idx = start_match.start()

# Find the next top-level "def <name>(" after the start; if none, replace to EOF
next_def = re.search(r"^def\s+\w+\s*\(", sections_text[start_idx + 1:], re.MULTILINE)
if next_def:
    end_idx = start_idx + 1 + next_def.start()
else:
    end_idx = len(sections_text)

new_header = dedent(
    """
    def header_section(result: WorkflowResult) -> str:
        metadata = build_report_metadata(result)
        return "\\n".join(render_report_header_lines(result.mode, metadata))


    """
)

sections_text = sections_text[:start_idx] + new_header + sections_text[end_idx:]

test_text = dedent(
    """
    from pathlib import Path

    from patchops.models import Manifest, ResolvedProfile, WorkflowResult
    from patchops.reporting.metadata import build_report_metadata, render_report_header_lines
    from patchops.reporting.sections import header_section


    def _build_result(tmp_path: Path, mode: str = "apply") -> WorkflowResult:
        target_root = tmp_path / "target_project"
        target_root.mkdir(parents=True, exist_ok=True)
        report_path = tmp_path / "report.txt"
        manifest = Manifest(
            manifest_version="1",
            patch_name="header_cleanup_patch",
            active_profile="generic_python",
        )
        profile = ResolvedProfile(
            name="generic_python",
            target_project_root=target_root,
            runtime_path=None,
            backup_root=target_root / "backups",
        )
        return WorkflowResult(
            mode=mode,
            manifest=manifest,
            profile=profile,
            target_project_root=target_root,
            report_path=report_path,
            backup_records=[],
            write_records=[],
            validation_results=[],
            smoke_results=[],
            audit_results=[],
            cleanup_results=[],
            archive_results=[],
            exit_code=0,
            result_label="PASS",
            failure=None,
        )


    def test_build_report_metadata_captures_header_values(tmp_path: Path) -> None:
        result = _build_result(tmp_path)
        metadata = build_report_metadata(result)

        assert metadata.patch_name == "header_cleanup_patch"
        assert metadata.target_project_root == result.target_project_root
        assert metadata.active_profile == "generic_python"
        assert metadata.report_path == result.report_path


    def test_render_report_header_lines_preserves_expected_shape(tmp_path: Path) -> None:
        result = _build_result(tmp_path, mode="verify_only")
        metadata = build_report_metadata(result)
        lines = render_report_header_lines(result.mode, metadata)

        assert lines[0] == "PATCHOPS VERIFY_ONLY"
        assert "Patch Name           : header_cleanup_patch" in lines
        assert f"Target Project Root  : {result.target_project_root}" in lines
        assert f"Active Profile       : {result.manifest.active_profile}" in lines
        assert f"Report Path          : {result.report_path}" in lines


    def test_header_section_renders_from_metadata_helper(tmp_path: Path) -> None:
        result = _build_result(tmp_path)
        expected = "\\n".join(render_report_header_lines(result.mode, build_report_metadata(result)))

        assert header_section(result) == expected
    """
).lstrip()

metadata_path.write_text(metadata_text, encoding="utf-8")
sections_path.write_text(sections_text, encoding="utf-8")
test_path.write_text(test_text, encoding="utf-8")

print(str(metadata_path))
print(str(sections_path))
print(str(test_path))