# Bundle release readiness

## Purpose

This file explains when the bundle release surface is ready to be treated as shippable.
It exists so release-readiness and maintenance-gate do not have to guess hidden bundle state.

## Required bundle release docs
- `docs/bundle_contract_packet.md`
- `docs/bundle_regression_gate.md`
- `docs/bundle_smoke_gate.md`
- `docs/self_hosted_bundle_proof.md`
- `docs/bundle_release_readiness.md`

## Required bundle release workflows
- `patchops/bundles/authoring.py`
- `patchops/bundles/launcher_emitter.py`

## Required bundle release tests
- `tests/test_bundle_contract_packet_current.py`
- `tests/test_bundle_manifest_regression_gate_current.py`
- `tests/test_bundle_post_build_smoke_gate_current.py`
- `tests/test_self_hosted_bundle_authoring_proof_current.py`

## Operator command sequence
- `make-bundle`
- `bundle-doctor`
- `build-bundle`
- `run-package`

## Readiness posture

A green release-readiness result means the bundle docs, bundle workflows, and bundle tests are present together.
A not-ready result should stay explicit about missing bundle release docs, missing bundle release workflows, and missing bundle release tests.
