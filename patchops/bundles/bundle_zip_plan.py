from __future__ import annotations

from pathlib import Path
from typing import Any

from patchops.bundles.bundle_zip_inspect import inspect_bundle_path


def plan_bundle_path(bundle_zip_path: str | Path) -> dict[str, Any]:
    bundle_path = Path(bundle_zip_path).resolve()
    inspected = inspect_bundle_path(bundle_path)

    launchers = list(inspected.get("launchers", []))
    selected_launcher = launchers[0] if launchers else None

    payload: dict[str, Any] = {
        "bundle_zip_path": str(bundle_path),
        "exists": inspected.get("exists", bundle_path.exists()),
        "ok": bool(inspected.get("ok", False)),
        "issue_count": int(inspected.get("issue_count", len(inspected.get("issues", [])))),
        "issues": list(inspected.get("issues", [])),
        "root_folder": inspected.get("root_folder"),
        "manifest_path": inspected.get("manifest_path"),
        "bundle_meta_path": inspected.get("bundle_meta_path"),
        "readme_path": inspected.get("readme_path"),
        "content_prefix": inspected.get("content_prefix"),
        "launchers": launchers,
        "selected_launcher": selected_launcher,
        "profile_resolution": "generic_python",
        "runtime_workspace_preview": f"data/runtime/bundle_runs/{bundle_path.stem}_<timestamp>",
        "report_path_preview": f"Desktop/{bundle_path.stem}_<timestamp>.txt",
        "write_targets_preview": [],
        "command_plan": [],
    }

    if not payload["ok"]:
        return payload

    root_folder = payload["root_folder"]
    if isinstance(root_folder, str) and root_folder:
        payload["write_targets_preview"] = [
            f"<target>/{root_folder}/content/<files>",
        ]

    payload["command_plan"] = [
        f"py -m patchops.cli check-bundle {bundle_path}",
        f"py -m patchops.cli inspect-bundle {bundle_path}",
        f"py -m patchops.cli plan-bundle {bundle_path}",
    ]
    return payload
