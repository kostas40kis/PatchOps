import json
from pathlib import Path

from patchops.manifest_validator import validate_manifest_data


def test_example_manifests_validate():
    examples_dir = Path(__file__).resolve().parents[1] / "examples"
    for path in examples_dir.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        validate_manifest_data(data)
