import json
from pathlib import Path


def _load_manifest(name: str) -> dict:
    path = Path("examples") / name
    return json.loads(path.read_text(encoding="utf-8"))


def test_generic_python_powershell_apply_example_manifest_shape() -> None:
    manifest = _load_manifest("generic_python_powershell_patch.json")
    assert manifest["active_profile"] == "generic_python_powershell"
    assert manifest["patch_name"] == "generic_python_powershell_example_patch"
    assert manifest["files_to_write"]
    assert manifest["smoke_commands"]
    assert manifest["smoke_commands"][0]["program"].lower().startswith("powershell")


def test_generic_python_powershell_verify_example_manifest_shape() -> None:
    manifest = _load_manifest("generic_python_powershell_verify_patch.json")
    assert manifest["active_profile"] == "generic_python_powershell"
    assert manifest["patch_name"] == "generic_python_powershell_example_verify"
    assert manifest["files_to_write"] == []
    assert manifest["validation_commands"]
    assert manifest["smoke_commands"]
