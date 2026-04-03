from pathlib import Path
import sys

project_root = Path(sys.argv[1])
checks = {
    project_root / "docs" / "summary_integrity_repair_stream.md": [
        "Patch 133A is the confirmed product bug.",
        "wrapper/content-path authoring problem",
        "malformed-manifest authoring problem",
    ],
    project_root / "docs" / "project_status.md": [
        "PATCHOPS_PATCH134A_STATUS",
        "summary-integrity repair stream truth reset",
        "Patch 133A repaired the manifest-local content-path issue and confirmed the real product bug",
    ],
    project_root / "docs" / "patch_ledger.md": [
        "PATCHOPS_PATCH134A_LEDGER",
        "Patch 134A resets the summary-integrity repair stream",
    ],
}

missing = []
for path, phrases in checks.items():
    text = path.read_text(encoding="utf-8")
    for phrase in phrases:
        if phrase not in text:
            missing.append(f"{path}: missing phrase -> {phrase}")

if missing:
    raise SystemExit("\n".join(missing))

print("patch_134a validation passed")