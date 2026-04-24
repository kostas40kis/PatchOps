from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_manifest_schema_documents_hardened_manifest_contract() -> None:
    text = _read("docs/manifest_schema.md")

    assert 'manifest_version` must be the string `"1"`' in text
    assert 'Use `"1"`, not `"1.0"`' in text
    assert "`active_profile` must be a non-empty string" in text
    assert "`files_to_write`" in text
    assert "Do not use `files` or `writes`" in text


def test_bundle_docs_document_preflight_skip_visibility() -> None:
    combined = "\n".join(
        [
            _read("docs/bundle_authoring_template.md"),
            _read("docs/zip_bundle_standard.md"),
            _read("docs/operator_quickstart.md"),
        ]
    )

    assert "canonical staged-authoring contract" in combined
    assert "canonical_staged_authoring_preflight_skipped" in combined
    assert "manifest_path" in combined
    assert "content_root" in combined
    assert "launcher_path" in combined


def test_failure_docs_document_file_evidence_and_post_apply_double_check() -> None:
    text = _read("docs/failure_repair_guide.md")

    assert "run-package" in text
    assert "dataclass-only `asdict(result)`" in text
    assert "`CREATED`, not `MISSING`" in text
    assert "post-apply double-check" in text
    assert "files_to_write" in text
    assert "wrapper failure" in text


def test_readme_summarizes_current_hardening_notes() -> None:
    text = _read("README.md")

    assert "safe `run-package` result serialization" in text
    assert "`files_to_write` versus `files` / `writes`" in text
    assert "visible bundle preflight skip warnings" in text
    assert "built-in post-apply direct existence checks" in text
