from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REQUIRED_RELEASE_DOCS = (
    "docs/release_checklist.md",
    "docs/stage1_freeze_checklist.md",
    "docs/project_status.md",
    "docs/patch_ledger.md",
)

REQUIRED_RELEASE_EXAMPLES = (
    "examples/trader_first_doc_patch.json",
    "examples/trader_first_verify_patch.json",
    "examples/generic_python_patch.json",
    "examples/generic_verify_patch.json",
)

REQUIRED_RELEASE_WORKFLOWS = (
    "patchops/cli.py",
    "patchops/readiness.py",
    "patchops/initial_milestone_gate.py",
    "patchops/workflows/verify_only.py",
    "patchops/workflows/wrapper_retry.py",
)

REQUIRED_RELEASE_LAUNCHERS = (
    "powershell/Invoke-PatchManifest.ps1",
    "powershell/Invoke-PatchVerify.ps1",
    "powershell/Invoke-PatchWrapperRetry.ps1",
)

REQUIRED_RELEASE_TESTS = (
    "tests/test_release_readiness_command.py",
    "tests/test_powershell_readiness_launcher.py",
    "tests/test_profile_summary_command.py",
    "tests/test_powershell_launchers.py",
)

REQUIRED_RELEASE_PROFILES = (
    "trader",
    "generic_python",
    "generic_python_powershell",
)


@dataclass(frozen=True)
class ReleaseReadinessSnapshot:
    status: str
    core_tests_state: str
    release_docs_ok: bool
    release_examples_ok: bool
    release_workflows_ok: bool
    release_launchers_ok: bool
    release_tests_ok: bool
    profiles_ok: bool
    missing_release_docs: tuple[str, ...]
    missing_release_examples: tuple[str, ...]
    missing_release_workflows: tuple[str, ...]
    missing_release_launchers: tuple[str, ...]
    missing_release_tests: tuple[str, ...]
    missing_profiles: tuple[str, ...]
    issues: tuple[str, ...]


def _missing_paths(wrapper_root: Path, required: tuple[str, ...]) -> tuple[str, ...]:
    missing: list[str] = []
    for relative_path in required:
        if not (wrapper_root / relative_path).exists():
            missing.append(relative_path)
    return tuple(missing)


def _missing_profiles(available_profiles: list[str]) -> tuple[str, ...]:
    return tuple(name for name in REQUIRED_RELEASE_PROFILES if name not in available_profiles)


def build_release_readiness_snapshot(
    wrapper_project_root: str | Path,
    available_profiles: list[str],
    core_tests_state: str = "unknown",
) -> ReleaseReadinessSnapshot:
    wrapper_root = Path(wrapper_project_root).resolve()

    missing_release_docs = _missing_paths(wrapper_root, REQUIRED_RELEASE_DOCS)
    missing_release_examples = _missing_paths(wrapper_root, REQUIRED_RELEASE_EXAMPLES)
    missing_release_workflows = _missing_paths(wrapper_root, REQUIRED_RELEASE_WORKFLOWS)
    missing_release_launchers = _missing_paths(wrapper_root, REQUIRED_RELEASE_LAUNCHERS)
    missing_release_tests = _missing_paths(wrapper_root, REQUIRED_RELEASE_TESTS)
    missing_profiles = _missing_profiles(available_profiles)

    release_docs_ok = not missing_release_docs
    release_examples_ok = not missing_release_examples
    release_workflows_ok = not missing_release_workflows
    release_launchers_ok = not missing_release_launchers
    release_tests_ok = not missing_release_tests
    profiles_ok = not missing_profiles

    issues: list[str] = []
    if not release_docs_ok:
        issues.append("missing release docs")
    if not release_examples_ok:
        issues.append("missing release examples")
    if not release_workflows_ok:
        issues.append("missing release workflows")
    if not release_launchers_ok:
        issues.append("missing release launchers")
    if not release_tests_ok:
        issues.append("missing release tests")
    if not profiles_ok:
        issues.append("missing expected profiles")
    if core_tests_state != "green":
        if core_tests_state == "unknown":
            issues.append("core test state not provided")
        else:
            issues.append(f"core test state is {core_tests_state}")

    hard_missing = any(
        (
            not release_docs_ok,
            not release_examples_ok,
            not release_workflows_ok,
            not release_launchers_ok,
            not release_tests_ok,
            not profiles_ok,
        )
    )

    if hard_missing:
        status = "not_ready"
    elif core_tests_state == "green":
        status = "green"
    else:
        status = "review_required"

    return ReleaseReadinessSnapshot(
        status=status,
        core_tests_state=core_tests_state,
        release_docs_ok=release_docs_ok,
        release_examples_ok=release_examples_ok,
        release_workflows_ok=release_workflows_ok,
        release_launchers_ok=release_launchers_ok,
        release_tests_ok=release_tests_ok,
        profiles_ok=profiles_ok,
        missing_release_docs=missing_release_docs,
        missing_release_examples=missing_release_examples,
        missing_release_workflows=missing_release_workflows,
        missing_release_launchers=missing_release_launchers,
        missing_release_tests=missing_release_tests,
        missing_profiles=missing_profiles,
        issues=tuple(issues),
    )


def render_release_readiness_scope_lines(
    snapshot: ReleaseReadinessSnapshot,
) -> tuple[str, ...]:
    return (
        "Surface     : release-readiness",
        f"Status      : {snapshot.status}",
        f"CoreTests   : {snapshot.core_tests_state}",
        f"Docs        : {'ok' if snapshot.release_docs_ok else 'missing'}",
        f"Examples    : {'ok' if snapshot.release_examples_ok else 'missing'}",
        f"Workflows   : {'ok' if snapshot.release_workflows_ok else 'missing'}",
        f"Launchers   : {'ok' if snapshot.release_launchers_ok else 'missing'}",
        f"Tests       : {'ok' if snapshot.release_tests_ok else 'missing'}",
        f"Profiles    : {'ok' if snapshot.profiles_ok else 'missing'}",
        f"Issues      : {len(snapshot.issues)}",
    )


def release_readiness_as_dict(snapshot: ReleaseReadinessSnapshot) -> dict[str, object]:
    return {
        "status": snapshot.status,
        "core_tests_state": snapshot.core_tests_state,
        "release_docs_ok": snapshot.release_docs_ok,
        "release_examples_ok": snapshot.release_examples_ok,
        "release_workflows_ok": snapshot.release_workflows_ok,
        "release_launchers_ok": snapshot.release_launchers_ok,
        "release_tests_ok": snapshot.release_tests_ok,
        "profiles_ok": snapshot.profiles_ok,
        "missing_release_docs": list(snapshot.missing_release_docs),
        "missing_release_examples": list(snapshot.missing_release_examples),
        "missing_release_workflows": list(snapshot.missing_release_workflows),
        "missing_release_launchers": list(snapshot.missing_release_launchers),
        "missing_release_tests": list(snapshot.missing_release_tests),
        "missing_profiles": list(snapshot.missing_profiles),
        "issues": list(snapshot.issues),
        "scope_lines": list(render_release_readiness_scope_lines(snapshot)),
    }


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
        f"Tests             : {'ok' if snapshot.release_tests_ok else 'missing'}",
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
        "MISSING RELEASE TESTS",
        "---------------------",
        *_items_or_none(snapshot.missing_release_tests),
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