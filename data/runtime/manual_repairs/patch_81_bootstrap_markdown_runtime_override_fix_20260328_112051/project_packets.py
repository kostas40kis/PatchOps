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
