from __future__ import annotations

from patchops.project_packets import build_starter_manifest_for_intent


def test_build_starter_manifest_for_documentation_patch() -> None:
    payload = build_starter_manifest_for_intent(
        profile_name="generic_python",
        intent="documentation_patch",
        target_root=r"C:\dev\demo",
    )
    assert payload["intent"] == "documentation_patch"
    assert payload["starter_examples"] == ["examples/generic_python_patch.json"]
    assert payload["manifest"]["active_profile"] == "generic_python"
    assert payload["manifest"]["target_project_root"] == r"C:\dev\demo"
    assert payload["manifest"]["tags"] == ["starter", "documentation_patch"]


def test_build_starter_manifest_for_verify_only_uses_verify_example() -> None:
    payload = build_starter_manifest_for_intent(
        profile_name="trader",
        intent="verify_only",
    )
    assert payload["starter_examples"] == ["examples/trader_verify_patch.json"]
    assert payload["manifest"]["patch_name"] == "starter_verify_only"
    assert payload["manifest"]["target_project_root"] == r"C:\dev\trader"
