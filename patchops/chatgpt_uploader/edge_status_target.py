from __future__ import annotations

import argparse
import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence
from urllib.parse import urlparse

PATCH_NAME = "u3_c33_edge_status_target_preflight"
CONFIRM_EDGE_STATUS_TARGET_PREFLIGHT = "PATCHOPS_CONFIRM_EDGE_STATUS_TARGET_PREFLIGHT"

PASS_EDGE_STATUS_TARGET_PREFLIGHT_READY = "PASS_EDGE_STATUS_TARGET_PREFLIGHT_READY"
BLOCKED_EDGE_STATUS_TARGET_CONFIG_MISSING = "BLOCKED_EDGE_STATUS_TARGET_CONFIG_MISSING"
BLOCKED_EDGE_STATUS_TARGET_BROWSER_MISMATCH = "BLOCKED_EDGE_STATUS_TARGET_BROWSER_MISMATCH"
BLOCKED_EDGE_STATUS_TARGET_URL_INVALID = "BLOCKED_EDGE_STATUS_TARGET_URL_INVALID"
BLOCKED_EDGE_STATUS_TARGET_CONFIRMATION_REQUIRED = "BLOCKED_EDGE_STATUS_TARGET_CONFIRMATION_REQUIRED"
BLOCKED_EDGE_STATUS_TARGET_CONFIRMATION_MISMATCH = "BLOCKED_EDGE_STATUS_TARGET_CONFIRMATION_MISMATCH"
BLOCKED_EDGE_STATUS_TARGET_NOT_READY = "BLOCKED_EDGE_STATUS_TARGET_NOT_READY"
BLOCKED_SEND_RISK = "BLOCKED_SEND_RISK"

DEFAULT_STATUS_TARGET_VALIDATION_PATH = Path("data/runtime/copilot_handoff/latest_uploader_status_target_config_validation.json")
DEFAULT_STATUS_TARGET_CONFIG_PATH = Path("data/config/uploader_status_target_config.json")
DEFAULT_JSON_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_edge_status_target_preflight.json")
DEFAULT_TXT_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_edge_status_target_preflight.txt")

CHATGPT_TITLE_TOKENS = ("chatgpt", "openai")
EDGE_TITLE_TOKENS = ("microsoft edge", "edge")
COMPOSER_NAME_TOKENS = ("message chatgpt", "message", "ask anything", "send a message", "prompt")


@dataclass(frozen=True)
class EdgeStatusTargetSafety:
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
class EdgeStatusTargetPreflightResult:
    ok: bool
    result_label: str
    patch_name: str
    browser_lane: str | None
    status_chat_configured: bool
    status_chat_url_hash_or_redacted: str | None
    target_url_sha256: str | None
    live_browser: bool
    confirmation_text_supplied: str | None
    confirmation_matched: bool
    edge_target_ready: bool
    edge_target_focused: bool
    composer_candidate_count: int
    target_window_count: int
    matching_target_count: int
    selected_target_title_hash: str | None
    selected_target_title_length: int | None
    provider: str
    required_next_gate: str
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
    safety: EdgeStatusTargetSafety = field(default_factory=EdgeStatusTargetSafety)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["safety"] = asdict(self.safety)
        return payload


@dataclass(frozen=True)
class EdgeTargetProbe:
    ready: bool
    focused: bool
    target_window_count: int
    matching_target_count: int
    selected_target_title: str | None
    composer_candidate_count: int
    issues: tuple[str, ...] = ()


class EdgeStatusTargetAdapter(Protocol):
    provider_name: str

    def focus_target(self) -> EdgeTargetProbe:
        ...


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


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
        path_display = f"/{parsed.path.strip('/').split('/')[0]}/<redacted>"
    else:
        path_display = "/<redacted>"
    return f"{parsed.scheme}://{host}{path_display}#sha256:{sha256_text(value)}"


def valid_chatgpt_url(value: str | None) -> bool:
    if not value:
        return False
    parsed = urlparse(value)
    if parsed.scheme != "https":
        return False
    if parsed.netloc.lower() not in {"chatgpt.com", "www.chatgpt.com"}:
        return False
    return parsed.path.startswith("/c/") and len(parsed.path.strip("/")) > 2


def extract_status_target(payload: Mapping[str, Any]) -> dict[str, Any]:
    status_chat_raw = payload.get("status_chat")
    policy_raw = payload.get("policy")
    status_chat = status_chat_raw if isinstance(status_chat_raw, Mapping) else {}
    policy = policy_raw if isinstance(policy_raw, Mapping) else {}

    lane = (
        normalize_optional_text(status_chat.get("browser_lane"))
        or normalize_optional_text(payload.get("browser_lane"))
        or normalize_optional_text(policy.get("browser_lane"))
    )
    target_url = (
        normalize_optional_text(status_chat.get("target_url"))
        or normalize_optional_text(payload.get("target_url"))
        or normalize_optional_text(payload.get("status_chat_url"))
        or normalize_optional_text(policy.get("status_chat_url"))
    )
    target_url_hash = (
        normalize_optional_text(status_chat.get("target_url_sha256"))
        or normalize_optional_text(payload.get("target_url_sha256"))
        or normalize_optional_text(payload.get("status_chat_url_hash_or_redacted"))
        or normalize_optional_text(policy.get("status_chat_url_hash_or_redacted"))
    )
    configured = normalize_bool(
        status_chat.get("enabled")
        if "enabled" in status_chat
        else payload.get("status_chat_configured", policy.get("status_chat_configured")),
        default=bool(target_url or target_url_hash),
    )
    result_ok = payload.get("ok")
    result_label = normalize_optional_text(payload.get("result_label"))
    return {
        "browser_lane": lane.lower() if lane else None,
        "target_url": target_url,
        "target_url_sha256": target_url_hash,
        "status_chat_configured": configured,
        "source_result_ok": result_ok,
        "source_result_label": result_label,
    }


class FakeEdgeStatusTargetAdapter:
    def __init__(self, mode: str = "ready") -> None:
        self.mode = mode
        self.provider_name = f"fake-{mode}"

    def focus_target(self) -> EdgeTargetProbe:
        if self.mode == "no-target":
            return EdgeTargetProbe(False, False, 0, 0, None, 0, ("no fake Edge ChatGPT target",))
        if self.mode == "ambiguous-target":
            return EdgeTargetProbe(False, False, 2, 2, None, 0, ("multiple fake Edge ChatGPT targets",))
        if self.mode == "no-composer":
            return EdgeTargetProbe(False, True, 1, 1, "ChatGPT - Microsoft Edge", 0, ("no fake composer candidate",))
        return EdgeTargetProbe(True, True, 1, 1, "ChatGPT - Microsoft Edge", 1, ())


class PywinautoEdgeStatusTargetAdapter:
    provider_name = "pywinauto"

    def __init__(self, *, settle_seconds: float = 0.4) -> None:
        self.settle_seconds = settle_seconds

    def _desktop(self) -> Any:
        try:
            from pywinauto import Desktop  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"pywinauto is required for live Edge preflight: {exc}") from exc
        return Desktop(backend="uia")

    def _looks_like_edge_chatgpt_window(self, window: Any) -> bool:
        title = _safe_window_title(window) or ""
        lowered = title.lower()
        return any(token in lowered for token in EDGE_TITLE_TOKENS) and any(token in lowered for token in CHATGPT_TITLE_TOKENS)

    def _find_composer_candidates(self, window: Any) -> list[Any]:
        candidates: list[Any] = []
        try:
            descendants = window.descendants()
        except Exception:
            return candidates
        for element in descendants:
            try:
                control_type = str(element.element_info.control_type or "").lower()
                name = str(element.window_text() or element.element_info.name or "").strip().lower()
                enabled = bool(element.is_enabled())
                visible = bool(element.is_visible())
            except Exception:
                continue
            if not enabled or not visible:
                continue
            if control_type not in {"edit", "document"}:
                continue
            if any(token in name for token in COMPOSER_NAME_TOKENS):
                candidates.append(element)
        return candidates

    def focus_target(self) -> EdgeTargetProbe:
        try:
            desktop = self._desktop()
            windows = list(desktop.windows())
        except Exception as exc:
            return EdgeTargetProbe(False, False, 0, 0, None, 0, (str(exc),))

        matches = [window for window in windows if self._looks_like_edge_chatgpt_window(window)]
        if not matches:
            return EdgeTargetProbe(False, False, len(windows), 0, None, 0, ("no visible Edge ChatGPT target window",))
        if len(matches) > 1:
            return EdgeTargetProbe(False, False, len(windows), len(matches), None, 0, ("multiple Edge ChatGPT target windows",))

        selected = matches[0]
        try:
            selected.set_focus()
            time.sleep(self.settle_seconds)
        except Exception as exc:
            return EdgeTargetProbe(False, False, len(windows), 1, _safe_window_title(selected), 0, (f"Edge focus failed: {exc}",))

        composer_candidates = self._find_composer_candidates(selected)
        if not composer_candidates:
            return EdgeTargetProbe(False, True, len(windows), 1, _safe_window_title(selected), 0, ("no safe ChatGPT composer candidate",))
        return EdgeTargetProbe(True, True, len(windows), 1, _safe_window_title(selected), len(composer_candidates), ())


def _safe_window_title(window: Any) -> str | None:
    try:
        title = str(window.window_text() or "")
        return title or None
    except Exception:
        return None


def build_adapter(provider: str) -> EdgeStatusTargetAdapter:
    if provider.startswith("fake-"):
        return FakeEdgeStatusTargetAdapter(provider.removeprefix("fake-"))
    if provider == "pywinauto":
        return PywinautoEdgeStatusTargetAdapter()
    raise ValueError(f"Unknown provider: {provider}")


def make_result(
    *,
    ok: bool,
    result_label: str,
    browser_lane: str | None,
    status_chat_configured: bool,
    status_chat_url_hash_or_redacted: str | None,
    target_url_sha256: str | None,
    live_browser: bool,
    confirmation_text_supplied: str | None,
    confirmation_matched: bool,
    edge_target_ready: bool,
    edge_target_focused: bool,
    composer_candidate_count: int,
    target_window_count: int,
    matching_target_count: int,
    selected_target_title: str | None,
    provider: str,
    required_next_gate: str,
    issues: Sequence[str],
) -> EdgeStatusTargetPreflightResult:
    safety = EdgeStatusTargetSafety(
        browser_action_performed=bool(edge_target_focused),
        chatgpt_submit_performed=False,
        operator_report_uploaded=False,
        status_message_posted=False,
        send_button_pressed=False,
        file_upload_attempted=False,
        raw_conversation_text_available=False,
        selenium_used=False,
        webdriver_used=False,
        browser_dom_automation_used=False,
        cloudflare_bypass_attempted=False,
        captcha_bypass_attempted=False,
        conversation_text_logged=False,
        random_page_click_performed=False,
    )
    return EdgeStatusTargetPreflightResult(
        ok=ok,
        result_label=result_label,
        patch_name=PATCH_NAME,
        browser_lane=browser_lane,
        status_chat_configured=status_chat_configured,
        status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
        target_url_sha256=target_url_sha256,
        live_browser=live_browser,
        confirmation_text_supplied=confirmation_text_supplied,
        confirmation_matched=confirmation_matched,
        edge_target_ready=edge_target_ready,
        edge_target_focused=edge_target_focused,
        composer_candidate_count=composer_candidate_count,
        target_window_count=target_window_count,
        matching_target_count=matching_target_count,
        selected_target_title_hash=sha256_text(selected_target_title) if selected_target_title else None,
        selected_target_title_length=len(selected_target_title) if selected_target_title else None,
        provider=provider,
        required_next_gate=required_next_gate,
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


def run_edge_status_target_preflight(
    *,
    status_target_payload: Mapping[str, Any] | None,
    live_browser: bool,
    confirmation_text: str | None,
    provider: str,
) -> EdgeStatusTargetPreflightResult:
    if status_target_payload is None:
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_STATUS_TARGET_CONFIG_MISSING,
            browser_lane=None,
            status_chat_configured=False,
            status_chat_url_hash_or_redacted=None,
            target_url_sha256=None,
            live_browser=live_browser,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=False,
            edge_target_ready=False,
            edge_target_focused=False,
            composer_candidate_count=0,
            target_window_count=0,
            matching_target_count=0,
            selected_target_title=None,
            provider=provider,
            required_next_gate="none",
            issues=("status target config/validation payload is required",),
        )

    target = extract_status_target(status_target_payload)
    browser_lane = target["browser_lane"]
    target_url = normalize_optional_text(target["target_url"])
    target_url_sha256 = target["target_url_sha256"] if target["target_url_sha256"] and str(target["target_url_sha256"]).startswith("sha256:") is False else None
    status_chat_url_hash_or_redacted = normalize_optional_text(target["target_url_sha256"]) or redact_status_url(target_url)
    status_chat_configured = bool(target["status_chat_configured"])

    if browser_lane != "edge":
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_STATUS_TARGET_BROWSER_MISMATCH,
            browser_lane=browser_lane,
            status_chat_configured=status_chat_configured,
            status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
            target_url_sha256=target_url_sha256,
            live_browser=live_browser,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=False,
            edge_target_ready=False,
            edge_target_focused=False,
            composer_candidate_count=0,
            target_window_count=0,
            matching_target_count=0,
            selected_target_title=None,
            provider=provider,
            required_next_gate="none",
            issues=("browser_lane must be edge for C33",),
        )

    if not status_chat_configured:
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_STATUS_TARGET_CONFIG_MISSING,
            browser_lane=browser_lane,
            status_chat_configured=False,
            status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
            target_url_sha256=target_url_sha256,
            live_browser=live_browser,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=False,
            edge_target_ready=False,
            edge_target_focused=False,
            composer_candidate_count=0,
            target_window_count=0,
            matching_target_count=0,
            selected_target_title=None,
            provider=provider,
            required_next_gate="none",
            issues=("status chat must be configured/enabled for Edge preflight",),
        )

    if target_url and not valid_chatgpt_url(target_url):
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_STATUS_TARGET_URL_INVALID,
            browser_lane=browser_lane,
            status_chat_configured=status_chat_configured,
            status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
            target_url_sha256=target_url_sha256,
            live_browser=live_browser,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=False,
            edge_target_ready=False,
            edge_target_focused=False,
            composer_candidate_count=0,
            target_window_count=0,
            matching_target_count=0,
            selected_target_title=None,
            provider=provider,
            required_next_gate="none",
            issues=("target_url must be an https://chatgpt.com/c/... URL",),
        )

    if not status_chat_url_hash_or_redacted:
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_STATUS_TARGET_URL_INVALID,
            browser_lane=browser_lane,
            status_chat_configured=status_chat_configured,
            status_chat_url_hash_or_redacted=None,
            target_url_sha256=target_url_sha256,
            live_browser=live_browser,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=False,
            edge_target_ready=False,
            edge_target_focused=False,
            composer_candidate_count=0,
            target_window_count=0,
            matching_target_count=0,
            selected_target_title=None,
            provider=provider,
            required_next_gate="none",
            issues=("target_url or target_url_sha256 is required",),
        )

    if not live_browser:
        return make_result(
            ok=False,
            result_label=BLOCKED_SEND_RISK,
            browser_lane=browser_lane,
            status_chat_configured=status_chat_configured,
            status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
            target_url_sha256=target_url_sha256,
            live_browser=False,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=False,
            edge_target_ready=False,
            edge_target_focused=False,
            composer_candidate_count=0,
            target_window_count=0,
            matching_target_count=0,
            selected_target_title=None,
            provider=provider,
            required_next_gate="edge_status_message_send_gate",
            issues=("--live-browser is required for Edge status target preflight",),
        )

    if confirmation_text is None:
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_STATUS_TARGET_CONFIRMATION_REQUIRED,
            browser_lane=browser_lane,
            status_chat_configured=status_chat_configured,
            status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
            target_url_sha256=target_url_sha256,
            live_browser=True,
            confirmation_text_supplied=None,
            confirmation_matched=False,
            edge_target_ready=False,
            edge_target_focused=False,
            composer_candidate_count=0,
            target_window_count=0,
            matching_target_count=0,
            selected_target_title=None,
            provider=provider,
            required_next_gate="edge_status_message_send_gate",
            issues=("confirmation is required",),
        )

    confirmation_matched = confirmation_text == CONFIRM_EDGE_STATUS_TARGET_PREFLIGHT
    if not confirmation_matched:
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_STATUS_TARGET_CONFIRMATION_MISMATCH,
            browser_lane=browser_lane,
            status_chat_configured=status_chat_configured,
            status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
            target_url_sha256=target_url_sha256,
            live_browser=True,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=False,
            edge_target_ready=False,
            edge_target_focused=False,
            composer_candidate_count=0,
            target_window_count=0,
            matching_target_count=0,
            selected_target_title=None,
            provider=provider,
            required_next_gate="edge_status_message_send_gate",
            issues=(f"confirmation must exactly match {CONFIRM_EDGE_STATUS_TARGET_PREFLIGHT}",),
        )

    try:
        adapter = build_adapter(provider)
    except Exception as exc:
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_STATUS_TARGET_NOT_READY,
            browser_lane=browser_lane,
            status_chat_configured=status_chat_configured,
            status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
            target_url_sha256=target_url_sha256,
            live_browser=True,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=True,
            edge_target_ready=False,
            edge_target_focused=False,
            composer_candidate_count=0,
            target_window_count=0,
            matching_target_count=0,
            selected_target_title=None,
            provider=provider,
            required_next_gate="edge_status_message_send_gate",
            issues=(str(exc),),
        )

    probe = adapter.focus_target()
    if not probe.ready or not probe.focused:
        return make_result(
            ok=False,
            result_label=BLOCKED_EDGE_STATUS_TARGET_NOT_READY,
            browser_lane=browser_lane,
            status_chat_configured=status_chat_configured,
            status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
            target_url_sha256=target_url_sha256,
            live_browser=True,
            confirmation_text_supplied=confirmation_text,
            confirmation_matched=True,
            edge_target_ready=probe.ready,
            edge_target_focused=probe.focused,
            composer_candidate_count=probe.composer_candidate_count,
            target_window_count=probe.target_window_count,
            matching_target_count=probe.matching_target_count,
            selected_target_title=probe.selected_target_title,
            provider=adapter.provider_name,
            required_next_gate="edge_status_message_send_gate",
            issues=probe.issues,
        )

    return make_result(
        ok=True,
        result_label=PASS_EDGE_STATUS_TARGET_PREFLIGHT_READY,
        browser_lane=browser_lane,
        status_chat_configured=True,
        status_chat_url_hash_or_redacted=status_chat_url_hash_or_redacted,
        target_url_sha256=target_url_sha256,
        live_browser=True,
        confirmation_text_supplied=confirmation_text,
        confirmation_matched=True,
        edge_target_ready=True,
        edge_target_focused=True,
        composer_candidate_count=probe.composer_candidate_count,
        target_window_count=probe.target_window_count,
        matching_target_count=probe.matching_target_count,
        selected_target_title=probe.selected_target_title,
        provider=adapter.provider_name,
        required_next_gate="edge_status_message_send_gate",
        issues=(),
    )


def load_status_target_payload(path: Path | None) -> Mapping[str, Any] | None:
    if path is None:
        if DEFAULT_STATUS_TARGET_VALIDATION_PATH.exists():
            return load_json_object(DEFAULT_STATUS_TARGET_VALIDATION_PATH)
        if DEFAULT_STATUS_TARGET_CONFIG_PATH.exists():
            return load_json_object(DEFAULT_STATUS_TARGET_CONFIG_PATH)
        return None
    if not path.exists():
        return None
    return load_json_object(path)


def render_text(result: EdgeStatusTargetPreflightResult) -> str:
    lines = [
        f"result_label: {result.result_label}",
        f"ok: {str(result.ok).lower()}",
        f"patch_name: {result.patch_name}",
        f"browser_lane: {result.browser_lane}",
        f"status_chat_configured: {str(result.status_chat_configured).lower()}",
        f"status_chat_url_hash_or_redacted: {result.status_chat_url_hash_or_redacted}",
        f"target_url_sha256: {result.target_url_sha256}",
        f"live_browser: {str(result.live_browser).lower()}",
        f"confirmation_text_supplied: {result.confirmation_text_supplied}",
        f"confirmation_matched: {str(result.confirmation_matched).lower()}",
        f"edge_target_ready: {str(result.edge_target_ready).lower()}",
        f"edge_target_focused: {str(result.edge_target_focused).lower()}",
        f"composer_candidate_count: {result.composer_candidate_count}",
        f"target_window_count: {result.target_window_count}",
        f"matching_target_count: {result.matching_target_count}",
        f"selected_target_title_hash: {result.selected_target_title_hash}",
        f"selected_target_title_length: {result.selected_target_title_length}",
        f"provider: {result.provider}",
        f"required_next_gate: {result.required_next_gate}",
        f"browser_action_performed: {str(result.browser_action_performed).lower()}",
        f"chatgpt_submit_performed: {str(result.chatgpt_submit_performed).lower()}",
        f"operator_report_uploaded: {str(result.operator_report_uploaded).lower()}",
        f"status_message_posted: {str(result.status_message_posted).lower()}",
        f"send_button_pressed: {str(result.send_button_pressed).lower()}",
        f"raw_conversation_text_available: {str(result.raw_conversation_text_available).lower()}",
        f"selenium_used: {str(result.selenium_used).lower()}",
        f"webdriver_used: {str(result.webdriver_used).lower()}",
        f"browser_dom_automation_used: {str(result.browser_dom_automation_used).lower()}",
        f"cloudflare_bypass_attempted: {str(result.cloudflare_bypass_attempted).lower()}",
        f"captcha_bypass_attempted: {str(result.captcha_bypass_attempted).lower()}",
        f"created_at: {result.created_at}",
    ]
    if result.issues:
        lines.append("issues:")
        for issue in result.issues:
            lines.append(f"- {issue}")
    else:
        lines.append("issues: none")
    return "\n".join(lines) + "\n"


def write_preflight_evidence(
    result: EdgeStatusTargetPreflightResult,
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
    parser = argparse.ArgumentParser(description="Edge status target preflight")
    parser.add_argument("--status-target-path", default=None)
    parser.add_argument("--provider", choices=("fake-ready", "fake-no-target", "fake-ambiguous-target", "fake-no-composer", "pywinauto"), default="fake-ready")
    parser.add_argument("--live-browser", action="store_true")
    parser.add_argument("--confirm-live-browser-text", default=None)
    parser.add_argument("--json-output-path", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--txt-output-path", default=str(DEFAULT_TXT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = load_status_target_payload(Path(args.status_target_path) if args.status_target_path else None)
    result = run_edge_status_target_preflight(
        status_target_payload=payload,
        live_browser=bool(args.live_browser),
        confirmation_text=args.confirm_live_browser_text,
        provider=args.provider,
    )

    if not args.no_write_evidence:
        write_preflight_evidence(result, json_output_path=Path(args.json_output_path), txt_output_path=Path(args.txt_output_path))

    if args.json:
        print(
            json.dumps(
                result.to_dict(),
                sort_keys=True,
                separators=(",", ":") if args.compact else None,
                indent=None if args.compact else 2,
            )
        )
    else:
        print(render_text(result), end="")

    return 0 if result.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())