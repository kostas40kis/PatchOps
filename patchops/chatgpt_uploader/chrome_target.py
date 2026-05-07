from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlsplit

PASS_CHROME_TARGET_CONFIG_VALIDATED = "PASS_CHROME_TARGET_CONFIG_VALIDATED"
BLOCKED_TARGET_CONFIG_MISSING = "BLOCKED_TARGET_CONFIG_MISSING"
BLOCKED_TARGET_CONFIG_INVALID = "BLOCKED_TARGET_CONFIG_INVALID"
BLOCKED_UNSUPPORTED_BROWSER = "BLOCKED_UNSUPPORTED_BROWSER"

EXPECTED_BROWSER = "chrome"
DEFAULT_TARGET_CONFIG_RELATIVE = Path("data/config/chatgpt_copilot_target.json")

SAFETY_FLAGS = {
    "selenium_used": False,
    "webdriver_used": False,
    "browser_dom_automation_used": False,
    "cloudflare_bypass_attempted": False,
    "captcha_bypass_attempted": False,
    "conversation_text_logged": False,
    "raw_conversation_text_logged": False,
    "random_page_click_performed": False,
    "chatgpt_submit_performed": False,
    "file_upload_attempted": False,
    "canonical_report_found": False,
    "live_browser_used": False,
    "browser_launched": False,
}


class ChromeTargetConfigError(ValueError):
    """Raised when Chrome target config is missing or invalid."""


@dataclass(frozen=True)
class ChromeTargetConfig:
    target_url: str
    browser: str = EXPECTED_BROWSER
    upload_mode: str = "file_picker_no_send"
    source: str = "operator_config"


@dataclass(frozen=True)
class ChromeTargetEvidence:
    ok: bool
    result: str
    expected_browser: str
    browser: str | None
    target_url_hash: str | None
    redacted_target_display: str | None
    raw_conversation_text_logged: bool
    file_upload_attempted: bool
    chatgpt_submit_performed: bool
    target_config_path: str | None
    safety_flags: dict[str, bool]
    error: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def target_url_sha256(target_url: str) -> str:
    return hashlib.sha256(str(target_url).encode("utf-8")).hexdigest()


def redact_target_url(target_url: str) -> str:
    value = str(target_url or "").strip()
    if not value:
        return "<missing-target-url>"

    parsed = urlsplit(value)
    host = parsed.netloc or "<unknown-host>"
    path_parts = [part for part in parsed.path.split("/") if part]
    if not path_parts:
        return f"{parsed.scheme or 'https'}://{host}/<redacted>"

    first = path_parts[0]
    last = path_parts[-1]
    if len(path_parts) == 1:
        return f"{parsed.scheme or 'https'}://{host}/{first}/<redacted>"
    return f"{parsed.scheme or 'https'}://{host}/{first}/.../{last[:8]}<redacted>"


def _normalize_browser(value: object) -> str:
    return str(value or EXPECTED_BROWSER).strip().lower()


def validate_target_url(target_url: object) -> str:
    value = str(target_url or "").strip()
    if not value:
        raise ChromeTargetConfigError("target_url is required")
    parsed = urlsplit(value)
    if parsed.scheme not in {"https", "http"}:
        raise ChromeTargetConfigError("target_url must use http or https")
    if "chatgpt.com" not in parsed.netloc.lower():
        raise ChromeTargetConfigError("target_url must point at chatgpt.com")
    return value


def validate_chrome_target_payload(payload: Mapping[str, Any]) -> ChromeTargetConfig:
    browser = _normalize_browser(payload.get("browser", EXPECTED_BROWSER))
    if browser != EXPECTED_BROWSER:
        raise ChromeTargetConfigError(f"{BLOCKED_UNSUPPORTED_BROWSER}: expected browser='chrome', got {browser!r}")

    target_url = validate_target_url(payload.get("target_url"))
    upload_mode = str(payload.get("upload_mode") or payload.get("mode") or "file_picker_no_send")
    source = str(payload.get("source") or payload.get("source_patch") or "operator_config")
    return ChromeTargetConfig(target_url=target_url, browser=EXPECTED_BROWSER, upload_mode=upload_mode, source=source)


def default_target_config_path(repo_root: Path | str | None = None) -> Path:
    if repo_root is None:
        return DEFAULT_TARGET_CONFIG_RELATIVE
    return Path(repo_root).expanduser().resolve() / DEFAULT_TARGET_CONFIG_RELATIVE


def read_chrome_target_config(path: Path | str) -> ChromeTargetConfig:
    config_path = Path(path).expanduser().resolve()
    if not config_path.exists():
        raise FileNotFoundError(str(config_path))
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ChromeTargetConfigError(f"target config is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ChromeTargetConfigError("target config must be a JSON object")
    return validate_chrome_target_payload(payload)


def build_chrome_target_evidence(config: ChromeTargetConfig, *, target_config_path: Path | str | None = None) -> ChromeTargetEvidence:
    return ChromeTargetEvidence(
        ok=True,
        result=PASS_CHROME_TARGET_CONFIG_VALIDATED,
        expected_browser=EXPECTED_BROWSER,
        browser=config.browser,
        target_url_hash=target_url_sha256(config.target_url),
        redacted_target_display=redact_target_url(config.target_url),
        raw_conversation_text_logged=False,
        file_upload_attempted=False,
        chatgpt_submit_performed=False,
        target_config_path=str(Path(target_config_path).expanduser().resolve()) if target_config_path else None,
        safety_flags=dict(SAFETY_FLAGS),
        error=None,
    )


def build_blocked_chrome_target_evidence(
    *,
    result: str,
    error: str,
    target_config_path: Path | str | None = None,
    browser: str | None = None,
) -> ChromeTargetEvidence:
    return ChromeTargetEvidence(
        ok=False,
        result=result,
        expected_browser=EXPECTED_BROWSER,
        browser=browser,
        target_url_hash=None,
        redacted_target_display=None,
        raw_conversation_text_logged=False,
        file_upload_attempted=False,
        chatgpt_submit_performed=False,
        target_config_path=str(Path(target_config_path).expanduser().resolve()) if target_config_path else None,
        safety_flags=dict(SAFETY_FLAGS),
        error=error,
    )


def probe_chrome_target_config(path: Path | str) -> ChromeTargetEvidence:
    config_path = Path(path).expanduser().resolve()
    try:
        config = read_chrome_target_config(config_path)
    except FileNotFoundError as exc:
        return build_blocked_chrome_target_evidence(
            result=BLOCKED_TARGET_CONFIG_MISSING,
            error=str(exc),
            target_config_path=config_path,
        )
    except ChromeTargetConfigError as exc:
        text = str(exc)
        result = BLOCKED_UNSUPPORTED_BROWSER if BLOCKED_UNSUPPORTED_BROWSER in text else BLOCKED_TARGET_CONFIG_INVALID
        return build_blocked_chrome_target_evidence(
            result=result,
            error=text,
            target_config_path=config_path,
        )
    return build_chrome_target_evidence(config, target_config_path=config_path)


def write_chrome_target_evidence(evidence: ChromeTargetEvidence, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(evidence.to_payload(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_path