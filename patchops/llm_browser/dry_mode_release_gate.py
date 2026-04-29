"""Dry-mode release gate for the optional LLM browser runner.

The gate validates the passive/dry-mode contract without performing live
automation.

It does not:
- start a browser;
- import or start Selenium;
- click/download anything;
- run PatchOps;
- paste into a composer;
- submit/send a message;
- start localhost services.

The gate is intended to provide one compact PASS/FAIL decision before moving
from dry-mode scaffolding toward any future operator-controlled live adapter.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib
from pathlib import Path
from typing import Callable, Iterable, Sequence


EXPECTED_PASSIVE_MODULES: tuple[str, ...] = (
    "patchops.llm_browser.audit_log",
    "patchops.llm_browser.artifact_detector",
    "patchops.llm_browser.chat_page_contract",
    "patchops.llm_browser.composer_paste",
    "patchops.llm_browser.dry_run_orchestrator",
    "patchops.llm_browser.orchestration_state",
    "patchops.llm_browser.pasteback_summary",
    "patchops.llm_browser.patchops_runner",
    "patchops.llm_browser.processed_store",
    "patchops.llm_browser.report_locator",
    "patchops.llm_browser.run_lock",
    "patchops.llm_browser.runner_integration",
)

EXPECTED_DOCS: tuple[str, ...] = (
    "docs/llm_browser_runner.md",
    "docs/llm_browser_audit_log_operator_examples.md",
)

EXPECTED_CLI_SURFACES: tuple[str, ...] = (
    "doctor",
    "open",
    "dry-run",
    "run-once",
    "audit-log",
    "release-gate",
)


@dataclass(frozen=True)
class ReleaseGateCheck:
    name: str
    ok: bool
    details: str

    @property
    def status(self) -> str:
        return "PASS" if self.ok else "FAIL"

    def to_payload(self) -> dict[str, object]:
        return {
            "name": self.name,
            "status": self.status,
            "ok": self.ok,
            "details": self.details,
        }


@dataclass(frozen=True)
class ReleaseGateReport:
    name: str
    ok: bool
    checks: tuple[ReleaseGateCheck, ...]

    @property
    def status(self) -> str:
        return "PASS" if self.ok else "FAIL"

    @property
    def exit_code(self) -> int:
        return 0 if self.ok else 1

    def to_payload(self) -> dict[str, object]:
        return {
            "name": self.name,
            "status": self.status,
            "ok": self.ok,
            "exit_code": self.exit_code,
            "checks": [check.to_payload() for check in self.checks],
        }


def _check_imports(module_names: Sequence[str]) -> ReleaseGateCheck:
    failures: list[str] = []
    for name in module_names:
        try:
            importlib.import_module(name)
        except Exception as exc:  # pragma: no cover - failure detail path
            failures.append(f"{name}: {exc!r}")

    if failures:
        return ReleaseGateCheck(
            name="passive_modules_import",
            ok=False,
            details="; ".join(failures),
        )

    return ReleaseGateCheck(
        name="passive_modules_import",
        ok=True,
        details=f"Imported {len(module_names)} passive llm-browser modules.",
    )


def _check_safety_policy() -> ReleaseGateCheck:
    from .runner_integration import (
        BrowserRunnerIntegrationOptions,
        BrowserRunnerSafetyPolicy,
        validate_safety_policy,
    )

    auto_send = validate_safety_policy(
        BrowserRunnerIntegrationOptions(
            safety=BrowserRunnerSafetyPolicy(allow_send=True),
        )
    )
    dry_side_effects = validate_safety_policy(
        BrowserRunnerIntegrationOptions(
            dry_run_only=True,
            safety=BrowserRunnerSafetyPolicy(allow_download_click=True),
        )
    )

    if auto_send != "auto_send_is_not_supported":
        return ReleaseGateCheck(
            name="safety_policy_rejects_auto_send",
            ok=False,
            details=f"Unexpected auto-send validation result: {auto_send!r}",
        )

    if dry_side_effects != "dry_run_only_disallows_side_effects":
        return ReleaseGateCheck(
            name="safety_policy_rejects_dry_mode_side_effects",
            ok=False,
            details=f"Unexpected dry-mode side-effect validation result: {dry_side_effects!r}",
        )

    return ReleaseGateCheck(
        name="safety_policy_rejects_auto_send_and_dry_side_effects",
        ok=True,
        details="Auto-send and dry-run side effects are rejected.",
    )


def _check_audit_metadata_contract() -> ReleaseGateCheck:
    from .audit_log import sanitize_metadata

    metadata = sanitize_metadata(
        {
            "planned_actions": ["would_acquire_run_lock", "scan_latest_assistant_reply_for_patchops_bundle"],
            "side_effects_performed": [],
            "nested": {"ok": True},
        }
    )

    if metadata.get("planned_actions") != [
        "would_acquire_run_lock",
        "scan_latest_assistant_reply_for_patchops_bundle",
    ]:
        return ReleaseGateCheck(
            name="audit_metadata_json_arrays",
            ok=False,
            details=f"planned_actions was not preserved as JSON array: {metadata.get('planned_actions')!r}",
        )

    if metadata.get("side_effects_performed") != []:
        return ReleaseGateCheck(
            name="audit_metadata_empty_side_effects_array",
            ok=False,
            details=f"side_effects_performed was not preserved as empty array: {metadata.get('side_effects_performed')!r}",
        )

    return ReleaseGateCheck(
        name="audit_metadata_json_arrays",
        ok=True,
        details="planned_actions and side_effects_performed remain JSON arrays.",
    )


def _check_dry_run_blocks_without_side_effects() -> ReleaseGateCheck:
    from .chat_page_contract import snapshot_from_html
    from .dry_run_orchestrator import dry_run_orchestrate_once

    snapshot = snapshot_from_html(
        '<article data-message-author-role="assistant">no zip here</article><textarea></textarea>'
    )
    result = dry_run_orchestrate_once(snapshot, browser="edge")

    if not result.blocked:
        return ReleaseGateCheck(
            name="dry_run_blocks_without_artifact",
            ok=False,
            details="Expected dry-run to block when no PatchOps artifact exists.",
        )

    if result.side_effects_performed != ():
        return ReleaseGateCheck(
            name="dry_run_has_no_side_effects",
            ok=False,
            details=f"Unexpected dry-run side effects: {result.side_effects_performed!r}",
        )

    if result.snapshot.state.value != "BLOCKED_ARTIFACT_MISSING":
        return ReleaseGateCheck(
            name="dry_run_expected_block_state",
            ok=False,
            details=f"Unexpected dry-run state: {result.snapshot.state.value!r}",
        )

    return ReleaseGateCheck(
        name="dry_run_blocks_without_side_effects",
        ok=True,
        details="Missing-artifact dry-run reaches BLOCKED_ARTIFACT_MISSING with no side effects.",
    )


def _check_docs(repo_root: Path) -> ReleaseGateCheck:
    missing: list[str] = []
    text_by_path: dict[str, str] = {}

    for relative in EXPECTED_DOCS:
        path = repo_root / relative
        if not path.exists():
            missing.append(relative)
            continue
        text_by_path[relative] = path.read_text(encoding="utf-8")

    if missing:
        return ReleaseGateCheck(
            name="dry_mode_docs_exist",
            ok=False,
            details="Missing docs: " + ", ".join(missing),
        )

    runner_doc = text_by_path["docs/llm_browser_runner.md"]
    examples_doc = text_by_path["docs/llm_browser_audit_log_operator_examples.md"]
    required_phrases = [
        "D0.27 audit-log docs and operator examples",
        "D0.26 audit-log readback CLI",
        "llm-browser dry-run --audit-log",
        "llm-browser run-once --dry-run --audit-log",
        "llm-browser audit-log --path --limit --json",
        "The audit-log surfaces are passive.",
        "There is still no `--auto-send` or `--allow-send` option.",
    ]
    combined = runner_doc + "\n" + examples_doc
    missing_phrases = [phrase for phrase in required_phrases if phrase not in combined]
    if missing_phrases:
        return ReleaseGateCheck(
            name="dry_mode_docs_contract",
            ok=False,
            details="Missing doc phrases: " + ", ".join(missing_phrases),
        )

    return ReleaseGateCheck(
        name="dry_mode_docs_contract",
        ok=True,
        details="Dry-mode runner and audit-log operator docs contain required contract phrases.",
    )


def _check_cli_surface_names(surface_names: Iterable[str]) -> ReleaseGateCheck:
    names = tuple(surface_names)
    missing = [name for name in EXPECTED_CLI_SURFACES if name not in names]
    if missing:
        return ReleaseGateCheck(
            name="cli_surface_contract",
            ok=False,
            details="Missing CLI surfaces: " + ", ".join(missing),
        )

    return ReleaseGateCheck(
        name="cli_surface_contract",
        ok=True,
        details="Expected llm-browser CLI surfaces are registered: " + ", ".join(EXPECTED_CLI_SURFACES),
    )


def evaluate_dry_mode_release_gate(
    *,
    repo_root: str | Path | None = None,
    cli_surface_names: Iterable[str] = EXPECTED_CLI_SURFACES,
    module_names: Sequence[str] = EXPECTED_PASSIVE_MODULES,
) -> ReleaseGateReport:
    root = Path.cwd() if repo_root is None else Path(repo_root)

    checks = (
        _check_imports(module_names),
        _check_safety_policy(),
        _check_audit_metadata_contract(),
        _check_dry_run_blocks_without_side_effects(),
        _check_docs(root),
        _check_cli_surface_names(cli_surface_names),
    )
    return ReleaseGateReport(
        name="llm_browser_dry_mode_release_gate",
        ok=all(check.ok for check in checks),
        checks=checks,
    )


def render_release_gate_report(report: ReleaseGateReport) -> str:
    lines: list[str] = []
    lines.append(f"Release gate: {report.name}")
    lines.append(f"Status      : {report.status}")
    lines.append(f"ExitCode    : {report.exit_code}")
    lines.append("")
    lines.append("Checks:")
    for check in report.checks:
        lines.append(f"- {check.status} {check.name}: {check.details}")
    lines.append("")
    return "\n".join(lines)
