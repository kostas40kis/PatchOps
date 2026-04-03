from __future__ import annotations

import json
from pathlib import Path


PATCH_81_BLOCK = r"""
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
        runtime_override=runtime_override,
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
        runtime_override=runtime_override,
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
"""

TEST_CONTENT = r"""from __future__ import annotations

import json
from pathlib import Path

from patchops.cli import main
from patchops.project_packets import bootstrap_target_onboarding


def test_bootstrap_target_onboarding_writes_expected_artifacts(tmp_path) -> None:
    payload = bootstrap_target_onboarding(
        project_name="OSM Remediation",
        target_root=r"C:\dev\osm",
        profile_name="generic_python",
        wrapper_project_root=tmp_path,
        initial_goals=["Document the target", "Create the first manifest"],
        starter_intent="documentation_patch",
    )

    onboarding_root = tmp_path / "onboarding"
    bootstrap_md = onboarding_root / "current_target_bootstrap.md"
    bootstrap_json = onboarding_root / "current_target_bootstrap.json"
    next_prompt = onboarding_root / "next_prompt.txt"
    starter_manifest = onboarding_root / "starter_manifest.json"

    assert payload["written"] is True
    assert payload["project_name"] == "OSM Remediation"
    assert payload["packet_path"].endswith("docs/projects/osm_remediation.md")
    assert payload["starter_manifest_path"] == str(starter_manifest.resolve())
    assert bootstrap_md.exists()
    assert bootstrap_json.exists()
    assert next_prompt.exists()
    assert starter_manifest.exists()

    md_text = bootstrap_md.read_text(encoding="utf-8")
    assert "# Current target bootstrap" in md_text
    assert "OSM Remediation" in md_text
    assert "Read these docs first:" in md_text
    assert "docs/projects/osm_remediation.md" in md_text

    json_payload = json.loads(bootstrap_json.read_text(encoding="utf-8"))
    assert json_payload["selected_profile"] == "generic_python"
    assert json_payload["starter_intent"] == "documentation_patch"
    assert json_payload["target_root"] == r"C:\dev\osm"
    assert json_payload["generic_docs"][0] == "README.md"

    starter_payload = json.loads(starter_manifest.read_text(encoding="utf-8"))
    assert starter_payload["active_profile"] == "generic_python"
    assert starter_payload["target_project_root"] == r"C:\dev\osm"
    assert starter_payload["intent"] == "documentation_patch"
    assert starter_payload["project_packet_path"].endswith("docs/projects/osm_remediation.md")

    prompt_text = next_prompt.read_text(encoding="utf-8")
    assert "Read these docs first:" in prompt_text
    assert "docs/projects/osm_remediation.md" in prompt_text
    assert "Then create or adapt the first manifest conservatively." in prompt_text


def test_bootstrap_target_cli_writes_bundle_and_returns_json(capsys, tmp_path) -> None:
    exit_code = main(
        [
            "bootstrap-target",
            "--project-name",
            "Wrapper Self Hosted",
            "--target-root",
            r"C:\dev\patchops",
            "--profile",
            "generic_python",
            "--wrapper-root",
            str(tmp_path),
            "--starter-intent",
            "documentation_patch",
            "--initial-goal",
            "Create onboarding bundle",
            "--initial-goal",
            "Create starter manifest stub",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)

    onboarding_root = tmp_path / "onboarding"
    assert payload["project_name"] == "Wrapper Self Hosted"
    assert Path(payload["packet_path"]).exists()
    assert (onboarding_root / "current_target_bootstrap.md").exists()
    assert (onboarding_root / "current_target_bootstrap.json").exists()
    assert (onboarding_root / "next_prompt.txt").exists()
    assert (onboarding_root / "starter_manifest.json").exists()
"""

def append_block_once(text: str, marker: str, block: str) -> str:
    if marker in text:
        return text
    return text.rstrip() + "\n\n" + block.strip() + "\n"


def patch_cli(cli_text: str) -> str:
    if 'command == "bootstrap-target"' in cli_text:
        return cli_text

    command_block = """
    if command == "bootstrap-target":
        import argparse
        import json

        from patchops.project_packets import bootstrap_target_onboarding

        bootstrap_parser = argparse.ArgumentParser(prog="patchops bootstrap-target")
        bootstrap_parser.add_argument("--project-name", required=True)
        bootstrap_parser.add_argument("--target-root", required=True)
        bootstrap_parser.add_argument("--profile", required=True)
        bootstrap_parser.add_argument("--wrapper-root", default=".")
        bootstrap_parser.add_argument("--runtime-override", default=None)
        bootstrap_parser.add_argument("--starter-intent", default="documentation_patch")
        bootstrap_parser.add_argument("--initial-goal", action="append", default=[])
        bootstrap_args = bootstrap_parser.parse_args(argv[1:])

        payload = bootstrap_target_onboarding(
            project_name=bootstrap_args.project_name,
            target_root=bootstrap_args.target_root,
            profile_name=bootstrap_args.profile,
            wrapper_project_root=bootstrap_args.wrapper_root,
            initial_goals=bootstrap_args.initial_goal,
            runtime_override=bootstrap_args.runtime_override,
            starter_intent=bootstrap_args.starter_intent,
        )
        print(json.dumps(payload, indent=2))
        return 0
"""

    replacement_targets = [
        '    parser.error("Unknown command")',
        "    parser.error('Unknown command')",
    ]
    for target in replacement_targets:
        if target in cli_text:
            return cli_text.replace(target, command_block.rstrip() + "\n\n" + target, 1)
    raise RuntimeError("Could not find fallback parser.error line in patchops/cli.py")


def main() -> int:
    project_root = Path(__file__).resolve().parents[4]
    project_packets_path = project_root / "patchops" / "project_packets.py"
    cli_path = project_root / "patchops" / "cli.py"
    test_path = project_root / "tests" / "test_project_packet_onboarding_bootstrap.py"

    project_packets_text = project_packets_path.read_text(encoding="utf-8")
    project_packets_text = append_block_once(
        project_packets_text,
        "# PATCHOPS_PATCH_81_ONBOARDING_BOOTSTRAP_START",
        PATCH_81_BLOCK,
    )
    project_packets_path.write_text(project_packets_text, encoding="utf-8")

    cli_text = cli_path.read_text(encoding="utf-8")
    cli_text = patch_cli(cli_text)
    cli_path.write_text(cli_text, encoding="utf-8")

    test_path.write_text(TEST_CONTENT, encoding="utf-8")

    print(
        json.dumps(
            {
                "written_files": [
                    str(project_packets_path),
                    str(cli_path),
                    str(test_path),
                ]
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())