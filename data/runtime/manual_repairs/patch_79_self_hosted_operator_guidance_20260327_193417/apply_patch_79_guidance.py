from __future__ import annotations

import argparse
import json
from pathlib import Path

WORKFLOW_START = "<!-- PATCH_79_SELF_HOSTED_WORKFLOW_START -->"
WORKFLOW_END = "<!-- PATCH_79_SELF_HOSTED_WORKFLOW_END -->"
QUICKSTART_START = "<!-- PATCH_79_SELF_HOSTED_QUICKSTART_START -->"
QUICKSTART_END = "<!-- PATCH_79_SELF_HOSTED_QUICKSTART_END -->"
STATUS_START = "<!-- PATCH_79_SELF_HOSTED_STATUS_START -->"
STATUS_END = "<!-- PATCH_79_SELF_HOSTED_STATUS_END -->"


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")



def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")



def upsert_block(path: Path, start_marker: str, end_marker: str, body: str) -> None:
    text = read_text(path)
    block = f"{start_marker}\n{body.rstrip()}\n{end_marker}\n"
    if start_marker in text and end_marker in text:
        start = text.index(start_marker)
        end = text.index(end_marker, start) + len(end_marker)
        new_text = text[:start].rstrip() + "\n\n" + block
        if end < len(text):
            tail = text[end:].lstrip("\r\n")
            if tail:
                new_text += "\n" + tail
    else:
        if text and not text.endswith("\n"):
            text += "\n"
        new_text = text.rstrip() + "\n\n" + block if text.strip() else block
    write_text(path, new_text)



def build_workflow_block() -> str:
    return """## Patch 79 - self-hosted operator flow

When PatchOps patches PatchOps itself, keep using the same model that PatchOps applies to other targets.

### Self-hosted read order

1. Read `handoff/current_handoff.md`.
2. Read `handoff/current_handoff.json`.
3. Read `handoff/latest_report_copy.txt`.
4. Read `docs/projects/wrapper_self_hosted.md` for target-level rules.

### Self-hosted operating rules

- Treat `C:\\dev\\patchops` as both the wrapper root and the current target root.
- Keep PowerShell thin. Use it only for path resolution, runtime invocation, one Desktop txt report, and report opening.
- Keep reusable packet logic in Python-owned surfaces such as `patchops/project_packets.py` and `patchops/cli.py`.
- Prefer narrow repair over broad rewrite when the handoff classifies a wrapper-only problem.
- Keep the canonical report as the main evidence artifact.

### Stable command surfaces

Use the CLI rather than custom PowerShell logic for packet operations:

- `py -m patchops.cli init-project-doc`
- `py -m patchops.cli refresh-project-doc`
- `py -m patchops.cli export-handoff`

### Self-hosted continuation rule

When the current work is already running, the handoff bundle is still the first resume surface.
The self-hosted packet exists to explain target-level rules and current project state, not to replace the handoff bundle.
"""



def build_quickstart_block() -> str:
    return r"""## Patch 79 - project-packet operator commands

Use the Python CLI for packet work. Do not duplicate reusable packet logic in PowerShell.

### Create a new target packet

```powershell
py -m patchops.cli init-project-doc --project-name "Wrapper Self Hosted" --target-root C:\dev\patchops --profile generic_python --initial-goal "Keep PowerShell thin" --initial-goal "Use the CLI for packet work"
```

### Refresh a maintained packet after a run

```powershell
py -m patchops.cli refresh-project-doc --name wrapper_self_hosted --wrapper-root C:\dev\patchops
```

### Re-export the handoff bundle after the canonical report exists

```powershell
py -m patchops.cli export-handoff --wrapper-root C:\dev\patchops
```

### Simple operator rule

- project packet = target-level memory surface
- handoff bundle = run-level resume surface
- one canonical report remains required
"""



def build_status_block() -> str:
    return """## Patch 79 - self-hosted operator guidance status

### Current state

- Patch 79 adds self-hosted operator guidance instead of widening the PowerShell layer.
- Project-packet scaffold and refresh commands now have a documented operator flow.
- `docs/projects/wrapper_self_hosted.md` becomes the maintained packet for PatchOps acting as its own current target.

### Why this matters

- operator usage remains simple,
- reusable logic stays in Python,
- self-hosted work now follows the same project-packet model as other targets.

### Next planned step

- Patch 80 should refresh `docs/project_packet_workflow.md`, `docs/operator_quickstart.md`, and `docs/project_status.md` as the formal Documentation Stop P-C once this patch passes.
"""



def build_wrapper_self_hosted_packet() -> str:
    return r"""# Project packet - Wrapper Self Hosted

## 1. Target identity
- **Project name:** Wrapper Self Hosted
- **Packet path:** `docs/projects/wrapper_self_hosted.md`
- **Target project root:** `C:\dev\patchops`
- **Wrapper project root:** `C:\dev\patchops`
- **Selected profile:** `generic_python`
- **Expected runtime:** `py` or the project virtual environment when explicitly chosen

## 2. What this target is
PatchOps is acting as its own current target project.
The target is still the PatchOps repository, not an external business-logic repo.
The goal is to use the existing PatchOps model to evolve PatchOps conservatively.

## 3. What must remain outside PatchOps
- target-repo business logic from other projects
- trader-specific or OSM-specific rules in the generic wrapper core
- reusable workflow logic implemented primarily in PowerShell

## 4. Self-hosted operating rules
- Read `handoff/current_handoff.md`, `handoff/current_handoff.json`, and `handoff/latest_report_copy.txt` first when continuing active work.
- Use this packet as the maintained target contract for self-hosted work.
- Keep PowerShell thin.
- Keep reusable logic in Python-owned surfaces.
- Prefer narrow repair over broad rewrite.
- Preserve one canonical report per run.

## 5. Recommended command surfaces
- `py -m patchops.cli init-project-doc`
- `py -m patchops.cli refresh-project-doc`
- `py -m patchops.cli export-handoff`

## 6. Current development state
- **Current phase:** Phase C
- **Current objective:** Make self-hosted packet generation and refresh operator-friendly.
- **Latest passed patch:** patch_78
- **Latest attempted patch:** patch_79
- **Latest known report path:** (pending current run)
- **Current recommendation:** Use the CLI for packet generation and refresh. Use PowerShell only as a thin launcher/report surface.
- **Next action:** Refresh Documentation Stop P-C after this patch passes.

### Current blockers
- (none)

### Outstanding risks
- wrapper-only repair scripts can still drift wider than the architecture wants if they duplicate reusable logic
"""



def build_operator_guidance_tests() -> str:
    return r'''from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_workflow_doc_mentions_self_hosted_operator_flow() -> None:
    text = _read("docs/project_packet_workflow.md")
    assert "Patch 79 - self-hosted operator flow" in text
    assert "init-project-doc" in text
    assert "refresh-project-doc" in text
    assert "docs/projects/wrapper_self_hosted.md" in text
    assert "Keep PowerShell thin" in text


def test_operator_quickstart_mentions_project_packet_commands() -> None:
    text = _read("docs/operator_quickstart.md")
    assert "Patch 79 - project-packet operator commands" in text
    assert "init-project-doc" in text
    assert "refresh-project-doc" in text
    assert "export-handoff" in text
    assert "one canonical report remains required" in text


def test_project_status_mentions_patch_79_and_patch_80() -> None:
    text = _read("docs/project_status.md")
    assert "Patch 79" in text
    assert "self-hosted operator guidance" in text
    assert "Patch 80" in text


def test_wrapper_self_hosted_packet_exists_and_declares_roots() -> None:
    text = _read("docs/projects/wrapper_self_hosted.md")
    assert "# Project packet - Wrapper Self Hosted" in text
    assert r"`C:\dev\patchops`" in text
    assert "generic_python" in text
    assert "handoff/current_handoff.md" in text
    assert "export-handoff" in text
    assert "patch_78" in text
    assert "patch_79" in text
'''



def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    written_files: list[str] = []

    workflow_path = root / "docs" / "project_packet_workflow.md"
    operator_quickstart_path = root / "docs" / "operator_quickstart.md"
    project_status_path = root / "docs" / "project_status.md"
    wrapper_self_hosted_path = root / "docs" / "projects" / "wrapper_self_hosted.md"
    test_path = root / "tests" / "test_project_packet_operator_guidance.py"

    upsert_block(workflow_path, WORKFLOW_START, WORKFLOW_END, build_workflow_block())
    written_files.append(str(workflow_path))

    upsert_block(operator_quickstart_path, QUICKSTART_START, QUICKSTART_END, build_quickstart_block())
    written_files.append(str(operator_quickstart_path))

    upsert_block(project_status_path, STATUS_START, STATUS_END, build_status_block())
    written_files.append(str(project_status_path))

    write_text(wrapper_self_hosted_path, build_wrapper_self_hosted_packet())
    written_files.append(str(wrapper_self_hosted_path))

    write_text(test_path, build_operator_guidance_tests())
    written_files.append(str(test_path))

    print(json.dumps({"written_files": written_files}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())