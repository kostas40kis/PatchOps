from __future__ import annotations

import json
from pathlib import Path

PATCH80_WORKFLOW_BLOCK = """<!-- PATCHOPS_PATCH80_SELF_HOSTED_COMMAND_FLOW:START -->
## Self-hosted project-packet command flow

When PatchOps patches itself, treat `docs/projects/wrapper_self_hosted.md` as the target-facing packet for the wrapper repo.

### Recommended self-hosted order

1. Start with the handoff bundle when work is already in progress.
2. Read `docs/projects/wrapper_self_hosted.md` when project-packet context is needed.
3. Use `py -m patchops.cli init-project-doc` only when creating a brand-new packet surface.
4. Use `py -m patchops.cli refresh-project-doc --name wrapper_self_hosted` after validated progress changes the mutable state.
5. Keep PowerShell thin: resolve paths, invoke the CLI, and produce one canonical report.
6. Keep reusable project-packet logic in Python-owned surfaces.

### Self-hosted examples

```text
py -m patchops.cli refresh-project-doc --name wrapper_self_hosted
py -m patchops.cli check <manifest>
py -m patchops.cli inspect <manifest>
py -m patchops.cli plan <manifest>
py -m patchops.cli apply <manifest>
```

Use the smallest correct patch class.
For docs-only self-hosted work, prefer a documentation patch.
If files are already correct and only evidence is needed, prefer a verify-only rerun.
<!-- PATCHOPS_PATCH80_SELF_HOSTED_COMMAND_FLOW:END -->"""

PATCH80_QUICKSTART_BLOCK = """<!-- PATCHOPS_PATCH80_PROJECT_PACKET_COMMANDS:START -->
## Project-packet command quickstart

For project-packet work, keep the flow mechanical:

1. Use `init-project-doc` to scaffold a brand-new packet from explicit inputs.
2. Use `refresh-project-doc` to update mutable packet state after a validated run.
3. Keep `docs/projects/wrapper_self_hosted.md` as the self-hosted reference packet for PatchOps itself.
4. Still produce one canonical report for every run.
5. Treat wrapper/report failures as wrapper-only repairs rather than rewriting target content.

### Command examples

```text
py -m patchops.cli init-project-doc --project-name demo_project --target-root C:\dev\demo --profile generic_python
py -m patchops.cli refresh-project-doc --name wrapper_self_hosted
```
<!-- PATCHOPS_PATCH80_PROJECT_PACKET_COMMANDS:END -->"""

PATCH80_STATUS_BLOCK = """<!-- PATCHOPS_PATCH80_PROJECT_PACKET_STATUS:START -->
## Project-packet rollout status

### Shipped now

- project-packet contract and workflow docs,
- `docs/projects/` as the official packet home,
- `docs/projects/trader.md` as the first maintained target packet,
- `docs/projects/wrapper_self_hosted.md` as the self-hosted packet,
- packet contract tests,
- `init-project-doc` scaffold support,
- `refresh-project-doc` mutable-state refresh support,
- operator guidance for self-hosted project-packet use.

### Still planned

- onboarding bootstrap artifacts,
- profile recommendation helper,
- starter helper by intent,
- final onboarding documentation stop.

### Current interpretation

The project-packet layer is now real and operator-usable.
The remaining work is about making startup even more mechanical, not about redesigning the architecture.
<!-- PATCHOPS_PATCH80_PROJECT_PACKET_STATUS:END -->"""

TEST_FILE = """from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def test_workflow_doc_has_self_hosted_command_flow() -> None:
    text = _read("docs/project_packet_workflow.md")
    assert "PATCHOPS_PATCH80_SELF_HOSTED_COMMAND_FLOW:START" in text
    assert "docs/projects/wrapper_self_hosted.md" in text
    assert "init-project-doc" in text
    assert "refresh-project-doc" in text


def test_operator_quickstart_mentions_project_packet_commands() -> None:
    text = _read("docs/operator_quickstart.md")
    assert "PATCHOPS_PATCH80_PROJECT_PACKET_COMMANDS:START" in text
    assert "init-project-doc" in text
    assert "refresh-project-doc" in text
    assert "one canonical report" in text


def test_project_status_tracks_shipped_and_remaining_packet_work() -> None:
    text = _read("docs/project_status.md")
    assert "PATCHOPS_PATCH80_PROJECT_PACKET_STATUS:START" in text
    assert "wrapper_self_hosted.md" in text
    assert "profile recommendation helper" in text
    assert "starter helper by intent" in text
"""

def replace_or_append(text: str, block: str) -> str:
    start_marker = block.splitlines()[0]
    end_marker = block.splitlines()[-1]
    if start_marker in text and end_marker in text:
        start_index = text.index(start_marker)
        end_index = text.index(end_marker) + len(end_marker)
        prefix = text[:start_index].rstrip()
        suffix = text[end_index:].lstrip("\n")
        pieces: list[str] = []
        if prefix:
            pieces.append(prefix)
        pieces.append(block)
        if suffix:
            pieces.append(suffix)
        return "\n\n".join(pieces) + "\n"
    return text.rstrip() + "\n\n" + block + "\n"

def update_doc(path: Path, block: str) -> None:
    original = path.read_text(encoding="utf-8")
    updated = replace_or_append(original, block)
    path.write_text(updated, encoding="utf-8")

def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()

    workflow_doc = root / "docs" / "project_packet_workflow.md"
    quickstart_doc = root / "docs" / "operator_quickstart.md"
    status_doc = root / "docs" / "project_status.md"
    test_file = root / "tests" / "test_project_packet_doc_stop_c.py"

    update_doc(workflow_doc, PATCH80_WORKFLOW_BLOCK)
    update_doc(quickstart_doc, PATCH80_QUICKSTART_BLOCK)
    update_doc(status_doc, PATCH80_STATUS_BLOCK)
    test_file.write_text(TEST_FILE, encoding="utf-8")

    print(
        json.dumps(
            {
                "written_files": [
                    str(workflow_doc),
                    str(quickstart_doc),
                    str(status_doc),
                    str(test_file),
                ]
            },
            indent=2,
        )
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())