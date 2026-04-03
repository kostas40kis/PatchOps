from __future__ import annotations

import re
from pathlib import Path


_DRIVE_PREFIX = re.compile(r"^[A-Za-z]:")


def normalize_path_string(value: str) -> str:
    value = value.replace("/", "\\") if _DRIVE_PREFIX.match(value) else value.replace("\\", "/")
    return value


def safe_relative_path(target: Path, root: Path) -> Path:
    try:
        return target.relative_to(root)
    except ValueError:
        return Path(target.name)


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
