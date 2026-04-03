import pytest

from src.trader.execution.chain_execution_context import build_default_chain_execution_context
from src.trader.execution.connector_capability_profile import build_default_connector_capability_profile
from src.trader.execution.connector_selection_policy import (
    ConnectorSelectionCandidate,
    ConnectorSelectionPolicyError,
    build_connector_selection_result,
    normalize_connector_selection_candidate,
    render_connector_selection_result_id,
)
from src.trader.execution.multi_chain_provider_health_snapshot import build_multi_chain_provider_health_snapshot


def test_normalizer_accepts_mapping_like_input_and_round_trips() -> None:
    context = build_default_chain_execution_context(chain="solana", execution_target="paper")
    profile = build_default_connector_capability_profile("solana")
    snapshot = build_multi_chain_provider_health_snapshot(
        chain_context=context,
        provider_key="jupiter_primary",
        status="healthy",
        observed_at_epoch_ms=1000,
        last_success_epoch_ms=900,
        latency_ms=120.0,
    )

    candidate = normalize_connector_selection_candidate(
        {
            "chain_context": context.to_dict(),
            "connector_profile": profile.to_dict(),
            "provider_health_snapshot": snapshot.to_dict(),
        }
    )

    round_tripped = ConnectorSelectionCandidate.from_dict(candidate.to_dict())
    assert round_tripped == candidate


def test_render_selection_result_id_is_stable_and_lowercase() -> None:
    context = build_default_chain_execution_context(chain="solana", execution_target="paper")
    assert (
        render_connector_selection_result_id(
            context=context,
            selected_provider_key="JUPITER_PRIMARY",
        )
        == "solana:jupiter:jupiter_primary:connector_selection"
    )


def test_deterministic_selection_prefers_lower_latency_healthy_candidate() -> None:
    context = build_default_chain_execution_context(chain="solana", execution_target="paper")
    profile = build_default_connector_capability_profile("solana")

    candidate_a = ConnectorSelectionCandidate(
        chain_context=context,
        connector_profile=profile,
        provider_health_snapshot=build_multi_chain_provider_health_snapshot(
            chain_context=context,
            provider_key="jupiter_secondary",
            status="healthy",
            observed_at_epoch_ms=2000,
            last_success_epoch_ms=1950,
            latency_ms=160.0,
        ),
    )
    candidate_b = ConnectorSelectionCandidate(
        chain_context=context,
        connector_profile=profile,
        provider_health_snapshot=build_multi_chain_provider_health_snapshot(
            chain_context=context,
            provider_key="jupiter_primary",
            status="healthy",
            observed_at_epoch_ms=2000,
            last_success_epoch_ms=1960,
            latency_ms=120.0,
        ),
    )

    result = build_connector_selection_result(
        chain_context=context,
        candidates=[candidate_a, candidate_b],
        max_freshness_ms=200,
    )

    assert result.selected_provider_key == "jupiter_primary"
    assert result.selected_connector_key == "solana_connector"
    assert result.block_reason is None
    assert "deterministic_best_candidate_selected" in result.decision_reason_codes


def test_degraded_candidate_blocks_when_not_allowed() -> None:
    context = build_default_chain_execution_context(chain="base", execution_target="paper")
    profile = build_default_connector_capability_profile("base")
    candidate = ConnectorSelectionCandidate(
        chain_context=context,
        connector_profile=profile,
        provider_health_snapshot=build_multi_chain_provider_health_snapshot(
            chain_context=context,
            provider_key="base_router_a",
            status="degraded",
            observed_at_epoch_ms=5000,
            last_success_epoch_ms=4900,
            latency_ms=700.0,
            degraded_reason="latency spike",
        ),
    )

    result = build_connector_selection_result(
        chain_context=context,
        candidates=[candidate],
        max_freshness_ms=1000,
        allow_degraded=False,
    )

    assert result.selected_provider_key is None
    assert result.block_reason == "provider_health_degraded"


def test_degraded_candidate_can_be_selected_when_allowed() -> None:
    context = build_default_chain_execution_context(chain="base", execution_target="paper")
    profile = build_default_connector_capability_profile("base")
    candidate = ConnectorSelectionCandidate(
        chain_context=context,
        connector_profile=profile,
        provider_health_snapshot=build_multi_chain_provider_health_snapshot(
            chain_context=context,
            provider_key="base_router_a",
            status="degraded",
            observed_at_epoch_ms=5000,
            last_success_epoch_ms=4900,
            latency_ms=700.0,
            degraded_reason="latency spike",
        ),
    )

    result = build_connector_selection_result(
        chain_context=context,
        candidates=[candidate],
        max_freshness_ms=1000,
        allow_degraded=True,
    )

    assert result.selected_provider_key == "base_router_a"
    assert "degraded_allowed_by_policy" in result.decision_reason_codes


def test_freshness_threshold_blocks_candidate_even_if_status_is_healthy() -> None:
    context = build_default_chain_execution_context(chain="ethereum", execution_target="paper")
    profile = build_default_connector_capability_profile("ethereum")
    candidate = ConnectorSelectionCandidate(
        chain_context=context,
        connector_profile=profile,
        provider_health_snapshot=build_multi_chain_provider_health_snapshot(
            chain_context=context,
            provider_key="eth_router_a",
            status="healthy",
            observed_at_epoch_ms=10000,
            last_success_epoch_ms=8000,
            latency_ms=300.0,
        ),
    )

    result = build_connector_selection_result(
        chain_context=context,
        candidates=[candidate],
        max_freshness_ms=1000,
    )

    assert result.selected_provider_key is None
    assert result.block_reason == "provider_health_freshness_expired"


def test_candidate_validation_blocks_profile_chain_mismatch() -> None:
    solana_context = build_default_chain_execution_context(chain="solana", execution_target="paper")
    base_context = build_default_chain_execution_context(chain="base", execution_target="paper")
    profile = build_default_connector_capability_profile("solana")
    snapshot = build_multi_chain_provider_health_snapshot(
        chain_context=base_context,
        provider_key="base_router_a",
        status="healthy",
        observed_at_epoch_ms=1000,
        last_success_epoch_ms=900,
        latency_ms=120.0,
    )

    with pytest.raises(
        ConnectorSelectionPolicyError,
        match="candidate connector profile chain does not match context chain",
    ):
        ConnectorSelectionCandidate(
            chain_context=base_context,
            connector_profile=profile,
            provider_health_snapshot=snapshot,
        )


def test_candidate_validation_blocks_snapshot_chain_mismatch() -> None:
    solana_context = build_default_chain_execution_context(chain="solana", execution_target="paper")
    base_context = build_default_chain_execution_context(chain="base", execution_target="paper")
    profile = build_default_connector_capability_profile("base")
    snapshot = build_multi_chain_provider_health_snapshot(
        chain_context=solana_context,
        provider_key="jupiter_primary",
        status="healthy",
        observed_at_epoch_ms=1000,
        last_success_epoch_ms=900,
        latency_ms=120.0,
    )

    with pytest.raises(
        ConnectorSelectionPolicyError,
        match="candidate provider health snapshot chain does not match context chain",
    ):
        ConnectorSelectionCandidate(
            chain_context=base_context,
            connector_profile=profile,
            provider_health_snapshot=snapshot,
        )


def test_same_inputs_produce_same_selection_output() -> None:
    context = build_default_chain_execution_context(chain="solana", execution_target="paper")
    profile = build_default_connector_capability_profile("solana")
    candidates = [
        ConnectorSelectionCandidate(
            chain_context=context,
            connector_profile=profile,
            provider_health_snapshot=build_multi_chain_provider_health_snapshot(
                chain_context=context,
                provider_key="jupiter_b",
                status="healthy",
                observed_at_epoch_ms=2000,
                last_success_epoch_ms=1950,
                latency_ms=180.0,
            ),
        ),
        ConnectorSelectionCandidate(
            chain_context=context,
            connector_profile=profile,
            provider_health_snapshot=build_multi_chain_provider_health_snapshot(
                chain_context=context,
                provider_key="jupiter_a",
                status="healthy",
                observed_at_epoch_ms=2000,
                last_success_epoch_ms=1960,
                latency_ms=120.0,
            ),
        ),
    ]

    first = build_connector_selection_result(
        chain_context=context,
        candidates=candidates,
        max_freshness_ms=500,
    )
    second = build_connector_selection_result(
        chain_context=context,
        candidates=list(reversed(candidates)),
        max_freshness_ms=500,
    )

    assert first.to_dict() == second.to_dict()