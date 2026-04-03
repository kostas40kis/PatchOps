import pytest

from src.trader.execution.chain_execution_context import build_default_chain_execution_context
from src.trader.execution.connector_capability_profile import build_default_connector_capability_profile
from src.trader.execution.order_style_capability_matrix import build_order_style_capability_matrix
from src.trader.execution.chain_reserve_policy_registry import build_default_chain_reserve_policy
from src.trader.execution.multi_chain_provider_health_snapshot import build_multi_chain_provider_health_snapshot
from src.trader.execution.chain_support_validation import (
    ChainSupportValidationError,
    chain_support_is_allowed,
    render_chain_support_validation_id,
    require_chain_support,
    validate_chain_support_request,
)


def _healthy_snapshot(context, provider_key="primary", latency_ms=100.0, observed=1000, last_success=950):
    return build_multi_chain_provider_health_snapshot(
        chain_context=context,
        provider_key=provider_key,
        status="healthy",
        observed_at_epoch_ms=observed,
        last_success_epoch_ms=last_success,
        latency_ms=latency_ms,
    )


def test_render_validation_id_is_stable_and_lowercase() -> None:
    assert (
        render_chain_support_validation_id(
            chain="Solana",
            execution_venue="Jupiter",
            action_type="Marketable_Execution",
        )
        == "solana:jupiter:marketable_execution:chain_support_validation"
    )


def test_marketable_execution_is_supported_for_healthy_solana_context() -> None:
    context = build_default_chain_execution_context(chain="solana", execution_target="paper")
    profile = build_default_connector_capability_profile("solana")
    matrix = build_order_style_capability_matrix(profile)
    reserve_policy = build_default_chain_reserve_policy("solana")
    snapshot = _healthy_snapshot(context, provider_key="jupiter_primary")

    result = validate_chain_support_request(
        chain_context=context,
        connector_profile=profile,
        order_style_matrix=matrix,
        reserve_policy=reserve_policy,
        provider_health_snapshot=snapshot,
        action_type="marketable_execution",
        available_native_balance=1.0,
        max_health_freshness_ms=500,
    )

    assert result.is_supported is True
    assert result.block_reason is None
    assert result.reason_codes == tuple()


def test_native_limit_order_blocks_when_not_supported() -> None:
    context = build_default_chain_execution_context(chain="solana", execution_target="paper")
    profile = build_default_connector_capability_profile("solana")
    matrix = build_order_style_capability_matrix(profile)
    reserve_policy = build_default_chain_reserve_policy("solana")
    snapshot = _healthy_snapshot(context)

    result = validate_chain_support_request(
        chain_context=context,
        connector_profile=profile,
        order_style_matrix=matrix,
        reserve_policy=reserve_policy,
        provider_health_snapshot=snapshot,
        action_type="native_limit_order",
        available_native_balance=1.0,
    )

    assert result.is_supported is False
    assert result.block_reason == "unsupported_native_limit_order"
    assert "unsupported_native_limit_order" in result.reason_codes


def test_profile_chain_mismatch_blocks_fail_closed() -> None:
    context = build_default_chain_execution_context(chain="base", execution_target="paper")
    profile = build_default_connector_capability_profile("solana")
    matrix = build_order_style_capability_matrix(profile)
    reserve_policy = build_default_chain_reserve_policy("base")
    snapshot = _healthy_snapshot(context, provider_key="base_router_a")

    result = validate_chain_support_request(
        chain_context=context,
        connector_profile=profile,
        order_style_matrix=matrix,
        reserve_policy=reserve_policy,
        provider_health_snapshot=snapshot,
        action_type="marketable_execution",
        available_native_balance=1.0,
    )

    assert result.is_supported is False
    assert result.block_reason == "unsupported_chain_profile_mismatch"


def test_provider_health_freshness_expiry_blocks_request() -> None:
    context = build_default_chain_execution_context(chain="ethereum", execution_target="paper")
    profile = build_default_connector_capability_profile("ethereum")
    matrix = build_order_style_capability_matrix(profile)
    reserve_policy = build_default_chain_reserve_policy("ethereum")
    snapshot = _healthy_snapshot(context, provider_key="eth_router_a", observed=10_000, last_success=8_000)

    result = validate_chain_support_request(
        chain_context=context,
        connector_profile=profile,
        order_style_matrix=matrix,
        reserve_policy=reserve_policy,
        provider_health_snapshot=snapshot,
        action_type="marketable_execution",
        available_native_balance=1.0,
        max_health_freshness_ms=1000,
    )

    assert result.is_supported is False
    assert result.block_reason == "provider_health_freshness_expired"


def test_insufficient_native_reserve_blocks_request() -> None:
    context = build_default_chain_execution_context(chain="solana", execution_target="paper")
    profile = build_default_connector_capability_profile("solana")
    matrix = build_order_style_capability_matrix(profile)
    reserve_policy = build_default_chain_reserve_policy("solana")
    snapshot = _healthy_snapshot(context)

    result = validate_chain_support_request(
        chain_context=context,
        connector_profile=profile,
        order_style_matrix=matrix,
        reserve_policy=reserve_policy,
        provider_health_snapshot=snapshot,
        action_type="marketable_execution",
        available_native_balance=0.001,
    )

    assert result.is_supported is False
    assert result.block_reason == "insufficient_native_reserve"


def test_quote_only_still_requires_supported_context_but_not_order_style() -> None:
    context = build_default_chain_execution_context(chain="solana", execution_target="paper")
    profile = build_default_connector_capability_profile("solana")
    matrix = build_order_style_capability_matrix(profile)
    reserve_policy = build_default_chain_reserve_policy("solana")
    snapshot = _healthy_snapshot(context)

    result = validate_chain_support_request(
        chain_context=context,
        connector_profile=profile,
        order_style_matrix=matrix,
        reserve_policy=reserve_policy,
        provider_health_snapshot=snapshot,
        action_type="quote_only",
        available_native_balance=1.0,
    )

    assert result.is_supported is True


def test_require_chain_support_raises_with_explicit_reason() -> None:
    context = build_default_chain_execution_context(chain="solana", execution_target="paper")
    profile = build_default_connector_capability_profile("solana")
    matrix = build_order_style_capability_matrix(profile)
    reserve_policy = build_default_chain_reserve_policy("solana")
    snapshot = _healthy_snapshot(context)

    with pytest.raises(
        ChainSupportValidationError,
        match="unsupported chain/venue/order-style combination: unsupported_native_stop_order",
    ):
        require_chain_support(
            chain_context=context,
            connector_profile=profile,
            order_style_matrix=matrix,
            reserve_policy=reserve_policy,
            provider_health_snapshot=snapshot,
            action_type="native_stop_order",
            available_native_balance=1.0,
        )


def test_chain_support_is_allowed_returns_boolean() -> None:
    context = build_default_chain_execution_context(chain="base", execution_target="paper")
    profile = build_default_connector_capability_profile("base")
    matrix = build_order_style_capability_matrix(profile)
    reserve_policy = build_default_chain_reserve_policy("base")
    snapshot = _healthy_snapshot(context, provider_key="base_router_a")

    assert chain_support_is_allowed(
        chain_context=context,
        connector_profile=profile,
        order_style_matrix=matrix,
        reserve_policy=reserve_policy,
        provider_health_snapshot=snapshot,
        action_type="marketable_execution",
        available_native_balance=1.0,
        max_health_freshness_ms=500,
    ) is True