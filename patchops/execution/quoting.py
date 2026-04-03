from __future__ import annotations

import shlex


def render_display_command(program: str, args: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in [program, *args])
