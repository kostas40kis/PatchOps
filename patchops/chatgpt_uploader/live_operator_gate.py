from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


CONFIRMATION_TOKEN = "UPLOAD_ONE_ATTACHMENT_NO_SEND"


@dataclass(frozen=True)
class LiveSingleUploadGateResult:
    live_single_upload_allowed: bool
    gate_status: str
    gate_result: str
    gate_failure_layer: str
    recommended_next_mode: str
    report_path_count: int
    selected_report_path: str
    selected_report_exists: bool
    selected_report_size_bytes: int
    allow_live_single_upload: bool
    operator_confirmation_valid: bool
    expected_confirmation_token: str
    multi_upload_blocked: bool
    chatgpt_submit_performed: bool = False
    conversation_text_logged: bool = False
    selenium_used: bool = False
    webdriver_used: bool = False
    browser_dom_automation_used: bool = False
    random_page_click_performed: bool = False

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def validate_live_single_upload_request(
    report_paths: Iterable[str | Path],
    *,
    allow_live_single_upload: bool = False,
    operator_confirm: str = "",
    confirmation_token: str = CONFIRMATION_TOKEN,
) -> LiveSingleUploadGateResult:
    paths = [Path(path).expanduser().resolve() for path in report_paths]
    selected = paths[0] if paths else Path("")

    if len(paths) != 1:
        return LiveSingleUploadGateResult(
            live_single_upload_allowed=False,
            gate_status="PASS_OR_BLOCKED",
            gate_result="BLOCKED_LIVE_SINGLE_UPLOAD_REQUIRES_EXACTLY_ONE_REPORT",
            gate_failure_layer="exactly_one_report_required",
            recommended_next_mode="provide_exactly_one_report_path_or_use_u2_7e_queue_with_explicit_multi_upload",
            report_path_count=len(paths),
            selected_report_path=str(selected) if paths else "",
            selected_report_exists=selected.exists() and selected.is_file() if paths else False,
            selected_report_size_bytes=selected.stat().st_size if paths and selected.exists() and selected.is_file() else 0,
            allow_live_single_upload=bool(allow_live_single_upload),
            operator_confirmation_valid=False,
            expected_confirmation_token=confirmation_token,
            multi_upload_blocked=len(paths) > 1,
        )

    if not selected.exists() or not selected.is_file() or selected.stat().st_size <= 0:
        return LiveSingleUploadGateResult(
            live_single_upload_allowed=False,
            gate_status="PASS_OR_BLOCKED",
            gate_result="BLOCKED_LIVE_SINGLE_UPLOAD_REPORT_UNAVAILABLE",
            gate_failure_layer="report_unavailable",
            recommended_next_mode="provide_existing_nonempty_report_path",
            report_path_count=1,
            selected_report_path=str(selected),
            selected_report_exists=selected.exists() and selected.is_file(),
            selected_report_size_bytes=selected.stat().st_size if selected.exists() and selected.is_file() else 0,
            allow_live_single_upload=bool(allow_live_single_upload),
            operator_confirmation_valid=False,
            expected_confirmation_token=confirmation_token,
            multi_upload_blocked=False,
        )

    if not allow_live_single_upload:
        return LiveSingleUploadGateResult(
            live_single_upload_allowed=False,
            gate_status="PASS_OR_BLOCKED",
            gate_result="BLOCKED_LIVE_SINGLE_UPLOAD_FLAG_REQUIRED",
            gate_failure_layer="allow_live_single_upload_flag_missing",
            recommended_next_mode="rerun_with_allow_live_single_upload_and_exact_operator_confirmation",
            report_path_count=1,
            selected_report_path=str(selected),
            selected_report_exists=True,
            selected_report_size_bytes=selected.stat().st_size,
            allow_live_single_upload=False,
            operator_confirmation_valid=False,
            expected_confirmation_token=confirmation_token,
            multi_upload_blocked=False,
        )

    confirmation_ok = str(operator_confirm or "").strip() == confirmation_token
    if not confirmation_ok:
        return LiveSingleUploadGateResult(
            live_single_upload_allowed=False,
            gate_status="PASS_OR_BLOCKED",
            gate_result="BLOCKED_LIVE_SINGLE_UPLOAD_CONFIRMATION_REQUIRED",
            gate_failure_layer="operator_confirmation_missing_or_invalid",
            recommended_next_mode="rerun_with_operator_confirm_upload_one_attachment_no_send",
            report_path_count=1,
            selected_report_path=str(selected),
            selected_report_exists=True,
            selected_report_size_bytes=selected.stat().st_size,
            allow_live_single_upload=True,
            operator_confirmation_valid=False,
            expected_confirmation_token=confirmation_token,
            multi_upload_blocked=False,
        )

    return LiveSingleUploadGateResult(
        live_single_upload_allowed=True,
        gate_status="PASS",
        gate_result="PASS_LIVE_SINGLE_UPLOAD_OPERATOR_GATE_OPEN",
        gate_failure_layer="",
        recommended_next_mode="run_single_upload_then_submission_blocker",
        report_path_count=1,
        selected_report_path=str(selected),
        selected_report_exists=True,
        selected_report_size_bytes=selected.stat().st_size,
        allow_live_single_upload=True,
        operator_confirmation_valid=True,
        expected_confirmation_token=confirmation_token,
        multi_upload_blocked=False,
    )


def write_live_operator_gate_evidence(evidence_dir: str | Path, payload: dict[str, Any]) -> tuple[Path, Path]:
    out_dir = Path(evidence_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "u2_7h_live_single_upload_operator_gate.json"
    txt_path = out_dir / "u2_7h_live_single_upload_operator_gate.txt"

    payload = dict(payload)
    payload["json_evidence"] = str(json_path)
    payload["txt_evidence"] = str(txt_path)

    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")

    lines = [
        "PATCHOPS U2.7H LIVE SINGLE-UPLOAD OPERATOR GATE",
        "================================================",
        f"PATCHOPS_U2_7H_STATUS: {payload.get('status', '')}",
        f"RESULT: {payload.get('result', '')}",
        f"RESULT_LABEL: {payload.get('result_label', '')}",
        f"JSON_EVIDENCE: {json_path}",
        f"TXT_EVIDENCE: {txt_path}",
        f"LIVE_SINGLE_UPLOAD_ALLOWED: {str(payload.get('live_single_upload_allowed', False)).lower()}",
        f"REPORT_PATH_COUNT: {payload.get('report_path_count', 0)}",
        f"SELECTED_REPORT_PATH: {payload.get('selected_report_path', '')}",
        f"ALLOW_LIVE_SINGLE_UPLOAD: {str(payload.get('allow_live_single_upload', False)).lower()}",
        f"OPERATOR_CONFIRMATION_VALID: {str(payload.get('operator_confirmation_valid', False)).lower()}",
        f"EXPECTED_CONFIRMATION_TOKEN: {payload.get('expected_confirmation_token', '')}",
        f"MULTI_UPLOAD_BLOCKED: {str(payload.get('multi_upload_blocked', False)).lower()}",
        f"SUBMISSION_BLOCKER_PASSED: {str(payload.get('submission_blocker_passed', False)).lower()}",
        f"QUEUE_ITEM_COUNT: {payload.get('queue_item_count', 0)}",
        f"SKIPPED_QUEUE_ITEM_COUNT: {payload.get('skipped_queue_item_count', 0)}",
        f"FAILURE_LAYER: {payload.get('failure_layer', '')}",
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
