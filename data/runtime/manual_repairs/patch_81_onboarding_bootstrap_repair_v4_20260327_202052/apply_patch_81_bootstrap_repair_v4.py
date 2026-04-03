from __future__ import annotations

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
    assert payload["written"] is True
    assert payload["starter_intent"] == "documentation_patch"
    assert (onboarding_root / "current_target_bootstrap.md").exists()
    assert (onboarding_root / "current_target_bootstrap.json").exists()
    assert (onboarding_root / "next_prompt.txt").exists()
    assert (onboarding_root / "starter_manifest.json").exists()

    bootstrap_json = json.loads((onboarding_root / "current_target_bootstrap.json").read_text(encoding="utf-8"))
    assert bootstrap_json["project_name"] == "OSM Remediation"
    assert bootstrap_json["starter_intent"] == "documentation_patch"


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
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    onboarding_root = Path(payload["onboarding_root"])

    assert payload["project_name"] == "Wrapper Self Hosted"
    assert payload["starter_intent"] == "documentation_patch"
    assert (onboarding_root / "current_target_bootstrap.md").exists()
    assert (onboarding_root / "current_target_bootstrap.json").exists()
    assert (onboarding_root / "next_prompt.txt").exists()
    assert (onboarding_root / "starter_manifest.json").exists()
"""

def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)

def patch_project_packets(text: str) -> str:
    original = text
    text = text.replace("runtime_path=runtime_override,", "runtime_override=runtime_override,")
    text = text.replace("runtime_path=runtime_override,", "runtime_override=runtime_override,")
    # If the bootstrap markdown builder signature uses runtime_override, the line above is enough.
    # If it already uses runtime_override, this is a no-op.
    ensure(text != original or "runtime_override=runtime_override," in text, "Could not align runtime_override keyword in project_packets.py.")
    return text

def insert_after_last_argument(block: str, insertion: str) -> str:
    lines = block.splitlines()
    if any("--starter-intent" in line for line in lines):
        return block
    insert_at = None
    for idx, line in enumerate(lines):
        if ".add_argument(" in line:
            insert_at = idx + 1
    if insert_at is None:
        raise SystemExit("Could not find bootstrap-target parser arguments in cli.py.")
    lines.insert(insert_at, insertion)
    return "\n".join(lines)

def patch_cli(text: str) -> str:
    original = text

    add_parser_anchor = 'add_parser("bootstrap-target"'
    ensure(add_parser_anchor in text, 'Could not find bootstrap-target parser in cli.py.')

    parser_idx = text.index(add_parser_anchor)
    # locate parser block up to the next blank line followed by "return parser" or the next subparser declaration
    tail = text[parser_idx:]
    end_candidates = []
    for marker in ("\n\n    return parser", '\n    if args.command == "apply":', '\n\ndef _display_value'):
        pos = tail.find(marker)
        if pos != -1:
            end_candidates.append(parser_idx + pos)
    ensure(end_candidates, "Could not determine end of parser section in cli.py.")
    parser_end = min(end_candidates)
    parser_block = text[parser_idx:parser_end]

    parser_var = None
    for line in parser_block.splitlines():
        if "subparsers.add_parser(" in line and "bootstrap-target" in line:
            parser_var = line.split("=", 1)[0].strip()
            break
    ensure(parser_var, "Could not determine bootstrap-target parser variable name in cli.py.")

    insertion = f'    {parser_var}.add_argument("--starter-intent", default="documentation_patch", help="Starter manifest intent for the onboarding bundle.")'
    new_parser_block = insert_after_last_argument(parser_block, insertion)
    text = text[:parser_idx] + new_parser_block + text[parser_end:]

    if "starter_intent=args.starter_intent" not in text:
        call_anchor = "bootstrap_target_onboarding("
        ensure(call_anchor in text, "Could not find bootstrap_target_onboarding call in cli.py.")
        call_idx = text.index(call_anchor)
        call_tail = text[call_idx:]
        close_idx = call_tail.find("\n        )")
        ensure(close_idx != -1, "Could not determine end of bootstrap_target_onboarding call in cli.py.")
        call_block = call_tail[:close_idx]
        ensure("runtime_override=args.runtime_override," in call_block or "runtime_override=args.runtime_override" in call_block,
               "Could not find runtime_override line in bootstrap_target_onboarding call.")
        call_block = call_block.replace(
            "runtime_override=args.runtime_override,",
            "runtime_override=args.runtime_override,\n                starter_intent=args.starter_intent,",
        )
        call_tail = call_block + call_tail[close_idx:]
        text = text[:call_idx] + call_tail

    ensure(text != original, "cli.py was not modified by Patch 81 repair v4.")
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

    packets_text = patch_project_packets(packets_text)
    cli_text = patch_cli(cli_text)

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