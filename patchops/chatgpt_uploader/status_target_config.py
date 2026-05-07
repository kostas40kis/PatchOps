from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse

PATCH_NAME = "u3_c28_uploader_status_target_config_named_lanes"

DEFAULT_CONFIG_PATH = Path("data/config/uploader_status_target_config.json")
DEFAULT_EXAMPLE_CONFIG_PATH = Path("data/config/uploader_status_target_config.example.json")
DEFAULT_JSON_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_uploader_status_target_config_validation.json")
DEFAULT_TXT_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_uploader_status_target_config_validation.txt")

PASS_UPLOADER_STATUS_TARGET_CONFIG_VALIDATED = "PASS_UPLOADER_STATUS_TARGET_CONFIG_VALIDATED"
BLOCKED_STATUS_TARGET_CONFIG_MISSING = "BLOCKED_STATUS_TARGET_CONFIG_MISSING"
BLOCKED_STATUS_TARGET_BROWSER_UNSUPPORTED = "BLOCKED_STATUS_TARGET_BROWSER_UNSUPPORTED"
BLOCKED_STATUS_TARGET_URL_INVALID = "BLOCKED_STATUS_TARGET_URL_INVALID"

ALLOWED_BROWSER_LANES = frozenset({"chrome", "edge"})
REJECTED_BROWSER_LANES = frozenset(
    {
        "any",
        "auto",
        "all",
        "default",
        "firefox",
        "brave",
        "opera",
        "vivaldi",
        "chromium",
        "msedge",
        "safari",
    }
)

REQUIRED_TOP_LEVEL_KEY = "status_chat"


@dataclass(frozen=True)
class StatusTargetConfigSafety:
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
class StatusTargetConfigValidation:
    ok: bool
    result_label: str
    config_path: str | None
    config_sha256: str | None
    enabled: bool
    browser_lane: str | None
    target_url_hash: str | None
    redacted_target_display: str | None
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
    safety: StatusTargetConfigSafety = field(default_factory=StatusTargetConfigSafety)

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


def normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def normalize_browser_lane(value: Any) -> str | None:
    text = normalize_optional_text(value)
    return text.lower() if text else None


def normalize_bool(value: Any, *, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on", "enabled"}:
        return True
    if text in {"0", "false", "no", "n", "off", "disabled"}:
        return False
    return default


def load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return payload


def redact_target_url(target_url: str) -> str:
    parsed = urlparse(target_url)
    host = parsed.netloc or "(no-host)"
    if parsed.path.startswith("/c/"):
        path_display = "/c/<redacted>"
    elif parsed.path:
        first = parsed.path.strip("/").split("/")[0]
        path_display = f"/{first}/<redacted>"
    else:
        path_display = "/<redacted>"
    return f"{parsed.scheme}://{host}{path_display}"


def is_valid_chatgpt_target_url(target_url: str | None) -> bool:
    if not target_url:
        return False
    parsed = urlparse(target_url)
    if parsed.scheme != "https":
        return False
    host = parsed.netloc.lower()
    if host not in {"chatgpt.com", "www.chatgpt.com"}:
        return False
    if not parsed.path or parsed.path == "/":
        return False
    return True


def make_validation(
    *,
    ok: bool,
    result_label: str,
    config_path: Path | None,
    config_sha256: str | None,
    enabled: bool,
    browser_lane: str | None,
    target_url_hash: str | None,
    redacted_target_display: str | None,
    issues: Sequence[str],
) -> StatusTargetConfigValidation:
    safety = StatusTargetConfigSafety()
    return StatusTargetConfigValidation(
        ok=ok,
        result_label=result_label,
        config_path=str(config_path) if config_path else None,
        config_sha256=config_sha256,
        enabled=enabled,
        browser_lane=browser_lane,
        target_url_hash=target_url_hash,
        redacted_target_display=redacted_target_display,
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


def validate_status_target_config_payload(
    payload: Mapping[str, Any],
    *,
    config_path: Path | None = None,
    config_sha256: str | None = None,
) -> StatusTargetConfigValidation:
    issues: list[str] = []

    status_chat = payload.get(REQUIRED_TOP_LEVEL_KEY)
    if not isinstance(status_chat, Mapping):
        issues.append("missing status_chat object")
        return make_validation(
            ok=False,
            result_label=BLOCKED_STATUS_TARGET_CONFIG_MISSING,
            config_path=config_path,
            config_sha256=config_sha256,
            enabled=False,
            browser_lane=None,
            target_url_hash=None,
            redacted_target_display=None,
            issues=issues,
        )

    enabled = normalize_bool(status_chat.get("enabled"), default=False)
    browser_lane = normalize_browser_lane(status_chat.get("browser_lane"))
    target_url = normalize_optional_text(status_chat.get("target_url"))
    supplied_hash = normalize_optional_text(status_chat.get("target_url_sha256"))

    if browser_lane not in ALLOWED_BROWSER_LANES:
        if browser_lane in REJECTED_BROWSER_LANES:
            issues.append(f"rejected browser_lane: {browser_lane}")
        else:
            issues.append(f"unsupported browser_lane: {browser_lane!r}")
        return make_validation(
            ok=False,
            result_label=BLOCKED_STATUS_TARGET_BROWSER_UNSUPPORTED,
            config_path=config_path,
            config_sha256=config_sha256,
            enabled=enabled,
            browser_lane=browser_lane,
            target_url_hash=supplied_hash,
            redacted_target_display=None,
            issues=issues,
        )

    if not is_valid_chatgpt_target_url(target_url):
        issues.append("target_url must be an https ChatGPT conversation or project chat URL")
        return make_validation(
            ok=False,
            result_label=BLOCKED_STATUS_TARGET_URL_INVALID,
            config_path=config_path,
            config_sha256=config_sha256,
            enabled=enabled,
            browser_lane=browser_lane,
            target_url_hash=supplied_hash,
            redacted_target_display=None,
            issues=issues,
        )

    computed_hash = sha256_text(target_url or "")
    target_url_hash = supplied_hash or computed_hash
    if supplied_hash and supplied_hash != computed_hash:
        issues.append("target_url_sha256 does not match target_url")
        return make_validation(
            ok=False,
            result_label=BLOCKED_STATUS_TARGET_URL_INVALID,
            config_path=config_path,
            config_sha256=config_sha256,
            enabled=enabled,
            browser_lane=browser_lane,
            target_url_hash=supplied_hash,
            redacted_target_display=redact_target_url(target_url or ""),
            issues=issues,
        )

    return make_validation(
        ok=True,
        result_label=PASS_UPLOADER_STATUS_TARGET_CONFIG_VALIDATED,
        config_path=config_path,
        config_sha256=config_sha256,
        enabled=enabled,
        browser_lane=browser_lane,
        target_url_hash=target_url_hash,
        redacted_target_display=redact_target_url(target_url or ""),
        issues=issues,
    )


def validate_status_target_config_path(config_path: Path) -> StatusTargetConfigValidation:
    if not config_path.exists():
        return make_validation(
            ok=False,
            result_label=BLOCKED_STATUS_TARGET_CONFIG_MISSING,
            config_path=config_path,
            config_sha256=None,
            enabled=False,
            browser_lane=None,
            target_url_hash=None,
            redacted_target_display=None,
            issues=[f"config file not found: {config_path}"],
        )
    config_sha256 = sha256_file(config_path)
    payload = load_json_object(config_path)
    return validate_status_target_config_payload(payload, config_path=config_path, config_sha256=config_sha256)


def render_text(validation: StatusTargetConfigValidation) -> str:
    lines = [
        f"result_label: {validation.result_label}",
        f"ok: {str(validation.ok).lower()}",
        f"config_path: {validation.config_path}",
        f"config_sha256: {validation.config_sha256}",
        f"enabled: {str(validation.enabled).lower()}",
        f"browser_lane: {validation.browser_lane}",
        f"target_url_hash: {validation.target_url_hash}",
        f"redacted_target_display: {validation.redacted_target_display}",
        f"browser_action_performed: {str(validation.browser_action_performed).lower()}",
        f"chatgpt_submit_performed: {str(validation.chatgpt_submit_performed).lower()}",
        f"operator_report_uploaded: {str(validation.operator_report_uploaded).lower()}",
        f"status_message_posted: {str(validation.status_message_posted).lower()}",
        f"send_button_pressed: {str(validation.send_button_pressed).lower()}",
        f"raw_conversation_text_available: {str(validation.raw_conversation_text_available).lower()}",
        f"selenium_used: {str(validation.selenium_used).lower()}",
        f"webdriver_used: {str(validation.webdriver_used).lower()}",
        f"browser_dom_automation_used: {str(validation.browser_dom_automation_used).lower()}",
        f"cloudflare_bypass_attempted: {str(validation.cloudflare_bypass_attempted).lower()}",
        f"captcha_bypass_attempted: {str(validation.captcha_bypass_attempted).lower()}",
        f"created_at: {validation.created_at}",
    ]
    if validation.issues:
        lines.append("issues:")
        for issue in validation.issues:
            lines.append(f"- {issue}")
    else:
        lines.append("issues: none")
    return "\n".join(lines) + "\n"


def write_validation_evidence(
    validation: StatusTargetConfigValidation,
    *,
    json_output_path: Path = DEFAULT_JSON_OUTPUT_PATH,
    txt_output_path: Path = DEFAULT_TXT_OUTPUT_PATH,
) -> tuple[Path, Path]:
    json_output_path.parent.mkdir(parents=True, exist_ok=True)
    txt_output_path.parent.mkdir(parents=True, exist_ok=True)
    json_output_path.write_text(json.dumps(validation.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    txt_output_path.write_text(render_text(validation), encoding="utf-8")
    return json_output_path, txt_output_path


def example_config_payload(*, browser_lane: str = "chrome", target_url: str = "https://chatgpt.com/c/example") -> dict[str, Any]:
    return {
        "status_chat": {
            "browser_lane": browser_lane,
            "target_url": target_url,
            "target_url_sha256": sha256_text(target_url),
            "enabled": True,
        }
    }


def write_example_config(path: Path = DEFAULT_EXAMPLE_CONFIG_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(example_config_payload(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PatchOps uploader status target config doctor for named browser lanes")
    parser.add_argument("--config-path", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--json-output-path", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--txt-output-path", default=str(DEFAULT_TXT_OUTPUT_PATH))
    parser.add_argument("--write-example-config", action="store_true")
    parser.add_argument("--example-config-path", default=str(DEFAULT_EXAMPLE_CONFIG_PATH))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.write_example_config:
        write_example_config(Path(args.example_config_path))

    config_path = Path(args.config_path)
    json_output_path = Path(args.json_output_path)
    txt_output_path = Path(args.txt_output_path)

    try:
        validation = validate_status_target_config_path(config_path)
    except Exception as exc:  # noqa: BLE001
        validation = make_validation(
            ok=False,
            result_label=BLOCKED_STATUS_TARGET_CONFIG_MISSING,
            config_path=config_path,
            config_sha256=sha256_file(config_path) if config_path.exists() else None,
            enabled=False,
            browser_lane=None,
            target_url_hash=None,
            redacted_target_display=None,
            issues=[str(exc)],
        )

    if not args.no_write_evidence:
        write_validation_evidence(validation, json_output_path=json_output_path, txt_output_path=txt_output_path)

    if args.json:
        print(
            json.dumps(
                validation.to_dict(),
                sort_keys=True,
                separators=(",", ":") if args.compact else None,
                indent=None if args.compact else 2,
            )
        )
    else:
        print(render_text(validation), end="")

    return 0 if validation.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())