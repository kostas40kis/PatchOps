from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from patchops.bundles import (
    build_bundled_launcher_command,
    invoke_bundled_launcher,
    resolve_bundle_launcher,
    resolve_bundled_launcher,
)


def test_resolve_bundled_launcher_prefers_root_single_launcher_for_both_modes(tmp_path: Path) -> None:
    root_launcher = tmp_path / "run_with_patchops.ps1"
    root_launcher.write_text("# root launcher\n", encoding="utf-8")

    launchers_dir = tmp_path / "launchers"
    launchers_dir.mkdir()
    (launchers_dir / "apply_with_patchops.ps1").write_text("# legacy apply\n", encoding="utf-8")
    (launchers_dir / "verify_with_patchops.ps1").write_text("# legacy verify\n", encoding="utf-8")

    apply_resolution = resolve_bundled_launcher(tmp_path, mode="apply")
    verify_resolution = resolve_bundle_launcher(tmp_path, mode="verify")

    assert apply_resolution.launcher_path == root_launcher
    assert apply_resolution.launcher_kind == "root_single"
    assert verify_resolution.launcher_path == root_launcher
    assert verify_resolution.launcher_kind == "root_single"


def test_resolve_bundled_launcher_falls_back_to_legacy_dual_launchers(tmp_path: Path) -> None:
    launchers_dir = tmp_path / "launchers"
    launchers_dir.mkdir()
    apply_launcher = launchers_dir / "apply_with_patchops.ps1"
    verify_launcher = launchers_dir / "verify_with_patchops.ps1"
    apply_launcher.write_text("# legacy apply\n", encoding="utf-8")
    verify_launcher.write_text("# legacy verify\n", encoding="utf-8")

    apply_resolution = resolve_bundled_launcher(tmp_path, mode="apply")
    verify_resolution = resolve_bundled_launcher(tmp_path, mode="verify")

    assert apply_resolution.launcher_path == apply_launcher
    assert apply_resolution.launcher_kind == "legacy_dual"
    assert verify_resolution.launcher_path == verify_launcher
    assert verify_resolution.launcher_kind == "legacy_dual"


def test_resolve_bundled_launcher_rejects_missing_launcher(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError) as exc:
        resolve_bundled_launcher(tmp_path, mode="apply")

    text = str(exc.value)
    assert "run_with_patchops.ps1" in text
    assert "apply_with_patchops.ps1" in text


def test_build_bundled_launcher_command_uses_stable_powershell_shape(tmp_path: Path) -> None:
    launcher_path = tmp_path / "run_with_patchops.ps1"
    launcher_path.write_text("# root launcher\n", encoding="utf-8")
    resolution = resolve_bundled_launcher(tmp_path, mode="apply")

    command = build_bundled_launcher_command(
        resolution,
        r"C:\dev\patchops",
        powershell_program="pwsh",
    )

    assert command == (
        "pwsh",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(launcher_path),
        "-WrapperRepoRoot",
        r"C:\dev\patchops",
    )


def test_invoke_bundled_launcher_runs_subprocess_in_bundle_root_and_captures_output(monkeypatch, tmp_path: Path) -> None:
    launcher_path = tmp_path / "run_with_patchops.ps1"
    launcher_path.write_text("# root launcher\n", encoding="utf-8")

    calls: list[dict[str, object]] = []

    def fake_run(command, *, cwd, capture_output, text, check, env):
        calls.append(
            {
                "command": tuple(command),
                "cwd": cwd,
                "capture_output": capture_output,
                "text": text,
                "check": check,
                "env": dict(env) if env is not None else None,
            }
        )
        return subprocess.CompletedProcess(command, 0, stdout="launcher ok", stderr="")

    monkeypatch.setattr("patchops.bundles.launcher_invoker.subprocess.run", fake_run)

    result = invoke_bundled_launcher(
        tmp_path,
        r"C:\dev\patchops",
        mode="apply",
        powershell_program="powershell",
        env={"PATCHOPS_TEST_MODE": "1"},
    )

    assert result.ok is True
    assert result.exit_code == 0
    assert result.stdout == "launcher ok"
    assert result.stderr == ""
    assert result.cwd == tmp_path
    assert result.resolution.launcher_path == launcher_path
    assert result.command[0] == "powershell"

    assert calls == [
        {
            "command": (
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(launcher_path),
                "-WrapperRepoRoot",
                r"C:\dev\patchops",
            ),
            "cwd": str(tmp_path),
            "capture_output": True,
            "text": True,
            "check": False,
            "env": {"PATCHOPS_TEST_MODE": "1"},
        }
    ]


def test_invoke_bundled_launcher_preserves_nonzero_exit_and_stderr(monkeypatch, tmp_path: Path) -> None:
    launcher_path = tmp_path / "run_with_patchops.ps1"
    launcher_path.write_text("# root launcher\n", encoding="utf-8")

    def fake_run(command, *, cwd, capture_output, text, check, env):
        return subprocess.CompletedProcess(command, 7, stdout="", stderr="boom")

    monkeypatch.setattr("patchops.bundles.launcher_invoker.subprocess.run", fake_run)

    result = invoke_bundled_launcher(tmp_path, r"C:\dev\patchops", mode="verify")

    assert result.ok is False
    assert result.exit_code == 7
    assert result.stderr == "boom"
    assert result.resolution.mode == "verify"
