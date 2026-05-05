from __future__ import annotations

from .models import UploaderSafetyFlags


class UploaderSafetyError(RuntimeError):
    pass


def assert_safe_no_side_effects(flags: UploaderSafetyFlags) -> None:
    """Raise if a doctor/foundation run performed a live side effect."""

    payload = flags.to_payload()
    unsafe = [name for name, value in payload.items() if value]
    if unsafe:
        raise UploaderSafetyError(
            "Uploader foundation expected no live side effects; unsafe flags: "
            + ", ".join(sorted(unsafe))
        )


def default_foundation_safety_flags() -> UploaderSafetyFlags:
    return UploaderSafetyFlags()
