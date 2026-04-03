from __future__ import annotations

import shutil
import sys
from pathlib import Path


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def backup_file(src: Path, backup_root: Path) -> None:
    if not src.exists():
        return
    destination = backup_root / src.relative_to(src.anchor if src.is_absolute() else Path('.'))
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, destination)


def replace_or_append_section(text: str, heading: str, body: str) -> str:
    marker = heading + "\n"
    if marker in text:
        start = text.index(marker)
        next_pos = text.find("\n## ", start + len(marker))
        if next_pos == -1:
            return text[:start].rstrip() + "\n\n" + heading + "\n" + body.strip() + "\n"
        return text[:start].rstrip() + "\n\n" + heading + "\n" + body.strip() + "\n\n" + text[next_pos + 2:].lstrip()
    return text.rstrip() + "\n\n" + heading + "\n" + body.strip() + "\n"


def main() -> int:
    repo_root = Path(sys.argv[1]).resolve()
    backup_root = Path(sys.argv[2]).resolve()
    backup_root.mkdir(parents=True, exist_ok=True)

    project_status = repo_root / 'docs' / 'project_status.md'
    patch_ledger = repo_root / 'docs' / 'patch_ledger.md'
    handoff_md = repo_root / 'handoff' / 'current_handoff.md'
    handoff_prompt = repo_root / 'handoff' / 'next_prompt.txt'
    test_path = repo_root / 'tests' / 'test_pythonization_stream_status_refresh_current.py'

    for path in (project_status, patch_ledger, handoff_md, handoff_prompt, test_path):
        if path.exists():
            rel = path.relative_to(repo_root)
            dest = backup_root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)

    status_text = project_status.read_text(encoding='utf-8') if project_status.exists() else '# Project Status\n'
    status_body = '''The Pythonization micro-patch stream is now complete through MP51.

Shipped outcomes from this stream:
- suspicious-run rule detection is present as a Python-owned helper,
- structured suspicious-run artifact modeling is present,
- optional artifact emission is available behind an explicit opt-in flag,
- canonical report mention for emitted artifacts is covered,
- suspicious-run guidance was refreshed in the durable docs,
- the stream includes a real self-hosted PatchOps-on-PatchOps proof run,
- maintenance docs, examples, and status surfaces were refreshed without redesigning PatchOps.

Optional future work remains additive only. The stream did not widen PowerShell into a second workflow engine and did not move target-project logic into PatchOps.'''
    status_text = replace_or_append_section(status_text, '## Pythonization stream status', status_body)
    ensure_parent(project_status)
    project_status.write_text(status_text, encoding='utf-8')

    if patch_ledger.exists():
        ledger_text = patch_ledger.read_text(encoding='utf-8')
        note = '- MP51 â€” final status refresh for the Pythonization stream completed after the MP50 self-hosted proof patch.'
        if note not in ledger_text:
            ledger_text = ledger_text.rstrip() + '\n' + note + '\n'
            patch_ledger.write_text(ledger_text, encoding='utf-8')

    if handoff_md.exists():
        handoff_text = handoff_md.read_text(encoding='utf-8')
        note = 'Pythonization stream: complete through MP51.'
        if note not in handoff_text:
            handoff_text = handoff_text.rstrip() + '\n\n' + note + '\n'
            handoff_md.write_text(handoff_text, encoding='utf-8')

    if handoff_prompt.exists():
        prompt_text = handoff_prompt.read_text(encoding='utf-8')
        header = 'Pythonization stream: complete through MP51.\n'
        if not prompt_text.startswith(header):
            handoff_prompt.write_text(header + prompt_text, encoding='utf-8')

    test_text = '''from pathlib import Path


def _read(repo_root: Path, relative_path: str) -> str:
    return (repo_root / relative_path).read_text(encoding="utf-8")


def test_project_status_marks_pythonization_stream_complete():
    repo_root = Path(__file__).resolve().parents[1]
    text = _read(repo_root, "docs/project_status.md")
    assert "## Pythonization stream status" in text
    assert "complete through MP51" in text
    assert "self-hosted PatchOps-on-PatchOps proof run" in text
    assert "did not widen PowerShell into a second workflow engine" in text


def test_patch_ledger_mentions_mp51_if_present():
    repo_root = Path(__file__).resolve().parents[1]
    path = repo_root / "docs/patch_ledger.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    assert "MP51" in text
    assert "Pythonization stream" in text


def test_handoff_surfaces_mark_stream_complete_if_present():
    repo_root = Path(__file__).resolve().parents[1]
    handoff_path = repo_root / "handoff/current_handoff.md"
    if handoff_path.exists():
        handoff_text = handoff_path.read_text(encoding="utf-8")
        assert "Pythonization stream: complete through MP51." in handoff_text

    prompt_path = repo_root / "handoff/next_prompt.txt"
    if prompt_path.exists():
        prompt_text = prompt_path.read_text(encoding="utf-8")
        assert prompt_text.startswith("Pythonization stream: complete through MP51.")
'''
    ensure_parent(test_path)
    test_path.write_text(test_text, encoding='utf-8')

    print(f'test_path={test_path}')
    print(f'patch_ledger_present={patch_ledger.exists()}')
    print(f'handoff_md_present={handoff_md.exists()}')
    print(f'handoff_prompt_present={handoff_prompt.exists()}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())