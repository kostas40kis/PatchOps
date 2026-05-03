
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

MODULE_REL = "patchops/llm_browser/live_adapter_edge_downloaded_archive_manifest_validation_cli_readback_apply_bypass.py"


def _load(repo_root: Path):
    path = repo_root / MODULE_REL
    spec = importlib.util.spec_from_file_location("l22_02_manifest_cli", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()
    module = _load(root)
    payload = module.build_manifest_validation_cli_readback_apply_bypass(root)
    false_fields = getattr(module, "FALSE_FIELDS")
    ok = (
        payload.get("ok") is True
        and payload.get("patch") == "L22.2"
        and payload.get("l22_1e_marker_accepted") is True
        and payload.get("default_manifest_preflight_readback_ok") is True
        and payload.get("authorized_manifest_preflight_readback_ok") is True
        and payload.get("default_manifest_validation_preflight_authorized") is False
        and payload.get("authorized_manifest_validation_preflight_authorized") is True
        and all(payload.get(field) is False for field in false_fields)
        and payload.get("next_patch") == "L22.3 Microsoft Edge downloaded-archive manifest validation passive plan checkpoint"
    )
    summary = {
        "ok": ok,
        "patch": payload.get("patch"),
        "l22_1e_marker_accepted": payload.get("l22_1e_marker_accepted"),
        "default_readback_ok": payload.get("default_manifest_preflight_readback_ok"),
        "authorized_readback_ok": payload.get("authorized_manifest_preflight_readback_ok"),
        "manifest_read": payload.get("downloaded_manifest_read"),
        "member_bytes_read": payload.get("downloaded_archive_member_bytes_read"),
        "browser_started": payload.get("browser_started"),
        "package_run": payload.get("package_run_performed_by_adapter"),
        "next_patch": payload.get("next_patch"),
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
