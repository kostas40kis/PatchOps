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

    old = """        md_text = _build_current_target_bootstrap_markdown(
            project_name=project_name,
            target_root=target_root,
            profile_name=profile_name,
            packet_path=packet_path,
            generic_docs=generic_docs,
            initial_goals=initial_goals,
            starter_manifest_path=str(starter_manifest_path.resolve()),
            starter_intent=starter_intent,
        )"""

    new = """        md_text = _build_current_target_bootstrap_markdown(
            project_name=project_name,
            target_root=target_root,
            profile_name=profile_name,
            packet_path=packet_path,
            generic_docs=generic_docs,
            initial_goals=initial_goals,
            runtime_override=runtime_override,
            starter_manifest_path=str(starter_manifest_path.resolve()),
            starter_intent=starter_intent,
        )"""

    if old not in text:
        raise SystemExit(f"Expected bootstrap markdown call block not found in {project_packets}.")

    text = text.replace(old, new, 1)
    project_packets.write_text(text, encoding="utf-8")

    print(
        json.dumps(
            {
                "written_files": [str(project_packets)],
                "message": "Added runtime_override to bootstrap markdown builder call.",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())