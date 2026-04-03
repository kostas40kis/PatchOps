from __future__ import annotations

import json
from pathlib import Path

from patchops.workflows.apply_patch import apply_manifest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_generic_content_path_example_applies_successfully_end_to_end(tmp_path: Path) -> None:
    source_manifest_path = PROJECT_ROOT / "examples" / "generic_content_path_patch.json"
    source_payload_path = PROJECT_ROOT / "examples" / "content" / "generic_content_path_note.txt"

    wrapper_root = tmp_path / "wrapper_project"
    target_root = tmp_path / "target_repo"
    report_dir = tmp_path / "reports"
    patch_root = (
        wrapper_root
        / "data"
        / "runtime"
        / "manual_repairs"
        / "patch_cp4_content_path_example_apply_flow_proof"
    )

    target_root.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    patch_root.mkdir(parents=True, exist_ok=True)

    payload = source_payload_path.read_text(encoding="utf-8")

    copied_payload_path = wrapper_root / "examples" / "content" / "generic_content_path_note.txt"
    copied_payload_path.parent.mkdir(parents=True, exist_ok=True)
    copied_payload_path.write_text(payload, encoding="utf-8")

    manifest_data = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    manifest_data["target_project_root"] = target_root.as_posix()
    manifest_data["report_preferences"] = {
        "report_dir": report_dir.as_posix(),
        "report_name_prefix": "generic_content_path_example_apply_current",
        "write_to_desktop": False,
    }

    manifest_path = patch_root / "patch_manifest.json"
    # Write compact JSON (no extra whitespace/newline) for reliability
    manifest_path.write_text(json.dumps(manifest_data, separators=(',', ':')), encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    written_file = target_root / "CONTENT_PATH_EXAMPLE.txt"
    assert result.result_label == "PASS"
    assert result.exit_code == 0
    assert result.report_path.exists()
    assert written_file.exists()
    assert written_file.read_text(encoding="utf-8") == payload

    report_text = result.report_path.read_text(encoding="utf-8")
    assert "CONTENT_PATH_EXAMPLE.txt" in report_text
    assert "generic_content_path_example" in report_text
    assert "Result   : PASS" in report_text
