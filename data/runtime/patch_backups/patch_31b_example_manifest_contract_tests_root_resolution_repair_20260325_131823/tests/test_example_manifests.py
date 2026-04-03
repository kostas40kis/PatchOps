import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = PROJECT_ROOT / "examples"
CORE_EXAMPLES = {
    "generic_python_patch.json",
    "generic_verify_patch.json",
    "generic_python_powershell_patch.json",
    "generic_python_powershell_verify_patch.json",
    "trader_code_patch.json",
    "trader_doc_patch.json",
    "trader_verify_patch.json",
    "trader_first_doc_patch.json",
    "trader_first_verify_patch.json",
}
VERIFY_EXAMPLES = [
    "generic_verify_patch.json",
    "generic_python_powershell_verify_patch.json",
    "trader_verify_patch.json",
    "trader_first_verify_patch.json",
]
ALLOWED_PROFILES = {"generic_python", "generic_python_powershell", "trader"}


def _example_paths() -> list[Path]:
    return sorted(EXAMPLES_DIR.glob("*.json"))


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "patchops.cli", *args],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
    )


def test_examples_directory_has_expected_surface() -> None:
    paths = _example_paths()
    names = {path.name for path in paths}
    assert EXAMPLES_DIR.exists(), f"Missing examples directory: {EXAMPLES_DIR}"
    assert len(paths) >= 10, "Expected a meaningful example-manifest surface."
    missing = sorted(CORE_EXAMPLES - names)
    assert not missing, f"Missing core example manifests: {missing}"


def test_example_manifests_are_valid_json_with_core_fields() -> None:
    for path in _example_paths():
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict), f"Example manifest must be a JSON object: {path.name}"
        for field in ("manifest_version", "patch_name", "active_profile"):
            assert field in data, f"Missing required field {field!r} in {path.name}"
        assert data["active_profile"] in ALLOWED_PROFILES, (
            f"Unexpected active_profile {data['active_profile']!r} in {path.name}"
        )
        assert any(
            field in data
            for field in (
                "validation_commands",
                "smoke_commands",
                "audit_commands",
                "cleanup_commands",
                "archive_commands",
                "files_to_write",
                "target_files",
            )
        ), f"Example manifest should express at least one meaningful workflow surface: {path.name}"


def test_examples_command_lists_current_manifest_files() -> None:
    result = _run_cli("examples")
    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(result.stdout)
    listed_names = {item["file_name"] for item in payload["examples"]}
    actual_names = {path.name for path in _example_paths()}
    missing = sorted(actual_names - listed_names)
    assert not missing, f"examples command omitted manifests: {missing}"
    assert payload["example_count"] == len(payload["examples"])


def test_schema_command_is_available_for_example_contract_work() -> None:
    result = _run_cli("schema")
    assert result.returncode == 0, result.stderr or result.stdout
    assert result.stdout.strip(), "schema command should emit a schema surface"


def test_verify_examples_can_be_planned_in_verify_mode() -> None:
    for file_name in VERIFY_EXAMPLES:
        manifest_path = EXAMPLES_DIR / file_name
        result = _run_cli("plan", str(manifest_path), "--mode", "verify")
        assert result.returncode == 0, (
            f"plan failed for {file_name}\nstdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
        )
        payload = json.loads(result.stdout)
        assert payload["manifest_path"].lower().endswith(file_name.lower())
        assert payload["mode"] == "verify"
