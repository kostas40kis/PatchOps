from __future__ import annotations

import json
import re
from pathlib import Path

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

    onboarding_root = tmp_path / "onboarding"

    assert payload["written"] is True
    assert payload["project_name"] == "OSM Remediation"
    assert payload["starter_intent"] == "documentation_patch"
    assert payload["onboarding_root"] == str(onboarding_root.resolve())
    assert (onboarding_root / "current_target_bootstrap.md").exists()
    assert (onboarding_root / "current_target_bootstrap.json").exists()
    assert (onboarding_root / "next_prompt.txt").exists()
    assert (onboarding_root / "starter_manifest.json").exists()

    json_payload = json.loads((onboarding_root / "current_target_bootstrap.json").read_text(encoding="utf-8"))
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
    onboarding_root = Path(payload["onboarding_root"])
    assert onboarding_root.exists()
    assert payload["starter_intent"] == "documentation_patch"
    assert (onboarding_root / "starter_manifest.json").exists()
"""

BOOTSTRAP_FUNCTION = """def bootstrap_target_onboarding(
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

    bootstrap_payload = {
        "written": True,
        "project_name": project_name,
        "project_slug": _packet_slug(project_name),
        "profile_name": profile_name,
        "target_root": target_root,
        "packet_path": str(Path(packet_path).resolve()),
        "onboarding_root": str(onboarding_root.resolve()),
        "bootstrap_markdown_path": str(current_target_bootstrap_md.resolve()),
        "bootstrap_json_path": str(current_target_bootstrap_json.resolve()),
        "next_prompt_path": str(next_prompt_path.resolve()),
        "starter_manifest_path": str(starter_manifest_path.resolve()),
        "starter_intent": starter_intent,
        "initial_goal_count": len(initial_goals),
        "generic_doc_count": len(generic_docs),
    }
    if runtime_override is not None:
        bootstrap_payload["runtime_path"] = runtime_override

    current_target_bootstrap_md.write_text(md_text + "\\n", encoding="utf-8")
    current_target_bootstrap_json.write_text(json.dumps(bootstrap_payload, indent=2) + "\\n", encoding="utf-8")
    next_prompt_path.write_text(_build_current_target_next_prompt(bootstrap_payload), encoding="utf-8")
    starter_manifest_path.write_text(
        json.dumps(
            _build_starter_manifest_payload(
                project_name=project_name,
                project_slug=_packet_slug(project_name),
                target_root=target_root,
                profile_name=profile_name,
                starter_intent=starter_intent,
            ),
            indent=2,
        ) + "\\n",
        encoding="utf-8",
    )
    return bootstrap_payload
"""

BOOTSTRAP_PARSER_BLOCK = """    bootstrap_target_parser = subparsers.add_parser(
        "bootstrap-target",
        help="Generate onboarding bootstrap artifacts for a target project.",
    )
    bootstrap_target_parser.description = (
        "Generate onboarding bootstrap artifacts parallel to handoff for a new target project."
    )
    bootstrap_target_parser.add_argument("--project-name", required=True, help="Human-readable project name")
    bootstrap_target_parser.add_argument("--target-root", required=True, help="Target project root")
    bootstrap_target_parser.add_argument("--profile", required=True, help="PatchOps profile to anchor the bootstrap")
    bootstrap_target_parser.add_argument("--wrapper-root", help="Override wrapper project root", default=None)
    bootstrap_target_parser.add_argument("--runtime-path", default=None, help="Optional explicit runtime override")
    bootstrap_target_parser.add_argument(
        "--starter-intent",
        default="documentation_patch",
        help="Starter manifest intent label for the generated onboarding bundle.",
    )
    bootstrap_target_parser.add_argument(
        "--initial-goal",
        action="append",
        default=[],
        help="Optional initial goal line; may be supplied more than once.",
    )
"""

BOOTSTRAP_MAIN_BLOCK = """    if args.command == "bootstrap-target":
        from patchops.project_packets import bootstrap_target_onboarding

        payload = bootstrap_target_onboarding(
            project_name=args.project_name,
            target_root=args.target_root,
            profile_name=args.profile,
            wrapper_project_root=args.wrapper_root,
            initial_goals=args.initial_goal,
            runtime_override=args.runtime_path,
            starter_intent=args.starter_intent,
        )
        print(json.dumps(payload, indent=2))
        return 0
"""

def restore_if_present(root: Path, active: Path, relative_backup: str) -> bool:
    restore_source = root / relative_backup
    if restore_source.exists():
        active.write_text(restore_source.read_text(encoding="utf-8"), encoding="utf-8")
        return True
    return False

def replace_bootstrap_function(text: str) -> str:
    pattern = r"def bootstrap_target_onboarding\((?:.|\n)*?\n(?=def |\Z)"
    if re.search(pattern, text):
        return re.sub(pattern, BOOTSTRAP_FUNCTION.strip() + "\n\n", text, count=1)
    return text.rstrip() + "\n\n" + BOOTSTRAP_FUNCTION.strip() + "\n"

def ensure_bootstrap_parser(text: str) -> str:
    if '"bootstrap-target"' not in text:
        marker = "\n\n    return parser\n"
        if marker not in text:
            raise SystemExit("Could not find return parser marker in cli.py.")
        return text.replace(marker, "\n" + BOOTSTRAP_PARSER_BLOCK + "\n    return parser\n", 1)

    if '--starter-intent' not in text:
        anchor = 'bootstrap_target_parser.add_argument("--runtime-path", default=None, help="Optional explicit runtime override")'
        if anchor in text:
            text = text.replace(
                anchor,
                anchor + '\n' + '    bootstrap_target_parser.add_argument(\n        "--starter-intent",\n        default="documentation_patch",\n        help="Starter manifest intent label for the generated onboarding bundle.",\n    )',
                1,
            )
        else:
            text = re.sub(r"\n\s*return parser\s*$", "\n    bootstrap_target_parser.add_argument(\n        \"--starter-intent\",\n        default=\"documentation_patch\",\n        help=\"Starter manifest intent label for the generated onboarding bundle.\",\n    )\n\n    return parser\n", text, count=1)
    return text

def ensure_bootstrap_main(text: str) -> str:
    text = text.replace('if command == "bootstrap-target":', 'if args.command == "bootstrap-target":')
    if 'if args.command == "bootstrap-target":' not in text:
        fallback = '\n    parser.error("Unknown command")\n'
        if fallback not in text:
            raise SystemExit('Could not find fallback parser.error in cli.py.')
        text = text.replace(fallback, "\n" + BOOTSTRAP_MAIN_BLOCK + "\n    parser.error(\"Unknown command\")\n", 1)
        return text

    pattern = r'if args\.command == "bootstrap-target":(?:.|\n)*?(?=\n    if args\.command == |\n    parser\.error\("Unknown command"\))'
    return re.sub(pattern, BOOTSTRAP_MAIN_BLOCK + "\n", text, count=1)

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    cli_path = root / "patchops" / "cli.py"
    packets_path = root / "patchops" / "project_packets.py"
    test_path = root / "tests" / "test_project_packet_onboarding_bootstrap.py"

    restored = {
        "cli_restored": restore_if_present(root, cli_path, r"data\runtime\manual_repairs\patch_81_onboarding_bootstrap_repair_20260327_200939\cli.py"),
        "project_packets_restored": restore_if_present(root, packets_path, r"data\runtime\manual_repairs\patch_81_onboarding_bootstrap_repair_20260327_200939\project_packets.py"),
        "test_restored": restore_if_present(root, test_path, r"data\runtime\manual_repairs\patch_81_onboarding_bootstrap_repair_20260327_200939\test_project_packet_onboarding_bootstrap.py"),
    }

    cli_text = cli_path.read_text(encoding="utf-8")
    cli_text = cli_text.replace("\n        import json\n", "\n")
    cli_text = ensure_bootstrap_parser(cli_text)
    cli_text = ensure_bootstrap_main(cli_text)
    cli_path.write_text(cli_text, encoding="utf-8")

    packets_text = packets_path.read_text(encoding="utf-8")
    packets_text = replace_bootstrap_function(packets_text)
    packets_path.write_text(packets_text, encoding="utf-8")

    test_path.write_text(TEST_FILE, encoding="utf-8")

    print(json.dumps({
        "written_files": [str(cli_path), str(packets_path), str(test_path)],
        "restored_from_known_good_backup": restored,
    }, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())