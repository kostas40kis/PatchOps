from __future__ import annotations

import re
from pathlib import Path


CLI_PATH = Path(r"C:\\dev\\patchops\\patchops\\cli.py")

PARSER_BLOCK = """
    init_project_doc_parser = subparsers.add_parser(
        \"init-project-doc\",
        help=\"Generate a starter project packet under docs/projects/\",
    )
    init_project_doc_parser.description = (
        \"Generate a starter project packet from explicit target inputs without guessing hidden state.\"
    )
    init_project_doc_parser.add_argument(\"--project-name\", required=True, help=\"Human-readable project name\")
    init_project_doc_parser.add_argument(\"--target-root\", required=True, help=\"Target project root for this packet\")
    init_project_doc_parser.add_argument(\"--profile\", required=True, help=\"PatchOps profile to anchor the packet\")
    init_project_doc_parser.add_argument(\"--runtime-path\", default=None, help=\"Optional explicit runtime override\")
    init_project_doc_parser.add_argument(
        \"--initial-goal\",
        action=\"append\",
        default=[],
        help=\"Optional initial goal line; may be supplied more than once.\",
    )
    init_project_doc_parser.add_argument(\"--output-path\", default=None, help=\"Optional explicit markdown output path\")
    init_project_doc_parser.add_argument(\"--wrapper-root\", help=\"Override wrapper project root\", default=None)

"""

HANDLER_BLOCK = """
    if args.command == \"init-project-doc\":
        from patchops.project_packets import scaffold_project_packet

        payload = scaffold_project_packet(
            project_name=args.project_name,
            target_root=args.target_root,
            profile_name=args.profile,
            runtime_path=args.runtime_path,
            wrapper_project_root=args.wrapper_root,
            output_path=args.output_path,
            initial_goals=args.initial_goal,
        )
        print(json.dumps(payload, indent=2))
        return 0

"""


def main() -> None:
    text = CLI_PATH.read_text(encoding="utf-8")

    if '"init-project-doc"' not in text:
        updated = re.sub(r"\n(\s*)return parser", "\n" + PARSER_BLOCK + r"\1return parser", text, count=1)
        if updated == text:
            raise SystemExit("Could not inject init-project-doc parser block into patchops/cli.py")
        text = updated

    if 'if args.command == "init-project-doc":' not in text:
        updated = re.sub(
            r"\n(\s*)parser\.error\(\"Unknown command\"\)\n(\s*)return 2",
            "\n" + HANDLER_BLOCK + r"\1parser.error(\"Unknown command\")\n\2return 2",
            text,
            count=1,
        )
        if updated == text:
            raise SystemExit("Could not inject init-project-doc handler block into patchops/cli.py")
        text = updated

    CLI_PATH.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()