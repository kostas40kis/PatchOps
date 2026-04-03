from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

MARKER = "PATCHOPS_MP44_STRUCTURED_BUG_ARTIFACT_MODEL"
TEST_MARKER = "PATCHOPS_MP44_STRUCTURED_BUG_ARTIFACT_MODEL_TEST"

MODULE_TEXT = '''from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MARKER = "PATCHOPS_MP44_STRUCTURED_BUG_ARTIFACT_MODEL"


@dataclass(slots=True)
class SuspiciousRunArtifact:
    detection_reason: str
    failure_class: str
    report_path: str | Path
    workflow_mode: str
    manifest_path: str | Path | None = None
    recommended_follow_up: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "detection_reason": self.detection_reason,
            "failure_class": self.failure_class,
            "report_path": str(self.report_path),
            "workflow_mode": self.workflow_mode,
            "manifest_path": None if self.manifest_path is None else str(self.manifest_path),
            "recommended_follow_up": self.recommended_follow_up,
        }

    def to_json_text(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\\n"
'''

TEST_TEXT = '''from __future__ import annotations

import json
from pathlib import Path

from patchops.suspicious_artifacts import SuspiciousRunArtifact

MARKER = "PATCHOPS_MP44_STRUCTURED_BUG_ARTIFACT_MODEL_TEST"


def test_bug_artifact_to_dict_contains_required_fields(tmp_path: Path):
    artifact = SuspiciousRunArtifact(
        detection_reason="summary contradicts required command evidence",
        failure_class="wrapper_failure",
        report_path=tmp_path / "latest_report.txt",
        workflow_mode="apply",
        manifest_path=tmp_path / "patch_manifest.json",
        recommended_follow_up="inspect report and repair wrapper layer",
    )

    payload = artifact.to_dict()

    assert payload["detection_reason"] == "summary contradicts required command evidence"
    assert payload["failure_class"] == "wrapper_failure"
    assert payload["workflow_mode"] == "apply"
    assert payload["report_path"].endswith("latest_report.txt")
    assert payload["manifest_path"].endswith("patch_manifest.json")
    assert payload["recommended_follow_up"] == "inspect report and repair wrapper layer"


def test_bug_artifact_json_text_is_machine_readable(tmp_path: Path):
    artifact = SuspiciousRunArtifact(
        detection_reason="critical provenance fields missing",
        failure_class="wrapper_failure",
        report_path=tmp_path / "report.txt",
        workflow_mode="verify",
        recommended_follow_up="collect fresh wrapper evidence",
    )

    parsed = json.loads(artifact.to_json_text())

    assert parsed["detection_reason"] == "critical provenance fields missing"
    assert parsed["failure_class"] == "wrapper_failure"
    assert parsed["workflow_mode"] == "verify"
    assert parsed["manifest_path"] is None
    assert parsed["recommended_follow_up"] == "collect fresh wrapper evidence"


def test_bug_artifact_path_fields_are_stringified(tmp_path: Path):
    artifact = SuspiciousRunArtifact(
        detection_reason="latest copied report missing",
        failure_class="wrapper_failure",
        report_path=tmp_path / "nested" / "report.txt",
        workflow_mode="export_handoff",
        manifest_path=tmp_path / "patch_manifest.json",
    )

    payload = artifact.to_dict()

    assert isinstance(payload["report_path"], str)
    assert isinstance(payload["manifest_path"], str)


def test_bug_artifact_keeps_shape_compact_when_manifest_path_missing(tmp_path: Path):
    artifact = SuspiciousRunArtifact(
        detection_reason="core report fields missing",
        failure_class="wrapper_failure",
        report_path=tmp_path / "report.txt",
        workflow_mode="wrapper_retry",
        manifest_path=None,
        recommended_follow_up=None,
    )

    payload = artifact.to_dict()
    assert set(payload.keys()) == {
        "detection_reason",
        "failure_class",
        "report_path",
        "workflow_mode",
        "manifest_path",
        "recommended_follow_up",
    }
'''


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def backup_if_exists(repo_root: Path, backup_root: Path, relative_path: str) -> None:
    source = repo_root / relative_path
    if not source.exists():
        return
    destination = backup_root / relative_path
    ensure_parent(destination)
    shutil.copy2(source, destination)


def main() -> int:
    repo_root = Path(sys.argv[1]).resolve()
    backup_root = Path(sys.argv[2]).resolve()
    backup_root.mkdir(parents=True, exist_ok=True)

    module_path = repo_root / 'patchops' / 'suspicious_artifacts.py'
    test_path = repo_root / 'tests' / 'test_suspicious_bug_artifact_model_current.py'

    already_present = False
    if module_path.exists() and test_path.exists():
        module_text = module_path.read_text(encoding='utf-8')
        test_text = test_path.read_text(encoding='utf-8')
        already_present = MARKER in module_text and TEST_MARKER in test_text

    if not already_present:
        backup_if_exists(repo_root, backup_root, 'patchops/suspicious_artifacts.py')
        backup_if_exists(repo_root, backup_root, 'tests/test_suspicious_bug_artifact_model_current.py')
        ensure_parent(module_path)
        module_path.write_text(MODULE_TEXT, encoding='utf-8')
        ensure_parent(test_path)
        test_path.write_text(TEST_TEXT, encoding='utf-8')

    print(json.dumps({
        'patched_files': [
            'patchops\\suspicious_artifacts.py',
            'tests\\test_suspicious_bug_artifact_model_current.py',
        ],
        'backup_root': str(backup_root),
        'already_present': already_present,
    }, indent=2))
    print(f'module_path={module_path}')
    print(f'test_path={test_path}')
    print(f'already_present={already_present}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())