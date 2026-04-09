from __future__ import annotations

from contextlib import redirect_stdout
import json
from io import StringIO
from pathlib import Path

from patchops.bundles.authoring import build_bundle_zip, create_proof_bundle, create_starter_bundle
from patchops.cli import main


def _run_cli(argv: list[str]) -> tuple[int, dict]:
    buffer = StringIO()
    with redirect_stdout(buffer):
        exit_code = int(main(argv))
    payload = json.loads(buffer.getvalue())
    return exit_code, payload


def test_check_bundle_directory_includes_safe_launcher_review(tmp_path: Path) -> None:
    result = create_starter_bundle(
        tmp_path / "starter_bundle",
        patch_name="safe_bundle",
        target_project="patchops",
        target_project_root="C:/dev/patchops",
    )
    staged = result.content_root / "docs" / "note.md"
    staged.parent.mkdir(parents=True, exist_ok=True)
    staged.write_text("# safe\n", encoding="utf-8")

    exit_code, payload = _run_cli(["check-bundle", str(result.bundle_root)])

    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["launcher_review"]["status"] == "safe"
    assert payload["launcher_review"]["issue_count"] == 0
    assert payload["launcher_issue_count"] == 0
    assert payload["launcher_issue_codes"] == []


def test_check_bundle_zip_rejects_risky_launcher_in_review_payload(tmp_path: Path) -> None:
    proof = create_proof_bundle(
        tmp_path / "launcher_risk_bundle",
        kind="launcher-risk",
        patch_name="launcher_risk_bundle",
        target_project="patchops",
        target_project_root="C:/dev/patchops",
    )
    built = build_bundle_zip(proof.bundle_root, tmp_path / "launcher_risk_bundle.zip")
    assert built.ok is True

    exit_code, payload = _run_cli(["check-bundle", str(built.output_zip)])

    assert exit_code == 1
    assert payload["ok"] is False
    assert payload["launcher_review"]["status"] == "reject"
    assert payload["launcher_review"]["issue_count"] >= 1
    assert payload["launcher_issue_count"] >= 1
    assert all(item["code"] for item in payload["launcher_review"]["issues"])


def test_inspect_bundle_zip_surfaces_launcher_review_for_safe_bundle(tmp_path: Path) -> None:
    proof = create_proof_bundle(
        tmp_path / "safe_proof_bundle",
        kind="apply",
        patch_name="safe_proof_bundle",
        target_project="patchops",
        target_project_root="C:/dev/patchops",
    )
    built = build_bundle_zip(proof.bundle_root, tmp_path / "safe_proof_bundle.zip")
    assert built.ok is True

    exit_code, payload = _run_cli(["inspect-bundle", str(built.output_zip)])

    assert exit_code == 0
    assert payload["ok"] is True
    assert payload["launcher_review"]["status"] == "safe"
    assert payload["launcher_review"]["issue_count"] == 0


def test_plan_bundle_zip_surfaces_reject_launcher_review_for_risky_bundle(tmp_path: Path) -> None:
    proof = create_proof_bundle(
        tmp_path / "risky_plan_bundle",
        kind="launcher-risk",
        patch_name="risky_plan_bundle",
        target_project="patchops",
        target_project_root="C:/dev/patchops",
    )
    built = build_bundle_zip(proof.bundle_root, tmp_path / "risky_plan_bundle.zip")
    assert built.ok is True

    exit_code, payload = _run_cli(["plan-bundle", str(built.output_zip)])

    assert exit_code == 1
    assert payload["ok"] is False
    assert payload["launcher_review"]["status"] == "reject"
    assert payload["launcher_issue_count"] >= 1
    assert any(item["code"] for item in payload["launcher_review"]["issues"])
