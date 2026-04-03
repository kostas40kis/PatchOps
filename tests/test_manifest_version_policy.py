import json

import pytest

from patchops.cli import main
from patchops.exceptions import ManifestError
from patchops.manifest_reference import build_manifest_schema_summary
from patchops.manifest_validator import (
    CURRENT_MANIFEST_VERSION,
    SUPPORTED_MANIFEST_VERSIONS,
    manifest_version_policy_summary,
    validate_manifest_data,
    validate_manifest_version,
)


def test_validate_manifest_version_accepts_current_version() -> None:
    assert validate_manifest_version(CURRENT_MANIFEST_VERSION) == CURRENT_MANIFEST_VERSION


def test_validate_manifest_version_rejects_unsupported_version_with_readable_error() -> None:
    with pytest.raises(ManifestError) as exc_info:
        validate_manifest_version("2")

    text = str(exc_info.value)
    assert "Unsupported manifest_version" in text
    assert "'2'" in text
    assert "'1'" in text
    assert "Current authoring target" in text
    assert "explicit migration/validator support" in text


def test_validate_manifest_data_delegates_manifest_version_policy() -> None:
    with pytest.raises(ManifestError) as exc_info:
        validate_manifest_data(
            {
                "manifest_version": "2026-preview",
                "patch_name": "bad_version",
                "active_profile": "generic_python",
                "files_to_write": [],
            }
        )

    assert "Unsupported manifest_version" in str(exc_info.value)


def test_manifest_version_policy_summary_is_stable() -> None:
    payload = manifest_version_policy_summary()

    assert payload["current_manifest_version"] == "1"
    assert payload["supported_manifest_versions"] == ["1"]
    assert payload["authoring_target"] == "1"
    assert "Future manifest versions require explicit validator and documentation updates." in payload["compatibility_intent"]
    assert "fail closed" in payload["unsupported_version_behavior"]


def test_build_manifest_schema_summary_exposes_version_policy_surface() -> None:
    payload = build_manifest_schema_summary()

    assert payload["manifest_version"] == "1"
    assert payload["current_manifest_version"] == "1"
    assert payload["supported_manifest_versions"] == ["1"]
    assert payload["version_policy"]["current_manifest_version"] == "1"
    assert payload["manifest_version_field"]["supported_values"] == ["1"]
    assert payload["manifest_version_field"]["authoring_target"] == "1"
    assert "unsupported_behavior" in payload["manifest_version_field"]


def test_schema_command_output_includes_version_policy(capsys) -> None:
    exit_code = main(["schema"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["current_manifest_version"] == "1"
    assert payload["supported_manifest_versions"] == ["1"]
    assert payload["version_policy"]["authoring_target"] == "1"
    assert payload["manifest_version_field"]["current_value"] == "1"