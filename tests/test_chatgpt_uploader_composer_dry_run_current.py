from __future__ import annotations

from pathlib import Path

from patchops.chatgpt_uploader.composer_dry_run import (
    ComposerWindow,
    FakeComposerAdapter,
    build_payload_text,
    normalize_title,
    run_composer_dry_run,
    score_composer_candidate,
    score_window,
    select_composer_candidate,
    select_target_window,
)


def test_normalize_title_removes_zero_width_edge_character() -> None:
    assert normalize_title("ChatGPT - Personal - Microsoft\u200b Edge") == "chatgpt - personal - microsoft edge"


def test_scores_real_edge_chatgpt_title_above_non_edge_chatgpt() -> None:
    edge = ComposerWindow(title="ChatGPT - Personal - Microsoft\u200b Edge", process_name="msedge.exe", class_name="Chrome_WidgetWin_1")
    opera = ComposerWindow(title="ChatGPT - wrapper - Opera", process_name="opera.exe", class_name="Chrome_WidgetWin_1")
    edge_score = score_window(edge, "chatgpt.com")
    opera_score = score_window(opera, "chatgpt.com")
    assert edge_score.score >= 60
    assert "normal_edge_window" in edge_score.reasons
    assert opera_score.score < edge_score.score
    assert any(reason.startswith("non_edge_process:") for reason in opera_score.reasons)


def test_select_target_window_rejects_opera_and_brave_when_edge_exists() -> None:
    windows = (
        ComposerWindow(title="ChatGPT - wrapper - Opera", process_name="opera.exe", class_name="Chrome_WidgetWin_1"),
        ComposerWindow(title="ChatGPT - Personal - Microsoft\u200b Edge", process_name="msedge.exe", class_name="Chrome_WidgetWin_1"),
        ComposerWindow(title="New Private Tab - Brave", process_name="brave.exe", class_name="Chrome_WidgetWin_1"),
    )
    candidates, matches = select_target_window(windows, "https://chatgpt.com/")
    assert len(candidates) == 3
    assert len(matches) == 1
    assert matches[0].window.process_name == "msedge.exe"


def test_composer_selector_prefers_message_over_address_bar() -> None:
    address = score_composer_candidate(name="Address and search bar", automation_id="addressEditBox", class_name="Edit", control_type="Edit", handle="a")
    composer = score_composer_candidate(name="Message ChatGPT", automation_id="prompt-textarea", class_name="Edit", control_type="Edit", handle="b")
    selected, matches = select_composer_candidate((address, composer))
    assert selected == composer
    assert len(matches) == 1
    assert "address_or_search_edit" in address.reasons
    assert "message_chatgpt_label" in composer.reasons


def test_composer_candidate_redacts_unknown_edit_names() -> None:
    candidate = score_composer_candidate(name="This might be a user draft and should not be logged verbatim", control_type="Edit")
    assert candidate.name.startswith("<redacted len=")


def test_fake_dry_run_ready_does_not_paste_by_default(tmp_path: Path) -> None:
    result = run_composer_dry_run(
        target_url="https://chatgpt.com/",
        payload_text=build_payload_text(),
        adapter=FakeComposerAdapter(),
        output_dir=tmp_path,
    )
    assert result.ok is True
    assert result.status == "PASS_DRY_RUN_READY"
    assert result.matching_candidate_count == 1
    assert result.focus_attempted is False
    assert result.paste_attempted is False
    assert result.safety_flags.chatgpt_submit_performed is False
    assert result.safety_flags.file_upload_attempted is False
    assert result.safety_flags.selenium_used is False
    assert (tmp_path / "composer_dry_run_result.json").exists()
    assert (tmp_path / "composer_dry_run_result.txt").exists()


def test_fake_dry_run_paste_blocks_when_two_real_composer_matches(tmp_path: Path) -> None:
    result = run_composer_dry_run(
        target_url="https://chatgpt.com/",
        payload_text="PATCHOPS dry-run paste payload",
        adapter=FakeComposerAdapter(composer_count=2),
        allow_focus=True,
        allow_paste=True,
        output_dir=tmp_path,
    )
    assert result.ok is False
    assert result.status == "BLOCKED_COMPOSER_NOT_UNIQUE"
    assert result.matching_composer_candidate_count == 2
    assert result.paste_attempted is False
    assert result.safety_flags.chatgpt_submit_performed is False


def test_fake_dry_run_paste_allows_address_bar_plus_single_composer(tmp_path: Path) -> None:
    address = score_composer_candidate(name="Address and search bar", automation_id="addressEditBox", class_name="Edit", control_type="Edit", handle="a")
    composer = score_composer_candidate(name="Message ChatGPT", automation_id="prompt-textarea", class_name="Edit", control_type="Edit", handle="b")
    result = run_composer_dry_run(
        target_url="https://chatgpt.com/",
        payload_text="PATCHOPS dry-run paste payload",
        adapter=FakeComposerAdapter(composer_candidates=(address, composer)),
        allow_focus=True,
        allow_paste=True,
        output_dir=tmp_path,
    )
    assert result.ok is True
    assert result.status == "PASS_DRY_RUN_PASTED"
    assert result.composer_candidate_count == 2
    assert result.matching_composer_candidate_count == 1
    assert result.selected_composer == composer
    assert result.paste_attempted is True
    assert result.paste_confirmed is True
    assert result.safety_flags.clipboard_written is True
    assert result.safety_flags.paste_attempted is True
    assert result.safety_flags.chatgpt_submit_performed is False
    assert "SELECTED_COMPOSER" in (tmp_path / "composer_dry_run_result.txt").read_text(encoding="utf-8")


def test_real_provider_is_blocked_without_explicit_gate(tmp_path: Path) -> None:
    class NoTouchAdapter(FakeComposerAdapter):
        provider_name = "pywinauto"
    result = run_composer_dry_run(
        target_url="https://chatgpt.com/",
        payload_text="payload",
        adapter=NoTouchAdapter(),
        allow_real_edge=False,
        output_dir=tmp_path,
    )
    assert result.ok is False
    assert result.status == "BLOCKED_REAL_EDGE_NOT_ALLOWED"
    assert result.candidate_count == 0
    assert result.paste_attempted is False


def test_ambiguous_edge_targets_block_paste(tmp_path: Path) -> None:
    windows = (
        ComposerWindow(title="ChatGPT - A - Microsoft Edge", process_name="msedge.exe", class_name="Chrome_WidgetWin_1"),
        ComposerWindow(title="ChatGPT - B - Microsoft Edge", process_name="msedge.exe", class_name="Chrome_WidgetWin_1"),
    )
    result = run_composer_dry_run(
        target_url="https://chatgpt.com/",
        payload_text="payload",
        adapter=FakeComposerAdapter(windows=windows),
        allow_paste=True,
        output_dir=tmp_path,
    )
    assert result.ok is False
    assert result.status == "BLOCKED_AMBIGUOUS_TARGET"
    assert result.matching_candidate_count == 2
    assert result.focus_attempted is False
    assert result.paste_attempted is False
