from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from patchops.readiness import (
    REQUIRED_INITIAL_MILESTONE_DOCS,
    REQUIRED_INITIAL_MILESTONE_EXAMPLES,
    REQUIRED_INITIAL_MILESTONE_PROFILES,
    REQUIRED_INITIAL_MILESTONE_WORKFLOWS,
    InitialMilestoneReadiness,
    build_initial_milestone_readiness,
    readiness_is_green,
)


REQUIRED_INITIAL_MILESTONE_TESTS = (
    "tests/test_readiness_surface.py",
    "tests/test_end_to_end_sample_suite.py",
    "tests/test_cleanup_archive_integration.py",
    "tests/test_operational_patch_types_doc.py",
    "tests/test_cleanup_workflow.py",
    "tests/test_archive_workflow.py",
    "tests/test_verify_only_flow.py",
    "tests/test_wrapper_retry.py",
)

REQUIRED_ARCHITECTURE_SENTINELS = (
    "patchops/manifest.py",
    "patchops/profiles/trader.py",
    "patchops/profiles/generic_python.py",
    "patchops/profiles/generic_python_powershell.py",
    "patchops/workflows/verify_only.py",
    "patchops/workflows/cleanup.py",
    "patchops/workflows/archive.py",
    "patchops/workflows/wrapper_retry.py",
    "patchops/readiness.py",
    "powershell/Invoke-PatchVerify.ps1",
)


@dataclass(frozen=True)
class InitialMilestoneGate:
    status: str
    readiness: InitialMilestoneReadiness
    tests_ok: bool
    architecture_ok: bool
    core_tests_green: bool
    missing_tests: tuple[str, ...]
    missing_architecture: tuple[str, ...]
    issues: tuple[str, ...]


def _missing_paths(repo_root: str | Path, paths: Iterable[str]) -> tuple[str, ...]:
    root = Path(repo_root)
    missing = []
    for item in paths:
        if not (root / item).exists():
            missing.append(item)
    return tuple(missing)


def build_initial_milestone_gate(
    repo_root: str | Path,
    available_profiles: Iterable[str],
    core_tests_green: bool,
) -> InitialMilestoneGate:
    readiness = build_initial_milestone_readiness(
        repo_root,
        available_profiles=available_profiles,
        core_tests_green=core_tests_green,
    )
    missing_tests = _missing_paths(repo_root, REQUIRED_INITIAL_MILESTONE_TESTS)
    missing_architecture = _missing_paths(repo_root, REQUIRED_ARCHITECTURE_SENTINELS)
    tests_ok = not missing_tests
    architecture_ok = not missing_architecture

    issues = list(readiness.issues)
    if not tests_ok:
        issues.append("missing required tests")
    if not architecture_ok:
        issues.append("major architecture drift detected")

    status = "complete" if readiness_is_green(readiness) and tests_ok and architecture_ok else "not_ready"
    return InitialMilestoneGate(
        status=status,
        readiness=readiness,
        tests_ok=tests_ok,
        architecture_ok=architecture_ok,
        core_tests_green=core_tests_green,
        missing_tests=missing_tests,
        missing_architecture=missing_architecture,
        issues=tuple(issues),
    )


def render_initial_milestone_gate_lines(gate: InitialMilestoneGate) -> tuple[str, ...]:
    return (
        "Surface  : final initial milestone gate",
        f"Status   : {gate.status}",
        f"Readiness: {'green' if readiness_is_green(gate.readiness) else 'not_ready'}",
        f"Tests    : {'ok' if gate.tests_ok else 'missing'}",
        f"Arch     : {'ok' if gate.architecture_ok else 'drift'}",
        f"Core     : {'green' if gate.core_tests_green else 'not_green'}",
        f"Issues   : {len(gate.issues)}",
    )


def initial_milestone_is_complete(gate: InitialMilestoneGate) -> bool:
    return gate.status == "complete"


def initial_milestone_gate_as_dict(gate: InitialMilestoneGate) -> dict:
    payload = asdict(gate)
    payload["readiness_status"] = gate.readiness.status
    payload["required_docs"] = REQUIRED_INITIAL_MILESTONE_DOCS
    payload["required_examples"] = REQUIRED_INITIAL_MILESTONE_EXAMPLES
    payload["required_profiles"] = REQUIRED_INITIAL_MILESTONE_PROFILES
    payload["required_workflows"] = REQUIRED_INITIAL_MILESTONE_WORKFLOWS
    payload["required_tests"] = REQUIRED_INITIAL_MILESTONE_TESTS
    payload["required_architecture_sentinels"] = REQUIRED_ARCHITECTURE_SENTINELS
    return payload
