from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    cli_path = root / "patchops" / "cli.py"

    text = cli_path.read_text(encoding="utf-8")

    bad = 'if command == "bootstrap-target":'
    good = 'if args.command == "bootstrap-target":'

    if bad not in text:
        raise SystemExit("Expected bootstrap-target NameError branch not found in cli.py")

    text = text.replace(bad, good, 1)
    cli_path.write_text(text, encoding="utf-8")

    print(json.dumps({"written_files": [str(cli_path)]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())