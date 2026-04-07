from __future__ import annotations

from dataclasses import dataclass


PACKAGE_AUTHORING_FAILURE = "package_authoring_failure"
WRAPPER_FAILURE = "wrapper_failure"
TARGET_CONTENT_FAILURE = "target_content_failure"
ENVIRONMENT_FAILURE = "environment_failure"
AMBIGUOUS_EVIDENCE = "ambiguous_evidence"


@dataclass(frozen=True)
class BundleFailureEvidence:
    launcher_started: bool
    inner_report_found: bool
    inner_failure_category: str | None = None
    inner_exit_code: int | None = None
    launcher_exit_code: int | None = None
    stderr: str = ""
    package_setup_error: str | None = None


@dataclass(frozen=True)
class BundleFailureClassification:
    category: str
    reason: str


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(item in lowered for item in needles)


def classify_bundle_run_failure(evidence: BundleFailureEvidence) -> BundleFailureClassification:
    stderr = evidence.stderr or ""
    package_setup_error = evidence.package_setup_error or ""

    if not evidence.launcher_started:
        package_text = f"{package_setup_error}\n{stderr}"
        if _contains_any(
            package_text,
            (
                "filenotfounderror",
                "no such file or directory",
                "package setup failed before launcher invocation",
                "bundle root",
                "launcher path",
                "manifest not found",
            ),
        ):
            return BundleFailureClassification(
                category=PACKAGE_AUTHORING_FAILURE,
                reason="Bundle setup failed before launcher invocation.",
            )
        if _contains_any(
            package_text,
            (
                "access is denied",
                "executionpolicy",
                "not recognized as an internal or external command",
                "python was not found",
                "powershell is not recognized",
            ),
        ):
            return BundleFailureClassification(
                category=ENVIRONMENT_FAILURE,
                reason="Environment prevented the bundle from starting.",
            )
        return BundleFailureClassification(
            category=AMBIGUOUS_EVIDENCE,
            reason="Launcher never started and the failing layer is not explicit.",
        )

    if evidence.inner_report_found and evidence.inner_failure_category:
        return BundleFailureClassification(
            category=evidence.inner_failure_category,
            reason="Inner report supplied the authoritative failure category.",
        )

    if _contains_any(
        stderr,
        (
            "argumentlist",
            "processstartinfo",
            "launcher",
            "patchops apply failed with exit code",
        ),
    ) and not evidence.inner_report_found:
        return BundleFailureClassification(
            category=WRAPPER_FAILURE,
            reason="Launcher execution failed before an authoritative inner report was produced.",
        )

    if _contains_any(
        stderr,
        (
            "access is denied",
            "executionpolicy",
            "not recognized as an internal or external command",
            "python was not found",
            "powershell is not recognized",
        ),
    ):
        return BundleFailureClassification(
            category=ENVIRONMENT_FAILURE,
            reason="Environment prevented the launched bundle workflow from completing.",
        )

    if evidence.inner_report_found and evidence.inner_exit_code not in (None, 0):
        return BundleFailureClassification(
            category=TARGET_CONTENT_FAILURE,
            reason="Inner report was present with a failing exit code but no explicit category.",
        )

    return BundleFailureClassification(
        category=AMBIGUOUS_EVIDENCE,
        reason="Available bundle-run evidence is not strong enough to identify the first failing layer.",
    )
