from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence


PHASE_1_FOUNDATION_TEST_PATHS: tuple[str, ...] = (
    "tests/test_chain_execution_context.py",
    "tests/test_connector_capability_profile.py",
    "tests/test_order_style_capability_matrix.py",
    "tests/test_chain_reserve_policy_registry.py",
    "tests/test_chain_aware_route_score_inputs.py",
    "tests/test_chain_aware_mode_policy.py",
    "tests/test_multi_chain_provider_health_snapshot.py",
    "tests/test_connector_selection_policy.py",
    "tests/test_chain_support_validation.py",
)


class CrossChainFoundationSuiteRunnerError(ValueError):
    \"\"\"Raised when the named phase-1 suite receives invalid data.\"\"\"


def _normalize_text(value: Any, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise CrossChainFoundationSuiteRunnerError(f"{field_name} must be a non-empty string")
    return text


def _normalize_non_negative_int(value: Any, field_name: str) -> int:
    try:
        normalized = int(value)
    except (TypeError, ValueError) as exc:
        raise CrossChainFoundationSuiteRunnerError(f"{field_name} must be integer-like") from exc
    if normalized < 0:
        raise CrossChainFoundationSuiteRunnerError(f"{field_name} must be non-negative")
    return normalized


def _normalize_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    raise CrossChainFoundationSuiteRunnerError(f"{field_name} must be a mapping")


@dataclass(frozen=True)
class CrossChainFoundationSuiteDefinition:
    suite_name: str
    phase_name: str
    test_paths: tuple[str, ...]
    purpose: str

    def __post_init__(self) -> None:
        validate_cross_chain_foundation_suite_definition(self)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CrossChainFoundationSuiteSummary:
    suite_name: str
    phase_name: str
    total_test_modules: int
    passed_test_modules: int
    failed_test_modules: int
    test_paths: tuple[str, ...]
    result: str

    def __post_init__(self) -> None:
        validate_cross_chain_foundation_suite_summary(self)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_cross_chain_foundation_suite_definition(value: CrossChainFoundationSuiteDefinition) -> None:
    _normalize_text(value.suite_name, "suite_name")
    _normalize_text(value.phase_name, "phase_name")
    _normalize_text(value.purpose, "purpose")

    if not value.test_paths:
        raise CrossChainFoundationSuiteRunnerError("test_paths must not be empty")

    for path in value.test_paths:
        normalized_path = _normalize_text(path, "test_path")
        if not normalized_path.startswith("tests/"):
            raise CrossChainFoundationSuiteRunnerError(
                "test_paths must be project-relative pytest module paths under tests/"
            )


def validate_cross_chain_foundation_suite_summary(value: CrossChainFoundationSuiteSummary) -> None:
    _normalize_text(value.suite_name, "suite_name")
    _normalize_text(value.phase_name, "phase_name")
    total_test_modules = _normalize_non_negative_int(value.total_test_modules, "total_test_modules")
    passed_test_modules = _normalize_non_negative_int(value.passed_test_modules, "passed_test_modules")
    failed_test_modules = _normalize_non_negative_int(value.failed_test_modules, "failed_test_modules")
    result = _normalize_text(value.result, "result").upper()

    if result not in {"PASS", "FAIL"}:
        raise CrossChainFoundationSuiteRunnerError("result must be PASS or FAIL")

    if total_test_modules != len(value.test_paths):
        raise CrossChainFoundationSuiteRunnerError(
            "total_test_modules must equal len(test_paths)"
        )
    if passed_test_modules + failed_test_modules != total_test_modules:
        raise CrossChainFoundationSuiteRunnerError(
            "passed_test_modules + failed_test_modules must equal total_test_modules"
        )
    if result == "PASS" and failed_test_modules != 0:
        raise CrossChainFoundationSuiteRunnerError(
            "PASS summary cannot report failed test modules"
        )
    if result == "FAIL" and failed_test_modules == 0:
        raise CrossChainFoundationSuiteRunnerError(
            "FAIL summary must report at least one failed test module"
        )


def build_cross_chain_foundation_suite_definition() -> CrossChainFoundationSuiteDefinition:
    return CrossChainFoundationSuiteDefinition(
        suite_name="cross_chain_foundation_suite",
        phase_name="Phase 1 - Cross-chain execution substrate",
        test_paths=PHASE_1_FOUNDATION_TEST_PATHS,
        purpose="Provide one named rerunnable validation surface for the whole phase-1 cross-chain substrate.",
    )


def build_cross_chain_foundation_suite_summary(
    *,
    failed_test_paths: Sequence[str] | None = None,
) -> CrossChainFoundationSuiteSummary:
    definition = build_cross_chain_foundation_suite_definition()
    failed = tuple(_normalize_text(path, "failed_test_path") for path in (failed_test_paths or ()))

    invalid_failures = sorted(set(failed).difference(definition.test_paths))
    if invalid_failures:
        raise CrossChainFoundationSuiteRunnerError(
            f"failed_test_paths must be members of the suite; invalid {invalid_failures}"
        )

    failed_count = len(failed)
    total = len(definition.test_paths)
    passed_count = total - failed_count

    return CrossChainFoundationSuiteSummary(
        suite_name=definition.suite_name,
        phase_name=definition.phase_name,
        total_test_modules=total,
        passed_test_modules=passed_count,
        failed_test_modules=failed_count,
        test_paths=definition.test_paths,
        result="PASS" if failed_count == 0 else "FAIL",
    )


def render_cross_chain_foundation_suite_summary_lines(
    summary: CrossChainFoundationSuiteSummary | Mapping[str, Any],
) -> list[str]:
    if isinstance(summary, Mapping):
        payload = _normalize_mapping(summary, "summary")
        normalized = CrossChainFoundationSuiteSummary(
            suite_name=_normalize_text(payload.get("suite_name"), "suite_name"),
            phase_name=_normalize_text(payload.get("phase_name"), "phase_name"),
            total_test_modules=_normalize_non_negative_int(payload.get("total_test_modules"), "total_test_modules"),
            passed_test_modules=_normalize_non_negative_int(payload.get("passed_test_modules"), "passed_test_modules"),
            failed_test_modules=_normalize_non_negative_int(payload.get("failed_test_modules"), "failed_test_modules"),
            test_paths=tuple(payload.get("test_paths") or ()),
            result=_normalize_text(payload.get("result"), "result").upper(),
        )
    else:
        normalized = summary

    return [
        "CROSS CHAIN FOUNDATION SUITE",
        f"Suite name: {normalized.suite_name}",
        f"Phase: {normalized.phase_name}",
        f"Total test modules: {normalized.total_test_modules}",
        f"Passed test modules: {normalized.passed_test_modules}",
        f"Failed test modules: {normalized.failed_test_modules}",
        f"Result: {normalized.result}",
        "Test paths:",
        *[f"- {path}" for path in normalized.test_paths],
    ]


def render_cross_chain_foundation_suite_summary_text(
    summary: CrossChainFoundationSuiteSummary | Mapping[str, Any],
) -> str:
    return "\\n".join(render_cross_chain_foundation_suite_summary_lines(summary))


__all__ = [
    "PHASE_1_FOUNDATION_TEST_PATHS",
    "CrossChainFoundationSuiteDefinition",
    "CrossChainFoundationSuiteRunnerError",
    "CrossChainFoundationSuiteSummary",
    "build_cross_chain_foundation_suite_definition",
    "build_cross_chain_foundation_suite_summary",
    "render_cross_chain_foundation_suite_summary_lines",
    "render_cross_chain_foundation_suite_summary_text",
    "validate_cross_chain_foundation_suite_definition",
    "validate_cross_chain_foundation_suite_summary",
]