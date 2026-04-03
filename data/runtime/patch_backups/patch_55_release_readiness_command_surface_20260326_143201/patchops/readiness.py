from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


REQUIRED_INITIAL_MILESTONE_DOCS = (
    "README.md",
    "docs/project_status.md",
    "docs/llm_usage.md",
    "docs/examples.md",
    "docs/failure_repair_guide.md",
    "docs/operational_patch_types.md",
)

REQUIRED_INITIAL_MILESTONE_EXAMPLES = (
    "examples/trader_first_verify_patch.json",
    "examples/trader_code_patch.json",
    "examples/generic_python_patch.json",
    "examples/generic_verify_patch.json",
    "examples/generic_cleanup_archive_patch.json",
)

REQUIRED_INITIAL_MILESTONE_PROFILES = (
    "trader",
    "generic_python",
    "generic_python_powershell",
)

REQUIRED_INITIAL_MILESTONE_WORKFLOWS = (
    "patchops/workflows/cleanup.py",
    "patchops/workflows/archive.py",
    "patchops/workflows/verify_only.py",
)


@dataclass(frozen=True)
class InitialMilestoneReadiness:
    status: str
    docs_ok: bool
    examples_ok: bool
    profiles_ok: bool
    workflows_ok: bool
    core_tests_green: bool
    missing_docs: tuple[str, ...]
    missing_examples: tuple[str, ...]
    missing_profiles: tuple[str, ...]
    missing_workflows: tuple[str, ...]
    issues: tuple[str, ...]


def _missing_paths(repo_root: str | Path, paths: Iterable[str]) -> tuple[str, ...]:
    root = Path(repo_root)
    missing = []
    for item in paths:
        if not (root / item).exists():
            missing.append(item)
    return tuple(missing)


def _missing_profile_names(available_profiles: Iterable[str]) -> tuple[str, ...]:
    available = set(available_profiles)
    return tuple(
        profile for profile in REQUIRED_INITIAL_MILESTONE_PROFILES if profile not in available
    )


def build_initial_milestone_readiness(
    repo_root: str | Path,
    available_profiles: Iterable[str],
    core_tests_green: bool,
) -> InitialMilestoneReadiness:
    missing_docs = _missing_paths(repo_root, REQUIRED_INITIAL_MILESTONE_DOCS)
    missing_examples = _missing_paths(repo_root, REQUIRED_INITIAL_MILESTONE_EXAMPLES)
    missing_workflows = _missing_paths(repo_root, REQUIRED_INITIAL_MILESTONE_WORKFLOWS)
    missing_profiles = _missing_profile_names(available_profiles)

    docs_ok = not missing_docs
    examples_ok = not missing_examples
    workflows_ok = not missing_workflows
    profiles_ok = not missing_profiles

    issues = []
    if not docs_ok:
        issues.append("missing required docs")
    if not examples_ok:
        issues.append("missing required examples")
    if not profiles_ok:
        issues.append("missing required profiles")
    if not workflows_ok:
        issues.append("missing required workflows")
    if not core_tests_green:
        issues.append("core tests are not green")

    status = "green" if not issues else "not_ready"
    return InitialMilestoneReadiness(
        status=status,
        docs_ok=docs_ok,
        examples_ok=examples_ok,
        profiles_ok=profiles_ok,
        workflows_ok=workflows_ok,
        core_tests_green=core_tests_green,
        missing_docs=missing_docs,
        missing_examples=missing_examples,
        missing_profiles=missing_profiles,
        missing_workflows=missing_workflows,
        issues=tuple(issues),
    )


def render_initial_milestone_readiness_lines(
    readiness: InitialMilestoneReadiness,
) -> tuple[str, ...]:
    return (
        "Surface  : initial milestone readiness",
        f"Status   : {readiness.status}",
        f"Docs     : {'ok' if readiness.docs_ok else 'missing'}",
        f"Examples : {'ok' if readiness.examples_ok else 'missing'}",
        f"Profiles : {'ok' if readiness.profiles_ok else 'missing'}",
        f"Workflows: {'ok' if readiness.workflows_ok else 'missing'}",
        f"Tests    : {'green' if readiness.core_tests_green else 'not_green'}",
        f"Issues   : {len(readiness.issues)}",
    )


def readiness_is_green(readiness: InitialMilestoneReadiness) -> bool:
    return readiness.status == "green"


def readiness_as_dict(readiness: InitialMilestoneReadiness) -> dict:
    return asdict(readiness)
