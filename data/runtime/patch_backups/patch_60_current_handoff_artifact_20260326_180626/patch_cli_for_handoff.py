from pathlib import Path
import re
import sys

project_root = Path(sys.argv[1]).resolve()
cli_path = project_root / "patchops" / "cli.py"
text = cli_path.read_text(encoding="utf-8")

import_line = "from patchops.handoff import write_current_handoff\n"
anchor = "from patchops.workflows.wrapper_retry import execute_wrapper_only_retry\n"

if import_line not in text:
    if anchor not in text:
        raise SystemExit("Could not find CLI import anchor for handoff writer.")
    text = text.replace(anchor, anchor + import_line, 1)

patterns = [
    (
        r'(if args\.command == "apply":\s+result = apply_manifest\(args\.manifest, wrapper_project_root=args\.wrapper_root\)\s+_print_run_summary\(result\)\s+)return result\.exit_code',
        r'\1write_current_handoff(result)\n        return result.exit_code',
        "apply handler",
    ),
    (
        r'(if args\.command == "verify":\s+result = verify_only\(args\.manifest, wrapper_project_root=args\.wrapper_root\)\s+_print_run_summary\(result\)\s+)return result\.exit_code',
        r'\1write_current_handoff(result)\n        return result.exit_code',
        "verify handler",
    ),
    (
        r'(if args\.command == "wrapper-retry":\s+result = execute_wrapper_only_retry\([\s\S]*?\)\s+_print_run_summary\(result\)\s+)return result\.exit_code',
        r'\1write_current_handoff(result)\n        return result.exit_code',
        "wrapper-retry handler",
    ),
]

for pattern, replacement, label in patterns:
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit(f"Could not patch {label} in patchops/cli.py")
    text = new_text

cli_path.write_text(text, encoding="utf-8")
print(str(cli_path))