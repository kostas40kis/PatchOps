from __future__ import annotations

import importlib
import importlib.metadata
import importlib.util
from collections.abc import Iterable

from .models import DependencyStatus, UploaderDoctorResult, UploaderSafetyFlags
from .target_url import parse_target_url


DEFAULT_OPTIONAL_DEPENDENCIES: tuple[str, ...] = (
    "playwright",
    "selenium",
    "pywinauto",
    "psutil",
    "pyperclip",
)


def check_dependency(name: str, *, required_for: Iterable[str] = ()) -> DependencyStatus:
    """Return import status for one optional dependency without installing it."""

    requirement = tuple(required_for)

    if importlib.util.find_spec(name) is None:
        return DependencyStatus(
            name=name,
            import_ok=False,
            version=None,
            error=f"ModuleNotFoundError: No module named {name!r}",
            required_for=requirement,
        )

    try:
        importlib.import_module(name)
        try:
            version = importlib.metadata.version(name)
        except Exception:
            version = "unknown"
        return DependencyStatus(
            name=name,
            import_ok=True,
            version=version,
            error=None,
            required_for=requirement,
        )
    except Exception as exc:
        return DependencyStatus(
            name=name,
            import_ok=False,
            version=None,
            error=f"{type(exc).__name__}: {exc}",
            required_for=requirement,
        )


def run_dependency_doctor(
    *,
    target_url: str,
    dependency_names: Iterable[str] = DEFAULT_OPTIONAL_DEPENDENCIES,
) -> UploaderDoctorResult:
    """Run the no-side-effect uploader doctor.

    This does not open a browser, does not touch the clipboard, does not upload,
    and does not submit anything to ChatGPT.
    """

    deps = tuple(check_dependency(name) for name in dependency_names)
    target = parse_target_url(target_url)

    notes: list[str] = [
        "doctor_only:no_browser_opened",
        "doctor_only:no_file_upload_attempted",
        "doctor_only:no_chatgpt_submit_performed",
    ]

    if not any(dep.name == "playwright" and dep.import_ok for dep in deps):
        notes.append("playwright_missing:file_input_upload_probe_not_ready")
    if not any(dep.name == "pywinauto" and dep.import_ok for dep in deps):
        notes.append("pywinauto_missing:normal_edge_uia_probe_not_ready")

    return UploaderDoctorResult(
        target_url=target,
        dependencies=deps,
        safety=UploaderSafetyFlags(),
        recommended_mode="doctor_only",
        notes=tuple(notes),
    )
