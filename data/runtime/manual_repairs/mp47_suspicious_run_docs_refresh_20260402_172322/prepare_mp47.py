from __future__ import annotations

import json
import re
import shutil
import sys
import textwrap
from pathlib import Path


SECTION_HEADER = "## Suspicious-run support"


def backup_file(repo_root: Path, backup_root: Path, relative_path: str) -> None:
    source = repo_root / relative_path
    if not source.exists():
        return
    target = backup_root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def main() -> int:
    repo_root = Path(sys.argv[1]).resolve()
    backup_root = Path(sys.argv[2]).resolve()

    doc_path = repo_root / "docs" / "failure_repair_guide.md"
    test_path = repo_root / "tests" / "test_suspicious_run_docs_current.py"

    backup_file(repo_root, backup_root, "docs/failure_repair_guide.md")
    backup_file(repo_root, backup_root, "tests/test_suspicious_run_docs_current.py")

    original_doc = doc_path.read_text(encoding="utf-8")
    section = textwrap.dedent(
        """
        ## Suspicious-run support

        Suspicious-run support is a conservative wrapper health aid. It is meant to help operators notice when wrapper evidence looks contradictory or incomplete. It is not a target-content feature and it does not claim that the target project itself is broken.

        What currently counts as suspicious should stay narrow. Examples include required command evidence contradicting the rendered summary, critical provenance fields missing after wrapper execution, a copied latest-report surface missing after a handoff export path that should have produced it, or a report structure missing required core fields.

        This surface starts opt-in on purpose. The first release is meant to stay maintenance-friendly and avoid noisy false positives in every run. Operators should enable emitted suspicious-run artifacts only when they are deliberately proving or inspecting wrapper health.

        When a suspicious-run artifact is emitted, read it as a small machine-readable aid rather than as a final verdict. The artifact summarizes the detection reason, failure class, report path, workflow mode, optional manifest path, and recommended follow-up so the next inspection step is easier to choose.
        """
    ).strip() + "\n"

    if SECTION_HEADER in original_doc:
        pattern = re.compile(r"(?ms)^## Suspicious-run support\s*\n.*?(?=^## |\Z)")
        updated_doc = pattern.sub(section + "\n", original_doc)
    else:
        updated_doc = original_doc.rstrip() + "\n\n" + section

    doc_path.write_text(updated_doc, encoding="utf-8")

    test_text = textwrap.dedent(
        '''
        from pathlib import Path


        def test_failure_repair_guide_documents_suspicious_run_support():
            text = Path("docs/failure_repair_guide.md").read_text(encoding="utf-8").lower()
            assert "## suspicious-run support" in text
            assert "wrapper health aid" in text
            assert "not a target-content feature" in text
            assert "starts opt-in" in text
            assert "read it as a small machine-readable aid" in text


        def test_failure_repair_guide_lists_conservative_suspicious_cases():
            text = Path("docs/failure_repair_guide.md").read_text(encoding="utf-8").lower()
            assert "required command evidence contradicting the rendered summary" in text
            assert "critical provenance fields missing after wrapper execution" in text
            assert "copied latest-report surface missing after a handoff export path" in text
            assert "report structure missing required core fields" in text
        '''
    ).strip() + "\n"
    test_path.write_text(test_text, encoding="utf-8")

    result = {
        "patched_files": [
            "docs\\failure_repair_guide.md",
            "tests\\test_suspicious_run_docs_current.py",
        ],
        "backup_root": str(backup_root),
        "already_present": False,
    }
    print(json.dumps(result, indent=2))
    print(f"doc_path={doc_path}")
    print(f"test_path={test_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())