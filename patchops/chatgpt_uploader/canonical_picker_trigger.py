from __future__ import annotations

from pathlib import Path

from patchops.chatgpt_uploader.slash_enter_trigger import (
    DEFAULT_SAFE_CLICK_X_RATIO,
    DEFAULT_SAFE_CLICK_Y_RATIO,
    SlashEnterRun,
    run_slash_enter_trigger,
    write_slash_enter_evidence,
)

CANONICAL_PICKER_TRIGGER_NAME = "safe_click_slash_enter_once"
CANONICAL_PICKER_TRIGGER_SEQUENCE = (
    "focus_edge",
    "safe_click_once",
    "slash_once",
    "enter_once",
    "detect_picker",
)
CANONICAL_FORBIDDEN_TRIGGER_BACKENDS = (
    "tab",
    "second_enter",
    "plus_control_search",
    "menu_control_search",
    "ctrl_u",
    "selenium",
    "webdriver",
    "dom_automation",
)


def run_canonical_picker_trigger(
    *,
    target_config_path: str | Path,
    evidence_dir: str | Path,
    allow_open_picker: bool,
    timeout_seconds: int = 10,
    safe_click_x_ratio: float = DEFAULT_SAFE_CLICK_X_RATIO,
    safe_click_y_ratio: float = DEFAULT_SAFE_CLICK_Y_RATIO,
    close_picker_on_detect: bool = True,
    evidence_basename: str = "canonical_picker_trigger",
) -> tuple[SlashEnterRun, Path, Path]:
    """Run the canonical future ChatGPT picker-open trigger.

    Production mode is exactly one attempt:
    focus Edge -> one safe click -> slash -> Enter once -> detect picker.

    `close_picker_on_detect` defaults to True for trigger-only proofs. Composition stages
    such as U2.5 may set it to False so the open picker can receive the exact report path.
    """
    run = run_slash_enter_trigger(
        target_config_path=target_config_path,
        allow_open_picker=bool(allow_open_picker),
        attempts=1,
        timeout_seconds=max(1, int(timeout_seconds)),
        x_ratio=float(safe_click_x_ratio),
        y_ratio=float(safe_click_y_ratio),
        close_picker_on_detect=bool(close_picker_on_detect),
    )
    json_path, txt_path = write_slash_enter_evidence(run, evidence_dir, basename=evidence_basename)
    return run, json_path, txt_path
