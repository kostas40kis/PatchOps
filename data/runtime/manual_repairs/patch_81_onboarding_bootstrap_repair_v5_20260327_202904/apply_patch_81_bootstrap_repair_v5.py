from __future__ import annotations

import argparse
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

BOOTSTRAP_PARSER_BLOCK = '''
    bootstrap_target_parser = subparsers.add_parser(
        "bootstrap-target",
        help="Generate onboarding bootstrap artifacts for a target project",
    )
    bootstrap_target_parser.description = (
        "Generate onboarding artifacts parallel to handoff for a new target project."
    )
    bootstrap_target_parser.add_argument("--project-name", required=True, help="Human-readable project name")
    bootstrap_target_parser.add_argument("--target-root", required=True, help="Target project root")
    bootstrap_target_parser.add_argument("--profile", required=True, help="PatchOps profile to anchor the onboarding bundle")
    bootstrap_target_parser.add_argument("--runtime-path", default=None, help="Optional explicit runtime override")
    bootstrap_target_parser.add_argument("--starter-intent", default="documentation_patch", help="Starter manifest intent")
    bootstrap_target_parser.add_argument(
        "--initial-goal",
        action="append",
        default=[],
        help="Optional initial goal line; may be supplied more than once.",
    )
    bootstrap_target_parser.add_argument("--wrapper-root", help="Override wrapper project root", default=None)
'''

BOOTSTRAP_BRANCH = '''
    if args.command == "bootstrap-target":
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
'''


def ensure_bootstrap_parser(cli_text: str) -> str:
    cli_text = cli_text.replace('if command == "bootstrap-target":', 'if args.command == "bootstrap-target":')

    if '"bootstrap-target"' not in cli_text:
        marker = "\n\n    return parser\n"
        if marker not in cli_text:
            raise RuntimeError("Could not find parser return anchor in cli.py.")
        cli_text = cli_text.replace(marker, "\n" + BOOTSTRAP_PARSER_BLOCK + "\n    return parser\n")
        return cli_text

    if '--starter-intent' not in cli_text:
        pattern = re.compile(
            r'(?P<head>\n\s*\w+\s*=\s*subparsers\.add_parser\(\s*"bootstrap-target".*?\)\n)(?P<body>.*?)(?=\n\s*\w+\s*=\s*subparsers\.add_parser\(|\n\s*return parser\n)',
            re.DOTALL,
        )
        match = pattern.search(cli_text)
        if not match:
            raise RuntimeError("Could not locate bootstrap-target parser block in cli.py.")
        body = match.group('body')
        runtime_line = re.search(r'.*--runtime-path.*\n', body)
        if runtime_line:
            insert_at = runtime_line.end()
            body = body[:insert_at] + '    bootstrap_target_parser.add_argument("--starter-intent", default="documentation_patch", help="Starter manifest intent")\n' + body[insert_at:]
        else:
            body += '    bootstrap_target_parser.add_argument("--starter-intent", default="documentation_patch", help="Starter manifest intent")\n'
        cli_text = cli_text[:match.start()] + match.group('head') + body + cli_text[match.end():]
    return cli_text


def ensure_bootstrap_branch(cli_text: str) -> str:
    cli_text = cli_text.replace('if command == "bootstrap-target":', 'if args.command == "bootstrap-target":')

    if '\n        import json\n' in cli_text:
        cli_text = cli_text.replace('\n        import json\n', '\n')

    if 'if args.command == "bootstrap-target":' in cli_text:
        block_pattern = re.compile(
            r'\n\s*if args\.command == "bootstrap-target":\n.*?(?=\n\s*if args\.command == |\n\s*parser\.error\(|\n\s*raise SystemExit|\Z)',
            re.DOTALL,
        )
        match = block_pattern.search(cli_text)
        if not match:
            raise RuntimeError("Could not locate bootstrap-target command block in cli.py.")
        return cli_text[:match.start()] + "\n" + BOOTSTRAP_BRANCH + cli_text[match.end():]

    anchor = '\n    parser.error("Unknown command")\n'
    if anchor not in cli_text:
        anchor = '\n    raise SystemExit(f"Unknown command: {args.command}")\n'
    if anchor not in cli_text:
        raise RuntimeError("Could not find command fallback anchor in cli.py.")
    return cli_text.replace(anchor, "\n" + BOOTSTRAP_BRANCH + anchor, 1)


def repair_project_packets(text: str) -> str:
    scaffold_call_pattern = re.compile(
        r'(packet_payload = scaffold_project_packet\(\n(?:.*\n)*?\s*initial_goals=initial_goals,\n)(?P<bad>\s*runtime_override=runtime_override,\n)',
        re.DOTALL,
    )
    text = scaffold_call_pattern.sub(r'\1        runtime_path=runtime_override,\n', text)

    builder_call_pattern = re.compile(
        r'(_build_current_target_bootstrap_markdown\(\n(?:.*\n)*?\s*starter_intent=starter_intent,\n)(?P<bad>\s*runtime_path=runtime_override,\n)',
        re.DOTALL,
    )
    text = builder_call_pattern.sub(r'\1    runtime_override=runtime_override,\n', text)

    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    cli_path = root / "patchops" / "cli.py"
    packets_path = root / "patchops" / "project_packets.py"
    test_path = root / "tests" / "test_project_packet_onboarding_bootstrap.py"

    cli_text = cli_path.read_text(encoding="utf-8")
    cli_text = ensure_bootstrap_parser(cli_text)
    cli_text = ensure_bootstrap_branch(cli_text)
    cli_path.write_text(cli_text, encoding="utf-8")

    packets_text = packets_path.read_text(encoding="utf-8")
    packets_text = repair_project_packets(packets_text)
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