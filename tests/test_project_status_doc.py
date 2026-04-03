from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = PROJECT_ROOT / "docs" / "project_status.md"


def _read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_project_status_doc_exists() -> None:
    assert DOC_PATH.exists(), f"Missing doc: {DOC_PATH}"


def test_project_status_doc_distinguishes_stable_now_from_future_work() -> None:
    text = _read_doc()
    lowered = text.lower()
    required_fragments = [
        "current state snapshot",
        "stable now",
        "exists in the repo today",
        "future work, not yet shipped behavior",
        "what remains future work rather than current behavior",
        "patch 41",
        "patch 48",
    ]
    for fragment in required_fragments:
        assert fragment in lowered, f"Missing required fragment in project status doc: {fragment}"


def test_project_status_doc_mentions_current_stable_surfaces() -> None:
    text = _read_doc()
    assert "verification-only reruns" in text
    assert "wrapper-only retry classification support" in text
    assert "powershell/Invoke-PatchVerify.ps1" in text
    assert "patchops.cli examples" in text
