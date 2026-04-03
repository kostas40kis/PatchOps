from __future__ import annotations

import shutil
import sys
from pathlib import Path


README_SNIPPET = """
## Suspicious-run support in maintenance mode

PatchOps now includes a small suspicious-run support layer that helps operators notice when wrapper evidence and repo truth may disagree. This is a wrapper health aid, not target-project business logic. The detector and artifact helpers stay conservative, and artifact emission starts opt-in rather than default-on so the canonical one-report flow remains stable.
""".strip()

STATUS_SNIPPET = """
## Pythonization stream maintenance note

The Pythonization micro-patch stream now includes suspicious-run rule detection, detector proofs, a compact machine-readable artifact model, optional artifact emission behind an explicit flag, and a short canonical report mention when an artifact is emitted. These additions are maintenance-grade wrapper-health aids and do not widen PatchOps into target-project policy logic.
""".strip()

QUICKSTART_SNIPPET = """
## Suspicious-run note

If a patch run looks internally contradictory, treat that as a wrapper-health signal first. Read the canonical report, then inspect any emitted suspicious-run artifact only when the run explicitly opted into artifact emission.
""".strip()

WRAPPER_PACKET_SNIPPET = """
## Suspicious-run maintenance note

The self-hosted maintenance stream now includes suspicious-run helpers for contradiction detection, compact optional artifact emission, and a short report mention when emission occurs. These surfaces exist to improve wrapper trust during maintenance work and remain intentionally conservative.
""".strip()

TEST_TEXT = '''
from pathlib import Path


def test_readme_mentions_suspicious_run_support():
    text = Path("README.md").read_text(encoding="utf-8")
    lowered = text.lower()
    assert "suspicious-run" in lowered
    assert "wrapper health aid" in lowered
    assert "opt-in" in lowered or "opt in" in lowered


def test_project_status_mentions_pythonization_stream_note():
    text = Path("docs/project_status.md").read_text(encoding="utf-8").lower()
    assert "pythonization micro-patch stream" in text
    assert "suspicious-run rule detection" in text
    assert "optional artifact emission" in text


def test_operator_quickstart_mentions_how_to_read_suspicious_runs():
    text = Path("docs/operator_quickstart.md").read_text(encoding="utf-8").lower()
    assert "suspicious-run" in text
    assert "canonical report" in text
    assert "artifact emission" in text or "artifact" in text


def test_wrapper_self_hosted_packet_mentions_suspicious_run_support_when_present():
    packet = Path("docs/projects/wrapper_self_hosted.md")
    if not packet.exists():
        return
    text = packet.read_text(encoding="utf-8").lower()
    assert "suspicious-run" in text
    assert "optional artifact emission" in text or "artifact emission" in text
'''.lstrip()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def backup_file(path: Path, repo_root: Path, backup_root: Path) -> None:
    if not path.exists():
        return
    backup_path = backup_root / path.relative_to(repo_root)
    ensure_parent(backup_path)
    shutil.copy2(path, backup_path)


def append_once(text: str, snippet: str) -> str:
    if snippet in text:
        return text
    if text and not text.endswith("\n"):
        text += "\n"
    return text + "\n" + snippet + "\n"


def update_text_file(path: Path, snippet: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    path.write_text(append_once(text, snippet), encoding="utf-8")


def main() -> int:
    repo_root = Path(sys.argv[1]).resolve()
    backup_root = Path(sys.argv[2]).resolve()

    files = [
        repo_root / "README.md",
        repo_root / "docs" / "project_status.md",
        repo_root / "docs" / "operator_quickstart.md",
    ]
    optional_packet = repo_root / "docs" / "projects" / "wrapper_self_hosted.md"
    if optional_packet.exists():
        files.append(optional_packet)

    for file_path in files:
        backup_file(file_path, repo_root, backup_root)

    update_text_file(repo_root / "README.md", README_SNIPPET)
    update_text_file(repo_root / "docs" / "project_status.md", STATUS_SNIPPET)
    update_text_file(repo_root / "docs" / "operator_quickstart.md", QUICKSTART_SNIPPET)
    if optional_packet.exists():
        update_text_file(optional_packet, WRAPPER_PACKET_SNIPPET)

    test_path = repo_root / "tests" / "test_pythonization_docs_stop_current.py"
    backup_file(test_path, repo_root, backup_root)
    ensure_parent(test_path)
    test_path.write_text(TEST_TEXT, encoding="utf-8")

    print("patched_files=README.md;docs/project_status.md;docs/operator_quickstart.md;tests/test_pythonization_docs_stop_current.py")
    print(f"test_path={test_path}")
    print(f"packet_present={optional_packet.exists()}")
    if optional_packet.exists():
        print(f"packet_path={optional_packet}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())