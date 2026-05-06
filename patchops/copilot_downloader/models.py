from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

FOUNDATION_RESULT_LABEL = "PASS_DOWNLOADER_FOUNDATION_READY"
CONFIG_VALIDATED_LABEL = "PASS_CONFIG_VALIDATED"
CONFIG_MISSING_LABEL = "BLOCKED_CONFIG_MISSING"
CONFIG_INVALID_LABEL = "BLOCKED_CONFIG_INVALID"
PASS_HASH_LEDGER_RECORDED = "PASS_HASH_LEDGER_RECORDED"
BLOCKED_DUPLICATE_ARTIFACT = "BLOCKED_DUPLICATE_ARTIFACT"
PASS_ARTIFACT_CLASSIFIED = "PASS_ARTIFACT_CLASSIFIED"
PASS_BUNDLE_VALIDATED_RUN_BLOCKED = "PASS_BUNDLE_VALIDATED_RUN_BLOCKED"
PASS_STAGED_ARTIFACT_READY = "PASS_STAGED_ARTIFACT_READY"
BLOCKED_STAGE_MISSING_SOURCE = "BLOCKED_STAGE_MISSING_SOURCE"
FAIL_STAGE_WRITE = "FAIL_STAGE_WRITE"
PASS_BROWSER_TARGET_CONFIGURED = "PASS_BROWSER_TARGET_CONFIGURED"
BLOCKED_BROWSER_TARGET_CONFIG_MISSING = "BLOCKED_BROWSER_TARGET_CONFIG_MISSING"
BLOCKED_BROWSER_TARGET_CONFIG_INVALID = "BLOCKED_BROWSER_TARGET_CONFIG_INVALID"

RESULT_LABELS: tuple[str, ...] = (
    FOUNDATION_RESULT_LABEL,
    CONFIG_VALIDATED_LABEL,
    CONFIG_MISSING_LABEL,
    CONFIG_INVALID_LABEL,
    PASS_HASH_LEDGER_RECORDED,
    BLOCKED_DUPLICATE_ARTIFACT,
    PASS_ARTIFACT_CLASSIFIED,
    PASS_BUNDLE_VALIDATED_RUN_BLOCKED,
    PASS_STAGED_ARTIFACT_READY,
    BLOCKED_STAGE_MISSING_SOURCE,
    FAIL_STAGE_WRITE,
    PASS_BROWSER_TARGET_CONFIGURED,
    BLOCKED_BROWSER_TARGET_CONFIG_MISSING,
    BLOCKED_BROWSER_TARGET_CONFIG_INVALID,
    "PASS_BROWSER_READY",
    "PASS_ARTIFACT_DETECTED",
    "PASS_STABLE_ARTIFACT_VALIDATED",
    "PASS_SCRIPT_EXTRACTED_RUN_BLOCKED",
    "PASS_SCRIPT_VALIDATED_RUN_BLOCKED",
    "PASS_PATCHOPS_RUN_COMPLETED",
    "PASS_CANONICAL_REPORT_FOUND",
    "PASS_HANDOFF_WRITTEN",
    "BLOCKED_NO_ARTIFACT",
    "BLOCKED_UNSTABLE_FILE",
    "BLOCKED_INVALID_ARTIFACT",
    "BLOCKED_AMBIGUOUS_ARTIFACTS",
    "BLOCKED_RUN_NOT_AUTHORIZED",
    "BLOCKED_BROWSER_NOT_READY",
    "BLOCKED_AMBIGUOUS_BROWSER_TARGET",
    "BLOCKED_LOGIN_OR_CHALLENGE",
    "FAIL_PATCHOPS_RUN",
    "FAIL_REPORT_MISSING",
    "FAIL_HANDOFF_WRITE",
)

ARTIFACT_KINDS: tuple[str, ...] = (
    "patchops_script_payload",
    "patchops_manifest_json",
    "patchops_bundle_zip",
    "unknown_zip",
    "unsupported_file",
)

SAFETY_FLAG_NAMES: tuple[str, ...] = (
    "webdriver_used",
    "selenium_used",
    "browser_dom_automation_used",
    "cloudflare_bypass_attempted",
    "captcha_bypass_attempted",
    "conversation_text_logged",
    "random_page_click_performed",
    "clipboard_read",
    "clipboard_written",
    "browser_used",
    "file_download_observed",
    "file_upload_attempted",
    "chatgpt_submit_performed",
    "artifact_executed",
    "patchops_invoked",
    "canonical_report_found",
)


@dataclass(frozen=True)
class DownloaderSafetyFlags:
    webdriver_used: bool = False
    selenium_used: bool = False
    browser_dom_automation_used: bool = False
    cloudflare_bypass_attempted: bool = False
    captcha_bypass_attempted: bool = False
    conversation_text_logged: bool = False
    random_page_click_performed: bool = False
    clipboard_read: bool = False
    clipboard_written: bool = False
    browser_used: bool = False
    file_download_observed: bool = False
    file_upload_attempted: bool = False
    chatgpt_submit_performed: bool = False
    artifact_executed: bool = False
    patchops_invoked: bool = False
    canonical_report_found: bool = False

    def to_dict(self) -> dict[str, bool]:
        return {name: bool(getattr(self, name)) for name in SAFETY_FLAG_NAMES}

    def true_flags(self) -> tuple[str, ...]:
        return tuple(name for name, value in self.to_dict().items() if value)


@dataclass(frozen=True)
class DownloaderEvidenceRecord:
    patch_name: str
    result_label: str
    safety: DownloaderSafetyFlags = field(default_factory=DownloaderSafetyFlags)
    details: dict[str, Any] = field(default_factory=dict)
    schema_version: int = 1
    producer: str = "patchops.copilot_downloader"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "producer": self.producer,
            "patch_name": self.patch_name,
            "result_label": self.result_label,
            "safety": self.safety.to_dict(),
            "details": self.details,
        }


@dataclass(frozen=True)
class DownloaderDoctorResult:
    ok: bool
    result_label: str
    checks: dict[str, bool]
    safety: DownloaderSafetyFlags = field(default_factory=DownloaderSafetyFlags)
    evidence_files: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "result_label": self.result_label,
            "checks": dict(self.checks),
            "safety": self.safety.to_dict(),
            "evidence_files": dict(self.evidence_files),
        }


@dataclass(frozen=True)
class DownloaderPaths:
    repo_root: Path
    runtime_root: Path
    evidence_root: Path

    def to_dict(self) -> dict[str, str]:
        return {
            "repo_root": str(self.repo_root),
            "runtime_root": str(self.runtime_root),
            "evidence_root": str(self.evidence_root),
        }


@dataclass(frozen=True)
class ArtifactCandidate:
    path: Path
    source: str
    extension: str
    size_bytes: int
    modified_timestamp: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "source": self.source,
            "extension": self.extension,
            "size_bytes": self.size_bytes,
            "modified_timestamp": self.modified_timestamp,
        }


@dataclass(frozen=True)
class ArtifactScanResult:
    result_label: str
    candidates: tuple[ArtifactCandidate, ...]
    ignored: tuple[dict[str, Any], ...] = ()

    @property
    def ok(self) -> bool:
        return self.result_label in {
            "PASS_ARTIFACT_DETECTED",
            "PASS_STABLE_ARTIFACT_VALIDATED",
            "BLOCKED_NO_ARTIFACT",
            "BLOCKED_AMBIGUOUS_ARTIFACTS",
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_label": self.result_label,
            "candidate_count": len(self.candidates),
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "ignored": list(self.ignored),
        }


@dataclass(frozen=True)
class ArtifactClassification:
    artifact_kind: str
    result_label: str
    path: Path
    reasons: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_kind": self.artifact_kind,
            "result_label": self.result_label,
            "path": str(self.path),
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class ShapeValidationResult:
    result_label: str
    artifact_kind: str
    path: Path
    issues: tuple[str, ...] = ()
    checks: dict[str, bool] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.issues and self.result_label in {
            "PASS_SCRIPT_VALIDATED_RUN_BLOCKED",
            PASS_BUNDLE_VALIDATED_RUN_BLOCKED,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_label": self.result_label,
            "artifact_kind": self.artifact_kind,
            "path": str(self.path),
            "issues": list(self.issues),
            "checks": dict(self.checks),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class StagedArtifact:
    artifact_sha256: str
    artifact_kind: str
    staging_dir: Path
    raw_artifact_path: Path
    metadata_path: Path
    normalized_script_path: Path | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_sha256": self.artifact_sha256,
            "artifact_kind": self.artifact_kind,
            "staging_dir": str(self.staging_dir),
            "raw_artifact_path": str(self.raw_artifact_path),
            "metadata_path": str(self.metadata_path),
            "normalized_script_path": None if self.normalized_script_path is None else str(self.normalized_script_path),
        }


@dataclass(frozen=True)
class BrowserTargetConfig:
    config_path: Path
    target_url: str
    target_url_sha256: str
    redacted_target_display: str
    evidence_dir: Path
    policy: dict[str, bool]
    schema_version: int = 1
    producer: str = "patchops.copilot_downloader"

    def to_private_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "producer": self.producer,
            "config_path": str(self.config_path),
            "target_url": self.target_url,
            "target_url_sha256": self.target_url_sha256,
            "redacted_target_display": self.redacted_target_display,
            "evidence_dir": str(self.evidence_dir),
            "policy": dict(self.policy),
        }

    def to_evidence_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "producer": self.producer,
            "config_path": str(self.config_path),
            "target_url_sha256": self.target_url_sha256,
            "redacted_target_display": self.redacted_target_display,
            "evidence_dir": str(self.evidence_dir),
            "policy": dict(self.policy),
        }