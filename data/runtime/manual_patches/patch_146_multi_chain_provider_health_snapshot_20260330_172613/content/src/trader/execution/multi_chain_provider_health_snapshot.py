from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from src.trader.execution.chain_execution_context import (
    ChainExecutionContext,
    normalize_chain_execution_context,
)


SUPPORTED_PROVIDER_HEALTH_STATUSES = frozenset(
    {"healthy", "degraded", "unhealthy", "stale"}
)


class MultiChainProviderHealthSnapshotError(ValueError):
    """Raised when multi-chain provider health snapshot data is invalid."""


def _normalize_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    raise MultiChainProviderHealthSnapshotError(f"{field_name} must be a mapping")


def _normalize_text(value: Any, field_name: str) -> str:
    text = str(value or "").strip().lower()
    if not text:
        raise MultiChainProviderHealthSnapshotError(f"{field_name} must be a non-empty string")
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
    raise MultiChainProviderHealthSnapshotError(f"{field_name} must be boolean-like")


def _normalize_non_negative_float(value: Any, field_name: str) -> float:
    try:
        normalized = float(value)
    except (TypeError, ValueError) as exc:
        raise MultiChainProviderHealthSnapshotError(f"{field_name} must be numeric") from exc
    if normalized < 0:
        raise MultiChainProviderHealthSnapshotError(f"{field_name} must be non-negative")
    return normalized


def _normalize_non_negative_int(value: Any, field_name: str) -> int:
    try:
        normalized = int(value)
    except (TypeError, ValueError) as exc:
        raise MultiChainProviderHealthSnapshotError(f"{field_name} must be integer-like") from exc
    if normalized < 0:
        raise MultiChainProviderHealthSnapshotError(f"{field_name} must be non-negative")
    return normalized


def render_multi_chain_provider_health_snapshot_id(
    *,
    context: Any,
    provider_key: str,
) -> str:
    normalized_context = normalize_chain_execution_context(context)
    normalized_provider_key = _normalize_text(provider_key, "provider_key")
    return ":".join(
        [
            normalized_context.chain,
            normalized_context.execution_venue,
            normalized_provider_key,
            "provider_health",
        ]
    )


@dataclass(frozen=True)
class MultiChainProviderHealthSnapshot:
    snapshot_id: str
    chain_context: ChainExecutionContext
    provider_key: str
    status: str
    observed_at_epoch_ms: int
    last_success_epoch_ms: int
    latency_ms: float
    freshness_ms: int
    provider_healthy: bool
    degraded_reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        validate_multi_chain_provider_health_snapshot(self)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["chain_context"] = self.chain_context.to_dict()
        return payload

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "MultiChainProviderHealthSnapshot":
        return normalize_multi_chain_provider_health_snapshot(payload)


def validate_multi_chain_provider_health_snapshot(value: MultiChainProviderHealthSnapshot) -> None:
    normalized_context = normalize_chain_execution_context(value.chain_context)
    provider_key = _normalize_text(value.provider_key, "provider_key")
    status = _normalize_text(value.status, "status")

    if not provider_key:
        raise MultiChainProviderHealthSnapshotError("provider_key must be a non-empty string")
    if status not in SUPPORTED_PROVIDER_HEALTH_STATUSES:
        raise MultiChainProviderHealthSnapshotError(
            f"status must be one of {sorted(SUPPORTED_PROVIDER_HEALTH_STATUSES)}"
        )

    observed_at_epoch_ms = _normalize_non_negative_int(
        value.observed_at_epoch_ms,
        "observed_at_epoch_ms",
    )
    last_success_epoch_ms = _normalize_non_negative_int(
        value.last_success_epoch_ms,
        "last_success_epoch_ms",
    )
    latency_ms = _normalize_non_negative_float(value.latency_ms, "latency_ms")
    freshness_ms = _normalize_non_negative_int(value.freshness_ms, "freshness_ms")
    provider_healthy = _normalize_bool(value.provider_healthy, "provider_healthy")

    if last_success_epoch_ms > observed_at_epoch_ms:
        raise MultiChainProviderHealthSnapshotError(
            "last_success_epoch_ms must be <= observed_at_epoch_ms"
        )

    if freshness_ms != observed_at_epoch_ms - last_success_epoch_ms:
        raise MultiChainProviderHealthSnapshotError(
            "freshness_ms must equal observed_at_epoch_ms - last_success_epoch_ms"
        )

    if status == "healthy" and not provider_healthy:
        raise MultiChainProviderHealthSnapshotError(
            "provider_healthy must be true when status is healthy"
        )

    if status in {"unhealthy", "stale"} and provider_healthy:
        raise MultiChainProviderHealthSnapshotError(
            "provider_healthy must be false when status is unhealthy or stale"
        )

    if status == "degraded" and not (value.degraded_reason and str(value.degraded_reason).strip()):
        raise MultiChainProviderHealthSnapshotError(
            "degraded_reason must be present when status is degraded"
        )

    _ = normalized_context


def normalize_multi_chain_provider_health_snapshot(value: Any) -> MultiChainProviderHealthSnapshot:
    if isinstance(value, MultiChainProviderHealthSnapshot):
        return value

    payload = _normalize_mapping(value, "value")
    normalized_context = normalize_chain_execution_context(payload.get("chain_context"))

    observed_at_epoch_ms = _normalize_non_negative_int(
        payload.get("observed_at_epoch_ms"),
        "observed_at_epoch_ms",
    )
    last_success_epoch_ms = _normalize_non_negative_int(
        payload.get("last_success_epoch_ms"),
        "last_success_epoch_ms",
    )
    freshness_ms = payload.get("freshness_ms")
    if freshness_ms is None:
        freshness_ms = observed_at_epoch_ms - last_success_epoch_ms

    provider_key = _normalize_text(payload.get("provider_key"), "provider_key")
    status = _normalize_text(payload.get("status"), "status")

    snapshot_id = str(
        payload.get("snapshot_id")
        or render_multi_chain_provider_health_snapshot_id(
            context=normalized_context,
            provider_key=provider_key,
        )
    )

    return MultiChainProviderHealthSnapshot(
        snapshot_id=snapshot_id,
        chain_context=normalized_context,
        provider_key=provider_key,
        status=status,
        observed_at_epoch_ms=observed_at_epoch_ms,
        last_success_epoch_ms=last_success_epoch_ms,
        latency_ms=_normalize_non_negative_float(payload.get("latency_ms", 0.0), "latency_ms"),
        freshness_ms=_normalize_non_negative_int(freshness_ms, "freshness_ms"),
        provider_healthy=_normalize_bool(payload.get("provider_healthy"), "provider_healthy"),
        degraded_reason=payload.get("degraded_reason"),
        metadata=dict(payload.get("metadata") or {}),
    )


def build_multi_chain_provider_health_snapshot(
    *,
    chain_context: Any,
    provider_key: str,
    status: str,
    observed_at_epoch_ms: int,
    last_success_epoch_ms: int,
    latency_ms: float,
    degraded_reason: str | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> MultiChainProviderHealthSnapshot:
    normalized_context = normalize_chain_execution_context(chain_context)
    normalized_status = _normalize_text(status, "status")

    return normalize_multi_chain_provider_health_snapshot(
        {
            "chain_context": normalized_context,
            "provider_key": provider_key,
            "status": normalized_status,
            "observed_at_epoch_ms": observed_at_epoch_ms,
            "last_success_epoch_ms": last_success_epoch_ms,
            "latency_ms": latency_ms,
            "freshness_ms": int(observed_at_epoch_ms) - int(last_success_epoch_ms),
            "provider_healthy": normalized_status == "healthy",
            "degraded_reason": degraded_reason,
            "metadata": dict(metadata or {}),
        }
    )


def validate_context_against_provider_health_snapshot(
    context: Any,
    snapshot: Any,
) -> None:
    normalized_context = normalize_chain_execution_context(context)
    normalized_snapshot = normalize_multi_chain_provider_health_snapshot(snapshot)

    if normalized_context.chain != normalized_snapshot.chain_context.chain:
        raise MultiChainProviderHealthSnapshotError(
            "context chain does not match provider health snapshot chain"
        )
    if normalized_context.execution_venue != normalized_snapshot.chain_context.execution_venue:
        raise MultiChainProviderHealthSnapshotError(
            "context execution_venue does not match provider health snapshot execution_venue"
        )
    if normalized_context.connector_key != normalized_snapshot.chain_context.connector_key:
        raise MultiChainProviderHealthSnapshotError(
            "context connector_key does not match provider health snapshot connector_key"
        )


def provider_health_block_reason(
    snapshot: Any,
    *,
    max_freshness_ms: int | None = None,
    allow_degraded: bool = False,
) -> str | None:
    normalized_snapshot = normalize_multi_chain_provider_health_snapshot(snapshot)

    if max_freshness_ms is not None and normalized_snapshot.freshness_ms > int(max_freshness_ms):
        return "provider_health_freshness_expired"

    if normalized_snapshot.status == "healthy":
        return None

    if normalized_snapshot.status == "degraded":
        if allow_degraded:
            return None
        return "provider_health_degraded"

    if normalized_snapshot.status == "stale":
        return "provider_health_stale"

    return "provider_health_unhealthy"


def provider_health_is_usable(
    snapshot: Any,
    *,
    max_freshness_ms: int | None = None,
    allow_degraded: bool = False,
) -> bool:
    return provider_health_block_reason(
        snapshot,
        max_freshness_ms=max_freshness_ms,
        allow_degraded=allow_degraded,
    ) is None


__all__ = [
    "SUPPORTED_PROVIDER_HEALTH_STATUSES",
    "MultiChainProviderHealthSnapshot",
    "MultiChainProviderHealthSnapshotError",
    "build_multi_chain_provider_health_snapshot",
    "normalize_multi_chain_provider_health_snapshot",
    "provider_health_block_reason",
    "provider_health_is_usable",
    "render_multi_chain_provider_health_snapshot_id",
    "validate_context_against_provider_health_snapshot",
    "validate_multi_chain_provider_health_snapshot",
]