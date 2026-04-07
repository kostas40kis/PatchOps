from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LauncherHeuristicFinding:
    code: str
    message: str


@dataclass(frozen=True)
class LauncherHeuristicReport:
    findings: tuple[LauncherHeuristicFinding, ...] = ()

    @property
    def ok(self) -> bool:
        return len(self.findings) == 0

    @property
    def warning_count(self) -> int:
        return len(self.findings)

    @property
    def codes(self) -> tuple[str, ...]:
        return tuple(item.code for item in self.findings)


def _contains(lowered: str, *needles: str) -> bool:
    return any(str(needle).lower() in lowered for needle in needles if needle)


def _add_unique(
    findings: list[LauncherHeuristicFinding],
    finding: LauncherHeuristicFinding,
) -> None:
    if any(item.code == finding.code for item in findings):
        return
    findings.append(finding)


def find_common_launcher_mistakes(text: str) -> tuple[LauncherHeuristicFinding, ...]:
    lowered = str(text or "").lower()
    findings: list[LauncherHeuristicFinding] = []

    if _contains(lowered, "get-content", "convertfrom-json") and "convertfrom-json" in lowered:
        _add_unique(
            findings,
            LauncherHeuristicFinding(
                code="fragile_json_handoff",
                message="Launcher appears to depend on Get-Content | ConvertFrom-Json handoff, which has repeatedly failed before real repo work started.",
            ),
        )

    if _contains(lowered, "py -c ", "python -c ", "py - <<", "python - <<"):
        _add_unique(
            findings,
            LauncherHeuristicFinding(
                code="large_inline_python_emission",
                message="Launcher appears to use inline Python authoring instead of staged deterministic content files.",
            ),
        )

    if _contains(lowered, "@'", '@"'):
        _add_unique(
            findings,
            LauncherHeuristicFinding(
                code="suspicious_here_string_usage",
                message="Launcher appears to use here-string content blocks, which are a high-risk source of quoting and indentation mistakes.",
            ),
        )

    if _contains(lowered, "copy-item", "move-item", "remove-item") and "py -m patchops.cli" not in lowered:
        _add_unique(
            findings,
            LauncherHeuristicFinding(
                code="manual_copy_logic_main_path",
                message="Launcher appears to use manual file-copy orchestration as a main path instead of delegating to PatchOps.",
            ),
        )

    if _contains(lowered, "py -m unittest", "python -m unittest"):
        _add_unique(
            findings,
            LauncherHeuristicFinding(
                code="direct_unittest_main_path",
                message="Launcher appears to use unittest directly as a main path instead of PatchOps CLI invocation.",
            ),
        )

    if "py -m patchops.cli" not in lowered:
        _add_unique(
            findings,
            LauncherHeuristicFinding(
                code="missing_standard_invocation_block",
                message="Launcher is missing the standard 'py -m patchops.cli ...' invocation block.",
            ),
        )

    if _contains(lowered, "$reportlines.add(", "add-sectionheader", "add-reportline", "add-line", "write-reportfile"):
        _add_unique(
            findings,
            LauncherHeuristicFinding(
                code="unsafe_report_buffer_patterns",
                message="Launcher appears to use fragile report-buffer helper patterns that have caused repeated failure-path bugs.",
            ),
        )

    if _contains(lowered, ".replace(", "-replace") and _contains(lowered, "get-content", "set-content", "writealltext"):
        _add_unique(
            findings,
            LauncherHeuristicFinding(
                code="brittle_exact_text_surgery",
                message="Launcher appears to perform brittle exact-text surgery instead of staging deterministic content.",
            ),
        )

    if (
        _contains(lowered, 'replace("\\", "/")', "unexpected character after line continuation character")
        or (
            _contains(lowered, "\\", '`"', '\"')
            and _contains(lowered, "py -c ", "python -c ", "@'", '@"', "writealltext", "set-content")
        )
    ):
        _add_unique(
            findings,
            LauncherHeuristicFinding(
                code="suspicious_nested_quoting_backslash_shape",
                message="Launcher appears to contain nested quoting or backslash-heavy authoring patterns that commonly break generated Python or PowerShell content.",
            ),
        )

    return tuple(findings)


def audit_bundle_launcher_text(text: str) -> LauncherHeuristicReport:
    return LauncherHeuristicReport(findings=find_common_launcher_mistakes(text))
