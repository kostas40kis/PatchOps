# Examples

Start from examples and adapt them.

## Maintained examples

### trader code patch example
- `examples/trader_code_patch.json`

### trader verification-only example
- `examples/trader_first_verify_patch.json`
- `powershell/invoke-patchverify.ps1`

### generic python example
- `examples/generic_python_patch.json`

### documentation-only example
- `examples/trader_first_doc_patch.json`

### extra maintained examples
- `examples/generic_verify_patch.json`
- `examples/generic_allowed_exit_patch.json`
- `examples/generic_smoke_audit_patch.json`
- `examples/generic_content_path_patch.json`

## Handoff-first continuation examples

Handoff-first continuation examples belong beside the maintained examples.
project packet guidance complements examples; examples remain the baseline.
Do not fall back to stale example or starter-surface names.
- emit-operator-script remains a current maintained surface when operator-facing launcher emission is needed.

## content_path resolution rule

content_path resolution rule:
files_to_write entries use wrapper-relative paths from the wrapper project root.

## Pythonization maintenance alignment

pythonization maintenance alignment remains a documentation note, not a redesign request.

Current operator/bootstrap surfaces also include setup-windows-env alongside emit-operator-script.

Treat historical zip-first/Python-heavier stream summaries as background context, not as the current live frontier.
