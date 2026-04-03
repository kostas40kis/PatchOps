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

    func_start = None
    func_end = None
    for idx, line in enumerate(lines):
        if line.startswith("def bootstrap_target_onboarding("):
            func_start = idx
            break
    if func_start is None:
        raise SystemExit(f"bootstrap_target_onboarding function not found in {project_packets}.")

    for idx in range(func_start + 1, len(lines)):
        if lines[idx].startswith("def "):
            func_end = idx
            break
    if func_end is None:
        func_end = len(lines)

    block = lines[func_start:func_end]
    block_text = "\n".join(block)
    if '"bootstrap_markdown_path"' in block_text:
        message = "bootstrap payload paths already present."
    else:
        packet_line_index = None
        for offset, line in enumerate(block):
            if '"packet_path"' in line and ':' in line:
                packet_line_index = func_start + offset
                break
        if packet_line_index is None:
            raise SystemExit(
                f'Could not find payload packet_path line inside bootstrap_target_onboarding in {project_packets}.'
            )

        indent = lines[packet_line_index][: len(lines[packet_line_index]) - len(lines[packet_line_index].lstrip())]
        additions = [
            indent + '"bootstrap_markdown_path": str(current_target_bootstrap_md.resolve()),',
            indent + '"bootstrap_json_path": str(current_target_bootstrap_json.resolve()),',
            indent + '"next_prompt_path": str(next_prompt_path.resolve()),',
            indent + '"starter_manifest_path": str(starter_manifest_path.resolve()),',
        ]
        insert_at = packet_line_index + 1
        for item in additions:
            lines.insert(insert_at, item)
            insert_at += 1
        message = "Inserted bootstrap payload path fields into bootstrap_target_onboarding return payload."

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