from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence


SAFETY_FLAGS: Mapping[str, str] = {
    "webdriver_used": "false",
    "selenium_used": "false",
    "browser_dom_automation_used": "false",
    "cloudflare_bypass_attempted": "false",
    "captcha_bypass_attempted": "false",
    "file_upload_attempted": "false",
    "chatgpt_submit_performed": "false",
    "conversation_text_logged": "false",
    "random_page_click_performed": "false",
    "clipboard_write_attempted": "true",
}


class ClipboardBackend(Protocol):
    """Minimal clipboard backend contract used by the uploader.

    Backends must never log previous clipboard contents. They may expose provider
    names and error strings only.
    """

    provider_name: str

    def get_text(self) -> str:
        ...

    def set_text(self, text: str) -> None:
        ...


@dataclass(frozen=True)
class ClipboardSetOptions:
    """Bounded clipboard write options for U0.6."""

    preserve_existing: bool = True
    max_chars: int = 20000


@dataclass(frozen=True)
class ClipboardSetVerifyResult:
    """Clipboard set/verify result with no prior clipboard content leakage."""

    status: str
    ok: bool
    provider: str
    requested_sha256: str
    observed_sha256: str | None
    requested_chars: int
    observed_chars: int | None
    verified: bool
    restored_existing: bool
    error: str | None = None
    safety_flags: Mapping[str, str] = field(default_factory=lambda: dict(SAFETY_FLAGS))

    def to_payload(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "status": self.status,
            "provider": self.provider,
            "requested_sha256": self.requested_sha256,
            "observed_sha256": self.observed_sha256,
            "requested_chars": self.requested_chars,
            "observed_chars": self.observed_chars,
            "verified": self.verified,
            "restored_existing": self.restored_existing,
            "error": self.error,
            "safety_flags": dict(self.safety_flags),
        }


class InMemoryClipboardBackend:
    """Deterministic test backend with the same set/get semantics."""

    provider_name = "memory"

    def __init__(self, initial_text: str = "") -> None:
        self._text = initial_text

    def get_text(self) -> str:
        return self._text

    def set_text(self, text: str) -> None:
        self._text = text


class PowerShellClipboardBackend:
    """Windows clipboard backend using PowerShell Set-Clipboard/Get-Clipboard.

    This avoids adding pyperclip as a required dependency. It is intentionally
    narrow and only exchanges text via stdin/stdout.
    """

    provider_name = "powershell"

    def __init__(self, executable: str | None = None, timeout_seconds: int = 15) -> None:
        self.executable = executable or _find_powershell_executable()
        self.timeout_seconds = timeout_seconds
        if not self.executable:
            raise RuntimeError("PowerShell executable was not found for clipboard access")

    def _run(self, command: str, *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [self.executable, "-NoProfile", "-NonInteractive", "-Command", command],
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=self.timeout_seconds,
            check=False,
        )

    def get_text(self) -> str:
        completed = self._run("Get-Clipboard -Raw")
        if completed.returncode != 0:
            raise RuntimeError(_compact_error("Get-Clipboard failed", completed.stderr))
        return completed.stdout

    def set_text(self, text: str) -> None:
        command = "Set-Clipboard -Value ([Console]::In.ReadToEnd())"
        completed = self._run(command, input_text=text)
        if completed.returncode != 0:
            raise RuntimeError(_compact_error("Set-Clipboard failed", completed.stderr))


def _compact_error(prefix: str, stderr: str) -> str:
    details = " ".join((stderr or "").replace("\r", " ").replace("\n", " ").split())
    if not details:
        return prefix
    return f"{prefix}: {details[:500]}"


def _find_powershell_executable() -> str | None:
    if os.name != "nt":
        return None
    candidates = ["powershell.exe", "pwsh.exe"]
    for candidate in candidates:
        try:
            completed = subprocess.run(
                [candidate, "-NoProfile", "-NonInteractive", "-Command", "$PSVersionTable.PSVersion.ToString()"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if completed.returncode == 0:
            return candidate
    return None


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def choose_clipboard_backend(provider: str = "auto") -> ClipboardBackend:
    normalized = provider.lower().strip()
    if normalized == "memory":
        return InMemoryClipboardBackend()
    if normalized == "powershell":
        return PowerShellClipboardBackend()
    if normalized != "auto":
        raise ValueError(f"unknown clipboard provider: {provider}")

    if os.name == "nt":
        try:
            return PowerShellClipboardBackend()
        except Exception:
            # Auto mode falls back to memory so tests and non-interactive runners can
            # still exercise the set/verify state machine without pretending that a
            # real Windows clipboard write happened.
            return InMemoryClipboardBackend()
    return InMemoryClipboardBackend()


def set_and_verify_clipboard(
    text: str,
    *,
    backend: ClipboardBackend | None = None,
    options: ClipboardSetOptions | None = None,
) -> ClipboardSetVerifyResult:
    """Set clipboard text, verify readback, and optionally restore old contents.

    This function performs no browser focus, no paste into ChatGPT, no upload,
    and no send/submit operation. Previous clipboard content is never returned
    in the result payload.
    """

    options = options or ClipboardSetOptions()
    provider = backend or choose_clipboard_backend("auto")
    requested_sha = sha256_text(text)

    if not text:
        return ClipboardSetVerifyResult(
            status="BLOCKED_EMPTY_TEXT",
            ok=False,
            provider=provider.provider_name,
            requested_sha256=requested_sha,
            observed_sha256=None,
            requested_chars=0,
            observed_chars=None,
            verified=False,
            restored_existing=False,
            error="clipboard payload is empty",
        )

    if len(text) > options.max_chars:
        return ClipboardSetVerifyResult(
            status="BLOCKED_TEXT_TOO_LARGE",
            ok=False,
            provider=provider.provider_name,
            requested_sha256=requested_sha,
            observed_sha256=None,
            requested_chars=len(text),
            observed_chars=None,
            verified=False,
            restored_existing=False,
            error=f"clipboard payload exceeds max_chars={options.max_chars}",
        )

    previous_text: str | None = None
    restored = False
    try:
        if options.preserve_existing:
            previous_text = provider.get_text()
        provider.set_text(text)
        observed = provider.get_text()
        observed_sha = sha256_text(observed)
        verified = observed == text
        status = "PASS" if verified else "FAIL_VERIFY_MISMATCH"
        ok = verified
        error = None if verified else "clipboard readback did not match requested text"
    except Exception as exc:
        return ClipboardSetVerifyResult(
            status="FAIL_CLIPBOARD_SET_VERIFY",
            ok=False,
            provider=provider.provider_name,
            requested_sha256=requested_sha,
            observed_sha256=None,
            requested_chars=len(text),
            observed_chars=None,
            verified=False,
            restored_existing=False,
            error=_single_line(str(exc), limit=500),
        )
    finally:
        if options.preserve_existing and previous_text is not None:
            try:
                provider.set_text(previous_text)
                restored = True
            except Exception:
                restored = False

    return ClipboardSetVerifyResult(
        status=status,
        ok=ok,
        provider=provider.provider_name,
        requested_sha256=requested_sha,
        observed_sha256=observed_sha,
        requested_chars=len(text),
        observed_chars=len(observed),
        verified=verified,
        restored_existing=restored,
        error=error,
    )


def _single_line(value: str, *, limit: int) -> str:
    text = " ".join(value.replace("\r", " ").replace("\n", " ").split())
    return text if len(text) <= limit else text[: max(0, limit - 3)] + "..."


def write_clipboard_evidence(result: ClipboardSetVerifyResult, output_dir: str | Path) -> dict[str, str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "u0_06_clipboard_set_verify.json"
    text_path = out / "u0_06_clipboard_set_verify.txt"
    payload = result.to_payload()
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "PATCHOPS CHATGPT UPLOADER U0.6 CLIPBOARD SET/VERIFY",
        "====================================================",
        f"Status             : {result.status}",
        f"OK                 : {str(result.ok).lower()}",
        f"Provider           : {result.provider}",
        f"RequestedChars     : {result.requested_chars}",
        f"ObservedChars      : {result.observed_chars if result.observed_chars is not None else 'n/a'}",
        f"Verified           : {str(result.verified).lower()}",
        f"RestoredExisting   : {str(result.restored_existing).lower()}",
        f"RequestedSha256    : {result.requested_sha256}",
        f"ObservedSha256     : {result.observed_sha256 or 'n/a'}",
        f"Error              : {result.error or ''}",
        "",
        "SAFETY",
        "------",
    ]
    for key, value in sorted(result.safety_flags.items()):
        lines.append(f"{key}:{value}")
    text_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"json_path": str(json_path), "text_path": str(text_path)}


def _default_payload() -> str:
    return "\n".join(
        [
            "PATCHOPS_LLM_PASTEBACK",
            "Status: PASS",
            "Result: PASS",
            "ExitCode: 0",
            "FailureLayer: n/a",
            "NextAction: U0.6 clipboard set/verify smoke payload only; no browser paste/send performed.",
            "END_PATCHOPS_LLM_PASTEBACK",
            "",
        ]
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Set and verify clipboard text for PatchOps Co-Pilot U0.6.")
    parser.add_argument("--text", default=None, help="Text to put on the clipboard. Defaults to a safe smoke payload.")
    parser.add_argument("--text-file", default=None, help="Read clipboard text from this file.")
    parser.add_argument("--provider", default="auto", choices=["auto", "memory", "powershell"], help="Clipboard provider.")
    parser.add_argument("--output-dir", default="data/runtime/u0_06_chatgpt_uploader_clipboard_set_verify")
    parser.add_argument("--max-chars", type=int, default=20000)
    parser.add_argument("--leave-on-clipboard", action="store_true", help="Do not restore previous clipboard contents after verification.")
    parser.add_argument("--json", action="store_true", help="Print JSON payload.")
    args = parser.parse_args(argv)

    if args.text_file:
        text = Path(args.text_file).read_text(encoding="utf-8")
    elif args.text is not None:
        text = args.text
    else:
        text = _default_payload()

    backend = choose_clipboard_backend(args.provider)
    result = set_and_verify_clipboard(
        text,
        backend=backend,
        options=ClipboardSetOptions(preserve_existing=not args.leave_on_clipboard, max_chars=args.max_chars),
    )
    outputs = write_clipboard_evidence(result, args.output_dir)
    payload = {**result.to_payload(), "outputs": outputs}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(Path(outputs["text_path"]).read_text(encoding="utf-8"), end="")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
