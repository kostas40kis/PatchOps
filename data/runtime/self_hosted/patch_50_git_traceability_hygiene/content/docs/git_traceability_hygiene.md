# Git and traceability hygiene

## Purpose

This document explains how PatchOps should think about Git visibility and traceability.

The important rule is:

Git visibility is useful and strongly preferred, but it is not the same thing as PatchOps core correctness.

A missing `.git` directory or unavailable Git metadata should usually be interpreted as an environment / traceability warning unless there is evidence that a required workflow depends on Git.

## What Git helps with

Git availability improves:

- change traceability
- release hygiene
- branch/commit visibility
- easier human handoff
- easier comparison between patch runs and repo history

These are valuable, but they are not the same thing as proof that the wrapper core is healthy.

## What Git does not mean by itself

If Git metadata is unavailable, that does not automatically mean:

- manifests are broken
- profile resolution is broken
- backups are broken
- file writing is broken
- validation execution is broken
- report generation is broken
- PatchOps is not usable

Those conclusions require direct evidence from the wrapper flows themselves.

## How to classify a missing-Git situation

Treat missing Git metadata as:

- a traceability / hygiene warning
- an environment note
- a release-readiness concern

Do not automatically treat it as:

- a core wrapper failure
- a reason to redesign the architecture
- a reason to blur wrapper and target concerns

## Maintained operator posture

The correct operator posture is:

1. trust the core wrapper checks first
2. read the canonical report
3. classify missing Git as warning-level unless a real dependency fails
4. improve traceability where practical
5. do not inflate a narrow environment warning into an architecture crisis

## Self-hosted PatchOps note

When PatchOps is used to patch PatchOps itself, the outer helper should not guess the report filename pattern.

Instead, it should trust the `Report Path` value printed by PatchOps stdout and surface that exact path to the operator.

That is the most reliable self-hosted behavior because report naming may include profile or workflow prefixes.