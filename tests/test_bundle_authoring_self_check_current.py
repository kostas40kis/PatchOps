from __future__ import annotations

import json
from pathlib import Path

from patchops.bundles.authoring import (
    create_starter_bundle,
    run_bundle_authoring_self_check,
)
from patchops.bundles.shape_validation import BundleShapeIssue


def _launcher_issue(path: Path) -> list[BundleShapeIssue]:
    return [
        BundleShapeIssue(
            code="launcher_risky",
            message="Launcher contains a risky pattern for bundle authoring.",
            path=str(path),
        )
    ]


def test_run_bundle_authoring_self_check_accepts_clean_starter_bundle(tmp_path: Path) -> None:
    authored = create_starter_bundle(
        tmp_path / "starter_bundle",
        patch_name="zp03_starter",
        target_project="patchops",
        target_project_root=r"C:\dev\patchops",
    )

    result = run_bundle_authoring_self_check(
        authored.bundle_root,
        launcher_checker=lambda path: [],
    )

    assert result.bundle_root == authored.bundle_root
    assert result.is_valid is True
    assert result.issue_count == 0
    assert result.messages == ()


def test_run_bundle_authoring_self_check_merges_shape_and_launcher_messages(tmp_path: Path) -> None:
    root = tmp_path / "broken_bundle"
    root.mkdir(parents=True, exist_ok=True)
    (root / "manifest.json").write_text("{}", encoding="utf-8")
    (root / "bundle_meta.json").write_text("{}", encoding="utf-8")
    (root / "run_with_patchops.ps1").write_text("param()\n", encoding="utf-8")

    result = run_bundle_authoring_self_check(
        root,
        launcher_checker=_launcher_issue,
    )

    codes = {message.code for message in result.messages}
    assert "missing_content_root" in codes
    assert "launcher_risky" in codes
    assert result.is_valid is False


def test_run_bundle_authoring_self_check_reports_missing_manifest_content_path(tmp_path: Path) -> None:
    authored = create_starter_bundle(
        tmp_path / "missing_content_bundle",
        patch_name="zp03_missing_content",
        target_project="patchops",
        target_project_root=r"C:\dev\patchops",
    )

    manifest = json.loads(authored.manifest_path.read_text(encoding="utf-8"))
    manifest["files_to_write"] = [
        {
            "path": "docs/example.md",
            "content": None,
            "content_path": "content/docs/example.md",
            "encoding": "utf-8",
        }
    ]
    authored.manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    result = run_bundle_authoring_self_check(
        authored.bundle_root,
        launcher_checker=lambda path: [],
    )

    codes = {message.code for message in result.messages}
    assert "content_path_missing" in codes
    assert result.is_valid is False
