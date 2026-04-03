from __future__ import annotations


def render_summary(exit_code: int, result_label: str) -> str:
    return "\n".join(
        [
            "SUMMARY",
            "-------",
            f"ExitCode : {exit_code}",
            f"Result   : {result_label}",
        ]
    )
