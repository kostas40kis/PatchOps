from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_current_handoff_mentions_content_path_repair_stream() -> None:
    content = (PROJECT_ROOT / "handoff" / "current_handoff.md").read_text(encoding="utf-8")
    assert "## content_path repair stream" in content
    assert "green through CP5" in content
    assert "wrapper project root first" in content
    assert "compatibility fallback" in content
    assert "Do not reopen" not in content  # prompt wording belongs in next_prompt, not current_handoff


def test_current_handoff_json_mentions_content_path_repair_stream() -> None:
    payload = json.loads((PROJECT_ROOT / "handoff" / "current_handoff.json").read_text(encoding="utf-8"))
    stream = payload["content_path_repair_stream"]
    assert stream["status"] == "green_through_cp5"
    assert stream["bug_state"] == "repaired"
    assert stream["resolution_rule"] == "wrapper_root_first"
    assert stream["fallback_rule"] == "manifest_local_compatibility_fallback"
    assert stream["example_apply_flow_proof"] is True


def test_next_prompt_mentions_content_path_repair_stream() -> None:
    content = (PROJECT_ROOT / "handoff" / "next_prompt.txt").read_text(encoding="utf-8")
    assert "[content_path repair stream]" in content
    assert "wrapper project root first" in content
    assert "compatibility fallback rather than the primary contract" in content
    assert "Do not reopen this area unless new contrary repo evidence appears." in content
