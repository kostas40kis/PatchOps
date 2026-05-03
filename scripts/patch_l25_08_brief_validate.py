from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.llm_browser import live_adapter_edge_real_archive_member_byte_read_first_controlled_proof as proof

FALSE_FIELDS = (
    "manifest_payload_read",
    "manifest_payload_bytes_read",
    "real_archive_manifest_read",
    "real_downloaded_manifest_read",
    "real_downloaded_artifact_read",
    "real_archive_candidate_extracted",
    "download_workflow_active",
    "download_workflow_execution_allowed",
    "real_browser_download_active",
    "browser_started",
    "edge_process_started",
    "browser_session_created",
    "selenium_imported",
    "cdp_used",
    "dom_scraping_used",
    "page_inspection_performed",
    "conversation_text_read",
    "prompt_text_extracted",
    "chatgpt_url_opened",
    "pasteback_workflow_active",
    "paste_performed",
    "send_or_submit_performed",
    "package_run_performed_by_adapter",
    "package_run",
    "localhost_server_started",
    "browser_extension_used",
    "git_commit_performed",
    "git_push_performed",
)

FORBIDDEN_IMPORT_MODULES = (
    "selenium",
    "webdriver_manager",
    "pyperclip",
    "psutil",
)

FORBIDDEN_ARCHIVE_CALL_SNIPPETS = (
    ".extract(",
    ".extractall(",
    ".open(",
    "testzip(",
    ".namelist(",
    ".infolist(",
)

TARGET_MEMBER = "bundle/run_with_patchops.ps1"
MANIFEST_MEMBER = "bundle/manifest.json"
TARGET_PAYLOAD = b"# synthetic launcher payload for L25.8 member-byte-read proof only\nWrite-Output 'L25.8 synthetic member'\n"
CONTROLLED_MEMBERS = {
    MANIFEST_MEMBER: b"{\"synthetic\":true,\"purpose\":\"member-byte-proof-manifest-not-read\"}\n",
    TARGET_MEMBER: TARGET_PAYLOAD,
}
EXPECTED_MEMBER_NAMES = sorted(CONTROLLED_MEMBERS)
EXPECTED_SHA256 = hashlib.sha256(TARGET_PAYLOAD).hexdigest()


def _assert(condition: bool, message: str, payload: dict[str, Any] | None = None) -> None:
    if not condition:
        if payload is not None:
            raise AssertionError(message + " :: " + json.dumps(payload, sort_keys=True, separators=(",", ":"))[:4000])
        raise AssertionError(message)


def _false_field_errors(payload: dict[str, Any]) -> list[str]:
    return [name for name in FALSE_FIELDS if payload.get(name) is not False]


def _forbidden_import_hits(source_text: str) -> list[str]:
    tree = ast.parse(source_text)
    hits: list[str] = []
    forbidden = set(FORBIDDEN_IMPORT_MODULES)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_name = alias.name.split(".", 1)[0]
                if root_name in forbidden:
                    hits.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            root_name = (node.module or "").split(".", 1)[0]
            if root_name in forbidden:
                hits.append(node.module or "")
    return sorted(set(hits))


def _archive_forbidden_call_hits(source_text: str) -> list[str]:
    return sorted(snippet for snippet in FORBIDDEN_ARCHIVE_CALL_SNIPPETS if snippet in source_text)


def _refresh_controlled_zip_fixture(root: Path) -> Path:
    candidate = root / proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    candidate.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(candidate, "w", compression=zipfile.ZIP_STORED) as archive:
        for name in EXPECTED_MEMBER_NAMES:
            archive.writestr(name, CONTROLLED_MEMBERS[name])
    return candidate


def build_validation_payload(repo_root: str | Path = REPO_ROOT) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    candidate = _refresh_controlled_zip_fixture(root)
    default_payload = proof.build_archive_member_byte_read_first_controlled_proof(root)
    authorized_payload = proof.build_archive_member_byte_read_first_controlled_proof(
        root,
        allow_archive_member_byte_read_proof=True,
        authorization_token=proof.REQUIRED_ARCHIVE_MEMBER_BYTE_READ_PROOF_TOKEN,
        candidate_archive_path=str(candidate),
        member_name=TARGET_MEMBER,
    )

    module_path = root / "patchops" / "llm_browser" / "live_adapter_edge_real_archive_member_byte_read_first_controlled_proof.py"
    doc_path = root / "docs" / "llm_browser_live_adapter_edge_real_archive_member_byte_read_first_controlled_proof.md"
    source_text = module_path.read_text(encoding="utf-8")
    doc_text = doc_path.read_text(encoding="utf-8")
    forbidden_import_hits = _forbidden_import_hits(source_text)
    forbidden_archive_call_hits = _archive_forbidden_call_hits(source_text)
    read_call_count = source_text.count(".read(")
    default_false_errors = _false_field_errors(default_payload)
    authorized_false_errors = _false_field_errors(authorized_payload)

    _assert(candidate.exists(), "controlled member-read zip fixture missing", authorized_payload)
    _assert(default_payload.get("ok") is True, "default payload is not ok", default_payload)
    _assert(default_payload.get("archive_member_bytes_read") is False, "default should not read member bytes", default_payload)
    _assert(authorized_payload.get("ok") is True, "authorized payload is not ok", authorized_payload)
    _assert(authorized_payload.get("patch") == "L25.8", "wrong patch marker", authorized_payload)
    _assert(authorized_payload.get("source_l25_07_summary", {}).get("ok") is True, "L25.7 source not ok", authorized_payload)
    _assert(authorized_payload.get("source_l25_07_summary", {}).get("future_member_byte_read_authorized") is True, "L25.7 future member-byte auth missing", authorized_payload)
    _assert(authorized_payload.get("source_l25_07_summary", {}).get("archive_member_bytes_read") is False, "L25.7 must not have read member bytes", authorized_payload)
    _assert(authorized_payload.get("archive_member_byte_read_allowed") is True, "member-byte read should be allowed", authorized_payload)
    _assert(authorized_payload.get("archive_member_bytes_read") is True, "member bytes should be read", authorized_payload)
    _assert(authorized_payload.get("archive_member_payload_read") is True, "member payload should be read", authorized_payload)
    _assert(authorized_payload.get("archive_member_payload_bytes_read") is True, "member payload bytes marker should be true", authorized_payload)
    _assert(authorized_payload.get("archive_member_payload_sha256_read") is True, "member payload sha256 marker should be true", authorized_payload)
    _assert(authorized_payload.get("archive_member_payload_byte_count") == len(TARGET_PAYLOAD), "member payload byte count mismatch", authorized_payload)
    _assert(authorized_payload.get("archive_member_payload_sha256") == EXPECTED_SHA256, "member payload sha256 mismatch", authorized_payload)
    _assert(authorized_payload.get("archive_member_name_read") == TARGET_MEMBER, "wrong member name read", authorized_payload)
    _assert(authorized_payload.get("archive_member_read_scope") == "controlled_runtime_non_manifest_member_bytes_only_no_manifest_payload", "wrong member-read scope", authorized_payload)
    _assert(authorized_payload.get("manifest_payload_read") is False, "manifest payload must remain false", authorized_payload)
    _assert(authorized_payload.get("real_archive_manifest_read") is False, "real archive manifest must remain false", authorized_payload)
    _assert(authorized_payload.get("real_archive_candidate_extracted") is False, "archive extraction must remain false", authorized_payload)
    _assert(authorized_payload.get("browser_started") is False, "browser must not start", authorized_payload)
    _assert(authorized_payload.get("package_run") is False, "package run must remain false", authorized_payload)
    _assert(authorized_payload.get("no_manifest_payload_read_added_by_l25_8") is True, "L25.8 should add no manifest payload read", authorized_payload)
    _assert(authorized_payload.get("no_archive_extraction_added_by_l25_8") is True, "L25.8 should add no extraction", authorized_payload)
    _assert(authorized_payload.get("no_browser_permission_added_by_l25_8") is True, "L25.8 should add no browser permission", authorized_payload)
    _assert(authorized_payload.get("no_pasteback_or_package_run_permission_added_by_l25_8") is True, "L25.8 should add no pasteback/package permission", authorized_payload)
    _assert(not default_false_errors, "default payload has non-false forbidden fields: " + ", ".join(default_false_errors), default_payload)
    _assert(not authorized_false_errors, "authorized payload has non-false forbidden fields: " + ", ".join(authorized_false_errors), authorized_payload)
    _assert(not forbidden_import_hits, "forbidden executable imports found: " + ", ".join(forbidden_import_hits), authorized_payload)
    _assert(not forbidden_archive_call_hits, "forbidden archive calls found: " + ", ".join(forbidden_archive_call_hits), authorized_payload)
    _assert(read_call_count == 1 and ".read(TARGET_CONTROLLED_MEMBER_NAME)" in source_text, "module must contain exactly one controlled archive read call", authorized_payload)
    _assert("read bytes from exactly one controlled non-manifest member" in doc_text, "doc missing member-byte proof boundary", authorized_payload)
    _assert("The manifest member `bundle/manifest.json` is not read" in doc_text, "doc missing manifest-not-read boundary", authorized_payload)
    _assert("Manifest payload is not read" in doc_text, "doc missing no manifest payload boundary", authorized_payload)
    _assert("No Microsoft Edge start" in doc_text, "doc missing no Edge start boundary", authorized_payload)
    _assert("No Selenium import" in doc_text, "doc missing no Selenium import boundary", authorized_payload)
    _assert("No click/download/archive-extract/manifest-payload-read/paste/send/package-run side effect" in doc_text, "doc missing side-effect boundary", authorized_payload)

    return {
        "ok": True,
        "patch": "L25.8",
        "fixture_refreshed": True,
        "fixture_member_names": EXPECTED_MEMBER_NAMES,
        "default_member_bytes_read": default_payload.get("archive_member_bytes_read"),
        "source_l25_07_ok": authorized_payload.get("source_l25_07_summary", {}).get("ok"),
        "source_l25_07_future_authorized": authorized_payload.get("source_l25_07_summary", {}).get("future_member_byte_read_authorized"),
        "member_byte_read_allowed": authorized_payload.get("archive_member_byte_read_allowed"),
        "archive_member_bytes_read": authorized_payload.get("archive_member_bytes_read"),
        "archive_member_payload_read": authorized_payload.get("archive_member_payload_read"),
        "archive_member_payload_bytes_read": authorized_payload.get("archive_member_payload_bytes_read"),
        "archive_member_payload_sha256_read": authorized_payload.get("archive_member_payload_sha256_read"),
        "archive_member_payload_byte_count": authorized_payload.get("archive_member_payload_byte_count"),
        "archive_member_payload_sha256_matches": authorized_payload.get("archive_member_payload_sha256") == EXPECTED_SHA256,
        "archive_member_name_read": authorized_payload.get("archive_member_name_read"),
        "archive_member_read_scope": authorized_payload.get("archive_member_read_scope"),
        "manifest_payload_read": authorized_payload.get("manifest_payload_read"),
        "real_archive_manifest_read": authorized_payload.get("real_archive_manifest_read"),
        "archive_extracted": authorized_payload.get("real_archive_candidate_extracted"),
        "browser_started": authorized_payload.get("browser_started"),
        "pasteback": authorized_payload.get("pasteback_workflow_active"),
        "package_run": authorized_payload.get("package_run"),
        "next_patch": authorized_payload.get("next_patch"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="L25.8 brief validator")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = build_validation_payload(args.repo_root)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
