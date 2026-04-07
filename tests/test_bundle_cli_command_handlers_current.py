from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from patchops.bundles.cli_commands import (
    run_apply_bundle_command,
    run_bundle_command,
    run_check_bundle_command,
    run_inspect_bundle_command,
    run_plan_bundle_command,
    run_verify_bundle_command,
)


def test_run_check_bundle_command_uses_nested_result_shape_and_serializes(monkeypatch, tmp_path: Path) -> None:
    metadata = SimpleNamespace(
        patch_name="patch_14_check",
        recommended_profile="generic_python",
    )
    extraction = SimpleNamespace(
        bundle_zip_path=tmp_path / "patch_14_check.zip",
        run_root=tmp_path / "workspace",
        bundle_root=tmp_path / "workspace" / "extracted_bundle",
    )
    validation = SimpleNamespace(
        errors=(SimpleNamespace(message="missing content root"),),
        warnings=(),
    )
    result = SimpleNamespace(
        is_valid=False,
        metadata=metadata,
        extraction=extraction,
        validation=validation,
    )
    calls: list[tuple[Path, Path, str | None]] = []

    def fake_check(bundle_zip_path, wrapper_project_root, *, timestamp_token=None):
        calls.append((Path(bundle_zip_path), Path(wrapper_project_root), timestamp_token))
        return result

    monkeypatch.setattr("patchops.bundles.cli_commands.check_bundle_zip", fake_check)

    payload = run_check_bundle_command(
        tmp_path / "patch_14_check.zip",
        tmp_path / "wrapper",
        timestamp_token="20260404_231800",
    )

    assert calls == [
        (
            tmp_path / "patch_14_check.zip",
            tmp_path / "wrapper",
            "20260404_231800",
        )
    ]
    assert payload["patch_name"] == "patch_14_check"
    assert payload["issue_count"] == 1
    assert payload["issues"] == ["missing content root"]


def test_run_inspect_and_plan_bundle_commands_serialize_nested_results(monkeypatch, tmp_path: Path) -> None:
    metadata = SimpleNamespace(
        patch_name="patch_14_inspect",
        recommended_profile="generic_python",
    )
    extraction = SimpleNamespace(
        bundle_zip_path=tmp_path / "patch_14_inspect.zip",
        run_root=tmp_path / "workspace",
        bundle_root=tmp_path / "workspace" / "extracted_bundle",
    )
    check_result = SimpleNamespace(
        metadata=metadata,
        extraction=extraction,
    )
    resolved_layout = SimpleNamespace(
        manifest_path=tmp_path / "workspace" / "extracted_bundle" / "manifest.json",
        content_root_path=tmp_path / "workspace" / "extracted_bundle" / "content",
    )
    inspect_result = SimpleNamespace(
        check=check_result,
        resolved_layout=resolved_layout,
        target_paths=("docs/example.md",),
        validation_command_names=("pytest",),
    )
    plan_result = SimpleNamespace(
        inspect=inspect_result,
        resolved_profile="generic_python",
        target_project_root=r"C:\dev\patchops",
        report_path_preview=tmp_path / "workspace" / "plan.txt",
        write_targets=("docs/example.md",),
        validation_command_names=("pytest",),
    )

    monkeypatch.setattr("patchops.bundles.cli_commands.inspect_bundle_zip", lambda *args, **kwargs: inspect_result)
    monkeypatch.setattr("patchops.bundles.cli_commands.plan_bundle_zip", lambda *args, **kwargs: plan_result)

    inspect_payload = run_inspect_bundle_command(tmp_path / "bundle.zip", tmp_path / "wrapper")
    plan_payload = run_plan_bundle_command(tmp_path / "bundle.zip", tmp_path / "wrapper")

    assert inspect_payload["patch_name"] == "patch_14_inspect"
    assert inspect_payload["write_targets"] == ["docs/example.md"]
    assert plan_payload["patch_name"] == "patch_14_inspect"
    assert plan_payload["target_project_root"] == r"C:\dev\patchops"
    assert plan_payload["validation_commands"][0]["name"] == "pytest"


def test_run_apply_and_verify_bundle_commands_serialize_nested_results(monkeypatch, tmp_path: Path) -> None:
    metadata = SimpleNamespace(
        patch_name="patch_14_apply",
        recommended_profile="generic_python",
    )
    extraction = SimpleNamespace(
        bundle_zip_path=tmp_path / "patch_14_apply.zip",
        run_root=tmp_path / "workspace",
        bundle_root=tmp_path / "workspace" / "extracted_bundle",
    )
    check_result = SimpleNamespace(
        metadata=metadata,
        extraction=extraction,
    )
    inspect_result = SimpleNamespace(check=check_result)
    plan_result = SimpleNamespace(inspect=inspect_result)
    apply_result = SimpleNamespace(
        plan=plan_result,
        prepared_manifest_path=tmp_path / "workspace" / "prepared_apply.json",
        workflow_result=SimpleNamespace(
            report_path=tmp_path / "reports" / "apply.txt",
            result_label="PASS",
            exit_code=0,
        ),
    )
    verify_result = SimpleNamespace(
        plan=plan_result,
        prepared_manifest_path=tmp_path / "workspace" / "prepared_verify.json",
        workflow_result=SimpleNamespace(
            report_path=tmp_path / "reports" / "verify.txt",
            result_label="PASS",
            exit_code=0,
        ),
    )

    monkeypatch.setattr("patchops.bundles.cli_commands.apply_bundle_zip", lambda *args, **kwargs: apply_result)
    monkeypatch.setattr("patchops.bundles.cli_commands.verify_bundle_zip", lambda *args, **kwargs: verify_result)

    apply_payload = run_apply_bundle_command(tmp_path / "bundle.zip", tmp_path / "wrapper")
    verify_payload = run_verify_bundle_command(tmp_path / "bundle.zip", tmp_path / "wrapper")

    assert apply_payload["patch_name"] == "patch_14_apply"
    assert apply_payload["report_path"].endswith("apply.txt")
    assert verify_payload["patch_name"] == "patch_14_apply"
    assert verify_payload["report_path"].endswith("verify.txt")


def test_run_bundle_command_dispatches_supported_names(monkeypatch, tmp_path: Path) -> None:
    def fake_runner(command_name: str):
        def _runner(bundle_zip_path, wrapper_project_root, *, timestamp_token=None):
            return {
                "command_name": command_name,
                "bundle_zip_path": str(bundle_zip_path),
                "wrapper_project_root": str(wrapper_project_root),
                "timestamp_token": timestamp_token,
            }
        return _runner

    monkeypatch.setattr("patchops.bundles.cli_commands.run_check_bundle_command", fake_runner("check-bundle"))
    monkeypatch.setattr("patchops.bundles.cli_commands.run_inspect_bundle_command", fake_runner("inspect-bundle"))
    monkeypatch.setattr("patchops.bundles.cli_commands.run_plan_bundle_command", fake_runner("plan-bundle"))
    monkeypatch.setattr("patchops.bundles.cli_commands.run_apply_bundle_command", fake_runner("apply-bundle"))
    monkeypatch.setattr("patchops.bundles.cli_commands.run_verify_bundle_command", fake_runner("verify-bundle"))

    from patchops.bundles import cli_commands as cli_commands_module

    cli_commands_module._BUNDLE_COMMAND_HANDLERS.update(
        {
            "check-bundle": cli_commands_module.run_check_bundle_command,
            "inspect-bundle": cli_commands_module.run_inspect_bundle_command,
            "plan-bundle": cli_commands_module.run_plan_bundle_command,
            "apply-bundle": cli_commands_module.run_apply_bundle_command,
            "verify-bundle": cli_commands_module.run_verify_bundle_command,
        }
    )

    payload = run_bundle_command(
        "plan-bundle",
        tmp_path / "bundle.zip",
        tmp_path / "wrapper",
        timestamp_token="20260404_231801",
    )

    assert payload["command_name"] == "plan-bundle"
    assert payload["bundle_zip_path"].endswith("bundle.zip")
    assert payload["timestamp_token"] == "20260404_231801"


def test_run_bundle_command_rejects_unknown_command(tmp_path: Path) -> None:
    with pytest.raises(ValueError) as exc:
        run_bundle_command(
            "unknown-bundle-command",
            tmp_path / "bundle.zip",
            tmp_path / "wrapper",
        )

    assert "Unsupported bundle command" in str(exc.value)
