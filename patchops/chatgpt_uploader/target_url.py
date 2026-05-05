from __future__ import annotations

from urllib.parse import urlparse

from .models import TargetUrlInfo


def parse_target_url(url: str) -> TargetUrlInfo:
    """Parse and classify a ChatGPT target URL without opening a browser."""

    raw = (url or "").strip()
    parsed = urlparse(raw)

    is_chatgpt = parsed.netloc.lower() == "chatgpt.com"
    has_gpt_project_path = "/g/" in parsed.path
    has_conversation_path = "/c/" in parsed.path

    if not raw:
        safe = False
        reason = "empty_url"
    elif parsed.scheme not in {"http", "https"}:
        safe = False
        reason = "unsupported_scheme"
    elif not is_chatgpt:
        safe = False
        reason = "not_chatgpt"
    elif not has_conversation_path:
        safe = False
        reason = "missing_conversation_path"
    else:
        safe = True
        reason = "chatgpt_conversation_url"

    return TargetUrlInfo(
        raw_url=raw,
        scheme=parsed.scheme,
        netloc=parsed.netloc,
        path=parsed.path,
        is_chatgpt=is_chatgpt,
        has_gpt_project_path=has_gpt_project_path,
        has_conversation_path=has_conversation_path,
        safe_to_use_as_config=safe,
        reason=reason,
    )
