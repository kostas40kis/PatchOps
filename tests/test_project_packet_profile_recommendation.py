from __future__ import annotations

from patchops.project_packets import recommend_profile_for_target


def test_recommend_profile_for_trader_target() -> None:
    payload = recommend_profile_for_target(target_root=r"C:\dev\trader")
    assert payload["recommended_profile"] == "trader"
    assert "smallest correct" in payload["rationale"]
    assert "examples/trader_first_verify_patch.json" in payload["starter_examples"]


def test_recommend_profile_for_generic_target() -> None:
    payload = recommend_profile_for_target(target_root=r"C:\dev\demo")
    assert payload["recommended_profile"] == "generic_python"
    assert "generic_python" in payload["rationale"]
    assert "examples/generic_python_verify_patch.json" in payload["starter_examples"]
