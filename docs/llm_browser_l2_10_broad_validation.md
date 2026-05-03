# L2.10 Live adapter browser profile preflight L2 broad validation checkpoint

This document freezes the passive broad-validation checkpoint for the L2 browser-profile preflight stack.

## Boundary

L2.10 is a passive broad-validation checkpoint. It aggregates and checks the accepted L2.1 through L2.9 browser-profile preflight surfaces and confirms that the L1 startup-request passive stack is still intact.

The checkpoint remains readback/model-only:

- no Selenium import
- no browser start
- no profile directory creation
- no profile filesystem write
- no adapter filesystem writes
- no click/download/paste/send/package-run side effect
- no commit or push

Profile paths may be calculated and read back as strings by existing preflight surfaces, but L2.10 must not create profile directories.

## Broad validation plan

The module exposes a planned command list for an operator or later gate to run separately. The planned command list is not executed by the module.

The planned readback commands include compileall, focused pytest for the L2 stack, the L2 aggregate readiness readback, the L2 documentation checkpoint readback, the L1 final acceptance marker readback, and git status. They deliberately exclude run-package, browser startup, click/download, paste/send, commit, and push operations.

## Content/manifest alignment repair

This L2.10c repair writes both documentation aliases used during the previous attempts:

- docs/llm_browser_live_adapter_browser_profile_l2_broad_validation_checkpoint.md
- docs/llm_browser_l2_10_broad_validation.md

The duplicated documentation aliases are intentional so older focused tests and the newer canonical L2 naming convention agree on the same passive boundary.

## Acceptance evidence expected

A passing run should show:

- apply passed
- compile passed
- focused pytest passed
- module JSON smoke passed
- module text smoke passed
- no Selenium import
- no browser start
- no profile directory creation
- no adapter filesystem writes
- no click/download/paste/send/package-run side effect
- no commit/push

## Next patch

If accepted, continue with: L2.11 Live adapter browser profile preflight L2 broad validation checkpoint CLI/readback
