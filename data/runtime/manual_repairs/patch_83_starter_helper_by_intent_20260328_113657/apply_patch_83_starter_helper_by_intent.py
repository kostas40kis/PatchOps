from __future__ import annotations

import json
from pathlib import Path

HELPER_START = "# PATCHOPS_PATCH83_STARTER_HELPER_START"
HELPER_END = "# PATCHOPS_PATCH83_STARTER_HELPER_END"
HELPER_BLOCK = r'''
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
        "code_patch": ["examples/trader_code_patch.json"] if trader else ["examples/generic_python_patch.json"],
        "documentation_patch": ["examples/trader_doc_patch.json"] if trader else ["examples/generic_python_doc_patch.json"],
        "validation_patch": ["examples/trader_verify_patch.json"] if trader else ["examples/generic_python_verify_patch.json"],
        "verify_only": ["examples/trader_verify_patch.json"] if trader else ["examples/generic_python_verify_patch.json"],
        "cleanup_patch": ["examples/generic_python_doc_patch.json"],
        "archive_patch": ["examples/generic_python_doc_patch.json"],
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
'''

TEST_HELPER = '''from __future__ import annotations

from patchops.project_packets import build_starter_manifest_for_intent


def test_build_starter_manifest_for_documentation_patch() -> None:
    payload = build_starter_manifest_for_intent(
        profile_name="generic_python",
        intent="documentation_patch",
        target_root=r"C:\\dev\\demo",
    )
    assert payload["intent"] == "documentation_patch"
    assert payload["starter_examples"] == ["examples/generic_python_doc_patch.json"]
    assert payload["manifest"]["active_profile"] == "generic_python"
    assert payload["manifest"]["target_project_root"] == r"C:\\dev\\demo"
    assert payload["manifest"]["tags"] == ["starter", "documentation_patch"]


def test_build_starter_manifest_for_verify_only_uses_verify_example() -> None:
    payload = build_starter_manifest_for_intent(
        profile_name="trader",
        intent="verify_only",
    )
    assert payload["starter_examples"] == ["examples/trader_verify_patch.json"]
    assert payload["manifest"]["patch_name"] == "starter_verify_only"
    assert payload["manifest"]["target_project_root"] == r"C:\\dev\\trader"
'''

TEST_COMMAND = '''from __future__ import annotations

import json

from patchops.cli import main


def test_starter_command_prints_json(capsys) -> None:
    exit_code = main([
        "starter",
        "--profile",
        "generic_python",
        "--intent",
        "documentation_patch",
        "--target-root",
        r"C:\\dev\\demo",
    ])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["intent"] == "documentation_patch"
    assert payload["manifest"]["active_profile"] == "generic_python"
    assert payload["manifest"]["target_project_root"] == r"C:\\dev\\demo"
    assert payload["starter_examples"] == ["examples/generic_python_doc_patch.json"]
'''


def ensure_helper_block(text: str) -> str:
    if HELPER_START in text and HELPER_END in text:
        prefix = text.split(HELPER_START, 1)[0]
        suffix = text.split(HELPER_END, 1)[1]
        return prefix.rstrip() + '\n\n' + HELPER_BLOCK.strip() + '\n' + suffix.lstrip('\n')
    return text.rstrip() + '\n\n' + HELPER_BLOCK.strip() + '\n'


def ensure_parser(lines: list[str]) -> list[str]:
    parser_line = '    starter_parser = subparsers.add_parser("starter")'
    if any(parser_line in line for line in lines):
        return lines

    insert_at = None
    for idx, line in enumerate(lines):
        if line.strip() == 'return parser':
            insert_at = idx
            break
    if insert_at is None:
        raise SystemExit('Could not find return parser in cli.py build_parser().')

    block = [
        '    starter_parser = subparsers.add_parser("starter")',
        '    starter_parser.add_argument("--profile", required=True)',
        '    starter_parser.add_argument("--intent", required=True)',
        '    starter_parser.add_argument("--target-root")',
        '    starter_parser.add_argument("--patch-name")',
        '    starter_parser.add_argument("--wrapper-root")',
        '',
    ]
    return lines[:insert_at] + block + lines[insert_at:]


def ensure_main_branch(lines: list[str]) -> list[str]:
    if any('if args.command == "starter":' in line for line in lines):
        return lines

    insert_at = None
    for idx, line in enumerate(lines):
        if 'parser.error("Unknown command")' in line:
            insert_at = idx
            break
    if insert_at is None:
        raise SystemExit('Could not find parser.error("Unknown command") in cli.py.')

    block = [
        '    if args.command == "starter":',
        '        from patchops.project_packets import build_starter_manifest_for_intent',
        '',
        '        payload = build_starter_manifest_for_intent(',
        '            profile_name=args.profile,',
        '            intent=args.intent,',
        '            target_root=args.target_root,',
        '            patch_name=args.patch_name,',
        '            wrapper_project_root=args.wrapper_root,',
        '        )',
        '        print(json.dumps(payload, indent=2))',
        '        return 0',
        '',
    ]
    return lines[:insert_at] + block + lines[insert_at:]


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--project-root', required=True)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    project_packets = root / 'patchops' / 'project_packets.py'
    cli = root / 'patchops' / 'cli.py'
    test_helper = root / 'tests' / 'test_project_packet_starter_helper.py'
    test_command = root / 'tests' / 'test_project_packet_starter_command.py'

    packets_text = project_packets.read_text(encoding='utf-8')
    packets_text = ensure_helper_block(packets_text)
    project_packets.write_text(packets_text, encoding='utf-8')

    cli_lines = cli.read_text(encoding='utf-8').splitlines()
    cli_lines = ensure_parser(cli_lines)
    cli_lines = ensure_main_branch(cli_lines)
    cli.write_text('\n'.join(cli_lines) + '\n', encoding='utf-8')

    test_helper.write_text(TEST_HELPER, encoding='utf-8')
    test_command.write_text(TEST_COMMAND, encoding='utf-8')

    print(
        json.dumps(
            {
                'written_files': [
                    str(project_packets),
                    str(cli),
                    str(test_helper),
                    str(test_command),
                ]
            },
            indent=2,
        )
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())