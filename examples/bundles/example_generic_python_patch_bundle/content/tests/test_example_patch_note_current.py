from __future__ import annotations

from pathlib import Path


def test_example_patch_note_mentions_flat_archive_and_single_launcher() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    text = (repo_root / 'docs' / 'example_patch_note.md').read_text(encoding='utf-8').lower()

    required = [
        'one root-level launcher',
        'bundle root contents directly',
        'one canonical desktop txt report',
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert not missing, f'example patch note is missing required phrases: {missing}'
