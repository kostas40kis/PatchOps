from __future__ import annotations

import ctypes
import hashlib
import json
import sys
from ctypes import wintypes
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

PASS_CHROME_TARGET_READY = "PASS_CHROME_TARGET_READY"
BLOCKED_CHROME_NOT_RUNNING = "BLOCKED_CHROME_NOT_RUNNING"
BLOCKED_CHROME_TARGET_AMBIGUOUS = "BLOCKED_CHROME_TARGET_AMBIGUOUS"
BLOCKED_LOGIN_OR_CHALLENGE = "BLOCKED_LOGIN_OR_CHALLENGE"
BLOCKED_CHROME_TARGET_NOT_READY = "BLOCKED_CHROME_TARGET_NOT_READY"

EXPECTED_BROWSER = "chrome"
EXPECTED_PROCESS_NAME = "chrome.exe"
LIVE_CONFIRM_TEXT = "PATCHOPS_CONFIRM_LIVE_BROWSER"

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
    "browser_launched": False,
    "window_focus_attempted": False,
}

LOGIN_OR_CHALLENGE_TOKENS = (
    "captcha",
    "cloudflare",
    "verify you are human",
    "checking your browser",
    "challenge",
    "sign in",
    "log in",
    "login",
    "authentication",
)

CHATGPT_TARGET_TOKENS = (
    "chatgpt",
    "chat.openai.com",
    "chatgpt.com",
)


@dataclass(frozen=True)
class ChromeWindowCandidate:
    hwnd: int | None
    process_id: int | None
    process_name: str
    title_hash: str
    redacted_title: str
    visible: bool
    minimized: bool
    looks_like_chrome: bool
    looks_like_chatgpt: bool
    matches_configured_target: bool
    login_or_challenge_detected: bool
    selected: bool = False


@dataclass(frozen=True)
class ChromePreflightEvidence:
    ok: bool
    result: str
    expected_browser: str
    live_browser_used: bool
    candidate_count: int
    selectable_count: int
    selected_hwnd: int | None
    selected_process_id: int | None
    selected_title_hash: str | None
    target_url_hash: str | None
    redacted_target_display: str | None
    raw_conversation_text_logged: bool
    file_upload_attempted: bool
    chatgpt_submit_performed: bool
    candidates: list[ChromeWindowCandidate]
    safety_flags: dict[str, bool]
    error: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def _sha256(value: str) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def title_hash(title: str) -> str:
    return _sha256(title or "")


def target_url_hash(target_url: str | None) -> str | None:
    if not target_url:
        return None
    return _sha256(target_url)


def redact_title(title: str) -> str:
    raw = str(title or "").strip()
    if not raw:
        return "<empty-title>"
    lowered = raw.lower()
    if "chatgpt" in lowered:
        return "ChatGPT - Google Chrome"
    if "google chrome" in lowered:
        return "<redacted> - Google Chrome"
    return "<redacted-window-title>"


def redact_target_display(target_url: str | None) -> str | None:
    if not target_url:
        return None
    value = str(target_url)
    if "chatgpt.com" in value:
        return "https://chatgpt.com/<redacted>"
    if "chat.openai.com" in value:
        return "https://chat.openai.com/<redacted>"
    return "<redacted-target-url>"


def title_indicates_login_or_challenge(title: str) -> bool:
    lowered = str(title or "").lower()
    return any(token in lowered for token in LOGIN_OR_CHALLENGE_TOKENS)


def title_looks_like_chatgpt(title: str) -> bool:
    lowered = str(title or "").lower()
    return any(token in lowered for token in CHATGPT_TARGET_TOKENS)


def title_matches_configured_target(title: str, target_url: str | None) -> bool:
    if not target_url:
        return title_looks_like_chatgpt(title)
    lowered_title = str(title or "").lower()
    lowered_target = str(target_url or "").lower()
    if "chatgpt.com" in lowered_target or "chat.openai.com" in lowered_target:
        return title_looks_like_chatgpt(lowered_title)
    return False


def _normalize_process_name(process_name: str) -> str:
    value = str(process_name or "").strip().lower()
    if value == "chrome":
        return EXPECTED_PROCESS_NAME
    return value


def build_candidate(
    *,
    hwnd: int | None = None,
    process_id: int | None = None,
    process_name: str,
    title: str,
    visible: bool,
    minimized: bool = False,
    target_url: str | None = None,
    selected: bool = False,
) -> ChromeWindowCandidate:
    normalized_process = _normalize_process_name(process_name)
    looks_like_chrome = normalized_process == EXPECTED_PROCESS_NAME
    looks_like_chatgpt = title_looks_like_chatgpt(title)
    matches_target = title_matches_configured_target(title, target_url)
    challenge = title_indicates_login_or_challenge(title)
    return ChromeWindowCandidate(
        hwnd=hwnd,
        process_id=process_id,
        process_name=normalized_process,
        title_hash=title_hash(title),
        redacted_title=redact_title(title),
        visible=bool(visible),
        minimized=bool(minimized),
        looks_like_chrome=looks_like_chrome,
        looks_like_chatgpt=looks_like_chatgpt,
        matches_configured_target=matches_target,
        login_or_challenge_detected=challenge,
        selected=selected,
    )


def evaluate_chrome_preflight_candidates(
    candidates: Sequence[ChromeWindowCandidate],
    *,
    target_url: str | None = None,
    live_browser_used: bool = False,
) -> ChromePreflightEvidence:
    candidate_list = list(candidates)
    live_safety_flags = dict(SAFETY_FLAGS)
    live_safety_flags["live_browser_used"] = bool(live_browser_used)

    chrome_candidates = [candidate for candidate in candidate_list if candidate.looks_like_chrome]
    challenge_candidates = [candidate for candidate in chrome_candidates if candidate.login_or_challenge_detected]
    selectable = [
        candidate
        for candidate in chrome_candidates
        if candidate.visible
        and not candidate.minimized
        and candidate.matches_configured_target
        and not candidate.login_or_challenge_detected
    ]

    marked_candidates: list[ChromeWindowCandidate] = []
    selected_hwnd: int | None = None
    selected_pid: int | None = None
    selected_hash: str | None = None

    result = BLOCKED_CHROME_NOT_RUNNING
    ok = False
    error = None

    if not chrome_candidates:
        result = BLOCKED_CHROME_NOT_RUNNING
        error = "No chrome.exe window candidates were found."
    elif challenge_candidates:
        result = BLOCKED_LOGIN_OR_CHALLENGE
        error = "A Chrome ChatGPT candidate appears to be in login, CAPTCHA, Cloudflare, or challenge state."
    elif len(selectable) == 0:
        result = BLOCKED_CHROME_TARGET_NOT_READY
        error = "Chrome is present but no visible normal ChatGPT target candidate was ready."
    elif len(selectable) > 1:
        result = BLOCKED_CHROME_TARGET_AMBIGUOUS
        error = "Multiple visible Chrome ChatGPT target candidates were found."
    else:
        result = PASS_CHROME_TARGET_READY
        ok = True
        selected = selectable[0]
        selected_hwnd = selected.hwnd
        selected_pid = selected.process_id
        selected_hash = selected.title_hash

    for candidate in candidate_list:
        is_selected = ok and candidate.hwnd == selected_hwnd and candidate.title_hash == selected_hash
        marked_candidates.append(
            ChromeWindowCandidate(
                hwnd=candidate.hwnd,
                process_id=candidate.process_id,
                process_name=candidate.process_name,
                title_hash=candidate.title_hash,
                redacted_title=candidate.redacted_title,
                visible=candidate.visible,
                minimized=candidate.minimized,
                looks_like_chrome=candidate.looks_like_chrome,
                looks_like_chatgpt=candidate.looks_like_chatgpt,
                matches_configured_target=candidate.matches_configured_target,
                login_or_challenge_detected=candidate.login_or_challenge_detected,
                selected=is_selected,
            )
        )

    return ChromePreflightEvidence(
        ok=ok,
        result=result,
        expected_browser=EXPECTED_BROWSER,
        live_browser_used=bool(live_browser_used),
        candidate_count=len(candidate_list),
        selectable_count=len(selectable),
        selected_hwnd=selected_hwnd,
        selected_process_id=selected_pid,
        selected_title_hash=selected_hash,
        target_url_hash=target_url_hash(target_url),
        redacted_target_display=redact_target_display(target_url),
        raw_conversation_text_logged=False,
        file_upload_attempted=False,
        chatgpt_submit_performed=False,
        candidates=marked_candidates,
        safety_flags=live_safety_flags,
        error=error,
    )


def write_chrome_preflight_evidence(evidence: ChromePreflightEvidence, path: Path | str) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(evidence.to_payload(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def _get_process_name_from_pid(pid: int) -> str:
    try:
        import subprocess

        command = [
            "powershell",
            "-NoProfile",
            "-Command",
            f"(Get-Process -Id {int(pid)} -ErrorAction SilentlyContinue).ProcessName",
        ]
        result = subprocess.run(command, text=True, capture_output=True, timeout=5, check=False)
        name = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
        if name.lower() == "chrome":
            return EXPECTED_PROCESS_NAME
        if name:
            return name.lower() + (".exe" if not name.lower().endswith(".exe") else "")
    except Exception:
        pass
    return "<unknown>"


def enumerate_windows_live(*, target_url: str | None = None) -> list[ChromeWindowCandidate]:
    if not sys.platform.startswith("win"):
        return []

    user32 = ctypes.windll.user32
    candidates: list[ChromeWindowCandidate] = []

    enum_windows_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def callback(hwnd: int, _lparam: int) -> bool:
        try:
            if not user32.IsWindowVisible(hwnd):
                return True
            title_length = user32.GetWindowTextLengthW(hwnd)
            if title_length <= 0:
                return True
            buffer = ctypes.create_unicode_buffer(title_length + 1)
            user32.GetWindowTextW(hwnd, buffer, title_length + 1)
            title = buffer.value or ""
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            process_name = _get_process_name_from_pid(int(pid.value))
            minimized = bool(user32.IsIconic(hwnd))
            candidate = build_candidate(
                hwnd=int(hwnd),
                process_id=int(pid.value),
                process_name=process_name,
                title=title,
                visible=True,
                minimized=minimized,
                target_url=target_url,
            )
            if candidate.looks_like_chrome:
                candidates.append(candidate)
        except Exception:
            return True
        return True

    user32.EnumWindows(enum_windows_proc(callback), 0)
    return candidates


def run_chrome_preflight(
    *,
    target_url: str | None = None,
    live_browser: bool = False,
    confirm_live_browser_text: str | None = None,
    candidates: Iterable[ChromeWindowCandidate] | None = None,
) -> ChromePreflightEvidence:
    if live_browser:
        if confirm_live_browser_text != LIVE_CONFIRM_TEXT:
            return ChromePreflightEvidence(
                ok=False,
                result=BLOCKED_CHROME_TARGET_NOT_READY,
                expected_browser=EXPECTED_BROWSER,
                live_browser_used=False,
                candidate_count=0,
                selectable_count=0,
                selected_hwnd=None,
                selected_process_id=None,
                selected_title_hash=None,
                target_url_hash=target_url_hash(target_url),
                redacted_target_display=redact_target_display(target_url),
                raw_conversation_text_logged=False,
                file_upload_attempted=False,
                chatgpt_submit_performed=False,
                candidates=[],
                safety_flags=dict(SAFETY_FLAGS),
                error="Live Chrome preflight requires --confirm-live-browser-text PATCHOPS_CONFIRM_LIVE_BROWSER.",
            )
        live_candidates = enumerate_windows_live(target_url=target_url)
        return evaluate_chrome_preflight_candidates(live_candidates, target_url=target_url, live_browser_used=True)

    return evaluate_chrome_preflight_candidates(list(candidates or []), target_url=target_url, live_browser_used=False)