from __future__ import annotations

import json
import re
from pathlib import Path

BOOTSTRAP_PARSER_BLOCK = """
    bootstrap_target_parser = subparsers.add_parser(
        \"bootstrap-target\",
        help=\"Generate onboarding bootstrap artifacts for a brand-new target\",
    )
    bootstrap_target_parser.description = (
        \"Generate onboarding artifacts parallel to handoff for a brand-new target project.\"
    )
    bootstrap_target_parser.add_argument(\"--project-name\", required=True, help=\"Human-readable project name\")
    bootstrap_target_parser.add_argument(\"--target-root\", required=True, help=\"Target project root\")
    bootstrap_target_parser.add_argument(\"--profile\", required=True, help=\"PatchOps profile to anchor the onboarding bundle\")
    bootstrap_target_parser.add_argument(\"--runtime-path\", default=None, help=\"Optional explicit runtime override\")
    bootstrap_target_parser.add_argument(\"--starter-intent\", default=\"documentation_patch\", help=\"Starter manifest intent label\")
    bootstrap_target_parser.add_argument(
        \"--initial-goal\",
        action=\"append\",
        default=[],
        help=\"Optional initial goal line; may be supplied more than once.\",
    )
    bootstrap_target_parser.add_argument(\"--wrapper-root\", help=\"Override wrapper project root\", default=None)
"""

BOOTSTRAP_MAIN_BLOCK = """
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
"""

BOOTSTRAP_TEST = """from __future__ import annotations

import json
from pathlib import Path

from patchops.cli import main
from patchops.project_packets import bootstrap_target_onboarding


def test_bootstrap_target_onboarding_writes_expected_artifacts(tmp_path) -> None:
    payload = bootstrap_target_onboarding(
        project_name=\"OSM Remediation\",
        target_root=r\"C:\\dev\\osm\",
        profile_name=\"generic_python\",
        wrapper_project_root=tmp_path,
        initial_goals=[\"Document the target\", \"Create the first manifest\"],
        starter_intent=\"documentation_patch\",
    )

    onboarding_dir = tmp_path / \"onboarding\"
    assert payload[\"written\"] is True
    assert payload[\"project_name\"] == \"OSM Remediation\"
    assert Path(payload[\"onboarding_dir\"]).resolve() == onboarding_dir.resolve()

    md_path = onboarding_dir / \"current_target_bootstrap.md\"
    json_path = onboarding_dir / \"current_target_bootstrap.json\"
    prompt_path = onboarding_dir / \"next_prompt.txt\"
    starter_path = onboarding_dir / \"starter_manifest.json\"

    assert md_path.exists()
    assert json_path.exists()
    assert prompt_path.exists()
    assert starter_path.exists()

    md_text = md_path.read_text(encoding=\"utf-8\")
    json_payload = json.loads(json_path.read_text(encoding=\"utf-8\"))
    prompt_text = prompt_path.read_text(encoding=\"utf-8\")
    starter_payload = json.loads(starter_path.read_text(encoding=\"utf-8\"))

    assert \"OSM Remediation\" in md_text
    assert json_payload[\"project_name\"] == \"OSM Remediation\"
    assert \"Create the first target packet\" in prompt_text or \"Use the generated onboarding bundle\" in prompt_text
    assert starter_payload[\"active_profile\"] == \"generic_python\"


def test_bootstrap_target_cli_writes_bundle_and_returns_json(capsys, tmp_path) -> None:
    exit_code = main(
        [
            \"bootstrap-target\",
            \"--project-name\",
            \"Wrapper Self Hosted\",
            \"--target-root\",
            r\"C:\\dev\\patchops\",
            \"--profile\",
            \"generic_python\",
            \"--wrapper-root\",
            str(tmp_path),
            \"--starter-intent\",
            \"documentation_patch\",
            \"--initial-goal\",
            \"Create onboarding bundle\",
            \"--initial-goal\",
            \"Create starter manifest stub\",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload[\"project_name\"] == \"Wrapper Self Hosted\"
    assert Path(payload[\"onboarding_dir\"]).exists()
    assert (Path(payload[\"onboarding_dir\"]) / \"current_target_bootstrap.md\").exists()
    assert (Path(payload[\"onboarding_dir\"]) / \"starter_manifest.json\").exists()
"""


def replace_or_insert_before(text: str, marker: str, block: str) -> str:
    if block.strip() in text:
        return text
    if marker not in text:
        raise RuntimeError(f"Marker not found: {marker}")
    return text.replace(marker, block + "\n" + marker, 1)


def remove_local_json_import_in_main(text: str) -> str:
    return re.sub(r"(?m)^\s{8}import json\s*$\n?", "", text)


def ensure_bootstrap_parser(text: str) -> str:
    if '"bootstrap-target"' in text or "'bootstrap-target'" in text:
        return text
    return replace_or_insert_before(text, "\n\n    return parser\n", "\n" + BOOTSTRAP_PARSER_BLOCK.rstrip() + "\n")


def ensure_bootstrap_main(text: str) -> str:
    text = text.replace("if command == \"bootstrap-target\":", "if args.command == \"bootstrap-target\":")
    text = remove_local_json_import_in_main(text)
    if 'if args.command == "bootstrap-target":' in text:
        # Replace an existing malformed block conservatively.
        pattern = re.compile(
            r'\n\s{4}if args\.command == "bootstrap-target":.*?(?=\n\s{4}if args\.command == |\n\s{4}parser\.error\(|\n\s{4}raise |\Z)',
            re.DOTALL,
        )
        if pattern.search(text):
            return pattern.sub("\n" + BOOTSTRAP_MAIN_BLOCK.rstrip() + "\n", text, count=1)
    # No branch found: insert before parser.error / raise unknown command.
    for marker in ['\n    parser.error("Unknown command")\n', "\n    raise SystemExit(parser.error(\"Unknown command\"))\n"]:
        if marker in text:
            return text.replace(marker, "\n" + BOOTSTRAP_MAIN_BLOCK.rstrip() + "\n" + marker.lstrip("\n"), 1)
    raise RuntimeError("Could not place bootstrap-target main block in cli.py")


def patch_project_packets(text: str) -> str:
    updated = text.replace("runtime_override=runtime_override", "runtime_path=runtime_override")
    return updated


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    cli_path = root / "patchops" / "cli.py"
    packets_path = root / "patchops" / "project_packets.py"
    onboarding_test_path = root / "tests" / "test_project_packet_onboarding_bootstrap.py"

    cli_text = cli_path.read_text(encoding="utf-8")
    packets_text = packets_path.read_text(encoding="utf-8")

    cli_text = ensure_bootstrap_parser(cli_text)
    cli_text = ensure_bootstrap_main(cli_text)
    packets_text = patch_project_packets(packets_text)

    cli_path.write_text(cli_text, encoding="utf-8")
    packets_path.write_text(packets_text, encoding="utf-8")
    onboarding_test_path.write_text(BOOTSTRAP_TEST, encoding="utf-8")

    print(json.dumps({
        "written_files": [
            str(cli_path),
            str(packets_path),
            str(onboarding_test_path),
        ]
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())