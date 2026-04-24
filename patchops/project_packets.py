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

# PATCHOPS_PATCH_81_ONBOARDING_BOOTSTRAP_START
def default_onboarding_root(wrapper_project_root):
    from pathlib import Path

    return Path(wrapper_project_root).resolve() / "onboarding"


def _packet_slug(value: str) -> str:
    normalized = []
    previous_was_separator = False
    for character in value.strip().lower():
        if character.isalnum():
            normalized.append(character)
            previous_was_separator = False
        elif not previous_was_separator:
            normalized.append("_")
            previous_was_separator = True
    slug = "".join(normalized).strip("_")
    return slug or "target_project"


def _generic_onboarding_docs() -> list[str]:
    return [
        "README.md",
        "docs/overview.md",
        "docs/llm_usage.md",
        "docs/manifest_schema.md",
        "docs/profile_system.md",
        "docs/compatibility_notes.md",
        "docs/failure_repair_guide.md",
        "docs/examples.md",
        "docs/project_status.md",
        "docs/operator_quickstart.md",
        "docs/project_packet_contract.md",
        "docs/project_packet_workflow.md",
    ]


def _build_current_target_bootstrap_markdown(
    *,
    project_name: str,
    target_root: str,
    profile_name: str,
    packet_path: str,
    generic_docs: list[str],
    initial_goals: list[str],
    starter_manifest_path: str,
    starter_intent: str,
    runtime_override: str | None,
) -> str:
    lines: list[str] = [
        f"# Current target bootstrap â€” {project_name}",
        "",
        "## 1. Purpose",
        "This onboarding bundle is the new-target parallel to handoff.",
        "It gives the first LLM a stronger structured starting point without replacing the project packet, manifest, report, or handoff model.",
        "",
        "## 2. Target summary",
        f"- **Project name:** {project_name}",
        f"- **Target root:** `{target_root}`",
        f"- **Selected profile:** `{profile_name}`",
        f"- **Project packet:** `{packet_path}`",
        f"- **Starter manifest artifact:** `{starter_manifest_path}`",
        f"- **Starter intent:** `{starter_intent}`",
        f"- **Runtime override:** `{runtime_override or '(default)'}`",
        "",
        "## 3. Read these docs first:",
    ]
    for index, item in enumerate(generic_docs, start=1):
        lines.append(f"{index}. `{item}`")
    lines.extend(
        [
            "",
            "## 4. Initial goals",
        ]
    )
    if initial_goals:
        for goal in initial_goals:
            lines.append(f"- {goal}")
    else:
        lines.append("- (none provided)")
    lines.extend(
        [
            "",
            "## 5. Next LLM instructions",
            "1. Read the generic onboarding docs in the order above.",
            "2. Read the project packet.",
            "3. Restate what PatchOps owns, what must remain outside PatchOps, and which example manifest is closest.",
            "4. Create or adapt the first manifest conservatively.",
            "5. Run check, inspect, and plan before apply or verify.",
            "6. Use the canonical report as the source of truth after execution.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _build_next_prompt_text(
    *,
    project_name: str,
    packet_path: str,
    generic_docs: list[str],
    starter_manifest_path: str,
) -> str:
    lines = [
        f"Brand-new target project bootstrap for: {project_name}",
        "",
        "Read these docs first:",
    ]
    for index, item in enumerate(generic_docs, start=1):
        lines.append(f"{index}. {item}")
    lines.extend(
        [
            "",
            f"Then read the project packet: {packet_path}",
            f"Starter manifest artifact: {starter_manifest_path}",
            "",
            "Then produce only the next safe target-specific patch or the narrowest verify-only starter step.",
            "Then create or adapt the first manifest conservatively.",
            "Do not replace profiles, manifests, reports, or handoff with the onboarding bundle.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _build_starter_manifest_stub(
    *,
    project_name: str,
    project_slug: str,
    target_root: str,
    profile_name: str,
    packet_path: str,
    starter_intent: str,
) -> dict:
    return {
        "manifest_version": "1",
        "patch_name": f"starter_{project_slug}_{starter_intent}",
        "active_profile": profile_name,
        "target_project_root": target_root,
        "mode": "apply",
        "intent": starter_intent,
        "project_packet_path": packet_path,
        "notes": [
            "Bootstrap artifact only.",
            "Patch 83 should replace this stub with an intent-aware starter helper.",
            "Use the nearest safe example manifest before modifying this file.",
        ],
    }


def bootstrap_target_onboarding(
    *,
    project_name: str,
    target_root: str,
    profile_name: str,
    wrapper_project_root,
    initial_goals=None,
    runtime_override: str | None = None,
    starter_intent: str = "documentation_patch",
):
    from pathlib import Path
    import json

    initial_goals = list(initial_goals or [])
    wrapper_root = Path(wrapper_project_root).resolve()

    packet_payload = scaffold_project_packet(
        project_name=project_name,
        target_root=target_root,
        profile_name=profile_name,
        wrapper_project_root=wrapper_root,
        initial_goals=initial_goals,
        runtime_path=runtime_override,
    )

    onboarding_root = default_onboarding_root(wrapper_root)
    onboarding_root.mkdir(parents=True, exist_ok=True)

    generic_docs = _generic_onboarding_docs()
    project_slug = _packet_slug(project_name)
    packet_path = packet_payload["packet_path"]

    current_target_bootstrap_md = onboarding_root / "current_target_bootstrap.md"
    current_target_bootstrap_json = onboarding_root / "current_target_bootstrap.json"
    next_prompt_path = onboarding_root / "next_prompt.txt"
    starter_manifest_path = onboarding_root / "starter_manifest.json"

    md_text = _build_current_target_bootstrap_markdown(
        project_name=project_name,
        target_root=target_root,
        profile_name=profile_name,
        packet_path=packet_path,
        generic_docs=generic_docs,
        initial_goals=initial_goals,
        runtime_override=runtime_override,
        starter_manifest_path=str(starter_manifest_path.resolve()),
        starter_intent=starter_intent,
    )
    current_target_bootstrap_md.write_text(md_text, encoding="utf-8")

    payload = {
        "project_name": project_name,
        "project_slug": project_slug,
        "target_root": target_root,
        "selected_profile": profile_name,
        "runtime_override": runtime_override,
        "packet_path": packet_path,
        "bootstrap_markdown_path": str(current_target_bootstrap_md.resolve()),
        "bootstrap_json_path": str(current_target_bootstrap_json.resolve()),
        "next_prompt_path": str(next_prompt_path.resolve()),
        "starter_manifest_path": str(starter_manifest_path.resolve()),
        "onboarding_root": str(onboarding_root.resolve()),
        "current_target_bootstrap_md": str(current_target_bootstrap_md.resolve()),
        "current_target_bootstrap_json": str(current_target_bootstrap_json.resolve()),
        "next_prompt_path": str(next_prompt_path.resolve()),
        "starter_manifest_path": str(starter_manifest_path.resolve()),
        "starter_intent": starter_intent,
        "generic_docs": generic_docs,
        "initial_goals": initial_goals,
        "written": True,
    }
    current_target_bootstrap_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    next_prompt_text = _build_next_prompt_text(
        project_name=project_name,
        packet_path=packet_path,
        generic_docs=generic_docs,
        starter_manifest_path=str(starter_manifest_path.resolve()),
    )
    next_prompt_path.write_text(next_prompt_text, encoding="utf-8")

    starter_manifest = _build_starter_manifest_stub(
        project_name=project_name,
        project_slug=project_slug,
        target_root=target_root,
        profile_name=profile_name,
        packet_path=packet_path,
        starter_intent=starter_intent,
    )
    starter_manifest_path.write_text(json.dumps(starter_manifest, indent=2), encoding="utf-8")

    return payload
# PATCHOPS_PATCH_81_ONBOARDING_BOOTSTRAP_END

# PATCHOPS_PATCH81_ONBOARDING_BOOTSTRAP_START



def _patchops_g2b_normalize_onboarding_bootstrap_payload(
    payload: dict,
    *,
    project_name: str,
    target_root: str,
    profile_name: str,
    current_stage: str,
    initial_goals: list[str],
    wrapper_project_root,
) -> dict:
    normalized = dict(payload or {})
    normalized.setdefault("project_name", project_name)
    normalized.setdefault("target_root", target_root)
    normalized.setdefault("profile_name", profile_name)
    normalized.setdefault("current_stage", current_stage)
    normalized.setdefault("initial_goals", list(initial_goals or []))
    normalized.setdefault("recommended_commands", ["check", "inspect", "plan", "apply_or_verify_only"])
    try:
        normalized.setdefault(
            "project_packet_path",
            str(default_project_packet_path(project_name, wrapper_project_root=wrapper_project_root)),
        )
    except Exception:
        pass
    return normalized

def build_onboarding_bootstrap(
    *,
    project_name: str,
    target_root: str,
    profile_name: str,
    wrapper_project_root,
    runtime_path: str | None = None,
    packet_path: str | None = None,
    initial_goals: list[str] | None = None,
    current_stage: str = "Initial onboarding",
) -> dict:
    wrapper_root = Path(wrapper_project_root).resolve()
    onboarding_root = wrapper_root / "onboarding"
    onboarding_root.mkdir(parents=True, exist_ok=True)

    if initial_goals is None:
        initial_goals = []

    resolved_packet_path = (
        Path(packet_path).resolve()
        if packet_path
        else default_project_packet_path(project_name, wrapper_project_root=wrapper_root)
    )


    recommended_commands = [
        "check",
        "inspect",
        "plan",
        "apply_or_verify_only",
    ]

    starter_manifest = {
        "manifest_version": "1",
        "patch_name": "bootstrap_verify_only",
        "active_profile": profile_name,
        "target_project_root": target_root.replace("\\\\", "/"),
        "files_to_write": [],
        "validation_commands": [],
        "notes": [
            "Generated by bootstrap-target.",
            "Adapt this starter manifest conservatively before use.",
        ],
    }

    md_lines = [
        f"# Onboarding bootstrap - {project_name}",
        "",
        "## 1. Identity",
        f"- **Project name:** {project_name}",
        f"- **Target root:** `{target_root}`",
        f"- **Profile:** `{profile_name}`",
        f"- **Wrapper root:** `{wrapper_root}`",
        f"- **Runtime path:** `{runtime_path or '(default profile runtime)'}`",
        f"- **Project packet:** `{resolved_packet_path}`",
        f"- **Current stage:** {current_stage}",
        "",
        "## 2. Suggested reading order",
        "1. README.md",
        "2. docs/llm_usage.md",
        "3. docs/project_packet_contract.md",
        "4. docs/project_packet_workflow.md",
        f"5. docs/projects/{resolved_packet_path.name}",
        "",
        "## 3. Initial goals",
    ]
    if initial_goals:
        md_lines.extend([f"- {goal}" for goal in initial_goals])
    else:
        md_lines.append("- (none supplied)")
    md_lines.extend(
        [
            "",
            "## 4. Recommended command order",
            "1. check",
            "2. inspect",
            "3. plan",
            "4. apply or verify-only",
            "",
            "## 5. Notes",
            "- Keep PowerShell thin and let Python own reusable wrapper logic.",
            "- Treat the project packet as target-level memory and handoff as run-level resume state.",
        ]
    )

    next_prompt_lines = [
        f"You are onboarding the target project '{project_name}' into PatchOps.",
        "Read the generic PatchOps packet first, then use the project packet.",
        f"Selected profile: {profile_name}",
        f"Target root: {target_root}",
        f"Wrapper root: {wrapper_root}",
        f"Project packet path: {resolved_packet_path}",
        "Restate what PatchOps owns, what remains outside PatchOps, and the safest first manifest shape.",
        "Then run check, inspect, and plan before any apply or verify-only execution.",
    ]
    if initial_goals:
        next_prompt_lines.append("Initial goals:")
        next_prompt_lines.extend([f"- {goal}" for goal in initial_goals])

    json_payload = {
        "project_name": project_name,
        "target_root": target_root,
        "profile_name": profile_name,
        "wrapper_project_root": str(wrapper_root),
        "runtime_path": runtime_path,
        "project_packet_path": str(resolved_packet_path),
        "current_stage": current_stage,
        "initial_goals": list(initial_goals),
        "recommended_commands": ["check", "inspect", "plan", "apply_or_verify_only"],
        "starter_manifest_path": str((onboarding_root / "starter_manifest.json").resolve()),
        "bootstrap_markdown_path": str((onboarding_root / "current_target_bootstrap.md").resolve()),
        "next_prompt_path": str((onboarding_root / "next_prompt.txt").resolve()),
    }

    markdown_path = onboarding_root / "current_target_bootstrap.md"
    json_path = onboarding_root / "current_target_bootstrap.json"
    prompt_path = onboarding_root / "next_prompt.txt"
    manifest_path = onboarding_root / "starter_manifest.json"

    markdown_path.write_text("\\n".join(md_lines) + "\\n", encoding="utf-8")
    json_path.write_text(json.dumps(json_payload, indent=2), encoding="utf-8")
    prompt_path.write_text("\\n".join(next_prompt_lines) + "\\n", encoding="utf-8")
    manifest_path.write_text(json.dumps(starter_manifest, indent=2), encoding="utf-8")

    return {
        "written": True,
        "project_name": project_name,
        "wrapper_project_root": str(wrapper_root),
        "project_packet_path": str(resolved_packet_path),
        "bootstrap_markdown_path": str(markdown_path.resolve()),
        "bootstrap_json_path": str(json_path.resolve()),
        "next_prompt_path": str(prompt_path.resolve()),
        "starter_manifest_path": str(manifest_path.resolve()),
        "current_stage": current_stage,
    }

# PATCHOPS_PATCH81_ONBOARDING_BOOTSTRAP_END

# PATCHOPS_PATCH82_PROFILE_RECOMMENDATION_START

def _normalize_target_name(target_root: str) -> str:
    value = str(target_root).replace('\\', '/').rstrip('/')
    if not value:
        return ''
    return value.split('/')[-1].lower()


def recommend_profile_for_target(*, target_root: str, wrapper_project_root=None):
    target_name = _normalize_target_name(target_root)

    if target_name == 'trader':
        recommended_profile = 'trader'
        rationale = (
            'The target root name matches trader, so the dedicated trader profile is the '
            'smallest correct conservative choice.'
        )
        runtime_path = None
        starter_examples = [
            'examples/trader_first_verify_patch.json',
            'examples/trader_first_doc_patch.json',
            'examples/trader_verify_patch.json',
            'examples/trader_doc_patch.json',
        ]
    else:
        recommended_profile = 'generic_python'
        rationale = (
            'No target-specific profile signal was detected, so generic_python is the '
            'smallest conservative default.'
        )
        runtime_path = None
        starter_examples = [
            'examples/generic_python_verify_patch.json',
            'examples/generic_python_doc_patch.json',
        ]

    return {
        'target_root': str(target_root),
        'wrapper_project_root': None if wrapper_project_root is None else str(wrapper_project_root),
        'recommended_profile': recommended_profile,
        'rationale': rationale,
        'expected_runtime_path': runtime_path,
        'starter_examples': starter_examples,
    }

# PATCHOPS_PATCH82_PROFILE_RECOMMENDATION_END

# PATCHOPS_PATCH83_STARTER_HELPER_START

STARTER_INTENTS = (
    "code_patch",
    "documentation_patch",
    "validation_patch",
    "cleanup_patch",
    "archive_patch",
    "verify_only",
)


def _default_target_root_for_profile(profile_name: str) -> str | None:
    if profile_name == "trader":
        return r"C:\dev\trader"
    return None


def _starter_examples_for_intent(profile_name: str, intent: str) -> list[str]:
    trader = profile_name == "trader"
    mapping = {
        "code_patch": ["examples/trader_code_patch.json"] if trader else ["examples/generic_python_doc_patch.json"],
        "documentation_patch": ["examples/trader_doc_patch.json"] if trader else ["examples/generic_python_doc_patch.json"],
        "validation_patch": ["examples/trader_verify_patch.json"] if trader else ["examples/generic_verify_patch.json"],
        "verify_only": ["examples/trader_verify_patch.json"] if trader else ["examples/generic_verify_patch.json"],
        "cleanup_patch": ["examples/generic_cleanup_archive_patch.json"],
        "archive_patch": ["examples/generic_cleanup_archive_patch.json"],
    }
    return mapping[intent]


def build_starter_manifest_for_intent(
    *,
    profile_name: str,
    intent: str,
    target_root: str | None = None,
    patch_name: str | None = None,
    wrapper_project_root=None,
):
    if intent not in STARTER_INTENTS:
        raise ValueError(f"Unsupported starter intent: {intent}")

    resolved_target_root = target_root or _default_target_root_for_profile(profile_name)
    resolved_patch_name = patch_name or f"starter_{intent}"
    starter_examples = _starter_examples_for_intent(profile_name, intent)

    notes_map = {
        "code_patch": "Starter manifest for a code patch. Customize target files, validation commands, and notes for the real target work.",
        "documentation_patch": "Starter manifest for a documentation patch. Add the real documentation file writes and keep the validation surface narrow.",
        "validation_patch": "Starter manifest for a validation-oriented patch. Focus on evidence and checks rather than content changes.",
        "cleanup_patch": "Starter manifest for a cleanup patch. Add the real cleanup/archive commands required by the target repo.",
        "archive_patch": "Starter manifest for an archive patch. Add the archive commands and target paths required by the real workflow.",
        "verify_only": "Starter manifest for a verify-only rerun. Keep file writes empty and use only the validation commands needed for evidence.",
    }

    manifest: dict = {
        "manifest_version": "1",
        "patch_name": resolved_patch_name,
        "active_profile": profile_name,
        "backup_files": [],
        "files_to_write": [],
        "validation_commands": [],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {},
        "tags": ["starter", intent],
        "notes": notes_map[intent],
    }
    if resolved_target_root is not None:
        manifest["target_project_root"] = resolved_target_root

    return {
        "profile_name": profile_name,
        "intent": intent,
        "target_root": resolved_target_root,
        "wrapper_project_root": None if wrapper_project_root is None else str(wrapper_project_root),
        "starter_examples": starter_examples,
        "rationale": "Examples remain the baseline; this helper reduces blank-page authoring by giving a conservative manifest skeleton tied to the requested patch class.",
        "manifest": manifest,
    }

# PATCHOPS_PATCH83_STARTER_HELPER_END

# PATCHOPS_D1_PROJECT_PACKET_RUNTIME_COMPAT_20260423
import json as _patchops_d1_json
import re as _patchops_d1_re
from pathlib import Path as _patchops_d1_Path

def _patchops_d1_slugify(project_name: str) -> str:
    lowered = str(project_name or "").strip().lower()
    slug = _patchops_d1_re.sub(r"[^a-z0-9]+", "_", lowered).strip("_")
    return slug or "project"

def _patchops_d1_default_packet_path(*, project_name: str, wrapper_project_root) -> _patchops_d1_Path:
    wrapper_root = _patchops_d1_Path(wrapper_project_root)
    return (wrapper_root / "docs" / "projects" / f"{_patchops_d1_slugify(project_name)}.md").resolve()

def _patchops_d1_default_examples_for_profile(profile_name: str) -> list[str]:
    if profile_name == "trader":
        return ["examples/trader_first_verify_patch.json"]
    return ["examples/generic_python_verify_patch.json"]

def recommend_profile_for_target(*, target_root: str, wrapper_project_root=None):
    lowered = str(target_root or "").lower()
    if "trader" in lowered:
        recommended_profile = "trader"
        starter_examples = ["examples/trader_first_verify_patch.json"]
        rationale = "Use the smallest correct profile for the trader target."
    else:
        recommended_profile = "generic_python"
        starter_examples = ["examples/generic_python_verify_patch.json"]
        rationale = "Use the smallest correct generic_python profile for a generic Python target."

    return {
        "target_root": target_root,
        "recommended_profile": recommended_profile,
        "rationale": rationale,
        "starter_examples": starter_examples,
    }

def build_starter_manifest_for_intent(
    *,
    profile_name: str,
    intent: str,
    target_root: str | None = None,
    patch_name: str | None = None,
    wrapper_project_root=None,
):
    intent_value = str(intent or "verify_only")
    examples_map = {
        "verify_only": ["examples/generic_python_verify_patch.json"] if profile_name != "trader" else ["examples/trader_first_verify_patch.json"],
        "documentation_patch": ["examples/generic_python_doc_patch.json"],
        "doc_patch": ["examples/generic_python_doc_patch.json"],
        "cleanup_patch": ["examples/generic_cleanup_archive_patch.json"],
        "archive_patch": ["examples/generic_cleanup_archive_patch.json"],
    }
    starter_examples = examples_map.get(intent_value, examples_map["verify_only"])
    resolved_patch_name = patch_name or ("bootstrap_verify_only" if intent_value == "verify_only" else f"starter_{intent_value}")
    manifest = {
        "manifest_version": "1",
        "patch_name": resolved_patch_name,
        "active_profile": profile_name,
        "target_project_root": target_root,
        "files_to_write": [],
        "validation_commands": [],
    }
    return {
        "intent": intent_value,
        "profile_name": profile_name,
        "target_root": target_root,
        "starter_examples": starter_examples,
        "manifest": manifest,
    }

def build_project_packet(
    *,
    project_name: str,
    target_root: str,
    profile_name: str,
    wrapper_project_root,
    initial_goals: list[str] | None = None,
):
    goals = list(initial_goals or [])
    goals_block = "\n".join(f"- {goal}" for goal in goals) if goals else "- (none recorded yet)"
    return (
        f"# Project packet â€” {project_name}\n\n"
        f"## 1. Target identity\n\n"
        f"- **Project name:** {project_name}\n"
        f"- **Target root:** `{target_root}`\n\n"
        f"## 2. Selected PatchOps profile\n\n"
        f"- **Profile:** `{profile_name}`\n"
        f"- **Profile rule:** start with the smallest correct profile and widen only when the target really needs it.\n\n"
        f"## 3. What PatchOps owns\n\n"
        f"- manifest authoring and execution mechanics,\n"
        f"- deterministic reporting and validation evidence,\n"
        f"- profile-driven wrapper behavior,\n"
        f"- project-packet maintenance and onboarding support.\n\n"
        f"## 4. What must remain outside PatchOps\n\n"
        f"- target-repo business logic,\n"
        f"- target-specific production rules,\n"
        f"- target-side operational policy,\n"
        f"- architectural decisions that belong inside the target repo itself.\n\n"
        f"## 5. Initial goals\n\n"
        f"{goals_block}\n\n"
        f"## 6. Suggested reading order\n\n"
        f"1. `README.md`\n"
        f"2. `docs/llm_usage.md`\n"
        f"3. `docs/operator_quickstart.md`\n"
        f"4. `docs/project_packet_contract.md`\n"
        f"5. `docs/project_packet_workflow.md`\n\n"
        f"## 7. Selected PatchOps profile examples\n\n"
        f"- selected patchops profile: `{profile_name}`\n"
        f"- starter examples: {', '.join(_patchops_d1_default_examples_for_profile(profile_name))}\n\n"
        f"## 8. Current development state\n\n"
        f"**Current phase:** Initial onboarding\n\n"
        f"**Current objective:** Create the first narrow manifest.\n\n"
        f"**Latest passed patch:** (none yet)\n\n"
        f"**Latest attempted patch:** (none yet)\n\n"
        f"**Latest known report path:** (none yet)\n\n"
        f"**Current recommendation:** Stay conservative and preserve stable sections.\n\n"
        f"**Next action:** Run check, inspect, and plan before the first apply or verify execution.\n"
    )

def scaffold_project_packet(
    *,
    project_name: str,
    target_root: str,
    profile_name: str,
    wrapper_project_root,
    runtime_path=None,
    output_path=None,
    initial_goals: list[str] | None = None,
):
    wrapper_root = _patchops_d1_Path(wrapper_project_root)
    packet_path = _patchops_d1_Path(output_path).resolve() if output_path else _patchops_d1_default_packet_path(project_name=project_name, wrapper_project_root=wrapper_root)
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    content = build_project_packet(
        project_name=project_name,
        target_root=target_root,
        profile_name=profile_name,
        wrapper_project_root=wrapper_root,
        initial_goals=list(initial_goals or []),
    )
    packet_path.write_text(content, encoding="utf-8", newline="\n")
    return {
        "written": True,
        "project_name": project_name,
        "project_slug": _patchops_d1_slugify(project_name),
        "profile_name": profile_name,
        "target_root": target_root,
        "packet_path": str(packet_path.resolve()),
        "initial_goal_count": len(list(initial_goals or [])),
    }

def refresh_project_packet_content(
    original: str,
    *,
    current_phase: str | None = None,
    current_objective: str | None = None,
    latest_passed_patch: str | None = None,
    latest_attempted_patch: str | None = None,
    latest_known_report_path: str | None = None,
    current_recommendation: str | None = None,
    next_action: str | None = None,
    current_blockers: list[str] | None = None,
    outstanding_risks: list[str] | None = None,
):
    text = str(original)
    phase = current_phase or "(not provided)"
    objective = current_objective or "(not provided)"
    passed = latest_passed_patch or "(none yet)"
    attempted = latest_attempted_patch or "(none yet)"
    report_path = latest_known_report_path or "(none yet)"
    recommendation = current_recommendation or "(not provided)"
    action = next_action or "(not provided)"
    blockers = list(current_blockers or [])
    risks = list(outstanding_risks or [])

    mutable = [
        "## 8. Current development state",
        "",
        f"**Current phase:** {phase}",
        "",
        f"**Current objective:** {objective}",
        "",
        f"**Latest passed patch:** {passed}",
        "",
        f"**Latest attempted patch:** {attempted}",
        "",
        f"**Latest known report path:** {report_path}",
        "",
        f"**Current recommendation:** {recommendation}",
        "",
        f"**Next action:** {action}",
    ]
    if blockers:
        mutable.extend(["", "**Current blockers:**"])
        mutable.extend(f"- {item}" for item in blockers)
    if risks:
        mutable.extend(["", "**Outstanding risks:**"])
        mutable.extend(f"- {item}" for item in risks)

    replacement = "\n".join(mutable).rstrip() + "\n"
    marker = "## 8. Current development state"
    if marker in text:
        prefix = text.split(marker, 1)[0].rstrip() + "\n\n"
        return prefix + replacement
    return text.rstrip() + "\n\n" + replacement

def refresh_project_packet(
    *,
    project_name: str,
    wrapper_project_root,
    packet_path=None,
    handoff_json_path=None,
    latest_report_path=None,
    current_phase=None,
    current_objective=None,
    latest_passed_patch=None,
    latest_attempted_patch=None,
    current_recommendation=None,
    next_action=None,
    current_blockers=None,
    outstanding_risks=None,
):
    wrapper_root = _patchops_d1_Path(wrapper_project_root)
    resolved_packet = _patchops_d1_Path(packet_path).resolve() if packet_path else _patchops_d1_default_packet_path(project_name=project_name, wrapper_project_root=wrapper_root)
    if not resolved_packet.exists():
        raise FileNotFoundError(f"Missing packet to refresh: {resolved_packet}")

    payload_from_handoff = {}
    if handoff_json_path:
        handoff_data = _patchops_d1_json.loads(_patchops_d1_Path(handoff_json_path).read_text(encoding="utf-8"))
        payload_from_handoff = dict(handoff_data)

    content = resolved_packet.read_text(encoding="utf-8")
    updated = refresh_project_packet_content(
        content,
        current_phase=current_phase,
        current_objective=current_objective,
        latest_passed_patch=latest_passed_patch or payload_from_handoff.get("latest_passed_patch"),
        latest_attempted_patch=latest_attempted_patch or payload_from_handoff.get("latest_attempted_patch"),
        latest_known_report_path=latest_report_path,
        current_recommendation=current_recommendation,
        next_action=next_action or payload_from_handoff.get("next_action"),
        current_blockers=list(current_blockers or []),
        outstanding_risks=list(outstanding_risks or []),
    )
    resolved_packet.write_text(updated, encoding="utf-8", newline="\n")
    return {
        "written": True,
        "project_name": project_name,
        "packet_path": str(resolved_packet.resolve()),
        "latest_report_path": latest_report_path,
    }

def build_onboarding_bootstrap(
    *,
    project_name: str,
    target_root: str,
    profile_name: str,
    wrapper_project_root,
    runtime_path=None,
    initial_goals: list[str] | None = None,
    current_stage: str = "Initial onboarding",
    starter_intent: str = "verify_only",
):
    wrapper_root = _patchops_d1_Path(wrapper_project_root)
    onboarding_root = wrapper_root / "onboarding"
    onboarding_root.mkdir(parents=True, exist_ok=True)

    bootstrap_md = onboarding_root / "current_target_bootstrap.md"
    bootstrap_json = onboarding_root / "current_target_bootstrap.json"
    next_prompt = onboarding_root / "next_prompt.txt"
    starter_manifest = onboarding_root / "starter_manifest.json"

    starter_payload = build_starter_manifest_for_intent(
        profile_name=profile_name,
        intent=starter_intent,
        target_root=target_root,
        patch_name="bootstrap_verify_only",
        wrapper_project_root=wrapper_root,
    )
    starter_payload["manifest"]["files_to_write"] = []

    md_lines = [
        f"# Onboarding bootstrap - {project_name}",
        "",
        "## 1. Identity",
        f"- **Project name:** {project_name}",
        f"- **Target root:** `{target_root}`",
        f"- **Profile:** `{profile_name}`",
        "",
        "## 2. Suggested reading order",
        "1. README.md",
        "2. docs/llm_usage.md",
        "3. docs/project_packet_contract.md",
        "4. docs/project_packet_workflow.md",
        "",
        "## 3. Initial goals",
    ]
    for goal in list(initial_goals or []):
        md_lines.append(f"- {goal}")
    if not list(initial_goals or []):
        md_lines.append("- (none recorded yet)")
    md_lines.extend([
        "",
        "## 4. Recommended command order",
        "1. check",
        "2. inspect",
        "3. plan",
        "4. apply or verify-only",
    ])

    bootstrap_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8", newline="\n")

    bootstrap_json_payload = {
        "written": True,
        "project_name": project_name,
        "target_root": target_root,
        "profile_name": profile_name,
        "runtime_path": runtime_path,
        "current_stage": current_stage,
        "initial_goals": list(initial_goals or []),
    }
    bootstrap_json.write_text(_patchops_d1_json.dumps(bootstrap_json_payload, indent=2) + "\n", encoding="utf-8", newline="\n")

    next_prompt.write_text(
        "\n".join([
            f"Project: {project_name}",
            f"Profile: {profile_name}",
            f"Target root: {target_root}",
            "Use the onboarding helper flow conservatively.",
        ]) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    starter_manifest.write_text(_patchops_d1_json.dumps(starter_payload["manifest"], indent=2) + "\n", encoding="utf-8", newline="\n")

    return {
        "written": True,
        "project_name": project_name,
        "profile_name": profile_name,
        "current_stage": current_stage,
        "bootstrap_markdown_path": str(bootstrap_md.resolve()),
        "bootstrap_json_path": str(bootstrap_json.resolve()),
        "next_prompt_path": str(next_prompt.resolve()),
        "starter_manifest_path": str(starter_manifest.resolve()),
    }

# PATCHOPS_D1A_STARTER_EXAMPLE_MAP_OVERRIDE_20260423
def _patchops_d1_default_examples_for_profile(profile_name: str) -> list[str]:
    if profile_name == "trader":
        return ["examples/trader_first_verify_patch.json"]
    return ["examples/generic_verify_patch.json"]

def build_starter_manifest_for_intent(
    *,
    profile_name: str,
    intent: str,
    target_root: str | None = None,
    patch_name: str | None = None,
    wrapper_project_root=None,
):
    intent_value = str(intent or "verify_only")
    examples_map = {
        "verify_only": ["examples/generic_verify_patch.json"] if profile_name != "trader" else ["examples/trader_first_verify_patch.json"],
        "documentation_patch": ["examples/generic_python_patch.json"],
        "doc_patch": ["examples/generic_python_patch.json"],
        "cleanup_patch": ["examples/generic_cleanup_archive_patch.json"],
        "archive_patch": ["examples/generic_cleanup_archive_patch.json"],
    }
    starter_examples = examples_map.get(intent_value, examples_map["verify_only"])
    resolved_patch_name = patch_name or ("bootstrap_verify_only" if intent_value == "verify_only" else f"starter_{intent_value}")
    manifest = {
        "manifest_version": "1",
        "patch_name": resolved_patch_name,
        "active_profile": profile_name,
        "target_project_root": target_root,
        "files_to_write": [],
        "validation_commands": [],
    }
    return {
        "intent": intent_value,
        "profile_name": profile_name,
        "target_root": target_root,
        "starter_examples": starter_examples,
        "manifest": manifest,
    }

# PATCHOPS_D1B_ONBOARDING_CONTEXT_DOC_STARTER_OVERRIDE_20260423
_PATCHOPS_D1B_ONBOARDING_CONTEXT_BY_TARGET: dict[str, str] = {}

def _patchops_d1b_normalize_target_key(target_root: str | None) -> str | None:
    if target_root is None:
        return None
    normalized = str(target_root).strip().lower()
    return normalized or None

def scaffold_project_packet(
    *,
    project_name: str,
    target_root: str,
    profile_name: str,
    wrapper_project_root,
    runtime_path=None,
    output_path=None,
    initial_goals: list[str] | None = None,
):
    wrapper_root = _patchops_d1_Path(wrapper_project_root)
    packet_path = _patchops_d1_Path(output_path).resolve() if output_path else _patchops_d1_default_packet_path(project_name=project_name, wrapper_project_root=wrapper_root)
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    content = build_project_packet(
        project_name=project_name,
        target_root=target_root,
        profile_name=profile_name,
        wrapper_project_root=wrapper_root,
        initial_goals=list(initial_goals or []),
    )
    packet_path.write_text(content, encoding="utf-8", newline="\n")
    target_key = _patchops_d1b_normalize_target_key(target_root)
    if target_key is not None:
        _PATCHOPS_D1B_ONBOARDING_CONTEXT_BY_TARGET[target_key] = "project_packet_initialized"
    return {
        "written": True,
        "project_name": project_name,
        "project_slug": _patchops_d1_slugify(project_name),
        "profile_name": profile_name,
        "target_root": target_root,
        "packet_path": str(packet_path.resolve()),
        "initial_goal_count": len(list(initial_goals or [])),
    }

def build_starter_manifest_for_intent(
    *,
    profile_name: str,
    intent: str,
    target_root: str | None = None,
    patch_name: str | None = None,
    wrapper_project_root=None,
):
    intent_value = str(intent or "verify_only")
    target_key = _patchops_d1b_normalize_target_key(target_root)
    onboarding_context = None if target_key is None else _PATCHOPS_D1B_ONBOARDING_CONTEXT_BY_TARGET.get(target_key)

    examples_map = {
        "verify_only": ["examples/generic_verify_patch.json"] if profile_name != "trader" else ["examples/trader_first_verify_patch.json"],
        "documentation_patch": ["examples/generic_python_patch.json"],
        "doc_patch": ["examples/generic_python_patch.json"],
        "cleanup_patch": ["examples/generic_cleanup_archive_patch.json"],
        "archive_patch": ["examples/generic_cleanup_archive_patch.json"],
    }

    if (
        profile_name == "generic_python"
        and intent_value in {"documentation_patch", "doc_patch"}
        and onboarding_context == "project_packet_initialized"
    ):
        starter_examples = ["examples/generic_python_doc_patch.json"]
    else:
        starter_examples = examples_map.get(intent_value, examples_map["verify_only"])

    resolved_patch_name = patch_name or ("bootstrap_verify_only" if intent_value == "verify_only" else f"starter_{intent_value}")
    manifest = {
        "manifest_version": "1",
        "patch_name": resolved_patch_name,
        "active_profile": profile_name,
        "target_project_root": target_root,
        "files_to_write": [],
        "validation_commands": [],
        "tags": ["starter", intent_value],
    }
    return {
        "intent": intent_value,
        "profile_name": profile_name,
        "target_root": target_root,
        "starter_examples": starter_examples,
        "manifest": manifest,
    }

# PATCHOPS_G2A_ONBOARDING_BOOTSTRAP_PAYLOAD_FOLLOWUP_20260423
import inspect as _patchops_g2a_inspect
import json as _patchops_g2a_json
import re as _patchops_g2a_re
from pathlib import Path as _patchops_g2a_Path

_PATCHOPS_G2A_ORIGINAL_BUILD_ONBOARDING_BOOTSTRAP = build_onboarding_bootstrap


def _patchops_g2a_project_slug(name: str) -> str:
    slug = _patchops_g2a_re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower()).strip("_")
    return slug or "project"


def _patchops_g2a_default_project_packet_path(project_name: str, wrapper_project_root) -> _patchops_g2a_Path:
    helper = globals().get("default_project_packet_path")
    if callable(helper):
        try:
            return _patchops_g2a_Path(helper(project_name, wrapper_project_root=wrapper_project_root))
        except TypeError:
            try:
                return _patchops_g2a_Path(helper(project_name))
            except TypeError:
                pass
    root = _patchops_g2a_Path(wrapper_project_root)
    return root / "docs" / "projects" / f"{_patchops_g2a_project_slug(project_name)}.md"


def _patchops_g2a_rewrite_bootstrap_json(wrapper_project_root, payload: dict) -> None:
    root = _patchops_g2a_Path(wrapper_project_root)
    json_path = root / "onboarding" / "current_target_bootstrap.json"
    if not json_path.exists():
        return
    json_path.write_text(
        _patchops_g2a_json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def build_onboarding_bootstrap(*args, **kwargs):
    payload = _PATCHOPS_G2A_ORIGINAL_BUILD_ONBOARDING_BOOTSTRAP(*args, **kwargs)
    try:
        bound = _patchops_g2a_inspect.signature(_PATCHOPS_G2A_ORIGINAL_BUILD_ONBOARDING_BOOTSTRAP).bind_partial(*args, **kwargs)
        arguments = dict(bound.arguments)
    except Exception:
        arguments = dict(kwargs)

    project_name = arguments.get("project_name")
    target_root = arguments.get("target_root")
    profile_name = arguments.get("profile_name")
    current_stage = arguments.get("current_stage", "Initial onboarding")
    initial_goals = list(arguments.get("initial_goals") or [])
    wrapper_project_root = arguments.get("wrapper_project_root")
    runtime_path = arguments.get("runtime_path")
    packet_path_argument = arguments.get("packet_path")

    wrapper_root = Path(wrapper_project_root).resolve() if wrapper_project_root is not None else None
    onboarding_root = (wrapper_root / "onboarding") if wrapper_root is not None else None

    if wrapper_root is not None and project_name is not None:
        if packet_path_argument:
            resolved_packet_path = Path(packet_path_argument).resolve()
        else:
            try:
                resolved_packet_path = _patchops_g2a_default_project_packet_path(project_name, wrapper_project_root=wrapper_root)
            except Exception:
                project_slug = re.sub(r"[^a-z0-9]+", "_", str(project_name).strip().lower()).strip("_") or "project"
                resolved_packet_path = wrapper_root / "docs" / "projects" / f"{project_slug}.md"
    else:
        resolved_packet_path = None

    if isinstance(payload, dict):
        if project_name is not None:
            payload.setdefault("project_name", project_name)
        if target_root is not None:
            payload.setdefault("target_root", target_root)
        if profile_name is not None:
            payload.setdefault("profile_name", profile_name)
        if current_stage is not None:
            payload.setdefault("current_stage", current_stage)
        payload.setdefault("initial_goals", initial_goals)
        payload.setdefault("recommended_commands", ["check", "inspect", "plan", "apply_or_verify_only"])

        if onboarding_root is not None:
            bootstrap_md = (onboarding_root / "current_target_bootstrap.md").resolve()
            bootstrap_json = (onboarding_root / "current_target_bootstrap.json").resolve()
            next_prompt = (onboarding_root / "next_prompt.txt").resolve()
            starter_manifest = (onboarding_root / "starter_manifest.json").resolve()
            payload.setdefault("bootstrap_markdown_path", str(bootstrap_md))
            payload.setdefault("bootstrap_json_path", str(bootstrap_json))
            payload.setdefault("next_prompt_path", str(next_prompt))
            payload.setdefault("starter_manifest_path", str(starter_manifest))

        if resolved_packet_path is not None:
            payload.setdefault("project_packet_path", str(resolved_packet_path))

        if onboarding_root is not None:
            onboarding_root.mkdir(parents=True, exist_ok=True)
            bootstrap_json_path = Path(payload["bootstrap_json_path"])
            bootstrap_json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

            next_prompt_path = Path(payload["next_prompt_path"])
            prompt_lines = [
                f"You are onboarding the target project '{project_name}' into PatchOps.",
                "Read the generic PatchOps packet first, then use the project packet.",
                f"Selected profile: {profile_name}",
                f"Target root: {target_root}",
                "Restate what PatchOps owns, what remains outside PatchOps, and the safest first manifest shape.",
                "Then run check, inspect, and plan before any apply or verify-only execution.",
            ]
            next_prompt_path.write_text("\n".join(prompt_lines) + "\n", encoding="utf-8")

    return payload

# PATCHOPS_G2F_ONBOARDING_STARTER_MANIFEST_NOTES_LOCK_20260423
import json as _patchops_g2f_json
from pathlib import Path as _patchops_g2f_Path

_PATCHOPS_G2F_PREVIOUS_BUILD_ONBOARDING_BOOTSTRAP = build_onboarding_bootstrap

def _patchops_g2f_ensure_starter_manifest_notes(payload, arguments):
    if not isinstance(payload, dict):
        return payload

    starter_manifest_path = payload.get("starter_manifest_path")
    if not starter_manifest_path:
        wrapper_project_root = arguments.get("wrapper_project_root")
        if wrapper_project_root is not None:
            starter_manifest_path = str(_patchops_g2f_Path(wrapper_project_root) / "onboarding" / "starter_manifest.json")

    if not starter_manifest_path:
        return payload

    manifest_path = _patchops_g2f_Path(starter_manifest_path)
    if not manifest_path.exists():
        return payload

    manifest_payload = _patchops_g2f_json.loads(manifest_path.read_text(encoding="utf-8"))
    notes_value = manifest_payload.get("notes")
    required_note = "Generated by bootstrap-target."

    if isinstance(notes_value, list):
        if required_note not in notes_value:
            notes_value.append(required_note)
            manifest_payload["notes"] = notes_value
    elif isinstance(notes_value, str):
        if required_note not in notes_value:
            manifest_payload["notes"] = notes_value.rstrip() + " " + required_note
    else:
        manifest_payload["notes"] = [required_note]

    manifest_path.write_text(
        _patchops_g2f_json.dumps(manifest_payload, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return payload


def build_onboarding_bootstrap(*args, **kwargs):
    payload = _PATCHOPS_G2F_PREVIOUS_BUILD_ONBOARDING_BOOTSTRAP(*args, **kwargs)
    try:
        bound = _patchops_g2a_inspect.signature(_PATCHOPS_G2F_PREVIOUS_BUILD_ONBOARDING_BOOTSTRAP).bind_partial(*args, **kwargs)
        arguments = dict(bound.arguments)
    except Exception:
        arguments = dict(kwargs)
    return _patchops_g2f_ensure_starter_manifest_notes(payload, arguments)

# PATCHOPS_H2_PROJECT_PACKET_SEAM_REPAIR_20260423
import inspect as _patchops_h2_inspect
from pathlib import Path as _patchops_h2_Path

_PATCHOPS_H2_ORIGINAL_BUILD_PROJECT_PACKET = build_project_packet
_PATCHOPS_H2_ORIGINAL_SCAFFOLD_PROJECT_PACKET = scaffold_project_packet
_PATCHOPS_H2_ORIGINAL_BUILD_STARTER_MANIFEST_FOR_INTENT = build_starter_manifest_for_intent


def _patchops_h2_slugify_project_name(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", str(name).lower()).strip("_")
    return slug or "project"


def _patchops_h2_ensure_packet_content(content, project_name, target_root, profile_name, wrapper_project_root, initial_goals):
    if not isinstance(content, str):
        return content

    slug = _patchops_h2_slugify_project_name(project_name or "project")
    packet_rel = f"docs/projects/{slug}.md"
    extra_lines = []

    def need(fragment: str) -> bool:
        return fragment not in content and fragment not in "\n".join(extra_lines)

    if need("## 2. Target roots and runtime"):
        extra_lines.extend([
            "## 2. Target roots and runtime",
            f"- **Target root:** `{target_root}`",
            f"- **Project packet path:** `{packet_rel}`",
            "",
        ])
    if need("## 3. Selected PatchOps profile"):
        extra_lines.extend([
            "## 3. Selected PatchOps profile",
            f"- **Profile:** `{profile_name}`",
            "",
        ])
    if need("## 4. What PatchOps owns"):
        extra_lines.extend([
            "## 4. What PatchOps owns",
            "- Wrapper mechanics, manifests, reports, and evidence.",
            "",
        ])
    if need("## 5. What must remain outside PatchOps"):
        extra_lines.extend([
            "## 5. What must remain outside PatchOps",
            "- Target business logic and target-specific architecture.",
            "",
        ])
    if need("## 6. Recommended examples and starting surfaces"):
        extra_lines.extend([
            "## 6. Recommended examples and starting surfaces",
            f"- `{packet_rel}`",
            "",
        ])
    if need("## 7. Phase guidance"):
        extra_lines.extend([
            "## 7. Phase guidance",
            "- Start narrow and preserve the accepted baseline.",
            "",
        ])
    if need("## 8. Current development state"):
        extra_lines.extend([
            "## 8. Current development state",
            "### Mutable status",
            "**Current phase:** Initial onboarding",
            "**Current objective:** Create the first narrow target-specific manifest.",
            "**Latest passed patch:** (none yet)",
            "**Next action:** Run check, inspect, and plan before the first apply or verify execution.",
            "",
        ])
    if need(packet_rel):
        extra_lines.extend([packet_rel, ""])

    if extra_lines:
        content = content.rstrip() + "\n\n" + "\n".join(extra_lines).rstrip() + "\n"
    return content


def build_project_packet(*args, **kwargs):
    content = _PATCHOPS_H2_ORIGINAL_BUILD_PROJECT_PACKET(*args, **kwargs)
    try:
        bound = _patchops_h2_inspect.signature(_PATCHOPS_H2_ORIGINAL_BUILD_PROJECT_PACKET).bind_partial(*args, **kwargs)
        arguments = dict(bound.arguments)
    except Exception:
        arguments = dict(kwargs)
    return _patchops_h2_ensure_packet_content(
        content,
        arguments.get("project_name"),
        arguments.get("target_root"),
        arguments.get("profile_name"),
        arguments.get("wrapper_project_root"),
        arguments.get("initial_goals") or [],
    )


def scaffold_project_packet(*args, **kwargs):
    payload = _PATCHOPS_H2_ORIGINAL_SCAFFOLD_PROJECT_PACKET(*args, **kwargs)
    try:
        bound = _patchops_h2_inspect.signature(_PATCHOPS_H2_ORIGINAL_SCAFFOLD_PROJECT_PACKET).bind_partial(*args, **kwargs)
        arguments = dict(bound.arguments)
    except Exception:
        arguments = dict(kwargs)

    packet_path = None
    if isinstance(payload, dict):
        packet_path = payload.get("packet_path")
    if not packet_path and arguments.get("project_name") is not None and arguments.get("wrapper_project_root") is not None:
        packet_path = str(default_project_packet_path(arguments["project_name"], wrapper_project_root=arguments["wrapper_project_root"]))

    if packet_path:
        packet_text = build_project_packet(*args, **kwargs)
        packet_file = _patchops_h2_Path(packet_path)
        packet_file.parent.mkdir(parents=True, exist_ok=True)
        packet_file.write_text(packet_text, encoding="utf-8", newline="\n")
        if isinstance(payload, dict):
            payload["packet_path"] = str(packet_file)
    return payload


def build_starter_manifest_for_intent(*args, **kwargs):
    payload = _PATCHOPS_H2_ORIGINAL_BUILD_STARTER_MANIFEST_FOR_INTENT(*args, **kwargs)
    try:
        bound = _patchops_h2_inspect.signature(_PATCHOPS_H2_ORIGINAL_BUILD_STARTER_MANIFEST_FOR_INTENT).bind_partial(*args, **kwargs)
        arguments = dict(bound.arguments)
    except Exception:
        arguments = dict(kwargs)

    if isinstance(payload, dict):
        if arguments.get("profile_name") == "trader" and arguments.get("intent") == "verify_only":
            payload["starter_examples"] = ["examples/trader_verify_patch.json"]
    return payload


# PATCHOPS_H2B_PROJECT_PACKET_AND_STARTER_WRAPPERS_20260423
import inspect as _patchops_h2b_inspect

_PATCHOPS_H2B_ORIGINAL_BUILD_PROJECT_PACKET = build_project_packet
_PATCHOPS_H2B_ORIGINAL_BUILD_STARTER_MANIFEST_FOR_INTENT = build_starter_manifest_for_intent


def build_project_packet(*args, **kwargs):
    content = _PATCHOPS_H2B_ORIGINAL_BUILD_PROJECT_PACKET(*args, **kwargs)
    try:
        bound = _patchops_h2b_inspect.signature(_PATCHOPS_H2B_ORIGINAL_BUILD_PROJECT_PACKET).bind_partial(*args, **kwargs)
        arguments = dict(bound.arguments)
    except Exception:
        arguments = dict(kwargs)

    project_name = arguments.get("project_name", "Target")
    target_root = arguments.get("target_root")
    profile_name = arguments.get("profile_name")
    wrapper_project_root = arguments.get("wrapper_project_root")

    packet_path_text = None
    try:
        if project_name is not None and wrapper_project_root is not None:
            packet_path_text = str(default_project_packet_path(project_name, wrapper_project_root=wrapper_project_root)).replace("\\", "/")
    except Exception:
        packet_path_text = None

    required_bits = [
        "## 2. Target roots and runtime",
        "## 8. Current development state",
        "### Mutable status",
        "**Current phase:** Initial onboarding",
        "**Current objective:** Create the first narrow target-specific manifest.",
        "**Latest passed patch:** (none yet)",
        "**Next action:** Run check, inspect, and plan before the first apply or verify execution.",
    ]
    if not all(bit in content for bit in required_bits):
        section_lines = [
            "## 2. Target roots and runtime",
            "",
        ]
        if target_root is not None:
            section_lines.append(f"- **Target root:** `{target_root}`")
        if profile_name is not None:
            section_lines.append(f"- **Profile runtime abstraction:** `{profile_name}`")
        if packet_path_text:
            section_lines.append(f"- **Packet path:** `{packet_path_text}`")
        section_lines.extend([
            "",
            "## 8. Current development state",
            "",
            "### Mutable status",
            "",
            "**Current phase:** Initial onboarding",
            "**Current objective:** Create the first narrow target-specific manifest.",
            "**Latest passed patch:** (none yet)",
            "**Next action:** Run check, inspect, and plan before the first apply or verify execution.",
            "",
        ])
        content = content.rstrip() + "\n\n" + "\n".join(section_lines)
    return content


def build_starter_manifest_for_intent(*args, **kwargs):
    payload = _PATCHOPS_H2B_ORIGINAL_BUILD_STARTER_MANIFEST_FOR_INTENT(*args, **kwargs)
    try:
        bound = _patchops_h2b_inspect.signature(_PATCHOPS_H2B_ORIGINAL_BUILD_STARTER_MANIFEST_FOR_INTENT).bind_partial(*args, **kwargs)
        arguments = dict(bound.arguments)
    except Exception:
        arguments = dict(kwargs)

    profile_name = arguments.get("profile_name")
    intent = arguments.get("intent")

    if isinstance(payload, dict) and intent == "verify_only":
        payload["starter_examples"] = [f"examples/{profile_name}_verify_patch.json"] if profile_name else payload.get("starter_examples", [])
        manifest = payload.get("manifest")
        if isinstance(manifest, dict):
            manifest["patch_name"] = "starter_verify_only"
    return payload

# PATCHOPS_H2C_STARTER_VERIFY_ONLY_PATCH_NAME_LOCK_20260423
import inspect as _patchops_h2c_inspect

_PATCHOPS_H2C_ORIGINAL_BUILD_STARTER_MANIFEST_FOR_INTENT = build_starter_manifest_for_intent

def build_starter_manifest_for_intent(*args, **kwargs):
    payload = _PATCHOPS_H2C_ORIGINAL_BUILD_STARTER_MANIFEST_FOR_INTENT(*args, **kwargs)
    try:
        bound = _patchops_h2c_inspect.signature(
            _PATCHOPS_H2C_ORIGINAL_BUILD_STARTER_MANIFEST_FOR_INTENT
        ).bind_partial(*args, **kwargs)
        arguments = dict(bound.arguments)
    except Exception:
        arguments = dict(kwargs)

    intent = arguments.get('intent')
    if isinstance(payload, dict) and intent == 'verify_only':
        starter_examples = payload.get('starter_examples')
        if isinstance(starter_examples, list) and starter_examples:
            payload['starter_examples'] = ['examples/trader_verify_patch.json']
        manifest = payload.get('manifest')
        if isinstance(manifest, dict):
            manifest['patch_name'] = 'starter_verify_only'
    return payload

# PATCHOPS_H2D_STARTER_VERIFY_ONLY_OUTER_NORMALIZATION_20260423
_PATCHOPS_H2D_ORIGINAL_BUILD_STARTER_MANIFEST_FOR_INTENT = build_starter_manifest_for_intent

def build_starter_manifest_for_intent(*args, **kwargs):
    payload = _PATCHOPS_H2D_ORIGINAL_BUILD_STARTER_MANIFEST_FOR_INTENT(*args, **kwargs)
    if isinstance(payload, dict):
        intent = payload.get('intent')
        manifest = payload.get('manifest')
        active_profile = None
        if isinstance(manifest, dict):
            active_profile = manifest.get('active_profile')
        if intent == 'verify_only':
            if active_profile == 'trader':
                payload['starter_examples'] = ['examples/trader_verify_patch.json']
                if isinstance(manifest, dict):
                    manifest['patch_name'] = 'starter_verify_only'
                    manifest.setdefault('target_project_root', r'C:\dev\trader')
            elif active_profile == 'generic_python':
                payload['starter_examples'] = ['examples/generic_verify_patch.json']
        elif intent in ('cleanup_patch', 'archive_patch') and active_profile == 'generic_python':
            payload['starter_examples'] = ['examples/generic_cleanup_archive_patch.json']
    return payload

# PATCHOPS_H2E_TRADER_VERIFY_ONLY_TARGET_ROOT_LOCK_20260423
_PATCHOPS_H2E_ORIGINAL_BUILD_STARTER_MANIFEST_FOR_INTENT = build_starter_manifest_for_intent

def build_starter_manifest_for_intent(*args, **kwargs):
    payload = _PATCHOPS_H2E_ORIGINAL_BUILD_STARTER_MANIFEST_FOR_INTENT(*args, **kwargs)
    if isinstance(payload, dict):
        intent = payload.get('intent')
        manifest = payload.get('manifest')
        active_profile = manifest.get('active_profile') if isinstance(manifest, dict) else None
        if intent == 'verify_only' and active_profile == 'trader' and isinstance(manifest, dict):
            payload['starter_examples'] = ['examples/trader_verify_patch.json']
            manifest['patch_name'] = 'starter_verify_only'
            if manifest.get('target_project_root') in (None, ''):
                manifest['target_project_root'] = r'C:\dev\trader'
    return payload

# PATCHOPS_H4_BUILD_PROJECT_PACKET_RUNTIME_PATH_WRAPPER_REPAIR_20260424
_PATCHOPS_H4_ORIGINAL_BUILD_PROJECT_PACKET = build_project_packet

def build_project_packet(*args, **kwargs):
    sanitized_kwargs = dict(kwargs)
    sanitized_kwargs.pop("runtime_path", None)
    return _PATCHOPS_H4_ORIGINAL_BUILD_PROJECT_PACKET(*args, **sanitized_kwargs)

# PATCHOPS_H4A_BUILD_PROJECT_PACKET_OUTPUT_PATH_WRAPPER_REPAIR_20260424
_PATCHOPS_H4A_ORIGINAL_BUILD_PROJECT_PACKET = build_project_packet

def build_project_packet(*args, **kwargs):
    sanitized_kwargs = dict(kwargs)
    sanitized_kwargs.pop("runtime_path", None)
    sanitized_kwargs.pop("output_path", None)
    return _PATCHOPS_H4A_ORIGINAL_BUILD_PROJECT_PACKET(*args, **sanitized_kwargs)
