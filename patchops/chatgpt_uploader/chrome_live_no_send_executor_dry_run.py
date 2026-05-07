from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

PASS_CHROME_LIVE_NO_SEND_EXECUTOR_DRY_RUN_VALIDATED = "PASS_CHROME_LIVE_NO_SEND_EXECUTOR_DRY_RUN_VALIDATED"
PASS_CHROME_LIVE_NO_SEND_EXECUTOR_DRY_RUN_WRITTEN = "PASS_CHROME_LIVE_NO_SEND_EXECUTOR_DRY_RUN_WRITTEN"
BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_PLAN_MISSING = "BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_PLAN_MISSING"
BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_PLAN_INVALID_JSON = "BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_PLAN_INVALID_JSON"
BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_UNSUPPORTED_KIND = "BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_UNSUPPORTED_KIND"
BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_PLAN_NOT_READY = "BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_PLAN_NOT_READY"
BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_UNSAFE = "BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_UNSAFE"

EXPECTED_BROWSER = "chrome"
EXPECTED_PLAN_KIND = "chrome_uploader_live_no_send_executor_plan"
EXPECTED_PLAN_RESULT = "PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_VALIDATED"
DRY_RUN_SCHEMA_VERSION = "1"
DRY_RUN_KIND = "chrome_uploader_live_no_send_executor_dry_run"
DEFAULT_PLAN_RELATIVE_PATH = "data/runtime/copilot_handoff/latest_uploader_live_no_send_executor_plan.json"
DEFAULT_DRY_RUN_RELATIVE_PATH = "data/runtime/copilot_handoff/latest_uploader_live_no_send_executor_dry_run.json"
DEFAULT_MARKER_RELATIVE_PATH = "data/runtime/copilot_handoff/latest_uploader_live_no_send_executor_dry_run.txt"
DEFAULT_ALLOWED_NEXT_SCRIPT = "scripts/run_uploader_chrome_live_no_send_executor.py"

FORBIDDEN_TRUE_FLAGS = {
    "selenium_used",
    "webdriver_used",
    "browser_dom_automation_used",
    "cloudflare_bypass_attempted",
    "captcha_bypass_attempted",
    "conversation_text_logged",
    "raw_conversation_text_logged",
    "random_page_click_performed",
    "chatgpt_submit_performed",
    "browser_action_performed",
    "send_button_pressed",
    "raw_conversation_text_available",
    "executor_plan_performs_browser_action",
    "executor_plan_performs_chatgpt_submit",
    "executor_plan_reads_conversation_text",
    "dry_run_performs_browser_action",
    "dry_run_performs_chatgpt_submit",
    "dry_run_reads_conversation_text",
    "executor_dry_run_performed_live_action",
    "send_allowed",
}
REQUIRED_TRUE_FIELDS = {
    "executor_plan_ready",
    "no_send_verified",
    "attachment_verified",
    "safe_for_downstream_planning",
    "human_supervision_required",
    "human_must_confirm_visible_chrome",
    "human_must_verify_no_send",
}
REQUIRED_FALSE_FIELDS = {
    "executor_plan_performs_browser_action",
    "executor_plan_performs_chatgpt_submit",
    "executor_plan_reads_conversation_text",
    "browser_action_performed",
    "chatgpt_submit_performed",
    "send_allowed",
    "raw_conversation_text_available",
}

DEFAULT_DRY_RUN_CHECKLIST = [
    "operator_confirms_existing_chrome_visible",
    "operator_confirms_target_conversation_already_open",
    "operator_confirms_no_cloudflare_or_captcha_or_modal",
    "operator_confirms_canonical_attachment_path_available",
    "operator_understands_future_executor_stops_before_send",
]
DEFAULT_STOP_CONDITIONS = [
    "visible_chrome_target_missing",
    "wrong_browser_or_non_chrome_target",
    "hidden_or_minimized_browser_window",
    "ambiguous_chrome_target",
    "cloudflare_or_captcha_detected",
    "unexpected_modal_or_error_dialog",
    "send_button_focus_or_submit_risk",
    "conversation_text_required",
    "attachment_chip_missing_or_mismatched",
    "canonical_path_unavailable",
    "any_request_to_read_conversation_text",
    "any_request_to_press_send",
]
DEFAULT_FORBIDDEN_ACTIONS = [
    "send_chatgpt_message",
    "press_send_button",
    "read_conversation_text",
    "log_raw_conversation_text",
    "use_dom_automation",
    "use_webdriver",
    "bypass_cloudflare_or_captcha",
    "random_click",
    "open_hidden_browser",
]


@dataclass(frozen=True)
class ChromeLiveNoSendExecutorDryRun:
    ok: bool
    result: str
    schema_version: str
    dry_run_kind: str
    expected_browser: str
    source_plan_basename: str | None
    source_plan_sha256: str | None
    source_contract_basename: str | None
    source_packet_basename: str | None
    source_boundary_basename: str | None
    source_ready_basename: str | None
    source_consumed_basename: str | None
    source_handoff_basename: str | None
    source_acceptance_basename: str | None
    plan_kind: str | None
    plan_result: str | None
    contract_kind: str | None
    contract_result: str | None
    packet_kind: str | None
    packet_result: str | None
    boundary_kind: str | None
    boundary_result: str | None
    dry_run_ready: bool
    executor_plan_ready: bool
    no_send_verified: bool
    attachment_verified: bool
    safe_for_downstream_planning: bool
    human_supervision_required: bool
    human_must_confirm_visible_chrome: bool
    human_must_verify_no_send: bool
    dry_run_performs_browser_action: bool
    dry_run_performs_chatgpt_submit: bool
    dry_run_reads_conversation_text: bool
    executor_dry_run_performed_live_action: bool
    browser_action_performed: bool
    chatgpt_submit_performed: bool
    send_allowed: bool
    raw_conversation_text_available: bool
    required_visible_state: list[str]
    execution_steps: list[str]
    dry_run_checklist: list[str]
    stop_conditions: list[str]
    forbidden_actions: list[str]
    allowed_next_script: str | None
    forbidden_true_flags: list[str]
    dry_run_created_utc: str | None
    reason: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def sha256_file(path: Path | str) -> str:
    resolved = Path(path).expanduser().resolve()
    digest = hashlib.sha256()
    with resolved.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _list(payload: Mapping[str, Any], key: str, fallback: list[str]) -> list[str]:
    value = payload.get(key)
    if isinstance(value, list):
        found = [str(item) for item in value if item is not None]
        return found if found else list(fallback)
    return list(fallback)


def forbidden_flags(payload: Mapping[str, Any]) -> list[str]:
    found = set(str(item) for item in payload.get("forbidden_true_flags", []) if item)
    safety = payload.get("safety_flags")
    if isinstance(safety, dict):
        for key in FORBIDDEN_TRUE_FLAGS:
            if bool(safety.get(key, False)):
                found.add(key)
    for key in FORBIDDEN_TRUE_FLAGS:
        if bool(payload.get(key, False)):
            found.add(key)
    return sorted(found)


def _dry_run(
    *,
    ok: bool,
    result: str,
    payload: Mapping[str, Any],
    source_plan_basename: str | None,
    source_plan_sha256: str | None,
    reason: str,
) -> ChromeLiveNoSendExecutorDryRun:
    stop_conditions = _list(payload, "executor_stop_conditions", DEFAULT_STOP_CONDITIONS)
    merged_stops = list(dict.fromkeys(stop_conditions + ["any_request_to_read_conversation_text", "any_request_to_press_send"]))
    return ChromeLiveNoSendExecutorDryRun(
        ok=bool(ok),
        result=result,
        schema_version=DRY_RUN_SCHEMA_VERSION,
        dry_run_kind=DRY_RUN_KIND,
        expected_browser=EXPECTED_BROWSER,
        source_plan_basename=source_plan_basename,
        source_plan_sha256=source_plan_sha256,
        source_contract_basename=payload.get("source_contract_basename"),
        source_packet_basename=payload.get("source_packet_basename"),
        source_boundary_basename=payload.get("source_boundary_basename"),
        source_ready_basename=payload.get("source_ready_basename"),
        source_consumed_basename=payload.get("source_consumed_basename"),
        source_handoff_basename=payload.get("source_handoff_basename"),
        source_acceptance_basename=payload.get("source_acceptance_basename"),
        plan_kind=payload.get("plan_kind"),
        plan_result=payload.get("result"),
        contract_kind=payload.get("contract_kind"),
        contract_result=payload.get("contract_result"),
        packet_kind=payload.get("packet_kind"),
        packet_result=payload.get("packet_result"),
        boundary_kind=payload.get("boundary_kind"),
        boundary_result=payload.get("boundary_result"),
        dry_run_ready=bool(ok),
        executor_plan_ready=bool(payload.get("executor_plan_ready", False)),
        no_send_verified=bool(payload.get("no_send_verified", False)),
        attachment_verified=bool(payload.get("attachment_verified", False)),
        safe_for_downstream_planning=bool(payload.get("safe_for_downstream_planning", False)),
        human_supervision_required=bool(payload.get("human_supervision_required", True)),
        human_must_confirm_visible_chrome=bool(payload.get("human_must_confirm_visible_chrome", True)),
        human_must_verify_no_send=bool(payload.get("human_must_verify_no_send", True)),
        dry_run_performs_browser_action=False,
        dry_run_performs_chatgpt_submit=False,
        dry_run_reads_conversation_text=False,
        executor_dry_run_performed_live_action=False,
        browser_action_performed=False,
        chatgpt_submit_performed=False,
        send_allowed=False,
        raw_conversation_text_available=False,
        required_visible_state=_list(payload, "required_visible_state", []) if ok else [],
        execution_steps=_list(payload, "execution_steps", []) if ok else [],
        dry_run_checklist=list(DEFAULT_DRY_RUN_CHECKLIST) if ok else [],
        stop_conditions=merged_stops,
        forbidden_actions=_list(payload, "forbidden_actions", DEFAULT_FORBIDDEN_ACTIONS),
        allowed_next_script=payload.get("allowed_next_script") if ok else None,
        forbidden_true_flags=forbidden_flags(payload),
        dry_run_created_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat() if ok else None,
        reason=reason,
    )


def validate_executor_plan_payload(
    payload: Mapping[str, Any],
    *,
    source_plan_basename: str | None = None,
    source_plan_sha256: str | None = None,
) -> ChromeLiveNoSendExecutorDryRun:
    plan_kind = payload.get("plan_kind")
    plan_result = payload.get("result")
    forbidden = forbidden_flags(payload)
    missing_true = sorted(key for key in REQUIRED_TRUE_FIELDS if not bool(payload.get(key, False)))
    false_violations = sorted(key for key in REQUIRED_FALSE_FIELDS if bool(payload.get(key, False)))

    if plan_kind != EXPECTED_PLAN_KIND:
        return _dry_run(
            ok=False,
            result=BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_UNSUPPORTED_KIND,
            payload=payload,
            source_plan_basename=source_plan_basename,
            source_plan_sha256=source_plan_sha256,
            reason="Executor plan kind is not chrome_uploader_live_no_send_executor_plan.",
        )
    if forbidden:
        return _dry_run(
            ok=False,
            result=BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_UNSAFE,
            payload=payload,
            source_plan_basename=source_plan_basename,
            source_plan_sha256=source_plan_sha256,
            reason="Executor plan contains forbidden true safety flags.",
        )
    if (
        not bool(payload.get("ok", False))
        or plan_result != EXPECTED_PLAN_RESULT
        or payload.get("expected_browser") != EXPECTED_BROWSER
        or not bool(payload.get("executor_plan_ready", False))
        or payload.get("allowed_next_script") != DEFAULT_ALLOWED_NEXT_SCRIPT
        or missing_true
        or false_violations
    ):
        reason = "Executor plan is not ready for dry-run validation."
        if missing_true:
            reason += " Missing true fields: " + ",".join(missing_true)
        if false_violations:
            reason += " False-field violations: " + ",".join(false_violations)
        if payload.get("allowed_next_script") != DEFAULT_ALLOWED_NEXT_SCRIPT:
            reason += " allowed_next_script must be scripts/run_uploader_chrome_live_no_send_executor.py."
        return _dry_run(
            ok=False,
            result=BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_PLAN_NOT_READY,
            payload=payload,
            source_plan_basename=source_plan_basename,
            source_plan_sha256=source_plan_sha256,
            reason=reason,
        )

    return _dry_run(
        ok=True,
        result=PASS_CHROME_LIVE_NO_SEND_EXECUTOR_DRY_RUN_VALIDATED,
        payload=payload,
        source_plan_basename=source_plan_basename,
        source_plan_sha256=source_plan_sha256,
        reason="Chrome live no-send executor dry run validated from executor plan; no browser action was performed.",
    )


def load_and_validate_executor_plan(path: Path | str) -> ChromeLiveNoSendExecutorDryRun:
    plan_path = Path(path).expanduser().resolve()
    if not plan_path.exists():
        return ChromeLiveNoSendExecutorDryRun(
            ok=False,
            result=BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_PLAN_MISSING,
            schema_version=DRY_RUN_SCHEMA_VERSION,
            dry_run_kind=DRY_RUN_KIND,
            expected_browser=EXPECTED_BROWSER,
            source_plan_basename=plan_path.name,
            source_plan_sha256=None,
            source_contract_basename=None,
            source_packet_basename=None,
            source_boundary_basename=None,
            source_ready_basename=None,
            source_consumed_basename=None,
            source_handoff_basename=None,
            source_acceptance_basename=None,
            plan_kind=None,
            plan_result=None,
            contract_kind=None,
            contract_result=None,
            packet_kind=None,
            packet_result=None,
            boundary_kind=None,
            boundary_result=None,
            dry_run_ready=False,
            executor_plan_ready=False,
            no_send_verified=False,
            attachment_verified=False,
            safe_for_downstream_planning=False,
            human_supervision_required=True,
            human_must_confirm_visible_chrome=True,
            human_must_verify_no_send=True,
            dry_run_performs_browser_action=False,
            dry_run_performs_chatgpt_submit=False,
            dry_run_reads_conversation_text=False,
            executor_dry_run_performed_live_action=False,
            browser_action_performed=False,
            chatgpt_submit_performed=False,
            send_allowed=False,
            raw_conversation_text_available=False,
            required_visible_state=[],
            execution_steps=[],
            dry_run_checklist=[],
            stop_conditions=["executor_plan_missing"],
            forbidden_actions=list(DEFAULT_FORBIDDEN_ACTIONS),
            allowed_next_script=None,
            forbidden_true_flags=[],
            dry_run_created_utc=None,
            reason="Executor plan JSON file is missing.",
        )
    try:
        payload = json.loads(plan_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return ChromeLiveNoSendExecutorDryRun(
            ok=False,
            result=BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_PLAN_INVALID_JSON,
            schema_version=DRY_RUN_SCHEMA_VERSION,
            dry_run_kind=DRY_RUN_KIND,
            expected_browser=EXPECTED_BROWSER,
            source_plan_basename=plan_path.name,
            source_plan_sha256=sha256_file(plan_path),
            source_contract_basename=None,
            source_packet_basename=None,
            source_boundary_basename=None,
            source_ready_basename=None,
            source_consumed_basename=None,
            source_handoff_basename=None,
            source_acceptance_basename=None,
            plan_kind=None,
            plan_result=None,
            contract_kind=None,
            contract_result=None,
            packet_kind=None,
            packet_result=None,
            boundary_kind=None,
            boundary_result=None,
            dry_run_ready=False,
            executor_plan_ready=False,
            no_send_verified=False,
            attachment_verified=False,
            safe_for_downstream_planning=False,
            human_supervision_required=True,
            human_must_confirm_visible_chrome=True,
            human_must_verify_no_send=True,
            dry_run_performs_browser_action=False,
            dry_run_performs_chatgpt_submit=False,
            dry_run_reads_conversation_text=False,
            executor_dry_run_performed_live_action=False,
            browser_action_performed=False,
            chatgpt_submit_performed=False,
            send_allowed=False,
            raw_conversation_text_available=False,
            required_visible_state=[],
            execution_steps=[],
            dry_run_checklist=[],
            stop_conditions=["executor_plan_invalid_json"],
            forbidden_actions=list(DEFAULT_FORBIDDEN_ACTIONS),
            allowed_next_script=None,
            forbidden_true_flags=[],
            dry_run_created_utc=None,
            reason=f"Executor plan JSON is invalid: {exc}",
        )
    if not isinstance(payload, dict):
        payload = {}
    return validate_executor_plan_payload(
        payload,
        source_plan_basename=plan_path.name,
        source_plan_sha256=sha256_file(plan_path),
    )


def write_executor_dry_run(dry_run: ChromeLiveNoSendExecutorDryRun, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = dry_run.to_payload()
    payload["write_result"] = PASS_CHROME_LIVE_NO_SEND_EXECUTOR_DRY_RUN_WRITTEN if dry_run.ok else dry_run.result
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def write_executor_dry_run_marker(dry_run: ChromeLiveNoSendExecutorDryRun, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "Chrome live no-send executor dry run",
        "====================================",
        f"result:{dry_run.result}",
        f"ok:{str(dry_run.ok).lower()}",
        f"dry_run_kind:{dry_run.dry_run_kind}",
        f"expected_browser:{dry_run.expected_browser}",
        f"plan_kind:{dry_run.plan_kind or ''}",
        f"plan_result:{dry_run.plan_result or ''}",
        f"dry_run_ready:{str(dry_run.dry_run_ready).lower()}",
        f"executor_plan_ready:{str(dry_run.executor_plan_ready).lower()}",
        f"no_send_verified:{str(dry_run.no_send_verified).lower()}",
        f"attachment_verified:{str(dry_run.attachment_verified).lower()}",
        f"safe_for_downstream_planning:{str(dry_run.safe_for_downstream_planning).lower()}",
        "dry_run_performs_browser_action:false",
        "dry_run_performs_chatgpt_submit:false",
        "dry_run_reads_conversation_text:false",
        "executor_dry_run_performed_live_action:false",
        "browser_action_performed:false",
        "chatgpt_submit_performed:false",
        "send_allowed:false",
        "raw_conversation_text_available:false",
        f"human_supervision_required:{str(dry_run.human_supervision_required).lower()}",
        f"human_must_confirm_visible_chrome:{str(dry_run.human_must_confirm_visible_chrome).lower()}",
        f"human_must_verify_no_send:{str(dry_run.human_must_verify_no_send).lower()}",
        "selenium_used:false",
        "webdriver_used:false",
        "browser_dom_automation_used:false",
        "cloudflare_bypass_attempted:false",
        "captcha_bypass_attempted:false",
        "conversation_text_logged:false",
        "raw_conversation_text_logged:false",
        "random_page_click_performed:false",
        "",
        "Dry-run checklist",
        "-----------------",
    ]
    lines.extend(f"- {item}" for item in dry_run.dry_run_checklist)
    lines.extend(["", "Execution steps", "---------------"])
    lines.extend(f"- {item}" for item in dry_run.execution_steps)
    lines.extend(["", "Stop conditions", "---------------"])
    lines.extend(f"- {item}" for item in dry_run.stop_conditions)
    lines.extend(["", f"allowed_next_script:{dry_run.allowed_next_script or ''}", f"forbidden_actions:{','.join(dry_run.forbidden_actions)}", f"reason:{dry_run.reason}"])
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path