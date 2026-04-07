from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
import shutil
import zipfile


BUNDLE_RUN_ROOT_RELATIVE = Path("data") / "runtime" / "bundle_runs"
EXTRACTED_BUNDLE_DIR_NAME = "extracted_bundle"


@dataclass(slots=True)
class BundleZipExtractionResult:
    bundle_zip_path: Path
    wrapper_project_root: Path
    run_root: Path
    extracted_root: Path
    bundle_root: Path
    was_flat_archive: bool
    top_level_entries: tuple[str, ...]


def _timestamp_token(value: str | None = None) -> str:
    if value:
        return value
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def sanitize_bundle_name_from_zip(bundle_zip_path: Path) -> str:
    stem = bundle_zip_path.stem.strip()
    if not stem:
        return "bundle"

    safe_chars: list[str] = []
    for char in stem:
        if char.isalnum() or char in {"-", "_"}:
            safe_chars.append(char)
        else:
            safe_chars.append("_")

    collapsed = "".join(safe_chars).strip("_")
    return collapsed or "bundle"


def build_bundle_run_root(
    wrapper_project_root: Path,
    bundle_zip_path: Path,
    *,
    timestamp_token: str | None = None,
) -> Path:
    bundle_name = sanitize_bundle_name_from_zip(bundle_zip_path)
    return wrapper_project_root / BUNDLE_RUN_ROOT_RELATIVE / f"{bundle_name}_{_timestamp_token(timestamp_token)}"


def _member_is_unsafe(member_name: str) -> bool:
    parts = PurePosixPath(member_name).parts
    if not parts:
        return False
    if PurePosixPath(member_name).is_absolute():
        return True
    return any(part in {"..", ""} for part in parts)


def _collect_top_level_entries(names: list[str]) -> tuple[str, ...]:
    entries: list[str] = []
    seen: set[str] = set()
    for name in names:
        parts = PurePosixPath(name).parts
        if not parts:
            continue
        first = parts[0]
        if first not in seen:
            entries.append(first)
            seen.add(first)
    return tuple(entries)


def extract_bundle_zip(
    bundle_zip_path: Path,
    wrapper_project_root: Path,
    *,
    timestamp_token: str | None = None,
) -> BundleZipExtractionResult:
    bundle_zip_path = Path(bundle_zip_path)
    wrapper_project_root = Path(wrapper_project_root)

    if not bundle_zip_path.exists():
        raise FileNotFoundError(f"Bundle zip does not exist: {bundle_zip_path}")
    if bundle_zip_path.suffix.lower() != ".zip":
        raise ValueError(f"Bundle input is not a .zip file: {bundle_zip_path}")

    run_root = build_bundle_run_root(
        wrapper_project_root,
        bundle_zip_path,
        timestamp_token=timestamp_token,
    )
    extracted_root = run_root / EXTRACTED_BUNDLE_DIR_NAME
    if run_root.exists():
        shutil.rmtree(run_root)
    extracted_root.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(bundle_zip_path, "r") as archive:
        member_names = [name for name in archive.namelist() if name and not name.endswith("/")]
        unsafe = [name for name in member_names if _member_is_unsafe(name)]
        if unsafe:
            raise ValueError(f"Unsafe bundle zip member(s): {unsafe}")

        top_level_entries = _collect_top_level_entries(member_names)
        was_flat_archive = False

        if top_level_entries and all("/" not in name for name in member_names):
            was_flat_archive = True
        elif len(top_level_entries) > 1:
            was_flat_archive = True

        archive.extractall(extracted_root)

    bundle_root = extracted_root
    if not was_flat_archive and len(top_level_entries) == 1:
        candidate = extracted_root / top_level_entries[0]
        if candidate.exists() and candidate.is_dir():
            bundle_root = candidate
        else:
            was_flat_archive = True
            bundle_root = extracted_root

    return BundleZipExtractionResult(
        bundle_zip_path=bundle_zip_path,
        wrapper_project_root=wrapper_project_root,
        run_root=run_root,
        extracted_root=extracted_root,
        bundle_root=bundle_root,
        was_flat_archive=was_flat_archive,
        top_level_entries=top_level_entries,
    )
