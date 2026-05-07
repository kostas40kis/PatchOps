from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH_NAME = "u3_c36_status_delivery_consistency_hardening"

ACTION_POST_STATUS_MESSAGE = "post_status_message"
ACTION_UPLOAD_OPERATOR_REPORT = "upload_operator_report"
ACTION_RECORD_PASS_LOCALLY_NO_UPLOAD = "record_pass_locally_no_upload"
ALLOWED_ACTIONS = frozenset({ACTION_POST_STATUS_MESSAGE, ACTION_UPLOAD_OPERATOR_REPORT, ACTION_RECORD_PASS_LOCALLY_NO_UPLOAD})
ALLOWED_BROWSER_LANES = frozenset({"chrome", "edge"})

PASS_STATUS_DELIVERY_CONSISTENCY_HARDENED = "PASS_STATUS_DELIVERY_CONSISTENCY_HARDENED"
BLOCKED_STATUS_DELIVERY_SCHEMA_INVALID = "BLOCKED_STATUS_DELIVERY_SCHEMA_INVALID"
BLOCKED_STATUS_DELIVERY_HASH_MISMATCH = "BLOCKED_STATUS_DELIVERY_HASH_MISMATCH"
BLOCKED_STATUS_DELIVERY_IDEMPOTENCY_CONFLICT = "BLOCKED_STATUS_DELIVERY_IDEMPOTENCY_CONFLICT"
BLOCKED_STATUS_DELIVERY_UNBOUNDED_RETRY = "BLOCKED_STATUS_DELIVERY_UNBOUNDED_RETRY"
BLOCKED_STATUS_DELIVERY_UNBOUNDED_TIMEOUT = "BLOCKED_STATUS_DELIVERY_UNBOUNDED_TIMEOUT"
BLOCKED_STATUS_DELIVERY_UNSAFE_FLAGS = "BLOCKED_STATUS_DELIVERY_UNSAFE_FLAGS"

DEFAULT_INPUT_PATH = Path("data/runtime/copilot_handoff/latest_uploader_status_report_policy.json")
DEFAULT_LEDGER_PATH = Path("data/runtime/copilot_handoff/status_delivery_consistency_ledger.jsonl")
DEFAULT_JSON_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_status_delivery_consistency.json")
DEFAULT_TXT_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_status_delivery_consistency.txt")

MAX_ALLOWED_RETRY_COUNT = 3
MIN_TIMEOUT_SECONDS = 1
MAX_TIMEOUT_SECONDS = 120

FORBIDDEN_TRUE_FLAGS = frozenset(
    {
        "raw_conversation_text_available",
        "selenium_used",
        "webdriver_used",
        "browser_dom_automation_used",
        "cloudflare_bypass_attempted",
        "captcha_bypass_attempted",
        "conversation_text_logged",
        "random_page_click_performed",
    }
)


@dataclass(frozen=True)
class StatusDeliveryConsistencySafety:
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
class StatusDeliveryConsistencyResult:
    ok: bool
    result_label: str
    patch_name: str | None
    patch_result: str | None
    selected_action: str | None
    browser_lane: str | None
    status_chat_configured: bool
    pass_status_message: str | None
    pass_status_message_sha256: str | None
    exact_message_sha256: str | None
    selected_action_sha256: str | None
    operator_report_path: str | None
    operator_report_sha256: str | None
    computed_operator_report_sha256: str | None
    idempotency_key: str | None
    normalized_delivery_sha256: str | None
    retry_count: int | None
    timeout_seconds: int | None
    ledger_path: str
    ledger_appended: bool
    ledger_duplicate_seen: bool
    issues: tuple[str, ...]
    browser_action_performed: bool
    chatgpt_submit_performed: bool
    operator_report_uploaded: bool
    status_message_posted: bool
    send_button_pressed: bool
    file_upload_attempted: bool
    raw_conversation_text_available: bool
    selenium_used: bool
    webdriver_used: bool
    browser_dom_automation_used: bool
    cloudflare_bypass_attempted: bool
    captcha_bypass_attempted: bool
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    safety: StatusDeliveryConsistencySafety = field(default_factory=StatusDeliveryConsistencySafety)

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


def normalize_bool(value: Any, *, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on", "enabled", "configured"}:
        return True
    if text in {"0", "false", "no", "n", "off", "disabled"}:
        return False
    return default


def normalize_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    text = normalize_optional_text(value)
    if text is None:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return payload


def expected_pass_status_message(patch_name: str) -> str:
    return f"{patch_name} has passed"


def get_policy_mapping(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    policy = payload.get("policy")
    if isinstance(policy, Mapping):
        return policy
    return payload


def get_safety_mapping(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    safety = payload.get("safety")
    if isinstance(safety, Mapping):
        return safety
    return payload


def first_value(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def normalized_delivery_payload(
    *,
    patch_name: str | None,
    patch_result: str | None,
    selected_action: str | None,
    browser_lane: str | None,
    status_chat_configured: bool,
    pass_status_message: str | None,
    pass_status_message_sha256: str | None,
    exact_message_sha256: str | None,
    selected_action_sha256: str | None,
    operator_report_path: str | None,
    operator_report_sha256: str | None,
    retry_count: int | None,
    timeout_seconds: int | None,
) -> dict[str, Any]:
    return {
        "browser_lane": browser_lane,
        "exact_message_sha256": exact_message_sha256,
        "operator_report_path": operator_report_path,
        "operator_report_sha256": operator_report_sha256,
        "pass_status_message": pass_status_message,
        "pass_status_message_sha256": pass_status_message_sha256,
        "patch_name": patch_name,
        "patch_result": patch_result,
        "retry_count": retry_count,
        "selected_action": selected_action,
        "selected_action_sha256": selected_action_sha256,
        "status_chat_configured": status_chat_configured,
        "timeout_seconds": timeout_seconds,
    }


def compute_normalized_delivery_sha256(payload: Mapping[str, Any]) -> str:
    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256_text(normalized)


def compute_idempotency_key(*, patch_name: str, selected_action: str, browser_lane: str | None, normalized_delivery_sha256: str) -> str:
    lane = browser_lane or "none"
    return sha256_text(f"patchops-status-delivery-v1|{patch_name}|{selected_action}|{lane}|{normalized_delivery_sha256}")


def read_ledger_entries(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text:
            continue
        payload = json.loads(text)
        if not isinstance(payload, dict):
            raise ValueError(f"Invalid ledger line in {path}")
        entries.append(payload)
    return entries


def append_ledger_entry(path: Path, entry: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(entry), sort_keys=True, separators=(",", ":")) + "\n")


def build_result(
    *,
    ok: bool,
    result_label: str,
    patch_name: str | None,
    patch_result: str | None,
    selected_action: str | None,
    browser_lane: str | None,
    status_chat_configured: bool,
    pass_status_message: str | None,
    pass_status_message_sha256: str | None,
    exact_message_sha256: str | None,
    selected_action_sha256: str | None,
    operator_report_path: str | None,
    operator_report_sha256: str | None,
    computed_operator_report_sha256: str | None,
    idempotency_key: str | None,
    normalized_delivery_sha256: str | None,
    retry_count: int | None,
    timeout_seconds: int | None,
    ledger_path: Path,
    ledger_appended: bool,
    ledger_duplicate_seen: bool,
    issues: Sequence[str],
) -> StatusDeliveryConsistencyResult:
    safety = StatusDeliveryConsistencySafety()
    return StatusDeliveryConsistencyResult(
        ok=ok,
        result_label=result_label,
        patch_name=patch_name,
        patch_result=patch_result,
        selected_action=selected_action,
        browser_lane=browser_lane,
        status_chat_configured=status_chat_configured,
        pass_status_message=pass_status_message,
        pass_status_message_sha256=pass_status_message_sha256,
        exact_message_sha256=exact_message_sha256,
        selected_action_sha256=selected_action_sha256,
        operator_report_path=operator_report_path,
        operator_report_sha256=operator_report_sha256,
        computed_operator_report_sha256=computed_operator_report_sha256,
        idempotency_key=idempotency_key,
        normalized_delivery_sha256=normalized_delivery_sha256,
        retry_count=retry_count,
        timeout_seconds=timeout_seconds,
        ledger_path=str(ledger_path),
        ledger_appended=ledger_appended,
        ledger_duplicate_seen=ledger_duplicate_seen,
        issues=tuple(issues),
        browser_action_performed=safety.browser_action_performed,
        chatgpt_submit_performed=safety.chatgpt_submit_performed,
        operator_report_uploaded=safety.operator_report_uploaded,
        status_message_posted=safety.status_message_posted,
        send_button_pressed=safety.send_button_pressed,
        file_upload_attempted=safety.file_upload_attempted,
        raw_conversation_text_available=safety.raw_conversation_text_available,
        selenium_used=safety.selenium_used,
        webdriver_used=safety.webdriver_used,
        browser_dom_automation_used=safety.browser_dom_automation_used,
        cloudflare_bypass_attempted=safety.cloudflare_bypass_attempted,
        captcha_bypass_attempted=safety.captcha_bypass_attempted,
        safety=safety,
    )


def run_status_delivery_consistency_doctor(
    payload: Mapping[str, Any],
    *,
    ledger_path: Path = DEFAULT_LEDGER_PATH,
    retry_count_override: int | None = None,
    timeout_seconds_override: int | None = None,
    append_ledger: bool = True,
) -> StatusDeliveryConsistencyResult:
    policy = get_policy_mapping(payload)
    safety = get_safety_mapping(payload)

    patch_name = normalize_optional_text(first_value(policy.get("patch_name"), payload.get("patch_name")))
    patch_result = normalize_optional_text(first_value(policy.get("patch_result"), payload.get("patch_result")))
    selected_action = normalize_optional_text(first_value(policy.get("selected_action"), payload.get("selected_action")))
    browser_lane = normalize_optional_text(first_value(policy.get("browser_lane"), payload.get("browser_lane")))
    if browser_lane:
        browser_lane = browser_lane.lower()
    status_chat_configured = normalize_bool(first_value(policy.get("status_chat_configured"), payload.get("status_chat_configured")), default=False)
    pass_status_message = normalize_optional_text(first_value(policy.get("pass_status_message"), payload.get("pass_status_message")))
    operator_report_path = normalize_optional_text(first_value(policy.get("operator_report_path"), payload.get("operator_report_path")))
    operator_report_sha256 = normalize_optional_text(first_value(policy.get("operator_report_sha256"), payload.get("operator_report_sha256")))
    exact_message_sha256 = normalize_optional_text(first_value(policy.get("exact_message_sha256"), payload.get("exact_message_sha256")))
    selected_action_sha256 = normalize_optional_text(first_value(policy.get("selected_action_sha256"), payload.get("selected_action_sha256")))
    supplied_idempotency_key = normalize_optional_text(first_value(policy.get("idempotency_key"), payload.get("idempotency_key")))
    retry_count = retry_count_override if retry_count_override is not None else normalize_int(first_value(policy.get("retry_count"), payload.get("retry_count")))
    timeout_seconds = timeout_seconds_override if timeout_seconds_override is not None else normalize_int(first_value(policy.get("timeout_seconds"), payload.get("timeout_seconds")))
    if retry_count is None:
        retry_count = 1
    if timeout_seconds is None:
        timeout_seconds = 30

    base_kwargs = {
        "patch_name": patch_name,
        "patch_result": patch_result,
        "selected_action": selected_action,
        "browser_lane": browser_lane,
        "status_chat_configured": status_chat_configured,
        "pass_status_message": pass_status_message,
        "pass_status_message_sha256": sha256_text(pass_status_message) if pass_status_message else None,
        "exact_message_sha256": exact_message_sha256,
        "selected_action_sha256": selected_action_sha256,
        "operator_report_path": operator_report_path,
        "operator_report_sha256": operator_report_sha256,
        "computed_operator_report_sha256": None,
        "idempotency_key": supplied_idempotency_key,
        "normalized_delivery_sha256": None,
        "retry_count": retry_count,
        "timeout_seconds": timeout_seconds,
        "ledger_path": ledger_path,
        "ledger_appended": False,
        "ledger_duplicate_seen": False,
    }

    schema_issues: list[str] = []
    if not patch_name:
        schema_issues.append("patch_name is required")
    if selected_action not in ALLOWED_ACTIONS:
        schema_issues.append(f"selected_action must be one of {sorted(ALLOWED_ACTIONS)}")
    if selected_action in {ACTION_POST_STATUS_MESSAGE, ACTION_UPLOAD_OPERATOR_REPORT} and browser_lane not in ALLOWED_BROWSER_LANES:
        schema_issues.append("browser_lane must be chrome or edge for browser delivery actions")
    if selected_action == ACTION_RECORD_PASS_LOCALLY_NO_UPLOAD and browser_lane not in {None, "", "chrome", "edge"}:
        schema_issues.append("record_pass_locally_no_upload may omit browser_lane or carry a named lane only")
    if selected_action in {ACTION_POST_STATUS_MESSAGE, ACTION_RECORD_PASS_LOCALLY_NO_UPLOAD} and patch_name:
        expected_message = expected_pass_status_message(patch_name)
        if pass_status_message != expected_message:
            schema_issues.append("pass_status_message must exactly equal '<patch_name> has passed'")
    if selected_action == ACTION_UPLOAD_OPERATOR_REPORT and not operator_report_path:
        schema_issues.append("operator_report_path is required for upload_operator_report")
    if schema_issues:
        return build_result(ok=False, result_label=BLOCKED_STATUS_DELIVERY_SCHEMA_INVALID, issues=schema_issues, **base_kwargs)

    if retry_count < 0 or retry_count > MAX_ALLOWED_RETRY_COUNT:
        return build_result(
            ok=False,
            result_label=BLOCKED_STATUS_DELIVERY_UNBOUNDED_RETRY,
            issues=(f"retry_count must be between 0 and {MAX_ALLOWED_RETRY_COUNT}",),
            **base_kwargs,
        )
    if timeout_seconds < MIN_TIMEOUT_SECONDS or timeout_seconds > MAX_TIMEOUT_SECONDS:
        return build_result(
            ok=False,
            result_label=BLOCKED_STATUS_DELIVERY_UNBOUNDED_TIMEOUT,
            issues=(f"timeout_seconds must be between {MIN_TIMEOUT_SECONDS} and {MAX_TIMEOUT_SECONDS}",),
            **base_kwargs,
        )

    unsafe_flags = [flag for flag in sorted(FORBIDDEN_TRUE_FLAGS) if normalize_bool(safety.get(flag), default=False)]
    if unsafe_flags:
        return build_result(
            ok=False,
            result_label=BLOCKED_STATUS_DELIVERY_UNSAFE_FLAGS,
            issues=tuple(f"forbidden safety flag was true: {flag}" for flag in unsafe_flags),
            **base_kwargs,
        )

    computed_report_sha: str | None = None
    if selected_action == ACTION_UPLOAD_OPERATOR_REPORT and operator_report_path:
        report_path = Path(operator_report_path)
        if not report_path.exists() or not report_path.is_file():
            return build_result(
                ok=False,
                result_label=BLOCKED_STATUS_DELIVERY_SCHEMA_INVALID,
                issues=(f"operator_report_path was not found: {operator_report_path}",),
                **base_kwargs,
            )
        computed_report_sha = sha256_file(report_path)
        if operator_report_sha256 and operator_report_sha256 != computed_report_sha:
            base_kwargs["computed_operator_report_sha256"] = computed_report_sha
            return build_result(
                ok=False,
                result_label=BLOCKED_STATUS_DELIVERY_HASH_MISMATCH,
                issues=("operator_report_sha256 does not match operator_report_path",),
                **base_kwargs,
            )
        operator_report_sha256 = computed_report_sha

    computed_pass_sha = sha256_text(pass_status_message) if pass_status_message else None
    computed_action_sha = sha256_text(selected_action) if selected_action else None
    hash_issues: list[str] = []
    if exact_message_sha256 and computed_pass_sha and exact_message_sha256 != computed_pass_sha:
        hash_issues.append("exact_message_sha256 does not match pass_status_message")
    if selected_action_sha256 and computed_action_sha and selected_action_sha256 != computed_action_sha:
        hash_issues.append("selected_action_sha256 does not match selected_action")
    if hash_issues:
        base_kwargs.update(
            {
                "pass_status_message_sha256": computed_pass_sha,
                "selected_action_sha256": selected_action_sha256,
                "operator_report_sha256": operator_report_sha256,
                "computed_operator_report_sha256": computed_report_sha,
            }
        )
        return build_result(ok=False, result_label=BLOCKED_STATUS_DELIVERY_HASH_MISMATCH, issues=hash_issues, **base_kwargs)

    exact_message_sha256 = exact_message_sha256 or computed_pass_sha
    selected_action_sha256 = selected_action_sha256 or computed_action_sha
    normalized_payload = normalized_delivery_payload(
        patch_name=patch_name,
        patch_result=patch_result,
        selected_action=selected_action,
        browser_lane=browser_lane,
        status_chat_configured=status_chat_configured,
        pass_status_message=pass_status_message,
        pass_status_message_sha256=computed_pass_sha,
        exact_message_sha256=exact_message_sha256,
        selected_action_sha256=selected_action_sha256,
        operator_report_path=operator_report_path,
        operator_report_sha256=operator_report_sha256,
        retry_count=retry_count,
        timeout_seconds=timeout_seconds,
    )
    normalized_sha = compute_normalized_delivery_sha256(normalized_payload)
    computed_idempotency_key = compute_idempotency_key(
        patch_name=patch_name or "",
        selected_action=selected_action or "",
        browser_lane=browser_lane,
        normalized_delivery_sha256=normalized_sha,
    )
    if supplied_idempotency_key and supplied_idempotency_key != computed_idempotency_key:
        return build_result(
            ok=False,
            result_label=BLOCKED_STATUS_DELIVERY_HASH_MISMATCH,
            patch_name=patch_name,
            patch_result=patch_result,
            selected_action=selected_action,
            browser_lane=browser_lane,
            status_chat_configured=status_chat_configured,
            pass_status_message=pass_status_message,
            pass_status_message_sha256=computed_pass_sha,
            exact_message_sha256=exact_message_sha256,
            selected_action_sha256=selected_action_sha256,
            operator_report_path=operator_report_path,
            operator_report_sha256=operator_report_sha256,
            computed_operator_report_sha256=computed_report_sha,
            idempotency_key=computed_idempotency_key,
            normalized_delivery_sha256=normalized_sha,
            retry_count=retry_count,
            timeout_seconds=timeout_seconds,
            ledger_path=ledger_path,
            ledger_appended=False,
            ledger_duplicate_seen=False,
            issues=("supplied idempotency_key does not match normalized delivery payload",),
        )

    entries = read_ledger_entries(ledger_path)
    duplicate_seen = False
    for entry in entries:
        if entry.get("idempotency_key") == computed_idempotency_key:
            duplicate_seen = True
            if entry.get("normalized_delivery_sha256") != normalized_sha:
                return build_result(
                    ok=False,
                    result_label=BLOCKED_STATUS_DELIVERY_IDEMPOTENCY_CONFLICT,
                    patch_name=patch_name,
                    patch_result=patch_result,
                    selected_action=selected_action,
                    browser_lane=browser_lane,
                    status_chat_configured=status_chat_configured,
                    pass_status_message=pass_status_message,
                    pass_status_message_sha256=computed_pass_sha,
                    exact_message_sha256=exact_message_sha256,
                    selected_action_sha256=selected_action_sha256,
                    operator_report_path=operator_report_path,
                    operator_report_sha256=operator_report_sha256,
                    computed_operator_report_sha256=computed_report_sha,
                    idempotency_key=computed_idempotency_key,
                    normalized_delivery_sha256=normalized_sha,
                    retry_count=retry_count,
                    timeout_seconds=timeout_seconds,
                    ledger_path=ledger_path,
                    ledger_appended=False,
                    ledger_duplicate_seen=True,
                    issues=("idempotency key already exists with different normalized delivery hash",),
                )

    ledger_appended = False
    if append_ledger and not duplicate_seen:
        append_ledger_entry(
            ledger_path,
            {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "patch_name": patch_name,
                "patch_result": patch_result,
                "selected_action": selected_action,
                "browser_lane": browser_lane,
                "idempotency_key": computed_idempotency_key,
                "normalized_delivery_sha256": normalized_sha,
                "exact_message_sha256": exact_message_sha256,
                "selected_action_sha256": selected_action_sha256,
                "operator_report_sha256": operator_report_sha256,
                "retry_count": retry_count,
                "timeout_seconds": timeout_seconds,
            },
        )
        ledger_appended = True

    return build_result(
        ok=True,
        result_label=PASS_STATUS_DELIVERY_CONSISTENCY_HARDENED,
        patch_name=patch_name,
        patch_result=patch_result,
        selected_action=selected_action,
        browser_lane=browser_lane,
        status_chat_configured=status_chat_configured,
        pass_status_message=pass_status_message,
        pass_status_message_sha256=computed_pass_sha,
        exact_message_sha256=exact_message_sha256,
        selected_action_sha256=selected_action_sha256,
        operator_report_path=operator_report_path,
        operator_report_sha256=operator_report_sha256,
        computed_operator_report_sha256=computed_report_sha,
        idempotency_key=computed_idempotency_key,
        normalized_delivery_sha256=normalized_sha,
        retry_count=retry_count,
        timeout_seconds=timeout_seconds,
        ledger_path=ledger_path,
        ledger_appended=ledger_appended,
        ledger_duplicate_seen=duplicate_seen,
        issues=(),
    )


def render_text(result: StatusDeliveryConsistencyResult) -> str:
    lines = [
        f"result_label: {result.result_label}",
        f"ok: {str(result.ok).lower()}",
        f"patch_name: {result.patch_name}",
        f"patch_result: {result.patch_result}",
        f"selected_action: {result.selected_action}",
        f"browser_lane: {result.browser_lane}",
        f"status_chat_configured: {str(result.status_chat_configured).lower()}",
        f"pass_status_message: {result.pass_status_message}",
        f"pass_status_message_sha256: {result.pass_status_message_sha256}",
        f"exact_message_sha256: {result.exact_message_sha256}",
        f"selected_action_sha256: {result.selected_action_sha256}",
        f"operator_report_path: {result.operator_report_path}",
        f"operator_report_sha256: {result.operator_report_sha256}",
        f"computed_operator_report_sha256: {result.computed_operator_report_sha256}",
        f"idempotency_key: {result.idempotency_key}",
        f"normalized_delivery_sha256: {result.normalized_delivery_sha256}",
        f"retry_count: {result.retry_count}",
        f"timeout_seconds: {result.timeout_seconds}",
        f"ledger_path: {result.ledger_path}",
        f"ledger_appended: {str(result.ledger_appended).lower()}",
        f"ledger_duplicate_seen: {str(result.ledger_duplicate_seen).lower()}",
        f"browser_action_performed: {str(result.browser_action_performed).lower()}",
        f"chatgpt_submit_performed: {str(result.chatgpt_submit_performed).lower()}",
        f"operator_report_uploaded: {str(result.operator_report_uploaded).lower()}",
        f"status_message_posted: {str(result.status_message_posted).lower()}",
        f"send_button_pressed: {str(result.send_button_pressed).lower()}",
        f"file_upload_attempted: {str(result.file_upload_attempted).lower()}",
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


def write_consistency_evidence(
    result: StatusDeliveryConsistencyResult,
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
    parser = argparse.ArgumentParser(description="PatchOps uploader status delivery consistency hardening doctor")
    parser.add_argument("--input-path", default=str(DEFAULT_INPUT_PATH))
    parser.add_argument("--patch-name", default=None)
    parser.add_argument("--patch-result", default=None)
    parser.add_argument("--selected-action", default=None)
    parser.add_argument("--browser-lane", default=None)
    parser.add_argument("--status-chat-configured", action="store_true")
    parser.add_argument("--pass-status-message", default=None)
    parser.add_argument("--operator-report-path", default=None)
    parser.add_argument("--operator-report-sha256", default=None)
    parser.add_argument("--retry-count", type=int, default=None)
    parser.add_argument("--timeout-seconds", type=int, default=None)
    parser.add_argument("--ledger-path", default=str(DEFAULT_LEDGER_PATH))
    parser.add_argument("--json-output-path", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--txt-output-path", default=str(DEFAULT_TXT_OUTPUT_PATH))
    parser.add_argument("--no-append-ledger", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    return parser


def _payload_from_args(args: argparse.Namespace) -> Mapping[str, Any]:
    explicit = any(
        value is not None
        for value in (
            args.patch_name,
            args.patch_result,
            args.selected_action,
            args.browser_lane,
            args.pass_status_message,
            args.operator_report_path,
            args.operator_report_sha256,
        )
    ) or bool(args.status_chat_configured)
    input_path = Path(args.input_path) if args.input_path else None
    if not explicit and input_path and input_path.exists():
        return load_json_object(input_path)
    return {
        "patch_name": args.patch_name,
        "patch_result": args.patch_result,
        "selected_action": args.selected_action,
        "browser_lane": args.browser_lane,
        "status_chat_configured": bool(args.status_chat_configured),
        "pass_status_message": args.pass_status_message,
        "operator_report_path": args.operator_report_path,
        "operator_report_sha256": args.operator_report_sha256,
        "retry_count": args.retry_count,
        "timeout_seconds": args.timeout_seconds,
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_status_delivery_consistency_doctor(
        _payload_from_args(args),
        ledger_path=Path(args.ledger_path),
        retry_count_override=args.retry_count,
        timeout_seconds_override=args.timeout_seconds,
        append_ledger=not args.no_append_ledger,
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