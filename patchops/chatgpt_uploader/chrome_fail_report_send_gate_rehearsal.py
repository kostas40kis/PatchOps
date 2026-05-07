from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH_NAME = "clu_05_chrome_fail_report_send_gate_rehearsal"
ACTION_UPLOAD_OPERATOR_REPORT = "upload_operator_report"
CONFIRM_CHROME_FAIL_REPORT_SEND_GATE_REHEARSAL = "PATCHOPS_CONFIRM_CHROME_FAIL_REPORT_SEND_GATE_REHEARSAL"
CONFIRM_CHROME_FAIL_REPORT_SEND = "PATCHOPS_CONFIRM_CHROME_FAIL_REPORT_SEND"

PASS_CHROME_FAIL_REPORT_SEND_GATE_READY = "PASS_CHROME_FAIL_REPORT_SEND_GATE_READY"
BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_CONFIRMATION_REQUIRED = "BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_CONFIRMATION_REQUIRED"
BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_CONFIRMATION_MISMATCH = "BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_CONFIRMATION_MISMATCH"
BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_EVIDENCE_MISSING = "BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_EVIDENCE_MISSING"
BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_EVIDENCE_INVALID = "BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_EVIDENCE_INVALID"
BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_HASH_MISMATCH = "BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_HASH_MISMATCH"
BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_ATTACHMENT_MISSING = "BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_ATTACHMENT_MISSING"
BLOCKED_SEND_RISK = "BLOCKED_SEND_RISK"

DEFAULT_CONSISTENCY_EVIDENCE_PATH = Path("data/runtime/copilot_handoff/latest_chrome_operator_report_attach_consistency.json")
DEFAULT_JSON_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_chrome_fail_report_send_gate_ready.json")
DEFAULT_TXT_OUTPUT_PATH = Path("data/runtime/copilot_handoff/latest_chrome_fail_report_send_gate_ready.txt")

PASS_CONSISTENCY_LABEL = "PASS_CHROME_OPERATOR_REPORT_ATTACH_CONSISTENT"
FORBIDDEN_ANY_RUN_FIELDS = (
    "operator_report_uploaded_any_run",
    "chatgpt_submit_performed_any_run",
    "status_message_posted_any_run",
    "send_button_pressed_any_run",
    "raw_conversation_text_available_any_run",
    "selenium_used",
    "webdriver_used",
    "browser_dom_automation_used",
    "cloudflare_bypass_attempted",
    "captcha_bypass_attempted",
)


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
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def normalize_int(value: Any, *, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


@dataclass(frozen=True)
class ChromeFailReportSendGateSafety:
    browser_action_performed: bool = False
    chatgpt_submit_performed: bool = False
    operator_report_uploaded: bool = False
    status_message_posted: bool = False
    send_button_pressed: bool = False
    file_upload_attempted: bool = False
    file_picker_used: bool = False
    raw_conversation_text_available: bool = False
    selenium_used: bool = False
    webdriver_used: bool = False
    browser_dom_automation_used: bool = False
    cloudflare_bypass_attempted: bool = False
    captcha_bypass_attempted: bool = False
    conversation_text_logged: bool = False
    random_page_click_performed: bool = False


@dataclass(frozen=True)
class ChromeFailReportSendGateResult:
    ok: bool
    result_label: str
    patch_name: str
    patch_result: str
    selected_action: str
    browser_lane: str
    consistency_evidence_path: str
    consistency_result_label: str | None
    consistency_ok: bool
    consistency_runs_requested: int
    consistency_runs_completed: int
    consistency_runs_passed: int
    consistency_consecutive_passes: int
    attachment_verified_from_prior_evidence: bool
    attachment_verified_all_runs: bool
    file_upload_attempted_all_runs: bool
    file_picker_used_all_runs: bool
    file_path_written_all_runs: bool
    send_gate_confirmation_required: bool
    send_gate_rehearsal_confirmation_supplied: str | None
    send_gate_rehearsal_confirmation_matched: bool
    real_send_confirmation_required_for_next_patch: str
    real_send_confirmation_supplied: str | None
    real_send_confirmation_present: bool
    real_send_confirmation_accepted_by_this_patch: bool
    operator_report_path: str | None
    operator_report_sha256: str | None
    computed_operator_report_sha256: str | None
    operator_report_hash_carried_forward: bool
    operator_report_hash_verified_on_disk: bool
    gate_ready: bool
    selected_action_sha256: str
    delivery_gate_sha256: str | None
    browser_action_performed: bool
    file_upload_attempted: bool
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
    issues: tuple[str, ...]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    safety: ChromeFailReportSendGateSafety = field(default_factory=ChromeFailReportSendGateSafety)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["safety"] = asdict(self.safety)
        return payload


def _make_result(
    *,
    ok: bool,
    result_label: str,
    evidence_path: Path,
    evidence_payload: Mapping[str, Any] | None,
    rehearsal_confirmation_text: str | None,
    rehearsal_confirmation_matched: bool,
    real_send_confirmation_text: str | None,
    operator_report_path: str | None,
    operator_report_sha256: str | None,
    computed_operator_report_sha256: str | None,
    hash_carried: bool,
    hash_verified: bool,
    issues: Sequence[str],
) -> ChromeFailReportSendGateResult:
    evidence = evidence_payload or {}
    selected_action_sha256 = sha256_text(ACTION_UPLOAD_OPERATOR_REPORT)
    delivery_gate_material = None
    if operator_report_sha256:
        delivery_gate_material = f"patchops-clu05-v1|chrome|{ACTION_UPLOAD_OPERATOR_REPORT}|{operator_report_sha256}|{CONFIRM_CHROME_FAIL_REPORT_SEND}"
    safety = ChromeFailReportSendGateSafety()
    return ChromeFailReportSendGateResult(
        ok=ok,
        result_label=result_label,
        patch_name=PATCH_NAME,
        patch_result="FAIL",
        selected_action=ACTION_UPLOAD_OPERATOR_REPORT,
        browser_lane="chrome",
        consistency_evidence_path=str(evidence_path),
        consistency_result_label=normalize_optional_text(evidence.get("result_label")),
        consistency_ok=normalize_bool(evidence.get("ok"), default=False),
        consistency_runs_requested=normalize_int(evidence.get("runs_requested"), default=0),
        consistency_runs_completed=normalize_int(evidence.get("runs_completed"), default=0),
        consistency_runs_passed=normalize_int(evidence.get("runs_passed"), default=0),
        consistency_consecutive_passes=normalize_int(evidence.get("consecutive_passes"), default=0),
        attachment_verified_from_prior_evidence=normalize_bool(evidence.get("attachment_verified_all_runs"), default=False),
        attachment_verified_all_runs=normalize_bool(evidence.get("attachment_verified_all_runs"), default=False),
        file_upload_attempted_all_runs=normalize_bool(evidence.get("file_upload_attempted_all_runs"), default=False),
        file_picker_used_all_runs=normalize_bool(evidence.get("file_picker_used_all_runs"), default=False),
        file_path_written_all_runs=normalize_bool(evidence.get("file_path_written_all_runs"), default=False),
        send_gate_confirmation_required=True,
        send_gate_rehearsal_confirmation_supplied=rehearsal_confirmation_text,
        send_gate_rehearsal_confirmation_matched=rehearsal_confirmation_matched,
        real_send_confirmation_required_for_next_patch=CONFIRM_CHROME_FAIL_REPORT_SEND,
        real_send_confirmation_supplied=real_send_confirmation_text,
        real_send_confirmation_present=real_send_confirmation_text is not None,
        real_send_confirmation_accepted_by_this_patch=False,
        operator_report_path=operator_report_path,
        operator_report_sha256=operator_report_sha256,
        computed_operator_report_sha256=computed_operator_report_sha256,
        operator_report_hash_carried_forward=hash_carried,
        operator_report_hash_verified_on_disk=hash_verified,
        gate_ready=ok,
        selected_action_sha256=selected_action_sha256,
        delivery_gate_sha256=sha256_text(delivery_gate_material) if delivery_gate_material else None,
        browser_action_performed=safety.browser_action_performed,
        file_upload_attempted=safety.file_upload_attempted,
        operator_report_uploaded=safety.operator_report_uploaded,
        chatgpt_submit_performed=safety.chatgpt_submit_performed,
        status_message_posted=safety.status_message_posted,
        send_button_pressed=safety.send_button_pressed,
        raw_conversation_text_available=safety.raw_conversation_text_available,
        selenium_used=safety.selenium_used,
        webdriver_used=safety.webdriver_used,
        browser_dom_automation_used=safety.browser_dom_automation_used,
        cloudflare_bypass_attempted=safety.cloudflare_bypass_attempted,
        captcha_bypass_attempted=safety.captcha_bypass_attempted,
        issues=tuple(issues),
        safety=safety,
    )


def run_chrome_fail_report_send_gate_rehearsal(
    *,
    consistency_evidence_payload: Mapping[str, Any] | None,
    consistency_evidence_path: Path = DEFAULT_CONSISTENCY_EVIDENCE_PATH,
    rehearsal_confirmation_text: str | None,
    real_send_confirmation_text: str | None = None,
    operator_report_path: str | None = None,
    expected_operator_report_sha256: str | None = None,
) -> ChromeFailReportSendGateResult:
    rehearsal_confirmation_matched = rehearsal_confirmation_text == CONFIRM_CHROME_FAIL_REPORT_SEND_GATE_REHEARSAL

    if rehearsal_confirmation_text is None:
        return _make_result(ok=False, result_label=BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_CONFIRMATION_REQUIRED, evidence_path=consistency_evidence_path, evidence_payload=consistency_evidence_payload, rehearsal_confirmation_text=None, rehearsal_confirmation_matched=False, real_send_confirmation_text=real_send_confirmation_text, operator_report_path=operator_report_path, operator_report_sha256=expected_operator_report_sha256, computed_operator_report_sha256=None, hash_carried=False, hash_verified=False, issues=("send gate rehearsal confirmation is required",))
    if not rehearsal_confirmation_matched:
        return _make_result(ok=False, result_label=BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_CONFIRMATION_MISMATCH, evidence_path=consistency_evidence_path, evidence_payload=consistency_evidence_payload, rehearsal_confirmation_text=rehearsal_confirmation_text, rehearsal_confirmation_matched=False, real_send_confirmation_text=real_send_confirmation_text, operator_report_path=operator_report_path, operator_report_sha256=expected_operator_report_sha256, computed_operator_report_sha256=None, hash_carried=False, hash_verified=False, issues=(f"confirmation must exactly match {CONFIRM_CHROME_FAIL_REPORT_SEND_GATE_REHEARSAL}",))
    if real_send_confirmation_text is not None:
        return _make_result(ok=False, result_label=BLOCKED_SEND_RISK, evidence_path=consistency_evidence_path, evidence_payload=consistency_evidence_payload, rehearsal_confirmation_text=rehearsal_confirmation_text, rehearsal_confirmation_matched=True, real_send_confirmation_text=real_send_confirmation_text, operator_report_path=operator_report_path, operator_report_sha256=expected_operator_report_sha256, computed_operator_report_sha256=None, hash_carried=False, hash_verified=False, issues=("CLU-05 is a rehearsal only; real send confirmation belongs to the optional send-test patch",))
    if not consistency_evidence_payload:
        return _make_result(ok=False, result_label=BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_EVIDENCE_MISSING, evidence_path=consistency_evidence_path, evidence_payload=consistency_evidence_payload, rehearsal_confirmation_text=rehearsal_confirmation_text, rehearsal_confirmation_matched=True, real_send_confirmation_text=None, operator_report_path=operator_report_path, operator_report_sha256=expected_operator_report_sha256, computed_operator_report_sha256=None, hash_carried=False, hash_verified=False, issues=("CLU-04 consistency evidence is required",))

    evidence = consistency_evidence_payload
    evidence_issues: list[str] = []
    if not normalize_bool(evidence.get("ok"), default=False):
        evidence_issues.append("consistency evidence ok must be true")
    if normalize_optional_text(evidence.get("result_label")) != PASS_CONSISTENCY_LABEL:
        evidence_issues.append(f"consistency result_label must be {PASS_CONSISTENCY_LABEL}")
    if normalize_optional_text(evidence.get("selected_action")) != ACTION_UPLOAD_OPERATOR_REPORT:
        evidence_issues.append("selected_action must be upload_operator_report")
    if normalize_optional_text(evidence.get("browser_lane")) != "chrome":
        evidence_issues.append("browser_lane must be chrome")
    if normalize_int(evidence.get("runs_completed"), default=0) < 3:
        evidence_issues.append("runs_completed must be at least 3")
    if normalize_int(evidence.get("runs_passed"), default=0) < 3:
        evidence_issues.append("runs_passed must be at least 3")
    if normalize_int(evidence.get("consecutive_passes"), default=0) < 3:
        evidence_issues.append("consecutive_passes must be at least 3")

    if evidence_issues:
        return _make_result(ok=False, result_label=BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_EVIDENCE_INVALID, evidence_path=consistency_evidence_path, evidence_payload=evidence, rehearsal_confirmation_text=rehearsal_confirmation_text, rehearsal_confirmation_matched=True, real_send_confirmation_text=None, operator_report_path=operator_report_path or normalize_optional_text(evidence.get("base_operator_report_path")), operator_report_sha256=expected_operator_report_sha256 or normalize_optional_text(evidence.get("base_operator_report_sha256")), computed_operator_report_sha256=None, hash_carried=False, hash_verified=False, issues=tuple(evidence_issues))

    if not (
        normalize_bool(evidence.get("attachment_verified_all_runs"), default=False)
        and normalize_bool(evidence.get("attachment_ready_all_runs"), default=False)
        and normalize_bool(evidence.get("file_upload_attempted_all_runs"), default=False)
        and normalize_bool(evidence.get("file_picker_used_all_runs"), default=False)
        and normalize_bool(evidence.get("file_path_written_all_runs"), default=False)
    ):
        return _make_result(ok=False, result_label=BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_ATTACHMENT_MISSING, evidence_path=consistency_evidence_path, evidence_payload=evidence, rehearsal_confirmation_text=rehearsal_confirmation_text, rehearsal_confirmation_matched=True, real_send_confirmation_text=None, operator_report_path=operator_report_path or normalize_optional_text(evidence.get("base_operator_report_path")), operator_report_sha256=expected_operator_report_sha256 or normalize_optional_text(evidence.get("base_operator_report_sha256")), computed_operator_report_sha256=None, hash_carried=False, hash_verified=False, issues=("prior CLU-04 evidence must prove attachment readiness, verification, picker use, path write, and upload attempt for all runs",))

    forbidden_true = [field for field in FORBIDDEN_ANY_RUN_FIELDS if normalize_bool(evidence.get(field), default=False)]
    if forbidden_true:
        return _make_result(ok=False, result_label=BLOCKED_SEND_RISK, evidence_path=consistency_evidence_path, evidence_payload=evidence, rehearsal_confirmation_text=rehearsal_confirmation_text, rehearsal_confirmation_matched=True, real_send_confirmation_text=None, operator_report_path=operator_report_path or normalize_optional_text(evidence.get("base_operator_report_path")), operator_report_sha256=expected_operator_report_sha256 or normalize_optional_text(evidence.get("base_operator_report_sha256")), computed_operator_report_sha256=None, hash_carried=False, hash_verified=False, issues=(f"forbidden prior-run flags were true: {', '.join(forbidden_true)}",))

    carried_path = normalize_optional_text(operator_report_path) or normalize_optional_text(evidence.get("base_operator_report_path"))
    carried_hash = normalize_optional_text(expected_operator_report_sha256) or normalize_optional_text(evidence.get("base_operator_report_sha256")) or normalize_optional_text(evidence.get("expected_operator_report_sha256"))
    evidence_base_hash = normalize_optional_text(evidence.get("base_operator_report_sha256"))
    if not carried_path or not carried_hash:
        return _make_result(ok=False, result_label=BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_HASH_MISMATCH, evidence_path=consistency_evidence_path, evidence_payload=evidence, rehearsal_confirmation_text=rehearsal_confirmation_text, rehearsal_confirmation_matched=True, real_send_confirmation_text=None, operator_report_path=carried_path, operator_report_sha256=carried_hash, computed_operator_report_sha256=None, hash_carried=False, hash_verified=False, issues=("operator report path and sha256 must be carried forward from CLU-04 or supplied explicitly",))
    if expected_operator_report_sha256 and evidence_base_hash and expected_operator_report_sha256 != evidence_base_hash:
        return _make_result(ok=False, result_label=BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_HASH_MISMATCH, evidence_path=consistency_evidence_path, evidence_payload=evidence, rehearsal_confirmation_text=rehearsal_confirmation_text, rehearsal_confirmation_matched=True, real_send_confirmation_text=None, operator_report_path=carried_path, operator_report_sha256=expected_operator_report_sha256, computed_operator_report_sha256=None, hash_carried=True, hash_verified=False, issues=("supplied operator report sha256 does not match CLU-04 base hash",))

    path_obj = Path(carried_path)
    if not path_obj.exists() or not path_obj.is_file():
        return _make_result(ok=False, result_label=BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_HASH_MISMATCH, evidence_path=consistency_evidence_path, evidence_payload=evidence, rehearsal_confirmation_text=rehearsal_confirmation_text, rehearsal_confirmation_matched=True, real_send_confirmation_text=None, operator_report_path=carried_path, operator_report_sha256=carried_hash, computed_operator_report_sha256=None, hash_carried=True, hash_verified=False, issues=(f"operator report file is not available for final hash check: {path_obj}",))

    computed_hash = sha256_file(path_obj)
    if computed_hash != carried_hash:
        return _make_result(ok=False, result_label=BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_HASH_MISMATCH, evidence_path=consistency_evidence_path, evidence_payload=evidence, rehearsal_confirmation_text=rehearsal_confirmation_text, rehearsal_confirmation_matched=True, real_send_confirmation_text=None, operator_report_path=carried_path, operator_report_sha256=carried_hash, computed_operator_report_sha256=computed_hash, hash_carried=True, hash_verified=False, issues=("computed operator report hash does not match carried-forward hash",))

    return _make_result(
        ok=True,
        result_label=PASS_CHROME_FAIL_REPORT_SEND_GATE_READY,
        evidence_path=consistency_evidence_path,
        evidence_payload=evidence,
        rehearsal_confirmation_text=rehearsal_confirmation_text,
        rehearsal_confirmation_matched=True,
        real_send_confirmation_text=None,
        operator_report_path=carried_path,
        operator_report_sha256=carried_hash,
        computed_operator_report_sha256=computed_hash,
        hash_carried=True,
        hash_verified=True,
        issues=(),
    )


def render_text(result: ChromeFailReportSendGateResult) -> str:
    lines = [
        f"result_label: {result.result_label}",
        f"ok: {str(result.ok).lower()}",
        f"patch_name: {result.patch_name}",
        f"patch_result: {result.patch_result}",
        f"selected_action: {result.selected_action}",
        f"browser_lane: {result.browser_lane}",
        f"consistency_evidence_path: {result.consistency_evidence_path}",
        f"consistency_result_label: {result.consistency_result_label}",
        f"consistency_ok: {str(result.consistency_ok).lower()}",
        f"consistency_runs_requested: {result.consistency_runs_requested}",
        f"consistency_runs_completed: {result.consistency_runs_completed}",
        f"consistency_runs_passed: {result.consistency_runs_passed}",
        f"consistency_consecutive_passes: {result.consistency_consecutive_passes}",
        f"attachment_verified_from_prior_evidence: {str(result.attachment_verified_from_prior_evidence).lower()}",
        f"attachment_verified_all_runs: {str(result.attachment_verified_all_runs).lower()}",
        f"file_upload_attempted_all_runs: {str(result.file_upload_attempted_all_runs).lower()}",
        f"file_picker_used_all_runs: {str(result.file_picker_used_all_runs).lower()}",
        f"file_path_written_all_runs: {str(result.file_path_written_all_runs).lower()}",
        f"send_gate_confirmation_required: {str(result.send_gate_confirmation_required).lower()}",
        f"send_gate_rehearsal_confirmation_supplied: {result.send_gate_rehearsal_confirmation_supplied}",
        f"send_gate_rehearsal_confirmation_matched: {str(result.send_gate_rehearsal_confirmation_matched).lower()}",
        f"real_send_confirmation_required_for_next_patch: {result.real_send_confirmation_required_for_next_patch}",
        f"real_send_confirmation_supplied: {result.real_send_confirmation_supplied}",
        f"real_send_confirmation_present: {str(result.real_send_confirmation_present).lower()}",
        f"real_send_confirmation_accepted_by_this_patch: {str(result.real_send_confirmation_accepted_by_this_patch).lower()}",
        f"operator_report_path: {result.operator_report_path}",
        f"operator_report_sha256: {result.operator_report_sha256}",
        f"computed_operator_report_sha256: {result.computed_operator_report_sha256}",
        f"operator_report_hash_carried_forward: {str(result.operator_report_hash_carried_forward).lower()}",
        f"operator_report_hash_verified_on_disk: {str(result.operator_report_hash_verified_on_disk).lower()}",
        f"gate_ready: {str(result.gate_ready).lower()}",
        f"selected_action_sha256: {result.selected_action_sha256}",
        f"delivery_gate_sha256: {result.delivery_gate_sha256}",
        f"browser_action_performed: {str(result.browser_action_performed).lower()}",
        f"file_upload_attempted: {str(result.file_upload_attempted).lower()}",
        f"operator_report_uploaded: {str(result.operator_report_uploaded).lower()}",
        f"chatgpt_submit_performed: {str(result.chatgpt_submit_performed).lower()}",
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


def write_evidence(
    result: ChromeFailReportSendGateResult,
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
    parser = argparse.ArgumentParser(description="Chrome fail-report send gate rehearsal")
    parser.add_argument("--consistency-evidence-path", default=str(DEFAULT_CONSISTENCY_EVIDENCE_PATH))
    parser.add_argument("--confirm-send-gate-rehearsal-text", default=None)
    parser.add_argument("--confirm-real-send-text", default=None)
    parser.add_argument("--operator-report-path", default=None)
    parser.add_argument("--operator-report-sha256", default=None)
    parser.add_argument("--json-output-path", default=str(DEFAULT_JSON_OUTPUT_PATH))
    parser.add_argument("--txt-output-path", default=str(DEFAULT_TXT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--no-write-evidence", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    evidence_path = Path(args.consistency_evidence_path)
    evidence_payload: dict[str, Any] | None
    evidence_payload = load_json_object(evidence_path) if evidence_path.exists() else None
    result = run_chrome_fail_report_send_gate_rehearsal(
        consistency_evidence_payload=evidence_payload,
        consistency_evidence_path=evidence_path,
        rehearsal_confirmation_text=args.confirm_send_gate_rehearsal_text,
        real_send_confirmation_text=args.confirm_real_send_text,
        operator_report_path=args.operator_report_path,
        expected_operator_report_sha256=args.operator_report_sha256,
    )
    if not args.no_write_evidence:
        write_evidence(result, json_output_path=Path(args.json_output_path), txt_output_path=Path(args.txt_output_path))
    if args.json:
        print(json.dumps(result.to_dict(), sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(result), end="")
    return 0 if result.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())