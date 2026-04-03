from __future__ import annotations

import json
from pathlib import Path
from typing import Any


EXAMPLE_NOTES = {
    "generic_python_patch.json": "Generic apply example that writes a file and runs a validation command.",
    "generic_backup_patch.json": "Generic apply example that proves backup behavior when a file already exists.",
    "generic_verify_patch.json": "Generic verify-only example for narrow reruns and validation-only flows.",
    "trader_code_patch.json": "Trader-oriented code patch example for the first real target profile.",
    "trader_doc_patch.json": "Trader-oriented documentation patch example.",
    "trader_verify_patch.json": "Trader-oriented verify-only example."
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def list_examples(profile_name: str | None = None) -> dict[str, Any]:
    examples_dir = _repo_root() / "examples"
    items: list[dict[str, Any]] = []

    if not examples_dir.exists():
        return {
            "examples_dir": str(examples_dir),
            "profile_filter": profile_name,
            "example_count": 0,
            "examples": [],
        }

    for path in sorted(examples_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        active_profile = data.get("active_profile")
        if profile_name and active_profile != profile_name:
            continue
        items.append(
            {
                "file_name": path.name,
                "path": str(path),
                "patch_name": data.get("patch_name"),
                "active_profile": active_profile,
                "suggested_usage": EXAMPLE_NOTES.get(path.name, "Example manifest bundled with PatchOps."),
            }
        )

    return {
        "examples_dir": str(examples_dir),
        "profile_filter": profile_name,
        "example_count": len(items),
        "examples": items,
    }
