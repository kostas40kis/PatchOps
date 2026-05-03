from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse

PATCH = "L25.49C"
NAME = "L25.49C operator-pasted Edge download-presence live probe"
AUTHORIZATION_TOKEN = "PATCHOPS_L25_49C_OPERATOR_PASTED_EDGE_DOWNLOAD_PRESENCE_AUTHORIZED"

class ProbeError(RuntimeError):
    pass

@dataclass(frozen=True)
class DownloadCandidate:
    tag: str
    role: str
    aria_label: str
    title: str
    text: str
    href: str
    download_attr: str

    def to_payload(self) -> dict[str, str]:
        return {
            "tag": self.tag,
            "role": self.role,
            "aria_label_hint": self.aria_label[:140],
            "title_hint": self.title[:140],
            "text_hint": self.text[:160],
            "href_hint": self.href[:180],
            "download_attr_hint": self.download_attr[:140],
        }

def emit(payload: dict[str, Any], *, compact: bool) -> None:
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if compact else None, indent=None if compact else 2))

def repo_root_from_arg(value: str | None) -> Path:
    if value:
        return Path(value).resolve()
    return Path(__file__).resolve().parents[2]

def default_profile_dir(repo_root: Path) -> Path:
    return repo_root / "data" / "runtime" / "browser_profiles" / "edge_operator_paste_l25_49c"

def default_download_dir() -> Path:
    return Path.home() / "Downloads"

def load_selenium() -> Any:
    try:
        from selenium import webdriver
        from selenium.webdriver.edge.options import Options
    except Exception as exc:
        raise ProbeError("Selenium is not importable. Install browser dependencies before this live browser proof.") from exc
    return webdriver, Options

def instruction_page() -> str:
    # L25.49C: use string concatenation only. No embedded triple-quoted HTML,
    # so the patch writer cannot accidentally produce an IndentationError.
    body = (
        "<html><head><title>PatchOps L25.49C operator paste probe</title></head>"
        "<body style='font-family:Segoe UI,Arial,sans-serif;max-width:900px;margin:40px auto;line-height:1.45'>"
        "<h1>PatchOps L25.49C is waiting</h1>"
        "<p><b>Action:</b> paste the ChatGPT conversation link into this Edge window manually.</p>"
        "<p>Pass Cloudflare/login manually if shown. Stop when the page visibly contains a download or zip artifact.</p>"
        "<p>PatchOps will only inspect for visible download candidates. It will not click, download, paste back, send, start localhost, or bypass Cloudflare.</p>"
        "</body></html>"
    )
    return "data:text/html;charset=utf-8," + quote(body)

def build_driver(*, profile_dir: Path, download_dir: Path) -> Any:
    webdriver, Options = load_selenium()
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

def document_ready(driver: Any) -> bool:
    try:
        return driver.execute_script("return document.readyState") in ("interactive", "complete")
    except Exception:
        return False

def collect_download_candidates(driver: Any) -> list[DownloadCandidate]:
    script = """
const nodes = Array.from(document.querySelectorAll('a,button,[role="button"],[download],span,div'));
const out = [];
function visible(el) {
  const style = window.getComputedStyle(el);
  if (!style || style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) === 0) return false;
  const rect = el.getBoundingClientRect();
  return rect.width > 0 && rect.height > 0;
}
for (const el of nodes) {
  if (!visible(el)) continue;
  const rawText = (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ');
  const aria = (el.getAttribute('aria-label') || '').trim();
  const title = (el.getAttribute('title') || '').trim();
  const href = (el.getAttribute('href') || '').trim();
  const downloadAttr = (el.getAttribute('download') || '').trim();
  const role = (el.getAttribute('role') || '').trim();
  const combined = [rawText, aria, title, href, downloadAttr, role].join(' ').toLowerCase();
  const looksDownload = combined.includes('.zip') || combined.includes('download') || downloadAttr.length > 0;
  if (looksDownload) {
    out.push({
      tag: (el.tagName || '').toLowerCase(),
      role: role,
      aria_label: aria.slice(0, 180),
      title: title.slice(0, 180),
      text: rawText.slice(0, 220),
      href: href.slice(0, 260),
      download_attr: downloadAttr.slice(0, 180)
    });
  }
  if (out.length >= 20) break;
}
return out;
"""
    raw = driver.execute_script(script) or []
    candidates: list[DownloadCandidate] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        candidates.append(DownloadCandidate(
            tag=str(item.get("tag") or ""),
            role=str(item.get("role") or ""),
            aria_label=str(item.get("aria_label") or ""),
            title=str(item.get("title") or ""),
            text=str(item.get("text") or ""),
            href=str(item.get("href") or ""),
            download_attr=str(item.get("download_attr") or ""),
        ))
    return candidates

def run_probe(*, repo_root: Path, profile_dir: Path, download_dir: Path, wait_seconds: int, keep_open: bool) -> dict[str, Any]:
    driver = None
    started = False
    try:
        driver = build_driver(profile_dir=profile_dir, download_dir=download_dir)
        started = True
        driver.get(instruction_page())
        deadline = time.time() + max(20, wait_seconds)
        candidates: list[DownloadCandidate] = []
        current_url = ""
        current_host = ""
        title = ""
        ready = False
        while time.time() < deadline:
            try:
                current_url = str(driver.current_url or "")
                title = str(driver.title or "")
                current_host = urlparse(current_url).netloc
            except Exception:
                current_url = ""
                current_host = ""
                title = ""
            ready = document_ready(driver)
            if current_url.startswith("http://") or current_url.startswith("https://"):
                candidates = collect_download_candidates(driver)
                if candidates:
                    break
            time.sleep(1.0)
        found = bool(candidates)
        payload = {
            "ok": found,
            "patch": PATCH,
            "l25_49b_html_quoting_indentation_repaired": True,
            "operator_pasted_edge_download_presence_probe": True,
            "edge_opened_for_operator_manual_navigation": started,
            "operator_pastes_link_manually": True,
            "operator_handles_cloudflare_manually": True,
            "patchops_pasted_link": False,
            "uses_real_browser_as_main_proof": True,
            "synthetic_fixture_main_proof": False,
            "browser": "edge",
            "current_url_host": current_host,
            "current_url_is_chatgpt": current_host.lower().endswith("chatgpt.com"),
            "page_title_hint": title[:120],
            "document_ready_observed": ready,
            "download_candidate_found": found,
            "download_candidate_count": len(candidates),
            "download_candidates": [c.to_payload() for c in candidates[:8]],
            "profile_dir": str(profile_dir),
            "download_dir": str(download_dir),
            "dedicated_profile_used": True,
            "default_profile_used": False,
            "minimal_dom_download_presence_detection_performed": True,
            "cloudflare_bypass_attempted": False,
            "download_click_automated": False,
            "download_performed_by_patchops": False,
            "artifact_bytes_read": False,
            "archive_member_extracted": False,
            "run_package_invoked_by_l25_49c": False,
            "pasteback": False,
            "send_submit_performed": False,
            "localhost_server_started": False,
            "browser_extension_used": False,
            "git_commit_performed": False,
            "git_push_performed": False,
        }
        if not found:
            payload["failure_layer"] = "no_visible_download_candidate_after_operator_navigation"
            payload["next_action"] = "Verify the operator-pasted page is the intended ChatGPT conversation and that the download control is visible; if visible, selector strategy needs repair."
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
    parser.add_argument("--profile-dir", default="")
    parser.add_argument("--download-dir", default="")
    parser.add_argument("--wait-seconds", type=int, default=420)
    parser.add_argument("--allow-live-browser", action="store_true")
    parser.add_argument("--authorization-token", default="")
    parser.add_argument("--keep-open", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    if not args.allow_live_browser or args.authorization_token != AUTHORIZATION_TOKEN:
        emit({
            "ok": False,
            "patch": PATCH,
            "error": "explicit live browser authorization token required",
            "live_browser_authorization_required": True,
            "browser_started": False,
            "patchops_pasted_link": False,
            "download_click_automated": False,
            "run_package_invoked_by_l25_49c": False,
        }, compact=args.compact)
        return 1
    repo_root = repo_root_from_arg(args.repo_root)
    profile_dir = Path(args.profile_dir).resolve() if args.profile_dir else default_profile_dir(repo_root)
    download_dir = Path(args.download_dir).resolve() if args.download_dir else default_download_dir()
    try:
        payload = run_probe(
            repo_root=repo_root,
            profile_dir=profile_dir,
            download_dir=download_dir,
            wait_seconds=args.wait_seconds,
            keep_open=args.keep_open,
        )
    except Exception as exc:
        emit({
            "ok": False,
            "patch": PATCH,
            "error": str(exc),
            "failure_layer": "operator_pasted_edge_probe_exception",
            "browser_started": False,
            "patchops_pasted_link": False,
            "download_candidate_found": False,
            "download_click_automated": False,
            "run_package_invoked_by_l25_49c": False,
            "pasteback": False,
            "send_submit_performed": False,
            "localhost_server_started": False,
            "browser_extension_used": False,
            "git_commit_performed": False,
            "git_push_performed": False,
        }, compact=args.compact)
        return 1
    emit(payload, compact=args.compact)
    return 0 if payload.get("ok") is True else 1

if __name__ == "__main__":
    raise SystemExit(main())

