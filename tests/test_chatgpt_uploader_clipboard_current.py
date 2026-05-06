from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.clipboard import (
    ClipboardSetOptions,
    InMemoryClipboardBackend,
    choose_clipboard_backend,
    set_and_verify_clipboard,
    sha256_text,
    write_clipboard_evidence,
)


SAFE_PASTEBACK = "PATCHOPS_LLM_PASTEBACK\nStatus: PASS\nEND_PATCHOPS_LLM_PASTEBACK\n"


def test_memory_clipboard_set_verify_passes_without_browser_or_send() -> None:
    backend = InMemoryClipboardBackend()
    result = set_and_verify_clipboard(SAFE_PASTEBACK, backend=backend, options=ClipboardSetOptions(preserve_existing=False))

    assert result.ok is True
    assert result.status == "PASS"
    assert result.provider == "memory"
    assert result.verified is True
    assert result.requested_sha256 == sha256_text(SAFE_PASTEBACK)
    assert result.observed_sha256 == sha256_text(SAFE_PASTEBACK)
    assert result.safety_flags["file_upload_attempted"] == "false"
    assert result.safety_flags["chatgpt_submit_performed"] == "false"
    assert result.safety_flags["selenium_used"] == "false"


def test_preserve_existing_restores_clipboard_without_leaking_prior_content() -> None:
    backend = InMemoryClipboardBackend("secret prior clipboard text")
    result = set_and_verify_clipboard(SAFE_PASTEBACK, backend=backend, options=ClipboardSetOptions(preserve_existing=True))

    assert result.ok is True
    assert result.restored_existing is True
    assert backend.get_text() == "secret prior clipboard text"
    payload_text = json.dumps(result.to_payload(), sort_keys=True)
    assert "secret prior clipboard text" not in payload_text
    assert SAFE_PASTEBACK not in payload_text


def test_empty_text_is_blocked() -> None:
    result = set_and_verify_clipboard("", backend=InMemoryClipboardBackend())

    assert result.ok is False
    assert result.status == "BLOCKED_EMPTY_TEXT"
    assert result.verified is False


def test_oversized_text_is_blocked_before_set() -> None:
    backend = InMemoryClipboardBackend("unchanged")
    result = set_and_verify_clipboard("x" * 11, backend=backend, options=ClipboardSetOptions(max_chars=10))

    assert result.ok is False
    assert result.status == "BLOCKED_TEXT_TOO_LARGE"
    assert backend.get_text() == "unchanged"


def test_write_clipboard_evidence_redacts_contents(tmp_path: Path) -> None:
    result = set_and_verify_clipboard(SAFE_PASTEBACK, backend=InMemoryClipboardBackend(), options=ClipboardSetOptions(preserve_existing=False))
    outputs = write_clipboard_evidence(result, tmp_path)

    json_payload = json.loads(Path(outputs["json_path"]).read_text(encoding="utf-8"))
    text_payload = Path(outputs["text_path"]).read_text(encoding="utf-8")
    assert json_payload["status"] == "PASS"
    assert "PATCHOPS_LLM_PASTEBACK" not in json.dumps(json_payload)
    assert "RequestedSha256" in text_payload
    assert "chatgpt_submit_performed:false" in text_payload


def test_choose_memory_backend_is_explicit() -> None:
    backend = choose_clipboard_backend("memory")
    assert isinstance(backend, InMemoryClipboardBackend)


def test_smoke_script_runs_by_path_with_memory_provider(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "scripts" / "run_u0_06_chatgpt_uploader_clipboard_set_verify.py"
    output_dir = tmp_path / "script_smoke"

    completed = subprocess.run(
        [sys.executable, str(script), "--provider", "memory", "--output-dir", str(output_dir), "--json"],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["status"] == "PASS"
    assert payload["ok"] is True
    assert payload["provider"] == "memory"
    assert Path(payload["outputs"]["json_path"]).exists()
