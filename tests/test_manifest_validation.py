import pytest

from patchops.manifest_validator import validate_manifest_data
from patchops.exceptions import ManifestError


def test_manifest_validation_accepts_minimum_shape():
    validate_manifest_data(
        {
            "manifest_version": "1",
            "patch_name": "example",
            "active_profile": "generic_python",
        }
    )


def test_manifest_validation_rejects_missing_required_fields():
    with pytest.raises(ManifestError):
        validate_manifest_data({"manifest_version": "1"})
