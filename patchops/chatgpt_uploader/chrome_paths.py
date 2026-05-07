from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping

PASS_CHROME_EXECUTABLE_FOUND = "PASS_CHROME_EXECUTABLE_FOUND"
BLOCKED_CHROME_NOT_FOUND = "BLOCKED_CHROME_NOT_FOUND"
BLOCKED_CHROME_PATH_INVALID = "BLOCKED_CHROME_PATH_INVALID"

CHROME_ONLY_BROWSER = "chrome"
CHROME_EXE_NAME = "chrome.exe"
CHROME_ENV_VARS = ("PATCHOPS_CHROME_PATH", "CHROME_PATH")

SAFETY_FLAGS = {
    "selenium_used": False,
    "webdriver_used": False,
    "browser_dom_automation_used": False,
    "cloudflare_bypass_attempted": False,
    "captcha_bypass_attempted": False,
    "conversation_text_logged": False,
    "random_page_click_performed": False,
    "chatgpt_submit_performed": False,
    "file_upload_attempted": False,
    "live_browser_used": False,
    "browser_launched": False,
}


@dataclass(frozen=True)
class ChromeCandidateEvidence:
    source: str
    basename: str
    redacted_path: str
    exists: bool
    is_file: bool
    executable_name_match: bool
    selected: bool = False


@dataclass(frozen=True)
class ChromeDiscoveryResult:
    ok: bool
    result: str
    browser: str
    executable_path: str | None
    executable_basename: str | None
    executable_redacted_path: str | None
    candidate_count: int
    candidates: list[ChromeCandidateEvidence]
    safety_flags: dict[str, bool]

    def to_payload(self, *, include_executable_path: bool = True) -> dict[str, object]:
        payload = asdict(self)
        payload["candidates"] = [asdict(candidate) for candidate in self.candidates]
        if not include_executable_path:
            payload["executable_path"] = None
        return payload


def default_chrome_candidate_paths(env: Mapping[str, str] | None = None) -> list[tuple[str, Path]]:
    source_env = os.environ if env is None else env
    candidates: list[tuple[str, Path]] = []

    local_app_data = source_env.get("LOCALAPPDATA") or os.environ.get("LOCALAPPDATA")
    if local_app_data:
        candidates.append(("LOCALAPPDATA", Path(local_app_data) / "Google" / "Chrome" / "Application" / CHROME_EXE_NAME))

    candidates.extend(
        [
            ("PROGRAMFILES", Path("C:/Program Files/Google/Chrome/Application") / CHROME_EXE_NAME),
            ("PROGRAMFILES_X86", Path("C:/Program Files (x86)/Google/Chrome/Application") / CHROME_EXE_NAME),
        ]
    )
    return candidates


def chrome_search_order(env: Mapping[str, str] | None = None) -> list[tuple[str, Path, bool]]:
    source_env = os.environ if env is None else env
    ordered: list[tuple[str, Path, bool]] = []

    for variable_name in CHROME_ENV_VARS:
        raw_value = source_env.get(variable_name)
        if raw_value:
            ordered.append((variable_name, Path(raw_value).expanduser(), True))

    for source, path in default_chrome_candidate_paths(source_env):
        ordered.append((source, path, False))

    return ordered


def redact_path(path: Path | str) -> str:
    path_obj = Path(path)
    drive = path_obj.drive
    basename = path_obj.name or "<unknown>"
    if drive:
        return f"{drive}/.../{basename}"
    return f".../{basename}"


def _candidate_evidence(source: str, path: Path, *, selected: bool = False) -> ChromeCandidateEvidence:
    exists = path.exists()
    is_file = path.is_file() if exists else False
    name_match = path.name.lower() == CHROME_EXE_NAME
    return ChromeCandidateEvidence(
        source=source,
        basename=path.name,
        redacted_path=redact_path(path),
        exists=exists,
        is_file=is_file,
        executable_name_match=name_match,
        selected=selected,
    )


def is_valid_chrome_executable(path: Path | str) -> bool:
    candidate = Path(path).expanduser()
    return candidate.exists() and candidate.is_file() and candidate.name.lower() == CHROME_EXE_NAME


def discover_chrome_executable(
    *,
    env: Mapping[str, str] | None = None,
    search_order: Iterable[tuple[str, Path | str, bool]] | None = None,
) -> ChromeDiscoveryResult:
    ordered = list(search_order if search_order is not None else chrome_search_order(env))
    evidence: list[ChromeCandidateEvidence] = []

    for source, raw_path, is_explicit in ordered:
        path = Path(raw_path).expanduser()
        valid = is_valid_chrome_executable(path)
        evidence.append(_candidate_evidence(source, path, selected=valid))

        if valid:
            return ChromeDiscoveryResult(
                ok=True,
                result=PASS_CHROME_EXECUTABLE_FOUND,
                browser=CHROME_ONLY_BROWSER,
                executable_path=str(path.resolve()),
                executable_basename=path.name,
                executable_redacted_path=redact_path(path),
                candidate_count=len(ordered),
                candidates=evidence,
                safety_flags=dict(SAFETY_FLAGS),
            )

        if is_explicit:
            return ChromeDiscoveryResult(
                ok=False,
                result=BLOCKED_CHROME_PATH_INVALID,
                browser=CHROME_ONLY_BROWSER,
                executable_path=None,
                executable_basename=None,
                executable_redacted_path=redact_path(path),
                candidate_count=len(ordered),
                candidates=evidence,
                safety_flags=dict(SAFETY_FLAGS),
            )

    return ChromeDiscoveryResult(
        ok=False,
        result=BLOCKED_CHROME_NOT_FOUND,
        browser=CHROME_ONLY_BROWSER,
        executable_path=None,
        executable_basename=None,
        executable_redacted_path=None,
        candidate_count=len(ordered),
        candidates=evidence,
        safety_flags=dict(SAFETY_FLAGS),
    )


def write_discovery_evidence(result: ChromeDiscoveryResult, path: Path | str, *, include_executable_path: bool = True) -> Path:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result.to_payload(include_executable_path=include_executable_path), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_path