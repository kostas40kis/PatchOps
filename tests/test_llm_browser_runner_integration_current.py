from __future__ import annotations

from pathlib import Path

from patchops.llm_browser.chat_page_contract import snapshot_from_html
from patchops.llm_browser.orchestration_state import OrchestrationState
from patchops.llm_browser.patchops_runner import PatchOpsRunCommand, PatchOpsRunResult
from patchops.llm_browser.report_locator import CanonicalReportLocation, CanonicalReportSummary
from patchops.llm_browser.runner_integration import (
    BrowserRunnerAdapters,
    BrowserRunnerIntegrationOptions,
    BrowserRunnerSafetyPolicy,
    planned_actions_for_options,
    run_browser_runner_integration_once,
    validate_safety_policy,
)


def _html_with_bundle(filename: str = "patch_d0_22_browser_runner_integration_skeleton_patchops_bundle.zip") -> str:
    return f"""
    <article data-message-author-role="assistant">
      <a href="/downloads/{filename}?download=1">{filename}</a>
    </article>
    <textarea id="prompt-textarea"></textarea>
    """


def _snapshot_provider():
    return snapshot_from_html(_html_with_bundle())


def _runner_result(tmp_path: Path, *, ok: bool = True) -> PatchOpsRunResult:
    artifact = tmp_path / "patch_d0_22_browser_runner_integration_skeleton_patchops_bundle.zip"
    artifact.write_bytes(b"zip")
    command = PatchOpsRunCommand(
        command=("python", "-m", "patchops.cli", "run-package", str(artifact), "--wrapper-root", str(tmp_path)),
        cwd=tmp_path,
        timeout_seconds=1800,
        artifact_path=artifact,
        wrapper_root=tmp_path,
    )
    return PatchOpsRunResult(
        command=command,
        exit_code=0 if ok else 1,
        stdout='{"ok": true}' if ok else '{"ok": false}',
        stderr="",
        timed_out=False,
        ok=ok,
        reason="success" if ok else "patchops_payload_ok_false",
        report_path=str(tmp_path / "patchops_run_package_20260429_193300.txt"),
        failure_category=None if ok else "target_content_failure",
        parsed_payload={"ok": ok},
    )


def _report_location(tmp_path: Path, *, passed: bool = True) -> CanonicalReportLocation:
    report = tmp_path / "patchops_run_package_20260429_193300.txt"
    report.write_text("Result : PASS\nExitCode : 0\nPatch : D0.22\n" if passed else "Result : FAIL\nExitCode : 1\nPatch : D0.22\n", encoding="utf-8")
    return CanonicalReportLocation(
        found=True,
        path=report,
        reason="explicit_report_path_found",
        source="test",
        summary=CanonicalReportSummary(
            path=report,
            result="PASS" if passed else "FAIL",
            exit_code=0 if passed else 1,
            patch="D0.22 browser runner integration skeleton",
            failure_category=None if passed else "target_content_failure",
            text_length=len(report.read_text(encoding="utf-8")),
        ),
        candidates_seen=(report,),
    )


def test_default_safety_policy_disables_side_effects() -> None:
    policy = BrowserRunnerSafetyPolicy()

    assert policy.side_effects_enabled is False
    assert policy.to_payload() == {
        "allow_download_click": False,
        "allow_patchops_run": False,
        "allow_paste": False,
        "allow_send": False,
        "side_effects_enabled": False,
    }


def test_validate_safety_policy_blocks_auto_send() -> None:
    options = BrowserRunnerIntegrationOptions(
        safety=BrowserRunnerSafetyPolicy(allow_send=True),
    )

    assert validate_safety_policy(options) == "auto_send_is_not_supported"


def test_validate_safety_policy_blocks_dry_run_side_effects() -> None:
    options = BrowserRunnerIntegrationOptions(
        dry_run_only=True,
        safety=BrowserRunnerSafetyPolicy(allow_download_click=True),
    )

    assert validate_safety_policy(options) == "dry_run_only_disallows_side_effects"


def test_validate_safety_policy_blocks_unsupported_browser() -> None:
    options = BrowserRunnerIntegrationOptions(browser="chrome")  # type: ignore[arg-type]

    assert validate_safety_policy(options) == "unsupported_browser"


def test_planned_actions_show_disabled_adapters() -> None:
    actions = planned_actions_for_options(BrowserRunnerIntegrationOptions())

    assert "capture_page_snapshot" in actions
    assert "download_click_adapter_disabled" in actions
    assert "patchops_run_adapter_disabled" in actions
    assert "paste_adapter_disabled" in actions
    assert "auto_send_adapter_absent" in actions


def test_integration_dry_run_mode_does_not_call_side_effect_adapters(tmp_path: Path) -> None:
    calls: list[str] = []

    def download_provider(filename: str):
        calls.append("download")
        return tmp_path / filename

    def patchops_provider(path):
        calls.append("patchops")
        return _runner_result(tmp_path)

    def report_provider(result):
        calls.append("report")
        return _report_location(tmp_path)

    def paste_provider(summary):
        calls.append("paste")
        return None

    result = run_browser_runner_integration_once(
        BrowserRunnerAdapters(
            snapshot_provider=_snapshot_provider,
            download_provider=download_provider,
            patchops_provider=patchops_provider,
            report_provider=report_provider,
            paste_provider=paste_provider,
        ),
        options=BrowserRunnerIntegrationOptions(dry_run_only=True),
    )

    assert calls == []
    assert result.side_effects_performed == ()
    assert result.dry_run.snapshot.state == OrchestrationState.DOWNLOADING
    assert result.dry_run.side_effects_performed == ()
    assert result.blocked is False


def test_integration_reports_safety_block_without_side_effects() -> None:
    result = run_browser_runner_integration_once(
        BrowserRunnerAdapters(snapshot_provider=_snapshot_provider),
        options=BrowserRunnerIntegrationOptions(
            dry_run_only=True,
            safety=BrowserRunnerSafetyPolicy(allow_patchops_run=True),
        ),
    )

    assert result.blocked is True
    assert result.blocked_reason == "dry_run_only_disallows_side_effects"
    assert result.side_effects_performed == ()


def test_integration_non_dry_run_can_call_enabled_adapters_without_send(tmp_path: Path) -> None:
    calls: list[str] = []

    def download_provider(filename: str):
        calls.append("download")
        return tmp_path / filename

    def patchops_provider(path):
        calls.append("patchops")
        return _runner_result(tmp_path)

    def report_provider(result):
        calls.append("report")
        return _report_location(tmp_path)

    def paste_provider(summary):
        calls.append("paste")
        return None

    result = run_browser_runner_integration_once(
        BrowserRunnerAdapters(
            snapshot_provider=_snapshot_provider,
            download_provider=download_provider,
            patchops_provider=patchops_provider,
            report_provider=report_provider,
            paste_provider=paste_provider,
        ),
        options=BrowserRunnerIntegrationOptions(
            dry_run_only=False,
            safety=BrowserRunnerSafetyPolicy(
                allow_download_click=True,
                allow_patchops_run=True,
                allow_paste=True,
                allow_send=False,
            ),
        ),
    )

    assert calls == ["download", "patchops", "report", "paste"]
    assert result.ok is True
    assert result.dry_run.snapshot.state == OrchestrationState.SUMMARY_READY
    assert result.side_effects_performed == (
        "download_provider_called",
        "patchops_provider_called",
        "report_provider_called",
        "paste_provider_called_without_send",
    )


def test_integration_non_dry_run_blocks_failed_patchops_result(tmp_path: Path) -> None:
    result = run_browser_runner_integration_once(
        BrowserRunnerAdapters(
            snapshot_provider=_snapshot_provider,
            download_provider=lambda filename: tmp_path / filename,
            patchops_provider=lambda path: _runner_result(tmp_path, ok=False),
            report_provider=lambda result: None,
        ),
        options=BrowserRunnerIntegrationOptions(
            dry_run_only=False,
            safety=BrowserRunnerSafetyPolicy(
                allow_download_click=True,
                allow_patchops_run=True,
                allow_paste=False,
            ),
        ),
    )

    assert result.blocked is True
    assert result.dry_run.snapshot.state == OrchestrationState.BLOCKED_PATCHOPS_RUN_FAILED
    assert result.dry_run.pasteback_summary.status == "FAIL"


def test_integration_payload_is_compact(tmp_path: Path) -> None:
    result = run_browser_runner_integration_once(
        BrowserRunnerAdapters(snapshot_provider=_snapshot_provider),
        options=BrowserRunnerIntegrationOptions(browser="opera"),
    )

    payload = result.to_payload()

    assert payload["options"]["browser"] == "opera"
    assert payload["adapter_availability"]["snapshot_provider"] is True
    assert payload["side_effects_performed"] == []
    assert payload["dry_run"]["side_effects_performed"] == []
    assert "latest_assistant_text" not in payload["dry_run"]
