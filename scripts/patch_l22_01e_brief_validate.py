
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

AUTH_TOKEN = "PATCHOPS_L22_EDGE_DOWNLOADED_ARCHIVE_MANIFEST_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY"
MODULE_REL = "patchops/llm_browser/live_adapter_edge_downloaded_archive_manifest_validation_passive_preflight_apply_bypass.py"


def _load(repo_root: Path):
    path = repo_root / MODULE_REL
    spec = importlib.util.spec_from_file_location("l22_01e_manifest_preflight", path)
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
    default = module.build_manifest_validation_passive_preflight_apply_bypass(root)
    authorized = module.build_manifest_validation_passive_preflight_apply_bypass(root, allow_manifest_validation_preflight=True, authorization_token=AUTH_TOKEN)
    false_fields = getattr(module, "FALSE_FIELDS")
    ok = (
        default.get("ok") is True
        and authorized.get("ok") is True
        and default.get("manifest_validation_preflight_authorized") is False
        and authorized.get("manifest_validation_preflight_authorized") is True
        and all(default.get(field) is False for field in false_fields)
        and all(authorized.get(field) is False for field in false_fields)
        and authorized.get("next_patch") == "L22.2 Microsoft Edge downloaded-archive manifest validation CLI/readback checkpoint"
    )
    summary = {
        "ok": ok,
        "patch": authorized.get("patch"),
        "default_authorized": default.get("manifest_validation_preflight_authorized"),
        "authorized_authorized": authorized.get("manifest_validation_preflight_authorized"),
        "manifest_read": authorized.get("downloaded_manifest_read"),
        "member_bytes_read": authorized.get("downloaded_archive_member_bytes_read"),
        "browser_started": authorized.get("browser_started"),
        "package_run": authorized.get("package_run_performed_by_adapter"),
        "next_patch": authorized.get("next_patch"),
    }
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
