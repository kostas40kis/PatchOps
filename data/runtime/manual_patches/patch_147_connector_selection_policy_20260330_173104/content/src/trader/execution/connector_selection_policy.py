from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Sequence

from src.trader.execution.chain_execution_context import (
    ChainExecutionContext,
    normalize_chain_execution_context,
)
from src.trader.execution.connector_capability_profile import (
    ConnectorCapabilityProfile,
    normalize_connector_capability_profile,
)
from src.trader.execution.multi_chain_provider_health_snapshot import (
    MultiChainProviderHealthSnapshot,
    normalize_multi_chain_provider_health_snapshot,
    provider_health_block_reason,
)


class ConnectorSelectionPolicyError(ValueError):
    """Raised when connector selection inputs are invalid."""


def _normalize_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    raise ConnectorSelectionPolicyError(f"{field_name} must be a mapping")


def _normalize_text(value: Any, field_name: str) -> str:
    text = str(value or "").strip().lower()
    if not text:
        raise ConnectorSelectionPolicyError(f"{field_name} must be a non-empty string")
    return text


def _normalize_bool(value: Any, field_name: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes"}:
            return True
        if lowered in {"false", "0", "no"}:
            return False
    raise ConnectorSelectionPolicyError(f"{field_name} must be boolean-like")


def render_connector_selection_result_id(
    *,
    context: Any,
    selected_provider_key: str | None,
) -> str:
    normalized_context = normalize_chain_execution_context(context)
    provider_key = "blocked"
    if selected_provider_key is not None:
        provider_key = _normalize_text(selected_provider_key, "selected_provider_key")
    return ":".join(
        [
            normalized_context.chain,
            normalized_context.execution_venue,
            provider_key,
            "connector_selection",
        ]
    )


@dataclass(frozen=True)
class ConnectorSelectionCandidate:
    chain_context: ChainExecutionContext
    connector_profile: ConnectorCapabilityProfile
    provider_health_snapshot: MultiChainProviderHealthSnapshot

    def __post_init__(self) -> None:
        validate_connector_selection_candidate(self)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chain_context": self.chain_context.to_dict(),
            "connector_profile": self.connector_profile.to_dict(),
            "provider_health_snapshot": self.provider_health_snapshot.to_dict(),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "ConnectorSelectionCandidate":
        return normalize_connector_selection_candidate(payload)


@dataclass(frozen=True)
class ConnectorSelectionResult:
    selection_id: str
    chain_context: ChainExecutionContext
    selected_provider_key: str | None
    selected_connector_key: str | None
    selected_execution_venue: str | None
    decision_reason_codes: tuple[str, ...] = field(default_factory=tuple)
    rejected_candidates: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    block_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "selection_id": self.selection_id,
            "chain_context": self.chain_context.to_dict(),
            "selected_provider_key": self.selected_provider_key,
            "selected_connector_key": self.selected_connector_key,
            "selected_execution_venue": self.selected_execution_venue,
            "decision_reason_codes": list(self.decision_reason_codes),
            "rejected_candidates": list(self.rejected_candidates),
            "block_reason": self.block_reason,
        }


def validate_connector_selection_candidate(value: ConnectorSelectionCandidate) -> None:
    context = normalize_chain_execution_context(value.chain_context)
    profile = normalize_connector_capability_profile(value.connector_profile)
    snapshot = normalize_multi_chain_provider_health_snapshot(value.provider_health_snapshot)

    if context.chain != profile.chain:
        raise ConnectorSelectionPolicyError(
            "candidate connector profile chain does not match context chain"
        )
    if context.execution_venue != profile.execution_venue:
        raise ConnectorSelectionPolicyError(
            "candidate connector profile execution_venue does not match context execution_venue"
        )
    if context.connector_key != profile.connector_key:
        raise ConnectorSelectionPolicyError(
            "candidate connector profile connector_key does not match context connector_key"
        )

    if context.chain != snapshot.chain_context.chain:
        raise ConnectorSelectionPolicyError(
            "candidate provider health snapshot chain does not match context chain"
        )
    if context.execution_venue != snapshot.chain_context.execution_venue:
        raise ConnectorSelectionPolicyError(
            "candidate provider health snapshot execution_venue does not match context execution_venue"
        )
    if context.connector_key != snapshot.chain_context.connector_key:
        raise ConnectorSelectionPolicyError(
            "candidate provider health snapshot connector_key does not match context connector_key"
        )


def normalize_connector_selection_candidate(value: Any) -> ConnectorSelectionCandidate:
    if isinstance(value, ConnectorSelectionCandidate):
        return value

    payload = _normalize_mapping(value, "value")
    return ConnectorSelectionCandidate(
        chain_context=normalize_chain_execution_context(payload.get("chain_context")),
        connector_profile=normalize_connector_capability_profile(payload.get("connector_profile")),
        provider_health_snapshot=normalize_multi_chain_provider_health_snapshot(payload.get("provider_health_snapshot")),
    )


def _candidate_sort_key(candidate: ConnectorSelectionCandidate) -> tuple[int, float, int, str]:
    snapshot = candidate.provider_health_snapshot
    status_rank = {
        "healthy": 0,
        "degraded": 1,
        "stale": 2,
        "unhealthy": 3,
    }[snapshot.status]
    return (
        status_rank,
        float(snapshot.latency_ms),
        int(snapshot.freshness_ms),
        str(snapshot.provider_key).lower(),
    )


def _reject_record(candidate: ConnectorSelectionCandidate, reason_code: str) -> dict[str, Any]:
    return {
        "provider_key": candidate.provider_health_snapshot.provider_key,
        "connector_key": candidate.connector_profile.connector_key,
        "execution_venue": candidate.connector_profile.execution_venue,
        "reason_code": reason_code,
    }


def build_connector_selection_result(
    *,
    chain_context: Any,
    candidates: Sequence[Any],
    max_freshness_ms: int | None = None,
    allow_degraded: bool = False,
) -> ConnectorSelectionResult:
    context = normalize_chain_execution_context(chain_context)
    normalized_candidates = [normalize_connector_selection_candidate(candidate) for candidate in candidates]

    rejected: list[dict[str, Any]] = []
    usable: list[ConnectorSelectionCandidate] = []

    for candidate in normalized_candidates:
        validate_connector_selection_candidate(candidate)

        block_reason = provider_health_block_reason(
            candidate.provider_health_snapshot,
            max_freshness_ms=max_freshness_ms,
            allow_degraded=allow_degraded,
        )
        if block_reason is not None:
            rejected.append(_reject_record(candidate, block_reason))
            continue

        usable.append(candidate)

    if not usable:
        selection_id = render_connector_selection_result_id(
            context=context,
            selected_provider_key=None,
        )
        block_reason = "no_usable_connector_candidate"
        if len(rejected) == 1:
            block_reason = str(rejected[0]["reason_code"])
        return ConnectorSelectionResult(
            selection_id=selection_id,
            chain_context=context,
            selected_provider_key=None,
            selected_connector_key=None,
            selected_execution_venue=None,
            decision_reason_codes=(block_reason,),
            rejected_candidates=tuple(rejected),
            block_reason=block_reason,
        )

    selected = sorted(usable, key=_candidate_sort_key)[0]
    reason_codes = ["deterministic_best_candidate_selected"]
    if selected.provider_health_snapshot.status == "degraded":
        reason_codes.append("degraded_allowed_by_policy")

    for candidate in usable:
        if candidate.provider_health_snapshot.provider_key == selected.provider_health_snapshot.provider_key:
            continue
        rejected.append(_reject_record(candidate, "lower_ranked_candidate"))

    selection_id = render_connector_selection_result_id(
        context=context,
        selected_provider_key=selected.provider_health_snapshot.provider_key,
    )

    return ConnectorSelectionResult(
        selection_id=selection_id,
        chain_context=context,
        selected_provider_key=selected.provider_health_snapshot.provider_key,
        selected_connector_key=selected.connector_profile.connector_key,
        selected_execution_venue=selected.connector_profile.execution_venue,
        decision_reason_codes=tuple(reason_codes),
        rejected_candidates=tuple(rejected),
        block_reason=None,
    )


__all__ = [
    "ConnectorSelectionCandidate",
    "ConnectorSelectionPolicyError",
    "ConnectorSelectionResult",
    "build_connector_selection_result",
    "normalize_connector_selection_candidate",
    "render_connector_selection_result_id",
    "validate_connector_selection_candidate",
]