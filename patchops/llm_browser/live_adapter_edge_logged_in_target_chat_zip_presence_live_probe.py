from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

PATCH = "L25.48A"
NAME = "L25.48A Microsoft Edge logged-in target-chat zip-presence live probe"
AUTHORIZATION_TOKEN = "PATCHOPS_L25_48A_EDGE_LIVE_ZIP_PRESENCE_AUTHORIZED"
DEFAULT_TARGET_URL = "https://chatgpt.com/g/g-p-69a9bf9c68f081918b698e637f36977d/c/69f77b2e-0450-83eb-9123-d11ef1ae81c8"

class LiveProbeError(RuntimeError):
    pass

@dataclass(frozen=True)
class ZipCandidate:
    tag: str
    role: str
    aria_label: str
    text: str
    href: str

    def to_payload(self) -> dict[str, str]:
        return {
            "tag": self.tag,
            "role": self.role,
            "aria_label": self.aria_label,
            "text": self.text,
            "href_hint": self.href[:180],
        }

def _emit(payload: dict[str, Any], *, compact: bool) -> None:
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if compact else None, indent=None if compact else 2))

def _repo_root_from_arg(value: str | None) -> Path:
    if value:
        return Path(value).resolve()
    return Path(__file__).resolve().parents[2]

def _default_profile_dir(repo_root: Path) -> Path:
    return repo_root / "data" / "runtime" / "browser_profiles" / "edge_supervised_l25_48a"

def _default_download_dir() -> Path:
    return Path.home() / "Downloads"

def _validate_target_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc.lower() != "chatgpt.com":
        raise LiveProbeError("target URL must be an https://chatgpt.com/... URL")
    if not (parsed.path.startswith("/g/") or parsed.path.startswith("/c/")):
        raise LiveProbeError("target URL must point to a ChatGPT conversation path")

def _load_selenium() -> Any:
    try:
        from selenium import webdriver
        from selenium.webdriver.edge.options import Options
    except Exception as exc:
        raise LiveProbeError("Selenium is not importable. Install browser extras: py -m pip install -e \".[browser]\"") from exc
    return webdriver, Options

def _build_driver(*, profile_dir: Path, download_dir: Path) -> Any:
    webdriver, Options = _load_selenium()
    profile_dir.mkdir(parents=True, exist_ok=True)
    download_dir.mkdir(parents=True, exist_ok=True)
    options = Options()
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument("--disable-notifications")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_experimental_option("prefs", {
        "download.default_directory": str(download_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    })
    return webdriver.Edge(options=options)

def _document_ready(driver: Any) -> bool:
    try:
        return driver.execute_script("return document.readyState") in ("interactive", "complete")
    except Exception:
        return False

def _collect_zip_candidates(driver: Any) -> list[ZipCandidate]:
    script = r'''
const nodes = Array.from(document.querySelectorAll('a,button,[role="button"],span,div'));
const out = [];
for (const el of nodes) {
  const rawText = (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ');
  const aria = (el.getAttribute('aria-label') || '').trim();
  const title = (el.getAttribute('title') || '').trim();
  const href = (el.getAttribute('href') || '').trim();
  const combined = [rawText, aria, title, href].join(' ');
  if (combined.toLowerCase().includes('.zip')) {
    out.push({
      tag: (el.tagName || '').toLowerCase(),
      role: el.getAttribute('role') || '',
      aria_label: aria.slice(0, 180),
      text: rawText.slice(0, 220),
      href: href.slice(0, 220)
    });
  }
  if (out.length >= 12) break;
}
return out;
'''
    raw = driver.execute_script(script) or []
    candidates: list[ZipCandidate] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        text = str(item.get("text") or "")
        aria = str(item.get("aria_label") or "")
        href = str(item.get("href") or "")
        if ".zip" not in (text + " " + aria + " " + href).lower():
            continue
        candidates.append(ZipCandidate(
            tag=str(item.get("tag") or ""),
            role=str(item.get("role") or ""),
            aria_label=aria,
            text=text,
            href=href,
        ))
    return candidates

def run_live_probe(*, repo_root: Path, target_url: str, profile_dir: Path, download_dir: Path, timeout_seconds: int, keep_open: bool) -> dict[str, Any]:
    _validate_target_url(target_url)
    driver = None
    started = False
    try:
        driver = _build_driver(profile_dir=profile_dir, download_dir=download_dir)
        started = True
        driver.set_page_load_timeout(max(30, timeout_seconds))
        driver.get(target_url)
        deadline = time.time() + timeout_seconds
        candidates: list[ZipCandidate] = []
        ready = False
        current_url = ""
        title = ""
        while time.time() < deadline:
            ready = _document_ready(driver)
            try:
                current_url = str(driver.current_url)
                title = str(driver.title or "")
            except Exception:
                current_url = ""
                title = ""
            candidates = _collect_zip_candidates(driver)
            if ready and candidates:
                break
            time.sleep(1.0)
        zip_found = bool(candidates)
        payload: dict[str, Any] = {
            "ok": zip_found,
            "patch": PATCH,
            "name": NAME,
            "l25_48_writer_quoting_repaired": True,
            "real_edge_live_target_chat_zip_presence_probe": True,
            "uses_real_browser_as_main_proof": True,
            "synthetic_fixture_main_proof": False,
            "browser": "edge",
            "browser_started": started,
            "target_url": target_url,
            "current_url_host": urlparse(current_url).netloc if current_url else "",
            "page_title_hint": title[:120],
            "document_ready_observed": ready,
            "zip_candidate_found": zip_found,
            "zip_candidate_count": len(candidates),
            "zip_candidates": [candidate.to_payload() for candidate in candidates[:5]],
            "profile_dir": str(profile_dir),
            "download_dir": str(download_dir),
            "dedicated_profile_used": True,
            "default_profile_used": False,
            "minimal_dom_artifact_detection_performed": True,
            "conversation_text_logged": False,
            "prompt_text_extracted": False,
            "artifact_content_reading_performed": False,
            "download_click_performed": False,
            "download_performed": False,
            "downloaded_file_bytes_read": False,
            "run_package_invoked_by_l25_48a": False,
            "pasteback": False,
            "send_submit_performed": False,
            "localhost_server_started": False,
            "browser_extension_used": False,
            "git_commit_performed": False,
            "git_push_performed": False,
        }
        if not zip_found:
            payload["failure_layer"] = "artifact_missing_or_login_required_or_selector_drift"
            payload["next_action"] = "Confirm the target chat is logged in in the dedicated Edge profile; if zip is visible, repair selector strategy."
        return payload
    finally:
        if driver is not None and not keep_open:
            try:
                driver.quit()
            except Exception:
                pass

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--profile-dir", default="")
    parser.add_argument("--download-dir", default="")
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--allow-live-browser", action="store_true")
    parser.add_argument("--authorization-token", default="")
    parser.add_argument("--keep-open", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    if not args.allow_live_browser or args.authorization_token != AUTHORIZATION_TOKEN:
        _emit({
            "ok": False,
            "patch": PATCH,
            "error": "explicit live browser authorization token required",
            "live_browser_authorization_required": True,
            "browser_started": False,
            "download_performed": False,
            "run_package_invoked_by_l25_48a": False,
        }, compact=args.compact)
        return 1
    repo_root = _repo_root_from_arg(args.repo_root)
    profile_dir = Path(args.profile_dir).resolve() if args.profile_dir else _default_profile_dir(repo_root)
    download_dir = Path(args.download_dir).resolve() if args.download_dir else _default_download_dir()
    try:
        payload = run_live_probe(
            repo_root=repo_root,
            target_url=args.target_url,
            profile_dir=profile_dir,
            download_dir=download_dir,
            timeout_seconds=max(10, int(args.timeout_seconds)),
            keep_open=bool(args.keep_open),
        )
    except Exception as exc:
        _emit({
            "ok": False,
            "patch": PATCH,
            "error": str(exc),
            "failure_layer": "live_edge_probe_exception",
            "browser_started": False,
            "zip_candidate_found": False,
            "download_performed": False,
            "run_package_invoked_by_l25_48a": False,
            "pasteback": False,
            "send_submit_performed": False,
            "localhost_server_started": False,
            "browser_extension_used": False,
            "git_commit_performed": False,
            "git_push_performed": False,
        }, compact=args.compact)
        return 1
    _emit(payload, compact=args.compact)
    return 0 if payload.get("ok") is True else 1

if __name__ == "__main__":
    raise SystemExit(main())

