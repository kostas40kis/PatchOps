from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import zipfile
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

DEFAULT_FAILURE_CATEGORY = "ambiguous_evidence"

@dataclass(slots=True)
class ProcessCapture:
    command: list[str]
    working_directory: str
    exit_code: int
    stdout: str
    stderr: str

@dataclass(slots=True)
class InnerReportSummary:
    result: str | None
    exit_code: int | None
    failure_category: str | None
    failure_class: str | None

@dataclass(slots=True)
class PackageRunResult:
    ok: bool
    source_path: str
    source_kind: str
    extracted_path: str | None
    bundle_root: str
    launcher_path: str
    launcher_command: list[str]
    launcher_working_directory: str
    exit_code: int
    stdout: str
    stderr: str
    inner_report_path: str | None
    inner_result: str | None
    inner_exit_code: int | None
    inner_failure_category: str | None
    outer_report_path: str
    failure_category: str
    notes: list[str]

def _utc_stamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

def _desktop_dir(explicit: Path | None = None) -> Path:
    if explicit is not None:
        explicit.mkdir(parents=True, exist_ok=True)
        return explicit
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        path = Path(user_profile) / "Desktop"
        path.mkdir(parents=True, exist_ok=True)
        return path
    path = Path.home() / "Desktop"
    path.mkdir(parents=True, exist_ok=True)
    return path

def _snapshot_txt_files(directory: Path) -> dict[str, float]:
    if not directory.exists():
        return {}
    snapshot: dict[str, float] = {}
    for path in directory.glob("*.txt"):
        try:
            snapshot[str(path.resolve())] = path.stat().st_mtime
        except OSError:
            continue
    return snapshot

def _new_txt_files(before: dict[str, float], directory: Path, exclude: Iterable[Path] = ()) -> list[Path]:
    excluded = {str(path.resolve()) for path in exclude}
    after = _snapshot_txt_files(directory)
    discovered = [Path(path_text) for path_text in after if path_text not in before and path_text not in excluded]
    discovered.sort(key=lambda item: item.stat().st_mtime if item.exists() else 0.0, reverse=True)
    return discovered

def _safe_extract(zip_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as archive:
        for member in archive.infolist():
            target_path = (destination / member.filename).resolve()
            if not str(target_path).startswith(str(destination.resolve())):
                raise ValueError(f"Unsafe zip member path: {member.filename}")
            archive.extract(member, destination)

def _find_bundle_root(extraction_root: Path) -> Path:
    children = [path for path in extraction_root.iterdir() if path.name not in {"__MACOSX"} and not path.name.startswith(".")]
    top_level_dirs = [path for path in children if path.is_dir()]
    top_level_files = [path for path in children if path.is_file()]
    if len(top_level_dirs) == 1 and not top_level_files:
        return top_level_dirs[0]
    return extraction_root

def _extract_zip_source(source_path: Path, wrapper_root: Path) -> tuple[Path, Path]:
    runtime_root = wrapper_root / "data" / "runtime" / "package_runs"
    runtime_root.mkdir(parents=True, exist_ok=True)
    run_root = runtime_root / f"{source_path.stem}_{_utc_stamp()}"
    extraction_root = run_root / "extracted"
    _safe_extract(source_path, extraction_root)
    bundle_root = _find_bundle_root(extraction_root)
    return extraction_root, bundle_root

def _load_bundle_meta(bundle_root: Path) -> dict[str, Any]:
    candidate = bundle_root / "bundle_meta.json"
    if not candidate.exists():
        return {}
    try:
        return json.loads(candidate.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

def _read_launcher_parameters(launcher_path: Path) -> set[str]:
    try:
        text = launcher_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = launcher_path.read_text(encoding="utf-8-sig")
    header = "\n".join(text.splitlines()[:120])
    return {match.group(1) for match in re.finditer(r"\$(\w+)", header)}

def _candidate_launcher_relpaths(bundle_root: Path, mode: str, bundle_meta: dict[str, Any]) -> list[Path]:
    candidates: list[Path] = []
    preferred_keys = ("verify_launcher_path", "verify_launcher") if mode == "verify" else ("apply_launcher_path", "apply_launcher")
    for key in preferred_keys + ("launcher_path", "launcher"):
        value = bundle_meta.get(key)
        if isinstance(value, str) and value.strip():
            candidates.append(bundle_root / value)
    launchers = bundle_meta.get("launchers")
    if isinstance(launchers, dict):
        value = launchers.get(mode) or launchers.get("default")
        if isinstance(value, str) and value.strip():
            candidates.append(bundle_root / value)
    candidates.extend([
        bundle_root / "launchers" / ("verify_with_patchops.ps1" if mode == "verify" else "apply_with_patchops.ps1"),
        bundle_root / "launchers" / ("run_verify.ps1" if mode == "verify" else "run_apply.ps1"),
        bundle_root / "launchers" / "apply_with_patchops.ps1",
        bundle_root / "launchers" / "verify_with_patchops.ps1",
    ])
    ps1_files = list(bundle_root.rglob("*.ps1"))
    scored: list[tuple[int, Path]] = []
    for item in ps1_files:
        rel = item.relative_to(bundle_root).as_posix().lower()
        score = 0
        if rel.startswith("launchers/"):
            score += 10
        if mode in rel:
            score += 5
        if "patchops" in rel:
            score += 3
        if "apply" in rel and mode == "apply":
            score += 4
        if "verify" in rel and mode == "verify":
            score += 4
        score -= rel.count("/")
        scored.append((score, item))
    scored.sort(key=lambda pair: (-pair[0], pair[1].as_posix()))
    candidates.extend([item for _, item in scored])
    unique: list[Path] = []
    seen: set[str] = set()
    for item in candidates:
        key = str(item.resolve()) if item.exists() else str(item)
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique

def _discover_launcher(bundle_root: Path, *, mode: str, bundle_meta: dict[str, Any], launcher_relative_path: str | None) -> Path:
    if launcher_relative_path:
        candidate = (bundle_root / launcher_relative_path).resolve()
        if candidate.exists():
            return candidate
        raise FileNotFoundError(f"Launcher path not found inside package: {launcher_relative_path}")
    for candidate in _candidate_launcher_relpaths(bundle_root, mode, bundle_meta):
        if candidate.exists():
            return candidate.resolve()
    raise FileNotFoundError(f"No packaged .ps1 launcher found under {bundle_root}")

def _build_launcher_command(*, launcher_path: Path, wrapper_root: Path, bundle_root: Path, source_path: Path, mode: str, profile: str | None, powershell_exe: str | None) -> list[str]:
    powershell = powershell_exe or shutil.which("powershell") or r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
    command = [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(launcher_path)]
    parameter_names = _read_launcher_parameters(launcher_path)
    values = {
        "WrapperRepoRoot": str(wrapper_root),
        "WrapperRoot": str(wrapper_root),
        "PatchOpsRoot": str(wrapper_root),
        "RepoRoot": str(wrapper_root),
        "BundleRoot": str(bundle_root),
        "PackageRoot": str(bundle_root),
        "DeliveryRoot": str(bundle_root),
        "PatchPackageRoot": str(bundle_root),
        "SourceRoot": str(bundle_root),
        "BundlePath": str(source_path),
        "PackagePath": str(source_path),
        "DeliveryPackagePath": str(source_path),
        "SourcePath": str(source_path),
        "Mode": mode,
        "Profile": profile,
        "ProfileName": profile,
    }
    for parameter_name, value in values.items():
        if value is None:
            continue
        if parameter_name in parameter_names:
            command.extend([f"-{parameter_name}", str(value)])
    return command

def _normalize_capture(command: list[str], cwd: Path, raw: Any) -> ProcessCapture:
    if isinstance(raw, ProcessCapture):
        return raw
    if isinstance(raw, subprocess.CompletedProcess):
        return ProcessCapture(command=command, working_directory=str(cwd), exit_code=int(raw.returncode), stdout="" if raw.stdout is None else str(raw.stdout), stderr="" if raw.stderr is None else str(raw.stderr))
    if isinstance(raw, dict):
        return ProcessCapture(command=list(raw.get("command", command)), working_directory=str(raw.get("working_directory", cwd)), exit_code=int(raw.get("exit_code", raw.get("returncode", 1))), stdout="" if raw.get("stdout") is None else str(raw.get("stdout")), stderr="" if raw.get("stderr") is None else str(raw.get("stderr")))
    exit_code = getattr(raw, "exit_code", getattr(raw, "returncode", 1))
    stdout = getattr(raw, "stdout", "")
    stderr = getattr(raw, "stderr", "")
    actual_command = getattr(raw, "command", command)
    actual_cwd = getattr(raw, "working_directory", cwd)
    return ProcessCapture(command=list(actual_command), working_directory=str(actual_cwd), exit_code=int(exit_code), stdout="" if stdout is None else str(stdout), stderr="" if stderr is None else str(stderr))

def _default_runner(command: list[str], cwd: Path) -> ProcessCapture:
    try:
        from patchops.execution.process_runner import run_process as patchops_run_process
    except Exception:
        patchops_run_process = None
    if patchops_run_process is not None:
        try:
            raw = patchops_run_process(program=command[0], args=command[1:], working_directory=cwd)
            return _normalize_capture(command, cwd, raw)
        except TypeError:
            pass
        except Exception:
            pass
    completed = subprocess.run(command, cwd=str(cwd), capture_output=True, text=True, shell=False)
    return _normalize_capture(command, cwd, completed)

def _detect_inner_report_path(*, stdout: str, stderr: str, desktop_dir: Path, desktop_before: dict[str, float], outer_report_path: Path, run_root: Path) -> Path | None:
    combined = "\n".join([stdout or "", stderr or ""])
    explicit_candidates = []
    for match in re.findall(r"[A-Za-z]:\\[^\r\n\"']+?\.txt", combined):
        candidate = Path(match)
        if candidate.exists():
            explicit_candidates.append(candidate.resolve())
    if explicit_candidates:
        explicit_candidates.sort(key=lambda item: item.stat().st_mtime if item.exists() else 0.0, reverse=True)
        for item in explicit_candidates:
            if item != outer_report_path.resolve():
                return item
    new_desktop_files = _new_txt_files(desktop_before, desktop_dir, exclude=[outer_report_path])
    if new_desktop_files:
        return new_desktop_files[0]
    runtime_candidates = sorted([path for path in run_root.rglob("*.txt") if path.resolve() != outer_report_path.resolve()], key=lambda item: item.stat().st_mtime if item.exists() else 0.0, reverse=True)
    if runtime_candidates:
        return runtime_candidates[0]
    return None

def _extract_summary_value(text: str, label: str) -> str | None:
    pattern = re.compile(rf'^\s*{re.escape(label)}\s*:\s*(.+?)\s*$', re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None


def _read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def _extract_summary_int(text: str, label: str) -> int | None:
    value = _extract_summary_value(text, label)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _read_inner_report_summary(inner_report_path: Path | None) -> InnerReportSummary:
    if inner_report_path is None or not inner_report_path.exists():
        return InnerReportSummary(result=None, exit_code=None, failure_category=None, failure_class=None)
    text = _read_text_file(inner_report_path)
    return InnerReportSummary(
        result=_extract_summary_value(text, "Result"),
        exit_code=_extract_summary_int(text, "ExitCode"),
        failure_category=(
            _extract_summary_value(text, "Failure Category")
            or _extract_summary_value(text, "FailureCategory")
            or _extract_summary_value(text, "Category")
        ),
        failure_class=_extract_summary_value(text, "Failure Class"),
    )


def _normalize_inner_failure_category(summary: InnerReportSummary) -> str:
    raw = (summary.failure_category or summary.failure_class or "").strip().lower()
    if not raw:
        return ""
    if "environment" in raw:
        return "environment_failure"
    if "author" in raw or "package_authoring" in raw:
        return "package_authoring_failure"
    if "wrapper" in raw:
        return "wrapper_failure"
    if "target" in raw:
        return "target_content_failure"
    if "ambiguous" in raw:
        return DEFAULT_FAILURE_CATEGORY
    return raw.replace(" ", "_")


def _contains_fatal_launcher_stderr(stderr: str) -> bool:
    text = (stderr or "").lower()
    if not text.strip():
        return False
    fatal_markers = (
        "syntaxerror",
        "modulenotfounderror",
        "importerror",
        "traceback (most recent call last)",
        "parsererror",
    )
    return any(marker in text for marker in fatal_markers)


def _failure_category_for_fatal_launcher_stderr(stderr: str) -> str:
    text = (stderr or "").lower()
    if "syntaxerror" in text or "parsererror" in text:
        return "package_authoring_failure"
    if "modulenotfounderror" in text or "importerror" in text:
        return "wrapper_failure"
    if "traceback (most recent call last)" in text:
        return "wrapper_failure"
    return DEFAULT_FAILURE_CATEGORY

def _resolve_effective_outcome(*, capture: ProcessCapture, inner_summary: InnerReportSummary, notes: list[str]) -> tuple[bool, int, str]:
    capture_ok = capture.exit_code == 0
    effective_ok = capture_ok
    effective_exit_code = capture.exit_code
    failure_category = "" if capture_ok else _classify_failure(setup_error=None, capture=capture)

    if (inner_summary.result or "").strip().upper() == "FAIL":
        effective_ok = False
        if capture_ok:
            notes.append("Inner report summary reported FAIL even though launcher exit code was 0.")
            effective_exit_code = inner_summary.exit_code if inner_summary.exit_code not in (None, 0) else 1
            failure_category = _normalize_inner_failure_category(inner_summary) or "target_content_failure"
        elif not failure_category:
            failure_category = _normalize_inner_failure_category(inner_summary) or DEFAULT_FAILURE_CATEGORY

    if inner_summary.result is None and _contains_fatal_launcher_stderr(capture.stderr):
        effective_ok = False
        effective_exit_code = capture.exit_code if capture.exit_code not in (None, 0) else 1
        failure_category = _failure_category_for_fatal_launcher_stderr(capture.stderr)
        notes.append(
            "Fatal launcher stderr was detected without a real inner report; treating run-package outcome as FAIL."
        )

    return effective_ok, effective_exit_code, failure_category




def _should_run_bundle_preflight(bundle_root: Path) -> bool:
    manifest_path = bundle_root / "manifest.json"
    content_root = bundle_root / "content"
    bundle_meta_path = bundle_root / "bundle_meta.json"
    if not manifest_path.exists() or not content_root.exists():
        return False

    try:
        manifest_preview = json.loads(_read_text_file(manifest_path))
    except Exception:
        manifest_preview = {}
    if isinstance(manifest_preview, dict) and manifest_preview.get("files_to_write"):
        return True

    if bundle_meta_path.exists():
        try:
            bundle_meta_preview = json.loads(_read_text_file(bundle_meta_path))
        except Exception:
            bundle_meta_preview = {}
        if isinstance(bundle_meta_preview, dict) and {
            "bundle_schema_version",
            "patch_name",
            "target_project",
            "recommended_profile",
            "target_project_root",
            "wrapper_project_root",
        }.issubset(bundle_meta_preview.keys()):
            return True

    return False


def _preflight_bundle_root(bundle_root: Path) -> None:
    from patchops.bundles.validator import validate_extracted_bundle_dir

    validation = validate_extracted_bundle_dir(bundle_root)
    if validation.is_valid:
        return

    rendered_errors: list[str] = []
    for item in validation.errors:
        detail = f"[{item.code}] {item.message}"
        if item.path:
            detail += f" ({item.path})"
        rendered_errors.append(detail)

    raise ValueError(
        "Bundle preflight failed before launcher execution:\n" + "\n".join(rendered_errors)
    )

def _classify_setup_failure_message(message: str) -> str:
    text = (message or "").lower()
    if not text.strip():
        return DEFAULT_FAILURE_CATEGORY

    environment_markers = (
        "powershell was not found",
        "powershell is not recognized",
        "python was not found",
        "the system cannot find the path specified",
        "the system cannot find the file specified",
        "win32exception",
    )
    if any(marker in text for marker in environment_markers):
        return "environment_failure"

    if "no such file or directory" in text and any(
        marker in text for marker in ("python", "powershell", "pwsh", ".exe")
    ):
        return "environment_failure"

    if "modulenotfounderror" in text or "importerror" in text:
        return "wrapper_failure"

    if "bundle preflight failed before launcher execution" in text:
        if any(
            marker in text
            for marker in (
                "generated_python_syntax_invalid",
                "bundle_meta_invalid",
                "missing_staged_file",
                "missing_content_directory",
                "missing_content_path",
                "content_path_missing",
                "launcher_is_missing_the_standard_py",
                "prep_helper",
            )
        ):
            return "package_authoring_failure"

    if any(
        marker in text
        for marker in (
            "syntaxerror",
            "parsererror",
            "invalid json primitive",
            "cannot bind argument",
            "cannot call a method on a null-valued expression",
            "add-sectionheader",
        )
    ):
        return "package_authoring_failure"

    return "package_authoring_failure"


def _classify_failure(*, setup_error: Exception | None, capture: ProcessCapture | None) -> str:
    if setup_error is not None:
        message = f"{type(setup_error).__name__}: {setup_error}"
        return _classify_setup_failure_message(message)
    if capture is None:
        return DEFAULT_FAILURE_CATEGORY
    combined = "\n".join([capture.stdout, capture.stderr]).lower()
    if any(marker in combined for marker in ("powershell is not recognized", "python was not found", "no such file or directory", "the system cannot find the path specified")):
        return "environment_failure"
    if any(marker in combined for marker in ("modulenotfounderror", "importerror")):
        return "wrapper_failure"
    if any(marker in combined for marker in ("syntaxerror", "parsererror", "this runner must be executed from the saved .ps1 file", "invalid json primitive", "cannot bind argument", "cannot call a method on a null-valued expression", "add-sectionheader")):
        return "package_authoring_failure"
    if capture.exit_code != 0 and any(marker in combined for marker in ("failed", "assertionerror", "traceback", "collected", "pytest", "error:", "failures")):
        return "target_content_failure"
    if capture.exit_code != 0:
        return "wrapper_failure"
    return ""

def _quote_command(parts: Sequence[str]) -> str:
    rendered: list[str] = []
    for item in parts:
        if re.search(r'[\s"]', item):
            rendered.append(f'"{item.replace(chr(34), chr(92) + chr(34))}"')
        else:
            rendered.append(item)
    return " ".join(rendered)

def _render_report(result: PackageRunResult) -> str:
    lines = ["PATCHOPS RUN-PACKAGE OUTER REPORT", "================================", f"Result              : {'PASS' if result.ok else 'FAIL'}", f"Failure Category    : {result.failure_category or '(none)'}", f"Source Path         : {result.source_path}", f"Source Kind         : {result.source_kind}", f"Extracted Path      : {result.extracted_path or '(not applicable)'}", f"Bundle Root         : {result.bundle_root}", f"Launcher Path       : {result.launcher_path}", f"Launcher Cwd        : {result.launcher_working_directory}", f"Inner Report Path   : {result.inner_report_path or '(not detected)'}", f"Inner Result        : {result.inner_result or '(not detected)'}", f"Inner Exit Code     : {result.inner_exit_code if result.inner_exit_code is not None else '(not detected)'}", f"Inner Failure       : {result.inner_failure_category or '(none)'}", f"Outer Report Path   : {result.outer_report_path}", f"Exit Code           : {result.exit_code}", "", "COMMAND", "-------", _quote_command(result.launcher_command), "", "STDOUT", "------", result.stdout or "(empty)", "", "STDERR", "------", result.stderr or "(empty)", "", "NOTES", "-----"]
    if result.notes:
        lines.extend(f"- {note}" for note in result.notes)
    else:
        lines.append("- none")
    lines.extend(["", "SUMMARY", "-------", f"Ok                 : {result.ok}", f"FailureCategory    : {result.failure_category or '(none)'}", f"InnerReportFound   : {bool(result.inner_report_path)}"])
    return "\n".join(lines) + "\n"



def _render_canonical_combined_report(*, result: PackageRunResult, inner_report_text: str, canonical_report_path: Path, requested_outer_report_path: Path) -> str:
    lines = [
        "PATCHOPS RUN-PACKAGE CANONICAL REPORT",
        "====================================",
        f"Result               : {'PASS' if result.ok else 'FAIL'}",
        f"Failure Category     : {result.failure_category or '(none)'}",
        f"Canonical Report Path: {canonical_report_path}",
        f"Requested Outer Path : {requested_outer_report_path}",
        f"Source Path          : {result.source_path}",
        f"Source Kind          : {result.source_kind}",
        f"Extracted Path       : {result.extracted_path or '(not applicable)'}",
        f"Bundle Root          : {result.bundle_root}",
        f"Launcher Path        : {result.launcher_path}",
        f"Launcher Cwd         : {result.launcher_working_directory}",
        f"Inner Report Path    : {result.inner_report_path or '(not detected)'}",
        f"Inner Result         : {result.inner_result or '(not detected)'}",
        f"Inner Exit Code      : {result.inner_exit_code if result.inner_exit_code is not None else '(not detected)'}",
        f"Inner Failure        : {result.inner_failure_category or '(none)'}",
        f"Outer Report Path    : {result.outer_report_path}",
        f"Exit Code            : {result.exit_code}",
        "",
        "COMMAND",
        "-------",
        _quote_command(result.launcher_command),
        "",
        "LAUNCHER STDOUT",
        "-------------",
        result.stdout or "(empty)",
        "",
        "LAUNCHER STDERR",
        "-------------",
        result.stderr or "(empty)",
        "",
        "NOTES",
        "-----",
    ]
    if result.notes:
        lines.extend(f"- {note}" for note in result.notes)
    else:
        lines.append("- none")
    lines.extend([
        "",
        "INNER REPORT",
        "------------",
        inner_report_text.rstrip(),
        "",
    ])
    return "\n".join(lines) + "\n"


def _write_single_canonical_report(result: PackageRunResult, *, requested_outer_report_path: Path) -> Path:
    canonical_inner = Path(result.inner_report_path).resolve() if result.inner_report_path else None
    outer_path = requested_outer_report_path.resolve()
    if canonical_inner is not None and canonical_inner.exists():
        result.notes.append("Canonical run-package context merged into inner report; no separate outer report artifact was kept.")
        result.outer_report_path = str(canonical_inner)
        inner_text = _read_text_file(canonical_inner)
        canonical_text = _render_canonical_combined_report(
            result=result,
            inner_report_text=inner_text,
            canonical_report_path=canonical_inner,
            requested_outer_report_path=outer_path,
        )
        canonical_inner.write_text(canonical_text, encoding="utf-8")
        if outer_path.exists() and outer_path != canonical_inner:
            outer_path.unlink()
        return canonical_inner
    result.outer_report_path = str(outer_path)
    outer_path.write_text(_render_report(result), encoding="utf-8")
    return outer_path

def run_delivery_package(source_path: Path, *, wrapper_root: Path, mode: str = "apply", profile: str | None = None, launcher_relative_path: str | None = None, report_path: Path | None = None, powershell_exe: str | None = None, desktop_dir: Path | None = None, runner: Callable[[list[str], Path], Any] | None = None) -> PackageRunResult:
    source_path = source_path.resolve()
    wrapper_root = wrapper_root.resolve()
    desktop = _desktop_dir(desktop_dir)
    report_path = (report_path or (desktop / f"patchops_run_package_{_utc_stamp()}.txt")).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    notes: list[str] = []
    extraction_root: Path | None = None
    bundle_root: Path | None = None
    launcher_path: Path | None = None
    desktop_before = _snapshot_txt_files(desktop)
    run_root = wrapper_root / "data" / "runtime" / "package_runs" / f"run_package_{_utc_stamp()}"
    run_root.mkdir(parents=True, exist_ok=True)
    try:
        if not source_path.exists():
            raise FileNotFoundError(f"Package source does not exist: {source_path}")
        if source_path.is_file():
            if source_path.suffix.lower() != ".zip":
                raise ValueError(f"Unsupported package file type: {source_path.suffix}")
            source_kind = "zip"
            extraction_root, bundle_root = _extract_zip_source(source_path, wrapper_root)
            notes.append("Zip source extracted by PatchOps.")
        elif source_path.is_dir():
            source_kind = "folder"
            bundle_root = source_path
            notes.append("Folder source used directly without extraction.")
        else:
            raise ValueError(f"Unsupported package source: {source_path}")
        bundle_meta = _load_bundle_meta(bundle_root)
        if bundle_meta:
            notes.append("bundle_meta.json detected and consulted during launcher discovery.")
        if _should_run_bundle_preflight(bundle_root):
            _preflight_bundle_root(bundle_root)
            notes.append("Bundle preflight passed before launcher invocation.")
        else:
            notes.append("Bundle preflight skipped because the bundle does not advertise the canonical staged-authoring contract.")
        launcher_path = _discover_launcher(bundle_root, mode=mode, bundle_meta=bundle_meta, launcher_relative_path=launcher_relative_path)
        command = _build_launcher_command(launcher_path=launcher_path, wrapper_root=wrapper_root, bundle_root=bundle_root, source_path=source_path, mode=mode, profile=profile, powershell_exe=powershell_exe)
        active_runner = runner or _default_runner
        capture = _normalize_capture(command, bundle_root, active_runner(command, bundle_root))
        inner_report = _detect_inner_report_path(stdout=capture.stdout, stderr=capture.stderr, desktop_dir=desktop, desktop_before=desktop_before, outer_report_path=report_path, run_root=run_root)
        inner_summary = _read_inner_report_summary(inner_report)
        ok, effective_exit_code, failure_category = _resolve_effective_outcome(capture=capture, inner_summary=inner_summary, notes=notes)
        result = PackageRunResult(ok=ok, source_path=str(source_path), source_kind=source_kind, extracted_path=None if extraction_root is None else str(extraction_root), bundle_root=str(bundle_root), launcher_path=str(launcher_path), launcher_command=capture.command, launcher_working_directory=str(bundle_root), exit_code=effective_exit_code, stdout=capture.stdout, stderr=capture.stderr, inner_report_path=None if inner_report is None else str(inner_report), inner_result=inner_summary.result, inner_exit_code=inner_summary.exit_code, inner_failure_category=_normalize_inner_failure_category(inner_summary), outer_report_path=str(report_path), failure_category=failure_category, notes=notes)
    except Exception as exc:
        failure_category = _classify_failure(setup_error=exc, capture=None)
        if bundle_root is None:
            bundle_root = source_path.parent if source_path.exists() else wrapper_root
        result = PackageRunResult(ok=False, source_path=str(source_path), source_kind="zip" if source_path.suffix.lower() == ".zip" else "folder", extracted_path=None if extraction_root is None else str(extraction_root), bundle_root=str(bundle_root), launcher_path=str(launcher_path or "(not discovered)"), launcher_command=["(package setup failed before launcher invocation)"], launcher_working_directory=str(bundle_root), exit_code=1, stdout="", stderr=f"{type(exc).__name__}: {exc}", inner_report_path=None, inner_result=None, inner_exit_code=None, inner_failure_category=None, outer_report_path=str(report_path), failure_category=failure_category, notes=notes + ["Launcher invocation did not start."])
    _write_single_canonical_report(result, requested_outer_report_path=report_path)
    return result


def _validate_cli_path_text(label, value):
    import re
    from pathlib import Path

    text = (value or "").strip()
    if not text:
        raise ValueError(f"{label} is required.")
    if re.match(r"^:[\/]", text):
        raise ValueError(
            f"{label} looks like a Windows path but is missing its drive letter: {text!r}. "
            'Use a full path like "C:\\dev\\patchops".'
        )
    return Path(text)


def cli_main(argv=None):
    import argparse
    import json
    from dataclasses import asdict

    parser = argparse.ArgumentParser(
        prog="patchops run-package",
        description="Run a ChatGPT delivery package zip or extracted delivery folder through PatchOps.",
    )
    parser.add_argument("source_path", help="Path to a delivery zip or extracted delivery folder.")
    parser.add_argument("--wrapper-root", required=True, help="PatchOps wrapper repo root.")
    parser.add_argument("--mode", choices=["apply", "verify"], default="apply")
    parser.add_argument("--profile", default=None)
    parser.add_argument("--launcher-relative-path", default=None)
    parser.add_argument("--report-path", default=None)
    parser.add_argument("--powershell-exe", default=None)
    parser.add_argument("--desktop-dir", default=None, help=argparse.SUPPRESS)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        source_path = _validate_cli_path_text("source_path", args.source_path)
        wrapper_root = _validate_cli_path_text("wrapper_root", args.wrapper_root)
        report_path = _validate_cli_path_text("report_path", args.report_path) if args.report_path else None
        desktop_dir = _validate_cli_path_text("desktop_dir", args.desktop_dir) if args.desktop_dir else None
    except ValueError as exc:
        parser.exit(2, f"patchops run-package: error: {exc}\n")

    result = run_delivery_package(
        source_path,
        wrapper_root=wrapper_root,
        mode=args.mode,
        profile=args.profile,
        launcher_relative_path=args.launcher_relative_path,
        report_path=report_path,
        powershell_exe=args.powershell_exe,
        desktop_dir=desktop_dir,
    )
    print(json.dumps(asdict(result), indent=2))
    return int(result.exit_code if result.exit_code else 0)
