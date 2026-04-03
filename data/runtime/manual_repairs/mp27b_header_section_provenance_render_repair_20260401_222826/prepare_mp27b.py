from __future__ import annotations

import json
from pathlib import Path
import sys
import textwrap

PATCH_NAME = "mp27b_header_section_provenance_render_repair"

IMPORT_LINE = "from patchops.reporting.metadata import build_report_header_metadata, render_report_header"
NEW_FUNCTION = [
    "def header_section(result: WorkflowResult) -> str:",
    "    return render_report_header(build_report_header_metadata(result))",
    "",
]

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def ensure_import(source: str) -> str:
    if IMPORT_LINE in source:
        return source
    lines = source.splitlines()
    insert_at = 0
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("from ") or stripped.startswith("import "):
            insert_at = idx + 1
    lines.insert(insert_at, IMPORT_LINE)
    return "\n".join(lines) + ("\n" if source.endswith("\n") else "")

def replace_top_level_function(source: str, function_name: str, new_lines: list[str]) -> str:
    lines = source.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.startswith(f"def {function_name}("):
            start = idx
            break
    if start is None:
        raise RuntimeError(f"Could not find top-level function: {function_name}")

    end = len(lines)
    for idx in range(start + 1, len(lines)):
        line = lines[idx]
        if line.startswith("def ") or line.startswith("class "):
            end = idx
            break

    replaced = lines[:start] + new_lines + lines[end:]
    return "\n".join(replaced) + "\n"

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
                "patch_name": "mp27b_header_section_bridge",
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
                    "report_name_prefix": "mp27b_header_section_bridge",
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
    ).strip() + "\n"

def main() -> int:
    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    content_root = working_root / "content"

    sections_path = wrapper_root / "patchops" / "reporting" / "sections.py"
    test_path = wrapper_root / "tests" / "test_header_section_bridge_current.py"

    sections_source = sections_path.read_text(encoding="utf-8")
    uses_metadata_renderer_before = "render_report_header(build_report_header_metadata(result))" in sections_source
    bridge_test_exists_before = test_path.exists()

    patched = ensure_import(sections_source)
    patched = replace_top_level_function(patched, "header_section", NEW_FUNCTION)

    staged = {
        "patchops/reporting/sections.py": patched,
        "tests/test_header_section_bridge_current.py": build_test_text(),
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