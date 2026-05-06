from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol

from patchops.chatgpt_uploader.composer_dry_run import (
    ComposerCandidate,
    ComposerWindow,
    select_target_window,
    sha256_text,
    target_host_from_url,
)


DEFAULT_CONFIRM_TEXT = "PATCHOPS_CONFIRM_SEND"


@dataclass(frozen=True)
class SendGateSafetyFlags:
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
    send_attempted: bool = False


@dataclass(frozen=True)
class SendGateResult:
    ok: bool
    status: str
    provider: str
    target_url: str
    target_host: str
    target_url_sha256: str
    candidate_count: int
    matching_candidate_count: int
    selected: ComposerCandidate | None
    composer_candidate_count: int
    focus_allowed: bool
    focus_attempted: bool
    focus_confirmed: bool
    send_allowed: bool
    send_attempted: bool
    send_confirmed: bool
    confirmation_required: str
    confirmation_received_sha256: str | None
    reason: str
    evidence_paths: dict[str, str]
    safety_flags: SendGateSafetyFlags
    candidates: tuple[ComposerCandidate, ...] = ()

    def to_payload(self) -> dict[str, object]:
        payload = asdict(self)
        payload["safety_flags"] = asdict(self.safety_flags)
        return payload


class SendGateAdapter(Protocol):
    provider_name: str

    def enumerate_windows(self) -> tuple[ComposerWindow, ...]:
        ...

    def focus_window(self, window: ComposerWindow) -> bool:
        ...

    def count_composer_candidates(self, window: ComposerWindow) -> int:
        ...

    def submit_composer(self, window: ComposerWindow) -> bool:
        ...


class FakeSendGateAdapter:
    provider_name = "fake"

    def __init__(self, windows: tuple[ComposerWindow, ...] | None = None, composer_count: int = 1) -> None:
        self._windows = windows or (
            ComposerWindow(
                title="ChatGPT - Microsoft Edge",
                process_name="msedge.exe",
                handle="fake-edge-1",
                url="https://chatgpt.com/",
                is_foreground=False,
            ),
        )
        self._composer_count = composer_count
        self.focused = False
        self.submitted = False

    def enumerate_windows(self) -> tuple[ComposerWindow, ...]:
        return self._windows

    def focus_window(self, window: ComposerWindow) -> bool:
        self.focused = True
        return True

    def count_composer_candidates(self, window: ComposerWindow) -> int:
        return self._composer_count

    def submit_composer(self, window: ComposerWindow) -> bool:
        self.submitted = True
        return True


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
        parts = [p.strip().strip('"') for p in line.strip().split(",")]
        if len(parts) >= 2:
            try:
                result[int(parts[1])] = parts[0]
            except ValueError:
                pass
    return result


class PywinautoSendGateAdapter:
    provider_name = "pywinauto"

    def __init__(self) -> None:
        from pywinauto import Desktop  # type: ignore

        self._desktop = Desktop(backend="uia")
        self._by_handle: dict[str, object] = {}

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

            window = ComposerWindow(
                title=title,
                process_name=names.get(pid),
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

    def count_composer_candidates(self, window: ComposerWindow) -> int:
        raw = self._raw_for(window)
        try:
            edits = raw.descendants(control_type="Edit")
        except Exception:
            edits = []

        count = 0
        for edit in edits:
            try:
                if edit.is_visible() and edit.is_enabled():
                    count += 1
            except Exception:
                continue
        return count

    def submit_composer(self, window: ComposerWindow) -> bool:
        # This is the only submit primitive, and it is never called unless every explicit gate passes.
        raw = self._raw_for(window)
        try:
            raw.set_focus()
            time.sleep(0.20)
            from pywinauto.keyboard import send_keys  # type: ignore

            send_keys("{ENTER}")
            time.sleep(0.25)
            return True
        except Exception:
            return False


def adapter_from_name(name: str) -> SendGateAdapter:
    if name == "fake":
        return FakeSendGateAdapter()
    if name == "pywinauto":
        return PywinautoSendGateAdapter()
    raise ValueError(f"unsupported provider: {name}")


def run_explicit_send_gate(
    *,
    target_url: str,
    adapter: SendGateAdapter,
    allow_real_edge: bool = False,
    allow_focus: bool = False,
    allow_send: bool = False,
    confirm_send_text: str = "",
    required_confirm_text: str = DEFAULT_CONFIRM_TEXT,
    output_dir: str | Path = "data/runtime/u0_09_chatgpt_uploader_explicit_send_gate",
) -> SendGateResult:
    target_host = target_host_from_url(target_url)
    target_hash = sha256_text(target_url)
    confirm_hash = sha256_text(confirm_send_text) if confirm_send_text else None
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    json_path = output / "explicit_send_gate_result.json"
    txt_path = output / "explicit_send_gate_result.txt"

    base_safety = SendGateSafetyFlags()

    if adapter.provider_name != "fake" and not allow_real_edge:
        return _write_result(
            SendGateResult(
                ok=False,
                status="BLOCKED_REAL_EDGE_NOT_ALLOWED",
                provider=adapter.provider_name,
                target_url=target_url,
                target_host=target_host,
                target_url_sha256=target_hash,
                candidate_count=0,
                matching_candidate_count=0,
                selected=None,
                composer_candidate_count=0,
                focus_allowed=allow_focus,
                focus_attempted=False,
                focus_confirmed=False,
                send_allowed=allow_send,
                send_attempted=False,
                send_confirmed=False,
                confirmation_required=required_confirm_text,
                confirmation_received_sha256=confirm_hash,
                reason="Real Edge access requires allow_real_edge.",
                evidence_paths={},
                safety_flags=base_safety,
                candidates=(),
            ),
            json_path,
            txt_path,
        )

    windows = adapter.enumerate_windows()
    candidates, matches = select_target_window(windows, target_url)
    selected = matches[0] if len(matches) == 1 else None

    if len(matches) == 0:
        return _write_result(
            SendGateResult(
                ok=False,
                status="BLOCKED_TARGET_NOT_FOUND",
                provider=adapter.provider_name,
                target_url=target_url,
                target_host=target_host,
                target_url_sha256=target_hash,
                candidate_count=len(candidates),
                matching_candidate_count=0,
                selected=None,
                composer_candidate_count=0,
                focus_allowed=False,
                focus_attempted=False,
                focus_confirmed=False,
                send_allowed=allow_send,
                send_attempted=False,
                send_confirmed=False,
                confirmation_required=required_confirm_text,
                confirmation_received_sha256=confirm_hash,
                reason="No normal Edge ChatGPT target window was found.",
                evidence_paths={},
                safety_flags=base_safety,
                candidates=candidates,
            ),
            json_path,
            txt_path,
        )

    if len(matches) > 1:
        return _write_result(
            SendGateResult(
                ok=False,
                status="BLOCKED_AMBIGUOUS_TARGET",
                provider=adapter.provider_name,
                target_url=target_url,
                target_host=target_host,
                target_url_sha256=target_hash,
                candidate_count=len(candidates),
                matching_candidate_count=len(matches),
                selected=None,
                composer_candidate_count=0,
                focus_allowed=False,
                focus_attempted=False,
                focus_confirmed=False,
                send_allowed=allow_send,
                send_attempted=False,
                send_confirmed=False,
                confirmation_required=required_confirm_text,
                confirmation_received_sha256=confirm_hash,
                reason="Multiple normal Edge ChatGPT target windows matched; refusing to choose.",
                evidence_paths={},
                safety_flags=base_safety,
                candidates=candidates,
            ),
            json_path,
            txt_path,
        )

    focus_attempted = False
    focus_confirmed = False
    composer_count = 0

    if allow_focus or allow_send:
        focus_attempted = True
        focus_confirmed = adapter.focus_window(selected.window)

    if focus_confirmed or adapter.provider_name == "fake":
        try:
            composer_count = adapter.count_composer_candidates(selected.window)
        except Exception:
            composer_count = 0

    if not allow_send:
        return _write_result(
            SendGateResult(
                ok=True,
                status="PASS_SEND_GATE_READY",
                provider=adapter.provider_name,
                target_url=target_url,
                target_host=target_host,
                target_url_sha256=target_hash,
                candidate_count=len(candidates),
                matching_candidate_count=len(matches),
                selected=selected,
                composer_candidate_count=composer_count,
                focus_allowed=allow_focus,
                focus_attempted=focus_attempted,
                focus_confirmed=focus_confirmed,
                send_allowed=False,
                send_attempted=False,
                send_confirmed=False,
                confirmation_required=required_confirm_text,
                confirmation_received_sha256=confirm_hash,
                reason="Explicit send gate is ready; send was not attempted because allow_send is false.",
                evidence_paths={},
                safety_flags=base_safety,
                candidates=candidates,
            ),
            json_path,
            txt_path,
        )

    if confirm_send_text != required_confirm_text:
        return _write_result(
            SendGateResult(
                ok=False,
                status="BLOCKED_SEND_CONFIRMATION_MISSING",
                provider=adapter.provider_name,
                target_url=target_url,
                target_host=target_host,
                target_url_sha256=target_hash,
                candidate_count=len(candidates),
                matching_candidate_count=len(matches),
                selected=selected,
                composer_candidate_count=composer_count,
                focus_allowed=allow_focus,
                focus_attempted=focus_attempted,
                focus_confirmed=focus_confirmed,
                send_allowed=True,
                send_attempted=False,
                send_confirmed=False,
                confirmation_required=required_confirm_text,
                confirmation_received_sha256=confirm_hash,
                reason="Send requires exact confirmation text.",
                evidence_paths={},
                safety_flags=base_safety,
                candidates=candidates,
            ),
            json_path,
            txt_path,
        )

    if not focus_confirmed and adapter.provider_name != "fake":
        return _write_result(
            SendGateResult(
                ok=False,
                status="BLOCKED_FOCUS_NOT_CONFIRMED",
                provider=adapter.provider_name,
                target_url=target_url,
                target_host=target_host,
                target_url_sha256=target_hash,
                candidate_count=len(candidates),
                matching_candidate_count=len(matches),
                selected=selected,
                composer_candidate_count=composer_count,
                focus_allowed=allow_focus,
                focus_attempted=focus_attempted,
                focus_confirmed=False,
                send_allowed=True,
                send_attempted=False,
                send_confirmed=False,
                confirmation_required=required_confirm_text,
                confirmation_received_sha256=confirm_hash,
                reason="Send was requested but target focus was not confirmed.",
                evidence_paths={},
                safety_flags=base_safety,
                candidates=candidates,
            ),
            json_path,
            txt_path,
        )

    if composer_count != 1:
        return _write_result(
            SendGateResult(
                ok=False,
                status="BLOCKED_COMPOSER_NOT_UNIQUE",
                provider=adapter.provider_name,
                target_url=target_url,
                target_host=target_host,
                target_url_sha256=target_hash,
                candidate_count=len(candidates),
                matching_candidate_count=len(matches),
                selected=selected,
                composer_candidate_count=composer_count,
                focus_allowed=allow_focus,
                focus_attempted=focus_attempted,
                focus_confirmed=focus_confirmed,
                send_allowed=True,
                send_attempted=False,
                send_confirmed=False,
                confirmation_required=required_confirm_text,
                confirmation_received_sha256=confirm_hash,
                reason=f"Expected exactly one composer candidate, found {composer_count}.",
                evidence_paths={},
                safety_flags=base_safety,
                candidates=candidates,
            ),
            json_path,
            txt_path,
        )

    send_confirmed = adapter.submit_composer(selected.window)
    safety = SendGateSafetyFlags(send_attempted=True, chatgpt_submit_performed=send_confirmed)

    return _write_result(
        SendGateResult(
            ok=send_confirmed,
            status="PASS_SEND_PERFORMED" if send_confirmed else "BLOCKED_SEND_NOT_CONFIRMED",
            provider=adapter.provider_name,
            target_url=target_url,
            target_host=target_host,
            target_url_sha256=target_hash,
            candidate_count=len(candidates),
            matching_candidate_count=len(matches),
            selected=selected,
            composer_candidate_count=composer_count,
            focus_allowed=allow_focus,
            focus_attempted=focus_attempted,
            focus_confirmed=focus_confirmed,
            send_allowed=True,
            send_attempted=True,
            send_confirmed=send_confirmed,
            confirmation_required=required_confirm_text,
            confirmation_received_sha256=confirm_hash,
            reason="Explicit send performed after all gates passed." if send_confirmed else "Send primitive returned false.",
            evidence_paths={},
            safety_flags=safety,
            candidates=candidates,
        ),
        json_path,
        txt_path,
    )


def _write_result(result: SendGateResult, json_path: Path, txt_path: Path) -> SendGateResult:
    payload = result.to_payload()
    payload["evidence_paths"] = {"json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "PATCHOPS_CHATGPT_UPLOADER_EXPLICIT_SEND_GATE",
        "Status              : " + result.status,
        "Provider            : " + result.provider,
        "TargetHost          : " + result.target_host,
        "TargetUrlSha256     : " + result.target_url_sha256,
        "CandidateCount      : " + str(result.candidate_count),
        "MatchingCandidates  : " + str(result.matching_candidate_count),
        "ComposerCandidates  : " + str(result.composer_candidate_count),
        "FocusAllowed        : " + str(result.focus_allowed).lower(),
        "FocusAttempted      : " + str(result.focus_attempted).lower(),
        "FocusConfirmed      : " + str(result.focus_confirmed).lower(),
        "SendAllowed         : " + str(result.send_allowed).lower(),
        "SendAttempted       : " + str(result.send_attempted).lower(),
        "SendConfirmed       : " + str(result.send_confirmed).lower(),
        "ConfirmationRequired: " + result.confirmation_required,
        "ConfirmationHash    : " + str(result.confirmation_received_sha256),
        "Reason              : " + result.reason,
    ]

    if result.selected is not None:
        lines.extend(
            [
                "SELECTED",
                "  title        :" + result.selected.window.title,
                "  process_name :" + str(result.selected.window.process_name),
                "  process_id   :" + str(result.selected.window.process_id),
                "  class_name   :" + str(result.selected.window.class_name),
                "  handle       :" + str(result.selected.window.handle),
                "  score        :" + str(result.selected.score),
                "  reasons      :" + ",".join(result.selected.reasons),
            ]
        )

    lines.append("CANDIDATES")
    for index, candidate in enumerate(result.candidates, 1):
        lines.append(f"[{index}] score={candidate.score} reasons={','.join(candidate.reasons)}")
        lines.append(f"  title:{candidate.window.title}")
        lines.append(f"  process_name:{candidate.window.process_name}")
        lines.append(f"  process_id:{candidate.window.process_id}")
        lines.append(f"  class_name:{candidate.window.class_name}")
        lines.append(f"  handle:{candidate.window.handle}")

    lines.append("SAFETY_FLAGS")
    for key, value in asdict(result.safety_flags).items():
        lines.append(f"{key}:{str(value).lower()}")
    lines.append("END_PATCHOPS_CHATGPT_UPLOADER_EXPLICIT_SEND_GATE")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return SendGateResult(
        ok=result.ok,
        status=result.status,
        provider=result.provider,
        target_url=result.target_url,
        target_host=result.target_host,
        target_url_sha256=result.target_url_sha256,
        candidate_count=result.candidate_count,
        matching_candidate_count=result.matching_candidate_count,
        selected=result.selected,
        composer_candidate_count=result.composer_candidate_count,
        focus_allowed=result.focus_allowed,
        focus_attempted=result.focus_attempted,
        focus_confirmed=result.focus_confirmed,
        send_allowed=result.send_allowed,
        send_attempted=result.send_attempted,
        send_confirmed=result.send_confirmed,
        confirmation_required=result.confirmation_required,
        confirmation_received_sha256=result.confirmation_received_sha256,
        reason=result.reason,
        evidence_paths={"json_path": str(json_path), "txt_path": str(txt_path)},
        safety_flags=result.safety_flags,
        candidates=result.candidates,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="U0.9 ChatGPT uploader explicit send gate")
    parser.add_argument("--target-url", default="https://chatgpt.com/")
    parser.add_argument("--provider", choices=("fake", "pywinauto"), default="fake")
    parser.add_argument("--allow-real-edge", action="store_true")
    parser.add_argument("--allow-focus", action="store_true")
    parser.add_argument("--allow-send", action="store_true")
    parser.add_argument("--confirm-send-text", default="")
    parser.add_argument("--required-confirm-text", default=DEFAULT_CONFIRM_TEXT)
    parser.add_argument("--output-dir", default="data/runtime/u0_09_chatgpt_uploader_explicit_send_gate")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        adapter = adapter_from_name(args.provider)
        result = run_explicit_send_gate(
            target_url=args.target_url,
            adapter=adapter,
            allow_real_edge=args.allow_real_edge,
            allow_focus=args.allow_focus,
            allow_send=args.allow_send,
            confirm_send_text=args.confirm_send_text,
            required_confirm_text=args.required_confirm_text,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        output = Path(args.output_dir)
        output.mkdir(parents=True, exist_ok=True)
        result = SendGateResult(
            ok=False,
            status="BLOCKED_ADAPTER_ERROR",
            provider=args.provider,
            target_url=args.target_url,
            target_host=target_host_from_url(args.target_url),
            target_url_sha256=sha256_text(args.target_url),
            candidate_count=0,
            matching_candidate_count=0,
            selected=None,
            composer_candidate_count=0,
            focus_allowed=args.allow_focus,
            focus_attempted=False,
            focus_confirmed=False,
            send_allowed=args.allow_send,
            send_attempted=False,
            send_confirmed=False,
            confirmation_required=args.required_confirm_text,
            confirmation_received_sha256=sha256_text(args.confirm_send_text) if args.confirm_send_text else None,
            reason=f"{args.provider} unavailable or failed: {exc}",
            evidence_paths={},
            safety_flags=SendGateSafetyFlags(),
            candidates=(),
        )
        result = _write_result(result, output / "explicit_send_gate_result.json", output / "explicit_send_gate_result.txt")

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
