"""Canonical report locator for the optional LLM browser runner.

This module resolves the canonical PatchOps report produced by a run-package
execution. It is deliberately passive:
- it imports no Selenium modules,
- it starts no browser driver,
- it does not run PatchOps,
- it does not click or download anything,
- it only interprets runner metadata and inspects local report files.

The locator prefers explicit report paths from PatchOpsRunResult payloads, then
stdout-discovered paths, then newest Desktop/runtime report candidates.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable, Mapping, Sequence

from .patchops_runner import PatchOpsRunResult, extract_report_path


_WINDOWS_TXT_PATH_RE = re.compile(
    r"(?P<path>[A-Za-z]:\\[^\r\n\"<>|?*]+?\.txt)",
    re.IGNORECASE,
)

_RESULT_RE = re.compile(r"^\s*Result\s*:?\s*(?P<value>PASS|FAIL)\s*$", re.IGNORECASE | re.MULTILINE)
_EXIT_RE = re.compile(r"^\s*Exit\s*Code\s*:?\s*(?P<value>-?\d+)\s*$", re.IGNORECASE | re.MULTILINE)
_EXITCODE_RE = re.compile(r"^\s*ExitCode\s*:?\s*(?P<value>-?\d+)\s*$", re.IGNORECASE | re.MULTILINE)
# Important: require a real Patch field delimiter. Do not match report headings
# like "PATCHOPS RUN-PACKAGE OUTER REPORT".
_PATCH_RE = re.compile(r"^\s*Patch\s*:\s*(?P<value>.+?)\s*$", re.IGNORECASE | re.MULTILINE)
_FAILURE_CATEGORY_RE = re.compile(
    r"^\s*(Failure\s*Category|FailureCategory)\s*:?\s*(?P<value>.*?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass(frozen=True)
class CanonicalReportSummary:
    path: Path
    result: str | None
    exit_code: int | None
    patch: str | None
    failure_category: str | None
    text_length: int

    @property
    def passed(self) -> bool:
        return (self.result or "").upper() == "PASS" and self.exit_code == 0

    def to_payload(self) -> dict[str, object]:
        return {
            "path": str(self.path),
            "result": self.result,
            "exit_code": self.exit_code,
            "patch": self.patch,
            "failure_category": self.failure_category,
            "text_length": self.text_length,
            "passed": self.passed,
        }


@dataclass(frozen=True)
class CanonicalReportLocation:
    found: bool
    path: Path | None
    reason: str
    source: str | None
    summary: CanonicalReportSummary | None
    candidates_seen: tuple[Path, ...]

    def to_payload(self) -> dict[str, object]:
        return {
            "found": self.found,
            "path": None if self.path is None else str(self.path),
            "reason": self.reason,
            "source": self.source,
            "summary": None if self.summary is None else self.summary.to_payload(),
            "candidates_seen": [str(path) for path in self.candidates_seen],
        }


def _payload_report_path(payload: Mapping[str, object] | None) -> str | None:
    if payload is None:
        return None

    for key in (
        "outer_report_path",
        "OuterReportPath",
        "inner_report_path",
        "InnerReportPath",
        "report_path",
        "ReportPath",
        "outerReportPath",
        "innerReportPath",
    ):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    return None


def report_paths_from_text(text: str) -> tuple[str, ...]:
    values: list[str] = []
    seen: set[str] = set()

    for match in _WINDOWS_TXT_PATH_RE.finditer(text or ""):
        value = match.group("path").strip()
        key = value.lower()
        if key not in seen:
            seen.add(key)
            values.append(value)

    for line in (text or "").splitlines():
        stripped = line.strip()
        if stripped.lower().endswith(".txt"):
            key = stripped.lower()
            if key not in seen:
                seen.add(key)
                values.append(stripped)

    return tuple(values)


def candidate_report_paths_from_runner(result: PatchOpsRunResult) -> tuple[Path, ...]:
    values: list[str] = []

    explicit = _payload_report_path(result.parsed_payload)
    if explicit:
        values.append(explicit)

    extracted = result.report_path or extract_report_path(result.stdout, result.parsed_payload)
    if extracted:
        values.append(extracted)

    values.extend(report_paths_from_text(result.stdout))
    values.extend(report_paths_from_text(result.stderr))

    seen: set[str] = set()
    paths: list[Path] = []
    for value in values:
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        paths.append(Path(value))

    return tuple(paths)


def newest_report_candidate(
    roots: Iterable[str | Path],
    *,
    patterns: Sequence[str] = ("patchops_run_package_*.txt", "patchops_*.txt"),
) -> Path | None:
    candidates: list[Path] = []
    for root_value in roots:
        root = Path(root_value)
        if not root.exists() or not root.is_dir():
            continue
        for pattern in patterns:
            candidates.extend(path for path in root.glob(pattern) if path.is_file())

    if not candidates:
        return None

    return max(candidates, key=lambda path: (path.stat().st_mtime, path.name))


def parse_report_summary(path: str | Path) -> CanonicalReportSummary:
    target = Path(path)
    text = target.read_text(encoding="utf-8", errors="replace")

    result_match = _RESULT_RE.search(text)
    exit_match = _EXIT_RE.search(text) or _EXITCODE_RE.search(text)
    patch_match = _PATCH_RE.search(text)
    failure_match = _FAILURE_CATEGORY_RE.search(text)

    exit_code = None
    if exit_match:
        try:
            exit_code = int(exit_match.group("value"))
        except ValueError:
            exit_code = None

    failure_category = None
    if failure_match:
        value = failure_match.group("value").strip()
        failure_category = value or None

    return CanonicalReportSummary(
        path=target,
        result=None if result_match is None else result_match.group("value").upper(),
        exit_code=exit_code,
        patch=None if patch_match is None else patch_match.group("value").strip(),
        failure_category=failure_category,
        text_length=len(text),
    )


def locate_canonical_report(
    *,
    runner_result: PatchOpsRunResult | None = None,
    search_roots: Iterable[str | Path] = (),
) -> CanonicalReportLocation:
    candidates: list[Path] = []

    if runner_result is not None:
        candidates.extend(candidate_report_paths_from_runner(runner_result))

    existing_candidates: list[Path] = []
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            existing_candidates.append(candidate)

    if existing_candidates:
        path = existing_candidates[0]
        return CanonicalReportLocation(
            found=True,
            path=path,
            reason="explicit_report_path_found",
            source="runner_result",
            summary=parse_report_summary(path),
            candidates_seen=tuple(candidates),
        )

    newest = newest_report_candidate(search_roots)
    if newest is not None:
        all_candidates = tuple(candidates + [newest])
        return CanonicalReportLocation(
            found=True,
            path=newest,
            reason="newest_report_candidate_found",
            source="search_roots",
            summary=parse_report_summary(newest),
            candidates_seen=all_candidates,
        )

    if candidates:
        return CanonicalReportLocation(
            found=False,
            path=None,
            reason="explicit_report_paths_missing",
            source="runner_result",
            summary=None,
            candidates_seen=tuple(candidates),
        )

    return CanonicalReportLocation(
        found=False,
        path=None,
        reason="no_report_candidates",
        source=None,
        summary=None,
        candidates_seen=(),
    )
