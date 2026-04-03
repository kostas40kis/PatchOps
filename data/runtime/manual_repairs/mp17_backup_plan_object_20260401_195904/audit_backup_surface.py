from __future__ import annotations

from pathlib import Path

root = Path(r"C:\dev\patchops")
backups_path = root / "patchops" / "files" / "backups.py"
writers_path = root / "patchops" / "files" / "writers.py"
models_path = root / "patchops" / "models.py"

print("CURRENT BACKUP/WRITE SURFACE AUDIT")
print("----------------------------------")
for label, path in (
    ("backups", backups_path),
    ("writers", writers_path),
    ("models", models_path),
):
    print(f"{label} exists : {'yes' if path.exists() else 'no'}")
    if path.exists():
        text = path.read_text(encoding="utf-8")
        print(f"{label} line count : {len(text.splitlines())}")
        if label == "backups":
            print(f"backups has backup_file : {'yes' if 'def backup_file' in text else 'no'}")
            print(f"backups has generate_backup_root : {'yes' if 'def generate_backup_root' in text else 'no'}")