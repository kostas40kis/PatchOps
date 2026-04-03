import json
from pathlib import Path

from patchops.manifest_validator import validate_manifest_data


def test_example_manifests_validate():
    examples_dir = Path(__file__).resolve().parents[1] / "examples"
    expected = {
        "generic_python_patch.json",
        "generic_backup_patch.json",
        "generic_verify_patch.json",
        "trader_code_patch.json",
        "trader_doc_patch.json",
        "trader_verify_patch.json",
    }
    actual = {path.name for path in examples_dir.glob("*.json")}
    assert expected.issubset(actual)
    for path in examples_dir.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        validate_manifest_data(data)