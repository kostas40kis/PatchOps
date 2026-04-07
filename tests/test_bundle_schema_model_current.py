from __future__ import annotations

import json
from pathlib import Path

import pytest

from patchops.bundles import (
    STANDARD_EXTRACTED_BUNDLE_LAYOUT,
    BundleMeta,
    build_standard_extracted_bundle_layout,
    load_bundle_metadata,
    resolve_bundle_layout,
)


def test_bundle_meta_parser_reads_standard_metadata_and_defaults(tmp_path: Path) -> None:
    meta_path = tmp_path / 'bundle_meta.json'
    meta_path.write_text(
        json.dumps(
            {
                'bundle_schema_version': 1,
                'patch_name': 'patch_05_python_bundle_schema_model',
                'target_project': 'patchops',
                'recommended_profile': 'generic_python',
                'target_project_root': r'C:\dev\patchops',
                'wrapper_project_root': r'C:\dev\patchops',
                'content_root': 'content',
                'manifest_path': 'manifest.json',
                'launcher_path': 'run_with_patchops.ps1',
            }
        ),
        encoding='utf-8',
    )

    parsed = load_bundle_metadata(meta_path)

    assert isinstance(parsed, BundleMeta)
    assert parsed.patch_name == 'patch_05_python_bundle_schema_model'
    assert parsed.normalized_content_root == 'content'
    assert parsed.normalized_manifest_path == 'manifest.json'
    assert parsed.normalized_launcher_path == 'run_with_patchops.ps1'


def test_bundle_meta_parser_rejects_missing_required_fields() -> None:
    with pytest.raises(ValueError) as exc_info:
        BundleMeta.from_mapping(
            {
                'bundle_schema_version': 1,
                'patch_name': 'patch_05_python_bundle_schema_model',
                'target_project': 'patchops',
                'recommended_profile': 'generic_python',
                'target_project_root': r'C:\dev\patchops',
            }
        )

    message = str(exc_info.value)
    assert 'missing required field' in message.lower()
    assert 'wrapper_project_root' in message


def test_standard_extracted_bundle_layout_locks_root_level_launcher() -> None:
    layout = build_standard_extracted_bundle_layout()

    assert layout == STANDARD_EXTRACTED_BUNDLE_LAYOUT
    assert layout.manifest_filename == 'manifest.json'
    assert layout.metadata_filename == 'bundle_meta.json'
    assert layout.content_root_name == 'content'
    assert layout.launcher_relative_path == 'run_with_patchops.ps1'
    assert layout.required_root_entries() == (
        'manifest.json',
        'bundle_meta.json',
        'content',
        'run_with_patchops.ps1',
    )


def test_resolve_bundle_layout_builds_expected_paths(tmp_path: Path) -> None:
    resolved = resolve_bundle_layout(tmp_path)

    assert resolved.bundle_root == tmp_path
    assert resolved.manifest_path == tmp_path / 'manifest.json'
    assert resolved.metadata_path == tmp_path / 'bundle_meta.json'
    assert resolved.content_root_path == tmp_path / 'content'
    assert resolved.launcher_path == tmp_path / 'run_with_patchops.ps1'
