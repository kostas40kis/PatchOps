from __future__ import annotations

import json
import re
import sys
import textwrap
from pathlib import Path


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def discover_write_origin_markers(paths: list[Path]) -> list[str]:
    patterns = [
        re.compile(r"""['"]([^'"\r\n]*(?:write|writes)[^'"\r\n]*(?:origin|engine|wrapper)[^'"\r\n]*)['"]""", re.IGNORECASE),
        re.compile(r"""['"]([^'"\r\n]*(?:origin|engine|wrapper)[^'"\r\n]*(?:write|writes)[^'"\r\n]*)['"]""", re.IGNORECASE),
    ]
    candidates: list[str] = []
    for path in paths:
        text = read_text(path)
        if not text:
            continue
        for pattern in patterns:
            for match in pattern.findall(text):
                normalized = " ".join(match.split())
                if len(normalized) >= 8:
                    candidates.append(normalized)
    fallback = [
        "File Write Origin",
        "Write Origin",
        "Wrapper-Owned Write Engine",
        "Wrapper Write Engine",
        "Writes Applied By Wrapper",
        "Writes Applied By",
    ]
    for item in fallback:
        if item not in candidates:
            candidates.append(item)
    ordered: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(item)
    return ordered


def main() -> int:
    project_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()
    validation_program = sys.argv[3]
    validation_prefix_arg = sys.argv[4]

    content_root = working_root / "content"
    inner_report_root = working_root / "inner_reports"
    content_root.mkdir(parents=True, exist_ok=True)
    inner_report_root.mkdir(parents=True, exist_ok=True)

    metadata_path = project_root / "patchops" / "reporting" / "metadata.py"
    sections_path = project_root / "patchops" / "reporting" / "sections.py"
    run_origin_test_path = project_root / "tests" / "test_run_origin_metadata_current.py"
    header_test_path = project_root / "tests" / "test_report_header_provenance_current.py"
    file_write_test_path = project_root / "tests" / "test_file_write_origin_proof_current.py"
    mp29_test_repo_path = project_root / "tests" / "test_launcher_to_core_provenance_current.py"

    metadata_text = read_text(metadata_path)
    sections_text = read_text(sections_path)

    has_metadata_builder = "build_run_origin_metadata" in metadata_text
    mentions_write_records = "write_records" in metadata_text or "write_records" in sections_text
    has_compat_guard = bool(
        re.search(r"""getattr\(\s*[^,\n]+,\s*['"]write_records['"]""", metadata_text)
        or re.search(r"""hasattr\(\s*[^,\n]+,\s*['"]write_records['"]""", metadata_text)
    )

    write_origin_markers = discover_write_origin_markers(
        [file_write_test_path, metadata_path, sections_path]
    )

    mp28_satisfied = all(
        [
            has_metadata_builder,
            run_origin_test_path.exists(),
            header_test_path.exists(),
            file_write_test_path.exists(),
            mentions_write_records,
            has_compat_guard,
            bool(write_origin_markers),
        ]
    )

    decision = "author_mp29"
    decision_reason = "mp28 satisfied; author the narrow launcher proof."
    if mp29_test_repo_path.exists():
        decision = "stop_mp29_already_present"
        decision_reason = "tests/test_launcher_to_core_provenance_current.py already exists."
    elif not mp28_satisfied:
        decision = "stop_mp28_incomplete"
        decision_reason = (
            "MP28 evidence is incomplete. Required signals: metadata builder, current provenance tests, "
            "write_records mention, compatibility guard, and write-origin marker."
        )

    state_lines = [
        f"decision={decision}",
        f"decision_reason={decision_reason}",
        f"metadata_path={metadata_path}",
        f"sections_path={sections_path}",
        f"run_origin_test_exists={'yes' if run_origin_test_path.exists() else 'no'}",
        f"header_test_exists={'yes' if header_test_path.exists() else 'no'}",
        f"file_write_test_exists={'yes' if file_write_test_path.exists() else 'no'}",
        f"has_metadata_builder={'yes' if has_metadata_builder else 'no'}",
        f"mentions_write_records={'yes' if mentions_write_records else 'no'}",
        f"has_compat_guard={'yes' if has_compat_guard else 'no'}",
        f"write_origin_markers={' | '.join(write_origin_markers)}",
    ]

    if decision != "author_mp29":
        (working_root / "prep_state.txt").write_text("\n".join(state_lines) + "\n", encoding="utf-8")
        return 0

    content_test_path = content_root / "tests" / "test_launcher_to_core_provenance_current.py"
    content_test_path.parent.mkdir(parents=True, exist_ok=True)

    markers_literal = repr(write_origin_markers)

    test_content = textwrap.dedent(
        f"""
        import json
        import shutil
        import subprocess
        import sys
        from pathlib import Path

        import pytest


        PROJECT_ROOT = Path(__file__).resolve().parents[1]
        LAUNCHER_PATH = PROJECT_ROOT / "powershell" / "Invoke-PatchManifest.ps1"
        WRITE_ORIGIN_MARKERS = {markers_literal}


        def _powershell_exe() -> str:
            candidates = [
                shutil.which("powershell"),
                r"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
            ]
            for candidate in candidates:
                if candidate and Path(candidate).exists():
                    return str(candidate)
            pytest.skip("Could not resolve powershell.exe for launcher testing.")


        def _write_manifest(tmp_path: Path) -> tuple[Path, Path, Path]:
            target_root = tmp_path / "target"
            target_root.mkdir(parents=True, exist_ok=True)
            report_dir = tmp_path / "reports"
            report_dir.mkdir(parents=True, exist_ok=True)

            manifest = {{
                "manifest_version": "1",
                "patch_name": "mp29_launcher_to_core_provenance_proof",
                "active_profile": "generic_python",
                "target_project_root": str(target_root.resolve()),
                "files_to_write": [
                    {{
                        "path": "generated/launcher_probe.txt",
                        "content": "launcher provenance proof\\n",
                        "encoding": "utf-8",
                    }}
                ],
                "validation_commands": [],
                "report_preferences": {{
                    "report_dir": str(report_dir.resolve()),
                    "report_name_prefix": "mp29_launcher",
                    "write_to_desktop": False,
                }},
            }}

            manifest_path = tmp_path / "mp29_launcher_manifest.json"
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            return manifest_path, target_root, report_dir


        def _assert_report_line_contains(report_text: str, label: str, expected_fragment: str) -> None:
            lines = report_text.splitlines()
            assert any(label in line and expected_fragment in line for line in lines), (
                f"Expected one report line containing label {{label!r}} and fragment {{expected_fragment!r}}.\\n"
                f"Report text:\\n{{report_text}}"
            )


        def test_invoke_patch_manifest_launcher_preserves_provenance_into_report(tmp_path: Path) -> None:
            assert LAUNCHER_PATH.exists(), f"Missing launcher: {{LAUNCHER_PATH}}"

            manifest_path, target_root, report_dir = _write_manifest(tmp_path)
            powershell_exe = _powershell_exe()

            result = subprocess.run(
                [
                    powershell_exe,
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(LAUNCHER_PATH),
                    "-ManifestPath",
                    str(manifest_path),
                    "-PythonExe",
                    sys.executable,
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
            )

            assert result.returncode == 0, (
                f"Launcher apply failed.\\nstdout:\\n{{result.stdout}}\\n\\nstderr:\\n{{result.stderr}}"
            )

            written_path = target_root / "generated" / "launcher_probe.txt"
            assert written_path.exists(), f"Expected written file from launcher apply: {{written_path}}"

            reports = sorted(report_dir.glob("*.txt"))
            assert reports, f"Expected a generated report under {{report_dir}}"
            report_text = reports[-1].read_text(encoding="utf-8")

            assert "PATCHOPS APPLY" in report_text
            _assert_report_line_contains(report_text, "Manifest Path", str(manifest_path.resolve()))
            _assert_report_line_contains(report_text, "Wrapper Project Root", str(PROJECT_ROOT.resolve()))
            _assert_report_line_contains(report_text, "Target Project Root", str(target_root.resolve()))
            _assert_report_line_contains(report_text, "Active Profile", "generic_python")
            assert "Runtime Path" in report_text
            assert str(written_path.resolve()) in report_text
            assert any(marker in report_text for marker in WRITE_ORIGIN_MARKERS), (
                "Expected current write-origin proof marker in launcher-generated report.\\n"
                f"Markers: {{WRITE_ORIGIN_MARKERS}}\\n\\nReport text:\\n{{report_text}}"
            )
        """
    ).lstrip()

    content_test_path.write_text(test_content, encoding="utf-8")

    validation_targets = [
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
        "patch_name": "mp29_launcher_to_core_provenance_proof",
        "active_profile": "generic_python",
        "target_project_root": str(project_root),
        "files_to_write": [
            {
                "path": "tests/test_launcher_to_core_provenance_current.py",
                "content_path": str(content_test_path.resolve().relative_to(project_root)),
                "encoding": "utf-8",
            }
        ],
        "validation_commands": [
            {
                "name": "mp29 provenance proof tests",
                "program": validation_program,
                "args": validation_args,
                "working_directory": ".",
                "allowed_exit_codes": [0],
            }
        ],
        "report_preferences": {
            "report_dir": str(inner_report_root.resolve()),
            "report_name_prefix": "mp29",
            "write_to_desktop": False,
        },
        "tags": [
            "maintenance",
            "pythonization",
            "phase_d",
            "mp29",
            "self_hosted",
        ],
        "notes": "MP29 launcher-to-core provenance propagation proof after confirmed MP28 completion.",
    }

    manifest_path = working_root / "patch_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    state_lines.extend(
        [
            f"content_test_path={content_test_path}",
            f"manifest_path={manifest_path}",
            f"inner_report_root={inner_report_root}",
            f"validation_targets={' | '.join(validation_targets)}",
        ]
    )
    (working_root / "prep_state.txt").write_text("\n".join(state_lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())