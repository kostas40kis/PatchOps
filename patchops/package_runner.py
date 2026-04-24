

from __future__ import annotations
def _normalize_run_package_report_artifact(
    report_path: object,
    run_result: object,
    source_path: object | None,
    requested_report_path: object | None,
) -> None:
    if not report_path:
        return

    try:
        actual_written_path = Path(str(report_path)).resolve()
    except Exception:
        return

    if not actual_written_path.exists():
        return

    raw_text = actual_written_path.read_text(encoding="utf-8")
    normalized = raw_text.replace("\r\n", "\n")

    inner_report_path = getattr(run_result, "inner_report_path", None)

    requested_path_obj = None
    inner_path_obj = None
    try:
        if requested_report_path:
            requested_path_obj = Path(str(requested_report_path)).resolve()
    except Exception:
        requested_path_obj = None

    try:
        if inner_report_path:
            inner_path_obj = Path(str(inner_report_path)).resolve()
    except Exception:
        inner_path_obj = None

    merged_single_artifact = (
        requested_path_obj is not None
        and inner_path_obj is not None
        and actual_written_path == inner_path_obj
    )

    desired_title = (
        "PATCHOPS RUN-PACKAGE CANONICAL REPORT"
        if merged_single_artifact
        else "PATCHOPS RUN-PACKAGE OUTER REPORT"
    )
    desired_result_prefix = (
        "Result               :"
        if merged_single_artifact
        else "Result              :"
    )
    desired_result_value = "PASS" if getattr(run_result, "ok", False) else "FAIL"

    rows = normalized.split("\n")
    if not rows:
        rows = [desired_title]
    elif rows[0].startswith("PATCHOPS RUN-PACKAGE "):
        rows[0] = desired_title
    else:
        rows.insert(0, desired_title)

    def replace_first(prefix_start: str, new_line: str) -> None:
        for idx, row in enumerate(rows):
            if row.startswith(prefix_start):
                rows[idx] = new_line
                return

    def insert_after(prefix_start: str, new_line: str) -> None:
        if new_line in rows:
            return
        for idx, row in enumerate(rows):
            if row.startswith(prefix_start):
                rows.insert(idx + 1, new_line)
                return

    replace_first("Result", f"{desired_result_prefix} {desired_result_value}")

    source_path_text = "(unknown)"
    if source_path is not None:
        try:
            source_path_text = str(Path(str(source_path)).resolve())
        except Exception:
            source_path_text = str(source_path)

    inner_report_text = "(not detected)"
    if inner_report_path:
        try:
            inner_report_text = str(Path(str(inner_report_path)).resolve())
        except Exception:
            inner_report_text = str(inner_report_path)

    launcher_path_value = getattr(run_result, "launcher_path", None)
    launcher_path_text = "(unknown)"
    if launcher_path_value:
        try:
            launcher_path_text = str(Path(str(launcher_path_value)).resolve())
        except Exception:
            launcher_path_text = str(launcher_path_value)

    inner_report_found = "True" if inner_report_path else "False"

    insert_after("Failure Category", f"Source Path         : {source_path_text}")
    insert_after("Source Path         :", f"Source Kind         : {getattr(run_result, 'source_kind', None) or '(unknown)'}")
    insert_after("Source Kind         :", f"Extracted Path      : {getattr(run_result, 'extracted_path', None) or '(not applicable)'}")
    insert_after("Extracted Path      :", f"Bundle Root         : {getattr(run_result, 'bundle_root', None) or '(unknown)'}")
    insert_after("Bundle Root         :", f"Launcher Path       : {launcher_path_text}")

    insert_after("Launcher Cwd", f"Inner Report Path   : {inner_report_text}")
    insert_after("Inner Report Path   :", f"InnerReportFound   : {inner_report_found}")
    insert_after("InnerReportFound   :", f"Inner Result        : {getattr(run_result, 'inner_result', None) or '(not detected)'}")
    insert_after("Inner Result        :", f"Inner Exit Code     : {getattr(run_result, 'inner_exit_code', None) if getattr(run_result, 'inner_exit_code', None) is not None else '(not detected)'}")
    insert_after("Inner Exit Code     :", f"Inner Failure       : {getattr(run_result, 'inner_failure_category', None) or '(none)'}")
    insert_after("Inner Failure       :", f"Outer Report Path   : {getattr(run_result, 'outer_report_path', None) or '(unknown)'}")
    insert_after("Outer Report Path   :", f"Exit Code           : {getattr(run_result, 'exit_code', None) if getattr(run_result, 'exit_code', None) is not None else '(unknown)'}")

    new_text = "\n".join(rows)
    if new_text != raw_text.replace("\r\n", "\n"):
        actual_written_path.write_text(new_text, encoding="utf-8", newline="")


import argparse
import json
import os
import re
import shutil
import subprocess
import traceback
import zipfile
from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence
import sys
import pathlib


def _looks_like_windows_missing_drive_path(value: str | None) -> bool:
    if value is None:
        return False
    raw = str(value).strip()
    return raw.startswith(":\\") or raw.startswith(":/")

def _extract_option_value_from_argv(argv: list[str], option_name: str) -> str | None:
    for index, token in enumerate(argv):
        if token == option_name:
            if index + 1 < len(argv):
                return argv[index + 1]
            return None
        prefix = option_name + "="
        if isinstance(token, str) and token.startswith(prefix):
            return token[len(prefix):]
    return None

DEFAULT_FAILURE_CATEGORY = "ambiguous_evidence"

# PATCHOPS_PATCH_219_RUN_PACKAGE_RESULT_SERIALIZER_GUARD
def _json_safe_scalar_or_container(value: object) -> object:
    if is_dataclass(value) and not isinstance(value, type):
        return _json_safe_scalar_or_container(asdict(value))

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, dict):
        safe_dict: dict[object, object] = {}
        for key, item in value.items():
            safe_key = _json_safe_scalar_or_container(key)
            if not isinstance(safe_key, (str, int, float, bool)) and safe_key is not None:
                safe_key = str(safe_key)
            safe_dict[safe_key] = _json_safe_scalar_or_container(item)
        return safe_dict

    if isinstance(value, (list, tuple, set)):
        return [_json_safe_scalar_or_container(item) for item in value]

    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    if hasattr(value, "to_dict") and callable(value.to_dict):
        try:
            return _json_safe_scalar_or_container(value.to_dict())
        except Exception as exc:
            return {
                "result_type": type(value).__name__,
                "result_repr": repr(value),
                "to_dict_error": str(exc),
            }

    return {
        "result_type": type(value).__name__,
        "result_repr": repr(value),
    }


def _json_safe_result(value, *, _top_level: bool = True):
    from dataclasses import asdict, is_dataclass
    from enum import Enum
    from pathlib import Path as _Path

    def nested(item):
        return _json_safe_result(item, _top_level=False)

    if isinstance(value, Enum):
        resolved = value.value
        return {"result": resolved} if _top_level else resolved

    if is_dataclass(value) and not isinstance(value, type):
        return nested(asdict(value))

    if isinstance(value, _Path):
        resolved = str(value)
        return {"result": resolved} if _top_level else resolved

    if value is None or isinstance(value, (str, int, float, bool)):
        return {"result": value} if _top_level else value

    if isinstance(value, dict):
        return {str(nested(key)): nested(item) for key, item in value.items()}

    if isinstance(value, (list, tuple, set, frozenset)):
        return [nested(item) for item in value]

    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        try:
            return nested(to_dict())
        except Exception:
            pass

    asdict_method = getattr(value, "_asdict", None)
    if callable(asdict_method):
        try:
            return nested(asdict_method())
        except Exception:
            pass

    value_dict = getattr(value, "__dict__", None)
    if isinstance(value_dict, dict) and value_dict:
        return nested(value_dict)

    slots = getattr(value, "__slots__", None)
    if slots:
        names = [slots] if isinstance(slots, str) else list(slots)
        payload = {}
        for name in names:
            if isinstance(name, str) and not name.startswith("_") and hasattr(value, name):
                payload[name] = nested(getattr(value, name))
        if payload:
            return payload

    return {
        "result_type": type(value).__name__,
        "repr": repr(value),
        "result_repr": repr(value),
    }
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
        "PATCHOPS RUN-PACKAGE OUTER REPORT",
        "====================================",
        f"Result              : {'PASS' if result.ok else 'FAIL'}",
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
    requested_report_path_input = report_path
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
    _normalize_run_package_report_artifact(
        getattr(result, 'outer_report_path', None),
        result,
        locals().get('source_path'),
    requested_report_path_input,
    )
    _normalize_run_package_report_artifact(
        getattr(result, 'outer_report_path', None),
        result,
        locals().get('source_path'),
    requested_report_path_input,
    )
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


# PATCHOPS_PATCH_220_RUN_PACKAGE_RESULT_CONTRACT_GUARD
def _patchops_p220_first_text(*values: object, default: str = "") -> str:
    for value in values:
        if value is None:
            continue
        text = str(value)
        if text:
            return text
    return default


def _patchops_p220_optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None


def _patchops_p220_int(value: object, *, default: int = 1) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def _patchops_p220_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, tuple):
        return [str(item) for item in value]
    return [str(value)]


def _patchops_p220_payload_field(payload: object, key: str, default: object = None) -> object:
    if isinstance(payload, dict):
        return payload.get(key, default)
    return default


def _patchops_p220_default_report_path(report_path: Path | None, desktop_dir: Path | None) -> Path:
    if report_path is not None:
        return Path(report_path).resolve()
    desktop = _desktop_dir(desktop_dir)
    return (desktop / f"patchops_run_package_{_utc_stamp()}.txt").resolve()


# PATCHOPS_PATCH_223B_COERCED_REPORT_GUARANTEE
def _patchops_p223b_report_text(value: object, *, default: str = "(not detected)") -> str:
    if value is None:
        return default
    text = str(value)
    return text if text else default


def _patchops_p223b_write_minimal_canonical_report(
    result: "PackageRunResult",
    *,
    outer_path: Path,
    reason: str,
) -> None:
    lines = [
        "PATCHOPS RUN-PACKAGE OUTER REPORT",
        "================================",
        f"Result              : {'PASS' if result.ok else 'FAIL'}",
        f"Failure Category    : {_patchops_p223b_report_text(result.failure_category, default='none')}",
        f"Source Path         : {_patchops_p223b_report_text(result.source_path)}",
        f"Source Kind         : {_patchops_p223b_report_text(result.source_kind)}",
        f"Extracted Path      : {_patchops_p223b_report_text(result.extracted_path, default='(not applicable)')}",
        f"Bundle Root         : {_patchops_p223b_report_text(result.bundle_root)}",
        f"Launcher Path       : {_patchops_p223b_report_text(result.launcher_path)}",
        f"Launcher Cwd        : {_patchops_p223b_report_text(result.launcher_working_directory)}",
        f"Inner Report Path   : {_patchops_p223b_report_text(result.inner_report_path)}",
        f"Inner Result        : {_patchops_p223b_report_text(result.inner_result)}",
        f"Inner Exit Code     : {_patchops_p223b_report_text(result.inner_exit_code)}",
        f"Inner Failure       : {_patchops_p223b_report_text(result.inner_failure_category, default='(none)')}",
        f"Outer Report Path   : {outer_path}",
        f"Exit Code           : {result.exit_code}",
        "",
        "COMMAND",
        "-------",
    ]
    lines.extend(result.launcher_command or ["(not detected)"])
    lines.extend(
        [
            "",
            "STDOUT",
            "------",
            result.stdout if result.stdout else "(empty)",
            "",
            "STDERR",
            "------",
            result.stderr if result.stderr else "(empty)",
            "",
            "NOTES",
            "-----",
            f"- Minimal fallback report writer used because: {reason}",
        ]
    )
    for note in result.notes:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "SUMMARY",
            "-------",
            f"Ok                 : {result.ok}",
            f"FailureCategory    : {_patchops_p223b_report_text(result.failure_category, default='none')}",
            f"InnerReportFound   : {bool(result.inner_report_path)}",
        ]
    )
    outer_path.parent.mkdir(parents=True, exist_ok=True)
    outer_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _patchops_p223b_ensure_canonical_report(result: "PackageRunResult") -> None:
    outer_path = Path(result.outer_report_path)
    if outer_path.exists():
        return

    try:
        _write_single_canonical_report(result, requested_outer_report_path=outer_path)
    except Exception as exc:
        result.notes.append(f"Could not write standard coerced-result report: {exc}")
        _patchops_p223b_write_minimal_canonical_report(
            result,
            outer_path=outer_path,
            reason=f"standard renderer raised {type(exc).__name__}: {exc}",
        )
        return

    if not outer_path.exists():
        _patchops_p223b_write_minimal_canonical_report(
            result,
            outer_path=outer_path,
            reason="standard renderer returned without creating the report file",
        )


def _patchops_p223_has_contract_payload(payload: object) -> bool:
    if not isinstance(payload, dict):
        return False
    contract_keys = {
        "ok",
        "exit_code",
        "source_path",
        "source_kind",
        "outer_report_path",
        "inner_report_path",
        "launcher_command",
        "launcher_path",
        "failure_category",
    }
    return any(key in payload for key in contract_keys)


def _coerce_package_run_result(
    value: object,
    *,
    source_path: Path,
    wrapper_root: Path,
    report_path: Path | None,
    desktop_dir: Path | None,
) -> PackageRunResult:
    # Return the stable run-package result dataclass for every CLI result path.
    if isinstance(value, PackageRunResult):
        return value

    payload = _json_safe_result(value)
    if not isinstance(payload, dict):
        payload = {"result": payload}

    original_type = type(value).__name__
    requested_report_path = _patchops_p220_default_report_path(report_path, desktop_dir)

    raw_exit = _patchops_p220_payload_field(
        payload,
        "exit_code",
        _patchops_p220_payload_field(payload, "result", 1),
    )
    exit_code = _patchops_p220_int(raw_exit, default=1)

    raw_ok = _patchops_p220_payload_field(payload, "ok", None)
    ok = bool(raw_ok) if raw_ok is not None else False

    # Shape drift is a wrapper contract failure.  Do not turn a raw scalar 0,
    # None, or ambiguous fallback object into a successful run-package result.
    # Attribute-style objects with recognizable result fields are accepted and
    # coerced below; arbitrary non-contract objects still fail closed.
    structured_payload = isinstance(value, dict) or _patchops_p223_has_contract_payload(payload)
    if not structured_payload:
        ok = False
        if exit_code == 0:
            exit_code = 1

    if ok and exit_code != 0:
        ok = False
    if not ok and exit_code == 0:
        exit_code = 1

    source_kind = _patchops_p220_first_text(
        _patchops_p220_payload_field(payload, "source_kind", None),
        "zip" if str(source_path).lower().endswith(".zip") else "folder",
    )
    outer_report_path = _patchops_p220_first_text(
        _patchops_p220_payload_field(payload, "outer_report_path", None),
        _patchops_p220_payload_field(payload, "report_path", None),
        requested_report_path,
    )

    notes = _patchops_p220_list(_patchops_p220_payload_field(payload, "notes", None))
    notes.insert(0, f"Normalized non-PackageRunResult run-package result type: {original_type}.")
    if structured_payload:
        notes.insert(1, "run-package cli_main coerced an attribute-style result into the stable PackageRunResult contract.")
    else:
        notes.insert(1, "run-package cli_main failed closed to preserve the stable result contract.")

    stderr = _patchops_p220_first_text(
        _patchops_p220_payload_field(payload, "stderr", None),
        f"Non-PackageRunResult returned by run_delivery_package: {original_type}",
    )

    result = PackageRunResult(
        ok=ok,
        source_path=_patchops_p220_first_text(_patchops_p220_payload_field(payload, "source_path", None), source_path),
        source_kind=source_kind,
        extracted_path=_patchops_p220_optional_text(_patchops_p220_payload_field(payload, "extracted_path", None)),
        bundle_root=_patchops_p220_first_text(_patchops_p220_payload_field(payload, "bundle_root", None), wrapper_root),
        launcher_path=_patchops_p220_first_text(_patchops_p220_payload_field(payload, "launcher_path", None), "(not discovered)"),
        launcher_command=_patchops_p220_list(
            _patchops_p220_payload_field(payload, "launcher_command", ["(non-PackageRunResult normalized before launcher evidence was available)"])
        ),
        launcher_working_directory=_patchops_p220_first_text(
            _patchops_p220_payload_field(payload, "launcher_working_directory", None),
            _patchops_p220_payload_field(payload, "cwd", None),
            wrapper_root,
        ),
        exit_code=exit_code,
        stdout=_patchops_p220_first_text(_patchops_p220_payload_field(payload, "stdout", None), default=""),
        stderr=stderr,
        inner_report_path=_patchops_p220_optional_text(_patchops_p220_payload_field(payload, "inner_report_path", None)),
        inner_result=_patchops_p220_optional_text(_patchops_p220_payload_field(payload, "inner_result", None)),
        inner_exit_code=(
            None
            if _patchops_p220_payload_field(payload, "inner_exit_code", None) is None
            else _patchops_p220_int(_patchops_p220_payload_field(payload, "inner_exit_code", None), default=1)
        ),
        inner_failure_category=_patchops_p220_optional_text(_patchops_p220_payload_field(payload, "inner_failure_category", None)),
        outer_report_path=str(Path(str(outer_report_path)).resolve()),
        failure_category=_patchops_p220_first_text(
            _patchops_p220_payload_field(payload, "failure_category", None),
            _patchops_p220_payload_field(payload, "classification", None),
            "none" if ok else "wrapper_failure",
        ),
        notes=notes,
    )

    _patchops_p223b_ensure_canonical_report(result)

    return result



# PATCHOPS_PATCH_221B_RUN_PACKAGE_EXCEPTION_REPORT_GUARD
def _package_run_exception_result(
    exc: BaseException,
    *,
    source_path: Path,
    wrapper_root: Path,
    report_path: Path | None,
    desktop_dir: Path | None,
) -> PackageRunResult:
    requested_report_path = _patchops_p220_default_report_path(report_path, desktop_dir)
    exception_text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)).strip()
    if not exception_text:
        exception_text = f"{type(exc).__name__}: {exc}"

    result = PackageRunResult(
        ok=False,
        source_path=str(Path(source_path)),
        source_kind="zip" if str(source_path).lower().endswith(".zip") else "folder",
        extracted_path=None,
        bundle_root=str(Path(wrapper_root)),
        launcher_path="(not discovered)",
        launcher_command=["(run_delivery_package raised before launcher evidence was available)"],
        launcher_working_directory=str(Path(wrapper_root)),
        exit_code=1,
        stdout="",
        stderr=exception_text,
        inner_report_path=None,
        inner_result=None,
        inner_exit_code=None,
        inner_failure_category=None,
        outer_report_path=str(Path(requested_report_path).resolve()),
        failure_category="wrapper_failure",
        notes=[
            "run_delivery_package raised an unexpected wrapper exception before a stable result was returned.",
            "Patch 221B normalized the exception into a fail-closed PackageRunResult instead of allowing a raw traceback escape.",
        ],
    )

    try:
        _write_single_canonical_report(result, requested_outer_report_path=Path(result.outer_report_path))
    except Exception as report_exc:
        result.notes.append(f"Could not write fallback exception report: {report_exc}")

    return result

def _run_package_result_to_jsonable(value):
    # Return a JSON-safe representation for run-package CLI output.
    #
    # The normal result is PackageRunResult, but CLI JSON output must not crash
    # if a wrapper repair, monkeypatch, or future adapter returns a dict,
    # primitive, None, SimpleNamespace-style object, slotted object, or fallback
    # shape.

    from dataclasses import asdict, is_dataclass
    from pathlib import Path as _Path

    if is_dataclass(value) and not isinstance(value, type):
        return _run_package_result_to_jsonable(asdict(value))

    if isinstance(value, _Path):
        return str(value)

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, dict):
        return {
            str(_run_package_result_to_jsonable(key)): _run_package_result_to_jsonable(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set, frozenset)):
        return [_run_package_result_to_jsonable(item) for item in value]

    asdict_method = getattr(value, "_asdict", None)
    if callable(asdict_method):
        try:
            return _run_package_result_to_jsonable(asdict_method())
        except Exception:
            pass

    value_dict = getattr(value, "__dict__", None)
    if isinstance(value_dict, dict):
        return _run_package_result_to_jsonable(value_dict)

    slots = getattr(value, "__slots__", None)
    if slots:
        if isinstance(slots, str):
            slot_names = [slots]
        else:
            slot_names = list(slots)
        payload = {}
        for slot_name in slot_names:
            if not isinstance(slot_name, str) or slot_name.startswith("_"):
                continue
            if hasattr(value, slot_name):
                payload[slot_name] = _run_package_result_to_jsonable(getattr(value, slot_name))
        if payload:
            return payload

    return repr(value)


# PATCHOPS_225_RUN_PACKAGE_STABLE_RESULT_CONTRACT
def _json_safe_result(value):
    from dataclasses import asdict, is_dataclass
    from pathlib import Path as _Path

    if is_dataclass(value) and not isinstance(value, type):
        return _json_safe_result(asdict(value))
    if isinstance(value, _Path):
        return str(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(_json_safe_result(key)): _json_safe_result(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_json_safe_result(item) for item in value]
    asdict_method = getattr(value, "_asdict", None)
    if callable(asdict_method):
        try:
            return _json_safe_result(asdict_method())
        except Exception:
            pass
    value_dict = getattr(value, "__dict__", None)
    if isinstance(value_dict, dict):
        return _json_safe_result(value_dict)
    slots = getattr(value, "__slots__", None)
    if slots:
        names = [slots] if isinstance(slots, str) else list(slots)
        payload = {}
        for name in names:
            if isinstance(name, str) and not name.startswith("_") and hasattr(value, name):
                payload[name] = _json_safe_result(getattr(value, name))
        if payload:
            return payload
    return repr(value)


def _patchops_225_is_contract_payload(payload):
    return isinstance(payload, dict) and (
        "exit_code" in payload
        or "ok" in payload
        or "outer_report_path" in payload
        or "inner_report_path" in payload
        or "failure_category" in payload
    )


def _patchops_225_result_to_payload(result, *, report_path=None, notes=None):
    normalized_note = "Normalized non-PackageRunResult result shape to stable result contract."
    notes = list(notes or [])

    if isinstance(result, dict):
        payload = _json_safe_result(result)
        if not isinstance(payload, dict):
            payload = {}
        payload_notes = list(payload.get("notes") or [])
        if normalized_note not in payload_notes:
            payload_notes.append(normalized_note)
        payload["notes"] = payload_notes
        payload.setdefault("exit_code", 0)
        payload.setdefault("ok", int(payload.get("exit_code") or 0) == 0)
        payload.setdefault("failure_category", "none" if payload.get("ok") else "wrapper_failure")
    elif hasattr(result, "__dict__"):
        payload = _json_safe_result(result)
        if not _patchops_225_is_contract_payload(payload):
            payload = {
                "ok": False,
                "exit_code": 1,
                "failure_category": "wrapper_failure",
                "stderr": "run_delivery_package returned a non-contract attribute object; failed closed to preserve the stable result contract.",
                "notes": [normalized_note, "failed closed to preserve the stable result contract"],
                "raw_result_repr": repr(result),
            }
        else:
            payload_notes = list(payload.get("notes") or [])
            if normalized_note not in payload_notes:
                payload_notes.append(normalized_note)
            payload["notes"] = payload_notes
            payload.setdefault("exit_code", 0)
            payload.setdefault("ok", int(payload.get("exit_code") or 0) == 0)
            payload.setdefault("failure_category", "none" if payload.get("ok") else "wrapper_failure")
    else:
        payload = {
            "ok": False,
            "exit_code": 1,
            "failure_category": "wrapper_failure",
            "stderr": f"run_delivery_package returned {type(result).__name__} scalar/non-contract result; failed closed to preserve the stable result contract.",
            "notes": [normalized_note, "failed closed to preserve the stable result contract"],
            "raw_result": _json_safe_result(result),
        }

    if notes:
        payload_notes = list(payload.get("notes") or [])
        payload_notes.extend(notes)
        payload["notes"] = payload_notes

    if report_path is not None and not payload.get("outer_report_path"):
        payload["outer_report_path"] = str(report_path)

    return payload


def _patchops_225_exception_payload(exc, *, report_path=None):
    return {
        "ok": False,
        "exit_code": 1,
        "failure_category": "wrapper_failure",
        "stderr": f"{type(exc).__name__}: {exc}",
        "notes": [
            "run_delivery_package raised an unexpected exception; failed closed to preserve the stable result contract."
        ],
        "outer_report_path": str(report_path) if report_path else None,
    }


def _patchops_225_write_cli_report(report_path, payload):
    if not report_path:
        return
    from pathlib import Path as _Path

    path = _Path(report_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "PATCHOPS RUN-PACKAGE OUTER REPORT",
        "---------------------------------",
        f"Result : {'PASS' if payload.get('ok') else 'FAIL'}",
        f"ExitCode : {payload.get('exit_code', 1)}",
        f"FailureCategory : {payload.get('failure_category')}",
        f"OuterReportPath : {path}",
        "",
        "NOTES",
        "-----",
    ]

    notes = payload.get("notes") or []
    if notes:
        lines.extend(str(note) for note in notes)
    else:
        lines.append("(none)")

    lines.extend(
        [
            "",
            "STDOUT",
            "------",
            str(payload.get("stdout") or ""),
            "",
            "STDERR",
            "------",
            str(payload.get("stderr") or ""),
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
def cli_main(argv=None):
    raw_argv = list(argv or [])
    if raw_argv and isinstance(raw_argv[0], str) and _looks_like_windows_missing_drive_path(raw_argv[0]):
        sys.stderr.write(
            f"source_path looks like a Windows path but is missing its drive letter: {raw_argv[0]}. Working directory: {Path.cwd()}\n"
        )
        raise SystemExit(2)

    wrapper_root_raw = _extract_option_value_from_argv(raw_argv, "--wrapper-root")
    if _looks_like_windows_missing_drive_path(wrapper_root_raw):
        sys.stderr.write(
            f"wrapper_root looks like a Windows path but is missing its drive letter: {wrapper_root_raw}. Working directory: {Path.cwd()}\n"
        )
        raise SystemExit(2)

    import argparse
    import json

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

    args = parser.parse_args(raw_argv if argv is not None else None)

    try:
        try:
            source_path = _validate_cli_path_text("source_path", args.source_path)
            wrapper_root = _validate_cli_path_text("wrapper_root", args.wrapper_root)
            report_path = _validate_cli_path_text("report_path", args.report_path) if args.report_path else None
            desktop_dir = _validate_cli_path_text("desktop_dir", args.desktop_dir) if args.desktop_dir else None
        except NameError:
            source_path = Path(args.source_path)
            wrapper_root = Path(args.wrapper_root)
            report_path = Path(args.report_path) if args.report_path else None
            desktop_dir = Path(args.desktop_dir) if args.desktop_dir else None

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
        payload = _patchops_225_result_to_payload(result, report_path=report_path)
    except Exception as exc:  # noqa: BLE001
        report_path = Path(args.report_path) if args.report_path else None
        payload = _patchops_225_exception_payload(exc, report_path=report_path)

    _patchops_225_write_cli_report(payload.get("outer_report_path") or (str(args.report_path) if args.report_path else None), payload)
    print(json.dumps(_json_safe_result(payload), indent=2))
    try:
        return int(payload.get("exit_code") or 0)
    except Exception:
        return 1
def _patchops_p01_extract_call_arguments(original_fn, args, kwargs):
    try:
        signature = _patchops_p01_inspect.signature(original_fn)
        bound = signature.bind_partial(*args, **kwargs)
        data = dict(bound.arguments)
    except Exception:
        data = dict(kwargs)
        if args:
            if "source_path" not in data:
                data["source_path"] = args[0]
            if len(args) > 1 and "wrapper_root" not in data:
                data["wrapper_root"] = args[1]
            if len(args) > 2 and "report_path" not in data:
                data["report_path"] = args[2]
            if len(args) > 3 and "desktop_dir" not in data:
                data["desktop_dir"] = args[3]
    return data


def _patchops_p01_should_preflight_reject(source_path):
    try:
        path_obj = Path(str(source_path))
    except Exception:
        return False, None
    if path_obj.suffix.lower() != ".zip":
        return False, None
    try:
        from patchops import bundle_review as _patchops_p01_bundle_review
    except Exception:
        return False, None
    try:
        payload = _patchops_p01_bundle_review.inspect_bundle_payload(path_obj)
    except Exception:
        return False, None
    if not isinstance(payload, dict):
        return False, None
    launcher_status = str(payload.get("launcher_status") or "").strip().lower()
    if not launcher_status:
        launcher_review = payload.get("launcher_review")
        if isinstance(launcher_review, dict):
            launcher_status = str(launcher_review.get("status") or "").strip().lower()
    return launcher_status == "reject", payload


def _patchops_p01_build_notes(payload):
    notes = ["Launcher execution skipped due to bundle review rejection."]
    issue_codes = payload.get("launcher_issue_codes")
    if isinstance(issue_codes, list) and issue_codes:
        notes.append("Launcher review issue codes: " + ", ".join(str(item) for item in issue_codes))
    launcher_review = payload.get("launcher_review")
    review_issues = launcher_review.get("issues") if isinstance(launcher_review, dict) else None
    if isinstance(review_issues, list):
        for item in review_issues:
            if isinstance(item, dict):
                parts = []
                code = item.get("code")
                message = item.get("message")
                path = item.get("path")
                if code:
                    parts.append(f"code={code}")
                if path:
                    parts.append(f"path={path}")
                if message:
                    parts.append(str(message))
                if parts:
                    notes.append("Launcher review: " + " | ".join(parts))
            elif item:
                notes.append(f"Launcher review: {item}")
    payload_issues = payload.get("issues")
    if isinstance(payload_issues, list):
        for item in payload_issues:
            if isinstance(item, str) and item.strip():
                notes.append(f"Bundle review issue: {item.strip()}")
    return notes


def _patchops_p01_write_report(report_path, source_path, payload, notes, stderr_text):
    if not report_path:
        return
    try:
        report_obj = Path(str(report_path))
    except Exception:
        return
    try:
        report_obj.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    launcher_review = payload.get("launcher_review") if isinstance(payload, dict) else None
    launcher_path = None
    if isinstance(launcher_review, dict):
        launcher_path = launcher_review.get("launcher_path")
    lines = [
        "PATCHOPS RUN-PACKAGE OUTER REPORT",
        "Result              : FAIL",
        "Failure Category    : package_authoring_failure",
        f"Source Path         : {source_path}",
        "Source Kind         : zip",
        "Extracted Path      : (not applicable)",
        "Bundle Root         : (preflight rejected before extraction)",
        f"Launcher Path       : {launcher_path or '(unknown)'}",
        "Inner Report Path   : (not detected)",
        "InnerReportFound   : False",
        "Inner Result        : (not detected)",
        "Inner Exit Code     : (not detected)",
        "Inner Failure       : (none)",
        f"Outer Report Path   : {report_obj}",
        "Exit Code           : 1",
        "",
        "STDERR",
        "------",
        stderr_text or "(none)",
        "",
        "NOTES",
        "-----",
    ]
    if notes:
        lines.extend(notes)
    else:
        lines.append("(none)")
    report_obj.write_text("\n".join(str(item) for item in lines) + "\n", encoding="utf-8")


_PATCHOPS_P01_V8_ORIGINAL_RUN_DELIVERY_PACKAGE = run_delivery_package

def run_delivery_package(*args, **kwargs):
    call_data = _patchops_p01_extract_call_arguments(_PATCHOPS_P01_V8_ORIGINAL_RUN_DELIVERY_PACKAGE, args, kwargs)
    source_path = call_data.get("source_path") or call_data.get("package_path") or call_data.get("source") or (args[0] if args else None)
    report_path = call_data.get("report_path")
    should_reject, payload = _patchops_p01_should_preflight_reject(source_path)
    if not should_reject:
        return _PATCHOPS_P01_V8_ORIGINAL_RUN_DELIVERY_PACKAGE(*args, **kwargs)
    notes = _patchops_p01_build_notes(payload or {})
    stderr_text = "\n".join(notes)
    _patchops_p01_write_report(report_path, source_path, payload or {}, notes, stderr_text)
    launcher_path = None
    if isinstance(payload, dict):
        launcher_review = payload.get("launcher_review")
        if isinstance(launcher_review, dict):
            launcher_path = launcher_review.get("launcher_path")
    return _patchops_p01_SimpleNamespace(
        ok=False,
        exit_code=1,
        failure_category="package_authoring_failure",
        inner_report_path=None,
        stderr=stderr_text,
        notes=notes,
        stdout="",
        launcher_path=launcher_path,
        source_kind="zip",
        extracted_path=None,
        bundle_root=None,
        inner_result=None,
        inner_exit_code=None,
        inner_failure_category=None,
        outer_report_path=str(report_path) if report_path else None,
    )
# PATCHOPS_PATCH_01_V8_END

# PATCHOPS_225C_FINAL_CONTRACT_OVERRIDE_START
def _json_safe_result(value, *, _top_level: bool = True):
    from dataclasses import fields, is_dataclass
    from enum import Enum
    from pathlib import Path as _Path

    def nested(item):
        return _json_safe_result(item, _top_level=False)

    if isinstance(value, Enum):
        resolved = value.value
        return {"result": resolved} if _top_level else resolved

    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: nested(getattr(value, field.name)) for field in fields(value)}

    if isinstance(value, _Path):
        resolved = str(value)
        return {"result": resolved} if _top_level else resolved

    if value is None or isinstance(value, (str, int, float, bool)):
        return {"result": value} if _top_level else value

    if isinstance(value, dict):
        return {str(nested(key)): nested(item) for key, item in value.items()}

    if isinstance(value, (list, tuple, set, frozenset)):
        return [nested(item) for item in value]

    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        try:
            converted = to_dict()
            if isinstance(converted, dict):
                return {str(nested(key)): nested(item) for key, item in converted.items()}
            return nested(converted)
        except Exception:
            pass

    asdict_method = getattr(value, "_asdict", None)
    if callable(asdict_method):
        try:
            converted = asdict_method()
            if isinstance(converted, dict):
                return {str(nested(key)): nested(item) for key, item in converted.items()}
            return nested(converted)
        except Exception:
            pass

    value_dict = getattr(value, "__dict__", None)
    if isinstance(value_dict, dict) and value_dict:
        return {str(nested(key)): nested(item) for key, item in value_dict.items()}

    slots = getattr(value, "__slots__", None)
    if slots:
        names = [slots] if isinstance(slots, str) else list(slots)
        payload = {}
        for name in names:
            if isinstance(name, str) and not name.startswith("_") and hasattr(value, name):
                payload[name] = nested(getattr(value, name))
        if payload:
            return payload

    return {
        "result_type": type(value).__name__,
        "repr": repr(value),
        "result_repr": repr(value),
    }


def _patchops_225_is_contract_payload(payload):
    return isinstance(payload, dict) and (
        "exit_code" in payload
        or "ok" in payload
        or "outer_report_path" in payload
        or "inner_report_path" in payload
        or "failure_category" in payload
    )


def _patchops_225_result_to_payload(result, *, report_path=None, notes=None):
    normalized_note = "Normalized non-PackageRunResult result shape to stable result contract."
    notes = list(notes or [])

    if isinstance(result, dict):
        payload = _json_safe_result(result, _top_level=False)
        payload_notes = list(payload.get("notes") or [])
        if normalized_note not in payload_notes:
            payload_notes.append(normalized_note)
        if notes:
            payload_notes.extend(notes)
        payload["notes"] = payload_notes
        payload.setdefault("exit_code", 0)
        payload.setdefault("ok", int(payload.get("exit_code") or 0) == 0)
        payload.setdefault("failure_category", "none" if payload.get("ok") else "wrapper_failure")
    elif hasattr(result, "__dict__"):
        payload = _json_safe_result(result, _top_level=False)
        if not _patchops_225_is_contract_payload(payload):
            result_type = type(result).__name__
            message = (
                f"Non-PackageRunResult returned by run_delivery_package: {result_type}. "
                "Failed closed to preserve the stable result contract."
            )
            payload = {
                "ok": False,
                "exit_code": 1,
                "failure_category": "wrapper_failure",
                "stderr": message,
                "notes": [normalized_note, "failed closed to preserve the stable result contract"],
                "raw_result_repr": repr(result),
            }
        else:
            payload_notes = list(payload.get("notes") or [])
            if normalized_note not in payload_notes:
                payload_notes.append(normalized_note)
            if notes:
                payload_notes.extend(notes)
            payload["notes"] = payload_notes
            payload.setdefault("exit_code", 0)
            payload.setdefault("ok", int(payload.get("exit_code") or 0) == 0)
            payload.setdefault("failure_category", "none" if payload.get("ok") else "wrapper_failure")
    else:
        result_type = type(result).__name__
        message = (
            f"Non-PackageRunResult returned by run_delivery_package: {result_type}. "
            "Failed closed to preserve the stable result contract."
        )
        payload = {
            "ok": False,
            "exit_code": 1,
            "failure_category": "wrapper_failure",
            "stderr": message,
            "notes": [normalized_note, "failed closed to preserve the stable result contract"],
            "raw_result": _json_safe_result(result),
        }

    if report_path is not None and not payload.get("outer_report_path"):
        from pathlib import Path as _Path
        payload["outer_report_path"] = str(_Path(report_path).resolve())
    elif payload.get("outer_report_path"):
        from pathlib import Path as _Path
        payload["outer_report_path"] = str(_Path(payload["outer_report_path"]).resolve())

    return payload


def _patchops_225_exception_payload(exc, *, report_path=None):
    from pathlib import Path as _Path

    payload = {
        "ok": False,
        "exit_code": 1,
        "failure_category": "wrapper_failure",
        "stderr": f"{type(exc).__name__}: {exc}",
        "notes": [
            "run_delivery_package raised an unexpected exception; failed closed to preserve the stable result contract."
        ],
    }
    if report_path:
        payload["outer_report_path"] = str(_Path(report_path).resolve())
    return payload


def _patchops_225_write_cli_report(report_path, payload):
    if not report_path:
        return
    from pathlib import Path as _Path

    path = _Path(report_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    result_label = "PASS" if payload.get("ok") else "FAIL"
    exit_code = payload.get("exit_code", 1)
    failure_category = payload.get("failure_category")
    stderr_text = str(payload.get("stderr") or "")

    lines = [
        "PATCHOPS RUN-PACKAGE OUTER REPORT",
        "---------------------------------",
        f"Result              : {result_label}",
        f"Exit Code           : {exit_code}",
        f"ExitCode            : {exit_code}",
        f"Failure Category    : {failure_category}",
        f"FailureCategory     : {failure_category}",
        f"Outer Report Path   : {path}",
        f"OuterReportPath     : {path}",
        "",
        "NOTES",
        "-----",
    ]

    notes = payload.get("notes") or []
    if notes:
        lines.extend(str(note) for note in notes)
    else:
        lines.append("(none)")

    if "Non-PackageRunResult returned by run_delivery_package:" in stderr_text:
        lines.extend(["", stderr_text])

    lines.extend(
        [
            "",
            "STDOUT",
            "------",
            str(payload.get("stdout") or ""),
            "",
            "STDERR",
            "------",
            stderr_text,
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
# PATCHOPS_225C_FINAL_CONTRACT_OVERRIDE_END

# PATCHOPS_226_RUN_PACKAGE_RESULT_CONTRACT_REPAIR_START
def _json_safe_result(value, *, _top_level: bool = True):
    from dataclasses import fields, is_dataclass
    from enum import Enum
    from pathlib import Path as _Path

    def nested(item):
        return _json_safe_result(item, _top_level=False)

    if isinstance(value, Enum):
        resolved = value.value
        return {"result": resolved} if _top_level else resolved

    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: nested(getattr(value, field.name)) for field in fields(value)}

    if isinstance(value, _Path):
        resolved = str(value)
        return {"result": resolved} if _top_level else resolved

    if value is None or isinstance(value, (str, int, float, bool)):
        return {"result": value} if _top_level else value

    if isinstance(value, dict):
        return {str(nested(key)): nested(item) for key, item in value.items()}

    if isinstance(value, (list, tuple, set, frozenset)):
        return [nested(item) for item in value]

    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        try:
            converted = to_dict()
            if isinstance(converted, dict):
                return {str(nested(key)): nested(item) for key, item in converted.items()}
            return nested(converted)
        except Exception:
            pass

    asdict_method = getattr(value, "_asdict", None)
    if callable(asdict_method):
        try:
            converted = asdict_method()
            if isinstance(converted, dict):
                return {str(nested(key)): nested(item) for key, item in converted.items()}
            return nested(converted)
        except Exception:
            pass

    value_dict = getattr(value, "__dict__", None)
    if isinstance(value_dict, dict) and value_dict:
        return {str(nested(key)): nested(item) for key, item in value_dict.items()}

    slots = getattr(value, "__slots__", None)
    if slots:
        names = [slots] if isinstance(slots, str) else list(slots)
        payload = {}
        for name in names:
            if isinstance(name, str) and not name.startswith("_") and hasattr(value, name):
                payload[name] = nested(getattr(value, name))
        if payload:
            return payload

    return {
        "result_type": type(value).__name__,
        "repr": repr(value),
        "result_repr": repr(value),
    }


def _patchops_226_is_valid_result_payload(payload):
    if not isinstance(payload, dict):
        return False

    if not any(key in payload for key in ("ok", "exit_code", "report_path", "outer_report_path", "inner_report_path", "failure_category")):
        return False

    if "ok" in payload and not isinstance(payload.get("ok"), bool):
        return False

    if "exit_code" in payload:
        try:
            int(payload.get("exit_code") or 0)
        except Exception:
            return False

    return True


def _patchops_225_is_contract_payload(payload):
    return _patchops_226_is_valid_result_payload(payload)


def _patchops_226_normalize_result_payload(payload, *, report_path=None, extra_notes=None):
    from pathlib import Path as _Path

    normalized = dict(payload)

    if "exit_code" not in normalized:
        normalized["exit_code"] = 0 if normalized.get("ok") is True else 1
    else:
        try:
            normalized["exit_code"] = int(normalized.get("exit_code") or 0)
        except Exception:
            normalized["exit_code"] = 1

    if "ok" not in normalized:
        normalized["ok"] = normalized["exit_code"] == 0

    if "failure_category" not in normalized or normalized.get("failure_category") is None:
        normalized["failure_category"] = "none" if normalized.get("ok") else "wrapper_failure"

    if report_path is not None and not normalized.get("outer_report_path") and not normalized.get("report_path"):
        normalized["outer_report_path"] = str(_Path(report_path).resolve())

    for key in ("outer_report_path", "inner_report_path", "report_path"):
        if normalized.get(key):
            normalized[key] = str(normalized[key])

    existing_notes = normalized.get("notes")
    if existing_notes is None:
        normalized["notes"] = []
    elif isinstance(existing_notes, list):
        normalized["notes"] = [str(note) for note in existing_notes]
    else:
        normalized["notes"] = [str(existing_notes)]

    if extra_notes:
        normalized["notes"].extend(str(note) for note in extra_notes)

    return normalized


def _patchops_225_result_to_payload(result, *, report_path=None, notes=None):
    converted = _json_safe_result(result, _top_level=False)

    if _patchops_226_is_valid_result_payload(converted):
        return _patchops_226_normalize_result_payload(converted, report_path=report_path, extra_notes=notes)

    result_type = type(result).__name__
    message = (
        f"Non-PackageRunResult returned by run_delivery_package: {result_type}. "
        "Failed closed to preserve the stable result contract."
    )
    return {
        "ok": False,
        "exit_code": 1,
        "failure_category": "wrapper_failure",
        "stderr": message,
        "notes": [
            "Normalized non-PackageRunResult result shape to stable result contract.",
            "failed closed to preserve the stable result contract",
        ],
        "raw_result": converted,
        "outer_report_path": str(report_path) if report_path else None,
    }


def _patchops_225_exception_payload(exc, *, report_path=None):
    from pathlib import Path as _Path

    payload = {
        "ok": False,
        "exit_code": 1,
        "failure_category": "wrapper_failure",
        "stderr": f"{type(exc).__name__}: {exc}",
        "notes": [
            "run_delivery_package raised an unexpected exception; failed closed to preserve the stable result contract."
        ],
    }
    if report_path:
        payload["outer_report_path"] = str(_Path(report_path).resolve())
    return payload


def _patchops_225_write_cli_report(report_path, payload):
    if not report_path:
        return
    from pathlib import Path as _Path

    path = _Path(report_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    result_label = "PASS" if payload.get("ok") else "FAIL"
    exit_code = payload.get("exit_code", 1)
    failure_category = payload.get("failure_category")
    stderr_text = str(payload.get("stderr") or "")

    lines = [
        "PATCHOPS RUN-PACKAGE OUTER REPORT",
        "---------------------------------",
        f"Result              : {result_label}",
        f"Exit Code           : {exit_code}",
        f"ExitCode            : {exit_code}",
        f"Failure Category    : {failure_category}",
        f"FailureCategory     : {failure_category}",
        f"Outer Report Path   : {path}",
        f"OuterReportPath     : {path}",
        "",
        "NOTES",
        "-----",
    ]

    notes = payload.get("notes") or []
    if notes:
        lines.extend(str(note) for note in notes)
    else:
        lines.append("(none)")

    if "Non-PackageRunResult returned by run_delivery_package:" in stderr_text:
        lines.extend(["", stderr_text])

    lines.extend(
        [
            "",
            "STDOUT",
            "------",
            str(payload.get("stdout") or ""),
            "",
            "STDERR",
            "------",
            stderr_text,
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
# PATCHOPS_226_RUN_PACKAGE_RESULT_CONTRACT_REPAIR_END

# PATCHOPS_226A_DICT_RESULT_NORMALIZATION_NOTE_REPAIR_START
def _patchops_225_result_to_payload(result, *, report_path=None, notes=None):
    normalized_note = "Normalized non-PackageRunResult result shape to stable result contract."
    converted = _json_safe_result(result, _top_level=False)

    if _patchops_226_is_valid_result_payload(converted):
        extra_notes = list(notes or [])
        if isinstance(result, dict):
            existing_notes = converted.get("notes")
            if isinstance(existing_notes, list):
                already_present = any(normalized_note in str(note) for note in existing_notes)
            elif existing_notes is None:
                already_present = False
            else:
                already_present = normalized_note in str(existing_notes)
            if not already_present:
                extra_notes.insert(0, normalized_note)

        return _patchops_226_normalize_result_payload(
            converted,
            report_path=report_path,
            extra_notes=extra_notes,
        )

    result_type = type(result).__name__
    message = (
        f"Non-PackageRunResult returned by run_delivery_package: {result_type}. "
        "Failed closed to preserve the stable result contract."
    )
    return {
        "ok": False,
        "exit_code": 1,
        "failure_category": "wrapper_failure",
        "stderr": message,
        "notes": [
            normalized_note,
            "failed closed to preserve the stable result contract",
        ],
        "raw_result": converted,
        "outer_report_path": str(report_path) if report_path else None,
    }
# PATCHOPS_226A_DICT_RESULT_NORMALIZATION_NOTE_REPAIR_END

# PATCHOPS_227_RUN_PACKAGE_PREFLIGHT_EXECUTION_TRUTH_START
def _patchops_227_call_existing(name, *args, default=None, **kwargs):
    func = globals().get(name)
    if callable(func):
        return func(*args, **kwargs)
    return default


def _patchops_227_snapshot_txt_files(desktop):
    func = globals().get("_snapshot_txt_files")
    if callable(func):
        try:
            return func(desktop)
        except Exception:
            pass
    try:
        return {path.resolve() for path in desktop.glob("*.txt")}
    except Exception:
        return set()


def _patchops_227_extract_zip_source(source_path, wrapper_root):
    func = globals().get("_extract_zip_source")
    if callable(func):
        return func(source_path, wrapper_root)

    import zipfile
    extract_root = wrapper_root / "data" / "runtime" / "package_runs" / f"run_package_{_utc_stamp()}" / "extracted"
    extract_root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source_path, "r") as archive:
        archive.extractall(extract_root)

    children = [child for child in extract_root.iterdir() if child.is_dir()]
    if len(children) == 1:
        return extract_root, children[0]
    return extract_root, extract_root


def _patchops_227_normalize_capture(command, cwd, raw_capture):
    func = globals().get("_normalize_capture")
    if callable(func):
        return func(command, cwd, raw_capture)

    if isinstance(raw_capture, ProcessCapture):
        return raw_capture

    if isinstance(raw_capture, dict):
        return ProcessCapture(
            command=list(raw_capture.get("command") or command),
            working_directory=str(raw_capture.get("working_directory") or cwd),
            exit_code=int(raw_capture.get("exit_code") or 0),
            stdout=str(raw_capture.get("stdout") or ""),
            stderr=str(raw_capture.get("stderr") or ""),
        )

    return ProcessCapture(
        command=list(command),
        working_directory=str(cwd),
        exit_code=int(getattr(raw_capture, "exit_code", 0) or 0),
        stdout=str(getattr(raw_capture, "stdout", "") or ""),
        stderr=str(getattr(raw_capture, "stderr", "") or ""),
    )


def _patchops_227_read_inner_report_summary(inner_report):
    if inner_report is None:
        return None
    func = globals().get("_read_inner_report_summary")
    if callable(func):
        try:
            return func(inner_report)
        except Exception:
            pass

    path = Path(inner_report)
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    exit_code = None
    result_label = None
    failure_category = None

    import re
    m = re.search(r"ExitCode\s*:\s*(-?\d+)", text)
    if m:
        exit_code = int(m.group(1))
    m = re.search(r"Result\s*:?\s*([A-Z]+)", text)
    if m:
        result_label = m.group(1)
    m = re.search(r"(?:Failure Class|FailureCategory|Category)\s*:\s*([A-Za-z0-9_\-]+)", text)
    if m:
        failure_category = m.group(1)

    return {
        "exit_code": exit_code,
        "result": result_label,
        "failure_category": failure_category,
    }


def _patchops_227_inner_value(summary, *names):
    if summary is None:
        return None
    for name in names:
        if isinstance(summary, dict) and name in summary:
            return summary.get(name)
        if hasattr(summary, name):
            return getattr(summary, name)
    return None


def _patchops_227_resolve_effective_outcome(capture, inner_summary, notes):
    func = globals().get("_resolve_effective_outcome")
    if callable(func):
        try:
            return func(capture=capture, inner_summary=inner_summary, notes=notes)
        except Exception:
            pass

    inner_exit = _patchops_227_inner_value(inner_summary, "exit_code", "inner_exit_code")
    inner_result = _patchops_227_inner_value(inner_summary, "result", "result_label", "inner_result")
    inner_category = _patchops_227_inner_value(inner_summary, "failure_category", "category", "inner_failure_category")

    if inner_exit is not None:
        code = int(inner_exit)
        ok = code == 0 and str(inner_result or "PASS").upper() == "PASS"
        return ok, code, ("none" if ok else (inner_category or "target_project_failure"))

    stderr_text = str(getattr(capture, "stderr", "") or "")
    if "SyntaxError" in stderr_text or "ModuleNotFoundError" in stderr_text or "Traceback" in stderr_text:
        return False, 1, "wrapper_failure"

    code = int(getattr(capture, "exit_code", 0) or 0)
    ok = code == 0
    return ok, code, ("none" if ok else "target_project_failure")


def _patchops_227_write_report(result, requested_outer_report_path):
    writer = globals().get("_write_single_canonical_report")
    if callable(writer):
        try:
            return writer(result, requested_outer_report_path=requested_outer_report_path)
        except Exception:
            pass

    writer = globals().get("_write_report")
    if callable(writer):
        try:
            return writer(result, requested_outer_report_path=requested_outer_report_path)
        except TypeError:
            try:
                return writer(result)
            except Exception:
                pass
        except Exception:
            pass

    path = Path(result.inner_report_path).resolve() if result.inner_report_path else Path(requested_outer_report_path).resolve()
    if result.inner_report_path and path.exists():
        result.notes.append("Canonical run-package context merged into inner report; no separate outer report artifact was kept.")
    else:
        path = Path(requested_outer_report_path).resolve()

    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "PATCHOPS RUN-PACKAGE OUTER REPORT",
        "================================",
        f"Result              : {'PASS' if result.ok else 'FAIL'}",
        f"Failure Category    : {result.failure_category or '(none)'}",
        f"Source Path         : {result.source_path}",
        f"Source Kind         : {result.source_kind}",
        f"Extracted Path      : {result.extracted_path or '(not applicable)'}",
        f"Bundle Root         : {result.bundle_root}",
        f"Launcher Path       : {result.launcher_path}",
        f"Launcher Cwd        : {result.launcher_working_directory}",
        f"Inner Report Path   : {result.inner_report_path or '(not detected)'}",
        f"Inner Result        : {result.inner_result or '(not detected)'}",
        f"Inner Exit Code     : {result.inner_exit_code if result.inner_exit_code is not None else '(not detected)'}",
        f"Inner Failure       : {result.inner_failure_category or '(none)'}",
        f"Outer Report Path   : {path}",
        f"Exit Code           : {result.exit_code}",
        "",
        "COMMAND",
        "-------",
        _quote_command(result.launcher_command) if "_quote_command" in globals() else " ".join(str(x) for x in result.launcher_command),
        "",
        "STDOUT",
        "------",
        result.stdout or "(empty)",
        "",
        "STDERR",
        "------",
        result.stderr or "(empty)",
        "",
        "NOTES",
        "-----",
    ]
    if result.notes:
        lines.extend(f"- {note}" for note in result.notes)
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "SUMMARY",
            "-------",
            f"Ok                 : {result.ok}",
            f"FailureCategory    : {result.failure_category or '(none)'}",
            f"InnerReportFound   : {bool(result.inner_report_path)}",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result.outer_report_path = str(path)
    return path


def _patchops_227_failure_result(
    *,
    source_path,
    source_kind,
    extracted_path=None,
    bundle_root=None,
    launcher_path=None,
    command=None,
    cwd=None,
    exit_code=1,
    stdout="",
    stderr="",
    failure_category="wrapper_failure",
    notes=None,
    report_path=None,
):
    result = PackageRunResult(
        ok=False,
        source_path=str(source_path),
        source_kind=source_kind,
        extracted_path=str(extracted_path) if extracted_path else None,
        bundle_root=str(bundle_root) if bundle_root else None,
        launcher_path=str(launcher_path) if launcher_path else None,
        launcher_command=list(command or []),
        launcher_working_directory=str(cwd) if cwd else None,
        exit_code=int(exit_code),
        stdout=str(stdout or ""),
        stderr=str(stderr or ""),
        inner_report_path=None,
        inner_result=None,
        inner_exit_code=None,
        inner_failure_category=None,
        outer_report_path=str(report_path) if report_path else None,
        failure_category=failure_category,
        notes=list(notes or []),
    )
    if report_path:
        _patchops_227_write_report(result, Path(report_path))
    return result


def _patchops_227_classify_setup_exception(exc):
    classifier = globals().get("_classify_setup_failure_message")
    if callable(classifier):
        try:
            return classifier(str(exc))
        except Exception:
            pass
    if isinstance(exc, FileNotFoundError):
        return "environment_failure"
    return "wrapper_failure"


def _patchops_227_should_reject_source(source_path):
    checker = globals().get("_patchops_p01_should_preflight_reject")
    if callable(checker):
        try:
            return checker(source_path)
        except Exception as exc:
            return True, {
                "issues": [{"code": "preflight_exception", "message": str(exc)}],
                "launcher_review": {},
            }
    return False, None


def run_delivery_package(
    source_path: Path,
    *,
    wrapper_root: Path,
    mode: str = "apply",
    profile: str | None = None,
    launcher_relative_path: str | None = None,
    report_path: Path | None = None,
    powershell_exe: str | None = None,
    desktop_dir: Path | None = None,
    runner=None,
) -> PackageRunResult:
    requested_report_path_input = report_path
    source_path = Path(source_path).resolve()
    wrapper_root = Path(wrapper_root).resolve()
    desktop = _desktop_dir(desktop_dir)
    report_path = (Path(report_path) if report_path else (desktop / f"patchops_run_package_{_utc_stamp()}.txt")).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)

    notes: list[str] = []
    extraction_root: Path | None = None
    bundle_root: Path | None = None
    launcher_path: Path | None = None
    command: list[str] = []
    desktop_before = _patchops_227_snapshot_txt_files(desktop)
    run_root = wrapper_root / "data" / "runtime" / "package_runs" / f"run_package_{_utc_stamp()}"
    run_root.mkdir(parents=True, exist_ok=True)
    source_kind = "unknown"

    try:
        should_reject, payload = _patchops_227_should_reject_source(source_path)
        if should_reject:
            build_notes = globals().get("_patchops_p01_build_notes")
            if callable(build_notes):
                try:
                    notes = list(build_notes(payload or {}))
                except Exception:
                    notes = []
            if not notes:
                notes = ["Launcher execution skipped due to bundle review rejection."]
            stderr_text = "\n".join(notes)
            launcher_review = (payload or {}).get("launcher_review") if isinstance(payload, dict) else None
            launcher_path_text = launcher_review.get("launcher_path") if isinstance(launcher_review, dict) else None
            return _patchops_227_failure_result(
                source_path=source_path,
                source_kind="zip" if source_path.suffix.lower() == ".zip" else ("folder" if source_path.is_dir() else "unknown"),
                launcher_path=launcher_path_text,
                exit_code=1,
                stderr=stderr_text,
                failure_category="package_authoring_failure",
                notes=notes,
                report_path=report_path,
            )

        if not source_path.exists():
            raise FileNotFoundError(f"Package source does not exist: {source_path}")

        if source_path.is_file():
            if source_path.suffix.lower() != ".zip":
                raise ValueError(f"Unsupported package file type: {source_path.suffix}")
            source_kind = "zip"
            extraction_root, bundle_root = _patchops_227_extract_zip_source(source_path, wrapper_root)
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
            notes.append(
                "Bundle preflight skipped because the bundle does not advertise the canonical staged-authoring contract."
            )

        launcher_path = _discover_launcher(
            bundle_root,
            mode=mode,
            bundle_meta=bundle_meta,
            launcher_relative_path=launcher_relative_path,
        )
        command = _build_launcher_command(
            launcher_path=launcher_path,
            wrapper_root=wrapper_root,
            bundle_root=bundle_root,
            source_path=source_path,
            mode=mode,
            profile=profile,
            powershell_exe=powershell_exe,
        )

        active_runner = runner or _default_runner
        capture = _patchops_227_normalize_capture(command, bundle_root, active_runner(command, bundle_root))

        inner_report = _detect_inner_report_path(
            stdout=capture.stdout,
            stderr=capture.stderr,
            desktop_dir=desktop,
            desktop_before=desktop_before,
            outer_report_path=report_path,
            run_root=run_root,
        )
        inner_summary = _patchops_227_read_inner_report_summary(inner_report)

        ok, effective_exit_code, failure_category = _patchops_227_resolve_effective_outcome(
            capture,
            inner_summary,
            notes,
        )

        inner_result = _patchops_227_inner_value(inner_summary, "result", "result_label", "inner_result")
        inner_exit_code = _patchops_227_inner_value(inner_summary, "exit_code", "inner_exit_code")
        inner_failure_category = _patchops_227_inner_value(
            inner_summary,
            "failure_category",
            "category",
            "inner_failure_category",
        )

        result = PackageRunResult(
            ok=bool(ok),
            source_path=str(source_path),
            source_kind=source_kind,
            extracted_path=str(extraction_root) if extraction_root else None,
            bundle_root=str(bundle_root) if bundle_root else None,
            launcher_path=str(launcher_path) if launcher_path else None,
            launcher_command=list(command),
            launcher_working_directory=str(bundle_root) if bundle_root else None,
            exit_code=int(effective_exit_code),
            stdout=str(capture.stdout or ""),
            stderr=str(capture.stderr or ""),
            inner_report_path=str(inner_report) if inner_report else None,
            inner_result=inner_result,
            inner_exit_code=inner_exit_code,
            inner_failure_category=inner_failure_category,
            outer_report_path=str(report_path),
            failure_category=failure_category,
            notes=notes,
        )

        final_report_path = _patchops_227_write_report(result, requested_report_path_input or report_path)
        result.outer_report_path = str(final_report_path)
        return result

    except Exception as exc:  # noqa: BLE001
        failure_category = _patchops_227_classify_setup_exception(exc)
        notes.append(f"Package runner failed before or during launcher execution: {type(exc).__name__}: {exc}")
        return _patchops_227_failure_result(
            source_path=source_path,
            source_kind=source_kind,
            extracted_path=extraction_root,
            bundle_root=bundle_root,
            launcher_path=launcher_path,
            command=command,
            cwd=bundle_root,
            exit_code=1,
            stderr=f"{type(exc).__name__}: {exc}",
            failure_category=failure_category,
            notes=notes,
            report_path=report_path,
        )
# PATCHOPS_227_RUN_PACKAGE_PREFLIGHT_EXECUTION_TRUTH_END

# PATCHOPS_227A_PROCESS_CAPTURE_AND_OUTCOME_REPAIR_START
from dataclasses import dataclass as _patchops_227a_dataclass


@_patchops_227a_dataclass
class ProcessCapture:
    command: list[str]
    working_directory: str
    exit_code: int
    stdout: str
    stderr: str


def _patchops_227_normalize_capture(command, cwd, raw_capture):
    if isinstance(raw_capture, ProcessCapture):
        return raw_capture

    if isinstance(raw_capture, dict):
        return ProcessCapture(
            command=list(raw_capture.get("command") or command),
            working_directory=str(raw_capture.get("working_directory") or cwd),
            exit_code=int(raw_capture.get("exit_code") or 0),
            stdout=str(raw_capture.get("stdout") or ""),
            stderr=str(raw_capture.get("stderr") or ""),
        )

    return ProcessCapture(
        command=list(getattr(raw_capture, "command", command) or command),
        working_directory=str(getattr(raw_capture, "working_directory", cwd) or cwd),
        exit_code=int(getattr(raw_capture, "exit_code", 0) or 0),
        stdout=str(getattr(raw_capture, "stdout", "") or ""),
        stderr=str(getattr(raw_capture, "stderr", "") or ""),
    )


def _patchops_227_resolve_effective_outcome(capture, inner_summary, notes):
    inner_exit = _patchops_227_inner_value(inner_summary, "exit_code", "inner_exit_code")
    inner_result = _patchops_227_inner_value(inner_summary, "result", "result_label", "inner_result")
    inner_category = _patchops_227_inner_value(inner_summary, "failure_category", "category", "inner_failure_category")

    if inner_exit is not None:
        code = int(inner_exit)
        result_text = str(inner_result or ("PASS" if code == 0 else "FAIL")).upper()
        ok = code == 0 and result_text == "PASS"
        return ok, code, ("none" if ok else (inner_category or "target_project_failure"))

    stderr_text = str(getattr(capture, "stderr", "") or "")
    if "ModuleNotFoundError" in stderr_text:
        return False, 1, "wrapper_failure"
    if "SyntaxError" in stderr_text:
        return False, 1, "package_authoring_failure"
    if "Traceback" in stderr_text:
        return False, 1, "wrapper_failure"

    code = int(getattr(capture, "exit_code", 0) or 0)
    ok = code == 0
    return ok, code, ("none" if ok else "target_project_failure")
# PATCHOPS_227A_PROCESS_CAPTURE_AND_OUTCOME_REPAIR_END

# PATCHOPS_227B_CANONICAL_REPORT_AND_OUTCOME_CONTRACT_REPAIR_START
def _patchops_227b_normalize_failure_category(category):
    text = str(category or "").strip()
    if text in {"none", "(none)"}:
        return ""
    if text == "target_project_failure":
        return "target_content_failure"
    return text


def _patchops_227_resolve_effective_outcome(capture, inner_summary, notes):
    inner_exit = _patchops_227_inner_value(inner_summary, "exit_code", "inner_exit_code")
    inner_result = _patchops_227_inner_value(inner_summary, "result", "result_label", "inner_result")
    inner_category = _patchops_227_inner_value(inner_summary, "failure_category", "category", "inner_failure_category")

    if inner_exit is not None:
        code = int(inner_exit)
        result_text = str(inner_result or ("PASS" if code == 0 else "FAIL")).upper()
        ok = code == 0 and result_text == "PASS"
        if ok:
            return True, 0, ""
        return False, code, (_patchops_227b_normalize_failure_category(inner_category) or "target_content_failure")

    stderr_text = str(getattr(capture, "stderr", "") or "")
    fatal_note = "Fatal launcher stderr was detected without a real inner report; treating run-package outcome as FAIL."
    if "ModuleNotFoundError" in stderr_text:
        if fatal_note not in notes:
            notes.append(fatal_note)
        return False, 1, "wrapper_failure"
    if "SyntaxError" in stderr_text:
        if fatal_note not in notes:
            notes.append(fatal_note)
        return False, 1, "package_authoring_failure"
    if "Traceback" in stderr_text:
        if fatal_note not in notes:
            notes.append(fatal_note)
        return False, 1, "wrapper_failure"

    code = int(getattr(capture, "exit_code", 0) or 0)
    ok = code == 0
    return ok, code, ("" if ok else "target_content_failure")


def _patchops_227b_display_category(category):
    return _patchops_227b_normalize_failure_category(category) or "(none)"


def _patchops_227b_command_text(command):
    quote = globals().get("_quote_command")
    if callable(quote):
        try:
            return quote(command)
        except Exception:
            pass
    return " ".join(str(item) for item in (command or []))


def _patchops_227_write_report(result, requested_outer_report_path):
    from pathlib import Path as _Path

    inner_report_path = _Path(result.inner_report_path).resolve() if result.inner_report_path else None
    requested_path = _Path(requested_outer_report_path).resolve() if requested_outer_report_path else None

    original_inner_text = ""
    if inner_report_path and inner_report_path.exists():
        original_inner_text = inner_report_path.read_text(encoding="utf-8", errors="replace")

    if inner_report_path:
        path = inner_report_path
        if requested_path and requested_path != path and requested_path.exists():
            try:
                requested_path.unlink()
            except OSError:
                pass
        canonical_title = "PATCHOPS RUN-PACKAGE CANONICAL REPORT"
        secondary_title = "PATCHOPS RUN-PACKAGE OUTER REPORT"
        if "Canonical run-package context merged into inner report; no separate outer report artifact was kept." not in result.notes:
            result.notes.append("Canonical run-package context merged into inner report; no separate outer report artifact was kept.")
    else:
        path = requested_path or (_Path(result.outer_report_path).resolve() if result.outer_report_path else _Path.cwd() / f"patchops_run_package_{_utc_stamp()}.txt")
        canonical_title = "PATCHOPS RUN-PACKAGE OUTER REPORT"
        secondary_title = ""

    path.parent.mkdir(parents=True, exist_ok=True)

    inner_found = bool(inner_report_path)
    failure_category = _patchops_227b_normalize_failure_category(result.failure_category)
    result.failure_category = failure_category

    lines = [
        canonical_title,
        "=" * max(len(canonical_title), 32),
    ]
    if secondary_title:
        lines.extend([secondary_title, "-" * len(secondary_title)])

    lines.extend(
        [
            f"Result              : {'PASS' if result.ok else 'FAIL'}",
            f"Failure Category    : {_patchops_227b_display_category(failure_category)}",
            f"Source Path         : {result.source_path}",
            f"Source Kind         : {result.source_kind}",
            f"Extracted Path      : {result.extracted_path or '(not applicable)'}",
            f"Bundle Root         : {result.bundle_root}",
            f"Launcher Path       : {result.launcher_path}",
            f"Launcher Cwd        : {result.launcher_working_directory}",
            f"Inner Report Path   : {result.inner_report_path or '(not detected)'}",
            f"Inner Result        : {result.inner_result or '(not detected)'}",
            f"Inner Exit Code     : {result.inner_exit_code if result.inner_exit_code is not None else '(not detected)'}",
            f"Inner Failure       : {_patchops_227b_display_category(result.inner_failure_category)}",
            f"Outer Report Path   : {path}",
            f"Exit Code           : {result.exit_code}",
            "",
            "COMMAND",
            "-------",
            _patchops_227b_command_text(result.launcher_command),
            "",
            "STDOUT",
            "------",
            result.stdout or "(empty)",
            "",
            "STDERR",
            "------",
            result.stderr or "(empty)",
            "",
            "NOTES",
            "-----",
        ]
    )

    if result.notes:
        lines.extend(f"- {note}" for note in result.notes)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "SUMMARY",
            "-------",
            f"Ok                 : {result.ok}",
            f"FailureCategory    : {_patchops_227b_display_category(failure_category)}",
            f"InnerReportFound   : {inner_found}",
        ]
    )

    if original_inner_text:
        lines.extend(
            [
                "",
                "INNER REPORT",
                "------------",
                original_inner_text.rstrip(),
            ]
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result.outer_report_path = str(path)
    return path
# PATCHOPS_227B_CANONICAL_REPORT_AND_OUTCOME_CONTRACT_REPAIR_END

# PATCHOPS_227C_FINAL_CANONICAL_REPORT_CONTRACT_REPAIR_START
def _patchops_227c_normalize_failure_category(category):
    text = str(category or "").strip()
    if text in {"none", "(none)"}:
        return ""
    if text == "target_project_failure":
        return "target_content_failure"
    return text


def _patchops_227c_display_category(category):
    return _patchops_227c_normalize_failure_category(category) or "(none)"


def _patchops_227c_command_text(command):
    quote = globals().get("_quote_command")
    if callable(quote):
        try:
            return quote(command)
        except Exception:
            pass
    return " ".join(str(item) for item in (command or []))


def _patchops_227_write_report(result, requested_outer_report_path):
    from pathlib import Path as _Path

    inner_report_path = _Path(result.inner_report_path).resolve() if result.inner_report_path else None
    requested_path = _Path(requested_outer_report_path).resolve() if requested_outer_report_path else None

    original_inner_text = ""
    if inner_report_path and inner_report_path.exists():
        original_inner_text = inner_report_path.read_text(encoding="utf-8", errors="replace")

    if inner_report_path:
        path = inner_report_path
        if requested_path and requested_path != path and requested_path.exists():
            try:
                requested_path.unlink()
            except OSError:
                pass
        canonical_title = "PATCHOPS RUN-PACKAGE CANONICAL REPORT"
        secondary_title = "PATCHOPS RUN-PACKAGE OUTER REPORT"
        if "Canonical run-package context merged into inner report; no separate outer report artifact was kept." not in result.notes:
            result.notes.append("Canonical run-package context merged into inner report; no separate outer report artifact was kept.")
    else:
        path = requested_path or (_Path(result.outer_report_path).resolve() if result.outer_report_path else _Path.cwd() / f"patchops_run_package_{_utc_stamp()}.txt")
        canonical_title = "PATCHOPS RUN-PACKAGE OUTER REPORT"
        secondary_title = ""

    path.parent.mkdir(parents=True, exist_ok=True)

    inner_found = bool(inner_report_path)
    result.failure_category = _patchops_227c_normalize_failure_category(result.failure_category)
    result.inner_failure_category = _patchops_227c_normalize_failure_category(result.inner_failure_category)

    inner_failed = False
    if inner_found:
        try:
            inner_failed = result.inner_exit_code is not None and int(result.inner_exit_code) != 0
        except Exception:
            inner_failed = False
        if str(result.inner_result or "").upper() == "FAIL":
            inner_failed = True

    mismatch_note = "Inner report summary reported FAIL even though launcher exit code was 0."
    if inner_failed and mismatch_note not in result.notes:
        result.notes.append(mismatch_note)

    result_label = "PASS" if result.ok else "FAIL"

    lines = [
        canonical_title,
        "=" * max(len(canonical_title), 32),
        f"Canonical Report Path: {path}",
    ]
    if secondary_title:
        lines.extend([secondary_title, "-" * len(secondary_title)])

    lines.extend(
        [
            f"Result              : {result_label}",
            f"Result               : {result_label}",
            f"Failure Category    : {_patchops_227c_display_category(result.failure_category)}",
            f"Source Path         : {result.source_path}",
            f"Source Kind         : {result.source_kind}",
            f"Extracted Path      : {result.extracted_path or '(not applicable)'}",
            f"Bundle Root         : {result.bundle_root}",
            f"Launcher Path       : {result.launcher_path}",
            f"Launcher Cwd        : {result.launcher_working_directory}",
            f"Inner Report Path   : {result.inner_report_path or '(not detected)'}",
            f"Inner Result        : {result.inner_result or '(not detected)'}",
            f"Inner Exit Code     : {result.inner_exit_code if result.inner_exit_code is not None else '(not detected)'}",
            f"Inner Failure       : {_patchops_227c_display_category(result.inner_failure_category)}",
            f"Outer Report Path   : {path}",
            f"Exit Code           : {result.exit_code}",
            "",
            "COMMAND",
            "-------",
            _patchops_227c_command_text(result.launcher_command),
            "",
            "STDOUT",
            "------",
            result.stdout or "(empty)",
            "",
            "STDERR",
            "------",
            result.stderr or "(empty)",
            "",
            "NOTES",
            "-----",
        ]
    )

    if result.notes:
        lines.extend(f"- {note}" for note in result.notes)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "SUMMARY",
            "-------",
            f"Ok                 : {result.ok}",
            f"FailureCategory    : {_patchops_227c_display_category(result.failure_category)}",
            f"InnerReportFound   : {inner_found}",
        ]
    )

    if original_inner_text:
        lines.extend(
            [
                "",
                "INNER REPORT",
                "------------",
                original_inner_text.rstrip(),
            ]
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result.outer_report_path = str(path)
    return path
# PATCHOPS_227C_FINAL_CANONICAL_REPORT_CONTRACT_REPAIR_END

# PATCHOPS_227D_CANONICAL_REPORT_PATH_ALIAS_REPAIR_START
def _patchops_227d_normalize_failure_category(category):
    text = str(category or "").strip()
    if text in {"none", "(none)"}:
        return ""
    if text == "target_project_failure":
        return "target_content_failure"
    return text


def _patchops_227d_display_category(category):
    return _patchops_227d_normalize_failure_category(category) or "(none)"


def _patchops_227d_command_text(command):
    quote = globals().get("_quote_command")
    if callable(quote):
        try:
            return quote(command)
        except Exception:
            pass
    return " ".join(str(item) for item in (command or []))


def _patchops_227_write_report(result, requested_outer_report_path):
    from pathlib import Path as _Path

    inner_report_path = _Path(result.inner_report_path).resolve() if result.inner_report_path else None
    requested_path = _Path(requested_outer_report_path).resolve() if requested_outer_report_path else None

    original_inner_text = ""
    if inner_report_path and inner_report_path.exists():
        original_inner_text = inner_report_path.read_text(encoding="utf-8", errors="replace")

    if inner_report_path:
        path = inner_report_path
        if requested_path and requested_path != path and requested_path.exists():
            try:
                requested_path.unlink()
            except OSError:
                pass
        canonical_title = "PATCHOPS RUN-PACKAGE CANONICAL REPORT"
        secondary_title = "PATCHOPS RUN-PACKAGE OUTER REPORT"
        if "Canonical run-package context merged into inner report; no separate outer report artifact was kept." not in result.notes:
            result.notes.append("Canonical run-package context merged into inner report; no separate outer report artifact was kept.")
    else:
        path = requested_path or (_Path(result.outer_report_path).resolve() if result.outer_report_path else _Path.cwd() / f"patchops_run_package_{_utc_stamp()}.txt")
        canonical_title = "PATCHOPS RUN-PACKAGE OUTER REPORT"
        secondary_title = ""

    path.parent.mkdir(parents=True, exist_ok=True)

    inner_found = bool(inner_report_path)
    result.failure_category = _patchops_227d_normalize_failure_category(result.failure_category)
    result.inner_failure_category = _patchops_227d_normalize_failure_category(result.inner_failure_category)

    inner_failed = False
    if inner_found:
        try:
            inner_failed = result.inner_exit_code is not None and int(result.inner_exit_code) != 0
        except Exception:
            inner_failed = False
        if str(result.inner_result or "").upper() == "FAIL":
            inner_failed = True

    mismatch_note = "Inner report summary reported FAIL even though launcher exit code was 0."
    if inner_failed and mismatch_note not in result.notes:
        result.notes.append(mismatch_note)

    result_label = "PASS" if result.ok else "FAIL"
    requested_display = str(requested_path) if requested_path else "(not requested)"
    inner_display = str(inner_report_path) if inner_report_path else "(not detected)"

    lines = [
        canonical_title,
        "=" * max(len(canonical_title), 32),
        f"Canonical Report Path: {path}",
        f"Requested Outer Path : {requested_display}",
        f"Inner Report Path    : {inner_display}",
    ]
    if secondary_title:
        lines.extend([secondary_title, "-" * len(secondary_title)])

    lines.extend(
        [
            f"Result              : {result_label}",
            f"Result               : {result_label}",
            f"Failure Category    : {_patchops_227d_display_category(result.failure_category)}",
            f"Source Path         : {result.source_path}",
            f"Source Kind         : {result.source_kind}",
            f"Extracted Path      : {result.extracted_path or '(not applicable)'}",
            f"Bundle Root         : {result.bundle_root}",
            f"Launcher Path       : {result.launcher_path}",
            f"Launcher Cwd        : {result.launcher_working_directory}",
            f"Inner Report Path   : {result.inner_report_path or '(not detected)'}",
            f"Inner Result        : {result.inner_result or '(not detected)'}",
            f"Inner Exit Code     : {result.inner_exit_code if result.inner_exit_code is not None else '(not detected)'}",
            f"Inner Failure       : {_patchops_227d_display_category(result.inner_failure_category)}",
            f"Outer Report Path   : {path}",
            f"Exit Code           : {result.exit_code}",
            "",
            "COMMAND",
            "-------",
            _patchops_227d_command_text(result.launcher_command),
            "",
            "STDOUT",
            "------",
            result.stdout or "(empty)",
            "",
            "STDERR",
            "------",
            result.stderr or "(empty)",
            "",
            "NOTES",
            "-----",
        ]
    )

    if result.notes:
        lines.extend(f"- {note}" for note in result.notes)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "SUMMARY",
            "-------",
            f"Ok                 : {result.ok}",
            f"FailureCategory    : {_patchops_227d_display_category(result.failure_category)}",
            f"InnerReportFound   : {inner_found}",
        ]
    )

    if original_inner_text:
        lines.extend(
            [
                "",
                "INNER REPORT",
                "------------",
                original_inner_text.rstrip(),
            ]
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result.outer_report_path = str(path)
    return path
# PATCHOPS_227D_CANONICAL_REPORT_PATH_ALIAS_REPAIR_END

# PATCHOPS_227E_CANONICAL_REPORT_SPACING_ALIAS_REPAIR_START
def _patchops_227e_normalize_failure_category(category):
    text = str(category or "").strip()
    if text in {"none", "(none)"}:
        return ""
    if text == "target_project_failure":
        return "target_content_failure"
    return text


def _patchops_227e_display_category(category):
    return _patchops_227e_normalize_failure_category(category) or "(none)"


def _patchops_227e_command_text(command):
    quote = globals().get("_quote_command")
    if callable(quote):
        try:
            return quote(command)
        except Exception:
            pass
    return " ".join(str(item) for item in (command or []))


def _patchops_227_write_report(result, requested_outer_report_path):
    from pathlib import Path as _Path

    inner_report_path = _Path(result.inner_report_path).resolve() if result.inner_report_path else None
    requested_path = _Path(requested_outer_report_path).resolve() if requested_outer_report_path else None

    original_inner_text = ""
    if inner_report_path and inner_report_path.exists():
        original_inner_text = inner_report_path.read_text(encoding="utf-8", errors="replace")

    if inner_report_path:
        path = inner_report_path
        if requested_path and requested_path != path and requested_path.exists():
            try:
                requested_path.unlink()
            except OSError:
                pass
        canonical_title = "PATCHOPS RUN-PACKAGE CANONICAL REPORT"
        secondary_title = "PATCHOPS RUN-PACKAGE OUTER REPORT"
        if "Canonical run-package context merged into inner report; no separate outer report artifact was kept." not in result.notes:
            result.notes.append("Canonical run-package context merged into inner report; no separate outer report artifact was kept.")
    else:
        path = requested_path or (_Path(result.outer_report_path).resolve() if result.outer_report_path else _Path.cwd() / f"patchops_run_package_{_utc_stamp()}.txt")
        canonical_title = "PATCHOPS RUN-PACKAGE OUTER REPORT"
        secondary_title = ""

    path.parent.mkdir(parents=True, exist_ok=True)

    inner_found = bool(inner_report_path)
    result.failure_category = _patchops_227e_normalize_failure_category(result.failure_category)
    result.inner_failure_category = _patchops_227e_normalize_failure_category(result.inner_failure_category)

    inner_failed = False
    if inner_found:
        try:
            inner_failed = result.inner_exit_code is not None and int(result.inner_exit_code) != 0
        except Exception:
            inner_failed = False
        if str(result.inner_result or "").upper() == "FAIL":
            inner_failed = True

    mismatch_note = "Inner report summary reported FAIL even though launcher exit code was 0."
    if inner_failed and mismatch_note not in result.notes:
        result.notes.append(mismatch_note)

    result_label = "PASS" if result.ok else "FAIL"
    requested_display = str(requested_path) if requested_path else "(not requested)"
    inner_display = str(inner_report_path) if inner_report_path else "(not detected)"
    inner_result_display = result.inner_result or "(not detected)"
    category_display = _patchops_227e_display_category(result.failure_category)

    lines = [
        canonical_title,
        "=" * max(len(canonical_title), 32),
        f"Canonical Report Path: {path}",
        f"Requested Outer Path : {requested_display}",
        f"Inner Report Path    : {inner_display}",
        f"Outer Report Path    : {path}",
    ]
    if secondary_title:
        lines.extend([secondary_title, "-" * len(secondary_title)])

    lines.extend(
        [
            f"Result              : {result_label}",
            f"Result               : {result_label}",
            f"Failure Category    : {category_display}",
            f"Failure Category     : {category_display}",
            f"Source Path         : {result.source_path}",
            f"Source Kind         : {result.source_kind}",
            f"Extracted Path      : {result.extracted_path or '(not applicable)'}",
            f"Bundle Root         : {result.bundle_root}",
            f"Launcher Path       : {result.launcher_path}",
            f"Launcher Cwd        : {result.launcher_working_directory}",
            f"Inner Report Path   : {result.inner_report_path or '(not detected)'}",
            f"Inner Report Path    : {inner_display}",
            f"Inner Result        : {inner_result_display}",
            f"Inner Result         : {inner_result_display}",
            f"Inner Exit Code     : {result.inner_exit_code if result.inner_exit_code is not None else '(not detected)'}",
            f"Inner Failure       : {_patchops_227e_display_category(result.inner_failure_category)}",
            f"Outer Report Path   : {path}",
            f"Outer Report Path    : {path}",
            f"Exit Code           : {result.exit_code}",
            "",
            "COMMAND",
            "-------",
            _patchops_227e_command_text(result.launcher_command),
            "",
            "STDOUT",
            "------",
            result.stdout or "(empty)",
            "",
            "STDERR",
            "------",
            result.stderr or "(empty)",
            "",
            "NOTES",
            "-----",
        ]
    )

    if result.notes:
        lines.extend(f"- {note}" for note in result.notes)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "SUMMARY",
            "-------",
            f"Ok                 : {result.ok}",
            f"FailureCategory    : {category_display}",
            f"InnerReportFound   : {inner_found}",
        ]
    )

    if original_inner_text:
        lines.extend(
            [
                "",
                "INNER REPORT",
                "------------",
                original_inner_text.rstrip(),
            ]
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result.outer_report_path = str(path)
    return path
# PATCHOPS_227E_CANONICAL_REPORT_SPACING_ALIAS_REPAIR_END

# PATCHOPS_227F_INNER_EXIT_CODE_ALIAS_REPAIR_START
def _patchops_227f_normalize_failure_category(category):
    text = str(category or "").strip()
    if text in {"none", "(none)"}:
        return ""
    if text == "target_project_failure":
        return "target_content_failure"
    return text


def _patchops_227f_display_category(category):
    return _patchops_227f_normalize_failure_category(category) or "(none)"


def _patchops_227f_command_text(command):
    quote = globals().get("_quote_command")
    if callable(quote):
        try:
            return quote(command)
        except Exception:
            pass
    return " ".join(str(item) for item in (command or []))


def _patchops_227_write_report(result, requested_outer_report_path):
    from pathlib import Path as _Path

    inner_report_path = _Path(result.inner_report_path).resolve() if result.inner_report_path else None
    requested_path = _Path(requested_outer_report_path).resolve() if requested_outer_report_path else None

    original_inner_text = ""
    if inner_report_path and inner_report_path.exists():
        original_inner_text = inner_report_path.read_text(encoding="utf-8", errors="replace")

    if inner_report_path:
        path = inner_report_path
        if requested_path and requested_path != path and requested_path.exists():
            try:
                requested_path.unlink()
            except OSError:
                pass
        canonical_title = "PATCHOPS RUN-PACKAGE CANONICAL REPORT"
        secondary_title = "PATCHOPS RUN-PACKAGE OUTER REPORT"
        if "Canonical run-package context merged into inner report; no separate outer report artifact was kept." not in result.notes:
            result.notes.append("Canonical run-package context merged into inner report; no separate outer report artifact was kept.")
    else:
        path = requested_path or (_Path(result.outer_report_path).resolve() if result.outer_report_path else _Path.cwd() / f"patchops_run_package_{_utc_stamp()}.txt")
        canonical_title = "PATCHOPS RUN-PACKAGE OUTER REPORT"
        secondary_title = ""

    path.parent.mkdir(parents=True, exist_ok=True)

    inner_found = bool(inner_report_path)
    result.failure_category = _patchops_227f_normalize_failure_category(result.failure_category)
    result.inner_failure_category = _patchops_227f_normalize_failure_category(result.inner_failure_category)

    inner_failed = False
    if inner_found:
        try:
            inner_failed = result.inner_exit_code is not None and int(result.inner_exit_code) != 0
        except Exception:
            inner_failed = False
        if str(result.inner_result or "").upper() == "FAIL":
            inner_failed = True

    mismatch_note = "Inner report summary reported FAIL even though launcher exit code was 0."
    if inner_failed and mismatch_note not in result.notes:
        result.notes.append(mismatch_note)

    result_label = "PASS" if result.ok else "FAIL"
    requested_display = str(requested_path) if requested_path else "(not requested)"
    inner_display = str(inner_report_path) if inner_report_path else "(not detected)"
    inner_result_display = result.inner_result or "(not detected)"
    inner_exit_display = result.inner_exit_code if result.inner_exit_code is not None else "(not detected)"
    category_display = _patchops_227f_display_category(result.failure_category)

    lines = [
        canonical_title,
        "=" * max(len(canonical_title), 32),
        f"Canonical Report Path: {path}",
        f"Requested Outer Path : {requested_display}",
        f"Inner Report Path    : {inner_display}",
        f"Outer Report Path    : {path}",
    ]
    if secondary_title:
        lines.extend([secondary_title, "-" * len(secondary_title)])

    lines.extend(
        [
            f"Result              : {result_label}",
            f"Result               : {result_label}",
            f"Failure Category    : {category_display}",
            f"Failure Category     : {category_display}",
            f"Source Path         : {result.source_path}",
            f"Source Kind         : {result.source_kind}",
            f"Extracted Path      : {result.extracted_path or '(not applicable)'}",
            f"Bundle Root         : {result.bundle_root}",
            f"Launcher Path       : {result.launcher_path}",
            f"Launcher Cwd        : {result.launcher_working_directory}",
            f"Inner Report Path   : {result.inner_report_path or '(not detected)'}",
            f"Inner Report Path    : {inner_display}",
            f"Inner Result        : {inner_result_display}",
            f"Inner Result         : {inner_result_display}",
            f"Inner Exit Code     : {inner_exit_display}",
            f"Inner Exit Code      : {inner_exit_display}",
            f"Inner Failure       : {_patchops_227f_display_category(result.inner_failure_category)}",
            f"Outer Report Path   : {path}",
            f"Outer Report Path    : {path}",
            f"Exit Code           : {result.exit_code}",
            "",
            "COMMAND",
            "-------",
            _patchops_227f_command_text(result.launcher_command),
            "",
            "STDOUT",
            "------",
            result.stdout or "(empty)",
            "",
            "STDERR",
            "------",
            result.stderr or "(empty)",
            "",
            "NOTES",
            "-----",
        ]
    )

    if result.notes:
        lines.extend(f"- {note}" for note in result.notes)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "SUMMARY",
            "-------",
            f"Ok                 : {result.ok}",
            f"FailureCategory    : {category_display}",
            f"InnerReportFound   : {inner_found}",
        ]
    )

    if original_inner_text:
        lines.extend(
            [
                "",
                "INNER REPORT",
                "------------",
                original_inner_text.rstrip(),
            ]
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result.outer_report_path = str(path)
    return path
# PATCHOPS_227F_INNER_EXIT_CODE_ALIAS_REPAIR_END

# PATCHOPS_227H_FORCE_ACTIVE_INNER_FAILURE_ALIAS_REPAIR_START
def _patchops_227h_normalize_failure_category(category):
    text = str(category or "").strip()
    if text in {"none", "(none)"}:
        return ""
    if text == "target_project_failure":
        return "target_content_failure"
    return text


def _patchops_227h_display_category(category):
    return _patchops_227h_normalize_failure_category(category) or "(none)"


def _patchops_227h_command_text(command):
    quote = globals().get("_quote_command")
    if callable(quote):
        try:
            return quote(command)
        except Exception:
            pass
    return " ".join(str(item) for item in (command or []))


def _patchops_227_write_report(result, requested_outer_report_path):
    from pathlib import Path as _Path

    inner_report_path = _Path(result.inner_report_path).resolve() if result.inner_report_path else None
    requested_path = _Path(requested_outer_report_path).resolve() if requested_outer_report_path else None

    original_inner_text = ""
    if inner_report_path and inner_report_path.exists():
        original_inner_text = inner_report_path.read_text(encoding="utf-8", errors="replace")

    if inner_report_path:
        path = inner_report_path
        if requested_path and requested_path != path and requested_path.exists():
            try:
                requested_path.unlink()
            except OSError:
                pass
        canonical_title = "PATCHOPS RUN-PACKAGE CANONICAL REPORT"
        secondary_title = "PATCHOPS RUN-PACKAGE OUTER REPORT"
        if "Canonical run-package context merged into inner report; no separate outer report artifact was kept." not in result.notes:
            result.notes.append("Canonical run-package context merged into inner report; no separate outer report artifact was kept.")
    else:
        path = requested_path or (_Path(result.outer_report_path).resolve() if result.outer_report_path else _Path.cwd() / f"patchops_run_package_{_utc_stamp()}.txt")
        canonical_title = "PATCHOPS RUN-PACKAGE OUTER REPORT"
        secondary_title = ""

    path.parent.mkdir(parents=True, exist_ok=True)

    inner_found = bool(inner_report_path)
    result.failure_category = _patchops_227h_normalize_failure_category(result.failure_category)
    result.inner_failure_category = _patchops_227h_normalize_failure_category(result.inner_failure_category)

    inner_failed = False
    if inner_found:
        try:
            inner_failed = result.inner_exit_code is not None and int(result.inner_exit_code) != 0
        except Exception:
            inner_failed = False
        if str(result.inner_result or "").upper() == "FAIL":
            inner_failed = True

    mismatch_note = "Inner report summary reported FAIL even though launcher exit code was 0."
    if inner_failed and mismatch_note not in result.notes:
        result.notes.append(mismatch_note)

    result_label = "PASS" if result.ok else "FAIL"
    requested_display = str(requested_path) if requested_path else "(not requested)"
    inner_display = str(inner_report_path) if inner_report_path else "(not detected)"
    inner_result_display = result.inner_result or "(not detected)"
    inner_exit_display = result.inner_exit_code if result.inner_exit_code is not None else "(not detected)"
    category_display = _patchops_227h_display_category(result.failure_category)
    inner_failure_display = _patchops_227h_display_category(result.inner_failure_category)

    lines = [
        canonical_title,
        "=" * max(len(canonical_title), 32),
        f"Canonical Report Path: {path}",
        f"Requested Outer Path : {requested_display}",
        f"Inner Report Path    : {inner_display}",
        f"Outer Report Path    : {path}",
    ]
    if secondary_title:
        lines.extend([secondary_title, "-" * len(secondary_title)])

    lines.extend(
        [
            f"Result              : {result_label}",
            f"Result               : {result_label}",
            f"Failure Category    : {category_display}",
            f"Failure Category     : {category_display}",
            f"Source Path         : {result.source_path}",
            f"Source Kind         : {result.source_kind}",
            f"Extracted Path      : {result.extracted_path or '(not applicable)'}",
            f"Bundle Root         : {result.bundle_root}",
            f"Launcher Path       : {result.launcher_path}",
            f"Launcher Cwd        : {result.launcher_working_directory}",
            f"Inner Report Path   : {result.inner_report_path or '(not detected)'}",
            f"Inner Report Path    : {inner_display}",
            f"Inner Result        : {inner_result_display}",
            f"Inner Result         : {inner_result_display}",
            f"Inner Exit Code     : {inner_exit_display}",
            f"Inner Exit Code      : {inner_exit_display}",
            f"Inner Failure       : {inner_failure_display}",
            f"Inner Failure        : {inner_failure_display}",
            f"Outer Report Path   : {path}",
            f"Outer Report Path    : {path}",
            f"Exit Code           : {result.exit_code}",
            "",
            "COMMAND",
            "-------",
            _patchops_227h_command_text(result.launcher_command),
            "",
            "STDOUT",
            "------",
            result.stdout or "(empty)",
            "",
            "STDERR",
            "------",
            result.stderr or "(empty)",
            "",
            "NOTES",
            "-----",
        ]
    )

    if result.notes:
        lines.extend(f"- {note}" for note in result.notes)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "SUMMARY",
            "-------",
            f"Ok                 : {result.ok}",
            f"FailureCategory    : {category_display}",
            f"InnerReportFound   : {inner_found}",
        ]
    )

    if original_inner_text:
        lines.extend(
            [
                "",
                "INNER REPORT",
                "------------",
                original_inner_text.rstrip(),
            ]
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result.outer_report_path = str(path)
    return path
# PATCHOPS_227H_FORCE_ACTIVE_INNER_FAILURE_ALIAS_REPAIR_END

# PATCHOPS_229_FINAL_FULL_PYTEST_THREE_FAILURE_REPAIR_START
def _patchops_229_normalize_failure_category(category):
    text = str(category or "").strip()
    if text in {"none", "(none)"}:
        return ""
    if text == "target_project_failure":
        return "target_content_failure"
    return text


def _patchops_229_display_category(category):
    return _patchops_229_normalize_failure_category(category) or "(none)"


def _patchops_229_command_text(command):
    quote = globals().get("_quote_command")
    if callable(quote):
        try:
            return quote(command)
        except Exception:
            pass
    return " ".join(str(item) for item in (command or []))


def _patchops_229_launcher_started(result):
    command = getattr(result, "launcher_command", None)
    launcher_path = getattr(result, "launcher_path", None)
    return bool(command) and bool(launcher_path)


def _patchops_227_write_report(result, requested_outer_report_path):
    from pathlib import Path as _Path

    inner_report_path = _Path(result.inner_report_path).resolve() if result.inner_report_path else None
    requested_path = _Path(requested_outer_report_path).resolve() if requested_outer_report_path else None

    original_inner_text = ""
    if inner_report_path and inner_report_path.exists():
        original_inner_text = inner_report_path.read_text(encoding="utf-8", errors="replace")

    if inner_report_path:
        path = inner_report_path
        if requested_path and requested_path != path and requested_path.exists():
            try:
                requested_path.unlink()
            except OSError:
                pass
        canonical_title = "PATCHOPS RUN-PACKAGE CANONICAL REPORT"
        secondary_title = "PATCHOPS RUN-PACKAGE OUTER REPORT"
        if "Canonical run-package context merged into inner report; no separate outer report artifact was kept." not in result.notes:
            result.notes.append("Canonical run-package context merged into inner report; no separate outer report artifact was kept.")
    else:
        path = requested_path or (_Path(result.outer_report_path).resolve() if result.outer_report_path else _Path.cwd() / f"patchops_run_package_{_utc_stamp()}.txt")
        canonical_title = "PATCHOPS RUN-PACKAGE OUTER REPORT"
        secondary_title = ""

    path.parent.mkdir(parents=True, exist_ok=True)

    inner_found = bool(inner_report_path)
    result.failure_category = _patchops_229_normalize_failure_category(result.failure_category)
    result.inner_failure_category = _patchops_229_normalize_failure_category(result.inner_failure_category)

    if not _patchops_229_launcher_started(result):
        no_start_note = "Launcher invocation did not start."
        if no_start_note not in result.notes:
            result.notes.append(no_start_note)

    inner_failed = False
    if inner_found:
        try:
            inner_failed = result.inner_exit_code is not None and int(result.inner_exit_code) != 0
        except Exception:
            inner_failed = False
        if str(result.inner_result or "").upper() == "FAIL":
            inner_failed = True

    mismatch_note = "Inner report summary reported FAIL even though launcher exit code was 0."
    if inner_failed and mismatch_note not in result.notes:
        result.notes.append(mismatch_note)

    result_label = "PASS" if result.ok else "FAIL"
    requested_display = str(requested_path) if requested_path else "(not requested)"
    inner_display = str(inner_report_path) if inner_report_path else "(not detected)"
    inner_result_display = result.inner_result or "(not detected)"
    inner_exit_display = result.inner_exit_code if result.inner_exit_code is not None else "(not detected)"
    category_display = _patchops_229_display_category(result.failure_category)
    inner_failure_display = _patchops_229_display_category(result.inner_failure_category)

    lines = [
        canonical_title,
        "=" * max(len(canonical_title), 32),
        f"Canonical Report Path: {path}",
        f"Requested Outer Path : {requested_display}",
        f"Inner Report Path    : {inner_display}",
        f"Outer Report Path    : {path}",
    ]
    if secondary_title:
        lines.extend([secondary_title, "-" * len(secondary_title)])

    lines.extend(
        [
            f"Result              : {result_label}",
            f"Result               : {result_label}",
            f"Failure Category    : {category_display}",
            f"Failure Category     : {category_display}",
            f"Source Path         : {result.source_path}",
            f"Source Kind         : {result.source_kind}",
            f"Extracted Path      : {result.extracted_path or '(not applicable)'}",
            f"Bundle Root         : {result.bundle_root}",
            f"Launcher Path       : {result.launcher_path or '(not started)'}",
            f"Launcher Cwd        : {result.launcher_working_directory or '(not started)'}",
            f"Inner Report Path   : {result.inner_report_path or '(not detected)'}",
            f"Inner Report Path    : {inner_display}",
            f"Inner Result        : {inner_result_display}",
            f"Inner Result         : {inner_result_display}",
            f"Inner Exit Code     : {inner_exit_display}",
            f"Inner Exit Code      : {inner_exit_display}",
            f"Inner Failure       : {inner_failure_display}",
            f"Inner Failure        : {inner_failure_display}",
            f"Outer Report Path   : {path}",
            f"Outer Report Path    : {path}",
            f"Exit Code           : {result.exit_code}",
            "",
            "COMMAND",
            "-------",
            _patchops_229_command_text(result.launcher_command),
            "",
            "STDOUT",
            "------",
            result.stdout or "(empty)",
            "",
            "STDERR",
            "------",
            result.stderr or "(empty)",
            "",
            "NOTES",
            "-----",
        ]
    )

    if result.notes:
        lines.extend(f"- {note}" for note in result.notes)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "SUMMARY",
            "-------",
            f"Ok                 : {result.ok}",
            f"FailureCategory    : {category_display}",
            f"InnerReportFound   : {inner_found}",
        ]
    )

    if original_inner_text:
        lines.extend(
            [
                "",
                "INNER REPORT",
                "------------",
                original_inner_text.rstrip(),
            ]
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result.outer_report_path = str(path)
    return path
# PATCHOPS_229_FINAL_FULL_PYTEST_THREE_FAILURE_REPAIR_END

