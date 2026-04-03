from __future__ import annotations

from pathlib import Path

ROOT = Path(r"C:\dev\patchops")
FILES = {
    "renderer": ROOT / "patchops" / "reporting" / "renderer.py",
    "sections": ROOT / "patchops" / "reporting" / "sections.py",
    "command_sections": ROOT / "patchops" / "reporting" / "command_sections.py",
    "test_reporting": ROOT / "tests" / "test_reporting.py",
    "test_reporting_command_sections_current": ROOT / "tests" / "test_reporting_command_sections_current.py",
    "test_reporting_output_helper_current": ROOT / "tests" / "test_reporting_output_helper_current.py",
    "test_summary_integrity_current": ROOT / "tests" / "test_summary_integrity_current.py",
    "test_summary_derivation_lock_current": ROOT / "tests" / "test_summary_derivation_lock_current.py",
    "test_required_vs_tolerated_report_current": ROOT / "tests" / "test_required_vs_tolerated_report_current.py",
    "test_summary_integrity_workflow_current": ROOT / "tests" / "test_summary_integrity_workflow_current.py",
}

CHECKS = {
    "sections": [
        ("def command_group_section", "has command_group_section"),
        ("def full_output_section", "has full_output_section"),
        ("def wrapper_only_retry_section", "has wrapper_only_retry_section"),
    ],
    "command_sections": [
        ("build_report_command_section", "exports build_report_command_section"),
        ("build_report_command_sections", "exports build_report_command_sections"),
        ("render_command_output_section", "exports render_command_output_section"),
        ("render_report_command_output_section", "exports render_report_command_output_section"),
        ("ReportCommandSection", "defines ReportCommandSection"),
    ],
}

print("CURRENT REPORTING SURFACE AUDIT")
print("-------------------------------")
for key, path in FILES.items():
    print(f"{key} exists : {'yes' if path.exists() else 'no'}")
    if not path.exists():
        continue
    text = path.read_text(encoding="utf-8")
    print(f"{key} line count : {len(text.splitlines())}")
    for fragment, label in CHECKS.get(key, []):
        print(f"{key} {label} : {'yes' if fragment in text else 'no'}")