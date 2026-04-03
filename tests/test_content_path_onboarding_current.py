from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_current_target_bootstrap_mentions_content_path_onboarding_rule() -> None:
    content = (PROJECT_ROOT / "onboarding" / "current_target_bootstrap.md").read_text(encoding="utf-8")
    assert "## content_path onboarding note" in content
    assert "wrapper-relative paths from the wrapper project root" in content
    assert "compatibility fallback" in content
    assert "duplicated nested patch-prefix bug" in content


def test_current_target_bootstrap_json_mentions_content_path_onboarding_rule() -> None:
    payload = json.loads((PROJECT_ROOT / "onboarding" / "current_target_bootstrap.json").read_text(encoding="utf-8"))
    stream = payload["content_path_onboarding_rule"]
    assert stream["authoring_rule"] == "wrapper_relative_from_wrapper_project_root"
    assert stream["fallback_rule"] == "manifest_local_compatibility_fallback"
    assert stream["preferred_example_manifest"] == "examples/generic_content_path_patch.json"
    assert stream["status"] == "maintenance_locked"


def test_onboarding_next_prompt_mentions_content_path_onboarding_rule() -> None:
    content = (PROJECT_ROOT / "onboarding" / "next_prompt.txt").read_text(encoding="utf-8")
    assert "[content_path onboarding note]" in content
    assert "wrapper-relative paths from the wrapper project root" in content
    assert "compatibility fallback rather than the primary contract" in content
    assert "generic content-path example" in content
