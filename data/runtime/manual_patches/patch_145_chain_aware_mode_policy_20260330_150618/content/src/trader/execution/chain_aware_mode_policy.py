from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from src.trader.execution.chain_aware_route_score_inputs import (
    ChainAwareRouteScoreInputs,
    normalize_chain_aware_route_score_inputs,
)
from src.trader.execution.chain_execution_context import (
    SUPPORTED_CHAINS,
    ChainExecutionContext,
    normalize_chain_execution_context,
)


SUPPORTED_EXECUTION_MODES = frozenset({"cheap", "balanced", "aggressive", "max"})


DEFAULT_CHAIN_AWARE_MODE_POLICY_BY_CHAIN: dict[str, dict[str, Any]] = {
    "solana": {
        "chain": "solana",
        "execution_venue": "jupiter",
        "default_mode": "balanced",
        "allow_conservative_fallback": True,
        "mode_thresholds": {
            "cheap": {
                "mode_name": "cheap",
                "max_price_impact_bps": 20.0,
                "max_fee_bps": 10.0,
                "max_latency_ms": 250.0,
                "max_hop_count": 2,
                "requires_provider_health": True,
            },
            "balanced": {
                "mode_name": "balanced",
                "max_price_impact_bps": 50.0,
                "max_fee_bps": 20.0,
                "max_latency_ms": 500.0,
                "max_hop_count": 3,
                "requires_provider_health": True,
            },
            "aggressive": {
                "mode_name": "aggressive",
                "max_price_impact_bps": 90.0,
                "max_fee_bps": 35.0,
                "max_latency_ms": 900.0,
                "max_hop_count": 4,
                "requires_provider_health": True,
            },
            "max": {
                "mode_name": "max",
                "max_price_impact_bps": 150.0,
                "max_fee_bps": 60.0,
                "max_latency_ms": 1400.0,
                "max_hop_count": 5,
                "requires_provider_health": True,
            },
        },
        "metadata": {
            "policy_family": "solana_jupiter",
            "note": "balanced remains the conservative default for the current solana baseline",
        },
    },
    "ethereum": {
        "chain": "ethereum",
        "execution_venue": "generic_evm_router",
        "default_mode": "cheap",
        "allow_conservative_fallback": True,
        "mode_thresholds": {
            "cheap": {
                "mode_name": "cheap",
                "max_price_impact_bps": 25.0,
                "max_fee_bps": 25.0,
                "max_latency_ms": 1500.0,
                "max_hop_count": 1,
                "requires_provider_health": True,
            },
            "balanced": {
                "mode_name": "balanced",
                "max_price_impact_bps": 60.0,
                "max_fee_bps": 45.0,
                "max_latency_ms": 3000.0,
                "max_hop_count": 1,
                "requires_provider_health": True,
            },
            "aggressive": {
                "mode_name": "aggressive",
                "max_price_impact_bps": 120.0,
                "max_fee_bps": 80.0,
                "max_latency_ms": 5000.0,
                "max_hop_count": 2,
                "requires_provider_health": True,
            },
            "max": {
                "mode_name": "max",
                "max_price_impact_bps": 200.0,
                "max_fee_bps": 120.0,
                "max_latency_ms": 8000.0,
                "max_hop_count": 2,
                "requires_provider_health": True,
            },
        },
        "metadata": {
            "policy_family": "evm_router",
            "note": "cheap is the conservative default for current evm-family baseline",
        },
    },
    "base": {
        "chain": "base",
        "execution_venue": "generic_evm_router",
        "default_mode": "cheap",
        "allow_conservative_fallback": True,
        "mode_thresholds": {
            "cheap": {
                "mode_name": "cheap",
                "max_price_impact_bps": 25.0,
                "max_fee_bps": 25.0,
                "max_latency_ms": 1500.0,
                "max_hop_count": 1,
                "requires_provider_health": True,
            },
            "balanced": {
                "mode_name": "balanced",
                "max_price_impact_bps": 60.0,
                "max_fee_bps": 45.0,
                "max_latency_ms": 3000.0,
                "max_hop_count": 1,
                "requires_provider_health": True,
            },
            "aggressive": {
                "mode_name": "aggressive",
                "max_price_impact_bps": 120.0,
                "max_fee_bps": 80.0,
                "max_latency_ms": 5000.0,
                "max_hop_count": 2,
                "requires_provider_health": True,
            },
            "max": {
                "mode_name": "max",
                "max_price_impact_bps": 200.0,
                "max_fee_bps": 120.0,
                "max_latency_ms": 8000.0,
                "max_hop_count": 2,
                "requires_provider_health": True,
            },
        },
        "metadata": {
            "policy_family": "evm_router",
            "note": "cheap is the conservative default for current evm-family baseline",
        },
    },
    "arbitrum": {
        "chain": "arbitrum",
        "execution_venue": "generic_evm_router",
        "default_mode": "cheap",
        "allow_conservative_fallback": True,
        "mode_thresholds": {
            "cheap": {
                "mode_name": "cheap",
                "max_price_impact_bps": 25.0,
                "max_fee_bps": 25.0,
                "max_latency_ms": 1500.0,
                "max_hop_count": 1,
                "requires_provider_health": True,
            },
            "balanced": {
                "mode_name": "balanced",
                "max_price_impact_bps": 60.0,
                "max_fee_bps": 45.0,
                "max_latency_ms": 3000.0,
                "max_hop_count": 1,
                "requires_provider_health": True,
            },
            "aggressive": {
                "mode_name": "aggressive",
                "max_price_impact_bps": 120.0,
                "max_fee_bps": 80.0,
                "max_latency_ms": 5000.0,
                "max_hop_count": 2,
                "requires_provider_health": True,
            },
            "max": {
                "mode_name": "max",
                "max_price_impact_bps": 200.0,
                "max_fee_bps": 120.0,
                "max_latency_ms": 8000.0,
                "max_hop_count": 2,
                "requires_provider_health": True,
            },
        },
        "metadata": {
            "policy_family": "evm_router",
            "note": "cheap is the conservative default for current evm-family baseline",
        },
    },
}


class ChainAwareModePolicyError(ValueError):
    """Raised when a chain-aware mode policy is invalid or unsupported."""


def _normalize_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    raise ChainAwareModePolicyError(f"{field_name} must be a mapping")


def _normalize_text(value: Any, field_name: str) -> str:
    text = str(value or "").strip().lower()
    if not text:
        raise ChainAwareModePolicyError(f"{field_name} must be a non-empty string")
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
    raise ChainAwareModePolicyError(f"{field_name} must be boolean-like")


def _normalize_non_negative_float(value: Any, field_name: str) -> float:
    try:
        normalized = float(value)
    except (TypeError, ValueError) as exc:
        raise ChainAwareModePolicyError(f"{field_name} must be numeric") from exc
    if normalized < 0:
        raise ChainAwareModePolicyError(f"{field_name} must be non-negative")
    return normalized


def _normalize_positive_int(value: Any, field_name: str) -> int:
    try:
        normalized = int(value)
    except (TypeError, ValueError) as exc:
        raise ChainAwareModePolicyError(f"{field_name} must be integer-like") from exc
    if normalized < 1:
        raise ChainAwareModePolicyError(f"{field_name} must be >= 1")
    return normalized


def render_chain_aware_mode_policy_id(chain: str, execution_venue: str) -> str:
    return ":".join(
        [
            _normalize_text(chain, "chain"),
            _normalize_text(execution_venue, "execution_venue"),
            "mode_policy",
        ]
    )


@dataclass(frozen=True)
class ModeThreshold:
    mode_name: str
    max_price_impact_bps: float
    max_fee_bps: float
    max_latency_ms: float
    max_hop_count: int
    requires_provider_health: bool = True

    def __post_init__(self) -> None:
        validate_mode_threshold(self)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "ModeThreshold":
        return normalize_mode_threshold(payload)


@dataclass(frozen=True)
class ChainAwareModePolicy:
    policy_id: str
    chain: str
    execution_venue: str
    default_mode: str
    allow_conservative_fallback: bool
    mode_thresholds: dict[str, dict[str, Any]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        validate_chain_aware_mode_policy(self)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "ChainAwareModePolicy":
        return normalize_chain_aware_mode_policy(payload)


def validate_mode_threshold(value: ModeThreshold) -> None:
    mode_name = _normalize_text(value.mode_name, "mode_name")
    if mode_name not in SUPPORTED_EXECUTION_MODES:
        raise ChainAwareModePolicyError(
            f"mode_name must be one of {sorted(SUPPORTED_EXECUTION_MODES)}"
        )

    _normalize_non_negative_float(value.max_price_impact_bps, "max_price_impact_bps")
    _normalize_non_negative_float(value.max_fee_bps, "max_fee_bps")
    _normalize_non_negative_float(value.max_latency_ms, "max_latency_ms")
    _normalize_positive_int(value.max_hop_count, "max_hop_count")
    _normalize_bool(value.requires_provider_health, "requires_provider_health")


def normalize_mode_threshold(value: Any) -> ModeThreshold:
    if isinstance(value, ModeThreshold):
        return value

    payload = _normalize_mapping(value, "value")
    return ModeThreshold(
        mode_name=_normalize_text(payload.get("mode_name"), "mode_name"),
        max_price_impact_bps=_normalize_non_negative_float(
            payload.get("max_price_impact_bps"),
            "max_price_impact_bps",
        ),
        max_fee_bps=_normalize_non_negative_float(
            payload.get("max_fee_bps"),
            "max_fee_bps",
        ),
        max_latency_ms=_normalize_non_negative_float(
            payload.get("max_latency_ms"),
            "max_latency_ms",
        ),
        max_hop_count=_normalize_positive_int(
            payload.get("max_hop_count"),
            "max_hop_count",
        ),
        requires_provider_health=_normalize_bool(
            payload.get("requires_provider_health", True),
            "requires_provider_health",
        ),
    )


def validate_chain_aware_mode_policy(value: ChainAwareModePolicy) -> None:
    chain = _normalize_text(value.chain, "chain")
    execution_venue = _normalize_text(value.execution_venue, "execution_venue")
    default_mode = _normalize_text(value.default_mode, "default_mode")

    if chain not in SUPPORTED_CHAINS:
        raise ChainAwareModePolicyError(
            f"chain must be one of {sorted(SUPPORTED_CHAINS)}"
        )

    defaults = DEFAULT_CHAIN_AWARE_MODE_POLICY_BY_CHAIN.get(chain)
    if defaults is None:
        raise ChainAwareModePolicyError(
            f"missing built-in mode policy for supported chain {chain!r}"
        )

    if execution_venue != defaults["execution_venue"]:
        raise ChainAwareModePolicyError(
            f"execution_venue must be {defaults['execution_venue']!r} for chain {chain!r}"
        )

    if default_mode not in SUPPORTED_EXECUTION_MODES:
        raise ChainAwareModePolicyError(
            f"default_mode must be one of {sorted(SUPPORTED_EXECUTION_MODES)}"
        )

    normalized_thresholds: dict[str, ModeThreshold] = {}
    for mode_name, threshold_payload in dict(value.mode_thresholds).items():
        normalized_name = _normalize_text(mode_name, "mode_name")
        threshold = normalize_mode_threshold(threshold_payload)
        if threshold.mode_name != normalized_name:
            raise ChainAwareModePolicyError(
                f"mode_thresholds key {normalized_name!r} must match embedded mode_name {threshold.mode_name!r}"
            )
        normalized_thresholds[normalized_name] = threshold

    missing_modes = sorted(SUPPORTED_EXECUTION_MODES.difference(normalized_thresholds))
    if missing_modes:
        raise ChainAwareModePolicyError(
            f"mode_thresholds must define all supported modes; missing {missing_modes}"
        )

    if default_mode not in normalized_thresholds:
        raise ChainAwareModePolicyError(
            f"default_mode {default_mode!r} must exist in mode_thresholds"
        )


def normalize_chain_aware_mode_policy(value: Any) -> ChainAwareModePolicy:
    if isinstance(value, ChainAwareModePolicy):
        return value

    payload = _normalize_mapping(value, "value")
    chain = _normalize_text(payload.get("chain"), "chain")
    defaults = DEFAULT_CHAIN_AWARE_MODE_POLICY_BY_CHAIN.get(chain)
    if defaults is None:
        raise ChainAwareModePolicyError(
            f"chain must be one of {sorted(DEFAULT_CHAIN_AWARE_MODE_POLICY_BY_CHAIN)}"
        )

    execution_venue = _normalize_text(
        payload.get("execution_venue", defaults["execution_venue"]),
        "execution_venue",
    )
    default_mode = _normalize_text(
        payload.get("default_mode", defaults["default_mode"]),
        "default_mode",
    )

    raw_thresholds = payload.get("mode_thresholds") or defaults["mode_thresholds"]
    normalized_thresholds = {
        _normalize_text(mode_name, "mode_name"): normalize_mode_threshold(threshold_payload).to_dict()
        for mode_name, threshold_payload in dict(raw_thresholds).items()
    }

    return ChainAwareModePolicy(
        policy_id=str(
            payload.get("policy_id")
            or render_chain_aware_mode_policy_id(chain=chain, execution_venue=execution_venue)
        ),
        chain=chain,
        execution_venue=execution_venue,
        default_mode=default_mode,
        allow_conservative_fallback=_normalize_bool(
            payload.get("allow_conservative_fallback", defaults["allow_conservative_fallback"]),
            "allow_conservative_fallback",
        ),
        mode_thresholds=normalized_thresholds,
        metadata=dict(payload.get("metadata") or defaults.get("metadata") or {}),
    )


def build_default_chain_aware_mode_policy(context_or_chain: Any) -> ChainAwareModePolicy:
    if isinstance(context_or_chain, (ChainExecutionContext, Mapping)):
        chain = normalize_chain_execution_context(context_or_chain).chain
    else:
        chain = _normalize_text(context_or_chain, "chain")
    defaults = DEFAULT_CHAIN_AWARE_MODE_POLICY_BY_CHAIN.get(chain)
    if defaults is None:
        raise ChainAwareModePolicyError(
            f"chain must be one of {sorted(DEFAULT_CHAIN_AWARE_MODE_POLICY_BY_CHAIN)}"
        )
    return normalize_chain_aware_mode_policy(defaults)


def build_chain_aware_mode_policy_registry() -> dict[str, ChainAwareModePolicy]:
    return {
        chain: build_default_chain_aware_mode_policy(chain)
        for chain in sorted(DEFAULT_CHAIN_AWARE_MODE_POLICY_BY_CHAIN)
    }


def lookup_chain_aware_mode_policy(
    registry: Mapping[str, Any],
    context_or_chain: Any,
    *,
    allow_conservative_fallback: bool = False,
) -> ChainAwareModePolicy:
    if isinstance(context_or_chain, (ChainExecutionContext, Mapping)):
        chain = normalize_chain_execution_context(context_or_chain).chain
    else:
        chain = _normalize_text(context_or_chain, "chain")

    if chain in registry:
        return normalize_chain_aware_mode_policy(registry[chain])

    if allow_conservative_fallback:
        built_in = DEFAULT_CHAIN_AWARE_MODE_POLICY_BY_CHAIN.get(chain)
        if built_in is not None:
            policy = normalize_chain_aware_mode_policy(built_in)
            if policy.allow_conservative_fallback:
                return policy

    raise ChainAwareModePolicyError(f"missing chain-aware mode policy for chain {chain!r}")


def validate_context_against_chain_aware_mode_policy(
    context: Any,
    policy: Any,
) -> None:
    normalized_context = normalize_chain_execution_context(context)
    normalized_policy = normalize_chain_aware_mode_policy(policy)

    if normalized_context.chain != normalized_policy.chain:
        raise ChainAwareModePolicyError(
            "context chain does not match chain-aware mode policy chain"
        )
    if normalized_context.execution_venue != normalized_policy.execution_venue:
        raise ChainAwareModePolicyError(
            "context execution_venue does not match chain-aware mode policy execution_venue"
        )


def resolve_effective_mode_threshold(
    policy: Any,
    requested_mode: str | None = None,
    *,
    allow_conservative_fallback: bool = False,
) -> ModeThreshold:
    normalized_policy = normalize_chain_aware_mode_policy(policy)

    if requested_mode is None:
        requested_mode = normalized_policy.default_mode

    normalized_mode = _normalize_text(requested_mode, "requested_mode")
    if normalized_mode not in SUPPORTED_EXECUTION_MODES:
        if allow_conservative_fallback and normalized_policy.allow_conservative_fallback:
            return normalize_mode_threshold(
                normalized_policy.mode_thresholds[normalized_policy.default_mode]
            )
        raise ChainAwareModePolicyError(
            f"requested_mode must be one of {sorted(SUPPORTED_EXECUTION_MODES)}"
        )

    if normalized_mode not in normalized_policy.mode_thresholds:
        if allow_conservative_fallback and normalized_policy.allow_conservative_fallback:
            return normalize_mode_threshold(
                normalized_policy.mode_thresholds[normalized_policy.default_mode]
            )
        raise ChainAwareModePolicyError(
            f"requested_mode {normalized_mode!r} is not configured for this chain-aware mode policy"
        )

    return normalize_mode_threshold(normalized_policy.mode_thresholds[normalized_mode])


def route_inputs_pass_mode_policy(
    route_inputs: Any,
    policy: Any,
    requested_mode: str | None = None,
    *,
    allow_conservative_fallback: bool = False,
) -> bool:
    normalized_inputs = normalize_chain_aware_route_score_inputs(route_inputs)
    normalized_policy = normalize_chain_aware_mode_policy(policy)

    validate_context_against_chain_aware_mode_policy(
        normalized_inputs.chain_context,
        normalized_policy,
    )
    threshold = resolve_effective_mode_threshold(
        normalized_policy,
        requested_mode=requested_mode,
        allow_conservative_fallback=allow_conservative_fallback,
    )

    if threshold.requires_provider_health and not normalized_inputs.provider_healthy:
        return False
    if normalized_inputs.estimated_price_impact_bps > threshold.max_price_impact_bps:
        return False
    if normalized_inputs.estimated_fee_bps > threshold.max_fee_bps:
        return False
    if normalized_inputs.estimated_latency_ms > threshold.max_latency_ms:
        return False
    if normalized_inputs.hop_count > threshold.max_hop_count:
        return False
    return True


__all__ = [
    "DEFAULT_CHAIN_AWARE_MODE_POLICY_BY_CHAIN",
    "SUPPORTED_EXECUTION_MODES",
    "ChainAwareModePolicy",
    "ChainAwareModePolicyError",
    "ModeThreshold",
    "build_chain_aware_mode_policy_registry",
    "build_default_chain_aware_mode_policy",
    "lookup_chain_aware_mode_policy",
    "normalize_chain_aware_mode_policy",
    "normalize_mode_threshold",
    "render_chain_aware_mode_policy_id",
    "resolve_effective_mode_threshold",
    "route_inputs_pass_mode_policy",
    "validate_context_against_chain_aware_mode_policy",
    "validate_chain_aware_mode_policy",
    "validate_mode_threshold",
]