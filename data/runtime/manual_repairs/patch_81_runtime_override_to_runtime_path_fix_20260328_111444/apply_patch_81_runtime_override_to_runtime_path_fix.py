from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    project_packets = root / "patchops" / "project_packets.py"

    text = project_packets.read_text(encoding="utf-8")

    old = "runtime_override=runtime_override,"
    new = "runtime_path=runtime_override,"

    occurrences = text.count(old)
    if occurrences != 1:
        raise SystemExit(
            "Expected exactly one occurrence of {!r} in {} but found {}.".format(
                old, project_packets, occurrences
            )
        )

    updated = text.replace(old, new, 1)
    project_packets.write_text(updated, encoding="utf-8")

    print(
        json.dumps(
            {
                "written_files": [str(project_packets)],
                "replacements": [{"old": old, "new": new}],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())