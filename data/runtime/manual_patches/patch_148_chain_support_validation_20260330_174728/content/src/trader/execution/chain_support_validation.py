from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from src.trader.execution.chain_execution_context import normalize_chain_execution_context
from src.trader.execution.connector_capability_profile import normalize_connector_capability_profile
from src.trader.execution.order_style_capability_matrix import (
    order_style_is_supported,
    normalize_order_style_capability_matrix,
)
from src.trader.execution.chain_reserve_policy_registry import (
    normalize_chain_reserve_policy,
    native_balance_satisfies_reserve,
)
from src.trader.execution.multi_chain_provider_health_snapshot import (
    normalize_multi_chain_provider_health_snapshot,
    provider_health_block_reason,
)


SUPPORTED_ACTION_TYPES = frozenset(
    {"quote_only", "marketable_execution", "synthetic_monitored_exit", "native_limit_order", "native_stop_order"}
)


class ChainSupportValidationError(ValueError):
    """Raised when chain-support validation inputs are malformed."""


def _normalize_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    raise ChainSupportValidationError(f"{field_name} must be a mapping")


def _normalize_text(value: Any, field_name: str) -> str:
    text = str(value or "").strip().lower()
    if not text:
        raise ChainSupportValidationError(f"{field_name} must be a non-empty string")
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
    raise ChainSupportValidationError(f"{field_name} must be boolean-like")


def _normalize_non_negative_float(value: Any, field_name: str) -> float:
    try:
        normalized = float(value)
    except (TypeError, ValueError) as exc:
        raise ChainSupportValidationError(f"{field_name} must be numeric") from exc
    if normalized < 0:
        raise ChainSupportValidationError(f"{field_name} must be non-negative")
    return normalized


@dataclass(frozen=True)
class ChainSupportValidationResult:
    validation_id: str
    is_supported: bool
    action_type: str
    reason_codes: tuple[str, ...] = field(default_factory=tuple)
    block_reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def render_chain_support_validation_id(
    *,
    chain: str,
    execution_venue: str,
    action_type: str,
) -> str:
    return ":".join(
        [
            _normalize_text(chain, "chain"),
            _normalize_text(execution_venue, "execution_venue"),
            _normalize_text(action_type, "action_type"),
            "chain_support_validation",
        ]
    )


def validate_chain_support_request(
    *,
    chain_context: Any,
    connector_profile: Any,
    order_style_matrix: Any,
    reserve_policy: Any,
    provider_health_snapshot: Any,
    action_type: str,
    available_native_balance: Any,
    max_health_freshness_ms: int | None = None,
    allow_degraded_provider: bool = False,
) -> ChainSupportValidationResult:
    context = normalize_chain_execution_context(chain_context)
    profile = normalize_connector_capability_profile(connector_profile)
    matrix = normalize_order_style_capability_matrix(order_style_matrix)
    reserve_policy_obj = normalize_chain_reserve_policy(reserve_policy)
    snapshot = normalize_multi_chain_provider_health_snapshot(provider_health_snapshot)

    normalized_action_type = _normalize_text(action_type, "action_type")
    if normalized_action_type not in SUPPORTED_ACTION_TYPES:
        raise ChainSupportValidationError(
            f"action_type must be one of {sorted(SUPPORTED_ACTION_TYPES)}"
        )

    balance = _normalize_non_negative_float(available_native_balance, "available_native_balance")
    _normalize_bool(allow_degraded_provider, "allow_degraded_provider")

    reason_codes: list[str] = []

    if context.chain != profile.chain:
        reason_codes.append("unsupported_chain_profile_mismatch")
    if context.execution_venue != profile.execution_venue:
        reason_codes.append("unsupported_execution_venue_profile_mismatch")
    if context.connector_key != profile.connector_key:
        reason_codes.append("unsupported_connector_profile_mismatch")

    if context.chain != matrix.chain:
        reason_codes.append("unsupported_chain_order_style_matrix_mismatch")
    if context.execution_venue != matrix.execution_venue:
        reason_codes.append("unsupported_execution_venue_order_style_matrix_mismatch")
    if context.connector_key != matrix.connector_key:
        reason_codes.append("unsupported_connector_order_style_matrix_mismatch")

    if context.chain != reserve_policy_obj.chain:
        reason_codes.append("unsupported_chain_reserve_policy_mismatch")

    if context.chain != snapshot.chain_context.chain:
        reason_codes.append("unsupported_chain_provider_health_mismatch")
    if context.execution_venue != snapshot.chain_context.execution_venue:
        reason_codes.append("unsupported_execution_venue_provider_health_mismatch")
    if context.connector_key != snapshot.chain_context.connector_key:
        reason_codes.append("unsupported_connector_provider_health_mismatch")

    provider_block_reason = provider_health_block_reason(
        snapshot,
        max_freshness_ms=max_health_freshness_ms,
        allow_degraded=allow_degraded_provider,
    )
    if provider_block_reason is not None:
        reason_codes.append(provider_block_reason)

    if not native_balance_satisfies_reserve(balance, reserve_policy_obj):
        reason_codes.append("insufficient_native_reserve")

    if normalized_action_type != "quote_only":
        if normalized_action_type == "marketable_execution":
            if not profile.supports_marketable_execution:
                reason_codes.append("unsupported_marketable_execution")
        elif normalized_action_type == "synthetic_monitored_exit":
            if not order_style_is_supported(matrix, "synthetic_monitored_exit"):
                reason_codes.append("unsupported_synthetic_monitored_exit")
        elif normalized_action_type == "native_limit_order":
            if not order_style_is_supported(matrix, "native_limit_order"):
                reason_codes.append("unsupported_native_limit_order")
        elif normalized_action_type == "native_stop_order":
            if not order_style_is_supported(matrix, "native_stop_order"):
                reason_codes.append("unsupported_native_stop_order")

    is_supported = len(reason_codes) == 0
    block_reason = None if is_supported else reason_codes[0]

    return ChainSupportValidationResult(
        validation_id=render_chain_support_validation_id(
            chain=context.chain,
            execution_venue=context.execution_venue,
            action_type=normalized_action_type,
        ),
        is_supported=is_supported,
        action_type=normalized_action_type,
        reason_codes=tuple(reason_codes),
        block_reason=block_reason,
        metadata={
            "chain": context.chain,
            "execution_venue": context.execution_venue,
            "connector_key": context.connector_key,
        },
    )


def chain_support_is_allowed(**kwargs: Any) -> bool:
    return validate_chain_support_request(**kwargs).is_supported


def require_chain_support(**kwargs: Any) -> ChainSupportValidationResult:
    result = validate_chain_support_request(**kwargs)
    if not result.is_supported:
        raise ChainSupportValidationError(
            f"unsupported chain/venue/order-style combination: {result.block_reason}"
        )
    return result


__all__ = [
    "SUPPORTED_ACTION_TYPES",
    "ChainSupportValidationError",
    "ChainSupportValidationResult",
    "chain_support_is_allowed",
    "render_chain_support_validation_id",
    "require_chain_support",
    "validate_chain_support_request",
]