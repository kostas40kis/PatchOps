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

# PATCHOPS_PATCH55_RELEASE_READINESS:START
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

REQUIRED_RELEASE_READINESS_DOCS = (
    "docs/release_checklist.md",
    "docs/stage1_freeze_checklist.md",
    "docs/project_status.md",
    "docs/patch_ledger.md",
)

REQUIRED_RELEASE_READINESS_EXAMPLES = (
    "examples/trader_first_doc_patch.json",
    "examples/trader_first_verify_patch.json",
    "examples/generic_python_patch.json",
    "examples/generic_verify_patch.json",
)

REQUIRED_RELEASE_READINESS_WORKFLOWS = (
    "patchops/cli.py",
    "patchops/readiness.py",
    "patchops/initial_milestone_gate.py",
    "patchops/workflows/verify_only.py",
    "patchops/workflows/wrapper_retry.py",
)

REQUIRED_RELEASE_READINESS_LAUNCHERS = (
    "powershell/Invoke-PatchManifest.ps1",
    "powershell/Invoke-PatchVerify.ps1",
    "powershell/Invoke-PatchWrapperRetry.ps1",
)


@dataclass(frozen=True)
class ReleaseReadinessSnapshot:
    status: str
    release_docs_ok: bool
    release_examples_ok: bool
    release_workflows_ok: bool
    release_launchers_ok: bool
    profiles_ok: bool
    core_tests_state: str
    missing_release_docs: tuple[str, ...]
    missing_release_examples: tuple[str, ...]
    missing_release_workflows: tuple[str, ...]
    missing_release_launchers: tuple[str, ...]
    missing_profiles: tuple[str, ...]
    issues: tuple[str, ...]


def _missing_release_paths(repo_root: str | Path, paths: Iterable[str]) -> tuple[str, ...]:
    root = Path(repo_root)
    missing = []
    for item in paths:
        if not (root / item).exists():
            missing.append(item)
    return tuple(missing)


def build_release_readiness_snapshot(
    repo_root: str | Path,
    available_profiles: Iterable[str],
    core_tests_state: str = "unknown",
) -> ReleaseReadinessSnapshot:
    if core_tests_state not in {"green", "unknown", "not_green"}:
        raise ValueError(
            "core_tests_state must be one of 'green', 'unknown', or 'not_green'."
        )

    missing_release_docs = _missing_release_paths(
        repo_root, REQUIRED_RELEASE_READINESS_DOCS
    )
    missing_release_examples = _missing_release_paths(
        repo_root, REQUIRED_RELEASE_READINESS_EXAMPLES
    )
    missing_release_workflows = _missing_release_paths(
        repo_root, REQUIRED_RELEASE_READINESS_WORKFLOWS
    )
    missing_release_launchers = _missing_release_paths(
        repo_root, REQUIRED_RELEASE_READINESS_LAUNCHERS
    )
    missing_profiles = _missing_profile_names(available_profiles)

    release_docs_ok = not missing_release_docs
    release_examples_ok = not missing_release_examples
    release_workflows_ok = not missing_release_workflows
    release_launchers_ok = not missing_release_launchers
    profiles_ok = not missing_profiles

    issues = []
    if not release_docs_ok:
        issues.append("missing release-readiness docs")
    if not release_examples_ok:
        issues.append("missing release-readiness examples")
    if not release_workflows_ok:
        issues.append("missing release-readiness workflow surfaces")
    if not release_launchers_ok:
        issues.append("missing release-readiness launchers")
    if not profiles_ok:
        issues.append("missing required profiles")
    if core_tests_state == "unknown":
        issues.append("core test state not provided")
    elif core_tests_state == "not_green":
        issues.append("core test surface is not green")

    static_surfaces_ok = (
        release_docs_ok
        and release_examples_ok
        and release_workflows_ok
        and release_launchers_ok
        and profiles_ok
    )

    if not static_surfaces_ok:
        status = "not_ready"
    elif core_tests_state == "green":
        status = "green"
    elif core_tests_state == "unknown":
        status = "review_required"
    else:
        status = "not_ready"

    return ReleaseReadinessSnapshot(
        status=status,
        release_docs_ok=release_docs_ok,
        release_examples_ok=release_examples_ok,
        release_workflows_ok=release_workflows_ok,
        release_launchers_ok=release_launchers_ok,
        profiles_ok=profiles_ok,
        core_tests_state=core_tests_state,
        missing_release_docs=missing_release_docs,
        missing_release_examples=missing_release_examples,
        missing_release_workflows=missing_release_workflows,
        missing_release_launchers=missing_release_launchers,
        missing_profiles=missing_profiles,
        issues=tuple(issues),
    )


def render_release_readiness_lines(
    snapshot: ReleaseReadinessSnapshot,
) -> tuple[str, ...]:
    return (
        "Surface     : release-readiness",
        f"Status      : {snapshot.status}",
        f"Docs        : {'ok' if snapshot.release_docs_ok else 'missing'}",
        f"Examples    : {'ok' if snapshot.release_examples_ok else 'missing'}",
        f"Workflows   : {'ok' if snapshot.release_workflows_ok else 'missing'}",
        f"Launchers   : {'ok' if snapshot.release_launchers_ok else 'missing'}",
        f"Profiles    : {'ok' if snapshot.profiles_ok else 'missing'}",
        f"Core Tests  : {snapshot.core_tests_state}",
        f"Issues      : {len(snapshot.issues)}",
    )


def release_readiness_as_dict(snapshot: ReleaseReadinessSnapshot) -> dict:
    payload = asdict(snapshot)
    payload["required_release_docs"] = REQUIRED_RELEASE_READINESS_DOCS
    payload["required_release_examples"] = REQUIRED_RELEASE_READINESS_EXAMPLES
    payload["required_release_workflows"] = REQUIRED_RELEASE_READINESS_WORKFLOWS
    payload["required_release_launchers"] = REQUIRED_RELEASE_READINESS_LAUNCHERS
    payload["recommended_commands"] = (
        "py -m pytest -q",
        "py -m patchops.cli profiles",
        "py -m patchops.cli doctor --profile trader",
        "py -m patchops.cli examples",
        "py -m patchops.cli schema",
        "py -m patchops.cli template --profile trader --mode apply --patch-name trader_stage1_template",
        "py -m patchops.cli check <manifest>",
        "py -m patchops.cli inspect <manifest>",
        "py -m patchops.cli plan <manifest>",
    )
    payload["scope_lines"] = list(render_release_readiness_lines(snapshot))
    payload["notes"] = (
        "This surface does not guess hidden state.",
        "Use --core-tests-green only when the green test state was already proven externally.",
    )
    return payload
# PATCHOPS_PATCH55_RELEASE_READINESS:END

# PATCHOPS_PATCH57_RELEASE_EVIDENCE:START
def _items_or_none(items: tuple[str, ...]) -> tuple[str, ...]:
    return items if items else ("(none)",)


def render_release_readiness_report_lines(
    snapshot: ReleaseReadinessSnapshot,
    wrapper_project_root: str | Path,
    focused_profile: str | None = None,
) -> tuple[str, ...]:
    wrapper_root = Path(wrapper_project_root).resolve()
    lines: list[str] = [
        "PATCHOPS RELEASE READINESS",
        "--------------------------",
        "Surface           : release-readiness",
        f"Wrapper Project   : {wrapper_root}",
        f"Focused Profile   : {focused_profile or '(none)'}",
        f"Status            : {snapshot.status}",
        f"Core Tests        : {snapshot.core_tests_state}",
        f"Docs              : {'ok' if snapshot.release_docs_ok else 'missing'}",
        f"Examples          : {'ok' if snapshot.release_examples_ok else 'missing'}",
        f"Workflows         : {'ok' if snapshot.release_workflows_ok else 'missing'}",
        f"Launchers         : {'ok' if snapshot.release_launchers_ok else 'missing'}",
        f"Profiles          : {'ok' if snapshot.profiles_ok else 'missing'}",
        f"Issues            : {len(snapshot.issues)}",
        "",
        "MISSING RELEASE DOCS",
        "--------------------",
        *_items_or_none(snapshot.missing_release_docs),
        "",
        "MISSING RELEASE EXAMPLES",
        "------------------------",
        *_items_or_none(snapshot.missing_release_examples),
        "",
        "MISSING RELEASE WORKFLOWS",
        "-------------------------",
        *_items_or_none(snapshot.missing_release_workflows),
        "",
        "MISSING RELEASE LAUNCHERS",
        "-------------------------",
        *_items_or_none(snapshot.missing_release_launchers),
        "",
        "MISSING PROFILES",
        "----------------",
        *_items_or_none(snapshot.missing_profiles),
        "",
        "ISSUES",
        "------",
        *_items_or_none(snapshot.issues),
        "",
        "RECOMMENDED COMMANDS",
        "--------------------",
        "py -m pytest -q",
        "py -m patchops.cli profiles",
        "py -m patchops.cli doctor --profile trader",
        "py -m patchops.cli examples",
        "py -m patchops.cli schema",
        "py -m patchops.cli template --profile trader --mode apply --patch-name trader_stage1_template",
        "py -m patchops.cli check <manifest>",
        "py -m patchops.cli inspect <manifest>",
        "py -m patchops.cli plan <manifest>",
        "",
        "NOTES",
        "-----",
        "This surface does not guess hidden state.",
        "Use --core-tests-green only when the green test state was already proven externally.",
    ]
    return tuple(lines)


def write_release_readiness_report(
    report_path: str | Path,
    snapshot: ReleaseReadinessSnapshot,
    wrapper_project_root: str | Path,
    focused_profile: str | None = None,
) -> str:
    path = Path(report_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(
        render_release_readiness_report_lines(
            snapshot,
            wrapper_project_root=wrapper_project_root,
            focused_profile=focused_profile,
        )
    ) + "\n"
    path.write_text(text, encoding="utf-8")
    return str(path)
# PATCHOPS_PATCH57_RELEASE_EVIDENCE:END
