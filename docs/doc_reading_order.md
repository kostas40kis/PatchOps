# Documentation Reading Order

This file is the smallest navigation map for PatchOps.

## If you are a human operator

Read in this order:

1. `README.md`
2. `docs/project_status.md`
3. `docs/operator_quickstart.md`
4. `docs/failure_repair_guide.md`

## If you are resuming already-running work

Read in this order:

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`
4. `docs/project_status.md`
5. the relevant `docs/projects/<target>.md` only if target context is needed

## If you are onboarding a brand-new target project

Read in this order:

1. `README.md`
2. `docs/operator_quickstart.md`
3. `docs/llm_usage.md`
4. `docs/project_packet_contract.md`
5. `docs/project_packet_workflow.md`
6. then create or update `docs/projects/<target>.md`

## If you need deep reference

Use these after the first-read surfaces:

- `docs/examples.md`
- `docs/profile_system.md`
- `docs/manifest_schema.md`
- `docs/powershell_runner_guardrails.md`
- `docs/common_mistakes_and_guardrails.md`

## Historical material

Older buildout plans, finalization plans, old freeze prompts, and source bundles are context only.
They help explain how the repo got here.
They should not be the first place an operator or LLM reconstructs current truth.
