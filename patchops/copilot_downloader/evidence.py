from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from patchops.copilot_downloader.models import DownloaderEvidenceRecord


def _jsonable(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, DownloaderEvidenceRecord):
        return _jsonable(value.to_dict())
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return _jsonable(value.to_dict())
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(item) for item in value]
    return value


def write_json_evidence(path: str | Path, payload: Any) -> Path:
    evidence_path = Path(path)
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    normalized = _jsonable(payload)
    evidence_path.write_text(json.dumps(normalized, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return evidence_path


def write_text_evidence(path: str | Path, payload: Any) -> Path:
    evidence_path = Path(path)
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    normalized = _jsonable(payload)
    lines = ["PatchOps Co-Pilot downloader evidence", f"generated_utc: {datetime.now(timezone.utc).isoformat()}"]
    for key, value in sorted(normalized.items()) if isinstance(normalized, dict) else [("payload", normalized)]:
        if isinstance(value, (dict, list)):
            rendered = json.dumps(value, indent=2, sort_keys=True)
        else:
            rendered = str(value)
        lines.append(f"{key}: {rendered}")
    evidence_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return evidence_path


def write_evidence_pair(evidence_root: str | Path, name: str, payload: Any) -> dict[str, str]:
    root = Path(evidence_root)
    json_path = write_json_evidence(root / f"{name}.json", payload)
    text_path = write_text_evidence(root / f"{name}.txt", payload)
    return {"json": str(json_path), "text": str(text_path)}