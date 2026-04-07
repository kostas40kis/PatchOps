from __future__ import annotations

from pathlib import Path
import json


def test_bundle_authoring_template_doc_exists_and_locks_manual_unzip_stage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    doc_path = repo_root / 'docs' / 'bundle_authoring_template.md'
    text = doc_path.read_text(encoding='utf-8').lower()

    required_phrases = [
        'manual unzip stage',
        'copy the maintained example bundle',
        'one canonical desktop txt report',
        'older patchops',
        'thin launcher',
        'archive the bundle root contents directly',
        'extra duplicate parent folder',
    ]

    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f'bundle authoring template doc is missing required phrases: {missing}'


def test_example_bundle_has_required_shape() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    bundle_root = repo_root / 'examples' / 'bundles' / 'example_generic_python_patch_bundle'

    required_paths = [
        bundle_root / 'manifest.json',
        bundle_root / 'bundle_meta.json',
        bundle_root / 'README.txt',
        bundle_root / 'run_with_patchops.ps1',
        bundle_root / 'content' / 'docs' / 'example_patch_note.md',
        bundle_root / 'content' / 'tests' / 'test_example_patch_note_current.py',
    ]

    missing = [str(path) for path in required_paths if not path.exists()]
    assert not missing, f'example bundle is missing required paths: {missing}'


def test_example_bundle_metadata_manifest_and_root_launcher_are_thin_and_concrete() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    bundle_root = repo_root / 'examples' / 'bundles' / 'example_generic_python_patch_bundle'

    bundle_meta = json.loads((bundle_root / 'bundle_meta.json').read_text(encoding='utf-8'))
    manifest = json.loads((bundle_root / 'manifest.json').read_text(encoding='utf-8'))
    launcher_text = (bundle_root / 'run_with_patchops.ps1').read_text(encoding='utf-8').lstrip()

    assert bundle_meta['bundle_schema_version'] == 1
    assert bundle_meta['manifest_path'] == 'manifest.json'
    assert bundle_meta['launcher_path'] == 'run_with_patchops.ps1'
    assert manifest['active_profile'] == 'generic_python'
    assert manifest['files_to_write'][0]['content_path'].startswith('content/')
    assert launcher_text.startswith('& {')
    assert 'py -m patchops.cli apply $manifestPath' in launcher_text
    assert 'py -m patchops.cli verify $manifestPath' not in launcher_text
