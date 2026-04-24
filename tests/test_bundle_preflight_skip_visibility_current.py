from __future__ import annotations

import json
from pathlib import Path
import zipfile

from patchops.bundle_review import check_bundle_payload


def _write_bundle(root: Path, *, advertised: bool) -> Path:
    bundle_root = root / ("advertised_bundle" if advertised else "legacy_bundle")
    (bundle_root / "content" / "docs").mkdir(parents=True)
    (bundle_root / "content" / "docs" / "note.md").write_text("hello\n", encoding="utf-8")
    (bundle_root / "run_with_patchops.ps1").write_text("& { Write-Host 'ok' }\n", encoding="utf-8")
    (bundle_root / "manifest.json").write_text(
        json.dumps(
            {
                "manifest_version": "1",
                "patch_name": "bundle_preflight_skip_visibility",
                "active_profile": "generic_python",
                "files_to_write": [],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    meta = {
        "schema_version": "1",
        "patch_name": "bundle_preflight_skip_visibility",
        "bundle_mode": "apply",
        "recommended_profile": "generic_python",
    }
    if advertised:
        meta.update(
            {
                "manifest_path": "manifest.json",
                "content_root": "content",
                "launcher_path": "run_with_patchops.ps1",
            }
        )

    (bundle_root / "bundle_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    zip_path = root / f"{bundle_root.name}.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for item in bundle_root.rglob("*"):
            if item.is_file():
                zf.write(item, item.relative_to(root).as_posix())

    return zip_path


def _warning_codes(payload: dict) -> set[str]:
    return {
        item.get("code")
        for item in payload.get("warnings", [])
        if isinstance(item, dict)
    }


def test_bundle_preflight_skip_is_visible_for_unadvertised_patchops_bundle(tmp_path: Path) -> None:
    zip_path = _write_bundle(tmp_path, advertised=False)

    payload = check_bundle_payload(zip_path)

    preflight = payload["canonical_staged_authoring_preflight"]
    assert preflight["checked"] is True
    assert preflight["looks_like_bundle"] is True
    assert preflight["preflight_skipped"] is True
    assert preflight["advertises_canonical_staged_authoring_contract"] is False
    assert "canonical_staged_authoring_preflight_skipped" in _warning_codes(payload)
    assert payload.get("warning_count", 0) >= 1


def test_bundle_preflight_skip_warning_is_not_added_when_contract_is_advertised(tmp_path: Path) -> None:
    zip_path = _write_bundle(tmp_path, advertised=True)

    payload = check_bundle_payload(zip_path)

    preflight = payload["canonical_staged_authoring_preflight"]
    assert preflight["checked"] is True
    assert preflight["looks_like_bundle"] is True
    assert preflight["preflight_skipped"] is False
    assert preflight["advertises_canonical_staged_authoring_contract"] is True
    assert "canonical_staged_authoring_preflight_skipped" not in _warning_codes(payload)


def test_bundle_preflight_skip_visibility_also_works_for_extracted_bundle_directory(tmp_path: Path) -> None:
    zip_path = _write_bundle(tmp_path, advertised=False)
    # check the extracted root, not the zip
    extracted_root = tmp_path / "legacy_bundle"

    payload = check_bundle_payload(extracted_root)

    assert payload["canonical_staged_authoring_preflight"]["preflight_skipped"] is True
    assert "canonical_staged_authoring_preflight_skipped" in _warning_codes(payload)
