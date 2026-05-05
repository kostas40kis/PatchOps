from __future__ import annotations

from patchops.chatgpt_uploader.dependency_check import check_dependency, run_dependency_doctor
from patchops.chatgpt_uploader.safety_policy import assert_safe_no_side_effects


TARGET = "https://chatgpt.com/g/example/c/example"


def test_check_dependency_for_stdlib_module() -> None:
    status = check_dependency("json", required_for=("unit_test",))

    assert status.name == "json"
    assert status.import_ok is True
    assert status.error is None
    assert status.required_for == ("unit_test",)


def test_check_dependency_for_missing_module_does_not_raise() -> None:
    status = check_dependency("definitely_missing_patchops_dependency_xyz")

    assert status.import_ok is False
    assert "ModuleNotFoundError" in (status.error or "")


def test_run_dependency_doctor_is_no_side_effect() -> None:
    result = run_dependency_doctor(target_url=TARGET, dependency_names=("json",))

    assert result.ok is True
    assert result.dependencies[0].name == "json"
    assert result.dependencies[0].import_ok is True
    assert_safe_no_side_effects(result.safety)
    assert "doctor_only:no_browser_opened" in result.notes
