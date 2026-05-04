from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from patchops.edge_rpa.edge_navigation_proof import run_l26_04_navigation_proof, validate_target_url
from patchops.edge_rpa.edge_session_classifier import run_l26_05_session_classifier

PATCH_NAME = "l26_05a_targeted_chatgpt_session_classifier_bridge"
_ALLOWED_CLASSIFICATIONS = {"accessible", "login_required", "human_challenge_required"}


@dataclass(frozen=True)
class TargetedChatGptClassificationResult:
    patch_name: str = PATCH_NAME
    observed_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    python_executable: str = sys.executable
    target_url_hash: str = ""
    target_url_host_redacted: str = ""
    navigation_invoked: bool = False
    navigation_result: str = ""
    navigation_classification: str = ""
    navigation_human_challenge_required: bool = False
    session_classifier_invoked: bool = False
    chatgpt_session_classified: bool = False
    classification: str = "unknown"
    target_chatgpt_confirmed: bool = False
    human_challenge_required: bool = False
    login_required: bool = False
    loop_stopped: bool = False
    unknown_classification_rejected: bool = False
    targeted_sequence_completed: bool = False
    navigation_json_path: str = ""
    classifier_json_path: str = ""
    targeted_report_path: str = ""
    webdriver_used: bool = False
    selenium_imported: bool = False
    cloudflare_bypass_attempted: bool = False
    chatgpt_prompt_submitted: bool = False
    download_click_performed: bool = False
    run_package_invoked: bool = False
    pasteback_or_send_performed: bool = False
    conversation_text_logged: bool = False
    full_conversation_text_logged: bool = False
    result: str = "FAIL"
    failure_layer: str = ""
    error: str = ""

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def _hash_text(value: object) -> str:
    text = "" if value is None else str(value)
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


def _target_meta(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    host = parsed.netloc
    host_redacted = host if len(host) <= 80 else f"<host redacted length={len(host)} sha256={_hash_text(host)}>"
    return _hash_text(url), host_redacted


def _write_report(path: Path, result: TargetedChatGptClassificationResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "L26.5A targeted ChatGPT session classifier bridge",
        "conversation_text_logged:false",
        "full_conversation_text_logged:false",
        "chatgpt_prompt_submitted:false",
        "download_click_performed:false",
        "run_package_invoked:false",
        "cloudflare_bypass_attempted:false",
        "",
        f"target_url_hash: {result.target_url_hash}",
        f"target_url_host_redacted: {result.target_url_host_redacted}",
        f"navigation_result: {result.navigation_result}",
        f"navigation_classification: {result.navigation_classification}",
        f"classification: {result.classification}",
        f"target_chatgpt_confirmed: {result.target_chatgpt_confirmed}",
        f"human_challenge_required: {result.human_challenge_required}",
        f"login_required: {result.login_required}",
        f"loop_stopped: {result.loop_stopped}",
        f"unknown_classification_rejected: {result.unknown_classification_rejected}",
        "",
        f"navigation_json_path: {result.navigation_json_path}",
        f"classifier_json_path: {result.classifier_json_path}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_l26_05a_targeted_classifier(*, output_dir: str | Path, target_url: str, start_if_missing: bool = True, settle_seconds: float = 8.0) -> TargetedChatGptClassificationResult:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "normal_edge_l26_05a_targeted_classification_result.json"
    report_path = out_dir / "normal_edge_l26_05a_targeted_classification_report.txt"
    nav_dir = out_dir / "navigation"
    cls_dir = out_dir / "classifier"
    nav_json = nav_dir / "normal_edge_l26_04_navigation_result.json"
    cls_json = cls_dir / "normal_edge_l26_05_session_classification_result.json"

    try:
        url = validate_target_url(target_url)
        target_hash, target_host = _target_meta(url)
    except Exception as exc:
        result = TargetedChatGptClassificationResult(failure_layer="url_validation", error=f"{type(exc).__name__}: {exc}", targeted_report_path=str(report_path))
        json_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
        return result

    nav_result = run_l26_04_navigation_proof(output_dir=nav_dir, target_url=url, start_if_missing=start_if_missing, settle_seconds=settle_seconds)
    nav_payload = nav_result.to_payload()

    cls_result = run_l26_05_session_classifier(output_dir=cls_dir, start_if_missing=start_if_missing, max_depth=5, max_controls=260)
    cls_payload = cls_result.to_payload()
    classification = str(cls_payload.get("classification", "unknown"))
    unknown_rejected = classification != "unknown"
    target_chatgpt_confirmed = bool(cls_payload.get("title_mentions_chatgpt") or classification in {"accessible", "login_required", "human_challenge_required"})
    known_stop = classification in {"login_required", "human_challenge_required"}
    sequence_ok = bool(nav_payload.get("normal_edge_navigation") and cls_payload.get("chatgpt_session_classified"))

    failure_layer = ""
    error = ""
    if not sequence_ok:
        failure_layer = "targeted_navigation_or_classifier"
        error = f"navigation_result={nav_payload.get('result')}; classifier_result={cls_payload.get('result')}"
    elif classification == "unknown":
        failure_layer = "targeted_classifier_unknown"
        error = "The classifier still returned unknown after controlled navigation to the target URL."
    elif classification not in _ALLOWED_CLASSIFICATIONS:
        failure_layer = "targeted_classifier_invalid"
        error = f"Unexpected classification: {classification}"

    result_pass = bool(sequence_ok and classification in _ALLOWED_CLASSIFICATIONS)
    result = TargetedChatGptClassificationResult(
        target_url_hash=target_hash,
        target_url_host_redacted=target_host,
        navigation_invoked=True,
        navigation_result=str(nav_payload.get("result", "")),
        navigation_classification=str(nav_payload.get("classification", "")),
        navigation_human_challenge_required=bool(nav_payload.get("human_challenge_required")),
        session_classifier_invoked=True,
        chatgpt_session_classified=bool(cls_payload.get("chatgpt_session_classified")),
        classification=classification,
        target_chatgpt_confirmed=target_chatgpt_confirmed,
        human_challenge_required=classification == "human_challenge_required",
        login_required=classification == "login_required",
        loop_stopped=known_stop,
        unknown_classification_rejected=unknown_rejected,
        targeted_sequence_completed=sequence_ok,
        navigation_json_path=str(nav_json),
        classifier_json_path=str(cls_json),
        targeted_report_path=str(report_path),
        webdriver_used=bool(nav_payload.get("webdriver_used") or cls_payload.get("webdriver_used")),
        selenium_imported=bool(nav_payload.get("selenium_imported") or cls_payload.get("selenium_imported")),
        cloudflare_bypass_attempted=bool(nav_payload.get("cloudflare_bypass_attempted") or cls_payload.get("cloudflare_bypass_attempted")),
        chatgpt_prompt_submitted=bool(nav_payload.get("chatgpt_prompt_submitted") or cls_payload.get("chatgpt_prompt_submitted")),
        download_click_performed=bool(nav_payload.get("download_click_performed") or cls_payload.get("download_click_performed")),
        run_package_invoked=bool(nav_payload.get("run_package_invoked") or cls_payload.get("run_package_invoked")),
        pasteback_or_send_performed=bool(nav_payload.get("pasteback_or_send_performed") or cls_payload.get("pasteback_or_send_performed")),
        conversation_text_logged=bool(nav_payload.get("conversation_text_logged") or cls_payload.get("conversation_text_logged")),
        full_conversation_text_logged=bool(cls_payload.get("full_conversation_text_logged")),
        result="PASS" if result_pass else "FAIL",
        failure_layer=failure_layer,
        error=error,
    )
    _write_report(report_path, result)
    json_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True), encoding="utf-8")
    return result


def assert_l26_05a_acceptance(result: TargetedChatGptClassificationResult) -> None:
    payload = result.to_payload()
    required_true = [
        "navigation_invoked",
        "session_classifier_invoked",
        "chatgpt_session_classified",
        "targeted_sequence_completed",
        "unknown_classification_rejected",
    ]
    required_false = [
        "webdriver_used",
        "selenium_imported",
        "cloudflare_bypass_attempted",
        "chatgpt_prompt_submitted",
        "download_click_performed",
        "run_package_invoked",
        "pasteback_or_send_performed",
        "conversation_text_logged",
        "full_conversation_text_logged",
    ]
    missing_true = [key for key in required_true if not payload.get(key)]
    unexpected_true = [key for key in required_false if payload.get(key)]
    if payload.get("classification") not in _ALLOWED_CLASSIFICATIONS:
        missing_true.append("classification_accessible_or_stop_state")
    if payload.get("result") != "PASS":
        missing_true.append("result_PASS")
    if missing_true or unexpected_true:
        raise AssertionError(f"L26.5A acceptance failed; missing_true={missing_true}; unexpected_true={unexpected_true}; classification={result.classification}; failure_layer={result.failure_layer}; error={result.error}")
