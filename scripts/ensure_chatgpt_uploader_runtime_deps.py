from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from patchops.chatgpt_uploader.runtime_dependency import ensure_dependencies, write_dependency_evidence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ensure ChatGPT uploader runtime dependencies for the current Python interpreter.")
    parser.add_argument("--repo-root", default=str(PROJECT_ROOT))
    parser.add_argument("--evidence-dir", default=None)
    parser.add_argument("--package", action="append", default=None)
    parser.add_argument("--allow-install", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=240)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).expanduser().resolve()
    evidence_dir = Path(args.evidence_dir).expanduser().resolve() if args.evidence_dir else repo_root / "data" / "runtime" / "chatgpt_uploader" / "u2_04b_runtime_dependency"
    result = ensure_dependencies(packages=args.package or ["pywinauto"], allow_install=bool(args.allow_install), timeout_seconds=max(30, int(args.timeout_seconds)))
    json_path, txt_path = write_dependency_evidence(result, evidence_dir)
    print(f"PATCHOPS_UPLOADER_RUNTIME_DEPENDENCY_STATUS: {result.status}")
    print(f"PYTHON_EXECUTABLE: {result.python_executable}")
    for check in result.checks:
        print(f"PACKAGE: {check['package']}")
        print(f"IMPORT_NAME: {check['import_name']}")
        print(f"AVAILABLE_BEFORE: {str(check['available_before']).lower()}")
        print(f"INSTALL_ATTEMPTED: {str(check['install_attempted']).lower()}")
        print(f"INSTALL_EXIT_CODE: {check['install_exit_code']}")
        print(f"AVAILABLE_AFTER: {str(check['available_after']).lower()}")
        print(f"CHECK_STATUS: {check['status']}")
    print(f"JSON_EVIDENCE: {json_path}")
    print(f"TXT_EVIDENCE: {txt_path}")
    print("FILE_PATH_WRITTEN: false")
    print("FILE_SELECTED: false")
    print("OPEN_BUTTON_PRESSED: false")
    print("ATTACHMENT_CONFIRMED: false")
    print("CHATGPT_SUBMIT_PERFORMED: false")
    print("SELENIUM_USED: false")
    print("WEBDRIVER_USED: false")
    print("BROWSER_DOM_AUTOMATION_USED: false")
    return 0 if result.status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
