from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SELF = Path("tests/test_source_bundle_modular_layout_truth_lock_current.py")

OLD_BACKSLASH_PATHS = (
    "patchops" + "\\" + "reporting.py",
    "patchops" + "\\" + "failure_classifier.py",
)

OLD_SLASH_PATHS = (
    "patchops" + "/" + "reporting.py",
    "patchops" + "/" + "failure_classifier.py",
)

HISTORICAL_ALLOWLIST = {
    Path("handoff/patchops_final_freeze_bundle_reconstructed_20260328.txt"),
    SELF,
}

TEXT_EXTS = {".md", ".txt", ".py", ".ps1", ".json"}


def _candidate_files() -> list[Path]:
    files: list[Path] = []

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue

        rel = path.relative_to(ROOT)
        parts = set(rel.parts)

        if ".git" in parts or ".venv" in parts or ".pytest_cache" in parts or "__pycache__" in parts:
            continue

        if len(rel.parts) >= 2 and rel.parts[0] == "data" and rel.parts[1] == "runtime":
            continue

        if rel in HISTORICAL_ALLOWLIST:
            continue

        if path.suffix.lower() not in TEXT_EXTS:
            continue

        files.append(path)

    return files


def test_active_source_bundle_materials_do_not_request_old_flat_modules() -> None:
    offenders: list[str] = []

    for path in _candidate_files():
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="ignore")

        has_old_path = any(item in text for item in OLD_BACKSLASH_PATHS + OLD_SLASH_PATHS)
        if not has_old_path:
            continue

        looks_like_source_bundle_contract = (
            "REQUESTED HIGH-PRIORITY SOURCES" in text
            or "MISSING :" in text
            or "HIGH-PRIORITY" in text
            or "source-bundle" in text.lower()
            or "future-llm" in text.lower()
        )

        if looks_like_source_bundle_contract:
            offenders.append(rel)

    assert offenders == []


def test_handoff_and_docs_name_the_current_modular_layout() -> None:
    material_paths = [
        ROOT / "docs" / "llm_usage.md",
        ROOT / "handoff" / "current_handoff.md",
        ROOT / "handoff" / "final_future_llm_source_bundle.txt",
    ]

    combined = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in material_paths
        if path.exists()
    )

    assert "patchops/reporting/" in combined
    assert "patchops/execution/failure_classifier.py" in combined
    assert "Old flat reporting/classifier module names are historical snapshot context only" in combined
