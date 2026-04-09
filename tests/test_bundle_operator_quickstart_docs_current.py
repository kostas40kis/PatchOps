from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _read(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_operator_quickstart_describes_the_proven_standardized_bundle_flow() -> None:
    quickstart = _read("docs/operator_quickstart.md")
    required = [
        "make-bundle",
        "bundle-doctor",
        "build-bundle",
        "run-package",
        "canonical Desktop txt report",
        "default maintained workflow",
    ]
    for phrase in required:
        assert phrase in quickstart


def test_bundle_docs_match_the_operator_quickstart_sequence() -> None:
    standard = _read("docs/zip_bundle_standard.md")
    template = _read("docs/bundle_authoring_template.md")
    llm = _read("docs/llm_usage.md")

    required = [
        "make-bundle",
        "check-bundle",
        "inspect-bundle",
        "plan-bundle",
        "bundle-doctor",
        "build-bundle",
        "run-package",
        "continue patch by patch from evidence",
    ]

    for phrase in required:
        assert phrase in standard
        assert phrase in template or phrase in llm


def test_docs_state_that_patch_12_made_the_process_proven_self_hosted() -> None:
    standard = _read("docs/zip_bundle_standard.md")
    quickstart = _read("docs/operator_quickstart.md")
    assert "Patch 12 onward" in standard
    assert "no longer requires ad hoc launcher authoring or manual zip guesswork" in quickstart
