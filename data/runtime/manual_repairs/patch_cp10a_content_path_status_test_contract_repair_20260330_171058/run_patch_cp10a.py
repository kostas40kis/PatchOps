from __future__ import annotations

import json
import sys
from pathlib import Path

project_root = Path(sys.argv[1]).resolve()
manifest_path = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(project_root))

from patchops.workflows.apply_patch import apply_manifest

try:
    result = apply_manifest(manifest_path, wrapper_project_root=project_root)
except Exception:
    manifest_content = manifest_path.read_text(encoding="utf-8")
    print(f"Failed to load or apply manifest.\\nManifest content:\\n{manifest_content}", file=sys.stderr)
    raise

payload = {
    "result_label": result.result_label,
    "exit_code": result.exit_code,
    "report_path": str(result.report_path),
    "failure_category": (str(result.failure.category) if result.failure else None),
    "failure_message": (result.failure.message if result.failure else None),
    "failure_details": (result.failure.details if result.failure else None),
}
print(json.dumps(payload))