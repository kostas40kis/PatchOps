from __future__ import annotations



import json

import re

from dataclasses import asdict, dataclass, field

from datetime import datetime, timezone

from pathlib import Path

from typing import Any



from patchops.chatgpt_uploader.config import ChatGptCopilotTargetConfig





DEFAULT_SAFETY_FLAGS: dict[str, bool] = {

    "selenium_used": False,

    "webdriver_used": False,

    "browser_dom_automation_used": False,

    "cloudflare_bypass_attempted": False,

    "captcha_bypass_attempted": False,

    "file_upload_attempted": False,

    "file_dialog_detected": False,

    "file_dialog_path_written": False,

    "attachment_confirmed": False,

    "chatgpt_submit_performed": False,

    "conversation_text_logged": False,

    "random_page_click_performed": False,

    "clipboard_written": False,

    "paste_attempted": False,

}





def utc_now_iso() -> str:

    return datetime.now(timezone.utc).isoformat()





def safe_run_id(value: str) -> str:

    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")

    return cleaned or "chatgpt_uploader_run"





@dataclass

class UploaderEvidence:

    run_id: str

    phase: str

    started_at: str

    finished_at: str | None = None

    result: str = "RUNNING"

    safety_flags: dict[str, bool] = field(default_factory=lambda: dict(DEFAULT_SAFETY_FLAGS))

    target: dict[str, Any] = field(default_factory=dict)

    edge_window: dict[str, Any] = field(default_factory=dict)

    details: dict[str, Any] = field(default_factory=dict)

    errors: list[dict[str, Any]] = field(default_factory=list)



    @classmethod

    def start(cls, phase: str, run_id: str | None = None) -> "UploaderEvidence":

        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        return cls(run_id=safe_run_id(run_id or f"{phase}_{stamp}"), phase=phase, started_at=utc_now_iso())



    def attach_config(self, config: ChatGptCopilotTargetConfig, config_path: str | Path) -> None:

        redacted = config.to_redacted_payload()

        redacted["config_path"] = str(config_path)

        self.target = redacted



    def set_detail(self, key: str, value: Any) -> None:

        self.details[key] = value



    def set_edge_window(self, payload: dict[str, Any]) -> None:

        self.edge_window = dict(payload)



    def set_safety_flag(self, key: str, value: bool) -> None:

        if key not in DEFAULT_SAFETY_FLAGS:

            raise KeyError(f"Unknown safety flag: {key}")

        self.safety_flags[key] = bool(value)



    def add_error(self, *, stage: str, message: str, error_type: str | None = None) -> None:

        self.errors.append(

            {

                "stage": stage,

                "error_type": error_type,

                "message": message,

                "recorded_at": utc_now_iso(),

            }

        )



    def finish(self, result: str) -> None:

        self.result = result

        self.finished_at = utc_now_iso()



    def to_payload(self) -> dict[str, Any]:

        return asdict(self)





def render_text_evidence(evidence: UploaderEvidence) -> str:

    payload = evidence.to_payload()

    lines: list[str] = []

    lines.append("PATCHOPS CHATGPT UPLOADER EVIDENCE")

    lines.append("=" * 44)

    lines.append(f"RunId     : {payload['run_id']}")

    lines.append(f"Phase     : {payload['phase']}")

    lines.append(f"Result    : {payload['result']}")

    lines.append(f"Started   : {payload['started_at']}")

    lines.append(f"Finished  : {payload['finished_at']}")

    lines.append("")

    lines.append("TARGET")

    lines.append("-" * 44)

    for key, value in sorted(payload.get("target", {}).items()):

        lines.append(f"{key} : {value}")

    lines.append("")

    lines.append("EDGE WINDOW")

    lines.append("-" * 44)

    for key, value in sorted(payload.get("edge_window", {}).items()):

        lines.append(f"{key} : {value}")

    lines.append("")

    lines.append("SAFETY FLAGS")

    lines.append("-" * 44)

    for key, value in sorted(payload.get("safety_flags", {}).items()):

        lines.append(f"{key} : {str(value).lower()}")

    lines.append("")

    lines.append("DETAILS")

    lines.append("-" * 44)

    for key, value in sorted(payload.get("details", {}).items()):

        lines.append(f"{key} : {value}")

    lines.append("")

    lines.append("ERRORS")

    lines.append("-" * 44)

    errors = payload.get("errors", [])

    if not errors:

        lines.append("<none>")

    else:

        for item in errors:

            lines.append(json.dumps(item, sort_keys=True))

    lines.append("")

    return "\n".join(lines)





def write_evidence_pair(evidence: UploaderEvidence, output_dir: str | Path) -> tuple[Path, Path]:

    out_dir = Path(output_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    run_id = safe_run_id(evidence.run_id)

    json_path = out_dir / f"{run_id}.json"

    txt_path = out_dir / f"{run_id}.txt"

    json_path.write_text(json.dumps(evidence.to_payload(), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    txt_path.write_text(render_text_evidence(evidence), encoding="utf-8")

    return json_path, txt_path



# PATCHOPS_U2_01C_EVIDENCE_COMPAT_START
# Backward-compatible uploader evidence API restored by U2.1C.

REQUIRED_SAFETY_FLAG_NAMES = tuple(DEFAULT_SAFETY_FLAGS.keys())


def default_safety_flags() -> dict[str, bool]:
    return dict(DEFAULT_SAFETY_FLAGS)


def new_evidence(
    phase: str = "chatgpt_uploader",
    run_id: str | None = None,
    **details: Any,
) -> dict[str, Any]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    payload: dict[str, Any] = {
        "run_id": safe_run_id(run_id or f"{phase}_{stamp}"),
        "phase": phase,
        "started_at": utc_now_iso(),
        "finished_at": None,
        "result": "RUNNING",
        "safety_flags": default_safety_flags(),
        "target": {},
        "edge_window": {},
        "details": {},
        "errors": [],
    }
    if details:
        payload["details"].update(details)
    return payload


def finalize_evidence(evidence: UploaderEvidence | dict[str, Any], result: str, **details: Any) -> UploaderEvidence | dict[str, Any]:
    if isinstance(evidence, UploaderEvidence):
        for key, value in details.items():
            evidence.set_detail(key, value)
        evidence.finish(result)
        return evidence

    evidence.setdefault("details", {}).update(details)
    evidence["result"] = result
    evidence["finished_at"] = utc_now_iso()
    return evidence


def _dict_evidence_to_uploader_evidence(payload: dict[str, Any]) -> UploaderEvidence:
    evidence = UploaderEvidence(
        run_id=str(payload.get("run_id") or "chatgpt_uploader_run"),
        phase=str(payload.get("phase") or "chatgpt_uploader"),
        started_at=str(payload.get("started_at") or utc_now_iso()),
        finished_at=payload.get("finished_at"),
        result=str(payload.get("result") or "RUNNING"),
        safety_flags=dict(payload.get("safety_flags") or DEFAULT_SAFETY_FLAGS),
        target=dict(payload.get("target") or {}),
        edge_window=dict(payload.get("edge_window") or {}),
        details=dict(payload.get("details") or {}),
        errors=list(payload.get("errors") or []),
    )
    return evidence


def write_evidence(
    evidence: UploaderEvidence | dict[str, Any],
    output_dir: str | Path,
    *,
    run_id: str | None = None,
) -> tuple[Path, Path]:
    if isinstance(evidence, dict):
        if run_id:
            evidence["run_id"] = safe_run_id(run_id)
        return write_evidence_pair(_dict_evidence_to_uploader_evidence(evidence), output_dir)

    if run_id:
        evidence.run_id = safe_run_id(run_id)
    return write_evidence_pair(evidence, output_dir)
# PATCHOPS_U2_01C_EVIDENCE_COMPAT_END

# PATCHOPS_U2_1QK_EVIDENCE_FINALIZE_COMPAT_START
_PATCHOPS_U2_1QK_PREVIOUS_FINALIZE_EVIDENCE = finalize_evidence


def finalize_evidence(evidence, result=None, *args, status=None, result_label=None, reason="", **kwargs):
    if result is None:
        result = result_label or status or "PASS"
    if status is None:
        status = result_label or result
    if result_label is None:
        result_label = status or result

    try:
        return _PATCHOPS_U2_1QK_PREVIOUS_FINALIZE_EVIDENCE(
            evidence,
            result,
            *args,
            status=status,
            result_label=result_label,
            reason=reason,
            **kwargs,
        )
    except TypeError:
        return _PATCHOPS_U2_1QK_PREVIOUS_FINALIZE_EVIDENCE(
            evidence,
            result=result,
            status=status,
            result_label=result_label,
            reason=reason,
            **kwargs,
        )
# PATCHOPS_U2_1QK_EVIDENCE_FINALIZE_COMPAT_END

# PATCHOPS_U2_1QL_EVIDENCE_BASENAME_COMPAT_START
import json as _patchops_u2_1ql_json
from dataclasses import asdict as _patchops_u2_1ql_asdict
from dataclasses import dataclass as _patchops_u2_1ql_dataclass
from dataclasses import is_dataclass as _patchops_u2_1ql_is_dataclass
from pathlib import Path as _PatchOpsU21QLPath


_PATCHOPS_U2_1QL_PREVIOUS_FINALIZE_EVIDENCE = finalize_evidence
_PATCHOPS_U2_1QL_PREVIOUS_WRITE_EVIDENCE = write_evidence


@_patchops_u2_1ql_dataclass(frozen=True)
class EvidenceWritePaths:
    json_path: _PatchOpsU21QLPath
    txt_path: _PatchOpsU21QLPath

    @property
    def json(self):
        return self.json_path

    @property
    def txt(self):
        return self.txt_path

    def to_payload(self):
        return {
            "json_path": str(self.json_path),
            "txt_path": str(self.txt_path),
            "json": str(self.json_path),
            "txt": str(self.txt_path),
        }


def _patchops_u2_1ql_payload_from_evidence(evidence):
    if isinstance(evidence, dict):
        return dict(evidence)
    if hasattr(evidence, "to_payload"):
        try:
            payload = evidence.to_payload()
            if isinstance(payload, dict):
                return dict(payload)
        except Exception:
            pass
    if _patchops_u2_1ql_is_dataclass(evidence):
        try:
            return dict(_patchops_u2_1ql_asdict(evidence))
        except Exception:
            pass
    if hasattr(evidence, "__dict__"):
        return dict(evidence.__dict__)
    return {"evidence": str(evidence)}


def _patchops_u2_1ql_copy_payload_to_evidence(evidence, payload):
    if not isinstance(payload, dict):
        return
    if isinstance(evidence, dict):
        evidence.update(payload)
        return
    for key, value in payload.items():
        try:
            setattr(evidence, key, value)
        except Exception:
            pass


def _patchops_u2_1ql_finalize_payload_defaults(payload, *, result=None, status=None, result_label=None, reason=""):
    payload = dict(payload or {})
    if result is None:
        result = result_label or status or payload.get("result") or payload.get("result_label") or payload.get("status") or "PASS"
    if status is None:
        status = payload.get("status") or result_label or result
    if result_label is None:
        result_label = payload.get("result_label") or status or result

    payload["result"] = result
    payload["status"] = status
    payload["result_label"] = result_label
    payload["reason"] = reason if reason != "" else payload.get("reason", "")

    safety_flags = dict(payload.get("safety_flags") or {})
    for key in (
        "browser_picker_opened",
        "file_upload_attempted",
        "chatgpt_submit_performed",
        "conversation_text_logged",
        "selenium_used",
        "webdriver_used",
        "browser_dom_automation_used",
    ):
        safety_flags[key] = bool(payload.get(key, safety_flags.get(key, False)))
        payload[key] = safety_flags[key]
    payload["safety_flags"] = safety_flags

    return payload


def finalize_evidence(evidence, result=None, *args, status=None, result_label=None, reason="", **kwargs):
    if result is None:
        result = result_label or status or "PASS"
    if status is None:
        status = result_label or result
    if result_label is None:
        result_label = status or result

    finalized = None
    try:
        finalized = _PATCHOPS_U2_1QL_PREVIOUS_FINALIZE_EVIDENCE(
            evidence,
            result,
            *args,
            status=status,
            result_label=result_label,
            reason=reason,
            **kwargs,
        )
    except TypeError:
        finalized = _PATCHOPS_U2_1QL_PREVIOUS_FINALIZE_EVIDENCE(
            evidence,
            result=result,
            status=status,
            result_label=result_label,
            reason=reason,
            **kwargs,
        )

    payload = _patchops_u2_1ql_payload_from_evidence(finalized if finalized is not None else evidence)
    payload = _patchops_u2_1ql_finalize_payload_defaults(
        payload,
        result=result,
        status=status,
        result_label=result_label,
        reason=reason,
    )
    _patchops_u2_1ql_copy_payload_to_evidence(evidence, payload)
    if finalized is not None and finalized is not evidence:
        _patchops_u2_1ql_copy_payload_to_evidence(finalized, payload)
    return finalized if finalized is not None else evidence


def _patchops_u2_1ql_render_evidence_text(payload):
    lines = [
        "PATCHOPS CHATGPT UPLOADER EVIDENCE",
        "==================================",
        f"STATUS: {payload.get('status', '')}",
        f"RESULT: {payload.get('result', '')}",
        f"RESULT_LABEL: {payload.get('result_label', '')}",
        f"REASON: {payload.get('reason', '')}",
        f"TARGET_CONFIG_PATH: {payload.get('target_config_path', '')}",
        f"TARGET_URL_REDACTED: {payload.get('target_url_redacted', payload.get('redacted_target_url', ''))}",
        f"TARGET_URL_SHA256: {payload.get('target_url_sha256', '')}",
        "BROWSER_PICKER_OPENED: false",
        "FILE_UPLOAD_ATTEMPTED: false",
        "CHATGPT_SUBMIT_PERFORMED: false",
        "CONVERSATION_TEXT_LOGGED: false",
        "SELENIUM_USED: false",
        "WEBDRIVER_USED: false",
        "BROWSER_DOM_AUTOMATION_USED: false",
        "",
    ]
    return "\n".join(lines)


def write_evidence(evidence, output_dir, *args, basename=None, **kwargs):
    if basename is None:
        try:
            return _PATCHOPS_U2_1QL_PREVIOUS_WRITE_EVIDENCE(evidence, output_dir, *args, **kwargs)
        except TypeError:
            return _PATCHOPS_U2_1QL_PREVIOUS_WRITE_EVIDENCE(evidence, output_dir)

    out_dir = _PatchOpsU21QLPath(output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    safe_basename = str(basename or "evidence").strip() or "evidence"
    safe_basename = safe_basename.replace("\\", "_").replace("/", "_").replace(":", "_")

    json_path = out_dir / f"{safe_basename}.json"
    txt_path = out_dir / f"{safe_basename}.txt"

    payload = _patchops_u2_1ql_payload_from_evidence(evidence)
    payload = _patchops_u2_1ql_finalize_payload_defaults(payload)

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    payload["json"] = str(json_path)
    payload["txt"] = str(txt_path)

    json_path.write_text(
        _patchops_u2_1ql_json.dumps(payload, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    txt_path.write_text(_patchops_u2_1ql_render_evidence_text(payload), encoding="utf-8")

    return EvidenceWritePaths(json_path=json_path, txt_path=txt_path)
# PATCHOPS_U2_1QL_EVIDENCE_BASENAME_COMPAT_END

# PATCHOPS_U2_1QM_EVIDENCE_LOWERCASE_TEXT_FLAGS_START
from pathlib import Path as _PatchOpsU21QMPath


_PATCHOPS_U2_1QM_PREVIOUS_WRITE_EVIDENCE = write_evidence


def _patchops_u2_1qm_extract_txt_path(paths):
    if paths is None:
        return None

    for attr in ("txt_path", "txt", "text_path"):
        if hasattr(paths, attr):
            value = getattr(paths, attr)
            if value:
                return _PatchOpsU21QMPath(value)

    if isinstance(paths, dict):
        for key in ("txt_path", "txt", "text_path"):
            value = paths.get(key)
            if value:
                return _PatchOpsU21QMPath(value)

    if isinstance(paths, (tuple, list)):
        for value in paths:
            candidate = _PatchOpsU21QMPath(value)
            if candidate.suffix.lower() == ".txt":
                return candidate

    return None


def _patchops_u2_1qm_ensure_legacy_lowercase_text_flags(txt_path):
    if txt_path is None:
        return

    path = _PatchOpsU21QMPath(txt_path)
    if not path.exists() or not path.is_file():
        return

    text = path.read_text(encoding="utf-8", errors="replace")

    required_lines = [
        "file_upload_attempted: False",
        "chatgpt_submit_performed: False",
        "conversation_text_logged: False",
        "selenium_used: False",
        "webdriver_used: False",
        "browser_dom_automation_used: False",
    ]

    missing = [line for line in required_lines if line not in text]
    if not missing:
        return

    if text and not text.endswith("\n"):
        text += "\n"

    text += "\n".join(missing) + "\n"
    path.write_text(text, encoding="utf-8")


def write_evidence(evidence, output_dir, *args, basename=None, **kwargs):
    try:
        if basename is None:
            paths = _PATCHOPS_U2_1QM_PREVIOUS_WRITE_EVIDENCE(evidence, output_dir, *args, **kwargs)
        else:
            paths = _PATCHOPS_U2_1QM_PREVIOUS_WRITE_EVIDENCE(evidence, output_dir, *args, basename=basename, **kwargs)
    except TypeError:
        if basename is None:
            paths = _PATCHOPS_U2_1QM_PREVIOUS_WRITE_EVIDENCE(evidence, output_dir, *args, **kwargs)
        else:
            try:
                paths = _PATCHOPS_U2_1QM_PREVIOUS_WRITE_EVIDENCE(evidence, output_dir, *args, **kwargs)
            except TypeError:
                paths = _PATCHOPS_U2_1QM_PREVIOUS_WRITE_EVIDENCE(evidence, output_dir)

    _patchops_u2_1qm_ensure_legacy_lowercase_text_flags(_patchops_u2_1qm_extract_txt_path(paths))
    return paths
# PATCHOPS_U2_1QM_EVIDENCE_LOWERCASE_TEXT_FLAGS_END
