import pytest

from src.trader.execution.chain_execution_context import build_default_chain_execution_context
from src.trader.execution.multi_chain_provider_health_snapshot import (
    MultiChainProviderHealthSnapshot,
    MultiChainProviderHealthSnapshotError,
    build_multi_chain_provider_health_snapshot,
    normalize_multi_chain_provider_health_snapshot,
    provider_health_block_reason,
    provider_health_is_usable,
    render_multi_chain_provider_health_snapshot_id,
    validate_context_against_provider_health_snapshot,
)


def test_builder_returns_healthy_solana_snapshot() -> None:
    context = build_default_chain_execution_context(chain="solana", execution_target="paper")
    snapshot = build_multi_chain_provider_health_snapshot(
        chain_context=context,
        provider_key="jupiter_primary",
        status="healthy",
        observed_at_epoch_ms=1_000_000,
        last_success_epoch_ms=999_900,
        latency_ms=120.0,
    )

    assert snapshot.chain_context.chain == "solana"
    assert snapshot.status == "healthy"
    assert snapshot.provider_healthy is True
    assert snapshot.freshness_ms == 100


def test_builder_returns_degraded_snapshot_with_reason() -> None:
    context = build_default_chain_execution_context(chain="base", execution_target="paper")
    snapshot = build_multi_chain_provider_health_snapshot(
        chain_context=context,
        provider_key="base_router_a",
        status="degraded",
        observed_at_epoch_ms=2_000_000,
        last_success_epoch_ms=1_999_000,
        latency_ms=850.0,
        degraded_reason="latency spike",
    )

    assert snapshot.status == "degraded"
    assert snapshot.degraded_reason == "latency spike"


def test_normalizer_accepts_mapping_like_input_and_round_trips() -> None:
    context = build_default_chain_execution_context(chain="arbitrum", execution_target="paper")
    snapshot = normalize_multi_chain_provider_health_snapshot(
        {
            "chain_context": context.to_dict(),
            "provider_key": "arb_router_a",
            "status": "healthy",
            "observed_at_epoch_ms": 5000,
            "last_success_epoch_ms": 4800,
            "latency_ms": 210.0,
            "provider_healthy": True,
            "metadata": {"source": "provider_monitor"},
        }
    )

    assert snapshot.metadata["source"] == "provider_monitor"

    round_tripped = MultiChainProviderHealthSnapshot.from_dict(snapshot.to_dict())
    assert round_tripped == snapshot


def test_render_snapshot_id_is_stable_and_lowercase() -> None:
    context = build_default_chain_execution_context(chain="solana", execution_target="paper")
    assert (
        render_multi_chain_provider_health_snapshot_id(
            context=context,
            provider_key="JUPITER_PRIMARY",
        )
        == "solana:jupiter:jupiter_primary:provider_health"
    )


def test_context_validation_blocks_chain_mismatch() -> None:
    context = build_default_chain_execution_context(chain="base", execution_target="paper")
    other_context = build_default_chain_execution_context(chain="solana", execution_target="paper")
    snapshot = build_multi_chain_provider_health_snapshot(
        chain_context=other_context,
        provider_key="jupiter_primary",
        status="healthy",
        observed_at_epoch_ms=1000,
        last_success_epoch_ms=900,
        latency_ms=100.0,
    )

    with pytest.raises(
        MultiChainProviderHealthSnapshotError,
        match="context chain does not match provider health snapshot chain",
    ):
        validate_context_against_provider_health_snapshot(context, snapshot)


def test_provider_health_block_reason_detects_unhealthy_state() -> None:
    context = build_default_chain_execution_context(chain="solana", execution_target="paper")
    snapshot = normalize_multi_chain_provider_health_snapshot(
        {
            "chain_context": context.to_dict(),
            "provider_key": "jupiter_primary",
            "status": "unhealthy",
            "observed_at_epoch_ms": 2000,
            "last_success_epoch_ms": 1500,
            "latency_ms": 900.0,
            "provider_healthy": False,
        }
    )

    assert provider_health_block_reason(snapshot) == "provider_health_unhealthy"
    assert provider_health_is_usable(snapshot) is False


def test_provider_health_block_reason_detects_stale_snapshot_by_freshness() -> None:
    context = build_default_chain_execution_context(chain="ethereum", execution_target="paper")
    snapshot = build_multi_chain_provider_health_snapshot(
        chain_context=context,
        provider_key="eth_router_a",
        status="healthy",
        observed_at_epoch_ms=10_000,
        last_success_epoch_ms=8_000,
        latency_ms=300.0,
    )

    assert provider_health_block_reason(snapshot, max_freshness_ms=1000) == "provider_health_freshness_expired"
    assert provider_health_is_usable(snapshot, max_freshness_ms=1000) is False


def test_provider_health_can_allow_degraded_when_explicitly_permitted() -> None:
    context = build_default_chain_execution_context(chain="base", execution_target="paper")
    snapshot = build_multi_chain_provider_health_snapshot(
        chain_context=context,
        provider_key="base_router_a",
        status="degraded",
        observed_at_epoch_ms=5000,
        last_success_epoch_ms=4900,
        latency_ms=700.0,
        degraded_reason="temporary latency spike",
    )

    assert provider_health_block_reason(snapshot) == "provider_health_degraded"
    assert provider_health_is_usable(snapshot, allow_degraded=True) is True


def test_validation_blocks_inconsistent_freshness() -> None:
    context = build_default_chain_execution_context(chain="solana", execution_target="paper")
    with pytest.raises(
        MultiChainProviderHealthSnapshotError,
        match="freshness_ms must equal observed_at_epoch_ms - last_success_epoch_ms",
    ):
        normalize_multi_chain_provider_health_snapshot(
            {
                "chain_context": context.to_dict(),
                "provider_key": "jupiter_primary",
                "status": "healthy",
                "observed_at_epoch_ms": 1000,
                "last_success_epoch_ms": 950,
                "freshness_ms": 10,
                "latency_ms": 120.0,
                "provider_healthy": True,
            }
        )


def test_validation_requires_degraded_reason_for_degraded_status() -> None:
    context = build_default_chain_execution_context(chain="base", execution_target="paper")
    with pytest.raises(
        MultiChainProviderHealthSnapshotError,
        match="degraded_reason must be present when status is degraded",
    ):
        normalize_multi_chain_provider_health_snapshot(
            {
                "chain_context": context.to_dict(),
                "provider_key": "base_router_a",
                "status": "degraded",
                "observed_at_epoch_ms": 1000,
                "last_success_epoch_ms": 900,
                "latency_ms": 500.0,
                "provider_healthy": False,
            }
        )