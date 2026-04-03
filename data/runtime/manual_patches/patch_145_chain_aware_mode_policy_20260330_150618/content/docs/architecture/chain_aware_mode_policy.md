# Chain Aware Mode Policy

Patch 145 extends execution-mode policy so mode behavior can vary by chain and venue.

## Purpose

The project already has execution-mode logic, but the growth plan requires mode policy to become
chain-aware in a reusable, explicit way instead of spreading chain/venue conditionals across the codebase.

This patch adds a canonical policy surface that can answer:

- what the default execution mode is for this chain/venue
- which thresholds apply for cheap / balanced / aggressive / max
- whether conservative fallback is allowed when a requested mode or policy is unavailable
- whether current route inputs satisfy the chosen mode policy

## What this patch models

The policy records:

- chain
- execution venue
- default mode
- conservative fallback allowance
- per-mode thresholds for:
  - max price impact
  - max fee
  - max latency
  - max hop count
  - provider-health requirement

## Current baseline posture

This patch stays conservative.

At the current baseline:

- solana uses `balanced` as the default mode on `jupiter`
- evm-family chains use `cheap` as the conservative default on `generic_evm_router`
- unsupported policy lookups block unless conservative fallback is explicitly allowed
- fallback returns the policy default rather than widening behavior

## Why now

The growth plan places this patch immediately after chain-aware route-score inputs so execution-mode
decision logic can become chain-aware without bypassing the new cross-chain substrate.