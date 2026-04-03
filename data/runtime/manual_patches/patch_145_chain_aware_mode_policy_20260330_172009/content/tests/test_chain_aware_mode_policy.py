import pytest

from src.trader.execution.chain_aware_mode_policy import (
    ChainAwareModePolicy,
    ChainAwareModePolicyError,
    build_chain_aware_mode_policy_registry,
    build_default_chain_aware_mode_policy,
    lookup_chain_aware_mode_policy,
    normalize_chain_aware_mode_policy,
    render_chain_aware_mode_policy_id,
    resolve_effective_mode_threshold,
    route_inputs_pass_mode_policy,
    validate_context_against_chain_aware_mode_policy,
)
from src.trader.execution.chain_aware_route_score_inputs import build_chain_aware_route_score_inputs
from src.trader.execution.chain_execution_context import build_default_chain_execution_context


def test_default_builder_returns_conservative_solana_policy() -> None:
    context = build_default_chain_execution_context(chain="solana", execution_target="paper")
    policy = build_default_chain_aware_mode_policy(context)

    assert policy.chain == "solana"
    assert policy.execution_venue == "jupiter"
    assert policy.default_mode == "balanced"
    assert policy.allow_conservative_fallback is True


def test_default_builder_returns_conservative_base_policy() -> None:
    context = build_default_chain_execution_context(chain="base", execution_target="paper")
    policy = build_default_chain_aware_mode_policy(context)

    assert policy.chain == "base"
    assert policy.execution_venue == "generic_evm_router"
    assert policy.default_mode == "cheap"
    assert policy.allow_conservative_fallback is True


def test_normalizer_accepts_mapping_like_input_and_round_trips() -> None:
    policy = normalize_chain_aware_mode_policy(
        {
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
            "metadata": {"source": "test"},
        }
    )

    assert policy.metadata["source"] == "test"

    round_tripped = ChainAwareModePolicy.from_dict(policy.to_dict())
    assert round_tripped == policy


def test_render_policy_id_is_stable_and_lowercase() -> None:
    assert (
        render_chain_aware_mode_policy_id("Solana", "Jupiter")
        == "solana:jupiter:mode_policy"
    )


def test_resolve_effective_mode_threshold_returns_requested_mode() -> None:
    policy = build_default_chain_aware_mode_policy("solana")
    threshold = resolve_effective_mode_threshold(policy, requested_mode="aggressive")

    assert threshold.mode_name == "aggressive"
    assert threshold.max_price_impact_bps == pytest.approx(90.0)


def test_lookup_missing_policy_blocks_without_fallback() -> None:
    context = build_default_chain_execution_context(chain="solana", execution_target="paper")
    with pytest.raises(
        ChainAwareModePolicyError,
        match="missing chain-aware mode policy for chain 'solana'",
    ):
        lookup_chain_aware_mode_policy({}, context)


def test_lookup_missing_policy_can_use_conservative_fallback() -> None:
    context = build_default_chain_execution_context(chain="solana", execution_target="paper")
    policy = lookup_chain_aware_mode_policy({}, context, allow_conservative_fallback=True)

    assert policy.chain == "solana"
    assert policy.default_mode == "balanced"


def test_context_validation_blocks_chain_mismatch() -> None:
    context = build_default_chain_execution_context(chain="base", execution_target="paper")
    policy = build_default_chain_aware_mode_policy("solana")

    with pytest.raises(
        ChainAwareModePolicyError,
        match="context chain does not match chain-aware mode policy chain",
    ):
        validate_context_against_chain_aware_mode_policy(context, policy)


def test_route_inputs_pass_balanced_policy_for_reasonable_solana_route() -> None:
    context = build_default_chain_execution_context(chain="solana", execution_target="paper")
    policy = build_default_chain_aware_mode_policy(context)
    route_inputs = build_chain_aware_route_score_inputs(
        chain_context=context,
        route_key="sol-usdc-main",
        quoted_in_amount=100.0,
        quoted_out_amount=99.1,
        estimated_price_impact_bps=25.0,
        estimated_fee_bps=8.0,
        estimated_latency_ms=220.0,
        hop_count=2,
        liquidity_band="deep",
        provider_healthy=True,
    )

    assert route_inputs_pass_mode_policy(route_inputs, policy, requested_mode="balanced") is True


def test_route_inputs_fail_when_provider_health_is_required_and_unhealthy() -> None:
    context = build_default_chain_execution_context(chain="solana", execution_target="paper")
    policy = build_default_chain_aware_mode_policy(context)
    route_inputs = build_chain_aware_route_score_inputs(
        chain_context=context,
        route_key="sol-usdc-main",
        quoted_in_amount=100.0,
        quoted_out_amount=99.1,
        estimated_price_impact_bps=25.0,
        estimated_fee_bps=8.0,
        estimated_latency_ms=220.0,
        hop_count=2,
        liquidity_band="deep",
        provider_healthy=False,
    )

    assert route_inputs_pass_mode_policy(route_inputs, policy, requested_mode="balanced") is False


def test_unknown_requested_mode_blocks_without_fallback_and_falls_back_when_enabled() -> None:
    policy = build_default_chain_aware_mode_policy("base")

    with pytest.raises(
        ChainAwareModePolicyError,
        match="requested_mode must be one of",
    ):
        resolve_effective_mode_threshold(policy, requested_mode="turbo")

    threshold = resolve_effective_mode_threshold(
        policy,
        requested_mode="turbo",
        allow_conservative_fallback=True,
    )
    assert threshold.mode_name == policy.default_mode


def test_registry_builder_contains_supported_chains() -> None:
    registry = build_chain_aware_mode_policy_registry()

    assert set(registry) == {"arbitrum", "base", "ethereum", "solana"}