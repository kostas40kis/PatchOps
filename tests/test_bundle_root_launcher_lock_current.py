from __future__ import annotations

import json
from pathlib import Path

from patchops.bundles.authoring import create_starter_bundle, run_bundle_authoring_self_check
from patchops.bundles.launcher_emitter import ROOT_BUNDLE_LAUNCHER_NAME, resolve_root_bundle_launcher_path


def test_create_starter_bundle_locks_root_launcher_filename_and_metadata_path() -> None:
    bundle = create_starter_bundle(
        Path.cwd() / 'data' / 'runtime' / 'bundle_lock_tmp' / 'starter_root_lock',
        patch_name='zp45a_root_lock',
        target_project='patchops',
        target_project_root='C:/dev/patchops',
    )

    meta = json.loads(bundle.bundle_meta_path.read_text(encoding='utf-8'))

    assert bundle.launcher_path.name == ROOT_BUNDLE_LAUNCHER_NAME
    assert bundle.launcher_path == bundle.bundle_root / ROOT_BUNDLE_LAUNCHER_NAME
    assert meta['launcher_path'] == ROOT_BUNDLE_LAUNCHER_NAME
    assert resolve_root_bundle_launcher_path(bundle.bundle_root) == bundle.bundle_root / ROOT_BUNDLE_LAUNCHER_NAME


def test_create_starter_bundle_does_not_emit_legacy_launcher_directory_by_default(tmp_path: Path) -> None:
    bundle = create_starter_bundle(
        tmp_path / 'starter_bundle',
        patch_name='zp45a_no_legacy_dir',
        target_project='patchops',
        target_project_root='C:/dev/patchops',
    )

    assert (bundle.bundle_root / ROOT_BUNDLE_LAUNCHER_NAME).exists()
    assert not (bundle.bundle_root / 'launchers').exists()


def test_authoring_self_check_fails_when_root_launcher_is_moved_under_launchers_folder(tmp_path: Path) -> None:
    bundle = create_starter_bundle(
        tmp_path / 'misplaced_launcher_bundle',
        patch_name='zp45a_misplaced_launcher',
        target_project='patchops',
        target_project_root='C:/dev/patchops',
    )

    legacy_dir = bundle.bundle_root / 'launchers'
    legacy_dir.mkdir(parents=True, exist_ok=True)
    misplaced = legacy_dir / ROOT_BUNDLE_LAUNCHER_NAME
    bundle.launcher_path.replace(misplaced)

    result = run_bundle_authoring_self_check(bundle.bundle_root)

    assert result.is_valid is False
    assert result.issue_count > 0


def test_authoring_self_check_recovers_when_root_launcher_is_restored(tmp_path: Path) -> None:
    bundle = create_starter_bundle(
        tmp_path / 'restored_launcher_bundle',
        patch_name='zp45a_restore_launcher',
        target_project='patchops',
        target_project_root='C:/dev/patchops',
    )

    legacy_dir = bundle.bundle_root / 'launchers'
    legacy_dir.mkdir(parents=True, exist_ok=True)
    misplaced = legacy_dir / ROOT_BUNDLE_LAUNCHER_NAME
    bundle.launcher_path.replace(misplaced)
    misplaced.replace(bundle.bundle_root / ROOT_BUNDLE_LAUNCHER_NAME)

    result = run_bundle_authoring_self_check(bundle.bundle_root)

    assert result.is_valid is True
    assert result.issue_count == 0
