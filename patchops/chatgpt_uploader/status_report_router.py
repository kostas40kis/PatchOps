from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse

PATCH_NAME = "u3_c32_core_router_matrix"

ACTION_POST_STATUS_MESSAGE = "post_status_message"
ACTION_UPLOAD_OPERATOR_REPORT = "upload_operator_report"
ACTION_RECORD_PASS_LOCALLY_NO_UPLOAD = "record_pass_locally_no_upload"

PASS_UPLOADER_STATUS_ROUTER_MATRIX_VALIDATED = "PASS_UPLOADER_STATUS_ROUTER_MATRIX_VALIDATED"
BLOCKED_UPLOADER_STATUS_ROUTER_PATCH_NAME_REQUIRED = "BLOCKED_UPLOADER_STATUS_ROUTER_PATCH_NAME_REQUIRED"
BLOCKED_UPLOADER_STATUS_ROUTER_RESULT_UNSUPPORTED = "BLOCKED_UPLOADER_STATUS_ROUTER_RESULT_UNSUPPORTED"
BLOCKED_UPLOADER_STATUS_ROUTER_REPORT_REQUIRED = "BLOCKED_UPLOADER_STATUS_ROUTER_REPORT_REQUIRED"
BLOCKED_UPLOADER_STATUS_ROUTER_REPORT_HASH_MISMATCH = "BLOCKED_UPLOADER_STATUS_ROUTER_REPORT_HASH_MISMATCH"
BLOCKED_UPLOADER_STATUS_ROUTER_BROWSER_UNSUPPORTED = "BLOCKED_UPLOADER_STATUS_ROUTER_BROWSER_UNSUPPORTED"
BLOCKED_UPLOADER_STATUS_ROUTER_STATUS_TARGET_INVALID = "BLOCKED_UPLOADER_STATUS_ROUTER_STATUS_TARGET_INVALID"

DEFAULT_INPUT_PATH = Path("data/runtime/copilot_handoff/latest_uploader_status_router_input.json")
DEFAULT_POLICY_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_uploader_status_report_policy.json")
DEFAULT_TXT_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_uploader_status_report_policy.txt")

PASS_RESULTS = frozenset({"PASS", "PASSED", "SUCCESS", "OK"})
FAIL_RESULTS = frozenset({"FAIL", "FAILED", "ERROR", "BLOCKED", "BLOCK", "ABORTED"})
ALLOWED_BROWSER_LANES = frozenset({"chrome", "edge"})
REJECTED_BROWSER_LANES = frozenset({"any", "auto", "all", "default", "firefox", "brave", "opera", "vivaldi", "chromium", "safari"})


@dataclass(frozen=True)
class StatusReportRouterSafety:
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
class StatusReportRouterDecision:
    ok: bool
    result_label: str
    patch_name: str | None
    patch_result: str | None
    normalized_patch_result: str | None
    selected_action: str | None
    browser_lane: str | None
    status_chat_configured: bool
    status_chat_url_hash_or_redacted: str | None
    operator_report_path: str | None
    operator_report_sha256: str | None
    pass_status_message: str | None
    required_next_gate: str
    source_input_path: str | None
    issues: tuple[str, ...]
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
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    safety: StatusReportRouterSafety = field(default_factory=StatusReportRouterSafety)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["safety"] = asdict(self.safety)
        payload["policy"] = {
            "patch_name": self.patch_name,
            "patch_result": self.patch_result,
            "selected_action": self.selected_action,
            "browser_lane": self.browser_lane,
            "status_chat_configured": self.status_chat_configured,
            "status_chat_url_hash_or_redacted": self.status_chat_url_hash_or_redacted,
            "operator_report_path": self.operator_report_path,
            "operator_report_sha256": self.operator_report_sha256,
            "pass_status_message": self.pass_status_message,
            "required_next_gate": self.required_next_gate,
        }
        return payload


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def normalize_bool(value: Any, *, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on", "enabled", "configured"}:
        return True
    if text in {"0", "false", "no", "n", "off", "disabled", "none"}:
        return False
    return default


def normalize_patch_result(value: Any) -> str | None:
    text = normalize_optional_text(value)
    return text.upper() if text else None


def normalize_browser_lane(value: Any) -> str | None:
    text = normalize_optional_text(value)
    return text.lower() if text else None


def expected_pass_status_message(patch_name: str) -> str:
    return f"{patch_name} has passed"


def load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return payload


def redact_status_url(value: str | None) -> str | None:
    if not value:
        return None
    parsed = urlparse(value)
    if not parsed.scheme or not parsed.netloc:
        return f"sha256:{sha256_text(value)}"
    host = parsed.netloc.lower()
    if parsed.path.startswith("/c/"):
        path_display = "/c/<redacted>"
    elif parsed.path:
        first = parsed.path.strip("/").split("/")[0]
        path_display = f"/{first}/<redacted>"
    else:
        path_display = "/<redacted>"
    return f"{parsed.scheme}://{host}{path_display}#sha256:{sha256_text(value)}"


def get_nested_mapping(payload: Mapping[str, Any], *keys: str) -> Mapping[str, Any] | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, Mapping):
            return value
    return None


def coalesce_mapping_value(payload: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in payload and payload[key] is not None:
            return payload[key]
    return None


def flatten_router_input(payload: Mapping[str, Any]) -> dict[str, Any]:
    status_chat = get_nested_mapping(payload, "status_chat", "status_target", "target", "chat") or {}
    policy = get_nested_mapping(payload, "policy", "router_input", "decision", "status_policy", "uploader_status_router_input") or {}
    merged: dict[str, Any] = {}
    for source in (payload, policy):
        for key, value in source.items():
            if isinstance(value, Mapping):
                continue
            merged[key] = value
    if status_chat:
        merged["status_chat_configured"] = coalesce_mapping_value(status_chat, "enabled", "configured", "status_chat_configured")
        merged["status_chat_url"] = coalesce_mapping_value(status_chat, "target_url", "status_chat_url", "url")
        merged["status_chat_url_hash_or_redacted"] = coalesce_mapping_value(status_chat, "target_url_sha256", "status_chat_url_hash_or_redacted", "url_hash")
        merged["browser_lane"] = coalesce_mapping_value(status_chat, "browser_lane", "lane") or merged.get("browser_lane")
    return merged


def make_decision(
    *,
    ok: bool,
    result_label: str,
    patch_name: str | None,
    patch_result: str | None,
    normalized_patch_result: str | None,
    selected_action: str | None,
    browser_lane: str | None,
    status_chat_configured: bool,
    status_chat_url_hash_or_redacted: str | None,
    operator_report_path: str | None,
    operator_report_sha256: str | None,
    pass_status_message: str | None,
    required_next_gate: str,
    source_input_path: Path | None,
    issues: Sequence[str],
) -> StatusReportRouterDecision:
    safety = StatusReportRouterSafety()
    return StatusReportRouterDecision(
        ok=ok,
        result_label=result_label,
        patch_name=patch_name,
        patch_result=patch_result,
        normalized_patch_result=normalized_patch_result,
        selected_action=selected_action,
        browser_lane=browser_lane,
        status_chat_configured=status_chat_configured,
        status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
        operator_report_path=operator_report_path,
        operator_report_sha256=operator_report_sha256,
        pass_status_message=pass_status_message,
        required_next_gate=required_next_gate,
        source_input_path=str(source_input_path) if source_input_path else None,
        issues=tuple(issues),
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
        safety=safety,
    )


def route_status_report_payload(payload: Mapping[str, Any], *, source_input_path: Path | None = None) -> StatusReportRouterDecision:
    flat = flatten_router_input(payload)
    patch_name = normalize_optional_text(coalesce_mapping_value(flat, "patch_name", "name"))
    patch_result_raw = normalize_optional_text(coalesce_mapping_value(flat, "patch_result", "result", "final_result"))
    normalized_result = normalize_patch_result(patch_result_raw)
    status_chat_configured = normalize_bool(coalesce_mapping_value(flat, "status_chat_configured", "status_chat_enabled"), default=False)
    status_chat_url = normalize_optional_text(coalesce_mapping_value(flat, "status_chat_url", "target_url"))
    status_chat_hash = normalize_optional_text(coalesce_mapping_value(flat, "status_chat_url_hash_or_redacted", "target_url_sha256", "status_chat_url_sha256"))
    browser_lane = normalize_browser_lane(coalesce_mapping_value(flat, "browser_lane", "lane"))
    operator_report_path_text = normalize_optional_text(coalesce_mapping_value(flat, "operator_report_path", "report_path"))
    expected_operator_report_sha256 = normalize_optional_text(coalesce_mapping_value(flat, "operator_report_sha256", "report_sha256"))

    if not patch_name:
        return make_decision(
            ok=False,
            result_label=BLOCKED_UPLOADER_STATUS_ROUTER_PATCH_NAME_REQUIRED,
            patch_name=None,
            patch_result=patch_result_raw,
            normalized_patch_result=normalized_result,
            selected_action=None,
            browser_lane=browser_lane,
            status_chat_configured=status_chat_configured,
            status_chat_url_hash_or_redacted=status_chat_hash or redact_status_url(status_chat_url),
            operator_report_path=operator_report_path_text,
            operator_report_sha256=expected_operator_report_sha256,
            pass_status_message=None,
            required_next_gate="none",
            source_input_path=source_input_path,
            issues=("patch_name is required",),
        )

    if normalized_result not in PASS_RESULTS and normalized_result not in FAIL_RESULTS:
        return make_decision(
            ok=False,
            result_label=BLOCKED_UPLOADER_STATUS_ROUTER_RESULT_UNSUPPORTED,
            patch_name=patch_name,
            patch_result=patch_result_raw,
            normalized_patch_result=normalized_result,
            selected_action=None,
            browser_lane=browser_lane,
            status_chat_configured=status_chat_configured,
            status_chat_url_hash_or_redacted=status_chat_hash or redact_status_url(status_chat_url),
            operator_report_path=operator_report_path_text,
            operator_report_sha256=expected_operator_report_sha256,
            pass_status_message=None,
            required_next_gate="none",
            source_input_path=source_input_path,
            issues=("patch_result must be PASS, FAIL, or BLOCKED family",),
        )

    if status_chat_configured and browser_lane not in ALLOWED_BROWSER_LANES:
        issue = f"browser_lane must be one of {sorted(ALLOWED_BROWSER_LANES)} when status chat is configured"
        if browser_lane in REJECTED_BROWSER_LANES:
            issue = f"rejected browser_lane: {browser_lane}"
        return make_decision(
            ok=False,
            result_label=BLOCKED_UPLOADER_STATUS_ROUTER_BROWSER_UNSUPPORTED,
            patch_name=patch_name,
            patch_result=patch_result_raw,
            normalized_patch_result=normalized_result,
            selected_action=None,
            browser_lane=browser_lane,
            status_chat_configured=status_chat_configured,
            status_chat_url_hash_or_redacted=status_chat_hash or redact_status_url(status_chat_url),
            operator_report_path=operator_report_path_text,
            operator_report_sha256=expected_operator_report_sha256,
            pass_status_message=None,
            required_next_gate="none",
            source_input_path=source_input_path,
            issues=(issue,),
        )

    status_chat_url_hash_or_redacted = status_chat_hash or redact_status_url(status_chat_url)
    if status_chat_configured and not status_chat_url_hash_or_redacted:
        return make_decision(
            ok=False,
            result_label=BLOCKED_UPLOADER_STATUS_ROUTER_STATUS_TARGET_INVALID,
            patch_name=patch_name,
            patch_result=patch_result_raw,
            normalized_patch_result=normalized_result,
            selected_action=None,
            browser_lane=browser_lane,
            status_chat_configured=status_chat_configured,
            status_chat_url_hash_or_redacted=None,
            operator_report_path=operator_report_path_text,
            operator_report_sha256=expected_operator_report_sha256,
            pass_status_message=None,
            required_next_gate="none",
            source_input_path=source_input_path,
            issues=("status chat is configured but no target URL or hash was supplied",),
        )

    if normalized_result in PASS_RESULTS:
        if status_chat_configured:
            return make_decision(
                ok=True,
                result_label=PASS_UPLOADER_STATUS_ROUTER_MATRIX_VALIDATED,
                patch_name=patch_name,
                patch_result=patch_result_raw,
                normalized_patch_result=normalized_result,
                selected_action=ACTION_POST_STATUS_MESSAGE,
                browser_lane=browser_lane,
                status_chat_configured=True,
                status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
                operator_report_path=None,
                operator_report_sha256=None,
                pass_status_message=expected_pass_status_message(patch_name),
                required_next_gate=f"{browser_lane}_status_message_send_gate",
                source_input_path=source_input_path,
                issues=(),
            )
        return make_decision(
            ok=True,
            result_label=PASS_UPLOADER_STATUS_ROUTER_MATRIX_VALIDATED,
            patch_name=patch_name,
            patch_result=patch_result_raw,
            normalized_patch_result=normalized_result,
            selected_action=ACTION_RECORD_PASS_LOCALLY_NO_UPLOAD,
            browser_lane=browser_lane,
            status_chat_configured=False,
            status_chat_url_hash_or_redacted=None,
            operator_report_path=None,
            operator_report_sha256=None,
            pass_status_message=expected_pass_status_message(patch_name),
            required_next_gate="none",
            source_input_path=source_input_path,
            issues=(),
        )

    if not operator_report_path_text:
        return make_decision(
            ok=False,
            result_label=BLOCKED_UPLOADER_STATUS_ROUTER_REPORT_REQUIRED,
            patch_name=patch_name,
            patch_result=patch_result_raw,
            normalized_patch_result=normalized_result,
            selected_action=ACTION_UPLOAD_OPERATOR_REPORT,
            browser_lane=browser_lane,
            status_chat_configured=status_chat_configured,
            status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
            operator_report_path=None,
            operator_report_sha256=expected_operator_report_sha256,
            pass_status_message=None,
            required_next_gate="none",
            source_input_path=source_input_path,
            issues=("operator_report_path is required for FAIL/BLOCKED results",),
        )

    report_path = Path(operator_report_path_text)
    if not report_path.exists() or not report_path.is_file():
        return make_decision(
            ok=False,
            result_label=BLOCKED_UPLOADER_STATUS_ROUTER_REPORT_REQUIRED,
            patch_name=patch_name,
            patch_result=patch_result_raw,
            normalized_patch_result=normalized_result,
            selected_action=ACTION_UPLOAD_OPERATOR_REPORT,
            browser_lane=browser_lane,
            status_chat_configured=status_chat_configured,
            status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
            operator_report_path=operator_report_path_text,
            operator_report_sha256=expected_operator_report_sha256,
            pass_status_message=None,
            required_next_gate="none",
            source_input_path=source_input_path,
            issues=(f"operator report file not found: {operator_report_path_text}",),
        )

    actual_report_sha256 = sha256_file(report_path)
    if expected_operator_report_sha256 and expected_operator_report_sha256 != actual_report_sha256:
        return make_decision(
            ok=False,
            result_label=BLOCKED_UPLOADER_STATUS_ROUTER_REPORT_HASH_MISMATCH,
            patch_name=patch_name,
            patch_result=patch_result_raw,
            normalized_patch_result=normalized_result,
            selected_action=ACTION_UPLOAD_OPERATOR_REPORT,
            browser_lane=browser_lane,
            status_chat_configured=status_chat_configured,
            status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
            operator_report_path=str(report_path),
            operator_report_sha256=actual_report_sha256,
            pass_status_message=None,
            required_next_gate="none",
            source_input_path=source_input_path,
            issues=("operator_report_sha256 did not match operator_report_path",),
        )

    lane_for_upload = browser_lane if status_chat_configured else (browser_lane or "chrome")
    if lane_for_upload not in ALLOWED_BROWSER_LANES:
        return make_decision(
            ok=False,
            result_label=BLOCKED_UPLOADER_STATUS_ROUTER_BROWSER_UNSUPPORTED,
            patch_name=patch_name,
            patch_result=patch_result_raw,
            normalized_patch_result=normalized_result,
            selected_action=ACTION_UPLOAD_OPERATOR_REPORT,
            browser_lane=lane_for_upload,
            status_chat_configured=status_chat_configured,
            status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
            operator_report_path=str(report_path),
            operator_report_sha256=actual_report_sha256,
            pass_status_message=None,
            required_next_gate="none",
            source_input_path=source_input_path,
            issues=("upload browser_lane must be chrome or edge",),
        )

    return make_decision(
        ok=True,
        result_label=PASS_UPLOADER_STATUS_ROUTER_MATRIX_VALIDATED,
        patch_name=patch_name,
        patch_result=patch_result_raw,
        normalized_patch_result=normalized_result,
        selected_action=ACTION_UPLOAD_OPERATOR_REPORT,
        browser_lane=lane_for_upload,
        status_chat_configured=status_chat_configured,
        status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
        operator_report_path=str(report_path),
        operator_report_sha256=actual_report_sha256,
        pass_status_message=None,
        required_next_gate=f"{lane_for_upload}_operator_report_upload_gate",
        source_input_path=source_input_path,
        issues=(),
    )


def route_status_report_path(input_path: Path) -> StatusReportRouterDecision:
    return route_status_report_payload(load_json_object(input_path), source_input_path=input_path)


def render_text(decision: StatusReportRouterDecision) -> str:
    lines = [
        f"result_label: {decision.result_label}",
        f"ok: {str(decision.ok).lower()}",
        f"patch_name: {decision.patch_name}",
        f"patch_result: {decision.patch_result}",
        f"normalized_patch_result: {decision.normalized_patch_result}",
        f"selected_action: {decision.selected_action}",
        f"browser_lane: {decision.browser_lane}",
        f"status_chat_configured: {str(decision.status_chat_configured).lower()}",
        f"status_chat_url_hash_or_redacted: {decision.status_chat_url_hash_or_redacted}",
        f"operator_report_path: {decision.operator_report_path}",
        f"operator_report_sha256: {decision.operator_report_sha256}",
        f"pass_status_message: {decision.pass_status_message}",
        f"required_next_gate: {decision.required_next_gate}",
        f"source_input_path: {decision.source_input_path}",
        f"browser_action_performed: {str(decision.browser_action_performed).lower()}",
        f"chatgpt_submit_performed: {str(decision.chatgpt_submit_performed).lower()}",
        f"operator_report_uploaded: {str(decision.operator_report_uploaded).lower()}",
        f"status_message_posted: {str(decision.status_message_posted).lower()}",
        f"send_button_pressed: {str(decision.send_button_pressed).lower()}",
        f"raw_conversation_text_available: {str(decision.raw_conversation_text_available).lower()}",
        f"selenium_used: {str(decision.selenium_used).lower()}",
        f"webdriver_used: {str(decision.webdriver_used).lower()}",
        f"browser_dom_automation_used: {str(decision.browser_dom_automation_used).lower()}",
        f"cloudflare_bypass_attempted: {str(decision.cloudflare_bypass_attempted).lower()}",
        f"captcha_bypass_attempted: {str(decision.captcha_bypass_attempted).lower()}",
        f"created_at: {decision.created_at}",
    ]
    if decision.issues:
        lines.append("issues:")
        for issue in decision.issues:
            lines.append(f"- {issue}")
    else:
        lines.append("issues: none")
    return "\n".join(lines) + "\n"


def write_router_evidence(
    decision: StatusReportRouterDecision,
    *,
    policy_output_path: Path = DEFAULT_POLICY_OUTPUT_PATH,
    txt_output_path: Path = DEFAULT_TXT_OUTPUT_PATH,
) -> tuple[Path, Path]:
    policy_output_path.parent.mkdir(parents=True, exist_ok=True)
    txt_output_path.parent.mkdir(parents=True, exist_ok=True)
    policy_output_path.write_text(json.dumps(decision.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    txt_output_path.write_text(render_text(decision), encoding="utf-8")
    return policy_output_path, txt_output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PatchOps uploader status-report core router matrix")
    parser.add_argument("--input-path", default=None)
    parser.add_argument("--patch-name", default=None)
    parser.add_argument("--patch-result", default=None)
    parser.add_argument("--operator-report-path", default=None)
    parser.add_argument("--operator-report-sha256", default=None)
    parser.add_argument("--status-chat-configured", action="store_true")
    parser.add_argument("--status-chat-url", default=None)
    parser.add_argument("--status-chat-url-hash-or-redacted", default=None)
    parser.add_argument("--browser-lane", default=None)
    parser.add_argument("--policy-output-path", default=str(DEFAULT_POLICY_OUTPUT_PATH))
    parser.add_argument("--txt-output-path", default=str(DEFAULT_TXT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    input_path_text = normalize_optional_text(args.input_path)
    if input_path_text:
        decision = route_status_report_path(Path(input_path_text))
    else:
        payload = {
            "patch_name": args.patch_name,
            "patch_result": args.patch_result,
            "operator_report_path": args.operator_report_path,
            "operator_report_sha256": args.operator_report_sha256,
            "status_chat_configured": bool(args.status_chat_configured),
            "status_chat_url": args.status_chat_url,
            "status_chat_url_hash_or_redacted": args.status_chat_url_hash_or_redacted,
            "browser_lane": args.browser_lane,
        }
        decision = route_status_report_payload(payload, source_input_path=None)

    if not args.no_write_evidence:
        write_router_evidence(decision, policy_output_path=Path(args.policy_output_path), txt_output_path=Path(args.txt_output_path))

    if args.json:
        print(
            json.dumps(
                decision.to_dict(),
                sort_keys=True,
                separators=(",", ":") if args.compact else None,
                indent=None if args.compact else 2,
            )
        )
    else:
        print(render_text(decision), end="")

    return 0 if decision.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())