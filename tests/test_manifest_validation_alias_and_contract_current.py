from __future__ import annotations

import pytest

from patchops.exceptions import ManifestError
from patchops.manifest_validator import validate_manifest_data, validate_manifest_version


def _base_manifest() -> dict[str, object]:
    return {
        "manifest_version": "1",
        "patch_name": "manifest_validation_alias_contract",
        "active_profile": "generic_python",
    }


def test_manifest_validation_still_accepts_minimum_shape() -> None:
    validate_manifest_data(_base_manifest())


def test_manifest_version_must_be_string_not_number() -> None:
    with pytest.raises(ManifestError, match="manifest_version must be the string"):
        validate_manifest_version(1)


def test_manifest_version_rejects_one_dot_zero_with_guidance() -> None:
    with pytest.raises(ManifestError, match="Use '1', not '1.0'"):
        validate_manifest_data({**_base_manifest(), "manifest_version": "1.0"})


def test_manifest_active_profile_must_be_non_empty_string() -> None:
    with pytest.raises(ManifestError, match="active_profile"):
        validate_manifest_data({**_base_manifest(), "active_profile": "   "})


def test_manifest_rejects_files_alias_before_silent_no_write() -> None:
    with pytest.raises(ManifestError, match="files_to_write"):
        validate_manifest_data(
            {
                **_base_manifest(),
                "files": [
                    {
                        "path": "docs/wrong.md",
                        "content": "this would be silently ignored without validation",
                    }
                ],
            }
        )


def test_manifest_rejects_writes_alias_before_silent_no_write() -> None:
    with pytest.raises(ManifestError, match="files_to_write"):
        validate_manifest_data(
            {
                **_base_manifest(),
                "writes": [
                    {
                        "path": "docs/wrong.md",
                        "content": "this would be silently ignored without validation",
                    }
                ],
            }
        )


def test_manifest_rejects_ambiguous_alias_even_when_files_to_write_exists() -> None:
    with pytest.raises(ManifestError, match="files_to_write"):
        validate_manifest_data(
            {
                **_base_manifest(),
                "files_to_write": [{"path": "docs/right.md", "content": "right"}],
                "files": [{"path": "docs/wrong.md", "content": "wrong"}],
            }
        )
