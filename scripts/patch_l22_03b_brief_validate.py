
from __future__ import annotations
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE = PROJECT_ROOT / "patchops" / "llm_browser" / "live_adapter_edge_downloaded_archive_manifest_validation_passive_plan_launcher_direct.py"
DOC = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_downloaded_archive_manifest_validation_passive_plan_launcher_direct.md"


def main() -> int:
    ok = MODULE.exists() and DOC.exists()
    summary = {
        "ok": ok,
        "patch": "L22.3b",
        "module_exists": MODULE.exists(),
        "doc_exists": DOC.exists(),
        "manifest_read": False,
        "archive_extracted": False,
        "member_bytes_read": False,
        "browser_started": False,
        "pasteback": False,
        "package_run": False,
        "next_patch": "L22.4 Microsoft Edge downloaded-archive manifest validation controlled authorization gate",
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
