from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable


PROJECT_PACKET_DIR = Path("docs") / "projects"


def slugify_project_name(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "_", value.strip().lower()).strip("_")
    return text or "project"


def resolve_wrapper_root(wrapper_project_root: str | Path | None = None) -> Path:
    if wrapper_project_root is None:
        return Path.cwd().resolve()
    return Path(wrapper_project_root).resolve()


def default_project_packet_path(
    project_name: str,
    *,
    wrapper_project_root: str | Path | None = None,
) -> Path:
    wrapper_root = resolve_wrapper_root(wrapper_project_root)
    return wrapper_root / PROJECT_PACKET_DIR / f"{slugify_project_name(project_name)}.md"


def _normalize_lines(values: Iterable[str] | None, *, empty_line: str) -> list[str]:
    if values is None:
        return [empty_line]

    normalized: list[str] = []
    for value in values:
        for raw_line in str(value).splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("- "):
                line = line[2:].strip()
            normalized.append(line)

    if not normalized:
        return [empty_line]

    return normalized


def build_project_packet(
    *,
    project_name: str,
    target_root: str,
    profile_name: str,
    runtime_path: str | None = None,
    wrapper_project_root: str | Path | None = None,
    initial_goals: Iterable[str] | None = None,
    current_phase: str = "Initial onboarding",
    current_objective: str = "Create the first narrow target-specific manifest.",
    latest_passed_patch: str | None = None,
    latest_attempted_patch: str | None = None,
    current_blockers: Iterable[str] | None = None,
    latest_known_report_path: str | None = None,
    current_recommendation: str = "Read the generic PatchOps packet, pick the closest example, and stay narrow.",
    next_action: str = "Run check, inspect, and plan before the first apply or verify execution.",
    outstanding_risks: Iterable[str] | None = None,
) -> str:
    clean_project_name = str(project_name).strip()
    if not clean_project_name:
        raise ValueError("project_name must not be empty")

    clean_profile_name = str(profile_name).strip()
    if not clean_profile_name:
        raise ValueError("profile_name must not be empty")

    clean_target_root = str(target_root).strip()
    if not clean_target_root:
        raise ValueError("target_root must not be empty")

    wrapper_root = resolve_wrapper_root(wrapper_project_root)
    packet_relative_path = PROJECT_PACKET_DIR / f"{slugify_project_name(clean_project_name)}.md"

    goal_lines = _normalize_lines(initial_goals, empty_line="No explicit goals were supplied yet.")
    blocker_lines = _normalize_lines(current_blockers, empty_line="No blockers are recorded right now.")
    risk_lines = _normalize_lines(outstanding_risks, empty_line="No outstanding risks are recorded right now.")

    packet_lines = [
        f"# Project packet â€” {clean_project_name}",
        "",
        "## 1. Target identity",
        f"- **Project name:** {clean_project_name}",
        f"- **Packet path:** `{packet_relative_path.as_posix()}`",
        f"- **Target project root:** `{clean_target_root}`",
        f"- **Wrapper project root:** `{wrapper_root}`",
        "",
        "## 2. Target roots and runtime",
        f"- **Target root:** `{clean_target_root}`",
        f"- **Wrapper root:** `{wrapper_root}`",
        f"- **Expected runtime:** `{runtime_path or '(use profile default unless a target-specific override is required)'}`",
        "",
        "## 3. Selected PatchOps profile",
        f"- **Profile:** `{clean_profile_name}`",
        "- **Profile rule:** start with the smallest correct profile and widen only when the target really needs it.",
        "",
        "## 4. What PatchOps owns",
        "- manifest authoring and execution mechanics,",
        "- deterministic reporting and validation evidence,",
        "- profile-driven wrapper behavior,",
        "- project-packet maintenance and onboarding support.",
        "",
        "## 5. What must remain outside PatchOps",
        "- target-repo business logic,",
        "- target-specific production rules,",
        "- target-side operational policy,",
        "- architectural decisions that belong inside the target repo itself.",
        "",
        "## 6. Recommended examples and starting surfaces",
        "- Read the generic PatchOps packet first.",
        "- Start from the closest example under `examples/`.",
        "- Use the packet as the target-facing contract, not as a replacement for manifests or reports.",
        "- Before execution, run `check`, `inspect`, and `plan`.",
        "",
        "## 7. Phase guidance",
        "- Build the target patch by patch with narrow manifests.",
        "- Keep PowerShell thin and keep reusable logic in Python.",
        "- Refresh this packet after meaningful report-producing runs.",
        "",
        "### Initial goals",
    ]

    packet_lines.extend(f"- {item}" for item in goal_lines)
    packet_lines.extend(
        [
            "",
            "## 8. Current development state",
            "",
            "### Mutable status",
            f"- **Current phase:** {current_phase}",
            f"- **Current objective:** {current_objective}",
            f"- **Latest passed patch:** {latest_passed_patch or '(none yet)'}",
            f"- **Latest attempted patch:** {latest_attempted_patch or '(none yet)'}",
            f"- **Latest known report path:** {latest_known_report_path or '(none yet)'}",
            f"- **Current recommendation:** {current_recommendation}",
            f"- **Next action:** {next_action}",
            "",
            "### Current blockers",
        ]
    )
    packet_lines.extend(f"- {item}" for item in blocker_lines)
    packet_lines.extend(
        [
            "",
            "### Outstanding risks",
        ]
    )
    packet_lines.extend(f"- {item}" for item in risk_lines)
    packet_lines.append("")

    return "\n".join(packet_lines)


def scaffold_project_packet(
    *,
    project_name: str,
    target_root: str,
    profile_name: str,
    runtime_path: str | None = None,
    wrapper_project_root: str | Path | None = None,
    output_path: str | Path | None = None,
    initial_goals: Iterable[str] | None = None,
) -> dict[str, object]:
    wrapper_root = resolve_wrapper_root(wrapper_project_root)
    packet_path = Path(output_path) if output_path is not None else default_project_packet_path(
        project_name,
        wrapper_project_root=wrapper_root,
    )
    if not packet_path.is_absolute():
        packet_path = (wrapper_root / packet_path).resolve()

    content = build_project_packet(
        project_name=project_name,
        target_root=target_root,
        profile_name=profile_name,
        runtime_path=runtime_path,
        wrapper_project_root=wrapper_root,
        initial_goals=initial_goals,
    )
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text(content + ("\n" if not content.endswith("\n") else ""), encoding="utf-8")

    return {
        "written": True,
        "project_name": project_name,
        "project_slug": slugify_project_name(project_name),
        "packet_path": str(packet_path),
        "target_root": target_root,
        "wrapper_root": str(wrapper_root),
        "profile_name": profile_name,
        "runtime_path": runtime_path,
        "initial_goal_count": len(_normalize_lines(initial_goals, empty_line="")),
    }


_MUTABLE_STATUS_HEADING = "### Mutable status"
_CURRENT_BLOCKERS_HEADING = "### Current blockers"
_OUTSTANDING_RISKS_HEADING = "### Outstanding risks"


def _normalize_status_line(value: str | None, *, empty_line: str) -> str:
    if value is None:
        return empty_line
    text = str(value).strip()
    return text or empty_line


def _load_optional_json(path: str | Path | None) -> dict:
    if path is None:
        return {}
    candidate = Path(path)
    if not candidate.exists():
        return {}
    try:
        payload = json.loads(candidate.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _build_mutable_status_lines(
    *,
    current_phase: str | None = None,
    current_objective: str | None = None,
    latest_passed_patch: str | None = None,
    latest_attempted_patch: str | None = None,
    latest_known_report_path: str | None = None,
    current_recommendation: str | None = None,
    next_action: str | None = None,
) -> list[str]:
    return [
        _MUTABLE_STATUS_HEADING,
        f"- **Current phase:** {_normalize_status_line(current_phase, empty_line='(none yet)')}",
        f"- **Current objective:** {_normalize_status_line(current_objective, empty_line='(none yet)')}",
        f"- **Latest passed patch:** {_normalize_status_line(latest_passed_patch, empty_line='(none yet)')}",
        f"- **Latest attempted patch:** {_normalize_status_line(latest_attempted_patch, empty_line='(none yet)')}",
        f"- **Latest known report path:** {_normalize_status_line(latest_known_report_path, empty_line='(none yet)')}",
        f"- **Current recommendation:** {_normalize_status_line(current_recommendation, empty_line='(none yet)')}",
        f"- **Next action:** {_normalize_status_line(next_action, empty_line='(none yet)')}",
        "",
    ]


def _replace_section(content: str, heading: str, next_heading: str, replacement_lines: list[str]) -> str:
    start = content.find(heading)
    if start == -1:
        raise ValueError(f"Missing heading in project packet: {heading}")
    end = content.find(next_heading, start)
    if end == -1:
        raise ValueError(f"Missing heading in project packet: {next_heading}")
    replacement = "\n".join(replacement_lines)
    if not replacement.endswith("\n"):
        replacement += "\n"
    return content[:start] + replacement + content[end:]


def refresh_project_packet_content(
    content: str,
    *,
    current_phase: str | None = None,
    current_objective: str | None = None,
    latest_passed_patch: str | None = None,
    latest_attempted_patch: str | None = None,
    latest_known_report_path: str | None = None,
    current_recommendation: str | None = None,
    next_action: str | None = None,
    current_blockers=None,
    outstanding_risks=None,
) -> str:
    blocker_lines = _normalize_lines(current_blockers, empty_line="(none)")
    risk_lines = _normalize_lines(outstanding_risks, empty_line="(none)")

    updated = _replace_section(
        content,
        _MUTABLE_STATUS_HEADING,
        _CURRENT_BLOCKERS_HEADING,
        _build_mutable_status_lines(
            current_phase=current_phase,
            current_objective=current_objective,
            latest_passed_patch=latest_passed_patch,
            latest_attempted_patch=latest_attempted_patch,
            latest_known_report_path=latest_known_report_path,
            current_recommendation=current_recommendation,
            next_action=next_action,
        ),
    )
    updated = _replace_section(
        updated,
        _CURRENT_BLOCKERS_HEADING,
        _OUTSTANDING_RISKS_HEADING,
        [_CURRENT_BLOCKERS_HEADING, *[f"- {item}" for item in blocker_lines], ""],
    )

    risk_marker = _OUTSTANDING_RISKS_HEADING
    risk_start = updated.find(risk_marker)
    if risk_start == -1:
        raise ValueError(f"Missing heading in project packet: {risk_marker}")
    risk_replacement = "\n".join([risk_marker, *[f"- {item}" for item in risk_lines], ""]) + "\n"
    updated = updated[:risk_start] + risk_replacement

    return updated if updated.endswith("\n") else updated + "\n"


def refresh_project_packet(
    *,
    project_name: str,
    wrapper_project_root: str | Path | None = None,
    packet_path: str | Path | None = None,
    handoff_json_path: str | Path | None = None,
    latest_report_path: str | None = None,
    current_phase: str | None = None,
    current_objective: str | None = None,
    latest_passed_patch: str | None = None,
    latest_attempted_patch: str | None = None,
    current_recommendation: str | None = None,
    next_action: str | None = None,
    current_blockers=None,
    outstanding_risks=None,
) -> dict[str, object]:
    wrapper_root = resolve_wrapper_root(wrapper_project_root)
    resolved_packet_path = Path(packet_path) if packet_path is not None else default_project_packet_path(
        project_name,
        wrapper_project_root=wrapper_root,
    )
    if not resolved_packet_path.is_absolute():
        resolved_packet_path = (wrapper_root / resolved_packet_path).resolve()
    if not resolved_packet_path.exists():
        raise FileNotFoundError(f"Project packet does not exist: {resolved_packet_path}")

    handoff_payload = _load_optional_json(handoff_json_path)

    refreshed_content = refresh_project_packet_content(
        resolved_packet_path.read_text(encoding="utf-8"),
        current_phase=current_phase,
        current_objective=current_objective,
        latest_passed_patch=latest_passed_patch or handoff_payload.get("latest_passed_patch"),
        latest_attempted_patch=latest_attempted_patch or handoff_payload.get("latest_attempted_patch"),
        latest_known_report_path=latest_report_path,
        current_recommendation=current_recommendation,
        next_action=next_action or handoff_payload.get("next_action"),
        current_blockers=current_blockers,
        outstanding_risks=outstanding_risks,
    )
    resolved_packet_path.write_text(refreshed_content, encoding="utf-8")

    return {
        "written": True,
        "project_name": project_name,
        "packet_path": str(resolved_packet_path.resolve()),
        "wrapper_root": str(wrapper_root),
        "latest_passed_patch": latest_passed_patch or handoff_payload.get("latest_passed_patch"),
        "latest_attempted_patch": latest_attempted_patch or handoff_payload.get("latest_attempted_patch"),
        "latest_report_path": latest_report_path,
        "handoff_json_path": str(Path(handoff_json_path).resolve()) if handoff_json_path else None,
    }
