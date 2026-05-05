from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Mapping


@dataclass(frozen=True)
class UploaderSafetyFlags:
    """Side-effect flags for uploader probes.

    The foundation/doctor layer is intentionally local-only. Any future live
    browser action must flip an explicit flag so tests and reports can prove
    what happened.
    """

    browser_opened: bool = False
    file_upload_attempted: bool = False
    chatgpt_submit_performed: bool = False
    webdriver_used: bool = False
    cloudflare_bypass_attempted: bool = False
    conversation_text_logged: bool = False
    random_page_click_performed: bool = False

    def to_payload(self) -> Mapping[str, bool]:
        return asdict(self)


@dataclass(frozen=True)
class TargetUrlInfo:
    raw_url: str
    scheme: str
    netloc: str
    path: str
    is_chatgpt: bool
    has_gpt_project_path: bool
    has_conversation_path: bool
    safe_to_use_as_config: bool
    reason: str

    def to_payload(self) -> Mapping[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class DependencyStatus:
    name: str
    import_ok: bool
    version: str | None = None
    error: str | None = None
    required_for: tuple[str, ...] = ()

    def to_payload(self) -> Mapping[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ReportPackageCandidate:
    source_path: str
    staged_path: str
    size_bytes: int
    sha256: str
    safe_name: str
    content_kind: str = "text_report"

    def to_payload(self) -> Mapping[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class UploaderDoctorResult:
    target_url: TargetUrlInfo
    dependencies: tuple[DependencyStatus, ...]
    safety: UploaderSafetyFlags = field(default_factory=UploaderSafetyFlags)
    recommended_mode: str = "doctor_only"
    notes: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return self.target_url.safe_to_use_as_config

    def to_payload(self) -> Mapping[str, object]:
        return {
            "ok": self.ok,
            "target_url": self.target_url.to_payload(),
            "dependencies": [dep.to_payload() for dep in self.dependencies],
            "safety": self.safety.to_payload(),
            "recommended_mode": self.recommended_mode,
            "notes": list(self.notes),
        }
