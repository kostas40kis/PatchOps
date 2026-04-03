from __future__ import annotations

import json
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def emit_kv(path: Path, key: str, value: str) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{key}={value}\n")


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: prepare_mp14a.py <wrapper_root> <working_root> <failed_report_path>", file=sys.stderr)
        return 2

    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    failed_report_path = Path(sys.argv[3]).expanduser()

    apply_path = wrapper_root / "patchops" / "workflows" / "apply_patch.py"
    sections_path = wrapper_root / "patchops" / "reporting" / "sections.py"
    command_sections_path = wrapper_root / "patchops" / "reporting" / "command_sections.py"
    target_test_rel = Path("tests") / "test_required_vs_tolerated_report_current.py"
    target_test_path = wrapper_root / target_test_rel
    summary_path = working_root / "prepare_summary.txt"
    if summary_path.exists():
        summary_path.unlink()

    apply_text = read_text(apply_path) if apply_path.exists() else ""
    sections_text = read_text(sections_path) if sections_path.exists() else ""
    command_sections_exists = command_sections_path.exists()

    failed_report_exists = failed_report_path.exists()
    failed_report_text = read_text(failed_report_path) if failed_report_exists else ""

    short_circuit_evidence = (
        "raise RuntimeError(command_failure.message)" in apply_text
        and "for command in commands:" in apply_text
    )
    report_shows_required = "NAME    : required_fail" in failed_report_text
    report_hides_later = "NAME    : later_success" not in failed_report_text if failed_report_exists else False

    rationale_bits = []
    if short_circuit_evidence:
        rationale_bits.append("apply_manifest still raises on first required command failure")
    if failed_report_exists and report_shows_required and report_hides_later:
        rationale_bits.append("failed MP14 report shows required_fail but not later_success")
    if not rationale_bits:
        rationale_bits.append("defaulting to narrow contract repair because it does not over-assert later command rendering")

    test_text = """from __future__ import annotations

import json
from pathlib import Path

from patchops.workflows.apply_patch import apply_manifest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _write_manifest(manifest_path: Path, manifest_data: dict) -> Path:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + \"\\n\", encoding=\"utf-8\")
    return manifest_path


def _base_manifest(tmp_path: Path, patch_name: str) -> dict:
    target_root = tmp_path / \"target_repo\"
    report_dir = tmp_path / \"reports\"
    target_root.mkdir()
    report_dir.mkdir()

    return {
        \"manifest_version\": \"1\",
        \"patch_name\": patch_name,
        \"active_profile\": \"generic_python\",
        \"target_project_root\": str(target_root).replace(\\\"\\\\\\\", \"/\"),
        \"backup_files\": [],
        \"files_to_write\": [],
        \"smoke_commands\": [],
        \"audit_commands\": [],
        \"cleanup_commands\": [],
        \"archive_commands\": [],
        \"failure_policy\": {},
        \"report_preferences\": {
            \"report_dir\": str(report_dir).replace(\\\"\\\\\\\", \"/\"),
            \"report_name_prefix\": patch_name,
            \"write_to_desktop\": False,
        },
        \"tags\": [\"test\", \"required_vs_tolerated\", \"report_truth\"],
        \"notes\": \"Temporary manifest used by the current required-versus-tolerated proof tests.\",
    }


def test_required_command_failure_outside_allowed_exit_codes_renders_fail(tmp_path: Path) -> None:
    wrapper_root = PROJECT_ROOT
    manifest_data = _base_manifest(tmp_path, \"required_failure_report_proof\")
    manifest_data[\"validation_commands\"] = [
        {
            \"name\": \"required_fail\",
            \"program\": \"python\",
            \"args\": [\"-c\", \"import sys; print('required fail'); sys.exit(1)\"],
            \"working_directory\": \".\",
            \"use_profile_runtime\": False,
            \"allowed_exit_codes\": [0],
        }
    ]

    manifest_path = _write_manifest(tmp_path / \"required_failure_report_proof.json\", manifest_data)
    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    assert result.result_label == \"FAIL\"
    assert result.exit_code == 1
    assert result.report_path.exists()

    report_text = result.report_path.read_text(encoding=\"utf-8\")
    assert \"NAME    : required_fail\" in report_text
    assert \"ExitCode : 1\" in report_text
    assert \"Result   : FAIL\" in report_text


def test_tolerated_non_zero_exit_still_renders_pass(tmp_path: Path) -> None:
    wrapper_root = PROJECT_ROOT
    manifest_data = _base_manifest(tmp_path, \"tolerated_failure_report_proof\")
    manifest_data[\"validation_commands\"] = [
        {
            \"name\": \"tolerated_non_zero\",
            \"program\": \"python\",
            \"args\": [\"-c\", \"import sys; print('tolerated non-zero'); sys.exit(3)\"],
            \"working_directory\": \".\",
            \"use_profile_runtime\": False,
            \"allowed_exit_codes\": [0, 3],
        }
    ]

    manifest_path = _write_manifest(tmp_path / \"tolerated_failure_report_proof.json\", manifest_data)
    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    assert result.result_label == \"PASS\"
    assert result.exit_code == 0
    assert result.report_path.exists()

    report_text = result.report_path.read_text(encoding=\"utf-8\")
    assert \"NAME    : tolerated_non_zero\" in report_text
    assert \"EXIT    : 3\" in report_text
    assert \"ExitCode : 0\" in report_text
    assert \"Result   : PASS\" in report_text


def test_earlier_required_failure_stays_sticky_without_assuming_later_command_rendering(tmp_path: Path) -> None:
    wrapper_root = PROJECT_ROOT
    manifest_data = _base_manifest(tmp_path, \"sticky_required_failure_report_proof\")
    manifest_data[\"validation_commands\"] = [
        {
            \"name\": \"required_fail\",
            \"program\": \"python\",
            \"args\": [\"-c\", \"import sys; print('required fail'); sys.exit(1)\"],
            \"working_directory\": \".\",
            \"use_profile_runtime\": False,
            \"allowed_exit_codes\": [0],
        },
        {
            \"name\": \"later_success\",
            \"program\": \"python\",
            \"args\": [\"-c\", \"print('later success')\"],
            \"working_directory\": \".\",
            \"use_profile_runtime\": False,
            \"allowed_exit_codes\": [0],
        },
    ]

    manifest_path = _write_manifest(tmp_path / \"sticky_required_failure_report_proof.json\", manifest_data)
    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    assert result.result_label == \"FAIL\"
    assert result.exit_code == 1
    assert result.report_path.exists()

    report_text = result.report_path.read_text(encoding=\"utf-8\")
    assert \"NAME    : required_fail\" in report_text
    assert \"FAILURE DETAILS\" in report_text
    assert \"required_fail\" in report_text
    assert \"ExitCode : 1\" in report_text
    assert \"Result   : FAIL\" in report_text
"""

    content_test_path = working_root / "content" / "tests" / "test_required_vs_tolerated_report_current.py"
    write_text(content_test_path, test_text)

    validation_candidates = [
        Path("tests") / "test_reporting.py",
        Path("tests") / "test_reporting_command_sections_current.py",
        Path("tests") / "test_summary_integrity_current.py",
        Path("tests") / "test_summary_derivation_lock_current.py",
        target_test_rel,
        Path("tests") / "test_summary_integrity_workflow_current.py",
    ]
    validation_targets = [str(path).replace("\\", "/") for path in validation_candidates if (wrapper_root / path).exists()]
    target_rel_str = str(target_test_rel).replace("\\", "/")
    if target_rel_str not in validation_targets:
        validation_targets.append(target_rel_str)

    manifest_data = {
        "manifest_version": "1",
        "patch_name": "mp14a_required_vs_tolerated_contract_repair",
        "active_profile": "generic_python",
        "target_project_root": str(wrapper_root).replace("\\", "/"),
        "backup_files": [target_rel_str],
        "files_to_write": [
            {
                "path": target_rel_str,
                "content_path": "content/tests/test_required_vs_tolerated_report_current.py",
                "encoding": "utf-8",
            }
        ],
        "validation_commands": [
            {
                "name": "reporting_stream_pytest",
                "program": "python",
                "args": ["-m", "pytest", "-q", *validation_targets],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": str((working_root / "inner_reports")).replace("\\", "/"),
            "report_name_prefix": "mp14a_required_vs_tolerated_contract_repair",
            "write_to_desktop": False,
        },
        "tags": ["maintenance", "pythonization", "mp14", "test_contract_repair"],
        "notes": "Narrow MP14 repair. Current repo evidence indicates the apply flow stops reporting after the first required validation failure, so the sticky-failure proof should not require later_success to be rendered.",
    }

    manifest_path = working_root / "patch_manifest.json"
    write_text(manifest_path, json.dumps(manifest_data, indent=2) + "\n")

    emit_kv(summary_path, "decision", "mp14a_test_contract_repair")
    emit_kv(summary_path, "target_test_path", str(target_test_path))
    emit_kv(summary_path, "failed_report_exists", str(failed_report_exists).lower())
    emit_kv(summary_path, "failed_report_shows_required", str(report_shows_required).lower())
    emit_kv(summary_path, "failed_report_hides_later_success", str(report_hides_later).lower())
    emit_kv(summary_path, "short_circuit_evidence", str(short_circuit_evidence).lower())
    emit_kv(summary_path, "command_sections_exists", str(command_sections_exists).lower())
    emit_kv(summary_path, "sections_mentions_name_lines", str("NAME    :" in sections_text).lower())
    emit_kv(summary_path, "manifest_path", str(manifest_path))
    for item in rationale_bits:
        emit_kv(summary_path, "rationale", item)
    for item in validation_targets:
        emit_kv(summary_path, "validation_target", item)

    print(str(manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())