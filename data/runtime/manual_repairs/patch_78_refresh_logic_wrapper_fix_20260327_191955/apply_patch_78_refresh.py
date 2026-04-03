from __future__ import annotations

import argparse
import json
from pathlib import Path

REFRESH_TEST = r"""
from __future__ import annotations

import json
from pathlib import Path

from patchops.cli import main
from patchops.project_packets import (
    build_project_packet,
    refresh_project_packet,
    refresh_project_packet_content,
    scaffold_project_packet,
)


def test_refresh_project_packet_content_updates_mutable_status_but_preserves_stable_sections(tmp_path) -> None:
    original = build_project_packet(
        project_name="Trader",
        target_root=r"C:\dev\trader",
        profile_name="trader",
        wrapper_project_root=tmp_path,
        initial_goals=["Create a first narrow manifest"],
    )

    updated = refresh_project_packet_content(
        original,
        current_phase="Phase C",
        current_objective="Add refresh support",
        latest_passed_patch="patch_77",
        latest_attempted_patch="patch_78",
        latest_known_report_path=r"C:\Users\kostas\Desktop\patch_78.txt",
        current_recommendation="Use refresh-project-doc conservatively.",
        next_action="Run compile and packet tests.",
        current_blockers=["Wrapper compatibility needs checking."],
        outstanding_risks=["Overwriting stable packet sections."],
    )

    assert "# Project packet Ã¢â‚¬â€ Trader" in updated
    assert "## 2. Target roots and runtime" in updated
    assert "## 7. Phase guidance" in updated
    assert "**Current phase:** Phase C" in updated
    assert "**Current objective:** Add refresh support" in updated
    assert "**Latest passed patch:** patch_77" in updated
    assert "**Latest attempted patch:** patch_78" in updated
    assert r"**Latest known report path:** C:\Users\kostas\Desktop\patch_78.txt" in updated
    assert "- Wrapper compatibility needs checking." in updated
    assert "- Overwriting stable packet sections." in updated


def test_refresh_project_packet_uses_handoff_json_conservatively(tmp_path) -> None:
    scaffold_payload = scaffold_project_packet(
        project_name="OSM Remediation",
        target_root=r"C:\dev\osm",
        profile_name="generic_python",
        wrapper_project_root=tmp_path,
        initial_goals=["Document the target", "Write the first patch"],
    )

    handoff_path = tmp_path / "handoff.json"
    handoff_path.write_text(
        json.dumps(
            {
                "latest_passed_patch": "patch_77",
                "latest_attempted_patch": "patch_78",
                "next_action": "Run refresh validation.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    payload = refresh_project_packet(
        project_name="OSM Remediation",
        wrapper_project_root=tmp_path,
        handoff_json_path=handoff_path,
        latest_report_path=r"C:\Users\kostas\Desktop\patch_78_report.txt",
        current_phase="Phase C",
        current_objective="Refresh packet state from known artifacts.",
        current_recommendation="Stay conservative and preserve stable sections.",
    )

    packet_path = Path(scaffold_payload["packet_path"])
    content = packet_path.read_text(encoding="utf-8")

    assert payload["written"] is True
    assert payload["project_name"] == "OSM Remediation"
    assert payload["packet_path"] == str(packet_path.resolve())
    assert "patch_77" in content
    assert "patch_78" in content
    assert r"C:\Users\kostas\Desktop\patch_78_report.txt" in content
    assert "Run refresh validation." in content
    assert "# Project packet Ã¢â‚¬â€ OSM Remediation" in content
    assert "## 5. What must remain outside PatchOps" in content


def test_refresh_project_doc_command_updates_existing_packet_and_returns_json(capsys, tmp_path) -> None:
    scaffold_project_packet(
        project_name="OSM Remediation",
        target_root=r"C:\dev\osm",
        profile_name="generic_python",
        wrapper_project_root=tmp_path,
        initial_goals=["Document the target contract"],
    )

    handoff_path = tmp_path / "handoff.json"
    handoff_path.write_text(
        json.dumps(
            {
                "latest_passed_patch": "patch_77",
                "latest_attempted_patch": "patch_78",
                "next_action": "Review refresh output.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "refresh-project-doc",
            "--project-name",
            "OSM Remediation",
            "--wrapper-root",
            str(tmp_path),
            "--handoff-json-path",
            str(handoff_path),
            "--report-path",
            r"C:\Users\kostas\Desktop\patch_78_report.txt",
            "--current-phase",
            "Phase C",
            "--current-objective",
            "Refresh packet state from known artifacts.",
            "--current-recommendation",
            "Keep the refresh conservative.",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    packet_path = Path(payload["packet_path"])
    assert packet_path.exists()

    content = packet_path.read_text(encoding="utf-8")
    assert payload["written"] is True
    assert payload["project_name"] == "OSM Remediation"
    assert payload["latest_passed_patch"] == "patch_77"
    assert payload["latest_attempted_patch"] == "patch_78"
    assert "Review refresh output." in content
    assert "Keep the refresh conservative." in content
"""

APPEND_PROJECT_PACKETS = r'''

_MUTABLE_STATUS_HEADING = "### Mutable status"
_CURRENT_BLOCKERS_HEADING = "### Current blockers"
_OUTSTANDING_RISKS_HEADING = "### Outstanding risks"


def _normalize_status_line(value: str | None, *, empty_line: str) -> str:
    if value is None:
        return empty_line
    text = str(value).strip()
    return text or empty_line


def _load_optional_json(path: str | Path | None) -> dict:
    if path is None:
        return {}
    candidate = Path(path)
    if not candidate.exists():
        return {}
    try:
        payload = json.loads(candidate.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _build_mutable_status_lines(
    *,
    current_phase: str | None = None,
    current_objective: str | None = None,
    latest_passed_patch: str | None = None,
    latest_attempted_patch: str | None = None,
    latest_known_report_path: str | None = None,
    current_recommendation: str | None = None,
    next_action: str | None = None,
) -> list[str]:
    return [
        _MUTABLE_STATUS_HEADING,
        f"- **Current phase:** {_normalize_status_line(current_phase, empty_line='(none yet)')}",
        f"- **Current objective:** {_normalize_status_line(current_objective, empty_line='(none yet)')}",
        f"- **Latest passed patch:** {_normalize_status_line(latest_passed_patch, empty_line='(none yet)')}",
        f"- **Latest attempted patch:** {_normalize_status_line(latest_attempted_patch, empty_line='(none yet)')}",
        f"- **Latest known report path:** {_normalize_status_line(latest_known_report_path, empty_line='(none yet)')}",
        f"- **Current recommendation:** {_normalize_status_line(current_recommendation, empty_line='(none yet)')}",
        f"- **Next action:** {_normalize_status_line(next_action, empty_line='(none yet)')}",
        "",
    ]


def _replace_section(content: str, heading: str, next_heading: str, replacement_lines: list[str]) -> str:
    start = content.find(heading)
    if start == -1:
        raise ValueError(f"Missing heading in project packet: {heading}")
    end = content.find(next_heading, start)
    if end == -1:
        raise ValueError(f"Missing heading in project packet: {next_heading}")
    replacement = "\n".join(replacement_lines)
    if not replacement.endswith("\n"):
        replacement += "\n"
    return content[:start] + replacement + content[end:]


def refresh_project_packet_content(
    content: str,
    *,
    current_phase: str | None = None,
    current_objective: str | None = None,
    latest_passed_patch: str | None = None,
    latest_attempted_patch: str | None = None,
    latest_known_report_path: str | None = None,
    current_recommendation: str | None = None,
    next_action: str | None = None,
    current_blockers=None,
    outstanding_risks=None,
) -> str:
    blocker_lines = _normalize_lines(current_blockers, empty_line="(none)")
    risk_lines = _normalize_lines(outstanding_risks, empty_line="(none)")

    updated = _replace_section(
        content,
        _MUTABLE_STATUS_HEADING,
        _CURRENT_BLOCKERS_HEADING,
        _build_mutable_status_lines(
            current_phase=current_phase,
            current_objective=current_objective,
            latest_passed_patch=latest_passed_patch,
            latest_attempted_patch=latest_attempted_patch,
            latest_known_report_path=latest_known_report_path,
            current_recommendation=current_recommendation,
            next_action=next_action,
        ),
    )
    updated = _replace_section(
        updated,
        _CURRENT_BLOCKERS_HEADING,
        _OUTSTANDING_RISKS_HEADING,
        [_CURRENT_BLOCKERS_HEADING, *[f"- {item}" for item in blocker_lines], ""],
    )

    risk_marker = _OUTSTANDING_RISKS_HEADING
    risk_start = updated.find(risk_marker)
    if risk_start == -1:
        raise ValueError(f"Missing heading in project packet: {risk_marker}")
    risk_replacement = "\n".join([risk_marker, *[f"- {item}" for item in risk_lines], ""]) + "\n"
    updated = updated[:risk_start] + risk_replacement

    return updated if updated.endswith("\n") else updated + "\n"


def refresh_project_packet(
    *,
    project_name: str,
    wrapper_project_root: str | Path | None = None,
    packet_path: str | Path | None = None,
    handoff_json_path: str | Path | None = None,
    latest_report_path: str | None = None,
    current_phase: str | None = None,
    current_objective: str | None = None,
    latest_passed_patch: str | None = None,
    latest_attempted_patch: str | None = None,
    current_recommendation: str | None = None,
    next_action: str | None = None,
    current_blockers=None,
    outstanding_risks=None,
) -> dict[str, object]:
    wrapper_root = resolve_wrapper_root(wrapper_project_root)
    resolved_packet_path = Path(packet_path) if packet_path is not None else default_project_packet_path(
        project_name,
        wrapper_project_root=wrapper_root,
    )
    if not resolved_packet_path.is_absolute():
        resolved_packet_path = (wrapper_root / resolved_packet_path).resolve()
    if not resolved_packet_path.exists():
        raise FileNotFoundError(f"Project packet does not exist: {resolved_packet_path}")

    handoff_payload = _load_optional_json(handoff_json_path)

    refreshed_content = refresh_project_packet_content(
        resolved_packet_path.read_text(encoding="utf-8"),
        current_phase=current_phase,
        current_objective=current_objective,
        latest_passed_patch=latest_passed_patch or handoff_payload.get("latest_passed_patch"),
        latest_attempted_patch=latest_attempted_patch or handoff_payload.get("latest_attempted_patch"),
        latest_known_report_path=latest_report_path,
        current_recommendation=current_recommendation,
        next_action=next_action or handoff_payload.get("next_action"),
        current_blockers=current_blockers,
        outstanding_risks=outstanding_risks,
    )
    resolved_packet_path.write_text(refreshed_content, encoding="utf-8")

    return {
        "written": True,
        "project_name": project_name,
        "packet_path": str(resolved_packet_path.resolve()),
        "wrapper_root": str(wrapper_root),
        "latest_passed_patch": latest_passed_patch or handoff_payload.get("latest_passed_patch"),
        "latest_attempted_patch": latest_attempted_patch or handoff_payload.get("latest_attempted_patch"),
        "latest_report_path": latest_report_path,
        "handoff_json_path": str(Path(handoff_json_path).resolve()) if handoff_json_path else None,
    }
'''


def ensure_project_packets(repo_root: Path) -> None:
    path = repo_root / "patchops" / "project_packets.py"
    text = path.read_text(encoding="utf-8")
    if "import json" not in text:
        text = text.replace("import re\n", "import json\nimport re\n", 1)
    if "def refresh_project_packet(" not in text:
        text = text.rstrip() + "\n" + APPEND_PROJECT_PACKETS
    path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")


def ensure_cli(repo_root: Path) -> None:
    path = repo_root / "patchops" / "cli.py"
    text = path.read_text(encoding="utf-8")

    if r'parser.error(\"Unknown command\")' in text:
        text = text.replace(r'parser.error(\"Unknown command\")', 'parser.error("Unknown command")')

    refresh_parser_block = """
    refresh_project_doc_parser = subparsers.add_parser(
        \"refresh-project-doc\",
        help=\"Refresh the mutable section of an existing project packet under docs/projects/\",
    )
    refresh_project_doc_parser.description = (
        \"Refresh the mutable packet state from explicit inputs and optional handoff/report artifacts.\"
    )
    refresh_project_doc_parser.add_argument(\"--project-name\", required=True, help=\"Human-readable project name\")
    refresh_project_doc_parser.add_argument(\"--wrapper-root\", help=\"Override wrapper project root\", default=None)
    refresh_project_doc_parser.add_argument(\"--packet-path\", default=None, help=\"Optional explicit markdown packet path\")
    refresh_project_doc_parser.add_argument(\"--handoff-json-path\", default=None, help=\"Optional handoff JSON path\")
    refresh_project_doc_parser.add_argument(\"--report-path\", default=None, help=\"Optional latest report path\")
    refresh_project_doc_parser.add_argument(\"--current-phase\", default=None, help=\"Optional current phase override\")
    refresh_project_doc_parser.add_argument(\"--current-objective\", default=None, help=\"Optional current objective override\")
    refresh_project_doc_parser.add_argument(\"--latest-passed-patch\", default=None, help=\"Optional latest passed patch override\")
    refresh_project_doc_parser.add_argument(\"--latest-attempted-patch\", default=None, help=\"Optional latest attempted patch override\")
    refresh_project_doc_parser.add_argument(\"--current-recommendation\", default=None, help=\"Optional recommendation override\")
    refresh_project_doc_parser.add_argument(\"--next-action\", default=None, help=\"Optional next action override\")
    refresh_project_doc_parser.add_argument(\"--blocker\", action=\"append\", default=[], help=\"Optional current blocker line; may be supplied more than once.\")
    refresh_project_doc_parser.add_argument(\"--risk\", action=\"append\", default=[], help=\"Optional outstanding risk line; may be supplied more than once.\")

"""
    init_marker = '    init_project_doc_parser.add_argument("--wrapper-root", help="Override wrapper project root", default=None)\n\n'
    if 'refresh_project_doc_parser = subparsers.add_parser(' not in text:
        if init_marker not in text:
            raise RuntimeError("Could not find init-project-doc parser block end in cli.py")
        text = text.replace(init_marker, init_marker + refresh_parser_block, 1)

    refresh_handler_block = """
    if args.command == \"refresh-project-doc\":
        from patchops.project_packets import refresh_project_packet

        payload = refresh_project_packet(
            project_name=args.project_name,
            wrapper_project_root=args.wrapper_root,
            packet_path=args.packet_path,
            handoff_json_path=args.handoff_json_path,
            latest_report_path=args.report_path,
            current_phase=args.current_phase,
            current_objective=args.current_objective,
            latest_passed_patch=args.latest_passed_patch,
            latest_attempted_patch=args.latest_attempted_patch,
            current_recommendation=args.current_recommendation,
            next_action=args.next_action,
            current_blockers=args.blocker,
            outstanding_risks=args.risk,
        )
        print(json.dumps(payload, indent=2))
        return 0

"""
    if 'if args.command == "refresh-project-doc":' not in text:
        marker = '\n\n    parser.error("Unknown command")'
        if marker not in text:
            raise RuntimeError("Could not find parser.error fallback in cli.py")
        text = text.replace(marker, "\n" + refresh_handler_block + '    parser.error("Unknown command")', 1)

    path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")


def write_refresh_test(repo_root: Path) -> None:
    path = repo_root / "tests" / "test_project_packet_refresh.py"
    path.write_text(REFRESH_TEST.strip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    args = parser.parse_args()

    repo_root = Path(args.project_root).resolve()
    ensure_project_packets(repo_root)
    ensure_cli(repo_root)
    write_refresh_test(repo_root)

    payload = {
        "written_files": [
            str(repo_root / "patchops" / "project_packets.py"),
            str(repo_root / "patchops" / "cli.py"),
            str(repo_root / "tests" / "test_project_packet_refresh.py"),
        ]
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())