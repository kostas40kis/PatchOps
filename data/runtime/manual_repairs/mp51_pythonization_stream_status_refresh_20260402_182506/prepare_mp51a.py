from __future__ import annotations

from pathlib import Path
import shutil
import sys


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def backup_if_exists(src: Path, backup_root: Path, repo_root: Path) -> None:
    if not src.exists():
        return
    rel = src.relative_to(repo_root)
    dst = backup_root / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def upsert_section(text: str, heading: str, body: str) -> str:
    marker = f"## {heading}\n"
    new_block = marker + body.rstrip() + "\n"
    if marker in text:
        start = text.index(marker)
        next_idx = text.find("\n## ", start + len(marker))
        if next_idx == -1:
            return text[:start].rstrip() + "\n\n" + new_block
        return text[:start].rstrip() + "\n\n" + new_block + "\n" + text[next_idx + 1:].lstrip()
    stripped = text.rstrip()
    if stripped:
        return stripped + "\n\n" + new_block
    return new_block


def replace_or_append(path: Path, transform) -> None:
    original = path.read_text(encoding="utf-8") if path.exists() else ""
    updated = transform(original)
    ensure_parent(path)
    path.write_text(updated, encoding="utf-8")


def main() -> int:
    repo_root = Path(sys.argv[1]).resolve()
    backup_root = Path(sys.argv[2]).resolve()

    project_status = repo_root / 'docs' / 'project_status.md'
    patch_ledger = repo_root / 'docs' / 'patch_ledger.md'
    current_handoff = repo_root / 'handoff' / 'current_handoff.md'
    next_prompt = repo_root / 'handoff' / 'next_prompt.txt'
    test_path = repo_root / 'tests' / 'test_pythonization_stream_status_refresh_current.py'

    for candidate in [project_status, patch_ledger, current_handoff, next_prompt, test_path]:
        backup_if_exists(candidate, backup_root, repo_root)

    status_body = """The Pythonization micro-patch stream is now closed through MP51.

- MP42â€“MP47 landed the suspicious-run helper, detector tests, structured artifact model, opt-in emission, compact report mention, and maintenance guidance.
- MP48 refreshed the durable maintenance docs for the stream.
- MP49 aligned examples and starter surfaces with the shipped helper-owned truth.
- MP50 proved a real PatchOps-on-PatchOps self-hosted apply path using check, inspect, plan, apply, backup/write, and inner-report capture.
- MP51 refreshes maintained status surfaces so future LLMs can see the stream is complete without reopening architecture.

What remains optional after this stream:
- future additive ergonomics if a new repo need proves them,
- not a redesign of manifests, profiles, or the PowerShell/Python boundary.
"""
    replace_or_append(project_status, lambda text: upsert_section(text, 'Pythonization Stream Status', status_body))

    if patch_ledger.exists():
        ledger_note = "\n- MP51 â€” Pythonization stream status refresh: maintained status surfaces now say the suspicious-run / self-hosted Pythonization stream is closed through MP51.\n"
        text = patch_ledger.read_text(encoding='utf-8')
        if 'MP51 â€” Pythonization stream status refresh' not in text:
            patch_ledger.write_text(text.rstrip() + ledger_note, encoding='utf-8')

    if current_handoff.exists():
        handoff_body = """Project identity remains unchanged. The Pythonization micro-patch stream is now closed through MP51.

Current stream status:
- suspicious-run support landed and stayed narrow,
- self-hosted proof landed,
- maintained status/docs surfaces have been refreshed,
- no redesign is needed.

Next action:
- return to ordinary maintenance mode unless a new narrow defect appears.
"""
        replace_or_append(current_handoff, lambda text: upsert_section(text, 'Pythonization Stream Refresh', handoff_body))

    if next_prompt.exists():
        prompt_text = next_prompt.read_text(encoding='utf-8')
        note = '\nPythonization stream note: MP42 through MP51 are now closed. Continue only if a new narrow maintenance issue is proven by current repo evidence.\n'
        if 'Pythonization stream note:' not in prompt_text:
            next_prompt.write_text(prompt_text.rstrip() + note, encoding='utf-8')

    test_text = '''from pathlib import Path\n\n\ndef test_project_status_records_pythonization_stream_closed() -> None:\n    text = Path("docs/project_status.md").read_text(encoding="utf-8")\n    assert "Pythonization Stream Status" in text\n    assert "closed through MP51" in text\n    assert "MP50 proved a real PatchOps-on-PatchOps self-hosted apply path" in text\n\n\ndef test_patch_ledger_mentions_mp51_when_present() -> None:\n    path = Path("docs/patch_ledger.md")\n    if not path.exists():\n        return\n    text = path.read_text(encoding="utf-8")\n    assert "MP51 â€” Pythonization stream status refresh" in text\n\n\ndef test_handoff_mentions_closed_stream_when_present() -> None:\n    path = Path("handoff/current_handoff.md")\n    if not path.exists():\n        return\n    text = path.read_text(encoding="utf-8")\n    assert "Pythonization Stream Refresh" in text\n    assert "closed through MP51" in text\n\n\ndef test_next_prompt_mentions_closed_stream_when_present() -> None:\n    path = Path("handoff/next_prompt.txt")\n    if not path.exists():\n        return\n    text = path.read_text(encoding="utf-8")\n    assert "Pythonization stream note:" in text\n    assert "MP42 through MP51" in text\n'''
    ensure_parent(test_path)
    test_path.write_text(test_text, encoding='utf-8')

    print(f"test_path={test_path}")
    print(f"handoff_present={current_handoff.exists()}")
    print(f"next_prompt_present={next_prompt.exists()}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())