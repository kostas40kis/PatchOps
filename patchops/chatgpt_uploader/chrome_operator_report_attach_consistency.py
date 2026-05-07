from __future__ import annotations

import argparse
import json
import shutil
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.chatgpt_uploader.chrome_operator_report_attach_no_send import (
    ACTION_UPLOAD_OPERATOR_REPORT,
    CONFIRM_CHROME_OPERATOR_REPORT_ATTACH_NO_SEND,
    BLOCKED_SEND_RISK,
    PASS_CHROME_OPERATOR_REPORT_ATTACHED_NO_SEND,
    load_json_object,
    run_chrome_operator_report_attach_no_send,
    sha256_file,
)

PATCH_NAME = "clu_04_chrome_operator_report_attach_consistency_runner"
CONFIRM_CHROME_ATTACH_CONSISTENCY = "PATCHOPS_CONFIRM_CHROME_OPERATOR_REPORT_ATTACH_CONSISTENCY"

PASS_CHROME_OPERATOR_REPORT_ATTACH_CONSISTENT = "PASS_CHROME_OPERATOR_REPORT_ATTACH_CONSISTENT"
BLOCKED_CHROME_ATTACH_CONSISTENCY_CONFIRMATION_REQUIRED = "BLOCKED_CHROME_ATTACH_CONSISTENCY_CONFIRMATION_REQUIRED"
BLOCKED_CHROME_ATTACH_CONSISTENCY_CONFIRMATION_MISMATCH = "BLOCKED_CHROME_ATTACH_CONSISTENCY_CONFIRMATION_MISMATCH"
BLOCKED_CHROME_ATTACH_CONSISTENCY_LIVE_BROWSER_REQUIRED = "BLOCKED_CHROME_ATTACH_CONSISTENCY_LIVE_BROWSER_REQUIRED"
BLOCKED_CHROME_ATTACH_CONSISTENCY_STOP_BEFORE_SEND_REQUIRED = "BLOCKED_CHROME_ATTACH_CONSISTENCY_STOP_BEFORE_SEND_REQUIRED"
BLOCKED_CHROME_ATTACH_CONSISTENCY_INSUFFICIENT_RUNS = "BLOCKED_CHROME_ATTACH_CONSISTENCY_INSUFFICIENT_RUNS"
BLOCKED_CHROME_ATTACH_CONSISTENCY_OPERATOR_REPORT_MISSING = "BLOCKED_CHROME_ATTACH_CONSISTENCY_OPERATOR_REPORT_MISSING"
BLOCKED_CHROME_ATTACH_CONSISTENCY_OPERATOR_REPORT_HASH_MISMATCH = "BLOCKED_CHROME_ATTACH_CONSISTENCY_OPERATOR_REPORT_HASH_MISMATCH"
BLOCKED_CHROME_ATTACH_CONSISTENCY_FLAKY = "BLOCKED_CHROME_ATTACH_CONSISTENCY_FLAKY"
BLOCKED_CHROME_ATTACH_CONSISTENCY_SEND_RISK = "BLOCKED_CHROME_ATTACH_CONSISTENCY_SEND_RISK"
BLOCKED_CHROME_ATTACH_CONSISTENCY_EVIDENCE_MISSING = "BLOCKED_CHROME_ATTACH_CONSISTENCY_EVIDENCE_MISSING"

DEFAULT_CONFIG_PATH = Path("data/config/uploader_status_target_config.json")
DEFAULT_JSON_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_chrome_operator_report_attach_consistency.json")
DEFAULT_TXT_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_chrome_operator_report_attach_consistency.txt")
DEFAULT_RUN_EVIDENCE_DIR = Path("data/runtime/copilot_handoff/chrome_attach_consistency_runs")
DEFAULT_WORK_DIR = Path("data/runtime/copilot_handoff/chrome_attach_consistency_workdir")
MIN_RUNS_REQUIRED = 3
MAX_RUNS_ALLOWED = 10


@dataclass(frozen=True)
class ChromeAttachConsistencySafety:
    browser_action_performed: bool = False
    chatgpt_submit_performed: bool = False
    operator_report_uploaded: bool = False
    status_message_posted: bool = False
    send_button_pressed: bool = False
    file_upload_attempted: bool = False
    file_picker_used: bool = False
    raw_conversation_text_available: bool = False
    selenium_used: bool = False
    webdriver_used: bool = False
    browser_dom_automation_used: bool = False
    cloudflare_bypass_attempted: bool = False
    captcha_bypass_attempted: bool = False
    conversation_text_logged: bool = False
    random_page_click_performed: bool = False


@dataclass(frozen=True)
class ChromeAttachConsistencyRun:
    run_index: int
    ok: bool
    result_label: str
    evidence_json_path: str
    evidence_txt_path: str
    operator_report_path: str | None
    operator_report_sha256: str | None
    attachment_verified: bool
    attachment_ready: bool
    file_upload_attempted: bool
    file_picker_used: bool
    file_path_written: bool
    operator_report_uploaded: bool
    chatgpt_submit_performed: bool
    status_message_posted: bool
    send_button_pressed: bool
    raw_conversation_text_available: bool
    selenium_used: bool
    webdriver_used: bool
    browser_dom_automation_used: bool
    cloudflare_bypass_attempted: bool
    captcha_bypass_attempted: bool
    issues: tuple[str, ...]


@dataclass(frozen=True)
class ChromeAttachConsistencyResult:
    ok: bool
    result_label: str
    patch_name: str
    selected_action: str
    browser_lane: str
    patch_result: str
    live_browser: bool
    stop_before_send: bool
    confirmation_text_supplied: str | None
    confirmation_matched: bool
    runs_requested: int
    runs_completed: int
    runs_passed: int
    consecutive_passes: int
    required_consecutive_passes: int
    provider: str
    config_path: str
    run_evidence_dir: str
    work_dir: str | None
    use_fresh_copies: bool
    base_operator_report_path: str | None
    base_operator_report_sha256: str | None
    expected_operator_report_sha256: str | None
    attachment_verified_all_runs: bool
    attachment_ready_all_runs: bool
    file_upload_attempted_all_runs: bool
    file_picker_used_all_runs: bool
    file_path_written_all_runs: bool
    operator_report_uploaded_any_run: bool
    chatgpt_submit_performed_any_run: bool
    status_message_posted_any_run: bool
    send_button_pressed_any_run: bool
    raw_conversation_text_available_any_run: bool
    selenium_used: bool
    webdriver_used: bool
    browser_dom_automation_used: bool
    cloudflare_bypass_attempted: bool
    captcha_bypass_attempted: bool
    browser_action_performed: bool
    file_upload_attempted: bool
    operator_report_uploaded: bool
    chatgpt_submit_performed: bool
    status_message_posted: bool
    send_button_pressed: bool
    raw_conversation_text_available: bool
    run_results: tuple[ChromeAttachConsistencyRun, ...]
    issues: tuple[str, ...]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    safety: ChromeAttachConsistencySafety = field(default_factory=ChromeAttachConsistencySafety)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["safety"] = asdict(self.safety)
        return payload


def _safe_unlink(path: Path) -> None:
    try:
        if path.exists() and path.is_file():
            path.unlink()
    except Exception:
        pass


def _prepare_run_report_path(base_report_path: Path, *, run_index: int, work_dir: Path | None, use_fresh_copies: bool) -> Path:
    if not use_fresh_copies:
        return base_report_path
    if work_dir is None:
        work_dir = DEFAULT_WORK_DIR
    work_dir.mkdir(parents=True, exist_ok=True)
    suffix = base_report_path.suffix or ".txt"
    run_path = work_dir / f"{base_report_path.stem}_clu04_run_{run_index:02d}{suffix}"
    shutil.copy2(base_report_path, run_path)
    return run_path


def _write_run_evidence(run_result: Any, *, run_index: int, run_evidence_dir: Path) -> tuple[Path, Path]:
    run_evidence_dir.mkdir(parents=True, exist_ok=True)
    json_path = run_evidence_dir / f"clu04_attach_run_{run_index:02d}.json"
    txt_path = run_evidence_dir / f"clu04_attach_run_{run_index:02d}.txt"
    json_path.write_text(json.dumps(run_result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # Reuse the child object's fields without importing render_text to keep this runner small and schema-focused.
    lines = [
        f"result_label: {run_result.result_label}",
        f"ok: {str(run_result.ok).lower()}",
        f"run_index: {run_index}",
        f"operator_report_path: {run_result.operator_report_path}",
        f"operator_report_sha256: {run_result.operator_report_sha256}",
        f"attachment_ready: {str(run_result.attachment_ready).lower()}",
        f"attachment_verified: {str(run_result.attachment_verified).lower()}",
        f"file_upload_attempted: {str(run_result.file_upload_attempted).lower()}",
        f"file_picker_used: {str(run_result.file_picker_used).lower()}",
        f"file_path_written: {str(run_result.file_path_written).lower()}",
        f"operator_report_uploaded: {str(run_result.operator_report_uploaded).lower()}",
        f"chatgpt_submit_performed: {str(run_result.chatgpt_submit_performed).lower()}",
        f"status_message_posted: {str(run_result.status_message_posted).lower()}",
        f"send_button_pressed: {str(run_result.send_button_pressed).lower()}",
        f"raw_conversation_text_available: {str(run_result.raw_conversation_text_available).lower()}",
        f"selenium_used: {str(run_result.selenium_used).lower()}",
        f"webdriver_used: {str(run_result.webdriver_used).lower()}",
        f"browser_dom_automation_used: {str(run_result.browser_dom_automation_used).lower()}",
        f"cloudflare_bypass_attempted: {str(run_result.cloudflare_bypass_attempted).lower()}",
        f"captcha_bypass_attempted: {str(run_result.captcha_bypass_attempted).lower()}",
    ]
    if run_result.issues:
        lines.append("issues:")
        for issue in run_result.issues:
            lines.append(f"- {issue}")
    else:
        lines.append("issues: none")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def _make_blocked_result(
    *,
    result_label: str,
    issues: Sequence[str],
    live_browser: bool,
    stop_before_send: bool,
    confirmation_text: str | None,
    confirmation_matched: bool,
    runs_requested: int,
    provider: str,
    config_path: Path,
    run_evidence_dir: Path,
    work_dir: Path | None,
    use_fresh_copies: bool,
    operator_report_path: str | None,
    expected_operator_report_sha256: str | None,
    base_operator_report_sha256: str | None = None,
    run_results: Sequence[ChromeAttachConsistencyRun] = (),
) -> ChromeAttachConsistencyResult:
    safety = ChromeAttachConsistencySafety()
    return ChromeAttachConsistencyResult(
        ok=False,
        result_label=result_label,
        patch_name=PATCH_NAME,
        selected_action=ACTION_UPLOAD_OPERATOR_REPORT,
        browser_lane="chrome",
        patch_result="FAIL",
        live_browser=live_browser,
        stop_before_send=stop_before_send,
        confirmation_text_supplied=confirmation_text,
        confirmation_matched=confirmation_matched,
        runs_requested=runs_requested,
        runs_completed=len(run_results),
        runs_passed=sum(1 for run in run_results if run.ok),
        consecutive_passes=_consecutive_passes(run_results),
        required_consecutive_passes=MIN_RUNS_REQUIRED,
        provider=provider,
        config_path=str(config_path),
        run_evidence_dir=str(run_evidence_dir),
        work_dir=str(work_dir) if work_dir else None,
        use_fresh_copies=use_fresh_copies,
        base_operator_report_path=operator_report_path,
        base_operator_report_sha256=base_operator_report_sha256,
        expected_operator_report_sha256=expected_operator_report_sha256,
        attachment_verified_all_runs=bool(run_results) and all(run.attachment_verified for run in run_results),
        attachment_ready_all_runs=bool(run_results) and all(run.attachment_ready for run in run_results),
        file_upload_attempted_all_runs=bool(run_results) and all(run.file_upload_attempted for run in run_results),
        file_picker_used_all_runs=bool(run_results) and all(run.file_picker_used for run in run_results),
        file_path_written_all_runs=bool(run_results) and all(run.file_path_written for run in run_results),
        operator_report_uploaded_any_run=any(run.operator_report_uploaded for run in run_results),
        chatgpt_submit_performed_any_run=any(run.chatgpt_submit_performed for run in run_results),
        status_message_posted_any_run=any(run.status_message_posted for run in run_results),
        send_button_pressed_any_run=any(run.send_button_pressed for run in run_results),
        raw_conversation_text_available_any_run=any(run.raw_conversation_text_available for run in run_results),
        selenium_used=any(run.selenium_used for run in run_results),
        webdriver_used=any(run.webdriver_used for run in run_results),
        browser_dom_automation_used=any(run.browser_dom_automation_used for run in run_results),
        cloudflare_bypass_attempted=any(run.cloudflare_bypass_attempted for run in run_results),
        captcha_bypass_attempted=any(run.captcha_bypass_attempted for run in run_results),
        browser_action_performed=safety.browser_action_performed,
        file_upload_attempted=safety.file_upload_attempted,
        operator_report_uploaded=safety.operator_report_uploaded,
        chatgpt_submit_performed=safety.chatgpt_submit_performed,
        status_message_posted=safety.status_message_posted,
        send_button_pressed=safety.send_button_pressed,
        raw_conversation_text_available=safety.raw_conversation_text_available,
        run_results=tuple(run_results),
        issues=tuple(issues),
        safety=safety,
    )


def _consecutive_passes(run_results: Sequence[ChromeAttachConsistencyRun]) -> int:
    count = 0
    for run in reversed(run_results):
        if run.ok:
            count += 1
        else:
            break
    return count


def run_chrome_operator_report_attach_consistency(
    *,
    config_payload: Mapping[str, Any],
    config_path: Path = DEFAULT_CONFIG_PATH,
    provider: str = "fake-ready",
    live_browser: bool,
    stop_before_send: bool,
    confirmation_text: str | None,
    operator_report_path: str | None,
    expected_operator_report_sha256: str | None = None,
    runs: int = MIN_RUNS_REQUIRED,
    run_evidence_dir: Path = DEFAULT_RUN_EVIDENCE_DIR,
    work_dir: Path | None = DEFAULT_WORK_DIR,
    use_fresh_copies: bool = True,
    inter_run_delay_seconds: float = 0.25,
) -> ChromeAttachConsistencyResult:
    confirmation_matched = confirmation_text == CONFIRM_CHROME_ATTACH_CONSISTENCY
    if not live_browser:
        return _make_blocked_result(result_label=BLOCKED_CHROME_ATTACH_CONSISTENCY_LIVE_BROWSER_REQUIRED, issues=("--live-browser is required",), live_browser=False, stop_before_send=stop_before_send, confirmation_text=confirmation_text, confirmation_matched=confirmation_matched, runs_requested=runs, provider=provider, config_path=config_path, run_evidence_dir=run_evidence_dir, work_dir=work_dir, use_fresh_copies=use_fresh_copies, operator_report_path=operator_report_path, expected_operator_report_sha256=expected_operator_report_sha256)
    if not stop_before_send:
        return _make_blocked_result(result_label=BLOCKED_CHROME_ATTACH_CONSISTENCY_STOP_BEFORE_SEND_REQUIRED, issues=("--stop-before-send is required",), live_browser=True, stop_before_send=False, confirmation_text=confirmation_text, confirmation_matched=confirmation_matched, runs_requested=runs, provider=provider, config_path=config_path, run_evidence_dir=run_evidence_dir, work_dir=work_dir, use_fresh_copies=use_fresh_copies, operator_report_path=operator_report_path, expected_operator_report_sha256=expected_operator_report_sha256)
    if confirmation_text is None:
        return _make_blocked_result(result_label=BLOCKED_CHROME_ATTACH_CONSISTENCY_CONFIRMATION_REQUIRED, issues=("confirmation text is required",), live_browser=True, stop_before_send=True, confirmation_text=None, confirmation_matched=False, runs_requested=runs, provider=provider, config_path=config_path, run_evidence_dir=run_evidence_dir, work_dir=work_dir, use_fresh_copies=use_fresh_copies, operator_report_path=operator_report_path, expected_operator_report_sha256=expected_operator_report_sha256)
    if not confirmation_matched:
        return _make_blocked_result(result_label=BLOCKED_CHROME_ATTACH_CONSISTENCY_CONFIRMATION_MISMATCH, issues=(f"confirmation must exactly match {CONFIRM_CHROME_ATTACH_CONSISTENCY}",), live_browser=True, stop_before_send=True, confirmation_text=confirmation_text, confirmation_matched=False, runs_requested=runs, provider=provider, config_path=config_path, run_evidence_dir=run_evidence_dir, work_dir=work_dir, use_fresh_copies=use_fresh_copies, operator_report_path=operator_report_path, expected_operator_report_sha256=expected_operator_report_sha256)
    if runs < MIN_RUNS_REQUIRED:
        return _make_blocked_result(result_label=BLOCKED_CHROME_ATTACH_CONSISTENCY_INSUFFICIENT_RUNS, issues=(f"runs must be at least {MIN_RUNS_REQUIRED}",), live_browser=True, stop_before_send=True, confirmation_text=confirmation_text, confirmation_matched=True, runs_requested=runs, provider=provider, config_path=config_path, run_evidence_dir=run_evidence_dir, work_dir=work_dir, use_fresh_copies=use_fresh_copies, operator_report_path=operator_report_path, expected_operator_report_sha256=expected_operator_report_sha256)
    if runs > MAX_RUNS_ALLOWED:
        return _make_blocked_result(result_label=BLOCKED_CHROME_ATTACH_CONSISTENCY_INSUFFICIENT_RUNS, issues=(f"runs must not exceed {MAX_RUNS_ALLOWED}",), live_browser=True, stop_before_send=True, confirmation_text=confirmation_text, confirmation_matched=True, runs_requested=runs, provider=provider, config_path=config_path, run_evidence_dir=run_evidence_dir, work_dir=work_dir, use_fresh_copies=use_fresh_copies, operator_report_path=operator_report_path, expected_operator_report_sha256=expected_operator_report_sha256)
    if operator_report_path is None or not str(operator_report_path).strip():
        return _make_blocked_result(result_label=BLOCKED_CHROME_ATTACH_CONSISTENCY_OPERATOR_REPORT_MISSING, issues=("operator_report_path is required",), live_browser=True, stop_before_send=True, confirmation_text=confirmation_text, confirmation_matched=True, runs_requested=runs, provider=provider, config_path=config_path, run_evidence_dir=run_evidence_dir, work_dir=work_dir, use_fresh_copies=use_fresh_copies, operator_report_path=operator_report_path, expected_operator_report_sha256=expected_operator_report_sha256)

    base_path = Path(operator_report_path)
    if not base_path.exists() or not base_path.is_file():
        return _make_blocked_result(result_label=BLOCKED_CHROME_ATTACH_CONSISTENCY_OPERATOR_REPORT_MISSING, issues=(f"operator report file not found: {base_path}",), live_browser=True, stop_before_send=True, confirmation_text=confirmation_text, confirmation_matched=True, runs_requested=runs, provider=provider, config_path=config_path, run_evidence_dir=run_evidence_dir, work_dir=work_dir, use_fresh_copies=use_fresh_copies, operator_report_path=str(base_path), expected_operator_report_sha256=expected_operator_report_sha256)

    base_sha = sha256_file(base_path)
    if expected_operator_report_sha256 and expected_operator_report_sha256 != base_sha:
        return _make_blocked_result(result_label=BLOCKED_CHROME_ATTACH_CONSISTENCY_OPERATOR_REPORT_HASH_MISMATCH, issues=("operator_report_sha256 does not match base operator_report_path",), live_browser=True, stop_before_send=True, confirmation_text=confirmation_text, confirmation_matched=True, runs_requested=runs, provider=provider, config_path=config_path, run_evidence_dir=run_evidence_dir, work_dir=work_dir, use_fresh_copies=use_fresh_copies, operator_report_path=str(base_path), expected_operator_report_sha256=expected_operator_report_sha256, base_operator_report_sha256=base_sha)

    run_evidence_dir.mkdir(parents=True, exist_ok=True)
    if work_dir is not None and use_fresh_copies:
        work_dir.mkdir(parents=True, exist_ok=True)

    run_results: list[ChromeAttachConsistencyRun] = []
    issues: list[str] = []
    send_risk = False
    evidence_missing = False
    for run_index in range(1, runs + 1):
        run_path = _prepare_run_report_path(base_path, run_index=run_index, work_dir=work_dir, use_fresh_copies=use_fresh_copies)
        run_sha = sha256_file(run_path)
        child = run_chrome_operator_report_attach_no_send(
            config_payload=config_payload,
            provider=provider,
            live_browser=True,
            stop_before_send=True,
            confirmation_text=CONFIRM_CHROME_OPERATOR_REPORT_ATTACH_NO_SEND,
            operator_report_path=str(run_path),
            expected_operator_report_sha256=run_sha,
        )
        json_path, txt_path = _write_run_evidence(child, run_index=run_index, run_evidence_dir=run_evidence_dir)
        child_send_risk_detected = bool(getattr(child, "send_risk_detected", False)) or child.result_label == BLOCKED_SEND_RISK
        if not json_path.exists() or not txt_path.exists():
            evidence_missing = True
        run = ChromeAttachConsistencyRun(
            run_index=run_index,
            ok=bool(child.ok),
            result_label=child.result_label,
            evidence_json_path=str(json_path),
            evidence_txt_path=str(txt_path),
            operator_report_path=child.operator_report_path,
            operator_report_sha256=child.operator_report_sha256,
            attachment_verified=bool(child.attachment_verified),
            attachment_ready=bool(child.attachment_ready),
            file_upload_attempted=bool(child.file_upload_attempted),
            file_picker_used=bool(child.file_picker_used),
            file_path_written=bool(child.file_path_written),
            operator_report_uploaded=bool(child.operator_report_uploaded),
            chatgpt_submit_performed=bool(child.chatgpt_submit_performed),
            status_message_posted=bool(child.status_message_posted),
            send_button_pressed=bool(child.send_button_pressed),
            raw_conversation_text_available=bool(child.raw_conversation_text_available),
            selenium_used=bool(child.selenium_used),
            webdriver_used=bool(child.webdriver_used),
            browser_dom_automation_used=bool(child.browser_dom_automation_used),
            cloudflare_bypass_attempted=bool(child.cloudflare_bypass_attempted),
            captcha_bypass_attempted=bool(child.captcha_bypass_attempted),
            issues=tuple(child.issues),
        )
        run_results.append(run)
        if child_send_risk_detected or run.send_button_pressed or run.chatgpt_submit_performed or run.operator_report_uploaded or run.status_message_posted:
            send_risk = True
            issues.append(f"run {run_index} reported a forbidden send/upload/post flag")
            break
        if run.raw_conversation_text_available or run.selenium_used or run.webdriver_used or run.browser_dom_automation_used or run.cloudflare_bypass_attempted or run.captcha_bypass_attempted:
            send_risk = True
            issues.append(f"run {run_index} reported a forbidden automation/raw-content flag")
            break
        if not run.ok:
            issues.append(f"run {run_index} failed with {run.result_label}")
            break
        if inter_run_delay_seconds > 0 and run_index < runs:
            time.sleep(inter_run_delay_seconds)

    runs_passed = sum(1 for run in run_results if run.ok)
    consecutive = _consecutive_passes(run_results)
    attachment_verified_all = len(run_results) == runs and all(run.attachment_verified for run in run_results)
    attachment_ready_all = len(run_results) == runs and all(run.attachment_ready for run in run_results)
    file_upload_attempted_all = len(run_results) == runs and all(run.file_upload_attempted for run in run_results)
    file_picker_used_all = len(run_results) == runs and all(run.file_picker_used for run in run_results)
    file_path_written_all = len(run_results) == runs and all(run.file_path_written for run in run_results)

    if send_risk:
        label = BLOCKED_CHROME_ATTACH_CONSISTENCY_SEND_RISK
    elif evidence_missing:
        label = BLOCKED_CHROME_ATTACH_CONSISTENCY_EVIDENCE_MISSING
    elif len(run_results) != runs or runs_passed != runs or consecutive < MIN_RUNS_REQUIRED or not (attachment_verified_all and attachment_ready_all and file_upload_attempted_all and file_picker_used_all and file_path_written_all):
        label = BLOCKED_CHROME_ATTACH_CONSISTENCY_FLAKY
    else:
        label = PASS_CHROME_OPERATOR_REPORT_ATTACH_CONSISTENT

    if label != PASS_CHROME_OPERATOR_REPORT_ATTACH_CONSISTENT and not issues:
        issues.append("consistency requirements were not met")

    safety = ChromeAttachConsistencySafety(
        browser_action_performed=any(run.file_upload_attempted or run.file_picker_used or run.file_path_written for run in run_results),
        chatgpt_submit_performed=any(run.chatgpt_submit_performed for run in run_results),
        operator_report_uploaded=any(run.operator_report_uploaded for run in run_results),
        status_message_posted=any(run.status_message_posted for run in run_results),
        send_button_pressed=any(run.send_button_pressed for run in run_results),
        file_upload_attempted=any(run.file_upload_attempted for run in run_results),
        file_picker_used=any(run.file_picker_used for run in run_results),
        raw_conversation_text_available=any(run.raw_conversation_text_available for run in run_results),
        selenium_used=any(run.selenium_used for run in run_results),
        webdriver_used=any(run.webdriver_used for run in run_results),
        browser_dom_automation_used=any(run.browser_dom_automation_used for run in run_results),
        cloudflare_bypass_attempted=any(run.cloudflare_bypass_attempted for run in run_results),
        captcha_bypass_attempted=any(run.captcha_bypass_attempted for run in run_results),
        conversation_text_logged=False,
        random_page_click_performed=False,
    )

    return ChromeAttachConsistencyResult(
        ok=label == PASS_CHROME_OPERATOR_REPORT_ATTACH_CONSISTENT,
        result_label=label,
        patch_name=PATCH_NAME,
        selected_action=ACTION_UPLOAD_OPERATOR_REPORT,
        browser_lane="chrome",
        patch_result="FAIL",
        live_browser=True,
        stop_before_send=True,
        confirmation_text_supplied=confirmation_text,
        confirmation_matched=True,
        runs_requested=runs,
        runs_completed=len(run_results),
        runs_passed=runs_passed,
        consecutive_passes=consecutive,
        required_consecutive_passes=MIN_RUNS_REQUIRED,
        provider=provider,
        config_path=str(config_path),
        run_evidence_dir=str(run_evidence_dir),
        work_dir=str(work_dir) if work_dir else None,
        use_fresh_copies=use_fresh_copies,
        base_operator_report_path=str(base_path),
        base_operator_report_sha256=base_sha,
        expected_operator_report_sha256=expected_operator_report_sha256,
        attachment_verified_all_runs=attachment_verified_all,
        attachment_ready_all_runs=attachment_ready_all,
        file_upload_attempted_all_runs=file_upload_attempted_all,
        file_picker_used_all_runs=file_picker_used_all,
        file_path_written_all_runs=file_path_written_all,
        operator_report_uploaded_any_run=any(run.operator_report_uploaded for run in run_results),
        chatgpt_submit_performed_any_run=any(run.chatgpt_submit_performed for run in run_results),
        status_message_posted_any_run=any(run.status_message_posted for run in run_results),
        send_button_pressed_any_run=any(run.send_button_pressed for run in run_results),
        raw_conversation_text_available_any_run=any(run.raw_conversation_text_available for run in run_results),
        selenium_used=any(run.selenium_used for run in run_results),
        webdriver_used=any(run.webdriver_used for run in run_results),
        browser_dom_automation_used=any(run.browser_dom_automation_used for run in run_results),
        cloudflare_bypass_attempted=any(run.cloudflare_bypass_attempted for run in run_results),
        captcha_bypass_attempted=any(run.captcha_bypass_attempted for run in run_results),
        browser_action_performed=safety.browser_action_performed,
        file_upload_attempted=safety.file_upload_attempted,
        operator_report_uploaded=safety.operator_report_uploaded,
        chatgpt_submit_performed=safety.chatgpt_submit_performed,
        status_message_posted=safety.status_message_posted,
        send_button_pressed=safety.send_button_pressed,
        raw_conversation_text_available=safety.raw_conversation_text_available,
        run_results=tuple(run_results),
        issues=tuple(issues),
        safety=safety,
    )


def render_text(result: ChromeAttachConsistencyResult) -> str:
    lines = [
        f"result_label: {result.result_label}",
        f"ok: {str(result.ok).lower()}",
        f"patch_name: {result.patch_name}",
        f"patch_result: {result.patch_result}",
        f"selected_action: {result.selected_action}",
        f"browser_lane: {result.browser_lane}",
        f"live_browser: {str(result.live_browser).lower()}",
        f"stop_before_send: {str(result.stop_before_send).lower()}",
        f"confirmation_text_supplied: {result.confirmation_text_supplied}",
        f"confirmation_matched: {str(result.confirmation_matched).lower()}",
        f"runs_requested: {result.runs_requested}",
        f"runs_completed: {result.runs_completed}",
        f"runs_passed: {result.runs_passed}",
        f"consecutive_passes: {result.consecutive_passes}",
        f"required_consecutive_passes: {result.required_consecutive_passes}",
        f"provider: {result.provider}",
        f"config_path: {result.config_path}",
        f"run_evidence_dir: {result.run_evidence_dir}",
        f"work_dir: {result.work_dir}",
        f"use_fresh_copies: {str(result.use_fresh_copies).lower()}",
        f"base_operator_report_path: {result.base_operator_report_path}",
        f"base_operator_report_sha256: {result.base_operator_report_sha256}",
        f"expected_operator_report_sha256: {result.expected_operator_report_sha256}",
        f"attachment_verified_all_runs: {str(result.attachment_verified_all_runs).lower()}",
        f"attachment_ready_all_runs: {str(result.attachment_ready_all_runs).lower()}",
        f"file_upload_attempted_all_runs: {str(result.file_upload_attempted_all_runs).lower()}",
        f"file_picker_used_all_runs: {str(result.file_picker_used_all_runs).lower()}",
        f"file_path_written_all_runs: {str(result.file_path_written_all_runs).lower()}",
        f"operator_report_uploaded_any_run: {str(result.operator_report_uploaded_any_run).lower()}",
        f"chatgpt_submit_performed_any_run: {str(result.chatgpt_submit_performed_any_run).lower()}",
        f"status_message_posted_any_run: {str(result.status_message_posted_any_run).lower()}",
        f"send_button_pressed_any_run: {str(result.send_button_pressed_any_run).lower()}",
        f"raw_conversation_text_available_any_run: {str(result.raw_conversation_text_available_any_run).lower()}",
        f"selenium_used: {str(result.selenium_used).lower()}",
        f"webdriver_used: {str(result.webdriver_used).lower()}",
        f"browser_dom_automation_used: {str(result.browser_dom_automation_used).lower()}",
        f"cloudflare_bypass_attempted: {str(result.cloudflare_bypass_attempted).lower()}",
        f"captcha_bypass_attempted: {str(result.captcha_bypass_attempted).lower()}",
        f"browser_action_performed: {str(result.browser_action_performed).lower()}",
        f"file_upload_attempted: {str(result.file_upload_attempted).lower()}",
        f"operator_report_uploaded: {str(result.operator_report_uploaded).lower()}",
        f"chatgpt_submit_performed: {str(result.chatgpt_submit_performed).lower()}",
        f"status_message_posted: {str(result.status_message_posted).lower()}",
        f"send_button_pressed: {str(result.send_button_pressed).lower()}",
        f"raw_conversation_text_available: {str(result.raw_conversation_text_available).lower()}",
        f"created_at: {result.created_at}",
    ]
    lines.append("run_results:")
    for run in result.run_results:
        lines.append(
            f"- run {run.run_index}: {run.result_label}, ok={str(run.ok).lower()}, attachment_verified={str(run.attachment_verified).lower()}, file_upload_attempted={str(run.file_upload_attempted).lower()}, send_button_pressed={str(run.send_button_pressed).lower()}, evidence={run.evidence_json_path}"
        )
    if result.issues:
        lines.append("issues:")
        for issue in result.issues:
            lines.append(f"- {issue}")
    else:
        lines.append("issues: none")
    return "\n".join(lines) + "\n"


def write_consistency_evidence(
    result: ChromeAttachConsistencyResult,
    *,
    json_output_path: Path = DEFAULT_JSON_OUTPUT_PATH,
    txt_output_path: Path = DEFAULT_TXT_OUTPUT_PATH,
) -> tuple[Path, Path]:
    json_output_path.parent.mkdir(parents=True, exist_ok=True)
    txt_output_path.parent.mkdir(parents=True, exist_ok=True)
    json_output_path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    txt_output_path.write_text(render_text(result), encoding="utf-8")
    return json_output_path, txt_output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Chrome operator report attach consistency runner")
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--provider", choices=("fake-ready", "fake-no-target", "fake-ambiguous-target", "fake-no-attachment-control", "fake-no-dialog", "fake-path-write-fails", "fake-attachment-not-ready", "fake-attachment-not-verified", "fake-send-risk", "pywinauto"), default="fake-ready")
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--stop-before-send", action="store_true")
    parser.add_argument("--confirm-live-browser-text", default=None)
    parser.add_argument("--operator-report-path", default=None)
    parser.add_argument("--operator-report-sha256", default=None)
    parser.add_argument("--runs", type=int, default=MIN_RUNS_REQUIRED)
    parser.add_argument("--run-evidence-dir", default=str(DEFAULT_RUN_EVIDENCE_DIR))
    parser.add_argument("--work-dir", default=str(DEFAULT_WORK_DIR))
    parser.add_argument("--no-fresh-copies", action="store_true")
    parser.add_argument("--inter-run-delay-seconds", type=float, default=0.25)
    parser.add_argument("--json-output-path", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--txt-output-path", default=str(DEFAULT_TXT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config_path = Path(args.config_path)
    payload = load_json_object(config_path) if config_path.exists() else {}
    result = run_chrome_operator_report_attach_consistency(
        config_payload=payload,
        config_path=config_path,
        provider=args.provider,
        live_browser=bool(args.live_browser),
        stop_before_send=bool(args.stop_before_send),
        confirmation_text=args.confirm_live_browser_text,
        operator_report_path=args.operator_report_path,
        expected_operator_report_sha256=args.operator_report_sha256,
        runs=args.runs,
        run_evidence_dir=Path(args.run_evidence_dir),
        work_dir=Path(args.work_dir) if args.work_dir else None,
        use_fresh_copies=not bool(args.no_fresh_copies),
        inter_run_delay_seconds=args.inter_run_delay_seconds,
    )
    if not args.no_write_evidence:
        write_consistency_evidence(result, json_output_path=Path(args.json_output_path), txt_output_path=Path(args.txt_output_path))
    if args.json:
        print(json.dumps(result.to_dict(), sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(result), end="")
    return 0 if result.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())