from __future__ import annotations

from patchops.chatgpt_uploader.edge_target import is_root_chatgpt_target, select_candidate_summaries

ROOT_TARGET = "https://chatgpt.com/"
CONVERSATION_TARGET = "https://chatgpt.com/g/g-p-x/c/abc"


def _summary(**overrides):
    payload = {
        "source": "win32",
        "handle": 1,
        "pid": 10,
        "process_name": "msedge.exe",
        "process_is_msedge": True,
        "class_name": None,
        "class_is_chromium_widget": None,
        "title_sha256": "hash",
        "title_length": 20,
        "title_has_chatgpt": False,
        "title_has_openai": False,
        "title_has_edge": True,
        "visible": True,
        "enabled": True,
        "rectangle": {"left": 0, "top": 0, "right": 100, "bottom": 100},
    }
    payload.update(overrides)
    return payload


def test_root_target_single_win32_edge_candidate_is_allowed() -> None:
    selected, selection = select_candidate_summaries([_summary()], ROOT_TARGET)
    assert len(selected) == 1
    assert selected[0]["candidate_reason"] == "root_target_single_msedge_window"
    assert selection["selection_mode"] == "root_target_single_edge_window"
    assert selection["edge_candidate_count"] == 1
    assert selection["ambiguous"] is False


def test_root_target_multiple_win32_edge_candidates_block() -> None:
    selected, selection = select_candidate_summaries([_summary(handle=1), _summary(handle=2)], ROOT_TARGET)
    assert selected == []
    assert selection["selection_mode"] == "root_target_ambiguous_edge_windows"
    assert selection["edge_candidate_count"] == 2
    assert selection["ambiguous"] is True


def test_non_root_target_does_not_use_win32_single_edge_fallback() -> None:
    selected, selection = select_candidate_summaries([_summary()], CONVERSATION_TARGET)
    assert selected == []
    assert selection["selection_mode"] == "no_matching_chatgpt_edge_window"
    assert selection["ambiguous"] is False


def test_chatgpt_title_still_wins_for_win32_candidate() -> None:
    selected, selection = select_candidate_summaries([_summary(title_has_chatgpt=True)], CONVERSATION_TARGET)
    assert len(selected) == 1
    assert selected[0]["candidate_reason"] == "msedge_title_has_chatgpt"
    assert selection["selection_mode"] == "chatgpt_title"


def test_root_detector_still_accepts_root_only() -> None:
    assert is_root_chatgpt_target(ROOT_TARGET) is True
    assert is_root_chatgpt_target("https://chatgpt.com") is True
    assert is_root_chatgpt_target(CONVERSATION_TARGET) is False
