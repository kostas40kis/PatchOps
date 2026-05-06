from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LaunchDecision:
    allow_launch: bool
    reason: str


def decide_launch_permission(
    *,
    target_mode: str,
    allow_launch_target_requested: bool,
    allow_open_configured_url_requested: bool,
) -> LaunchDecision:
    """Return whether the Edge preflight may open the configured target URL.

    U2.0B rule:
    - operator_set mode is focus-only and must never open a URL.
    - even launch_target mode needs two explicit flags: --allow-launch-target and
      --allow-open-configured-url.
    """
    mode = (target_mode or "").strip()
    if not allow_launch_target_requested:
        return LaunchDecision(False, "launch_not_requested")
    if mode == "operator_set":
        return LaunchDecision(False, "operator_set_mode_is_focus_only")
    if mode != "launch_target":
        return LaunchDecision(False, f"unsupported_target_mode:{mode or '<empty>'}")
    if not allow_open_configured_url_requested:
        return LaunchDecision(False, "opening_configured_url_requires_explicit_allow_open_configured_url")
    return LaunchDecision(True, "launch_target_explicitly_allowed")
