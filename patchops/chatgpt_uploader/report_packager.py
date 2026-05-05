from __future__ import annotations

import hashlib
import re
import shutil
from pathlib import Path

from .models import ReportPackageCandidate


_ALLOWED_SUFFIXES = {".txt", ".md", ".log", ".json"}
_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9_.-]+")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_upload_name(source: Path, *, max_stem: int = 80) -> str:
    stem = _SAFE_NAME_RE.sub("_", source.stem).strip("._-") or "patchops_report"
    suffix = source.suffix.lower() or ".txt"
    if suffix not in _ALLOWED_SUFFIXES:
        suffix = ".txt"
    return f"{stem[:max_stem]}{suffix}"


def build_safe_report_copy(
    source_path: str | Path,
    *,
    staging_root: str | Path | None = None,
) -> ReportPackageCandidate:
    """Copy a local report to a short safe staging path.

    This prepares a file for future upload, but it does not open a browser and
    does not upload anything.
    """

    source = Path(source_path).expanduser().resolve()

    if not source.exists():
        raise FileNotFoundError(f"Report path does not exist: {source}")
    if not source.is_file():
        raise ValueError(f"Report path is not a file: {source}")
    if source.suffix.lower() not in _ALLOWED_SUFFIXES:
        raise ValueError(f"Unsupported report suffix for safe upload staging: {source.suffix}")

    root = Path(staging_root) if staging_root is not None else Path.cwd() / "data" / "runtime" / "chatgpt_uploader_staging"
    root = root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    digest = _sha256(source)
    safe_name = safe_upload_name(source)
    staged_name = f"{digest[:12]}_{safe_name}"
    staged = root / staged_name

    shutil.copy2(source, staged)

    return ReportPackageCandidate(
        source_path=str(source),
        staged_path=str(staged),
        size_bytes=staged.stat().st_size,
        sha256=digest,
        safe_name=staged_name,
    )
