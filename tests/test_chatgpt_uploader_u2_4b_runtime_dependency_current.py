from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from patchops.chatgpt_uploader import runtime_dependency
from patchops.chatgpt_uploader.runtime_dependency import ensure_dependencies, write_dependency_evidence

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_available_stdlib_dependency_passes_without_install() -> None:
    result = ensure_dependencies(packages=["json"], allow_install=False)
    assert result.status == "PASS"
    assert result.checks[0]["available_before"] is True
    assert result.checks[0]["install_attempted"] is False
    assert result.checks[0]["available_after"] is True


def test_missing_dependency_blocks_without_install(monkeypatch) -> None:
    monkeypatch.setattr(runtime_dependency, "import_available", lambda name: False)
    result = ensure_dependencies(packages=["definitely_missing_package_for_patchops"], allow_install=False)
    assert result.status == "BLOCKED_DEPENDENCY_UNAVAILABLE"
    assert result.checks[0]["status"] == "BLOCKED_MISSING_NOT_INSTALLED"
    assert result.checks[0]["install_attempted"] is False


def test_install_failure_is_controlled(monkeypatch) -> None:
    seen: list[str] = []

    def fake_available(name: str) -> bool:
        seen.append(name)
        return False

    def fake_install(package: str, *, timeout_seconds: int = 240):
        return 123, "stdout", "stderr"

    monkeypatch.setattr(runtime_dependency, "import_available", fake_available)
    monkeypatch.setattr(runtime_dependency, "install_package", fake_install)
    result = ensure_dependencies(packages=["missing-package"], allow_install=True)
    assert result.status == "BLOCKED_DEPENDENCY_UNAVAILABLE"
    assert result.checks[0]["install_attempted"] is True
    assert result.checks[0]["install_exit_code"] == 123
    assert result.checks[0]["status"] == "BLOCKED_INSTALL_FAILED"


def test_write_dependency_evidence(tmp_path) -> None:
    result = ensure_dependencies(packages=["json"], allow_install=False)
    json_path, txt_path = write_dependency_evidence(result, tmp_path)
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert payload["checks"][0]["package"] == "json"
    text = txt_path.read_text(encoding="utf-8")
    assert "PATCHOPS CHATGPT UPLOADER RUNTIME DEPENDENCIES" in text
    assert "Package          : json" in text


def test_dependency_script_no_install_controlled(tmp_path) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "ensure_chatgpt_uploader_runtime_deps.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--evidence-dir",
            str(tmp_path / "evidence"),
            "--package",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "PATCHOPS_UPLOADER_RUNTIME_DEPENDENCY_STATUS: PASS" in result.stdout
    assert "INSTALL_ATTEMPTED: false" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout
