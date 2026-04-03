from __future__ import annotations

import json
import sys
from pathlib import Path


PATCH_NAME = "mp21_single_file_writer_helper"


def replace_function(source: str, function_name: str, replacement: str) -> str:
    marker = f"def {function_name}("
    start = source.find(marker)
    if start == -1:
        raise RuntimeError(f"Could not find function: {function_name}")
    next_start = source.find("\ndef ", start + 1)
    if next_start == -1:
        end = len(source)
    else:
        end = next_start + 1
    updated = source[:start] + replacement.rstrip() + "\n"
    if end < len(source):
        updated += source[end:]
    return updated


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: prepare_mp21.py <project_root> <working_root>")

    project_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    content_root = working_root / "content"
    inner_report_dir = working_root / "inner_reports"
    manifest_path = working_root / "patch_manifest.json"
    audit_path = working_root / "prepare_audit.txt"

    writers_path = project_root / "patchops" / "files" / "writers.py"
    models_path = project_root / "patchops" / "models.py"
    write_plan_test_path = project_root / "tests" / "test_write_plan_current.py"

    writers_text = writers_path.read_text(encoding="utf-8")
    models_text = models_path.read_text(encoding="utf-8")

    audit = {
        "patch_name": PATCH_NAME,
        "writers_path": str(writers_path),
        "models_path": str(models_path),
        "write_plan_test_path": str(write_plan_test_path),
        "writers_exists": writers_path.exists(),
        "models_exists": models_path.exists(),
        "load_content_exists": "def load_content(" in writers_text,
        "write_text_file_exists": "def write_text_file(" in writers_text,
        "write_single_file_exists_before": "def write_single_file(" in writers_text,
        "write_plan_exists": "WritePlan" in writers_text or "WritePlan" in models_text,
        "build_write_plan_exists": "build_write_plan" in writers_text,
        "write_plan_test_exists": write_plan_test_path.exists(),
    }

    missing = []
    if not audit["load_content_exists"]:
        missing.append("load_content missing from patchops/files/writers.py")
    if not audit["write_text_file_exists"]:
        missing.append("write_text_file missing from patchops/files/writers.py")
    if not audit["write_plan_exists"]:
        missing.append("WritePlan surface missing from current repo truth")
    if not audit["build_write_plan_exists"]:
        missing.append("build_write_plan surface missing from current repo truth")
    if not audit["write_plan_test_exists"]:
        missing.append("tests/test_write_plan_current.py missing from current repo truth")

    if missing:
        audit["baseline_ok"] = False
        audit["baseline_errors"] = missing
        audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
        raise SystemExit("MP20 baseline not confirmed:\n- " + "\n- ".join(missing))

    helper_block = (
        'def write_single_file(destination: Path, content: str, encoding: str = "utf-8") -> WriteRecord:\n'
        '    ensure_directory(destination.parent)\n'
        '    destination.write_text(content, encoding=encoding)\n'
        '    return WriteRecord(path=destination, encoding=encoding)\n'
    )

    write_text_wrapper = (
        'def write_text_file(destination: Path, content: str, encoding: str = "utf-8") -> WriteRecord:\n'
        '    return write_single_file(destination, content, encoding=encoding)\n'
    )

    updated_writers = writers_text
    if "def write_single_file(" not in updated_writers:
        anchor = "def write_text_file("
        index = updated_writers.find(anchor)
        if index == -1:
            raise SystemExit("Could not locate write_text_file anchor in writers.py")
        updated_writers = updated_writers[:index] + helper_block + "\n" + updated_writers[index:]

    updated_writers = replace_function(updated_writers, "write_text_file", write_text_wrapper)
    if not updated_writers.endswith("\n"):
        updated_writers += "\n"

    test_content = '''from __future__ import annotations

from pathlib import Path

from patchops.files.writers import write_single_file, write_text_file
from patchops.models import WriteRecord


def test_write_single_file_creates_parent_directories_and_writes_utf8_without_bom(tmp_path):
    destination = tmp_path / "nested" / "folder" / "note.txt"
    content = "hello â€“ ÎšÎ±Î»Î·Î¼Î­ÏÎ±"

    record = write_single_file(destination, content, encoding="utf-8")

    assert isinstance(record, WriteRecord)
    assert record.path == destination
    assert record.encoding == "utf-8"
    assert destination.read_text(encoding="utf-8") == content
    assert destination.read_bytes() == content.encode("utf-8")


def test_write_text_file_delegates_to_single_file_writer(monkeypatch, tmp_path):
    destination = tmp_path / "delegated.txt"
    expected = WriteRecord(path=destination, encoding="utf-8")
    calls = []

    def fake_write_single_file(inner_destination: Path, inner_content: str, encoding: str = "utf-8") -> WriteRecord:
        calls.append((inner_destination, inner_content, encoding))
        return expected

    monkeypatch.setattr("patchops.files.writers.write_single_file", fake_write_single_file)

    result = write_text_file(destination, "payload", encoding="utf-8")

    assert result is expected
    assert calls == [(destination, "payload", "utf-8")]
'''

    writer_target = content_root / "patchops" / "files" / "writers.py"
    writer_target.parent.mkdir(parents=True, exist_ok=True)
    writer_target.write_text(updated_writers, encoding="utf-8")

    test_target = content_root / "tests" / "test_single_file_writer_current.py"
    test_target.parent.mkdir(parents=True, exist_ok=True)
    test_target.write_text(test_content, encoding="utf-8")

    manifest = {
        "manifest_version": "1",
        "patch_name": PATCH_NAME,
        "active_profile": "generic_python",
        "target_project_root": str(project_root),
        "backup_files": [
            "patchops/files/writers.py",
            "tests/test_single_file_writer_current.py",
        ],
        "files_to_write": [
            {
                "path": "patchops/files/writers.py",
                "content_path": "content/patchops/files/writers.py",
                "encoding": "utf-8",
            },
            {
                "path": "tests/test_single_file_writer_current.py",
                "content_path": "content/tests/test_single_file_writer_current.py",
                "encoding": "utf-8",
            },
        ],
        "validation_commands": [
            {
                "name": "write-plan-and-single-file-writer-tests",
                "program": "py",
                "args": [
                    "-m",
                    "pytest",
                    "-q",
                    "tests/test_write_plan_current.py",
                    "tests/test_single_file_writer_current.py",
                ],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "report_preferences": {
            "report_dir": str(inner_report_dir),
            "report_name_prefix": "mp21",
            "write_to_desktop": False,
        },
        "tags": [
            "pythonization",
            "mp21",
            "self_hosted",
            "writers",
        ],
        "notes": "MP21 single-file writer helper. Keep PowerShell thin and move deterministic single-file writing into one Python helper.",
    }

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    audit["baseline_ok"] = True
    audit["manifest_path"] = str(manifest_path)
    audit["writer_target"] = str(writer_target)
    audit["test_target"] = str(test_target)
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    print(f"Prepared manifest: {manifest_path}")
    print(f"Prepared audit   : {audit_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())