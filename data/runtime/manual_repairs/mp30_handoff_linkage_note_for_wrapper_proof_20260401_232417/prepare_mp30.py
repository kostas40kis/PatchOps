from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path


LINKAGE_HEADER = "## Wrapper proof linkage"
REQUIRED_FRAGMENTS = [
    "handoff/current_handoff.md",
    "canonical report",
    "Manifest Path",
    "Active Profile",
    "Runtime Path",
    "Wrapper Project Root",
    "Target Project Root",
    "File Write Origin",
    "This note is a linkage note only. It does not redesign the handoff bundle.",
]


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def ensure_trailing_newline(value: str) -> str:
    if not value.endswith("\n"):
        return value + "\n"
    return value


def build_note() -> str:
    return textwrap.dedent(
        """
        ## Wrapper proof linkage

        Continuation readers of `handoff/current_handoff.md` and related bundle artifacts should treat the canonical report as the source of truth for wrapper-exercised provenance.

        Review these report fields directly before inferring wrapper execution from prose:

        - `Manifest Path`
        - `Active Profile`
        - `Runtime Path`
        - `Wrapper Project Root`
        - `Target Project Root`
        - `File Write Origin`

        This note is a linkage note only. It does not redesign the handoff bundle.
        """
    ).strip() + "\n"


def main() -> int:
    project_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    validation_program = sys.argv[3]
    validation_prefix_arg = sys.argv[4]

    content_root = working_root / "content"
    inner_report_root = working_root / "inner_reports"
    content_root.mkdir(parents=True, exist_ok=True)
    inner_report_root.mkdir(parents=True, exist_ok=True)

    handoff_doc_repo_path = project_root / "docs" / "handoff_surface.md"
    mp29_test_repo_path = project_root / "tests" / "test_launcher_to_core_provenance_current.py"
    mp30_test_repo_path = project_root / "tests" / "test_wrapper_proof_handoff_linkage_current.py"

    handoff_text = read_text(handoff_doc_repo_path)
    already_present = all(fragment in handoff_text for fragment in REQUIRED_FRAGMENTS)

    decision = "author_mp30"
    decision_reason = "MP29 proof exists; author the narrow handoff linkage note."
    if mp30_test_repo_path.exists() and already_present:
        decision = "stop_mp30_already_present"
        decision_reason = "Wrapper-proof handoff linkage note and current test already exist."
    elif not mp29_test_repo_path.exists():
        decision = "stop_mp29_missing"
        decision_reason = "MP29 proof surface is missing. tests/test_launcher_to_core_provenance_current.py was not found."

    state_lines = [
        f"decision={decision}",
        f"decision_reason={decision_reason}",
        f"handoff_doc_path={handoff_doc_repo_path}",
        f"handoff_doc_exists={'yes' if handoff_doc_repo_path.exists() else 'no'}",
        f"mp29_test_exists={'yes' if mp29_test_repo_path.exists() else 'no'}",
        f"mp30_test_exists={'yes' if mp30_test_repo_path.exists() else 'no'}",
        f"linkage_header_present={'yes' if LINKAGE_HEADER in handoff_text else 'no'}",
        f"required_fragments_present={'yes' if already_present else 'no'}",
        f"required_fragments={' | '.join(REQUIRED_FRAGMENTS)}",
    ]

    if decision != "author_mp30":
        (working_root / "prep_state.txt").write_text("\n".join(state_lines) + "\n", encoding="utf-8")
        return 0

    updated_doc_text = handoff_text
    note_text = build_note()

    if not updated_doc_text:
        updated_doc_text = "# Handoff surface\n\n"
    updated_doc_text = ensure_trailing_newline(updated_doc_text).rstrip() + "\n\n" + note_text

    content_doc_path = content_root / "docs" / "handoff_surface.md"
    content_doc_path.parent.mkdir(parents=True, exist_ok=True)
    content_doc_path.write_text(updated_doc_text, encoding="utf-8")

    content_test_path = content_root / "tests" / "test_wrapper_proof_handoff_linkage_current.py"
    content_test_path.parent.mkdir(parents=True, exist_ok=True)

    test_content = textwrap.dedent(
        """
        from pathlib import Path


        PROJECT_ROOT = Path(__file__).resolve().parents[1]
        HANDOFF_DOC = PROJECT_ROOT / "docs" / "handoff_surface.md"
        REQUIRED_FRAGMENTS = [
            "handoff/current_handoff.md",
            "canonical report",
            "Manifest Path",
            "Active Profile",
            "Runtime Path",
            "Wrapper Project Root",
            "Target Project Root",
            "File Write Origin",
            "This note is a linkage note only. It does not redesign the handoff bundle.",
        ]


        def test_wrapper_proof_handoff_linkage_note_current() -> None:
            assert HANDOFF_DOC.exists(), f"Missing handoff surface doc: {HANDOFF_DOC}"
            text = HANDOFF_DOC.read_text(encoding="utf-8")
            assert "## Wrapper proof linkage" in text
            for fragment in REQUIRED_FRAGMENTS:
                assert fragment in text, f"Missing fragment in handoff linkage note: {fragment!r}"
        """
    ).lstrip()
    content_test_path.write_text(test_content, encoding="utf-8")

    validation_targets = [
        "tests/test_wrapper_proof_handoff_linkage_current.py",
        "tests/test_launcher_to_core_provenance_current.py",
    ]
    for candidate in (
        "tests/test_run_origin_metadata_current.py",
        "tests/test_report_header_provenance_current.py",
        "tests/test_file_write_origin_proof_current.py",
    ):
        if (project_root / candidate).exists():
            validation_targets.append(candidate)

    validation_args = []
    if validation_prefix_arg:
        validation_args.append(validation_prefix_arg)
    validation_args.extend(["-m", "pytest", "-q"])
    validation_args.extend(validation_targets)

    manifest = {
        "manifest_version": "1",
        "patch_name": "mp30_handoff_linkage_note_for_wrapper_proof",
        "active_profile": "generic_python",
        "target_project_root": str(project_root),
        "files_to_write": [
            {
                "path": "docs/handoff_surface.md",
                "content_path": str(content_doc_path.resolve().relative_to(project_root)),
                "encoding": "utf-8",
            },
            {
                "path": "tests/test_wrapper_proof_handoff_linkage_current.py",
                "content_path": str(content_test_path.resolve().relative_to(project_root)),
                "encoding": "utf-8",
            },
        ],
        "validation_commands": [
            {
                "name": "mp30 wrapper-proof handoff linkage tests",
                "program": validation_program,
                "args": validation_args,
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "report_preferences": {
            "report_dir": str(inner_report_root.resolve()),
            "report_name_prefix": "mp30",
            "write_to_desktop": False,
        },
        "tags": [
            "maintenance",
            "pythonization",
            "phase_d",
            "mp30",
            "self_hosted",
        ],
        "notes": "MP30 handoff linkage note for wrapper proof after confirmed MP29 completion.",
    }

    (working_root / "patch_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (working_root / "prep_state.txt").write_text("\n".join(state_lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())