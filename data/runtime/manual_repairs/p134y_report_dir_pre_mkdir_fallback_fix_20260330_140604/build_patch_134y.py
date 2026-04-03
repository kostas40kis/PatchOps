from __future__ import annotations

import json
import sys
from pathlib import Path

patch_root = Path(sys.argv[1]).resolve()
content_root = patch_root / "content"
(content_root / "patchops" / "workflows").mkdir(parents=True, exist_ok=True)

common_py = """from __future__ import annotations

from datetime import datetime
from hashlib import sha1
from pathlib import Path

from patchops.files.paths import ensure_directory


MAX_REPORT_PATH_LENGTH = 220
FALLBACK_REPORT_DIR_NAME = \"patchops_reports\"


def infer_workspace_root(target_project_root: Path) -> Path | None:
    return target_project_root.parent if target_project_root.parent != target_project_root else None


def default_report_directory() -> Path:
    return Path.home() / \"Desktop\"


def fallback_report_directory() -> Path:
    fallback_dir = default_report_directory() / FALLBACK_REPORT_DIR_NAME
    ensure_directory(fallback_dir)
    return fallback_dir


def build_report_path(prefix: str, patch_name: str, report_dir: Path) -> Path:
    safe_prefix = prefix.lower().replace(\" \", \"_\")
    safe_patch = patch_name.lower().replace(\" \", \"_\")
    timestamp = datetime.now().strftime(\"%Y%m%d_%H%M%S\")

    name_token = safe_prefix if safe_prefix == safe_patch else f\"{safe_prefix}_{safe_patch}\"
    preferred = report_dir / f\"{name_token}_{timestamp}.txt\"
    if len(str(preferred)) <= MAX_REPORT_PATH_LENGTH:
        ensure_directory(report_dir)
        return preferred

    digest_source = f\"{safe_prefix}|{safe_patch}|{report_dir}\"
    digest = sha1(digest_source.encode(\"utf-8\")).hexdigest()[:12]

    compact_base = safe_patch[:40] if safe_patch else \"report\"
    compact = report_dir / f\"{compact_base}_{digest}_{timestamp}.txt\"
    if len(str(compact)) <= MAX_REPORT_PATH_LENGTH:
        ensure_directory(report_dir)
        return compact

    minimal = report_dir / f\"r_{digest}_{timestamp}.txt\"
    if len(str(minimal)) <= MAX_REPORT_PATH_LENGTH:
        ensure_directory(report_dir)
        return minimal

    fallback_dir = fallback_report_directory()
    return fallback_dir / f\"r_{digest}_{timestamp}.txt\"
"""

manifest = {
    "manifest_version": "1",
    "patch_name": "p134y_report_dir_pre_mkdir_fallback_fix",
    "active_profile": "generic_python",
    "target_project_root": "C:/dev/patchops",
    "backup_files": [],
    "files_to_write": [
        {
            "path": "patchops/workflows/common.py",
            "content": None,
            "content_path": "content/patchops/workflows/common.py",
            "encoding": "utf-8",
        }
    ],
    "validation_commands": [
        {
            "name": "report_path_pre_mkdir_fallback_pytest",
            "program": "py",
            "args": [
                "-m",
                "pytest",
                "-q",
                "tests/test_report_preference_apply_flow.py",
                "tests/test_report_preference_apply_flow_current.py",
                "tests/test_report_preference_examples.py",
                "tests/test_apply_report_write_current.py",
                "tests/test_report_path_current.py",
            ],
            "working_directory": ".",
            "use_profile_runtime": False,
            "allowed_exit_codes": [0],
        }
    ],
    "smoke_commands": [],
    "audit_commands": [],
    "cleanup_commands": [],
    "archive_commands": [],
    "failure_policy": {},
    "report_preferences": {
        "report_dir": str((patch_root / "inner_reports")).replace("\\", "/"),
        "report_name_prefix": "p134y",
        "write_to_desktop": False,
    },
    "tags": [
        "self_hosted",
        "summary_integrity",
        "report_path",
        "fallback_fix",
        "mkdir_timing",
    ],
    "notes": "Patch 134Y delays custom report_dir creation until after candidate path selection so fallback can trigger before Windows long-path mkdir failures.",
}

(content_root / "patchops" / "workflows" / "common.py").write_text(common_py, encoding="utf-8")
manifest_path = patch_root / "patch_manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

print(str(manifest_path))