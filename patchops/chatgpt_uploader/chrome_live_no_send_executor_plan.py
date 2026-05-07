from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_VALIDATED = "PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_VALIDATED"
PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_WRITTEN = "PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_WRITTEN"
BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_CONTRACT_MISSING = "BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_CONTRACT_MISSING"
BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_CONTRACT_INVALID_JSON = "BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_CONTRACT_INVALID_JSON"
BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_UNSUPPORTED_KIND = "BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_UNSUPPORTED_KIND"
BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_CONTRACT_NOT_READY = "BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_CONTRACT_NOT_READY"
BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_UNSAFE = "BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_UNSAFE"

EXPECTED_BROWSER = "chrome"
EXPECTED_CONTRACT_KIND = "chrome_uploader_live_no_send_preflight_contract"
EXPECTED_CONTRACT_RESULT = "PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_VALIDATED"
PLAN_SCHEMA_VERSION = "1"
PLAN_KIND = "chrome_uploader_live_no_send_executor_plan"
DEFAULT_CONTRACT_RELATIVE_PATH = "data/runtime/copilot_handoff/latest_uploader_live_no_send_preflight_contract.json"
DEFAULT_PLAN_RELATIVE_PATH = "data/runtime/copilot_handoff/latest_uploader_live_no_send_executor_plan.json"
DEFAULT_MARKER_RELATIVE_PATH = "data/runtime/copilot_handoff/latest_uploader_live_no_send_executor_plan.txt"
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
    "packet_performs_browser_action",
    "packet_performs_chatgpt_submit",
    "packet_reads_conversation_text",
    "executor_plan_performs_browser_action",
    "executor_plan_performs_chatgpt_submit",
    "executor_plan_reads_conversation_text",
    "send_allowed",
}
REQUIRED_TRUE_FIELDS = {
    "preflight_contract_ready",
    "no_send_verified",
    "attachment_verified",
    "safe_for_downstream_planning",
    "human_must_confirm_visible_chrome",
    "human_must_verify_no_send",
}
REQUIRED_FALSE_FIELDS = {
    "packet_performs_browser_action",
    "packet_performs_chatgpt_submit",
    "packet_reads_conversation_text",
    "browser_action_performed",
    "chatgpt_submit_performed",
    "send_allowed",
    "raw_conversation_text_available",
}

EXECUTION_STEPS = [
    "confirm_visible_existing_chrome_window",
    "confirm_correct_target_conversation_already_open",
    "confirm_no_cloudflare_or_captcha_or_unexpected_modal",
    "future_executor_focus_existing_chrome_window",
    "future_executor_open_file_picker",
    "future_executor_type_canonical_path_into_picker",
    "future_executor_press_enter_in_picker",
    "future_executor_verify_attachment_chip_no_send",
    "future_executor_stop_before_send",
]
DEFAULT_REQUIRED_VISIBLE_STATE = [
    "visible_existing_chrome_window",
    "correct_target_conversation_already_open",
    "file_picker_not_open_initially",
    "send_button_not_focused",
    "no_cloudflare_or_captcha",
    "no_unexpected_modal",
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
class ChromeLiveNoSendExecutorPlan:
    ok: bool
    result: str
    schema_version: str
    plan_kind: str
    expected_browser: str
    source_contract_basename: str | None
    source_contract_sha256: str | None
    source_packet_basename: str | None
    source_boundary_basename: str | None
    source_ready_basename: str | None
    source_consumed_basename: str | None
    source_handoff_basename: str | None
    source_acceptance_basename: str | None
    contract_kind: str | None
    contract_result: str | None
    packet_kind: str | None
    packet_result: str | None
    boundary_kind: str | None
    boundary_result: str | None
    executor_plan_ready: bool
    no_send_verified: bool
    attachment_verified: bool
    safe_for_downstream_planning: bool
    human_supervision_required: bool
    human_must_confirm_visible_chrome: bool
    human_must_verify_no_send: bool
    executor_plan_performs_browser_action: bool
    executor_plan_performs_chatgpt_submit: bool
    executor_plan_reads_conversation_text: bool
    browser_action_performed: bool
    chatgpt_submit_performed: bool
    send_allowed: bool
    raw_conversation_text_available: bool
    required_visible_state: list[str]
    execution_steps: list[str]
    executor_stop_conditions: list[str]
    forbidden_actions: list[str]
    allowed_next_script: str | None
    forbidden_true_flags: list[str]
    plan_created_utc: str | None
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


def _plan(
    *,
    ok: bool,
    result: str,
    payload: Mapping[str, Any],
    source_contract_basename: str | None,
    source_contract_sha256: str | None,
    reason: str,
) -> ChromeLiveNoSendExecutorPlan:
    stop_conditions = _list(payload, "stop_conditions", DEFAULT_STOP_CONDITIONS)
    merged_stops = list(dict.fromkeys(stop_conditions + ["send_button_focus_or_submit_risk", "any_request_to_read_conversation_text", "any_request_to_press_send"]))
    return ChromeLiveNoSendExecutorPlan(
        ok=bool(ok),
        result=result,
        schema_version=PLAN_SCHEMA_VERSION,
        plan_kind=PLAN_KIND,
        expected_browser=EXPECTED_BROWSER,
        source_contract_basename=source_contract_basename,
        source_contract_sha256=source_contract_sha256,
        source_packet_basename=payload.get("source_packet_basename"),
        source_boundary_basename=payload.get("source_boundary_basename"),
        source_ready_basename=payload.get("source_ready_basename"),
        source_consumed_basename=payload.get("source_consumed_basename"),
        source_handoff_basename=payload.get("source_handoff_basename"),
        source_acceptance_basename=payload.get("source_acceptance_basename"),
        contract_kind=payload.get("contract_kind"),
        contract_result=payload.get("result"),
        packet_kind=payload.get("packet_kind"),
        packet_result=payload.get("packet_result"),
        boundary_kind=payload.get("boundary_kind"),
        boundary_result=payload.get("boundary_result"),
        executor_plan_ready=bool(ok),
        no_send_verified=bool(payload.get("no_send_verified", False)),
        attachment_verified=bool(payload.get("attachment_verified", False)),
        safe_for_downstream_planning=bool(payload.get("safe_for_downstream_planning", False)),
        human_supervision_required=True,
        human_must_confirm_visible_chrome=bool(payload.get("human_must_confirm_visible_chrome", True)),
        human_must_verify_no_send=bool(payload.get("human_must_verify_no_send", True)),
        executor_plan_performs_browser_action=False,
        executor_plan_performs_chatgpt_submit=False,
        executor_plan_reads_conversation_text=False,
        browser_action_performed=False,
        chatgpt_submit_performed=False,
        send_allowed=False,
        raw_conversation_text_available=False,
        required_visible_state=_list(payload, "required_visible_state", DEFAULT_REQUIRED_VISIBLE_STATE) if ok else [],
        execution_steps=list(EXECUTION_STEPS) if ok else [],
        executor_stop_conditions=merged_stops,
        forbidden_actions=_list(payload, "forbidden_actions", DEFAULT_FORBIDDEN_ACTIONS),
        allowed_next_script=payload.get("allowed_next_script") if ok else None,
        forbidden_true_flags=forbidden_flags(payload),
        plan_created_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat() if ok else None,
        reason=reason,
    )


def validate_preflight_contract_payload(
    payload: Mapping[str, Any],
    *,
    source_contract_basename: str | None = None,
    source_contract_sha256: str | None = None,
) -> ChromeLiveNoSendExecutorPlan:
    contract_kind = payload.get("contract_kind")
    contract_result = payload.get("result")
    forbidden = forbidden_flags(payload)
    missing_true = sorted(key for key in REQUIRED_TRUE_FIELDS if not bool(payload.get(key, False)))
    false_violations = sorted(key for key in REQUIRED_FALSE_FIELDS if bool(payload.get(key, False)))

    if contract_kind != EXPECTED_CONTRACT_KIND:
        return _plan(
            ok=False,
            result=BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_UNSUPPORTED_KIND,
            payload=payload,
            source_contract_basename=source_contract_basename,
            source_contract_sha256=source_contract_sha256,
            reason="Preflight contract kind is not chrome_uploader_live_no_send_preflight_contract.",
        )
    if forbidden:
        return _plan(
            ok=False,
            result=BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_UNSAFE,
            payload=payload,
            source_contract_basename=source_contract_basename,
            source_contract_sha256=source_contract_sha256,
            reason="Preflight contract contains forbidden true safety flags.",
        )
    if (
        not bool(payload.get("ok", False))
        or contract_result != EXPECTED_CONTRACT_RESULT
        or payload.get("expected_browser") != EXPECTED_BROWSER
        or not bool(payload.get("preflight_contract_ready", False))
        or missing_true
        or false_violations
    ):
        reason = "Preflight contract is not ready for executor-plan generation."
        if missing_true:
            reason += " Missing true fields: " + ",".join(missing_true)
        if false_violations:
            reason += " False-field violations: " + ",".join(false_violations)
        return _plan(
            ok=False,
            result=BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_CONTRACT_NOT_READY,
            payload=payload,
            source_contract_basename=source_contract_basename,
            source_contract_sha256=source_contract_sha256,
            reason=reason,
        )

    return _plan(
        ok=True,
        result=PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_VALIDATED,
        payload=payload,
        source_contract_basename=source_contract_basename,
        source_contract_sha256=source_contract_sha256,
        reason="Chrome live no-send executor plan generated from validated preflight contract; no browser action was performed.",
    )


def load_and_validate_preflight_contract(path: Path | str) -> ChromeLiveNoSendExecutorPlan:
    contract_path = Path(path).expanduser().resolve()
    if not contract_path.exists():
        return ChromeLiveNoSendExecutorPlan(
            ok=False,
            result=BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_CONTRACT_MISSING,
            schema_version=PLAN_SCHEMA_VERSION,
            plan_kind=PLAN_KIND,
            expected_browser=EXPECTED_BROWSER,
            source_contract_basename=contract_path.name,
            source_contract_sha256=None,
            source_packet_basename=None,
            source_boundary_basename=None,
            source_ready_basename=None,
            source_consumed_basename=None,
            source_handoff_basename=None,
            source_acceptance_basename=None,
            contract_kind=None,
            contract_result=None,
            packet_kind=None,
            packet_result=None,
            boundary_kind=None,
            boundary_result=None,
            executor_plan_ready=False,
            no_send_verified=False,
            attachment_verified=False,
            safe_for_downstream_planning=False,
            human_supervision_required=True,
            human_must_confirm_visible_chrome=True,
            human_must_verify_no_send=True,
            executor_plan_performs_browser_action=False,
            executor_plan_performs_chatgpt_submit=False,
            executor_plan_reads_conversation_text=False,
            browser_action_performed=False,
            chatgpt_submit_performed=False,
            send_allowed=False,
            raw_conversation_text_available=False,
            required_visible_state=[],
            execution_steps=[],
            executor_stop_conditions=["preflight_contract_missing"],
            forbidden_actions=list(DEFAULT_FORBIDDEN_ACTIONS),
            allowed_next_script=None,
            forbidden_true_flags=[],
            plan_created_utc=None,
            reason="Preflight contract JSON file is missing.",
        )
    try:
        payload = json.loads(contract_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return ChromeLiveNoSendExecutorPlan(
            ok=False,
            result=BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_CONTRACT_INVALID_JSON,
            schema_version=PLAN_SCHEMA_VERSION,
            plan_kind=PLAN_KIND,
            expected_browser=EXPECTED_BROWSER,
            source_contract_basename=contract_path.name,
            source_contract_sha256=sha256_file(contract_path),
            source_packet_basename=None,
            source_boundary_basename=None,
            source_ready_basename=None,
            source_consumed_basename=None,
            source_handoff_basename=None,
            source_acceptance_basename=None,
            contract_kind=None,
            contract_result=None,
            packet_kind=None,
            packet_result=None,
            boundary_kind=None,
            boundary_result=None,
            executor_plan_ready=False,
            no_send_verified=False,
            attachment_verified=False,
            safe_for_downstream_planning=False,
            human_supervision_required=True,
            human_must_confirm_visible_chrome=True,
            human_must_verify_no_send=True,
            executor_plan_performs_browser_action=False,
            executor_plan_performs_chatgpt_submit=False,
            executor_plan_reads_conversation_text=False,
            browser_action_performed=False,
            chatgpt_submit_performed=False,
            send_allowed=False,
            raw_conversation_text_available=False,
            required_visible_state=[],
            execution_steps=[],
            executor_stop_conditions=["preflight_contract_invalid_json"],
            forbidden_actions=list(DEFAULT_FORBIDDEN_ACTIONS),
            allowed_next_script=None,
            forbidden_true_flags=[],
            plan_created_utc=None,
            reason=f"Preflight contract JSON is invalid: {exc}",
        )
    if not isinstance(payload, dict):
        payload = {}
    return validate_preflight_contract_payload(
        payload,
        source_contract_basename=contract_path.name,
        source_contract_sha256=sha256_file(contract_path),
    )


def write_executor_plan(plan: ChromeLiveNoSendExecutorPlan, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = plan.to_payload()
    payload["write_result"] = PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_WRITTEN if plan.ok else plan.result
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def write_executor_plan_marker(plan: ChromeLiveNoSendExecutorPlan, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "Chrome live no-send executor plan",
        "=================================",
        f"result:{plan.result}",
        f"ok:{str(plan.ok).lower()}",
        f"plan_kind:{plan.plan_kind}",
        f"expected_browser:{plan.expected_browser}",
        f"contract_kind:{plan.contract_kind or ''}",
        f"contract_result:{plan.contract_result or ''}",
        f"executor_plan_ready:{str(plan.executor_plan_ready).lower()}",
        f"no_send_verified:{str(plan.no_send_verified).lower()}",
        f"attachment_verified:{str(plan.attachment_verified).lower()}",
        f"safe_for_downstream_planning:{str(plan.safe_for_downstream_planning).lower()}",
        "executor_plan_performs_browser_action:false",
        "executor_plan_performs_chatgpt_submit:false",
        "executor_plan_reads_conversation_text:false",
        "browser_action_performed:false",
        "chatgpt_submit_performed:false",
        "send_allowed:false",
        "raw_conversation_text_available:false",
        f"human_supervision_required:{str(plan.human_supervision_required).lower()}",
        f"human_must_confirm_visible_chrome:{str(plan.human_must_confirm_visible_chrome).lower()}",
        f"human_must_verify_no_send:{str(plan.human_must_verify_no_send).lower()}",
        "selenium_used:false",
        "webdriver_used:false",
        "browser_dom_automation_used:false",
        "cloudflare_bypass_attempted:false",
        "captcha_bypass_attempted:false",
        "conversation_text_logged:false",
        "raw_conversation_text_logged:false",
        "random_page_click_performed:false",
        "",
        "Execution steps",
        "---------------",
    ]
    lines.extend(f"- {item}" for item in plan.execution_steps)
    lines.extend(["", "Executor stop conditions", "------------------------"])
    lines.extend(f"- {item}" for item in plan.executor_stop_conditions)
    lines.extend(["", f"allowed_next_script:{plan.allowed_next_script or ''}", f"forbidden_actions:{','.join(plan.forbidden_actions)}", f"reason:{plan.reason}"])
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path