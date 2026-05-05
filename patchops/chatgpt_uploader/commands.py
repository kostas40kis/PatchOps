from __future__ import annotations

import json
from typing import Any

from .dependency_check import run_dependency_doctor
from .report_packager import build_safe_report_copy
from .safety_policy import assert_safe_no_side_effects


def doctor_payload(*, target_url: str) -> dict[str, Any]:
    result = run_dependency_doctor(target_url=target_url)
    assert_safe_no_side_effects(result.safety)
    return dict(result.to_payload())


def package_report_payload(*, report_path: str, staging_root: str | None = None) -> dict[str, Any]:
    candidate = build_safe_report_copy(report_path, staging_root=staging_root)
    return dict(candidate.to_payload())


def print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    """Small module CLI for tests/proofs.

    Full patchops.cli wiring is intentionally deferred to a later patch.
    """

    import argparse

    parser = argparse.ArgumentParser(prog="python -m patchops.chatgpt_uploader.commands")
    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor")
    doctor.add_argument("--target-url", required=True)

    package = sub.add_parser("package-report")
    package.add_argument("--report-path", required=True)
    package.add_argument("--staging-root")

    args = parser.parse_args(argv)

    if args.command == "doctor":
        print_json(doctor_payload(target_url=args.target_url))
        return 0

    if args.command == "package-report":
        print_json(package_report_payload(report_path=args.report_path, staging_root=args.staging_root))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
