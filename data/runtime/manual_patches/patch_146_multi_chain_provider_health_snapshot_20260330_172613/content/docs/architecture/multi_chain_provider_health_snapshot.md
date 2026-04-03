# Multi Chain Provider Health Snapshot

Patch 146 normalizes provider health across chains into one canonical snapshot shape.

## Purpose

The growth plan requires later ranking, loop, and pause/resume behavior to reason about provider health
in a unified way rather than through connector-specific ad hoc fields.

This patch adds a canonical provider-health snapshot object that can be reused by:

- ranking penalties,
- mode-policy gating,
- connector selection,
- loop pause and block decisions.

## What this patch models

The snapshot records:

- chain execution context
- provider key
- health status
- observed timestamp
- last-success timestamp
- latency
- freshness
- healthy/unhealthy boolean
- degraded reason where applicable

It also provides helpers for:

- context/snapshot validation
- block-reason derivation
- usable/not-usable determination under freshness and degraded-state rules

## Current baseline posture

This patch remains conservative.

At the current baseline:

- expired freshness can block otherwise healthy snapshots
- degraded snapshots block unless explicitly allowed
- unhealthy and stale snapshots are block conditions
- chain/venue/connector mismatches fail closed

## Why now

The roadmap places this patch immediately after chain-aware mode policy so later ranking and loop
layers can use a normalized provider-health shape for block reasons and pause decisions.