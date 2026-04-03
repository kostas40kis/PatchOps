from __future__ import annotations

import json
import sys
from pathlib import Path

PATCH_NAME = "mp14_required_vs_tolerated_report_proof"


def write_utf8(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def as_repo_relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: prepare_mp14.py <repo_root> <work_root>")

    repo_root = Path(sys.argv[1]).resolve()
    work_root = Path(sys.argv[2]).resolve()
    content_root = work_root / "content"
    inner_reports = work_root / "inner_reports"
    inner_reports.mkdir(parents=True, exist_ok=True)

    tests_path = content_root / "tests" / "test_required_vs_tolerated_report_current.py"

    test_code = """from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\\n", encoding="utf-8")


def _report_path_from_text(text: str) -> Path:
    match = re.search(r"(?m)^Report Path\\s*:\\s*(.+?)\\s*$", text)
    assert match is not None, text
    report_path = Path(match.group(1).strip())
    assert report_path.exists(), report_path
    return report_path


def _run_apply(manifest_path: Path) -> tuple[subprocess.CompletedProcess[str], str]:
    result = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "apply", str(manifest_path)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    report_path = _report_path_from_text(result.stdout + "\\n" + result.stderr)
    return result, report_path.read_text(encoding="utf-8")


def _command(name: str, exit_code: int, allowed_exit_codes: list[int] | None = None) -> dict:
    command = {
        "name": name,
        "program": sys.executable,
        "args": [
            "-c",
            f"import sys; print({name!r}); sys.stderr.write({name!r} + '-stderr\\\\n'); sys.exit({exit_code})",
        ],
        "working_directory": ".",
    }
    if allowed_exit_codes is not None:
        command["allowed_exit_codes"] = allowed_exit_codes
    return command


def _manifest(tmp_path: Path, patch_name: str, commands: list[dict]) -> Path:
    target_root = tmp_path / "target"
    report_dir = tmp_path / "reports"
    target_root.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "manifest_version": "1",
        "patch_name": patch_name,
        "active_profile": "generic_python",
        "target_project_root": str(target_root).replace('\\\\', '/'),
        "backup_files": [],
        "files_to_write": [],
        "validation_commands": commands,
        "report_preferences": {
            "report_dir": str(report_dir).replace('\\\\', '/'),
            "report_name_prefix": patch_name,
            "write_to_desktop": False,
        },
        "tags": ["test", "mp14", "required_vs_tolerated"],
        "notes": "MP14 proof manifest generated from test_required_vs_tolerated_report_current.py",
    }
    manifest_path = tmp_path / f"{patch_name}.json"
    _write_json(manifest_path, manifest)
    return manifest_path


def test_required_failure_renders_fail(tmp_path: Path) -> None:
    manifest_path = _manifest(
        tmp_path,
        "required_failure_renders_fail",
        [_command("required_fail", 1)],
    )

    result, report_text = _run_apply(manifest_path)

    assert result.returncode != 0
    assert "Result             : FAIL" in result.stdout
    assert "NAME    : required_fail" in report_text
    assert "EXIT    : 1" in report_text
    assert "Result   : FAIL" in report_text


def test_tolerated_non_zero_can_still_render_pass(tmp_path: Path) -> None:
    manifest_path = _manifest(
        tmp_path,
        "tolerated_non_zero_passes",
        [_command("tolerated_non_zero", 1, allowed_exit_codes=[0, 1])],
    )

    result, report_text = _run_apply(manifest_path)

    assert result.returncode == 0
    assert "Result             : PASS" in result.stdout
    assert "NAME    : tolerated_non_zero" in report_text
    assert "EXIT    : 1" in report_text
    assert "Result   : PASS" in report_text


def test_later_success_does_not_erase_earlier_required_failure(tmp_path: Path) -> None:
    manifest_path = _manifest(
        tmp_path,
        "later_success_does_not_erase_required_failure",
        [
            _command("required_fail", 1),
            _command("later_success", 0),
        ],
    )

    result, report_text = _run_apply(manifest_path)

    assert result.returncode != 0
    assert "Result             : FAIL" in result.stdout
    assert "NAME    : required_fail" in report_text
    assert "NAME    : later_success" in report_text
    assert report_text.count("EXIT    : 1") >= 1
    assert report_text.count("EXIT    : 0") >= 1
    assert "Result   : FAIL" in report_text
"""

    write_utf8(tests_path, test_code)

    manifest = {
        "manifest_version": "1",
        "patch_name": PATCH_NAME,
        "active_profile": "generic_python",
        "target_project_root": str(repo_root).replace("\\", "/"),
        "backup_files": [
            "tests/test_required_vs_tolerated_report_current.py",
        ],
        "files_to_write": [
            {
                "path": "tests/test_required_vs_tolerated_report_current.py",
                "content_path": as_repo_relative(tests_path, work_root),
                "encoding": "utf-8",
            }
        ],
        "validation_commands": [
            {
                "name": "required_vs_tolerated_report_contracts",
                "program": "py",
                "args": [
                    "-m",
                    "pytest",
                    "-q",
                    "tests/test_reporting.py",
                    "tests/test_reporting_command_sections_current.py",
                    "tests/test_summary_integrity_current.py",
                    "tests/test_summary_derivation_lock_current.py",
                    "tests/test_required_vs_tolerated_report_current.py",
                    "tests/test_summary_integrity_workflow_current.py",
                ],
                "working_directory": ".",
            }
        ],
        "report_preferences": {
            "report_dir": str(inner_reports.resolve()).replace("\\", "/"),
            "report_name_prefix": "mp14",
            "write_to_desktop": True,
        },
        "tags": [
            "self_hosted",
            "pythonization",
            "mp14",
            "required_vs_tolerated_report_proof",
            "reporting",
        ],
        "notes": "MP14: add narrow report-truth proofs for required versus tolerated command exits.",
    }

    manifest_path = work_root / "patch_manifest.json"
    write_utf8(manifest_path, json.dumps(manifest, indent=2) + "\n")

    print(f"INFO: staged_tests={tests_path}")
    print(str(manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())