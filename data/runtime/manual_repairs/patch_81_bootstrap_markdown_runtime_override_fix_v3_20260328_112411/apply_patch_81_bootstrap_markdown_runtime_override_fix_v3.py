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

    lines = project_packets.read_text(encoding="utf-8").splitlines()

    start = None
    end = None
    for idx, line in enumerate(lines):
        if "md_text = _build_current_target_bootstrap_markdown(" in line:
            start = idx
            break

    if start is None:
        raise SystemExit(f"Bootstrap markdown builder call not found in {project_packets}.")

    for idx in range(start + 1, len(lines)):
        if lines[idx].strip() == ")":
            end = idx
            break

    if end is None:
        raise SystemExit(f"Could not find end of bootstrap markdown builder call in {project_packets}.")

    block = lines[start:end + 1]
    if any("runtime_override=" in line for line in block):
        message = "runtime_override already present in bootstrap markdown builder call."
    else:
        insert_at = None
        for offset, line in enumerate(block):
            if "starter_manifest_path=" in line:
                insert_at = start + offset
                break
        if insert_at is None:
            raise SystemExit(
                f"starter_manifest_path argument not found inside bootstrap markdown builder call in {project_packets}."
            )
        indent = lines[insert_at][: len(lines[insert_at]) - len(lines[insert_at].lstrip())]
        lines.insert(insert_at, indent + "runtime_override=runtime_override,")
        message = "Inserted runtime_override into bootstrap markdown builder call."

    project_packets.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "written_files": [str(project_packets)],
                "message": message,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())