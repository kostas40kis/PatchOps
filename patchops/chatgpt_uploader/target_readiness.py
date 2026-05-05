from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit


REQUESTED_TARGET_URL_ENV = "PATCHOPS_CHATGPT_UPLOADER_TARGET_URL"
DEFAULT_FAILURE_LAYER = "target_readiness_probe"
CHATGPT_HOST_SUFFIX = "chatgpt.com"
_CONVERSATION_ID_RE = re.compile(r"/c/([0-9a-fA-F-]{16,})")


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def _normalise_url(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    parts = urlsplit(raw)
    if not parts.scheme:
        parts = urlsplit("https://" + raw)
    scheme = (parts.scheme or "https").lower()
    netloc = parts.netloc.lower()
    path = parts.path or "/"
    return urlunsplit((scheme, netloc, path, "", ""))


def _redact_url(normalized_url: str) -> str:
    if not normalized_url:
        return ""
    parts = urlsplit(normalized_url)
    path = parts.path or "/"
    redacted_path = path
    match = _CONVERSATION_ID_RE.search(path)
    if match:
        redacted_path = path[: match.start(1)] + "<conversation_id>" + path[match.end(1) :]
    return urlunsplit((parts.scheme, parts.netloc, redacted_path, "", ""))


def _host_is_chatgpt(host: str) -> bool:
    clean = host.lower().split(":", 1)[0]
    return clean == CHATGPT_HOST_SUFFIX or clean.endswith("." + CHATGPT_HOST_SUFFIX)


@dataclass(frozen=True)
class TargetReadinessProbeResult:
    result: str
    target_url_provided: bool
    target_url_hash: str
    target_url_redacted: str
    target_url_host: str
    target_url_is_chatgpt: bool
    target_url_has_conversation_id: bool
    target_url_has_project_g_path: bool
    safe_target_url: bool
    target_probe_performed: bool
    network_request_performed: bool
    pywinauto_probe_requested: bool
    pywinauto_imported: bool
    edge_window_probe_attempted: bool
    normal_edge_window_detected: bool
    edge_window_title_redacted: str
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
    canonical_report_found: bool = False

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def _redact_window_title(title: str) -> str:
    clean = " ".join(str(title or "").split())
    if not clean:
        return ""
    lowered = clean.lower()
    if "chatgpt" in lowered:
        return "<normal_edge_title_contains_chatgpt>"
    if "edge" in lowered or "microsoft" in lowered:
        return "<normal_edge_title>"
    return "<window_title_redacted>"


def _try_pywinauto_edge_probe() -> tuple[bool, bool, str, str]:
    """Return (imported, detected, redacted_title, error)."""
    try:
        from pywinauto import Desktop  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on operator machine
        return False, False, "", f"pywinauto_unavailable:{exc.__class__.__name__}: {exc}"

    try:
        desktop = Desktop(backend="uia")
        for window in desktop.windows():
            title = ""
            try:
                title = str(window.window_text() or "")
            except Exception:
                title = ""
            lowered = title.lower()
            if "edge" in lowered or "chatgpt" in lowered:
                return True, True, _redact_window_title(title), ""
        return True, False, "", "normal_edge_window_not_detected"
    except Exception as exc:  # pragma: no cover - depends on operator machine
        return True, False, "", f"pywinauto_probe_failed:{exc.__class__.__name__}: {exc}"


def probe_target_readiness(
    *,
    target_url: str | None = None,
    output_dir: str | Path | None = None,
    allow_pywinauto_probe: bool = False,
) -> TargetReadinessProbeResult:
    raw_url = target_url if target_url is not None else os.environ.get(REQUESTED_TARGET_URL_ENV, "")
    normalized = _normalise_url(raw_url or "")
    parts = urlsplit(normalized) if normalized else None
    host = parts.netloc if parts is not None else ""
    path = parts.path if parts is not None else ""
    provided = bool(str(raw_url or "").strip())
    is_chatgpt = bool(parts is not None and parts.scheme in {"http", "https"} and _host_is_chatgpt(host))
    has_conversation = bool(_CONVERSATION_ID_RE.search(path))
    has_project_g_path = "/g/" in path
    safe_target = bool(provided and is_chatgpt and has_conversation)

    py_imported = False
    edge_attempted = False
    edge_detected = False
    title_redacted = ""
    probe_error = ""

    if allow_pywinauto_probe:
        edge_attempted = True
        py_imported, edge_detected, title_redacted, probe_error = _try_pywinauto_edge_probe()

    error = ""
    result = "PASS"
    failure_layer = ""
    if not provided:
        result = "BLOCKED"
        failure_layer = DEFAULT_FAILURE_LAYER
        error = "target_url_missing"
    elif not is_chatgpt:
        result = "BLOCKED"
        failure_layer = DEFAULT_FAILURE_LAYER
        error = "target_url_not_chatgpt"
    elif not has_conversation:
        result = "BLOCKED"
        failure_layer = DEFAULT_FAILURE_LAYER
        error = "target_url_missing_conversation_id"
    elif allow_pywinauto_probe and probe_error and not edge_detected:
        # The URL is still safe, but the optional local session diagnostic is not ready.
        result = "BLOCKED"
        failure_layer = "normal_edge_session_probe"
        error = probe_error

    probe_result = TargetReadinessProbeResult(
        result=result,
        target_url_provided=provided,
        target_url_hash=_sha256_text(normalized) if normalized else "",
        target_url_redacted=_redact_url(normalized),
        target_url_host=host,
        target_url_is_chatgpt=is_chatgpt,
        target_url_has_conversation_id=has_conversation,
        target_url_has_project_g_path=has_project_g_path,
        safe_target_url=safe_target,
        target_probe_performed=True,
        network_request_performed=False,
        pywinauto_probe_requested=allow_pywinauto_probe,
        pywinauto_imported=py_imported,
        edge_window_probe_attempted=edge_attempted,
        normal_edge_window_detected=edge_detected,
        edge_window_title_redacted=title_redacted,
        failure_layer=failure_layer,
        error=error,
    )

    if output_dir is not None:
        write_probe_artifacts(Path(output_dir), probe_result)

    return probe_result


def write_probe_artifacts(output_dir: Path, result: TargetReadinessProbeResult) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = result.to_payload()
    json_path = output_dir / "chatgpt_uploader_target_readiness_probe.json"
    report_path = output_dir / "chatgpt_uploader_target_readiness_probe.txt"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "PATCHOPS CHATGPT UPLOADER TARGET READINESS PROBE",
        "================================================",
        f"Result                         : {result.result}",
        f"Target URL Provided            : {result.target_url_provided}",
        f"Target URL Host                : {result.target_url_host}",
        f"Target URL Redacted            : {result.target_url_redacted}",
        f"Target URL Hash                : {result.target_url_hash}",
        f"Target URL Is ChatGPT          : {result.target_url_is_chatgpt}",
        f"Target URL Has Conversation ID : {result.target_url_has_conversation_id}",
        f"Target URL Has Project Path    : {result.target_url_has_project_g_path}",
        f"Safe Target URL                : {result.safe_target_url}",
        f"Network Request Performed      : {result.network_request_performed}",
        f"Pywinauto Probe Requested      : {result.pywinauto_probe_requested}",
        f"Pywinauto Imported             : {result.pywinauto_imported}",
        f"Edge Window Probe Attempted    : {result.edge_window_probe_attempted}",
        f"Normal Edge Window Detected    : {result.normal_edge_window_detected}",
        f"Edge Window Title Redacted     : {result.edge_window_title_redacted}",
        "",
        "SAFETY CHECKLIST",
        "================",
        f"webdriver_used                 : {result.webdriver_used}",
        f"selenium_used                  : {result.selenium_used}",
        f"browser_dom_automation_used    : {result.browser_dom_automation_used}",
        f"cloudflare_bypass_attempted    : {result.cloudflare_bypass_attempted}",
        f"captcha_bypass_attempted       : {result.captcha_bypass_attempted}",
        f"file_upload_attempted          : {result.file_upload_attempted}",
        f"chatgpt_submit_performed       : {result.chatgpt_submit_performed}",
        f"conversation_text_logged       : {result.conversation_text_logged}",
        f"random_page_click_performed    : {result.random_page_click_performed}",
        f"canonical_report_found         : {result.canonical_report_found}",
        "",
        f"Failure Layer                  : {result.failure_layer}",
        f"Error                          : {result.error}",
        "",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return {"json": json_path, "report": report_path}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m patchops.chatgpt_uploader.target_readiness")
    parser.add_argument("--target-url", default=None, help="Configured ChatGPT target URL to inspect without navigation.")
    parser.add_argument("--output-dir", default=None, help="Optional directory for JSON/text probe artifacts.")
    parser.add_argument(
        "--allow-pywinauto-probe",
        action="store_true",
        help="Allow safe local normal-Edge window diagnostics. Does not click, upload, send, or navigate.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON payload.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = probe_target_readiness(
        target_url=args.target_url,
        output_dir=args.output_dir,
        allow_pywinauto_probe=bool(args.allow_pywinauto_probe),
    )
    if args.json:
        print(json.dumps(result.to_payload(), indent=2, sort_keys=True))
    else:
        print(f"Result: {result.result}")
        print(f"Safe Target URL: {result.safe_target_url}")
        if result.error:
            print(f"Error: {result.error}")
    return 0 if result.result == "PASS" else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
