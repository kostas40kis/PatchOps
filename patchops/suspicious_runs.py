from __future__ import annotations

from dataclasses import dataclass
from typing import Any


WRAPPER_FAILURE = "wrapper_failure"


@dataclass(frozen=True)
class SuspiciousRunFinding:
    code: str
    message: str
    failure_class: str = WRAPPER_FAILURE


_REQUIRED_REPORT_FIELDS = (
    "SUMMARY",
    "ExitCode",
    "Result",
)


def _summary_contradiction(summary_result: str | None, required_command_results: list[dict[str, Any]] | None) -> list[SuspiciousRunFinding]:
    findings: list[SuspiciousRunFinding] = []
    if summary_result != "PASS":
        return findings
    for item in required_command_results or []:
        if item.get("required") and item.get("exit_code") not in (0, None):
            findings.append(
                SuspiciousRunFinding(
                    code="required_command_summary_contradiction",
                    message="Required command evidence contradicts rendered summary.",
                )
            )
            break
    return findings


def _missing_critical_provenance(wrapper_executed: bool, provenance: dict[str, Any] | None) -> list[SuspiciousRunFinding]:
    if not wrapper_executed:
        return []
    provenance = provenance or {}
    required_keys = ("workflow_mode", "wrapper_project_root", "report_path")
    if any(not provenance.get(key) for key in required_keys):
        return [
            SuspiciousRunFinding(
                code="missing_critical_provenance",
                message="Critical provenance fields are missing after wrapper execution.",
            )
        ]
    return []


def _missing_latest_report_copy(
    latest_report_copy_expected: bool,
    latest_report_copy_exists: bool | None,
    workflow_mode: str | None,
) -> list[SuspiciousRunFinding]:
    if latest_report_copy_expected and latest_report_copy_exists is False and workflow_mode == "export_handoff":
        return [
            SuspiciousRunFinding(
                code="missing_latest_report_copy",
                message="Copied latest-report surface is missing after handoff export.",
            )
        ]
    return []


def _missing_required_report_fields(report_text: str) -> list[SuspiciousRunFinding]:
    if all(field in report_text for field in _REQUIRED_REPORT_FIELDS):
        return []
    return [
        SuspiciousRunFinding(
            code="missing_required_report_fields",
            message="Report structure is missing required core fields.",
        )
    ]


def detect_suspicious_run(
    *,
    report_text: str,
    summary_result: str | None,
    required_command_results: list[dict[str, Any]] | None = None,
    wrapper_executed: bool = False,
    provenance: dict[str, Any] | None = None,
    latest_report_copy_expected: bool = False,
    latest_report_copy_exists: bool | None = None,
    workflow_mode: str | None = None,
) -> list[SuspiciousRunFinding]:
    findings: list[SuspiciousRunFinding] = []
    findings.extend(_summary_contradiction(summary_result, required_command_results))
    findings.extend(_missing_critical_provenance(wrapper_executed, provenance))
    findings.extend(_missing_latest_report_copy(latest_report_copy_expected, latest_report_copy_exists, workflow_mode))
    findings.extend(_missing_required_report_fields(report_text))
    return findings
