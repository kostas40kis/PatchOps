from __future__ import annotations

import json
from pathlib import Path

from patchops.llm_browser.chat_page_contract import ArtifactCandidate
from patchops.llm_browser.processed_store import (
    ProcessedArtifactRecord,
    ProcessedArtifactStore,
    default_store_path,
    sha256_file,
)


def _candidate(filename: str = "patch_d0_13_processed_artifact_store_patchops_bundle.zip") -> ArtifactCandidate:
    return ArtifactCandidate(
        filename=filename,
        href="/downloads/" + filename,
        source="href",
        text=filename,
    )


def test_default_store_path_uses_explicit_store_path(tmp_path: Path) -> None:
    explicit = tmp_path / "custom.json"

    assert default_store_path(environ={"PATCHOPS_LLM_BROWSER_PROCESSED_STORE": str(explicit)}) == explicit


def test_default_store_path_uses_store_dir(tmp_path: Path) -> None:
    root = tmp_path / "state"

    assert default_store_path(environ={"PATCHOPS_LLM_BROWSER_STORE_DIR": str(root)}) == root / "processed_artifacts.json"


def test_default_store_path_uses_localappdata_when_available(tmp_path: Path) -> None:
    local = tmp_path / "LocalAppData"

    assert default_store_path(environ={"LOCALAPPDATA": str(local)}) == local / "PatchOps" / "llm_browser" / "processed_artifacts.json"


def test_sha256_file_is_deterministic(tmp_path: Path) -> None:
    artifact = tmp_path / "patch_d0_13_processed_artifact_store_patchops_bundle.zip"
    artifact.write_bytes(b"zip bytes")

    assert sha256_file(artifact) == sha256_file(artifact)
    assert len(sha256_file(artifact)) == 64


def test_store_loads_missing_file_as_empty_without_writing(tmp_path: Path) -> None:
    store_path = tmp_path / "processed_artifacts.json"
    store = ProcessedArtifactStore(store_path)

    assert store.records() == ()
    assert store_path.exists() is False
    assert store.last_repair.reason == "missing_store"


def test_mark_processed_writes_record_and_payload(tmp_path: Path) -> None:
    artifact = tmp_path / "patch_d0_13_processed_artifact_store_patchops_bundle.zip"
    artifact.write_bytes(b"zip bytes")
    report = tmp_path / "report.txt"
    report.write_text("PASS", encoding="utf-8")
    store = ProcessedArtifactStore(tmp_path / "processed_artifacts.json", clock=lambda: "2026-04-29T22:00:00+00:00")

    record = store.mark_processed(
        artifact,
        result="PASS",
        report_path=report,
        candidate=_candidate(),
        notes=("canonical report accepted",),
    )

    assert record.sha256 == sha256_file(artifact)
    assert record.filename == artifact.name
    assert record.href == "/downloads/" + artifact.name
    assert record.report_path == str(report)
    assert record.processed_at == "2026-04-29T22:00:00+00:00"
    assert record.notes == ("canonical report accepted",)

    payload = json.loads((tmp_path / "processed_artifacts.json").read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1"
    assert payload["records"][0]["sha256"] == sha256_file(artifact)


def test_decide_for_same_hash_skips_duplicate(tmp_path: Path) -> None:
    artifact = tmp_path / "patch_d0_13_processed_artifact_store_patchops_bundle.zip"
    artifact.write_bytes(b"same bytes")
    store = ProcessedArtifactStore(tmp_path / "processed_artifacts.json", clock=lambda: "2026-04-29T22:00:00+00:00")

    store.mark_processed(artifact, result="PASS", candidate=_candidate())
    decision = store.decide_for_file(artifact, candidate=_candidate())

    assert decision.should_process is False
    assert decision.reason == "sha256_already_processed"
    assert decision.existing_record is not None
    assert decision.existing_record.sha256 == sha256_file(artifact)


def test_same_filename_different_hash_is_new_with_warning(tmp_path: Path) -> None:
    first = tmp_path / "first" / "patch_d0_13_processed_artifact_store_patchops_bundle.zip"
    second = tmp_path / "second" / "patch_d0_13_processed_artifact_store_patchops_bundle.zip"
    first.parent.mkdir()
    second.parent.mkdir()
    first.write_bytes(b"first")
    second.write_bytes(b"second")
    store = ProcessedArtifactStore(tmp_path / "processed_artifacts.json", clock=lambda: "2026-04-29T22:00:00+00:00")

    store.mark_processed(first, result="PASS", candidate=_candidate())
    decision = store.decide_for_file(second, candidate=_candidate())

    assert decision.should_process is True
    assert decision.reason == "new_artifact"
    assert decision.warning == "same_filename_different_hash"
    assert len(decision.filename_conflicts) == 1
    assert decision.filename_conflicts[0].filename == first.name


def test_store_processed_keys_include_hash_filename_href_and_path(tmp_path: Path) -> None:
    artifact = tmp_path / "patch_d0_13_processed_artifact_store_patchops_bundle.zip"
    artifact.write_bytes(b"zip bytes")
    candidate = _candidate()
    store = ProcessedArtifactStore(tmp_path / "processed_artifacts.json")

    record = store.mark_processed(artifact, result="PASS", candidate=candidate)
    keys = store.processed_keys()

    assert record.sha256 in keys
    assert artifact.name in keys
    assert candidate.href in keys
    assert str(artifact).lower() in keys


def test_mark_processed_updates_existing_hash_in_place(tmp_path: Path) -> None:
    artifact = tmp_path / "patch_d0_13_processed_artifact_store_patchops_bundle.zip"
    artifact.write_bytes(b"zip bytes")
    store = ProcessedArtifactStore(tmp_path / "processed_artifacts.json", clock=lambda: "2026-04-29T22:00:00+00:00")

    store.mark_processed(artifact, result="FAIL", candidate=_candidate(), notes=("first",))
    store.mark_processed(artifact, result="PASS", candidate=_candidate(), notes=("second",))

    records = store.records()
    assert len(records) == 1
    assert records[0].result == "PASS"
    assert records[0].notes == ("second",)


def test_corrupt_store_is_backed_up_and_repaired(tmp_path: Path) -> None:
    store_path = tmp_path / "processed_artifacts.json"
    store_path.write_text("{ this is not json", encoding="utf-8")
    store = ProcessedArtifactStore(store_path, clock=lambda: "2026-04-29T22:00:00+00:00")

    assert store.records() == ()
    assert store.last_repair.repaired is True
    assert store.last_repair.reason == "corrupt_store_repaired"
    assert store.last_repair.backup_path is not None
    assert store.last_repair.backup_path.exists()
    assert "this is not json" in store.last_repair.backup_path.read_text(encoding="utf-8")

    payload = json.loads(store_path.read_text(encoding="utf-8"))
    assert payload == {"records": [], "schema_version": "1"}


def test_record_from_payload_normalizes_optional_fields() -> None:
    record = ProcessedArtifactRecord.from_payload(
        {
            "sha256": "ABCDEF",
            "filename": " patch.zip ",
            "path": " C:/Downloads/patch.zip ",
            "processed_at": " now ",
            "result": " PASS ",
            "report_path": "",
            "href": None,
            "notes": ["one", 2],
        }
    )

    assert record.sha256 == "abcdef"
    assert record.filename == "patch.zip"
    assert record.path == "C:/Downloads/patch.zip"
    assert record.processed_at == "now"
    assert record.result == "PASS"
    assert record.report_path is None
    assert record.href is None
    assert record.notes == ("one", "2")


def test_decision_payload_is_compact(tmp_path: Path) -> None:
    artifact = tmp_path / "patch_d0_13_processed_artifact_store_patchops_bundle.zip"
    artifact.write_bytes(b"zip bytes")
    store = ProcessedArtifactStore(tmp_path / "processed_artifacts.json")

    decision = store.decide_for_file(artifact, candidate=_candidate())
    payload = decision.to_payload()

    assert payload["should_process"] is True
    assert payload["reason"] == "new_artifact"
    assert payload["sha256"] == sha256_file(artifact)
    assert payload["existing_record"] is None
    assert payload["filename_conflicts"] == []
