from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

MODULE_TEXT = '''from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MARKER = "PATCHOPS_MP46A_ARTIFACT_REPORT_MENTION_REPAIR"


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


def emit_suspicious_run_artifact(
    artifact: SuspiciousRunArtifact,
    output_path: str | Path,
    *,
    emit: bool = False,
) -> Path | None:
    if not emit:
        return None
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(artifact.to_json_text(), encoding="utf-8")
    return destination


def suspicious_run_artifact_report_lines(artifact_path: str | Path | None) -> list[str]:
    if artifact_path is None:
        return []
    path = Path(artifact_path)
    return [f"Suspicious-run artifact emitted : {path}"]
'''

TEST_TEXT = '''from __future__ import annotations

from pathlib import Path

from patchops.suspicious_artifacts import (
    SuspiciousRunArtifact,
    emit_suspicious_run_artifact,
    suspicious_run_artifact_report_lines,
)

MARKER = "PATCHOPS_MP46A_ARTIFACT_REPORT_MENTION_REPAIR_TEST"


def _artifact(tmp_path: Path) -> SuspiciousRunArtifact:
    return SuspiciousRunArtifact(
        detection_reason="summary contradicts required command evidence",
        failure_class="wrapper_failure",
        report_path=tmp_path / "latest_report.txt",
        workflow_mode="apply",
        manifest_path=tmp_path / "patch_manifest.json",
        recommended_follow_up="inspect wrapper evidence before widening scope",
    )


def test_report_lines_are_empty_when_no_artifact_was_emitted(tmp_path: Path):
    lines = suspicious_run_artifact_report_lines(None)
    assert lines == []


def test_report_lines_include_emitted_artifact_path(tmp_path: Path):
    artifact_path = tmp_path / "artifacts" / "suspicious_run.json"
    emitted = emit_suspicious_run_artifact(_artifact(tmp_path), artifact_path, emit=True)
    lines = suspicious_run_artifact_report_lines(emitted)
    assert len(lines) == 1
    assert lines[0].startswith("Suspicious-run artifact emitted : ")
    assert str(artifact_path) in lines[0]


def test_report_line_wording_stays_compact(tmp_path: Path):
    artifact_path = tmp_path / "artifact.json"
    line = suspicious_run_artifact_report_lines(artifact_path)[0]
    assert "emitted" in line.lower()
    assert "artifact" in line.lower()
    assert "report" not in line.lower()
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
    test_path = repo_root / 'tests' / 'test_suspicious_artifact_report_mention_current.py'

    backup_if_exists(repo_root, backup_root, 'patchops/suspicious_artifacts.py')
    backup_if_exists(repo_root, backup_root, 'tests/test_suspicious_artifact_report_mention_current.py')

    ensure_parent(module_path)
    module_path.write_text(MODULE_TEXT, encoding='utf-8')
    ensure_parent(test_path)
    test_path.write_text(TEST_TEXT, encoding='utf-8')

    print(json.dumps({
        'patched_files': [
            'patchops\\suspicious_artifacts.py',
            'tests\\test_suspicious_artifact_report_mention_current.py',
        ],
        'backup_root': str(backup_root),
    }, indent=2))
    print(f'module_path={module_path}')
    print(f'test_path={test_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())