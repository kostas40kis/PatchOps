from __future__ import annotations

import re
import shutil
import sys
import textwrap
from pathlib import Path


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def backup_file(repo_root: Path, backup_root: Path, target: Path) -> None:
    if not target.exists():
        return
    relative = target.relative_to(repo_root)
    destination = backup_root / relative
    ensure_parent(destination)
    shutil.copy2(target, destination)


def replace_or_append_section(text: str, heading: str, body: str) -> str:
    pattern = re.compile(rf"^## {re.escape(heading)}\n.*?(?=^## |\Z)", re.MULTILINE | re.DOTALL)
    section = f"## {heading}\n{body.strip()}\n"
    if pattern.search(text):
        return pattern.sub(section + "\n", text, count=1)
    if text and not text.endswith("\n"):
        text += "\n"
    return text + "\n" + section


def main() -> int:
    repo_root = Path(sys.argv[1]).resolve()
    backup_root = Path(sys.argv[2]).resolve()
    docs_path = repo_root / 'docs' / 'examples.md'
    test_path = repo_root / 'tests' / 'test_pythonization_examples_stop_current.py'

    if not docs_path.exists():
        raise SystemExit('docs/examples.md not found.')

    backup_file(repo_root, backup_root, docs_path)
    if test_path.exists():
        backup_file(repo_root, backup_root, test_path)

    text = docs_path.read_text(encoding='utf-8')
    body = textwrap.dedent('''
    The Pythonization maintenance stream added helper-owned suspicious-run support, but the example and starter surfaces remain conservative.

    - Existing examples should still be read as the default operator path.
    - Suspicious-run artifact emission is opt-in and maintenance-facing, not a mandatory default behavior for all runs.
    - Template and examples surfaces should remain low-risk and should not imply a broader product redesign.
    - The main value of this stop is to keep examples aligned with shipped helper-owned truth without widening normal operator expectations.
    ''').strip()

    updated = replace_or_append_section(text, 'Pythonization maintenance alignment', body)
    docs_path.write_text(updated, encoding='utf-8')

    current_test = textwrap.dedent('''
    from pathlib import Path


    def test_examples_doc_mentions_pythonization_alignment_stop():
        text = Path('docs/examples.md').read_text(encoding='utf-8').lower()
        assert 'pythonization maintenance alignment' in text
        assert 'opt-in' in text or 'opt in' in text
        assert 'maintenance-facing' in text
        assert 'low-risk' in text or 'low risk' in text
        assert 'not a mandatory default behavior' in text
    ''').strip() + '\n'
    test_path.write_text(current_test, encoding='utf-8')

    print('patched_files=docs/examples.md;tests/test_pythonization_examples_stop_current.py')
    print(f'test_path={test_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())