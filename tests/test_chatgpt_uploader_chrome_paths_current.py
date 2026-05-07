from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_paths import (
    BLOCKED_CHROME_NOT_FOUND,
    BLOCKED_CHROME_PATH_INVALID,
    PASS_CHROME_EXECUTABLE_FOUND,
    CHROME_EXE_NAME,
    discover_chrome_executable,
    is_valid_chrome_executable,
    redact_path,
    write_discovery_evidence,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _fake_chrome(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("fake chrome executable for tests", encoding="utf-8")
    return path


def test_discovers_patchops_chrome_path_before_other_candidates(tmp_path: Path) -> None:
    explicit = _fake_chrome(tmp_path / "explicit" / CHROME_EXE_NAME)
    fallback = _fake_chrome(tmp_path / "fallback" / CHROME_EXE_NAME)

    result = discover_chrome_executable(
        env={"PATCHOPS_CHROME_PATH": str(explicit)},
        search_order=[
            ("PATCHOPS_CHROME_PATH", explicit, True),
            ("LOCALAPPDATA", fallback, False),
        ],
    )

    assert result.ok is True
    assert result.result == PASS_CHROME_EXECUTABLE_FOUND
    assert result.browser == "chrome"
    assert result.executable_path == str(explicit.resolve())
    assert result.executable_basename == CHROME_EXE_NAME
    assert result.candidates[0].source == "PATCHOPS_CHROME_PATH"
    assert result.candidates[0].selected is True
    assert result.safety_flags["browser_launched"] is False
    assert result.safety_flags["file_upload_attempted"] is False
    assert result.safety_flags["chatgpt_submit_performed"] is False
    assert result.safety_flags["webdriver_used"] is False


def test_invalid_explicit_path_blocks_without_falling_back(tmp_path: Path) -> None:
    invalid = tmp_path / "missing" / CHROME_EXE_NAME
    fallback = _fake_chrome(tmp_path / "fallback" / CHROME_EXE_NAME)

    result = discover_chrome_executable(
        search_order=[
            ("PATCHOPS_CHROME_PATH", invalid, True),
            ("LOCALAPPDATA", fallback, False),
        ]
    )

    assert result.ok is False
    assert result.result == BLOCKED_CHROME_PATH_INVALID
    assert result.executable_path is None
    assert len(result.candidates) == 1
    assert result.candidates[0].source == "PATCHOPS_CHROME_PATH"
    assert result.candidates[0].exists is False


def test_finds_first_valid_default_candidate(tmp_path: Path) -> None:
    missing = tmp_path / "missing" / CHROME_EXE_NAME
    valid = _fake_chrome(tmp_path / "default" / "Application" / CHROME_EXE_NAME)

    result = discover_chrome_executable(
        search_order=[
            ("LOCALAPPDATA", missing, False),
            ("PROGRAMFILES", valid, False),
        ]
    )

    assert result.ok is True
    assert result.result == PASS_CHROME_EXECUTABLE_FOUND
    assert result.executable_path == str(valid.resolve())
    assert len(result.candidates) == 2
    assert result.candidates[0].selected is False
    assert result.candidates[1].selected is True


def test_not_found_result_is_blocked_not_failure(tmp_path: Path) -> None:
    result = discover_chrome_executable(
        search_order=[
            ("LOCALAPPDATA", tmp_path / "a" / CHROME_EXE_NAME, False),
            ("PROGRAMFILES", tmp_path / "b" / CHROME_EXE_NAME, False),
        ]
    )

    assert result.ok is False
    assert result.result == BLOCKED_CHROME_NOT_FOUND
    assert result.executable_path is None
    assert result.candidate_count == 2
    assert all(candidate.selected is False for candidate in result.candidates)


def test_valid_chrome_requires_file_named_chrome_exe(tmp_path: Path) -> None:
    chrome = _fake_chrome(tmp_path / CHROME_EXE_NAME)
    wrong_name = _fake_chrome(tmp_path / "chromium.exe")
    directory_named_chrome = tmp_path / "dir" / CHROME_EXE_NAME
    directory_named_chrome.mkdir(parents=True)

    assert is_valid_chrome_executable(chrome) is True
    assert is_valid_chrome_executable(wrong_name) is False
    assert is_valid_chrome_executable(directory_named_chrome) is False


def test_redacted_path_does_not_expose_parent_directories(tmp_path: Path) -> None:
    chrome = _fake_chrome(tmp_path / "very" / "secret" / "folder" / CHROME_EXE_NAME)
    redacted = redact_path(chrome)

    assert CHROME_EXE_NAME in redacted
    assert "secret" not in redacted
    assert "folder" not in redacted
    assert str(chrome.parent) not in redacted


def test_write_discovery_evidence_can_omit_exact_path(tmp_path: Path) -> None:
    chrome = _fake_chrome(tmp_path / "Chrome" / CHROME_EXE_NAME)
    result = discover_chrome_executable(search_order=[("CLI", chrome, False)])
    evidence_path = write_discovery_evidence(result, tmp_path / "evidence.json", include_executable_path=False)

    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert payload["result"] == PASS_CHROME_EXECUTABLE_FOUND
    assert payload["executable_path"] is None
    assert payload["executable_basename"] == CHROME_EXE_NAME
    assert payload["safety_flags"]["browser_launched"] is False
    assert payload["safety_flags"]["file_upload_attempted"] is False


def test_probe_script_outputs_json_and_evidence(tmp_path: Path) -> None:
    chrome = _fake_chrome(tmp_path / "chrome-bin" / CHROME_EXE_NAME)
    evidence_path = tmp_path / "probe.json"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_executable_probe.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--candidate",
            f"TEST={chrome}",
            "--evidence-path",
            str(evidence_path),
            "--json",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["result"] == PASS_CHROME_EXECUTABLE_FOUND
    assert payload["browser"] == "chrome"
    assert payload["executable_path"] is None
    assert payload["executable_basename"] == CHROME_EXE_NAME
    assert payload["safety_flags"]["selenium_used"] is False
    assert payload["safety_flags"]["webdriver_used"] is False
    assert payload["safety_flags"]["browser_dom_automation_used"] is False
    assert payload["safety_flags"]["browser_launched"] is False

    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["result"] == PASS_CHROME_EXECUTABLE_FOUND
    assert evidence["executable_path"] is None


def test_probe_script_returns_zero_for_blocked_not_found(tmp_path: Path) -> None:
    missing = tmp_path / "missing" / CHROME_EXE_NAME
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_executable_probe.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--candidate",
            f"TEST={missing}",
            "--json",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["result"] == BLOCKED_CHROME_NOT_FOUND
    assert payload["ok"] is False
    assert payload["safety_flags"]["browser_launched"] is False


def test_chrome_paths_patch_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]

    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_paths_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_paths.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_executable_probe.py",
    ]

    forbidden_import_or_dependency_tokens = [
        "import selenium",
        "from selenium",
        "selenium.",
        "webdriver.chrome",
        "webdriver.edge",
        "chromedriver",
        "pywinauto",
        "playwright",
    ]

    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden_import_or_dependency_tokens:
            assert token not in text

    combined = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths)
    assert '"webdriver_used": false' in combined
    assert '"browser_dom_automation_used": false' in combined