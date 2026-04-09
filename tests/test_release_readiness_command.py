import json
from pathlib import Path

from patchops.cli import main


REQUIRED_RELEASE_DOCS = (
    "docs/release_checklist.md",
    "docs/stage1_freeze_checklist.md",
    "docs/project_status.md",
    "docs/patch_ledger.md",
)

REQUIRED_RELEASE_EXAMPLES = (
    "examples/trader_first_doc_patch.json",
    "examples/trader_first_verify_patch.json",
    "examples/generic_python_patch.json",
    "examples/generic_verify_patch.json",
)

REQUIRED_RELEASE_WORKFLOWS = (
    "patchops/cli.py",
    "patchops/readiness.py",
    "patchops/initial_milestone_gate.py",
    "patchops/workflows/verify_only.py",
    "patchops/workflows/wrapper_retry.py",
)

REQUIRED_RELEASE_LAUNCHERS = (
    "powershell/Invoke-PatchManifest.ps1",
    "powershell/Invoke-PatchVerify.ps1",
    "powershell/Invoke-PatchWrapperRetry.ps1",
)

REQUIRED_RELEASE_TESTS = (
    "tests/test_release_readiness_command.py",
    "tests/test_powershell_readiness_launcher.py",
    "tests/test_profile_summary_command.py",
    "tests/test_powershell_launchers.py",
)

REQUIRED_BUNDLE_RELEASE_DOCS = (
    "docs/bundle_contract_packet.md",
    "docs/bundle_regression_gate.md",
    "docs/bundle_smoke_gate.md",
    "docs/self_hosted_bundle_proof.md",
    "docs/bundle_release_readiness.md",
)

REQUIRED_BUNDLE_RELEASE_WORKFLOWS = (
    "patchops/bundles/authoring.py",
    "patchops/bundles/launcher_emitter.py",
)

REQUIRED_BUNDLE_RELEASE_TESTS = (
    "tests/test_bundle_contract_packet_current.py",
    "tests/test_bundle_manifest_regression_gate_current.py",
    "tests/test_bundle_post_build_smoke_gate_current.py",
    "tests/test_self_hosted_bundle_authoring_proof_current.py",
)


def _write_file(repo_root: Path, relative_path: str, content: str = "x\n") -> None:
    path = repo_root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_release_ready_repo(repo_root: Path) -> None:
    for relative_path in (
        *REQUIRED_RELEASE_DOCS,
        *REQUIRED_RELEASE_EXAMPLES,
        *REQUIRED_RELEASE_WORKFLOWS,
        *REQUIRED_RELEASE_LAUNCHERS,
        *REQUIRED_RELEASE_TESTS,
        *REQUIRED_BUNDLE_RELEASE_DOCS,
        *REQUIRED_BUNDLE_RELEASE_WORKFLOWS,
        *REQUIRED_BUNDLE_RELEASE_TESTS,
    ):
        _write_file(repo_root, relative_path)


def test_release_readiness_command_is_honest_when_core_test_state_is_unknown(tmp_path, capsys):
    _seed_release_ready_repo(tmp_path)

    exit_code = main(
        [
            "release-readiness",
            "--wrapper-root",
            str(tmp_path),
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "review_required"
    assert payload["core_tests_state"] == "unknown"
    assert payload["release_docs_ok"] is True
    assert payload["release_examples_ok"] is True
    assert payload["release_workflows_ok"] is True
    assert payload["release_launchers_ok"] is True
    assert payload["release_tests_ok"] is True
    assert payload["profiles_ok"] is True
    assert payload["bundle_release_docs_ok"] is True
    assert payload["bundle_release_workflows_ok"] is True
    assert payload["bundle_release_tests_ok"] is True
    assert "core test state not provided" in payload["issues"]
    assert payload["report_lines"][0] == "PATCHOPS RELEASE READINESS"
    assert "Status            : review_required" in payload["report_lines"]
    assert "Tests             : ok" in payload["report_lines"]
    assert "Bundle Tests      : ok" in payload["report_lines"]


def test_release_readiness_command_can_report_green_with_explicit_test_state(tmp_path, capsys):
    _seed_release_ready_repo(tmp_path)

    exit_code = main(
        [
            "release-readiness",
            "--wrapper-root",
            str(tmp_path),
            "--profile",
            "trader",
            "--core-tests-green",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "green"
    assert payload["core_tests_state"] == "green"
    assert payload["release_tests_ok"] is True
    assert payload["bundle_release_tests_ok"] is True
    assert payload["profile_summaries"][0]["name"] == "trader"
    assert "Surface     : release-readiness" in payload["scope_lines"]
    assert "Tests       : ok" in payload["scope_lines"]
    assert "BundleTests : ok" in payload["scope_lines"]
    assert "Focused Profile   : trader" in payload["report_lines"]


def test_release_readiness_command_can_write_deterministic_report_artifact(tmp_path, capsys):
    _seed_release_ready_repo(tmp_path)
    report_path = tmp_path / "evidence" / "release_readiness.txt"

    exit_code = main(
        [
            "release-readiness",
            "--wrapper-root",
            str(tmp_path),
            "--profile",
            "trader",
            "--core-tests-green",
            "--report-path",
            str(report_path),
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    report_text = report_path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert payload["report_path"] == str(report_path.resolve())
    assert report_text.startswith("PATCHOPS RELEASE READINESS\n")
    assert f"Wrapper Project   : {tmp_path.resolve()}" in report_text
    assert "Focused Profile   : trader" in report_text
    assert "Status            : green" in report_text
    assert "Core Tests        : green" in report_text
    assert "Tests             : ok" in report_text
    assert "Bundle Tests      : ok" in report_text
    assert "MISSING BUNDLE RELEASE TESTS" in report_text
    assert "NOTES" in report_text
    assert report_text.endswith(
        "Use --core-tests-green only when the green test state was already proven externally.\n"
    )


def test_release_readiness_command_fails_cleanly_when_required_surfaces_are_missing(tmp_path, capsys):
    _write_file(tmp_path, "docs/project_status.md")
    _write_file(tmp_path, "patchops/cli.py")

    exit_code = main(
        [
            "release-readiness",
            "--wrapper-root",
            str(tmp_path),
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["status"] == "not_ready"
    assert "docs/release_checklist.md" in payload["missing_release_docs"]
    assert "examples/generic_python_patch.json" in payload["missing_release_examples"]
    assert "powershell/Invoke-PatchVerify.ps1" in payload["missing_release_launchers"]
    assert "tests/test_release_readiness_command.py" in payload["missing_release_tests"]
    assert "docs/bundle_release_readiness.md" in payload["missing_bundle_release_docs"]
    assert "tests/test_bundle_post_build_smoke_gate_current.py" in payload["missing_bundle_release_tests"]


def test_release_readiness_command_reports_bundle_gate_gap_even_when_classic_surfaces_are_seeded(tmp_path, capsys):
    for relative_path in (
        *REQUIRED_RELEASE_DOCS,
        *REQUIRED_RELEASE_EXAMPLES,
        *REQUIRED_RELEASE_WORKFLOWS,
        *REQUIRED_RELEASE_LAUNCHERS,
        *REQUIRED_RELEASE_TESTS,
    ):
        _write_file(tmp_path, relative_path)

    exit_code = main(
        [
            "release-readiness",
            "--wrapper-root",
            str(tmp_path),
            "--core-tests-green",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["status"] == "not_ready"
    assert payload["release_tests_ok"] is True
    assert payload["bundle_release_tests_ok"] is False
    assert payload["bundle_release_docs_ok"] is False
    assert "missing bundle release docs" in payload["issues"]
    assert "missing bundle release tests" in payload["issues"]
    assert payload["missing_bundle_release_tests"] == list(REQUIRED_BUNDLE_RELEASE_TESTS)
