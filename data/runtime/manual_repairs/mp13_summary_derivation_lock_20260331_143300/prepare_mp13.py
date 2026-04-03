from __future__ import annotations

import json
import sys
from pathlib import Path

PATCH_NAME = "mp13_summary_derivation_lock"


def write_utf8(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def as_repo_relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: prepare_mp13.py <repo_root> <work_root>")

    repo_root = Path(sys.argv[1]).resolve()
    work_root = Path(sys.argv[2]).resolve()
    content_root = work_root / "content"
    inner_reports = work_root / "inner_reports"
    inner_reports.mkdir(parents=True, exist_ok=True)

    reporting_test = repo_root / "tests" / "test_reporting.py"
    summary_test = repo_root / "tests" / "test_summary_integrity_current.py"
    workflow_test = repo_root / "tests" / "test_summary_integrity_workflow_current.py"
    if not reporting_test.exists():
        raise RuntimeError(f"Required repo file missing: {reporting_test}")
    if not summary_test.exists():
        raise RuntimeError(f"Required repo file missing: {summary_test}")

    new_test_path = content_root / "tests" / "test_summary_derivation_lock_current.py"
    new_test_text = '''from pathlib import Path

from patchops.reporting.renderer import render_workflow_report
from tests.test_summary_integrity_current import _build_result, _command_result, _command_spec


def test_summary_lock_rejects_required_smoke_failure_even_when_result_label_claims_pass(tmp_path: Path) -> None:
    result = _build_result(
        tmp_path,
        smoke_specs=[_command_spec("required_smoke", [0])],
        smoke_results=[_command_result("required_smoke", 7, "smoke")],
        exit_code=0,
        result_label="PASS",
    )

    report = render_workflow_report(result)

    assert "SMOKE COMMANDS" in report
    assert "NAME    : required_smoke" in report
    assert "EXIT    : 7" in report
    assert "ExitCode : 7" in report
    assert "Result   : FAIL" in report


def test_summary_lock_keeps_required_failure_sticky_even_when_later_non_zero_is_tolerated(tmp_path: Path) -> None:
    result = _build_result(
        tmp_path,
        validation_specs=[_command_spec("required_validation", [0])],
        validation_results=[_command_result("required_validation", 4, "validation")],
        smoke_specs=[_command_spec("tolerated_smoke", [0, 3])],
        smoke_results=[_command_result("tolerated_smoke", 3, "smoke")],
        exit_code=0,
        result_label="PASS",
    )

    report = render_workflow_report(result)

    assert "NAME    : required_validation" in report
    assert "NAME    : tolerated_smoke" in report
    assert "EXIT    : 4" in report
    assert "EXIT    : 3" in report
    assert "ExitCode : 4" in report
    assert "Result   : FAIL" in report


def test_summary_lock_preserves_pass_when_only_explicitly_tolerated_non_zero_exists(tmp_path: Path) -> None:
    result = _build_result(
        tmp_path,
        smoke_specs=[_command_spec("tolerated_smoke", [0, 5])],
        smoke_results=[_command_result("tolerated_smoke", 5, "smoke")],
        exit_code=0,
        result_label="PASS",
    )

    report = render_workflow_report(result)

    assert "NAME    : tolerated_smoke" in report
    assert "EXIT    : 5" in report
    assert "ExitCode : 0" in report
    assert "Result   : PASS" in report
'''
    write_utf8(new_test_path, new_test_text)

    selected_tests = [
        "tests/test_reporting.py",
        "tests/test_reporting_command_sections_current.py",
        "tests/test_summary_integrity_current.py",
        "tests/test_summary_derivation_lock_current.py",
    ]
    if workflow_test.exists():
        selected_tests.append("tests/test_summary_integrity_workflow_current.py")

    manifest = {
        "manifest_version": "1",
        "patch_name": PATCH_NAME,
        "active_profile": "generic_python",
        "target_project_root": str(repo_root).replace("\\", "/"),
        "backup_files": [
            "tests/test_summary_derivation_lock_current.py",
        ],
        "files_to_write": [
            {
                "path": "tests/test_summary_derivation_lock_current.py",
                "content_path": as_repo_relative(new_test_path, work_root),
                "encoding": "utf-8",
            }
        ],
        "validation_commands": [
            {
                "name": "summary_derivation_lock_contracts",
                "program": "py",
                "args": ["-m", "pytest", "-q", *selected_tests],
                "working_directory": ".",
            }
        ],
        "report_preferences": {
            "report_name_prefix": "mp13",
            "report_dir": str(inner_reports.resolve()).replace("\\", "/"),
        },
        "tags": [
            "self_hosted",
            "pythonization",
            "mp13",
            "summary_derivation_lock",
            "reporting",
        ],
        "notes": "MP13: tighten summary derivation tests around rendered ExitCode and Result without changing report cosmetics.",
    }

    manifest_path = work_root / "patch_manifest.json"
    write_utf8(manifest_path, json.dumps(manifest, indent=2) + "\n")

    print(f"INFO: staged_tests={new_test_path}")
    print(f"INFO: selected_tests={selected_tests}")
    print(str(manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())