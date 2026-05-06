from __future__ import annotations



import hashlib

import json

from dataclasses import dataclass

from datetime import datetime, timezone

from pathlib import Path

from typing import Any, Mapping

from urllib.parse import urlparse





DEFAULT_CONFIG_RELATIVE_PATH = Path("data/config/chatgpt_copilot_target.json")

SCHEMA_VERSION = "1"

SUPPORTED_BROWSERS = {"msedge"}

SUPPORTED_MODES = {"operator_set", "launch_target", "normal_edge_session"}





def utc_now_iso() -> str:

    return datetime.now(timezone.utc).isoformat()





def target_url_sha256(target_url: str) -> str:

    return hashlib.sha256(target_url.encode("utf-8")).hexdigest()





def validate_target_url(target_url: str) -> str:

    if not isinstance(target_url, str) or not target_url.strip():

        raise ValueError("target_url must be a non-empty string")



    normalized = target_url.strip()

    if normalized != target_url:

        raise ValueError("target_url must not contain surrounding whitespace")



    parsed = urlparse(normalized)

    if parsed.scheme != "https":

        raise ValueError("target_url must use https")



    if parsed.netloc.lower() != "chatgpt.com":

        raise ValueError("target_url must point to chatgpt.com")



    if "/c/" not in parsed.path:

        raise ValueError("target_url must point to a specific ChatGPT conversation path containing /c/")



    return normalized





def redact_target_url(target_url: str) -> str:

    normalized = validate_target_url(target_url)

    parsed = urlparse(normalized)

    parts = [part for part in parsed.path.split("/") if part]

    redacted_parts: list[str] = []



    i = 0

    while i < len(parts):

        part = parts[i]

        redacted_parts.append(part)

        if part == "c" and i + 1 < len(parts):

            conversation_id = parts[i + 1]

            if len(conversation_id) <= 12:

                redacted_parts.append("<conversation>")

            else:

                redacted_parts.append(f"{conversation_id[:8]}...{conversation_id[-8:]}")

            i += 2

            continue

        i += 1



    return f"{parsed.scheme}://{parsed.netloc}/" + "/".join(redacted_parts)





def default_config_path(repo_root: str | Path | None = None) -> Path:

    if repo_root is None:

        return DEFAULT_CONFIG_RELATIVE_PATH

    return Path(repo_root) / DEFAULT_CONFIG_RELATIVE_PATH





@dataclass(frozen=True)

class ChatGptCopilotTargetConfig:

    target_url: str

    browser: str = "msedge"

    mode: str = "operator_set"

    allow_real_edge_default: bool = True

    allow_upload_default: bool = False

    allow_send_default: bool = False

    created_at: str | None = None

    target_url_sha256: str | None = None

    schema_version: str = SCHEMA_VERSION

    source_patch: str | None = None



    def __post_init__(self) -> None:

        normalized_url = validate_target_url(self.target_url)

        if self.target_url != normalized_url:

            object.__setattr__(self, "target_url", normalized_url)



        if self.schema_version != SCHEMA_VERSION:

            raise ValueError(f"Unsupported target config schema_version: {self.schema_version!r}")



        if self.browser not in SUPPORTED_BROWSERS:

            raise ValueError(f"Unsupported browser: {self.browser!r}")



        if self.mode not in SUPPORTED_MODES:

            raise ValueError(f"Unsupported mode: {self.mode!r}")



        expected_hash = target_url_sha256(normalized_url)

        if self.target_url_sha256 is not None and self.target_url_sha256 != expected_hash:

            raise ValueError("target_url_sha256 does not match target_url")



        if self.target_url_sha256 is None:

            object.__setattr__(self, "target_url_sha256", expected_hash)



        if self.created_at is None:

            object.__setattr__(self, "created_at", utc_now_iso())



        if self.allow_send_default and not self.allow_upload_default:

            raise ValueError("allow_send_default cannot be true when allow_upload_default is false")



    @classmethod

    def from_payload(cls, payload: Mapping[str, Any]) -> "ChatGptCopilotTargetConfig":

        return cls(

            target_url=str(payload["target_url"]),

            browser=str(payload.get("browser", "msedge")),

            mode=str(payload.get("mode", "operator_set")),

            allow_real_edge_default=bool(payload.get("allow_real_edge_default", True)),

            allow_upload_default=bool(payload.get("allow_upload_default", False)),

            allow_send_default=bool(payload.get("allow_send_default", False)),

            created_at=payload.get("created_at"),

            target_url_sha256=payload.get("target_url_sha256"),

            schema_version=str(payload.get("schema_version", SCHEMA_VERSION)),

            source_patch=payload.get("source_patch"),

        )



    def to_payload(self) -> dict[str, Any]:

        return {

            "schema_version": self.schema_version,

            "target_url": self.target_url,

            "browser": self.browser,

            "mode": self.mode,

            "allow_real_edge_default": self.allow_real_edge_default,

            "allow_upload_default": self.allow_upload_default,

            "allow_send_default": self.allow_send_default,

            "created_at": self.created_at,

            "target_url_sha256": self.target_url_sha256,

            "source_patch": self.source_patch,

        }



    def to_redacted_payload(self) -> dict[str, Any]:

        return {

            "schema_version": self.schema_version,

            "target_url_redacted": redact_target_url(self.target_url),

            "browser": self.browser,

            "mode": self.mode,

            "allow_real_edge_default": self.allow_real_edge_default,

            "allow_upload_default": self.allow_upload_default,

            "allow_send_default": self.allow_send_default,

            "created_at": self.created_at,

            "target_url_sha256": self.target_url_sha256,

            "source_patch": self.source_patch,

        }





def read_target_config(path: str | Path = DEFAULT_CONFIG_RELATIVE_PATH) -> ChatGptCopilotTargetConfig:

    config_path = Path(path)

    payload = json.loads(config_path.read_text(encoding="utf-8"))

    if not isinstance(payload, dict):

        raise ValueError("target config must be a JSON object")

    return ChatGptCopilotTargetConfig.from_payload(payload)





def write_target_config(

    path: str | Path,

    *,

    target_url: str,

    browser: str = "msedge",

    mode: str = "operator_set",

    allow_real_edge_default: bool = True,

    allow_upload_default: bool = False,

    allow_send_default: bool = False,

    source_patch: str | None = None,

) -> ChatGptCopilotTargetConfig:

    config = ChatGptCopilotTargetConfig(

        target_url=target_url,

        browser=browser,

        mode=mode,

        allow_real_edge_default=allow_real_edge_default,

        allow_upload_default=allow_upload_default,

        allow_send_default=allow_send_default,

        source_patch=source_patch,

    )

    config_path = Path(path)

    config_path.parent.mkdir(parents=True, exist_ok=True)

    config_path.write_text(json.dumps(config.to_payload(), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return config



# PATCHOPS_U2_01C_CONFIG_COMPAT_START
# Backward-compatible uploader config API restored by U2.1C.
# This preserves the newer U2.0 names while restoring the accepted U2.x names used by later modules.

class ConfigValidationError(ValueError):
    """Raised when the ChatGPT uploader target config is invalid."""


def validate_target_url(target_url: str) -> str:  # type: ignore[no-redef]
    if not isinstance(target_url, str) or not target_url.strip():
        raise ConfigValidationError("target_url must be a non-empty string")

    normalized = target_url.strip()
    if normalized != target_url:
        raise ConfigValidationError("target_url must not contain surrounding whitespace")

    parsed = urlparse(normalized)
    if parsed.scheme != "https":
        raise ConfigValidationError("target_url must use https")

    if parsed.netloc.lower() != "chatgpt.com":
        raise ConfigValidationError("target_url must point to chatgpt.com")

    path = parsed.path or "/"
    if path not in ("", "/") and "/c/" not in path:
        raise ConfigValidationError(
            "target_url must be either https://chatgpt.com/ or a specific ChatGPT conversation path containing /c/"
        )

    return normalized


class ChatGPTUploaderConfig(ChatGptCopilotTargetConfig):
    """Compatibility name for the accepted uploader config model."""

    def __post_init__(self) -> None:
        try:
            super().__post_init__()
        except ValueError as exc:
            raise ConfigValidationError(str(exc)) from exc


def _compat_config_to_dict(self) -> dict[str, Any]:
    return self.to_payload()


def _compat_config_redacted_dict(self) -> dict[str, Any]:
    return self.to_redacted_payload()


ChatGptCopilotTargetConfig.to_dict = _compat_config_to_dict  # type: ignore[attr-defined]
ChatGptCopilotTargetConfig.to_redacted_dict = _compat_config_redacted_dict  # type: ignore[attr-defined]
ChatGPTUploaderConfig.to_dict = _compat_config_to_dict  # type: ignore[attr-defined]
ChatGPTUploaderConfig.to_redacted_dict = _compat_config_redacted_dict  # type: ignore[attr-defined]


def load_config(path: str | Path = DEFAULT_CONFIG_RELATIVE_PATH) -> ChatGPTUploaderConfig:
    config_path = Path(path)
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ConfigValidationError("target config must be a JSON object")
        return ChatGPTUploaderConfig.from_payload(payload)
    except ConfigValidationError:
        raise
    except Exception as exc:
        raise ConfigValidationError(str(exc)) from exc


def write_config(
    path_or_config: str | Path | ChatGptCopilotTargetConfig = DEFAULT_CONFIG_RELATIVE_PATH,
    config: ChatGptCopilotTargetConfig | None = None,
    **kwargs: Any,
) -> ChatGPTUploaderConfig:
    if isinstance(path_or_config, ChatGptCopilotTargetConfig):
        cfg = path_or_config
        output_path = Path(config) if config is not None else Path(kwargs.pop("path", DEFAULT_CONFIG_RELATIVE_PATH))
    else:
        output_path = Path(path_or_config)
        cfg = config

    if cfg is None:
        target_url = kwargs.pop("target_url", None)
        if target_url is None:
            raise ConfigValidationError("target_url is required when config is not provided")

        cfg = ChatGPTUploaderConfig(
            target_url=target_url,
            browser=str(kwargs.pop("browser", "msedge")),
            mode=str(kwargs.pop("mode", "operator_set")),
            allow_real_edge_default=bool(kwargs.pop("allow_real_edge_default", True)),
            allow_upload_default=bool(kwargs.pop("allow_upload_default", False)),
            allow_send_default=bool(kwargs.pop("allow_send_default", False)),
            source_patch=kwargs.pop("source_patch", None),
        )

    payload = cfg.to_payload()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return ChatGPTUploaderConfig.from_payload(payload)


def read_config(path: str | Path = DEFAULT_CONFIG_RELATIVE_PATH) -> ChatGPTUploaderConfig:
    return load_config(path)


# Keep newer U2.0 names working, but return the compatibility subclass where practical.
def read_target_config(path: str | Path = DEFAULT_CONFIG_RELATIVE_PATH) -> ChatGPTUploaderConfig:  # type: ignore[no-redef]
    return load_config(path)


def write_target_config(  # type: ignore[no-redef]
    path: str | Path,
    *,
    target_url: str,
    browser: str = "msedge",
    mode: str = "operator_set",
    allow_real_edge_default: bool = True,
    allow_upload_default: bool = False,
    allow_send_default: bool = False,
    source_patch: str | None = None,
) -> ChatGPTUploaderConfig:
    return write_config(
        path,
        target_url=target_url,
        browser=browser,
        mode=mode,
        allow_real_edge_default=allow_real_edge_default,
        allow_upload_default=allow_upload_default,
        allow_send_default=allow_send_default,
        source_patch=source_patch,
    )
# PATCHOPS_U2_01C_CONFIG_COMPAT_END

# PATCHOPS_U2_1QA_CONFIG_API_COMPAT_START
import json as _patchops_u2_1qa_json
import os as _patchops_u2_1qa_os
import re as _patchops_u2_1qa_re
from dataclasses import asdict as _patchops_u2_1qa_asdict
from dataclasses import dataclass as _patchops_u2_1qa_dataclass
from dataclasses import field as _patchops_u2_1qa_field
from dataclasses import is_dataclass as _patchops_u2_1qa_is_dataclass
from pathlib import Path as _PatchOpsU21QAPath
from urllib.parse import urlsplit as _patchops_u2_1qa_urlsplit
from urllib.parse import urlunsplit as _patchops_u2_1qa_urlunsplit


class ConfigValidationError(ValueError):
    pass


_CONFIG_ENV_VARS = (
    "PATCHOPS_CHATGPT_UPLOADER_CONFIG",
    "PATCHOPS_CHATGPT_COPILOT_TARGET_CONFIG",
    "CHATGPT_COPILOT_TARGET_CONFIG",
)


def _patchops_u2_1qa_repo_root():
    return _PatchOpsU21QAPath(__file__).resolve().parents[2]


def default_config_path(root=None):
    for env_name in _CONFIG_ENV_VARS:
        value = _patchops_u2_1qa_os.environ.get(env_name)
        if value:
            return _PatchOpsU21QAPath(value).expanduser().resolve()
    base = _PatchOpsU21QAPath(root).resolve() if root is not None else _patchops_u2_1qa_repo_root()
    return base / "data" / "config" / "chatgpt_copilot_target.json"


def normalize_target_url(url=None):
    raw = (url or "").strip()
    if not raw:
        raw = "https://chatgpt.com/"
    parsed = _patchops_u2_1qa_urlsplit(raw)
    if not parsed.scheme:
        raw = "https://" + raw
        parsed = _patchops_u2_1qa_urlsplit(raw)

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    if scheme != "https":
        raise ConfigValidationError("target_url must use https")
    if netloc not in {"chatgpt.com", "www.chatgpt.com"}:
        raise ConfigValidationError("target_url must point to chatgpt.com")

    path = parsed.path or "/"
    if not path.startswith("/"):
        path = "/" + path

    if path == "/":
        return "https://chatgpt.com/"

    return _patchops_u2_1qa_urlunsplit(("https", "chatgpt.com", path, parsed.query, parsed.fragment))


def validate_target_url(url=None):
    return normalize_target_url(url)


def is_valid_target_url(url=None):
    try:
        validate_target_url(url)
        return True
    except Exception:
        return False


def redact_target_url(url=None):
    normalized = normalize_target_url(url)
    parsed = _patchops_u2_1qa_urlsplit(normalized)
    parts = [part for part in parsed.path.split("/") if part]

    redacted_parts = []
    for index, part in enumerate(parts):
        if index > 0 and parts[index - 1] in {"c", "g"}:
            redacted_parts.append("<redacted>")
        elif _patchops_u2_1qa_re.search(r"[0-9a-fA-F]{8,}", part):
            redacted_parts.append("<redacted>")
        else:
            redacted_parts.append(part)

    redacted_path = "/" + "/".join(redacted_parts) if redacted_parts else "/"
    return _patchops_u2_1qa_urlunsplit((parsed.scheme, parsed.netloc, redacted_path, "", ""))


def redacted_target_url(url=None):
    return redact_target_url(url)


@_patchops_u2_1qa_dataclass
class UploaderConfig:
    target_url: str = "https://chatgpt.com/"
    allow_upload: bool = False
    allow_send: bool = False
    allow_browser_launch: bool = False
    allow_file_picker: bool = False
    allow_live_actions: bool = False
    dry_run: bool = True
    target_config_path: str = ""
    metadata: dict = _patchops_u2_1qa_field(default_factory=dict)

    def __post_init__(self):
        self.target_url = normalize_target_url(self.target_url)
        self.allow_upload = bool(self.allow_upload)
        self.allow_send = bool(self.allow_send)
        self.allow_browser_launch = bool(self.allow_browser_launch)
        self.allow_file_picker = bool(self.allow_file_picker)
        self.allow_live_actions = bool(self.allow_live_actions)
        self.dry_run = bool(self.dry_run)

    @property
    def normalized_target_url(self):
        return normalize_target_url(self.target_url)

    @property
    def redacted_target_url(self):
        return redact_target_url(self.target_url)

    @property
    def target_url_redacted(self):
        return redact_target_url(self.target_url)

    @property
    def upload_enabled(self):
        return bool(self.allow_upload)

    @property
    def send_enabled(self):
        return bool(self.allow_send)

    @property
    def browser_launch_enabled(self):
        return bool(self.allow_browser_launch)

    def to_payload(self):
        return {
            "target_url": self.normalized_target_url,
            "target_url_redacted": self.target_url_redacted,
            "redacted_target_url": self.redacted_target_url,
            "allow_upload": self.allow_upload,
            "allow_send": self.allow_send,
            "allow_browser_launch": self.allow_browser_launch,
            "allow_file_picker": self.allow_file_picker,
            "allow_live_actions": self.allow_live_actions,
            "dry_run": self.dry_run,
            "target_config_path": self.target_config_path,
            "metadata": dict(self.metadata or {}),
            "file_upload_attempted": False,
            "chatgpt_submit_performed": False,
            "conversation_text_logged": False,
            "selenium_used": False,
            "webdriver_used": False,
            "browser_dom_automation_used": False,
        }

    def to_dict(self):
        return self.to_payload()

    def as_dict(self):
        return self.to_payload()

    def get(self, key, default=None):
        return self.to_payload().get(key, default)

    def __getitem__(self, key):
        payload = self.to_payload()
        if key not in payload:
            raise KeyError(key)
        return payload[key]


ChatGPTUploaderConfig = UploaderConfig
ChatGPTCopilotTargetConfig = UploaderConfig
TargetConfig = UploaderConfig


def _config_from_mapping(data=None, *, path=None):
    payload = dict(data or {})
    target_url = (
        payload.get("target_url")
        or payload.get("url")
        or payload.get("chatgpt_url")
        or payload.get("target")
        or "https://chatgpt.com/"
    )
    return UploaderConfig(
        target_url=str(target_url),
        allow_upload=bool(payload.get("allow_upload", payload.get("file_upload_allowed", payload.get("upload_enabled", False)))),
        allow_send=bool(payload.get("allow_send", payload.get("send_allowed", payload.get("send_enabled", False)))),
        allow_browser_launch=bool(payload.get("allow_browser_launch", payload.get("launch_allowed", payload.get("browser_launch_enabled", False)))),
        allow_file_picker=bool(payload.get("allow_file_picker", payload.get("file_picker_allowed", False))),
        allow_live_actions=bool(payload.get("allow_live_actions", False)),
        dry_run=bool(payload.get("dry_run", True)),
        target_config_path=str(path or payload.get("target_config_path", "")),
        metadata=dict(payload.get("metadata") or {}),
    )


def create_default_config(target_url=None, **overrides):
    payload = {
        "target_url": target_url or overrides.pop("target_url", None) or "https://chatgpt.com/",
        "allow_upload": False,
        "allow_send": False,
        "allow_browser_launch": False,
        "allow_file_picker": False,
        "allow_live_actions": False,
        "dry_run": True,
    }
    payload.update(overrides)
    return _config_from_mapping(payload)


def default_config(target_url=None, **overrides):
    return create_default_config(target_url=target_url, **overrides)


def create_config(target_url=None, **overrides):
    return create_default_config(target_url=target_url, **overrides)


def _payload_from_config(config):
    if isinstance(config, UploaderConfig):
        return config.to_payload()
    if hasattr(config, "to_payload"):
        payload = config.to_payload()
        if isinstance(payload, dict):
            return dict(payload)
    if hasattr(config, "to_dict"):
        payload = config.to_dict()
        if isinstance(payload, dict):
            return dict(payload)
    if _patchops_u2_1qa_is_dataclass(config):
        return dict(_patchops_u2_1qa_asdict(config))
    if isinstance(config, dict):
        return dict(config)
    raise TypeError(f"Unsupported uploader config type: {type(config).__name__}")


def write_config(config, path=None):
    target = _PatchOpsU21QAPath(path).expanduser().resolve() if path is not None else default_config_path()
    cfg = _config_from_mapping(_payload_from_config(config), path=target)
    payload = cfg.to_payload()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_patchops_u2_1qa_json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return target


def save_config(config, path=None):
    return write_config(config, path)


def read_config(path=None):
    target = _PatchOpsU21QAPath(path).expanduser().resolve() if path is not None else default_config_path()
    if not target.exists():
        raise FileNotFoundError(str(target))
    data = _patchops_u2_1qa_json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ConfigValidationError("config file must contain a JSON object")
    return _config_from_mapping(data, path=target)


def load_config(path=None):
    return read_config(path)


def load_or_default_config(path=None, **overrides):
    try:
        return load_config(path)
    except FileNotFoundError:
        return create_default_config(**overrides)


def config_to_payload(config):
    return _config_from_mapping(_payload_from_config(config)).to_payload()


def validate_config(config):
    return _config_from_mapping(_payload_from_config(config))


def set_target_url(path, target_url):
    target = _PatchOpsU21QAPath(path).expanduser().resolve() if path is not None else default_config_path()
    cfg = create_default_config(target_url=target_url)
    write_config(cfg, target)
    return cfg


def write_default_config(path=None, target_url=None):
    return write_config(create_default_config(target_url=target_url), path)
# PATCHOPS_U2_1QA_CONFIG_API_COMPAT_END

# PATCHOPS_U2_1QB_CONFIG_LEGACY_API_COMPAT_START
import hashlib as _patchops_u2_1qb_hashlib
import json as _patchops_u2_1qb_json
import os as _patchops_u2_1qb_os
import re as _patchops_u2_1qb_re
from pathlib import Path as _PatchOpsU21QBPath
from urllib.parse import urlsplit as _patchops_u2_1qb_urlsplit
from urllib.parse import urlunsplit as _patchops_u2_1qb_urlunsplit


def _patchops_u2_1qb_repo_root():
    return _PatchOpsU21QBPath(__file__).resolve().parents[2]


def _patchops_u2_1qb_sha256_text(value):
    return _patchops_u2_1qb_hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()


def normalize_target_url(url=None):
    raw = (url or "").strip()
    if not raw:
        raw = "https://chatgpt.com/"
    parsed = _patchops_u2_1qb_urlsplit(raw)
    if not parsed.scheme:
        raw = "https://" + raw
        parsed = _patchops_u2_1qb_urlsplit(raw)

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    if scheme != "https":
        raise ConfigValidationError("target_url must use https")
    if netloc not in {"chatgpt.com", "www.chatgpt.com"}:
        raise ConfigValidationError("target_url must point to chatgpt.com")

    path = parsed.path or "/"
    if not path.startswith("/"):
        path = "/" + path

    if path == "/":
        return "https://chatgpt.com/"

    return _patchops_u2_1qb_urlunsplit(("https", "chatgpt.com", path, parsed.query, parsed.fragment))


def validate_target_url(url=None):
    return normalize_target_url(url)


def is_valid_target_url(url=None):
    try:
        validate_target_url(url)
        return True
    except Exception:
        return False


def redact_target_url(url=None):
    normalized = normalize_target_url(url)
    parsed = _patchops_u2_1qb_urlsplit(normalized)
    parts = [part for part in parsed.path.split("/") if part]

    redacted_parts = []
    for index, part in enumerate(parts):
        previous = parts[index - 1] if index > 0 else ""
        if previous == "c":
            redacted_parts.append("<conversation>")
        elif previous == "g":
            redacted_parts.append("<gpt>")
        elif _patchops_u2_1qb_re.search(r"[0-9a-fA-F]{8,}", part):
            redacted_parts.append("<redacted>")
        else:
            redacted_parts.append(part)

    redacted_path = "/" + "/".join(redacted_parts) if redacted_parts else "/"
    return _patchops_u2_1qb_urlunsplit((parsed.scheme, parsed.netloc, redacted_path, "", ""))


def redacted_target_url(url=None):
    return redact_target_url(url)


def default_config_path(root=None):
    for env_name in (
        "PATCHOPS_CHATGPT_UPLOADER_CONFIG",
        "PATCHOPS_CHATGPT_COPILOT_TARGET_CONFIG",
        "CHATGPT_COPILOT_TARGET_CONFIG",
    ):
        value = _patchops_u2_1qb_os.environ.get(env_name)
        if value:
            return _PatchOpsU21QBPath(value).expanduser().resolve()

    base = _PatchOpsU21QBPath(root).expanduser().resolve() if root is not None else _patchops_u2_1qb_repo_root()
    return base / "data" / "config" / "chatgpt_copilot_target.json"


def _patchops_u2_1qb_bool(value, default=False):
    if value is None:
        return bool(default)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on", "allow", "allowed"}
    return bool(value)


def _patchops_u2_1qb_payload_from_any(config):
    if isinstance(config, dict):
        return dict(config)
    if hasattr(config, "to_payload"):
        payload = config.to_payload()
        if isinstance(payload, dict):
            return dict(payload)
    if hasattr(config, "to_dict"):
        payload = config.to_dict()
        if isinstance(payload, dict):
            return dict(payload)
    if hasattr(config, "__dict__"):
        return dict(config.__dict__)
    raise TypeError(f"Unsupported config object: {type(config).__name__}")


def _patchops_u2_1qb_config_from_mapping(data=None, *, path=None):
    payload = dict(data or {})
    target_url = payload.get("target_url") or payload.get("url") or payload.get("chatgpt_url") or payload.get("target") or "https://chatgpt.com/"

    cfg = UploaderConfig(
        target_url=str(target_url),
        allow_upload=_patchops_u2_1qb_bool(payload.get("allow_upload", payload.get("file_upload_allowed", payload.get("upload_enabled", False)))),
        allow_send=_patchops_u2_1qb_bool(payload.get("allow_send", payload.get("send_allowed", payload.get("send_enabled", False)))),
        allow_browser_launch=_patchops_u2_1qb_bool(payload.get("allow_browser_launch", payload.get("launch_allowed", payload.get("browser_launch_enabled", False)))),
        allow_file_picker=_patchops_u2_1qb_bool(payload.get("allow_file_picker", payload.get("file_picker_allowed", False))),
        allow_live_actions=_patchops_u2_1qb_bool(payload.get("allow_live_actions", False)),
        dry_run=_patchops_u2_1qb_bool(payload.get("dry_run", True), True),
        target_config_path=str(path or payload.get("target_config_path", payload.get("config_path", ""))),
        metadata=dict(payload.get("metadata") or {}),
    )

    cfg.mode = str(payload.get("mode", getattr(cfg, "mode", "operator_set")) or "operator_set")
    cfg.browser = str(payload.get("browser", getattr(cfg, "browser", "msedge")) or "msedge")
    cfg.allow_upload_default = cfg.allow_upload
    cfg.allow_send_default = cfg.allow_send
    cfg.real_edge_default = _patchops_u2_1qb_bool(payload.get("real_edge_default", payload.get("allow_browser_launch", False)))
    cfg.target_url_sha256 = _patchops_u2_1qb_sha256_text(cfg.target_url)
    return cfg


def _patchops_u2_1qb_config_to_payload(self):
    target_url = normalize_target_url(getattr(self, "target_url", "https://chatgpt.com/"))
    mode = str(getattr(self, "mode", "operator_set") or "operator_set")
    browser = str(getattr(self, "browser", "msedge") or "msedge")
    payload = {
        "target_url": target_url,
        "target_url_redacted": redact_target_url(target_url),
        "redacted_target_url": redact_target_url(target_url),
        "target_url_sha256": _patchops_u2_1qb_sha256_text(target_url),
        "mode": mode,
        "browser": browser,
        "allow_upload": bool(getattr(self, "allow_upload", False)),
        "allow_send": bool(getattr(self, "allow_send", False)),
        "allow_browser_launch": bool(getattr(self, "allow_browser_launch", False)),
        "allow_file_picker": bool(getattr(self, "allow_file_picker", False)),
        "allow_live_actions": bool(getattr(self, "allow_live_actions", False)),
        "allow_upload_default": bool(getattr(self, "allow_upload_default", getattr(self, "allow_upload", False))),
        "allow_send_default": bool(getattr(self, "allow_send_default", getattr(self, "allow_send", False))),
        "real_edge_default": bool(getattr(self, "real_edge_default", getattr(self, "allow_browser_launch", False))),
        "dry_run": bool(getattr(self, "dry_run", True)),
        "target_config_path": str(getattr(self, "target_config_path", "") or ""),
        "metadata": dict(getattr(self, "metadata", {}) or {}),
        "file_upload_attempted": False,
        "chatgpt_submit_performed": False,
        "conversation_text_logged": False,
        "selenium_used": False,
        "webdriver_used": False,
        "browser_dom_automation_used": False,
    }
    return payload


def _patchops_u2_1qb_class_create(cls, target_url=None, **overrides):
    payload = dict(overrides)
    if target_url is not None:
        payload["target_url"] = target_url
    return _patchops_u2_1qb_config_from_mapping(payload)


def _patchops_u2_1qb_class_read(cls, path=None):
    return read_config(path)


def _patchops_u2_1qb_instance_write(self, path=None):
    return write_config(self, path)


def _patchops_u2_1qb_get(self, key, default=None):
    return self.to_payload().get(key, default)


def _patchops_u2_1qb_getitem(self, key):
    payload = self.to_payload()
    if key not in payload:
        raise KeyError(key)
    return payload[key]


UploaderConfig.create = classmethod(_patchops_u2_1qb_class_create)
UploaderConfig.read = classmethod(_patchops_u2_1qb_class_read)
UploaderConfig.load = classmethod(_patchops_u2_1qb_class_read)
UploaderConfig.write = _patchops_u2_1qb_instance_write
UploaderConfig.save = _patchops_u2_1qb_instance_write
UploaderConfig.to_payload = _patchops_u2_1qb_config_to_payload
UploaderConfig.to_dict = _patchops_u2_1qb_config_to_payload
UploaderConfig.as_dict = _patchops_u2_1qb_config_to_payload
UploaderConfig.get = _patchops_u2_1qb_get
UploaderConfig.__getitem__ = _patchops_u2_1qb_getitem


def create_default_config(target_url=None, **overrides):
    payload = dict(overrides)
    if target_url is not None:
        payload["target_url"] = target_url
    return _patchops_u2_1qb_config_from_mapping(payload)


def default_config(target_url=None, **overrides):
    return create_default_config(target_url=target_url, **overrides)


def create_config(target_url=None, **overrides):
    return create_default_config(target_url=target_url, **overrides)


def validate_config(config):
    return _patchops_u2_1qb_config_from_mapping(_patchops_u2_1qb_payload_from_any(config))


def config_to_payload(config):
    return validate_config(config).to_payload()


def write_config(config_or_path, path_or_config=None):
    if isinstance(config_or_path, (str, _PatchOpsU21QBPath)) and path_or_config is not None:
        target = _PatchOpsU21QBPath(config_or_path).expanduser().resolve()
        config = path_or_config
    else:
        config = config_or_path
        target = _PatchOpsU21QBPath(path_or_config).expanduser().resolve() if path_or_config is not None else default_config_path()

    cfg = _patchops_u2_1qb_config_from_mapping(_patchops_u2_1qb_payload_from_any(config), path=target)
    payload = cfg.to_payload()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_patchops_u2_1qb_json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return target


def save_config(config_or_path, path_or_config=None):
    return write_config(config_or_path, path_or_config)


def read_config(path=None):
    target = _PatchOpsU21QBPath(path).expanduser().resolve() if path is not None else default_config_path()
    if not target.exists():
        raise FileNotFoundError(str(target))
    data = _patchops_u2_1qb_json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ConfigValidationError("config file must contain a JSON object")
    return _patchops_u2_1qb_config_from_mapping(data, path=target)


def load_config(path=None):
    return read_config(path)


def load_or_default_config(path=None, **overrides):
    try:
        return load_config(path)
    except FileNotFoundError:
        return create_default_config(**overrides)


def write_target_config(config_or_path, path_or_config=None):
    return write_config(config_or_path, path_or_config)


def read_target_config(path=None):
    return read_config(path)


def load_target_config(path=None):
    return read_config(path)


def set_target_url(path, target_url, **overrides):
    cfg = create_default_config(target_url=target_url, **overrides)
    write_config(cfg, path)
    return cfg


def write_default_config(path=None, target_url=None, **overrides):
    return write_config(create_default_config(target_url=target_url, **overrides), path)


ChatGPTUploaderConfig = UploaderConfig
ChatGPTCopilotTargetConfig = UploaderConfig
TargetConfig = UploaderConfig
# PATCHOPS_U2_1QB_CONFIG_LEGACY_API_COMPAT_END

# PATCHOPS_U2_1QC_CONFIG_LEGACY_FINAL_COMPAT_START
def _patchops_u2_1qc_config_payload_for_eq(config):
    if hasattr(config, "to_payload"):
        payload = dict(config.to_payload())
    elif hasattr(config, "__dict__"):
        payload = dict(config.__dict__)
    else:
        return config
    payload.pop("target_config_path", None)
    payload.pop("metadata", None)
    return payload


def _patchops_u2_1qc_config_eq(self, other):
    try:
        return _patchops_u2_1qc_config_payload_for_eq(self) == _patchops_u2_1qc_config_payload_for_eq(other)
    except Exception:
        return False


def _patchops_u2_1qc_config_ne(self, other):
    return not _patchops_u2_1qc_config_eq(self, other)


def _patchops_u2_1qc_apply_legacy_attrs(cfg):
    if not hasattr(cfg, "browser") or not getattr(cfg, "browser", None):
        cfg.browser = "msedge"
    if not hasattr(cfg, "mode") or not getattr(cfg, "mode", None):
        cfg.mode = "operator_set"

    real_edge = getattr(cfg, "allow_real_edge_default", None)
    if real_edge is None:
        real_edge = getattr(cfg, "real_edge_default", None)
    if real_edge is None:
        real_edge = True

    cfg.allow_real_edge_default = bool(real_edge)
    cfg.real_edge_default = bool(real_edge)
    cfg.allow_upload_default = bool(getattr(cfg, "allow_upload_default", getattr(cfg, "allow_upload", False)))
    cfg.allow_send_default = bool(getattr(cfg, "allow_send_default", getattr(cfg, "allow_send", False)))
    return cfg


_PATCHOPS_U2_1QC_PREVIOUS_CREATE_DEFAULT_CONFIG = create_default_config
_PATCHOPS_U2_1QC_PREVIOUS_CREATE_CONFIG = create_config
_PATCHOPS_U2_1QC_PREVIOUS_DEFAULT_CONFIG = default_config
_PATCHOPS_U2_1QC_PREVIOUS_READ_CONFIG = read_config
_PATCHOPS_U2_1QC_PREVIOUS_LOAD_CONFIG = load_config
_PATCHOPS_U2_1QC_PREVIOUS_WRITE_CONFIG = write_config
_PATCHOPS_U2_1QC_PREVIOUS_SAVE_CONFIG = save_config


def create_default_config(target_url=None, **overrides):
    if "allow_real_edge_default" in overrides and "real_edge_default" not in overrides:
        overrides["real_edge_default"] = overrides["allow_real_edge_default"]
    if "real_edge_default" in overrides and "allow_browser_launch" not in overrides:
        overrides["allow_browser_launch"] = overrides["real_edge_default"]
    cfg = _PATCHOPS_U2_1QC_PREVIOUS_CREATE_DEFAULT_CONFIG(target_url=target_url, **overrides)
    return _patchops_u2_1qc_apply_legacy_attrs(cfg)


def create_config(target_url=None, **overrides):
    return create_default_config(target_url=target_url, **overrides)


def default_config(target_url=None, **overrides):
    return create_default_config(target_url=target_url, **overrides)


def read_config(path=None):
    cfg = _PATCHOPS_U2_1QC_PREVIOUS_READ_CONFIG(path)
    return _patchops_u2_1qc_apply_legacy_attrs(cfg)


def load_config(path=None):
    return read_config(path)


def write_config(config_or_path, path_or_config=None):
    result = _PATCHOPS_U2_1QC_PREVIOUS_WRITE_CONFIG(config_or_path, path_or_config)
    return result


def save_config(config_or_path, path_or_config=None):
    return write_config(config_or_path, path_or_config)


def _patchops_u2_1qc_class_create(cls, target_url=None, **overrides):
    return create_default_config(target_url=target_url, **overrides)


def _patchops_u2_1qc_class_read(cls, path=None):
    return read_config(path)


def _patchops_u2_1qc_instance_write(self, path=None):
    return write_config(self, path)


def _patchops_u2_1qc_payload(self):
    payload = dict(_patchops_u2_1qb_config_to_payload(self)) if "_patchops_u2_1qb_config_to_payload" in globals() else {}
    if not payload:
        payload = {
            "target_url": normalize_target_url(getattr(self, "target_url", "https://chatgpt.com/")),
            "target_url_redacted": redact_target_url(getattr(self, "target_url", "https://chatgpt.com/")),
            "redacted_target_url": redact_target_url(getattr(self, "target_url", "https://chatgpt.com/")),
            "allow_upload": bool(getattr(self, "allow_upload", False)),
            "allow_send": bool(getattr(self, "allow_send", False)),
            "allow_browser_launch": bool(getattr(self, "allow_browser_launch", False)),
            "allow_file_picker": bool(getattr(self, "allow_file_picker", False)),
            "allow_live_actions": bool(getattr(self, "allow_live_actions", False)),
            "dry_run": bool(getattr(self, "dry_run", True)),
            "target_config_path": str(getattr(self, "target_config_path", "") or ""),
            "metadata": dict(getattr(self, "metadata", {}) or {}),
            "file_upload_attempted": False,
            "chatgpt_submit_performed": False,
            "conversation_text_logged": False,
            "selenium_used": False,
            "webdriver_used": False,
            "browser_dom_automation_used": False,
        }

    payload["browser"] = str(getattr(self, "browser", payload.get("browser", "msedge")) or "msedge")
    payload["mode"] = str(getattr(self, "mode", payload.get("mode", "operator_set")) or "operator_set")
    payload["allow_real_edge_default"] = bool(getattr(self, "allow_real_edge_default", payload.get("real_edge_default", True)))
    payload["real_edge_default"] = bool(getattr(self, "real_edge_default", payload["allow_real_edge_default"]))
    payload["allow_upload_default"] = bool(getattr(self, "allow_upload_default", payload.get("allow_upload", False)))
    payload["allow_send_default"] = bool(getattr(self, "allow_send_default", payload.get("allow_send", False)))
    return payload


UploaderConfig.create = classmethod(_patchops_u2_1qc_class_create)
UploaderConfig.read = classmethod(_patchops_u2_1qc_class_read)
UploaderConfig.load = classmethod(_patchops_u2_1qc_class_read)
UploaderConfig.write = _patchops_u2_1qc_instance_write
UploaderConfig.save = _patchops_u2_1qc_instance_write
UploaderConfig.__eq__ = _patchops_u2_1qc_config_eq
UploaderConfig.__ne__ = _patchops_u2_1qc_config_ne
UploaderConfig.to_payload = _patchops_u2_1qc_payload
UploaderConfig.to_dict = _patchops_u2_1qc_payload
UploaderConfig.as_dict = _patchops_u2_1qc_payload

ChatGPTUploaderConfig = UploaderConfig
ChatGPTCopilotTargetConfig = UploaderConfig
TargetConfig = UploaderConfig
# PATCHOPS_U2_1QC_CONFIG_LEGACY_FINAL_COMPAT_END

# PATCHOPS_U2_1QD_REAL_EDGE_DEFAULT_COMPAT_START
_PATCHOPS_U2_1QD_PREVIOUS_QB_MAPPING = globals().get("_patchops_u2_1qb_config_from_mapping")
_PATCHOPS_U2_1QD_PREVIOUS_CREATE_DEFAULT_CONFIG = create_default_config
_PATCHOPS_U2_1QD_PREVIOUS_READ_CONFIG = read_config
_PATCHOPS_U2_1QD_PREVIOUS_WRITE_CONFIG = write_config


def _patchops_u2_1qd_bool(value, default=False):
    if value is None:
        return bool(default)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on", "allow", "allowed"}
    return bool(value)


def _patchops_u2_1qd_explicit_real_edge_default(payload):
    payload = dict(payload or {})
    if "allow_real_edge_default" in payload:
        return _patchops_u2_1qd_bool(payload.get("allow_real_edge_default"), True)
    if "real_edge_default" in payload:
        return _patchops_u2_1qd_bool(payload.get("real_edge_default"), True)
    return None


def _patchops_u2_1qd_apply_legacy_real_edge_default(cfg, explicit=None):
    real_edge = True if explicit is None else bool(explicit)

    cfg.allow_real_edge_default = real_edge
    cfg.real_edge_default = real_edge

    if not hasattr(cfg, "browser") or not getattr(cfg, "browser", None):
        cfg.browser = "msedge"
    if not hasattr(cfg, "mode") or not getattr(cfg, "mode", None):
        cfg.mode = "operator_set"

    cfg.allow_upload_default = bool(getattr(cfg, "allow_upload_default", getattr(cfg, "allow_upload", False)))
    cfg.allow_send_default = bool(getattr(cfg, "allow_send_default", getattr(cfg, "allow_send", False)))
    return cfg


def _patchops_u2_1qb_config_from_mapping(data=None, *, path=None):
    payload = dict(data or {})
    explicit = _patchops_u2_1qd_explicit_real_edge_default(payload)

    if _PATCHOPS_U2_1QD_PREVIOUS_QB_MAPPING is not None:
        cfg = _PATCHOPS_U2_1QD_PREVIOUS_QB_MAPPING(payload, path=path)
    else:
        cfg = _PATCHOPS_U2_1QD_PREVIOUS_CREATE_DEFAULT_CONFIG(
            target_url=payload.get("target_url") or payload.get("url") or payload.get("chatgpt_url") or payload.get("target") or "https://chatgpt.com/"
        )

    return _patchops_u2_1qd_apply_legacy_real_edge_default(cfg, explicit=explicit)


def create_default_config(target_url=None, **overrides):
    payload = dict(overrides)
    if target_url is not None:
        payload["target_url"] = target_url
    return _patchops_u2_1qb_config_from_mapping(payload)


def create_config(target_url=None, **overrides):
    return create_default_config(target_url=target_url, **overrides)


def default_config(target_url=None, **overrides):
    return create_default_config(target_url=target_url, **overrides)


def read_config(path=None):
    cfg = _PATCHOPS_U2_1QD_PREVIOUS_READ_CONFIG(path)
    payload = cfg.to_payload() if hasattr(cfg, "to_payload") else getattr(cfg, "__dict__", {})
    explicit = _patchops_u2_1qd_explicit_real_edge_default(payload)
    return _patchops_u2_1qd_apply_legacy_real_edge_default(cfg, explicit=explicit)


def load_config(path=None):
    return read_config(path)


def write_config(config_or_path, path_or_config=None):
    return _PATCHOPS_U2_1QD_PREVIOUS_WRITE_CONFIG(config_or_path, path_or_config)


def save_config(config_or_path, path_or_config=None):
    return write_config(config_or_path, path_or_config)


def _patchops_u2_1qd_config_payload_for_eq(config):
    if hasattr(config, "to_payload"):
        payload = dict(config.to_payload())
    elif hasattr(config, "__dict__"):
        payload = dict(config.__dict__)
    else:
        return config

    payload.pop("target_config_path", None)
    payload.pop("metadata", None)
    return payload


def _patchops_u2_1qd_config_eq(self, other):
    try:
        return _patchops_u2_1qd_config_payload_for_eq(self) == _patchops_u2_1qd_config_payload_for_eq(other)
    except Exception:
        return False


def _patchops_u2_1qd_config_ne(self, other):
    return not _patchops_u2_1qd_config_eq(self, other)


def _patchops_u2_1qd_payload(self):
    if "_patchops_u2_1qc_payload" in globals():
        payload = dict(_patchops_u2_1qc_payload(self))
    elif "_patchops_u2_1qb_config_to_payload" in globals():
        payload = dict(_patchops_u2_1qb_config_to_payload(self))
    elif hasattr(self, "__dict__"):
        payload = dict(self.__dict__)
    else:
        payload = {}

    target_url = normalize_target_url(payload.get("target_url") or getattr(self, "target_url", "https://chatgpt.com/"))
    real_edge = bool(getattr(self, "allow_real_edge_default", getattr(self, "real_edge_default", True)))

    payload.update({
        "target_url": target_url,
        "target_url_redacted": redact_target_url(target_url),
        "redacted_target_url": redact_target_url(target_url),
        "browser": str(getattr(self, "browser", payload.get("browser", "msedge")) or "msedge"),
        "mode": str(getattr(self, "mode", payload.get("mode", "operator_set")) or "operator_set"),
        "allow_real_edge_default": real_edge,
        "real_edge_default": real_edge,
        "allow_upload": bool(getattr(self, "allow_upload", payload.get("allow_upload", False))),
        "allow_send": bool(getattr(self, "allow_send", payload.get("allow_send", False))),
        "allow_upload_default": bool(getattr(self, "allow_upload_default", payload.get("allow_upload", False))),
        "allow_send_default": bool(getattr(self, "allow_send_default", payload.get("allow_send", False))),
        "file_upload_attempted": False,
        "chatgpt_submit_performed": False,
        "conversation_text_logged": False,
        "selenium_used": False,
        "webdriver_used": False,
        "browser_dom_automation_used": False,
    })
    return payload


def _patchops_u2_1qd_class_create(cls, target_url=None, **overrides):
    return create_default_config(target_url=target_url, **overrides)


def _patchops_u2_1qd_class_read(cls, path=None):
    return read_config(path)


def _patchops_u2_1qd_instance_write(self, path=None):
    return write_config(self, path)


UploaderConfig.create = classmethod(_patchops_u2_1qd_class_create)
UploaderConfig.read = classmethod(_patchops_u2_1qd_class_read)
UploaderConfig.load = classmethod(_patchops_u2_1qd_class_read)
UploaderConfig.write = _patchops_u2_1qd_instance_write
UploaderConfig.save = _patchops_u2_1qd_instance_write
UploaderConfig.__eq__ = _patchops_u2_1qd_config_eq
UploaderConfig.__ne__ = _patchops_u2_1qd_config_ne
UploaderConfig.to_payload = _patchops_u2_1qd_payload
UploaderConfig.to_dict = _patchops_u2_1qd_payload
UploaderConfig.as_dict = _patchops_u2_1qd_payload

ChatGPTUploaderConfig = UploaderConfig
ChatGPTCopilotTargetConfig = UploaderConfig
TargetConfig = UploaderConfig
# PATCHOPS_U2_1QD_REAL_EDGE_DEFAULT_COMPAT_END

# PATCHOPS_U2_1QF_RESOLVE_CONFIG_PATH_ALIAS_START
import os as _patchops_u2_1qf_os
from pathlib import Path as _PatchOpsU21QFPath


def _patchops_u2_1qf_repo_root():
    return _PatchOpsU21QFPath(__file__).resolve().parents[2]


def _patchops_u2_1qf_pathish(value):
    if value is None:
        return ""
    return str(value).strip().strip('"')


def _patchops_u2_1qf_looks_like_config_path(value):
    raw = _patchops_u2_1qf_pathish(value)
    if not raw:
        return False
    lowered = raw.replace("\\", "/").lower()
    return lowered.endswith(".json") or "target" in lowered or "config" in lowered


def resolve_config_path(*args, **kwargs):
    """Resolve the ChatGPT uploader target config path.

    Compatibility surface:
    - resolve_config_path()
    - resolve_config_path(repo_root)
    - resolve_config_path(repo_root, target_config)
    - resolve_config_path(repo_root=..., target_config=...)
    - resolve_config_path(repo_root=..., config_path=...)
    - resolve_config_path(path=...)
    """
    explicit = (
        kwargs.get("target_config")
        or kwargs.get("config_path")
        or kwargs.get("target_config_path")
        or kwargs.get("path")
    )
    repo_root = kwargs.get("repo_root") or kwargs.get("root") or kwargs.get("project_root")

    if len(args) >= 2:
        if repo_root is None:
            repo_root = args[0]
        if explicit is None:
            explicit = args[1]
    elif len(args) == 1:
        only = args[0]
        if explicit is None and _patchops_u2_1qf_looks_like_config_path(only):
            explicit = only
        elif repo_root is None:
            repo_root = only

    if explicit:
        return _PatchOpsU21QFPath(explicit).expanduser().resolve()

    for env_name in (
        "PATCHOPS_CHATGPT_UPLOADER_CONFIG",
        "PATCHOPS_CHATGPT_COPILOT_TARGET_CONFIG",
        "CHATGPT_COPILOT_TARGET_CONFIG",
    ):
        value = _patchops_u2_1qf_os.environ.get(env_name)
        if value:
            return _PatchOpsU21QFPath(value).expanduser().resolve()

    if "default_config_path" in globals():
        try:
            return _PatchOpsU21QFPath(default_config_path(repo_root)).expanduser().resolve()
        except TypeError:
            return _PatchOpsU21QFPath(default_config_path()).expanduser().resolve()

    base = _PatchOpsU21QFPath(repo_root).expanduser().resolve() if repo_root else _patchops_u2_1qf_repo_root()
    return base / "data" / "config" / "chatgpt_copilot_target.json"


def resolve_target_config_path(*args, **kwargs):
    return resolve_config_path(*args, **kwargs)


def target_config_path(*args, **kwargs):
    return resolve_config_path(*args, **kwargs)


def ensure_config_parent(path=None, *args, **kwargs):
    resolved = resolve_config_path(*args, path=path, **kwargs)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def load_or_default_config(path=None, **overrides):
    resolved = resolve_config_path(path) if path is not None else resolve_config_path()
    try:
        return load_config(resolved)
    except FileNotFoundError:
        return create_default_config(**overrides)
# PATCHOPS_U2_1QF_RESOLVE_CONFIG_PATH_ALIAS_END

# PATCHOPS_U2_1QG_PAYLOAD_INCLUDE_TARGET_URL_COMPAT_START
import hashlib as _patchops_u2_1qg_hashlib


_PATCHOPS_U2_1QG_PREVIOUS_PAYLOAD = UploaderConfig.to_payload


def _patchops_u2_1qg_sha256_text(value):
    return _patchops_u2_1qg_hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()


def _patchops_u2_1qg_payload(self, include_target_url=True, include_sensitive=True, **kwargs):
    try:
        payload = dict(_PATCHOPS_U2_1QG_PREVIOUS_PAYLOAD(self))
    except TypeError:
        payload = dict(_PATCHOPS_U2_1QG_PREVIOUS_PAYLOAD(self))

    target_url = normalize_target_url(payload.get("target_url") or getattr(self, "target_url", "https://chatgpt.com/"))
    redacted = redact_target_url(target_url)

    payload["target_url"] = target_url
    payload["target_url_redacted"] = redacted
    payload["redacted_target_url"] = redacted
    payload["target_url_sha256"] = payload.get("target_url_sha256") or _patchops_u2_1qg_sha256_text(target_url)

    payload.setdefault("browser", str(getattr(self, "browser", "msedge") or "msedge"))
    payload.setdefault("mode", str(getattr(self, "mode", "operator_set") or "operator_set"))
    payload.setdefault("allow_upload", bool(getattr(self, "allow_upload", False)))
    payload.setdefault("allow_send", bool(getattr(self, "allow_send", False)))
    payload.setdefault("allow_upload_default", bool(getattr(self, "allow_upload_default", payload.get("allow_upload", False))))
    payload.setdefault("allow_send_default", bool(getattr(self, "allow_send_default", payload.get("allow_send", False))))
    payload.setdefault("allow_real_edge_default", bool(getattr(self, "allow_real_edge_default", getattr(self, "real_edge_default", True))))
    payload.setdefault("real_edge_default", bool(getattr(self, "real_edge_default", payload.get("allow_real_edge_default", True))))

    payload["file_upload_attempted"] = False
    payload["chatgpt_submit_performed"] = False
    payload["conversation_text_logged"] = False
    payload["selenium_used"] = False
    payload["webdriver_used"] = False
    payload["browser_dom_automation_used"] = False

    if include_target_url is False or include_sensitive is False:
        payload.pop("target_url", None)

    return payload


UploaderConfig.to_payload = _patchops_u2_1qg_payload
UploaderConfig.to_dict = _patchops_u2_1qg_payload
UploaderConfig.as_dict = _patchops_u2_1qg_payload
ChatGPTUploaderConfig = UploaderConfig
ChatGPTCopilotTargetConfig = UploaderConfig
TargetConfig = UploaderConfig
# PATCHOPS_U2_1QG_PAYLOAD_INCLUDE_TARGET_URL_COMPAT_END

# PATCHOPS_U2_1QK_TARGET_CONFIG_COMPAT_START
import hashlib as _patchops_u2_1qk_hashlib
import json as _patchops_u2_1qk_json
import os as _patchops_u2_1qk_os
import re as _patchops_u2_1qk_re
from pathlib import Path as _PatchOpsU21QKPath
from urllib.parse import urlsplit as _patchops_u2_1qk_urlsplit
from urllib.parse import urlunsplit as _patchops_u2_1qk_urlunsplit


_PATCHOPS_U2_1QK_PREVIOUS_CREATE_DEFAULT_CONFIG = create_default_config
_PATCHOPS_U2_1QK_PREVIOUS_CREATE_CONFIG = create_config
_PATCHOPS_U2_1QK_PREVIOUS_DEFAULT_CONFIG = default_config
_PATCHOPS_U2_1QK_PREVIOUS_WRITE_CONFIG = write_config
_PATCHOPS_U2_1QK_PREVIOUS_SAVE_CONFIG = save_config
_PATCHOPS_U2_1QK_PREVIOUS_READ_CONFIG = read_config
_PATCHOPS_U2_1QK_PREVIOUS_LOAD_CONFIG = load_config


def _patchops_u2_1qk_sha256_text(value):
    return _patchops_u2_1qk_hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()


def normalize_target_url(url=None):
    raw = "" if url is None else str(url).strip()
    if not raw:
        raise ConfigValidationError("target_url must not be empty")

    parsed = _patchops_u2_1qk_urlsplit(raw)
    if not parsed.scheme:
        raw = "https://" + raw
        parsed = _patchops_u2_1qk_urlsplit(raw)

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    if scheme != "https":
        raise ConfigValidationError("target_url must use https")
    if netloc not in {"chatgpt.com", "www.chatgpt.com"}:
        raise ConfigValidationError("target_url must point to chatgpt.com")

    path = parsed.path or "/"
    if not path.startswith("/"):
        path = "/" + path

    if path == "/":
        return "https://chatgpt.com/"

    return _patchops_u2_1qk_urlunsplit(("https", "chatgpt.com", path, parsed.query, parsed.fragment))


def validate_target_url(url=None):
    return normalize_target_url(url)


def is_valid_target_url(url=None):
    try:
        validate_target_url(url)
        return True
    except Exception:
        return False


def _patchops_u2_1qk_redact_sensitive_segment(segment, marker):
    raw = str(segment or "")
    if not raw:
        return marker + "<redacted>"

    if len(raw) <= 8 and not _patchops_u2_1qk_re.search(r"[0-9a-fA-F]{8,}", raw):
        return raw

    prefix = raw[:8]
    return prefix + marker + "<redacted>"


def redact_target_url(url=None):
    normalized = normalize_target_url(url)
    parsed = _patchops_u2_1qk_urlsplit(normalized)

    parts = [part for part in parsed.path.split("/") if part]
    redacted_parts = []

    for index, part in enumerate(parts):
        previous = parts[index - 1] if index > 0 else ""

        if previous == "c":
            redacted_parts.append(_patchops_u2_1qk_redact_sensitive_segment(part, "<conversation>"))
        elif previous == "g":
            redacted_parts.append(_patchops_u2_1qk_redact_sensitive_segment(part, "<gpt>"))
        elif _patchops_u2_1qk_re.search(r"[0-9a-fA-F]{8,}", part):
            redacted_parts.append(_patchops_u2_1qk_redact_sensitive_segment(part, ""))
        else:
            redacted_parts.append(part)

    redacted_path = "/" + "/".join(redacted_parts) if redacted_parts else "/"
    return _patchops_u2_1qk_urlunsplit((parsed.scheme, parsed.netloc, redacted_path, "", ""))


def redacted_target_url(url=None):
    return redact_target_url(url)


def _patchops_u2_1qk_payload_from_any(config):
    if isinstance(config, dict):
        return dict(config)
    if hasattr(config, "to_payload"):
        payload = config.to_payload()
        if isinstance(payload, dict):
            return dict(payload)
    if hasattr(config, "to_dict"):
        payload = config.to_dict()
        if isinstance(payload, dict):
            return dict(payload)
    if hasattr(config, "__dict__"):
        return dict(config.__dict__)
    raise TypeError(f"Unsupported config object: {type(config).__name__}")


def _patchops_u2_1qk_apply_standard_payload_fields(payload):
    payload = dict(payload)
    target_url = normalize_target_url(payload.get("target_url") or payload.get("url") or payload.get("chatgpt_url") or payload.get("target"))

    payload["target_url"] = target_url
    payload["target_url_redacted"] = redact_target_url(target_url)
    payload["redacted_target_url"] = redact_target_url(target_url)
    payload["target_url_sha256"] = _patchops_u2_1qk_sha256_text(target_url)

    payload.setdefault("mode", "operator_set")
    payload.setdefault("browser", "msedge")
    payload.setdefault("allow_upload", False)
    payload.setdefault("allow_send", False)
    payload.setdefault("allow_upload_default", bool(payload.get("allow_upload", False)))
    payload.setdefault("allow_send_default", bool(payload.get("allow_send", False)))
    payload.setdefault("allow_real_edge_default", bool(payload.get("real_edge_default", True)))
    payload.setdefault("real_edge_default", bool(payload.get("allow_real_edge_default", True)))
    payload.setdefault("allow_browser_launch", bool(payload.get("real_edge_default", True)))
    payload.setdefault("allow_file_picker", False)
    payload.setdefault("allow_live_actions", False)
    payload.setdefault("dry_run", True)
    payload.setdefault("metadata", {})

    payload["file_upload_attempted"] = False
    payload["chatgpt_submit_performed"] = False
    payload["conversation_text_logged"] = False
    payload["selenium_used"] = False
    payload["webdriver_used"] = False
    payload["browser_dom_automation_used"] = False

    return payload


def create_default_config(target_url=None, **overrides):
    if target_url is not None and not str(target_url).strip():
        raise ConfigValidationError("target_url must not be empty")
    if "target_url" in overrides and not str(overrides.get("target_url") or "").strip():
        raise ConfigValidationError("target_url must not be empty")

    cfg = _PATCHOPS_U2_1QK_PREVIOUS_CREATE_DEFAULT_CONFIG(target_url=target_url, **overrides)

    if not hasattr(cfg, "browser") or not getattr(cfg, "browser", None):
        cfg.browser = str(overrides.get("browser", "msedge") or "msedge")
    if not hasattr(cfg, "mode") or not getattr(cfg, "mode", None):
        cfg.mode = str(overrides.get("mode", "operator_set") or "operator_set")

    real_edge = overrides.get("allow_real_edge_default", overrides.get("real_edge_default", getattr(cfg, "allow_real_edge_default", getattr(cfg, "real_edge_default", True))))
    cfg.allow_real_edge_default = bool(real_edge)
    cfg.real_edge_default = bool(real_edge)
    cfg.allow_upload_default = bool(overrides.get("allow_upload_default", getattr(cfg, "allow_upload", False)))
    cfg.allow_send_default = bool(overrides.get("allow_send_default", getattr(cfg, "allow_send", False)))

    if "source_patch" in overrides:
        cfg.source_patch = str(overrides.get("source_patch") or "")
        metadata = dict(getattr(cfg, "metadata", {}) or {})
        metadata["source_patch"] = cfg.source_patch
        cfg.metadata = metadata

    return cfg


def create_config(target_url=None, **overrides):
    return create_default_config(target_url=target_url, **overrides)


def default_config(target_url=None, **overrides):
    return create_default_config(target_url=target_url, **overrides)


def _patchops_u2_1qk_class_create(cls, target_url=None, **overrides):
    return create_default_config(target_url=target_url, **overrides)


def _patchops_u2_1qk_class_read(cls, path=None):
    return read_config(path)


def _patchops_u2_1qk_instance_write(self, path=None):
    return write_config(self, path)


UploaderConfig.create = classmethod(_patchops_u2_1qk_class_create)
UploaderConfig.read = classmethod(_patchops_u2_1qk_class_read)
UploaderConfig.load = classmethod(_patchops_u2_1qk_class_read)
UploaderConfig.write = _patchops_u2_1qk_instance_write
UploaderConfig.save = _patchops_u2_1qk_instance_write


_PATCHOPS_U2_1QK_PREVIOUS_PAYLOAD = UploaderConfig.to_payload


def _patchops_u2_1qk_payload(self, include_target_url=True, include_sensitive=True, **kwargs):
    try:
        payload = dict(_PATCHOPS_U2_1QK_PREVIOUS_PAYLOAD(self))
    except TypeError:
        payload = dict(_PATCHOPS_U2_1QK_PREVIOUS_PAYLOAD(self))

    payload = _patchops_u2_1qk_apply_standard_payload_fields(payload)

    if hasattr(self, "source_patch"):
        payload["source_patch"] = str(getattr(self, "source_patch") or "")
        metadata = dict(payload.get("metadata") or {})
        metadata["source_patch"] = payload["source_patch"]
        payload["metadata"] = metadata

    if include_target_url is False or include_sensitive is False:
        payload.pop("target_url", None)

    return payload


UploaderConfig.to_payload = _patchops_u2_1qk_payload
UploaderConfig.to_dict = _patchops_u2_1qk_payload
UploaderConfig.as_dict = _patchops_u2_1qk_payload


def read_config(path=None):
    cfg = _PATCHOPS_U2_1QK_PREVIOUS_READ_CONFIG(path)
    payload = cfg.to_payload() if hasattr(cfg, "to_payload") else getattr(cfg, "__dict__", {})
    if payload.get("target_url"):
        validate_target_url(payload.get("target_url"))
    if not hasattr(cfg, "allow_real_edge_default"):
        cfg.allow_real_edge_default = bool(payload.get("allow_real_edge_default", payload.get("real_edge_default", True)))
    if not hasattr(cfg, "real_edge_default"):
        cfg.real_edge_default = bool(getattr(cfg, "allow_real_edge_default", True))
    return cfg


def load_config(path=None):
    return read_config(path)


def write_config(config_or_path, path_or_config=None):
    if isinstance(config_or_path, (str, _PatchOpsU21QKPath)) and path_or_config is not None:
        path = _PatchOpsU21QKPath(config_or_path).expanduser().resolve()
        config = path_or_config
    else:
        config = config_or_path
        path = _PatchOpsU21QKPath(path_or_config).expanduser().resolve() if path_or_config is not None else default_config_path()

    payload = _patchops_u2_1qk_apply_standard_payload_fields(_patchops_u2_1qk_payload_from_any(config))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_patchops_u2_1qk_json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def save_config(config_or_path, path_or_config=None):
    return write_config(config_or_path, path_or_config)


def write_target_config(path, *, target_url, source_patch="", **overrides):
    target = _PatchOpsU21QKPath(path).expanduser().resolve()
    if not str(target_url or "").strip():
        raise ConfigValidationError("target_url must not be empty")

    cfg = create_default_config(target_url=target_url, source_patch=source_patch, **overrides)
    payload = cfg.to_payload()
    payload["target_config_path"] = str(target)
    payload["source_patch"] = str(source_patch or "")
    metadata = dict(payload.get("metadata") or {})
    if source_patch:
        metadata["source_patch"] = str(source_patch)
    payload["metadata"] = metadata

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_patchops_u2_1qk_json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return target


def read_target_config(path=None):
    return read_config(path)


def load_target_config(path=None):
    return read_config(path)


ChatGPTUploaderConfig = UploaderConfig
ChatGPTCopilotTargetConfig = UploaderConfig
TargetConfig = UploaderConfig
# PATCHOPS_U2_1QK_TARGET_CONFIG_COMPAT_END

# PATCHOPS_U2_1QL_TARGET_CONFIG_PATH_EQ_COMPAT_START
from pathlib import Path as _PatchOpsU21QLPath


_PATCHOPS_U2_1QL_PREVIOUS_EQ = getattr(UploaderConfig, "__eq__", None)


def _patchops_u2_1ql_is_path_like(value):
    return isinstance(value, (str, _PatchOpsU21QLPath))


def _patchops_u2_1ql_resolved_path_text(value):
    if value is None:
        return ""
    try:
        return str(_PatchOpsU21QLPath(value).expanduser().resolve())
    except Exception:
        return str(value)


def _patchops_u2_1ql_config_path(config):
    if hasattr(config, "target_config_path"):
        value = getattr(config, "target_config_path", "")
        if value:
            return _patchops_u2_1ql_resolved_path_text(value)

    if hasattr(config, "to_payload"):
        try:
            payload = config.to_payload()
            value = payload.get("target_config_path") if isinstance(payload, dict) else ""
            if value:
                return _patchops_u2_1ql_resolved_path_text(value)
        except Exception:
            pass

    return ""


def _patchops_u2_1ql_payload_for_config_eq(config):
    if hasattr(config, "to_payload"):
        try:
            payload = dict(config.to_payload())
        except TypeError:
            payload = dict(config.to_payload(include_target_url=True))
    elif hasattr(config, "__dict__"):
        payload = dict(config.__dict__)
    else:
        return config

    payload.pop("target_config_path", None)
    payload.pop("metadata", None)
    return payload


def _patchops_u2_1ql_config_eq(self, other):
    if _patchops_u2_1ql_is_path_like(other):
        self_path = _patchops_u2_1ql_config_path(self)
        other_path = _patchops_u2_1ql_resolved_path_text(other)
        return bool(self_path) and self_path == other_path

    try:
        return _patchops_u2_1ql_payload_for_config_eq(self) == _patchops_u2_1ql_payload_for_config_eq(other)
    except Exception:
        if _PATCHOPS_U2_1QL_PREVIOUS_EQ is not None:
            try:
                return bool(_PATCHOPS_U2_1QL_PREVIOUS_EQ(self, other))
            except Exception:
                return False
        return False


def _patchops_u2_1ql_config_ne(self, other):
    return not _patchops_u2_1ql_config_eq(self, other)


UploaderConfig.__eq__ = _patchops_u2_1ql_config_eq
UploaderConfig.__ne__ = _patchops_u2_1ql_config_ne
ChatGPTUploaderConfig = UploaderConfig
ChatGPTCopilotTargetConfig = UploaderConfig
TargetConfig = UploaderConfig
# PATCHOPS_U2_1QL_TARGET_CONFIG_PATH_EQ_COMPAT_END
