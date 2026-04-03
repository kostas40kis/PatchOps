from pathlib import Path
import sys

project_root = Path(sys.argv[1]).resolve()
output_path = Path(sys.argv[2]).resolve()

source_path = project_root / "patchops" / "cli.py"
text = source_path.read_text(encoding="utf-8")

if 'if args.command == "export-handoff":' not in text:
    parser_insert = '''
    export_handoff_parser = subparsers.add_parser(
        "export-handoff",
        help="Generate the current handoff bundle from a canonical report",
    )
    export_handoff_parser.description = (
        "Generate current_handoff files, latest report artifacts, and a compact handoff bundle directory."
    )
    export_handoff_parser.add_argument(
        "--report-path",
        default=None,
        help="Optional path to the latest canonical PatchOps report.",
    )
    export_handoff_parser.add_argument(
        "--wrapper-root",
        help="Override wrapper project root",
        default=None,
    )
    export_handoff_parser.add_argument(
        "--current-stage",
        default="Stage 2 in progress",
        help="Stage label to write into the exported handoff files.",
    )
    export_handoff_parser.add_argument(
        "--bundle-name",
        default="current",
        help="Bundle directory name under handoff/bundle.",
    )
'''

    return_anchor = '\n    return parser\n'
    if return_anchor not in text:
        raise SystemExit("Could not find parser return anchor in patchops/cli.py")
    text = text.replace(return_anchor, parser_insert + return_anchor, 1)

    handler_insert = '''
    if args.command == "export-handoff":
        from patchops.handoff import export_handoff_bundle

        payload = export_handoff_bundle(
            report_path=args.report_path,
            wrapper_project_root=args.wrapper_root,
            current_stage=args.current_stage,
            bundle_name=args.bundle_name,
        )
        print(json.dumps(payload, indent=2))
        return 0

'''
    inspect_anchor = '\n    if args.command == "inspect":\n'
    if inspect_anchor not in text:
        raise SystemExit("Could not find inspect handler anchor in patchops/cli.py")
    text = text.replace(inspect_anchor, '\n' + handler_insert + '    if args.command == "inspect":\n', 1)

output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(text, encoding="utf-8")
print(str(output_path))