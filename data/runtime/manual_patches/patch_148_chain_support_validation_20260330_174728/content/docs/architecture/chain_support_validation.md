# Chain Support Validation

Patch 148 centralizes fail-closed validation for chain, venue, connector, order-style, reserve, and provider-health support.

## Purpose

By Patch 147, the cross-chain substrate already has:

- chain execution context
- connector capability profiles
- order-style capability matrices
- reserve policies
- provider-health snapshots
- connector-selection policy

The next step is to stop deeper execution layers from having to repeat support checks in scattered ways.

This patch creates one canonical validation surface that can answer:

- is this proposed action supported for the current chain/venue/connector combination
- if not, what explicit reason code blocked it

## What this patch does

It validates:

- context vs connector profile alignment
- context vs order-style matrix alignment
- context vs reserve policy alignment
- context vs provider-health snapshot alignment
- provider freshness / degraded / unhealthy block reasons
- native reserve sufficiency
- action-type support for:
  - `quote_only`
  - `marketable_execution`
  - `synthetic_monitored_exit`
  - `native_limit_order`
  - `native_stop_order`

## Current baseline posture

This patch is fail-closed.

Unsupported combinations produce explicit reason codes and a deterministic primary block reason.
Deeper execution layers can consume the result object or call the raising helper.

## Why now

The roadmap places this patch immediately after connector selection so the cross-chain substrate has one central guard layer before later ranking, allocator, and managed-position work build on top of it.