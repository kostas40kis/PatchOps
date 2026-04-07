from __future__ import annotations

from patchops.bundles import (
    BUNDLE_RUN_ROOT_RELATIVE,
    BundleValidationIssue,
    BundleValidationMessage,
    BundleValidationResult,
    validate_extracted_bundle,
    validate_extracted_bundle_dir,
)


def test_bundle_exports_keep_validator_compatibility_names_available() -> None:
    assert BundleValidationIssue is BundleValidationMessage
    assert validate_extracted_bundle is validate_extracted_bundle_dir


def test_bundle_exports_keep_old_and_new_surfaces_visible() -> None:
    assert isinstance(BUNDLE_RUN_ROOT_RELATIVE.as_posix(), str)
    assert "BundleValidationResult" in BundleValidationResult.__name__
