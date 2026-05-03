from __future__ import annotations

import argparse
import fnmatch
import json
import time
import zipfile
from pathlib import Path
from typing import Any

PATCH = "L25.49A"
NAME = "L25.49A manual browser + selected/latest Downloads zip live probe"
AUTHORIZATION_TOKEN = "PATCHOPS_L25_49A_MANUAL_ZIP_PATH_OR_LATEST_AUTHORIZED"
TEMP_SUFFIXES = (".crdownload", ".tmp", ".opdownload", ".part")

def emit(payload: dict[str, Any], *, compact: bool) -> None:
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if compact else None, indent=None if compact else 2))

def is_temporary_download(path: Path) -> bool:
    lower = path.name.lower()
    return any(lower.endswith(suffix) for suffix in TEMP_SUFFIXES)

def validate_stable_zip(path: Path, *, stable_seconds: float) -> tuple[bool, dict[str, Any]]:
    if not path.exists() or not path.is_file():
        return False, {"reason": "zip path does not exist or is not a file", "path": str(path)}
    if is_temporary_download(path):
        return False, {"reason": "temporary browser download file", "path": str(path)}
    if path.suffix.lower() != ".zip":
        return False, {"reason": "file extension is not .zip", "path": str(path)}
    try:
        first = path.stat()
    except OSError as exc:
        return False, {"reason": f"stat failed before stability wait: {exc}", "path": str(path)}
    if first.st_size <= 0:
        return False, {"reason": "zero byte candidate", "path": str(path), "size": first.st_size}
    time.sleep(stable_seconds)
    try:
        second = path.stat()
    except OSError as exc:
        return False, {"reason": f"stat failed after stability wait: {exc}", "path": str(path)}
    if first.st_size != second.st_size:
        return False, {"reason": "size changed during stability window", "path": str(path), "first_size": first.st_size, "second_size": second.st_size}
    if second.st_size <= 0:
        return False, {"reason": "zero byte candidate after stability wait", "path": str(path), "size": second.st_size}
    if not zipfile.is_zipfile(path):
        return False, {"reason": "zip container validation failed", "path": str(path), "size": second.st_size}
    return True, {
        "zip_path": str(path),
        "zip_name": path.name,
        "zip_size_bytes": second.st_size,
        "zip_mtime_epoch": second.st_mtime,
        "stable_seconds": stable_seconds,
        "stable_size_observed": True,
        "zip_container_validation_performed": True,
        "zip_container_valid": True,
    }

def latest_recent_zip(download_dir: Path, *, pattern: str, recent_minutes: int) -> tuple[Path | None, list[dict[str, Any]]]:
    cutoff = time.time() - max(1, recent_minutes) * 60
    rows: list[dict[str, Any]] = []
    for path in download_dir.iterdir():
        if not path.is_file() or is_temporary_download(path):
            continue
        if path.suffix.lower() != ".zip":
            continue
        if not fnmatch.fnmatch(path.name, pattern):
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        if stat.st_mtime < cutoff:
            continue
        rows.append({"path": str(path), "name": path.name, "mtime": stat.st_mtime, "size": stat.st_size})
    rows.sort(key=lambda row: float(row["mtime"]), reverse=True)
    return (Path(str(rows[0]["path"])) if rows else None, rows[:10])

def wait_for_latest_zip(download_dir: Path, *, pattern: str, wait_seconds: int, recent_minutes: int) -> tuple[Path | None, list[dict[str, Any]]]:
    deadline = time.time() + max(5, wait_seconds)
    last_rows: list[dict[str, Any]] = []
    while time.time() < deadline:
        found, rows = latest_recent_zip(download_dir, pattern=pattern, recent_minutes=recent_minutes)
        last_rows = rows
        if found is not None:
            return found, rows
        time.sleep(1.0)
    return None, last_rows

def success_payload(*, source_mode: str, details: dict[str, Any], download_dir: Path, pattern: str, recent_minutes: int) -> dict[str, Any]:
    payload = {
        "ok": True,
        "patch": PATCH,
        "manual_browser_download_bridge": True,
        "explicit_zip_path_or_latest_download_supported": True,
        "uses_real_download_as_main_proof": True,
        "synthetic_fixture_main_proof": False,
        "zip_source_mode": source_mode,
        "download_dir": str(download_dir),
        "file_pattern": pattern,
        "recent_minutes": recent_minutes,
        "cloudflare_bypass_attempted": False,
        "browser_automation_used": False,
        "selenium_used": False,
        "dom_scraping_used": False,
        "download_click_automated": False,
        "artifact_payload_extracted": False,
        "archive_member_extracted": False,
        "run_package_invoked_by_l25_49a": False,
        "pasteback": False,
        "send_submit_performed": False,
        "localhost_server_started": False,
        "browser_extension_used": False,
        "git_commit_performed": False,
        "git_push_performed": False,
    }
    payload.update(details)
    return payload

def run_probe(*, download_dir: Path, zip_path: Path | None, pattern: str, wait_seconds: int, stable_seconds: float, recent_minutes: int) -> dict[str, Any]:
    if zip_path is not None:
        ok, details = validate_stable_zip(zip_path, stable_seconds=stable_seconds)
        if ok:
            return success_payload(source_mode="explicit_zip_path", details=details, download_dir=download_dir, pattern=pattern, recent_minutes=recent_minutes)
        return {
            "ok": False,
            "patch": PATCH,
            "failure_layer": "explicit_zip_path_invalid",
            "details": details,
            "manual_browser_download_bridge": True,
            "run_package_invoked_by_l25_49a": False,
            "pasteback": False,
            "send_submit_performed": False,
            "localhost_server_started": False,
            "browser_extension_used": False,
            "git_commit_performed": False,
            "git_push_performed": False,
        }
    found, rows = wait_for_latest_zip(download_dir, pattern=pattern, wait_seconds=wait_seconds, recent_minutes=recent_minutes)
    if found is None:
        return {
            "ok": False,
            "patch": PATCH,
            "failure_layer": "no_recent_zip_found",
            "download_dir": str(download_dir),
            "file_pattern": pattern,
            "wait_seconds": wait_seconds,
            "recent_minutes": recent_minutes,
            "recent_zip_candidates": rows,
            "manual_browser_download_bridge": True,
            "run_package_invoked_by_l25_49a": False,
            "pasteback": False,
            "send_submit_performed": False,
            "localhost_server_started": False,
            "browser_extension_used": False,
            "git_commit_performed": False,
            "git_push_performed": False,
        }
    ok, details = validate_stable_zip(found, stable_seconds=stable_seconds)
    if ok:
        details["recent_zip_candidates"] = rows
        return success_payload(source_mode="latest_recent_download", details=details, download_dir=download_dir, pattern=pattern, recent_minutes=recent_minutes)
    return {
        "ok": False,
        "patch": PATCH,
        "failure_layer": "latest_recent_zip_invalid",
        "details": details,
        "recent_zip_candidates": rows,
        "manual_browser_download_bridge": True,
        "run_package_invoked_by_l25_49a": False,
        "pasteback": False,
        "send_submit_performed": False,
        "localhost_server_started": False,
        "browser_extension_used": False,
        "git_commit_performed": False,
        "git_push_performed": False,
    }

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--download-dir", required=True)
    parser.add_argument("--zip-path", default="")
    parser.add_argument("--pattern", default="*.zip")
    parser.add_argument("--wait-seconds", type=int, default=300)
    parser.add_argument("--stable-seconds", type=float, default=2.0)
    parser.add_argument("--recent-minutes", type=int, default=180)
    parser.add_argument("--allow-live-filesystem", action="store_true")
    parser.add_argument("--authorization-token", default="")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    if not args.allow_live_filesystem or args.authorization_token != AUTHORIZATION_TOKEN:
        emit({
            "ok": False,
            "patch": PATCH,
            "error": "explicit live filesystem authorization token required",
            "live_filesystem_authorization_required": True,
            "browser_automation_used": False,
            "download_click_automated": False,
            "run_package_invoked_by_l25_49a": False,
        }, compact=args.compact)
        return 1
    download_dir = Path(args.download_dir).resolve()
    zip_path = Path(args.zip_path).resolve() if args.zip_path else None
    payload = run_probe(
        download_dir=download_dir,
        zip_path=zip_path,
        pattern=args.pattern,
        wait_seconds=args.wait_seconds,
        stable_seconds=args.stable_seconds,
        recent_minutes=args.recent_minutes,
    )
    emit(payload, compact=args.compact)
    return 0 if payload.get("ok") is True else 1

if __name__ == "__main__":
    raise SystemExit(main())

