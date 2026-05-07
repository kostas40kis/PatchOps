from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

PASS_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_CONTRACT_VALIDATED = "PASS_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_CONTRACT_VALIDATED"
PASS_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_CONTRACT_WRITTEN = "PASS_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_CONTRACT_WRITTEN"
BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_DRY_RUN_MISSING = "BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_DRY_RUN_MISSING"
BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_DRY_RUN_INVALID_JSON = "BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_DRY_RUN_INVALID_JSON"
BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_UNSUPPORTED_KIND = "BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_UNSUPPORTED_KIND"
BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_DRY_RUN_NOT_READY = "BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_DRY_RUN_NOT_READY"
BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_UNSAFE = "BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_UNSAFE"

EXPECTED_BROWSER = "chrome"
EXPECTED_DRY_RUN_KIND = "chrome_uploader_live_no_send_executor_dry_run"
EXPECTED_DRY_RUN_RESULT = "PASS_CHROME_LIVE_NO_SEND_EXECUTOR_DRY_RUN_VALIDATED"
CONTRACT_SCHEMA_VERSION = "1"
CONTRACT_KIND = "chrome_uploader_live_no_send_executor_manual_probe_contract"
CONFIRMATION_TEXT = "PATCHOPS_CONFIRM_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE"
DEFAULT_DRY_RUN_RELATIVE_PATH = "data/runtime/copilot_handoff/latest_uploader_live_no_send_executor_dry_run.json"
DEFAULT_CONTRACT_RELATIVE_PATH = "data/runtime/copilot_handoff/latest_uploader_live_no_send_executor_manual_probe_contract.json"
DEFAULT_MARKER_RELATIVE_PATH = "data/runtime/copilot_handoff/latest_uploader_live_no_send_executor_manual_probe_contract.txt"
DEFAULT_ALLOWED_NEXT_SCRIPT = "scripts/run_uploader_chrome_live_no_send_executor.py"
FUTURE_EXECUTOR_COMMAND_TEMPLATE = (
    "python scripts/run_uploader_chrome_live_no_send_executor.py "
    "--contract-json data/runtime/copilot_handoff/latest_uploader_live_no_send_executor_manual_probe_contract.json "
    "--live-browser "
    "--confirm-live-browser-text PATCHOPS_CONFIRM_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE "
    "--stop-before-send"
)

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
    "dry_run_performs_browser_action",
    "dry_run_performs_chatgpt_submit",
    "dry_run_reads_conversation_text",
    "executor_dry_run_performed_live_action",
    "manual_probe_contract_performs_browser_action",
    "manual_probe_contract_performs_chatgpt_submit",
    "manual_probe_contract_reads_conversation_text",
    "manual_probe_contract_performed_live_action",
    "send_allowed",
}
REQUIRED_TRUE_FIELDS = {
    "dry_run_ready",
    "executor_plan_ready",
    "no_send_verified",
    "attachment_verified",
    "safe_for_downstream_planning",
    "human_supervision_required",
    "human_must_confirm_visible_chrome",
    "human_must_verify_no_send",
}
REQUIRED_FALSE_FIELDS = {
    "dry_run_performs_browser_action",
    "dry_run_performs_chatgpt_submit",
    "dry_run_reads_conversation_text",
    "executor_dry_run_performed_live_action",
    "browser_action_performed",
    "chatgpt_submit_performed",
    "send_allowed",
    "raw_conversation_text_available",
}

EXTRA_MANUAL_CHECKLIST = [
    "operator_confirms_chatgpt_composer_visible",
    "operator_confirms_attachment_area_visible_or_known",
    "operator_confirms_no_send_intent",
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
class ChromeLiveNoSendExecutorManualProbeContract:
    ok: bool
    result: str
    schema_version: str
    contract_kind: str
    expected_browser: str
    source_dry_run_basename: str | None
    source_dry_run_sha256: str | None
    source_plan_basename: str | None
    source_contract_basename: str | None
    source_packet_basename: str | None
    source_boundary_basename: str | None
    source_ready_basename: str | None
    source_consumed_basename: str | None
    source_handoff_basename: str | None
    source_acceptance_basename: str | None
    dry_run_kind: str | None
    dry_run_result: str | None
    plan_kind: str | None
    plan_result: str | None
    manual_probe_contract_ready: bool
    dry_run_ready: bool
    executor_plan_ready: bool
    no_send_verified: bool
    attachment_verified: bool
    safe_for_downstream_planning: bool
    human_supervision_required: bool
    human_must_confirm_visible_chrome: bool
    human_must_verify_no_send: bool
    explicit_confirmation_required: bool
    confirmation_text: str
    manual_probe_contract_performs_browser_action: bool
    manual_probe_contract_performs_chatgpt_submit: bool
    manual_probe_contract_reads_conversation_text: bool
    manual_probe_contract_performed_live_action: bool
    browser_action_performed: bool
    chatgpt_submit_performed: bool
    send_allowed: bool
    raw_conversation_text_available: bool
    human_visible_preflight_checklist: list[str]
    future_executor_command_template: str | None
    allowed_next_script: str | None
    stop_conditions: list[str]
    forbidden_actions: list[str]
    forbidden_true_flags: list[str]
    contract_created_utc: str | None
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


def _build_checklist(payload: Mapping[str, Any], ok: bool) -> list[str]:
    if not ok:
        return []
    base = _list(payload, "dry_run_checklist", [])
    return list(dict.fromkeys(base + EXTRA_MANUAL_CHECKLIST))


def _contract(
    *,
    ok: bool,
    result: str,
    payload: Mapping[str, Any],
    source_dry_run_basename: str | None,
    source_dry_run_sha256: str | None,
    reason: str,
) -> ChromeLiveNoSendExecutorManualProbeContract:
    stop_conditions = _list(payload, "stop_conditions", DEFAULT_STOP_CONDITIONS)
    merged_stops = list(dict.fromkeys(stop_conditions + ["any_request_to_read_conversation_text", "any_request_to_press_send"]))
    return ChromeLiveNoSendExecutorManualProbeContract(
        ok=bool(ok),
        result=result,
        schema_version=CONTRACT_SCHEMA_VERSION,
        contract_kind=CONTRACT_KIND,
        expected_browser=EXPECTED_BROWSER,
        source_dry_run_basename=source_dry_run_basename,
        source_dry_run_sha256=source_dry_run_sha256,
        source_plan_basename=payload.get("source_plan_basename"),
        source_contract_basename=payload.get("source_contract_basename"),
        source_packet_basename=payload.get("source_packet_basename"),
        source_boundary_basename=payload.get("source_boundary_basename"),
        source_ready_basename=payload.get("source_ready_basename"),
        source_consumed_basename=payload.get("source_consumed_basename"),
        source_handoff_basename=payload.get("source_handoff_basename"),
        source_acceptance_basename=payload.get("source_acceptance_basename"),
        dry_run_kind=payload.get("dry_run_kind"),
        dry_run_result=payload.get("result"),
        plan_kind=payload.get("plan_kind"),
        plan_result=payload.get("plan_result"),
        manual_probe_contract_ready=bool(ok),
        dry_run_ready=bool(payload.get("dry_run_ready", False)),
        executor_plan_ready=bool(payload.get("executor_plan_ready", False)),
        no_send_verified=bool(payload.get("no_send_verified", False)),
        attachment_verified=bool(payload.get("attachment_verified", False)),
        safe_for_downstream_planning=bool(payload.get("safe_for_downstream_planning", False)),
        human_supervision_required=bool(payload.get("human_supervision_required", True)),
        human_must_confirm_visible_chrome=bool(payload.get("human_must_confirm_visible_chrome", True)),
        human_must_verify_no_send=bool(payload.get("human_must_verify_no_send", True)),
        explicit_confirmation_required=True,
        confirmation_text=CONFIRMATION_TEXT,
        manual_probe_contract_performs_browser_action=False,
        manual_probe_contract_performs_chatgpt_submit=False,
        manual_probe_contract_reads_conversation_text=False,
        manual_probe_contract_performed_live_action=False,
        browser_action_performed=False,
        chatgpt_submit_performed=False,
        send_allowed=False,
        raw_conversation_text_available=False,
        human_visible_preflight_checklist=_build_checklist(payload, ok),
        future_executor_command_template=FUTURE_EXECUTOR_COMMAND_TEMPLATE if ok else None,
        allowed_next_script=payload.get("allowed_next_script") if ok else None,
        stop_conditions=merged_stops,
        forbidden_actions=_list(payload, "forbidden_actions", DEFAULT_FORBIDDEN_ACTIONS),
        forbidden_true_flags=forbidden_flags(payload),
        contract_created_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat() if ok else None,
        reason=reason,
    )


def validate_executor_dry_run_payload(
    payload: Mapping[str, Any],
    *,
    source_dry_run_basename: str | None = None,
    source_dry_run_sha256: str | None = None,
) -> ChromeLiveNoSendExecutorManualProbeContract:
    dry_run_kind = payload.get("dry_run_kind")
    dry_run_result = payload.get("result")
    forbidden = forbidden_flags(payload)
    missing_true = sorted(key for key in REQUIRED_TRUE_FIELDS if not bool(payload.get(key, False)))
    false_violations = sorted(key for key in REQUIRED_FALSE_FIELDS if bool(payload.get(key, False)))

    if dry_run_kind != EXPECTED_DRY_RUN_KIND:
        return _contract(
            ok=False,
            result=BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_UNSUPPORTED_KIND,
            payload=payload,
            source_dry_run_basename=source_dry_run_basename,
            source_dry_run_sha256=source_dry_run_sha256,
            reason="Executor dry-run kind is not chrome_uploader_live_no_send_executor_dry_run.",
        )
    if forbidden:
        return _contract(
            ok=False,
            result=BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_UNSAFE,
            payload=payload,
            source_dry_run_basename=source_dry_run_basename,
            source_dry_run_sha256=source_dry_run_sha256,
            reason="Executor dry-run contains forbidden true safety flags.",
        )
    if (
        not bool(payload.get("ok", False))
        or dry_run_result != EXPECTED_DRY_RUN_RESULT
        or payload.get("expected_browser") != EXPECTED_BROWSER
        or payload.get("allowed_next_script") != DEFAULT_ALLOWED_NEXT_SCRIPT
        or missing_true
        or false_violations
    ):
        reason = "Executor dry-run is not ready for manual-probe contract generation."
        if missing_true:
            reason += " Missing true fields: " + ",".join(missing_true)
        if false_violations:
            reason += " False-field violations: " + ",".join(false_violations)
        if payload.get("allowed_next_script") != DEFAULT_ALLOWED_NEXT_SCRIPT:
            reason += " allowed_next_script must be scripts/run_uploader_chrome_live_no_send_executor.py."
        return _contract(
            ok=False,
            result=BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_DRY_RUN_NOT_READY,
            payload=payload,
            source_dry_run_basename=source_dry_run_basename,
            source_dry_run_sha256=source_dry_run_sha256,
            reason=reason,
        )

    return _contract(
        ok=True,
        result=PASS_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_CONTRACT_VALIDATED,
        payload=payload,
        source_dry_run_basename=source_dry_run_basename,
        source_dry_run_sha256=source_dry_run_sha256,
        reason="Chrome live no-send manual-probe contract generated from validated executor dry-run; no browser action was performed.",
    )


def load_and_validate_executor_dry_run(path: Path | str) -> ChromeLiveNoSendExecutorManualProbeContract:
    dry_run_path = Path(path).expanduser().resolve()
    if not dry_run_path.exists():
        return ChromeLiveNoSendExecutorManualProbeContract(
            ok=False,
            result=BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_DRY_RUN_MISSING,
            schema_version=CONTRACT_SCHEMA_VERSION,
            contract_kind=CONTRACT_KIND,
            expected_browser=EXPECTED_BROWSER,
            source_dry_run_basename=dry_run_path.name,
            source_dry_run_sha256=None,
            source_plan_basename=None,
            source_contract_basename=None,
            source_packet_basename=None,
            source_boundary_basename=None,
            source_ready_basename=None,
            source_consumed_basename=None,
            source_handoff_basename=None,
            source_acceptance_basename=None,
            dry_run_kind=None,
            dry_run_result=None,
            plan_kind=None,
            plan_result=None,
            manual_probe_contract_ready=False,
            dry_run_ready=False,
            executor_plan_ready=False,
            no_send_verified=False,
            attachment_verified=False,
            safe_for_downstream_planning=False,
            human_supervision_required=True,
            human_must_confirm_visible_chrome=True,
            human_must_verify_no_send=True,
            explicit_confirmation_required=True,
            confirmation_text=CONFIRMATION_TEXT,
            manual_probe_contract_performs_browser_action=False,
            manual_probe_contract_performs_chatgpt_submit=False,
            manual_probe_contract_reads_conversation_text=False,
            manual_probe_contract_performed_live_action=False,
            browser_action_performed=False,
            chatgpt_submit_performed=False,
            send_allowed=False,
            raw_conversation_text_available=False,
            human_visible_preflight_checklist=[],
            future_executor_command_template=None,
            allowed_next_script=None,
            stop_conditions=["executor_dry_run_missing"],
            forbidden_actions=list(DEFAULT_FORBIDDEN_ACTIONS),
            forbidden_true_flags=[],
            contract_created_utc=None,
            reason="Executor dry-run JSON file is missing.",
        )
    try:
        payload = json.loads(dry_run_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return ChromeLiveNoSendExecutorManualProbeContract(
            ok=False,
            result=BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_DRY_RUN_INVALID_JSON,
            schema_version=CONTRACT_SCHEMA_VERSION,
            contract_kind=CONTRACT_KIND,
            expected_browser=EXPECTED_BROWSER,
            source_dry_run_basename=dry_run_path.name,
            source_dry_run_sha256=sha256_file(dry_run_path),
            source_plan_basename=None,
            source_contract_basename=None,
            source_packet_basename=None,
            source_boundary_basename=None,
            source_ready_basename=None,
            source_consumed_basename=None,
            source_handoff_basename=None,
            source_acceptance_basename=None,
            dry_run_kind=None,
            dry_run_result=None,
            plan_kind=None,
            plan_result=None,
            manual_probe_contract_ready=False,
            dry_run_ready=False,
            executor_plan_ready=False,
            no_send_verified=False,
            attachment_verified=False,
            safe_for_downstream_planning=False,
            human_supervision_required=True,
            human_must_confirm_visible_chrome=True,
            human_must_verify_no_send=True,
            explicit_confirmation_required=True,
            confirmation_text=CONFIRMATION_TEXT,
            manual_probe_contract_performs_browser_action=False,
            manual_probe_contract_performs_chatgpt_submit=False,
            manual_probe_contract_reads_conversation_text=False,
            manual_probe_contract_performed_live_action=False,
            browser_action_performed=False,
            chatgpt_submit_performed=False,
            send_allowed=False,
            raw_conversation_text_available=False,
            human_visible_preflight_checklist=[],
            future_executor_command_template=None,
            allowed_next_script=None,
            stop_conditions=["executor_dry_run_invalid_json"],
            forbidden_actions=list(DEFAULT_FORBIDDEN_ACTIONS),
            forbidden_true_flags=[],
            contract_created_utc=None,
            reason=f"Executor dry-run JSON is invalid: {exc}",
        )
    if not isinstance(payload, dict):
        payload = {}
    return validate_executor_dry_run_payload(
        payload,
        source_dry_run_basename=dry_run_path.name,
        source_dry_run_sha256=sha256_file(dry_run_path),
    )


def write_manual_probe_contract(contract: ChromeLiveNoSendExecutorManualProbeContract, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = contract.to_payload()
    payload["write_result"] = PASS_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_CONTRACT_WRITTEN if contract.ok else contract.result
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def write_manual_probe_contract_marker(contract: ChromeLiveNoSendExecutorManualProbeContract, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "Chrome live no-send executor manual-probe contract",
        "=================================================",
        f"result:{contract.result}",
        f"ok:{str(contract.ok).lower()}",
        f"contract_kind:{contract.contract_kind}",
        f"expected_browser:{contract.expected_browser}",
        f"dry_run_kind:{contract.dry_run_kind or ''}",
        f"dry_run_result:{contract.dry_run_result or ''}",
        f"manual_probe_contract_ready:{str(contract.manual_probe_contract_ready).lower()}",
        f"dry_run_ready:{str(contract.dry_run_ready).lower()}",
        f"executor_plan_ready:{str(contract.executor_plan_ready).lower()}",
        f"no_send_verified:{str(contract.no_send_verified).lower()}",
        f"attachment_verified:{str(contract.attachment_verified).lower()}",
        f"safe_for_downstream_planning:{str(contract.safe_for_downstream_planning).lower()}",
        f"explicit_confirmation_required:{str(contract.explicit_confirmation_required).lower()}",
        f"confirmation_text:{contract.confirmation_text}",
        "manual_probe_contract_performs_browser_action:false",
        "manual_probe_contract_performs_chatgpt_submit:false",
        "manual_probe_contract_reads_conversation_text:false",
        "manual_probe_contract_performed_live_action:false",
        "browser_action_performed:false",
        "chatgpt_submit_performed:false",
        "send_allowed:false",
        "raw_conversation_text_available:false",
        "selenium_used:false",
        "webdriver_used:false",
        "browser_dom_automation_used:false",
        "cloudflare_bypass_attempted:false",
        "captcha_bypass_attempted:false",
        "conversation_text_logged:false",
        "raw_conversation_text_logged:false",
        "random_page_click_performed:false",
        "",
        "Human-visible preflight checklist",
        "---------------------------------",
    ]
    lines.extend(f"- {item}" for item in contract.human_visible_preflight_checklist)
    lines.extend(["", "Future executor command template", "--------------------------------"])
    lines.append(contract.future_executor_command_template or "")
    lines.extend(["", "Stop conditions", "---------------"])
    lines.extend(f"- {item}" for item in contract.stop_conditions)
    lines.extend(["", f"allowed_next_script:{contract.allowed_next_script or ''}", f"forbidden_actions:{','.join(contract.forbidden_actions)}", f"reason:{contract.reason}"])
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path