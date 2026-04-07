from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BundleApplyPaths:
    zip_path: Path
    extract_root: Path
    bundle_root: Path
    manifest_path: Path
    launcher_path: Path


def _top_level_roots(zip_file: zipfile.ZipFile) -> list[str]:
    roots: list[str] = []
    seen: set[str] = set()
    for name in zip_file.namelist():
        clean = name.replace('\\', '/').strip('/')
        if not clean:
            continue
        root = clean.split('/', 1)[0]
        if root and root not in seen:
            seen.add(root)
            roots.append(root)
    return roots


def _resolve_apply_paths(bundle_zip_path: str | Path, extract_root: str | Path | None = None) -> BundleApplyPaths:
    zip_path = Path(bundle_zip_path).resolve()
    if not zip_path.exists():
        raise FileNotFoundError(f"Bundle zip does not exist: {zip_path}")
    if zip_path.is_dir():
        raise IsADirectoryError(f"Bundle zip path is a directory, not a file: {zip_path}")

    with zipfile.ZipFile(zip_path) as zf:
        roots = _top_level_roots(zf)
        if len(roots) != 1:
            raise ValueError(f"Bundle zip must contain exactly one top-level root. Found: {roots}")
        root_name = roots[0]
        target_extract_root = Path(extract_root).resolve() if extract_root is not None else Path(tempfile.mkdtemp(prefix='patchops_bundle_apply_')).resolve()
        zf.extractall(target_extract_root)

    bundle_root = target_extract_root / root_name
    manifest_path = bundle_root / 'manifest.json'
    launchers_root = bundle_root / 'launchers'
    preferred_launchers = [
        launchers_root / 'apply_with_patchops.ps1',
        launchers_root / 'apply.ps1',
    ]
    launcher_path = next((candidate for candidate in preferred_launchers if candidate.exists()), None)
    if launcher_path is None and launchers_root.exists():
        ps1_files = sorted(launchers_root.glob('*.ps1'))
        if ps1_files:
            launcher_path = ps1_files[0]
    if launcher_path is None:
        raise FileNotFoundError(f"Apply launcher was not found under: {launchers_root}")
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest was not found in extracted bundle root: {manifest_path}")

    return BundleApplyPaths(
        zip_path=zip_path,
        extract_root=target_extract_root,
        bundle_root=bundle_root,
        manifest_path=manifest_path,
        launcher_path=launcher_path,
    )


def _build_launcher_command(paths: BundleApplyPaths, wrapper_root: str | Path | None) -> list[str]:
    command = [
        'powershell',
        '-NoProfile',
        '-ExecutionPolicy',
        'Bypass',
        '-File',
        str(paths.launcher_path),
    ]
    if wrapper_root is not None:
        command.extend(['-WrapperRepoRoot', str(Path(wrapper_root).resolve())])
    return command


def _run_launcher_command(command: list[str], working_directory: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(working_directory),
        capture_output=True,
        text=True,
        check=False,
    )


def _extract_summary_value(text: str, label: str) -> str | None:
    pattern = re.compile(rf'^\s*{re.escape(label)}\s*:\s*(.+?)\s*$', re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None


def _build_report_chain(
    paths: BundleApplyPaths,
    completed: subprocess.CompletedProcess[str],
    wrapper_root: str | Path | None,
) -> dict[str, Any]:
    combined_output = completed.stdout
    if completed.stderr:
        combined_output = combined_output + ("\n" if combined_output else "") + completed.stderr

    report_path = _extract_summary_value(combined_output, 'Report Path')
    manifest_path_reported = (
        _extract_summary_value(combined_output, 'Manifest Path Used')
        or _extract_summary_value(combined_output, 'Manifest Path')
    )
    chain: dict[str, Any] = {
        'zip_path': str(paths.zip_path),
        'extract_root': str(paths.extract_root),
        'bundle_root': str(paths.bundle_root),
        'launcher_path': str(paths.launcher_path),
        'manifest_path': str(paths.manifest_path),
        'wrapper_root_passed': str(Path(wrapper_root).resolve()) if wrapper_root is not None else None,
        'wrapper_project_root_reported': _extract_summary_value(combined_output, 'Wrapper Project Root'),
        'target_project_root': _extract_summary_value(combined_output, 'Target Project Root'),
        'active_profile': _extract_summary_value(combined_output, 'Active Profile'),
        'manifest_path_reported': manifest_path_reported,
        'final_report_path': report_path,
        'related_inner_report_path': report_path,
        'launcher_stdout_present': bool(completed.stdout),
        'launcher_stderr_present': bool(completed.stderr),
    }
    return chain


def apply_bundle_path(
    bundle_zip_path: str | Path,
    *,
    wrapper_root: str | Path | None = None,
    extract_root: str | Path | None = None,
    keep_extract_root: bool = True,
) -> dict[str, Any]:
    paths = _resolve_apply_paths(bundle_zip_path, extract_root=extract_root)
    command = _build_launcher_command(paths, wrapper_root=wrapper_root)
    completed = _run_launcher_command(command, working_directory=paths.bundle_root)
    report_chain = _build_report_chain(paths, completed, wrapper_root=wrapper_root)

    payload = {
        'zip_path': str(paths.zip_path),
        'extract_root': str(paths.extract_root),
        'bundle_root': str(paths.bundle_root),
        'manifest_path': str(paths.manifest_path),
        'launcher_path': str(paths.launcher_path),
        'command': command,
        'working_directory': str(paths.bundle_root),
        'exit_code': int(completed.returncode),
        'stdout': completed.stdout,
        'stderr': completed.stderr,
        'ok': completed.returncode == 0,
        'final_report_path': report_chain['final_report_path'],
        'related_inner_report_path': report_chain['related_inner_report_path'],
        'report_chain': report_chain,
    }

    if not keep_extract_root:
        shutil.rmtree(paths.extract_root, ignore_errors=True)

    return payload