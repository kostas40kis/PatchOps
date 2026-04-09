from __future__ import annotations

from pathlib import Path

from patchops.bundles.authoring import create_starter_bundle, run_bundle_execution_entry


def test_bundle_execution_entry_runs_apply_sequence_from_metadata(tmp_path: Path) -> None:
    result = create_starter_bundle(
        tmp_path / "apply_bundle",
        patch_name="entry_apply_bundle",
        target_project="patchops",
        target_project_root=r"C:\dev\patchops",
        mode="apply",
    )

    observed: list[list[str]] = []

    def runner(argv: list[str]) -> int:
        observed.append(list(argv))
        return 0

    entry = run_bundle_execution_entry(result.bundle_root, wrapper_root=r"C:\dev\patchops", command_runner=runner)

    assert entry.exit_code == 0
    assert entry.workflow_mode == "apply"
    assert entry.executed_command_count == 5
    assert observed == [
        ["check-bundle", str(result.bundle_root.resolve())],
        ["check", str(result.manifest_path.resolve())],
        ["inspect", str(result.manifest_path.resolve())],
        ["plan", str(result.manifest_path.resolve())],
        ["apply", str(result.manifest_path.resolve()), "--wrapper-root", str(Path(r"C:\dev\patchops").resolve())],
    ]


def test_bundle_execution_entry_runs_verify_sequence_from_metadata(tmp_path: Path) -> None:
    result = create_starter_bundle(
        tmp_path / "verify_bundle",
        patch_name="entry_verify_bundle",
        target_project="patchops",
        target_project_root=r"C:\dev\patchops",
        mode="verify",
    )

    observed: list[list[str]] = []

    def runner(argv: list[str]) -> int:
        observed.append(list(argv))
        return 0

    entry = run_bundle_execution_entry(result.bundle_root, wrapper_root=r"C:\dev\patchops", command_runner=runner)

    assert entry.exit_code == 0
    assert entry.workflow_mode == "verify"
    assert entry.executed_command_count == 5
    assert observed[-1][0] == "verify"
    assert observed[-1][1] == str(result.manifest_path.resolve())


def test_bundle_execution_entry_stops_after_the_first_failing_layer(tmp_path: Path) -> None:
    result = create_starter_bundle(
        tmp_path / "failing_bundle",
        patch_name="entry_fail_bundle",
        target_project="patchops",
        target_project_root=r"C:\dev\patchops",
        mode="apply",
    )

    observed: list[list[str]] = []

    def runner(argv: list[str]) -> int:
        observed.append(list(argv))
        return 1 if argv[0] == "inspect" else 0

    entry = run_bundle_execution_entry(result.bundle_root, command_runner=runner)

    assert entry.exit_code == 1
    assert entry.executed_command_count == 3
    assert observed == [
        ["check-bundle", str(result.bundle_root.resolve())],
        ["check", str(result.manifest_path.resolve())],
        ["inspect", str(result.manifest_path.resolve())],
    ]
