from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
HANDOFF_DOC = PROJECT_ROOT / "docs" / "handoff_surface.md"
REQUIRED_FRAGMENTS = [
    "handoff/current_handoff.md",
    "canonical report",
    "Manifest Path",
    "Active Profile",
    "Runtime Path",
    "Wrapper Project Root",
    "Target Project Root",
    "File Write Origin",
    "This note is a linkage note only. It does not redesign the handoff bundle.",
]


def test_wrapper_proof_handoff_linkage_note_current() -> None:
    assert HANDOFF_DOC.exists(), f"Missing handoff surface doc: {HANDOFF_DOC}"
    text = HANDOFF_DOC.read_text(encoding="utf-8")
    assert "## Wrapper proof linkage" in text
    for fragment in REQUIRED_FRAGMENTS:
        assert fragment in text, f"Missing fragment in handoff linkage note: {fragment!r}"
