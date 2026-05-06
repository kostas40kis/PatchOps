from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from patchops.chatgpt_uploader.canonical_upload_enter_stage import (
    CanonicalUploadEnterStageResult,
    run_canonical_type_path_enter_no_send,
)
from patchops.chatgpt_uploader.config import load_config


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class EdgeLaunchRecoveryResult:
    status: str
    reason: str
    target_url_present: bool
    launch_attempted: bool
    process_started: bool
    executable: str | None
    wait_seconds: float
    safety_flags: dict[str, bool]
    created_at: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EdgeRecoveryUploadResult:
    status: str
    reason: str
    report_path: str | None
    launch_result: dict[str, Any]
    upload_result: dict[str, Any] | None
    safety_flags: dict[str, bool]
    created_at: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def edge_recovery_safety_flags(*, launch_attempted: bool = False, upload_result: CanonicalUploadEnterStageResult | None = None) -> dict[str, bool]:
    upload_flags = dict(upload_result.safety_flags) if upload_result is not None else {}
    return {
        "normal_edge_launch_attempted": bool(launch_attempted),
        "configured_target_open_attempted": bool(launch_attempted),
        "target_config_overwritten": False,
        "hardcoded_target_url_used": False,
        "canonical_picker_trigger_attempted": bool(upload_flags.get("canonical_picker_trigger_attempted", False)),
        "file_picker_open_attempted": bool(upload_flags.get("file_picker_open_attempted", False)),
        "safe_click_attempted": bool(upload_flags.get("safe_click_attempted", False)),
        "slash_sent": bool(upload_flags.get("slash_sent", False)),
        "tab_sent": False,
        "second_enter_attempted": False,
        "plus_control_search_attempted": False,
        "menu_control_search_attempted": False,
        "ctrl_u_attempted": False,
        "file_path_written": bool(upload_flags.get("file_path_written", False)),
        "picker_enter_pressed": bool(upload_flags.get("picker_enter_pressed", False)),
        "file_upload_attempted": bool(upload_flags.get("file_upload_attempted", False)),
        "file_selected_or_confirmed_by_picker_enter": bool(upload_flags.get("file_selected_or_confirmed_by_picker_enter", False)),
        "open_button_clicked": False,
        "attachment_confirmed": False,
        "chatgpt_submit_performed": False,
        "selenium_used": False,
        "webdriver_used": False,
        "browser_dom_automation_used": False,
        "random_page_click_performed": False,
        "conversation_text_logged": False,
        "clipboard_written": False,
        "paste_attempted": False,
    }


def _edge_executable_candidates() -> list[Path]:
    candidates: list[Path] = []
    found = shutil.which("msedge")
    if found:
        candidates.append(Path(found))
    for env_name in ("ProgramFiles", "ProgramFiles(x86)", "LocalAppData"):
        root = os.environ.get(env_name)
        if not root:
            continue
        candidates.append(Path(root) / "Microsoft" / "Edge" / "Application" / "msedge.exe")
    unique: list[Path] = []
    seen: set[str] = set()
    for item in candidates:
        key = str(item).lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def find_msedge_executable() -> str | None:
    for candidate in _edge_executable_candidates():
        try:
            if candidate.exists() and candidate.is_file():
                return str(candidate)
        except OSError:
            continue
    return shutil.which("msedge")


def _launch_result(
    *,
    status: str,
    reason: str,
    target_url_present: bool,
    launch_attempted: bool,
    process_started: bool,
    executable: str | None,
    wait_seconds: float,
) -> EdgeLaunchRecoveryResult:
    return EdgeLaunchRecoveryResult(
        status=status,
        reason=reason,
        target_url_present=bool(target_url_present),
        launch_attempted=bool(launch_attempted),
        process_started=bool(process_started),
        executable=executable,
        wait_seconds=float(wait_seconds),
        safety_flags=edge_recovery_safety_flags(launch_attempted=launch_attempted),
        created_at=utc_now_iso(),
    )


def launch_configured_edge_target(
    *,
    target_config_path: str | Path,
    allow_launch_edge: bool = False,
    wait_seconds: float = 8.0,
) -> EdgeLaunchRecoveryResult:
    try:
        cfg = load_config(target_config_path)
    except Exception as exc:
        return _launch_result(
            status="BLOCKED_CONFIG_LOAD_FAILED",
            reason=f"target config could not be loaded: {exc}",
            target_url_present=False,
            launch_attempted=False,
            process_started=False,
            executable=None,
            wait_seconds=0.0,
        )
    target_url = str(getattr(cfg, "target_url", "") or "").strip()
    if not allow_launch_edge:
        return _launch_result(
            status="PASS_LAUNCH_SKIPPED",
            reason="--allow-launch-edge not provided",
            target_url_present=bool(target_url),
            launch_attempted=False,
            process_started=False,
            executable=None,
            wait_seconds=0.0,
        )
    if not target_url:
        return _launch_result(
            status="BLOCKED_TARGET_URL_MISSING",
            reason="configured target_url is empty",
            target_url_present=False,
            launch_attempted=False,
            process_started=False,
            executable=None,
            wait_seconds=0.0,
        )
    exe = find_msedge_executable()
    if not exe:
        return _launch_result(
            status="BLOCKED_EDGE_EXECUTABLE_NOT_FOUND",
            reason="could not find msedge executable",
            target_url_present=True,
            launch_attempted=False,
            process_started=False,
            executable=None,
            wait_seconds=0.0,
        )
    try:
        subprocess.Popen([exe, target_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
    except Exception as exc:
        return _launch_result(
            status="BLOCKED_EDGE_LAUNCH_FAILED",
            reason=f"normal Edge launch failed: {exc}",
            target_url_present=True,
            launch_attempted=True,
            process_started=False,
            executable=exe,
            wait_seconds=0.0,
        )
    wait = max(0.0, float(wait_seconds))
    if wait > 0:
        time.sleep(wait)
    return _launch_result(
        status="PASS_EDGE_LAUNCH_REQUESTED",
        reason="configured target URL launched in normal Microsoft Edge; no WebDriver/DOM automation used",
        target_url_present=True,
        launch_attempted=True,
        process_started=True,
        executable=exe,
        wait_seconds=wait,
    )


def run_edge_recovery_then_type_path_enter_no_send(
    *,
    target_config_path: str | Path,
    report_path: str | Path,
    evidence_dir: str | Path,
    allow_launch_edge: bool,
    allow_open_picker: bool,
    launch_wait_seconds: float = 8.0,
    timeout_seconds: int = 10,
    safe_click_x_ratio: float = 0.50,
    safe_click_y_ratio: float = 0.34,
) -> EdgeRecoveryUploadResult:
    report_str = str(Path(report_path).expanduser().resolve())
    launch = launch_configured_edge_target(
        target_config_path=target_config_path,
        allow_launch_edge=bool(allow_launch_edge),
        wait_seconds=float(launch_wait_seconds),
    )
    if launch.status.startswith("BLOCKED_"):
        return EdgeRecoveryUploadResult(
            status=launch.status,
            reason=launch.reason,
            report_path=report_str,
            launch_result=launch.to_payload(),
            upload_result=None,
            safety_flags=edge_recovery_safety_flags(launch_attempted=launch.launch_attempted),
            created_at=utc_now_iso(),
        )
    upload = run_canonical_type_path_enter_no_send(
        target_config_path=target_config_path,
        report_path=report_path,
        evidence_dir=evidence_dir,
        allow_open_picker=bool(allow_open_picker),
        timeout_seconds=max(1, int(timeout_seconds)),
        safe_click_x_ratio=float(safe_click_x_ratio),
        safe_click_y_ratio=float(safe_click_y_ratio),
    )
    return EdgeRecoveryUploadResult(
        status=upload.status,
        reason=upload.reason,
        report_path=upload.report_path or report_str,
        launch_result=launch.to_payload(),
        upload_result=upload.to_payload(),
        safety_flags=edge_recovery_safety_flags(launch_attempted=launch.launch_attempted, upload_result=upload),
        created_at=utc_now_iso(),
    )


def write_edge_recovery_upload_evidence(result: EdgeRecoveryUploadResult, evidence_dir: str | Path, *, basename: str = "u2_06a_edge_recovery_upload") -> tuple[Path, Path]:
    root = Path(evidence_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    safe_base = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in basename).strip("_") or "edge_recovery_upload"
    json_path = root / f"{safe_base}.json"
    txt_path = root / f"{safe_base}.txt"
    json_path.write_text(json.dumps(result.to_payload(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    launch = result.launch_result or {}
    lines = [
        "PATCHOPS CHATGPT UPLOADER EDGE RECOVERY THEN TYPE PATH ENTER NO SEND",
        "==================================================================",
        f"Status                 : {result.status}",
        f"Reason                 : {result.reason}",
        f"ReportPath             : {result.report_path or ''}",
        f"LaunchStatus           : {launch.get('status', '')}",
        f"LaunchAttempted        : {str(result.safety_flags['normal_edge_launch_attempted']).lower()}",
        f"LaunchWaitSeconds      : {launch.get('wait_seconds', 0.0)}",
        f"ConfiguredTargetOpen   : {str(result.safety_flags['configured_target_open_attempted']).lower()}",
        f"TargetConfigOverwritten: {str(result.safety_flags['target_config_overwritten']).lower()}",
        f"HardcodedTargetUsed    : {str(result.safety_flags['hardcoded_target_url_used']).lower()}",
        f"CanonicalTrigger       : {str(result.safety_flags['canonical_picker_trigger_attempted']).lower()}",
        f"SlashSent              : {str(result.safety_flags['slash_sent']).lower()}",
        f"TabSent                : {str(result.safety_flags['tab_sent']).lower()}",
        f"SecondEnterAttempted   : {str(result.safety_flags['second_enter_attempted']).lower()}",
        f"PlusControlSearch      : {str(result.safety_flags['plus_control_search_attempted']).lower()}",
        f"MenuControlSearch      : {str(result.safety_flags['menu_control_search_attempted']).lower()}",
        f"CtrlUAttempted         : {str(result.safety_flags['ctrl_u_attempted']).lower()}",
        f"FilePathWritten        : {str(result.safety_flags['file_path_written']).lower()}",
        f"PickerEnterPressed     : {str(result.safety_flags['picker_enter_pressed']).lower()}",
        f"FileUploadAttempted    : {str(result.safety_flags['file_upload_attempted']).lower()}",
        "OpenButtonClicked      : false",
        "AttachmentConfirmed    : false",
        "ChatGPTSubmitPerformed : false",
        "SeleniumUsed           : false",
        "WebDriverUsed          : false",
        "BrowserDomAutomation   : false",
        "RandomPageClick        : false",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path
