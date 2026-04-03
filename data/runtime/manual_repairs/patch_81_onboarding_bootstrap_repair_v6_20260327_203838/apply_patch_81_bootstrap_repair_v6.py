from __future__ import annotations

import argparse
import json
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

    onboarding_root = Path(payload["onboarding_root"])
    assert payload["project_name"] == "OSM Remediation"
    assert payload["starter_intent"] == "documentation_patch"
    assert (onboarding_root / "current_target_bootstrap.md").exists()
    assert (onboarding_root / "current_target_bootstrap.json").exists()
    assert (onboarding_root / "next_prompt.txt").exists()
    assert (onboarding_root / "starter_manifest.json").exists()

    bootstrap_json = json.loads((onboarding_root / "current_target_bootstrap.json").read_text(encoding="utf-8"))
    assert bootstrap_json["project_name"] == "OSM Remediation"
    assert bootstrap_json["starter_intent"] == "documentation_patch"
    assert bootstrap_json["starter_manifest_path"].endswith("starter_manifest.json")


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
    out = capsys.readouterr().out
    payload = json.loads(out)
    onboarding_root = Path(payload["onboarding_root"])
    assert payload["project_name"] == "Wrapper Self Hosted"
    assert payload["starter_intent"] == "documentation_patch"
    assert (onboarding_root / "current_target_bootstrap.md").exists()
    assert (onboarding_root / "current_target_bootstrap.json").exists()
    assert (onboarding_root / "next_prompt.txt").exists()
    assert (onboarding_root / "starter_manifest.json").exists()
"""

BOOTSTRAP_PARSER_BLOCK = """
    bootstrap_target_parser = subparsers.add_parser(
        \"bootstrap-target\",
        help=\"Generate onboarding bootstrap artifacts for a target project\",
    )
    bootstrap_target_parser.description = (
        \"Generate onboarding artifacts parallel to handoff for a new target project.\"
    )
    bootstrap_target_parser.add_argument(\"--project-name\", required=True, help=\"Human-readable project name\")
    bootstrap_target_parser.add_argument(\"--target-root\", required=True, help=\"Target project root\")
    bootstrap_target_parser.add_argument(\"--profile\", required=True, help=\"PatchOps profile to anchor the onboarding bundle\")
    bootstrap_target_parser.add_argument(\"--runtime-path\", default=None, help=\"Optional explicit runtime override\")
    bootstrap_target_parser.add_argument(\"--starter-intent\", default=\"documentation_patch\", help=\"Starter manifest intent\")
    bootstrap_target_parser.add_argument(
        \"--initial-goal\",
        action=\"append\",
        default=[],
        help=\"Optional initial goal line; may be supplied more than once.\",
    )
    bootstrap_target_parser.add_argument(\"--wrapper-root\", help=\"Override wrapper project root\", default=None)
""".strip("\n")

BOOTSTRAP_BRANCH = """
    if args.command == \"bootstrap-target\":
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
""".strip("\n")


def _replace_or_insert_bootstrap_parser(text: str) -> str:
    if 'bootstrap-target' not in text:
        anchor = '\n\n    return parser\n'
        if anchor not in text:
            raise RuntimeError('Could not find parser return anchor in cli.py.')
        return text.replace(anchor, '\n\n' + BOOTSTRAP_PARSER_BLOCK + '\n\n    return parser\n', 1)

    if '--starter-intent' in text:
        return text

    for needle in (
        'bootstrap_target_parser.add_argument("--runtime-path", default=None, help="Optional explicit runtime override")\n',
        "bootstrap_target_parser.add_argument('--runtime-path', default=None, help='Optional explicit runtime override')\n",
    ):
        if needle in text:
            insertion = '    bootstrap_target_parser.add_argument("--starter-intent", default="documentation_patch", help="Starter manifest intent")\n'
            return text.replace(needle, needle + insertion, 1)

    for needle in (
        'bootstrap_target_parser.add_argument("--wrapper-root", help="Override wrapper project root", default=None)\n',
        "bootstrap_target_parser.add_argument('--wrapper-root', help='Override wrapper project root', default=None)\n",
    ):
        if needle in text:
            insertion = '    bootstrap_target_parser.add_argument("--starter-intent", default="documentation_patch", help="Starter manifest intent")\n'
            return text.replace(needle, insertion + needle, 1)

    raise RuntimeError('bootstrap-target parser exists but starter-intent could not be inserted safely.')


def _replace_or_insert_bootstrap_branch(text: str) -> str:
    text = text.replace('if command == "bootstrap-target":', 'if args.command == "bootstrap-target":')
    text = text.replace('\n        import json\n', '\n')

    start_marker = 'if args.command == "bootstrap-target":'
    start = text.find(start_marker)
    if start != -1:
        next_if = text.find('\n    if args.command == "', start + len(start_marker))
        next_fallback = text.find('\n    parser.error(', start + len(start_marker))
        next_raise = text.find('\n    raise SystemExit', start + len(start_marker))
        candidates = [pos for pos in (next_if, next_fallback, next_raise) if pos != -1]
        end = min(candidates) if candidates else len(text)
        return text[:start] + BOOTSTRAP_BRANCH + text[end:]

    anchor = '\n    parser.error("Unknown command")\n'
    if anchor not in text:
        anchor = '\n    raise SystemExit(f"Unknown command: {args.command}")\n'
    if anchor not in text:
        raise RuntimeError('Could not find command fallback anchor in cli.py.')
    return text.replace(anchor, '\n' + BOOTSTRAP_BRANCH + '\n\n' + anchor.lstrip('\n'), 1)


def _patch_bootstrap_target_onboarding(block: str) -> str:
    lines = block.splitlines(True)
    out: list[str] = []
    in_scaffold = False
    in_builder = False

    for line in lines:
        if 'packet_payload = scaffold_project_packet(' in line:
            in_scaffold = True
        if 'md_text = _build_current_target_bootstrap_markdown(' in line:
            in_builder = True

        if in_scaffold and 'runtime_override=runtime_override' in line:
            line = line.replace('runtime_override=runtime_override', 'runtime_path=runtime_override')

        if in_builder and ('runtime_path=runtime_override' in line or 'runtime_override=runtime_override' in line):
            continue

        out.append(line)

        if in_scaffold and line.strip() == ')':
            in_scaffold = False
        if in_builder and line.strip() == ')':
            in_builder = False

    return ''.join(out)


def _repair_project_packets(text: str) -> str:
    marker = 'def bootstrap_target_onboarding('
    start = text.find(marker)
    if start == -1:
        raise RuntimeError('Could not find bootstrap_target_onboarding in project_packets.py.')
    next_def = text.find('\ndef ', start + len(marker))
    if next_def == -1:
        next_def = len(text)
    block = text[start:next_def]
    repaired = _patch_bootstrap_target_onboarding(block)
    return text[:start] + repaired + text[next_def:]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--project-root', required=True)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    cli_path = root / 'patchops' / 'cli.py'
    packets_path = root / 'patchops' / 'project_packets.py'
    test_path = root / 'tests' / 'test_project_packet_onboarding_bootstrap.py'

    cli_text = cli_path.read_text(encoding='utf-8')
    cli_text = _replace_or_insert_bootstrap_parser(cli_text)
    cli_text = _replace_or_insert_bootstrap_branch(cli_text)
    cli_path.write_text(cli_text, encoding='utf-8')

    packets_text = packets_path.read_text(encoding='utf-8')
    packets_text = _repair_project_packets(packets_text)
    packets_path.write_text(packets_text, encoding='utf-8')

    test_path.write_text(TEST_FILE, encoding='utf-8')

    print(json.dumps({
        'written_files': [
            str(cli_path),
            str(packets_path),
            str(test_path),
        ]
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())