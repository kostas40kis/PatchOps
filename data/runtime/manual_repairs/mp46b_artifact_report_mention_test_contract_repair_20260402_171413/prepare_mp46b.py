from __future__ import annotations

import re
import shutil
import sys
import textwrap
from pathlib import Path


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def replace_test_function(text: str) -> str:
    pattern = re.compile(
        r"^def test_report_line_wording_stays_compact\([^\n]*\):\n(?:    .*\n|\n)*?(?=^def |\Z)",
        re.MULTILINE,
    )
    replacement = textwrap.dedent(
        '''
        def test_report_line_wording_stays_compact():
            line = suspicious_run_artifact_report_lines(Path("artifact.json"))[0]
            assert "emitted" in line.lower()
            assert "artifact" in line.lower()
            label_text = line.split(":", 1)[0].lower()
            assert "report" not in label_text
        '''
    ).strip() + "\n"
    updated, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise SystemExit('Could not replace test_report_line_wording_stays_compact function block.')
    return updated


def main() -> int:
    repo_root = Path(sys.argv[1]).resolve()
    test_path = repo_root / 'tests' / 'test_suspicious_artifact_report_mention_current.py'
    text = test_path.read_text(encoding='utf-8')
    updated = replace_test_function(text)
    test_path.write_text(updated, encoding='utf-8')
    print(f'test_path={test_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())