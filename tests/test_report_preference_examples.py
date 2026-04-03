import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_manifest(name: str) -> dict:
    path = PROJECT_ROOT / "examples" / name
    return json.loads(path.read_text(encoding="utf-8"))


def test_generic_report_prefix_example_fields() -> None:
    manifest = _load_manifest("generic_report_prefix_patch.json")
    assert manifest["active_profile"] == "generic_python"
    assert manifest["report_preferences"]["report_name_prefix"] == "generic_prefix_demo"
    assert manifest["report_preferences"]["write_to_desktop"] is True
    assert manifest["report_preferences"]["report_dir"] is None


def test_generic_report_dir_example_fields() -> None:
    manifest = _load_manifest("generic_report_dir_patch.json")
    assert manifest["active_profile"] == "generic_python"
    assert manifest["report_preferences"]["report_name_prefix"] == "generic_dir_demo"
    assert manifest["report_preferences"]["report_dir"] == ".\\data\\runtime\\reports"
    assert manifest["report_preferences"]["write_to_desktop"] is False
