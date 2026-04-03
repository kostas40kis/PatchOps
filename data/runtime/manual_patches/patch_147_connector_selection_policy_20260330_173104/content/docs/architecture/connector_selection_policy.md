# Connector Selection Policy

Patch 147 adds deterministic connector and provider selection.

## Purpose

The cross-chain substrate now knows:

- chain execution context,
- connector capability,
- order-style support,
- reserve policy,
- route-score inputs,
- chain-aware mode policy,
- provider health snapshots.

The next step is to make connector/provider choice explicit and deterministic instead of hidden inside later execution paths.

## What this patch models

This patch defines:

- a `ConnectorSelectionCandidate`
- a `ConnectorSelectionResult`
- deterministic selection over matching candidates
- explicit rejection reasons
- explicit block reasons when no candidate is usable

## Current baseline posture

This patch stays fail-closed.

At the current baseline:

- unhealthy and stale providers block selection
- degraded providers block unless explicitly allowed
- freshness expiry can block otherwise healthy candidates
- context/profile/snapshot mismatches fail closed
- deterministic ordering avoids hidden connector switching

## Why now

The roadmap places this patch immediately after normalized provider health so the system can choose a usable connector/provider combination before deeper execution layers or later ranking/allocation work depend on hidden switching behavior.