from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


FORBIDDEN_SUBMISSION_KEYS = (
    "chatgpt_submit_performed",
    "message_submitted",
    "prompt_submitted",
    "send_button_clicked",
    "submit_button_clicked",
    "send_hotkey_pressed",
    "ctrl_enter_sent",
    "enter_sent_to_chat_input",
    "conversation_text_logged",
    "browser_dom_automation_used",
    "webdriver_used",
    "selenium_used",
)

ALLOWED_ENTER_KEYS = (
    "picker_enter_pressed",
    "enter_pressed_once",
)


@dataclass(frozen=True)
class SubmissionGuardViolation:
    path: str
    key: str
    value: Any

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SubmissionGuardResult:
    status: str
    result: str
    result_label: str
    submission_blocker_passed: bool
    violation_count: int
    first_violation_path: str
    first_violation_key: str
    recommended_next_mode: str
    checked_payload_count: int
    checked_queue_item_count: int
    chatgpt_submit_performed: bool
    conversation_text_logged: bool
    selenium_used: bool
    webdriver_used: bool
    browser_dom_automation_used: bool
    violations: tuple[SubmissionGuardViolation, ...]

    def to_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["violations"] = [v.to_payload() for v in self.violations]
        return payload


def _truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _walk_payload(value: Any, path: str = "$") -> list[tuple[str, str, Any]]:
    found: list[tuple[str, str, Any]] = []

    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if key_text in FORBIDDEN_SUBMISSION_KEYS and _truthy(item):
                found.append((child_path, key_text, item))
            found.extend(_walk_payload(item, child_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(_walk_payload(item, f"{path}[{index}]"))

    return found


def evaluate_submission_blocker(payload: dict[str, Any]) -> SubmissionGuardResult:
    payload = dict(payload or {})
    violations = tuple(
        SubmissionGuardViolation(path=path, key=key, value=value)
        for path, key, value in _walk_payload(payload)
    )

    queue_items = payload.get("queue_items")
    item_results = payload.get("item_results")

    checked_queue_count = len(queue_items) if isinstance(queue_items, list) else 0
    checked_payload_count = 1 + (len(item_results) if isinstance(item_results, list) else 0)

    if violations:
        first = violations[0]
        return SubmissionGuardResult(
            status="FAIL_FORBIDDEN_SUBMISSION_SIDE_EFFECT",
            result="FAIL_U2_7G_FORBIDDEN_SUBMISSION_SIDE_EFFECT",
            result_label="FAIL_U2_7G_FORBIDDEN_SUBMISSION_SIDE_EFFECT",
            submission_blocker_passed=False,
            violation_count=len(violations),
            first_violation_path=first.path,
            first_violation_key=first.key,
            recommended_next_mode="stop_and_repair_submission_guard_before_any_more_live_uploads",
            checked_payload_count=checked_payload_count,
            checked_queue_item_count=checked_queue_count,
            chatgpt_submit_performed=True,
            conversation_text_logged=any(v.key == "conversation_text_logged" for v in violations),
            selenium_used=any(v.key == "selenium_used" for v in violations),
            webdriver_used=any(v.key == "webdriver_used" for v in violations),
            browser_dom_automation_used=any(v.key == "browser_dom_automation_used" for v in violations),
            violations=violations,
        )

    return SubmissionGuardResult(
        status="PASS",
        result="PASS_U2_7G_SUBMISSION_BLOCKED_QUEUE_SAFE",
        result_label="PASS_U2_7G_SUBMISSION_BLOCKED_QUEUE_SAFE",
        submission_blocker_passed=True,
        violation_count=0,
        first_violation_path="",
        first_violation_key="",
        recommended_next_mode="continue_to_downloader_foundation_or_live_single_upload_operator_gate",
        checked_payload_count=checked_payload_count,
        checked_queue_item_count=checked_queue_count,
        chatgpt_submit_performed=False,
        conversation_text_logged=False,
        selenium_used=False,
        webdriver_used=False,
        browser_dom_automation_used=False,
        violations=tuple(),
    )


def load_payload(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("submission guard payload must be a JSON object")
    return data


def write_submission_guard_evidence(evidence_dir: str | Path, payload: dict[str, Any]) -> tuple[Path, Path]:
    out_dir = Path(evidence_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "u2_7g_submission_blocker.json"
    txt_path = out_dir / "u2_7g_submission_blocker.txt"

    payload = dict(payload)
    payload["json_evidence"] = str(json_path)
    payload["txt_evidence"] = str(txt_path)

    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")

    lines = [
        "PATCHOPS U2.7G QUEUE SUBMISSION BLOCKER",
        "=======================================",
        f"PATCHOPS_U2_7G_STATUS: {payload.get('status', '')}",
        f"RESULT: {payload.get('result', '')}",
        f"RESULT_LABEL: {payload.get('result_label', '')}",
        f"JSON_EVIDENCE: {json_path}",
        f"TXT_EVIDENCE: {txt_path}",
        f"SUBMISSION_BLOCKER_PASSED: {str(payload.get('submission_blocker_passed', False)).lower()}",
        f"VIOLATION_COUNT: {payload.get('violation_count', 0)}",
        f"FIRST_VIOLATION_PATH: {payload.get('first_violation_path', '')}",
        f"FIRST_VIOLATION_KEY: {payload.get('first_violation_key', '')}",
        f"CHECKED_PAYLOAD_COUNT: {payload.get('checked_payload_count', 0)}",
        f"CHECKED_QUEUE_ITEM_COUNT: {payload.get('checked_queue_item_count', 0)}",
        f"RECOMMENDED_NEXT_MODE: {payload.get('recommended_next_mode', '')}",
        "CHATGPT_SUBMIT_PERFORMED: false",
        "CONVERSATION_TEXT_LOGGED: false",
        "SELENIUM_USED: false",
        "WEBDRIVER_USED: false",
        "BROWSER_DOM_AUTOMATION_USED: false",
        "",
    ]
    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, txt_path
