from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from patchops.bundles.launcher_heuristics import audit_bundle_launcher_text


def _normalize_message(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = " ".join(value.split())
        return cleaned or None
    if isinstance(value, Mapping):
        for key in ("message", "text", "warning", "issue", "reason", "code"):
            candidate = _normalize_message(value.get(key))
            if candidate:
                return candidate
    for attr in ("message", "text", "warning", "issue", "reason", "code"):
        if hasattr(value, attr):
            candidate = _normalize_message(getattr(value, attr))
            if candidate:
                return candidate
    cleaned = " ".join(str(value).split())
    return cleaned or None


def _collect_messages(source: Any) -> list[str]:
    if source is None:
        return []
    if isinstance(source, str):
        message = _normalize_message(source)
        return [] if message is None else [message]

    values: list[Any] = []
    if isinstance(source, Mapping):
        for key in ("warnings", "issues", "findings", "messages", "heuristics", "risk_warnings"):
            if key in source:
                values.append(source[key])
    else:
        for attr in ("warnings", "issues", "findings", "messages", "heuristics", "risk_warnings"):
            if hasattr(source, attr):
                values.append(getattr(source, attr))

    if not values and isinstance(source, Iterable) and not isinstance(source, (bytes, bytearray)):
        values.append(source)

    messages: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value is None:
            continue
        if isinstance(value, str):
            normalized = _normalize_message(value)
            if normalized and normalized not in seen:
                seen.add(normalized)
                messages.append(normalized)
            continue
        if isinstance(value, Mapping):
            normalized = _normalize_message(value)
            if normalized and normalized not in seen:
                seen.add(normalized)
                messages.append(normalized)
            continue
        if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
            for item in value:
                normalized = _normalize_message(item)
                if normalized and normalized not in seen:
                    seen.add(normalized)
                    messages.append(normalized)
            continue
        normalized = _normalize_message(value)
        if normalized and normalized not in seen:
            seen.add(normalized)
            messages.append(normalized)
    return messages


def check_launcher_path(path: str | Path) -> dict[str, Any]:
    launcher_path = Path(path).resolve()
    if not launcher_path.exists():
        issue = f"Launcher path does not exist: {launcher_path}"
        return {
            "path": str(launcher_path),
            "exists": False,
            "ok": False,
            "issue_count": 1,
            "issues": [issue],
        }
    if launcher_path.is_dir():
        issue = f"Launcher path is a directory, not a file: {launcher_path}"
        return {
            "path": str(launcher_path),
            "exists": True,
            "ok": False,
            "issue_count": 1,
            "issues": [issue],
        }

    text = launcher_path.read_text(encoding="utf-8")
    audit_result = audit_bundle_launcher_text(text)
    issues = _collect_messages(audit_result)
    if not issues:
        if isinstance(audit_result, Mapping):
            if audit_result.get("ok") is False:
                issues = ["Launcher audit returned not ok without explicit issue text."]
        elif hasattr(audit_result, "ok") and getattr(audit_result, "ok") is False:
            issues = ["Launcher audit returned not ok without explicit issue text."]

    return {
        "path": str(launcher_path),
        "exists": True,
        "ok": len(issues) == 0,
        "issue_count": len(issues),
        "issues": issues,
    }

