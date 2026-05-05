"""Safe ChatGPT report uploader foundation.

This package owns local, no-browser primitives for the future ChatGPT report
uploader. Live browser/file-upload behavior must remain behind explicit gates.
"""

from .dependency_check import check_dependency, run_dependency_doctor
from .models import (
    DependencyStatus,
    ReportPackageCandidate,
    TargetUrlInfo,
    UploaderDoctorResult,
    UploaderSafetyFlags,
)
from .report_packager import build_safe_report_copy
from .safety_policy import assert_safe_no_side_effects
from .target_url import parse_target_url

__all__ = [
    "DependencyStatus",
    "ReportPackageCandidate",
    "TargetUrlInfo",
    "UploaderDoctorResult",
    "UploaderSafetyFlags",
    "assert_safe_no_side_effects",
    "build_safe_report_copy",
    "check_dependency",
    "parse_target_url",
    "run_dependency_doctor",
]
