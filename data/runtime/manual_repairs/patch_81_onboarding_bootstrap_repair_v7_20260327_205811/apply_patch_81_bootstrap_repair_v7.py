from __future__ import annotations

import json
from pathlib import Path

BOOTSTRAP_PARSER_BLOCK = """
    bootstrap_target_parser = subparsers.add_parser(
        "bootstrap-target",
        help="Generate onboarding bootstrap artifacts for a target project.",
    )
    bootstrap_target_parser.description = (
        "Generate onboarding artifacts parallel to handoff for a brand-new target project."
    )
    bootstrap_target_parser.add_argument("--project-name", required=True, help="Human-readable target project name")
    bootstrap_target_parser.add_argument("--target-root", required=True, help="Target project root for onboarding")
    bootstrap_target_parser.add_argument("--profile", required=True, help="PatchOps profile to anchor the onboarding bundle")
    bootstrap_target_parser.add_argument("--runtime-path", default=None, help="Optional explicit runtime override")
    bootstrap_target_parser.add_argument("--wrapper-root", help="Override wrapper project root", default=None)
    bootstrap_target_parser.add_argument(
        "--initial-goal",
        action="append",
        default=[],
        help="Optional initial goal line; may be supplied more than once.",
    )
    bootstrap_target_parser.add_argument(
        "--starter-intent",
        default="documentation_patch",
        help="Starter manifest intent for the onboarding bundle.",
    )

"""

MAIN_TAIL = """
    if args.command == "refresh-project-doc":
        from patchops.project_packets import refresh_project_packet

        payload = refresh_project_packet(
            project_name=args.project_name,
            wrapper_project_root=args.wrapper_root,
            packet_path=args.packet_path,
            handoff_json_path=args.handoff_json_path,
            latest_report_path=args.report_path,
            current_phase=args.current_phase,
            current_objective=args.current_objective,
            latest_passed_patch=args.latest_passed_patch,
            latest_attempted_patch=args.latest_attempted_patch,
            current_recommendation=args.current_recommendation,
            next_action=args.next_action,
            current_blockers=args.blocker,
            outstanding_risks=args.risk,
        )
        print(json.dumps(payload, indent=2))
        return 0

    if args.command == "bootstrap-target":
        from patchops.project_packets import bootstrap_target_onboarding

        payload = bootstrap_target_onboarding(
            project_name=args.project_name,
            target_root=args.target_root,
            profile_name=args.profile,
            runtime_override=args.runtime_path,
            wrapper_project_root=args.wrapper_root,
            initial_goals=args.initial_goal,
            starter_intent=args.starter_intent,
        )
        print(json.dumps(payload, indent=2))
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
"""

TEST_FILE = """from __future__ import annotations

import json
from pathlib import Path

from patchops.cli import main
from patchops.project_packets import bootstrap_target_onboarding


def test_bootstrap_target_onboarding_writes_expected_artifacts(tmp_path) -> None:
    payload = bootstrap_target_onboarding(
        project_name="OSM Remediation",
        target_root=r"C:\\dev\\osm",
        profile_name="generic_python",
        wrapper_project_root=tmp_path,
        initial_goals=["Document the target", "Create the first manifest"],
        starter_intent="documentation_patch",
    )

    assert payload["written"] is True
    assert payload["project_name"] == "OSM Remediation"

    onboarding_root = Path(payload["onboarding_root"])
    assert onboarding_root.exists()

    bootstrap_md = Path(payload["bootstrap_markdown_path"])
    bootstrap_json = Path(payload["bootstrap_json_path"])
    next_prompt = Path(payload["next_prompt_path"])
    starter_manifest = Path(payload["starter_manifest_path"])
    packet_path = Path(payload["packet_path"])

    assert bootstrap_md.exists()
    assert bootstrap_json.exists()
    assert next_prompt.exists()
    assert starter_manifest.exists()
    assert packet_path.exists()

    md_text = bootstrap_md.read_text(encoding="utf-8")
    assert "# Current target bootstrap" in md_text
    assert "OSM Remediation" in md_text
    assert "documentation_patch" in md_text

    json_payload = json.loads(bootstrap_json.read_text(encoding="utf-8"))
    assert json_payload["project_name"] == "OSM Remediation"
    assert json_payload["starter_intent"] == "documentation_patch"


def test_bootstrap_target_cli_writes_bundle_and_returns_json(capsys, tmp_path) -> None:
    exit_code = main(
        [
            "bootstrap-target",
            "--project-name",
            "Wrapper Self Hosted",
            "--target-root",
            r"C:\\dev\\patchops",
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
    assert payload["written"] is True
    assert payload["project_name"] == "Wrapper Self Hosted"
    assert Path(payload["bootstrap_markdown_path"]).exists()
    assert Path(payload["bootstrap_json_path"]).exists()
    assert Path(payload["next_prompt_path"]).exists()
    assert Path(payload["starter_manifest_path"]).exists()
"""

BOOTSTRAP_FUNCTION = """
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

    onboarding_root = wrapper_root / "onboarding"
    onboarding_root.mkdir(parents=True, exist_ok=True)

    packet_path = packet_payload["packet_path"]
    bootstrap_md_path = onboarding_root / "current_target_bootstrap.md"
    bootstrap_json_path = onboarding_root / "current_target_bootstrap.json"
    next_prompt_path = onboarding_root / "next_prompt.txt"
    starter_manifest_path = onboarding_root / "starter_manifest.json"

    md_lines = [
        "# Current target bootstrap",
        "",
        f"- **Project name:** {project_name}",
        f"- **Target root:** `{target_root}`",
        f"- **Profile:** `{profile_name}`",
        f"- **Packet path:** `{packet_path}`",
        f"- **Starter intent:** `{starter_intent}`",
        "",
        "## Initial goals",
    ]
    if initial_goals:
        md_lines.extend(f"- {goal}" for goal in initial_goals)
    else:
        md_lines.append("- (none)")
    md_lines.extend(
        [
            "",
            "## Recommended next steps",
            "- Read the generic PatchOps onboarding docs.",
            "- Read the generated project packet.",
            "- Run check, inspect, and plan before the first apply.",
        ]
    )
    if runtime_override:
        md_lines.extend(["", f"- **Runtime override:** `{runtime_override}`"])
    bootstrap_md_path.write_text("\\n".join(md_lines) + "\\n", encoding="utf-8")

    bootstrap_payload = {
        "written": True,
        "project_name": project_name,
        "target_root": target_root,
        "profile_name": profile_name,
        "packet_path": str(Path(packet_path).resolve()),
        "onboarding_root": str(onboarding_root.resolve()),
        "bootstrap_markdown_path": str(bootstrap_md_path.resolve()),
        "bootstrap_json_path": str(bootstrap_json_path.resolve()),
        "next_prompt_path": str(next_prompt_path.resolve()),
        "starter_manifest_path": str(starter_manifest_path.resolve()),
        "starter_intent": starter_intent,
        "runtime_override": runtime_override,
        "initial_goals": initial_goals,
    }
    bootstrap_json_path.write_text(json.dumps(bootstrap_payload, indent=2), encoding="utf-8")

    next_prompt_lines = [
        "Read the generic PatchOps onboarding docs first.",
        f"Then read the project packet at {packet_path}.",
        f"Starter intent: {starter_intent}.",
        "Create or validate the first narrow manifest from that starting point.",
    ]
    next_prompt_path.write_text("\\n".join(next_prompt_lines) + "\\n", encoding="utf-8")

    starter_manifest_payload = {
        "manifest_version": "1",
        "patch_name": "starter_patch",
        "active_profile": profile_name,
        "target_project_root": target_root,
        "intent": starter_intent,
        "notes": [
            "Starter manifest stub generated by bootstrap-target.",
            "Fill in files_to_write and commands as appropriate for the target.",
        ],
    }
    starter_manifest_path.write_text(json.dumps(starter_manifest_payload, indent=2), encoding="utf-8")

    return bootstrap_payload
"""

def patch_cli(cli_text: str) -> str:
    cli_text = cli_text.replace('\n        import json\n', '\n')
    if 'bootstrap-target' not in cli_text.split('def main', 1)[0]:
        marker = '\n    return parser\n'
        if marker not in cli_text:
            raise SystemExit('Could not find build_parser return marker in cli.py.')
        cli_text = cli_text.replace(marker, '\n' + BOOTSTRAP_PARSER_BLOCK + '    return parser\n', 1)
    else:
        if '--starter-intent' not in cli_text:
            import re
            m = re.search(r'^\s*(\w+)\s*=\s*subparsers\.add_parser\(\s*"bootstrap-target"', cli_text, flags=re.M)
            if not m:
                raise SystemExit('Could not identify bootstrap-target parser variable in cli.py.')
            var_name = m.group(1)
            insertion = (
                f'    {var_name}.add_argument(\n'
                f'        "--starter-intent",\n'
                f'        default="documentation_patch",\n'
                f'        help="Starter manifest intent for the onboarding bundle.",\n'
                f'    )\n'
            )
            marker = '\n    return parser\n'
            if marker not in cli_text:
                raise SystemExit('Could not find build_parser return marker in cli.py.')
            cli_text = cli_text.replace(marker, '\n' + insertion + '    return parser\n', 1)

    main_marker = '    if args.command == "refresh-project-doc":'
    end_marker = '\nif __name__ == "__main__":'
    if main_marker not in cli_text or end_marker not in cli_text:
        raise SystemExit('Could not find refresh-project-doc/main tail markers in cli.py.')
    prefix = cli_text.split(main_marker, 1)[0]
    suffix = cli_text.split(end_marker, 1)[1]
    cli_text = prefix + MAIN_TAIL + suffix
    return cli_text

def patch_project_packets(text: str) -> str:
    import re

    text = text.replace('runtime_override=runtime_override,', 'runtime_path=runtime_override,')
    text = text.replace('runtime_path=runtime_override,', 'runtime_path=runtime_override,', 1)
    text = text.replace('runtime_path=runtime_override,\n        )\n\n    onboarding_root', 'runtime_path=runtime_override,\n    )\n\n    onboarding_root')
    text = text.replace('runtime_path=runtime_override,', 'runtime_path=runtime_override,')
    text = text.replace('runtime_path=runtime_override,', 'runtime_path=runtime_override,')
    text = text.replace('runtime_path=runtime_override,', 'runtime_path=runtime_override,')
    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')
    text = text.replace('runtime_path=runtime_override,\n        )\n\n    onboarding_root = default_onboarding_root(wrapper_root)', 'runtime_path=runtime_override,\n    )\n\n    onboarding_root = default_onboarding_root(wrapper_root)')

    text = text.replace('runtime_path=runtime_override,', 'runtime_path=runtime_override,')
    text = text.replace('runtime_path=runtime_override,\n        )\n\n    onboarding_root = default_onboarding_root(wrapper_root)', 'runtime_path=runtime_override,\n    )\n\n    onboarding_root = default_onboarding_root(wrapper_root)')
    text = text.replace('runtime_path=runtime_override,\n        )\n\n    onboarding_root = default_onboarding_root(wrapper_root)', 'runtime_path=runtime_override,\n    )\n\n    onboarding_root = default_onboarding_root(wrapper_root)')

    text = text.replace('runtime_path=runtime_override,\n        )\n\n    onboarding_root = default_onboarding_root(wrapper_root)', 'runtime_path=runtime_override,\n    )\n\n    onboarding_root = default_onboarding_root(wrapper_root)')
    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')
    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')
    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')
    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')

    text = text.replace('runtime_path=runtime_override,', 'runtime_path=runtime_override,')
    text = text.replace('runtime_override=runtime_override,', 'runtime_path=runtime_override,')
    text = text.replace('runtime_path=runtime_override,', 'runtime_path=runtime_override,')

    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')
    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')

    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')
    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')

    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')
    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')

    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')

    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')

    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')

    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')

    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')

    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')

    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')
    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')
    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')

    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')
    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')
    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')
    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')

    text = text.replace('runtime_path=runtime_override,\n        )', 'runtime_path=runtime_override,\n    )')

    # Remove any bad runtime kwarg passed into bootstrap markdown builder.
    text = text.replace('            runtime_path=runtime_override,\n', '')
    text = text.replace('            runtime_override=runtime_override,\n', '')

    pattern = r'\ndef bootstrap_target_onboarding\([\s\S]*?(?=\n(?:def |if __name__|class ))'
    replacement = '\n' + BOOTSTRAP_FUNCTION + '\n'
    if re.search(pattern, text):
        text = re.sub(pattern, replacement, text, count=1)
    else:
        text = text.rstrip() + '\n\n' + BOOTSTRAP_FUNCTION + '\n'

    return text

def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    cli_path = root / "patchops" / "cli.py"
    packets_path = root / "patchops" / "project_packets.py"
    test_path = root / "tests" / "test_project_packet_onboarding_bootstrap.py"

    cli_text = cli_path.read_text(encoding="utf-8")
    packets_text = packets_path.read_text(encoding="utf-8")

    cli_text = patch_cli(cli_text)
    packets_text = patch_project_packets(packets_text)

    cli_path.write_text(cli_text, encoding="utf-8")
    packets_path.write_text(packets_text, encoding="utf-8")
    test_path.write_text(TEST_FILE, encoding="utf-8")

    print(json.dumps({
        "written_files": [
            str(cli_path),
            str(packets_path),
            str(test_path),
        ]
    }, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())