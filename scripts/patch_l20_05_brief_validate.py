from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT_TEXT = str(_REPO_ROOT)
if _REPO_ROOT_TEXT not in sys.path:
    sys.path.insert(0, _REPO_ROOT_TEXT)

from patchops.llm_browser import live_adapter_edge_downloaded_file_filesystem_validation_existence_proof as l20_05


def _ensure_fixture(repo_root: Path) -> Path:
    fixture = repo_root / l20_05.DEFAULT_CANDIDATE_RELATIVE_PATH
    fixture.parent.mkdir(parents=True, exist_ok=True)
    if not fixture.exists():
        fixture.write_text("L20.5 synthetic existence-only fixture. Do not read contents.\n", encoding="utf-8")
    return fixture


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Brief L20.5 validation")
    parser.add_argument("--repo-root", default=str(_REPO_ROOT))
    parser.add_argument("--target-url", default="https://chatgpt.com/")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    _ensure_fixture(repo_root)
    default_payload = l20_05.build_edge_downloaded_file_filesystem_validation_existence_proof(
        repo_root,
        target_url=args.target_url,
    )
    authorized_payload = l20_05.build_edge_downloaded_file_filesystem_validation_existence_proof(
        repo_root,
        allow_filesystem_existence_proof=True,
        authorization_token=l20_05.REQUIRED_FILESYSTEM_EXISTENCE_PROOF_AUTHORIZATION_TOKEN,
        candidate_path_metadata=l20_05.DEFAULT_CANDIDATE_RELATIVE_PATH,
        target_url=args.target_url,
    )
    result = authorized_payload.get("existence_validation_result") or {}
    ok = (
        default_payload.get("ok") is True
        and authorized_payload.get("ok") is True
        and default_payload.get("filesystem_existence_proof_authorized") is False
        and default_payload.get("real_file_exists_check_performed") is False
        and authorized_payload.get("filesystem_existence_proof_authorized") is True
        and authorized_payload.get("filesystem_validation_performed") is True
        and authorized_payload.get("real_file_exists_check_performed") is True
        and authorized_payload.get("downloaded_file_exists_check_performed") is True
        and result.get("candidate_exists") is True
        and authorized_payload.get("real_file_stat_performed") is False
        and authorized_payload.get("real_file_hash_performed") is False
        and authorized_payload.get("downloaded_file_stat_performed") is False
        and authorized_payload.get("downloaded_file_hash_performed") is False
        and authorized_payload.get("downloaded_file_bytes_read") is False
        and authorized_payload.get("downloaded_archive_opened") is False
        and authorized_payload.get("downloaded_manifest_read") is False
        and authorized_payload.get("browser_started") is False
        and authorized_payload.get("edge_process_started") is False
    )
    summary = {
        "ok": ok,
        "patch": authorized_payload.get("patch"),
        "source_patch": authorized_payload.get("source_patch"),
        "source_l20_4_controlled_authorization_gate_accepted": authorized_payload.get("source_l20_4_controlled_authorization_gate_accepted"),
        "l20_4_complete": authorized_payload.get("l20_4_complete"),
        "default_filesystem_existence_proof_authorized": default_payload.get("filesystem_existence_proof_authorized"),
        "authorized_filesystem_existence_proof_authorized": authorized_payload.get("filesystem_existence_proof_authorized"),
        "candidate_safe_for_l20_5_existence_only_proof": (authorized_payload.get("candidate_safety") or {}).get("candidate_safe_for_l20_5_existence_only_proof"),
        "existence_only_validation_performed": result.get("existence_only_validation_performed"),
        "candidate_exists": result.get("candidate_exists"),
        "filesystem_validation_performed": authorized_payload.get("filesystem_validation_performed"),
        "real_file_exists_check_performed": authorized_payload.get("real_file_exists_check_performed"),
        "downloaded_file_exists_check_performed": authorized_payload.get("downloaded_file_exists_check_performed"),
        "real_file_stat_performed": authorized_payload.get("real_file_stat_performed"),
        "real_file_hash_performed": authorized_payload.get("real_file_hash_performed"),
        "downloaded_file_stat_performed": authorized_payload.get("downloaded_file_stat_performed"),
        "downloaded_file_hash_performed": authorized_payload.get("downloaded_file_hash_performed"),
        "downloaded_file_bytes_read": authorized_payload.get("downloaded_file_bytes_read"),
        "downloaded_archive_opened": authorized_payload.get("downloaded_archive_opened"),
        "downloaded_manifest_read": authorized_payload.get("downloaded_manifest_read"),
        "browser_started": authorized_payload.get("browser_started"),
        "edge_process_started": authorized_payload.get("edge_process_started"),
        "chatgpt_url_opened": authorized_payload.get("chatgpt_url_opened"),
        "package_run_performed_by_adapter": authorized_payload.get("package_run_performed_by_adapter"),
        "missing_commands": authorized_payload.get("missing_commands"),
        "missing_doc_phrases": authorized_payload.get("missing_doc_phrases"),
        "required_repo_paths_ok": (authorized_payload.get("required_repo_paths") or {}).get("ok"),
        "next_patch": authorized_payload.get("next_patch"),
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
