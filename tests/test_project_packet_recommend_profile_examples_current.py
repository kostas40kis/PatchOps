from __future__ import annotations

from patchops.project_packets import build_starter_manifest_for_intent


def test_build_starter_manifest_for_generic_verify_only_uses_current_verify_example() -> None:
    payload = build_starter_manifest_for_intent(
        profile_name="generic_python",
        intent="verify_only",
    )
    assert payload["starter_examples"] == ["examples/generic_verify_patch.json"]


def test_build_starter_manifest_for_generic_cleanup_patch_uses_cleanup_archive_example() -> None:
    payload = build_starter_manifest_for_intent(
        profile_name="generic_python",
        intent="cleanup_patch",
    )
    assert payload["starter_examples"] == ["examples/generic_cleanup_archive_patch.json"]


def test_build_starter_manifest_for_generic_archive_patch_uses_cleanup_archive_example() -> None:
    payload = build_starter_manifest_for_intent(
        profile_name="generic_python",
        intent="archive_patch",
    )
    assert payload["starter_examples"] == ["examples/generic_cleanup_archive_patch.json"]
