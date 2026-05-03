from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT_TEXT = str(_REPO_ROOT)
if _REPO_ROOT_TEXT not in sys.path:
    sys.path.insert(0, _REPO_ROOT_TEXT)

from patchops.llm_browser import live_adapter_edge_downloaded_file_metadata_validation_proof as l19_05


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Brief L19.5 validation")
    parser.add_argument("--repo-root", default=str(_REPO_ROOT))
    parser.add_argument("--target-url", default="https://chatgpt.com/")
    args = parser.parse_args(argv)

    default_payload = l19_05.build_edge_downloaded_file_metadata_validation_proof(
        Path(args.repo_root).resolve(),
        target_url=args.target_url,
    )
    authorized_payload = l19_05.build_edge_downloaded_file_metadata_validation_proof(
        Path(args.repo_root).resolve(),
        allow_downloaded_file_metadata_validation_proof=True,
        authorization_token=l19_05.REQUIRED_METADATA_VALIDATION_PROOF_AUTHORIZATION_TOKEN,
        downloaded_file_metadata=l19_05.positive_downloaded_file_metadata_fixture(),
        target_url=args.target_url,
    )
    ok = (
        default_payload.get("ok") is True
        and authorized_payload.get("ok") is True
        and default_payload.get("downloaded_file_metadata_validation_classification_performed") is False
        and authorized_payload.get("downloaded_file_metadata_validation_proof_authorized") is True
        and authorized_payload.get("downloaded_file_metadata_validation_classification_performed") is True
        and authorized_payload.get("downloaded_file_metadata_validation_ready") is True
        and authorized_payload.get("downloaded_file_validation_execution_allowed") is False
        and authorized_payload.get("downloaded_file_validation_active") is False
        and authorized_payload.get("downloaded_file_validation_performed") is False
        and authorized_payload.get("downloaded_file_exists_check_performed") is False
        and authorized_payload.get("downloaded_file_stat_performed") is False
        and authorized_payload.get("downloaded_file_hash_performed") is False
        and authorized_payload.get("downloaded_file_bytes_read") is False
        and authorized_payload.get("downloaded_archive_opened") is False
        and authorized_payload.get("downloaded_archive_contents_listed") is False
        and authorized_payload.get("downloaded_archive_extracted") is False
        and authorized_payload.get("downloaded_manifest_read") is False
        and authorized_payload.get("browser_started") is False
        and authorized_payload.get("edge_process_started") is False
    )
    summary = {
        "ok": ok,
        "patch": authorized_payload.get("patch"),
        "source_patch": authorized_payload.get("source_patch"),
        "source_l19_4_controlled_authorization_gate_accepted": authorized_payload.get("source_l19_4_controlled_authorization_gate_accepted"),
        "l19_4_complete": authorized_payload.get("l19_4_complete"),
        "default_downloaded_file_metadata_validation_classification_performed": default_payload.get("downloaded_file_metadata_validation_classification_performed"),
        "authorized_downloaded_file_metadata_validation_proof_authorized": authorized_payload.get("downloaded_file_metadata_validation_proof_authorized"),
        "authorized_downloaded_file_metadata_validation_classification_performed": authorized_payload.get("downloaded_file_metadata_validation_classification_performed"),
        "downloaded_file_metadata_validation_ready": authorized_payload.get("downloaded_file_metadata_validation_ready"),
        "downloaded_file_metadata_validation_scope": authorized_payload.get("downloaded_file_metadata_validation_scope"),
        "downloaded_file_validation_execution_allowed": authorized_payload.get("downloaded_file_validation_execution_allowed"),
        "downloaded_file_validation_active": authorized_payload.get("downloaded_file_validation_active"),
        "downloaded_file_validation_performed": authorized_payload.get("downloaded_file_validation_performed"),
        "downloaded_file_exists_check_performed": authorized_payload.get("downloaded_file_exists_check_performed"),
        "downloaded_file_stat_performed": authorized_payload.get("downloaded_file_stat_performed"),
        "downloaded_file_hash_performed": authorized_payload.get("downloaded_file_hash_performed"),
        "downloaded_file_bytes_read": authorized_payload.get("downloaded_file_bytes_read"),
        "downloaded_archive_opened": authorized_payload.get("downloaded_archive_opened"),
        "downloaded_archive_contents_listed": authorized_payload.get("downloaded_archive_contents_listed"),
        "downloaded_archive_extracted": authorized_payload.get("downloaded_archive_extracted"),
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
