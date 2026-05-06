from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Protocol
from urllib.parse import urlparse

_ZERO_WIDTH_RE = re.compile(r"[\u200b\u200c\u200d\ufeff]")
_SAFE_LABEL_KEYWORDS = (
    "message", "chatgpt", "ask anything", "prompt", "composer", "send a message",
    "address", "search", "web address", "url", "location", "omnibox",
)
_ADDRESS_NEGATIVE_RE = re.compile(r"\b(address|search|web address|url|location|omnibox)\b", re.I)
_COMPOSER_POSITIVE_RE = re.compile(r"\b(message|ask anything|chatgpt|prompt|composer|send a message)\b", re.I)


@dataclass(frozen=True)
class ComposerSafetyFlags:
    selenium_used: bool = False
    webdriver_used: bool = False
    browser_dom_automation_used: bool = False
    cloudflare_bypass_attempted: bool = False
    captcha_bypass_attempted: bool = False
    file_upload_attempted: bool = False
    chatgpt_submit_performed: bool = False
    conversation_text_logged: bool = False
    random_page_click_performed: bool = False
    clipboard_written: bool = False
    paste_attempted: bool = False


@dataclass(frozen=True)
class ComposerWindow:
    title: str
    process_name: str | None = None
    process_id: int | None = None
    class_name: str | None = None
    handle: str | None = None
    url: str | None = None
    is_foreground: bool = False


@dataclass(frozen=True)
class ComposerCandidate:
    window: ComposerWindow
    score: int
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ComposerEditCandidate:
    handle: str | None
    name: str
    automation_id: str | None
    class_name: str | None
    control_type: str | None
    visible: bool
    enabled: bool
    score: int
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ComposerDryRunResult:
    ok: bool
    status: str
    provider: str
    target_url: str
    target_host: str
    target_url_sha256: str
    payload_sha256: str
    payload_size_chars: int
    candidate_count: int
    matching_candidate_count: int
    selected: ComposerCandidate | None
    composer_candidate_count: int
    matching_composer_candidate_count: int
    selected_composer: ComposerEditCandidate | None
    focus_allowed: bool
    focus_attempted: bool
    focus_confirmed: bool
    paste_allowed: bool
    paste_attempted: bool
    paste_confirmed: bool
    reason: str
    evidence_paths: dict[str, str]
    safety_flags: ComposerSafetyFlags
    candidates: tuple[ComposerCandidate, ...] = ()
    composer_candidates: tuple[ComposerEditCandidate, ...] = ()

    def to_payload(self) -> dict[str, object]:
        payload = asdict(self)
        payload["safety_flags"] = asdict(self.safety_flags)
        return payload


class ComposerAdapter(Protocol):
    provider_name: str

    def enumerate_windows(self) -> tuple[ComposerWindow, ...]:
        ...

    def focus_window(self, window: ComposerWindow) -> bool:
        ...

    def inspect_composer_candidates(self, window: ComposerWindow) -> tuple[ComposerEditCandidate, ...]:
        ...

    def paste_text(self, window: ComposerWindow, text: str, composer: ComposerEditCandidate | None = None) -> bool:
        ...

    def count_composer_candidates(self, window: ComposerWindow) -> int:
        ...


def normalize_title(value: str | None) -> str:
    if not value:
        return ""
    value = _ZERO_WIDTH_RE.sub("", value)
    return " ".join(value.lower().split())


def target_host_from_url(target_url: str) -> str:
    return (urlparse(target_url).netloc or "").lower()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _safe_label(value: str | None) -> str:
    normalized = normalize_title(value)
    if not normalized:
        return ""
    if len(normalized) <= 80 and any(keyword in normalized for keyword in _SAFE_LABEL_KEYWORDS):
        return normalized
    digest = sha256_text(normalized)[:12]
    return f"<redacted len={len(normalized)} sha256_12={digest}>"


def _is_normal_edge_window(window: ComposerWindow) -> bool:
    process = (window.process_name or "").lower()
    title = normalize_title(window.title)
    return process == "msedge.exe" or "microsoft edge" in title


def _is_chatgpt_like(window: ComposerWindow, target_host: str) -> bool:
    title = normalize_title(window.title)
    url = (window.url or "").lower()
    return (
        "chatgpt" in title
        or "openai" in title
        or (target_host and target_host in title)
        or (target_host and target_host in url)
    )


def score_window(window: ComposerWindow, target_host: str) -> ComposerCandidate:
    score = 0
    reasons: list[str] = []
    title = normalize_title(window.title)
    url = (window.url or "").lower()
    process = (window.process_name or "").lower()
    class_name = (window.class_name or "").lower()

    if window.url and url.rstrip("/") == f"https://{target_host}".rstrip("/"):
        score += 90
        reasons.append("exact_target_url")
    if target_host and target_host in url:
        score += 70
        reasons.append("target_host_match")
    if "chatgpt" in title:
        score += 40
        reasons.append("chatgpt_title")
    if "openai" in title:
        score += 30
        reasons.append("openai_title")
    if _is_normal_edge_window(window):
        score += 40
        reasons.append("normal_edge_window")
    elif process:
        score -= 35
        reasons.append(f"non_edge_process:{process}")
    if "chrome_widgetwin" in class_name:
        score += 10
        reasons.append("chromium_top_window")

    return ComposerCandidate(window=window, score=score, reasons=tuple(reasons))


def select_target_window(windows: Iterable[ComposerWindow], target_url: str) -> tuple[tuple[ComposerCandidate, ...], tuple[ComposerCandidate, ...]]:
    target_host = target_host_from_url(target_url)
    candidates = tuple(score_window(w, target_host) for w in windows)
    matches = tuple(
        c for c in candidates
        if _is_normal_edge_window(c.window) and _is_chatgpt_like(c.window, target_host) and c.score >= 60
    )
    return candidates, matches


def score_composer_candidate(*, name: str | None, automation_id: str | None = None, class_name: str | None = None, control_type: str | None = None, visible: bool = True, enabled: bool = True, handle: str | None = None) -> ComposerEditCandidate:
    safe_name = _safe_label(name)
    safe_automation_id = _safe_label(automation_id)
    safe_class_name = _safe_label(class_name)
    label = " ".join(part for part in (normalize_title(name), normalize_title(automation_id), normalize_title(class_name)) if part)
    reasons: list[str] = []
    score = 0

    if visible:
        score += 10
        reasons.append("visible")
    else:
        score -= 40
        reasons.append("not_visible")
    if enabled:
        score += 10
        reasons.append("enabled")
    else:
        score -= 40
        reasons.append("not_enabled")

    if _ADDRESS_NEGATIVE_RE.search(label):
        score -= 120
        reasons.append("address_or_search_edit")
    if "message chatgpt" in label:
        score += 110
        reasons.append("message_chatgpt_label")
    elif "ask anything" in label:
        score += 100
        reasons.append("ask_anything_label")
    elif "send a message" in label:
        score += 90
        reasons.append("send_message_label")
    elif "message" in label and "chatgpt" in label:
        score += 90
        reasons.append("message_and_chatgpt_label")
    elif "prompt" in label or "composer" in label:
        score += 80
        reasons.append("prompt_or_composer_label")
    elif _COMPOSER_POSITIVE_RE.search(label):
        score += 50
        reasons.append("weak_composer_label")

    if (control_type or "").lower() == "edit":
        score += 10
        reasons.append("edit_control")

    return ComposerEditCandidate(
        handle=handle,
        name=safe_name,
        automation_id=safe_automation_id or None,
        class_name=safe_class_name or None,
        control_type=control_type,
        visible=visible,
        enabled=enabled,
        score=score,
        reasons=tuple(reasons),
    )


def select_composer_candidate(candidates: Iterable[ComposerEditCandidate]) -> tuple[ComposerEditCandidate | None, tuple[ComposerEditCandidate, ...]]:
    all_candidates = tuple(candidates)
    matches = tuple(c for c in all_candidates if c.visible and c.enabled and c.score >= 80 and "address_or_search_edit" not in c.reasons)
    if len(matches) != 1:
        return None, matches
    return matches[0], matches


class FakeComposerAdapter:
    provider_name = "fake"

    def __init__(self, windows: tuple[ComposerWindow, ...] | None = None, composer_count: int = 1, composer_candidates: tuple[ComposerEditCandidate, ...] | None = None) -> None:
        self._windows = windows or (
            ComposerWindow(
                title="ChatGPT - Microsoft Edge",
                process_name="msedge.exe",
                handle="fake-edge-1",
                url="https://chatgpt.com/",
                is_foreground=False,
            ),
        )
        if composer_candidates is not None:
            self._composer_candidates = composer_candidates
        else:
            self._composer_candidates = tuple(
                score_composer_candidate(
                    name="Message ChatGPT",
                    automation_id=f"fake-composer-{i}",
                    class_name="Edit",
                    control_type="Edit",
                    visible=True,
                    enabled=True,
                    handle=f"fake-composer-{i}",
                )
                for i in range(composer_count)
            )
        self.focused = False
        self.pasted_text: str | None = None

    def enumerate_windows(self) -> tuple[ComposerWindow, ...]:
        return self._windows

    def focus_window(self, window: ComposerWindow) -> bool:
        self.focused = True
        return True

    def inspect_composer_candidates(self, window: ComposerWindow) -> tuple[ComposerEditCandidate, ...]:
        return self._composer_candidates

    def count_composer_candidates(self, window: ComposerWindow) -> int:
        selected, matches = select_composer_candidate(self._composer_candidates)
        return len(matches) if selected is not None else len(self._composer_candidates)

    def paste_text(self, window: ComposerWindow, text: str, composer: ComposerEditCandidate | None = None) -> bool:
        self.pasted_text = text
        return composer is not None


def _process_names_by_pid() -> dict[int, str]:
    if os.name != "nt":
        return {}
    try:
        completed = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=8,
            check=False,
        )
    except Exception:
        return {}
    result: dict[int, str] = {}
    for line in completed.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip().strip('"') for p in line.split(",")]
        if len(parts) >= 2:
            try:
                result[int(parts[1])] = parts[0]
            except ValueError:
                pass
    return result


class PywinautoComposerAdapter:
    provider_name = "pywinauto"

    def __init__(self) -> None:
        from pywinauto import Desktop  # type: ignore
        self._desktop = Desktop(backend="uia")
        self._by_handle: dict[str, object] = {}
        self._composer_by_handle: dict[str, object] = {}

    def enumerate_windows(self) -> tuple[ComposerWindow, ...]:
        names = _process_names_by_pid()
        windows: list[ComposerWindow] = []
        self._by_handle.clear()
        for raw in self._desktop.windows():
            try:
                title = raw.window_text() or ""
                class_name = raw.class_name() or None
                pid = int(raw.process_id())
                handle = str(getattr(raw, "handle", ""))
            except Exception:
                continue
            if not title and not class_name:
                continue
            process_name = names.get(pid)
            window = ComposerWindow(
                title=title,
                process_name=process_name,
                process_id=pid,
                class_name=class_name,
                handle=handle,
                url=None,
                is_foreground=False,
            )
            windows.append(window)
            if handle:
                self._by_handle[handle] = raw
        return tuple(windows)

    def _raw_for(self, window: ComposerWindow):
        if not window.handle or window.handle not in self._by_handle:
            raise RuntimeError("selected window handle is not available")
        return self._by_handle[window.handle]

    def focus_window(self, window: ComposerWindow) -> bool:
        raw = self._raw_for(window)
        try:
            raw.set_focus()
            time.sleep(0.20)
            return True
        except Exception:
            return False

    def inspect_composer_candidates(self, window: ComposerWindow) -> tuple[ComposerEditCandidate, ...]:
        raw = self._raw_for(window)
        self._composer_by_handle.clear()
        try:
            edits = raw.descendants(control_type="Edit")
        except Exception:
            edits = []
        result: list[ComposerEditCandidate] = []
        for edit in edits:
            try:
                element = edit.element_info
                handle = str(getattr(edit, "handle", "") or getattr(element, "handle", "") or id(edit))
                name = getattr(element, "name", "") or ""
                automation_id = getattr(element, "automation_id", "") or None
                class_name = getattr(element, "class_name", "") or None
                control_type = getattr(element, "control_type", "") or "Edit"
                visible = bool(edit.is_visible())
                enabled = bool(edit.is_enabled())
            except Exception:
                continue
            candidate = score_composer_candidate(
                name=name,
                automation_id=automation_id,
                class_name=class_name,
                control_type=control_type,
                visible=visible,
                enabled=enabled,
                handle=handle,
            )
            result.append(candidate)
            self._composer_by_handle[handle] = edit
        return tuple(result)

    def count_composer_candidates(self, window: ComposerWindow) -> int:
        _selected, matches = select_composer_candidate(self.inspect_composer_candidates(window))
        return len(matches)

    def paste_text(self, window: ComposerWindow, text: str, composer: ComposerEditCandidate | None = None) -> bool:
        try:
            raw = self._raw_for(window)
            raw.set_focus()
            time.sleep(0.20)
            if composer is not None and composer.handle and composer.handle in self._composer_by_handle:
                try:
                    self._composer_by_handle[composer.handle].set_focus()
                    time.sleep(0.15)
                except Exception:
                    pass
            _set_clipboard_text_tk(text)
            from pywinauto.keyboard import send_keys  # type: ignore
            send_keys("^v")
            time.sleep(0.25)
            return True
        except Exception:
            return False


def _set_clipboard_text_tk(text: str) -> None:
    import tkinter as tk
    root = tk.Tk()
    try:
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
    finally:
        try:
            root.destroy()
        except Exception:
            pass


def build_payload_text(text: str | None = None) -> str:
    return text or "PATCHOPS U0.8 DRY RUN PAYLOAD - no send requested."


def run_composer_dry_run(
    *,
    target_url: str,
    payload_text: str,
    adapter: ComposerAdapter,
    allow_real_edge: bool = False,
    allow_focus: bool = False,
    allow_paste: bool = False,
    output_dir: str | Path = "data/runtime/u0_08_chatgpt_uploader_composer_dry_run",
) -> ComposerDryRunResult:
    target_host = target_host_from_url(target_url)
    target_hash = sha256_text(target_url)
    payload_hash = sha256_text(payload_text)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    json_path = output / "composer_dry_run_result.json"
    txt_path = output / "composer_dry_run_result.txt"

    safety = ComposerSafetyFlags()

    if adapter.provider_name != "fake" and not allow_real_edge:
        result = ComposerDryRunResult(False, "BLOCKED_REAL_EDGE_NOT_ALLOWED", adapter.provider_name, target_url, target_host, target_hash, payload_hash, len(payload_text), 0, 0, None, 0, 0, None, allow_focus, False, False, allow_paste, False, False, "Real Edge access requires allow_real_edge.", {}, safety, (), ())
        return _write_result(result, json_path, txt_path)

    windows = adapter.enumerate_windows()
    candidates, matches = select_target_window(windows, target_url)
    selected = matches[0] if len(matches) == 1 else None

    if len(matches) == 0:
        result = ComposerDryRunResult(False, "BLOCKED_TARGET_NOT_FOUND", adapter.provider_name, target_url, target_host, target_hash, payload_hash, len(payload_text), len(candidates), 0, None, 0, 0, None, False, False, False, allow_paste, False, False, "No normal Edge ChatGPT target window was found.", {}, safety, candidates, ())
        return _write_result(result, json_path, txt_path)

    if len(matches) > 1:
        result = ComposerDryRunResult(False, "BLOCKED_AMBIGUOUS_TARGET", adapter.provider_name, target_url, target_host, target_hash, payload_hash, len(payload_text), len(candidates), len(matches), None, 0, 0, None, False, False, False, allow_paste, False, False, "Multiple normal Edge ChatGPT target windows matched; refusing to choose.", {}, safety, candidates, ())
        return _write_result(result, json_path, txt_path)

    focus_attempted = False
    focus_confirmed = False
    composer_candidates: tuple[ComposerEditCandidate, ...] = ()
    matching_composer_candidates: tuple[ComposerEditCandidate, ...] = ()
    selected_composer: ComposerEditCandidate | None = None
    paste_attempted = False
    paste_confirmed = False

    if allow_focus or allow_paste:
        focus_attempted = True
        focus_confirmed = adapter.focus_window(selected.window)

    if focus_confirmed or adapter.provider_name == "fake":
        try:
            composer_candidates = adapter.inspect_composer_candidates(selected.window)
            selected_composer, matching_composer_candidates = select_composer_candidate(composer_candidates)
        except Exception:
            composer_candidates = ()
            matching_composer_candidates = ()
            selected_composer = None

    if allow_paste:
        if not focus_confirmed and adapter.provider_name != "fake":
            status = "BLOCKED_FOCUS_NOT_CONFIRMED"
            ok = False
            reason = "Paste was requested but focus was not confirmed."
        elif selected_composer is None:
            status = "BLOCKED_COMPOSER_NOT_UNIQUE"
            ok = False
            reason = f"Expected exactly one high-confidence composer candidate, found {len(matching_composer_candidates)} of {len(composer_candidates)} visible edit controls."
        else:
            paste_attempted = True
            paste_confirmed = adapter.paste_text(selected.window, payload_text, selected_composer)
            if paste_confirmed:
                status = "PASS_DRY_RUN_PASTED"
                ok = True
                reason = "Dry-run payload pasted into selected composer candidate. No send was performed."
                safety = ComposerSafetyFlags(clipboard_written=True, paste_attempted=True)
            else:
                status = "BLOCKED_PASTE_NOT_CONFIRMED"
                ok = False
                reason = "Paste was attempted but not confirmed. No send was performed."
                safety = ComposerSafetyFlags(paste_attempted=True)
    else:
        status = "PASS_DRY_RUN_READY"
        ok = True
        reason = "Target/composer dry-run is ready; paste was not attempted because allow_paste is false."

    result = ComposerDryRunResult(
        ok=ok,
        status=status,
        provider=adapter.provider_name,
        target_url=target_url,
        target_host=target_host,
        target_url_sha256=target_hash,
        payload_sha256=payload_hash,
        payload_size_chars=len(payload_text),
        candidate_count=len(candidates),
        matching_candidate_count=len(matches),
        selected=selected,
        composer_candidate_count=len(composer_candidates),
        matching_composer_candidate_count=len(matching_composer_candidates),
        selected_composer=selected_composer,
        focus_allowed=allow_focus,
        focus_attempted=focus_attempted,
        focus_confirmed=focus_confirmed,
        paste_allowed=allow_paste,
        paste_attempted=paste_attempted,
        paste_confirmed=paste_confirmed,
        reason=reason,
        evidence_paths={},
        safety_flags=safety,
        candidates=candidates,
        composer_candidates=composer_candidates,
    )
    return _write_result(result, json_path, txt_path)


def _write_result(result: ComposerDryRunResult, json_path: Path, txt_path: Path) -> ComposerDryRunResult:
    payload = result.to_payload()
    payload["evidence_paths"] = {"json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "PATCHOPS_CHATGPT_UPLOADER_COMPOSER_DRY_RUN",
        "Status              : " + result.status,
        "Provider            : " + result.provider,
        "TargetHost          : " + result.target_host,
        "TargetUrlSha256     : " + result.target_url_sha256,
        "PayloadSha256       : " + result.payload_sha256,
        "PayloadSizeChars    : " + str(result.payload_size_chars),
        "CandidateCount      : " + str(result.candidate_count),
        "MatchingCandidates  : " + str(result.matching_candidate_count),
        "ComposerCandidates  : " + str(result.composer_candidate_count),
        "MatchingComposerCandidates : " + str(result.matching_composer_candidate_count),
        "FocusAllowed        : " + str(result.focus_allowed).lower(),
        "FocusAttempted      : " + str(result.focus_attempted).lower(),
        "FocusConfirmed      : " + str(result.focus_confirmed).lower(),
        "PasteAllowed        : " + str(result.paste_allowed).lower(),
        "PasteAttempted      : " + str(result.paste_attempted).lower(),
        "PasteConfirmed      : " + str(result.paste_confirmed).lower(),
        "Reason              : " + result.reason,
    ]
    if result.selected is not None:
        lines.extend([
            "SELECTED_WINDOW",
            "  title        :" + result.selected.window.title,
            "  process_name :" + str(result.selected.window.process_name),
            "  process_id   :" + str(result.selected.window.process_id),
            "  class_name   :" + str(result.selected.window.class_name),
            "  handle       :" + str(result.selected.window.handle),
            "  score        :" + str(result.selected.score),
            "  reasons      :" + ",".join(result.selected.reasons),
        ])
    if result.selected_composer is not None:
        c = result.selected_composer
        lines.extend([
            "SELECTED_COMPOSER",
            "  name         :" + c.name,
            "  automation_id:" + str(c.automation_id),
            "  class_name   :" + str(c.class_name),
            "  control_type :" + str(c.control_type),
            "  handle       :" + str(c.handle),
            "  score        :" + str(c.score),
            "  reasons      :" + ",".join(c.reasons),
        ])
    lines.append("WINDOW_CANDIDATES")
    for index, candidate in enumerate(result.candidates, 1):
        lines.append(f"[{index}] score={candidate.score} reasons={','.join(candidate.reasons)}")
        lines.append(f"  title:{candidate.window.title}")
        lines.append(f"  process_name:{candidate.window.process_name}")
        lines.append(f"  process_id:{candidate.window.process_id}")
        lines.append(f"  class_name:{candidate.window.class_name}")
        lines.append(f"  handle:{candidate.window.handle}")
    lines.append("COMPOSER_CANDIDATES")
    for index, candidate in enumerate(result.composer_candidates, 1):
        lines.append(f"[{index}] score={candidate.score} reasons={','.join(candidate.reasons)}")
        lines.append(f"  name:{candidate.name}")
        lines.append(f"  automation_id:{candidate.automation_id}")
        lines.append(f"  class_name:{candidate.class_name}")
        lines.append(f"  control_type:{candidate.control_type}")
        lines.append(f"  handle:{candidate.handle}")
        lines.append(f"  visible:{candidate.visible}")
        lines.append(f"  enabled:{candidate.enabled}")
    lines.append("SAFETY_FLAGS")
    for key, value in asdict(result.safety_flags).items():
        lines.append(f"{key}:{str(value).lower()}")
    lines.append("END_PATCHOPS_CHATGPT_UPLOADER_COMPOSER_DRY_RUN")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return ComposerDryRunResult(
        ok=result.ok,
        status=result.status,
        provider=result.provider,
        target_url=result.target_url,
        target_host=result.target_host,
        target_url_sha256=result.target_url_sha256,
        payload_sha256=result.payload_sha256,
        payload_size_chars=result.payload_size_chars,
        candidate_count=result.candidate_count,
        matching_candidate_count=result.matching_candidate_count,
        selected=result.selected,
        composer_candidate_count=result.composer_candidate_count,
        matching_composer_candidate_count=result.matching_composer_candidate_count,
        selected_composer=result.selected_composer,
        focus_allowed=result.focus_allowed,
        focus_attempted=result.focus_attempted,
        focus_confirmed=result.focus_confirmed,
        paste_allowed=result.paste_allowed,
        paste_attempted=result.paste_attempted,
        paste_confirmed=result.paste_confirmed,
        reason=result.reason,
        evidence_paths={"json_path": str(json_path), "txt_path": str(txt_path)},
        safety_flags=result.safety_flags,
        candidates=result.candidates,
        composer_candidates=result.composer_candidates,
    )


def adapter_from_name(name: str) -> ComposerAdapter:
    if name == "fake":
        return FakeComposerAdapter()
    if name == "pywinauto":
        return PywinautoComposerAdapter()
    raise ValueError(f"unsupported provider: {name}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="U0.8D ChatGPT uploader composer candidate selector dry-run gate")
    parser.add_argument("--target-url", default="https://chatgpt.com/")
    parser.add_argument("--provider", choices=("fake", "pywinauto"), default="fake")
    parser.add_argument("--payload", default=None)
    parser.add_argument("--payload-file", default=None)
    parser.add_argument("--allow-real-edge", action="store_true")
    parser.add_argument("--allow-focus", action="store_true")
    parser.add_argument("--allow-paste", action="store_true")
    parser.add_argument("--output-dir", default="data/runtime/u0_08_chatgpt_uploader_composer_dry_run")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.payload_file:
        payload_text = Path(args.payload_file).read_text(encoding="utf-8")
    else:
        payload_text = build_payload_text(args.payload)

    try:
        adapter = adapter_from_name(args.provider)
        result = run_composer_dry_run(
            target_url=args.target_url,
            payload_text=payload_text,
            adapter=adapter,
            allow_real_edge=args.allow_real_edge,
            allow_focus=args.allow_focus,
            allow_paste=args.allow_paste,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        output = Path(args.output_dir)
        output.mkdir(parents=True, exist_ok=True)
        target_host = target_host_from_url(args.target_url)
        result = ComposerDryRunResult(
            ok=False,
            status="BLOCKED_ADAPTER_ERROR",
            provider=args.provider,
            target_url=args.target_url,
            target_host=target_host,
            target_url_sha256=sha256_text(args.target_url),
            payload_sha256=sha256_text(payload_text),
            payload_size_chars=len(payload_text),
            candidate_count=0,
            matching_candidate_count=0,
            selected=None,
            composer_candidate_count=0,
            matching_composer_candidate_count=0,
            selected_composer=None,
            focus_allowed=args.allow_focus,
            focus_attempted=False,
            focus_confirmed=False,
            paste_allowed=args.allow_paste,
            paste_attempted=False,
            paste_confirmed=False,
            reason=f"{args.provider} unavailable or failed: {exc}",
            evidence_paths={},
            safety_flags=ComposerSafetyFlags(),
            candidates=(),
            composer_candidates=(),
        )
        result = _write_result(result, output / "composer_dry_run_result.json", output / "composer_dry_run_result.txt")

    if args.json:
        print(json.dumps(result.to_payload(), indent=2, sort_keys=True))
    else:
        print(result.status)
        print(result.reason)
        for key, path in result.evidence_paths.items():
            print(f"{key}: {path}")

    return 0 if result.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
