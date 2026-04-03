from __future__ import annotations

import json
import shutil
import sys
import textwrap
from pathlib import Path


RULE_MODULE = textwrap.dedent(
    """
    from __future__ import annotations

    from dataclasses import dataclass
    from pathlib import Path
    from typing import Any, Iterable, Mapping


    WRAPPER_FAILURE = "wrapper_failure"


    @dataclass(frozen=True)
    class SuspiciousRunFinding:
        code: str
        message: str
        failure_class: str = WRAPPER_FAILURE


    def _normalize_result(value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip().upper()
        return cleaned or None


    def _missing_required_report_fields(report_text: str) -> list[str]:
        required = ["SUMMARY", "ExitCode :", "Result   :"]
        return [field for field in required if field not in report_text]


    def detect_suspicious_run(
        *,
        report_text: str,
        summary_result: str | None = None,
        required_command_results: Iterable[Mapping[str, Any]] | None = None,
        wrapper_executed: bool = False,
        provenance: Mapping[str, Any] | None = None,
        latest_report_copy_expected: bool = False,
        latest_report_copy_exists: bool | None = None,
        workflow_mode: str | None = None,
    ) -> list[SuspiciousRunFinding]:
        findings: list[SuspiciousRunFinding] = []

        normalized_summary = _normalize_result(summary_result)
        for command in required_command_results or []:
            if not bool(command.get("required", True)):
                continue
            exit_code = command.get("exit_code")
            name = str(command.get("name", "required command"))
            if normalized_summary == "PASS" and exit_code not in (0, None):
                findings.append(
                    SuspiciousRunFinding(
                        code="required_command_summary_contradiction",
                        message=f"Rendered summary says PASS but required command '{name}' exited {exit_code}.",
                    )
                )
                break

        missing_fields = _missing_required_report_fields(report_text)
        if missing_fields:
            findings.append(
                SuspiciousRunFinding(
                    code="missing_required_report_fields",
                    message="Canonical report is missing required core fields: " + ", ".join(missing_fields) + ".",
                )
            )

        if wrapper_executed:
            provenance_map = dict(provenance or {})
            missing_provenance = [
                field
                for field in ("wrapper_project_root", "report_path", "workflow_mode")
                if not provenance_map.get(field)
            ]
            if missing_provenance:
                findings.append(
                    SuspiciousRunFinding(
                        code="missing_critical_provenance",
                        message="Wrapper execution completed but critical provenance fields are missing: "
                        + ", ".join(missing_provenance)
                        + ".",
                    )
                )

        if latest_report_copy_expected and latest_report_copy_exists is False:
            findings.append(
                SuspiciousRunFinding(
                    code="missing_latest_report_copy",
                    message=(
                        "A latest-report copy was expected for workflow "
                        f"{workflow_mode or 'unknown'} but no copied report surface was present."
                    ),
                )
            )

        return findings


    def read_report_text(report_path: str | Path) -> str:
        return Path(report_path).read_text(encoding="utf-8")
    """
).strip() + "\n"


CURRENT_TEST = textwrap.dedent(
    """
    from patchops.suspicious_runs import detect_suspicious_run


    def test_detect_suspicious_run_flags_required_command_summary_contradiction():
        findings = detect_suspicious_run(
            report_text="SUMMARY\\n-------\\nExitCode : 1\\nResult   : PASS\\n",
            summary_result="PASS",
            required_command_results=[
                {"name": "targeted validation", "required": True, "exit_code": 1},
            ],
        )
        assert [finding.code for finding in findings] == ["required_command_summary_contradiction"]


    def test_detect_suspicious_run_flags_missing_provenance_after_wrapper_execution():
        findings = detect_suspicious_run(
            report_text="SUMMARY\\n-------\\nExitCode : 0\\nResult   : FAIL\\n",
            summary_result="FAIL",
            wrapper_executed=True,
            provenance={"workflow_mode": "apply"},
        )
        assert [finding.code for finding in findings] == ["missing_critical_provenance"]


    def test_detect_suspicious_run_flags_missing_latest_report_copy_when_expected():
        findings = detect_suspicious_run(
            report_text="SUMMARY\\n-------\\nExitCode : 0\\nResult   : FAIL\\n",
            summary_result="FAIL",
            latest_report_copy_expected=True,
            latest_report_copy_exists=False,
            workflow_mode="export_handoff",
        )
        assert [finding.code for finding in findings] == ["missing_latest_report_copy"]


    def test_detect_suspicious_run_flags_missing_required_report_fields():
        findings = detect_suspicious_run(
            report_text="PATCHOPS REPORT WITHOUT SUMMARY\\n",
            summary_result="FAIL",
        )
        assert [finding.code for finding in findings] == ["missing_required_report_fields"]


    def test_detect_suspicious_run_returns_empty_list_for_conservative_normal_case():
        findings = detect_suspicious_run(
            report_text="SUMMARY\\n-------\\nExitCode : 0\\nResult   : PASS\\n",
            summary_result="PASS",
            required_command_results=[
                {"name": "full validation", "required": True, "exit_code": 0},
            ],
            wrapper_executed=True,
            provenance={
                "wrapper_project_root": "C:/dev/patchops",
                "report_path": "C:/Users/kostas/Desktop/example.txt",
                "workflow_mode": "apply",
            },
            latest_report_copy_expected=False,
            latest_report_copy_exists=None,
            workflow_mode="apply",
        )
        assert findings == []
    """
).strip() + "\n"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def backup_file(src: Path, backup_root: Path, repo_root: Path) -> None:
    if not src.exists():
        return
    relative = src.relative_to(repo_root)
    dest = backup_root / relative
    ensure_parent(dest)
    shutil.copy2(src, dest)


def write_file(path: Path, content: str) -> None:
    ensure_parent(path)
    path.write_text(content, encoding="utf-8")


def print_kv(key: str, value: object) -> None:
    print(f"{key}={value}")


def main() -> int:
    repo_root = Path(sys.argv[1]).resolve()
    backup_root = Path(sys.argv[2]).resolve()
    backup_root.mkdir(parents=True, exist_ok=True)

    rule_path = repo_root / "patchops" / "suspicious_runs.py"
    test_path = repo_root / "tests" / "test_suspicious_run_rule_set_current.py"

    backup_file(rule_path, backup_root, repo_root)
    backup_file(test_path, backup_root, repo_root)

    write_file(rule_path, RULE_MODULE)
    write_file(test_path, CURRENT_TEST)

    print(json.dumps(
        {
            "patched_files": [
                str(rule_path.relative_to(repo_root)),
                str(test_path.relative_to(repo_root)),
            ],
            "backup_root": str(backup_root),
        },
        indent=2,
    ))
    print_kv("rule_path", str(rule_path))
    print_kv("test_path", str(test_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())