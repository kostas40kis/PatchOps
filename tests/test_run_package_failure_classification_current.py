from __future__ import annotations

from pathlib import Path

from patchops.package_runner import (
    ProcessCapture,
    _classify_failure,
    _classify_setup_failure_message,
)


def test_preflight_generated_python_syntax_invalid_is_package_authoring_failure() -> None:
    message = (
        "ValueError: Bundle preflight failed before launcher execution:\n"
        "[generated_python_syntax_invalid] Generated Python bundle content is not syntax-valid"
    )
    assert _classify_setup_failure_message(message) == "package_authoring_failure"


def test_preflight_bundle_meta_invalid_is_package_authoring_failure() -> None:
    message = (
        "ValueError: Bundle preflight failed before launcher execution:\n"
        "[bundle_meta_invalid] Bundle metadata could not be parsed"
    )
    assert _classify_setup_failure_message(message) == "package_authoring_failure"


def test_setup_modulenotfounderror_is_wrapper_failure() -> None:
    setup_error = RuntimeError("ModuleNotFoundError: No module named 'patchops'")
    assert _classify_failure(setup_error=setup_error, capture=None) == "wrapper_failure"


def test_capture_modulenotfounderror_is_wrapper_failure() -> None:
    capture = ProcessCapture(
        command=["python", "-m", "patchops.cli", "profiles"],
        working_directory=str(Path("C:/dev/patchops")),
        exit_code=1,
        stdout="",
        stderr="ModuleNotFoundError: No module named 'patchops'\n",
    )
    assert _classify_failure(setup_error=None, capture=capture) == "wrapper_failure"


def test_missing_python_executable_is_environment_failure() -> None:
    setup_error = FileNotFoundError("[Errno 2] No such file or directory: 'C:/Python312/python.exe'")
    assert _classify_failure(setup_error=setup_error, capture=None) == "environment_failure"


def test_missing_powershell_executable_is_environment_failure() -> None:
    setup_error = FileNotFoundError("[Errno 2] No such file or directory: 'pwsh.exe'")
    assert _classify_failure(setup_error=setup_error, capture=None) == "environment_failure"
