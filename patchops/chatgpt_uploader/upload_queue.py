from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


FORBIDDEN_TRUE_KEYS = (
    "chatgpt_submit_performed",
    "conversation_text_logged",
    "selenium_used",
    "webdriver_used",
    "browser_dom_automation_used",
    "random_page_click_performed",
)


@dataclass(frozen=True)
class UploadQueueItem:
    index: int
    report_path: str
    report_name: str
    report_exists: bool
    report_size_bytes: int
    report_sha256: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class QueueSelection:
    original_queue_item_count: int
    queue_item_count: int
    skipped_queue_item_count: int
    multi_upload_allowed: bool
    effective_max_items: int
    items: tuple[UploadQueueItem, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "original_queue_item_count": self.original_queue_item_count,
            "queue_item_count": self.queue_item_count,
            "skipped_queue_item_count": self.skipped_queue_item_count,
            "multi_upload_allowed": self.multi_upload_allowed,
            "effective_max_items": self.effective_max_items,
            "items": [item.to_payload() for item in self.items],
        }


@dataclass(frozen=True)
class RepeatabilitySummary:
    status: str
    result: str
    result_label: str
    queue_item_count: int
    pass_count: int
    blocked_count: int
    forbidden_count: int
    first_failure_index: int | None
    first_failure_layer: str
    recommended_next_mode: str
    chatgpt_submit_performed: bool
    conversation_text_logged: bool
    selenium_used: bool
    webdriver_used: bool
    browser_dom_automation_used: bool
    random_page_click_performed: bool

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def sha256_file(path: str | Path) -> str:
    p = Path(path)
    if not p.exists() or not p.is_file():
        return ""
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build_upload_queue(report_paths: Iterable[str | Path]) -> list[UploadQueueItem]:
    queue: list[UploadQueueItem] = []
    for index, raw_path in enumerate(report_paths, start=1):
        path = Path(raw_path).expanduser().resolve()
        queue.append(
            UploadQueueItem(
                index=index,
                report_path=str(path),
                report_name=path.name,
                report_exists=path.exists() and path.is_file(),
                report_size_bytes=path.stat().st_size if path.exists() and path.is_file() else 0,
                report_sha256=sha256_file(path),
            )
        )
    return queue


def select_queue_items(
    queue: Iterable[UploadQueueItem],
    *,
    allow_multi_upload: bool = False,
    max_items: int | None = None,
) -> QueueSelection:
    items = list(queue)
    original_count = len(items)

    if max_items is not None and int(max_items) <= 0:
        raise ValueError("max_items must be a positive integer when provided")

    if allow_multi_upload:
        effective_max = int(max_items) if max_items is not None else original_count
    else:
        effective_max = 1 if max_items is None else min(1, int(max_items))

    selected = tuple(items[:effective_max])
    skipped = max(0, original_count - len(selected))

    return QueueSelection(
        original_queue_item_count=original_count,
        queue_item_count=len(selected),
        skipped_queue_item_count=skipped,
        multi_upload_allowed=bool(allow_multi_upload),
        effective_max_items=effective_max,
        items=selected,
    )


def write_queue_file(queue: Iterable[UploadQueueItem], path: str | Path) -> Path:
    out = Path(path).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps([item.to_payload() for item in queue], indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return out


def read_queue_file(path: str | Path) -> list[UploadQueueItem]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("queue file must contain a list")
    out: list[UploadQueueItem] = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("queue item must be an object")
        out.append(
            UploadQueueItem(
                index=int(item.get("index") or len(out) + 1),
                report_path=str(item.get("report_path") or ""),
                report_name=str(item.get("report_name") or Path(str(item.get("report_path") or "")).name),
                report_exists=bool(item.get("report_exists")),
                report_size_bytes=int(item.get("report_size_bytes") or 0),
                report_sha256=str(item.get("report_sha256") or ""),
            )
        )
    return out


def has_forbidden_side_effect(payload: dict[str, Any]) -> bool:
    return any(bool(payload.get(key)) for key in FORBIDDEN_TRUE_KEYS)


def classify_repeatability_results(item_results: Iterable[dict[str, Any]]) -> RepeatabilitySummary:
    results = list(item_results)
    pass_count = 0
    blocked_count = 0
    forbidden_count = 0
    first_failure_index: int | None = None
    first_failure_layer = ""
    recommended_next_mode = "continue_to_queue_submission_blocker_or_downloader_foundation"

    for i, payload in enumerate(results, start=1):
        if has_forbidden_side_effect(payload):
            forbidden_count += 1
            if first_failure_index is None:
                first_failure_index = i
                first_failure_layer = str(payload.get("failure_layer") or "forbidden_side_effect")
                recommended_next_mode = "stop_and_repair_forbidden_side_effect_guard"
            continue

        status = str(payload.get("status") or "")
        result = str(payload.get("result") or "")

        if status == "PASS" and (
            result == "PASS_ATTACHMENT_READY_NO_SEND_HARDENED"
            or result == "PASS_EXISTING_TARGET_UPLOAD_ATTACHED_NO_SEND"
            or "ATTACHMENT_READY" in result
        ):
            pass_count += 1
        else:
            blocked_count += 1
            if first_failure_index is None:
                first_failure_index = i
                first_failure_layer = str(payload.get("failure_layer") or "unknown_blocked_layer")
                recommended_next_mode = str(payload.get("recommended_next_mode") or "patch_first_repeatability_failure")

    if forbidden_count:
        status = "FAIL_FORBIDDEN_SIDE_EFFECT"
        result = "FAIL_U2_7E_FORBIDDEN_SIDE_EFFECT"
        result_label = "FAIL_U2_7E_FORBIDDEN_SIDE_EFFECT"
    elif results and pass_count == len(results):
        status = "PASS"
        result = "PASS_U2_7E_REPEATABILITY_QUEUE_READY_NO_SEND"
        result_label = "PASS_U2_7E_REPEATABILITY_QUEUE_READY_NO_SEND"
        first_failure_layer = ""
        recommended_next_mode = "continue_to_queue_submission_blocker_or_downloader_foundation"
    else:
        status = "PASS_OR_BLOCKED"
        result = "PASS_OR_BLOCKED_U2_7E_FIRST_REPEATABILITY_LAYER_CLASSIFIED"
        result_label = "PASS_OR_BLOCKED_U2_7E_FIRST_REPEATABILITY_LAYER_CLASSIFIED"

    return RepeatabilitySummary(
        status=status,
        result=result,
        result_label=result_label,
        queue_item_count=len(results),
        pass_count=pass_count,
        blocked_count=blocked_count,
        forbidden_count=forbidden_count,
        first_failure_index=first_failure_index,
        first_failure_layer=first_failure_layer,
        recommended_next_mode=recommended_next_mode,
        chatgpt_submit_performed=any(bool(p.get("chatgpt_submit_performed")) for p in results),
        conversation_text_logged=any(bool(p.get("conversation_text_logged")) for p in results),
        selenium_used=any(bool(p.get("selenium_used")) for p in results),
        webdriver_used=any(bool(p.get("webdriver_used")) for p in results),
        browser_dom_automation_used=any(bool(p.get("browser_dom_automation_used")) for p in results),
        random_page_click_performed=any(bool(p.get("random_page_click_performed")) for p in results),
    )


def write_repeatability_evidence(evidence_dir: str | Path, payload: dict[str, Any]) -> tuple[Path, Path]:
    out_dir = Path(evidence_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "u2_7e_repeatability_queue_foundation.json"
    txt_path = out_dir / "u2_7e_repeatability_queue_foundation.txt"

    payload = dict(payload)
    payload["json_evidence"] = str(json_path)
    payload["txt_evidence"] = str(txt_path)

    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")

    lines = [
        "PATCHOPS U2.7E REPEATABILITY QUEUE FOUNDATION",
        "=============================================",
        f"PATCHOPS_U2_7E_STATUS: {payload.get('status', '')}",
        f"RESULT: {payload.get('result', '')}",
        f"RESULT_LABEL: {payload.get('result_label', '')}",
        f"JSON_EVIDENCE: {json_path}",
        f"TXT_EVIDENCE: {txt_path}",
        f"QUEUE_FILE: {payload.get('queue_file', '')}",
        f"ORIGINAL_QUEUE_ITEM_COUNT: {payload.get('original_queue_item_count', payload.get('queue_item_count', 0))}",
        f"QUEUE_ITEM_COUNT: {payload.get('queue_item_count', 0)}",
        f"SKIPPED_QUEUE_ITEM_COUNT: {payload.get('skipped_queue_item_count', 0)}",
        f"MULTI_UPLOAD_ALLOWED: {str(payload.get('multi_upload_allowed', False)).lower()}",
        f"EFFECTIVE_MAX_ITEMS: {payload.get('effective_max_items', '')}",
        f"PASS_COUNT: {payload.get('pass_count', 0)}",
        f"BLOCKED_COUNT: {payload.get('blocked_count', 0)}",
        f"FORBIDDEN_COUNT: {payload.get('forbidden_count', 0)}",
        f"FIRST_FAILURE_INDEX: {payload.get('first_failure_index', '')}",
        f"FIRST_FAILURE_LAYER: {payload.get('first_failure_layer', '')}",
        f"RECOMMENDED_NEXT_MODE: {payload.get('recommended_next_mode', '')}",
        "CHATGPT_SUBMIT_PERFORMED: false",
        "CONVERSATION_TEXT_LOGGED: false",
        "SELENIUM_USED: false",
        "WEBDRIVER_USED: false",
        "BROWSER_DOM_AUTOMATION_USED: false",
        "RANDOM_PAGE_CLICK_PERFORMED: false",
        "",
    ]
    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, txt_path
