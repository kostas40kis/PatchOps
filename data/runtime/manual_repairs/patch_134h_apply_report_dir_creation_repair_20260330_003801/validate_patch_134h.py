from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
apply_text = (root / "patchops" / "workflows" / "apply_patch.py").read_text(encoding="utf-8")
test_text = (root / "tests" / "test_report_preference_apply_flow_current.py").read_text(encoding="utf-8")
stream_text = (root / "docs" / "summary_integrity_repair_stream.md").read_text(encoding="utf-8")

assert "report_path.parent.mkdir(parents=True, exist_ok=True)" in apply_text
assert "test_apply_manifest_creates_missing_custom_report_dir" in test_text
assert "PATCHOPS_PATCH134H_REPORT_DIR_REPAIR" in stream_text
print("patch_134h validation passed")
