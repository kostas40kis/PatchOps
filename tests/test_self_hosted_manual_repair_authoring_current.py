from __future__ import annotations

import json
import sys
from pathlib import Path

from patchops.cli import main


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _build_manifest(tmp_path: Path) -> tuple[Path, Path, Path]:
    patch_root = tmp_path / "self_hosted_manual_repair_patch"
    target_root = tmp_path / "target_repo"
    content_root = patch_root / "content"
    reports_root = patch_root / "reports"

    target_root.mkdir(parents=True, exist_ok=True)
    reports_root.mkdir(parents=True, exist_ok=True)

    expected_output = target_root / "docs" / "stream_note.txt"
    _write_text(content_root / "notes" / "stream_note.txt", "self-hosted authoring ok\n")

    validation_code = (
        "from pathlib import Path; import sys; "
        f"p = Path(r'{expected_output}'); "
        "sys.exit(0 if p.exists() and p.read_text(encoding='utf-8') == 'self-hosted authoring ok\\n' else 1)"
    )

    manifest = {
        "manifest_version": "1",
        "patch_name": "self_hosted_manual_repair_authoring_current",
        "active_profile": "generic_python",
        "target_project_root": str(target_root),
        "files_to_write": [
            {
                "path": "docs/stream_note.txt",
                "content_path": "content/notes/stream_note.txt",
                "encoding": "utf-8",
            }
        ],
        "validation_commands": [
            {
                "name": "written_file_matches_expected_content",
                "program": sys.executable,
                "args": ["-c", validation_code],
                "working_directory": str(target_root),
            }
        ],
        "report_preferences": {
            "report_dir": str(reports_root),
            "report_name_prefix": "self_hosted_manual_repair_authoring_current",
        },
    }

    manifest_path = patch_root / "patch_manifest.json"
    _write_text(manifest_path, json.dumps(manifest, indent=2))
    return manifest_path, expected_output, reports_root


def test_self_hosted_manual_repair_relative_content_path_survives_check_inspect_plan_and_apply(
    capsys,
    tmp_path: Path,
) -> None:
    manifest_path, expected_output, reports_root = _build_manifest(tmp_path)

    assert main(["check", str(manifest_path)]) == 0
    capsys.readouterr()

    assert main(["inspect", str(manifest_path)]) == 0
    capsys.readouterr()

    assert main(["plan", str(manifest_path)]) == 0
    capsys.readouterr()

    assert main(["apply", str(manifest_path)]) == 0
    capsys.readouterr()

    assert expected_output.read_text(encoding="utf-8") == "self-hosted authoring ok\n"
    assert list(reports_root.glob("*.txt"))