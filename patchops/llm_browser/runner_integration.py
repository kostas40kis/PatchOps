"""Browser runner integration skeleton for the optional LLM browser runner.

This module introduces the first integration boundary that can compose the
already-passive layers into a single one-shot runner shape. It is intentionally
adapter-driven and side-effect guarded.

Default behavior is dry-run/skeleton only:
- imports no Selenium modules,
- starts no browser driver by itself,
- does not click/download by itself,
- does not run PatchOps by itself,
- does not paste/send by itself,
- tests inject fake adapters only.

A future patch can provide real adapters behind explicit operator flags.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Mapping

from .chat_page_contract import ChatPageSnapshot
from .dry_run_orchestrator import DryRunOrchestrationResult, dry_run_orchestrate_once
from .orchestration_state import OrchestrationState
from .pasteback_summary import PastebackSummary
from .patchops_runner import PatchOpsRunResult
from .report_locator import CanonicalReportLocation


SnapshotProvider = Callable[[], ChatPageSnapshot]
DownloadProvider = Callable[[str], str | Path | None]
PatchOpsProvider = Callable[[str | Path], PatchOpsRunResult | None]
ReportProvider = Callable[[PatchOpsRunResult | None], CanonicalReportLocation | None]
PasteProvider = Callable[[PastebackSummary], object]


@dataclass(frozen=True)
class BrowserRunnerSafetyPolicy:
    allow_download_click: bool = False
    allow_patchops_run: bool = False
    allow_paste: bool = False
    allow_send: bool = False

    @property
    def side_effects_enabled(self) -> bool:
        return self.allow_download_click or self.allow_patchops_run or self.allow_paste or self.allow_send

    def to_payload(self) -> dict[str, object]:
        return {
            "allow_download_click": self.allow_download_click,
            "allow_patchops_run": self.allow_patchops_run,
            "allow_paste": self.allow_paste,
            "allow_send": self.allow_send,
            "side_effects_enabled": self.side_effects_enabled,
        }


@dataclass(frozen=True)
class BrowserRunnerIntegrationOptions:
    browser: str = "edge"
    processed_artifacts: tuple[str, ...] = ()
    dry_run_only: bool = True
    max_failures: int = 3
    safety: BrowserRunnerSafetyPolicy = field(default_factory=BrowserRunnerSafetyPolicy)

    def to_payload(self) -> dict[str, object]:
        return {
            "browser": self.browser,
            "processed_artifacts": list(self.processed_artifacts),
            "dry_run_only": self.dry_run_only,
            "max_failures": self.max_failures,
            "safety": self.safety.to_payload(),
        }


@dataclass(frozen=True)
class BrowserRunnerAdapters:
    snapshot_provider: SnapshotProvider
    download_provider: DownloadProvider | None = None
    patchops_provider: PatchOpsProvider | None = None
    report_provider: ReportProvider | None = None
    paste_provider: PasteProvider | None = None

    def available(self) -> dict[str, bool]:
        return {
            "snapshot_provider": self.snapshot_provider is not None,
            "download_provider": self.download_provider is not None,
            "patchops_provider": self.patchops_provider is not None,
            "report_provider": self.report_provider is not None,
            "paste_provider": self.paste_provider is not None,
        }


@dataclass(frozen=True)
class BrowserRunnerIntegrationResult:
    dry_run: DryRunOrchestrationResult
    options: BrowserRunnerIntegrationOptions
    adapter_availability: dict[str, bool]
    side_effects_performed: tuple[str, ...]
    blocked_reason: str | None

    @property
    def ok(self) -> bool:
        return self.dry_run.ok and not self.blocked_reason

    @property
    def blocked(self) -> bool:
        return bool(self.blocked_reason) or self.dry_run.blocked

    def to_payload(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "blocked": self.blocked,
            "blocked_reason": self.blocked_reason,
            "options": self.options.to_payload(),
            "adapter_availability": dict(self.adapter_availability),
            "side_effects_performed": list(self.side_effects_performed),
            "dry_run": self.dry_run.to_payload(),
        }


def validate_safety_policy(options: BrowserRunnerIntegrationOptions) -> str | None:
    if options.safety.allow_send:
        return "auto_send_is_not_supported"
    if options.dry_run_only and options.safety.side_effects_enabled:
        return "dry_run_only_disallows_side_effects"
    if options.max_failures <= 0:
        return "max_failures_must_be_positive"
    if options.browser not in {"edge", "opera"}:
        return "unsupported_browser"
    return None


def planned_actions_for_options(options: BrowserRunnerIntegrationOptions) -> tuple[str, ...]:
    actions = ["capture_page_snapshot", "run_passive_orchestration_decision"]
    if options.safety.allow_download_click:
        actions.append("download_click_adapter_enabled")
    else:
        actions.append("download_click_adapter_disabled")
    if options.safety.allow_patchops_run:
        actions.append("patchops_run_adapter_enabled")
    else:
        actions.append("patchops_run_adapter_disabled")
    if options.safety.allow_paste:
        actions.append("paste_adapter_enabled_without_send")
    else:
        actions.append("paste_adapter_disabled")
    actions.append("auto_send_adapter_absent")
    return tuple(actions)


def run_browser_runner_integration_once(
    adapters: BrowserRunnerAdapters,
    *,
    options: BrowserRunnerIntegrationOptions | None = None,
) -> BrowserRunnerIntegrationResult:
    opts = options or BrowserRunnerIntegrationOptions()
    availability = adapters.available()
    safety_error = validate_safety_policy(opts)

    snapshot = adapters.snapshot_provider()

    if safety_error is not None:
        dry_run = dry_run_orchestrate_once(
            snapshot,
            browser=opts.browser,
            processed_artifacts=opts.processed_artifacts,
            max_failures=opts.max_failures if opts.max_failures > 0 else 1,
        )
        return BrowserRunnerIntegrationResult(
            dry_run=dry_run,
            options=opts,
            adapter_availability=availability,
            side_effects_performed=(),
            blocked_reason=safety_error,
        )

    # Skeleton mode: compute the first dry-run decision without executing real
    # side-effect adapters. Later patches can explicitly route through the
    # adapters under operator-controlled flags.
    first_pass = dry_run_orchestrate_once(
        snapshot,
        browser=opts.browser,
        processed_artifacts=opts.processed_artifacts,
        max_failures=opts.max_failures,
    )

    downloaded_path: str | Path | None = None
    runner_result: PatchOpsRunResult | None = None
    report_location: CanonicalReportLocation | None = None
    side_effects: list[str] = []

    # In dry_run_only mode, never call side-effect providers. The returned
    # planned actions show what would have happened.
    if not opts.dry_run_only:
        # Side-effect adapters remain opt-in and still cannot send. D0.22 keeps
        # this path conservative: it calls only adapters explicitly enabled by
        # policy and records that they were called.
        candidate = None
        if first_pass.artifact_detection is not None and first_pass.artifact_detection.candidate is not None:
            candidate = first_pass.artifact_detection.candidate

        if opts.safety.allow_download_click and adapters.download_provider is not None and candidate is not None:
            downloaded_path = adapters.download_provider(candidate.filename)
            side_effects.append("download_provider_called")

        if opts.safety.allow_patchops_run and adapters.patchops_provider is not None and downloaded_path is not None:
            runner_result = adapters.patchops_provider(downloaded_path)
            side_effects.append("patchops_provider_called")

        if adapters.report_provider is not None and runner_result is not None:
            report_location = adapters.report_provider(runner_result)
            side_effects.append("report_provider_called")

    dry_run = dry_run_orchestrate_once(
        snapshot,
        browser=opts.browser,
        processed_artifacts=opts.processed_artifacts,
        downloaded_path=downloaded_path,
        runner_result=runner_result,
        report_location=report_location,
        max_failures=opts.max_failures,
    )

    if (
        not opts.dry_run_only
        and opts.safety.allow_paste
        and adapters.paste_provider is not None
        and dry_run.snapshot.state == OrchestrationState.SUMMARY_READY
    ):
        adapters.paste_provider(dry_run.pasteback_summary)
        side_effects.append("paste_provider_called_without_send")

    return BrowserRunnerIntegrationResult(
        dry_run=dry_run,
        options=opts,
        adapter_availability=availability,
        side_effects_performed=tuple(side_effects),
        blocked_reason=None,
    )
