from __future__ import annotations

from pathlib import Path

root = Path(r"C:\dev\patchops")
writers_path = root / "patchops" / "files" / "writers.py"
write_test_path = root / "tests" / "test_write_plan_current.py"

print("CURRENT WRITE PLAN SURFACE AUDIT")
print("-------------------------------")
for label, path in (
    ("writers", writers_path),
    ("write plan test", write_test_path),
):
    print(f"{label} exists : {'yes' if path.exists() else 'no'}")
    if path.exists():
        text = path.read_text(encoding="utf-8")
        print(f"{label} line count : {len(text.splitlines())}")
        if label == "writers":
            print(f"writers has load_content : {'yes' if 'def load_content' in text else 'no'}")
            print(f"writers has write_text_file : {'yes' if 'def write_text_file' in text else 'no'}")
            print(f"writers has WritePlan : {'yes' if 'class WritePlan' in text else 'no'}")
            print(f"writers has build_write_plan : {'yes' if 'def build_write_plan' in text else 'no'}")