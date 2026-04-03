from __future__ import annotations

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
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"


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
