from __future__ import annotations

import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from subprocess import CompletedProcess, run
from typing import Callable, Iterable, Sequence

from patchops.readiness import (
    MAINTENANCE_GATE_REGRESSION_TESTS,
    MAINTENANCE_GATE_SMOKE_TESTS,
    ReleaseReadinessSnapshot,
    build_release_readiness_snapshot,
    release_readiness_exit_code,
    render_release_readiness_scope_lines,
)


@dataclass(frozen=True)
class MaintenanceGateCommandResult:
    name: str
    ok: bool
    exit_code: int
    command: tuple[str, ...]
    cwd: str
    stdout: str
    stderr: str
    test_paths: tuple[str, ...]


@dataclass(frozen=True)
class MaintenanceGateSnapshot:
    status: str
    core_tests_state: str
    regression_gate: MaintenanceGateCommandResult
    smoke_gate: MaintenanceGateCommandResult
    release_readiness: ReleaseReadinessSnapshot
    issues: tuple[str, ...]


def run_pytest_paths(
    *,
    wrapper_project_root: str | Path,
    test_paths: Sequence[str],
    name: str,
    python_executable: str | None = None,
) -> MaintenanceGateCommandResult:
    root = Path(wrapper_project_root).resolve()
    executable = python_executable or sys.executable
    command = (str(executable), "-m", "pytest", "-q", *tuple(str(item) for item in test_paths))
    completed: CompletedProcess[str] = run(
        command,
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    return MaintenanceGateCommandResult(
        name=name,
        ok=completed.returncode == 0,
        exit_code=int(completed.returncode),
        command=tuple(str(part) for part in command),
        cwd=str(root),
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
        test_paths=tuple(str(item) for item in test_paths),
    )


def _normalize_core_tests_state(core_tests_state: str) -> str:
    normalized = str(core_tests_state or "unknown").strip().lower()
    if normalized not in {"green", "unknown", "not_green"}:
        raise ValueError(
            "core_tests_state must be one of 'green', 'unknown', or 'not_green'."
        )
    return normalized


def build_maintenance_gate_snapshot(
    wrapper_project_root: str | Path,
    *,
    available_profiles: Iterable[str],
    core_tests_state: str = "unknown",
    python_executable: str | None = None,
    command_runner: Callable[..., MaintenanceGateCommandResult] = run_pytest_paths,
) -> MaintenanceGateSnapshot:
    normalized_core_tests_state = _normalize_core_tests_state(core_tests_state)
    wrapper_root = Path(wrapper_project_root).resolve()

    regression_gate = command_runner(
        wrapper_project_root=wrapper_root,
        test_paths=MAINTENANCE_GATE_REGRESSION_TESTS,
        name="bundle_manifest_regression_gate",
        python_executable=python_executable,
    )
    smoke_gate = command_runner(
        wrapper_project_root=wrapper_root,
        test_paths=MAINTENANCE_GATE_SMOKE_TESTS,
        name="bundle_post_build_smoke_gate",
        python_executable=python_executable,
    )

    release_readiness = build_release_readiness_snapshot(
        wrapper_root,
        available_profiles=available_profiles,
        core_tests_state=normalized_core_tests_state,
    )

    issues: list[str] = []
    if not regression_gate.ok:
        issues.append("bundle/manifest regression gate failed")
    if not smoke_gate.ok:
        issues.append("post-build bundle smoke gate failed")
    issues.extend(str(item) for item in release_readiness.issues)

    if not regression_gate.ok or not smoke_gate.ok or release_readiness_exit_code(release_readiness) != 0:
        status = "not_ready"
    elif release_readiness.status == "review_required":
        status = "review_required"
    else:
        status = "green"

    return MaintenanceGateSnapshot(
        status=status,
        core_tests_state=normalized_core_tests_state,
        regression_gate=regression_gate,
        smoke_gate=smoke_gate,
        release_readiness=release_readiness,
        issues=tuple(issues),
    )


def render_maintenance_gate_scope_lines(snapshot: MaintenanceGateSnapshot) -> tuple[str, ...]:
    return (
        "Surface          : maintenance-gate",
        f"Status           : {snapshot.status}",
        f"CoreTests        : {snapshot.core_tests_state}",
        f"RegressionGate   : {'ok' if snapshot.regression_gate.ok else 'failed'}",
        f"SmokeGate        : {'ok' if snapshot.smoke_gate.ok else 'failed'}",
        f"ReleaseReadiness : {snapshot.release_readiness.status}",
        f"Issues           : {len(snapshot.issues)}",
    )


def maintenance_gate_as_dict(snapshot: MaintenanceGateSnapshot) -> dict[str, object]:
    payload = asdict(snapshot)
    payload["scope_lines"] = list(render_maintenance_gate_scope_lines(snapshot))
    payload["release_readiness_scope_lines"] = list(
        render_release_readiness_scope_lines(snapshot.release_readiness)
    )
    return payload


def _items_or_none(items: Sequence[str]) -> tuple[str, ...]:
    return tuple(items) if items else ("(none)",)


def _command_section_lines(result: MaintenanceGateCommandResult) -> tuple[str, ...]:
    lines = [
        result.name.upper(),
        "-" * len(result.name),
        f"Status            : {'ok' if result.ok else 'failed'}",
        f"Exit Code         : {result.exit_code}",
        f"Working Directory : {result.cwd}",
        f"Command           : {' '.join(result.command)}",
        "Test Paths",
        "----------",
        *_items_or_none(result.test_paths),
        "",
        "STDOUT",
        "------",
        *(result.stdout.splitlines() or ["(none)"]),
        "",
        "STDERR",
        "------",
        *(result.stderr.splitlines() or ["(none)"]),
    ]
    return tuple(lines)


def render_maintenance_gate_report_lines(
    snapshot: MaintenanceGateSnapshot,
    *,
    wrapper_project_root: str | Path,
    focused_profile: str | None = None,
) -> tuple[str, ...]:
    wrapper_root = Path(wrapper_project_root).resolve()
    lines: list[str] = [
        "PATCHOPS MAINTENANCE GATE",
        "-------------------------",
        "Surface            : maintenance-gate",
        f"Wrapper Project    : {wrapper_root}",
        f"Focused Profile    : {focused_profile or '(none)'}",
        f"Status             : {snapshot.status}",
        f"Core Tests         : {snapshot.core_tests_state}",
        f"Regression Gate    : {'ok' if snapshot.regression_gate.ok else 'failed'}",
        f"Smoke Gate         : {'ok' if snapshot.smoke_gate.ok else 'failed'}",
        f"Release Readiness  : {snapshot.release_readiness.status}",
        f"Issues             : {len(snapshot.issues)}",
        "",
        "SUMMARY",
        "-------",
        *render_maintenance_gate_scope_lines(snapshot),
        "",
        "ISSUES",
        "------",
        *_items_or_none(snapshot.issues),
        "",
        *render_release_readiness_scope_lines(snapshot.release_readiness),
        "",
        *_command_section_lines(snapshot.regression_gate),
        "",
        *_command_section_lines(snapshot.smoke_gate),
    ]
    return tuple(lines)


def write_maintenance_gate_report(
    report_path: str | Path,
    snapshot: MaintenanceGateSnapshot,
    *,
    wrapper_project_root: str | Path,
    focused_profile: str | None = None,
) -> str:
    path = Path(report_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(
        render_maintenance_gate_report_lines(
            snapshot,
            wrapper_project_root=wrapper_project_root,
            focused_profile=focused_profile,
        )
    ) + "\n"
    path.write_text(text, encoding="utf-8")
    return str(path)
