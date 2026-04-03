from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import textwrap

PATCH_NAME = "mp27a_header_section_provenance_render_repair"

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def patch_sections_text(source: str) -> str:
    import_line = "from patchops.reporting.metadata import build_report_header_metadata, render_report_header"
    if import_line not in source:
        marker = "from patchops.models import BackupRecord, CommandResult, WorkflowResult, WriteRecord"
        if marker not in source:
            raise RuntimeError("Could not find models import in sections.py")
        source = source.replace(marker, marker + "\\n" + import_line)

    pattern = re.compile(
        r"def header_section\\(result: WorkflowResult\\) -> str:\\n(?:    .*\\n)+?(?=\\n\\ndef wrapper_only_retry_section)",
        re.MULTILINE,
    )
    replacement = textwrap.dedent(
        """
        def header_section(result: WorkflowResult) -> str:
            return render_report_header(build_report_header_metadata(result))
        """
    ).strip()
    if not pattern.search(source):
        raise RuntimeError("Could not find header_section block in sections.py")
    source = pattern.sub(replacement, source)
    return source

def build_test_text() -> str:
    return textwrap.dedent(
        """
        from __future__ import annotations

        import json
        from pathlib import Path

        from patchops.reporting import build_report_header_metadata, render_report_header
        from patchops.reporting.sections import header_section
        from patchops.workflows.apply_patch import apply_manifest


        def test_header_section_delegates_to_metadata_renderer(tmp_path: Path) -> None:
            wrapper_root = tmp_path / "wrapper_root"
            manifest_root = tmp_path / "manifest_root"
            target_root = tmp_path / "target_root"
            report_dir = tmp_path / "reports"

            wrapper_root.mkdir(parents=True, exist_ok=True)
            manifest_root.mkdir(parents=True, exist_ok=True)
            target_root.mkdir(parents=True, exist_ok=True)
            report_dir.mkdir(parents=True, exist_ok=True)

            manifest_path = manifest_root / "patch_manifest.json"
            manifest_data = {
                "manifest_version": "1",
                "patch_name": "mp27a_header_section_bridge",
                "active_profile": "generic_python",
                "target_project_root": str(target_root),
                "backup_files": [],
                "files_to_write": [],
                "validation_commands": [],
                "smoke_commands": [],
                "audit_commands": [],
                "cleanup_commands": [],
                "archive_commands": [],
                "failure_policy": {},
                "report_preferences": {
                    "report_dir": str(report_dir),
                    "report_name_prefix": "mp27a_header_section_bridge",
                    "write_to_desktop": False,
                },
            }
            manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\\n", encoding="utf-8")

            result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

            expected = render_report_header(build_report_header_metadata(result))
            actual = header_section(result)

            assert actual == expected
            assert "Wrapper Mode Used    : apply" in actual
            assert f"Manifest Path Used   : {manifest_path.resolve()}" in actual
        """
    ).strip() + "\\n"

def main() -> int:
    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    content_root = working_root / "content"

    sections_path = wrapper_root / "patchops" / "reporting" / "sections.py"
    test_path = wrapper_root / "tests" / "test_header_section_bridge_current.py"

    sections_source = sections_path.read_text(encoding="utf-8")
    uses_metadata_renderer_before = "render_report_header(build_report_header_metadata(result))" in sections_source
    bridge_test_exists_before = test_path.exists()

    patched_sections = patch_sections_text(sections_source)
    bridge_test = build_test_text()

    staged = {
        "patchops/reporting/sections.py": patched_sections,
        "tests/test_header_section_bridge_current.py": bridge_test,
    }

    for relative_path, content in staged.items():
        write_text(content_root / relative_path, content)

    audit = {
        "patch_name": PATCH_NAME,
        "sections_path": str(sections_path),
        "test_path": str(test_path),
        "uses_metadata_renderer_before": uses_metadata_renderer_before,
        "bridge_test_exists_before": bridge_test_exists_before,
        "staged_files": [str((content_root / path).resolve()) for path in staged.keys()],
    }
    write_text(working_root / "prepare_audit.txt", json.dumps(audit, indent=2) + "\\n")
    print(f"Prepared audit   : {working_root / 'prepare_audit.txt'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())