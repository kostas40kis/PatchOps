from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DependencyCheck:
    package: str
    import_name: str
    available_before: bool
    install_attempted: bool
    install_exit_code: int | None
    available_after: bool
    status: str
    stdout_tail: str
    stderr_tail: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RuntimeDependencyResult:
    status: str
    python_executable: str
    python_version: str
    checks: list[dict[str, Any]]
    created_at: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def import_available(import_name: str) -> bool:
    return importlib.util.find_spec(import_name) is not None


def _tail(text: str, limit: int = 4000) -> str:
    if not text:
        return ""
    return text[-limit:]


def install_package(package: str, *, timeout_seconds: int = 240) -> tuple[int, str, str]:
    proc = subprocess.run(
        [sys.executable, "-m", "pip", "install", package],
        text=True,
        capture_output=True,
        timeout=max(30, int(timeout_seconds)),
    )
    return int(proc.returncode), proc.stdout or "", proc.stderr or ""


def ensure_dependencies(
    *,
    packages: list[str] | None = None,
    allow_install: bool = False,
    timeout_seconds: int = 240,
) -> RuntimeDependencyResult:
    package_list = packages or ["pywinauto"]
    checks: list[DependencyCheck] = []
    for package in package_list:
        import_name = package.replace("-", "_")
        before = import_available(import_name)
        install_attempted = False
        install_exit_code: int | None = None
        stdout = ""
        stderr = ""
        if not before and allow_install:
            install_attempted = True
            try:
                install_exit_code, stdout, stderr = install_package(package, timeout_seconds=timeout_seconds)
            except subprocess.TimeoutExpired as exc:
                install_exit_code = -1
                stdout = exc.stdout or "" if isinstance(exc.stdout, str) else ""
                stderr = (exc.stderr or "" if isinstance(exc.stderr, str) else "") + "\nINSTALL_TIMEOUT"
            except Exception as exc:
                install_exit_code = -2
                stderr = f"INSTALL_EXCEPTION:{exc}"
        after = import_available(import_name)
        if after:
            status = "PASS_AVAILABLE"
        elif install_attempted:
            status = "BLOCKED_INSTALL_FAILED"
        else:
            status = "BLOCKED_MISSING_NOT_INSTALLED"
        checks.append(
            DependencyCheck(
                package=package,
                import_name=import_name,
                available_before=before,
                install_attempted=install_attempted,
                install_exit_code=install_exit_code,
                available_after=after,
                status=status,
                stdout_tail=_tail(stdout),
                stderr_tail=_tail(stderr),
            )
        )
    overall = "PASS" if all(item.available_after for item in checks) else "BLOCKED_DEPENDENCY_UNAVAILABLE"
    return RuntimeDependencyResult(
        status=overall,
        python_executable=sys.executable,
        python_version=sys.version.replace("\n", " "),
        checks=[item.to_payload() for item in checks],
        created_at=utc_now_iso(),
    )


def write_dependency_evidence(result: RuntimeDependencyResult, evidence_dir: str | Path, *, basename: str = "u2_04b_runtime_dependency") -> tuple[Path, Path]:
    root = Path(evidence_dir).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    safe_base = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in basename).strip("_") or "runtime_dependency"
    json_path = root / f"{safe_base}.json"
    txt_path = root / f"{safe_base}.txt"
    payload = result.to_payload()
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "PATCHOPS CHATGPT UPLOADER RUNTIME DEPENDENCIES",
        "================================================",
        f"Status           : {result.status}",
        f"PythonExecutable : {result.python_executable}",
        f"PythonVersion    : {result.python_version}",
    ]
    for check in result.checks:
        lines.extend(
            [
                "",
                f"Package          : {check.get('package')}",
                f"ImportName       : {check.get('import_name')}",
                f"AvailableBefore  : {str(check.get('available_before')).lower()}",
                f"InstallAttempted : {str(check.get('install_attempted')).lower()}",
                f"InstallExitCode  : {check.get('install_exit_code')}",
                f"AvailableAfter   : {str(check.get('available_after')).lower()}",
                f"CheckStatus      : {check.get('status')}",
            ]
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path
