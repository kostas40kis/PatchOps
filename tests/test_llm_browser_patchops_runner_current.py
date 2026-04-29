from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess

import pytest

from patchops.llm_browser.patchops_runner import (
    build_run_package_command,
    extract_report_path,
    interpret_run_package_result,
    parse_run_package_payload,
    resolve_patchops_python_command,
    run_patchops_package,
)


@dataclass
class FakeCompleted:
    returncode: int
    stdout: str
    stderr: str = ""


def test_resolve_patchops_python_command_prefers_venv_python(tmp_path: Path) -> None:
    python_exe = tmp_path / ".venv" / "Scripts" / "python.exe"
    python_exe.parent.mkdir(parents=True)
    python_exe.write_text("", encoding="utf-8")

    assert resolve_patchops_python_command(tmp_path) == (str(python_exe),)


def test_resolve_patchops_python_command_falls_back_to_py_launcher(tmp_path: Path) -> None:
    assert resolve_patchops_python_command(tmp_path) == ("py", "-3")


def test_build_run_package_command_is_stable(tmp_path: Path) -> None:
    artifact = tmp_path / "patch_d0_15_patchops_subprocess_runner_patchops_bundle.zip"
    artifact.write_bytes(b"zip")
    wrapper = tmp_path / "wrapper"
    wrapper.mkdir()

    command = build_run_package_command(
        artifact,
        wrapper_root=wrapper,
        timeout_seconds=123,
        python_command=("python",),
    )

    assert command.command == (
        "python",
        "-m",
        "patchops.cli",
        "run-package",
        str(artifact),
        "--wrapper-root",
        str(wrapper),
    )
    assert command.cwd == wrapper
    assert command.timeout_seconds == 123
    assert command.to_payload()["artifact_path"] == str(artifact)


def test_build_run_package_command_validates_inputs(tmp_path: Path) -> None:
    wrapper = tmp_path / "wrapper"
    wrapper.mkdir()
    artifact = tmp_path / "missing.zip"

    with pytest.raises(FileNotFoundError, match="artifact"):
        build_run_package_command(artifact, wrapper_root=wrapper)

    artifact.write_bytes(b"zip")
    with pytest.raises(FileNotFoundError, match="wrapper root"):
        build_run_package_command(artifact, wrapper_root=tmp_path / "missing-wrapper")

    with pytest.raises(ValueError, match="timeout_seconds"):
        build_run_package_command(artifact, wrapper_root=wrapper, timeout_seconds=0)

    with pytest.raises(ValueError, match="python_command"):
        build_run_package_command(artifact, wrapper_root=wrapper, python_command=())


def test_parse_run_package_payload_reads_plain_json() -> None:
    payload = parse_run_package_payload('{"ok": true, "outer_report_path": "C:\\\\Users\\\\kostas\\\\Desktop\\\\report.txt"}')

    assert payload is not None
    assert payload["ok"] is True


def test_parse_run_package_payload_reads_json_inside_noise() -> None:
    stdout = 'banner\n{"ok": false, "failure_category": "target_content_failure"}\ntrailer'

    payload = parse_run_package_payload(stdout)

    assert payload is not None
    assert payload["ok"] is False
    assert payload["failure_category"] == "target_content_failure"


def test_extract_report_path_prefers_payload_report_path() -> None:
    assert extract_report_path(
        "C:\\Users\\kostas\\Desktop\\other.txt",
        {"outer_report_path": "C:\\Users\\kostas\\Desktop\\preferred.txt"},
    ) == "C:\\Users\\kostas\\Desktop\\preferred.txt"


def test_extract_report_path_falls_back_to_last_windows_txt_path() -> None:
    stdout = """
    first C:\\Users\\kostas\\Desktop\\old.txt
    later C:\\Users\\kostas\\Desktop\\patchops_run_package_20260429_191500.txt
    """

    assert extract_report_path(stdout) == "C:\\Users\\kostas\\Desktop\\patchops_run_package_20260429_191500.txt"


def test_interpret_result_fails_on_nonzero_exit_code(tmp_path: Path) -> None:
    artifact = tmp_path / "patch.zip"
    artifact.write_bytes(b"zip")
    command = build_run_package_command(artifact, wrapper_root=tmp_path, python_command=("python",))

    result = interpret_run_package_result(
        command=command,
        exit_code=1,
        stdout="",
        stderr="boom",
        timed_out=False,
    )

    assert result.ok is False
    assert result.reason == "nonzero_exit_code"


def test_interpret_result_fails_closed_on_payload_ok_false_even_with_zero_exit(tmp_path: Path) -> None:
    artifact = tmp_path / "patch.zip"
    artifact.write_bytes(b"zip")
    command = build_run_package_command(artifact, wrapper_root=tmp_path, python_command=("python",))
    stdout = '{"ok": false, "failure_category": "target_content_failure", "outer_report_path": "C:\\\\Users\\\\kostas\\\\Desktop\\\\report.txt"}'

    result = interpret_run_package_result(
        command=command,
        exit_code=0,
        stdout=stdout,
        stderr="",
        timed_out=False,
    )

    assert result.ok is False
    assert result.reason == "patchops_payload_ok_false"
    assert result.failure_category == "target_content_failure"
    assert result.report_path == "C:\\Users\\kostas\\Desktop\\report.txt"


def test_interpret_result_fails_closed_on_inner_result_fail_even_with_zero_exit(tmp_path: Path) -> None:
    artifact = tmp_path / "patch.zip"
    artifact.write_bytes(b"zip")
    command = build_run_package_command(artifact, wrapper_root=tmp_path, python_command=("python",))
    stdout = '{"ok": true, "inner_result": "FAIL"}'

    result = interpret_run_package_result(
        command=command,
        exit_code=0,
        stdout=stdout,
        stderr="",
        timed_out=False,
    )

    assert result.ok is False
    assert result.reason == "patchops_inner_result_fail"


def test_interpret_result_reports_timeout(tmp_path: Path) -> None:
    artifact = tmp_path / "patch.zip"
    artifact.write_bytes(b"zip")
    command = build_run_package_command(artifact, wrapper_root=tmp_path, python_command=("python",))

    result = interpret_run_package_result(
        command=command,
        exit_code=None,
        stdout="",
        stderr="",
        timed_out=True,
    )

    assert result.ok is False
    assert result.reason == "timeout"
    assert result.exit_code is None


def test_run_patchops_package_uses_injected_runner(tmp_path: Path) -> None:
    artifact = tmp_path / "patch_d0_15_patchops_subprocess_runner_patchops_bundle.zip"
    artifact.write_bytes(b"zip")
    wrapper = tmp_path / "wrapper"
    wrapper.mkdir()
    calls = []

    def fake_runner(command, cwd, timeout_seconds, env):
        calls.append((tuple(command), cwd, timeout_seconds, env))
        return FakeCompleted(
            0,
            '{"ok": true, "outer_report_path": "C:\\\\Users\\\\kostas\\\\Desktop\\\\patchops_run_package.txt"}',
        )

    result = run_patchops_package(
        artifact,
        wrapper_root=wrapper,
        timeout_seconds=77,
        python_command=("python",),
        env={"EXAMPLE": "1"},
        process_runner=fake_runner,
    )

    assert result.ok is True
    assert result.reason == "success"
    assert result.report_path == "C:\\Users\\kostas\\Desktop\\patchops_run_package.txt"
    assert calls
    assert calls[0][0][:4] == ("python", "-m", "patchops.cli", "run-package")
    assert calls[0][1] == wrapper
    assert calls[0][2] == 77
    assert calls[0][3] == {"EXAMPLE": "1"}


def test_run_patchops_package_handles_timeout_from_injected_runner(tmp_path: Path) -> None:
    artifact = tmp_path / "patch_d0_15_patchops_subprocess_runner_patchops_bundle.zip"
    artifact.write_bytes(b"zip")
    wrapper = tmp_path / "wrapper"
    wrapper.mkdir()

    def timeout_runner(command, cwd, timeout_seconds, env):
        raise subprocess.TimeoutExpired(command, timeout_seconds, output="partial out", stderr="partial err")

    result = run_patchops_package(
        artifact,
        wrapper_root=wrapper,
        timeout_seconds=5,
        python_command=("python",),
        process_runner=timeout_runner,
    )

    assert result.ok is False
    assert result.reason == "timeout"
    assert result.timed_out is True
    assert result.stdout == "partial out"
    assert result.stderr == "partial err"


def test_run_result_payload_is_compact(tmp_path: Path) -> None:
    artifact = tmp_path / "patch_d0_15_patchops_subprocess_runner_patchops_bundle.zip"
    artifact.write_bytes(b"zip")
    wrapper = tmp_path / "wrapper"
    wrapper.mkdir()

    result = run_patchops_package(
        artifact,
        wrapper_root=wrapper,
        python_command=("python",),
        process_runner=lambda command, cwd, timeout_seconds, env: FakeCompleted(0, '{"ok": true}'),
    )

    payload = result.to_payload()

    assert payload["ok"] is True
    assert payload["reason"] == "success"
    assert payload["stdout_length"] == len('{"ok": true}')
    assert payload["stderr_length"] == 0
    assert payload["command"]["artifact_path"] == str(artifact)
