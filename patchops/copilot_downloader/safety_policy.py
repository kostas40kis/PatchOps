from __future__ import annotations

from patchops.copilot_downloader.models import DownloaderSafetyFlags, SAFETY_FLAG_NAMES

D0_01_ALLOWED_TRUE_FLAGS: frozenset[str] = frozenset()


def default_safety_flags() -> DownloaderSafetyFlags:
    return DownloaderSafetyFlags()


def validate_foundation_boundary(flags: DownloaderSafetyFlags) -> list[str]:
    issues: list[str] = []
    data = flags.to_dict()
    unknown = sorted(set(data) - set(SAFETY_FLAG_NAMES))
    for name in unknown:
        issues.append(f"unknown safety flag: {name}")
    for name, value in data.items():
        if value and name not in D0_01_ALLOWED_TRUE_FLAGS:
            issues.append(f"{name} must remain false for D0.1 foundation")
    return issues


def assert_foundation_boundary(flags: DownloaderSafetyFlags) -> None:
    issues = validate_foundation_boundary(flags)
    if issues:
        raise ValueError("Downloader D0.1 safety boundary violation: " + "; ".join(issues))