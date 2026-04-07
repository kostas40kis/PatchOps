from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .models import BundleMeta
from .validator import BundleValidationResult, validate_extracted_bundle_dir
from .zip_loader import BundleZipExtractionResult, extract_bundle_zip


@dataclass(frozen=True)
class BundleCheckResult:
    extraction: BundleZipExtractionResult
    validation: BundleValidationResult

    @property
    def is_valid(self) -> bool:
        return self.validation.is_valid

    @property
    def bundle_root(self) -> Path:
        return self.extraction.bundle_root

    @property
    def metadata(self) -> BundleMeta | None:
        return self.validation.metadata


def check_bundle_zip(
    bundle_zip_path: str | Path,
    wrapper_project_root: str | Path,
    *,
    timestamp_token: str | None = None,
) -> BundleCheckResult:
    extraction = extract_bundle_zip(
        Path(bundle_zip_path),
        Path(wrapper_project_root),
        timestamp_token=timestamp_token,
    )
    validation = validate_extracted_bundle_dir(extraction.bundle_root)
    return BundleCheckResult(extraction=extraction, validation=validation)
