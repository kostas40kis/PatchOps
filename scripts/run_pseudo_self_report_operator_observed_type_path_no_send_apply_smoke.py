from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH_NAME = "pseudo_self_report_upload_no_send_repair_17_operator_observed_type_path"
CONFIRM_TEXT = "PATCHOPS_CONFIRM_CHROME_OPERATOR_OBSERVED_TYPE_PATH_NO_SEND"
RESULT_LABEL = "OPERATOR_OBSERVED_SEQUENCE_ATTEMPTED_TYPE_PATH_NO_SEND"
DEFAULT_CONFIG_PATH = Path("data/config/uploader_status_target_config.json")
DEFAULT_JSON_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_pseudo_self_report_operator_observed_type_path_no_send.json")
DEFAULT_TXT_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_pseudo_self_report_operator_observed_type_path_no_send.txt")
DEFAULT_DESKTOP_DIR = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return payload


def normalize_bool(value: Any, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def validate_config(config_payload: Mapping[str, Any] | None) -> tuple[bool, str | None, str | None, tuple[str, ...]]:
    if not config_payload:
        return False, None, None, ("status target config is required",)
    status = config_payload.get("status_chat")
    if not isinstance(status, Mapping):
        return False, None, None, ("status_chat object is required",)
    issues: list[str] = []
    enabled = normalize_bool(status.get("enabled"), default=False)
    lane = str(status.get("browser_lane") or "").strip()
    target_url = str(status.get("target_url") or "").strip()
    target_hash = str(status.get("target_url_sha256") or "").strip() or None
    if not enabled:
        issues.append("status_chat.enabled must be true")
    if lane != "chrome":
        issues.append("browser_lane must be chrome")
    if not target_url.startswith("https://chatgpt.com/") or "/c/" not in target_url:
        issues.append("target_url must be a ChatGPT conversation URL")
    url_hash = sha256_text(target_url) if target_url else None
    if target_url and target_hash and target_hash != url_hash:
        issues.append("target_url_sha256 does not match target_url")
    return not issues, url_hash, target_hash, tuple(issues)


def is_child_of(path: Path, parent: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(parent.resolve(strict=False))
        return True
    except ValueError:
        return False


def send_literal_path(path_text: str) -> None:
    from pywinauto import keyboard  # type: ignore
    # Do not use validation here. The operator will observe whether text appears.
    # Escape braces only; Windows paths do not need slash escaping for send_keys with vk_packet.
    safe = path_text.replace("{", "{{}").replace("}", "{}}")
    keyboard.send_keys(safe, pause=0.001, with_spaces=True, vk_packet=True)


def send_sequence(path_text: str, *, slash_delay: float, picker_ready_delay: float, after_type_delay: float) -> tuple[bool, tuple[str, ...]]:
    from pywinauto import Desktop, keyboard  # type: ignore

    issues: list[str] = []
    try:
        windows = list(Desktop(backend="uia").windows())
        chrome_windows = [w for w in windows if "chrome" in str(w.window_text() or "").lower() and ("chatgpt" in str(w.window_text() or "").lower() or "patchops" in str(w.window_text() or "").lower())]
        if chrome_windows:
            chrome_windows[0].set_focus()
            time.sleep(0.4)
        else:
            issues.append("no Chrome ChatGPT/PatchOps window matched; continuing with current foreground window")
    except Exception as exc:
        issues.append(f"focus attempt failed; continuing with current foreground window: {exc}")

    # Operator-observed mode: no picker/window validation. Just do the exact intended sequence.
    keyboard.send_keys("/", pause=0.05)
    time.sleep(slash_delay)
    keyboard.send_keys("{ENTER}", pause=0.05)
    time.sleep(picker_ready_delay)
    send_literal_path(path_text)
    time.sleep(after_type_delay)
    keyboard.send_keys("{ENTER}", pause=0.05)
    return True, tuple(issues)


@dataclass(frozen=True)
class AttemptResult:
    ok: bool
    result_label: str
    patch_name: str
    selected_action: str
    browser_lane: str
    live_browser: bool
    stop_before_send: bool
    confirmation_matched: bool
    status_chat_configured: bool
    status_chat_url_hash_or_redacted: str | None
    target_url_sha256: str | None
    desktop_directory: str | None
    self_report_path: str | None
    self_report_filename: str | None
    self_report_sha256: str | None
    computed_self_report_sha256: str | None
    operator_observed_mode: bool
    automated_ui_step_validation_used: bool
    automated_attachment_verification_used: bool
    chrome_open_invoked: bool
    mouse_clicks_used: bool
    slash_key_attempted: bool
    upload_command_enter_attempted: bool
    full_path_type_attempted: bool
    picker_enter_attempted: bool
    path_text_sent: str | None
    path_text_length: int
    path_text_sha256: str | None
    operator_must_confirm_visible_result: bool
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
    provider: str
    issues: tuple[str, ...]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def make_result(**kwargs: Any) -> AttemptResult:
    defaults: dict[str, Any] = dict(
        ok=False,
        result_label="BLOCKED_UNSET",
        patch_name=PATCH_NAME,
        selected_action="upload_self_report_operator_observed_type_path_no_send",
        browser_lane="chrome",
        live_browser=True,
        stop_before_send=True,
        confirmation_matched=False,
        status_chat_configured=False,
        status_chat_url_hash_or_redacted=None,
        target_url_sha256=None,
        desktop_directory=None,
        self_report_path=None,
        self_report_filename=None,
        self_report_sha256=None,
        computed_self_report_sha256=None,
        operator_observed_mode=True,
        automated_ui_step_validation_used=False,
        automated_attachment_verification_used=False,
        chrome_open_invoked=False,
        mouse_clicks_used=False,
        slash_key_attempted=False,
        upload_command_enter_attempted=False,
        full_path_type_attempted=False,
        picker_enter_attempted=False,
        path_text_sent=None,
        path_text_length=0,
        path_text_sha256=None,
        operator_must_confirm_visible_result=True,
        operator_report_uploaded=False,
        chatgpt_submit_performed=False,
        status_message_posted=False,
        send_button_pressed=False,
        raw_conversation_text_available=False,
        selenium_used=False,
        webdriver_used=False,
        browser_dom_automation_used=False,
        cloudflare_bypass_attempted=False,
        captcha_bypass_attempted=False,
        provider="pywinauto",
        issues=(),
    )
    defaults.update(kwargs)
    return AttemptResult(**defaults)


def run_attempt(*, config_payload: Mapping[str, Any] | None, provider: str, live_browser: bool, confirmation_text: str | None, self_report_path: str | None, expected_sha256: str | None, desktop_dir: Path, slash_delay: float, picker_ready_delay: float, after_type_delay: float) -> AttemptResult:
    config_ok, url_hash, target_hash, config_issues = validate_config(config_payload)
    confirmation_matched = confirmation_text == CONFIRM_TEXT
    report = Path(self_report_path) if self_report_path else None
    common = dict(
        confirmation_matched=confirmation_matched,
        status_chat_configured=config_ok,
        status_chat_url_hash_or_redacted=url_hash,
        target_url_sha256=target_hash,
        desktop_directory=str(desktop_dir),
        self_report_path=str(report) if report else None,
        self_report_filename=report.name if report else None,
    )
    if not config_ok:
        return make_result(result_label="BLOCKED_OPERATOR_OBSERVED_CONFIG_INVALID", issues=config_issues, **common)
    if confirmation_text is None:
        return make_result(result_label="BLOCKED_OPERATOR_OBSERVED_CONFIRMATION_REQUIRED", issues=("live confirmation is required",), **common)
    if not confirmation_matched:
        return make_result(result_label="BLOCKED_OPERATOR_OBSERVED_CONFIRMATION_MISMATCH", issues=(f"confirmation must exactly match {CONFIRM_TEXT}",), **common)
    if not live_browser:
        return make_result(result_label="BLOCKED_OPERATOR_OBSERVED_LIVE_BROWSER_REQUIRED", live_browser=False, issues=("--live-browser is required",), **common)
    if report is None or not report.exists() or not report.is_file():
        return make_result(result_label="BLOCKED_OPERATOR_OBSERVED_REPORT_MISSING", issues=(f"self report not found: {report}",), **common)
    if not is_child_of(report, desktop_dir):
        return make_result(result_label="BLOCKED_OPERATOR_OBSERVED_REPORT_NOT_ON_DESKTOP", issues=(f"self report must be on Desktop: {desktop_dir}",), **common)
    computed = sha256_file(report)
    if expected_sha256 and expected_sha256 != computed:
        return make_result(result_label="BLOCKED_OPERATOR_OBSERVED_REPORT_HASH_MISMATCH", self_report_sha256=expected_sha256, computed_self_report_sha256=computed, issues=("self report hash mismatch",), **common)

    path_text = str(report.resolve(strict=False))
    issues: tuple[str, ...] = ()
    if provider == "pywinauto":
        _ok, issues = send_sequence(path_text, slash_delay=slash_delay, picker_ready_delay=picker_ready_delay, after_type_delay=after_type_delay)
    elif provider == "fake-ready":
        issues = ()
    else:
        return make_result(result_label="BLOCKED_OPERATOR_OBSERVED_UNKNOWN_PROVIDER", self_report_sha256=computed, computed_self_report_sha256=computed, issues=(f"unknown provider: {provider}",), **common)

    return make_result(
        ok=True,
        result_label=RESULT_LABEL,
        confirmation_matched=True,
        status_chat_configured=True,
        status_chat_url_hash_or_redacted=url_hash,
        target_url_sha256=target_hash,
        desktop_directory=str(desktop_dir),
        self_report_path=str(report),
        self_report_filename=report.name,
        self_report_sha256=computed,
        computed_self_report_sha256=computed,
        slash_key_attempted=True,
        upload_command_enter_attempted=True,
        full_path_type_attempted=True,
        picker_enter_attempted=True,
        path_text_sent=path_text,
        path_text_length=len(path_text),
        path_text_sha256=sha256_text(path_text),
        provider=provider,
        issues=issues,
    )


def render_text(result: AttemptResult) -> str:
    lines: list[str] = []
    for key, value in result.to_dict().items():
        if key == "issues":
            continue
        if isinstance(value, bool):
            value = str(value).lower()
        lines.append(f"{key}: {value}")
    if result.issues:
        lines.append("issues:")
        for issue in result.issues:
            lines.append(f"- {issue}")
    else:
        lines.append("issues: none")
    return "\n".join(lines) + "\n"


def write_evidence(result: AttemptResult, *, json_output_path: Path = DEFAULT_JSON_OUTPUT_PATH, txt_output_path: Path = DEFAULT_TXT_OUTPUT_PATH) -> tuple[Path, Path]:
    json_output_path.parent.mkdir(parents=True, exist_ok=True)
    txt_output_path.parent.mkdir(parents=True, exist_ok=True)
    json_output_path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    txt_output_path.write_text(render_text(result), encoding="utf-8")
    return json_output_path, txt_output_path


def write_self_report(path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"patch_name: {PATCH_NAME}",
        "purpose: operator-observed attempt-only upload sequence; no automated UI-step validation",
        f"created_at: {datetime.now(timezone.utc).isoformat()}",
        "selected_action: upload_self_report_operator_observed_type_path_no_send",
        "browser_lane: chrome",
        "manual_sequence: existing_chrome__slash__enter__type_full_path__enter",
        "operator_observed_mode: true",
        "automated_ui_step_validation_used: false",
        "automated_attachment_verification_used: false",
        "operator_report_uploaded: false",
        "chatgpt_submit_performed: false",
        "send_button_pressed: false",
        "chrome_open_invoked: false",
        "mouse_clicks_used: false",
        "raw_conversation_text_available: false",
        "selenium_used: false",
        "webdriver_used: false",
        "browser_dom_automation_used: false",
        "cloudflare_bypass_attempted: false",
        "captcha_bypass_attempted: false",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return sha256_file(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Operator-observed attempt-only flow: existing Chrome, slash Enter, type full path, Enter, no Send")
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--desktop-dir", default=str(DEFAULT_DESKTOP_DIR))
    parser.add_argument("--self-report-filename", default="pseudo_self_report_upload_no_send_repair_17_operator_observed_type_path_self_report.txt")
    parser.add_argument("--provider", choices=("pywinauto", "fake-ready"), default="pywinauto")
    parser.add_argument("--confirm-live-browser-text", default=CONFIRM_TEXT)
    parser.add_argument("--slash-delay", type=float, default=0.30)
    parser.add_argument("--picker-ready-delay", type=float, default=0.90)
    parser.add_argument("--after-type-delay", type=float, default=0.25)
    parser.add_argument("--json-output-path", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--txt-output-path", default=str(DEFAULT_TXT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config_path = Path(args.config_path)
    desktop_dir = Path(args.desktop_dir)
    self_report_path = desktop_dir / args.self_report_filename
    self_report_hash = write_self_report(self_report_path)
    config_payload = load_json_object(config_path) if config_path.exists() else None
    result = run_attempt(
        config_payload=config_payload,
        provider=args.provider,
        live_browser=True,
        confirmation_text=args.confirm_live_browser_text,
        self_report_path=str(self_report_path),
        expected_sha256=self_report_hash,
        desktop_dir=desktop_dir,
        slash_delay=args.slash_delay,
        picker_ready_delay=args.picker_ready_delay,
        after_type_delay=args.after_type_delay,
    )
    write_evidence(result, json_output_path=Path(args.json_output_path), txt_output_path=Path(args.txt_output_path))
    print(f"DESKTOP_DIR: {desktop_dir}")
    print(f"SELF_REPORT_FILENAME: {self_report_path.name}")
    print(f"SELF_REPORT_PATH: {self_report_path}")
    print(f"SELF_REPORT_SHA256: {self_report_hash}")
    print(f"ATTEMPTED_PATH_TEXT: {self_report_path}")
    print(f"EVIDENCE_JSON: {args.json_output_path}")
    print(f"EVIDENCE_TXT: {args.txt_output_path}")
    print(render_text(result), end="")
    if args.json:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 0 if result.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())