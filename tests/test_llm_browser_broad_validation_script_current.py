from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_llm_browser_broad_validation_script_exists_and_has_operator_contract() -> None:
    text = _read("scripts/llm_browser_broad_validation.ps1")

    required = [
        "PATCHOPS LLM-BROWSER BROAD VALIDATION",
        "patchops_llm_browser_broad_validation_",
        "Invoke-NativeCapture",
        "TimeoutFullPytestSeconds",
        "PlanOnly",
        "SkipFullPytest",
        "compileall patchops tests",
        "llm-browser release-gate",
        "llm-browser checkpoint",
        "llm-browser doctor none",
        "llm-browser audit-log missing-file readback",
        "full pytest",
        "Write-Utf8NoBom",
        "Commands captured",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_llm_browser_broad_validation_script_captures_stdout_stderr_and_uses_timeouts() -> None:
    text = _read("scripts/llm_browser_broad_validation.ps1")

    required = [
        "RedirectStandardOutput = $true",
        "RedirectStandardError = $true",
        "WaitForExit([Math]::Max(1, $TimeoutSeconds) * 1000)",
        "TimedOut",
        "--- STDOUT ---",
        "--- STDERR ---",
        "$script:Failures",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []


def test_llm_browser_broad_validation_script_avoids_known_hanging_or_runspace_patterns() -> None:
    text = _read("scripts/llm_browser_broad_validation.ps1")

    forbidden = [
        "Start-Job",
        "Register-ObjectEvent",
        "BeginOutputReadLine",
        "BeginErrorReadLine",
        "add_OutputDataReceived",
        "add_ErrorDataReceived",
        "git commit",
        "git push",
        "--auto-send",
        "--allow-send",
    ]

    present = [item for item in forbidden if item in text]
    assert present == []


def test_llm_browser_runner_doc_links_d0_30_broad_validation_script() -> None:
    text = _read("docs/llm_browser_runner.md")

    required = [
        "D0.30 operator broad validation script",
        "scripts/llm_browser_broad_validation.ps1",
        "single Desktop report",
        "PlanOnly",
        "SkipFullPytest",
        "full pytest",
        "does not run git commit",
        "does not run git push",
    ]

    missing = [item for item in required if item not in text]
    assert missing == []
