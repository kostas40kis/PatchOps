from __future__ import annotations

import json
from pathlib import Path

from patchops.maintenance_gate import (
    MaintenanceGateCommandResult,
    build_maintenance_gate_snapshot,
    render_maintenance_gate_report_lines,
    write_maintenance_gate_report,
)
from patchops.cli import main
from patchops.readiness import (
    REQUIRED_BUNDLE_RELEASE_DOCS,
    REQUIRED_BUNDLE_RELEASE_TESTS,
    REQUIRED_BUNDLE_RELEASE_WORKFLOWS,
    REQUIRED_RELEASE_DOCS,
    REQUIRED_RELEASE_EXAMPLES,
    REQUIRED_RELEASE_LAUNCHERS,
    REQUIRED_RELEASE_TESTS,
    REQUIRED_RELEASE_WORKFLOWS,
)


def _write_file(repo_root: Path, relative_path: str, content: str = "x\n") -> None:
    path = repo_root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_release_ready_repo(repo_root: Path) -> None:
    for relative_path in (
        *REQUIRED_RELEASE_DOCS,
        *REQUIRED_RELEASE_EXAMPLES,
        *REQUIRED_RELEASE_WORKFLOWS,
        *REQUIRED_RELEASE_LAUNCHERS,
        *REQUIRED_RELEASE_TESTS,
        *REQUIRED_BUNDLE_RELEASE_DOCS,
        *REQUIRED_BUNDLE_RELEASE_WORKFLOWS,
        *REQUIRED_BUNDLE_RELEASE_TESTS,
    ):
        _write_file(repo_root, relative_path)


def _fake_runner_factory(*, regression_ok: bool = True, smoke_ok: bool = True):
    def _runner(
        *,
        wrapper_project_root: str | Path,
        test_paths,
        name: str,
        python_executable: str | None = None,
    ) -> MaintenanceGateCommandResult:
        ok = regression_ok if name == "bundle_manifest_regression_gate" else smoke_ok
        return MaintenanceGateCommandResult(
            name=name,
            ok=ok,
            exit_code=0 if ok else 1,
            command=(str(python_executable or "python"), "-m", "pytest", "-q", *tuple(test_paths)),
            cwd=str(Path(wrapper_project_root).resolve()),
            stdout="ok\n" if ok else "failed\n",
            stderr="",
            test_paths=tuple(test_paths),
        )

    return _runner


def test_maintenance_gate_snapshot_is_green_when_all_subgates_are_green(tmp_path: Path) -> None:
    _seed_release_ready_repo(tmp_path)

    snapshot = build_maintenance_gate_snapshot(
        tmp_path,
        available_profiles=("trader", "generic_python", "generic_python_powershell"),
        core_tests_state="green",
        command_runner=_fake_runner_factory(),
    )

    assert snapshot.status == "green"
    assert snapshot.regression_gate.ok is True
    assert snapshot.smoke_gate.ok is True
    assert snapshot.release_readiness.status == "green"


def test_maintenance_gate_snapshot_reports_review_required_when_core_tests_are_unknown(tmp_path: Path) -> None:
    _seed_release_ready_repo(tmp_path)

    snapshot = build_maintenance_gate_snapshot(
        tmp_path,
        available_profiles=("trader", "generic_python", "generic_python_powershell"),
        core_tests_state="unknown",
        command_runner=_fake_runner_factory(),
    )

    assert snapshot.status == "review_required"
    assert snapshot.release_readiness.status == "review_required"
    assert "core test state not provided" in snapshot.issues


def test_maintenance_gate_snapshot_fails_cleanly_when_regression_gate_fails(tmp_path: Path) -> None:
    _seed_release_ready_repo(tmp_path)

    snapshot = build_maintenance_gate_snapshot(
        tmp_path,
        available_profiles=("trader", "generic_python", "generic_python_powershell"),
        core_tests_state="green",
        command_runner=_fake_runner_factory(regression_ok=False),
    )

    assert snapshot.status == "not_ready"
    assert snapshot.regression_gate.ok is False
    assert "bundle/manifest regression gate failed" in snapshot.issues


def test_maintenance_gate_can_write_deterministic_report_artifact(tmp_path: Path) -> None:
    _seed_release_ready_repo(tmp_path)
    snapshot = build_maintenance_gate_snapshot(
        tmp_path,
        available_profiles=("trader", "generic_python", "generic_python_powershell"),
        core_tests_state="green",
        command_runner=_fake_runner_factory(),
    )
    report_path = tmp_path / "evidence" / "maintenance_gate.txt"

    written = write_maintenance_gate_report(
        report_path,
        snapshot,
        wrapper_project_root=tmp_path,
        focused_profile="trader",
    )
    report_text = Path(written).read_text(encoding="utf-8")

    assert written == str(report_path.resolve())
    assert report_text.startswith("PATCHOPS MAINTENANCE GATE\n")
    assert f"Wrapper Project    : {tmp_path.resolve()}" in report_text
    assert "Focused Profile    : trader" in report_text
    assert "Release Readiness  : green" in report_text
    assert "BUNDLE_MANIFEST_REGRESSION_GATE" in report_text
    assert "BUNDLE_POST_BUILD_SMOKE_GATE" in report_text


def test_maintenance_gate_doc_mentions_combined_gate_and_existing_surfaces() -> None:
    text = Path("docs/maintenance_gate.md").read_text(encoding="utf-8")
    required = [
        "maintenance-gate",
        "bundle and manifest regression gate",
        "post-build bundle smoke gate",
        "release-readiness",
        "continue patch by patch from evidence",
    ]
    for phrase in required:
        assert phrase in text
