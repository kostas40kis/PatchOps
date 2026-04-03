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
