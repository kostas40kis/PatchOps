from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse

PATCH_NAME = "u3_c27_uploader_status_reporter_armed_gate"

DEFAULT_POLICY_PATH = Path("data/runtime/copilot_handoff/latest_uploader_status_report_policy.json")
DEFAULT_JSON_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_uploader_status_reporter_armed_gate.json")
DEFAULT_TXT_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_uploader_status_reporter_armed_gate.txt")

ACTION_POST_STATUS_MESSAGE = "post_status_message"
ACTION_UPLOAD_OPERATOR_REPORT = "upload_operator_report"
ACTION_RECORD_PASS_LOCALLY_NO_UPLOAD = "record_pass_locally_no_upload"

ALLOWED_SELECTED_ACTIONS = frozenset(
    {
        ACTION_POST_STATUS_MESSAGE,
        ACTION_UPLOAD_OPERATOR_REPORT,
        ACTION_RECORD_PASS_LOCALLY_NO_UPLOAD,
    }
)
ALLOWED_BROWSER_LANES = frozenset({"chrome", "edge"})

CONFIRM_POST_STATUS_MESSAGE = "PATCHOPS_CONFIRM_UPLOADER_STATUS_POST_MESSAGE"
CONFIRM_UPLOAD_OPERATOR_REPORT = "PATCHOPS_CONFIRM_UPLOADER_STATUS_UPLOAD_REPORT"

PASS_UPLOADER_STATUS_REPORTER_ARMED_GATE_VALIDATED = "PASS_UPLOADER_STATUS_REPORTER_ARMED_GATE_VALIDATED"
BLOCKED_UPLOADER_STATUS_REPORTER_CONFIRMATION_REQUIRED = "BLOCKED_UPLOADER_STATUS_REPORTER_CONFIRMATION_REQUIRED"
BLOCKED_UPLOADER_STATUS_REPORTER_CONFIRMATION_MISMATCH = "BLOCKED_UPLOADER_STATUS_REPORTER_CONFIRMATION_MISMATCH"
BLOCKED_UPLOADER_STATUS_REPORTER_UNSUPPORTED_BROWSER_LANE = "BLOCKED_UPLOADER_STATUS_REPORTER_UNSUPPORTED_BROWSER_LANE"

CONTROLLED_RESULT_LABELS = frozenset(
    {
        PASS_UPLOADER_STATUS_REPORTER_ARMED_GATE_VALIDATED,
        BLOCKED_UPLOADER_STATUS_REPORTER_CONFIRMATION_REQUIRED,
        BLOCKED_UPLOADER_STATUS_REPORTER_CONFIRMATION_MISMATCH,
        BLOCKED_UPLOADER_STATUS_REPORTER_UNSUPPORTED_BROWSER_LANE,
    }
)

REQUIRED_GATE_BY_ACTION = {
    ACTION_POST_STATUS_MESSAGE: CONFIRM_POST_STATUS_MESSAGE,
    ACTION_UPLOAD_OPERATOR_REPORT: CONFIRM_UPLOAD_OPERATOR_REPORT,
    ACTION_RECORD_PASS_LOCALLY_NO_UPLOAD: None,
}

NESTED_POLICY_KEYS = (
    "policy",
    "decision",
    "delivery_policy",
    "status_policy",
    "status_report_policy",
    "uploader_status_report_policy",
    "status_report_decision",
)


@dataclass(frozen=True)
class StatusReporterArmedGateSafety:
    browser_action_performed: bool = False
    chatgpt_submit_performed: bool = False
    operator_report_uploaded: bool = False
    status_message_posted: bool = False
    send_button_pressed: bool = False
    file_upload_attempted: bool = False
    raw_conversation_text_available: bool = False
    selenium_used: bool = False
    webdriver_used: bool = False
    browser_dom_automation_used: bool = False
    cloudflare_bypass_attempted: bool = False
    captcha_bypass_attempted: bool = False
    conversation_text_logged: bool = False
    random_page_click_performed: bool = False


@dataclass(frozen=True)
class StatusReporterArmedGate:
    ok: bool
    result_label: str
    patch_name: str | None
    patch_result: str | None
    selected_action: str | None
    browser_lane: str | None
    status_chat_configured: bool
    status_chat_url_hash_or_redacted: str | None
    operator_report_path: str | None
    operator_report_sha256: str | None
    pass_status_message: str | None
    required_next_gate: str | None
    confirmation_required: bool
    confirmation_text_supplied: str | None
    confirmation_matched: bool
    browser_action_performed: bool
    chatgpt_submit_performed: bool
    operator_report_uploaded: bool
    status_message_posted: bool
    send_button_pressed: bool
    raw_conversation_text_available: bool
    selenium_used: bool
    webdriver_used: bool
    browser_dom_automation_used: bool
    cloudflare_bypass_attempted: bool
    captcha_bypass_attempted: bool
    issues: tuple[str, ...] = ()
    policy_path: str | None = None
    policy_sha256: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    safety: StatusReporterArmedGateSafety = field(default_factory=StatusReporterArmedGateSafety)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["safety"] = asdict(self.safety)
        return payload


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return payload


def normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def normalize_selected_action(value: Any) -> str | None:
    text = normalize_optional_text(value)
    return text.lower() if text else None


def normalize_browser_lane(value: Any) -> str | None:
    text = normalize_optional_text(value)
    return text.lower() if text else None


def normalize_bool(value: Any, *, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on", "configured", "enabled"}:
        return True
    if text in {"0", "false", "no", "n", "off", "none", "missing", "disabled"}:
        return False
    return default


def lookup(policy: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in policy:
            return policy[key]

    for nested_key in NESTED_POLICY_KEYS:
        nested = policy.get(nested_key)
        if isinstance(nested, Mapping):
            for key in keys:
                if key in nested:
                    return nested[key]

    return None


def redact_or_hash_status_url(policy: Mapping[str, Any]) -> str | None:
    provided = lookup(
        policy,
        "status_chat_url_hash_or_redacted",
        "target_url_sha256",
        "status_chat_url_sha256",
        "status_chat_url_hash",
    )
    provided_text = normalize_optional_text(provided)
    if provided_text:
        return provided_text

    raw_url = lookup(policy, "status_chat_url", "target_url")
    raw_text = normalize_optional_text(raw_url)
    if not raw_text:
        return None

    parsed = urlparse(raw_text)
    host = parsed.netloc or "(no-host)"
    return f"{host}#sha256:{sha256_text(raw_text)}"


def resolve_operator_report_sha256(policy: Mapping[str, Any], operator_report_path: str | None) -> str | None:
    provided = normalize_optional_text(lookup(policy, "operator_report_sha256", "report_sha256"))
    if provided:
        return provided

    if not operator_report_path:
        return None

    candidate = Path(operator_report_path)
    if candidate.exists() and candidate.is_file():
        return sha256_file(candidate)
    return None


def default_pass_status_message(patch_name: str | None) -> str | None:
    if not patch_name:
        return None
    return f"{patch_name} has passed"


def blocked_gate(
    *,
    result_label: str,
    issues: list[str],
    patch_name: str | None,
    patch_result: str | None,
    selected_action: str | None,
    browser_lane: str | None,
    status_chat_configured: bool,
    status_chat_url_hash_or_redacted: str | None,
    operator_report_path: str | None,
    operator_report_sha256: str | None,
    pass_status_message: str | None,
    required_next_gate: str | None,
    confirmation_required: bool,
    confirmation_text_supplied: str | None,
    confirmation_matched: bool,
    policy_path: Path | None,
    policy_sha256: str | None,
) -> StatusReporterArmedGate:
    safety = StatusReporterArmedGateSafety()
    return StatusReporterArmedGate(
        ok=False,
        result_label=result_label,
        patch_name=patch_name,
        patch_result=patch_result,
        selected_action=selected_action,
        browser_lane=browser_lane,
        status_chat_configured=status_chat_configured,
        status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
        operator_report_path=operator_report_path,
        operator_report_sha256=operator_report_sha256,
        pass_status_message=pass_status_message,
        required_next_gate=required_next_gate,
        confirmation_required=confirmation_required,
        confirmation_text_supplied=confirmation_text_supplied,
        confirmation_matched=confirmation_matched,
        browser_action_performed=safety.browser_action_performed,
        chatgpt_submit_performed=safety.chatgpt_submit_performed,
        operator_report_uploaded=safety.operator_report_uploaded,
        status_message_posted=safety.status_message_posted,
        send_button_pressed=safety.send_button_pressed,
        raw_conversation_text_available=safety.raw_conversation_text_available,
        selenium_used=safety.selenium_used,
        webdriver_used=safety.webdriver_used,
        browser_dom_automation_used=safety.browser_dom_automation_used,
        cloudflare_bypass_attempted=safety.cloudflare_bypass_attempted,
        captcha_bypass_attempted=safety.captcha_bypass_attempted,
        issues=tuple(issues),
        policy_path=str(policy_path) if policy_path else None,
        policy_sha256=policy_sha256,
        safety=safety,
    )


def build_status_reporter_armed_gate(
    policy: Mapping[str, Any],
    *,
    confirmation_text: str | None = None,
    policy_path: Path | None = None,
) -> StatusReporterArmedGate:
    issues: list[str] = []
    safety = StatusReporterArmedGateSafety()

    patch_name = normalize_optional_text(lookup(policy, "patch_name", "name"))
    patch_result = normalize_optional_text(lookup(policy, "patch_result", "result"))
    selected_action = normalize_selected_action(lookup(policy, "selected_action", "action"))
    browser_lane = normalize_browser_lane(lookup(policy, "browser_lane", "browser"))
    status_chat_configured = normalize_bool(
        lookup(policy, "status_chat_configured", "status_chat_enabled", "target_configured"),
        default=False,
    )
    operator_report_path = normalize_optional_text(lookup(policy, "operator_report_path", "report_path"))
    operator_report_sha256 = resolve_operator_report_sha256(policy, operator_report_path)
    status_chat_url_hash_or_redacted = redact_or_hash_status_url(policy)
    policy_sha256 = sha256_file(policy_path) if policy_path and policy_path.exists() else None

    supplied_confirmation = normalize_optional_text(confirmation_text)
    if supplied_confirmation is None:
        supplied_confirmation = normalize_optional_text(
            lookup(policy, "confirmation_text_supplied", "confirmation_text", "confirm_text")
        )

    if selected_action not in ALLOWED_SELECTED_ACTIONS:
        issues.append(f"unsupported selected_action: {selected_action!r}")
        return blocked_gate(
            result_label=BLOCKED_UPLOADER_STATUS_REPORTER_CONFIRMATION_MISMATCH,
            issues=issues,
            patch_name=patch_name,
            patch_result=patch_result,
            selected_action=selected_action,
            browser_lane=browser_lane,
            status_chat_configured=status_chat_configured,
            status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
            operator_report_path=operator_report_path,
            operator_report_sha256=operator_report_sha256,
            pass_status_message=None,
            required_next_gate=None,
            confirmation_required=False,
            confirmation_text_supplied=supplied_confirmation,
            confirmation_matched=False,
            policy_path=policy_path,
            policy_sha256=policy_sha256,
        )

    required_gate = REQUIRED_GATE_BY_ACTION[selected_action]
    action_needs_browser_lane = selected_action in {ACTION_POST_STATUS_MESSAGE, ACTION_UPLOAD_OPERATOR_REPORT}
    if action_needs_browser_lane and browser_lane not in ALLOWED_BROWSER_LANES:
        issues.append(f"unsupported or missing browser_lane for {selected_action}: {browser_lane!r}")
        return blocked_gate(
            result_label=BLOCKED_UPLOADER_STATUS_REPORTER_UNSUPPORTED_BROWSER_LANE,
            issues=issues,
            patch_name=patch_name,
            patch_result=patch_result,
            selected_action=selected_action,
            browser_lane=browser_lane,
            status_chat_configured=status_chat_configured,
            status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
            operator_report_path=operator_report_path,
            operator_report_sha256=operator_report_sha256,
            pass_status_message=default_pass_status_message(patch_name) if selected_action == ACTION_POST_STATUS_MESSAGE else None,
            required_next_gate=required_gate,
            confirmation_required=True,
            confirmation_text_supplied=supplied_confirmation,
            confirmation_matched=False,
            policy_path=policy_path,
            policy_sha256=policy_sha256,
        )

    if browser_lane is not None and browser_lane not in ALLOWED_BROWSER_LANES:
        issues.append(f"unsupported browser_lane: {browser_lane!r}")
        return blocked_gate(
            result_label=BLOCKED_UPLOADER_STATUS_REPORTER_UNSUPPORTED_BROWSER_LANE,
            issues=issues,
            patch_name=patch_name,
            patch_result=patch_result,
            selected_action=selected_action,
            browser_lane=browser_lane,
            status_chat_configured=status_chat_configured,
            status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
            operator_report_path=operator_report_path,
            operator_report_sha256=operator_report_sha256,
            pass_status_message=None,
            required_next_gate=None,
            confirmation_required=False,
            confirmation_text_supplied=supplied_confirmation,
            confirmation_matched=False,
            policy_path=policy_path,
            policy_sha256=policy_sha256,
        )

    confirmation_required = required_gate is not None
    confirmation_matched = (supplied_confirmation == required_gate) if confirmation_required else True

    if confirmation_required and not supplied_confirmation:
        issues.append(f"confirmation required: {required_gate}")
        result_label = BLOCKED_UPLOADER_STATUS_REPORTER_CONFIRMATION_REQUIRED
        ok = False
    elif confirmation_required and supplied_confirmation != required_gate:
        issues.append(f"confirmation mismatch: expected {required_gate}")
        result_label = BLOCKED_UPLOADER_STATUS_REPORTER_CONFIRMATION_MISMATCH
        ok = False
    else:
        result_label = PASS_UPLOADER_STATUS_REPORTER_ARMED_GATE_VALIDATED
        ok = True

    supplied_message = normalize_optional_text(lookup(policy, "pass_status_message", "status_message"))
    pass_status_message = (
        supplied_message or default_pass_status_message(patch_name)
        if selected_action == ACTION_POST_STATUS_MESSAGE
        else None
    )

    required_next_gate = required_gate if required_gate is not None else "none"

    return StatusReporterArmedGate(
        ok=ok,
        result_label=result_label,
        patch_name=patch_name,
        patch_result=patch_result,
        selected_action=selected_action,
        browser_lane=browser_lane,
        status_chat_configured=status_chat_configured,
        status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
        operator_report_path=operator_report_path,
        operator_report_sha256=operator_report_sha256,
        pass_status_message=pass_status_message,
        required_next_gate=required_next_gate,
        confirmation_required=confirmation_required,
        confirmation_text_supplied=supplied_confirmation,
        confirmation_matched=confirmation_matched,
        browser_action_performed=safety.browser_action_performed,
        chatgpt_submit_performed=safety.chatgpt_submit_performed,
        operator_report_uploaded=safety.operator_report_uploaded,
        status_message_posted=safety.status_message_posted,
        send_button_pressed=safety.send_button_pressed,
        raw_conversation_text_available=safety.raw_conversation_text_available,
        selenium_used=safety.selenium_used,
        webdriver_used=safety.webdriver_used,
        browser_dom_automation_used=safety.browser_dom_automation_used,
        cloudflare_bypass_attempted=safety.cloudflare_bypass_attempted,
        captcha_bypass_attempted=safety.captcha_bypass_attempted,
        issues=tuple(issues),
        policy_path=str(policy_path) if policy_path else None,
        policy_sha256=policy_sha256,
        safety=safety,
    )


def render_text(gate: StatusReporterArmedGate) -> str:
    lines = [
        f"patch_name: {gate.patch_name}",
        f"patch_result: {gate.patch_result}",
        f"result_label: {gate.result_label}",
        f"ok: {str(gate.ok).lower()}",
        f"selected_action: {gate.selected_action}",
        f"browser_lane: {gate.browser_lane}",
        f"status_chat_configured: {str(gate.status_chat_configured).lower()}",
        f"status_chat_url_hash_or_redacted: {gate.status_chat_url_hash_or_redacted}",
        f"operator_report_path: {gate.operator_report_path}",
        f"operator_report_sha256: {gate.operator_report_sha256}",
        f"pass_status_message: {gate.pass_status_message}",
        f"required_next_gate: {gate.required_next_gate}",
        f"confirmation_required: {str(gate.confirmation_required).lower()}",
        f"confirmation_text_supplied: {gate.confirmation_text_supplied}",
        f"confirmation_matched: {str(gate.confirmation_matched).lower()}",
        f"browser_action_performed: {str(gate.browser_action_performed).lower()}",
        f"chatgpt_submit_performed: {str(gate.chatgpt_submit_performed).lower()}",
        f"operator_report_uploaded: {str(gate.operator_report_uploaded).lower()}",
        f"status_message_posted: {str(gate.status_message_posted).lower()}",
        f"send_button_pressed: {str(gate.send_button_pressed).lower()}",
        f"raw_conversation_text_available: {str(gate.raw_conversation_text_available).lower()}",
        f"selenium_used: {str(gate.selenium_used).lower()}",
        f"webdriver_used: {str(gate.webdriver_used).lower()}",
        f"browser_dom_automation_used: {str(gate.browser_dom_automation_used).lower()}",
        f"cloudflare_bypass_attempted: {str(gate.cloudflare_bypass_attempted).lower()}",
        f"captcha_bypass_attempted: {str(gate.captcha_bypass_attempted).lower()}",
        f"policy_path: {gate.policy_path}",
        f"policy_sha256: {gate.policy_sha256}",
        f"created_at: {gate.created_at}",
    ]
    if gate.issues:
        lines.append("issues:")
        for issue in gate.issues:
            lines.append(f"- {issue}")
    else:
        lines.append("issues: none")
    return "\n".join(lines) + "\n"


def write_gate_evidence(
    gate: StatusReporterArmedGate,
    *,
    json_output_path: Path = DEFAULT_JSON_OUTPUT_PATH,
    txt_output_path: Path = DEFAULT_TXT_OUTPUT_PATH,
) -> tuple[Path, Path]:
    json_output_path.parent.mkdir(parents=True, exist_ok=True)
    txt_output_path.parent.mkdir(parents=True, exist_ok=True)
    json_output_path.write_text(json.dumps(gate.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    txt_output_path.write_text(render_text(gate), encoding="utf-8")
    return json_output_path, txt_output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PatchOps uploader status reporter armed gate")
    parser.add_argument("--policy-path", default=str(DEFAULT_POLICY_PATH))
    parser.add_argument("--json-output-path", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--txt-output-path", default=str(DEFAULT_TXT_OUTPUT_PATH))
    parser.add_argument("--confirm-uploader-status-text", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def run_from_paths(
    *,
    policy_path: Path,
    json_output_path: Path = DEFAULT_JSON_OUTPUT_PATH,
    txt_output_path: Path = DEFAULT_TXT_OUTPUT_PATH,
    confirmation_text: str | None = None,
    write_evidence: bool = True,
) -> StatusReporterArmedGate:
    policy = load_json_object(policy_path)
    gate = build_status_reporter_armed_gate(policy, confirmation_text=confirmation_text, policy_path=policy_path)
    if write_evidence:
        write_gate_evidence(gate, json_output_path=json_output_path, txt_output_path=txt_output_path)
    return gate


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    policy_path = Path(args.policy_path)
    json_output_path = Path(args.json_output_path)
    txt_output_path = Path(args.txt_output_path)

    try:
        gate = run_from_paths(
            policy_path=policy_path,
            json_output_path=json_output_path,
            txt_output_path=txt_output_path,
            confirmation_text=args.confirm_uploader_status_text,
            write_evidence=not args.no_write_evidence,
        )
    except Exception as exc:  # noqa: BLE001
        safety = StatusReporterArmedGateSafety()
        gate = StatusReporterArmedGate(
            ok=False,
            result_label=BLOCKED_UPLOADER_STATUS_REPORTER_CONFIRMATION_MISMATCH,
            patch_name=None,
            patch_result=None,
            selected_action=None,
            browser_lane=None,
            status_chat_configured=False,
            status_chat_url_hash_or_redacted=None,
            operator_report_path=None,
            operator_report_sha256=None,
            pass_status_message=None,
            required_next_gate=None,
            confirmation_required=False,
            confirmation_text_supplied=args.confirm_uploader_status_text,
            confirmation_matched=False,
            browser_action_performed=safety.browser_action_performed,
            chatgpt_submit_performed=safety.chatgpt_submit_performed,
            operator_report_uploaded=safety.operator_report_uploaded,
            status_message_posted=safety.status_message_posted,
            send_button_pressed=safety.send_button_pressed,
            raw_conversation_text_available=safety.raw_conversation_text_available,
            selenium_used=safety.selenium_used,
            webdriver_used=safety.webdriver_used,
            browser_dom_automation_used=safety.browser_dom_automation_used,
            cloudflare_bypass_attempted=safety.cloudflare_bypass_attempted,
            captcha_bypass_attempted=safety.captcha_bypass_attempted,
            issues=(str(exc),),
            policy_path=str(policy_path),
            policy_sha256=sha256_file(policy_path) if policy_path.exists() else None,
            safety=safety,
        )
        if not args.no_write_evidence:
            write_gate_evidence(gate, json_output_path=json_output_path, txt_output_path=txt_output_path)

    if args.json:
        print(
            json.dumps(
                gate.to_dict(),
                sort_keys=True,
                separators=(",", ":") if args.compact else None,
                indent=None if args.compact else 2,
            )
        )
    else:
        print(render_text(gate), end="")

    return 0 if gate.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())