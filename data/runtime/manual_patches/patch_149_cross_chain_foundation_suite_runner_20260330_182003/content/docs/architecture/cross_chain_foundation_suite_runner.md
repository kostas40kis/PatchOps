# Cross Chain Foundation Suite Runner

Patch 149 adds the named validation surface for the whole Phase 1 cross-chain execution substrate.

## Purpose

By Patch 148, the project has the core cross-chain substrate pieces in place:

- chain execution context
- connector capability profile
- order-style capability matrix
- chain reserve policy registry
- chain-aware route-score inputs
- chain-aware mode policy
- multi-chain provider health snapshot
- connector selection policy
- chain support validation

This patch gives that substrate one canonical named suite so it can be rerun as a single phase-level proof instead of only as scattered patch-local test commands.

## What this patch adds

It defines:

- the named suite identity
- the ordered list of Phase 1 foundation test modules
- a canonical summary object
- a text renderer for phase-level reporting
- a dedicated rerun script

## Current baseline posture

This patch does not widen behavior.
It is a validation/reporting patch only.

Its job is to make the current phase easier to rerun, inspect, and reference from maintained docs and future gates.

## Why now

The maintained growth plan places this patch at the end of Phase 1 so the cross-chain substrate has one coherent validation surface before later managed-position, allocator, ranking, and loop layers build on top of it.