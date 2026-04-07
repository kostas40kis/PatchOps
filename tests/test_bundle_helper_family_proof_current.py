from __future__ import annotations

import json
from pathlib import Path
import zipfile

from patchops.bundles.authoring import create_starter_bundle
from patchops.bundles.failure_classification import (
    PACKAGE_AUTHORING_FAILURE,
    BundleFailureEvidence,
    classify_bundle_run_failure,
)
from patchops.bundles.launcher_formatter import is_launcher_safely_wrapped
from patchops.bundles.launcher_heuristics import find_common_launcher_mistakes
from patchops.bundles.preflight import preflight_bundle_zip


def _package_bundle_root(bundle_root: Path, zip_path: Path) -> Path:
    with zipfile.ZipFile(zip_path, "w") as archive:
        for path in bundle_root.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(bundle_root))
    return zip_path


def test_bundle_helper_family_proof_for_safe_starter_bundle(tmp_path: Path) -> None:
    starter_root = tmp_path / "starter_bundle"
    result = create_starter_bundle(
        starter_root,
        patch_name="zp19_demo_bundle",
        target_project="patchops",
        target_project_root="C:/dev/patchops",
    )

    content_docs = result.content_root / "docs"
    content_tests = result.content_root / "tests"
    content_docs.mkdir(parents=True, exist_ok=True)
    content_tests.mkdir(parents=True, exist_ok=True)
    (content_docs / "note.md").write_text("# proof\n", encoding="utf-8")
    (content_tests / "test_note_current.py").write_text(
        "def test_note_current() -> None:\n    assert True\n",
        encoding="utf-8",
    )

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    manifest["files_to_write"] = [
        {
            "target_path": "docs\\note.md",
            "content_path": "content/docs/note.md",
        },
        {
            "target_path": "tests\\test_note_current.py",
            "content_path": "content/tests/test_note_current.py",
        },
    ]
    manifest["validation_commands"] = [
        {
            "name": "demo_contract",
            "command": ["py", "-m", "pytest", "-q", "tests/test_note_current.py"],
        }
    ]
    result.manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    zip_path = _package_bundle_root(starter_root, tmp_path / "zp19_demo_bundle.zip")
    wrapper_root = tmp_path / "wrapper"
    wrapper_root.mkdir()

    preflight = preflight_bundle_zip(
        zip_path,
        wrapper_root,
        timestamp_token="20260407_174900",
    )

    assert preflight.is_valid is True
    assert preflight.ok is True
    assert preflight.warning_count == 0
    assert preflight.inspect.target_paths == ("docs\\note.md", "tests\\test_note_current.py")
    assert preflight.inspect.validation_command_names == ("demo_contract",)
    assert len(preflight.launcher_audits) == 1
    assert preflight.launcher_audits[0].path.name == "run_with_patchops.ps1"
    assert preflight.launcher_audits[0].codes == ()

    launcher_text = result.launcher_path.read_text(encoding="utf-8")
    assert is_launcher_safely_wrapped(launcher_text) is True
    assert find_common_launcher_mistakes(launcher_text) == ()


def test_bundle_helper_family_proof_keeps_package_authoring_classification_explicit() -> None:
    classification = classify_bundle_run_failure(
        BundleFailureEvidence(
            launcher_started=False,
            inner_report_found=False,
            stderr="FileNotFoundError: [Errno 2] No such file or directory: '...\\content\\tests\\missing.py'",
            package_setup_error="(package setup failed before launcher invocation)",
        )
    )

    assert classification.category == PACKAGE_AUTHORING_FAILURE
    assert "before launcher invocation" in classification.reason
