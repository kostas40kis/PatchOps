from __future__ import annotations

from pathlib import Path

root = Path(r"C:\dev\patchops")
backups_path = root / "patchops" / "files" / "backups.py"
existing_test_path = root / "tests" / "test_backup_plan_current.py"
report_test_path = root / "tests" / "test_backup_report_evidence_current.py"

print("CURRENT BACKUP REPORT EVIDENCE SURFACE AUDIT")
print("-------------------------------------------")
for label, path in (
    ("backups", backups_path),
    ("existing backup plan test", existing_test_path),
    ("new backup report test", report_test_path),
):
    print(f"{label} exists : {'yes' if path.exists() else 'no'}")
    if path.exists():
        text = path.read_text(encoding="utf-8")
        print(f"{label} line count : {len(text.splitlines())}")
        if label == "backups":
            print(f"backups has build_backup_plan : {'yes' if 'def build_backup_plan' in text else 'no'}")
            print(f"backups has execute_backup_plan : {'yes' if 'def execute_backup_plan' in text else 'no'}")
            print(f"backups has render_backup_report_line : {'yes' if 'def render_backup_report_line' in text else 'no'}")