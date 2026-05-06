from __future__ import annotations

from pathlib import Path

from patchops.chatgpt_uploader.composer_dry_run import ComposerWindow
from patchops.chatgpt_uploader.explicit_send_gate import (
    DEFAULT_CONFIRM_TEXT,
    FakeSendGateAdapter,
    run_explicit_send_gate,
)


def test_send_gate_ready_does_not_send_by_default(tmp_path: Path) -> None:
    result = run_explicit_send_gate(
        target_url="https://chatgpt.com/",
        adapter=FakeSendGateAdapter(),
        output_dir=tmp_path,
    )

    assert result.ok is True
    assert result.status == "PASS_SEND_GATE_READY"
    assert result.send_allowed is False
    assert result.send_attempted is False
    assert result.send_confirmed is False
    assert result.safety_flags.chatgpt_submit_performed is False
    assert result.safety_flags.send_attempted is False
    assert (tmp_path / "explicit_send_gate_result.json").exists()
    assert (tmp_path / "explicit_send_gate_result.txt").exists()


def test_real_provider_is_blocked_without_explicit_gate(tmp_path: Path) -> None:
    class NoTouchAdapter(FakeSendGateAdapter):
        provider_name = "pywinauto"

    result = run_explicit_send_gate(
        target_url="https://chatgpt.com/",
        adapter=NoTouchAdapter(),
        allow_real_edge=False,
        output_dir=tmp_path,
    )

    assert result.ok is False
    assert result.status == "BLOCKED_REAL_EDGE_NOT_ALLOWED"
    assert result.send_attempted is False


def test_send_requires_exact_confirmation_text(tmp_path: Path) -> None:
    result = run_explicit_send_gate(
        target_url="https://chatgpt.com/",
        adapter=FakeSendGateAdapter(composer_count=1),
        allow_focus=True,
        allow_send=True,
        confirm_send_text="wrong",
        output_dir=tmp_path,
    )

    assert result.ok is False
    assert result.status == "BLOCKED_SEND_CONFIRMATION_MISSING"
    assert result.send_attempted is False
    assert result.safety_flags.chatgpt_submit_performed is False


def test_send_blocks_when_composer_is_not_unique(tmp_path: Path) -> None:
    result = run_explicit_send_gate(
        target_url="https://chatgpt.com/",
        adapter=FakeSendGateAdapter(composer_count=2),
        allow_focus=True,
        allow_send=True,
        confirm_send_text=DEFAULT_CONFIRM_TEXT,
        output_dir=tmp_path,
    )

    assert result.ok is False
    assert result.status == "BLOCKED_COMPOSER_NOT_UNIQUE"
    assert result.send_attempted is False
    assert result.safety_flags.chatgpt_submit_performed is False


def test_fake_send_performs_only_after_all_explicit_gates(tmp_path: Path) -> None:
    adapter = FakeSendGateAdapter(composer_count=1)
    result = run_explicit_send_gate(
        target_url="https://chatgpt.com/",
        adapter=adapter,
        allow_focus=True,
        allow_send=True,
        confirm_send_text=DEFAULT_CONFIRM_TEXT,
        output_dir=tmp_path,
    )

    assert result.ok is True
    assert result.status == "PASS_SEND_PERFORMED"
    assert result.focus_attempted is True
    assert result.focus_confirmed is True
    assert result.send_allowed is True
    assert result.send_attempted is True
    assert result.send_confirmed is True
    assert result.safety_flags.send_attempted is True
    assert result.safety_flags.chatgpt_submit_performed is True
    assert adapter.submitted is True


def test_ambiguous_edge_targets_block_send(tmp_path: Path) -> None:
    windows = (
        ComposerWindow(title="ChatGPT - A - Microsoft Edge", process_name="msedge.exe", class_name="Chrome_WidgetWin_1"),
        ComposerWindow(title="ChatGPT - B - Microsoft Edge", process_name="msedge.exe", class_name="Chrome_WidgetWin_1"),
    )

    result = run_explicit_send_gate(
        target_url="https://chatgpt.com/",
        adapter=FakeSendGateAdapter(windows=windows),
        allow_focus=True,
        allow_send=True,
        confirm_send_text=DEFAULT_CONFIRM_TEXT,
        output_dir=tmp_path,
    )

    assert result.ok is False
    assert result.status == "BLOCKED_AMBIGUOUS_TARGET"
    assert result.matching_candidate_count == 2
    assert result.send_attempted is False


def test_non_edge_chatgpt_window_is_not_selected(tmp_path: Path) -> None:
    windows = (
        ComposerWindow(title="ChatGPT - wrapper - Opera", process_name="opera.exe", class_name="Chrome_WidgetWin_1"),
        ComposerWindow(title="New Private Tab - Brave", process_name="brave.exe", class_name="Chrome_WidgetWin_1"),
    )

    result = run_explicit_send_gate(
        target_url="https://chatgpt.com/",
        adapter=FakeSendGateAdapter(windows=windows),
        allow_focus=True,
        allow_send=True,
        confirm_send_text=DEFAULT_CONFIRM_TEXT,
        output_dir=tmp_path,
    )

    assert result.ok is False
    assert result.status == "BLOCKED_TARGET_NOT_FOUND"
    assert result.send_attempted is False
