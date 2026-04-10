from __future__ import annotations

import os
from pathlib import Path

from patchops.windows_env_setup import (
    apply_windows_env_setup,
    build_windows_env_setup_plan,
    windows_env_setup_as_dict,
)


def test_build_windows_env_setup_plan_defaults_current_shape(tmp_path: Path) -> None:
    wrapper_root = tmp_path / "wrapper"
    home_root = tmp_path / "home"

    plan = build_windows_env_setup_plan(
        wrapper_project_root=wrapper_root,
        home_root=home_root,
        existing_user_path="",
    )

    assert plan.wrapper_project_root == wrapper_root.resolve()
    assert plan.reports_root == home_root / "Desktop" / "PatchOpsReports"
    assert plan.bin_root == home_root / "bin" / "PatchOps"
    assert [path.name for path in plan.project_report_roots] == [
        "patchops",
        "trader",
        "generic_python",
        "_maintenance",
    ]
    assert plan.env_vars["PATCHOPS_WRAPPER_ROOT"] == str(wrapper_root.resolve())
    assert plan.path_after[-1] == str(plan.bin_root)
    assert plan.path_will_change is True


def test_build_windows_env_setup_plan_keeps_bin_path_append_idempotent(tmp_path: Path) -> None:
    wrapper_root = tmp_path / "wrapper"
    home_root = tmp_path / "home"
    existing_path = os.pathsep.join([
        str(home_root / "tools"),
        str(home_root / "bin" / "PatchOps"),
    ])

    plan = build_windows_env_setup_plan(
        wrapper_project_root=wrapper_root,
        home_root=home_root,
        existing_user_path=existing_path,
    )

    assert plan.path_will_change is False
    assert list(plan.path_after).count(str(home_root / "bin" / "PatchOps")) == 1


def test_windows_env_setup_as_dict_keeps_current_contract(tmp_path: Path) -> None:
    plan = build_windows_env_setup_plan(
        wrapper_project_root=tmp_path / "wrapper",
        reports_root=tmp_path / "reports",
        bin_root=tmp_path / "bin" / "PatchOps",
        existing_user_path="",
    )

    payload = windows_env_setup_as_dict(plan)

    assert payload["wrapper_project_root"] == str((tmp_path / "wrapper").resolve())
    assert payload["reports_root"] == str(tmp_path / "reports")
    assert payload["bin_root"] == str(tmp_path / "bin" / "PatchOps")
    assert payload["project_report_roots"] == [
        str(tmp_path / "reports" / "patchops"),
        str(tmp_path / "reports" / "trader"),
        str(tmp_path / "reports" / "generic_python"),
        str(tmp_path / "reports" / "_maintenance"),
    ]
    assert payload["path_will_change"] is True
    assert payload["directory_count"] == 6


def test_apply_windows_env_setup_can_create_directories_without_registry_persistence(tmp_path: Path) -> None:
    reports_root = tmp_path / "reports"
    bin_root = tmp_path / "bin" / "PatchOps"
    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()

    plan = build_windows_env_setup_plan(
        wrapper_project_root=wrapper_root,
        reports_root=reports_root,
        bin_root=bin_root,
        existing_user_path="",
    )

    result = apply_windows_env_setup(plan, persist_user_env=False)

    assert result["persisted_user_env"] is False
    assert reports_root.exists()
    assert bin_root.exists()
    assert (reports_root / "patchops").exists()
    assert os.environ["PATCHOPS_WRAPPER_ROOT"] == str(wrapper_root.resolve())
    assert os.environ["PATCHOPS_REPORTS_ROOT"] == str(reports_root)
    assert os.environ["PATCHOPS_BIN"] == str(bin_root)
