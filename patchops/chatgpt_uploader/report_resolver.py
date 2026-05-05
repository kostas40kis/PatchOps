from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

DEFAULT_FAILURE_LAYER = "report_resolver"
DEFAULT_REPORT_GLOB = "*.txt"
MAX_PREVIEW_CHARS = 120


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _coerce_path(value: str | os.PathLike[str] | None) -> Path | None:
    if value is None:
        return None
    raw = str(value).strip().strip('"')
    if not raw:
        return None
    return Path(raw).expanduser()


def _safe_preview(text: str, limit: int = MAX_PREVIEW_CHARS) -> str:
    compact = " ".join(str(text or "").replace("\r", " ").replace("\n", " ").split())
    if len(compact) <= limit:
        return compact
    return compact[: max(0, limit - 3)] + "..."


def _candidate_sort_key(path: Path) -> tuple[float, str]:
    try:
        mtime = path.stat().st_mtime
    except OSError:
        mtime = 0.0
    return (mtime, path.name.lower())


def _iter_report_candidates(report_dir: Path, *, prefix: str = "", glob_pattern: str = DEFAULT_REPORT_GLOB) -> Iterable[Path]:
    if not report_dir.exists() or not report_dir.is_dir():
        return ()
    clean_prefix = str(prefix or "")
    candidates: list[Path] = []
    for path in report_dir.glob(glob_pattern or DEFAULT_REPORT_GLOB):
        if not path.is_file():
            continue
        if clean_prefix and not path.name.startswith(clean_prefix):
            continue
        candidates.append(path)
    return tuple(candidates)


@dataclass(frozen=True)
class ReportResolverResult:
    result: str
    resolver_mode: str
    report_path_provided: bool
    report_dir_provided: bool
    report_path: str
    report_name: str
    report_exists: bool
    report_is_file: bool
    report_size_bytes: int
    report_sha256: str
    report_mtime_utc: str
    candidate_count: int
    candidate_names: tuple[str, ...]
    latest_selected: bool
    report_preview: str
    failure_layer: str
    error: str
    webdriver_used: bool = False
    selenium_used: bool = False
    browser_dom_automation_used: bool = False
    cloudflare_bypass_attempted: bool = False
    captcha_bypass_attempted: bool = False
    file_upload_attempted: bool = False
    chatgpt_submit_performed: bool = False
    conversation_text_logged: bool = False
    random_page_click_performed: bool = False

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def ok(self) -> bool:
        return self.result == "PASS"


def _blocked(*, mode: str, report_path_provided: bool, report_dir_provided: bool, error: str, candidate_count: int = 0, candidate_names: tuple[str, ...] = ()) -> ReportResolverResult:
    return ReportResolverResult(
        result="BLOCKED",
        resolver_mode=mode,
        report_path_provided=report_path_provided,
        report_dir_provided=report_dir_provided,
        report_path="",
        report_name="",
        report_exists=False,
        report_is_file=False,
        report_size_bytes=0,
        report_sha256="",
        report_mtime_utc="",
        candidate_count=candidate_count,
        candidate_names=candidate_names,
        latest_selected=False,
        report_preview="",
        failure_layer=DEFAULT_FAILURE_LAYER,
        error=error,
    )


def resolve_report(
    *,
    report_path: str | os.PathLike[str] | None = None,
    report_dir: str | os.PathLike[str] | None = None,
    prefix: str = "",
    glob_pattern: str = DEFAULT_REPORT_GLOB,
) -> ReportResolverResult:
    """Resolve one local PatchOps report without parsing or uploading it.

    Resolution priority is intentionally narrow:
    1. explicit report_path, if supplied;
    2. latest matching .txt inside report_dir, if supplied.

    This module does not open a browser, submit text, upload files, or parse PASS/FAIL
    report contents. U0.4 owns parsing and later patches own pasteback/send gates.
    """
    explicit = _coerce_path(report_path)
    directory = _coerce_path(report_dir)

    if explicit is not None:
        return _resolve_explicit_path(explicit)

    if directory is not None:
        return _resolve_latest_in_dir(directory, prefix=prefix, glob_pattern=glob_pattern)

    return _blocked(
        mode="none",
        report_path_provided=False,
        report_dir_provided=False,
        error="No report path or report directory was supplied.",
    )


def _resolve_explicit_path(path: Path) -> ReportResolverResult:
    resolved = path.resolve()
    if not resolved.exists():
        return _blocked(
            mode="explicit_path",
            report_path_provided=True,
            report_dir_provided=False,
            error=f"Report path does not exist: {resolved}",
        )
    if not resolved.is_file():
        return ReportResolverResult(
            result="BLOCKED",
            resolver_mode="explicit_path",
            report_path_provided=True,
            report_dir_provided=False,
            report_path=str(resolved),
            report_name=resolved.name,
            report_exists=True,
            report_is_file=False,
            report_size_bytes=0,
            report_sha256="",
            report_mtime_utc="",
            candidate_count=1,
            candidate_names=(resolved.name,),
            latest_selected=False,
            report_preview="",
            failure_layer=DEFAULT_FAILURE_LAYER,
            error=f"Report path is not a file: {resolved}",
        )
    return _build_success(resolved, mode="explicit_path", latest_selected=False, candidate_names=(resolved.name,))


def _resolve_latest_in_dir(report_dir: Path, *, prefix: str = "", glob_pattern: str = DEFAULT_REPORT_GLOB) -> ReportResolverResult:
    resolved_dir = report_dir.resolve()
    if not resolved_dir.exists():
        return _blocked(
            mode="latest_in_dir",
            report_path_provided=False,
            report_dir_provided=True,
            error=f"Report directory does not exist: {resolved_dir}",
        )
    if not resolved_dir.is_dir():
        return _blocked(
            mode="latest_in_dir",
            report_path_provided=False,
            report_dir_provided=True,
            error=f"Report directory is not a directory: {resolved_dir}",
        )

    candidates = tuple(_iter_report_candidates(resolved_dir, prefix=prefix, glob_pattern=glob_pattern))
    candidate_names = tuple(sorted(path.name for path in candidates))
    if not candidates:
        return _blocked(
            mode="latest_in_dir",
            report_path_provided=False,
            report_dir_provided=True,
            error="No matching report files were found.",
            candidate_count=0,
            candidate_names=(),
        )
    selected = sorted(candidates, key=_candidate_sort_key)[-1]
    return _build_success(
        selected.resolve(),
        mode="latest_in_dir",
        latest_selected=True,
        candidate_names=candidate_names,
    )


def _build_success(path: Path, *, mode: str, latest_selected: bool, candidate_names: tuple[str, ...]) -> ReportResolverResult:
    data = path.read_bytes()
    stat = path.stat()
    try:
        from datetime import datetime, timezone
        mtime_utc = datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()
    except Exception:
        mtime_utc = ""
    preview = _safe_preview(data[:2048].decode("utf-8", errors="replace"))
    return ReportResolverResult(
        result="PASS",
        resolver_mode=mode,
        report_path_provided=mode == "explicit_path",
        report_dir_provided=mode == "latest_in_dir",
        report_path=str(path),
        report_name=path.name,
        report_exists=True,
        report_is_file=True,
        report_size_bytes=len(data),
        report_sha256=_sha256_bytes(data),
        report_mtime_utc=mtime_utc,
        candidate_count=len(candidate_names),
        candidate_names=candidate_names,
        latest_selected=latest_selected,
        report_preview=preview,
        failure_layer="",
        error="",
    )


def write_resolver_outputs(result: ReportResolverResult, output_dir: str | os.PathLike[str]) -> dict[str, str]:
    target = Path(output_dir).resolve()
    target.mkdir(parents=True, exist_ok=True)
    payload = result.to_payload()
    json_path = target / "chatgpt_uploader_report_resolver.json"
    txt_path = target / "chatgpt_uploader_report_resolver.txt"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    txt_path.write_text(render_text_summary(result), encoding="utf-8")
    return {"json_path": str(json_path), "txt_path": str(txt_path)}


def render_text_summary(result: ReportResolverResult) -> str:
    lines = [
        "PATCHOPS CHATGPT UPLOADER REPORT RESOLVER",
        "==========================================",
        f"Result                    : {result.result}",
        f"Resolver Mode             : {result.resolver_mode}",
        f"Report Path Provided      : {str(result.report_path_provided).lower()}",
        f"Report Dir Provided       : {str(result.report_dir_provided).lower()}",
        f"Report Path               : {result.report_path}",
        f"Report Name               : {result.report_name}",
        f"Report Exists             : {str(result.report_exists).lower()}",
        f"Report Is File            : {str(result.report_is_file).lower()}",
        f"Report Size Bytes         : {result.report_size_bytes}",
        f"Report SHA256             : {result.report_sha256}",
        f"Report MTime UTC          : {result.report_mtime_utc}",
        f"Candidate Count           : {result.candidate_count}",
        f"Latest Selected           : {str(result.latest_selected).lower()}",
        f"Failure Layer             : {result.failure_layer}",
        f"Error                     : {result.error}",
        "",
        "SAFETY CHECKLIST",
        "----------------",
        f"webdriver_used            : {str(result.webdriver_used).lower()}",
        f"selenium_used             : {str(result.selenium_used).lower()}",
        f"browser_dom_automation_used: {str(result.browser_dom_automation_used).lower()}",
        f"cloudflare_bypass_attempted: {str(result.cloudflare_bypass_attempted).lower()}",
        f"captcha_bypass_attempted  : {str(result.captcha_bypass_attempted).lower()}",
        f"file_upload_attempted     : {str(result.file_upload_attempted).lower()}",
        f"chatgpt_submit_performed  : {str(result.chatgpt_submit_performed).lower()}",
        f"conversation_text_logged  : {str(result.conversation_text_logged).lower()}",
        f"random_page_click_performed: {str(result.random_page_click_performed).lower()}",
        "",
        "REPORT PREVIEW",
        "--------------",
        result.report_preview,
        "",
    ]
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Resolve the local canonical PatchOps report for ChatGPT uploader handoff.")
    parser.add_argument("--report-path", default="", help="Explicit PatchOps report path to resolve.")
    parser.add_argument("--report-dir", default="", help="Directory to scan for the latest report when --report-path is omitted.")
    parser.add_argument("--prefix", default="", help="Optional filename prefix filter for --report-dir scanning.")
    parser.add_argument("--glob", default=DEFAULT_REPORT_GLOB, help="Glob pattern for --report-dir scanning. Defaults to *.txt.")
    parser.add_argument("--output-dir", default="", help="Optional directory for JSON/TXT resolver outputs.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of text summary.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    result = resolve_report(
        report_path=args.report_path or None,
        report_dir=args.report_dir or None,
        prefix=args.prefix,
        glob_pattern=args.glob,
    )
    output_paths: dict[str, str] = {}
    if args.output_dir:
        output_paths = write_resolver_outputs(result, args.output_dir)
    payload = result.to_payload()
    if output_paths:
        payload["output_paths"] = output_paths
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text_summary(result))
        if output_paths:
            print("OUTPUTS")
            print("-------")
            for key, value in sorted(output_paths.items()):
                print(f"{key}: {value}")
    return 0 if result.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
