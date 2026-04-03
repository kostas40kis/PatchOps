# Examples

See the `examples/` folder for Stage 1 manifests:

- `trader_code_patch.json`
- `trader_doc_patch.json`
- `trader_verify_patch.json`
- `generic_python_patch.json`
- `generic_backup_patch.json`
- `generic_verify_patch.json`

## Safe proving order

Use examples in this order:

1. `generic_python_patch.json`
   - safe first apply run against a throwaway local project
   - creates the initial file that later runs can back up and verify
2. `generic_backup_patch.json`
   - rewrites the same generic file with different content
   - proves that backup discipline is visible before trader-profile work begins
3. `generic_verify_patch.json`
   - proves verification-only flow without rewriting files
4. `trader_code_patch.json`
   - first trader-shaped example after the wrapper itself is already proven
5. `trader_doc_patch.json`
   - documentation-oriented trader example
6. `trader_verify_patch.json`
   - trader verify-only example

These examples are intentionally simple. They demonstrate manifest shape, profile selection, report structure, backup visibility, and how validation commands attach to a run.