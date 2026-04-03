from __future__ import annotations

import json
from pathlib import Path

PATCH84_LLM_USAGE_BLOCK = """<!-- PATCHOPS_PATCH84_LLM_USAGE_ONBOARDING:START -->
## Project-packet onboarding now includes helpers

For a brand-new target project, the onboarding flow is now:

1. read the generic PatchOps packet,
2. determine the smallest correct profile with `recommend-profile`,
3. create or refresh the target packet under `docs/projects/`,
4. generate the first manifest from the closest example or `starter`,
5. run `check`, `inspect`, `plan`, then apply or verify,
6. inspect the canonical report,
7. refresh the project packet and continue patch by patch.

For already-running PatchOps work, continuation still begins with:
- `handoff/current_handoff.md`
- `handoff/current_handoff.json`
- `handoff/latest_report_copy.txt`

Project packets and onboarding helpers speed up new-target startup.
They do not replace handoff for current-state continuation.
<!-- PATCHOPS_PATCH84_LLM_USAGE_ONBOARDING:END -->"""

PATCH84_WORKFLOW_BLOCK = """<!-- PATCHOPS_PATCH84_WORKFLOW_MECHANICAL:START -->
## Mechanical onboarding sequence

A future LLM should treat new-target onboarding as mechanical:

1. read the generic PatchOps packet,
2. run `recommend-profile --target-root ...`,
3. inspect the closest starter examples,
4. use `init-project-doc` for a brand-new packet when needed,
5. use `bootstrap-target` when a stronger onboarding bundle is helpful,
6. use `starter --profile ... --intent ...` to avoid blank-page manifest authoring,
7. use `refresh-project-doc` after validated progress changes mutable packet state,
8. continue with `check`, `inspect`, `plan`, and then apply or verify.

The onboarding story should now feel closer to the handoff story:
structured, conservative, and evidence-first.
<!-- PATCHOPS_PATCH84_WORKFLOW_MECHANICAL:END -->"""

PATCH84_PROFILE_SYSTEM_BLOCK = """<!-- PATCHOPS_PATCH84_PROFILE_SYSTEM_HELPERS:START -->
## Project-packet helper relationship to profiles

Profiles remain the executable abstraction.
The onboarding helpers do not replace profile choice; they make it more explicit and faster.

Current helper surfaces:
- `recommend-profile --target-root ...`
- `starter --profile ... --intent ...`

Correct relationship:
- profile = executable target assumptions
- project packet = maintained target-facing contract
- starter helper = conservative first-manifest scaffold tied to patch class

When in doubt, choose the smallest correct profile and the narrowest starter intent.
<!-- PATCHOPS_PATCH84_PROFILE_SYSTEM_HELPERS:END -->"""

PATCH84_EXAMPLES_BLOCK = """<!-- PATCHOPS_PATCH84_EXAMPLES_STARTER_GUIDANCE:START -->
## Examples remain the baseline even with helpers

The onboarding helpers do not replace examples.
They reduce blank-page authoring and point operators toward the closest conservative starting surface.

Recommended operator order:
1. inspect the closest examples,
2. use `recommend-profile` when profile choice is unclear,
3. use `starter` only to generate a conservative first manifest skeleton,
4. narrow the manifest deliberately before apply or verify.

This keeps examples as the baseline and helpers as accelerators.
<!-- PATCHOPS_PATCH84_EXAMPLES_STARTER_GUIDANCE:END -->"""

PATCH84_STATUS_BLOCK = """<!-- PATCHOPS_PATCH84_STATUS_FINALIZATION:START -->
## Project-packet rollout status after Documentation Stop P-D

### Shipped now

- project-packet contract and workflow docs,
- maintained project-packet examples under `docs/projects/`,
- scaffold and refresh helpers,
- onboarding bootstrap artifacts,
- profile recommendation helper,
- starter helper by intent,
- operator-facing documentation connecting onboarding and continuation,
- tests protecting the packet, workflow, helper, and command surfaces.

### Practical interpretation

The onboarding layer is now substantially complete:
- generic docs teach PatchOps,
- project packets teach one target,
- helper commands reduce ambiguity during first use,
- handoff remains the resume surface for already-running work.

### Remaining posture

Further changes after this point should be maintenance, refinement, or target-specific expansion rather than architectural redesign.
<!-- PATCHOPS_PATCH84_STATUS_FINALIZATION:END -->"""

TEST_FILE = '''from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def test_llm_usage_mentions_helpers_and_handoff_split() -> None:
    text = _read("docs/llm_usage.md")
    assert "PATCHOPS_PATCH84_LLM_USAGE_ONBOARDING:START" in text
    assert "recommend-profile" in text
    assert "starter --profile" in text
    assert "handoff/current_handoff.md" in text


def test_workflow_doc_describes_mechanical_sequence() -> None:
    text = _read("docs/project_packet_workflow.md")
    assert "PATCHOPS_PATCH84_WORKFLOW_MECHANICAL:START" in text
    assert "bootstrap-target" in text
    assert "refresh-project-doc" in text
    assert "structured, conservative, and evidence-first" in text


def test_profile_system_and_examples_explain_helper_relationship() -> None:
    profile_text = _read("docs/profile_system.md")
    examples_text = _read("docs/examples.md")
    assert "PATCHOPS_PATCH84_PROFILE_SYSTEM_HELPERS:START" in profile_text
    assert "recommend-profile --target-root" in profile_text
    assert "PATCHOPS_PATCH84_EXAMPLES_STARTER_GUIDANCE:START" in examples_text
    assert "examples as the baseline" in examples_text


def test_project_status_marks_onboarding_layer_substantially_complete() -> None:
    text = _read("docs/project_status.md")
    assert "PATCHOPS_PATCH84_STATUS_FINALIZATION:START" in text
    assert "profile recommendation helper" in text
    assert "starter helper by intent" in text
    assert "handoff remains the resume surface" in text
'''


def replace_or_append(text: str, block: str) -> str:
    start_marker = block.splitlines()[0]
    end_marker = block.splitlines()[-1]
    if start_marker in text and end_marker in text:
        prefix = text.split(start_marker, 1)[0]
        suffix = text.split(end_marker, 1)[1]
        if prefix and not prefix.endswith("\n"):
            prefix += "\n"
        if suffix and not suffix.startswith("\n"):
            suffix = "\n" + suffix
        return prefix + block + suffix
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

    llm_usage_doc = root / "docs" / "llm_usage.md"
    workflow_doc = root / "docs" / "project_packet_workflow.md"
    profile_system_doc = root / "docs" / "profile_system.md"
    examples_doc = root / "docs" / "examples.md"
    status_doc = root / "docs" / "project_status.md"
    test_file = root / "tests" / "test_project_packet_doc_stop_d.py"

    update_doc(llm_usage_doc, PATCH84_LLM_USAGE_BLOCK)
    update_doc(workflow_doc, PATCH84_WORKFLOW_BLOCK)
    update_doc(profile_system_doc, PATCH84_PROFILE_SYSTEM_BLOCK)
    update_doc(examples_doc, PATCH84_EXAMPLES_BLOCK)
    update_doc(status_doc, PATCH84_STATUS_BLOCK)
    test_file.write_text(TEST_FILE, encoding="utf-8")

    print(
        json.dumps(
            {
                "written_files": [
                    str(llm_usage_doc),
                    str(workflow_doc),
                    str(profile_system_doc),
                    str(examples_doc),
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