from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_text(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_project_packet_contract_doc_exists_and_defines_the_surface() -> None:
    content = read_text("docs/project_packet_contract.md")
    lowered = content.lower()

    assert "project packet" in lowered
    assert "docs/projects/" in content or "docs\\projects\\" in content
    assert "required structure" in lowered
    assert "stable" in lowered
    assert "mutable" in lowered


def test_project_packet_contract_doc_preserves_core_boundaries() -> None:
    content = read_text("docs/project_packet_contract.md")
    lowered = content.lower()

    assert "project-agnostic" in lowered
    assert "powershell remains thin" in lowered
    assert "python owns reusable" in lowered
    assert "profiles remain the executable abstraction" in lowered
    assert "handoff remains the continuation surface" in lowered
